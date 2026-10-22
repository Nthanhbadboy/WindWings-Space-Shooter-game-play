# GAMEPLAY — GDD WindWings: Space Shooter (spec hoá từ APK)

> Tài liệu này **đọc kết quả reverse-engineering** của bản `com.Wind.wings.Space.Shooter`
> v1.3.118 (Unity 2022.3.62f3, IL2CPP) rồi viết lại thành spec thiết kế.
> **Không** chứa code, **không** hướng dẫn build lại APK.
> Quy ước: mỗi số có `(nguồn: …)`; suy luận đánh dấu `> Giả định:`; cuối file là
> **"Còn thiếu / phải đoán"**.

---

## 0. One-pager

| Hạng mục | Nội dung | Nguồn |
|---|---|---|
| Thể loại | **Vertical scrolling shooter** (shmup dọc) + RPG tiến trình + PvP async | `07-enums.md` (`PlayMode` 7 giá trị) |
| Nền tảng | Android (Unity 2022.3.62f3, IL2CPP, arm64), split APK + XAPK | `01-apk-inventory.json`, `02-unity-engine.md` |
| Phiên bản phân tích | 1.3.118, package `com.Wind.wings.Space.Shooter` | `01-apk-inventory.md` |
| Nhà phát hành | GCENTER VIET NAM TECHNOLOGY JSC | `01-apk-inventory.json` (manifest) |
| Điều khiển | 1 ngón kéo tàu (touch drag) hoặc 2 nút trái/phải; **auto-fire** | `GameDatas.TypeControl`, `07-enums.md` |
| Thời lượng 1 trận | 2,5–4 phút (suy từ `rate` × số spawner) | `waves.json` → `ENCOUNTERS.md` §3 |
| Số mode chơi | **7** `PlayMode` + **3** `PVPMode` | `07-enums.md` |
| Nội dung PvE | **282 wave** (236 campaign + 22 boss ch1 + 23 boss ch2 + 1 unknown); 250 map; 299 stage | `waves.json`, `MapController.csv`, `Stage_Behaviour.csv` |
| Tiền tệ | 4 chính + 6 phụ | `GameDatas`, `TypeResource` |
| Kiếm tiền | IAP 170 SKU (**không có giá**) + 19 vị trí quảng cáo | `13-iap-products.csv`, `AdPos` (`07-enums.md`) |
| Ngôn ngữ | 19 (có tiếng Việt) | `LanguageAssets.csv`, `12-localization.csv` |
| Damage địch | 458 súng, 40–1.200 | `Gun_Attack.csv` → `COMBAT.md` |

> Nguồn số ở bảng trên: `01-apk-inventory.md` (phiên bản), `14-ships.csv` (25 tàu),
> `14-drones.csv` (13 drone), `14-bosses.csv` (46 wave-boss), `15-enemy-hp.csv` (800 instance HP),
> `13-iap-products.csv` (170 SKU), `AdPos` (19 vị trí, `07-enums.md`).

### 0.1 Ba vòng lặp

**30 giây — vòng lặp hành động**

```
thấy enemy → kéo tàu né đạn → auto-fire giết → nhặt coin/item → wave tiếp
   ↑                                                            │
   └──────────── power-up tạm thời (item drop) ◄────────────────┘
```
Mục tiêu: **3–8 giây/enemy wave nhỏ**, 1 item drop mỗi 15–20 giây
(nguồn: `15-enemy-hp.csv` — 800 instance, median HP 600.000 khi khác 0; xem `BALANCE.md` §2).

**10 phút — vòng lặp phiên**

```
chọn stage (tốn energy) → chọn ability/talent (Board_Begin) → 3–5 wave → boss
   → Board_Endgame (coin + exp + rank point) → nâng 1 cấp → chơi tiếp hoặc hết energy
```
Mục tiêu: **2–3 trận/phiên**, mỗi trận phải cho **≥ 1 lần nâng cấp có ý nghĩa**.

**1 tuần — vòng lặp meta**

```
quest ngày (Board_Quest) → key (Key0-2) → hộp quà (Board_QuestRewards)
battle pass tuần (Board_BattlePass) → mốc 16 = 3 ngày premium
arena/PvP mùa ~1 tháng (Board_Arena / Board_PVP) → league/rank → quà cuối mùa
```
Mục tiêu: **mỗi ngày 15–20 phút đủ làm hết quest**, cuối tuần chạm mốc battle pass.

> Nguồn cho "mùa 1 tháng": `txt_pvp_reward_info` = "Each season takes place in 1 months."
> Nguồn cho "mốc 16 = premium 3 ngày": `txt_battlepass_free_premium`.

---

## 1. Core loop chi tiết

### 1.1 Điều khiển & di chuyển

| Thành phần | Spec | Bằng chứng |
|---|---|---|
| Di chuyển | kéo trực tiếp (tàu theo ngón tay, có lerp), hoặc nút trái/phải | `GameDatas.TypeControl`, `UILeftRight` |
| Tốc độ | `GP_Controller.speed` + `speedLerp` (giá trị không có trong dump) | `06` §`GP_Controller` |
| Biên | `GP_Controller.Boundary` — tàu không ra khỏi màn | `06` §`GP_Controller` |
| Nghiêng tàu | theo vận tốc ngang (không phải input trực tiếp) | `> Giả định:` từ `TypeMove` |
| Va chạm | `CircleCollider2D`/`BoxCollider2D` trên player + enemy | `04-unity-assets.md` (1.368 + 5.424) |

**Không có nút bắn.** Toàn bộ vũ khí **auto-fire**; người chơi chỉ quyết định *vị trí* và *thời
điểm dùng skill*.

### 1.2 Auto-fire — 4 tầng hoả lực

