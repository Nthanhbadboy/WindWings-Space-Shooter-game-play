# BALANCE — số liệu WindWings: Space Shooter (bản spec hoá)

> Sinh từ dữ liệu **đã bóc** trong repo. Mỗi bảng ghi nguồn. Suy đoán ghi `> Giả định:`.
> Không có giá trị nào được nội suy thành số cụ thể nếu APK không có — những chỗ đó ghi
> **"không xác định được từ APK"** và được liệt kê lại ở §6 để phần 2 đi tìm.
>
> **Cập nhật vòng 2:** nguồn số nay là `reverse-engineering/scriptableobjects/*.csv` +
> `docs/apk-analysis/*.csv` + `datas/*.json`. Số liệu combat/wave/economy chi tiết nằm ở
> `COMBAT.md`, `ENCOUNTERS.md`, `ECONOMY.md` (cùng thư mục) — **không lặp lại ở đây**.

---

## 0. TL;DR cho designer

| Câu hỏi | Trả lời ngắn | Nguồn |
|---|---|---|
| Boss khó nhất (theo HP phải bắn hết) | `Boss-39006`: **11,235,000** tổng (16 part) | `15-enemy-hp.csv` |
| Boss dễ nhất | `Boss-39001`: 270.000 · `Boss-37004`: 272.000 | `15-enemy-hp.csv` |
| Boss chương 1 khác chương 2 thế nào | Median tổng HP **4,2 M → 6,0 M**; boss 3 phase **1 → 7** | `15-enemy-hp.csv` §2.3 |
| HP enemy thường | **68 / 70 prefab = 0**; 2 prefab = 20.000 — prefab **không lưu** HP enemy thường | `Enemy_Datas.csv` (981 dòng) |
| Tàu mạnh nhất theo "sao" | `10024 Elves` 5.11 sao; yếu nhất `10001 Bluesky` 2.0 | `14-ships.csv` |
| Damage vũ khí | **458 giá trị** (457 > 0), 40–1.200, median 400 — nhưng **toàn bộ là súng địch** | `Gun_Attack.csv` → `COMBAT.md` |
| DPS lý thuyết của địch | 7,8 – 3.333 (median 454), tính từ burst pattern | `Gun_Attack.csv` → `COMBAT.md` §4 |
| Sát thương chạm thân boss | 251 hitbox: `dmgFirst` 200–10.000 (median 500) + 14 sentinel, `dmgPerSec` 5–1.000 | `Boss_BodyPhysics.csv` |
| Số wave / spawner | **282 wave** (236 campaign + 45 boss), **48 archetype**, 10.776 placement sau dedup, 250 map | `waves.json` → `ENCOUNTERS.md` §1–2 |
| Giá coin/gem/IAP | **0 cột giá** trong 91 CSV — **không thấy** trong asset (phạm vi: chỉ CSV) | `ECONOMY.md` §0 |
| Phần thưởng trong hộp | **0 giá trị** — `Box_Rewards.id = 0` cho 800/800 dòng | `Box_Rewards.csv` |
| Damage của **player** | **0 giá trị** — `forceType = Enemy` 458/458 | `Gun_Attack.csv` |
| Có thể dựng lại balance đầy đủ? | Không. Nhưng đã có **HP + damage địch + nhịp wave** — đủ để suy đường cong | §7 |

---

## 1. Phương pháp & nguồn

| Bảng | File | Trạng thái |
|---|---|---|
| HP **800** enemy/boss | `15-enemy-hp.csv` = `Enemy_Datas.csv` (800 dòng, 394 có HP > 0) | ✅ có số |
| Cờ enemy | `docs/apk-analysis/Enemy_Datas.csv` | ✅ có số |
| Roster tàu/drone/boss/item | `14-ships.csv`, `14-drones.csv`, `14-bosses.csv`, `14-items.csv` | ✅ có số |
| Tên tàu/drone/boss/talent/ability | `12-localization.csv` | ✅ có text |
| Tech ability / shop pack / GP / rank | `Tech_Ability_Data.csv`, `DataShopPack.csv`, `GP_Datas.csv`, `RankManager.csv` | ⚠ chỉ có sprite/id, không có số balance |
| **Damage vũ khí địch** | `reverse-engineering/scriptableobjects/Gun_Attack.csv` (458 dòng) | ✅ có số → `COMBAT.md` |
| **Burst pattern** | `Gun_Attack.csv` `allGunDatas[0..2].{countShots,timeShot,timeReload,timeRounds,countMags}` | ✅ có số → `COMBAT.md` §3 |
| Đạn (hitbox, xuyên khiên) | `Bullet_Linearly.csv` (186 dòng) | ✅ có số → `COMBAT.md` §7 |
| Damage va chạm boss | `Boss_BodyPhysics.csv` (`dmgFirst`, `dmgPerSec`) | ✅ có số → `COMBAT.md` §6.3 |
| Armor / `noDamage` | `Enemy_Health.csv` (800 dòng) | ✅ 189 / 800 `True` |
| **Wave / spawner / map** | `datas/waves.json`, `MapController.csv`, `Stage_Behaviour.csv` | ✅ có số → `ENCOUNTERS.md` |
| **Giá & phần thưởng cụ thể** | `Box_Rewards.csv`, `Shop_Cell.csv`, `DataShopPack.csv`, `13-iap-products.csv` | ❌ **thật sự không có số** → `ECONOMY.md` §0 |
| **Tỉ lệ rơi item** | `Sub_Item.csv` + `Item_Movement.csv` (702 lượt) | ✅ 676 coin / 26 item → `ECONOMY.md` §1.1 |
| Damage của **player** | `Player_Get_Datas.StartMainCannonDamages[]` (không serialize) | ❌ trong `libil2cpp.so` |

> Bảng trên là **kết quả kiểm lại toàn bộ 91 CSV** ở `reverse-engineering/scriptableobjects/`
> bằng cách lọc cột số và đếm giá trị phân biệt. Chi tiết phép kiểm: `ECONOMY.md` §8.

**Quy ước dedup HP:** một enemy có thể xuất hiện nhiều lần trong cùng file vì cùng prefab được
đặt trong: (a) prefab gốc, (b) scene `Board_FightBoss` (tab preview), (c) scene map/scrollview.
Ta gom theo **root prefab** + **đường dẫn component sau root**, lấy `max(HP)` cho mỗi cặp
`(root, component)`. Cặp nào chỉ khác nhau phần "Tab (n)/…/Parent_View/…" bị coi là **bản copy UI**.

---

## 2. HP enemy / boss

> **Cập nhật vòng 2:** nguồn `15-enemy-hp.csv` nay có **800 dòng** (bản vòng 1 dùng 981 dòng
> từ lần bóc trước). Toàn bộ §2 đã tính lại từ file 800 dòng — **các số dưới đây thay thế
> hoàn toàn số vòng 1**, kể cả bảng 39 prefab.

### 2.1 Tổng quan

