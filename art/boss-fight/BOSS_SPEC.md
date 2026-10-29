# Boss-37001 — BẢNG CHUẨN ĐẠN & PHA

**STATUS: CHƯA XONG / cần director giải quyết câu hỏi cuối tài liệu.** Không phải dữ liệu gameplay đã triển khai. Các con số gốc giữ nguyên; việc chọn một dòng gốc làm mẫu cho đòn của boss mới là **[GÁN ĐỀ XUẤT]**, không biến dòng đó thành bằng chứng gốc của chính đòn mới. Không chỉnh `docs/spec/`, `datas/`, `tools/`, `tests/`.

## Các mục đã đọc

- `docs/spec/COMBAT.md` §0 (dòng 11–35), §3/§3.1–3.2 (130–175), §7 (436–464), đồng thời §2.1 và §5.1 để đối chiếu ngữ cảnh.
- `reverse-engineering/scriptableobjects/Gun_Attack.csv`: header, các dòng 319/445 có chuỗi `Boss-37001`, dòng 81 để tham khảo mẫu 4 băng; `Bullet_Linearly.csv` header, dòng 4/74/148; `Bullet_SineWave.csv` header và dòng 2–3. Có đọc `bltDamage`, `bltSpeed`, `bltId`, 5 trường `allGunDatas`, `border.w`, `pointRadius[0]`, `throughShield`, `throughAll`, `fixedOnLinecast`, `m_Enabled`, `gunType`.
- `docs/spec/ENEMY_BEHAVIOUR.md` §1.3 (62–76); `datas/sprites.csv` lọc tên không phân biệt hoa thường: 7 dòng = `EBullet-17` Texture2D/Sprite (233, 1488), `bullet_trail_3` (364), atlas `Bullets` (622), `Efx_BulletHit_0/1/2` (1957, 2653, 2656). Đây là **chỉ mục tên/kích thước**, không chứng minh hình dạng riêng của từng `bltId`; không dùng lại ảnh gốc.
- Từ nhánh `arena/020ecffe-windwings-space-shooter-game-p` commit `137f166eebcadfe979440b26da4674160ae296bd`: `docs/design/04_COMBAT_FX_ART_ANIMATION.md` §4.1, `03_BOSS_BOOK.md` §3.1 mục 9 + §3.2, `06_PRODUCTION_ROADMAP.md` Mốc A. Đã đọc cả `art/boss-fight/CINEMATIC_SPEC.md` cũ và `manifest.json`/`build-cinematic.py`.

**Ba số gốc áp dụng:** 15,0 (`border.w` 184/186; COMBAT §7), 330,0 damage và 16,0 tốc độ (`Gun_Attack.csv` dòng 319, `bltDamage`/`bltSpeed`), 3 băng × `timeReload=0,6000000238` (`Gun_Attack.csv` dòng 319). Không đổi damage mỗi viên để làm boss mạnh hơn; dùng mật độ và lịch pha.

## Quy ước và giới hạn nguồn

