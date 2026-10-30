# Boss-37001 DREADNOUGHT — SPEC thiết kế / CHƯA HOÀN THÀNH

Nguồn hiệu lực: `docs/design/03_BOSS_BOOK.md` §3.2A và §3.5, `docs/design/06_PRODUCTION_ROADMAP.md` Mốc A tại commit director `5701bed` (nhánh `arena/020ecffe`). §3.2A thay cấu tạo và chiến đấu tối thiểu cũ khi khác nhau; §3.2 giữ nền tính cách. Bộ cũ commit `fd4f65a` **không phải** bản nâng cấp hoàn thành. `BOSS_CINEMATIC.md` mô tả 7 tiết mục; `dreadnought-manifest.json` là kiểm kê thiết kế, tọa độ đo và asset final chưa có.

## Cấu tạo: 5 vòng, 11 điểm hỏa lực

Vị trí trong bảng là **vùng thiết kế**, không phải điểm sinh đã đo. Canvas 512², hướng xuống. Thứ tự lớp: 3 biến thể thân → đế tĩnh → pod → đầu quay BigGun/ụ phụ → vòng giáp lõi → lõi glow → pháo giữa → khói/lửa hư hại → FX.

| Vòng | Điểm hỏa lực | Vị trí thiết kế x,y | Chuyển động / yêu cầu |
|---|---|---|---|
| 1 | BigGun trái / phải | (118,252) / (394,252) | đế tĩnh đường kính 74–88 px; đầu quay độc lập ±65° |
| 2 | Main Cannon / đầu tia | (256,356) | thân **cố định**; emitter sáng khi sạc |
| 3 | ụ vai trái / phải | (92,142) / (420,142) | mỗi ụ đế riêng + đầu 1–2 nòng quay ±45° |
| 3 | ụ hông trái / phải | (70,330) / (442,330) | mỗi ụ đế riêng + đầu 1–2 nòng quay ±35° |
| 4 | pod trái / phải | (42,238) / (470,238) | thân **cố định**; 8 ống/pod; nắp/đèn chuyển trạng thái |
| 5 | pháo quạt trái / phải | (188,292) / (324,292) | **cố định**, hướng xuống-trái / xuống-phải |

Lõi `(256,228)`, Ø≈62 px, vòng giáp mở/đóng; không tính lõi là điểm hỏa lực. Pivot và muzzle chính thức **chưa đo**. Mọi đầu quay cần đế độc lập + GIF 360° trên thân; mọi họng cần tọa độ trong manifest. Tọa độ thiết kế không được dùng làm tọa độ final.

## Cơ chế bộ phận

| Bộ phận | HP bộ phận | Hệ quả sau phá |
|---|---:|---|
| BigGun trái/phải, mỗi | 18.000 **[ĐỀ XUẤT director §3.2A B]** | đầu nổ, đế cháy; mất một → ụ còn lại Overdrive nhịp tổng ×0,8, tỏa thêm ±3°; mất hai → lõi mở lâu hơn sau đòn |
| ụ phụ, mỗi | 7.500 **[ĐỀ XUẤT director]** | tắt ụ, đế cháy; mất hai ụ phụ cùng phía → điểm mù tương đối và boss tăng tần suất tên lửa |
| pod, mỗi | 12.000 **[ĐỀ XUẤT director]** | pod cháy, ngừng phóng; mất một → 2 cặp/lượt; mất hai → tăng sử dụng Main Cannon |
| pháo quạt, mỗi | 6.000 **[ĐỀ XUẤT director]** | tắt quạt phía đó, áp sát phía bị phá an toàn hơn |
| lõi | không HP riêng trước khi lộ | khi lộ nhận ×1,5 damage; quá tải dưới 15% HP thân |

Thân 225.000 HP [GỐC]. Bắn trúng bộ phận trừ HP bộ phận và HP thân theo ×1,0, không cộng hai lần vào thân. Mỗi lần mất bộ phận lớn: dừng 0,4s → điện chớp tại chỗ → đổi vòng đòn ngay. Chi tiết timing chưa được chốt ghi [ĐỀ XUẤT], không tự khóa số.

## Bảng đạn và nhịp

Các họ hình là **hình vẽ mới**, G319/G81 chỉ tham chiếu thông số theo hành vi; không gọi là sprite/đạn gốc. `border.w=15` gốc ánh xạ hitbox mới bán kính 0,15 unit; collider tia rộng 0,3 unit [ĐẠO DIỄN §3.5(3)]. Hình có thể lớn hơn hitbox. Collider, damage và muzzle runtime chuyển coder QA.

