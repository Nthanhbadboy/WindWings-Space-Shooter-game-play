# Godot 4.x build & packaging spec — 3 kênh (Microsoft Store · Amazon Appstore · Huawei AppGallery)

**Trạng thái: PROVISIONAL / plan-level.** Không build gì trong tài liệu này, không đụng SDK, không tạo
keystore, không upload store. Mọi preset dưới đây là **hợp đồng khoá-giá-trị** để session Godot-coder
dùng lại; mọi con số đều có nguồn kiểm được (file + dòng, hoặc tài liệu trong repo + mục).

Nhãn bằng chứng dùng đúng 6 loại: `STATIC_CONFIRMED` · `RUNTIME_CONFIRMED` · `INFERRED` ·
`RUNTIME_UNVERIFIED` · `UNKNOWN` · `CONFLICTING`.

## 0. Phạm vi

| Trong phạm vi | Ngoài phạm vi (USER-ONLY hoặc session khác) |
|---|---|
| Khoá export preset + giá trị đề xuất cho 3 kênh | Tạo/giữ keystore, app signing key |
| Quy tắc versioning ánh xạ 3 store | Đăng ký tài khoản, khai thuế, payout |
| Luồng signing (ai ký cái gì) | Bấm upload / submit / publish |
| Kế hoạch CI + cổng kích thước/ký | Chạy build thật, cài SDK, mua plugin |
| Mapping port-plan (file riêng) | Vẽ/duyệt asset, giá bán, nội dung listing |

Nguyên tắc: **không kênh nào được coi là “xong” chỉ vì preset đúng** — bước account/keys/publish luôn
là USER (mandate Phase C §USER-ONLY 1–6).

## 1. Pin

| Thành phần | Giá trị |
|---|---|
| Engine | **Godot `4.7.2-stable`**, tag commit `ed1daf0bf001b61586d9930840f2f1394092c079` (GitHub release API, publish `2026-08-18`) |
| Nguồn khoá Android | `platform/android/export/export_plugin.cpp` @ `4.7.2-stable`, 177365 B, sha256 `b00c8a24eeedff494441a9220270458c5d49261be78ae57a3473445c03aa07f8` |
| Nguồn khoá Windows | `platform/windows/export/export_plugin.cpp` @ `4.7.2-stable`, 45520 B, sha256 `0305ee0406b90db7e4a66b8725f569e0294873f2c5a7907ca75442290432242c` |
| Nguồn khoá PC dùng chung | `editor/export/editor_export_platform_pc.cpp` @ `4.7.2-stable`, sha256 `88bb623a4a6ce2d008d1398d207c00167ae199786be60ea5676f2325ca5886cd` |
| APK gốc (baseline kỹ thuật) | `minSdk 24` / `targetSdk 36` — `docs/apk-analysis/01-apk-inventory.md:466` (nhánh `20330d0e`) |
| Store facts | `docs/research/phase-b/PHASE_B_COMMERCIAL_RESEARCH.md` + `docs/rollout/PHASE_C_EXECUTION_PLAN.md` (nhánh `20330d0e`) |
| Learning-note 135 | `docs/rollout/LEARNING_NOTE_135_ANIMATOR_PORT.md` (nhánh này) |

Mọi tham chiếu `file:line` của Godot dưới đây là **dòng trong 3 file đã pin ở trên**.

## 2. Ma trận 3 kênh (số lấy từ Phase B, không tự thêm)

| | Microsoft Store (Windows) | Amazon Appstore (Fire) | Huawei AppGallery |
|---|---|---|---|
| Phí account | `$0` | `$0` | `$0` + verify danh tính |
| Revenue share (game) | **12%** store / 88% dev | 70/30 (SBAP 80/20 khi đủ điều kiện) | **30/70 ngoài TQ**; 50/50 đại lục |
| Định dạng nhận | **MSIX** là chuẩn; *cũng* nhận MSI/EXE (Win32 không đóng gói) và PWA | **APK hoặc AAB**, ≤ **2,5 GB**, **không nhận OBB**; Vega dùng VPKG riêng | **APK ≤ 4 GB**; **AAB ≤ 150 MB**, **bắt buộc App Signing**; nhận cả EXE cho app Windows |
| Review | ≤ 3 ngày làm việc | — | 3–5 ngày làm việc |
| Ghi chú phạm vi | Cần **bản Windows** | Kênh Android mobile đã đóng 20/08/2025 → **chỉ Fire tablet/TV** (D1a/D10a) | 170+ nước; TQ đại lục cần 版号 → **loại lúc launch** (D2a) |

