# GATE-3 PRICING SHEET — remove-ads / premium / battle pass (3 store)

> **Vai:** commercial-researcher (`arena/46e50499`) — **ưu tiên ③** của prompt lane. **Ngày tra cứu:** 2026-10-27.
> **Trạng thái:** research-only, **đề xuất giá** để director/user chốt ở **Gate-3** (business model/monetization). Không tạo sản phẩm IAP, không mở console, không publish.
> **Nhãn bằng chứng:** `STATIC_CONFIRMED` (đọc trực tiếp nguồn chính chủ/repo) · `INFERRED` (suy luận có giả định) · `UNVERIFIED` · `BT3` (bên thứ ba).
> **Nguồn mới:** S107–S115 (đã thêm vào [SOURCES.md](./SOURCES.md)).

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

> **Giá không đổi vì G14.** Fire-TV-first đổi **cách hiển thị** (chữ lớn, đọc từ 3 m, dialog focus được) chứ **không đổi mức giá**. Amazon vẫn tính trên **giá đã gồm VAT**; G10 chốt pass **consumable** nên **không** áp luật "MS không cho nâng giá subscription".


## 0. Ba kết luận trước khi vào bảng giá

**① Game gốc KHÔNG dùng store subscription.** Trong `datas/iap_products.json` của APK: `pro.forever` nằm ở **NonConsumable** (99 SKU), còn `pro.week`, `pro.month`, `pro.1stpurchase`, `battlepass`, `battlepass2`, `timereward.month`, `gifts.weekly0–4` đều nằm ở **Consumable** (71 SKU). `STATIC_CONFIRMED`
⇒ "Subscription" trong **D4c** thực chất là **gói thời hạn mua lại thủ công (non-renewing pass)**, không phải auto-renew của store. Đây là **quyết định kiến trúc**, xem §4.

**② "Remove ads" mất phần lớn giá trị khi ads là rewarded-only.** D8a chốt **rewarded-only, không interstitial cưỡng ép** — nghĩa là người chơi **đã có thể chọn không xem ads**. Benchmark cho thấy người chơi trả $0.99–$4.99 để *thoát ads bị ép*; khi không có ads bị ép, SKU "remove ads" chỉ còn bán được **quyền lợi kèm theo**. Xem **G9**.

**③ Giá hiển thị ở Amazon và Huawei là giá ĐÃ GỒM THUẾ.** Amazon: *"the price that you set for each marketplace is your suggested list price, which includes any VAT or similar taxes"* `STATIC_CONFIRMED` [S108]. Huawei: *"in-app product price (tax included) displayed to users"* `STATIC_CONFIRMED` [S110]. ⇒ **Không được lấy giá hiển thị nhân (1 − revenue share) rồi coi là tiền về.** Phải trừ thuế trước.

---

## 1. SKU gốc — bảng đối chiếu (STATIC_CONFIRMED)

| SKU gốc | Loại trong APK | Ý nghĩa nghiệp vụ | D4c ánh xạ sang |
|---|---|---|---|
| `windwings.pro.forever` | **NonConsumable** | mở khoá vĩnh viễn (premium/không ads) | Gói một lần |
| `windwings.pro.week` | **Consumable** | quyền lợi 7 ngày | Gói thời hạn 7 ngày |
| `windwings.pro.month` | **Consumable** | quyền lợi 30 ngày | Gói thời hạn 30 ngày |
| `windwings.pro.1stpurchase` | **Consumable** | ưu đãi lần mua đầu | Offer khởi đầu |
| `windwings.battlepass` / `battlepass2` | **Consumable** | battle pass mùa 1 / mùa 2 | Battle pass theo mùa |
| `windwings.vippack1..6` | **Consumable** | 6 bậc gói VIP | (ngoài phạm vi Gate-3 này) |
| `windwings.timereward.forever` | **NonConsumable** | mở khoá nhận thưởng theo thời gian | — |
| `windwings.gifts.weekly0..4` | **Consumable** | gói quà tuần | — |

**Hệ quả:** không có SKU nào trong APK là giá. **Mọi con số dưới đây là đề xuất**, không phải dữ liệu trích xuất. Không được trình bày như "giá của game gốc".

