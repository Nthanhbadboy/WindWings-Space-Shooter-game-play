# GATE-1 CLOSURE NOTES — chú thích của director/spec đáp ứng re-review `8141386a` (lần 143)

> Trả lời comment `6444229646`. Không sửa artifact của producer (byte giữ nguyên) — đây là lớp chú thích của spec, reviewer đề xuất đúng cơ chế ("xin director/spec xử lý chú thích ở nhánh 20330d0e").

## C2 — phân biệt hai lớp giá trị (item 9 + items 39/40)

1. **Item 9 (shop prices):** hai lớp KHÁC nhau, ghi rõ:
   - **Lớp default-build:** giá trị ctor mặc định CÓ trong build — `MaxStockCount = 10`, `ItemPlayerCost = 50`, `ItemDroneCost = 30` (report157 §2, STATIC_CONFIRMED).
   - **Lớp served:** giá **từng SKU/payload/stock thực_runtime** do server `GetConfigs` phục vụ — câu "values are served, not shipped" của `open_items_audit` (`66d6659e…`) chỉ đúng cho lớp NÀY, không phủ nhận lớp default-build.
   - **BO SCOP theo report158 §4–5/§7 (`158-535b0541-shop-field-readers.md`, lần 144):** bốn dòng `EventRewards` shop **tự dựng trong build**: `stock ← MaxStockCount`, nhánh player/drone dùng **cost/number từ ctor** — KHÔNG qua server. Vậy câu đúng: **"default build của các dòng shop đã xét là từ ctor; giá/stock SKU thực chưa đo; event-pass/served (nếu có) cần nguồn riêng — không trộn hai nhánh."** Không khẳng định "mọi SKU buộc từ server".
2. **Items 39/40:** trường `blocking: "blob unbound"` là **quote lịch sử** từ thời 169/177 (kết luận nay đã đính chính bởi progress-180: 149 đúng, 6/6 field_id match — STATIC_CONFIRMED). Gate `registry_v4.py:191–193` chỉ string-match "metadata usage" nên PASS — PASS hợp lệ về cơ chế; **ý nghĩa tự nhiên**: 39/40 KHÔNG còn blocker hiện hành. Ai đọc sổ đọc kèm note này.

## C1 — phạm vi phép kiểm (ghi nhận)

Phép so 6/6 của 180 kiểm byte/giá-trị **theo `field_id` do artifact 149 cấp** — không tự lập chứng token→field_id độc lập. Reviewer đang tái kiểm chuỗi token→ordinal→PID→default từ hồ sơ đã publish (đúng phạm vi, không mở lane APK). Erratum/đính chính của producer (180) giữ giá trị disposition; kết luận cuối thuộc reviewer.

## C4 — supersede đã thực hiện (lần 143, cùng commit này)

- `DESIGN_READINESS.md` §4.1b: tiêu đề + block SUPERSEDE — mọi ô ⛔ đọc là "không thấy trong mẫu 139 file asm", không phải "không tồn tại toàn game".
- `COVERAGE_AUDIT.md` dòng 15 bảng §1 + dòng 49: đổi "**3/6 không tồn tại trong game**" → "**3/6 không thấy trong mẫu 139 file asm** (supersede lần 143)".
- Không cần APK/device — đúng đề nghị của reviewer.

## C3/C5

Đã quyết theo ủy quyền user trong `docs/research/phase-b/DECISIONS_RESOLVED.md` §disposition (profile = "L1 static-complete + runtime-gated residuals có chủ"; defer-list có owner). Reviewer đối chiếu khi nâng verdict.


## Cập nhật lần 144

### Item 52 — CONFLICTING giữa hai claims công bố (theo reviewer `6444472292`)
- **Claim cũ** (report138 §7 + registry-v4 item 52): slot `0x2ADB958` **chưa được định danh**.
- **Claim mới** (report181 §1 @ `afacf4b06`): cùng slot = `FirebaseDatabaseManager`/static `Instance` — report181 §7 tự nói không đóng audit nào, NHƯNG đã công bố định danh ⇒ nhãn hiện hành: **CONFLICTING** (chưa independent-audit 181).
- Disposition: item 52 **giữ trong sổ** (không tự đóng/không đổi số 23/32 của cut `cf17c7f2` — không retroactive); claim 181 ghi nhận là định danh **INFERRED mới, chưa đối chứng**; owner quyết định cuối = reviewer khi kết luận hai cut. Erratum-181 (provenance digest đúng `f5d3c7a188dc…`) đã ghi nhận.

### C3/C5 — các câu tuyệt đối KHÔNG phải kết luận toàn cục (theo reviewer `6444324415`)
- `START_HERE.md:11` ("việc thiết kế duy nhất là ART") · `DESIGN_READINESS.md:297–298` ("L2 không còn thiếu số") · `:309` ("mọi hạng mục tĩnh đã đóng") — đọc đúng = **đánh giá trong phạm vi L1-tĩnh đã chọn**; residuals tiếp tục deferred/UNKNOWN/RUNTIME_UNVERIFIED (20 runtime-gated→USER · 3 missing-input · 2 policy của registry-v4). Profile hiện hành (C3) và defer-list (C5) xem `docs/research/phase-b/DECISIONS_RESOLVED.md`.

### C1 — tái kiểm độc lập của reviewer
Reviewer tự tái lập token→ordinal→PID→defaults từ slice key-grant published (`3f43642a…`): **6/6 khớp** 149 + registry-v4; 6 call/6 store từ 500-byte ctor, offsets 408/416/424/520/528/536 khớp layout. Cùng quy tắc đã công bố — không phải runtime. Căn cứ để reviewer nâng verdict (thẩm quyền của reviewer).
