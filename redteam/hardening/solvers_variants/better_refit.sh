#!/bin/bash
# Hardening check solver "better_refit" (same interface as scripts/solvers/*.sh).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python redteam/hardening/refit_solver.py --rho 1.0 --input-dir "$1" --output-dir "$2"
