# 135 — `PVP_Manager.MaxRankStars`: 10 thang sao, bind vào byte thật (+ xác nhận 128)

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY; phần "sao di chuyển trong trận" là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_max_rank_stars.json.gz` (2559 B, sha256 `004898a23e08004f4ff595b1734605a5403293ee8d13691f5f3a8b55bd69a69c`)
**Báo cáo trước:** 127 (§6.5 `not_decoded` "`MaxRankStars` **giá trị**"), 128 (§3.4 đọc giá trị, nhưng chỉ bằng văn xuôi), 134 (`AllRewards` 43 dòng — dùng làm mốc kiểm chéo).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| `MaxRankStars` có mấy phần tử? | **10** (`List<int[]>`, một phần tử mỗi rank 0..9) | 10 lời gọi `InitializeArray` trong `..cctor` |
| Độ dài 10 mảng? | `3,3,4,4,5,5,5,5,5,5` | `mov w1,#len` + `bl 0x110D09C` (newarr) |
| Bao nhiêu blob thật? | **5** — 6 mảng cuối **dùng chung một blob** | `addend` 45960992 lặp 6 lần |
| Giá trị? | `[3,3,3] [4,4,4] [4,4,4,4] [5,5,5,5]` rồi `[5,5,5,5,5]` ×6 | `fieldDefaultValues` + bất biến SHA-256 tên field |
| Báo cáo 128 đúng không? | **ĐÚNG** — xác nhận, không đính chính | §6, 5/5 field khớp digest |
| Ai đọc bảng? | **chưa** thấy trong raw đã pin | 15 method `PVP_Manager` không method nào chạm statics `+0x18` |
| Nghĩa "1 ô = 1 level"? | **suy luận từ độ dài** (9/10 rank khớp `AllRewards`) | §4 — rank 0 là ngoại lệ |

**Một câu:** 44 con số của `MaxRankStars` **đã bind được** vào byte thật: 10 lời gọi `InitializeArray` → 5 field `<PrivateImplementationDetails>` → dữ liệu trong `fieldDefaultValues`, và mỗi field qua được một phép kiểm **không thể may mắn** (tên field chính là `sha256` của đúng lát byte được khai báo). Cái còn thiếu không phải giá trị, mà là **method đọc** — nằm ngoài raw đã pin.

---

## 1. Phương pháp — 4 tầng, mỗi tầng kiểm được

```text
PVP_Manager..cctor (RVA 19916640, 19.944 B)
  ├─ 10 × (mov w1,#len → bl newarr → ldr fieldHandle → bl InitializeArray 0x205B07C)
  │        └─ raw meta-rewards-535b0541: initialize_arrays[] = {initialize_rva, length, addend, token}
  ├─ token  → ordinal  : token_source = token & 0x7FFFFFFF, ordinal = (token_source − 1) / 2
  ├─ ordinal → field    : resolution của 128 (`datas/l2_535b0541_meta_rewards.json.gz`, status "ok")
  └─ field  → byte      : `reverse-engineering/il2cpp/field-defaults.json` (fieldDefaultValues v31)
```

Bốn phép kiểm trong verifier (`tools/verify/max_rank_stars.py`), tất cả **tái tính được**:

| # | Phép kiểm | Vì sao nó chặn được gán sai |
|---|---|---|
| 1 | `declared_bytes == 4 × length` | `newarr` khai 3/4/5 ô ⇒ blob phải đúng 12/16/20 byte; blob khác độ dài bị loại |
| 2 | `len(data) ≥ declared_bytes` và dữ liệu cắt đúng `declared_bytes` | phần đệm (`trailing_hex`) không lẫn vào giá trị |
| 3 | **`sha256(data).upper() == tên field`** | Roslyn đặt tên `<PrivateImplementationDetails>.<HEX>` bằng `sha256` của chính byte khởi tạo — gán sai field là sai digest, **5/5 khớp** |
| 4 | `ordinal == (token_source − 1) / 2` và `token_source` lẻ | cùng quy ước `2*ordinal+1` mà `ia-resolved.json` ghi; token lẻ/ordinal lệch là fail |

