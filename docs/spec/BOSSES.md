# BOSSES — boss và enemy: dữ liệu đọc được, và chỗ còn trống

> Phạm vi: **enemy + boss** của WindWings: Space Shooter (`com.Wind.wings.Space.Shooter` 1.3.118,
> Unity 2022.3.62f3, IL2CPP). Súng của tàu — kể cả drone — chỉ dùng để ra **một con số damage**,
> nên không nằm trong file này; xem `COMBAT.md` và `BALANCE.md`.
>
> Nguồn: `datas/waves.json` (22.462 entry), `15-enemy-hp.csv` (**981 dòng**, bản vòng 3),
> `Enemy_Datas.csv` (981), `Enemy_Movement.csv` (981), `Boss_BodyPhysics.csv` (251),
> `class-inventory.csv` (677 class). Bản cũ `docs/apk-analysis/` chỉ có **800 dòng** cho các bảng
> `Enemy_*` — mọi số dưới đây lấy từ **bản vòng 3**.
>
> Quy ước mức: **A** đo được · **B** suy ra · **C** ước lượng · **D** chưa đọc.
> Mục cuối: **Còn thiếu / phải đoán**.

---

## 0. Tóm tắt

| Chỉ số | Giá trị | Mức |
|---|---:|---|
| Tổng wave | **282** | A |
| — campaign (thường) | **237** | A |
| — boss | **45** (22 ở `70xx` · 23 ở `90xx`) | A |
| Wave boss **có** boss | **45 / 45** | A |
| Wave thường **có** boss | **0 / 237** | A |
| Prefab boss | **39** | A |
| Tổng HP 39 boss | **206.167.000** trên **206** bộ phận | A |
| Prefab enemy thường | **70** | A |
| **Entry** enemy thường (đếm list) | **22.417 / 22.462** | A |
| **Entry** boss (đếm list) | **45 / 22.462** | A |
| **Quân** enemy thường (× `copies`) | **45.569 / 45.659** | A |
| **Quân** boss (× `copies`) | **90 / 45.659** | A |
| Boss có vùng va chạm | **27 / 39** | A |
| Prefab enemy thường có HP > 0 | **2 / 70** (20.000 mỗi cái) | A |
| Class enemy/boss **chưa đọc** | **87 class / 7.036 instance** | D |

> **Điều đáng chú ý nhất:** boss chiếm **0,2%** tổng entry nhưng **45/45** wave của nó là wave riêng.
> Nghĩa là boss **không phải một enemy to hơn** — nó là **một loại màn khác**, xác nhận đúng cách
> hiểu "boss là màn riêng". Ngược lại, enemy thường gần như toàn bộ nội dung: **45.569 quân** trong 45.659.
>
> **Hai đơn vị đếm, đừng lẫn:** *entry* = số phần tử trong `listPrefabEnemies` (**22.462**);
> *quân* = entry × `copies` (**45.659**). `BOSSES.md` và `GAMEPLAY.md` §1.3.1 luôn ghi rõ đang dùng đơn vị nào.

---

## 1. Hai tầng nội dung tách hẳn nhau

| | Campaign | Boss |
|---|---:|---:|
| Số wave | **237** | **45** |
| Quân mỗi wave | 4 – 951 · median **152** | **4** (44/45) = 2 boss + 2 turret |
| Thành phần | 1–28 prefab thường | đúng **1 prefab boss** + `CD-31002` |
| Khoảng id | `Wave_00xx` – `Wave_6xxx` | `Wave_7001`–`Wave_7022` · `Wave_9001`–`Wave_9024` |
| Enemy trong wave | 1–28 prefab thường | **đúng 1 prefab boss** |
| Entry trung bình | ~95 | ~1 |
| Boss trong wave | **0** | **1** |

Mã hoá id rất gọn: `7001`–`7022` = **22 wave boss đợt 1**, `9001`–`9024` = **23 wave boss đợt 2**.
Không có wave `70xx/90xx` nào thiếu boss, và không wave thường nào chen boss.

**Ngoại lệ duy nhất:** `Wave_7011` — 46 spawner / **308 quân**, gồm `CB-30015` **×304** + `Boss-37011` ×2 + `CD-31002` ×2.
Đây là wave boss duy nhất có quân thường, và cũng là wave boss "dày" nhất.

> **Nhận định (mức A):** đây là **hai vòng tiến trình độc lập** (mã `37xxx` đi với `70xx`, mã `39xxx`
> đi với `90xx` — xem §2), không phải một danh sách boss trải đều. Điều kiện lật ngược: nếu
> `Stage_Behaviour` (299 instance, có `stageType`) cho thấy `70xx` và `90xx` nằm chung một chuỗi stage
> thì phải đọc lại thành một vòng.

---

