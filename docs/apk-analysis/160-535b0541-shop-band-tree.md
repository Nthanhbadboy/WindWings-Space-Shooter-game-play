# 160 — Cây chọn dải: `id ≤ 199` / `≤ 299` / `≥ 300` dẫn tới **dòng `EventRewards`** nào

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + dump/metadata đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Ngưỡng id, field nào nuôi dòng nào, ô `Shop_Pack` nào nhận giá là hằng lúc build; **id nào thực sự có trong dữ liệu shop** và **người chơi có đủ medal** là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_shop_band_tree.json.gz` (4277 B, sha256 `17ff84e54fb29080987bd6a552a9d3faf3bb48bc18778f7dcef0e8f2f5aa90a0`)
**Báo cáo trước:** 159 (chuỗi `SetPopup` → `Buy` chỉ so ví), 158 (tám field, bốn dòng, ba đường giá), 157 (hàm dựng + `timeToReset = 12600`), 156 (bộ đếm đã bán), 155 (ví medal).
**Verifier:** `tools/verify/shop_band_tree.py` (~8 s, 25 check) · **Test:** `tests/test_shop_band_tree.py` (29 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| Ngưỡng id nằm ở đâu? | hai `cmp` đầu hàm click: `cmp w8,#0xc7` (199) và `cmp w8,#0x12b` (299), cả hai `b.le` | §2 |
| `id ≤ 199` → dòng nào? | dòng **player**: `ItemPlayerValue +0x9C` / `ItemPlayerCost +0xA0`, `stock = MaxStockCount +0x98`, giá vào `Shop_Pack.PlayerCards +0x4C` | §3 |
| `200 ≤ id ≤ 299` → dòng nào? | dòng **drone**: `ItemDroneValue +0xA4` / `ItemDroneCost +0xA8`, giá vào `Shop_Pack.DroneCards +0x48` | §3 |
| `id ≥ 300` → dòng nào? | **hai** dòng: một dòng dùng lại field drone (ô `+0x48`), một dòng `id−300` đọc `ItemResourceValues +0xB0` / `ItemResourceCost +0xB8` | §3 |
| `300`/`301` khác gì các id còn lại? | ô `Shop_Pack` mà giá được ghi vào: `300 → Gcoins +0x10`, `301 → Energy +0x2C`, còn lại `→ DroneExp +0x44` | §3 |
| Vì sao 158 đếm **bốn** dòng mỗi shop mà chỉ có **ba** dải? | vì dải `≥ 300` dựng hai dòng; 4 dòng = 1 player + 1 drone + 2 resource | §3 |
| Nhánh click có tự gác không? | **có**: mỗi dải so `sold ([cell+0x28]) < MaxStockCount (+0x98)` rồi so ví, thiếu thì nhảy về epilogue 22734236 / 19943128 trước khi dựng dòng | §4 |

**Một câu:** `cell.id` thô quyết định dải (`≤199` player, `≤299` drone, `≥300` resource); mỗi dải dựng `EventRewards` từ field của chính shop, riêng dải resource dựng thêm một dòng theo chỉ số `id−300`, và ô `Shop_Pack` nhận giá nói loại hàng: `PlayerCards`, `DroneCards`, `Gcoins`, `Energy` hay `DroneExp`.

---

## 1. Vì sao cần báo cáo này

158 pin tám field và đếm **bốn** `EventRewards..ctor` mỗi shop; 159 đóng chuỗi popup. Nhưng cả hai đều dừng ở chỗ "có bốn dòng" mà chưa nói **dòng nào ứng với ô nào người chơi bấm**. Câu hỏi tồn đọng nguyên văn: *"cây chọn dải trong `OnClickPlayerItem`: ngưỡng id nào dẫn tới dòng `EventRewards` nào"*. Lượt này chỉ đóng đúng câu đó — không mở lại giá ba dải (158), chuỗi popup (159), bộ đếm (156), ví (155).

---

