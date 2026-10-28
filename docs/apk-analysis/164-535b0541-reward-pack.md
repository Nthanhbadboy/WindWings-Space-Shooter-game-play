# 164 — Từ `Shop_Pack` tới hàng thưởng popup hiện: bốn pack, ba `EventRewards` sống, một bị bỏ

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + 8 slice + `dump.cs` đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Bảng field, giá trị nhúng trong `.ctor`, phép nhân giá và chín pad của `SetEventRewardTabs` là hằng lúc build; **index nào rơi vào pad nào**, **ba float `.rodata`**, **pack bị bỏ có ai đọc không** và **một pack hai slot** là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_reward_pack.json.gz` (9181 B, sha256 `be544db4d0f55a8cc45276264c078726cea4eff0715186210299a991a9ce8626`)
**Báo cáo trước:** 163 (lambda `b__N` của `Action<int>`), 162 (khoá PlayerPrefs), 160 (cây chọn dải, đếm 4 pack + 4 `EventRewards`), 159 (chuỗi popup), 157 (hằng kinh tế trong `.ctor`), 129 (bảng index của `Shop_Pack`).
**Verifier:** `tools/verify/reward_pack.py` (~1,4 s, 82 check) · **Test:** `tests/test_reward_pack.py`.

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| `Shop_Pack` có bao nhiêu field? | **28** `int`, `0x10 … 0x7C`; **27** field có index `0..26`, chỉ `multipleBonus` (`0x7C`) không có | §2 |
| Một cú bấm dựng mấy pack? | **4** pack mỗi shop — nhưng chỉ **3** cặp `EventRewards` sống | §3 |
| Dải player ghi gì? | `+0x4C PlayerCards = itemId + 1` | §3 |
| Dải drone ghi gì? | `+0x48 DroneCards = itemId + 1` | §3 |
| Dải resource ghi gì? | **một trong ba** `+0x10 Gcoins` / `+0x2C Energy` / `+0x44 DroneExp` = `itemValue` | §3 |
| `number` / `price` / `stock` của `EventRewards` lấy ở đâu? | player `ItemPlayerValue`/`ItemPlayerCost`; drone `ItemDroneValue`/`ItemDroneCost`; resource-wallet `itemValue`/`itemCost` (closure); `stock` **luôn** `MaxStockCount` | §4 |
| `itemCost` của dải resource từ đâu? | `ItemResourceCost[cell.id − 300]`, `itemValue` = `ItemResourceValues[cell.id − 300]` | §4 |
| Pack thứ tư là gì, và tại sao vô hình? | một pack `DroneCards` dựng sớm trên nhánh resource, có `EventRewards(…ItemDroneValue, ItemDroneCost…)` nhưng con trỏ **không được copy khỏi `x0`** ⇒ bị bỏ | §5 |
| Popup hiện giá thế nào? | `String.Format(fmt, rewards.price × count)` → `textCost`; `count = 1` | §6 |
| Popup tính tồn thế nào? | `maxStock = rewards.stock − GetStockItem(index)` → `textStock` (`count/maxStock`), slider `maxValue = maxStock − 1`, `step = 1`, `Value(0)`, ẩn khi `maxStock ≤ 1` | §6 |
| `SetEventRewardTabs` vẽ gì? | **đúng một** hàng: `GetListIndexRewards(pack)[0]`, icon index `value − 1`, nhảy bảng **21** mục tại VA `0x779E50` vào **9** pad | §7 |
| Chín pad khác nhau ở đâu? | box sprite = `GetBoxSpriteGeneral(k)`; icon = `allSpriteRewards` / `listSpriteDrones` / `listSpritePlayers` / `itemRandomSprite`; chỉ 2 pad set `_isCards` | §8 |

**Một câu:** mỗi cú bấm dựng bốn `Shop_Pack`, dán vào mỗi pack đúng một field (dải thẻ: `itemId + 1`; dải resource: một trong ba field ví = `itemValue`), bọc ba pack bằng `EventRewards(pack, number, price, MaxStockCount)` — pack thứ tư bị bỏ vì kết quả cấp phát không được giữ — rồi `SetPopup` in `price × count` lên `textCost`, tính `maxStock` từ `GetStockItem`, và `SetEventRewardTabs` chỉ vẽ **một** hàng trên chín pad.

---

## 1. Vì sao cần báo cáo này

163 đóng câu hỏi "`Action<int>` trỏ vào lambda nào", nhưng để lại nguyên văn hai dòng mở: *"field `Shop_Pack +0x48/+0x4c`"* và *"`+0x10/+0x2c/+0x44`"* chưa được pin — tức là chưa ai nói **field nào** cú bấm ghi, và 160 đếm **bốn** `Shop_Pack` + **bốn** `EventRewards` mỗi shop mà chưa giải thích cặp thứ tư để làm gì. Lượt này trả lời cả hai từ byte đã pin, rồi đi thêm một bước: từ pack → `EventRewards` → hàng thưởng mà `SetEventRewardTabs` thực sự vẽ.

Phạm vi: `Shop_Pack` (bảng field), bốn site `Shop_Pack..ctor` và bốn site `EventRewards..ctor` mỗi shop, `Popup_{Arena,PVP}ShopExchange.SetPopup` + `SetEventRewardTabs`. **Không** mở lại giá ba dải (158), chuỗi popup (159), cây chọn dải (160), bộ đếm đã bán (156), khoá PlayerPrefs (162), lambda (163).

---

## 2. `Shop_Pack`: 28 field, 27 field có index

`Shop_Pack` khai báo **28** `public int`, từ `0x10 Gcoins` tới `0x7C multipleBonus`. Báo cáo này **không** suy lại thứ tự index: 129 đã pin `GetValueByIndex` (27 mục, `0..26` ↔ `0x10..0x78`), và verifier so `index_order` của 129 với bảng field đọc trực tiếp từ `dump.cs` — hai nguồn khớp từng dòng.

| # | field | offset | # | field | offset | # | field | offset |
|---|---|---|---|---|---|---|---|---|
| 0 | `Gcoins` | `0x10` | 10 | `DeviceA` | `0x38` | 20 | `VipPoint` | `0x60` |
| 1 | `Gems` | `0x14` | 11 | `DeviceS` | `0x3C` | 21 | `TimeRewards` | `0x64` |
| 2 | `Item0` | `0x18` | 12 | `DeviceSS` | `0x40` | 22 | `ArenaMedal` | `0x68` |
| 3 | `Item1` | `0x1C` | 13 | `DroneExp` | `0x44` | 23 | `PvPMedal` | `0x6C` |
| 4 | `Item2` | `0x20` | 14 | `DroneCards` | `0x48` | 24 | `TryDrone` | `0x70` |
| 5 | `Item3` | `0x24` | 15 | `PlayerCards` | `0x4C` | 25 | `TryShip` | `0x74` |
| 6 | `Overdrive` | `0x28` | 16 | `Key0` | `0x50` | 26 | `Premium` | `0x78` |
| 7 | `Energy` | `0x2C` | 17 | `Key1` | `0x54` | — | `multipleBonus` | `0x7C` |
| 8 | `DeviceC` | `0x30` | 18 | `Key2` | `0x58` | | | |
| 9 | `DeviceB` | `0x34` | 19 | `WingCoins` | `0x5C` | | | |

Ba field đáng nhớ nhất là `22 ArenaMedal` / `23 PvPMedal` — đúng hai loại huy chương mà popup hiện số dư — và `7 Energy`, `13 DroneExp`, `0 Gcoins` là ba field ví mà dải resource ghi. Bảng đầy đủ 28 dòng nằm trong artifact tại `pack_table.fields` (mỗi dòng có `name`, `offset`, `index`, `nine_table_offset`). Điều cần nhớ: **`0x48 DroneCards` và `0x4C PlayerCards`** là hai field mà 163 treo lại, và `0x10/0x2C/0x44` là ba field ví.

---

## 3. Bốn pack mỗi shop, và field mỗi pack ghi

Mỗi shop dựng đúng **bốn** `Shop_Pack` (khớp 160) bằng `bl 0x1341298`, và mỗi pack ghi **một** field — trừ pack ví ghi **một trong ba**:

| site `Shop_Pack..ctor` (Arena / PVP) | dải | field ghi | giá trị | site `str` |
|---|---|---|---|---|
| 22733720 / 19942612 | resource | `+0x48 DroneCards` | `itemId + 1` | 22733752 |
| 22733824 / 19942716 | resource | `+0x10 Gcoins` **hoặc** `+0x2C Energy` **hoặc** `+0x44 DroneExp` | `itemValue` | 22733844, 22734440, 22734448 |
| 22734004 / 19942896 | player | `+0x4C PlayerCards` | `itemId + 1` | 22734036 |
| 22734304 / 19943196 | drone | `+0x48 DroneCards` | `itemId + 1` | 22734336 |

Ba chỗ đáng chú ý:

1. **Hai pack cùng ghi `DroneCards`.** Dải drone ghi `+0x48` một cách thẳng; nhánh resource cũng ghi `+0x48` trên một pack khác (pack bị bỏ, §5). Đọc "field" không đủ để nói "hàng nào" — phải đọc **pack nào tới được popup**.
2. **Pack ví ghi một trong ba.** Cùng một pack (`x22` ở Arena 22733824) nhưng ba `str` nằm trên ba nhánh loại trừ nhau, chọn bằng `cmp w21, #0x12C` (22733832) và `cmp w21, #0x12D` (22734432): `id = 300 → Gcoins`, `id = 301 → Energy`, còn lại `→ DroneExp`. Đây là cùng bậc `300/301` mà 163 thấy ở closure (`id_branches`), nên hai chỗ khớp nhau.
3. **`itemId + 1`.** Cả ba pack thẻ đều cộng 1 vào `cell.itemId` (`add w8, w8, #1`) trước khi ghi. Vì sao `+1` (chứ không phải id thô) là câu của báo cáo 129/162 về catalogue; ở đây chỉ pin **có** phép cộng và **toán hạng** của nó (`ldr w8, [x8, #0x1C]`, tức `cell.itemId`).