| Chỉ số | Giá trị | Nguồn |
|---|---:|---|
| Số instance `Enemy_Datas` | **800** dòng (bản cũ) · **981** dòng (vòng 3) = **690** path GO | `Enemy_Datas.csv` |
| **Số loại enemy (prefab root)** | **92** = 52 thường + 39 boss + 1 mini-boss | `ENCOUNTERS.md` §2.5 |

> ⚠ **Số dòng HP phụ thuộc lần chạy pipeline:** 800 (bản cũ) → **981** (vòng 3).
> Root `Boss-` vẫn **39**. Nhưng **tổng HP theo boss lệch 11–71%** giữa 2 lần — xem `DATA_SYNC.md` §3.1.
> Đừng dùng "tổng HP" để so sánh khi chưa chốt **đơn vị đếm** (root hay bộ phận).
| Số instance có `StartHealthPoint > 0` | **394** | `15-enemy-hp.csv` |
| Số instance HP = 0 (slot chưa dùng / part trang trí) | **406 (50,8%)** | `15-enemy-hp.csv` |
| HP lớn nhất | 10.000.000 (`CB(TEST)` — object test, **loại khỏi balance**) | `15-enemy-hp.csv` |
| HP lớn nhất hợp lệ | **11.235.000** tổng prefab (`Boss-39006`) | `15-enemy-hp.csv` |
| HP 1 component lớn nhất | 5.000.000 (`Boss-37018`, `Boss-37019`) | `15-enemy-hp.csv` |
| Median HP (chỉ dòng > 0) | **600.000** (sau khi gộp trùng: 353 đơn vị, vẫn 600.000) | `15-enemy-hp.csv` |
| Số prefab boss có HP | **39** (ch1 18 + ch2 21) | `15-enemy-hp.csv` |
| Số dòng liên quan boss | 231 / 800 | `15-enemy-hp.csv` |

> **⚠ Trùng lặp:** 800 dòng nhưng **690 đường dẫn GameObject** khác nhau (110 dòng lặp, cùng
> nguyên nhân prefab + instance scene — `ENCOUNTERS.md` §1.3). Sau khi gộp `max` theo đường dẫn:
> **353 đơn vị có HP > 0**, median vẫn **600.000**, max vẫn 10.000.000.
> Bảng 39 prefab boss ở §2.2 đã gộp trùng nên **không bị ảnh hưởng**.

Phân bố HP (394 instance > 0, raw):

| Khoảng HP | Số instance |
|---|---:|
| < 100 K | 52 |
| 100 K – 500 K | 107 |
| 500 K – 1 M | **122** |
| 1 M – 2 M | 44 |
| 2 M – 3 M | 35 |
| ≥ 3 M | **34** |

> Đọc bảng này: trong **34 dòng ≥ 3 M**, **21 dòng có root là `Boss-xxxxx`**, 13 dòng còn lại
> là **bản copy trong scene preview** (`Board_FightBoss/Parent/Tab (5)/...`, `Tab (7)/...`,
> `ObjectMove/...`) hoặc `CB(TEST)` 10 M. ⇒ toàn bộ ≥ 3 M đều là **boss hoặc bản sao boss**.
> Dải 500 K–1 M (122) là enemy thường + part phụ.
> Nhịp HP là bậc 2: enemy ~0,5–0,6 M, boss ~4–11 M tổng.

### 2.2 Bảng 39 prefab boss (dedup, tính lại từ 800 dòng)

**tail** = số component HP duy nhất của prefab; **phase HP** = component đặt tên `HP/HP1/HP2/HP3`;
**tổng HP** = tổng mọi component (thân + part phụ) — "damage phải bỏ ra để giết sạch".

| prefab | wave | tail | phase HP | tổng HP (dedup) |
|---|---:|---:|---|---:|
| `Boss-37001` | 7001 | 3 | – | 1.225.000 |
| `Boss-37002` | 7002 | 5 | – | 1.320.000 |
| `Boss-37003` | 7003 | 5 | – | 3.000.000 |
| `Boss-37004` | 7004 | 5 | – | 272.000 |
| `Boss-37005` | 7005 | 2 | – | 4.700.000 |
| `Boss-37006` | 7006 | 17 | – | 4.100.000 |
| `Boss-37008` | 7008 | 2 | – | 1.300.000 |
| `Boss-37009` | 7009 | 1 | – | **0** ⚠ |
| `Boss-37010` | 7010 | 1 | – | 4.500.000 |
| `Boss-37011` | 7011 | 1 | – | 4.000.000 |
| `Boss-37012` | 7012 | 1 | – | **0** ⚠ |
| `Boss-37013` | 7013 | 2 | – | 4.300.000 |
| `Boss-37014` | 7014 | 3 | HP1=2.400.000 · HP2=3.100.000 | 5.500.000 |
| `Boss-37015` | 7015 | 1 | – | 4.350.000 |
| `Boss-37016` | 7016 | 2 | – | 5.580.000 |
| `Boss-37017` | 7017 | 1 | – | 4.300.000 |
| `Boss-37018` | 7018 | 1 | – | 5.000.000 |
| `Boss-37019` | 7019 | 2 | – | 5.000.000 |
| `Boss-39001` | 9001 | 4 | – | 270.000 |
| `Boss-39002` | 9002 | 4 | HP1=680.000 · HP2=550.000 · HP3=450.000 | 1.680.000 |
| `Boss-39003` | 9003 | 1 | – | **0** ⚠ |
| `Boss-39004` | 9004 | 6 | – | 3.100.000 |
| `Boss-39005` | 9005 | 8 | – | 3.320.000 |
| `Boss-39006` | 9006 | 16 | – | **11.235.000** |
| `Boss-39007` | 9007 | 1 | – | **0** ⚠ |
| `Boss-39008` | 9008 | 1 | – | **0** ⚠ |
| `Boss-39009` | 9009 | 4 | HP3=2.500.000 | 4.500.000 |
| `Boss-39010` | 9010 | 14 | – | 6.600.000 |
| `Boss-39011` | 9011 | 6 | HP1=1.800.000 · HP2=2.900.000 · HP3=2.500.000 | 7.200.000 |
| `Boss-39012` | 9012 | 4 | HP1=1.800.000 · HP2=2.600.000 · HP3=2.800.000 | 8.400.000 |
| `Boss-39013` | 9013 | 4 | HP1=2.200.000 · HP2=2.500.000 · HP3=3.000.000 | 7.700.000 |
| `Boss-39014` | 9014 | 4 | HP1=2.350.000 · HP2=2.680.000 · HP3=3.000.000 | 8.030.000 |
| `Boss-39015` | 9015 | 3 | HP1=2.500.000 · HP2=3.000.000 | 5.500.000 |
| `Boss-39016` | 9016 | 2 | HP=600.000 | 600.000 |
| `Boss-39017` | 9017 | 13 | HP2=2.800.000 · HP3=3.200.000 | 7.900.000 |
| `Boss-39018` | 9018 | 3 | HP2=2.800.000 · HP3=3.200.000 | 6.000.000 |
| `Boss-39019` | 9019 | 3 | HP1=2.200.000 · HP2=2.800.000 · HP3=3.200.000 | 8.200.000 |
| `Boss-39020` | 9020 | 3 | HP2=2.800.000 · HP3=3.200.000 | 6.000.000 |
| `Boss-39021` | 9021 | 4 | HP1=2.200.000 · HP2=2.800.000 · HP3=3.200.000 | 8.200.000 |

