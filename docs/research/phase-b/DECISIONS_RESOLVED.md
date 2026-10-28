# DECISIONS RESOLVED — D1–D12 (Gate 2/3 cấu hình launch)

> **⚠ CHỐT USER 2026-10-28 (lần 160):** bản Windows là **F2P + IAP, KHÔNG ADS**. ⇒ **D3(b) khẳng định** · **D6 đổi (a) → (b) — không còn bản paid premium riêng** · **D4/G9 không áp dụng Windows** · **G12 đổi thành giá IAP/battle pass**. Mỗi mục dưới ghi rõ `CHỐT USER 2026-10-28` nơi bị siêu truyền.
>
> **Tình trạng thẩm quyền:** user ủy quyền ngày 2026-10-27 (lần 132): *"bạn tự quyết và phân việc, phần phân tích chỉ để học tập, cần thiết lắm thì mới đào thêm, không thì triển khai theo kế hoạch."*
> Director (SS 0) quyết D1–D12 theo ủy quyền đó; user giữ quyền bác bỏ từng mục bất cứ lúc nào (mỗi mục đánh dấu `[USER có thể bác bỏ]`).
> Căn cứ: `DECISIONS_NEEDED.md` + `PHASE_B_COMMERCIAL_RESEARCH.md` + `SOURCES.md` (S1–S73, ngày tra cứu 2026-10-27) — do Session E (`arena/46e50499`) lập. Nhãn bằng chứng giữ theo 6 loại.

| # | Quyết định | Chọn | Lý do chốt | Ghi chú triển khai |
|---|---|---|---|---|
| **D1** | Amazon Appstore | **(a) Giữ — định vị kênh Fire tablet/TV** | User đã chốt bộ 3 store gồm Amazon; kênh Android mobile chung đã đóng 20/08/2025 [S15][S16] nhưng Fire tablet/TV/Vega còn | Scope thiết bị theo **D10(a)**: tablet trước |
| **D2** | Trung Quốc đại lục | **(a) Loại đại lục lúc launch** | Cần 版号 qua NPH nội địa (6–12 tháng, bên thứ 3) [S39][S40]; phát hành 170+ nước còn lại không chặn | AppGallery đăng ký phạm vi ngoài đại lục; xem xét lại chỉ khi user yêu cầu |
| **D3** | Ads trên Windows | **(b) Windows KHÔNG ads — CHỐT USER 2026-10-28** | User chốt "không ads" + bản Windows là **F2P + IAP**. Cũng đúng về hạ tầng: MS không còn ad SDK cho game [S122], không có plugin Godot cho SDK Windows nào [S17][S19][S21] | **Không cần SDK ads Windows ⇒ nhánh rủi ro biến mất.** Doanh thu Windows = **IAP toàn bộ**; không cần eCPM, không cần single-vendor risk |
| **D4** | Hình thái gỡ quảng cáo | **(c) Một lần + subscription cả hai** | Khớp SKU sẵn có của game: `pro.forever` / `pro.week` / `pro.month` (STATIC_CONFIRMED từ APK); bài học 1945 (chỉ gói tháng → review xấu) [S31] | **Áp dụng Android/Fire/AppGallery thôi** — Windows không ads (D3b) ⇒ **không có SKU "remove ads" trên Windows**. SKU Windows = battle pass / tiện ích / non-consumable. G10 chốt consumable hay subscription store |
| **D5** | Loại tài khoản pháp lý | **Tạm (a) Individual toàn bộ — nhưng là mục USER-ONLY** | Cả 3 store đều free; nhưng Huawei không đổi quốc gia verify, MS không đổi Individual→Company [S1][S34] ⇒ **trước khi tạo tài khoản, user phải xác nhận pháp nhân/thuế** | Ghi trong USER-ONLY checklist (PHASE_C_EXECUTION_PLAN.md); director không thể quyết thay về pháp lý |
| **D6** | Paid premium edition | **(b) Chỉ F2P — BẢN CẢI 2026-10-28 (CHỐT USER)** | User chốt Windows = **F2P + IAP, không ads** ⇒ **không có bản paid premium riêng**. Bài học Sky Force vẫn giữ: mô hình kép F2P mobile + premium PC chứng minh người chơi PC chịu trả [S32] — nhưng áp dụng dưới dạng **IAP**, không phải app trả phí. MS phí game 12% | **SKU Windows = IAP**: non-consumable `pro.forever` + consumable `pro.week`/`pro.month`/`battlepass` + battle pass. **G12 đổi từ "giá app" sang "giá IAP".** Xóa khỏi lane Windows: paid app, free trial, reserve-price tier |
| **D7** | Loot box trả phí | **(a) KHÔNG** | Player-respecting; tránh rủi ro pháp lý (Bỉ/Hà Lan lịch sử, Huawei 18+ ảnh hưởng đại lục) [S54]; rating thấp hơn = easy cert | Random vật phẩm nhận bằng chơi (không trả phí) không bị ảnh hưởng |
| **D8** | Tần suất & định dạng ads | **(a) Rewarded-only, cap 4–6/lượt/ngày** (Android/Fire/AppGallery); Windows 0 ads (D3b) | Ngành khuyến nghị rewarded opt-in; HAWK mất người chơi vì interstitial cưỡng ép [S55] | Cap sẽ fine-tune bằng data soft-launch, không đoán trước |
| **D9** | Kiến trúc đa store | **(a) Interface chung + adapter từng store — TRÊN GODOT 4.x** | 3 bộ API IAP/ads khác nhau (Windows.Services.Store / Amazon IAP / HMS IAP); tránh code rẽ nhánh trực tiếp | Engine chốt bởi USER lần 134: Godot — adapter = GDScript interface + plugin từng store; ma trận plugin do E research |
| **D10** | Phạm vi thiết bị Amazon | **(a) Fire tablet trước; Fire TV/Vega hoãn** | TV cần UI/controller riêng → tăng scope; Vega dùng VPKG riêng [S15] | TV/Vega đưa backlog Gate-5 |
| **D11** | Analytics/CMP | **(a) Third-party phổ thông; verify tương thích Fire/HMS tại Gate-4** | Cần đo D1/D7/D30 + ARPDAU + consent GDPR; Huawei bắt buộc opt-out personalized ads; COPPA 2025 siết [S63][S71] | SDK cụ thể chốt ở Gate-4 sau khi có engine/plugin sẵn |
| **D12** | UA & ngân sách | **(a) Organic-first; UA chỉ khi LTV > 3× CPI** | 3 store này chủ yếu organic (Huawei có Paid Promotion); CPI trung bình $0,36–0,95 [S61] | Không đốt tiền khi retention chưa đo được |

