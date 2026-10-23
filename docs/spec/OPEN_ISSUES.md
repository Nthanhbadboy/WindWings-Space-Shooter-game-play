# Sổ vấn đề **chưa chốt** — tổng hợp

> **asm-check** (bản `6109008c`): **16/17 PASS** · `size_capped` **0/425** · ❌ `RankManager` thiếu **8 B** (`ctor` rỗng) — xem **`ASM_INTEGRITY.md`**. Mọi kết luận phủ định trong file này chỉ đúng trong **17 class đã export**.

> Mục đích: một chỗ duy nhất liệt kê **mọi thứ còn hở** sau 6 vòng phân tích, kèm **bằng chứng số**,
> **cách chốt rẻ nhất**, và **nếu không chốt được thì thiết kế phải tự quyết cái gì**.
> Không lặp lại nội dung đã xong — chỉ trỏ về file gốc.
>
> Nguồn: `docs/apk-analysis/*.csv` · `datas/*.json` · `reverse-engineering/raw/typetrees/*.jsonl.gz` ·
> `reverse-engineering/raw/il2cpp-consts/*.asm.txt` · `reverse-engineering/il2cpp/dump.cs.gz`.
> Bản dữ liệu: nhánh đối chiếu `8871068a`.

**Thang mức (giữ nguyên toàn bộ SPEC):**

| Mức | Nghĩa |
|---|---|
| **A** | Đọc trực tiếp từ dữ liệu/lệnh máy, không suy diễn |
| **B** | Suy ra từ ≥2 nguồn độc lập, có **điều kiện lật ngược** ghi kèm |
| **C** | Một nguồn, hoặc suy luận chuỗi |
| **D** | **Không có dữ liệu** — phải quyết khi thiết kế |

---

## 1. Bảng tổng — **28 vấn đề**, chia theo **nguyên nhân** (quan trọng hơn mức độ)

