#!/bin/bash
# Run the self-contained baselines (residual-only Welsch IRLS and LUD) on the
# public train instances through the solver interface and print their scores.
#
# Usage:
#   bash scripts/baseline.sh

set -e

cd /home/user

python eval/train/evaluate.py --methods welsch_irls lud \
    --out outputs/scores_baseline.json --diagnostics-out outputs/diagnostics_baseline.json
