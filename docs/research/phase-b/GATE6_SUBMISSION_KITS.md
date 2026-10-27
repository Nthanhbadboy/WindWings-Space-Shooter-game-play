# GATE-6 SUBMISSION KITS — Rating questionnaire + Privacy/Data-safety form × 3 store


> 🔴 **CẢNH BÁO KÊNH AMAZON (bổ sung 2026-10-27, sau khi tài liệu này hoàn tất):** từ **08/10/2026** Amazon đã thay dòng Fire tablet bằng **Alexa Tablet (Android 16 + Google Play)**. Theo FAQ chính chủ Amazon, app cho Alexa Tablet **phải nộp qua Google Play** (trừ Amazon Kids+), **APS không khả dụng** (dùng AdMob), và doanh số/thanh toán/thuế nằm ở **Play Console**. ⇒ Mọi nội dung "Amazon" trong tài liệu này chỉ còn áp dụng cho **Fire TV/Vega, Fire OS installed base, và Amazon Kids+** — **KHÔNG** áp dụng cho tablet Amazon mới. Xem [`ALERT_AMAZON_CHANNEL_CHANGE_2026-10-27.md`](./ALERT_AMAZON_CHANNEL_CHANGE_2026-10-27.md) [S116–S121]. Việc này ảnh hưởng **D1/D10/D9a** và đang chờ user chốt phương án A/B/C/D.

> **Vai:** commercial-researcher (`arena/46e50499`). **Ngày tra cứu toàn bộ:** **2026-10-27** (mỗi URL ghi kèm ngày truy cập; ngày "last updated" của trang ghi riêng nếu có).
> **Trạng thái:** research-only. Không đăng ký tài khoản, không mở console, không nộp gì, không SDK/publish/merge. **Không tự chuyển gate** — đây là *hồ sơ chuẩn bị* để director/user duyệt ở Gate-6.
> **Nhãn bằng chứng:** `STATIC_CONFIRMED` = đọc trực tiếp tài liệu chính chủ (đã fetch) hoặc file spec trong repo · `INFERRED` = suy luận có nêu giả định · `UNKNOWN` = không tìm được nguồn công khai · `RUNTIME_UNVERIFIED` = chưa chạy thực tế · `CONFLICTING` = nguồn mâu thuẫn.
> **Nguồn:** `[Sxx]` trỏ [SOURCES.md](./SOURCES.md). Nguồn mới của tài liệu này: **S79–S88** (đã bổ sung vào SOURCES.md cùng ngày).

---

## §0. PHẠM VI ĐÃ CHỐT (đồng bộ board PR12 lần 150 + `DECISIONS_RESOLVED.md` lần 144/145/148)

> Khối này **thay thế** mọi chỗ trong tài liệu còn ngụ ý "Fire tablet trước" hoặc "chờ user chốt G9–G17". Các quyết định dưới đây do **director quyết theo ủy quyền**, **user có quyền bác bỏ** — nếu bác, phần tương ứng phải làm lại.

| Quyết định | Chốt | Ảnh hưởng trực tiếp tới tài liệu này |
|---|---|---|
| **G13** | **Giữ 3 store lúc launch** (MS · Amazon · Huawei); Amazon thu về **Fire TV / Vega / Fire-OS legacy / Kids+**; **Google Play = follow-up ngay sau launch** (store thứ 4) | Kit/queue/giá làm cho **3 store cũ**; phần Google Play là **BACKLOG-Post-launch**, không làm bây giờ |
| **G14** | **"Fire TV + Fire-OS legacy trước"** (thay D10a "Fire tablet trước"); tablet Amazon mới đi Google Play | **Fire TV = remote/D-pad, không cảm ứng** ⇒ UI và luồng IAP phải dùng điều hướng phím |
| **G15** | **Không tích hợp APS** lúc launch | Không có mục APS trong danh sách SDK phải làm; ads Fire TV quyết ở gate tương ứng |
| **G16** | **Không lập mô hình doanh thu ads** — chỉ đo eCPM thật ở soft-launch | Không có bảng "doanh thu ads kỳ vọng"; chỉ có công thức |
| **G17** | **Giữ D2a** — không vào đại lục Trung Quốc | Huawei = AppGallery **ngoài** đại lục; TQ chỉ là backlog có điều kiện |
| **G9** | Premium bundle **$3,99** (không-ads + auto-grant rewarded + QoL) — không bán "remove ads" thuần | SKU chính là Premium |
| **G10** | **Non-renewing pass consumable** — không dùng subscription API store | Bớt 1 API surface; tránh khoá giá MS + consent auto-renew Huawei |
| **G11** | Battle pass **$4,99** launch, chu kỳ **30 ngày**; lên $5,99 chỉ sau khi có buy-rate thật | Bảng giá P5 |
| **G12** | Premium Windows **$9,99**; bundle PC $14,99 tuỳ chọn sau launch | Bảng giá P6/P7 |

## 0. Kết luận điều hành (đọc 30 giây)

