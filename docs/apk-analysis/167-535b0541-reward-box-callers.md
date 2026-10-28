# 167 — Ai vẽ hàng thưởng: bản đồ xref của 7 method `Box_Rewards`

**Trạng thái:** `DECODED_STATIC` (chỉ đọc 8 slice + `dump.cs` đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Số call-site, class gọi, thanh ghi tham số là hằng lúc build; **giá trị float `.rodata`**, **nội dung cell `0x2ade140`** và **ý nghĩa field của từng caller** là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_reward_box_callers.json.gz` (6926 B, sha256 `7f42bf4bac4a7606dc5e194852f4800e4f65bc6b736a4dd7b16d3366dec2644b`)
**Báo cáo trước:** 166 (hộp thưởng vẽ gì), 165 (widget số lượng), 164 (`Shop_Pack` → `EventRewards` → hàng popup), 163 (lambda `Action<int>`), 161 (`dump.cs` → RVA).
**Verifier:** `tools/verify/reward_box_callers.py` (~1,3 s, **39 check**) · **Test:** `tests/test_reward_box_callers.py` (**49 test**).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| Ai gọi `SetInfo`? | **30** call-site (dedupe) trong **10** method của **8** class: 2 popup đổi, `Popup_PVPRewards`, `Board_PVP`, `TimeFreeRewardPack` (2 method), `Board_EventSeasonPass` (2 method), `Board_QuestRewards` + state machine `<OpenBox>d__43` | §3 |
| Ai gọi `SetNumber`? | **4**: hai `OnChange` (165), tail-call trong `SetInfo`, và **một** `bl` trực tiếp từ `Board_EventSeasonPass.SetEventRewardTabs` | §4 |
| Ai gọi `GetShortNumber`? | **1**: chính `SetNumber` (20001656) | §5 |
| `SetGrayScale` / `SetBoxSprite` / `SetIconSprite` / `.ctor`? | **0** call-site trong 8 slice ⇒ "chưa có trong mẫu", **không** phải "không tồn tại" | §6 |
| Tham số thật ở từng site? | `x5 = xzr` ở **cả 30** site (bonus luôn null); `_isCards` là literal ở 29 site và `cset w4, eq` ở đúng 1; `_scaleIcon` = 1.0 ×17 / 1.25 ×6 / 1.5 ×1 / cell ×5 / field ×1 | §7 |
| `number` từ đâu? | local ×19, hằng `1` ×3, field ×5, `ldr w3,[x21]` ×2, và **một** lần là kết quả `Dictionary<int,int>.get_Item` (26393436) | §8 |
| Số mà hàng nhận ở popup? | `mul w1, w8, w9` — **tích**, đúng như 165 nói (`number × count`) | §4 |
| Vì sao phải dedupe? | 8 slice **chồng nhau**: 709/1788 method xuất hiện ở ≥2 slice; 38 hit thô → **35** site | §2 |

**Một câu:** hàng thưởng không phải widget riêng của popup đổi — nó là component dùng chung cho 8 class (đổi trong shop, thưởng PvP, board nhiệm vụ, season pass, quà theo giờ), mọi nơi đều truyền bonus `null`, và cờ xám của 166 **không** đi qua `SetGrayScale` ở bất kỳ site nào trong mẫu.

---

## 1. Vì sao cần báo cáo này

166 đóng phần *vẽ*: `SetInfo` → `SetNumber` → `GetShortNumber`. Nhưng nó chỉ trả lời được "hàng trông thế nào", chưa trả lời "hàng nằm ở đâu và ai bật cờ xám" — 164/165 chỉ thấy popup đổi vì đó là nơi chúng dừng lại. Câu đó là câu hỏi xref, và 8 slice đã pin đủ để trả lời mà không cần `.so`.

Phạm vi: mọi `bl`/`b` tới 7 method của `Box_Rewards`, cộng quy ước tham số AAPCS tại từng site. **Không** mở lại giá ba dải (158), chuỗi popup (159), cây dải (160), bộ đếm đã bán (156), PlayerPrefs (162), lambda (163), `Shop_Pack`/9 pad (164), widget số lượng (165), hình thức hàng (166).

---

## 2. Mẫu và cách đếm

| Slice | Method | Ghi chú |
|---|---|---|
| `arena-pvp-535b0541` | 103 | 2 popup đổi + `Popup_PVPRewards` + `Board_PVP` |
| `box-draw-535b0541` | 103 | chính `Box_Rewards` |
| `key-grant-535b0541` | — | chồng với `Board_PVP` |
| `key-jump-535b0541` | — | chồng với `TimeFreeRewardPack` |
| `meta-rewards-535b0541` | — | chồng với `TimeFreeRewardPack` |
| `pack-index-535b0541` | — | — |
| `pvp-dispatch-535b0541` | — | — |
| `pvp-rules-535b0541` | — | — |

Sau khi gộp theo `(class, RVA)`: **1788** method duy nhất, trong đó **709** xuất hiện ở **≥2** slice. Vì vậy **38** hit thô chỉ là **35** call-site thật: 4 hit thừa là `Board_PVP.SetupHunters` (2 slice) và `TimeFreeRewardPack` ×2 method (2 slice mỗi cái).

Quy tắc dedupe: khoá `(target, class, caller, call_rva)`; mỗi dòng giữ **danh sách slice** đã thấy nó, nên chồng lấn là dữ liệu, không bị mất.

---

## 3. `SetInfo` — 30 site, 10 method, 8 class

| Class | Method (RVA) | Site | Kiểu gọi |
|---|---|---|---|
| `Popup_ArenaShopExchange` | `SetEventRewardTabs` 22836632 | 1 | **tail `b`** |
| `Popup_PVPShopExchange` | `SetEventRewardTabs` 19889752 | 1 | **tail `b`** |
| `Popup_PVPRewards` | `SetRewards` 19879636 | 2 | `bl` |
| `Board_PVP` | `SetupHunters` 19791640 | 1 | `bl` |
| `TimeFreeRewardPack` | `SetRewards` 19186068 | 1 | `bl` |
| `TimeFreeRewardPack` | `GetRewards` 19186908 | 1 | `bl` |
| `Board_EventSeasonPass` | `SetEventRewardTabs` 19439716 | 1 | `bl` |
| `Board_EventSeasonPass` | `SetRewards(int, int)` 19450080 | 8 | `bl` |
| `Board_QuestRewards` | `OnPressedButtonOpenNow` 19989112 | 1 | `bl` |
| `Board_QuestRewards.<OpenBox>d__43` | `MoveNext` 19996384 | **13** | `bl` |

Ba điểm đáng pin:

- **Chỉ hai popup đổi tail-call.** Ở đó `SetInfo` là việc cuối của `SetEventRewardTabs`, nên compiler phát `b` thay vì `bl` — khớp với 164 (popup dựng hàng cuối cùng) và giải thích vì sao 166 thấy `SetInfo` tail-call `SetNumber`.
- **State machine của board nhiệm vụ là nơi vẽ nhiều hàng nhất** (13 site trong một `MoveNext`). Đây là code sinh tự động từ `async`/iterator, không phải 13 hàng thiết kế: mỗi `case` của state machine gọi lại cùng một khối vẽ.
- **`Board_EventSeasonPass.SetRewards(int, int)` vẽ 8 hàng** — tức season pass vẽ theo cặp `(index, count)` chứ không theo danh sách pad như popup đổi.

---

## 4. `SetNumber` — 4 site, và số là một **tích**

| Caller | Site | Tham số `w1` |
|---|---|---|
| `Board_EventSeasonPass.SetEventRewardTabs` 19439716 | 19440912 | `mov w1, w25` (local), `this` = `ldr x0, [x24, #0x28]` |
| `Popup_PVPShopExchange.OnChange` 19887764 | 19888504 | **`mul w1, w8, w9`** |
| `Box_Rewards.SetInfo` 19990656 | 19991068 | `mov w1, w19` — tail `b` |
| `Popup_ArenaShopExchange.OnChange` 22834804 | 22835544 | **`mul w1, w8, w9`** |

Ở cả hai popup, `w1` được tính bằng `mul` **ngay trước** call ⇒ hàng nhận `number × count`, không phải `number`. Đây là xác nhận độc lập cho câu của 165 ("`SetNumber(rewards.number × count)`"), đo từ phía callee thay vì phía caller.

`Board_EventSeasonPass` gọi **trực tiếp** `SetNumber` (không qua `SetInfo`) — tức season pass có một hàng chỉ đổi số, không đổi sprite/scale.

---

## 5. `GetShortNumber` — đúng một caller, và `this` bị bỏ trống

Site duy nhất: `SetNumber` @ 20001656. Nhưng ở đó `x0` **không** được nạp lại sau cổng `b.lt`:

```asm
20001632  cmp  w19, #1
20001636  str  w19, [x20, #0x64]
20001640  b.lt 20001780           ; nhánh "không số"
20001644  adrp x21, #0x2ade000
20001648  ldr  x21, [x21, #0x140] ; cell 0x2ade140 (lần 1)
20001652  mov  w1, w19            ; number
20001656  bl   GetShortNumber     ; x0 vẫn là giá trị cũ
```

`GetShortNumber` **không đọc** `x0` lần nào trước khi tự ghi `x0` (`adrp x0, #0x2ae1000` @20001876), nên `this` truyền vào là rác vô hại. Hai check giữ điều này: `getshortnumber-never-reads-this` và `the-getshortnumber-call-leaves-x0-stale`.

---

## 6. Bốn method không có call-site nào trong mẫu

`SetBoxSprite` (20002124), `SetIconSprite` (20002152), `SetGrayScale` (20002236), `.ctor` (20002504) — **0** hit trên 8 slice.

Đây là chỗ dễ sai nhất, nên nói rõ hai chiều:

- `.ctor` không bao giờ xuất hiện dưới dạng `bl` tới RVA của nó: IL2CPP cấp phát qua helper 17879616 rồi mới gọi ctor, và ctor của `MonoBehaviour` con nằm trong bảng method chứ không phải đích của một `bl` trực tiếp trong các method đã cắt. **Không** kết luận gì từ con số 0 này.
- `SetGrayScale` **không** phải đường mà popup dùng để bật cờ xám: 165 đo được popup gọi thẳng `Material.SetFloat` (41329332) trên cell `0x2adbea8`. Vậy setter của `Box_Rewards` là đường *khác* (dùng ở nơi không nằm trong 8 slice), còn cờ xám của popup là inline.

---

## 7. Quy ước tham số tại từng site (`SetInfo`)

`SetInfo(Sprite _boxSpr, Sprite _iconSpr, int _number, bool _isCards, float _scaleIcon, string _strBonus)` → `x1, x2, w3, w4, s0, x5`.

| Tham số | Phân bố trên 30 site |
|---|---|
| `_strBonus` | `x5 = xzr` **×30** — không site nào truyền chuỗi |
| `_isCards` | `wzr` ×23 · `#1` literal ×6 · `cset w4, eq` ×1 (`Board_PVP.SetupHunters`) |
| `_scaleIcon` | `fmov s0, #1.0` ×17 · `#1.25` ×6 · `#1.5` ×1 · cell `.rodata` ×5 · field ×1 |
| `_boxSpr` | kết quả call trước ×23 · local ×4 · `mov x1, xzr` ×3 |
| `_iconSpr` | field ×21 · `ldr` không offset ×3 · local ×6 |

Hai cell scale là `0x756c14` (×4: ba site `Board_EventSeasonPass` + một site `Board_QuestRewards`) và `0x756f10` (×1). `0x756c14` chính là literal mà 164 gặp ở pad đầu của popup đổi — cùng một hằng, hai nơi dùng.

Ba site truyền **box sprite null** (`mov x1, xzr`: 19452264, 20000140, 20000296) ⇒ hàng chỉ có icon + số, không có khung. Đó là hàng "số không khung", không phải lỗi decode.

---

## 8. `_number` đến từ đâu (30 site)

| Nguồn | Số site | Ví dụ |
|---|---|---|
| local (`mov w3, w19/w21/w24/w28…`) | 19 | `Popup_ArenaShopExchange` 22837708 |
| field của object (`ldr w3, [xN, #0x…]`) | 5 | `Popup_PVPRewards` `[x0,#0x18]`, `[x0,#0x1c]`; `Board_QuestRewards` `[x20,#0x1c]` |
| hằng `1` | 3 | `TimeFreeRewardPack` ×2, `<OpenBox>d__43` 19998496 |
| `ldr w3, [x21]` (không offset) | 2 | `Board_EventSeasonPass` 19451736/19451872 |
| **kết quả call** | 1 | `Board_EventSeasonPass` 19452264 ← `Dictionary<int,int>.get_Item` (26393436) |

Điểm cần giữ: ba site hằng `1` nghĩa là một số hàng **luôn hiện "1"** bất kể dữ liệu thật (quà theo giờ vẽ số lượng 1). Đây là hành vi thiết kế đọc được từ static, không phải suy đoán.

---

## 9. Chuỗi prefix của `SetNumber`: hai lần dereference

166 gọi cell `0x2ade140` là "prefix cell". Chuỗi nạp thật là:

```asm
20001644  adrp x21, #0x2ade000
20001648  ldr  x21, [x21, #0x140]   ; cell 0x2ade140 -> một slot
20001660  ldr  x8, [x21]            ; slot -> con trỏ chuỗi
20001672  mov  x0, x8
20001676  bl   String.Concat(string, string)   ; 33439876
```

Nghĩa là **hai** lần dereference: cell → slot → string. Cùng cell đó cũng được đưa vào helper runtime 17879080 ngay sau cổng `tbnz` (20001612–20001620), nên "prefix cell" là **nhãn của điểm nạp**, chưa phải bằng chứng đây là một string object. Nội dung chuỗi vẫn là `MODEL_NOT_MEASURED runtime`; báo cáo này chỉ pin *đường nạp*.

---

## 10. Giới hạn và open item

1. **Cell `0x2ade140` thực chất là gì** (static field kiểu `string` vs literal cache) — `MODEL_NOT_MEASURED runtime`; §9 chỉ pin đường nạp.
2. **Giá trị hai float `.rodata`** `0x756c14` / `0x756f10` — không rodata window nào trong 8 slice phủ hai địa chỉ này ⇒ `MODEL_NOT_MEASURED runtime`.
3. **Field nào của class nào** đứng sau mỗi `ldr w3, [xN, #0x…]` / `ldr x0, [xN, #0x…]` — bảng ghi *thanh ghi + offset*, không ghi class chủ ⇒ `MODEL_NOT_MEASURED`.
4. **Call-site ngoài 8 slice** cho `SetGrayScale` / `SetIconSprite` / `SetBoxSprite` — "not consulted ≠ missing": 8 slice là mẫu, không phải toàn ảnh.

---

## 11. Cách tái lập

```bash
python3 tools/verify/reward_box_callers.py       # in bytes/sha256/39 check, ghi lại artifact
python3 -m unittest tests.test_reward_box_callers -v
python3 tools/verify-claims.py                   # APKD1 + AI1 đã sync theo báo cáo này
```

Verifier đọc `dump.cs` (`BD.name`/`BD.method` cho tên + size) và 8 slice raw; mọi RVA ghi dạng **thập phân**, cell tĩnh ghi dạng hex. Dedupe theo `(target, class, caller, call_rva)`; mỗi dòng giữ danh sách slice để chồng lấn không bị mất.
