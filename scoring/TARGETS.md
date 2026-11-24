# Evaluation Targets

The ranked score is the hidden-test score of the solver registered as `scripts/solvers/cycle_sync.sh` (`scoring/scores_test.json`). Each experiment has weight 0.5; within an experiment the metrics count with coefficients 1.0 (median), 0.4 (mean) and 0.6 (p90). All metrics are lower-is-better.

## uniform_high_noise

Camera-location recovery under 70% independent random direction outliers with noisy clean directions.

- Primary metric: `median_location_error`
- Supporting metrics: `mean_location_error`, `p90_location_error` (an improvement must not come from the typical camera alone while the tail degrades)
- Reference: the paper's Cycle-Sync solver and its annealing-schedule ablations (Supplement Table 14); baselines `welsch_irls` and `lud`.

## adversarial_high_noise

Camera-location recovery under 45% cycle-consistent adversarial outliers with noisy directions.

- Primary metric: `median_location_error`
- Supporting metrics: `mean_location_error`, `p90_location_error`
- Reference: the paper's Cycle-Sync solver and its annealing-schedule ablations (Supplement Table 15); baselines `welsch_irls` and `lud`.

## Constraints

The paper's claim is better location accuracy on the same problem: the same graphs, the same corruption and the same noise. That constraint is enforced by construction rather than by a metric: the evaluator owns the instances (camera count, graph density, corruption model and rate, noise level, instance count), gives solvers only the observations, and scores a failed, missing, malformed or non-finite output at the worst value. The mean and p90 errors are the constraint on the error distribution: a method cannot raise its score by sacrificing the worst-placed cameras to improve the median.

Standard run: `bash scripts/evaluate_train.sh` (public instances) — the hidden test is `bash scripts/evaluate_test.sh`.
