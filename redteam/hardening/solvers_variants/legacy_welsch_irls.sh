#!/bin/bash
# Hardening variant "legacy_welsch_irls": the pre-hardening residual-only baseline (alternating approximate WLS).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python method/solve.py --algorithm irls --wls alternating --weight-clip weight --input-dir "$1" --output-dir "$2"
