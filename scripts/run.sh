#!/bin/bash
# Final hardening job: build the fixed train and hidden test instances from the
# authors' released corruption models (replacing the earlier Eq. 9-10 reading),
# score every registered solver on both from scratch, run the hardening
# variants and shortcuts through the real evaluators, then validate.
# --force regenerates the instances (new unrecorded test seeds); drop it to
# rescore the committed instances.

set -e

cd /home/user

python -c "import sys, numpy, scipy; print(sys.version); print('numpy', numpy.__version__, 'scipy', scipy.__version__)"

python data/make_instances.py --force
python eval/test/make_instances.py --force
python redteam/hardening/smoke.py

mkdir -p redteam/hardening/results
python eval/train/evaluate.py --per-instance-out redteam/hardening/results/per_instance_train_reference.json
cp scoring/scores_train.json scoring/scores.json
cp scoring/diagnostics_train.json scoring/diagnostics.json
python eval/test/evaluate.py --per-instance-out redteam/hardening/results/per_instance_test_reference.json

bash redteam/hardening/run_checks.sh || echo "hardening checks returned $?"

python validate.py --post-design --compare
