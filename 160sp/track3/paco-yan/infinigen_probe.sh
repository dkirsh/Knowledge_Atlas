#!/usr/bin/env bash
# infinigen_probe.sh — collect everything Claude needs to verify the
# parameter-source mapping doc.
#
# Run in WSL Ubuntu, with your `infinigen` conda env active:
#     conda activate infinigen
#     bash /mnt/c/Users/user/Documents/Claude/Projects/Cogs\ 160/infinigen_probe.sh
#
# Output lands at the same folder as 'infinigen_probe.out.txt'.
# The exact path is printed at the end.

set -u  # fail on undefined vars but keep going on grep misses

# Where Claude can read the result on Windows side
OUT="/mnt/c/Users/user/Documents/Claude/Projects/Cogs 160/infinigen_probe.out.txt"

# Locate Infinigen package — try multiple strategies
INFINIGEN_PATH="$(python -c 'import infinigen, os; print(os.path.dirname(infinigen.__file__))' 2>/dev/null || echo '')"

# Fallback 1: pip list (might be installed under a slightly different name)
PIP_INFINIGEN="$(pip list 2>/dev/null | grep -i infinigen || echo '')"

# Fallback 2: search common clone locations and $HOME for an infinigen tree
INFINIGEN_CLONES="$(find "$HOME" -maxdepth 4 -type d -name 'infinigen' 2>/dev/null | head -10)"

# Fallback 3: where does Blender's bundled Python find it? (Phase 1 smoke test path)
BLENDER_BIN="$(command -v blender 2>/dev/null || echo '')"

# Locate Knowledge_Atlas root (assumes ~/Knowledge_Atlas; adjust if elsewhere)
KA_ROOT="$HOME/Knowledge_Atlas"

