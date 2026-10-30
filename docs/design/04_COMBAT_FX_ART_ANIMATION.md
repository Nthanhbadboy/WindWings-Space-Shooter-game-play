# 04 — CHIẾN ĐẤU, FX, NGHỆ THUẬT & CHUYỂN ĐỘNG

## 4.1 Hệ chiến đấu (từ 458 súng / 186 loại đạn của gốc)

> **BẢN ĐỒ NGUỒN — đọc các mục này TRƯỚC khi viết bất kỳ thông số nào**
> (mọi thông số chiến đấu đều tra ở đây trước; chỉ sáng tạo ở chỗ gốc
> không có, và phải ghi [ĐỀ XUẤT] cạnh số tự đặt):
> - `docs/spec/COMBAT.md` **§0** (bảng TL;DR: damage 40–1.200 median 400,
>   tốc độ đạn 2,0–23,0, tầm bay), **§3** (mẫu bắn 5 tham số `GunData`:
>   `countShots/timeShot/timeReload/timeRounds/countMags` — định nghĩa
>   gốc từng trường), **§7** (bảng 186 loại đạn `Bullet_Linearly`).
> - `reverse-engineering/scriptableobjects/Gun_Attack.csv` (458 dòng súng
>   địch/boss: `bltDamage`, `bltSpeed`, 5 tham số burst) và
>   `Bullet_Linearly.csv` (186 loại đạn: `border.w`, `pointRadius`,
>   `throughShield`, `throughAll`, `fixedOnLinecast`), `Bullet_SineWave.csv`.
> - `docs/spec/ENEMY_BEHAVIOUR.md` **§1.3** (hằng số va chạm `border.w=15`
>   dùng chung 799/800 địch — bán kính va chạm chuẩn của cả game).
> - `datas/sprites.csv` lọc theo `bullet`/`EBullet`/`Efx_BulletHit`:
>   chỉ mục ảnh đạn gốc để học **phân loại và ngôn ngữ hình** (cấm dùng
>   lại file ảnh gốc; vẽ mới theo họ).
>
> Chuẩn gốc rút ra (mức A, dùng làm khung cho mọi spec):
> - Hitbox đạn chuẩn **15 unit** (184/186 loại); khác biệt giữa các đạn
>   chủ yếu ở sprite và hành vi, không ở kích thước va chạm.
> - Sức mạnh của boss/địch nằm ở **mật độ và mẫu đạn, không phải
>   damage/viên** (đòn boss không mạnh hơn đạn thường theo viên).
> - 31% đạn xuyên khiên → khiên không bao giờ là "chặn 100%".
> - Súng của người chơi KHÔNG nằm trong `Gun_Attack.csv` (458/458 là
>   Enemy); damage tàu lấy từ mảng đã decode (4500/2680/8000 trong Slice).

Gốc: damage súng 40–1.200 (median 400), burst có 5 tham số, đạn có họ
riêng [gốc — COMBAT.md]. Làm mới giữ cấu trúc, rút gọn cho dễ đọc:

- **Đạn người chơi:** theo tàu (02): thẳng dồn / tỏa / nặng chậm / drone
  phụ. Đạn phải **to, sáng, có vệt** — người chơi không bao giờ mất dấu
  đạn của mình.
- **Đạn địch:** chỉ 3 họ hình dạng trong Slice để học đọc: cầu năng lượng
  (chậm, né dễ), viên laser dài (nhanh, theo đường thẳng), tên lửa (có
  khóa, có vệt khói). [MỞ RỘNG] thêm họ theo boss/chương. Đạn nguy hiểm
  luôn màu nóng (cam/đỏ/hồng), đạn ta luôn màu lạnh (xanh/teal/trắng) —
  luật màu này không ngoại lệ.
- **Va chạm:** hitbox nhỏ hơn hình (tha thứ ~30%) để cảm giác "né sượt"
  xảy ra thường xuyên — đó là khoảnh khắc vui nhất của thể loại này.
- **Sát thương:** mọi số ghi nguồn: khung tàu 2.500 HP, damage tàu
  4500/2680/8000, boss 225.000 [gốc/slice]. Phân tầng theo quyết định
  đạo diễn (Boss Book §3.5 câu 4): đạn địch thường và đạn bắn nhanh/tỏa
  **3–6% HP tàu/viên**; đòn boss nặng có telegraph dài (≥0,9s, nhịp
  thưa) được **10–15%/viên**; tia quét tính theo thời gian đứng trong
  tia (120 HP/0,5s — Boss Book §3.2). Sức mạnh tổng đến từ mật độ đạn
  và mẫu bắn, không từ việc phình damage từng viên rẻ tiền.

## 4.2 Cảm giác trận đánh (game feel) — bảng juice chuẩn

