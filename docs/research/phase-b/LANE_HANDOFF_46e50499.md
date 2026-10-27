# HANDOFF — VAI commercial-researcher (`arena/46e50499`)

> **Cập nhật:** 2026-10-27 · **Đầu mối duy nhất:** file này. Mọi tài liệu khác trong `docs/research/phase-b/` là chi tiết.
> **Trạng thái lane:** **ĐÓNG ĐƯỢC — đủ điều kiện báo `STATUS: XONG`.** ① ② ③ ④ ⑤ đã xong; **G9–G17 đã được director chốt** (board PR12 lần 150 = comment mới nhất; file `DECISIONS_RESOLVED.md` lần 144/145/148 trên nhánh spec); kit/queue/bảng giá **đã đồng bộ theo G13=A (3 store) + G14 (Fire-TV-first) + G15 (không APS)**. Chỉ còn **G1–G8** treo ở các gate khác, không chặn lane này.
> **Ràng buộc đang giữ:** research-only. Không đăng ký tài khoản, không cài SDK, không build/nộp/publish, không merge/close PR, không force-push, không ghi vào `docs/spec/` · `datas/` · `tools/` · `tests/`.

---

## 1. Năm việc của prompt lane — đã làm gì

| # | Việc | Kết quả | File | Commit |
|---|---|---|---|---|
| ① | **Gate-6 requirement sheets** (rating questionnaire + privacy/data form × 3 store) | `XONG` | `GATE6_SUBMISSION_KITS.md` | `e37b7bc` |
| ② | **Ma trận plugin Godot** (IAP/Ads/Analytics × 3 store) | `XONG` | `GATE4_GODOT_COMMERCE_QUEUE.md` | `04efc4e` |
| ③ | **Benchmark giá** remove-ads / premium → đề xuất bảng giá Gate-3 | `XONG` | `GATE3_PRICING_SHEET.md` | `1c3aa35` |
| ④ | **eCPM rewarded Windows + trạng thái ads Fire 2026** | `XONG` — **Windows: không tồn tại nguồn** (Microsoft không có ad SDK cho game); Fire: đã chốt | `ADS_WINDOWS_AND_FIRE_STATUS_2026-10-27.md` | `387f762` |
| ⑤ | **NPH Trung Quốc** | `XONG` — củng cố **D2a** (không vào đại lục), có điều kiện mở lại | `CHINA_PUBLISHER_TRACK_NPH-TQ.md` | `387f762` |

**Phát sinh ngoài 5 việc (leo thang Gate-1):** Amazon đã đổi kênh phân phối ngày **08/10/2026** — tablet Amazon chạy **Android 16 + Google Play**, không còn đi qua Amazon Appstore. Ghi tại `ALERT_AMAZON_CHANNEL_CHANGE_2026-10-27.md` (`3d89763`). **Đây là lý do chính lane chưa thể đóng.**

---

## 2. Tài liệu trong lane (đọc theo thứ tự này)

| File | Nội dung | Trạng thái |
|---|---|---|
| **`LANE_HANDOFF_46e50499.md`** | File này — đầu mối | — |
| `ALERT_AMAZON_CHANNEL_CHANGE_2026-10-27.md` | ⚠ Thay đổi kênh Amazon + 4 phương án + G13/G14/G15 | **Đọc trước** |
| `GATE3_PRICING_SHEET.md` | Bảng giá P1–P7, cơ chế giá 3 store, công thức net, G9–G12 | Chờ chốt G9/G10 |
| `GATE4_GODOT_COMMERCE_QUEUE.md` | Plugin IAP/Ads/Analytics theo store, việc phải tự viết | Chờ chốt G13 (tập store) |
| `GATE6_SUBMISSION_KITS.md` | Kit rating + privacy × 3 store + §8b khoảng trống nếu thêm Google Play | Chờ chốt G13 |
| `ADS_WINDOWS_AND_FIRE_STATUS_2026-10-27.md` | Windows không có ad SDK chính chủ; Fire/APS 2026 | Xong |
| `CHINA_PUBLISHER_TRACK_NPH-TQ.md` | Rào pháp lý TQ, kinh tế, điều kiện mở lại D2a | Xong |
| `PHASE_B_COMMERCIAL_RESEARCH.md` | Báo cáo nền: comps, điều kiện store, kịch bản doanh thu | Nền |
| `STORE_COMPARISON_3COL.md` | Bảng so sánh 3 store + **§A nhánh Alexa Tablet** | Nền |
| `DECISIONS_NEEDED.md` | D1–D12 (đã chốt) · **G1–G17 (chờ user)** | **Chờ user** |
| `SOURCES.md` | **S1–S132**, ngày tra cứu 27/10/2026 | Nền |