## 2. Cây quyết định: hai `cmp`, hai `b.le`

`Arena_Shop.OnClickPlayerItem` 22733228 (**1384 B**; `PVP_Shop` 19942120, **1380 B**):

```
22733452  ldr  w1,  [x20, #0x64]     cell.id
22733456  str  w1,  [x21, #0x18]     display.id
22733460  bl   Arena_Shop.GetIdItem        → 22732732
22733468  str  w0,  [x21, #0x1c]     display.idItem
22733476  bl   Arena_Shop.GetStockItem     → 22732896
22733484  str  w0,  [x21, #0x28]     display.sold
22733488  cmp  w8,  #0xc7            id <= 199 ?
22733492  b.le #0x15ae41c            → 22733852   player block
22733496  cmp  w8,  #0x12b           id <= 299 ?
22733500  b.le #0x15ae530            → 22734128   drone block
          (rơi xuống)                            resource block
22733556  sub  w8,  w8, #0x12c       index = id - 300
```

| | `Arena_Shop` | `PVP_Shop` |
|---|---|---|
| `OnClickPlayerItem` | 22733228 (1384 B) | 19942120 (1380 B) |
| `cmp #0xc7` / `b.le` | 22733488 / 22733492 → **22733852** | 19942380 / 19942384 → **19942744** |
| `cmp #0x12b` / `b.le` | 22733496 / 22733500 → **22734128** | 19942388 / 19942392 → **19943020** |
| `sub #0x12c` (index base) | 22733556 | 19942448 |
| `GetIdItem` | 22732732 | **19941788** (bản sao riêng của `PVP_Shop`) |
| `GetStockItem` | 22732896 | 19889588 |

Dải resource còn hai cổng biên độ trước khi đọc mảng: `cmp w8, w10` + `b.hs #0x15ae710` (22733564) cho `ItemResourceCost`, lặp lại ở 22733600 cho `ItemResourceValues` — `w10` là `array.Length` (`[x9,#0x18]`), dữ liệu thật nằm ở `+0x20`. Vượt biên thì nhảy ra ngoài hàm (22734604/22734608), tức là **không dựng dòng nào**.

---

## 3. Bốn dòng `EventRewards` và ô `Shop_Pack` đi kèm

`Board_EventSeasonPass.EventRewards..ctor(Shop_Pack pack, int number, int price, int stock)` 19464628. `Shop_Pack..ctor` 20189848. Mỗi lượt click dựng **một `Shop_Pack` cho mỗi dải**, riêng dải resource dựng **hai** (mỗi dòng một pack): 4 điểm gọi `Shop_Pack..ctor` mỗi hàm (Arena 22733720 / 22733824 / 22734004 / 22734304).

| # | dòng (Arena / PVP) | vai | `number` ← | `price` ← | `stock` ← | ô pack nhận giá |
|---|---|---|---|---|---|---|
| 1 | 22733792 / 19942684 | `resource-pre` | `ItemDroneValue +0xA4` | `ItemDroneCost +0xA8` | `MaxStockCount +0x98` | **`DroneCards +0x48`** |
| 2 | 22734080 / 19942972 | `player` | `ItemPlayerValue +0x9C` | `ItemPlayerCost +0xA0` | `+0x98` | **`PlayerCards +0x4C`** |
| 3 | 22734380 / 19943272 | `drone` | `ItemDroneValue +0xA4` | `ItemDroneCost +0xA8` | `+0x98` | **`DroneCards +0x48`** |
| 4 | 22734492 / 19943384 | `resource-index` | `display +0x14` ← `ItemResourceValues +0xB0[index]` | `display +0x10` ← `ItemResourceCost +0xB8[index]` | `+0x98` | xem bảng dưới |

Ô giá của dòng 4 chọn theo chỉ số, đúng hai `cmp` + ba `str`:

