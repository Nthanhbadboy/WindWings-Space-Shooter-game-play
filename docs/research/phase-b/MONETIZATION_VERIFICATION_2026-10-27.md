# XÁC MINH TUYẾN KIẾM TIỀN 3 STORE — theo thông tin user (2026-10-27; user duyệt lần 135)

> Nguồn: tra cứu web ngày 2026-10-27, link chính chủ tại chỗ. Nhãn bằng chứng 6 loại. Tình trạng user khai:
> ① MS đã đăng ký kiếm tiền + khai thuế ② Amazon chưa làm ③ Huawei đã đăng ký ④ cả 3 store dùng hệ thống thanh toán riêng, KHÔNG qua Google Billing ⑤ keystore user tự thêm.
> **User duyệt (lần 135): "OK đẩy — 3 store kiếm tiền theo đúng luật của chúng nó, không phải bàn cãi."** ⇒ Nguyên tắc thương mại chốt: mỗi store dùng commerce/ads riêng theo đúng quy định của store đó (Amazon IAP bắt buộc · HMS IAP/Ads Kit · Windows.Services.Store) — không lách, không tranh cãi policy.

## Verdict từng ý

| Ý user | Verdict | Bằng chứng |
|---|---|---|
| MS: "đăng ký kiếm tiền + khai thuế rồi" | ✓ ĐÚNG VÀ ĐỦ — MS chỉ yêu cầu đúng 2 thứ trước khi nhận tiền: **payout profile** (ngân hàng/PayPal) + **tax profile** (không phải Mỹ → **W-8BEN**), trạng thái phải **Complete** (validation ~48h; đang "Pending validation" thì chưa tính là xong) | learn.microsoft.com — Set up payout and tax profiles; Manage account ("Regardless of country, must fill US tax forms; non-US → W-8"); FAQ manage-your-account; Q&A payout-validation ~48h — STATIC_CONFIRMED |
| Amazon: "chắc tương tự, chưa làm" | ✓ CHÍNH XÁC — Amazon yêu cầu **Tax Identity Interview** (Mỹ + Canada) trong Developer Console (My Settings > Tax Identity) trước khi nhận royalty; trả hàng tháng, ~30/45 ngày sau cuối tháng, chiếu tài liệu 1099/1042-S. **Tài khoản chưa tạo → đây là mục USER-ONLY còn lại duy nhất về tài khoản** | developer.amazon.com — Set Up Tax Forms; Appstore Payments; Getting-paid blog (2024) — STATIC_CONFIRMED |
| Huawei: "đăng ký rồi; thị trường này chỉ kiếm tiền bằng quảng cáo và hệ thống của nó" | ✓ ĐÚNG — hai tuyến tiền vào: **HMS IAP Kit** (bắt merchant verification 1–2 ngày, khai ngân hàng + thuế, public key, 3 loại hàng hoá) và **HUAWEI Ads Kit / Petal Ads Publisher** (OAID, SDK, console riêng). Không có Google Billing (thiết bị HMS không GMS) | developer.huawei.com — Ads Kit; Ads Publisher Service; AppGallery Review Guidelines §6 (khuyến nghị HMS IAP); Merchant Service Agreement (thuế VAT/WHT); Petal Ads settlement — STATIC_CONFIRMED |
| "Cả 3 store hệ thống kiếm tiền riêng, không qua gg billing" | ✓ XÁC NHẬN 3/3 — Amazon: digital goods **phải** dùng Amazon IAP, không ngoại lệ, vi phạm = reject; Huawei: guideline khuyến nghị/bắt lộ trình HMS IAP; Microsoft: commerce riêng của Store (Windows.Services.Store). Google Play Billing không tồn tại trên cả 3 kênh | Amazon policy Monetization + blog compliance (2025) "No exception to IAP policy"; Amazon migrate-google-billing doc (Google Billing ≠ Amazon IAP); Huawei guideline §6.4 — STATIC_CONFIRMED |
| "keystore tôi sẽ add vào" | ✓ GHI NHẬN — user giữ & tự ký. Lưu ý kỹ thuật: Android (AppGallery + Amazon) = release keystore của user; **Huawei AAB ≤150MB bắt buộc App Signing** (upload key + app signing key Huawei giữ); Amazon nhận APK/AAB ký bằng key user; **MS Store: Partner Center tự ký MSIX** — không cần keystore riêng cho kênh Windows | Huawei App Review FAQ (bổ sung vòng 134, Phase B); Amazon submission docs; MS packaging docs — STATIC_CONFIRMED |

