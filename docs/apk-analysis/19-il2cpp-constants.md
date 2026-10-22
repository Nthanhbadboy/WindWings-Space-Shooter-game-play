# Hằng số bóc từ thân hàm IL2CPP

> **Kết luận tạm thời.** Các giá trị dưới đây là hằng số *nhìn thấy trong mã máy*,
> chưa chắc là giá trị thiết kế cuối cùng: có thể là hằng số phụ (epsilon, clamp,
> hệ số nội suy), và có thể bị che bởi phép tính khác. Dùng để **đối chiếu**, không
> phải để chép nguyên. Dữ liệu thô: `reverse-engineering/raw/il2cpp-consts/`.

- .so: `ls` — arm
- class đích: **1**, method: **1**

## `GameDatas` — cờ save/anti-cheat, cheat counters

- method đọc được: **1**, có hằng số: **0**
- float: `—`
- int: `—`

## Đọc tiếp

- Mỗi class có file JSON: `reverse-engineering/raw/il2cpp-consts/<Class>.json`
  (từng method, từng hằng số, kèm địa chỉ).
- Disassembly có chú thích: `<Class>.asm.txt`.
- Hằng số chỉ có nghĩa khi đọc cùng control flow — file `.asm.txt` để đối chiếu.
