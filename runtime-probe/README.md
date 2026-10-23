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

Kết quả: `runtime-probe/bin/Release/netstandard2.1/RamusBridge.dll`.

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

CI đọc bằng `npx ramus-cli logcat --limit 800`, tách các dòng `RAMUSB|`, parse JSON, ghi vào `summary.json` (`transport: "logcat"`).

---

## 6. CI trên Ramus

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
| `RAMUS_APK_URL` | repo variable | Khuyến nghị | URL APK để CI tải (release asset, artifact public…) |

Không có APK ⇒ job `preflight` tắt job `probe` kèm notice, CI không đỏ.

### Chạy

```bash
# anonymous (không cần secret)
gh workflow run runtime-probe.yml -f apk_url="https://…/app.apk" -f scenario=anonymous

# có key: bật HTTP + dump field static của các class game
gh workflow run runtime-probe.yml -f apk_url="https://…/app.apk" \
  -f statics="Stage_Datas,Player_Get_Datas,Enemy_Get_Datas,Stage_Get_Datas" \
  -f wait_scene=Ingame

# kèm kịch bản bấm + đợi scene (đợi scene chỉ có tác dụng ở chế độ key)
gh workflow run runtime-probe.yml -f apk_url="https://…/app.apk" -f taps="0.5,0.82 0.5,0.82" -f wait_scene=Ingame
```

Hoặc đặt APK sẵn ở `runtime-probe/app.apk` (đã `.gitignore`) và bấm Run.

Workflow làm tuần tự:

1. `preflight` — chọn APK + chế độ, không cần secret.
2. `Resolve APK` — tải/copy, **chặn nếu > 150 MB ở chế độ trial** (báo lỗi kèm cách xử lý), in sha256.
3. `Credentials` — key: export; trial: `ramus trial --force`, lưu `expiresAt` + `limits`.
4. `session start --apk … --wait --timeout 600`, thử 3 lần, lưu `session.json`.
5. `wait --stable` + screenshot màn hình đầu.
6. `adb forward` **chỉ ở chế độ key**; trial ghi chú rõ "no-adb".
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

## 7. Giới hạn đã biết

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
| `ramus status` trả `unauthorized` | key sai/hết hạn → rotate at ramus.dev/settings, `gh secret set` lại |
| Ảnh 413 | giảm độ phân giải hoặc dùng `ramus screenshot` |
