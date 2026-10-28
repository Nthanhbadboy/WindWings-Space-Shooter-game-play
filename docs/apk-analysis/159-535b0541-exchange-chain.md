# 159 — Chuỗi đổi thưởng khép kín: shop click → `SetPopup` → `Buy` chỉ **so ví** rồi gọi callback

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + dump/metadata đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Ai gọi ai, ghi field nào, so ví nào là hằng lúc build; **người chơi có đủ medal tại thời điểm bấm** là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_exchange_chain.json.gz` (3458 B, sha256 `09672352efc79270ad9e62045d4a51b9934181fab8ed8fad50d2dc68c063eb18`)
**Báo cáo trước:** 158 (bốn dòng `EventRewards`, giá ba dải), 157 (hàm dựng + 12600 s), 156 (bộ đếm đã bán), 155 (ví medal), 154 (slider).
**Verifier:** `tools/verify/exchange_chain.py` (~7 s) · **Test:** `tests/test_exchange_chain.py` (20 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| Ai gọi `Popup_*ShopExchange.SetPopup`? | **đúng một chỗ mỗi shop**: `Arena_Shop.OnClickPlayerItem` tại 22734600, `PVP_Shop.OnClickPlayerItem` tại 19943488 — cả hai là **tail branch `b`** | §2 |
| "`SetPopup` không có caller" có đúng? | **không** — câu đó chỉ đúng với bản sao thứ ba `Popup_Exchange` (TypeDefIndex 693) | §2 |
| Đối số thứ ba (`Action<int> exit`) là gì? | một delegate dựng ngay trước lời gọi bằng `Action<int>..ctor` (25841028), target là **cell vừa click** | §2 |
| `SetPopup` làm gì? | ghi `exit` +0x50, `count = 1` +0x58, `rewards` +0x60, `maxStock = rewards.stock − GetStockItem(index)` +0x5C, text giá = `price × count`, dựng tab + slider | §3 |
| `OnPressedButtonBuy` trừ medal? | **không**. Nó chỉ `total = price × count`, so với `GameDatas.get_ArenaMedal` / `get_PvPMedal`, thiếu thì `ret`, đủ thì **gọi `exit(count)`** rồi ẩn popup | §4 |
| Vậy ai trừ medal? | closure mua của shop (155/156) — popup chỉ **gác cổng** | §5 |

**Một câu:** popup đổi thưởng **không có ví**: nó kiểm `price × count` với medal hiện có rồi gọi callback `Action<int>` do shop truyền vào — người trừ medal là closure của shop, đúng closure mà 155 đã đếm.

---

## 1. Vì sao cần báo cáo này

154 dựng được công thức slider (`count → cost → onExit`) nhưng không trả lời được **ai mở popup** và **`onExit` là gì**; ghi chú của lane khi đó nói "`SetPopup` không có caller" và coi đó là "not consulted". Lượt này quét lại toàn bộ tám slice cho cả **ba** bản popup và tìm ra: hai bản shop **có** caller, bản thứ ba (`Popup_Exchange`) mới không có.

---

## 2. Caller: một tail branch mỗi shop

Quét mọi `bl`/`b` tới 22835700 (`Popup_ArenaShopExchange.SetPopup`) và 19888660 (`Popup_PVPShopExchange.SetPopup`) trên 8 slice:

| popup | caller | lời gọi | kiểu |
|---|---|---|---|
| `Popup_ArenaShopExchange` (466) | `Arena_Shop.OnClickPlayerItem` 22733228 | **22734600** | `b` (tail) |
| `Popup_PVPShopExchange` (875) | `PVP_Shop.OnClickPlayerItem` 19942120 | **19943488** | `b` (tail) |

Đuôi hàm của caller (Arena):

```
22734512  ldr  x19, [x19, #0xc0]      popup component
22734520  ldr  x0,  [x8]              klass cho object_new
22734524  bl   0x110d240             new Action<int>
22734532  ldr  x8,  [x8, #0xe0]
22734536  ldr  x2,  [x8]              method handle
22734540  mov  x1,  x20               target = cell vừa click
22734552  bl   0x18a4d84             Action<int>..ctor(object, IntPtr)   → 25841028
22734560  mov  x0,  x19              this = popup
22734564  mov  w1,  w22              index
22734568  mov  x2,  x21              EventRewards
22734572  mov  x3,  x23              the Action
22734600  b    #0x15c71f4            → Popup_ArenaShopExchange.SetPopup
```

⇒ `onExit` của 154 **là** một `Action<int>` gắn với cell, dựng ngay trước lời gọi. PVP y hệt (`19943444` `bl 0x18a4d84`, `19943488` `b`).

---

## 3. `SetPopup`: ghi gì, tính gì

`Popup_ArenaShopExchange.SetPopup(int index, EventRewards eventReward, Action<int> exit)` 22835700 (**932 B**; PVP 19888660, **928 B**):

```
22835744  mov  x22, x3                exit
22835748  mov  x20, x2                eventReward
22835752  mov  w21, w1                index
22836040  str  x22, [x19, #0x50]      this.exit      = exit
22836104  mov  w8, #1
22836112  str  w8,  [x22, #0x58]!     this.count     = 1        (pre-index write-back)
22836116  str  x20, [x22, #8]         this.rewards   = eventReward   (0x58+8 = 0x60)
22836132  ldr  w23, [x20, #0x20]      eventReward.stock
22836144  mov  w0,  w21
22836152  bl   Arena_Shop.GetStockItem          → 22732896
22836156  sub  w8,  w23, w0
22836164  str  w8,  [x21, #0x5c]!     this.maxStock  = stock − sold
22836172  ldr  w9,  [x20, #0x1c]      eventReward.price
22836168  ldur w8,  [x21, #-4]        count
22836188  mul  w8,  w9, w8            price × count
22836216  bl   String.Format          → 33442960   (text giá)
22836464  bl   SetEventRewardTabs     → 22836632
22836536  bl   Slider.set_Value       → 20903608   (chỉ khi maxStock > 1)
```

PVP cùng cấu trúc với `GetStockItem` 19889588 và `SetEventRewardTabs` 19889752; khác biệt duy nhất đáng kể: PVP đọc `x21` thay `x20` cho `price` (22836172 ↔ 19889140) — cùng nghĩa.

Ba field `+0x50`, `+0x58`, `+0x60` khớp layout popup mà 153 đã pin; `+0x5C` là `maxStock` — chính là trần slider của 154, nay có công thức đầy đủ **`rewards.stock − GetStockItem(index)`**.

---

## 4. `OnPressedButtonBuy`: so ví rồi gọi callback

`Popup_ArenaShopExchange.OnPressedButtonBuy()` 22837792 (**184 B**; PVP 19890912, **184 B**):

```
22837836  ldr  x8,  [x19, #0x60]      rewards
22837852  ldr  w8,  [x8, #0x1c]       price
22837860  ldr  w9,  [x19, #0x58]      count
22837868  mul  w20, w8, w9            total = price × count
22837884  bl   GameDatas.get_ArenaMedal        → 20084804
22837888  cmp  w0,  w20
22837892  b.ge …                      ví < total ⇒ ret (không làm gì)
22837908  ldr  x8,  [x19, #0x50]      exit
22837916  ldr  w1,  [x19, #0x58]      count  ← đối số
22837932  blr  x9                     exit(count)
22837968  b    GameObject.SetActive(false)   → 41424900
```

PVP: `bl GameDatas.get_PvPMedal` 19891004, `blr x9` 19891052, `SetActive` 19891088.

**Không có một lời gọi `set_ArenaMedal`/`set_PvPMedal` nào trong cả hai lớp popup** (quét toàn bộ method của hai lớp: 0). Nghĩa là popup **không sở hữu việc trừ tiền** — nó chỉ kiểm và gọi lại.

---

## 5. Hệ quả: chuỗi trả tiền nằm ở phía shop

| bước | nơi | làm gì |
|---|---|---|
| 1 | `Arena_Shop.OnClickPlayerItem` 22733228 | dựng `EventRewards(pack, value, cost, stock)` (158) |
| 2 | cùng hàm, 22734600 | `SetPopup(index, rewards, new Action<int>(cell, …))` |
| 3 | `SetPopup` 22835700 | `maxStock = rewards.stock − sold`, text giá `price × count` |
| 4 | `OnPressedButtonBuy` 22837792 | `price × count ≤ medal ?` → nếu thiếu thì thoát |
| 5 | `exit(count)` → closure `g__OnBuy\|2/4/6` | **closure trừ medal + `SetStockItem`** (155/156) |

Vì vậy mọi kết luận "popup trừ medal" là sai; và câu hỏi "mua quá trần có bị chặn không" (156 §8) có thêm một mảnh: cổng chặn duy nhất ở phía popup là **số medal**, không phải `maxStock` — `maxStock` chỉ dùng để vẽ slider và text.

---

## 6. Bảng đối chiếu hai phía

| | `Arena_Shop` | `PVP_Shop` |
|---|---|---|
| popup | `Popup_ArenaShopExchange` 466 | `Popup_PVPShopExchange` 875 |
| caller / lời gọi | 22733228 / **22734600** | 19942120 / **19943488** |
| `SetPopup` | 22835700 (932 B) | 19888660 (928 B) |
| `GetStockItem` trong `SetPopup` | 22732896 | 19889588 |
| `SetEventRewardTabs` | 22836632 | 19889752 |
| `OnPressedButtonBuy` | 22837792 (184 B) | 19890912 (184 B) |
| ví được so | `get_ArenaMedal` 20084804 | `get_PvPMedal` 20085132 |
| setter ví trong lớp popup | 0 | 0 |

---

## 7. Giới hạn và open item

**Đóng được:**
- Ai mở popup (`SetPopup`): đúng một caller mỗi shop, là hàm click của shop (§2).
- `onExit` là gì: `Action<int>` trên cell, truyền vào `SetPopup`, lưu `+0x50`, gọi với `count` ở nút Buy (§2, §4).
- Popup **không** trừ medal; debit nằm ở closure shop (§5).

**Không đóng được (STATIC-ONLY):**
- **`Action<int>` trỏ tới method nào**: method handle được nạp từ ô static (`ldr x2, [x8]` sau `adrp`); cần bảng token metadata để đặt tên — không có trong workspace. Đây là bước chặn chính xác.
- **Tràn số**: `mul` 32-bit, cả hai toán hạng từ dữ liệu, code không có kiểm tràn ⇒ `MODEL_NOT_MEASURED runtime`.
- **`Popup_Exchange` (693)**: cùng ba đối số nhưng toàn bộ method nằm dưới RVA thấp nhất của 8 slice ⇒ đường mua của bản thứ ba chưa đọc.

---

## 8. Cách tái lập

```
python3 tools/verify/exchange_chain.py             # dựng lại artifact, in bytes + sha256 + 14/14
python3 -m unittest tests.test_exchange_chain -q   # 20 test
```

Artifact pin: **3458 B**, sha256 `09672352efc79270ad9e62045d4a51b9934181fab8ed8fad50d2dc68c063eb18`, **14/14 check** (2 popup, 2 caller, 0 setter ví trong popup). Nguồn pin trong artifact: `reverse-engineering/raw/arena-pvp-535b0541/native.json.gz`, `reverse-engineering/il2cpp/dump.cs.gz`, `datas/l2_535b0541_shop_field_readers.json.gz` (158).
