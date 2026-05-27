"""Run the residual-only Welsch IRLS baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve

sys.path.append(str(Path(__file__).resolve().parents[1]))

from data.synthetic import generate_problem


EXPERIMENTS = {
    "uniform_high_noise": {"corruption": "uniform", "q": 0.7, "sigma": 0.2},
    "adversarial_high_noise": {"corruption": "adversarial", "q": 0.45, "sigma": 0.2},
}


def weighted_location_solve(
    n: int,
    edges: np.ndarray,
    directions: np.ndarray,
    weights: np.ndarray,
    inner_iters: int = 20,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Solve the weighted location objective used by the baseline."""

    m = len(edges)
    alpha = np.ones(m, dtype=float)
    locations = np.zeros((n, 3), dtype=float)
    rows = []
    cols = []
    data = []
    for e, (i, j) in enumerate(edges):
        w = float(max(weights[e], 1e-12))
        rows.extend([e, e])
        cols.extend([int(i), int(j)])
        data.extend([np.sqrt(w), -np.sqrt(w)])
    a = sparse.coo_matrix((data, (rows, cols)), shape=(m, n)).tocsr()
    ata = (a.T @ a).tolil()
    ata[0, :] = 1.0
    ata = ata.tocsr()

    for _ in range(inner_iters):
        b = np.sqrt(np.maximum(weights, 1e-12))[:, None] * alpha[:, None] * directions
        rhs = a.T @ b
        rhs[0, :] = 0.0
        for dim in range(3):
            locations[:, dim] = spsolve(ata, rhs[:, dim])
        diff = locations[edges[:, 0]] - locations[edges[:, 1]]
        new_alpha = np.maximum(1.0, np.sum(diff * directions, axis=1))
        if np.max(np.abs(new_alpha - alpha)) < 1e-7:
            alpha = new_alpha
            break
        alpha = new_alpha
    residuals = np.linalg.norm(
        locations[edges[:, 0]] - locations[edges[:, 1]] - alpha[:, None] * directions,
        axis=1,
    )
    return locations, alpha, residuals


def residual_irls(
    n: int,
    edges: np.ndarray,
    directions: np.ndarray,
    t_max: int = 20,
    delta: float = 1e-8,
) -> dict[str, np.ndarray]:
    """Residual-only robust reweighting baseline."""

    weights = np.ones(len(edges), dtype=float)
    trace = []
    locations = np.zeros((n, 3), dtype=float)
    residuals = np.ones(len(edges), dtype=float)
    alpha = np.ones(len(edges), dtype=float)
    for _ in range(t_max):
        locations, alpha, residuals = weighted_location_solve(n, edges, directions, weights)
        weights = np.exp(-4.0 * residuals) / (residuals + delta)
        weights = np.clip(weights, 1e-8, 1e8)
        trace.append(float(np.median(residuals)))
    return {
        "locations": locations,
        "alpha": alpha,
        "residuals": residuals,
        "weights": weights,
        "trace": np.asarray(trace),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiments", nargs="+", default=list(EXPERIMENTS))
    parser.add_argument("--n", type=int, default=80)
    parser.add_argument("--p", type=float, default=0.5)
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--seed", type=int, default=100)
    parser.add_argument("--t-max", type=int, default=20)
    parser.add_argument("--out-dir", default="outputs/irls")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, list[str]] = {}
    for exp_name in args.experiments:
        cfg = EXPERIMENTS[exp_name]
        manifest[exp_name] = []
        for trial in range(args.trials):
            seed = args.seed + trial
            problem = generate_problem(
                n=args.n,
                p=args.p,
                q=cfg["q"],
                sigma=cfg["sigma"],
                corruption=cfg["corruption"],
                seed=seed,
            )
            result = residual_irls(problem.n, problem.edges, problem.directions, t_max=args.t_max)
            artifact = out_dir / exp_name / f"trial_{trial:03d}.npz"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(
                artifact,
                n=problem.n,
                p=problem.p,
                q=problem.q,
                sigma=problem.sigma,
                corruption=problem.corruption,
                seed=problem.seed,
                locations_true=problem.locations,
                edges=problem.edges,
                directions=problem.directions,
                corrupted=problem.corrupted,
                locations_est=result["locations"],
                residuals=result["residuals"],
                weights=result["weights"],
                trace=result["trace"],
            )
            manifest[exp_name].append(str(artifact))
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
