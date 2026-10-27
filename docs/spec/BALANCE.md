# BALANCE — số liệu WindWings: Space Shooter (bản spec hoá)

> Sinh từ dữ liệu **đã bóc** trong repo. Mỗi bảng ghi nguồn. Suy đoán ghi `> Giả định:`.
> Không có giá trị nào được nội suy thành số cụ thể nếu APK không có — những chỗ đó ghi
> **"không xác định được từ APK"** và được liệt kê lại ở §6 để phần 2 đi tìm.

---

## 0. TL;DR cho designer

| Câu hỏi | Trả lời ngắn | Nguồn |
|---|---|---|
| Boss khó nhất (theo HP phải bắn hết) | `Boss-39017`: 9,900,000 tổng (3 phase + 15 part phụ) | `15-enemy-hp.csv` |
| Boss dễ nhất | `Boss-37004`: 136,000 | `15-enemy-hp.csv` |
| Boss chương 1 khác chương 2 thế nào | Ch1 **1 phase** (17/18 prefab); Ch2 **3 phase** (11/21 prefab) | `15-enemy-hp.csv` |
| HP enemy thường | median 500,000; 27% số enemy có HP = 0 (slot trang trí) | `Enemy_Datas.csv` |
| Tàu mạnh nhất theo "sao" | `10024 Elves` 5.11 sao; yếu nhất `10001 Bluesky` 2.0 | `14-ships.csv` |
| Bao nhiêu nội dung balance thật sự có | **Rất ít**: chỉ HP + roster + 6 bảng SO phụ; **0 giá trị** damage/giá/thưởng | `10-scriptableobjects.md`, §6 |
| Có thể dựng lại balance đầy đủ? | Không. Phải thiết kế lại từ đầu dựa trên khung ở §7 | — |

---

## 1. Phương pháp & nguồn

| Bảng | File | Trạng thái |
|---|---|---|
| HP 981 enemy/boss | `docs/apk-analysis/15-enemy-hp.csv` (dẫn xuất từ `Enemy_Datas.csv`) | ✅ có số |
| Cờ enemy | `docs/apk-analysis/Enemy_Datas.csv` | ✅ có số |
| Roster tàu/drone/boss/item | `14-ships.csv`, `14-drones.csv`, `14-bosses.csv`, `14-items.csv` | ✅ có số |
| Tên tàu/drone/boss/talent/ability | `12-localization.csv` | ✅ có text |
| Tech ability / shop pack / GP / rank | `Tech_Ability_Data.csv`, `DataShopPack.csv`, `GP_Datas.csv`, `RankManager.csv` | ⚠ chỉ có sprite/id, không có số balance |
| Damage, giá, thưởng, tỉ lệ rơi | `06-gameplay-systems.md`, `09-numbers-and-formulas.md` | ❌ chỉ có tên field |

**Quy ước dedup HP:** một enemy có thể xuất hiện nhiều lần trong cùng file vì cùng prefab được
đặt trong: (a) prefab gốc, (b) scene `Board_FightBoss` (tab preview), (c) scene map/scrollview.
Ta gom theo **root prefab** + **đường dẫn component sau root**, lấy `max(HP)` cho mỗi cặp
`(root, component)`. Cặp nào chỉ khác nhau phần "Tab (n)/…/Parent_View/…" bị coi là **bản copy UI**.

---

## 2. HP enemy / boss

### 2.1 Tổng quan

| Chỉ số | Giá trị | Nguồn |
|---|---:|---|
| Số instance `Enemy_Datas` | 981 | `10-scriptableobjects.md` |
| Số instance có `StartHealthPoint > 0` | 467 | `Enemy_Datas.csv` |
| Số instance HP = 0 (slot chưa dùng / trang trí) | 514 | `Enemy_Datas.csv` |
| HP lớn nhất | 10,000,000 (`CB(TEST)` — object test, **loại khỏi balance**) | `15-enemy-hp.csv` |
| HP lớn nhất (hợp lệ) | 5,000,000 (`Boss-37019`, `Enemy_Ingame/GunParent`) | `15-enemy-hp.csv` |
| Số cặp `(path, HP)` duy nhất | 860 / 981 | tính từ `15-enemy-hp.csv` |
| Số prefab boss có HP | 39 | `15-enemy-hp.csv` |
| Số prefab `Wave_*` chứa enemy | 35 (`Wave_0003`…`Wave_0136`) | `15-enemy-hp.csv` |

