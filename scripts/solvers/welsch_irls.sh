#!/bin/bash
# Solver entry point for method "welsch_irls".
# Usage: bash scripts/solvers/welsch_irls.sh <input_dir> <output_dir>
# Reads <input_dir>/*.npz (n, edges, directions, experiment) and writes
# <output_dir>/<same name>.npz holding "locations" (n x 3).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
python baseline/solve_irls.py --input-dir "$1" --output-dir "$2"
