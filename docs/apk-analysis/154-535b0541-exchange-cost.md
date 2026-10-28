# 154 — Popup đổi thưởng: HAI loại tiền, MỘT công thức giá, và phần trừ tồn kho

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + dump/metadata đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Công thức giá, hai ví, và luật tồn kho là hằng lúc build; **một season bán món gì với giá bao nhiêu** là `MODEL_NOT_MEASURED runtime` vì hàng nằm trong dữ liệu event-pass.
**Artifact:** `datas/l2_535b0541_exchange_cost.json.gz` (4086 B, sha256 `e4045686828975f40fb1d75a941acadae9ff1d275932a166d63965a84a315d83`)
**Báo cáo trước:** 153 (khoá `ARENA_SHOP_ITEM_*`, `GetStockItem` +0x98 `MaxStockCount`), 151 (`rewards` của `Board_EventSeasonPass`), 149/130/133 (thang thưởng hunter).
**Verifier:** `tools/verify/exchange_cost.py` (~9,2 s) · **Test:** `tests/test_exchange_cost.py` (38 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| Popup đổi thưởng dùng tiền nào? | **hai ví khác nhau**: `Popup_PVPShopExchange` → `GameDatas.get_PvPMedal` (20085132), `Popup_ArenaShopExchange` → `GameDatas.get_ArenaMedal` (20084804) | §2 |
| Giá một món là số hằng? | **Không** — `cost = price × count`, `count = round(slider.value / slider.step)` | §3 |
| Chia theo `maxValue` hay `step`? | **theo `step`** — offset **+0x64**, không phải `maxValue` +0x60 | §3 |
| Làm tròn kiểu gì? | `Math.Round` mặc định ⇒ **half-to-even**, thấy rõ qua cặp `tst x8,#1` + `fcsel` | §3 |
| Trần mua lấy từ đâu? | `maxStock (+0x5C) = rewards.stock (+0x20) − Shop.GetStockItem(index)` — đúng khoá 153 đã giải | §4 |
| Popup có trừ medal không? | **Không** — chỉ `onExit(count)` rồi `SetActive(false)`; không có setter ví nào | §5 |
| Hai popup là hai implementation? | **Không** — 11 field trùng khít, 8 method, chỉ `SetPopup` lệch **4 byte** | §6 |
| Ai gọi `SetPopup`? | **không có caller** trong 8 slice đã dump (kể cả `arena-pvp`) | §8 |
| Chỉ có hai popup như vậy? | **Không** — còn `Popup_Exchange` (693) cùng 11 field nhưng `SetPopup` **5 tham số**, nằm **ngoài** mọi slice | §7 |

**Một câu:** popup đổi thưởng không bán "một món giá X" — nó bán **một dòng `EventRewards` theo bước trượt**, tính `price × count` tại chỗ, chặn bằng tồn kho còn lại của cửa hàng, rồi **trả số lượng về cho hàm gọi** và để phần trừ ví cho nơi khác.

---

## 1. Vì sao cần báo cáo này

153 để lại đúng một câu hỏi mở: *"the exchange popup's medal price"*. Báo cáo đó đọc được `GetStockItem`/`SetStockItem` nhưng dừng ở ranh giới popup. Lượt này mở đúng ranh giới đó — 2 class `Popup_*ShopExchange`, 8 method mỗi bên, 1 field ẩn `EventRewards`.

Spec lần 114 xếp follow-up 20 của 535 trong ceiling, nên đây là lượt kế tiếp hợp lệ, không mở lane mới.

---

## 2. Hai popup, hai ví

`Popup_PVPShopExchange` (TypeDefIndex **875**) và `Popup_ArenaShopExchange` (**466**) khai báo **11 field giống nhau từng offset**:

| offset | field | kiểu | serialized |
|---|---|---|---|
| +0x20 | `textHeader` | `TextMeshPro` | có |
| +0x28 | `textStock` | `TextMeshPro` | có |
| +0x30 | `textCost` | `TextMeshPro` | có |
| +0x38 | `textCoinEvent` | `TextMeshPro` | có |
| +0x40 | `btnIcon` | `SpriteRenderer` | có |
| +0x48 | `slider` | `Slider` | có |
| **+0x50** | `onExit` | `Action<int>` | không |
| **+0x58** | `count` | `int` | không |
| **+0x5C** | `maxStock` | `int` | không |
| **+0x60** | `rewards` | `Board_EventSeasonPass.EventRewards` | không |
| +0x68 | `boxReward` | `Box_Rewards` | có |

Chỉ **một** khác biệt thật, ở ví — đọc từ lệnh, không đoán:

| popup | setter | rva lệnh | target |
|---|---|---|---|
| `Popup_PVPShopExchange` | `GameDatas.get_PvPMedal()` | 19888936 (SetPopup) / 19888552 (OnChange) / 19891004 (Buy) | **20085132** |
| `Popup_ArenaShopExchange` | `GameDatas.get_ArenaMedal()` | 22835976 / 22835592 / 22837884 | **20084804** |

Hai ví này **không** phải cùng một ô nhớ: `get_PvPMedal` và `get_ArenaMedal` là hai static getter riêng (20085132 ≠ 20084804). Nghĩa là popup PvP tiêu medal PvP, popup Arena tiêu medal Arena — cùng một khung UI, hai economy.

---

## 3. Giá là công thức, chia theo `step`

`OnChange(float amount)` (PVP **19887764**, Arena **22834804**, cùng **896 B**) là nơi duy nhất hình thành giá:

```
count  = Math.Round(slider.value / slider.step)      // 19887940 ldr s9,[x8,#0x64]
                                                     // 19887976 fdiv s9, s8, s9
                                                     // 19888008 bl  #0x2990b70   (Math.Round)
                                                     // 19888072 tst x8, #1
                                                     // 19888076 fcsel d0,d0,d1,eq  (half-to-even)
cost   = EventRewards.price * count                  // 19888172 mul w8, w9, w8
preview= Box_Rewards.SetNumber(number * count)       // 19888500 mul w1, w8, w9  → 20001584
dim    = (wallet < cost) ? 1.0 : 0.0                 // 19888596 cmp w19, w9
                                                     // 19888612 fcsel s0,s1,s0,lt
```

Ba điểm cần nhấn:

1. **Chia cho `step`, không chia cho `maxValue`.** `Slider` giữ `maxValue` ở **+0x60** và `step` ở **+0x64**; lệnh đọc đúng **+0x64**. Nếu ai đó đọc nhanh `+0x60` sẽ ra công thức sai (giá luôn bằng `price`).
2. **Làm tròn half-to-even.** `bl 0x2990b70` là helper chưa có tên trong `dump.cs`; nhưng ngay sau nó là cặp `tst x8,#1` + `fcsel …eq`, tức tie-break về số chẵn — đúng hành vi `Math.Round` mặc định của .NET. `slider.value` là float nên `count` là **số bước trượt**, không phải `maxValue`.
3. **Preview nhân đúng `number`, không dùng `price`.** `Box_Rewards.SetNumber` (20001584) nhận `EventRewards.number (+0x18) × count` — nên hộp quà hiển thị số đơn vị người chơi thật sự nhận, còn `textCost` hiển thị `price × count`.

Dim đỏ nút mua: `btnIcon.material.SetFloat("_EffectAmount", …)` với `Renderer.get_material` **41323636** và `Material.SetFloat` **41329332**; literal duy nhất trong `slot_refs` là `'_EffectAmount'`. Nút mờ ⇒ **không đủ tiền**, đây là tín hiệu UI chứ không phải chặn logic (chặn logic ở §5).

---

## 4. Trần mua = tồn kho còn lại của cửa hàng

`SetPopup(int index, Board_EventSeasonPass.EventRewards eventReward, Action<int> exit)` (PVP **19888660** / 928 B, Arena **22835700** / 932 B):

```
19889072  str wN, [xN, #0x58]!      count = 1
19889076  str xN, [xN, #8]          this.rewards = eventReward
19889108  bl  PVP_Shop.GetStockItem (19889588)        ← khoá của 153
19889112  sub wN, wN, wN            rewards.stock − GetStockItem(index)
19889120  str wN, [xN, #0x5C]!      maxStock
19889032/19889252  LanguageManager.GetText("txt_exchange" / "txt_stock")  → 21202600
19889536  Slider.set_Value          ← 20903608
```

`EventRewards` là class lồng, **4 int sau một ref**:

| offset | field | kiểu |
|---|---|---|
| +0x10 | `pack` | `Shop_Pack` |
| +0x18 | `number` | `int` |
| +0x1C | `price` | `int` |
| +0x20 | `stock` | `int` |

Đây chính là chỗ 153 "hứa": `GetStockItem` đọc `PlayerPreferences` `<PREFIX>_ITEM_STOCK`, còn popup lấy `rewards.stock` (số build-time của season) trừ đi số đã bán. Tồn kho **không** nằm trong popup — popup chỉ *đọc* nó.

Lưu ý: popup gọi `PVP_Shop.GetStockItem` ở PVP và `Arena_Shop.GetStockItem` ở Arena (§2 `stock_read`), tức mỗi popup bám đúng cửa hàng của mình.

---

## 5. Nút mua: kiểm tra rồi trả số lượng, KHÔNG trừ ví

`OnPressedButtonBuy()` — PVP **19890912**, Arena **22837792**, cùng **184 B**:

```
19890972  ldr wN, [xN, #0x1c]       rewards.price
19890980  ldr wN, [xN, #0x58]       count
19890988  mul wN, wN, wN            cost = price × count
19891004  bl  GameDatas.get_PvPMedal        (20085132)
19891008  cmp wN, wN                wallet vs cost
19891012  b.ge                      đủ ⇒ đi tiếp, thiếu ⇒ nhảy ra
19891036  ldr w1, [xN, #0x58]       tham số cho lời gọi kế
          bl  onExit(count)         (delegate +0x50)
19891084  b   …                     → SetActive(false)
```

Trong toàn bộ 184 byte **không có** lệnh ghi vào ví và **không có** lời gọi setter nào (`set_PvPMedal`/`set_ArenaMedal`). Nghĩa là popup là **thuần UI**: nó xác nhận đủ tiền, giao `count` cho `onExit`, tự tắt — còn việc trừ medal và cộng vật phẩm do **caller của `SetPopup`** quyết định (§8).

Đây là câu trả lời thẳng cho câu hỏi mở của 153: **popup không giữ giá trị tiền tệ, chỉ giữ công thức**.

---

## 6. Sinh đôi: lệch đúng 4 byte ở `SetPopup`

| method | PVP rva / size | Arena rva / size | Δ |
|---|---|---|---|
| `.ctor` | 8 B | 8 B | 0 |
| `Exit` | 72 B | 72 B | 0 |
| `Add` | 60 B | 60 B | 0 |
| `Minus` | 56 B | 56 B | 0 |
| `OnChange` | 19887764 / 896 | 22834804 / 896 | 0 |
| `SetEventRewardTabs` | 1088 B | 1088 B | 0 |
| `OnPressedButtonBuy` | 19890912 / 184 | 22837792 / 184 | 0 |
| **`SetPopup`** | 19888660 / **928** | 22835700 / **932** | **−4** |

Lệch 4 byte này **không** phải logic khác: cùng 4 bước `guards`, cùng 2 key, cùng `Slider.set_Value`; chênh nằm ở cách nạp tham số trước `SetPopup` (`str x20,[x22,#8]` vs `str x21,[x22,#8]`) khiến nhánh `bl` dịch **+4 B** trong thân hàm. Báo cáo ghi con số, không suy ra nguyên nhân.

---

## 7. Bản thứ ba: `Popup_Exchange`

Dump có **ba** popup cùng khối 11 field. Bản thứ ba là `Popup_Exchange` (TypeDefIndex **693**), khác hai bản kia ở chỗ `SetPopup` nhận **5 tham số**:

```
public void SetPopup(int index, Board_EventSeasonPass.EventRewards eventReward,
                     Sprite[] droneCardSprites, Sprite[] shipCardSprites, Action<int> exit)   19460836
private void SetEventRewardTabs(Sprite[] droneCardSprites, Sprite[] shipCardSprites)         19469564
```

Đủ 8 method, cùng bộ tên: `OnChange` 19468668 · `SetPopup` 19460836 · `SetEventRewardTabs` 19469564 · `OnPressedButtonExit` 19470660 · `OnPressedButtonBuy` 19470732 · `OnPressedButtonMinus` 19470916 · `OnPressedButtonAdd` 19470972 · `.ctor` 19471032. Field block y hệt §2 (11 field, `rewards` +0x60 kiểu `Board_EventSeasonPass.EventRewards`).

Nhưng **không slice nào chạm tới nó**: rva thấp nhất trong 8 slice là **19586252**, cao nhất của `Popup_Exchange` là **19471032** — thấp hơn **115220 B**. Vì vậy ví của bản thứ ba **không đọc được** từ dữ liệu đã dump, và nó thành open item (§9) chứ không được suy ra từ hai bản kia. Cùng lý do, không khẳng định bản này dùng chung công thức §3 — mới chỉ thấy **cùng khối field và cùng bộ tên method**, chưa có byte nào của nó để so.

## 8. Entry point: ai mở popup thì chưa biết

Quét `bl` tới `19888660` và `22835700` trên **cả 8 slice** (`arena-pvp`, `key-grant`, `pvp-dispatch`, `meta-rewards`, `pack-index`, …): **0 caller**.

Vì vậy chuỗi "mở popup → nhận `count` → trừ medal → cộng vật phẩm" bị cắt đúng tại `SetPopup`. Điều này khớp với 153: `OnClickPlayerItem` của `Arena_Shop`/`PVP_Shop` **không** truyền lambda tiêu ví, và `popupExchange` ở +0xC0 chỉ được gán trong inspector. Kết luận trung thực: **không phải "missing", mà là "không được consultation"** — phần trừ ví nằm ngoài 8 slice đã dump, ghi thành open item, không đoán.

---

## 9. Đối chiếu và giới hạn

**Đóng được:**
- 153 `open_items` "medal price của popup đổi thưởng" → **đóng bằng công thức** (§3), không phải bằng một con số.
- Xác nhận 2 popup dùng chung một implementation, khác ví (§2, §6).
- Xác nhận popup và shop dùng **cùng một bộ đếm tồn kho** (§4).

**Không đóng được (STATIC-ONLY):**
- `price`/`number`/`stock` của từng season: `Board_EventSeasonPass.eventRewards` là mảng static nạp từ dữ liệu event-pass ⇒ `MODEL_NOT_MEASURED runtime`.
- Helper `Math.Round` ở rva **43584368**: literal `bl #0x2990b70` **không có** trong `dump.cs`, nên tên gọi chỉ suy từ call-site + cặp tie-break, **không** phải từ signature.
- Ai trừ medal sau `onExit`: `SetPopup` không có caller (§8).

**4 open item của lượt này** nằm nguyên trong artifact (`open_items`), cộng các item lane đã có từ trước và **không** bị lượt này đóng: served config value + band thật của người chơi (runtime); `MaxStockCount` +0x98 ai ghi; `LanguageManager.GetText` 21202600; bảng glyph roman 21103836; catalogue `Random.Range` chọn gì hôm nay (runtime).

---

## 10. Cách tái lập

```
python3 tools/verify/exchange_cost.py     # dựng lại artifact, in bytes + sha256 + 16/16
python3 -m unittest tests.test_exchange_cost -q   # 38 test
```

Artifact pin: **4086 B**, sha256 `e4045686828975f40fb1d75a941acadae9ff1d275932a166d63965a84a315d83`. Test `test_rebuild_reproduces_bytes` dựng lại từ `exchange_cost.build()` với `mtime=0` và so **bytes** với file trên đĩa, nên mọi thay đổi nguồn đều làm đỏ test trước khi artifact kịp trôi.
