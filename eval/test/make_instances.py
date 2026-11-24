"""Create the hidden test instances (eval/test/instances/<experiment>.npz).

Every instance is drawn from the benchmark's synthetic model with a fresh
128-bit seed taken from the operating system. The seeds are never written
anywhere, so the stored files are the only copy of the test ground truth and
nothing outside eval/test/ can regenerate it. Idempotent: existing files are
kept unless --force is given (which replaces the hidden test, so every stored
test score must then be regenerated).

This file carries its own copy of the generator on purpose: the hidden test
must not depend on code outside eval/test/. The corruption models are those of
the authors' released code (noise = sigma x a uniformly random unit vector
added to the unit direction; adversarial outliers are directions of an
alternative camera cloud, and noise is added to every edge).
"""

from __future__ import annotations

import argparse
import secrets
from pathlib import Path

import numpy as np

TEST_COUNT = 40
EXPERIMENTS = {
    "uniform_high_noise": {"n": 100, "p": 0.5, "q": 0.7, "sigma": 0.2, "corruption": "uniform"},
    "adversarial_high_noise": {"n": 100, "p": 0.5, "q": 0.45, "sigma": 0.2, "corruption": "adversarial"},
}
OUT_DIR = Path(__file__).resolve().parent / "instances"


def _normalize(x: np.ndarray) -> np.ndarray:
    return x / np.maximum(np.linalg.norm(x, axis=-1, keepdims=True), 1e-15)


def generate(n: int, p: float, q: float, sigma: float, corruption: str, rng: np.random.Generator):
    locations = rng.normal(size=(n, 3))
    alt_locations = rng.normal(size=(n, 3))
    mask = rng.random((n, n)) < p
    ii, jj = np.where(np.triu(mask, 1))
    true_dir = _normalize(locations[ii] - locations[jj])
    bad = rng.random(len(ii)) < q
    noise = _normalize(rng.normal(size=true_dir.shape))
    if corruption == "uniform":
        observed = true_dir + sigma * noise
        observed[bad] = noise[bad]
    else:
        observed = true_dir.copy()
        observed[bad] = _normalize(alt_locations[ii] - alt_locations[jj])[bad]
        observed = observed + sigma * noise
    edges = np.stack([ii, jj], axis=1).astype(np.int32)
    return locations, edges, _normalize(observed), bad


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, cfg in EXPERIMENTS.items():
        path = OUT_DIR / f"{name}.npz"
        if path.exists() and not args.force:
            print(f"keep {path.name}")
            continue
        arrays: dict[str, np.ndarray] = {"count": np.int64(TEST_COUNT)}
        for k in range(TEST_COUNT):
            rng = np.random.default_rng(secrets.randbits(128))
            locations, edges, directions, bad = generate(rng=rng, **cfg)
            arrays[f"n_{k:03d}"] = np.int64(cfg["n"])
            arrays[f"edges_{k:03d}"] = edges
            arrays[f"directions_{k:03d}"] = directions
            arrays[f"locations_{k:03d}"] = locations
            arrays[f"corrupted_{k:03d}"] = bad
        np.savez_compressed(path, **arrays)
        print(f"wrote {path.name} ({TEST_COUNT} instances)")


if __name__ == "__main__":
    main()
