# 150 — Ô metadata chưa có tên: hai luật, một ô được đặt tên, và một nhánh thứ ba bị bỏ sót

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + dump/metadata đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Mọi giá trị ở đây là hằng lúc build; hành vi trên máy vẫn `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_cell_identity.json.gz` (8053 B, sha256 `23be51eba7d4cc82e597788341eb51f8d63784ab2091c51f9e352318192c2e5b`)
**Báo cáo trước:** 149 (ô `0x2ADF238`), 138 (ba ô Firestore + nhánh `get_pathRoot`), 142 (ô `0x2ADB8E0`).
**Verifier:** `tools/verify/cell_identity.py` (~2,0 s) · **Test:** `tests/test_cell_identity.py` (27 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| Ô `0x2ADF238` (149 để mở) là gì? | **`Board_PVP`** — ô đó chính là type usage của `Board_PVP` | §2 |
| Vì sao chắc? | nó được dùng **trong `Board_PVP..cctor`** để ghi statics, và ba lệnh ghi phủ đúng **layout static duy nhất** của `Board_PVP` trong 1086 class | §2 |
| `.cctor` đó còn nói gì? | literal `010000000f000000` → `backBoard = BoardHome (1)`, `costEnergy = 15` | §3 |
| `get_pathRoot` có mấy nhánh? | **3**, không phải 2 — nhánh thứ ba trả literal **`arena---datas`** | §4 |
| Loại ô suy ra được không cần bảng usage? | **Có**: addend ∈ `stringliteral.json` ⇒ string-literal; ngược lại ⇒ type | §5 |
| Ô nào vẫn chưa có tên? | `0x2ADB958` (type index **25385**) · `0x2AE1000` (**method-ref** 121683) · `0x2AEC9A0` / `0x2AEC9B0` (không có addend) | §6 |
| Có gì mới về cấu trúc chung? | **1076/1076** ô trong 8 raw mang **đúng một** cặp token `(kind, index)` | §6 |

**Một câu:** hai luật rẻ tiền — phân loại ô theo addend, và đặt tên ô bằng chính `..cctor` của class cộng với tính duy nhất của layout static — đã đóng được ô mà 149 bỏ mở, và lôi ra một nhánh thứ ba trong `get_pathRoot` mà 138 chưa từng liệt kê.

---

## 1. Vì sao cần báo cáo này

Ba báo cáo (138, 142, 149) dừng ở cùng một bức tường: một ô trong bảng metadata mà `slot_refs` không nói ra class hay chuỗi. Nhưng "không đọc được từ `slot_refs`" không có nghĩa "không đọc được": `slot_refs` chỉ ghi *addend*, còn ngữ nghĩa nằm ở **chỗ ô được dùng**. Báo cáo này thay vì thế bằng hai luật kiểm được, rồi áp cho cả 8 ô mà lane để mở.

---

## 2. Luật C — đặt tên ô bằng chính `..cctor` của class

Một class khởi tạo static của chính nó trong `..cctor` của nó, và nó chạm tới vùng static **qua type usage của chính nó**. Nên nếu ô `C` được load trong `K..cctor` và các lệnh `str` sau đó (qua con trỏ statics `+0xB8`) rơi đúng vào các field static mà `dump.cs` khai báo cho `K`, thì `C` là type usage của `K` — với điều kiện layout đó **duy nhất** trong dump.

`Board_PVP..cctor` (rva **19796920**, 88 B, 22 lệnh):

| rva | lệnh | nghĩa |
|---|---|---|
| 19796940 | `ldr x20, [x20, #0x238]` | load ô `0x2ADF238` |
| 19796984 | `ldr x8, [x8, #0xb8]` | con trỏ statics |
| 19796988 | `str d0, [x8]` | 8 byte tại `+0x0` — từ literal `0x757FE8` |
| 19796992 | `str xzr, [x8, #0x10]` | 8 byte tại `+0x10` |
| 19796996 | `str wzr, [x8, #0x18]` | 4 byte tại `+0x18` |

Layout static `Board_PVP` (dump.cs): `+0x0 BoardID backBoard` · `+0x4 int costEnergy` · `+0x8 string roomId` · `+0x10 int betCoinValues` · `+0x14 int betGemValues` · `+0x18 int betMedalValues`.

Phủ khớp từng byte: `+0x0..0x7` (hai field đầu, một lệnh 8 byte), `+0x10..0x17` (hai field bet), `+0x18..0x1b`. Field duy nhất không được ghi là `+0x8` — kiểu `string`, mặc định `null`, đúng như mong đợi.

**Kiểm duy nhất:** trong **1086** class parse được từ `dump.cs`, chỉ **một** class có đúng layout `{0x0:BoardID, 0x4:int, 0x8:string, 0x10:int, 0x14:int, 0x18:int}` — `Board_PVP`. (13 class có ba `int` tại `0x10/0x14/0x18`, nhưng không class nào trong số đó khớp cả sáu field.)

**Kiểm thứ hai (độc lập-ish):** cùng ô đó là nơi ba handler cược ghi giá trị đã chọn — `OnChangeCoins` → `+0x10`, `OnChangeGems` → `+0x14`, `OnChangeMedals` → `+0x18` — và `PVP_Endgame.AddBetValues(int rankMine)` cũng đi qua ô này. Bốn method, ba offset, một ô: khớp với ba field `bet*` của `Board_PVP`.

→ **Đóng mục 3 của 149.**

---

## 3. Bonus từ cùng `.cctor`: mặc định của bàn PvP

Literal 8 byte mà `Board_PVP..cctor` dùng là `010000000f000000` (va `7700456`), và lệnh `str d0, [x8]` ghi nó vào `+0x0` — tức hai field đầu:

| Offset | Field | Kiểu | Giá trị |
|---|---|---|---|
| `+0x0` | `backBoard` | `BoardID` | **1** = `BoardHome` (`public const BoardID BoardHome = 1;`) |
| `+0x4` | `costEnergy` | `int` | **15** |

---

## 4. `ArenaManager.get_pathRoot` có **ba** nhánh, không phải hai

138 viết: *"`get_pathRoot` trả slot `0x2AEC9A0` khi `companyName == "Test"` và slot `0x2AEC9B0` khi PREMIUM"*. Đọc đủ 204 byte của method (rva 22685676):

```text
if (Application.companyName == "Test")        // 41274380 = Application.get_companyName
                                              // 33475124 = String.op_Equality
                                              // "Test" = literal 46033008, ô 0x2ADF3E0
        return <cell 0x2AEC9A0>;              // Test root
if (VersionControlSystem.PREMIUM)             // 20068044 = VersionControlSystem.get_PREMIUM
        return <cell 0x2AEC9B0>;              // PREMIUM root
return "arena---datas";                       // literal 46051720, ô 0x2AEC9A8
```

Ba điểm mới:

1. **Nhánh thứ ba tồn tại** và trả literal **`arena---datas`** — chuỗi mà 138 gặp lại ở dạng đường dẫn `arena---datas/is-open` nhưng chưa nối vào `get_pathRoot`. Ô của nó là `0x2AEC9A8`, chưa từng được liệt kê.
2. **Vị từ PREMIUM là `VersionControlSystem.get_PREMIUM`**, không phải field nào của `ArenaManager`. Tên gọi lấy trực tiếp từ `dump.cs` theo RVA, không cần raw.
3. **Ô `0x2ADB8E0` xuất hiện ngay trong method này** và method gọi `Application.get_companyName` ngay sau khi init ô đó → xác nhận độc lập cho 142 (ô đó là `UnityEngine.Application`).

Lưu ý ghi trong artifact: addend `46051720` được gắn vào lệnh `ldr x0,[x8]` tại 22685864 — lệnh dùng chung sau `csel`, nên việc gán literal cho ô `0x2AEC9A8` theo `slot_refs` là **cách gán của extractor**, không phải suy luận của báo cáo này; csel chọn `x9` (`0x2AEC9B0`) khi PREMIUM và `x8` (`0x2AEC9A8`) khi không.

---

## 5. Luật K — loại ô suy từ addend

| Addend | Có trong `stringliteral.json`? | Kết luận |
|---|---|---|
| `46033008` | có → `"Test"` | string-literal |
| `46051720` | có → `"arena---datas"` | string-literal |
| `45764056` (`0x2ADB8E0`) | không | type usage — khớp 142 (`Application`) |
| `45765696` (`0x2ADF238`) | không | type usage — khớp §2 (`Board_PVP`) |
| `45771320` (`0x2ADB958`) | không | type usage |
| `45900224` (`0x2AE1000`) | không | **không phải type** — xem §6 |

Luật này có 4 ca đối chứng (hai ô đã biết tên, hai literal đọc được); nó không phải giả thuyết.

---

## 6. Ô vẫn chưa có tên, và phần thiếu chính xác là gì

Mỗi ô trong 8 raw mang **đúng một** cặp token `(kind, index)` — **1076/1076** ô nhất quán — nên danh tính của ô được xác định rõ; chỉ thiếu **bảng index → tên**.

| Ô | Token | Nghĩa | Chặn ở đâu |
|---|---|---|---|
| `0x2ADB958` | kind 1 (type), index **25385** | một class, đọc field `+0` rồi test bằng `Object.op_Implicit` | luật C không áp được (không `..cctor` nào đã pin load ô này); cần bảng type-index → tên |
| `0x2AE1000` | kind 6 (**method-ref**), index **121683** | **không phải type** — generic instantiation của `JsonParse.FromJson<T>` | 138 gọi đây là "type argument"; thực ra nó là method-ref, nên cần bảng method-ref, không phải bảng type |
| `0x2AEC9A0` | — (không có `slot_ref`) | Test root | extractor chỉ ghi 3/5 lần load của method; hai ô này không có addend nên **chưa biết cả loại** |
| `0x2AEC9B0` | — | PREMIUM root | như trên |

---

## 7. Đính chính & xác nhận

| Loại | Đích | Nội dung |
|---|---|---|
| **Đính chính** | 138 | `get_pathRoot` có **3** nhánh; nhánh thứ ba trả `arena---datas`; vị từ PREMIUM là `VersionControlSystem.get_PREMIUM` |
| **Đính chính** | 149 | ô `0x2ADF238` = `Board_PVP`; ba offset `+0x10/+0x14/+0x18` là `betCoinValues/betGemValues/betMedalValues` |
| **Đính chính (nhẹ)** | 138 | `0x2AE1000` là **method-ref**, không phải type argument dạng type |
| **Xác nhận** | 142 | ô `0x2ADB8E0` = `UnityEngine.Application`, nay từ một method thứ hai |
| **Xác nhận** | 138 | `arena---datas` là database root thật — nó là nhánh fallback của `get_pathRoot` |

---

## 8. Còn mở

| Mục | Bước chặn |
|---|---|
| Test root (`0x2AEC9A0`) và PREMIUM root (`0x2AEC9B0`) | hai ô string nhưng extractor không ghi addend cho hai lần load đó (3/5 lần load của method được ghi) ⇒ cần bảng metadata usage, repo không có |
| class sau `0x2ADB958` | type index 25385 đã biết, thiếu bảng index→tên; luật C không áp (không `..cctor` nào đã pin) |
| generic argument sau `0x2AE1000` | method-ref 121683; cần bảng method-ref |
| giá trị trên máy | `MODEL_NOT_MEASURED runtime` |

Ba mục đầu đều có dạng "một con số đã biết, một bảng còn thiếu" — không phải "chưa tìm ra".

---

## 9. Chạy lại

```bash
python3 tools/verify/cell_identity.py      # in bytes/sha + 8 ô + 13/13 check + totals
python3 -m unittest tests.test_cell_identity -q
```

Artifact dựng lại tất định (gzip `mtime=0`, `sort_keys=True`, `separators=(',',':')`).

---

provenance: static-only decode of the original XAPK; 4 sources with sha256 in `datas/l2_535b0541_cell_identity.json.gz` §`provenance` (`key-grant` raw, `arena-pvp` raw, `stringliteral.json`, `dump.cs.gz`) plus the token census over all 8 pinned raws. No emulator, no probe, no device. RVAs decimal. Runtime behaviour of these roots stays `MODEL_NOT_MEASURED runtime`.
