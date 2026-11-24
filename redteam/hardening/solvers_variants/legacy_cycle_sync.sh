#!/bin/bash
# Hardening variant "legacy_cycle_sync": the pre-hardening implementation (alternating approximate WLS, legacy softmin, invented T-AAB temperatures, weight clipping).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python method/solve.py --wls alternating --softmin legacy --taab-temps gym --weight-clip weight --input-dir "$1" --output-dir "$2"
