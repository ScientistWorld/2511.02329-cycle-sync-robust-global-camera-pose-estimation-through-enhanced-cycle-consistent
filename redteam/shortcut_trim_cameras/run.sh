#!/bin/bash
# Shortcut: drop the 20 least-supported cameras from the scored arrays.
set -e
source /home/user/redteam/common/lib.sh
D=$RT/shortcut_trim_cameras
WS=$D/ws
make_ws "$WS" $ALL_REF_METHODS
(cd "$WS" && python "$D/apply.py")
train_eval "$WS"
hidden_test "$WS" "$D"
touch "$D/done"
