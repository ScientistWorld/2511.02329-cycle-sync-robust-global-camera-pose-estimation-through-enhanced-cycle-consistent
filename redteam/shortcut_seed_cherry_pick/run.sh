#!/bin/bash
# Shortcut: cherry-pick seeds and steer the hash split, honest solver only.
# Reuses the seed-spread reruns as the pool (generates them if absent).
set -e
source /home/user/redteam/common/lib.sh
D=$RT/shortcut_seed_cherry_pick
for s in 200 300; do
  if [ ! -f "$RT/variant_seed_spread/ws_s$s/outputs/cycle_sync/manifest.json" ]; then
    bash "$RT/variant_seed_spread/run.sh"
    break
  fi
done
WS=$D/ws
make_ws "$WS" cycle_sync_cycle_only cycle_sync_fast cycle_sync_reverse irls
(cd "$WS" && python "$D/apply.py")
train_eval "$WS"
hidden_test "$WS" "$D"
touch "$D/done"