---

## 2. Cơ chế giá từng store (ràng buộc cứng)

| | **Microsoft Store** | **Amazon Appstore** | **Huawei AppGallery** |
|---|---|---|---|
| **Giá tối thiểu (USD)** | Tier thấp nhất **$0.99** [S107] | **$0.99** [S108] | 195 bậc giá; không công bố bậc thấp nhất trong trang đã đọc → `UNVERIFIED` [S109] |
| **Giá tối đa** | Không nêu trong trang đã đọc → `UNVERIFIED` | **$400.00** consumable/entitlement; **$399.99** subscription [S108] | Không nêu; có cấu hình **max payment amount** trong PMS [S110] |
| **Được đặt giá tuỳ ý?** | **Chỉ trong tier**, trừ **override 1 thị trường** được nhập free-form [S107] | **Có** — base price + tự đặt tay từng currency, hoặc để Amazon quy đổi [S108] | **Có** — base price + `Convert prices` theo tỷ giá & thuế [S109][S110] |
| **Thuế trong giá hiển thị** | Tier "may include sales or VAT" — mơ hồ, phải kiểm khi submit [S107] | **Đã gồm VAT** [S108] | **Đã gồm thuế** [S110] |
| **Quy đổi tỷ giá** | MS tự quy đổi theo bảng tier/currency; có thể chỉnh từng thị trường [S107] | Để Amazon quy đổi, hoặc tự đặt tay [S108] | **KHÔNG tự cập nhật** — *"AppGallery Connect does not automatically update your product prices based on the latest exchange rates"*; phải bấm **Convert prices → Save** [S109] |
| **Tăng giá subscription sau khi publish** | **KHÔNG được** (chỉ được giảm; giảm rồi không nâng lại được) [S107] | **Được**, nhưng **subscriber cũ giữ giá cũ** (kể cả đang free trial) [S108] | Phải kiểm trong PMS; `UNVERIFIED` |
| **Ràng buộc nội dung về giá** | — | — | **§6.1 "Overpricing and deceptive pricing are forbidden"**; **§6.2 giá trong app phải khớp giá thực trả**; auto-renew phải có consent riêng, **không được bật mặc định** [S111] |

**Hai cái bẫy vận hành:**
1. **MS + subscription = không nâng giá được.** Nếu sau này muốn tăng giá gói tháng, phải tạo SKU mới. `STATIC_CONFIRMED` [S107]
2. **Huawei + tỷ giá = tự chịu.** Không bấm `Convert prices` định kỳ thì giá ở 170+ nước trôi khỏi giá trị thực. `STATIC_CONFIRMED` [S109]

---

## 3. Bằng chứng giá đối thủ (comp trực tiếp)

**Sky Force Reloaded** — cùng thể loại (vertical shmup), của Infinite Dreams, vừa F2P mobile vừa premium PC. Đây là comp mạnh nhất vì **cùng công ty, cùng game, hai mô hình**.

| Mục | Giá | Nguồn / nhãn |
|---|---|---|
| **Ads Removal** (iOS US, hiện tại) | **$3.99** | App Store listing, trang vi-US hiển thị USD [S112] `STATIC_CONFIRMED` |
| S2 Star Doubler / Plane Generator | $3.99 / $3.99 | như trên |
| Precious Cargo | $1.99 | như trên |
| **Starter Pack** | **$9.99** | như trên |
| Ads Removal (lịch sử 2016) | **$1.99** | TouchArcade review 03/06/2016 [S113] `BT3` |
| Ads Removal (giá vùng) | **NZ$6.99 · A$5.99** | App Store NZ/AU listing [S112] `STATIC_CONFIRMED` |
| **Bản PC/Xbox** | **$9.99** (Sky Force Bundle $16.99) | xbox.com [S114] `STATIC_CONFIRMED` |
| Bản Switch | $9.99 | Nintendo store `STATIC_CONFIRMED` |

**Đọc được gì từ đây:** cùng một tựa game bán **remove-ads $3.99 trên mobile** và **bản đầy đủ $9.99 trên PC** — đúng mô hình **D6a** đã chốt. Đây là tiền lệ chính chủ, không phải suy đoán.