| Vũ khí | Mẫu / telegraph | Họ đạn | Damage | Nguồn / số chưa chốt |
|---|---|---|---:|---|
| BigGun mỗi ụ | 3 băng × 1 viên; cách 0,6s, `timeRounds=1,8s` từ viên cuối; báo họng 0,9s | cầu lớn | 330 | G319 [GỐC], §3.5 [ĐẠO DIỄN]; speed 16 tham chiếu G319 |
| BigGun Overdrive | cùng mẫu, nhịp tổng ×0,8, tỏa thêm ±3° | cầu | 330 | §3.2A C [ĐẠO DIỄN]; cách áp ×0,8 vào từng trường chưa chốt, không tự ghi |
| ụ vai | 3 viên/băng, 0,12s; 2 băng; nghỉ 1,4s | laser dài | 150 | §3.2A C [ĐẠO DIỄN]; speed, thời gian giữa 2 băng và telegraph riêng chưa chốt |
| ụ hông | quạt 5 viên, −24°→+24°, 1 băng; nghỉ 1,8s | tỏa vàng | 150 | §3.2A C [ĐẠO DIỄN]; speed/telegraph riêng chưa chốt |
| Main Cannon không tia | 1 phát, sạc 1,0s, nghỉ 2,2s; hình 1,25× cầu BigGun | cầu nặng | 330 | §3.2A C [ĐẠO DIỄN]; speed chưa chốt |
| tia quét | sạc 1,2s và cảnh báo; −25°→+25° trong 1,9s | tia liên tục | 120/0,5s | §3.2/§3.2A; rộng 0,3 unit §3.5 |
| tên lửa mỗi pod | khóa 0,8s; 2 cặp/pod/lượt, tổng 4 cặp khi còn 2 pod | tên lửa + khói rời | 300/quả | G81 speed 4,8 tham chiếu [GỐC], số cặp §3.2A C [DESIGN]; khóa chỉ kích hoạt khi điều kiện mục D(4) |
| pháo quạt lõi | quạt 7 viên ngắn khi tàu vào nửa dưới giữa sân; 2 đèn đỏ báo 0,6s; nghỉ 2,6s | tỏa nhỏ | 150 | §3.2A C [ĐẠO DIỄN]; góc quạt/speed chưa chốt |

Nghỉ riêng từng vũ khí ở §3.2A C ưu tiên khi áp dụng; nghỉ giữa đòn khác ở nền §3.2: hồi 1 1,6s, hồi 2 0,8s; không cộng với `timeRounds`; cùng súng dùng `timeRounds` §3.5(5). Trong Hồi 3, ụ còn sống nhanh ×1,3 và tỏa loạn ±6°; cứ 2 vòng thường có 1 tia hai chiều. Cách kết hợp Overdrive ×0,8 và ×1,3 nếu cùng lúc là **[ĐỀ XUẤT: chưa chọn phép kết hợp]**, không tự tuyên bố director đã chốt.

## Các số còn thiếu — [ĐỀ XUẤT], chưa duyệt

Các số dưới đây chỉ để director có cơ sở đối chiếu, **không thay thế bảng đã chốt** và không được coi là số runtime đã duyệt:

- Ụ vai: speed **16 unit/s** (tham chiếu G319), báo trước **0,6s** và khoảng giữa hai băng **0,6s**. Đạn trong mỗi băng vẫn **0,12s**, 2 băng và nghỉ **1,4s** theo §3.2A C.
- Ụ hông: speed **12 unit/s**, báo trước **0,6s**. Quạt 5 viên ±24° và nghỉ 1,8s giữ nguyên §3.2A C.
- Main Cannon phát đơn: speed **12 unit/s** (tham chiếu speed G445, không khẳng định G445 là cấu hình đòn), vẫn sạc 1,0s và nghỉ 2,2s.
- Quạt lõi: speed **12 unit/s**, 7 hướng đều **−24°, −16°, −8°, 0°, +8°, +16°, +24°**; đèn báo 0,6s, điều kiện kích hoạt và nghỉ 2,6s giữ đúng §3.2A C.
- Nếu Overdrive và PANIC cùng áp dụng: **[ĐỀ XUẤT]** nhân thời gian ×0,8 rồi chia 1,3; ví dụ 0,6 × 0,8 / 1,3 ≈ 0,3692s. Cách kết hợp này chưa được director chốt; không được triển khai như quy tắc chính thức chỉ dựa trên đề xuất art.

## Hư hại và bàn giao

Ba biến thể thân theo ngưỡng HP phải có các **đế cháy** tương ứng: vừa cháy nhỏ 2–3 điểm; nặng cháy pod/ụ, nứt từ lõi ra cánh, khói bám thân. Có trạng thái từng BigGun và từng pod đã phá: đầu/phần hoạt động biến mất, đế cháy còn lại. Bản cũ chỉ là nguồn tham khảo/tái dùng nếu khớp cấu tạo, chưa đủ. Đánh giá theo tổng thể cỡ game + chuyển động, không chấm từng pixel. Bản GIF cũ <40s và không có 7 tiết mục, không phải DREADNOUGHT.
