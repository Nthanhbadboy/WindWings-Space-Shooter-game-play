# 163 — `Action<int>` của popup trỏ vào **lambda nào**: ba `<>c__DisplayClass31_N`, không cần bảng token

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + 8 slice + `dump.cs` đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Đích delegate, thân lambda và phép trừ ví là hằng lúc build; **số pack người chơi bấm**, **nội dung hai catalogue** và **tràn 32-bit** là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_buy_delegate.json.gz` (8343 B, sha256 `a1c98fc6ad2d529c26c692a9565250c94962a6e760b55ce1e11d15f1327c6f5b`)
**Báo cáo trước:** 162 (khoá PlayerPrefs), 161 (index RVA của dump), 160 (cây chọn dải), 159 (chuỗi popup), 156 (bộ đếm đã bán), 153 (bố cục ô + ba dải).
**Verifier:** `tools/verify/buy_delegate.py` (~0,8 s, 43 check) · **Test:** `tests/test_buy_delegate.py` (52 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| `Action<int>` mà `SetPopup` nhận trỏ vào method nào? | `<OnClickPlayerItem>b__1` / `b__3` / `b__5` — **một lambda cho mỗi dải** | §4 |
| Có cần bảng metadata token không? | **Không.** `x1` là đúng object vừa cấp trong cùng hàm, và lớp đó chỉ có **một** method `void (int)` | §4 |
| Ba dải cấp ba lớp nào? | `<>c__DisplayClass31_1` (player) · `_2` (drone) · `_3` (resource) | §2, §3 |
| Lambda làm gì trước khi mua? | bật lại `ScrollView.EnableScrollView(true)`, rồi **no-op nếu `count < 1`** | §5 |
| Lambda gọi tiếp đâu? | nhảy đuôi (`b`) sang `g__OnBuy\|2` / `\|4` / `\|6(locals.id, count)` | §5 |
| Closure trừ ví thế nào? | `msub` = `số dư − itemCost × count` — **một** phép trừ, không kiểm tra lại | §6 |
| `itemCost` ở đâu ra? | player `0x9c × 0xa0`, drone `0xa4 × 0xa8`; resource đọc thẳng **bảng giá** | §3 |
| Closure cộng gì? | `PlayerCards[id + 10001]` · `DroneCards[id + 20001]` · `Coins`/`Energy`/`DroneExp` | §6, §7 |
| Ai chặn mua khi thiếu ví? | **chỉ `OnClickPlayerItem`** (guard inline trên từng nhánh) — closure không đọc lại ví | §6 |
| Sau khi mua, ô shop hiện gì? | dựng lại chuỗi 5 phần tử qua `String.Concat` → `Shop_Cell.SetStockCount` | §8 |

**Một câu:** popup không giữ con trỏ method nào cả — mỗi dải cấp một `<>c__DisplayClass31_N` riêng, và vì lớp đó chỉ khai báo đúng một method `void (int)` nên `Action<int>` buộc phải trỏ vào lambda `b__N` của chính nó; lambda đó bật lại scroll view, chặn `count < 1`, rồi nhảy đuôi sang `g__OnBuy|N` để trừ ví bằng `msub`, cộng vật phẩm và ghi lại bộ đếm đã bán.

---

## 1. Vì sao cần báo cáo này

159 đóng chuỗi popup (`OnPressedButtonBuy` so ví rồi `blr x9`) nhưng để lại nguyên văn một open item: *"the delegate target method is read from a static cell, so naming it needs a metadata token table"*. Lượt này cho thấy câu đó **không cần** bảng token: IL sinh ra `new Action<int>(target, methodCell)` với `target` là object vừa cấp trong chính `OnClickPlayerItem`, nên chỉ cần đọc **cấu trúc lớp** là đủ.

Phạm vi: bảy cell tĩnh của `OnClickPlayerItem` trong hai lớp shop, ba lambda 108 byte, ba closure `g__OnBuy|N`, và các guard inline trên ba nhánh. Không mở lại giá ba dải (158), chuỗi popup (159), cây chọn dải (160), bộ đếm (156), khoá PlayerPrefs (162).

---

## 2. Bảy cell tĩnh, và vì sao đúng là bảy

`OnClickPlayerItem(Shop_Cell cell)` — Arena **22733228** (1384 B), PVP **19942120** (1380 B) — đọc bảy ô trên đúng một trang:

| dải | cell **lớp** | cell **method** | Arena | PVP |
|---|---|---|---|---|
| (ngoài, lớp bắt `this`/`cell`) | `0xb8` | — | `0x2aed0b8` | `0x2ae1058` |
| player | `0xc8` | `0xc0` | `0x2aed0c8` / `0x2aed0c0` | `0x2ae1068` / `0x2ae1060` |
| drone | `0xd8` | `0xd0` | `0x2aed0d8` / `0x2aed0d0` | `0x2ae1078` / `0x2ae1070` |
| resource | `0xe8` | `0xe0` | `0x2aed0e8` / `0x2aed0e0` | `0x2ae1088` / `0x2ae1080` |

Mỗi ô được đọc **đúng hai lần** trong một shop: một lần trong khối static-init (`bl 0x110d028`, tám site liền nhau) và một lần ở chỗ dùng thật ⇒ **14** site `adrp`+`ldr` mỗi hàm (verifier đếm `click.signatures == 14`). Khối static-init nằm **trước** chỗ rẽ nhánh nên không thuộc nhánh nào; verifier ghi nó vào `not_on_a_band_path` (8 dòng = 1 cấp lớp ngoài + 7 static-init).

Cách quy ô về nhánh: dựng **tập đạt tới** (reachability) của từng nhánh từ ba điểm vào, rồi ô nào chỉ nằm trong tập của một nhánh thì thuộc nhánh đó. Đây là lý do phải đi theo luồng điều khiển chứ không quét cửa sổ lệnh liền kề: khối nhánh player kết thúc bằng `b` sang khối chung, và nếu quét văn bản sẽ vơ luôn lệnh `bl` của nhánh drone nằm ngay sau (lỗi đã gặp khi viết verifier).

---

## 3. Ba nhánh, và cái mỗi nhánh dán vào closure

Bậc rẽ nhánh giữ nguyên 160:

```
cmp w8, #0xc7   ; id ≤ 199  → nhánh player    (khoá 100 + i, 162)
b.le  …
cmp w8, #0x12b  ; id ≤ 299  → nhánh drone     (khoá 200 + i, 162)
b.le  …
                ; còn lại   → nhánh resource  (khoá 300 + i, 162)
