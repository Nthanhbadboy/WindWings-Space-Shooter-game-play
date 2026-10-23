# Đối chiếu dữ liệu tĩnh ↔ dữ liệu chạy thật — 23/10

Hai nguồn độc lập, giờ đối chiếu được:

| Nguồn | Ở đâu | Cách sinh ra |
|---|---|---|
| **Tĩnh** | nhánh `arena/ef6b75ef-windwings-space-shooter-game-p` (`8492c220`) | bóc `.cctor` của IL2CPP bằng asm + relocation, **không chạy game** |
| **Động** | thư mục này (`docs/apk-analysis/ramus/2026-10-23-phone/`) | `/statics` của bridge trong game đang chạy trên Mate 20 X |

Hai đường **không** dùng chung code, không dùng chung giả định ⇒ chỗ nào khớp thì là bằng chứng
thật cho cả hai; chỗ nào lệch thì một trong hai đang sai và phải tìm ra cái nào.

> **Cảnh báo bản (áp cho mọi dòng dưới):** nguồn động chạy trên
> `com.Gcenter.WindWings.SpaceShooter.Premium` **1.0.69**; nguồn tĩnh bóc từ
> `com.Wind.wings.Space.Shooter` **1.3.118**. Khớp nhau ⇒ **củng cố**; lệch nhau ⇒ **có thể chỉ
> là khác bản**, không nhất thiết là lỗi.

---

## 1. Khớp — `listMapDatas` có đúng 250 phần tử

| | Giá trị | Nguồn |
|---|---:|---|
| Tĩnh | **250** | `datas/maps.json` · `len(d["maps"])` |
| Động | **250** | `statics_Map_Get_Datas.json` · `.fields.listMapDatas_count` |

**Mức A.** Đây là phép đối chiếu mạnh nhất hiện có: con số 250 là **độ dài của một mảng lồng**,
không phải một giá trị đơn lẻ dễ trùng ngẫu nhiên. Nó nói rằng việc bóc `.cctor` của
`Map_Get_Datas` đã tìm **đúng cấu trúc**, không phải một mảng khác cùng class.

Điều **chưa** chứng minh được: **nội dung** từng phần tử có đúng không. Nguồn động chỉ trả về
128 phần tử, và cả 128 đều là **chuỗi tên type** (lỗi đọc mảng lồng của bridge, đã sửa ở commit
`9fb827c` nhưng **chưa chạy lại trên điện thoại**). Nguồn tĩnh thì tự nhận là tạm thời:

> `datas/map_waves_candidate.json` ghi nguyên văn: *"TẠM THỜI … 7 mảng đầu chắc chắn (immediate);
> 243 mảng sau ghép theo thứ tự blob PID — chưa xác thực bằng token."*

⇒ **7 mảng đầu** dùng được làm mốc so sánh; **243 mảng sau** thì không, vì chúng được ghép theo
thứ tự blob, có thể lệch.

## 2. Lệch — `listStatValues`: tĩnh 12 mảng, động 10

| | Giá trị |
|---|---|
| Tĩnh (`datas/device_table.json`) | **12** mảng, mỗi mảng **5** số thực |
| Động (`statics_Device_Get_Data.json`) | **10** phần tử trong `listStatValues`, mỗi phần tử là `Il2CppStructArray<float>` (= `float[5]`) |

**Không khớp: 12 ≠ 10.** Ba khả năng, chưa cái nào được chứng minh:

1. **Bản mod đổi số thiết bị** — 1.0.69 có 10, 1.3.118 có 12. Khả năng cao nhất, vì đây là bảng
   cân bằng hay bị chỉnh khi phát hành.
2. **Bóc tĩnh gom dư** — chính file tĩnh đã tự cảnh báo: *"12 array captures, NOT 12 proven
   devices; field grouping pending"*. Tức 12 mảng đó có thể thuộc nhiều field khác nhau, không
   phải tất cả là phần tử của một `List`.
3. **Bridge cắt bớt** — nhưng `_count = 10` và mảng có 10 phần tử, tức **không** bị cắt ở 128.
   Loại trừ được khả năng này.

> Nhận định: đây là **lỗ hổng thật** trong chuỗi bằng chứng của blocker `B1/T5` (bảng stat device).
> Cho tới khi một lần chạy lấy được **nội dung** 10 mảng đó (sau bản sửa `arr`/`depth`), không nên
> dùng `device_table.json` như số liệu cuối.

## 3. Số liệu tĩnh có sẵn nhưng **chưa** dùng

Nhánh kia có nhiều file mà bộ spec hiện tại chỉ trích dẫn chứ chưa khai thác:

| File (nhánh `ef6b75ef`) | Kích thước | Liên quan tới |
|---|---:|---|
| `datas/map_table_segments.json` | 70.632 B | `Map_Get_Datas` 11 cấu trúc — `DIFFICULTY_MODES` §7 |
| `datas/map_segments_full.json` | — | cùng chủ đề |
| `datas/device_table.json` | 3.732 B | bảng stat device (mục 2 ở trên) |
| `datas/enemy_hp_by_id.json` | — | `ENEMY_HP_RUNTIME` |
| `datas/boss_hp.json` · `bosses.json` | — | `BOSSES` |
| `datas/verify_checks.json` | — | bộ tự kiểm của chính pipeline bóc |
| `datas/validate.py` | — | script kiểm dữ liệu |
| `reverse-engineering/raw/typetrees/*.jsonl.gz` | 111 class | toàn bộ typetree |

`datas/validate.py` + `verify_checks.json` đáng đọc trước: nếu pipeline đã tự kiểm thì biết ngay
file nào được coi là đã xác thực, file nào còn tạm thời — thay vì đoán.

---

## Còn thiếu / phải đoán

- **Chưa so được nội dung** `listMapDatas`: nguồn động là tên type, nguồn tĩnh là "tạm thời"
  243/250. Cần một lần chạy `collect.sh --local` với `&arr=256&depth=2`.
- **Chưa biết** 12 vs 10 là khác bản hay bóc dư — mục 2 liệt kê 3 khả năng, chưa loại được cái nào.
- **Chưa đọc** `datas/validate.py` để biết pipeline tự đánh dấu mức tin cậy thế nào.
- Mọi so sánh ở đây **vắt qua hai bản game khác nhau**; một phép so trong cùng một bản sẽ mạnh hơn.
