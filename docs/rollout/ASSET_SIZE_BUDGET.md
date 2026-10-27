# Asset & size budget — APK gốc đo được gì, dùng thế nào cho cổng V6

**Trạng thái: PROVISIONAL.** Mọi con số dưới đây bóc từ 2 artifact có trong repo (không ước lượng):
`docs/apk-analysis/01-apk-inventory.json` (sha256 `537a9d7f…`) và `docs/apk-analysis/04-asset-manifest.csv`
(sha256 `f1a5cf69…`). Bản máy đọc: `reverse-engineering/raw/godot-build-spec/asset-size-budget.json`.

Mục đích: trả lời **“bản Godot có vừa 150 MB AAB không?”** bằng số đo được, và chỉ ra chỗ **không** được cộng.

## 1. Sự thật lưu trữ (container bytes) — `STATIC_CONFIRMED`

| Hạng mục | size (byte) | ZIP-stored | Ghi chú |
|---|---:|---:|---|
| XAPK tổng | 142.125.649 | — | `01-apk-inventory.json:xapk_size` |
| `com.Wind.wings.Space.Shooter.apk` | 118.135.473 | 1.340 entry | `parts[0]` |
| `config.arm64_v8a.apk` | 23.889.752 | 24 entry | `parts[1]` |
| `assets/bin/Data/data.unity3d` | 63.881.856 | **stored** (size = compressed) | bundle nội bộ vẫn nén |
| `assets/bin/Data/resources.resource` | 5.105.184 | **stored** | |
| `assets/bin/Data/Managed/Metadata/global-metadata.dat` | 8.621.240 | 2.460.067 | |
| `lib/arm64-v8a/libil2cpp.so` | 47.011.752 | 13.496.697 | code IL2CPP |
| `lib/arm64-v8a/libunity.so` | 17.783.496 | 7.809.249 | engine |

Đọc đúng: `data.unity3d` **63,9 MB là bản đã nén** (LZ4/LZMA bên trong bundle) và được ZIP *stored* —
nên 63,9 MB là **trần trên của media gốc khi chưa giải nén**, không phải tổng asset thô.

## 2. Census theo loại asset — `STATIC_CONFIRMED` (số đếm) / `UNKNOWN` (ngữ nghĩa `bytes`)

| type | count | bytes | % tổng 3 loại |
|---|---:|---:|---:|
| Texture2D | 653 | 67.205.407 | 40,07 |
| Sprite | 2.185 | 50.625.720 | 30,18 |
| AudioClip | 69 | 49.914.660 | 29,76 |
| **cộng** | **2.907** | **167.745.787** | 100 |

⚠️ **Không được cộng cột này thành “160 MB phải vừa 150 MB”.** Ba lý do kiểm được:

1. **Tổng 167,7 MB > container 63,9 MB** (tỉ lệ **2,63×**) ⇒ `bytes` không phải byte trong ZIP.
2. **Sprite và Texture chồng nhau**: 2.185 Sprite trên 653 Texture2D; 635 Sprite có trường `atlas`;
   62.815 `SpriteRenderer` dùng chung 2.185 sprite ⇒ cùng pixel bị đếm nhiều lần.
3. **Ngữ nghĩa `bytes` = `UNKNOWN`**: cột này do exporter ngoài repo sinh ra
   (`EXPORT_MANIFEST` → `/tmp/apk/unity/export-manifest.csv`, xem `tools/apk-analyze/data_pack.py`) và
   repo **không** có mã xuất cột đó.

Phép thử hình học (để biết nó *gần* cái gì): với 653 texture, `bytes/(w×h)` có **median 0,6821**,
min 0,0130, max 2,1847. Mức ~0,5–1,0 byte/pixel khớp texture **đã nén GPU**; 67 texture tên có tiền tố
`sactx-…-ETC2-…` xác nhận định dạng ETC2 ⇒ nhiều khả năng `bytes` là **dữ liệu texture đã nén + mip**
(`INFERRED`). Không dùng hệ số này để nhân ra tổng: biên độ 168× giữa min và max.

## 3. Atlas vs texture lẻ — `STATIC_CONFIRMED`

| Nhóm | count | bytes | ghi chú |
|---|---:|---:|---|
| `sactx-*` (sprite atlas) | 67 | 32.557.993 | 31,05 MiB; 1024² (21), 512² (17), 512×1024 (9), 1024×512 (6) |
| texture lẻ | 586 | 34.647.414 | 33,04 MiB |
| Sprite gắn `atlas` | 635 / 2.185 | — | 1.550 sprite không có atlas |

Hệ quả cho port: 62.815 `SpriteRenderer` chỉ cần **2.185 sprite** ⇒ số *sprite sheet* Godot cần dựng lại
là **2.185 cell**, không phải 62.815. Đây là chỗ tiết kiệm lớn nhất nếu dựng atlas đúng cách.

