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
| **Spawner = `Call_Data` object** | **23.757** (= Σ `copies`; khớp `class-inventory.csv` 23.757) | hai nguồn độc lập |
| Dòng trong `waves.json` (đã **gộp** object trùng, mỗi dòng mang `copies`) | **11.089** (11.072 ở 281 wave có tên + 17 ở `unknown`) | `waves.json` |
| Dòng **thật** (bỏ **608** dòng mốc `StartPoint`/`EndPoint`) | **10.481** | tính từ `waves.json` |
| Tên spawner khác nhau (toàn cục) | **1.015** — *tên, không phải số component* | tính từ `waves.json` |
| Wave campaign | **236** (`Wave_0000` – `Wave_0235`) | `waves.json` |
| Wave boss ch1 | **22** (`Wave_7001` – `Wave_7022`) | `waves.json` |
| Wave boss ch2 | **23** (`Wave_9001` – `Wave_9024`, thiếu `9016`) | `waves.json` |
| Dòng cấu hình/wave | min **3** · median **28,5** · max **257** (`Wave_0163`) | tính từ `waves.json` |
| Enemy entry (tổng `listPrefabEnemies`) | **22.451** | `waves.json` |
| Archetype spawner | **48** (+5 marker) từ **53** tên gốc | §2.4 |
| Prefab enemy | **92** = 52 thường + 39 boss + 1 MB | §2.5 |
| Map | **250** (`Map-0000` – `Map-0249`) | `MapController.csv` |
| Stage trên board | **299** (Normal 199 · Boss 26 · Combat 49 · MiniBoss 25) | `Stage_Behaviour.csv` |
| Tên enemy prefab | ✅ **đã resolve** (pipeline vòng 3): **22.451** entry · **109** prefab khác nhau | `waves.json` nhánh `ef6b75ef` |
| Enemy prefab / wave | min **2** · median **6** · max **28** | tính từ `waves.json` vòng 3 |
| `Wave.indexWave` | **0 cho 686/686 dòng** — vô dụng | `Wave.csv` |

> ⚠ **Ba lỗi dữ liệu phải nêu trước khi đọc bảng:**
>
> 1. ~~**Tên enemy không resolve được.**~~ **ĐÃ SỬA (vòng 3, 23/10):** trạng thái `"?"` là của
>    **snapshot cũ**. `waves.json` hiện tại resolve **22.451 entry · 109 prefab** (bảng trên).
>    Đoạn `"?"` giữ lại chỉ để đọc báo cáo cũ — **không** phải hiện trạng.
> 2. **`spawn_type` 5 và 6 KHÔNG phải boss/special.** `waves.json` gán nhãn `boss`/`special`
>    nhưng spawner tương ứng tên là `EndPoint` (**320** + 7 `Endpoint`) và `StartPoint` (**281**).
>    Theo enum `SpawnTypes` trong `dump.cs`: `5 = EndMapPoint`, `6 = StartWavePoint`.
>    Đây là **mốc đầu/cuối wave** (tổng **608** dòng = 320 `EndPoint` + 7 `Endpoint` + 281 `StartPoint`),
>    không phải loại enemy. Kiểm chéo: `spawn_type` `boss` 327 + `special` 281 = **608** — khớp đúng.
> 3. **"Spawner" có ba cách đếm — đừng trộn** (sửa lần 3, 25/10, sau khi đối chiếu `class-inventory.csv`):
>    **object** **23.757** `Call_Data` · **dòng `waves.json`** **11.089** (gộp object trùng, mỗi dòng mang
>    `copies`) · **quân** Σ`len × copies` = **45.659** (mức **B**). Σ `copies` = 23.757 = số object ⇒
>    **hai nguồn gặp nhau**, không có "export nhân đôi".
>    ⚠ `copies` **không** có field tương ứng trong raw `Call_Data` (`number`/`rate` thôi) ⇒ *vì sao* trùng
>    thì **chưa kết luận**; chỉ kết luận **số khớp**. Bản sáng 25/10 gọi 11.089 dòng là "spawner" là **sai đơn vị**.

---

## 1. Tổng quan wave

### 1.1 Phân nhóm (nguồn: `waves.json`, tên `Wave_NNNN`)

**Ba đơn vị, đừng trộn** (đo 25/10 trên `waves.json` + `class-inventory.csv`):

