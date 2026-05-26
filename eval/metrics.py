"""Method-agnostic metrics for camera-location synchronization."""

from __future__ import annotations

import numpy as np


def geometric_median(points: np.ndarray, max_iters: int = 100, tol: float = 1e-8) -> np.ndarray:
    """Compute the Euclidean geometric median with Weiszfeld iterations."""

    y = np.median(np.asarray(points, dtype=float), axis=0)
    for _ in range(max_iters):
        diff = points - y
        dist = np.linalg.norm(diff, axis=1)
        if np.any(dist < tol):
            return points[int(np.argmin(dist))].copy()
        weights = 1.0 / np.maximum(dist, tol)
        y_next = np.sum(weights[:, None] * points, axis=0) / np.sum(weights)
        if np.linalg.norm(y_next - y) < tol:
            return y_next
        y = y_next
    return y


def l1_similarity_align(reference: np.ndarray, estimate: np.ndarray) -> np.ndarray:
    """Align estimate to reference by the paper's L1 translation-scale objective.

    The paper removes gauge freedom by minimizing
    ``sum_i ||t_i^* - (c * t_hat_i + t)||_2`` over scalar ``c`` and translation
    ``t``. This IRLS solver alternates the geometric median translation update
    with the weighted least-squares scale update for that nonsmooth objective.
    """

    ref = np.asarray(reference, dtype=float)
    est = np.asarray(estimate, dtype=float)
    ref_center = ref.mean(axis=0)
    est_center = est.mean(axis=0)
    x = est - est_center
    y = ref - ref_center
    denom = float(np.sum(x * x))
    scale = 1.0 if denom <= 1e-12 else float(np.sum(x * y) / denom)
    translation = geometric_median(ref - scale * est)

    for _ in range(100):
        residual = ref - (scale * est + translation)
        dist = np.linalg.norm(residual, axis=1)
        weights = 1.0 / np.maximum(dist, 1e-8)
        denom = float(np.sum(weights * np.sum(est * est, axis=1)))
        if denom <= 1e-12:
            break
        next_scale = float(np.sum(weights * np.sum(est * (ref - translation), axis=1)) / denom)
        next_translation = geometric_median(ref - next_scale * est)
        if abs(next_scale - scale) < 1e-8 and np.linalg.norm(next_translation - translation) < 1e-8:
            scale = next_scale
            translation = next_translation
            break
        scale = next_scale
        translation = next_translation
    return scale * est + translation


def location_errors(reference: np.ndarray, estimate: np.ndarray) -> np.ndarray:
    aligned = l1_similarity_align(reference, estimate)
    return np.linalg.norm(np.asarray(reference) - aligned, axis=1)


def median_location_error(reference: np.ndarray, estimate: np.ndarray) -> float:
    return float(np.median(location_errors(reference, estimate)))


def exact_recovery_rate(errors: list[float], threshold: float = 1e-4) -> float:
    if not errors:
        return 0.0
    return float(np.mean(np.asarray(errors) < threshold))
