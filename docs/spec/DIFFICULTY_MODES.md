# DIFFICULTY_MODES — 3 chế độ: cái gì **đổi**, cái gì **không**

> **Bạn nói:** *"con nào cũng có HP bar hết, bất kỳ stage nào cũng có 3 chế độ normal hard nightmare,
> chế độ khó hơn thì nhiều enemy hơn và có vẻ nhiều hp hơn."*
>
> **Bạn chơi lại game và chốt (23/10) — lần hai, đính chính chính mình:**
> *"3 mode nó **không nhân số quân** mà UI có chính xác số enemy bị eliminate để đạt số sao,
> số quân **không theo quy luật**."*
>
> **Đây là lần chốt đúng, và nó KHỚP với số liệu tôi đo từ đầu:** `GetCountEnemies` **304 lệnh · 0 `mul`**,
> `GetListWaves` **278 lệnh · 0 phép nhân**. Tôi **rút lại** kết luận `kCount` ở bản trước — bản đó dựa
> trên câu "chắc chắn đông hơn" của bạn, không dựa trên dữ liệu. Số liệu nói **không nhân**, và giờ
> chơi game cũng nói **không nhân**. Hai nguồn độc lập **trùng nhau** ⇒ mức **A**.
>
> **Vậy chế độ khó hơn khác ở đâu?** Ba kênh **có** bằng chứng: **ngưỡng sao/nhiệm vụ (%)** ·
> **thưởng** · **giá năng lượng**. Và một kênh bạn vẫn khẳng định: **HP enemy** (§5).
>
> **"Số quân không theo quy luật" = đúng, và đây là số:** 282 wave, min **4** · median **131** · max **951**,
> **CV = 1,01**, **150/282** giá trị khác nhau ⇒ **không có công thức**, phải đọc bảng (`MISSIONS_STARS` §5.1).

---

## 0. Bốn vế, bốn phán quyết

| Vế | Phán quyết | Bằng chứng | Mức |
|---|---|---|---|
| **Con nào cũng có HP bar** | ✅ **ĐÚNG — 109/109 = 100 %** | `Enemy_Hp_Bar` **909** + `Enemy_Display.hpProgressBarRenderer` **976/981**. Hợp hai nguồn: **không sót prefab nào** | **A** |
| **Stage nào cũng có 3 chế độ** | ✅ **ĐÚNG** | `txt_stagemode_0/1/2` = Normal/Hard/Nightmare · `Stage_Datas.MaxModeIndex` · `ModeCurrent` | **A** |
| ~~Khó hơn ⇒ nhiều enemy hơn~~ | ❌ **SAI — đã đính chính** (bạn chơi lại + số liệu) | `GetCountEnemies` **304 lệnh · 0 `mul` · 0 `get_stageMode`**; `GetListWaves` **278 lệnh · 0 phép nhân**; `Call_Data` **23.757/23.757** không field chế độ ⇒ **kCount ≡ 1** | **A** |
| **Khó hơn ⇒ nhiều HP hơn** | ⚠️ **Bạn khẳng định; tôi chưa có phép nhân để đối chiếu.** Đây là kênh **duy nhất** còn lại | HP serialize **1 số/prefab** (**981**), `StartHpPoint = 0` ở **981/981** ⇒ HP **ghi lúc spawn** — chỗ duy nhất chế độ chen vào được (§5.1) | **A (chơi game) · C (giá trị)** |

**Chế độ ĐỔI gì — có bằng chứng số:**

| Kênh | Bằng chứng | Mức |
|---|---|---|
| **Ngưỡng sao / nhiệm vụ** (`pct[mode]`) | `(int)(pct × countEnemies)` in ra UI — `MISSIONS_STARS` §1 | **A** |
| **Thưởng** (`levelDelta[mode]`) | `float[]` index bằng `ModeCurrent` — §3 | **A** |
| **Giá năng lượng** | `GetCostEnergyForPlay(stageIndex, stageLevel)` | **A** |
| **HP enemy** (`kHp[mode]`) | bạn chơi game, chưa có phép nhân tĩnh để đối chiếu | **A (chơi game)** |
| ~~Số quân~~ | **không** — xem hàng trên | **A (phủ định)** |

**Chế độ KHÔNG đổi:** **map · danh sách wave · số quân · loại enemy · bảng HP gốc**.

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

