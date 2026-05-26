# Problem Definition

What problem does this paper address? Write this so that someone with no knowledge of the paper can understand what needs to be solved and how success is measured.

Do NOT describe the paper's method or solution here — only the problem itself. Think about if a future scientist agent try to solve this problem from scratch without knowing what approach the paper took. If you leak the solution, you compromise the benchmark.

## Research Question

Estimate absolute 3D camera locations from a graph of noisy, outlier-corrupted pairwise unit direction measurements. The estimates are only identifiable up to global translation and scale, so a solution must recover the relative camera configuration despite missing distances, graph sparsity, noise, and severe direction corruption.

## Why It Matters

Camera poses are a core input to structure-from-motion, 3D reconstruction, robotics, AR/VR, neural rendering, and Gaussian splatting. A robust global location estimator reduces reliance on incremental pipelines and bundle adjustment when pairwise image matches contain many outliers.

## Success Criteria

A successful solution returns camera locations with low median aligned translation error, remains stable under high corruption rates, and does not collapse to trivial all-zero or near-collinear configurations. It should outperform a residual-only robust least-squares baseline at the same graph size, corruption model, noise level, and number of trials.
