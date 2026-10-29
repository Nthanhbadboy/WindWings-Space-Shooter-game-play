# GAME DIRECTOR'S VISION — Hồ sơ đạo diễn (Director's Bible)

> **Địa vị của văn bản này:** đây là luật chung cao nhất cho MỌI session làm game
> (art, coder và các session sau). Mọi prompt giao việc phải trích dẫn chương
> của văn bản này; sản phẩm lệch khỏi nó là sai, dù chỉ số/test xanh.
> **Bản kịch bản đầy đủ có hiệu lực chi tiết nằm ở `docs/design/`**
> (tập 00–06: chiến dịch/wave/địch, hạm đội/hangar, Boss Book, chiến đấu/FX,
> màn hình/UI/âm thanh, lộ trình) — văn bản này là luật tóm tắt, khi có khác
> biệt thì chi tiết theo `docs/design/` và báo lại director.
> Nguyên mẫu *WindWings: Space Shooter* là tài liệu tham chiếu về **ngôn ngữ
> thiết kế** (số liệu mức A trong `docs/spec/`, dữ liệu trong `datas/`) —
> học ngôn ngữ, sáng tạo nội dung mới, không sao chép asset/trace hình gốc.
> Người duyệt cuối cùng mọi thứ thuộc về thẩm mỹ/trải nghiệm: **USER**.

---

## 1. Tưởng tượng tổng thể — game này là gì

Một game bắn súng dọc thương mại trên PC: người chơi là phi công của một
phi đội tinh nhuệ, xuất kích từ **hangar trên trạm vũ trụ**, bay qua các
chặng hành lang pháo đài địch, hạ boss trấn ải, mang chiến lợi phẩm về
**nâng cấp tàu trong hangar**, rồi xuất kích tiếp, mạnh dần lên.

Cảm giác phải đạt, theo thứ tự ưu tiên:

1. **"Tàu của tôi đang sống"** — tàu lơ lửng, lửa cháy, đèn thở trong hangar;
   trong trận nó nghiêng, giật, chớp sáng. Không một thực thể chính nào là
   ảnh tĩnh dán lên màn hình.
2. **"Kẻ địch có tổ chức"** — địch vào theo đội hình có ý đồ, boss là một
   nhân vật có tính cách chiến đấu, không phải trụ pháo bắn đều.
3. **"Mỗi trận là một cảnh phim ngắn"** — có mở màn, leo thang, cao trào,
   kết liễu; người xem tắt tiếng vẫn kể lại được diễn biến.
4. **"Về hangar là về nhà"** — hangar là nơi người chơi ngắm thành quả,
   nâng cấp, chọn tàu; nó phải có không gian, ánh sáng, sự sống riêng.

Ba trụ cột thiết kế (vi phạm một trụ là sản phẩm sai, bất kể đẹp):

- **Đọc được (Readability):** ở kích thước thật trong game, 0,5 giây phải
  phân biệt được ta/địch/đạn nguy hiểm/an toàn. Đẹp ở ảnh phóng to mà mù ở
  64px là thất bại.
- **Sống (Alive):** mọi thực thể chính có ít nhất một chuyển động nội tại
  không cần người chơi tác động (hover, thở sáng, xoay chờ, khói, đèn).
- **Công bằng (Fair):** mọi nguồn sát thương lớn đều báo trước bằng hình
  ảnh/âm thanh đủ thời gian né. Khó vì né giỏi, không khó vì bị đánh úp.

## 2. Vòng lặp game (game loop) — xương sống thương mại

```
MENU → HANGAR (ngắm/chọn/nâng cấp tàu) → XUẤT KÍCH
     → 5 WAVE địch leo thang → BOSS (cảnh phim 3 hồi)
     → MÀN KẾT QUẢ (sao/thua-thắng/thưởng) → về HANGAR (mạnh hơn) → lặp lại
```

- Mỗi vòng 6–10 phút. Thưởng cuối trận quay về hangar mở khóa/nâng cấp —
  người chơi luôn có lý do bay trận tiếp theo.
- Độ khó đi theo dữ kiện nguyên mẫu: vùng chơi 20×25 unit, HP tàu
  2500×(1+0,18×…), boss trong slice HP 225.000, damage 3 tàu 4500/2680/8000.
  Mọi con số mới phải suy ra từ khung này và ghi rõ nguồn.
- Bản Windows hiện tại là **Launch Slice**: vòng lặp trên ở quy mô nhỏ nhất
  nhưng **đầy đủ hình hài** (có hangar thật, 5 wave thật, boss thật, kết quả
  thật) — thà nhỏ mà trọn vẹn như game thật, không làm to mà rỗng.

## 3. Chỉ đạo nghệ thuật (art direction)

