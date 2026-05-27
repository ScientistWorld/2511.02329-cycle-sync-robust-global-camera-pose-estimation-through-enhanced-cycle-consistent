#!/bin/bash
# Evaluate the visible train slice of saved method outputs.
#
# Mirrors scripts/evaluate.sh's manifest-based contract while writing
# scoring/scores_train.json instead of scoring/scores.json.

set -e

cd /home/user

mkdir -p scoring

python eval/train/evaluate.py "$@"
