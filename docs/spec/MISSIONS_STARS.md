# MISSIONS_STARS — vì sao game **phải** biết tổng số quân

> **Bạn hỏi:** *"mỗi mode đều tính số enemy bị eliminate để đạt được 1, 2, 3 sao. Điều tôi thấy là tại sao
> app phải tính tổng số quân spawn làm gì?"*
>
> **Trả lời ngắn:** app **không đếm** quân đã spawn. `GetCountEnemies(stageIndex)` **cộng bảng wave**
> (304 lệnh, **0 phép nhân**, đọc `GetListWaves`) — nó là **mẫu số** của ngưỡng sao, không phải bộ đếm.
> Ngưỡng sao lưu dạng **phần trăm**, nên **bắt buộc** phải có mẫu số để đổi thành số tuyệt đối in lên
> màn hình `"Eliminate {0} enemies"` và để biết đã xong chưa.
>
> Và tôi tìm được **lệnh chứng minh** — dưới đây là asm, không phải suy đoán.
>
> **Bạn đã kiểm trong game (23/10), lần hai:** *"3 mode nó **không nhân số quân** mà UI có **chính xác** số
> enemy bị eliminate để đạt số sao, số quân **không theo quy luật**."* — **Khớp 100 %** với asm ở §1 và với
> số đo ở §5.1. Đây là lần chốt **đúng**; xem `DIFFICULTY_MODES.md` §5 để biết điều tôi rút lại.

---

## 0. Ba câu trả lời, ba mức

| Câu hỏi | Trả lời | Mức |
|---|---|---|
| Ngưỡng sao tính từ đâu? | **`{0} = (int)( pct[mode][slot] × countEnemies )`** — trích asm §1 | **A** |
| Vì sao phải có tổng số quân? | Nó là **mẫu số**; ngưỡng lưu bằng **%** nên phải nhân ra số tuyệt đối. Cộng thêm: đếm số nhiệm vụ xong để ra sao, và biết màn kết thúc | **A** |
| Mỗi mode có ngưỡng khác nhau *vì* khác số quân? | **KHÔNG.** `countEnemies` **không** phụ thuộc mode ⇒ khác biệt **100 %** đến từ `pct[mode]` | **A** (asm) |

Điều này **khớp đúng** với điều bạn thấy: mỗi mode có bộ ngưỡng sao riêng — nhưng cơ chế là
**bảng % theo mode**, không phải "đếm lại số quân của mode đó".

---

## 1. Lệnh chứng minh — `Stage_Get_Datas.GetStringInfo`

Hàm dựng **chuỗi nhiệm vụ** (`0x12C5760`, **512 lệnh**). Đoạn quyết định, trích nguyên văn:

```asm
0x12c58c4: bl   #0x12c5f60     ; GetCountEnemies(stageIndex)      ← MẪU SỐ
0x12c58c8: mov  w20, w0        ; w20 = count

0x12c5a14: ldr  w21, [x9, #0x34]   ; Stage_Datas.ModeCurrent      ← CHẾ ĐỘ
0x12c5a28: mov  w0, w21
0x12c5a30: bl   #0x14e5618     ; GetKillPercentMissionComplete(ModeCurrent)
0x12c5a40: add  x8, x0, #0x20      ; float[0] … [1] là #0x24, [2] là #0x28
0x12c5aa0: ldr  s0, [x8]           ; pct = mảng[slot]
0x12c5aa4: scvtf s1, w20           ; (float)count
0x12c5ab0: fmul  s0, s0, s1        ; pct × count
0x12c5ab8: fcvtzs w8, s0           ; → int  ← chính là {0} trong "Eliminate {0} enemies"
```

Ba dòng cuối là **toàn bộ** câu trả lời cho câu hỏi của bạn: **`pct × tổng quân`**.

### Hàm này gọi những gì (đếm trong 512 lệnh)

