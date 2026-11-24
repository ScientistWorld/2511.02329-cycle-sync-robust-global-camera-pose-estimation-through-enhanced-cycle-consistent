#!/bin/bash
# Hardening job: build the fixed instances, score the reference solvers on the
# train and hidden test instances (from scratch), run the hardening variants
# and shortcuts through the real evaluators, then validate.

set -e

cd /home/user

python -c "import sys, numpy, scipy; print(sys.version); print('numpy', numpy.__version__, 'scipy', scipy.__version__)"
rm -rf outputs/cycle_sync outputs/cycle_sync_reverse outputs/cycle_sync_cycle_only outputs/cycle_sync_fast outputs/irls

python data/make_instances.py
python eval/test/make_instances.py
# Safety copy in case the job is killed while the evaluator hides the files
# (removed before the shortcut pass, which must find no copy of the truth).
mkdir -p tmp/test_instances_backup && cp eval/test/instances/*.npz tmp/test_instances_backup/
python redteam/hardening/smoke.py

mkdir -p redteam/hardening/results
python eval/train/evaluate.py --per-instance-out redteam/hardening/results/per_instance_train_reference.json
cp scoring/scores_train.json scoring/scores.json
cp scoring/diagnostics_train.json scoring/diagnostics.json
python eval/test/evaluate.py --per-instance-out redteam/hardening/results/per_instance_test_reference.json

bash redteam/hardening/run_checks.sh || echo "hardening checks returned $?"
rm -rf tmp/test_instances_backup

python validate.py --post-design --compare
