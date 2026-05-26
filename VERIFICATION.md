# Verification

Validated in compute job `b411c5f8-115` with exit code 0.

Command path: `scripts/run.sh` reused existing method artifacts, regenerated scores with `scripts/evaluate.sh`, and ran `python validate.py --compare`.

Result: all scoring and structure checks passed. Reproduced median location errors:
- `uniform_high_noise`: Cycle-Sync `0.2047`, Welsch IRLS `0.3630`
- `adversarial_high_noise`: Cycle-Sync `0.1638`, Welsch IRLS `0.2465`
