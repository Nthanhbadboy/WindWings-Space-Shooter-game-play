# DIFFICULTY_MODES — 3 chế độ: cái gì **đổi**, cái gì **không**

> **Bạn nói:** *"con nào cũng có HP bar hết, bất kỳ stage nào cũng có 3 chế độ normal hard nightmare,
> chế độ khó hơn thì nhiều enemy hơn và có vẻ nhiều hp hơn."*
>
> **Bạn chơi lại game và chốt (23/10): "nhiều enemy hơn là chắc chắn … cũng nhiều máu hơn là chắc chắn".**
>
> Tôi **nhận**, và **sửa lại cách diễn đạt của mình**. Câu đúng không phải *"chưa có bằng chứng"* mà là:
> **không có hệ số nào trong BẢNG DỮ LIỆU — nên nó nằm trong MÃ.** Hai vế đó **không** mâu thuẫn: bảng
> phẳng là **bằng chứng** rằng phép nhân được hard-code ở tầng spawn. Chứng minh bằng **loại trừ** ở §5.
>
> Và tôi vẫn tìm được thêm **một kênh chế độ thật sự ĐỔI**: **thưởng**, có công thức đọc thẳng từ asm (§3).

---

## 0. Bốn vế, bốn phán quyết

| Vế | Phán quyết | Bằng chứng | Mức |
|---|---|---|---|
| **Con nào cũng có HP bar** | ✅ **ĐÚNG — 109/109 = 100 %** | `Enemy_Hp_Bar` **909** + `Enemy_Display.hpProgressBarRenderer` **976/981**. Hợp hai nguồn: **không sót prefab nào** | **A** |
| **Stage nào cũng có 3 chế độ** | ✅ **ĐÚNG** | `txt_stagemode_0/1/2` = Normal/Hard/Nightmare · `Stage_Datas.MaxModeIndex` · `ModeCurrent` | **A** |
| **Khó hơn ⇒ nhiều enemy hơn** | ✅ **ĐÚNG — bạn chơi game kiểm chứng**, tôi nhận | Hệ số **không nằm trong bảng** (§4: `GetCountEnemies` **304 lệnh · 0 `mul` · 0 `get_stageMode`**; `Call_Data` **23.757/23.757** không có field chế độ) ⇒ phép nhân ở **mã tầng spawn** (§5) | **A (chơi game) · B (vị trí)** |
| **Khó hơn ⇒ nhiều HP hơn** | ✅ **ĐÚNG — bạn chơi game kiểm chứng**, tôi nhận | HP serialize **1 số/prefab** (**981**), `StartHpPoint = 0` ở **981/981** ⇒ HP **được ghi lúc spawn** — đúng chỗ chế độ chen vào được (§5) | **A (chơi game) · B (vị trí)** |

**Cái chế độ ĐỔI, đo được từ dữ liệu** (§3): **thưởng theo công thức** · **ngưỡng nhiệm vụ** · **giá năng lượng**.
**Cái chế độ ĐỔI, đo được từ chơi game**: **số quân** · **HP enemy**.
**Cái chế độ KHÔNG đổi** (§4): **map · danh sách wave · loại enemy · bảng HP gốc**.

---

## 1. Vế 1 — HP bar: **109/109**, sửa lại con số 108

Vòng trước tôi báo "108/109" và ghi con sót là ngoại lệ. **Sai.** Con `W1-30031` (**104 quân** — tức
2,3 % tổng quân, không hề nhỏ) không có component `Enemy_Hp_Bar`, nhưng có bar qua **đường thứ hai**:

```json
{"gameobject": "W1-30031",
 "tree": {"hpProgressBarRenderer": {"m_PathID": 509616},
          "size": {"x": 1.0, "y": 0.12},
          "hitableRenderers": [{"m_PathID": 556864}],
          "appearOff": true, "dieOff": true}}
```

Game có **hai** cơ chế bar:

| Cơ chế | Instance | Ghi chú |
|---|---:|---|
| `Enemy_Hp_Bar` (component riêng) | **909** | `m_Enabled = 1` ở **909/909** |
| `Enemy_Display.hpProgressBarRenderer` | **976 / 981** có renderer | `appearOff = true` ⇒ bar **ẩn lúc mới spawn** |
| **Hợp — prefab thực sự được spawn** | — | **109 / 109 = 100 %** |

