#!/bin/bash
# Example job script submitted via the end-of-turn YAML block.
#
# This runs inside the compute container with:
#   - Your workspace mounted at /home/user
#   - GPU(s) available
#   - No internet access
#
# Make sure all data, code, and dependencies are already in the
# workspace or baked into the container before submitting.

set -e

cd /home/user

# Continue the interrupted CPU validation job by regenerating only the
# artifacts that were missing after the full smoke run was killed.
SKIP_EVALUATE=1 bash scripts/method.sh --n 100 --p 0.5 --trials 10 --t-max 20 --methods cycle_sync_cycle_only cycle_sync_fast

bash scripts/evaluate.sh
bash scripts/evaluate_train.sh
bash scripts/evaluate_test.sh
python validate.py --compare
