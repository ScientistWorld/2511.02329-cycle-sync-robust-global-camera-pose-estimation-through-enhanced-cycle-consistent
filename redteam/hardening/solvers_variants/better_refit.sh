#!/bin/bash
# Hardening variant "better_refit": better: Cycle-Sync, then an unweighted refit on its top (1-q)|E| edges by final weight.
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python redteam/hardening/refit_solver.py --rho 1.0 --input-dir "$1" --output-dir "$2"
