# DANH SÁCH QUYẾT ĐỊNH CẦN USER CHỐT (Phase B → Gate 2/3)

- Ngày lập: **2026-10-27**. Mỗi quyết định gắn: bối cảnh, phương án, rủi ro, gate liên quan, thông tin còn thiếu.
- Kỷ luật gate: research này **không tự xác nhận "Phase B xong"**; mọi quyết định dưới đây chờ user phê duyệt. Bằng chứng gốc ở [PHASE_B_COMMERCIAL_RESEARCH.md](./PHASE_B_COMMERCIAL_RESEARCH.md) và [SOURCES.md](./SOURCES.md).
- **Cập nhật 2026-10-27 (vòng commercial-researcher):** D1–D12 dưới đây **đã được director chốt theo uỷ quyền của user** — bản ghi đầy đủ ở `docs/research/phase-b/DECISIONS_RESOLVED.md` (nhánh spec `20330d0e`). User vẫn giữ quyền bác bỏ từng mục. Phần **G1–G5 ở cuối file** là quyết định **mới phát sinh ở Gate-6**, chưa được chốt.

| # | Quyết định | Bối cảnh / bằng chứng | Phương án | Rủi ro nếu chọn | Gate | Thông tin còn thiếu |
|---|---|---|---|---|---|---|
| D1 | **Giữ hay thay Amazon Appstore khi kênh Android mobile đã đóng 20/08/2025** | Chỉ còn Fire tablet/Fire TV/Vega [S15][S16] | (a) Giữ, định vị lại là kênh Fire/TV; (b) Bỏ Amazon, thêm store khác; (c) Hoãn quyết định tới sau MVP | (a) Thị phần nhỏ, phải test controller/TV; (b) mất mức 80/20 SBAP và thiết bị Fire | 2 | Quy mô thiết bị Fire của phân khúc khách hàng mình (không có số công khai cho riêng genre) |
| D2 | **Có theo đuổi Trung Quốc đại lục trên AppGallery không?** | Game cần 版号 NPPA qua NPH nội địa, không tự đứng tên [S39][S40] | (a) Loại đại lục lúc launch, phát hành 170+ nước còn lại; (b) Tìm NPH TQ song song (6–12 tháng, số thời gian là bên thứ 3) | (a) Mất thị trường TQ; (b) chi phí pháp lý/thời gian, kiểm duyệt nội dung, kiểm soát dữ liệu | 2 | Danh sách NPH phù hợp, báo giá dịch vụ |
| D3 | **Chiến lược ads trên Windows** | Không có SDK第一方; MAX/LevelPlay không hỗ trợ Windows; Vungle chỉ interstitial+rewarded v7.x; Pubfinity còn hoạt động nhưng nhỏ (UWP casual); RISE đã pivot, RISE Engage 404 [S17][S19][S21][S77][S78] | (a) Vungle rewarded-only trên Windows; (b) Windows không ads, thuần IAP + paid premium; (c) Thêm Pubfinity nếu đóng gói UWP và cần banner/native | (a) phụ thuộc một nhà cung cấp lớn; (b) giảm ARPDAU người không mua; (c) Pubfinity quy mô nhỏ, danh mục curated | 3 | Hợp đồng Vungle: eCPM Windows, ngưỡng thanh toán, fill rate thực tế; điều kiện onboarding Pubfinity |
| D4 | **Hình thái gỡ quảng cáo: một lần, subscription, hay cả hai?** | Bản gốc có cả `pro.forever`, `pro.week`, `pro.month` (STATIC_CONFIRMED); Sky Force bán Ads Removal $3,99 một lần [S31]; 1945 bị chê vì chỉ có gói tháng | (a) Một lần (durable/entitlement); (b) Subscription; (c) Cả hai, subscription cao cấp hơn | (b) review tiêu cực như 1945; (a) bỏ qua dòng tiền định kỳ; (c) phức tạp SKU | 3 | Giá sẵn lòng trả — cần soft launch A/B |
| D5 | **Loại tài khoản pháp lý trên từng store** | Cả 3 cho individual/company, miễn phí; Huawei không đổi quốc gia verify; Microsoft không cho đổi Individual→Company [S1][S34] | (a) Cá nhân toàn bộ; (b) Doanh nghiệp toàn bộ; (c) Pha trộn | (a) hạn chế dịch vụ (vd Petal Ads một số luồng chỉ enterprise), thuế cá nhân; (b) cần pháp nhân | 2/3 | Tình trạng pháp nhân/tax của user |
| D6 | **Có bán paid premium edition không?** | Sky Force Reloaded chứng minh mô hình kép: mobile F2P + PC/console $9,99 không microtransaction [S32]; MS Store cho paid app, phí 12% | (a) Có, riêng bản Windows premium; (b) Chỉ F2P; (c) Làm sau khi F2P ổn định | Tự cạnh tranh phiên bản F2P; cần cân bằng progression như Sky Force | 3 | Định giá theo sức chịu chi của audience |
| D7 | **Có dùng loot box/random item trả phí không?** | Huawei xếp gambling/loot box vào 18+, app 18+ có thể không được phát hành đại lục [S54]; Play/App Store gắn nhãn random items/simulated gambling; 1945 và HAWK đều bị review phàn nàn | (a) Không (đề xuất theo định hướng player-respecting); (b) Có nhưng trang bị rõ xác suất, không ảnh hưởng sức mạnh | (b) rating cao hơn, rủi ro pháp lý một số vùng (Bỉ/Hà Lan lịch sử) | 3 | Luật từng nước về gacha (cập nhật tại Gate-7) |
| D8 | **Tần suất & định dạng ads** | ECONOMY.md đề xuất 5 vị trí (đề xuất, không phải gốc); ngành khuyến nghị rewarded opt-in; HAWK mất người chơi vì interstitial cưỡng ép | (a) Chỉ rewarded + cap 4–6/ngày; (b) Thêm interstitial có cap; (c) Banner trên Android/Fire | Quá nhiều → D7/D30 tụt (median D7 ngành đã chỉ ~4% [S55]); quá ít → IAA thấp | 3 | Số impressions/DAU thực đo sau soft launch |
| D9 | **Kiến trúc đa store: lớp abstraction IAP/ads** | Ba bộ API khác nhau (Windows.Services.Store / Amazon IAP / HMS IAP), ba bộ ads | (a) Interface chung + adapter từng store; (b) Code rẽ nhánh trực tiếp | (a) chi phí kỹ thuật ban đầu; (b) nợ kỹ thuật, khó test | 4 | Chọn engine (Unity?) ảnh hưởng plugin sẵn có |
| D10 | **Phạm vi thiết bị Amazon: Fire tablet only hay cả Fire TV/Vega** | Vega dùng VPKG, không thay bằng APK/AAB [S15]; Fire TV cần controller | (a) Tablet trước; (b) Tablet + TV; (c) Bỏ Vega ở giai đoạn đầu | TV cần UI/controller riêng, tăng scope | 4/5 | Nguồn lực QA thiết bị |
| D11 | **Chọn analytics/CMP trung lập và vị trí dữ liệu** | Cần đo D1/D7/D30, ARPDAU, consent GDPR; Huawei yêu cầu opt-out personalized ads; COPPA 2025 siết targeted ads cho trẻ [S63][S71] | (a) Giải pháp third-party phổ thông; (b) Tự dựng + SDK console | (a) phải kiểm tra tương thích Fire/HMS; (b) tốn công | 4 | Khả năng tương thích từng SDK trên 3 nền |
| D12 | **Mục tiêu payback & ngân sách UA** | CPI game 2024 trung bình $0,36; hybrid-casual $0,95 (Adjust) [S61]; ba store này chủ yếu organic, Huawei có Paid Promotion | (a) Organic-first, UA chỉ sau khi LTV>3× CPI; (b) Mở UA sớm trên Petal Ads | Đốt tiền nếu retention dưới median; Amazon/MS gần như không có công cụ UA quy mô | 7 | LTV thực sau soft launch |