| Hàm | Số lần | Vai trò |
|---|---:|---|
| **`GetCountEnemies`** `0x12C5F60` | **2** | mẫu số cho nhiệm vụ "giết quân" |
| `GetCountSpecialEnemies` `0x12C6420` | 1 | mẫu số cho "giết quân đặc biệt" |
| `GetCountSupplyNormal` `0x12C687C` | 1 | mẫu số cho "cứu người" |
| **`GetKillPercentMissionComplete`** `0x14E5618` | **3** | `float[3]` **theo chế độ**, tra theo `slot` |
| `GetBranchPercent1` `0x14E5790` | 2 | `float[3]` theo chế độ |
| `GetBranchPercent2` · `GetBranchPercent3` | 1 · 1 | như trên |

⇒ **5 hàm đếm** + **4 hàm `%` theo chế độ** = đúng cấu trúc "ngưỡng = % × tổng".

**Đọc thân hàm `GetKillPercentMissionComplete` (188 B — bản `68ce86a7`, `Player_Get_Datas.asm.txt`):**

```asm
0x14e563c: ldrb  w8,  [x24, #0x2ae]   ; cờ khởi tạo static
0x14e5640: ldr   x20, [x20, #0xb78]   ; slot 0x2ae8b78 = mảng FALLBACK (0.50/0.80/1.00)
0x14e5644: ldr   x21, [x21, #0xb80]   ; slot 0x2ae8b80 = mảng mode 1 (0.35/0.60/0.98)
0x14e5648: ldr   x22, [x22, #0xb88]   ; slot 0x2ae8b88 = mảng mode 0 (0.20/0.45/0.80)
0x14e5694: cmp   w19, #1
0x14e5698: csel  x8,  x21, x20, eq    ; mode==1 ? mode1 : fallback
0x14e569c: cmp   w19, #0
0x14e56a0: mov   w1,  #3
0x14e56a4: csel  x19, x22, x8,  eq    ; mode==0 ? mode0 : ở trên
0x14e56a8: bl    #0x110d09c           ; new float[3]
0x14e56ac: ldr   x1,  [x19]
0x14e56b8: bl    #0x205b07c           ; memcpy 3 float
```

⇒ **`pct` = đúng 9 số**: 3 chế độ × 3 nhiệm vụ, mỗi chế độ là **một `static float[3]`**.

> ⚠️ **Sửa 25/10 — dòng cũ ở đây SAI hai chỗ.** Bản trước ghi `0xb78` là "mảng #0", `0xb88` là "#2",
> rồi kết luận *"mode ngoài `0..2` rơi về chế độ 0"*. Đọc đúng thứ tự `csel`: mode `0` → **0xb88**,
> mode `1` → **0xb80**, **mọi giá trị khác** → **0xb78** (fallback riêng, `.50/.80/1.00`), **không**
> rơi về mode 0. Đây là đúng lỗi `P0` của review `25c367aca` (R1).

> **Chốt thêm một mắt ghép (nâng B → A):** `ldr w21, [x9, #0x34]` đọc **`Stage_Datas.ModeCurrent`**
> (field `@0x34`) rồi truyền thẳng vào `GetKillPercentMissionComplete`.
> Vậy **`stageLevel` trong các hàm dữ liệu CHÍNH LÀ `ModeCurrent`** — trước đây tôi chỉ để mức **B**.

---

## 2. Vì sao "1, 2, 3 sao" — nhiệm vụ là **cộng dồn**

`Stage_Get_Datas.IsMissionCompleted(stageIndex, **stageLevel**, missionIndex)` — **47 lệnh**:

```asm
0x12c55e4: mov  w0, w21        ; stageIndex
0x12c55e8: mov  w1, w20        ; stageLevel = ModeCurrent
0x12c55ec: mov  x2, xzr        ; 0
0x12c55f0: bl   #0x12b79a8     ; → int: **số sao ĐÃ LƯU** (GetStarStageMaster), không phải kills lượt này
0x12c5624: cmp  w0, w19        ; so với missionIndex
0x12c5630: cset w0, gt         ; return  savedStars > missionIndex
```