## 2. Bảng đầy đủ 39 boss

`Bộ phận` = số dòng HP dưới cùng một prefab (mỗi bộ phận có thanh máu riêng).
`Vùng va chạm` = số `Boss_BodyPhysics` gắn trên prefab đó. `dmgFirst` = damage lần chạm đầu,
`dmg/s` = damage mỗi giây khi đứng trong vùng.

| Boss | Wave | Bộ phận HP | Tổng HP | HP lớn nhất | Vùng va chạm | dmgFirst | dmg/s |
|---|---|---:|---:|---:|---:|---|---|
| `Boss-37001` | `Wave_7001` | 3 | 1.225.000 | 1.000.000 | 1 | 500 | 50 |
| `Boss-37002` | `Wave_7002` | 5 | 1.320.000 | 900.000 | 1 | 500 | 5 |
| `Boss-37003` | `Wave_7003` | 6 | 3.500.000 | 1.500.000 | — | — | — |
| `Boss-37004` | `Wave_7004` | 5 | 4.204.000 | 4.000.000 | 4 | 500 | 1.000 |
| `Boss-37005` | `Wave_7005` | 1 | 3.900.000 | 3.900.000 | 1 | 500 | 100 |
| `Boss-37006` | `Wave_7006`, `Wave_7007` | 23 | 7.060.000 | 2.200.000 | 10 | 500 · 1.500 · 5.000 | 50 · 100 · 150 |
| `Boss-37008` | `Wave_7008`, `Wave_7020` | 1 | 1.100.000 | 1.100.000 | 1 | 500 | 100 |
| `Boss-37009` | `Wave_7009` | 2 | 4.200.000 | 4.200.000 | — | — | — |
| `Boss-37010` | `Wave_7010` | 2 | 4.500.000 | 4.500.000 | 2 | 500 | 15 |
| `Boss-37011` | `Wave_7011` | 1 | 4.000.000 | 4.000.000 | — | — | — |
| `Boss-37012` | `Wave_7012`, `Wave_7021` | 2 | 2.800.000 | 2.800.000 | — | — | — |
| `Boss-37013` | `Wave_7013` | 2 | 4.300.000 | 4.300.000 | 1 | 500 | 15 |
| `Boss-37014` | `Wave_7014` | 3 | 5.500.000 | 3.100.000 | 2 | 500 · **9.000.000** | 15 · 50 |
| `Boss-37015` | `Wave_7015` | 2 | 4.350.000 | 4.350.000 | — | — | — |
| `Boss-37016` | `Wave_7016` | 3 | 5.580.000 | 3.870.000 | 1 | 1.500 | 100 |
| `Boss-37017` | `Wave_7017`, `Wave_7022` | 2 | 4.300.000 | 4.300.000 | — | — | — |
| `Boss-37018` | `Wave_7018` | 2 | 5.000.000 | 5.000.000 | 7 | 1.000 · 1.500 | 100 |
| `Boss-37019` | `Wave_7019` | 2 | 5.000.000 | 5.000.000 | 1 | 1.500 | 100 |
| `Boss-39001` | `Wave_9001` | 5 | 470.000 | 200.000 | — | — | — |
| `Boss-39002` | `Wave_9002` | 4 | 1.680.000 | 680.000 | 4 | 500 | 15 |
| `Boss-39003` | `Wave_9003` | 1 | **0** | **0** | 1 | 500 | 5 |
| `Boss-39004` | `Wave_9004` | 5 | 1.480.000 | 800.000 | — | — | — |
| `Boss-39005` | `Wave_9005` | 10 | 6.590.000 | 1.600.000 | 1 | 500 | 10 |
| `Boss-39006` | `Wave_9006` | 18 | 13.480.000 | 1.500.000 | — | — | — |
| `Boss-39007` | `Wave_9007` | 2 | 648.000 | 648.000 | — | — | — |
| `Boss-39008` | `Wave_9008` | 2 | 3.000.000 | 3.000.000 | 1 | 1.500 | 100 |
| `Boss-39009` | `Wave_9009` | 7 | 6.900.000 | 2.500.000 | — | — | — |
| `Boss-39010` | `Wave_9015` | 22 | 8.550.000 | 600.000 | — | — | — |
| `Boss-39011` | `Wave_9011` | 6 | 7.200.000 | 2.900.000 | 3 | 1.500 · 1.800 | 100 |
| `Boss-39012` | `Wave_9012` | 4 | 7.200.000 | 2.800.000 | 8 | 500 · 2.500 | 15 · 30 · 180 |
| `Boss-39013` | `Wave_9013` | 4 | 7.700.000 | 3.000.000 | 1 | 1.500 | 100 |
| `Boss-39014` | `Wave_9014` | 4 | 8.030.000 | 3.000.000 | 2 | 1.000 · 5.000 | 30 · 200 |
| `Boss-39015` | `Wave_9019` | 6 | **14.500.000** | 3.500.000 | 2 | 1.000 | 80 |
| `Boss-39016` | `Wave_9010` | 2 | 600.000 | 600.000 | 1 | 500 | 10 |
| `Boss-39017` | `Wave_9017`, `Wave_9024` | 21 | 13.500.000 | 3.200.000 | 11 | 200 · 500 · **500.000** | 30 · 50 · 100 |
| `Boss-39018` | `Wave_9018`, `Wave_9023` | 4 | 8.200.000 | 3.200.000 | 2 | 1.500 · 5.000 | 100 · 300 |
| `Boss-39019` | `Wave_9020` | 4 | 8.200.000 | 3.200.000 | 1 | 1.500 | 100 |
| `Boss-39020` | `Wave_9021` | 4 | 8.200.000 | 3.200.000 | 1 | 1.500 | 100 |
| `Boss-39021` | `Wave_9022` | 4 | 8.200.000 | 3.200.000 | 1 | 1.500 | 100 |

