#!/usr/bin/env python3
"""phase_a_rerender.py — Track 3 Task 2 Phase A renders.

Produces the three Phase-1 renders per room that the per-room viewer.html
consumes:

    bedroom_default.glb       (manifest defaults)
    bedroom_warm_sunset.glb   (params/bedroom_warm_sunset.json)
    bedroom_cool_morning.glb  (params/bedroom_cool_morning.json)

    bathroom_default.glb       (manifest defaults)
    bathroom_warm_sunset.glb   (params/bathroom_warm_sunset.json)
    bathroom_cool_morning.glb  (params/bathroom_cool_morning.json)

Also re-renders the pre-existing bedroom_default.glb whose .meta.json
sidecar has `resolved_params: {}` — that's the empty-defaults bug. The
wrapper's idempotency check would otherwise treat the broken sidecar as
valid and refuse to re-render.

Idempotency:
    For each render target, this script reads the sidecar and only
    invokes the wrapper if (a) the .glb is missing, (b) the sidecar is
    missing, or (c) the sidecar's resolved_params dict does not match
    what the wrapper would resolve from the manifest/params file.

Run from the diggss/ directory:
    cd ~/Knowledge_Atlas/160sp/track3/diggss
    python3 ../../../scripts/track3/phase_a_rerender.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


# Resolve paths relative to this script's location (scripts/track3/).
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent                              # ~/Knowledge_Atlas
DIGGSS = REPO_ROOT / "160sp" / "track3" / "diggss"          # student dir
WRAPPER = HERE / "infinigen_wrapper.py"


# (room, output_filename, params_source)
# params_source is either ("default", None) or ("file", "params/<name>.json").
RENDER_PLAN: list[tuple[str, str, tuple[str, str | None]]] = [
    ("bedroom",  "bedroom_default.glb",      ("default", None)),
    ("bedroom",  "bedroom_warm_sunset.glb",  ("file",    "bedroom_warm_sunset.json")),
    ("bedroom",  "bedroom_cool_morning.glb", ("file",    "bedroom_cool_morning.json")),
    ("bathroom", "bathroom_default.glb",     ("default", None)),
    ("bathroom", "bathroom_warm_sunset.glb", ("file",    "bathroom_warm_sunset.json")),
    ("bathroom", "bathroom_cool_morning.glb",("file",    "bathroom_cool_morning.json")),
]


def manifest_for(room: str) -> Path:
    return DIGGSS / "manifests" / f"{room}.manifest.json"


def params_for(filename: str) -> Path:
    return DIGGSS / "params" / filename


def out_for(filename: str) -> Path:
    return DIGGSS / "renders" / filename


def resolve_target_params(room: str, source: tuple[str, str | None]) -> dict:
    """Compute what the wrapper SHOULD resolve, for idempotency comparison."""
    kind, val = source
    if kind == "default":
        mf = manifest_for(room)
        with open(mf) as f:
            manifest = json.load(f)
        return {k: v["default"]
                for k, v in manifest["properties"].items()
                if "default" in v}
    if kind == "file":
        with open(params_for(val)) as f:
            return json.load(f)
    raise ValueError(f"unknown source kind {kind!r}")


def already_good(out_path: Path, expected: dict) -> bool:
    """True if the .glb exists and its sidecar's resolved_params matches expected."""
    if not out_path.exists():
        return False
    sidecar = out_path.with_suffix(out_path.suffix + ".meta.json")
    if not sidecar.exists():
        return False
    try:
        with open(sidecar) as f:
            sc = json.load(f)
    except Exception:
        return False
    return sc.get("resolved_params") == expected


def invoke_wrapper(room: str, out_path: Path, source: tuple[str, str | None]) -> int:
    cmd = [
        sys.executable, str(WRAPPER),
        "--room", room,
        "--manifest", str(manifest_for(room)),
        "--out", str(out_path),
        "--verbose",
    ]
    kind, val = source
    if kind == "default":
        cmd.append("--params-default")
    else:
        cmd.extend(["--params", str(params_for(val))])

    print(f"\n--- render: {out_path.name} ---")
    print(" ".join(cmd))
    return subprocess.call(cmd)


def main() -> int:
    if not WRAPPER.exists():
        sys.stderr.write(f"Cannot find wrapper at {WRAPPER}\n")
        return 1

    out_for("placeholder").parent.mkdir(parents=True, exist_ok=True)

    summary: list[tuple[str, str]] = []
    for room, fname, source in RENDER_PLAN:
        out_path = out_for(fname)
        try:
            expected = resolve_target_params(room, source)
        except FileNotFoundError as e:
            print(f"SKIP {fname}: missing input ({e})")
            summary.append((fname, "MISSING_INPUT"))
            continue

        if already_good(out_path, expected):
            print(f"OK   {fname}: sidecar already matches; skipping.")
            summary.append((fname, "SKIPPED_OK"))
            continue

        # If the .glb exists but the sidecar is empty/wrong, force re-render
        # by deleting it.  This is the bedroom_default.glb fix.
        if out_path.exists():
            print(f"NOTE {fname}: existing file has stale sidecar; will re-render.")
            out_path.unlink()
            sidecar = out_path.with_suffix(out_path.suffix + ".meta.json")
            sidecar.unlink(missing_ok=True)

        rc = invoke_wrapper(room, out_path, source)
        summary.append((fname, "OK" if rc == 0 else f"FAIL({rc})"))

    print("\n=== Phase A render summary ===")
    for fname, status in summary:
        print(f"  {status:>14}  {fname}")
    failed = [f for f, s in summary if s.startswith("FAIL") or s == "MISSING_INPUT"]
    return 0 if not failed else 2


if __name__ == "__main__":
    sys.exit(main())
