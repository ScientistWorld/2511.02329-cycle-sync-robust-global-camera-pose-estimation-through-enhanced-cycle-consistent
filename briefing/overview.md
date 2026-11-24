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
