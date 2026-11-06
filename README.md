# Cycle-Sync: Robust Global Camera Pose Estimation through Enhanced Cycle-Consistent Synchronization

<!-- scope-note -->
> [!NOTE]
> **Not a full reproduction of the paper.** This environment keeps the paper's core problem at a reduced scale so it is easy to run. It measures an AI scientist's idea and how well it is carried out, not the full research loop.

| This paper | Scientist World, the framework this environment belongs to |
|:---:|:---:|
| <a href="https://arxiv.org/abs/2511.02329"><img alt="This paper on arXiv" src="https://img.shields.io/badge/arXiv-2511.02329-b31b1b?logo=arxiv&logoColor=white"></a> | <a href="https://arxiv.org/abs/2611.08478"><img alt="Scientist World on arXiv" src="https://img.shields.io/badge/arXiv-2611.08478-b31b1b?logo=arxiv&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world"><img alt="Scientist World code" src="https://img.shields.io/badge/Code-Scientist_World-181717?logo=github&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world_cli"><img alt="Command line code" src="https://img.shields.io/badge/Code-Command_line-181717?logo=github&logoColor=white"></a> |

| **Paper ID** | [2511.02329](https://arxiv.org/abs/2511.02329) |
|:---|:---|
| **Domain** | Computer Vision / Structure-from-Motion |
| **TL;DR** | Cycle-Sync estimates camera poses globally by using cycle-consistent message passing to robustly downweight corrupted pairwise directions. |

## Summary

The paper addresses robust global camera pose estimation, with emphasis on estimating camera locations from corrupted pairwise unit directions. Its location solver alternates weighted least squares with cycle-consistency-based edge reweighting under a Welsch-type loss. On synthetic data, it remains accurate at high uniform corruption and near the adversarial `q < 0.5` limit where residual-only and prior solvers degrade. On real SfM datasets, the full pipeline combines this solver with robust rotation and direction estimation.

## Problem

Recover absolute 3D camera locations from a measurement graph whose edges contain pairwise unit direction observations between cameras. The recovered locations are identifiable only up to a global translation and scale, so the task is to estimate the relative camera configuration.

## The paper's method

The paper introduces Cycle-Sync, a robust global camera pose framework whose central contribution is a camera-location solver that adapts message-passing least squares to location estimation without known inter-camera distances.

## Key results of the paper

- Synthetic high-noise uniform corruption (`q=0.7`, `sigma=0.2`): reported median error `0.24` versus `0.36` for residual-only reweighting.
- Synthetic high-noise adversarial corruption (`q=0.45`, `sigma=0.2`): reported median error `0.17` versus `0.32` for residual-only reweighting.
- This reproduction scores the same two high-noise synthetic settings and the supplementary annealing-schedule variants from Tables 14 and 15.
- On ETH3D location-estimation comparisons, the paper reports average median error near `0.01` for Cycle-Sync under STE preprocessing.

## Run it

```bash
pip install sciworld
sw research 2511.02329 --mode innovate --agent claude-code
sw evaluate 2511.02329
```

## More

The full problem statement, method notes, evaluation protocol and reproduction log are in [DETAILS.md](DETAILS.md).

