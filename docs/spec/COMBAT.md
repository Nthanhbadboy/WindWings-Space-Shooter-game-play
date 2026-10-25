# COMBAT — súng, damage, TTK

> **asm-check** (bản `6109008c`): **16/17 PASS** · `size_capped` **0/425** · ❌ `RankManager` thiếu **8 B** (`ctor` rỗng) — xem **`ASM_INTEGRITY.md`**. Mọi kết luận phủ định trong file này chỉ đúng trong **17 class đã export**.

> Vòng 2. Nguồn sự thật: `reverse-engineering/scriptableobjects/*.csv` + `docs/apk-analysis/*.csv`.
> Không trích dẫn lại tài liệu tóm tắt vòng 1.
> Mỗi bảng ghi `(nguồn: <file>)`; suy đoán đánh dấu `> Giả định:`.

---

## 0. TL;DR

| Chỉ số | Giá trị | Nguồn |
|---|---:|---|
| Súng serialize được | **458** dòng (`Gun_Attack`) = **420** cấu hình không trùng | `Gun_Attack.csv` |
| Damage/viên | **40 – 1.200**, median **400** (457/458 dòng > 0) | `Gun_Attack.csv` `bltDamage` |
| Damage phổ biến nhất | **300–349** (140 súng, 31%) | histogram §1 |
| Tốc độ đạn | **2,0 – 23,0** | `bltSpeed` |
| Tầm bay (thực tế trên từng súng) | **3 – 360** unit, median **40** | `bltSpeed × bltLifetime` |
| DPS lý thuyết (492 cấu hình) | **7,8 – 3.333**, median **454** (dedup: 452 / 506,7) | §4 |
| Súng của **player** trong dump | **0** — toàn bộ 458 là enemy/boss | `forceType = Enemy` 458/458 |
| Enemy có `noDamage` (bất tử với đạn) | **189 / 800 (23,6%)** | `Enemy_Health.csv` |
| Đạn xuyên khiên | **58 / 186** loại đạn | `Bullet_Linearly.csv` `throughShield` |
| TTK | **ước lượng được theo tàu** — DPS player **KHÔNG phải** `damage × rate`: report 79 peer `549a7b5b7c` chứng minh tàu 1 dùng `rate` làm **interval đặt hạn bắn** (deadline = `Time.time` + rate), chưa đếm phát phụ/nhiều nòng. Bind index→ID tàu **ĐÃ XONG** (`0x14e2ce4`, id − 10001) | §6.1 |

> ⚠ **Phát hiện quan trọng nhất:** `Gun_Attack.csv` **không chứa súng của người chơi**.
> Bằng chứng: cột `forceType` có đúng 2 giá trị (`Enemy = 0`, `Ally = 1`) và **458/458 dòng = 0**.
> Damage của player nằm ở `Player_Get_Datas.StartMainCannonDamages[]` — class **không được
> serialize** trong `data.unity3d`. **Đính chính 25/10:** câu *"phải decompile `libil2cpp.so`"* là
> **cũ** — 6 mảng đã decode từ `reverse-engineering/il2cpp/ia-resolved.json`
> → `datas/player_start_stats.json` (§6.1). ~~Cái còn thiếu là bind index → ID tàu~~ — **bind ĐÃ XONG**
> (`0x14e2ce4`, id − 10001, `CROSS_BRANCH` T4); cái thiếu là **chứng minh DPS runtime** (report 79).

---

## 1. Phân bố `bltDamage` (458 súng)

> **⚠ Đọc trước: 38 dòng lặp.** 458 dòng nhưng chỉ **382 `_gameobject`** khác nhau; gom theo
> toàn bộ field (bỏ `path_id`/`m_GameObject`/`m_Script`/`parentBarrels`) → **420 dòng không trùng**.
> Nguyên nhân giống `ENCOUNTERS.md` §1.3: exporter duyệt cả prefab gốc lẫn instance scene.
> **Mọi bảng trong file này tính trên 458 dòng raw** (đúng nguyên văn CSV); số sau dedup ghi
> kèm ở những chỗ chênh đáng kể. Chênh lệch lớn nhất: **median DPS 454,5 → 506,7**.

Histogram khoảng 50 (nguồn: `Gun_Attack.csv`, cột `bltDamage`):

