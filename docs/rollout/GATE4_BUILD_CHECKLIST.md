# Gate-4 build checklist — ai chạy gì, lệnh nào, đạt khi nào

**Trạng thái: PROVISIONAL / plan-level.** Tài liệu này biến 3 file spec thành một chuỗi lệnh kiểm được.
Không chạy gì ở đây; mỗi dòng ghi rõ **ai** chạy và **bằng chứng** phải nộp.

Liên quan: `GODOT_BUILD_PACKAGING_SPEC.md` (khoá preset + ngưỡng) · `GODOT_EXPORT_PRESET_CONTRACT.json`
(hợp đồng máy đọc) · `VERIFIER_PROTOCOL_GODOT_PORT.md` (V1–V9) · `MSIX_PACKAGING_PLAN.md` (M1–M6).

## 0. Ai làm gì (một dòng)

| Vai | Việc trong Gate-4 |
|---|---|
| **USER** | cài SDK/Godot? — *không bắt buộc*; cấp keystore, pháp nhân, quyết định MSIX vs EXE, quyền IP, lệnh publish |
| **Godot-coder** | dựng project, viết `export_presets.cfg` + `version.json`, chạy export, nộp artifact + log |
| **ef6b75ef (verifier)** | chạy lại export trong checkout sạch, diff preset với hợp đồng, đo byte, kiểm provenance, viết báo cáo |
| **Reviewer 8141386a** | nâng verdict Gate (không phải tôi) |

## 1. P0 — điều kiện tiên quyết (kiểm trước khi export)

| # | Điều kiện | Cách kiểm | Nhãn |
|---|---|---|---|
| P0.1 | Godot **đúng** `4.7.2-stable` | `godot --version` → `4.7.2.stable.*` | `STATIC_CONFIRMED` (log) |
| P0.2 | Android: JDK + Android SDK; biến `export/android/java_sdk_path` trỏ đúng | Godot Editor Settings → Export → Android; `bin/java`, `bin/keytool` tồn tại (**mã**: `android_export_plugin.cpp:2686-2701`) | `STATIC_CONFIRMED` |
| P0.3 | Android build-tools ≥ **28** (mã chọn bản build-tools: `android_export_plugin.cpp:2738-2747`, ưu tiên bản khớp target SDK **36**) | liệt kê `build-tools/` trong SDK | `INFERRED` (phiên bản chính xác của build-tools theo SDK cài) |
| P0.4 | MSIX: Windows SDK có `MakeAppx.exe`, `makepri.exe` | `where MakeAppx` | `STATIC_CONFIRMED` (log) |
| P0.5 | Keystore release của USER đặt **ngoài repo**, alias + mật khẩu lấy từ secret | `git grep -l "keystore"` không thấy file nhị phân | V1 |
| P0.6 | `version.json` tồn tại, `version_code` là int ≥ 1 | đọc file | V3 |

Nếu P0.1–P0.6 thiếu bất kỳ mục nào → **dừng**, báo `NOT_READY — thiếu P0.x`; không export “tạm”.

## 2. Chuỗi lệnh (coder chạy, verifier chạy lại độc lập)

```bash
# 1) import sạch (G1)
godot --headless --quit --path .

# 2) Windows (M1)
godot --headless --export-release "Windows Desktop" build/win/WindWings.exe

# 3) Android AAB cho AppGallery (M1)
godot --headless --export-release "Android AppGallery AAB" build/android/WindWings.aab

# 4) Android APK cho Amazon/AppGallery fallback
godot --headless --export-release "Android APK (AppGallery/Amazon)" build/android/WindWings.apk

# 5) cổng kích thước (V6) — số byte thật
stat -c '%n %s' build/win/WindWings.exe build/android/WindWings.aab build/android/WindWings.apk

# 6) chữ ký APK (V7) — apksigner nằm trong Android build-tools
apksigner verify --print-certs build/android/WindWings.apk
```

Windows (PowerShell, máy có Windows SDK) — M3–M5:

```powershell
MakeAppx.exe pack /d .\build\msix\ /p .\build\msix\WindWings.msix
# dev test (chỉ Win11, gói unsigned phải có OID trong Identity@Publisher):
Add-AppxPackage -Path .\build\msix\WindWings.msix -AllowUnsigned
```

Ngưỡng đạt: APK ≤ **2,5 GB** (Amazon, chặt hơn 4 GB của AppGallery) · AAB ≤ **150 MB** (Huawei) ·
`.msix` không có ngưỡng đã xác minh (`UNKNOWN`, ghi byte thật).

## 3. Bằng chứng phải nộp (đúng thứ tự, thiếu là fail)

1. `git rev-parse HEAD` + CI run id theo headSha.
2. `export_presets.cfg` nguyên văn + `version.json` + `project.godot` (3 mục ở protocol §2).
3. Log của cả 4 lệnh export (không cắt).
4. Bảng byte của 3 artifact + sha256 từng file.
5. `apksigner` output (cert SHA-256) **hoặc** ghi `RUNTIME_UNVERIFIED` + lý do thiếu tool.
6. Danh sách asset kèm nguồn (vẽ mới/mua/sinh script) + sha256.
7. Danh sách `.gdap` (nếu có IAP/ads) kèm giấy phép + phiên bản.

## 4. Verifier làm gì với bộ đó

| V | Việc | Fail điển hình |
|---|---|---|
| V1 | `git ls-files` lọc `*.keystore,*.jks,*.pfx,*.p12,*.exe,*.apk,*.aab`; so byte > 5 MB | có artifact build trong repo |
| V2 | parse `export_presets.cfg` → diff với `GODOT_EXPORT_PRESET_CONTRACT.json` | thiếu `binary_format/embed_pck`; `export_format=1` mà `use_gradle_build=false` |
| V3 | `version.json` vs `version/code` vs `application/file_version` | code không tăng; 3 nguồn lệch nhau |
| V4 | cross-check C1–C6 | `min_sdk 21`; bật `x86_64` cho bản phát hành |
| V5 | checkout sạch + export lại đúng 4.7.2 | export lỗi; cảnh báo template thiếu |
| V6 | đo byte | AAB > 150 MB |
| V7 | `apksigner`/cert | APK không ký; cert khác cert đã khai |
| V8 | asset vs danh mục gốc | có file tên trùng asset gốc |
| V9 | claim không nguồn | “chạy mượt trên Fire” không log |

## 5. Ba thứ chặn Gate-4 dù build xanh

1. **Quyền IP/phân phối** (Phase C §User-ONLY 3) — USER.
2. **Keystore + alias** (P0.5) — USER cấp, tôi không giữ.
3. **Quyết định MSIX vs EXE/PWA** (U3) — đổi hẳn đường đóng gói Windows.

## 6. Điều checklist này không hứa

- Không hứa store nhận: review/duyệt là của store.
- Không hứa chạy đúng trên Fire tablet/Windows ARM: cần thiết bị thật (`UNKNOWN`).
- Không thay playtest/art review: Gate-4 chỉ là cổng **build được + ký được + đúng hợp đồng**.
