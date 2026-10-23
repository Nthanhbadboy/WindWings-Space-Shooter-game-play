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
                                       │ adb forward tcp:8080 tcp:8080
┌──────────────────────────────────────┴─────────────────────────────────────────┐
│ GitHub Actions                                                                  │
│   npx ramus-cli session start --apk app.apk --wait                               │
│   npx ramus-cli screenshot / snapshot / tap / logcat                            │
│   node .github/scripts/ramus-probe.mjs  → report.md + summary.json + PNG/JPEG   │
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
dotnet build runtime-probe/RamusBridge.csproj -c Release \
  -p:Loader=BepInEx6 -p:BepInExRoot="/đường/dẫn/BepInEx"

# MelonLoader / LemonLoader
dotnet build runtime-probe/RamusBridge.csproj -c Release \
  -p:Loader=MelonLoader -p:MelonDir="/đường/dẫn/MelonLoader"

# BepInEx 5 (bản Mono, dùng để thử trên PC trước)
dotnet build runtime-probe/RamusBridge.csproj -c Release \
  -p:Loader=BepInEx5 -p:UnityManagedDir="/đường/dẫn/Managed"
```

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

## 5. Đường dự phòng: logcat

Ramus trial (15 phút) **không có adb tunnel**. Khi đó bridge vẫn ghi mỗi 10 s một dòng:

```
I/Unity: RAMUSB|{"ok":true,"scene":"Ingame","frame":1234,"fps":59.8,"ts":1,"uptime":92.4}
```

CI đọc bằng `npx ramus-cli logcat --limit 800`, tách các dòng `RAMUSB|`, parse JSON, và ghi vào `summary.json` (`transport: "logcat"`). Muốn tắt: `mirror=0`.

Đây là lý do bridge **không phụ thuộc HTTP** để CI có tín hiệu: HTTP là đường nhanh, logcat là đường chắc chắn.

---

## 6. CI trên Ramus

### Bí mật / biến

| Tên | Loại | Bắt buộc | Ý nghĩa |
|---|---|---|---|
| `RAMUS_API_KEY` | secret | Có (trừ khi `use_trial`) | Key tại `ramus.dev/settings`. **Không dán vào chat/URL.** |
| `RAMUS_APK_URL` | repo variable | Khuyến nghị | URL APK để CI tải (release asset, artifact public…) |

Không có key → job `preflight` tắt job `probe` kèm notice, không đỏ CI. Fork PR không có secret cũng vậy.

### Chạy

```bash
gh workflow run runtime-probe.yml -f apk_url="https://…/app.apk" -f scenario=smoke -f wait_scene=Ingame -f taps="0.5,0.82 0.5,0.82"
```

Hoặc đặt APK sẵn ở `runtime-probe/app.apk` (đã `.gitignore`) và bấm Run.

Workflow làm tuần tự:

1. `session start --apk … --wait` (timeout 900 s), lưu `session.json`.
2. `wait --stable` + screenshot màn hình đầu.
3. Mở `adb` tunnel (best effort) → `adb forward tcp:8080 tcp:8080` → `curl /health`.
4. Bấm kịch bản (`taps`), đợi scene nếu có `wait_scene`.
5. Chạy `ramus-probe.mjs`: gom health/state/scene/hierarchy/find/statics/logs + screenshot, fallback logcat.
6. Upload artifact `runtime-probe-<run_id>` (report.md, summary.json, ảnh, session.json, sha256 APK).
7. Comment `report.md` vào PR (nếu là PR).
8. `session end` — luôn chạy, kể cả khi fail.

### Đọc kết quả

`report.md` có bảng metric + danh sách root object + static field + lỗi. `summary.json` giữ nguyên payload để phân tích sâu.

`verdict`:

| Giá trị | Nghĩa |
|---|---|
| `ok` | có dữ liệu, fps ≥ 20 |
| `degraded` | có dữ liệu nhưng fps < 20 |
| `bridge-unreachable` | không HTTP, không logcat → plugin chưa nạp hoặc app chưa chạy |
| `app-unstable` | log có dấu hiệu crash/died |
| `error` | script lỗi |

`--strict` (mặc định bật) chỉ fail job khi **không có dữ liệu nào**. Fps thấp là cảnh báo, không phải fail.

---

## 7. Giới hạn đã biết

- **Chưa build/chạy thử trong sandbox này** (không có .NET SDK và không có thiết bị). Code đã qua kiểm tra cú pháp/khung nhưng **lần build đầu phải chạy trên máy bạn**; xem mục Troubleshooting.
- `Ramus` là SaaS: cần key hoặc trial. Trial: 15 phút, APK ≤ 150 MB, **không adb** → chỉ còn đường logcat.
- `/screenshot` trả PNG base64 nhị phân qua HTTP; ảnh 1080p có thể vượt 6 MB → trả 413, dùng `ramus screenshot`.
- `/statics` phụ thuộc reflection của interop; một số field generic/struct lồng nhau sẽ bị bỏ qua (có `written` trong response để biết đã đọc được bao nhiêu).
- Không có endpoint **ghi**: mọi thứ là read-only + 3 lệnh điều khiển (`timescale`, `quit`, `mark`).

### Troubleshooting

| Triệu chứng | Kiểm tra |
|---|---|
| `curl` connection refused | `adb forward --list`; bridge bind `0.0.0.0`? xem `mirror` log |
| Plugin không nạp | logcat có `[RamusBridge]`? Loader có hỗ trợ Unity 2022.3.62f3? |
| `main thread did not answer` | game pause/`timescale=0` và `Update()` không chạy → dùng logcat |
| Build thiếu `UnityEngine.CoreModule` | chạy game một lần để sinh `BepInEx/interop`, hoặc trỏ `-p:InteropDir=` |
| Ảnh 413 | giảm độ phân giải hoặc dùng `ramus screenshot` |