Phân bố HP (467 instance > 0):

| Khoảng HP | Số instance |
|---|---:|
| < 100 K | 63 |
| 100 K – 500 K | 136 |
| 500 K – 1 M | 130 |
| 1 M – 2 M | 56 |
| 2 M – 3 M | 43 |
| ≥ 3 M | 39 |

> Đọc bảng này: **39 instance ≥ 3 M chính là 39 prefab boss** — tức "1 dòng = 1 boss".
> Dải 100 K–1 M (266 instance) là enemy thường và **part phụ của boss**.
> Nhịp HP của game là bậc 2: enemy ~0.1–1 M, boss ~3–10 M tổng.

### 2.2 Bảng 39 prefab boss (đã dedup, bỏ bản copy UI)

Cột **rows** = số dòng gốc trong `15-enemy-hp.csv`; **copy UI** = số dòng là bản sao trong
`Board_FightBoss`/`Board_SelectBoss`/scrollview; **tail** = số component HP duy nhất của prefab;
**phase HP** = các component đặt tên `HP1/HP2/HP3` (mỗi cái = 1 thanh máu = 1 phase);
**tổng HP** = tổng mọi component (thân + part phụ) — đây là "damage phải bỏ ra để giết sạch prefab".

| prefab | wave (giả định) | rows | copy UI | tail | phase HP | tổng HP (dedup) | HP thân lớn nhất | part phụ |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| `Boss-37001` | 7001 | 3 | 0 | 3 | – | 1,225,000 | 1,000,000 | 2 |
| `Boss-37002` | 7002 | 6 | 0 | 6 | – | 1,180,000 | 380,000 | 5 |
| `Boss-37003` | 7003 | 4 | 0 | 4 | – | 1,500,000 | 500,000 | 3 |
| `Boss-37004` | 7004 | 3 | 0 | 3 | – | 136,000 | 68,000 | 2 |
| `Boss-37005` | 7005 | 4 | 0 | 4 | – | 6,300,000 | 3,900,000 | 3 |
| `Boss-37006` | 7006 | 18 | 0 | 18 | – | 6,220,000 | 2,200,000 | 17 |
| `Boss-37008` | 7008 | 4 | 0 | 4 | – | 1,700,000 | 1,100,000 | 3 |
| `Boss-37009` | 7009 | 1 | 0 | 1 | – | 0 ⚠ | 0 | 0 |
| `Boss-37010` | 7010 | 2 | 0 | 2 | – | 4,500,000 | 4,500,000 | 1 |
| `Boss-37011` | 7011 | 1 | 0 | 1 | – | 4,000,000 | 4,000,000 | 0 |
| `Boss-37012` | 7012 | 2 | 0 | 2 | – | 2,800,000 | 2,800,000 | 1 |
| `Boss-37013` | 7013 | 2 | 0 | 2 | – | 4,300,000 | 4,300,000 | 1 |
| `Boss-37014` | 7014 | 6 | 3 | 3 | HP1=2,400,000 · HP2=3,100,000 | 5,500,000 | 3,100,000 | 2 |
| `Boss-37015` | 7015 | 2 | 0 | 2 | – | 4,350,000 | 4,350,000 | 1 |
| `Boss-37016` | 7016 | 4 | 0 | 4 | – | 7,290,000 | 3,870,000 | 3 |
| `Boss-37017` | 7017 | 2 | 0 | 2 | – | 4,300,000 | 4,300,000 | 1 |
| `Boss-37018` | 7018 | 1 | 0 | 1 | – | 0 ⚠ | 0 | 0 |
| `Boss-37019` | 7019 | 2 | 0 | 2 | – | 5,000,000 | 5,000,000 | 1 |
| `Boss-39001` | 9001 | 1 | 0 | 1 | – | 0 ⚠ | 0 | 0 |
| `Boss-39002` | 9002 | 4 | 0 | 4 | HP1=680,000 · HP2=550,000 · HP3=450,000 | 1,680,000 | 680,000 | 3 |
| `Boss-39003` | 9003 | 2 | 0 | 2 | – | 580,000 | 580,000 | 1 |
| `Boss-39004` | 9004 | 12 | 3 | 9 | – | 6,410,000 | 1,650,000 | 8 |
| `Boss-39005` | 9005 | 19 | 7 | 12 | – | 5,960,000 | 1,500,000 | 11 |
| `Boss-39006` | 9006 | 31 | 15 | 16 | – | 9,355,000 | 1,500,000 | 15 |
| `Boss-39007` | 9007 | 3 | 1 | 2 | – | 648,000 | 648,000 | 1 |
| `Boss-39008` | 9008 | 10 | 4 | 6 | HP3=3,300,000 | 8,820,000 | 3,300,000 | 5 |
| `Boss-39009` | 9009 | 9 | 4 | 5 | HP=600,000 · HP3=2,500,000 | 5,100,000 | 2,500,000 | 4 |
| `Boss-39010` | 9010 | 13 | 0 | 13 | – | 4,450,000 | 600,000 | 12 |
| `Boss-39011` | 9011 | 12 | 6 | 6 | HP1=1,800,000 · HP2=2,900,000 · HP3=2,500,000 | 7,200,000 | 2,900,000 | 5 |
| `Boss-39012` | 9012 | 8 | 4 | 4 | HP1=1,800,000 · HP2=2,600,000 · HP3=2,800,000 | 7,200,000 | 2,800,000 | 3 |
| `Boss-39013` | 9013 | 8 | 1 | 4 | HP1=2,200,000 · HP2=2,500,000 · HP3=3,000,000 | 7,700,000 | 3,000,000 | 3 |
| `Boss-39014` | 9014 | 8 | 1 | 4 | HP1=2,350,000 · HP2=2,680,000 · HP3=3,000,000 | 8,030,000 | 3,000,000 | 3 |
| `Boss-39015` | 9015 | 8 | 2 | 4 | HP1=2,500,000 · HP2=3,000,000 · HP3=3,500,000 | 9,000,000 | 3,500,000 | 3 |
| `Boss-39016` | 9016 | 2 | 0 | 2 | HP=600,000 | 600,000 | 600,000 | 1 |
| `Boss-39017` | 9017 | 33 | 14 | 16 | HP1=1,800,000 · HP2=2,800,000 · HP3=3,200,000 | 9,900,000 | 3,200,000 | 15 |
| `Boss-39018` | 9018 | 8 | 4 | 4 | HP1=2,200,000 · HP2=2,800,000 · HP3=3,200,000 | 8,200,000 | 3,200,000 | 3 |
| `Boss-39019` | 9019 | 4 | 0 | 4 | HP1=2,200,000 · HP2=2,800,000 · HP3=3,200,000 | 8,200,000 | 3,200,000 | 3 |
| `Boss-39020` | 9020 | 4 | 0 | 4 | HP1=2,200,000 · HP2=2,800,000 · HP3=3,200,000 | 8,200,000 | 3,200,000 | 3 |
| `Boss-39021` | 9021 | 4 | 0 | 4 | HP1=2,200,000 · HP2=2,800,000 · HP3=3,200,000 | 8,200,000 | 3,200,000 | 3 |

