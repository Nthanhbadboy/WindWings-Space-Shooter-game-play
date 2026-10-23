#!/usr/bin/env bash
# collect.sh — một phiên Ramus, thu hết dữ liệu cần cho docs/spec.
#
# Chạy:  bash runtime-probe/collect.sh /duong/dan/to/windwings-mod.apk
#
# Không có tham số nào khác. Không hỏi lại. Sai ở đâu thì in "STOP:" rồi thoát.
# Mọi thứ ghi vào docs/apk-analysis/ramus/<ngày>/
set -uo pipefail

MOD_APK=${1:-}
[ -n "$MOD_APK" ] || { echo "STOP: thiếu tham số APK. Dùng: bash runtime-probe/collect.sh <apk>"; exit 2; }
[ -f "$MOD_APK" ] || { echo "STOP: không thấy file $MOD_APK"; exit 2; }

RAMUS_CLI=${RAMUS_CLI:-ramus-cli@0.1.17}
PKG=com.Wind.wings.Space.Shooter
OUT=${OUT:-docs/apk-analysis/ramus/$(date +%F)}
mkdir -p "$OUT"

say(){ printf '\n== %s ==\n' "$*"; }
die(){ echo "STOP: $*"; echo "Đã ghi những gì có vào $OUT — dán 40 dòng cuối cho người phụ trách."; exit 1; }
ram(){ npx --yes "$RAMUS_CLI" "$@"; }

# ── 1. kiểm APK ────────────────────────────────────────────────────────────
say "1. kiểm APK"
ls -l "$MOD_APK"
sha256sum "$MOD_APK" | tee "$OUT/apk-sha256.txt"
unzip -l "$MOD_APK" | grep -qiE "RamusBridge\.dll|BepInEx/|MelonLoader/" \
  || die "APK không có RamusBridge.dll và không có thư mục loader — đây không phải bản mod"

# ── 2. phiên ───────────────────────────────────────────────────────────────
say "2. bật phiên"
ram session start --apk "$MOD_APK" --wait --timeout 600 | tee "$OUT/session.json" \
  || die "session start thất bại"
SID=$(python3 - "$OUT/session.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
s=d.get("session")
print(s if isinstance(s,str) else (d.get("sessionId") or d.get("id") or d.get("session",{}).get("id") or ""))
PY
)
[ -n "$SID" ] || die "không đọc được session id từ session.json"
ram session status | tee "$OUT/session-status.json"
echo "session=$SID"
python3 - "$OUT/session.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
if d.get("watchUrl"): print("WATCH (đưa cho user):", d["watchUrl"])
PY

# ── 3. tunnel (key mode) ───────────────────────────────────────────────────
MODE=key
say "3. mở adb tunnel"
if out=$(ram adb --port 5555 2>&1); then
  printf '%s\n' "$out" | tee "$OUT/adb.txt"
  SERIAL=$(printf '%s\n' "$out" | grep -oE '(emulator-[0-9]+|[0-9]{1,3}(\.[0-9]{1,3}){3}:[0-9]+)' | head -1)
  [ -n "$SERIAL" ] || SERIAL=$(adb devices 2>/dev/null | awk 'NR>1 && $2=="device"{print $1; exit}')
  if [ -n "$SERIAL" ]; then
    echo "$SERIAL" > "$OUT/serial.txt"
    adb -s "$SERIAL" forward tcp:8080 tcp:8080 >/dev/null 2>&1 || true
  fi
else
  MODE=trial; echo "không có adb (trial) — chỉ lấy được logcat + ảnh"
fi

B=http://127.0.0.1:8080
wait_health(){ # $1 = giây
  local end=$(( $(date +%s) + $1 ))
  while [ "$(date +%s)" -lt "$end" ]; do
    if curl -fsS --max-time 5 "$B/health" -o "$OUT/health.json" 2>/dev/null; then return 0; fi
    sleep 5
  done
  return 1
}

