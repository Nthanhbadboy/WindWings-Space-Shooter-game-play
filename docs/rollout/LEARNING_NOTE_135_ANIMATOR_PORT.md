# Learning-note 135 — tầng apply/evaluate + channel setter, dùng cho port Godot

**Nguồn:** chu kỳ 135 của lane `ef6b75ef`, static-only trên `libunity.so` gốc.
Artifact `datas/l3_ef6b75ef135_native_apply_seed.json.gz` 10434 B
`5c6d7d85dceb25fc46b13a9d7d4d3f83f706b0979c9d7a76b4e25c3e3555b534`; probe
`reverse-engineering/raw/owner135/probe.json.gz` 11743 B `c11aedd5…`; report
`docs/apk-analysis/135-ef6b75ef-native-apply-samplers.md`; handoff PR12 **6442988169**.

Nhãn bằng chứng: mọi mục §1–§2 dưới đây là `STATIC_CONFIRMED` **ở mức byte** (đọc từ body FDE, không
chạy lệnh). Các mục §3 là `INFERRED` khi nói “Godot làm tương đương bằng…”. Không có `RUNTIME_CONFIRMED`
nào trong tài liệu này.

## 1. Số của lớp này (đếm được từ artifact)

| Thân | Vai trò đọc được | Extent |
|---|---|---|
| `6b2ce8` | builder **context apply** (dựng lại map ~0x90 B + 5 byte/word dẫn xuất) | `0x204` |
| `6b6950` | **commit gate** (descriptor hằng `{0x10b0b30, 0x1e}`) | `0xa0` |
| `6b2bdc` | **chọn backend** theo byte `+0x5e5` (2 writer) + nhánh legacy `+0x48f` | `0x10c` |
| `6b784c` | **giải controller**: handle `+0x638`, phụ `+0x198`, chain `6acb84` | `0x344` |
| `6bd5c0` / `6be690` | hai writer, **chỉ đọc phần đầu** (bị cắt ở cap 0x800) | `0x8a4` / `0xa34` |
| `6b6850` | **evaluate companion**: vòng `+0x168`/`+0x178`, scratch `+0x5e8` | `0x100` |
| `6b1538` | **chain walk** có tag (`[node+0x20]&~1`, next `+0x28`, index `slot+0xc`) | `0x9c` |
| `6a99f0` | setter float: 7 case (kind 5..11) qua **jump table `0x152614`** | `0x120` |
| `6a98c4` | setter int (kind 9): registry + `cset ne` + hook | `0xe0` |
| `6a99a4` | setter kind `0x0b`: trả `old != new` | `0x2c` |
| `6a9b90` | release channel: slot `+0x18` arg `0x10` | `0x3c` |
| `3dfa9c` | **interval table**: count `+0x40`, base `+0x30`, stride `0x10` | `0x44` |
| `3d8614` | id → object (0 → null, âm bị loại, fallback `5d83b8(id,-1)`) | `0x50` |
| `518b40` | lazy object `+0x38` + word `+0x40` | `0x44` |
| `6d788c` | indexed child: holder `+0x30`, count `+0x30`, base `+0x20` | `0x40` |
| `6b7cf8` | vector builder: count*8, push `6bba14`, memcpy `109acd0` | `0x60` |
| `6c7060` | bulk builder (chỉ annotate `0x150` B đầu) | `0x108c` |

Tổng 24 thân · 9952 B · 177 chuyển điều khiển · 297 fact byte-verified · 0 string.

## 2. Hợp đồng hành vi mà port phải tái tạo (không phải “tên class”)

1. **Một change token cho mỗi animator.** Context apply có word 0 = `animator[+0x610]`; rebuild chỉ xảy
   ra khi khác. Commit thành công mirror counter vào `context[0x58]`. Nghĩa là: *không* dựng lại bảng
   trạng thái mỗi frame — chỉ khi token đổi.
2. **Hai trạng thái context tách bạch:** “invalid” (word0 = 1, zero `0x08–0x68`, con trỏ `0x90/0xa0/0xa8/0xb0`)
   và “hợp lệ nhưng cũ” (vẫn đi tiếp vào commit gate).
