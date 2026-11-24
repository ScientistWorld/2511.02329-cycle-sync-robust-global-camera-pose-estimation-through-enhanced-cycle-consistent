"""Exploration job for the final hardening pass.

Settles, on public seeds, the questions the final design depends on:

1. Data model. ``eq9`` is the gym's literal reading of the paper's Eqs. 9-10
   (Gaussian noise added to t_i - t_j before normalising). ``authors`` is the
   generator in the authors' released code (ports of the lab's
   UniformCorruptionModel.m / AdvCorruptionModel.m): sigma times a uniformly
   random unit vector added to the *unit* direction, and in the adversarial
   model added to every edge after corruption.
2. T-AAB settings. ``gym`` = this gym's invented temperatures (1, 1.4, ...,
   on pi-normalised scores) with the exact geodesic arc distance; ``authgeo``
   = the authors' temperatures (tau = 2, 4, 8, 16, 20 on radian scores) with
   the geodesic distance the paper defines; ``authfull`` = the authors'
   closed form as coded (arccos of the squared projection norm inside the
   arc). ``authgeo``/``authfull`` also clip h to [1e-8, 10] as the authors do
   instead of clipping weights to [1e-8, 1e8].
3. Baselines: the paper's lambda = 0 ablation (T-AAB start, residual-only
   Welsch reweighting), residual-only Welsch IRLS from uniform weights, LUD
   (IRLS for rho = |x|), and one unweighted least-squares solve.
4. Headroom: a refit on the top edges by final weight, more / fewer
   iterations, and an oracle least-squares fit on the truly clean edges.

Every solver call is wrapped so that one failure cannot stop the job.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
import traceback
from pathlib import Path

import numpy as np
from scipy import sparse
from scipy.sparse.csgraph import connected_components

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from data.synthetic import generate_problem  # noqa: E402
from method.cycle_sync import (  # noqa: E402
    SCHEDULES,
    WEIGHT_MAX,
    WEIGHT_MIN,
    _segment_weighted_mean,
    build_graph,
    cycle_scores,
    wls_exact,
)

_spec = importlib.util.spec_from_file_location("ev_train", ROOT / "eval" / "train" / "evaluate.py")
ev = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ev)

OUT = Path(__file__).resolve().parent
SETTINGS = {
    "uniform_high_noise": dict(n=100, p=0.5, q=0.7, sigma=0.2, corruption="uniform"),
    "adversarial_high_noise": dict(n=100, p=0.5, q=0.45, sigma=0.2, corruption="adversarial"),
}
NOISELESS = {
    "uniform_q08_noiseless": dict(n=100, p=0.5, q=0.8, sigma=0.0, corruption="uniform"),
    "adversarial_q04_noiseless": dict(n=100, p=0.5, q=0.4, sigma=0.0, corruption="adversarial"),
}
N_INST = 16
N_NOISELESS = 5
GYM_BETAS = [1.0 * 1.4**k for k in range(5)]
AUTH_BETAS = [np.pi * min(2.0 ** (k + 1), 20.0) for k in range(5)]
COEF = np.array([1.0, 0.4, 0.6])


def normalize(x: np.ndarray) -> np.ndarray:
    return x / np.maximum(np.linalg.norm(x, axis=-1, keepdims=True), 1e-15)


def gen_eq9(cfg: dict, seed: int) -> dict:
    p = generate_problem(seed=seed, **cfg)
    return dict(n=p.n, edges=p.edges, directions=p.directions, locations=p.locations, corrupted=p.corrupted)


def gen_authors(cfg: dict, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    n, p, q, sigma = cfg["n"], cfg["p"], cfg["q"], cfg["sigma"]
    t = rng.normal(size=(n, 3))
    t_alt = rng.normal(size=(n, 3))
    mask = rng.random((n, n)) < p
    ii, jj = np.where(np.triu(mask, 1))
    g_gt = normalize(t[ii] - t[jj])
    m = len(ii)
    bad = rng.random(m) < q
    u = normalize(rng.normal(size=(m, 3)))
    if cfg["corruption"] == "uniform":
        g = g_gt + sigma * u
        g[bad] = u[bad]
    else:
        g = g_gt.copy()
        g[bad] = normalize(t_alt[ii] - t_alt[jj])[bad]
        g = g + sigma * u
    return dict(n=n, edges=np.stack([ii, jj], 1).astype(np.int64), directions=normalize(g), locations=t, corrupted=bad)


GENERATORS = {"eq9": gen_eq9, "authors": gen_authors}


def aab_values(graph, formula: str, min_sin: float = 0.6):
    a = graph.g_ik
    b = -graph.g_jk
    g = graph.g_ij
    cross = np.linalg.norm(np.cross(graph.g_ik, graph.g_jk), axis=1)
    c = np.sum(a * b, axis=1)
    det = 1.0 - c * c
    ok = (cross >= min_sin) & (np.abs(det) >= 1e-12)
    safe = np.where(ok, det, 1.0)
    ga = np.sum(g * a, axis=1)
    gb = np.sum(g * b, axis=1)
    c0 = (ga - c * gb) / safe
    c1 = (gb - c * ga) / safe
    inside = (c0 > 0.0) & (c1 > 0.0)
    pn2 = np.clip((ga * ga + gb * gb - 2.0 * ga * gb * c) / safe, 0.0, 1.0)
    cos_in = np.sqrt(pn2) if formula == "geo" else pn2
    val = np.where(inside, cos_in, np.maximum(ga, gb))
    d = np.arccos(np.clip(val, -1.0, 1.0)) / np.pi
    return ok, d[ok]


def taab(graph, formula: str, betas: list[float]) -> np.ndarray:
    ok, d = aab_values(graph, formula)
    te = graph.t_edge[ok]
    e_ik = graph.t_ik[ok]
    e_jk = graph.t_jk[ok]
    m = graph.m
    cnt = np.bincount(te, minlength=m)
    has = cnt > 0
    scores = np.ones(m)
    scores[has] = np.bincount(te, weights=d, minlength=m)[has] / cnt[has]
    for beta in betas:
        new = _segment_weighted_mean(te, m, scores[e_ik] + scores[e_jk], d, beta)
        scores = np.where(has, new, scores)
    return scores


def cs_run(inst, graph, init, sched="t_over_t_plus_10", t_max=20, clip="w"):
    n = inst["n"]
    w = np.ones(graph.m) if init is None else np.exp(-20.0 * init)
    loc = None
    for t in range(1, t_max + 1):
        loc, _alpha, r = wls_exact(n, graph.I, graph.J, graph.gamma, w, t0=loc)
        lam = SCHEDULES[sched](t)
        h = r if lam == 0.0 else (1.0 - lam) * r + lam * cycle_scores(graph, loc, r, beta=20.0)
        if clip == "h":
            hh = np.clip(h, 1e-8, 10.0)
            w = np.exp(-4.0 * hh) / (hh + 1e-8)
        else:
            w = np.clip(np.exp(-4.0 * h) / (h + 1e-8), WEIGHT_MIN, WEIGHT_MAX)
    return loc, w


def lud_run(inst, graph, iters=20):
    w = np.ones(graph.m)
    loc = None
    for _ in range(iters):
        loc, _a, r = wls_exact(inst["n"], graph.I, graph.J, graph.gamma, w, t0=loc)
        w = 1.0 / np.sqrt(r * r + 1e-16)
    return loc, w


def connected(n, edges):
    g = sparse.coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(n, n))
    return connected_components(g, directed=False)[0] == 1


def subset_fit(inst, graph, keep, t0=None):
    w = np.full(graph.m, 1e-12)
    w[keep] = 1.0
    return wls_exact(inst["n"], graph.I, graph.J, graph.gamma, w, t0=t0)[0]


def refit(inst, graph, w_final, loc0, q, rho):
    m, n = graph.m, inst["n"]
    edges = np.stack([graph.I, graph.J], 1)
    k = max(int(round(rho * (1.0 - q) * m)), n)
    order = np.argsort(-w_final, kind="stable")
    while k < m and not connected(n, edges[order[:k]]):
        k = min(m, int(k * 1.1) + 1)
    return subset_fit(inst, graph, order[:k], t0=loc0)


def precision(score_low_is_clean, corrupted, q):
    k = int(round((1.0 - q) * len(corrupted)))
    order = np.argsort(score_low_is_clean, kind="stable")[:k]
    return float(np.mean(~corrupted[order]))


def metrics(inst, loc):
    if loc is None or not np.all(np.isfinite(loc)):
        return [float("nan")] * 3
    return ev.instance_metrics(inst["locations"], ev.normalise_estimate(np.asarray(loc, float))).tolist()


def run_instance(inst, q, full=True):
    graph = build_graph(inst["n"], inst["edges"], inst["directions"])
    res, times, diag = {}, {}, {}

    def go(name, fn):
        t0 = time.time()
        try:
            out = fn()
        except Exception:
            traceback.print_exc()
            out = None
        times[name] = time.time() - t0
        return out

    init_gym = go("taab_gym", lambda: taab(graph, "geo", GYM_BETAS))
    init_ag = go("taab_authgeo", lambda: taab(graph, "geo", AUTH_BETAS))
    init_af = go("taab_authfull", lambda: taab(graph, "auth", AUTH_BETAS))
    for nm, init in (("gym", init_gym), ("authgeo", init_ag), ("authfull", init_af)):
        if init is not None:
            diag[f"init_precision_{nm}"] = precision(init, inst["corrupted"], q)

    runs = {
        "cs_gym": lambda: cs_run(inst, graph, init_gym, clip="w"),
        "cs_authgeo": lambda: cs_run(inst, graph, init_ag, clip="h"),
        "cs_authfull": lambda: cs_run(inst, graph, init_af, clip="h"),
        "lud": lambda: lud_run(inst, graph),
    }
    if full:
        runs.update(
            {
                "lam0_gym": lambda: cs_run(inst, graph, init_gym, sched="zero", clip="w"),
                "lam0_authgeo": lambda: cs_run(inst, graph, init_ag, sched="zero", clip="h"),
                "irls_uniform": lambda: cs_run(inst, graph, None, sched="zero", clip="w"),
                "ls_unweighted": lambda: (subset_fit(inst, graph, np.arange(graph.m)), None),
                "reverse_authgeo": lambda: cs_run(inst, graph, init_ag, sched="ten_over_t_plus_10", clip="h"),
                "cycleonly_authgeo": lambda: cs_run(inst, graph, init_ag, sched="one", clip="h"),
                "fast_authgeo": lambda: cs_run(inst, graph, init_ag, sched="t_over_t_plus_5", clip="h"),
                "uniforminit_authgeo": lambda: cs_run(inst, graph, None, clip="h"),
                "tmax3_authgeo": lambda: cs_run(inst, graph, init_ag, t_max=3, clip="h"),
                "tmax40_authgeo": lambda: cs_run(inst, graph, init_ag, t_max=40, clip="h"),
                "oracle_clean_ls": lambda: (subset_fit(inst, graph, np.flatnonzero(~inst["corrupted"])), None),
            }
        )
    outs = {}
    for name, fn in runs.items():
        out = go(name, fn)
        outs[name] = out
        res[name] = metrics(inst, None if out is None else out[0])
        if out is not None and out[1] is not None:
            diag[f"final_precision_{name}"] = precision(-out[1], inst["corrupted"], q)
    if full:
        for base in ("cs_authgeo", "cs_gym"):
            out = outs.get(base)
            for rho in (1.0, 0.8):
                name = f"refit{int(rho * 100)}_{base}"
                if out is None:
                    res[name] = [float("nan")] * 3
                    continue
                loc = go(name, lambda: refit(inst, graph, out[1], out[0], q, rho))
                res[name] = metrics(inst, loc)
    return res, times, diag


def summarise(per: dict, ref: str) -> list[str]:
    lines = []
    names = list(per)
    arr = {k: np.array(v) for k, v in per.items()}
    ref_cost = arr[ref] @ COEF
    lines.append(f"| solver | median | mean | p90 | weighted cost | gain vs {ref} | paired SE | wins |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for k in names:
        a = arr[k]
        cost = a @ COEF
        diff = ref_cost - cost
        ok = np.isfinite(diff)
        se = float(np.std(diff[ok], ddof=1) / np.sqrt(ok.sum())) if ok.sum() > 1 else float("nan")
        lines.append(
            f"| {k} | {np.nanmean(a[:, 0]):.4f} | {np.nanmean(a[:, 1]):.4f} | {np.nanmean(a[:, 2]):.4f} | "
            f"{np.nanmean(cost):.4f} | {np.nanmean(diff):+.4f} | {se:.4f} | {int(np.sum(diff[ok] > 0))}/{int(ok.sum())} |"
        )
    return lines


def main() -> None:
    import numpy, scipy  # noqa: F401

    print("numpy", np.__version__, "scipy", scipy.__version__, flush=True)
    results: dict = {"settings": {}, "noiseless": {}}
    md = ["# Exploration results (public seeds)", ""]
    t_start = time.time()
    for model, gen in GENERATORS.items():
        for sname, cfg in SETTINGS.items():
            per: dict = {}
            times: dict = {}
            diags: dict = {}
            for k in range(N_INST):
                inst = gen(cfg, 70_000 + 1000 * (sname == "adversarial_high_noise") + k)
                res, tm, dg = run_instance(inst, cfg["q"], full=True)
                for name, v in res.items():
                    per.setdefault(name, []).append(v)
                for name, v in tm.items():
                    times.setdefault(name, []).append(v)
                for name, v in dg.items():
                    diags.setdefault(name, []).append(v)
                print(f"[{model}/{sname}] instance {k} done ({time.time() - t_start:.0f}s)", flush=True)
            results["settings"][f"{model}/{sname}"] = {"per_instance": per, "times": times, "diag": diags}
            md += [f"## {model} / {sname}", ""]
            md += summarise(per, "cs_authgeo")
            md += [""]
            md += ["diagnostics (mean over instances): " + ", ".join(f"{k}={np.mean(v):.3f}" for k, v in sorted(diags.items()))]
            md += ["seconds per instance: " + ", ".join(f"{k}={np.mean(v):.2f}" for k, v in sorted(times.items()))]
            md += [""]
            (OUT / "results.json").write_text(json.dumps(results))
            (OUT / "results.md").write_text("\n".join(md) + "\n")
            print("\n".join(md[-(len(per) + 6):]), flush=True)
    for sname, cfg in NOISELESS.items():
        per = {}
        for k in range(N_NOISELESS):
            inst = gen_eq9(cfg, 90_000 + 100 * len(sname) + k)
            res, _tm, _dg = run_instance(inst, cfg["q"], full=False)
            for name, v in res.items():
                per.setdefault(name, []).append(v)
        results["noiseless"][sname] = per
        md += [f"## noiseless {sname} (exact recovery = median < 1e-4)", ""]
        for name, v in per.items():
            a = np.array(v)
            md.append(f"- {name}: median errors {', '.join(f'{x:.2e}' for x in a[:, 0])}; exact {int(np.sum(a[:, 0] < 1e-4))}/{len(a)}")
        md.append("")
        (OUT / "results.json").write_text(json.dumps(results))
        (OUT / "results.md").write_text("\n".join(md) + "\n")
    md.append(f"total time {time.time() - t_start:.0f}s")
    (OUT / "results.md").write_text("\n".join(md) + "\n")
    print("\n".join(md), flush=True)


if __name__ == "__main__":
    main()
