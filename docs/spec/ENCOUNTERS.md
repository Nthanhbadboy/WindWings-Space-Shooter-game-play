# ENCOUNTERS — 282 wave, spawner, nhịp độ

> Vòng 2. Nguồn sự thật: `datas/waves.json` (sinh từ `Call_Data` trong `data.unity3d`),
> `reverse-engineering/scriptableobjects/Call_Data.csv`, `MapController.csv`, `Wave.csv`,
> `Stage_Behaviour.csv`.
> Mỗi bảng ghi `(nguồn: <file>)`.

---

## 0. TL;DR

| Chỉ số | Giá trị | Nguồn |
|---|---:|---|
| Wave khai báo | **282** (281 có tên + 1 `unknown`) | `waves.json` |
| Spawner | **23.757** (23.692 ở 281 wave có tên + 65 ở `unknown`) | `waves.json` |
| Spawner **thật** (bỏ `StartPoint`/`EndPoint`) | **22.385** | tính từ `waves.json` |
| ⚠ Spawner **sau khi bỏ bản trùng** (~÷2) | **10.498** | §1.3 |
| Wave campaign | **236** (`Wave_0000` – `Wave_0235`) | `waves.json` |
| Wave boss ch1 | **22** (`Wave_7001` – `Wave_7022`) | `waves.json` |
| Wave boss ch2 | **23** (`Wave_9001` – `Wave_9024`, thiếu `9016`) | `waves.json` |
| Spawner/wave (ghi nhận) | min **6** · median **62** · max **621** (`Wave_0163`) | tính từ `waves.json` |
| Spawner/wave (**sau dedup**) | min **3** · median **28** · max **255** | §1.3 |
| Archetype spawner | **48** (+5 marker) từ **53** tên gốc | §2.4 |
| Prefab enemy | **92** = 52 thường + 39 boss + 1 MB | §2.5 |
| Map | **250** (`Map-0000` – `Map-0249`) | `MapController.csv` |
| Stage trên board | **299** (Normal 199 · Boss 26 · Combat 49 · MiniBoss 25) | `Stage_Behaviour.csv` |
| Tên enemy prefab | ✅ **đã resolve** (pipeline vòng 3): **22.462** entry · **109** prefab khác nhau | `waves.json` nhánh `ef6b75ef` |
| Enemy prefab / wave | min **2** · median **6** · max **28** | tính từ `waves.json` vòng 3 |
| `Wave.indexWave` | **0 cho 686/686 dòng** — vô dụng | `Wave.csv` |

> ⚠ **Ba lỗi dữ liệu phải nêu trước khi đọc bảng:**
>
> 1. **Tên enemy không resolve được.** Mọi entry `enemies` trong `waves.json` là `"?"`
>    (**45.659 / 45.659** entry, 1 giá trị duy nhất) — bước pathID → prefab name thất bại
>    hoàn toàn. Vì vậy **không có bảng "prefab nào xuất hiện ở bao nhiêu wave"**.
>    Thay vào đó §2 dùng **tên spawner** (có thật) để suy ra họ enemy.
> 2. **`spawn_type` 5 và 6 KHÔNG phải boss/special.** `waves.json` gán nhãn `boss`/`special`
>    nhưng spawner tương ứng tên là `EndPoint` (672 + 14 `Endpoint`) và `StartPoint` (686).
>    Theo enum `SpawnTypes` trong `dump.cs`: `5 = EndMapPoint`, `6 = StartWavePoint`.
>    Đây là **mốc đầu/cuối wave**, không phải loại enemy.
> 3. **Spawner bị nhân đôi.** 185/282 wave có mỗi spawner xuất hiện **đúng 2 lần**; tổng
>    theo tên chỉ còn **10.498**. Mọi số trong file là **raw** — số thiết kế ≈ chia 2 (§1.3).

---

## 1. Tổng quan wave

### 1.1 Phân nhóm (nguồn: `waves.json`, tên `Wave_NNNN`)

