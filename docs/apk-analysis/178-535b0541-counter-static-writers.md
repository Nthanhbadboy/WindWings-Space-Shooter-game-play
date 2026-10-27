# 178 — `+0xb8` là `static_fields`: ba bộ đếm chìa khoá **là static**, và mục 32 đã trả lời xong

**Trạng thái:** `DECODED_STATIC` (slice đã ghim + `dump.cs`)
**Lớp bằng chứng:** STATIC-ONLY. Mỗi dòng của bảng truy được về `datas/l2_535b0541_counter_static_writers.json.gz`.
**Artifact:** `datas/l2_535b0541_counter_static_writers.json.gz` — **2142 B**, sha256 `11c6cf4b2b5c3a26d26086efc326652eb3d7539b6ac0667a181ce42791fcd718`
**Verifier:** `tools/verify/counter_static_writers.py` (**14 check**) · **Test:** `tests/test_counter_static_writers.py` (**22 test**)
**Sửa:** 176 (`datas/l2_535b0541_keycount_writers.json.gz`) — sáu địa chỉ giữ nguyên, **tiền đề bị lật**

---

## 0. TL;DR

| | 176 ghi | 178 đo |
|---|---|---|
| `keyCount0/1/2` là gì | "instance fields", "properties, **not statics**" | **`private static int` của `GameDatas`** (TypeDefIndex 249) tại `0x50/0x54/0x58` |
| `+0xb8` là gì | "the object behind slot… +0xb8" | **`Il2CppClass::static_fields`** |
| six site | 20070896 · 20071048 · 20071224 · 20071376 · 20071552 · 20071704 | **y nguyên** |

Đây là **cái bẫy của 172, sâu thêm một tầng**: `+0xb8` có hình dạng y hệt một field của object, nên một phép truy ngược base dừng ở `ldr` đầu tiên sẽ xếp một store **static** vào loại **instance**. 172 sai ở tầng ô-metadata; 178 sai ở tầng `static_fields`.

Chuỗi thật (in nguyên từ `get_KeyCount0`, RVA 20070740):

```asm
20070748 adrp x19, #0x2ce1000      ; cờ init của method
20070752 adrp x20, #0x2adb000      ; trang của ô TypeInfo
20070760 ldr  x20, [x20, #0xaf8]   ; x20 = &GameDatas_c  (ô TypeInfo, 0x2adbaf8)
20070796 strb w8,  [x19, #0x5f5]   ; đặt cờ
20070800 ldr  x8,  [x20]           ; x8 = GameDatas_c*
20070804 ldr  w9,  [x8,  #0xe0]    ; cổng cctor
20070808 cbnz w9,  +               ;
20070812 mov  x0,  x8              ;
20070816 bl   #0x110d12c           ; init class
20070824 ldr  x9,  [x8,  #0xb8]    ; static_fields   ← chỗ 176 gọi là "object"
20070828 ldr  w9,  [x9,  #0x50]    ; keyCount0
```

## 1. `dump.cs` nói thẳng

```
public class GameDatas : MonoBehaviour        // TypeDefIndex: 249
    private static int keyCount0; // 0x50
    private static int keyCount1; // 0x54
    private static int keyCount2; // 0x58
```

Cả bốn mươi ba field của `GameDatas` đều `static`, offset chạy `0x0…0xA0`, và ba bộ đếm nằm đúng `0x50/0x54/0x58` — **trùng khít** giá trị mà accessor dùng. Nếu `+0xb8` là một object thì offset trong `dump.cs` (vốn là offset trong khối static) không thể trùng. Artifact lưu cả `declared` (đọc trực tiếp từ `dump.cs`), nên con số này không phải "nhớ lại".

## 2. Census: 102 store, và vì sao quét offset là vô nghĩa

Toàn bộ corpus đã ghim (**1788 method / 159 059 lệnh / 280 class**) có **102** store vào ba offset đó, phân loại theo **chuỗi dẫn xuất của thanh ghi base**:

