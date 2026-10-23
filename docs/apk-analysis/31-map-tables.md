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

## Gán field — ĐÃ CHỐT ở mức asm (A)

Nối 3 nguồn: offset field trong dump.cs, lệnh `str` vào statics cuối mỗi
nhóm trong `.cctor`, và thứ tự segment:

| Offset | Field | Segment |
|---|---|---|
| 0x0 | `listMapTryPlayerDatas` | 1 |
| 0x8 | `AllArenaStartMaps` | 2–12 (63 mảng len 36) |
| 0x10 | `AllArenaRandomMaps` | 13–23 |
| 0x18 | `AllPvPStartMaps` | 24–34 (10×10 len 7) |
| 0x20 | `mapCurrentPlayTest` = 0 | — |
| **0x28** | **`listMapDatas`** | **35 (250 mảng)** |
| 0x30 | `listMapBranchDatas` | 36–40 |
| 0x38 | `listIdBosses` (Dictionary) | — |
| 0x40 | `listMapFightBossDatas` | 41–62 |
| 0x48 | `listMapChallangeDatas` | 63–67 |
| 0x50 | `listMapEndlessDatas` | 68 |
| 0x58 | `listMapObstacleDatas` | 69 |
| 0x60 | `mapChallangeIndexs` (int[]) | cuối .cctor |

→ `datas/maps.json` = `listMapDatas` theo thứ tự `.cctor` (nội dung A;
đánh số map 1-based vẫn theo quy ước phần tử *N−1*).

Thiếu đúng 1 mảng (index 4, IA call mà exporter chưa bắt được token); 41 IA
khác thuộc segment chưa gán field.

## Còn mở

- Offset static store trong `.cctor` để gán segment→field 100% (nâng lên A).
- Bắt nốt 36 IA call bị hụt trong exporter (token qua thanh ghi khác x20).

### Cảnh báo kiểm toán bổ sung

Nhãn A ở trên chỉ áp dụng việc gán **segment 35 → field @0x28**.
Resolver token còn là giả thuyết được hỗ trợ mạnh, chưa xác minh runtime:
19/540 mẫu chưa khớp độ dài, exporter bỏ sót call và chưa loại trừ token cũ
trong thanh ghi. Vì vậy nội dung `maps.json` / `ia-resolved.json` vẫn
**PROVISIONAL**, không dùng nhãn PASS hoàn tất cho toàn bộ T1.
Bảng device hiện là 11 blob bắt được, không phải đã chứng minh danh sách
11 device: asm có call khởi tạo đầu tiên chưa bắt được, và blob cuối có thể
thuộc field khác. Chưa gán tên/ý nghĩa cho các hàng.

Kiểm toán exporter: đã khôi phục đoạn ghi field-defaults.json bị xóa nhầm
khi dọn probe; các raw probe đã có được giữ để truy vết, ngừng sinh mới.

### Vòng sửa capture tiếp theo

`c5859b662`: bỏ chọn wrapper theo tần suất; chỉ ghi sự kiện tại đúng
`bl 0x205b07c` (được script.json nhận diện InitializeArray). Token x1 bị
xóa sau call theo ABI để tránh lấy token của mảng trước tại array-new.
Output mới giữ cả call site, array-new site, raw blob, field và length_valid.
**Chưa có kết quả tái xuất được lưu:** Actions 39918069220 thất bại tại
Commit reports; dữ liệu 540 token hiện tại vẫn là bản cũ. Lệnh rerun bị GitHub
từ chối (workflow không rerun được). Không nâng mức tin cậy từ bản sửa code này.
