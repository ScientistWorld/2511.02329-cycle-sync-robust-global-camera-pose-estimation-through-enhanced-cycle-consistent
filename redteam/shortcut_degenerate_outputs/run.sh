#!/bin/bash
# Shortcut / degenerate check: NaN, constant and random estimates.
set -e
source /home/user/redteam/common/lib.sh
D=$RT/shortcut_degenerate_outputs
WS=$D/ws
make_ws "$WS" $ALL_REF_METHODS
(cd "$WS" && python "$D/apply.py")
train_eval "$WS"
hidden_test "$WS" "$D"
python - "$D/scores_test.json" > "$D/json_check.txt" <<'EOF'
import json, sys
text = open(sys.argv[1]).read()
def reject(tok):
    raise ValueError(tok)
try:
    json.loads(text, parse_constant=reject)
    print("scores_test.json is strict JSON: True")
except ValueError as exc:
    print("scores_test.json is strict JSON: False (contains", exc, ")")
EOF
cat "$D/json_check.txt"
touch "$D/done"
