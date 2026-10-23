# runtime-probe — cầu nối trạng thái trong game + CI trên Ramus

Bộ này gồm hai nửa:

| Nửa | File | Việc nó làm |
|---|---|---|
| **Trong APK** | `RamusBridge.cs` (+ `Adapters/*`) | HTTP server nhúng chạy trong tiến trình game, trả scene / hierarchy / component / static field / log / ảnh chụp qua cổng 8080 |
| **Ngoài CI** | `.github/workflows/ramus-probe.yml`, `.github/scripts/ramus-probe.mjs` | Bật emulator cloud bằng Ramus, cài APK, gọi server, chụp màn hình, xuất `report.md` + `summary.json` |

Mục tiêu: kiểm thử **hộp trắng** — không chỉ nhìn pixel mà đọc được *scene nào đang chạy, object nào tồn tại, field static nào bằng bao nhiêu* — trên một thiết bị Android thật, mỗi lần push.

> Chỉ dùng với **APK do bạn tự build hoặc có quyền kiểm thử**. Repo này không phát hành APK mod.

---

## 1. Kiến trúc

```
┌────────────────────────── Android device / Ramus VM ──────────────────────────┐
│  Unity 2022.3.62f3 · IL2CPP · arm64                                            │
│                                                                                │
│   RamusBridge.dll (plugin)                                                     │
│     ├─ Bridge.Init()        ← loader adapter gọi (BepInEx6 / BepInEx5 / Melon)  │
│     ├─ TcpListener :8080    ← luồng nền, HTTP/1.1 tự parse, JSON tự ghép        │
│     ├─ ConcurrentQueue      ← mọi lệnh Unity được đẩy về main thread            │
│     ├─ BridgeHost.Update()  ← bơm queue + đo fps/frame + mirror logcat          │
│     └─ Debug.Log("RAMUSB|{json}")  ← đường dự phòng khi không có adb            │
└──────────────────────────────────────┬─────────────────────────────────────────┘
                    adb forward tcp:8080 │ logcat "RAMUSB|{json}"
┌──────────────────────────────────────┴─────────────────────────────────────────┐
│ GitHub Actions                                                                  │
│   npx ramus-cli trial                                (anonymous, không cần key) │
│   npx ramus-cli session start --apk app.apk --wait                              │
│   npx ramus-cli screenshot / snapshot / tap / logcat                            │
│   node .github/scripts/ramus-probe.mjs  → report.md + summary.json + JPEG/PNG   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

Ba quyết định kỹ thuật quan trọng:

1. **Không dùng `HttpListener`** — nó ném `PlatformNotSupportedException` trên nhiều cấu hình IL2CPP/Android. `TcpListener` thuần + parser HTTP/1.1 tối giản luôn chạy.
2. **Không dùng `Newtonsoft.Json` hay `JsonUtility`** — `JsonUtility` không serialize `Dictionary`, còn kéo Newtonsoft vào làm plugin nặng thêm và dễ xung đột assembly với game. Một writer ~80 dòng là đủ.
3. **Mọi truy cập Unity API đi qua main thread** — object IL2CPP không thread-safe; đọc `Transform` từ luồng HTTP có thể crash native. `Bridge.OnMain()` gói lệnh vào queue, `BridgeHost.Update()` bơm mỗi frame, timeout 2–8 s.

---

## 2. So sánh tool trên GitHub (điều tra 23/10/2026)

| Tool | ★ | Trạng thái | Dùng được cho game này? | Vai trò ở đây |
|---|---|---|---|---|
| [`All-Of-Us-Mods/FusionCore`](https://github.com/All-Of-Us-Mods/FusionCore) | 34 | push 17/10/2026 | **Có** — BepInEx 6 fork cho Android IL2CPP, .NET 10, tự tải `libunity.so` unstripped | **Khuyến nghị chính** (adapter `BepInEx6`) |
| [`NextBep/BepInEx.Android.Launcher`](https://github.com/NextBep/BepInEx.Android.Launcher) | 12 | push 18/10/2026 | Có — launcher + quản lý modpack, arm64-v8a | Thay thế; README của họ **khuyên dùng FusionCore** |
| [`LemonLoader/MelonLoaderInstaller`](https://github.com/LemonLoader/MelonLoaderInstaller) | 26 | — | Có — MelonLoader cho Android, cần patch APK | Adapter `MelonLoader` |
| [`Tb1281/BepInEx-Android`](https://github.com/Tb1281/BepInEx-Android) | 0 | push 22/10/2026 | Chưa chứng minh — CoreCLR-hosting, provenance-gated CI | Không chọn (0★, chưa có release ổn định) |
| [`vfsfitvnm/frida-il2cpp-bridge`](https://github.com/vfsfitvnm/frida-il2cpp-bridge) | 1764 | ổn định | Có — dump/trace/hijack IL2CPP runtime, **không cần `global-metadata.dat`** | Phương án **không nhúng plugin** khi loader fail |

Kết luận: **không có tool nào "ngon hơn" để thay thế cả hai nửa**. Ramus lo phần thiết bị (cloud emulator + UI tree + screenshot), FusionCore/BepInEx lo phần nhúng, còn `frida-il2cpp-bridge` là lưới an toàn. Vì vậy bridge được viết **độc lập loader** (`RamusBridge.cs` không `using` BepInEx/Melon) và có 3 adapter mỏng.

> Nhận định: nếu FusionCore không chạy được trên build này (Unity 2022.3.62f3), đường lui là Frida + `Java.perform` gắn gadget, khi đó chỉ mất phần HTTP trong tiến trình chứ không mất kịch bản CI.

---

## 3. Build

### 3.1 Kiểm nhanh không cần Unity (đã chạy trong CI — compile **và** self-test runtime)

```bash
# 1. stub UnityEngine (assembly identity 0.0.0.0)
dotnet build runtime-probe/BuildCheck/UnityStubs.csproj -c Release -p:OutDir=.ci/refs/unity-stub/

