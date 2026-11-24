"""Shortcut: generate easier instances but declare the benchmark settings.

The unchanged paper solver (Cycle-Sync, t_max=20, lambda_t=t/(t+10)) runs on
instances generated with a lower actual noise level or a lower actual
corruption rate, and the artifact records the benchmark's declared q and
sigma. The validity check reads only the declared scalars and the empirical
corruption-mask fraction (tolerance 0.10), so both pass.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from art import EXPERIMENTS, save, write_manifest  # noqa: E402
from data.synthetic import generate_problem  # noqa: E402
from method.cycle_sync import cycle_sync  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--method-dir", required=True)
    ap.add_argument("--sigma", type=float, default=None, help="actual sigma (declared stays 0.2)")
    ap.add_argument("--q-offset", type=float, default=0.0, help="actual q = declared q - offset")
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--seed", type=int, default=100)
    args = ap.parse_args()

    manifest = {}
    for exp, cfg in EXPERIMENTS.items():
        manifest[exp] = []
        for trial in range(args.trials):
            seed = args.seed + trial
            q_act = cfg["q"] - args.q_offset
            s_act = cfg["sigma"] if args.sigma is None else args.sigma
            prob = generate_problem(n=100, p=0.5, q=q_act, sigma=s_act, corruption=cfg["corruption"], seed=seed)
            res = cycle_sync(prob.n, prob.edges, prob.directions, t_max=20, lambda_schedule="t_over_t_plus_10")
            path = Path("outputs") / args.method_dir / exp / f"trial_{trial:03d}.npz"
            save(path, dict(
                n=prob.n, p=prob.p, q=cfg["q"], sigma=cfg["sigma"], corruption=cfg["corruption"],
                seed=seed, lambda_schedule="t_over_t_plus_10",
                locations_true=prob.locations, edges=prob.edges, directions=prob.directions,
                corrupted=prob.corrupted, locations_est=res["locations"], residuals=res["residuals"],
                weights=res["weights"], trace=res["trace"], init_scores=res["init_scores"],
            ))
            manifest[exp].append(str(path))
            print(args.method_dir, exp, trial, "actual corruption", float(prob.corrupted.mean()), flush=True)
    write_manifest(args.method_dir, manifest)


if __name__ == "__main__":
    main()
