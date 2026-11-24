"""Cycle-Sync location solver.

Implements Algorithm 1 of "Cycle-Sync: Robust Global Camera Pose Estimation
through Enhanced Cycle-Consistent Synchronization" (Li, Shi, Lerman) for
camera-location estimation from pairwise unit directions:

  1. T-AAB initialisation: AAB-style geodesic cycle inconsistencies over
     well-shaped 3-cycles, aggregated by iteratively reweighted message passing;
     initial weights w = exp(-20 s).
  2. For t = 1..t_max:
       - weighted least squares (Eq. 3) over locations and per-edge scales,
         subject to alpha_ij >= 1 and sum_i t_i = 0 (solved exactly);
       - residuals r_ij = ||t_i - t_j - alpha_ij gamma_ij||;
       - cycle corruption scores s_ij (Eqs. 6-7) using distances estimated in
         the current iteration and cycle weights exp(-beta (r_ik + r_jk));
       - h = (1 - lambda_t) r + lambda_t s, w = exp(-4 h) / (h + delta).

Everything is vectorised over edges and 3-cycles.

Two legacy switches reproduce the pre-hardening implementation for comparison
only: ``wls="alternating"`` (at most 20 alternating alpha / location sweeps,
restarted from alpha = 1 at every outer iteration) and ``softmin="legacy"``
(falls back to an unweighted cycle mean when the unnormalised Eq. 6 weights
underflow below 1e-12).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import linalg as sla

WEIGHT_MIN = 1e-8
WEIGHT_MAX = 1e8

SCHEDULES = {
    "t_over_t_plus_10": lambda t: t / (t + 10.0),
    "ten_over_t_plus_10": lambda t: 10.0 / (t + 10.0),
    "one": lambda t: 1.0,
    "t_over_t_plus_5": lambda t: t / (t + 5.0),
    "zero": lambda t: 0.0,
}


@dataclass
class Graph:
    """Viewing graph with oriented directions and its list of 3-cycles.

    ``dir(a, b)`` denotes the observed unit direction approximating
    (t_a - t_b) / ||t_a - t_b||; edge ``e = (i, j)`` with ``i < j`` stores
    ``gamma_e = dir(i, j)``. Each 3-cycle entry is (edge ij, third vertex k).
    """

    n: int
    m: int
    I: np.ndarray
    J: np.ndarray
    gamma: np.ndarray
    t_edge: np.ndarray
    t_ik: np.ndarray
    t_jk: np.ndarray
    g_ij: np.ndarray
    g_ik: np.ndarray
    g_jk: np.ndarray
    has_cycle: np.ndarray


def build_graph(n: int, edges: np.ndarray, directions: np.ndarray) -> Graph:
    edges = np.asarray(edges, dtype=np.int64)
    gamma = np.asarray(directions, dtype=float)
    if edges.ndim != 2 or edges.shape[1] != 2:
        raise ValueError("edges must have shape (m, 2)")
    if gamma.shape != (len(edges), 3):
        raise ValueError("directions must have shape (m, 3)")
    if np.any(edges[:, 0] >= edges[:, 1]):
        raise ValueError("edges must be stored with i < j")
    n = int(n)
    m = len(edges)
    I = edges[:, 0]
    J = edges[:, 1]
    eid = np.full((n, n), -1, dtype=np.int64)
    eid[I, J] = np.arange(m)
    eid[J, I] = np.arange(m)
    adj = eid >= 0
    common = adj[I] & adj[J]
    t_edge, t_k = np.nonzero(common)  # row-major: t_edge is sorted
    ti = I[t_edge]
    tj = J[t_edge]
    t_ik = eid[ti, t_k]
    t_jk = eid[tj, t_k]
    g_ij = gamma[t_edge]
    g_ik = np.where((ti < t_k)[:, None], gamma[t_ik], -gamma[t_ik])
    g_jk = np.where((tj < t_k)[:, None], gamma[t_jk], -gamma[t_jk])
    has_cycle = np.bincount(t_edge, minlength=m) > 0
    return Graph(n, m, I, J, gamma, t_edge, t_ik, t_jk, g_ij, g_ik, g_jk, has_cycle)


def _segment_weighted_mean(
    seg: np.ndarray,
    m: int,
    cost: np.ndarray,
    vals: np.ndarray,
    beta: float,
    legacy: bool = False,
) -> np.ndarray:
    """Per-edge sum_k exp(-beta cost_k) vals_k / sum_k exp(-beta cost_k).

    ``seg`` must be sorted. The default form subtracts the per-edge minimum
    cost before exponentiating, which leaves the normalised Eq. 6 average
    unchanged and avoids underflow. Edges without entries return NaN.
    """

    out = np.full(m, np.nan)
    if len(seg) == 0:
        return out
    if legacy:
        w = np.exp(-beta * cost)
        num = np.bincount(seg, weights=w * vals, minlength=m)
        den = np.bincount(seg, weights=w, minlength=m)
        cnt = np.bincount(seg, minlength=m)
        plain = np.bincount(seg, weights=vals, minlength=m)
        has = cnt > 0
        good = has & (den > 1e-12)
        out[good] = num[good] / den[good]
        fallback = has & ~good
        out[fallback] = plain[fallback] / cnt[fallback]
        return out
    uniq, starts = np.unique(seg, return_index=True)
    seg_min = np.full(m, np.inf)
    seg_min[uniq] = np.minimum.reduceat(cost, starts)
    w = np.exp(-beta * (cost - seg_min[seg]))
    num = np.bincount(seg, weights=w * vals, minlength=m)
    den = np.bincount(seg, weights=w, minlength=m)
    out[uniq] = num[uniq] / den[uniq]
    return out


def aab_inconsistencies(graph: Graph, min_sin: float = 0.6) -> tuple[np.ndarray, np.ndarray]:
    """AAB-style geodesic inconsistency of every well-shaped 3-cycle.

    For edge ij and vertex k the feasible directions closing the triangle with
    positive scales form the great-circle arc between dir(i, k) and dir(k, j).
    The inconsistency is the geodesic distance (divided by pi) from gamma_ij to
    that arc. Only triangles whose angle between dir(i, k) and dir(j, k) lies
    in [arcsin(min_sin), pi - arcsin(min_sin)] are used (T-AAB).
    Returns (mask over cycles, inconsistency per kept cycle).
    """

    a = graph.g_ik
    b = -graph.g_jk
    g = graph.g_ij
    cross = np.linalg.norm(np.cross(graph.g_ik, graph.g_jk), axis=1)
    c = np.sum(a * b, axis=1)
    det = 1.0 - c * c
    ok = (cross >= min_sin) & (np.abs(det) >= 1e-12)
    safe_det = np.where(ok, det, 1.0)
    ga = np.sum(g * a, axis=1)
    gb = np.sum(g * b, axis=1)
    c0 = (ga - c * gb) / safe_det
    c1 = (gb - c * ga) / safe_det
    proj = c0[:, None] * a + c1[:, None] * b
    pn = np.linalg.norm(proj, axis=1)
    inside = (c0 >= 0.0) & (c1 >= 0.0) & (pn > 1e-12)
    cos_proj = np.where(inside, np.sum(g * proj, axis=1) / np.where(pn > 1e-12, pn, 1.0), -np.inf)
    best = np.maximum(np.maximum(ga, gb), cos_proj)
    d = np.arccos(np.clip(best, -1.0, 1.0)) / np.pi
    return ok, d[ok]


def truncated_aab_scores(
    graph: Graph,
    iterations: int = 5,
    beta0: float = 1.0,
    beta_growth: float = 1.4,
) -> np.ndarray:
    """T-AAB estimate of the angular corruption level of every edge."""

    ok, d = aab_inconsistencies(graph)
    te = graph.t_edge[ok]
    e_ik = graph.t_ik[ok]
    e_jk = graph.t_jk[ok]
    m = graph.m
    cnt = np.bincount(te, minlength=m)
    has = cnt > 0
    scores = np.ones(m, dtype=float)
    scores[has] = np.bincount(te, weights=d, minlength=m)[has] / cnt[has]
    beta = beta0
    for _ in range(iterations):
        w = np.exp(-beta * (scores[e_ik] + scores[e_jk]))
        num = np.bincount(te, weights=w * d, minlength=m)
        den = np.bincount(te, weights=w, minlength=m)
        upd = has & (den > 1e-12)
        new_scores = scores.copy()
        new_scores[upd] = num[upd] / den[upd]
        scores = new_scores
        beta *= beta_growth
    return scores


def _scatter_edges(I: np.ndarray, J: np.ndarray, vec: np.ndarray, n: int) -> np.ndarray:
    """Return B^T vec: out[i] += vec_e for e=(i, j), out[j] -= vec_e."""

    out = np.empty((n, vec.shape[1]))
    for c in range(vec.shape[1]):
        out[:, c] = np.bincount(I, weights=vec[:, c], minlength=n) - np.bincount(J, weights=vec[:, c], minlength=n)
    return out


def _solve_spd(mat: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    try:
        factor = sla.cho_factor(mat, lower=True, check_finite=False)
        sol = sla.cho_solve(factor, rhs, check_finite=False)
        if np.all(np.isfinite(sol)):
            return sol
    except (np.linalg.LinAlgError, ValueError):
        pass
    return np.linalg.lstsq(mat, rhs, rcond=None)[0]


def _wls_objective(t: np.ndarray, I: np.ndarray, J: np.ndarray, gamma: np.ndarray, w: np.ndarray):
    d = t[I] - t[J]
    p = np.sum(d * gamma, axis=1)
    alpha = np.maximum(1.0, p)
    res = d - alpha[:, None] * gamma
    return float(np.sum(w * np.sum(res * res, axis=1))), d, p, alpha, res


def wls_exact(
    n: int,
    I: np.ndarray,
    J: np.ndarray,
    gamma: np.ndarray,
    weights: np.ndarray,
    t0: np.ndarray | None = None,
    max_iter: int = 100,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Exact solution of Eq. (3): min sum_e w_e ||t_i - t_j - alpha_e gamma_e||^2
    subject to alpha_e >= 1 and sum_i t_i = 0.

    Eliminating alpha_e = max(1, gamma_e^T (t_i - t_j)) leaves a convex,
    continuously differentiable, piecewise-quadratic function of the locations,
    minimised by a generalised Newton method with Armijo backtracking. On a
    fixed active set the function is quadratic, so the iteration stops at the
    exact minimiser once the active set settles. One camera is grounded to fix
    the translation gauge; the result is re-centred.
    """

    m = len(I)
    w = np.asarray(weights, dtype=float)
    deg = np.bincount(I, weights=w, minlength=n) + np.bincount(J, weights=w, minlength=n)
    ground = int(np.argmax(deg))
    keep = np.ones(3 * n, dtype=bool)
    keep[3 * ground : 3 * ground + 3] = False
    gg = gamma[:, :, None] * gamma[:, None, :]
    eye = np.eye(3)
    ar = np.arange(n)

    t = np.zeros((n, 3)) if t0 is None else np.array(t0, dtype=float, copy=True)
    t -= t.mean(axis=0)
    f_val, d, p, alpha, res = _wls_objective(t, I, J, gamma, w)
    for _ in range(max_iter):
        active = p < 1.0
        grad = _scatter_edges(I, J, 2.0 * w[:, None] * res, n)
        blocks = 2.0 * w[:, None, None] * (eye[None, :, :] - (~active).astype(float)[:, None, None] * gg)
        h4 = np.zeros((n, n, 3, 3))
        h4[I, J] = -blocks
        h4[J, I] = -blocks
        diag = np.zeros((n, 3, 3))
        np.add.at(diag, I, blocks)
        np.add.at(diag, J, blocks)
        h4[ar, ar] = diag
        hess = h4.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n)
        step = np.zeros(3 * n)
        step[keep] = -_solve_spd(hess[np.ix_(keep, keep)], grad.reshape(-1)[keep])
        step = step.reshape(n, 3)
        slope = float(np.sum(grad * step))
        if not np.isfinite(slope) or slope >= 0.0:
            break
        s = 1.0
        accepted = False
        for _ls in range(50):
            t_new = t + s * step
            f_new, d_new, p_new, alpha_new, res_new = _wls_objective(t_new, I, J, gamma, w)
            if f_new <= f_val + 1e-4 * s * slope:
                accepted = True
                break
            s *= 0.5
        if not accepted:
            break
        t = t_new - t_new.mean(axis=0)
        same_active = np.array_equal(p_new < 1.0, active)
        rel_decrease = (f_val - f_new) / max(abs(f_val), 1e-300)
        small_step = s * float(np.max(np.abs(step))) <= 1e-12 * max(1.0, float(np.max(np.abs(t))))
        f_val, d, p, alpha, res = f_new, d_new, p_new, alpha_new, res_new
        if (s == 1.0 and same_active) or small_step or rel_decrease < 1e-15:
            break
    residuals = np.linalg.norm(res, axis=1)
    return t, alpha, residuals


