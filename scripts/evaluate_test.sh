#!/bin/bash
# Hidden-test evaluation: run every registered solver (scripts/solvers/*.sh)
# on the hidden instances held in eval/test/ and write scoring/scores_test.json.
# Takes no arguments; scores every method on disk.

set -e

cd /home/user

mkdir -p scoring

python eval/test/evaluate.py