| Store | Form bắt buộc để được publish | Chặn publish nếu thiếu? | Ai/cái gì sinh ra nó |
|---|---|---|---|
| **Microsoft Store** | ① IARC questionnaire (Age ratings) ② Privacy policy **URL** (nếu app có thu thập/tham chiếu dữ liệu cá nhân) ③ (Company account + bán ở EU) EU-DSA trader/KYBC verification | **Có** — submission bị đánh `Incomplete`, không qua certification | Partner Center, 6 tab submission [S74] |
| **Amazon Appstore** | ① Target audience (3 nhóm, kích hoạt COPPA policy) ② Content rating questionnaire ③ **User data privacy questionnaire (privacy labels)** — bắt buộc với **mọi app mới & mọi update từ Q2/2025** | **Có** — "You can no longer publish a new app or update an existing app if the privacy questionnaire is incomplete" [S66] | Developer Console → Target Your App [S69] |
| **Huawei AppGallery** | ① Content rating questionnaire (bắt buộc) ② Privacy policy URL + link in-app ③ **Privacy tags** (khai dữ liệu + SDK bên thứ 3) | **Có** — rating thiếu/khai sai → app bị từ chối hoặc gỡ; privacy tags thiếu → release bị reject (nguồn bên thứ 3 cho phần "reject", xem §3.3) | AGC → Distribute → Release app [S86][S85] |

**Ba điểm khác biệt quan trọng nhất so với Google Play** (dễ làm sai vì quen Play):
1. **Không store nào dùng "Data safety" của Google.** Amazon có privacy labels (gần giống), Huawei có privacy tags (gần giống), **Microsoft không có form khai dữ liệu** — chỉ có privacy policy URL + capability trong manifest (kết luận từ **vắng mặt** form trong tài liệu submission chính chủ đã đọc: nhãn `INFERRED`, xem §2.4).
2. **Amazon KHÔNG dùng IARC** — Amazon tự ấn định maturity rating từ questionnaire riêng [S69][S70]; **Microsoft và Huawei dùng IARC/đối tác** (Huawei: rating một số khu vực do "third-party rating agencies" của Huawei cấp) [S80][S88].
3. **Khai third-party SDK là bắt buộc ở Amazon + Huawei**, không chỉ dữ liệu của mình [S66][S87]. ⇒ **Danh sách SDK phải chốt trước khi nộp** — đây là phụ thuộc cứng vào Gate-4 (D11).

---

## 1. Hồ sơ dữ liệu — nguồn sự thật duy nhất (dùng chung cho cả 3 form)

Mọi form dưới đây đều hỏi cùng một tập câu hỏi gốc. Trả lời **một lần** ở đây, rồi suy ra 3 form.

### 1.1 Dữ liệu game sẽ thu thập — theo phạm vi MVP

Căn cứ phạm vi: `docs/spec/GAMEPLAY.md` §7.2 — **"Không có trong MVP: Arena, PvP, Challenge, Survival, TryPlayer, event, VIP, premium, gift code, drone, tech, talent"** ⇒ MVP **không có PvP, không ranking liên server, không chat, không UGC** → **không có "user-to-user communication"** trên mọi form. `STATIC_CONFIRMED`

| Nhóm (theo taxonomy Amazon) | Dữ liệu | MVP có? | Nguồn sinh ra | Nhãn |
|---|---|---|---|---|
| Device or other IDs | Advertising ID (Android/Amazon) · **OAID** (Huawei) · IP | **Có** | Ads SDK (rewarded) + analytics | `INFERRED` — phụ thuộc SDK chốt ở Gate-4 (D11) |
| Device or other IDs | Device model, OS version, ngôn ngữ, màn hình | **Có** | Analytics/crash | `INFERRED` |
| App info and performance | Crash logs, diagnostics (fps, load time) | **Có** | Crash/analytics SDK | `INFERRED` |
| App activity | App interactions, tiến trình chơi, level, item | **Có** | Analytics + save local | `INFERRED` |
| Purchase history | Lịch sử IAP (consumable/non-consumable) | **Có** | Store IAP (MS/Amazon/HMS) — store là bên xử lý thanh toán, **dev không thấy số thẻ** | `STATIC_CONFIRMED` (cơ chế) |
| Financial info | Payment info | **Không** | Store lo toàn bộ; theo Amazon: "payment information entered outside your app ⇒ not collected" [S66] | `STATIC_CONFIRMED` |
| User Info (name, email, user ID) | — | **Không ở MVP** | Không có account bắt buộc trong MVP | `INFERRED` — cần user xác nhận (câu hỏi G5) |
| Location | — | **Không** | Không dùng GPS/LBS | `INFERRED` |
| UGC / Messages | — | **Không** | Không chat (MVP) | `STATIC_CONFIRMED` (phạm vi MVP) |
| Contacts / Photos / Health | — | **Không** | — | `STATIC_CONFIRMED` |

**Nếu mở full launch (có account + cloud save + Arena/PvP như game gốc):** thêm `User Info → User IDs`, `User Info → Name (nickname hiển thị)`, `App activity` mở rộng, và với Amazon sẽ rơi vào mục **"User Generated Content or User to User Communication"** nếu thêm chat/guild → phải khai lại toàn bộ form. Ghi nhận: game gốc **có** account + cloud save + PvP + rankings (`Board_AccountSettings`, `Board_LinkAccount`, `Board_PvP`, `Popup_Ban`) `STATIC_CONFIRMED` — nên đây là **form sẽ phải làm lại**, không phải form một lần.