Phép kiểm 3 là phép kiểm mạnh nhất: nó biến "field nào của bảng PID" từ **niềm tin vào báo cáo trước** thành **số học tự kiểm**.

---

## 2. Bảng 10 rank

| rank | ô | `int[]` | blob (addend) | field `<PID>.<HEX>` | token | ordinal | RVA `InitializeArray` |
|---:|---:|---|---:|---|---:|---:|---:|
| 0 | 3 | `[3, 3, 3]` | 45958200 | `02433989…FD250` | 13 | 6 | 19930288 |
| 1 | 3 | `[4, 4, 4]` | 45959168 | `2AFC299A…36E82` | 255 | 127 | 19930420 |
| 2 | 4 | `[4, 4, 4, 4]` | 45963544 | `E55F7043…CE20C` | 1349 | 674 | 19930540 |
| 3 | 4 | `[5, 5, 5, 5]` | 45961144 | `7DE254EA…E134DD` | 749 | 374 | 19930660 |
| 4 | 5 | `[5, 5, 5, 5, 5]` | 45960992 | `785C9B32…FEFFA` | 711 | 355 | 19930780 |
| 5–9 | 5 | *cùng blob* | 45960992 | `785C9B32…FEFFA` | 711 | 355 | 19930892 / 19931004 / 19931116 / 19931228 / 19931340 |

Byte thô (đúng `declared_bytes`, phần đệm đã cắt):

```
02433989…  03000000 03000000 03000000                → [3, 3, 3]
2AFC299A…  04000000 04000000 04000000                → [4, 4, 4]
E55F7043…  04000000 04000000 04000000 04000000       → [4, 4, 4, 4]
7DE254EA…  05000000 05000000 05000000 05000000       → [5, 5, 5, 5]
785C9B32…  05000000 05000000 05000000 05000000 05000000 → [5, 5, 5, 5, 5]
```

⇒ `MaxRankStars[rank] = int[]{ N, N, … }` với `N = 3, 4, 4, 5, 5…` — mỗi **level** trong rank có **cùng** một trần sao. Đây là bảng **trần sao theo level**, không phải bảng cộng dồn: mọi phần tử trong một mảng bằng nhau, nên không có "ngưỡng tăng dần" nào bị hiểu sai.

---

## 3. Vì sao 6 mảng cuối dùng chung blob (không phải lỗi trích xuất)

Cả 6 lời gọi `InitializeArray` ở RVA 19930780…19931340 trỏ **cùng** `addend` 45960992 và **cùng** field `785C9B32…`. Roslyn gộp các mảng khởi tạo giống nhau thành **một** field PID duy nhất — nội dung `[5,5,5,5,5]` giống nhau ở 6 rank ⇒ 1 blob, 6 chỗ dùng. Vì vậy "chỉ có 5 blob" là **đúng cấu trúc**, và bất kỳ báo cáo nào liệt kê 10 blob khác nhau đều sai.

Hệ quả kiểm tra: nếu 6 mảng đó thật sự khác nhau, `addend` phải khác → raw đã pin **không** thể hiện điều đó ⇒ giả thuyết "10 bảng khác nhau" bị loại bằng dữ liệu.

---

## 4. Kiểm chéo với `AllRewards` (báo cáo 134): 9/10 rank khớp

`AllRewards` có 43 dòng `PVPReward{rank, lvl, …}`; số **level** mỗi rank chiếm được:

| rank | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| level có thưởng | 1,2 | 0,1,2 | 0–3 | 0–3 | 0–4 | 0–4 | 0–4 | 0–4 | 0–4 | 0–4 |
| số level | 2 | 3 | 4 | 4 | 5 | 5 | 5 | 5 | 5 | 5 |
| **độ dài `MaxRankStars`** | **3** | 3 | 4 | 4 | 5 | 5 | 5 | 5 | 5 | 5 |

