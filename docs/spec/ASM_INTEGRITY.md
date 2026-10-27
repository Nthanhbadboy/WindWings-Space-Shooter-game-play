# Gác cổng asm — **không để cắt cụt im lặng** nữa

> Sự cố ngày 23/10/2026: công cụ export cắt mỗi method ở **4.608 byte** và **không báo gì**.
> Hậu quả: **11/12 file asm bị cụt**, và tôi đã rút ra **3 kết luận sai** rồi **công bố chúng như
> bằng chứng phủ định**. File này tồn tại để việc đó không lặp lại.
>
> Phạm vi: mọi kết luận trong `docs/spec/` có dùng asm. Bản dữ liệu chuẩn: **`6109008c`**.

---

## 0. Sự cố — cái gì đã xảy ra, và cái gì đã bị nói sai

**Cơ chế hỏng:** mỗi method bị cắt ở `4.608 B`. File vẫn mở được, vẫn `grep` ra kết quả, **chỉ thiếu
phần đuôi**. Không có cờ, không có cảnh báo.

**Ba kết luận sai đã công bố (nay đã rút):**

| Đã nói | Thực tế |
|---|---|
| "`.cctor` của `Player_Get_Datas` **không** gán `StartHp`" | `.cctor` bị cắt trước đoạn gán stat — **có gán: 2500** |
| "Không có lệnh ghi `#0x314` (abi7) trong **bất kỳ** asm nào" | 11/12 file cụt ⇒ câu này **vô nghĩa** |
| "`Player_Health.Start()` **không** đụng tới HP" | đúng phần đầu; **thân lambda** ở file khác ghi `StartHealth` |

**Thiệt hại thật:** mất **3 vòng** đi tìm đúng chỗ mà dữ liệu **đã có sẵn**, và tệ hơn — đã trình bày
*vắng mặt bằng chứng* như *bằng chứng vắng mặt*.

---

## 1. Bốn cờ tự kiểm

### Cờ 1 — `size_capped` (công cụ tự báo)

Mỗi method trong `<Class>.json` có `"size_capped": true|false`. **Phải `false` cho 100%.**

```
bản 6109008c:  425/425 method  size_capped = false   ✅
```

### Cờ 2 — **phủ địa chỉ** (quan trọng nhất, không phụ thuộc công cụ)

```
max(địa chỉ lệnh có trong .asm.txt)  >=  max(rva + bytes của mọi method) − 4
```

Nếu file dừng **trước** địa chỉ đó ⇒ **cụt thật**. Phép này bắt được cả trường hợp **thiếu 2 lệnh**.

### Cờ 3 — **opcode cuối**

Lệnh cuối phải là `ret` · `b` · `br` · `retab` · hoặc `bl` tới helper `0x110d250/0x110d258`
(throw helper — không bao giờ trả về).

### Cờ 4 — **method phải CÓ MẶT** (thêm 23/10, sau khi kiểm chéo)

```
mọi method trong <Class>.json   →   phải có khối ";;; <tên>" trong .asm.txt
                                →   và khối đó phải có ≥1 dòng lệnh
```

**Vì sao phải thêm:** cờ 2 chỉ kiểm **đuôi file**. Một method bị bỏ sót **ở giữa** vẫn cho file kết
thúc đúng ⇒ cờ 2 PASS. Đo trên bản `68ce86a7`: **25 method vắng hẳn** khỏi `asm.txt` trên 15/17 class
— **24 là stub 8 B** (vô hại) và **1 là `Player_Ingame.get_IsAttacking` 32 B** (mất thật, cách method
gần nhất **>0x60** ⇒ đúng là lỗ hổng giữa file, không phải cụt đuôi).

> ⚠ **Bẫy đã gặp ở nhánh dữ liệu:** họ thêm cờ `ends_clean` = *"có `ret` trong ≤48 lệnh cuối"*.
> Với method **vắng mặt**, danh sách lệnh **rỗng** ⇒ điều kiện thoả **vacuous** ⇒ cờ trả **`True`**.
> Kết quả: `RankManager.ctor` **không có trong asm** mà vẫn được báo "sạch", và `T2` kết luận
> *"không thiếu byte nào"* — **sai**. **Cờ báo "sạch" cho file thiếu method là cờ tệ hơn không có cờ.**
> Sửa tối thiểu: `ends_clean = present and last_op in {...}`.

