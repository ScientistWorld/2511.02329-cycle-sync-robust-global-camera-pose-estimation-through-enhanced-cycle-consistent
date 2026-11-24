# Overview

- **Paper ID:** 2511.02329
- **Title:** Cycle-Sync: Robust Global Camera Pose Estimation through Enhanced Cycle-Consistent Synchronization
- **Domain:** Computer Vision / Structure-from-Motion
- **TL;DR:** Cycle-Sync estimates camera poses globally by using cycle-consistent message passing to robustly downweight corrupted pairwise directions.

## Short Summary

The paper addresses robust global camera pose estimation, with emphasis on estimating camera locations from corrupted pairwise unit directions. Its location solver alternates weighted least squares with cycle-consistency-based edge reweighting under a Welsch-type loss. On synthetic data, it remains accurate at high uniform corruption and near the adversarial `q < 0.5` limit where residual-only and prior solvers degrade. On real SfM datasets, the full pipeline combines this solver with robust rotation and direction estimation.

## Key Results

- Synthetic high-noise uniform corruption (`q=0.7`, `sigma=0.2`, Supplement Table 14): reported median error `0.24` versus `0.36` for residual-only reweighting (`lambda_t = 0`).
- Synthetic high-noise adversarial corruption (`q=0.45`, `sigma=0.2`, Supplement Table 15): reported median error `0.17` versus `0.32` for residual-only reweighting.
- This gym scores the same two settings, with the corruption models of the authors' released code, on 40 hidden instances each. Reproduced hidden-test median errors: `0.283` (uniform) and `0.204` (adversarial) for Cycle-Sync versus `0.333` / `0.250` for `lambda_t = 0`; the five annealing schedules of Tables 14-15 come out in the paper's order. Noiseless exact recovery at `q=0.8` uniform and `q=0.4` adversarial also reproduces.
- On ETH3D location-estimation comparisons, the paper reports average median error near `0.01` for Cycle-Sync under STE preprocessing (not part of this gym).

---

# Problem Definition

## Research Question

Recover absolute 3D camera locations from a measurement graph whose edges contain pairwise unit direction observations between cameras. The recovered locations are identifiable only up to a global translation and scale, so the task is to estimate the relative camera configuration.

## Inputs and Outputs

Each problem instance provides:
- `n` cameras.
- An undirected viewing graph over the cameras.
- A unit direction vector for each graph edge.

A solver must output one 3D location per camera. It sees only these observations: no ground-truth locations, corruption labels, inter-camera distances or image measurements are available.

## Difficulty

The benchmark stresses high outlier rates, noisy clean directions, missing graph edges, and variable inter-camera distances. In one setting most directions are independent random outliers; in the other, almost half of the directions are outliers generated from an internally consistent but wrong camera configuration, which makes them hard to tell apart from the true structure. Even the clean directions carry angular noise.

## Success Criteria

A successful solution has low aligned camera-location error across many independent instances, in both the typical camera and the worst-placed cameras, and remains stable under severe corruption.

---

# Paper's Method

How the paper approaches the problem, i.e. the paper's core contributions.

## Key Contribution

The paper introduces Cycle-Sync, a robust global camera pose framework whose central contribution is a camera-location solver that adapts message-passing least squares to location estimation without known inter-camera distances.

## Approach

For camera locations, Cycle-Sync optimizes a Welsch-type robust objective over absolute locations and per-edge distances, with constraints `alpha_ij >= 1` and centered locations. Each iteration solves a weighted least-squares location problem, computes residuals, estimates edge corruption through weighted 3-cycle inconsistencies, blends residual and cycle scores with `lambda_t = t / (t + 10)`, and updates weights as `exp(-4 h) / (h + delta)` (h clipped to `[1e-8, 10]`). Initial weights `exp(-20 s)` are obtained from truncated AAB-style geodesic cycle scores over well-shaped triangles (angle between the two other sides in `[arcsin 0.6, pi - arcsin 0.6]`), re-averaged five times with cycle weights at the temperatures of the authors' release (`tau = 2, 4, 8, 16, 20` on radian scores).

