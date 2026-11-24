#!/bin/bash
# Hardening check solver "legacy_cycle_sync" (same interface as scripts/solvers/*.sh).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python method/solve.py --wls alternating --softmin legacy --input-dir "$1" --output-dir "$2"
