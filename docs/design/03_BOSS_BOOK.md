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

## 3.2A Bản nâng cấp bắt buộc — Boss-37001 DREADNOUGHT (thay cho bản tối thiểu ở §3.2)

> USER phán bản boss hiện tại còn đơn giản. Kể từ mục này, Boss-37001
> phải được thiết kế lại thành một **dreadnought nhiều lớp vũ khí**, có
> cơ chế phối hợp đòn và phá hủy bộ phận. §3.2 giữ vai trò tính cách/nền
> tảng; **mọi chi tiết cấu tạo và chiến đấu lấy theo §3.2A khi có khác
> biệt**. Art không được tự giảm số súng/cơ chế cho dễ làm; khó ở đâu
> thì báo đúng món đó.

### A. Cấu tạo thân và sơ đồ hỏa lực (canvas 512×512, boss hướng xuống)

Boss gồm **5 vòng hỏa lực chồng nhau**. Tọa độ dưới đây là *vùng thiết
kế* trên canvas; art tự đo tọa độ pixel chính thức khi đặt linh kiện.

| Vòng | Bộ phận | Vị trí thiết kế | Chuyển động | Vai trò chiến đấu |
|---|---|---|---|---|
| 1 — Pháo hạm chính | **2 BigGun xoay độc lập** (trái/phải) | Hai ổ lớn ở (x≈118, y≈252) và (x≈394, y≈252), đế đường kính 74–88px | Đầu quay ±65°, đế tĩnh | Đòn chủ lực: một ụ ngắm trực tiếp, ụ còn lại bắn chặn hướng di chuyển của người chơi |
| 2 — Pháo giữa | **1 Main Cannon kiêm đầu phát tia** | Tâm (x≈256, y≈356), họng hướng xuống | Thân pháo cố định, đầu phát tia sáng khi sạc | Tia quét; khi không phát tia thì bắn phát đạn nặng đơn lẻ |
| 3 — Pháo phụ | **4 ụ nhỏ**: 2 vai trên (x≈92/420, y≈142) + 2 hông dưới (x≈70/442, y≈330) | Mỗi ụ gồm đế nhỏ + đầu 1–2 nòng | Đầu quay ±45° (vai) / ±35° (hông) | Tạo làn đạn chéo, ép người chơi rời vị trí an toàn; không bao giờ cả 4 cùng bắn tối đa |
| 4 — Vũ khí diện rộng | **2 pod tên lửa tổ ong** (8 ống/pod) | Hông ngoài (x≈42 và x≈470, y≈238), thân pod cố định | Chỉ nắp/đèn khóa chuyển trạng thái | Khóa vị trí 0,8s rồi phóng theo cặp; dùng để trừng việc đứng yên |
| 5 — Phòng thủ gần & lõi | **2 pháo quạt sát lõi** (x≈188/324, y≈292) + **lõi năng lượng** (x≈256, y≈228, Ø≈62px) | Pháo quạt cố định hướng xuống-trái/xuống-phải; lõi nằm dưới vòng giáp mở | Lõi pulse; vòng giáp mở/đóng | Pháo quạt tạo quạt đạn ngắn khi người chơi áp sát; lõi là điểm yếu chỉ lộ rõ khi boss sạc tia, sau khi mất 2 BigGun, hoặc ở Hồi 3 |

**Tổng số điểm hỏa lực: 11** (2 BigGun + 1 Main Cannon + 4 ụ phụ + 2
pod tên lửa + 2 pháo quạt). Đây là mức tối thiểu của bản nâng cấp;
không tính đèn/glow là súng.

Cấu trúc lớp từ dưới lên: thân 3 bậc hư hại → đế tĩnh của mọi ụ → pod
tên lửa → đầu quay BigGun/ụ phụ → vòng giáp lõi → lõi glow → pháo giữa
→ lớp khói/lửa hư hại → FX. Mọi đầu quay phải có đế riêng; mọi họng
súng phải có điểm sinh đạn ghi trong manifest.

### B. Bộ phận phá được và hệ quả (đây là phần làm trận đấu hết đơn điệu)

