"""Rank-style comparison of an evaluator result against the reference.

Mirrors the gym's rank before its cross-attempt normalisation (which needs the
population of later attempts): for every experiment and every metric declared
in scoring/reference.json, the improvement over the reference is taken in the
metric's better direction, multiplied by |coefficient| and by the experiment
weight, and summed. Missing values are skipped (they contribute nothing), as
the rank does. Non-finite values are listed separately because what happens
to them depends on how the rank parses the file.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path("/home/user")
REFERENCE = ROOT / "scoring" / "reference.json"
REF_SCORES = {
    "test": ROOT / "scoring" / "scores_test.json",
    "train": ROOT / "scoring" / "scores_train.json",
}


def load(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def strict_json_ok(path: str | Path) -> bool:
    def reject(token: str) -> float:
        raise ValueError(token)

    try:
        json.loads(Path(path).read_text(), parse_constant=reject)
    except ValueError:
        return False
    return True


def compare(result: dict, method: str, split: str = "test", ref_method: str = "cycle_sync") -> dict:
    reference = load(REFERENCE)
    ref_scores = load(REF_SCORES[split])
    rows = []
    total = 0.0
    skipped: list[str] = []
    non_finite: list[str] = []
    for exp, spec in reference["experiments"].items():
        weight = float(spec.get("weight", 1.0))
        ref_vals = ref_scores["experiments"][exp]["results"][ref_method]
        got = result.get("experiments", {}).get(exp, {}).get("results", {}).get(method)
        for metric, mspec in spec["metrics"].items():
            coef = abs(float(mspec.get("coefficient", 0.0)))
            ref_v = ref_vals.get(metric)
            value = None if got is None else got.get(metric)
            row = {
                "experiment": exp,
                "metric": metric,
                "reference": ref_v,
                "value": value,
                "contribution": None,
            }
            if value is None:
                skipped.append(f"{exp}/{metric}")
            elif not math.isfinite(float(value)):
                non_finite.append(f"{exp}/{metric}")
            elif ref_v is not None:
                gain = (value - ref_v) if mspec["higher_is_better"] else (ref_v - value)
                row["contribution"] = weight * coef * gain
                total += row["contribution"]
            rows.append(row)
    return {
        "method": method,
        "split": split,
        "weighted_improvement": total,
        "skipped": skipped,
        "non_finite": non_finite,
        "rows": rows,
    }


def metric(result: dict, exp: str, method: str, name: str):
    return result.get("experiments", {}).get(exp, {}).get("results", {}).get(method, {}).get(name)
