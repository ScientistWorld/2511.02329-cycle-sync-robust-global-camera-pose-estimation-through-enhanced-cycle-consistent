"""Synthetic camera-location data (the paper's Eqs. 9-10).

Ground-truth camera locations are i.i.d. N(0, I_3); the viewing graph is
Erdos-Renyi with edge probability p. Each edge (i, j), i < j, observes
Normalize(t_i - t_j + sigma * eps) with probability 1 - q. With probability q
it observes an outlier: Normalize(eps) under uniform corruption, or
Normalize(t_i^c - t_j^c + sigma * eps) for an alternative camera cloud t^c
under the cycle-consistent adversarial model.

This module is public. Use it to generate as many development instances as
you like; the benchmark's fixed instances are described in
``briefing/evaluation.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

EXPERIMENTS = {
    "uniform_high_noise": {"n": 100, "p": 0.5, "q": 0.7, "sigma": 0.2, "corruption": "uniform"},
    "adversarial_high_noise": {"n": 100, "p": 0.5, "q": 0.45, "sigma": 0.2, "corruption": "adversarial"},
}


@dataclass(frozen=True)
class SyntheticProblem:
    n: int
    p: float
    q: float
    sigma: float
    corruption: str
    seed: object
    locations: np.ndarray
    edges: np.ndarray
    directions: np.ndarray
    corrupted: np.ndarray


def normalize(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    norm = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / np.maximum(norm, eps)


def generate_problem(
    n: int = 100,
    p: float = 0.5,
    q: float = 0.7,
    sigma: float = 0.2,
    corruption: str = "uniform",
    seed: object = 0,
) -> SyntheticProblem:
    """Generate one instance; ``seed`` is anything ``np.random.default_rng`` accepts."""

    if corruption not in {"uniform", "adversarial"}:
        raise ValueError("corruption must be 'uniform' or 'adversarial'")

    rng = np.random.default_rng(seed)
    locations = rng.normal(size=(n, 3))
    alt_locations = rng.normal(size=(n, 3))

    mask = rng.random((n, n)) < p
    ii, jj = np.where(np.triu(mask, 1))
    edges = np.stack([ii, jj], axis=1).astype(np.int64)
    if edges.size == 0:
        raise ValueError("generated graph has no edges")

    clean = locations[ii] - locations[jj]
    clean_noisy = clean + sigma * rng.normal(size=clean.shape)
    bad = rng.random(len(edges)) < q
    if corruption == "uniform":
        corrupted_vecs = rng.normal(size=clean.shape)
    else:
        corrupted_vecs = alt_locations[ii] - alt_locations[jj]
        corrupted_vecs = corrupted_vecs + sigma * rng.normal(size=clean.shape)

    observed = clean_noisy.copy()
    observed[bad] = corrupted_vecs[bad]
    directions = normalize(observed)

    return SyntheticProblem(
        n=n,
        p=p,
        q=q,
        sigma=sigma,
        corruption=corruption,
        seed=seed,
        locations=locations,
        edges=edges,
        directions=directions,
        corrupted=bad,
    )


def generate_experiment(name: str, seed: object) -> SyntheticProblem:
    cfg = EXPERIMENTS[name]
    return generate_problem(seed=seed, **cfg)


def save_instance_set(path: str | Path, problems: list[SyntheticProblem]) -> None:
    """Store a list of instances in one .npz (keys suffixed with _000, _001, ...)."""

    arrays: dict[str, np.ndarray] = {"count": np.int64(len(problems))}
    for k, prob in enumerate(problems):
        arrays[f"n_{k:03d}"] = np.int64(prob.n)
        arrays[f"edges_{k:03d}"] = prob.edges.astype(np.int32)
        arrays[f"directions_{k:03d}"] = prob.directions.astype(np.float64)
        arrays[f"locations_{k:03d}"] = prob.locations.astype(np.float64)
        arrays[f"corrupted_{k:03d}"] = prob.corrupted.astype(bool)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **arrays)


def load_instance_set(path: str | Path) -> list[dict[str, np.ndarray]]:
    """Load a set written by ``save_instance_set``.

    Each entry has ``n``, ``edges``, ``directions`` (the solver inputs) and, for
    the public train set, ``locations`` (ground truth) and ``corrupted``.
    """

    out = []
    with np.load(path, allow_pickle=False) as z:
        for k in range(int(z["count"])):
            item = {
                "n": int(z[f"n_{k:03d}"]),
                "edges": np.asarray(z[f"edges_{k:03d}"], dtype=np.int64),
                "directions": np.asarray(z[f"directions_{k:03d}"], dtype=float),
            }
            for key in ("locations", "corrupted"):
                name = f"{key}_{k:03d}"
                if name in z.files:
                    item[key] = np.asarray(z[name])
            out.append(item)
    return out