---

## 4. `EventRewards(pack, number, price, stock)`: bốn cặp, ba nguồn số

`Board_EventSeasonPass.EventRewards` có bốn field: `pack 0x10`, `number 0x18`, `price 0x1C`, `stock 0x20`. Constructor `.ctor(Shop_Pack, int, int, int)` = `0x12901B4` (19464628). Mỗi shop gọi nó **bốn** lần:

| `EventRewards` (Arena / PVP) | dải | pack | `number` | `price` | `stock` | số phận |
|---|---|---|---|---|---|---|
| 22733792 / 19942684 | resource | pack `DroneCards` | `ItemDroneValue` | `ItemDroneCost` | `MaxStockCount` | **bị bỏ** |
| 22734080 / 19942972 | player | pack `PlayerCards` | `ItemPlayerValue` | `ItemPlayerCost` | `MaxStockCount` | sống |
| 22734380 / 19943272 | drone | pack `DroneCards` | `ItemDroneValue` | `ItemDroneCost` | `MaxStockCount` | sống |
| 22734492 / 19943384 | resource | pack ví | `itemValue` | `itemCost` | `MaxStockCount` | sống |

Bốn nguồn số, đúng như byte:

- **`ItemPlayerValue` / `ItemPlayerCost`** — `ldp w24, w23, [x19, #0x9C]` rồi `mov w2, w24; mov w3, w23`. Hai field kinh tế của `Arena_Shop`, 157 đã pin giá trị nhúng `1` và `50`.
- **`ItemDroneValue` / `ItemDroneCost`** — `ldp w22, w23, [x19, #0xA4]`, `1` và `30`.
- **`MaxStockCount`** — `ldr w24, [x19, #0x98]` (drone: `w25`), giá trị nhúng `10`. Cả bốn cặp đều dùng đúng field này, không cặp nào đọc `stock` từ chỗ khác.
- **`itemValue` / `itemCost`** — hai field `0x14` / `0x10` của closure `<>c__DisplayClass31_3` (dải resource), nên cặp thứ tư **không** đọc field kinh tế của shop.

