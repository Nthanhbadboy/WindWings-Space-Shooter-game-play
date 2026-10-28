# 161 — `dump.cs` có **hai** bảng địa chỉ: đặt tên 9 960/20 174 `bl` và đóng loạt "RVA này là gì"

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + `dump.cs`/8 slice đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Tên method, số RVA, số site `bl` là hằng trong file đã pin; **hành vi** của các helper runtime và việc game có gọi đúng nhánh nào lúc chạy là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_dump_rva_index.json.gz` (5183 B, sha256 `de3afba626d19ec59bee67daeb3f1cd4873b7358a580415c1d286938b536e50b` — bản sửa errata §11)
**Báo cáo trước:** 160 (cây chọn dải), 159 (chuỗi popup), 158 (tám field), 157 (hàm dựng + 12600 s), 154 (`Math.Round` 43584368 "không có trong `dump.cs`").
**Verifier:** `tools/verify/dump_rva_index.py` (~1 s, 22 check) · **Test:** `tests/test_dump_rva_index.py` (30 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| `dump.cs` có bao nhiêu địa chỉ method? | **64 727** (image trải `0x1216610` … `0x299080c`) | §2 |
| Ngoài bảng đó còn bảng nào? | **phụ lục `/* GenericInstMethod :`**: **49 561** dòng `\|-RVA:` cho từng **generic instantiation** | §2 |
| Vậy tổng tên đọc được? | **114 288** (64 727 + 49 561), không trùng RVA nào | §2 |
| `Action<int>..ctor` 25841028 mà 159 nói "không có trong dump"? | **có** — nhưng ở **bảng generic**, không có dòng method cấp cao | §5 |
| Hai `DisplayClass` ctor 160 để mở (22771696 / 22772596)? | `Arena_Shop.<>c__DisplayClass31_2..ctor` / `…31_3..ctor` | §5 |
| Đích `bl` phổ biến nhất trong 8 slice? | **`List<object>.AddWithResize`** 29195864 — **1 305** site | §4 |
| 20 174 site `bl` được đặt tên bao nhiêu? | **9 960** (1 104 trong slice + 5 638 method + 3 218 generic) = **49,4 %** | §4 |
| Số còn lại? | **10 176** dồn vào **18 helper dưới method đầu** + **38** vào **4 đích sau method cuối** = 10 214 | §6, §7 |
| `Math.Round` 43584368 của 154? | **vẫn chưa có tên**: nằm sau method cuối 868 byte và **không** có trong bảng nào — 154 giữ nguyên caveat | §7 |
| 8 slice có khớp dump không? | **1 788/1 788** method khớp cả class lẫn signature; 2 499 record vì **711** trùng giữa các file | §3 |

**Một câu:** `dump.cs` không chỉ có bảng RVA method — nó còn có phụ lục generic instantiation, và hai bảng cộng lại đặt tên được 9 960/20 174 `bl` trong tám slice; phần không đặt tên được là **một họ 18 helper đóng** dưới method đầu và **4 đích** sau method cuối, nên từ nay mọi câu "RVA này là gì" đều có câu trả lời hoặc có biên rõ ràng.

---

## 1. Vì sao cần báo cáo này

Suốt 149→160, mỗi lần gặp một `bl` không tên, báo cáo lại mở một open item cùng một kiểu: *"helper `Math.Round` ở rva 43584368 … không có trong `dump.cs`"* (154), *"method handle nạp từ ô static, cần bảng token metadata"* (159), *"destination `0x110d12c` … unowned"* (nháp 160). Ba câu đó **không** phải ba vấn đề khác nhau — chúng là một câu: *công cụ `arena_rewards.owner()` chỉ biết 1 788 method trong slice, còn dump thì biết 114 288*. Lượt này đóng đúng câu đó, một lần, cho cả lane.

Phạm vi: chỉ dựng index + đối chiếu + đặt tên danh sách **có giới hạn**. Không mở lại giá ba dải (158), chuỗi popup (159), cây chọn dải (160), bộ đếm (156), ví (155).

---

## 2. Hai bảng trong một file dump

`reverse-engineering/il2cpp/dump.cs.gz` (e08f23fb…, 542 227 dòng, 10 906 khai báo lớp) chứa hai dạng dòng địa chỉ:

```
	// RVA: 0x15AE1AC Offset: 0x15AA1AC VA: 0x15AE1AC
	private void OnClickPlayerItem(Shop_Cell cell) { }
```

và, bên trong mỗi method generic, một khối phụ lục:

```
	// RVA: -1 Offset: -1
	public static T get_Instance() { }
	/* GenericInstMethod :
	|
	|-RVA: 0x1DA895C Offset: 0x1DA495C VA: 0x1DA895C
	|-Singleton<object>.get_Instance
	*/
