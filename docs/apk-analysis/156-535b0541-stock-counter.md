# 156 — `*_ITEM_STOCK` là bộ đếm **đã bán**: sáu closure cộng dồn, hai trần cùng trừ

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + dump/metadata đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Chiều tăng, người ghi và hai phép trừ là hằng lúc build; **một người chơi đã mua bao nhiêu trong mùa này** là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_stock_counter.json.gz` (3019 B, sha256 `df6ee0ebbdd61e769d3cf4257ee6648aaaf3e80f069ac2654e721096b128059b`)
**Báo cáo trước:** 155 (ví medal + 6 closure mua), 154 (popup cap `rewards.stock − GetStockItem`), 153 (khoá `*_ITEM_STOCK`, `ResetShop` ghi 0, `MaxStockCount` không có writer).
**Verifier:** `tools/verify/stock_counter.py` (~0,6 s) · **Test:** `tests/test_stock_counter.py` (28 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| `*_ITEM_STOCK` lưu cái gì? | **số đã bán**, không phải số còn lại | §3, §7 |
| Ai ghi nó sau khi mua? | **đúng 6 closure mua** của hai shop (`<>c__DisplayClass31_1/2/3`), mỗi shop ba cái | §3 |
| Ghi theo chiều nào? | **cộng**: cả 6 đều `add w2, w8, w21` ⇒ `SetStockItem(_id, snapshot + count)`; **không** có `sub` nào trong 8 slice | §3 |
| Snapshot lấy từ đâu? | từ `GetStockItem` **lúc click**, lưu vào display class `+0x28` (`str w0,[x21,#0x28]` ngay sau lời gọi) | §4 |
| Ai đọc? | **8 lời gọi mỗi shop**: 3 closure mua (vẽ lại text), 3 `InitShop`, 1 `OnClickPlayerItem`, 1 `SetPopup` của popup đổi thưởng | §5 |
| Trần là gì? | **hai trần khác nhau** cùng trừ bộ đếm: `MaxStockCount (+0x98)` cho text trên ô, `EventRewards.stock (+0x20)` cho slider của popup | §6 |
| Có chỗ nào giảm không? | **chỉ `ResetShop`** (153) đưa về 0, ba dải mỗi shop; không có đường giảm từng phần | §7 |

**Một câu:** ô `*_ITEM_STOCK` là **bộ đếm số đã bán** — nó chỉ tăng, mỗi lần mua cộng đúng `count`, và cả hai con số người chơi nhìn thấy (text trên ô, trần slider) đều là `trần − sold`.

---

## 1. Vì sao cần báo cáo này

155 chốt được **ai trừ medal** (6 closure mua) nhưng chạm bộ đếm kho chỉ để nói rằng closure mua có gọi `SetStockItem`. 153 đã đọc khoá và biết `ResetShop` ghi 0, nhưng gọi giá trị đó là "stock" mà không nói chiều biến thiên. Lượt này trả lời đúng một câu: **giá trị ấy tăng hay giảm, ai ghi, và ai trừ nó**.

Không đọc lại khoá/ba dải (153), không đọc lại ví (155), không đọc lại công thức giá (154) — chỉ đối chiếu.

---

## 2. Cặp accessor, đúng như 153 đã pin

| shop | `GetStockItem` | `SetStockItem` | TypeDefIndex | khoá | ô literal |
|---|---|---|---|---|---|
| `Arena_Shop` | 22732896 (164 B) | 22733060 (168 B) | 418 | `ARENA_SHOP_ITEM_STOCK` | `0x2AED088` (45011080) |
| `PVP_Shop` | 19889588 (164 B) | 19941952 (168 B) | 912 | `PVP_SHOP_ITEM_STOCK` | `0x2AE0D40` (44961088) |

Cả hai getter đọc với **default 0**; setter dựng khoá bằng `Int32.ToString(index)` rồi `String.Concat(prefix, index)`. Số liệu này lấy từ artifact 153 và được verifier đối chiếu lại, không suy diễn mới.

---

## 3. Người ghi: sáu closure, tất cả đều **cộng**

Quét mọi `bl` tới hai `SetStockItem` trên 8 slice: **6 lời gọi, không có lời gọi nào khác**.

| shop | closure | rva lời gọi ghi | biểu thức |
|---|---|---|---|
| `Arena_Shop` | `<>c__DisplayClass31_1` | 22736116 | `add w2, w8, w21` |
| `Arena_Shop` | `<>c__DisplayClass31_2` | 22772300 | `add w2, w8, w21` |
| `Arena_Shop` | `<>c__DisplayClass31_3` | 22773480 | `add w2, w8, w21` |
| `PVP_Shop` | `<>c__DisplayClass31_1` | 19945012 | `add w2, w8, w21` |
| `PVP_Shop` | `<>c__DisplayClass31_2` | 19945912 | `add w2, w8, w21` |
| `PVP_Shop` | `<>c__DisplayClass31_3` | 19947092 | `add w2, w8, w21` |

Đọc thẳng từ closure Arena dải 1:

```
22736080  ldr  w8, [x8, #0x28]      snapshot đã chụp lúc click
22736108  add  w2, w8, w21          w2 = snapshot + count
22736112  mov  w1, w20              w1 = _id
22736116  bl   Arena_Shop.SetStockItem
```

Ba closure của mỗi shop khớp **số lượng** ba dải của 153 (chỉ khớp số, không khẳng định thứ tự ánh xạ dải ↔ closure).

---

## 4. Snapshot: đọc một lần lúc click, không đọc lại lúc ghi

`OnClickPlayerItem(Shop_Cell cell)` gọi `GetStockItem` rồi **cất ngay** kết quả vào display class:

```
22733476  bl   Arena_Shop.GetStockItem
22733484  str  w0, [x21, #0x28]      ← closure giữ con số này
```

PVP y hệt ở `19942368` → `19942376`. Nghĩa là giá trị ghi lại là `số-đã-bán-tại-thời-điểm-click + count`, không phải "đọc lại rồi cộng" — hai lần mua liên tiếp trong cùng một frame sẽ dựa trên cùng một snapshot.

Ba field của display class được đọc qua `x19` trong closure dải 1: `+0x10` (giá/đơn vị), `+0x14` (số lượng mỗi đơn vị), `+0x18` (cell/row); `+0x1c` (id) và `+0x28` (sold) đọc qua thanh ghi khác. Ở `OnClickPlayerItem` cạnh chỗ chụp snapshot còn hai hằng so sánh **`cmp w8, #0xc7`** (199) và **`cmp w8, #0x12b`** (299) — ghi nhận số, không suy ra nhánh.

---

## 5. Người đọc: tám lời gọi mỗi shop

| nhóm | Arena_Shop | PVP_Shop |
|---|---|---|
| 3 closure mua (vẽ lại text sau khi ghi) | 22736232 · 22772420 · 22773600 | 19945132 · 19946032 · 19947212 |
| `InitShop` ×3 | 22730568 · 22731104 · 22731756 | 19939624 · 19940160 · 19940812 |
| `OnClickPlayerItem` | 22733476 | 19942368 |
| `Popup_*ShopExchange.SetPopup` | 22836152 | 19889108 |

Tức bộ đếm này được đọc ở **cả ba tầng**: lúc dựng shop, lúc click một ô, và lúc mở popup đổi thưởng.

---

## 6. Hai trần khác nhau cùng trừ bộ đếm

```
22736224  ldr  w22, [x8, #0x98]     Shop.MaxStockCount
22736232  bl   GetStockItem(_id)
22736236  sub  w8, w22, w0          text trên ô = MaxStockCount − sold
```

Sáu closure mua đều có đúng cặp này (`ldr w22,[x8,#0x98]` → `sub w8,w22,w0`): Arena `22736224/22736236`, `22772408/22772424`, `22773588/22773604`; PVP `19945120/19945136`, `19946020/19946036`, `19947200/19947216`.

Còn popup (154 §4) dùng **field khác**: `maxStock = EventRewards.stock (+0x20) − GetStockItem(index)`.

| nơi hiển thị | trần | nguồn trần |
|---|---|---|
| text trên ô shop | `MaxStockCount` **+0x98** | **không có writer trong dump** (153) |
| slider popup đổi thưởng | `EventRewards.stock` **+0x20** | dữ liệu event-pass (`MODEL_NOT_MEASURED runtime`) |

Hai trần **không** được chứng minh là bằng nhau ở đâu trong code. Nếu dữ liệu season đặt `stock` khác `MaxStockCount`, người chơi sẽ thấy "còn 3" trên ô nhưng slider chỉ cho mua 2 (hoặc ngược lại). Đây là quan sát từ hai phép trừ, không phải kết luận về UI runtime.

---

## 7. Hệ quả: bộ đếm đơn điệu tăng, `ResetShop` là chỗ duy nhất về 0

- Không có đường **giảm từng phần**: 6/6 lời gọi ghi đều `add`.
- Chỗ duy nhất ghi **0**: `ResetShop` (153) — ba dải mỗi shop, rvas `22729240 / 22729852 / 22730020` (Arena) và `19938296 / 19938908 / 19939076` (PVP), mỗi shop ghi 3 lần.
- Vì `maxStock = trần − sold` và `sold` chỉ tăng, **trần mua trong popup giảm dần trong một mùa** và chỉ được nạp lại khi shop reset.

Vì vậy từ ngữ của 153/154 ("stock", "tồn kho") nên đọc là **số đã bán**. Nếu đọc là "còn lại", mọi phép trừ ở §6 sẽ ra số âm dần — sai dấu.

---

## 8. Giới hạn và open item

**Đóng được:**
- Ai ghi bộ đếm sau khi mua (câu 155 để mở): 6 closure mua, và chỉ chúng.
- Chiều: cộng `count` vào snapshot chụp lúc click; không có `sub` nào.
- Hai trần khác nhau cùng trừ bộ đếm; `ResetShop` là chỗ duy nhất về 0.

**Không đóng được (STATIC-ONLY):**
- **Ai ghi `MaxStockCount` (+0x98)** — vẫn như 153: không có `str` nào trong dump và field không `[SerializeField]`, nên trần hiển thị không có nguồn static.
- **Mua quá trần có bị chặn không**: code đã trừ medal/cards **trước** khi đọc lại bộ đếm để vẽ text; phần so sánh nằm trong closure nhưng quyết định runtime ⇒ `MODEL_NOT_MEASURED runtime`.
- **Hai hằng `#0xc7`/`#0x12b`** chọn nhánh nào trong `OnClickPlayerItem`: chỉ có số, không có tên nhánh.

---

## 9. Cách tái lập

```
python3 tools/verify/stock_counter.py             # dựng lại artifact, in bytes + sha256 + 13/13
python3 -m unittest tests.test_stock_counter -q   # 28 test
```

Artifact pin: **3019 B**, sha256 `df6ee0ebbdd61e769d3cf4257ee6648aaaf3e80f069ac2654e721096b128059b`. Test `test_rebuild_reproduces_bytes` dựng lại bằng `stock_counter.build()` với `mtime=0` và so **bytes** với file trên đĩa.