Nguồn: `15-enemy-hp.csv`, gom theo `(root prefab, đường dẫn component)`, lấy `max` mỗi cặp.

**Ghi chú bảng:**
- ⚠ **5 prefab có tổng HP = 0**: `37009`, `37012`, `39003`, `39007`, `39008` → prefab chỉ là
  "vỏ", HP set lúc chạy. **Không dùng 5 dòng này để cân bằng.** (Vòng 1 ghi 3 — sai vì nguồn cũ.)
- `Boss-39006` là **trùm HP** (11,2 M, 16 part) đồng thời có **24 súng** (`COMBAT.md` §5)
  → boss "dày" nhất game cả về máu lẫn hoả lực.
- `Boss-39015` chỉ còn **2 phase** ở nguồn mới (vòng 1 ghi 3) — phase 3 nằm ở prefab khác.

### 2.3 So sánh 2 chương

| Chỉ số | Chapter 1 (`Boss-37xxx`) | Chapter 2 (`Boss-39xxx`) |
|---|---:|---:|
| Số prefab | 18 | 21 |
| Prefab có **3 phase** | 1 (`37014` có 2) | **7** (`39011`–`39014`, `39019`, `39021` + `39009`) |
| Prefab 0 phase (1 thanh máu) | 16 | 12 |
| Median tổng HP | **4.200.000** | **6.000.000** |
| Tổng HP cả chương | 58.447.000 | 104.435.000 |
| Cao nhất | `37016` 5.580.000 | `39006` 11.235.000 |
| Thấp nhất (khác 0) | `37004` 272.000 | `39001` 270.000 |

Phân bố số phase toàn bộ 39 prefab: **0 phase = 25**, 1 phase = 2, 2 phase = 5, **3 phase = 7**.

> **Đọc ra:** chương 2 tăng **median HP 1,43×** (4,2 M → 6,0 M) và **số boss 3 phase gấp 7**.
> Khác kết luận vòng 1 (cho rằng HP thân không tăng) — số mới cho thấy **cả HP lẫn phase đều tăng**,
> nhưng phase tăng mạnh hơn (7×). Vẫn giữ nguyên bài học: **phase là đòn bẩy độ khó chính**.

### 2.4 Enemy thường

> **Sửa lại ở bản vòng 3.** Mục này trước đây dựa trên **800 dòng** (bản cũ) và kết luận
> "median HP enemy thường = 500.000". **Sai** — con số đó là median của một mẫu **lẫn boss + bộ phận
> boss + object UI**. Số dưới đây lấy từ bản **981 dòng**.

| Chỉ số | Giá trị | Nguồn |
|---|---:|---|
| Tổng dòng HP | **981** | `15-enemy-hp.csv` |
| Thuộc 39 root `Boss-*` | **206** (167 dòng HP > 0) | `15-enemy-hp.csv` |
| Thuộc `Wave_*` | **260** dòng / 34 prefab — **HP > 0: 0** | `15-enemy-hp.csv` |
| Tổng dòng HP > 0 | **467** | `15-enemy-hp.csv` |
| Median 467 dòng > 0 | **600.000** — ⚠ **không phải** HP enemy thường | `15-enemy-hp.csv` |
| Prefab enemy thường (70) **có** HP > 0 | **2 / 70** = 20.000 mỗi cái (`W1-30031`, `W2-30037`) | `15-enemy-hp.csv` |
| 68 prefab enemy thường còn lại | **HP = 0** | `15-enemy-hp.csv` |
| Max không phải boss | 10.000.000 (`CB(TEST)` — object test, bỏ) | `15-enemy-hp.csv` |

**Kết luận đúng:** **không có HP của enemy thường trong prefab.** 260 dòng thuộc `Wave_*` đều bằng 0,
và `Enemy_Datas.StartHealthPoint` (trùng khít `start_hp`) cũng 0 ở đúng 260 dòng đó.
HP trong prefab **chỉ dành cho boss**.

Cờ hành vi (nguồn: `Enemy_Datas.csv`, **981 dòng** — bản vòng 3):

| Cờ | True | False | Ý nghĩa |
|---|---:|---:|---|
| `IsCaAttack` | **524** | 457 | có thể tấn công (53,4%) |
| `IsBringItems` | 0 | **981** | không enemy nào mang item sẵn — item do controller drop |
| `IsInvisible` | 0 | **981** | không có enemy invisible |
| `IsAlive` | 2 | 979 | giá trị editor |
| `CurrentHealthPoint` | 0 | 981 | chỉ là giá trị editor |
| `StartHpPoint` | 0 | 981 | cột thứ hai, không dùng |

> **Đường lấy HP enemy thường (mức B, chưa chạy):** `Enemy_Health` không có field HP, nên công thức
> nằm trong **thân hàm** `Init`/`SetUp` của nó — cần **method body IL2CPP**, hiện chưa có
> (`AI_FEASIBILITY.md` §1). Ứng viên khác: `MapController` (396) có `IndexWaveArena`, `Stage_Behaviour`
> (299) có `stageType` — nếu một trong hai có trường scale thì HP = base × scale.
> Xem `AI_FEASIBILITY.md` §1.7.

## 3. Roster

### 3.1 25 tàu (`Data_Players.allPlayers`)

| id | Tên (EN) | Star | Sprite pathID | Actived | Bộ field đạn |
|---:|---|---:|---:|---|---|
| 10001 | Bluesky | 2.00 | 3581 | True | `p1_*` |
| 10002 | Phoenix | 2.50 | 3224 | True | `p2_*` |
| 10003 | Trooper | 2.51 | 3527 | True | `p3_*` |
| 10004 | Lightning | 3.50 | 3025 | True | `p4_*` |
| 10005 | Genesis | 5.05 | 3285 | True | `p5_*` |
| 10006 | RedStorm | 4.00 | 2659 | True | `p6_*` |
| 10007 | Green Cyborg | 5.03 | 3424 | True | `p7_*` |
| 10008 | Tornado | 3.00 | 3828 | True | **(class riêng)** |
| 10009 | Scientist | 3.00 | 2964 | True | `p9_*` |
| 10010 | Vanguard | 5.04 | 3184 | True | **(class riêng)** |
| 10011 | Icarus | 4.00 | 3846 | True | `p11_*` |
| 10012 | Justice Destiny | 4.55 | 3455 | True | **(class riêng)** |
| 10013 | Falcon Force | 3.50 | 2807 | True | `p13_*` |
| 10014 | Predator | 4.50 | 3423 | True | `p14_*` |
| 10015 | Molten Core | 5.00 | 3167 | True | **(class riêng)** |
| 10016 | The Omega | 5.07 | 3540 | True | `p16_*` |
| 10017 | Soldier 93 | 4.53 | 2826 | True | `p17_*` |
| 10018 | Ice Knight | 3.00 | 3721 | True | `p18_*` |
| 10019 | Supersonic | 5.08 | 3132 | True | `p19_*` |
| 10020 | Hawk Saw | 4.54 | 3160 | True | `p20_*` |
| 10021 | The Horizon | 5.09 | 2374 | True | `p21_*` |
| 10022 | Hydra | 4.56 | 3372 | True | `p22_*` |
| 10023 | Dracula | 5.07 | 2602 | True | `p23_*` |
| 10024 | Elves | 5.11 | 2896 | True | `p24_*` |
| 10999 | **không có tên** (chưa mở) | 1.00 | 3101 | False | — |

