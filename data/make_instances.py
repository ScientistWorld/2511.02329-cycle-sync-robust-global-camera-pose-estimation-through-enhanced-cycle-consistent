"""Write the public train instances to data/instances/train/<experiment>.npz.

The train instances use public seeds and include ground truth, so they can be
used freely for development. Idempotent: existing files are kept unless
--force is given.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data.synthetic import EXPERIMENTS, generate_experiment, save_instance_set  # noqa: E402

TRAIN_COUNT = 20
PUBLIC_SEED_BASE = {"uniform_high_noise": 1000, "adversarial_high_noise": 2000}
OUT_DIR = Path(__file__).resolve().parent / "instances" / "train"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    for name in EXPERIMENTS:
        path = OUT_DIR / f"{name}.npz"
        if path.exists() and not args.force:
            print(f"keep {path}")
            continue
        problems = [generate_experiment(name, PUBLIC_SEED_BASE[name] + k) for k in range(TRAIN_COUNT)]
        save_instance_set(path, problems)
        print(f"wrote {path} ({TRAIN_COUNT} instances)")


if __name__ == "__main__":
    main()