**9/10 khớp** ⇒ "mỗi ô = một level" là suy luận có dữ liệu đỡ, **không** phải đoán. Rank 0 là ngoại lệ: 3 ô nhưng chỉ 2 level có thưởng. Hai khả năng (level 0 tồn tại mà không có dòng thưởng / ô đầu là placeholder) **không phân biệt được** bằng dữ liệu đã pin ⇒ ghi `not_decoded`, không chọn bừa.

---

## 5. Cái gì **không** decode được (và chặn ở đâu)

| mục | bước chặn chính xác |
|---|---|
| **method đọc** `MaxRankStars` | 15 method `PVP_Manager` đã pin **không** method nào `ldr` statics `+0x18` (chỉ `+0x10` ở `LoadRemoteConfigs`/`..cctor` và `+0x20`). Reader nằm ở class chưa pin (`PVP_Endgame` / `Board_*`) ⇒ "index = rank" là **suy luận thứ tự** (10 phần tử ↔ 10 rank), không phải biểu thức index đã dịch |
| rank 0 lệch 1 ô | xem §4 |
| sao cộng/trừ khi thắng/thua | `MODEL_NOT_MEASURED runtime` |
| nghĩa "trần sao" vs "sao cần để lên level" | tên field + cấu trúc hằng số ⇒ đọc là **trần**; ngữ nghĩa đầy đủ cần reader ở trên |

---

## 6. Quan hệ với báo cáo 128 — **xác nhận**, không đính chính

128 §3.4 ghi `[3,3,3]`, `[4,4,4]`, `[4,4,4,4]`, `[5,5,5,5]`, "6 bậc cuối giống nhau, cùng blob". Báo cáo này **xác nhận đúng 5/5 blob** và bổ sung thứ 128 không có:

1. **Bất biến SHA-256** giữa tên field PID và byte khởi tạo (`5/5`) — biến phép gán thành kiểm được.
2. **Độ dài khai báo** `declared_bytes == 4 × newarr` cho cả 5 blob.
3. **Quy ước token** `(token_source − 1)/2 == ordinal` cho cả 10 lời gọi.
4. **Bản đồ level ↔ độ dài** với `AllRewards` (9/10) — thứ 128 không kiểm.
5. Artifact + verifier riêng: từ nay câu "MaxRankStars bằng mấy" trả lời bằng một lệnh, không phải trích dẫn văn xuôi.

Không có mục nào phải sửa ở 128; mục `not_decoded` "`MaxRankStars` **giá trị**" của 127 thì **đóng**.

---

## 7. Tái lập

```bash
python3 tools/verify/max_rank_stars.py            # ghi artifact, in 10 thang sao
python3 -m unittest tests.test_max_rank_stars     # 19 test
python3 tools/verify-claims.py --require AB,AO,AP # needle APKD1/AI1
```

---

## 8. Tệp thay đổi

| tệp | nội dung |
|---|---|
| `tools/verify/max_rank_stars.py` | đọc `..cctor` + resolution 128 + `fieldDefaultValues`, tự assert 4 tầng |
| `datas/l2_535b0541_max_rank_stars.json.gz` | artifact 2559 B |
| `tests/test_max_rank_stars.py` | 19 test |
| `docs/apk-analysis/135-535b0541-max-rank-stars.md` | báo cáo này |
| `tools/verify-claims.py`, `docs/spec/START_HERE.md` | needle `APKD1` 79→80 `.md`, `AI1` datas 112→113 |

`provenance:` STATIC-ONLY, original APK `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`, `libil2cpp.so` `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`, `dump.cs` `8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c`; nguồn: `meta-rewards-535b0541` (10 `InitializeArray`), `l2_535b0541_meta_rewards` (token→field), `field-defaults.json` (byte), `l2_535b0541_pvp_manager_rules` (mốc kiểm chéo level). RVA trong artifact ghi dạng thập phân.