Closure đó được nhồi ngay đầu nhánh resource:

```
ldr x8, [x21, #0x18]        ; cell.id
sub w8, w8, #0x12c          ; id - 300
ldr x9, [x19, #0xb8]        ; ItemResourceCost  (int[3])
ldr w9, [x9, #0x20]         ; [id - 300]
str w9, [x20, #0x10]        ; itemCost
ldr x9, [x19, #0xb0]        ; ItemResourceValues (int[3])
ldr w8, [x8, #0x20]         ; [id - 300]
str w8, [x20, #0x14]        ; itemValue
```

⇒ `itemCost = ItemResourceCost[cell.id − 300]`, `itemValue = ItemResourceValues[cell.id − 300]`. Hai mảng này là `int[3]` mà 157 đã thấy được khởi tạo trong `.ctor`; 300/301/302 là ba ô `0..2`.

**Hệ quả về giá.** Với dải thẻ, `price` là `ItemPlayerCost = 50` **thô**, còn closure dán `itemCost = ItemPlayerValue × ItemPlayerCost = 50` (163 §6). Ở giá trị nhúng `1` hai số bằng nhau; nếu designer đặt `ItemPlayerValue > 1` thì popup in `50 × count` trong khi ví bị trừ `(value × 50) × count` — popup in thiếu đúng `value` lần. Dải resource thì **không** lệch: `price` của nó đã là `ItemResourceCost[id − 300]`, tức giá một đơn vị, nên `price × count` bằng đúng `itemCost × count` mà lambda trừ.