- Thứ tự bộ 5 luôn là **(countShots, timeShot, timeReload, timeRounds, countMags)**. Dòng gốc `countShots=0` phải lưu nguyên 0; COMBAT §3.1 mô tả mặc định constructor là 1 nòng. `timeShot=0` và `timeReload>0` là hai trường khác nhau: không biến 0 thành khoảng thời gian ba phát. Bộ 5 là cấu hình **mỗi nòng/pod**, không tự nhân thêm nòng khi đếm viên.
- Hai dòng có đường dẫn bắt đầu `Boss-37001/…/MB-39005`: `Gun_Attack.csv:319`, `path_id=651246`, `bltId=80059`, `m_Enabled=0`, `gunType=1`; và `:445`, `path_id=699809`, `bltId=80049`, `m_Enabled=1`, `gunType=3` (Passive — COMBAT §2.1). Đây là dữ liệu **nested MB-39005**, không đủ chứng cứ gán chắc cho pháo chính mới. `COMBAT.md:305–308` lại liệt kê 37001 không có súng ở root: cần làm rõ cách nhóm root trước khi coi đây là súng gốc trực tiếp của boss.
- Bullet `80059` (`Bullet_Linearly.csv:4`), `80049` (`:148`), `80027` (`:74`) đều: `border.w=15.0`, `pointRadius[0]=0.15000000596046448`, `throughShield=False`, `throughAll=False`, `fixedOnLinecast=False`. `border.w` và `pointRadius` là **hai trường riêng**; chưa có phép chuyển đã kiểm chứng giữa hai đơn vị, không tự biến 15 thành 0,15 hay thành px. 799/800 `Enemy_Movement` cũng có `border.w=15` theo `ENEMY_BEHAVIOUR.md` §1.3; **không chứng minh 15 là bán kính hình tròn trong engine mới**.
- Phân bố raw theo COMBAT §3.1: `countShots=0` **421** dòng, `timeShot=0` **397**, `timeReload=0,20` **61**, `timeRounds=2,0` **91**, `countMags=3` **125**; đây là phân bố riêng từng trường, **không** chứng minh chúng cùng nằm trên một dòng.
- `Bullet_SineWave.csv:2–3` có `BLT_80104/80105`, `border.w=10`, `speed=12`, nhưng không đủ liên kết hình/đòn Boss-37001; không tự đổi toàn bộ họ sang sine-wave.
- Cảnh báo và lịch pha ở `03_BOSS_BOOK.md` là **thiết kế được director chốt [DESIGN]**, không phải số trích từ nguyên mẫu. Sprite của ta dùng nóng cho đạn địch, lạnh cho đạn ta theo `04 §4.1`; không cắt/chắp sprite gốc.

## A. Bảng đạn theo đòn

Số trong cột nguồn là dòng vật lý có header là dòng 1. `T` = canvas 512×512, gốc trên trái; các điểm pixel từ `art/boss-fight/manifest.json` là **[ĐỀ XUẤT/CHƯA ĐO]**, không được xem là pivot đã chứng minh. Số đạn/visual cần xác minh ở engine.

