"""Build the agent's cycle_sync output for the drop-experiment runs.

The agent's method is a real one that fails the adversarial setting: the
reference Cycle-Sync estimates on uniform_high_noise and the residual-only
Welsch IRLS estimates on adversarial_high_noise (same instances).

--mode honest      : both experiments written.
--mode drop        : adversarial_high_noise left out of the manifest.
--mode trainfilter : both written; after evaluate_train.sh the agent deletes
                     adversarial_high_noise/cycle_sync from scores_train.json.
--mode reffilter   : both written; the agent writes its own
                     scoring/reference.json that lists only uniform_high_noise
                     (the agent is not given the gym's reference.json).
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from art import read_manifest, write_manifest  # noqa: E402

ADV = "adversarial_high_noise"


def build(mode: str) -> None:
    manifest = read_manifest("cycle_sync")
    irls = read_manifest("irls")
    dst_dir = Path("outputs/cycle_sync") / ADV
    files = []
    for src in irls[ADV]:
        dst = dst_dir / Path(src).name
        shutil.copyfile(src, dst)
        files.append(str(dst))
    manifest[ADV] = files
    if mode == "drop":
        manifest.pop(ADV)
    write_manifest("cycle_sync", manifest)
    if mode == "reffilter":
        ref_path = Path("scoring/reference.json")
        ref = json.loads(ref_path.read_text())
        ref["experiments"].pop(ADV)
        ref_path.write_text(json.dumps(ref, indent=2) + "\n")


def filter_train() -> None:
    path = Path("scoring/scores_train.json")
    scores = json.loads(path.read_text())
    scores["experiments"][ADV]["results"].pop("cycle_sync")
    path.write_text(json.dumps(scores, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["honest", "drop", "trainfilter", "reffilter"])
    ap.add_argument("--filter-train", action="store_true")
    args = ap.parse_args()
    if args.filter_train:
        filter_train()
    else:
        build(args.mode)
