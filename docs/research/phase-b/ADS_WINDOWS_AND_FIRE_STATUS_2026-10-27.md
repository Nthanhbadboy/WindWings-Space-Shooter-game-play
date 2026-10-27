# ADS TRÊN WINDOWS VÀ FIRE — TRẠNG THÁI 2026 (đóng vòng ④)

> **Vai:** commercial-researcher (`arena/46e50499`) · **Ngày tra cứu:** 2026-10-27
> **Câu hỏi gốc của vòng ④:** *eCPM rewarded trên Windows là bao nhiêu, và ads trên Fire năm 2026 còn dùng được không?*
> **Nhãn:** `STATIC_CONFIRMED` (chính chủ, đã fetch) · `BT3` (bên thứ ba) · `VENDOR_CLAIM` (số do chính nhà bán công bố, **không kiểm chứng được**) · `UNVERIFIED` · `CONFLICTING`.
> **Kết luận trước, đọc phần sau để kiểm:** **không có eCPM rewarded chính thức nào cho Windows** — vì Microsoft **không có SDK quảng cáo nào cho game** nữa. Con số duy nhất tồn tại là **$6,20 do một nhà bán SDK tự công bố**, không kiểm chứng được ⇒ **không dùng để lập mô hình**. Trên Fire: Mobile Ad Network đã chết 2021, APS chỉ còn cho Fire TV/Fire tablet và có điều khoản nhường 30% impression.

---

## 1. Windows: Microsoft không bán quảng cáo cho game nữa

**Nguồn chính chủ:** Microsoft Learn — *Monetization for games*, `ms.date: 01/14/2026`, commit "Updated to reflect current advertising models" (14/01/2026). `STATIC_CONFIRMED` [S122]

Nguyên văn 3 cách kiếm tiền Microsoft liệt kê cho game Windows:

1. *"Put your game in the Microsoft Store …"*
2. *"Use APIs in the Windows SDK to create in-game purchases …"*
3. *"**Work with any third party ad provider SDKs, such as Vungle, Rise (Unity), and Pubfinity**, to display ads in your game."*

⇒ Không còn mục "Microsoft Advertising SDK", không còn "Universal Ad Client SDK", không còn "Monetize with Microsoft". **Microsoft chỉ còn bán IAP/add-on**; quảng cáo là **hoàn toàn bên thứ ba**.

**Hệ quả trực tiếp:**

| Câu hỏi | Trả lời |
|---|---|
| Có "eCPM rewarded của Microsoft Store" không? | **Không tồn tại.** Không có ad network của Microsoft ⇒ không có eCPM để công bố |
| Microsoft có công bố benchmark eCPM cho Windows không? | **Không.** Trang chính chủ chỉ liệt kê tên SDK bên thứ ba, không nêu số |
| Vậy con số nào dùng được? | **Không có.** Mọi số "eCPM Windows" trên Internet đều là **seller claim** hoặc suy từ mobile |
| Có phải "Windows không có ads" không? | **Không.** Ads **được phép**, chỉ là phải tự tích hợp SDK bên thứ ba + tự chịu fill rate |

> Điều này **củng cố D3b** ("Windows không ads") bằng một lý do mạnh hơn dự kiến: không phải chỉ vì *quyết định sản phẩm*, mà vì **không có hạ tầng chính chủ**, và các SDK bên thứ ba cho Windows đều **không có trong danh sách plugin Godot** (xem `GATE4_GODOT_COMMERCE_QUEUE.md`).

### 1.1 Con số duy nhất tồn tại — và tại sao không dùng

**MG Ads (Miracle Games)** — `ad.mguwp.net`, SDK quảng cáo **tổng hợp (aggregation)** cho **Windows 10/11 UWP**, tự nhận *"As a Microsoft partner"*, có **rewarded video / interstitial / banner**, và đáng chú ý: case study ghi *"Integrating **GAM** via MG Ads"* (Google Ad Manager) ⇒ nhu cầu ads Windows đi qua **đại lý**, không qua Microsoft. [S123]