| # | Vấn đề | Nhóm | Mức | Ảnh hưởng thiết kế |
|---|---|---|---|---|
| A1 | ~~Giá trị `StartHp`~~ ✅ **ĐÓNG = 2500** | **lỗi export** | **A** | **mở khoá TTK** — `BALANCE` §0.6.13 |
| A2 | Bảng map→wave **nằm inline** trong `.cctor` 25.996 lệnh — **giao nhánh dữ liệu**, spec không tự trích | **uỷ thác** | **C** | chặn "màn nào gồm wave nào" |
| A3 | ~~`OnChangeDataDevice`~~ ✅ **ĐÓNG** — device **không** cộng HP tối đa, chỉ giáp + hồi | **lỗi export** | **A** | `BALANCE` §0.6.7d |
| A4 | ~~Caller của `GetStartHp()`~~ ✅ **ĐÓNG** = `<Start>b__14_1` | **lỗi export** | **A** | HP chốt **trong `Start()`** — `BALANCE` §0.6.15 |
| B1 | 3 bảng stat của device | **RVA data** | D | chặn "device mạnh bao nhiêu" |
| B2 | ~~13 tàu `20001–20013`~~ ✅ **ĐÓNG — là 13 DRONE**, không phải tàu | — | **A** | số tàu vẫn **25**; drone đã có ở `BALANCE` §3.2 |
| B3 | ~~HP enemy scale theo stage~~ ✅ **cơ chế ĐÃ RÕ**: HP = `Dictionary<int,float>` trong `Enemy_Get_Datas.cctor` (chưa dump) · **enemy có giáp** | **chưa dump 1 class** | **B** | thiếu **nội dung bảng HP** (981 giá trị) — `ENEMY_HP_RUNTIME.md` |
| B4 | `GetCountEnemies` mỗi stage | **chưa lấy** | D | ảnh hưởng nhiệm vụ/độ dài |
| B8 | **Hệ số chế độ cho SỐ QUÂN + HP** — người chơi kiểm chứng khó hơn ⇒ đông hơn & nhiều máu hơn (**A**). Bảng dữ liệu **phẳng** (981 HP/prefab, 23.757 `Call_Data` không field chế độ) ⇒ hệ số **hard-code trong `MoveNext` 840 B chưa đọc** | **chưa dump class spawn** | **B+** (vị trí) · **C** (giá trị) | clone phải **tự chọn** `kCount`/`kHp`; giao thức đo 10 phút — `DIFFICULTY_MODES.md` §5.4 |
| B5 | 43/305 trace chưa đối chiếu | **chưa lấy** | — | rủi ro sai số nhỏ |
| B6 | Damage boss không khai báo (19 class) | **chưa lấy** | C | thiếu 19/37 nhóm đòn |
| B7 | ~~12 stat Basic vs `NumberTechStats()` = 60~~ | ✅ **đã chốt** | A | = `List.Count`, không phải hằng số |
| C1 | Thời điểm (time) của animation event | **vắng mặt thật** | D | nhịp bắn 86,7% không đọc được |
| C2 | Bảng controller→clip | **vắng mặt thật** | D | không biết anim nào phát khi nào |
| C3 | `Spawner.dataScript` rỗng | **vắng mặt thật** | D | quy luật spawn phải suy từ wave |
| C4 | `Wave.indexWave` = 0 | **vắng mặt thật** | D | thứ tự wave trong màn |
| C5 | `Call_Data.number/editType` = 0 | **vắng mặt thật** | D | số quân mỗi lần gọi |
| C6 | `Enemy_Physics.allColliders = []` | **vắng mặt thật** | A | enemy thường **không** damage va chạm |
| C7 | **45 root prefab mã `900xx`** ngoài roster | **chưa lấy** | C | nội dung dự phòng |
| C8 | `Boss_BodyPhysics` 251 instance | **đã có** | B | chỉ boss có damage va chạm |
| D1 | Feel / aim assist / input latency | **cần chạy game** | D | phải tự thiết kế |
| D2 | Thứ tự resolve stat lúc runtime | **cần chạy game** | B | đã có mô hình, chưa xác nhận |
| D3 | Tỉ lệ rơi item trong màn | **cần chạy game** | D | phải tự thiết kế |
| D4 | % giảm damage thực tế của giáp/device | **cần chạy game** | D | phải tự thiết kế |
| E1 | Asm **từng** bị cắt cụt 11/12 file (`8871068a`) → `6109008c` hết cụt (`size_capped` 0/425). **`68ce86a7`: 25 method vắng hẳn khỏi asm** (24 stub 8 B + 1 method 32 B) | **lỗi công cụ** | A | **cờ 4** ở `ASM_INTEGRITY` §3; `RankManager` FAIL là **thật nhưng vô hại** |
| E2 | ~~`ships.json` thiếu 13 dòng~~ ✅ **ĐÓNG — KHÔNG phải lỗi công cụ: tôi đọc sai** `Data_Players` (class dùng chung tàu + drone) | **tôi đọc sai** | **A** | **25 tàu**, không phải 38 |
| E3 | `RankManager.asm` **thiếu 8 B** (`ctor` = `ret` rỗng) — cờ gác cổng bắt được, **vẫn còn ở `68ce86a7`** | **lỗi công cụ** | A | **không mất dữ liệu**; FAIL đúng, không phải dương tính giả |
| E4 | **`Player_Ingame.get_IsAttacking` 32 B mất hẳn** khỏi `asm.txt` — method **duy nhất không phải stub** trong 25 method vắng mặt. `set_IsAttacking` **còn** ⇒ field @ **`0x2c`** | **lỗi công cụ** | C | dùng field `@0x2c` cho `IsAttacking`; **điều kiện phụ** (nếu có) trong getter thì mất |

---

## 2. Nhóm A — **lỗi export**: chốt được bằng **một yêu cầu rất nhỏ**

### A1. Giá trị `StartHp` — ✅ **ĐÓNG = 2500** (bản `6109008c`)

- **Kết quả (A):** `str d0,[x8,#0x68]` trong `.cctor` của `Player_Get_Datas` ghi **cặp liền nhau**:
  **{`stepCommon` = 0,18 @`0x68`; `StartHp` = 2500,0 @`0x6C`}**.
- **Công thức đầy đủ:** `HPmax = 2500 × (1 + 0,18×TechStatPoints(0) + abi7×GetNumberAbility(7))`,
  gán trong **`Player_Health.Start()`** → `bl GetStartHp 0x14e311c` → `stp s0,s1,[x8]` @`0x14c7e48`
  ⇒ `StartHealth@0x0`, `CurrentHealth@0x4` (`BALANCE` §0.6.13–0.6.15).
- **`TechStatPoints(0)` = stat "Health" của tab Basic** (A) — `txt_techstat_label_0` = `Health`,
  `txt_techstat_desc_0` = "Increase health points"; tab `txt_basic`. ⇒ phần lớn HP đến từ **nâng cấp**,
  không từ tàu (`BALANCE` §0.6.9).
- **Vì sao trước đây tưởng "thiếu":** không phải game thiếu, mà **asm bị cắt** ở bản `8871068a`
  (dừng ở `0x14e5cc4`). Bản `6109008c` đã đủ — `size_capped` **0/425** (`ASM_INTEGRITY.md`).
