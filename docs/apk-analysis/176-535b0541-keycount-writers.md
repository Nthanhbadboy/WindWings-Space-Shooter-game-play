# 176 — Ai ghi `GameDatas.KeyCount0/1/2`: tiền đề của mục 32 sai, và sáu chỗ ghi

**Trạng thái:** `DECODED_STATIC` (đọc native + asm slice đã ghim; không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Mọi con số dưới đây đến từ `datas/l2_535b0541_keycount_writers.json.gz`.
**Artifact:** `datas/l2_535b0541_keycount_writers.json.gz` — **9416 B**, sha256 `f44fdb903dc2e67c651aedfa38fc725e779f398626bcc1c4281253eff93dbcdc`
**Verifier:** `tools/verify/keycount_writers.py` (**14 check**) · **Test:** `tests/test_keycount_writers.py` (**22 test**)
**Trả lời:** mục **32** của audit ("a direct static store outside these classes") — narrowing, chưa close (§6)

---

## 0. TL;DR

| | |
|---|---|
| 132 hỏi | "thấy *call* chứ không thấy *store*; một chỗ ghi thẳng vào **static** 0x50/0x54/0x58 ở nơi khác sẽ không hiện" |
| 176 đo | **không có static cell nào để ghi.** `+0x50/+0x54/+0x58` là **field của instance**, nằm sau chuỗi `slot tĩnh 0x2adb000+0xaf8 → [x] → +0xb8` |
| quét đúng cách | lần theo chuỗi, chỉ tính store qua thanh ghi đã đi hết chuỗi |
| kết quả | **6** chỗ ghi, **tất cả** trong `GameDatas`: 3 setter + 3 getter (getter **cache** giá trị nạp lười) |
| quét theo offset (cách cũ) | **106** chỗ ghi ở cùng ba offset — vô nghĩa, vì mỗi lớp có field +0x50 riêng |
| coverage | 1.788 method / 159.059 lệnh native + 139 file asm / 138.226 lệnh |

---

## 1. Tiền đề sai ở đâu

132 (và 147 khi tạo mục 32) giả định `KeyCount0/1/2` là **static** — tức chúng nằm ở một ô trong khối tĩnh, và câu hỏi là "có ai ghi thẳng vào ô đó không". Đọc thân `set_KeyCount0` (20070940) thì thấy không phải:

| RVA | lệnh | nghĩa |
|---|---|---|
| 20070952 | `adrp x20, #0x2adb000` | trang của **slot** singleton |
| 20070960 | `ldr x20, [x20, #0xaf8]` | `x20` = giá trị slot = con trỏ tới object quản lý |
| 20071004 | `ldr x0, [x20]` | `x0` = object bên trong |
| 20071036 | `ldr x8, [x0, #0xb8]` | `x8` = **holder** chứa ba bộ đếm |
| 20071048 | `str w19, [x8, #0x50]` | `KeyCount0 = value` |

`KeyCount0/1/2` là **property** (`get_`/`set_`), và field thật nằm trên holder. Nên "một chỗ ghi static khác" **không thể tồn tại** — không có ô static nào cho ba field đó. Câu hỏi đúng phải là: *có method nào khác đi hết chuỗi rồi ghi không?*

## 2. Quét theo chuỗi, không theo offset

Với mỗi method, verifier gắn nhãn thanh ghi theo đúng ba bước của chuỗi:

```
(page 0x2adb000) + ldr [x, #0xaf8]      -> 'slot'
'slot'           + ldr [x]              -> 'behind'
'behind'         + ldr [x, #0xb8]       -> 'holder'
store [holder, #0x50|0x54|0x58]         -> một chỗ ghi thật
```

Mọi phép ghi khác vào thanh ghi đều **xoá** nhãn (nên không có chuyện "đoán bừa"), và `cmp`/`tst`/`fmov`/`movk` được coi là không ghi — đúng như 169/172 đã phải làm với `adrp`.

Vì sao không quét offset trơn: cùng ba offset đó, trong chính corpus này, có **106** chỗ ghi thuộc về **lớp khác** (`Shop_Pack`, `ArenaManager`, `Board_Quest`, `Map_Get_Datas`, …) — mỗi lớp có field +0x50 riêng. Quét offset trơn sẽ trả về 106 dòng vô nghĩa; quét theo chuỗi trả về **6**, và cả 6 đều đúng là chỗ ta đang tìm.

## 3. Sáu chỗ ghi

| method | vai | RVA store | field | lệnh |
|---|---|---|---|---|
| `get_KeyCount0` (20070740) | **getter** | 20070896 | `+0x50` | `str w19, [x9, #0x50]` |
| `set_KeyCount0` (20070940) | setter | 20071048 | `+0x50` | `str w19, [x8, #0x50]` |
| `get_KeyCount1` (20071068) | **getter** | 20071224 | `+0x54` | `str w19, [x9, #0x54]` |
| `set_KeyCount1` (20071268) | setter | 20071376 | `+0x54` | `str w19, [x8, #0x54]` |
| `get_KeyCount2` (20071396) | **getter** | 20071552 | `+0x58` | `str w19, [x9, #0x58]` |
| `set_KeyCount2` (20071596) | setter | 20071704 | `+0x58` | `str w19, [x8, #0x58]` |

**Vì sao getter lại ghi:** giá trị khởi tạo là **−1** (sentinel "chưa nạp"). `get_KeyCount0` đọc `[holder+0x50]`, `cmn w9, #1` (so với −1), nếu đúng thì gọi `PlayerPreferences.GetInt` (0x277cca0) rồi **ghi lại** kết quả vào `[holder+0x50]`:

| RVA | lệnh |
|---|---|
| 20070828 | `ldr w9, [x9, #0x50]` |
| 20070832 | `cmn w9, #1` |
| 20070860 | `bl #0x277cca0` (PlayerPrefs.GetInt) |
| 20070896 | `str w19, [x9, #0x50]` |

Nên "3 setter" của 132 là **chưa đủ**: có 3 nguồn ghi nữa, và chúng nằm trong chính ba accessor — không phải ở nơi khác. Đó là câu trả lời cho mục 32: *không có chỗ ghi lạ nào; nhưng cũng không phải chỉ setter ghi.*

## 4. Hai corpus độc lập nói cùng một chuyện

| corpus | đơn vị | khớp |
|---|---|---|
| 8 file `raw/*/native.json.gz` (de-dup theo `(class, rva)` còn 6 nguồn) | 1.788 method · 159.059 lệnh | 6 RVA |
| 139 file `raw/il2cpp-consts/*.asm.txt` | 138.226 lệnh | **đúng 6 RVA đó** |

Hai cách bóc khác nhau (native scan + asm slice) ra cùng tập sáu RVA ⇒ kết quả không phụ thuộc một nguồn.

## 5. Vì sao đây là *narrowing*, không phải *closed*

Coverage là **corpus**, không phải binary. Một method không nằm trong 8 native scan lẫn 139 slice vẫn có thể đi hết chuỗi rồi ghi — không có raw nào để nói ngược lại. Vậy mục 32 chuyển từ *"phương pháp không thấy được store"* thành *"đã quét store, 1.788 method + 138.226 lệnh, không có chỗ ghi lạ; phần chưa phủ vẫn chưa phủ"*.

Đây đúng là loại tiến bộ mà **hợp đồng 173** muốn: mục 32 đổi từ `SCAN` mơ hồ thành một phép đo có biên.

## 6. Cái report này **không** làm

* **Không** đổi verdict của mục 32 trong `open_items_audit`. Đổi verdict là đổi byte của audit ⇒ 168 (băm audit) và 173 (băm mọi artifact) phải sinh lại theo đúng thứ tự. Việc đó thuộc một report **refresh audit** riêng — và khi làm, mục 32 nên được ghi là *"tiền đề 'static' sai; đã quét chain-aware 1.788 method, 6 writer"*, không phải "đã đóng".
* **Không** kết luận gì về giá trị: chạy thật thì `KeyCount0` bằng bao nhiêu vẫn là `MODEL_NOT_MEASURED runtime`.
* **Không** chạm 3 file bảo vệ, không probe, không emulator.

## 7. Tái lập

```bash
python3 tools/verify/keycount_writers.py        # 14/14 check, 6 writers
python3 -m unittest tests.test_keycount_writers -q   # 22 test
python3 -c "import sys; sys.path.insert(0,'tools/verify'); import keycount_writers as K; \
print(len([w for w in K.collect()['writers']]))"     # 6
```
