#!/bin/bash
# Hardening checks: run better / weaker / legacy variants and the shortcut
# solvers through the real evaluators, then summarise.
#
# Assumes the reference scores (scoring/scores_{train,test}.json) are already
# written. The shortcut pass uses the default output path of the hidden test
# (scoring/scores_test.json) so that a solver trying to forge that file is
# tested faithfully; the reference files are saved first and restored after.

set -u

cd /home/user

R=redteam/hardening/results
mkdir -p "$R"

echo "=== variants: hidden test ==="
python eval/test/evaluate.py --solvers-dir redteam/hardening/solvers_variants \
    --out "$R/scores_test_variants.json" --diagnostics-out "$R/diagnostics_test_variants.json" \
    --per-instance-out "$R/per_instance_test_variants.json" > "$R/log_test_variants.txt" 2>&1
echo "variants test rc=$?"

echo "=== variants: train ==="
python eval/train/evaluate.py --solvers-dir redteam/hardening/solvers_variants \
    --out "$R/scores_train_variants.json" --diagnostics-out "$R/diagnostics_train_variants.json" \
    --per-instance-out "$R/per_instance_train_variants.json" > "$R/log_train_variants.txt" 2>&1
echo "variants train rc=$?"

echo "=== shortcuts: hidden test (default output path) ==="
rm -rf tmp/test_instances_backup
SAVE="$(mktemp -d)"
cp scoring/scores_test.json scoring/diagnostics_test.json "$SAVE"/
# A forged score file placed before the run must not survive it.
cat > scoring/scores_test.json <<'EOF'
{"experiments": {"uniform_high_noise": {"results": {"cycle_sync": {"median_location_error": 0.0, "mean_location_error": 0.0, "p90_location_error": 0.0}}}, "adversarial_high_noise": {"results": {"cycle_sync": {"median_location_error": 0.0, "mean_location_error": 0.0, "p90_location_error": 0.0}}}}}
EOF
python eval/test/evaluate.py --solvers-dir redteam/hardening/solvers_shortcuts \
    --per-instance-out "$R/per_instance_test_shortcuts.json" > "$R/log_test_shortcuts.txt" 2>&1
echo "shortcuts test rc=$?"
mv scoring/scores_test.json "$R/scores_test_shortcuts.json"
mv scoring/diagnostics_test.json "$R/diagnostics_test_shortcuts.json"
cp "$SAVE"/scores_test.json "$SAVE"/diagnostics_test.json scoring/
rm -rf "$SAVE"
ls -la eval/test/instances/

echo "=== analysis ==="
python redteam/hardening/analyze.py
