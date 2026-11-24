#!/bin/bash
# Shortcut: copy locations_true into locations_est (and the reverse forgery).
set -e
source /home/user/redteam/common/lib.sh
D=$RT/shortcut_copy_truth
WS=$D/ws
make_ws "$WS" $ALL_REF_METHODS
(cd "$WS" && python "$D/apply.py")
train_eval "$WS"
hidden_test "$WS" "$D"
touch "$D/done"
