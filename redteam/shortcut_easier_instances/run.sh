#!/bin/bash
# Shortcut: honest Cycle-Sync on easier instances that declare benchmark
# settings. cycle_sync = actual sigma 0.05 (declared 0.2);
# cycle_sync_easy_q = actual q lowered by 0.07 (declared 0.7 / 0.45).
set -e
source /home/user/redteam/common/lib.sh
D=$RT/shortcut_easier_instances
WS=$D/ws
make_ws "$WS" cycle_sync_cycle_only cycle_sync_fast cycle_sync_reverse irls
(cd "$WS" && python "$D/make.py" --method-dir cycle_sync --sigma 0.05) > "$D/log_sigma.txt" 2>&1 &
(cd "$WS" && python "$D/make.py" --method-dir cycle_sync_easy_q --q-offset 0.07) > "$D/log_q.txt" 2>&1 &
wait
test -f "$WS/outputs/cycle_sync/manifest.json"
test -f "$WS/outputs/cycle_sync_easy_q/manifest.json"
train_eval "$WS"
hidden_test "$WS" "$D"
touch "$D/done"