## Quyết định mặc định đề xuất (chờ user bác bỏ hoặc phê duyệt)

Nếu user muốn một cấu hình khởi điểm để bàn tiếp, nhóm nghiên cứu đề xuất (đây là **đề xuất**, không phải quyết định):
**D1(a) · D2(a) · D3(b) · D4(c) · D6(b) · D7(a) · D8(a) · D9(a) · D10(a) · D11(a) · D12(a)** — tương ứng định vị: F2P rewarded-first, không P2W, **Windows = F2P + IAP, không ads**, Fire tablet trước, AppGallery ngoài đại lục, UA organic-first.

---

## BỔ SUNG — Quyết định Gate-6 (G1–G5), phát sinh khi lập requirement sheets

Chi tiết bằng chứng + câu trả lời chuẩn bị sẵn: [GATE6_SUBMISSION_KITS.md](./GATE6_SUBMISSION_KITS.md).

| # | Quyết định | Bối cảnh / bằng chứng | Phương án | Rủi ro nếu chọn | Gate | Thông tin còn thiếu |
|---|---|---|---|---|---|---|
| **G1** | **Định vị tuổi (target audience)** | Amazon: chọn audience có trẻ em ⇒ **bắt buộc** Child-Directed App (COPPA) Policy [S69][S83]; Huawei: audience có trẻ ⇒ chính sách trẻ em riêng + **consent cha mẹ** + hạn chế ads/IAP [S73]; COPPA sửa đổi 2025 cần opt-in riêng cho targeted ads [S63] | (a) 16+/không dành cho trẻ · (b) mixed có trẻ · (c) dành cho trẻ | (b)(c) tăng đáng kể nghĩa vụ pháp lý + giới hạn quảng cáo/IAP; (a) mất reach nhóm phụ huynh/trẻ | 6 | Art/âm thanh cuối cùng để xác nhận mức bạo lực hoạt hình |
| **G2** | **Privacy policy: nơi host + ai là data controller** | MS bắt buộc **privacy policy URL** trong Partner Center, policy phải nêu loại bên nhận dữ liệu [S81]; Amazon bắt buộc policy khi thu thập dữ liệu gắn cá nhân [S84]; Huawei bắt buộc **URL trong AGC + link in-app** [S71] | (a) trang riêng trên domain dự án · (b) GitHub Pages · (c) dịch vụ tạo policy | (b)(c) rẻ nhưng dễ thiếu chi tiết; policy sai nội dung = fail cert/gỡ app | 6 | User chọn nơi host; tên pháp nhân/địa chỉ liên hệ (liên quan D5) |
| **G3** | **EU DSA trader status** | MS: dev là "Trader" phải nộp DUNS/giấy tờ doanh nghiệp, trạng thái ở Legal info → Developer [S82]; Apple/Google đã gỡ app không khai từ 2025 (tham chiếu chung, BT3) | (a) khai trader + địa chỉ/điện thoại công khai · (b) khai non-trader | (a) địa chỉ công khai trên PDP EU; (b) rủi ro gỡ khỏi EU nếu thực tế có doanh thu | 6 | User quyết (dữ liệu cá nhân) — gộp với D5; trạng thái DSA của Amazon/Huawei còn `UNKNOWN` |
| **G4** | **Account/cloud save có trong MVP?** | Spec: MVP **không** có Arena/PvP/event/VIP [spec GAMEPLAY §7.2]; game gốc có account + cloud save (`Board_AccountSettings`, `Board_LinkAccount`) | (a) không — save local · (b) có account/cloud | (b) thêm User IDs/nickname vào **cả 3 form**, và phải khai lại khi mở PvP | 6 | User chọn; ảnh hưởng trực tiếp khối lượng khai báo |
| **G5** | **Chốt danh sách SDK để khai** | Amazon + Huawei **bắt buộc** khai dữ liệu do third-party SDK thu thập [S66][S87]; D11 để SDK cụ thể ở Gate-4 | chờ Gate-4 | Khai thiếu SDK = form chưa hoàn chỉnh ⇒ Amazon **không cho publish/update** (từ Q2/2025) [S66] | 4 → 6 | Chốt SDK analytics/ads/CMP ở Gate-4 |