| Đòn / họ hình của bản mới | Tốc độ gốc / damage | Hitbox / flags | 5 tham số mỗi nòng (CS, TS, TR, TĐ, CM) | Cảnh báo | Điểm sinh T | NGUỒN / giới hạn |
|---|---|---|---|---|---|---|
| DOMINANT — pháo xoay, cầu năng lượng 2 nòng | 16,0 / 330,0 mỗi viên | `border.w=15`; `pointRadius[0]=0,15`; `throughShield=False`, `throughAll=False`, `fixedOnLinecast=False` | `(0, 0, 0,6000000238, 1,7999999523, 3)` | **0,9 s [ĐỀ XUẤT]**, sách chưa định lượng cảnh báo pháo | trái `(144,280)`, phải `(368,280)` [ĐỀ XUẤT/CHƯA ĐO] | **[GỐC]** `Gun_Attack.csv:319` / `bltId=80059`, `bltDamage`, `bltSpeed`, `allGunDatas[0].*`; `Bullet_Linearly.csv:4`; **[GÁN ĐỀ XUẤT]** dùng mẫu nested MB-39005 cho 2 ụ và vẽ lại cầu; sprite `80059` chưa join. |
| ENRAGED — liên thanh 3 viên mỗi nòng, đồng thời có thể kết hợp đòn khác | 16,0 / 330,0 | như dòng 80059 | `(0, 0, 0,6000000238, 1,7999999523, 3)`; 3 băng, **dự kiến** 1 nòng mặc định/băng | **0,9 s [ĐỀ XUẤT]** | `(144,280)` / `(368,280)` [CHƯA ĐO] | **[GỐC]** `Gun_Attack.csv:319`, `Bullet_Linearly.csv:4`, COMBAT §3.1; **[DESIGN]** Boss Book 3.2 ba viên; **[GÁN ĐỀ XUẤT]** ánh xạ ba băng vào ba viên, phải xác minh runtime `countShots=0`/barrels. |
| PANIC — đạn thẳng tỏa ±6° | 16,0 / 330,0 | như dòng 80059 | `(0, 0, 0,46153848, 1,7999999523, 3)` | **0,8 s [ĐỀ XUẤT]** | `(144,280)` / `(368,280)` [CHƯA ĐO] | **[GỐC]** các số trừ `timeReload`: `Gun_Attack.csv:319`, `Bullet_Linearly.csv:4`; **[DESIGN]** Boss Book 3.2 +30% tốc độ bắn, ±6°; **[ĐỀ XUẤT]** `0,6000000238/1,3=0,46153848 s` vì sách không nói trường nào thay đổi; speed đạn giữ 16. |
| Tên lửa — 4 cặp, hướng về vị trí đã khóa, không bám sau phóng | 4,8000001907 / 300,0 | `border.w=15`, `pointRadius[0]=0,15`, 3 flags False như trên | `(0, 0, 0,1800000072, 0,8000000119, 4)` **mỗi pod**, 2 pod đồng bộ dự kiến 4 cặp | **0,8 s** reticle bám rồi khóa [DESIGN Boss Book 3.2] | `(68,333)` / `(444,333)` [ĐỀ XUẤT/CHƯA ĐO] | **[GỐC]** `Gun_Attack.csv:81`, `bltId=80027`, 5 trường + damage/speed; `Bullet_Linearly.csv:74`; **[GÁN ĐỀ XUẤT]** dùng hàng Boss-39010 làm mẫu 4 băng, không có chứng cứ `80027` là sprite tên lửa/homing. Tên lửa và luật khóa là thiết kế mới; cần xác nhận. |
| Tia Lão Hống — liên tục, không đạn viên | **N/A tốc độ đạn**, 120 HP mỗi 0,5 s (240 HP/s khi liên tục chạm) | **CHƯA XÁC ĐỊNH** bề rộng collider tia, `border.w`/`pointRadius`/flags viên không áp dụng tự động cho tia liên tục | `(N/A, N/A, N/A, N/A, N/A)` — không có `GunData` đạn viên được chứng minh | **1,2 s** [DESIGN]; quét `−25°→+25°` **1,9 s** | `(256,399)` [ĐỀ XUẤT/CHƯA ĐO] | **[DESIGN]** `03_BOSS_BOOK.md` §3.2, commit `137f166`; **[CHƯA TRA RA GỐC]** collider ray, 5 trường và cơ chế tick. Không gán giả BLT_80059 cho tia. |
| Tia tuyệt vọng | N/A / 120 HP mỗi 0,5 s **nếu** dùng cùng tick — [ĐỀ XUẤT] vì sách chỉ nói quét 2 chiều | CHƯA XÁC ĐỊNH như tia trên | `(N/A, N/A, N/A, N/A, N/A)` | **1,2 s [ĐỀ XUẤT]** dùng cảnh báo tia gốc thiết kế; `−25°→+25°→−25°` **1,9 s mỗi chiều [ĐỀ XUẤT]** | `(256,399)` [CHƯA ĐO] | **[DESIGN]** Boss Book 3.2 có 2 chiều; **[ĐỀ XUẤT]** cùng tick, góc và thời lượng mỗi chiều vì sách không nêu tường minh. |

### Vấn đề phải hỏi / không tự đoán

