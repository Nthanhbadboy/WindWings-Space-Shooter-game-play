# 97 — L3: rà toàn55.584 layout, nối trạng thái/hình học/material/font

**26/10/2026 — tạm thời.** Tiếp report96, không quay lại backlog wing. Hai kết quả
khác nhau: audit **tất cả saved layouts**, và composition metadata cho **797 current-index
layouts**. Không lấy kết quả audit lịch sử làm scene/asset identity mới hoặc rendered approval.

## 1. Không bỏ54.787 file ngoài index, cũng không coi chúng là54.787 màn thiếu

Tool `tools/verify/ui_layout_inventory.py` đã đọc/decompress/phân tích **55.584 files**,
giữ SHA256 từng file, root_path_id/class/node count/scope/features. Data:
`datas/ui_layout_inventory.json.gz` +4 shards `datas/ui-layout-inventory/*.json.gz`.
Source raw không bị xoá/gộp; mọi artifact mới <5MB. Full source-hash regression kiểm tất cả
files, không chỉ lấy mẫu. Scan đầy đủ mất~132s; regression hash/manifest không phải scan semantic lại.

| Đo trên saved export files | Kết quả |
|---|---:|
| Current `_index.csv` |797 files /117 class labels |
| Ngoài current index |54.787 files |
| Class label chỉ có ở ngoài index |**0** — không có nghĩa không có state/variant mới |
| Sprite observations ngoài index chỉ giữ tên |**3.843.228** |
| Sprite observations ngoài index còn scoped `m_Sprite` |**0** |
| TMP components ngoài index |**1.003.504**, không có `m_fontAsset` PPtr trong layout record |
| Groups theo class + common drawing-topology fingerprint |**30.827** |
| Ngoài-index files có cùng fingerprint với indexed candidate |**14.081**, thuộc409 groups |
| Groups không có indexed candidate |**30.418** |

Fingerprint giữ path/depth/name/active/transform/rect và component class/sprite-name/text/key;
**cố ý không** có material/font/serialized PPtrs vì schema legacy không giữ chúng.
Đây là topology candidate grouping, **không phải** semantic dedup, same prefab hoặc asset identity.
Test thay sprite PPtr nhưng giữ tên cho cùng fingerprint chứng minh không được truyền bindings
797 sang14.081 files để “đóng thiếu”. Cũng không xoá30.418 groups không match rồi coi là rác.
Không nhân3.843.228 observations thành số sprite/đối tượng runtime.

**Sửa hướng đọc report96:** “54.787 chưa join” không có nghĩa game có54.787 màn độc lập
chưa biết. Cùng117 class labels đã hiện diện trong index; thiếu thật ở scope/state/biến thể và
references đã mất trong summaries cũ. Muốn exact identity phải trở lại serialized source,
không kéo dài name-join hoặc đếm file export thay tiến độ L3.

## 2. Artifact composition dùng được, thay vì chỉ sprite→node

`tools/verify/ui_composition.py` → `datas/ui_composition.json.gz` +6 shards
`datas/ui-composition/*.json.gz` (~2.8MB tổng shards). Mỗi visual-component record giữ:

- source index/hash, node/component index/path;
- parent index/status, activity serialised trong layout-root;
- matrix TRS dẫn xuất trong **layout-root frame**, không scene world;
- raw visual_properties: màu/alpha, flip/draw mode/size, sorting layer/order khi có,
  font size/style/autosizing/alignment/margins/wrapping…;
- scoped Material/font references, không tìm theo tên;
- renderer_enabled=unknown khi export không ghi; rect_layout_pending khi có RectTransform.

| Đo trên797 layouts | Kết quả |
|---|---:|
| Visual-component observations |**100.312** |
| Matrix có thể tính theo chuỗi parent path/depth duy nhất |**99.731** |
| Matrix chưa xác định do chuỗi ambiguous/invalid |**581**, không thay bằng identity |
| Serialized within-root activity false / true / unknown |**89.754 /10.409 /149** |
| Material-array entries exact scoped join |**76.802** |
| TMP font exact scoped join |**18.467**, thêm1 null |
| TMP sharedMaterial exact scoped join |**18.467**, thêm1 null |

Các counts là observations/references, không phải số font/material độc lập, không tỷ lệ
L3 đã xong. Font fallback/localization/dynamic material có consumers riêng, không được coi
đã mô phỏng bởi reference join.

### Parent reconstruction và lỗi slash thật trong raw

Source layout không giữ Transform/GameObject PPtrs cho từng node. Không bịa chúng:
edge chỉ chấp nhận unique parent **path + depth** và được ghi `unique_path_parent`.
Có797 roots,149.174 unique-path parents và**160 ambiguous parent nodes**. Những descendants
phụ thuộc ambiguity không có matrix; activity còn có thể false chắc chắn nếu chính nó/ancestor
đã serialised inactive, còn trường hợp thiếu chứng cứ giữ unknown.