- **object** = một `Call_Data` instance trong dump: **23.757** (`class-inventory.csv` cùng số);
- **dòng** = một cấu hình trong `waves.json` — export **gộp object trùng**, mỗi dòng mang `copies`:
  **11.089** dòng, và **Σ `copies` = 23.757** ⇒ hai cách đếm **gặp nhau**;
- **lượt** = `Σ copies` của một nhóm/wave = số object. 23.757 **lượt** toàn bộ chính là con số bảng cũ
  ghi ở cột "Spawner" — nên bảng cũ **không sai**, chỉ gọi tên khác đơn vị.
  ⚠ Vì vậy **11.089 là số cấu hình, KHÔNG phải số spawner**. Bản sáng 25/10 viết "11.089 dòng cấu hình" là sai.

| Nhóm | Khoảng tên | Số wave | **Dòng** | **Lượt** (`Σ copies`) | Median dòng | Median lượt |
|---|---|---|---:|---:|---:|---:|
| **Campaign** | `Wave_0000` – `Wave_0235` | 236 | 10.894 | **23.338** | 33,5 | **72** |
| **Boss ch1** | `Wave_7001` – `Wave_7022` | 22 | 109 | 218 | 3 | 6 |
| **Boss ch2** | `Wave_9001` – `Wave_9024` | 23 | 69 | 138 | 3 | 6 |
| `unknown` | — | 1 | 17 | 63 | 17 | 63 |
| **Tổng** | | **282** | **11.089** | **23.757** | 28,5 | **62** |

Cột `Lượt` khớp bảng cũ **theo từng nhóm** (boss 218 · 138) và **từng wave 9/9** — bảng dưới.
Chênh: `campaign` **−7 lượt**, `unknown` **+7** so với bảng cũ, vì hai snapshot khác nhau
(§17 `DATA_SYNC`). **Tổng không đổi** — ví dụ: tổng khớp mà nội dung đã đổi.

| Wave | Dòng (mới) | `Σ copies` (mới) | Bảng cũ ghi |
|---|---:|---:|---:|
| `Wave_0000` | 42 | **150** | 150 |
| `Wave_0010` | 190 | **331** | 331 |
| `Wave_0050` | 36 | **72** | 72 |
| `Wave_0100` | 18 | **36** | 36 |
| `Wave_0150` | 27 | **54** | 54 |
| `Wave_0163` | 257 | **622** | 622 |
| `Wave_0200` | 21 | **42** | 42 |
| `Wave_0235` | 42 | **84** | 84 |
| `Wave_7001` | 3 | **6** | 6 |

**Kiểm tự động (`AQ5`): 9/9 wave khớp** `Σ copies` = số bảng cũ — chạy `tools/verify-claims.py`.

Wave `unknown` (17 dòng · 63 lượt) không có tên `Wave_NNNN` — nhiều khả năng là
object lỗi khi export. Nó chiếm **0,2 %** dòng, không ảnh hưởng kết luận.

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

### 1.3 ⚠ Hai spawner **cùng tên** không chắc là một — **đừng chia 2**

> **Sửa 25/10 (review R2).** Bản trước khuyên *"số thiết kế ≈ chia 2"* và coi `Boss_1` ×2 là
> **một boss ghi hai lần**. **Lời khuyên đó rút lại**: cùng **tên GameObject** không chứng minh
> cùng **resource**.

**Bằng chứng cùng tên nhưng khác resource** (đã kéo về repo, `raw/early-waves/`):

| Wave | Resource normal (`root`) | Resource Chapter2 (`root`) | Cùng `resources.assets` |
|---|---|---|---|
| `Wave_0164` | `…/wave_0164__148604` | `…/wave_0164__148637` | ✅ |
| `Wave_0113` | `…/wave_0113__21468` | `…/wave_0113__21456` | ✅ |
| `Wave_0005` | `…/wave_0005__38187` | `…/wave_0005__38205` | ✅ |

⇒ Một wave **có thể** có hai prefab cùng tên ở hai **root khác nhau**; xoá một bản vì "trùng tên"
là **gộp nhầm** dữ liệu của chapter/resource khác.

**Đếm đúng phải theo identity, không theo tên:** `container key` (đường dẫn trong bundle) +
`serialized file` + **`root` pathID** + `Call_Data` component pathID. Cùng một prefab được tham chiếu
hai lần thì `Call_Data` **pathID trùng**; hai prefab khác nhau thì **pathID khác** dù tên giống.

