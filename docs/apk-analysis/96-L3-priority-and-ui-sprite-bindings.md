# 96 — Đưa L3 lên ưu tiên chính; thiếu ở sản phẩm nhìn thấy, không ở số lượng bảng

**26/10/2026 — cập nhật theo yêu cầu chủ dự án. Kết luận tạm thời.**
L3 là bộ mặt game: hình ảnh trong đúng cảnh, bố cục, thứ lớp, ánh sáng, chuyển động,
nhịp hiệu ứng/âm thanh và chuyển trạng thái. Không được lấy export assets, test logic xanh,
hoặc số báo cáo native để kết luận phần này đủ. **Đổi ưu tiên: hoàn thiện chuỗi L3 trước;
wing/map-save chỉ đào tiếp khi là dependency cụ thể của cảnh/hiệu ứng cần dựng.**
Không dựng lại game từ screenshot; art mới, tham chiếu raw APK. Screenshot chỉ đối chiếu
flow/bố cục/reference đã cho, không chứng minh native numeric khác build. Không thêm yêu cầu
blind-A/B/người test thật; không đợi screenshot mới để bóc các phần raw đã có.

## 1. Rà lại spec hiện tại, không dùng snapshot cũ

Peer `b000f905b180bd8fb901b55ce9a52bbe554dcf61`: raw snapshot6 docs tại
`raw/peer-review/l3-b000f905/`. DONE§L3/START_HERE đã đính chính “input đủ” thành một phần.
Tuy nhiên README còn mục “L3 bỏ”, “bỏ L2/L3”; DESIGN_READINESS còn câu “chỉ cần nếu làm L3”.
Phải phân biệt lịch sử với chỉ dẫn hiện hành, không để AI triển khai đọc nhầm ưu tiên.
Các counts505 unknown/643 passthrough/27 rig inferred là **peer audit**, chưa phải đo mới ở96.

| Mắt xích L3 | Đã có | Thiếu cần làm, không được đổi thành “đủ” |
|---|---|---|
| Asset identity/ý nghĩa | pixel, mesh, pivot/border, pack v2 có kiểm nguồn | phân vai art/unknown/passthrough; numeric name không là glyph; atlas/rig identities còn phải nối |
| Asset→UI/cảnh | source layout và serialized PPtrs | bảng tra được screen→node→sprite, trạng thái + transform; gameplay prefab→sprite/material/VFX |
| Hình ảnh composited | scene sprite/camera/mask contracts scoped | hierarchy hiệu lực, order/material/blend/light/particle trong cảnh cụ thể; chưa có render reconstruction được nghiệm thu |
| Motion/juice | clip curves, animator graphs, event/receiver và một số consumer | ghép đúng object/state, transitions, thời điểm xuất hiện/tắt, camera/feedback; event inventory không là playback |
| Sound đi với hình | audio rules/trigger consumers | gắn trigger/timeline của cảnh; không coi WAV export là sound design đã tái lập |
| Đối chiếu đầu ra | reference/metrics có số và raw | gate composition/motion/audio chưa chứng nhận; cùng metric không đồng nghĩa cùng hình/trải nghiệm |

Không cần kết luận toàn bộ gameplay thiếu mới giải quyết L3. Cần đóng từng chuỗi sử dụng
nhìn thấy được, giữ source/provenance và ranh giới thực sự của chuỗi đó.

## 2. Làm ngay: UI screen→node→sprite index, không chỉ thêm lời hứa

`tools/verify/ui_l3_bindings.py` tạo **`datas/ui_l3_bindings.json.gz`** (~2.09 MB),
tra theo `sources` và `uses`, mỗi use giữ source index, node/component index, path,
local position/scale/rotation/size, activeSelf và visual_properties raw.
Exact identity phải là `(serialized_file,path_id)` qua PPtr + externals, không join tên toàn cục.

Kết quả đo trực tiếp source hiện có:

| Chỉ số | Kết quả / cách đọc |
|---|---|
| Layout files đang có |55,584 — inventory, **không** số màn độc lập |
| Sources thuộc `_index.csv`, đã join batch này |**797 files /117 class labels** |
| Ngoài index, chưa join batch này |**54,787 files**; không âm thầm gộp vào coverage |
| Sprite component observations trong797 files |**76,806** |
| Exact scoped nonnull PPtr resolutions |**75,749** observations |
| Null sprite PPtrs |**1,057**; không phải failed joins hoặc runtime-invisible |
| Sprite identities khác nhau được tham chiếu |**1,099** `(file,path_id)`; không phải75,749 asset |

Nhiều source chứa nested/repeated layouts. Không coi observations là số sprite duy nhất,
số UI elements runtime hay màn độc lập. Không từ1099 suy phần trăm “game đẹp đã xong”.
Ngoài797 source, dữ liệu legacy có thể chỉ còn tên sprite; tool có nhánh name_candidate_only/
ambiguous_name, **không nâng** unique-name thành exact identity. Không chọn bừa collision đầu.
Mỗi source có SHA256; raw797 layouts và render-context/Sprite.jsonl.gz giữ nguyên trong repo.
Null/missing scope không được fallback sang tên để tạo ra “100% đã gắn”.

**Điểm sửa nhận định:** không phải UI chưa từng có scoped bindings — report43/46 có joins
scoped. Thiếu là bảng đủ rộng/đưa được cho bên design.96 mở rộng thành một index dùng trực tiếp
cho toàn797 indexed sources, chưa lấp54,787 sources ngoài index và chưa là UI rendered output.

## 3. Ưu tiên triển khai từ đây — L3 dẫn đường

1. **UI reference chain:** mở rộng ngoài index theo owner-scope, giữ source classes/duplicates;
   thêm parent effective state, sorting/material/font, selected/pressed/disabled/transition.
   Đi theo Home → chọn màn/tàu/drone → HUD → pause/reborn → kết trận/thưởng;
   màn đã có raw không chờ chụp thêm mới bóc.
2. **Gameplay appearance chain:** player/drone/enemy/boss/bullet/pickup/background → prefab
   → SpriteRenderer/mesh/material/particle/Spine → clip/state/event. Sửa identity/meaning
   dựa raw; không gán sprite ID số thành font, không suy rig identity từ region name.
3. **Motion/feedback chain:** một hành động → hình/đạn/particle → animation/camera → sound
   → cleanup, có timeline đúng source. Combat native chỉ ưu tiên nếu chính chain này cần.
4. **Scene-level reference:** nối các chain trên trong cùng scene/state rồi đối chiếu
   composition/motion/audio bằng máy. Phải có output và kết quả gate thật mới cập nhật pass;
   không dùng median35 screenshots hay854 tests logic để tự nhận L3.

Bản repo vẫn là reverse/reference, chưa có game clone/render pipeline chạy được. Không bịa
screenshot render, không tạo mock rồi gọi là APK output, không thay audit bằng vẽ lại từ ảnh.

## 4. Kiểm tra

12 tests mới: regeneration, input scope/inventory, exact identity, null refs, name collisions,
no-scope/no-name-fallback và source hashes. `datas/validate.py` PASS.
Đây là kiểm index/binding, **không** L3 acceptance. Full CI receipt ghi riêng sau run.
