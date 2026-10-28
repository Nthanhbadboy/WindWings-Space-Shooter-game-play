# QUEUE GODOT — Ma trận plugin IAP / Ads / Analytics cho 3 store


> 🔴 **CẢNH BÁO KÊNH AMAZON (bổ sung 2026-10-27, sau khi tài liệu này hoàn tất):** từ **08/10/2026** Amazon đã thay dòng Fire tablet bằng **Alexa Tablet (Android 16 + Google Play)**. Theo FAQ chính chủ Amazon, app cho Alexa Tablet **phải nộp qua Google Play** (trừ Amazon Kids+), **APS không khả dụng** (dùng AdMob), và doanh số/thanh toán/thuế nằm ở **Play Console**. ⇒ Mọi nội dung "Amazon" trong tài liệu này chỉ còn áp dụng cho **Fire TV/Vega, Fire OS installed base, và Amazon Kids+** — **KHÔNG** áp dụng cho tablet Amazon mới. Xem [`ALERT_AMAZON_CHANNEL_CHANGE_2026-10-27.md`](./ALERT_AMAZON_CHANNEL_CHANGE_2026-10-27.md) [S116–S121]. Việc này ảnh hưởng **D1/D10/D9a** và đang chờ user chốt phương án A/B/C/D.

> **Vai:** commercial-researcher (`arena/46e50499`) — **ưu tiên ②** của prompt lane. **Ngày tra cứu:** 2026-10-27.
> **Trạng thái:** research-only. Không cài SDK, không build, không tạo tài khoản store, không sửa protected paths. Đây là **đầu vào kỹ thuật** cho session Godot-coder (vai trống) + verifier `ef6b75ef`, **không phải** quyết định kiến trúc — D9a đã chốt interface chung + adapter.
> **Nhãn bằng chứng:** `STATIC_CONFIRMED` (đọc trực tiếp nguồn chính chủ/repo) · `INFERRED` (suy luận có nêu giả định) · `UNVERIFIED` (không tìm được nguồn) · `CONFLICTING`.
> **Nguồn mới:** S89–S104 (đã thêm vào [SOURCES.md](./SOURCES.md)).

---

## 0. Kết luận đi thẳng vào việc

**Ba store, ba commerce SDK khác nhau — và chỉ một trong số đó có plugin Godot chính thức, mà lại là store ta KHÔNG dùng.**

| Store | SDK bắt buộc | Plugin Godot chính thức? | Hệ quả cho D9a |
|---|---|---|---|
| **Microsoft Store (Windows)** | `Windows.Services.Store` (WinRT) | **Không có** — phải viết **GDExtension C++/WinRT** | Adapter #1 = code native mới |
| **Amazon Appstore (Fire)** | **Appstore SDK** (IAP native, v3.0.9) | **Không có** — issue Godot #91029 vẫn mở từ 2024 | Adapter #2 = Android plugin mới |
| **Huawei AppGallery** | **HMS IAP Kit** | **Không có** cho IAP (chỉ có mẫu Ads cộng đồng) | Adapter #3 = Android plugin mới |
| *(Google Play — KHÔNG dùng)* | Google Play Billing | **Có** — `GodotGooglePlayBilling` v3.3.0, Godot Foundation duy trì | Chỉ dùng làm **khuôn API tham chiếu** |

⇒ **D9a đúng về kiến trúc nhưng rẻ hơn thực tế nhiều:** "1 interface + 3 adapter" trên Godot nghĩa là **3 adapter phải tự viết**, không phải cấu hình plugin có sẵn. Đây là chi phí kỹ thuật lớn nhất của lane Godot và cần được đưa vào Gate-5 (MVP scope) dưới dạng work-item có chủ.

---

## 1. Nhánh Amazon — kết quả rõ ràng, kể cả tin xấu

### 1.1 Tin quan trọng nhất: con đường "mượn API Google Billing" đã đóng

Amazon có **Appstore Billing Compatibility SDK** — thư viện mô phỏng đúng API Google Play Billing (đổi `com.android.billingclient.api` → `com.amazon.device.iap.billingclient.api`), hỗ trợ consumable/entitlement/subscription, tương thích GPB 4.0–7.0. `STATIC_CONFIRMED` [S91][S92]

