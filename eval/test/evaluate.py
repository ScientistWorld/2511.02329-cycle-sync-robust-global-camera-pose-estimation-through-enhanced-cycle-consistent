"""Evaluate the held-out test slice of saved camera-location estimates."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


SLICE_NAME = "test"
DEFAULT_OUTPUT = "scoring/scores_test.json"
DEFAULT_DIAGNOSTICS = "scoring/diagnostics_test.json"
DEFAULT_TRAIN_SCORES = "scoring/scores_train.json"
DEFAULT_ALIAS = {"irls": "welsch_irls"}
EXPECTED_CONFIGS = {
    "uniform_high_noise": {"n": 100, "p": 0.5, "q": 0.7, "sigma": 0.2, "corruption": "uniform"},
    "adversarial_high_noise": {"n": 100, "p": 0.5, "q": 0.45, "sigma": 0.2, "corruption": "adversarial"},
}


def geometric_median(points: np.ndarray, max_iters: int = 100, tol: float = 1e-8) -> np.ndarray:
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
    ref = np.asarray(reference, dtype=float)
    est = np.asarray(estimate, dtype=float)
    x = est - est.mean(axis=0)
    y = ref - ref.mean(axis=0)
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


def scalar_string(value: object) -> str:
    if isinstance(value, np.ndarray):
        return str(value.item())
    return str(value)


def scalar_float(value: object) -> float:
    if isinstance(value, np.ndarray):
        return float(value.item())
    return float(value)


def benchmark_instance_valid(exp_name: str, artifact: object) -> float:
    expected = EXPECTED_CONFIGS.get(exp_name)
    if expected is None:
        return 1.0
    empirical_q = float(np.mean(artifact["corrupted"]))
    return float(
        int(scalar_float(artifact["n"])) == expected["n"]
        and abs(scalar_float(artifact["p"]) - expected["p"]) <= 1e-12
        and abs(scalar_float(artifact["q"]) - expected["q"]) <= 1e-12
        and abs(scalar_float(artifact["sigma"]) - expected["sigma"]) <= 1e-12
        and scalar_string(artifact["corruption"]) == expected["corruption"]
        and abs(empirical_q - expected["q"]) <= 0.10
    )


def exact_recovery_rate(errors: list[float], threshold: float = 1e-4) -> float:
    if not errors:
        return 0.0
    return float(np.mean(np.asarray(errors) < threshold))


def declared_metrics(reference_path: Path) -> dict[str, set[str]]:
    if not reference_path.exists():
        return {}
    reference = json.loads(reference_path.read_text())
    return {
        exp_name: set(exp.get("metrics", {}))
        for exp_name, exp in reference.get("experiments", {}).items()
    }


def required_methods_by_experiment(train_scores_path: Path) -> dict[str, set[str]]:
    if not train_scores_path.exists():
        return {}
    train_scores = json.loads(train_scores_path.read_text())
    return {
        exp_name: set(experiment.get("results", {}))
        for exp_name, experiment in train_scores.get("experiments", {}).items()
    }


def split_files(exp_name: str, files: list[str]) -> list[str]:
    keyed = []
    for file_name in files:
        key = f"{exp_name}:{Path(file_name).name}"
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        keyed.append((digest, file_name))
    ordered = [file_name for _, file_name in sorted(keyed)]
    cutoff = (len(ordered) + 1) // 2
    return ordered[cutoff:]


def discover_manifests(args: argparse.Namespace) -> dict[str, Path]:
    manifests: dict[str, Path] = {}
    for manifest_path in sorted(Path("outputs").glob("*/manifest.json")):
        method_dir = manifest_path.parent.name
        method_name = DEFAULT_ALIAS.get(method_dir, method_dir)
        manifests[method_name] = manifest_path

    explicit_defaults = {
        "cycle_sync": args.cycle_sync,
        "welsch_irls": args.irls,
    }
    for method_name, manifest_name in explicit_defaults.items():
        if manifest_name:
            manifests[method_name] = Path(manifest_name)

    for item in args.manifest:
        if "=" not in item:
            raise SystemExit("--manifest entries must have the form METHOD=path/to/manifest.json")
        method_name, manifest_name = item.split("=", 1)
        manifests[method_name] = Path(manifest_name)

    required_by_exp = required_methods_by_experiment(Path(args.train_scores))
    train_methods = set().union(*required_by_exp.values()) if required_by_exp else set()
    if not train_methods:
        return manifests
    missing = sorted(method for method in train_methods if method not in manifests)
    if missing:
        raise SystemExit(
            "scores_train.json contains methods without matching manifests: "
            + ", ".join(missing)
        )
    return {method_name: manifests[method_name] for method_name in sorted(train_methods)}


def evaluate_manifest(
    manifest_path: Path,
    metric_filter: dict[str, set[str]] | None = None,
) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, object]]]:
    manifest = json.loads(manifest_path.read_text())
    scores: dict[str, dict[str, float]] = {}
    diagnostics: dict[str, dict[str, object]] = {}
    for exp_name, files in manifest.items():
        if metric_filter and exp_name not in metric_filter:
            continue
        selected_files = split_files(exp_name, list(files))
        if not selected_files:
            continue
        medians = []
        means = []
        p90s = []
        edges = []
        corruptions = []
        valid_instances = []
        for file_name in selected_files:
            with np.load(file_name, allow_pickle=False) as z:
                errors = location_errors(z["locations_true"], z["locations_est"])
                medians.append(float(np.median(errors)))
                means.append(float(np.mean(errors)))
                p90s.append(float(np.percentile(errors, 90)))
                edges.append(len(z["edges"]))
                corruptions.append(float(np.mean(z["corrupted"])))
                valid_instances.append(benchmark_instance_valid(exp_name, z))

        all_scores = {
            "median_location_error": float(np.mean(medians)),
            "mean_location_error": float(np.mean(means)),
            "p90_location_error": float(np.mean(p90s)),
            "mean_corruption_fraction": float(np.mean(corruptions)),
            "benchmark_instance_valid_rate": float(np.mean(valid_instances)),
            "exact_recovery_rate": exact_recovery_rate(medians),
        }
        allowed = metric_filter.get(exp_name) if metric_filter else None
        scores[exp_name] = {
            key: value for key, value in all_scores.items() if allowed is None or key in allowed
        }
        diagnostics[exp_name] = {
            "slice": SLICE_NAME,
            "selected_files": selected_files,
            "trial_median_location_errors": [float(x) for x in medians],
            "trial_mean_location_errors": [float(x) for x in means],
            "trial_p90_location_errors": [float(x) for x in p90s],
            "std_median_location_error": float(np.std(medians)),
            "exact_recovery_rate": exact_recovery_rate(medians),
            "benchmark_instance_valid_rate": float(np.mean(valid_instances)),
            "mean_num_edges": float(np.mean(edges)),
            "num_trials": float(len(medians)),
        }
    return scores, diagnostics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle-sync", default=None)
    parser.add_argument("--irls", default=None)
    parser.add_argument(
        "--manifest",
        action="append",
        default=[],
        help="Additional METHOD=manifest.json artifact manifest to evaluate.",
    )
    parser.add_argument("--out", default=DEFAULT_OUTPUT)
    parser.add_argument("--diagnostics-out", default=DEFAULT_DIAGNOSTICS)
    parser.add_argument("--reference", default="scoring/reference.json")
    parser.add_argument("--train-scores", default=DEFAULT_TRAIN_SCORES)
    args = parser.parse_args()

    metric_filter = declared_metrics(Path(args.reference))
    required_by_exp = required_methods_by_experiment(Path(args.train_scores))
    scores = {"experiments": {}}
    diagnostics = {"experiments": {}}
    for method_name, manifest_path in discover_manifests(args).items():
        if not manifest_path.exists():
            continue
        method_results, method_diagnostics = evaluate_manifest(manifest_path, metric_filter)
        for exp_name, metrics in method_results.items():
            if required_by_exp and method_name not in required_by_exp.get(exp_name, set()):
                continue
            scores["experiments"].setdefault(exp_name, {"results": {}})
            scores["experiments"][exp_name]["results"][method_name] = metrics
        for exp_name, metrics in method_diagnostics.items():
            if required_by_exp and method_name not in required_by_exp.get(exp_name, set()):
                continue
            diagnostics["experiments"].setdefault(exp_name, {"results": {}})
            diagnostics["experiments"][exp_name]["results"][method_name] = metrics

    if required_by_exp:
        missing_by_exp = {}
        for exp_name, expected_methods in required_by_exp.items():
            actual_methods = set(scores["experiments"].get(exp_name, {}).get("results", {}))
            missing = sorted(expected_methods - actual_methods)
            if missing:
                missing_by_exp[exp_name] = missing
        if missing_by_exp:
            details = "; ".join(
                f"{exp_name}: {', '.join(methods)}"
                for exp_name, methods in sorted(missing_by_exp.items())
            )
            raise SystemExit(f"test slice did not score all train methods: {details}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scores, indent=2, sort_keys=True) + "\n")
    diagnostics_out = Path(args.diagnostics_out)
    diagnostics_out.parent.mkdir(parents=True, exist_ok=True)
    diagnostics_out.write_text(json.dumps(diagnostics, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