Nguồn: `14-ships.csv` (id/Star/Sprite/Actived) + `12-localization.csv` (`txt_plane_name_<id>`).

| Thống kê star | Giá trị |
|---|---|
| Min | 2.00 (`10001`) |
| Median | 4.54 |
| Max | 5.11 (`10024`) |
| Số tàu ≥ 5.0 sao | 10/24 |
| Số tàu < 3.0 sao | 3/24 |

> **Star là "hệ số sức mạnh" chứ không phải rarity thuần:** 10003 có `2.509999990463257`
> (float nhiễu) chứng tỏ star được tính bằng công thức cộng dồn chứ không phải hằng số thiết kế.
> Cùng hiện tượng ở `20008 = 5.019999980926514`. ⇒ Star nên là **biến derived**, không hard-code.

Mô tả cơ chế từng tàu (dùng để viết kit): `txt_plane_desc_10001..10024`, ví dụ:
`10005 "Laser destroys everything"`, `10006 "Destroy enemy bullets when super power is active"`,
`10009 "Create a ship"`, `10010 "Super bomb"`, `10021 "Bend space to eliminate enemy bullets, fire missiles"` (nguồn: `12-localization.csv`).

### 3.2 13 drone

| id | Tên (EN) | Star | Sprite | Actived | Bộ field đạn |
|---:|---|---:|---:|---|---|
| 20001 | Machinegun | 1.00 | 3657 | True | `d1_*` |
| 20002 | Protector | 1.50 | 3866 | True | `d2_*` |
| 20003 | Rumble | 2.50 | 2445 | True | `d3_*` |
| 20004 | Railgun | 3.00 | 3091 | True | `d4_*` |
| 20005 | Nostromo | 3.50 | 2614 | True | `d5_*` |
| 20006 | Split | 3.50 | 2889 | True | `d6_*` |
| 20007 | Sunshine | 4.00 | 2877 | True | **(class riêng)** |
| 20008 | Nova | 5.02 | 3474 | True | `d8_*` |
| 20009 | Lin Sabiu | 5.00 | 2635 | True | **(class riêng)** |
| 20010 | Bumblebee | 4.55 | 3190 | True | `d10_*` |
| 20011 | Swarm | 3.01 | 2321 | True | `d11_*` |
| 20012 | Spitfire | 5.01 | 2507 | True | `d12_*` |
| 20013 | **không có tên** (chưa mở) | 1.00 | 3816 | False | — |

Nguồn: `14-drones.csv` + `txt_drone_name_<id>`. Median star 3.5. Skill name: `txt_droneability_name_20001..20012` (Gunery, Energy shield, Missiles, Laser, Carl Gustaf, Split, Sunshine, Nova, Lin Sabiu, Bumblebee, Swarm, Spitfire).

### 3.3 46 wave-boss (`Data_Boss.allBosses`)

| idWave | Sprite | Ghi chú |
|---:|---:|---|
| 7001 | 3869 | |
| 7002 | 2341 | |
| 7003 | 3323 | |
| 7004 | 2994 | |
| 7005 | 3928 | sprite dùng lại ở 7008 |
| 7006 | 3022 | |
| 7007 | 0 | **không có sprite** → wave đặc biệt |
| 7008 | 3928 | trùng sprite 7005 |
| 7009 | 3625 | |
| 7010 | 3520 | |
| 7011 | 2392 | |
| 7012 | 2720 | |
| 7013 | 2551 | |
| 7014 | 3097 | |
| 7015 | 3629 | |
| 7016 | 3254 | |
| 7017 | 3704 | |
| 7018 | 3369 | |
| 7019 | 2501 | |
| 7020 | 3351 | |
| 7021 | 2598 | |
| 7022 | 3441 | |
| 9001 | 0 | **không có sprite** |
| 9002 | 2680 | |
| 9003 | 3024 | |
| 9004 | 2707 | |
| 9005 | 2815 | |
| 9006 | 2848 | |
| 9007 | 2628 | |
| 9008 | 3299 | |
| 9009 | 3316 | |
| 9010 | 2646 | |
| 9011 | 2722 | |
| 9012 | 3600 | |
| 9013 | 2760 | |
| 9014 | 3090 | |
| 9015 | 0 | **không có sprite** |
| 9016 | 0 | **không có sprite** |
| 9017 | 3685 | |
| 9018 | 3282 | |
| 9019 | 2879 | |
| 9020 | 3330 | |
| 9021 | 2502 | |
| 9022 | 3652 | |
| 9023 | 3397 | |
| 9024 | 2360 | |

Nguồn: `14-bosses.csv`. 46 dòng = 22 (ch1) + 24 (ch2). 4 dòng sprite = 0: 7007, 9001, 9015, 9016.

**Đối chiếu wave ↔ prefab HP** (`> Giả định:` số `37xxx`/`39xxx` khớp 1:1 với `70xx`/`90xx`):

| Wave có Data_Boss | Có prefab HP? | Ghi chú |
|---|---|---|
| 7001–7019 (trừ 7007) | ✅ 18 prefab | |
| 7007 | ❌ | sprite = 0 → wave không boss |
| 7020, 7021, 7022 | ❌ | không có prefab `37xxx` tương ứng → tái dùng prefab trước |
| 9001 | ❌ | sprite = 0 |
| 9002–9021 (trừ 9015, 9016) | ✅ 21 prefab | |
| 9015, 9016 | ❌ | sprite = 0 |
| 9022, 9023, 9024 | ❌ | tái dùng prefab trước |

⇒ **46 wave-boss nhưng chỉ 39 prefab boss thân** — 7 wave tái dùng boss cũ hoặc là wave đặc biệt.
Điều này giải thích vì sao "20 boss chính" nhưng "46 wave": mỗi boss xuất hiện 2–3 lần với biến thể.

### 3.4 6 item rơi

