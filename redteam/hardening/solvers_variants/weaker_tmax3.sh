#!/bin/bash
# Hardening check solver "weaker_tmax3" (same interface as scripts/solvers/*.sh).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python method/solve.py --t-max 3 --input-dir "$1" --output-dir "$2"