```

| bảng | dòng nhận dạng | số RVA | ghi chú |
|---|---|---|---|
| method | `// RVA: 0x…` | **64 727** | RVA nhỏ nhất `0x1216610`, lớn nhất `0x299080c` |
| generic instantiation | `\|-RVA: 0x… Offset:` | **49 561** | ví dụ `Action<int>..ctor`, `List<object>.AddWithResize` |
| **tổng** | | **114 288** | **không** RVA nào nằm ở cả hai bảng |

Đây là lý do 154/159/160 sai khi nói "không có trong dump": phép quét của các báo cáo đó chỉ đọc bảng thứ nhất.

---

## 3. Đối chiếu ngược: 8 slice khớp dump 100 %

Trước khi dùng index để đặt tên, phải chứng minh index và slice nói về cùng một build:

| phép đo | kết quả |
|---|---|
| record trong 8 file slice | **2 499** (`arena-pvp` 1361, `meta-rewards` 540, `key-grant` 448, `box-draw` 103, `pack-index` 26, `key-jump` 19, `pvp-dispatch` 1, `pvp-rules` 1) |
| method **phân biệt** `(class, rva)` | **1 788** ⇒ **711** record trùng giữa các file |
| có mặt trong bảng method của dump | **1 788 / 1 788** |
| trùng **tên lớp** | **1 788 / 1 788** |
| trùng **signature** (sau khi gộp khoảng trắng) | **1 788 / 1 788** |

Một chi tiết parser đáng ghi: tên lớp iterator chứa ký tự `|` (`Board_PVP.<>c__DisplayClass76_0.<<CheckUserSignInOrRestoreYourDatas>g__IESignInOrRestoreYourDatas|1>d`). Cắt tên tại `|` cho ra **6 "lệch lớp" giả**; cho `|` vào lớp ký tự hợp lệ thì về **0**. Verifier pin đúng `0` để không ai vô tình "sửa" lại regex.

---

## 4. Phân loại 20 174 site `bl`

| nguồn tên | site | ví dụ |
|---|---|---|
| method trong **slice** | **1 104** | `Arena_Shop.GetIdItem` |
| bảng **method** của dump | **5 638** | `GameDatas.get_ArenaMedal` |
| bảng **generic** của dump | **3 218** | `List<int>..ctor` |
| **chưa có tên** | **10 214** | 18 helper + 4 đích sau method cuối (§6, §7) |
| **tổng** | **20 174** | — |

Đáng chú ý: đích được gọi nhiều nhất trong **toàn bộ** tám slice không phải một method của game mà là **`List<object>.AddWithResize` (29195864) — 1 305 site**, tức các `List<object>` (danh sách sự kiện, danh sách UI) lớn dần khắp code. Kế đó `List<int>.AddWithResize` (28921100, **596**), `List<object>.get_Item` (**187**), `Func<bool>..ctor` (**113**), `List<object>..ctor` (**124**).

**Không một `bl` nào rơi vào khoảng giữa hai method có tên** (0 site) — nghĩa là bảng method phủ kín vùng ảnh: cứ có `bl` vào trong `0x1216610…0x299080c` là hoặc có tên, hoặc thuộc họ helper dưới đáy ảnh.

---

## 5. Mười sáu RVA từng bị hỏi, nay có tên

| RVA | tên | bảng | mở từ |
|---|---|---|---|
| 19464628 | `Board_EventSeasonPass.EventRewards..ctor(Shop_Pack, int, int, int)` | method | 158 |
| 20189848 | `Shop_Pack..ctor()` | method | 158 |
| 22732732 | `Arena_Shop.GetIdItem(int)` | method | 160 |
| 19941788 | `PVP_Shop.GetIdItem(int)` | method | **mới** (bản PVP của 160) |
| 20084804 | `GameDatas.get_ArenaMedal()` | method | 155 |
| 20085132 | `GameDatas.get_PvPMedal()` | method | 155 |
| 22771696 | `Arena_Shop.<>c__DisplayClass31_2..ctor()` | method | **160 để mở** |
| 22772596 | `Arena_Shop.<>c__DisplayClass31_3..ctor()` | method | **160 để mở** |
| 22835700 | `Popup_ArenaShopExchange.SetPopup(int, EventRewards, Action<int>)` | method | 159 |
| 19888660 | `Popup_PVPShopExchange.SetPopup(int, EventRewards, Action<int>)` | method | 159 |
| 25841028 | **`Action<int>..ctor`** | **generic** | **159 để mở** |
| 33442960 | `String.Format(string, object)` | method | 159 |
| 41424900 | `GameObject.SetActive(bool)` | method | 159 |
| 20903608 | `Slider.set_Value(float)` | method | 154 |
| 29195864 | `List<object>.AddWithResize` | generic | **mới** |
| 28921100 | `List<int>.AddWithResize` | generic | **mới** |

