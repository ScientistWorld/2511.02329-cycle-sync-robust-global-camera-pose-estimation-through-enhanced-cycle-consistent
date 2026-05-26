"""Method-agnostic metrics for camera-location synchronization."""

from __future__ import annotations

import numpy as np


def l2_similarity_align(reference: np.ndarray, estimate: np.ndarray) -> np.ndarray:
    """Align estimate to reference by translation and scalar scale.

    The paper defines an L1 similarity alignment. This evaluator uses the
    closed-form least-squares analogue for reproducibility and speed; the
    reported metric remains the paper's per-camera median Euclidean error.
    """

    ref = np.asarray(reference, dtype=float)
    est = np.asarray(estimate, dtype=float)
    ref_center = ref.mean(axis=0, keepdims=True)
    est_center = est.mean(axis=0, keepdims=True)
    x = est - est_center
    y = ref - ref_center
    denom = float(np.sum(x * x))
    scale = 1.0 if denom <= 1e-12 else float(np.sum(x * y) / denom)
    return scale * x + ref_center


def location_errors(reference: np.ndarray, estimate: np.ndarray) -> np.ndarray:
    aligned = l2_similarity_align(reference, estimate)
    return np.linalg.norm(np.asarray(reference) - aligned, axis=1)


def median_location_error(reference: np.ndarray, estimate: np.ndarray) -> float:
    return float(np.median(location_errors(reference, estimate)))


def exact_recovery_rate(errors: list[float], threshold: float = 1e-4) -> float:
    if not errors:
        return 0.0
    return float(np.mean(np.asarray(errors) < threshold))
