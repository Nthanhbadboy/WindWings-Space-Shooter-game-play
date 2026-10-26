# 145 — 26 lời gọi store "unknown" của 144: đóng hết, khoá đến từ method khác

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY; giá trị dưới các khoá là trạng thái máy — `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_store_key_callers.json.gz` (3719 B, sha256 `8759167e9268fdf28548aaab5bb2f3581296ebf9713b97c81c6afb476f3dd875`)
**Báo cáo trước:** 144 (census 184 lời gọi, 26 unknown), 143 (store `GameDatas`), 142 (`Application` cell).
**Verifier:** `tools/verify/store_key_callers.py` · **Test:** `tests/test_store_key_callers.py` (28 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| 26 lời gọi unknown của 144? | **đóng hết** — 0 còn lại | §2 |
| Chia theo cơ chế? | **8** bản ghi qua *return của helper* · **18** qua *static field* | §3, §4 |
| 22 vị trí gọi (26 bản ghi)? | 4 vị trí nằm ở 2 raw (`key-jump` + `meta-rewards`) nên đếm 8 | §3 |
| Khoá mới đặt tên? | **3** literal + **1** tiền tố: `TIME_EVENT_ENDED` · `TIME_EVENT_STARTED` · `TIME_EVENT_OPEN` · `SLOT_FREE_CARDS_` | §4, §5 |
| Census có đổi không? | **không** — vẫn 184 lời gọi, cùng 5 raw | §6 |
| Phân loại sau khi đọc lại? | literal **115 → 133** · computed **43 → 51** · unknown **26 → 0** | §6 |
| Khoá literal tổng cộng? | **25 → 28** | §5 |

**Một câu:** cả 26 lời gọi mà 144 để trống đều lấy khoá từ **ngoài method** — bốn lời gọi đi qua `TimeFreeRewardPack.Key(int slot)` trả về `String.Concat("SLOT_FREE_CARDS_", slot)`, mười tám lời gọi đọc ba `static string` của `Board_EventSeasonPass` mà `..cctor` ghi vào (một trong hai lệnh ghi là `stp` nên đọc từng thanh ghi một sẽ trượt).

---

## 1. Vì sao 144 dừng ở 26

Bộ đọc của 144 theo dõi thanh ghi **trong một method**: `adrp` → page, load từ page → ô string, load từ ô → literal, `mov` lan truyền, mọi lệnh ghi khác **xoá** role. Ba đường mà khoá đi ra khỏi method đó:

```text
(a) bl <helper>            -> x0 = ('ret', helper)      ; 144: unknown
(b) ldr x8,[cell]; ldr x8,[x8,#0xB8]; ldr x19,[x8,#off] ; 144: unknown
(c) str x19,[sp,#n] ... ldr x0,[sp,#n]                  ; 144: unknown
```

145 thêm đúng ba luật tương ứng: **giải return của callee** (đệ quy, sâu ≤ 3), **bảng static field** `(klass cell, offset) → literal` dựng từ mọi `str`/`stp` vào khối static, và **bảng slot stack**. Không có luật nào nới lỏng việc "lệnh ghi không mô hình hoá thì xoá role" — nên kết quả vẫn là cận dưới.

---

## 2. Kết quả

| # | Cơ chế | Bản ghi | Vị trí | Khoá / tiền tố | API |
|---|---|---|---|---|---|
| 1 | return của helper | 8 | 4 | `SLOT_FREE_CARDS_` (tiền tố) | `GetInt` 2 · `SetInt` 2 |
| 2 | static field | 18 | 18 | `TIME_EVENT_STARTED` 6 · `TIME_EVENT_ENDED` 9 · `TIME_EVENT_OPEN` 3 | `GetString` 11 · `SetString` 7 |

Bốn vị trí gọi helper nằm trong `TimeFreeRewardPack.SetRewards` (rva 19186068, hai lời gọi: 19186252 `GetInt`, 19186340 `SetInt`), `GetRewards` (19186908 → 19187188 `GetInt`), `RandomCards` (19187772 → 19187916 `SetInt`) — và cả bốn có mặt ở **hai raw** `key-jump-535b0541` và `meta-rewards-535b0541`, nên 4 vị trí ⇒ 8 bản ghi.

Mười tám vị trí còn lại đều thuộc một class: `Board_EventSeasonPass` (§4).

---

## 3. Cơ chế 1 — `TimeFreeRewardPack.Key(int slot)` trả về tiền tố + index

```text
0x124C8EC  public static string Key(int slot)          (rva 19187948)
  adrp x19,#0x2add000 ; ldr x19,[x19,#0x1c8]   -> ô 0x2ADD1C8 (44945864)
  ...
  str w0,[sp,#0xc]                             -> slot nằm trên stack
  add x0,sp,#0xc ; bl <int.ToString-like 0x2103338>
  ldr x8,[x19]                                 -> x8 = literal "SLOT_FREE_CARDS_"
  mov x0,x8 ; mov x1,x0_ToString ; bl <String.Concat 0x1FE4084 (33439876)>
  ret
```

* Ô `0x2ADD1C8` có `slot_ref.addend = 0x2BE4ED8` (**46026456**) → `stringliteral.json` cho `SLOT_FREE_CARDS_`. Đây chính là chỗ 143/144 không thấy: literal nằm **trong callee**, không nằm trong method gọi.
* Vì tham số thứ hai là `slot` (biến vòng lặp / chỉ số phần thưởng), bốn lời gọi này là **computed**, không phải literal: tiền tố biết, index thì không (§7).
* `SLOT_FREE_CARDS_` xuất hiện **8 lần** trong census — đúng bằng 4 vị trí × 2 raw.

---

## 4. Cơ chế 2 — ba `static string` của `Board_EventSeasonPass`

Đường đọc (ví dụ `IsOpen`, rva 19436984):

```text
ldr x8,[x21]              ; x21 = ô klass 0x2ADDDB8 (44948920)
ldr x8,[x8,#0xB8]         ; Il2CppClass::static_fields
ldr x19,[x8,#0x10]        ; static string tại offset 0x10
mov x0,x19 ; bl <PlayerPreferences.GetString>
```

Đường ghi là `..cctor` (rva **19462112**, `private static void .cctor()`, cùng ô klass 44948920):

| Khoá | Offset | Literal (addend) | Lệnh ghi | rva lệnh ghi | Số lời gọi | API |
|---|---|---|---|---|---|---|
| `TIME_EVENT_STARTED` | `0x10` (16) | 46031720 | `str` | 19464560 | 6 | `GetString` 4 · `SetString` 2 |
| `TIME_EVENT_ENDED` | `0x18` (24) | 46031704 | `stp` | 19464596 | 9 | `GetString` 6 · `SetString` 3 |
| `TIME_EVENT_OPEN` | `0x20` (32) | 46031712 | `stp` | 19464596 | 3 | `GetString` 1 · `SetString` 2 |

Điểm chết người của 144: hai khoá `ENDED`/`OPEN` được ghi bằng **một** lệnh `stp x11, x9, [x8, #0x18]` — đọc theo từng thanh ghi một thì chỉ thấy khoá đầu, và bản thân cặp đó còn bị luật "lệnh ghi lạ thì xoá role" nuốt mất. Bảng static dựng bằng cả `str` **và** `stp` nên đọc ra cả hai.

Người dùng ba khoá này (đúng như tên gọi — cửa sổ thời gian của event mùa):

| Khoá | Method tiêu thụ |
|---|---|
| `TIME_EVENT_STARTED` | `IsOpen` (19436984) · `OnEnable` (19444672) · `OnPurchased` (19457420) · `<IEUpdateEventTime>d__43.MoveNext` (19467084) |
| `TIME_EVENT_ENDED` | `IsOpen` · `GetTimeRemain` (19436420) · `IsDoubleTime` (19445996) · `OnPurchased` · `<IECheckDoubleCoins>d__..MoveNext` (19465676) · `<IEUpdateEventTime>d__43.MoveNext` |
| `TIME_EVENT_OPEN` | `IsOpen` (đọc + ghi) · `SetTimeOpen` (19438844, ghi) |

Cùng `..cctor` đó còn hai lệnh ghi static **không phải khoá** (`str x19,[x9]` ở static `+0` = một object, `str xzr,[x8,#0x28]` = null); chúng vẫn được ghi vào `statics` để bảng đầy đủ, không phải vì chúng là khoá.

---

## 5. Bộ khoá sau 145

* **Literal: 25 → 28.** Ba khoá mới là `TIME_EVENT_ENDED` (9 lời gọi), `TIME_EVENT_STARTED` (6), `TIME_EVENT_OPEN` (3). Hai mươi lăm khoá của 144 giữ nguyên số lời gọi.
* **Tiền tố: 11 → 12** (+1 `Concat` mà tham số đầu không phải literal): thêm `SLOT_FREE_CARDS_` với 8 lời gọi.
* `PRO_ExpiryDateTime` vẫn là khoá bị gọi nhiều nhất (**26**).

---

## 6. Đối chiếu với 144 — cùng census, chỉ đổi chỗ phân loại

| | 144 | 145 |
|---|---|---|
| Lời gọi | 184 | **184** |
| Theo raw | 80 / 49 / 41 / 10 / 4 | **y hệt** |
| Theo API | 67 / 58 / 32 / 25 / 2 | **y hệt** |
| Theo loại | literal 115 · computed 43 · unknown 26 | **literal 133 · computed 51 · unknown 0** |

26 bản ghi unknown chia đúng 18 literal + 8 computed; 115 + 18 = 133 và 43 + 8 = 51 — không có lời gọi nào bị đếm hai lần hay rơi ra ngoài. Verifier chạy lại toàn bộ census bằng bộ đọc mới, nên nếu một lời gọi từng là literal mà bộ đọc mới làm mất role thì bài test sẽ đỏ, không phải im lặng.

---

## 7. Chưa đọc được

| Mục | Bước chặn |
|---|---|
| **Nửa index của 51 khoá computed** | `String.Concat(<tiền tố>, index)` — index là biến vòng lặp hoặc vị trí trong mảng shop/quest, nên tập khoá khả dĩ cần **độ dài mảng** (decode khác). Ví dụ `SLOT_FREE_CARDS_` chạy theo `slot` của `TimeFreeRewardPack`. |
| **Giá trị dưới khoá** | trạng thái máy, không có trong APK — `MODEL_NOT_MEASURED runtime`. |
| **Hai static không phải khoá** | 44986264 `+0` (`Rank/PVP/`) và 44953992 `+0` (một chuỗi số dài) — đã ghi trong `statics`, chưa cần diễn giải. |

---

## 8. Chạy lại

```bash
python3 tools/verify/store_key_callers.py       # in bytes/sha + 184/22/133/51/0
python3 -m unittest tests.test_store_key_callers -q
```

Artifact dựng lại tất định (gzip `mtime=0`, `sort_keys=True`), nên sha256 trong bài test là pin cứng.

---

provenance: static-only decode of the original XAPK; sources and their sha256 are listed in `datas/l2_535b0541_store_key_callers.json.gz` §`provenance` (8 native raws + `stringliteral.json` + `dump.cs.gz` + the 144 artifact). RVAs are decimal. Nothing here was measured at runtime.
