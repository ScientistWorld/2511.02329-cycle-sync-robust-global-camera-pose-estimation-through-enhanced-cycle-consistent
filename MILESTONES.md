# Reproduction Milestones

**Current: core_claim**

<!-- Milestone levels (update "Current" above as you progress):
  none             — just started, no meaningful progress yet
  method_runs      — the paper's method executes end-to-end without errors
  core_claim       — minimum experiment supports the paper's central claim
  core_claim_plus  — core claim reproduced on additional settings
  secondary_claims — secondary results or contributions reproduced
  majority         — more than half of reported results reproduced
  near_complete    — most results reproduced, only minor gaps remain
  full             — all reported results reproduced
-->

## Progress Log

### [2026-05-26 23:40] - none
- Read the paper and identified Cycle-Sync's core location-estimation algorithm and synthetic evaluation protocol.
- Implemented the paper's Welsch-weighted WLS loop with cycle-consistency message passing, plus a residual-only Welsch IRLS comparator.
- Added synthetic data generation, artifact-based evaluation, scoring reference targets, scripts, and packaging dependencies.
- Static validation passes; compute job is needed before claiming `method_runs`.

### [2026-05-27 00:00] - method_runs
- CPU test job executed Cycle-Sync and residual-only Welsch IRLS on both synthetic benchmark settings and produced output artifacts.
- Cycle-Sync improved over the residual-only baseline in both settings and matched the scale of the paper's Supplement Table 14/15 numbers.
- Job failed only at final validation because diagnostics were written into `scoring/scores.json`; evaluator has been patched to keep diagnostics separate.

### [2026-05-27 00:12] - core_claim
- Regenerated schema-valid `scoring/scores.json` from job artifacts.
- `uniform_high_noise`: Cycle-Sync median error `0.2047` versus residual-only Welsch IRLS `0.3630`, matching the paper's reported scale (`0.24` versus `0.36`).
- `adversarial_high_noise`: Cycle-Sync median error `0.1638` versus residual-only Welsch IRLS `0.2465`, matching the paper's reported scale (`0.17` versus `0.32`).
- `python validate.py --compare` passes locally on the generated scores; a CPU validation job is being submitted to verify the patched evaluator in-container.

## Stop Justification
- Not stopped. A CPU validation job is being submitted to verify the patched evaluator in-container.