| index | icon pathID | 5 sprite stat (pathID) | Vai trò |
|---:|---:|---|---|
| 1 | 2376 | 2854, 3416, 3916, 2832, 3209 | Power (damage) |
| 2 | 3944 | 2809, 3317, 2672, 2915, 2353 | Overdrive / super power |
| 3 | 3427 | 2861, 3919, 2823, 3405, 3805 | HP |
| 101 | 3442 | 3589, 2949, 3415, 2983, 2903 | Droid 1 (giáp + hút coin) |
| 102 | 2920 | 3589, 2949, 3315, 3310, 3448 | Droid 2 (cận chiến) |
| 103 | 2651 | 3589, 2949, 3364, 3487, 3385 | Droid 3 (sniper) |

Nguồn: `14-items.csv`. Ghi chú: 101/102/103 **dùng chung 2 sprite đầu** (3589, 2949) → 3 droid
chia sẻ icon gốc, khác nhau ở 3 sprite nâng cấp. Đây là tiết kiệm atlas có chủ đích.

---

## 4. Bảng ScriptableObject — cái nào dùng được?

### 4.1 `Tech_Ability_Data` — 6 instance ✅ dùng được một phần

6 asset: `TechAbility1..6`, mỗi asset có `listDatas[5]` với `{Level, TypeIndex, Sprite}`.

Mỗi ô ghi `Level·TypeIndex·Sprite pathID`.

| asset | entry 0 | entry 1 | entry 2 | entry 3 | entry 4 |
|---|---|---|---|---|---|
| `TechAbility1` | 1·2·3893 | 2·1·2700 | 3·1·2700 | 2·2·3893 | 4·1·2700 |
| `TechAbility2` | 1·0·2543 | 2·0·2543 | 1·0·2463 | 3·0·2543 | 2·0·2463 |
| `TechAbility3` | 1·0·2601 | 2·0·2601 | 1·0·2959 | 3·0·2601 | 2·0·2959 |
| `TechAbility4` | 1·1·3298 | 2·1·3298 | 1·2·2493 | 3·1·3298 | 2·2·2493 |
| `TechAbility5` | 1·0·3827 | 1·0·3308 | 2·0·3827 | 3·0·3827 | 2·0·3308 |
| `TechAbility6` | 1·0·3852 | 2·0·2930 | 1·0·3852 | 3·0·2930 | 4·0·3852 |

Nguồn: `Tech_Ability_Data.csv` (5 entry × 6 asset = 30 mốc).

**Kết luận:** dùng được để biết **số ability mỗi stat (5)** và **icon theo (level, type)**, nhưng
**không có % hiệu ứng**. Hiệu ứng nằm ở `Player_Get_Datas.abi*` và text `txt_techstatability_desc_<stat*100+level>`
(ví dụ `txt_techstatability_desc_300` = "If health points are below 30%, power increases by 10%").
⇒ Spec hoá ability nên **lấy text làm nguồn số**, không lấy bảng này.

### 4.2 `DataShopPack` — 2 instance ⚠ chỉ có sprite

| Field | Số phần tử | Nội dung |
|---|---:|---|
| `allRankSprites` | **5** | sprite khung rank |
| `allSpriteRewards` | **5** | icon phần thưởng |
| `listSpritePlayers` | **5** | icon tàu |
| `listSpriteDrones` | **5** | icon drone |
| `listAvatars` | **5** | avatar |
| `cardPlayerRandomSprite`, `cardDroneRandomSprite`, `itemRandomSprite` | 1 mỗi loại | icon "random" |

> **Sửa vòng 2:** bảng cũ ghi 7 / 27 / 24 / 12 / 24 — **sai**. Mỗi mảng chỉ serialize
> **5 phần tử** (11 cột = 5 × (FileID + PathID) + len). Chi tiết cột: `ECONOMY.md` §4.

Nguồn: `DataShopPack.csv` (69 cột).

**Kết luận:** ❌ **không dùng được cho balance** — không có giá, không có tỉ lệ, không có
số lượng. Chỉ dùng để **map pathID → icon** khi dựng shop UI. 2 instance là bản trùng
(`_gameobject` = `DataShop` cả 2) → **dedup thành 1**.

### 4.3 `GP_Datas` — 1 instance ⚠ là state runtime, không phải config

| Field | Giá trị serialize | Ý nghĩa |
|---|---|---|
| `countAllEnemies`, `countEnemies` | 0 | đếm runtime |
| `spawnCount`, `supplyCount`, `starCount`, `starGetCount` | 0 | đếm runtime |
| `enemyLayer.m_Mask` | **512** | layer mask của enemy (bit 9) |
| `isUsingSkill`, `isTransforming`, `isLockChange` | True/False/False | cờ runtime |
| `player` (ref) | pathID 2625 | trỏ tới player prefab |

Nguồn: `GP_Datas.csv`.

**Kết luận:** ❌ không phải balance. **Dùng được 1 số:** `enemyLayerMask = 512` là thông số
layer vật lý cần tái tạo (Unity layer 9 = enemy). Các field còn lại là counter.

### 4.4 `RankManager` — 3 instance ⚠ chỉ là UI wiring

| GameObject chứa | Field đáng chú ý |
|---|---|
| `Board_Maps/Board_Ranks` | refs `loadingObject`, `popupNoInternet`, `popupUploadFailed`, `btnExitCover` |
| `BOARD_ENDGAME` | refs tới loading/popup |
| `Board_Ranks` | refs tới loading/popup |

Nguồn: `RankManager.csv`.

**Kết luận:** ❌ không có ngưỡng rank, không có công thức điểm. `RankManager` chỉ là client
gọi Firebase (`GetTimeOnline`, `IECheckCampaignRankings`, `IESetCampaignRankings`,
`IETryGetRoomRankCampaign`). Toàn bộ config rank nằm ở **Firebase Realtime DB
`/arena---datas/rank-configs/...`** (nguồn: `RankManager.csv` chỉ có 3 dòng ref UI + class
`RankManager` trong `dump.cs` gọi Firebase) → **không có trong APK**.

### 4.5 `ArenaManager` — 1 instance ⚠

Chỉ là component gắn trên `Board_Arena` (pathID 653116), không serialize field nào
(nguồn: `ArenaManager.csv`). Config mùa/rank nằm trong code + Firebase.

### 4.6 Bảng tổng kết độ dùng được

| Bảng | Dùng được cho | Không dùng được cho |
|---|---|---|
| `Tech_Ability_Data` (6) | số ability/stat, icon, level | % hiệu ứng, giá |
| `DataShopPack` (2→1) | icon roster, avatar, khung rank | giá, tỉ lệ, stock |
| `GP_Datas` (1) | layer mask 512 | mọi thứ khác |
| `RankManager` (3) | đường đi UI | ngưỡng rank, thưởng |
| `ArenaManager` (1) | tên class/board | mùa, rank, thưởng |
| `Data_Players` (2) | roster + star + sprite | giá, level curve |
| `Data_Boss` (1) | 46 wave → sprite | HP, phase |
| `Data_Items` (1) | 6 item + sprite stat | effect số |
| `SoundClip` (92) | map id → clip | — |
| `LanguageAssets` (19) | toàn bộ text 19 ngôn ngữ | — |

