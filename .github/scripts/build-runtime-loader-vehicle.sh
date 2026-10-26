#!/usr/bin/env bash
# Build a separate FusionCore Android loader + target-specific RamusBridge plugin.
# The official WindWings XAPK is downloaded read-only for provenance/inventory;
# entries may be read into temporary files for inspection, but the source XAPK is
# never changed/repacked and is never included in Git.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
OUT="${OUT:-${RUNNER_TEMP:-/tmp}/runtime-loader-vehicle}"
SCRATCH="${RUNNER_TEMP:-/tmp}/runtime-loader-scratch"
APK_TAG="${APK_TAG:-windwings-apk-1.3.118}"
APK_ASSET="${APK_ASSET:-windwings.xapk}"
APK_SHA256="${APK_SHA256:-f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e}"
APK_SIZE="${APK_SIZE:-142125649}"
FUSIONCORE_COMMIT="${FUSIONCORE_COMMIT:-bf4c69d9d4724e4eff058664a5be0a1d9cfd4e61}"
FUSIONCORE_TAG="${FUSIONCORE_TAG:-0.045}"
PHONE_REFS_TAG="${PHONE_REFS_TAG:-phone-refs}"
PHONE_REFS_SHA256="${PHONE_REFS_SHA256:-d5416e4e95628136fe6e49d2e9905b11fca1bba03a7bceb481801e5b85bd710f}"
PACKAGE="${RAMUS_PACKAGE:-com.Wind.wings.Space.Shooter}"

log() { printf '[loader-vehicle] %s\n' "$*"; }
die() { printf '[loader-vehicle] ERROR: %s\n' "$*" >&2; exit 1; }

