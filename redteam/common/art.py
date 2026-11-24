"""Artifact helpers used by redteam shortcut and variant scripts.

All paths in manifests are relative to the sandbox workspace, and scripts run
with the sandbox as their working directory, exactly like the gym's own
method and baseline scripts do in /home/user.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/home/user")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXPERIMENTS = {
    "uniform_high_noise": {"corruption": "uniform", "q": 0.7, "sigma": 0.2},
    "adversarial_high_noise": {"corruption": "adversarial", "q": 0.45, "sigma": 0.2},
}


def read_manifest(method: str, ws: str | Path = ".") -> dict[str, list[str]]:
    return json.loads((Path(ws) / "outputs" / method / "manifest.json").read_text())


def write_manifest(method: str, manifest: dict[str, list[str]], ws: str | Path = ".") -> None:
    path = Path(ws) / "outputs" / method / "manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n")


def load(path: str | Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


def save(path: str | Path, arrays: dict[str, np.ndarray]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **arrays)


def derive(src_method, dst_method, fn, ws=".", experiments=None):
    """Write dst artifacts as fn(exp, arrays) of the src artifacts."""

    manifest = read_manifest(src_method, ws)
    out: dict[str, list[str]] = {}
    for exp, files in manifest.items():
        if experiments is not None and exp not in experiments:
            continue
        out[exp] = []
        for file_name in files:
            arrays = fn(exp, load(Path(ws) / file_name))
            dst = Path("outputs") / dst_method / exp / Path(file_name).name
            save(Path(ws) / dst, arrays)
            out[exp].append(str(dst))
    write_manifest(dst_method, out, ws)
    return out


def test_half_names(exp: str, names: list[str]) -> list[str]:
    """Names the hidden test will select (same rule as eval/test/evaluate.py)."""

    keyed = sorted((hashlib.sha256(f"{exp}:{n}".encode()).hexdigest(), n) for n in names)
    ordered = [n for _, n in keyed]
    return ordered[(len(ordered) + 1) // 2:]