Nhưng — **nguyên văn từ tài liệu Amazon và thông báo chính thức:** *"Starting September 15, 2026, Amazon Appstore will no longer offer technical support or maintenance for the Appstore Billing Compatibility SDK"*; *"The Easy Port Gradle plugin will also be discontinued on September 15th"*. `STATIC_CONFIRMED` [S92][S93]

Đánh giá hệ quả (hôm nay **27/10/2026**, tức **đã quá hạn 42 ngày**):
- Tích hợp cũ **vẫn chạy** ("existing IAP integration … will continue to function") — không phải SDK chết. `STATIC_CONFIRMED` [S93]
- Nhưng **không còn support/maintenance**, và **tính năng mới (subscription modifications, add-ons) chỉ có ở Appstore SDK native**. `STATIC_CONFIRMED` [S93]
- ⇒ Với **dự án mới** (ta), viết mới trên một SDK đã hết hỗ trợ là quyết định tồi. **Chọn Appstore SDK native.** `INFERRED` (khuyến nghị, không phải tuyên bố của Amazon)

### 1.2 Không có plugin Godot cho Amazon IAP

| Bằng chứng | Nhãn |
|---|---|
| `binogure-studio/godotamazon` — module Amazon IAP + Game Circle, **Godot 2.1** (2018) | `STATIC_CONFIRMED` [S95] |
| `josh-oo/godot-amazon-android-module` — module engine, thời Godot 2/3 (`engine.cfg`), không phải plugin v2 | `STATIC_CONFIRMED` |
| Godot issue **#91029** (2024): *"Amazon In-App Purchase on Godot 4.2.1 … In-app purchase plugin codes for Android and iOS are available in the Godot official documentation, but not for Amazon"* — **vẫn là yêu cầu chưa được đáp** | `STATIC_CONFIRMED` [S95] |
| Tài liệu Godot chính thức chỉ mô tả `GodotGooglePlayBilling` — không có mục Amazon | `STATIC_CONFIRMED` [S89] |

**Việc phải làm:** viết **Android plugin v2** (Java/Kotlin + `.gdap`/`.gdip`) bọc Appstore SDK, expose GDScript API khớp interface chung. Tham chiếu triển khai: `AmazonAppDev/amazon-iap-kotlin` (mẫu Kotlin chính chủ, test bằng **Amazon App Tester** + `amazon.sdktester.json`). `STATIC_CONFIRMED` [S94]

### 1.3 Nhánh DRM/Simple Sign-in có sẵn (không cần làm)

Appstore SDK gộp **IAP + DRM + Simple Sign-in** trong một JAR — tức nếu sau này cần chống copy APK hoặc đăng nhập nhẹ, không phải thêm SDK. `STATIC_CONFIRMED` [S94]

---

## 2. Nhánh Huawei

### 2.1 IAP Kit — không có plugin Godot

Đã rà: tài liệu Godot chỉ có Google Play Billing [S89]; hệ sinh thái plugin HMS có Cocos SDKHub (IAP + Ads Kit), Unity (HMS Unity Plugin), Solar2D (`com.solar2d-plugin.huaweiIAP`), libGDX, React Native — **không có Godot** [S105]. `INFERRED` (kết luận từ vắng mặt; đã tìm theo nhiều cách, không thấy repo Godot nào)

⇒ Adapter #3 = Android plugin v2 bọc `com.huawei.hms:iap`. Dùng **IapClient** (3 loại hàng: consumable / non-consumable / subscription — khớp S43 đã đăng ký). Không dùng HMS Toolkit: **HMS Toolkit sẽ ngừng cập nhật, các dịch vụ ở nước ngoài decommission 30/12/2026**. `STATIC_CONFIRMED` [S104]

### 2.2 Petal Ads — chỉ có mẫu cộng đồng, KHÔNG có plugin chính thức

