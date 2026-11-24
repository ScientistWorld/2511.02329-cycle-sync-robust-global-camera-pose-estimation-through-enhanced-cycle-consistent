#!/bin/bash
# Less optimisation: the reference Cycle-Sync stopped after t_max=3 iterations
# on the gym's instances (seed base 100), written as the agent's cycle_sync.
set -e
source /home/user/redteam/common/lib.sh
D=$RT/variant_weaker_tmax3
WS=$D/ws
make_ws "$WS" irls
(cd "$WS" && python "$ROOT/method/run_synthetic.py" --methods cycle_sync --n 100 --p 0.5 \
  --trials 10 --seed 100 --t-max 3 --out-root outputs)
train_eval "$WS"
hidden_test "$WS" "$D"
touch "$D/done"
