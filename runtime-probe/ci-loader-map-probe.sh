#!/usr/bin/env bash
# One bounded, authorized CI attempt at Map_Get_Datas via a separate FusionCore
# app. The source XAPK is installed from its original inner APK bytes; it is
# never rewritten. No session is created without RAMUS_API_KEY because trial
# mode has no adb tunnel and cannot issue /statics.
set -euo pipefail

OUT="${PROBE_OUT:-reports/runtime-loader-probe}"
BUNDLE="${LOADER_BUNDLE:-$RUNNER_TEMP/runtime-loader-vehicle}"
APK_TAG="${APK_TAG:-windwings-apk-1.3.118}"
APK_ASSET="${APK_ASSET:-windwings.xapk}"
APK_SHA256="${APK_SHA256:-f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e}"
PACKAGE="${RAMUS_PACKAGE:-com.Wind.wings.Space.Shooter}"
LOADER_PACKAGE="dev.allofus.fusioncore"
RAMUS_CLI="ramus-cli@0.1.17"
SESSION=""
mkdir -p "$OUT"

block() {
  local status="$1" step="$2" reason="$3"
  local started=false source_sha_observed
  [ -n "$SESSION" ] && started=true
  source_sha_observed="$(jq -r '.source_xapk.source.sha256 // "NOT_DOWNLOADED"' "$BUNDLE/provenance.json" 2>/dev/null || echo NOT_DOWNLOADED)"
  jq -n --arg status "$status" --arg step "$step" --arg reason "$reason" \
    --arg source_sha256 "$source_sha_observed" --arg source_sha256_expected "$APK_SHA256" \
    --arg session_id "$SESSION" --argjson session_started "$started" \
    --arg loader_sha256 "$(jq -r '.vehicle.sha256 // "NOT_BUILT"' "$BUNDLE/provenance.json" 2>/dev/null || echo NOT_BUILT)" \
    --arg bridge_sha256 "$(jq -r '.bridge.sha256 // "NOT_BUILT"' "$BUNDLE/provenance.json" 2>/dev/null || echo NOT_BUILT)" \
    '{schema:"windwings-runtime-map-probe/v1",status:$status,failed_step:$step,reason:$reason,
      session_started:$session_started,session_id:(if $session_started then $session_id else null end),
      source_xapk_modified:false,source_xapk_sha256:$source_sha256,source_xapk_sha256_expected:$source_sha256_expected,
      loader_sha256:$loader_sha256,bridge_sha256:$bridge_sha256,
      request:{type:"Map_Get_Datas",max:200,arr:256,depth:2},runtime_readback:null,
      map_values:null,second_device_status:"NOT_REACHED",live_dps_status:"NOT_REACHED"}' \
    > "$OUT/map-step.json"
  {
    echo "# #28 runtime probe — Map step blocked"
    echo
    echo "- **Status:** \`$status\`"
    echo "- **Failed step:** \`$step\`"
    echo "- **Blocker:** $reason"
    echo "- **Session started:** $([ -n "$SESSION" ] && echo yes || echo no)"
    [ -z "$SESSION" ] || echo "- **Session ID:** \`$SESSION\`"
    echo "- **Original XAPK modified:** no"
    echo "- **Original XAPK SHA-256 (verified by build):** \`$source_sha_observed\` (expected \`$APK_SHA256\`)"
    echo "- **Loader SHA-256:** \`$(jq -r '.vehicle.sha256 // "NOT_BUILT"' "$BUNDLE/provenance.json" 2>/dev/null || echo NOT_BUILT)\`"
    echo "- **Bridge SHA-256:** \`$(jq -r '.bridge.sha256 // "NOT_BUILT"' "$BUNDLE/provenance.json" 2>/dev/null || echo NOT_BUILT)\`"
    echo "- **Requested call:** \`/statics?type=Map_Get_Datas&max=200&arr=256&depth=2\`"
    echo "- **Map values:** not observed; no readback is inferred."
    echo "- **Step 2 (second device):** not reached."
    echo "- **Step 3 (live DPS):** not reached."
  } > "$OUT/map-step-report.md"
  echo "::notice::#28 stopped at $step: $reason"
  exit 0
}