| Thứ có | Chi tiết | Nhãn |
|---|---|---|
| SDK chính chủ | `com.huawei.hms:ads-prime` (chạy cả máy Huawei **và** Android khác, ngoài đại lục) hoặc `ads-lite` (chỉ máy Huawei). Yêu cầu **HMS Core (APK) 4.0.0.300+**. Có `ads-omsdk` nếu cần đo hiệu quả quảng cáo. | `STATIC_CONFIRMED` [S97] |
| Mẫu Godot 4 (cộng đồng, cá nhân) | Repo `moussabhamza99-creator/petlads` — Android plugin + wrapper GDScript, banner/interstitial/rewarded, có **ad unit test chính chủ của Huawei** (`testw6ac88gbe3`, `testb4z2vhch44`, `testx9dtjw2sp5`). Chất lượng: repo cá nhân, không bảo trì cam kết | `STATIC_CONFIRMED` (nội dung repo) + `UNVERIFIED` (độ tin cậy/bảo trì) [S98] |
| Mẫu Godot 3.5 | `samaranez1/Petal-Ads-for-Godot-3.5` — banner + rewarded; ghi chú: **rewarded cần máy có HMS Core** | `STATIC_CONFIRMED` [S98] |

⇒ Adapter ads Huawei: **dùng ads-prime** (vì D2a phát hành ngoài đại lục, app chạy trên cả máy Huawei lẫn Android thường), viết plugin riêng lấy mẫu cộng đồng làm tham chiếu. **Không** dùng `ads-lite` (sẽ không fill trên máy không-Huawei).

---

## 3. Nhánh Windows

### 3.1 `Windows.Services.Store` — điều kiện tiên quyết rất cụ thể

`STATIC_CONFIRMED` [S101]:
- Namespace chỉ dùng được từ **Windows 10 1607 (build 14393)** trở lên.
- **Bắt buộc app là MSIX package có identity liên kết với Partner Center.** Với app Flutter đóng MSIX, plugin cộng đồng ghi rõ: *"An unpackaged build (flutter run) reports isAvailable() == false"* — và thảo luận CsWinRT của Microsoft trả lời thẳng: **"It won't work. The API requires that the full package be available in the Microsoft Store."**
- **Không chạy được khi app chạy elevated (as administrator)** — Microsoft không hỗ trợ Store purchase ở app elevated.
- **Không có receipt phía client.** Muốn xác thực server-side phải dùng **Microsoft Store collection API**.
- `StoreLicense.IsActive` **luôn true** với add-on ⇒ phải xét theo **ExpirationDate**.
- **Không có trạng thái pending**: hộp thoại Store kết thúc trước khi hàm trả về.

### 3.2 Hệ quả cho Godot trên Windows

- Godot export Windows ra **exe thường**, không phải MSIX → **phải đóng gói MSIX** mới gọi được Store API. Điều này khớp: MSIX là định dạng được Store **ký lại và host miễn phí**. `STATIC_CONFIRMED` [S103]
- Không tìm thấy plugin/GDExtension có sẵn cho `Windows.Services.Store` trong Godot ⇒ **viết GDExtension C++/WinRT** gọi `StoreContext::GetDefault()`. `INFERRED` (từ vắng mặt plugin)
- Kiểm thử khó: **dev license không phải retail license** — tài liệu Microsoft ghi *"A developer license is not a retail license and is not supported; using one may result in errors or crashes"* [S101]. ⇒ Test IAP thật chỉ làm được qua **submission ở Partner Center** (gói flight/private audience), không test được ở máy dev thuần. **Đây là rủi ro lịch sử lớn nhất của nhánh Windows.**
- Vì **D3b: Windows không ads (CHỐT USER 2026-10-28)**, không cần SDK ads trên Windows ⇒ giảm hẳn một nhánh rủi ro. **⇒ G9 ("remove ads" còn bán được không) KHÔNG ÁP DỤNG Windows** — chỉ Android/Fire/AppGallery.

---

## 4. Analytics