Nguồn: `PHASE_C_EXECUTION_PLAN.md` §Trạng thái 3 kênh + §User-ONLY; `PHASE_B_COMMERCIAL_RESEARCH.md`
§Microsoft Store (packaging, S7) · §Amazon (S13/S15) · §AppGallery (S37) — `STATIC_CONFIRMED` theo
research của session E, **không** phải tôi đo lại. Con số nào store đổi về sau thì bảng này phải sửa
theo console, không theo tài liệu này.

## 3. Android — preset cho AppGallery và Amazon

### 3.1 Hai preset, không một

| Preset | Kênh | `gradle_build/export_format` | Ghi chú |
|---|---|---|---|
| `Android AppGallery AAB` | AppGallery | `1` (`Export AAB`) | Bắt buộc gradle build; trần **150 MB** theo AppGallery |
| `Android APK (AppGallery/Amazon)` | AppGallery fallback + Amazon | `0` (`Export APK`) | Trần 4 GB (AppGallery) / 2,5 GB (Amazon) |

Hai preset **cùng code, khác định dạng**; Amazon chỉ nhận tới 2,5 GB nên cổng kích thước đặt theo
ngưỡng thấp hơn (2,5 GB) cho file APK phát hành.

### 3.2 Khoá đã kiểm (Godot 4.7.2)

| Khoá | Kiểu / miền giá trị | Dòng | Đề xuất |
|---|---|---|---|
| `gradle_build/use_gradle_build` | bool | 2194 | `true` (bắt buộc cho AAB) |
| `gradle_build/export_format` | enum `Export APK,Export AAB` = `0,1` | 2198 | `1` (AAB) · `0` (APK) |
| `gradle_build/min_sdk` | string | 2202 | để trống ⇒ **24** (`DEFAULT_MIN_SDK_VERSION`, dòng 303) = đúng baseline APK gốc |
| `gradle_build/target_sdk` | string | 2203 | để trống ⇒ **36** (`DEFAULT_TARGET_SDK_VERSION`, dòng 305) = đúng baseline APK gốc |
| `gradle_build/compress_native_libraries` | bool | 2197 | `false` (giữ `.so` rời để store soi được) |
| `architectures/arm64-v8a` | bool (default `true`) | 2223–2224 | `true` |
| `architectures/armeabi-v7a` | bool | 2224 + ABI list 703–706 | `true` nếu muốn Fire tablet đời cũ; quyết định sản phẩm |
| `architectures/x86_64` | bool | 2224 + ABI list 706 | `false` cho bản phát hành |
| `version/code` | int, range `1,4096,1,or_greater` | 2234 | tăng đơn điệu, xem §5 |
| `version/name` | string | 2235 | trống ⇒ lấy `project.godot` `config/version` |
| `package/unique_name` | string `ext.domain.name` | 2237 | phải khác package APK gốc (`com.Wind.wings.Space.Shooter`) — dùng của game mới |
| `package/name` | string | 2238 | tên hiển thị |
| `package/signed` | bool | 2239 | `true` |
| `package/app_category` | enum, default `Game` | 2240 | `Game` |
| `keystore/release` | string `*.keystore,*.jks` | 2230 | trỏ tới keystore **của user** (không commit) |
| `keystore/release_user` | string | 2231 | alias key |
| `keystore/release_password` | password | 2232 | lấy từ secret CI, không nằm trong preset |
| `permissions/custom_permissions` | PackedStringArray | 2279 | rỗng cho slice đầu; thêm theo adapter IAP/ads sau |
| `screen/immersive_mode` | bool | 2262 | `true` |

**Ràng buộc cứng đọc được từ mã:** đặt `export_format = AAB` mà **không** bật gradle build ⇒ exporter
trả lỗi (dòng 2116–2117). Vì vậy AAB và `use_gradle_build=true` là một cặp, không phải hai tuỳ chọn.

**Không có trong Godot:** không có khoá OBB/expansion nào trong exporter Android (`grep -i obb` = 0 hit
trên file đã pin) ⇒ ràng buộc “Amazon không nhận OBB” tự thoả, nhưng cũng có nghĩa **không thể** có
phương án nội dung tách rời kiểu OBB — mọi asset phải đi trong AAB/APK hoặc tải sau (chưa thiết kế).

**Target SDK:** engine mặc định 36 khớp baseline APK; **yêu cầu target API tối thiểu hiện hành của
AppGallery và Amazon là `UNKNOWN` trong tài liệu này** (không tra được console/trang chính chủ trong
phiên này) → mục 8 là checklist cho user/E xác nhận, **không** đoán số.

