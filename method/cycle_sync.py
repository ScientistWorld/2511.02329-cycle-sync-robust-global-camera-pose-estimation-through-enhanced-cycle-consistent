"""Cycle-Sync location solver.

This implements Algorithm 1 from "Cycle-Sync: Robust Global Camera Pose
Estimation through Enhanced Cycle-Consistent Synchronization" for synthetic
camera-location measurements.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve


def _normalize(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    return x / np.maximum(np.linalg.norm(x, axis=-1, keepdims=True), eps)


@dataclass
class GraphData:
    n: int
    edges: np.ndarray
    directions: np.ndarray
    edge_index: dict[tuple[int, int], int]
    neighbors: list[set[int]]
    common: list[np.ndarray]


def build_graph(n: int, edges: np.ndarray, directions: np.ndarray) -> GraphData:
    edge_index: dict[tuple[int, int], int] = {}
    neighbors = [set() for _ in range(n)]
    for idx, (i, j) in enumerate(edges):
        i, j = int(i), int(j)
        if i > j:
            raise ValueError("edges must be stored with i < j")
        edge_index[(i, j)] = idx
        neighbors[i].add(j)
        neighbors[j].add(i)
    common = []
    for i, j in edges:
        common.append(np.array(sorted(neighbors[int(i)] & neighbors[int(j)]), dtype=np.int64))
    return GraphData(n, edges.astype(np.int64), directions.astype(float), edge_index, neighbors, common)


def edge_direction(graph: GraphData, a: int, b: int) -> np.ndarray:
    if a < b:
        return graph.directions[graph.edge_index[(a, b)]]
    return -graph.directions[graph.edge_index[(b, a)]]


def edge_id(graph: GraphData, a: int, b: int) -> int:
    if a < b:
        return graph.edge_index[(a, b)]
    return graph.edge_index[(b, a)]


def _well_shaped(g1: np.ndarray, g2: np.ndarray, min_sin: float = 0.6) -> bool:
    return np.linalg.norm(np.cross(g1, g2)) >= min_sin


def _aab_inconsistency(gij: np.ndarray, gik: np.ndarray, gjk: np.ndarray) -> float:
    """AAB-style geodesic inconsistency for a bearing 3-cycle.

    For the edge ``ij`` and auxiliary node ``k``, AAB measures the spherical
    distance from the observed direction ``gamma_ij`` to the set of directions
    that can close a triangle with positive scales:

        alpha_ij gamma + alpha_jk gamma_jk + alpha_ki gamma_ki = 0.

    With the orientation used here, that feasible set is the great-circle arc
    between ``gamma_ik`` and ``gamma_kj``. The closest point is the normalized
    projection onto their span when the projection lies in the positive cone;
    otherwise it is the nearer endpoint of the arc.
    """

    a = gik
    b = -gjk
    gram = np.array([[1.0, float(np.dot(a, b))], [float(np.dot(a, b)), 1.0]])
    if abs(np.linalg.det(gram)) < 1e-12:
        return np.nan

    rhs = np.array([float(np.dot(gij, a)), float(np.dot(gij, b))])
    coeff = np.linalg.solve(gram, rhs)
    candidates = [a, b]
    if coeff[0] >= 0.0 and coeff[1] >= 0.0:
        projected = coeff[0] * a + coeff[1] * b
        norm = np.linalg.norm(projected)
        if norm > 1e-12:
            candidates.append(projected / norm)

    best_cos = max(float(np.dot(gij, candidate)) for candidate in candidates)
    return float(np.arccos(np.clip(best_cos, -1.0, 1.0)) / np.pi)


def truncated_aab_scores(
    graph: GraphData,
    iterations: int = 5,
    beta0: float = 1.0,
    beta_growth: float = 1.4,
) -> np.ndarray:
    """Estimate angular corruption using well-shaped 3-cycles.

    The paper cites AAB's closed-form geodesic distance. For this reproducible
    implementation, the same truncated AAB update is instantiated with the
    standard coplanarity residual of a bearing triangle.
    """

    m = len(graph.edges)
    dvals: list[list[tuple[int, float]]] = [[] for _ in range(m)]
    for e, (i, j) in enumerate(graph.edges):
        gij = edge_direction(graph, int(i), int(j))
        for k in graph.common[e]:
            gik = edge_direction(graph, int(i), int(k))
            gjk = edge_direction(graph, int(j), int(k))
            if not _well_shaped(gik, gjk):
                continue
            val = _aab_inconsistency(gij, gik, gjk)
            if np.isfinite(val):
                dvals[e].append((int(k), val))

    scores = np.array([np.mean([v for _, v in vals]) if vals else 1.0 for vals in dvals], dtype=float)
    beta = beta0
    for _ in range(iterations):
        new_scores = scores.copy()
        for e, (i, j) in enumerate(graph.edges):
            vals = dvals[e]
            if not vals:
                continue
            weights = []
            residuals = []
            for k, val in vals:
                w = np.exp(-beta * (scores[edge_id(graph, int(i), k)] + scores[edge_id(graph, int(j), k)]))
                weights.append(w)
                residuals.append(val)
            weights_arr = np.asarray(weights)
            z = float(weights_arr.sum())
            if z > 1e-12:
                new_scores[e] = float(np.dot(weights_arr, residuals) / z)
        scores = new_scores
        beta *= beta_growth
    return scores


def weighted_location_solve(
    n: int,
    edges: np.ndarray,
    directions: np.ndarray,
    weights: np.ndarray,
    inner_iters: int = 20,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Solve Eq. (3) by alternating alpha updates and sparse WLS location solves."""

    m = len(edges)
    alpha = np.ones(m, dtype=float)
    locations = np.zeros((n, 3), dtype=float)
    rows = []
    cols = []
    data = []
    for e, (i, j) in enumerate(edges):
        w = float(max(weights[e], 1e-12))
        rows.extend([e, e])
        cols.extend([int(i), int(j)])
        data.extend([np.sqrt(w), -np.sqrt(w)])
    a = sparse.coo_matrix((data, (rows, cols)), shape=(m, n)).tocsr()
    ata = (a.T @ a).tolil()
    # Gauge fixing for sum_i t_i = 0 by replacing one normal equation.
    ata[0, :] = 1.0
    ata = ata.tocsr()

    for _ in range(inner_iters):
        b = np.sqrt(np.maximum(weights, 1e-12))[:, None] * alpha[:, None] * directions
        rhs = a.T @ b
        rhs[0, :] = 0.0
        for dim in range(3):
            locations[:, dim] = spsolve(ata, rhs[:, dim])
        diff = locations[edges[:, 0]] - locations[edges[:, 1]]
        new_alpha = np.maximum(1.0, np.sum(diff * directions, axis=1))
        if np.max(np.abs(new_alpha - alpha)) < 1e-7:
            alpha = new_alpha
            break
        alpha = new_alpha
    residuals = np.linalg.norm(locations[edges[:, 0]] - locations[edges[:, 1]] - alpha[:, None] * directions, axis=1)
    return locations, alpha, residuals


