# Evaluation

## Metrics

The primary metric is `median_location_error`. Estimated locations are aligned to ground truth by solving for a single global scale and translation, then Euclidean error is computed for each camera and the median over cameras is reported. Lower is better.

The score also includes `mean_location_error` and `p90_location_error` to capture average and tail failures that a median alone can hide. `benchmark_instance_valid_rate` checks whether scored artifacts match the required instance settings. `mean_corruption_fraction` is reported as a diagnostic constraint on benchmark difficulty.

## Experiments

The benchmark contains two synthetic camera-location recovery settings:
- `uniform_high_noise`: high-rate independent random direction outliers plus noisy clean measurements.
- `adversarial_high_noise`: high-rate outliers that are mutually consistent with an alternative camera configuration, plus noisy clean measurements.

Both settings use Gaussian 3D camera locations, an Erdos-Renyi viewing graph with edge probability `p=0.5`, `n=100` cameras, and 10 independent trials.

## Protocol

Methods write artifacts under `outputs/<method_name>/manifest.json`. Each manifest maps experiment names to `.npz` artifact files containing the true locations, estimated locations, graph edges, directions, corruption mask, and instance metadata. `scripts/evaluate.sh` reads those artifacts and writes `scoring/scores.json`; it does not run any method code.

Train and test evaluators split the same artifact set deterministically by trial filename hash. `scripts/evaluate_train.sh` writes `scoring/scores_train.json`; `scripts/evaluate_test.sh` writes `scoring/scores_test.json` and scores the same method keys present in the train file.
