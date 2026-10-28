# PHASE B — BÁO CÁO NGHIÊN CỨU THƯƠNG MẠI (COMMERCIAL RESEARCH)


> 🔴 **CẢNH BÁO KÊNH AMAZON (bổ sung 2026-10-27, sau khi tài liệu này hoàn tất):** từ **08/10/2026** Amazon đã thay dòng Fire tablet bằng **Alexa Tablet (Android 16 + Google Play)**. Theo FAQ chính chủ Amazon, app cho Alexa Tablet **phải nộp qua Google Play** (trừ Amazon Kids+), **APS không khả dụng** (dùng AdMob), và doanh số/thanh toán/thuế nằm ở **Play Console**. ⇒ Mọi nội dung "Amazon" trong tài liệu này chỉ còn áp dụng cho **Fire TV/Vega, Fire OS installed base, và Amazon Kids+** — **KHÔNG** áp dụng cho tablet Amazon mới. Xem [`ALERT_AMAZON_CHANNEL_CHANGE_2026-10-27.md`](./ALERT_AMAZON_CHANNEL_CHANGE_2026-10-27.md) [S116–S121]. Việc này ảnh hưởng **D1/D10/D9a** và đang chờ user chốt phương án A/B/C/D.

- **Dự án:** WindWings: Space Shooter — game shooter không gian mới (mobile/PC), kế thừa kết quả reverse-engineering nhánh spec `arena/20330d0e-windwings-space-shooter-game-p` (PR #12).
- **Ngày tra cứu toàn bộ:** **2026-10-27** (mọi URL dưới đây được truy cập ngày này; ngày "last updated" riêng của trang được ghi kèm nếu có).
- **Phạm vi:** 3 store đã chốt — (1) Microsoft Store (Windows PC), (2) Amazon Appstore (Android/Fire), (3) Huawei AppGallery (Android/HMS).
- **Ràng buộc tuân thủ:** research-only, KHÔNG đăng ký tài khoản, KHÔNG cài SDK, KHÔNG chạy app, KHÔNG merge/close PR, KHÔNG đụng nhánh spec. Mọi thay đổi nằm trên nhánh `arena/46e50499-windwings-space-shooter-game-p`.
- **Quy ước bằng chứng:** `[Sxx]` trỏ tới mục trong [SOURCES.md](./SOURCES.md). Mỗi con số store gắn URL chính chủ + ngày tra cứu. Mục không tìm được nguồn chính chủ ghi **`UNVERIFIED`**. Nhãn kế thừa từ mandate: `STATIC_CONFIRMED` (đọc từ file repo spec), `INFERRED` (suy luận có nêu giả định), `UNKNOWN`.

> ⚠️ **Cảnh báo đọc trước — 3 phát hiện thay đổi giả định ban đầu:**
> 1. **Amazon Appstore cho Android mobile đã đóng từ 20/08/2025** — không còn submit/update app cho điện thoại Android; store chỉ còn phục vụ **Fire tablet, Fire TV và thiết bị Vega OS** [S15][S16]. Lựa chọn store "Amazon Appstore (Android/Fire)" trên thực tế hôm nay là **kênh Fire-only**.
> 2. **Amazon Appstore trên Windows 11 (WSA) đã ngừng 05/03/2025** [S22][S23] — không còn đường phân phối Android app qua Windows; hai store Amazon và Microsoft là hai bề mặt tách biệt.
> 3. **Microsoft không còn SDK quảng cáo in-app** (tắt 01/06/2020) và AppLovin MAX / Unity LevelPlay **không hỗ trợ Windows**; phương án ads thực tế trên Windows hiện chủ yếu là **Vungle/Liftoff** (chỉ interstitial + rewarded ở bản v7.x) [S18][S19][S20][S21].

---

## Mục lục
1. Dữ liệu economy kế thừa từ bản reverse-engineering
2. Đối tượng mục tiêu & 4 comparable titles
3. Điều kiện phát hành từng store (tóm tắt; bảng 3 cột đầy đủ ở file riêng)
4. Monetization khả dụng từng store (IAP / quảng cáo / subscription / ad-free)
5. Kịch bản doanh thu conservative / base / optimistic (không bịa số)
6. Compliance checklist từng store
7. Roadmap gates: map 8 gates của mandate theo store
8. Tổng kết rủi ro & mô hình khả thi xuyên store
9. Danh sách quyết định cần user chốt (file riêng)
10. Nguồn tham khảo (xem SOURCES.md)

---

## 1. Dữ liệu economy kế thừa từ bản reverse-engineering

Nguồn: nhánh spec `arena/20330d0e…` (fetch tường minh, không checkout), các nhãn dưới đây là `STATIC_CONFIRMED` theo file của nhánh đó.

| Hạng mục | Bằng chứng trong spec | Ý nghĩa cho game mới |
|---|---|---|
| 170 IAP SKU, 0 giá trong APK (giá nằm trên store) | `docs/apk-analysis/13-iap-products.md`, `datas/iap_products.json` | Toàn bộ giá phải tự thiết kế — không có số gốc để chép |
| 99 non-consumable + 71 consumable; prefix `windwings.` | cùng nguồn | Tàu rời (`playerunlock` 96 SKU = 56%), gem 19 SKU, quà 11, VIP 6, battle pass 2, coin 3… |
| Premium/ad-free theo thời gian: `pro.week`, `pro.month`, `pro.forever`, `timereward.*` | IAP product IDs | Bản gốc có cả subscription lẫn mua trọn — cần quyết định hình thái cho game mới |
| Rewarded video + native ads + "Remove ads" | `12-localization.csv`: `txt_reborn_ads` "Watch video/Xem quảng cáo", `txt_get_no_ads` "Remove ads", `txt_nativeads_header`, `txt_tiploading_7` (video cuối trận x10 coin) | Chứng minh thể loại này chạy được hybrid ads + IAP; người chơi đã được dạy chỗ xem ads |
| 20 board chứa shop cell + 7 popup upsell (`Popup_NoGems`, `Popup_NoCoins`, `Board_RebornIAP`…) | `docs/spec/ECONOMY.md` §3 | Monetization rải ngữ cảnh (contextual offer), không phải một shop tập trung |
| 5 vị trí ads trong ngân sách đề xuất của spec | `ECONOMY.md` §8.2 (bảng tự ghi rõ là **đề xuất**, không phải số gốc) | Điểm khởi đầu cho thiết kế tần suất ads |
| Enum `PurchaseType { Free, Pro, IAP, IAPBeginner, Gem, Coin }` | `dump.cs` qua ECONOMY.md §3.3 | Sáu luồng thu cần ánh xạ sang API từng store |
| Tỉ lệ rơi đặt sẵn: 676 coin / 26 item thật trong 702 lượt; 11,7% slot enemy mang item | `ECONOMY.md` §8.1 | Mốc cân bằng nguồn currency (sources); sinks phải tự thiết kế |

**Giới hạn cần nhớ:** giá coin/gem/IAP, trọng số random hộp quà, ngưỡng VIP 1–6 là `UNKNOWN` theo chính spec (mục §10 của ECONOMY.md) — không được trình bày số thiếu là "số ngành".

---

## 2. Đối tượng mục tiêu & 4 comparable titles

### 2.1 Đối tượng mục tiêu (INFERRED từ bằng chứng thể loại + listing của comps)

- **Nhân khẩu gameplay:** người chơi arcade/shmup casual-to-midcore, phiên chơi ngắn (chờ tàu, di chuyển), thích kỷ niệm game arcade/bắn máy bay thập niên 194X, ưu tiên điều khiển một tay trên điện thoại dọc.
- **Độ tuổi mục tiêu:** từ **10+** (ESRB E10+ / Everyone 10+ là rating phổ biến của các comp: 1945 Air Force "Everyone 10+", Sky Force Reloaded 9+ trên App Store) [S26][S31].
- **Hành vi chi tiêu:** phần lớn chơi miễn phí, chịu xem rewarded video để tăng tiến độ; phân khúc nhỏ chi cho gói no-ads/rút ngắn grind, whale chi tàu/bundle giá cao (1945 có SKU tới 199,99 USD) [S27].
- **Địa lý:** thể loại shmup mobile có tỷ trọng lớn ở Đông Nam Á, Mỹ Latinh, Trung Đông/Ấn Độ (các thị trường Android chiếm ưu thế) — `INFERRED` từ bảng quốc gia của các comp và chiến lược của 1SOFT; **không có nguồn nhân khẩu chính chủ, giữ ở mức định tính.**
- **Định vị đề xuất (chờ user chốt ở Gate-2):** arcade shooter dọc, progression sâu, art "di sản" space-shooter, **player-respecting** (không pay-to-win mặc định — theo DIRECTOR_STATUS nhánh spec, mục (d)).

### 2.2 Bảng tóm tắt 4 comparable titles

| Tiêu chí | Space Shooter: Galaxy Attack | 1945 Air Force | HAWK: Freedom Squadron | Sky Force Reloaded |
|---|---|---|---|---|
| Nhà phát hành | 1SOFT (ONESOFT, VN) | 1SOFT (ONESOFT, VN) | MY.GAMES / UPWAKE.ME | Infinite Dreams (PL) |
| Thể loại | Vertical shoot-'em-up, arcade | Vertical shmup chủ đề WWII | Vertical shmup **co-op**, autofire | Vertical shmup premium-craft |
| Model | F2P: ads + IAP + VIP + bản Premium $0,99 | F2P: rewarded ads + IAP + VIP tháng | F2P: ads + IAP + premium tháng + energy | **Kép:** mobile F2P ads+IAP nhỏ; PC/console **trả phí $9,99, không microtransaction** |
| Bằng chứng model | Play: "Contains ads · In-app purchases" [S24] | Play: "Contains ads · In-app purchases", IAP $0,99–$199,99 [S26][S27] | Play: "Contains ads · In-app purchases (Includes Random Items)" [S29] | App Store: Ads Removal $3,99, Plane Generator $3,99, Starter Pack $9,99; Steam $9,99 [S31][S32] |
| Quy mô (nhãn ngày 27/10/2026) | Mô tả listing tự nhận 50M+ tải; AppBrain ước lượng 9,1M riêng package này — **ước lượng bên thứ 3** [S24][S25] | Huy hiệu Play **100M+**, 4,8★ / 4,3M đánh giá [S26] | Ra mắt 01/2017; 5M người chơi sau ~1 năm (thông cáo lịch sử) [S30] | Huy hiệu Play 10M+; AppBrain ước lượng 12M — bên thứ 3 [S33] |
| Điểm mạnh | Progression sâu, PvP, sự kiện, mạng lưới ad network dày (AdMob/Unity/AppLovin/Meta/ironSource theo AppBrain) | Bộ nội dung lớn (~900 màn), clan/PvP, cỗ máy UA playable ads top thị trường (Udonis trích AppMagic) | Co-op nhiều người chơi là khác biệt thật; BRObot, >130 màn, hình ảnh trau chuốt | Thương hiệu "sạch", không P2W, giá IAP thấp; một bản build bán được trên Steam/console |
| Điểm yếu (từ review công khai) | Phàn nàn paywall/P2W, PvP lệch sức mạnh tàu trả phí, energy 20 lượt, mệt quảng cáo | Paywall giữa game (~màn 95), PvP matchmaking lệch, meta phức tạp, loot box bị gắn "simulated gambling" trên iOS | Quảng cáo không bỏ qua cuối màn (phàn nàn Reddit), grind nặng, energy; cơ cấu publisher có rủi ro địa chính trị | Quy mô doanh thu nhỏ hơn nhiều, live-ops mỏng, không ăn tiền whale |

### 2.3 Chi tiết từng title (nguồn + ngày)

**A. Space Shooter: Galaxy Attack — 1SOFT** (`com.space.shooter.alien.galaxyattack`)
- Google Play listing ghi nhãn "Contains ads · In-app purchases"; có biến thể trả phí "Galaxy Attack (Premium)" $0,99 [S24] (truy cập 27/10/2026).
- AppBrain (bên thứ 3, truy cập 27/10/2026): 9,1M tổng tải package này, 47 thư viện, liệt kê AdMob/Unity Ads/AppLovin/Facebook Ads/ironSource [S25]. **Số tải là ước lượng, không phải số chính chủ.**
- Review người dùng trên Play: paywall ẩn sau tiến độ, PvP nghiêng về tàu trả phí, hệ energy 20 lượt [S24].
- Bài học: ads dày + VIP + bản premium song song là công thức của chính nhà phát hành cùng "hệ" với game bị reverse-engineer — tham chiếu trực tiếp nhất cho cơ chế, nhưng cũng là mẫu bị chê P2W cần tránh.

**B. 1945 Air Force — 1SOFT** (`com.os.airforce`)
- Play (27/10/2026): 100M+ tải, 4,8★ từ 4,31M review, nhãn Everyone 10+, "Contains ads · In-app purchases" [S26].
- AppGrooves (bên thứ 3): dải IAP $0,99–$199,99/item [S27]; review nói không có gói no-ads một lần, chỉ phí tháng — **dẫn chứng định tính, kiểm tra lại trên store khi vào Gate-3**.
- Udonis (24/04/2025) trích AppMagic: playable ad của 1945 Air Force thuộc nhóm hiển thị nhiều nhất thị trường (~2 tỷ impression/90 ngày) [S28] — nguồn bên thứ 3.
- Bài học: rewarded ads **tùy chọn** được người chơi khen, nhưng P2W/PvP và grind là điểm rớt điểm; UA bằng playable ads là vũ cạnh tranh lớn của genre.

**C. HAWK: Freedom Squadron — MY.GAMES/UPWAKE.ME** (`com.my.hawk.air.shooter`)
- Play (27/10/2026): "Contains ads · In-app purchases (Includes Random Items)", nhấn mạnh co-op [S29].
- AppGrooves (2022, bên thứ 3): IAP $0,99–$114,99 [S27].
- Phỏng vấn App2Top (10/2018, cập nhật 10/2018): doanh thu ~$900k/tháng thời điểm đó, thiết kế monetization theo chiều sâu tăng ARPU [S30] — **số lịch sử, không phải hiện trạng, không dùng để dự báo.**
- Bài học: co-op là điểm khác biệt bảo vệ được trước các game đơn người chơi; quảng cáo cưỡng ép/bỏ không qua làm người chơi lâu năm rời bỏ (bằng chứng Reddit) — ủng hộ nguyên tắc "chỉ rewarded + hạn chế interstitial".

**D. Sky Force Reloaded — Infinite Dreams** (`pl.idreams.SkyForceReloaded2016`)
- App Store US (27/10/2026): Free, IAP "Ads Removal $3,99", "Plane Generator $3,99", "Starter Pack $9,99", rating 9+ [S31].
- Steam (27/10/2026): $9,99, ra mắt 29/11/2017, đánh giá 8,9/10; FAQ nhà phát hành trên Steam Community: bản PC **không microtransaction/ads, cân bằng lại progression** [S32]. Có mặt trên Switch/PS/Xbox cùng giá $9,99.
- Google Play: "Contains ads · In-app purchases", 10M+ tải [S33].
- Bài học: **mô hình kép** (mobile F2P nhẹ + PC/console premium) là bằng chứng sống cho chiến lược riêng từng store — rất hợp với việc Microsoft Store yếu mảng ads, có thể đẩy bản premium/no-ads trên Windows.

---

## 3. Điều kiện phát hành từng store (tóm tắt)

> Bảng so sánh 3 cột đầy đủ (store × hạng mục) nằm tại [STORE_COMPARISON_3COL.md](./STORE_COMPARISON_3COL.md). Dưới đây là các điểm then chốt.

### 3.1 Microsoft Store (Windows PC)
- **Tài khoản:** Partner Center, Individual hoặc Company; **không phí đăng ký cho cả hai loại** (flow mới; Individual miễn phí từ 10/09/2025 ở ~200 markets, Company bỏ phí $99 từ 07/05/2026); xác minh danh tính bằng giấy tờ + selfie [S1][S2].
- **Revenue share (hiện hành, kiểm tra 27/10/2026):** **12% cho game** (dev giữ 88%), 15% cho app; Xbox console 30%. App Developer Agreement v8.11 (17/03/2026) §6 [S3]; trang Get started **đã fetch nguyên văn** xác nhận: commerce riêng giữ 100% chỉ cho non-gaming, commerce Microsoft phí 12% game/15% app [S4][S74]. Quyền chọn commerce riêng/giữ 100% **chỉ áp dụng app non-game** — **game bắt buộc dùng commerce của Microsoft**, kể cả gỡ quảng cáo và subscription (Store Policies 7.20 §10.8.1) [S5].
- **Review:** tối đa **3 business days**, listing xuất hiện trung bình ~15 phút sau khi pass; add-on (IAP) certification ~1 giờ [S6].
- **Packaging:** MSIX là chuẩn; cũng nhận MSI/EXE (Win32 không đóng gói) và PWA [S7]. Unity xuất bản được sang UWP/MSIX.
- **Vùng:** 240+ quốc gia/vùng, 110+ ngôn ngữ [S8].

### 3.2 Amazon Appstore (thực tế 2026: Fire tablet / Fire TV / Vega)
- **Tài khoản:** Amazon Developer Console, **miễn phí — chính chủ xác nhận**: Payments FAQ ghi nguyên văn "The program is free. You pay nothing to create a developer account, use Amazon APIs, and submit apps" [S9]; trang chủ developer cũng ghi "Registration is easy, free"; 2 loại tài khoản Sole Proprietorship / Business [S75].
- **Revenue share:** chuẩn 70/30; **Small Business Accelerator (SBAP, đã fetch toàn bộ FAQ ngày 27/10/2026):** dev có tổng doanh thu Appstore **dưới 1 triệu USD trong năm lịch sử trước** (mọi địa lý/tiền tệ) và **mọi dev mới** tự động được nâng royalty 70/30 → **80/20**; cộng AWS credits tương đương 10% doanh thu (phải tự enroll, tối thiểu $10 doanh thu/thị trường/tháng, credits hết hạn sau 12 tháng) [S10]. Nếu đạt **≥1 triệu USD trong năm thì quay lại 70/30 từ năm kế tiếp** (không phải bị cắt ngay trong năm); dev có hợp đồng tùy chỉnh (custom agreement) bị loại khỏi chương trình [S10].
- **Review:** điển hình 3–5 ngày (KB cộng đồng, 12/2023); tài liệu chính thức khuyên liên hệ nếu sau 6 ngày vẫn "in review" [S11][S12].
- **Packaging:** **APK hoặc AAB** (AAB nhận từ 18/05/2022, Amazon tự chuyển bằng bundletool), ≤2,5GB, không nhận OBB; thiết bị Vega dùng định dạng VPKG riêng [S13][S15].
- **Vùng:** gần 200 quốc gia tải về; IAP theo marketplace (US/CA/MX/BR/GB/DE/FR/IT/ES/JP/IN/AU); **JP: IAP trên Android đã dừng 20/02/2025** (Fire tablet vẫn qua amazon.co.jp) [S14][S16].

### 3.3 Huawei AppGallery (Android/HMS)
- **Tài khoản:** HUAWEI ID + **identity verification** (individual/enterprise); **đăng ký miễn phí** cả hai loại (FAQ chính thức Q11) [S34].
- **Revenue share (game):** ngoài Trung Quốc **Huawei 30% : dev 70%**; **IAP game tại Trung Quốc đại lục 50:50**; paid game 30:70 cả hai vùng. Tỷ lệ này nhất quán trong cả Joint Operations Agreement bản 2020 lẫn **AG Connect Distribution Service Agreement for Paid Apps bản 26/01/2022 (bản công khai mới nhất, đã fetch)** [S35][S76]. Mức ưu đãi 85% thời 2019–2020 đã hết hạn. Công thức settlement: `(thu hộ – chiết khấu – thuế gián thu – hoàn tiền – channel deduction) × (1 – commission)`; từ 01/01/2022 Huawei không còn khấu trừ Channel Deduction đối với vùng Part II/III; **mức quyết toán tối thiểu €200** (vùng Part II/III) hoặc CNY 1.000 (dev nước ngoài tại đại lục), dồn kỳ nếu chưa đạt [S76]. Lưu ý: điều khoản hiệu lực lúc onboard trong AGC console là phiên bản mới nhất — cần đối chiếu lại khi ký (mục quyết định D5).
- **Review:** **3–5 working days** theo App Review FAQ chính thức (một số trang trợ giúp AAB ghi 1–3 ngày — tài liệu Huawei nội bộ không nhất quán, lấy con số FAQ làm chuẩn) [S36].
- **Packaging:** APK (≤4GB), AAB (≤150MB, bắt buộc dùng App Signing của Huawei), cả EXE cho app Windows [S37].
- **Vùng:** AppGallery + IAP tại 170+ quốc gia/vùng, 78 ngôn ngữ, 195 bậc giá [S38]. **Trung Quốc đại lục: game cần ISBN/版号 của NPPA + software copyright + ICP filing, dev nước ngoài không tự xin được** [S39][S40].

---

## 4. Monetization khả dụng từng store

### 4.1 Ma trận "có/không hôm nay" (ngày tra cứu 27/10/2026)

| Cơ chế | Microsoft Store (Windows) | Amazon Appstore (Fire) | Huawei AppGallery (HMS) |
|---|---|---|---|
| **IAP consumable** (gem, coin, bundle) | ✅ Add-on consumable (Store-managed/developer-managed), Windows.Services.Store [S41] | ✅ Amazon IAP API — **bắt buộc dùng cho nội dung số** (Monetization Policy) [S42] | ✅ HMS IAP Kit loại 0 consumable [S43] |
| **IAP non-consumable** (mở tàu, gỡ quảng cáo vĩnh viễn) | ✅ Durable (Forever hoặc 1–365 ngày) [S41] | ✅ Entitlement ("premium purchases such as ad-free versions") [S14] | ✅ IAP loại 1; tài liệu PMS nêu thẳng ví dụ "ad removal" [S44] |
| **Subscription tự gia hạn** | ✅ Subscription add-on (Win10 1607+, chỉ trên Windows.Services.Store) [S45] | ✅ IAP subscription [S14] | ✅ IAP loại 2 auto-renewable [S43] |
| **Phí xử lý IAP** | **12%** (game, gồm cả subscription) [S3][S5] | **20%** nếu <$1M/năm, ngược lại 30% [S9][S10] | **30%** ngoài TQ; **50%** tại đại lục (game IAP) [S35] |
| **Rewarded video** | ⚠️ Chỉ qua bên thứ 3. **Vungle/Liftoff có SDK Windows cập nhật 2026** (v7.x Win32/WinUI3/WinForms/WPF + UWP v6.11.6); v7.x **chỉ interstitial + rewarded** [S19][S20] | ✅ APS + các SDK Amazon test tương thích: AdColony, Chartboost, APS, Vungle, Mintegral (danh sách cập nhật 15/08/2023) [S46] | ✅ Ads Kit (Petal Ads): rewarded, interstitial, banner, native, splash, roll [S47] |
| **Interstitial** | ⚠️ Như trên (Vungle); không nên cưỡng ép theo định hướng player-respecting | ✅ qua các SDK trên | ✅ |
| **Banner/native** | ⚠️ Vungle: banner chỉ còn trên nhánh UWP cũ v6.5.2+, v7.x desktop không có banner [S20]. **Pubfinity xác nhận còn hoạt động 27/10/2026** (SDK UWP banner/native/video, danh mục nhỏ chủ yếu game casual Random Salad) [S77]; **RISE đã pivot, trang RISE Engage 404 — không còn bằng chứng SDK Windows** [S78] | ✅ banner/interstitial (APS); native có thể qua mạng khác | ✅ đầy đủ |
| **SDK quảng cáo第一方 còn sống?** | ❌ Microsoft Ad Monetization (UWP) tắt 01/06/2020; Monetize Now/pubCenter web tắt 15/10/2025, không sản phẩm thay thế [S17][S18] | ❌ Amazon Mobile Ads Network tắt 30/09/2021 → thay bằng APS [S48] | ✅ Petal Ads Publisher Service (170+ quốc gia; >85.000 app tích hợp Ads Kit tính 30/09/2025) [S49] |
| **AdMob (Google) phục vụ được?** | ❌ Không có SDK Windows | ⚠️ Chạy được trên Fire không có Play Services (Google xác nhận) nhưng **Google không hỗ trợ trên third-party store** và **không có trong danh sách tương thích của Amazon** [S50][S46] | ⚠️ Chạy được trên thiết bị non-Huawei Android thường; thiết bị HMS không GMS cần đánh giá riêng — `UNVERIFIED` cho kho AppGallery |
| **AppLovin MAX / Unity LevelPlay** | ❌ Cả hai chính thức chỉ Android/iOS, không Windows [S21][S51] | ✅ MAX có adapter Fire OS; Amazon liệt kê AppLovin Max 11.8.2 tương thích Fire [S52] | ✅ bản Android (mediation đa mạng) |
| **Phí nền tảng quảng cáo** | Theo hợp đồng trực tiếp với ad network (Vungle…), **không phải phí Store** | APS: **10% publisher transaction fee** trên giá thầu (từ 01/09/2023, cả demand Amazon lẫn bên thứ 3) [S53]; APS là chương trình cần duyệt/mời [S52] | Tỷ lệ chia sẻ ads hiện tại **UNVERIFIED** (tuyên bố 80% cho dev là chính sách 2021, không còn cơ sở hiện hành) [S47] |
| **Paid app (bán bản game)** | ✅ Free/Paid/Free trial, phí 12% | ✅ "Download fee" [S9] | ✅ Paid Apps (30:70 ngoài TQ) [S35] |

### 4.2 Diễn giải theo từng store

**Microsoft Store — mảng ads yếu nhất, mảng IAP/subscription chắc nhất.**
- Game bắt buộc commerce Microsoft, phí 12% thấp nhất trong ba; add-on đủ 3 loại (consumable/durable/subscription) [S41][S45].
- Không có ad SDK第一方; AppLovin MAX và LevelPlay không có Windows. Vungle/Liftoff là mạng lớn duy nhất còn cập nhật đều (NuGet v7.1.1–7.1.2, 09–10/2026) nhưng chỉ có interstitial + rewarded trên desktop [S19][S20]; Pubfinity còn hoạt động nhưng quy mô nhỏ, tập trung UWP/casual [S77]; RISE đã rời mảng SDK Windows [S78]. **Kết luận thiết kế:** trên Windows nên lấy thu nhập từ IAP + gói ad-free/trả phí, ads chỉ là tùy chọn rewarded qua Vungle (hoặc Pubfinity nếu đóng gói UWP); không nên thiết kế kinh tế phụ thuộc banner.

**Amazon Appstore (Fire) — đủ bộ ads + IAP nhưng thị trường hẹp.**
- IAP API đủ 3 dạng (consumable/entitlement/subscription) và là bắt buộc với nội dung số [S14][S42].
- APS là tuyến ads chính (in-app bidding, phí 10%), cộng 5 mạng Amazon test tương thích; AppLovin MAX chạy được trên Fire [S46][S52]. AdMob chỉ là phương án "tự chịu rủi ro hỗ trợ".
- Sau 20/08/2025, kênh này chỉ còn ý nghĩa với hệ thiết bị Fire (tablet/TV) và Vega — đặc thù nhập cư bằng controller/TV cần xem xét ở Gate-4 (không phải phone shmup thuần).

**Huawei AppGallery — bộ công cụ đối xứng Google nhất.**
- IAP Kit đủ 3 loại product, có subscription; Ads Kit đủ 6 định dạng; Petal Ads mạnh ở châu Âu/Trung Đông/ĐNÁ/Mỹ Latinh (170+ nước) [S43][S47][S49].
- Cần bật Merchant Service và ký hợp đồng publisher; cá nhân vẫn làm publisher được nếu đã xác minh [S49].
- Tại Trung Quốc đại lục: ads và IAP đi quy trình riêng, game cần 版号 (mục 6.3).

### 4.3 Kết luận: model nào khả thi xuyên cả 3 store?

| Model | Khả thi cả 3? | Ghi chú |
|---|---|---|
| **Rewarded-ads-first + IAP consumable (gem/coin/bundle)** | ✅ | Ads: Vungle (Win) / APS+đối tác (Fire) / Ads Kit (HMS). IAP: cả ba đủ API. Đây là model chung khả thi nhất |
| **Gói "Remove ads" mua một lần (non-consumable)** | ✅ | Durable (MS) / Entitlement (Amazon) / non-consumable (HMS) — bám đúng `pro.forever` của bản gốc |
| **Subscription ad-free/Premium tuần/tháng** | ✅ | Cả ba hỗ trợ auto-renewable; tiệm cận `pro.week`/`pro.month` của bản gốc |
| **Battle pass bán bằng IAP** | ✅ | Định danh như consumable/entitlement theo từng mùa; cả ba store chấp nhận |
| **Banner/native ads làm nguồn thu chính** | ❌ trên Windows | Chỉ thiết kế cho Android/Fire/HMS; Windows bỏ banner |
| **Interstitial cưỡng ép** | ⚠️ kỹ thuật được cả 3, nhưng vi phạm định hướng player-respecting và rủi ro review/đánh giá | Chỉ dùng hạn chế, có tần suất cap |
| **Loot box/gacha (mua random)** | ⚠️ | Bị gắn nhãn "Includes Random Items"/simulated gambling; Huawei xếp gambling/loot box vào nhóm **18+** [S54]; ảnh hưởng rating và một số thị trường — cần quyết định ở Gate-3 |
| **Paid premium edition (giống Sky Force PC)** | ✅ | Cả 3 cho bán paid app; đặc biệt hợp Windows nơi ads yếu — **[SUPERSEDED 2026-10-28] User chốt Windows = F2P + IAP, không ads (D6b); không còn bản paid premium riêng** |

---

## 5. Kịch bản doanh thu conservative / base / optimistic

> **Nguyên tắc theo mandate:** không bịa doanh thu, không hứa forecast. Phần này là **khung mô hình tham số hóa** với (a) công thức, (b) khoảng tham số có nguồn công khai, (c) ví dụ số học trên **1.000 DAU** để minh họa — không phải dự báo cho game của mình. S liệu thật chỉ có sau soft launch (Gate-7).

### 5.1 Công thức thu nhập (áp riêng từng store)

```
Doanh thu ads/tháng = DAU × 30 × (số rewarded impression/DAU) × eCPM / 1000
Doanh thu IAP/tháng  = MAU × tỷ lệ payer tháng (%) × ARPPU
                     ≈ (DAU × hệ số MAU/DAU) × payer_conv_tháng × ARPPU
Net dev revenue      = Gross × (1 − nền tảng fee) − thuế/chi phí thanh toán
LTV(30 ngày)         = Σ ARPDAU ngày 1..30 theo đường retention thực đo
Payback (tháng)      = CAC / (ARPDAU × biên lợi nhuận sau phí)
```

### 5.2 Bảng giả định từng dòng (mọi khoảng tham số gắn nguồn; chưa có nguồn cho bề mặt riêng → `UNVERIFIED`)

| Tham số | Conservative | Base | Optimistic | Nguồn / ngày |
|---|---|---|---|---|
| D1 retention | 22% (median ngành 2025) | 30% (top quartile) | 40% (top decile) | GameAnalytics 2026 Benchmarks, dữ liệu 2025, 16.000+ game [S55] (27/10/2026) |
| D7 retention | <4% (median) | 6–7% (P75) | 11–12% (P90) | cùng nguồn [S55] |
| D30 retention | 0,7–0,8% (median) | 3% (mốc "khỏe" top 25% báo cáo 2025) | 6%+ | [S55][S56] |
| Genre Shooting D1 tham chiếu | 28,54% (bảng tổng hợp bên thứ 3 từ GameAnalytics 2025) | — | — | digitalminds tổng hợp [S56], 04/10/2026 |
| Rewarded impression/DAU | 2 | 4 | 6 | **Không có benchmark chính chủ — giả định thiết kế**, tương quan 5 vị trí ads trong ECONOMY.md §8.2 (`INFERRED`) |
| eCPM rewarded Android (Mỹ) | $3,02 (casual Android H1/2025, xu hướng giảm từ $3,60 H1/2023) | $10–16 | $19,63 (Android Mỹ, MAF) | TopOn qua Game Growth Advisor [S57]; MAF [S58] (27/10/2026) |
| eCPM rewarded **Windows/Vungle** | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** | Không có báo cáo công khai tách nền Windows — phải lấy số từ dashboard Vungle sau khi tích hợp |
| eCPM rewarded **Fire tablet / AppGallery** | **UNVERIFIED** (dùng khoảng Android làm proxy, giảm 20–40% do demand hẹp — `INFERRED`) | như cột conservative | như cột conservative | Amazon/Huawei không công bố eCPM |
| ARPDAU blended (ads-only casual) | $0,01–0,05 | — | — | Game Growth Advisor tổng hợp Appodeal/TopOn [S57] |
| ARPDAU blended (hybrid casual ads+IAP) | — | $0,15–0,50 | — | [S57] |
| Tỷ lệ payer ngày (hyper/arcade tham chiếu) | 0,94% (báo cáo GameAnalytics hyper-casual) | 1–2% | 2–4% | GameAnalytics industry report [S59]; earnify tổng hợp [S60] |
| ARPPU | $42 (hyper-casual benchmark) | tự đo sau soft launch | tự đo | [S59] |
| CPI game trung bình 2024 | $0,36 (mọi game); hyper-casual $0,40; hybrid-casual $0,95 | — | — | Adjust Mobile Games Insights 2025 [S61] |
| Hệ số MAU/DAU | 5× | 4× | 3× | Giả định thiết kế (`INFERRED`), thay bằng số thực sau 30 ngày |

### 5.3 Ví dụ số học minh họa trên 1.000 DAU (KHÔNG phải dự báo)

Lấy tham số **base**: 4 rewarded/DAU, eCPM giả định $8 (Android; Windows/Fire/HMS phải thay số thực), 30 ngày.

- Ads gross/tháng = 1.000 × 30 × 4 × 8 / 1000 = **$960 gross/tháng/1.000 DAU**
- Sau phí nền tảng:
  - Microsoft (ads không qua Store, phí thuộc hợp đồng Vungle — chưa biết, tạm để 100% gross ở tầng Store): $960
  - Amazon APS (trừ 10% transaction fee): ~$864
  - Huawei: tỷ lệ **UNVERIFIED** → không tính được net, để trống trong mô hình
- IAP ví dụ: MAU = 1.000 × 4 = 4.000; payer 1,5% = 60 payer; ARPPU giả định $20 (**giả định**) → gross $1.200/tháng; sau phí: MS ×0,88 = $1.056; Amazon (gói 80/20) ×0,80 = $960; Huawei (ngoài TQ) ×0,70 = $840.
- **Ba kịch bản chỉ khác nhau ở tập tham số §5.2 (retention × impressions × eCPM × conversion), không được điền doanh thu "kỳ vọng" trước khi có số soft launch.** Mỗi thay đổi giả định phải ghi ngày và người quyết định.

### 5.4 Metrics bắt buộc track (xây dashboard từ Gate-7)

| Nhóm | Chỉ số |
|---|---|
| Retention | D1, D7, D30 (classic retention), rolling retention, đường cong 30 ngày |
| Engagement | sessions/DAU, thời lượng phiên, số màn/phiên, tỷ lệ hoàn thành màn |
| Ads | fill rate, eCPM theo format/quốc gia, impressions/DAU, rewarded opt-in rate, tỷ lệ xem hết |
| IAP | ARPDAU (ads / IAP / blended), ARPPU, payer conversion (ngày & tháng), AOV, refund rate |
| LTV/CAC | LTV D7/D30/D90, CPI theo kênh, **payback period** (mục tiêu payback ≤ D90), ROAS D7/D30 |
| Kỹ thuật | crash-free sessions, ANR, thời gian load, tỷ lệ lỗi giao dịch IAP |
| Store | rating, số review, tỷ lệ từ chối certification, thời gian review từng lần submit |

**Lưu ý hạ tầng đo:** ba store có hệ riêng (Partner Center analytics, Amazon Reports/Earnings, AGC + Petal Ads console); cần lớp analytics trung lập (quyết định nhà cung cấp ở Gate-4, tuyệt đối không hard-code key vào repo).

---

## 6. Compliance checklist từng store

### 6.1 Khung pháp lý chung (nguồn chính phủ/liên minh)

| Quy định | Yêu cầu cốt lõi | Nguồn (27/10/2026) |
|---|---|---|
| **COPPA (Mỹ, trẻ <13)** | Đồng ý cha mẹ trước khi thu thập thông tin cá nhân; **sửa đổi 2025 (Federal Register 22/04/2025): phải có opt-in riêng cho targeted advertising/chia sẻ bên thứ 3, giới hạn lưu trữ dữ liệu** | FTC Six-Step Plan + press release 16/01/2025 [S62][S63] |
| **GDPR (EU/EEA)** | Căn cứ xử lý hợp pháp, quyền chủ thể, xóa tài khoản; trẻ em độ tuổi đồng ý số **13–16 tùy quốc gia thành viên** | European Commission + EDPB [S64][S65] |
| Luật tuổi tiểu bang Mỹ (TX/UT/LA…) | App store phải verify tuổi, lấy consent phụ huynh dưới 18 | Amazon GetUserAgeData (live 01/01/2026) [S67] |

### 6.2 Microsoft Store

1. **Privacy policy URL** bắt buộc nhập trong Partner Center nếu thu thập/chuyển dữ liệu cá nhân (Store Policies 7.20 §10.5) [S5].
2. **Age rating:** hoàn thành questionnaire **IARC** cho mọi sản phẩm, cập nhật suốt vòng đời (§11.11) [S5][S68].
3. **Quảng cáo (§10.10):** tôn trọng advertising ID; ads trung thực, phân biệt được nội dung; privacy statement phải nêu việc gửi dữ liệu cho ad provider và cách opt-out quảng cáo quan tâm; sản phẩm nhắm trẻ <13 phải khai báo với Microsoft và ads phải phù hợp trẻ [S5].
4. **Financial (§10.8):** game dùng Store IAP API, không điều hướng người dùng sang cơ chế thanh toán khác [S5].
5. Chạy **Windows App Certification Kit (WACK)** trước khi nộp; nội dung kiểm thử gồm security/technical/content compliance [S6].

### 6.3 Amazon Appstore (Fire)

1. **Privacy Labels:** khai báo User Data Privacy questionnaire trong Developer Console (hiển thị trên trang chi tiết app từ 11/2023) [S66].
2. **Content rating:** questionnaire **riêng của Amazon** (không phải IARC — Amazon tự ấn định maturity rating, giữ quyền thay đổi) [S69].
3. **Tuân thủ family-friendly:** Content Policy coi Appstore là môi trường gia đình; nội dung không phù hợp không có cơ chế bảo vệ sẽ bị từ chối [S70].
4. **Tuổi người dùng:** tích hợp GetUserAgeData API để đáp ứng luật tiểu bang Mỹ (live 01/01/2026); báo cáo "significant change" khi đổi thực hành dữ liệu [S67][S15].
5. **IAP:** mọi nội dung số phải qua Amazon IAP API, không thanh toán thay thế (Monetization and Advertising Policy) [S42].
6. Dữ liệu cá nhân: liên kết privacy policy, cơ chế xóa tài khoản nếu có hệ thống account.

### 6.4 Huawei AppGallery

1. **Privacy policy URL** trong AGC + trong app; nêu mục đích/phạm vi thu thập kể cả SDK bên thứ 3; hỗ trợ rút consent và **xóa tài khoản** (Review Guidelines §7) [S71].
2. **Tuân thủ luật theo vùng:** guideline nêu rõ GDPR (EU), PIPL và luật bảo vệ trẻ em TQ, PDPO Hồng Kông, PDPA Singapore [S71].
3. **Quảng cáo (§5):** gắn nhãn "Ad", không hiển thị trên lock screen/ngoài app/sau khi app đóng, không bật lên ở vùng người dùng hay bấm phím hệ thống; ads phải phù hợp độ tuổi [S72].
4. **Age rating:** hệ riêng — ngoài TQ 3+/7+/12+/16+/18+; đại lục 3+/8+/A12/A14/A16/A18; **gambling/loot box thuộc 18+ và app 18+ có thể không được phát hành tại đại lục** [S54].
5. **Bảo vệ trẻ vị thành niên (§8):** consent phụ huynh trước khi thu thập dữ liệu trẻ em, chính sách quyền riêng tư trẻ em chuyên biệt; app trẻ em không được chứa link ngoài/IAP ngoài vùng kiểm soát phụ huynh [S73].
6. **Trung Quốc đại lục (game):** bắt buộc Software Copyright Certificate + **Publication Approval Number (版号/ISBN của NPPA)** + ICP filing; công ty nước ngoài không tự xin, phải qua NPH nội địa có giấy phép; quy trình cho game nhập khẩu thường 6–12 tháng theo các đơn vị tư vấn (nguồn bên thứ 3 [S40], con số thời gian `UNVERIFIED` chính chủ). Tài liệu chính chủ Huawei (doc 30215) xác nhận tài liệu phải nộp trong mục Copyright information/Publication number [S39].
7. OAID chỉ dùng cho quảng cáo/phân tích; không ép xem ads hoặc giao dữ liệu để mở khóa nội dung [S71].

### 6.5 Checklist gộp dùng chung cho cả 3

- [ ] Privacy policy công khai (URL), nêu đầy đủ SDK ads/analytics và chia sẻ bên thứ 3
- [ ] Cơ chế xóa tài khoản & export/xóa dữ liệu
- [ ] CMP/consent flow cho EEA (GDPR) + UK; tôn trọng opt-out personalized ads (Huawei §7.7, MS §10.10.5)
- [ ] Xác định đúng "directed to children" theo COPPA; bật chế độ child-directed cho ad SDK nếu áp dụng
- [ ] Khai báo data safety/privacy label đúng thực tế trên cả 3 console
- [ ] Hoàn thành IARC (MS) / maturity questionnaire (Amazon) / age rating (Huawei)
- [ ] Đánh giá lại rating nếu dùng loot box (nguy cơ 18+ tại Huawei, nhãn simulated gambling trên iOS/Play)
- [ ] Lưu evidence consent, hợp đồng ad network, dữ liệu xử lý trong khu vực phù hợp
- [ ] Quy trình xử lý yêu cầu xóa dữ liệu và khiếu nại (SLA hỗ trợ)

---

## 7. Roadmap gates — map 8 gates của mandate (§6) theo store

> Nguồn 8 gates: `docs/PROJECT_DIRECTOR_MANDATE.md` §6 trên nhánh spec (đọc qua `git show`, không checkout).

| Gate (mandate §6) | Việc chung | Bổ sung riêng Microsoft | Bổ sung riêng Amazon/Fire | Bổ sung Huawei/HMS |
|---|---|---|---|---|
| **1. Review findings & giới hạn Phase A** | Chấp nhận spec kinh tế (170 SKU không giá, ads positions, sinks thiếu) | — | — | — |
| **2. Product Brief & target player** | Chốt đối tượng, định vị player-respecting | Quyết định bản Windows là F2P hay premium (học Sky Force) | Chốt có/không theo đuổi Fire TV (controller) | Chốt loại trừ đại lục hay đầu tư TQ qua NPH |
| **3. Business model & monetization** | Chọn mix rewarded/IAP/ad-free/subscription; nguyên tắc no P2W | Chốt Vungle làm ad partner (duy nhất còn bằng chứng sống); không kỳ vọng banner | Chốt APS + 1–2 mạng trong danh sách tương thích; quyết định AdMob (rủi ro không hỗ trợ) | Chốt Ads Kit + IAP Kit; làm rõ tỷ lệ chia sẻ ads trong hợp đồng |
| **4. Architecture & technical risks** | Lớp abstraction IAP/ads đa store; analytics | MSIX packaging, WACK, Windows.Services.Store; đánh giá Vungle SDK v7 (WebView2 runtime) | Fire OS API level, test máy Fire thật, AAB/APK; controller/TV | HMS Core dependency, AGC project, App Signing cho AAB, OAID/consent |
| **5. MVP scope & acceptance criteria** | Định nghĩa đủ luồng IAP/ads trên cả 3 | Add-on types mapping (consumable/durable/subscription) | IAP entitlement/subscription mapping; App Tester | PMS product types 0/1/2 mapping; sandbox testing |
| **6. Implementation & independent review** | Code review, bảo mật key, không hard-code secret | — | — | Tuân thủ guideline §5/§7/§8 từ lúc code |
| **7. Integration/runtime validation & release-readiness** | Soft launch, đo metrics §5.4, compliance bằng chứng | Certification ≤3 ngày; thử lại chu kỳ submit/add-on | Review 3–5 ngày; test trên Fire tablet + Fire TV; privacy labels | Review 3–5 ngày; Cloud Testing/Cloud Debug; test ID ad trước formal ID |
| **8. User acceptance & explicit release authorization** | User ký duyệt release từng store | Lên lịch publish, theo dõi 15 phút hiển thị | Lựa chọn quốc gia/marketplace | Chọn vùng phát hành (loại đại lục nếu chưa có 版号) |

**Việc cross-cutting không thuộc gate nào nhưng phải có trước Gate-7:** legal entity/tax profile cho payout của 3 console; hợp đồng ad network (Vungle, APS, Petal Ads); quy trình support/refund; kế hoạch ứng phó từ chối review (mỗi store cho resubmit, nhưng Amazon/Huawei có thể kéo dài 1–2 vòng).

---

## 8. Tổng kết rủi ro & mô hình khả thi

### 8.1 Rủi ro已 định vị có nguồn

| # | Rủi ro | Mức độ | Nguồn |
|---|---|---|---|
| R1 | Amazon Appstore Android mobile đóng cửa → thị phần điện thoại Android không còn kênh Amazon | Cao | [S15][S16] |
| R2 | Windows không còn ad SDK第一方, hai mediator lớn không hỗ trợ → lựa chọn ads thực tế hẹp (Vungle là mạng lớn; Pubfinity quy mô nhỏ; RISE đã pivot) | Cao | [S17][S19][S21][S77][S78] |
| R3 | Vungle Windows v7.x không có banner, chỉ interstitial/rewarded — thiết kế kinh tế phải tương thích | Trung bình | [S20] |
| R4 | Vào Trung Quốc đại lục cần 版号 qua NPH nội địa, 6–12 tháng, không tự đứng tên | Cao (nếu theo đuổi TQ) | [S39][S40] |
| R5 | Tỷ lệ chia sẻ quảng cáo HMS hiện không công bố chính thức hiện hành | Trung bình | [S47] |
| R6 | eCPM/ARPDAU trên Windows/Fire/AppGallery không có benchmark công khai → không cam kết doanh thu | Trung bình | §5.2 |
| R7 | Loot box đẩy rating 18+ (Huawei) và nhãn gambling (iOS/Play) | Trung bình | [S54] |
| R8 | WSA ngừng → không thể "một APK chạy cả Windows qua Amazon" | Thấp (đã rõ) | [S22][S23] |
| R9 | Tài liệu Huawei có chỗ không nhất quán (review 1–3 vs 3–5 ngày; điều khoản nhiều phiên bản) | Thấp | [S36][S35] |

### 8.2 Mô hình xuyên store đề xuất (trình Gate-3, chưa phải quyết định)

1. **Lõi chung:** F2P + rewarded video (tối đa ~4–6/người/ngày) + IAP consumable (gem/coin/bundle) + gỡ quảng cáo một lần + Premium subscription tùy chọn + battle pass nhẹ.
2. **Microsoft Store:** **F2P + IAP, không ads** — [SUPERSEDED 2026-10-28, D3b/D6b] thay cho "IAP/subscription + paid premium edition + Vungle ads" ở bản trước.
3. **Amazon/Fire:** F2P đầy đủ ads (APS + mạng tương thích) + IAP; tận dụng mức 80/20 Small Business Accelerator; kiểm soát phạm vi thiết bị (tablet/TV).
4. **Huawei AppGallery:** F2P đầy đủ Ads Kit + IAP Kit; phát hành ngoài đại lục trước; loại TQ cho tới khi có đối tác 版号.
5. **Không** P2W áp đặt, **không** interstitial cưỡng ép, **không** loot box trả thưởng ảnh hưởng sức mạnh (tránh 18+) — phù hợp định hướng player-respecting của director status.

---

## 9. Quyết định cần user chốt

Xem file chuyên biệt: [DECISIONS_NEEDED.md](./DECISIONS_NEEDED.md) (12 quyết định, gắn gate và hạn chế thông tin).

## 10. Nguồn tham khảo

Toàn bộ URL, ngày truy cập và loại nguồn (chính chủ/bên thứ 3) được liệt kê tại [SOURCES.md](./SOURCES.md). Mọi con số trong báo cáo đối chiếu được theo ID `[Sxx]`. Mục nào thiếu nguồn chính chủ đã được gắn **UNVERIFIED** ngay tại chỗ, không thay bằng trí nhớ.

---

## 11. Nhật ký kiểm chứng bổ sung (vòng 2 — cùng ngày 2026-10-27)

Vòng rà soát thứ hai được chạy để đóng các mục còn treo ở bản đầu. Kết quả:

| Mục | Trạng thái trước | Sau kiểm chứng vòng 2 | Nguồn |
|---|---|---|---|
| Microsoft 12% game / 15% app / 100% non-game tự commerce | Đã có từ App Developer Agreement, chưa đối chiếu trang hướng dẫn | **Xác nhận nguyên văn** trên trang Get started ("…keep 100% of the revenue for non-gaming apps, or use Microsoft's commerce platform … pay a competitive fee of 12% for games and 15% for apps") | [S74] |
| Amazon phí đăng ký | Suy ra từ nhiều trang, chưa có câu chính chủ | **Xác nhận chính chủ**: Payments FAQ — "The program is free. You pay nothing to create a developer account, use Amazon APIs, and submit apps" | [S9] |
| SBAP: điều kiện & thời điểm mất ưu đãi | Ghi chung "<$1M → 80/20" | **Làm rõ**: tự động cho dev mới & dev <$1M (mọi địa lý/tiền tệ); **đạt ≥$1M thì về 70/30 từ năm kế tiếp**; dev có custom agreement bị loại; AWS credits 10% phải tự enroll, tối thiểu $10/thị trường/tháng, hết hạn 12 tháng | [S10] |
| Huawei 30:70 (ngoài TQ) / 50:50 (đại lục) | Chỉ có template 2020 | **Tái xác nhận** trong AG Connect Distribution Service Agreement bản **26/01/2022** (bản công khai mới nhất); bổ sung công thức settlement, bỏ channel deduction từ 01/01/2022, ngưỡng quyết toán tối thiểu €200 / CNY 1.000 | [S35][S76] |
| Pubfinity (ads Windows) | `UNVERIFIED` | **Còn hoạt động** — site live, SDK UWP banner/native/video, quy mô nhỏ, curated | [S77] |
| RISE (ads Windows) | `UNVERIFIED` | **Không còn bằng chứng SDK Windows** — RISE Engage trả 404, công ty pivot sang supply platform programmatic | [S78] |

**Vẫn giữ `UNVERIFIED` sau vòng 2 (không có nguồn công khai):** eCPM riêng cho Windows/Vungle, Fire tablet và AppGallery; tỷ lệ chia sẻ doanh thu quảng cáo HMS/Petal Ads; thời gian cấp 版号 thực tế; điều kiện onboarding thương mại của Pubfinity.

**Hệ quả cho quyết định:** không có thay đổi nào làm đảo kết luận §6–§8; D3 được cập nhật để phản ánh việc RISE không còn là phương án và Pubfinity chỉ phù hợp nếu đóng gói UWP.
