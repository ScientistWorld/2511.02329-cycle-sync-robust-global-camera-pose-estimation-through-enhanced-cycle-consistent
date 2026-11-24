#!/bin/bash
# Hardening check solver "mixed_exactwls_legacysoftmin" (same interface as scripts/solvers/*.sh).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python method/solve.py --wls exact --softmin legacy --input-dir "$1" --output-dir "$2"
