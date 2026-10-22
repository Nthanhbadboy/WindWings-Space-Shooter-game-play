#!/usr/bin/env bash
# Probe public sources for the WindWings APK from inside GitHub Actions.
# The Arena sandbox can only reach github.com / pypi.org, so this runs on a
# GitHub-hosted runner (open internet) and prints a compact report.
set -u

UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
OUT="${GITHUB_STEP_SUMMARY:-/dev/null}"

say() { echo "$@" | tee -a "$OUT"; }

probe() {
  local name="$1" url="$2"
  local hdr body code clen ctype eff
  hdr=$(curl -sSL -A "$UA" --max-time 45 -o /tmp/body.bin -D /tmp/hdr.txt \
        -w '%{http_code}|%{size_download}|%{content_type}|%{url_effective}' "$url" 2>/tmp/err.txt || true)
  code=${hdr%%|*}; rest=${hdr#*|}
  clen=$(awk 'BEGIN{IGNORECASE=1} /^content-length:/{v=$2} END{gsub(/\r/,"",v); print v}' /tmp/hdr.txt | tail -1)
  ctype=$(echo "$rest" | cut -d'|' -f3)
  eff=$(echo "$rest" | cut -d'|' -f4)
  say "### $name"
  say "- url: \`$url\`"
  say "- http: $code  bytes: $(stat -c%s /tmp/body.bin 2>/dev/null || echo 0)  content-length: ${clen:-?}  type: ${ctype:-?}"
  say "- final: \`${eff:0:160}\`"
  file /tmp/body.bin 2>/dev/null | sed 's/^/  /' | tee -a "$OUT"
  case "$ctype" in
    *json*|*text*|*html*)
      head -c 700 /tmp/body.bin | tr '\n' ' ' | sed 's/  */ /g' | tee -a "$OUT"; echo | tee -a "$OUT" ;;
  esac
  say ""
}

say "# APK source probe ($(date -u +%FT%TZ))"
say ""

probe "APKPure d.apkpure.com APK" "https://d.apkpure.com/b/APK/com.Wind.wings.Space.Shooter?version=latest"
probe "APKPure d.apkpure.com XAPK" "https://d.apkpure.com/b/XAPK/com.Wind.wings.Space.Shooter?version=latest"
probe "APKPure d.apkpure.net APK" "https://d.apkpure.net/b/APK/com.Wind.wings.Space.Shooter?version=latest"
probe "APKPure download page" "https://apkpure.com/windwings-space-shooter/com.Wind.wings.Space.Shooter/download"
probe "APKCombo page" "https://apkcombo.com/windwings-space-shooter/com.Wind.wings.Space.Shooter/"
probe "APKCombo download page" "https://apkcombo.com/windwings-space-shooter/com.Wind.wings.Space.Shooter/download/apk"
probe "Uptodown download page" "https://wind-wings-space-shooter.en.uptodown.com/android/download"
probe "Aptoide search API" "https://ws75.aptoide.com/api/7/apps/search?query=WindWings%20Space%20Shooter&limit=10"
probe "Aptoide getMeta" "https://ws75.aptoide.com/api/7/app/getMeta?package_name=com.Wind.wings.Space.Shooter"
probe "APKMonk page" "https://apkmonk.com/app/com.Wind.wings.Space.Shooter/"
probe "APKSupport page" "https://apk.support/download-app/com.Wind.wings.Space.Shooter"
probe "APKMirror search" "https://www.apkmirror.com/?post_type=app_release&searchtype=apk&s=windwings"
probe "apkfab page" "https://apkfab.com/windwings-space-shooter/com.Wind.wings.Space.Shooter"
probe "apkdl page" "https://apk-dl.com/wind-wings-space-shooter-galaxy-attack/com.Wind.wings.Space.Shooter"
probe "apkvision page" "https://apkvision.org/games/action/windwings-space-shooter-108292/"
probe "m.apkpure API v3" "https://api.pureapk.com/m/v3/cms/app_version?hl=en-US&package_name=com.Wind.wings.Space.Shooter"

say "## done"
