# 138 — `LoadRemoteConfigs` (PvP + Arena): đường dẫn remote, cổng `IsOpen`, callback — và một đính chính số La Mã

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY; giá trị server trả về là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_remote_configs.json.gz` (4240 B, sha256 `258f68c07024cae59eae0e64d1a13fde33d666d1f97217bfd0fa0b4ef51043f5`)
**Báo cáo trước:** 134 (`PVP_Manager` rules — nói `IsOpen` chỉ ghi trong `..cctor`), 136 (bản đồ statics — thấy `LoadRemoteConfigs` ghi `IsOpen`), 137 (bảng hiển thị hạng).
**Verifier:** `tools/verify/remote_configs.py` · **Test:** `tests/test_remote_configs.py` (25 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| Bảng PvP lấy cấu hình ở đâu? | `data-leagues/data-configs` | `get_pathOfDataConfigs` RVA 19915932 = `Concat('data-leagues', '/data-configs')` |
| Arena lấy ở đâu? | `arena---datas/is-open` | `Concat(get_pathRoot(), '/is-open')`, literal `/is-open` |
| Giá trị remote là gì? | PvP: **object JSON**; Arena: **một số nguyên** | `JsonParse.FromJson<object>` / `Int32.Parse` |
| Cổng mở bảng tính sao? | PvP: `IsOpen = config[+0x10]`; Arena: `IsOpen = count > 0` | `strb w20` / `cmp w20,#0` + `cset w9, gt` |
| Mất mạng thì sao? | **đóng bảng**, log `No network connected`, callback `false` | literal + `strb wzr` + `br x3` với `w1 = wzr` |
| Callback gọi mấy lần? | **đúng 1 lần** mỗi nhánh (đúng/sai), qua `br x3` | 4 chỗ `mov w1, #1` / `mov w1, wzr` + `br x3` |
| 134 nói "`IsOpen` chỉ ghi trong `..cctor`"? | **thiếu 3 chỗ**: parent ghi `false`, handler ghi giá trị remote, handler ghi `false` khi lỗi | §5 |
| 136/137 nói số hạng là số Ả Rập? | **sai**: đuôi `b` gọi `MyLibrary.ToRoman` ⇒ **số La Mã** | §6 |

**Một câu:** cả hai bảng (PvP và Arena) đều **fail-closed**: `IsOpen` bị đặt `false` ở **3–4 chỗ**, chỉ được bật khi snapshot remote parse được, và callback `Action<bool>` nhận `true` chỉ ở đúng một nhánh.

---

## 1. Method đã đọc

| Method | RVA | Size | Vai trò |
|---|---:|---:|---|
| `PVP_Manager.LoadRemoteConfigs(Action<bool>)` | 19916080 | 544 B | parent PvP |
| `PVP_Manager.<>c__DisplayClass29_0.<LoadRemoteConfigs>g__OnSaveDataLoaded(DataSnapshot)` | 19936584 | 260 B | handler PvP |
| `ArenaManager.LoadRemoteConfigs(Action<bool>)` | 22691808 | 548 B | parent Arena |
| `ArenaManager.<>c__DisplayClass44_0.<LoadRemoteConfigs>g__OnListCountLoaded(DataSnapshot)` | 22705216 | 244 B | handler Arena |
| `ArenaManager.get_pathRoot()` | 22685676 | 204 B | gốc đường dẫn Arena |

Nguồn: `reverse-engineering/raw/arena-pvp-535b0541/native.json.gz`; mọi `bl`/`b` đều được đối chiếu chữ ký trong `dump.cs` nên tên hàm dưới đây **không phải suy đoán**.

---

## 2. Bảng đường dẫn