finish_session() {
  if [ -n "$SESSION" ]; then
    npx --yes "$RAMUS_CLI" session end --session "$SESSION" > "$OUT/session-end.txt" 2>&1 || true
    SESSION=""
  fi
}
trap finish_session EXIT

[ -s "$BUNDLE/fusionApp-debug.apk" ] || block "BLOCKED_LOADER_ARTIFACT" "loader-build" "FusionCore APK artifact is missing."
[ -s "$BUNDLE/RamusBridge.dll" ] || block "BLOCKED_BRIDGE_ARTIFACT" "bridge-build" "Target BepInEx6 phone bridge DLL is missing."
[ -s "$BUNDLE/provenance.json" ] || block "BLOCKED_PROVENANCE" "loader-provenance" "Loader provenance receipt is missing."

if [ "${GITHUB_EVENT_NAME:-}" = "pull_request" ]; then
  commit_subject="$(git log -1 --format=%s)"
  case "$commit_subject" in
    *'[runtime-probe-28-once]'*) ;;
    *) block "SKIPPED_NO_ONE_SHOT_TRIGGER" "explicit-run-gate" \
         "PR builds do not create sessions by default. The head commit must explicitly include [runtime-probe-28-once]; no session was created." ;;
  esac
else
  [ "${RUN_MAP_PROBE:-false}" = "true" ] || block "SKIPPED_NO_ONE_SHOT_TRIGGER" "explicit-run-gate" \
    "workflow_dispatch run_map_probe was not true; no session was created."
fi

if [ -z "${RAMUS_API_KEY:-}" ]; then
  block "BLOCKED_NO_ADB_CREDENTIAL" "pre-session-transport-gate" \
    "RAMUS_API_KEY is not configured for this workflow. Anonymous trial has no adb tunnel, so it cannot install the original split XAPK beside the separate loader or call /statics; no session was created. Do not paste a key in chat."
fi

# Start exactly one session. No automatic retries: the step report records the
# actual CLI response if the loader APK cannot be installed on the selected VM.
set +e
npx --yes "$RAMUS_CLI" session start --apk "$BUNDLE/fusionApp-debug.apk" --wait --timeout 240 \
  > "$OUT/session-start.stdout" 2> "$OUT/session-start.stderr"
start_rc=$?
set -e
if [ "$start_rc" -ne 0 ]; then
  block "BLOCKED_SESSION_START" "loader-session-start" \
    "Ramus session start returned exit $start_rc for the pinned FusionCore loader APK. See session-start.stdout/stderr; no retry was made."
fi
SESSION="$(python3 - "$OUT/session-start.stdout" <<'PY'
import json,sys
try:
 d=json.load(open(sys.argv[1]))
 s=d.get('session')
 if isinstance(s,dict): s=s.get('id') or s.get('sessionId')
 print(s or d.get('sessionId') or d.get('id') or '')
except Exception: print('')
PY
)"
[ -n "$SESSION" ] || block "BLOCKED_SESSION_ID" "loader-session-start" "Ramus reported success but no session ID could be read; no second start was attempted."
printf '%s\n' "$SESSION" > "$OUT/session-id.txt"

if ! command -v adb >/dev/null 2>&1; then
  sudo apt-get update -qq && sudo apt-get install -y -qq android-tools-adb
fi
set +e
npx --yes "$RAMUS_CLI" adb --port 5555 > "$OUT/adb-tunnel.txt" 2>&1
adb_rc=$?
set -e
if [ "$adb_rc" -ne 0 ]; then
  block "BLOCKED_ADB_TUNNEL" "adb-tunnel" "Ramus ADB tunnel returned exit $adb_rc. No fallback session or trial retry was attempted."
