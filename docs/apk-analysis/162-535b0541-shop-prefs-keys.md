# 162 — Trạng thái từng ô shop nằm trong **PlayerPrefs**, và `ResetShop` là chỗ ghi công thức id

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + 8 slice + `dump.cs` đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Chuỗi lời gọi, cell tĩnh, hằng số và công thức là hằng lúc build; **giá trị thật trong `PlayerPrefs`** và nội dung các `List<int>` là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_shop_prefs_keys.json.gz` (4384 B, sha256 `6c0fbe7397dbb187f959a95d50b5abf29da9aa46b1b7f23e268ec3517bbf7886`)
**Báo cáo trước:** 161 (index RVA của dump + errata `static class`), 160 (cây chọn dải), 159 (chuỗi popup), 157 (hàm dựng + 12600 s), 156 (bộ đếm đã bán), 153 (bố cục ô + ba dải).
**Verifier:** `tools/verify/shop_prefs_keys.py` (~1 s, 22 check) · **Test:** `tests/test_shop_prefs_keys.py` (29 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| `GetIdItem(index)` làm gì? | `PlayerPreferences.GetInt(<cell ID> + index.ToString(), 0)` | §3 |
| `GetStockItem(index)` làm gì? | `PlayerPreferences.GetInt(<cell STOCK> + index.ToString(), 0)` | §3 |
| `SetStockItem(index, v)` làm gì? | `PlayerPreferences.SetInt(<cell STOCK> + index.ToString(), v)` | §3 |
| Vậy id trong ô shop nằm ở đâu? | **PlayerPrefs**, không phải trong asset `Shop` đã serialize | §3 |
| Ai ghi khoá id? | **chỉ `ResetShop`** — không tồn tại `SetIdItem` nào trong 64 727 method | §4, §5 |
| `ResetShop` ghi gì cho từng dải? | player `catalogue[i] − 10001` · drone `catalogue[i]` · resource `= cell id`; stock **luôn 0** | §4 |
| Ba dải của 153 là gì? | chính là **ba công thức id được ghi**, không phải ba mức giá | §4, §6 |
| `GetIdItem` có phải ánh xạ 1-1? | **không** — chỉ dải resource tình cờ lưu đúng cell id | §6 |
| Vì sao `MaxStockCount` (+0x98) không có writer? | vì trần là **field của asset**, còn bộ đếm là **pref** — hai kho khác nhau | §6 |
| Mỗi cell tĩnh bị mấy method chạm? | ID: **2** method · STOCK: **3** method, tất cả trong lớp shop của nó | §2 |

**Một câu:** cả trạng thái từng ô của shop (id hàng và số đã bán) nằm trong `PlayerPrefs` dưới khoá `"<TÊN_KHOÁ>" + cellId.ToString()`; `ResetShop` là nơi duy nhất ghi khoá id, và nó ghi ba công thức khác nhau cho ba dải — `−10001`, giữ nguyên, và chính cell id — rồi xoá bộ đếm bán về 0.

---

## 1. Vì sao cần báo cáo này

160 kết thúc bằng một open item nguyên văn: *"whether `GetIdItem` (22732732) is an identity map — the mapping table itself is data"*. 153 thì pin bốn cell tĩnh và kết luận kho stock bị `ResetShop` xoá về 0, nhưng **không** nhìn khoá id. 161 vừa cho một index đặt tên được mọi đích `bl` trong slice — nên lượt này chỉ cần đọc đúng sáu hàm nhỏ (164/164/168 byte × 2 shop) và một hàm `ResetShop` 1752 byte để trả lời cả hai câu.

Phạm vi: chỉ sáu accessor + `ResetShop` của hai shop. Không mở lại giá ba dải (158), chuỗi popup (159), cây chọn dải (160), bộ đếm (156), ví (155).

---

## 2. Bốn cell tĩnh và ai chạm vào chúng

Địa chỉ tuyệt đối dựng lại từ cặp `adrp`+`ldr` (có **huỷ hiệu lực khi thanh ghi bị ghi đè** — nếu không sẽ ra hàng loạt dương tính giả, đúng lỗi 160 đã gặp):

| cell | địa chỉ | site | method chạm |
|---|---|---|---|
| `ARENA_SHOP_ITEM_ID` | `0x2aed090` | 4 | `Arena_Shop.GetIdItem` 22732732 · `Arena_Shop.ResetShop` 22728328 |
| `ARENA_SHOP_ITEM_STOCK` | `0x2aed088` | 6 | `GetStockItem` 22732896 · `SetStockItem` 22733060 · `ResetShop` 22728328 |
| `PVP_SHOP_ITEM_ID` | `0x2ae1018` | 4 | `PVP_Shop.GetIdItem` 19941788 · `PVP_Shop.ResetShop` 19937384 |
| `PVP_SHOP_ITEM_STOCK` | `0x2ae0d40` | 6 | `GetStockItem` 19889588 · `SetStockItem` 19941952 · `ResetShop` 19937384 |

Không method nào ngoài hai lớp shop chạm bốn cell này trong 1 788 method của tám slice. Tên khoá lấy nguyên từ 153 (đọc từ bảng field), lượt này chỉ xác nhận lại **từ phía code**.

---

## 3. Ba accessor, mỗi cái một dòng

`Arena_Shop.GetIdItem(int index)` **22732732** (164 B; PVP `19941788`, 164 B):

```
22732808  add  x0, sp, #0xc        ; &index
22732816  bl   Int32.ToString                  → 34616120
22732836  bl   String.Concat(str0, str1)       → 33439876   ; <cell ID> + index
22732876  bl   PlayerPreferences.GetInt(key, 0) → 20912668   ; w1 = wzr ⇒ mặc định 0
```

`GetStockItem` 22732896 / 19889588 (164 B) y hệt, chỉ đổi cell sang `<…>_STOCK`.
`SetStockItem(int index, int stock)` 22733060 / 19941952 (168 B) y hệt nhưng kết thúc bằng `PlayerPreferences.SetInt(key, w19)` 20912644, và `w19 = w2` là tham số `stock`.

| accessor | Arena | PVP | byte | kết thúc bằng |
|---|---|---|---|---|
| `GetIdItem` | 22732732 | 19941788 | 164 | `GetInt(key, 0)` |
| `GetStockItem` | 22732896 | 19889588 | 164 | `GetInt(key, 0)` |
| `SetStockItem` | 22733060 | 19941952 | 168 | `SetInt(key, value)` |

Hệ quả trực tiếp: **khoá là chuỗi**, nên `GetIdItem(105)` không phải "phần tử 105" của bảng nào trong asset — nó là `PlayerPrefs["ARENA_SHOP_ITEM_ID105"]`. Việc nối chuỗi làm bằng `String.Concat` với `Int32.ToString()`, không có dấu phân cách.

---

## 4. `ResetShop`: sáu lần `SetInt`, ba dải, ba công thức

`Arena_Shop.ResetShop()` **22728328** (1752 B, 438 lệnh; PVP `19937384`, cùng 1752 B) — cấu trúc đối xứng tuyệt đối:

| dải | khoá index | hằng số | giá trị ghi vào khoá **ID** | giá trị ghi vào khoá **STOCK** |
|---|---|---|---|---|
| player | `add w28, w22, #0x64` (100 + i) | `mov w29, #-0x2711` | `add w1, w21, w29` ⇒ `catalogue[i] − 10001` | `mov w1, wzr` ⇒ **0** |
| drone | `add w27, w22, #0xc8` (200 + i) | — | `mov w1, w21` ⇒ `catalogue[i]` | **0** |
| resource | `add w20, w9, #0x12c` (300 + i) | — | `mov w1, w20` ⇒ **chính cell id** | **0** |