- **Bảng HP theo điểm stat 0:** 0 → **2.500** · 10 → 7.000 · 30 → 16.000 · 60 → 29.500.
- **Hai số tôi từng ghi sai, nay đính chính:** `stepCommon` = **0,18** (không phải 0,168 — 0,168 là
  `stepLevel`); `StartHp` **có** trong `.cctor` (không phải "gán runtime").
- **Điều kiện lật ngược:** nếu tech stat 0 hoặc ability 7 được cộng thêm ở một đường khác chưa đọc
  (**device đã bị loại**: `OnChangeDataDevice` **không** ghi `StartHealth`) thì HPmax phải cộng thêm.

### A2. Bảng **map → wave** — **uỷ thác cho nhánh dữ liệu**

> **Quyết định (23/10):** bảng nằm **inline** trong `.cctor` (25.996 lệnh). Nhánh spec **không tự trích** —
> để nhánh dữ liệu xuất thành CSV/JSON. Khi có file, việc còn lại chỉ là **đối chiếu**, không phải dịch asm.

- **Cấu trúc đã rõ (A):** `Map_Get_Datas.GetListWaves(int mapIndex) → int[]`; `GetNumberWaves()`.
- **Thân `GetListWaves` (A):** đọc singleton → nếu field `@0x0 == 1` lấy `mapIndex` từ `@0x4` (chế độ test), rồi `listMapDatas[clamp(mapIndex, count−1)]`.
- **Vì sao thiếu:** `dump.cs` liệt kê **8 method** cho `Map_Get_Datas` và **không có `.cctor`** — trong khi class có **12 static field** (`listMapDatas`, `listMapBranchDatas`, `listIdBosses`…). Dữ liệu nạp ở đâu đó **không export**.
- **Cách chốt:** dump `Map_Get_Datas..cctor`, hoặc dump runtime `listMapDatas` (12 map × N wave).
- **Trạng thái `68ce86a7` (đo lại 23/10):** `.cctor` **đã có** — **100.896 B · 3.444 hằng `int`**
  và chỉ **40 `debug_rva`** (1,1 %) ⇒ **không** phải vấn đề relocation. Con số `1.192/1.194` slot
  đọc ra `\x7fELF` **chỉ thuộc `Device_Get_Data`** (39 `debug_rva` / 82 hằng = 47,6 %) — xem
  `WHERE_TO_LOOK.md` §1.
- **Đã bóc thử:** **117 cặp** `(A,B)` từ khuôn 8 lệnh (`.cctor` tạo **716 record**, 118 cái cùng khuôn).
  **Giả thuyết "117 cặp = map→wave" BỊ BÁC** bằng phép kiểm thứ tự: wave boss trong `.cctor` là
  `9010, 7001, 7003, 7002, 7004…` — lệch thứ tự, có lặp (`7005`×2), chỉ phủ **17/45**.
  Xem `WHERE_TO_LOOK.md` §2.1.
- **Còn lại:** dạng `w1=3` (**320 record**, lớn nhất) **chưa đọc** — nơi khả năng cao chứa `listMapDatas`.
- **Nếu không chốt:** tự chia 282 wave thành màn (hiện `ENCOUNTERS` đã có phân bố wave theo 20-wave bin).

> **ĐÍNH CHÍNH:** chênh **299 stage vs 282 wave** từng bị tôi ghi như "lệch 18". **Không phải lỗi.**
> `GetListWaves` trả **`int[]`** ⇒ quan hệ **nhiều-một**: nhiều stage dùng chung một wave.
> Hai con số đo **hai thứ khác nhau** (`ENCOUNTERS` §2).

### A3. `Player_Health.OnChangeDataDevice` — ✅ **ĐÓNG** (A)

- **Đã đọc đủ 452 B** trong `Player_Health.asm.txt` (không còn nằm ngoài vùng dump).
- **Kết quả:** **KHÔNG** ghi `StartHealth@0x0` hay `CurrentHealth@0x4`. Chỉ đặt
  `reduceDamageByDevice@0x58` (id **1000–1999**) và `amountAutoGainHpByDevice` (id **5000–5999**),
  rồi gọi `GainHealth`. Chi tiết `BALANCE` §0.6.7d.
- **Hệ quả:** device **không** cộng HP tối đa; nó tăng **HP hiệu dụng** qua giáp + hồi máu.

### A4. Ai gọi `GetStartHp()` — ✅ **ĐÓNG** (A)

- **Caller:** `Player_Health.<Start>b__14_1` (lambda 604 B) — gọi `bl 0x14e311c` rồi `stp s0,s1,[x8]`
  ghi `StartHealth@0x0` + `CurrentHealth@0x4` tại `0x14c7e48`.