### 1.2 Câu hỏi lõi — câu trả lời chuẩn bị sẵn

| Câu hỏi xuất hiện ở cả 3 store | Trả lời chuẩn bị | Ghi chú |
|---|---|---|
| App có thu thập dữ liệu người dùng không? | **Có** (advertising ID, diagnostics, app activity) | Không thể trả "No" nếu có ads SDK hoặc analytics — khai sai = rủi ro gỡ app |
| Có chuyển dữ liệu cho bên thứ ba không? | **Có** — cho ad network + analytics provider | "Third-party transfer" ≠ "service provider xử lý thay dev" — Amazon định nghĩa rõ [S66]; **ad network là bên thứ ba**, analytics thường là service provider → khai khác nhau |
| Có bán dữ liệu không? | **Không** | Huawei §7.13 cấm bán `STATIC_CONFIRMED` [S71] |
| Có dùng cho quảng cáo cá nhân hoá không? | **Có, có consent** | Huawei bắt buộc opt-out personalized ads `STATIC_CONFIRMED` [S71]; COPPA 2025 cần opt-in riêng nếu có trẻ em [S63] |
| Có tài khoản/đăng nhập không? | **MVP: không** · full: có | Ảnh hưởng trực tiếp số mục phải khai |
| Trẻ em có dùng được không? | **Cần user quyết (G1)** | Đây là đòn bẩy lớn nhất của cả Gate-6 — xem §4 |

---

## 2. MICROSOFT STORE — kit

### 2.1 Trình tự nộp (6 tab, chính chủ)

`STATIC_CONFIRMED` [S74] — Partner Center → Start Submission, 6 tab: **Pricing and Availability** → **Properties** (category, system requirements) → **Age Ratings** → **Packages** → **Store Listings** → **Submission options** (optional). Thiếu mục nào → trạng thái **`Incomplete`**, không nộp được. Certification tối đa **3 business days**, hiển thị ~15 phút.

### 2.2 Age rating — IARC

| Điểm | Nội dung | Nguồn |
|---|---|---|
| Cơ chế | Trả lời **IARC questionnaire** ngay trong tab Age Ratings; IARC sinh rating cho từng khu vực | [S68][S80] |
| Bắt buộc | **Mọi sản phẩm** tạo qua Partner Center, kể cả khi đã có rating từ board khác | [S79] "You're required to take the IARC ratings questionnaire for **ALL** products created via Partner Center" |
| Cấm | **"Placeholder answers shouldn't be submitted."** Khai sai/khai tạm = vi phạm | [S79] |
| Tái dùng | Có IARC Certificate ID / **GRID** từ store khác → nhập vào "Import ratings" thay vì làm lại | [S79][S80] |
| Dùng lại | Rating đã gán sẽ **dùng cho mọi update sau**; đổi nội dung → phải **Edit** làm lại | [S80] |
| Chia sẻ dữ liệu | Khi làm questionnaire, **tên publisher + email được chia sẻ với IARC**; IARC gửi email xác nhận rating khi app publish | [S80] |
| Giới hạn | IARC chỉ có giá trị cho **digital distribution**; bán đĩa phải xin rating board | [S79] |
| Add-on | Add-on có nội dung khác/khắt khe hơn app cha → phải làm questionnaire riêng cho add-on | [S80] |

**Việc phải làm:** chuẩn bị trước bộ câu trả lời IARC (bạo lực hoạt hình, máu me, ngôn từ, chất gây nghiện, cờ bạc, mua trong app, quảng cáo, chia sẻ vị trí, mua sắm, UGC). **Không** dùng ratings của game gốc WindWings — đây là sản phẩm mới, nội dung mới.

### 2.3 Privacy — policy §10.5

`STATIC_CONFIRMED` [S81]: nếu app "accesses, collects or transmits Personal Information, **or if otherwise required by law**" → **phải có privacy policy**; cung cấp cho user bằng cách **nhập privacy policy URL trong Partner Center**; policy phải nêu: dữ liệu nào được truy cập/thu thập/truyền, dùng/lưu/bảo vệ thế nào, **loại bên nhận** dữ liệu; phải cập nhật khi thêm tính năng.

Thực tế vận hành: Partner Center tự phát hiện capability trong package và có thể **buộc** trường này thành bắt buộc [S81 + Q&A cộng đồng — `INFERRED` cho phần "tự phát hiện"].

### 2.4 Không có "data safety form" — giới hạn của kết luận

Đã rà: danh sách 6 tab submission [S74], trang age ratings [S80], policy 7.20 §10.5 [S81] — **không** thấy form khai dữ liệu kiểu Google Play. Nhãn: `INFERRED` (kết luận từ **vắng mặt bằng chứng** trong tài liệu chính chủ đã đọc, không phải tuyên bố "chắc chắn không tồn tại"). Hệ quả thực dụng: **nghĩa vụ khai dữ liệu của Microsoft nằm ở privacy policy + manifest capability**, nên privacy policy phải viết đủ chi tiết (không được viết chung chung).

### 2.5 EU DSA trader / KYBC