| Khoảng | Số súng | % | Biểu đồ |
|---|---:|---:|---|
| 0 – 49 | 2 | 0,4% | ▏ |
| 50 – 99 | 0 | 0% | |
| 100 – 149 | 18 | 3,9% | ▍ |
| 150 – 199 | 3 | 0,7% | ▏ |
| 200 – 249 | 35 | 7,7% | ▋ |
| 250 – 299 | 7 | 1,5% | ▏ |
| **300 – 349** | **140** | **30,6%** | ███████████████ |
| 350 – 399 | 20 | 4,4% | ▍ |
| 400 – 449 | 34 | 7,4% | ▋ |
| 450 – 499 | 63 | 13,8% | ███████ |
| 500 – 549 | 43 | 9,4% | █████ |
| 550 – 599 | 1 | 0,2% | ▏ |
| 600 – 649 | 61 | 13,3% | ███████ |
| 650 – 699 | 16 | 3,5% | ▊ |
| 700 – 899 | 0 | 0% | |
| 900 – 949 | 10 | 2,2% | █ |
| 1.000 – 1.049 | 2 | 0,4% | ▏ |
| 1.050 – 1.199 | 0 | 0% | |
| 1.200 – 1.249 | 2 | 0,4% | ▏ |
| **Tổng** | **457** | 100% | |

(1 súng có `bltDamage = 0` → rơi khỏi bảng.)

**Đọc ra:**
- Damage **không chia đều** — có 2 cụm: `300–350` và `600–650`. Đây là dấu hiệu designer
  dùng **bảng mốc cố định** (300/450/600/900/1200) rồi ±10%, không phải công thức liên tục.
- **Không có súng nào 700–899** → khoảng trống có chủ đích: 600 là "đạn thường", 900 là
  "đòn nặng". Nếu clone cần thêm tầng, nên đặt ở 750 (giữa khoảng trống).
- Tỉ lệ 300 : 450 : 600 ≈ **31% : 14% : 13%** → 3 mốc này chiếm **58%** toàn bộ vũ khí.

---

## 2. Phân loại vũ khí

### 2.1 `gunType` (enum `Gun_Attack.GunType`)

| Giá trị | Tên | Số súng | % | Hành vi suy ra |
|---:|---|---:|---:|---|
| 0 | `None` | 10 | 2,2% | không tự bắn (dùng `StartSyncAttack`) |
| 1 | **`Auto`** | **325** | 71,0% | tự bắn theo chu kỳ `GunData` |
| 2 | **`Sync`** | **115** | 25,1% | bắn đồng loạt theo nhịp của cha |
| 3 | `Passive` | 8 | 1,7% | chỉ bắn khi được gọi |

Nguồn: `Gun_Attack.csv` `gunType`, enum từ `dump.cs` (`Gun_Attack.GunType`).

> `Auto` + `Sync` = **96%** → chỉ cần 2 kiểu vũ khí là dựng được gần như toàn bộ game.

### 2.2 `forceType` — toàn bộ là đạn địch

| Giá trị | Tên | Số súng |
|---:|---|---:|
| 0 | `Enemy` | **458 / 458** |
| 1 | `Ally` | 0 |

⇒ Khẳng định ở §0 được xác nhận bằng số.

### 2.3 `shootAudioClipName` — âm bắn

13 giá trị khác nhau (nguồn: `Gun_Attack.csv` + enum `AllClipName` trong `dump.cs`):

| id | Clip | Số súng |
|---:|---|---:|
| 0 | `None` | 243 |
| 67 | `Sfx_EnemyShoot7` | 96 |
| 64 | `Sfx_EnemyShoot4` | 33 |
| 62 | `Sfx_EnemyShoot2` | 16 |
| 69 | `Sfx_EnemyShoot9` | 14 |
| 63 | `Sfx_EnemyShoot3` | 12 |
| 66 | `Sfx_EnemyShoot6` | 10 |
| 65 | `Sfx_EnemyShoot5` | 10 |
| 72 | `Sfx_EnemyShoot12` | 9 |
| 68 | `Sfx_EnemyShoot8` | 6 |
| 61 | `Sfx_EnemyShoot1` | 4 |
| 71 | `Sfx_EnemyShoot11` | 3 |
| 73 | `Sfx_EnemyShoot13` | 2 |

