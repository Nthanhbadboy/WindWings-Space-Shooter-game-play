#!/usr/bin/env bash
# prepare-apk.sh — turn whatever the repo ships (APK, XAPK, APKS bundle) into
# something Ramus can install, and print a reproducible inventory.
#
#   prepare-apk.sh --source release:windwings-apk-1.3.118 --out .ci/apk
#   prepare-apk.sh --source https://…/app.xapk            --out .ci/apk
#   prepare-apk.sh --source runtime-probe/app.apk        --out .ci/apk
#
# Writes into <out>:
#   base.apk                 the APK to hand to `ramus session start --apk`
#   splits/*.apk             config splits, if the source was a bundle
#   apk-inventory.txt        every APK found, with size / manifest / arm64 libs
#
# Emits `key=value` lines (and appends them to $GITHUB_OUTPUT when present):
#   apk=…  splits=…  kind=apk|xapk|apks  package=…  has_obb=true|false
set -euo pipefail

SRC=""
OUT=".ci/apk"
while [ $# -gt 0 ]; do
  case "$1" in
    --source) SRC="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

[ -n "$SRC" ] || { echo "usage: prepare-apk.sh --source <path|url|release:TAG> --out DIR" >&2; exit 2; }

log() { printf '[prepare-apk] %s\n' "$*"; }
die() { printf '[prepare-apk] ERROR %s\n' "$*" >&2; exit 1; }

emit() {
  printf '%s\n' "$1"
  if [ -n "${GITHUB_OUTPUT:-}" ]; then printf '%s\n' "$1" >> "$GITHUB_OUTPUT"; fi
}

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$OUT"
rm -rf "$OUT/splits" "$OUT/obb"   # never mix leftovers from a previous run
mkdir -p "$OUT/splits"

# ── 1. fetch ───────────────────────────────────────────────────────────────
LOCAL=""
case "$SRC" in
  release:*)
    TAG="${SRC#release:}"
    log "downloading GitHub release '$TAG' (draft releases need a token with repo read access)"
    mkdir -p "$WORK/rel"
    if ! gh release download "$TAG" --dir "$WORK/rel" --clobber \
         --pattern '*.apk' --pattern '*.xapk' --pattern '*.apks' 2>"$WORK/rel.err"; then
      # Older CLI builds do not accept repeated --pattern; retry without a filter.
      if ! gh release download "$TAG" --dir "$WORK/rel" --clobber 2>>"$WORK/rel.err"; then
        cat "$WORK/rel.err" >&2
        die "could not download release $TAG (draft releases need contents:write on the workflow token, or attach the APK elsewhere)"
      fi
    fi
    LOCAL="$(find "$WORK/rel" -type f \( -iname '*.apk' -o -iname '*.xapk' -o -iname '*.apks' \) -printf '%s %p\n' | sort -rn | head -1 | cut -d' ' -f2-)"
    [ -n "$LOCAL" ] || die "release $TAG has no .apk/.xapk/.apks asset"
    ;;
  http://*|https://*)
    log "downloading $SRC"
    LOCAL="$WORK/$(basename "${SRC%%\?*}")"
    curl -fL --retry 3 --retry-delay 2 -o "$LOCAL" "$SRC" || die "download failed"
    ;;
  *)
    [ -f "$SRC" ] || die "no such file: $SRC"
    LOCAL="$SRC"
    ;;
esac

[ -s "$LOCAL" ] || die "empty file: $LOCAL"
SIZE=$(stat -c%s "$LOCAL" 2>/dev/null || stat -f%z "$LOCAL")
log "source: $(basename "$LOCAL") — ${SIZE} bytes"

# A real APK/XAPK is a zip.
MAGIC=$(head -c 4 "$LOCAL" | od -An -tx1 | tr -d ' \n')
[ "$MAGIC" = "504b0304" ] || die "$(basename "$LOCAL") is not a zip (magic $MAGIC) — truncated download?"

# ── 2. is it already a plain APK? ──────────────────────────────────────────
is_apk() {
  unzip -l "$1" 2>/dev/null | awk '{ $1=$2=$3=""; sub(/^ +/,""); print }' | grep -qx 'AndroidManifest.xml'
}