Hai hệ quả trực tiếp:

* 159 viết *"`Action<int>..ctor` (25841028)"* như một suy luận từ call-site. Nay là **tên thật**, lấy từ bảng generic — nhưng **target của delegate** vẫn là method handle nạp từ ô static, nên open item *"delegate trỏ tới method nào"* của 159 **không** đóng; chỉ phần "ctor là gì" đóng.
* 160 ghi hai ctor `DisplayClass31_2/31_3` là "unowned". Nay có tên: click dựng **hai** display class (một cho dòng, một cho callback), đúng như 159 mô tả `Action<int>` gắn với cell.

---

## 6. Họ helper dưới đáy ảnh: 18 đích, 10 176 site

Mọi đích `bl` nằm **dưới** method đầu tiên (`< 0x1216610`) — tức ngoài vùng code managed — gom lại đúng **18** địa chỉ, tất cả trong dải `0x110d0…`:

| RVA | hex | site | dấu vết call-site |
|---|---|---|---|
| 17879080 | `0x110d028` | **4 631** | 4 630/4 631 có `adrp` ngay trước (tra ô static) |
| 17879340 | `0x110d12c` | **1 695** | **1 690/1 695** tiền tố là `ldr w?,[x?,#0xe0]` + `cbnz` |
| 17879616 | `0x110d240` | **1 547** | 1 011/1 547 có `adrp` (cấp phát object — 158 gọi nó là `ALLOC`) |
| 17879196 | `0x110d09c` | **850** | 42/850 có `adrp` |
| 17879632 | `0x110d250` | **613** | 21/613 có `adrp` |
| 17879084 | `0x110d03c` | **196** | 196/196 có `adrp` |
| 12 đích còn lại | `0x110d…` | 644 | tổng cả họ: **10 176** |

Dấu vết `ldr …, #0xe0` + `cbnz` ở 1 690/1 695 site của 17879340 khớp mẫu **kiểm tra khởi tạo lớp** (đọc cờ, nếu chưa khởi tạo thì gọi). Đây là **suy luận từ hình dạng call-site**, không phải tên đọc được — artifact ghi đúng như vậy, không gán tên.

Không đặt tên được vì chúng **không có dòng nào** trong metadata managed: tìm chuỗi `0x110d12c` trong toàn bộ 542 227 dòng dump → **0** lần; tương tự `0x110d240`, `0x110d250`.

---

## 7. Bốn đích sau method cuối — và `Math.Round` của 154

Method cuối cùng trong dump là `__Il2CppComDelegate.Finalize()` ở `0x299080c`. Sau nó còn **4** đích `bl` (38 site):

| RVA | hex | site | cách method cuối | method có tên gần nhất |
|---|---|---|---|---|
| 43584288 | `0x2990b20` | 16 | 788 B | `__Il2CppComDelegate` |
| 43584304 | `0x2990b30` | 16 | 804 B | `__Il2CppComDelegate` |
| **43584368** | **`0x2990b70`** | **5** | **868 B** | `__Il2CppComDelegate` |
| 43584480 | `0x2990be0` | 1 | 980 B | `__Il2CppComDelegate` |

`0x2990b70` **chính là** đích mà 154 gọi là helper `Math.Round`. Lượt này xác nhận **154 đã đúng khi không dám đặt tên**: RVA đó không có trong bảng method, không có trong bảng generic, và nằm sau method cuối 868 byte. Tên "Math.Round" vẫn chỉ là suy luận từ call-site + cặp tie-break của 154 — **không** nâng cấp thành tên đo được.

---

## 8. Bẫy mới phát hiện: `b` (tail) trỏ vào **giữa thân** method

Trong 3 664 site `b` của tám slice, **2 652** đích (3 062 site) **không** phải method start và **không** nằm ngoài ảnh: chúng rơi *bên trong* thân một method khác. Ví dụ lớn nhất:

```
19877384  b #0x12f4ea4      ← Popup_PvPRankings.<IEDisplayRank>d__24
```

`0x12f4ea4` nằm **2 324 byte sau** method start gần nhất (`0x12f4590`, `private bool MoveNext()`). Nhìn vào ngữ cảnh thì vẫn là `b #0x12f4ea4` lặp nhiều lần liền nhau — dấu hiệu chỉ số bảng nhảy (jump table) bị bộ tách slice in ra dưới dạng địa chỉ chứ không phải nhãn. Hệ quả thực dụng:

