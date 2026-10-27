# HANDOFF — VAI commercial-researcher (`arena/46e50499`)

> **Cập nhật:** 2026-10-27 · **Đầu mối duy nhất:** file này. Mọi tài liệu khác trong `docs/research/phase-b/` là chi tiết.
> **Trạng thái lane:** **CHƯA ĐÓNG.** ① ② ③ ④ ⑤ đều đã có kết quả; lane **không được** báo `STATUS: XONG` cho tới khi user chốt các quyết định còn treo — vì chúng đổi **phạm vi** của ②③, không chỉ đổi nội dung.
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

## 3. Việc user phải chốt — theo thứ tự chặn

### 3.1 Chặn trên (quyết xong mới làm tiếp được)

| # | Câu hỏi | Phương án | Đề xuất của lane |
|---|---|---|---|
| **G13** | **Bộ store** giữ 3 hay đổi? | A giữ 3, Amazon thu về Fire TV/legacy · B thay Amazon bằng **Google Play** · C thêm Play = 4 store · D bỏ Amazon | **A ngay, B quyết ở Gate-2** khi có số liệu |
| **G14** | **D10a "Fire tablet trước"** còn hiệu lực? | giữ (nhưng = đi Google Play) · đảo sang Fire TV · **Windows trước** · hoãn | Windows trước — MS không bị ảnh hưởng bởi thay đổi này |

> **Vì sao G13 chặn:** nó đổi **tập store** ⇒ đổi bộ kit Gate-6 phải làm, đổi danh sách adapter Godot phải tự viết, đổi hệ số chia doanh thu trong bảng giá. Làm tiếp trước khi chốt = làm lại.

### 3.2 Chặn nội dung (đã có đề xuất, chờ duyệt)

| # | Câu hỏi | Đề xuất |
|---|---|---|
| **G9** | "Remove ads" còn bán được khi ads là rewarded-only? | Đổi thành **Premium: no ads + auto-grant rewarded + QoL** — **$3.99** |
| **G10** | Gói thời hạn: consumable + hạn server, hay subscription store? | **(A) consumable + hạn server** — tránh luật "MS không cho nâng giá subscription" và consent auto-renew riêng của Huawei |
| **G11** | Battle pass: giá + độ dài mùa | **$4.99 launch → $5.99**, mùa 4–6 tuần |
| **G12** | Premium Windows | **$9.99** |
| **G15** | Có đi APS trên Fire TV không? | Chỉ dùng mediation thường; **tránh APS** (review một lần, không appeal, điều khoản nhường 30% impression) |
| **G16** | Có lập mô hình doanh thu ads không? | **Không** — chỉ đo eCPM thật ở soft launch |
| **G17** | Mở lại D2a (đại lục TQ)? | **Giữ D2a** |

### 3.3 Chờ ở gate khác (không phải lane này quyết)

`G1` 16+ · `G2` privacy URL · `G3` DSA trader → phụ thuộc D5 (entity, **user-only**) · `G4` account/cloud save · `G5` danh sách SDK (chặn ở Gate-4) · `G6` ghim Godot ≥4.5 · `G7` test plan IAP Windows · `G8` một nguồn analytics.
Chi tiết: [`DECISIONS_NEEDED.md`](./DECISIONS_NEEDED.md).

---

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

## 6. Khi nào lane đóng

Điều kiện (theo prompt lane): **Gate-6 kit hoàn tất + handoff đã đăng**.
Hiện: kit **đã có bản đầy đủ cho 3 store cũ**, **nhưng phạm vi đúng/sai phụ thuộc G13** ⇒ **chưa đóng**.
Khi user chốt **G13 + G14**, lane sẽ: (a) cập nhật kit theo tập store đã chốt, (b) cập nhật bảng giá nếu hệ số đổi, (c) đăng `STATUS: XONG [arena/46e50499] — vai commercial-researcher — handoff: <file + SHA>` rồi **dừng**, không tự nhận việc mới.