`STATIC_CONFIRMED` [S82]: yêu cầu **"Know Your Business Customer"** gắn với EU DSA — dev được phân loại **"Trader"** phải nộp **DUNS ID hoặc một loại giấy tờ xác minh doanh nghiệp**; kiểm tra trạng thái tại **Partner Center → Account Settings → Legal Info → tab Developer → "EU Digital Service Act compliance status"**. Trang này nói về **company account**.

Rủi ro cho ta: D5 đang là **Individual** ⇒ hai khả năng: (a) Individual không thuộc diện KYBC → chỉ cần khai trader status; (b) bị yêu cầu xác minh → phải có DUNS. → `UNKNOWN` cho nhánh Individual; **kiểm tra tại console trước khi nộp** (không tốn chi phí, chỉ là một trường trạng thái). Trên PDP sẽ hiện dòng "This seller has certified…" [S82].

### 2.6 Checklist nộp MS

- [ ] Privacy policy **URL công khai, https, không 404**, có tên app, nêu loại bên nhận dữ liệu [S81]
- [ ] Trả lời IARC questionnaire đầy đủ (không placeholder) — hoặc nhập IARC ID/GRID [S79][S80]
- [ ] Xác nhận **EU DSA compliance status** ở Legal info [S82]
- [ ] Manifest: khai đúng capability (mạng, file) — capability thừa làm tăng nghĩa vụ privacy [S81]
- [ ] Store listing EN (+VI nếu mở VN) — dùng `STORE_ASSETS_AND_LISTING_DRAFT.md` (nhánh `a5a74747`)
- [ ] Ghi chú certification (submission options): nêu Windows không có ads (D3b) để reviewer không tìm ad SDK

---

## 3. AMAZON APPSTORE — kit

> **Phạm vi kit này (theo G14):** áp cho **Fire TV / Vega / Fire-OS legacy**, **không** áp cho **Alexa Tablet** (đi Google Play — BACKLOG-Post-launch). Vì Fire TV **không có cảm ứng**, mọi ảnh chụp màn hình/asset dùng cho review phải là **ảnh UI điều hướng bằng remote**, và danh mục thiết bị khi khai "Target Your App" phải chọn **Fire TV**, không chọn tablet.


### 3.1 Màn "Target Your App" có 5 phần

`STATIC_CONFIRMED` [S69]: **Supported devices** · **Availability** · **Target audience** · **Content rating** · **User data privacy**. (Đây là màn thứ 2 trong 4 bước: Upload → Target → Details → Review/Submit.)

### 3.2 Target audience — quyết định kích hoạt COPPA

`STATIC_CONFIRMED` [S69] — 3 lựa chọn và hệ quả pháp lý:

| Lựa chọn | Hệ quả |
|---|---|
| App dành cho trẻ em (0–12, hoặc 13–15 ở một số marketplace) | **Bắt buộc** tuân thủ **Child-Directed App (COPPA) Policy** [S83] |
| Mixed audience, có trẻ em | **Bắt buộc** COPPA policy, **trừ khi** xác nhận trẻ em không dùng app |
| Không dành cho trẻ em (chỉ 16+) | Chỉ cần tuân **Content Policy Guidelines** chung [S70] |

Amazon khuyến nghị: "only select age groups for your app's target audience if you have confirmed your app is appropriate for those audiences" — **không** chọn bừa để được reach rộng [S69].

### 3.3 Content rating (Amazon tự ấn định — KHÔNG phải IARC)

`STATIC_CONFIRMED` [S69]. Amazon hỏi 2 nhóm:

**Subject Matter:** Violence · **Cartoon Violence** · Drugs · Nudity · Sex · Intolerance · Profanity · Academic
**Additional Information:** Account creation or other personal information collected · **Advertisements** · Gambling · Location detection/Location-Based Services · **User Generated Content or User to User Communication**

Cơ chế & ràng buộc:
- Amazon **gán summary maturity rating** (All Ages / Guidance Suggested / Mature / Adult) dựa trên khai của dev **và review của Amazon**; Amazon **giữ quyền tự ấn định** [S69].
- **Rating chỉ đổi được khi nộp app file mới** ("Content ratings for published apps can only be changed when submitting a new app file") [S69] ⇒ khai sai = phải nộp version mới mới sửa được.
- Rủi ro thực tế: phần lớn app fail review vì **content policy**, không phải kỹ thuật; Amazon có quyền suppress app **hồi tố** [S69][S70].

**Câu trả lời dự kiến của WindWings** (chờ art review xác nhận):
| Mục | Đáp án dự kiến | Nhãn |
|---|---|---|
| Violence | **Có** (bắn hạ tàu/địch) | `STATIC_CONFIRMED` (thể loại) |
| Cartoon Violence | **Có** — phong cách hoạt hình, không máu me | `INFERRED` — cần soi art thật trước khi khai |
| Advertisements | **Có** (rewarded, D8a) | `STATIC_CONFIRMED` (D8a) |
| Account creation / personal info | **MVP: Không** (không account) — nhưng app *có thu thập* ad ID ⇒ khai ở privacy labels, không phải mục này | `INFERRED` |
| Gambling | **Không** (D7a: không loot box trả phí) | `STATIC_CONFIRMED` (D7a) |
| Location | **Không** | `INFERRED` |
| UGC / user-to-user | **Không** (MVP không PvP/chat) | `STATIC_CONFIRMED` (spec §7.2) |
| Academic | **Không** | `STATIC_CONFIRMED` |