- **Caller khác:** `GetGainHpItem` · `GetGainHpItemAddOverTime` (item hồi máu).
- **Kiểm lại `68ce86a7`:** `0x14e311c` xuất hiện **2 lần** trong `Player_Health.asm.txt` ⇒ **không hồi quy**.

### E1. **Asm export bị cắt cụt** — **A** (lỗi công cụ, không phải dữ liệu game)

**Bản `8871068a`:** 11/12 file không kết thúc bằng `ret` ⇒ đã **rút lại 3 kết luận âm tính**
(`.cctor` không gán `StartHp` · không có lệnh ghi `#0x314` · `GetStartHp` chỉ 2 caller). Chi tiết `DATA_SYNC` §7.29.

**Bản `68ce86a7` — kiểm bằng phép đếm, không bằng cờ của pipeline:**

| Trạng thái | Số method | Ghi chú |
|---|---:|---|
| Có header + có lệnh | **400** | — |
| **Vắng hẳn khỏi `asm.txt`** | **25** | 15/17 class |
| Header nhưng 0 lệnh | **0** | — |

- **24/25 là stub 8 B** (`ret`) ⇒ **không mất logic**.
- **1/25 là `Player_Ingame.get_IsAttacking` (32 B)** ⇒ **mất thật**; xem **E4**.
- ⚠ **Bẫy:** cờ `ends_clean` của pipeline trả **`True`** cho method **vắng mặt** (khối rỗng ⇒ điều kiện
  thoả vacuous). **Cờ báo "sạch" cho file thiếu method là cờ tệ hơn không có cờ.** Cách sửa: cờ 4
  (`ASM_INTEGRITY` §3) — `present = len(insns) > 0` **và** opcode cuối hợp lệ.

### E2. `Data_Players` **38** dòng — ✅ **ĐÓNG: tôi đọc sai, KHÔNG phải lỗi công cụ**

| Nguồn | Số dòng | id | Loại |
|---|---|---|---|
| `14-Data_Players.csv` | **38** | `10001–10024` + `10999` + `20001–20013` | class **dùng chung** |
| `datas/ships.json` · `14-ships.csv` | **25** | `10001–10024` + `10999` | **tàu** |
| `datas/drones.json` | **13** | `20001–20013` | **drone** |

**Bằng chứng (A, kiểm độc lập trên `68ce86a7`):**

- `drones.json` = **13 item**, id **20001–20013**, `star` **1,0–5,02**, `actived` **12/13** (`20013` = `False`).
- `14-Data_Players.csv` chỉ có **4 cột**: `['Actived','Sprite','Star','id']` — **0** cột HP.
- `BALANCE` §3.2 **cùng repo** đã ghi "**13 drone**" từ `14-drones.csv` — tức **file này mâu thuẫn với
  `BALANCE`, không phải pipeline thiếu dòng**.

⇒ **Số tàu = 25.** `200xx` **không** phải "bộ tàu thứ hai bị bỏ sót".
**Bài học:** `Data_Players` là bảng **cha** cho cả tàu lẫn drone; đọc nó như bảng riêng của tàu là
**sai từ đầu**. Đây là lỗi **mâu thuẫn nội bộ spec**, và lẽ ra tôi phải tự bắt được.

## 3. Nhóm B — dữ liệu **có** nhưng chưa lấy được

### B1. Ba bảng stat của device — **D**
`listStatValues` · `percentByLevels1` · `percentByLevels2` nạp bằng
`RuntimeHelpers.InitializeArray` từ **field RVA data**. Không có trong `dump.cs` lẫn asm.
**Cách chốt:** đọc vùng `.data` tại RVA của 3 field, hoặc chạy game in `GetStatValue1/2` cho 5 loại × rank 0…n.

**Trạng thái `68ce86a7`:** vẫn **MISSING**. Đo trên 17 class: **1.192/1.194** hằng `debug_rva` giải ra
`a = 0x0` với `a_bytes = 7f454c46…` (`\x7fELF`) ⇒ pipeline đang đọc **header file** thay vì **VA sau
relocation**. 5 commit về `.rela.dyn`/two-level decode **chưa đổi kết quả đo**.
**Điều kiện lật ngược:** nếu 3 bảng được nạp bằng `List.Add` trong `.cctor` (như `NumberTechStats`)
thì đọc RVA **vô ích** — phải parse `.cctor` của `Device_Get_Data`.

### B2. 13 tàu `20001–20013` — **C** (xem E2)

### B3. HP enemy scale theo stage — **D**, và **giả thuyết cũ của tôi SAI**

