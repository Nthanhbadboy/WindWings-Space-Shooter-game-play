# 144 — Khoá của store `PlayerPreferences`: 25 khoá literal, 11 tiền tố ghép index, 184 lời gọi

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY; giá trị trong store là trạng thái máy — `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_game_store_keys.json.gz` (4956 B, sha256 `75974f5a3313f47a66daccc3973f39b1038a211f0e750f3b04691315ec7324ad`)
**Báo cáo trước:** 143 (store thứ hai — báo cáo này thay heuristic "slot_ref gần nhất" bằng theo dõi thanh ghi), CM4 (`opening_persistence`: hai store), 142 (`Application` cell).
**Verifier:** `tools/verify/game_store_keys.py` · **Test:** `tests/test_game_store_keys.py` (32 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| Store thứ hai là gì? | `PlayerPreferences` — JSON-backed (`GetRawData` / `SaveToDisk` / `LoadFromDisk`) | §1 |
| Bao nhiêu lời gọi? | **184** (143 đếm 174 vì chỉ xét method có `slot_ref` string) | §2 |
| Phân loại khoá? | **115 literal · 43 computed · 26 unknown** | §2 |
| Bao nhiêu khoá literal? | **25** | §3 |
| Bao nhiêu tiền tố ghép index? | **11** + 1 `String.Concat` không có literal ở tham số đầu | §4 |
| Khoá nào 143 đã liệt kê? | cả **6** setter `GameDatas` xuất hiện đúng ở đây | §5 |
| Giá trị mặc định của `GetString`? | `FREE_VERSION` (22 lần) · `OFF` (1 lần) | §3 |
| 26 lời gọi "unknown"? | khoá đến từ **tham số** hoặc call khác — chưa đặt tên | §6 |

**Một câu:** store riêng của game có **25 khoá literal** đặt tên được, **11 tiền tố** ghép với index lúc chạy, và **26 lời gọi** mà khoá không phải literal — và cả ba nhóm chỉ tách ra được khi theo dõi thanh ghi từng method, vì heuristic "slot_ref gần nhất" của 143 chỉ chốt được 6/42.

---

## 1. Cách đọc

```text
adrp x8, #page            -> x8 = page
ldr  x8, [x8, #off]       -> x8 = ô string (cell = page+off)
ldr  x0, [x8]             -> x0 = literal; chữ lấy từ slot_ref.addend của cell
mov  x0, x8               -> sao chép role
bl   <String.Concat>      -> x0 = "computed", tiền tố = tham số literal đầu tiên
<call store>              -> đọc role của x0 (và x1) NGAY TRƯỚC khi gọi
```

Bất kỳ lệnh nào ghi vào thanh ghi mà bộ đọc không mô hình hoá đều **xoá** role — nên kết quả là **cận dưới** của những gì đọc được, không phải suy đoán.

10 API của store (RVA → tên): `SetValue` 20912164 · `GetValue` 20912432 · `SetInt` 20912644 · `SetFloat` 20912652 · `SetString` 20912660 · `GetInt` 20912668 · `GetFloat` 20912676 · `GetString` 20912684 · `DeleteAll` 20912692 · `DeleteKey` 20912964.

---

## 2. Census 184 lời gọi

| Theo API | | Theo raw | | Theo loại khoá | |
|---|---:|---|---:|---|---:|
| `SetInt` | 67 | `meta-rewards` | 80 | literal | **115** |
| `GetInt` | 58 | `key-grant` | 49 | computed | **43** |
| `SetString` | 32 | `arena-pvp` | 41 | unknown | **26** |
| `GetString` | 25 | `box-draw` | 10 | | |
| `DeleteKey` | 2 | `key-jump` | 4 | | |

**51** lời gọi là **tail call** (`b`) — cùng bẫy đã gặp ở 143 với `PlayerPrefs.SetInt`. `key-jump` (4 lời gọi) là raw mà 143 **không** thấy, vì mọi method ở đó không có `slot_ref` string nào; đây là chỗ 174 → 184.

---

## 3. 25 khoá literal

| Khoá | literal | lời gọi | API | mặc định |
|---|---:|---:|---|---|
| `VersionProfile` | 46044672 | 6 | `SetString` | — |
| `Local_Arena_Rank` | 46013520 | 4 | `GetInt`/`SetInt` | — |
| `FIRST_OPEN_ARENA` | 46000200 | 2 | `GetInt`/`SetInt` | — |
| `CountOpen` | 45993688 | 6 | `GetInt`/`SetInt` | — |
| `FirstGetPower` | 46001560 | 6 | `GetInt`/`SetInt` | — |
| `FIRST_OPEN_PVP` | 46000232 | 4 | `GetInt`/`SetInt` | — |
| `HunterSeasonProgress` | 46005248 | 4 | `GetInt`/`SetInt` | — |
| `HunterSeasonDies` | 46005240 | 4 | `GetInt`/`SetInt` | — |
| `IsFirstOpenQuest` | 46010056 | 4 | `GetInt`/`SetInt` | — |
| `TotalGemSpend` | 46039304 | 4 | `GetInt`/`SetInt` | — |
| `Compensation` | 45992328 | 4 | `GetInt`/`SetInt` | — |
| `PREMIUM_DAILY_COLLECTED` | 46021056 | 4 | `GetInt`/`SetInt` | — |
| `PRO_ExpiryDateTime` | 46021128 | 26 | `GetString`/`SetString` | **`FREE_VERSION`** |
| `CanCollectPremiumGift` | 45988904 | 4 | `GetInt`/`SetInt` | — |
| `IsPremiumTag` | 46010576 | 4 | `GetInt`/`SetInt` | — |
| `CountThroughAds` | 45993728 | 4 | `GetInt`/`SetInt` | — |
| `LastArenaPoints` | 46012552 | 4 | `GetInt`/`SetInt` | — |
| `TIME_EVENT_DOUBLE_ENDED` | 46031696 | 7 | `GetString`/`SetString` | `OFF` (1) |
| `IS_FIRST_TIME_EVENT` | 46006280 | 2 | `GetInt`/`SetInt` | — |
| `IsEventStarted` | 46010032 | 2 | `GetInt`/`SetInt` | — |
| `IS_BUY_EVENT_COMBO` | 46006264 | 2 | `GetInt`/`SetInt` | — |
| `TIME_VIDEO_ACTIVE` | 46031944 | 2 | **`DeleteKey`** | — |
| `VIDEO_CURRENT_INDEX` | 46044008 | 2 | `GetInt`/`SetInt` | — |
| `LUCKY_VALUE_4` | 46012416 | 2 | `GetInt`/`SetInt` | — |
| `LUCKY_VALUE_5` | 46012424 | 2 | `GetInt`/`SetInt` | — |

Hai ghi chú đọc được từ bảng:

* `VersionProfile` **chỉ được ghi** (6 lần `SetString`, 3 raw) — không có lần đọc nào trong 8 raw đã pin.
* `TIME_VIDEO_ACTIVE` chỉ xuất hiện trong 2 lời gọi **`DeleteKey`** (`ResetCheat` và `ResetDaily` của `Popup_WatchVideos`) — tức khoá này bị xoá chứ không đọc/ghi.
* `GetString` có đối số mặc định literal: **`FREE_VERSION` 22 lần**, **`OFF` 1 lần**.

---

## 4. 11 tiền tố ghép index (+1 ngoại lệ)

`String.Concat(<literal>, index)` — chữ của khoá chỉ hoàn chỉnh lúc chạy:

| Tiền tố | lời gọi |
|---|---:|
| `ARENA_SHOP_ITEM_ID` | 4 |
| `ARENA_SHOP_ITEM_STOCK` | 5 |
| `HunterCollectProgress` | 4 |
| `PVP_SHOP_ITEM_ID` | 4 |
| `PVP_SHOP_ITEM_STOCK` | 5 |
| `Quest_Value_Key` | 4 |
| `Quest_Collect_Index` | 4 |
| `Quest_Check_Collect_Index` | 4 |
| `STOCK_EXCHANGE_EVENT1_` | 2 |
| `FIRST_FREE_BOX` | 2 |
| `GET_VIDEO_DONE` | 2 |
| `GET_VIDEO_UNLOCK` | 2 |

Ngoài ra **1** lời gọi đi qua `String.Concat` nhưng tham số đầu **không** phải literal (ghi `prefix: null`) — không đặt tên được, đã tính trong nhóm computed.

---

## 5. Đối chiếu với 143

143 liệt kê 6 setter `GameDatas` **không** dùng `PlayerPrefs`; cả 6 xuất hiện đúng ở bảng §3 với khoá literal:

| Property (`GameDatas`) | Khoá ở store này |
|---|---|
| `Compensation` | `Compensation` |
| `IsCollectPremiumDailyGift` | `PREMIUM_DAILY_COLLECTED` |
| `CanCollectPremiumGift` | `CanCollectPremiumGift` |
| `IsPremiumTag` | `IsPremiumTag` |
| `CountThroughAds` | `CountThroughAds` |
| `LastArenaPoints` | `LastArenaPoints` |

Không có mâu thuẫn giữa hai báo cáo: 21 khoá của 143 là **Unity `PlayerPrefs`**, 25 khoá ở đây là **store riêng**, hai tập rời nhau.

---

## 6. `not_decoded` (3 mục)

| Mục | Bước chặn |
|---|---|
| **26** lời gọi khoá không phải literal/computed (ví dụ `key-jump.SetRewards`, `key-jump.RandomCards`) | khoá đến từ **tham số** hoặc từ một call khác trong method; đặt tên cần tập caller hoặc pass giá trị liên method |
| **index** của 43 khoá ghép | `String.Concat(prefix, index)` dựng khoá lúc chạy; index bị chặn bởi độ dài mảng shop/quest — việc của một decode khác |
| giá trị lưu trong store | trạng thái máy, không nằm trong APK — **`MODEL_NOT_MEASURED runtime`** |

---

## 7. Tái lập

```bash
python3 tools/verify/game_store_keys.py            # in bytes/sha256 + đếm literal/computed/unknown
python3 -m unittest tests.test_game_store_keys      # 32 test
python3 tools/verify-claims.py --require AB,AO,AP
```

`evidence: STATIC_ONLY_ORIGINAL_APK` · nguồn: 8 raw `reverse-engineering/raw/*/native.json.gz`,
`reverse-engineering/il2cpp/stringliteral.json` (chữ của 25 khoá + 11 tiền tố),
`reverse-engineering/il2cpp/dump.cs.gz` (10 RVA `PlayerPreferences` + 5 RVA `String.Concat`).

---

`provenance:` APK gốc `535b0541` → `libil2cpp.so` → 5 raw có lời gọi store (`meta-rewards` 80 · `key-grant` 49 · `arena-pvp` 41 · `box-draw` 10 · `key-jump` 4) → theo dõi thanh ghi → `slot_refs.addend` → `stringliteral.json` → artifact 4956 B `75974f5a…` → 32 test. Không emulator/probe/device.
