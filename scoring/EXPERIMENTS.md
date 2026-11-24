# Experiment Overview

Both experiments score a camera-location solver on fixed problem instances that the evaluator owns: the solver receives only the viewing graph and the observed pairwise directions, and every metric is recomputed from the locations it returns. The ranked numbers come from 40 hidden instances per experiment; 20 public instances per experiment, drawn from the same generator, are available for development.

## uniform_high_noise

Tests whether a camera-location estimator can recover a global camera configuration when most pairwise direction observations (70%) are independently replaced by unrelated random directions and the remaining observations are noisy.

This setting measures robustness to severe but unstructured outliers. The median per-camera error is the headline quantity; the mean and 90th-percentile errors check that the improvement is not limited to the typical camera while many cameras stay badly placed.

## adversarial_high_noise

Tests whether a camera-location estimator can remain accurate when the corrupted directions (45%) are mutually consistent with an alternative camera configuration, making the outliers harder to identify than independent random errors.

This setting measures robustness near the ambiguity limit of this corruption model (the alternative configuration cannot claim the majority of edges), with the same graph size, density and noise level as the uniform setting and the same three error metrics.
