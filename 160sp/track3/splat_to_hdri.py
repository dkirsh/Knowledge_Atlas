#!/usr/bin/env python3
"""splat_to_hdri.py — Track 3 Phase 2.5 splat-augmentation scaffold.

Takes a 3D Gaussian Splatting capture (.ply or .splat format) of a real
exemplar room, extracts the lighting environment as a spherical-harmonic
decomposition, and writes a standard equirectangular .hdr file the
parametric Infinigen renderer applies as image-based lighting (IBL).

Per the Sprint-3 panel addendum on splat augmentation: splats supply
realism layers (lighting, materials) over the parametric Track 3 pipeline.
The parametric room geometry stays editable; the splat-derived HDRI is a
render-time asset, not a replacement for the parameter manifest.

Algorithm (Sprint 5 fills in the real implementation):
    1. Load splat file -> per-Gaussian {position, opacity, SH coefficients}
    2. For each direction on a 2:1 equirect map, accumulate the
       SH-evaluated radiance from Gaussians sampled along that ray
    3. Bake to an HxW float32 RGB buffer (default 1024x512; 256x128 in
       --quick mode)
    4. Save as .hdr (Radiance RGBE format)

Usage:

    # Default-quality bake
    python3 splat_to_hdri.py --splat scans/kitchen.splat \\
        --out 3d_rooms/kitchen/lighting.hdr

    # Quick mode (low-res, faster, lower quality)
    python3 splat_to_hdri.py --splat scans/kitchen.splat \\
        --out 3d_rooms/kitchen/lighting.hdr --quick

Output: a Radiance .hdr file at the requested path, plus a sidecar
JSON <out>.meta.json recording the splat source, extraction time, and
quality flag. If splat libraries (splatviz, nerfstudio, gsplat) are not
installed, writes a stub HDR file (8x4 grayscale gradient) and reports
the missing dependency clearly so students can install and re-run.

Sprint 4 deliverable: this SCAFFOLD (CLI + file I/O + stub mode +
documentation). Sprint 5 implementer fills in the SH-extraction and
HDR-bake steps using libraries like splatviz / nerfstudio / gsplat.
"""
from __future__ import annotations
import argparse, json, struct, sys, time
from pathlib import Path
from typing import Optional


# ──────────────────────────────────────────────────────────────────
# Splat file validation
# ──────────────────────────────────────────────────────────────────

VALID_EXTENSIONS = {".ply", ".splat"}


def validate_splat_file(path: Path) -> tuple[bool, str]:
    """Return (ok, reason). Lightweight format sniff; deep parse is in Sprint 5."""
    if not path.exists():
        return False, f"File not found: {path}"
    if path.suffix.lower() not in VALID_EXTENSIONS:
        return False, f"Unexpected extension {path.suffix!r}; expected one of {sorted(VALID_EXTENSIONS)}"
    if path.stat().st_size < 64:
        return False, f"File too small ({path.stat().st_size} bytes); likely truncated"
    # Sniff the first bytes
    with open(path, "rb") as f:
        head = f.read(16)
    if path.suffix.lower() == ".ply" and not head.startswith(b"ply"):
        return False, "PLY magic 'ply' missing in header"
    # .splat format has no fixed magic; size check is the best we can do here
    return True, "ok"


# ──────────────────────────────────────────────────────────────────
# Real extraction (Sprint 5 fills in)
# ──────────────────────────────────────────────────────────────────

def extract_sh_environment(splat_path: Path, quick: bool) -> Optional["np.ndarray"]:
    """Load splat, extract SH coefficients, bake to equirect HDR buffer.

    Returns a (H, W, 3) float32 RGB array, or None if splat libraries
    are not installed (in which case caller falls back to stub mode).
    """
    try:
        import numpy as np  # noqa: F401
    except ImportError:
        return None
    try:
        # Sprint 5: replace these placeholder imports with the real
        # nerfstudio / splatviz / gsplat loader.
        import nerfstudio  # noqa: F401  # type: ignore
    except ImportError:
        return None

    # ── Sprint 5 implementer fills in below ──────────────────────
    # 1. gaussians = load_splat(splat_path)
    # 2. resolution = (256, 128) if quick else (1024, 512)
    # 3. envmap = bake_sh_to_equirect(gaussians, resolution)
    # 4. return envmap  # (H, W, 3) float32
    # ──────────────────────────────────────────────────────────────
    raise NotImplementedError(
        "Sprint 5 deliverable: SH extraction + equirect bake. "
        "Sprint 4 ships the scaffold; this code path is reached only "
        "when splat libraries ARE installed but the implementation is not."
    )