| Tầng | Nguồn | Điều kiện | Ghi chú |
|---|---|---|---|
| 1 | Pháo chính (main cannon) | luôn bật | `Player_Attack.GetMainCannonDamage()` |
| 2 | Pháo cánh (wing cannon) | mở theo tàu/level | `GetWingCannonDamage()` |
| 3 | Drone (2 slot) | trang bị drone | `Drone_Get_Datas` |
| 4 | Skill chủ động (special cannon, laser, bomb…) | hồi theo thời gian/giết | `Player_Get_Datas.abi*` |

Thứ tự ưu tiên damage: xem `BALANCE.md` §7.3.

### 1.3 Wave

| Thành phần | Giá trị / hành vi | Nguồn |
|---|---|---|
| Đơn vị | `Wave` có `indexWave`, `startPoint`, `endPoint` | `dump.cs` `Wave` |
| Số wave/map | `Map_Get_Datas.GetNumberWaves()` — **giá trị chưa bóc** | `06` |
| Danh sách wave | `GetListWaves(mapIndex)` | `06` |
| Spawn | `SpawnTypes { None, Path, Points, RandomTopDown, Rocket, EndMapPoint, StartWavePoint }` | `07-enums.md` |
| Cuộn nền | `MapController.listZLayers/listSpeedLayers/listNameLayers` (parallax 3 lớp) | `dump.cs` `MapController` |
| Sự kiện wave | `onSpawnLasers`, `onSpawnEMP` (laser/EMP theo wave) | `dump.cs` `MapController` |
| Kết thúc wave | `Wave.CheckSpawnEnded(bool lastWave)`, `GetWaveLength()` | `dump.cs` `Wave` |
| Quân mỗi wave | **4 – 951**, median **131,5**; tổng **45.659** | `waves.json` — xem §1.3.1 |

Cấu trúc 1 stage (suy ra):

```
Stage = 3–5 Wave thường + 1 Wave boss (StageType.Boss)
StageType { Normal, MiniBoss, Boss, Combat }   (07-enums.md)
```
> Giả định: mỗi stage có đúng 1 wave boss ở cuối; `Combat` là wave chỉ có enemy thường.

### 1.3.1 Số quân mỗi wave — kiểm bằng số

Mỗi spawner không có `count` tường minh (0 trên **11.093/11.093**), số quân = `len(enemies) × copies`.

| Chỉ số | Giá trị | Nguồn |
|---|---:|---|
| Tổng quân toàn game | **45.659** | `waves.json` |
| Quân/wave min · median · max | **4 · 131,5 · 951** | `waves.json` |
| Campaign (237 wave) | min 4 · median **152** · max 951 | `waves.json` |
| Boss wave (45 wave) | **4 quân** ở 44/45 | `waves.json` |
| `copies` phổ biến | **2** (9.790) · 1 (792) · 4 (202) · 3 (201) | `waves.json` |

Cấu trúc một wave boss điển hình (44/45 wave):

| Spawner | `spawn_type` | `copies` | Enemy |
|---|---|---:|---|
| `Boss_1` | `point` | 2 | 1 prefab boss |
| `EndPoint` | `boss` | 2 | `CD-31002` |
| `StartPoint` | `special` | 2 | 0 |

`copies = 2` nghĩa là **2 bản sao của spawner**, nên wave boss chuẩn = **2 boss + 2 `CD-31002` = 4 quân**.
Không có loại quân nào khác: **45/45 wave boss chỉ chứa đúng 2 loại** (1 prefab boss + `CD-31002`).
Ngoại lệ duy nhất: **`Wave_7011`** — 46 spawner / **308 quân** (boss + `CB-30015` ×152).

> **Nhận định (mức A):** "giết hết" khả thi về mặt số vì mỗi wave có **danh sách quân hữu hạn, cố định**,
> không sinh thêm ngoài `copies`. Tổng 45.659 không phải số ước lượng mà là **đếm được từng con**.

### 1.3.2 Điều kiện thắng — dữ liệu xác nhận đến đâu

| Bằng chứng | Giá trị | Nguồn |
|---|---|---|
| Cờ thắng nằm ở **player** | `Player_Health.IsVictory`, `isAlive`, `onExtraLife` | `dump.cs` |
| Wave kết thúc theo **spawn** | `Wave.CheckSpawnEnded(bool lastWave)` · `SetLastWave(bool)` · `GetWaveLength()` | `dump.cs` |
| Hành vi cuối path | **`Stop` = 752/800 (94,0%)** · `Loop` = 48 (6,0%) | `Enemy_Movement.csv` + `EndOfPathInstruction { Loop=0, Reverse=1, Stop=2 }` |
| Chết | `isAlive = false` → `Board_Reborn` (5 cách trả) | §1.6 |
| Thắng | `Board_Endgame` + `IsVictory` | `dump.cs`, `08-ui-map.md` |

**Điểm quyết định:** **94,0%** enemy dùng `Stop` — bay hết path thì **dừng lại trong màn**, không bay vòng,
không tự biến mất. Chỉ **6,0%** dùng `Loop`. Nghĩa là phần lớn enemy **ở lại** cho đến khi bị bắn hạ
(hoặc tự huỷ theo `timeToClear` của `Player_Health`).

> **Nhận định (mức B):** `CheckSpawnEnded` nói wave kết thúc khi **spawn xong**, không phải khi **giết xong**.
> Hai điều này chỉ tương đương nếu trong thân hàm còn đếm enemy sống. Tôi **chưa đọc được thân hàm**
> nên chưa phân biệt được "hết spawn là qua" với "hết spawn **và** sạch quân mới qua".
>
> **Điều kiện lật ngược:** nếu `CheckSpawnEnded` chỉ chờ spawner chạy hết mà không đếm enemy còn sống,
> thì "giết hết" **không** bắt buộc — chỉ cần sống sót. Xem `AI_FEASIBILITY.md` §1 (method body chưa có).

### 1.3.3 Nâng cấp — 12 stat, **không** chỉ damage

`§3.4` liệt kê 12 stat. Phân loại theo tác dụng:

| Loại | Stat | Số |
|---|---|---:|
| **Damage trực tiếp** | Special cannon, Normal cannon, Laser weapon, Bomb, Rocket Barrage, Super Lazer, Mega Bomb | **7** |
| **Không phải damage** | **Health, Magnet, Stun, Invisible, Invisible II** | **5** |