# 2. type-check bridge
dotnet build runtime-probe/RamusBridge.csproj -c Release \
  -p:Loader=Core -p:StubUnity=true -p:UnityStubDir=.ci/refs/unity-stub -p:Tfm=netstandard2.1

# 3. self-test: boot server thật rồi gọi từng endpoint
dotnet run --project runtime-probe/SelfTest/RamusBridge.SelfTest.csproj \
  -p:UnityStubDir=.ci/refs/unity-stub
```

`BuildCheck/UnityStubs.cs` thay cho `UnityEngine` ⇒ chứng minh bridge type-check đúng;
self-test chứng minh HTTP/JSON/hàng đợi main-thread chạy được.
Chạy đủ 5 target (kèm DLL loader thật + self-test) bằng:

```bash
./.github/scripts/build-bridge.sh --out dist --refs .ci/refs
# dist/core/ dist/bepinex6/ dist/melon/ dist/bepinex5/  (+ inventory.txt)
```

### 3.2 Build cho máy có Unity

Yêu cầu: .NET SDK 8/9 (`dotnet --version`), quyền truy cập thư mục cài của loader.

```bash
# FusionCore / BepInEx 6 (Android IL2CPP)
./runtime-probe/build.sh BepInEx6 "/đường/dẫn/BepInEx"

# MelonLoader / LemonLoader
./runtime-probe/build.sh MelonLoader "/đường/dẫn/MelonLoader"

