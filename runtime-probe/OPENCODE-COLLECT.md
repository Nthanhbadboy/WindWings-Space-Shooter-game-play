# Runbook cho opencode — thu thập dữ liệu in-game qua Ramus

> **Đối tượng đọc:** một agent (opencode) không có ngữ cảnh của cuộc trao đổi trước.
> Mọi thứ cần thiết phải nằm trong file này. Làm đúng thứ tự, không sáng tạo thêm.
>
> **Đầu vào:** một **APK mod đã chạy được ở máy local** (đã có `RamusBridge.dll` bên trong,
> mở cổng 8080). Không dùng APK gốc từ release: bản gốc **không có bridge**, chạy lên cũng
> không đọc được `/statics`.
>
> **Đích:** lấp các ô còn trống trong `docs/spec/` bằng số đo thật, mỗi số ghi rõ nguồn.

---

## 0. Ba giới hạn quyết định cách làm

| Giới hạn | Hệ quả |
|---|---|
| Trial Ramus: 15 phút, **không có adb** | `http://127.0.0.1:8080` **không gọi được**. Chỉ đọc được dòng `RAMUSB\|{json}` trong logcat + chụp màn hình. |
| Key mode (`RAMUS_API_KEY`): có adb | `adb forward` rồi `curl` được toàn bộ HTTP API, gồm `/statics`. **Đây là đường duy nhất lấy được số.** |
| Trial giới hạn APK ≤ 150 MB | Kiểm kích thước **trước** khi bật phiên, đừng để phiên chết vì lý do biết trước. |

**Quy tắc vàng:** cái gì HTTP lấy được thì lấy bằng HTTP. Logcat chỉ là đường dự phòng để
chứng minh *app có chạy*, không phải nguồn số liệu.

---

## 1. Biến môi trường

```bash
set -euo pipefail
export RAMUS_CLI="ramus-cli@0.1.17"

# Đường dẫn APK mod đã chạy được ở local. Sửa đúng file bạn có.
export MOD_APK="$PWD/.ci/apk/windwings-mod.apk"

# Ngày chạy, dùng để đặt tên thư mục kết quả.
export RUN_DATE="$(date +%F)"
export OUT="docs/apk-analysis/ramus/$RUN_DATE"
mkdir -p "$OUT"
```

Nếu chưa có key mà chỉ muốn kiểm tra app có chạy:

```bash
npx --yes "$RAMUS_CLI" trial --force        # key ẩn danh 15 phút
npx --yes "$RAMUS_CLI" status               # phải thấy "key" khác "missing"
```

Nếu có key thật thì đặt `export RAMUS_API_KEY=...` **trong shell**, không ghi vào file nào
trong repo, không echo ra log.

---

## 2. Kiểm tra APK trước khi tốn một phiên

```bash
ls -l "$MOD_APK"
sha256sum "$MOD_APK" | tee "$OUT/apk-sha256.txt"

# Kích thước: trial chỉ nhận ≤ 150 MB.
python3 - "$MOD_APK" <<'PY'
import os, sys
n = os.path.getsize(sys.argv[1])
print(f"{n} bytes = {n/1048576:.1f} MB")
print("OK cho trial" if n <= 150*1048576 else "QUÁ 150 MB — trial sẽ từ chối, dùng key mode")
PY

# Bridge phải nằm trong APK, nếu không thì mọi bước sau vô nghĩa.
unzip -l "$MOD_APK" | grep -iE "RamusBridge\.dll|BepInEx/|MelonLoader/" | head
```

- Không thấy `RamusBridge.dll` ⇒ **dừng lại**, báo lại: đây không phải bản mod.
- APK > 150 MB và không có key ⇒ chỉ chạy được phần "kiểm tra app có chạy" (mục 5).

---

## 3. Bật phiên

```bash
npx --yes "$RAMUS_CLI" session start --apk "$MOD_APK" --wait --timeout 600 \
  | tee "$OUT/session.json"
```

CLI trả JSON dạng:

```json
{ "session": "<uuid>", "status": "active", "watchUrl": "https://ramus.dev/share#...", "idleTtlSec": 600 }
```

Lưu lại ngay:

```bash
SID=$(jq -r 'if (.session|type)=="string" then .session else (.sessionId // .id // empty) end' \
        "$OUT/session.json")
echo "session=$SID"
npx --yes "$RAMUS_CLI" session status | tee "$OUT/session-status.json"
```

