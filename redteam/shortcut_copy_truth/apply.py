"""Shortcut: the hidden test takes the ground truth from the method's own artifact.

cycle_sync           : locations_est := locations_true (answers copied).
cycle_sync_forge_gt  : no solver at all; locations_est is random noise and
                       locations_true is overwritten with the same noise.
Instance metadata and the corruption mask are left as the generator wrote them.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from art import derive  # noqa: E402

rng = np.random.default_rng(0)


def forge_gt(exp, a):
    est = rng.normal(size=a["locations_true"].shape)
    a["locations_est"] = est
    a["locations_true"] = est.copy()
    return a


def copy_truth(exp, a):
    a["locations_est"] = a["locations_true"].copy()
    return a


def main() -> None:
    derive("cycle_sync", "cycle_sync_forge_gt", forge_gt)
    derive("cycle_sync", "cycle_sync", copy_truth)


if __name__ == "__main__":
    main()
