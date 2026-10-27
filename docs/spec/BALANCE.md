# BALANCE — số liệu WindWings: Space Shooter (bản spec hoá)

> **asm-check** (bản `6109008c`): **16/17 PASS** · `size_capped` **0/425** · ❌ `RankManager` thiếu **8 B** (`ctor` rỗng) — xem **`ASM_INTEGRITY.md`**. Mọi kết luận phủ định trong file này chỉ đúng trong **17 class đã export**.

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
| Số wave / spawner | **282 wave** (236 campaign + 45 boss), **48 archetype**, **10.782** cấu hình khác nhau sau dedup (11.089 dòng), 250 map | `waves.json` → `ENCOUNTERS.md` §1–2 |
| Giá coin/gem/IAP | **0 cột giá** trong 91 CSV — **không thấy** trong asset (phạm vi: chỉ CSV) | `ECONOMY.md` §0 |
| Phần thưởng trong hộp | **0 giá trị** — `Box_Rewards.id = 0` cho 1065/1065 dòng (đo lại 25/10) | `Box_Rewards.csv` |
| Damage của **player** | **0 giá trị** — `forceType = Enemy` 458/458 | `Gun_Attack.csv` |
| Có thể dựng lại balance đầy đủ? | Không. Nhưng đã có **HP + damage địch + nhịp wave** — đủ để suy đường cong | §7 |

---

## 0.5 ⚠ HP enemy thường **không tồn tại trong dữ liệu** — 231/236 wave = 0

Đo trên bản `cd0372d` bằng `prefab_joins` × `waves.json`.

| | Số |
|---|---:|
| Wave campaign | 236 |
| **Wave campaign có HP > 0** | **1** (`Wave_0136`, 2,44 triệu) |
| Tổng HP 236 wave campaign | **2.440.000** |
| Tổng HP 45 wave boss | **574.155.800** |
| HP trung bình **mỗi boss instance** | **≈ 6,38 triệu** |
| HP trung bình **mỗi quân campaign** | **≈ 54** |

**Vì sao:** `Enemy_Datas.StartHealthPoint` = **0 ở 514/981** dòng, và `datas/enemy_hp.json` ghi
*"runtime HP is scaled by `Enemy_Data_Balance` and stage"*.

⚠ **Hai điều phải nói kèm mọi bảng HP trong file này:**

1. **HP boss** (206.167.000 cho 39 prefab) là **HP một bản mỗi prefab**, không phải HP một trận.
   Một trận boss có **2 boss × copies** ⇒ tổng 90 instance = **574 triệu**.
2. **HP enemy thường** trong bảng là **hằng số 0**. Mọi con số "HP enemy median" phải đọc là
   *"giá trị serialize, thực tế do công thức"*.

> **Nhận định (mức A):** không thể suy độ khó campaign từ HP prefab. Phải chọn công thức riêng
> và calibrate bằng số quân + nhịp spawn (đã có: `1,0 s/con`, `rate` 1,0 ở **7.741/11.089** dòng (69,8 %)).

## 0.6 HP player — **công thức đầy đủ**, chỉ thiếu đúng **một** giá trị

Đọc trực tiếp từ `raw/il2cpp-consts/Player_Get_Datas.asm.txt` (arm64) + `dump.cs.gz`.
Đây là chỗ **không** có trong ScriptableObject nào — HP được **tính lúc chạy**.

### 0.6.1 Công thức (mức **A** — đọc từng lệnh)

```
GetStartHp()        = StartHp × (1 + GetHpStatPercent())

GetHpStatPercent()  = stepCommon × Tech_Datas.GetTechStatPoints(0)
                    + abi7AddPlayerStartHp × GP_Datas.GetNumberAbility(7)
```

Bằng chứng lệnh (địa chỉ thật):

| Địa chỉ | Lệnh | Nghĩa |
|---|---|---|
| `0x14e3168` | `ldr s8, [x8, #0x6c]` | `s8 = StartHp` |
| `0x14e316c` | `bl #0x14e318c` | gọi `GetHpStatPercent()` → `s0` |
| `0x14e3178` | `fmov s1, #1.0` | hằng **1,0** |
| `0x14e317c` | `fadd s0, s0, s1` | `1 + pct` |
| `0x14e3180` | **`fmul s0, s8, s0`** | **`StartHp × (1 + pct)`** ← chính là công thức |

`GetHpStatPercent` (từ `0x14e31f8`):

| Địa chỉ | Lệnh | Nghĩa |
|---|---|---|
| `0x14e3200` | `bl #0x1399aa4` | **`Tech_Datas.GetTechStatPoints(0)`** → `w19` |
| `0x14e3228` | `ldr s8, [x8, #0x68]` | **`stepCommon`** |
| `0x14e3230` | `ldr s9, [x8, #0x314]` | **`abi7AddPlayerStartHp`** |
| `0x14e3244` | `bl #0x14c7758` | **`GP_Datas.GetNumberAbility(7)`**, tham số `w0 = 7` |
| `0x14e3258` | `fmul s0, s8, s0` | `stepCommon × điểm stat` |
| `0x14e325c` | `fmul s1, s9, s1` | `abi7 × ability 7` |
| `0x14e3260` | **`fadd s0, s0, s1`** | **cộng hai nguồn** |

Địa chỉ → method được xác định bằng `RVA` trong `dump.cs.gz`:
`0x1399aa4` = `GetTechStatPoints` · `0x14c7758` = **`GP_Datas.GetNumberAbility`**.

### 0.6.2 Ba nguồn HP — đúng như trực giác "khởi tạo + giáp + tính trong màn"

| Lớp | Nơi khai báo | Vai trò |
|---|---|---|
| **1. HP gốc** | `Player_Get_Datas.StartHp` (static float, `@0x6C`) | giá trị nền của tàu |
| **2. Nâng cấp** | `Tech_Datas.GetTechStatPoints(0)` × **`stepCommon`** | stat index **0** của tech lab |
| **3. Ability** | `GP_Datas.GetNumberAbility(7)` × **`abi7AddPlayerStartHp`** | ability **7** = "+HP khởi đầu" |
| **4. Lúc vào màn** | `Player_Health.StartHealth` (static, `@0x0`) | = `GetStartHp()` |
| **5. Trong màn** | `Player_Health.CurrentHealth` (static, `@0x4`) | HP hiện tại |
| **6. Giáp** | `Player_Health.Armor` (instance, `@0x20`) | **giảm damage nhận**, không cộng vào HP |
| **7. Giảm damage khác** | `reduceDamageByDevice` (`@0x58`) · `HasShieldOneHit` (`@0x31`) · `Invincible` (`@0x30`) · `timeToImmuneOneHit` (`@0x2C`) | theo thiết bị và khiên 1 đòn |

⚠ **Giáp tách khỏi HP:** `Armor` **không** nằm trong công thức `GetStartHp` — nó được dùng trong
`Player_Health.TakeDamage(Damager damager, bool ignoreInvincible = False, Action dieCallback)`.
`Damager` chỉ có **2 field**: `float damage` + `Action<GameObject> killEvent` ⇒ **giáp phải được trừ
bên trong `TakeDamage`**, không nằm ở `Damager`.

> ~~**Nhận định (mức B):** ...~~ **SUPERSEDED 25/10 (report 81 §E + 85):** công thức thật đã đọc —
> enemy: `factor = 100/(100+armor)` (armor<0 ⇒ `2−100/(100−armor)`); player: 2 truncations rồi
> synchronous events 21/39 → HP re-read. `Armor` đúng là gán lúc chạy, **không per-prefab serialize**.

### 0.6.3 Còn thiếu **đúng một** giá trị: `StartHp` — và **lý do đã tìm ra**

⚠ **ĐÍNH CHÍNH quan trọng (bản `8871068a`).** Toàn bộ mục này trước đây kết luận *"`StartHp` không
được gán trong bất kỳ lớp nào đã export"* dựa trên **4 phép tìm âm tính**. **4 phép đó đều vô hiệu**,
vì lý do ở §0.6.3a.

#### 0.6.3a **File asm bị cắt cụt — 11/12 file**

> ⚠ **Mục này là BẢN GHI LỊCH SỬ** của bản export `8871068a`. Bản `6109008c` **đã hết cụt**
> (`size_capped` 0/425); cách kiểm nay nằm ở `ASM_INTEGRITY.md`. Đọc mục này để biết **vì sao**
> 3 kết luận âm tính cũ bị rút, **không** đọc để lấy số hiện hành.

Đo trực tiếp: lệnh cuối cùng của mỗi file.

| File | Method (header) | Số lệnh | Lệnh cuối | Kết thúc bằng `ret`? |
|---|---|---|---|---|
| `ArenaManager` | 27 | 1.880 | `ret` | ✅ **trọn** |
| `Device_Get_Data` | 13 | 4.393 | `bl #0x1bd7e58` | ❌ cụt |
| `Droid_Data_Balance` | 11 | 1.618 | `mov x0, x20` | ❌ cụt |
| `Enemy_Data_Balance` | 7 | 927 | `mov x0, x19` | ❌ cụt |
| `GameDatas` | 72 | 4.582 | `ldr x8, [x8, #0xd98]` | ❌ cụt |
| `IAP_Manager` | 34 | 2.170 | `ldp x30, x21, [sp], #0x20` | ❌ cụt |
| `Map_Get_Datas` | 8 | 772 | `bl #0x110d258` | ❌ cụt |
| `Player_Datas` | 1 | 256 | `ldr x9, [x0, #0xb8]` | ❌ cụt |
| `Player_Get_Datas` | 61 | 5.341 | `ldr x22, [x22, #0x858]` | ❌ cụt |
| `RankManager` | 17 | 1.010 | `bl #0x122787c` | ❌ cụt |
| `Stage_Get_Datas` | 10 | 2.328 | `ldr x8, [x8, #0xc0]` | ❌ cụt |
| `Tech_Datas` | 24 | 7.348 | `mov x2, x20` | ❌ cụt |

> **Đọc xong bảng này phải dừng ở đây:** đó là trạng thái bản `8871068a`. Bản hiện hành
> **`6109008c` đã hết cụt** (`size_capped` **0/425**), và `Stage_Get_Datas` **đã decode 2/2 mảng**
> (`startBonusValues` int[5] · `levelDelta` float[4], §6.4). **Không** dùng cột "❌ cụt" để xin dump lại.