## Cấu hình launch kết quả (một dòng)

**F2P rewarded-first · không P2W · không loot box trả phí (D7a/D8a) · Windows = F2P + IAP, không ads (D3b/D6b — CHỐT USER 2026-10-28) · Android = Fire tablet trước (D1a/D10a) · AppGallery ngoài đại lục (D2a) · SKU gỡ-ads kép khớp game sẵn có (D4c, chỉ Android) · organic-first (D12a).**

## Điều kiện Gate-1 kèm theo — disposition theo cùng ủy quyền

| Điều kiện (AI-3 own125) | Disposition |
|---|---|
| **C1** reward-blob 149-vs-169/177 | **Xuống mức CONFLICTING learning-note — KHÔNG chặn triển khai.** APK gốc là authority của sản phẩm gửi store; số decode phục vụ học tập. 535 resolve opportunistic trong registry-v4 nếu rẻ; cấm đào lane riêng. |
| **C2** registry-v4 final ledger | **535 xuất best-effort** (shipped-default/served/policy/missing-input; số mở không cần = 0; không đào lane mới). Mechanical — mảnh cuối của Gate-1. |
| **C3** fidelity/acceptance profile | **Director quyết (ủy quyền): Profile hiện hành = "L1 static-complete + runtime-gated residuals có chủ".** Mọi claim gắn 1/6 nhãn bằng chứng; bar của Gate-1 = static-complete + residuals khai rõ owner; đo runtime L2/L3 = contract riêng, không chặn triển khai. |
| **C4** 139-file absence | Đã đúng từ trước (`MISSING_FOR_NEW_GAME.md:267` ghi "chưa thấy ≠ không tồn tại") — xong. |
| **C5** bound ceiling | **Director chấp nhận (ủy quyền) defer-list làm điều kiện Gate-1:** boss-phase×2 → ef (đào CHỈ khi triển khai cần) · registry residuals → 535-v4 · runtime-gated 20+5 → MODEL_NOT_MEASURED, chờ user mở runtime lane. |

⇒ **Gate-1: READY-FOR-CLOSE** — chỉ còn C2 (registry-v4) là deliverable cơ học. Verdict `NOT_READY` của AI-3 chỉ reviewer đó nâng khi registry-v4 publish; director không tự nâng verdict review người khác (nguyên tắc lần 124).

---

