#!/bin/bash
# Hardening variant "cycle_sync": the reference, rerun (must match the stored reference exactly).
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
python method/solve.py --input-dir "$1" --output-dir "$2"