### 3.4 User data privacy (privacy labels) — form chặn publish

`STATIC_CONFIRMED` [S66]. Mốc thời gian chính thức:
- **04/2023** — mục "User data privacy" xuất hiện trong Target Your App.
- **11/2023** — nhãn hiển thị công khai trên app detail page; chưa khai → hiện "Privacy information not provided by the developer".
- **Q2/2025** — **bắt buộc**: "All new apps and app updates are required to have a completed privacy questionnaire. **You can no longer publish a new app or update an existing app if the privacy questionnaire is incomplete or has unaddressed issues.**"

Quy tắc khai:
- Phải khai dữ liệu gắn với **một cá nhân** ("associated with an individual user"); dữ liệu **anonymous không phải khai**.
- **Phải khai cả dữ liệu do third-party plugin/SDK thu thập** ("Any data collection or data transfer done by third-party code must be indicated").
- "Third-party transfer" **không** tính: (i) service provider xử lý thay dev, (ii) mục đích pháp lý, (iii) hành động do user chủ động/đã consent rõ ràng.
- Thanh toán do store xử lý, dev không thấy thông tin thẻ ⇒ **không khai** mục payment [S66].
- 3 cách khai: trong lúc submit · live metadata update · màn User Data Privacy (upload Excel hàng loạt).

**Data types liên quan tới ta** (trích bảng chính chủ [S66]): `Device or other IDs` (device/advertising ID, IP) · `App info and performance` (Crash logs, Diagnostics) · `App activity` (App interactions, Other actions) · `Purchase history`.
**Purposes** cần chọn: `Analytics` · `Developer Advertising or Marketing` · **`Third-party Advertising or Marketing`** (nếu ad network là bên thứ ba) · `Fraud Prevention, Security & Compliance` · `App functionality`.
Bắt buộc kèm theo: **privacy policy** nếu thu thập dữ liệu gắn cá nhân (theo Privacy and Security Policy [S84]).

### 3.5 Age verification API (Mỹ, theo tiểu bang)

`STATIC_CONFIRMED` [S67]: **GetUserAgeData API** live **01/01/2026** cho Texas/Utah/Louisiana; Amazon coi đây là "significant change" ⇒ cần kiểm tra xem app có thuộc diện phải gọi API/khai tuổi không. Nếu phát hành ở Mỹ → đưa vào Gate-7 (release-readiness) kiểm lại.

### 3.6 Checklist nộp Amazon

- [ ] Target audience đã chọn theo **quyết định G1** (không chọn bừa)
- [ ] Content rating questionnaire đầy đủ (nhớ: đổi rating = phải nộp app file mới)
- [ ] Privacy labels: khai **cả SDK bên thứ 3**, phân biệt ad network (third-party) vs analytics (service provider)
- [ ] Privacy policy URL hợp lệ (nếu thu thập dữ liệu cá nhân) [S84]
- [ ] Bỏ **Nhật Bản** khỏi phạm vi IAP (JP IAP đã dừng 20/02/2025) [S16]
- [ ] Chỉ target **Fire tablet** (D10a); Fire TV/Vega để sau
- [ ] Kiểm tra diện áp dụng GetUserAgeData nếu bán ở TX/UT/LA [S67]

---

## 4. HUAWEI APPGALLERY — kit

### 4.1 Content rating — bắt buộc, có thể bị "Rating rejected"

`STATIC_CONFIRMED` [S86][S54]:
- Luồng: **AGC → Distribute → Release app → Draft → Content rating → Set → Start questionnaire → trả lời → Verify** → hệ thống trả **"youngest age group applicable"**.
- Dev được **chọn rating cao hơn** kết quả (ví dụ kết quả ≤16+ nhưng muốn 18+ thì chọn 18+).
- Nếu kết quả là **"Rating rejected"** → phải xem lý do, sửa nội dung, upload lại.
- **Cảnh báo chính thức:** "False statements about your app content may lead to app removal or freezing."
- Review Guidelines §1.10: phải chọn rating theo nội dung và **cập nhật khi nội dung thay đổi** [S71-doc 50104-01].
- Thang điểm: quốc tế **3+/7+/12+/16+/18+**; Trung Quốc đại lục **3+/8+/A12/A14/A16/A18**; **gambling/loot box = 18+** và 18+ có thể **không phát hành được ở đại lục** [S54]. (Ta đã loại đại lục — D2a — và không có loot box trả phí — D7a ⇒ không chạm ngưỡng 18+ vì lý do này.)

### 4.2 Privacy policy — 2 nơi, cùng một nội dung