---

## 5. Pack thứ tư: dựng, bọc, rồi bỏ

Trên nhánh resource, trước khi dựng pack ví, code dựng thêm một pack `DroneCards` và một `EventRewards` cho nó:

```
22733708 bl 0x110d240        ; cấp phát
22733716 mov x21, x0         ; giữ pack
22733720 bl 0x1341298        ; Shop_Pack..ctor
22733732 cbz x21, …
22733752 str w8, [x21, #0x48]; DroneCards = itemId + 1
22733760 ldp w22, w23, [x19, #0xa4]   ; ItemDroneValue, ItemDroneCost
22733768 bl 0x110d240        ; cấp phát EventRewards
22733772 mov x1, x21         ; arg1 = pack
22733776 mov w2, w22         ; number
22733780 mov w3, w23         ; price
22733784 mov w4, w24         ; stock
22733792 bl 0x12901b4        ; EventRewards..ctor
22733796 ldr x8, [x20, #0x18]; ← không hề đọc lại x0
```

`EventRewards..ctor` nhận `this` trong `x0`; muốn giữ object thì phải copy `x0` sang thanh ghi callee-saved **trước** lời gọi. Ở ba cặp còn lại đều có (`mov x21, x0` ngay sau `bl 0x110d240` — Arena 22734076, 22734376, 22734488). Ở cặp này **không** có: `x0` bị `ldr x0, [x25]` ghi đè ngay sau. Verifier định nghĩa `kept = có `mov xK, x0` nằm giữa lệnh cấp phát và lời gọi ctor` — đúng phép thử này, và đúng **một** trong bốn cặp mỗi shop trượt.

**Đây là lý do phải đi theo luồng điều khiển.** Pack ví được dựng **sớm** (22733824) nhưng `EventRewards` của nó nằm tận **đuôi dùng chung** (22734492), sau cả ba nhánh; nếu quét cửa sổ lệnh liền kề thì pack ví bị gán nhầm cho `EventRewards` của nhánh player. Cùng lý do: `str` vào pack ví nằm ở 22733844 **và** 22734440/22734448 — hai chỗ cách nhau 600 byte nhưng cùng một pack.

Hệ quả thực tế: popup chỉ nhận **ba** hàng — player, drone, ví. Hàng "drone card" mà nhánh resource dựng ra không bao giờ tới `SetPopup`. Đọc bảng `EventRewards` mà không xét `kept` sẽ kết luận sai rằng dải resource bán drone card.

---

## 6. `SetPopup`: bốn field, giá, tồn, slider

`Popup_ArenaShopExchange.SetPopup(int index, EventRewards eventReward, Action<int> exit)` = **22835700** (932 B); `Popup_PVPShopExchange` = 19888660 (928 B). Bốn store vào `this` (`x19`, có hai bản sao pre-index `x21`/`x22`):

| field | offset | op | RVA | nghĩa |
|---|---|---|---|---|
| `onExit` | `0x50` | `str x22, [x19, #0x50]` | 22836040 | `Action<int>` của dải (163) |
| `count` | `0x58` | `str w8, [x22, #0x58]!` với `mov w8, #1` | 22836112 | **luôn 1** |
| `rewards` | `0x60` | `str x20, [x22, #8]` (x22 = this+0x58) | 22836116 | cặp `EventRewards` sống |
| `maxStock` | `0x5C` | `str w8, [x21, #0x5C]!` | 22836164 | tồn còn lại |

