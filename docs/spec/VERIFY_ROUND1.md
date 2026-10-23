# VERIFY_ROUND1 — kiểm lại 6 phán quyết của nhánh dữ liệu

> **Bản đã đọc:** `arena/ef6b75ef-…` @ **`68ce86a7`** (21 commit mới so với `6109008c`, 6.822 file đổi,
> +25.329 / −9.150). Đọc bằng `git show` trên ref đã fetch — **không merge, không checkout**.
>
> **Đây là báo cáo kiểm chéo, không phải bản sao.** Mỗi phán quyết của họ được tôi **kiểm lại bằng
> phép đo của mình**; chỗ nào tôi không đồng ý thì ghi rõ **vì sao**, chỗ nào họ đúng thì ghi **họ đúng**.
> Quy ước mức A/B/C giữ nguyên như `DONE.md`.

---

## 0. Trả lời ngắn

| Câu hỏi | Trả lời |
|---|---|
| Họ chạy lô song song chưa? | ✅ **6/13 task** (`T2 · T3 · T4 · T6 · T10 · T12`) — chạy **offline**, 1 script, không cần APK |
| Kết quả họ báo | **5 PASS · 1 REVERSED** (`T6`) |
| Tôi kiểm lại thấy mấy cái đúng? | **4/6 đúng nguyên** · **`T2` đúng kết luận nhưng sai cơ chế** · **`T4` đúng nhưng phép kiểm yếu** (chỉ kiểm *có hằng số*, không kiểm *phép toán*) |
| Có gì mới thật? | ✅ **`T6` là phát hiện thật** (13 `200xx` là **drone**, không phải tàu) · ✅ **`T12` xác nhận `2500` lần 2** |
| Có gì vẫn chưa xong? | ❌ **`T1` (map→wave) và `T5` (bảng device) vẫn MISSING** — xem §3, có số đo |

**Một câu:** vòng này **đóng được 2 mục** (`E2`, `B2`), **xác nhận 1 mục** (`A1`), nhưng **không mở được
2 mục quan trọng nhất** (`A2` map→wave, `B1` bảng device) — và lý do **đo được**, không phải "chưa tới lượt".

---

## 1. Sáu phán quyết của họ — và tôi kiểm lại

| Task | Họ báo | Tôi kiểm lại | Kết luận |
|---|---|---|---|
| **T2** | **PASS** — "ctor = 8 byte (method rỗng), `ends_clean` mọi method: True, không thiếu byte nào" | ⚠ **Kết luận đúng, cơ chế sai.** `RankManager.asm.txt` **vẫn dừng ở `0x127cb80`**; `;;; ctor` **không có trong file** (18 header / 19 method). Cờ `ends_clean = True` là **True rỗng** — khối không tồn tại thì không có `ret` nào để kiểm | ⚠ **PASS về hệ quả · REVERSED về cơ chế** |
| **T3** | **PASS** — 5/5 hằng `6,0 · 3,0 · 1,1 · 0,2 · 0,5` | ✅ Đúng: 5/5 có trong `GetSurvivalScore` (612 B). ⚠ Nhưng **tiền đề của tôi sai**: hàm này là **score**, không phải HP — nên PASS **không** đóng được `B3` | ✅ PASS · ⚠ **giả định H3 của tôi vô nghĩa** |
| **T4** | **PASS** — `cmp [30,58,118,248]`, float `[0,168 · 1,0 · 1,05 · 1,15]`, có `#0x2711` | ✅ Phần `stepLevel` **đúng từng số**. ❌ Phần `10001` tôi mô tả **sai phép toán**: asm là `mov w0,#0x2711` (nhánh return) **và `adds w19,w19,#-0x2711`** = **TRỪ 10001** để lấy chỉ số, **không phải `add w0,w19,#0x2711`** | ✅ PASS · ❌ **H4b của tôi sai chiều** |
| **T6** | **REVERSED** — `20001–20013` là **drone**, không phải tàu | ✅ **Đúng, và tôi kiểm độc lập**: `datas/drones.json` có **13 item**, id **20001–20013**, `star` **1,0–5,02**, `actived` **12/13** — khớp từng con số với bảng `E2` của tôi, chỉ khác **nhãn** | ✅ **REVERSED — tôi sai** |
| **T10** | **PASS** — "**48** root 900xx, 0 lần trong waves" | ✅ Phần "0 lần trong waves" **đúng**. ⚠ Số **48** là **do regex không neo**: `^900\d\d` bắt thêm 3 tên có hậu tố. `^900\d\d$` = **45** — đúng số tôi đã ghi | ✅ PASS · ⚠ 48 vs 45 = **khác định nghĩa** |
| **T12** | **PASS** — cặp `VA 0x757bc0: [0,18 · 2500,0]` | ✅ **Đúng.** 15 cặp `ldr d`; cặp `(0,18 · 2500,0)` có mặt. Tôi kiểm lại bằng chính file asm của họ: `Player_Health.asm.txt` vẫn gọi `0x14e311c` **2 lần** ⇒ không có hồi quy | ✅ **PASS — `A1` nay là A hai nguồn** |

