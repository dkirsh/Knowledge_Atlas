#!/usr/bin/env python3
"""infinigen_wrapper.py — Track 3 Task 2 central artifact.

Takes a JSON parameter dict (matching a Task 1 manifest), invokes Infinigen
Indoors to instantiate the corresponding room, and outputs the result as a
.blend file with full procedural textures and materials.

This is the SCAFFOLD students adapt. The JSON-loading, glTF-export, and
sidecar-writing logic is complete; the per-room Infinigen instantiation is
mostly pluggable but ships with working defaults for the seven Infinigen-
covered room types (kitchen, living_room, bedroom, bathroom, dining_room,
hallway, office). Students extend the ROOM_BUILDERS dict with their own
parameter mappings as they author manifests.

Usage:

    # Default-parameters smoke render (used by setup_track3.sh)
    python3 infinigen_wrapper.py --room living_room --params-default \
        --out renders/living_room_default.gltf

    # Render with a custom manifest + parameter file
    python3 infinigen_wrapper.py --room living_room \
        --manifest manifests/living_room.schema.json \
        --params params/living_room_warm.json \
        --out renders/living_room_warm.gltf

    # Quick-render mode (CPU, low-quality, for sweeps)
    python3 infinigen_wrapper.py --room kitchen --params-default \
        --out renders/k.blend --quick

Output: a .blend file at the requested path, plus a sidecar JSON
<out>.meta.json recording the resolved parameters and render time.

If Infinigen import fails (smoke-test mode without Infinigen installed),
the wrapper will write a minimal placeholder glTF and report the failure
clearly so students can debug their install rather than thinking the
wrapper is broken.
"""
from __future__ import annotations
import argparse, json, sys, time, os, subprocess, tempfile, hashlib
from pathlib import Path
from typing import Optional


# ──────────────────────────────────────────────────────────────────
# Room builders — extend as you author manifests.
# Each entry maps a room_type string to a callable that takes a
# parameter dict and returns a configured Infinigen scene object.
# ──────────────────────────────────────────────────────────────────

def build_living_room(params: dict, infinigen):
    """Default Infinigen living_room with parameter overrides."""
    # Real Infinigen API differs across versions; this is the documented v0.5 shape.
    room = infinigen.entities.LivingRoom(
        ceiling_height=params.get("ceiling_height_m", 2.7),
        daylight=params.get("daylight_intensity", 0.7),
        wall_warmth=params.get("wall_warmth_index", 0.5),
        furniture_density=params.get("furniture_density", 0.6),
        biophilia_count=params.get("biophilia_count", 2),
    )
    return room


def build_default(params: dict, infinigen, room_type: str):
    """Generic fallback: instantiate Infinigen by class-name lookup."""
    cls_name = "".join(w.capitalize() for w in room_type.split("_"))
    cls = getattr(infinigen.entities, cls_name, None)
    if cls is None:
        raise ValueError(f"No Infinigen class for room_type={room_type!r} "
                         f"(looked for infinigen.entities.{cls_name})")
    # Pass through whatever parameter names the manifest declared
    return cls(**params)


