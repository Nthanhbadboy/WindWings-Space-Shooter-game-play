# 157 — `MaxStockCount` **có** writer (hàm dựng), và shop reset mỗi **12600 s = 3 h 30**

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + dump/metadata đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Năm field kinh tế và `timeToReset` là hằng lúc build; **người chơi đã chờ đủ 3 h 30 hay chưa** là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_shop_ctor_timer.json.gz` (3741 B, sha256 `30c5c67865a0c137e41f0d3dad64cee8dd55f1e89a36d70a293c7d0cc7f57fc8`)
**Báo cáo trước:** 156 (bộ đếm đã bán), 155 (ví medal), 154 (trần slider), 153 (layout kho + `ResetShop` ghi 0).
**Verifier:** `tools/verify/shop_ctor_timer.py` (~8 s) · **Test:** `tests/test_shop_ctor_timer.py` (27 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| Ai ghi `MaxStockCount` (+0x98)? | **`Arena_Shop..ctor` 22735024 và `PVP_Shop..ctor` 19943896** — và chỉ hai chỗ đó | §2, §4 |
| Vì sao 153 không thấy? | vì writer là `stur q0, [x19, #0x98]` (store 128-bit), không phải `str w?` | §5 |
| `MaxStockCount` bằng bao nhiêu? | **10** | §2 |
| Bốn field kinh tế còn lại? | `ItemPlayerValue=1`, `ItemPlayerCost=50`, `ItemDroneValue=1`, `ItemDroneCost=30` | §2, §3 |
| Hai mảng `int[3]`? | `ItemResourceValues` +0xB0, `ItemResourceCost` +0xB8, mỗi cái `new int[3]` | §3 |
| Shop reset bao lâu một lần? | **12600 s = 3 h 30** (`timeToReset` +0xF8, `private double`) | §6 |
| Cơ chế reset? | `OnEnable` đọc `GetTotalSecondsTravelTime(key)`; `= -1` **hoặc** `>= 12600.0` ⇒ `ResetShop()` | §6 |
| Nhánh "chưa tới hạn" có đóng dấu giờ không? | **không** — `InitShop()` nhảy qua lời gọi `UpdateSystemTimeSaved` | §6 |
| Có popup thứ ba cùng bộ field? | **có** — `Popup_Exchange` (TypeDefIndex 693), nằm **ngoài** cả 8 slice | §7 |

**Một câu:** `MaxStockCount = 10` là **hằng của hàm dựng**, ghi bằng một `stur q0` 128-bit cùng ba field kinh tế khác, và chính `timeToReset = 12600.0` trong cùng hàm dựng là ngưỡng để `OnEnable` gọi `ResetShop()` — nên kho shop tự đầy lại **mỗi 3 h 30**.

---

## 1. Vì sao cần báo cáo này

153 kết luận `MaxStockCount` (+0x98) **không có writer** trong 2499 method đã dump; 156 lặp lại kết luận đó ở §6 và §8. Cả hai đều dựa trên một phép quét `str`. Lượt này sửa lại điều đó bằng đúng một phép quét rộng hơn, rồi dùng cùng hàm dựng để trả lời câu 153/156 còn để mở: **khi nào `ResetShop` chạy**.

Không đọc lại: khoá `*_ITEM_STOCK` (153/156), sáu closure mua (155/156), công thức giá (154), ví medal (155).

---

## 2. Writer: một lệnh `stur`, bốn số

`Arena_Shop..ctor` (22735024, 216 B) và `PVP_Shop..ctor` (19943896, 216 B) **giống nhau từng lệnh**, chỉ khác trang `adrp` và ô cờ static-init (`#0x86f` so với `#0x4ed`):

```
22735120  adrp x8, #0x779000
22735124  ldr  q0, [x8, #0xb90]        ← literal tại va 7838608
22735128  mov  w8, #0x1e
22735132  str  w8, [x19, #0xa8]        ← ItemDroneCost = 30
22735136  mov  w1, #3
22735140  stur q0, [x19, #0x98]        ← 0x98, 0x9C, 0xA0, 0xA4 cùng lúc
```

Bốn số trong literal (little-endian, `0a000000 01000000 32000000 01000000`):

| ô | field (private) | giá trị |
|---|---|---|
| +0x98 | `MaxStockCount` | **10** |
| +0x9C | `ItemPlayerValue` | 1 |
| +0xA0 | `ItemPlayerCost` | **50** |
| +0xA4 | `ItemDroneValue` | 1 |
| +0xA8 | `ItemDroneCost` (`str w8`) | **30** |

Hai hàm dựng đọc **cùng một literal** (`va 7838608`, cùng `ldr q0, [x8, #0xb90]`), nên shop Arena và shop PvP khởi tạo kinh tế **giống hệt nhau**.

---

## 3. Hai bảng `int[3]`, và không có đường override

```
22735136  mov  w1, #3
22735144  ldr  x0, [x22]               ← element type int
22735148  bl   il2cpp_array_new
22735160  mov  x20, x0
22735164  bl   InitializeArray
22735168  str  x20, [x19, #0xb0]       ← ItemResourceValues
22735176  mov  w1, #3
22735180  bl   il2cpp_array_new
22735196  bl   InitializeArray
22735208  str  x20, [x19, #0xb8]       ← ItemResourceCost
```

Cả hai shop: hai mảng, mỗi mảng dài **3**, `InitializeArray` gọi đúng hai lần.

Bảy field trên đều **`private`** và **không** có `[SerializeField]`; `timeToReset` cũng `private double`. Không có hàng prefab `Arena_Shop`/`PVP_Shop` trong `reverse-engineering/raw/ui/_index.csv` (797 root UI), nên **không có đường dữ liệu prefab nào ghi đè** các số này — hàm dựng là nguồn duy nhất.

Hàm dựng kết thúc bằng `b #0x2782ba0` = `MonoBehaviour..ctor`, tức phần thân trên là **toàn bộ** việc khởi tạo state của shop.

---

## 4. Không có writer thứ hai: quét cả họ store

Quét toàn bộ 8 slice với mọi mnemonic bắt đầu bằng `st` và toán hạng đích `#0x98]`:

| lớp | method | rva lệnh | lệnh |
|---|---|---|---|
| `Arena_Shop` | `public void .ctor()` | 22735140 | `stur q0, [x19, #0x98]` |
| `PVP_Shop` | `public void .ctor()` | 19944012 | `stur q0, [x19, #0x98]` |

**Đúng hai dòng, cả hai là hàm dựng.** Không có `str w`, `str x`, `stp` nào khác chạm +0x98.

---

## 5. Sửa 153: lỗi nằm ở phép quét, không ở dữ liệu

153 viết: *"`MaxStockCount` (+0x98) được đọc làm trần mua nhưng không có writer trong dump"*. Câu đó **sai**, và sai vì đúng một lý do: phép quét chỉ tìm `str w?` nên không thấy một store **128-bit** phủ bốn ô liền nhau.

Hệ quả cần sửa, không chỉ là một câu chữ:

- §6 của 156 đối chiếu `maxStock = MaxStockCount − sold` với `maxStock = EventRewards.stock − sold` và ghi cột "nguồn trần" của vế đầu là *"không có writer trong dump"*. Nay vế đầu có nguồn: **hằng 10 của hàm dựng**.
- Vì vậy trần trên ô shop là **số build-time cố định 10**, còn trần slider popup là `EventRewards.stock` từ dữ liệu event-pass. Hai trần vẫn **không** được chứng minh bằng nhau.

Điều **không** thay đổi: `*_ITEM_STOCK` vẫn là bộ đếm **đã bán** (156), `ResetShop` vẫn là chỗ duy nhất đưa nó về 0 (153).

---

## 6. `timeToReset = 12600.0` và cơ chế reset

Cùng hàm dựng đặt ngưỡng thời gian:

```
22735200  mov  x8, #0x9c0000000000
22735204  movk x8, #0x40c8, lsl #48
22735212  str  x8, [x19, #0xf8]        ← 0x40C89C0000000000 = 12600.0
```

`Arena_Shop.OnEnable` (22727788, 540 B) dùng nó làm ngưỡng:

```
22727872  ldr  x0, [x20]               ← literal ô 46031920
22727884  bl   MyLibrary.GetTotalSecondsTravelTime(string)   → 21105208
22727888  fmov d1, #-1.00000000
22727892  fcmp d0, d1
22727896  b.eq #0x15accf4              → 22727924  (chưa có dấu giờ)
22727900  ldr  d1, [x19, #0xf8]        ← timeToReset
22727904  fcmp d0, d1
22727908  b.ge #0x15accf4              → 22727924  (đã đủ 12600 s)
22727912  mov  x0, x19
22727916  bl   Arena_Shop.InitShop()   → 22730080
22727920  b    #0x15acd08              → 22727944  (nhảy qua lời gọi bên dưới)
22727924  mov  x0, x19
22727928  bl   Arena_Shop.ResetShop()  → 22728328
22727932  ldr  x0, [x20]
22727940  bl   MyLibrary.UpdateSystemTimeSaved(string)        → 21105576
```

Quy tắc: `elapsed = GetTotalSecondsTravelTime(key)`.

| `elapsed` | nhánh | đóng dấu giờ? |
|---|---|---|
| `= -1` (chưa có bản ghi) | `ResetShop()` | **có** |
| `>= 12600.0` | `ResetShop()` | **có** |
| `0 … < 12600.0` | `InitShop()` | **không** (nhảy qua `UpdateSystemTimeSaved`) |

Nghĩa là mốc thời gian được ghi lại **chỉ khi shop thực sự reset** — "thời điểm reset gần nhất", không phải "lần mở gần nhất". `PVP_Shop.OnEnable` (19936844, 540 B) y hệt với tham số riêng:

| | `Arena_Shop` | `PVP_Shop` |
|---|---|---|
| `OnEnable` | 22727788 (540 B) | 19936844 (540 B) |
| khoá | `TIME_TO_RESET_ARENA_SHOP` (ô 46031920) | `TIME_TO_RESET_PVP_SHOP` (ô 46031928) |
| `GetTotalSecondsTravelTime` | 22727884 | 19936940 |
| `ldr d1,[x19,#0xf8]` | 22727900 | 19936956 |
| `InitShop()` | lời gọi 22727916 → 22730080 | 19936972 → 19939136 |
| `ResetShop()` | lời gọi 22727928 → 22728328 | 19936984 → 19937384 |
| `UpdateSystemTimeSaved` | 22727940 | 19936996 |

Hai target `ResetShop` ở bảng trên là **method thật** trong dump (`private void ResetShop()`, 1752 B; `public void InitShop()`, 1952 B) — mỗi shop chỉ có một cái.

`InitShop` dài 1952 B và `ResetShop` 1752 B, tức `ResetShop` không chỉ xoá bộ đếm: nó là toàn bộ đường dựng lại kho (153 đã thấy ba lần ghi 0 cho ba dải).

Ngoài ra `OnEnable` còn dùng chuỗi định dạng `###,###,##0` (ô 45970552) cho text đếm ngược — ghi nhận, không suy ra nhãn UI.

---

## 7. Popup đổi thưởng: **ba** bản, không phải hai

153/154/156 nói về "hai popup" (`Popup_ArenaShopExchange`, `Popup_PVPShopExchange`). Trong dump còn một lớp thứ ba có **cùng 11 field, cùng offset**:

| lớp | TypeDefIndex | field | method | method nằm trong slice |
|---|---|---|---|---|
| `Popup_ArenaShopExchange` | 466 | 11 | 8 | **8/8** |
| `Popup_PVPShopExchange` | 875 | 11 | 8 | **8/8** |
| `Popup_Exchange` | 693 | 11 | 8 | **0/8** |

Cả ba đều có `maxStock` +0x5C, `count` +0x58, `rewards` +0x60, `onExit` +0x50. Khác biệt: `Popup_Exchange.SetPopup(int, EventRewards, Sprite[] droneCardSprites, Sprite[] shipCardSprites, Action<int> exit)` có **năm** tham số (hai bản kia ba), và toàn bộ method của nó nằm **dưới** RVA thấp nhất của 8 slice (`0x128F2E4 … 0x1291AB8` so với `19586252`), nên **chưa được đọc**. Đây là "not consulted", không phải "missing".

---

## 8. Xác nhận chéo

| mục | kết quả |
|---|---|
| 156: text trên ô là `MaxStockCount − sold` | **xác nhận và định lượng** — trần là hằng **10**, text đếm lùi từ 10 |
| 153: `ResetShop` ghi 0 vào khoá kho | **xác nhận hành động, nay có thời điểm** — chạy khi `elapsed >= 12600 s` hoặc chưa có bản ghi |
| 149/150: shop Arena và shop PvP là một lớp lặp hai lần | **xác nhận ở hàm dựng** — 216 B, chung literal, kinh tế giống hệt |
| 154: popup dùng `EventRewards.stock` | **không đổi**, và có thêm bản sao thứ ba ngoài slice (§7) |

---

## 9. Giới hạn và open item

**Đóng được:**
- Ai ghi `MaxStockCount` (+0x98): hai hàm dựng, và chỉ chúng. Đóng luôn `open_items[0]` của 156 ("who writes `MaxStockCount`").
- Giá trị khởi tạo của năm field kinh tế + hai mảng `int[3]`.
- Chu kỳ reset: 12600 s, khoá riêng từng shop, ngưỡng lấy từ chính field `timeToReset`.

**Không đóng được (STATIC-ONLY):**
- **10 đơn vị có bằng `EventRewards.stock` không** — `MaxStockCount` là hằng build-time, `stock` đến từ dữ liệu event-pass; không chỗ nào trong dump so sánh hai số ⇒ `MODEL_NOT_MEASURED runtime`.
- **Reset giữa phiên** — chỉ `OnEnable` đọc lại đồng hồ, nên shop đang mở qua mốc 3 h 30 không được đường này mô tả.
- **Đồng hồ thiết bị chạy lùi** — `MyLibrary.GetTotalSecondsTravelTime` (21105208) nằm trong thư viện dùng chung, không có trong 8 slice; chỉ có lời gọi và sentinel `-1` là bằng chứng.
- **Ví của `Popup_Exchange`** — cả 8 method nằm ngoài slice nên đường mua của bản thứ ba chưa đọc.

---

## 10. Cách tái lập

```
python3 tools/verify/shop_ctor_timer.py              # dựng lại artifact, in bytes + sha256 + 18/18
python3 -m unittest tests.test_shop_ctor_timer -q    # 27 test
```

Artifact pin: **3741 B**, sha256 `30c5c67865a0c137e41f0d3dad64cee8dd55f1e89a36d70a293c7d0cc7f57fc8`, **18/18 check**. Test `test_rebuild_reproduces_bytes` dựng lại bằng `shop_ctor_timer.build()` với `mtime=0` rồi so **bytes** với file trên đĩa.

Nguồn đã pin trong artifact (sha256 từng file): `reverse-engineering/raw/arena-pvp-535b0541/native.json.gz`, `reverse-engineering/il2cpp/dump.cs.gz`, `datas/l2_535b0541_shop_stock_layout.json.gz` (để đối chiếu câu chữ 153).