| Getter | RVA | Giá trị |
|---|---:|---|
| `PVP_Manager.get_pathRoot` | 19859292 | `data-leagues` |
| `get_pathOfDataConfigs` | 19915932 | `data-leagues/data-configs` |
| `get_pathOfDataRanks` | 19874728 | `data-leagues/data-ranks` |
| `get_pathOfDataUsers` | 19887544 | `data-leagues/data-users` |
| `get_pathOfDataPlayOfUsers` | 19915052 | `data-leagues/data-play/data-play-users` |
| `get_pathOfDataPlayOfMachines` | 19915784 | `data-leagues/data-play/data-play-machines` |

`ArenaManager.get_pathRoot` (RVA 22685676) **có điều kiện**, ba nhánh:

```text
companyName == "Test"   -> static string slot 0x2AEC9A0   (chuỗi chưa đọc được)
PREMIUM                 -> static string slot 0x2AEC9B0   (chuỗi chưa đọc được)
còn lại                 -> "arena---datas"                (slot 0x2AEC9A8)
```

Kiểm: `Application.get_companyName` (41274380) → `string.op_Equality` (33475124) → `tbz`; nhánh còn lại gọi `get_PREMIUM` (20068044) rồi `csel` giữa hai slot. Hai slot `0x2AEC9A0` / `0x2AEC9B0` **không** bị `ldr x0,[x8]` ở bất kỳ raw đã pin nào ⇒ không có `addend` ⇒ không có chữ (§7).

---

## 3. `PVP_Manager` — chuỗi đọc cấu hình

```text
NetworkReachability.get_internetReachability()  19916288   -> cbz w0 (0 = NotReachable) => nhánh lỗi
Object.op_Implicit(<static field +0 của class 0x2ADB958>)   19916348  -> tbz (không tồn tại) => nhánh lỗi
get_pathOfDataConfigs()                          19916392   -> "data-leagues/data-configs"
Action<object>..ctor(displayClass)               19916444
DownloadDatabase(path, onComplete)               19916480   (tail `b`)
```

Handler `OnSaveDataLoaded` (19936584):

```text
DataSnapshot.get_Value()        19936664   -> null => nhánh lỗi
GetRawJsonValue()               19936680
JsonParse.FromJson<object>(...) 19936696
ldrb w20, [obj, #0x10]          19936712   -> bool của object cấu hình
strb w20, [statics, #0x4C]      19936736   -> PVP_Manager.IsOpen = bool đó
mov  w1, #1 ; br x3             19936760   -> callback(true)
```

Nhánh lỗi: `Log("No network connected")` → `strb wzr,[statics,#0x4C]` → `callback(false)`.

---

## 4. `ArenaManager` — chuỗi đọc cấu hình

```text
get_internetReachability()                      22692028   -> cbz w0 => nhánh lỗi
Object.op_Implicit(...)                         22692088   -> tbz => nhánh lỗi
String.Concat(get_pathRoot(), "/is-open")       22692120/22692140
DownloadDatabase(path, onComplete)              22692236   (tail `b`)
```

Handler `OnListCountLoaded` (22705216):

```text
get_Value() / GetRawJsonValue()      22705284 / 22705300
Int32.Parse(raw)                     22705308   -> w20 = số nguyên
cmp w20, #0 ; cset w9, gt            22705344/22705348
strb w9, [statics, #0x1C]            22705352   -> ArenaManager.<cổng> = count > 0
mov  w1, #1 ; br x3                  22705376   -> callback(true)
```

Nhánh lỗi: `Log("No network connected")` (22692256) → `strb wzr,[statics,#0x1C]` → `callback(false)`.

Nghĩa là `/is-open` **không phải boolean**: nó là **số lượng** (danh sách mùa/giải đang mở), và bảng mở khi `count > 0`. Đây là điểm dễ đọc sai nhất nếu chỉ nhìn tên khoá.

---

## 5. Cổng fail-closed — số chỗ ghi

| Lớp | Field | Offset | Các chỗ ghi (RVA) |
|---|---|---:|---|
| `PVP_Manager` | `IsOpen` | `0x4C` (76) | `..cctor` 19936560 `wzr`; parent 19916560 `wzr`; handler 19936736 = bool cấu hình; handler 19936792 `wzr` (lỗi) |
| `ArenaManager` | `<cổng>` | `0x1C` (28) | parent 22692292 `wzr`; handler 22705352 `count > 0`; handler 22705408 `wzr` (lỗi) |