* **`b` không phải `bl`**: không báo cáo nào được đọc một `b` mid-body thành lời gọi hàm.
* 160 đã dựa vào `b` cho **nhánh điều khiển trong cùng hàm** (`b.le`, `b` tail tới `SetPopup`) — cách dùng đó an toàn vì đích vẫn là RVA thật của method đích; điều **không** an toàn là coi `b` mid-body là "gọi vào giữa hàm".
* 20 đích lớn nhất được ghi kèm `nearest_named_method` trong artifact để lần sau khỏi phải đoán.

---

## 9. Giới hạn và open item

**Đóng được:**
- Hai bảng địa chỉ của dump và kích thước từng bảng (64 727 + 49 561 = 114 288), biên ảnh.
- 8 slice khớp dump 100 % về class và signature; 2 499 record = 1 788 method + 711 trùng.
- 9 960/20 174 site `bl` có tên; phần còn lại là **họ đóng 18 helper** (10 176) + **4 đích sau method cuối** (38).
- Mười sáu RVA từng bị hỏi nay có tên, gồm `Action<int>..ctor` (bảng generic), hai `DisplayClass31_2/31_3` ctor của 160, `PVP_Shop.GetIdItem` 19941788.

**Không đóng được (STATIC-ONLY):**
- **Tên của 18 helper**: chúng không có dòng nào trong metadata managed; tên thật nằm trong thư viện runtime/codegen, không nằm trong APK. Hình dạng call-site được ghi, tên thì không.
- **`Math.Round` 43584368**: sau method cuối 868 byte, không có trong bảng nào — giữ nguyên cách gọi của 154.
- **Target của `Action<int>`** (159): có tên ctor nhưng method handle vẫn nạp từ ô static ⇒ cần bảng token metadata.
- **Generic instantiation có trùng thân hay không**: phụ lục cho một RVA mỗi instantiation, nhưng shared generics có thể gộp nhiều instantiation về một thân — `MODEL_NOT_MEASURED runtime`.
- **`b` mid-body** (2 652 đích): chỉ ghi nhận, không diễn giải; muốn đọc đúng cần bộ tách jump table.

---

## 10. Cách tái lập

```
python3 tools/verify/dump_rva_index.py             # dựng lại artifact, in bytes + sha256 + 24/24
python3 -m unittest tests.test_dump_rva_index -q   # 30 test
```

Artifact pin: **5183 B**, sha256 `de3afba626d19ec59bee67daeb3f1cd4873b7358a580415c1d286938b536e50b`, **24/24 check** (64 727 method RVA, 49 561 generic RVA, 1 788 slice khớp, 20 174 site `bl` phân loại, 18 helper, 4 đích sau cuối). Nguồn pin: `reverse-engineering/il2cpp/dump.cs.gz` (e08f23fb…), 8 file `reverse-engineering/raw/*535b0541/native.json.gz`, `datas/l2_535b0541_shop_band_tree.json.gz` (160).

---

## 11. Errata — 162 phát hiện một lỗi parse trong chính index này

`ResetShop` của hai shop gọi `bl #0x277D2C0`, index đời đầu trả về `PropertyName | Range(int, int)`. Nhìn vào dump thì:

```
public static class Random // TypeDefIndex: 7798
	// RVA: 0x277D2C0 …
	public static int Range(int minInclusive, int maxExclusive) { }
```

Tên đúng là **`Random.Range`**. Nguyên nhân: regex nhận khai báo lớp chỉ liệt kê `sealed`/`abstract`/`partial` mà **quên `static `**, nên 484 khai báo `static class` bị bỏ qua và method của chúng bị gán sang lớp đứng trước.

| | giá trị |
|---|---|
| khai báo `static class` bị bỏ qua | **484** |
| dòng method bị gán sai lớp | **3 780 / 64 727** (5,8 %) |
| ví dụ | `Random.Range`, `Convert.*` (233), `AndroidJNI.*` (233), `ExceptionBuilder.*` (255), `Math.*` (54) |

Đã sửa regex, thêm hai check (`484-static-class-declarations-are-parsed`, `Random.Range-0x277d2c0-belongs-to-Random`) và dựng lại artifact: **5183 B**, sha256 `de3afba626d19ec59bee67daeb3f1cd4873b7358a580415c1d286938b536e50b`, **24/24 check**; số lớp `10 422 → 10 906`. Các con số khác của 161 (64 727 method RVA, 49 561 generic RVA, 1 788 slice khớp, 20 174 site `bl`, 18 helper, 4 đích sau cuối) **không đổi** — lỗi chỉ ở cột tên lớp, không ở phép đếm địa chỉ.

Bài học giữ nguyên tinh thần 161: một index chỉ đáng tin khi có phép thử ngược. Lỗi này lọt vì chưa có phép thử nào *khẳng định* một dòng cụ thể thuộc đúng lớp — nay có.
