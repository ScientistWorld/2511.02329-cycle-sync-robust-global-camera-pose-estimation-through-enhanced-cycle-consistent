"""Residual-only Welsch IRLS baseline (lambda_t = 0 reweighting, uniform start).

Self-contained: it does not import method/, so edits to the proposed method
never change the baseline. Solver interface:

    python baseline/solve_irls.py --input-dir IN --output-dir OUT

Reads ``IN/*.npz`` (``n``, ``edges``, ``directions``) and writes
``OUT/<same name>`` with ``locations`` (n x 3).

Each iteration solves the weighted least-squares problem
    min sum_e w_e ||t_i - t_j - alpha_e gamma_e||^2,  alpha_e >= 1,  sum_i t_i = 0
exactly, then reweights every edge by its own residual with the Welsch-type
rule w = exp(-4 r) / (r + delta).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from scipy import linalg as sla

WEIGHT_MIN = 1e-8
WEIGHT_MAX = 1e8


def _scatter_edges(I, J, vec, n):
    out = np.empty((n, vec.shape[1]))
    for c in range(vec.shape[1]):
        out[:, c] = np.bincount(I, weights=vec[:, c], minlength=n) - np.bincount(J, weights=vec[:, c], minlength=n)
    return out


def _solve_spd(mat, rhs):
    try:
        factor = sla.cho_factor(mat, lower=True, check_finite=False)
        sol = sla.cho_solve(factor, rhs, check_finite=False)
        if np.all(np.isfinite(sol)):
            return sol
    except (np.linalg.LinAlgError, ValueError):
        pass
    return np.linalg.lstsq(mat, rhs, rcond=None)[0]


def _objective(t, I, J, gamma, w):
    d = t[I] - t[J]
    p = np.sum(d * gamma, axis=1)
    alpha = np.maximum(1.0, p)
    res = d - alpha[:, None] * gamma
    return float(np.sum(w * np.sum(res * res, axis=1))), p, alpha, res


def wls_exact(n, I, J, gamma, w, t0=None, max_iter=100):
    """Generalised Newton on the alpha-eliminated, piecewise-quadratic objective."""

    deg = np.bincount(I, weights=w, minlength=n) + np.bincount(J, weights=w, minlength=n)
    ground = int(np.argmax(deg))
    keep = np.ones(3 * n, dtype=bool)
    keep[3 * ground : 3 * ground + 3] = False
    gg = gamma[:, :, None] * gamma[:, None, :]
    eye = np.eye(3)
    ar = np.arange(n)
    t = np.zeros((n, 3)) if t0 is None else np.array(t0, dtype=float, copy=True)
    t -= t.mean(axis=0)
    f_val, p, alpha, res = _objective(t, I, J, gamma, w)
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
            f_new, p_new, alpha_new, res_new = _objective(t_new, I, J, gamma, w)
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
        f_val, p, alpha, res = f_new, p_new, alpha_new, res_new
        if (s == 1.0 and same_active) or small_step or rel_decrease < 1e-15:
            break
    return t, alpha, np.linalg.norm(res, axis=1)


def welsch_irls(n, edges, directions, t_max=20, delta=1e-8):
    edges = np.asarray(edges, dtype=np.int64)
    gamma = np.asarray(directions, dtype=float)
    I, J = edges[:, 0], edges[:, 1]
    w = np.ones(len(edges))
    t = None
    for _ in range(t_max):
        t, _alpha, r = wls_exact(int(n), I, J, gamma, w, t0=t)
        w = np.clip(np.exp(-4.0 * r) / (r + delta), WEIGHT_MIN, WEIGHT_MAX)
    return t


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--t-max", type=int, default=20)
    args = parser.parse_args()
    in_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(in_dir.glob("*.npz")):
        with np.load(path, allow_pickle=False) as z:
            n = int(z["n"])
            edges = np.asarray(z["edges"], dtype=np.int64)
            directions = np.asarray(z["directions"], dtype=float)
        locations = welsch_irls(n, edges, directions, t_max=args.t_max)
        np.savez(out_dir / path.name, locations=np.asarray(locations, dtype=float))


if __name__ == "__main__":
    main()