---

## 2. Hai chỗ tôi không đồng ý — kèm phép đo

### 2.1 `ends_clean` của họ có **lỗi True rỗng** — và nó che đúng thứ tôi lo

Tôi quét **cả 17 class**, so **mọi method** trong `*.json` với khối `;;;` trong `*.asm.txt`:

| Trạng thái | Số method | Ví dụ |
|---|---:|---|
| Có header + có lệnh | **400** | — |
| **Mất hẳn khỏi asm** (không có cả header) | **25** | `RankManager.ctor` · `Player_Get_Datas.ctor` · `Player_Attack.SetPlayerRank` |
| Header nhưng 0 lệnh | **0** | — |

**24/25 là stub 8 byte** (`ret` + padding) ⇒ **không mất gì**. Nhưng **1 method là 32 byte**:

```
Player_Ingame.get_IsAttacking   rva 0x14b279c   32 B   → KHÔNG có trong asm
```

Và nó **đứng một mình**: không method nào của `Player_Ingame` nằm trong **±0x60** quanh
`0x14b279c`. Nghĩa là đây **không phải cụt đuôi** mà là **lỗ hổng giữa file** — đúng loại mà cờ 2
của tôi **không bắt được** (`ASM_INTEGRITY` §6 mục 2, tôi đã tự ghi là "chưa kiểm").

**Vì sao `ends_clean` không bắt:** cờ đó định nghĩa là *"có `ret` trong ≤48 lệnh cuối"*. Với method
**vắng mặt**, danh sách lệnh **rỗng** ⇒ vòng lặp không chạy ⇒ `False`? Nhưng JSON ghi `True`.
Tức là khi khối rỗng, điều kiện được thoả **vacuous** — cùng một lỗi logic với "for all x in ∅: P(x)".
**Một cái cờ báo "sạch" cho file thiếu method là cái cờ tệ hơn không có cờ.**

> **Sửa tối thiểu (1 dòng):** thêm `present = len(insns) > 0` vào từng method, và
> `ends_clean = present and last_op in {ret,b,br,retab}`. Sau đó **method vắng mặt sẽ FAIL** thay vì
> PASS. Đây chính là **cờ thứ tư** tôi viết ở `ASM_INTEGRITY` §3.

### 2.2 `T2` — "không thiếu byte nào" **sai**, nhưng **không mất dữ liệu**

Chính xác đến từng địa chỉ:

```
max(addr trong RankManager.asm.txt) = 0x127cb80      ← dòng cuối là: 0x127cb80: ret
ctor                                 = 0x127cb84, 8 B → kết thúc 0x127cb8c
```

Thiếu **đúng 8 byte** — tôi đúng về phép đo. Nhưng `ctor` 8 byte của một class không có field
khởi tạo **chỉ là `ret`** ⇒ **không có logic nào bị mất**. Vậy:

| Vế | Ai đúng |
|---|---|
| "`RankManager` thiếu 8 B" | **tôi đúng** (đo được, vẫn còn ở `68ce86a7`) |
| "Việc đó vô hại" | **họ đúng** |
| "Không thiếu byte nào" | **sai** |
| "`ends_clean` chứng minh điều đó" | **sai** — cờ đó True rỗng |