{
  echo "================================================================"
  echo "INFINIGEN PROBE — generated $(date -Iseconds)"
  echo "================================================================"
  echo
  echo "## Environment"
  echo "Python:           $(python --version 2>&1)"
  echo "Conda env:        ${CONDA_DEFAULT_ENV:-<none>}"
  echo "Infinigen path:   ${INFINIGEN_PATH:-<not importable as 'infinigen'>}"
  echo "Knowledge_Atlas:  $KA_ROOT $([ -d "$KA_ROOT" ] && echo '(exists)' || echo '(MISSING)')"
  echo "Infinigen ver:    $(python -c 'import infinigen; print(getattr(infinigen, "__version__", "unknown"))' 2>&1)"
  echo
  echo "## Locator fallbacks"
  echo "pip list match:    ${PIP_INFINIGEN:-<no match>}"
  echo "blender binary:    ${BLENDER_BIN:-<not on PATH>}"
  echo "infinigen dirs found under \$HOME:"
  if [ -n "$INFINIGEN_CLONES" ]; then
    echo "$INFINIGEN_CLONES" | sed 's/^/  /'
  else
    echo "  (none — try widening the search)"
  fi
  echo

  # If the import didn't work, try to derive INFINIGEN_PATH from a clone
  if [ -z "$INFINIGEN_PATH" ] && [ -n "$INFINIGEN_CLONES" ]; then
    # Pick the first one that contains a Python __init__ file
    for CAND in $INFINIGEN_CLONES; do
      if [ -f "$CAND/__init__.py" ]; then
        INFINIGEN_PATH="$CAND"
        echo "(Derived INFINIGEN_PATH from clone: $INFINIGEN_PATH)"
        echo
        break
      fi
    done
  fi

  if [ -z "$INFINIGEN_PATH" ] || [ ! -d "$INFINIGEN_PATH" ]; then
    echo "!! Could not locate Infinigen source. Continuing with Knowledge_Atlas only."
    INFINIGEN_PATH=""
  fi

  if [ -n "$INFINIGEN_PATH" ]; then
    echo "================================================================"
    echo "## Top-level layout of infinigen/"
    echo "================================================================"
    ls -la "$INFINIGEN_PATH" 2>&1
    echo
    echo "## Subdirectories two levels deep:"
    find "$INFINIGEN_PATH" -maxdepth 2 -type d 2>&1 | sort
  fi

  if [ -n "$INFINIGEN_PATH" ]; then
    echo
    echo "================================================================"
    echo "## Factory class search (Kitchen + Dining symbols)"
    echo "================================================================"
    for SYMBOL in \
        "class SingleCabinetFactory" \
        "class KitchenCounter" \
        "class BowlFactory" \
        "class BottleFactory" \
        "class HardwareFactory" \
        "class WindowFactory" \
        "class CeilingLightFactory" \
        "class PointLampFactory" \
        "class DeskLampFactory" \
        "class LargePlantContainerFactory" \
        "class ChairFactory" \
        "class TableFactory" \
        "class SideboardFactory"
    do
      echo
      echo "--- $SYMBOL ---"
      grep -rn "$SYMBOL" "$INFINIGEN_PATH" 2>/dev/null | head -5 \
        || echo "  (not found)"
    done

    echo
    echo "================================================================"
    echo "## Knob / parameter name search"
    echo "================================================================"
    for PATTERN in \
        "ceiling_height" \
        "color_temperature\|kelvin" \
        "sun_strength\|sky_strength" \
        "emission_strength\|light_strength" \
        "wall_material" \
        "floor_material"
    do
      echo
      echo "--- $PATTERN ---"
      grep -rn -E "$PATTERN" "$INFINIGEN_PATH" 2>/dev/null | head -10 \
        || echo "  (not found)"
    done

    echo
    echo "================================================================"
    echo "## Constraint / room shell search"
    echo "================================================================"
    if [ -d "$INFINIGEN_PATH/core/constraints" ]; then
      echo "--- listing of core/constraints/:"
      ls -la "$INFINIGEN_PATH/core/constraints/" 2>&1
      echo
      echo "--- ceiling_height occurrences:"
      grep -rn "ceiling_height" "$INFINIGEN_PATH/core/constraints/" 2>/dev/null | head -10
    else
      echo "core/constraints/ does not exist — searching whole tree:"
      find "$INFINIGEN_PATH" -name "*.py" -exec grep -l "ceiling_height" {} \; 2>/dev/null | head -10
    fi
  else
    echo
    echo "================================================================"
    echo "## Skipping Infinigen-source searches (no path located)"
    echo "================================================================"
    echo "Things to try manually in your shell:"
    echo "  pip list | grep -i infinigen"
    echo "  find / -name 'infinigen' -type d 2>/dev/null | head"
    echo "  echo \$PYTHONPATH"
    echo "  cat ~/.bashrc | grep -i infinigen"
    echo "  ls ~/REPOS/  ~/repos/  ~/code/  ~/projects/  2>/dev/null"
  fi

  echo
  echo "================================================================"
  echo "## Knowledge_Atlas: shipped Track 3 scripts"
  echo "================================================================"
  if [ -d "$KA_ROOT/scripts/track3" ]; then
    echo "--- listing scripts/track3/:"
    ls -la "$KA_ROOT/scripts/track3/" 2>&1
    for FILE in infinigen_wrapper.py validation_gate.py llm_wrapper_starter.py splat_to_hdri.py splat_to_materials.py; do
      echo
      echo "--- HEAD of scripts/track3/$FILE (first 80 lines):"
      head -80 "$KA_ROOT/scripts/track3/$FILE" 2>/dev/null \
        || echo "  (file not present)"
    done
  else
    echo "scripts/track3/ not found at $KA_ROOT/scripts/track3"
    echo "Searching for it under \$HOME:"
    find "$HOME" -path "*Knowledge_Atlas*scripts/track3*" -type d 2>/dev/null | head -5
  fi

  echo
  echo "================================================================"
  echo "## Knowledge_Atlas: scaffolds + presets"
  echo "================================================================"
  if [ -d "$KA_ROOT/3d_rooms" ]; then
    find "$KA_ROOT/3d_rooms" -maxdepth 3 -type f 2>/dev/null | head -30
  else
    echo "3d_rooms/ not found."
  fi

  echo
  echo "================================================================"
  echo "## Done"
  echo "================================================================"
  echo "Output written to: $OUT"
} > "$OUT" 2>&1

echo "Probe complete. Output at:"
echo "  WSL side:     $OUT"
echo "  Windows side: C:\\Users\\user\\Documents\\Claude\\Projects\\Cogs 160\\infinigen_probe.out.txt"
echo
echo "Tell Claude 'probe ready' and Claude will read it."
