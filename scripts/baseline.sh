#!/bin/bash
# Run the residual-only Welsch IRLS baseline on the public train instances
# through the solver interface and print its scores.
#
# Usage:
#   bash scripts/baseline.sh

set -e

cd /home/user

python eval/train/evaluate.py --methods welsch_irls \
    --out outputs/scores_baseline.json --diagnostics-out outputs/diagnostics_baseline.json