```
22733832  cmp  w21, #0x12c          ; id == 300 ?
22733836  b.ne #0x15ae65c           → 22734428
22733844  str  w23, [x22, #0x10]    ; Gcoins    (+0x10)
22734432  cmp  w21, #0x12d          ; id == 301 ?
22734436  b.ne #0x15ae670           → 22734448
22734440  str  w23, [x22, #0x2c]    ; Energy    (+0x2C)
22734448  str  w23, [x22, #0x44]    ; DroneExp  (+0x44)
```

Tên field lấy từ chính `dump.cs`, `class Shop_Pack // TypeDefIndex: 1032`: `Gcoins 0x10`, `Energy 0x2C`, `DroneExp 0x44`, `DroneCards 0x48`, `PlayerCards 0x4C`.

Ba dòng 1–3 còn **đóng dấu `GetIdItem() + 1`** vào ô card trước khi dựng pack:

```
22733736  ldr  w8,  [x8, #0x1c]     display.idItem
22733748  add  w8,  w8, #1
22733752  str  w8,  [x21, #0x48]    pack.DroneCards = idItem + 1      (dòng 1)
22734032  add  w8,  w8, #1
22734036  str  w8,  [x22, #0x4c]    pack.PlayerCards = idItem + 1     (dòng 2)
22734332  add  w8,  w8, #1
22734336  str  w8,  [x22, #0x48]    pack.DroneCards = idItem + 1      (dòng 3)
```

Dòng 4 thì pack nhận **giá** (không phải id hàng) ở `+0x10/+0x2C/+0x44`; đây là lý do hai dòng của dải resource không thể thay thế nhau.

---

## 4. Mỗi dải tự gác: `sold < MaxStockCount` và ví

Ba cổng stock (một mỗi dải), cùng nhảy về epilogue khi đã bán đủ:

```
22733616  ldr  w8,  [x21, #0x28]     sold            (resource)
22733620  ldr  w9,  [x19, #0x98]     MaxStockCount
22733624  cmp  w8,  w9
22733628  b.ge #0x15ae59c            → 22734236  epilogue (ret)
22733900  ldr  w8,  [x21, #0x28]     sold            (player)
22733912  b.ge #0x15ae59c            → 22734236
22734176  ldr  w8,  [x21, #0x28]     sold            (drone)
22734188  b.ge #0x15ae59c            → 22734236
```

Và ba lần đọc ví, một mỗi dải (`GameDatas.get_ArenaMedal` 20084804; PVP `get_PvPMedal` 20085132): Arena 22733660 / 22733944 / 22734220 — PVP 19942552 / 19942836 / 19943112. Dải player so `b.lt` (ví < tổng ⇒ thoát), dải drone so `b.ge` (ví ≥ tổng ⇒ dựng dòng, ngược lại thoát) — cùng nghĩa, chỉ khác cách xếp block.

⇒ 159 đã nói "popup gác cổng"; 160 cho thấy **cổng có từ trước khi popup tồn tại**: click đã kiểm stock và ví, popup chỉ kiểm lại số medal.

---

## 5. Ghi chú phương pháp: vì sao phải đi theo đường

Quét ngược đơn thuần từ lời gọi **sai** ở dòng 3 và 4: block player (22733852–22734127) và block drone (22734128 … 22734424) nằm ở địa chỉ **cao hơn** dải resource nhưng chỉ chạy khi `b.le` nhảy vào, nên các lệnh `ldp w23, w24, [x19, #0xa4]` (22734344) hay `str w8, [x22, #0x48]` (22734336) trông như "lệnh gần nhất" của dòng 4 dù dòng 4 không bao giờ đi qua đó. Verifier vì vậy **duyệt đồ thị luồng** (`walk_rows`): mỗi đường từ đầu hàm, trạng thái thanh ghi là (base, offset) và danh sách ô pack đã ghi; mỗi điểm `bl EventRewards..ctor` ghi lại đúng provenance của đường đang chạy. Arena tốn 475 bước, PVP 473; dòng 4 gộp ba đường con (300/301/khác) nên `pack_slots` của nó có đủ ba ô.

