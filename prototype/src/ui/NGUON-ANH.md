# Nguồn ảnh nền — ảnh thật, không vẽ lại

Quy tắc của dự án (D19 + D20): **nền chỉ dùng ảnh thật**. Ảnh vẽ lại (gradient, tinh vân bằng
cọ mềm, Trái Đất bằng fbm) không bao giờ giống được, và mắt người nhận ra ngay.
**Vẽ không đẹp thì bỏ, không vẽ bù.**

| File | Ảnh gì | Kích thước | Nguồn | Giấy phép |
|---|---|---|---|---|
| `sky_deep.jpg` | Hubble Ultra Deep Field — **lớp xa nhất, đứng yên tuyệt đối** | 2560×2560 (gốc 4000²) | NASA / ESA (wallpaperaccess "hubble 4k") | NASA/ESA: phạm vi công cộng |
| `nebula_a.jpg` | Tarantula Nebula (30 Doradus) — teal/amber, **lớp thứ 2, trôi** | 2560×2016 (gốc 3840×2160) | ESO/NASA Hubble (wallpaperaccess "nebula 4k") | phạm vi công cộng |
| `nebula_b.jpg` | cùng ảnh Tarantula, vùng xanh tím | 1760×1188 | như trên | như trên |
| `nebula_c.jpg` | Carina — "Mystic Mountain", Hubble | 1100×1650 (gốc 1279×2575) | NASA / ESA (science.nasa.gov) | NASA: phạm vi công cộng |
| `nebula_haze.jpg` | tinh vân xanh/lam (Hubble) làm mờ 22 px — **sương màu của lớp 2** | 1920×1080 (gốc 3840×2160, cắt bỏ 260 px đáy có watermark) | wallpaperaccess "hubble 4k" | phạm vi công cộng |

## Xử lý đã làm (PIL, ghi lại để làm lại được)

1. `sky_deep.jpg`: Deep Field 4000² → **2560² LANCZOS**, JPEG q82. Không cắt, không ghép, không vẽ.
2. `nebula_*.jpg`: cắt vùng có cấu trúc → resize LANCZOS → **nướng vignette**:
   nhân ảnh với `smoothstep` 4 cạnh (biên 22 %), luỹ thừa 1,45 → mép về 0.
   Nhờ vậy khi `AdditiveBlending` mép ảnh **biến mất**, không thấy khung chữ nhật.
   Script tái lập được: `python3 docs/tools/nebula_tiles.py` (hộp cắt ghi trong file).
3. **Không** tăng độ bão hoà, **không** vẽ thêm sao, **không** ghép ảnh.

Độ sáng hạ trong **code**, không sửa file: `backdrop.js` → `material.color` (nền `#9e9e9e`,
mây `0,72`). Đổi độ sáng chỉ sửa một số.

## Ảnh cũ đã bỏ (D20)

- `sky_nebula.jpg` (Carina 1100×2214, lớp xa cũ) — **thay** bằng `sky_deep.jpg` vì độ phân giải thấp.
- `earth.jpg`, `earth_clouds.png`, `earth_lights.png` — map NASA thật nhưng **Trái Đất đã bị bỏ khỏi
  game**; không còn file trong thư mục này. Cần lại thì tải từ
  `https://github.com/mrdoob/three.js/tree/dev/examples/textures/planets`.

## Ảnh mới thay vào thì phải

1. Là ảnh thật, độ phân giải **≥ 2000 px** cạnh dài (nền chính ≥ 2500 px).
2. Nền tĩnh: tỉ lệ tuỳ ý (code dùng `cover`), nhưng **càng vuông càng ít mất chi tiết**.
3. Mây trôi: nếu muốn mép tan thì nướng vignette; đặt tên `nebula_*.jpg` và khai báo trong
   `src/art.js` → `BACKDROP_ART`, thêm dòng vào `CLOUD_DEFS` trong `backdrop.js`.
4. Ghi dòng mới vào bảng trên, kèm nguồn + giấy phép.
