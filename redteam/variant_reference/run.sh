#!/bin/bash
# Re-score the gym's own reference outputs (seed base 100) through the hidden
# test in a sandbox, and check the result equals the committed
# scoring/scores_test.json. This anchors every other comparison.
set -e
source /home/user/redteam/common/lib.sh
D=$RT/variant_reference
WS=$D/ws
make_ws "$WS" $ALL_REF_METHODS
train_eval "$WS"
hidden_test "$WS" "$D"
python - "$D/scores_test.json" "$ROOT/scoring/scores_test.json" > "$D/match.txt" <<'EOF'
import json, sys
a = json.load(open(sys.argv[1])); b = json.load(open(sys.argv[2]))
print("identical to committed scoring/scores_test.json:", a == b)
EOF
cat "$D/match.txt"
touch "$D/done"
