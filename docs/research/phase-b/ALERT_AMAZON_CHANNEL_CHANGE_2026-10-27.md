# ⚠ AMAZON CHANNEL — THAY ĐỔI CẤP GATE-1 (phát hiện 2026-10-27)

> **Vai:** commercial-researcher (`arena/46e50499`) — vòng ④ của prompt lane (ads trên Fire 2026) **mở rộng thành báo động kênh Amazon**.
> **Lý do viết:** trong lúc kiểm trạng thái ads Fire 2026, phát hiện một thay đổi **làm sai giả định D1/D10 và ảnh hưởng 4 deliverable đã giao**. Việc này **không thể im lặng** chờ tới Gate-6.
> **Ngày tra cứu:** 2026-10-27. Nhãn: `STATIC_CONFIRMED` (nguyên văn chính chủ, đã fetch) · `BT3` (bên thứ ba) · `INFERRED` · `UNKNOWN`.
> **Nguồn mới:** S116–S121.

---

## 0. Một đoạn tóm tắt

**Amazon đã ngừng dùng Amazon Appstore cho tablet.** Ngày **08/10/2026** Amazon ra dòng **Alexa Tablet** chạy **Android 16 đầy đủ + Google Play**, thay cho Fire tablet. FAQ chính chủ của Amazon nói thẳng: muốn phát hành trên Alexa Tablet thì **phải nộp app lên Google Play**; **APS không có trên Alexa Tablet**, dùng **AdMob** thay thế; **doanh số/thanh toán/thuế đều nằm ở Google Play Console**, không hiện trong Amazon Developer.

⇒ Kênh "Amazon Appstore" từ hôm nay chỉ còn: **Fire TV (Vega)**, **installed base Fire tablet (đang sunset)**, và **Amazon Kids+**. Còn "tablet Amazon" — thị trường tablet lớn nhất của họ — thì **không còn đi qua Amazon Appstore nữa**.

---

## 1. Bằng chứng chính chủ (nguyên văn)

**Nguồn: `developer.amazon.com/docs/device-specs/alexa-tablet-devices-faq.html` — "Last updated: Oct 08, 2026"** `STATIC_CONFIRMED`

| Mục | Nguyên văn |
|---|---|
| **App submission** | *"Unless you are submitting an Amazon Kids+ app, you will need to submit your app to the Google Play Store to distribute on Alexa Tablets."* |
| **Account** | *"If you would like to distribute your apps on the new Alexa Tablets, you will need to submit your app to the Google Play Store. The Amazon Appstore Support team has no visibility or access to your Google Play account."* |
| **Testing** | *"Alexa Tablets are not available in Appstore Quality Central. If you would like to do Live App Testing on Alexa Tablets, please use Google Play's pre-launch testing options."* |
| **Monetization / ads** | *"APS is not available on Alexa Tablets. Please use Google AdMob or equivalent as an alternative."* |
| **Reporting & telemetry** | *"All app-related activities – including sales, engagement, statistical data, and payments – on Alexa Tablets will be visible on your Google Play Console. This information is not available in your Amazon Developer account."* |
| **Taxes & payments** | *"For any questions related to earnings, taxes, and payments made on your app's Alexa Tablet sales, please contact Google Play Support."* |

**Xác nhận thiết bị (chính chủ):** `developer.amazon.com/docs/device-specs/` có trang spec cho **Alexa Tablet 8 / 11 / 12 Pro (2026)** — **Initial OS version: Android 16, API level 36**, `Build.MANUFACTURER == "Amazon" && GoogleApiAvailability == true`. Tức đây là **thiết bị GMS thật**, không phải Fire OS. `STATIC_CONFIRMED` [S118]

**Xác nhận từ kênh dev chính chủ Amazon (Dev News 12/10/2026):** *"Alexa Tablet apps distribute through Google Play (except Amazon Kids+), test on Play's pre-launch tracks, and use AdMob or similar instead of Amazon Publisher Services."* `STATIC_CONFIRMED` [S117]

