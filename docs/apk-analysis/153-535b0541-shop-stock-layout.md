# 153 — Hai cửa hàng Arena/PvP: khoá lưu, ba dải ô, và catalogue bốc ngẫu nhiên lúc reset

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + dump/metadata đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Khung cửa hàng (khoá, dải, offset, cách trả công) là hằng lúc build; **ô nào bán gì hôm nay** là `MODEL_NOT_MEASURED runtime` vì `Random.Range`.
**Artifact:** `datas/l2_535b0541_shop_stock_layout.json.gz` (4107 B, sha256 `792f25b76cc6aea9c8e29ded62a305227d320c05153f0cb731efdff8a29ce250`)
**Báo cáo trước:** 151 (`rewards` — chạm `Popup_ArenaShopExchange` để lấy `Length`), 149 (array của `Board_PVP..ctor`), 130/133 (thang thưởng hunter).
**Verifier:** `tools/verify/shop_stock_layout.py` (~5,7 s) · **Test:** `tests/test_shop_stock_layout.py` (33 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| `Arena_Shop` và `PVP_Shop` là hai implementation? | **Không** — cùng một class hai lần: **30/30 field trùng khít**, chỉ khác kiểu `popupExchange` | §2 |
| Cửa hàng lưu gì? | **hai khoá `PlayerPreferences`**: `<PREFIX>_ITEM_ID` và `<PREFIX>_ITEM_STOCK` | §3 |
| Có bao nhiêu ô? | **ba dải** `index + 100 / + 200 / + 300` → `listItemPlayers` / `listItemDrones` / `listItemResources`; `InitShop` cấp `int[5]` ba lần ⇒ **5 dòng mỗi dải** | §4 |
| Giá trị lưu là id thô? | **Không** — dải player lưu `id − 10001`, dải drone lưu `id`, dải resource lưu `300 + i` | §4 |
| Mua thì được gì? | đường mua **cộng lại 10001** rồi `GetPlayerCards/SetPlayerCards` ⇒ mua vật phẩm player = **cộng card** | §5 |
| Catalogue ở đâu? | **không ship** — `ResetShop` xáo `Player_Get_Datas.GetListAllIdPlayerActived()` bằng `Random.Range` + `RemoveAt` | §6 |
| Có gì bất thường? | `MaxStockCount` (+0x98) **bị đọc làm trần mua nhưng không chỗ nào ghi** trong 2499 method đã dump | §7 |

**Một câu:** cửa hàng PvP/Arena không có "bảng hàng" trong APK — nó chỉ ship **tên khoá, ba dải ô và một phép xáo**, còn bán gì là kết quả `Random.Range` trên chính danh sách vật phẩm người chơi đã mở.

---

## 1. Vì sao cần báo cáo này

Đề bài #29 ghi rõ ba mảng: luật trong trận, pool map, và **medal/shop exchange**. Hai cái đầu đã có báo cáo; cái thứ ba chưa ai mở — 151 chỉ chạm `Popup_ArenaShopExchange` để lấy `Length` của `rewards`, không đọc shop.

Spec lần 114 để AI-4 tự chọn follow-up, nên lượt này lấp đúng khoảng trống đó, trong giới hạn static.

---

## 2. Hai class sinh đôi

`Arena_Shop` (TypeDefIndex **418**) và `PVP_Shop` (**912**) khai báo **30 field trùng khít** về tên và offset:

| offset | field | | offset | field |
|---|---|---|---|---|
| +0x20 | `textMedal` | | +0x98 | `MaxStockCount` |
| +0x28 | `textTimeReset` | | +0x9C | `ItemPlayerValue` |
| +0x30…+0x48 | `parentPlayer` … `parentMedal` | | +0xA0 | `ItemPlayerCost` |
| +0x60 | `onExit` | | +0xA4/A8 | `ItemDroneValue` / `ItemDroneCost` |
| **+0x68** | `listItemPlayers` | | +0xB0/B8 | `ItemResourceValues` / `ItemResourceCost` |
| **+0x70** | `listItemDrones` | | +0xC0 | `popupExchange` |
| **+0x78** | `listItemResources` | | +0xF8 | `timeToReset` |

Chỉ **một** khác biệt về kiểu: `popupExchange` ở +0xC0 là `Popup_ArenaShopExchange` (Arena) và `Popup_PVPShopExchange` (PVP).

Về mã: `ResetShop` (1752 B), `InitShop` (1952 B), `GetIdItem` (164 B), `GetStockItem` (164 B), `SetStockItem` (168 B), `OnEnable` (540 B), `OnPressedButtonEsc` (156 B) **trùng kích thước từng byte**. Duy nhất `OnClickPlayerItem` lệch **4 byte** (Arena 1384, PVP 1380) — nhiều khả năng do nhánh `popupExchange` khác kiểu; báo cáo ghi nhận con số, không đoán nguyên nhân.

Hệ quả thực dụng: mọi kết luận dưới đây áp cho **cả hai** cửa hàng, chỉ đổi tiền tố khoá.

---

## 3. Cửa hàng lưu gì — hai khoá, không phải một bảng

Không có field nào trong class giữ id vật phẩm. Id đọc từ `PlayerPreferences`:

| class | khoá id | ô literal | khoá stock | ô literal |
|---|---|---|---|---|
| `PVP_Shop` | `PVP_SHOP_ITEM_ID` | `0x2AE1018` (44961816) | `PVP_SHOP_ITEM_STOCK` | `0x2AE0D40` (44961088) |
| `Arena_Shop` | `ARENA_SHOP_ITEM_ID` | `0x2AED090` (45011088) | `ARENA_SHOP_ITEM_STOCK` | `0x2AED088` (45011080) |

Ba method truy cập, đọc thẳng từ lệnh:

```
PVP_Shop.GetIdItem(int index)        rva 19941788
   Int32.ToString(index) -> String.Concat("PVP_SHOP_ITEM_ID", <số>)
   -> PlayerPreferences.GetInt(key, 0)                        ; mặc định 0
PVP_Shop.GetStockItem(int index)     rva 19889588   ; GetInt("PVP_SHOP_ITEM_STOCK", 0)
PVP_Shop.SetStockItem(int, int)      rva 19941952   ; SetInt("PVP_SHOP_ITEM_STOCK", stock)
```

Vì mặc định là **0**, một bản cài mới (trước lần `ResetShop` đầu tiên) có id ô = 0 cho mọi ô — tức "ô rỗng", không phải "ô bán vật phẩm 0".

Khoá là chuỗi literal ship sẵn, nên chúng cũng là **tên chính xác** để tra save trên thiết bị (`PlayerPreferences` = `PlayerPrefs`), hữu ích cho ai đối chiếu save thật sau này.

---

## 4. Ba dải ô và ba quy tắc giá trị

`ResetShop` ghi **sáu** lần `SetInt` cho mỗi cửa hàng: ba cho id, ba cho stock. Cả ba dải đều dựa trên một phép cộng hằng:

| dải | phép cộng | mảng đích (instance) | giá trị id | stock |
|---|---|---|---|---|
| 1 | `add w28, w22, #0x64` (index + **100**) | `listItemPlayers` (+0x68) | **`id − 10001`** | 0 |
| 2 | `add w27, w22, #0xc8` (index + **200**) | `listItemDrones` (+0x70) | `id` (nguyên) | 0 |
| 3 | `add w20, w9, #0x12c` (index + **300**) | `listItemResources` (+0x78) | **`300 + i`** | 0 |

Con số **10001** xuất hiện dưới dạng `mov w29, #-0x2711` (rva **19938136** ở PVP, **22729080** ở Arena) và được cộng vào id trước khi ghi. Dải 3 tự ghi chính khoá của nó làm giá trị (`value = 300 + i`) — nghĩa là tài nguyên không "tra id", chúng **được đánh số bằng đúng vị trí ô**.

Số ô: `InitShop` (rva **19939136**) gọi helper cấp phát ba lần (`mov w1, #5` @ 19939508 / 19940044 / 19940692 rồi `bl` cấp mảng), và class khai báo `Shop_Cell[]` cho cả ba dải + `int[]` cho value/cost ⇒ **5 dòng mỗi dải**. Số ô thực tế lúc chạy còn bị chặn bởi độ dài mảng `[SerializeField]` khai trong scene (`listItemPlayers.Length`), nên 5 là **trần do code**, không phải hằng số bán hàng.

---

## 5. Đường mua: cộng lại 10001, rồi trả bằng card

`PVP_Shop.<>c__DisplayClass31_1.<OnClickPlayerItem>g__OnBuy|2` (rva **19944488**):

```
19944896  ldr  w22, [x8, #0x1c]     ; giá trị ô đọc từ cell (đã trừ 10001)
19944916  mov  w8, #0x2711          ; 10001
19944920  add  w22, w22, w8         ; id thật = giá trị ô + 10001
19944932  bl   #0x14e7948           ; Player_Saved_Datas.GetPlayerCards(playerIndex)
19944944  madd w1, w8, w21, w0      ; card = perCopy * count + card hiện có
19944952  bl   #0x14e7a88           ; Player_Saved_Datas.SetPlayerCards(...)
```

Nên vòng đời một ô dải 1 là: `ResetShop` ghi `id − 10001` → UI đọc qua `GetIdItem` → mua thì `+10001` ra id thật → **cộng card** theo `perCopy × count`. Không có "số lượng vật phẩm trong kho" nào được tạo ở đây; thứ tăng là **card của player**.

Hai dải còn lại dùng cùng khung `OnBuy` (`|4` cho drone, `|6` cho resource) với các đích khác nhau — báo cáo chỉ khẳng định phần dải 1 vì đó là chỗ có chuỗi `+0x2711` kiểm được; hai dải kia không có hằng 10001 nên **không** suy rộng.

---

## 6. Catalogue: bốc ngẫu nhiên, không ship bảng hàng

`ResetShop` là một phép xáo:

| bước | lệnh | helper (rva) |
|---|---|---|
| lấy pool | `bl` @ … | `Player_Get_Datas.GetListAllIdPlayerActived()` (**21897964**) — id các vật phẩm player **đã mở** |
| chọn | `bl` @ … | `Random.Range(int,int)` (**41407168**) — min/max, không phải float |
| rút & thêm | `bl` @ … | `List<int>.RemoveAt` (**28926656**) rồi `List<int>.AddWithResize` (**28921100**) ⇒ xáo kiểu "rút ngẫu nhiên rồi nối vào cuối" |
| dải drone | `bl` @ … | `Drone_Get_Datas.get_CountDrones()` (**21862140**) — cận trên số ô |
| dải resource | `listItemResources.Length` | — |

Điều này giải thích vì sao 133/149 không tìm ra "bảng giá shop": **không có bảng nào**. Cái ship là khung; cái bán là mẫu ngẫu nhiên từ chính tiến trình của người chơi. Nên câu hỏi "ô 3 bán gì" là `MODEL_NOT_MEASURED runtime`, còn "ô 3 có thể bán gì" bị chặn bởi tập vật phẩm player đã mở của từng người.

---

## 7. Một chỗ lệch: `MaxStockCount` bị đọc mà không bị ghi

`MaxStockCount` (+0x98, `int`, **không** `[SerializeField]`):

* **đọc**: trong cả ba nhánh `<OnBuy>` của cả hai cửa hàng (6 chỗ), dùng làm trần số lượng mua;
* **ghi**: **không có** lệnh `str`/`strb` nào nhắm `+0x98` trong **2499 method** của tám lát cắt đã dump.

Field không có `[SerializeField]` nên không thể được Inspector điền; không có writer nghĩa là nó giữ **0** suốt vòng đời, trừ khi có code ngoài các lát cắt hoặc reflection. Báo cáo ghi đây là **phủ định có biên** (biên = 2499 method / 8 slice của một build `9cb038e8…`), và để trong `open_items`, không kết luận "field chết".

---

## 8. Đính chính & xác nhận

| Nguồn | Nói | 153 |
|---|---|---|
| #29 remit | "medal/shop exchange" chưa decode | **mở** — phía cửa hàng đã decode (§3–§6) |
| 151 | chỉ dùng `Popup_ArenaShopExchange` để lấy `Length` của `rewards` | **không đổi** — popup đó vẫn chưa decode ở đây; giá medal của nó thuộc event-pass, ghi `open_items` |
| (giả định ngầm) | `Arena_Shop` và `PVP_Shop` là hai implementation riêng | **đính chính**: cùng một class hai lần (§2) |
| (giả định ngầm) | shop có bảng hàng tĩnh trong APK | **đính chính**: không; `ResetShop` xáo pool của chính người chơi (§6) |

---

## 9. Còn mở

1. **Ô nào bán gì trong một bản cài thật** — `Random.Range(0, count)` ở `ResetShop`; `MODEL_NOT_MEASURED runtime`.
2. **`MaxStockCount` (+0x98) không có writer** trong 2499 method đã dump — phủ định có biên, xem §7.
3. **Giá medal của popup đổi thưởng** — `Popup_PVPShopExchange.SetPopup` đọc `Board_EventSeasonPass.EventRewards` và số medal; bảng giá nằm trong dữ liệu event-pass, thuộc lane khác.
4. **`LanguageManager.GetText` (rva 21202600)** — `InitShop` gọi nó 4 lần cho nhãn UI, nhưng method này vẫn chưa có raw pin (mục mở cũ của 137/148).

---

## 10. Chạy lại

```bash
python3 tools/verify/shop_stock_layout.py              # -> datas/l2_535b0541_shop_stock_layout.json.gz
python3 -m unittest tests.test_shop_stock_layout -q     # 33 test
```

Artifact mang `provenance` (sha256 của `arena-pvp` `3197425a…`, `stringliteral.json` `5e62507e…`, `dump.cs.gz` `e08f23fb…`) và **15 check tự khẳng định** khi build: hai khoá mỗi cửa hàng, tên khoá đúng, sáu lệnh ghi mỗi lần reset, ba dải 100/200/300, dải khớp ba mảng `Shop_Cell[]`, cả hai cùng trừ 10001, getter mặc định 0, catalogue có `Random.Range`, đường mua cộng lại 10001, mua trả bằng card, hai class trùng 30 field, chỉ một method lệch kích thước, ba lần cấp `int[5]`, và `MaxStockCount` không có writer.
