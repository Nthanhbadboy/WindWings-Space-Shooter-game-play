# 03 — SÁCH BOSS (BOSS BOOK)

> Gốc có **39 boss**, 795 event animation có mốc thời gian, nhịp sự kiện
> đặc trưng **0,17 / 0,33 / 1,0 / 5,0 giây**, boss dùng rig Spine (27 rig)
> [gốc — `datas/boss_anim_events.csv`, `docs/spec/BOSS_ANIM_TIMELINE.md`].
> Bản làm mới: mỗi boss là một **nhân vật** được viết hồ sơ trước khi vẽ.
> Boss-37001 dưới đây là **boss mẫu chuẩn** — 38 boss sau theo đúng khuôn
> hồ sơ này, khác tính cách/vũ khí dấu ấn/bối cảnh.

## 3.1 Khuôn hồ sơ boss (bắt buộc đủ 9 mục)

1. **Danh tính:** tên nội bộ + biệt danh người chơi sẽ gọi + 1 câu tính cách.
2. **Ngoại hình:** silhouette 1 câu, màu dấu ấn, bộ linh kiện (thân trần +
   bộ phận động + glow + lớp hư hại 3 bậc + mảnh vỡ).
3. **Vũ khí dấu ấn:** 1 vũ khí chỉ boss này có (tia quét, mưa tên lửa,
   vòng đạn, triệu hồi...) + vũ khí phụ.
4. **Kịch bản 3 hồi** theo %HP: mỗi hồi gồm đòn gì, nhịp nào, boss "diễn"
   hành vi gì thể hiện tính cách.
5. **Bảng đòn:** mỗi đòn đủ: báo trước (hình/âm, số giây) · thời lượng ·
   nghỉ · thông số đạn · khe né · lý do tồn tại.
6. **Cái chết:** chuỗi nổ ≥3s có thứ tự + phần thưởng rơi.
7. **Bối cảnh sân đấu:** nền/địa hình đi kèm, môi trường phản ứng gì.
8. **Âm thanh:** nhạc riêng/nhịp, tiếng dấu ấn của vũ khí chính.
9. **Thông số:** HP, ngưỡng pha, sát thương từng đòn — suy từ khung gốc
   (boss slice 225.000 HP; tàu 2.500 HP; damage tàu 4500/2680/8000).
   **Bắt buộc kèm "Bảng chuẩn đạn & pha"**: mỗi đòn phải gán được vào
   chuẩn gốc — mẫu bắn 5 tham số (`countShots/timeShot/timeReload/
   timeRounds/countMags`), họ đạn, tốc độ, damage/viên, hitbox — tra tại
   `docs/spec/COMBAT.md` §3+§7 và `reverse-engineering/scriptableobjects/
   Gun_Attack.csv` + `Bullet_Linearly.csv` (bản đồ nguồn đầy đủ ở tập 04
   §4.1). Mỗi dòng ghi nguồn [GỐC: file/mục] hoặc [ĐỀ XUẤT: lý do]; dòng
   nào không tra được cũng không tự đặt thì hồ sơ chưa hoàn chỉnh.
   Nhớ nguyên tắc gốc: boss mạnh ở **mật độ/mẫu đạn**, không ở damage/viên.

## 3.2 Boss mẫu — Boss-37001 "LÃO PHÁO ĐÀI"

- **Tính cách 1 câu:** *Một pháo đài bay lão luyện, khinh địch — đánh
  khoan thai như đi dạo, chỉ nổi điên khi bị thương thật.*
- **Ngoại hình:** chiến hạm thép xanh-đen, 2 ụ pháo xoay, pháo chính giữa,
  pod tên lửa tổ ong 2 hông, lõi teal trung tâm. Màu dấu ấn: **teal lạnh**
  (điểm nhận diện ở mọi kích thước). Linh kiện đã sản xuất tại
  `art/boss-fight/` (thân trần + 8 lớp + 14 FX/đạn) — hồ sơ này là kịch
  bản chính thức cho bộ linh kiện đó.
- **Vũ khí dấu ấn:** **Tia quét Lão Hống** — sạc 1,2s (đường cảnh báo hổ
  phách hiện trước) rồi quét −25°→+25° trong 1,9s; đứng trong tia mất
  120 HP/0,5s; né bằng cách qua khỏi đầu tia hoặc chui sát thân boss.
