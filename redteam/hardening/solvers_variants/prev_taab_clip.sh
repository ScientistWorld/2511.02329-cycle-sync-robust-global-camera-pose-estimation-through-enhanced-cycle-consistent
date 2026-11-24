#!/bin/bash
# Hardening variant "prev_taab_clip": Cycle-Sync with the previous iteration's invented T-AAB temperatures and weight clipping (exact WLS).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python method/solve.py --taab-temps gym --weight-clip weight --input-dir "$1" --output-dir "$2"