# BepInEx 5 (bản Mono, dùng để thử trên PC trước)
./runtime-probe/build.sh BepInEx5 "/đường/dẫn/Managed"
```

(tương đương `dotnet build runtime-probe/RamusBridge.csproj -c Release -p:Loader=… -p:<Root>=…`)

Kết quả: `runtime-probe/bin/Release/netstandard2.1/RamusBridge.dll`
(hoặc `net6.0` nếu bạn ép `-p:TargetFramework=net6.0`).

- Với **BepInEx 6 IL2CPP**, `BepInEx/interop/` phải đã được sinh (chạy game một lần với bất kỳ plugin nào). Build lần đầu trước khi có interop sẽ lỗi thiếu `UnityEngine.CoreModule`.
- Với **MelonLoader**, `Il2CppInterop` nằm trong thư mục cài MelonLoader; nếu bản của bạn đặt tên khác, truyền `-p:MelonInteropDir=...`.
- `netstandard2.1` là mặc định; Unity 2022.3 hỗ trợ tốt. Có thể ép `-p:TargetFramework=net6.0` cho FusionCore.

### Cài

1. Copy `RamusBridge.dll` vào `BepInEx/plugins/` (hoặc `Mods/` của MelonLoader).
2. Copy `ramus-bridge.ini.example` → `ramus-bridge.ini` cạnh DLL nếu muốn đổi cổng/token.
3. Khởi động game, xem log:
   ```
   [RamusBridge] listening on http://127.0.0.1:8080
   ```
4. Trên máy có adb:
   ```bash
   adb forward tcp:8080 tcp:8080
   curl -s http://127.0.0.1:8080/health | jq
   ```

---

## 4. API

Mặc định bind `127.0.0.1` — chỉ vào được qua `adb forward`. Đặt `token=` trong ini thì mọi request phải kèm `X-Ramus-Token: <token>` hoặc `?token=<token>`.

| Method | Path | Trả về |
|---|---|---|
| GET | `/health` | scene, fps, frame, uptime, unity version, timeScale, avg/max frame |
| GET | `/state` | thêm device, OS, RAM, GPU, quality, độ phân giải |
| GET | `/scene?max=200` | scene hiện tại + root GameObject (tên, active, tag, layer, component) |
| GET | `/hierarchy?depth=3&max=1500` | cây object có giới hạn node |
| GET | `/find?name=Sub&max=50` | tìm theo tên, **có cả object inactive**, kèm path đầy đủ |
| GET | `/statics?type=Stage_Datas&max=200` | field static public/private của type game (qua reflection) |
| GET | `/logs?n=150` | ring buffer 500 dòng `Debug.Log` (bắt cả log từ thread khác) |
| GET | `/metrics` | fps, avg/max frame time |
| GET | `/screenshot` | PNG từ `ScreenCapture` (≤ 6 MB; ảnh lớn dùng `ramus screenshot`) |
| GET | `/wait?scene=Name&timeout=30000` | chặn tới khi scene đổi — dùng để đồng bộ CI |
| POST | `/timescale?v=0.5` | đổi `Time.timeScale` (0 = pause để chụp ảnh ổn định) |
| POST | `/quit` | `Application.Quit()` |
| POST | `/mark?name=x` | ghi `RAMUSB-MARK\|x` vào logcat |

Ví dụ:

```bash
curl -s 'http://127.0.0.1:8080/find?name=Sub&max=5' | jq '.objects[] | {name, path, components}'
curl -s 'http://127.0.0.1:8080/statics?type=Stage_Datas' | jq '.fields'
curl -s -X POST 'http://127.0.0.1:8080/timescale?v=0' && curl -s http://127.0.0.1:8080/screenshot -o paused.png
```

`/statics` chỉ đọc field **primitive / string / array ≤ 64 phần tử**. Không có endpoint eval, không ghi vào game — bề mặt tấn công giữ ở mức đọc.

---

## 5. Đường logcat (bắt buộc cho trial)

Ramus trial **không có adb tunnel**, nên HTTP trong tiến trình không gọi được từ CI. Bridge vẫn ghi logcat:

```
I/Unity: RAMUSB|{"ok":true,"scene":"Ingame","frame":1234,"fps":59.8,"ts":1,"uptime":92.4,
                 "unity":"2022.3.62f3","rootCount":31,
                 "roots":[{"n":"Main Camera","a":true},{"n":"Sub_Player","a":true}, …]}