Tên thật `TMP SubMesh [TextMeshPro/Sprite]` chứa dấu `/`. Split cuối `/` như filesystem sẽ
bịa thêm một cấp và làm mất1478 parent matches ở phép thử ban đầu. Tool dùng nguyên suffix
`/` + **node.name** để bỏ child khỏi path; có tests cho slash trong node/ancestor name.
Sau sửa, không còn missing-parent case ở dataset này;160 ambiguous vẫn giữ nguyên,
không dùng “match đầu tiên” để nâng coverage. Đây vẫn không phải PPtr-edge proof.

### Không đánh tráo hệ tọa độ/trạng thái

- Root matrix là identity trong **root frame**. Local TRS của root được giữ riêng, không
  giả định scene parent là identity rồi gọi toạ độ world.
- Phép nhân row-major T*R*S/parent*local bằng float64, raw near-unit quaternion;
  không tuyên bố giống rounding Unity/FP32 hoặc engine layout. Invalid/missing TRS không fallback.
- Không chạy anchors/Canvas/ContentSizeFitter/animation/driver layout; local position của
  RectTransform không tự là final on-screen rectangle. `rect_layout_pending` luôn minh bạch.
- activeSelf/ancestor flags thuộc prefab snapshot, không state runtime. Camera culling,
  shader, SpriteMask/occlusion/sorting effects vẫn chưa được thực thi.
- Kiểm exporter hiện tại: visual-property whitelist **không có m_Enabled**, nên toàn bộ
  renderer-enabled chưa xác định. Không tự default=true rồi nhận visible.

## 3. Thiếu gì tiếp để tạo đúng bộ mặt game

**Đổi từ backlog file sang source/scene chains:**
1. Recovery scoped UI node GameObject/Transform/parent/component identities và m_Enabled
   từ APK; giải quyết160 ambiguous parents bằng PPtr, không đoán theo sibling names.
2. Ghép font/material/renderer state với hierarchy + camera/Canvas + dynamic state writers;
   Home → chọn tàu/drone/màn → HUD → pause/reborn → kết trận/thưởng là flow ưu tiên.
3. Nối gameplay appearance prefab→sprite/material/Spine/particles→animation/event/audio,
   để tài liệu không chỉ có phần menu mà thiếu hình ảnh chiến đấu.
4. Sau khi đủ chuỗi scene cụ thể mới dựng/đối chiếu output composition/motion/audio.
   Asset/matrix/reference export không là rendered acceptance; không vẽ từ screenshot.

Raw nguồn giữ nguyên, index/shards/input hashes giữ cùng derived output. Report62 đã cảnh báo
raw UI tích lũy nhiều run;97 **không** phủ nhận cảnh báo đó: đây là lần full scan/hash/feature
và topology grouping, không biến provenance cũ còn thiếu thành exact APK identity.

## 4. Kiểm tra

37 tests mới (15 inventory,22 composition), thêm lifecycle cleanup cho12 tests96 để nhả
large decoded artifacts giữa test classes. Negative cases: duplicate parent path, missing/depth
mismatch, inactive ancestors, unknown activity, slash names, rotation+scale+translation,
zero/negative scale, invalid quaternion/nonfinite inputs, scoped references/nulls và topology≠identity.
`datas/validate.py` PASS. Full suite receipt ghi sau CI; không phải L3 visual gate.

### Regression/CI receipt

- Full903 tests local PASS73.060s;49 UI-focused PASS14.659s, datas validate PASS.
- Sau đó pin phép cộng float của matrix thành left-to-right rõ ràng: built-in `sum`
  thay cách cộng float từ Python3.12, không để snapshot phụ thuộc interpreter. Source matrix
  chunks trên Python3.11 giữ nguyên; header hash cập nhật.22 composition tests chạy lại PASS.
- Chuyển regeneration comparison sang từng record để lỗi không sinh diff100k records gây
  chẩn đoán tốn bộ nhớ/thời gian. Không thay đổi asserted fields hay tolerance để “làm xanh”.
- **Codec915ac075, Verify40226781914 SUCCESS/job1m51s**, kiểm full suite trên Python3.12.
  Run đầu40226331214 là run cũ bị supersede; snapshot riêng giữ status thật, không ghi thành PASS.
  Không khẳng định đã lấy log chứng minh nguyên nhân chậm run cũ; cancellation API trả403.
- Peer ACK96=6402053761 đã nhận/lưu raw; chưa gọi đó là independent review spec cập nhật,
  chưa tự ACK97. CI/handoff receipts cùng `raw/l3-ui/`. Đây không phải L3 render acceptance.