> **Kiểm chéo 23/10 (`VERIFY_ROUND1` §1):** lô song song báo `T3` = PASS vì `GetSurvivalScore` có
> **5/5** hằng `6,0 · 3,0 · 1,1 · 0,2 · 0,5`. **PASS đó không đóng được B3** — hàm này là **điểm**
> (`Mathf.RoundToInt(bracket × base)`, xem §3 B3 bảng dưới), **không** phải HP. Tiền đề giả định
> `H3` của tôi **sai**; `B3` giữ nguyên **D**.

Tôi từng nghi `Enemy_Data_Balance` chứa công thức HP. **Đọc đủ 7 method: không có method nào trả HP.**

| Method | Trả về |
|---|---|
| `GetArenaPlayScore` · `GetArenaScore` · `GetPVPPlayScore` · `GetSurvivalScore` | **điểm** |
| `GetBonusCoin` · `GetBonusExp` | **thưởng** |
| `.cctor` | nạp bảng |

`GetSurvivalScore(int id)` đọc được toàn bộ (A):

```
bracket = stageField @0x8c   → L<6: ×6,0 · L<15: ×3,0 · L<23: ×C1 · L<29: ×0,5 · else ×C2
base    = theo id:  30000–30015 → 15,0 | 30,0 (bitmask 0x183)
                    30018–30039 → 15,0 | 40,0 (bitmask 0x200601)
                    36000–37000 → 85,0 · 37000–38000 → 230,0 · 38000–39000 → 500,0
                    ngoài dải    → 1
return  Mathf.RoundToInt(bracket × base)
```

⇒ đây là **công thức điểm chế độ sinh tồn**, **không phải HP**.

**Dữ liệu HP enemy thật (`Enemy_Datas.csv`, 981 dòng):**

| Chỉ số | Giá trị (bản `6109008c`) |
|---|---|
| `StartHealthPoint > 0` | **467 / 981** · **72 giá trị khác nhau** (1.000 – 10.000.000) |
| `StartHpPoint` | **0 ở 981/981** ⇒ field chết |
| `CurrentHealthPoint` | **0 ở 981/981** ⇒ field chết |
| **`Boss-*`** (root prefab) | **38 / 39 có HP > 0** (`Boss-39003` = **0**) · 213 dòng, 173 dòng > 0 · khoảng 90.000 – 31.480.000 |
| **`CB-*`** (enemy thường) | **1 / 37** — chỉ `CB(TEST)` = 10.000.000 |
| `CB-30003` · `CB-30015` · `CD-31002` | **0,0** · **0,0** · **0,0** |

### ✅ ĐÃ CHỐT (23/10): HP enemy **CÓ THẬT**, nằm trong **một `Dictionary` chưa dump**

Chi tiết: `ENEMY_HP_RUNTIME.md`. Ba mắt ghép:

| Bằng chứng (mức A) | Số |
|---|---|
| `Enemy_Hp_Bar` instance, `m_Enabled = 1` | **909 / 909** |
| Prefab **thực sự được spawn** có HP bar | **108 / 109** |
| Quân thuộc prefab có HP bar | **45.555 / 45.659 = 99,8 %** |
| `CB-30003` (4.793 quân — nhiều nhất game) | **có** `CB-30003/Enemy_UI/HP_Bar`, đang bật |

⇒ ❌ **"HP bar chỉ có trên boss" là SAI** — câu đó tôi dùng làm bằng chứng cho "chết 1 phát"
mà **chưa bao giờ kiểm**. Rút lại.

**Nguồn HP thật (mức A, đọc từ `dump.cs`):**

```csharp
public class Enemy_Get_Datas : MonoBehaviour {
    private static Dictionary<int, float> AllStartHealthPointEnemies;   // 0x0
    public static float GetStartHealthPoint(int _enemyId);   // RVA 0x157F6A8
    public static float GetDamagePowered(float _crtDamage);   // RVA 0x157EEA0
    private static void .cctor();                             // RVA 0x157F7CC
}
```

`Enemy_Controller.GetStartHealth()` · `TakeDamage()` · `UpdateHpBar()` · `CacheComponents()`;
`Enemy_Health.CalculateDamage(float, ref float _hp, bool)` + **`armor` @`0x34`** ⇒ **enemy cũng có giáp**.

⇒ **`B3` chuyển D → B**: cơ chế đã rõ, chỉ thiếu **nội dung bảng HP** — và nó nằm trong
**một `.cctor`**. `Enemy_Get_Datas` **không có** trong 17 class của `TARGET_CLASSES`.

**Đường cong độ khó (× `copies`, bản **`68ce86a7`**; cột "cũ" là `6109008c`):**

