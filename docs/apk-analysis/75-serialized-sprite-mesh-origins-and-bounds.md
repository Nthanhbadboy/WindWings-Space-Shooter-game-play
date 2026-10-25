# 75 — Sprite mesh gốc, origin và bounds: không đoán pivot của PNG đã trim

**Tạm thời/static, 25/10/2026. Không phải Unity scene-placement hoặc GPU approval.**

## Phạm vi và nguồn

Follow-up report72: giữ mesh đã serialize thành bảng dùng được, thay vì chỉ giữ
PNG crop/source-pivot rồi để implementation tự đoán điểm đăng ký.
Không bóc lại APK, không xuất lại media, không đọc screenshot để dựng hình.

Nguồn có sẵn:
- `reverse-engineering/raw/sprite-geometry/index.json`, `objects-000..005.jsonl.gz`:
  Sprite `m_RD.m_VertexData`, index buffer, submeshes, source rect/pivot/PPU.
- `reverse-engineering/raw/sprite-pixels/audit.json.gz`: exact RGBA reconstruction report72.
- `datas/sprite_export_contract.json.gz`:2185typed Sprite identities/PNG paths/hashes/offsets.
- Strict decoder `tools/recovery/sprite_pixel_audit.py`: float32 positions, uint16 triangle
  indices; reviewed layout/alignment/submesh restrictions, zero UV0 checked as before.

Nguồn APK là các raw trên. `raw/sprite-meshes/derivation.json` là **derivation metadata**,
không phải capture APK mới; giữ decoder hash, source chunk hashes, contract hash và summary.

## Deliverable

`datas/sprite_mesh_contract.json.gz`, sinh bằng `tools/verify/sprite_mesh_contracts.py`:

- **2185Sprites,27072vertices,24375triangles**.
- Typed owning-file + Sprite pathID, raw object SHA, vertex/index payload SHA.
- Position floats và triangle indices giữ nguyên thứ tự, không scale/recenter/flip/repair.
- Serialized submeshes/localAABB giữ riêng với measured vertex bounds.
- Source normalized pivot, source rect/offset/border/PPU, PNG path/hash/export offsets giữ riêng.
- Mesh-origin diagnostics không được đổi tên thành PNG pivot/Transform.

`origin_relative_to_mesh_aabb[i] = -min(position[i]) / (max(position[i])-min(position[i]))`

Đây chỉ là phép tính vị trí origin so với XY bounding box của decoded vertices.
Không có texture sampling, parent transform, renderer flip, animation hoặc material trong
phép tính. Không suy công thức mapping nó lên trimmed PNG hoặc scene từ bảng này.

## Kết quả đọc và tính trực tiếp

| Quan sát | Kết quả |
|---|---:|
| Mesh vertex-count khác4 |1652|
| Mesh có z khác0 |0|
| PPU distinct serialized values |497|
| PPU=100 |980Sprites|
| Mesh-AABB origin khác source normalized pivot quá1e-5 |467|
| Mesh origin ngoài XY AABB, strict arithmetic |7|
| Ngoài XY AABB quá1e-5 |6|
| Serialized submesh localAABB center/extent đều0 |2185Sprites|

Không mặc định PPU=100 cho mọi Sprite. Ngưỡng1e-5 là **reporting tolerance mới**, không phải
APK branch, snapping rule hay tiêu chuẩn nghiệm thu.

Ví dụ `resources.assets:3050` (`RankA`) có origin-relative-to-mesh-AABB x≈−0.2317073;
`3304` (`RankS`) x≈−0.2696629; `2316` (`Than2`) y≈−0.2440476.
Không clamp về[0,1] hoặc tự recenter mesh để làm pivot trông hợp lý.

7strict-outside IDs đều `resources.assets`:2146,2316,2692,2836,3050,3304,3687.
**2836 chỉ x≈−3.076e−8**; vì thế giữ riêng strict vs tolerance counts, không gọi cả7 là
lỗi placement. Cũng không sửa near-zero thành0 trong dữ liệu gốc.

**2185serialized submesh localAABBs đều zero** trong raw đang xét. Measured bounds của
vertices không zero. Không lấy field zero đó làm actual visible bounds; cũng không overwrite
raw bằng measured bounds hoặc tự kết luận vì sao Unity lưu zero.

### Triangle cross-sign inventory, không tự sửa winding

Tính `(bx-ax)*(cy-ay)-(by-ay)*(cx-ax)` bằng Python float trên decoded float32 coordinates:
- negative24013, positive17, exactly-zero345.
- Positive xuất hiện ở13Sprite meshes; exactly-zero ở110meshes.

Đây không phải GPU front-face/culling verdict: coordinate transform, precision và shader
chưa chạy. Không đổi winding hoặc xóa zero-area triangles để “sửa” raw.
All-zero UV0 trong layout đã kiểm vẫn giữ nguyên; **không bịa atlas UVs từ nó**.

## Kiểm lại và giới hạn

```bash
python3 tools/verify/sprite_mesh_contracts.py
python3 -m unittest discover -s tests -v
python3 datas/validate.py
```

Verifier tái dùng pixel-contract provenance checks, rồi decode mesh từ raw và đối chiếu
object/payload/source hashes. Không cần tải ZIP và không chạy lại pixel comparisons trong
bước này; report72 đã có audit media riêng. Không nâng unit tests thành runtime approval.

6tests mới: regeneration/source hashes, origin ngoài bounds không clamp, winding/zero-area
không repair, invalid/nonfinite input rejection, real census/bounds distinction và sourcepivot
khác mesh-origin diagnostic. Không thêm PNG/ZIP/APK/native binary vàoGit; release không đổi.

**Local:224tests PASS** (Pillow13), datasvalidation PASS. FinalVerify của code bàn giao
được kiểm riêng; không dùng PASS để nâng mesh inventory thành rendered placement.

## Task peer

`arena/20330d0e-windwings-space-shooter-game-p`, xem `docs/HANDOFF_AI_TASKS.md`:
1. Dùng typed mesh contract khi cần source geometry; không mặc định mọi Sprite là quad/PPU100.
2. Source normalized pivot, measured mesh bounds, serialized zero localAABB và trimmedPNG
   registration là các khái niệm khác nhau. Không gộp/clamp/repair theo tên field.
3. Nếu implementation dùng quad hoặc tự đặt pivot thay geometry gốc, ghi rõ new design/
   approximation, không nâng thành APK-equivalent placement.
4. Actual UV generation, renderer transforms/material/flip và scene placement còn mở;
   cần consumer/engine validation cụ thể. Không cần full APK export/Premium/pool-history.
