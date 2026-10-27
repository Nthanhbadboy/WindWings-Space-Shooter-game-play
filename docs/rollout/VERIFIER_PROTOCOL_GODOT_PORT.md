# Verifier protocol — kiểm độc lập code Godot của session Godot-coder (role ③)

**Trạng thái: PROVISIONAL / chưa có code để kiểm.** Tài liệu này chốt *cách* tôi sẽ kiểm khi session
Godot-coder mở, để hai bên không phải thương lượng lại tiêu chí sau khi code đã viết.

Nguyên tắc gốc (nguyên tắc 124 của board): **người viết ≠ người kiểm**, và **người kiểm không sửa code của
người viết**. Tôi chỉ tạo: báo cáo kiểm + danh sách lỗi có đường dẫn file/dòng + log chạy. Verdict Gate vẫn
thuộc reviewer `8141386a`; tài liệu này chỉ sinh ra **verification report** cho từng lần bàn giao.

## 1. Ranh giới

| Tôi làm | Tôi không làm |
|---|---|
| Chạy lại build/export trong checkout sạch của nhánh coder | Sửa code, preset, asset của coder |
| Diff preset thật với `GODOT_EXPORT_PRESET_CONTRACT.json` | Tự chọn giá trị thay coder |
| Kiểm version/khối lượng/chữ ký từ artifact | Ký hộ, tạo keystore, upload store |
| Kiểm provenance asset (không dùng asset gốc) | Duyệt chất lượng art (session art-designer) |
| Ghi nhãn bằng chứng cho từng kết luận | Nâng verdict Gate (reviewer) |

## 2. Đầu vào bắt buộc mỗi lần bàn giao

Coder gửi 1 comment PR12 (hoặc 1 file trong nhánh) có đủ 8 mục; thiếu mục nào thì báo cáo dừng ở mức
`NOT_READY — thiếu đầu vào`, không tự đi tìm thay:

1. branch + `git rev-parse HEAD` của lần bàn giao.
2. CI run id **theo đúng headSha** đó + kết luận.
3. `export_presets.cfg` (nguyên văn) + `version.json`.
4. `project.godot` (ít nhất các mục `config/version`, `run/main_scene`, `rendering/renderer/rendering_method.*`).
5. Danh sách asset trong project: đường dẫn + sha256 + nguồn (vẽ mới / mua / sinh bằng script).
6. Danh sách plugin ngoài engine: tên, nguồn, phiên bản, **giấy phép**, file `.gdap` nếu là Android plugin.
7. Artifact build: tên file + byte + sha256 (`.exe`, `.pck`, `.apk`, `.aab` nếu có).
8. Log export đầy đủ (không cắt) cho từng preset.

## 3. Bộ kiểm V1–V9