Thêm 6 nhóm ability (`txt_techstatability_name_1xx`–`6xx`, **53 tên** unique):

| Nhóm | Tên | Hiệu ứng đọc được |
|---|---|---|
| 1xx | Auto heal · Skip a hit | hồi **{0}% HP mỗi 5 s** · **vô hiệu 1 đòn**, hồi mỗi N giây |
| 2xx | Shooting speed · Critical | giảm delay đại bác **3%** · **x2 crit rate +5%** |
| 3xx | Angry · Take the chance | **HP < 30% → power +10%** · **KO +5%** khi enemy < 30% HP |
| 4xx | Lucky · Auto-fix | (không có text) · kỹ năng hồi **10% HP** |
| 5xx | Laser upgrade · Duration | **khiên + 2 tia laser** · thời lượng **+5%** |
| 6xx | Quick charge | giảm thời gian hồi năng lượng |

> **Nhận định (mức A):** phần lớn nâng cấp đúng là **nhân vào một con số** (damage, delay, crit, %).
> Nhưng **5/12 stat** và 6 nhóm ability có hiệu ứng **không phải damage**: hồi máu, chắn 1 đòn,
> khiên, invisible, magnet, stun. Chúng vẫn là **số passive**, không phải nút bấm kỹ năng —
> trừ **Laser upgrade** (kích hoạt khiên + bắn 2 tia), nghi là **chủ động**.

### 1.4 Drop item

| Item | Tác dụng | Sprite |
|---|---|---|
| Power | tăng damage tạm thời | 1 icon + 5 sprite stat (`14-items.csv` index 1) |
| Overdrive / Super | đầy thanh super | index 2 |
| HP | hồi máu | index 3 |
| Droid 1/2/3 | gọi trợ thủ (giáp / cận chiến / sniper) | index 101–103 |

Nguồn: `14-items.csv`, `06` §`Data_Items`, `txt_item_*` (`12-localization.csv`).

| Quy tắc | Giá trị | Nguồn |
|---|---|---|
| Tỉ lệ rơi | **không xác định được từ APK** | không có field weight |
| Enemy mang item sẵn | **không** (`IsBringItems = False` cho 800/800) | `Enemy_Datas.csv` |
| Coin rơi | theo `Enemy_Data_Balance.GetBonusCoin(id)` | `06` |
| Hút item | `Player_Get_Datas.StartMagnetRange` + tech `Magnet` | `06`, `txt_techstat_*` |

### 1.5 Endgame

| Kết cục | Điều kiện | Board | Thưởng |
|---|---|---|---|
| Thắng | giết boss cuối / hết wave | `Board_Endgame` | coin + exp + rank point |
| Thua | `Player_Health.OnDie` và hết reborn | `Board_Reborn` → `Board_Endgame` | coin theo % damage gây ra |
| Thoát giữa trận | `Board_Pause` → Back | `Board_Pause` | mất energy, không thưởng |

`Board_Endgame` có 3 hành động tăng thưởng:
`btnX2Coins` (video), `btnX20Coins` (IAP), `btnAutoX3Coins` (auto-battle x3) — nguồn: `08-ui-map.md`.

### 1.6 Reborn (hồi sinh)

| Lựa chọn | Nguồn | Điều kiện |
|---|---|---|
| `btnContinueByGems` | gem | đủ gem |
| `btnContinueByEnergy` | energy | đủ energy |
| `btnContinueByAds` | video | ad ready |
| `btnContinueFree` | free | lần đầu trong trận? (không xác định) |
| `btnContinueByPremium` | premium account | `GameDatas.IsProVersion` |

Nguồn: `08-ui-map.md` `Board_Reborn`. Xác nhận từ `dump.cs`:
`Player_Get_Datas.GetCostReborn(int _countReborn)`, `GetCostReborn2(int _countReborn)`,
`GetMaxRebornCount(int vipLevel)` ⇒ **giá hồi sinh tăng theo số lần** và **số lần tối đa phụ thuộc
VIP level**, khớp text `txt_vip_unlock_1_2` = "Maximum chance of revival up to {0}"
(nguồn: `12-localization.csv`).

---

## 2. 7 PlayMode + 3 PVPMode

### 2.1 Bảng tổng

| # | `PlayMode` | Mục đích | Thưởng chính | Điều kiện mở | Nguồn |
|---:|---|---|---|---|---|
| 0 | **Normal** | chạy stage theo chapter, tiến trình chính | coin, exp, star | mặc định | `07-enums.md` |
| 1 | **FightBoss** | đánh lại boss đã gặp để farm | coin, item, card | **thắng stage {0}** | `txt_fightbosscommingsoon` |
| 2 | **Challange** | 4 loại thử thách + 5 modifier | coin ×hệ số, key | **không xác định** (`popupLocked`) | `txt_challange_*` |
| 3 | **Survival** | sống càng lâu càng điểm (`EndlessType.Normal`) | coin, rank point | **không xác định** (`noPopup`) | `Map_Get_Datas.listMapEndlessDatas` |
| 4 | **TryPlayer** | dùng thử tàu chưa mua | không (chỉ trải nghiệm) | có `ShipTrial` | `06` §`ShipTrial` |
| 5 | **Arena** | PvP **async** theo league, 10 giải | arena point, medal | qua stage {0} | `Board_Arena` |
| 6 | **PVP** | PvP realtime/room, 10 rank | pvp medal | qua stage {0} | `Board_PVP` |

> Ghi chú cột "Điều kiện mở": chỉ 4 mode có text xác nhận mốc mở
> (`txt_arena_commingsoon`, `txt_pvp_commingsoon`, `txt_fightbosscommingsoon`,
> `txt_droid_commingsoon` = "Collect {0} stars"); các mode còn lại **không xác định được từ APK**
> — giá trị `{0}` cũng chưa bóc.