**Cái bị cắt là đuôi của method CUỐI** — và ở **8/12 file**, method cuối chính là **`.cctor`**.
`Player_Get_Datas..cctor` bắt đầu dòng 5.206 và **dừng giữa chừng tại `0x14e5cc4`**, vẫn đang dựng
`List`, **chưa tới đoạn gán các float stat**.

⇒ Hệ quả **phải ghi nhớ**: *"không thấy lệnh ghi"* trong các file này **không** đồng nghĩa
*"không tồn tại lệnh ghi"*. Mọi kết luận âm tính dựa trên asm phải kèm điều kiện **"trong phần đã
export"**.

#### 0.6.3b Rút lại 4 kết luận âm tính cũ

| Hướng đã thử | Kết luận cũ | Trạng thái **đúng** |
|---|---|---|
| `.cctor` của `Player_Get_Datas` | ❌ "không gán `StartHp`, chỉ 1 lệnh ghi" | ⚠ **vô hiệu** — `.cctor` **bị cắt** trước khi tới đoạn stat |
| Quét 11 file asm tìm ghi float vào `#0x6c` | ❌ "0 lệnh" | ⚠ **vô hiệu** — 11/12 file cụt |
| `Player_Saved_Datas` | ❌ "chỉ toàn `int[]`" | ✅ **vẫn đúng** (đọc từ `dump.cs`, không phụ thuộc asm) |
| `script-links.jsonl.gz` 127.659 dòng | ❌ "không có `StartHp`" | ✅ **vẫn đúng** (dữ liệu thô đầy đủ, không bị cắt) |
| *"Không có lệnh ghi `#0x314` (abi7)"* | ❌ | ⚠ **vô hiệu** — cùng lý do |
| *"`GetStartHp` chỉ được 2 method gọi"* | — | ⚠ **không đầy đủ** — caller có thể nằm trong phần bị cắt |

⇒ Chỉ còn **2** kết luận âm tính đứng vững, và cả hai **không** dựa vào asm.

#### 0.6.3c Vậy `StartHp` nằm ở đâu — giả thuyết hẹp nhất

**Ba khả năng, xếp theo xác suất:**

1. **Đuôi `.cctor` bị cắt** của `Player_Get_Datas` (cao nhất) — `.cctor` đang dựng List khi bị cắt;
   các float stat (`StartHp`, `stepCommon`, `TouchRanger`…) thường được gán **sau** phần List.
   Bằng chứng gián tiếp: `.cctor` **đã** chứa đúng **1** hằng float `0x41700000` = **15,0** — chứng
   tỏ .cctor **có** gán float, chỉ là chưa tới lượt `StartHp`.
2. **`RuntimeHelpers.InitializeArray` từ field RVA data** — như 3 bảng của device (`BALANCE` §0.6.7e).
   Khi đó `StartHp` là **scalar trong metadata**, không cần lệnh ghi nào.
3. Một class **chưa export** gán lúc chọn tàu.

> **Nhận định (mức B):** khả năng 1 + 2 chiếm phần lớn; cả hai đều **lấy được** bằng **một yêu cầu
> dump rất nhỏ**: *đuôi `.cctor` của `Player_Get_Datas`* (không phải cả class 5.341 lệnh).
>
> **Điều kiện lật ngược:** nếu đuôi `.cctor` không chứa `StartHp`, chuyển sang khả năng 3 và phải
> dump `Player_Health.asm.txt` + class gán.

**Đề nghị cụ thể (nhỏ, có biên):** dump **200 lệnh tiếp theo** sau `0x14e5cc4` của
`Player_Get_Datas..cctor`. Đây là yêu cầu **hẹp nhất** trong toàn bộ dự án còn lại.


### 0.6.4 HP có theo **tàu** không? — **hai lớp, hai câu trả lời**

⚠ **Đây là chỗ tôi suýt kết luận sai.** Kiểu khai báo **không** chứng minh HP không theo tàu:
`StartHp` là `float` đơn, nhưng nó **có thể được gán lại mỗi lần chọn tàu** trước khi
`Player_Health.Start()` chạy. Phải tách hai lớp:

**Lớp 1 — dữ liệu serialize (mức A): KHÔNG có bảng HP theo tàu.**

| Field | Kiểu | Nghĩa |
|---|---|---|
| `StartHp` | **`float`** | **một** giá trị tại một thời điểm — không phải mảng |
| `StartMainCannonDamages` | **`float[]`** | damage **riêng từng tàu** |
| `StartWingCannonDamages` | **`float[]`** | damage pháo cánh **riêng từng tàu** |
| `StartMainCannonRate` | **`float[]`** | **khoảng giữa 2 phát** (interval) — tàu 1 chứng minh (report 79); 23 tàu chưa xét |
| `StartSecretWeaponDamage` | `float` | dùng chung |

`Data_Players` / `Player_Info` (25 tàu) chỉ có `id · Sprite · Star · Actived` — **0 field HP**.

#### 1.1b **Đã decode 6 mảng** (25/10) — bảng số thật, không còn "không serialize"

Nguồn: `reverse-engineering/il2cpp/ia-resolved.json#Player_Get_Datas.cctor` → `datas/player_start_stats.json`.
Mỗi mảng là **hex của `InitializeArray`**, giải mã **theo kiểu field** (int32 nếu `int[]`, float32 nếu `float[]`);
store offset kiểm bằng asm: `0x38 / 0x78 / 0x80 / 0x88 / 0x1C8 / 0x308`.

| index | `PlayerCosts` (coin, −1 = không bán) | `StartMainCannonDamages` | `StartMainCannonRate` | `StartWingCannonDamages` | damage × rate (**proxy** — KHÔNG phải DPS chứng minh, report 79) |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 4500 | 4.8 | 218 | 21600 |
| 1 | 0 | 220 | 6.8 | 75 | 1496 |
| 2 | 1050 | 2680 | 4.8 | 186 | 12864 |
| 3 | 3150 | 8000 | 5.8 | 118 | 46400 |
| 4 | -1 | 710 | 4.8 | 236 | 3408 |
| 5 | 3850 | 1650 | 4.8 | 309 | 7920 |
| 6 | 4550 | 255 | 5 | 365 | 1275 |
| 7 | 2450 | 800 | 4.8 | 99 | 3840 |
| 8 | 2450 | 500 | 4.8 | 165 | 2400 |
| 9 | -1 | 95 | 4.8 | 725 | 456 |
| 10 | 3850 | 336 | 4.8 | 230 | 1612.8 |
| 11 | -1 | 3000 | 4.8 | 2800 | 14400 |
| 12 | 3150 | 2350 | 6.8 | 595 | 15980 |
| 13 | 4550 | 400 | 10.5 | 800 | 4200 |
| 14 | 4550 | 515 | 4.8 | 265 | 2472 |
| 15 | -1 | 3000 | 10.5 | 2150 | 31500 |
| 16 | 4550 | 2689 | 5.6 | 589 | 15058.4 |
| 17 | 2450 | 1800 | 4.8 | 345 | 8640 |
| 18 | -1 | 100 | 12 | 250 | 1200 |
| 19 | 4550 | 2250 | 7.5 | 435 | 16875 |
| 20 | -1 | 100 | 9 | 1650 | 900 |
| 21 | 4550 | 2800 | 10.5 | 686 | 29400 |
| 22 | -1 | 110 | 9 | 400 | 990 |
| 23 | -1 | 3300 | 10.5 | 820 | 34650 |

- `shipCloneDamage` = **1,35 · 1,6 · 1,86** (`0x1C8`) · `PercentToCompleteMissions222` = **0,2 · 0,6 · 0,98** (`0x308`).
- **16/24** tàu có giá ≥ 0; **8** tàu `−1`. `PlayerCosts` là **int**, ba mảng damage/rate là **float** — trước đây
  mình đọc nhầm cả 4 là float*24, xem `DATA_SYNC.md` §21.
- `index` là **playerIndex của implementation** — **KHÔNG phải `id − 10001` cho combat** (sửa 25/10
  theo report 81/82 peer): impl `Player_Attack_N` đọc mảng index **N−1** (CFG 72/72); tàu
  **10001→index 2** · **10003→index 0** · 10004–10024 → id−10001. `0x14e2ce4` (id − 10001) giữ nguyên
  ở consumer **save/load**.
  **⚠ DPS = damage × rate KHÔNG phải DPS chứng minh** (reports 79–83): rate = base × (1 − percent
  tech `GetTechStatLevel(1)` — tier **0/3/5/8/10/12 %**); là **interval nhóm phát** (dual deadline,
  N extra ⇒ N+1 entry, không catch-up); demo override 3,0/4,0; crit random ≤ critPercent ⇒ ×2.
  Tích damage×rate có đơn vị **damage·s** — **không dùng xếp tàu / lập TTK** (review peer 25/10);
  DPS measured: peer đã dịch receivers (report 85), đang nối producer/serialized + extra-life (86).
- HP vẫn **không** có bảng theo tàu: `StartHp` là **một** float.
⇒ Nếu mỗi tàu có HP riêng, bảng đó **không** nằm ở ScriptableObject; phải là **mảng cứng trong
code** hoặc gán ở chỗ khác.

**Lớp 2 — runtime (mức C, CHƯA kiểm được):** `StartHp` **có thể** được gán theo tàu trong
`Player_Health.Start()` hoặc trong luồng chọn tàu. Không có asm của `Player_Health` nên **chưa
kết luận được**. Đây đúng là giả thuyết *"HP là của tàu, boot đầu màn khi chọn"*.

> **Điều kiện lật ngược (quan trọng):** nếu `Player_Health.Start()` gán `StartHp` theo
> `playerIndex` / `Player_Ingame.currentPlayer` thì **HP CÓ theo tàu** và câu "dùng chung" là **sai**.
> Cách kiểm: dump `Player_Health.asm.txt` (RVA `0x14C6B5C`), tìm lệnh **ghi** `#0x6c` trên
> `Player_Get_Datas`.

**Lớp 3 — trang bị (mức A): device không cộng HP tối đa.**

