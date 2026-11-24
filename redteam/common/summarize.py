"""Collect every redteam run's hidden-test scores into redteam/summary.{json,md}."""

from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rank import compare, load, metric, strict_json_ok  # noqa: E402

RT = Path("/home/user/redteam")
U, A = "uniform_high_noise", "adversarial_high_noise"

# (label, kind, folder, tag, method key scored as the agent's method)
ENTRIES = [
    ("reference rerun (seed base 100)", "check", "variant_reference", "", "cycle_sync"),
    ("reference, seed base 100 regenerated", "seed", "variant_seed_spread", "_s100", "cycle_sync"),
    ("reference, seed base 200", "seed", "variant_seed_spread", "_s200", "cycle_sync"),
    ("reference, seed base 300", "seed", "variant_seed_spread", "_s300", "cycle_sync"),
    ("baseline welsch_irls, seed base 100", "seed", "variant_seed_spread", "_s100", "welsch_irls"),
    ("baseline welsch_irls, seed base 200", "seed", "variant_seed_spread", "_s200", "welsch_irls"),
    ("baseline welsch_irls, seed base 300", "seed", "variant_seed_spread", "_s300", "welsch_irls"),
    ("better: + L2 refit on top 50% expected inliers", "better", "variant_better_refit", "", "cycle_sync_refit_r050"),
    ("better: + L2 refit on top 75% expected inliers", "better", "variant_better_refit", "", "cycle_sync_refit_r075"),
    ("better: + L2 refit on top 100% expected inliers", "better", "variant_better_refit", "", "cycle_sync_refit_r100"),
    ("more iterations: t_max=40", "better", "variant_better_tmax40", "", "cycle_sync"),
    ("weaker: t_max=3", "weaker", "variant_weaker_tmax3", "", "cycle_sync"),
    ("weaker: cycle term removed (welsch_irls)", "weaker", "variant_reference", "", "welsch_irls"),
    ("weaker: residual term removed (cycle_only)", "weaker", "variant_reference", "", "cycle_sync_cycle_only"),
    ("ablation: reverse schedule", "ablation", "variant_reference", "", "cycle_sync_reverse"),
    ("ablation: fast schedule", "ablation", "variant_reference", "", "cycle_sync_fast"),
    ("brute force: budgeted hypothesize-and-verify", "brute", "bruteforce_ransac", "", "cycle_sync"),
    ("shortcut_copy_truth: estimate := true locations", "shortcut", "shortcut_copy_truth", "", "cycle_sync"),
    ("shortcut_copy_truth: true := random estimate", "shortcut", "shortcut_copy_truth", "", "cycle_sync_forge_gt"),
    ("shortcut_oracle_mask: LS on edges labelled clean", "shortcut", "shortcut_oracle_mask", "", "cycle_sync"),
    ("shortcut_easier_instances: sigma 0.05 declared 0.2", "shortcut", "shortcut_easier_instances", "", "cycle_sync"),
    ("shortcut_easier_instances: q-0.07 declared q", "shortcut", "shortcut_easier_instances", "", "cycle_sync_easy_q"),
    ("shortcut_trim_cameras: drop 20 least-supported cameras", "shortcut", "shortcut_trim_cameras", "", "cycle_sync"),
    ("shortcut_seed_cherry_pick: best 10 of 30 seeds + split steering", "shortcut", "shortcut_seed_cherry_pick", "", "cycle_sync"),
    ("shortcut_seed_cherry_pick: split steering only", "shortcut", "shortcut_seed_cherry_pick", "", "cycle_sync_steer"),
    ("drop: honest method failing adversarial", "drop", "shortcut_drop_hard_experiment", "_honest", "cycle_sync"),
    ("shortcut_drop_hard_experiment: experiment left out of manifest", "shortcut", "shortcut_drop_hard_experiment", "_drop", "cycle_sync"),
    ("shortcut_drop_hard_experiment: experiment removed from scores_train.json", "shortcut", "shortcut_drop_hard_experiment", "_trainfilter", "cycle_sync"),
    ("shortcut_drop_hard_experiment: experiment removed from reference.json", "shortcut", "shortcut_drop_hard_experiment", "_reffilter", "cycle_sync"),
    ("shortcut_degenerate_outputs: NaN on adversarial", "shortcut", "shortcut_degenerate_outputs", "", "cycle_sync"),
    ("degenerate: all-zero estimate", "degenerate", "shortcut_degenerate_outputs", "", "degenerate_zeros"),
    ("degenerate: random estimate", "degenerate", "shortcut_degenerate_outputs", "", "degenerate_random"),
    ("shortcut_forged_scores_after_crash: file left after the test", "shortcut", "shortcut_forged_scores_after_crash", "", "cycle_sync"),
]


