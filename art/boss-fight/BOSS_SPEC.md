# Boss-37001 — BẢNG CHUẨN ĐẠN & PHA

**STATUS: ART CHƯA XONG; ENGINE CHUYỂN CODER QA.** Có test pivot 360° độc lập, chưa chốt hồ sơ art. Chuẩn kịch bản/số do director quyết; art không tự thay chuẩn. Nguồn hiệu lực: `docs/design/03_BOSS_BOOK.md` §3.2 và §3.5, `04_COMBAT_FX_ART_ANIMATION.md` §4.1, `06_PRODUCTION_ROADMAP.md` §6.4.1 tại commit `28716f4` (bao gồm §3.5 câu 7; các quyết định số ở `185aa8b09cb30209a8a02871d27674ad048f1407`) nhánh `arena/020ecffe-windwings-space-shooter-game-p`. Gốc nguyên bản: `docs/spec/COMBAT.md` §0/§3/§7, `ENEMY_BEHAVIOUR.md` §1.3, `Gun_Attack.csv` dòng 319/81/445, `Bullet_Linearly.csv` dòng 4/74/148. Hình mới không phải sprite gốc.

## Sáu quyết định có hiệu lực

1. `Gun_Attack.csv:319` là súng con BigGunWing1 trong MB-39005 của Boss-37001 [GỐC]; `m_Enabled=0` là mặc định serialize, code gốc bật; dòng 445 là cấu hình khác cùng module. Boss Book §3.5(1).
2. `(countShots; timeShot; timeReload; timeRounds; countMags) = (0; 0; 0,6; 1,8; 3)`: 3 băng × 1 viên, cách 0,6 s, nghỉ 1,8 s từ viên cuối đến viên đầu vòng sau [GỐC + ĐẠO DIỄN].
3. `border.w=15` là số nội bộ gốc, `pointRadius=0,15`; director chốt ánh xạ 100:1 → **bán kính hitbox đạn game mới 0,15 unit**; collider tia **rộng 0,3 unit** (đường kính). Không chép số 15 thô vào game mới.
4. Pháo DOMINANT **330/viên [GỐC]**, đạn nhanh/tỏa ENRAGED và PANIC **150/viên [ĐẠO DIỄN]**, tên lửa **300/quả [GỐC]**; tia **120 mỗi 0,5 s [DESIGN Boss Book §3.2]**.
5. Không cộng dồn nghỉ: trong một đòn nhịp `GunData` điều khiển; giữa các đòn khác dùng thời gian nghỉ của pha tính từ viên cuối. Nếu đòn kế tiếp dùng cùng súng, dùng `timeRounds` của súng, không cộng nghỉ sách.
6. 80059 và 80027 là **tham chiếu thông số theo hành vi**; sprite mới lần lượt thuộc họ cầu/laser và tên lửa, **không gọi là hình/đạn gốc**.

7. Hư hại và lắp linh kiện chấm tổng thể ở cỡ game và trong chuyển động; không chấm khớp từng pixel. Art tự chọn biến thể thân hoặc overlay. [ART] tự đánh giá; collider, khe né và muzzle trong runtime là [ENGINE] **CHUYỂN CODER QA**, không chặn kết luận art. Book §3.5(7), `28716f4`.

## A. Bảng đạn theo đòn

CS/TS/TR/TĐ/CM = `countShots/timeShot/timeReload/timeRounds/countMags`. Các điểm `T` là canvas 512², số hiện có từ `manifest.json` **chưa chứng minh**, không dùng như pivot đã chốt. Numeric 15 bên dưới chỉ ghi nguồn gốc, collider game mới là 0,15.