**Tổng: 39 boss · 206 bộ phận · 206.167.000 HP.**

Đọc bảng này ra vài thứ:

- **`Boss-37007` không tồn tại.** Dải `7001`–`7022` có 22 wave nhưng chỉ 18 prefab `37xxx`; ba wave
  `7020`/`7021`/`7022` dùng lại `37008`/`37012`/`37017`. Tổng **39 prefab ↔ 45 wave** khớp vì **6 boss
  xuất hiện 2 lần**: `37006`, `37008`, `37012`, `37017`, `39017`, `39018`.
- **`Boss-39016` nằm ở `Wave_9010`**, không phải `90016`. Tương tự `39010` ở `Wave_9015`,
  `39015` ở `Wave_9019`. Mã prefab **không** bằng số wave — đừng suy ra thứ tự từ số.
- **`39019`–`39021` giống nhau tuyệt đối:** 4 bộ phận · 8.200.000 HP · 3.200.000 max · dmg 1.500/100.
  Đây là **ba biến thể cùng một khuôn**, chỉ khác sprite/skin.
- **HP dao động 0 → 14.500.000**, chênh **~30 lần** giữa boss yếu nhất có HP và mạnh nhất. Không có
  đường cong đều: `39001` (470.000) đứng ngay sau `37019` (5.000.000).

> **Nhận định (mức B):** thứ tự tiến trình **không** theo số prefab. `37001`→`37019` tăng dần rõ
> (1,2M → 5,0M), nhưng `39001` (0,47M) thấp hơn cả `37002` — nên `39xxx` là **vòng mới**, không phải
> phần tiếp theo của `37xxx`. Điều kiện lật ngược: nếu `Stage_Behaviour.stageType` xếp `39001` sau
> `37019` trong cùng một chuỗi thì phải đọc lại là một vòng.

---

## 3. Va chạm — cơ chế "đâm vào boss thì mất máu"

`Boss_BodyPhysics` (251 instance) là **vùng gây sát thương** gắn trên thân boss. 4 cột quyết định:

| Cột | Giá trị | Nghĩa |
|---|---|---|
| `isTrigger` | **249 / 251 = True** | gần như toàn bộ là vùng trigger, không phải vật lý cứng |
| `isFirstTrigger` | **110 / 251 = True** | có/không có damage "chạm lần đầu" |
| `dmgFirst` | 500 (114 lần) · 1.000 (33) · 1.500 (22) · 200 (20) | damage lần chạm đầu |
| `dmgPerSec` | 50 (77) · 100 (60) · 15 (31) · 30 (24) | damage mỗi giây khi ở trong vùng |
| `layerMask.m_Mask` | **256** ở **251 / 251** | layer 8 — chỉ va với đúng layer người chơi |

**Toàn bộ 251 vùng dùng chung một layer mask = 256.** Nghĩa là cơ chế va chạm **không phân biệt
boss nào** — mọi boss đâm vào đều xử lý giống nhau, chỉ khác **con số**.

Hai giá trị bất thường cần soi lại:

| Boss | Giá trị | Vì sao đáng ngờ |
|---|---|---|
| `Boss-37014` | `dmgFirst = 9.000.000` | gấp **6.000 lần** mức phổ biến 1.500; lớn hơn cả tổng HP của chính nó (5,5M) |
| `Boss-39017` | `dmgFirst = 500.000` | gấp **333 lần** mức 1.500; cùng boss còn có 200 và 500 bình thường |

