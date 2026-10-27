# 177 — `Board_PVP..ctor` dựng **bảy** collection, sáu trong đó lấy từ chính APK

**Trạng thái:** `DECODED_STATIC` (slice đã ghim; không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Mỗi dòng của bảng đến từ `datas/l2_535b0541_pvp_array_init.json.gz`.
**Artifact:** `datas/l2_535b0541_pvp_array_init.json.gz` — **1965 B**, sha256 `388f4fbfdb00d2b9c0b3d9930e27c7a5564b6c51d87976203896b1e5df871ced`
**Verifier:** `tools/verify/pvp_array_init.py` (**12 check**) · **Test:** `tests/test_pvp_array_init.py` (**20 test**)
**Sửa:** cách đọc mục **30/39/40** của audit (chưa đổi verdict — xem §5)

> Số hiệu: bản CLAIM đầu tiên của report này ghi nhầm là **169**; 169 đã là `pvp_reward_arrays`. Report này là **177**.

---

## 0. TL;DR

| | |
|---|---|
| audit (30/39/40) nói | nội dung hai blob `Board_PVP` (`rewardValues`, `rewardScales`) **cần dữ liệu được phục vụ** |
| `.ctor` (19796420, 500 B / 125 lệnh) đo được | **bảy** collection, **sáu** mảng độ dài **6** dựng bằng `RuntimeHelpers.InitializeArray` từ `<PrivateImplementationDetails>` — dữ liệu **nằm trong APK** |
| thêm | `+0x1b0` = `List<object>`, **không có** trong bảng field trước đó (cả 133 lẫn 173) |
| còn thiếu | **ghép ô → blob**: cần bảng *metadata usage*, repo không có (`ia-resolved.json` có 17 bucket, không có `Board_PVP`) |

Nói cách khác: câu hỏi không còn là "chờ server trả gì", mà là "ô `0x2ae0008` trỏ tới blob nào" — một việc **PIN-RAW**, không phải việc thiết bị.

---

## 1. Bảy store trong ctor

| offset | loại | độ dài | ô dữ liệu | lớp phần tử | lệnh khởi tạo |
|---|---|---|---|---|---|
| `+0x198` | array | **6** | `0x2ae0008` | `0x2add318` | `InitializeArray` (19796684) |
| `+0x1a0` | array | **6** | `0x2ae0010` | `0x2add318` | 19796716 |
| `+0x1a8` | array | **6** | `0x2ae0018` | **`0x2add350`** | 19796748 |
| `+0x1b0` | **`List<object>`** | — | `0x2ae0028` (tham số) | `List<object>..ctor` | 19796772 |
| `+0x208` | array | **6** | `0x2ae0030` | `0x2add318` | 19796804 |
| `+0x210` | array | **6** | `0x2ae0038` | `0x2add318` | 19796836 |
| `+0x218` | array | **6** | `0x2ae0040` | `0x2add318` | 19796876 |

Hai chi tiết đáng chú ý:

1. **`+0x1a8` dùng lớp phần tử khác** (`0x2add350` thay vì `0x2add318`) — đúng như 133 nói `rewardScales` là `float[]` còn các mảng kia là `int[]`. Đây là bằng chứng độc lập cho kiểu phần tử, lấy từ chính ctor chứ không từ khai báo.
2. **`+0x1b0` là `List<object>`** — dựng bằng cặp `il2cpp_codegen_object_new` + `List<object>..ctor` (29193868), không qua `newarr`/`InitializeArray`. Nó được đọc ở 19800320 (`OnLoaded`), 19811460 (`<IESummarySeasonRewards>b__1`) và trong `MoveNext` — tức là danh sách làm việc của màn PvP, không phải bảng thưởng.

`.ctor` kết thúc bằng nhảy tới `Board..ctor` (19131072) — đúng thứ tự khởi tạo của một `MonoBehaviour` con.

## 2. Vì sao "phục vụ" là cách đọc sai

Ba mục 30/39/40 được đánh `POLICY` với lý do *"cần bảng metadata usage để đặt tên cell"*. Điều đó vẫn đúng. Nhưng "hai blob cần payload phục vụ" thì không: ctor chứng minh dữ liệu khởi tạo **có sẵn trong APK**, cùng đường với mọi mảng tĩnh khác của game. Cái thiếu là **liên kết** ô → blob, và liên kết đó nằm trong `global-metadata.dat`, không nằm trên server.

Hệ quả cho hợp đồng của 173: mục 30/39/40 nên đổi `kind` từ `POLICY` sang **`PIN-RAW`** khi audit được làm mới — việc cần làm là ghim thêm raw có bảng usage, không phải xin quyền probe thiết bị.

## 3. Corpus blob đã có trong repo

`reverse-engineering/il2cpp/field-defaults.json` (10493 field) chứa **982** field `<PrivateImplementationDetails>`, mỗi field có `raw` hex và `ints` đã giải mã; **99** trong đó dài đúng 24 byte — đúng kích thước sáu mảng ở trên. Nghĩa là **dữ liệu đã có**; chỉ thiếu ánh xạ ô → tên field.

Đã thử ghép bằng băm nội dung (tên field PID là hash) trên hai mẫu: **không khớp** với `sha1(raw)` lẫn các biến thể cắt tiền tố/hậu tố. Ghi lại như một kết quả âm để người sau không thử lại lần nữa.

## 4. Giới hạn

* Sáu mảng **có** dữ liệu trong APK, nhưng **giá trị cụ thể** chưa đọc được ⇒ vẫn `NOT_BOUND`, chưa phải "đã giải".
* `List<object>` ở `+0x1b0` chỉ được nhận là `List<object>`; nội dung phần tử là gì thì cần đọc `OnLoaded`, chưa làm ở đây.
* Mọi thứ hiển thị trên thiết bị vẫn `MODEL_NOT_MEASURED runtime`.

## 5. Không đổi verdict trong report này

Đổi verdict mục 30/39/40 là đổi byte artifact của audit ⇒ 168 và 173 phải sinh lại theo thứ tự. Việc đó thuộc report **refresh audit**, và ghi chú đúng cho nó là: *"dữ liệu nằm trong APK; thiếu liên kết ô→blob (`PIN-RAW`)"* — không phải "cần server".

## 6. Tái lập

```bash
python3 tools/verify/pvp_array_init.py                 # 12/12 check, 7 collection
python3 -m unittest tests.test_pvp_array_init -q       # 20 test
```