**Thông cáo chính chủ Amazon (08/10/2026, Kevin Keith – VP Devices):** dòng tablet mới *"run Android, and come with access to the full Google Play Store"*. `STATIC_CONFIRMED` [S119]

**Về số phận Fire tablet:** Amazon *"will stop shipping the devices in the next month or two"* và *"support them for four years from the last ship date"* — đây là **Amazon trả lời báo chí**, ta đọc qua Wired; **không tìm được trang chính chủ Amazon phát biểu cùng nội dung** ⇒ nhãn `BT3` (trích phát ngôn Amazon). `BT3` [S120]

---

## 2. Ảnh hưởng trực tiếp tới các quyết định đã chốt

| Quyết định | Nội dung đã chốt | Còn đúng không? | Ghi chú |
|---|---|---|---|
| **D1** | Giữ Amazon, định vị **kênh Fire tablet/TV** | **KHÔNG còn đúng nguyên trạng** | Fire tablet = installed base đang sunset; tablet mới **không** đi qua Amazon Appstore. Kênh thật còn lại: **Fire TV/Vega + Kids+** |
| **D10** | **Fire tablet trước**; Fire TV/Vega hoãn | **Đảo chiều** | "Tablet trước" giờ nghĩa là **đi Google Play**, không phải Amazon Appstore. Nếu vẫn chỉ 3 store: phải chuyển sang **Fire TV trước** hoặc chấp nhận chỉ phục vụ installed base |
| **D9a** | 1 interface + 3 adapter (Amazon IAP) | Adapter Amazon **vẫn cần** cho Fire TV/Fire OS cũ | Nhưng **không dùng được trên Alexa Tablet** (sales/payments ở Google Play) ⇒ adapter này phục vụ **thiết bị legacy + TV**, không phải tablet mới |
| Nền tảng 3 store đã LOCK | MS · Amazon · Huawei | **Cần xem lại** | Muốn chạm tablet Amazon mới **bắt buộc** có Google Play = **store thứ 4** (mâu thuẫn với "chốt đúng 3") |

**Bốn deliverable bị ảnh hưởng:**
1. `PHASE_B_COMMERCIAL_RESEARCH.md` — toàn bộ §3.2 mô tả Amazon như kênh Fire tablet đang sống.
2. `STORE_COMPARISON_3COL.md` — dòng "Amazon = Fire tablet/TV" cần sửa.
3. `GATE6_SUBMISSION_KITS.md` — kit Amazon (rating/privacy labels) **vẫn đúng cho Fire TV / Fire OS / Kids+**, nhưng **vô dụng cho Alexa Tablet** (ở đó Google Play quyết).
4. `GATE4_GODOT_COMMERCE_QUEUE.md` — Appstore SDK adapter vẫn cần cho Fire TV, nhưng **không dùng cho tablet mới**; phần "ads trên Fire" phải tách 2 nhánh.

---

## 3. Trạng thái ads trên Fire — trả lời câu hỏi ④

### 3.1 Fire OS / Fire TV (kênh Amazon Appstore còn sống)

| Kênh quảng cáo | Trạng thái 2026 | Nguồn |
|---|---|---|
| **Amazon Mobile Ad Network** | **ĐÃ CHẾT** — deprecate 30/09/2021, không nhận app mới | [S48] `STATIC_CONFIRMED` |
| **APS (Amazon Publisher Services)** | **Còn sống**, nhưng là **header bidding** (không phải ad network tự phục vụ): SDK/tag + đấu giá qua TAM/UAM; **supports Fire TV + Fire tablets** | [S121] `STATIC_CONFIRMED` |
| Điều kiện vào APS | **Không phải open enrollment**: nộp → Amazon review **một lần**, **không có appeal path**; review gồm **content governance + brand safety**; **không công bố tiêu chí** | [S121] `BT3` (phân tích của vendor, trích tài liệu Amazon) |
| Phí APS | **10% publisher transaction fee** trên demand Amazon DSP qua TAM (từ 09/2023); TAM còn "nominal $0.01 CPM charged to bidders" | [S53][S121] |
| Ràng buộc đáng chú ý | Với **Fire TV app có ads** ≥50.000 giờ/tháng (Mỹ) hoặc ≥30.000 giờ/tháng (quốc gia khác có APS), **sau khi Amazon liên hệ**, dev **buộc** tích hợp APS và **nhường 30% tổng impression trong nước** cho Amazon, **Amazon giữ 100% doanh thu** phần đó | [S121] `STATIC_CONFIRMED` |