| Ứng viên | Trạng thái | Ghi chú cho ta |
|---|---|---|
| **GameAnalytics** | **SDK Godot chính thức** (`GA-SDK-GODOT`), dạng **GDExtension**; yêu cầu **Godot 4.5+**, SCons + Python; hỗ trợ **Android, Windows, Mac, Linux, iOS, Web**; Asset Store cập nhật **15/09/2026**. `STATIC_CONFIRMED` [S99][S100] | **Ứng viên chính.** GameAnalytics là **đối tác Huawei Ecosystem từ 2021**, SDK Android có hỗ trợ **OAID** — phù hợp AppGallery. `STATIC_CONFIRMED` (thông cáo chính thức) |
| GameAnalytics trên **Fire OS** | **Không có tuyên bố hỗ trợ Fire OS** trong tài liệu | `UNVERIFIED` — Fire OS là Android không GMS; SDK chủ yếu gửi HTTP nên *khả năng* chạy được, nhưng **phải test thật trên Fire**, không suy diễn |
| **Huawei Analytics Kit** | `com.huawei.hms:hianalytics`; phải **bật Analytics trong AGC** + chọn data processing location trước khi dùng. `STATIC_CONFIRMED` [S106] | Tuỳ chọn **bổ sung** nếu cần số liệu trong AGC console; không nên làm nguồn sự thật duy nhất (khoá vào 1 store) |
| **Firebase** | Không rà trong vòng này | `UNKNOWN` — ngoài phạm vi; nếu cân nhắc thì phải kiểm chứng riêng (Fire không GMS là rủi ro) |

**Nguyên tắc đề xuất:** **một** analytics duy nhất làm nguồn sự thật (GameAnalytics) để D1/D7/D30 + ARPDAU so sánh được giữa 3 store; công cụ riêng của store chỉ để đọc số trong console. Lý do: nếu mỗi store một bộ số, không so sánh được — đúng yêu cầu metric của Phase B §5.

---

## 5. Xác thực biên lai (server-side) — phần dễ bị bỏ sót

Không store nào cho receipt tin cậy ở client theo cách giống nhau:

| Store | Cách xác thực | Nguồn |
|---|---|---|
| Amazon | **RVS** (Receipt Verification Service) — REST `purchases.products.get`, `purchases.subscriptionsv2.get` | [S91] |
| Huawei | **HMS IAP server-side verify** (purchaseToken) | S38/S43 (đã có) |
| Microsoft | **Microsoft Store collection API** (không có receipt client) | [S101] |

Có thư viện Go mã nguồn mở `go-iap` hỗ trợ **Amazon, HMS, Microsoft Store** trong cùng một API verify — dùng được làm tham chiếu/khung cho backend, hoặc để so sánh luồng. `STATIC_CONFIRMED` [S102] (chất lượng/bảo trì: `UNVERIFIED`)

⇒ **Hệ quả:** backend verify là **work-item riêng**, không phải "phần thêm". Nếu MVP chưa có backend, cần chấp nhận rủi ro gian lận ở mức thấp và ghi rõ là nợ kỹ thuật.

---

## 6. Ma trận quyết định (một trang)

| Hạng mục | Windows | Amazon/Fire | Huawei/AppGallery |
|---|---|---|---|
| **IAP** | GDExtension C++/WinRT → `StoreContext`; **cần MSIX** | Android plugin v2 → **Appstore SDK 3.0.9** | Android plugin v2 → **HMS IAP Kit** |
| **Plugin có sẵn?** | ❌ | ❌ | ❌ |
| **Test ở máy dev** | ❌ (cần retail license qua submission) | ✅ **Amazon App Tester** + `amazon.sdktester.json` | ⚠️ sandbox IAP; cần máy có HMS Core cho ads |
| **Ads** | **Không** (D3b) | APS (invite-only) / AppLovin MAX 11.8.2 / Vungle; **AdMob không có trong danh sách Amazon** | **Petal Ads `ads-prime`** (không phải ads-lite), cần HMS Core 4.0.0.300+ |
| **Ads plugin Godot** | — | ⚠️ AdMob của Poing chạy được trên Android nói chung nhưng **không được Amazon liệt kê**; rủi ro chính sách | ⚠️ chỉ có mẫu cộng đồng |
| **Analytics** | GameAnalytics ✅ | GameAnalytics `UNVERIFIED` trên Fire | GameAnalytics (OAID) ✅ / Huawei Analytics Kit tuỳ chọn |
| **Verify server** | Store collection API | RVS | HMS IAP verify |
| **Ràng buộc engine** | Godot 4.5+ nếu dùng GameAnalytics | như Windows | như Windows |