> `watchUrl` là link cho **người** xem/tự bấm trên trình duyệt, hiệu lực 72 giờ. In nó ra cho
> user ngay, đừng giữ lại một mình.

Nếu `session start` fail 3 lần: dừng, ghi `session.json` + thông báo lỗi, không thử tiếp.

---

## 4. Key mode — mở tunnel rồi gọi HTTP

Bỏ qua mục này nếu đang ở trial (không có adb).

```bash
# 1) CLI in ra serial của thiết bị và dựng cầu adb.
out=$(npx --yes "$RAMUS_CLI" adb --port 5555 2>&1 | tee "$OUT/adb.txt")
serial=$(printf '%s\n' "$out" | grep -oE '(emulator-[0-9]+|[0-9]{1,3}(\.[0-9]{1,3}){3}:[0-9]+)' | head -1)
[ -n "$serial" ] || serial=$(adb devices | awk 'NR>1 && $2=="device"{print $1; exit}')
echo "serial=$serial"

# 2) Cổng 8080 của máy này → cổng 8080 trong game.
adb -s "$serial" forward tcp:8080 tcp:8080

# 3) Bằng chứng bridge sống.
curl -fsS --max-time 10 http://127.0.0.1:8080/health | tee "$OUT/health.json" | jq
```

Nếu `/health` không trả 200:

```bash
adb -s "$serial" shell pidof com.Wind.wings.Space.Shooter     # tiến trình còn sống?
adb -s "$serial" logcat -b main -b crash -d > "$OUT/main-crash-logcat.txt"
adb -s "$serial" shell monkey -p com.Wind.wings.Space.Shooter -c android.intent.category.LAUNCHER 1
sleep 20 && curl -fsS http://127.0.0.1:8080/health | jq
```

Vẫn không lên ⇒ ghi lại, chuyển sang mục 5 để ít nhất chứng minh app có chạy.

### Bộ lệnh HTTP cần gọi (key mode)

```bash
B=http://127.0.0.1:8080
for p in health state metrics "scene?max=200" "hierarchy?depth=3&max=1500" "logs?n=150"; do
  f=$(echo "$p" | tr '/?&=.' '_')
  curl -fsS --max-time 20 "$B/$p" -o "$OUT/$f.json" || echo "FAIL $p" >> "$OUT/failed.txt"
done
curl -fsS "$B/screenshot" -o "$OUT/screen-ingame.png" || true
```

---

## 5. Trial (hoặc khi HTTP chết) — đọc logcat + chụp màn hình

```bash
PKG=com.Wind.wings.Space.Shooter

npx --yes "$RAMUS_CLI" app launch || true
sleep 10

# Ảnh: phải có ít nhất 3 khung, cách nhau vài giây, để thấy màn hình ĐỔI.
for i in 0 1 2; do
  npx --yes "$RAMUS_CLI" screenshot --out "$OUT/screen-$i.jpg" --max-width 720
  sleep 8
done

# Dòng mirror của bridge (nếu có).
npx --yes "$RAMUS_CLI" logcat --limit 500 --filter "$PKG" > "$OUT/logcat-package.txt" || true
npx --yes "$RAMUS_CLI" logcat --limit 500 > "$OUT/logcat-raw.txt" || true
grep -a "RAMUSB|" "$OUT/logcat-package.txt" > "$OUT/ramus-mirror.txt" || true
wc -l "$OUT/ramus-mirror.txt"
```

Cách đọc kết quả:

- `screen-00` và `screen-01` **giống hệt nhau** (cùng SHA-256) ⇒ màn hình đứng yên: hoặc đang
  load, hoặc đang kẹt. Chưa kết luận được gì.
- `logcat-package.txt` có `I/Unity: Start Load Scene` ⇒ game **đã yêu cầu nạp scene**. Không
  đồng nghĩa nạp xong.
- **Không** dùng lần chết nào xảy ra sau khi có người bấm/chỉnh tay trong phiên làm bằng chứng
  app lỗi. Ghi rõ "do thao tác tay" nếu biết.

Hộp thoại chặn đường (immersive "Got it", consent của game "Continue"):

```bash
npx --yes "$RAMUS_CLI" snapshot --raw > "$OUT/ui-0.xml"     # đọc text= để biết nút nào
npx --yes "$RAMUS_CLI" tap 0.856,0.259 --expect-gone "Got it"   # toạ độ chuẩn hoá 0..1
```

`snapshot` có thể trả `Cannot read properties of null (reading 'length')` đúng lúc cây UI đang
đổi — **thử lại 2 lần cách 1,5 giây** trước khi coi là màn hình trống.