### 2.2 Chi tiết từng mode

**Normal** — trục tiến trình. `Board_Stage` → `Board_Begin` → in-game → `Board_Endgame`.
Có 3 độ khó: `txt_stagemode_0/1/2` = **Normal / Hard / Nightmare** (`12-localization.csv`).
Mỗi stage 3 sao (điều kiện sao **không xác định** — có `Stage_Mission` nhưng chưa bóc thân hàm).

**FightBoss** — `Board_SelectBoss` liệt kê 46 wave-boss (`Data_Boss.allBosses`), chọn 1 → vào
`Board_FightBoss` → `Board_Begin`. Khác Normal ở chỗ **vào thẳng wave boss**, không qua wave thường.
(`Map_Get_Datas.listMapFightBossDatas`, `GameMode.indexBoss`.)

**Challange** — 4 loại, mỗi loại 1 luật riêng (nguồn: `txt_challange_short_0..3`):

| # | Tên | Luật | Nguồn |
|---:|---|---|---|
| 0 | Protect | hộ tống tàu con tin | `txt_challange_short_0` |
| 1 | Rescue | giải cứu con tin | `txt_challange_short_1` |
| 2 | The dark | chiến đấu trong đêm (giảm tầm nhìn) | `txt_challange_short_2` |
| 3 | Explosion | enemy nổ khi chết (gây damage lan) | `txt_challange_short_3` |

5 modifier phụ (`txt_challange_mission_0..4`): không hồi sinh · drone skill chỉ dùng 1 lần ·
enemy tăng HP + sức mạnh · laser chết chóc · khoá tạm khi va chạm.
Ngoài ra `GP_Spawner.ChallangeAutoSpawnLasers(rdTime = 12)` ⇒ **laser xuất hiện mỗi 12 giây**.

**Survival** — `EndlessType { Normal, Obstacle }`; chế độ Obstacle dùng chung board
`Board_Survival` (enum `BoardID.BoardObstacle = 27` **không có class**). Điểm =
`Enemy_Data_Balance.GetSurvivalScore(idEnemy)`.

**TryPlayer** — dùng thử tàu có giới hạn thời gian. `ShipTrial` + `Popup_TryShip` +
`Popup_TrialExpried`. Sau khi hết hạn → `Popup_TrialExpried` mời mua.

**Arena** — 10 league (nguồn: `txt_arena_level_name0..9`, `12-localization.csv`): Bronze, Silver, Gold, Platinum, Diamond, Master, Grandmaster, **Phoneix**
(typo trong game), Legend, Champion (`txt_arena_level_name0..9`).
Cơ chế: mỗi mùa chia phòng (`ArenaConfig.MaxRoomCount`, `MinUserCount`), đánh theo lượt,
hết mùa tổng kết → thăng/giữ/xuống hạng (`RankUpIndexs`/`RankDropIndexs`).
Xem `txt_rule_desc1..6`: 10 giải · cần {0} để tổng kết · phòng < {0} người thì giữ nguyên giải ·
thưởng theo thứ hạng · mỗi phòng tối đa {0} người.

**PVP** — 10 rank (`txt_pvp_rank_0..9`): Herald, Guardian, Crusader, Archon, Legend, Ancient,
Divine, Immortal, Eternal, God (nguồn: `12-localization.csv`).
3 `PVPMode`: enum `{Tournament, Solo, Hunter}` nhưng text là **Leagues / Betting / Hunter**
(`txt_pvp_mode_0/1/2`) ⇒ **enum và text lệch nhau**, xem §9.

### 2.3 3 PVPMode — đối chiếu và cảnh báo

| `PVPMode` (enum) | Text (`12-localization.csv`) | Diễn giải | Trạng thái |
|---:|---|---|---|
| 0 `Tournament` | "Leagues" | đấu theo giải/rank | ⚠️ tên lệch |
| 1 `Solo` | "Betting" | **cá cược** — có thể đặt cược medal | ⚠️ **khác hoàn toàn** |
| 2 `Hunter` | "Hunter" | khớp | ✅ |

> **Đây là điểm phải quyết định khi làm bản mới:** "Betting" (cá cược) là cơ chế
> **nhạy cảm** — nhiều nước cấm cá cược trong game trẻ em, và Google Play policy hạn chế.
> Khuyến nghị: **thay `Betting` bằng mode "Duel" (1v1 không cược)** hoặc bỏ hẳn thành 2 mode.

---

## 3. Progression — 9 nhánh

| # | Nhánh | Đơn vị tiến trình | Trần | Nguồn |
|---:|---|---|---|---|
| 1 | **Tàu** (ship) | level 1→N + **star** | 25 tàu (24 mở), star 2.0–5.11 | `14-ships.csv` |
| 2 | **Star** (sao tàu) | sao 1→5, mỗi sao = nhiều mảnh | 5 sao | `Player_Get_Datas.PlayerStarCosts` |
| 3 | **Device** | 5 slot × 5 rank (C→SS) | rank SS | `Device_Get_Data`, 5 device |
| 4 | **Drone** | level + star, 2 slot | 13 drone, star 1.0–5.02 | `14-drones.csv` |
| 5 | **Tech** | 12 stat, level theo TechLab | `MAX_LV_TECHLAB` | `Tech_Datas` |
| 6 | **Talent** | 6 talent, mở theo VIP | 6 | `txt_talent_*`, `Talent.indexVip` |
| 7 | **Chapter** | stage 1..N × 3 độ khó | `MAX_STAGE_OF_CHAPTERS[]` | `Stage_Datas` |
| 8 | **Arena** | league 0→9, point theo mùa | Champion | `ArenaManager` |
| 9 | **Battle Pass** | level mùa + 2 track (free/premium) | `MAX_LEVEL_BP` | `Board_BattlePass` |

### 3.1 Tàu → Star