- **Nguồn hình:** 100% generate trực tiếp theo ngôn ngữ đã USER chốt (tàu
  cong, giáp tầng, semi-realistic 2.5D). **Cấm** vẽ lại bằng code/đa giác,
  cấm chép/trace nguyên mẫu. Xử lý sau sinh chỉ là hậu kỳ (tách nền, đặt
  canvas, ánh xạ màu nhẹ) — không tái cấu trúc hình.
- **Ngôn ngữ màu theo phe:** Ta = thép xanh + teal + hổ phách. Địch = gỉ
  đỏ/nâu + cam cháy. Boss = thép xanh-đen uy nghi + lõi teal + điểm cam.
  Mỗi cá thể chính phải có **màu dấu ấn riêng** để nhận diện ở 64px —
  bài học từ boss đơn sắc bị chìm nền.
- **Hình khối trước chi tiết:** silhouette đọc được ở kích thước hiển thị
  nhỏ nhất là cổng đầu tiên; chi tiết mịn là lớp sau. Chi tiết phải là mảng
  lớn chuyển mềm, không nhiễu li ti.
- **Ánh sáng:** mọi asset chính có nguồn sáng thống nhất (sáng trên, tối
  mép dưới), AO mềm giữa các tầng giáp; hiệu ứng phát sáng (glow/lửa/tia)
  KHÔNG nung vào thân — luôn là lớp riêng để animate.
- **Nguyên tắc linh kiện:** mọi thực thể cần chuyển động bộ phận (tàu,
  boss, địch lớn) được generate thành **bộ linh kiện ngay từ đầu**: thân
  trần đứng một mình được + từng bộ phận chuyển động là ảnh riêng + glow
  riêng. Cấm sinh một ảnh phẳng rồi cắt lớp/đoán pivot về sau.

## 4. Chỉ đạo chuyển động (motion doctrine)

Phân tầng rõ ràng, không tầng nào thay thế tầng nào:

| Tầng | Ai làm | Nội dung |
|---|---|---|
| **Linh kiện động** | Art | Pháo xoay quanh pivot do art đo và chứng minh bằng GIF xoay 360°, lõi sáng theo nhịp, bộ phận hư hại theo bậc HP |
| **Chuyển động thủ tục** | Coder (code) | Hover/bob, nghiêng thân theo vận tốc (banking), giật khi bắn, chớp trúng đòn 0,05s, rung 0,10/20 frame, lửa động cơ bằng particle dài/ngắn theo di chuyển |
| **Đạo diễn trận đấu** | Art dựng kịch bản, coder cài hệ thống | Máy trạng thái theo **tình huống** (vị trí người chơi, %HP, lượt đòn) — cấm cài theo mốc giây chết, cấm nhúng GIF/hoạt cảnh vào game |

Nguyên tắc điện ảnh áp cho mọi trận lớn: **khởi đòn đọc được (anticipation)
→ va chạm có khung đứng hình + chớp (impact) → nhịp thở sau đòn (recovery)**.
Chuyển động mà không phục vụ 3 nhịp này là trang trí thừa.

## 5. Chỉ đạo boss (boss doctrine)

Mỗi boss là một **nhân vật** có: tên gọi nội bộ, tính cách chiến đấu một câu
(ví dụ: "lão luyện và khinh địch — áp đảo chậm rãi, nổi điên khi bị thương"),
vũ khí dấu ấn riêng (boss này: tia quét + tên lửa khóa).

Cấu trúc trận bắt buộc 3 hồi theo % HP (100–70 / 70–30 / 30–0):

- **Hồi 1 — Áp đảo:** vào trận có nghi thức; đòn thưa mạnh; boss có hành vi
  "diễn" (tiến ép sân, dừng đánh giá) cho thấy tính cách.
- **Hồi 2 — Thách thức:** khoảnh khắc boss "nhận ra đối thủ" (dừng, lõi gắt
  sáng) rồi đổi nhịp: kết hợp đòn ép góc, nghỉ ngắn.
- **Hồi 3 — Tuyệt vọng:** hư hại visible tăng theo bậc, bắn nhanh nhưng
  kém chính xác hơn, một đòn tuyệt vọng kéo dài; **cái chết là cao trào
  ≥3 giây nổ theo chuỗi có thứ tự** (bộ phận nổ trước → cháy lan → lõi quá
  tải → nổ chính → mảnh vỡ + sóng xung kích → im lặng khói tàn).

Mỗi đòn trong hồ sơ boss phải trả lời được 3 câu: báo trước bằng gì/mấy
giây? né bằng cách nào? vì sao tồn tại trong câu chuyện của trận này?
Không trả lời được thì cắt đòn.

## 6. Chỉ đạo hangar (hangar doctrine)

