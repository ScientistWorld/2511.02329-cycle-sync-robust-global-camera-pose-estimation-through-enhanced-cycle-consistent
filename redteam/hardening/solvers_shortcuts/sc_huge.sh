#!/bin/bash
# Hardening check solver "sc_huge" (same interface as scripts/solvers/*.sh).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python redteam/hardening/shortcut_solver.py --mode huge --input-dir "$1" --output-dir "$2"