**Ngoại lệ có thật:** `Player_Datas.asm.txt` **lan sang class kế** (dumper ghi liền mạch theo địa chỉ),
nên lệnh cuối của nó thuộc `Player_Health` và **không** cần kiểm opcode. Cờ ghi
`lan sang class kế (+N B)` — đây là **thông tin**, không phải lỗi.

> Chính vì lan như vậy mà tôi đọc được `Player_Health.Start()` **trước khi** công cụ được sửa.

---

## 2. Script — chạy được, không cần cài gì

Lưu thành `asm_guard.py`, chạy `python3 asm_guard.py <thư-mục-il2cpp-consts>`.
**exit code = 0** nghĩa là tất cả PASS.

```python
#!/usr/bin/env python3
"""Gác cổng: kiểm file asm IL2CPP có bị cắt cụt / thiếu method không.

Dùng:  python3 asm_guard.py <thư-mục-il2cpp-consts>
Trả về exit code 0 nếu TẤT CẢ pass, 1 nếu có file fail.

4 cờ: ① size_capped ② phủ địa chỉ ③ opcode cuối ④ method phải CÓ MẶT
"""
import sys, os, glob, json

TERM = {"ret", "b", "br", "retab"}


def check(d):
    rows, fail = [], 0
    for jf in sorted(glob.glob(os.path.join(d, "*.json"))):
        cls = os.path.basename(jf)[:-5]
        af = os.path.join(d, cls + ".asm.txt")
        if not os.path.exists(af):
            rows.append((cls, 0, 0, "", "", "FAIL: thiếu .asm.txt"))
            fail += 1
            continue
        ms = json.load(open(jf, encoding="utf-8"))["methods"]
        capped = sum(1 for m in ms if m.get("size_capped"))
        end = max(int(m["rva"], 16) + m.get("bytes", 0) for m in ms) - 4
        lines = [l.rstrip("\n") for l in open(af, encoding="utf-8")]
        ins = [l.strip() for l in lines
               if l.strip().startswith("0x") and ":" in l]
        if not ins:
            rows.append((cls, len(ms), 0, "", "", "FAIL: rỗng"))
            fail += 1
            continue
        # --- cờ 4: method khai trong JSON phải có khối ";;; <tên>" trong asm
        hdr = {l[4:].split("  ")[0].strip() for l in lines if l.startswith(";;; ")}
        gone = [m["method"] for m in ms if m["method"] not in hdr]
        hard = [n for n in gone
                if int(next(m["bytes"] for m in ms if m["method"] == n)) > 8]
        mx = max(int(i.split(":")[0], 16) for i in ins)
        op = ins[-1].split(":", 1)[1].strip().split()[0]
        ok_cov = mx >= end
        spill = mx > end            # file chứa cả thân method của class KẾ
        ok_op = spill or op in TERM or "110d25" in ins[-1]
        ok = ok_cov and ok_op and capped == 0 and not hard
        if not ok:
            fail += 1
        why = []
        if not ok_cov:
            why.append("thiếu %d B" % (end - mx))
        if not ok_op:
            why.append("opcode cuối=%s" % op)
        if spill:
            why.append("lan sang class kế (+%d B)" % (mx - end))
        if capped:
            why.append("%d method bị cap" % capped)
        if gone:
            why.append("vắng %d method%s" % (
                len(gone), " (%s… %d B)" % (hard[0], int(
                    next(m["bytes"] for m in ms if m["method"] == hard[0])))
                if hard else " — toàn stub ≤8 B"))
        rows.append((cls, len(ms), len(ins), hex(mx), hex(end),
                     "PASS" if ok else "FAIL: " + ", ".join(why)))
    w = max([len(r[0]) for r in rows] + [5])
    print("%-*s %5s %6s %11s %11s  %s" % (w, "class", "mth", "lệnh", "max asm", "cần tới", "cờ"))
    for r in rows:
        print("%-*s %5d %6d %11s %11s  %s" % (w, r[0], r[1], r[2], r[3], r[4], r[5]))
    print("\n%d/%d PASS" % (len(rows) - fail, len(rows)))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(check(sys.argv[1] if len(sys.argv) > 1 else "."))
```

---

## 3. Baseline — chạy thật, không phải chép tay

### 3.1 Bản `6109008c`

