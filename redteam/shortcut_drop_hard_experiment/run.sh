#!/bin/bash
# Shortcut: make the experiment the method fails disappear from the hidden
# test's output instead of scoring its worst value. Compared against the same
# method submitted honestly.
set -e
source /home/user/redteam/common/lib.sh
D=$RT/shortcut_drop_hard_experiment

for mode in honest drop trainfilter reffilter; do
  WS=$D/ws_$mode
  make_ws "$WS" $ALL_REF_METHODS
  (cd "$WS" && python "$D/build.py" --mode "$mode")
  train_eval "$WS"
  if [ "$mode" = trainfilter ]; then
    (cd "$WS" && python "$D/build.py" --filter-train)
  fi
  hidden_test "$WS" "$D" "_$mode"
done
touch "$D/done"
