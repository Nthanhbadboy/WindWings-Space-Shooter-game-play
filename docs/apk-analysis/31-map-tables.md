# 31 — Bảng map đã giải bằng token InitializeArray (A−)

> Mốc giải mã 2026-10-23. Mọi giá trị lấy trực tiếp từ APK (asm .cctor +
> blob field-default trong `global-metadata.dat`), không suy từ screenshot.

## Cách giải (đã kiểm chứng)

1. `il2cpp_consts.py` ghi với mỗi call `InitializeArray` trong `.cctor`:
   độ dài mảng (`mov w1,#N`) + handle `x20` → slot qword `0x80000000|(kind<<29)|src`.
2. Mọi token của `Map_Get_Datas` đều **lẻ**: `src = 2*ordinal + 1`, ordinal là
   thứ tự field trong type `<PrivateImplementationDetails>` **cùng image**
   (Assembly-CSharp: type 2461, fields 16300..17039 — 740 field).
3. Kiểm: 540/540 token có blob; 521/540 khớp `len(blob)/4` với `len` asm (±3
   do làm tròn 16B). 0 token không giải được trên toàn 20 class
   (`ia-resolved.json`: 573 mảng / 10 method).

→ `datas/map_segments_full.json`: mọi segment của `.cctor` kèm giá trị từng mảng
(nguồn `immediates` = hằng số trong asm, chắc chắn; `blob` = token→PID ở trên).

## Gán field theo hình dạng (mức B, chưa chốt offset static)

| Segment | Hình dạng | Field khả dĩ |
|---|---|---|
| 3–12 | 10 list, tổng 63 mảng len 36 (hoán vị wave) | `AllArenaRandomMaps` (63) |
| 25–34 | 10×10 mảng len 7 | `AllPvPStartMaps`? |
| **35** | **250 mảng, 243×len 3 + 7 immediate** | **`listMapDatas`** |
| 37 | 25 mảng len 20–25 | branch/boss list |
| 38–40, 64–67 | mảng len 3 | fight-boss / endless |
| 43–59 | 17×8 mảng len 1–2 | challenge |
| 68–69 | dài không đều (tới 69) | obstacle / index list |

`listMapDatas` = segment 35 vì: 250 phần tử (khớp vòng lặp campaign của spec),
được dùng bởi logic `GetListWaves`; các segment khác đều có hình dạng chế độ
riêng (Arena 63×36, PvP 7-wave...). `datas/maps.json` = 250 map theo thứ tự
`.cctor`; map *N* (1-based) = phần tử *N−1* (PROVISIONAL về đánh số, nội dung A−).

Thiếu đúng 1 mảng (index 4, IA call mà exporter chưa bắt được token); 41 IA
khác thuộc segment chưa gán field.

## Còn mở

- Offset static store trong `.cctor` để gán segment→field 100% (nâng lên A).
- Bắt nốt 36 IA call bị hụt trong exporter (token qua thanh ghi khác x20).