> **Giả định (mức C):** hai con số này là **sát thương tuyệt đối "chết ngay"** đặt bằng tay cho pha
> kết liễu (hoặc lỗi nhập liệu). Chưa phân biệt được vì chưa đọc class `Boss*_AttackPhases`.
> Cần đọc `Boss14_AnimationEvents` / `Boss17_AnimationEvents` để biết vùng đó bật ở pha nào.

---

## 4. Boss thiếu gì

| Thiếu | Số | Mức |
|---|---:|---|
| Boss **không có vùng va chạm** | **12 / 39** | A |
| Boss **HP = 0** | **1 / 39** (`39003`) | A |
| Boss **1 bộ phận duy nhất** | **4 / 39** (`37005`, `37008`, `37011`, `39003`) | A |
| Boss **> 15 bộ phận** | **4 / 39** (`37006` 23 · `39010` 22 · `39017` 21 · `39006` 18) | A |
| Boss **≥ 10 bộ phận** | 5 / 39 (thêm `39005` 10) | A |

12 boss **không** có `Boss_BodyPhysics`: `37003`, `37009`, `37011`, `37012`, `37015`, `37017`,
`39001`, `39004`, `39006`, `39007`, `39009`, `39010`. Đây **không** phải lỗi ghép — `Boss_BodyPhysics`
có đủ **251/251** dòng, nên vắng là vắng thật.

`Boss-39003` có HP = 0 ở dòng duy nhất của nó, nhưng vẫn có 1 vùng va chạm (500/5). Nghĩa là nó
**không chết bằng HP** — chết bằng cơ chế khác (đếm thời gian / sự kiện / pha).

> **Giả định (mức C):** `39003` là boss "không thể giết" hoặc boss đếm ngược. Điều kiện lật ngược:
> nếu class `Boss3_*` (75 instance `Boss3_Plasma`) có trường HP thì `start_hp = 0` chỉ là giá trị mặc
> định trong prefab và HP thật do code set.

---

## 5. Enemy thường — 70 prefab, 8 họ

| Họ | Prefab | Vai trò đọc được từ dữ liệu |
|---|---:|---|
| `CB` | **33** | lao thẳng / bay theo path (`isTurret = False`) |
| `CD` | **15** | **turret** (`isTurret = True` toàn bộ) |
| `W2` | 6 | chỉ 1/6 có HP (20.000); 5 còn lại HP = 0 (xem §5.2) |
| `XB` | 5 | lao thẳng |
| `GD` | 4 | **turret** |
| `BB` | 4 | lao thẳng |
| `H` | 2 | **turret** (`H-38001`, `H-38002`) |
| `W1` | 1 | HP 20.000 |

### 5.1 Turret — 21/70 prefab, 16,7% entry

**Toàn bộ `CD` (15) + `GD` (4) + `H` (2) + 1 `W2` = 22 prefab** đều `isTurret = True`; **toàn bộ `CB`/`XB`/`BB`
`False`**. Ranh giới gần tuyệt đối — họ prefab quyết định cách di chuyển, chỉ `W2` có 1 ngoại lệ.

22 prefab turret chiếm **7.570 / 45.659 quân (16,6%)**. Nghĩa là **cứ 6 quân thì 1 đứng yên bắn**.

| `isTurret` | Prefab | Entry | % entry |
|---|---:|---:|---:|
| True | 22 | 7.570 | **16,6%** |
| False | 48 | 38.089 | 83,4% |

### 5.2 Bảy prefab `W1`/`W2` — HP 20.000, không phải "không có HP"

`W1-30031`, `W2-30032` … `W2-30037` — **7 prefab, đủ cả 7 trong ba bảng** HP + `Enemy_Datas` + movement
(mỗi prefab 1 dòng). HP: `W1-30031` = **20.000**, `W2-30037` = **20.000**, 5 cái còn lại = **0**.

⚠ **Bản nháp đầu của mục này ghi "7 prefab không có HP" — đó là lỗi regex của tôi.** Regex nhận mã
prefab `^[A-Za-z]{1,4}-\d{5}` trượt `W1-30031` vì có **chữ số trước dấu gạch**. Sửa thành
`^[A-Za-z]{1,4}\d{0,2}-\d{5}` thì đủ 7. Chi tiết ở `DATA_SYNC.md` §7.1.1.

20.000 bằng **4%** HP boss yếu nhất có HP (`39001` = 470.000) — nên đây là **vật phụ rẻ**, không phải
enemy chiến đấu thật.

> **Giả định (mức B):** `W` = **wing** (cánh/bệ phụ). Điều kiện lật ngược: nếu `Enemy_Physics`
> (981 instance, chưa đọc) cho thấy chúng có collider riêng thì là thực thể độc lập.

### 5.3 Tốc độ — chỉ 5 nấc, không phải thang liên tục

`listSpeeds[0]` đo được **981 giá trị** (mỗi instance 1 giá trị) trên 70 prefab:

| Giá trị | Số lần |
|---:|---:|
| **5,0** | 562 |
| 1,0 | 123 |
| **20,0** | 118 |
| 3,5 | 83 |
| 0,8 | 47 |
| 1,2 | 22 |

min **0,2** · median **5,0** · max **30,0**. Hai nấc `5,0` và `20,0` chiếm **680/981 (69,3%)**.

> **Nhận định (mức A):** tốc độ enemy **không** là biến liên tục để cân — nó là **lựa chọn trong vài nấc**.
> Đây là thứ dựng lại rất nhanh: 2 giá trị 5 và 20 tái tạo **69,3%** cảm giác tốc độ; thêm 1,0 và 3,5 là **90,3%**.

### 5.4 Phân bố entry — đầu dài

| Prefab | Entry | % tổng |
|---|---:|---:|
| `CB-30003` | 2.283 | 10,2% |
| `CB-30024` | 1.800 | 8,0% |
| `CB-30015` | 1.738 | 7,8% |
| `CB-30001` | 1.520 | 6,8% |
| `CB-30012` | 1.411 | 6,3% |
| `CB-30022` | 1.391 | 6,2% |
| `CB-30009` | 1.036 | 4,6% |
| `CB-30002` | 985 | 4,4% |

8 prefab đầu = **54,3%** tổng entry. `CD-31002` xuất hiện ở **281 / 282 wave** — nhiều nhất game,
nhưng chỉ 591 entry vì mỗi wave chỉ 1–2 con.

---

## 6. HP của enemy thường **không có trong prefab** — chỗ trống lớn nhất

Đây là phát hiện quan trọng nhất của file này.

`15-enemy-hp.csv` có **981 dòng**, nhưng chỉ **467 dòng có `start_hp > 0`**. Trong 467 dòng đó:

- **206 dòng thuộc 39 boss** (§2) — toàn bộ boss có HP.
- **1 dòng thuộc `MB-39005`** = **330.000** — mini-boss duy nhất có HP riêng, và **không** nằm trong wave nào.
- Phần còn lại thuộc object UI/test: `Board_FightBoss`, `Board_SelectBoss`, `CB(TEST)` (10.000.000),
  `Tab (5)`, `Parent`, `ScrollView`…

**70 prefab enemy thường trong wave: 68 prefab `start_hp = 0`, chỉ 2 prefab có HP dương**
(`W1-30031` và `W2-30037`, mỗi cái **20.000** — §5.2). Tổng HP của cả 70 prefab thường = **40.000**,
tức **0,02%** tổng HP boss (206.167.000). Nói cách khác: **dữ liệu HP trong prefab dành cho boss,
không dành cho enemy thường.**

Kiểm chéo bằng bảng khác — `Enemy_Datas.csv` (981 dòng, cùng 981 object):

| Cột | Giá trị > 0 | Nhận xét |
|---|---:|---|
| `StartHealthPoint` | **467 / 981** | trùng khít `start_hp` |
| `StartHpPoint` | **0 / 981** | toàn 0 |
| `CurrentHealthPoint` | **0 / 981** | toàn 0 (giá trị runtime, prefab để trống) |
| `IsAlive` | 2 / 981 `True` | prefab lưu trạng thái mặc định, không phải chỉ số |

Ba cột còn mang thông tin khác: `IsCaAttack` **True 524 / False 457**, `IsBringItems`, `IsInvisible`.
Nhưng **không cột nào cho HP của enemy thường**.

> **Nhận định (mức A):** HP enemy thường **không tồn tại dưới dạng dữ liệu trong prefab**. Nó được
> **tính bằng code** lúc spawn. Đây không phải "dữ liệu bị cắt" — đã kiểm hai bảng độc lập, cả hai
> đều 0, và cả hai đều đủ 981 dòng.
>
> **Điều kiện lật ngược:** nếu `MapController` (396 instance, có `IndexWaveArena`, `allMoveLayers[i].speed`)
> hoặc `Stage_Behaviour` (299, có `stageType`) có trường scale thì HP = base × scale và base nằm ở đó.

Điều này **không** chặn việc dựng lại game — `BALANCE.md` đã có DPS người chơi và HP boss. Nhưng nếu
muốn **đúng số** cho enemy thường thì phải đọc **thân hàm**: `Enemy_Health` không có field HP, nên
công thức nằm trong method `Init`/`SetUp` của nó — **dữ liệu method body chưa có** (xem `AI_FEASIBILITY.md` §1).

---

## 7. 87 class enemy/boss chưa đọc — phần "hành vi" còn nguyên

> Danh sách dưới đây là **cái gì chưa đọc**. Đánh giá **đủ/chưa đủ** và **thứ tự đọc tiếp** ở §8.

