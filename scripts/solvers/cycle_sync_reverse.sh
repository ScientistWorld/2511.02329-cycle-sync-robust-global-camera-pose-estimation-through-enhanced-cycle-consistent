#!/bin/bash
# Solver entry point for method "cycle_sync_reverse".
# Usage: bash scripts/solvers/cycle_sync_reverse.sh <input_dir> <output_dir>
# Reads <input_dir>/*.npz (n, edges, directions, experiment) and writes
# <output_dir>/<same name>.npz holding "locations" (n x 3).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
python method/solve.py --schedule ten_over_t_plus_10 --input-dir "$1" --output-dir "$2"