| Số họ công bố | Giá trị | Nhãn | Vì sao không dùng |
|---|---|---|---|
| eCPM case study "Snack Short" | **$6,20** | `VENDOR_CLAIM` | Một game, một case, **không nêu geo/format/thời gian đo**, không có bên thứ ba xác nhận [S124] |
| Fill rate | **98–99,5%** | `VENDOR_CLAIM` | Marketing trên blog công ty; fill rate 99%+ trên inventory Windows là con số **không kiểm chứng được** |
| "eCPM tăng 25%, doanh thu +40%" | không có mẫu số | `VENDOR_CLAIM` | Không có số tuyệt đối, không có baseline |

⇒ **Ghi nhận là có tồn tại một lựa chọn ads cho Windows, nhưng không có cơ sở định lượng.** Đưa $6,20 vào bảng giá hoặc vào dự báo doanh thu sẽ là **bịa số có vỏ bọc nguồn**.

### 1.2 Nếu vẫn muốn biết "khoảng nào" — thì phải nói rõ là suy từ mobile

Không có dữ liệu Windows, chỉ có **mobile** (BT3, và các nguồn **mâu thuẫn nhau rõ rệt**):

| Nguồn (BT3) | US rewarded video eCPM | Ghi chú |
|---|---|---|
| MAF.ad (2026) | $15,15 | [S125] |
| Yango Ads Q4/2024 (qua MonetizationGuy) | $19,63 iOS / $16,49 Android | |
| Tenjin × CAS Q2/2024 | $24,39 iOS / $30,25 Android | cao nhất |
| Appodeal Q4/2024 | ~$17,3 iOS / ~$13,2 Android | thấp hơn |
| Udonis | $13,81 iOS / $12,91 Android | |
| Playwire (tier-1 range) | $15–$30 | |
| **Chỉ số theo geo (revenuelab)** | VN nằm nhóm **Tier 3 = 0,05–0,18× US** | ⇒ nếu áp US ~$15 thì VN ~**$0,75–$2,70** |

**Spread giữa các nguồn cho cùng một chỉ số US là ~$13–$30 (>2×).** Đây là **`CONFLICTING`** — và là lý do kỹ thuật để **không lập mô hình doanh thu ads** ở giai đoạn này.

> **Không được** lấy số mobile áp cho Windows. Windows là PC: không có store ad network, không có ATT/Play Services, inventory phần lớn nằm ở web/desktop display giá thấp hơn mobile rewarded rõ rệt. **`UNVERIFIED` — không có nguồn nào đo được.**

### 1.3 Diễn biến cần theo dõi (không phải quyết định)