⇒ Nhiệm vụ `i` được coi là **đã xong (đã lưu)** khi **`savedStars > i`**. Với 3 nhiệm vụ ⇒ `saved` 0/1/2/3
⇒ row 0/1/2 sáng dần. Khớp đúng câu của bạn.

> ⚠️ **Sửa 25/10 — bản trước ghi `0x12b79a8` là "SỐ NHIỆM VỤ ĐÃ XONG" và để ngỏ *"nghi tính từ kills"*.**
> Sai ngữ nghĩa: `0x12b79a8` = **`GetStarStageMaster`** đọc `StarStageMaster{stageIndex}_{modeIndex}`
> (`PlayerPrefs`), tức **trạng thái đã lưu giữa các lượt**, không phải kết quả lượt đang chơi.
> Kết quả **lượt đang chơi** do `GetMissionCompleted(killCount, countEnemies, slot)` tính từ counter
> snapshot ở `Board_Endgame` — hai hàm khác nhau, đừng gộp (review R1).
>
> Chuỗi lưu thật (`57-endgame-mission-stars-save-continue.md` §4): `result ∈ −1..2` →
> `newStars = result + 1` → **chỉ ghi khi `newStars > savedStars`** (guard ở caller, không phải trong setter).

Và sao được lưu **theo từng chế độ**:

```csharp
public static int GetStarStageMaster(int stageIndex, int modeIndex);          // 0x12C…
public static void SetStarStageMaster(int stageIndex, int modeIndex, int stars);
public static int GetStarStageBranch(int stageIndex, int modeIndex);          // nhánh
```

⇒ "**mỗi mode đều có 1,2,3 sao riêng**" = **A**, có chữ ký hàm làm bằng chứng.
(`GetAllStageStarCount(stageIndex)` tổng hợp lại cho màn chọn stage.)

> **Còn một ẩn số:** số sao **tối đa** không ghi ở đâu. `SetStarCheat(..., star = 5)` có mặc định **5**,
> nên hàm set **không** chặn ở 3. Ba là suy ra từ số nhiệm vụ = 3 (`txt_mission_0/1/2`) — **mức B**.

---

## 3. Loại nhiệm vụ xoay vòng theo `stageIndex % 6`

Cùng hàm `GetStringInfo`, **trước** khi chọn mẫu số:

```asm
0x12c582c: tbnz w20, #0, #0x12c5934      ; stageIndex lẻ → nhánh xoay vòng
0x12c5934: mov  w8, #0xaaab
0x12c5938: movk w8, #0x2aaa, lsl #16     ; 0x2AAAAAAB = magic CHIA 6
0x12c594c: mov  w9, #6
0x12c5950: msub w8, w8, w9, w20          ; w8 = stageIndex % 6
0x12c5954: cmp  w8, #3                   ; → nhánh A
0x12c595c: cmp  w8, #1                   ; → nhánh B ("quân đặc biệt")
```

⇒ **loại nhiệm vụ không ngẫu nhiên, cũng không theo chế độ** — nó xoay theo **`stageIndex % 6`**.
Bảng nối với chuỗi trong `12-localization.csv` (**mức B** — nối theo *hàm nào được gọi*, chưa đọc hết
nhánh):

| # | Loại | Nguồn **mẫu số** | Chuỗi |
|---:|---|---|---|
| 0 | Giết quân thường | `GetCountEnemies` | `txt_mission_0/1/2` · `txt_mission_kill_enemies` = "Eliminate {0} enemies" |
| 1 | Giết quân đặc biệt | `GetCountSpecialEnemies` | `txt_mission_branch_1_1/2/3` = "Eliminate {0} special enemies" |
| 2 | Cứu người | `GetCountSupplyNormal` · `GetCountSupply` | `txt_mission_branch_3_1/2/3` = "Rescue {0} peoples" |
| 3 | Thu thập sao | `GP_Datas.starCount` | `txt_mission_branch_4_1/2/3` = "Collect {0} star" |
| 4 | An toàn / đầy máu | `Player_Health` | `txt_mission_hp_safe` = "Safe" · `txt_mission_hp_full` = "Full health" |
| 5 | Hoàn thành màn | — | `txt_mission_complete_stage` = "Complete stage" |