---

## 6. Dữ liệu phải lấy (đây là mục đích của cả runbook)

Gọi từng loại, lưu **nguyên văn JSON**, không cắt bớt:

```bash
for t in Player_Get_Datas Stage_Get_Datas Enemy_Get_Datas; do
  curl -fsS "http://127.0.0.1:8080/statics?type=$t&max=200" -o "$OUT/statics-$t.json" \
    || echo "FAIL statics $t" >> "$OUT/failed.txt"
  jq -r '"\(.type // "?"): \(.written // 0) field(s)"' "$OUT/statics-$t.json" 2>/dev/null || true
done
```

| Loại | Dùng để lấp | Ghi chú |
|---|---|---|
| `Player_Get_Datas` | `docs/spec/MISSIONS_STARS.md` — các mảng `pct` đang trống | Đọc `pct` từng mode; **không** suy ra số nào không có trong JSON |
| `Stage_Get_Datas` | `levelDelta` (hệ số thưởng theo mode) | |
| `Enemy_Get_Datas` | HP gốc từng enemy | Đối chiếu `docs/apk-analysis/*.csv`; lệch thì ghi cả hai, không chọn một |

Ngoài ra, khi đang ở màn chơi, ghi lại **một** ảnh HUD rõ nét + text trên màn hình
(`snapshot --raw` → các `text=`) để đối chiếu với số trong CSV.

---

## 7. Chuẩn hoá kết quả

```bash
# Một bảng duy nhất, mỗi dòng một số đo và nguồn của nó.
jq -n --arg sid "$SID" --slurpfile p "$OUT/statics-Player_Get_Datas.json" \
      '{session:$sid, player:($p[0] // null)}' > "$OUT/extract-player.json"
```

Mỗi số khi đưa vào `docs/` phải kèm **đường dẫn tới file JSON + đường dẫn `jq`**, ví dụ:

```
pct[mode=1][slot=0] = 0.85   ← ramus/2026-10-24/statics-Player_Get_Datas.json · .fields.pct[1][0]
```

Không có đường dẫn đó thì **không phải số liệu**, chỉ là trí nhớ.

---

## 8. Luật viết tài liệu

1. Tiếng Việt, thuật ngữ kỹ thuật giữ tiếng Anh.
2. Mỗi con số ghi nguồn như mục 7. Không nguồn ⇒ không viết.
3. Suy luận phải mở đầu bằng `> Nhận định:` và nói rõ nó **chưa** được chứng minh.
4. Phân mức bằng chứng: **A** = đo trực tiếp, **B** = suy ra từ dữ liệu đã có, **C** = suy đoán.
5. Cuối **mỗi** file tài liệu phải có mục `## Còn thiếu / phải đoán`.
6. Không viết câu khẳng định tuyệt đối khi mới có một lần đo.
7. **Không** commit APK, DLL build, hay file > 5 MB vào repo.
8. **Không** đăng tải/phát hành APK mod ở bất kỳ đâu; chỉ dùng trong phiên Ramus.

---

## 9. Kết thúc phiên

```bash
npx --yes "$RAMUS_CLI" screenshot --out "$OUT/screen-final.jpg" 2>/dev/null || true
npx --yes "$RAMUS_CLI" session end || true
ls -la "$OUT"
```

Bàn giao gồm:

- `session.json`, `session-status.json` — phiên nào, chế độ nào, hết hạn khi nào;
- `health.json` + các `*.json` HTTP (key mode) **hoặc** `logcat-*.txt` + `screen-*.jpg` (trial);
- `statics-*.json` — nguyên văn, không sửa;
- danh sách `failed.txt` nếu có lệnh hỏng.

---

## Còn thiếu / phải đoán

- **Chưa có bằng chứng** rằng bản mod của bạn chứa bridge đúng phiên bản đang dùng trong
  `.github/` — kiểm bằng `sha256sum` + so với `dist/` trước khi tin kết quả `/statics`.
- **Chưa rõ** bridge có mirror `/statics` vào logcat hay không. Nếu **không**, trial tuyệt đối
  không lấy được số ⇒ phải có key mode. Đây là giả định, chưa đo.
- Số field trong `Player_Get_Datas` (bao nhiêu mảng `pct`, mỗi mảng bao nhiêu slot) là **chưa
  xác nhận** trong runbook này; phải đọc từ JSON thật, không lấy từ tài liệu cũ.
- Chưa biết toạ độ nút consent của game có ổn định giữa các lần chạy hay không.