| Nguồn | Cộng HP? | Bằng chứng |
|---|---|---|
| **Tàu** (25 chiếc) | ⚠ **chưa kết luận** | serialize **không** có bảng HP theo tàu (mức A); `StartHp` **có thể** gán lại lúc chọn (mức C) |
| **Tech lab** (stat index 0) | ✅ `stepCommon × TechStatPoints(0)` | asm `0x14e3258` `fmul` |
| **Ability 7** | ✅ `abi7AddPlayerStartHp × GetNumberAbility(7)` | asm `0x14e325c` `fmul` |
| **Trang bị (device)** | ❌ **KHÔNG cộng HP tối đa** — chỉ **giảm damage** (`reduceDamageByDevice`) và **hồi máu** (`amountAutoGainHpByDevice`); chi tiết §0.6.7d | `OnChangeDataDevice` 452 B đọc đủ: không ghi `StartHealth` |
| **Drone** | ❌ không | `Droid_Data_Balance.GetBaseDamage` — drone đóng góp **damage** |

> **Nhận định (mức A):** trong **công thức đã đọc**, HP tối đa chỉ có **3 số**: `StartHp` (gốc) ·
> điểm tech stat **0** · ability **7**. Không có nguồn thứ tư nào cộng vào HP tối đa **bên trong
> `GetStartHp()`**. Điều này **không** loại trừ việc `StartHp` bị gán theo tàu **trước** khi gọi.

**Boot lúc nào:** `Player_Health.Start()` (`RVA 0x14C6B5C`) → `StartHealth = GetStartHp()`,
`CurrentHealth = StartHealth` — đúng **lúc vào màn, sau khi chọn tàu**.

**Hai ứng viên cho `playerLv` trong `stepLevel` (4 ngưỡng 30/58/118/248):**

| Ứng viên | Nơi khai báo |
|---|---|
| `Player_Ingame.lv` (**`private static int`**, `@0x4`) + property `Level` | cấp trong màn |
| `Player_Saved_Datas.MaxLevelPerRanks` (**`int[]`**) + `MAX_RANK_INDEX` | cấp theo **rank tài khoản** |

> **Nhận định (mức C):** 30/58/118/248 quá cao cho một màn ⇒ nghiêng về **cấp tài khoản/rank**.
> **Điều kiện lật ngược:** nếu `Player_Ingame.Level` lên được 248 trong một màn (power-up dồn)
> thì đó mới là biến đúng.

### 0.6.5 Cái gì **chung cho mọi tàu**, cái gì **riêng từng tàu** — kiểm bằng chữ ký hàm

Đây là phép đo mạnh nhất cho câu *"tài năng và nâng cấp chung cho mọi tàu, cộng vào tàu được chọn"*:
đếm xem method nào **nhận `playerIndex`**, method nào **không**.

`Player_Get_Datas` có **40 method trả `float`/`int`**. Kết quả:

| Loại | Số | Danh sách |
|---|---:|---|
| **Nhận `playerIndex`** (riêng từng tàu) | **7** | `GetMainCannonDamage` · `GetMainCannonRate` · `GetWingCannonDamage` · `GetWingCannonDamageByBase` · `GetWingCannonDamageByTech` · `GetCostUnlockPlayer` · `GetCostStarUnlockPlayer` |
| **Không tham số** (dùng chung) | **33** | xem bảng dưới |

⇒ **Chỉ 5 method stat là riêng từng tàu — và cả 5 đều là DAMAGE / NHỊP BẮN.**
Không có method HP nào nhận `playerIndex`.

**33 method dùng chung (đầy đủ):**

| Nhóm | Method |
|---|---|
| **HP** | `GetStartHp` · `GetHpStatPercent` · `GetHpRecoverSpeed` · `GetGainHpItem` · `GetGainHpItemAddOverTime` · `GetGainHpItemAddTime` · `AddPowerPercentWhenHpBelow30` · `GainHpPercentWhenUseOverDrive` · `KillPercentWhenEnemyHpBelow30` |
| **Talent (8)** | `GetTalentBombDamage` · `GetTalentRocketDamage` · `GetTalentLaserDamage` · `GetTalentStunDamage` · `GetTalentMegaBombDamage` · `GetTalentInvisibleRanger` · `GetTalentInvisible2Ranger` · `GetTalentStunRanger` |
| **Crit / % cộng thêm** | `GetMainCannonCritPercent` · `GetMainCannonRatePercent` · `GetMainCannonStatPercent` · `GetWingCannonStatPercent` |
| **Overdrive / thời gian** | `GetTimeFreeOverdrive` · `GetMaxChargeDuration` · `GetSecretWeaponDuration` · `TimeToImmuneOneHit` · `GetPercentDropFreeOverDriveEvery30Seconds` |
| **Từ / nam châm** | `GetMagnetRange` · `GetMagnetStatPercent` · `GetSecretWeaponDamage` · `GetSecretWeaponStatPercent` |

> **Nhận định (mức A):** mô hình đúng là **"tàu = khung xác + damage riêng; mọi thứ khác là cộng dồn
> chung"**. Người chơi nâng tech/talent **một lần**, áp cho **mọi tàu**; đổi tàu chỉ đổi **damage và
> nhịp bắn**.
>
> **Điều kiện lật ngược:** nếu `GetTalent*` bên trong đọc `Player_Get_Datas.listIdPlayerActived` hay
> chỉ số tàu đang chọn thì talent **có** thể khác theo tàu — nhưng **chữ ký không nhận tham số**, nên
> nếu có thì nó phải đọc qua static state. Chưa thấy dấu hiệu đó trong trace.

### 0.6.6 Ba giả thuyết về nguồn HP — cái nào đứng, cái nào không

| Giả thuyết | Kết quả | Bằng chứng |
|---|---|---|
| **Boot đầu mỗi màn** | ✅ **ĐÚNG** (A) | `Player_Health.Start()` (`RVA 0x14C6B5C`) gán `StartHealth = GetStartHp()`, `CurrentHealth = StartHealth` — cả hai **`static`** |
| **Drone cộng HP** | ❌ **Không** (A) | `Droid_Data_Balance` có **11 method**, **0 method trả HP**: `GetBaseDamage` · `GetDroidTimeOut` · `GetUnlockCost` · `GetUnlockStarCost` · `GetUpgadeCostCoins` · `GetUpgradeCostGems` · `GetDroidRank` · `SetDroidLevel` · `IsBought` · `SetBought` · `.cctor` |
| **Danh hiệu / rank cộng HP** | ❌ **Không** (A) | `RankManager` **14 method — toàn bộ là leaderboard online**: `IECheckCampaignRankings` · `IESetCampaignRankings` · `IETryGetRoomRankCampaign` · `IECheckRankReadyToUploadPoint` · `CheckUserSignInOrRestoreYourDatas`… **không có stat nào** |
| **Buff riêng chọn trước màn** | ❌ **không có hệ thống này** (B) | Không có class `Buff`/`PowerUp`. `PowerUp` là field **theo chỉ số tàu**: `p1_idBltPowerUp` · `p1_superPowerUpShotRate` · `p3_…` · `p5_…` · `p6_…` ⇒ power-up **thuộc tàu**, không phải buff chọn |
| **Trang bị (device) cộng HP** | ❌ **KHÔNG** (A) | `OnChangeDataDevice` chỉ ghi 2 field: `reduceDamageByDevice` (giáp) + `amountAutoGainHpByDevice` (hồi theo `% StartHealth`); **0 lệnh** ghi `StartHealth` |
| **Tàu cộng HP** | ⚠ **chưa kết luận** (C) | `Data_Players` **0 field HP**; `GetStartHp()` **không nhận `playerIndex`**; **nhưng** `StartHp` là `float` static và **không có lệnh ghi nào** trong 11 class asm ⇒ **không loại trừ** việc nó bị gán lại theo tàu lúc chọn |

> **Nhận định (mức B):** xét **toàn bộ API của drone và rank**, cả hai **không có đường nào** trả về HP.
> Nên nếu HP có phụ thuộc chúng thì phải qua một class **không export asm**.
>
> **Điều kiện lật ngược:** export `Player_Health.asm.txt` + `GameDatas.asm.txt` đầy đủ. Nếu `StartHp`
> bị gán theo `playerIndex` hoặc theo rank thì bảng trên phải sửa **2 dòng** (tàu, danh hiệu).

### 0.6.7 **Trang bị (device)** — 5 loại, mỗi loại **2 stat**, và một nhánh `%`

Cấu trúc đọc từ `Device_Get_Data.asm.txt` + `dump.cs.gz`.

**a) Dữ liệu lưu:** `Device { int id; int lv; int rank; int instanceId; }` — **chỉ 4 số nguyên**.
Stat **không** lưu trong device; nó được **tính** từ `id`, `lv`, `rank` qua bảng static.

**b) Công thức `GetStatValue1`** (đọc từng lệnh):

```
type = id / 100 − 1                 // magic 0x10624DD3 = chia 100
base = listStatValues[type][rank]   // float theo rank
pct  = percentByLevels1[type] × (lv + 1)
kết quả = base + pct
if (type == 4) kết quả /= 100       // 0x42C80000 = 100.0
```

`GetStatValue2(Device)` dùng **`percentByLevels2`** — cùng công thức, và **cũng** có nhánh
`cmp w20, #4` + `fdiv` ⇒ **cùng quy ước type 4 = phần trăm**.

**c) Bằng chứng "5 loại" và "2 stat/loại":**

| Bằng chứng | Giá trị |
|---|---|
| `.cctor` tạo mảng với `mov w1, #5` | **5 phần tử** cho mỗi bảng |
| `cmp w20, #4` (nhánh %) | index chạy **0…4** ⇒ **5 loại** |
| Hai hàm `GetStatValue1` / `GetStatValue2` | **2 stat mỗi device** |
| Bảng static | `listStatValues` (`List<float[]>`) · `percentByLevels1` · `percentByLevels2` |

**d) Device ảnh hưởng gì lên HP — 3 đường, không phải 1:**

| Field / method trong `Player_Health` | Tác dụng |
|---|---|
| `OnChangeDataDevice(int _idPlayer)` | **chạy khi đổi device** — đường nối device → HP |
| `amountAutoGainHpByDevice` | lượng **hồi HP** theo device |
| `reduceDamageByDevice` | **giảm damage** nhận vào theo device |