Nguồn: tính từ `docs/apk-analysis/15-enemy-hp.csv`.

**Ghi chú quan trọng của bảng:**
- ⚠ `Boss-37009`, `Boss-37018`, `Boss-39001` có **1 component HP = 0** → prefab chỉ là "vỏ" để
  instantiate runtime, HP được set trong code/prefab khác. **Không dùng 3 dòng này để cân bằng.**
- `Boss-37001` chứa **`MB-39005`** như một child boss (`Enemy_Ingame/Body/MB-39005/...`) →
  bằng chứng MB (mini-boss) được tái sử dụng làm part trong boss chính.
- Boss nhiều part nhất: `Boss-37006` (17 part), `Boss-39006` (15), `Boss-39017` (15) — đây là
  loại "boss có nhiều súng phá được", không phải 17 phase.

### 2.3 So sánh 2 chương

| Chỉ số | Chapter 1 (`Boss-37xxx`) | Chapter 2 (`Boss-39xxx`) |
|---|---:|---:|
| Số prefab | 18 | 21 |
| Số phase phổ biến | 1 phase (17/18) | 3 phase (11/21), 7 không có component `HP*` |
| HP thân median | 2,950,000 | 2,800,000 |
| **Tổng HP median** (thân + part) | **4,150,000** | **7,200,000** |
| Tổng HP cả chương | 60,301,000 | 125,433,000 |
| Tổng HP cao nhất | `37016` = 7,290,000 | `39017` = 9,900,000 |
| Tổng HP thấp nhất | `37004` = 136,000 | `39016` = 600,000 |

