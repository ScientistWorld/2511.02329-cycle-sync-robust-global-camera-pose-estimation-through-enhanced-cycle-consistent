#!/bin/bash
# Reproduce the benchmark end to end.
#
# The paper's method and baseline need no training: each is a solver
# registered under scripts/solvers/ that the evaluators run on fixed instances.
#   1. public train instances (data/instances/train/, regenerated if missing)
#   2. train scoring  -> scoring/scores_train.json (copied to scoring/scores.json)
#   3. hidden test scoring -> scoring/scores_test.json (only where eval/test/
#      holds the hidden instances)

set -e

cd /home/user

python data/make_instances.py
bash scripts/evaluate_train.sh
cp scoring/scores_train.json scoring/scores.json
cp scoring/diagnostics_train.json scoring/diagnostics.json
if [ -f eval/test/instances/uniform_high_noise.npz ]; then
    bash scripts/evaluate_test.sh
fi