fi
ADB_SERIAL="$(adb devices | awk 'NR>1 && $2=="device" {print $1; exit}')"
[ -n "$ADB_SERIAL" ] || block "BLOCKED_ADB_DEVICE" "adb-tunnel" "ADB tunnel opened but adb devices returned no connected device."
printf '%s\n' "$ADB_SERIAL" > "$OUT/adb-serial.txt"

set +e
adb -s "$ADB_SERIAL" shell getprop ro.product.cpu.abilist > "$OUT/device-abilist.txt" 2>&1
abi_rc=$?
set -e
if [ "$abi_rc" -ne 0 ]; then
  block "BLOCKED_DEVICE_ABI" "device-abi-check" "Could not read ro.product.cpu.abilist from the selected Ramus device."
fi
if ! grep -q 'arm64-v8a' "$OUT/device-abilist.txt"; then
  block "BLOCKED_DEVICE_ABI" "device-abi-check" \
    "Selected Ramus profile does not advertise arm64-v8a, required by both the pinned loader and original game XAPK. No alternate profile selection exists in ramus-cli 0.1.17 help; no second device was started."
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"; finish_session' EXIT
XAPK="$TMP/$APK_ASSET"
set +e
gh release download "$APK_TAG" --repo "${GITHUB_REPOSITORY:?}" --pattern "$APK_ASSET" --dir "$TMP" --clobber \
  > "$OUT/source-download.stdout" 2> "$OUT/source-download.stderr"
download_rc=$?
set -e
if [ "$download_rc" -ne 0 ] || [ ! -s "$XAPK" ]; then
  block "BLOCKED_SOURCE_DOWNLOAD" "source-xapk-download" "Could not retrieve the pinned XAPK from release $APK_TAG; no source APK was installed."
fi
chmod a-w "$XAPK"
source_before="$(sha256sum "$XAPK" | awk '{print $1}')"
if [ "$source_before" != "$APK_SHA256" ]; then
  block "BLOCKED_SOURCE_SHA" "source-xapk-integrity" "Downloaded XAPK SHA-256 $source_before does not match the pinned original $APK_SHA256."
fi
mkdir -p "$TMP/unpacked"
unzip -q "$XAPK" -d "$TMP/unpacked"
python3 - "$TMP/unpacked/manifest.json" "$PACKAGE" <<'PY' || block "BLOCKED_SOURCE_PACKAGE" "source-xapk-manifest" "XAPK manifest package does not match the authorized WindWings package."
import json,sys
m=json.load(open(sys.argv[1]))
p=m.get('package_name') or m.get('package') or ''
if p != sys.argv[2]:
    print(f'package mismatch: expected {sys.argv[2]}, got {p}', file=sys.stderr)
    raise SystemExit(1)
PY

mapfile -t PARTS < <(find "$TMP/unpacked" -type f -iname '*.apk' -printf '%s %p\n' | sort -rn | cut -d' ' -f2-)
[ "${#PARTS[@]}" -gt 0 ] || block "BLOCKED_SOURCE_APK_PARTS" "source-xapk-extract" "The pinned XAPK contains no APK parts."
BASE=""
for f in "${PARTS[@]}"; do
  case "$(basename "$f")" in base.apk|base-master.apk|*universal*.apk) BASE="$f"; break ;; esac
done
[ -n "$BASE" ] || BASE="${PARTS[0]}"
INSTALL_PARTS=("$BASE")
for f in "${PARTS[@]}"; do [ "$f" = "$BASE" ] || INSTALL_PARTS+=("$f"); done
set +e
if [ "${#INSTALL_PARTS[@]}" -eq 1 ]; then
  adb -s "$ADB_SERIAL" install -r -t "${INSTALL_PARTS[0]}" > "$OUT/game-install.txt" 2>&1
else
  adb -s "$ADB_SERIAL" install-multiple -r -t "${INSTALL_PARTS[@]}" > "$OUT/game-install.txt" 2>&1
