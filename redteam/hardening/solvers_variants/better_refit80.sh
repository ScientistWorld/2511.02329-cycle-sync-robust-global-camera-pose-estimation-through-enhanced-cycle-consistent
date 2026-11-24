#!/bin/bash
# Hardening variant "better_refit80": better: as better_refit on the top 0.8(1-q)|E| edges.
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python redteam/hardening/refit_solver.py --rho 0.8 --input-dir "$1" --output-dir "$2"
