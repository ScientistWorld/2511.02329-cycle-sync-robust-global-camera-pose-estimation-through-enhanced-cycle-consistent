#!/bin/bash
# More iterations: the reference Cycle-Sync with t_max=40 instead of 20 on the
# gym's instances (seed base 100), written as the agent's cycle_sync output.
set -e
source /home/user/redteam/common/lib.sh
D=$RT/variant_better_tmax40
WS=$D/ws
make_ws "$WS" irls
(cd "$WS" && python "$ROOT/method/run_synthetic.py" --methods cycle_sync --n 100 --p 0.5 \
  --trials 10 --seed 100 --t-max 40 --out-root outputs)
train_eval "$WS"
hidden_test "$WS" "$D"
touch "$D/done"
