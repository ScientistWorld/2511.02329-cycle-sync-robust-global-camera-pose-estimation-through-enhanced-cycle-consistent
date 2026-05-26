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

if [ ! -f outputs/cycle_sync/manifest.json ] || [ ! -f outputs/irls/manifest.json ]; then
  bash scripts/reproduce.sh
else
  bash scripts/evaluate.sh
fi
python validate.py --compare
