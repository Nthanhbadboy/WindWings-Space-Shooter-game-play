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

# Flatten the loader assemblies into one folder, so the csproj can reference a
# single directory and never see the same assembly twice.
#
# The BepInEx IL2CPP zip also ships a private .NET runtime under dotnet/. Copying
# mscorlib/System.* out of it makes the compiler resolve predefined types from
# the 6.0 runtime instead of the targeting pack — CS0518 "System.Object is not
# defined", 291 errors. Those are dropped here.
flatten() {  # flatten <src-dir> <dst-dir>
  local src="$1" dst="$2"
  mkdir -p "$dst"
  find "$src" -type f -name '*.dll' \
       ! -path '*/dotnet/*' \
       ! -name 'mscorlib.dll' \
       ! -name 'netstandard.dll' \
       ! -name 'System.*.dll' \
       ! -name 'Microsoft.*.dll' \
       ! -name 'WindowsBase.dll' \
       ! -name 'Presentation*.dll' \
       -exec cp -n {} "$dst/" \; 2>/dev/null || true
  find "$dst" -maxdepth 1 -name '*.dll' | wc -l
}

# The Mono adapter inherits from MonoBehaviour, so the compiler needs a type
# identity for `UnityEngine, Version=0.0.0.0`. Build one stub assembly once and
# reference it; never ship it.
STUB_DIR="$PWD/$REFS/unity-stub"
build_unity_stub() {
  if [ -f "$STUB_DIR/UnityEngine.dll" ]; then return 0; fi
  log "building UnityEngine stub (identity 0.0.0.0)"
  rm -rf runtime-probe/BuildCheck/obj runtime-probe/BuildCheck/bin
  dotnet build runtime-probe/BuildCheck/UnityStubs.csproj -c Release -v minimal -nologo \
    "-p:OutDir=$STUB_DIR/" 2>&1 | sed 's/^/    /' || return 1
  [ -f "$STUB_DIR/UnityEngine.dll" ]
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

# ─────────────────────────────────────────────────────────────── 0. Unity stub
if ! build_unity_stub; then
  bad "UnityEngine stub assembly (BuildCheck)"
fi

# ─────────────────────────────────────────────────────────────── 1. core (stubs)
log "core: syntax/type check against BuildCheck/UnityStubs.cs"
build "core (netstandard2.1, Unity stubs)" core \
  -p:Loader=Core -p:StubUnity=true -p:UnityStubDir="$STUB_DIR" -p:Tfm=netstandard2.1

# ─────────────────────────────────────────────────────────────── 2. BepInEx 6
BEP6="$REFS/bep6"
if [ -d "$BEP6" ] && [ "$(flatten "$BEP6" "$REFS/flat-bep6")" -gt 0 ]; then
  log "BepInEx 6 IL2CPP: $(ls "$REFS/flat-bep6" | wc -l) reference assemblies"
  build "BepInEx 6 IL2CPP (net6.0)" bepinex6 \
    -p:Loader=BepInEx6 -p:StubUnity=true -p:UnityStubDir="$STUB_DIR" -p:Tfm=net6.0 \
    -p:RefsDir="$PWD/$REFS/flat-bep6"
else
  bad "BepInEx 6 IL2CPP (reference zip missing)"
fi

# ─────────────────────────────────────────── 2b. BepInEx 6 on-device (phone)
# Reference the ACTUAL core + generated interop assemblies pulled from the
# device (binding-exact). StubUnity off -- UnityEngine identity comes from the
# interop UnityEngine.CoreModule proxy.
BEP6P="$REFS/bep6-refs-phone/bep6-core-phone"
BEPI="$REFS/bep6-refs-phone/bep6-interop"
if [ -d "$BEP6P" ] && [ -d "$BEPI" ] && [ "$(ls "$BEPI"/*.dll 2>/dev/null | wc -l)" -gt 0 ]; then
  rm -rf "$REFS/flat-bep6-phone"; mkdir -p "$REFS/flat-bep6-phone"
  # core first, interop after (cp -n keeps the core identity on clashes).
  find "$BEP6P" "$BEPI" -maxdepth 2 -type f -name '*.dll' -exec cp -n {} "$REFS/flat-bep6-phone/" \; 2>/dev/null || true
  log "BepInEx 6 phone refs: $(ls "$REFS/flat-bep6-phone" | wc -l) assemblies"
  build "BepInEx 6 phone-interop (net6.0)" bepinex6-phone \
    -p:Loader=BepInEx6 -p:StubUnity=false -p:Tfm=net6.0 \
    -p:RefsDir="$PWD/$REFS/flat-bep6-phone"
else
  bad "BepInEx 6 phone refs missing"
fi

# ─────────────────────────────────────────────────────────────── 3. MelonLoader
MELON="$REFS/melon"
if [ -d "$MELON" ] && [ "$(flatten "$MELON" "$REFS/flat-melon")" -gt 0 ]; then
  log "MelonLoader: $(ls "$REFS/flat-melon" | wc -l) reference assemblies"
  build "MelonLoader (net6.0)" melon \
    -p:Loader=MelonLoader -p:StubUnity=true -p:UnityStubDir="$STUB_DIR" -p:Tfm=net6.0 \
    -p:RefsDir="$PWD/$REFS/flat-melon"
else
  bad "MelonLoader (reference zip missing)"
fi

# ─────────────────────────────────────────────────────────────── 4. BepInEx 5
BEP5="$REFS/bep5"
if [ -d "$BEP5" ] && [ "$(flatten "$BEP5" "$REFS/flat-bep5")" -gt 0 ]; then
  log "BepInEx 5: $(ls "$REFS/flat-bep5" | wc -l) reference assemblies"
  build "BepInEx 5 (netstandard2.1)" bepinex5 \
    -p:Loader=BepInEx5 -p:StubUnity=true -p:UnityStubDir="$STUB_DIR" -p:Tfm=netstandard2.1 \
    -p:RefsDir="$PWD/$REFS/flat-bep5"
else
  bad "BepInEx 5 (reference zip missing)"
fi

# ─────────────────────────────────────────────────── 5. headless self-test (run)
# Compiles the same RamusBridge.cs against the stub and drives the HTTP server
# over a real socket. Needs the stub, so it is skipped if the stub failed.
if [ -f "$STUB_DIR/UnityEngine.dll" ]; then
  log "self-test: boot bridge on 127.0.0.1:18080 and call every endpoint"
  rm -rf runtime-probe/SelfTest/obj runtime-probe/SelfTest/bin
  # tee keeps the raw output (including the RAMUSB| mirror line) for the
  # contract test that follows; sed keeps the log readable.
  if dotnet run --project runtime-probe/SelfTest/RamusBridge.SelfTest.csproj \
       -c Release -v quiet "-p:UnityStubDir=$STUB_DIR" 2>&1 \
       | tee "$OUT/selftest.log" | sed 's/^/    /'; then
    ok "self-test (HTTP + JSON + main-thread queue)"
  else
    bad "self-test (HTTP + JSON + main-thread queue)"
  fi
else
  bad "self-test (UnityEngine stub missing)"
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