3. **Copy map là hợp đồng dữ liệu**, không phải chi tiết nội bộ: 18 word ở `+0x08..+0x7c` lấy từ 3 nguồn
   (`[source+0x48]`, vector `[source+0x18]`, `[[source+0x18]+0x58]`) + 5 trường dẫn xuất.
4. **Bit “có thể bind”**: `+0x80 = (w54 & w58 & w5c) != -1` — ba word phải cùng khác `-1`; `+0x82` là
   “bảng con thứ nhất khác rỗng”; `+0x84 = -1` hoặc word `+0x50` của phần tử đầu bảng con thứ hai.
5. **Chọn backend bằng dữ liệu, không bằng loại object**: byte `+0x5e5` quyết định writer; hai writer
   **không** ghi cùng entry (arg4 `1` vs `0` vào cùng hàm insert) ⇒ nếu port gộp làm một, phải tách cờ
   cấu hình tương đương để còn đường quay lại.
6. **Change detection ở tầng setter**: `6a98c4`/`6a99a4` trả bool “đã đổi”, và `6a98c4` gọi hook toàn cục
   với `(0, old, new)` *sau* khi so sánh. Port giữ được hành vi “setter trả false khi ghi lại đúng giá
   trị cũ” là giữ được nhịp cập nhật.
7. **Lookup theo interval, không theo id trực tiếp**: `3dfa9c` so `(entry_start - key_start) unsigned <
   key_width` trên bảng stride `0x10`, key lấy từ `x1+0x30`; payload là word thứ 2 của entry.

## 3. Ánh xạ gợi ý sang Godot 4.x (`INFERRED`, không phải yêu cầu)

| Hợp đồng | Cách làm trong Godot | Vì sao khớp |
|---|---|---|
| 1 · change token | một `int` version trên node animator + so sánh trước khi rebuild state cache | đúng cơ chế “đổi mới dựng lại” |
| 2 · invalid state | hàm `invalidate()` set cờ + xoá cache; `is_valid()` đọc cờ | hai trạng thái rõ ràng |
| 4 · bit bind | kiểm 3 word trước khi tạo `Sprite2D`/`AnimationPlayer` con | tránh bind nửa vời |
| 5 · hai backend | hai `Resource` writer cùng interface, chọn bằng `bool` trong dữ liệu | giữ nguyên khác biệt entry |
| 6 · setter trả bool | setter Godot (`set_x`) trả `false` nếu `is_equal_approx` với giá trị cũ | change detection |
| 7 · interval | `Array` sort theo `start` + binary search, so `start - key < width` | cùng ngữ nghĩa |

**Không** suy ra từ tài liệu này: Godot có “Animator” giống Unity, có `+0x610` tương đương, hoặc
`AnimationTree` xử lý được các kind 5..11. Đó là việc của session Godot-coder + verifier.

## 4. Cái KHÔNG có trong learning-note này

- Không có tên class/type nào (static-only, không symbol).
- Không có giá trị runtime: counter `+0x610` thực tế tăng bao nhiêu lần, backend nào được chọn lúc chơi,
  kind nào xuất hiện nhiều — tất cả `UNKNOWN`.
- Hai writer (`6bd5c0`, `6be690`) bị cắt ở 0x800 ⇒ phần thân còn lại **chưa đọc**; đừng dùng note này để
  nói “đã hiểu writer”.
- Jump table `0x152614` chỉ được mô tả từ code dispatch; **target byte chưa decode** ⇒ 7 case là “7 nhánh”,
  không phải “7 kiểu dữ liệu đã đặt tên”.
- Không có kết luận nào về render/pose: chuỗi này là apply/evaluate/channel, không phải pose/blend.

## 5. Nếu port cần thêm từ lane native

Chỉ khi có lệnh user. Ba câu hỏi còn treo đã nêu ở handoff 6442988169: (a) đọc tiếp writer nào, (b) có tách
`6c7060` thành chu kỳ riêng với cap lớn hơn, (c) `+0x610` có cần thêm bằng chứng runtime. Theo lệnh hiện
tại, lane native **dừng**; note này là đầu vào đủ để Godot-coder dựng cơ chế ở §2.