| loại | số | nghĩa |
|---|---|---|
| `cell` | **0** | không có store nào ghi vào ô metadata |
| `static-block` | **16** | base = `[klass, #0xb8]` ⇒ ghi vào khối static |
| `instance` | **85** | base là object field thật |
| `unknown` | **1** | base là tham số (`Box_Rewards`, 20002516, store 128-bit `stp`) |

Phân bố offset: `0x50` **45**, `0x54` **20**, `0x58` **37**; trải trên **22 class / 33 method**.

Nói cách khác: nếu chỉ khớp offset thì ba bộ đếm có **102** ứng viên thay vì 6 — sai **17 lần**. Chỉ 16 trong 102 đi qua khối static, và chỉ **6** trong 16 thuộc `GameDatas`.

### 16 store vào khối static

| class | site | offset | ô TypeInfo |
|---|---|---|---|
| **`GameDatas`** | **20070896 · 20071048 · 20071224 · 20071376 · 20071552 · 20071704** | **0x50 / 0x54 / 0x58** | **`0x2adb000` + `0xaf8`** |
| `GP_PVP_Manager` (+ `d__26`) | 19856096 · 19856176 · 19861392 · 19865664 · 19866208 | 0x50 / 0x58 | `0x2adf000` + `0xfb0` |
| `Map_Get_Datas` | 21064448 · 21067920 | 0x50 / 0x58 | `0x2adc000` + `0x6d8` |
| `Shop_Pack` | 20251232 · 20255028 | 0x50 / 0x58 | `0x2add000` + `0xdc8` |
| `Board_Quest` | 19977176 | 0x50 | `0x2adc000` + `0x298` |

Mười store còn lại ghi vào khối static của **class khác**, ở **cùng offset** — đó chính là thứ khiến một phép quét offset trông như "tìm được người ghi".

## 3. Trả lời mục 32

> mục 32 hỏi: *"a direct static store outside these classes"* — một store static trực tiếp nằm ngoài các class này.

**Không có.** Sáu store vào khối static của `GameDatas` đều nằm trong ba accessor; `outside_stores` trong artifact là **`[]`**. Và điều kiện để ghi được vào khối đó là phải có `GameDatas_c*` (để lấy `static_fields`) — mọi đường đều đi qua ô TypeInfo `0x2adbaf8`.

Vì vậy bước mở rộng quét mà 173 ghi cho mục 32 (*"widen the scan from calls to stores on the three counter cells"*) **đã thực hiện xong**, và kết quả là âm: cái mục đó gọi là "ô đếm" hoá ra là **field static**, nên câu hỏi "có ai store thẳng vào ô không" tự triệt tiêu.

## 4. 176 giữ đúng gì

* Sáu địa chỉ store và ba tên `KeyCount0/1/2` — **đúng**.
* Ghi nhận getter cũng ghi (cache giá trị) — **đúng**, và đúng vì getter ghi vào cùng `static_fields`.
* Giới hạn "corpus ≠ binary" — **giữ nguyên**, xem §5.

## 5. Giới hạn

1. Base là **tham số** thì vẫn `unknown`: 1 ca (`Box_Rewards` 20002516) — không suy gì từ nó.
2. Corpus là các slice đã ghim; method không nằm trong scan nào vẫn vô hình.
3. Giá trị nằm trong khối static sau khi khớp vẫn là `MODEL_NOT_MEASURED runtime`.
4. `Il2CppClass` được suy từ **hình dạng truy cập** (`0xe0` = cổng cctor, `0xb8` = `static_fields`) **cộng** với việc `dump.cs` khai báo static đúng ba offset đó — không phải từ một bảng layout `Il2CppClass` trong repo (repo không có). Nếu ai đó có layout chính thức của bản Unity này thì nên đối chiếu lại; kết luận của report không phụ thuộc vào việc `0xb8` tên là gì, chỉ phụ thuộc vào việc **ba offset là static**.

## 6. Tái lập

```bash
python3 tools/verify/counter_static_writers.py              # 14/14 check, 102 store, 16 static-block
python3 -m unittest tests.test_counter_static_writers -q    # 22 test
```