```
mở tàu:  coin (PlayerCosts[]) hoặc star (PlayerStarCosts[]) hoặc IAP (shipfull*)
nâng:    level (coin) + star (mảnh/star)
star:    PlayerTimeStars[] = thời gian chờ mở bằng star
```
`14-ships.csv` cho **thứ tự sức mạnh**: 10001 Bluesky 2.00 → 10024 Elves 5.11
(nguồn: `14-ships.csv`, cột `Star`).
`10999` (Actived=False) là slot chưa dùng.

### 3.2 Device

5 loại × 5 rank (nguồn: `txt_device_name_1..5`): **Shield / Power / Radar / Bullet technology / Core**,
rank C→SS (`txt_rank_name_*`).
5 stat: Armor, Power, Attack range, Shooting speed, Revive HP (`txt_devicestat_name_1..5`).
Mỗi tàu có bộ device riêng (`Player_Device_Saved_Datas`) ⇒ **không stack toàn cục**.
Có thể bán device (`Board_SellDevices`) và fusion (`Board_BlackBox`).

### 3.3 Drone

13 drone, 2 slot. Mỗi drone: level, star, skill (1 skill/drone).
Skill name: Gunery, Energy shield, Missiles, Laser, Carl Gustaf, Split, Sunshine, Nova,
Lin Sabiu, Bumblebee, Swarm, Spitfire (`txt_droneability_name_20001..20012`).
Nâng bằng card (`DroneCard`) hoặc coin; craft ở `Popup_DroneCraft`.
Droid (3 con, item 101–103) mở bằng **sao**: `txt_droid_commingsoon` = "Collect {0} stars".

### 3.4 Tech — 12 stat

| # | Stat | # | Stat |
|---:|---|---:|---|
| 0 | Health | 6 | Rocket Barrage |
| 1 | Special cannon | 7 | Stun |
| 2 | Normal cannon | 8 | Invisible |
| 3 | Magnet | 9 | Super Lazer |
| 4 | Laser weapon | 10 | Mega Bomb |
| 5 | Bomb | 11 | Invisible II |

Nguồn: `txt_techstat_label_0..11` trong `12-localization.csv`. Mỗi stat có 5 mốc ability
(`Tech_Ability_Data.listDatas[5]`) và text mô tả theo (stat×100 + level), ví dụ
`txt_techstatability_desc_300` = "HP < 30% → power +10%".

### 3.5 Talent — 6, mở theo VIP

`NanoBomb`, `Rocket Barrage`, `Stun`, `Invisible`, `Super Lazer`, `Mega Bomb`
(nguồn: `txt_talent_name_1..6`); `Talent.indexVip` ⇒ **mỗi talent yêu cầu VIP level**.
Dùng ở `Board_Talents` (mở từ `Board_Begin.popupTalents`).

### 3.6 Chapter

2 chapter (`Boss-37xxx` = ch1, `Boss-39xxx` = ch2, nguồn: `15-enemy-hp.csv`). Mỗi chapter N stage × 3 độ khó
(nguồn: `Stage_Datas.MAX_STAGE_OF_CHAPTERS[]` — giá trị chưa bóc).
`Stage_Datas.MAX_STAGE_OF_CHAPTERS[]`, `MAX_ZONE_OF_CHAPTERS[]` — **giá trị chưa bóc**.
Map chọn theo rank ở arena (`Map_Get_Datas.GetListMapArena(rank, index)`).

### 3.7 Arena / Battle Pass

- Arena: league 0–9, point theo trận, thăng/xuống hạng cuối mùa.
- BP: 2 track, mốc 16 = 3 ngày premium, nhiệm vụ 4 loại
  (dùng tàu X giết Y enemy / dùng drone skill / dùng talent / mua IAP).

---

## 4. Economy

### 4.1 Bốn tiền tệ chính

| Tiền tệ | Ký hiệu | Nguồn chính | Tiêu chính |
|---|---|---|---|
| **Coin** | coin | trận thắng, `GetBonusCoin(id)` | nâng tàu/device/drone |
| **Gem** | gem | IAP, quest, achievement | mở tàu, mua energy, reborn |
| **Energy** | energy | hồi theo thời gian, IAP, ads | **vào trận** |
| **Star** | star | mở tàu, quest | mở khoá tàu/nâng star |

`TypeResource { Energy, Star, Coins, Gems, WingCoins }` — nguồn: `07-enums.md`.

### 4.2 Sáu tiền tệ phụ

| Tiền tệ | Nguồn (theo text) | Tiêu |
|---|---|---|
| **WingCoin** | mở hộp quest · mua gói VIP · nhặt in-game · mua ở shop | shop WingCoin |
| **Key0/1/2** | quest ngày | mở hộp quest (3 loại hộp) |
| **VIP point** | IAP | lên VIP 1–6 |
| **Arena point / medal** | trận arena | `Popup_ArenaShopExchange` |
| **Campaign point** | xếp hạng campaign | `Board_Ranks` |
| **PvP medal** | trận PvP | `Popup_PVPShopExchange` |
| **Overdrive** | item drop | dùng skill siêu |
| **Event coin** | event season pass | `Popup_Exchange` |

Nguồn: `txt_info_morewingcoins` (`12-localization.csv`) liệt kê **đúng 4 nguồn WingCoin** (ở trên).

### 4.3 Bảng SOURCE vs SINK

| Nguồn (SOURCE) | Coin | Gem | Energy | Star | WingCoin | Key | Medal |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Thắng trận thường | ●●● | ○ | – | ○ | ● | – | – |
| Boss / FightBoss | ●●●● | ● | – | ● | ● | – | – |
| Quest ngày | ●● | ●● | ● | ● | – | ●●● | – |
| Quest reward box | ●● | ● | ● | ● | ●●● | – | – |
| Battle Pass free | ●● | ●● | ●● | ● | ●● | ● | – |
| Battle Pass premium | ●●● | ●●● | ●●● | ●●● | ●●● | ●● | – |
| Arena cuối mùa | ●● | ●● | – | ● | ●● | – | ●●● |
| PvP cuối mùa | ●● | ●● | – | ● | ● | – | ●●● |
| Ads (19 vị trí) | ●● | ●● | ●● | ○ | ●● | ● | – |
| IAP (170 SKU) | ●●●●● | ●●●●● | ●●●● | ●●● | ●●●● | ●● | ● |
| Gift code | ●●● | ●●● | ●●● | ●●● | ●●● | ●● | ● |

