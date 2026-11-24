#!/bin/bash
# Hardening check solver "mixed_altwls_stablesoftmin" (same interface as scripts/solvers/*.sh).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python method/solve.py --wls alternating --softmin stable --input-dir "$1" --output-dir "$2"