**Giá hiện trên `textCost` (`0x30`).** `rewards.price` đọc ở 22836172 (`ldr w9, [x20, #0x1C]`), `count` đọc lại qua `ldur w8, [x21, #-4]` (= `this+0x58`), nhân ở 22836188 (`mul w8, w9, w8`), rồi `String.Format(fmt, value)` ở 22836216 ghi lên `textCost`. Vì `count` luôn `1`, con số hiện ra **bằng đúng `price`**; nó chỉ khác khi ai đó ghi `count` khác 1, mà đường code duy nhất ghi `count` là store ở trên.

**Tồn còn lại.** `GetStockItem(index)` gọi ở 22836152, trừ ở 22836156 (`sub w8, w23, w0`) với `w23 = ldr w23, [x20, #0x20]` = `rewards.stock` (nhúng `10`), ghi vào `maxStock` ở 22836164. `textStock` (`0x28`) dựng lại thành mảng 5 phần tử qua `String.Concat` (22836428): `GetText(key)` + `"/"` + `count` + `"/"` + `maxStock` — tức ô hiện **"1/tồn"**.

**Slider.** `if (maxStock > 1)`: `step = 0x3F800000` (1.0f, 22836560), `maxValue = float(maxStock − 1)` (22836564 `sub` → 22836568 `scvtf` → 22836572), `Value(0)` (22836580). Cổng là `cmp w20, #1` + `b.le` ở 22836520, và nhánh ≤ 1 gọi `SetActive(false)` ở 22836588; PVP y hệt nhưng thanh ghi là `w21` (`cmp w21, #1` ở 19889476).

**Thứ tự.** `SetEventRewardTabs()` (22836464) → `get_gameObject` + `SetActive(true)` (22836492, cho chính popup) → `SetActive(true/false)` cho slider → `set_Value(0)`. Verifier kiểm tra đúng thứ tự này trên danh sách lời gọi.

**Nhãn tiền tệ.** `get_ArenaMedal()` (22835976) → `ToString` → `textCoinEvent` (`0x38`) ở 22836036; PVP dùng `get_PvPMedal`. Đây là số dư huy chương hiện ở góc popup, không phải giá.

---

## 7. `SetEventRewardTabs`: một hàng, bảng 21 mục, chín pad

`Popup_ArenaShopExchange.SetEventRewardTabs()` = **22836632** (1088 B), PVP = 19889752. Bốn bước:

1. `rewards = this.rewards` (`ldr x8, [x21, #0x60]`), `pack = rewards.pack` (`ldr x19, [x8, #0x10]`).
2. `array = Shop_Pack.GetListIndexRewards(pack)` (22836736) — 129 đã pin hàm này. `ldr w8, [x0, #0x18]` = độ dài; `cbz w8` ⇒ pack rỗng thì **không vẽ gì**.
3. `index = array[0]` (`ldr w20, [x0, #0x20]`, 22836760) — **chỉ phần tử đầu**. `value = GetValueByIndex(pack, index)` (22836780), `iconIndex = value − 1` (`sub w22, w0, #1`, 22836812).
4. `cmp w20, #0x15` + `b.hi` (22836784/22836788) ⇒ bảng nhảy **21** mục tại VA `0x779E50` (`adrp x8, #0x779000` + `add x8, x8, #0xe50`), nhảy bằng `br x9`.

Vì chỉ vẽ `array[0]`, **một pack hai slot khác 0 sẽ chỉ hiện slot đầu** — và mọi pack do click dựng đều chỉ ghi một field, nên trường hợp đó không có đường phát sinh trong code đã pin.

**Bảng nhảy không nằm trong raw đã pin.** Đây là open item **duy nhất** của phần này: `0x779E50` là `.rodata`, workspace không có `libil2cpp.so` gốc, nên không thể pin 21 byte ánh xạ **index → pad**. Chín pad thì đo được đầy đủ (§8); chỉ các **cạnh** index→pad là thiếu.

---

## 8. Chín pad: box sprite, icon, số, `_isCards`, scale

