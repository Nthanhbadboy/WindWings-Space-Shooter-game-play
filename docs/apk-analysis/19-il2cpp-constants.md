# Hằng số bóc từ thân hàm IL2CPP

> **Kết luận tạm thời.** Các giá trị dưới đây là hằng số *nhìn thấy trong mã máy*,
> chưa chắc là giá trị thiết kế cuối cùng: có thể là hằng số phụ (epsilon, clamp,
> hệ số nội suy), và có thể bị che bởi phép tính khác. Dùng để **đối chiếu**, không
> phải để chép nguyên. Dữ liệu thô: `reverse-engineering/raw/il2cpp-consts/`.

- .so: `libil2cpp.so` — aarch64
- class đích: **12**, method: **305**

## Hàm trả về hằng số (độ tin cậy cao)

Những method mà toàn bộ thân hàm chỉ là `mov w0, #imm; ret` — đây gần như chắc chắn
là giá trị thiết kế, không phải hằng số phụ.

| class | method | giá trị |
|---|---|---:|
| — | chưa tìm thấy | — |

## `GameDatas` — cờ save/anti-cheat, cheat counters

- method đọc được: **73**, có hằng số: **72**
- float: `—`
- int: `2, 3, 5, 6, 7, 8, 10, 14, 15, 16, 22, 23, 24, 26, 40, 64, 96, 100, 250, 500, 3463, 16959, 16960, 26214`
- hằng số dùng trong phép tính: `—`

## `Player_Get_Datas` — chỉ số tàu: HP, damage, tốc độ bắn, giá nâng cấp

- method đọc được: **62**, có hằng số: **61**
- float: `-1.0, 0.25, 0.5, 1.0, 1.25, 1.5, 2.25, 2.5, 3.0, 3.5, 5.0, 8.0, 9.0, 25.0, 30.0`
- int: `2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 21, 24, 30, 48, 58, 64, 78, 98, 108`
- hằng số dùng trong phép tính: `arith:fadd:1.0, arith:fdiv:3.5, arith:fmul:0.5, arith:fmul:1.5, arith:fmul:8.0, arith:fsub:1.0, arith:scvtf:1.25`

## `IAP_Manager` — giá và product id runtime

- method đọc được: **35**, có hằng số: **34**
- float: `—`
- int: `2, 3, 4, 5, 7, 8, 12, 24, 48, 50, 64, 71`
- hằng số dùng trong phép tính: `—`

## `ArenaManager` — arena: rank, mùa, thưởng

- method đọc được: **34**, có hằng số: **27**
- float: `—`
- int: `2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 32, 40, 60, 64, 101, 112, 1000`
- hằng số dùng trong phép tính: `—`

## `Tech_Datas` — tech lab: giá, delta giá, sao

- method đọc được: **25**, có hằng số: **24**
- float: `-4.0, -1.0, 0.5, 1.0, 5.0`
- int: `2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 16, 24, 28, 30, 31, 32, 34, 40, 43, 44, 48, 60, 63`
- hằng số dùng trong phép tính: `arith:fadd:-4.0, arith:fmul:0.5`

## `RankManager` — rank: ngưỡng điểm, thời gian

- method đọc được: **19**, có hằng số: **17**
- float: `10.0`
- int: `2, 8, 16`
- hằng số dùng trong phép tính: `arith:fadd:10.0`

## `Device_Get_Data` — device: stat, giá

- method đọc được: **14**, có hằng số: **13**
- float: `-5.0, 0.5, 1.0, 5.0, 25.0, 30.0`
- int: `2, 3, 4, 5, 8, 9, 11, 12, 16, 17, 24, 28, 32, 38, 48, 56, 57, 96, 999, 1000, 10001, 19923, 1103626240, 1106247680`
- hằng số dùng trong phép tính: `arith:fmul:-5.0, arith:fmul:0.5, arith:fmul:5.0, arith:fsub:1.0`

## `Droid_Data_Balance` — drone: damage, timeout, giá unlock/upgrade

- method đọc được: **13**, có hằng số: **11**
- float: `1.0, 3.0, 4.0, 15.0`
- int: `2, 3, 4, 5, 6, 8, 12, 16, 30, 32, 50, 56, 68, 101, 102, 103, 312, 500, 800, 1120403456, 1135869952, 1140457472`
- hằng số dùng trong phép tính: `arith:fadd:1.0`

## `Stage_Get_Datas` — stage: bonus, delta level/coin/gem, số enemy

- method đọc được: **11**, có hằng số: **10**
- float: `1.0, 1.25, 1.5, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0`
- int: `2, 3, 4, 5, 6, 8, 12, 16, 29, 32, 36, 40, 59, 60, 112, 312, 26214, 30009, 30015, 30016, 30029, 30030, 30039, 31011`
- hằng số dùng trong phép tính: `arith:fmul:1.0, arith:fmul:1.25, arith:fmul:5.0`

## `Map_Get_Datas` — map: wave, danh sách map theo mode

- method đọc được: **10**, có hằng số: **8**
- float: `—`
- int: `2, 3, 4, 6, 9, 10, 16, 43691, 52429`
- hằng số dùng trong phép tính: `—`

## `Enemy_Data_Balance` — enemy: bonus coin/exp, điểm survival/arena/pvp

- method đọc được: **8**, có hằng số: **7**
- float: `0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 6.0, 9.0, 11.0, 15.0, 20.0, 23.0, 25.0, 30.0`
- int: `2, 6, 8, 10, 15, 16, 21, 23, 29, 30, 59, 64, 120, 200, 250, 387, 450, 998, 1537, 24464, 30010, 30014, 30015, 30016`
- hằng số dùng trong phép tính: `arith:fadd:1.0, arith:fmul:9.0, arith:fmul:11.0, arith:fmul:25.0`

## `Player_Datas` — dữ liệu runtime của player

- method đọc được: **1**, có hằng số: **1**
- float: `—`
- int: `30, 36, 64, 96, 1120403456`
- hằng số dùng trong phép tính: `—`

## Đọc tiếp

- Mỗi class có file JSON: `reverse-engineering/raw/il2cpp-consts/<Class>.json`
  (từng method, từng hằng số, kèm địa chỉ).
- Disassembly có chú thích: `<Class>.asm.txt`.
- Hằng số chỉ có nghĩa khi đọc cùng control flow — file `.asm.txt` để đối chiếu.