```
class                mth   lệnh     max asm     cần tới  cờ
ArenaManager          34   1624   0x15a4414   0x15a4414  PASS
Device_Get_Data       14   1007   0x1257038   0x1257038  PASS
Droid_Data_Balance    13    565   0x1452014   0x1452014  PASS
Enemy_Data_Balance     8   1062   0x13217f8   0x13217f8  PASS
GameDatas             73   4385   0x1327bcc   0x1327bcc  PASS
IAP_Manager           35   2093   0x13fa8c4   0x13fa8c4  PASS
Map_Get_Datas         10  25996   0x14178e4   0x14178e4  PASS
Player_Ability        46   3462   0x1474abc   0x1474abc  PASS
Player_Attack         19    798   0x147a078   0x147a078  PASS
Player_Datas           1    256   0x14c6f48   0x14c6b50  PASS
Player_Get_Datas      62   4362   0x14e6280   0x14e6280  PASS
Player_Health         12   1271   0x14c7f80   0x14c7f80  PASS
Player_Ingame         20    661   0x14bc184   0x14bc184  PASS
Player_Talent         23   2003   0x14bf6a0   0x14bf6a0  PASS
RankManager           19    704   0x127cb80   0x127cb88  FAIL: thiếu 8 B
Stage_Get_Datas       11   2937   0x12c8374   0x12c8374  PASS
Tech_Datas            25   1919   0x13a1dd0   0x13a1dd0  PASS

16/17 PASS
```

### Phát hiện khi chạy lần đầu

| File | Vấn đề | Ảnh hưởng |
|---|---|---|
| **`RankManager`** | **thiếu 8 B** = 2 lệnh — method `ctor` (`0x127cb84`, 8 B) | **không ảnh hưởng kết luận** (ctor rỗng); nhưng **cờ đã bắt đúng**, chứng minh bộ kiểm hoạt động |
| `Player_Datas` | lan sang class kế `+0x3F8` B | **có lợi** — nhờ đó đọc được `Player_Health` trước khi có file riêng |

⇒ **16/17 PASS.** File duy nhất fail là một `ctor` rỗng ⇒ **không có kết luận nào trong SPEC bị ảnh hưởng
ở bản này**. Nhưng quy tắc dưới đây vẫn áp dụng, vì lần sau có thể là `.cctor`.

> ⚠ **ĐÍNH CHÍNH 23/10:** tôi từng gọi FAIL này là *"dương tính giả"*. **Không phải.**
> Kiểm lại bản `68ce86a7`: `RankManager.asm.txt` **vẫn dừng ở `0x127cb80`**, `;;; ctor` (`0x127cb84`, 8 B)
> **vẫn không có trong file**. Vậy phép đo **đúng**; chỉ có **hệ quả là vô hại** (ctor rỗng). Ghi
> "dương tính giả" sẽ khiến lần sau một FAIL thật bị bỏ qua.

### 3.2 Bản `68ce86a7` — thêm cờ 4

```
17 class · 425 method
  có header + có lệnh      400
  vắng hẳn khỏi asm.txt     25   ← cờ 4 bắt
  header nhưng 0 lệnh        0
  size_capped = false      425/425
  phủ địa chỉ FAIL           1   RankManager  (thiếu 8 B)
  cờ 4 FAIL                  1   Player_Ingame (vắng 3 method, 1 cái 32 B)
  ─────────────────────────────────────────
  KẾT QUẢ                   15/17 PASS   (bản 6109008c: 16/17)
```

⚠ **Chú ý về `asm.txt`:** 17 file asm ở `68ce86a7` **giống hệt** `6109008c` — 21 commit mới chỉ làm
giàu `*.json` (hằng số/RVA), **không** export lại thân hàm. Nghĩa là **25 method vắng mặt đã có từ
trước**, chỉ là bản trước tôi **chưa kiểm** (tôi tự ghi ở §6 là "chưa kiểm"). Nay đã kiểm.

25 method vắng mặt nằm ở **15/17 class**; **24/25 là stub 8 B**, **1/25 là 32 B**
(`Player_Ingame.get_IsAttacking` — `set_IsAttacking` **còn**, nên cứu được field `@0x2c`). ⇒ **Cờ 4 bắt được một lỗ hổng mà cờ 2 không thấy** — đúng mục đích
tôi đã ghi ở §6 (mục 2) là "chưa kiểm". Nay **đã kiểm**.

---

## 3.5 Quy tắc **phép kiểm phải có ca có thể thất bại**

