# Runbook cho opencode — một phiên Ramus, lấy **hết** dữ liệu còn thiếu

> **Đối tượng đọc:** agent (opencode) không có ngữ cảnh của các cuộc trao đổi trước.
> File này **tự chứa**: mục tiêu, cách cấy server, cách bật phiên, danh mục phải lấy, cách
> kiểm tra đã đủ chưa. Làm đúng thứ tự.
>
> **Mục tiêu duy nhất:** mỗi lần bật phiên Ramus là **một phiên tốn quota** ⇒ phiên nào cũng
> phải lấy đủ cho nhiều ngày đọc. Đừng bật phiên để trả lời một câu hỏi.
>
> **Đầu vào:** APK mod đã chạy được ở máy local (đã có `RamusBridge.dll`, mở cổng 8080).
> Nếu chưa có, xem §2.5 — cấy server từ chính repo này.

---

## 0. Bốn giới hạn quyết định cách làm

| Giới hạn | Hệ quả |
|---|---|
| Trial Ramus: **không có adb**, 15 phút | `http://127.0.0.1:8080` **không gọi được**. Chỉ có logcat + ảnh. **Không lấy được số.** |
| Key mode (`RAMUS_API_KEY`): có adb | `adb forward` → `curl` toàn bộ API, gồm `/statics`. **Đường duy nhất lấy được số.** |
| Trial: APK ≤ 150 MB | Kiểm size **trước** khi bật phiên. |
| Static field của IL2CPP chỉ sống sau khi class được nạp | Phải dump **3 lúc**: menu → chọn mode/stage → trong màn chơi. Dump một lần ở menu sẽ ra `null` hàng loạt. |

**Nguyên tắc:** một phiên = một lần chạy `collect.sh` (§7). Chạy xong, kiểm `manifest.txt`
(§8) rồi mới `session end`.

---

## 1. Biến môi trường

```bash
set -euo pipefail
export RAMUS_CLI="ramus-cli@0.1.17"
export PKG="com.Wind.wings.Space.Shooter"

# APK mod đã chạy được ở local. Sửa đúng đường dẫn bạn có.
export MOD_APK="$PWD/.ci/apk/windwings-mod.apk"

export RUN_DATE="$(date +%F)"
export OUT="docs/apk-analysis/ramus/$RUN_DATE"
mkdir -p "$OUT"
```

Chưa có key, chỉ muốn xem app có chạy:

```bash
npx --yes "$RAMUS_CLI" trial --force
npx --yes "$RAMUS_CLI" status          # "key" phải khác "missing"
```

Có key: `export RAMUS_API_KEY=...` **trong shell**. Không ghi vào file trong repo, không echo.

---

## 2. Kiểm APK trước khi tốn một phiên

```bash
ls -l "$MOD_APK"
sha256sum "$MOD_APK" | tee "$OUT/apk-sha256.txt"

python3 - "$MOD_APK" <<'PY'
import os, sys
n = os.path.getsize(sys.argv[1])
print(f"{n} bytes = {n/1048576:.1f} MB")
print("OK cho trial" if n <= 150*1048576 else "QUÁ 150 MB — cần key mode")
PY

unzip -l "$MOD_APK" | grep -iE "RamusBridge\.dll|BepInEx/|MelonLoader/" | head
```

Không thấy `RamusBridge.dll` ⇒ **dừng**, sang §2.5.

---

## 2.5. Cấy server vào APK (chỉ khi bản mod chưa có bridge)

Server là một plugin C# nằm trong `runtime-probe/`: `TcpListener` ở cổng 8080 trên luồng nền,
trả JSON và **đồng thời** ghi `RAMUSB|{json}` ra logcat (đường dự phòng khi không có adb).

**a) Build DLL** (chạy trên máy có .NET SDK):

```bash
.github/scripts/build-bridge.sh
# → dist/core/RamusBridge.dll        (netstandard2.1, tham chiếu Unity)
# → dist/bepinex5/RamusBridge.dll    (BepInEx 5)
# → dist/bepinex6/RamusBridge.dll    (BepInEx 6 IL2CPP)
# → dist/melon/RamusBridge.dll       (MelonLoader)
```

**b) Chọn loader khớp với bản mod đang dùng.** Đừng trộn: BepInEx 5 và 6 khác API.
Bản đã chạy được ở local của bạn dùng loader nào thì dùng lại đúng loader đó.

**c) Đóng gói:**

| Loader | Cần gì trong APK |
|---|---|
| BepInEx 5 | `lib/arm64-v8a/libdoorstop.so` + `assets/BepInEx/` + `RamusBridge.dll` trong `BepInEx/plugins/` |
| BepInEx 6 IL2CPP | như trên, đúng bản IL2CPP, `RamusBridge.dll` trong `BepInEx/plugins/` |
| MelonLoader | `lib/arm64-v8a/libmelonloader.so` + `MelonLoader/` + DLL trong `Mods/` |

