# M5 HANDOVER CONTRACT — bàn giao gì để verify được "multi-wave loader"

**Vai:** build-spec/verifier (`ef6b75ef`) · **Trạng thái:** PROVISIONAL · **Chưa có M5 để kiểm**
(coder tip vẫn `3f69db320` = M1–M4 + fix F1/F3–F7).

Mục đích: coder **không phải đoán** tôi sẽ kiểm gì, và tôi **không phải thương lượng** sau khi code đã viết.
Máy kiểm: `reverse-engineering/raw/verify-ef6b75ef-m5/verify_m5.py` (`1236593a…`) — chạy được ngay bây giờ,
hiện trả `NOT_DELIVERED`.

## 1. Coder nộp gì (đủ 4 mục, thiếu mục nào ⇒ tôi dừng ở `NOT_READY`)

| # | Mục | Định dạng | Vì sao cần |
|---|---|---|---|
| 1 | **payload 282 wave** trong `game/` | 1 file JSON (tên tuỳ ý) có `waves[]`, mỗi phần tử `{wave, spawners[]}`; **giữ nguyên tên + thứ tự** `datas/waves.json` | để đếm từng wave, không đếm bằng mắt |
| 2 | **metadata nguồn** | `source` + `source_sha256 = dde007618b7cbc83f0702298f7744609f8b25b2d7479ab15964b1fb6fa8abc73` | pin đúng file gốc, chặn "dữ liệu tự chế" |
| 3 | **trace replay** (nếu muốn đạt M5.7) | JSONL: mỗi dòng `{"wave":"Wave_0000","enemy":"CB-30003"}` theo **đúng thứ tự spawn thật** | không có Godot trong sandbox ⇒ chỉ trace mới chứng minh được thứ tự |
| 4 | **commit + CI theo headSha** | `git rev-parse HEAD` + run id | protocol §2 |

## 2. Tôi sẽ kiểm gì (đúng 8 mục, đã mutation-test)

| Kiểm | Cách đo | Fail khi |
|---|---|---|
| **M5.1** payload tồn tại | quét `game/data/**.json` tìm mảng nhiều wave | không có ⇒ `NOT_DELIVERED` (không suy diễn) |
| **M5.2** tập wave | so tên **và thứ tự** với 282 wave gốc | thiếu/thừa/đảo thứ tự |
| **M5.3** bộ đếm từng wave | `spawner_rows`, `Σ len(enemies)`, `Σ copies`, `Σ(copies×len)` vs `anchor_waves.json:per_wave` | lệch **1 đơn vị** ở bất kỳ wave nào |
| **M5.3b** thứ tự row | digest **order-sensitive** của từng wave | row bị đảo/đổi dù tổng không đổi |
| **M5.4** wave rỗng | đếm `spawners == []` | có wave "xong ngay" |
| **M5.5** khối lượng | byte + gzip của payload | ≥ 5.000.000 B (luật commit) |
| **M5.6** pin nguồn | `source_sha256` == sha của `datas/waves.json` | thiếu/sai pin |
| **M5.7** thứ tự replay | so trace với thứ tự `copies → enemies[]` | lệch 1 phần tử; **không có trace ⇒ `UNVERIFIABLE`**, không cho điểm |

### Bằng chứng máy kiểm **có răng** (4 biến thể, chạy thật)

| Fixture | Kết quả |
|---|---|
| coder tip hiện tại (chỉ 1 wave) | `NOT_DELIVERED` |
| payload dựng đúng từ gốc | 6 PASS + `M5.7 UNVERIFIABLE` |
| xoá 1 row của 1 wave | `M5.3 FAIL` + `M5.3b FAIL` |
| đảo 2 row của 1 wave (tổng **không đổi**) | `M5.3 PASS` nhưng `M5.3b FAIL` ← chứng minh chỉ đếm tổng là không đủ |
| trace đúng thứ tự (887 event, 2 wave) | `M5.7 PASS` |
| trace đảo thứ tự | `M5.7 FAIL` |

## 3. Rủi ro phải chốt **trước** khi coder chạy M5

**Quy tắc gom `Call_Data` → `Wave_NNNN` chưa đóng.** Trong workspace có một bản `datas/waves.json`
**không nằm trong nhánh nào** (sha256 `6964336b…`, 2.798.644 B, mtime 2026-10-27T17:20Z) với **11.096** row
thay vì **11.089**. So với bản chính thức `dde00761…`: **9 wave khác** —

| Wave | row (bản lạ / chính thức) | row chỉ có ở bản lạ / chính thức |
|---|---|---|
| `Wave_0025` | 233 / 233 | 7 / 7 |
| `Wave_0026` | 42 / 42 | 1 / 1 |
| `Wave_0048` | **9 / 10** | 1 / 2 |
| `Wave_0049` | 9 / 9 | 1 / 1 |
| `Wave_0104` | 193 / 193 | 3 / 3 |
| `Wave_0137` | 48 / 48 | 7 / 7 |
| `Wave_0163` | 257 / 257 | 3 / 3 |
| `Wave_0198` | 13 / 13 | 1 / 1 |
| **`unknown`** | **25 / 17** | 20 / 12 |

Chi tiết máy đọc: `grouping_divergence.json` (`e5876d38…`). **Kết luận:** tổng số có thể khớp trong khi
thành viên từng row khác ⇒ M5 **phải** chấp-nhận theo **đúng bản `dde00761…`**, không theo tổng.
Riêng wave tên `unknown` cần director quyết: giữ 17 row như bản chính thức, hay tách riêng khỏi 282.

## 4. Khối lượng (đo được, để coder chọn định dạng)

| Dạng | Byte | Ghi chú |
|---|---:|---|
| minified `{source, source_sha256, waves[]}` | **1.759.649** (1,68 MiB) | dưới luật 5 MB, trên vẫn ổn |
| gzip cùng nội dung | **53.120** | nếu cần nhẹ |

Đề nghị: **1 file minified** + giữ đủ 4 bộ đếm; đừng tách 282 file rời (khó diff, dễ lệch).

## 5. Cái contract này **không** hứa

- Không hứa Godot chạy được: `RUNTIME_UNVERIFIED` cho tới khi có máy có engine.
- Không quyết map→wave binding: spec `COVERAGE_AUDIT.md` §7 ghi chỉ **7/250** map chắc ⇒ phần stage/map
  flow vẫn `UNKNOWN`/`INFERRED`.
- Không thay verdict: verdict M5 chỉ viết khi có commit + CI + (nếu muốn M5.7) trace.