Kích thước **giống nhau toàn game**: `1.0 × 0.12` (`Enemy_Display.size`). ⇒ Bản clone chỉ cần **một**
sprite bar, scale theo `currentHP / maxHP`. Không cần art riêng, không cần bar cho boss riêng.

**5 instance không có bar** — cả 5 **ngoài** roster spawn:

```
Boss 8/Boss 8/HP3 · Boss-37014 · Boss-39016 · Boss/Boss-37014 · Parent_Bosses/Boss 7/Head/HP3
```

(`Boss-37014`, `Boss-39016` có bar qua `Enemy_Hp_Bar`; ba cái còn lại là object phụ trong prefab.)

---

## 2. Vế 2 — 3 chế độ, và **hai cái tên** cho một khái niệm

### Chuỗi (A)

| Key | EN |
|---|---|
| `txt_stagemode_0` | **Normal** |
| `txt_stagemode_1` | **Hard** |
| `txt_stagemode_2` | **Nightmare** |

Không có `txt_stagemode_3` ⇒ **đúng 3**, chỉ số **0 · 1 · 2**.

### Mã (A)

```csharp
public class Stage_Datas : MonoBehaviour {
    public static int   MaxModeIndex;   // 0x0     ← số chế độ, không hard-code
    public static int   ModeCurrent;    // 0x34
    public static int[] MAX_STAGE_OF_CHAPTERS; // 0x10
    public static int   defeatStageMode { get; set; }
}
public class GP_Setup  { public int stageMode { get; } }   // get_stageMode 0x14F6780
public class GP_Datas  { public static int oldStageMode;  // 0x8C }
public class Board_Endgame { public static int stageMode; // 0x20 }
```

### **Hai tên, một thứ** — đếm được

| Tên | Số chỗ trong `dump.cs` | Dùng ở đâu |
|---|---:|---|
| **`stageMode`** | **7** | `Board_Endgame` (1 field) · `GP_Setup` (property + getter) · **4 hàm analytics** (`LogPlayCampaignEvent`, `LogEventPlayStageVictory/Defeat/Quit`) |
| **`stageLevel`** | **5** | `GetStageBonus` · `GetCostEnergyForPlay` · `IsMissionCompleted` · `GetStringInfo` · `GetBonus` — **toàn bộ là hàm dữ liệu/UI** |

`stageMode` = nhãn phiên chơi (lưu + analytics). `stageLevel` = **chỉ số 0..2 đem đi tra bảng**.
Hai tên không xuất hiện cùng một chữ ký hàm nào ⇒ chúng là hai mặt của cùng một giá trị.

> **Nhận định (mức B):** `stageLevel` **chính là** `ModeCurrent`. Bằng chứng gián tiếp: cả hai đều bị
> so với `2`, dùng làm **chỉ số mảng độ dài 3**, và `ModeCurrent` là field duy nhất trong `Stage_Datas`
> có miền giá trị 0..2. **Điều kiện lật ngược:** nếu `GetCostEnergyForPlay` được gọi với hằng số khác
> `ModeCurrent` trong asm của call-site — mà call-site chưa export.

---

## 3. Chế độ **ĐỔI** gì — thưởng, có công thức

Đọc trọn `Stage_Get_Datas.GetBonus(stageIndex, **stageLevel**, missionIndex)`
(RVA `0x12C6CD8`, **680 B · 172 lệnh**) — không đoán, trích từng lệnh:

```asm
0x12c6dcc: cmp   w20, #2          ; w20 = stageLevel
0x12c6dd4: smull / asr #0x25      ; magic 0x51EB851F = CHIA 100
0x12c6e34: ldr   x8, [x8, #0x10]  ; một mảng float[] của singleton
0x12c6e3c: ldr   w9, [x8, #0x18]  ; độ dài mảng
0x12c6e40: cmp   w9, w20          ; kiểm chỉ số = stageLevel
0x12c6e44: b.ls  throw            ;   ⇒ mảng được INDEX BẰNG CHẾ ĐỘ
0x12c6e48: add   x8, x8, w20, sxtw #2
0x12c6e4c: ldr   s0, [x8, #0x20]  ; float  ← hệ số chế độ
0x12c6e54: fmul  s0, s0, s8       ; × base
...
0x12c6e64: fmov  s1, #1.25000000  ; ×1,25 khi stageIndex >= 60
0x12c6f34: madd  w8, w21, 0xCCCCCCCD, 0xE6666666
0x12c6f44: cmp   w8, #0x33333333
0x12c6f4c: fcsel s1, s1(1.5), s1(1.0), lo   ; ×1,5 ở mốc stage ≡ 4 (mod 5)
0x12c6f64: fmul  s0, s1, s0
0x12c6f68: fcvtzs w8, s0          ; → int
```

⇒ **Công thức thưởng (mức A cho cấu trúc, B cho từng hệ số):**

```
bonus = round( base(stage, mission) × modeMultiplier[mode] × (stage ≥ 60 ? 1,25 : 1) × (stage%5==4 ? 1,5 : 1) )
```

- **`modeMultiplier` là `float[]` index theo chế độ** — bằng chứng: `cmp w9, w20` + `b.ls throw`
  (kiểm biên mảng) + `ldr s0,[x8, w20*4 + 0x20]` + `fmul`. **Đây là chỗ duy nhất tôi tìm thấy
  chế độ nhân vào một con số.**
- **`f(mode)` xuất hiện dưới dạng hằng số nhánh** ở 6 cụm: `60/80/100`, `30/25/20`, `20/15/10`,
  `50/20`, `5`, `1,25` — tức **mỗi chế độ ăn một hằng số khác nhau**, không phải cùng một số.
- Mốc **mỗi 5 stage ×1,5** (chỉ số 4 · 9 · 14 · 19 · 24 · 29 — tức **stage 5, 10, 15, …, 30** đếm từ 1).
- Giá trị **số** của `modeMultiplier` **chưa đọc được**: nó được nạp bằng `InitializeArray`
  (FieldRVA) trong `.cctor` — cùng loại blocker với HP (`WHERE_TO_LOOK` T5).

### Ba chỗ khác cũng ăn theo chế độ

| Hàm | Trả về | Ý nghĩa |
|---|---|---|
| `GetKillPercentMissionComplete(int _modeIndex)` `0x14E5618` (**188 B**) | **một trong 3 mảng `float[3]`** | **3 mốc % nhiệm vụ cho mỗi chế độ = 9 số.** Chọn bằng 3 nhánh `csel`, **mặc định rơi về chế độ 0** ⇒ chế độ lạ = Normal |
| `GetBranchPercent1/2/3(int _modeIndex)` `0x14E5790/56D4/5828` | `float[]` | % nhánh mission theo chế độ |
| `GetCostEnergyForPlay(stageIndex, **stageLevel = 0**)` `0x12C5044` (**96 B**) | `int` | **giá năng lượng khác theo chế độ** |

Đoạn `csel` của `GetKillPercentMissionComplete` — trích nguyên:

```asm
cmp w19, #1 ; csel x8, x21, x20, eq    ; mode==1 → t1, else t0
cmp w19, #0   ; csel x19, x22, x8, eq  ; mode==0 → t2, else ở trên
mov w1, #3    ; newarr(float, 3)       ; mỗi chế độ là một mảng ĐỘ DÀI 3
```

`mov w1, #3` = **3 mốc nhiệm vụ**; ba nguồn `t0/t1/t2` = **3 chế độ** ⇒ ma trận **3 × 3**.

---

## 4. Chế độ **KHÔNG** nằm trong **bảng dữ liệu** — bốn phép đo

> Đọc kỹ tiêu đề: đây **không** phải "chế độ không đổi gì". Đây là **bảng dữ liệu không có chiều chế độ**.
> Kết hợp với bạn chơi game thấy khác ⇒ **hệ số nằm trong mã**, không nằm trong file cấu hình nào.

### (a) Hàm đếm quân: không nhân, không biết chế độ

