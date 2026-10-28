# 72 — Sprite pixels: crop/flip/mesh-mask reproduction và fractional bounds

**25/10/2026 — provisional/static export audit. Không phải Unity GPU/render approval.**

## Kết quả

Tải lại **assets-v2.zip** đã audit ở report70, kiểm SHA archive và từng PNG nguồn.
Dùng raw geometry report62 để tái tạo Sprite từ **owning Texture2D PNG** bằng một
implementation riêng, không gọi UnityPy SpriteHelper/MeshHandler trong auditor.

**2185/2185 Sprite có cùng size và cùng toàn bộ RGBA bytes với PNG v2**.
Không chỉ so header/bounding box/histogram hoặc hash file PNG nén.
Phạm vi này đóng câu hỏi “v2 Sprite có tái tạo nhất quán từ raw geometry theo
pipeline export đã đọc không?”, **không đóng fidelity với Unity renderer gốc**.

| Đo trong scope | Kết quả |
|---|---:|
| Sprite so sánh | 2185 match /0 mismatch /0 error |
| Texture PNG thực sự dùng bởi các Sprite | 482 |
| Fractional textureRect | 593 |
| Float rect vượt texture bounds | 40 |
| Sau round từng boundary vẫn vượt bounds | **9** |
| Float vượt nhưng rounded box ở trong bounds | **31** |
| Packed rotation0/flipH/flipV/180 | 2041 /53 /54 /37 |
| Separate alpha texture | 0 |
| Mesh UV0 khác0 | 0 |
| Output size khác rounded source_rect width/height | **517** |

Mọi2185mesh đã đọc cóposition float32 stream0 (3components) và UV0 float32 stream1
(2components), stream aligned16bytes, uint16 triangle index buffer/topology0.
UV0 rỗng về giá trị nên dùng polygon triangle-mask path của format-tool; không
im lặng chuyển sang generic UV triangle rasterizer. Layout/UV/index lạ sẽ reject.

## Bốn bước đã kiểm bằng pixels

1. Chuyển Texture PNG top-origin về bottom-origin mà raw rect dùng.
2. Crop theo float textureRect, Pillow round **từng boundary**, không round riêng
   width/height; không clamp cho “an toàn”.
3. Undo packed flip/rotation theo settingsRaw, tạo mask từ mesh positions/triangles
   với pixelsToUnits và normalized mesh minima; giữ alpha có sẵn.
4. Flip lại PNG top-origin. So raw RGBA bytes và hash với v2 Sprite output.

Format references UnityPy1.25.4 SpriteHelper/MeshHelper/enums +license giữ tại
`raw/sprite-geometry/toolchain/`, có wheel provenance. Chúng là **toolchain format
reference**, không phải APK gameplay evidence. Input game là raw object bytes/
geometry đã pin; pixel inputs là v2 media với hash/provenance report70.

Pillow **12.0.0** trong audit CI; local synthetic/regression cũng chạy với Pillow13.0.0.
Đây không phải tuyên bố mọi phiên bản Pillow/Unity crop fractional giống nhau.

## 40 fractional bounds không đồng nghĩa40 PNG hỏng

Chỉ9rounded boxes cần padding ngoài texture:8vượt cạnh trên1pixel,1vượt phải1pixel
(theo raw bottom-origin texture coordinates; cả9unpacked/rotation0).

Trong `data.unity3d/resources.assets`, Sprite pathIDs:

- Top1pixel: **2072,2099,2114,2134,2169,4006,4050,4085**.
- Right1pixel: **4092**.

Ví dụ2072: y≈201.903488,height311,texture height512 → float y+height≈512.903488;
rounded crop `[0,202,311,513]`, output **311×311**, top1pixel padding. Nếu tựclamp
boundary513→512, output thành311×310. Tất cả9counterfactual clamped sizes khác
output v2;31float-outside cases còn lại không đổi size sau rounding.

Auditor tái tạo đúng padding/crop/mask của export tool, không sửa raw thành rounded
hoặc clamped rect. Không kết luận Unity GPU cũng sample border theo Pillow; việc
bỏ clamp trong reference audit không phải luật mới cho game.

## 517 PNG không bằng full source canvas: cẩn thận pivot

Output crop/mask chưa tự dựng lại full source canvas. `source_rect`,
`texture_rect_offset`, `atlas_rect_offset`, raw mesh và source-normalized `pivot`
được giữ riêng. **Không gắn pivot chuẩn hóa của source rect trực tiếp vào PNG đã trim**,
không tự center toàn bộ Sprite vì nhìn ảnh vừa khuôn.

`datas/sprite_export_contract.json.gz` giữ2185typed identities/output paths/hashes,
source_rect/source_normalized_pivot/pixelsToUnits/trim+atlas offsets/export size/
alpha bbox và raw mesh object ref. Nó **không** đưa một công thức final_png_pivot
chưa kiểm qua renderer. Muốn dựng đúng placement phải chọn mesh/full-canvas hoặc
một transform có chứng cứ theo consumer; không đổi registration chỉ để đẹp preview.

## Raw, reproducibility và CI

- Auditor: `tools/recovery/sprite_pixel_audit.py`.
- CI **40196744366 success**, producer commitb624a4ebc; raw bot commit7d2436d66.
- `raw/sprite-pixels/audit.json.gz`:2185rows với crop/source rect/pivot/offset,
  rounded box/padding, decoded mesh proof (payload hashes/counts), expected+actual
  sizes/RGBA hashes, difference extrema, alpha bbox, source PNG SHA/size/path.
  Không commit original media hay pixel dumps vào Git.
- Sources gồm format-reference hashes, geometry chunk hashes, native/metadata/data
  input pins, v2 catalog decompressed SHA và archive SHA. Serialized basename cũ
  chỉ map sang full logical file khi **unique**, không global pathID join.
- `tools/verify/sprite_pixel_contracts.py`: tái kiểm provenance/typed media mapping,
  raw mesh decoding, row metadata, rounded boxes/padding và2185saved match results;
  sinh `datas/sprite_export_contract.json.gz` từ raw đã giữ.

```bash
python3 tools/verify/sprite_pixel_contracts.py
# Pixel audit thực sự cần ZIP ngoài Git và Pillow; không cần APK/full analyze:
python3 tools/recovery/sprite_pixel_audit.py --archive /path/outside-checkout/assets-v2.zip
```

Regression **202tests PASS local** (không skip khi dùng venv cóPillow), datas validationPASS.
7test mới cho float32/uint16 mesh, bad layout/index/truncation/UV, boundary round/padding,
synthetic orientation/alpha-mask;4test contract/provenance,40vs9bounds,517trim/pivot warning.
Verify workflow cài pinnedPillow12 để pixel fixture tests không bịskip trên CI sạch.
Final-commit CI cần kiểm riêng; raw audit CI không thay final regression.

## Còn thiếu thật, không mở lại pipeline không cần thiết

- Unity GPU mesh edge/UV/filtering, compressed texture conversion fidelity,
  PMA/blend/shader/material và scene registration vẫn chưa nghiệm thu.
- Parent transforms/nine-slice/borders/pivot consumer phải đọc khi gắn sprite cụ thể,
  không suy toàn UI từ một geometry table hoặc ảnh xem nhanh.
- Spine associations/reference folders report71 vẫn hiện hành; audit này không
  render Spine hay xác nhận material replacements đúng trên engine mới.
- Font fallback/localization và nghe audio vẫn mở. Không cần rerun asset export,
  invent texture0×0, redraw screenshot, Premium hoặc pool-history proof để tiếp.