`class-inventory.csv` liệt kê **95 class** thuộc enemy/boss. Đã có CSV cho **8**.
Còn **87 class / 7.036 instance** chưa đọc lần nào:

| Instance | Class | Cho biết điều gì |
|---:|---|---|
| 1.134 | `Enemy_EfxDestroyed` | hiệu ứng khi chết (feel) |
| 981 | `Enemy_Physics` | khối va chạm, khối lượng, layer |
| 981 | `Enemy_Display` | hiển thị, hướng nhìn |
| 971 | `Enemy_Destroy` | điều kiện chết |
| 909 | `Enemy_Hp_Bar` | thanh máu — vị trí, kích thước, kiểu |
| 695 | `Enemy_Burned` | trạng thái bị đốt |
| 391 | `Enemy_LookAtPlayer` | **hướng ngắm** — quyết định cảm giác bị nhắm |
| 241 | `Enemy_CameraVibrate` | **rung camera** — feel |
| 140 | `Enemy_Stun` | choáng |
| 75 | `Boss3_Plasma` | đòn plasma boss 3 |
| 72 | `Enemy_Sync_Attack` | **bắn đồng loạt** nhiều nòng |
| 68 | `Boss_PlasmaBeam` | chùm plasma |
| 56 | `Enemy_OffObjectWhenDestroy` | tắt bộ phận khi chết |
| 51 | `Enemy_Attack` | **đòn đánh cơ bản** |
| 35 | `Enemy_Rotate` | xoay |
| 16 | `BossLaser` | laser |
| 12 | `Boss_Rocket` · `Boss8_Spawner` | rocket, gọi quân |
| **37 class / 65 instance** | `Boss*_Director` (19) · `MB*_Director` (17) · `MiniBoss1_Director` | **điều phối pha** — mỗi boss/mini-boss một class riêng |
| 3 class | `Boss19_AttackPhases` · `Boss20_AttackPhases` · `Boss21_AttackPhases` | **bảng pha tấn công** |

**Nhóm đòn đánh/pattern: 50 class / 415 instance.** Đây chính là phần trả lời "boss đánh thế nào" —
và **chưa có một dòng CSV nào**.

> **Nhận định (mức A):** phần số (HP, bộ phận, va chạm, tốc độ, turret) đã đủ để dựng lại **khuôn**.
> Phần **hành vi** (ai bắn lúc nào, pha nào, bao nhiêu đòn) **chưa đọc** — không phải không có.
> `unity_data.py` hỗ trợ danh sách class đích; thêm 87 tên này vào `TARGETS` là có CSV, không cần tool mới.

---

## 8. Kịch bản — đủ chưa

"Kịch bản" ở đây chia **7 lớp**. Mỗi lớp phải trả lời được một câu hỏi riêng, nên phải kiểm riêng.

### 8.1 Bảng kiểm 7 lớp

| # | Lớp kịch bản | Class | Instance | Đã đọc | Trạng thái |
|---:|---|---|---:|---:|---|
| 1 | **Sinh quân** (wave, spawner, list enemy) | `Call_Data` | **23.757** | **23.757** | ✅ **100%** |
| 2 | **Di chuyển** (path, speed, turret, hướng) | `Enemy_Movement` | 981 | 981 | ✅ **100%** |
| 3 | **HP** | `Enemy_Datas` | 981 | 981 | ✅ **100%** |
| 4 | **Bắn** (cadence, burst) | `Gun_Attack` | 458 | 458 | ✅ **100%** |
| 5 | **Đạn** (đường bay, delay) | `Bullet_Linearly` · `Bullet_SineWave` | 186 + 2 | 188 | ✅ **100%** |
| 6 | **Va chạm boss** (`dmgFirst`, `dmgPerSec`) | `Boss_BodyPhysics` | 251 | 251 | ✅ **100%** |
| 7 | **Va chạm enemy thường** | `Enemy_Physics` | **981** | **0** | ❌ **0%** |
| 8 | Ngắm hướng | `Enemy_LookAtPlayer` | 391 | 0 | ❌ 0% |
| 9 | Điều kiện chết | `Enemy_Destroy` | 971 | 0 | ❌ 0% |
| 10 | Bị đốt · choáng · rung camera | `Enemy_Burned` 695 · `Enemy_Stun` 140 · `Enemy_CameraVibrate` 241 | 1.076 | 0 | ❌ 0% |
| 11 | Đòn đánh theo nhịp | `Enemy_Attack` 51 · `Enemy_Sync_Attack` 72 | 123 | 0 | ❌ 0% |
| 12 | **Pha boss** | 37 `*_Director` (65) + `Boss19/20/21_AttackPhases` (3) | **68** | 0 | ❌ **0%** |
| 13 | Đòn đặc biệt boss | `Boss3_Plasma` 75 · `Boss_PlasmaBeam` 68 · `BossLaser` 16 · `Boss_Rocket` 12 · `Boss8_Spawner` 12 · `Boss6_Sword` 8 · `Boss3_Flamer` 6 | 197 | 0 | ❌ 0% |