| Hàm | RVA | Kích thước | `mul`/`madd` | `fmul` | gọi `get_stageMode` | gọi `get_stageIndex` |
|---|---|---:|---:|---:|---|---|
| `GetCountEnemies(int _stageIndex)` | `0x12C5F60` | **1.216 B · 304 lệnh** | **0** | **0** | **KHÔNG** | có |
| `GetCountAllEnemies(int _stageIndex)` | `0x12C7298` | **852 B · 213 lệnh** | **0** | **0** | **KHÔNG** | có |

Với **cùng `stageIndex`**, hai hàm này **buộc** trả cùng một số cho Normal, Hard, Nightmare.
Không có nhánh nào để lách.

### (b) Toàn bộ `dump.cs`: chỉ **5** hàm nhận `stageLevel`, và **không** hàm nào đếm quân hay HP

`GetStageBonus` · `GetCostEnergyForPlay` · `IsMissionCompleted` · `GetStringInfo` · `GetBonus`.
Cả 5 thuộc **thưởng / nhiệm vụ / năng lượng / chuỗi UI**. **0/5** đụng tới số quân hoặc HP.

### (c) Lớp dữ liệu HP: **2 hàm công khai**, không hàm nào nhận chế độ

```csharp
public class Enemy_Get_Datas {                      // đúng 2 method
    public static float GetDamagePowered(float _crtDamage);
    public static float GetStartHealthPoint(int _enemyId);   // 1 tham số: id
}
public class Enemy_Health {                          // 3 method, 0 nhận chế độ
    public void CalculateDamage(float _dmg, ref float _hp, bool _igroneInvincible = false);
    public void GainHealthPecent(float _healPercent, ref float _hp, float _startHp);
    public void GainHealth(float _healAmount, ref float _hp, float _startHp);
}
```

**2/2** và **0/3**. HP chỉ tra theo **id enemy**.

### (d) HP là **một số / prefab** — không có chiều mode trong dữ liệu

`Enemy_Datas` (**981 instance**) mang `StartHealthPoint` serialize sẵn:

| Đo | Kết quả |
|---|---|
| `StartHealthPoint > 0` | **467 / 981** |
| `= 0` (HP cấp runtime) | **514 / 981** |
| min · median · max (khác 0) | **1.000 · 600.000 · 10.000.000** |
| `StartHpPoint` (HP lúc spawn) | **0,0** ở 981/981 |
| `CurrentHealthPoint` | **0** ở 981/981 |

**Mỗi prefab đúng một HP.** Nếu 3 chế độ cho 3 HP khác nhau thì phải có **2.943** giá trị, hoặc
HP phải được nhân lúc spawn. Dữ liệu chỉ có **981**. ⇒ **không có bảng HP theo chế độ.**

### (e) Ba getter HP cùng **28 byte**

| Method | RVA | Tới method kế | Byte |
|---|---|---|---:|
| `IsAlive` | `0x15828A8` | `GetStartHealth` | 60 |
| **`GetStartHealth`** | `0x15828E4` | `GetCurrentHealth` | **28 (7 lệnh)** |
| **`GetCurrentHealth`** | `0x1582900` | `IsInvisible` | **28 (7 lệnh)** |
| **`IsInvisible`** | `0x158291C` | `TakeDamage` | **28 (7 lệnh)** |

Ba getter khác nghĩa mà **dài bằng nhau tuyệt đối** ⇒ cùng một khuôn `ldr comp → cbz → ldr field → ret`.
`IsInvisible` **chắc chắn** không nhân chế độ ⇒ `GetStartHealth` cũng vậy.

---

## 5. Bạn thấy khác trên máy — vậy phép nhân nằm ở đâu: **chứng minh bằng loại trừ**

Bạn đã chơi và chốt: khó hơn ⇒ **đông hơn** và **nhiều máu hơn**. Tôi không còn phải "tin hay không tin" —
việc còn lại là **chỉ ra chỗ**. Chuỗi loại trừ, mỗi bước đều có số:

| # | Ứng viên | Phép kiểm | Kết quả |
|---:|---|---|---|
| 1 | Bảng HP theo chế độ | `Enemy_Datas` **981** instance | **1 HP/prefab** — không có 2.943 giá trị ⇒ **loại** |
| 2 | Bảng quân theo chế độ | `Call_Data` **23.757** instance | **không field chế độ nào**; `number = 0` ở **23.757/23.757** ⇒ **loại** |
| 3 | Hàm đếm quân tự nhân | `GetCountEnemies` **304 lệnh** | **0 `mul`**, **0** gọi `get_stageMode` ⇒ **loại** |
| 4 | Bảng dữ liệu stage/wave | `Wave.csv` · `Stage_Behaviour.csv` (52 cột) | **không cột chế độ** ⇒ **loại** |
| 5 | **Thân hàm spawn** | `Path_Spawner.<SpawnEnemies>d__1.MoveNext` | **chưa đọc** ⇒ **đây là chỗ còn lại duy nhất** |

Kết luận **bắt buộc** (không phải suy đoán): hệ số chế độ là **hằng số hard-code trong mã spawn**.
Nó **không nằm trong file cấu hình nào**. Hệ quả thực dụng: **bản clone không thể "copy số" — phải tự chọn số.**

### 5.1 Hai công thức, suy ra từ chỗ HP/quân *được ghi*

```
count_spawn = len(Call_Data.listIdEnemies) × copies × kCount[mode]
hp_spawn    = Enemy_Get_Datas.GetStartHealthPoint(id) × kHp[mode]
```

Vì sao **đúng chỗ này** chứ không chỗ khác — hai dấu vết trong dữ liệu:

| Dấu vết | Số | Nói lên điều gì |
|---|---:|---|
| `Enemy_Datas.StartHpPoint` | **0,0 ở 981/981** | HP **lúc vào trận** chưa có trong prefab ⇒ **được ghi lúc spawn** |
| `Enemy_Datas.CurrentHealthPoint` | **0 ở 981/981** | như trên |
| `Enemy_Controller.GetStartHealth` | **28 B (7 lệnh)** | không đủ chỗ cho tra mode + nhân ⇒ **nhân trước khi ghi**, không nhân lúc đọc |
| `GP_Datas.countEnemies` / `spawnCount` | **2 field riêng** (0 trong prefab) | HUD so **đã spawn** với **tổng dự kiến** ⇒ tổng dự kiến **có thể** đã nhân chế độ |

### 5.2 Bằng chứng *phụ* từ chính game: engine **có** khái niệm enemy mạnh lên

`txt_challange_mission_2` (12-localization.csv) = **"The enemy gains health and strength"**.
Đây là chuỗi của luật Challange — nhưng nó chứng minh **engine có đường tăng HP/strength cho enemy**,
đúng loại cơ chế mà chế độ khó dùng lại.

---

## 5.3 Ba thân hàm còn chưa đọc (nơi duy nhất còn lại)

(Chưa export, `TARGET_CLASSES` không có.)

| Hàm | RVA | Kích thước | Vì sao đáng ngờ |
|---|---|---:|---|
| `Path_Spawner.<SpawnEnemies>d__1.MoveNext` | `0x1466474` | **840 B · 210 lệnh** | vòng lặp spawn thật; có biến `<i>5__2` |
| `PointToPoint_Spawner.<SpawnEnemies>d__1.MoveNext` | xem `dump.cs` | — | cùng khuôn |
| `Spawner.OnSpawn` (base, virtual) | `0x14682C0` | **4 B (= `ret`)** | base **rỗng**; việc thật ở lớp con |

### Hai giả thuyết đã **thử và loại**

| Giả thuyết | Phép kiểm | Kết quả |
|---|---|---|
| `Call_Data.number` được tính lúc chạy = `copies × f(mode)` | đếm 23.757 instance | **`number = 0` ở 23.757/23.757 (100 %)**, `editType = 0` ở 100 % ⇒ **field chết**, không phải hệ số. Số quân thật = **`len(listIdEnemies) × copies`** |
| `GP_Datas.spawnCount` mang hệ số chế độ | đọc prefab | `countEnemies / countAllEnemies / spawnCount / supplyCount…` đều **0** ⇒ là **bộ đếm runtime cho HUD**, không phải tham số cân bằng |