## 4. Audio — `STATIC_CONFIRMED` (số đo) / `INFERRED` (định dạng gốc)

69 `AudioClip` = 49.914.660 byte (29,8% census); 8 clip lớn nhất:

| name | bytes |
|---|---:|
| Action Dynamic Track #2 1 MP3 | 7.064.108 |
| Energy Rock Track #2 (looped) 1 | 6.313.004 |
| Energy Rock Track #3 (looped) | 5.863.724 |
| Energy Rock Track #2 (looped) 2 | 5.619.500 |
| Heavy Riff 5 (Looped) | 5.449.004 |
| Bgm_Home 1 | 4.566.572 |
| Bgm_Home 2 | 3.914.540 |
| Bgm_Boss 1 | 2.845.484 |

Đường dẫn đều kết thúc `.wav` trong khi tên clip ghi “MP3” ⇒ đóng gói bên trong chưa chắc là PCM
(`INFERRED`; mã giải mã chưa kiểm). **Không** kết luận “audio gốc 49,9 MB nên bản Godot cũng 49,9 MB”.

## 5. Công thức ngân sách cho V6 (phải tính, không được đoán)

```
media_budget = gate_bytes − engine_bytes − script_bytes − pck_overhead
```

| Vế | Trạng thái | Giá trị dùng được |
|---|---|---|
| `gate_bytes` | `STATIC_CONFIRMED` | AAB 150.000.000 · APK 2.500.000.000 · MSIX `UNKNOWN` |
| `engine_bytes` (Godot template) | `UNKNOWN` | phải đo từ artifact export đầu tiên |
| `script_bytes` | `UNKNOWN` | phải đo |
| `pck_overhead` | `UNKNOWN` | phải đo |
| media hiện có | `STATIC_CONFIRMED` | 63.881.856 B (`data.unity3d`, đã nén) |

Mốc so sánh duy nhất đang có: APK gốc dùng **70,3 MB native + 63,9 MB media** cho 118,1 MB file.
Bản Godot **không** kế thừa con số native đó — nên chỉ ghi nhận như bậc độ lớn (`INFERRED`), không
trừ thẳng vào 150 MB.

## 6. Đòn giảm byte (xếp theo mức chắc chắn)

| # | Đòn | Bằng chứng | Rủi ro |
|---|---|---|---|
| L1 | Dựng lại 2.185 sprite thành atlas thay vì 62.815 file | 62.815 renderer / 2.185 sprite | mất đúng pixel gốc |
| L2 | Texture giữ ETC2/ASTC 0,5–1 B/px thay vì RGBA32 (4 B/px) | median 0,6821 B/px | chất lượng trên màn hình lớn |
| L3 | Audio sang Vorbis/Ogg (Opus cho SFX) | 69 clip, 8 clip nặng 41,6 MB | loop point sai nếu không khai đúng |
| L4 | Bỏ asset không dùng: đếm `Sprite` không có `SpriteRenderer` | cần join `sprites.csv` | cắt nhầm animation |
| L5 | Split AAB theo màn/level để hạ 150 MB | — | phức tạp pipeline, AppGallery chưa xác nhận dynamic delivery |

## 7. Cổng & câu hỏi mở

- Gate V6 chạy bằng `stat -c '%n %s'` trên artifact thật (`GATE4_BUILD_CHECKLIST.md` §2 bước 5).
- **Chưa chốt:** ngưỡng MSIX của MS Store (`UNKNOWN`); engine/script byte của Godot (`UNKNOWN`);
  ngân sách media mục tiêu do USER chọn (gợi ý ≤ 90 MB để chừa chỗ, **không phải** số đã xác minh).
- Bảng này **không** là giấy phép dùng lại asset gốc: quyền IP vẫn là câu hỏi USER (Phase C, User-ONLY 3).

## 8. Tái lập (chạy lại đúng 2 input)

```bash
sha256sum docs/apk-analysis/01-apk-inventory.json docs/apk-analysis/04-asset-manifest.csv
# 537a9d7fe9ae44b5ec5238d3e82f9b2c20d8dd28d888862a66d4ed05d5de0118  (inventory)
# f1a5cf69d9562bb95ba0a43c71fbf4888d73682f4f265bb0f3ef143023451e54  (manifest csv)
python3 - <<'PY'
import csv,collections
rows=list(csv.DictReader(open('docs/apk-analysis/04-asset-manifest.csv')))
c=collections.Counter()
for r in rows: c[r['type']]+=int(r['bytes'])
print(c, sum(c.values()))
PY
```

Kỳ vọng: `Counter({'Texture2D': 67205407, 'Sprite': 50625720, 'AudioClip': 49914660}) 167745787`.
Lệch một byte ⇒ input đã đổi, **không** dùng bảng này.