| Nhóm | Khoảng tên | Số wave | Spawner | Median/wave |
|---|---|---|---:|---:|
| **Campaign** | `Wave_0000` – `Wave_0235` | 236 | 23.336 | 72 |
| **Boss ch1** | `Wave_7001` – `Wave_7022` | 22 | 218 | 6 |
| **Boss ch2** | `Wave_9001` – `Wave_9024` | 23 | 138 | 6 |
| `unknown` | — | 1 | 65 | 65 |
| **Tổng** | | **282** | **23.757** | 62 |

Wave `unknown` (65 spawner, median 65) không có tên `Wave_NNNN` — nhiều khả năng là
object lỗi khi export. Nó chiếm **0,3%** spawner, không ảnh hưởng kết luận.

Số `Wave_7001…7022` và `Wave_9001…9024` **trùng khít** danh sách `idWave` trong
`14-bosses.csv` (22 + 24) trừ `9016`. ⇒ Wave boss là **asset riêng, đặt tên theo `idWave`**,
không nằm lẫn trong campaign. (Đây là bằng chứng mạnh cho map `idWave ↔ prefab boss` mà vòng 1
chỉ dám đánh dấu "giả định".)

### 1.2 Vì sao wave boss chỉ có 6 spawner

`Wave_7001` (nguồn: `waves.json`):

| spawner | type | rate | speed | enemies |
|---|---|---:|---:|---|
| `Boss_1` | point | 1,0 | 0,0 | `?` |
| `Boss_1` | point | 1,0 | 0,0 | `?` |
| `StartPoint` | special | 1,0 | 0,0 | — |
| `StartPoint` | special | 1,0 | 0,0 | — |
| `EndPoint` | boss | 1,0 | 0,0 | `?` |
| `EndPoint` | boss | 1,0 | 0,0 | `?` |

⇒ Wave boss = **2 spawner `Boss_1` + 2 mốc đầu + 2 mốc cuối**, không có enemy thường.
`Wave_9002` giống hệt. Đây là lý do "bosswave" chỉ cần 6 dòng.

### 1.3 ⚠ Export **nhân đôi** spawner — đọc số phải chia 2

Kiểm tra: gom mỗi wave theo bộ `(spawner, spawn_type, rate, speed, y_spawn, radius)`.

| Kiểm tra | Kết quả |
|---|---:|
| Wave mà **mọi** spawner xuất hiện **đúng 2 lần** | **185 / 282 (65,6%)** |
| Wave có ít nhất 1 spawner lặp **số lẻ** | 51 / 282 |
| Wave có tổng spawner **lẻ** | 21 / 282 |
| Tổng spawner **theo tên, mỗi wave** (bỏ trùng) | **10.498** (44,2% của 23.757) |

Ví dụ `Wave_7001`: `Boss_1` ×2, `StartPoint` ×2, `EndPoint` ×2 — không phải 2 boss, mà là
**1 boss ghi 2 lần**.

> **Giả định:** nguyên nhân là exporter duyệt cả **prefab gốc** lẫn **instance trong scene**
> (hoặc `Call_Data` được tham chiếu 2 lần). Hệ quả:
> - Mọi con số trong `ENCOUNTERS.md` là **số raw** (đúng nguyên văn `waves.json`), **không**
>   phải số spawner thiết kế. Muốn số thiết kế ≈ **chia 2**.
> - Median thực tế ≈ **31** spawner/wave (62 / 2), không phải 62.
> - `Wave_0163` lớn nhất: **617 raw ⇒ ~309 thiết kế**.
>
> Không thể tự ý bỏ bản trùng vì 51 wave có ngoại lệ — phải đọc `Call_Data` gốc trong
> `data.unity3d` để biết bản nào là prefab.

### 1.4 Phân bố `spawn_type`

| `spawn_type` trong json | Thực chất | Số spawner | % |
|---|---|---:|---:|
| `point_range` | point-to-point range | 16.498 | 69,6% |
| `point` | điểm cố định | 4.199 | 17,7% |
| `path` | theo đường | 1.688 | 7,1% |
| `boss` | **`EndMapPoint`** (mốc cuối) | 686 | 2,9% |
| `special` | **`StartWavePoint`** (mốc đầu) | 686 | 2,9% |

