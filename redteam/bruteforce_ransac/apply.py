"""Budgeted brute-force search over inlier sets (hypothesize and verify).

Instead of message passing over cycles, sample random connected edge subsets,
solve the least-squares location problem on each, count edges whose observed
direction agrees with the hypothesis within an angular threshold, keep the
best hypothesis and refit on its inliers. This is the exhaustive search the
paper's reweighting replaces; with ~2475 edges the inlier-set space is
2^2475, so only a fixed budget of hypotheses is tried. Uses only n, edges and
directions from each instance.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy import sparse
from scipy.sparse.csgraph import connected_components

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from art import derive  # noqa: E402
from method.cycle_sync import weighted_location_solve  # noqa: E402

HYPOTHESES = 400
SUBSET = 300
THRESHOLD = 0.25  # radians
rng = np.random.default_rng(12345)


def connected(n: int, edges: np.ndarray) -> bool:
    g = sparse.coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(n, n))
    return connected_components(g, directed=False)[0] == 1


def angular_residual(locs: np.ndarray, edges: np.ndarray, dirs: np.ndarray) -> np.ndarray:
    d = locs[edges[:, 0]] - locs[edges[:, 1]]
    cos = np.sum(d * dirs, axis=1) / np.maximum(np.linalg.norm(d, axis=1), 1e-12)
    return np.arccos(np.clip(cos, -1.0, 1.0))


def ransac(exp, a):
    n = int(a["n"])
    edges = a["edges"]
    dirs = a["directions"]
    m = len(edges)
    best_cnt, best_locs, best_inl = -1, None, None
    for _ in range(HYPOTHESES):
        for _ in range(50):
            sel = rng.choice(m, size=SUBSET, replace=False)
            if connected(n, edges[sel]):
                break
        w = np.zeros(m)
        w[sel] = 1.0
        locs = weighted_location_solve(n, edges, dirs, w)[0]
        inl = angular_residual(locs, edges, dirs) < THRESHOLD
        if inl.sum() > best_cnt:
            best_cnt, best_locs, best_inl = int(inl.sum()), locs, inl
    if best_inl.sum() >= n and connected(n, edges[best_inl]):
        best_locs = weighted_location_solve(n, edges, dirs, best_inl.astype(float))[0]
    out = {k: v for k, v in a.items() if k not in {"residuals", "weights", "trace", "init_scores", "lambda_schedule"}}
    out["locations_est"] = best_locs
    print(exp, "best inlier count", best_cnt, "of", m, flush=True)
    return out


def main() -> None:
    derive("cycle_sync", "cycle_sync", ransac)


if __name__ == "__main__":
    main()