> **Đọc ra:** chương 2 **không tăng HP thân** (2.8 M ≈ 2.95 M) mà **tăng số phase + số part** →
> độ khó đến từ **nhịp attack và số mục tiêu**, không phải từ "HP to hơn". Đây là bài học
> thiết kế trực tiếp dùng được: muốn boss khó hơn thì thêm phase/part, không nên chỉ tăng HP.

### 2.4 Enemy thường

| Chỉ số | Giá trị | Nguồn |
|---|---:|---|
| Instance enemy thường (không thuộc root `Boss-*`) HP > 0 | 252 | `15-enemy-hp.csv` |
| Median HP enemy thường | 500,000 | `15-enemy-hp.csv` |
| Max HP enemy thường | 10,000,000 (`CB(TEST)` — bỏ) | `15-enemy-hp.csv` |
| Số prefab `Wave_*` có chứa enemy | 35 | `15-enemy-hp.csv` |
| Wave nhiều enemy nhất | `Wave_0005` (67 slot), `Wave_0004` (54), `Wave_0003` (28) | `15-enemy-hp.csv` |
| Wave id lớn nhất thấy được | `Wave_0136` | `15-enemy-hp.csv` |

Phân loại theo root path (981 dòng):

| Nhóm | Số dòng | Số dòng HP>0 |
|---|---:|---:|
| Prefab `Boss-*` | 201 | 163 |
| Prefab `Wave_*` | 233 | 0 ⚠ |
| Prefab `W1-/W2-*` (chương 2) | 47 | 2 |
| Bản copy trong board (Tab/ScrollView/Parent_View/Board_*) | 96 | 81 |
| Khác (`Enemy_Ingame`, `Body`, `Gun*`, `Head`…) | 404 | 221 |

> ⚠ **233 dòng thuộc `Wave_*` đều có HP = 0** → enemy trong wave prefab lấy HP từ
> `Enemy_Data_Balance` lúc runtime, không serialize trong prefab. Đây chính là lý do
> **không thể tái tạo đường cong HP theo stage** từ APK (xem §6).

### 2.5 Cờ hành vi của enemy (dùng để phân loại)

| Cờ | True | False | Ý nghĩa |
|---|---:|---:|---|
| `IsCaAttack` | 524 | 457 | Có thể tấn công (53%) |
| `IsBringItems` | 0 | 981 | **Không enemy nào mang item sẵn** — item do controller drop |
| `IsInvisible` | 0 | 981 | Không có enemy invisible mặc định |
| `IsAlive` | 2 | 979 | Giá trị editor-time, không dùng |
| `m_Enabled` | 981 | 0 | Tất cả bật |

Nguồn: `Enemy_Datas.csv`.

---

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

| asset | Level / TypeIndex / Sprite pathID (5 entry) |
|---|---|
| `TechAbility1` | 1·2·3893 | 2·1·2700 | 3·1·2700 | 2·2·3893 | 4·1·2700 |
| `TechAbility2` | 1·0·2543 | 2·0·2543 | 1·0·2463 | 3·0·2543 | 2·0·2463 |
| `TechAbility3` | 1·0·2601 | 2·0·2601 | 1·0·2959 | 3·0·2601 | 2·0·2959 |
| `TechAbility4` | 1·1·3298 | 2·1·3298 | 1·2·2493 | 3·1·3298 | 2·2·2493 |
| `TechAbility5` | 1·0·3827 | 1·0·3308 | 2·0·3827 | 3·0·3827 | 2·0·3308 |
| `TechAbility6` | 1·0·3852 | 2·0·2930 | 1·0·3852 | 3·0·2930 | 4·0·3852 |

Nguồn: `Tech_Ability_Data.csv`, `10-scriptableobjects.md`.

