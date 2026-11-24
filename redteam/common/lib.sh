# Shared helpers for redteam runs. Source this from a run.sh.
#
# Every run builds a fresh sandbox workspace ("ws") holding the gym's own
# evaluation surface: eval/ (unchanged copy), scripts/evaluate_train.sh and
# scripts/evaluate_test.sh (unchanged except that their `cd /home/user` line
# points at the sandbox), scoring/reference.json, and copies of whichever
# reference output directories the run needs. The shortcut or variant is then
# put in place inside the sandbox the way a future agent would do it in its
# own workspace, the agent's train evaluation is run, and finally the hidden
# test script is run with no arguments. The gym's real outputs/ and scoring/
# are never modified.

ROOT=/home/user
RT=$ROOT/redteam
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1

make_ws() {  # make_ws <abs ws dir> [reference method dirs to copy...]
  local ws="$1"; shift
  rm -rf "$ws"
  mkdir -p "$ws/scripts" "$ws/scoring" "$ws/outputs"
  cp -r "$ROOT/eval" "$ws/eval"
  find "$ws/eval" -name __pycache__ -prune -exec rm -rf {} +
  local s
  for s in evaluate_train.sh evaluate_test.sh; do
    sed "s#^cd /home/user\$#cd \"$ws\"#" "$ROOT/scripts/$s" > "$ws/scripts/$s"
    if ! grep -q "^cd \"$ws\"\$" "$ws/scripts/$s"; then
      echo "failed to retarget $s into $ws" >&2
      return 1
    fi
  done
  cp "$ROOT/scoring/reference.json" "$ws/scoring/reference.json"
  local m
  for m in "$@"; do
    cp -r "$ROOT/outputs/$m" "$ws/outputs/$m"
  done
}

train_eval() {  # train_eval <ws>: what the agent runs before signalling done
  bash "$1/scripts/evaluate_train.sh"
}

hidden_test() {  # hidden_test <ws> <dest dir> [tag]
  local ws="$1" dest="$2" tag="${3:-}" rc f
  mkdir -p "$dest"
  bash "$ws/scripts/evaluate_test.sh" && rc=0 || rc=$?
  echo "$rc" > "$dest/test_exit_code${tag}.txt"
  for f in scores_test diagnostics_test scores_train; do
    if [ -f "$ws/scoring/$f.json" ]; then
      cp "$ws/scoring/$f.json" "$dest/${f}${tag}.json"
    fi
  done
  echo "hidden test for $ws exited with $rc"
  return 0
}

ALL_REF_METHODS="cycle_sync cycle_sync_cycle_only cycle_sync_fast cycle_sync_reverse irls"