- **Kịch bản 3 hồi:**
  - *Hồi 1 (100–70% HP) — Áp đảo:* vào trận nghi thức 1,5s (vòng cảnh
    báo, đèn thân bật dần). Đòn: pháo xoay ngắm bắn đạn năng lượng (nghỉ
    1,6s), lâu lâu **tiến xuống ép sân 2s rồi lui** (diễn tính khinh địch).
  - *Hồi 2 (70–30%) — Bị thách thức:* mốc 70%: dừng 0,5s, lõi gắt sáng
    (khoảnh khắc "nhận ra đối thủ"). Từ đây: pháo bắn liên thanh 3 viên,
    kết hợp **khóa tên lửa** (reticle bám vị trí tàu 0,8s → phóng 4 cặp,
    tàu chạy tiếp thì trượt) và tia quét đầu tiên. Nghỉ giữa đòn 0,8s.
  - *Hồi 3 (30–0%) — Tuyệt vọng:* lớp hư hại bậc 2–3 hiện dần, thân rung
    nhẹ, pháo nhanh hơn 30% nhưng góc tỏa loạn ±6°, tia quét tuyệt vọng
    quét 2 chiều liên tiếp. Dưới 15%: lõi quá tải nhấp nháy cảnh báo.
- **Cái chết (≥3s, theo chuỗi):** ụ trái nổ → pod phải cháy → chớp điện
  dọc thân → lõi trắng màn 0,3s → nổ chính → 3–4 mảnh giáp văng + sóng
  xung kích dọn sạch đạn địch trên sân → khói tàn 1s → màn kết quả.
- **Sân đấu:** hành lang pháo đài (cấu trúc 2 bên như frame-sheet đã
  dựng), đèn thành chuyển đỏ khi boss sạc tia.
- **Âm thanh:** nhạc boss riêng nhịp trống dồn; tiếng sạc tia rít tăng
  dần; khóa tên lửa có "bíp" dồn dập. (Chưa có nhạc thì placeholder có
  ghi rõ, xem tập 05.)

## 3.3 Danh mục 39 boss — cách sáng tạo tiếp

Không chép 39 boss gốc; sáng tạo theo **ma trận**: [tính cách] × [vũ khí
dấu ấn] × [bối cảnh]. Ví dụ hàng đợi thiết kế (viết hồ sơ đầy đủ khi tới
lượt sản xuất, theo đúng khuôn 3.1):

| # | Biệt danh | Tính cách | Vũ khí dấu ấn | Sân |
|---|---|---|---|---|
| 1 | Lão Pháo Đài (37001) | Khinh địch lão luyện | Tia quét + tên lửa khóa | Hành lang pháo đài |
| 2 | Góa Phụ Vành Đai | Mai phục kiên nhẫn | Vòng đạn nở chậm + mìn trôi | Vành đai thiên thạch |
| 3 | Song Sinh | Hai lõi phối hợp | Bắn chéo đồng bộ 2 nguồn | Xưởng đóng tàu |
| 4 | Kẻ Đào Tẩu | Đánh rồi chạy | Đòn dồn dập rồi dịch chuyển vị trí | Cảng vũ trụ |
| 5 | Mẹ Bầy | Triệu hồi | Sinh drone con theo đợt, thân yếu | Tổ ong cơ khí |
| … | … | … | … | … |

Mỗi boss cách nhau ít nhất 1 chương; boss sau **kế thừa 1 bài học** từ
boss trước (đã biết né tia → boss sau có đòn trừng việc đứng yên...).

## 3.4 Luật sản xuất boss (không thương lượng)

- Hồ sơ 9 mục duyệt xong **trước** khi generate ảnh đầu tiên.
- Linh kiện sinh theo bộ (thân trần trước), pivot do art đo + GIF xoay
  360° chứng minh; đạn/FX của boss sinh cùng lô với thân.
- Art dựng GIF hoạt cảnh toàn trận theo kịch bản 3 hồi → USER duyệt →
  coder cài thành **hệ thống theo tình huống** (%HP/vị trí), cấm cài theo
  mốc giây và cấm nhúng GIF. Nghiệm thu: 2 clip chơi khác nhau phải cho
  2 trận khác nhau nhưng cùng "tính cách".