Nguồn: `waves.json` + enum `SpawnTypes` (`dump.cs`).

> **Đọc ra:** 70% spawner là `point_range` — game gốc **né** việc đặt tay từng enemy, thay bằng
> dải điểm spawn. Đây là lý do 1 wave có thể có 617 spawner thật (`Wave_0163`) mà vẫn làm được.

### 1.5 Tham số spawn

| Tham số | Giá trị | Số spawner | Nghĩa |
|---|---|---:|---|
| `rate` | **1,0** | 16.173 | 1 giây/enemy |
| | 0,0 | 5.682 | spawn đồng loạt |
| | 0,5 | 1.047 | 2 giây/enemy |
| | 2,0 | 319 | 0,5 giây/enemy |
| | 6,0 | 110 | 6 giây/enemy |
| `speed` | **1,5** | 10.920 | tốc độ di chuyển chuẩn |
| | 0,0 | 7.541 | đứng yên |
| | **5,2** | 2.890 | lao nhanh (3,5×) |
| | 2,0 | 1.620 | |
| `y_spawn` | **9,6** | 15.485 | mép trên màn hình |
| | 12,0 | 4.088 | ngoài màn (vào trễ) |
| | 8,0 / 5,0 / 6,0 | 602 / 500 / 473 | spawn giữa màn (ambush) |

Nguồn: `waves.json`.

> `y_spawn = 9,6` ở 65,2% spawner ⇒ **toạ độ world của mép trên màn là 9,6**. Dùng số này để
> dựng camera orthographic: `orthographicSize = 9,6 / 2 = 4,8` nếu neo giữa, hoặc
> `size = 9,6` nếu neo dưới. Đây là thông số **duy nhất** suy ra được kích thước khung hình.

---

## 2. Danh mục enemy — suy từ tên spawner

Vì `enemies` toàn `?`, ta dùng **tên spawner** để suy ra họ enemy. **1.015 tên nhưng chỉ 53 tên gốc**
(hậu tố `(n)` là số thứ tự instance) — xem §2.4.

### 2.1 10 họ lớn nhất

| Họ (khớp theo chuỗi con của tên spawner) | Số spawner | Suy luận |
|---|---:|---|
| `CB1` | **10.934** (+ `CB15` 435) | enemy cơ bản chương 1 (biến thể `Vua`, `Cham`, `Nhanh`) |
| `Point 1` | 4.192 | điểm spawn generic (không mang tên enemy) |
| `CB09` | **1.465** | enemy bắn, tiền tố `1-`/`3-`/`4-`/`6-` + hậu tố `_Top`/`_Left`/`_Right` |
| `Path_CB3_5` | 1.130 | đường bay CB3, biến thể 5 |
| `Group` | 929 | nhóm spawner |
| `ChamNo` | 536 | enemy nổ chậm |
| `CB15` | 435 | enemy chương 1 loại 15 |
| `Point_H` | 387 | điểm spawn ngang |
| `CheckPlayerNo` | 372 | **trigger điều kiện** (kiểm tra vị trí player) |
| `KhoaPlayer` | 371 | **"khoá player"** — chặn di chuyển (cơ chế đặc biệt) |

Nguồn: `waves.json`, đếm bằng khớp chuỗi con trên `spawners[].spawner` (23.757 dòng).
`CB13` 267 · `CB14` 180 · `CB4` 60 · `CD05` 36 · `CD3_1` 277.

### 2.2 Họ đặc biệt (không phải enemy)

| Tên | Số | Chức năng suy ra |
|---|---:|---|
| `CheckPlayerNo` | 372 | kiểm tra player đã vào vùng → mới spawn |
| `KhoaPlayer` | 371 | khoá player (dùng ở wave có "cửa") |
| `Boss_1` / `Boss_2` | 90 / 52 | spawner boss (wave `7xxx`/`9xxx`) |
| `XB1` / `XB` (không phải `XB1`) | 88 / **46** | họ enemy chương 2 |
| `Trap_Move` | 18 | bẫy di động |
| `Help` | 12 | tàu cứu hộ (challenge "Rescue"/"Protect") |
| `StartPoint` | 686 | mốc **đầu** wave (`spawn_type = special`) |
| `EndPoint` + `Endpoint` | 672 + 14 | mốc **cuối** wave (`spawn_type = boss`) |