## 4. Windows — Godot xuất `.exe`, MSIX là bước đóng gói ngoài engine

### 4.1 Kết luận cứng

`grep -i "msix\|appx"` trên `platform/windows/export/export_plugin.cpp` và
`editor/export/editor_export_platform_pc.cpp` @ `4.7.2-stable` = **0 hit** ⇒ Godot **không** có đích
export MSIX/APPX (`STATIC_CONFIRMED`, đo trên 2 file đã pin). Windows build = `.exe` + `.pck`.

Hệ quả cho MS Store: cần một bước **đóng gói MSIX bên ngoài** (Windows Application Packaging Project
hoặc `makeappx`/MSIX Packaging Tool) rồi mới submit. Chi tiết công cụ là `INFERRED` theo quy trình
Windows chung; **định dạng nhận** của store (MSIX chuẩn, nhận thêm MSI/EXE/PWA) là số của Phase B
(`STATIC_CONFIRMED` theo research, không phải tôi kiểm lại store).

### 4.2 Khoá preset Windows đã kiểm

| Khoá | Kiểu / miền | Dòng | Đề xuất |
|---|---|---|---|
| `binary_format/architecture` | enum `x86_64,x86_32,arm64` | windows 462 | `x86_64` cho bản store đầu |
| `binary_format/embed_pck` | bool | pc 65 | `true` (một file `.exe` duy nhất, dễ đóng MSIX) |
| `debug/export_console_wrapper` | enum `No,Debug Only,Debug and Release` | pc 63 | `0` (`No`) cho release |
| `texture_format/s3tc_bptc` | bool | pc 67 | `true` |
| `codesign/enable` | bool | windows 464 | `false` ở bản dựng cho MS Store **nếu** Partner Center ký MSIX (xem §6) |
| `application/modify_resources` | bool | windows 474 | `true` |
| `application/icon` | file `*.ico,*.png,*.webp,*.svg` | windows 475 | icon `.ico` do session art cấp |
| `application/product_name` | string | windows 481 | tên game |
| `application/company_name` | string | windows 480 | pháp nhân user (USER-ONLY xác nhận) |
| `application/file_version` | string | windows 478 | trống ⇒ lấy version project; MSIX `Version` là **4 thành phần** nên phải chuẩn hoá (§5) |
| `application/product_version` | string | windows 479 | như trên |

## 5. Versioning — một nguồn, ba ánh xạ

Đề xuất (chưa tạo file, chỉ đặc tả): một file `version.json` ở root project Godot là **nguồn duy nhất**:

```
{ "version_name": "0.1.0", "version_code": 1 }
```

| Đích | Ánh xạ | Ràng buộc kiểm được |
|---|---|---|
| Android `version/code` | `version_code` | kiểu int, range khai báo `1,4096,1,or_greater` (dòng 2234) ⇒ không được 0 |
| Android `version/name` | `version_name` | chuỗi hiển thị |
| Windows `application/file_version` / `product_version` | `version_name` chuẩn hoá 4 thành phần `a.b.c.d` | exporter dùng cho PE resource |
| MSIX `Identity Version` | `a.b.c.0` (thành phần thứ 4 = 0) | MSIX yêu cầu 4 số, `INFERRED` theo định dạng gói |
| Huawei AppGallery AAB | đọc `versionCode` trong bundle | trần 4 GB/150 MB không liên quan |

Quy tắc: `version_code` **tăng đơn điệu mỗi lần submit** bất kể store nào; không tái sử dụng code đã
submit (kể cả bản bị từ chối). Việc “code tối đa” của từng store là `UNKNOWN` — chỉ chặn bằng range
của engine và kiểm tra ở console.

## 6. Signing flow — ai ký cái gì

| Kênh | Ai ký | Việc session/user phải làm | Nhãn |
|---|---|---|---|
| AppGallery AAB | **Huawei App Signing**: upload key (user) → signing key (Huawei giữ) | bật App Signing trong AGC, upload key do user giữ | `STATIC_CONFIRMED` (research E, `MONETIZATION_VERIFICATION_2026-10-27.md` dòng keystore) |
| AppGallery APK | keystore release **của user** | `keystore/release*` trỏ tới file ngoài repo | `STATIC_CONFIRMED` (khoá có trong exporter, dòng 2230–2232) |
| Amazon APK/AAB | ký bằng key **của user** | như trên | `STATIC_CONFIRMED` (research E) |
| MS Store | **Partner Center ký MSIX** — không cần keystore riêng | đóng gói MSIX chưa ký hoặc ký dev, submit | `STATIC_CONFIRMED` (research E) |