```

- Ghi **ngay frame đầu** và **mỗi lần đổi scene**, sau đó mỗi `mirror` giây (mặc định 10).
- `mirror_roots=12` quyết định bao nhiêu root object được kèm theo (0 = tắt).
- Một dòng bị cắt ở 3.500 ký tự để không làm nghẹt logcat.

CI đọc bằng `npx ramus-cli logcat --limit 500` (CLI từ chối > 500), tách các dòng
`RAMUSB|`, parse JSON, ghi vào `summary.json` (`transport: "logcat"`).

> **`ramus logcat` trả JSON, không trả text.** Định dạng thật, đọc từ log của lượt
> chạy `39923633849`:
>
> ```json
> { "lines": [ { "stamp": "08:20:44", "stream": "system",
>                "text": "I/ActivityTaskManager: Displayed com.Wind.wings.Space.Shooter/…" } ] }
> ```
>
> Bản đầu của `ramus-probe.mjs` regex trên **chuỗi JSON thô** ⇒ histogram tag ra
> một rổ `other` 2.502 dòng, và bảng "did the app start" chỉ so khớp được tình cờ.
> Đã sửa: parse `.lines[].text` rồi mới chạy regex; chấp nhận cả text thuần cho CLI cũ.
> Lượt đó trả 2.504 dòng và **không** có dòng nào chứa `com.Wind.wings.Space.Shooter`.

---

## 6. CI trên Ramus

### 📦 APK đã có sẵn trong repo

Repo có **draft release** `windwings-apk-1.3.118` với một asset duy nhất:

| | |
|---|---|
| File | `windwings.xapk` |
| Kích thước | **142.125.649 B** (≈ 135,5 MiB) |
| Định dạng | **XAPK** = zip chứa `base.apk` (+ config splits / OBB nếu có) |
| Truy cập | draft ⇒ cần token có `contents: write` để đọc |

Vì là XAPK chứ không phải APK, `.github/scripts/prepare-apk.sh` mở gói trước khi Ramus thấy nó:

```bash
.github/scripts/prepare-apk.sh --source release:windwings-apk-1.3.118 --out .ci/apk
# .ci/apk/base.apk          → tham số --apk của `ramus session start`
# .ci/apk/splits/*.apk      → cài bằng `adb install-multiple` (chỉ chế độ key)
# .ci/apk/obb/              → đẩy bằng `adb push` (chỉ chế độ key)
# .ci/apk/apk-inventory.txt → mỗi APK: size, manifest, lib arm64, Unity data
```

Script nhận cả 4 kiểu nguồn và **không đoán bừa**: nó liệt kê mọi `.apk` trong gói, chọn `base.apk`
(hoặc file lớn nhất), phần còn lại xếp vào `splits`. Inventory được đẩy lên artifact nên nếu bản
XAPK này có split thì bạn thấy ngay tên và kích thước.

Chọn nguồn theo thứ tự: input `apk_source` → biến `RAMUS_APK_SOURCE` → `runtime-probe/app.apk`
→ **auto-dò release có chữ `apk` trong tag**. Không cần cấu hình gì thêm.

> ⚠️ **Đừng publish release này.** Repo đang public; publish = phát hành lại game cho toàn thế giới.
> Giữ ở dạng draft, cấp `contents: write` cho job là đọc được. Nếu không muốn cấp quyền đó, đặt
> biến `RAMUS_APK_SOURCE` trỏ tới URL/đường dẫn khác.

> Nhận định: 135,5 MiB nằm dưới trần 150 MB của trial nên **chạy anonymous được ngay**. Rủi ro duy
> nhất là nếu `base.apk` bên trong cần `config.arm64_v8a.apk` đi kèm (Unity xuất AAB hay tách `.so`
> theo ABI) — lúc đó trial chỉ cài được base và app có thể crash vì thiếu native lib; artifact
> `apk-inventory.txt` cho biết ngay, và chế độ key (`adb install-multiple`) xử lý được.

### 🔑 Nạp key an toàn (đọc trước)

Key Ramus có dạng `rms_…` và **mở toàn bộ tài khoản Ramus của bạn**. Ba luật:

1. **Không dán key vào chat, issue, PR hay commit.** Nếu đã dán ở đâu → vào
   <https://ramus.dev/settings> **revoke và tạo key mới** trước khi làm bất cứ việc gì khác.
2. Chỉ đưa key vào **GitHub Actions secret**:
   ```bash
   gh secret set RAMUS_API_KEY          # dán khi được hỏi, không lưu vào shell history
   # hoặc: Settings → Secrets and variables → Actions → New repository secret
   ```
3. Repo có **chốt chặn**: job `preflight` chạy `git grep -nE 'rms_[A-Za-z0-9_-]{20,}'` và
   **fail** nếu phát hiện key trong cây làm việc.

Workflow **không bao giờ** echo key ra log: nó chỉ `export` vào `$GITHUB_ENV`, còn `ramus status`
là bước kiểm key sớm (key sai ⇒ fail ngay với hướng dẫn rotate).

> Nhận định: key từng xuất hiện trong transcript chat nên được coi là **đã lộ**. Rotate rồi
> `gh secret set` lại là việc 2 phút; bỏ qua thì bất kỳ ai đọc log cũng điều khiển được
> emulator và APK upload của bạn.

### Hai chế độ

| | **Anonymous (mặc định)** | **Signed-in key** |
|---|---|---|
| Chuẩn bị | không cần gì | secret `RAMUS_API_KEY` |
| Credential | `ramus trial` mint tại chỗ, **15 phút** | key dài hạn |
| Session | 1 session đồng thời | theo hạn mức tài khoản |
| APK | **≤ 150 MB** | theo hạn mức tài khoản |
| `adb` | **không** | có → `adb forward` |
| Đường dữ liệu | logcat `RAMUSB\|` | HTTP + logcat |
| Lấy được | scene, fps, frame, timeScale, uptime, `rootCount` + tên root, screenshot, UI tree | tất cả trên + `/hierarchy`, `/find`, component, `/statics` |
| Comment PR | có (do `gh`, không phải Ramus) | có |

Workflow tự chọn: có secret ⇒ key; không có ⇒ trial. Muốn **ép** trial dù có key (để kiểm chính đường anonymous): `force_trial: true`.

### Ngân sách 15 phút của trial

| Bước | Thời gian thực tế |
|---|---|
| mint trial | ~2 s |
| upload APK + boot VM (`session start --wait`) | 2–4 phút (APK 100 MB) |
| `wait --stable` + screenshot đầu | 30–60 s |
| probe (logcat wait + screenshot + UI tree) | 1,5–2 phút |
| share link + `session end` | ~15 s |
| **tổng** | **≈ 5–7 phút** |

Vẫn dư, nhưng ba thứ ăn thời gian nhất nên tránh: APK sát 150 MB, `taps` dài, và `--wait-server` lớn (script đã tự đặt 5 s ở chế độ trial).

### Bí mật / biến

| Tên | Loại | Bắt buộc | Ý nghĩa |
|---|---|---|---|
| `RAMUS_API_KEY` | secret | Không | Bỏ trống ⇒ tự chạy anonymous. Có ⇒ bật adb + HTTP + `/statics`. **Không dán vào chat/URL**; rotate tại ramus.dev/settings nếu đã lộ. |
| `RAMUS_APK_SOURCE` | repo variable | Không | Ghi đè nguồn APK: đường dẫn, `https://…`, hoặc `release:<tag>`. Bỏ trống ⇒ auto-dò release trong repo |