| Bộ phận | HP bộ phận (đề xuất cân bằng) | Khi bị phá | Hệ quả chiến thuật |
|---|---:|---|---|
| BigGun trái/phải (mỗi ụ) | 18.000 | Đầu pháo nổ, đế cháy còn lại trên thân; đòn tương ứng biến mất | Mất 1 ụ → ụ còn lại vào chế độ **Overdrive**: nhịp nhanh hơn 20% nhưng tỏa thêm ±3°; mất cả 2 → vòng giáp lõi mở lâu hơn sau mỗi đòn |
| Ụ phụ (mỗi ụ) | 7.500 | Tắt ụ đó, để lại đế cháy | Mất 2 ụ phụ cùng phía → phía đó thành **điểm mù**, người chơi có hành lang an toàn tương đối nhưng boss tăng tần suất tên lửa để bù |
| Pod tên lửa (mỗi pod) | 12.000 | Pod cháy, không phóng nữa | Mất 1 pod → tên lửa giảm còn 2 cặp/lượt; mất 2 → boss dùng Main Cannon nhiều hơn |
| Pháo quạt (mỗi khẩu) | 6.000 | Tắt quạt phía đó | Áp sát phía đã phá an toàn hơn |
| Lõi | Không có HP riêng trước khi lộ; khi lộ nhận **×1,5 damage** | Kích hoạt mốc quá tải ở 15% HP thân | Thưởng cho người chơi dám đánh vào lúc boss sạc/ép sân |

Thân boss vẫn 225.000 HP [GỐC]; HP bộ phận là lớp điều tiết nhịp,
không cộng vào HP thân hai lần: đạn trúng bộ phận trừ cả HP bộ phận và
HP thân theo hệ số 1,0; đạn trúng thân thường chỉ trừ HP thân.

### C. Mẫu đạn theo từng vòng hỏa lực

Mọi dòng phải truy nguồn theo §3.5; số chưa có gốc ghi [ĐẠO DIỄN].

| Vũ khí | Mẫu bắn chính thức | Đạn | Damage/viên | Cách đọc né |
|---|---|---|---|---|
| BigGun (mỗi ụ) | G319: 3 băng×1 viên, `timeReload=0,6`, `timeRounds=1,8` [GỐC] | Cầu năng lượng lớn | 330 | Telegraph họng sáng 0,9s; né khỏi đường ngắm |
| BigGun Overdrive | Cùng mẫu, nhịp tổng ×0,8, tỏa ±3° [ĐẠO DIỄN] | Cầu năng lượng | 330 | Đạn nhanh nhịp hơn nhưng kém chính xác |
| Ụ phụ vai | 3 viên/băng, giãn 0,12s; 2 băng; nghỉ 1,4s [ĐẠO DIỄN theo khung GunData] | Viên laser dài | 150 | Hai ụ bắn chéo tạo chữ X có khe giữa |
| Ụ phụ hông | Quạt 5 viên góc −24°→+24°, 1 băng; nghỉ 1,8s [ĐẠO DIỄN] | Đạn tỏa vàng | 150 | Quạt có khe ở hai rìa và giữa các viên |
| Main Cannon (không tia) | 1 phát đơn, sạc 1,0s, nghỉ 2,2s [ĐẠO DIỄN] | Cầu nặng lớn hơn BigGun 1,25× về hình | 330 | Sạc lâu, dễ né, trừng đứng yên giữa sân |
| Tia quét | Sạc 1,2s có đường cảnh báo; quét −25°→+25°/1,9s [Boss Book §3.2] | Tia liên tục | 120/0,5s | Né qua đầu tia hoặc áp sát dưới họng |
| Tên lửa mỗi pod | Khóa 0,8s; 2 cặp/pod/lượt (tổng 4 cặp khi còn 2 pod) [GỐC khung G81 + DESIGN] | Tên lửa có khói | 300/quả | Khóa vị trí đã đứng; di chuyển sau khóa thì trượt |
| Pháo quạt lõi | Quạt 7 viên ngắn, chỉ kích hoạt khi người chơi vào nửa dưới giữa sân; nghỉ 2,6s [ĐẠO DIỄN] | Đạn tỏa nhỏ | 150 | Báo bằng 2 đèn đỏ sát lõi 0,6s |

