#!/bin/bash
# Shortcut: use the generator's corruption labels to pick inliers.
set -e
source /home/user/redteam/common/lib.sh
D=$RT/shortcut_oracle_mask
WS=$D/ws
make_ws "$WS" $ALL_REF_METHODS
(cd "$WS" && python "$D/apply.py")
train_eval "$WS"
hidden_test "$WS" "$D"
touch "$D/done"