134 chỉ thấy dòng đầu ⇒ **đính chính**: `IsOpen` **không** phải "giá trị khởi tạo", nó là cổng được **đặt lại về false** ở mỗi lần load và mỗi lần lỗi. 136 đã nêu 1 chỗ; báo cáo này liệt kê đủ.

---

## 6. Đính chính 136 / 137 — số hạng là **số La Mã**

Khi đối chiếu chữ ký các đích `bl`/`b` của chuỗi remote, cùng bộ tra `dump.cs` cho ra:

| RVA | Chữ ký |
|---:|---|
| 21103836 | `public static string ToRoman(int number) { }` — class `MyLibrary : MonoBehaviour` (TypeDefIndex 1433) |

`GetRankNumber` (136 §4) kết thúc bằng `sub w0, w8, w19` rồi **`b #0x14204DC`** — tức `b` tới **21103836** = `MyLibrary.ToRoman`, **không** phải `Int32.ToString`. Vậy chuỗi trả về là **số La Mã**:

- 136 ghi `returns = "Int32.ToString(cells - level)"` → **sai tên đích**, đúng phần `cells - level`.
- 137 in bảng hiển thị `Herald 3 … God 5` → **phải đọc là** `Herald III … God V`.

Bản thân **bảng ký tự** của `ToRoman` vẫn `not_decoded`: thân method này không nằm trong raw đã pin (chỉ có chữ ký). Với `n ≤ 5` dạng La Mã thông dụng là `I, II, III, IV, V`, nhưng đó là **quy ước**, không phải số đo — nên không đưa vào artifact dưới dạng "đã đo".

Không sửa artifact 136 / 137 (đã handoff); đính chính nằm ở đây.

---

## 7. `not_decoded` (4 mục)

| Mục | Bước chặn |
|---|---|
| Hai biến thể gốc Arena | slot `0x2AEC9A0` (khi `companyName == "Test"`) và `0x2AEC9B0` (khi `PREMIUM`) không bị deref ở raw nào đã pin ⇒ không có `addend` ⇒ không có chữ |
| Class của object cấu hình PvP | `JsonParse.FromJson<object>` lấy type ở metadata slot `0x2AE1000`, không phải literal kind-5 ⇒ field `+0x10` chỉ được gọi bằng offset, chưa có tên |
| Class sở hữu static field `+0` đọc trước khi fetch | cả hai parent đọc `field +0` của class sau slot `0x2ADB958` và kiểm bằng `Object.op_Implicit`; class này chưa được định danh bằng symbol đã pin |
| Giá trị server | `data-leagues/data-configs` và `arena---datas/is-open` nằm trong Firebase, không nằm trong APK — **`MODEL_NOT_MEASURED runtime`** |

---

## 8. Tái lập

```bash
python3 tools/verify/remote_configs.py         # in bytes/sha256 + số getter/parent/handler/witness
python3 -m unittest tests.test_remote_configs   # 25 test
python3 tools/verify-claims.py --require AB,AO,AP
```

Mỗi khẳng định ở trên gắn với một **witness instruction** được assert nguyên văn (38 witness trên 5 method) — đổi byte là hỏng build, không chỉ hỏng văn xuôi.

`evidence: STATIC_ONLY_ORIGINAL_APK` · nguồn: `arena-pvp-535b0541/native.json.gz`,
`reverse-engineering/il2cpp/stringliteral.json`, `reverse-engineering/il2cpp/dump.cs.gz`.

---

`provenance:` APK gốc `535b0541` → `libil2cpp.so` → raw `arena-pvp-535b0541` (5 method) → `stringliteral.json` (đường dẫn + câu log) → `dump.cs` (chữ ký mọi callee) → verifier → artifact 4240 B `258f68c0…` → 25 test. Không emulator/probe/device.
