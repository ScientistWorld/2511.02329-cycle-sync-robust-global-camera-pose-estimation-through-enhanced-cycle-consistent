# Evaluation

How success is measured. Describe only the metrics, targets, and evaluation procedure — do NOT describe the paper's method or how they achieved these results. Think of this as a general evaluation protocal for other scientists trying to solve the same problem, where they should not see this paper's solution.

## Metrics

The primary metric is median camera-location error. Estimated locations are aligned to ground truth by a global translation and scalar scale, then Euclidean error is computed per camera and the median over cameras is reported. Lower is better.

The evaluation also reports the realized corruption fraction, number of graph edges, number of trials, and exact-recovery rate. Exact recovery means median location error below `1e-4`, following the paper.

## Baselines and Targets

The reference target for the proposed method is the paper's Supplement Table 14 and Table 15 synthetic annealing ablation: median error `0.24` for uniform corruption with `q=0.7`, `sigma=0.2`, and median error `0.17` for adversarial cycle-consistent corruption with `q=0.45`, `sigma=0.2`. The residual-only Welsch IRLS baseline from the same tables reports `0.36` and `0.32`, respectively.

## Evaluation Protocol

Synthetic camera locations are sampled from `N(0, I_3)`. The viewing graph is Erdos-Renyi with edge probability `p=0.5`. The standard reproduction uses `n=100` cameras and 10 independent trials. Uniform corruption replaces a corrupted direction with a random Gaussian unit vector; adversarial corruption replaces it with a direction generated from an alternative camera cloud. Evaluation reads saved method artifacts in `outputs/` and writes `scoring/scores.json`.
