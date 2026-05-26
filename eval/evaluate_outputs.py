"""Evaluate saved camera-location estimates and write scoring/scores.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from metrics import exact_recovery_rate, median_location_error


METHOD_NAMES = {
    "cycle_sync": "cycle_sync",
    "irls": "welsch_irls",
}


def evaluate_manifest(manifest_path: Path) -> dict[str, dict[str, float]]:
    manifest = json.loads(manifest_path.read_text())
    results = {}
    for exp_name, files in manifest.items():
        medians = []
        edges = []
        corruptions = []
        for file_name in files:
            with np.load(file_name, allow_pickle=False) as z:
                medians.append(median_location_error(z["locations_true"], z["locations_est"]))
                edges.append(len(z["edges"]))
                corruptions.append(float(np.mean(z["corrupted"])))
        results[exp_name] = {
            "median_location_error": float(np.mean(medians)),
            "std_median_location_error": float(np.std(medians)),
            "exact_recovery_rate": exact_recovery_rate(medians),
            "mean_num_edges": float(np.mean(edges)),
            "mean_corruption_fraction": float(np.mean(corruptions)),
            "num_trials": float(len(medians)),
        }
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle-sync", default="outputs/cycle_sync/manifest.json")
    parser.add_argument("--irls", default="outputs/irls/manifest.json")
    parser.add_argument("--out", default="scoring/scores.json")
    args = parser.parse_args()

    scores = {"experiments": {}}
    manifests = {
        "cycle_sync": Path(args.cycle_sync),
        "welsch_irls": Path(args.irls),
    }
    for method_name, manifest_path in manifests.items():
        if not manifest_path.exists():
            continue
        method_results = evaluate_manifest(manifest_path)
        for exp_name, metrics in method_results.items():
            scores["experiments"].setdefault(exp_name, {"results": {}})
            scores["experiments"][exp_name]["results"][method_name] = metrics

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scores, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