| Đòn / hình mới | Speed / damage | Collider game mới / flags gốc | CS; TS; TR; TĐ; CM | Telegraph / điểm sinh T | Nguồn |
|---|---|---|---|---|---|
| DOMINANT pháo nặng, họ cầu năng lượng | 16 / **330** | bán kính **0,15 unit**; `throughShield=False`, `throughAll=False`, `fixedOnLinecast=False` | `0; 0; 0,6; 1,8; 3` | **0,9 s** [ĐẠO DIỄN §3.5(4)]; `(144,280)`, `(368,280)` [CHƯA ĐO] | [GỐC] Gun319, BLT_Linearly:4; [ĐẠO DIỄN] Book §3.5; hình mới tham chiếu dòng 319 |
| ENRAGED liên thanh, họ cầu/laser mới | 16 / **150** | 0,15 unit; flags như trên | `0; 0; 0,6; 1,8; 3` | 0,9 s [ĐỀ XUẤT, chưa director chốt]; hai ụ như trên [CHƯA ĐO] | [GỐC] nhịp/speed Gun319; **damage 150 [ĐẠO DIỄN]** §3.5(4); hình mới tham chiếu dòng 319 |
| PANIC tỏa, họ laser mới | 16 / **150** | 0,15 unit; flags như trên | `0; 0; 0,46153848; 1,8; 3` | 0,8 s [ĐỀ XUẤT, chưa chốt]; hai ụ như trên [CHƯA ĐO] | [ĐẠO DIỄN] +30% nhịp, ±6° Book §3.2; **0,6/1,3 = 0,46153848 s [ĐỀ XUẤT cách áp]**; damage 150 §3.5(4) |
| Tên lửa 4 cặp, hình mới họ tên lửa | 4,8 / **300** | 0,15 unit; flags False theo BLT_80027 | `0; 0; 0,18; 0,8; 4` mỗi pod | reticle bám **0,8 s**, khóa rồi bắn; `(68,333)`, `(444,333)` [CHƯA ĐO] | [GỐC] Gun81, Bullet_Linearly:74; [ĐẠO DIỄN] Book §3.5(6), hình mới tham chiếu dòng 81 |
| Tia quét | không phải đạn viên; **120/0,5 s** | **rộng 0,3 unit**; quầng ngoài không tính | N/A (không chứng minh GunData cho tia) | sạc **1,2 s**, quét **−25°→+25° trong 1,9 s**; `(256,399)` [CHƯA ĐO] | [DESIGN] Book §3.2; collider [ĐẠO DIỄN] §3.5(3) |
| Tia cuối PANIC | 120/0,5 s nếu cùng tia [ĐỀ XUẤT, chưa chốt] | **rộng 0,3 unit** | N/A | **2 chiều liên tiếp**; cùng góc/thời gian từng chiều là [ĐỀ XUẤT, chưa chốt] | [DESIGN] Book §3.2, §3.5(3) |

## B. Pha

| Pha | Thứ tự và nghỉ | Biến đổi / di chuyển | Ranh giới |
|---|---|---|---|
| DOMINANT >70% | vào trận **1,5 s**, pháo nặng; giữa hai đòn khác **1,6 s**; nếu dùng lại cùng súng nghỉ `timeRounds=1,8 s`, không cộng 1,6 | damage **330**, 3 viên/vòng; tiến xuống ép sân **2 s** rồi lui; biên độ, điểm đến và thời gian lui **chưa director chốt** | HP ≤70% → dừng 0,5 s, lõi sáng; xử lý đòn đang dở **chưa chốt** |
| ENRAGED 30–70% | nhận diện **0,5 s**; 3 viên, khóa tên lửa + tia; giữa các đòn khác **0,8 s**, nếu cùng súng dùng timeRounds không cộng dồn | damage viên nhanh **150**, tên lửa **300**, tia **120/0,5 s**; thứ tự kết hợp, di chuyển cụ thể **chưa chốt** | HP <30% → PANIC; xử lý đòn đang dở **chưa chốt** |
| PANIC <30% | bắn nhanh/tỏa, tia cuối quét **hai chiều liên tiếp**; nghỉ sau đòn **chưa director chốt** | nhịp pháo nhanh hơn **30%**, tỏa **±6°**, damage **150**; lõi quá tải khi **<15% HP** | HP ≤0 → DYING; thời điểm ngắt collider **chưa chốt** |
| DYING | ụ trái nổ → pod phải cháy → điện dọc thân → trắng **0,3 s** → nổ chính → **3–4 mảnh** + sóng dọn đạn địch → khói **1 s**; tổng **≥3 s** | thứ tự [DESIGN]; hitbox, timing chi tiết **chưa chốt** | kết quả sau chuỗi |

## C. CLIP CẦN SỬA