## Bổ sung lần 144 — G9–G12 (Gate-3 giá/SKU) — director quyết theo cùng ủy quyền, user có thể bác bỏ

| # | Quyết | Chọn | Lý do |
|---|---|---|---|
| **G9** | Bản chất SKU "remove ads" | **Đổi thành Premium bundle $3,99**: không-ads **+** nhận thưởng rewarded không cần xem **+** QoL | D8a rewarded-only ⇒ "chỉ gỡ ads" bán cho nhu cầu không tồn tại; bán quyền-lợi, không bán sự-vắng-mặt (đề xuất E, `GATE3_PRICING_SHEET.md`) |
| **G10** | Cơ chế thời hạn | **Non-renewing pass consumable** (mua lại thủ công) — KHÔNG dùng subscription API store | Data gốc: `pro.week/month` nằm trong ConsumableProducts (71) — mua-lại-thủ-công; tránh MS khóa-giá-sub sau publish + Huawei consent auto-renew + bớt 1 adapter API |
| **G11** | Battle pass | **$4,99 launch** · chu kỳ 30 ngày · nâng $5,99 chỉ sau khi có buy-rate thật (median casual ~10%) | Comp `GATE3_PRICING_SHEET.md` P5; không đặt giá theo dự đoán |
| **G12** | Premium Windows | **$9,99** (SKU mới, D6a) · bundle PC $14,99 tuỳ chọn sau launch | Sky Force PC/Xbox $9,99 chính chủ; MS game fee 12% |

Bảng giá P1–P7 đầy đủ: `GATE3_PRICING_SHEET.md`. Gems/coins KHÔNG chốt trong lần này (cần cân bằng kinh tế — lane riêng).

---

## Bổ sung lần 145 — G13–G15 (phản ứng ALERT Amazon: Alexa Tablet 08/10/2026 chạy Android 16 + Google Play) — director quyết theo ủy quyền, [USER có thể bác bỏ]

| # | Quyết | Chọn | Lý do |
|---|---|---|---|
| **G13** | Bộ store | **(A) Launch giữ 3 store đã chốt** (MS · Amazon · Huawei) — Amazon thu về **Fire TV / Vega / Fire-OS legacy / Kids+**; **Google Play = follow-up ngay sau launch** (store thứ 4: plugin Play Billing chính thức Godot có sẵn, chạm đúng Alexa Tablet mới; hồ sơ asset/kits tái dùng được) | Không phá cấu hình đã chốt của user; Play quyết ở Gate-2-kế khi có số; cảnh báo E `ALERT_AMAZON_CHANNEL_CHANGE_2026-10-27.md` [S116–S121] |
| **G14** | D10a điều chỉnh | **"Fire TV + Fire-OS legacy trước"; tablet-Amazon-mới = Google Play (theo G13-followup)**; Windows không đổi | Alexa Tablet không qua Appstore; Fire tablet ngừng ship |
| **G15** | APS trên Fire TV | **KHÔNG tích hợp APS lúc launch** | Điều khoản nhường 30% impression + Amazon giữ 100% doanh thu phần đó chỉ kích hoạt ≥50k giờ/tháng — xa; ads Fire TV quyết khi tới Gate tương ứng |

Hệ quả: Gate-6 kits chốt phạm vi theo 3-store-A (đã có banner Amazon-scope trong 4 tài liệu E); Google Play mục "BACKLOG-Post-launch" trong PHASE_C plan.


---

## Bổ sung lần 148 — G16/G17 (theo research cuối của `46e50499` @`387f7628`) — director quyết theo ủy quyền

| # | Quyết | Chọn | Lý do |
|---|---|---|---|
| **G16** | Mô hình doanh thu ads | **(a) KHÔNG lập mô hình ads** — chỉ đo eCPM thật ở soft-launch rồi mới quyết thiết kế | Windows không còn ad-network chính chủ (MS Learn 01/2026: chỉ hướng dẫn SDK bên thứ 3); benchmark US rewarded lệch >2× (CONFLICTING); D3b giữ — nay có lý do hạ-tầng |
| **G17** | D2a (đại lục TQ) | **GIỮ D2a** — không vào đại lục; 4 điều kiện mở lại ghi trong research (doanh thu ổn ≥2/3 store · đối tác nội địa chủ động · chấp nhận thực nhận 30–50% · backend+PIPL+chống-nghiện); HK/MO/TW = đường hợp lý nếu muốn người chơi Trung văn | 3 tầng khoá: cấm WFOE tự xuất bản · 版号 import ~3%/đợt 6–8 tháng · kinh tế thực nhận ~30–50% |
