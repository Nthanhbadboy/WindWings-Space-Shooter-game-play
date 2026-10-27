# 158 — Tám field kinh tế của shop: `ldp` đọc **cặp value/cost**, và `EventRewards.stock` = `MaxStockCount`

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + dump/metadata đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Người đọc/khoảng offset/lời gọi là hằng lúc build; **nhánh nào chạy cho một dải shop cụ thể** là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_shop_field_readers.json.gz` (3922 B, sha256 `dd3af9c90a623c98e8d7519ddcb967964e2679717deeaa80f91a9bba95d79278`)
**Báo cáo trước:** 157 (hàm dựng + 12600 s), 156 (bộ đếm đã bán), 154 (popup slider), 153 (layout kho).
**Verifier:** `tools/verify/shop_field_readers.py` (~0,4 s) · **Test:** `tests/test_shop_field_readers.py` (21 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| Field nào shop **thật sự** đọc? | **cả tám** — không field nào chết | §3 |
| Vì sao 153/156 tưởng `ItemPlayerValue`/`ItemDroneValue` không ai đọc? | chúng chỉ được đọc bằng **`ldp`** (nạp cặp 8 byte), không phải `ldr w?` | §2, §3 |
| `ItemPlayerValue`/`Cost` được đọc ở đâu? | 3 chỗ mỗi shop: `InitShop` + hai nhánh của `OnClickPlayerItem` | §4 |
| Giá một ô lấy từ đâu? | dải 3: `ItemResourceCost[id − 300]`; dải player: `ItemPlayerCost × ItemPlayerValue`; dải drone: `ItemDroneCost × ItemDroneValue` | §4 |
| `EventRewards` ai dựng? | chính `OnClickPlayerItem`, **4 dòng mỗi shop**, `stock` luôn = `MaxStockCount` | §5 |
| Hai trần của 156/157 có cùng nguồn không? | **có** cho các dòng shop tự dựng: `EventRewards.stock` ← `MaxStockCount` (+0x98) | §5 |
| Còn thiếu gì? | nội dung ba số của hai mảng `int[3]` (blob `InitializeArray` không bind được) | §7 |

**Một câu:** shop đọc **cả tám** field hàm dựng, và bốn dòng `EventRewards` nó tự tạo đều lấy `stock = MaxStockCount` — nên trần trên ô và trần slider là **cùng một con số 10**, không phải hai nguồn rời.

---

## 1. Vì sao cần báo cáo này

157 chốt hàm dựng ghi tám field nhưng để mở câu "field nào thật sự chạy". Audit item 9 (*"medal shop prices / stock"*) vẫn `OPEN` với lý do *"prices/stock đến từ shop config arrays"*. Lượt này đếm người đọc theo từng field, thay vì suy từ tên field.

---

## 2. Hai cái bẫy của phép đếm, và cách loại

**(a) `ldp` nạp hai số một lần.** `ldp w8, w9, [x19, #0x9c]` đọc `+0x9C` vào `w8` và `+0xA0` vào `w9`. Một census chỉ tìm `ldr w?` sẽ thấy hai field này "không ai đọc" — **đúng cùng một loại lỗi** làm 153 kết luận sai rằng `+0x98` không có writer (store 128-bit `stur q0`). Artifact đếm riêng: **24 lượt đọc cặp**, và cả bốn field value/cost đều có **0 lượt đọc đơn**.

**(b) Phần lớn toán hạng `#0xb0`/`#0xb8` trong các method này là ô metadata, không phải field.** Ví dụ ngay trong hàm dựng:

```
22735056  ldr x22, [x22, #0x318]     ← sau adrp x22,#0x2add000: ô metadata
22735060  ldr x20, [x20, #0xa8]      ← sau adrp x20,#0x2ae1000: ô metadata
22735064  ldr x21, [x21, #0xb0]      ← ô metadata
22735092  ldr x0,  [x0,  #0xa8]       ← chuỗi khởi tạo metadata (bl 0x110d028)
```

Census vì vậy chỉ đếm truy cập có **base register truy ngược về `this`** (qua `mov`/nạp con trỏ, không bao giờ qua `adrp`). Cột *captured* là truy cập qua một field trỏ tới shop khác (ví dụ closure giữ shop ở `+0x18 → +0x10`).

---

## 3. Bảng đếm (mỗi dòng = một field, hai shop cộng lại)

| field | offset | đọc | trong đó `ldp` | đọc trực tiếp `this` | qua con trỏ | ghi |
|---|---|---|---|---|---|---|
| `MaxStockCount` | +0x98 | **16** | 0 | 8 | 8 | 2 |
| `ItemPlayerValue` | +0x9C | 6 | **6** | 0 | 0 | 0 |
| `ItemPlayerCost` | +0xA0 | 6 | **6** | 0 | 0 | 0 |
| `ItemDroneValue` | +0xA4 | 6 | **6** | 0 | 2 | 0 |
| `ItemDroneCost` | +0xA8 | 6 | **6** | 0 | 2 | 2 |
| `ItemResourceValues` | +0xB0 | 4 | 0 | 4 | 0 | 2 |
| `ItemResourceCost` | +0xB8 | 4 | 0 | 4 | 0 | 2 |
| `timeToReset` | +0xF8 | 4 | 0 | 2 | 2 | 2 |

Tổng: **62 truy cập** (52 đọc, 10 ghi). Nơi đọc:

- `timeToReset`: `OnEnable` (22727900 / 19936956) và coroutine đếm ngược `IEUpdateTime` (22778240 / 19951852, qua field `+0x20`).
- `ItemResourceValues`/`Cost`: **chỉ hai method** `InitShop` (22731512 / 22731548) và `OnClickPlayerItem` (22733584 / 22733540) — cùng cặp ở PVP (19940568 / 19940604 và 19942476 / 19942432).
- `MaxStockCount`: 5 lượt trực tiếp trong `OnClickPlayerItem` (22733620, 22733764, 22733904, 22734048, 22734180) — mỗi dải một lượt và mỗi chỗ kiểm trần — cộng **3 lượt qua con trỏ** `this+0x18 → +0x10` trong ba closure mua của mỗi shop (Arena 22736224 / 22772408 / 22773588, PVP 19945120 / 19946020 / 19947200). Ba closure này chính là ba dòng `MaxStockCount` mà 156 đếm.

Người ghi vẫn **chỉ hàm dựng**: `{22735024, 19943896}` — không method nào khác trong họ `Arena_Shop`/`PVP_Shop` ghi vào tám field này.

---

## 4. Hai kiểu giá trong `OnClickPlayerItem`

**Dải 3 — mảng theo chỉ số `id − 300`:**

```
22733540  ldr  x9, [x19, #0xb8]      ItemResourceCost
22733548  ldr  w8, [x21, #0x18]      cell.id
22733552  ldr  w10, [x9, #0x18]      array.Length
22733556  sub  w8, w8, #0x12c        index = id − 300
22733560  cmp  w8, w10
22733564  b.hs …                     kiểm biên
22733572  add  x9, x9, x8, lsl #2
22733576  ldr  w9, [x9, #0x20]       giá = ItemResourceCost[index]  (data ở +0x20)
22733580  str  w9, [x20, #0x10]      cell.cost
22733584  ldr  x9, [x19, #0xb0]      ItemResourceValues
22733608  ldr  w8, [x8, #0x20]
22733612  str  w8, [x20, #0x14]      cell.value = ItemResourceValues[index]
```

`0x12c` = 300, khớp dải thứ ba của 153; `+0x20` là chỗ bắt đầu của mảng `int[]` trong object IL2CPP (sau `klass`/`monitor`/`bounds`/`max_length`).

**Dải player / drone — giá = cost × value, đọc bằng `ldp`:**

```
22733888  ldp  w8, w9, [x19, #0x9c]  w8 = ItemPlayerValue(1), w9 = ItemPlayerCost(50)
22733892  mul  w9, w9, w8            = 50
22733896  stp  w9, w8, [x20, #0x10]  cell.cost = 50, cell.value = 1

22734164  ldp  w8, w9, [x19, #0xa4]  w8 = ItemDroneValue(1),  w9 = ItemDroneCost(30)
22734168  mul  w9, w9, w8            = 30
22734172  stp  w9, w8, [x20, #0x10]  cell.cost = 30, cell.value = 1
```

`InitShop` dùng đúng hai cặp này (22730376, 22730912) để đổ số cho các ô ngay khi dựng danh sách — nên `ItemPlayerCost=50` / `ItemDroneCost=30` của 157 **có** đường ra UI, chỉ là đi qua `ldp` chứ không qua `ldr`.

---

## 5. Bốn dòng `EventRewards` mỗi shop — và trần slider dùng chung `MaxStockCount`

Mỗi shop có **bốn** lời gọi `bl 19464628` trong `OnClickPlayerItem`, và 19464628 là

```
Board_EventSeasonPass.EventRewards..ctor(Shop_Pack pack, int number, int price, int stock)
```

(theo `dump.cs`). Đối số được nạp bằng `mov w2/w3/w4` ngay trước lời gọi:

| # | Arena (gọi) | `number` | `price` | `stock` | PVP (gọi) |
|---|---|---|---|---|---|
| 1 | 22733792 | `this.+0xA4` = `ItemDroneValue` | `this.+0xA8` = `ItemDroneCost` | **`this.+0x98`** | 19942684 |
| 2 | 22734080 | `this.+0x9C` = `ItemPlayerValue` | `this.+0xA0` = `ItemPlayerCost` | **`this.+0x98`** | 19942972 |
| 3 | 22734380 | `this.+0xA4` = `ItemDroneValue` | `this.+0xA8` = `ItemDroneCost` | **`this.+0x98`** | 19943272 |
| 4 | 22734492 | (số của cell) | `x20.+0x10` = `cell.cost` | **`this.+0x98`** | 19943384 |

Nguồn `stock` y hệt ở cả bốn dòng: `ldr w24/w25, [x19, #0x98]` (22733764, 22734048, 22734348, 22734460) — tức **`EventRewards.stock` ← `MaxStockCount`**.

Điều này trả lời câu 157 để mở ("10 có bằng `EventRewards.stock` không") ở mức tĩnh, cho các dòng do shop dựng:

- 154: trần slider = `EventRewards.stock − GetStockItem(index)`.
- 156: text trên ô = `MaxStockCount − GetStockItem(_id)`.
- Nay: dòng `EventRewards` mà shop đẩy sang popup mang `stock = MaxStockCount` ⇒ **hai trần là cùng một field, cùng giá trị 10** cho các dòng này.

Không kết luận gì cho các dòng `EventRewards` do **board event-pass** dựng từ dữ liệu season — đó vẫn là dữ liệu, không phải hằng.

---

## 6. Xác nhận chéo

| mục | kết quả |
|---|---|
| 154: popup cap `EventRewards.stock − sold` | **xác nhận và có nguồn** — shop tự điền `stock` từ `+0x98` (§5) |
| 156: 3 closure mỗi shop đọc `MaxStockCount` trước `sub` | **xác nhận** — đúng 3 lượt/shop, chain `this+0x18 → +0x10`, không thêm lượt nào khác |
| 157: seed `ItemPlayerCost=50`, `ItemDroneCost=30` | **xác nhận là sống** — ra UI qua `mul` + `stp` ở §4 |
| 153: dải thứ ba `300+i` | **xác nhận** — `sub w8, w8, #0x12c` trước khi chỉ số hoá hai mảng |

---

## 7. Giới hạn và open item

**Đóng được:**
- Không field nào trong tám field là chết; bảng đọc/ghi đầy đủ (§3).
- Nguồn `EventRewards.stock` cho các dòng shop dựng = `MaxStockCount` (§5) — đóng `open_items[0]` của 157.
- Đường giá của cả ba dải (§4).

**Không đóng được (STATIC-ONLY):**
- **Ba số thật của `ItemResourceCost`/`ItemResourceValues`**: hai mảng là `int[3]` do `InitializeArray` nạp từ blob `<PrivateImplementationDetails>`; bảng token nối ô static `0x2AE10A8`/`0x2AE10B0` với blob **không có trong workspace** (`ia-resolved.json` phủ 17 method, không có hai hàm dựng shop). Đây là **bước chặn chính xác**, không phải "không có dữ liệu".
- **Dải nào chạy cho ô nào**: bốn dòng `EventRewards` được bảo vệ bằng `cmp w21, #0x12c` (300) và một lựa chọn runtime ⇒ `MODEL_NOT_MEASURED runtime`.
- **Ai nhận bốn dòng đó**: mỗi dòng được truyền vào một lời gọi có target nằm ngoài tám slice đã pin; phía shop là tĩnh, phía popup chưa đọc.

---

## 8. Cách tái lập

```
python3 tools/verify/shop_field_readers.py             # dựng lại artifact, in bytes + sha256 + 15/15
python3 -m unittest tests.test_shop_field_readers -q   # 21 test
```

Artifact pin: **3922 B**, sha256 `dd3af9c90a623c98e8d7519ddcb967964e2679717deeaa80f91a9bba95d79278`, **15/15 check**, tổng `62` truy cập (`52` đọc / `10` ghi), `24` lượt đọc cặp, `8` dòng `EventRewards`. Nguồn đã pin trong artifact: `reverse-engineering/raw/arena-pvp-535b0541/native.json.gz`, `reverse-engineering/il2cpp/dump.cs.gz`, `datas/l2_535b0541_shop_ctor_timer.json.gz` (157).
