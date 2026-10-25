# DESIGN_QUESTIONS — 48 câu hỏi phải trả lời để thiết kế game mới

> Mục đích: **không phải** liệt kê dữ liệu đã có, mà là **đối chiếu câu hỏi của designer với dữ liệu**.
> Mỗi câu ghi rõ: trạng thái, số cụ thể, và **nếu thiếu thì lấy bằng cách nào**.
>
> Bản `4539709` (nhánh dữ liệu). Mọi số đều kiểm được trên `docs/spec/` hoặc đo lại từ
> `datas/*.json` + `reverse-engineering/raw/typetrees/*.jsonl.gz`.

**Cách chấm:**

| Ký | Nghĩa |
|---|---|
| ✅ | có **số cụ thể**, kiểm chéo được, đủ để chốt thiết kế |
| ⚠ | có **một phần** — có số nhưng thiếu điều kiện hoặc thiếu vế còn lại |
| ❌ | **chưa trả lời được** bằng dữ liệu hiện có |

**Tổng: 48 câu — ✅ 33 · ⚠ 14 · ❌ 1** (cập nhật **25/10 lần 2**: A6/B1 ✅ bind xong · C4 ⚠ có mẫu runtime · E2/E3 ✅ ĐÓNG-BỎ feel; trước đó 29/15/4).
Bốn câu còn ❌: **A5 · A6 · B1 · C4**; ba câu vừa lên ⚠ là **E2 · E3 · A7**, một câu vừa đóng là **D3**.
Cộng **B3** (⚠) ⇒ **5 hàng blocker** trong 9 hàng ban đầu.

> **Nhật ký 24/10 (nhánh Arena):** đóng **D3** bằng `event-receivers.json.gz` (**795/795 có `time`**) sau khi nhánh dữ liệu
> export đúng; nâng **E2** lên ⚠ bằng hằng số trong `Enemy_Display.OnHit`; nâng **A7** lên ⚠ bằng schema `Call_Data`.
> Số khớp claim **R1–R6** + **S2** trong `tools/verify-claims.py`.

---

## A. Vòng lặp và nhịp chơi — 8 câu

| # | Câu hỏi | Trạng thái | Số / nguồn |
|---:|---|---|---|
| A1 | Một wave kéo dài bao lâu? | ⚠ | **median 11,4 s** · mean 16,1 · **max 108 s** · min 2 s (đo mới: spawner dài nhất × `rate`) + **6,4 s bay vào** (`y_spawn` 9,6 ÷ `speed` 1,5) |
| A2 | Cả campaign dài bao lâu? | ⚠ | **≥ 63,5 phút** (cộng spawner dài nhất của 236 wave, **chưa** cộng thời gian giết) |
| A3 | Game có bao nhiêu màn? | ✅ | **299 stage / 2 chapter** — `Stage_Normal` **199** · `Stage_Combat` **49** · `Stage_MiniBoss` **25** · `Stage_Boss` **26** (`Stage_Behaviour.csv`) |
| A4 | Bao lâu gặp boss một lần? | ✅ | **45 wave boss / 282 = 1 mỗi 6,3 wave**; mỗi wave boss = **2 boss + 2 turret + 6,8 `CB-30015`** (`ENCOUNTERS` §3.6) |
| A5 | Một phiên chơi dài bao lâu? | ❌ | cần biết **stage ↔ wave** (A6) và luật continue |
| A6 | Một stage = mấy wave? | ✅ | **bind xong (25/10)** — **11 bảng / 614 mảng** (`DIFFICULTY_MODES` §7): 320×len3 ↔ 3 mode · 118×len2 = stage→boss (giải thích 299 stage vs 281 wave) · 104×len7 ↔ 7 `PlayMode`; `GetListWaves(mapIndex)` đọc mảng len-3; peer ghép entry (`map_table_segments.json` + `maps.json`) |
| A7 | Trên màn hình có bao nhiêu địch cùng lúc? | ⚠ | **CẬP NHẬT 24/10:** số quân mỗi spawner = **độ dài `listPrefabEnemies`** (`number = 0` ở **1.200/1.200** dòng `Call_Data`), dài nhất **30** quân khi `rate = 0`; `rate = 0` nay nghiêng **B** về "spawn cả loạt". Vẫn cần mô phỏng timeline để ra **địch/giây** |
| A8 | Địch bay nhanh cỡ nào? | ✅ | `speed` median **1,5** · bay vào max **30,0** · `BLT` speed median **8,0** max 23 (`BALANCE` §5) |