**Kiểm `Call_Data` có bị tham chiếu 2 lần không — đo trên 14 file wave đã kéo:**

| Wave (normal) | `root` | `Call_Data` | pathID **khác nhau** | Chapter2 `root` | `Call_Data` |
|---|---:|---:|---:|---:|---:|
| `Wave_0164` | 148604 | **42** | **42** | 148637 | **42** |
| `Wave_0113` | 21468 | **91** | **91** | 21456 | **91** |
| `Wave_0005` | 38187 | **16** | **16** | 38205 | **16** |
| **cộng 3 wave** | | **149** | **149** | | **149** |

⇒ **0 component bị tham chiếu 2 lần** trong cả 14 file. `waves.json` của `Wave_0164` có **42 dòng**
= **42 `Call_Data`** (khớp tuyệt đối). Tên lặp lại (vd `Group (1)` ×2) là **hai component ở hai parent
khác nhau**, không phải một bản ghi hai lần.

**Vì sao có câu "185/282 wave mọi spawner lặp đúng 2":** **88,3 %** dòng có `copies = 2`, và cách
đọc cũ hiểu `copies` thành "dòng bị lặp". Cùng **một** dữ liệu, hai cách đọc. Còn **10.498** là số
cặp `(wave, spawner)` khác tên (nay **10.504**, chênh 6 do các dòng `unknown`) — **không** phải số dòng.

### 1.4 Phân bố `spawn_type`

| `spawn_type` trong json | Thực chất | **Dòng** | % dòng | **Lượt** | % lượt |
|---|---|---:|---:|---:|---:|
| `point_range` | point-to-point range | 7.536 | 68,0 % | **16.498** | 69,4 % |
| `point` | điểm cố định | 2.084 | 18,8 % | **4.199** | 17,7 % |
| `path` | theo đường | 861 | 7,8 % | **1.688** | 7,1 % |
| `boss` | **`EndMapPoint`** (mốc cuối: 320 `EndPoint` + 7 `Endpoint`) | 327 | 2,9 % | 686 | 2,9 % |
| `special` | **`StartWavePoint`** (mốc đầu) | 281 | 2,5 % | 686 | 2,9 % |

Cột `Lượt` **khớp đúng** dãy `16.498 / 4.199 / 1.688 / 686 / 686` mà `CROSS_BRANCH_20330d0e.md`
§3c ghi từ snapshot trước (tổng 45.659) ⇒ lại một lần nữa: **cùng dữ liệu, khác đơn vị**.

Nguồn: `waves.json` + enum `SpawnTypes` (`dump.cs`).

> **Đọc ra:** 68 % spawner là `point_range` — game gốc **né** việc đặt tay từng enemy, thay bằng
> dải điểm spawn. Đây là lý do 1 wave có thể có **257** spawner (`Wave_0163`) mà vẫn làm được.

### 1.5 Tham số spawn

Số dưới đây là **lượt** (`Σ copies`) — đơn vị cũ; cột **Dòng** là số cấu hình.

| Tham số | Giá trị | **Dòng** | **Lượt** | Nghĩa |
|---|---|---:|---:|---|
| `rate` | **1,0** | 7.741 | 16.175 | 1 giây/enemy |
| | 0,0 | 2.371 | 5.682 | spawn đồng loạt |
| | 0,5 | 532 | 1.047 | 2 giây/enemy |
| | 2,0 | 163 | 319 | 0,5 giây/enemy |
| | 6,0 | 58 | 110 | 6 giây/enemy |
| `speed` | **1,5** | 4.983 | 10.920 | tốc độ di chuyển chuẩn |
| | 0,0 | 3.599 | 7.536 | đứng yên |
| | **5,2** | 1.462 | 2.890 | lao nhanh (3,5×) |
| | 2,0 | 749 | 1.620 | |
| `y_spawn` | **9,6** | 7.428 | 15.485 | mép trên màn hình |
| | 12,0 | 1.701 | 4.088 | ngoài màn (vào trễ) |
| | 8,0 / 5,0 / 6,0 | 287 / 217 / 200 | 602 / 500 / 473 | spawn giữa màn (ambush) |

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

Nguồn: `waves.json`, đếm bằng khớp chuỗi con trên `spawners[].spawner` (**11.089** dòng).
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
> 11.089 cấu hình. Đây là phần **tự động hoá được gần hết**.

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
| Spawner (đã dedup) | **11.099** (bản `8c6da25`) |
| **Entry enemy** | **22.451** — **0** giá trị `"?"` |
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

