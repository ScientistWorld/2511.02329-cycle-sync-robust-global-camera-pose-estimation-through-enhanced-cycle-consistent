# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

### [2026-05-27 00:07] - core_claim_plus
- Previous compute-container runs validated Cycle-Sync on both high-noise uniform corruption and high-noise cycle-consistent adversarial corruption.
- The reproduced median errors beat the residual-only Welsch IRLS baseline in both settings and are numerically close to the paper's Supplement Tables 14 and 15.

### [2026-05-27 00:07] - core_claim_plus
- Replaced the T-AAB initialization residual with the AAB-style geodesic distance to the positive-scale feasible cycle arc.
- Added the paper's remaining annealing schedule variants for a follow-up CPU job; milestone remains `core_claim_plus` until those new results finish.

### [2026-05-27 00:09] - core_claim_plus
- Continuation audit confirmed the existing core results are from the implemented Cycle-Sync algorithm and an independent artifact evaluator.
- Expanded annealing-schedule outputs were absent, so a CPU reproduction job is being resubmitted before claiming `secondary_claims`.
