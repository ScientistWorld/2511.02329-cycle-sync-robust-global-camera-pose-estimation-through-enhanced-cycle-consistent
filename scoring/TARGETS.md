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

## Secondary: uniform_exact_recovery
Tests the paper's noiseless exact-recovery claim under high uniform corruption.
- **Metric**: `exact_recovery_rate` (higher is better; median error below `1e-4`)
- **Constraint metrics**: `median_location_error`, `mean_corruption_fraction`
- **Run**: `bash scripts/reproduce.sh`, then inspect `scoring/scores.json`