**53% súng không có âm bắn** (243/458) → tiếng súng trong game gần như chỉ do **một nửa**
số súng phát; nửa còn lại im lặng để tránh rối. Đây là quyết định mix audio, nên giữ.

---

## 3. Burst pattern — 5 tham số `GunData`

Định nghĩa **chính xác** từ Tooltip serialize trong `dump.cs` (`class GunData`):

| Field | Tooltip gốc | Nghĩa |
|---|---|---|
| `countShots` | "Số lượng đạn. = barrel count" | số nòng bắn cùng lúc |
| `timeShot` | "Thời gian giữa các phát bắn trong một băng. = barrel rate" | giãn cách trong băng |
| `timeReload` | "Thời gian giữa các băng trong một vòng bắn. = shot rate" | giãn cách giữa băng |
| `timeRounds` | "Thời gian giữa các vòng bắn. = turn rate" | nghỉ giữa 2 vòng |
| `countMags` | "Số lượng các băng đạn trong một vòng bắn. = turn count" | số băng/vòng |

Cấu trúc: `vòng bắn = countMags × băng`, `băng = countShots × viên`.

### 3.1 Phân bố giá trị

| Field | Giá trị phổ biến (số dòng) | Nhận xét |
|---|---|---|
| `countMags` | 3 (125), 1 (75), 6 (66), **0 (44)**, 4 (36), 15 (30), 2 (27), 12 (20), 40 (16), 5 (14) | 0 = bắn vô hạn |
| `countShots` | **0 (421)**, 3 (16), 8 (9), 21 (6), 6 (6) | 0 = 1 nòng (mặc định constructor) |
| `timeShot` | **0,0 (397)**, 0,08 (14), 0,10 (14), 0,15 (12), 0,18 (9) | 0 = bắn **loạt** tức thời |
| `timeReload` | 0,20 (61), 0,05 (48), 0,12 (45), 0,30 (45), 0,50 (38), 0,10 (37), 0,60 (31), 0,15 (21) | dải 0,05–0,6 s |
| `timeRounds` | 2,0 (91), 1,0 (63), 0,0 (46), 3,0 (45), 1,8 (33), 5,0 (27), 0,5 (19), 1,5 (19) | dải 0,5–5 s |
| `timeStart` | 1,0 (255), 0,0 (110), 2,0 (19), 3,0 (16), 1,4 (12), 2,25 (7) | trễ trước phát đầu |

Nguồn: `Gun_Attack.csv` các cột `allGunDatas[0..2].*`.

### 3.2 Ba kiểu bắn thực tế rút ra

| Kiểu | Điều kiện | Số súng | Ví dụ |
|---|---|---:|---|
| **Loạt tức thời** (volley) | `timeShot = 0` | 397 | bắn 3–6 viên cùng lúc |
| **Băng liên tục** (burst) | `timeShot > 0` | 61 | 0,08 s/viên × 3 = 0,24 s |
| **Nhiều vòng** | `allGunDatas = [3]` | **29** | 3 mức burst tăng dần theo phase boss |

Ví dụ 1 súng 3 vòng (`Wave_0005/W2-30041/CD-31005`):

| Vòng | countMags | timeShot | timeReload | timeRounds |
|---:|---:|---:|---:|---:|
| 0 | 1 | 0,0 | 0,40 | 3,0 |
| 1 | 2 | 0,0 | 0,30 | 3,0 |
| 2 | 3 | 0,0 | 0,25 | 3,0 |

⇒ Boss/enemy khó dần bằng cách **tăng số băng + giảm reload**, không tăng damage.

---

### 3.3 Damage khai báo **trong `*_Director`** — 112 field, thang 55 → 2.800

Ngoài `Gun_Attack.bltDamage`, boss còn khai báo damage **theo từng đòn** bằng field float
riêng trong class `*_Director`. Đây là **số serialize**, đọc 100% bằng typetree.

| Chỉ số | Số |
|---|---:|
| Instance Director/Phases | **63** (37 class) |
| Instance **có field damage** | **27** |
| **Tổng field damage** | **112** |
| Class có field damage | **19** |
| Boss prefab có field damage | **18 / 39** |