Một phép kiểm chỉ có giá trị nếu **nêu được một kết quả đầu vào làm nó FAIL**.

Ca thật, 23/10: tôi trích 117 cặp `(A,B)` từ `.cctor` của `Map_Get_Datas` và kiểm
*"B có phải tên wave không"* → **117/117 hợp lệ**. Nghe rất mạnh. Nhưng:

```
Wave_0000 … Wave_0212 đều tồn tại  ⇒  213/213 giá trị 0..212 "là wave"
```

⇒ với mọi `B ≤ 212` phép kiểm **luôn đúng bất kể B nghĩa là gì**. **Phép kiểm rỗng.**

Phép kiểm **có lực** thay vào đó là **kiểm thứ tự**: các wave boss phải xuất hiện theo đúng thứ tự
`7001, 7002, 7003…`. Kết quả: `9010, 7001, 7003, 7002, 7004, 7005, 7006, 7005…` — **lệch, có lặp,
chỉ phủ 17/45**. ⇒ giả thuyết **bị bác**, và nhờ vậy tôi **không** ghi bảng đó vào SPEC.

| Loại phép kiểm | Có giá trị? | Ví dụ |
|---|---|---|
| "giá trị nằm trong miền hợp lệ" khi miền hợp lệ phủ gần hết miền thực tế | ❌ **rỗng** | 117/117 "là wave" |
| "thứ tự khớp nguồn độc lập" | ✅ | thứ tự wave boss |
| "tổng khớp một con số đã biết" | ✅ | `Σ len × copies = 45.659` |
| "cùng kết quả bằng bộ đọc thứ hai" | ✅ | `StartHp` 2500 hai nguồn |

---

## 4. Quy tắc bắt buộc — định nghĩa **"được phép phủ định"**

Một câu dạng *"không có / không tồn tại / không bao giờ"* **chỉ được viết** khi **cả 3** điều đúng:

1. `asm_guard.py` cho **PASS** trên file chứa class đó (hoặc file lan sang và **đã** kiểm địa chỉ);
2. phạm vi được ghi rõ: *"trong 17 class đã export"*, kèm danh sách;
3. có **điều kiện lật ngược** đi kèm.

Nếu **FAIL** ⇒ chỉ được viết: **"không thấy trong phần đã export"**, kèm toạ độ thiếu.

**Mẫu dán vào mọi kết luận âm tính:**

```
[asm: <Class> @ <rva-đầu>..<rva-cuối>, PASS 16/17, size_capped 0/425]
```

**Mỗi file SPEC có kết luận âm tính phải mang dòng đóng dấu ở đầu:**

```
> **asm-check:** 16/17 PASS · size_capped 0/425 · FAIL: RankManager (8 B, ctor rỗng)
```

---

## 5. Khi có bản dữ liệu mới — 4 bước, không bỏ bước nào

1. Chạy `asm_guard.py` trên thư mục mới; **FAIL thì dừng**, không đọc tiếp.
2. So **17 dòng baseline** ở §3: số method và địa chỉ cuối **phải khớp**; lệch ⇒ ghi vào `DATA_SYNC`.
3. Chạy lại các con số đã công bố (đặc biệt `enemy_hp.json`, `waves.json`) — bản `6109008c` đã làm
   **7 số đổi giá trị** (`DATA_SYNC` §7.31c).
4. Cập nhật dòng đóng dấu ở §4 trong **mọi** file có kết luận âm tính.

---

## 6. Còn thiếu / phải đoán

1. **`RankManager` vẫn thiếu 8 B** — vẫn còn ở `68ce86a7`. Nay đã rõ: **ctor rỗng** ⇒ **vô hại**,
   nhưng **chưa** đóng (cờ vẫn FAIL).
2. ~~Cờ 2 không kiểm được lỗ hổng giữa file~~ → **đã có cờ 4** (§1). Kết quả lần đầu: **25 method vắng mặt**,
   trong đó **1 method 32 B mất thật** (`Player_Ingame.get_IsAttacking`).
   **Việc còn lại:** `IsAttacking` phải suy từ trạng thái trong bản clone — **không** đọc được từ asm.
   `ArenaManager` 33 header / 34 method vẫn lệch 1 — **chưa** phân định (nested class).
3. Baseline gắn với **một bản APK** (`v1.3.118`). Bản game khác ⇒ **mọi số trong SPEC phải đo lại**.