## BỔ SUNG — Quyết định Gate-4/5 phát sinh từ queue Godot

Chi tiết + bằng chứng: [GATE4_GODOT_COMMERCE_QUEUE.md](./GATE4_GODOT_COMMERCE_QUEUE.md).

| # | Quyết định | Bối cảnh / bằng chứng | Phương án | Rủi ro nếu chọn | Gate | Thông tin còn thiếu |
|---|---|---|---|---|---|---|
| **G6** | **Ghim phiên bản Godot (≥4.5)** | GameAnalytics Godot SDK yêu cầu **4.5+** [S99][S100]; AdMob plugin Poing yêu cầu **4.5+** [S96] ⇒ dùng 4.2/4.3 sẽ mất analytics chính thức | (a) Godot 4.5+ · (b) Godot cũ + analytics tự viết | (a) ghim theo plugin, phải nâng khi plugin nâng; (b) tự viết analytics = thêm việc + sai số | 4/5 | User/Godot-coder chốt; cần biết bản Godot ổn định muốn dùng |
| **G7** | **Kế hoạch test IAP Windows** | `Windows.Services.Store` cần **MSIX có identity Partner Center** + **không elevated**; **dev license không phải retail license** ⇒ không test được ở máy dev thuần [S101] | (a) tạo submission **private audience/flight** sớm để test · (b) hoãn Windows IAP sang sau khi 2 store kia xong | (a) tốn một vòng submission, cần tài khoản MS sẵn sàng (user đã có); (b) rủi ro phát hiện muộn, đúng lúc gần release | 4/5 | Lịch submission; xác nhận quyền tạo flight trong Partner Center |
| **G8** | **Một hay nhiều nguồn analytics** | GameAnalytics có SDK Godot chính thức + là đối tác Huawei (OAID); Huawei Analytics Kit chỉ đọc được trong AGC [S99][S106] | (a) GameAnalytics làm nguồn sự thật duy nhất · (b) thêm Analytics Kit per-store | (a) Fire OS chưa được xác nhận hỗ trợ → phải test; (b) số liệu không so sánh được giữa 3 store | 4 | Kết quả test GameAnalytics trên Fire thật |