1. `COMBAT.md:305–308` ghi 37001 không có súng tại root nhưng `Gun_Attack.csv:319,445` có đường dẫn bắt đầu Boss-37001 và đi qua `MB-39005`; dòng 319 còn `m_Enabled=0`. Director/coder xác nhận hai dòng này có phải súng của boss gốc hay của prefab con và cách kích hoạt? Trong lúc chưa xác nhận, ánh xạ ở bảng vẫn là **ứng viên**, không phải boss-original fact.
2. `COMBAT.md:136–142` nói `countShots` là số nòng đồng thời, `timeShot` giãn cách trong băng; `:149` nói `countShots=0` mặc định 1, `:161` ví dụ `timeShot=0` là volley. Mẫu `(0; 0; 0,6; 1,8; 3)` trên dòng 319 có thực phát đúng **3 viên/1 nòng**, và thời gian nghỉ `timeRounds=1,8` tính từ bắt đầu hay kết thúc vòng? Cần xác nhận runtime/asm, không suy ra chắc từ tên trường.
3. `04_COMBAT_FX_ART_ANIMATION.md:23–24,42–43` gọi `border.w=15` chuẩn 184/186 và hitbox bé hơn hình ~30%; `Bullet_Linearly.csv:4,74,148` lại có `pointRadius[0]=0,15`. 15 là biên/distance/radius theo hệ gốc nào; `0,15` đơn vị nào, tỷ lệ world/viewport và ~30% có áp vào collider nào? Đề nghị coder dẫn mapping runtime, nhất là **collider của tia liên tục**.
4. `Gun_Attack.csv:319` có 330 HP/viên = **13,2%** của 2.500 HP; `04 §4.1` dòng 44–46 nói đòn thường 3–6% HP/viên và boss 10–20%/đợt trúng liên tục. Có giữ 330 gốc và chấp nhận 13,2%/viên, hay chọn một dòng gốc 75–150 HP làm mẫu? Chưa tự sửa damage.
5. `03_BOSS_BOOK.md:48–54` nghỉ giữa đòn 1,6 s / 0,8 s, còn `Gun_Attack.csv:319` `timeRounds=1,7999999523` và `:81` `0,8000000119`. Director/coder xác nhận nghỉ boss scheduler có thay thế hay cộng vào `timeRounds`? Nếu cộng cả hai, số thực tế sẽ khác; không tự giấu mâu thuẫn.
6. `datas/sprites.csv` chỉ có tên/đường dẫn/kích thước; chưa join được `bltId=80027` sang hình tên lửa hay chuyển động khóa. Xin ref/join gốc nếu director muốn gọi đây là **họ tên lửa gốc** thay vì mẫu số linear được gán mới. Tương tự cầu 80059 chưa có chứng minh hình.

## B. Bảng pha — state-driven, không chạy theo mốc GIF

`A=(144,280)`, `B=(368,280)`, `C=(256,399)`, `L=(68,333)`, `R=(444,333)` là local pixel [ĐỀ XUẤT/CHƯA ĐO]; world origin là neo boss `H`, hướng dương `+y` đi xuống. Thời gian theo giây, world unit chỉ dùng cho khoảng dịch **đề xuất**, chưa chứng minh chuyển đổi với px hay `border.w`. Trường không có ở sách được gắn [ĐỀ XUẤT].

| Pha / điều kiện | Vòng đòn, nghỉ | Hệ số / góc | Di chuyển / đích | Chuyển ngưỡng khi đòn dở | Nguồn |
|---|---|---|---|---|---|
| ENTER → DOMINANT: HP >70% | Vào **1,5 s**, sau đó lặp pháo 80059 → nghỉ **1,6 s**; **2 vòng pháo → 1 lần ép sân [ĐỀ XUẤT]** | đạn `×1,0` speed/damage so G319; ±0° cơ bản **[ĐỀ XUẤT]** | Neo `H`; tiến đến `H+(0,+0,8)` trong **2,0 s**, lui về `H` trong **2,0 s [ĐỀ XUẤT]**; sách chỉ nói 2 s rồi lui, không cho độ dịch/lui | Khi `HP≤70%` đánh dấu ngưỡng; kết thúc băng đang bắn rồi dừng **0,5 s** tại vị trí hiện tại; không phát đòn mới **[ĐỀ XUẤT]** | **[DESIGN]** Boss Book 3.2; **[GỐC]** Gun319; mọi điều kiện cụ thể khác [ĐỀ XUẤT] |
| ENRAGED: 30%≤HP≤70% sau nhận diện | 3 băng 80059 → nghỉ **0,8 s** → khóa 0,8 s + 4 cặp 80027 đồng thời với sạc 1,2 s → tia 1,9 s → nghỉ **0,8 s** → lặp **[THỨ TỰ/OVERLAP ĐỀ XUẤT]** | damage ×1,0, speed viên ×1,0 so DOMINANT; 3 băng/nòng [G319] | neo `H`, ngang `H+(±0,4,0)` trong **1,0 s mỗi đoạn [ĐỀ XUẤT]**; không ép phần thân ngoài sân | Khi `HP<30%` đánh dấu; nếu beam đang gây damage thì hết lượt quét 1,9 s, nếu đang khóa/chưa bắn thì hủy lock; đòn khác kết thúc băng hiện tại **[ĐỀ XUẤT]** | **[DESIGN]** Boss Book 3.2 70%, 0,5 s, 3 viên, 0,8 s lock/nghỉ, 4 cặp, tia; thứ tự/di chuyển/chính sách cắt [ĐỀ XUẤT] |
| PANIC: 0<HP<30% | fan 3 băng/nòng → nghỉ **0,8 s [ĐỀ XUẤT dùng nhịp hồi 2]** → sạc 1,2 s → hai sweep ×1,9 s/chiều → nghỉ **0,8 s [ĐỀ XUẤT]** → lặp | tốc độ bắn **×1,3**, interval `0,46153848 s`; góc tỏa **±6°**; damage/speed viên ×1,0. Dưới **15%** bật core overload | neo `H`, rung visual **±2 px @12 Hz [ĐỀ XUẤT]**, collider không rung; di chuyển tới `H` trong **1,0 s [ĐỀ XUẤT]** | `HP≤0`: ngắt ngay hitbox và spawn, vào `DYING`, quét đạn địch bằng sóng trong chuỗi chết **[ĐỀ XUẤT cơ chế chuyển]** | **[DESIGN]** Boss Book 3.2 30%, +30% nhịp, ±6°, 2 chiều, 15%; thời gian từng chiều/rung/nghỉ [ĐỀ XUẤT] |
| DYING | ụ trái → pod phải → điện → lõi trắng **0,3 s** → nổ → **3–4** mảnh + sóng dọn đạn → khói **1,0 s**; tổng **≥3,0 s** | **0** hitbox mới hoặc đạn boss mới [ĐỀ XUẤT] | dừng tại vị trí vào DYING, vận tốc **0** [ĐỀ XUẤT] | sau ≥3,0 s → kết quả | **[DESIGN]** Boss Book 3.2, tắt hitbox là [ĐỀ XUẤT] |