---

## 6. Bảng đối chiếu hai shop

| | `Arena_Shop` | `PVP_Shop` |
|---|---|---|
| `OnClickPlayerItem` | 22733228 (1384 B) | 19942120 (1380 B) |
| dòng 1 `resource-pre` | 22733792 | 19942684 |
| dòng 2 `player` | 22734080 | 19942972 |
| dòng 3 `drone` | 22734380 | 19943272 |
| dòng 4 `resource-index` | 22734492 | 19943384 |
| `cmp #0x12c` / `#0x12d` | 22733832 / 22734432 | 19942724 / 19943324 |
| ô `Gcoins`/`Energy`/`DroneExp` | 22733844 / 22734440 / 22734448 | 19942736 / 19943332 / 19943340 |
| cổng stock → epilogue | 22734236 | 19943128 |
| ví | `get_ArenaMedal` 20084804 ×3 | `get_PvPMedal` 20085132 ×3 |
| `SetPopup` (159) | 22734600 | 19943488 |

`SetPopup` vẫn là lời gọi **duy nhất** và nằm **sau dòng cuối** (22734600 > 22734492; 19943488 > 19943384) ⇒ popup luôn nhận dòng vừa dựng xong của dải.

---

## 7. Giới hạn và open item

**Đóng được:**
- Ngưỡng id và đích nhảy của từng ngưỡng ở cả hai shop (§2).
- Bốn dòng `EventRewards` ↔ dải: player / drone / resource-pre / resource-index (§3).
- Ô `Shop_Pack` nhận giá theo dải và theo id `300`/`301`/khác, kèm tên field từ `dump.cs` (§3).
- Cổng stock + ví tồn tại **trong** handler click, không chỉ trong popup (§4).

**Không đóng được (STATIC-ONLY):**
- **Id nào thực sự tồn tại trong từng dải**: `cell.id` đọc từ `cell+0x64` của dữ liệu shop đã serialize; code chỉ chứng minh biên, không chứng minh tập id — `MODEL_NOT_MEASURED runtime`.
- **`GetIdItem` có phải ánh xạ 1-1**: kết quả được ghi vào `display+0x1C`, đóng dấu `+1` vào ô card rồi dòng đọc lại; bảng ánh xạ là dữ liệu.
- **Vì sao dải resource dựng thêm dòng dùng field drone**: dòng 1 dùng `ItemDroneValue/Cost` với ô `DroneCards`; dòng nào được danh sách hiển thị là câu hỏi thứ tự UI, ngoài đường này.
- **`DroneExp +0x44`** cho các id resource khác `300`/`301`: là sản phẩm kinh nghiệm drone hay chỉ dùng lại ô, phụ thuộc dữ liệu — `MODEL_NOT_MEASURED runtime`.
- **Độ dài hai mảng `ItemResourceValues/Cost`**: `b.hs` nhảy ra ngoài hàm; độ dài thật nằm trong object shop đã serialize.

---

## 8. Cách tái lập

```
python3 tools/verify/shop_band_tree.py             # dựng lại artifact, in bytes + sha256 + 25/25
python3 -m unittest tests.test_shop_band_tree -q   # 29 test
```

Artifact pin: **4277 B**, sha256 `17ff84e54fb29080987bd6a552a9d3faf3bb48bc18778f7dcef0e8f2f5aa90a0`, **25/25 check** (4 dòng/shop, 8 dòng tổng, 4 pack/shop, 3 cổng stock + 3 lần đọc ví mỗi shop). Nguồn pin trong artifact: `reverse-engineering/raw/arena-pvp-535b0541/native.json.gz`, `reverse-engineering/il2cpp/dump.cs.gz` (đọc `Shop_Pack` field), `datas/l2_535b0541_exchange_chain.json.gz` (159), `datas/l2_535b0541_shop_field_readers.json.gz` (158).
