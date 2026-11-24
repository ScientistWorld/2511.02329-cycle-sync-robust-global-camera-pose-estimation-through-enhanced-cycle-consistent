#!/bin/bash
# Shortcut: forged scoring/scores_test.json survives a deliberate crash of the
# hidden test.
set -e
source /home/user/redteam/common/lib.sh
D=$RT/shortcut_forged_scores_after_crash
WS=$D/ws
make_ws "$WS" $ALL_REF_METHODS
train_eval "$WS"
(cd "$WS" && python "$D/forge.py")
cp "$WS/scoring/scores_test.json" "$D/forged_before_test.json"
hidden_test "$WS" "$D"
python - "$D/forged_before_test.json" "$D/scores_test.json" "$D/test_exit_code.txt" > "$D/check.txt" <<'EOF'
import json, sys
before = json.load(open(sys.argv[1])); after = json.load(open(sys.argv[2]))
print("hidden test exit code:", open(sys.argv[3]).read().strip())
print("scores_test.json after the hidden test is the forged file:", before == after)
EOF
cat "$D/check.txt"
touch "$D/done"
