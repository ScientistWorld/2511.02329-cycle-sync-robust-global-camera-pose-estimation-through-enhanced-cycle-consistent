#!/bin/bash
# Train-slice evaluation: run every registered solver (scripts/solvers/*.sh)
# on the public train instances and write scoring/scores_train.json.

set -e

cd /home/user

mkdir -p scoring

python eval/train/evaluate.py "$@"