## BỔ SUNG — Quyết định Gate-3 phát sinh từ bảng giá

Chi tiết + bằng chứng: [GATE3_PRICING_SHEET.md](./GATE3_PRICING_SHEET.md).

| # | Quyết định | Bối cảnh / bằng chứng | Phương án | Rủi ro nếu chọn | Gate | Thông tin còn thiếu |
|---|---|---|---|---|---|---|
| **G9** | **"Remove ads" còn bán được khi ads là rewarded-only?** | D8a chốt rewarded-only (không ép xem) ⇒ người chơi đã có quyền không xem ads; benchmark cho thấy $0.99–4.99 là giá để *thoát ads bị ép* [S115] | (a) giữ "remove ads" thuần · (b) đổi thành **Premium: gỡ ads + nhận thưởng rewarded không cần xem + QoL** · (c) bỏ SKU, chỉ bán battle pass + premium PC | (a) SKU chính gần như không bán được; (c) mất dải giá thấp | 3 | Kết quả A/B sau soft launch |
| **G10** | **Gói thời hạn: consumable hay subscription store?** | APK gốc: `pro.week`/`pro.month`/`battlepass` đều là **Consumable**, chỉ `pro.forever` là NonConsumable [datas/iap_products.json]; MS **không cho nâng giá subscription** sau publish [S107]; Huawei đòi consent auto-renew riêng [S111] | (A) consumable + hết hạn **server** · (B) subscription store · (C) bỏ gói thời hạn | (A) cần logic hạn dùng ở server (không dựa giờ máy); (B) phức tạp 3 adapter + không nâng giá được trên MS | 3 | Chọn A/B/C |
| **G11** | **Giá battle pass + độ dài mùa** | Casual mặc định $5.99, buy rate ~10%; dải $5–15/mùa [S115] | (a) $4.99 launch → $5.99 · (b) $9.99 ngay | (b) khó bán ở tập casual | 3 | Số mùa/năm; nội dung mỗi mùa |
| **G12** | **Giá premium Windows** | Sky Force PC/Xbox **$9.99** (chính chủ) [S114]; MS phí game 12% | (a) $9.99 · (b) $12.99 · (c) $7.99 | (b) vượt tiền lệ cùng thể loại; (c) bỏ tiền trên bàn | 3 | Wishlist/refund sau launch |