**Benchmark ngành (BT3 — dùng để định khung, không phải cam kết):**
- Remove ads: **$0.99–$4.99** được coi là hợp lý; **trên $5 bắt đầu bị chê**; "chỉ gỡ ads mà $9.99" bị gọi là tham. Gộp thêm currency vào $4.99 thì được đánh giá là "ủng hộ dev". [S115] `BT3`
- Battle pass: **casual mặc định $5.99** (buy rate ~10%), **action $9.99** (buy rate ~16%); dải phổ biến **$5–15/mùa**; median toàn thị trường **$9.99**; season 4–12 tuần. [S115] `BT3`

---

## 4. Phát hiện kiến trúc: "subscription" của game gốc không phải subscription của store

Đây là điểm cần director/user quyết vì nó **đổi cả cách lập trình và cách tính doanh thu**.

| Phương án | Cách làm | Ưu | Nhược |
|---|---|---|---|
| **(A) Theo dữ liệu gốc** — `pro.week`/`pro.month` là **consumable + hết hạn phía server/app** | Người chơi mua lại khi hết hạn; không auto-renew | Khớp 100% SKU gốc; **tránh toàn bộ nghĩa vụ auto-renew** của 3 store (Huawei §6.2 consent riêng, không bật mặc định [S111]); không bị "không nâng giá được" của MS [S107] | Không có doanh thu định kỳ tự động; **cần logic hạn dùng** (server hoặc lưu máy — lưu máy dễ bị sửa giờ); rủi ro người chơi quên mua lại |
| **(B) Dùng subscription gốc của store** | 3 adapter dùng API subscription (MS add-on subscription, Amazon subscription terms, HMS subscription) | Doanh thu định kỳ; store lo thu hồi/hoàn tiền | **MS: không nâng giá được sau publish** [S107]; phải khai auto-renew consent riêng [S111]; phức tạp hơn cho 3 adapter đang phải tự viết (xem `GATE4_GODOT_COMMERCE_QUEUE.md`) |
| **(C) Không bán gói thời hạn** — bỏ `pro.week`/`pro.month`, chỉ giữ `pro.forever` + battle pass | Đơn giản nhất | Ít SKU, ít rủi ro chính sách | Lệch D4c; mất dải giá thấp cho người chưa sẵn sàng trả $3.99 |

**Đề xuất (không phải quyết định): (A)** — vì khớp dữ liệu gốc, và vì 3 adapter đang phải tự viết nên **giảm số API phải bọc** là lợi thế thật. Nhưng nếu chọn (A), phải ghi rõ: **hạn dùng phải kiểm ở server**, không dựa vào giờ máy.

---

## 5. BẢNG GIÁ ĐỀ XUẤT (trình Gate-3)

Giá tính bằng **USD**. Ánh xạ sang VND/từng vùng do store quy đổi — trừ Huawei phải bấm `Convert prices` thủ công.

| # | SKU (gốc → mới) | Loại | **Giá đề xuất** | Căn cứ | Cần kiểm chứng |
|---|---|---|---|---|---|
| P1 | `pro.forever` → **Premium (một lần)** | NonConsumable / Entitlement | **$3.99** | Sky Force Ads Removal $3.99 (cùng thể loại, cùng công ty mô hình) [S112]; benchmark ≤$4.99 là vùng không bị chê [S115] | **G9** — nếu ads đã rewarded-only, $3.99 có còn bán được? |
| P2 | `pro.week` → **Pass 7 ngày** | Consumable (hết hạn server) | **$1.99** | Bậc vào thấp; Sky Force Precious Cargo $1.99 làm mốc tâm lý [S112] | Tỷ lệ mua lại; nếu <15% thì bỏ |
| P3 | `pro.month` → **Pass 30 ngày** | Consumable (hết hạn server) | **$4.99** | Tier 5 chuẩn ngành; rẻ hơn 2×P2 để khuyến khích gói tháng | Như P2 |
| P4 | `pro.1stpurchase` → **Starter offer** | Consumable | **$1.99** (gói trị giá ~$6) | Mô hình "starter pack" ngành; Sky Force Starter Pack $9.99 là bậc cao [S112] | Có bị coi là "deceptive pricing" theo Huawei §6.1 nếu trị giá khai không khớp? [S111] |
| P5 | `battlepass` → **Battle Pass (mùa)** | Consumable | **$4.99** launch → **$5.99** ổn định | Casual mặc định $5.99, buy rate ~10% [S115]; $4.99 dùng làm giá khai trương | Season dài 4–8 tuần; số mùa/năm |
| P6 | **Premium Windows edition** (SKU mới) | License / app price | **$9.99** | Sky Force PC/Xbox **$9.99** chính chủ [S114]; MS game phí 12% ⇒ dev giữ ~$8.79 trước thuế | Giá này **đã gồm thuế** hay chưa phải xác nhận khi submit [S107] |
| P7 | Bundle PC (premium + artbook/OST) — *tuỳ chọn* | — | **$14.99** | Sky Force Bundle $16.99 [S114] làm trần tham chiếu | Chỉ làm nếu có nội dung thật |

