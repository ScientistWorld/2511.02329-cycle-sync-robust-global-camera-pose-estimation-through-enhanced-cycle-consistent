# Verification Report

## Initial Assessment

The workspace entered final verification at `secondary_claims`. The claimed milestone is justified by prior compute-container runs: the implementation reproduces the synthetic high-noise location-estimation experiments and the schedule ablation, with the proposed method family outperforming the residual-only baseline on both supported settings.

## Issues Found

- Minor: `briefing/problem.md`, `briefing/evaluation.md`, `scoring/EXPERIMENTS.md`, and `scoring/TARGETS.md` contained template language or solution-specific phrasing that was too revealing for from-scratch scientist agents.
- Minor: `baseline/run_irls.py` imported a helper from `method/`, making the baseline less cleanly separable from the paper method.
- Minor: Python bytecode caches under `data/` were not ignored.
- Pending validation: `eval/evaluate_outputs.py` was expanded to emit all metrics declared in `scoring/reference.json`, so `scoring/scores.json` must be regenerated in the compute container.
- Pending validation: CPU job `20621f4b-374` was killed during full from-scratch regeneration, so the next job resumes the missing ablation artifacts and rewrites the score files.
- Cosmetic infrastructure issue: tracked root files `README.md`, `manifest.json`, and `trajectory/turn_*.jsonl` are reported dirty by git, but they are device/read-only session artifacts that cannot be restored from this environment.

## Fixes Applied

- Rewrote the strict method-agnostic docs to describe only the problem, inputs, metrics, artifact interface, and experiment difficulty.
- Made `baseline/run_irls.py` self-contained by moving its weighted location solve and residual-only robust reweighting code into `baseline/`.
- Added Python bytecode patterns to `.gitignore`.
- Syntax-checked the changed Python files with `python -m py_compile`.
- Left `action.yaml` set to submit a CPU test job that runs `scripts/reproduce.sh`, train/test evaluation, and `python validate.py --compare`.
- Added `SKIP_EVALUATE=1` support to `scripts/baseline.sh` and `scripts/method.sh`, and updated `scripts/reproduce.sh` to score only once after all artifacts are written.
- Updated `scripts/run.sh` to complete the missing ablation artifacts from the interrupted validation run before regenerating `scores.json`, `scores_train.json`, and `scores_test.json`.

## Final Judgment

The workspace is structurally ready after the documentation and separation fixes, but the expanded main score contract still needs one compute-container continuation job before final `done`.

- Milestone: secondary_claims
- Ready for gym use: partial pending CPU validation
- Confidence: medium
- Key limitation: synthetic camera-location experiments only; real-image SfM pipeline is not reproduced.