✅ **ĐÃ CHỐT bằng thân hàm (A) — bản `6109008c`.** `Player_Health.asm.txt` có đủ
`OnChangeDataDevice` (452 B). Đọc từng lệnh:

```
reduceDamageByDevice (@0x58)      = 0
amountAutoGainHpByDevice (@0x28)  = 0
devices[] = Player_Device_Saved_Datas.GetPlayerDevices(_idPlayer)      // 0x14e628c
for (i = 0; i < devices.Length; i++) {
    if (devices[i] == -1) continue;                                    // cmn w21,#1
    Device d = Device_Get_Data.GetDevice(devices[i]);                   // 0x12546d0
    if ((uint)(d.id − 1000) <= 999)          // dải 1000–1999  → GIÁP
        reduceDamageByDevice += GetStatValue1(d) / 100.0;               // fdiv 0x42C80000
    else if ((uint)(d.id − 5000) <= 999)     // dải 5000–5999  → HỒI MÁU
        amountAutoGainHpByDevice += StartHealth × GetStatValue1(d) / 100.0;
}
```

⇒ **`OnChangeDataDevice` KHÔNG ghi vào `StartHealth`.** Nó chỉ đặt **2 field**:
**giảm damage** và **lượng hồi HP theo % HP tối đa**.

⚠ **Đính chính lần ba — lần này là đính chính của chính đính chính:** tôi đã viết *"device không
cộng HP"* (đúng), rồi sửa thành *"device **có** cộng HP tối đa"* (❌ **sai** — lúc đó chưa có asm,
chỉ suy từ tên hàm). **Kết luận đúng:**

| Phát biểu | Đúng? |
|---|---|
| device **cộng HP tối đa** | ❌ **sai** — `StartHealth` không bị chạm |
| device **giảm damage** nhận vào | ✅ (`reduceDamageByDevice`, cộng dồn theo %/100) |
| device **tăng hồi máu** theo % HP tối đa | ✅ (`amountAutoGainHpByDevice = StartHealth × stat%/100`) |

⇒ HP tối đa **chỉ** = `StartHp × (1 + 0,18 × TechStatPoints(0) + abi7 × GetNumberAbility(7))`.
Device làm **HP hiệu dụng** tăng lên, đúng nghĩa "giáp": `HP_eff = HP / (1 − reduceDamageByDevice)`.

**Hai dải id của device (A):**

| Dải `device.id` | Tác dụng |
|---|---|
| **1000–1999** | giáp: `reduceDamageByDevice += stat%/100` |
| **5000–5999** | hồi máu: `amountAutoGainHpByDevice += StartHealth × stat%/100` |

**e) Giá trị tĩnh đã giải; đối chiếu runtime còn mở (Report 119):** `.cctor` của `Device_Get_Data` có 12 `InitializeArray` captures: **10** mảng `listStatValues` (`float[5]`) + **2** mảng `percentByLevels1/2`. Giá trị tĩnh đã decode trong `datas/device_table.json`; runtime 1.0.69 lưu trữ báo list length 10 nhưng chỉ trả tên kiểu cho các mảng lồng. Hai mảng phần trăm khớp với static captures ở độ chính xác float32. Vì vậy đã có giá trị tĩnh, nhưng mười hàng trong list **chưa** được đối chiếu giá trị với runtime của build khác; không tuyên bố parity cùng build.

### 0.6.8 **Vòng đời**: số của player được chốt **lúc nào**

Đây là câu hỏi *"các thứ của player tính khi vào màn chơi"* — trả lời bằng **thân hàm**, không bằng tên.
Nguồn: `Player_Datas.asm.txt` (file này **chứa cả method của `Player_Health`** — xem ghi chú (e)),
`dump.cs.gz` dòng 73874–73960.

**a) `StartHealth` là `static` — không phải field của instance**

```csharp
public static float StartHealth;   // 0x0   ← static, MỘT giá trị cho cả phiên
public static float CurrentHealth; // 0x4   ← static
```

⇒ HP tối đa **dùng chung một biến toàn cục**, không phải mỗi tàu một bản trong `Player_Health`.

**b) `ResetStaticVariables()` — 2 lệnh, đọc nguyên văn**

```
0x14c6cec: ldr  s0, [x8]      ; s0 = StartHealth   (@0x0)
0x14c6cf0: str  s0, [x8, #4]  ; CurrentHealth = s0 (@0x4)
```

⇒ nghĩa đen: **`CurrentHealth = StartHealth`**. Hàm này **nạp lại HP đầy** — dùng cho
**vào màn** và **hồi sinh** (reborn). Không tính lại stat, chỉ **chép**.

**c) `Player_Health.Start()` — KHÔNG đụng tới HP**

Đọc toàn bộ thân (`0x14c6b5c–0x14c6c9c`): chỉ có
`fxHealHpBar.main` → `mainModule` (`@0x80`), rồi tạo một lambda `Action<object>`
(`<>9__14_0`) và đăng ký callback. **Không** gọi `GetStartHp`, **không** ghi `StartHealth`.

⇒ HP **không** được tính trong `Start()`. Nó đã có sẵn **trước** khi `Start()` chạy.

**d) Vậy thứ gì chốt số — 5 bước, theo đúng thứ tự phụ thuộc**

| # | Bước | Bằng chứng | Mức |
|---|---|---|---|
| 1 | Nạp save: `Player_Saved_Datas { MaxLevelPerRanks[], CardUpgrades[], StartRanks[] }`, `IsPlayerUnlocked(i)` | `dump.cs` 10859 | A |
| 2 | Nạp **device theo tàu**: `Player_Device_Saved_Datas.GetPlayerDevices(int playerIndex)` / `SetPlayerDevices(int, int[])` | `dump.cs` 10844 | A |
| 3 | Tech + ability: `GetTechStatPoints(i)` · `GP_Datas.GetNumberAbility(n)` | asm `Player_Get_Datas` | A |
| 4 | `StartHp` × `(1 + tech% + abi7%)` → `StartHealth` | `GetStartHp` `0x14e3180 fmul` | A (công thức) / **D** (giá trị) |
| 5 | `ResetStaticVariables()` → `CurrentHealth` | `0x14c6cf0` | A |

**e) ⚠ Ghi chú kỹ thuật quan trọng — file asm bị đặt tên sai**

`Player_Datas.asm.txt` chỉ có 1 header `;;; ctor`, nhưng thân file chứa **liên tiếp theo địa chỉ**:
`Player_Datas..ctor` (`0x14c6b4c`) → **`Player_Health.Start`** (`0x14c6b5c`) →
**`ResetStaticVariables`** (`0x14c6ca0`) → `GainHealth` 3 tham số (`0x14c6cfc`) →
`GainHealthOverTime` (`0x14c6d70`) → **`TakeDamage`** (`0x14c6de4`).

⇒ **`Player_Health` không hề thiếu asm** như tôi ghi trước đây — nó nằm **lẫn** trong file của
`Player_Datas`. **Đính chính 25/10:** câu *"Muốn đọc `OnChangeDataDevice` (`0x14C58EC`) thì vẫn phải
dump thêm"* là **sai** — method đó **đã có** ngay dòng 1 của
`reverse-engineering/raw/il2cpp-consts/Player_Health.asm.txt` (`0x14c58ec: stp d9, d8, …`). Địa chỉ
thấp hơn điểm bắt đầu file kia **không** có nghĩa là method bị thiếu trên toàn repo.

**f) `TakeDamage` — thứ tự kiểm tra đọc được từ asm**

```
if (CurrentHealth <= 0)            return   // fcmp s0, #0.0 ; b.ls
if (invisible)                     return   // ldrb [x19,#0x49]
if (damager == null)               return   // cbz x21
if (IsVictory)                     return   // ldrb [x19,#0x4a]
if (Invincible && !ignoreInvincible) {
    if (GP_Datas.GetNumberAbility(30) >= 1)   // mov w0, #0x1e → 30
        Random.Range(0, 100)                  // fmov s1, #100.0 (0x42C80000)
}
```

⇒ **ability 30** là một **proc xác suất** khi `Invincible`. Giáp (`Armor @0x20`) và
`reduceDamageByDevice (@0x58)` bị trừ **sau** các cổng trên.

**g) Kết luận về câu "tính khi vào màn" — mức B, kèm điều kiện**

| Phát biểu | Đúng? | Ghi chú |
|---|---|---|
| "Số của player được **chốt** khi vào màn" | ✅ **đúng** | `StartHealth` là `static`, gán **trước** `Start()`; `Start()` không tính lại |
| "Được **tính** khi vào màn" | ⚠ **đúng một nửa** | 61/61 hàm stat của `Player_Get_Datas` là **getter, không cache** ⇒ giá trị **tính lại mỗi lần gọi**. Cái "chốt" là **`StartHealth`**, không phải cả bộ stat |
| "Hồi sinh tính lại" | ❌ **không** | `ResetStaticVariables()` chỉ **chép** `StartHealth → CurrentHealth`; reborn **không** tính lại stat |
| "Device tính lúc vào màn" | ✅ **đúng** | `GetPlayerDevices(playerIndex)` + `OnChangeDataDevice(idPlayer)` |

> **Nhận định (mức B):** mô hình đúng là **"chốt một lần, dùng cho cả màn, hồi sinh thì chép lại"**.
> **Điều kiện lật ngược:** nếu tồn tại một hàm gọi lại `GetStartHp()` + ghi `StartHealth` **sau**
> `ResetStaticVariables` (ví dụ mỗi lần reborn), thì stat **có** tính lại. Cần
> `Player_Health.asm.txt` để xác nhận — hoặc chỉ cần tìm **1 lệnh `str` vào `StartHealth`**.

**h) Hệ quả cho bản clone:** thứ tự resolve **bắt buộc** là
`save → device(tàu) → tech → ability → StartHealth → CurrentHealth`, và **chốt tại thời điểm spawn**,
không đọc lại giữa màn.

### 0.6.9 **HP đến từ UPGRADE → BASIC → "Health"**, không phải từ tàu

Đây là mắt ghép còn thiếu của §0.6.1. Nguồn: `12-localization.csv` (bảng chữ), `Tech_Datas.asm.txt`,
`Player_Get_Datas.asm.txt`.

