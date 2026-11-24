#!/bin/bash
# Run the paper's method (Cycle-Sync and its annealing-schedule ablations) on
# the public train instances through the solver interface and print scores.
#
# Usage:
#   bash scripts/method.sh

set -e

cd /home/user

python eval/train/evaluate.py \
    --methods cycle_sync cycle_sync_reverse cycle_sync_cycle_only cycle_sync_fast \
    --out outputs/scores_method.json --diagnostics-out outputs/diagnostics_method.json