> **Nhận định:** loại 4 và 5 **không** dùng `{0}` ⇒ không cần mẫu số. Đó là lý do `GetCountEnemies`
> **không** được gọi cho mọi stage — chỉ 2/6 loại cần.

---

## 4. Vậy **vì sao** phải tính tổng? Bốn lý do, cái nào cũng có số

| # | Lý do | Bằng chứng |
|---:|---|---|
| 1 | **Mẫu số của ngưỡng sao** (ngưỡng lưu bằng **%**) | `fmul pct × count` → `fcvtzs` |
| 2 | **Đếm số nhiệm vụ đã xong** để ra 1/2/3 sao | `IsMissionCompleted` = `completed > slot` |
| 3 | **Biết màn kết thúc** | `GP_Datas`: `countEnemies` + `countAllEnemies` + `spawnCount` — **3 field `int` riêng**, đều `0` trong prefab ⇒ cấp runtime |
| 4 | **Thanh tiến trình HUD** (đã diệt / tổng) | như trên: `spawnCount` là *đếm thật*, `countEnemies` là *thiết kế* |

### Và nó **rẻ** — vì nó không đếm gì cả

| Phép đo trên `GetCountEnemies` | Số |
|---|---:|
| Kích thước | **1.216 B · 304 lệnh** |
| Phép `mul` / `madd` | **0** |
| Phép `fmul` / `fdiv` | **0** |
| Có vòng qua object đã spawn? | **Không** — chỉ đọc mảng wave qua `GetListWaves` (**278 lệnh · 0 phép nhân**, chỉ `/6` để tách chương) |

⇒ Nó **cộng độ dài các mảng** trong bảng thiết kế. Không phải "quét toàn bộ quân trên màn hình".
Chạy một lần rồi cache vào `GP_Datas.countEnemies`; **không** phải per-frame.

---

## 5. Hệ quả — chỗ này **quan trọng cho độ khó**

```
{0}(mode, slot) = (int)( pct[mode][slot] × countEnemies(stageIndex) )
```

**Bạn đã xác nhận trong game (23/10):** *"3 mode nó **không nhân số quân** mà UI có **chính xác** số enemy
bị eliminate để đạt số sao"*. Khớp đúng công thức trên: `countEnemies` **một giá trị cho cả 3 chế độ**
(`DIFFICULTY_MODES` §4 — 304 lệnh, 0 `mul`), nên con số in ra là **số nguyên chính xác** bằng
`pct × count`. ⇒ **Mọi khác biệt ngưỡng giữa 3 chế độ đến từ `pct[mode]`, KHÔNG từ số quân.**

### 5.1 "Số quân không theo quy luật" — **đúng**, và đây là số đo

Đo trên **282 wave** (`datas/waves.json`):

| Thống kê | Số |
|---|---:|
| Tổng quân toàn game | **45.659** |
| min · p25 · **median** · p75 · max | **4** · 60 · **131** · 201 · **951** |
| mean ± SD | **161,9 ± 163,9** |
| Hệ số biến thiên **CV** | **1,01** |
| Số giá trị **khác nhau** | **150 / 282** (53 %) |
| Tương quan vị trí wave ↔ số quân | **r = −0,456** (không tăng dần) |
| Tự tương quan lag-1 | **+0,625** (wave gần nhau na ná) |

⇒ **Không có công thức** `f(wave)`; **không** có "mỗi wave sau đông hơn wave trước". Số quân **phải đọc
từ bảng**. Bản clone: **nhúng bảng**, đừng viết hàm.

> **Cẩn thận với `r = −0,456`:** 5 wave "to nhất" đều là wave **đầu** (`Wave_0000` 883 · `Wave_0001` 936 ·
> `Wave_0010` 951). Có thể chúng là wave **dùng chung** chứ không đứng đầu campaign. Mức **C**.

