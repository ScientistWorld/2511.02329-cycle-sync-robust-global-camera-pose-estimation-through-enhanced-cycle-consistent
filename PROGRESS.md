# Progress

## What Works

Implemented a runnable Cycle-Sync synthetic benchmark:
- `method/cycle_sync.py` implements Algorithm 1's weighted least-squares location updates, cycle inconsistency aggregation, Welsch-style weights, and `lambda_t = t/(t+10)` schedule.
- `baseline/run_irls.py` runs the residual-only Welsch IRLS comparator corresponding to `lambda_t = 0`.
- `eval/evaluate_outputs.py` evaluates saved artifacts without importing `method/`.
- `scripts/reproduce.sh` runs both methods and writes `scoring/scores.json`.

## Results

No reproduced numerical results yet. Static validation passes, but the method has not run in the container because NumPy/SciPy are installed by `environment/setup.sh` during the job.

## Remaining

Run the CPU test job, inspect `scoring/scores.json`, and compare against the Supplement Table 14/15 references with `python validate.py --compare`. If the method runs and shows the expected improvement over residual-only IRLS, update the milestone to at least `core_claim`.

## Issues

The login-node Python environment lacks NumPy/SciPy, so only syntax compilation and static validator checks were run locally. Actual numerical execution is delegated to the compute container.

## Deviations from Paper

- Evaluation alignment uses closed-form L2 similarity alignment rather than the paper's L1 alignment objective. The metric remains median per-camera Euclidean translation error after global translation and scale alignment; this choice keeps evaluation deterministic and lightweight.
- The T-AAB initializer is implemented with the standard triangle coplanarity residual over well-shaped cycles. The paper cites AAB's closed-form geodesic residual; this reproduction preserves the truncated cycle-consistency initialization and subsequent Cycle-Sync computation but may not exactly match the initializer's closed-form constants.