Không có APK ⇒ job `preflight` tắt job `probe` kèm notice, CI không đỏ.

### Chạy

```bash
# anonymous (không cần secret)
# mặc định: dùng draft release có sẵn trong repo
gh workflow run runtime-probe.yml -f scenario=anonymous

# có key: bật HTTP + dump field static của các class game
gh workflow run runtime-probe.yml -f statics="Stage_Datas,Player_Get_Datas,Enemy_Get_Datas,Stage_Get_Datas" -f wait_scene=Ingame

# nguồn khác
gh workflow run runtime-probe.yml -f apk_source="https://…/app.apk"
gh workflow run runtime-probe.yml -f apk_source="release:my-other-tag"

# kèm kịch bản bấm + đợi scene (đợi scene chỉ có tác dụng ở chế độ key)
gh workflow run runtime-probe.yml -f apk_url="https://…/app.apk" -f taps="0.5,0.82 0.5,0.82" -f wait_scene=Ingame
```

Hoặc đặt APK sẵn ở `runtime-probe/app.apk` (đã `.gitignore`) và bấm Run.

Workflow làm tuần tự:

1. `preflight` — chọn APK + chế độ, không cần secret.
2. `Prepare APK` — mở XAPK/APKS, tách `base.apk` + splits + OBB, in inventory và sha256;
   **chặn nếu base > 150 MB ở chế độ trial**.
3. `Credentials` — key: export; trial: `ramus trial --force`, lưu `expiresAt` + `limits`.
4. `session start --apk … --wait --timeout 600`, thử 3 lần, lưu `session.json`.
5. `wait --stable` + screenshot màn hình đầu.
6. `adb forward`, `adb install-multiple` (nếu có splits) và `adb push` OBB **chỉ ở chế độ key**;
   trial ghi chú rõ "no-adb".
7. Bấm kịch bản (`taps`).
8. `ramus-probe.mjs` — HTTP nếu có, không thì logcat; tính `verdict`; ghi `report.md`, `summary.json`.
9. Ảnh + watch link + artifact `runtime-probe-<run_id>` (14 ngày).
10. Comment `report.md` vào PR (nếu là PR).
11. `session end` — luôn chạy.

### `/statics` đóng được gì cho chính project này

`/statics?type=Player_Get_Datas` trả **field static thật trong bộ nhớ**, trong đó có 3 mảng
`pct` (3 mode × 2 slot) — đúng 9 con số mà phân tích tĩnh từ `docs/spec/` **chưa lấy được**
(RVA chưa resolve, `debug_rva` chỉ 2/1.929). Chạy harness một lần ở chế độ key là có dữ liệu runtime
để đối chiếu với `MISSIONS_STARS.md` §"Còn thiếu / phải đoán", không cần suy luận thêm.

Tương tự `Stage_Get_Datas.levelDelta` (hệ số nhân theo mode) và `Enemy_Get_Datas` (HP gốc)
đều là field static ⇒ đọc trực tiếp được khi game đã load xong.

> Nhận định: reflection qua `Il2CppInterop` có thể trượt với `Il2CppArrayBase<float>` tuỳ phiên
> bản interop. Nếu `/statics` trả `written` thấp bất thường, kiểm `logs` của bridge trước khi
> kết luận field không tồn tại.

### Đọc kết quả

`report.md` có bảng metric + root object + static field (nếu có HTTP) + ghi chú + lỗi. `summary.json` giữ nguyên payload.

`verdict`:

| Giá trị | Nghĩa |
|---|---|
| `ok` | có dữ liệu, fps ≥ 20 |
| `degraded` | có dữ liệu nhưng fps < 20 |
| `bridge-unreachable` | không HTTP, không logcat → plugin chưa nạp hoặc app chưa chạy |
| `app-unstable` | log có dấu hiệu crash/died |
| `error` | script lỗi |

`--strict` (mặc định bật) chỉ fail job khi **không có dữ liệu nào**; fps thấp chỉ là cảnh báo.

### Chạy tay toàn bộ quy trình (không cần CI)