**d) Ký lại** — APK đã sửa bắt buộc phải ký lại thì mới cài được:

```bash
java -jar uber-apk-signer.jar --apks "$MOD_APK" --out "$OUT/signed"
```

**e) Kiểm bridge đã nằm trong APK:**

```bash
unzip -l "$OUT/signed/${MOD_APK##*/}" | grep -i RamusBridge.dll
```

Đây chính là bước CI dùng để quyết định có bật phiên hay không — không có DLL thì mọi bước sau
vô nghĩa.

> **Không** commit APK, DLL build hay file > 5 MB vào repo. Không phát hành bản mod ở đâu.

---

## 3. Bật phiên

```bash
npx --yes "$RAMUS_CLI" session start --apk "$MOD_APK" --wait --timeout 600 \
  | tee "$OUT/session.json"

SID=$(jq -r 'if (.session|type)=="string" then .session else (.sessionId // .id // empty) end' \
        "$OUT/session.json")
echo "session=$SID"
npx --yes "$RAMUS_CLI" session status | tee "$OUT/session-status.json"
```

> `watchUrl` trong `session.json` là link cho **người** xem và tự bấm, hiệu lực 72 giờ. In ra
> cho user ngay — đừng giữ một mình.

`session start` fail 3 lần ⇒ dừng, ghi lỗi, không thử tiếp.

---

## 4. Mở tunnel (key mode)

```bash
out=$(npx --yes "$RAMUS_CLI" adb --port 5555 2>&1 | tee "$OUT/adb.txt")
serial=$(printf '%s\n' "$out" | grep -oE '(emulator-[0-9]+|[0-9]{1,3}(\.[0-9]{1,3}){3}:[0-9]+)' | head -1)
[ -n "$serial" ] || serial=$(adb devices | awk 'NR>1 && $2=="device"{print $1; exit}')
echo "$serial" > "$OUT/serial.txt"

adb -s "$serial" forward tcp:8080 tcp:8080
curl -fsS --max-time 10 http://127.0.0.1:8080/health | tee "$OUT/health.json" | jq
```

`/health` không lên ⇒ thu logcat rồi xem lại:

```bash
adb -s "$serial" shell pidof "$PKG"
adb -s "$serial" logcat -b main -b crash -d > "$OUT/main-crash-logcat.txt"
adb -s "$serial" shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1
sleep 25 && curl -fsS http://127.0.0.1:8080/health | jq
```

---

## 5. API của bridge (dùng trong §7)

| Method | Path | Trả về |
|---|---|---|
| GET | `/health` | scene, fps, uptime, unity version |
| GET | `/state` | trạng thái gọn (dùng cho mirror logcat) |
| GET | `/scene?max=N` | scene đang mở + object gốc |
| GET | `/hierarchy?depth=D&max=N` | cây object |
| GET | `/find?name=X&max=N` | object theo tên |
| GET | `/statics?type=T&max=N&arr=128&depth=2` | **static field của class `T`**; `arr` = phần tử mỗi mảng, `depth` = số tầng mảng lồng (2 để mở `List<int[]>`) |
| GET | `/logs?n=N` | vòng log trong tiến trình |
| GET | `/metrics` | frame/fps |
| GET | `/screenshot` | PNG màn hình |
| POST | `/timescale?v=<x>` | đổi `Time.timeScale` — **`0` để đóng băng game khi dump** |
| POST | `/mark?name=x` | ghi `RAMUSB-MARK\|x` vào logcat |

Nếu `RamusBridge.ini` có `token=...` thì mọi request phải kèm `X-Ramus-Token: <token>`.

---

## 6. Danh mục phải lấy (đủ để không phải chạy lại)

Ký hiệu **P0** = đang chặn tài liệu, **P1** = đối chiếu, **P2** = làm dày thêm.

### A. Static data — `/statics?type=<T>`