`STATIC_CONFIRMED` [S71]:
- **§7.1:** app phải có **link in-app dễ tìm** tới privacy policy, đồng thời **nộp link đó trong AGC** để hiển thị ở app information; cả hai link phải dễ truy cập.
- **§7.2:** link phải dẫn tới policy nêu **mục đích, phương thức, phạm vi** thu thập & sử dụng dữ liệu cá nhân, **bao gồm bên được uỷ thác và third-party code/plugin nhúng trong app**.
- **§7.5:** consent trước khi thu thập/xử lý; **§7.11** bảo mật (HTTPS…); **§7.12** nếu chia sẻ dữ liệu phải nêu **dữ liệu nào, cho ai, mục đích**; **§7.13** **cấm bán dữ liệu cá nhân**; **§7.15** cấm dùng dữ liệu nhạy cảm (call log, SMS, sinh trắc, sức khoẻ, **vị trí**) cho quảng cáo/cải tiến ngoài chức năng chính.

⇒ Với ta: **advertising ID/OAID phải được khai**, có consent, có opt-out personalized ads; **không** đụng vị trí.

### 4.3 Privacy tags (form khai dữ liệu của Huawei)

`STATIC_CONFIRMED` (doc chính chủ, bản tiếng Trung) [S85]:
- Mục đích: để user xem app dùng dữ liệu gì **trước khi tải**.
- **Đường dẫn khai:** Developer Center → **分发 (Distribute) → 版本信息 (Release info) → 隐私标签信息录入 (Privacy tag info entry)**.
- Bắt đầu hiển thị **11/2021**; **từ 28/07/2022** app mới/update **có thu thập hoặc xử lý thông tin cá nhân** (hoặc tích hợp SDK/component làm việc đó) **phải** khai privacy tags — nguồn bên thứ 3 (OMA) cho mốc 28/07/2022: `BT3`, xem ghi chú.
- Form hỏi: **"Collect personal data?" Yes/No** → nếu **Yes** phải khai **từng loại dữ liệu + mục đích sử dụng**, bao gồm dữ liệu do **third-party component** thu thập [S85 + hướng dẫn AGC].
- Hệ quả nếu khai thiếu/sai: release bị từ chối/reject (nguồn bên thứ 3 `BT3`; tài liệu chính chủ chỉ nói chung là phải khai đầy đủ, chính xác).

`STATIC_CONFIRMED` [S87] — FAQ bảo vệ thông tin cá nhân: nếu chia sẻ dữ liệu với **third-party SDK** phải nêu **danh tính + liên hệ bên thứ ba, mục đích, phương thức, phạm vi, loại dữ liệu**, và **lấy consent trước**; không được gửi dữ liệu (device ID, lịch sử dùng…) cho SDK bên thứ ba khi chưa thông báo + consent.

### 4.4 Minor protection — chỉ bắt buộc nếu audience có trẻ em

`STATIC_CONFIRMED` [S73]: nếu app dành cho/bao gồm trẻ vị thành niên → toàn bộ nội dung phải phù hợp; nếu thu thập dữ liệu nhạy cảm của trẻ → theo luật bảo vệ trẻ; **§8.12** phải có **chính sách riêng về quyền riêng tư trẻ em**; **§8.13** phải có **sự đồng ý của cha mẹ/người giám hộ** trước khi thu thập dữ liệu của trẻ; **§8.11** ads cho trẻ phải theo luật/tiêu chuẩn ngành.

### 4.5 Rating do bên thứ ba cấp — dữ liệu gì bị chia sẻ

`STATIC_CONFIRMED` [S88] (AGC Service Agreement §3.10): ở một số khu vực, chức năng rating do **third-party rating agencies do Huawei chọn** cung cấp; dev **đồng ý** cung cấp cho họ: **tên công ty (hoặc tên cá nhân), chi tiết questionnaire, thông tin app, gói cài đặt, email, bản quyền app, số 版号, giấy phép kinh doanh**. Huawei có quyền **điều chỉnh hệ thống rating và tiêu chí tuổi** của mình.

### 4.6 Checklist nộp Huawei

- [ ] Content rating questionnaire (AGC Draft) — trả lời đúng, không khai sai
- [ ] Privacy policy: **URL trong AGC** + **link in-app** (cùng nội dung) [S71]
- [ ] Privacy tags: khai **từng data type + purpose + third-party SDK** [S85][S87]
- [ ] Consent flow: hiển thị policy + consent **trước** khi SDK khởi tạo (không được init ads/analytics trước consent) [S87]
- [ ] Opt-out personalized ads (bắt buộc) [S71]
- [ ] Nếu audience có trẻ: policy trẻ em riêng + parental consent [S73]
- [ ] Phạm vi phát hành: **ngoài đại lục** (D2a) — đại lục cần 版号 qua NPH [S39]

---

## 5. Ma trận "một câu hỏi — ba câu trả lời"

| Câu hỏi | Microsoft | Amazon | Huawei |
|---|---|---|---|
| Rating do ai cấp? | **IARC** (qua Partner Center) [S80] | **Amazon tự ấn định** [S69] | **Huawei** (+ đối tác ở một số khu vực) [S88] |
| Có dùng IARC ID chung được không? | Có — nhập GRID/Certificate ID [S79] | **Không** — questionnaire riêng | Có thể dùng chung IARC (khuyến nghị, cần xác minh trong console: `UNKNOWN`) |
| Form khai dữ liệu tên gì? | **Không có** — chỉ privacy URL [S81] | **Privacy labels / User data privacy** [S66] | **Privacy tags** [S85] |
| Khai dữ liệu của SDK bên thứ 3? | Không có form ⇒ nằm trong privacy policy | **Bắt buộc** [S66] | **Bắt buộc** [S85][S87] |
| Thiếu form thì sao? | Submission `Incomplete`, fail cert [S74] | **Không publish/update được** (từ Q2/2025) [S66] | Bị reject/gỡ (rating sai: gỡ hoặc freeze) [S86] |
| Đổi rating sau khi live? | Edit questionnaire, dùng từ update sau [S80] | **Chỉ khi nộp app file mới** [S69] | Làm lại questionnaire khi nội dung đổi [S71-doc 50101 §1.10] |
| Yêu cầu EU DSA | Trader/KYBC ở Legal info (company: DUNS/giấy tờ) [S82] | `UNKNOWN` — không thấy trang chính chủ riêng | `UNKNOWN` — không thấy trang chính chủ riêng |

