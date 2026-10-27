# SELF-REVIEW — hero PLAYER ID 10001, hướng A Ink & Ember (pass hero-first)

Session `arena/f2272cda-windwings-space-shooter-game-p` · 2026-10-27 · VISION-ATTEST: CÓ
Vai: Art-designer-A thay `5438fec9` (USER đã đóng session cũ). Cổng duyệt: Art-style-auditor
`arena/65f8a31f` — tôi KHÔNG tự tuyên bố art đã được duyệt.

## 1. Đã cải thiện gì so A cũ (`125e1e33`, cùng slot)
Xem cạnh nhau ở `compare/vs_old_a_same_slot.png` và hàng 3 của `preview/verify_64_true_size.png`:
- **Cấu trúc cơ khí:** A cũ = thân nón xám một dải gradient + 4 vây cam chữ nhật dán bên +
  2 vòi phun chấm cam (giấy cắt). Bản mới = 2–3 lớp giáp chồng có mép tấm, bản lề bulông ở
  gốc cánh, khối đuôi có tấm giáp, khe sensor mũi, anten — chi tiết gắn vào nơi có lý do chịu lực.
- **Vật liệu:** kim loại gunmetal có 5–6 bậc sáng/tấm + AO trong khe + rim-light trên; kính canopy
  phát hổ phách có vệt specular; emissive nozzle tách hẳn kim loại. A cũ không có phân biệt vật liệu.
- **Lặp hình:** A cũ dùng chung một thân nón cho #01/#08/#13 (auditor đã nêu). Bản mới là thiết kế
  riêng cho slot 10001, không dùng lại công thức.
- **Đọc ở 64 px:** silhouette delta + canopy hổ phách + vent ember + glow đuôi giữ được trên cả nền
  caro lẫn nền gameplay ink900; A cũ ở 64 px chỉ còn cục xám với 4 chấm cam.
- **Số planner (raw, không sửa ngưỡng):** A cũ lệch 2 dải (colors 676, val_std 0.232); bản mới
  lệch 1 dải (colors 1413). dark_share 0.049 → 0.007; val_std 0.232 → 0.241.

## 2. Điểm còn yếu (tự nêu, không chờ auditor chỉ)
- **`colors` = 1413 ∉ [110,160]** — lệch duy nhất còn lại và là lệch cố hữu: dải này hiệu chuẩn
  trên contact-sheet JPEG đã downsample (ART_STUDY §5 thừa nhận JPEG làm `colors` thành cận dưới),
  còn bản nộp là PNG 256 vẽ mịn có vi-xước kim loại. Giảm `colors` đồng nghĩa làm phẳng bề mặt
  (phá 2.5D) nên tôi không đổi art để đuổi số này; ghi rõ để auditor/user phán quyết.
- **Bề mặt giữa cánh còn thưa chi tiết** so mật độ greebles của gốc (gốc có mảng decal/khe phụ);
  vòng redo sau nên thêm 1–2 đường panel chìm + decal số hiệu ở mặt trên cánh.
- **Hue tím trong bóng đổ** (dĩ vãng của nền magenta) vẫn còn rất nhẹ ở khe tối nhất; không thấy
  ở 64 px nhưng soi 4× thì có.
- **Bất đối xứng có chủ đích mới chỉ ở anten**; gốc #1 có bất đối xứng decal mạnh hơn.
- Bản 64 px lấy từ 256 bằng LANCZOS, chưa làm bản 64 "hand-tuned" (giản lược chi tiết có chủ đích
  cho cỡ nhỏ) như pipeline thương mại thường làm.

## 3. Những gì CHƯA kiểm / không tự nhận
- KHÔNG kiểm runtime Godot, không mock gameplay 0.2 s, không test ba người —
  **[RUNTIME_UNVERIFIED]**.
- KHÔNG tự chấm ĐẠT cổng thẩm mỹ/kỹ thuật — quyền của auditor `65f8a31f`.
- Chưa đối chiếu trên atlas thật/ép khuôn UV; chưa kiểm bleed 1 px cho atlas packing.
- `measure_asset.py` chạy NGUYÊN BẢN (sha256 `c3318234…b053` từ nhánh planner `1b836828`),
  kết quả raw trong `measure/`. Số máy chỉ là proxy: không chứng minh từng panel đạt 3–5 bậc sáng
  và không chấm được đẹp.
- CI: xem comment PR12 kèm headSha — nếu 0 check-run thì ghi UNKNOWN, không ghi PASS.

## 4. Bảng số raw (planner nguyên bản, class ship)
| bản | colors | val | val_std | dark | chroma | fill | lệch |
|---|---|---|---|---|---|---|---|
| A mới (nộp) | 1413 | 0.505 | 0.241 | 0.007 | 0.221 | 0.320 | colors |
| A mới chưa grade | 959 | 0.339 | 0.199 | 0.163 | 0.148 | 0.310 | colors,val,val_std,dark,chroma |
| A cũ @125e1e33 | 676 | 0.511 | 0.232 | 0.049 | 0.223 | 0.239 | colors,val_std |

Dải ship: colors [110,160] · val [0.46,0.52] · val_std [0.24,0.30] · dark [0.00,0.10] · chroma [0.19,0.23].
Style 2.5D (grad_stops/outline_px/detail) chưa chạy riêng ở đây vì script planner in chúng ở chế độ
`--dir` cùng bảng trên; bản nộp không có viền đen (dark 0.007) nên outline dày không tồn tại.

## 5. Đối chiếu gốc (bắt buộc)
`compare/compare_index.csv` + `compare/pair1_true_10001.png` (TRUE — đúng ID 10001) +
3 cặp ANALOGUE (#13, #19, #20) ghi rõ không cùng ID; cùng footprint 256×256, subject 86.7% canvas
(= tỉ lệ ô gốc 130/150). Hash sheet + hash từng crop + hash sprite nộp đều trong CSV.