if [ "$MODE" = key ]; then
  say "4. chờ bridge sống"
  wait_health 180 || die "không gọi được $B/health sau 180s"
  cat "$OUT/health.json"

  # Tên class thật. Run 23/10 gọi trượt vì đoán tên không có namespace
  # (SpaceShooter.EnemySystem.Enemy_Get_Datas); /types trả đúng tên để dùng lại.
  say "4b. liệt kê tên class"
  mkdir -p "$OUT/types"
  for q in Enemy_Get_Datas Percent Map_Get_Datas Stage_Get_Datas GP_Datas Tech Drone; do
    get "/types?filter=$q" "$OUT/types/$q.json"
  done
fi

# ── 4. dump ────────────────────────────────────────────────────────────────
TYPES="Player_Get_Datas Stage_Get_Datas Enemy_Get_Datas Map_Get_Datas Device_Get_Data
Enemy_Data_Balance Data_Players Data_Items Data_Boss DataShopPack IAPProduct GP_Datas
Tech_Ability_Data RankManager ArenaManager Box_Rewards Call_Data Wave Spawner"

get(){ curl -fsS --max-time 25 "$B$1" -o "$2" 2>/dev/null || echo "FAIL $1" >> "$OUT/failed.txt"; }

dump_moment(){ # $1 = menu | stage | ingame
  local L=$1
  say "dump [$L]"
  if [ "$MODE" = key ]; then
    for t in $TYPES; do
      mkdir -p "$OUT/statics-$L"
      get "/statics?type=$t&max=300&arr=256&depth=2" "$OUT/statics-$L/$t.json"
    done
    mkdir -p "$OUT/core-$L"
    get "/scene?max=300"               "$OUT/core-$L/scene.json"
    get "/hierarchy?depth=4&max=2000"  "$OUT/core-$L/hierarchy.json"
    get "/logs?n=300"                  "$OUT/core-$L/logs.json"
    get "/metrics"                     "$OUT/core-$L/metrics.json"
    for o in Player_Ingame Player_Health Enemy_Sub Enemy_Hp_Bar Stage_Behaviour MapController Gun_Attack; do
      mkdir -p "$OUT/find"; get "/find?name=$o&max=20" "$OUT/find/$L-$o.json"
    done
  fi
  ram snapshot --raw > "$OUT/ui-$L.xml" 2>/dev/null || echo "FAIL snapshot $L" >> "$OUT/failed.txt"
  ram screenshot --out "$OUT/screen-$L.jpg" --max-width 720 >/dev/null 2>&1 || true
  if [ -n "${SERIAL:-}" ]; then
    adb -s "$SERIAL" logcat -b main -b crash -d > "$OUT/logcat-$L.txt" 2>/dev/null || true
  else
    ram logcat --limit 500 --filter "$PKG" > "$OUT/logcat-$L.txt" 2>/dev/null || true
  fi
}

# Bấm vào phần tử có text khớp. Không khớp thì in danh sách text và dừng — không đoán.
tap_text(){ # $1 = xml, $2.. = regex
  local xml=$1; shift
  local coords
  coords=$(python3 - "$xml" "$@" <<'PY'
import re,sys
xml=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
pats=[re.compile(p,re.I) for p in sys.argv[2:]]
m=re.search(r'bounds="\[0,0\]\[(\d+),(\d+)\]"',xml)
if not m: sys.exit(1)
W,H=int(m.group(1)),int(m.group(2))
nodes=re.findall(r'<node[^>]*text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',xml)
if not nodes:
    nodes=[(b,d,e,f,g) for a,b,c,d,e,f,g in re.findall(r'<node[^>]*text="([^"]*)"([^>]*)bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',xml)]
for text,x1,y1,x2,y2 in nodes:
    if not text.strip(): continue
    if any(p.search(text) for p in pats):
        cx=(int(x1)+int(x2))/2/W; cy=(int(y1)+int(y2))/2/H
        print(f"{cx:.4f},{cy:.4f}"); print(text[:60],file=sys.stderr); sys.exit(0)
sys.exit(1)
PY
)
  [ -n "$coords" ] || return 1
  echo "tap $coords"
  ram tap "$coords" >/dev/null 2>&1 || true
  sleep 3
}

