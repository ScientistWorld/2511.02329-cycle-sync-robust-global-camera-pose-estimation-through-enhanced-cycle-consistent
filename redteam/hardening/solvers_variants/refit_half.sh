#!/bin/bash
# Hardening check solver "refit_half" (same interface as scripts/solvers/*.sh).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python redteam/hardening/refit_solver.py --rho 0.5 --input-dir "$1" --output-dir "$2"