## BỔ SUNG — LEO THANG GATE-1: kênh Amazon đổi bản chất (2026-10-27)

Chi tiết + nguyên văn chính chủ: [ALERT_AMAZON_CHANNEL_CHANGE_2026-10-27.md](./ALERT_AMAZON_CHANNEL_CHANGE_2026-10-27.md) [S116–S121].

> Bối cảnh một câu: **08/10/2026** Amazon thay Fire tablet bằng **Alexa Tablet chạy Android 16 + Google Play**; FAQ chính chủ nói app cho tablet này **phải nộp qua Google Play** (trừ Kids+), **APS không có**, doanh thu/thuế ở **Play Console**. ⇒ giả định "Amazon = kênh tablet" của **D1a/D10a** hết hiệu lực; kênh Amazon còn lại = **Fire TV/Vega + Fire OS installed base + Kids+**.

| # | Quyết định | Bối cảnh / bằng chứng | Phương án | Rủi ro nếu chọn | Gate | Thông tin còn thiếu |
|---|---|---|---|---|---|---|
| **G13** | **Bộ store chốt lại: giữ đúng 3 hay đổi thành phần?** | Amazon đã chuyển tablet sang Google Play [S116][S119]; Fire tablet ngừng ship, hỗ trợ 4 năm [S120]; "3 store đã lock" = MS · Amazon · Huawei | (A) giữ 3 store, Amazon thu về **Fire TV/Vega + legacy Fire OS** · (B) **thay Amazon bằng Google Play** (MS · Google Play · Huawei) · (C) thêm Google Play thành **4 store** · (D) bỏ Amazon, còn 2 store | (A) phải làm UI/UX TV hoặc sống bằng installed base đang chết; (B)(C) phá quyết định "đúng 3 store" + thêm tài khoản Play $25; (C) 4 adapter = scope lớn nhất | **1** (sửa D1/D10) | Chốt A/B/C/D; nếu B/C: có chấp nhận Google Play Billing thay Amazon IAP cho nhánh Android không |
| **G14** | **D10a "Fire tablet trước" còn hiệu lực?** | Fire tablet ngừng ship trong 1–2 tháng [S120]; tablet Amazon mới không dùng Amazon Appstore [S116] | (a) giữ "tablet trước" nhưng hiểu là **đi Google Play** · (b) đảo sang **Fire TV trước** · (c) **Windows trước** (MS đã chốt, không bị ảnh hưởng) · (d) hoãn, chờ G13 | Đảo thứ tự ảnh hưởng trực tiếp lịch Gate-2→Gate-6 và kit nào làm trước | 2 | Chốt thứ tự store ưu tiên sau G13 |
| **G15** | **Ads trên Amazon: có đi APS không?** | APS chỉ còn cho **Fire TV + Fire tablets** [S121]; **Fire TV có ads ≥30–50k giờ/tháng buộc nhường 30% impression nội địa, Amazon giữ 100% doanh thu phần đó** [S121]; Alexa Tablet: **APS không có, dùng AdMob** [S116] | (a) APS cho Fire TV/legacy, AdMob cho Alexa Tablet · (b) chỉ dùng mediation/Vungle-Mintegral, **không** đụng APS · (c) bỏ ads trên nhánh Amazon | (a) phải review APS một lần, không appeal, không công bố tiêu chí; (c) mất doanh thu ads ở kênh Amazon | 4 | Ngưỡng "có ads" áp thế nào với game (không phải video); quy mô kỳ vọng |

