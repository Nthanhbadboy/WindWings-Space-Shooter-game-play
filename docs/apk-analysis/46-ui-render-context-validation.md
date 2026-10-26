# 46 — Nghiệm thu render-context/Map: chưa được gọi full (PROVISIONAL)

Analyze **40180792800 success**, bot raw **4c8d6461e** đã pull về.
Audit tái lập: `python3 tools/verify/ui_render_audit.py`.
Raw: `reverse-engineering/raw/ui-audit/render-context-audit.json` giữ source/hash.

## Dữ liệu đã lấy được

| Nhóm | Typetree đọc được |
|---|---:|
| Camera | 6 |
| Native Font (chỉ metadata, không binary) | 1 |
| Material | 261 |
| Sprite rect/pivot/PPU metadata | 2.185 |
| TMP_FontAsset | 7 |

TMP names raw: AGENCYB SDF, Agency SDF-Cyrillic, Amiri-Bold SDF,
NotoSansKR-Medium SDF, NotoSansSC-Medium SDF, Roboto-Medium SDF-Currency, SDF-Thai.
Có glyph/face/material/atlas reference trong tree. Không đồng nhất TMP asset
với một file TTF độc lập. Không commit font program/ảnh gốc.

## Hai lỗi nghiệm thu đã phát hiện, không che bằng job success

1. **Native render-context thiếu serialized_file.** Typetree đọc được nhưng
   helper lấy nhầm `object_reader=None` trên raw ObjectReader, nên scope rỗng.
   Layout từ parsed head vẫn có file context đúng (GP_Tutorials ở level2,
   external file3=sharedassets0.assets). Không lấy font path105 trần để nối
   chính xác khi catalog thiếu file scope. Đây chưa phải complete exact join.
2. **Map vẫn bị cắt ở parent có >80 child.** Sau tăng node budget, đã có
   **10.315 node**, pending_transforms=0 nhưng **child_limit_skipped=120**,
   truncated=true. Không thể báo đủ chỉ vì không chạm 12.000 node. Home277 và
   GP_Tutorials126 đều truncated=false trong snapshot này.

Commit **9f4f8fa10** sửa file_context fallback và bỏ cap child80 (vẫn giữ global
node budget12000), thêm test raw-reader/parsed-object scope và missing-context
status. Lượt export sau mới nghiệm thu lại được. Không sửa raw để giả lập scope
hoặc giả lập 120 child chưa đọc.

## Kết quả dùng cho thiết kế

Đã có thêm camera/geometry/font data và routing xác nhận ở report45. Bộ board
và tutorial vẽ reference được. **Chưa chốt full Map/pixel-exact external binding**
cho đến khi sửa pipeline được chạy và audit scope/truncation qua.

Các OPEN runtime không biến mất chỉ vì visual data tăng: popup queue,
Home_Loader consumer, restart persistence, overlay/input state theo coroutine.