[ -n "${GH_TOKEN:-}" ] || die 'GH_TOKEN is required to retrieve the draft XAPK release asset and pinned phone refs.'
mkdir -p "$OUT" "$SCRATCH/source"
rm -rf "$OUT"/* "$SCRATCH/fusioncore" "$SCRATCH/xapk-inventory.json"

# ── Build the Android-side plugin against pinned on-device BepInEx refs. ─────
export BEP6_TAG="${BEP6_TAG:-v6.0.0-pre.2}"
export BEP5_TAG="${BEP5_TAG:-v5.4.23.5}"
export MELON_TAG="${MELON_TAG:-v0.7.3}"
export PHONE_REFS_TAG PHONE_REFS_SHA256
chmod +x "$ROOT/.github/scripts/fetch-loader-refs.sh" "$ROOT/.github/scripts/build-bridge.sh"
cd "$ROOT"
.github/scripts/fetch-loader-refs.sh --refs .ci/refs | tee "$OUT/loader-ref-fetch.log"
phone_refs_zip=".ci/bep6-phone-refs.zip"
[ -s "$phone_refs_zip" ] || die "pinned BepInEx phone refs were not fetched ($PHONE_REFS_TAG)"
actual_phone_refs_sha="$(sha256sum "$phone_refs_zip" | awk '{print $1}')"
[ "$actual_phone_refs_sha" = "$PHONE_REFS_SHA256" ] || die "phone refs SHA mismatch: $actual_phone_refs_sha"
sha256sum .ci/bep6.zip .ci/bep5.zip .ci/melon.zip .ci/bep6-phone-refs.zip > "$OUT/loader-ref-sha256.txt"
{
  java -version 2>&1
  dotnet --info 2>&1
  sdkmanager --version 2>&1 || true
} > "$OUT/build-toolchain.txt"
BRIDGE_OUT=".ci/runtime-loader-bridge"
.github/scripts/build-bridge.sh --out "$BRIDGE_OUT" --refs .ci/refs 2>&1 | tee "$OUT/bridge-build.log"
BRIDGE="$ROOT/$BRIDGE_OUT/bepinex6-phone/RamusBridge.dll"
[ -s "$BRIDGE" ] || die 'bridge-build did not produce the BepInEx 6 phone target.'
cp "$BRIDGE" "$OUT/RamusBridge.dll"

# ── Fetch, pin and inspect (read-only) the original XAPK. ────────────────────
XAPK="$SCRATCH/source/$APK_ASSET"
GH_TOKEN="$GH_TOKEN" gh release download "$APK_TAG" --repo "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}" \
  --pattern "$APK_ASSET" --dir "$SCRATCH/source" --clobber
[ -s "$XAPK" ] || die "release did not produce $XAPK"
chmod a-w "$XAPK"
source_sha_before="$(sha256sum "$XAPK" | awk '{print $1}')"
source_size="$(stat -c%s "$XAPK")"
[ "$source_sha_before" = "$APK_SHA256" ] || die "XAPK SHA mismatch: $source_sha_before"
[ "$source_size" = "$APK_SIZE" ] || die "XAPK size mismatch: $source_size"

python3 - "$XAPK" "$OUT/source-xapk-inventory.json" "$PACKAGE" <<'PY'
import hashlib, json, os, re, shutil, sys, tempfile, zipfile
from pathlib import Path
xapk_path, out_path, expected_pkg = sys.argv[1:]
abis_re = re.compile(r"^lib/([^/]+)/[^/]+$")
sha = hashlib.sha256()
with open(xapk_path, "rb") as f:
    for block in iter(lambda: f.read(1024 * 1024), b""):
        sha.update(block)
entries = []
manifest = {}
with zipfile.ZipFile(xapk_path) as outer:
    names = outer.namelist()
    manifest_name = next((n for n in names if n.lower().endswith("manifest.json")), None)
    if manifest_name:
        try:
            manifest = json.loads(outer.read(manifest_name))
        except Exception as exc:
            raise SystemExit(f"invalid XAPK manifest.json: {exc}")
    apk_infos = [i for i in outer.infolist() if i.filename.lower().endswith(".apk")]
    if not apk_infos:
        raise SystemExit("XAPK has no inner APKs")
    with tempfile.TemporaryDirectory(prefix="windwings-xapk-inspect-") as tmp:
        for index, info in enumerate(apk_infos):
            target = Path(tmp) / f"part-{index}.apk"
            h = hashlib.sha256()
            with outer.open(info) as src, target.open("wb") as dst:
                while True:
                    block = src.read(1024 * 1024)
                    if not block:
                        break
                    h.update(block)
                    dst.write(block)
            with zipfile.ZipFile(target) as apk:
                apknames = apk.namelist()
                abis = sorted({m.group(1) for name in apknames if (m := abis_re.fullmatch(name))})
            entries.append({"name": info.filename, "size_bytes": info.file_size,
                            "sha256": h.hexdigest(), "abis": abis})
package = manifest.get("package_name") or manifest.get("package") or ""
if not package:
    raise SystemExit("XAPK manifest does not identify a package")
if package != expected_pkg:
    raise SystemExit(f"XAPK package mismatch: expected {expected_pkg}, got {package}")
all_abis = sorted({abi for entry in entries for abi in entry["abis"]})
result = {
    "source": {"release_tag": "windwings-apk-1.3.118", "asset": "windwings.xapk",
               "size_bytes": os.path.getsize(xapk_path), "sha256": sha.hexdigest(),
               "modified": False},
    "manifest_package": package or None,
    "apk_parts": entries,
    "abis": all_abis,
    "obb_entries": [n for n in names if "/obb/" in n.lower() or n.lower().endswith(".obb")],
    "apk_part_count": len(entries),
}
Path(out_path).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, indent=2, sort_keys=True))
PY
source_sha_after="$(sha256sum "$XAPK" | awk '{print $1}')"
[ "$source_sha_after" = "$source_sha_before" ] || die 'original XAPK bytes changed during inspection.'
printf 'before=%s\nafter=%s\nmodified=false\n' "$source_sha_before" "$source_sha_after" > "$OUT/source-xapk-sha256-check.txt"

# ── Build a distinct loader app from a full commit pin. ──────────────────────
git clone --filter=blob:none --depth 1 --branch "$FUSIONCORE_TAG" \
  https://github.com/All-Of-Us-Mods/FusionCore.git "$SCRATCH/fusioncore"
actual_fusioncore_commit="$(git -C "$SCRATCH/fusioncore" rev-parse HEAD)"
[ "$actual_fusioncore_commit" = "$FUSIONCORE_COMMIT" ] || die "FusionCore source pin mismatch: $actual_fusioncore_commit"
FUSIONCORE_WRAPPER_SHA256="$(sha256sum "$SCRATCH/fusioncore/gradle/wrapper/gradle-wrapper.properties" | awk '{print $1}')"
export FUSIONCORE_WRAPPER_SHA256
chmod +x "$SCRATCH/fusioncore/gradlew"
(
  cd "$SCRATCH/fusioncore"
  ./gradlew --no-daemon --stacktrace :fusionApp:assembleDebug 2>&1 | tee "$OUT/fusioncore-build.log"
)
LOADER_APK="$SCRATCH/fusioncore/fusionApp/build/outputs/apk/debug/fusionApp-debug.apk"
[ -s "$LOADER_APK" ] || die 'FusionCore build did not produce fusionApp-debug.apk.'
cp "$LOADER_APK" "$OUT/fusionApp-debug.apk"

python3 - "$OUT/fusionApp-debug.apk" "$OUT/source-xapk-inventory.json" "$PACKAGE" <<'PY'
import hashlib, json, re, sys, zipfile
from pathlib import Path
apk_path, source_inventory_path, package = sys.argv[1:]
with zipfile.ZipFile(apk_path) as z:
    names = z.namelist()
abis = sorted({m.group(1) for name in names
               if (m := re.fullmatch(r"lib/([^/]+)/[^/]+", name))})
if not abis:
    raise SystemExit("loader APK contains no native ABI libraries")
source = json.loads(Path(source_inventory_path).read_text())
source_check = dict(line.split("=", 1) for line in (Path(apk_path).parent / "source-xapk-sha256-check.txt").read_text().splitlines())
source["hash_check"] = source_check
loader_sha = hashlib.sha256(Path(apk_path).read_bytes()).hexdigest()
bridge_path = Path(apk_path).parent / "RamusBridge.dll"
ref_hash_file = Path(apk_path).parent / "loader-ref-sha256.txt"
ref_hashes = {}
for line in ref_hash_file.read_text().splitlines():
    digest, filename = line.split(None, 1)
    ref_hashes[Path(filename.strip()).name] = digest
if not bridge_path.is_file():
    raise SystemExit("bridge DLL missing from vehicle output")
bridge_sha = hashlib.sha256(bridge_path.read_bytes()).hexdigest()
provenance = {
    "schema": "windwings-runtime-loader-vehicle/v1",
    "vehicle": {
        "project": "All-Of-Us-Mods/FusionCore",
        "tag": "0.045",
        "commit": "bf4c69d9d4724e4eff058664a5be0a1d9cfd4e61",
        "app_id": "dev.allofus.fusioncore",
        "artifact": "fusionApp-debug.apk",
        "size_bytes": Path(apk_path).stat().st_size,
        "sha256": loader_sha,
        "abis": abis,
        "gradle_wrapper_properties_sha256": __import__("os").environ.get("FUSIONCORE_WRAPPER_SHA256"),
        "source_xapk_modified": False,
    },
    "bridge": {
        "project_path": "runtime-probe/",
        "adapter": "BepInEx6/FusionCore phone target",
        "target_framework": "net10.0",
        "artifact": "RamusBridge.dll",
        "size_bytes": bridge_path.stat().st_size,
        "sha256": bridge_sha,
        "phone_refs_tag": "phone-refs",
        "phone_refs_sha256": "d5416e4e95628136fe6e49d2e9905b11fca1bba03a7bceb481801e5b85bd710f",
    },
    "source_xapk": source,
    "build": {
        "repository": __import__("os").environ.get("GITHUB_REPOSITORY"),
        "commit": __import__("os").environ.get("REPO_HEAD_SHA") or __import__("os").environ.get("GITHUB_SHA"),
        "run_id": __import__("os").environ.get("GITHUB_RUN_ID"),
        "workflow": __import__("os").environ.get("GITHUB_WORKFLOW"),
        "bepinex_refs": "v6.0.0-pre.2; phone refs separately pinned above",
        "melonloader_refs": "v0.7.3 (compiled matrix/provenance only; FusionCore runtime uses BepInEx Fusion)",
        "bepinex5_refs": "v5.4.23.5 (compiled matrix/provenance only)",
        "loader_reference_archive_sha256": ref_hashes,
        "toolchain_record": "build-toolchain.txt",
    },
    "deployment": {
        "separate_package": True,
        "bridge_destination": f"/sdcard/FusionCore/{package}/BepInEx/plugins/RamusBridge.dll",
        "original_xapk_in_loader_apk": False,
        "original_xapk_repacked": False,
    },
}
Path(Path(apk_path).parent / "provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n")
print(json.dumps({"loader_sha256": loader_sha, "loader_abis": abis,
                  "bridge_sha256": bridge_sha, "source_abis": source["abis"]}, indent=2))
PY

printf '%s\n' \
  'This is a separate FusionCore loader app. Install the original XAPK independently;' \
  'the build only downloaded and read the release asset, and did not repack it.' \
  'RamusBridge.dll is supplied alongside the APK for the loader plugin directory.' \
  > "$OUT/README.txt"

log "loader vehicle built: $OUT/fusionApp-debug.apk"
log "provenance: $OUT/provenance.json"
sha256sum "$OUT/fusionApp-debug.apk" "$OUT/RamusBridge.dll" "$XAPK" | tee "$OUT/SHA256SUMS.txt"