Sáu lời gọi `SetInt` mỗi shop: Arena `22729192, 22729240, 22729804, 22729852, 22729972, 22730020`; PVP `19938248, 19938296, 19938860, 19938908, 19939028, 19939076` — luôn theo cặp **(ID, STOCK)** cho mỗi dải.

Bối cảnh của `w21` (giá trị catalogue) đáng ghi: dải player lấy từ mảng `[this+0x68]`, dải drone **tự dựng** danh sách bằng `Drone_Get_Datas.get_CountDrones()` (21862140) + `Random.Range(0, count)` (41407168) + `List<int>.RemoveAt` (28926656) + `List<int>.AddWithResize` (28921100), dải resource đi thẳng theo độ dài `[this+0x78]`. Đây là lý do dải drone **không** có hằng số bù: danh sách của nó đã là id drone thật.

> `Random.Range` chính là chỗ 161 sai tên lớp (nó ghi `PropertyName`), đã sửa ở errata 161 §11 và được 162 dùng làm phép thử.

---

## 5. Không có `SetIdItem` — khoá id chỉ có một người ghi

Quét **cả 64 727 method** của `dump.cs`: **0** method có `SetIdItem` trong signature. Ba accessor là toàn bộ API của khoá: `GetIdItem` (đọc), và `ResetShop` (ghi, 3 lần). Không có setter công khai nào để UI hay server đặt id trực tiếp.

Đây là phủ định **có biên rõ**: biên là 64 727 method của build `9cb038e8…`; một caller tự dựng chuỗi khoá rồi gọi `PlayerPreferences.SetInt` chung chung thì phép quét tên không bắt được, nên câu đúng là *"không có setter id nào trong metadata; ngoài `ResetShop` không method nào chạm cell id trong tám slice"*.

