"""Evaluate saved camera-location estimates and write scoring/scores.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from metrics import exact_recovery_rate, median_location_error


def declared_metrics(reference_path: Path) -> dict[str, set[str]]:
    if not reference_path.exists():
        return {}
    reference = json.loads(reference_path.read_text())
    return {
        exp_name: set(exp.get("metrics", {}))
        for exp_name, exp in reference.get("experiments", {}).items()
    }


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
        edges = []
        corruptions = []
        for file_name in files:
            with np.load(file_name, allow_pickle=False) as z:
                medians.append(median_location_error(z["locations_true"], z["locations_est"]))
                edges.append(len(z["edges"]))
                corruptions.append(float(np.mean(z["corrupted"])))
        all_scores = {
            "median_location_error": float(np.mean(medians)),
            "mean_corruption_fraction": float(np.mean(corruptions)),
            "exact_recovery_rate": exact_recovery_rate(medians),
        }
        allowed = metric_filter.get(exp_name) if metric_filter else None
        scores[exp_name] = {
            key: value for key, value in all_scores.items() if allowed is None or key in allowed
        }
        diagnostics[exp_name] = {
            "trial_median_location_errors": [float(x) for x in medians],
            "std_median_location_error": float(np.std(medians)),
            "exact_recovery_rate": exact_recovery_rate(medians),
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
    manifests = {
        "cycle_sync": Path(args.cycle_sync),
        "welsch_irls": Path(args.irls),
        "cycle_sync_reverse": Path("outputs/cycle_sync_reverse/manifest.json"),
        "cycle_sync_cycle_only": Path("outputs/cycle_sync_cycle_only/manifest.json"),
        "cycle_sync_fast": Path("outputs/cycle_sync_fast/manifest.json"),
    }
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
