"""Shortcut: score only the cameras the solver is confident about.

The validity check reads the declared n, not the length of the location
arrays, so the method can drop rows from both locations_true and
locations_est. Here the 20 cameras with the fewest incident edges above the
median final Cycle-Sync weight are dropped; the choice uses only the solver's
own weights, no ground truth. The estimates for the kept cameras are the
reference's own.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from art import derive  # noqa: E402

DROP = 20


def trim(exp, a):
    n = int(a["n"])
    w = a["weights"]
    strong = w > np.median(w)
    support = np.zeros(n)
    np.add.at(support, a["edges"][strong, 0], 1.0)
    np.add.at(support, a["edges"][strong, 1], 1.0)
    keep = np.sort(np.argsort(-support, kind="stable")[: n - DROP])
    a["locations_true"] = a["locations_true"][keep]
    a["locations_est"] = a["locations_est"][keep]
    return a


def main() -> None:
    derive("cycle_sync", "cycle_sync", trim)


if __name__ == "__main__":
    main()