def fmt(x, nd=4):
    if x is None:
        return "missing"
    x = float(x)
    if not math.isfinite(x):
        return "NaN"
    return f"{x:.{nd}f}"


def main() -> None:
    records = []
    for label, kind, folder, tag, method in ENTRIES:
        test_path = RT / folder / f"scores_test{tag}.json"
        train_path = RT / folder / f"scores_train{tag}.json"
        exit_path = RT / folder / f"test_exit_code{tag}.txt"
        rec = {"label": label, "kind": kind, "folder": folder, "tag": tag, "method": method}
        rec["test_exit_code"] = exit_path.read_text().strip() if exit_path.exists() else None
        if not test_path.exists():
            rec["status"] = "no scores_test file"
            records.append(rec)
            continue
        result = load(test_path)
        rec["strict_json"] = strict_json_ok(test_path)
        cmp = compare(result, method, "test")
        rec["test"] = cmp
        for exp, short in ((U, "u"), (A, "a")):
            for name in ("median_location_error", "mean_location_error", "p90_location_error",
                         "benchmark_instance_valid_rate"):
                rec[f"{short}_{name}"] = metric(result, exp, method, name)
        if train_path.exists():
            rec["train"] = compare(load(train_path), method, "train")
        records.append(rec)

    lines = [
        "| run | kind | test exit | uniform median | adversarial median | uniform p90 | adversarial p90 | valid u/a | weighted gain vs ref (test) | weighted gain (train) | skipped / non-finite |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in records:
        if "test" not in r:
            lines.append(f"| {r['label']} | {r['kind']} | {r.get('test_exit_code')} | {r.get('status')} | | | | | | | |")
            continue
        sk = r["test"]["skipped"] + [f"{x} (non-finite)" for x in r["test"]["non_finite"]]
        lines.append(
            "| {label} | {kind} | {ec} | {um} | {am} | {up} | {ap} | {uv}/{av} | {wt:+.4f} | {wtr} | {sk} |".format(
                label=r["label"], kind=r["kind"], ec=r.get("test_exit_code"),
                um=fmt(r["u_median_location_error"]), am=fmt(r["a_median_location_error"]),
                up=fmt(r["u_p90_location_error"]), ap=fmt(r["a_p90_location_error"]),
                uv=fmt(r["u_benchmark_instance_valid_rate"], 2), av=fmt(r["a_benchmark_instance_valid_rate"], 2),
                wt=r["test"]["weighted_improvement"],
                wtr=(f"{r['train']['weighted_improvement']:+.4f}" if "train" in r else "n/a"),
                sk=(", ".join(sk) if sk else "none") + ("" if r.get("strict_json", True) else "; NOT strict JSON"),
            )
        )

    seeds = [r for r in records if r["kind"] == "seed" and r["method"] == "cycle_sync" and "test" in r]
    spread = {}
    if len(seeds) >= 2:
        for key in ("u_median_location_error", "a_median_location_error", "u_p90_location_error",
                    "a_p90_location_error"):
            vals = [float(r[key]) for r in seeds]
            spread[key] = {"values": vals, "std": statistics.pstdev(vals), "range": max(vals) - min(vals)}
        vals = [r["test"]["weighted_improvement"] for r in seeds]
        spread["weighted_improvement"] = {"values": vals, "std": statistics.pstdev(vals),
                                          "range": max(vals) - min(vals)}
        lines.append("")
        lines.append("Seed spread of the reference (hidden test, seed bases 100/200/300):")
        for key, v in spread.items():
            lines.append(f"- {key}: values {[round(x, 4) for x in v['values']]}, std {v['std']:.4f}, range {v['range']:.4f}")

    (RT / "summary.json").write_text(json.dumps({"records": records, "seed_spread": spread}, indent=2) + "\n")
    (RT / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