def cycle_scores(graph: GraphData, locations: np.ndarray, residuals: np.ndarray, beta: float = 20.0) -> np.ndarray:
    m = len(graph.edges)
    scores = np.zeros(m, dtype=float)
    for e, (i, j) in enumerate(graph.edges):
        vals = []
        weights = []
        i = int(i)
        j = int(j)
        for k in graph.common[e]:
            k = int(k)
            gij = edge_direction(graph, i, j)
            gjk = edge_direction(graph, j, k)
            gki = edge_direction(graph, k, i)
            dij = np.linalg.norm(locations[i] - locations[j])
            djk = np.linalg.norm(locations[j] - locations[k])
            dki = np.linalg.norm(locations[k] - locations[i])
            val = np.linalg.norm(dij * gij + djk * gjk + dki * gki)
            w = np.exp(-beta * (residuals[edge_id(graph, i, k)] + residuals[edge_id(graph, j, k)]))
            vals.append(val)
            weights.append(w)
        if weights:
            weights_arr = np.asarray(weights)
            z = float(weights_arr.sum())
            scores[e] = float(np.dot(weights_arr, vals) / z) if z > 1e-12 else float(np.mean(vals))
        else:
            scores[e] = residuals[e]
    return scores


def cycle_sync(
    n: int,
    edges: np.ndarray,
    directions: np.ndarray,
    t_max: int = 20,
    beta: float = 20.0,
    delta: float = 1e-8,
    init: str = "t-aab",
    lambda_schedule: str = "t_over_t_plus_10",
) -> dict[str, np.ndarray]:
    """Run Algorithm 1 with the paper's annealing schedule or ablation variants."""

    graph = build_graph(n, edges, directions)
    if init == "uniform":
        corruption = np.zeros(len(edges), dtype=float)
    elif init == "t-aab":
        corruption = truncated_aab_scores(graph)
    else:
        raise ValueError("init must be 't-aab' or 'uniform'")

    weights = np.exp(-20.0 * corruption)
    trace = []
    locations = np.zeros((n, 3), dtype=float)
    residuals = np.ones(len(edges), dtype=float)
    alpha = np.ones(len(edges), dtype=float)
    for t in range(1, t_max + 1):
        locations, alpha, residuals = weighted_location_solve(n, edges, directions, weights)
        s_cycle = cycle_scores(graph, locations, residuals, beta=beta)
        if lambda_schedule == "t_over_t_plus_10":
            lam = t / (t + 10.0)
        elif lambda_schedule == "ten_over_t_plus_10":
            lam = 10.0 / (t + 10.0)
        elif lambda_schedule == "one":
            lam = 1.0
        elif lambda_schedule == "t_over_t_plus_5":
            lam = t / (t + 5.0)
        else:
            raise ValueError(
                "lambda_schedule must be one of "
                "'t_over_t_plus_10', 'ten_over_t_plus_10', 'one', or 't_over_t_plus_5'"
            )
        h = (1.0 - lam) * residuals + lam * s_cycle
        weights = np.exp(-4.0 * h) / (h + delta)
        weights = np.clip(weights, 1e-8, 1e8)
        trace.append(float(np.median(residuals)))
    return {
        "locations": locations,
        "alpha": alpha,
        "residuals": residuals,
        "weights": weights,
        "trace": np.asarray(trace),
        "init_scores": corruption,
    }


def residual_irls(
    n: int,
    edges: np.ndarray,
    directions: np.ndarray,
    t_max: int = 20,
    delta: float = 1e-8,
) -> dict[str, np.ndarray]:
    """A Welsch IRLS baseline without cycle-consistency weighting."""

    weights = np.ones(len(edges), dtype=float)
    trace = []
    locations = np.zeros((n, 3), dtype=float)
    residuals = np.ones(len(edges), dtype=float)
    alpha = np.ones(len(edges), dtype=float)
    for _ in range(t_max):
        locations, alpha, residuals = weighted_location_solve(n, edges, directions, weights)
        weights = np.exp(-4.0 * residuals) / (residuals + delta)
        weights = np.clip(weights, 1e-8, 1e8)
        trace.append(float(np.median(residuals)))
    return {
        "locations": locations,
        "alpha": alpha,
        "residuals": residuals,
        "weights": weights,
        "trace": np.asarray(trace),
    }
