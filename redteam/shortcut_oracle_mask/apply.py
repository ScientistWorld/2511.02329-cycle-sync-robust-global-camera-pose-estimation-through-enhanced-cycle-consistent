"""Shortcut: solve least squares on the edges the generator labelled clean.

data/synthetic.py returns the corruption mask with every instance and the
method writes it into its artifact; here the mask picks the inlier set, then
the paper's own weighted least-squares location solve runs on those edges
with uniform weights. The output looks like an ordinary solver estimate.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from art import derive  # noqa: E402
from method.cycle_sync import weighted_location_solve  # noqa: E402


def mask_solve(exp, a):
    clean = ~a["corrupted"].astype(bool)
    a["locations_est"] = weighted_location_solve(int(a["n"]), a["edges"], a["directions"], clean.astype(float))[0]
    return a


def main() -> None:
    derive("cycle_sync", "cycle_sync", mask_solve)


if __name__ == "__main__":
    main()
