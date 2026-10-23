#!/usr/bin/env bash
# fetch-loader-refs.sh — download the real loader releases used to compile the bridge.
#
#   fetch-loader-refs.sh --refs .ci/refs
#
# Produces .ci/refs/{bep6,bep5,melon}. The BepInEx zips contain directories with
# restrictive modes, so permissions are repaired before anything walks the tree.
set -euo pipefail

REFS=".ci/refs"
while [ $# -gt 0 ]; do
  case "$1" in
    --refs) REFS="$2"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
set -x

BEP6_TAG="${BEP6_TAG:-v6.0.0-pre.2}"
BEP5_TAG="${BEP5_TAG:-v5.4.23.5}"
MELON_TAG="${MELON_TAG:-v0.7.3}"
mkdir -p "$REFS"

log() { printf '[refs] %s\n' "$*"; }

fetch() {  # fetch <url> <dest-zip> <out-dir>
  local url="$1" zip="$2" out="$3"
  log "GET $url"
  curl -fL --retry 3 --retry-delay 2 --silent --show-error -o "$zip" "$url"
  mkdir -p "$out"
  unzip -q -o "$zip" -d "$out"
  # Some BepInEx archives ship directories with restrictive modes.
  chmod -R u+rwX "$out" 2>/dev/null || true
}

fetch "https://github.com/BepInEx/BepInEx/releases/download/$BEP6_TAG/BepInEx-Unity.IL2CPP-win-x64-${BEP6_TAG#v}.zip" \
      .ci/bep6.zip "$REFS/bep6"
fetch "https://github.com/BepInEx/BepInEx/releases/download/$BEP5_TAG/BepInEx_win_x64_${BEP5_TAG#v}.zip" \
      .ci/bep5.zip "$REFS/bep5"
fetch "https://github.com/LavaGang/MelonLoader/releases/download/$MELON_TAG/MelonLoader.x64.zip" \
      .ci/melon.zip "$REFS/melon"

# Optional: on-device BepInEx 6 refs (core + generated interop pulled from the
# game device, binding-exact). Skipped silently if the release isn't reachable
# (the standalone phone build target then reports refs missing instead).
PHONE_REFS_TAG="${PHONE_REFS_TAG:-phone-refs}"
if curl -fL --retry 2 --silent -o .ci/bep6-phone-refs.zip \
     "https://github.com/${GITHUB_REPOSITORY}/releases/download/$PHONE_REFS_TAG/bep6-phone-refs.zip" 2>/dev/null; then
  rm -rf .ci/phone-refs "$REFS/bep6-refs-phone"
  mkdir -p .ci/phone-refs "$REFS"
  unzip -q -o .ci/bep6-phone-refs.zip -d ".ci/phone-refs" || true
  # zip layout: <ziproot>/bep6-refs-phone/{bep6-core-phone,bep6-interop}
  src=$(find .ci/phone-refs -maxdepth 4 -type d -name 'bep6-refs-phone' 2>/dev/null | head -1 || true)
  if [ -n "$src" ]; then
    mv "$src" "$REFS/bep6-refs-phone"
  else
    src=$(find .ci/phone-refs -maxdepth 4 -type d -name 'bep6-*' 2>/dev/null | head -1 || true)
    if [ -n "$src" ] && [ -d "$src" ]; then mv "$src" "$REFS/bep6-refs-phone"; fi
  fi
  rm -rf .ci/phone-refs
  if [ -d "$REFS/bep6-refs-phone" ]; then
    log "phone refs: $( (find "$REFS/bep6-refs-phone" -name '*.dll' 2>/dev/null) | wc -l ) dll"
  else
    log "phone refs: nested dirs not found, listing dump:"
    find .ci -maxdepth 3 -type d | sed 's/^/  /' | head -20 || true
  fi
else
  log "phone refs not available (skipping)"
fi

for d in bep6 bep5 melon; do
  n=$(find "$REFS/$d" -name '*.dll' 2>/dev/null | wc -l || echo 0)
  log "$d: $n dll"
  find "$REFS/$d" -name '*.dll' 2>/dev/null | head -8 | sed 's/^/  /' || true
done

# The three references the adapters actually need — fail early if a zip changed shape.
for needle in bep6/BepInEx.Core.dll bep6/BepInEx.Unity.IL2CPP.dll melon/MelonLoader.dll bep5/BepInEx.dll; do
  if find "$REFS" -name "$(basename "$needle")" 2>/dev/null | grep -q .; then
    log "found $(basename "$needle")"
  else
    log "MISSING $(basename "$needle")"
  fi
done