---

## 3. Quyết định — TRẠNG THÁI CUỐI

### 3.1 Đã chốt (director quyết theo ủy quyền; user có quyền bác bỏ)

| # | Chốt | Ghi chú |
|---|---|---|
| **G9** | **Premium bundle $3,99** (không-ads + auto-grant rewarded + QoL), bỏ "remove ads" thuần | đổi bản chất SKU chính |
| **G10** | **Pass consumable, hết hạn server** — không dùng subscription API store | bớt 1 API; tránh khoá giá MS + consent Huawei |
| **G11** | Battle pass **$4,99** launch · chu kỳ **30 ngày** · lên $5,99 chỉ khi có buy-rate thật | |
| **G12** | Premium Windows **$9,99** · bundle PC $14,99 tuỳ chọn sau launch | |
| **G13** | **Giữ 3 store lúc launch**; Amazon = Fire TV/Vega/Fire-OS legacy/Kids+; **Google Play = follow-up ngay sau launch** | Play là store thứ 4, **BACKLOG** |
| **G14** | **Fire-TV-first** (thay D10a) | kéo theo: UI D-pad, không banner TV, test trên thiết bị TV thật |
| **G15** | **Không APS** lúc launch | tránh điều khoản nhường 30% impression |
| **G16** | **Không lập mô hình doanh thu ads** — chỉ đo eCPM thật | |
| **G17** | **Giữ D2a** — không vào đại lục TQ | HK/MO/TW vẫn là đường hợp lý nếu muốn tiếng Trung |

Chi tiết đầy đủ: `docs/research/phase-b/DECISIONS_RESOLVED.md` trên nhánh spec `20330d0e` (lần 144/145/148).

### 3.2 Còn treo (thuộc gate khác, không chặn lane này)

`G1` 16+ · `G2` privacy URL · `G3` DSA trader → phụ thuộc D5 entity (**user-only**) · `G4` account/cloud save · `G5` danh sách SDK (chặn ở Gate-4) · `G6` ghim Godot ≥4.5 · `G7` test plan IAP Windows · `G8` một nguồn analytics.

## 4. Điều lane này KHÔNG làm (và sẽ không làm)

- **Không** đăng ký tài khoản store, không mở console, không nộp gì.
- **Không** viết code, không cài SDK, không build.
- **Không** tự chuyển gate, không tự ACK, không tự nhận XONG.
- **Không** đưa số liệu không có nguồn chính chủ + ngày tra cứu. Chỗ nào không có ⇒ ghi `UNVERIFIED`/`UNKNOWN`, **không bịa**.
- **Không** lập dự báo doanh thu. Bảng giá chỉ có **giá đề xuất** + **công thức net**.

---

## 5. Ba con số hay bị hiểu sai (nhắc lại để khỏi tranh luận lại)

1. **Amazon displayed price đã gồm VAT**, Huawei cũng vậy ⇒ **không** lấy giá × (1 − share) ra net. Phải trừ thuế trước.
2. **VN–US không có hiệp định thuế** ⇒ **30% withholding** trên doanh thu phát sinh ở Mỹ. Đây là khoản mất thật, không phải "thuế công ty tự lo".
3. **Không có eCPM Windows.** Không phải thiếu số — Microsoft **không còn ad network cho game**. Con số $6,20 đang lưu hành là **seller claim một case**, không dùng được.

---

## 6. Điều kiện đóng lane — ĐÃ THỎA

Theo prompt lane: **Gate-6 kit hoàn tất + handoff đã đăng**.

- Kit Gate-6: có, và **đã đồng bộ phạm vi 3-store-A + Fire-TV-first** (§0 mới trong 3 tài liệu gate).
- Gate-4 queue: xong, đã thêm **§0.1 hệ quả Fire-TV-first** (D-pad, không banner TV, không APS).
- Gate-3 bảng giá: xong, giá **không đổi** vì G14 chỉ đổi cách hiển thị.
- Handoff: **file này**.
- CI: nhánh không có `.github/workflows/` ⇒ `check-runs = 0` cho mọi headSha; thay bằng kiểm cục bộ (diff clean · table column count · relative links · `[Sxx]` tồn tại).

⇒ **Lane đủ điều kiện đăng `STATUS: XONG`.** Không tự nhận việc mới sau khi đăng.