Mỗi pad kết thúc bằng một `b` (hoặc `b` đuôi) vào chuỗi nạp đối số chung rồi `b 0x1310880` = `Box_Rewards.SetInfo(Sprite _boxSpr, Sprite _iconSpr, int _number, bool _isCards = False, float _scaleIcon = 1, string _strBonus)`. Đọc đúng đường đi của từng pad (BFS ngắn nhất tới lời gọi `SetInfo`) cho bảng sau:

| pad `pad_rva` | `bl GetBoxSpriteGeneral` | `_boxSpr` | `_iconSpr` | `_number` | `_isCards` | `_scaleIcon` |
|---|---|---|---|---|---|---|
| 22836820 | 22836856 | `GetBoxSpriteGeneral(index)` | `allSpriteRewards[index]` | `rewards.number` | false | `.rodata 0x756C14` |
| 22836920 | 22836956 | `GetBoxSpriteGeneral(index)` | `allSpriteRewards[index]` | `rewards.number` | false | 1.0 |
| 22837020 | 22837056 | `GetBoxSpriteGeneral(index)` | `itemRandomSprite` | `rewards.number` | false | `.rodata 0x756CAC` |
| 22837120 | 22837156 | `GetBoxSpriteGeneral(6)` | `allSpriteRewards[6]` | `rewards.number` | false | `.rodata 0x756F10` |
| 22837220 | 22837256 | `GetBoxSpriteGeneral(0xE)` | `listSpriteDrones[value − 1]` | `rewards.number` | **true** | 1.0 |
| 22837288 | 22837324 | `GetBoxSpriteGeneral(0xF)` | `listSpritePlayers[value − 1]` | `rewards.number` | **true** | 1.0 |
| 22837400 | 22837436 | `GetBoxSpriteGeneral(0x13)` | `allSpriteRewards[19]` | `rewards.number` | false | 1.25 |
| 22837488 | 22837524 | `GetBoxSpriteGeneral(0x14)` | `allSpriteRewards[20]` | `rewards.number` | false | 1.5 |
| 22837584 | 22837620 | `GetBoxSpriteGeneral(0x15)` | `allSpriteRewards[21]` | `rewards.number` | false | 1.25 |

(`index` = `GetListIndexRewards(pack)[0]`, giá trị trong `w20`; `value − 1` là `w22`.)

Ba pad đầu truyền **chính index** cho `GetBoxSpriteGeneral` — đó là lý do nội dung icon phụ thuộc slot nào khác 0. Sáu pad còn lại truyền **hằng** `6 / 0xE / 0xF / 0x13 / 0x14 / 0x15`, tức sáu loại thưởng được vẽ bằng khung riêng.

Hai pad `0xE` và `0xF` là **hai pad thẻ**, và chúng chia sẻ đúng một khối cuối (`0x15C7868` = byte 22837352): cả hai đều `_isCards = true`, `_scaleIcon = 1.0`, icon lấy từ `listSpriteDrones[value − 1]` / `listSpritePlayers[value − 1]`. Vì `value` chính là `Shop_Pack` field mà click vừa ghi (`DroneCards = itemId + 1`, `PlayerCards = itemId + 1`), `value − 1` quay lại **đúng `cell.itemId`** — tức index sprite của thẻ. Đây là chỗ hai báo cáo khớp nhau: `+1` lúc ghi, `−1` lúc vẽ.

`_number` luôn là `w19 = ldr w19, [x8, #0x18]` với `x8 = this.rewards` ⇒ **`EventRewards.number`**. Với dải thẻ số này là `1`; với dải ví là `ItemResourceValues[id − 300]`.

Ba scale đọc từ `.rodata`: `0x756C14`, `0x756CAC`, `0x756F10`. **Giá trị float chưa biết** — cần byte `.so`, workspace không có. Năm pad còn lại dùng `fmov s0, #1.0 / #1.25 / #1.5`, đọc thẳng từ lệnh.

PVP: chín pad **giống từng ô** (cùng `box_arg`, `icon`, `is_cards`, `scale`), chỉ khác RVA — verifier so hai danh sách và chúng bằng nhau.

---

## 9. Đối chiếu và những gì đổi so với các báo cáo trước