| Nơi tiêu (SINK) | Coin | Gem | Energy | Star | WingCoin | Key |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| Vào trận (Normal/Boss/Challenge) | – | – | **●●●** | – | – | – |
| Reborn | – | ●● | ●● | – | – | – |
| Mở tàu | ●●● | ●●● | – | ●●● | – | – |
| Nâng tàu (level) | ●●●●● | ○ | – | – | – | – |
| Nâng drone | ●●● | ● | – | ● | – | – |
| Nâng device | ●●●● | ●● | – | – | – | – |
| Nâng tech | ●●●● | ●● | – | – | – | – |
| Mở hộp quest | – | – | – | – | – | ●●● |
| Mua energy | – | ●●● | – | – | – | – |
| Shop WingCoin | – | – | – | – | ●●● | – |
| Arena/PvP shop | – | – | – | – | – | – |
| Speed up gift login | – | ● | – | – | – | – |

Ký hiệu: ● = có, số lượng ● = mức độ (1–5), ○ = rất ít/không đáng kể, – = không.

### 4.4 Suy ra tốc độ tiến trình

Giả thiết cân bằng (dùng cho bản clone, không phải số của WindWings):

| Chỉ số | Giá trị đề xuất | Cách kiểm |
|---|---:|---|
| Energy tối đa | 20 | `GameDatas.energy` + `MAX_ENERGY` |
| Hồi energy | 1 / 8 phút | 160 phút đầy = ~2,7 h |
| Cost/trận | 1 energy (Normal), 2 (Boss), 3 (Challenge) | `Stage_Datas.CostOverDrive` |
| Trận/ngày (free) | 20–25 | 20 energy + 3 ads + 2 quest |
| Coin/trận | 300–1.200 | `GetBonusCoin` |
| Coin để nâng 1 cấp tàu (lv 20) | 8.000 | `PlayerCosts[]` |
| Thời gian lên 1 tàu 5 sao | **12–18 ngày** | > Giả định |
| Thời gian full 12 tech stat | **6–8 tuần** | > Giả định |
| Thời gian 1 mùa arena | 30 ngày | `txt_pvp_reward_info` |

> **Nguyên tắc thiết kế rút ra:** game gốc dùng **nhiều lớp tiền tệ** để mỗi hành động có
> "đơn vị" riêng (energy để chơi, key để mở hộp, medal để mua đồ PvP). Bản clone **nên giảm
> còn 3 tiền tệ chính + 3 tiền tệ mode** — 10 loại là quá nhiều cho người chơi mới.

---

## 5. Meta systems

| Hệ thống | Nội dung | Board | Điều kiện |
|---|---|---|---|
| **Battle Pass** | 2 track (free/premium), 4 loại nhiệm vụ | `Board_BattlePass`, `Board_BattlePassPro` | qua stage |
| **Shop** | coin / gem / energy / gift / sale | `Board_Shop`, `Board_ShopCoins/Gems/Energy`, `Board_BigShop` | luôn |
| **Quest** | quest ngày + 3 loại hộp | `Board_Quest`, `Board_QuestRewards` | luôn |
| **Arena season** | 10 league, phòng, tổng kết mùa | `Board_Arena`, `Board_Ranks` | qua stage {0} |
| **PvP** | 10 rank, 3 mode | `Board_PVP`, `Board_RoomPVP` | qua stage {0} |
| **Event** | season pass event + ability event | `Board_EventSeasonPass`, `Popup_AbilityEvent1` | theo lịch |
| **VIP** | 6 mốc, 4 quyền lợi/mốc | `Board_Vip` | tích VIP point |
| **Premium** | gói premium (pro*), 3 ngày free ở BP 16 | `Popup_PremiumDailyRewards` | IAP |
| **Gift login** | 30 ô đăng nhập | `Board_GiftLogin`, `Tab_LogIn` | mở game hằng ngày |
| **Gift code** | redeem code | `Popup_Redeem` | luôn |
| **Rate game** | popup sau N trận | `Popup_Rate` | `VictoryCount ≥ RateStepCount × PopRateCount` |

---

## 6. Boss

### 6.1 Kiến trúc kỹ thuật

```
Boss_Director : Enemy_Appear
├─ Boss_AttackPhases
│   ├─ allHpParents[]        // mỗi phần tử = 1 thanh máu = 1 phase
│   ├─ IEAttackRound1/2/3    // 3 vòng đòn cho mỗi phase
│   └─ (chuyển phase khi HP parent hiện tại = 0)
└─ Boss_AttackTypes
    ├─ DataAttackFixed       // đòn cố định theo vị trí
    ├─ DataAttackAuto        // đòn tự động theo nhịp
    ├─ DataAttackAutoCircle  // đòn toả tròn
    ├─ DataAttackArrangePosition   // dàn theo đội hình
    └─ DataAttackRandomPositionX   // random trục X
```
Nguồn: `dump.cs` `Boss_Director`, `Boss_AttackPhases`, `Boss_AttackTypes`.

⇒ **Phase không phải "máu còn 50% thì đổi"** mà là **nhiều HP parent**: bắn hết thanh này
thì thanh tiếp theo được kích hoạt, kéo theo bộ đòn mới. Đây là lý do có boss 3 thanh
`HP1/HP2/HP3` với HP **tăng dần** (boss càng về sau càng trâu).

### 6.2 20 boss chính

Tên lấy từ `txt_boss_name_0..19` (`12-localization.csv`). **Chỉ 16/20 key có bản dịch** —
4 key (12, 13, 17, 18) còn nguyên placeholder nên **không xác định được tên**.

