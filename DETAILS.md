# Overview

- **Paper ID:** 2511.02329
- **Title:** Cycle-Sync: Robust Global Camera Pose Estimation through Enhanced Cycle-Consistent Synchronization
- **Domain:** Computer Vision / Structure-from-Motion
- **TL;DR:** Cycle-Sync estimates camera poses globally by using cycle-consistent message passing to robustly downweight corrupted pairwise directions.

## Short Summary

The paper addresses robust global camera pose estimation, with emphasis on estimating camera locations from corrupted pairwise unit directions. Its location solver alternates weighted least squares with cycle-consistency-based edge reweighting under a Welsch-type loss. On synthetic data, it remains accurate at high uniform corruption and near the adversarial `q < 0.5` limit where residual-only and prior solvers degrade. On real SfM datasets, the full pipeline combines this solver with robust rotation and direction estimation.

## Key Results

- Synthetic high-noise uniform corruption (`q=0.7`, `sigma=0.2`): reported median error `0.24` versus `0.36` for residual-only reweighting.
- Synthetic high-noise adversarial corruption (`q=0.45`, `sigma=0.2`): reported median error `0.17` versus `0.32` for residual-only reweighting.
- This reproduction scores the same two high-noise synthetic settings and the supplementary annealing-schedule variants from Tables 14 and 15.
- On ETH3D location-estimation comparisons, the paper reports average median error near `0.01` for Cycle-Sync under STE preprocessing.

---

# Problem Definition

## Research Question

Recover absolute 3D camera locations from a measurement graph whose edges contain pairwise unit direction observations between cameras. The recovered locations are identifiable only up to a global translation and scale, so the task is to estimate the relative camera configuration.

## Inputs and Outputs

Each problem instance provides:
- `n` cameras.
- An undirected viewing graph over the cameras.
- A unit direction vector for each graph edge.

A solver must output one 3D location per camera. It must not use ground-truth locations, hidden corruption labels, inter-camera distances, image measurements, or any information not present in the benchmark artifact.

## Difficulty

The benchmark stresses high outlier rates, noisy clean directions, missing graph edges, and variable inter-camera distances. Some outliers are independent random directions, while others are generated from an internally consistent but wrong camera configuration.

## Success Criteria

A successful solution has low aligned camera-location error across multiple trials, remains stable under severe corruption, and preserves the benchmark settings for camera count, graph density, noise level, corruption model, and corruption rate.

---

# Paper's Method

How the paper approaches the problem, i.e. the paper's core contributions.

## Key Contribution

The paper introduces Cycle-Sync, a robust global camera pose framework whose central contribution is a camera-location solver that adapts message-passing least squares to location estimation without known inter-camera distances.

## Approach

For camera locations, Cycle-Sync optimizes a Welsch-type robust objective over absolute locations and per-edge distances, with constraints `alpha_ij >= 1` and centered locations. Each iteration solves a weighted least-squares location problem, computes residuals, estimates edge corruption through weighted 3-cycle inconsistencies, blends residual and cycle scores with `lambda_t = t / (t + 10)`, and updates weights as `exp(-4 h) / (h + delta)`. Initial weights are obtained from truncated AAB-style geodesic cycle scores over well-shaped triangles.

The full paper also adds MPLS-cycle for rotation synchronization and STE-based robust direction estimation/filtering for real image pipelines. This reproduction focuses on the synthetic location-estimation experiments that isolate the paper's core location solver.

## Main Claims

Primary claim: cycle-consistency message passing makes global camera-location estimation robust under high uniform and cycle-consistent adversarial direction corruption, outperforming residual-only robust reweighting and prior location solvers.

Secondary claims: the approach improves deterministic recovery guarantees, strengthens global SfM pipelines without bundle adjustment, improves rotation synchronization through MPLS-cycle, and benefits from robust subspace-based direction filtering.

---

# Evaluation

## Metrics

The primary metric is `median_location_error`. Estimated locations are aligned to ground truth by solving for a single global scale and translation, then Euclidean error is computed for each camera and the median over cameras is reported. Lower is better.

The score also includes `mean_location_error` and `p90_location_error` to capture average and tail failures that a median alone can hide. `benchmark_instance_valid_rate` checks whether scored artifacts match the required instance settings. `mean_corruption_fraction` is reported as a diagnostic constraint on benchmark difficulty.

## Experiments

The benchmark contains two synthetic camera-location recovery settings:
- `uniform_high_noise`: high-rate independent random direction outliers plus noisy clean measurements.
- `adversarial_high_noise`: high-rate outliers that are mutually consistent with an alternative camera configuration, plus noisy clean measurements.

Both settings use Gaussian 3D camera locations, an Erdos-Renyi viewing graph with edge probability `p=0.5`, `n=100` cameras, and 10 independent trials.

## Protocol

Methods write artifacts under `outputs/<method_name>/manifest.json`. Each manifest maps experiment names to `.npz` artifact files containing the true locations, estimated locations, graph edges, directions, corruption mask, and instance metadata. `scripts/evaluate.sh` reads those artifacts and writes `scoring/scores.json`; it does not run any method code.

