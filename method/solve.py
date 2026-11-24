"""Solver entry point used by the benchmark's solver interface.

Usage (normally through scripts/solvers/<name>.sh):

    python method/solve.py --input-dir IN --output-dir OUT [options]

Every ``IN/*.npz`` holds one problem instance with ``n`` (camera count),
``edges`` (m x 2, i < j) and ``directions`` (m x 3 unit vectors approximating
(t_i - t_j) / ||t_i - t_j||). For each instance the solver writes
``OUT/<same file name>`` holding ``locations`` (n x 3).
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from method.cycle_sync import SCHEDULES, TAAB_TEMPERATURES, cycle_sync, residual_irls  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--algorithm", choices=["cycle_sync", "irls"], default="cycle_sync")
    parser.add_argument("--schedule", choices=sorted(SCHEDULES), default="t_over_t_plus_10")
    parser.add_argument("--t-max", type=int, default=20)
    parser.add_argument("--beta", type=float, default=20.0)
    parser.add_argument("--init", choices=["t-aab", "uniform"], default="t-aab")
    parser.add_argument("--wls", choices=["exact", "alternating"], default="exact")
    parser.add_argument("--softmin", choices=["stable", "legacy"], default="stable")
    parser.add_argument("--taab-temps", choices=sorted(TAAB_TEMPERATURES), default="authors")
    parser.add_argument("--weight-clip", choices=["score", "weight"], default="score")
    args = parser.parse_args()

    in_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(in_dir.glob("*.npz")):
        with np.load(path, allow_pickle=False) as z:
            n = int(z["n"])
            edges = np.asarray(z["edges"], dtype=np.int64)
            directions = np.asarray(z["directions"], dtype=float)
        if args.algorithm == "irls":
            result = residual_irls(n, edges, directions, t_max=args.t_max, wls=args.wls, weight_clip=args.weight_clip)
        else:
            result = cycle_sync(
                n,
                edges,
                directions,
                t_max=args.t_max,
                beta=args.beta,
                init=args.init,
                lambda_schedule=args.schedule,
                wls=args.wls,
                softmin=args.softmin,
                taab_temps=args.taab_temps,
                weight_clip=args.weight_clip,
            )
        np.savez(out_dir / path.name, locations=np.asarray(result["locations"], dtype=float))


if __name__ == "__main__":
    main()