> **Nhận định (mức B) — A1/A2:** 11,4 s/wave × 236 = 44,8 phút thuần spawn, nhưng cộng 6,4 s bay
> vào mỗi đợt và thời gian người chơi bắn hạ ⇒ **thực tế ước 90–150 phút**. Đây là **ước lượng**,
> không phải số đo: `rate = 0` ở **2.371 spawner** nghĩa là spawn tức thời, nên `t = n × rate`
> **đánh giá thấp** ở các wave đó.
> **Điều kiện lật ngược:** nếu `rate = 0` thực ra là "spawn theo `count` mỗi khung hình" thì A1 phải
> tính lại hoàn toàn.

## B. Độ khó và tiến trình — 10 câu

| # | Câu hỏi | Trạng thái | Số / nguồn |
|---:|---|---|---|
| B1 | HP của enemy thường? | ✅ | **150 cặp id → HP** (`datas/enemy_hp_by_id.json`, claim **WRH2**; `CB-30003` = 650); dict dựng trong `.cctor`, 0 vòng lặp (claim **IAB1**); wave HP = 0 ⇒ lấy theo id — `kHp[mode]` **không tồn tại** |
| B2 | HP của người chơi? | ✅ | **`HPmax = 2500 × (1 + 0,18×TechStatPoints(0) + abi7×GetNumberAbility(7))`** (mức **A**, bản `6109008c`). `str d0,[x8,#0x68]` ghi **cặp** {**0,18** @`0x68`; **2500,0** @`0x6C`}. ✅ **ĐÍNH CHÍNH:** `stepCommon` = **0,18** (0,168 là `stepLevel`). HP gán trong **`Player_Health.Start()`** → `GetStartHp` → `StartHealth@0x0`/`CurrentHealth@0x4`; `ResetStaticVariables()` chỉ **chép** (hồi sinh không tính lại). Giáp **tách riêng** (`Armor@0x20`, hyperbolic) — không cộng HP, nhưng device tăng **HP hiệu dụng** qua `reduceDamageByDevice` + hồi máu. Bảng: 0→**2.500** · 10→7.000 · 30→16.000 · 60→29.500 — `BALANCE` §0.6.13–0.6.15 |
| B3 | Damage người chơi tăng theo cấp thế nào? | ⚠ | `Player_Get_Datas.stepLevel`: **4 ngưỡng cấp 30 / 58 / 118 / 248**, hằng số **0,168 · 1,0 · 1,05 · 1,15** (0,1764 = 0,168×1,05; 0,1932 = 0,168×1,15); `GetMainCannonDamage` = `base × (1 + k)` với k = 0,168 · 0,1764 · 0,1932 |
| B4 | Giết một enemy mất bao lâu (TTK)? | ⚠ | có **DPS median 454,5** (`COMBAT` §4) + **HP boss 6,38 M/instance**; còn thiếu **giá trị `StartHp`** (`BALANCE` §0.6) và **HP enemy runtime** |
| B5 | Độ khó tăng bằng gì? | ✅ | **bằng damage đòn boss, không bằng HP**: `Boss10` 800→1.350 · `Boss6` 600→2.800 · `Boss9` 500→800 (`BOSSES` §8.4.1) |
| B6 | Enemy mới ra mắt theo nhịp nào? | ✅ | **53/70 loại (76%) ra mắt trong 30 wave đầu**; chỉ **3 loại** sau wave 150 |
| B7 | Bao nhiêu loại mới mỗi 20 wave? | ✅ | **51 · 3 · 1 · 0 · 2 · 1 · 9 · 2 · 1 · 0** (bin 0–199) |
| B8 | Số quân tăng dần theo wave? | ⚠ | **4 – 951 quân/wave**, median 130,5; chưa đo **tương quan** với chỉ số wave |
| B9 | Có chế độ khó hơn không? | ✅ | **3 class Director có 2 bản damage** (×1,69 · ×4,67 · ×1,6); 6 class còn lại hai bản giống hệt |
| B10 | Có enemy miễn nhiễm damage? | ✅ | `Enemy_Health.noDamage = True` **241/981 = 24,6%** |

