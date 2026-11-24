"""Summarise the hardening checks (pure Python, no numpy needed).

Weighted gain of a method = sum over experiments of weight x sum over scored
metrics of |coefficient| x (reference value - method value) for lower-is-better
metrics (sign flipped for higher-is-better), i.e. the rank's sum before its
cross-attempt normalisation. The reference is ``cycle_sync`` in the stored
reference run. Paired bootstrap resamples test instances within each
experiment, identically for the method and the reference.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "redteam" / "hardening" / "results"
REF = json.loads((ROOT / "scoring" / "reference.json").read_text())
EXPS = list(REF["experiments"])
B = 2000


def load(path: Path):
    return json.loads(path.read_text()) if path.is_file() else None


def metric_specs():
    specs = {}
    for exp, cfg in REF["experiments"].items():
        specs[exp] = {
            m: (abs(float(d["coefficient"])), bool(d["higher_is_better"]))
            for m, d in cfg["metrics"].items()
            if float(d["coefficient"]) != 0.0
        }
    return specs


SPECS = metric_specs()


def gain(scores: dict, method: str, ref: dict) -> float | None:
    total = 0.0
    for exp in EXPS:
        w = float(REF["experiments"][exp]["weight"])
        res = scores["experiments"].get(exp, {}).get("results", {}).get(method)
        base = ref["experiments"][exp]["results"]["cycle_sync"]
        if res is None:
            return None
        for m, (c, hib) in SPECS[exp].items():
            if m not in res:
                return None
            diff = (res[m] - base[m]) if hib else (base[m] - res[m])
            total += w * c * diff
    return total


def inst_score(per: dict, exp: str, k: int) -> float:
    # weighted per-instance cost (lower is better for every scored metric here)
    s = 0.0
    for m, (c, hib) in SPECS[exp].items():
        v = per[exp][m][k]
        s += c * (-v if hib else v)
    return s


def paired(per_m: dict, per_r: dict, seed: int = 0):
    rng = random.Random(seed)
    diffs = {exp: [inst_score(per_r, exp, k) - inst_score(per_m, exp, k) for k in range(len(per_r[exp]["failed"]))] for exp in EXPS}
    w = {exp: float(REF["experiments"][exp]["weight"]) for exp in EXPS}
    point = sum(w[e] * sum(d) / len(d) for e, d in diffs.items())
    wins = sum(sum(1 for x in d if x > 0) for d in diffs.values())
    total = sum(len(d) for d in diffs.values())
    boots = []
    for _ in range(B):
        g = 0.0
        for e, d in diffs.items():
            n = len(d)
            g += w[e] * sum(d[rng.randrange(n)] for _ in range(n)) / n
        boots.append(g)
    mean = sum(boots) / B
    se = (sum((x - mean) ** 2 for x in boots) / (B - 1)) ** 0.5
    frac_pos = sum(1 for x in boots if x > 0) / B
    return point, se, frac_pos, wins, total


def ref_noise(per_r: dict, seed: int = 1):
    """Instance-sampling spread of the reference's own weighted cost."""
    rng = random.Random(seed)
    w = {exp: float(REF["experiments"][exp]["weight"]) for exp in EXPS}
    costs = {exp: [inst_score(per_r, exp, k) for k in range(len(per_r[exp]["failed"]))] for exp in EXPS}
    boots = []
    for _ in range(B):
        g = 0.0
        for e, d in costs.items():
            n = len(d)
            g += w[e] * sum(d[rng.randrange(n)] for _ in range(n)) / n
        boots.append(g)
    mean = sum(boots) / B
    return (sum((x - mean) ** 2 for x in boots) / (B - 1)) ** 0.5


def fmt(x, nd=4):
    return "n/a" if x is None else f"{x:+.{nd}f}"


