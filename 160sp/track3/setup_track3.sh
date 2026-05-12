#!/usr/bin/env bash
# setup_track3.sh — one-command bootstrap for COGS 160 Track 3 (VR Studio).
#
# Installs Blender 4.x (if missing), creates a Python venv, installs Infinigen
# Indoors, and runs a smoke test that renders one default living_room and
# exports it to glTF. Reports OK or specific actionable errors.
#
# Tested on macOS (Homebrew) and Ubuntu 22.04. Other Linux distros will need
# manual Blender install; the script will tell you.
#
# Usage:  bash scripts/track3/setup_track3.sh
#
# Exit codes:
#   0 = ready to work
#   1 = install failed
#   2 = smoke test failed
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TRACK3_DIR="$REPO_ROOT/track3"
VENV_DIR="$TRACK3_DIR/.venv"
INFINIGEN_DIR="$TRACK3_DIR/infinigen_indoors"
SMOKE_DIR="$TRACK3_DIR/smoke"

cyan()  { printf "\033[96m%s\033[0m\n" "$*"; }
amber() { printf "\033[93m%s\033[0m\n" "$*"; }
green() { printf "\033[92m%s\033[0m\n" "$*"; }
red()   { printf "\033[91m%s\033[0m\n" "$*" >&2; }

cyan "==> Track 3 setup starting (REPO_ROOT=$REPO_ROOT)"

mkdir -p "$TRACK3_DIR" "$SMOKE_DIR"

# ─── Step 1: Blender ────────────────────────────────────────────────
cyan "==> Step 1/5: Verify Blender 4.x"
if ! command -v blender >/dev/null 2>&1; then
  amber "Blender not on PATH."
  case "$(uname -s)" in
    Darwin)
      if command -v brew >/dev/null 2>&1; then
        cyan "==> Installing Blender via Homebrew (this can take ~5 min)..."
        brew install --cask blender
      else
        red "Homebrew not found. Install Blender manually: https://www.blender.org/download/"
        exit 1
      fi ;;
    Linux)
      red "Linux Blender install must be manual. Recommended: snap install blender --classic"
      red "or download from https://www.blender.org/download/"
      exit 1 ;;
    *)
      red "Unsupported OS: $(uname -s). Install Blender manually." ; exit 1 ;;
  esac
fi
BLENDER_VERSION="$(blender --version 2>&1 | head -1 | awk '{print $2}')"
green "Blender $BLENDER_VERSION OK"
case "$BLENDER_VERSION" in
  4.*) ;;
  *) amber "Warning: Blender $BLENDER_VERSION; Infinigen Indoors prefers 4.x. Continuing." ;;
esac

# ─── Step 2: Python venv ────────────────────────────────────────────
cyan "==> Step 2/5: Python venv at $VENV_DIR"
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"
python3 -m pip install --quiet --upgrade pip
green "Python venv ready ($(python3 --version))"

# ─── Step 3: Infinigen ──────────────────────────────────────────────
cyan "==> Step 3/5: Infinigen Indoors at $INFINIGEN_DIR"
if [ ! -d "$INFINIGEN_DIR/.git" ]; then
  cyan "==> Cloning Infinigen (https://github.com/princeton-vl/infinigen)..."
  git clone --depth 1 https://github.com/princeton-vl/infinigen.git "$INFINIGEN_DIR" || {
    red "Clone failed. Check network / GitHub access. You can clone manually then re-run."
    exit 1
  }
fi
cd "$INFINIGEN_DIR"
cyan "==> pip install -e . (this can take ~3 min)..."
pip install --quiet -e . || {
  red "Infinigen install failed. Common causes:"
  red "  - missing system libs (libgl, libglu) on Linux: apt-get install libgl1 libglu1-mesa"
  red "  - Python version mismatch (Infinigen needs Python 3.10+)"
  exit 1
}
green "Infinigen installed"
cd "$REPO_ROOT"

# ─── Step 4: Smoke test ─────────────────────────────────────────────
cyan "==> Step 4/5: Smoke test — render default living_room"
SMOKE_LOG="$SMOKE_DIR/smoke_$(date +%Y%m%d_%H%M%S).log"
SMOKE_OUT="$SMOKE_DIR/living_room_smoke.gltf"
if python3 "$REPO_ROOT/scripts/track3/infinigen_wrapper.py" \
    --room living_room \
    --params-default \
    --out "$SMOKE_OUT" \
    --quick > "$SMOKE_LOG" 2>&1; then
  if [ -f "$SMOKE_OUT" ]; then
    SIZE_KB=$(($(stat -f%z "$SMOKE_OUT" 2>/dev/null || stat -c%s "$SMOKE_OUT") / 1024))
    green "Smoke test OK — $SMOKE_OUT (${SIZE_KB} KB)"
  else
    red "Smoke test ran but produced no glTF. Check log: $SMOKE_LOG"
    exit 2
  fi
else
  red "Smoke test failed. See log: $SMOKE_LOG"
  red "Common causes:"
  red "  - Blender Python and Infinigen Python incompatible: try Blender 4.0.x specifically"
  red "  - GPU not available: use --quick flag (CPU fallback) — already tried here"
  red "  - infinigen_wrapper.py missing (re-pull repo)"
  exit 2
fi

# ─── Step 5: Done ───────────────────────────────────────────────────
cyan "==> Step 5/5: Done"
green "Track 3 environment is ready."
green ""
green "Next steps (per t3_task1.html Phase 2):"
green "  1. Activate the venv:    source $VENV_DIR/bin/activate"
green "  2. Survey coverage:      python3 scripts/track3/extract_infinigen_params.py --all"
green "  3. Author your manifest: copy 3d_rooms/_scaffold/manifest_template.json to your branch"
green ""
green "If you get stuck, post in #track3-help with the smoke log: $SMOKE_LOG"