| Wave | có HP | median | max | cũ |
|---|---|---|---|---|
| 0–239 | **4 / 240** | 0 | 5.000.000 | 5/240 · max 7.000.000 |
| 220–239 | 3/20 | 4.160.000 | 5.000.000 | 3,31 M |
| 240–259 | **20/20** | **8.600.000** | **13.520.000** | *(khớp tuyệt đối)* |
| 260–279 | 19/20 | **15.400.000** | **29.370.000** | 16,23 M · max 33,42 M |
| 280–282 | 2/2 | **18.300.000** | 20.200.000 | 20,6 M |

⇒ **≈ 1,79× mỗi 20 wave**; tổng HP toàn game **480.892.000** (bản `68ce86a7`).
⚠ Bản `6109008c` cho **1,89×** / **496.410.000** — con số **đổi theo lần export** nên hạ **A → B**.
Bin **240–259 khớp tuyệt đối** giữa hai bản (8,60 M · max 13,52 M). Định nghĩa phép tính ở
`VERIFY_ROUND1` §4.2; **điều kiện lật ngược:** export sau trả lại instance đã mất ⇒ về ≈496 M.

**Cách chốt:** dump `Enemy_Health.asm.txt`, tìm **1 lệnh ghi** vào `StartHealth`. Rất rẻ.
Đây là **câu hỏi số 1 còn lại** vì nó quyết định toàn bộ cảm giác chơi.

### B4. `GetCountEnemies` / `GetCountAllEnemies` mỗi stage — **D**
Có thân hàm (A): duyệt `GetListWaves(stageIndex)` → đếm theo `listIgroneEnemies`. **Thiếu `listMapDatas`** (A2) nên chưa ra số.

### B8. Hệ số chế độ cho **số quân** và **HP** — **cơ chế A, giá trị C**

**Người chơi đã kiểm chứng trực tiếp (23/10):** chế độ khó hơn **đông enemy hơn** và **nhiều máu hơn**.
Không còn phải suy đoán *có hay không* — chỉ còn *ở đâu* và *bao nhiêu*.

**Ở đâu:** bằng **loại trừ**, không phải bằng phỏng đoán (`DIFFICULTY_MODES.md` §5):

| Ứng viên | Số đo | Kết quả |
|---|---|---|
| Bảng HP theo chế độ | `Enemy_Datas` **981** instance, **1 HP/prefab** | ❌ không tồn tại |
| Bảng quân theo chế độ | `Call_Data` **23.757**, `number = 0` ở **23.757/23.757**, không field chế độ | ❌ không tồn tại |
| Hàm đếm tự nhân | `GetCountEnemies` **304 lệnh · 0 `mul` · 0 `get_stageMode`** | ❌ |
| Cột chế độ trong CSV | `Wave.csv` · `Stage_Behaviour.csv` (52 cột) | ❌ |
| **Thân hàm spawn** | `Path_Spawner.<SpawnEnemies>d__1.MoveNext` **840 B** | ✅ **chỗ còn lại duy nhất** |

**Bao nhiêu:** **CHƯA BIẾT**, và **không** suy được từ bảng (không có bảng). Hai đường lấy:
(a) dump `Path_Spawner`/`PointToPoint_Spawner` (2 class, **chưa** trong `TARGET_CLASSES`);
(b) **đọc trực tiếp trong game** — `txt_mission_kill_enemies` in `"Eliminate {0} enemies"` (ra `kCount`),
và đếm số phát bắn để giết cùng một enemy (ra `kHp`). Giao thức: `DIFFICULTY_MODES.md` §5.4.

### B5. 43/305 trace chưa đối chiếu
`formula_traces.json.gz` có **305 trace / 43 method**; đã dùng ~các trace chính (`stepLevel`, `GetCostUpgrade`, `NumberTechStats`). 43 method còn lại **chưa từng đọc** ⇒ rủi ro sai số ở các ngưỡng phụ.

### B6. 19/37 class Director **không khai báo** field damage — **C**

| Có field damage | **18** class / 63 instance |
|---|---|
| Không có | **19** class: `Boss1`, `Boss3`, `Boss4`, `Boss5`, `Boss7`, `Boss8`, `Boss_Director`, `Boss19/20/21_AttackPhases`, `MB2`–`MB8`, `MB10` |

⇒ 19 nhóm này damage nằm ở **súng con** (`Gun_Attack.bltDamage`, 28 giá trị, median 300) ⇒ cần
**map súng → boss** qua `prefab_joins` để có damage đầy đủ. **Làm được**, chưa làm.

**Giá trị **đã** chốt cho 18 class (A — đọc `typetrees`, khớp `CSV` ở 9 file có CSV):**

