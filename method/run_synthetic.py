"""Run Cycle-Sync on synthetic experiments and write method artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1]))

from data.synthetic import generate_problem, save_problem
from method.cycle_sync import cycle_sync


EXPERIMENTS = {
    "uniform_high_noise": {"corruption": "uniform", "q": 0.7, "sigma": 0.2},
    "adversarial_high_noise": {"corruption": "adversarial", "q": 0.45, "sigma": 0.2},
}

METHODS = {
    "cycle_sync": "t_over_t_plus_10",
    "cycle_sync_reverse": "ten_over_t_plus_10",
    "cycle_sync_cycle_only": "one",
    "cycle_sync_fast": "t_over_t_plus_5",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiments", nargs="+", default=list(EXPERIMENTS))
    parser.add_argument("--methods", nargs="+", default=list(METHODS))
    parser.add_argument("--n", type=int, default=80)
    parser.add_argument("--p", type=float, default=0.5)
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--seed", type=int, default=100)
    parser.add_argument("--t-max", type=int, default=20)
    parser.add_argument("--out-root", default="outputs")
    args = parser.parse_args()

    unknown_methods = sorted(set(args.methods) - set(METHODS))
    if unknown_methods:
        raise SystemExit(f"Unknown methods: {', '.join(unknown_methods)}")

    out_root = Path(args.out_root)
    manifests: dict[str, dict[str, list[str]]] = {method_name: {} for method_name in args.methods}

    for method_name in args.methods:
        out_dir = out_root / method_name
        out_dir.mkdir(parents=True, exist_ok=True)
        schedule = METHODS[method_name]
        manifest = manifests[method_name]
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
                result = cycle_sync(
                    problem.n,
                    problem.edges,
                    problem.directions,
                    t_max=args.t_max,
                    lambda_schedule=schedule,
                )
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
                    lambda_schedule=schedule,
                    locations_true=problem.locations,
                    edges=problem.edges,
                    directions=problem.directions,
                    corrupted=problem.corrupted,
                    locations_est=result["locations"],
                    residuals=result["residuals"],
                    weights=result["weights"],
                    trace=result["trace"],
                    init_scores=result["init_scores"],
                )
                save_problem(problem, out_dir / exp_name / f"problem_{trial:03d}.npz")
                manifest[exp_name].append(str(artifact))
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