⇒ Sửa cách ghi trong `ASM_INTEGRITY`: **FAIL của tôi là FAIL thật nhưng vô hại**, không phải
"dương tính giả". Đây là khác biệt quan trọng: nếu tôi ghi "dương tính giả" thì lần sau một FAIL
thật cũng bị bỏ qua.

### 2.3 `T10` — 45 hay 48, tuỳ định nghĩa, và định nghĩa phải ghi

| Regex | Số root | Gồm |
|---|---:|---|
| `^900\d\d$` (**đúng 5 chữ số**) | **45** | `90026 · 90043 · …` |
| `^900\d\d` (tiền tố) | **48** | thêm **`90030 [Quest_Notice]` · `90036-Lasers` · `90053-Laser`** |

Cả hai đều đúng. Tôi giữ **45** nhưng ghi kèm **regex** — đây đúng là quy tắc tôi đã tự đặt
("mỗi số ghi nguồn") và đã vi phạm ở chính con số này.

---

## 3. `T1` (map→wave) và `T5` (bảng device) — **vẫn MISSING**, có số đo

5 commit gần nhất đều về giải mã RVA/two-level decode (`238e0f6a` · `63fe3f54` · `5949129f` ·
`9247f333` · `68ce86a7`). Tôi đếm **kết quả**, không đọc commit message:

| Phép đo trên `68ce86a7` | Số | Nghĩa |
|---|---:|---|
| Hằng `debug_rva` trong 17 class | **1.194** | mọi slot RVA mà pipeline chạm tới |
| Slot giải ra **`a = 0x0`** | **1.192** | **98,3 %** |
| Trong đó `a_bytes` bắt đầu bằng `7f454c46` (`\x7fELF`) | **1.192** | đang đọc **header file**, không đọc vùng dữ liệu |
| Slot giải ra khác 0 | **2** | — |
| `.cctor` của `Map_Get_Datas` | **100.896 B · 3.484 hằng** | dữ liệu **có**, nhưng **chưa bóc thành mảng** |

⇒ Chuỗi RVA **vẫn chưa nối được**. Không có file `map_waves.csv` / `device_stats.csv` nào được sinh.
`T1` · `T5` giữ nguyên **MISSING**.

> **Nhận định (mức B):** `a_bytes = b"\x7fELF…"` là chữ ký rất rõ — code đang lấy **địa chỉ file**
> thay vì **địa chỉ VA sau relocation**. Với `R_AARCH64_RELATIVE` phải cộng **addend** vào **base
> load**, không phải đọc thẳng `*(slot)`. Nếu slot chứa `0`, addend nằm trong `.rela.dyn` —
> đúng như commit `68ce86a7` nói, nhưng **kết quả chưa đổi** ⇒ nhánh đó chưa chạy hoặc chạy sai.
> **Điều kiện lật ngược:** nếu tồn tại bảng map→wave **không** nằm ở RVA field-data mà được nạp
> bằng `List.Add` trong `.cctor` (như `NumberTechStats`), thì đọc RVA **vô ích** — phải parse
> `.cctor`. `.cctor` 100.896 B là đủ để thử, không cần APK.

---

## 4. Số liệu **đã đổi** vì tái export — phải cập nhật spec

Tôi tính lại **từ file của họ**, không chép số họ báo.

### 4.1 Wave

| Số | `6109008c` | **`68ce86a7`** | Ghi chú |
|---|---:|---:|---|
| `count_waves` | 282 | **282** | không đổi |
| `count_spawners` | 11.095 | **11.092** | −3 |
| `Σ len(enemies)` | 22.471 | **22.457** | −14 |
| `Σ len × copies` | 45.659 | **45.659** | **không đổi** — chênh lệch nằm ở wave `unknown` |
| Median quân/wave | 130,5 | **131,5** | — |
| Max quân/wave | 951 | **951** | — |
| Prefab khác nhau | 109 | **109** | — |
| **Σ `copies`** | 23.757 | **23.757** | ✅ = **số dòng `Call_Data`** — xác nhận `Call_Data` là **mỗi bản sao** của spawner, không phải mỗi spawner |