**Chưa chứng minh đường né:** hình thái/hitbox tia, vận tốc player và chuyển đổi world/px chưa xác thực. Sách nêu né khỏi đầu tia hoặc áp sát thân, nhưng chưa thể gán số corridor mà không tự bịa. Kết hợp đòn chỉ là lịch ứng viên đến khi test được đường thoát. Ngoài ra `timeRounds` và thời gian nghỉ ở bảng pha chưa có quy tắc cộng/thay thế đã duyệt (câu hỏi 5).

## C. CLIP CẦN SỬA — chưa render lại trong turn này

1. `build-cinematic.py:88,118`: cảnh báo tia **1,1 s**, sweep **1,4 s**, `±24°`; sách yêu cầu **1,2 s**, **1,9 s**, `±25°`. Đèn tường hiện chỉ `danger` tổng (`:56–59`), chưa xác nhận đỏ riêng khi sạc.
2. `:109–116`: reticle đặt lệch PLAYER ±100/105 px, không bám PLAYER **0,8 s** rồi khóa; `range(3)` = **3 cặp**, sách yêu cầu **4 cặp**.
3. `:119`: tia PANIC một chiều **1,6 s**, sách yêu cầu **hai chiều liên tiếp**. `:93–105` fan chưa mô hình ±6° và ×1,3 theo bảng; kiểm bằng số thay vì nhìn VFX.
4. `:32` boss vào **2,0 s**, sách **1,5 s**. Motion ép sân theo Gaussian, chưa chứng minh **2,0 s tiến rồi lui**; nghỉ theo thiết kế chưa đo.
5. `:91` core overload bắt đầu lúc PANIC, không chờ **<15% HP**. `:134` có **10 mảnh**, yêu cầu **3–4**; trắng màn `:139–140` là 3 frame biến thiên, chưa chứng minh **0,3 s** trắng.
6. `:105` di chuyển đạn theo **270/320 px/s**, không phải speed 16,0/4,8 unit gốc với mapping được xác nhận. Tốc độ/timing, hitbox, sát thương và né chưa có runtime nên GIF chưa chứng minh bảng.
7. Hình đạn địch trong `exports/effects/energy.png`, `laser_bullet.png`, beam được dùng trong clip cần QA theo `04 §4.1`: **đạn nguy hiểm màu nóng**, đạn PLAYER màu lạnh. Chưa khẳng định mọi frame đều đạt.

Không sinh ảnh mới hay render trong turn lập bảng. GIF/MP4 trước đây là mockup, không biến thành căn cứ PASS.