Thang giá trị (bỏ outlier):

| Nhóm | Dải | Ghi chú |
|---|---|---|
| **Đòn thường** | **300 – 1.500** | dày nhất 350–600 — **trùng thang `bltDamage`** |
| **Laser** | **50 · 55 · 80 · 180** | damage/tick nhỏ, chạm liên tục |
| **Kiếm/chém** | 400 · 600 · **2.800** | `Boss6_Director` 2.800 là mức cao nhất của đòn thường |
| **Tường chặn** | **1.000.000** | `MB12_Director.wallBltDmg` (`Boss-37014`) |
| **Sentinel chết-ngay** | **9.000.000** | `Boss-37014` `Boss_BodyPhysics.dmgFirst` ×3 |

> **Nhận định (mức A):** **đòn đặc biệt của boss không mạnh hơn đạn thường về damage/viên.**
> 300–1.500 là **cùng một thang** với `bltDamage` (§1). Cái làm đòn boss khác là
> **số viên, hình dạng, và nhịp** — không phải con số damage.
>
> ⇒ Thiết kế đòn boss cho bản clone: **giữ damage trong dải 350–600**, khác biệt hoá bằng
> **pattern** (toả tròn, xoáy, laser quét) và **số viên**.

**Bảng đầy đủ 18 boss** ở `BOSSES.md` §8.4.1 (kèm tên từng field, ví dụ `dmgBltIdAttack4TwoHand`
1.350 của `Boss10`, `damageBulletArea` 1.200 của `Boss15`).

**Độ khó tăng bằng damage, không bằng HP:** cùng class Director có 2 instance —
`Boss10` 800 → **1.350** (×1,69) · `Boss6` 600 → **2.800** (×4,67) · `Boss9` 500 → **800** (×1,6).
6 class còn lại hai instance giống hệt.

> **Giả định (mức B):** instance thứ hai là **chế độ khó / vòng sau**, không phải boss khác.
> Điều kiện lật ngược: nếu `path_id` của instance thứ hai thuộc prefab **khác** trong cùng họ
> (đã kiểm: `Boss10_Director` 601074 nằm ở `Boss-39012`, 703790 cũng `Boss-39012` ⇒ **cùng prefab**).

## 4. DPS lý thuyết

Công thức (suy ra từ Tooltip §3):

```
băng      = max(countShots, 1) viên
vòng      = max(countMags, 1) băng
burst     = vòng × băng × timeShot + (vòng − 1) × timeReload
chu_kỳ    = burst + timeRounds
DPS       = bltDamage × băng × vòng / chu_kỳ
```

> Giả định: `countShots = 0` → 1 viên; `countMags = 0` → 1 băng; `timeShot = 0` → bắn loạt.
> Đã tính cả 3 vòng của 29 súng `[3]` → **492 cấu hình**.

| Chỉ số DPS | Giá trị |
|---|---:|
| Min | **7,84** (`Boss-37002/Wing2/Gun2.1`, 40 dmg, 5 s/vòng) |
| P25 | 260,9 |
| Median | **454,5** |
| Max | **3.333,3** (`CD-31015`, 600 dmg, 3 băng, 0,05 s reload) |
| Tỉ lệ max/min | **425×** |

Phân bố DPS (492 cấu hình, bin không chồng lấn):

| Khoảng | Số cấu hình | % |
|---|---:|---:|
| 0–99 | 32 | 6,5% |
| 100–199 | 63 | 12,8% |
| 200–299 | 50 | 10,2% |
| 300–399 | 68 | 13,8% |
| 400–499 | 41 | 8,3% |
| 500–699 | 27 | 5,5% |
| 700–899 | 46 | 9,3% |
| 900–1.099 | 17 | 3,5% |
| **1.100–1.499** | **63** | 12,8% |
| 1.500–1.999 | 41 | 8,3% |
| 2.000–2.499 | 35 | 7,1% |
| 2.500–2.999 | **0** | 0% |
| 3.000–3.499 | **9** | 1,8% |
| **Tổng** | **492** | 100% |

Nguồn: tính từ `Gun_Attack.csv` (loại 1 súng `bltDamage = 0`).