> **ĐÃ CHỐT — mức A (23/10, từ `MISSIONS_STARS.md` §1):** `stageLevel` **chính là** `ModeCurrent`.
> `Stage_Get_Datas.GetStringInfo` đọc thẳng field đó rồi truyền vào hàm `%` theo chế độ:
>
> ```asm
> 0x12c5a14: ldr  w21, [x9, #0x34]   ; Stage_Datas.ModeCurrent  (@0x34)
> 0x12c5a28: mov  w0, w21
> 0x12c5a30: bl   #0x14e5618         ; GetKillPercentMissionComplete(ModeCurrent)
> ```
>
> Trước đây tôi để **B** vì chưa có call-site. **Nay có.**

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
bonus = round( base(stage, mission) × levelDelta[mode] × (stage ≥ 60 ? 1,25 : 1) × (stage%5==4 ? 1,5 : 1) )
```

- **`levelDelta` là `float[]` index theo chế độ** — bằng chứng:
  **Tên thật** lấy từ `dump.cs`: `Stage_Get_Datas.levelDelta` (`private static float[]` @`0x10`);
  `modeMultiplier` là **tên tôi tự đặt** trước đây — nay bỏ (`UNITY_RULES` §6). `cmp w9, w20` + `b.ls throw`
  (kiểm biên mảng) + `ldr s0,[x8, w20*4 + 0x20]` + `fmul`. **Đây là chỗ duy nhất tôi tìm thấy
  chế độ nhân vào một con số.**
- **`f(mode)` xuất hiện dưới dạng hằng số nhánh** ở 6 cụm: `60/80/100`, `30/25/20`, `20/15/10`,
  `50/20`, `5`, `1,25` — tức **mỗi chế độ ăn một hằng số khác nhau**, không phải cùng một số.
- Mốc **mỗi 5 stage ×1,5** (chỉ số 4 · 9 · 14 · 19 · 24 · 29 — tức **stage 5, 10, 15, …, 30** đếm từ 1).
- **Giá trị số của `levelDelta` — ĐÃ ĐỌC ĐƯỢC (23/10):** `[1, 2, 3.6, 3.6]`
  (`docs/apk-analysis/ramus/2026-10-23-phone/statics_Stage_Get_Datas.json` ·
  `.fields.levelDelta`, `_count = 4`). Nghĩa là:

  | index | 0 | 1 | 2 | 3 |
  |---|---:|---:|---:|---:|
  | hệ số thưởng | **1** | **2** | **3,6** | **3,6** |

  **Hai điều phải nói kèm:**
  1. Mảng có **4 phần tử**, trong khi tài liệu cũ giả định `float[3]` (§8 trước đây ghi `levelDelta[3]`).
     Mức **B** — dữ liệu từ bản `com.Gcenter.WindWings.SpaceShooter.Premium` 1.0.69, không phải
     `com.Wind.wings.Space.Shooter` 1.3.118.
  2. Bạn đã thấy trong game **3 chế độ**. Nếu `levelDelta` thật sự index bằng `ModeCurrent` thì
     **index 3 là chế độ thứ tư không hiện trong menu stage** (nghi: nhánh Arena/PvP/branch).
     > Nhận định: đây chỉ là suy luận từ **độ dài mảng**, chưa có phép đo nào chỉ ra index 3 dùng
     > cho việc gì. Đừng dựng tính năng dựa trên nó.

  Với số này, công thức ở trên thành:
  `bonus = round( base × [1 | 2 | 3,6 | 3,6][mode] × (stage ≥ 60 ? 1,25 : 1) × (stage%5==4 ? 1,5 : 1) )`.

### Ba chỗ khác cũng ăn theo chế độ

| Hàm | Trả về | Ý nghĩa |
|---|---|---|
| `GetKillPercentMissionComplete(int _modeIndex)` `0x14E5618` (**188 B**) | **một trong 3 mảng `float[3]`** | **3 mốc % nhiệm vụ cho mỗi chế độ = 9 số.** Chọn bằng 3 nhánh `csel`, **mặc định rơi về chế độ 0** ⇒ chế độ lạ = Normal. **Runtime 23/10 chỉ thấy MỘT mảng** — xem `MISSIONS_STARS` §7.1 |
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

## 5. `kCount ≡ 1` — **ba nguồn độc lập** cùng nói "không nhân số quân"

| Nguồn | Phép đo | Kết quả |
|---|---|---|
| **Bạn chơi lại (23/10)** | — | **3 mode không nhân số quân**; UI in **chính xác** số cần diệt cho từng sao |
| `GetCountEnemies` | **304 lệnh** | **0** `mul` · **0** `fmul` · **0** lần gọi `get_stageMode`; chỉ **cộng** độ dài mảng |
| `GetListWaves` | **278 lệnh** | **0** phép nhân; phép số học duy nhất là `/6` (tách chương) |
| `Call_Data` | **23.757** instance | **không** field chế độ; `number = 0` ở **100 %** |
| `Wave.csv` · `Stage_Behaviour.csv` | 52 cột | **không** cột chế độ |

⇒ **`kCount[mode] = 1` cho cả 3 chế độ** (mức **A**). Số quân mỗi màn **giống hệt** ở Normal, Hard, Nightmare.

> **Tôi rút lại điều gì:** bản trước tôi kết luận "hệ số nằm trong thân `MoveNext`" — vì tôi dựa vào câu
> *"chắc chắn đông hơn"* của bạn thay vì dựa vào số liệu. Số liệu **luôn** nói không nhân. Nay bạn kiểm lại
> và cũng nói không nhân ⇒ **không có phép nhân nào cần tìm**, và **3 thân hàm spawn không còn là blocker**
> cho số quân (chúng vẫn có thể chứa `kHp`, xem §5.2).

### 5.1 Vậy vì sao *cảm giác* đông hơn — và nó **không** mâu thuẫn với "không nhân"

Hai câu của bạn **đều đúng**, và đây là cơ chế giải thích cả hai:

```
số_quân_cùng_lúc ≈ tốc_độ_spawn × thời_gian_sống
thời_gian_sống ∝ HP enemy
```

`rate` (tốc độ spawn) **không** đổi theo chế độ (`Call_Data.rate`: 1,0 ở **16.173** · 0,0 ở **5.682**).
Nhưng nếu **HP tăng** thì mỗi con sống lâu hơn ⇒ **số con cùng lúc trên màn hình tăng** — dù **tổng số
quân của màn không đổi một con**. Đó là "thấy đông hơn" mà **không** phải "nhân số quân".

> **Ví dụ bằng số:** Normal có **47–157** con cùng lúc (`ENEMY_HP_RUNTIME` §3.1). Nếu `kHp = 1,5` thì
> cùng một `rate`, số con cùng lúc thành **~70–235**. Tổng số quân vẫn **45.659**. **Không** có gì bị nhân
> ngoài HP.

Và kênh thứ hai cũng làm "thấy đông hơn": **ngưỡng sao là %** (`MISSIONS_STARS` §1) ⇒ chế độ khó hơn đòi
bạn **giết tới % cao hơn của cùng danh sách đó** ⇒ bạn phải chơi **sâu hơn vào wave** ⇒ gặp nhiều con hơn
trong **cùng một** wave.

> **Nhận định (mức C, về cảm giác):** "đông hơn" = **Little's law**, không phải hệ số spawn.
> **Điều kiện lật ngược:** nếu `GP_Datas.countEnemies` (tổng dự kiến) khác nhau giữa 3 chế độ trên **cùng
> một stage** — đo được bằng cách so số trên HUD/tiến trình, hoặc so `{0} / pct`.

### 5.2 `kHp` — chỗ duy nhất còn lại của "nhiều máu hơn"

```
hp_spawn = Enemy_Get_Datas.GetStartHealthPoint(id) × kHp[mode]
```

Bốn dấu vết ép phép nhân vào **đúng** chỗ này:

| Dấu vết | Số | Nói lên điều gì |
|---|---:|---|
| `Enemy_Datas.StartHpPoint` | **0,0 ở 981/981** | HP lúc vào trận **chưa** có trong prefab ⇒ **ghi lúc spawn** |
| `Enemy_Datas.CurrentHealthPoint` | **0 ở 981/981** | như trên |
| `Enemy_Controller.GetStartHealth` | **28 B (7 lệnh)** | không đủ chỗ tra mode + nhân ⇒ **nhân trước khi ghi**, không nhân lúc đọc |
| `Enemy_Datas` | **981** instance, **1 HP/prefab** | bảng HP **không** có chiều chế độ ⇒ hệ số phải ở **mã** |

### 5.3 Bằng chứng *phụ* từ chính game: engine **có** khái niệm enemy mạnh lên

`txt_challange_mission_2` (12-localization.csv) = **"The enemy gains health and strength"** — engine có
đường tăng HP/strength cho enemy, đúng loại cơ chế mà chế độ khó dùng lại.

### 5.4 "Số quân không theo quy luật" — **đúng**, và đây là số đo

Bạn nói đúng: **không có công thức** cho số quân mỗi wave. Đo trên 282 wave (`datas/waves.json`):

| Thống kê | Số |
|---|---:|
| Tổng quân toàn game | **45.659** |
| min · p25 · **median** · p75 · max | **4** · 60 · **131** · 201 · **951** |
| mean ± SD | **161,9 ± 163,9** |
| Hệ số biến thiên **CV** | **1,01** (phân tán ≈ 1 độ lệch chuẩn trên mỗi trung bình) |
| Số giá trị **khác nhau** | **150 / 282** (53 %) |
| Tương quan vị trí wave ↔ số quân | **r = −0,456** (không phải xu hướng tăng) |
| Tự tương quan lag-1 | **+0,625** (wave gần nhau na ná nhau) |

⇒ Số quân phải **đọc từ bảng**, **không** suy được bằng công thức. Bản clone: **nhúng bảng**, đừng cố
viết hàm `f(wave)`.

> **Cảnh báo về con số `r = −0,456`:** đây có thể là **artefact của thứ tự file** (`Wave_0000…` là wave
> đầu và to nhất: 883 · 936 · 951 · 761 · 846). **Chưa** xác định chúng có thật sự đứng đầu campaign hay
> chỉ là wave dùng chung. Mức **C**.

### 5.5 Cách đo `kHp` trong 10 phút — thứ duy nhất còn thiếu

| Cần đo | Cách đọc | Suy ra |
|---|---|---|
| **`kHp`** | cùng **1 loại enemy**, cùng **1 súng** ở cùng cấp, đếm **số phát** cho tới khi chết, lặp ở 3 chế độ | `kHp = số_phát(khó) / số_phát(Normal)` |
| **`pct[mode]`** | đọc `{0}` trong `"Eliminate {0} enemies"` ở 3 chế độ | `pct[mode] = {0} / countEnemies(stage)` — mà `countEnemies` **giống nhau** ở 3 chế độ ⇒ `pct[1]/pct[0] = {0}₁/{0}₀` |

Vì sao đếm phát bắn là đủ: `số_phát = ceil(HP × f(giáp) / damage)`. Với `số_phát ≥ 10`, sai số làm tròn
**< 5 %** — phân biệt được `1,25×` / `1,5×` / `2×`. Dùng con bị spawn nhiều nhất `CB-30003` (**4.793** quân).

| Chế độ | `{0}` nhiệm vụ | số phát để giết `CB-30003` |
|---|---:|---:|
| Normal (0) | | |
| Hard (1) | | |
| Nightmare (2) | | |

---

## 6. Hệ quả cho SPEC — số nào phải đổi nhãn

| Số đang ghi | Vấn đề | Sửa |
|---|---|---|
| **45.659 quân** | ✅ **dùng chung cho cả 3 chế độ** — `kCount ≡ 1` (§5) | giữ nguyên, thêm dòng "**cùng số quân ở 3 chế độ**" |
| **11.094 spawner** | số spawner trong asset, không phải số quân | giữ, ghi rõ |
| **282 wave** | `GetListWaves(stageIndex)` — **1 tham số**, không mode | ✅ **wave dùng chung 3 chế độ** |
| **299 stage** | mỗi stage × 3 chế độ = **897 lượt chơi** | thêm dòng **897** |
| **63,5 phút** (282 wave) | `rate` không đổi theo chế độ | ✅ **giữ nguyên cho cả 3 chế độ** — độ dài **không** đổi; cái đổi là **thời gian mỗi con sống** (HP) |
| **"HP enemy = 0 trong CSV"** | HP cấp runtime | ✅ đã sửa ở `ENEMY_HP_RUNTIME` |
| **108/109 HP bar** | thiếu đường `Enemy_Display` | **109/109** (§1) |
| **Không có bảng mode** | **có** — chỉ là bảng **thưởng**, không phải bảng quân/HP | thêm §3 |

### Khuyến nghị cho bản clone (L1 — giống cơ chế, sáng tạo phần còn lại)

**Giữ đúng cơ chế gốc** — 3 chế độ **dùng chung map, danh sách wave, số quân, loại enemy**.
Khác nhau ở **4 bảng**; ba cái đầu **có trong dữ liệu gốc**, cái cuối **hard-code nên clone tự chọn**:

```
levelDelta[3]        → thưởng          (gốc: float[] ẩn;   clone: 1.0 / 1.35 / 1.7)
missionKillPercent[3][3] → 3 mốc % mỗi chế độ (gốc: 3×float[3] ẩn; clone: 60/80/100 · 70/88/100 · 80/95/100)
energyCost[stage][3]     → giá năng lượng   (clone: +0 % / +25 % / +50 %)
kHp[3]                   → HP enemy         (gốc: hard-code, CHƯA biết; clone: 1.0 / 1.5 / 2.0)
kCount                   → **1.0 — ĐỪNG nhân** (gốc = 1, mức A)
```

> **Đừng gán số clone cho bản gốc.** Dòng `kHp` là **lựa chọn thiết kế**; gốc có cơ chế nhưng **giá trị
> chưa đo**. Ghi `// clone-chosen, not original` trong code.

