#!/bin/bash
# Hardening check solver "legacy_welsch_irls" (same interface as scripts/solvers/*.sh).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python method/solve.py --algorithm irls --wls alternating --input-dir "$1" --output-dir "$2"