fi
install_rc=$?
set -e
if [ "$install_rc" -ne 0 ]; then
  block "BLOCKED_GAME_INSTALL" "source-xapk-install" "Android rejected the unchanged XAPK APK part(s); see game-install.txt."
fi

# Restore only the runtime bridge plugin into FusionCore's external plugin path.
adb -s "$ADB_SERIAL" shell appops set "$LOADER_PACKAGE" MANAGE_EXTERNAL_STORAGE allow \
  > "$OUT/loader-appops.txt" 2>&1 || true
PLUGIN_DIR="/sdcard/FusionCore/$PACKAGE/BepInEx/plugins"
adb -s "$ADB_SERIAL" shell mkdir -p "$PLUGIN_DIR" \
  > "$OUT/plugin-mkdir.txt" 2>&1 || block "BLOCKED_PLUGIN_PATH" "bridge-deploy" "Could not create FusionCore's documented per-game plugin directory."
adb -s "$ADB_SERIAL" push "$BUNDLE/RamusBridge.dll" "$PLUGIN_DIR/RamusBridge.dll" \
  > "$OUT/bridge-push.txt" 2>&1 || block "BLOCKED_BRIDGE_DEPLOY" "bridge-deploy" "Could not copy the pinned bridge DLL to the FusionCore plugin directory."

adb -s "$ADB_SERIAL" shell am start -n "$LOADER_PACKAGE/.SelectorActivity" > "$OUT/loader-launch.txt" 2>&1 \
  || block "BLOCKED_LOADER_LAUNCH" "loader-launch" "FusionCore SelectorActivity did not start."

# Find the target game row in the live accessibility tree. Tap only if its exact
# package text has bounds; otherwise stop without guessing coordinates.
for attempt in $(seq 1 30); do
  adb -s "$ADB_SERIAL" shell uiautomator dump /sdcard/ramus-loader-ui.xml >/dev/null 2>&1 || true
  adb -s "$ADB_SERIAL" exec-out cat /sdcard/ramus-loader-ui.xml > "$OUT/loader-ui.xml" 2>/dev/null || true
  if grep -Fq "$PACKAGE" "$OUT/loader-ui.xml"; then break; fi
  sleep 1
