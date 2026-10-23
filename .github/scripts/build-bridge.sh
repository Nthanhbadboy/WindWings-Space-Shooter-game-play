#!/usr/bin/env bash
# build-bridge.sh — compile RamusBridge for every loader, against real loader DLLs.
#
#   build-bridge.sh --out dist
#
# Exit code is the number of failed targets: the workflow job goes red if any
# compile fails. No target is ever reported as success on a skipped build.
set -euo pipefail

OUT="dist"
REFS=".ci/refs"
while [ $# -gt 0 ]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    --refs) REFS="$2"; shift 2 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

PROJ="runtime-probe/RamusBridge.csproj"
mkdir -p "$OUT"
declare -a PASSED=() FAILED=()

log()  { printf '[build] %s\n' "$*"; }
ok()   { PASSED+=("$1"); log "PASS  $1"; }
bad()  { FAILED+=("$1"); log "FAIL  $1"; }

# Flatten every DLL from an extracted archive into one folder, so the csproj can
# reference a single directory and never see the same assembly twice.
flatten() {  # flatten <src-dir> <dst-dir>
  local src="$1" dst="$2"
  mkdir -p "$dst"
  find "$src" -type f -name '*.dll' -exec cp -n {} "$dst/" \; 2>/dev/null || true
  find "$dst" -maxdepth 1 -name '*.dll' | wc -l
}

build() {  # build <label> <out-subdir> <extra msbuild args...>
  local label="$1" sub="$2"; shift 2
  rm -rf "runtime-probe/obj" "runtime-probe/bin"
  if dotnet build "$PROJ" -c Release -v minimal -nologo \
       "-p:OutDir=$PWD/$OUT/$sub/" "$@" 2>&1 | sed 's/^/    /'; then
    if ls "$OUT/$sub"/*.dll >/dev/null 2>&1; then ok "$label"; else bad "$label (no dll produced)"; fi
  else
    bad "$label"
  fi
}

# ─────────────────────────────────────────────────────────────── 1. core (stubs)
log "core: syntax/type check against BuildCheck/UnityStubs.cs"
build "core (netstandard2.1, Unity stubs)" core \
  -p:Loader=Core -p:StubUnity=true -p:TargetFramework=netstandard2.1

# ─────────────────────────────────────────────────────────────── 2. BepInEx 6
BEP6="$REFS/bep6"
if [ -d "$BEP6" ] && [ "$(flatten "$BEP6" "$REFS/flat-bep6")" -gt 0 ]; then
  log "BepInEx 6 IL2CPP: $(ls "$REFS/flat-bep6" | wc -l) reference assemblies"
  build "BepInEx 6 IL2CPP (net6.0)" bepinex6 \
    -p:Loader=BepInEx6 -p:StubUnity=true -p:TargetFramework=net6.0 \
    -p:RefsDir="$PWD/$REFS/flat-bep6"
else
  bad "BepInEx 6 IL2CPP (reference zip missing)"
fi

# ─────────────────────────────────────────────────────────────── 3. MelonLoader
MELON="$REFS/melon"
if [ -d "$MELON" ] && [ "$(flatten "$MELON" "$REFS/flat-melon")" -gt 0 ]; then
  log "MelonLoader: $(ls "$REFS/flat-melon" | wc -l) reference assemblies"
  build "MelonLoader (net6.0)" melon \
    -p:Loader=MelonLoader -p:StubUnity=true -p:TargetFramework=net6.0 \
    -p:RefsDir="$PWD/$REFS/flat-melon"
else
  bad "MelonLoader (reference zip missing)"
fi

# ─────────────────────────────────────────────────────────────── 4. BepInEx 5
BEP5="$REFS/bep5"
if [ -d "$BEP5" ] && [ "$(flatten "$BEP5" "$REFS/flat-bep5")" -gt 0 ]; then
  log "BepInEx 5: $(ls "$REFS/flat-bep5" | wc -l) reference assemblies"
  build "BepInEx 5 (netstandard2.1)" bepinex5 \
    -p:Loader=BepInEx5 -p:StubUnity=true -p:TargetFramework=netstandard2.1 \
    -p:RefsDir="$PWD/$REFS/flat-bep5"
else
  bad "BepInEx 5 (reference zip missing)"
fi

# ─────────────────────────────────────────────────────────────── report
echo
echo "──────────────────────────────────────"
printf 'passed: %d\n' "${#PASSED[@]}"
for p in "${PASSED[@]:-}"; do [ -n "$p" ] && printf '  ✓ %s\n' "$p"; done
printf 'failed: %d\n' "${#FAILED[@]}"
for f in "${FAILED[@]:-}"; do [ -n "$f" ] && printf '  ✗ %s\n' "$f"; done
echo "──────────────────────────────────────"

if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  {
    echo "## Bridge build matrix"
    echo
    echo "| target | result |"
    echo "| --- | --- |"
    for p in "${PASSED[@]:-}"; do [ -n "$p" ] && echo "| $p | ✅ |"; done
    for f in "${FAILED[@]:-}"; do [ -n "$f" ] && echo "| $f | ❌ |"; done
  } >> "$GITHUB_STEP_SUMMARY"
fi

[ "${#FAILED[@]}" -eq 0 ]
