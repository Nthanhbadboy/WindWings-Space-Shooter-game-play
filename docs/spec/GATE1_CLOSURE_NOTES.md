# GATE-1 CLOSURE NOTES — chú thích của director/spec đáp ứng re-review `8141386a` (lần 143)

> Trả lời comment `6444229646`. Không sửa artifact của producer (byte giữ nguyên) — đây là lớp chú thích của spec, reviewer đề xuất đúng cơ chế ("xin director/spec xử lý chú thích ở nhánh 20330d0e").

## C2 — phân biệt hai lớp giá trị (item 9 + items 39/40)

1. **Item 9 (shop prices):** hai lớp KHÁC nhau, ghi rõ:
   - **Lớp default-build:** giá trị ctor mặc định CÓ trong build — `MaxStockCount = 10`, `ItemPlayerCost = 50`, `ItemDroneCost = 30` (report157 §2, STATIC_CONFIRMED).
   - **Lớp served:** giá **từng SKU/payload/stock thực_runtime** do server `GetConfigs` phục vụ — câu "values are served, not shipped" của `open_items_audit` (`66d6659e…`) chỉ đúng cho lớp NÀY, không phủ nhận lớp default-build.
   - Đọc đúng: item 9 = "default có trong build; per-SKU runtime là server-variable".
2. **Items 39/40:** trường `blocking: "blob unbound"` là **quote lịch sử** từ thời 169/177 (kết luận nay đã đính chính bởi progress-180: 149 đúng, 6/6 field_id match — STATIC_CONFIRMED). Gate `registry_v4.py:191–193` chỉ string-match "metadata usage" nên PASS — PASS hợp lệ về cơ chế; **ý nghĩa tự nhiên**: 39/40 KHÔNG còn blocker hiện hành. Ai đọc sổ đọc kèm note này.

## C1 — phạm vi phép kiểm (ghi nhận)

Phép so 6/6 của 180 kiểm byte/giá-trị **theo `field_id` do artifact 149 cấp** — không tự lập chứng token→field_id độc lập. Reviewer đang tái kiểm chuỗi token→ordinal→PID→default từ hồ sơ đã publish (đúng phạm vi, không mở lane APK). Erratum/đính chính của producer (180) giữ giá trị disposition; kết luận cuối thuộc reviewer.

## C4 — supersede đã thực hiện (lần 143, cùng commit này)

- `DESIGN_READINESS.md` §4.1b: tiêu đề + block SUPERSEDE — mọi ô ⛔ đọc là "không thấy trong mẫu 139 file asm", không phải "không tồn tại toàn game".
- `COVERAGE_AUDIT.md` dòng 15 bảng §1 + dòng 49: đổi "**3/6 không tồn tại trong game**" → "**3/6 không thấy trong mẫu 139 file asm** (supersede lần 143)".
- Không cần APK/device — đúng đề nghị của reviewer.

## C3/C5

Đã quyết theo ủy quyền user trong `docs/research/phase-b/DECISIONS_RESOLVED.md` §disposition (profile = "L1 static-complete + runtime-gated residuals có chủ"; defer-list có owner). Reviewer đối chiếu khi nâng verdict.
