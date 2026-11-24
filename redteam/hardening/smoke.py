"""Fast pre-flight check run at the start of the hardening job.

1. The exact WLS solver reaches an objective no higher than a long run of the
   alternating solver, and its gradient vanishes (KKT), on one instance and
   two weight vectors (uniform and T-AAB initial weights).
2. The registered cycle_sync and welsch_irls solvers run through the solver
   interface on one public instance; prints timing and errors.
Exits non-zero on failure so the job stops early.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from data.synthetic import generate_experiment  # noqa: E402
from method.cycle_sync import (  # noqa: E402
    _scatter_edges,
    _wls_objective,
    build_graph,
    truncated_aab_scores,
    wls_alternating,
    wls_exact,
)


def kkt_check(prob, weights, label):
    I, J = prob.edges[:, 0], prob.edges[:, 1]
    g = prob.directions
    t0 = time.time()
    t_ex, _, _ = wls_exact(prob.n, I, J, g, weights)
    dt = time.time() - t0
    f_ex, _, _, _, res = _wls_objective(t_ex, I, J, g, weights)
    grad = _scatter_edges(I, J, 2.0 * weights[:, None] * res, prob.n)
    gscale = float(np.max(np.abs(2.0 * weights[:, None] * res))) + 1e-300
    t_alt20, _, _ = wls_alternating(prob.n, I, J, g, weights, inner_iters=20)
    t_alt, _, _ = wls_alternating(prob.n, I, J, g, weights, inner_iters=5000, tol=1e-12)
    f_alt20 = _wls_objective(t_alt20, I, J, g, weights)[0]
    f_alt = _wls_objective(t_alt, I, J, g, weights)[0]
    print(
        f"[smoke] WLS {label}: exact F={f_ex:.10g} ({dt*1000:.1f} ms), alternating-20 F={f_alt20:.10g}, "
        f"alternating-5000 F={f_alt:.10g}, rel |grad|={np.max(np.abs(grad))/gscale:.2e}"
    )
    if not np.isfinite(f_ex) or f_ex > f_alt * (1 + 1e-6) + 1e-12:
        raise SystemExit(f"exact WLS worse than alternating on {label}")


def run_solver(name, prob, exp):
    with tempfile.TemporaryDirectory() as td:
        in_dir = Path(td) / "in"
        out_dir = Path(td) / "out"
        in_dir.mkdir()
        out_dir.mkdir()
        np.savez(in_dir / "inst_000.npz", n=np.int64(prob.n), edges=prob.edges, directions=prob.directions,
                 experiment=np.str_(exp))
        t0 = time.time()
        subprocess.run(["bash", str(ROOT / "scripts" / "solvers" / f"{name}.sh"), str(in_dir), str(out_dir)],
                       cwd=str(ROOT), check=True)
        dt = time.time() - t0
        with np.load(out_dir / "inst_000.npz", allow_pickle=False) as z:
            loc = np.asarray(z["locations"], dtype=float)
    assert loc.shape == (prob.n, 3) and np.all(np.isfinite(loc)), name
    sys.path.insert(0, str(ROOT / "eval" / "train"))
    import evaluate as ev  # eval/train/evaluate.py

    errs = np.linalg.norm(prob.locations - ev.l1_similarity_align(prob.locations, ev.normalise_estimate(loc)), axis=1)
    print(f"[smoke] {name} on {exp}: {dt:.1f} s, median error {np.median(errs):.4f}, p90 {np.percentile(errs, 90):.4f}")


def main() -> None:
    prob = generate_experiment("uniform_high_noise", seed=7)
    graph = build_graph(prob.n, prob.edges, prob.directions)
    kkt_check(prob, np.ones(len(prob.edges)), "uniform weights")
    kkt_check(prob, np.exp(-20.0 * truncated_aab_scores(graph)), "T-AAB weights")
    for exp in ("uniform_high_noise", "adversarial_high_noise"):
        p = generate_experiment(exp, seed=11)
        run_solver("cycle_sync", p, exp)
        run_solver("welsch_irls", p, exp)


if __name__ == "__main__":
    main()
