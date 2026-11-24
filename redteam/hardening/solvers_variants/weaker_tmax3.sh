#!/bin/bash
# Hardening variant "weaker_tmax3": weaker: Cycle-Sync stopped after 3 iterations.
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python method/solve.py --t-max 3 --input-dir "$1" --output-dir "$2"