> **Đọc ra:** DPS trải **425×**, phân bố **2 đỉnh**: đỉnh thấp **300–399** (68 cấu hình) và
> đỉnh cao **1.100–1.499** (63). **43,3%** dưới 400 DPS; **30,1%** từ 1.100 trở lên.
> Khoảng **2.500–2.999 trống hoàn toàn** và chỉ **9** cấu hình vượt 3.000 — đây là
> **tầng "trừng phạt"** (boss phase cuối), không phải DPS nền.
>
> Nên clone: giữ 2 đỉnh, giữ khoảng trống 2,5 K–3 K, và **đừng** làm mượt phân bố —
> chính khoảng trống tạo cảm giác "gặp đòn nặng" rõ rệt.

## 5. Súng của boss — 21 root

Nhóm theo root `_gameobject`, lấy damage cao nhất (nguồn: `Gun_Attack.csv`):

| prefab | Số súng | Damage max | Damage min | `gunType` |
|---|---:|---:|---:|---|
| `Boss-37002` | 4 | 440 | 40 | 1 |
| `Boss-37003` | 4 | 400 | 200 | 1 |
| `Boss-37004` | 5 | 500 | 300 | 1 |
| `Boss-37006` | **12** | 600 | **0** ⚠ | 1 |
| `Boss-37008` | 1 | 200 | 200 | 1 |
| `Boss-37009` | 2 | 500 | 500 | 1 |
| `Boss-37010` | 3 | 600 | 500 | 0, 1 |
| `Boss-37011` | 3 | 200 | 200 | 1 |
| `Boss-37012` | 1 | 400 | 400 | 1 |
| `Boss-37014` | 1 | **900** | 900 | 1 |
| `Boss-37016` | 2 | 450 | 450 | 1 |
| `Boss-37019` | 5 | 450 | 450 | 1 |
| `Boss-39002` | 5 | 350 | 100 | 1 |
| `Boss-39004` | 14 | 600 | 255 | 1, 2 |
| `Boss-39005` | 3 | 300 | 240 | 2 |
| `Boss-39006` | **24** | 675 | 300 | 1, 2 |
| `Boss-39008` | 4 | **1.200** | 650 | 1 |
| `Boss-39009` | 5 | **1.000** | 500 | 1, 3 |
| `Boss-39010` | **18** | 300 | 100 | 1, 2 |
| `Boss-39016` | 3 | 300 | 200 | 1 |
| `Boss-39017` | 3 | 200 | 200 | 1 |

**Đọc ra:**
- Chương 2 dùng **nhiều súng hơn** (24–18 súng/boss) so với chương 1 (1–5) → độ khó đến từ
  **mật độ đạn**, không phải damage/viên. Khớp kết luận HP ở `BALANCE.md` §2.3.
- **2 boss có damage > 900**: `39008` (1.200) và `39009` (1.000) → đây là "wall" cuối chương 2.
- `Boss-39006` có 24 súng nhưng max chỉ 675 → boss bắn **dày nhưng nhẹ**, ngược lại `39008`
  bắn **thưa nhưng nặng**. Hai kiểu thiết kế khác nhau, nên giữ cả hai khi clone.

### 5.1 Boss không có súng trong dump

`37001`, `37005`, `37013`, `37015`, `37017`, `37018`, `39001`, `39003`, `39007`, `39011`–`39015`,
`39018`–`39021` **không xuất hiện** ở cột root ⇒ súng của chúng nằm trong prefab khác
(hoặc tên root khác như `Boss`/`Parent`/`Body`, xem §5.2).

### 5.2 336 súng có root không phân giải được

**122 súng** (21 root `Boss-xxxxx`) gán được về prefab boss; **336 súng còn lại** thuộc
**106 root generic**. Top 10:

| Root | Số súng | Loại |
|---|---:|---|
| `Boss` | 23 | instance scene preview (`Board_FightBoss`) |
| `Parent` | 20 | generic container |
| `Body` | 18 | generic container |
| `Enemy_Ingame` | 15 | wrapper runtime |
| `Board_FightBoss` | 13 | scene preview UI |
| `Wave_0005` | 11 | prefab wave (enemy thường, không phải boss) |
| `Gun5` | 10 | tên gun lẻ |
| `Tab (5)` | 10 | scene preview UI |
| `Childs` | 10 | generic container |
| `Boss 6` | 9 | instance scene (có số hiệu) |