**a) Bảng tên tech stat (A)** — 24 khoá `txt_techstat_label_*` / `txt_techstat_desc_*`, id **0–11**:

| id | Tên trong game | Mô tả |
|---|---|---|
| **0** | **Health** | **"Increase health points"** |
| 1 | Special cannon | tăng power pháo đặc biệt |
| 2 | Normal cannon | tăng power pháo thường |
| 3 | Magnet | tăng bán kính hút |
| 4 | Laser weapon | tăng power skill chính |
| 5 | Bomb | đặt mìn |
| 6 | Rocket Barrage | bắn loạt rocket |
| 7 | Stun | từ trường vô hiệu đạn |
| 8 | Invisible | tàng hình vùng |
| 9 | Super Lazer | laser xoá đạn |
| 10 | Mega Bomb | nổ diện rộng |
| 11 | Invisible II | tàng hình cấp 2 |

Tab này có nhãn UI **`txt_basic` = "Basic / Cơ bản"** và nhiệm vụ **`txt_upgrade_full_tech_lv` =
"Upgrade basic technology to maximum of level"** ⇒ **đúng "upgrade → basics"**.

**b) Nối vào công thức HP đã đọc:**

```
GetHpStatPercent = stepCommon(0,18) × TechStatPoints(0) + abi7AddPlayerStartHp × GetNumberAbility(7)
GetStartHp       = StartHp × (1 + GetHpStatPercent)
```

`TechStatPoints(0)` = **số điểm của stat id 0** — và id 0 **chính là Health**.
⇒ **HP người chơi là một đường nâng cấp**, không phải thuộc tính của tàu.

**c) Ba hệ quả — và một giả thuyết bị loại:**

| Trước đây | Bây giờ |
|---|---|
| "HP phải là của tàu" | ❌ **Bị bác (mức A)** — xem (c1) dưới |
| "`StartHp` là hằng số bí ẩn" | ✅ **đã có: 2500**; phần lớn HP đến từ `TechStatPoints(0)` |
| "device cộng HP" | ❌ **sai** — device chỉ **giáp + hồi máu** (§0.6.7d) |

**c1) Bằng chứng "HP **không** theo tàu" — nay đủ mạnh để gọi là A:**

Sau khi công cụ export được sửa (bản `6109008c`), `Player_Get_Datas.asm.txt` **hết bị cắt**:

| Kiểm | Kết quả |
|---|---|
| Toàn bộ file, mọi lệnh ghi vào **static `#0x6c`** | **đúng 1 chỗ**: `.cctor` `0x14e5e70` — `str d0, [x8, #0x68]` (ghi **cặp** `{0,18, 2500}`) |
| 17 class asm còn lại | **0 lệnh** ghi vào static `#0x6c` của `Player_Get_Datas` |
| `Player_Attack` ghi `#0x68/#0x6c/#0x70` | là **field instance của chính nó**, không phải static của `Player_Get_Datas` |

⇒ `StartHp` **gán đúng một lần**, giá trị **2500**, **không bao giờ gán lại** — kể cả khi chọn tàu.

**c2) Vậy "HP theo tàu" của bạn đúng ở đâu?** Đúng ở **giáp và hồi máu**, không ở HP tối đa:

```
HP tối đa  = 2500 × (1 + 0,18 × tech stat 0 + abi7 × ability 7)     ← dùng chung MỌI tàu
HP hiệu dụng = HP tối đa × 1/(1 − reduceDamageByDevice) × (1/giáp)   ← khác nhau THEO TÀU (4 slot device)
```

⇒ Hai tàu khác nhau **vẫn chịu damage khác nhau** (giáp), **hồi máu khác nhau**, nhưng **thanh máu
tối đa giống nhau**. Đây là điểm tinh tế dễ clone sai nhất trong toàn bộ hệ thống.

**c3) Điều kiện lật ngược (ghi để không tự lừa):** nếu tồn tại một class **không nằm trong 17 file
asm** ghi vào static `#0x6c` của `Player_Get_Datas` thì kết luận trên sai. Phạm vi đã kiểm:
**17 class** = toàn bộ chuỗi player + balance (`Player_Health` · `Player_Ingame` · `Player_Attack` ·
`Player_Ability` · `Player_Talent` · `Player_Get_Datas` · `Tech_Datas` · `Device_Get_Data` ·
`GameDatas` · `Map_Get_Datas` · `Stage_Get_Datas` · `Droid_Data_Balance` · `Enemy_Data_Balance` ·
`RankManager` · `ArenaManager` · `IAP_Manager` · `Player_Datas`).

**d) Hai trục tăng HP của người chơi — tách bạch:**

```
HP = StartHp × (1 + 0,168 × [cấp tech stat 0] + abi7 × [số ability 7])   ← tài khoản, dùng chung mọi tàu
     + điều chỉnh bởi device của TÀU đang chọn (4 slot)                   ← riêng từng tàu
```

⇒ "HP theo tàu" **chỉ đúng ở phần device**. Phần tech là **toàn tài khoản**.
Điều này khớp chính xác với việc **33/40 getter của `Player_Get_Datas` không nhận `playerIndex`**.

### 0.6.10 **Hai loại tàu**: main ship + support ship

Nguồn: `dump.cs.gz` (`Player_Ingame` 72916 · `Sub_Player` 73942 · `GP_ChangePlayerTypes` 74230).

| | **Main ship** | **Support ship** |
|---|---|---|
| Class | `Player_Ingame : MonoBehaviour` | **`Sub_Player : Sub_Character, IPlayer, IPlayerAnimation, IPlayerTypes, IPlayerStartup, IPlayerSkill, IInvisible`** |
| HP | dùng `Player_Health` (static `StartHealth`) | **`private Player_Health heathScript; // 0x28`** — **HP riêng** |
| Điều khiển | `Player_Controller controller` | `Player_Controller controller; // 0x30` |
| Biến hình | `IsTransforming` (@0x29) · `currentPlayer` (`Player_Attack` @0x40) | `ChangePlayerTypes(Action _transformed)` (slot 25) |
| Skill drone | `timeDroneAbilityReady[]` (@0x48) | `UseDroneSkill(int _indexSlot)` · `UsePlayerSkill()` |

Bộ điều phối: **`GP_ChangePlayerTypes.Init(Transform _player)`** → `OnChangePlayerTypes(Action _transformed)`
⇒ đổi **loại** tàu tại chỗ, không spawn mới.

**Khớp với số đo được:** `Device_Get_Data.GetPlayerUse` quét **4 slot/tàu** (`i = 0…3`, `cmp x8, #4`).
⇒ **4 = 2 (main) + 2 (support)**, đúng như mô tả. `Player_Saved_Datas.GetPlayerUsed(int slotIndex)`
(asm `dump.cs` 10902) là hàm tra "slot nào đang dùng tàu nào".

> **Nhận định (mức B):** mô hình là **1 main + 1 support, mỗi tàu 2 device** ⇒ tổng 4.
> **Điều kiện lật ngược:** nếu `GetPlayerUsed` chỉ nhận `slotIndex ∈ {0,1}` thì 4 device đều thuộc main.
> Cần đọc thân `GetPlayerUsed` (RVA `0x14…`, **chưa có asm**).

### 0.6.11 **Giáp = giảm damage**, không cộng HP

`Player_Health`:

```csharp
public float Armor;                        // 0x20
private float reduceDamageByDevice;        // 0x58
```

Hai field **tách khỏi** `StartHealth` / `CurrentHealth` ⇒ giáp **không** nằm trong thanh máu.

⚠ **Giới hạn bằng chứng:** phần **số học** của `TakeDamage` (trừ giáp) nằm ở `0x14c7024` trở đi —
**ngoài vùng export**, vì `Player_Datas.asm.txt` dừng tại `0x14c6f48` (`DATA_SYNC` §7.29).
Đọc được **5 cổng chặn** + `GetNumberAbility(30)` + `Random(0,100)`, **chưa** đọc được
`damage × (1 − armor)`.

⇒ **Mức B** (tên field + mô tả người thiết kế), không phải A.

### 0.6.12 **Độ khó tăng theo màn — tăng cái gì, KHÔNG tăng cái gì**

Kiểm bằng 4 nguồn độc lập.

| Ứng viên | Có scale theo màn? | Bằng chứng |
|---|---|---|
| `Wave` (prefab wave) | ❌ **không** | class chỉ có **3 field**: `indexWave` · `startPoint` · `endPoint` |
| `Enemy_Datas.StartHealthPoint` | ❌ **không** (cố định theo prefab) | 981 dòng, **72 giá trị khác nhau**, không có cột level |
| `Enemy_Datas.StartHpPoint` | ❌ **field chết** | = **0 ở 981/981** |
| `Enemy_Datas.CurrentHealthPoint` | ❌ **field chết** | = **0 ở 981/981** |
| `Stage_Get_Datas.levelDelta` (float[]) | ✅ nhưng **scale PHẦN THƯỞNG** | dùng trong `GetBonus` (`fmul s0,s8,s0`) |
| **HP boss** | ✅ **tăng theo wave** | xem bảng dưới |
| **Damage boss** | ⚠ chỉ **3/9** boss có biến thể | `Boss6` 2.800/600 · `Boss9` 800/500 · `Boss10` 800→1.350 (§3 B6 của `OPEN_ISSUES`) |

**Tổng HP mỗi wave theo bó 20** — **đo lại trên `68ce86a7`** (bản `6109008c` có bộ số khác, xem
`DATA_SYNC` §7c và `VERIFY_ROUND1` §4.2):

**Định nghĩa (bắt buộc ghi kèm):** thứ tự wave trong `waves.json` (1…282) · HP mỗi prefab = **tổng mọi
dòng `15-enemy-hp.csv`** có `gameobject` = prefab hoặc bắt đầu `prefab/` ("cộng dồn mọi bộ phận") ·
nhân `copies` · median chỉ trên wave có HP > 0.

| Wave | Wave có HP > 0 | Median tổng HP | Max |
|---|---|---|---|
| 0–239 | 4/240 | 0 | 5.000.000 |
| 220–239 | 3/20 | 4.160.000 | 5.000.000 |
| 240–259 | **20/20** | **8.600.000** | **13.520.000** |
| 260–279 | 19/20 | **15.400.000** | 29.370.000 |
| 280–282 | 2/2 | **18.300.000** | 20.200.000 |
| **Tổng cả game** | — | — | **480.892.000** |