Nguồn: `waves.json` hiện tại. "Real" = spawner thật (đã bỏ `StartPoint`/`EndPoint`).
> **25/10:** bảng này **đo lại toàn bộ**. Cột `Lượt` = đúng các số bảng cũ (150/331/622…) —
> xem lại thì bảng cũ **đếm lượt**, không đếm dòng. Cột `Real`/`point_range`/… đếm **dòng**.

| Wave | Vị trí | Dòng | Lượt | Real | point_range | point | path | Họ chiếm ưu thế |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `Wave_0000` | đầu game | 42 | **150** | 39 | 15 | 11 | 13 | `Path_CB3_5` 13 · `Group` 11 |
| `Wave_0010` | sớm | 190 | **331** | 187 | 128 | 35 | 24 | `CB1` 70 · `Point` 41 |
| `Wave_0050` | giữa ch1 | 36 | **72** | 34 | 27 | 4 | 3 | `CB1` 25 · `Path_CB3_5` 3 |
| `Wave_0100` | giữa | 18 | **36** | 16 | 0 | 14 | 2 | `Point` 14 · `Path_CB13` 2 |
| `Wave_0150` | giữa | 27 | **54** | 25 | 13 | 12 | 0 | `1-CB09_Top` 6 · `KhoaPlayer` 5 |
| `Wave_0163` | **lớn nhất** | 257 | **622** | 255 | 248 | 0 | 7 | `CB1` 217 · `Point` 24 |
| `Wave_0200` | muộn | 21 | **42** | 19 | 0 | 8 | 11 | `Path_CB3_5` 11 · `Point` 6 |
| `Wave_0235` | cuối campaign | 42 | **84** | 40 | 4 | 36 | 0 | `Point` 17 · `Point_H` 7 |
| `Wave_7001` | boss ch1 | 3 | **6** | 1 | 0 | 1 | 0 | `Boss_1` 1 · `StartPoint` 1 |
| `Wave_9002` | boss ch2 | 3 | **6** | 1 | 0 | 1 | 0 | `Boss_1` 1 |

### 3.1 Nhịp độ đọc được từ bảng

```
đầu game  : 136–311 spawner, nhiều path  → dạy né + dạy bám đường
giữa      : 32–68 spawner, chuyển sang point → dạy phản xạ
muộn      : 38–80 spawner, xuất hiện CheckPlayerNo / KhoaPlayer → dạy đọc tình huống
cuối      : 80 spawner, point áp đảo → áp lực liên tục
boss      : 2 spawner → đấu 1-1
```

> **Nghịch lý cần giữ khi clone:** số spawner **không tăng dần**. Đỉnh ở `Wave_0010` (311)
> và `Wave_0163` (**257**), nhưng `Wave_0100` chỉ **18**. Game gốc **giảm mật độ để tăng độ khó**
> (ít enemy nhưng khó hơn) — đây là dấu hiệu thiết kế theo "intensity curve", không theo
> "số lượng tăng dần".

### 3.2 5 wave nhỏ nhất / lớn nhất (campaign)

| Nhỏ nhất | Lượt | Lượt không-mốc | | Lớn nhất | Lượt | Lượt không-mốc |
|---|---:|---:|---|---|---:|---:|
| `Wave_0114` | 6 | 2 | | `Wave_0163` | **622** | **618** |
| `Wave_0115` | 6 | 2 | | `Wave_0025` | **560** | **554** |
| `Wave_0016` | 8 | 2 | | `Wave_0006` | **491** | **471** |
| `Wave_0031` | 8 | 2 | | `Wave_0104` | **467** | **463** |
| `Wave_0098` | 14 | 10 | | `Wave_0198` | **457** | **453** |

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
### 3.3 Đường cong HP theo wave — và **231/236 wave campaign có HP = 0**

Dựng bằng `prefab_joins` (map `Enemy_Datas.StartHealthPoint` về prefab gốc) × `waves.json` (quân).
Bản `cd0372d`.

