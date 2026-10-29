# 02 — HẠM ĐỘI, HANGAR & TIẾN TRÌNH NGƯỜI CHƠI

## 2.1 Hạm đội tàu người chơi (từ 25 tàu của gốc)

Gốc có **25 tàu** (`ships.json`), mỗi tàu là một `Player_Info` {id, Sprite,
Star, Actived} [gốc]; damage tra theo tàu (`GetMainCannonDamage(playerIndex)`)
[gốc]; HP chung theo công thức `2500 × (1 + 0,18×TechStatPoints(0) +
ability7)` [gốc] — tức tàu khác nhau ở **súng và lối chơi**, không khác ở
bảng HP thô. Giữ đúng triết lý này:

- Mỗi tàu = một **lối chơi**: bắn thẳng dồn dập / tỏa góc rộng / đạn nặng
  chậm / drone hỗ trợ... Người chơi chọn tàu theo sở trường, không có
  "tàu cuối mạnh hơn mọi mặt".
- **[SLICE]** 3 tàu đã cài số thật: 10001 (damage 4500, cân bằng — tàu
  khởi đầu), 10003 (2680, nhanh/tỏa — mở sau chặng đầu), 10004 (8000,
  chậm/nặng — tàu "pháo hạm"). Ba tàu này là 3 nguyên mẫu lối chơi; mọi
  tàu sau là biến thể có dấu ấn riêng, không sao chép chỉ số.
- **[MỞ RỘNG]** Mở tàu theo tiến trình chương + nhiệm vụ, hướng về 25 tàu;
  mỗi tàu kèm drone/wing riêng (gốc có 13 drone, luật bắn theo level [gốc]).

## 2.2 Hangar — "nhà" của người chơi

Hangar là scene 3 lớp chiều sâu (theo luật đạo diễn chương 6):

```
[Lớp nền]  Khoang trạm: sàn kim loại vạch teal, tường khoang, ánh sáng
           tập trung ở bệ giữa, rìa tối dần (vignette tự nhiên).
[Lớp giữa] BỆ PHÓNG tròn (vòng năng lượng xoay chậm, sáng theo nhịp thở)
           + TÀU trưng trên bệ (hover, bóng co giãn, lửa đuôi nhỏ,
           glow canopy thở, đèn thân so le).
[Lớp trước] Giàn khung 2 bên + xà trên (trong suốt giữa) tạo chiều sâu;
           hạt môi trường: khói mỏng trôi, tia lửa rơi ngẫu nhiên.
[UI]       Trên: thanh tài nguyên (vàng/gem/năng lượng).
           Giữa-trái/phải: mũi tên đổi tàu. Dưới: tên tàu + 3 thanh chỉ
           số (Công/Tốc/Giáp) + nút NÂNG CẤP + nút XUẤT KÍCH lớn.
```

- Đổi tàu: tàu cũ hạ bệ/trượt ra, tàu mới vào — có chuyển động chuyển
  cảnh 0,5–0,8s, không cắt hình đột ngột. Chỉ số đổi theo tàu thật.
- Đứng yên 30 giây hangar vẫn sống (đèn, khói, vòng bệ, lửa) — đây là
  tiêu chuẩn nghiệm thu của hangar, kiểm bằng clip 30s.
- **[SLICE]** Hangar đủ: nền + bệ + tàu sống + đổi 3 tàu + chỉ số + xuất
  kích. **[MỞ RỘNG]** nâng cấp có cây (2.3), drone bay quanh tàu trưng.

## 2.3 Tiến trình & nâng cấp

Học cấu trúc gốc, đơn giản hóa cho bản làm mới:

- **Sao chặng:** thắng chặng nhận 1–3 sao theo máu còn lại/thời gian
  (lưu `StarCount`, sao theo chặng như gốc [gốc]) — sao là cổng mở chương.
- **Tiền tệ:** Coin rơi trong trận theo công thức kiểu gốc (giá trị xu
  theo hạng xu × hệ số chặng) [gốc]; dùng nâng cấp. Gem là tiền hiếm
  (thưởng sao/boss) — **không bán bằng tiền thật trong phạm vi này** (IAP
  170 sản phẩm của gốc [gốc] thuộc [CẮT]/USER-ONLY).
- **Nâng cấp tàu (Tech):** các nấc tăng theo % nhỏ bám công thức HP gốc
  (mốc 0,18/nấc là cảm hứng thang đo); mỗi nấc phải *thấy được* (đạn to
  hơn, thêm tia, drone mạnh hơn) — cấm nâng cấp chỉ là con số.
- **Drone hỗ trợ:** bay kèm tàu, bắn theo luật level như gốc [gốc];
  [SLICE] chưa bắt buộc, [MỞ RỘNG] mở từ tàu thứ 2.
- **Talent/Ability:** gốc có 23 method talent [gốc] — [MỞ RỘNG] chọn lọc
  thành cây kỹ năng bị động/ chủ động đơn giản, mỗi kỹ năng 1 dòng mô tả
  và 1 hiệu ứng hình ảnh riêng.

## 2.4 Nhịp tiến trình tổng thể

| Giai đoạn người chơi | Mở ra | Cảm giác mục tiêu |
|---|---|---|
| Trận đầu | Tàu 10001, hangar cơ bản | "Tôi có tàu, tàu đang sống" |
| Qua chặng mẫu | Tàu 10003, nâng cấp đầu | "Có lựa chọn, có lớn lên" |
| Hạ boss mẫu | Tàu 10004, drone đầu | "Tôi hạ được thứ khổng lồ" |
| [MỞ RỘNG] Các chương | Tàu/họ địch/boss mới theo chương | Luôn có thứ chưa thấy |

Mọi mốc mở khóa phải được báo trước trong hangar ("Hạ boss chặng này để
mở tàu 10004") để người chơi có mục tiêu nhìn thấy được.