## BỔ SUNG — vòng ④ (ads) và ⑤ (NPH Trung Quốc)

Chi tiết: [ADS_WINDOWS_AND_FIRE_STATUS_2026-10-27.md](./ADS_WINDOWS_AND_FIRE_STATUS_2026-10-27.md) [S122–S125][S132] · [CHINA_PUBLISHER_TRACK_NPH-TQ.md](./CHINA_PUBLISHER_TRACK_NPH-TQ.md) [S126–S131].

| # | Quyết định | Bối cảnh / bằng chứng | Phương án | Rủi ro nếu chọn | Gate | Thông tin còn thiếu |
|---|---|---|---|---|---|---|
| **G16** | **Có lập mô hình doanh thu ads không, hay chỉ đo?** | **Không tồn tại** eCPM chính chủ cho Windows — Microsoft không có ad SDK cho game [S122]; số duy nhất là seller claim **$6,20** một case [S124]; benchmark mobile lệch **$13–$30** cùng một chỉ số US, VN = Tier 3 **0,05–0,18× US** [S125] | (a) **Không mô hình hoá** — chỉ đo eCPM thật ở soft launch rồi mới quyết thiết kế ads · (b) dùng benchmark BT3 để lập kế hoạch | (b) **bịa số có vỏ nguồn**: spread >2×, và không có nguồn Windows nào ⇒ mọi con số là suy diễn | 4 | Số impression/DAU thật; SDK ads chọn được (G15) |
| **G17** | **Có mở lại D2a (đại lục Trung Quốc) không?** | Dev nước ngoài **không được** tự phát hành (Đ.10 cấm WFOE/liên doanh) [S127]; **~3% 版号** là bản import [S128]; thực nhận **~30–50%**, có case **~20%** [S129]; **không** mượn được HK/Macau [S131] | (a) **giữ D2a** — không vào đại lục · (b) mở lại khi đủ 4 điều kiện ở §5 tài liệu NPH-TQ | (b) 6–8 tháng+ hồ sơ, server trong đại lục, PIPL, real-name, không kiểm soát ngày ra mắt | 1 | Chỉ mở khi có đối tác nội địa chủ động đề nghị (HĐ thật) |

**Ghi chú không cần quyết định:** (1) **D3b (Windows không ads) — CHỐT USER 2026-10-28**, và **bản Windows là F2P + IAP** (không còn bản paid premium riêng). Lý do *hạ tầng*: Microsoft không còn ad SDK cho game [S122], không có plugin Godot cho SDK Windows nào. **Hệ quả:** D4/G9 **không áp dụng Windows** (chỉ Android/Fire/AppGallery); **G12 đổi từ "giá premium Windows" thành "giá IAP / battle pass Windows"**; **G16 (eCPM Windows) biến mất** — không cần dự đoán khi không có ads. (2) **HK/Macau/Đài Loan là đường hợp lý** nếu muốn có người chơi Trung văn — không cần NPH-TQ, không cần 版号, đi qua store quốc tế.