INVENTORY="$OUT/apk-inventory.txt"
: > "$INVENTORY"
{
  echo "source:      $(basename "$LOCAL") ($SIZE bytes)"
  echo "sha256:      $(sha256sum "$LOCAL" | cut -d' ' -f1)"
  echo "fetched at:  $(date -u +%FT%TZ)"
  echo
} >> "$INVENTORY"

if is_apk "$LOCAL"; then
  KIND="apk"
  cp "$LOCAL" "$OUT/base.apk"
  SPLITS=""
  log "plain APK — using as base"
else
  log "not a plain APK → treating as an XAPK/APKS container"
  mkdir -p "$WORK/unz"
  unzip -q -o "$LOCAL" -d "$WORK/unz" || die "unzip failed"

  KIND="xapk"
  case "$LOCAL" in *.apks) KIND="apks" ;; esac

  # Every APK inside, biggest first.
  mapfile -t FOUND < <(find "$WORK/unz" -type f -iname '*.apk' -printf '%s %p\n' | sort -rn | cut -d' ' -f2-)
  [ "${#FOUND[@]}" -gt 0 ] || die "container holds no .apk — cannot install without adb (bundletool split APKs need apksigner)"

  BASE=""
  for f in "${FOUND[@]}"; do
    case "$(basename "$f")" in
      base.apk|base-master.apk|*universal*.apk) BASE="$f"; break ;;
    esac
  done
  [ -n "$BASE" ] || BASE="${FOUND[0]}"

  cp "$BASE" "$OUT/base.apk"
  SPLITS=""
  for f in "${FOUND[@]}"; do
    [ "$f" = "$BASE" ] && continue
    cp "$f" "$OUT/splits/$(basename "$f")"
    SPLITS="$SPLITS $OUT/splits/$(basename "$f")"
  done
  SPLITS="${SPLITS# }"

  # OBB payloads travel outside the APK; only adb can push them.
  OBB_DIRS=$(find "$WORK/unz" -type d -ipath '*Android/obb*' 2>/dev/null | head -1 || true)
  if [ -n "$OBB_DIRS" ]; then
    mkdir -p "$OUT/obb"
    find "$WORK/unz" -type d -ipath '*Android/obb*' -exec cp -r {}/* "$OUT/obb/" \; 2>/dev/null || true
    log "OBB payload found → $OUT/obb (push with adb; trial mode cannot)"
  fi
fi

# ── 3. inventory ───────────────────────────────────────────────────────────
PKG=""
MANIFEST_JSON="$(find "$WORK" -maxdepth 3 -name 'manifest.json' | head -1 || true)"
if [ -n "$MANIFEST_JSON" ]; then
  PKG=$(python3 - "$MANIFEST_JSON" <<'PY' 2>/dev/null || true
import json,sys
try:
    d=json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
print(d.get("package_name") or d.get("package") or "")
PY
)
fi

for f in "$OUT/base.apk" $SPLITS; do
  [ -f "$f" ] || continue
  bytes=$(stat -c%s "$f")
  manifest=$(unzip -l "$f" 2>/dev/null | grep -c 'AndroidManifest.xml' || true)
  arm64=$(unzip -l "$f" 2>/dev/null | grep -c 'lib/arm64-v8a/' || true)
  obb=$(unzip -l "$f" 2>/dev/null | grep -c 'assets/bin/Data' || true)
  printf '%-52s %12s B  manifest=%s arm64libs=%-4s unitydata=%s\n' \
    "$(basename "$f")" "$bytes" "$manifest" "$arm64" "$obb" >> "$INVENTORY"
done

BASE_MB=$(( $(stat -c%s "$OUT/base.apk") / 1000000 ))
{
  echo
  echo "kind:        $KIND"
  echo "base:        $OUT/base.apk (${BASE_MB} MB)"
  echo "splits:      ${SPLITS:-none}"
  echo "package:     ${PKG:-unknown (manifest.json absent)}"
} >> "$INVENTORY"

cat "$INVENTORY"

emit "apk=$OUT/base.apk"
emit "splits=$SPLITS"
emit "kind=$KIND"
emit "package=$PKG"
emit "base_mb=$BASE_MB"
