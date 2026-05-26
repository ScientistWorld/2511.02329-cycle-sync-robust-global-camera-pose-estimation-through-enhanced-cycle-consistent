# Progress

## What Works

Implemented a runnable Cycle-Sync synthetic benchmark:
- `method/cycle_sync.py` implements Algorithm 1's weighted least-squares location updates, cycle inconsistency aggregation, Welsch-style weights, and `lambda_t = t/(t+10)` schedule.
- `baseline/run_irls.py` runs the residual-only Welsch IRLS comparator corresponding to `lambda_t = 0`.
- `eval/evaluate_outputs.py` evaluates saved artifacts without importing `method/`.
- `scripts/reproduce.sh` runs both methods and writes `scoring/scores.json`.
- First CPU job completed both synthetic experiments and wrote artifacts for Cycle-Sync and the residual-only baseline.
- CPU validation job `b411c5f8-115` completed successfully and verified `python validate.py --compare` inside the compute container.
- The packaged benchmark covers two synthetic settings, so it reaches `core_claim_plus`: high uniform corruption and cycle-consistent adversarial corruption.

## Results

The first CPU job produced valid method artifacts but failed final validation because `scores.json` contained extra diagnostic fields not declared in `reference.json`.

Observed reproduced numbers from the failed job's generated `scores.json`:
- `uniform_high_noise`: Cycle-Sync median location error `0.2047`; residual-only Welsch IRLS `0.3630`; paper reference `0.24` and `0.36`.
- `adversarial_high_noise`: Cycle-Sync median location error `0.1638`; residual-only Welsch IRLS `0.2465`; paper reference `0.17` and `0.32`.

These results support the core claim numerically. The scorer contract is now verified in-container.

## Remaining

An attempted expansion to the paper's noiseless uniform-corruption exact-recovery claim did not pass: with the current approximate T-AAB initializer, `uniform_exact_recovery` produced `0.1005` median error and `0.0` exact-recovery rate. That unsupported target was removed from the score contract rather than claimed.

To reach still higher milestones, implement the full real-image SfM pipeline: MPLS-cycle sample generation, STE direction estimation, and ETH3D/IMC style experiments. The current environment focuses on the paper's synthetic location-estimation experiments.

## Issues

The login-node Python environment lacks NumPy/SciPy, so numerical execution is delegated to the compute container. The first job failure was a scoring schema mismatch, not a method runtime failure; the second job passed after diagnostics were separated from `scores.json`.

The continuation audit flagged that the original evaluator used an L2 similarity alignment. This has been replaced with an IRLS/Weiszfeld implementation of the paper's L1 translation-scale alignment before the expanded job.

Job `68267221-a05` completed the expanded computation but failed validation because the unsupported exact-recovery experiment emitted a baseline method not present in `reference.json`. The evaluator now skips undeclared experiments when a reference contract is supplied, and the unsupported exact-recovery target has been removed.

## Deviations from Paper

- The T-AAB initializer is implemented with the standard triangle coplanarity residual over well-shaped cycles. The paper cites AAB's closed-form geodesic residual; this reproduction preserves the truncated cycle-consistency initialization and subsequent Cycle-Sync computation but may not exactly match the initializer's closed-form constants.