### 2.3 Mã enemy trong tên spawner vs. trong file HP

**Trong `waves.json`** có 9 mã enemy: `CB1`, `CB4`, `CB09`, `CB13`, `CB14`, `CB15`, `CD05`,
`CD3_1`, `Path_CB3_5`. **Không** mã nào khớp tên trực tiếp với `15-enemy-hp.csv` — vì
`15-enemy-hp.csv` dùng **đường dẫn instance trong prefab wave** (`Wave_0005/...`,
`Boss-37001/...`), còn đây là **tên spawner** (component đặt enemy lên màn).
> Nối "họ spawner → prefab enemy → HP" **cần resolve `Call_Data.listPrefabEnemies[i].m_PathID`**
> (xem §9) — hoặc đọc `Call_Data` bằng **AssetRipper** (giữ nguyên nested `[SerializeField]`
> mà exporter CSV bỏ qua), hoặc hook `Enemy_Controller.Awake()` bằng Frida để thấy prefab
> thật được instantiate. Xem `AI_FEASIBILITY.md` §1.7.

**Ngoài `waves.json`**, 3 mã `W2-*`/`MB-*`/`BB-*` xuất hiện ở **`Gun_Attack.csv`** và
`Boss_BodyPhysics.csv` — đây là **mini-boss/prefab riêng**, không phải spawner:

| Mã | Xuất hiện ở | Damage súng |
|---|---|---:|
| `MB-39005` | `Gun_Attack.csv`, `Boss_BodyPhysics.csv` | 330 |
| `BB-36004` | `Gun_Attack.csv` | 400 / 600 |
| `W2-30041` | `Gun_Attack.csv` (root `Wave_0005`) | – |

Nguồn: `Gun_Attack.csv` `_gameobject`, `Boss_BodyPhysics.csv` `_gameobject`.

### 2.4 Quy luật spawn — **48 archetype**, không phải 1.015 cấu hình

Tên spawner có dạng **`TênGốc (n)`**; `(n)` chỉ là **số thứ tự instance**, không mang cấu hình.
Bỏ hậu tố: **1.015 tên → 53 tên gốc**, trừ **5 marker** còn **48 archetype spawner thật**.

Mỗi archetype có bộ tham số **gần như hằng số** — đây là quy luật, không phải đặt tay:

| Archetype | Số lần | `spawn_type` | `rate` | `y_spawn` |
|---|---:|---|---|---|
| `CB1 Nhanh` (nhanh) | 4.622 | point_range **100%** | **1,0 × 4.622/4.622** | **9,6 × 4.618** |
| `Point 1` | 4.192 | point 2.536 · point_range | 1,0 2.536 · 0,0 1.656 | 12,0 × 2.262 |
| `CB1 Vua` (vua) | 2.951 | point_range **100%** | **1,0 × 2.951/2.951** | **9,6 × 2.945** |
| `CB1 Cham` (chậm) | 1.487 | point_range **100%** | **1,0 × 1.487/1.487** | **9,6 × 1.487** |
| `6-CB09_Left` | 1.238 | point_range | 0,0 × 1.172 | 9,6 × 1.238 |
| `CB1` | 1.150 | point_range | 0,0 × 953 | 12,0 × 880 |
| `Path_CB3_5` | 1.130 | path **100%** | 0,5 × 571 | 9,6 × 1.114 |
| `Group` | 929 | point_range | 0,0 × 929 | 0,0 × 605 |
| `ChamNo` | 536 | point_range | 1,0 × 536 | 9,6 × 528 |
| `CB15` | 435 | point_range | 0,0 × 359 | 0,0 × 269 |
| `Point_H` | 387 | point **100%** | 0,0 × 387 | 12,0 × 387 |
| `CB1 Ban Vua` | 304 | point_range | 1,0 × 304 | 9,6 × 304 |

Nguồn: `waves.json`, tính bằng cách bỏ `\s*\(\d+\)$` khỏi `spawners[].spawner`.