| # | Kiểm | Cách làm | Đạt khi | Nhãn bằng chứng sinh ra |
|---|---|---|---|---|
| V1 | Vệ sinh repo | `git ls-files` lọc `*.keystore,*.jks,*.pfx,*.p12,*.exe,*.apk,*.aab`; so byte từng file > 5 MB | 0 file bí mật; 0 artifact build trong repo; mọi file < 5 MB | `STATIC_CONFIRMED` |
| V2 | Hợp đồng preset | đọc `export_presets.cfg` (INI) → so từng khoá/giá trị với `GODOT_EXPORT_PRESET_CONTRACT.json`; khoá ngoài hợp đồng phải có giải trình | 100 % khoá bắt buộc khớp; không khoá lạ không giải trình | `STATIC_CONFIRMED` |
| V3 | Version nhất quán | `version.json` vs `version/code`, `version/name`, `application/file_version` | cùng một nguồn; code tăng so với lần trước | `STATIC_CONFIRMED` |
| V4 | Ràng buộc engine | kiểm C1–C6 trong contract (AAB⇒gradle, min_sdk ≥ 24, Vulkan ≥ 29, …) | không vi phạm | `STATIC_CONFIRMED` |
| V5 | Tái lập build | checkout sạch đúng headSha, chạy lại `--export-release` từng preset bằng **đúng** Godot `4.7.2-stable` | export không lỗi; log không cảnh báo bị bỏ qua | `RUNTIME_CONFIRMED` (máy tôi) |
| V6 | Cổng kích thước | đo byte thật của `.apk`/`.aab` | APK ≤ 2,5 GB (ngưỡng chặt hơn: Amazon) · AAB ≤ 150 MB (Huawei) | `STATIC_CONFIRMED` (số đo trên file) |
| V7 | Chữ ký | `apksigner verify --print-certs` (nếu có tool) hoặc ghi rõ `RUNTIME_UNVERIFIED` khi thiếu tool | APK/AAB có chữ ký, cert SHA-256 ghi vào báo cáo | `RUNTIME_CONFIRMED` / `RUNTIME_UNVERIFIED` |
| V8 | Provenance asset | so danh sách asset với danh mục gốc (`datas/sprites.csv`, `assets/manifest-full.csv` nếu có); asset trùng tên gốc phải có ghi chú vẽ lại | 0 asset gốc; mọi asset có nguồn khai báo | `STATIC_CONFIRMED` (so tên/hash) |
| V9 | Kiểm claim | mọi câu trong tài liệu coder gắn nhãn phải có nguồn: file+dòng (STATIC) hoặc log/CI (RUNTIME) | 0 claim không nguồn | `STATIC_CONFIRMED` |

Ghi chú công cụ: trong sandbox của tôi **không có** Android SDK/`apksigner`/`bundletool`/Windows SDK.
Vì vậy V7 chỉ chạy được khi user mở quyền cài SDK (Gate-4, USER-ONLY); nếu không, báo cáo ghi
`RUNTIME_UNVERIFIED` **kèm lý do**, không được im lặng bỏ qua.

## 4. Định dạng báo cáo

```
VERIFY [Godot-coder] — headSha <sha> — CI <run id>
V1 PASS/FAIL … (mỗi dòng 1 kiểm + bằng chứng: file/dòng hoặc số đo + sha256)
Verdict nội bộ: APPROVE / APPROVE-BOUNDED / NOT_READY
Không kiểm được: <danh sách + lý do>
Đề nghị sửa: <danh sách, mỗi mục 1 hành động kiểm được>
```

`APPROVE-BOUNDED` dùng khi mọi kiểm bắt buộc đạt nhưng còn mục `UNKNOWN` do môi trường (ví dụ chưa có
SDK để verify chữ ký) — phải liệt kê đúng mục đó, không gộp vào “đạt hết”.

## 5. Những gì tôi sẽ KHÔNG nhận làm bằng chứng

- Ảnh chụp màn hình hoặc video làm bằng chứng “đã chạy” (chỉ là minh hoạ).
- “Máy tôi chạy được” không kèm log + sha256 artifact.
- Artifact không khớp headSha, hoặc file bị sửa sau khi đo.
- Plugin ngoài engine không nêu giấy phép/phiên bản (đặc biệt Spine).
- Số liệu không đọc lại được từ file nguồn.

## 6. Cái protocol này không phủ

- Chất lượng cảm giác chơi, cân bằng, độ vui — thuộc user/playtest, không phải verifier.
- Kết quả review của store, thời gian duyệt, doanh thu.
- Quyền IP/phân phối (Phase C §User-ONLY 3).
- Hiệu năng thật trên Fire tablet/Windows ARM — cần thiết bị, hiện `UNKNOWN`.

## 7. Liên kết

- Hợp đồng preset máy đọc được: `docs/rollout/GODOT_EXPORT_PRESET_CONTRACT.json`
- Spec đóng gói: `docs/rollout/GODOT_BUILD_PACKAGING_SPEC.md`
- Port-plan: `docs/rollout/PORT_PLAN_SCENE_SYSTEM_MAP.md`
- Learning-note native 135: `docs/rollout/LEARNING_NOTE_135_ANIMATOR_PORT.md`