> Ghi chú có chủ đích: hai ô `UNKNOWN` ở hàng DSA là **khoảng trống thật** — chưa tìm được trang chính chủ của Amazon/Huawei về trader status. Không suy diễn từ Apple/Google. Cần kiểm tra trong console khi onboard (Gate-7), không chặn Gate-6.

---

## 6. Phụ thuộc & rủi ro

| # | Rủi ro | Mức | Xử lý |
|---|---|---|---|
| R1 | **Danh sách SDK chưa chốt** (D11 để Gate-4) ⇒ không thể khai privacy labels/tags cuối cùng | **Cao** | Gate-6 nộp **khung khai báo** + quy trình; chốt số liệu sau Gate-4. Ghi rõ đây là chặn mềm, không phải chặn cứng nếu chưa nộp |
| R2 | **Privacy policy URL chưa có** (cần domain/hosting) | Cao | Cần user quyết (G2). Không được dùng link tạm (MS: URL phải https, không 404 [S81]) |
| R3 | **Khai sai** (thừa/thiếu dữ liệu) | Cao | Dùng §1 làm nguồn duy nhất; review chéo với session verifier `ef6b75ef` trước khi submit |
| R4 | **Audience trẻ em** kích hoạt COPPA + Huawei minor + COPPA-2025 opt-in ads | Cao | Quyết định G1 — xem §7 |
| R5 | Amazon đổi rating chỉ khi nộp file mới | Trung bình | Khai đúng ngay lần đầu; nếu sai, gộp vào bản update kế tiếp |
| R6 | Huawei rating "rejected" do nội dung | Trung bình | Soi art/âm thanh trước khi khai; tránh yếu tố 18+ (máu me, cờ bạc) |
| R7 | EU DSA trader (địa chỉ/điện thoại công khai) | Trung bình | G3 — liên quan D5 (Individual vs Company) |

---

## 7. Quyết định cần user chốt ở Gate-6 (mới, ngoài D1–D12)

| # | Quyết định | Lựa chọn | Hệ quả | Đề xuất |
|---|---|---|---|---|
| **G1** | **Định vị tuổi** (target audience) | (a) 16+ / không dành cho trẻ · (b) mixed (có trẻ) · (c) dành cho trẻ | (a) tránh COPPA child-directed + Huawei minor + tránh ràng buộc ads trẻ em; (b)(c) phải có parental consent, policy trẻ em riêng, hạn chế ads/IAP, mất một phần doanh thu ads nhưng reach rộng hơn | **(a)** — khớp D7a/D8a và tránh khối nghĩa vụ lớn nhất; gameplay shmup không cần nhắm trẻ em |
| **G2** | **Privacy policy**: nơi host + ai là data controller | (a) trang riêng trên domain dự án · (b) GitHub Pages · (c) dịch vụ tạo policy | (b)(c) rẻ nhưng phải đủ chi tiết (MS đòi nêu "loại bên nhận dữ liệu") | **(a) hoặc (b)** — miễn là https + nội dung đủ |
| **G3** | **EU DSA trader** | (a) khai trader + địa chỉ/điện thoại công khai · (b) khai non-trader | (a) địa chỉ công khai; (b) rủi ro nếu thực tế có doanh thu EU | Cần user quyết (dữ liệu cá nhân) — gộp với D5 |
| **G4** | **Account/cloud save có trong MVP?** | (a) không (local save) · (b) có | (b) thêm User IDs/nickname vào mọi form + phải khai lại khi thêm PvP | **(a)** cho MVP |
| **G5** | **Chốt danh sách SDK khai báo** | chờ Gate-4 | Không chốt được trước Gate-4 | Gate-6 khung → Gate-7 số cuối |

---

## 8. Nguồn mới (đã thêm vào SOURCES.md)

