# Evaluation Targets

## uniform_high_noise

Optimize camera-location recovery under high independent random direction corruption with additive noise.

- Primary metric: `median_location_error` (lower is better)
- Supporting metrics: `mean_location_error`, `p90_location_error`
- Constraint checks: `benchmark_instance_valid_rate`, `mean_corruption_fraction`
- Standard run: `bash scripts/reproduce.sh`, then inspect `scoring/scores.json`

## adversarial_high_noise

Optimize camera-location recovery under high cycle-consistent adversarial direction corruption with additive noise.

- Primary metric: `median_location_error` (lower is better)
- Supporting metrics: `mean_location_error`, `p90_location_error`
- Constraint checks: `benchmark_instance_valid_rate`, `mean_corruption_fraction`
- Standard run: `bash scripts/reproduce.sh`, then inspect `scoring/scores.json`
