# Sổ vấn đề **chưa chốt** — tổng hợp

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

## 1. Bảng tổng — **25 vấn đề**, chia theo **nguyên nhân** (quan trọng hơn mức độ)

| # | Vấn đề | Nhóm | Mức | Ảnh hưởng thiết kế |
|---|---|---|---|---|
| A1 | Giá trị `StartHp` | **lỗi export** | D | **chặn TTK** — không có HP thì không cân được damage |
| A2 | `Map_Get_Datas` không có `.cctor` ⇒ bảng map→wave | **lỗi export** | D | chặn "màn nào gồm wave nào" |
| A3 | `Player_Health.OnChangeDataDevice` ngoài vùng dump | **lỗi export** | C | chặn "device cộng bao nhiêu HP" |
| A4 | Caller thật của `GetStartHp()` | **lỗi export** | C | xác nhận thời điểm chốt HP |
| B1 | 3 bảng stat của device | **RVA data** | D | chặn "device mạnh bao nhiêu" |
| B2 | 13 tàu `20001–20013` | **chưa lấy** | C | ảnh hưởng số tàu (25 vs 38) |
| B3 | HP enemy scale theo stage | **sai giả thuyết** | D | chặn cân bằng 231/236 wave |
| B4 | `GetCountEnemies` mỗi stage | **chưa lấy** | D | ảnh hưởng nhiệm vụ/độ dài |
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
| E1 | **Asm export bị cắt cụt 11/12 file** | **lỗi công cụ** | A | **vô hiệu mọi kết luận âm tính cũ** |
| E2 | `ships.json` thiếu 13 dòng so với `Data_Players` | **lỗi công cụ** | A | số tàu trong SPEC phải ghi 38 |

---

## 2. Nhóm A — **lỗi export**: chốt được bằng **một yêu cầu rất nhỏ**

### A1. Giá trị `StartHp` — **D**

- **Công thức đã xong (A):** `GetStartHp = StartHp × (1 + stepCommon × TechStatPoints(0) + abi7 × GetNumberAbility(7))`; `stepCommon = 0,168` (`BALANCE` §0.6.1).
- **`TechStatPoints(0)` = stat "Health" của tab Basic** (A) — `txt_techstat_label_0` = `Health`,
  `txt_techstat_desc_0` = "Increase health points"; tab `txt_basic`. ⇒ `StartHp` chỉ là **HP gốc ở cấp 0**;
  phần lớn HP đến từ **nâng cấp**, không phải từ tàu (`BALANCE` §0.6.9).
- **Vì sao thiếu:** `.cctor` của `Player_Get_Datas` **bị cắt giữa chừng** tại `0x14e5cc4`, vẫn đang dựng `List`, **chưa tới** đoạn gán float (`DATA_SYNC` §7.29).
- **Bằng chứng `.cctor` có gán float:** đã thấy đúng **1** hằng `0x41700000` = **15,0** trong phần đọc được.
- **Cách chốt (rẻ nhất toàn dự án):** dump **200 lệnh tiếp theo sau `0x14e5cc4`**.
- **Nếu không chốt:** chọn `StartHp` theo thang damage đã biết — damage đạn 28 giá trị, median **300**, max **1.500**; boss 350–2.800 ⇒ HP player hợp lý **≈ 5.000–20.000**. Ghi là **quyết định thiết kế**, không phải số gốc.

### A2. Bảng **map → wave** — **D**

- **Cấu trúc đã rõ (A):** `Map_Get_Datas.GetListWaves(int mapIndex) → int[]`; `GetNumberWaves()`.
- **Thân `GetListWaves` (A):** đọc singleton → nếu field `@0x0 == 1` lấy `mapIndex` từ `@0x4` (chế độ test), rồi `listMapDatas[clamp(mapIndex, count−1)]`.
- **Vì sao thiếu:** `dump.cs` liệt kê **8 method** cho `Map_Get_Datas` và **không có `.cctor`** — trong khi class có **12 static field** (`listMapDatas`, `listMapBranchDatas`, `listIdBosses`…). Dữ liệu nạp ở đâu đó **không export**.
- **Cách chốt:** dump `Map_Get_Datas..cctor`, hoặc dump runtime `listMapDatas` (12 map × N wave).
- **Nếu không chốt:** tự chia 282 wave thành màn (hiện `ENCOUNTERS` đã có phân bố wave theo 20-wave bin).

> **ĐÍNH CHÍNH:** chênh **299 stage vs 282 wave** từng bị tôi ghi như "lệch 18". **Không phải lỗi.**
> `GetListWaves` trả **`int[]`** ⇒ quan hệ **nhiều-một**: nhiều stage dùng chung một wave.
> Hai con số đo **hai thứ khác nhau** (`ENCOUNTERS` §2).

### A3. `Player_Health.OnChangeDataDevice` — **C**

- **Vị trí:** RVA `0x14C58EC` — **thấp hơn** điểm bắt đầu file `Player_Datas.asm.txt` (`0x14c6b4c`) ⇒ **nằm ngoài** phần đã dump.
- **Đã biết:** tên hàm + tham số `(int _idPlayer)` ⇒ **device → HP có thật** (`BALANCE` §0.6.7d).
- **Cách chốt:** dump **~150 lệnh** tại `0x14C58EC`; cần biết nó ghi `StartHealth (@0x0)` hay `CurrentHealth (@0x4)`.
- **Nếu không chốt:** thiết kế **cho device cộng HP tối đa** — an toàn hơn (nếu gốc chỉ hồi thì bản clone "rộng tay" hơn một chút).

### A4. Ai gọi `GetStartHp()` — **C**

