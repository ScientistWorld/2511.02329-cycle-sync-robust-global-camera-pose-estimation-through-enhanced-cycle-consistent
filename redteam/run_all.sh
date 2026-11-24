#!/bin/bash
# Run every redteam check and shortcut in one CPU job, then summarise.
# Heavy runs (new Cycle-Sync solves) go in the background; light runs that
# only rewrite the reference's saved outputs run in the foreground. A run that
# already finished (its done marker exists) is skipped, so a killed job can be
# resubmitted and resumes.
cd /home/user
RT=/home/user/redteam
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "cpus: $(nproc)"

run() {
  local name=$1
  if [ -f "$RT/$name/done" ]; then echo "skip $name (done)"; return 0; fi
  echo "[$(date +%T)] start $name"
  local t0=$SECONDS
  bash "$RT/$name/run.sh" > "$RT/$name/log.txt" 2>&1
  echo "[$(date +%T)] end $name rc=$? ($((SECONDS - t0)) s)"
}

run variant_seed_spread &
run variant_better_tmax40 &
run variant_weaker_tmax3 &
run shortcut_easier_instances &
run bruteforce_ransac &

for name in variant_reference variant_better_refit shortcut_copy_truth shortcut_oracle_mask \
    shortcut_trim_cameras shortcut_drop_hard_experiment shortcut_degenerate_outputs \
    shortcut_forged_scores_after_crash; do
  run "$name"
done
wait
run shortcut_seed_cherry_pick
python "$RT/common/summarize.py" > "$RT/summary_stdout.txt" 2>&1
cat "$RT/summary_stdout.txt"