## Phát hiện tiền về — ảnh hưởng trực tiếp dev Việt Nam

1. **VIỆT NAM CHƯA CÓ HIỆP ĐỊNH THUẾ THU NHẬP ĐANG HIỆU LỰC VỚI MỸ** (ký 2015 nhưng chưa có hiệu lực — tính đến 9/2026). Hệ quả: phần doanh thu **khách Mỹ** trên MS Store bị **withholding 30%** (mặc định không-giảm được qua treaty); phần khách ngoài Mỹ **không** bị giữ tại nguồn. Amazon cùng logic: US-source royalty bị giữ theo interview (không có treaty VN để giảm). → Tính giá/báo doanh thu cần tách "thu nhập ròng US vs ngoài-US". STATIC_CONFIRMED (IRS-list via w8ben guide; taxesforexpats 9/2026; MS "withholding applies only to US sales").
2. **Huawei trả tiền hàng tháng**: settlement sheet ngày 15 (tháng trước), xác nhận trong 15 ngày (không trả lời = tự xác nhận), ngưỡng **€200** mới trả, trả trong 30 ngày sau xác nhận. STATIC_CONFIRMED (Petal Ads Financial Settlement).
3. **MS**: payout hàng tháng khi đạt ngưỡng tối thiểu; nếu tax profile đang "Pending Microsoft Action" thì không sửa được gì cho tới khi xong. STATIC_CONFIRMED (Partner Center docs).
4. **Amazon**: chỉ còn kênh Fire tablet/TV (kênh Android chung đóng 20/08/2025); JP market đã tắt IAP từ 20/02/2025 — đăng phạm vi marketplace nhớ tắt/bỏ JP cho IAP. STATIC_CONFIRMED (Amazon blog 02/2025; Wikipedia).

## Lưu ý nhỏ (không chặn, ghi để minh bạch)

- **MS policy 10.14 (cập nhật 21/10/2026):** tài khoản **Company** dành cho ai hoạt động thương mại/nghề nghiệp; Individual cho cá nhân phi-thương-mại (Q&A trên learn.microsoft.com trích policy). Tài khoản MS của user đã tạo theo loại nào thì dùng đúng loại đó; không đổi được Individual→Company. → Khi nộp app, cứ đi theo loại tài khoản hiện có. Nhãn: INFERRED (từ Q&A + policy, cần xem lại khi nộp).
- **Amazon Mobile Ad Network** vẫn được nhắc trong doc submission (01/2026) nhưng trạng thái nhận app mới cần E verify trước khi tính rewarded-ads trên Fire. RUNTIME_UNVERIFIED → E-queue.

## Hệ quả vào kế hoạch (sửa PHASE_C khi user duyệt)

| USER-ONLY mục | Trạng thái mới |
|---|---|
| #1 Pháp lý D5 | **MS ✓ (đã có tài khoản + thuế)** · **Huawei ✓ (đã đăng ký)** · **Amazon ✗ chưa** — mục duy nhất còn: tạo tài khoản Amazon + Tax Identity Interview |
| #2 Tạo 3 tài khoản | → thu hẹp còn **Amazon** |
| #3 Quyền IP/art gốc | giữ nguyên — chờ user xác nhận (mục duy nhất không liên quan tài khoản) |
| #4 Keystore | **user tự thêm — xác nhận**; chỉ nhớ Huawei AAB cần App Signing bật trong console |
| #5 Payout/tax | MS ✓ · Huawei ✓ (merchant IAP + Ads) · **Amazon pending** |
| #6 Lệnh SDK/publish | giữ nguyên |

## E-queue bổ sung (research kiếm tiền —Godot + 3 store)

- Godot × Amazon IAP / **Billing Compatibility SDK** (API giống Google Play → có thể tái dùng đường plugin Godot Google Billing?) — E verify.
- Godot × **HMS IAP plugin + Ads Kit** trên AppGallery — E verify (cộng đồng đã có plugin nào 2026?).
- Ads trên **Fire tablet** 2026: Amazon Mobile Ad Network nhận app mới? AdMob không-GMS? → quyết D8a trên kênh Amazon.
- Quy tắc hợp tác xuất hoá đơn/ thuế VN khi nhận tiền từ Huawei (EUR) và Amazon — để user đối chiếu với người làm thuế của user (không research thay quyết thuế).