Bí mật không bao giờ vào preset/commit. Tên secret đề xuất cho CI (chưa tạo): `ANDROID_KEYSTORE_B64`,
`ANDROID_KEY_ALIAS`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_PASSWORD`. Khi build local, dùng
biến môi trường và `--export-release` với preset đã trỏ sẵn — không hardcode.

## 7. CI plan (chưa chạy) — 4 cổng

| Cổng | Kiểm | Fail khi |
|---|---|---|
| G1 | `godot --headless --quit` import project sạch | lỗi import/parse |
| G2 | export **Windows** + **Android APK** (debug template) | export lỗi |
| G3 | cổng kích thước: APK ≤ **2,5 GB** (ngưỡng Amazon, thấp hơn 4 GB Huawei); AAB ≤ **150 MB** (Huawei) | vượt ngưỡng |
| G4 | cổng ký: APK verify bằng `apksigner verify`; AAB có `versionCode` = `version.json` | thiếu chữ ký / lệch version |

Artifact: `.exe`, `.pck`, `.apk`, `.aab`, `version.json` + log. Không upload store trong CI.

## 8. Checklist USER/E phải xác nhận (không đoán)

1. **Target API tối thiểu hiện hành** của AppGallery và Amazon (và trần `targetSdk`) — `UNKNOWN`.
2. **Amazon**: còn nhận AAB cho Fire tablet không, và ngưỡng 2,5 GB có đổi — `UNKNOWN` (số trong §2 là
   của research 2026-10-27).
3. **MS Store**: loại sản phẩm (MSIX đóng gói vs EXE không đóng gói/PWA) mà user chọn cho bản Windows —
   quyết định này đổi hẳn §4.
4. **Pháp nhân** ghi trong `application/company_name` + `application/copyright` — USER-ONLY.
5. **Quyền IP/phân phối** (Phase C §User-ONLY 3) — chặn Gate-4 dù preset đã sẵn.

## 9. Exit criteria cho Gate-4 (đếm được)

- [ ] 3 preset (`Android AppGallery AAB`, `Android APK (AppGallery/Amazon)`, `Windows Desktop`) có **đủ
      mọi khoá ở §3.2/§4.2** với giá trị đúng bảng (kiểm bằng script đọc `export_presets.cfg`).
- [ ] `version.json` là nguồn duy nhất; `version/code` trong preset **bằng** `version_code`.
- [ ] G1–G4 xanh trên CI của nhánh Godot, kèm kích thước thật của `.apk`/`.aab` ghi trong log.
- [ ] Không file bí mật nào nằm trong repo (`git grep` cho `*.keystore`, `*.jks`, `*.pfx`, `*.p12` = 0).
- [ ] §8 mục 1–5 có câu trả lời của user, ghi ngày.

## 10. UNKNOWN / điều gì sẽ làm spec này sai

- Store đổi ngưỡng/kích thước/định dạng ⇒ §2 phải cập nhật theo console, không theo tài liệu này.
- Godot đổi tên khoá giữa các bản 4.x ⇒ mọi dòng trong §3.2/§4.2 gắn với tag `4.7.2-stable`; nâng engine
  phải chạy lại bước kiểm khoá (mục 11) trước khi tin bảng.
- MSIX: nếu user chọn đường EXE không đóng gói thì §4 mất hiệu lực phần đóng gói.

## 10b. Bằng chứng thô của vòng này

`reverse-engineering/raw/godot-build-spec/pins.json` (4143 B) ghi: tag + commit engine, sha256/byte của 3
file nguồn đã tải, **map khoá → số dòng** (android 40 khoá · windows 31 · pc 8), số hit `msix|appx` = **0**
trên cả 3 file, số hit `obb` = **0**, và 4 hằng số exporter (min 24 / target 36 / Vulkan 29 / enum APK-AAB).

## 11. Reproduce (đọc lại đúng nguồn, không build)

```
gh api repos/godotengine/godot/releases/latest --jq '.tag_name'
gh api "repos/godotengine/godot/contents/platform/android/export/export_plugin.cpp?ref=4.7.2-stable" --jq .content | base64 -d
gh api "repos/godotengine/godot/contents/platform/windows/export/export_plugin.cpp?ref=4.7.2-stable" --jq .content | base64 -d
gh api "repos/godotengine/godot/contents/editor/export/editor_export_platform_pc.cpp?ref=4.7.2-stable" --jq .content | base64 -d
grep -n -i "msix\|appx" <hai file exporter>    # kỳ vọng: 0 hit
```