---

## 7. Khuyến nghị thứ tự thi công (đề xuất, không phải quyết định)

Lý do xếp thứ tự: **giảm rủi ro học được sớm nhất với chi phí thấp nhất**.

| Bước | Việc | Vì sao trước |
|---|---|---|
| 1 | Chốt **Godot ≥ 4.5** và dựng **interface GDScript** (mua/khôi phục/consume/subscription) | Mọi adapter phải khớp interface này; đổi sau rất đắt |
| 2 | **Adapter Amazon** (Appstore SDK) + App Tester | Test được ngay trên máy dev, không cần chờ store duyệt |
| 3 | **Adapter HMS IAP** | Sandbox tốt; cùng dạng Android plugin v2 với Amazon ⇒ tái dùng kỹ năng |
| 4 | **Analytics** (một nguồn) | Cần trước soft launch để có D1/D7 |
| 5 | **Petal Ads** | Sau khi có IAP ổn định; ads là doanh thu phụ (D8a) |
| 6 | **GDExtension Windows** + đóng gói MSIX | Đắt và **chỉ test được qua submission** ⇒ làm cuối, và phải chấp nhận vòng lặp chậm |
| — | Verify server | Song song từ bước 2, nhưng có thể để nợ nếu MVP |

**Không đưa số giờ vào bảng này** — không có số đo, và ước lượng của người viết spec không phải dữ liệu. Kích thước tương đối theo thứ tự trên: Amazon < Huawei < Windows.

---

## 8. Rủi ro mới phát hiện (đưa vào sổ chung)

| # | Rủi ro | Mức | Xử lý |
|---|---|---|---|
| **G-R1** | **Không có plugin chính thức cho cả 3 store** ⇒ 3 adapter là code native phải tự viết, không phải "cấu hình" | **Cao** | Đưa vào Gate-5 như work-item có chủ; verifier `ef6b75ef` kiểm riêng từng adapter |
| **G-R2** | **Appstore Billing Compatibility SDK hết hỗ trợ 15/09/2026** ⇒ mọi hướng dẫn/plugin cũ trên internet (dùng `com.amazon.device.iap.billingclient.api`) đã lỗi thời | **Cao** | Chỉ dùng **Appstore SDK native**; ghi rõ trong prompt Godot-coder để không copy nhầm tutorial |
| **G-R3** | **Windows IAP chỉ test được qua submission** (dev license không phải retail license) | **Cao** | Lên kế hoạch một bản flight/private audience sớm để test; đừng để tới cuối |
| **G-R4** | GameAnalytics yêu cầu **Godot 4.5+**; AdMob plugin cũng 4.5+ ⇒ **engine bị ghim** | Trung bình | Chốt phiên bản engine ở Gate-4/5 và ghim cùng plugin |
| **G-R5** | GameAnalytics trên **Fire OS** chưa có tuyên bố hỗ trợ | Trung bình | Test sớm trên Fire thật; nếu fail, phương án B = analytics tự viết gửi HTTP |
| **G-R6** | Petal Ads chỉ có mẫu cộng đồng (repo cá nhân) | Trung bình | Không đưa mẫu vào production nguyên trạng; review code + tự viết theo SDK doc chính chủ `ads-prime` |
| **G-R7** | HMS Toolkit decommission 30/12/2026 | Thấp | Không phụ thuộc Toolkit trong pipeline |

---

## 9. Bàn giao

**Cho session Godot-coder (khi mở):** dùng §6 làm checklist adapter, §1.2 làm lý do không tìm plugin Amazon, §3.1 làm ràng buộc bắt buộc của Windows (MSIX + không elevated + không receipt client).

**Cho verifier `ef6b75ef`:** 3 điểm kiểm độc lập — ① adapter có đúng interface chung không; ② có dùng nhầm SDK đã EOL (Billing Compatibility) không; ③ có tự bịa receipt/verify ở client thay vì gọi server không.

**Cho director / Gate-4–5:** G-R1 và G-R3 là hai mục **ảnh hưởng trực tiếp scope MVP** và cần được ghi vào sổ trước khi ước lượng khối lượng.