Dùng khi muốn thử ngay trên máy, hoặc khi chưa nạp được secret:

```bash
export RAMUS_API_KEY=...            # hoặc: npx ramus-cli trial   (15 phút, không adb)
npx ramus-cli status                # xác nhận key sống

npx ramus-cli session start --apk ./app.apk --wait
npx ramus-cli adb --port 5555       # in ra serial
adb -s <serial> forward tcp:8080 tcp:8080
curl -s localhost:8080/health | jq

node .github/scripts/ramus-probe.mjs --out reports/local --mode key \
  --statics "Stage_Datas,Player_Get_Datas" --strict

npx ramus-cli session end
```

Không có `adb` (trial) thì bỏ 3 dòng `adb`, giữ `--mode trial`; script sẽ đọc logcat.

---

## 7. Kết quả chạy thật + điều chưa chứng minh

### 7.1 Chuỗi lỗi đã sửa (mỗi lỗi là một lần chạy CI thật)

| # | Triệu chứng | Nguyên nhân | Sửa |
|---|---|---|---|
| 1 | `INSTALL_FAILED_MISSING_SPLIT` | XAPK = base + `config.arm64_v8a` | `prepare-apk.sh` mở gói |
| 2 | `Prepare APK` exit 1 | `pipefail` + base không có `lib/` | `\|\| true` + `trap ERR` |
| 3 | vẫn `MISSING_SPLIT` | merge xong nhưng bị bỏ vì exit code | quyết định theo **nội dung file** |
| 4 | `INSTALL_PARSE_FAILED_NO_CERTIFICATES` | APKEditor ghi "signature block" nhưng không ký | `uber-apk-signer --allowResign` |
| 5 | `bridge-unreachable` | APK không chứa `RamusBridge.dll` | **đúng như thiết kế** — xem §7.2 |

### 7.2 Cái gì **chưa** được chứng minh

> **ABI chưa được chứng minh.** Tôi từng viết "game chết vì arm64 trên emulator x86_64".
> Đó là **giả thuyết**, không phải kết luận. Bằng chứng thật chỉ có:
> `abis=arm64-v8a` (từ inventory) + `ramus.dev/docs/quickstart` ghi emulator **x86_64**.
> Log trích ra lại toàn là cảnh báo `app_process` của chính emulator, **không** có
> `UnsatisfiedLinkError` hay `dlopen failed` nào của game — nên chưa đủ để kết luận.
> Báo cáo CI giờ ghi đúng mức độ này và liệt kê các khả năng, thay vì khẳng định.

Ba khả năng còn phân biệt được, và cách phân biệt:

| Khả năng | Dấu hiệu | Cách xác nhận |
|---|---|---|
| ABI không khớp | không có `Unity` tag, không có `Displayed <package>` | `adb logcat` trên thiết bị có adb, tìm `UnsatisfiedLinkError` / `dlopen` |
| Activity không được start | `Displayed <package>` vắng mặt dù cài OK | `ramus app launch` rồi chụp lại |
| Chết trước khi Unity init | có `Start proc …<package>` rồi im | logcat đầy đủ (không chỉ 500 dòng cuối) |

Report từ nay có thêm dòng **"activity started (Displayed/Start proc)"** — tín hiệu này
tách được "chưa từng chạy" khỏi "chạy rồi chết".

### 7.3 Đã sửa một lỗi thật trong adapter nhờ đọc source loader

Đối chiếu `LavaGang/MelonLoader` **v0.7.3** (`MelonBase.cs`): từ 0.7 **không còn
`OnApplicationStart`**. Adapter cũ override hàm đó ⇒ **không compile được** với 0.7.
Đã đổi sang cặp hook tồn tại ở **cả 0.6 và 0.7**:

```csharp
public override void OnInitializeMelon()   // Init bridge (thuần .NET)
public override void OnUpdate()            // tạo host GameObject ở frame đầu
public override void OnApplicationQuit()   // Shutdown
```

Đã xác nhận bằng source thật: `MelonMod : MelonTypeBase<MelonMod>` → `MelonBase.174–273`
có `OnInitializeMelon`, `OnUpdate`, `OnApplicationQuit`; `LoggerInstance.Msg(string)` có;
`MelonInfoAttribute(Type,string,string,string,string=null)` và
`MelonGameAttribute(string=null,string=null)` khớp cách dùng.
BepInEx 6: `BasePlugin` (`Runtimes/Unity/BepInEx.Unity.IL2CPP/BasePlugin.cs`) có
`public ManualLogSource Log` và `public abstract void Load()` ⇒ adapter `BepInEx6` khớp.

