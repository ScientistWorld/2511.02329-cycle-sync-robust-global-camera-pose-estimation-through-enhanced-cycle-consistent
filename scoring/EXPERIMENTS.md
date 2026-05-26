# Experiment Overview

## uniform_high_noise
Tests whether a camera-location estimator can recover a global camera configuration when most pairwise direction observations are independently replaced by unrelated random directions and the remaining observations are noisy.

## adversarial_high_noise
Tests whether a camera-location estimator can remain accurate when corrupted directions are mutually consistent with an alternative camera configuration, making the outliers harder to reject than independent random errors.

## uniform_exact_recovery
Tests whether a camera-location estimator reaches the noiseless exact-recovery regime rather than merely reducing average error under noisy corruption.
