"""Degenerate and impossible outputs.

cycle_sync         : reference estimates on uniform_high_noise; NaN estimates
                     on adversarial_high_noise (a run that blew up there).
degenerate_zeros   : every camera at the origin.
degenerate_random  : independent N(0, I) estimates.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from art import derive  # noqa: E402

rng = np.random.default_rng(1)


def zeros(exp, a):
    a["locations_est"] = np.zeros_like(a["locations_true"])
    return a


def random(exp, a):
    a["locations_est"] = rng.normal(size=a["locations_true"].shape)
    return a


def nan_on_adversarial(exp, a):
    if exp == "adversarial_high_noise":
        a["locations_est"] = np.full_like(a["locations_true"], np.nan)
    return a


def main() -> None:
    derive("cycle_sync", "degenerate_zeros", zeros)
    derive("cycle_sync", "degenerate_random", random)
    derive("cycle_sync", "cycle_sync", nan_on_adversarial)


if __name__ == "__main__":
    main()