| Boss | Damage các đòn | Biến thể |
|---|---|---|
| `MB9` (Boss-37011) | 1.000 | — |
| `MB11` (37013) | 350 · 350 · 400 · 400 | — |
| `MB12` (37014) | 400 · 800 · **1.000.000** | 2 instance giống nhau |
| `MB13` (37015) | 400 · 350 | — |
| `MB14` (37016) | 600 · 350 · 500 · 400 | — |
| `MB15` (37017) | laser 80 · 350 · 600 · 800 · 450 | — |
| `MB16` (37018) | laser 50 · 400 · 600 · 1.000 | — |
| `MB19` (37019) | 300 | — |
| `MiniBoss1` (37002) | laser 55 | — |
| `Boss6` | 2.800 / 600 | **2 giá trị** |
| `Boss9` | 800 / 500 | **2 giá trị** |
| `Boss10` | 8 đòn, 350–1.350; laser 50 → 180 | **2 bộ, đòn mạnh ×1,69** |
| `Boss11` · `Boss12` · `Boss15` · `Boss17` · `Boss18` | 300–1.500 | **2 dòng giống hệt** |

⇒ **Chỉ 3/9 boss có CSV hai biến thể khác nhau** (`Boss6`, `Boss9`, `Boss10`).
5 boss còn lại (`11`, `12`, `15`, `17`, `18`) khai **2 dòng nhưng damage y hệt** ⇒ **độ khó không tăng
qua damage** ở các boss này.

**`wallBltDmg = 1.000.000`** (`MB12`) — gấp **1.250×** đòn cao nhất còn lại (800) ⇒ **sentinel**
(kill-plane), không phải đòn đánh. **Đừng** đưa vào bảng DPS.

### B7. **`NumberTechStats()` = 60** — ✅ **ĐÃ CHỐT ngay trong vòng này** (A)

Thân hàm chỉ **6 lệnh** có nghĩa:

```
ldr x8, [x0, #0xb8]     ; static holder
ldr x8, [x8, #0x40]     ; → List
cbz x8, null-ref
ldr w0, [x8, #0x18]     ; return List.Count
```

⇒ `NumberTechStats()` **không phải hằng số** — nó trả **`Count` của một `List` static** (field `@0x40`).
Vậy **60 = số bản ghi trong bảng tech**, **không** phải "60 cấp".

Kết hợp với `12-localization.csv` (chỉ **12** stat có nhãn, id `0–11`) và
`GetMainCannonDamage` tra **`10001 + playerIndex`** (`mov w8, #0x2711`):

⇒ **Bảng tech có 2 dải id:** `0–11` = tab **Basic** (có nhãn UI), `10001+playerIndex` = stat
**riêng từng tàu** (không có nhãn trong file chữ). `60 = 12 + 48` là giả thuyết khớp số, **chưa
kiểm từng id** — nhưng **không còn là ẩn số về cơ chế**.

### C7. **45 root prefab mã `900xx`** — nằm ngoài roster (A)

`prefab-roots.csv`: **2.081 root**, trong đó **45 root** khớp `^900\d\d$` — **đúng 5 chữ số**
(`90017`–`90071`). ⚠ **Phải ghi regex:** `^900\d\d` (không neo) cho **48**, vì bắt thêm
`90030 [Quest_Notice]` · `90036-Lasers` · `90053-Laser`. Hai số đúng với hai định nghĩa. **Không mã nào** trong 45 xuất hiện trong **45.659 quân đã spawn** (kiểm 100% qua
`prefab-roots.csv`). ⇒ hazard/obstacle/zone **đặt sẵn hoặc dự phòng**, không nằm trong luồng wave.
**Chưa biết** cái nào được dùng trong màn nào.

---

## 4. Nhóm C — dữ liệu **vắng mặt thật**: phải **quyết** khi thiết kế

| # | Thiếu gì | Bằng chứng | Bản clone phải quyết |
|---|---|---|---|
| C1 | **Time** của animation event | 318 clip / **793 event** nhưng chỉ có `m_Events__count`; **0 keyframe** | nhịp bắn: dùng `Gun_Attack.timeShot` cho 13,3% súng; **86,7% còn lại tự đặt nhịp** (gợi ý 0,08–0,25 s) |
| C2 | controller → clip | **0** bản ghi | tự đặt tên state: `idle`/`move`/`attack`/`die` |
| C3 | `Spawner.dataScript` | rỗng **100%** (11.099 spawner) | dùng `waves.json` (45.659 quân) làm nguồn duy nhất |
| C4 | `Wave.indexWave` | **0** toàn bộ | thứ tự wave = thứ tự trong `waves.json` |
| C5 | `Call_Data.number` / `editType` | **0** ở 23.757/23.757 | số quân mỗi lần gọi = `len(listPrefabEnemies) × copies` |
| C6 | damage va chạm enemy thường | `Enemy_Physics.allColliders = []` **981/981** | **enemy thường không gây damage khi chạm** — chỉ đạn; nếu muốn clone "khó hơn" thì đây là knob |
| C8 | damage va chạm boss | `Boss_BodyPhysics` **251** instance, median 500 | boss **có** damage chạm; giữ |