### 5.2 Vậy `pct[mode]` — ~~đo bằng con số UI in ra~~ *(đã bị thay bằng §7.3)*

> **25/10:** không cần đọc `{0}` trên UI nữa — ba mảng `pct` đã lấy **trực tiếp từ `field_default`**
> (`§7.3`). Cách dưới đây giữ lại làm **đường kiểm độc lập** nếu có thiết bị: nếu số UI khớp bảng §7.3
> thì cả hai cùng đúng.

Vì `{0}` là **số nguyên chính xác** và mẫu số **giống nhau** ở 3 chế độ:

```
pct[mode][slot] = {0}(mode, slot) / countEnemies(stage)
⇒ pct[1]/pct[0] = {0}₁/{0}₀ ,  pct[2]/pct[0] = {0}₂/{0}₀
```

Vào **cùng một stage**, cùng **nhiệm vụ đầu tiên**, đọc `{0}` ở 3 chế độ:

| Chế độ | `{0}` đọc được | suy ra |
|---|---:|---|
| Normal (0) | | `pct[0] = {0}₀ / count` |
| Hard (1) | | `pct[1] = {0}₁ / count` |
| Nightmare (2) | | `pct[2] = {0}₂ / count` |

Nếu `pct[2] = 1,0` (Nightmare phải giết **hết** — giả định **B**) thì chỉ cần **2 phép chia** là ra
`pct[0]`, `pct[1]` chính xác. Và `count` tôi **đã có** trong `waves.json` — chỉ cần biết stage nào.

---

## 6. Công thức cho bản clone

```
count       = Σ (len(listIdEnemies) × copies)     // 45.659 toàn game; GIỐNG NHAU ở 3 chế độ
pct[3][3]   = { {0.60, 0.80, 1.00},               // Normal
                {0.70, 0.88, 1.00},               // Hard
                {0.85, 0.95, 1.00} }              // Nightmare   ← số clone tự chọn
target[m][s] = round(pct[m][s] × count)            // KHÔNG có kCount
saos         = số s sao cho killCount ≥ target[m][s]  (cộng dồn, tối đa 3)
```

**Ba điều bắt buộc để không sai:**
1. **Không nhân số quân theo chế độ** (gốc = 1). Muốn khó hơn thì tăng **`pct`** và **HP**, không tăng số con.
2. `target` phải tính từ **cùng** `count` mà HUD dùng — một nguồn sự thật duy nhất. Lệch một chỗ là thanh
   tiến trình vượt 100 % hoặc 3 sao thành dễ.
3. Nhiệm vụ **cộng dồn** (`completed > slot`): xong nhiệm vụ 3 ⇒ 1, 2 cũng xong. Đừng cho phép "xong 3
   mà chưa xong 1".

---

## 7. Dữ liệu runtime 23/10 — **3 trong 9 số** đã đọc được

Lần đầu tiên `pct` có **giá trị thật**, đọc từ game đang chạy trên điện thoại (BepInEx +
bridge, endpoint `/statics`). Nguồn file:
`docs/apk-analysis/ramus/2026-10-23-phone/statics_Player_Get_Datas.json` · đường dẫn
`.fields.PercentToCompleteMissions222`.

```json
"PercentToCompleteMissions222": [0.2, 0.6, 0.98]
"PercentToCompleteMissions222_count": 3
```

| Điều | Nội dung | Mức |
|---|---|---|
| **3 giá trị** của một mảng `float[3]` nhiệm vụ | **0,2 · 0,6 · 0,98** | **B** — xem cảnh báo bản dưới |
| Đây là **một** mảng, không phải 9 | JSON chỉ có **một** field `float[3]` thuộc nhóm mission | **A** (trong bản mod đó) |
| `pct × count` cho ra số nguyên | 0,2 / 0,6 / 0,98 là các tỉ lệ "tròn" hợp lý cho 3 mốc nhiệm vụ | **C** — chưa đối chiếu số UI |