**Kết luận:** dùng được để biết **số ability mỗi stat (5)** và **icon theo (level, type)**, nhưng
**không có % hiệu ứng**. Hiệu ứng nằm ở `Player_Get_Datas.abi*` và text `txt_techstatability_desc_<stat*100+level>`
(ví dụ `txt_techstatability_desc_300` = "If health points are below 30%, power increases by 10%").
⇒ Spec hoá ability nên **lấy text làm nguồn số**, không lấy bảng này.

### 4.2 `DataShopPack` — 2 instance ⚠ chỉ có sprite

| Field | Số phần tử | Nội dung |
|---|---:|---|
| `allRankSprites` | 7 | sprite khung rank |
| `allSpriteRewards` | 27 | icon phần thưởng |
| `listSpritePlayers` | 24 | icon 24 tàu (khớp `14-ships.csv`) |
| `listSpriteDrones` | 12 | icon 12 drone |
| `listAvatars` | 24 | avatar |
| `cardPlayerRandomSprite`, `cardDroneRandomSprite`, `itemRandomSprite` | 1 mỗi loại | icon "random" |

Nguồn: `DataShopPack.csv` (69 cột), `10-scriptableobjects.md`.

**Kết luận:** ❌ **không dùng được cho balance** — không có giá, không có tỉ lệ, không có
số lượng. Chỉ dùng để **map pathID → icon** khi dựng shop UI. 2 instance là bản trùng
(pathID 2496 và 636597, khác `m_FileID`) → **dedup thành 1**.

### 4.3 `GP_Datas` — 1 instance ⚠ là state runtime, không phải config

| Field | Giá trị serialize | Ý nghĩa |
|---|---|---|
| `countAllEnemies`, `countEnemies` | 0 | đếm runtime |
| `spawnCount`, `supplyCount`, `starCount`, `starGetCount` | 0 | đếm runtime |
| `enemyLayer.m_Mask` | **512** | layer mask của enemy (bit 9) |
| `isUsingSkill`, `isTransforming`, `isLockChange` | True/False/False | cờ runtime |
| `player` (ref) | pathID 2625 | trỏ tới player prefab |

Nguồn: `GP_Datas.csv`, `10-scriptableobjects.md`.

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
`/arena---datas/rank-configs/...`** (nguồn: `PHAN_TICH` §5.6) → **không có trong APK**.

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
(nguồn: `06-gameplay-systems.md`). **Thứ tự nhân và hệ số cụ thể không xác định** (nằm trong thân hàm).

```
HP boss hiển thị = HP serialized (bảng §2.2)
                  × hệ số Enemy_Data_Balance / Stage_Get_Datas theo chapter-stage (chưa bóc)
```
Bằng chứng: ghi chú cuối `15-enemy-hp.md`: "giá trị runtime còn bị nhân bởi
`Enemy_Data_Balance` / `Stage_Get_Datas` theo chapter/stage".

```
Điểm arena/PvP = f(idEnemy, timeLife)   // GetArenaScore, GetPVPPlayScore, GetArenaPlayScore
Điểm survival  = GetSurvivalScore(idEnemy)
Thưởng         = GetBonusCoin(id) / GetBonusExp(id)
```
Chỉ biết **signature**, không biết thân hàm (nguồn: `06` §`Enemy_Data_Balance`).

### 5.2 Không suy ra được (mức D)

| Nhóm | Lý do |
|---|---|
| Damage nền từng tàu | `StartMainCannonDamages[]` là mảng serialize, không có trong textasset/CSV bóc được |
| Giá nâng cấp (coin/gem) | `PlayerCosts[]`, `GetUpgadeCostCoins()` — thân hàm IL2CPP |
| Tỉ lệ rơi item | Không có field tỉ lệ trong `Data_Items` hay `GP_Datas` |
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
đã đo (HP boss ch1 ~4.15 M, ch2 ~7.2 M; enemy median 500 K).

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
`14-data-tables.md` · `10-scriptableobjects.md` · `Tech_Ability_Data.csv` · `DataShopPack.csv` ·
`GP_Datas.csv` · `RankManager.csv` · `ArenaManager.csv` · `12-localization.csv` ·
`06-gameplay-systems.md` · `07-enums.md` · `13-iap-products.csv` ·
`reverse-engineering/il2cpp/dump.cs.gz` (class `Stage_Datas`, `Map_Get_Datas`, `Player_Health`,
`Enemy_Health`, `Boss_AttackPhases`, `Boss_AttackTypes`).