> **Nhận định (mức A) — B6:** đây là **quy luật thiết kế mạnh nhất** tìm được ở lớp nội dung.
> Game **dạy gần hết roster trong 13% đầu campaign** rồi khai thác bằng **tổ hợp**, không bằng
> enemy mới. Clone làm khác đi (rải enemy mới suốt 236 wave) sẽ **không giống nhịp** bản gốc.
>
> **Đã kiểm điều kiện lật ngược:** bỏ `Wave_0000` (42 spawner / 883 quân — thuộc nhóm 3 wave
> nhiều quân nhất) rồi đếm lại: **vẫn 70 loại · 53 ra mắt trong 30 wave đầu · 76% · 3 sau wave 150**
> — **không đổi một số nào**. Kết luận **không** phải artefact của wave đầu.
>
> **Kết luận (mức A):** roster được giới thiệu **dồn ở đầu**, phần còn lại là tổ hợp lại.

## C. Kinh tế và tiến trình — 8 câu

| # | Câu hỏi | Trạng thái | Số / nguồn |
|---:|---|---|---|
| C1 | Có bao nhiêu chỉ số nâng cấp (tech stat)? | ✅ | **60** (`Tech_Datas.NumberTechStats` pool `60.0`) |
| C2 | Giá nâng cấp tăng thế nào? | ⚠ | `Tech_Datas.GetCostUpgrade` pool **2,55** (hệ số nhân); `SetTechStatLevel` **0,4 · 1,48 · 0,57 · −0,1** |
| C3 | Cấu trúc chi phí tech? | ⚠ | `Tech_Datas.NumberTechStats` có **0,2 / −0,2 / −4,0** cạnh 60 — chưa rõ là phụ phí hay bậc VIP |
| C4 | Người chơi kiếm bao nhiêu vàng/giờ? | ⚠ | **mẫu runtime (25/10)**: phiên 23/10 — **276 kill → 540 coin** Stage 1 (≈ 2 coin/kill); công thức `GetBonusCoin` **100,0 · 20,0**; chưa có luật drop đầy đủ |
| C5 | Có bao nhiêu tàu? | ✅ | **25** (id 10001–10024 + 10999), **star 1–5** (`ships.json` 25 · `14-Data_Players.csv` 38 dòng) |
| C6 | Drone / thiết bị bay kèm? | ✅ | `drones.json`; `Droid_Data_Balance.GetBaseDamage` pool **100,0 · 0,6 · 3,0 · 4,0** |
| C7 | Có gói IAP nào? | ✅ | `iap_products.json`; `Tech_Datas.NumberTechStats` gọi `IAP_Manager.GetVipPoint` ⇒ **tech stat mở theo VIP** |
| C8 | Vật phẩm tiêu hao? | ✅ | `items.json` · `Sub_Item.csv` · `Shop_Cell.csv` (192 dòng) |

## D. Nội dung — 8 câu