| Sự kiện | Hiệu ứng bắt buộc | Thông số gốc tham chiếu |
|---|---|---|
| Địch trúng đạn | Chớp trắng thân + tia lửa nhỏ + lệch nhẹ | Flash **0,05s** [gốc] |
| Tàu trúng đạn | Chớp + rung màn hình + viền đỏ thoáng | Rung **0,10s / 20 frame** [gốc] |
| Địch chết | Nổ theo cỡ địch + xu văng ra bay về HUD | Chuỗi rơi xu gốc [gốc] |
| Boss sạc đòn lớn | Âm rít tăng + glow tụ + đường cảnh báo | Telegraph ≥0,8s (luật Công bằng) |
| Boss chết | Chuỗi nổ theo thứ tự + dọn đạn + chậm 0,2s ở nổ chính | Xem Boss Book 3.2 |
| Nhặt xu/item | Vật phẩm bay có từ tính về tàu khi gần | Bán kính hút khai trong code |

## 4.3 Nghệ thuật — quy trình sản xuất (bài học xương máu)

1. **Generate trực tiếp, không vẽ lại bằng code.** Chuẩn hình: ngôn ngữ
   tàu đã USER chốt (cong, giáp tầng, 2.5D). Tham khảo nguyên mẫu qua
   contact sheet trong repo để học ngôn ngữ — cấm trace/chép.
2. **NĂNG LỰC SẢN XUẤT — RÀNG BUỘC CỨNG (điều kiện lập kế hoạch):**
   session art sinh tối đa **10 ảnh generate trong 1 turn** (mỗi ảnh là
   một lần gọi công cụ sinh ảnh độc lập; xử lý hậu kỳ/render GIF không
   tính vào quota này nhưng tốn thời gian riêng). Hệ quả bắt buộc:
   - Mọi nhiệm vụ art phải được **chia sẵn thành các LÔ ≤10 ảnh**, đánh
     số Lô 1, Lô 2, ... kèm danh sách từng ảnh trong từng lô, NGAY trong
     prompt giao việc. Cấm giao một danh sách dài hơn 10 ảnh như việc
     của một turn.
   - Cuối mỗi turn, art báo cáo theo lô: `ĐÃ GIAO LÔ x/y — z/10 ảnh đạt`,
     liệt kê món còn thiếu; dừng ở đó chờ director/USER nói "tiếp" mới
     sinh lô kế. Cấm tự gộp nhiều turn vào một báo cáo "đã xong".
   - Ước lượng quy mô theo ràng buộc này: 1 boss đầy đủ (~22 file hình)
     ≈ **3 turn sinh ảnh** + 1 turn hậu kỳ/render; đội địch 13–16 con ≈
     **2 turn**; hangar (nền + giàn + bệ) ≈ 1 turn. Lộ trình ở tập 06 đã
     tính theo các con số này — không được hứa nhanh hơn.
   - Ảnh sinh lỗi/dị dạng vẫn tính vào quota của turn đó; báo lỗi ngay,
     ảnh thay thế thuộc lô của turn sau.
   - **PHÂN BIỆT 2 LOẠI LỖI SINH ẢNH (không được lẫn):**
     (a) *Hết quota turn* — thông báo `Image generation limit of 10
     reached for this turn`: chỉ là giới hạn theo lượt; dừng sinh, báo
     cáo lô, chờ turn sau sinh tiếp. (b) ***403 PERMISSION_DENIED*** —
     dịch vụ báo tài khoản bị đánh dấu hoạt động đáng ngờ: đây là
     **chặn ở cấp tài khoản, không phải quota**. Khi gặp 403 phải:
     DỪNG NGAY mọi lần sinh và **cấm bấm thử lại liên tục** (retry dồn
     có thể làm cờ nặng thêm); báo cáo nguyên văn mã lỗi + thời điểm
     lên board và chờ USER xử lý tài khoản; trong lúc chờ chuyển sang
     việc không cần generate (ghép linh kiện sẵn có, đo pivot, viết
     SPEC/manifest, render GIF từ asset đã có, kiểm kê thiếu món).
     Cấm gọi 403 là "đủ quota", cấm báo "đã sinh" khi chưa có file
     thật, cấm dùng ảnh lỗi/ảnh cũ mạo danh ảnh mới.
   - **SỰ CỐ 30/10/2026 — CHẶN CẤP TÀI KHOẢN (đã xác nhận):** session
     art `215aa58f` thử 7 yêu cầu và session sinh ảnh mới `93c8b06c`
     thử 1 yêu cầu đầu tiên — tất cả đều trả `403 PERMISSION_DENIED`
     "account has been flagged for suspicious activity... check the
     email associated with your account". Kết luận: cờ ở cấp tài
     khoản dịch vụ, không phải quota, không phải do một session.
     Từ lúc này: **mọi session đóng băng sinh ảnh** cho tới khi USER
     thông báo tài khoản đã được gỡ (USER kiểm tra email liên kết tài
     khoản và làm theo hướng dẫn kháng nghị/xác minh trong email đó —
     session không tự gỡ được, không tạo session mới để lách). Trong
     thời gian đóng băng, art làm phần không-cần-generate: kiểm tra
     lắp linh kiện sẵn có lên bố cục mới, hoàn thiện SPEC/manifest,
     bảng thiếu món.
   - **Cập nhật sự cố 30/10 (tiếp):** USER đã kiểm tra và **không nhận
     được thư nào**. Suy luận thực tế: tài khoản bị đánh dấu nhiều
     khả năng là tài khoản dịch vụ phía nền tảng (công cụ sinh ảnh
     chạy qua endpoint `google-genai/gemini-3.1-flash-image`), không
     phải hộp thư cá nhân của USER — nên đường "kiểm tra email/kháng
     nghị" có thể không tới được USER. Hệ quả: (1) tiếp tục đóng băng,
     **không session nào được tự thử lại**; (2) lần thử kế tiếp chỉ
     thực hiện khi USER ra lệnh đích danh, đúng **1 yêu cầu**, nếu vẫn
     403 thì đóng băng tiếp; (3) đường gỡ chính thức còn lại là USER
     liên hệ hỗ trợ của nền tảng kèm nguyên văn lỗi + mốc thời gian
     lần đầu bị chặn, hoặc chờ cờ tự hết hạn (không có thời hạn công
     bố để hứa hẹn).