> ⚠ Điều khoản cuối là **điều khoản thật, đang hiệu lực**, áp cho **Fire TV**. Với game của ta (không phải video streaming, và quy mô nhỏ) gần như chắc chắn không chạm ngưỡng 30–50k giờ/tháng — nhưng nó cho thấy **Amazon có quyền lấy 30% inventory** khi đủ lớn. Không được giả định "ads trên Fire là tự do".

### 3.2 Alexa Tablet (thiết bị Amazon mới)

- **APS KHÔNG có.** Nguyên văn: *"APS is not available on Alexa Tablets. Please use Google AdMob or equivalent as an alternative."* [S116] `STATIC_CONFIRMED`
- ⇒ Trên tablet Amazon mới, ads đi qua **AdMob hoặc tương đương** — tức hệ sinh thái Google, không phải Amazon.

### 3.3 Kết luận cho D8a (rewarded-only, cap 4–6/ngày)

- Trên **Alexa Tablet**: rewarded qua AdMob — khả thi về mặt kỹ thuật, nhưng **không cần SDK Amazon nào**, và **cần Google Play** để phân phối.
- Trên **Fire OS cũ**: rewarded qua các SDK trong danh sách tương thích của Amazon (Vungle/Mintegral/Chartboost/AppLovin…) hoặc APS. **AdMob không nằm trong danh sách tương thích** — nhắc lại rủi ro đã ghi ở Gate-4 [S46].
- Trên **Fire TV**: màn hình TV + remote ⇒ UI/UX khác hẳn, và **không nằm trong MVP** (D10a trước đây hoãn TV).

**Kết luận thẳng:** nếu vẫn giữ đúng **3 store đã lock**, thì **kênh Amazon có doanh thu thực tế đang teo rất nhanh**: tablet mới đi Google Play, Fire tablet ngừng bán, chỉ còn Fire TV/Vega (cần UI riêng) và installed base 4 năm.

---

## 4. Ba phương án — cần user chốt (leo thang, không tự quyết)

| | Phương án | Nội dung | Ưu | Nhược |
|---|---|---|---|---|
| **A** | **Giữ đúng 3 store, thu hẹp Amazon** | Amazon = **Fire TV/Vega + installed base Fire OS**; bỏ mục tiêu "tablet" trên Amazon. Không thêm Google Play | Không phá vỡ quyết định đã lock; không thêm việc | **Phải làm UI/UX cho TV** (D10 trước đây hoãn) hoặc chỉ sống bằng installed base đang chết dần. Adapter Amazon IAP chỉ phục vụ thiết bị legacy |
| **B** | **Sửa bộ store: thay Amazon bằng Google Play** | 3 store = **MS · Google Play · Huawei**; bỏ Amazon | Chạm được **tablet Amazon mới** (vì chúng chạy Play) + toàn bộ Android; **AdMob/Play Billing có sẵn plugin Godot chính thức** (xem Gate-4) ⇒ giảm mạnh khối lượng adapter phải tự viết | **Phá quyết định "chốt đúng 3 store"** của user; cần tài khoản Play ($25 một lần); mất SBAP 80/20 và Fire TV |
| **C** | **Giữ Amazon + thêm Google Play = 4 store** | MS · Amazon (TV/legacy) · Huawei · **Google Play** (cho tablet Amazon mới + Android) | Phủ hết; giữ quan hệ Amazon | **4 adapter**, scope lớn nhất; nhiều nghĩa vụ tuân thủ nhất; trái tinh thần "3 store" |
| **D** | **Bỏ Amazon, giữ 3 store khác** | MS · Huawei · (thêm store khác hoặc chỉ 2) | Đơn giản | Mất kênh Amazon hoàn toàn; "3 store" thành 2 |

