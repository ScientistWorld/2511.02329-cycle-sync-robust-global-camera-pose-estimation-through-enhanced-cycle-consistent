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
