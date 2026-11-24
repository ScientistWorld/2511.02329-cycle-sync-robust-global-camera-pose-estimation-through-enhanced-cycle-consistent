"""Cycle-Sync + an L2 refit on the edges Cycle-Sync trusts most.

The paper's final Welsch weights exp(-4h)/(h+delta) behave like 1/h for small
h, so the last solve is dominated by a handful of edges and is close to an L1
fit on the inliers. With sigma=0.2 noise an unweighted least-squares fit on a
confident inlier set should average the noise better. The inlier set is the
top rho * (1 - q) * |E| edges by Cycle-Sync's own final weight (q is the
benchmark's public corruption rate); no ground truth or corruption labels are
used. The subset is grown until it connects every camera.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy import sparse
from scipy.sparse.csgraph import connected_components

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from art import EXPERIMENTS, derive  # noqa: E402
from method.cycle_sync import weighted_location_solve  # noqa: E402

RHOS = {"r050": 0.5, "r075": 0.75, "r100": 1.0}


def connected(n: int, edges: np.ndarray) -> bool:
    g = sparse.coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(n, n))
    return connected_components(g, directed=False)[0] == 1


def refit(rho: float):
    def fn(exp, a):
        n = int(a["n"])
        edges = a["edges"]
        m = len(edges)
        k = max(int(round(rho * (1.0 - EXPERIMENTS[exp]["q"]) * m)), n)
        order = np.argsort(-a["weights"], kind="stable")
        while not connected(n, edges[order[:k]]) and k < m:
            k = min(m, int(k * 1.1) + 1)
        w = np.zeros(m)
        w[order[:k]] = 1.0
        a["locations_est"] = weighted_location_solve(n, edges, a["directions"], w)[0]
        return a

    return fn


def main() -> None:
    for tag, rho in RHOS.items():
        derive("cycle_sync", f"cycle_sync_refit_{tag}", refit(rho))


if __name__ == "__main__":
    main()
