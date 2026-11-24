"""Public (train) evaluator for camera-location recovery.

Runs every registered solver (``scripts/solvers/<method>.sh``) on the public
train instances in ``data/instances/train/`` and writes
``scoring/scores_train.json`` (or ``--out``). The hidden test uses the same
solver interface, metrics and fail-closed rules on its own instances.

Solver interface
    bash scripts/solvers/<method>.sh <input_dir> <output_dir>
``input_dir`` holds one ``inst_XXX.npz`` per instance with ``n``, ``edges``
(m x 2, i < j), ``directions`` (m x 3 unit vectors approximating
(t_i - t_j)/||t_i - t_j||) and ``experiment`` (the setting's name). The
solver must write ``<output_dir>/inst_XXX.npz`` containing ``locations``
(n x 3, finite).

Metrics (lower is better), per instance after L1 similarity alignment of the
estimate to the ground truth, then averaged over instances:
``median_location_error``, ``mean_location_error``, ``p90_location_error``.

Fail closed: a non-zero solver exit or a missing / malformed / non-finite
output scores the instance at the error of the uninformative all-cameras-at-
one-point output, and valid outputs are capped at that value. The method
``cycle_sync`` is always reported (at worst values if no solver exists).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
INSTANCE_DIR = ROOT / "data" / "instances" / "train"
DEFAULT_SOLVERS = ROOT / "scripts" / "solvers"
DEFAULT_OUT = ROOT / "scoring" / "scores_train.json"
DEFAULT_DIAG = ROOT / "scoring" / "diagnostics_train.json"

EXPERIMENTS = ("uniform_high_noise", "adversarial_high_noise")
METRICS = ("median_location_error", "mean_location_error", "p90_location_error")
REQUIRED_METHODS = ("cycle_sync",)
METHOD_NAME = re.compile(r"^[A-Za-z0-9_.\-]+$")


def geometric_median(points: np.ndarray, max_iters: int = 100, tol: float = 1e-8) -> np.ndarray:
    y = np.median(points, axis=0)
    for _ in range(max_iters):
        dist = np.linalg.norm(points - y, axis=1)
        if np.any(dist < tol):
            return points[int(np.argmin(dist))].copy()
        weights = 1.0 / np.maximum(dist, tol)
        y_next = np.sum(weights[:, None] * points, axis=0) / np.sum(weights)
        if np.linalg.norm(y_next - y) < tol:
            return y_next
        y = y_next
    return y


def l1_similarity_align(reference: np.ndarray, estimate: np.ndarray) -> np.ndarray:
    """argmin over scalar c and translation t of sum_i ||t*_i - (c est_i + t)||."""

    ref = np.asarray(reference, dtype=float)
    est = np.asarray(estimate, dtype=float)
    x = est - est.mean(axis=0)
    y = ref - ref.mean(axis=0)
    denom = float(np.sum(x * x))
    scale = 1.0 if denom <= 1e-12 else float(np.sum(x * y) / denom)
    translation = geometric_median(ref - scale * est)
    for _ in range(100):
        dist = np.linalg.norm(ref - (scale * est + translation), axis=1)
        weights = 1.0 / np.maximum(dist, 1e-8)
        denom = float(np.sum(weights * np.sum(est * est, axis=1)))
        if denom <= 1e-12:
            break
        next_scale = float(np.sum(weights * np.sum(est * (ref - translation), axis=1)) / denom)
        next_translation = geometric_median(ref - next_scale * est)
        converged = abs(next_scale - scale) < 1e-8 and np.linalg.norm(next_translation - translation) < 1e-8
        scale, translation = next_scale, next_translation
        if converged:
            break
    return scale * est + translation


def normalise_estimate(est: np.ndarray) -> np.ndarray:
    peak = float(np.max(np.abs(est))) if est.size else 0.0
    if peak > 0.0 and np.isfinite(peak):
        est = est / peak
    return est - est.mean(axis=0)


def instance_metrics(truth: np.ndarray, est: np.ndarray) -> np.ndarray:
    errors = np.linalg.norm(truth - l1_similarity_align(truth, est), axis=1)
    return np.array([np.median(errors), np.mean(errors), np.percentile(errors, 90)], dtype=float)


def load_instances(instance_dir: Path) -> dict[str, list[dict]]:
    data: dict[str, list[dict]] = {}
    for exp in EXPERIMENTS:
        path = instance_dir / f"{exp}.npz"
        if not path.is_file():
            raise SystemExit(f"train instances missing: {path} (run python data/make_instances.py)")
        insts = []
        with np.load(path, allow_pickle=False) as z:
            for k in range(int(z["count"])):
                truth = np.asarray(z[f"locations_{k:03d}"], dtype=float)
                insts.append(
                    {
                        "n": int(z[f"n_{k:03d}"]),
                        "edges": np.asarray(z[f"edges_{k:03d}"], dtype=np.int64),
                        "directions": np.asarray(z[f"directions_{k:03d}"], dtype=float),
                        "truth": truth,
                        "worst": instance_metrics(truth, np.zeros_like(truth)),
                    }
                )
        data[exp] = insts
    return data


def discover_methods(solvers_dir: Path, only: list[str] | None) -> dict[str, Path | None]:
    found = {p.stem: p for p in sorted(solvers_dir.glob("*.sh")) if METHOD_NAME.match(p.stem)}
    if only:
        found = {k: v for k, v in found.items() if k in only}
    methods: dict[str, Path | None] = dict(found)
    for name in REQUIRED_METHODS:
        methods.setdefault(name, None)
    return dict(sorted(methods.items()))


def read_estimate(path: Path, n: int) -> np.ndarray | None:
    try:
        with np.load(path, allow_pickle=False) as z:
            arr = np.asarray(z["locations"])
    except Exception:
        return None
    if arr.dtype.kind not in "fiu" or arr.shape != (n, 3):
        return None
    arr = arr.astype(float)
    if not np.all(np.isfinite(arr)):
        return None
    return arr


def run_solver(script: Path, exp: str, insts: list[dict]) -> tuple[list[np.ndarray | None], int, float]:
    work = Path(tempfile.mkdtemp(prefix="cs_train_"))
    try:
        in_dir = work / "in"
        out_dir = work / "out"
        in_dir.mkdir()
        out_dir.mkdir()
        for k, inst in enumerate(insts):
            np.savez(
                in_dir / f"inst_{k:03d}.npz",
                n=np.int64(inst["n"]),
                edges=inst["edges"],
                directions=inst["directions"],
                experiment=np.str_(exp),
            )
        start = time.time()
        proc = subprocess.run(["bash", str(script), str(in_dir), str(out_dir)], cwd=str(ROOT), stdout=sys.stderr)
        elapsed = time.time() - start
        estimates = [
            read_estimate(out_dir / f"inst_{k:03d}.npz", inst["n"]) if proc.returncode == 0 else None
            for k, inst in enumerate(insts)
        ]
        return estimates, proc.returncode, elapsed
    finally:
        shutil.rmtree(work, ignore_errors=True)


def score_instances(insts: list[dict], estimates: list[np.ndarray | None]) -> tuple[np.ndarray, np.ndarray]:
    values = np.empty((len(insts), len(METRICS)))
    failed = np.zeros(len(insts), dtype=bool)
    for k, (inst, est) in enumerate(zip(insts, estimates)):
        vals = None
        if est is not None:
            try:
                with np.errstate(all="ignore"):
                    vals = instance_metrics(inst["truth"], normalise_estimate(est))
            except Exception:
                vals = None
            if vals is not None and not np.all(np.isfinite(vals)):
                vals = None
        if vals is None:
            failed[k] = True
            vals = inst["worst"]
        values[k] = np.minimum(vals, inst["worst"])
    return values, failed


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def scores_payload(table: dict[str, dict[str, np.ndarray]]) -> dict:
    out: dict = {"experiments": {}}
    for exp in EXPERIMENTS:
        results = {}
        for method, per_exp in table.items():
            vals = per_exp[exp].mean(axis=0)
            results[method] = {metric: float(v) for metric, v in zip(METRICS, vals)}
        out["experiments"][exp] = {"results": results}
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solvers-dir", default=str(DEFAULT_SOLVERS))
    parser.add_argument("--instances-dir", default=str(INSTANCE_DIR))
    parser.add_argument("--methods", nargs="*", default=None, help="restrict to these registered solvers")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--diagnostics-out", default=str(DEFAULT_DIAG))
    parser.add_argument("--per-instance-out", default=None)
    args = parser.parse_args()

    out = Path(args.out)
    diag_out = Path(args.diagnostics_out)
    for path in (out, diag_out):
        path.unlink(missing_ok=True)

    methods = discover_methods(Path(args.solvers_dir), args.methods)
    data = load_instances(Path(args.instances_dir))
    worst = {exp: np.stack([inst["worst"] for inst in data[exp]]) for exp in EXPERIMENTS}
    table = {m: {exp: worst[exp].copy() for exp in EXPERIMENTS} for m in methods}
    failed_table = {m: {exp: np.ones(len(data[exp]), dtype=bool) for exp in EXPERIMENTS} for m in methods}
    diagnostics: dict = {"experiments": {exp: {"results": {}} for exp in EXPERIMENTS}}
    write_json(out, scores_payload(table))

    for method, script in methods.items():
        for exp in EXPERIMENTS:
            info = {"num_instances": len(data[exp])}
            if script is None:
                info.update({"returncode": None, "num_failed": len(data[exp]), "note": "no solver registered"})
            else:
                print(f"[train] {method} / {exp}", file=sys.stderr, flush=True)
                estimates, rc, elapsed = run_solver(script, exp, data[exp])
                values, failed = score_instances(data[exp], estimates)
                table[method][exp] = values
                failed_table[method][exp] = failed
                info.update({"returncode": rc, "num_failed": int(failed.sum()), "solver_seconds": round(elapsed, 1)})
            diagnostics["experiments"][exp]["results"][method] = info
            write_json(out, scores_payload(table))

    write_json(diag_out, diagnostics)
    if args.per_instance_out:
        per_instance = {
            method: {
                exp: {
                    **{metric: table[method][exp][:, j].tolist() for j, metric in enumerate(METRICS)},
                    "failed": failed_table[method][exp].tolist(),
                }
                for exp in EXPERIMENTS
            }
            for method in methods
        }
        write_json(Path(args.per_instance_out), per_instance)
    print(json.dumps(scores_payload(table), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
