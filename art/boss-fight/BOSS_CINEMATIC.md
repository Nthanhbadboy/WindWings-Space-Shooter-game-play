# Boss-37001 DREADNOUGHT — kịch bản trình diễn CHƯA RENDER

Nguồn: Boss Book §3.2A D tại commit `5701bed`; số và điều kiện theo `BOSS_SPEC.md`. GIF là trình diễn art, không phải logic game. **Đầu ra bắt buộc ≥40 giây**, đủ 7 tiết mục và ba hồi; clip tối thiểu cũ không được gọi là nâng cấp. Trình tự chi tiết và thời lượng ngoài các con số chốt dưới đây là **[ĐỀ XUẤT]**, chưa khóa.

| # | Tiết mục bắt buộc | Trình bày / kiểm tra | Trạng thái |
|---|---|---|---|
| 1 | Ép sân, Hồi 1 | tiến 2s; BigGun trái ngắm trực tiếp, phải bắn dự đoán hướng di chuyển 0,35s; ụ vai chỉ bắn khi tàu ở 1/3 trên; lui, lõi hở 1,0s | CHƯA: chưa có thân 11 điểm và GIF |
| 2 | Lưới chéo, Hồi 1 muộn/Hồi 2 | hai vai bắn chữ X; hai hông bắn quạt sau 0,25s; hai lớp chừa hành lang di chuyển chéo nhìn được | CHƯA: chưa có 4 ụ phụ |
| 3 | Dồn vào tia, Hồi 2 | ụ phụ ép ngoài vào giữa trong 1,2s; cảnh báo trên vùng còn trống, tia hướng sang phía tàu bị dồn; hết tia lõi hở 1,2s | CHƯA: chưa dựng |
| 4 | Bão tên lửa có điều kiện, Hồi 2 | tàu đứng yên >0,8s hoặc trong vùng nhỏ mới reticle bám 0,8s → khóa → 4 cặp khi 2 pod còn; BigGun bắn thưa lúc tên lửa bay | CHƯA: chưa có pod 8 ống hay dàn cảnh điều kiện |
| 5 | Phá ụ và đổi tính cách, mọi hồi | một bộ phận lớn bị phá → dừng 0,4s, điện tại đó, đầu biến mất, đế cháy; đổi vòng đòn **ngay**; BigGun còn lại Overdrive hoặc theo hệ quả tương ứng | CHƯA: chưa có lớp phá/lịch chuyển đòn |
| 6 | Vòng xoáy tuyệt vọng, Hồi 3 <30% | thân cháy bậc 3, ụ sống nhanh ×1,3, tỏa ±6°; 2 vòng thường rồi tia quét 2 chiều; lõi mở lâu hơn + quạt lõi dày hơn; <15% nếu phá thêm 1 bộ phận thì bỏ một lượt tia | CHƯA: chưa dựng bộ phận/quạt, nhánh bỏ lượt |
| 7 | Chết dây chuyền ≥3,5s | bộ phận đã phá cháy lại → ụ còn sống nổ → pod nổ → điện thân → lõi trắng 0,3s → nổ chính + 3–4 mảnh + sóng → khói tàn 1s | CHƯA: clip chết cũ không phản ánh cấu tạo mới/trạng thái phá |

Khi render phải có clip/sheet/manifest ghi xuất xứ layer, mốc và các điều kiện minh họa; tự xem không tiếng, kiểm câu chuyện và tổng thể ở cỡ game. [ENGINE] khe né, logic dự đoán, điều kiện khóa, HP bộ phận và dọn đạn chuyển coder QA; GIF không chứng minh runtime và coder không được nhúng GIF.