1. `build-cinematic.py:88,118`: báo 1,1 s/quét 1,4 s/±24° thay vì **1,2 s/1,9 s/±25°**.
2. `:109–116`: reticle bị lệch vị trí tàu, 3 cặp thay vì **bám 0,8 s rồi 4 cặp**.
3. `:119`: tia cuối một chiều, yêu cầu **2 chiều**; fan chưa chứng minh ×1,3 và ±6°.
4. `:32`: vào trận 2 s thay vì **1,5 s**; chuyển động ép sân chưa chứng minh đúng **2 s**.
5. `:91`: lõi sáng từ đầu PANIC thay vì **<15% HP**; `:134` 10 mảnh thay vì **3–4**; flash chưa chứng minh trắng **0,3 s**.
6. `:105` tốc độ theo px/s chưa map world; chưa chứng minh collider **0,15 unit** và tia **0,3 unit**, damage **330/150/300** và né an toàn.
7. Cần kiểm màu đạn địch nóng/đạn ta lạnh, đèn thành đỏ khi sạc; chuỗi chết ≥3 s và khói tàn 1 s phải duyệt độc lập.
8. Cần chứng minh 2 pivot bằng GIF quay 360° và overlay hư hại ghép đúng; xem không tiếng, đánh giá cỡ thật và nêu cách né từng đòn.

Không khẳng định đoạn nào đã qua QA chỉ từ bảng này. Không render lại trong bước cập nhật SPEC.

## D. Thiết kế bộ đạn mới — ứng viên B2/B3, chưa hoàn tất

Gói `masters/bullet-B2`, `bullet-B3` và đầu/thân tia B1 vẽ mới, không dùng sprite gốc; `exports/bullet-B2` là bản thử, **chưa là production**. Body và 3 mức glow được xuất riêng; tách theo alpha, tâm phát sáng vẫn nằm trong body; cần kiểm pulse ở cỡ game. Không đổi số trong bảng A; điểm sinh T dưới đây là ước lượng trên canvas 512, kiểm runtime giao coder.

| Họ mới / đòn | Hình | Tham chiếu / damage | Tâm / điểm sinh dự kiến | Glow chồng |
|---|---|---|---|---|
| Cầu DOMINANT | cầu lớn cam đỏ / lõi vàng trắng | Gun319 / 16 / 330; bán kính 0,15 unit | tâm canvas; ụ trái/phải, muzzle thực **chuyển coder QA** | `heavy-orb/glow-{0,1,2}.png` |
| Laser ENRAGED | mũi dài tím hồng | Gun319 / 16 / 150; 0,15 unit | tâm canvas; ụ trái/phải, muzzle runtime chờ coder | `laser/glow-{0,1,2}.png` |
| Tỏa PANIC | sao nhỏ vàng | Gun319 / 16 / 150; 0,15 unit; nhịp ×1,3 và ±6° | tâm canvas; ụ trái/phải, muzzle runtime chờ coder | `panic/glow-{0,1,2}.png` |
| Tên lửa | thân cơ khí mũi đỏ + khói rời | Gun81 / 4,8 / 300; 0,15 unit | tâm canvas; đuôi phía trên do mũi hướng xuống; pod trái/phải, runtime chờ coder | `missile/glow-{0,1,2}.png`; `missile-trail/body.png` riêng |
| Tia | đầu nổ đỏ + thân dài cam | Book §3.2 / 120 mỗi 0,5s; collider rộng 0,3 unit | đầu tia pháo giữa; runtime chờ coder | `beam-head/glow-{0,1,2}.png`; `beam-strip/glow-{0,1,2}.png`; top/bottom pixel trùng, filter runtime chuyển coder |

Sheet tham khảo `exports/bullet-B2/projectile-real-size-study.png` dùng PLAYER 18 px / 1,4 unit trên canvas 240×350, các kích thước đạn là **đề xuất minh họa**, chưa hiệu chỉnh runtime. Không xem sheet này là xác nhận va chạm hay QA engine.

Tên lửa B3: body 64², tâm đề xuất `(32,32)`; đầu hướng +Y, tâm ổ phụt phía sau `(32,4)`; plume 64×128 có đầu nối gần `(32,124)`. Các anchor là đề xuất art, điểm gắn runtime **CHUYỂN CODER QA**. Màu body được tự điều chỉnh từ cam sang đỏ; tâm sáng giữ trung tính.