| # | Tên | prefab tương ứng | HP phase | Tổng HP prefab |
|---:|---|---|---|---:|
| 0 | Sarajevo | `Boss-37001` | – | 1.225.000 |
| 1 | Mother Ship | `Boss-37002` | – | 1.320.000 |
| 2 | Guillotine | `Boss-37003` | – | 3.000.000 |
| 3 | Spider Guardian | `Boss-37004` | – | 272.000 |
| 4 | Emerald Weapon | `Boss-37005` | – | 4.700.000 |
| 5 | The Destroyer | `Boss-37006` | – | 4.100.000 |
| 6 | Psycho Toad | `Boss-37008` | – | 1.300.000 |
| 7 | Ghost of Abyss | `Boss-37009` | – | **0** ⚠ |
| 8 | The Saboteur | `Boss-37010` | – | 4.500.000 |
| 9 | Cyber Samurai | `Boss-37011` | – | 4.000.000 |
| 10 | Octovios | `Boss-37012` | – | **0** ⚠ |
| 11 | Monkey King | `Boss-37013` | – | 4.300.000 |
| 12 | **không xác định** | `Boss-37014` | HP1 2,4M · HP2 3,1M | 5.500.000 |
| 13 | **không xác định** | `Boss-37015` | – | 4.350.000 |
| 14 | Kukuma | `Boss-37016` | – | 5.580.000 |
| 15 | QueenBee | `Boss-37017` | – | 4.300.000 |
| 16 | Frosty Clown | `Boss-37018` | – | 5.000.000 |
| 17 | **không xác định** | `Boss-37019` | – | 5.000.000 |
| 18 | **không xác định** | — | – | — |
| 19 | Soul Master | — | – | — |

> **Nguồn tên:** `txt_boss_name_0..19` (`12-localization.csv`); 4 key (12, 13, 17, 18) còn
> placeholder nên **không xác định được tên**. **Nguồn HP:** `15-enemy-hp.csv`, bảng đầy đủ
> 39 prefab ở `BALANCE.md` §2.2.
>
> **`Giả định:`** ghép theo **thứ tự** — 18 prefab `Boss-37xxx` cho 20 tên boss, nên 2 tên
> cuối (#18, #19) **không có prefab** và phép ghép có thể lệch từ #6 trở đi (vì `Boss-37007`
> không tồn tại). Cần `Map_Get_Datas.listIdBosses` để chốt.
>
> Lớp đòn (`Boss_AttackTypes`) dùng chung cho toàn bộ chương 1 — 5 kiểu: `DataAttackFixed`,
> `DataAttackAuto`, `DataAttackAutoCircle`, `DataAttackArrangePosition`,
> `DataAttackRandomPositionX` (nguồn: `class Boss_AttackTypes`, `dump.cs`).

### 6.3 2 mini-boss + 16 MB variant

| Nhóm | Số | Nhận diện | HP |
|---|---:|---|---:|
| Mini-boss (MB) | 2 (MB, MB2) | atlas `sactx-…-MB`, `sactx-…-MB2` | – |
| MB variant | 16 (MB11–MB17…) | atlas `MB11`…`MB17` | – |
| MB lồng trong boss | ≥ 1 | `Boss-37001/Body/MB-39005` | – |

Nguồn số: `04-unity-assets.md` (tên atlas `sactx-*-MB-*`, `sactx-*-MB2-*`) và `15-enemy-hp.csv`
(path `Boss-37001/Body/MB-39005`).

**Không xác định được:** HP, phase, attack class riêng của MB — chưa có prefab MB độc lập
trong `15-enemy-hp.csv` (chỉ có MB lồng trong boss).

### 6.4 Nhịp độ trận boss (đề xuất)

| Phase | Thời lượng | Hành vi | Số đòn |
|---|---:|---|---:|
| Vào | 2 s | animation spawn, chưa bắn | 0 |
| 1 | 15–25 s | 1–2 `AttackType` cơ bản | 3–5 |
| 2 | 20–30 s | thêm `AutoCircle`, thêm 1 part phá được | 5–7 |
| 3 | 25–40 s | toàn bộ đòn + 1 đòn "enrage" | 7–10 |
| Chết | 1,5 s | nổ, rơi reward | – |

Dữ liệu gốc cho thấy **chương 2 = 3 phase**, chương 1 = 1 phase (17/18 prefab) ⇒ đúng
tinh thần "tăng độ khó bằng số phase, không bằng HP".

---

## 7. Thứ tự build đề xuất

### 7.1 Bảng công việc

| # | Hạng mục | Người-tuần | Lý do thứ tự |
|---:|---|---:|---|
| 0 | Khung dự án, build pipeline, scene loader | 3 | chặn mọi thứ khác |
| 1 | `BoardManager` + 3 `LoadBoardMode` + back stack | 2 | nền của toàn bộ UI |
| 2 | Core loop in-game: di chuyển, auto-fire, wave, spawn | 6 | phần "game" thật sự |
| 3 | Enemy + HP + collision + drop item | 3 | cần cho loop |
| 4 | Boss director + phase + attack types | 6 | nội dung cao cấp nhất |
| 5 | `Board_Home` + `Board_Maps` + `Board_Stage` | 4 | người chơi phải vào được trận |
| 6 | `Board_Endgame` + thưởng + reborn | 2 | đóng vòng lặp |
| 7 | Progression: tàu, star, device | 5 | động lực chơi |
| 8 | Drone + tech + talent | 5 | mở chiều sâu |
| 9 | Economy: coin/gem/energy + shop | 4 | monetize |
| 10 | Quest + battle pass | 3 | retention |
| 11 | Arena (async) | 4 | cần backend |
| 12 | PvP realtime | 6 | đắt nhất, làm sau |
| 13 | Art pass + Spine + audio | 8 | song song được |
| 14 | Live-ops, event, gift code, IAP | 4 | sau khi có nội dung |
| 15 | QA, balancing, soft launch | 6 | – |
| | **Tổng** | **~56** | |

### 7.2 Bản cắt MVP (12 tuần)