3. **Linh kiện trước, ảnh sau:** thân trần → bộ phận động → glow → hư
   hại → đạn/FX cùng hệ. Mọi pivot do art đo.
4. **Hậu kỳ tối thiểu:** tách nền (kiểm halo ở nền sáng + tối), đặt
   canvas đúng slot (tàu 256², địch 128², boss 512², đạn 64²/64×128,
   FX 256², nền 1080×1920 [contract coder]), thu nhỏ Lanczos trực tiếp
   từ master. Số đo ảnh (planner) chỉ là **tham khảo** — mắt USER là cổng.
5. **Kiểm ở kích thước thật:** mọi asset nộp kèm bản thu về cỡ hiển thị
   (tàu ~93px, địch ~50px trong viewport 10,8 unit) đặt trên nền gameplay.
   Đẹp ở 1024² mà nát ở cỡ thật = loại, sinh lại với khối to hơn.

## 4.4 Chuyển động — 3 tầng (chi tiết của luật đạo diễn chương 4)

- **Tầng linh kiện (art):** pháo xoay, lõi nhịp, cánh/pod phụ nếu có;
  bằng chứng = GIF xoay/từng bộ phận do art tự render từ file export.
- **Tầng thủ tục (coder):** hover/bob (biên độ 0,05–0,12 unit, chu kỳ
  1,6–2,4s), banking nghiêng theo vận tốc ngang (tới ~12°), giật lùi
  0,03 unit khi bắn loạt, lửa particle: dài theo tốc độ dọc, tắt khi chết.
  Hằng số tập trung 1 file tuning, khai nguồn từng số.
- **Tầng trận đấu (art kịch bản → coder hệ thống):** trạng thái theo
  %HP/vị trí (Boss Book), nhịp đòn bám nhịp gốc 0,17/0,33/1,0/5,0s [gốc]
  làm thang tham chiếu cho tốc độ sự kiện.

## 4.5 Kế hoạch kho hình (đếm được, thay cho "2.885 sprite" của gốc)

Không sản xuất 2.184 sprite như gốc; sản xuất theo **nhu cầu scene**:

| Nhóm | Slice cần | Cách tính |
|---|---|---|
| Tàu người chơi (thân+glow) | 3×2 | Theo 02 |
| Địch 5 wave (thân, +glow nếu có) | 13–16 | Theo 01 — đủ ý đồ wave |
| Boss mẫu (linh kiện+FX/đạn) | ~22 file | Đã có tại art/boss-fight |
| Đạn (ta 3 họ, địch 3 họ) | 6 | 4.1 |
| FX (nổ 4 frame, khói, tia lửa, vòng, chớp) | ~10 | 4.2 |
| Nền (không gian trận, hành lang boss, hangar+giàn) | 3–4 | Theo scene |
| UI (khung, nút, biểu tượng tài nguyên) | ~10 | Theo 05 |
| **Tổng Slice** | **~70 file** | Đủ một game nhỏ trọn vẹn |

[MỞ RỘNG] Mỗi chương cộng: 1 nền, 4–8 địch, 1 boss (~22 file), 0–2 tàu.