In this gym the weighted least-squares step is solved exactly (as the authors' active-set solver does), Eq. 6 averages over every 3-cycle of an edge, and `t_max = 20`, `beta = 20`, `delta = 1e-8`. The implementation is `method/cycle_sync.py`, registered as `scripts/solvers/cycle_sync.sh`; the annealing ablations of Supplement Tables 14-15 are registered as `cycle_sync_reverse`, `cycle_sync_cycle_only`, `cycle_sync_fast` and `cycle_sync_residual_only` (`lambda_t = 0`).

The full paper also adds MPLS-cycle for rotation synchronization and STE-based robust direction estimation/filtering for real image pipelines. This reproduction focuses on the synthetic location-estimation experiments that isolate the paper's core location solver.

## Main Claims

Primary claim: cycle-consistency message passing makes global camera-location estimation robust under high uniform and cycle-consistent adversarial direction corruption, outperforming residual-only robust reweighting and prior location solvers.

Secondary claims: the approach improves deterministic recovery guarantees, strengthens global SfM pipelines without bundle adjustment, improves rotation synchronization through MPLS-cycle, and benefits from robust subspace-based direction filtering.

---

# Evaluation

## Protocol: solvers on fixed instances

A method is a **solver**: an executable script `scripts/solvers/<name>.sh` taking two arguments,

    bash scripts/solvers/<name>.sh <input_dir> <output_dir>

`<input_dir>` holds one file `inst_XXX.npz` per problem instance with

- `n` — number of cameras (100),
- `edges` — `m x 2` integer array of camera pairs `(i, j)` with `i < j`,
- `directions` — `m x 3` unit vectors; row `e` approximates `(t_i - t_j) / ||t_i - t_j||` for edge `e = (i, j)`,
- `experiment` — the setting's name (`uniform_high_noise` or `adversarial_high_noise`).

The solver must write `<output_dir>/inst_XXX.npz` (same file name) containing `locations`, an `n x 3` finite array of estimated camera locations. Nothing else in the output is read.

The evaluators own the instances and the ground truth; a solver only ever sees the observations above. Every registered solver is run on every instance of every experiment, and every number is recomputed from the returned locations.

- `scripts/evaluate_train.sh` (and `scripts/evaluate.sh`) run every registered solver on the public train instances in `data/instances/train/` (20 per setting, ground truth included, regenerable with `python data/make_instances.py`) and write `scoring/scores_train.json` (`scoring/scores.json`).
- `scripts/evaluate_test.sh` runs every registered solver on hidden test instances (40 per setting) drawn from the same generator with unpublished seeds, and writes `scoring/scores_test.json`. The hidden test ranks methods; you cannot see or regenerate its instances.

Both sides use the same generator, the same interface and the same metrics, so an honest method scores alike on both.

## Metrics

For each instance the estimate is aligned to the ground truth by the L1 similarity fit (one global scale and translation minimising the sum of per-camera Euclidean distances, the paper's gauge), and the per-camera errors are computed. Per experiment, the reported value is the mean over instances of:

- `median_location_error` (primary, the paper's headline metric) — median per-camera error;
- `mean_location_error` — mean per-camera error;
- `p90_location_error` — 90th-percentile per-camera error (tail failures).

All are lower-is-better. The ranking weighs both experiments equally and, within each, the median, mean and p90 errors with coefficients 1.0, 0.4 and 0.6.

## Failures

A solver that exits non-zero, or an instance whose output is missing, unreadable, of the wrong shape, or non-finite, scores that instance at the error of the uninformative output that puts every camera at one point (about 1.5 median error); valid outputs are capped at the same value. A failed experiment therefore costs its worst value rather than disappearing.

The method key `cycle_sync` is always scored (at the failure value if `scripts/solvers/cycle_sync.sh` is missing): the method being ranked is the one registered as `scripts/solvers/cycle_sync.sh`. Other registered solvers are scored alongside it for comparison.

## Experiments

Both settings use `n = 100` cameras with i.i.d. standard Gaussian 3D locations, an Erdos-Renyi viewing graph with edge probability `p = 0.5`, and noise level `sigma = 0.2`: a clean edge observes its true unit direction plus `sigma` times a uniformly random unit vector, renormalised (see `data/synthetic.py`).

- `uniform_high_noise`: each edge is, with probability `q = 0.7`, replaced by an unrelated uniformly random unit direction.
- `adversarial_high_noise`: each edge is, with probability `q = 0.45`, replaced by the direction between the same two cameras in a second, independent camera configuration, so the corrupted edges agree with each other; noise is then added to every edge.

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

### Iteration 11: claude-opus-5-5 (hardener)
- **Milestone**: `secondary_claims` | **Status**: error
- **Working time**: 22m | **GPU**: 0.0h
- **Jobs**: 2 total (1 completed, 1 failed)

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

### Iteration 11: claude-opus-5-5 (hardener)
- **Milestone**: `secondary_claims` | **Status**: done
- **Working time**: 15m | **GPU**: 0.0h
- **Jobs**: 4 total (3 completed, 1 failed)

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

### [2026-11-24 07:10] - secondary_claims
- Hardening (final pass): the synthetic generator now follows the authors' released corruption models; T-AAB temperatures and h clipping come from the authors' code; the paper's lambda=0 number is attached to the lambda=0 ablation (`cycle_sync_residual_only`); LUD added as a baseline.
- Hidden test (40 instances per setting): Cycle-Sync 0.283 / 0.204 median error vs lambda=0 0.333 / 0.250; all five annealing schedules in the paper's order; noiseless exact recovery reproduced. `validate.py --post-design --compare` passes. Details in `HARDENING.md`.

</details>


---

# Reproduction Milestones

**Current: secondary_claims**
