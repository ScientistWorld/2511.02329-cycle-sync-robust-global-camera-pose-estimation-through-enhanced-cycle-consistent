#!/bin/bash
# Better-variant check: Cycle-Sync followed by an L2 refit on its most trusted
# edges, computed from the reference's own saved Cycle-Sync outputs (final
# weights), for three inlier-set sizes. The size to report is chosen on the
# train slice.
set -e
source /home/user/redteam/common/lib.sh
D=$RT/variant_better_refit
WS=$D/ws
make_ws "$WS" $ALL_REF_METHODS
(cd "$WS" && python "$D/apply.py")
train_eval "$WS"
hidden_test "$WS" "$D"
touch "$D/done"