| báo cáo | điều đã pin | lượt này |
|---|---|---|
| 163 | `+0x48/+0x4C` chưa xác định; lambda `b__1/b__3/b__5`; closure dán `itemCost = value × cost` | **đóng**: `0x48 DroneCards`, `0x4C PlayerCards` (thêm `0x10/0x2C/0x44` cho ví); closure resource dán **giá bảng**, không nhân |
| 160 | 4 `Shop_Pack` + 4 `EventRewards` mỗi shop | **giải thích**: pack thứ tư có `EventRewards` nhưng bị bỏ ⇒ chỉ 3 hàng tới popup |
| 157 | `ItemPlayerValue 1`, `ItemPlayerCost 50`, `ItemDroneValue 1`, `ItemDroneCost 30`, `MaxStockCount 10` | **dùng làm `number/price/stock`**: 12/16 tham số là field kinh tế, 4 tham số `stock` đều `MaxStockCount` |
| 129 | `GetValueByIndex` 27 mục `0x10..0x78` | **tái dùng**, không suy lại; thêm `multipleBonus 0x7C` là field duy nhất không index |
| 162 | bộ đếm đã bán là PlayerPref | **khớp**: popup đọc lại `GetStockItem(index)` mỗi lần mở, không cache `stock` |
| 159 | `SetPopup(index, rewards, action)` | **khớp**: bốn store đúng bốn field, `count = 1`, giá = `price × count` |
| 154 | slider khởi tạo `1` | **khớp**: `step = 1.0f`, `maxValue = maxStock − 1`, `Value(0)`, ẩn khi `maxStock ≤ 1` |

---

## 10. Giới hạn và open item

| open item | vì sao chưa đóng |
|---|---|
| index nào rơi vào pad nào | 21 byte bảng nhảy tại VA `0x779E50` không có trong raw đã pin, và APK gốc không có trong workspace ⇒ không pin được cửa sổ `.rodata` mới (cấm sinh raw mới). Chín pad **đã** đo; chỉ cạnh index→pad là thiếu |
| ba float `0x756C14 / 0x756CAC / 0x756F10` | đọc bằng `ldr s0, [xN, #…]`; thiếu `.so` nên chưa biết giá trị, dù năm pad khác dùng `fmov` |
| pack bị bỏ có ai đọc không | trong `OnClickPlayerItem` thì chứng minh được là không dùng; còn caller khác đọc thì là `MODEL_NOT_MEASURED runtime` |
| một pack hai slot khác 0 | `SetEventRewardTabs` chỉ vẽ `array[0]`, và mọi pack do click dựng đều ghi đúng một field ⇒ không có đường phát sinh — `MODEL_NOT_MEASURED runtime` |
| lớp display class thật của dải player | đường player cấp closure qua `Object::.ctor` (ctor rỗng bị inline) trong khi drone/resource gọi thẳng `<>c__DisplayClass31_2` / `_3`; layout `itemCost 0x10 / itemValue 0x14 / CS$<>8__localsN 0x18` giống nhau ở cả ba, và 163 đã pin `_1` cho lambda player |
| `ItemResourceValues` / `ItemResourceCost` chứa gì | chỉ biết chúng là `int[3]` khởi tạo trong `.ctor` (157); nội dung là dữ liệu serialize — `MODEL_NOT_MEASURED runtime` |

---

## 11. Cách tái lập

```bash
python3 tools/verify/reward_pack.py              # 82 check, ghi lại datas/l2_535b0541_reward_pack.json.gz
python3 -m unittest tests.test_reward_pack       # test của báo cáo này
python3 -m unittest discover -s tests            # toàn bộ
python3 tools/verify-claims.py                   # chạy toàn bộ claim, gồm APKD1/AI1
```

Đọc lại từ artifact: `shops[<shop>].packs[i]` (site ctor, field ghi, giá trị, `event_rewards`), `shops[<shop>].rewards[i]` (`bands`, `number`, `price`, `stock`, `kept`), `shops[<shop>].popup` (bốn store, `cost`, `remaining`, slider), `shops[<shop>].tabs` (`picks`, `dispatch`, `pads`). Mọi RVA trong tài liệu này là **thập phân** và lấy nguyên từ artifact; chuỗi hex chỉ dùng cho địa chỉ VA/rodata và offset field.