# ── 5. đi qua menu ─────────────────────────────────────────────────────────
say "5. dọn hộp thoại hệ thống"
ram app launch >/dev/null 2>&1 || true
sleep 8
dump_moment menu
tap_text "$OUT/ui-menu.xml" 'got it|^ok$|allow|accept' && dump_moment menu

say "6. vào màn chơi"
entered=0
for i in 1 2 3 4 5 6; do
  ram snapshot --raw > "$OUT/ui-step.xml" 2>/dev/null || true
  if tap_text "$OUT/ui-step.xml" '^continue$|^play$|^start$|^start game$|^let.s go$'; then
    sleep 4; continue
  fi
  if [ "$MODE" = key ] && curl -fsS --max-time 8 "$B/health" 2>/dev/null | grep -qi 'ingame'; then
    entered=1; break
  fi
  # stage/mode: bấm ô stage đầu tiên nếu thấy chữ stage
  if tap_text "$OUT/ui-step.xml" '^stage 1$|^1-1$|^stage$|^play$|^select$'; then sleep 4; continue; fi
  break
done
sleep 6
dump_moment stage || true
[ "$entered" -eq 1 ] && echo "đã vào scene chơi" || echo "chưa xác nhận được scene chơi — vẫn dump tiếp"

if [ "$MODE" = key ]; then
  say "7. đóng băng rồi dump trong màn"
  curl -fsS -X POST "$B/timescale?v=0" >/dev/null 2>&1 || true
  dump_moment ingame
  for i in 1 2 3 4 5; do get "/metrics" "$OUT/metrics-$i.json"; sleep 2; done
  curl -fsS -X POST "$B/timescale?v=1" >/dev/null 2>&1 || true
fi

# ── 6. kiểm đủ ─────────────────────────────────────────────────────────────
say "8. kiểm tra đầy đủ"
python3 - "$OUT" "$MODE" <<'PY'
import json,pathlib,sys
out=pathlib.Path(sys.argv[1]); mode=sys.argv[2]
need={"P0 statics":["statics-ingame/Player_Get_Datas.json","statics-ingame/Stage_Get_Datas.json",
                    "statics-ingame/Enemy_Get_Datas.json","statics-ingame/Map_Get_Datas.json",
                    "statics-ingame/Device_Get_Data.json","statics-ingame/Enemy_Data_Balance.json"],
      "ten class":["types/Percent.json","types/Enemy_Get_Datas.json"],
      "P0 runtime":["find/ingame-Player_Health.json","find/ingame-Enemy_Sub.json"],
      "màn hình":["screen-menu.jpg","screen-stage.jpg","screen-ingame.jpg"],
      "log":["logcat-final.txt"] if (pathlib.Path(sys.argv[1])/"logcat-final.txt").exists() else ["logcat-ingame.txt"],
      "handle":["session.json"]}
bad=[]
for g,fs in need.items():
    for f in fs:
        p=out/f
        if not (p.exists() and p.stat().st_size>20): bad.append(f"[{g}] {f}")
if mode=="trial":
    print("MODE=trial: không có adb ⇒ KHÔNG lấy được số từ /statics. Chỉ có ảnh + logcat.")
    print("ĐÂY KHÔNG PHẢI LỖI CỦA SCRIPT — cần key mode để có số liệu.")
else:
    print("\nĐỦ" if not bad else "THIẾU:\n  "+"\n  ".join(bad))
PY

say "xong"
echo "session giữ nguyên: $SID"
echo "kết thúc khi không cần nữa: npx --yes $RAMUS_CLI session end"
