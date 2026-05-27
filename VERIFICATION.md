# Verification Report

## Initial Assessment

The workspace entered final verification at `secondary_claims`. The claimed milestone is justified by prior compute-container runs: the implementation reproduces the synthetic high-noise location-estimation experiments and the schedule ablation, with the proposed method family outperforming the residual-only baseline on both supported settings.

## Issues Found

- Minor: `briefing/problem.md`, `briefing/evaluation.md`, `scoring/EXPERIMENTS.md`, and `scoring/TARGETS.md` contained template language or solution-specific phrasing that was too revealing for from-scratch scientist agents.
- Minor: `baseline/run_irls.py` imported a helper from `method/`, making the baseline less cleanly separable from the paper method.
- Minor: Python bytecode caches under `data/` were not ignored.
- Resolved: `eval/evaluate_outputs.py` was expanded to emit all metrics declared in `scoring/reference.json`, and `scoring/scores.json` was regenerated in the compute container.
- Resolved: CPU job `20621f4b-374` was killed during full from-scratch regeneration. CPU continuation job `2af2234f-ef6` completed successfully and regenerated the missing ablation artifacts and score files.
- Cosmetic infrastructure issue: tracked root files `README.md`, `manifest.json`, and `trajectory/turn_*.jsonl` are reported dirty by git, but they are device/read-only session artifacts that cannot be restored from this environment.

## Fixes Applied

- Rewrote the strict method-agnostic docs to describe only the problem, inputs, metrics, artifact interface, and experiment difficulty.
- Made `baseline/run_irls.py` self-contained by moving its weighted location solve and residual-only robust reweighting code into `baseline/`.
- Added Python bytecode patterns to `.gitignore`.
- Syntax-checked the changed Python files with `python -m py_compile`.
- Submitted validation jobs to regenerate the expanded score contract and rerun train/test evaluation plus `python validate.py --compare`.
- Added `SKIP_EVALUATE=1` support to `scripts/baseline.sh` and `scripts/method.sh`, and updated `scripts/reproduce.sh` to score only once after all artifacts are written.
- Updated `scripts/run.sh` to complete the missing ablation artifacts from the interrupted validation run before regenerating `scores.json`, `scores_train.json`, and `scores_test.json`.
- Verified that `python validate.py --compare` passes after job `2af2234f-ef6`; all five method output manifests are present.

## Final Judgment

The workspace is ready to serve as a research gym for the supported synthetic camera-location experiments. Improve-mode agents can build on the implemented Cycle-Sync code and reproduced outputs; from-scratch agents can use the method-agnostic problem, data, and evaluation interface without importing the paper method.

- Milestone: secondary_claims
- Ready for gym use: yes
- Confidence: high
- Key limitation: synthetic camera-location experiments only; real-image SfM pipeline is not reproduced.