| ID | Nguồn | Nội dung dùng ở đây |
|---|---|---|
| S79 | MS Learn — Age ratings (Game Publishing Guide) [đã đọc] | IARC bắt buộc cho **mọi** sản phẩm; placeholder bị cấm; digital-only |
| S80 | MS Learn — Age ratings for PWA/MSIX [đã đọc] | Chia sẻ tên+email với IARC; import GRID; rating dùng lại; retake khi đổi nội dung |
| S81 | MS Store Policies 7.20 §10.5 [đã đọc] | Privacy policy URL bắt buộc nếu có Personal Information; nội dung policy phải có |
| S82 | MS Learn — Company account verification (EU DSA/KYBC) [đã đọc] | DUNS/giấy tờ doanh nghiệp; Partner Center → Legal info → Developer |
| S83 | Amazon — Child-Directed App (COPPA) Policy [trang chính chủ] | Nghĩa vụ khi audience có trẻ em |
| S84 | Amazon — Privacy and Security Policy [trang chính chủ] | Privacy policy bắt buộc khi thu thập dữ liệu gắn cá nhân |
| S85 | Huawei — AppGallery Privacy Tag Service Description (bản CN) [đã đọc] | Đường dẫn khai privacy tags; Yes/No; phải khai third-party component |
| S86 | Huawei — Releasing an app: Content rating [đã đọc] | Luồng questionnaire → Verify → youngest age; chọn cao hơn; "Rating rejected"; cảnh báo khai sai bị gỡ/freeze |
| S87 | Huawei — FAQs về bảo vệ thông tin cá nhân (FAQ-faq-03) [đã đọc] | Bắt buộc nêu danh tính third-party SDK + consent trước |
| S88 | Huawei — AGC Service Agreement §3.10 [đã đọc] | Rating do đối tác cấp ở một số khu vực; dữ liệu chia sẻ cho rating agency |

**Nguồn bên thứ ba (BT3), dùng có đánh dấu:** mốc "28/07/2022 bắt buộc privacy tags" (OMA/Zendesk) — tài liệu Huawei đọc được xác nhận **có** privacy tags và **có** yêu cầu khai, nhưng không nêu mốc ngày đó.

---

## 8b. KHOẢNG TRỐNG NẾU G13 CHỌN B/C (thêm Google Play)

> **Chỉ là danh sách hạng mục phải NGHIÊN CỨU, không phải yêu cầu đã xác nhận.** Tuyệt đối **không** dùng mục này để nộp gì — mỗi dòng phải được tra từ tài liệu chính chủ Google Play kèm ngày tra cứu rồi mới viết thành kit.
> Lý do tồn tại: kit Amazon trong tài liệu này làm cho **Fire OS / Fire TV**; nếu G13 = **B** (thay Amazon bằng Google Play) hoặc **C** (4 store) thì **kit Amazon không dùng được** cho tablet Amazon mới [S116].

| # | Hạng mục cần tra | Vì sao chặn | Trạng thái |
|---|---|---|---|
| 1 | **Data safety form** — bộ câu hỏi, loại dữ liệu, mục đích, có chia sẻ/không, mã hoá khi truyền | Đây là form **bắt buộc** thay cho privacy labels của Amazon; chưa có bản nháp nào | `UNKNOWN` — chưa tra |
| 2 | **Content rating** — Google Play dùng IARC hay hệ riêng, luồng questionnaire | Nếu dùng IARC thì **tái sử dụng được** phần MS §2.2; nếu không thì phải làm mới | `UNKNOWN` — chưa tra |
| 3 | **Target API level** — mức tối thiểu theo năm, hạn chót | Ảnh hưởng trực tiếp **G6** (ghim phiên bản Godot/Android target) | `UNKNOWN` — chưa tra |
| 4 | **Account deletion requirement** — có bắt buộc cơ chế xoá tài khoản/web link không | Ta **không có account** (G4) ⇒ nếu bắt buộc thì phải khai "không áp dụng" đúng cách | `UNKNOWN` — chưa tra |
| 5 | **Ads declaration** — có mục khai "app chứa quảng cáo" không, ảnh hưởng rating trẻ em | Liên quan D8a (rewarded-only) | `UNKNOWN` — chưa tra |
| 6 | **Revenue share & thuế** — hệ số, ai khấu trừ, hiệp định VN–US có áp dụng | Ảnh hưởng trực tiếp **bảng giá Gate-3** (đang giả định 12% MS / 30% Amazon / ~15% Huawei) | `UNKNOWN` — chưa tra |
| 7 | **Gói nộp & giới hạn** — AAB/APK, kích thước, signing | Ảnh hưởng build pipeline | `UNKNOWN` — chưa tra |

**Điều đã biết chắc (từ nguồn chính chủ Amazon, không phải suy đoán):** mọi hoạt động của app trên Alexa Tablet *"including sales, engagement, statistical data, and payments"* hiển thị ở **Play Console**, **không** ở Amazon; và **APS không khả dụng** [S116].

## 9. Việc tiếp theo của lane (chưa làm trong vòng này)

1. **② Queue Godot** — ma trận plugin IAP/ads (Google Billing × HMS IAP/Ads × Amazon IAP/Billing-Compatibility × AdMob) + analytics SDK trên Fire/HMS. *Đây là đầu vào trực tiếp cho R1 ở trên.*
2. **③ Bảng giá** remove-ads/premium → đề xuất Gate-3.
3. **④** eCPM rewarded Windows + trạng thái ads Fire 2026 (D3b đã chọn **không ads trên Windows** ⇒ hạ ưu tiên; phần Fire vẫn cần cho D8a).
4. **⑤** NPH Trung Quốc để sẵn (hạ ưu tiên — D2a đã loại đại lục).

**Trạng thái gate:** tài liệu này là **đầu vào** cho Gate-6. Không có gate nào được chuyển; user/director giữ quyết định.
