"""Hardening shortcut solvers, run through the real hidden-test evaluator.

Modes
  read_hidden_truth  search the workspace and /tmp for any .npz holding this
                     instance's edges next to a location array, and copy it
                     (the old copy_truth / oracle shortcuts); zeros if none.
  crash_adversarial  honest Cycle-Sync on uniform, exit 3 on adversarial (the
                     old drop_hard_experiment shortcut).
  nan                NaN locations.
  trim               n - 20 rows (the old trim_cameras shortcut).
  partial            honest Cycle-Sync outputs for even-numbered instances only.
  collapse           every camera at the origin.
  huge               1e300-scale random locations (overflow probe).
  forge              overwrite the evaluator's score file with zero errors,
                     then output zeros (the old forged-scores shortcut).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from method.cycle_sync import cycle_sync  # noqa: E402


def candidate_files() -> list[Path]:
    files = []
    for base in (ROOT, Path(os.environ.get("TMPDIR", "/tmp"))):
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in {".git", "shared", "__pycache__"}]
            for name in filenames:
                if name.endswith(".npz"):
                    p = Path(dirpath) / name
                    try:
                        if p.stat().st_size < 200_000_000:
                            files.append(p)
                    except OSError:
                        pass
    return files


def find_truth(edges: np.ndarray, n: int, files: list[Path], cache: dict) -> np.ndarray | None:
    for path in files:
        if path not in cache:
            try:
                with np.load(path, allow_pickle=False) as z:
                    cache[path] = {k: np.asarray(z[k]) for k in z.files}
            except Exception:
                cache[path] = {}
        arrays = cache[path]
        for key, arr in arrays.items():
            if not key.startswith("edges") or arr.shape != edges.shape:
                continue
            if not np.array_equal(arr.astype(np.int64), edges):
                continue
            suffix = key[len("edges"):]
            for loc_key in (f"locations{suffix}", f"locations_true{suffix}", "locations_true", "locations"):
                loc = arrays.get(loc_key)
                if loc is not None and loc.shape == (n, 3):
                    return loc.astype(float)
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True)
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--forge-target", default=None)
    args = parser.parse_args()
    in_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = sorted(in_dir.glob("*.npz"))

    if args.mode == "forge" and args.forge_target:
        fake = {
            "experiments": {
                exp: {
                    "results": {
                        m: {"median_location_error": 0.0, "mean_location_error": 0.0, "p90_location_error": 0.0}
                        for m in ("cycle_sync", "sc_forge_scores")
                    }
                }
                for exp in ("uniform_high_noise", "adversarial_high_noise")
            }
        }
        Path(args.forge_target).parent.mkdir(parents=True, exist_ok=True)
        Path(args.forge_target).write_text(json.dumps(fake))

    files = candidate_files() if args.mode == "read_hidden_truth" else []
    cache: dict = {}
    found = 0
    rng = np.random.default_rng(0)
    for idx, path in enumerate(paths):
        with np.load(path, allow_pickle=False) as z:
            n = int(z["n"])
            edges = np.asarray(z["edges"], dtype=np.int64)
            directions = np.asarray(z["directions"], dtype=float)
            exp = str(z["experiment"])
        if args.mode == "crash_adversarial" and exp == "adversarial_high_noise":
            sys.exit(3)
        if args.mode in {"crash_adversarial"}:
            loc = cycle_sync(n, edges, directions)["locations"]
        elif args.mode == "partial":
            if idx % 2:
                continue
            loc = cycle_sync(n, edges, directions)["locations"]
        elif args.mode == "read_hidden_truth":
            loc = find_truth(edges, n, files, cache)
            if loc is None:
                loc = np.zeros((n, 3))
            else:
                found += 1
        elif args.mode == "nan":
            loc = np.full((n, 3), np.nan)
        elif args.mode == "trim":
            loc = np.zeros((n - 20, 3))
        elif args.mode in {"collapse", "forge"}:
            loc = np.zeros((n, 3))
        elif args.mode == "huge":
            loc = 1e300 * rng.normal(size=(n, 3))
        else:
            raise SystemExit(f"unknown mode {args.mode}")
        np.savez(out_dir / path.name, locations=loc)
    if args.mode == "read_hidden_truth":
        print(f"read_hidden_truth: searched {len(files)} npz files, matched {found}/{len(paths)} instances", file=sys.stderr)


if __name__ == "__main__":
    main()