> **Hệ quả cho dựng lại:** chỉ cần **48 định nghĩa archetype** + bảng vị trí, không cần
> 23.757 cấu hình. Đây là phần **tự động hoá được gần hết**.

### 2.5 Prefab enemy thật: **92** (52 thường + 39 boss + 1 MB)

Đếm theo **root** của `_gameobject` trong `Enemy_Datas.csv` (bỏ sub-object `Gun5`/`HP`/`Child2`):

| Họ | Prefab | Dải id | Vai trò |
|---|---:|---|---|
| `CB` | **26** | 30001–30060 | enemy thường (chương 1) |
| `CD` | **13** | 31002–31016 | enemy thường |
| `GD` | **4** | 33002–33005 | enemy thường |
| `XB` | **4** | 34003–34006 | enemy thường |
| `BB` | **3** | 36001–36004 | enemy thường |
| `H` | **2** | 38001–38002 | enemy thường |
| **Tổng thường** | **52** | | |
| `Boss` | **39** | 37001–39021 | boss |
| `MB` | **1** | 39005 | mini-boss |
| **Tổng** | **92** | | |

> ⚠ **Đính chính:** con số **690 GameObject** ở `BALANCE.md` là **mọi object** trong prefab
> enemy (súng, hitbox, object con, hiệu ứng) — **không** phải 690 loại enemy. Số loại là **92**.

### 2.6 ✅ Đã resolve — enemy thật trong wave (pipeline vòng 3)