Hangar là **scene thật trong game**, không phải màn hình chọn tàu trá hình:

- Không gian: khoang trạm vũ trụ có sàn, bệ phóng trung tâm, giàn hai bên,
  ánh sáng tập trung vào tàu; tàu treo trên bệ, bóng co giãn theo nhịp hover,
  lửa đuôi cháy nhỏ đều, glow thở.
- Sự sống môi trường: đèn khoang so le, khói mỏng, tia lửa ngẫu nhiên, vòng
  bệ xoay chậm — người chơi đứng yên 30 giây vẫn thấy cảnh sống.
- Chức năng: đổi qua lại các tàu sở hữu (tàu hiện thật khác nhau), xem chỉ
  số, nâng cấp (dù nông), nút xuất kích — mọi thao tác có phản hồi hình/
  động nhỏ. Đây là nơi bán "cảm giác sở hữu" của game thương mại.

## 7. Chỉ đạo địch & wave (enemy doctrine)

- Địch là **đội hình**, không phải cá thể rải rác: mỗi wave một ý đồ (ép
  hai cánh, vòng cung đạn, drone bao vây...) đọc được trong dữ liệu wave
  nguyên mẫu (282 wave là thư viện tham chiếu ý đồ).
- Mỗi họ địch có dấu ấn hình + hành vi riêng (nhanh giòn, chậm trâu, quay
  tại chỗ bắn tỏa...). Màu địch luôn đối lập phe ta để đọc trận.
- Leo thang trong 5 wave: wave sau thêm *ý đồ mới*, không chỉ tăng máu.

## 8. Chỉ đạo cảm giác (game feel / juice)

Chuẩn đã đo từ nguyên mẫu/spec: chớp trúng đòn 0,05s; rung màn hình
0,10/20 frame khi va chạm lớn; đạn và va chạm có tia lửa + âm thanh đi cặp;
boss chết dọn sạch đạn bằng sóng xung kích. Mọi hiệu ứng mới phải khai:
kích hoạt bởi sự kiện gì, kéo dài bao lâu, mạnh cỡ nào — không thêm "cho đẹp".

## 9. Chỉ đạo giao diện & âm thanh

- UI là Control thật trong engine theo khung art giao; chữ tối thiểu, biểu
  tượng là chính; mọi nút có trạng thái hover/nhấn.
- Âm thanh: mỗi hành động chính có tiếng cặp (bắn, trúng, nổ, cảnh báo boss,
  tia sạc) theo `audio_rules.json`; nhạc nền theo khu vực (hangar yên,
  trận căng, boss riêng) — chưa có nhạc thì ghi placeholder, không im lặng
  giả vờ xong.

## 10. Thước đo tiến độ (điều cấm kỵ khi báo cáo)

- Tiến độ chỉ tính bằng **thứ người chơi thấy được**: số scene hoàn chỉnh,
  số asset thật trên tổng số slot, số giây chuyển động chạy trong build,
  số trận/hồi boss chơi được. **Cấm** dùng số test pass, số run CI xanh,
  số chỉ số đo ảnh làm thước đo tiến độ game.
- Nghiệm thu bằng chứng theo thứ hạng tin cậy: (1) USER chạy trên máy;
  (2) clip/screenshot từ build thật có tương tác khác nhau giữa 2 lần chơi;
  (3) GIF hoạt cảnh dựng từ asset thật; (4) ảnh tĩnh. Cấm gọi bằng chứng
  hạng 3–4 bằng tên của hạng 1–2 (bài học "hangar" trên nền sao).
- Fallback/placeholder phải luôn được nêu tên trong mọi báo cáo — không để
  cơ chế dự phòng che mất phần chưa làm.

## 11. Lộ trình sản xuất (đạo diễn định hướng)

1. **Đóng gói Boss-37001 thành hồ sơ đầy đủ** (linh kiện + kịch bản 3 hồi +
   spec số + bằng chứng xoay) → coder cài thành hệ thống → nghiệm thu 2
   clip chơi khác nhau. Đây là boss mẫu chuẩn cho 38 boss sau.
2. **Hangar thật** theo Chương 6 (coder dựng scene bằng khung tạm song
   song art giao nền/giàn/bệ theo lô ảnh).
3. **Đội địch 5 wave** theo Chương 7 (art theo lô 10 ảnh/turn, đủ họ địch
   của 5 wave; coder cài ý đồ wave).
4. Chốt Launch Slice trọn vòng lặp Chương 2 → USER nghiệm thu như một
   game nhỏ hoàn chỉnh → mới bàn mở rộng nội dung (thêm chặng/boss/tàu).

Mọi session nhận việc phải khai đầu báo cáo: *"Làm theo GAME_DIRECTOR_VISION
chương X"* — không khai được thì chưa bắt đầu.