def wls_alternating(
    n: int,
    I: np.ndarray,
    J: np.ndarray,
    gamma: np.ndarray,
    weights: np.ndarray,
    inner_iters: int = 20,
    tol: float = 1e-7,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Legacy approximate solver: alternate location solves and alpha
    projections, starting from alpha = 1, for at most ``inner_iters`` sweeps."""

    m = len(I)
    w = np.maximum(np.asarray(weights, dtype=float), 1e-12)
    lap = np.zeros((n, n))
    lap[I, J] = -w
    lap[J, I] = -w
    lap[np.arange(n), np.arange(n)] = np.bincount(I, weights=w, minlength=n) + np.bincount(J, weights=w, minlength=n)
    keep = np.arange(1, n)
    sub = lap[np.ix_(keep, keep)]
    try:
        factor = sla.cho_factor(sub, lower=True, check_finite=False)
        solve = lambda rhs: sla.cho_solve(factor, rhs, check_finite=False)  # noqa: E731
    except (np.linalg.LinAlgError, ValueError):
        solve = lambda rhs: np.linalg.lstsq(sub, rhs, rcond=None)[0]  # noqa: E731
    alpha = np.ones(m)
    t = np.zeros((n, 3))
    for _ in range(inner_iters):
        rhs = _scatter_edges(I, J, (w * alpha)[:, None] * gamma, n)
        t = np.zeros((n, 3))
        t[keep] = solve(rhs[keep])
        t -= t.mean(axis=0)
        new_alpha = np.maximum(1.0, np.sum((t[I] - t[J]) * gamma, axis=1))
        done = float(np.max(np.abs(new_alpha - alpha))) < tol
        alpha = new_alpha
        if done:
            break
    residuals = np.linalg.norm(t[I] - t[J] - alpha[:, None] * gamma, axis=1)
    return t, alpha, residuals


def weighted_location_solve(
    n: int,
    edges: np.ndarray,
    directions: np.ndarray,
    weights: np.ndarray,
    method: str = "exact",
    t0: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Solve Eq. (3); returns (locations, alpha, residuals)."""

    edges = np.asarray(edges, dtype=np.int64)
    gamma = np.asarray(directions, dtype=float)
    I, J = edges[:, 0], edges[:, 1]
    if method == "exact":
        return wls_exact(int(n), I, J, gamma, weights, t0=t0)
    if method == "alternating":
        return wls_alternating(int(n), I, J, gamma, weights)
    raise ValueError("method must be 'exact' or 'alternating'")


def cycle_scores(
    graph: Graph,
    locations: np.ndarray,
    residuals: np.ndarray,
    beta: float = 20.0,
    legacy: bool = False,
) -> np.ndarray:
    """Eqs. (6)-(7): weighted average of distance-based 3-cycle inconsistencies."""

    dist = np.linalg.norm(locations[graph.I] - locations[graph.J], axis=1)
    te = graph.t_edge
    vec = (
        dist[te][:, None] * graph.g_ij
        + dist[graph.t_jk][:, None] * graph.g_jk
        - dist[graph.t_ik][:, None] * graph.g_ik
    )
    dvals = np.linalg.norm(vec, axis=1)
    cost = residuals[graph.t_ik] + residuals[graph.t_jk]
    scores = _segment_weighted_mean(te, graph.m, cost, dvals, beta, legacy=legacy)
    no_cycle = ~graph.has_cycle
    scores[no_cycle] = residuals[no_cycle]
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
    wls: str = "exact",
    softmin: str = "stable",
) -> dict[str, np.ndarray]:
    """Run Algorithm 1 with the paper's schedule (or an ablation schedule)."""

    if lambda_schedule not in SCHEDULES:
        raise ValueError(f"lambda_schedule must be one of {sorted(SCHEDULES)}")
    if softmin not in {"stable", "legacy"}:
        raise ValueError("softmin must be 'stable' or 'legacy'")
    schedule = SCHEDULES[lambda_schedule]
    graph = build_graph(n, edges, directions)
    if init == "uniform":
        corruption = np.zeros(graph.m, dtype=float)
    elif init == "t-aab":
        corruption = truncated_aab_scores(graph)
    else:
        raise ValueError("init must be 't-aab' or 'uniform'")

    weights = np.exp(-20.0 * corruption)
    locations = None
    residuals = np.ones(graph.m)
    alpha = np.ones(graph.m)
    trace = []
    for t in range(1, t_max + 1):
        locations, alpha, residuals = weighted_location_solve(
            graph.n, np.stack([graph.I, graph.J], axis=1), graph.gamma, weights, method=wls, t0=locations
        )
        s_cycle = cycle_scores(graph, locations, residuals, beta=beta, legacy=(softmin == "legacy"))
        lam = schedule(t)
        h = (1.0 - lam) * residuals + lam * s_cycle
        weights = np.clip(np.exp(-4.0 * h) / (h + delta), WEIGHT_MIN, WEIGHT_MAX)
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
    wls: str = "exact",
) -> dict[str, np.ndarray]:
    """Welsch IRLS without cycle-consistency weighting (uniform start)."""

    edges = np.asarray(edges, dtype=np.int64)
    weights = np.ones(len(edges), dtype=float)
    locations = None
    residuals = np.ones(len(edges))
    alpha = np.ones(len(edges))
    trace = []
    for _ in range(t_max):
        locations, alpha, residuals = weighted_location_solve(n, edges, directions, weights, method=wls, t0=locations)
        weights = np.clip(np.exp(-4.0 * residuals) / (residuals + delta), WEIGHT_MIN, WEIGHT_MAX)
        trace.append(float(np.median(residuals)))
    return {
        "locations": locations,
        "alpha": alpha,
        "residuals": residuals,
        "weights": weights,
        "trace": np.asarray(trace),
    }