**Vì sao `kCount` phải = 1 (không chỉ vì "cho giống"):** nếu nhân số quân thì bạn phải nhân cả
`countEnemies` **và** `pct` sinh ra từ nó (`MISSIONS_STARS` §1); lệch một chỗ là **thanh tiến trình vượt
100 %** hoặc **3 sao thành dễ**. Gốc **không** làm vậy — nó tăng độ khó bằng **HP** và **ngưỡng %**, hai
chỗ **không** đụng tới tổng số quân. Đó là lý do thiết kế gốc **sạch**: một nguồn sự thật duy nhất cho
"số quân của màn".

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

- ~~`MaxModeIndex` chưa có giá trị~~ → **đọc được: 4** (`statics_Stage_Datas.json` · `.fields.MaxModeIndex`).
  Vẫn **chưa phân định** "chỉ số lớn nhất" hay "số lượng": nếu là số lượng thì có 4 chế độ, khớp
  đúng **4 phần tử** của `levelDelta`. Hai dữ kiện cùng chỉ về 4, nhưng cả hai đều từ **cùng một
  nguồn** (cùng file JSON) nên **không phải hai bằng chứng độc lập**.
- ~~`levelDelta[3]` chưa có số~~ → **`[1, 2, 3.6, 3.6]`** (§3). Blocker T5 **không còn** cho field này.
- **`missionKillPercent[3][3]`**: đọc được **3 trong 9** số — `[0.2, 0.6, 0.98]`
  (`MISSIONS_STARS` §7). Còn 6 số và chưa biết mảng vừa đọc ứng với chế độ nào.