---

## 5. Công thức — cái gì suy ra được, cái gì không

### 5.1 Suy ra được (mức B/C)

**Damage địch — nay có số tuyệt đối** (nguồn: `Gun_Attack.csv`, chi tiết `COMBAT.md`):

```
damage 1 viên    = Gun_Attack.bltDamage                     (40 – 1.200, 457 giá trị > 0)
DPS              = bltDamage × max(countShots,1) × max(countMags,1) / chu_kỳ
chu_kỳ           = max(countMags,1)×max(countShots,1)×timeShot
                 + (max(countMags,1) − 1) × timeReload
                 + timeRounds
sát thương chạm  = Boss_BodyPhysics.dmgFirst + dmgPerSec × t   (200–10.000 / 5–1.000)
```

**Damage player — vẫn chỉ có công thức dạng, không có hệ số:**

```
Sát thương 1 phát
  = GetMainCannonDamage(playerIndex) hoặc GetWingCannonDamage(playerIndex)
  × xDmgByRank                     // Player_Attack.xDmgByRank, theo rank
  × (1 + addPowerByDevice)         // device
  × (1 + dmgTechItem0)             // tech
  × (1 + addPowerPerKill × kills)  // nếu isAddPowerWhenKill
  × (crit ? 2 : 1)                 // GetMainCannonCritPercent
```
Bằng chứng: các field/hàm trên tồn tại trong `Player_Attack` + `Player_Get_Datas`
(nguồn: `class Player_Attack`, `class Player_Get_Datas` trong `dump.cs`).
**Thứ tự nhân và hệ số cụ thể không xác định** (nằm trong thân hàm).
Xác nhận bằng số: `Gun_Attack.forceType = Enemy` cho **458/458** dòng ⇒ không có súng player
trong asset.

```
HP boss hiển thị = HP serialized (bảng §2.2)
                  × hệ số Enemy_Data_Balance / Stage_Get_Datas theo chapter-stage (chưa bóc)
```
Bằng chứng: `Enemy_Datas.StartHealthPoint` là giá trị **serialize trong prefab**; hệ số nhân
theo chapter/stage nằm ở `Enemy_Data_Balance` + `Stage_Get_Datas` — hai class **không serialize**
(`datas/README.md` §Quy ước xác nhận; `dump.cs` xác nhận chỉ có thân hàm).

```
Điểm arena/PvP = f(idEnemy, timeLife)   // GetArenaScore, GetPVPPlayScore, GetArenaPlayScore
Điểm survival  = GetSurvivalScore(idEnemy)
Thưởng         = GetBonusCoin(id) / GetBonusExp(id)
```
Chỉ biết **signature**, không biết thân hàm (nguồn: `class Enemy_Data_Balance` trong `dump.cs`).

### 5.2 Không suy ra được (mức D)

| Nhóm | Lý do |
|---|---|
| Damage nền từng tàu | `StartMainCannonDamages[]` **không serialize**; `Gun_Attack.forceType` = Enemy 458/458 xác nhận không có súng player trong asset |
| Giá nâng cấp (coin/gem) | `PlayerCosts[]`, `GetUpgadeCostCoins()` — thân hàm; **0 cột giá** trong 91 CSV (`ECONOMY.md` §8) |
| Tỉ lệ rơi item | Không có field trọng số; chỉ suy được **tỉ lệ instance** 676 coin : 26 item (`Item_Movement.csv`) |
| Hệ số scale HP theo stage | `Enemy_Data_Balance` + `Stage_Get_Datas` (scene bundle khác, chưa tìm ra) |
| Ngưỡng VIP 1..6 | `GetVipLevel(vipPoints)` — thân hàm |
| Giá energy/trận | `Stage_Datas.CostOverDrive`, `CostItems[]` — mảng serialize |
| Rank threshold arena | Nằm trên Firebase |

### 5.3 Bảng "độ tin cậy" của các con số trong file

| Số | Mức | Ghi chú |
|---|---|---|
| HP boss/enemy | **A** | serialize, đọc trực tiếp |
| Roster id/star/sprite | **A** | serialize |
| Số phase mỗi boss | **B** | đếm component `HP1/2/3` |
| Wave ↔ prefab boss | **C** | `> Giả định:` khớp số |
| "1 phase = 1 thanh máu" | **B** | `Boss_AttackPhases.allHpParents[]` + 3 round |
| Median/mean ở §2 | **A** | tính từ CSV |
| Mọi con số "damage/giá" | **D** | **không có** |

---

## 6. Field còn thiếu — danh sách cho PHẦN 2 đi tìm

### 6.0 Đã tìm được ở vòng 2 (gạch khỏi danh sách cũ)

| Mục từng ghi "chưa có" | Trạng thái mới | Nguồn |
|---|---|---|
| Damage vũ khí | ✅ **458 giá trị** (nhưng chỉ của địch) | `Gun_Attack.csv` → `COMBAT.md` |
| Burst pattern (shot rate, reload) | ✅ 5 tham số × 458 súng | `Gun_Attack.csv` §3 `COMBAT.md` |
| Tốc độ / tầm đạn | ✅ `bltSpeed` 2–23, `bltLifetime` 1–18 | `Gun_Attack.csv` |
| Hitbox đạn | ✅ `border.w = 15` (184/186) | `Bullet_Linearly.csv` |
| Đạn xuyên khiên | ✅ 58/186 | `Bullet_Linearly.csv` |
| Sát thương va chạm boss | ✅ 247 cặp | `Boss_BodyPhysics.csv` |
| Armor / `noDamage` | ✅ 189/800 | `Enemy_Health.csv` |
| Số wave + spawner | ✅ 282 / **48 archetype** / 10.776 placement | `waves.json` → `ENCOUNTERS.md` |
| Số map + parallax | ✅ 250 map, 5 lớp | `MapController.csv` |
| Số stage theo loại | ✅ 299 (Normal 199 · Boss 26 · Combat 49 · MiniBoss 25) | `Stage_Behaviour.csv` |
| Tỉ lệ rơi tương đối | ✅ 676 coin / 26 item | `Item_Movement.csv` → `ECONOMY.md` §1 |
| Số mốc ability tech | ✅ 6 bảng × 5 mốc | `Tech_Ability_Data.csv` |

**Vẫn còn thiếu thật** (đã kiểm, không có trong bất kỳ CSV nào):
**giá trị số** của: damage player · giá coin/gem · thưởng trong hộp · trọng số rơi · HP player ·
ngưỡng VIP · số stage/chapter · mapping wave→stage.

> ⚠ **Sửa lại:** *tên field* của tất cả các mục trên **đã có** — chúng nằm trong
> `Player_Get_Datas` (178 field), `Tech_Datas` (13), `Droid_Data_Balance` (6),
> `Stage_Get_Datas` (5), `Device_Get_Data` (3). Cái thiếu là **giá trị** trong `.cctor()`.
> Bảng đầy đủ: `TUNING_KNOBS.md` §2–3.