done
POINT="$(python3 - "$OUT/loader-ui.xml" "$PACKAGE" <<'PY'
import re,sys,xml.etree.ElementTree as ET
path,pkg=sys.argv[1:]
try: root=ET.parse(path).getroot()
except Exception: raise SystemExit(1)
for n in root.iter('node'):
    if n.attrib.get('text') == pkg:
        m=re.fullmatch(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',n.attrib.get('bounds',''))
        if m:
            x1,y1,x2,y2=map(int,m.groups())
            print((x1+x2)//2,(y1+y2)//2)
            raise SystemExit(0)
raise SystemExit(1)
PY
)" || block "BLOCKED_TARGET_NOT_LISTED" "fusioncore-target-selection" "The live FusionCore UI did not expose the exact game package with tap bounds; no coordinates were guessed."
read -r TAP_X TAP_Y <<< "$POINT"
printf '%s %s\n' "$TAP_X" "$TAP_Y" > "$OUT/target-tap-from-ui-bounds.txt"
adb -s "$ADB_SERIAL" shell input tap "$TAP_X" "$TAP_Y" > "$OUT/target-tap.txt" 2>&1 \
  || block "BLOCKED_TARGET_LAUNCH" "fusioncore-target-selection" "Could not tap the exact target row from its live accessibility bounds."
adb -s "$ADB_SERIAL" forward tcp:8080 tcp:8080 > "$OUT/adb-forward.txt" 2>&1 || true

health_ok=false
for attempt in $(seq 1 60); do
  if curl -fsS --max-time 4 http://127.0.0.1:8080/health -o "$OUT/health.json"; then health_ok=true; break; fi
  sleep 3
done
[ "$health_ok" = true ] || block "BLOCKED_BRIDGE_UNREACHABLE" "bridge-health" "No RamusBridge /health response arrived within the bounded 180-second wait after launching the game."

set +e
curl -fsS --max-time 30 \
  'http://127.0.0.1:8080/statics?type=Map_Get_Datas&max=200&arr=256&depth=2' \
  -o "$OUT/map-runtime-readback.json"
readback_rc=$?
set -e
[ "$readback_rc" -eq 0 ] || block "BLOCKED_MAP_READBACK" "map-statics-request" "The authorized /statics request failed; see session logs. No map values were inferred."
set +e
python3 tools/compare_l2_a5a74747_28_runtime_map.py "$OUT/map-runtime-readback.json" \
  --out "$OUT/map-comparison.json" > "$OUT/map-comparison.stdout" 2> "$OUT/map-comparison.stderr"
compare_rc=$?
set -e
source_after="$(sha256sum "$XAPK" | awk '{print $1}')"
[ "$source_after" = "$source_before" ] || block "BLOCKED_SOURCE_MUTATION" "source-xapk-integrity" "The XAPK source SHA changed after use; do not accept this run as evidence."

loader_sha="$(jq -r '.vehicle.sha256' "$BUNDLE/provenance.json")"
bridge_sha="$(jq -r '.bridge.sha256' "$BUNDLE/provenance.json")"
comparison_status="$(jq -r '.status' "$OUT/map-comparison.json")"
jq -n --arg status "$comparison_status" --arg source_sha "$source_before" \
  --arg loader_sha "$loader_sha" --arg bridge_sha "$bridge_sha" \
  --arg session "$SESSION" --argjson comparison "$(cat "$OUT/map-comparison.json")" \
  '{schema:"windwings-runtime-map-probe/v1",status:$status,failed_step:(if $status == "RUNTIME_READBACK_MATCHES_STATIC" then null else "map-comparison" end),
    session_started:true,session_id:$session,source_xapk_modified:false,source_xapk_sha256:$source_sha,
    loader_sha256:$loader_sha,bridge_sha256:$bridge_sha,
    request:{type:"Map_Get_Datas",max:200,arr:256,depth:2},runtime_readback:"session-receipt:map-runtime-readback.json",
    map_values:(if $comparison.evidence_level == "RUNTIME_READBACK" then $comparison.rows else null end),
    comparison:$comparison,second_device_status:"NOT_REACHED",live_dps_status:"NOT_REACHED"}' \
  > "$OUT/map-step.json"
{
  echo "# #28 runtime probe — Map step"
  echo
  echo "- **Status:** \`$comparison_status\`"
  echo "- **Session:** started once; see session-start.stdout and session-id.txt."
  echo "- **Original XAPK modified:** no; SHA-256 before/after: \`$source_before\` / \`$source_after\`."
  echo "- **Loader SHA-256:** \`$loader_sha\`"
  echo "- **RamusBridge.dll SHA-256:** \`$bridge_sha\`"
  echo "- **Request:** \`/statics?type=Map_Get_Datas&max=200&arr=256&depth=2\`"
  echo "- **Compared:** $(jq -r '.rows_compared' "$OUT/map-comparison.json") rows / $(jq -r '.values_compared' "$OUT/map-comparison.json") scalar values; mismatches: $(jq -r '.value_mismatch_count' "$OUT/map-comparison.json")."
  echo "- **Step 2 (second device):** not run in this session; check the CLI/profile support before any second session."
  echo "- **Step 3 (live DPS):** not reached by this map-only receipt."
} > "$OUT/map-step-report.md"

if [ "$compare_rc" -eq 0 ]; then
  echo 'Map step completed. Preserve this readback and continue to the separate second-device/live-DPS receipts.'
else
  echo 'Map readback was incomplete or mismatched; stop at the exact map step and do not infer missing values.'
fi
