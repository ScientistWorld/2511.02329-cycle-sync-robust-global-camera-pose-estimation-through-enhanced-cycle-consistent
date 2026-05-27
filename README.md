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
- On ETH3D location-estimation comparisons, the paper reports average median error near `0.01` for Cycle-Sync under STE preprocessing.

---

# Problem Definition

What problem does this paper address? Write this so that someone with no knowledge of the paper can understand what needs to be solved and how success is measured.

Do NOT describe the paper's method or solution here — only the problem itself. Think about if a future scientist agent try to solve this problem from scratch without knowing what approach the paper took. If you leak the solution, you compromise the benchmark.

## Research Question

Estimate absolute 3D camera locations from a graph of noisy, outlier-corrupted pairwise unit direction measurements. The estimates are only identifiable up to global translation and scale, so a solution must recover the relative camera configuration despite missing distances, graph sparsity, noise, and severe direction corruption.

## Why It Matters

Camera poses are a core input to structure-from-motion, 3D reconstruction, robotics, AR/VR, neural rendering, and Gaussian splatting. A robust global location estimator reduces reliance on incremental pipelines and bundle adjustment when pairwise image matches contain many outliers.

## Success Criteria

A successful solution returns camera locations with low median aligned translation error, remains stable under high corruption rates, and does not collapse to trivial all-zero or near-collinear configurations. It should outperform a residual-only robust least-squares baseline at the same graph size, corruption model, noise level, and number of trials.

---

# Paper's Method

How the paper approaches the problem, i.e. the paper's core contributions.

## Key Contribution

The paper introduces Cycle-Sync, a robust global camera pose framework whose central contribution is a camera-location solver that adapts message-passing least squares to location estimation without known inter-camera distances.

## Approach

For camera locations, Cycle-Sync optimizes a Welsch-type robust objective over absolute locations and per-edge distances, with constraints `alpha_ij >= 1` and centered locations. Each iteration solves a weighted least-squares location problem, computes residuals, estimates edge corruption through weighted 3-cycle inconsistencies, blends residual and cycle scores with `lambda_t = t / (t + 10)`, and updates weights as `exp(-4 h) / (h + delta)`. Initial weights are obtained from truncated AAB-style cycle coplanarity scores over well-shaped triangles.

The full paper also adds MPLS-cycle for rotation synchronization and STE-based robust direction estimation/filtering for real image pipelines. This reproduction focuses on the synthetic location-estimation experiments that isolate the paper's core location solver.

## Main Claims

Primary claim: cycle-consistency message passing makes global camera-location estimation robust under high uniform and cycle-consistent adversarial direction corruption, outperforming residual-only robust reweighting and prior location solvers.

Secondary claims: the approach improves deterministic recovery guarantees, strengthens global SfM pipelines without bundle adjustment, improves rotation synchronization through MPLS-cycle, and benefits from robust subspace-based direction filtering.

---

# Evaluation

How success is measured. Describe only the metrics, targets, and evaluation procedure — do NOT describe the paper's method or how they achieved these results. Think of this as a general evaluation protocal for other scientists trying to solve the same problem, where they should not see this paper's solution.

## Metrics

The primary metric is median camera-location error. Estimated locations are aligned to ground truth by a global translation and scalar scale, then Euclidean error is computed per camera and the median over cameras is reported. Lower is better.

The evaluation also reports the realized corruption fraction, number of graph edges, number of trials, and exact-recovery rate. Exact recovery means median location error below `1e-4`, following the paper.

## Baselines and Targets

The reference target for the proposed method is the paper's Supplement Table 14 and Table 15 synthetic annealing ablation: median error `0.24` for uniform corruption with `q=0.7`, `sigma=0.2`, and median error `0.17` for adversarial cycle-consistent corruption with `q=0.45`, `sigma=0.2`. The residual-only Welsch IRLS baseline from the same tables reports `0.36` and `0.32`, respectively.

## Evaluation Protocol

Synthetic camera locations are sampled from `N(0, I_3)`. The viewing graph is Erdos-Renyi with edge probability `p=0.5`. The standard reproduction uses `n=100` cameras and 10 independent trials. Uniform corruption replaces a corrupted direction with a random Gaussian unit vector; adversarial corruption replaces it with a direction generated from an alternative camera cloud. Evaluation reads saved method artifacts in `outputs/` and writes `scoring/scores.json`.

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


---

# Reproduction Milestones

**Current: core_claim**

## Stop Justification
- Completed at milestone `core_claim`.