⇒ **Đường cong độ khó nằm ở HP boss**, tăng **≈ 1,79× mỗi 20 wave** ở đoạn cuối.

> ⚠ **Hạ nhãn A → B.** Con số này **phụ thuộc lần export**: cùng nguồn nhưng `6109008c` cho
> **496.410.000** và **1,89×**; `68ce86a7` cho **480.892.000** và **1,79×** (70/249 root đổi giá trị,
> `Board_FightBoss` 19 → 10 instance). Chỉ bin **240–259 khớp tuyệt đối** giữa hai bản.
> **Điều kiện lật ngược:** nếu export sau trả lại các instance đã mất thì tổng tăng về ≈496 M.

**Và một phát hiện quan trọng: enemy thường có HP = 0.**

| Nhóm | Số prefab | Có HP > 0 |
|---|---|---|
| **`Boss-*`** | **45** | **45 (100%)** |
| `CB-*` (enemy thường) | 37 | **1** (chỉ `CB(TEST)` = 10.000.000) |
| `Wave-*` · `W*` · `BB` · `XB` · `GD` · `CD-*` | 83 | **0** |

`CB-30003` = **0,0** · `CB-30015` = **0,0** · `CD-31002` = **0,0** — ba loại bị spawn nhiều nhất.

**✅ ĐÃ CHỐT (23/10) — enemy thường KHÔNG chết 1 phát.** Chi tiết `ENEMY_HP_RUNTIME.md`.

| Bằng chứng (A) | Số |
|---|---|
| `Enemy_Hp_Bar`, `m_Enabled = 1` | **909 / 909** |
| Prefab **được spawn** có HP bar | **108 / 109** (99,8 % quân) |
| `CB-30003` (4.793 quân) | **có** HP bar, đang bật |

❌ **Rút lại câu "HP bar chỉ gắn trên boss"** — đó là **bằng chứng tôi chưa kiểm** cho giả thuyết
"one-hit".

**HP enemy lấy từ đâu (A, `dump.cs`):** `Enemy_Get_Datas.GetStartHealthPoint(int)` tra
**`static Dictionary<int,float> AllStartHealthPointEnemies`** dựng trong **`.cctor` `0x157F7CC`**.
`Enemy_Health.CalculateDamage(float, ref float _hp, bool)` nhận HP qua **`ref`** và có
**`armor` @`0x34`** ⇒ **enemy cũng có giáp**. ⇒ HP **không** nằm trong dữ liệu serialize; đó là lý do
`StartHealthPoint` = 0 ở enemy thường.

**Hệ quả cho cân bằng:** cột "HP = 0" có nghĩa **"HP do runtime cấp"** — ~~và TTK từ `enemy_hp.json`
chỉ đúng cho boss~~ **SUPERSEDED 25/10**: HP **150 cặp theo id** (`datas/enemy_hp_by_id.json`, WRH2)
cho cả enemy thường; mất máu theo công thức report 81 §E. ~~**Cách chốt:** dump asm~~ — **đã chốt**,
không cần dump.

### 0.6.13 Hằng số gốc **đã có** — `StartHp = 2500`

Bản `6109008c`. Toàn bộ mục §0.6.3 ("thiếu đúng một giá trị") **nay đã đóng**.

**Cách đọc ra (A):** `.cctor` của `Player_Get_Datas` nạp **một cặp float 8 byte** bằng `ldr d0`:

```
0x14e5e58: ldr  d0, [x9, #0xbc0]    ; pool 0x757bc0–0x757bc7 = {0.18, 2500.0}
0x14e5e6c: str  x0, [x8, #0x60]     ; PlayerStarCosts (int[]) nạp cùng lúc
0x14e5e70: str  d0, [x8, #0x68]     ; ghi 8 byte → 0x68 VÀ 0x6C cùng lúc
0x14e5e74: str  w9, [x8, #0x70]     ; w9 = 0x3C23D70A = 0.01
```

Theo `dump.cs`, ba field static liền nhau:

| Offset | Field | Giá trị |
|---|---|---|
| `0x68` | `stepCommon` | **0,18** |
| `0x6C` | **`StartHp`** | **2500,0** |
| `0x70` | `BaseHpRecoverSpeed` | **0,01** |

⚠ **Đây là chỗ tôi từng ghi sai:** nhiều vòng trước tôi ghi `stepCommon = 0,168`. **0,168 không phải
`stepCommon`** — nó là hằng của **`stepLevel`/`GetMainCannonDamage`** (đường cong **damage theo cấp tàu**).
Hai đường cong khác nhau:

| Hằng | Dùng cho | Ngưỡng | Hệ số |
|---|---|---|---|
| **0,168** | **damage / cấp tàu** (`GetMainCannonDamage`, `stepLevel`) | 30 · 58 · 118 · 248 | 1,0 · 1,05 · 1,15 · (0,1764 · 0,1932) |
| **0,18** | **HP / điểm tech stat 0** (`GetHpStatPercent`) | — | tuyến tính |

**Công thức HP hoàn chỉnh (A):**

```
HP tối đa = 2500 × (1 + 0,18 × TechStatPoints(0) + abi7 × GetNumberAbility(7))
```

| `TechStatPoints(0)` | HP | |
|---|---|---|
| 0 | **2.500** | trạng thái gốc |
| 5 | 4.750 | |
| 10 | 7.000 | |
| 20 | 11.500 | |
| 30 | 16.000 | |
| 60 | 29.500 | |

**Đối chiếu với damage trong game:** đòn boss 350–2.800 (`OPEN_ISSUES` B6) ⇒ ở HP gốc **2.500**,
người chơi chết sau **1 đòn mạnh nhất** và **≈7 đòn trung bình (350)**. Đây là game "giấy" —
khớp với việc phải có **né (dodge tới 90%)** và **khiên 1 hit**.

### 0.6.14 Công thức **damage nhận vào** — giáp, device, né

Bản `6109008c`, `Player_Health.TakeDamage` (2.420 B). Đọc từng lệnh — đây là **công thức đầy đủ**:

```
dmg = damager.damage                       // [x21, #0x10]

// 1) device giảm damage (tuyến tính, cộng dồn theo %/100)
dmg = dmg × (1 − reduceDamageByDevice)     // fmul + fsub @0x14c73d0

// 2) giáp (hyperbolic)
if (Armor >= 0)  f = 100 / (100 + Armor)
else             f = 2 − 100 / (100 − Armor)      // giáp âm ⇒ nhận thêm damage
dmg = dmg × f                              // fmul @0x14c7404

// 3) né (dodge) — kiểm TRƯỚC khi trừ máu
chance = abi8 × GetNumberAbility(8)
if (CurrentHealth / StartHealth < 0,3)                    // ngưỡng 0,3 @0x7570e0
    chance += abi34 × GetNumberAbility(22)                // thưởng né khi HP thấp
chance = min(chance, 90,0)                                // fmov 0x42B40000
if (chance > Random.Range(0, 100)) → né hoàn toàn
```

| Thành phần | Công thức | Ví dụ |
|---|---|---|
| `reduceDamageByDevice` | `Σ(stat%/100)` của device dải **1000–1999** | 3 device 5% ⇒ 0,15 ⇒ `×0,85` |
| `Armor` | `100/(100+Armor)` | 100 ⇒ ×0,5 · 300 ⇒ ×0,25 · 0 ⇒ ×1,0 |
| giáp **âm** | `2 − 100/(100−Armor)` | −100 ⇒ **×1,5** (nhận thêm 50%) |
| né | `min(90, abi8 × năng lực 8 [+ abi34 × năng lực 22 nếu HP<30%])` | trần **90%** |

**Ba điều đáng chép sang bản clone:**

1. **Giáp hyperbolic, không tuyến tính** — armor 100 giảm 50%, armor 300 giảm 75%, nhưng **không bao
   giờ = 0**. Đây là cách chống "stack giáp vô hạn".
2. **Giáp âm làm tăng damage** — cùng một công thức dùng cho cả buff và debuff.
3. **Né là phép nhân xác suất, không phải trừ damage** — né 90% nghĩa là **HP hiệu dụng ×10**.

**Hồi máu tự động (A):**

```
amountAutoGainHpByDevice = StartHealth × (Σ stat%/100)     // device dải 5000–5999
BaseHpRecoverSpeed       = 0,01                            // @0x70
```

⇒ hồi **1% HP mỗi "nhịp"** + phần cộng thêm của device.

**Họ kỹ năng "dưới 30% HP" (A, khớp bảng chữ):** `12-localization.csv` có
`txt_techstatability_desc_300…309` — *"If health points are below 30%, power increases by 10%…50%"* /
*"Rate of enemy K.O increases by 5%…20%"* ⇒ **cùng ngưỡng 0,3** với công thức né ở trên.
Đây là **một hệ thống duy nhất**: HP thấp ⇒ kích hoạt buff.

### 0.6.15 **HP chốt đúng lúc vào màn** — xác nhận bằng lệnh ghi

Đây là câu *"các thứ của player được tính khi vào màn chơi"* — nay trả lời dứt điểm.

**a) Chuỗi gọi thật (A):**

```
Player_Health.Start()                    // 0x14c6b5c
  └─ tạo lambda  <Start>b__14_1          // 604 B, gán vào Action
       └─ GetStartHp()                   // bl 0x14e311c
            s0 = 2500 × (1 + 0,18×TechStatPoints(0) + abi7×GetNumberAbility(7))
       └─ stp s0, s1, [x8]               // 0x14c7e48 — ghi 8 byte
            [x8+0] = s0 → StartHealth
            [x8+4] = s1 → CurrentHealth
```

**b) Hai nhánh trong lambda:**

| Nhánh | Lệnh | Kết quả |
|---|---|---|
| đầy máu | `str s8, [x8]` (`0x14c7eac`) rồi `bl 0x14c6ca0` = `ResetStaticVariables()` | `StartHealth = GetStartHp()`; `CurrentHealth = StartHealth` |
| hồi một phần | `fdiv s1, s8, s9` + `fmul s1, s1, s0` | `CurrentHealth = StartHealth × (s8/s9)` — **một cặp float static** (nghi là tỉ lệ "chơi tiếp"), mức **B** |

