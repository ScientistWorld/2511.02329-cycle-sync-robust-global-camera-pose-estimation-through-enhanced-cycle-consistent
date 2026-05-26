"""Synthetic camera-location data for Cycle-Sync experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np


@dataclass(frozen=True)
class SyntheticProblem:
    n: int
    p: float
    q: float
    sigma: float
    corruption: str
    seed: int
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
    seed: int = 0,
) -> SyntheticProblem:
    """Generate the paper's Erdos-Renyi synthetic camera-location model.

    Clean directions follow Eq. (9). For ``corruption='adversarial'``,
    corrupted directions follow Eq. (10) using an alternative camera cloud.
    """

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


def save_problem(problem: SyntheticProblem, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        n=problem.n,
        p=problem.p,
        q=problem.q,
        sigma=problem.sigma,
        corruption=problem.corruption,
        seed=problem.seed,
        locations=problem.locations,
        edges=problem.edges,
        directions=problem.directions,
        corrupted=problem.corrupted,
    )


def load_problem(path: str | Path) -> SyntheticProblem:
    with np.load(path, allow_pickle=False) as z:
        return SyntheticProblem(
            n=int(z["n"]),
            p=float(z["p"]),
            q=float(z["q"]),
            sigma=float(z["sigma"]),
            corruption=str(z["corruption"]),
            seed=int(z["seed"]),
            locations=z["locations"],
            edges=z["edges"],
            directions=z["directions"],
            corrupted=z["corrupted"],
        )


def write_manifest(problems: list[Path], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([str(p) for p in problems], indent=2) + "\n")
