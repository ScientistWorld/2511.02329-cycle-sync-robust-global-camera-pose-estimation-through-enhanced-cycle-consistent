#!/bin/bash
# Public evaluation: run every registered solver (scripts/solvers/<method>.sh)
# on the public train instances (data/instances/train/) and write
# scoring/scores.json. Uses only code in eval/ and never imports method/.
#
# To add a method, add scripts/solvers/<name>.sh taking <input_dir> <output_dir>
# (see briefing/evaluation.md for the file format).
#
# Usage: bash scripts/evaluate.sh [--methods NAME ...]

set -e

cd /home/user

mkdir -p scoring

python eval/train/evaluate.py --out scoring/scores.json --diagnostics-out scoring/diagnostics.json "$@"
