#!/bin/bash
# Reproduce the gym end to end: score every registered solver (the paper's
# Cycle-Sync, its annealing ablations and the baselines) on the fixed public
# train instances and the hidden test instances, run the hardening variants and
# shortcuts through the real evaluators, then validate.
# The instance files are committed; make_instances.py only writes missing ones
# (passing --force to eval/test/make_instances.py would draw a new hidden test
# from fresh unrecorded seeds and invalidate every stored test score).

set -e

cd /home/user

python -c "import sys, numpy, scipy; print(sys.version); print('numpy', numpy.__version__, 'scipy', scipy.__version__)"

python data/make_instances.py
python eval/test/make_instances.py
python redteam/hardening/smoke.py

mkdir -p redteam/hardening/results
python eval/train/evaluate.py --per-instance-out redteam/hardening/results/per_instance_train_reference.json
cp scoring/scores_train.json scoring/scores.json
cp scoring/diagnostics_train.json scoring/diagnostics.json
python eval/test/evaluate.py --per-instance-out redteam/hardening/results/per_instance_test_reference.json

bash redteam/hardening/run_checks.sh || echo "hardening checks returned $?"

python validate.py --post-design --compare