---

## 6. Ba dải của 153 hoá ra là ba công thức ghi

153 đọc ra ba dải `id − 10001` / `id` / `300 + i` và gọi đó là "ba đường giá". Nay rõ nghĩa:

| 153 nói | thực tế |
|---|---|
| dải 1: `id − 10001` | giá trị `ResetShop` **ghi** vào khoá ID cho cell `100 + i`: `catalogue[i] − 10001` (`mov w29, #-0x2711`) |
| dải 2: `id` | giá trị ghi cho cell `200 + i`: `catalogue[i]` nguyên |
| dải 3: `300 + i` | giá trị ghi cho cell `300 + i`: chính cell id ⇒ **dải duy nhất mà `GetIdItem` là ánh xạ 1-1** |

Đồng thời trả lời hai câu còn treo:

* **160 hỏi `GetIdItem` có phải 1-1** → **không**. Nó đọc một entry `PlayerPrefs` do `ResetShop` ghi; chỉ dải resource tình cờ trùng cell id.
* **153 hỏi vì sao `MaxStockCount` (+0x98) không có writer** → vì trần nằm trong **asset `Shop`** (157: ctor đặt 10), còn "đã bán" nằm trong **prefs**. Hai kho khác nhau, nên không có writer cho trần là chuyện bình thường, không phải field chết.

---

## 7. Bảng đối chiếu hai shop

| | `Arena_Shop` | `PVP_Shop` |
|---|---|---|
| `GetIdItem` | 22732732 (164 B) | 19941788 (164 B) |
| `GetStockItem` | 22732896 (164 B) | 19889588 (164 B) |
| `SetStockItem` | 22733060 (168 B) | 19941952 (168 B) |
| `ResetShop` | 22728328 (1752 B) | 19937384 (1752 B) |
| cell ID / STOCK | `0x2aed090` / `0x2aed088` | `0x2ae1018` / `0x2ae0d40` |
| khoá index | 100 + i / 200 + i / 300 + i | giống hệt |
| hằng bù dải player | `−10001` (`#-0x2711`) | giống hệt |
| `SetStockItem` được gọi bởi | 6 closure mua (156) | 6 closure mua (156) |

---

## 8. Giới hạn và open item

**Đóng được:**
- Ba accessor mỗi shop là `PlayerPrefs` `GetInt`/`SetInt` trên khoá `"<cell>" + index`.
- Bốn cell tĩnh × số method chạm (2 cho ID, 3 cho STOCK), không method ngoài lớp shop.
- `ResetShop` ghi **cả hai** khoá cho cả ba dải, kèm công thức id và việc xoá stock.
- Không tồn tại `SetIdItem` trong 64 727 method ⇒ khoá id chỉ có `ResetShop` ghi.
- Ba dải của 153 = ba công thức ghi, không phải ba mức giá; `GetIdItem` không 1-1.

**Không đóng được (STATIC-ONLY):**
- **Nội dung các `List<int>`**: dải player/resource đọc mảng `[this+0x68]`/`[this+0x78]`, dải drone dựng bằng `Drone_Get_Datas` + `Random.Range` ⇒ giá trị là dữ liệu chạy — `MODEL_NOT_MEASURED runtime`.
- **`PlayerPrefs` sống sót qua cài lại hay không**: là `SharedPreferences` của Android; hành vi nền tảng nằm ngoài APK — `MODEL_NOT_MEASURED runtime`.
- **Ý nghĩa của `−10001`**: hằng số đọc được, nhưng vì sao dải player lệch 10 001 đơn vị so với catalogue thì phụ thuộc dữ liệu catalogue.
- **Chuỗi thật trong cell**: 153 pin tên khoá từ bảng field; code chỉ `Concat`, không dựng khoá ở đây.

---

## 9. Cách tái lập

```
python3 tools/verify/shop_prefs_keys.py             # dựng lại artifact, in bytes + sha256 + 22/22
python3 -m unittest tests.test_shop_prefs_keys -q   # 29 test
```

Artifact pin: **4384 B**, sha256 `6c0fbe7397dbb187f959a95d50b5abf29da9aa46b1b7f23e268ec3517bbf7886`, **22/22 check** (2 shop, 6 accessor, 8 site cell ID, 12 site cell STOCK, 12 lần ghi `SetInt`). Nguồn pin: `reverse-engineering/raw/arena-pvp-535b0541/native.json.gz` + 7 file slice còn lại, `reverse-engineering/il2cpp/dump.cs.gz`, `datas/l2_535b0541_shop_stock_layout.json.gz` (153), `datas/l2_535b0541_stock_counter.json.gz` (156), `datas/l2_535b0541_shop_band_tree.json.gz` (160), `datas/l2_535b0541_dump_rva_index.json.gz` (161).
