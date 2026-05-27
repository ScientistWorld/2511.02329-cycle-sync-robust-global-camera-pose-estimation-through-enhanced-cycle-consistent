#!/bin/bash
# Run the paper's proposed method.
#
# This script trains/runs the paper's method using code in method/.
#
# Usage:
#   bash scripts/method.sh

set -e

cd /home/user

python method/run_synthetic.py "$@"

if [ "${SKIP_EVALUATE:-0}" != "1" ]; then
    bash scripts/evaluate.sh
fi