| # | Type | Lấy gì | Đích (file docs) | Ưu tiên |
|---|---|---|---|---|
| A1 | `Player_Get_Datas` | các mảng `pct` theo **mode** (ngưỡng sao) + toàn bộ field | `MISSIONS_STARS.md` (đang trống) | **P0** |
| A2 | `Stage_Get_Datas` | `levelDelta` theo mode, `ModeCurrent`, bảng stage | `DIFFICULTY_MODES.md`, `BALANCE.md` | **P0** |
| A3 | `Enemy_Get_Datas` | HP gốc, `noDamage`, phân loại boss | `ENEMY_HP_RUNTIME.md` | **P0** |
| A4 | `Map_Get_Datas` | `listMapDatas` (map → danh sách wave), `GetNumberWaves` | `ENCOUNTERS.md` — blocker A2/T1 | **P0** |
| A5 | `Device_Get_Data` | bảng stat device (39 field) | `BALANCE.md` — blocker B1/T5 | **P0** |
| A6 | `Enemy_Data_Balance` | hằng cân bằng, thứ tự nhân HP | `ENEMY_HP_RUNTIME.md` — blocker B3 | **P0** |
| A7 | `Data_Players`, `Data_Items`, `Data_Boss` | id, star, giá | đối chiếu `14-*.csv` | P1 |
| A8 | `DataShopPack`, `IAPProduct`, `GP_Datas` | gói shop, giá IAP | `ECONOMY.md` | P1 |
| A9 | `Tech_Ability_Data` | cây tech, ability 7 (HP) | `BALANCE.md` §HP player | P1 |
| A10 | `RankManager`, `ArenaManager`, `Box_Rewards` | rank, arena, thưởng box | `ECONOMY.md` | P2 |
| A11 | `Call_Data`, `Call_Point`, `Wave`, `Spawner` | cấu trúc wave/spawn | `ENCOUNTERS.md` | P2 |

**Dump mỗi type 3 lần** (hậu tố file `-menu`, `-stage`, `-ingame`) — static chỉ sống sau khi
class được nạp. Thiếu một lúc là mất dữ liệu, phải chạy lại phiên.

### B. Runtime instance — `/find`, `/hierarchy`

| # | Object | Lấy gì | Đích | Ưu tiên |
|---|---|---|---|---|
| B1 | `Player_Ingame`, `Player_Health` | HP hiện tại / max, giáp, `StartHealth` | `COMBAT.md`, `BALANCE.md` | **P0** |
| B2 | `Enemy_Sub` × nhiều stage | HP enemy **runtime** ở stage 1 / 20 / 40 / boss | `ENEMY_HP_RUNTIME.md` — chốt thứ tự nhân | **P0** |
| B3 | `Enemy_Hp_Bar` | có HP bar ở mọi enemy? | xác nhận 109/109 | P1 |
| B4 | `MapController`, `Stage_Behaviour` | stage hiện tại, tiến trình wave | `GAMEPLAY.md` | P1 |
| B5 | `Gun_Attack`, `Bullet_*` | damage, tốc độ bắn | `COMBAT.md` | P1 |

### C. Màn hình — `screenshot` + `snapshot --raw`

| # | Lúc nào | Lấy gì | Đích |
|---|---|---|---|
| C1 | Menu chính | danh sách mode (3 chế độ), text | `DIFFICULTY_MODES.md` |
| C2 | Màn chọn stage | **chuỗi nhiệm vụ sao** (`Eliminate {0} enemies`) ở **từng mode** | `MISSIONS_STARS.md` — đối chiếu `pct` |
| C3 | Vào màn | HUD: HP bar `109/109`, stage, tiền | `UI.md`, `COMBAT.md` |
| C4 | Đang có wave | số enemy trên màn, formation | `ENCOUNTERS.md` |
| C5 | Boss | thanh máu boss, tên | `BOSSES.md` |

Mỗi ảnh chụp kèm `snapshot --raw` cùng lúc — **text trong XML là số liệu**, ảnh chỉ là bằng chứng.

### D. Log + số đo

| # | Lấy gì | Lệnh |
|---|---|---|
| D1 | `main` + `crash` buffer đầy đủ | `adb -s $serial logcat -b main -b crash -d` |
| D2 | Dòng mirror `RAMUSB\|` | `grep -a "RAMUSB|"` trên logcat package |
| D3 | fps / frame time | `/metrics` × 5 lần cách 2 s |
| D4 | ABI thật của thiết bị | `getprop ro.product.cpu.abilist` |

---

## 7. Chạy collector — **không viết lại**

Phần §6 đã được đóng gói thành script chạy được, **không cần agent suy luận**:

```bash
bash runtime-probe/collect.sh /duong/dan/to/windwings-mod.apk
```

Nó tự làm: kiểm APK → bật phiên → in `watchUrl` → mở adb tunnel → chờ `/health` (tối đa
180 s) → dump 3 lúc (menu / stage / ingame) → đọc `ui-*.xml` để bấm đúng nút → đóng băng
`timescale` khi dump → kiểm đầy đủ → in **ĐỦ** hoặc **THIẾU**.

Đặc tính quan trọng khi giao cho agent yếu:

| Tình huống | Hành vi |
|---|---|
| APK không có bridge | in `STOP:` và thoát, không bật phiên |
| `session start` fail | in `STOP:`, giữ nguyên `session.json` |
| `/health` không lên sau 180 s | in `STOP:`, không dump rỗng |
| Không tìm thấy nút để bấm | **không đoán toạ độ**, in danh sách `text=` rồi đi tiếp |
| Trial (không adb) | tự chuyển sang logcat + ảnh, và nói rõ *không có số liệu* |

Script **không** tự `session end` — phiên được giữ để người dùng xem, kết thúc bằng tay.

## 8. Kiểm tra đã đủ chưa — trước khi `session end`

```bash
python3 - "$OUT" <<'PY'
import json, pathlib, sys
out = pathlib.Path(sys.argv[1])
must = {
  "P0 statics": ["statics-ingame/Player_Get_Datas.json", "statics-ingame/Stage_Get_Datas.json",
                 "statics-ingame/Enemy_Get_Datas.json", "statics-ingame/Map_Get_Datas.json",
                 "statics-ingame/Device_Get_Data.json", "statics-ingame/Enemy_Data_Balance.json"],
  "P0 runtime": ["find/Player_Health.json", "find/Enemy_Sub.json"],
  "màn hình":   ["screen-menu.jpg", "screen-stage.jpg", "screen-ingame.jpg"],
  "log":        ["logcat-final.txt"],
  "handle":     ["session.json", "health.json"],
}
bad = 0
for group, files in must.items():
    for f in files:
        p = out / f
        ok = p.exists() and p.stat().st_size > 20
        if not ok:
            # một file "rỗng" và một file "không tồn tại" là hai lỗi khác nhau
            print(f"MISSING  [{group}] {f}")
            bad += 1
print("\nĐỦ" if bad == 0 else f"\nTHIẾU {bad} mục — đừng end session, chạy tiếp phần còn thiếu")
PY

grep -c '"fields"' "$OUT"/statics-ingame/*.json 2>/dev/null | grep -v ':0' || true
```

Chỉ `session end` khi in ra **ĐỦ**, hoặc khi đã ghi rõ lý do không lấy được (ví dụ: trial không
có adb).

---

## 9. Chuẩn hoá + luật viết tài liệu

Mỗi con số đưa vào `docs/` phải kèm **nguồn máy đọc được**:

```
pct[mode=1][slot=0] = 0.85   ← ramus/2026-10-24/statics-ingame/Player_Get_Datas.json · .fields.pct[1][0]
```

1. Tiếng Việt, thuật ngữ kỹ thuật giữ tiếng Anh.
2. Không có đường dẫn nguồn ⇒ **không phải số liệu**, không được viết.
3. Suy luận mở đầu bằng `> Nhận định:` và nói rõ **chưa** được chứng minh.
4. Mức bằng chứng: **A** = đo trực tiếp · **B** = suy ra từ dữ liệu đã có · **C** = suy đoán.
5. Cuối **mỗi** file tài liệu phải có `## Còn thiếu / phải đoán`.
6. Một lần đo không đủ để viết câu khẳng định tuyệt đối.
7. **Không** commit APK / DLL build / file > 5 MB. **Không** phát hành bản mod.
8. Chết/lỗi xảy ra **sau khi có người bấm tay trong phiên** không được dùng làm bằng chứng app lỗi.

---

## 10. Kết thúc

```bash
npx --yes "$RAMUS_CLI" screenshot --out "$OUT/screen-final.jpg" || true
npx --yes "$RAMUS_CLI" session end || true
ls -la "$OUT"
```

Bàn giao: `session.json`, `session-status.json`, `health.json`, `statics-*/`, `find/`, `core-*/`,
`screen-*.jpg`, `ui-*.xml`, `logcat-*.txt`, `failed.txt` (nếu có).

---

## Còn thiếu / phải đoán

- **Chưa xác nhận** bridge có mirror `/statics` vào logcat hay không. Nếu **không**, trial tuyệt
  đối không lấy được số ⇒ bắt buộc key mode. Đây là giả định, chưa đo.
- **Chưa xác nhận** danh sách type ở §6A là đủ: tên class lấy từ 111 typetree của bản
  `ef6b75ef`, nhưng một class có thể **không có static** hoặc tên khác lúc runtime.
- **Chưa biết** toạ độ các nút mode/stage/Play có ổn định giữa các lần chạy; §7 in `ui-select.xml`
  để opencode đọc text rồi tap, không hard-code.
- **Chưa đo** mất bao nhiêu giây từ `Start Load Scene` tới frame đầu tiên — §7 dùng `sleep 20`,
  con số này là **đoán**.
- Số field thật trong `Player_Get_Datas` (bao nhiêu mảng `pct`, mấy slot) **chưa chốt**; phải đọc
  từ JSON thật, không lấy từ tài liệu cũ.