### 4.2 HP boss theo wave — **con số 1,89× phải hạ xuống 1,79×**

**Định nghĩa (tôi chốt, để `T13` chạy được):** chia theo **thứ tự wave trong `waves.json`**
(1…282); mỗi wave = **tổng HP của mọi enemy được spawn × `copies`**; HP của một prefab =
**tổng mọi dòng `15-enemy-hp.csv` có `gameobject` = prefab hoặc bắt đầu `prefab/`** ("cộng dồn mọi
bộ phận"); bin **20 wave**; median chỉ tính wave có HP > 0.

| Bin | `6109008c` (đang ghi trong spec) | **`68ce86a7` (đo lại)** |
|---|---|---|
| 0–239 | 5/240 | **4/240** |
| 220–239 | 3,31 M | **4,16 M** (3/20) |
| 240–259 | 19/20 · **8,60 M** · max 13,52 M | 20/20 · **8,60 M** · max **13,52 M** |
| 260–279 | 20/20 · **16,23 M** · max 33,42 M | 19/20 · **15,40 M** · max **29,37 M** |
| 280–282 | 1/2 · **20,6 M** | 2/2 · **18,30 M** |
| **Tổng toàn game** | **496.410.000** | **480.892.000** ⚠ −3,1 % |
| **Tỉ lệ / 20 wave cuối** | **1,89×** | **1,79×** ⚠ |

⇒ `H13` **REVERSED** ở 3/4 dòng. Bin **240–259 khớp tuyệt đối** (8,60 M / 13,52 M) — đó là bin
duy nhất tôi giữ **A**; ba dòng còn lại hạ xuống **B** kèm khoảng.

> **Vì sao đổi:** `15-enemy-hp.csv` mới có **249 root** (cũ 251) và **70 root đổi giá trị** — ví dụ
> `Boss-39012` 4,5 M → **2,8 M**, `Enemy_Ingame` 4,3 M → **2,5 M**. Số `instances` của
> `Board_FightBoss` 19 → **10**. Đây là **cùng một nguồn, hai lần export khác nhau** ⇒ con số này
> là **mức B**, không phải A.

### 4.3 Một phát hiện mới từ dữ liệu mới: **chỉ còn 1 boss HP = 0**

`BALANCE` §2.2 ghi "**5 prefab có tổng HP = 0**". Bản mới:

| Prefab | `6109008c` | **`68ce86a7`** |
|---|---:|---:|
| `Boss-37009` | 0 | **4.200.000** |
| `Boss-37012` | 0 | **2.800.000** |
| `Boss-39007` | 0 | **3.564.000** |
| `Boss-39008` | 0 | **8.820.000** |
| `Boss-39003` | 0 | **0** ⚠ (vẫn 0, 2 dòng) |

⇒ **1/39 boss không có HP** (`39003`), không phải 5. Khớp `BOSSES.md` ("1/39") — tức `BALANCE`
mới là file sai.

### 4.4 13 `200xx` là **drone** — `E2` phải đóng bằng "tôi đọc sai", không phải "lỗi công cụ"

| Bằng chứng | Số |
|---|---|
| `datas/drones.json` | **13 item**, id **20001–20013** |
| `star` | **1,0 – 5,02** |
| `actived` | **12/13** |
| `14-Data_Players.csv` cột | **`['Actived','Sprite','Star','id']`** — **0** cột HP |
| `BALANCE` §3.2 của tôi | **đã** ghi "13 drone" từ `14-drones.csv` |

⇒ `Data_Players` là **class dùng chung** cho cả tàu lẫn drone. `ships.json` 25 dòng **không** thiếu
gì. `OPEN_ISSUES` E2 (mức **A**, "lỗi công cụ") là **sai**: đây là **tôi đọc một bảng dùng chung
như bảng riêng của tàu**, và **file `BALANCE` cùng repo đã ghi đúng** — tức lỗi **mâu thuẫn nội bộ**,
không phải lỗi pipeline.

---

## 5. Đã sửa gì trong spec sau khi kiểm

| File | Sửa |
|---|---|
| `OPEN_ISSUES.md` | **E2 đóng** (đọc sai, không phải lỗi công cụ) · **B2 đóng** (13 drone) · **E1 ghi lại** 25 method vắng mặt · thêm **E4** (`get_IsAttacking` 32 B mất hẳn) · `A2`/`B1` thêm số **1.192/1.194** · `C7` ghi kèm regex |
| `ASM_INTEGRITY.md` | thêm **cờ 4 — method phải có mặt**; baseline mới **25 vắng mặt / 400 có lệnh**; ghi bài học `ends_clean` True rỗng |
| `BALANCE.md` | bảng HP boss theo wave → số mới; "5 prefab HP = 0" → **1**; hạ `1,89×` → **1,79×**, nhãn **B** |
| `DATA_SYNC.md` | bảng delta thêm cột `68ce86a7`; wave 11.092 / 22.457; HP 480,89 M |
| `PARALLEL_TASKS.md` | §8 kết quả vòng 1: `T2/T3/T4/T6/T10/T12` đã chạy, 7 task còn lại |
| `README.md` | thêm file này; sửa "23.757 spawner" → **11.092 spawner / 45.659 quân** |

---

## 6. Ba việc **rẻ nhất** cho vòng sau — xếp theo chi phí

| # | Việc | Chi phí | Vì sao rẻ |
|---:|---|---|---|
| 1 | Sửa `ends_clean` thành `present and last_op in {...}` | **1 dòng** | để method vắng mặt **FAIL** thay vì PASS — hiện tại cờ báo "sạch" cho file thiếu method |
| 2 | Export riêng `Player_Ingame.get_IsAttacking` (32 B, `0x14b279c`) | ~1 khối asm | hoặc xác nhận **không lấy được** ⇒ bản clone suy `IsAttacking` từ trạng thái |
| 3 | Thử **parse `.cctor`** của `Map_Get_Datas` (100.896 B) **trước** khi sửa RVA reader | 1 script ~60 dòng | nếu bảng nạp bằng `List.Add` (như `NumberTechStats`) thì sửa RVA **vô ích** — và `.cctor` đã có sẵn |

> **Vì sao không đưa `T9` (animation) lên đây:** `T9` cần AssetRipper + decode `m_StreamedClip`, tốn hơn
> ba việc trên **cộng lại**. Nó quan trọng cho *feel*, không chặn *cơ chế*.

---

## 7. Còn thiếu / phải đoán

- **`T1` · `T5` vẫn MISSING.** Tôi **không** kết luận "không lấy được" — chỉ kết luận "lần export này
  chưa lấy được", kèm số 1.192/1.194. **Điều kiện lật ngược:** nếu bảng nằm trong `.cctor` dạng
  `List.Add` thì phải parse `.cctor` (100.896 B), **không** phải sửa RVA reader.
- **`B3` (HP enemy runtime) vẫn mở.** `GetSurvivalScore` 612 B có 5/5 hằng nhưng đó là **score**
  (`GetSurvivalScore` được dùng ở `ArenaManager`/ranking), **không** phải HP. Vẫn cần
  `Enemy_Health.asm.txt` tìm lệnh ghi `StartHealth`.
- **`T13` chỉ còn 1 bin đạt ±2 %** (240–259). Ba bin kia lệch vì export đổi; nếu export đổi lần nữa
  thì **phải tính lại cả 4**. Tôi đã ghi định nghĩa ở §4.2 để lần sau không phải hỏi.
- **`ends_clean` True rỗng** là **giả thuyết của tôi** về nguyên nhân — tôi **chưa đọc code** của họ
  ở dòng đó. Nếu code có kiểm `len(insns) > 0` mà vẫn True thì nguyên nhân khác, và **cờ 4 của tôi
  mới là thứ bắt được**, không phải sửa cờ của họ.
- **21 commit mới có 9 commit `chore(re) [skip ci]`** (43 %) sinh file trong `raw/ui/` (6.722 file).
  Tôi **không** đọc khối đó trong vòng này; nếu `ui_text_keys` 2,0 MB → **2,98 MB** (+47 %) thì
  `UI.md`/`ECONOMY.md` có thể có chuỗi mới chưa dùng.