> Nhận định: đây chính là loại lỗi mà "đọc code bằng mắt" không bắt được — nó chỉ lộ ra khi
> đối chiếu với source/DLL thật của đúng phiên bản loader.

### 7.4 Build thật, không phải "đã kiểm cú pháp"

`.github/scripts/build-bridge.sh` compile **4 target** với DLL loader tải thật từ GitHub
Release, và **job đỏ nếu bất kỳ target nào lỗi** (exit code = số target fail).

**Lần chạy `39921281530` — kết quả thật, comment treo trên PR #12:**

```
[build] PASS  core (netstandard2.1, Unity stubs)      33.280 B
[build] PASS  BepInEx 5 (netstandard2.1)              33.792 B
[build] PASS  BepInEx 6 IL2CPP (net6.0)               34.304 B
[build] PASS  MelonLoader (net6.0)                    34.816 B
[build] PASS  self-test (HTTP + JSON + main-thread queue)
```

#### Self-test: chạy thật, không chỉ compile

`runtime-probe/SelfTest` compile **đúng file `RamusBridge.cs` sẽ ship** với stub
`UnityEngine`, boot server ở `127.0.0.1:18080` rồi gọi bằng `HttpClient` thật:

| Nhóm | Kiểm |
|---|---|
| Boot | server listen, `RAMUS_BRIDGE_PORT` có hiệu lực |
| 8 endpoint GET | `/health` `/state` `/scene` `/hierarchy` `/find` `/statics` `/logs` `/metrics` — 200, JSON hợp lệ, < 8 s |
| `/health` shape | `ok:true`, có `scene`, `unity`, `Content-Type: application/json` |
| `/screenshot` | route đúng (503 khi stub không chụp được) |
| route lạ | 404 sạch, không rớt kết nối |
| `POST /timescale` | round-trip `?v=`, trả `ok:true` |
| đồng thời | 20 request `/health` song song → 20/20 200 (hàng đợi main-thread) |
| shutdown | `Bridge.Shutdown()` dừng server, cổng được giải phóng |

> Nhận định: self-test tìm ra 4 lỗi **500 thật** ở `/state /scene /hierarchy /find` mà
> 4 target compile hoàn toàn không thấy. Nguyên nhân nằm ở **stub**, không ở bridge:
> `QualitySettings.names` và `Scene.GetRootGameObjects()` trả `null`, trong khi Unity
> trả mảng rỗng. Đã sửa stub theo đúng hành vi Unity. Đây là ví dụ cụ thể cho việc
> "compile xanh" ≠ "chạy được".

Self-test **không** chứng minh: reflection trên IL2CPP đọc đúng field của game,
`/screenshot` chụp được frame thật, hay `/statics` trả 3 mảng `pct`. Những thứ đó
vẫn cần game chạy với plugin đã nạp.

sha256 từng DLL được in trong comment CI cùng kích thước, để đối chiếu bản tải về.

> Lưu ý: hash **khác nhau giữa các lần chạy** dù `Deterministic=true`, vì stub
> `UnityEngine.dll` được build lại mỗi lần (MVID mới) rồi được tham chiếu vào DLL.
> Đừng dùng hash này để kiểm tra build tái lập; chỉ dùng để khớp artifact với log.

| Target | Tham chiếu | TFM |
|---|---|---|
| core | stub `UnityEngine.dll` (identity 0.0.0.0) | netstandard2.1 |
| BepInEx 6 IL2CPP | `BepInEx-Unity.IL2CPP-win-x64-6.0.0-pre.2.zip` | net6.0 |
| MelonLoader | `MelonLoader.x64.zip` v0.7.3 | net6.0 |
| BepInEx 5 | `BepInEx_win_x64_5.4.23.5.zip` | netstandard2.1 |

#### Bốn lỗi compile thật đã sửa (mỗi lỗi là một log CI, không phải suy đoán)

| # | Lỗi từ log | Nguyên nhân thật | Sửa |
|---|---|---|---|
| 1 | `find: '.ci/refs/bep6/dotnet': Permission denied` | zip BepInEx có thư mục mode hạn chế, `set -e` giết step | `chmod -R u+rwX` sau khi giải nén (`fetch-loader-refs.sh`) |
| 2 | `NETSDK1005: … doesn't have a target for 'net6.0'` | `-p:TargetFramework` chỉ áp **sau** restore | đổi sang `-p:Tfm=`, TFM tham gia restore |
| 3 | `CS0012: MonoBehaviour … add a reference to 'UnityEngine, Version=0.0.0.0'` | stub chỉ là **file .cs compile kèm** ⇒ không có assembly identity | `BuildCheck/UnityStubs.csproj` build ra **UnityEngine.dll** 0.0.0.0, `Reference` thật |
| 3b | `CS0050: return type 'HttpResponse' is less accessible` | method `public`, kiểu trả về `internal` | `Screenshot()` → `internal` |
| 4 | `CS0518: System.Object is not defined` (**291 lỗi**) | zip BepInEx 6 chứa **cả runtime .NET** (`dotnet/`); flatten hút `mscorlib`/`System.*` vào | lọc bỏ `dotnet/*`, `mscorlib`, `netstandard`, `System.*`, `Microsoft.*` |