Train and test evaluators split the same artifact set deterministically by trial filename hash. `scripts/evaluate_train.sh` writes `scoring/scores_train.json`; `scripts/evaluate_test.sh` writes `scoring/scores_test.json` and scores the same method keys present in the train file.

---

# Reproduction Log

### Iteration 1: gpt-5.5
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 9m | **GPU**: 0.0h
- **Jobs**: 2 total (1 completed, 1 failed)

<details>
<summary>Progress Log</summary>

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

### [2026-05-27 00:30] - core_claim_plus
- CPU validation job `b411c5f8-115` completed with exit code 0.
- In-container `python validate.py --compare` passed with schema-valid scores and all structural checks.
- The reproduction supports the paper's core robustness claim on both high-noise uniform corruption and high-noise cycle-consistent adversarial corruption.

</details>

### Iteration 2: gpt-5.5
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 6m | **GPU**: 0.0h
- **Jobs**: 4 total (2 completed, 2 failed)

<details>
<summary>Progress Log</summary>

### [2026-05-27 00:00] - core_claim_plus
- Validated Cycle-Sync synthetic location reproduction on uniform high-noise corruption and adversarial high-noise corruption.
- Confirmed the paper's proposed cycle-weighted solver improves over residual-only Welsch IRLS on both supported benchmark settings.
- Revalidated the package with the paper's L1 translation-scale alignment objective.

</details>

### Iteration 3: gpt-5.5
- **Milestone**: `secondary_claims` | **Status**: done
- **Working time**: 8m | **GPU**: 0.0h
- **Jobs**: 5 total (3 completed, 2 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 4: gpt-5.5 (designer_stage_1)
- **Milestone**: `secondary_claims` | **Status**: done
- **Working time**: 4m | **GPU**: 0.0h
- **Jobs**: 5 total (3 completed, 2 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 5: gpt-5.5 (designer_stage_2)
- **Milestone**: `secondary_claims` | **Status**: done
- **Working time**: 4m | **GPU**: 0.0h
- **Jobs**: 5 total (3 completed, 2 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 6: gpt-5.5 (designer_stage_3)
- **Milestone**: `secondary_claims` | **Status**: done
- **Working time**: 2m | **GPU**: 0.0h
- **Jobs**: 7 total (5 completed, 2 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 7: gpt-5.5 (packager)
- **Milestone**: `secondary_claims` | **Status**: done
- **Working time**: 1m | **GPU**: 0.0h
- **Jobs**: 7 total (5 completed, 2 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 8: gpt-5.5 (verifier)
- **Milestone**: `secondary_claims` | **Status**: done
- **Working time**: 9m | **GPU**: 0.0h
- **Jobs**: 9 total (6 completed, 3 failed)

<details>
<summary>Progress Log</summary>

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

### [2026-05-27 01:45] - secondary_claims
- CPU continuation job `2af2234f-ef6` completed successfully with exit code 0.
- The regenerated artifacts cover all five reported synthetic methods on both high-noise experiments; `python validate.py --compare` reports all checks passed.

</details>

### Iteration 9: gpt-5.5 (verifier)
- **Milestone**: `secondary_claims` | **Status**: done
- **Working time**: 5m | **GPU**: 0.0h
- **Jobs**: 9 total (6 completed, 3 failed)

<details>
<summary>Progress Log</summary>

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

### [2026-05-27 01:45] - secondary_claims
- CPU continuation job `2af2234f-ef6` completed successfully with exit code 0.
- The regenerated artifacts cover all five reported synthetic methods on both high-noise experiments; `python validate.py --compare` reports all checks passed.

### [2026-05-27 01:49] - secondary_claims
- Final audit confirmed the method implements the paper's Cycle-Sync location solver rather than a surrogate, and `eval/` remains method-independent.
- Replaced the stale continuation-only `scripts/run.sh` with a clean final verification runner that regenerates the full synthetic benchmark before validation.

### [2026-05-27 01:52] - secondary_claims
- Final verification found no critical scoring, separation, or train/test issues; `python validate.py --compare` passes.
- Reworded method-safe research direction guidance and removed ignored local bytecode caches.

</details>

### Iteration 10: claude-opus-5-5 (redteam)
- **Milestone**: `secondary_claims` | **Status**: done
- **Working time**: 13m | **GPU**: 0.0h
- **Jobs**: 1 total (1 completed, 0 failed)

<details>
<summary>Progress Log</summary>

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

### [2026-05-27 01:45] - secondary_claims
- CPU continuation job `2af2234f-ef6` completed successfully with exit code 0.
- The regenerated artifacts cover all five reported synthetic methods on both high-noise experiments; `python validate.py --compare` reports all checks passed.

### [2026-05-27 01:49] - secondary_claims
- Final audit confirmed the method implements the paper's Cycle-Sync location solver rather than a surrogate, and `eval/` remains method-independent.
- Replaced the stale continuation-only `scripts/run.sh` with a clean final verification runner that regenerates the full synthetic benchmark before validation.

### [2026-05-27 01:52] - secondary_claims
- Final verification found no critical scoring, separation, or train/test issues; `python validate.py --compare` passes.
- Reworded method-safe research direction guidance and removed ignored local bytecode caches.

</details>


---

# Reproduction Milestones

**Current: secondary_claims**