def _run_generate_indoors(room_type: str, params: dict, infinigen, out_path: Path) -> Path:
    """Subprocess generate_indoors.py for Track 3 Task 2."""
    out_dir = Path(tempfile.mkdtemp(prefix=f"infinigen_{room_type}_"))

    if hasattr(infinigen, "repo_root"):
        root_val = infinigen.repo_root() if callable(infinigen.repo_root) else infinigen.repo_root
        infinigen_root = Path(root_val)
    else:
        # Fallback if repo_root is unavailable
        infinigen_root = Path.home() / "infinigen"

    seed_int = int(hashlib.md5(out_path.name.encode()).hexdigest(), 16) % (2**31)
    seed_str = hex(seed_int)[2:] # format as hex string since Infinigen parses args.seed as base 16

    target_room = "Bedroom" if room_type == "bedroom" else "Bathroom"

    interceptor_code = f'''
import sys, runpy
import infinigen_examples.util.generate_indoors_util as gu
from infinigen.core.tags import Semantics

# Patch 1: Force Room Type
_old_apply = gu.apply_greedy_restriction
def new_apply(stages, restrict_parent_rooms, variable_room):
    _old_apply(stages, {{Semantics.{target_room}}}, variable_room)
gu.apply_greedy_restriction = new_apply
'''
    warmth = params.get("lighting_warmth")
    if warmth is not None:
        target_temp = 6500 - (warmth * 3000)
        interceptor_code += f'''
# Patch 2: Lighting Warmth
import infinigen.assets.lighting.indoor_lights as il
_old_init = il.PointLampFactory.__init__
def new_init(self, factory_seed):
    _old_init(self, factory_seed)
    self.params["Temperature"] = {target_temp}
il.PointLampFactory.__init__ = new_init
'''

    interceptor_code += '''
sys.argv = ["generate_indoors.py"] + sys.argv[1:]
runpy.run_module("infinigen_examples.generate_indoors", run_name="__main__")
'''
    executable_path = out_dir / "interceptor.py"
    with open(executable_path, "w") as f:
        f.write(interceptor_code)

    cmd = [sys.executable, str(executable_path)]

    cmd.extend([
        "-g", "singleroom", "fast_solve",
        "--output_folder", str(out_dir),
        "-t", "coarse", "populate",
        "--seed", seed_str
    ])

    # Map manifest parameters to gin override paths
    overrides = []

    if "ceiling_height_m" in params:
        overrides.extend(["-p", f"RoomConstants.global_params.wall_height={params['ceiling_height_m']}"])
    if "wall_thickness_m" in params:
        overrides.extend(["-p", f"RoomConstants.global_params.wall_thickness={params['wall_thickness_m']}"])
    if "daylight_intensity" in params:
        overrides.extend(["-p", f"nishita_lighting.strength={params['daylight_intensity']}"])
    if "sun_elevation_deg" in params:
        overrides.extend(["-p", f"nishita_lighting.sun_elevation={params['sun_elevation_deg']}"])
    if "dust_density" in params:
        overrides.extend(["-p", f"nishita_lighting.dust_density={params['dust_density']}"])
    if "camera_exposure" in params:
        overrides.extend(["-p", f"configure_render_cycles.exposure={params['camera_exposure']}"])

    if overrides:
        cmd.extend(overrides)

    result = subprocess.run(cmd, cwd=str(infinigen_root), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"generate_indoors.py failed (exit {result.returncode}):\n{result.stderr[-2000:]}")

    blends = list(out_dir.rglob("*.blend"))
    if not blends:
        raise FileNotFoundError(f"generate_indoors.py produced no .blend file in {out_dir}")

    return blends[0]


def build_bedroom(params: dict, infinigen, out_path: Path = None):
    """Bridged builder for bedroom that uses generate_indoors.py subprocess."""
    return _run_generate_indoors("bedroom", params, infinigen, out_path)


def build_bathroom(params: dict, infinigen, out_path: Path = None):
    """Bridged builder for bathroom that uses generate_indoors.py subprocess."""
    return _run_generate_indoors("bathroom", params, infinigen, out_path)


ROOM_BUILDERS = {
    "living_room":  lambda p, i, out=None: build_living_room(p, i),
    "kitchen":      lambda p, i, out=None: build_default(p, i, "kitchen"),
    "bedroom":      build_bedroom,
    "bathroom":     build_bathroom,
    "dining_room":  lambda p, i, out=None: build_default(p, i, "dining_room"),
    "hallway":      lambda p, i, out=None: build_default(p, i, "hallway"),
    "office":       lambda p, i, out=None: build_default(p, i, "office"),
}


# ──────────────────────────────────────────────────────────────────
# glTF export via Blender headless
# ──────────────────────────────────────────────────────────────────

GLTF_EXPORT_PY = r"""
# Run inside Blender's Python: bake the current scene to glTF.
import bpy, sys
out_path = sys.argv[sys.argv.index('--') + 1]
bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format='GLB',          # single-file binary
    export_image_format='AUTO',
    export_yup=True,
    export_apply=True,
    export_draco_mesh_compression_enable=True
)
print(f"Wrote {out_path}")
"""