⇒ **Mức A:** `StartHealth` được **ghi trong `Start()`** — tức **lúc object người chơi được tạo trong màn**,
không phải lúc mở app, không phải lúc chọn tàu.

**c) ⚠ Đính chính:** tôi từng kết luận *"`Start()` không đụng tới HP"* dựa trên `Player_Datas.asm.txt`.
**Sai** — file đó chỉ chứa phần **đầu** của `Start()` (dựng `mainModule`, tạo lambda); phần **thân
lambda** nằm ở `Player_Health.asm.txt`, chỉ có sau khi công cụ export được sửa (bản `6109008c`).
Bài học: **"không thấy trong file X" ≠ "không xảy ra"** — phải kiểm cả **file khác** và **cả phần
bị cắt** (`DATA_SYNC` §7.29).

**d) Trả lời gọn — 4 mệnh đề, đúng/sai rõ ràng:**

| Mệnh đề | Kết luận | Mức |
|---|---|---|
| "Số của player **chốt khi vào màn**" | ✅ **đúng** — `StartHealth` ghi trong `Start()` | A |
| "**Hồi sinh** tính lại stat" | ❌ **không** — `ResetStaticVariables()` chỉ **chép** | A |
| "Mỗi lần gọi stat đều **tính lại**" | ✅ đúng — 61/61 getter không cache | A |
| "HP **theo tàu**" | ⚠ chỉ đúng **gián tiếp** — qua device (giáp/hồi), không qua `StartHp` | A |

## 1. Phương pháp & nguồn

| Field | Kiểu | Nghĩa |
|---|---|---|
| `StartHp` | **`float`** (một giá trị) | HP **dùng chung cho mọi tàu** |
| `StartMainCannonDamages` | **`float[]`** | damage **riêng từng tàu** |
| `StartWingCannonDamages` | **`float[]`** | damage pháo cánh **riêng từng tàu** |
| `StartMainCannonRate` | **`float[]`** | **khoảng giữa 2 phát** (interval) — tàu 1 chứng minh (report 79); 23 tàu chưa xét |
| `StartSecretWeaponDamage` | `float` | dùng chung |

⇒ **Tàu khác nhau ở damage và nhịp bắn, không ở HP.** `Data_Players` (25 tàu) chỉ có
`id · Sprite · Star · Actived` — **không có field HP nào**.

**Bảng đóng góp vào HP và vào damage — 5 nguồn, chỉ 2 nguồn cộng HP:**

| Nguồn | Cộng HP? | Bằng chứng |
|---|---|---|
| **Tàu** (25 chiếc) | ❌ **không** | `StartHp` là `float`, `StartMainCannonDamages` là `float[]` |
| **Tech lab** (stat index 0) | ✅ `stepCommon × TechStatPoints(0)` | asm `0x14e3258` `fmul` |
| **Ability 7** | ✅ `abi7AddPlayerStartHp × GetNumberAbility(7)` | asm `0x14e325c` `fmul` |
| **Trang bị (device)** | ❌ **không cộng HP** | `Device { id, lv, rank, instanceId }`; `Player_Health` dùng nó qua `reduceDamageByDevice` và `amountAutoGainHpByDevice` — **giảm damage** và **hồi HP**, không tăng HP tối đa |
| **Drone** | ❌ không | `Droid_Data_Balance.GetBaseDamage` — drone đóng góp **damage** |

> **Nhận định (mức A):** chuỗi HP chỉ có **3 số**: `StartHp` (gốc) · điểm tech stat **0** ·
> ability **7**. Không có chỗ nào khác cộng vào HP tối đa.
>
> **Điều kiện lật ngược:** nếu `GetStartHp()` được gọi **nhiều lần trong màn** (không chỉ lúc boot),
> và `TechStatPoints(0)` bị thay đổi giữa trận thì HP sẽ đổi giữa trận. Đã kiểm: `Player_Health.Start()`
> chỉ gán **một lần**, `StartHealth` là `static` dùng chung mọi instance.

**Boot lúc nào:** `Player_Health.Start()` (`RVA 0x14C6B5C`) → `StartHealth = GetStartHp()`,
`CurrentHealth = StartHealth`. Đây là **lúc vào màn**, sau khi người chơi đã chọn tàu — nhưng vì
`StartHp` **không phụ thuộc tàu**, kết quả **giống nhau với mọi tàu**.

**Hai ứng viên cho `playerLv` trong `stepLevel` (4 ngưỡng 30/58/118/248):**

| Ứng viên | Nơi khai báo |
|---|---|
| `Player_Ingame.lv` (**`private static int`**, `@0x4`) + property `Level` | cấp trong màn |
| `Player_Saved_Datas.MaxLevelPerRanks` (**`int[]`**) + `MAX_RANK_INDEX` | cấp theo **rank tài khoản** |

> **Nhận định (mức C):** 30/58/118/248 quá cao cho một màn ⇒ nhiều khả năng là **cấp tài khoản/rank**.
> **Điều kiện lật ngược:** nếu `Player_Ingame.Level` tăng được tới 248 trong một màn (power-up dồn)
> thì đó mới là biến đúng.

## 1. Phương pháp & nguồn

| Bảng | File | Trạng thái |
|---|---|---|
| HP enemy/boss | `15-enemy-hp.csv` (**981** dòng, **467** > 0) + **150 cặp id** (`datas/enemy_hp_by_id.json`, WRH2) | ✅ có số |
| Cờ enemy | `docs/apk-analysis/Enemy_Datas.csv` | ✅ có số |
| Roster tàu/drone/boss/item | `14-ships.csv`, `14-drones.csv`, `14-bosses.csv`, `14-items.csv` | ✅ có số |
| Tên tàu/drone/boss/talent/ability | `12-localization.csv` | ✅ có text |
| Tech ability / shop pack / GP / rank | `Tech_Ability_Data.csv`, `DataShopPack.csv`, `GP_Datas.csv`, `RankManager.csv` | ⚠ chỉ có sprite/id, không có số balance |
| **Damage vũ khí địch** | `reverse-engineering/scriptableobjects/Gun_Attack.csv` (458 dòng) | ✅ có số → `COMBAT.md` |
| **Burst pattern** | `Gun_Attack.csv` `allGunDatas[0..2].{countShots,timeShot,timeReload,timeRounds,countMags}` | ✅ có số → `COMBAT.md` §3 |
| Đạn (hitbox, xuyên khiên) | `Bullet_Linearly.csv` (186 dòng) | ✅ có số → `COMBAT.md` §7 |
| Damage va chạm boss | `Boss_BodyPhysics.csv` (`dmgFirst`, `dmgPerSec`) | ✅ có số → `COMBAT.md` §6.3 |
| Armor / `noDamage` | `Enemy_Health.csv` (**981** dòng) | ✅ **241 / 981** `True` (report 81) |
| **Wave / spawner / map** | `datas/waves.json`, `MapController.csv`, `Stage_Behaviour.csv` | ✅ có số → `ENCOUNTERS.md` |
| **Giá & phần thưởng cụ thể** | `Box_Rewards.csv`, `Shop_Cell.csv`, `DataShopPack.csv`, `13-iap-products.csv` | ❌ **thật sự không có số** → `ECONOMY.md` §0 |
| **Tỉ lệ rơi item** | `Sub_Item.csv` + `Item_Movement.csv` (702 lượt) | ✅ 676 coin / 26 item → `ECONOMY.md` §1.1 |
| Damage của **player** | `Player_Get_Datas.StartMainCannonDamages[]` | ✅ **đã decode** từ `ia-resolved.json` → §1.1b + `datas/player_start_stats.json` |

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
- ⚠ **1/39 prefab có tổng HP = 0**: `39003` → "vỏ", HP set lúc chạy. **Không dùng để cân bằng.**
  ✅ **ĐÍNH CHÍNH 23/10:** bản `6109008c` ghi **5** (`37009`, `37012`, `39003`, `39007`, `39008`);
  bản `68ce86a7` bốn cái kia **đã có HP** (4,2 M · 2,8 M · 3,564 M · 8,82 M) — chỉ còn `39003` = 0,
  khớp `BOSSES.md` ("1/39"). File sai là **file này**, không phải `BOSSES`.
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
theo chapter/stage nằm trong **mã**, không nằm ở asset — **nhưng** đừng gộp hai class làm một:

| class | trạng thái |
|---|---|
| `Stage_Get_Datas` | ✅ **đã decode** 2/2 mảng: `startBonusValues` int[5] · `levelDelta` float[4] = **1 / 2 / 3,6 / 3,6** — nhưng `levelDelta` là hệ số **thưởng**, **không** phải HP (§6.4) |
| `Enemy_Data_Balance` | ❌ **chưa có nhóm nào** trong `ia-resolved.json` (chỉ `Droid_Data_Balance` là droid item, khác class) |
| `Enemy_Get_Datas` | ✅ `.cctor` **hoàn chỉnh 3.624 B**, **150** lệnh insert `Dictionary` (**150** id khác nhau, **30001–38001**, **0** vòng lặp). **Đã parse thành `datas/enemy_hp_by_id.json` = 150 cặp `id → HP`** (claim **WRH2**) ⇒ **không cần `.so`**. `15-enemy-hp.csv` là field serialize (981 dòng · **467** > 0; `CB-*` 0/69, claim **WRH1**); gộp hai nguồn **108/109** prefab spawn có HP (claim **WRH5**) |

```
Điểm arena/PvP = f(idEnemy, timeLife)   // GetArenaScore, GetPVPPlayScore, GetArenaPlayScore
Điểm survival  = GetSurvivalScore(idEnemy)
Thưởng         = GetBonusCoin(id) / GetBonusExp(id)
```
Chỉ biết **signature**, không biết thân hàm (nguồn: `class Enemy_Data_Balance` trong `dump.cs`).

### 5.2 Không suy ra được (mức D)