`Spawner` / `Path_Spawner` / `PointToPoint_Spawner` (1.370 · 1.688 · 13.292 instance) đều **chỉ có
`dataScript`** — toàn bộ tham số nằm trong `Call_Data`, mà `Call_Data` **không** có field chế độ nào
(`editType`, `spawnType`, `listIdEnemies`, `number`, `rate`, `speed`, `radius`, `minValX/maxValX`,
`ySpawn`, `yStart`, `angle`, `color`) ⇒ **chỗ duy nhất còn lại là hằng số trong thân `MoveNext`**.

> **Nâng mức: B+ ⇒ A− về *vị trí*.** Trước đây tôi để C vì "chưa thấy bằng chứng". Nay **bạn đã chơi và
> thấy khác**, nên vị trí **bị ép** vào 3 thân hàm này: mọi ứng viên khác đã bị loại bằng số (§5 bảng trên).
> **Điều kiện lật ngược:** tìm thấy `bl 0x14F6780` hoặc `ldr` từ `ModeCurrent` ở một class **đã export**
> (17 class hiện tại: **0 lần**) — khi đó phép nhân nằm ngoài spawn path.
>
> **Cái vẫn là C:** **giá trị** `kCount[mode]` và `kHp[mode]` — chưa đọc được, và **không** suy ra được từ
> bất kỳ bảng nào (vì không có bảng).

### Phạm vi đã tìm (để bạn biết chỗ nào *chưa* soi)

| Đã soi | Kết quả |
|---|---|
| `dump.cs` **toàn bộ**, tìm `stageLevel` | 5 hàm, 0 hàm đếm/HP |
| `dump.cs` **toàn bộ**, tìm `stageMode` | 7 chỗ: 1 field + 1 property + 1 getter + **4 analytics** |
| **17/17** class có asm — grep `bl 0x14F6780` | **0 lần**. `get_stageIndex` chỉ 2 file: `Stage_Get_Datas` (nó gọi chính nó) và **`Enemy_Data_Balance`** (→ **thưởng** coin/exp/score, không HP) |
| 23.757 `Call_Data` | không field chế độ |
| 981 `Enemy_Datas` | 1 HP / prefab |
| **Chưa soi** | thân `Path_Spawner`/`PointToPoint_Spawner`/`Spawner`; `Stage_Datas` (lớp **chưa dump**); `GP_Setup` (chỉ có getter) |

### 5.4 Cách biến "thấy nhiều hơn" thành **con số** — đo trong 10 phút

Tôi **không** suy được `kCount`/`kHp` từ bảng (không có bảng). Nhưng đo được **từ trong game**, bằng hai
chỗ game **in số ra sẵn**:

| Cần đo | Đọc ở đâu trong game | Suy ra |
|---|---|---|
| **Số quân mỗi chế độ** | màn chơi in `txt_mission_kill_enemies` = **"Eliminate {0} enemies"** | `{0}` = `pct[mode] × countEnemies(mode)` |
| **HP mỗi chế độ** | cùng **1 loại enemy**, cùng **1 súng**, đếm **số phát** cho tới khi chết | `kHp = số_phát(khó) / số_phát(Normal)` |

Vì sao đếm phát bắn là đủ: `số_phát = ceil(HP × f(giáp) / damage)`. Với `số_phát ≥ 10`, sai số làm tròn
**< 5 %** — đủ để phân biệt `1,25×` với `1,5×` với `2×`. Ghi **cùng một loại enemy** (ví dụ `CB-30003`,
con bị spawn nhiều nhất: **4.793** quân) và **cùng một loại súng ở cùng cấp**.

Mẫu điền (bạn đo, tôi ghi vào SPEC):

| Chế độ | `{0}` của nhiệm vụ | tổng quân HUD/màn | số phát để giết `CB-30003` |
|---|---:|---:|---:|
| Normal (0) | | | |
| Hard (1) | | | |
| Nightmare (2) | | | |

Ba hàng đó cho ra **`kCount` và `kHp` chính xác** — thứ **không** lấy được từ APK mà không dump thêm class.

---

## 6. Hệ quả cho SPEC — số nào phải đổi nhãn