> **Cảnh báo bản — bắt buộc đọc kèm:** dữ liệu này lấy từ
> `com.Gcenter.WindWings.SpaceShooter.Premium` **1.0.69** (bản mod đóng gói lại), **không phải**
> `com.Wind.wings.Space.Shooter` **1.3.118** mà toàn bộ file này phân tích. Hai bản khớp nhau ở
> `StartHp = 2500` và `stepCommon = 0.18`, nhưng **không** có bằng chứng chúng là cùng một build.
> Vì vậy mức là **B**, không phải A.

### 7.1 Chỗ mâu thuẫn với asm — **chưa giải quyết**

§1 đọc asm và kết luận `pct` = **9 số** (3 chế độ × 3 nhiệm vụ), chọn bằng 3 nhánh `csel`
trong `GetKillPercentMissionComplete`. Runtime chỉ thấy **một** mảng `float[3]`.

Ba khả năng, **chưa cái nào được chứng minh**:

1. **Bản mod đã đổi cấu trúc** — Premium 1.0.69 gộp 3 mảng thành 1, chế độ ăn ở chỗ khác.
2. **Hai mảng còn lại nằm ở class khác** — `GetKillPercentMissionComplete` trả bản **copy**
   (`new float[3]` + `memcpy`), nên 3 mảng nguồn **không nhất thiết** thuộc `Player_Get_Datas`;
   chúng có thể ở class chưa được gọi.
