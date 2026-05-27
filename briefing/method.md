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