- **Đã thấy:** `GetGainHpItem` (dòng 2.837) · `GetGainHpItemAddOverTime` (2.993) — cả hai là **item hồi máu**.
- **Cảnh báo:** caller thật (ước là `Player_Health.Start` hoặc một `Setup`) **có thể nằm trong phần bị cắt** ⇒ con số "chỉ 2" là **cận dưới**, không phải "chỉ có 2".

### E1. **Asm export bị cắt cụt** — **A** (lỗi công cụ, không phải dữ liệu game)

| File | Method | Lệnh | Kết thúc bằng `ret` |
|---|---|---|---|
| `ArenaManager` | 27 | 1.880 | ✅ |
| 11 file còn lại | 1–72 | 256–7.348 | ❌ **cụt** |

⇒ Đã **rút lại 3 kết luận âm tính** (`.cctor` không gán `StartHp` · không có lệnh ghi `#0x314` · `GetStartHp` chỉ 2 caller). Chi tiết `DATA_SYNC` §7.29.

### E2. `Data_Players` có **38** dòng, `ships.json` chỉ **25** — **A**

| Nguồn | Số dòng | id |
|---|---|---|
| `14-Data_Players.csv` | **38** | `10001–10024` + `10999` + **`20001–20013`** |
| `datas/ships.json` | **25** | `10001–10024` + `10999` |
| `14-ships.csv` | **25** | như trên |

⇒ **13 dòng `20001–20013` bị bỏ sót** khi sinh `ships.json` (`Actived = True` ở 12/13, `20013` = `False`;
`Star` 1,0–5,02; sprite `m_PathID` riêng, không trùng bộ 25 tàu).
**Chưa biết vai trò** — nghi là tàu legendary hoặc bộ tàu của chế độ khác.

> **Nhận định (mức C):** `20001–20013` là **bộ tàu thứ hai**, không phải biến thể sprite của bộ 25.
> **Điều kiện lật ngược:** nếu `GetListPlayers()` hoặc `GetAllShipNoUnlock()` chỉ trả về bộ 25 thì
> `200xx` là dữ liệu chết. Cần đọc thân `GetListAllIdPlayers()` (asm) — **làm được ngay**.

---

## 3. Nhóm B — dữ liệu **có** nhưng chưa lấy được

### B1. Ba bảng stat của device — **D**
`listStatValues` · `percentByLevels1` · `percentByLevels2` nạp bằng
`RuntimeHelpers.InitializeArray` từ **field RVA data**. Không có trong `dump.cs` lẫn asm.
**Cách chốt:** đọc vùng `.data` tại RVA của 3 field, hoặc chạy game in `GetStatValue1/2` cho 5 loại × rank 0…n.

### B2. 13 tàu `20001–20013` — **C** (xem E2)

### B3. HP enemy scale theo stage — **D**, và **giả thuyết cũ của tôi SAI**

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

| Chỉ số | Giá trị |
|---|---|
| `StartHealthPoint > 0` | **467 / 981** · **72 giá trị khác nhau** (1.000 – 10.000.000) |
| `StartHpPoint` | **0 ở 981/981** ⇒ field chết |
| `CurrentHealthPoint` | **0 ở 981/981** ⇒ field chết |
| **`Boss-*`** | **45 / 45 có HP** (90.000 – 31.480.000) |
| **`CB-*`** (enemy thường) | **1 / 37** — chỉ `CB(TEST)` = 10.000.000 |
| `CB-30003` · `CB-30015` · `CD-31002` | **0,0** · **0,0** · **0,0** |

**Hai cách đọc — chưa chốt:**

1. **Enemy thường chết 1 phát.** Ủng hộ: 2 field HP chết · `Enemy_Data_Balance` **0 method HP** ·
   HP bar chỉ có trên boss · 5 cổng chặn trong `TakeDamage`.
2. **Runtime gán HP.** Ủng hộ: ghi chú trong `enemy_hp.json` — *"runtime HP is scaled by
   `Enemy_Data_Balance` and stage"* — nhưng class đó **không có** method HP, nên ghi chú **chỉ sai
   địa chỉ**, không sai ý.

**Cách chốt:** dump `Enemy_Health.asm.txt`, tìm **1 lệnh ghi** vào `StartHealth`. Rất rẻ.
Đây là **câu hỏi số 1 còn lại** vì nó quyết định toàn bộ cảm giác chơi.

### B4. `GetCountEnemies` / `GetCountAllEnemies` mỗi stage — **D**
Có thân hàm (A): duyệt `GetListWaves(stageIndex)` → đếm theo `listIgroneEnemies`. **Thiếu `listMapDatas`** (A2) nên chưa ra số.

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

`prefab-roots.csv`: **2.081 root**, trong đó **45 root** có tên đúng dạng `900xx`
(`90017`–`90071`). **Không mã nào** trong 45 xuất hiện trong **45.659 quân đã spawn** (kiểm 100% qua
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
| Device có cộng HP không | **CÓ** — `Player_Health.OnChangeDataDevice(int)` | B |
| Device thuộc về tàu nào | **đúng 1 tàu** (`Player_Device_Saved_Datas.GetPlayerDevices` theo `playerIndex`) | A |
| HP chốt lúc nào | `StartHealth` **static**; `ResetStaticVariables()` chỉ **chép**; `Start()` **không** tính | A |
| Hồi sinh có tính lại stat | **KHÔNG** | A |
| Damage 18/37 class Director | bảng đầy đủ ở §3 B6 | A |
| `GetSurvivalScore` | công thức đầy đủ; **không phải HP** | A |
| Asm export bị cắt | **11/12 file**, rút lại 3 kết luận âm tính | A |

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