| # | Câu hỏi | Trạng thái | Số / nguồn |
|---:|---|---|---|
| D1 | Có bao nhiêu loại enemy? | ✅ | **178 prefab có AI** · **109 dùng trong wave** · **22 chưa từng xuất hiện** · **70 loại** xuất hiện trong campaign |
| D2 | Có bao nhiêu boss? | ✅ | **39 prefab** · **45 wave boss** · **90 instance** · **206.167.000 HP** tổng |
| D3 | Boss có mấy pha, thứ tự ra sao? | ⚠ | **HẠ MỨC 25/10 (review R1) — MỘT PHẦN.** Có **mốc trong clip** (mức A), **chưa** có thứ tự/điều kiện chuyển pha (mức C). Cũ:** `event-receivers.json.gz`: **795/795 event có `time`** (793 boss + 2 `CB-30040`) trên **34 prefab · 97 clip · 269 cặp (prefab, clip)**; timeline từng clip ở **`BOSS_ANIM_TIMELINE.md`**. Boss 1 (Spine, không event): **8 tên entry + 5 nhánh** chuyển state. Pha = 3 đòn **lặp** (`Attack1/2/3`, `loop=true`) ngăn bằng clip chuyển `Chuyensangattack2/3` — **không** phải đếm pha theo thời gian |
| D4 | Turret hoạt động thế nào? | ✅ | **44 prefab / 112 component**: **21 spawn qua wave (41)** + **23 đặt sẵn trong `Wave_*` (71)** ⇒ **63,4% turret không do wave sinh** (`BOSSES` §5.1) |
| D5 | Đạn có mấy loại, nhanh cỡ nào? | ✅ | **186 loại** `Bullet_Linearly`; `bltDamage` **28 giá trị**, phổ biến 300 (135 lần); `bltSpeed` median 8,0 |
| D6 | Có bẫy / vùng sát thương môi trường? | ✅ | **16 prefab**: 13 mã `900xx` + **3 `Expl-*` (Poision Zone)** 500 first + 50/s; **không** spawn qua `Call_Data` |
| D7 | Có nội dung bị cắt bỏ? | ✅ | **22 prefab** chưa từng xuất hiện (`W2-30041`…`30057` 17 · `W2-30053 Mau` · `CB-30005` 2 · `CB-30017` · `CB-30019` · `CD-31017` 2) |
| D8 | Wave có mấy loại spawner? | ✅ | `spawn_type`: `point_range` **7.545** · `point` **2.085** · `path` **861** · `boss` **327** · `special` **281** |

## E. Feel và juice — 8 câu

| # | Câu hỏi | Trạng thái | Số / nguồn |
|---:|---|---|---|
| E1 | Có rung màn hình không? | ⚠ | `Enemy_CameraVibrate` **241 instance** — có **cơ chế**, chưa đo **biên độ / thời gian** |
| E2 | Có nháy trắng khi trúng đòn (hit flash)? | ✅ | **ĐÓNG — BỎ (quyết định 25/10)**: game mới **không thêm**. Số đo để tham khảo: `OnHit` alpha **0,5** + tắt sau **0,05 s** (`J9`) |
| E3 | Có khựng hình khi trúng (hit stop)? | ✅ | **ĐÓNG — BỎ (quyết định 25/10)**: game mới **không thêm**. **0** site `set_timeScale` trên **139** file asm (`AF2`) |
| E4 | Âm thanh dài bao nhiêu? | ✅ | **69/69 WAV · 571 s** (`ASSETS`); `shootAudioClipName` gắn từng súng |
| E5 | Nhịp bắn của súng? | ✅ | `timeShot` median **0,10 s**; **397/458 loạt tức thời** · **61/458 băng liên tục** · **29 súng có 3 vòng** (`COMBAT` §3.1) |
| E6 | Tỷ lệ màn hình? | ✅ | canvas **10,8 × 19,2** (9:16) |
| E7 | Vùng chơi hiệu dụng? | ✅ | **20 × 25** unit · bán kính spawn **15** · `y_spawn` **9,6** |
| E8 | Hiệu ứng hạt? | ✅ | **4.845 `ParticleSystem`** (khớp độc lập giữa 2 nhánh) |

## F. Sản xuất — 6 câu

| # | Câu hỏi | Trạng thái | Số / nguồn |
|---:|---|---|---|
| F1 | Cần bao nhiêu art? | ✅ | **163 sprite** · **27 Spine rig / 577 region / 185 animation** (`ASSETS` §2) |
| F2 | Animation dựng lại được chưa? | ⚠ | **791 clip**, tên + thời lượng (**median 1,9 s**, max 75,0) + **793 event**; **0 keyframe** ⇒ thiếu **dáng chuyển động** |
| F3 | UI có bao nhiêu màn? | ✅ | **114 màn** · 6.580 file · 1.404.553 node · 103.655 text-key (`UI`) |
| F4 | Engine / build? | ✅ | Unity **2022.3.62f3** · IL2CPP · `com.Wind.wings.Space.Shooter` **1.3.118** |
| F5 | Đã dịch ngược được bao nhiêu? | ⚠ | class **45/677 = 6,6%** · instance MB **48,9%** · object **9,0%** · lớp enemy/boss **58,9%** · **method body 0,44%** |
| F6 | Clone mất bao lâu? | ⚠ | `AI_FEASIBILITY.md` — tách **khả năng** khỏi **thời gian**; chưa có ước lượng theo người-tháng |