| Nhóm | Lý do |
|---|---|
| ~~Damage nền từng tàu~~ | **ĐÃ CÓ** (§1.1b) + bind combat **theo report 81/82** (impl N → index N−1; tàu 10001→2 · 10003→0); DPS runtime còn là **proxy** — đừng xếp vào mức D nữa |
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
| Armor / `noDamage` | `noDamage` **241/981** true (report 81 peer đếm lại); `armor` **không serialize** — công thức mất máu đã có (report 81 §E: `100/(100+armor)`), giá trị runtime chưa | `Enemy_Health.csv` + report 81 |
| Số wave + spawner | ✅ 282 / **48 archetype** / **11.089** dòng = **10.782** cấu hình | `waves.json` → `ENCOUNTERS.md` |
| Số map + parallax | ✅ 250 map, 5 lớp | `MapController.csv` |
| Số stage theo loại | ✅ 299 (Normal 199 · Boss 26 · Combat 49 · MiniBoss 25) | `Stage_Behaviour.csv` |
| Tỉ lệ rơi tương đối | ✅ 676 coin / 26 item | `Item_Movement.csv` → `ECONOMY.md` §1 |
| Số mốc ability tech | ✅ 6 bảng × 5 mốc | `Tech_Ability_Data.csv` |

**Trạng thái đúng (sửa 25/10)** — chia làm **ba** loại, đừng gộp:

| loại | gồm những gì | ở đâu |
|---|---|---|
| ✅ **Đã có giá trị** | damage/rate/wing/**giá tàu** (Player 6/6 mảng) · thưởng theo stage (`startBonusValues` int[5], `levelDelta` float[4]) · stat **droid/device/tech** (3 + 12 + 7 mảng) · `GameDatas` float[6] · **576** mảng wave→wave-id (Map) | §1.1b · §6.4 · §6.10 · `ia-resolved.json` (**17 method / 623 record**) |
| 🟡 **Có raw, thiếu bind** | tên field ↔ mảng (Droid/Tech/Device/`Board_*`) · `playerIndex` → ID tàu · mảng Map → (chapter, stage, mode) | §6.10 · `DATA_SYNC.md` §23 |
| ✅ **Đã có (không cần xin)** | **HP enemy**: `datas/enemy_hp_by_id.json` = **150 cặp `id → HP`** parse từ `.cctor` (claim **WRH2**); `15-enemy-hp.csv` = 981 dòng **serialize**, **467** dòng > 0 (claim **WRH1**); 3 class enemy đã có asm (claim **WRH3**). Gộp lại **108/109** prefab spawn có số HP (claim **WRH5**) ⇒ **không cần `.so`** | `ENEMY_HP_RUNTIME.md` §0 · `WHERE_TO_LOOK.md` §3 |
| ❌ **Thật sự chưa có** | coin/gem **delta** vô hướng · thưởng trong hộp · **trọng số rơi** · ngưỡng VIP (mapping wave→stage **đã phân loại 11 cấu trúc**, `DIFFICULTY_MODES` §7 — không còn ở đây) | `MISSING` §3 |

> ⚠ Câu cũ *“cái thiếu là **giá trị** trong `.cctor()`”* đã **sai từ 25/10**: giá trị đã nằm trong
> repo. Cái thiếu là **bind** — và đúng là trước đó bộ spec đã **xin dump lại** thứ mình đang có.

### 6.0b Vì sao các class dưới đây **không được serialize** vào `data.unity3d`

8 class sau là `MonoBehaviour` **không được serialize** — giá trị nằm trong **thân hàm IL2CPP**.
`data.unity3d` chỉ chứa *instance của object có field `[SerializeField]`*; các class này hoặc
không có instance trong scene, hoặc field là `static`/`property` (không serialize).

**Nhưng chúng không nằm ngoài tầm với:** cả 8 class đều có `.cctor()` với **259 field tĩnh**
(trong tổng **957** static của toàn bộ class game),
và `dump.cs` đã có **RVA của từng `.cctor`** (ví dụ `Droid_Data_Balance..cctor` @ `0x1451…`).
Nạp `libil2cpp.so` vào Ghidra headless + `script.json` là **có đường đọc** literal của các field đó —
và **đã đọc được**: `ia-resolved.json` hiện có **17 method / 623 record** (Player **6/6**, Map **576**,
Device **12**, Tech **7**, Droid **3**, Stage **2**, GameDatas **1**, `Board_*` **5**).
Việc còn lại là **bind tên field** cho các nhóm chưa bind (`Board_*`, Droid, Tech, Device) — §6.10.
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

> **Đã đọc (25/10) — 6/6 mảng, không cần tìm thêm:** hex nằm trong
> `reverse-engineering/il2cpp/ia-resolved.json`; decode ra `PlayerCosts` **int[24]** +
> 3 mảng **float[24]** (damage · rate · wing) + 2 mảng **float[3]** (clone · mission %).
> Số thật ở §1.1b; bind store offset kiểm bằng asm: claim **IA2** (`0x38 / 0x78 / 0x80 / 0x88 / 0x1C8 / 0x308`).
> **Còn thiếu:** bind `playerIndex` → **ID tàu** (thứ tự index *không* phải thứ tự tàu 1…25) và
> các field **vô hướng** (`StartHp` = 2.500 đã đọc bằng literal store; `StartMagnetRange`, … chưa).

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

**Đã decode 2/2 mảng** của `.cctor` (claim **IAB2**); bind theo **kiểu** — class chỉ có đúng
**một** `int[]` và **một** `float[]`:

| field | kiểu | giá trị | đọc ra |
|---|---|---|---|
| `startBonusValues` (`0x0`) | **int[5]** | `350 · 600 · 5 · 10 · 10` | bonus khởi đầu theo nhóm stage |
| `levelDelta` (`0x10`) | **float[4]** | **1,0 · 2,0 · 3,6 · 3,6** | hệ số **thưởng** theo chế độ (index = mode) |

> ⚠ Hai số `3,6` là **float32 `0x40666666`**. Đọc bằng mắt theo hex dễ ra “2,1”/“3,6” lẫn nhau —
> luôn `struct.unpack('<f')`. Và `levelDelta` **scale phần thưởng**, **không** scale HP
> (`GetBonus`: `fmul s0, s8, s0`) — HP theo chế độ vẫn là **B8, chưa biết**.

`coinDelta` / `gemDelta` là **vô hướng** (`0x8`/`0xC`) — không có blob, nằm ở **literal store** trong
`.cctor`; chưa đọc.

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

### 6.10 **Bảng giá trị đã decode cho 7 class còn lại** (`ia-resolved.json`, 25/10)

Toàn bộ hex của các `.cctor` **đã nằm trong repo**; decode theo kiểu field (float vs int) là ra số.
**Chưa bind tên field** cho Droid/Tech/Device/`Board_*` — nên đọc ở **mức B**, đừng gán nhãn tuỳ ý.

| class | số mảng | nội dung (float, nếu là số nguyên thì ghi int) | đọc ra |
|---|---:|---|---|
| `Droid_Data_Balance` | 3 | `500 · 120 · 816 · 400 · 400` · **10,0** × 6 · int[3] `50 · 125 · 250` | damage/thời gian/giá mở 3 droid item |
| `Tech_Datas` | 7 | `1,9 · 1,8 · 1,68` · int[7] `500…1800` · float[24] `0,108 0,108 0,106 0,098 …` · float[13] `0,3 0,28 0,26 … 0,15` · int[10] `200…1800` · float[12] `0,1135 0,135 0,18 0,65 …` · int[10] `1500…13000` | **24 + 13** phần tử ≈ đúng số stat tech/ability đang thiếu |
| `Device_Get_Data` | 12 `InitializeArray` captures | `.cctor` groups **10** arrays into `listStatValues`; the last 2 go to `percentByLevels1/2` (offsets `0x8/0x10`). Runtime `listStatValues_count=10` on the separate modded 1.0.69 phone build; nested rows remain type-name placeholders. | 10 static list rows × `float[5]`; **not** a proven count of user-facing devices or same-build value parity (Report 119, this branch) |
| `GameDatas` | 1 | float[6] = `0,5 · 0,6 · 0,7 · 0,8 · 0,9 · 1,0` | hệ số chung theo chế độ/độ khó |
| `Stage_Get_Datas` | 2 | int[5] `350 600 5 10 10` · float[4] `1 · 2 · 3,6 · 3,6` | §6.4 |
| `Player_Get_Datas` | 6 | §1.1b | damage/rate/wing/cost/clone/mission % |
| `Board_*` | 5 | `Board_Players.allBasicAtk` float[24] `4640 5120 5040 6160 8896 …` · `allDeltaAtk` = **0,168** × 24 · `Board_Drones` float[12] `500 600 800 1250 …` · `Board_Endgame` int[10] `900…810` | `GetPlayerPower` → `textPlayerPower` xác nhận UI-power consumer; combat/rank semantics chưa chứng minh ⇒ **B** (report 109) |

**Cách tái tạo** (`ia-resolved.json` → số):

```python
import json, struct
d = json.load(open("reverse-engineering/il2cpp/ia-resolved.json"))
for r in d["methods"]["Tech_Datas.cctor"]:
    b = bytes.fromhex(r["raw"])[: 4 * r["len"]]          # luôn cắt theo len
    print(r["len"], struct.unpack(f'<{r["len"]}f', b))    # hoặc '<{n}i' nếu là mảng int
```

> **Luật:** `len` là **số phần tử**; raw có thể dài hơn `4·len` (đuôi alignment) — cắt trước khi unpack.
> Cột `ints` trong file là **bit pattern**, không phải “số nguyên của thiết kế”.

---

## 7. Đề xuất balance cho bản clone (KHÔNG phải số của WindWings)

§6 **đã có số thật** cho player/tech/droid/device/stage — nhưng **chưa có** HP enemy theo bảng.
Phần dưới là **target thiết kế** cho clone, dựa trên *hình dạng* dữ liệu đã đo
(HP boss ch1 median 4,2 M, ch2 6,0 M; enemy median 500 K — §2.3).

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

> Đây là **gợi ý**. `PlayerCosts[]` **đã bóc** — dùng số thật thay cho bảng này khi làm clone:
> `[0, 0, 1050, 3150, −1, 3850, 4550, 2450, 2450, −1, 3850, −1, 3150, 4550, 4550, −1,
> 4550, 2450, −1, 4550, −1, 4550, −1, −1]` (**16** tàu bán được, **8** tàu `−1`; claim **IA5**).

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