Nguồn: `Gun_Attack.csv`, `_gameobject` cắt phần trước `/`.

> Muốn gán 336 súng này về đúng enemy/boss phải đi theo `m_Parent` (không có trong CSV)
> hoặc parse `data.unity3d`. Vì vậy bảng §5 **chỉ phủ 122/458 súng (26,6%)** — đủ để thấy
> xu hướng nhưng **không** phải toàn cảnh hoả lực boss.
>
> ⚠ `Boss-37006` có 1 súng `bltDamage = 0` — nhiều khả năng là súng "trang trí"/mount không bắn.
> Đã loại khỏi DPS §4.

---

## 6. TTK

### 6.1 Vì sao **hiện** chưa có số tuyệt đối — nhưng đã biết chỗ lấy

> ⚠ **Sửa lại:** trước đây mục này ghi "không có damage player". **Sai.** Damage player nằm trong
> `Player_Get_Datas`: `StartMainCannonDamages[]` · `StartMainCannonRate[]` ·
> `StartWingCannonDamages[]` · `StartSecretWeaponDamage`, cộng bộ `pN_startShotRate` /
> `pN_startBltSpeed` cho **20 archetype tàu**. Tất cả là `static` → khởi tạo trong `.cctor()`.
> **Cập nhật 25/10:** 6 mảng (`PlayerCosts` int[24] · 3× float[24] · 2× float[3]) **đã decode**
> từ `ia-resolved.json` ⇒ **đã có giá trị**, không còn câu "chưa chạy Ghidra". Cái thiếu là
> **bind** `playerIndex` → ID tàu **ĐÃ XONG** (`0x14e2ce4`, id − 10001, T4). Xem `TUNING_KNOBS.md` §2.2–2.3 · `BALANCE.md` §1.1b.

TTK = `HP / DPS_player`. Trong đó:
- **HP enemy**: **đã có** — `datas/enemy_hp_by_id.json` **150 cặp `id → HP`** (runtime, claim **WRH2**)
  + `15-enemy-hp.csv` **981** dòng serialize (**467** > 0 — cũ ghi 800/394 là **sai**; claim **WRH1**).
  Gộp lại **108/109** prefab spawn có số HP (claim **WRH5**). ~~Còn thiếu hệ số `kHp[mode]`~~ — **không có `kHp`** (sửa 25/10, `DIFFICULTY_MODES` §3–5); TTK = HP(id) ÷ DPS, đủ để tính.
- **DPS player**: **proxy — KHÔNG giao như DPS thật** (sửa 25/10 lần 2 theo report 79 peer). Tích
  `StartMainCannonDamages[24] × StartMainCannonRate[24]` decode từ `ia-resolved.json` →
  `datas/player_start_stats.json` (index 0 = **21.600**, min **456**, max **46.400**) — chỉ dùng
  **ước lượng**. Report 79: tàu 1 dùng `rate` làm **interval** (deadline `@0x10c = Time.time + rate
  @0xa8`); còn phát phụ, nhiều nòng, modifier; không suy 23 tàu từ tàu 1.
  Bind index→ID tàu **ĐÃ XONG** (`0x14e2ce4`, id − 10001).

⇒ Lập được **hai** bảng TTK: (a) theo **ID tàu** (bind xong — số mảng thật, DPS là proxy), (b) theo
**giả thiết DPS** cho designer. Cả hai đều **ước lượng**: nhịp bắn thật chưa chứng minh (report 79).

### 6.2 Bảng TTK (giây)

5 mốc HP phổ biến (nguồn: `15-enemy-hp.csv`, giá trị serialize):

> DPS các cột là **tham số giả định** để suy TTK; DPS player thật **chưa chứng minh** (report 79).