| Tuần | Nội dung |
|---:|---|
| 1–2 | khung + `BoardManager` + Home/Maps/Stage |
| 3–5 | core loop + enemy + drop |
| 6–7 | boss 1 phase + Endgame + reborn |
| 8–9 | tàu (5 con) + nâng cấp + device |
| 10 | shop + energy + coin |
| 11 | quest ngày + battle pass free |
| 12 | art pass, audio, QA, soft launch |

**Không có trong MVP:** Arena, PvP, Challenge, Survival, TryPlayer, event, VIP, premium,
gift code, drone, tech, talent.

> Ước lượng trên là **của người viết spec**, không phải số đo từ APK. Giả định team 4–5 người
> (2 client, 1 backend, 1 art, 1 QA) và có sẵn engine/framework.

---

## 8. Điểm khác biệt đề xuất (khác WindWings)

| # | WindWings | Đề xuất | Lý do |
|---:|---|---|---|
| 1 | 10 loại tiền tệ | **3 chính + 3 mode** | giảm cognitive load |
| 2 | 3 độ khó × 2 chapter × nhiều stage | **roguelite run 20 phút** + 1 chapter hub | nội dung ít mà chơi lâu |
| 3 | PvP "Betting" | **Duel không cược** | policy + đạo đức |
| 4 | 20 boss tĩnh | **8 boss × 3 biến thể** | tiết kiệm art |
| 5 | Reborn 5 cách | **1 cách free + 1 ads** | đơn giản, không pay-to-win |
| 6 | 19 ngôn ngữ ngay từ đầu | **EN + VI trước** | tránh phình file |
| 7 | Ads ở 19 vị trí | **5 vị trí** (Endgame x2, reborn, free item, shop energy) | giữ trải nghiệm |
| 8 | Không có narrative | **1 dòng lore/boss** | tăng kết nối |

---

## 9. Còn thiếu / phải đoán

| # | Điều | Trạng thái | Ảnh hưởng |
|---:|---|---|---|
| 1 | Tên 4 boss (index 12, 13, 17, 18) | **không có trong APK** | không được bịa; dùng "Boss 12"… |
| 2 | Mapping `txt_boss_name_N` ↔ prefab `Boss-37xxx` | **C — giả định** theo thứ tự | có thể lệch |
| 3 | `PVPMode.Solo` vs text "Betting" | **A — lệch thật** | phải quyết định thiết kế |
| 4 | Điều kiện mở Arena/PvP (`stage {0}`) | **giá trị {0} chưa bóc** | không biết mốc chính xác |
| 5 | Số stage/chapter | **D** — `MAX_STAGE_OF_CHAPTERS[]` | không biết độ dài game |
| 6 | Số wave/map | **D** — `GetNumberWaves()` | không biết độ dài trận |
| 7 | Tỉ lệ rơi item | **D** | chưa có — lấy bằng Ghidra `Enemy_Data_Balance` + Frida |
| 8 | Damage/giá/thưởng | **D** — xem `BALANCE.md` §6 | phải thiết kế lại |
| 9 | Điều kiện 3 sao mỗi stage | **D** — `Stage_Mission` chưa bóc | lấy được: `Stage_Get_Datas.IsMissionCompleted()` |
| 10 | HP/phase của 2 mini-boss + 16 MB | **D** | chỉ có tên atlas |
| 11 | Cơ chế "Overdrive" | **C** — có `PercentFreeOverDrive`, item index 2 | chưa rõ công thức |
| 12 | Số lần reborn tối đa | **D** — `GetMaxRebornCount()` | ảnh hưởng monetize |
| 13 | `Betting` hoạt động thế nào | **không xác định** | nên bỏ |
| 14 | `GP_Datas` toàn 0 | **A** | bảng này vô dụng |
| 15 | 3 board `BoardObstacle/BoardUpgrades/BoardTradeDevices` không có class | **A** | map thủ công |

---

## 10. Nguồn

**Dữ liệu bóc:**
`01-apk-inventory.json` · `04-asset-manifest.csv` · `12-localization.csv` · `13-iap-products.csv` ·
`14-{ships,drones,bosses,items}.csv` ·
`15-enemy-hp.csv` · `Enemy_Datas.csv` · `DataShopPack.csv` · `Tech_Ability_Data.csv` ·
`GP_Datas.csv` · `RankManager.csv` · `SkeletonDataAsset.csv` · `SoundClip.csv` ·
`datas/waves.json` · `datas/enemy_hp.json` · `datas/bosses.json` · `datas/ships.json` ·
`reverse-engineering/scriptableobjects/`: `Gun_Attack.csv` · `Bullet_Linearly.csv` ·
`Enemy_Health.csv` · `Boss_BodyPhysics.csv` · `Box_Rewards.csv` · `Shop_Cell.csv` ·
`Sub_Item.csv` · `Item_Movement.csv` · `Tech_Ability_Data.csv` · `MapController.csv` ·
`Stage_Behaviour.csv` · `Wave.csv` · `Call_Data.csv` · `Spawner.csv`

**Mã IL2CPP:**
`reverse-engineering/il2cpp/dump.cs.gz` — class `BoardManager`, `UIManager`, `MapController`,
`Map_Get_Datas`, `Stage_Get_Datas`, `Stage_Datas`, `Chapter`, `Wave`, `Boss_AttackPhases`,
`Boss_AttackTypes`, `Boss_Director`, `Player_Attack`, `Player_Health`, `Enemy_Health`,
`GP_Spawner`, `GP_Endgame`, `Popup`, `Popup_Notices`.

**Số liệu chi tiết vòng 2:** `COMBAT.md` (súng/damage/TTK) · `ENCOUNTERS.md` (wave/spawner/map) ·
`ECONOMY.md` (thưởng/shop/giá).

**Tài liệu cùng bộ:**
`docs/spec/BALANCE.md` (số liệu HP/roster) · `docs/spec/UI.md` + `screens.csv` (màn hình) ·
`docs/spec/ASSETS.md` + `sprite-list.csv` (art/audio).