> **Nguồn:** nhánh `arena/ef6b75ef-…` commit `61d5385` (`docs/conclusions.md` #8).
> Pipeline chạy lại đã resolve được `listPrefabEnemies` → **không còn `"?"`**.
> Số dưới đây **thay thế** mọi câu "chưa biết enemy trong wave" ở các mục trước.

| Chỉ số | Giá trị |
|---|---:|
| Wave | **282** (236 campaign + 45 boss + 1 lỗi) |
| Spawner (đã dedup) | **11.093** |
| **Entry enemy** | **22.462** — **0** giá trị `"?"` |
| **Prefab enemy khác nhau** | **109** |
| Entry enemy / wave | min **2** · median **63** · max **603** |
| **Prefab khác nhau / wave** | min **2** · median **6** · max **28** |

Phân bố 109 prefab theo họ:

| Họ | Số prefab | Ghi chú |
|---|---:|---|
| `Boss-` | **39** | dùng trong **45** wave boss (`70xx`/`90xx`) |
| `CB-300xx` | **33** | enemy thường — họ lớn nhất |
| `CD-310xx` | **15** | enemy thường |
| `W2-300xx` | **6** | biến thể |
| `XB-340xx` | **5** | |
| `GD-33xxx` · `BB-36xxx` | **4** · **4** | |
| `H-380xx` | **2** | |
| `W1-300xx` | **1** | |

12 prefab xuất hiện nhiều nhất:

| Prefab | Số entry | Prefab | Số entry |
|---|---:|---|---:|
| `CB-30003` | 2.283 | `CB-30002` | 985 |
| `CB-30024` | 1.800 | `XB-34001` | 757 |
| `CB-30015` | 1.738 | `CB-30016` | 606 |
| `CB-30001` | 1.520 | `CB-30023` | 603 |
| `CB-30012` | 1.411 | `CD-31002` | 591 |
| `CB-30022` | 1.391 | | |

> **5 prefab phổ biến nhất chiếm 39,0% tổng entry** — độ đa dạng thật rất thấp.
> Đây là lý do một bản clone chỉ cần **~10–15 prefab enemy là đủ cảm giác**.

> `> Nhận định (mức B):` trần nội dung enemy là **109 prefab**, không phải 45.659.
> Con số 45.659 trong bản trước là **tổng số tham chiếu**, không phải số thứ phải thiết kế.

---

## 3. 10 wave tiêu biểu (số thật)

Nguồn: `waves.json`. "real" = spawner thật (đã bỏ `StartPoint`/`EndPoint`).
> ⚠ Tất cả là **số raw** — export nhân đôi spawner (§1.3), nên số thiết kế ≈ **một nửa**.

| Wave | Vị trí | Tổng | Real | point_range | point | path | Họ chiếm ưu thế |
|---|---|---:|---:|---:|---:|---:|---|
| `Wave_0000` | đầu game | 150 | 136 | 52 | 38 | 46 | `Path_CB3_5` 46 · `Group` 44 |
| `Wave_0010` | sớm | 331 | 311 | 216 | 58 | 37 | `CB1` 127 (`Vua` 77 + `Cham` 50) · `Point 1` 80 |
| `Wave_0050` | giữa ch1 | 72 | 68 | 54 | 8 | 6 | `CB1` 50 |
| `Wave_0100` | giữa | 36 | 32 | 0 | **28** | 4 | `Point 1` 28 · `Path_CB13` 4 |
| `Wave_0150` | giữa | 54 | 50 | 26 | 24 | 0 | `CB09` 26 (5 biến thể) · `KhoaPlayer` 10 · `CD05` 10 |
| `Wave_0163` | **lớn nhất** | 621 | **617** | **603** | 0 | 14 | `CB1` 538 · `Point 1` 47 |
| `Wave_0200` | muộn | 42 | 38 | 0 | 16 | **22** | `Path_CB3_5` 22 |
| `Wave_0235` | cuối campaign | 84 | 80 | 8 | 72 | 0 | `Point 1` 34 · `Point_H` 14 · `CheckPlayerNo` 14 |
| `Wave_7001` | boss ch1 | 6 | **2** | 0 | 2 | 0 | `Boss_1` 2 |
| `Wave_9002` | boss ch2 | 6 | **2** | 0 | 2 | 0 | `Boss_1` 2 |

### 3.1 Nhịp độ đọc được từ bảng

```
đầu game  : 136–311 spawner, nhiều path  → dạy né + dạy bám đường
giữa      : 32–68 spawner, chuyển sang point → dạy phản xạ
muộn      : 38–80 spawner, xuất hiện CheckPlayerNo / KhoaPlayer → dạy đọc tình huống
cuối      : 80 spawner, point áp đảo → áp lực liên tục
boss      : 2 spawner → đấu 1-1
```

> **Nghịch lý cần giữ khi clone:** số spawner **không tăng dần**. Đỉnh ở `Wave_0010` (311)
> và `Wave_0163` (617), nhưng `Wave_0100` chỉ 32. Game gốc **giảm mật độ để tăng độ khó**
> (ít enemy nhưng khó hơn) — đây là dấu hiệu thiết kế theo "intensity curve", không theo
> "số lượng tăng dần".

### 3.2 5 wave nhỏ nhất / lớn nhất (campaign)

| Nhỏ nhất | Tổng | Real | | Lớn nhất | Tổng | Real |
|---|---:|---:|---|---|---:|---:|
| `Wave_0114` | 6 | 2 | | `Wave_0163` | 621 | **617** |
| `Wave_0115` | 6 | 2 | | `Wave_0025` | 555 | 555 |
| `Wave_0016` | 8 | 2 | | `Wave_0006` | 471 | – |
| `Wave_0031` | 8 | 2 | | `Wave_0104` | 464 | – |
| `Wave_0098` | 14 | 10 | | `Wave_0198` | 451 | 451 |

Thành phần 4 wave nhỏ nhất (raw):

| Wave | Thành phần |
|---|---|
| `Wave_0114` | `Boss_2` ×2 + `StartPoint` ×2 + `Endpoint` ×2 |
| `Wave_0115` | `Path_CB3_5 (15)` ×2 + `StartPoint` ×2 + `Endpoint` ×2 |
| `Wave_0016` | `Point_CD3_1 (4)` ×2 + `StartPoint` ×3 + `EndPoint` ×3 |
| `Wave_0031` | `Path_CB3_5 (1)` ×2 + `StartPoint` ×3 + `EndPoint` ×3 |

⇒ Đây **không phải wave nghỉ** mà là **wave 1-spawner**: `0114` là **mini-boss** (`Boss_2`),
3 wave còn lại là 1 đường bay / 1 điểm spawn. Sau khi bỏ bản trùng, chúng chỉ còn **1 spawner
duy nhất** — dùng làm **nhịp nghỉ** giữa 2 wave lớn.

## 4. Map & parallax

### 4.1 Map

| Chỉ số | Giá trị | Nguồn |
|---|---:|---|
| Instance `MapController` | 396 | `MapController.csv` |
| Map duy nhất | **250** (`Map-0000` – `Map-0249`) | `MapController.csv` |
| Map bị đặt 2 lần | 146 (396 − 250) | tính |
| `isMoveEnemyLayer` | `False` **396/396** | `MapController.csv` |
| `worked` | `True` **396/396** | `MapController.csv` |
| `IndexWaveArena` / `IndexWavePvP` | 1 giá trị duy nhất (=0) | `MapController.csv` |

⇒ 250 map cho 236 wave campaign + arena/pvp → **gần 1 map/wave**. Đây là chi phí art lớn
nhất của game gốc, và là chỗ **nên cắt** ở bản clone.

### 4.2 Parallax — 5 lớp

| Lớp | Speed phổ biến | Số map | Vai trò |
|---|---|---:|---|
| 0 | **0,20** | 350 | nền xa nhất |
| | 0,40 | 28 | |
| | 0,25 | 18 | |
| 1 | **1,00** | 364 | lớp chuẩn |
| | 2,00 | 32 | lớp nhanh |
| 2 | **0,05** | 190 | tinh vân rất chậm |
| | 0,10 | 117 | |
| | 0,22 | 53 | |
| 3 | **0,50** | 348 | lớp gần |
| | 0,40 | 30 | |
| | 0,25 | 18 | |
| 4 | 0,15 / 0,35 / 0,22 | 64 / 63 / 55 | lớp gần nhất; **77 map không set** (dùng 4 lớp) |

`enemyParentMove.speed` = **0,0** ở 368 map, **1,0** ở 28 map → chỉ 7% map có nền **di chuyển
theo enemy**.

Nguồn: `MapController.csv` (`allMoveLayers[i].speed`).

> **Nhận xét:** tỉ lệ tốc độ lớp `0,05 : 0,20 : 0,50 : 1,00` = **1 : 4 : 10 : 20**.
> Đây là công thức parallax rất "chuẩn vật lý" — dùng lại tỉ lệ này cho bản clone là an toàn
> về cảm giác, không cần copy art.

---

## 5. Stage trên board map

`Stage_Behaviour` — 299 instance, mỗi cái là 1 nút stage trên `Board_Maps`.

| `stageType` | Enum | Số stage | % |
|---:|---|---:|---:|
| 0 | `Normal` | **199** | 66,6% |
| 1 | `MiniBoss` | 25 | 8,4% |
| 2 | `Boss` | 26 | 8,7% |
| 3 | `Combat` | 49 | 16,4% |

Nguồn: `Stage_Behaviour.csv` + enum `StageType` (`dump.cs`).
(`refresh` = `False` 299/299 — cờ editor.)

**Đọc ra:**
- 2/3 stage là thường, **1/3 là boss/mini-boss/combat** → mật độ nội dung đặc hơn nhiều
  game cùng loại (thường 1 boss/10 stage).
- `Boss` 26 ≈ 22 wave boss ch1 + 4 → khớp.
- `MiniBoss` 25 ⇒ có **25 trận mini-boss** trong campaign, không phải chỉ 2 như vòng 1 ghi
  (vòng 1 đếm theo atlas `MB`/`MB2`, đếm sai).

---

## 6. `Wave.csv` — vì sao không dùng được

| Field | Giá trị | Kết luận |
|---|---|---|
| `indexWave` | **0** cho 686/686 dòng | **vô dụng** — là giá trị runtime, không serialize |
| `startPoint` / `endPoint` | pathID ref | chỉ là con trỏ, không cho biết toạ độ |
| `_gameobject` | `Wave_0004`, `Wave_0005`… | **đây mới là nguồn duy nhất của index** |

Nguồn: `Wave.csv`.

⇒ Muốn biết thứ tự wave: **parse tên GameObject `Wave_NNNN`**, không đọc `indexWave`.
686 dòng `Wave.csv` phủ **281 GameObject `Wave_*` khác nhau** (trùng lặp vì mỗi wave có nhiều
instance trong scene — `Wave_0004` 11 dòng, `Wave_0005` 10 dòng…).

---

## 7. Công thức dựng wave (đề xuất cho bản clone)

```
1 wave:
  startPoint (mốc vào)  →  2..617 spawner  →  endPoint (mốc ra)
  mỗi spawner:
      type    ∈ {point, point_range, path}
      rate    ∈ {0; 0,5; 1; 2; 6}      giây/enemy
      speed   ∈ {0; 1; 1,5; 2; 3,5; 5,2}
      y_spawn ∈ {5; 6; 8; 9,6; 12}
      enemies = danh sách prefab (hiện chưa resolve)
```

**Target nhịp độ đề xuất** (dựa trên số đo §3):

| Giai đoạn | Real spawner/wave | rate chủ đạo | speed chủ đạo |
|---|---:|---:|---:|
| 10 wave đầu | 60–150 | 0,5 | 1,5 |
| giữa chương | 40–80 | 1,0 | 1,5–2,0 |
| cuối chương | 30–60 | 1,0 | 2,0–5,2 |
| boss | 1–3 | — | — |
| wave nghỉ | 1–2 | — | — |

---

## 8. Nguồn

`datas/waves.json` · `docs/apk-analysis/14-bosses.csv` ·
`reverse-engineering/scriptableobjects/`: `Call_Data.csv` · `MapController.csv` · `Wave.csv` ·
`Stage_Behaviour.csv` · `Spawner.csv` · `PointToPoint_Spawner.csv` · `Path_Spawner.csv` ·
`Rocket_Spawner.csv` · `AirFree_Spawner.csv` · `PinMap_Spawner.csv` ·
`Waypoints_Spawner.csv` · `MeteoriteGenerator.csv` · `PathCreator.csv`
`reverse-engineering/il2cpp/dump.cs.gz`: enum `SpawnTypes`, enum `StageType`, class `Wave`,
class `MapController`.

---

## 9. Còn thiếu / phải đoán

| # | Điều | Trạng thái | Cách xử lý |
|---:|---|---|---|
| 1 | **Enemy prefab nào trong wave nào** | **D** — 45.659 entry = `"?"` | phải chạy lại `wave_report.py` với pathID→name (cần `data.unity3d`) |
| 2 | `spawn_type` 5/6 bị đặt tên sai (`boss`/`special`) | **A — lỗi đã xác nhận** | đọc là `EndMapPoint`/`StartWavePoint` |
| 3 | `Wave.indexWave` = 0 toàn bộ | **A** | dùng tên GameObject |
| 4 | Số enemy thực tế trong 1 spawner | **D** — `count = 0` cho **23.757/23.757** (`number` không serialize); `radius` = 0,1 toàn bộ | không biết wave có bao nhiêu enemy |
| 5 | Toạ độ start/end point (world) | **D** — chỉ có pathID; `PathCreator.csv` **0 cột `points[i].x/y`** | xem `ENEMY_BEHAVIOUR.md` §2 |
| 6 | 1 wave nối wave khác thế nào | **C** — `y_spawn` + `EndPoint` gợi ý tuần tự | |
| 7 | Wave nào thuộc stage nào | **D** — `Map_Get_Datas.GetListWaves()` trong code | không map được 236 wave → 299 stage |
| 8 | `KhoaPlayer` / `CheckPlayerNo` hoạt động ra sao | **C** — suy từ tên; `Enemy_Appear.csv` chỉ có ref | cần test · `ENEMY_BEHAVIOUR.md` §6 |
| 9 | Không thấy `Wave_9016` (dù `idWave 9016` có trong `14-bosses.csv`) | **A** | boss 9016 dùng wave khác |
| 10 | 1 wave tên `unknown` (65 spawner, không thuộc `Wave_NNNN` nào) | **A** — có trong `waves.json` | ảnh hưởng 1/282 wave, 0,3% spawner |

---