**Đọc 6/13 lớp, nhưng 6 lớp đó là 6 lớp "số".** 7 lớp còn lại — toàn bộ phần **hành vi** — chưa đọc một dòng.

### 8.2 Kiểm tính toàn vẹn của lớp 1 — khớp tuyệt đối

`waves.json` được dựng bằng cách gộp `Call_Data` theo wave rồi **dedupe** các spawner trùng cấu hình
(`copies` = số lần lặp). Nếu dedupe sai, tổng `copies` sẽ hụt.

| Phép kiểm | Kết quả |
|---|---:|
| Tổng `copies` trong `waves.json` | **23.757** |
| `Call_Data` trong `class-inventory.csv` | **23.757** |
| **Lệch** | **0** |
| Spawner duy nhất (sau dedupe) | 11.093 |
| Tổng quân (`len(enemies) × copies`) | **45.659** |

> **Nhận định (mức A):** lớp sinh quân **không mất một object nào**. Con số 45.659 quân không phải ước lượng —
> nó khớp với tổng `copies` đúng bằng số `Call_Data` thực có trong file. Đây là lớp duy nhất trong 7 lớp
> có được phép kiểm chéo như vậy, và nó **qua**.
>
> Lưu ý: `Call_Data.csv` (CSV rời) chỉ có **1.200** dòng vì bị `MAX_CSV_ROWS` cắt — nhưng
> `waves.json` do `wave_report.py` sinh (không cap) nên **đủ 23.757**.

### 8.3 Chỗ đứt lớn nhất: một class quyết định 85,8% khối lượng

Với mỗi prefab, muốn "chạy được kịch bản" thì cần biết **nó gây damage bằng cách nào**. Có 3 nguồn:
súng (`Gun_Attack`), va chạm (`Boss_BodyPhysics` / `Enemy_Physics`), hoặc đòn script (`Boss*_*`).

| Nhóm | Prefab | Entry | % entry |
|---|---:|---:|---:|
| Có **súng** đọc được | 40 | 6.425 | **14,1%** |
| Có **va chạm boss** đọc được | 30 | 104 | 0,2% |
| **Không có nguồn damage nào đọc được** | **54** | **39.174** | **85,8%** |

**88,5%** trong số đó là họ **`CB`** (34.663 / 39.174 entry = **75,9%** toàn game). `CB` là họ **lao thẳng**
(`isTurret = False` 100%), **27/33 prefab `CB` không có `Gun_Attack`** — nghĩa là chúng gây damage
bằng **va chạm**, và component va chạm của enemy thường chính là `Enemy_Physics` — **chưa đọc**.

> **Nhận định (mức A):** nếu dựng game ngay từ dữ liệu hiện có, **76% quân địch sẽ bay vào mà không
> gây sát thương**, vì `Enemy_Physics` (981 instance) chưa được đọc. Đây **không** phải "không có dữ liệu":
> class nằm trong `class-inventory`, có 981 instance, và `Boss_BodyPhysics` cho thấy dạng field sẽ gặp
> (`dmgFirst`, `dmgPerSec`, `isTrigger`, `layerMask`).
>
> **Điều kiện lật ngược:** nếu `Enemy_Physics` không có trường damage (chỉ là collider), thì damage của
> `CB` nằm ở `Enemy_Attack` (51) hoặc `Enemy_DestroyAttack` (2) — khi đó phải đọc nhóm đó trước.

### 8.4 Boss: 5 con chưa có đòn đánh nào

| Nguồn đòn | Số boss |
|---|---:|
| Súng **và** va chạm | **14** |
| Chỉ súng | 7 |
| Chỉ va chạm | 13 |
| **Không có cả hai** | **5** |

5 boss đó: `37011` · `37015` · `37017` · `39001` · `39007` — tổng **13.770.000 HP = 6,7%** HP boss toàn game.
Với 5 con này, **100% đòn đánh** nằm trong `*_Director` / `AttackPhases` / `Boss*_Plasma` — tất cả **chưa đọc**.

Boss có đòn đặc biệt **được đặt tên riêng** (đọc được từ tên class, chưa đọc nội dung):

| Class | Instance | Gợi ý cơ chế |
|---|---:|---|
| `Boss3_Plasma` | 75 | đạn plasma boss 3 |
| `Boss_PlasmaBeam` | 68 | chùm plasma |
| `BossLaser` | 16 | laser |
| `Boss_Rocket` | 12 | rocket |
| `Boss8_Spawner` | 12 | gọi quân |
| `Boss6_Sword` | 8 | chém |
| `Boss3_Flamer` | 6 | phun lửa |

