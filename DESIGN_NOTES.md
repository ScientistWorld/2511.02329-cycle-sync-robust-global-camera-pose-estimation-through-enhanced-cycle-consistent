Train/Test Evaluation Design Handoff

Checked:
- Read `scripts/evaluate_train.sh` and `scripts/evaluate_test.sh` side by side. Train invokes `eval/train/evaluate.py`; test invokes `eval/test/evaluate.py` and writes `scoring/scores_test.json`.
- Checked for hardcoded method defaults in the split scripts. The evaluators enumerate manifests under `outputs/*/manifest.json` and accept explicit `--manifest METHOD=path` entries.
- Checked for train/test leakage with grep. No cross-imports between `eval/train/` and `eval/test/` were found.
- Checked for paper-agreement metric names in the split eval and reference schema. No scored metric is shaped as agreement with a published value.
- Confirmed `scoring/scores_train.json` and `scoring/scores_test.json` do not exist.
- Ran `bash -n` on both split scripts.

Changed:
- Added `mean_location_error` and `p90_location_error` to both split evaluators. The previous visible score focused on median recovery, which a method could game by improving typical cameras while leaving hard cameras bad.
- Added `benchmark_instance_valid_rate` to both split evaluators. This catches shortcuts that alter the artifact's problem size, graph density, noise level, or corruption regime instead of improving recovery under the intended benchmark conditions.
- Updated `scoring/reference.json` so the new tail-error and validity metrics are scored. The old `mean_corruption_fraction` remains as a zero-weight diagnostic for compatibility with earlier score files, but it no longer rewards artificially high corruption fractions.
- Added missing metric descriptions in `scoring/reference.json`.

Runtime concerns for the runner iteration:
- The split evaluators trust the artifact to contain `locations_true`, `locations_est`, and benchmark metadata. The validity metric checks metadata, but it cannot cryptographically prove that a malicious method did not forge ground truth inside its own `.npz` outputs. A stronger future design would store held-out problem files independently of method output and score estimates against those neutral files.
- The train/test split is a deterministic hash split over artifact filenames. This is adequate for ten current trials per experiment, but if a future run emits very few trials the slices may become noisy.
- `benchmark_instance_valid_rate` assumes the synthetic benchmark scale used by the current reproduction: `n=80`, `p=0.5`, `sigma=0.2`, and the experiment-specific corruption settings. If the runner intentionally changes benchmark scale, this metric must be updated alongside that change.
- I did not run the Python evaluators or produce score numbers because this iteration is file-edit-only.
