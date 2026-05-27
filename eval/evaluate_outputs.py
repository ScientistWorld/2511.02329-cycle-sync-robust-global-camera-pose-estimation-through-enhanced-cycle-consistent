"""Evaluate saved camera-location estimates and write scoring/scores.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from metrics import exact_recovery_rate, location_errors


DEFAULT_ALIAS = {"irls": "welsch_irls"}
EXPECTED_CONFIGS = {
    "uniform_high_noise": {"n": 100, "p": 0.5, "q": 0.7, "sigma": 0.2, "corruption": "uniform"},
    "adversarial_high_noise": {"n": 100, "p": 0.5, "q": 0.45, "sigma": 0.2, "corruption": "adversarial"},
}


def declared_metrics(reference_path: Path) -> dict[str, set[str]]:
    if not reference_path.exists():
        return {}
    reference = json.loads(reference_path.read_text())
    return {
        exp_name: set(exp.get("metrics", {}))
        for exp_name, exp in reference.get("experiments", {}).items()
    }


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


def evaluate_manifest(
    manifest_path: Path,
    metric_filter: dict[str, set[str]] | None = None,
) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    manifest = json.loads(manifest_path.read_text())
    scores = {}
    diagnostics = {}
    for exp_name, files in manifest.items():
        if metric_filter and exp_name not in metric_filter:
            continue
        medians = []
        means = []
        p90s = []
        edges = []
        corruptions = []
        valid_instances = []
        for file_name in files:
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
    parser.add_argument("--cycle-sync", default="outputs/cycle_sync/manifest.json")
    parser.add_argument("--irls", default="outputs/irls/manifest.json")
    parser.add_argument(
        "--manifest",
        action="append",
        default=[],
        help="Additional METHOD=manifest.json artifact manifest to evaluate.",
    )
    parser.add_argument("--out", default="scoring/scores.json")
    parser.add_argument("--diagnostics-out", default="scoring/diagnostics.json")
    parser.add_argument("--reference", default="scoring/reference.json")
    args = parser.parse_args()

    scores = {"experiments": {}}
    diagnostics = {"experiments": {}}
    metric_filter = declared_metrics(Path(args.reference))
    manifests = {}
    for manifest_path in sorted(Path("outputs").glob("*/manifest.json")):
        method_dir = manifest_path.parent.name
        method_name = DEFAULT_ALIAS.get(method_dir, method_dir)
        manifests[method_name] = manifest_path
    manifests.update({
        "cycle_sync": Path(args.cycle_sync),
        "welsch_irls": Path(args.irls),
    })
    for item in args.manifest:
        if "=" not in item:
            raise SystemExit("--manifest entries must have the form METHOD=path/to/manifest.json")
        method_name, manifest_name = item.split("=", 1)
        manifests[method_name] = Path(manifest_name)
    for method_name, manifest_path in manifests.items():
        if not manifest_path.exists():
            continue
        method_results, method_diagnostics = evaluate_manifest(manifest_path, metric_filter)
        for exp_name, metrics in method_results.items():
            scores["experiments"].setdefault(exp_name, {"results": {}})
            scores["experiments"][exp_name]["results"][method_name] = metrics
        for exp_name, metrics in method_diagnostics.items():
            diagnostics["experiments"].setdefault(exp_name, {"results": {}})
            diagnostics["experiments"][exp_name]["results"][method_name] = metrics

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scores, indent=2, sort_keys=True) + "\n")
    diagnostics_out = Path(args.diagnostics_out)
    diagnostics_out.parent.mkdir(parents=True, exist_ok=True)
    diagnostics_out.write_text(json.dumps(diagnostics, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