### D. Bộ máy chiến đấu — đòn phải phối hợp, không bắn rời rạc

Boss chạy bằng **máy trạng thái theo tình huống**, chọn đòn theo vị trí
người chơi, khoảng cách, bộ phận còn sống và %HP. Mỗi "tiết mục" dưới
đây là một chuỗi có mở đầu–cao điểm–hở, không phải một phát bắn:

1. **ÉP SÂN (Hồi 1):** Boss tiến xuống 2s; BigGun trái bắn ngắm trực
   tiếp, BigGun phải bắn vào vị trí người chơi + dự đoán hướng di
   chuyển 0,35s. Ụ vai chỉ bắn khi người chơi nấp ở 1/3 sân trên. Kết
   thúc: boss lui, lõi hở 1,0s.
2. **LƯỚI CHÉO (mở ở Hồi 1 muộn/Hồi 2):** Hai ụ vai bắn chữ X; hai ụ
   hông bắn quạt chậm 0,25s sau đó, tạo làn đạn hai lớp nhưng chừa một
   hành lang an toàn di chuyển theo đường chéo. Đây là đòn dạy người
   chơi đọc nhiều nguồn đạn cùng lúc.
3. **DỒN VÀO TIA (Hồi 2):** Ụ phụ hai bên bắn ép từ ngoài vào giữa
   trong 1,2s → đường cảnh báo tia hiện ở phía sân còn trống → Main
   Cannon quét tia về phía người chơi vừa bị dồn sang. Dừng tia xong
   lõi hở 1,2s — phần thưởng cho người né đúng.
4. **BÃO TÊN LỬA CÓ ĐIỀU KIỆN (Hồi 2):** Chỉ khi người chơi đứng yên
   >0,8s hoặc di chuyển trong vùng nhỏ: reticle khóa; trong lúc tên lửa
   bay, BigGun bắn thưa để buộc người chơi tiếp tục di chuyển.
5. **PHÁ Ụ — ĐỔI TÍNH CÁCH (mọi hồi):** Mỗi lần mất một bộ phận lớn,
   boss dừng 0,4s, điện chớp tại bộ phận đó, rồi đổi vòng đòn ngay
   (không tiếp tục bắn như chưa có gì). Người chơi phải *thấy* chiến
   thuật của mình làm boss yếu đi thật.
6. **VÒNG XOÁY TUYỆT VỌNG (Hồi 3, <30%):** Thân cháy bậc 3; ụ còn sống
   bắn nhanh ×1,3 nhưng tỏa loạn ±6°; cứ 2 vòng đạn thường thì có 1 lần
   tia quét hai chiều; lõi tự mở lâu hơn nhưng boss cũng bắn quạt lõi
   dày hơn. Dưới 15%: lõi quá tải — nếu người chơi phá thêm một bộ
   phận trong cửa sổ này, boss bỏ qua một lượt tia tuyệt vọng (phần
   thưởng kỹ năng).
7. **CHẾT DÂY CHUYỀN (≥3,5s):** Bộ phận đã phá cháy lại trước → ụ còn
   sống nổ → pod phát nổ → điện chạy dọc thân → lõi trắng 0,3s → nổ
   chính → 3–4 mảnh lớn + sóng xung kích dọn đạn → khói tàn 1s. Thứ tự
   có thể thay đổi theo bộ phận nào bị phá trước, nhưng không được rút
   thành một quầng nổ.

### E. Tiêu chuẩn sản xuất cho bản nâng cấp

- Art được tự do thiết kế lại silhouette để chứa đủ 11 điểm hỏa lực;
  không bắt giữ nguyên thân hiện tại nếu thân chật. Boss phải đọc như
  một **pháo đài có hệ thống**, không phải thân cũ dán thêm nòng.
- Mỗi đầu quay vẫn theo chuẩn: đế tĩnh + đầu riêng + pivot do art đo +
  GIF xoay trên thân. Pháo cố định phải ghi rõ "cố định" trong manifest
  để coder không tự xoay.
