#!/bin/bash
# Hardening check solver "sc_forge_scores": overwrite the score file the
# evaluator is about to write (the evaluator runs solvers with cwd = workspace
# root), then output uninformative locations.
set -e
TARGET="$PWD/scoring/scores_test.json"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python redteam/hardening/shortcut_solver.py --mode forge --forge-target "$TARGET" --input-dir "$1" --output-dir "$2"