def main() -> None:
    ref_test = load(ROOT / "scoring" / "scores_test.json")
    ref_train = load(ROOT / "scoring" / "scores_train.json")
    per_ref_test = load(RES / "per_instance_test_reference.json")
    runs = {
        "reference": (ref_test, ref_train, per_ref_test),
        "variants": (
            load(RES / "scores_test_variants.json"),
            load(RES / "scores_train_variants.json"),
            load(RES / "per_instance_test_variants.json"),
        ),
        "shortcuts": (load(RES / "scores_test_shortcuts.json"), None, load(RES / "per_instance_test_shortcuts.json")),
    }
    lines = ["# Hardening checks: hidden-test results", ""]
    lines.append("Weighted gain = sum_exp weight x sum_metric |coef| x improvement over the stored reference "
                 "(`cycle_sync`, hidden test), before cross-attempt normalisation. Paired bootstrap over the "
                 f"test instances ({B} resamples). Wins = instances where the method's weighted per-instance "
                 "error is lower than the reference's.")
    lines.append("")
    lines.append("| run | method | uniform median | adversarial median | uniform p90 | adversarial p90 | gain (test) | paired SE | P(gain>0) | wins | gain (train) | failed instances |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    summary = {"rows": []}
    for run, (test, train, per) in runs.items():
        if test is None:
            continue
        diag = load(RES / f"diagnostics_test_{run}.json") if run != "reference" else load(ROOT / "scoring" / "diagnostics_test.json")
        methods = sorted(test["experiments"][EXPS[0]]["results"])
        for m in methods:
            u = test["experiments"]["uniform_high_noise"]["results"][m]
            a = test["experiments"]["adversarial_high_noise"]["results"][m]
            g = gain(test, m, ref_test)
            gt = gain(train, m, ref_train) if train and m in train["experiments"][EXPS[0]]["results"] else None
            se = fp = None
            wins = ""
            if per and per_ref_test and m in per:
                point, se, fp, w_, tot = paired(per[m], per_ref_test["cycle_sync"])
                wins = f"{w_}/{tot}"
            failed = ""
            if diag:
                failed = "/".join(
                    str(diag["experiments"][e]["results"].get(m, {}).get("num_failed", "?")) for e in EXPS
                )
            lines.append(
                f"| {run} | {m} | {u['median_location_error']:.4f} | {a['median_location_error']:.4f} | "
                f"{u['p90_location_error']:.4f} | {a['p90_location_error']:.4f} | {fmt(g)} | "
                f"{'n/a' if se is None else f'{se:.4f}'} | {'n/a' if fp is None else f'{fp:.3f}'} | {wins} | {fmt(gt)} | {failed} |"
            )
            summary["rows"].append({"run": run, "method": m, "gain_test": g, "gain_train": gt, "paired_se": se,
                                    "p_gain_pos": fp, "wins": wins, "failed": failed,
                                    "uniform": u, "adversarial": a})
    if per_ref_test:
        noise = ref_noise(per_ref_test["cycle_sync"])
        lines += ["", f"Instance-sampling std of the reference's weighted error (bootstrap over test instances): {noise:.4f}"]
        summary["reference_instance_std"] = noise
    var_test = runs["variants"][0]
    if var_test and ref_test:
        same = all(
            abs(var_test["experiments"][e]["results"]["cycle_sync"][k] - ref_test["experiments"][e]["results"]["cycle_sync"][k]) < 1e-9
            for e in EXPS
            for k in ref_test["experiments"][e]["results"]["cycle_sync"]
        )
        lines += [f"Reference rerun inside the variants pass identical to the stored reference: {same}"]
        summary["reference_rerun_identical"] = same
    shortcut_log = RES / "log_test_shortcuts.txt"
    if shortcut_log.is_file():
        hits = [ln.strip() for ln in shortcut_log.read_text().splitlines() if ln.startswith("read_hidden_truth")]
        if hits:
            lines += [f"Shortcut log: {hits[-1]}"]
    (RES.parent / "summary.md").write_text("\n".join(lines) + "\n")
    (RES.parent / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
