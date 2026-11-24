#!/bin/bash
# Rerun the reference method (Cycle-Sync, paper settings, the gym's own
# method/run_synthetic.py) and the residual-only baseline on three instance
# seed bases (100 = the gym's, 200, 300), 10 trials per experiment each, and
# score every run through the hidden test. Cycle-Sync is deterministic given
# an instance, so the instance seed is the only source of spread.
set -e
source /home/user/redteam/common/lib.sh
D=$RT/variant_seed_spread

gen() {
  local seed=$1 ws=$D/ws_s$1
  make_ws "$ws"
  (
    cd "$ws"
    python "$ROOT/method/run_synthetic.py" --methods cycle_sync --n 100 --p 0.5 \
      --trials 10 --seed "$seed" --t-max 20 --out-root outputs
    python "$ROOT/baseline/run_irls.py" --n 100 --p 0.5 --trials 10 --seed "$seed" \
      --t-max 20 --out-dir outputs/irls
  )
  train_eval "$ws"
  hidden_test "$ws" "$D" "_s$seed"
}

gen 100 > "$D/log_s100.txt" 2>&1 &
gen 200 > "$D/log_s200.txt" 2>&1 &
gen 300 > "$D/log_s300.txt" 2>&1 &
wait
for s in 100 200 300; do
  test -f "$D/scores_test_s$s.json" || { echo "seed $s failed"; exit 1; }
done
touch "$D/done"