| HP mục tiêu | Nguồn giá trị | DPS 50k | DPS 100k | DPS 250k | DPS 500k | DPS 1M |
|---|---:|---:|---:|---:|---:|---:|
| 270.000 | `Boss-39001` (min, prefab) | 5,4 | 2,7 | 1,1 | 0,5 | 0,3 |
| 500.000 | median enemy (không phải boss) | 10,0 | 5,0 | 2,0 | 1,0 | 0,5 |
| 1.000.000 | `Boss-37001` (1 trong 3 part) | 20,0 | 10,0 | 4,0 | 2,0 | 1,0 |
| 3.200.000 | phase cao nhất `Boss-39017…39021` | 64,0 | 32,0 | 12,8 | 6,4 | 3,2 |
| 5.000.000 | component max (`37018`, `37019`) | 100,0 | 50,0 | 20,0 | 10,0 | 5,0 |
| 11.235.000 | `Boss-39006` tổng prefab (max) | 224,7 | 112,4 | 44,9 | 22,5 | 11,2 |

Nguồn HP: `datas/enemy_hp_by_id.json` (**150 cặp id → HP**, chuẩn — WRH2) · `15-enemy-hp.csv` **981 dòng** serialize (WRH1); xem `BALANCE.md` §2.2.

**Chọn DPS:** với mục tiêu TTK boss 60–95 s (`GAMEPLAY.md` §6.4) và median tổng HP boss
chương 2 = **6,0 M** → **DPS player cuối chương 2 ≈ 65k–100k**; chương 1 (median 4,2 M) ≈ 45k–70k.
Đây là **mốc thiết kế đề xuất**, không phải số của game gốc.

### 6.3 Sát thương môi trường (va chạm)

`Boss_BodyPhysics` (251 dòng) — damage khi **chạm vào thân boss**:

| Field | Ý nghĩa | Dải giá trị | Median |
|---|---|---|---:|
| `dmgFirst` | damage lần chạm đầu | **200 – 10.000** (233/251 dòng nằm trong dải này) | 500 |
| `dmgFirst` (sentinel) | 14 dòng **9.000.000 / 500.000 / 100.000** | ngoài thang — **coi là "giết ngay"** | – |
| `dmgPerSec` | damage/giây khi đứng trong hitbox | **5 – 1.000** | 50 |

Nguồn: `Boss_BodyPhysics.csv`. Cờ kèm theo: `isTrigger = True` 249/251,
`isFirstTrigger = True` 110/251 (chỉ 110 hitbox có đòn "chạm đầu" riêng; 141 dùng chung `dmgPerSec`).

> **Giả định:** 14 dòng `dmgFirst` ≥ 100.000 là **sentinel "instant kill" / hitbox chặn đường**,
> không phải damage theo số. Đã tách khỏi dải cân bằng; nếu coi là số thật thì dải sẽ là
> 200 – 9.000.000 và vô nghĩa với player HP ~vài trăm.
>
> **Đây là damage "không thể né" duy nhất trong game** — người chơi buộc phải học hitbox boss.
> Tỉ lệ `dmgFirst : dmgPerSec` = **40:1 → 2:1** (theo median và 2 đầu dải) ⇒ chạm 1 lần
> đau hơn đứng lâu, nhưng đứng 10 s vẫn tương đương 1 lần chạm.

### 6.4 Armor — enemy bất tử với đạn

| `noDamage` | Số dòng | % |
|---|---:|---:|
| `True` | **189** | 23,6% |
| `False` | 611 | 76,4% |

Nguồn: `Enemy_Health.csv` (800 dòng).

Phân bố theo root: `Wave_0005` (34), `Wave_0004` (30), `Wave_0003` (28) — 3 wave đầu chiếm
**49%** số enemy `noDamage` ⇒ đây là **các part trang trí/cảnh** trong wave mẫu, không phải
enemy chiến đấu. `W2-30053 Mau` (7) và `Boss-37006` (6) là các part thật sự bất tử.

> Hệ quả thiết kế: `noDamage` **không phải cơ chế "invulnerable"** mà là cờ đánh dấu
> **object không phải mục tiêu** (đèn, dây, cảnh nền). Khi clone: đừng làm enemy
> "không thể giết" — người chơi sẽ ức chế.

---

## 7. Đạn — `Bullet_Linearly` (186 loại)

