# Evaluation Targets

## Primary: uniform_high_noise
Tests camera-location recovery under high random outlier corruption with additive direction noise.
- **Metric**: `median_location_error` (lower is better)
- **Constraint metric**: `mean_corruption_fraction` (the benchmark must keep the high-corruption setting fixed)
- **Run**: `bash scripts/reproduce.sh`, then inspect `scoring/scores.json`

## Primary: adversarial_high_noise
Tests camera-location recovery under cycle-consistent adversarial outlier corruption with additive direction noise.
- **Metric**: `median_location_error` (lower is better)
- **Constraint metric**: `mean_corruption_fraction` (the benchmark must keep the near-limit adversarial corruption setting fixed)
- **Run**: `bash scripts/reproduce.sh`, then inspect `scoring/scores.json`