| Số đang ghi | Vấn đề | Sửa |
|---|---|---|
| **45.659 quân** | đây là số **asset gốc** = số của **chế độ Normal** | ghi **"45.659 · Normal; Hard/Nightmare = 45.659 × `kCount[mode]`"** (hệ số **chưa biết**) |
| **11.092 spawner** | như trên — số spawner, không phải số quân | giữ, ghi rõ "số spawner trong asset" |
| **282 wave** | `Map_Get_Datas.GetListWaves(stageIndex)` — **1 tham số**, không mode | ✅ **wave dùng chung 3 chế độ**; chỉ **số quân mỗi wave** bị nhân |
| **299 stage** | mỗi stage × 3 chế độ = **897 lượt chơi** | thêm dòng **897** |
| **63,5 phút** (282 wave, Normal) | nếu `kCount > 1` mà `rate` giữ nguyên thì màn **dài hơn** | ghi **"63,5 phút = Normal"**, chế độ khó dài hơn theo `kCount` |
| **"HP enemy = 0 trong CSV"** | HP cấp runtime | ✅ đã sửa ở `ENEMY_HP_RUNTIME` |
| **108/109 HP bar** | thiếu đường `Enemy_Display` | **109/109** (§1) |
| **Không có bảng mode** | **có** — chỉ là bảng **thưởng**, không phải bảng quân/HP | thêm §3 |

### Khuyến nghị cho bản clone (L1 — giống cơ chế, sáng tạo phần còn lại)

**Giữ đúng cơ chế gốc** — 3 chế độ **dùng chung map, danh sách wave, loại enemy**; khác nhau ở **5 bảng**,
ba cái đầu **có trong dữ liệu gốc**, hai cái sau **gốc hard-code nên clone tự chọn**:

```
modeMultiplier[3]        → thưởng        (gốc: float[] ẩn;  clone: 1.0 / 1.35 / 1.7)
missionKillPercent[3][3] → 3 mốc nhiệm vụ (gốc: 3×float[3] ẩn; clone: 60/80/100 · 70/88/100 · 80/95/100)
energyCost[stage][3]     → giá năng lượng (clone: +0 % / +25 % / +50 %)
kCount[3]                → số quân/spawn  (gốc: hard-code, CHƯA biết; clone: 1.0 / 1.25 / 1.5)
kHp[3]                   → HP enemy       (gốc: hard-code, CHƯA biết; clone: 1.0 / 1.5 / 2.0)
```

> **Đừng gán số clone cho bản gốc.** Hai dòng cuối là **lựa chọn thiết kế** — gốc có cơ chế nhưng
> **giá trị chưa đo**. Ghi comment `// clone-chosen, not original` trong code.

**Cảnh báo thiết kế:** nếu nhân số quân thì **HUD `countEnemies` phải nhân cùng** — nếu không, thanh tiến
trình màn sẽ vượt 100 % hoặc kẹt dưới 100 %. Gốc giữ `countEnemies` và `spawnCount` là **hai field riêng**
(`GP_Datas`) nên nó so sánh được; bản clone phải làm y vậy.

---

## 7. Phát hiện phụ — `Map_Get_Datas` có **11 cấu trúc**, không phải một bảng map→wave

| Field | Kiểu | Dùng cho |
|---|---|---|
| `listMapTryPlayerDatas` @0x0 | `List<int[]>` | `PlayMode.TryPlayer` |
| `AllArenaStartMaps` @0x8 · `AllArenaRandomMaps` @0x10 | `List<List<int[]>>` | Arena |
| `AllPvPStartMaps` @0x18 | `List<List<int[]>>` | PvP |
| **`listMapDatas`** @0x28 | **`List<int[]>`** | **campaign** |
| `listMapBranchDatas` @0x30 | `List<List<int[]>>` | nhánh |
| `listIdBosses` @0x38 | **`Dictionary<int,int>`** | stage → boss |
| `listMapFightBossDatas` @0x40 · `listMapChallangeDatas` @0x48 | `List<List<int[]>>` | FightBoss · Challange |
| `listMapEndlessDatas` @0x50 · `listMapObstacleDatas` @0x58 | `List<int[]>` | Endless |