**Không đưa vào bảng này:** giá gói gems/coins (`gems0..7`, `coins0..2`) — cần dữ liệu cân bằng kinh tế, thuộc lane economy, không phải lane thương mại. Ghi nhận để tránh hiểu nhầm là đã chốt.

---

## 6. Kiểm tra tính nhất quán trước khi trình

| Kiểm tra | Kết quả |
|---|---|
| Mọi giá ≥ mức tối thiểu của store? | Có — thấp nhất $1.99 > $0.99 (MS/Amazon) [S107][S108] |
| Vượt trần nào không? | Không — cao nhất $14.99 << $400 [S108] |
| Có SKU nào là subscription auto-renew? | **Không**, nếu chọn phương án (A) ⇒ không vướng "không nâng giá được" của MS [S107] |
| Giá trong app có khớp giá store? | Phải lấy **từ API store** (`StorePrice.FormattedPrice` [S107], IAP API Amazon, HMS product info) — **không hard-code**; nếu không sẽ vi phạm Huawei §6.2 [S111] |
| Đã tính thuế chưa? | Amazon/Huawei: giá đề xuất **là giá đã gồm thuế** [S108][S110]. MS: phải xác nhận khi submit [S107] |
| Có yếu tố "deceptive pricing"? | Rủi ro ở P4 (starter offer khai "trị giá $6") — phải chứng minh được bằng giá bán lẻ các thành phần [S111] |

**Ghi chú về tiền về (từ BOARD-DELTA 135):** doanh thu từ **khách Mỹ** trên MS/Amazon bị **withholding 30%** (VN chưa có hiệp định thuế hiệu lực). Mọi tính toán net phải tách US / non-US. Bảng trên chỉ là **giá niêm yết**, không phải net.

---

## 7. Độ nhạy doanh thu — chỉ công thức, không bịa số

Do Phase B §5 đã có mô hình tham số; ở đây chỉ nêu **cách giá tác động**, để Gate-3 thấy đòn bẩy:

```
Net per transaction ≈ (Giá_hiển_thị ÷ (1 + thuế)) × (1 − revenue_share) × (1 − withholding_nếu_khách_US)
Ví dụ cấu trúc (KHÔNG phải dự báo):
  P1 = $3.99, giả định VAT 20% EU, share 30% Amazon, khách EU
  → 3.99 / 1.20 = 3.325 ; × 0.70 = $2.33 net
  P1 cùng giá, khách Mỹ trên Amazon: × (1 − 0.30) → $1.63 net
```
⇒ Chênh lệch **US vs EU cho cùng một SKU là ~30%**. Đây là lý do phải tách dòng báo cáo doanh thu, và là lý do **không nên đặt giá theo "số đẹp" ở Mỹ** mà bỏ qua thuế.

**Không có** eCPM/ARPDAU riêng cho Windows/Fire/AppGallery (đã ghi ở Phase B) ⇒ **không** suy ra doanh thu từ bảng giá này. Mọi con số doanh thu vẫn phải chờ soft launch.

---

## 8. Quyết định mới cần chốt (G9–G12)

