## Bàn giao: chạy probe từ tài khoản chính

Tài liệu này viết cho phiên/agent đang giữ **email chính** (nhánh `arena/ef6b75ef-…`).
Nhánh đó là nhánh nghiên cứu RE (53.676 file, `tools/verify/**`), **không** có harness
runtime — muốn chạy probe thì lấy code từ nhánh `arena/20330d0e-…`.

### Vì sao phải chạy từ phía tài khoản chính

| Việc | Phiên phụ (nhánh 20330d0e) | Tài khoản chính |
|---|---|---|
| `git push` | được | được |
| `workflow_dispatch` (bấm chạy tay) | **403** — `Resource not accessible by integration` | cần `Actions: write` |
| `gh secret set RAMUS_API_KEY` | **403** | cần quyền admin repo |
| Đọc `secrets` | **403** (không biết secret có tồn tại hay không) | — |

⇒ Chạy được bằng **push** (mỗi push tạo một run), hoặc bằng `workflow_dispatch` nếu
token của bạn có quyền Actions.

### 1. Lấy code

```bash
git fetch origin arena/20330d0e-windwings-space-shooter-game-p
git checkout -b probe arena/20330d0e-windwings-space-shooter-game-p
```

### 2. Hai chế độ

| | trial (mặc định, không cần secret) | key (`RAMUS_API_KEY`) |
|---|---|---|
| Thời lượng | 15 phút, 1 phiên | dài hơn |
| Dung lượng APK | ≤ 150 MB | không giới hạn ở mức này |
| adb | **không** | **có** (`adb forward tcp:8080`) |
| Đọc được | logcat, screenshot, UI tree | **+ HTTP bridge, `/scene`, `/statics`** |

Muốn có 3 mảng `pct` trong `Player_Get_Datas` (9 số cho 3 mode × 2 slot) thì **bắt buộc**
chế độ key + APK có bridge.

### 3. Kích hoạt

**Cách A — workflow_dispatch** (nếu có quyền):

```bash
gh workflow run ramus-probe.yml --ref probe \
  -f allow_no_bridge=true -f force_trial=false -f strict=false -f scenario=key-smoke
```

**Cách B — bằng push** (khi dispatch bị 403). Tạo file override một lần rồi push:

```bash
cat > runtime-probe/probe-inputs.json <<'JSON'
{ "allow_no_bridge": true, "force_trial": false, "strict": false, "scenario": "key-smoke" }
JSON
git add runtime-probe/probe-inputs.json && git commit -m "probe: một lượt" && git push -u origin probe
```

Xoá file đó sau khi chạy xong — mỗi lần push kèm file sẽ tiêu một phiên.

### 4. Đọc kết quả

- Comment trên PR, tìm marker `<!-- runtime-probe -->` (report) và `<!-- bridge-build -->`
  (ma trận build + self-test).
- Artifact `runtime-probe-<run_id>` chứa `summary.json`, `logcat.txt`, `screen-*.jpg`,
  `ui-*.json`, `ui-*.xml`.
- Bản lưu bằng chứng: `runtime-probe/results/2026-10-23-trial-abi-smoke.md`.

### 4b. Chạy "bridge anonymous" (trial + mirror logcat)

Điều kiện duy nhất: **APK phải chứa `RamusBridge.dll`**. Gate sẽ từ chối chạy nếu thiếu
(`bridge: no` trong inventory) — đó là hành vi đúng, không phải lỗi.

```json
{ "allow_no_bridge": false, "force_trial": true, "strict": true,
  "scenario": "bridge-anonymous" }
```

Kỳ vọng khi APK có bridge và máy chạy được app:

| Dấu hiệu | Ở đâu |
|---|---|
| `RAMUSB|{...}` trong logcat | `logcat.txt`, và mục *logcat evidence* của report |
| `verdict: ok`, `transport: logcat` | đầu report |
| `scene`, `rootCount`, `roots[].n` | bảng metric + `summary.json` |

Nếu report ghi `bridge-unreachable` + `RAMUSB lines: 0`, đọc tiếp mục *Did the app start*:
`activity started: no` ⇒ app chưa từng chạy (ABI/loader), **không phải** bridge hỏng.

Phân biệt "chạy thật" với "skip": artifact ~60 KB và có `session:` là chạy thật;
artifact ~3 KB, `session: n/a` là gate đã skip.

Đã chứng minh sẵn trong CI (không cần thiết bị): job `bridge build` có step
**Mirror contract test** — self-test sinh dòng `RAMUSB|` thật từ `CompactStateJson()`,
parser của probe đọc lại và phải ra `verdict=ok`, `transport=logcat`.

### 5. Đã biết trước — đừng tiêu phiên để hỏi lại

| Dữ kiện | Mức |
|---|---|
| Compile 4 loader thật + self-test HTTP | **A** — 5/5, 37/37 check, run `39921281530` |
| APK cài được trên Ramus (sau merge + ký) | **A** — nhiều lượt |
| APK **không** chứa `RamusBridge.dll` | **A** — inventory `bridge: no` |
| Trial chỉ trả logcat stream `system`; `--filter <package>` = 0 dòng | **A** — run `39925095796` |
| App không hề xuất hiện trong log/UI của phiên trial | **A** |
| Nguyên nhân app không chạy = ABI arm64 vs x86_64 | **B — giả thuyết**, chưa có `UnsatisfiedLinkError` |

**Điều duy nhất cần lấy:** một dòng log từ buffer `main`/`crash` nói rõ vì sao tiến trình
chết, hoặc xác nhận nó **không** chết khi chạy trên arm64.

### 6. Ba đường, xếp theo chi phí

1. **Key mode + `adb logcat`** — cùng APK, cùng thiết bị, khác transport:
   ```bash
   npx ramus-cli adb            # tunnel
   adb -s <serial> logcat -b main,crash -d | grep -iE 'wind|unity|il2cpp|dlopen|Unsatisfied'
   ```
2. **Thiết bị/emulator arm64 thật** — nếu chạy được thì giả thuyết ABI bị bác bỏ.
3. **Build Unity x86_64** chỉ để test (`Unity 2022.3` hỗ trợ) — không phát hành.

### 7. Giới hạn phải nói kèm

APK **không** có bridge ⇒ mọi kết quả từ đường này chỉ nói về việc app có khởi động,
**không** nói gì về `/scene`, `/statics` hay 9 số `pct`. Đừng đọc report thành "harness
hỏng": harness đã compile + self-test đúng; thiếu là thiếu **DLL trong APK**, và game là
IL2CPP nên phải qua **patcher của loader**, không chỉ copy `Mods/`.