**Đề xuất của lane (không phải quyết định):** **A trước, B là phương án dài hạn.**
Lý do: (1) A không phá vỡ gì đã chốt và vẫn dùng được toàn bộ hồ sơ Gate-6/Gate-4 đã làm cho Fire OS; (2) nhưng A **không thể là chiến lược dài hạn** vì Fire TV đòi UI riêng và installed base có hạn 4 năm; (3) B rẻ hơn về kỹ thuật (có plugin chính thức) và chạm được chính thiết bị Amazon mới — nên **quyết định B nên được đưa ra ở Gate-2 (Product Brief/target player), không phải bây giờ** khi chưa có số liệu.

**Điều KHÔNG nên làm:** tiếp tục coi "Amazon Appstore = kênh tablet" trong bất kỳ tài liệu nào từ hôm nay.

---

## 5. Việc lane này sẽ làm tiếp (không chờ quyết định)

1. **Sửa 4 deliverable** để ghi rõ: mọi mục "Amazon" trong tài liệu cũ áp cho **Fire TV / Fire OS / Kids+**, **không** áp cho Alexa Tablet. Đánh dấu bằng khối cảnh báo đầu file, không xoá nội dung cũ (giữ vết).
2. Bổ sung **cột "Alexa Tablet"** vào bảng so sánh 3 store → thành 3 store + 1 kênh đặc biệt.
3. Giữ nguyên mốc ĐÓNG lane (Gate-6 kits) nhưng **không báo XONG** cho tới khi user chốt A/B/C/D — vì lựa chọn đó đổi **tập store** mà kit phải phục vụ.

---

## 6. Nguồn mới

| ID | Nguồn | Loại | Dùng cho |
|---|---|---|---|
| S116 | **Amazon — Alexa Tablet Devices FAQ** (`last updated Oct 08, 2026`) | CP | Nguyên văn: phải nộp qua **Google Play** trừ Kids+; **APS không có**, dùng **AdMob**; sales/payments/thuế ở **Play Console** |
| S117 | Amazon Developer Community — Dev News 12/10/2026 | CP | Bản tóm tắt chính chủ: *"distribute through Google Play (except Amazon Kids+), test on Play's pre-launch tracks, and use AdMob or similar instead of APS"* |
| S118 | Amazon — Alexa Tablet device specs + Identify Alexa Tablet Devices | CP | Android 16 / API 36; `MANUFACTURER=="Amazon" && GoogleApiAvailability==true` |
| S119 | aboutamazon.com — Introducing all-new Alexa Tablets (08/10/2026, Kevin Keith VP Devices) | CP | Thông cáo chính chủ: chạy Android, **full Google Play Store** |
| S120 | Wired / CNBC / Reuters / TechCrunch về Alexa Tablet & Fire sunset | BT3 | Fire tablet **ngừng ship trong 1–2 tháng**, hỗ trợ **4 năm** từ lần ship cuối; giá $229–$549; bán ở US/CA/MX từ 14/10, EU từ 19/10 |
| S121 | Amazon — Appstore Advertising Policies (Fire TV inventory share) + APS publisher page + phân tích vendor | CP + BT3 | APS cho **Fire TV + Fire tablets**; Fire TV ≥30–50k giờ/tháng **buộc** APS + **nhường 30% impression**, Amazon giữ 100% doanh thu phần đó; APS review một lần, không appeal, không công bố tiêu chí |