- Hư hại theo 3 biến thể thân phải vẽ lại **cả các đế cháy** tương ứng
  ở từng bậc: bậc vừa có 2–3 điểm cháy nhỏ; bậc nặng có cháy ở pod/ụ,
  nứt giáp chạy từ lõi ra cánh và khói bám thân.
- GIF toàn trận mới tối thiểu 40 giây, phải trình diễn đủ 7 tiết mục
  ở mục D — thiếu tiết mục nào thì GIF đó chưa được gọi là bản nâng cấp.
- Đạn bổ sung nếu phát sinh họ mới (đạn quạt lõi dùng họ tỏa nhỏ hiện
  có là đủ; không sinh họ mới trừ khi đọc không phân biệt được).

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

## 3.5 Quyết định đạo diễn — trả lời 6 câu chặn của art về Boss-37001

> Art hỏi ngày 29/10 khi gắn chuẩn đạn (báo cáo PR #12 `6499273647`).
> Director trả lời dứt điểm tại đây; các quyết định này có hiệu lực cho
> BOSS_SPEC của Boss-37001 và làm tiền lệ cho boss sau. [GỐC] = dữ liệu
> nguyên mẫu trả lời; [ĐẠO DIỄN] = director quyết, ghi lý do.

1. **Dòng 319 (`MB-39005/BigGunWing1`) là súng gì? [GỐC]** Là súng con
   trong prefab boss: đường dẫn đầy đủ `Boss-37001/Enemy_Ingame/Body/
   MB-39005/Body/BigGunWing1/...` — khớp `COMBAT.md` §5.1 (37001 không có
   súng ở root, súng nằm trong prefab con). `m_Enabled=0` là trạng thái
   serialize mặc định (đạn/súng gốc đều `actived=False`, được code bật
   khi vào trận — `COMBAT.md` §7). Dòng 445 là cấu hình thứ hai trên
   chính module MB-39005 (`countMags=6, timeReload=0,5, timeRounds=2,0`)
   — boss dùng **nhiều cấu hình súng trên cùng module**, bật theo đòn.
2. **`countShots=0, countMags=3` bắn thế nào? [GỐC + ĐẠO DIỄN]**
   `countShots=0` = 1 nòng (mặc định constructor, `COMBAT.md` §3.1);
   `timeShot=0` nên trong 1 băng bắn tức thời. Dòng 319: **1 vòng = 3
   băng × 1 viên = 3 viên**, cách nhau `timeReload=0,6s`; hết vòng nghỉ
   `timeRounds=1,8s`. Neo thời gian của `timeRounds` (từ đầu hay cuối
   vòng) gốc chưa kết luận — **[ĐẠO DIỄN] chốt: tính từ viên cuối của
   vòng trước tới viên đầu của vòng sau** (khoảng nghỉ thuần), để tính
   telegraph/nghỉ giữa đòn không mơ hồ.
3. **`border.w=15` và `pointRadius=0,15` map sang game mới thế nào?
   [GỐC + ĐẠO DIỄN]** Gốc ghi 15 là "bán kính va chạm = 15 unit" trong
   hệ đơn vị nội bộ của gốc (`ENEMY_BEHAVIOUR.md` §1.3), và
   `pointRadius=0,15` là bán kính điểm va chạm của đạn — hai số này
   cùng thang 100:1. **[ĐẠO DIỄN] chốt ánh xạ: hitbox đạn trong game
   mới = 0,15 unit** (thang sân 20×25), hình đạn vẽ lớn hơn hitbox
   (tha thứ ~30% như tập 04 §4.1). Cấm chép số 15 thô vào game mới.
   Collider tia: [ĐẠO DIỄN] bề rộng vùng sát thương = **0,3 unit**
   (đường kính, theo cùng ánh xạ), phần quầng sáng ngoài không tính.
4. **Damage 330 (13,2% HP) hay khung 3–6%? [ĐẠO DIỄN]** Giữ **330 cho
   đòn pháo nặng DOMINANT** — đó là dòng gốc truy được tới Boss-37001,
   và đòn này thưa (3 viên/vòng + nghỉ dài, có telegraph 0,9s) nên tổng
   DPS thấp; nó thuộc nhóm "đòn nặng có báo trước 10–15%/viên". Đòn
   bắn nhanh/tỏa ở ENRAGED–PANIC dùng **damage 150/viên (6%)** — quyết
   theo nguyên tắc gốc "boss mạnh ở mật độ, không ở damage/viên"
   (`COMBAT.md` §5, §7). Tên lửa giữ dòng 81: **300/quả** [GỐC], né
   được nhờ khóa vị trí. Tập 04 §4.1 đã sửa lại khung cho khớp quyết
   định này.
5. **Nghỉ của Boss Book (1,6s/0,8s) và `timeRounds` (1,8s) cộng hay
   thay? [ĐẠO DIỄN]** **Không cộng.** Trong một đòn: nhịp do thông số
   súng quyết (gồm cả `timeRounds`). Giữa hai đòn khác nhau: áp dụng
   khoảng nghỉ của hồi trong Boss Book tính từ viên cuối của đòn trước.
   Nếu đòn kế tiếp dùng lại cùng một súng, `timeRounds` của súng là
   khoảng nghỉ — không cộng thêm nghỉ của sách.
6. **Chưa có join chứng minh 80027 = tên lửa, 80059 = cầu? [ĐẠO DIỄN]**
   Không cần join: bản làm mới ở mức L1 — **hình là vẽ mới của chúng
   ta**, hai dòng đó chỉ là *tham chiếu thông số theo hành vi* (dòng 81
   chậm 4,8 → họ tên lửa; dòng 319 nhanh 16 → họ cầu/laser). Trong
   BOSS_SPEC phải ghi "hình mới thuộc họ X, thông số tham chiếu dòng Y",
   cấm ghi là đạn/hình gốc.
7. **Chuẩn hư hại và chuẩn lắp linh kiện: tổng thể, không từng pixel
   [ĐẠO DIỄN — chốt theo lệnh USER 29/10]** Yêu cầu cũ "overlay hư hại
   khớp chi tiết giáp từng pixel" bị hủy vì không khả thi với ảnh sinh
   độc lập và không phải thứ người chơi nhìn thấy. Chuẩn mới: hư hại
   được giao dưới dạng **3 biến thể thân theo bậc** (nguyên vẹn / hư
   hại vừa / hư hại nặng, chuyển bậc theo ngưỡng HP ở §3.2) hoặc lớp
   phủ — art tự chọn kỹ thuật theo §6.4.2 — và chỉ chấm ở **tổng thể**:
   ở kích thước hiển thị thật và trong chuyển động, người xem thấy rõ
   boss xuống sức theo bậc, không lộ mép ghép/ghosting/thân biến mất
   đột ngột. Tương tự, lắp pháo/pod chấm ở tổng thể (đế ngồi ổn định,
   không lộ lỗ khi xoay ở cỡ game), không đòi đăng ký từng pixel.
   Bảng chất lượng của art phải tách 2 tầng: **[ART] tự đóng được**
   (hình/lớp/pivot/GIF) và **[ENGINE] chờ coder QA** (collider, khe
   né, muzzle trong runtime) — tầng ENGINE không chặn art hoàn thành
   phần của mình.

## 3.4 Luật sản xuất boss (không thương lượng)

- Hồ sơ 9 mục duyệt xong **trước** khi generate ảnh đầu tiên.
- Linh kiện sinh theo bộ (thân trần trước), pivot do art đo + GIF xoay
  360° chứng minh; đạn/FX của boss sinh cùng lô với thân.
- Art dựng GIF hoạt cảnh toàn trận theo kịch bản 3 hồi → USER duyệt →
  coder cài thành **hệ thống theo tình huống** (%HP/vị trí), cấm cài theo
  mốc giây và cấm nhúng GIF. Nghiệm thu: 2 clip chơi khác nhau phải cho
  2 trận khác nhau nhưng cùng "tính cách".