---

## 9 câu blocker — phải trả lời **trước** khi bắt tay thiết kế

Xếp theo **chi phí trả lời thấp → cao**, không theo mức quan trọng.

| Hạng | Câu | Vì sao chặn | Cách trả lời | Chi phí |
|---:|---|---|---|---|
| 1 | ✅ **ĐÓNG — B2 giá trị `StartHp`** = **2500** (bản `6109008c`) | không có HP thì **không có TTK** — nhưng **công thức đã xong** | ✅ **đã giải xong cấu trúc** (`BALANCE` §0.6, đọc lệnh arm64) **và có hằng số 2500**. ⚠ **ĐÍNH CHÍNH:** kết luận cũ *"`.cctor` không gán `StartHp`"* **vô hiệu** — asm export **bị cắt cụt ở 11/12 file**, `Player_Get_Datas..cctor` dừng giữa chừng tại `0x14e5cc4` (`DATA_SYNC` §7.29). Yêu cầu cũ *"dump 200 lệnh sau `0x14e5cc4`"* **không còn** — bản `6109008c` đã đọc trọn | **rất thấp** — đã xong |
| 2 | **A6 — stage ↔ wave** | quyết định **số màn** và **độ dài phiên** | `Stage_Behaviour.textStageIndex` → `Text` component; hoặc đọc thứ tự con của `Parent_Stages` trong `Board_Maps` | **thấp** — đã có `transform-tree` |
| 3 | ⚠ **MỘT PHẦN — E2 có số (0,05 s · 0,5), E3 chưa thấy dấu vết** | quyết định **feel**, thứ người chơi cảm nhận mạnh nhất | đọc `Enemy_Display` field + tìm `timeScale`/`Material.color` trong 305 trace đã có | **thấp** |
| 4 | ⚠ **MỘT PHẦN — D3 thứ tự pha boss** (hạ mức 25/10, review R1): **mốc TRONG clip** đã có (**795/795** event có `time`) nhưng **thứ tự pha, điều kiện vào/thoát, số lần lặp, hành vi callback** vẫn **chưa** | mỗi trận boss là **điểm nhấn** | mốc: `BOSS_ANIM_TIMELINE.md` (269 cặp clip, nhịp 0,17 s) — **không cần decoder**. Còn thiếu: join state-machine (`controller-graphs.json.gz` có 395 state/357 transition, **302** có condition) với nhịp `time`, và hành vi handler (T2) | **thấp** cho thứ tự state, **trung bình** cho hành vi |
| 5 | **B1 — HP enemy runtime** | toàn bộ **231 wave** phụ thuộc công thức này | đọc thân `Enemy_Data_Balance.GetSurvivalScore` (đã có hằng số **6,0 · 3,0 · 1,1 · 0,2 · 0,5 · 500,0 · 23,0 · 40,0**) + tìm chỗ **stage** được truyền vào | **trung bình** |
| 6 | **C4 — vàng/giờ** | quyết định **toàn bộ đường cong meta** | `Enemy_Data_Balance.GetBonusCoin` (**100,0 · 20,0**) × số quân/giờ (tính từ A1) | **trung bình** |
| 7 | **A7 — mật độ địch đồng thời** | quyết định **hiệu năng** và **cảm giác ngộp** | mô phỏng timeline: 11.089 dòng × `rate` × `copies` (= 23.757 lượt) | **trung bình** — làm được bằng script |
| 8 | **A5 — độ dài phiên** | quyết định **retention**, IAP, số mạng | cần **cả** A6 **và** luật continue (chưa có trong dữ liệu) | **cao** — cần chơi thử / đọc `GamePlayManager` |
| 9 | **B3 — đường cong damage player** | quyết định **số enemy chịu được** ở mỗi cấp | đọc rẽ nhánh đầy đủ của `stepLevel` + map 4 ngưỡng 30/58/118/248 vào **loại cấp nào** (player level? tech lab?) | **cao** — cần đọc asm có ngữ cảnh |