- **`kCount ≡ 1`** — **ĐÓNG** (A): ba nguồn độc lập (bạn chơi lại · 304 lệnh `GetCountEnemies` · 278 lệnh
  `GetListWaves`) cùng nói **không nhân**. Ba thân hàm spawn **không** còn là blocker cho số quân.
- **`kHp[mode]` CHƯA BIẾT GIÁ TRỊ** — cơ chế **A** (bạn chơi), vị trí **C** (nghi tầng spawn, §5.2).
  **Không** suy được từ bảng (không có bảng). Hai đường: dump `Path_Spawner`/`PointToPoint_Spawner`, hoặc
  đếm số phát bắn trong game (§5.5).
- **Bảng dữ liệu KHÔNG có chiều chế độ** — phủ định có phạm vi: 17 class asm + toàn bộ chữ ký `dump.cs`
  + 23.757 `Call_Data` + 981 `Enemy_Datas` + `Wave.csv` + `Stage_Behaviour.csv`. Kết luận đúng, và nó
  **khớp** với "không nhân số quân"; nó **không** loại trừ `kHp` vì HP được ghi **lúc spawn**.
- ~~`stageLevel ≡ stageMode` chỉ là mức B~~ → **A**: `GetStringInfo` `ldr w21,[x9,#0x34]` (`ModeCurrent`) rồi truyền vào `GetKillPercentMissionComplete` — `MISSIONS_STARS.md` §1.
- **118 cặp `stage → boss`** mới là *giả thuyết khớp số*, chưa đọc được phần tử.
- **Nhánh `stageIndex ≥ 60 → ×1,25`** trong `GetBonus` **chưa hiểu ngữ nghĩa**: `stageIndex` bị clamp
  về 29 cho phần `base` nhưng vẫn so với 59/60 cho phần hệ số. Có thể là chỉ số **cộng dồn toàn game**
  (0…298) chứ không phải trong chương. **Chưa** xác định.
- **Số quân mỗi wave là dữ liệu, không phải công thức** (§5.4: CV **1,01**, **150/282** giá trị khác nhau,
  `r = −0,456`) ⇒ clone phải **nhúng bảng**, đừng viết hàm `f(wave)`.
- **Nếu chỉ được chọn một hệ số cho clone:** chọn `kHp` (đó là kênh duy nhất gốc thật sự có thể nhân),
  và **để `kCount = 1`** — nhân số quân sẽ phá ngưỡng sao.
- Tôi **đã rút lại hai lần**: (1) "chưa có bằng chứng" → sai, phải nói "bảng phẳng"; (2) "kCount nằm
  trong `MoveNext`" → **sai**, `kCount ≡ 1`. Lần rút lại thứ hai là do tôi tin câu nói thay vì số liệu —
  **số liệu đã đúng ngay từ đầu.**
