# 139 — `ArenaManager` statics: mặc định trong `..cctor`, bảng thưởng 10 hạng, cầu `ArenaConfig` → `ArenaManager` (+ đính chính 138)

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY; giá trị cấu hình do server trả về là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_arena_statics.json.gz` (3336 B, sha256 `261eca3a7268b5450fed691b224edaf09979a1ff9ca8662fd9ab68f48399a4b5`)
**Báo cáo trước:** 127 (§Arena, để ngỏ `SeasonTimes`/`RankUpIndexs`/`RankDropIndexs` và quà medal), 134 (`PVP_Manager` rules), 138 (cổng `IsOpen` — báo cáo này **đính chính** class sở hữu).
**Verifier:** `tools/verify/arena_statics.py` · **Test:** `tests/test_arena_statics.py` (29 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| `ArenaManager` có bao nhiêu static? | **9** field, `0x0 … 0x38` | `dump.cs` (TypeDefIndex 401) + `..cctor` ghi đủ 9 |
| Giá trị mặc định? | `IsOpen=false`, `MaxRoomCount=50`, `MinUserCount=25`, `SeasonSummaryTime=60.0`, `SeasonTimes=null`, `RankMapsIndex=0`, `RankUpIndexs=null`, `RankDropIndexs=null`, `rewards=string[10]` | RVA 22692372, 516 B |
| Hai int `50/25` nằm ở đâu? | **một** literal 8 byte `3200000019000000` (VA 7699216) | nếu đọc như `double` sẽ ra `5.3e-313` |
| `SeasonSummaryTime`? | **60.0** (`0x404E000000000000`) | `movz` ngay trong `..cctor` |
| `rewards` là gì? | **bảng thưởng 10 hạng × 6 khung xếp hạng**, đơn vị `Medal`/`Gems` | 10 literal chuỗi, đọc nguyên văn §3 |
| Ai đọc bảng đó? | chưa thấy trong raw này | §6 `not_decoded` |
| Ai ghi `SeasonTimes`/`RankUpIndexs`/`RankDropIndexs`? | **`Board_Arena.GetConfigs`** (RVA 22782048) parse từ 2 chuỗi remote | §4 — xác nhận điều 127 để ngỏ |
| Cổng `+0x1C` ở 138 là của ai? | **`ArenaConfig.IsOpen`**, không phải `ArenaManager` | §5 — **đính chính 138** |

**Một câu:** `ArenaManager` có **đúng 9** static, `..cctor` điền hết, và trong đó `rewards` là **bảng quà Arena đọc được nguyên văn** (10 hạng, 6 khung); phần "động" (`SeasonTimes`, `RankUpIndexs`, `RankDropIndexs`) thì `..cctor` để `null` và `Board_Arena.GetConfigs` mới là chỗ nạp từ chuỗi remote.

---

## 1. Bố cục static (đo từ `dump.cs`, khớp từng offset với `..cctor`)

| Offset | Field | Kiểu | Ghi bởi |
|---:|---|---|---|
| `0x00` | `IsOpen` | `bool` | `..cctor` (**chỉ** ở đây) |
| `0x04` | `MaxRoomCount` | `int` | `..cctor` → `GetConfigs` |
| `0x08` | `MinUserCount` | `int` | `..cctor` → `GetConfigs` |
| `0x10` | `SeasonSummaryTime` | `double` | `..cctor` → `GetConfigs` |
| `0x18` | `SeasonTimes` | `int[]` | `..cctor` (null) → `GetConfigs` |
| `0x20` | `RankMapsIndex` | `int` | `..cctor` |
| `0x28` | `RankUpIndexs` | `int[]` | `..cctor` (null) → `GetConfigs` |
| `0x30` | `RankDropIndexs` | `int[]` | `..cctor` (null) → `GetConfigs` |
| `0x38` | `rewards` | `string[]` | `..cctor` |

Metadata slot dẫn tới khối static này là **`0x2AE19D0` = 44964304**; bố cục 9 field khớp **chính xác** từng offset nên phép gán class ở đây không dựa vào tên.

---

## 2. `..cctor` (RVA 22692372, 516 B) — 9 phép ghi

```asm
22692584  strb wzr, [x8]                 ; IsOpen      (+0x00) = false
22692588  stur d0, [x8, #4]              ; MaxRoomCount(+0x04) = 50 , MinUserCount(+0x08) = 25
22692592  stp  x9, xzr, [x8, #0x10]      ; SeasonSummaryTime(+0x10) = 60.0 , SeasonTimes(+0x18) = null
22692596  str  wzr, [x8, #0x20]          ; RankMapsIndex(+0x20) = 0
22692600  stp  xzr, xzr, [x8, #0x28]     ; RankUpIndexs(+0x28) = null , RankDropIndexs(+0x30) = null
22692868  str  x0, [x8, #0x38]           ; rewards(+0x38) = string[10]
```

Ba chi tiết dễ đọc sai:

1. **`stur d0, [x8,#4]`** phủ **8 byte** = hai field `int`. Literal là `3200000019000000` (VA **7699216**): `0x32 = 50` ở `+4`, `0x19 = 25` ở `+8`. Đọc như `double` sẽ ra `5.3e-313` — vô nghĩa nhưng vẫn "một số", nên rất dễ lọt.
2. **`x9` không phải địa chỉ**: `mov x9, #0x404E000000000000` là **bit pattern** của `60.0` (double), không phải pointer. Verifier decode bằng `struct.unpack('<d', …)`, không suy từ ngữ nghĩa.
3. **`stp xzr, xzr`** để lại **hai** mảng `null` — nghĩa là `SeasonTimes`/`RankUpIndexs`/`RankDropIndexs` **không** có bảng shipped; nếu code đọc trước khi config tới thì gặp `null` (§4).

`rewards` được dựng bằng `newarr` (RVA 22692604, `mov w1,#0xa`) với element type lấy từ slot `0x2ADB7D0`, rồi **10** lệnh `str` ghi lần lượt 10 literal chuỗi vào `[x0,#0x20] … [x0,#0x68]`; phần tử là **literal string** nên mảng là `string[]`.

---

## 3. Bảng thưởng Arena — đọc nguyên văn từ 10 literal

Định dạng mỗi phần tử: `#<khung>[Medal:<m>,Gems:<g>]` nối bằng `';'`, đúng 6 khung: `#1`, `#2`, `#3-4`, `#5-10`, `#11-45`, `#46-50`.

| rank | #1 | #2 | #3-4 | #5-10 | #11-45 | #46-50 |
|---:|---|---|---|---|---|---|
| 0 | 680 / 250 | 460 / 180 | 320 / 120 | 200 / 80 | 120 / 50 | 60 / 20 |
| 1 | 800 / 300 | 540 / 220 | 380 / 150 | 240 / 100 | 140 / 60 | 70 / 20 |
| 2 | 1000 / 350 | 680 / 250 | 470 / 170 | 290 / 110 | 170 / 70 | 90 / 30 |
| 3 | 1250 / 400 | 850 / 290 | 490 / 190 | 370 / 130 | 220 / 80 | 110 / 30 |
| 4 | 1500 / 500 | 1010 / 360 | 700 / 240 | 440 / 160 | 260 / 100 | 130 / 40 |
| 5 | 2000 / 600 | 1350 / 430 | 940 / 290 | 590 / 190 | 350 / 120 | 180 / 50 |
| 6 | 2500 / 700 | 1690 / 500 | 1180 / 330 | 740 / 220 | 440 / 140 | 220 / 60 |
| 7 | 3000 / 800 | 2030 / 580 | 1410 / 390 | 880 / 260 | 530 / 160 | 270 / 60 |
| 8 | 4000 / 900 | 2710 / 650 | 1890 / 430 | 1180 / 290 | 710 / 180 | 360 / 70 |
| 9 | 5000 / 1000 | 3380 / 720 | 2350 / 480 | 1470 / 320 | 880 / 200 | 440 / 80 |

Kiểm trong verifier: mỗi phần tử **đúng 6** khung, nhãn khung **giống nhau** ở cả 10 phần tử, chuỗi dựng lại từ parse **bằng đúng** literal gốc, và cả `Medal` lẫn `Gems` **không giảm** khi rank tăng (10 giá trị/khung). Không có phép "nội suy" nào: bảng trên là nội dung literal.

---

## 4. Cầu `ArenaConfig` → `ArenaManager` (`Board_Arena.GetConfigs`, RVA 22782048, 800 B)

`ArenaConfig` (TypeDefIndex 402) là class **khác**, static:

| Offset | Field | Kiểu |
|---:|---|---|
| `0x00` | `RankSplit` | `string` |
| `0x08` | `SeasonTime` | `string` |
| `0x10` | `MaxRoomCount` | `int` |
| `0x14` | `MinRoomCount` | `int` |
| `0x18` | `SummaryTime` | `float` |
| `0x1C` | `IsOpen` | `bool` |

`GetConfigs` đọc `ArenaConfig` → ghi `ArenaManager`:

| Đọc (RVA) | Từ `ArenaConfig` | Ghi (RVA) | Sang `ArenaManager` |
|---:|---|---:|---|
| 22782184 | `MaxRoomCount` `+0x10` | 22782216 | `MaxRoomCount` `+0x04` |
| 22782220 | `MinRoomCount` `+0x14` | 22782224 | `MinUserCount` `+0x08` |
| 22782228 | `SummaryTime` `+0x18` (float) | 22782236 | `SeasonSummaryTime` `+0x10` (double, qua `fcvt d0, s0`) |
| 22782240 | `SeasonTime` `+0x08` (chuỗi) | 22782328 | `SeasonTimes` `+0x18` (`int[]`) |
| 22782480 | `RankSplit` `+0x00` (chuỗi) | 22782576 / 22782600 | `RankUpIndexs` `+0x28` / `RankDropIndexs` `+0x30` |

Chuỗi được xử lý theo đúng pipeline (mỗi bước có chữ ký `dump.cs`):

```text
SeasonTime : string.Replace('"' , null)  ->  Split(';')   -> Int32.Parse  -> SeasonTimes[i]
RankSplit  : string.Replace('"' , null)  ->  Split(';')   -> Split('-')
                                         -> Int32.Parse(tách trước) = RankUpIndexs[i]
                                         -> Int32.Parse(tách sau)  = RankDropIndexs[i]
```

Nghĩa là dữ liệu server phải có dạng **chuỗi có bọc nháy kép, phân tách bằng `;`**, và mỗi phần tử rank là cặp `lo-hi`. Verifier assert `Replace` chạy **trước** `Split` (nếu đảo thứ tự, nháy kép sẽ dính vào số và `Int32.Parse` ném lỗi). Đây là **hình dạng** dữ liệu, không phải giá trị — giá trị vẫn là runtime (§6).

---

## 5. Đính chính 138 — `+0x1C` là `ArenaConfig.IsOpen`

138 ghi cổng Arena là `ArenaManager` `+0x1C bool`. **Sai class**: `ArenaManager.IsOpen` ở **`+0x00`**, còn `+0x1C` là `ArenaConfig.IsOpen`.

Bằng chứng (ba lớp, cùng chỉ về một kết luận):

1. **Bố cục**: `ArenaConfig` khai đúng `bool IsOpen; // 0x1C`; `ArenaManager` khai `bool IsOpen; // 0x0` và **không** có field nào ở `+0x1C` (khoảng `0x18..0x1F` là `SeasonTimes`).
2. **Slot**: lệnh ghi `strb wzr, [x8, #0x1c]` trong `ArenaManager.LoadRemoteConfigs` đi qua metadata slot **`0x2AECA98`** — slot này được dùng bởi `ArenaConfig`, `Board_Arena` và `ArenaManager`, **không** phải slot `0x2AE19D0` của khối static `ArenaManager`.
3. **Ngữ nghĩa**: `GetConfigs` đọc `ArenaConfig` rồi mới đổ sang `ArenaManager`, tức hai class là hai tầng: `ArenaConfig` = cấu hình remote, `ArenaManager` = bản sao runtime cho phần còn lại của game.

Hệ quả: `ArenaManager.IsOpen` **chỉ** bị `..cctor` ghi (`false`) — nó **không** phải cổng remote; cổng remote là `ArenaConfig.IsOpen`. Ghi chú fail-closed của 138 (`LoadRemoteConfigs` đặt `false` mỗi lần load) vẫn đúng, nhưng **thuộc `ArenaConfig`**.

Nguyên nhân lọt: 138 theo dõi statics base bằng thanh ghi nhưng **không kiểm slot thuộc class nào**, nên một field `+0x1C` bị gán cho class chứa method. 136 đã mắc đúng lỗi này theo hướng ngược lại (bỏ sót vì không theo dõi thanh ghi); nay sửa bằng cách **luôn khoá theo slot**.

---

## 6. `not_decoded` (3 mục)

| Mục | Bước chặn |
|---|---|
| Giá trị cấu hình server | `SeasonTimes`, `RankUpIndexs`, `RankDropIndexs`, `MaxRoomCount`, `MinRoomCount`, `SeasonSummaryTime` sau khi `GetConfigs` chạy là dữ liệu Firebase — **`MODEL_NOT_MEASURED runtime`** |
| Ai đọc `rewards` `+0x38` | không method nào trong raw `arena-pvp` index `ArenaManager.rewards` sau khi khoá klass slot; consumer nằm ngoài raw hoặc đọc mảng qua slot khác |
| Bảng ký tự `MyLibrary.ToRoman` | RVA **21103836** không có trong **0/8** raw đã pin (đã quét toàn bộ `reverse-engineering/raw/*/native.json.gz`) ⇒ số La Mã mà `GetRankNumber` in ra (138 §6) vẫn chưa đo được |

---

## 7. Tái lập

```bash
python3 tools/verify/arena_statics.py            # in bytes/sha256 + số write/reward/band
python3 -m unittest tests.test_arena_statics      # 29 test
python3 tools/verify-claims.py --require AB,AO,AP
```

`evidence: STATIC_ONLY_ORIGINAL_APK` · nguồn: `arena-pvp-535b0541/native.json.gz`,
`reverse-engineering/il2cpp/stringliteral.json`, `reverse-engineering/il2cpp/dump.cs.gz`.

---

`provenance:` APK gốc `535b0541` → `libil2cpp.so` → raw `arena-pvp-535b0541` (`ArenaManager..cctor`, `Board_Arena.GetConfigs`) → `stringliteral.json` (10 chuỗi thưởng + ký tự nháy) → `dump.cs` (bố cục field + chữ ký callee) → verifier → artifact 3336 B `261eca3a…` → 29 test. Không emulator/probe/device.