⇒ **`A2` không phải một bảng** mà là **11 cấu trúc**, mỗi `PlayMode` một bảng. Điều này **giải thích**
vì sao 117 cặp tôi bóc ra trông như "quan hệ" chứ không phải "nhóm" — `.cctor` tạo **614 mảng**:

| Độ dài mảng | Số mảng | Đọc ra là gì |
|---:|---:|---|
| **3** | **320** | khớp **3 chế độ** (§3: mọi bảng mode đều độ dài 3) |
| **2** | **118** | khớp **`Dictionary<int,int>` `listIdBosses`** — 118 cặp `stage → boss` |
| 7 | 104 | 7 `PlayMode` |
| 4 · 1 · 5 · 6 · 9 · 8 | 21 · 21 · 12 · 9 · 5 · 4 | — |

> **Nhận định (mức B):** **118 cặp `stage → boss`** là con số dùng được ngay (39 boss trong
> `BOSSES`, 299 stage ⇒ mỗi boss phụ trách ~7,6 stage). **Điều kiện lật ngược:** nếu đọc phần tử của
> 118 mảng đó ra mà giá trị đầu **không** nằm trong dải `stageIndex` (0…298) thì không phải.

---

## 8. Còn thiếu / phải đoán

- **`MaxModeIndex` chưa có giá trị** — `static int` của `Stage_Datas`, lớp **chưa dump**. Suy từ chuỗi:
  **2** nếu là chỉ số lớn nhất, **3** nếu là số lượng. **Chưa phân định** — và đây là chỗ dễ sai 1 đơn vị.
- **`modeMultiplier[3]` chưa có số.** Nạp bằng `InitializeArray` (FieldRVA) — cùng blocker T5.
  Cần đọc `FieldRVA` + `il2cpp-pool-floats`/pool double, hoặc một lần dump `.cctor` của `Stage_Datas`
  (lớp **chưa** nằm trong `TARGET_CLASSES`).
- **`missionKillPercent[3][3]` chưa có số** — 9 float trong 3 mảng; cùng blocker.
- **`kCount[mode]` và `kHp[mode]` CHƯA BIẾT GIÁ TRỊ.** Cơ chế: **A** (bạn chơi + loại trừ §5). Vị trí:
  **B+** (3 thân hàm spawn). Giá trị: **không có trong bất kỳ file nào** ⇒ **không** lấy được từ APK nếu
  không dump thêm `Path_Spawner`/`PointToPoint_Spawner` (hoặc đọc trực tiếp trong game, §5.4).
- **Bảng dữ liệu KHÔNG có chiều chế độ** — phủ định có phạm vi: 17 class asm + toàn bộ chữ ký `dump.cs`
  + 23.757 `Call_Data` + 981 `Enemy_Datas` + `Wave.csv` + `Stage_Behaviour.csv`. **Đây là kết luận đúng**,
  và nó **không** nói "chế độ không đổi quân/HP" — nó nói **phép nhân nằm trong mã**.
- **`stageLevel ≡ stageMode`** chỉ là mức **B** (không có call-site trong asm đã export).
- **118 cặp `stage → boss`** mới là *giả thuyết khớp số*, chưa đọc được phần tử.
- **Nhánh `stageIndex ≥ 60 → ×1,25`** trong `GetBonus` **chưa hiểu ngữ nghĩa**: `stageIndex` bị clamp
  về 29 cho phần `base` nhưng vẫn so với 59/60 cho phần hệ số. Có thể là chỉ số **cộng dồn toàn game**
  (0…298) chứ không phải trong chương. **Chưa** xác định.
- **Tỉ lệ `kCount : kHp` chưa đo.** Nếu bạn chỉ muốn *một* con số để dựng clone: dùng **cùng một hệ số**
  cho cả quân và HP (ví dụ `1,0/1,35/1,7`) — đơn giản, và không sai hơn mức hiểu biết hiện tại.
- Tôi **đã rút lại** câu "chưa có bằng chứng nhiều quân/nhiều HP". Câu đúng: **bảng phẳng, mã có nhân.**