Microsoft **đã nộp đơn patent** `US 2026/0260258 A1` — *"Contextually Aware Management of Interactive Software Application Access"* (nộp 23/04/2026, công bố 03/09/2026, ưu tiên từ đơn 2023): chèn ads vào **điểm dừng tự nhiên** của game PC/Xbox, người xem nhận "ad credit" 15 phút–1 giờ chơi không ads. `BT3` (nhiều báo lớn: The Verge, IGN, Eurogamer, Tom's Hardware, GamesIndustry.biz) [S132]

**Nhưng:** đây **chỉ là đơn patent**. *"Microsoft has not announced plans to integrate the system into Xbox, Windows 11, Game Pass, or any existing game"* `BT3`. ⇒ **Không tính vào kế hoạch.** Nếu được hiện thực hoá, nó sẽ tạo ra một **ad network chính chủ cho PC** — lúc đó câu hỏi eCPM Windows mới có câu trả lời thật. Ghi nhận để theo dõi, **không suy diễn**.

---

## 2. Fire / Amazon: trạng thái ads 2026

Tóm tắt từ [`ALERT_AMAZON_CHANNEL_CHANGE_2026-10-27.md`](./ALERT_AMAZON_CHANNEL_CHANGE_2026-10-27.md) — chi tiết nguyên văn ở đó.

| Kênh | Trạng thái | Nhãn |
|---|---|---|
| **Amazon Mobile Ad Network** | **Chết** — deprecated 30/09/2021, không nhận app mới | `STATIC_CONFIRMED` [S48] |
| **APS** (Fire TV + Fire tablet) | Sống, nhưng là **header bidding** không phải network tự phục vụ; **10% publisher transaction fee** trên demand Amazon DSP qua TAM; duyệt **một lần, không appeal, không công bố tiêu chí** | `STATIC_CONFIRMED` + `BT3` [S121] |
| **Điều khoản Fire TV** | App Fire TV có ads **≥50.000 giờ/tháng (Mỹ) / ≥30.000 (nước khác)** → sau khi Amazon liên hệ, **buộc** dùng APS + **nhường 30% tổng impression nội địa, Amazon giữ 100% doanh thu phần đó** | `STATIC_CONFIRMED` [S121] |
| **Alexa Tablet** | **APS không có.** Nguyên văn: *"Please use Google AdMob or equivalent"* | `STATIC_CONFIRMED` [S116] |
| AdMob trên Fire OS | **Không** nằm trong danh sách ad SDK tương thích của Amazon (nhắc lại rủi ro đã ghi ở Gate-4) | `STATIC_CONFIRMED` [S46] |

### 2.1 Áp vào D8a (rewarded-only, cap 4–6/ngày)

| Nhánh | Khả thi? | Ghi chú |
|---|---|---|
| Fire OS / Fire tablet | **Có**, nhưng phải chọn SDK trong danh sách tương thích Amazon (Vungle/Mintegral/Chartboost/AppLovin…), **không AdMob** | Cần mediation hoặc chọn 1 SDK; không có plugin Godot chính thức ⇒ tự viết bridge |
| Fire TV / Vega | **Có**, UI/UX khác hoàn toàn | Không nằm trong MVP |
| Alexa Tablet | **Có** qua AdMob | Nhưng phải phát hành qua **Google Play** ⇒ phụ thuộc quyết định G13 |
| **Windows** | **Không có hạ tầng chính chủ**; chỉ có SDK bên thứ ba, **không có plugin Godot** | **Giữ D3b: Windows không ads** |

---

## 3. Kết luận vòng ④

1. **Windows rewarded eCPM: `UNVERIFIED` — và sẽ giữ nguyên như vậy.** Lý do không phải "chưa tìm kỹ" mà là **không tồn tại nguồn chính chủ** (Microsoft không có ad network cho game) và **nguồn bên thứ ba duy nhất là seller claim một case**. **Không đưa số vào bất kỳ bảng giá/mô hình nào.**
2. **D3b (Windows không ads) được giữ, nay có thêm lý do hạ tầng**, không chỉ lý do sản phẩm.
3. **Fire 2026: ads vẫn làm được nhưng đang teo** — Mobile Ad Network chết, APS chỉ cho Fire TV/tablet với điều khoản nhường 30% impression, tablet mới của Amazon **không dùng APS nữa**.
4. **Không có cơ sở để lập dự báo doanh thu ads ở bất kỳ store nào** — spread giữa các nguồn >2×, và VN rơi vào Tier 3. Giữ nguyên lập trường: **bảng giá chỉ đưa công thức, không đưa doanh thu kỳ vọng** (đã ghi ở `GATE3_PRICING_SHEET.md` §7).

---

## 4. Nguồn mới của tài liệu này

| ID | Nguồn | Loại | Dùng cho |
|---|---|---|---|
| S122 | Microsoft Learn — *Monetization for games* (`ms.date` 01/14/2026) | CP | Nguyên văn: ads chỉ qua **third-party SDK** (Vungle, Rise/Unity, Pubfinity); **Microsoft không còn ad SDK cho game** |
| S123 | MG Ads / Miracle Games — `ad.mguwp.net` | BT3 (`VENDOR_CLAIM`) | SDK ads tổng hợp cho Windows 10/11 UWP; có rewarded; *"GAM via MG Ads"*; case Cooking City, Snack Short |
| S124 | mguwp.com news — "Meet the New MG Ads SDK" | BT3 (`VENDOR_CLAIM`) | eCPM **$6,20** (case Snack Short), fill rate 98–99,5% — **không kiểm chứng được** |
| S125 | Benchmark eCPM (MAF.ad, Playio, Playwire, Appodeal, Tenjin/CAS, Udonis, revenuelab) | BT3 | US rewarded **$13–$30** tuỳ nguồn (`CONFLICTING`); VN = Tier 3, **0,05–0,18× US** |
| S132 | Patent `US 2026/0260258 A1` — The Verge, IGN, Eurogamer, Tom's Hardware, GamesIndustry.biz, TechSpot | BT3 | Microsoft nộp patent hệ ads "ad credit" cho PC/Xbox (công bố 03/09/2026); **chỉ là patent, chưa sản phẩm** |