| Field | Giá trị | Số dòng | Nghĩa |
|---|---|---|---|
| `border.w` | **15,0** | 184 | hitbox đạn mặc định |
| | 40,0 / 9,6 | 1 / 1 | biến thể |
| `pointRadius[0]` | 0,15 | 134 | bán kính va chạm |
| | 0,10 / 0,30 / 0,40 / 0,46 | 23 / 7 / 6 / 3 | |
| `throughShield` | **True** | **58** | xuyên khiên |
| | False | 128 | |
| `throughAll` | True | 10 | xuyên mọi mục tiêu |
| `fixedOnLinecast` | True | 46 | bám đường linecast |
| `igroneRevoke` | True | 34 | không bị huỷ khi hết tầm |
| `delay` | 0,0 | **186** | không đạn nào có delay |
| `delayPool` | 0,5 / 1,0 | 5 / 1 | |
| `actived` | False | **186** | cờ editor, luôn tắt |

Nguồn: `Bullet_Linearly.csv`.

**Đọc ra:**
- **31% đạn xuyên khiên** (58/186). Nếu clone làm khiên là "chặn 100%", sẽ sai cảm giác gốc.
- Hitbox đạn **cố định 15 unit** ở 184/186 loại → chỉ có **1 kích thước đạn** về mặt va chạm;
  **cùng hằng số 15 unit với `border.w` của 799/800 enemy** (`ENEMY_BEHAVIOUR.md` §1.3) — đây là
  **bán kính va chạm chuẩn của cả game**, không phải tham số riêng của đạn;
  khác biệt thị giác là do sprite, không do hitbox.
- `actived = False` toàn bộ → đạn được bật bằng code, không bật sẵn trong prefab.

---

## 8. Công thức damage — cái gì suy ra được

```
damage 1 viên (enemy)  = Gun_Attack.bltDamage
sát thương/chạm thân   = Boss_BodyPhysics.dmgFirst  (lần đầu)
                       + dmgPerSec × thời_gian_đứng_trong_hitbox
DPS (enemy)            = bltDamage × băng × vòng / chu_kỳ        (§4)
damage 1 viên (player) = ???  ← KHÔNG CÓ trong dump
```

Hệ số nhân của player (từ `Player_Attack`, đã ghi ở vòng 1) **không kiểm chứng được** bằng số
vì không có giá trị gốc. Xem `BALANCE.md` §6.

---

## 9. Nguồn

`reverse-engineering/scriptableobjects/`: `Gun_Attack.csv` · `Bullet_Linearly.csv` ·
`Bullet_SineWave.csv` · `Enemy_Health.csv` · `Enemy_Datas.csv` · `Boss_BodyPhysics.csv` ·
`Boss4_ExplosionTimer.csv` · `Player19Laser.csv` · `SoundClip.csv`
`docs/apk-analysis/`: `15-enemy-hp.csv` · `Enemy_Datas.csv`
`reverse-engineering/il2cpp/dump.cs.gz`: enum `Gun_Attack.GunType`, `BulletForceType`,
`AllClipName`, `class GunData`, `class Gun_Attack`.

---

## 10. Còn thiếu / phải đoán

| # | Điều | Trạng thái | Ảnh hưởng |
|---:|---|---|---|
| 1 | **Giá trị** damage player | **có tên field** (`Player_Get_Datas.StartMainCannonDamages[]`), chưa có số | đọc `.cctor` bằng Ghidra là có TTK tuyệt đối |
| 2 | **HP của player** | không có (`Player_Health.StartHealth` trong code) | không biết "sống được mấy phát" |
| 3 | 18/39 prefab boss không có súng trong dump + 336 súng root generic | **C** — thiếu `m_Parent` | bảng §5 chỉ phủ 26,6% súng |
| 4 | `countShots = 0` nghĩa là 1 nòng hay "không giới hạn" | **C** — suy từ constructor default | DPS có thể lệch |
| 5 | Công thức cộng dồn damage player (crit, device, tech) | **D** — thân hàm IL2CPP | `BALANCE.md` §5.1 |
| 6 | `BlT_*` (đạn) → `bltId` map tới sprite nào | **C** — cần `sprites.csv` + pathID | art |
| 7 | Vì sao 189 object `noDamage` | **B** — đọc là "không phải mục tiêu" | tránh hiểu sai là armor |
| 8 | `Bullet_SineWave` (2 dòng) dùng ở đâu | **D** — quá ít mẫu | |
| 9 | Tốc độ bắn thực tế có bị `Time.timeScale` điều chỉnh | **D** | cảm giác |

---
