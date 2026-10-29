# 05 — MÀN HÌNH, UI, ÂM THANH & HỆ THỐNG PHỤ

## 5.1 Bản đồ màn hình (từ 797 màn của gốc, rút về xương sống thương mại)

Gốc có 797 màn/150.131 node [gốc] — phần lớn là popup/meta. Làm mới giữ
đủ luồng để game có "hình hài thương mại", mỗi màn 1 việc:

| # | Màn | Việc duy nhất | Phạm vi |
|---|---|---|---|
| 1 | Logo/Nạp | Vào game trong <3s | [SLICE] |
| 2 | Menu chính | Chơi · Hangar · Cài đặt (nhãn bản build) | [SLICE] |
| 3 | Hangar | Chọn/nâng cấp tàu, xuất kích (tập 02) | [SLICE] |
| 4 | HUD trận | Máu, sóng wave, điểm, tạm dừng | [SLICE] |
| 5 | Cảnh báo boss | Banner + tên boss + nhạc chuyển | [SLICE] |
| 6 | Kết quả thắng | Sao 1–3, thưởng, nút: Chơi lại / Về hangar | [SLICE] |
| 7 | Kết quả thua | Chết ở đâu, nút: Thử lại / Về hangar nâng cấp | [SLICE] |
| 8 | Tạm dừng + Cài đặt | Âm thanh/nhạc/độ rung, tiếp tục/thoát | [SLICE] |
| 9 | Bản đồ chương | Chặng đã mở, sao từng chặng | [MỞ RỘNG] |
| 10 | Kho tàu & nâng cấp sâu | Cây tech, drone, talent | [MỞ RỘNG] |
| 11 | Nhiệm vụ ngày/Battle Pass | Hàng chờ: BP gốc 85+39 mốc [gốc] | [MỞ RỘNG] |
| 12 | Arena/PvP | Gốc: 10 hạng Arena, 10 hạng PvP 3 chế độ [gốc] — cần quyết thiết kế riêng (bỏ Betting) | [MỞ RỘNG — chưa cam kết] |

**Luật thị giác UI** (đo từ gốc): khung chiếm ~0,48 khung hình, màu nhấn
≤10% diện tích, tương phản chữ 0,45–0,80 [gốc — VISUAL_DESIGN]. Nút chính
1 màu nhấn duy nhất/màn; mọi nút có hover/nhấn; chữ trên nút ≤3 từ.

## 5.2 Âm thanh (từ registry 92 id / 15 luật của gốc)

- **Nhạc 3 khu vực:** hangar (yên, điện tử nhẹ) · trận (căng vừa) ·
  boss (dồn dập riêng). Chuyển nhạc theo sự kiện (boss vào → cắt nhạc
  boss kèm 0,5s lặng báo hiệu).
- **SFX bắt buộc có cặp với hình:** bắn ta/địch, trúng giáp, nổ nhỏ/lớn,
  sạc tia (rít tăng), khóa tên lửa (bíp dồn), nhặt xu, UI bấm, cảnh báo.
- **Luật:** theo `audio_rules.json` của gốc (mute/volume/pause/oneshot)
  [gốc]. Âm thanh tự sinh/tìm nguồn mở đều phải khai nguồn + giấy phép;
  thiếu thì ghi placeholder [PLACEHOLDER-AUDIO], không im lặng giả xong.
- Âm lượng chuẩn hóa: tiếng báo nguy hiểm (sạc/khóa) luôn nghe rõ trên
  nhạc — đó là một nửa của luật Công bằng.

## 5.3 Hệ thống phụ & kinh tế (khung thương mại, phạm vi kiểm soát)

| Hệ | Gốc có | Quyết định làm mới |
|---|---|---|
| Sao chặng/lưu | StarCount + sao theo chặng [gốc] | [SLICE] có, lưu local `user://` |
| Coin rơi/nhặt | Công thức theo hạng xu × hệ số chặng [gốc] | [SLICE] đơn giản hóa, khai công thức |
| Item rơi (6 loại) | 6 loại (+1Level...) [gốc] | [MỞ RỘNG] nhặt giữa trận: khiên/súng phụ/máu |
| Đăng nhập ngày (30 ô), Quà | Có [gốc] | [MỞ RỘNG] sau khi vòng lặp chứng minh vui |
| Battle Pass 85+39 mốc | Có [gốc] | [MỞ RỘNG] — chỉ khi có nhịp cập nhật |
| VIP/Energy | Có [gốc] | [CẮT] cho tới khi có lý do thiết kế |
| Arena/PvP | 10+10 hạng [gốc] | [MỞ RỘNG — chưa cam kết], Betting [CẮT] hẳn |
| IAP 170 sản phẩm | Có [gốc] | **[CẮT]/USER-ONLY** — ngoài phạm vi kỹ thuật này |

## 5.4 Lưu trữ & hồ sơ người chơi

Lưu local: sao từng chặng, tàu đã mở, nâng cấp, cài đặt, kỷ lục boss.
Ghi theo khóa có tên rõ (học kiểu `StarStageMaster{stage}_{mode}` của
gốc), có số phiên bản schema để nâng cấp về sau không vỡ save. Mọi lần
ghi save trong Slice đã chạy thật (harness coder đã chứng minh [slice]).
