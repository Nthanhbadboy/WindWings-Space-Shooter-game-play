# 146 — Nửa index của 51 khoá computed: dải 100/200/300, sentinel 999, và chỗ dừng

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY; index là giá trị lúc chạy, giá trị dưới khoá là trạng thái máy — `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_computed_key_index.json.gz` (4470 B, sha256 `d9ff7301848e8bb1a4ac23105973c0c13e18a99c111fe6ba79e9f6fdee4f43c6`)
**Báo cáo trước:** 145 (đóng 26 lời gọi unknown), 144 (census 184, 51 computed), 143 (store `GameDatas`).
**Verifier:** `tools/verify/computed_key_index.py` (~1,0 s) · **Test:** `tests/test_computed_key_index.py` (22 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| 51 lời gọi computed của 145 | **39 vị trí** (12 vị trí xuất hiện ở 2 raw: 4 `Key(slot)`, 2 hunter, 6 quest) | §1 |
| Index đến từ đâu? | **3 dạng + 1 ca đặc biệt**: dải `i + band` (12) · tham số `int index` (19) · return của helper (4) · static field (3) · field của struct (1) | §1 |
| Dải số nào? | **100 / 200 / 300**, giống nhau ở `Arena_Shop` và `PVP_Shop` | §2 |
| Cận của dải? | `cmp <counter>, <array length>` với độ dài đọc từ `[xObj, #0x18]` — **độ dài lúc chạy**, không phải hằng | §2 |
| Có index literal nào? | **999**, **20** vị trí gọi, chỉ ở hai họ `Quest_Value_Key` + `Quest_Collect_Index` | §4 |
| Bao nhiêu tiền tố enumerate được tĩnh? | **4 / 14** — chỉ 4 họ shop | §6 |
| Index của `SLOT_FREE_CARDS_`? | `slot` của `TimeFreeRewardPack.Key(int slot)`, 4 vị trí | §5 |

**Một câu:** nửa index **không** liệt kê được từ code — 12 vị trí là `i + {100,200,300}` với `i` chạy tới độ dài một mảng cấu hình, 19 vị trí là tham số do caller truyền, 4 vị trí là `slot` của helper; thứ duy nhất đóng được là **cấu trúc dải** và **sentinel 999**, phần còn lại cần dữ liệu cấu hình chứ không phải code.

---

## 1. Ba dạng index (39 vị trí)

```text
dạng A — dải:        add wR, wL, #band          ; wL là biến vòng lặp
                     cmp wL, wT                 ; wT = độ dài mảng
                     b.ge  ra ngoài
dạng B — tham số:    str w0, [sp, #0xc]         ; spill tham số ở prologue
                     add x0, sp, #0xc ; bl <int→string> ; bl <String.Concat>
dạng C — helper:     key = Key(slot)            ; cả chuỗi dựng trong callee
```

| Dạng | Vị trí | Ghi chú |
|---|---|---|
| `band` | **12** | 2 shop × 3 dải × 2 tiền tố (ID/STOCK) |
| `parameter` | **19** | mỗi method một vị trí; instance method nhận `int` ở **w1** |
| `helper` | **4** | `SetRewards` / `GetRewards` / `RandomCards` → `Key(int slot)` |
| `static-field` | **3** | `FIRST_FREE_BOX` ×2 + 1 khoá tiền tố `null`, index là `static int` |
| `field` (struct) | **1** | `Board_PVP.OnClickHunterCollect(WinPoint point)` — index nằm trong struct tham số |

---

## 2. Dải 100 / 200 / 300

| Shop | Dải | Tiền tố | Guard (rva) | Cận |
|---|---|---|---|---|
| `Arena_Shop.ResetShop` | 100 | `ARENA_SHOP_ITEM_ID` | 22729088 | `ldr w8, [x8, #0x18]` |
| `Arena_Shop.ResetShop` | 100 | `ARENA_SHOP_ITEM_STOCK` | 22729088 | `ldr w8, [x8, #0x18]` |
| `Arena_Shop.ResetShop` | 200 | `ARENA_SHOP_ITEM_ID` | 22729088 | `ldr w8, [x8, #0x18]` |
| `Arena_Shop.ResetShop` | 200 | `ARENA_SHOP_ITEM_STOCK` | 22729088 | `ldr w8, [x8, #0x18]` |
| `Arena_Shop.ResetShop` | 300 | `ARENA_SHOP_ITEM_ID` | 22728800 | `ldr w1, [x20, #0x18]` |
| `Arena_Shop.ResetShop` | 300 | `ARENA_SHOP_ITEM_STOCK` | 22728800 | `ldr w1, [x20, #0x18]` |
| `PVP_Shop.ResetShop` | 100 | `PVP_SHOP_ITEM_ID` | 19938144 | `ldr w8, [x8, #0x18]` |
| `PVP_Shop.ResetShop` | 100 | `PVP_SHOP_ITEM_STOCK` | 19938144 | `ldr w8, [x8, #0x18]` |
| `PVP_Shop.ResetShop` | 200 | `PVP_SHOP_ITEM_ID` | 19938144 | `ldr w8, [x8, #0x18]` |
| `PVP_Shop.ResetShop` | 200 | `PVP_SHOP_ITEM_STOCK` | 19938144 | `ldr w8, [x8, #0x18]` |
| `PVP_Shop.ResetShop` | 300 | `PVP_SHOP_ITEM_ID` | 19937856 | `ldr w1, [x20, #0x18]` |
| `PVP_Shop.ResetShop` | 300 | `PVP_SHOP_ITEM_STOCK` | 19937856 | `ldr w1, [x20, #0x18]` |

Đọc ra: khoá shop có dạng `ARENA_SHOP_ITEM_ID{100+i}`, `PVP_SHOP_ITEM_STOCK{200+i}`… — **dải là hằng số trong code**, còn `i` chạy tới `items.Length` của mảng shop (nạp từ object cấu hình tại `[x19, #0x68]` rồi `[.., #0x18]`). Dải 300 dùng **một mảng khác** (`[x20, #0x18]`) — đó là lý do guard của nó khác rva.

`Arena_Shop.InitShop` / `PVP_Shop.InitShop` gọi `GetStockItem`/`SetStockItem` với cùng công thức `band + counter`, nên nửa *đọc* và nửa *ghi* của cùng một khoá dùng chung dải.

---

## 3. Mười chín method nhận `int`

| Class | Method | Tiền tố | Tham số |
|---|---|---|---|
| `Arena_Shop` | `GetIdItem(int index)` | `ARENA_SHOP_ITEM_ID` | `w1` (instance → lệch 1 thanh ghi) |
| `Arena_Shop` | `GetStockItem(int index)` | `ARENA_SHOP_ITEM_STOCK` | `w0` |
| `Arena_Shop` | `SetStockItem(int index, int stock)` | `ARENA_SHOP_ITEM_STOCK` | `w1` |
| `PVP_Shop` | `GetIdItem(int index)` | `PVP_SHOP_ITEM_ID` | `w1` |
| `PVP_Shop` | `GetStockItem(int index)` | `PVP_SHOP_ITEM_STOCK` | `w0` |
| `PVP_Shop` | `SetStockItem(int index, int stock)` | `PVP_SHOP_ITEM_STOCK` | `w1` |
| `Board_PVP` | `IsCollected(int index)` | `HunterCollectProgress` | `w0` |
| `Board_Quest` | `GetQuestValue(int _indexQuest)` | `Quest_Value_Key` | `w0` |
| `Board_Quest` | `SetQuestValue(int _indexQuest, int _value)` | `Quest_Value_Key` | `w0` |
| `Board_Quest` | `GetQuestCollectIndex(int _indexQuest)` | `Quest_Collect_Index` | `w0` |
| `Board_Quest` | `SetQuestCollectIndex(int _indexQuest, int _value)` | `Quest_Collect_Index` | `w0` |
| `Board_Quest` | `GetQuestCheckCollectIndex(int _indexQuest)` | `Quest_Check_Collect_Index` | `w0` |
| `Board_Quest` | `SetQuestCheckCollectIndex(int _indexQuest, int _value)` | `Quest_Check_Collect_Index` | `w0` |
| `Board_EventSeasonPass` | `GetStock(int index)` | `STOCK_EXCHANGE_EVENT1_` | `w0` |
| `Board_EventSeasonPass` | `SetStock(int index, int stock)` | `STOCK_EXCHANGE_EVENT1_` | `w0` |
| `Popup_WatchVideos` | `IsVideoDone(int index)` | `GET_VIDEO_DONE` | `w0` |
| `Popup_WatchVideos` | `SetVideoDone(int index, bool done)` | `GET_VIDEO_DONE` | `w0` |
| `Popup_WatchVideos` | `IsVideoUnlock(int index)` | `GET_VIDEO_UNLOCK` | `w0` |
| `Popup_WatchVideos` | `SetVideoUnlock(int index, bool done)` | `GET_VIDEO_UNLOCK` | `w0` |

Caller của 19 method này (đo trên 8 raw): phần lớn truyền **thanh ghi** (id quest đọc từ field, biến vòng lặp, counter static) chứ không phải hằng — nên tập index không đóng được từ code.

---

## 4. Sentinel `999`

**20** vị trí gọi truyền **literal 999** làm index, chỉ ở hai họ:

| Tiền tố | Vị trí literal 999 |
|---|---|
| `Quest_Value_Key` | **16** (qua `GetQuestValue` 8 + `SetQuestValue` 8) |
| `Quest_Collect_Index` | **4** (qua `SetQuestCollectIndex`) |

Ví dụ: `Board_Quest.<AdsTimer>d__53.MoveNext` (rva lời gọi 19978424, 19978436) và `Board_Quest.OnQuestCollect` (19964728, 19964740). Nghĩa: ngoài quest id thật, store còn một **slot sentinel 999** — khoá `Quest_Value_Key999`, `Quest_Collect_Index999` tồn tại trong không gian khoá. Đây là index literal duy nhất tìm thấy trong toàn bộ 39 vị trí.

---

## 5. Bốn vị trí đi qua helper

`TimeFreeRewardPack.Key(int slot)` (rva 19187948) dựng khoá `SLOT_FREE_CARDS_<slot>`; index là **tham số `slot` của callee**, không phải của method gọi. 4 vị trí (× 2 raw = 8 bản ghi): `SetRewards` (19186252, 19186340), `GetRewards` (19187188), `RandomCards` (19187916). Cận của `slot`: caller truyền biến đếm phần thưởng — xem §7.

---

## 6. Ba vị trí index là `static int`, một là struct

* `Board_QuestRewards.SetButtonStates` (19985308) và `OnPressedButtonOpenFree` (19991964, khoá có tiền tố `null`) đọc index từ **static field** của một class (`ldr x0, [klass + 0xB8]`) rồi mới `ToString` — tức bộ đếm đã lưu, không phải hằng.
* `Board_PVP.OnClickHunterCollect(WinPoint point)` (19793316) nhận index trong **struct tham số** (`mov x20, x1`), tức chỉ số hunter gắn với điểm vừa bấm.

---

## 7. Kết luận: 4/14 tiền tố enumerate được

| Nhóm | Tiền tố | Trạng thái |
|---|---|---|
| Shop | `ARENA_SHOP_ITEM_ID`, `ARENA_SHOP_ITEM_STOCK`, `PVP_SHOP_ITEM_ID`, `PVP_SHOP_ITEM_STOCK` | **cấu trúc tĩnh**: 3 dải × `items.Length` |
| Còn lại | `HunterCollectProgress`, 3 họ `Quest_*`, `STOCK_EXCHANGE_EVENT1_`, `GET_VIDEO_DONE/UNLOCK`, `FIRST_FREE_BOX`, `SLOT_FREE_CARDS_`, `null` | **không enumerate tĩnh** — index do caller/dữ liệu quyết định |

Đây là câu trả lời đúng cho `not_decoded` #2 của 144: **không phải code thiếu**, mà index sống ở dữ liệu. Muốn biết tập khoá đầy đủ phải decode danh sách shop/quest/video (độ dài mảng + id), tức lớp dữ liệu serialized — không phải lớp code này.

---

## 8. Chưa đọc được

| Mục | Bước chặn |
|---|---|
| Cận trên của từng dải và từng danh sách | độ dài **lúc chạy**: `ldr wT, [xConfig, #0x18]` trên object cấu hình; nội dung mảng đến từ dữ liệu serialized ⇒ cần decode dữ liệu, không phải code |
| Giá trị index do caller truyền | caller truyền thanh ghi (id quest, biến vòng lặp, counter static); chỉ các vị trí literal là thấy được — **20** vị trí truyền `999` |
| Giá trị lưu dưới khoá | trạng thái máy — **`MODEL_NOT_MEASURED runtime`** |

---

## 9. Chạy lại

```bash
python3 tools/verify/computed_key_index.py     # in bytes/sha + 51/39/12/19/20/14
python3 -m unittest tests.test_computed_key_index -q
```

Artifact dựng lại tất định (gzip `mtime=0`, `sort_keys=True`) nên sha256 trong test là pin cứng.

---

provenance: static-only decode of the original XAPK; 10 sources with sha256 in `datas/l2_535b0541_computed_key_index.json.gz` §`provenance` (8 native raws + `stringliteral.json` + the 145 artifact). RVAs decimal. Index values are runtime state; nothing here was measured on a device.