# ──────────────────────────────────────────────────────────────────
# Stub HDR writer — used when splat libraries are unavailable
# ──────────────────────────────────────────────────────────────────

def write_stub_hdr(out_path: Path, width: int = 8, height: int = 4) -> None:
    """Write a minimal Radiance .hdr file with a grayscale gradient.

    Sufficient for the smoke-test signal-path: students can verify the
    wrapper produces a file at the right location and the sidecar
    metadata reports the missing dependency clearly.
    """
    # Radiance RGBE header
    header = (
        b"#?RADIANCE\n"
        b"# Stub HDR generated by splat_to_hdri.py (splat libs unavailable)\n"
        b"FORMAT=32-bit_rle_rgbe\n"
        b"\n"
        f"-Y {height} +X {width}\n".encode("ascii")
    )
    # Gradient pixels: top row brightest, bottom row dimmest
    pixels = bytearray()
    for y in range(height):
        intensity = int(255 * (1.0 - y / max(height - 1, 1)))
        # RGBE: R, G, B, exponent (128 = 2^0)
        for _ in range(width):
            pixels.extend([intensity, intensity, intensity, 128])
    out_path.write_bytes(header + bytes(pixels))


# ──────────────────────────────────────────────────────────────────
# HDR file writer (real path)
# ──────────────────────────────────────────────────────────────────

def write_hdr(out_path: Path, envmap) -> None:
    """Write an (H, W, 3) float32 array as Radiance .hdr (RGBE encoding).

    Sprint 5 implementer: replace with imageio.imwrite(out_path, envmap,
    format='HDR-FI') once dependencies are available.
    """
    raise NotImplementedError(
        "Sprint 5 deliverable: real RGBE encoder (use imageio or OpenEXR)."
    )


# ──────────────────────────────────────────────────────────────────
# Sidecar metadata
# ──────────────────────────────────────────────────────────────────

def write_sidecar(
    out_path: Path,
    splat_path: Path,
    elapsed: float,
    quick: bool,
    note: str = "",
) -> None:
    sidecar = out_path.with_suffix(out_path.suffix + ".meta.json")
    meta = {
        "tool": "splat_to_hdri.py",
        "tool_version": "0.1.0-sprint4-scaffold",
        "splat_source": str(splat_path),
        "splat_source_size_bytes": splat_path.stat().st_size if splat_path.exists() else None,
        "output": str(out_path),
        "extraction_time_seconds": round(elapsed, 3),
        "quality_flag": "quick" if quick else "default",
        "format": "Radiance HDR (RGBE)",
        "extraction_method": "spherical_harmonics_per_gaussian",
        "note": note,
    }
    sidecar.write_text(json.dumps(meta, indent=2))


# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(
        description="Extract HDRI lighting from a 3D Gaussian Splatting capture.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--splat", required=True, type=Path,
                   help="Input splat file (.ply or .splat)")
    p.add_argument("--out", required=True, type=Path,
                   help="Output .hdr path (e.g., 3d_rooms/kitchen/lighting.hdr)")
    p.add_argument("--quick", action="store_true",
                   help="Low-resolution SH extraction (256x128, faster, lower quality)")
    args = p.parse_args()

    splat_path: Path = args.splat.resolve()
    out_path: Path = args.out.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    ok, reason = validate_splat_file(splat_path)
    if not ok:
        sys.stderr.write(f"\033[91mSplat validation failed: {reason}\033[0m\n")
        return 1

    t0 = time.time()
    envmap = extract_sh_environment(splat_path, quick=args.quick)

    if envmap is None:
        # Stub mode: splat libraries unavailable
        sys.stderr.write(
            "\033[93mSplat libraries not installed (need numpy + nerfstudio / "
            "splatviz / gsplat). Writing stub HDR for smoke-test only.\033[0m\n"
            "\033[96mTo install: pip3 install --break-system-packages numpy nerfstudio\033[0m\n"
        )
        write_stub_hdr(out_path)
        write_sidecar(
            out_path, splat_path, time.time() - t0, args.quick,
            note="Stub HDR (8x4 grayscale gradient); install splat libraries and re-run for real bake.",
        )
        print(f"\033[93mOK (STUB): wrote {out_path}\033[0m")
        return 0

    # Real path
    write_hdr(out_path, envmap)
    write_sidecar(out_path, splat_path, time.time() - t0, args.quick)
    print(f"\033[92mOK: wrote {out_path} ({time.time() - t0:.1f}s)\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