| Nhóm | Wave | Tổng quân | **Tổng HP serialize** |
|---|---:|---:|---:|
| **Campaign** (`Wave_0000`–`0235`) | **236** | **45.050** | **2.440.000** |
| **Boss** (`Wave_7xxx`/`9xxx`) | **45** | **484** | **574.155.800** |
| **`unknown`** (wave không đánh số) | **1** | **125** | 0 |
| **Tổng** | **282** | **45.659** | **576.595.800** |

| Chỉ số | Giá trị |
|---|---:|
| Wave campaign có HP > 0 | **1 / 236** |
| Wave boss có HP > 0 | **45 / 45** |
| HP/wave campaign (median) | **0** |
| **HP mỗi boss instance** (trung bình) | **≈ 6,38 triệu** |
| **HP mỗi quân campaign** (trung bình) | **≈ 54** |

**Wave campaign duy nhất có HP:** `Wave_0136` — 164 quân, **2.440.000** HP.

**Vì sao 231 wave còn lại bằng 0:** HP **không** lưu trong prefab enemy thường.
`datas/enemy_hp.json` ghi rõ: *"runtime HP is scaled by `Enemy_Data_Balance` and stage"*.
⇒ **Toàn bộ độ khó của campaign do công thức runtime quyết định, không do dữ liệu thiết kế.**

> **Nhận định (mức A):** đây là con số mạnh nhất trong cả hồ sơ để chứng minh **"số liệu chết"**:
> **231 / 236 wave** có HP = **chính xác 0** trong prefab. Không phải thiếu dữ liệu — dữ liệu
> **đúng là 0** vì HP được nhân lúc chạy.
>
> Hệ quả cho clone: **không thể** dựng lại độ khó bằng cách chép HP prefab. Phải chọn **công thức**
> (HP × hệ số stage) và **calibrate bằng cảm giác**, không bằng số âm bản.
>
> **Điều kiện lật ngược:** nếu `Enemy_Data_Balance` (`GetSurvivalScore` có hằng số 1,1 · 0,2 · 0,01 —
> xem `19-il2cpp-constants.md`) chứa hệ số theo stage thì dựng lại được. Hiện mới có **hằng số**,
> chưa có **thứ tự nhân**.

**Tỷ lệ đáng chú ý:** 45 wave boss chứa **574 triệu HP**, gấp **235 lần** toàn bộ 236 wave campaign
(2,44 triệu). Nghĩa là **trận boss là nơi tiêu HP**, campaign là nơi tiêu **thời gian di chuyển**.

---

### 3.4 25 prefab **ngoài 178** — 9 đạn có va chạm + 16 vật thể gây damage

`prefab_joins` có **453 prefab gốc**, không phải 178. Phần lớn là `Wave_*` (246 container).
**25 prefab còn lại** không có `Enemy_Controller` nhưng **có `Boss_BodyPhysics`** — tức là
**vật thể có damage va chạm**, không phải enemy có AI:

| Nhóm | Prefab | `dmgFirst` | `dmgPerSec` |
|---|---:|---|---|
| Đạn có va chạm (`BLT_*`) | **9** | 0 – 3.000 | 10 – 100 |
| Mã `900xx` | **13** | 500 – **500.000** | 5 – 500 |
| `Expl-*` | **3** | 500 | 50 |

**3 vùng độc:** `Expl-91025 (Poision Zone)` · `Expl-91026` · `Expl-91027 (Poision Zone)`
— **500 first + 50/s**, `isTrigger = true` ⇒ **vùng damage theo thời gian**, đứng trong đó mất máu.

**13 mã `900xx`:** `90026 · 90043 · 90046 · 90056 · 90057 · 90058 · 90059 · 90063 · 90064 ·
90065 · 90067 · 90070 · 90071`. Các mức:
`90046` **100.000** · `90056` **500.000** (một biến thể) và 10.000 (3 biến thể) ·
`90057/58/59` **10.000 + 15/s** · `90043` 2.000 + 20/s · còn lại 500 + 5–100/s.

