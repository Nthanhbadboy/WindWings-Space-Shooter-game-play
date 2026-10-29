# 01 — CHIẾN DỊCH, WAVE & ĐỊCH

## 1.1 Cấu trúc chiến dịch

Nguyên mẫu tổ chức nội dung theo **chặng (stage) → wave**, boss trấn ở cuối
chuỗi chặng, lưu sao theo `StarStageMaster{stageIndex}_{modeIndex}` [gốc],
3 chế độ khó với `levelDelta [1, 2, 3.6, 3.6]` (chỉ scale thưởng/khó,
không nhân số quân) [gốc].

Thiết kế làm mới:

- **[SLICE]** Một "chặng mẫu" hoàn chỉnh: 5 wave (Wave_0016–0020, 343 lượt
  địch theo dữ liệu đã cài) + Boss-37001 cuối chặng + màn kết quả 3 sao.
  Đây là đơn vị nội dung chuẩn: mọi chặng sau nhân theo khuôn này.
- **[MỞ RỘNG]** Chiến dịch chia **chương**: mỗi chương 1 vùng không gian có
  danh tính riêng (xưởng đóng tàu, vành đai thiên thạch, pháo đài lõi...)
  gồm nhiều chặng; cuối chương là boss lớn. Độ khó 3 chế độ mở sau khi
  thắng thường, đúng tinh thần levelDelta của gốc.
- Nhịp trong 1 chặng: wave 1–2 dạy ý đồ mới → wave 3–4 kết hợp ý đồ →
  wave 5 dồn dập "khảo bài" → boss tổng kết. Không wave nào chỉ tăng máu.

## 1.2 Ngữ pháp wave (học từ 282 wave của gốc)

`waves.json` của gốc có 23.757 spawner, địch vào theo **đường bay (path)**
và **đội hình**, không rải ngẫu nhiên. Trích ra thành thư viện ý đồ dùng lại:

| Ý đồ wave | Mô tả | Cảm giác |
|---|---|---|
| Sóng tràn | Hàng ngang địch nhỏ tràn từ trên xuống theo nhịp | Khởi động, xả đạn thỏa tay |
| Kẹp hai cánh | Hai đội xiên vào từ 2 góc, ép người chơi ra giữa | Buộc di chuyển ngang |
| Vòng cung đạn | Địch chậm đứng bắn tỏa có nhịp | Đọc đạn, len khe |
| Đuổi bắt | Địch nhanh lao theo hướng người chơi từng đợt | Căng thẳng, buộc né sớm |
| Lá chắn sống | Địch trâu đi trước che địch bắn tỉa sau | Ưu tiên mục tiêu |
| Mồi & bẫy | Nhóm yếu đi trước, nhóm mạnh ập vào khi người chơi lao lên | Dạy kiềm chế |

**[SLICE]** 5 wave hiện có phải đọc ra được ít nhất 4 ý đồ khác nhau;
**[MỞ RỘNG]** mỗi chương thêm 1–2 ý đồ mới, không lặp nguyên xi ý đồ 2
chặng liên tiếp.

## 1.3 Sách địch (bestiary) — từ 70 prefab của gốc

Gốc có 70 địch thường, 399 đường bay, HP theo **id địch** (không theo wave)
[gốc]. Làm mới theo họ hành vi — mỗi họ: hình dấu ấn + hành vi + vai trò:

| Họ | Dấu ấn hình | Hành vi | Vai trò trong trận |
|---|---|---|---|
| CB — Chiến đấu cơ | Nhọn, gỉ đỏ | Bay đường cong, bắn thẳng từng viên | Xương sống mọi wave |
| CD — Drone | Tròn, lõi sáng giữa | Bay chậm, xoay tại chỗ, bắn tỏa nhịp | Kiểm soát khu vực |
| GD — Pháo hạm nhỏ | Thân dày, nòng lớn | Đi chậm, dừng bắn loạt có telegraph | Mục tiêu ưu tiên |
| XB — Xuyên phá | Thon dài | Lao nhanh theo đường thẳng/dồn đuổi | Tạo p
...[truncated 2087 chars]