3. **Interop không expose** hết static field — đã thấy 5 field khác trong class này trả về
   `(Dictionary`2)` thay vì dữ liệu.

> Nhận định: khả năng 2 là **rẻ nhất để loại trừ** — chỉ cần một lệnh
> `GET /types?filter=Percent` trên thiết bị, rồi `/statics?type=<kết quả>`. Nếu tìm ra
> `PercentToCompleteMissions111` / `...333` thì đó chính là 3 mảng theo chế độ.
> Tên `...222` có hậu tố số là **gợi ý mạnh** rằng còn hai biến thể cùng họ.

### 7.2 `listIgroneEnemies` — **31 ID**, trả lời câu hỏi mở cũ ở phần cuối file

`Stage_Get_Datas.listIgroneEnemies` đọc được **31 phần tử**
(`statics_Stage_Get_Datas.json` · `.fields.listIgroneEnemies`):

```
30009 30015 30016 38001 30029 30030 31011 31012 31014 38002 30031 30032 30033
30034 30035 30036 30037 30038 30039 30040 30041 35008 35014 35015 35053 35026
35027 35042 35043 35045 35029
```

Đây là **danh sách loại enemy bị `GetCountEnemies` bỏ qua**. Hệ quả trực tiếp: mẫu số
`countEnemies(stage)` **nhỏ hơn** tổng 45.659 toàn game, và mức nhỏ hơn bao nhiêu thì
**chưa tính được** — cần biết 31 ID này chiếm bao nhiêu bản ghi trong `waves.json`.
Đó là phép tính **làm được offline**, không cần thiết bị (xem "Còn thiếu" §8).

---

### 7.3 Đã resolve **9/9 số** + mẫu số stage 2/3 (25/10, review R1)

Ba mảng `static` đọc thẳng từ `field_default` của `<PrivateImplementationDetails>` — **không** phải
đoán từ tên hàm, không cần screenshot:

| `ModeCurrent` | slot | float32 | hex | Ý nghĩa |
|---|---|---|---:|---|
| **0** | `0x2ae8b88` | **0.20 / 0.45 / 0.80** | `cdcc4c3e 6666e63e cdcc4c3f` | chế độ 0 |
| **1** | `0x2ae8b80` | **0.35 / 0.60 / 0.98** | `3333b33e 9a99193f 48e17a3f` | chế độ 1 |
| **khác 0/1** | `0x2ae8b78` | **0.50 / 0.80 / 1.00** | `0000003f cdcc4c3f 0000803f` | **fallback** |

**Mẫu số** (normal, non-branch, `ChapterCurrent = 0`, `LevelCurrent = 0`):

| Stage hiển thị | Wave mặc định | Slot không marker − ID38001 | `GetCountEnemies` |
|---|---|---:|---:|
| 2 | `0164` | 274 − 12 | **262** |
| 3 | `0113` + `0005` | (95 − 8) + (155 − 4) | **238** |

**Ngưỡng `{0}`** = `fcvtzs(pct × denominator)` (không `ceil`):

| Stage | Mode 0 | Mode 1 | Khác 0/1 |
|---|---|---|---|
| 2 (262) | **52 / 117 / 209** | 91 / 157 / 256 | 131 / 209 / 262 |
| 3 (238) | **47 / 107 / 190** | 83 / 142 / 233 | 119 / 190 / 238 |

Kết quả `GetMissionCompleted` được gọi là **tier 0/1/2**, **không** tự gọi "1/2/3 sao UI".

**Phạm vi — đừng mở rộng:** bảng này là campaign `GameMode0`, non-branch, mission thường.
**Không** áp cho `Chapter2`, branch, special mission 3/4, challenge, map debug hay bản Premium.
Đây là mẫu số **cấu hình theo thuật toán**, không phải số object đang sống hay số kill chắc chắn đạt được.

Nguồn (đã kéo về repo, xem `DATA_SYNC.md` §kéo 25/10): `reverse-engineering/raw/early-waves/mission-denominators.json.gz`,
`raw/endgame-missions/mission-progress-flow.json.gz`, `raw/ui-audit/enemy-exit-missions.json.gz`;
đường đọc: `docs/apk-analysis/56-early-stage-mission-denominators.md`, `57-endgame-mission-stars-save-continue.md`.

## 8. Còn thiếu / phải đoán

- ~~Giá trị `pct[mode][slot]` chưa đọc~~ → **đã đọc đủ 9/9** (§7.3). Ba mảng `float[3]` và **ánh xạ
  chế độ đã rõ**: mode 0 `0x2ae8b88`, mode 1 `0x2ae8b80`, **khác 0/1 → fallback `0x2ae8b78`**.
- ~~`countEnemies` cho từng stage chưa có~~ → **có mẫu số stage 2/3**: **262** và **238** (§7.3).
  Vẫn **chưa** có cho mọi stage và cho branch / Chapter2 / special mission — đừng ngoại suy.
- ~~`PercentToCompleteMissions222` = `[0.2, 0.6, 0.98]` … chưa biết 3 phần tử là gì~~ → **dòng này SAI
  và đã bỏ.** Giá trị đó là **trộn** hai mảng khác nhau; ba mảng thật là `[.20,.45,.80]`,
  `[.35,.60,.98]`, `[.50,.80,1.00]`, và mỗi mảng là **3 tier của một chế độ** (§7.3).
- ~~`0x12b79a8` / `0x12b7860` chưa export ⇒ nghi tính từ kills~~ → **`0x12b79a8` đọc `savedStars`
  (`GetStarStageMaster`)**, không phải kills (§2 + §7.3). Không còn là ẩn số về *nguồn số*; chỉ còn
  **chưa** export `0x12b7860` (nhánh branch) — nhánh branch ngoài phạm vi bảng §7.3.
- **Số sao tối đa** = 3 chỉ là **B** (§2). `SetStarCheat` mặc định `star = 5` không chặn.
- **Bảng 6 loại nhiệm vụ ↔ 6 nguồn đếm** là **B** — nối theo *hàm nào được gọi trong `GetStringInfo`*,
  chưa đọc hết 6 nhánh. **Điều kiện lật ngược:** một stage thật có loại nhiệm vụ khác bảng §3.
- **`listIgroneEnemies`** (31 ID, §7.2): **đã tính cho stage 2/3** — chính là 12 và 8+4 slot bị loại
  (`§7.3`). **Chưa** tính cho các stage còn lại; với những stage đó mẫu số 45.659 vẫn là **cận trên**.