### 6.0b Vì sao các class dưới đây **không được serialize** vào `data.unity3d`

8 class sau là `MonoBehaviour` **không được serialize** — giá trị nằm trong **thân hàm IL2CPP**.
`data.unity3d` chỉ chứa *instance của object có field `[SerializeField]`*; các class này hoặc
không có instance trong scene, hoặc field là `static`/`property` (không serialize).

**Nhưng chúng không nằm ngoài tầm với:** cả 8 class đều có `.cctor()` với **259 field tĩnh**
(trong tổng **957** static của toàn bộ class game),
và `dump.cs` đã có **RVA của từng `.cctor`** (ví dụ `Droid_Data_Balance..cctor` @ `0x1451…`).
Nạp `libil2cpp.so` vào Ghidra headless + `script.json` là **có đường đọc** literal của các field đó —
chưa chạy nên **chưa biết đọc được bao nhiêu**.
Chi tiết + danh sách field: `AI_FEASIBILITY.md` §1.7.

Đây là 8 class được nêu trong handoff. Mỗi class: field cần, ảnh hưởng gì, và nơi nên tìm.

### 6.1 `Player_Get_Datas` (MonoBehaviour, TypeDefIndex 316) — **quan trọng nhất**

| Field cần | Kiểu | Ảnh hưởng |
|---|---|---|
| `PlayerCosts[]` | int[] | giá mở tàu bằng coin |
| `PlayerStarCosts[]` | int[] | giá mở tàu bằng gem/star |
| `PlayerTimeStars[]` | int[] | thời gian chờ mở bằng star |
| `StartHp` | float | HP gốc |
| `StartMainCannonDamages[]` | float[] | damage pháo chính theo tàu |
| `StartMainCannonRate[]` | float[] | tốc độ bắn pháo chính |
| `StartWingCannonDamages[]` | float[] | damage pháo cánh |
| `StartMagnetRange` | float | tầm hút |
| `PercentFreeOverDrive` | float | tỉ lệ overdrive free |
| `StartSecretWeaponDamage/Duration` | float | vũ khí bí mật |
| `StartMaxDuration` | float | thời lượng max |
| `pN_startShotRate`, `pN_startBltSpeed`, `pN_superPowerUpShotRate`, `pN_superPowerUpBltSpeed`, `pN_speedMainCannonBlt`, `pN_radiusCheck` | float | **bộ số đạn của 20 tàu** (thiếu p8/p10/p12/p15) |
| `p2_normalLifetime`, `p2_normalSize`, `p2_supermodeLifetime` | MinMaxCurve | particle đạn tàu 2 |
| `shipCloneLifeTime`, `shipCloneDamage[]` | float | clone (tàu 9/13/14) |
| `forceFieldDuration`, `p19_startShotRate`, `p21_zoneDuration` | float | skill đặc biệt |
| `PercentToCompleteMissions222[]` | float[] | tỉ lệ mission |
| `abi5GainHp` … `abi34Rate` (30 field) | float | hiệu ứng tech ability |
| `stepCommon`, `BaseHpRecoverSpeed`, `stepLevel(playerLv)` | float | đường cong level |

Nơi tìm: scene bundle `Player_Get_Datas` (MonoBehaviour trên prefab/`GP_Manager`), hoặc
asset `.unity3d` khác trong split APK (handoff phần 2 bước 2).

### 6.2 `Droid_Data_Balance` (SpaceShooter, TypeDefIndex 1623)

`MaxLevelUpgrade`, `BaseDamages[]`, `DroidTimeOut[]`, `UnlockCosts[]`, `UnlockStarCosts[]`,
`StartRanks[]`, + thân hàm `GetUpgadeCostCoins`, `GetUpgradeCostGems`.
→ Cần cho: 3 droid item (101/102/103) và damage/cooldown.

### 6.3 `Tech_Datas` (TypeDefIndex 1190)

`MAX_LV_TECHLAB`, `CostUnlockStats[]`, `maxUpgradePlayer`, `maxUpgradeTech`,
`basePriceStatUpgrade[]`, `deltaPricePlayers[]`, `deltaPriceDrones[]`, `deltaPriceDroids[]`,
`basePriceTechStatUpgrade[]`, `deltaPriceTechStats[]`, `DeltaStarCost`, `StartStarCost`,
`CostUpgradeTechLab[]`.
→ Cần cho: giá + trần 12 stat tech và 3 nhánh nâng cấp phụ.

### 6.4 `Stage_Get_Datas` (TypeDefIndex 782)

`startBonusValues[]`, `coinDelta`, `gemDelta`, `levelDelta[]`, `listIgroneEnemies`
+ thân hàm `GetBonus(stageIndex, stageLevel, missionIndex)`, `GetCountEnemies`,
`GetCountSpecialEnemies`, `GetCountSupplyNormal`, `GetCountAllEnemies`.
→ Cần cho: **thưởng theo stage** và **đếm enemy** (dùng để tính độ dài stage).

### 6.5 `Map_Get_Datas` (TypeDefIndex 270)

`listMapDatas`, `listMapBranchDatas`, `listMapTryPlayerDatas`, `AllArenaStartMaps`,
`AllArenaRandomMaps`, `AllPvPStartMaps`, `listIdBosses`, `listMapFightBossDatas`,
`listMapChallangeDatas`, `listMapEndlessDatas`, `listMapObstacleDatas`, `mapChallangeIndexs[]`
+ `GetNumberWaves()`, `GetListWaves(mapIndex)`.
→ Cần cho: **số wave mỗi map**, map pool theo mode/rank.

### 6.6 `Enemy_Data_Balance` (TypeDefIndex 222)

`listStaticEmemies` + thân hàm `GetBonusCoin(id)`, `GetBonusExp(id)`, `GetSurvivalScore(id)`,
`GetArenaScore(idE,timeLife)`, `GetPVPPlayScore`, `GetArenaPlayScore`.
→ Cần cho: **thưởng mỗi enemy**, công thức điểm.

### 6.7 `Device_Get_Data` (TypeDefIndex 580)

`listStatValues` (List<float[]>), `percentByLevels1[]`, `percentByLevels2[]`.
→ Cần cho: giá trị 5 stat × 5 rank × N level.

### 6.8 `GameDatas` (TypeDefIndex 249)

Toàn bộ field là `static` + property, **không có giá trị serialize**:
`energy/coins/gems/starCount/keyCount0-2/wingCoins/timeRewards/coinEvent1/vipPoints/
arenaPoints/campaignPoints/arenaMedal/pvpMedal/…`
+ thân hàm `GetVipLevel(vipPoints)`, `IsProVersion`, `GetInstallDays`, `IsCountryPremium`.
→ Cần cho: giá trị khởi tạo, ngưỡng VIP, thời gian hồi energy.

