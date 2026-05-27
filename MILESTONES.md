# Reproduction Milestones

**Current: secondary_claims**

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

### [2026-05-27 00:37] - secondary_claims
- CPU job `4e1d83ec-1f1` regenerated all high-noise synthetic outputs and passed `python validate.py --compare` in the compute container.
- Reproduced the paper's annealing-schedule ablation for `lambda_t=t/(t+10)`, residual-only Welsch IRLS, reverse annealing, cycle-only weighting, and fast annealing on both uniform and adversarial high-noise settings.

### [2026-05-27 00:52] - secondary_claims
- Updated `scripts/run.sh` to regenerate the reproduction outputs from scratch before scoring.
- Expanded the main evaluator to write every declared metric in `scoring/reference.json`; milestone remains `secondary_claims` while the validation job runs.

### [2026-05-27 01:33] - secondary_claims
- CPU validation job `20621f4b-374` was killed before completing all ablation artifacts, leaving a partial `scores.json`.
- Added restart-safe scoring behavior and prepared a CPU continuation job to regenerate the missing ablation outputs, rewrite all score files, and rerun validation.