> Nhận định: đây là toàn bộ những gì "đọc source bằng mắt" ở vòng trước đã bỏ sót.
> Không có log CI nào thì cả 4 lỗi này vẫn nằm nguyên trong repo và người dùng sẽ
> gặp chúng khi tự build.

> `UnityEngine.dll` stub chỉ dùng lúc compile — nó chứng minh bridge type-check đúng,
> **không** chứng minh khớp `UnityEngine` thật của game. Muốn chắc thì build với
> `-p:UnityManagedDir=<game>_Data/Managed` trên máy có bản Unity đó.

### 7.5 Chốt: còn thiếu gì để probe chạy được

1. **Bridge phải nằm trong bản được cài.** CI không patch APK. Hoặc build plugin vào bản test,
   hoặc dùng FusionCore/NextBep nạp plugin từ storage của launcher (khi đó `allow_no_bridge: true`).
   Lưu ý game là **IL2CPP**: loader cần `libil2cpp` đã patch, nên "bỏ DLL vào `Mods/`" **không đủ**
   nếu bản cài chưa qua patcher của loader.
2. **Thiết bị phải chạy được app.** Cần bằng chứng `Displayed <package>` + `Unity` tag;
   nếu là arm64-only thì cần thiết bị/emulator arm64 (Ramus hiện x86_64).

Gate dừng **trước khi tạo phiên Ramus** nếu APK không có `RamusBridge.dll`, để không đốt
15 phút credential cho một kết luận đã biết trước. Trạng thái hiện tại của repo đúng là
trạng thái này: `bridge: no` ⇒ `probe` báo *skipped* kèm lý do, build vẫn xanh.

## 8. Giới hạn đã biết

- **Chưa build/chạy thử trong sandbox này** (không có .NET SDK, không có thiết bị). Code đã qua kiểm tra cú pháp/khung; **lần build đầu phải chạy trên máy bạn**.
- Trial: 15 phút, 1 session, APK ≤ 150 MB, **không adb**, không camera/mic (lệnh đó cần key). Hết hạn giữa chừng thì các lệnh sau trả `unauthorized` — script ghi chú rõ.
- Trial là **anonymous**, nhưng APK vẫn được upload lên hạ tầng Ramus: chỉ đẩy build bạn có quyền kiểm thử.
- `/screenshot` trả PNG; ảnh 1080p có thể vượt 6 MB → 413, dùng `ramus screenshot`.
- `/statics` phụ thuộc reflection của interop; field generic/struct lồng nhau có thể bị bỏ qua (`written` cho biết đã đọc được bao nhiêu).
- Không có endpoint **ghi**: read-only + 3 lệnh điều khiển (`timescale`, `quit`, `mark`).

### Troubleshooting

| Triệu chứng | Kiểm tra |
|---|---|
| `curl` connection refused | `adb forward --list`; bridge bind `0.0.0.0`? xem `mirror` log |
| Trial: không thấy dòng `RAMUSB\|` | APK có `RamusBridge.dll`? plugin có nạp (log `[RamusBridge]`)? tăng `--logcat-wait` |
| Plugin không nạp | logcat có `[RamusBridge]`? Loader hỗ trợ Unity 2022.3.62f3? |
| `main thread did not answer` | game pause/`timescale=0` và `Update()` không chạy → dùng logcat |
| Build thiếu `UnityEngine.CoreModule` | chạy game một lần để sinh `BepInEx/interop`, hoặc trỏ `-p:InteropDir=` |
| `session start` fail 3 lần | hết slot trial (1 session đồng thời) hoặc APK > 150 MB |
| `release:…` trả 404 | release là draft và token chỉ read-only (fork PR) → chạy trên nhánh của repo, hoặc đặt `RAMUS_APK_SOURCE` |
| App crash ngay sau khi cài | xem `apk-inventory.txt`: có `config.*.apk` không? trial không cài được split → cần key |
| `not a zip (magic …)` | tải hỏng/HTML thay vì file — kiểm URL |
| `ramus status` trả `unauthorized` | key sai/hết hạn → rotate at ramus.dev/settings, `gh secret set` lại |
| Ảnh 413 | giảm độ phân giải hoặc dùng `ramus screenshot` |