### 8.5 Kết luận: đủ hay chưa

| Câu hỏi | Trả lời | Căn cứ |
|---|---|---|
| Kịch bản **sinh quân** đủ chưa? | ✅ **Đủ** | 23.757/23.757 = 100%, lệch 0 |
| Kịch bản **di chuyển** đủ chưa? | ✅ **Đủ** | 981/981, 109/109 prefab |
| Kịch bản **bắn** đủ chưa? | ✅ Đủ **cho 40 prefab** | 458/458 `Gun_Attack` |
| Kịch bản **gây damage của enemy thường** đủ chưa? | ❌ **Chưa** | `Enemy_Physics` 981 chưa đọc → 85,8% entry |
| Kịch bản **pha boss** đủ chưa? | ❌ **Chưa** | 68 instance Director/Phases chưa đọc |
| Kịch bản **chết / trạng thái** đủ chưa? | ❌ **Chưa** | `Enemy_Destroy` 971 · `Enemy_Burned` 695 · `Enemy_Stun` 140 |

**Tóm một câu:** phần **"bao nhiêu, ở đâu, đi đường nào, bắn nhanh cỡ nào"** đã đủ và kiểm chéo được.
Phần **"gây damage bằng gì, lúc nào, theo pha nào"** mới đọc được 14,1% khối lượng.

### 8.6 Thứ tự đọc tiếp — xếp theo số, không theo cảm giác

| Ưu tiên | Class | Instance | Mở khoá |
|---:|---|---:|---|
| **1** | `Enemy_Physics` | **981** | **85,8% entry** (damage va chạm của `CB`) |
| 2 | `Enemy_LookAtPlayer` | 391 | hướng ngắm của enemy bắn |
| 3 | `Enemy_Destroy` | 971 | điều kiện chết, drop |
| 4 | `Enemy_Burned` · `Enemy_Stun` | 695 · 140 | trạng thái hiệu ứng |
| 5 | 37 `*_Director` + 3 `AttackPhases` | 68 | pha boss (5 boss chưa có đòn nào) |
| 6 | `Enemy_Attack` · `Enemy_Sync_Attack` | 51 · 72 | nhịp bắn nhiều nòng |
| 7 | `Boss3_Plasma` … `Boss3_Flamer` | 197 | đòn đặc biệt từng boss |

> #1 chỉ là **một class**. Thêm tên nó vào `TARGETS` của `unity_data.py` rồi chạy lại là có,
> không cần tool mới — cùng đường với 8 class đã đọc được.

---

## 9. Còn thiếu / phải đoán

| # | Thứ | Mức | Ghi chú |
|---:|---|---|---|
| 1 | **HP enemy thường** (68/70 prefab = 0) | **A** (không có trong prefab) | nằm trong thân hàm `Enemy_Health.Init`; method body chưa có |
| 2 | **Hành vi 87 class** enemy/boss | **D** | 7.036 instance chưa đọc; xếp thứ tự ở §8.6 — #1 `Enemy_Physics` mở khoá 85,8% entry |
| 3 | **Bảng pha** `Boss19/20/21_AttackPhases` | **D** | 3 instance nhưng mỗi cái có thể là cả một bảng đòn |
| 4 | **37 class Director** (65 instance) | **D** | 19 `Boss*` + 17 `MB*` + `MiniBoss1`; "nhạc trưởng" của từng boss |
| 5 | Ý nghĩa `dmgFirst = 9.000.000` / `500.000` | **C** | 2 giá trị bất thường; cần đọc animation event |
| 6 | `Boss-39003` chết bằng gì | **C** | HP = 0 nhưng có vùng va chạm |
| 7 | 7 prefab `W1`/`W2` là gì | **B** | HP 20.000 (2 cái) hoặc 0; nghi là cánh/bệ phụ |
| 8 | Thứ tự tiến trình `37xxx` vs `39xxx` | **B** | HP không tăng đơn điệu giữa hai dải |
| 9 | `Stage_Behaviour.stageType` cho 299 stage | **A** (đã có) | Normal 199 · MiniBoss 25 · Boss 26 · Combat 49 — **chưa** nối vào 282 wave |
| 10 | Số đòn mỗi boss, nhịp bắn | **D** | `Boss4_ExplosionTimer` (155) có `timeMin`/`timeMax` 0–6,8 s nhưng chỉ 1 boss |

> Không có mục nào ở đây là "không thể". #1 cần **method body** (IL2CPP), #2–#4 và #10 cần **thêm class
> vào `TARGETS`** rồi chạy lại, #5–#8 là **chưa chốt cách đọc**, #9 đã có dữ liệu nhưng chưa nối.
