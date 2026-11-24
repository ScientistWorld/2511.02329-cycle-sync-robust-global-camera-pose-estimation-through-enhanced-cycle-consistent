"""Hardening variant: Cycle-Sync followed by an unweighted least-squares refit.

After the paper's Cycle-Sync run, keep the rho * (1 - q) * |E| edges with the
largest final Cycle-Sync weight (q is the setting's public corruption rate,
read from the experiment name in the input file), grow the set until it
connects every camera, and solve the constrained least-squares problem with
unit weights on that set. With sigma = 0.2 noise, averaging over the trusted
edges should beat the final, very peaked Welsch weights. No ground truth or
corruption labels are used.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
from scipy import sparse
from scipy.sparse.csgraph import connected_components

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from method.cycle_sync import cycle_sync, weighted_location_solve  # noqa: E402

Q = {"uniform_high_noise": 0.7, "adversarial_high_noise": 0.45}


def connected(n: int, edges: np.ndarray) -> bool:
    g = sparse.coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(n, n))
    return connected_components(g, directed=False)[0] == 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--rho", type=float, default=1.0)
    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(Path(args.input_dir).glob("*.npz")):
        with np.load(path, allow_pickle=False) as z:
            n = int(z["n"])
            edges = np.asarray(z["edges"], dtype=np.int64)
            directions = np.asarray(z["directions"], dtype=float)
            exp = str(z["experiment"])
        res = cycle_sync(n, edges, directions)
        m = len(edges)
        k = max(int(round(args.rho * (1.0 - Q.get(exp, 0.5)) * m)), n)
        order = np.argsort(-res["weights"], kind="stable")
        while k < m and not connected(n, edges[order[:k]]):
            k = min(m, int(k * 1.1) + 1)
        w = np.full(m, 1e-12)
        w[order[:k]] = 1.0
        locations = weighted_location_solve(n, edges, directions, w, t0=res["locations"])[0]
        np.savez(out_dir / path.name, locations=locations)


if __name__ == "__main__":
    main()