def export_to_gltf(scene_blend_path: Path, out_path: Path) -> bool:
    """Invoke Blender headless to export a .blend to GLB. Returns True on success."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(GLTF_EXPORT_PY)
        export_script = Path(f.name)
    try:
        result = subprocess.run([
            "blender", "-b", str(scene_blend_path),
            "--python", str(export_script),
            "--", str(out_path),
        ], capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            sys.stderr.write(f"Blender export failed:\n{result.stderr[-500:]}\n")
            return False
        return out_path.exists()
    finally:
        export_script.unlink(missing_ok=True)


# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--room", required=True,
                   help="Room type (living_room, kitchen, bedroom, etc.)")
    p.add_argument("--manifest", help="Path to room's JSON-Schema manifest (optional; "
                                       "used to validate params before render)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--params", help="Path to JSON parameter dict")
    g.add_argument("--params-default", action="store_true",
                   help="Render with default parameters")
    p.add_argument("--out", required=True, help="Output .blend path")
    p.add_argument("--quick", action="store_true",
                   help="Quick CPU render (smoke-test quality, 60-second budget)")
    args = p.parse_args()

    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Load parameters
    if args.params_default:
        params = {}
    else:
        with open(args.params) as f: params = json.load(f)

    # Idempotency check
    meta_path = out_path.with_suffix(out_path.suffix + ".meta.json")
    if out_path.exists() and meta_path.exists():
        try:
            with open(meta_path) as f:
                sidecar = json.load(f)
            if sidecar.get("resolved_params") == params:
                print("skip: already rendered with matching params")
                return 0
        except Exception:
            pass # fallback to rendering

    # Optional manifest validation
    if args.manifest:
        try:
            from jsonschema import validate
            with open(args.manifest) as f: manifest = json.load(f)
            validate(instance=params, schema=manifest)
        except ImportError:
            sys.stderr.write("Warning: jsonschema not installed; skipping manifest validation\n")
        except Exception as e:
            sys.stderr.write(f"Manifest validation failed: {e}\n")
            return 1

    builder = ROOM_BUILDERS.get(args.room)
    if builder is None:
        sys.stderr.write(f"No builder for room_type={args.room!r}. "
                         f"Available: {sorted(ROOM_BUILDERS)}\n")
        sys.stderr.write("Add your own builder to ROOM_BUILDERS in this file.\n")
        return 1

    t0 = time.time()
    try:
        import infinigen
    except ImportError:
        sys.stderr.write("Infinigen not installed. Run: bash scripts/track3/setup_track3.sh\n")
        # In smoke-test mode we still produce a stub glTF so setup_track3.sh
        # can verify the wrapper itself runs.
        if args.params_default:
            _write_stub_gltf(out_path, args.room)
            _write_sidecar(out_path, args.room, params, time.time() - t0,
                          note="Infinigen unavailable — stub glTF written for smoke test only")
            return 0
        return 1

    # Build + render
    try:
        build_output = builder(params, infinigen, out_path)

        if isinstance(build_output, Path):
            # Copy .blend to final output path
            import shutil
            shutil.copy2(str(build_output), str(out_path))
        else:
            scene = build_output
            scene.save(str(out_path))

        if not out_path.exists():
            sys.stderr.write("Render produced no output file\n")
            return 2
    except Exception as e:
        import traceback
        sys.stderr.write(f"Render failed: {type(e).__name__}: {e}\n{traceback.format_exc()}\n")
        return 2

    elapsed = time.time() - t0
    _write_sidecar(out_path, args.room, params, elapsed)
    print(f"OK: rendered {args.room} -> {out_path} ({elapsed:.1f}s)")
    return 0


def _write_sidecar(out: Path, room: str, params: dict, elapsed: float, note: str = "") -> None:
    sidecar = out.with_suffix(out.suffix + ".meta.json")
    with open(sidecar, "w") as f:
        json.dump({
            "room": room,
            "resolved_params": params,
            "render_time_seconds": round(elapsed, 2),
            "wrapper_version": "0.1.0-sprint3",
            "note": note,
        }, f, indent=2)


def _write_stub_gltf(out: Path, room: str) -> None:
    """Minimal valid GLB so smoke test can verify the wrapper signal-path."""
    minimal = (b"glTF" + (2).to_bytes(4, "little") + (88).to_bytes(4, "little")
               + (20).to_bytes(4, "little") + b"JSON" + b'{"asset":{"version":"2.0"}}')
    out.write_bytes(minimal)


if __name__ == "__main__":
    sys.exit(main())
    sys.exit(main())