```

Mỗi nhánh, sau khi cấp closure `{itemCost@0x10, itemValue@0x14, locals@0x18}`, **dán giá** vào hai field đó:

| nhánh | lệnh dán | nghĩa |
|---|---|---|
| player | `ldp w8, w9, [x19, #0x9c]` · `mul w9, w9, w8` · `stp w9, w8, [x20, #0x10]` | `itemCost = 0x9c × 0xa0`, `itemValue = 0x9c` |
| drone | `ldp w8, w9, [x19, #0xa4]` · `mul w9, w9, w8` · `stp w9, w8, [x20, #0x10]` | `itemCost = 0xa4 × 0xa8`, `itemValue = 0xa4` |
| resource | `add x9, x9, x8, lsl #2` · `ldr w9, [x9, #0x20]` · `str w9, [x20, #0x10]` | giá đọc từ **`List<int>` 0xb8**, số lượng từ **`List<int>` 0xb0** |

Tức `itemCost` mà popup so (159) **đã là** giá của cả gói (`value × cost`), còn `count` là số gói — nên closure trừ `itemCost × count` là đúng `cost × value × count`, và cộng `itemValue × count` thẻ.

Trước khi dựng popup, mỗi nhánh còn hai guard inline (ghi trong `medal_guard` / `stock_guard`):

```
ldr w8, [x21, #0x28]      ; stock chụp lúc mở ô (locals.stock)
ldr w9, [x19, #0x98]      ; MaxStockCount
cmp w8, w9
b.ge  <thất bại>          ; đã bán đủ trần ⇒ không mở popup
…
bl    GameDatas.get_ArenaMedal / get_PvPMedal
cmp   w0, w8              ; số dư vs itemCost
b.lt / b.ge  <thất bại>   ; thiếu ví ⇒ không mở popup (độ cực đảo theo cách xếp khối)
```

---

## 4. Delegate: `new Action<int>(closure, *cell)` — và phép loại trừ

Cả ba nhánh kết thúc bằng cùng một khuôn (Arena gọi tại **22734552**, PVP tại **19943444**, đích `0x18a4d84` = **25841028**, một instantiation `Action<int>..ctor` trong bảng generic):

```
adrp x8, #0x2aed000
ldr  x8, [x8, #0xd0]      ; ← cell METHOD của nhánh
ldr  x2, [x8]             ; x2 = con trỏ method trong cell
mov  x1, x20              ; x1 = closure vừa cấp của nhánh
bl   Action<int>..ctor    ; 25841028
…
b    Popup_ArenaShopExchange.SetPopup   ; Arena 22734600 → 22835700
                                        ; PVP   19943488 → 19888660
```

`x1` là **object vừa cấp trên chính nhánh đó**: cả ba nhánh đều `mov x20, x0` ngay sau `bl 0x110d240` (allocation helper), và `x20` không bị ghi đè cho tới lệnh này. Một delegate của C# chỉ bind được vào method **instance của lớp của target**, nên chỉ cần biết lớp đó có bao nhiêu method nhận một `int`:

| lớp | `.ctor()` | `g__OnBuy\|N(int _id, int count)` | `b__N(int count)` |
|---|---|---|---|
| `Arena_Shop.<>c__DisplayClass31_1` | 22734620 | 22735600 | **22735492** |
| `Arena_Shop.<>c__DisplayClass31_2` | 22771696 | 22771812 | **22771704** |
| `Arena_Shop.<>c__DisplayClass31_3` | 22772596 | 22772712 | **22772604** |
| `PVP_Shop.<>c__DisplayClass31_1` | 19944372 | 19944488 | **19944380** |
| `PVP_Shop.<>c__DisplayClass31_2` | 19945308 | 19945424 | **19945316** |
| `PVP_Shop.<>c__DisplayClass31_3` | 19946208 | 19946324 | **19946216** |

Mỗi lớp đúng **ba** method, và **một** trong ba có dạng `void (int)` — nên đích delegate là `b__N` **theo phép loại trừ**, không cần đọc nội dung cell.

Nhãn dải lấy từ **vị trí bậc rẽ nhánh** (160 + 162 đã pin `0xc7 / 0x12b` và ba gốc khoá `100 / 200 / 300`), rồi đối chiếu độc lập bằng **vật phẩm mà closure cộng**: nhánh thứ nhất ⇒ dải player ⇒ `PlayerCards`, thứ hai ⇒ `DroneCards`, nhánh còn lại ⇒ ví. Cả hai cách khớp cho cả hai shop (`granted-items-match-the-ladder-position`).

Lớp được nhận diện bằng `ctor` được gọi: 5/6 nhánh gọi đúng `<>c__DisplayClass31_N..ctor`, riêng nhánh **player của Arena** gọi `Object..ctor` (thân `.ctor` rỗng nên IL2CPP gộp) — nên nó là `_1` **theo phép trừ** hai lớp còn lại, và vẫn khớp vì đúng lớp đó có duy nhất một `void (int)`.

---

## 5. Lambda 108 byte: bật lại scroll, chặn `count < 1`, nhảy đuôi

Cả sáu lambda cùng khuôn, cùng kích thước **108 B** (Arena 22735492 / 22771704 / 22772604; PVP 19944380 / 19945316 / 19946216):

```
ldr x8, [x0, #0x18]      ; locals
cbz x8, …
ldr x8, [x8, #0x10]      ; <>4__this = shop
cbz x8, …
ldr x0, [x8, #0x50]      ; shop.ScrollView
cbz x0, …
mov w19, w1              ; count
mov w1, #1
bl  ScrollView.set_EnableScrollView(true)    ; 21291032 — bật LẠI scroll
cmp w19, #1
b.lt <thoát>             ; count < 1 ⇒ không làm gì
ldr  w1, [x8, #0x18]     ; locals.id
mov  x0, x20             ; this = closure
mov  w2, w19             ; count
b    <OnClickPlayerItem>g__OnBuy|N         ; nhảy ĐUÔI, không gọi
```

Hai điều đáng ghi: (a) `OnClickPlayerItem` **tắt** scroll (`mov w1, wzr`) trước khi mở popup, lambda **bật lại** — nên scroll không bao giờ kẹt tắt sau khi mua; (b) lambda nhảy đuôi (`b`, không phải `bl`), nên khung stack của `Action<int>` được dùng lại nguyên vẹn cho closure.

---

## 6. Closure: một `msub` cho ví, không đọc lại ví

Ba closure, cùng thứ tự thao tác, khác phần cộng thưởng:

| | Arena | PVP | byte |
|---|---|---|---|
| player | 22735600 | 19944488 | 808 / 820 |
| drone | 22771812 | 19945424 | 784 / 784 |
| resource | 22772712 | 19946324 | 1068 / 1068 |

```
bl   GameDatas.get_ArenaMedal / get_PvPMedal
ldr  w8, [x19, #0x10]        ; itemCost
msub w0, w8, w21, w0         ; số dư − itemCost × count
bl   GameDatas.set_ArenaMedal / set_PvPMedal
```

Ví: Arena `get_ArenaMedal` **20084804** / `set_ArenaMedal` **20085004**; PVP `get_PvPMedal` **20085132** / `set_PvPMedal` **20085332**.

Giữa lần `get` và `msub` chỉ có đúng hai lệnh (`ldr w8, [x19, #0x10]`, `mov x1, xzr`) — **không** có `cmp`, tức closure **không** kiểm tra lại số dư. Điều này làm guard inline ở §3 thành **cửa duy nhất** lúc mua, đúng như 159 mô tả ở phía popup. (Nếu số dư đổi giữa lúc mở popup và lúc bấm mua thì `set_…Medal` nhận giá trị âm — nhánh đó là `MODEL_NOT_MEASURED runtime`.)

---

## 7. Cộng thưởng: ba đường, có thiên lệch chỉ số

**player** — `mov w8, #0x2711` (**22736024**), `add w22, w22, w8`, rồi `GetPlayerCards` **22736040**, `madd w1, w8, w21, w0` (**22736052**), `SetPlayerCards` **22736060**:

```
PlayerCards[itemId + 10001] += itemValue × count
```

**drone** — `mov w9, #0x4e21` (**22772204**), `GetDroneCards` **22772220**, `madd` **22772232**, `SetDroneCards` **22772240**:

```
DroneCards[itemId + 20001] += itemValue × count
```

**resource** — rẽ theo id, mỗi nhánh `get` → `madd` → `set`:

| điều kiện | cộng vào | get | madd | set | hiệu ứng |
|---|---|---|---|---|---|
| `cmp w20, #0x12d` (`b.eq`) | `Energy` | 22773172 | 22773184 | 22773188 | `CallEffectStatic(type 2)` 22773240, rồi `PostEvent` 22773296 |
| `cmp w20, #0x12c` | `Coins` | 22773040 | 22773052 | 22773056 | `CallEffectStatic(type 0)` 22773108 |
| còn lại | `DroneExp` | 22773308 | 22773320 | 22773324 | không gọi `CallEffectStatic` (artifact chỉ có 2 entry cho hai nhánh trên) |

Tất cả đều là **read-modify-write** trên cùng một bộ đếm (`madd`, không phải gán).

---

## 8. Sau khi cộng: bộ đếm đã bán, rồi dựng lại chuỗi của ô

Giống nhau ở cả sáu closure:

```
ldr w8,  [.., #0x28]        ; stock chụp lúc mở ô
add w2,  w8, w21            ; snapshot + count
bl      SetStockItem(id, …) ; Arena 22736116 / 22772300 / 22773480
                            ; PVP   19945012 / 19945912 / 19947092
```

rồi dựng mảng `string[5]` (`bl 0x110d09c` với `mov w1, #5`), đổ năm phần tử:

1. nhãn `LanguageManager.GetText(…)`;
2. literal đọc từ `0x2adb000 + 0xbd0`;
3. **số còn lại** — `sub w8, w22, w0` với `w22 = MaxStockCount`, `w0 = GetStockItem(id)` (`Arena` 22736236 / 22772424 / 22773604);
4. literal đọc từ `0x2adb000 + 0x8d0`;
5. **trần** `MaxStockCount` — `add x0, x8, #0x98` rồi `Int32.ToString()` (`Arena` 22736312 / 22772500 / 22773680);

rồi gộp bằng `String.Concat(string[])` và đưa vào `Shop_Cell.SetStockCount(str)`. Artifact ghi từng phần tử dưới `cell_text.{cells, subs, max_stock_adds, calls}` nên mọi con số ở đây đều truy được:

| | array | concat | set_stock_count |
|---|---|---|---|
| Arena player | 22736128 | 22736348 | 22736376 |
| Arena drone | 22772312 | 22772536 | 22772564 |
| Arena resource | 22773492 | 22773716 | 22773744 |
| PVP player | 19945024 | 19945248 | 19945276 |
| PVP drone | 19945924 | 19946148 | 19946176 |
| PVP resource | 19947104 | 19947328 | 19947356 |

Chỗ này khớp 156: bộ đếm là **pref** (162), còn số hiển thị là `trần − đã bán`, nên sau khi mua ô hiện đúng phần còn lại chứ không hiện số đã bán.

---

## 9. Đối chiếu và những gì đổi so với các báo cáo trước

| báo cáo | điều đã pin | lượt này |
|---|---|---|
| 159 | `SetPopup(index, rewards, action)`; `OnPressedButtonBuy` so ví rồi `blr x9` | **đóng** open item "cần bảng token": đích là `b__N`, suy ra từ cấu trúc lớp |
| 160 | bậc rẽ `0xc7 / 0x12b`, 4 `Shop_Pack` + 4 `EventRewards` mỗi shop | khớp: mỗi nhánh dựng `Shop_Pack` + `EventRewards` rồi mới dựng delegate |
| 162 | `ResetShop` ghi `catalogue − 10001` cho dải player | **khứ hồi**: closure player cộng lại `10001` trước khi index `PlayerCards` |
| 156 | sáu closure tăng bộ đếm đã bán | khớp: cả sáu đều `SetStockItem(id, snapshot + count)` |
| 153 | `itemCost` là giá gói | **làm rõ**: player/drone dán `value × cost`; resource đọc thẳng bảng giá |

---

## 10. Giới hạn và open item

| open item | vì sao chưa đóng |
|---|---|
| popup có thể truyền `count = 0` không | lambda no-op khi `count < 1`, 154 thấy slider khởi tạo 1; có đường runtime nào hạ xuống 0 không là `MODEL_NOT_MEASURED runtime` |
| hai catalogue chứa gì | thiên lệch `10001 / 20001` cho thấy chỉ số thẻ nằm trong hai dải đó, nhưng danh sách được nạp từ save lúc reset — `MODEL_NOT_MEASURED runtime` |
| vì sao một trong ba `.ctor` bị gộp vào `Object..ctor` | thân rỗng, gộp là lựa chọn codegen; lớp vẫn xác định được bằng phép trừ + vật phẩm closure cộng |
| tràn 32-bit ở `itemCost × count` | `msub`/`madd` là 32-bit và cả hai toán hạng đều từ dữ liệu — `MODEL_NOT_MEASURED runtime` |
| field `Shop_Pack +0x48/+0x4c` và `+0x10/+0x2c/+0x44` | ngoài phạm vi lượt này (160 đã đếm bốn hàm dựng); chưa pin vào artifact |

---

## 11. Cách tái lập

```bash
python3 tools/verify/buy_delegate.py          # 43 check, ghi lại datas/l2_535b0541_buy_delegate.json.gz
python3 -m unittest tests.test_buy_delegate   # 52 test
python3 tools/verify-claims.py                # chạy toàn bộ claim, gồm APKD1/AI1
```

Đọc lại từ artifact: `shops[<shop>].bands[<dải>].{class_cell,method_cell,delegate,lambda_,closure}`. Mọi RVA trong tài liệu này là **thập phân** và lấy nguyên từ artifact; chuỗi hex chỉ dùng cho địa chỉ cell tĩnh.
