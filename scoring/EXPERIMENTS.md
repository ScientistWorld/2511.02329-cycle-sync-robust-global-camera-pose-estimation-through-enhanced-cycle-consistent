# Experiment Overview

## uniform_high_noise
Tests whether a camera-location estimator can recover a global camera configuration when most pairwise direction observations are independently replaced by unrelated random directions and the remaining observations are noisy.

This experiment also compares the annealing schedules reported in the paper's high-noise synthetic ablation. The schedule variants test whether a solver is robust because it gradually shifts from residual information to graph-consistency information, rather than relying on either source alone.

## adversarial_high_noise
Tests whether a camera-location estimator can remain accurate when corrupted directions are mutually consistent with an alternative camera configuration, making the outliers harder to reject than independent random errors.

This experiment includes the same annealing-schedule variants under cycle-consistent corruption near the model limit, where residual-only reweighting is especially vulnerable.