### 6.9 Class bổ sung nên tìm cùng

| Class | Vì sao |
|---|---|
| `Stage_Datas` | `MAX_STAGE_OF_CHAPTERS[]`, `MAX_ZONE_OF_CHAPTERS[]`, `CostOverDrive`, `CostItems[]` |
| `Wave` / `Stage_Generator` | số wave thực tế (hiện chỉ biết prefab tồn tại tới `Wave_0136`) |
| `ArenaConfig` | `RankSplit`, `SeasonTime`, `MaxRoomCount`, `MinRoomCount`, `SummaryTime`, `IsOpen` |
| `GP_Controller` | `speed`, `speedLerp`, `Boundary` — cảm giác điều khiển |
| `Player_Health` | `StartHealth`, `Armor` — HP khởi đầu runtime |
| `Enemy_Health` | `armor` mặc định |
| `Popup_BuyEnergy` / `Board_ShopEnergy` | `GetCostBuyEnergy/GetValueBuyEnergy` (thân hàm) |
| `Board_ShopCoins.allCosts[]` / `.allValues[]` | giá shop coin |

---

## 7. Đề xuất balance cho bản clone (KHÔNG phải số của WindWings)

Vì §6 chưa có, đây là **target thiết kế** để đội làm clone có mốc, dựa trên *hình dạng* dữ liệu
đã đo (HP boss ch1 median 4,2 M, ch2 6,0 M; enemy median 500 K — `BALANCE.md` §2.3).

### 7.1 Khung HP đề xuất

| Tầng nội dung | HP enemy | HP boss | Ghi chú |
|---|---:|---:|---|
| Chapter 1 (stage 1–5) | 800 – 3,000 | 30,000 | dạy người chơi, 1 phase |
| Chapter 1 (stage 6–15) | 3,000 – 12,000 | 120,000 | thêm part phá được |
| Chapter 1 (stage 16–22) | 12,000 – 40,000 | 300,000 | 1–2 phase |
| Chapter 2 (stage 1–10) | 40,000 – 120,000 | 900,000 | 2 phase |
| Chapter 2 (stage 11–24) | 120,000 – 400,000 | 2,500,000 | 3 phase + 3–5 part |
| Endless | scale tuyến tính theo phút | — | mỗi 60 s ×1.12 HP |

> Tỉ lệ giữa chương giữ nguyên tinh thần bản gốc: **số phase tăng gấp 3, HP thân tăng ~1.5×.**

### 7.2 Time-to-kill (TTK) mục tiêu

| Đối tượng | TTK mục tiêu | Ghi chú |
|---|---|---|
| Enemy thường | 0.3 – 1.0 s | phải chết trong 1 đợt bắn |
| Enemy elite | 2 – 5 s | |
| Boss phase 1 | 15 – 25 s | |
| Boss phase 2 | 20 – 30 s | |
| Boss phase 3 | 25 – 40 s | tổng 1 trận boss 60–95 s |
| 1 stage (wave + boss) | 2.5 – 4 phút | |

Cách kiểm: DPS người chơi ≈ `damage × số đạn/giây` (tính từ bảng §7.3) → TTK = HP / DPS.

### 7.3 Bảng "power budget" đề xuất (mỗi nguồn chiếm bao nhiêu % damage)

| Nguồn | % damage cuối | Lý do |
|---|---:|---|
| Pháo chính (main cannon) | 45% | nguồn chính, scale theo tàu |
| Pháo cánh (wing cannon) | 15% | |
| Device | 15% | 5 slot × 3% |
| Tech basic | 10% | 12 stat |
| Item power-up trong trận | 10% | tạm thời, decay khi chết |
| Crit | +5% kỳ vọng | 1 crit = ×2 |

> Dùng để tránh lỗi phổ biến của clone: **để một nguồn (thường là device) chiếm >50%** làm
> mọi thứ khác vô nghĩa. WindWings tách device theo tàu (`Player_Device_Saved_Datas`) nên
> không stack toàn cục — spec cũng nên làm vậy.

### 7.4 Đường cong nâng cấp đề xuất

| Cấp | Giá (coin) | Damage +% | Ghi chú |
|---:|---:|---:|---|
| 1–10 | 100 × 1.18^n | +4% | nhanh, tạo cảm giác tiến bộ |
| 11–30 | 1,000 × 1.15^n | +3% | |
| 31–60 | 10,000 × 1.12^n | +2% | |
| 61–max | 100,000 × 1.10^n | +1.5% | |

> Đây là **gợi ý**, không có cơ sở từ APK. Nếu phần 2 bóc được `PlayerCosts[]` thì thay bằng số thật.

---

## 8. Còn thiếu / phải đoán

| # | Điều | Trạng thái | Cách xử lý |
|---:|---|---|---|
| 1 | 4 tên boss (index 12, 13, 17, 18) | **không có trong APK** (key chưa dịch) | để placeholder, không bịa |
| 2 | Tên tàu 10999, drone 20013 | **không có** | nội dung chưa mở |
| 3 | Wave ↔ prefab boss | **C — giả định** khớp số 37xxx↔70xx | xác nhận khi tìm được `Map_Get_Datas` |
| 4 | 3 prefab boss có HP = 0 | **A — dữ liệu thật** nhưng vô nghĩa | bỏ khỏi bảng cân bằng |
| 5 | Toàn bộ damage/giá/tỉ lệ | **D** | §6 + §7 |
| 6 | `Boss-39011` HP1..3 "root" vs "copy UI" lệch nhau (1.8/2.9/2.5 vs 2.0/3.1/3.5) | **A** (cả 2 tồn tại) | coi bản **root** là bản trong trận, bản copy là preview |
| 7 | `Boss-39009` có `HP` (600 K, tay) + `HP3` (2.5 M, thân) | **A** | đọc là boss có 1 part HP riêng + 1 thanh chính |
| 8 | Số stage/chapter | **D** (`MAX_STAGE_OF_CHAPTERS[]`) | §6.9 |
| 9 | Có bao nhiêu wave/map | **D** | §6.5 |
| 10 | 20 boss chính ↔ 39 prefab | **C** | 39 prefab = 20 boss × ~2 biến thể (ch1/ch2) |

---

## 9. Nguồn

`docs/apk-analysis/15-enemy-hp.csv` · `Enemy_Datas.csv` · `14-{ships,drones,bosses,items}.csv` ·
`Tech_Ability_Data.csv` · `DataShopPack.csv` ·
`GP_Datas.csv` · `RankManager.csv` · `ArenaManager.csv` · `12-localization.csv` ·
`13-iap-products.csv` · `Enemy_Health.csv` · `Boss_BodyPhysics.csv` · `Gun_Attack.csv` ·
`reverse-engineering/il2cpp/dump.cs.gz` (class `Stage_Datas`, `Map_Get_Datas`, `Player_Health`,
`Enemy_Health`, `Boss_AttackPhases`, `Boss_AttackTypes`).
