# Experiment Overview

## uniform_high_noise

Tests whether a camera-location estimator can recover a global camera configuration when most pairwise direction observations are independently replaced by unrelated random directions and the remaining observations are noisy.

This setting measures robustness to severe but unstructured outliers while holding graph size, graph density, noise level, corruption probability, and trial count fixed.

## adversarial_high_noise

Tests whether a camera-location estimator can remain accurate when corrupted directions are mutually consistent with an alternative camera configuration, making the outliers harder to identify than independent random errors.

This setting measures robustness near the ambiguity limit for this corruption model while using the same graph size, graph density, noise level, and trial count as the uniform-outlier setting.
