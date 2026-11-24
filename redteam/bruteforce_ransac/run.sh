#!/bin/bash
# Brute-force check: budgeted hypothesize-and-verify search over inlier sets
# on the gym's instances, written as the agent's cycle_sync output.
set -e
source /home/user/redteam/common/lib.sh
D=$RT/bruteforce_ransac
WS=$D/ws
make_ws "$WS" cycle_sync irls
(cd "$WS" && python "$D/apply.py")
train_eval "$WS"
hidden_test "$WS" "$D"
touch "$D/done"