---

## 5. Nhóm D — cần **chạy game** mới chốt

| # | Vấn đề | Đã biết | Phải tự quyết |
|---|---|---|---|
| D1 | Feel: aim assist, gia tốc, input latency | không có trong dữ liệu tĩnh | chọn "arcade mượt": aim assist ±12°, drag 0,12 s |
| D2 | Thứ tự resolve stat | mô hình **B**: `save → device(tàu) → tech → ability → StartHealth → CurrentHealth`, chốt **1 lần** trước spawn (`BALANCE` §0.6.8) | giữ đúng thứ tự này |
| D3 | Tỉ lệ rơi item | không có; item hồi máu gọi `GetStartHp()` (A4) | tự đặt: 1 item/45 s hoặc theo wave |
| D4 | % giảm damage của `Armor` / `reduceDamageByDevice` | có **tên field**, chưa có hệ số | tự đặt: giáp giảm 20–40%, trần 75% |

---

## 6. **Đã đóng** trong vòng này (ghi để không làm lại)

| Việc | Kết quả | Mức |
|---|---|---|
| Device: bao nhiêu loại, mấy stat | **5 loại × 2 stat**, `type 4` = phần trăm | A |
| Device: mấy slot mỗi tàu | **4** (`GetPlayerUse` `cmp x8,#4`) | A |
| Device có cộng HP **tối đa** không | ❌ **KHÔNG** — `OnChangeDataDevice` 452 B **không** ghi `StartHealth`; chỉ **giáp** (id 1000–1999) và **hồi máu** (id 5000–5999). HP **hiệu dụng** vẫn tăng, HP **tối đa** thì không | A |
| Device thuộc về tàu nào | **đúng 1 tàu** (`Player_Device_Saved_Datas.GetPlayerDevices` theo `playerIndex`) | A |
| HP chốt lúc nào | **`Player_Health.Start()`** → lambda `<Start>b__14_1` → `bl GetStartHp 0x14e311c` → `stp s0,s1,[x8]` @`0x14c7e48` ⇒ `StartHealth@0x0`, `CurrentHealth@0x4` | A |
| Hồi sinh có tính lại stat | **KHÔNG** | A |
| Damage 18/37 class Director | bảng đầy đủ ở §3 B6 | A |
| `GetSurvivalScore` | công thức đầy đủ; **không phải HP** | A |
| Asm export bị cắt | `8871068a`: **11/12 file** ⇒ rút lại 3 kết luận âm tính. `68ce86a7`: **25 method vắng hẳn** (24 stub + 1 method 32 B) | A |
| **13 dòng `200xx` là gì** | **drone** (13 item, `star` 1,0–5,02) — **không** phải tàu bị bỏ sót; số tàu = **25** | A |
| `GetSurvivalScore` có phải HP | **KHÔNG** — là **điểm** (`bracket × base`), 5 hằng số khớp 100% | A |

---

## 7. Còn thiếu / phải đoán

1. **Ưu tiên 1 — 200 lệnh** sau `0x14e5cc4` (`Player_Get_Datas..cctor`): có thể đóng **A1**, mở khoá
   toàn bộ phần cân bằng damage/HP.
2. **Ưu tiên 2 — `Map_Get_Datas..cctor`** hoặc `listMapDatas`: đóng **A2** + **B4**, tức là biết
   "màn nào gồm wave nào" và "màn có bao nhiêu quân".
3. **Ưu tiên 3 — đọc thân `GetListAllIdPlayers()`** (đã có asm, **không cần dump thêm**): chốt **E2/B2**
   (13 tàu `20001–20013` là thật hay dữ liệu chết).
4. **Ưu tiên 4 — map súng → boss** từ `prefab_joins`: nâng **B6** từ 18/37 lên 37/37 nhóm đòn.
5. Những mục **C1–C8** thì **không có đường lấy thêm** bằng dump tĩnh — đã kiểm bằng số đếm, và bản
   clone **phải tự quyết**. Ghi rõ để không ai đi tìm lại.
6. **Rủi ro còn lại lớn nhất:** mọi con số về **nhịp bắn** (86,7% súng) và **thời điểm ra đòn của boss**
   đều là **suy luận**, không phải số gốc. Cân bằng damage sẽ lệch nếu nhịp thật khác.