> **Nhận định (cập nhật 24/10, mức A):** trong 9 blocker, **2 câu đã ĐÓNG** (1 — `StartHp` = 2500;
> 4 — `time` của 795 event). **Câu 3 nửa đóng** (E2 có số, E3 chưa thấy). **3 câu (2, 5, 6) trả lời
> được bằng dữ liệu đã có** — không cần chạy lại pipeline. Chỉ **2 câu (7, 9)** cần việc mới thật sự
> (mô phỏng timeline địch/giây · đọc asm có ngữ cảnh cho đường cong damage), và **cả hai đều KHÔNG
> chặn L1** vì L1 cho phép tự chọn số.
>
> **Điều kiện lật ngược:** nếu `GetStartHp` trả **hằng số cứng** nằm trong `.rdata` mà `formula_trace`
> không bắt (vì nó chỉ bắt float pool + flow), thì blocker #1 rẻ hơn nữa — chỉ cần đọc thân hàm.

---

## Còn thiếu / phải đoán

1. ~~**Giá trị `StartHp`**~~ — **ĐÃ ĐÓNG = 2500** (hạng 1 ở bảng trên). Nguyên nhân *"không thấy"*
   trước đây là **asm bản `8871068a` bị cắt cụt** (`DATA_SYNC` §7.29); bản `6109008c` đã đọc trọn.
   Câu *"toàn file asm không có lệnh ghi `#0x6c`"* chỉ đúng trên bản cụt — **đừng** dùng lại.
2. ~~**Hệ số HP enemy theo chế độ `kHp[mode]`**~~ — **KHÔNG TỒN TẠI (sửa 25/10)**: chỉ `levelDelta`
   (**thưởng**, `[1, 2, 3.6, 3.6]`) là chỗ duy nhất chế độ nhân; 0/5 hàm `stageLevel` liên quan HP;
   HP = 1 số/prefab; `kCount ≡ 1` ⇒ khác biệt khó/dễ = **composition theo bảng mode**
   (`DIFFICULTY_MODES` §3–5). **HP gốc đã có** (150 cặp, claim **WRH2**) ⇒ TTK tính được đầy đủ.
   Câu *"runtime HP scaled by `Enemy_Data_Balance` and stage"* trong `enemy_hp.json` là **note thừa**,
   chưa thấy cơ chế nào làm điều đó.
3. **stage ↔ wave** — 299 stage và 281 wave chưa khớp; `Stage_Behaviour` không có field `wave`.
4. **Độ dài phiên chơi** — phụ thuộc (2), (3) và luật continue.
5. ~~**Timing của 793 event**~~ — **ĐÃ CÓ**: **795/795** event trong clip có `time` (hạng 4 ở bảng
   trên, `BOSS_ANIM_TIMELINE.md`). Cái còn thiếu là **join** mốc `time` với state-machine và callback,
   không phải decoder `m_StreamedClip`.
6. **Mật độ địch đồng thời** — cần mô phỏng timeline, chưa làm.
7. **Vàng/giờ** — cần drop rate × số quân/giờ.
8. **`stepLevel` map vào cấp nào** — 4 ngưỡng 30/58/118/248 nhưng chưa biết `playerLv` thuộc hệ thống nào.
9. **`rate = 0` ở 2.371 spawner** — "spawn tức thời" hay "mỗi khung hình"? Ảnh hưởng trực tiếp A1/A2.
   *Đếm lại 23/10 (`DESIGN_READINESS.md` §3): bản cũ ghi 2.373 — sai 2. Claim `I3` khoá con số.*
10. **`stageType` 0/1/2/3** — chỉ 100/299 dòng có giá trị, chưa biết map với 4 loại stage nào.

> ~~HP player~~ đã **đóng một phần lớn** ở vòng này: từ *"không có dữ liệu"* thành
> *"có công thức đầy đủ, thiếu 1 hằng số"*.