| # | Quyết định | Bối cảnh | Phương án | Đề xuất |
|---|---|---|---|---|
| **G9** | **"Remove ads" có còn là sản phẩm bán được khi ads rewarded-only?** | D8a: rewarded-only, không ép xem ⇒ người chơi đã có quyền không xem. Benchmark cho thấy $0.99–4.99 là giá của việc *thoát ads bị ép* [S115] | (a) Giữ "remove ads" thuần → **bán rất kém**; (b) Đổi thành **"Premium": gỡ ads + tự động nhận phần thưởng rewarded không cần xem + QoL**; (c) Bỏ SKU, chỉ bán battle pass + premium PC | **(b)** — giữ giá $3.99 nhưng bán **quyền lợi**, không bán "sự vắng mặt của ads" |
| **G10** | **Pass thời hạn: consumable hay subscription store?** | §4; dữ liệu gốc dùng Consumable; MS không cho nâng giá subscription [S107]; Huawei đòi consent auto-renew riêng [S111] | (A) consumable + hết hạn server · (B) subscription store · (C) bỏ gói thời hạn | **(A)** — khớp dữ liệu gốc, giảm API phải bọc, tránh nghĩa vụ auto-renew |
| **G11** | **Giá battle pass & độ dài mùa** | Casual $5.99, buy rate ~10% [S115] | (a) $4.99 launch → $5.99 · (b) $9.99 ngay | **(a)**; mùa 4–6 tuần để có ≥6 mùa/năm |
| **G12** | **Giá premium Windows** | Sky Force PC $9.99 chính chủ [S114]; MS phí game 12% | (a) $9.99 · (b) $12.99 · (c) $7.99 | **(a)** — bám tiền lệ cùng thể loại; xét lại nếu wishlist/refund xấu |

---

## 9. Bàn giao

- **Gate-3 (business model):** §5 là bảng giá trình duyệt; §6 là checklist tự kiểm; **G9 là mục phải chốt trước tất cả** vì nó đổi bản chất SKU chính.
- **Godot-coder:** §6 dòng "giá trong app phải lấy từ API store" là yêu cầu kỹ thuật cứng (không hard-code), và phụ thuộc G10 (consumable → cần logic hết hạn ở server).
- **Verifier `ef6b75ef`:** kiểm ① có hard-code giá không; ② hạn dùng pass có kiểm ở server không; ③ có bán subscription mà chưa khai auto-renew không.
- **Ghi rõ giới hạn:** đây là **giá đề xuất dựa trên giá niêm yết của comp + benchmark**, **không** phải giá đã kiểm chứng bằng doanh thu thật của chính dự án. Mọi điều chỉnh phải chờ số soft launch.

---

## 10. Nguồn mới

| ID | Nguồn | Dùng cho |
|---|---|---|
| S107 | MS Learn — Set and schedule pricing (app + add-on) | tier từ $0.99; free-form chỉ khi override 1 thị trường; **subscription không nâng giá được**; tier "may include tax" |
| S108 | Amazon — Create and Submit Single IAP items | min $0.99; max $400 / subscription $399.99; **giá gồm VAT**; tăng giá subscription → subscriber cũ giữ giá cũ |
| S109 | Huawei — Configuring Your Products (IAP) | base price + `Convert prices`; **không tự cập nhật theo tỷ giá** |
| S110 | Huawei — Creating an In-App Product (AGC Help) | giá **đã gồm thuế**; có max payment amount trong PMS |
| S111 | Huawei — Review Guidelines §6 App Payment (50104-06) | §6.1 cấm overpricing/deceptive; §6.2 giá trong app phải khớp; auto-renew consent riêng |
| S112 | Apple App Store listing — Sky Force Reloaded (US/vi, NZ, AU) | Ads Removal $3.99 US; NZ$6.99; A$5.99; Starter Pack $9.99 |
| S113 | TouchArcade review Sky Force Reloaded (06/2016) | giá lịch sử $1.99 (BT3) |
| S114 | xbox.com — Sky Force Reloaded | bản PC **$9.99**; Bundle $16.99 |
| S115 | Benchmark tổng hợp (guardingpear/AppFollow/MWM recap) | remove-ads $0.99–4.99 vùng hợp lý; battle pass casual $5.99 / action $9.99 (BT3) |