**Không con nào được spawn:** `listPrefabEnemies` = **45.659 phần tử, map tên 100% qua
`prefab-roots.csv`, và **0** phần tử thuộc 25 prefab này`. Trong cây transform, mỗi prefab là
**root đơn độc** (1 node, không cha) — không nằm trong prefab `Wave_*` nào.

> **Nhận định (mức B):** đây là **vật thể do boss hoặc script sinh ra lúc chạy**, không phải
> nội dung wave. Bằng chứng trực tiếp: `MB12_Director` có `idWallBltL = 80177` ·
> `idWallBltR = 80178` — trùng họ `BLT_*` trong nhóm này.
>
> **Điều kiện lật ngược:** nếu `900xx` xuất hiện trong `Enemy_Destroy`/`Enemy_BurstBulletWhenDie`
> (chưa đọc) thì chúng là **mảnh vỡ khi enemy chết**, không phải hazard đặt sẵn.

⚠ **Con số 178 prefab "toàn bộ enemy" phải ghi kèm:** 178 là **prefab có `Enemy_Controller`**.
Tổng prefab gốc **453**; 25 trong số đó **gây damage mà không có AI**.

### 3.5 `copies` — **22.451 entry khai báo → 45.659 "quân" nếu `copies` là số bản sao**

Mỗi spawner có field **`copies`** (số bản sao của chính spawner đó). Đây là field **quyết định
quy mô** mà các bảng trước bỏ qua:

| | Số |
|---|---:|
| Phần tử `listPrefabEnemies` (khai báo) | **22.451** |
| **× `copies` = quân thực tế** | **45.659** |
| Hệ số phóng | **2,03×** |
| Dòng có `copies = 2` | **9.793 / 11.089 = 88,3 %** |
| Quân đến từ dòng `copies > 1` | **43.189 = 94,6 %** |
| Quân đến từ dòng `copies = 1` | **2.470 = 5,4 %** |

Dải `copies`: 1 (**793**) · 2 (**9.793**) · 3 (199) · 4 (200) · 6 (16) · 10 (13) → **max 76**.

> **Nhận định (mức A):** **94,6% quân địch đến từ `copies`, không phải từ danh sách prefab.**
> Ai clone mà đọc `listPrefabEnemies` rồi spawn 1 lần sẽ ra **đúng một nửa** số quân của game.
>
> ⚠ **Hạ xuống mức B (25/10)** vì **không kiểm được nguồn của `copies`**: `Call_Data` trong raw
> (`raw/early-waves/*.json.gz`) chỉ có `number` (0 ở 42/42 component của `Wave_0164`) và `rate`,
> **không** có field `copies`; `copies` do exporter của nhánh dữ liệu sinh ra. Báo cáo `54` bên đó
> cũng ghi *"không coi `copies` trong `datas/waves.json` là số đợt"*. ⇒ `45.659` chỉ đọc được là
> "quân **nếu** `copies` = số bản sao"; muốn chắc phải xem exporter hoặc giải `bytes_base64`.
>
> **Điều kiện lật ngược:** nếu `copies` là **số làn song song** (nhiều đường bay) chứ không phải
> số bản sao, thì tổng quân vẫn 45.659 nhưng phân bố không gian khác. `spawn_type` của spawner
> `copies > 1` sẽ phân biệt (chưa đo).

### 3.6 Wave boss **không chỉ có boss** — 90 boss + 90 turret + 304 enemy thường

45 wave boss cộng lại **484 quân**, chia làm 3 tầng:

| Thành phần | Số | Mỗi wave |
|---|---:|---:|
| `Boss-*` | **90** | **2,0** |
| `CD-31002` (turret) | **90** | **2,0** |
| **`CB-30015`** (enemy thường) | **304** | **6,8** |

⇒ **Mỗi wave boss = 2 boss + 2 turret + ~7 enemy thường.** Đây **không** phải màn đấu boss thuần
— nó là wave hỗn hợp có boss ở giữa.

`CB-30015` là enemy thường phổ biến thứ 2 toàn game (**3.740** lần spawn) và **304/484 = 62,8%**
quân trong wave boss. Nó là **enemy hộ vệ mặc định của boss**.

> **Nhận định (mức B):** turret `CD-31002` xuất hiện **đúng 90 lần = 2 per wave**, không lệch
> wave nào ⇒ được **đặt cứng theo boss**, không phải ngẫu nhiên. Điều kiện lật ngược: nếu
> wave boss nào cũng có 2 turret nhưng **vị trí khác nhau** thì chúng là phần thiết kế màn,
> không phải thuộc tính boss.

### 3.7 Nhịp độ: **mỗi wave 11,4 s** và **76% roster ra mắt trong 30 wave đầu**

Hai con số quyết định nhịp game, đo trên `waves.json` bản `4539709`.

**a) Thời lượng spawn mỗi wave** — `t = len(enemies) × copies × rate`, lấy **spawner dài nhất**
trong wave (vì các spawner chạy song song):

| Nhóm | Wave | Median | Mean | Max | Min |
|---|---:|---:|---:|---:|---:|
| Campaign | 236 | **11,4 s** | 16,1 s | **108,0 s** | 2,0 s |
| Cộng dồn | 236 | — | — | **63,5 phút** | — |

Phân bố (11 bin, tổng **236**): **≤ 10 s: 85** · **10–19 s: 107** · 20–29 s: 17 ·
30–59 s: **12** · 60–69 s: **8** · ≥ 70 s: **7** (đuôi dài = wave có spawner `rate` lớn).

Cộng **6,4 s bay vào** (`y_spawn` 9,6 ÷ `speed` 1,5) ⇒ một wave điển hình
**≈ 18 s** trước khi tính thời gian bắn hạ.

⚠ **Đánh giá thấp:** **2.373 spawner có `rate = 0`** ⇒ `t = 0`. Nếu `rate = 0` nghĩa là "spawn
tức thời toàn bộ", thời lượng thật **ngắn hơn**; nếu là "spawn mỗi khung hình", nó **dài hơn**.
Chưa phân giải được từ dữ liệu.

**b) Đường cong giới thiệu enemy** — wave đầu tiên mỗi prefab xuất hiện:

| Cửa sổ wave | Loại enemy **mới** |
|---|---:|
| **0 – 19** | **51** |
| 20 – 39 | 3 |
| 40 – 59 | 1 |
| 60 – 79 | 0 |
| 80 – 99 | 2 |
| 100 – 119 | 1 |
| 120 – 139 | 9 |
| 140 – 159 | 0 |
| 160 – 179 | 2 |
| 180 – 199 | 1 |

⇒ **53 / 70 loại (76%) ra mắt trong 30 wave đầu** = **12,7% đầu campaign**. Chỉ **3 loại** ra mắt
sau wave 150.

> **Nhận định (mức A):** game **dạy gần hết roster trong 1/8 đầu** rồi khai thác bằng **tổ hợp lại**,
> không bằng enemy mới. Clone rải enemy mới suốt 236 wave sẽ **lệch nhịp** rõ rệt.
>
> **Đã kiểm điều kiện lật ngược:** bỏ `Wave_0000` (42 spawner / 883 quân — không phải wave khởi
> đầu điển hình) rồi đếm lại: **vẫn 70 · 53 · 76% · 3** — **không đổi số nào**.
>
> **Cái giá phải trả khi clone:** 51 loại enemy phải xong **trước** khi làm 200 wave còn lại;
> 200 wave sau chỉ cần **bố cục lại**, không cần art/AI mới.

**c) Cấu trúc màn trong UI:** **299 stage / 2 chapter** — `Stage_Normal` **199** ·
`Stage_Combat` **49** · `Stage_MiniBoss` **25** · `Stage_Boss` **26** (`Stage_Behaviour.csv`).
⚠ **Chưa khớp** với **281 wave** (236 campaign + 45 boss) — xem `DATA_SYNC` §7.24.

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
| 4 | Số enemy thực tế trong 1 spawner | **D** — `count = 0` cho **11.089/11.089** dòng (`number` không serialize); `radius` = 0,1 toàn bộ | không biết wave có bao nhiêu enemy |
| 5 | Toạ độ start/end point (world) | **D** — chỉ có pathID; `PathCreator.csv` **0 cột `points[i].x/y`** | xem `ENEMY_BEHAVIOUR.md` §2 |
| 6 | 1 wave nối wave khác thế nào | **C** — `y_spawn` + `EndPoint` gợi ý tuần tự | |
| 7 | Wave nào thuộc stage nào | **D** — `Map_Get_Datas.GetListWaves()` trong code | không map được 236 wave → 299 stage |
| 8 | `KhoaPlayer` / `CheckPlayerNo` hoạt động ra sao | **C** — suy từ tên; `Enemy_Appear.csv` chỉ có ref | cần test · `ENEMY_BEHAVIOUR.md` §6 |
| 9 | Không thấy `Wave_9016` (dù `idWave 9016` có trong `14-bosses.csv`) | **A** | boss 9016 dùng wave khác |
| 10 | 1 wave tên `unknown` (65 spawner, không thuộc `Wave_NNNN` nào) | **A** — có trong `waves.json` | ảnh hưởng 1/282 wave, 0,3% spawner |

---
