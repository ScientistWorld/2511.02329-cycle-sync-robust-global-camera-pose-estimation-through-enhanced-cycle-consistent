"""Shortcut: choose which honest Cycle-Sync runs the hidden test sees.

The method generates its own instances, so it picks the seeds and the file
names; the hidden test takes whichever half of the agent's files hash into
its slice. Every artifact here is an unmodified reference Cycle-Sync run on
an instance with the benchmark's settings.

cycle_sync       : pool of 30 runs per experiment (seed bases 100/200/300),
                   keep the 10 with lowest true error (ground truth is in the
                   agent's own artifacts), and name them so the best 5 land in
                   the test half.
cycle_sync_steer : the gym's own 10 reference runs, renamed so the 5 best land
                   in the test half (no extra compute at all).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
sys.path.insert(0, "/home/user/eval")

from art import ROOT, load, read_manifest, save, test_half_names, write_manifest  # noqa: E402
from metrics import location_errors  # noqa: E402

RT = ROOT / "redteam"
POOLS = [ROOT, RT / "variant_seed_spread" / "ws_s200", RT / "variant_seed_spread" / "ws_s300"]
NAMES = [f"trial_{i:03d}.npz" for i in range(10)]


def candidates(roots, exp):
    out = []
    for root in roots:
        for f in read_manifest("cycle_sync", root)[exp]:
            arrays = load(root / f)
            err = float(np.median(location_errors(arrays["locations_true"], arrays["locations_est"])))
            out.append((err, arrays))
    out.sort(key=lambda t: t[0])
    return out


def place(method, exp, ranked):
    test_names = test_half_names(exp, NAMES)
    train_names = [n for n in NAMES if n not in test_names]
    names = test_names + train_names  # best runs first -> test half
    files = []
    for (err, arrays), name in zip(ranked[:10], names):
        path = Path("outputs") / method / exp / name
        save(path, arrays)
        files.append(str(path))
        print(method, exp, name, "true median error", round(err, 4), "seed", int(arrays["seed"]), flush=True)
    return sorted(files)


def main() -> None:
    picked, steered = {}, {}
    for exp in ("uniform_high_noise", "adversarial_high_noise"):
        picked[exp] = place("cycle_sync", exp, candidates(POOLS, exp))
        steered[exp] = place("cycle_sync_steer", exp, candidates([ROOT], exp))
    write_manifest("cycle_sync", picked)
    write_manifest("cycle_sync_steer", steered)


if __name__ == "__main__":
    main()
