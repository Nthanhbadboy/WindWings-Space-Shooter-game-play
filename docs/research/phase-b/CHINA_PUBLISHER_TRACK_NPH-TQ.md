# ⑤ NPH TRUNG QUỐC (NPH-TQ) — ĐÁNH GIÁ ĐƯỜNG ĐI

> **Vai:** commercial-researcher (`arena/46e50499`) · **Ngày tra cứu:** 2026-10-27 · **Ưu tiên thấp nhất** trong prompt lane.
> **Câu hỏi:** có nên tính đường **nhà phát hành Trung Quốc (NPH-TQ)** cho thị trường đại lục không, và nếu có thì điều kiện là gì?
> **Nhãn:** `STATIC_CONFIRMED` (đọc văn bản luật/trang chính phủ) · `BT3` (báo/luật sư/tư vấn) · `INFERRED` · `UNVERIFIED`.
> **Ràng buộc nền:** **D2a đã chốt: KHÔNG vào đại lục Trung Quốc.** Tài liệu này **không mở lại D2a** — nó ghi lại *vì sao D2a đúng*, *điều kiện nào sẽ đổi kết luận*, và *chi phí thật nếu đổi ý*.

---

## 1. Kết luận trước

**D2a đúng, và lý do mạnh hơn "không muốn làm" — đó là rào pháp lý mà một studio nước ngoài tự nó KHÔNG THỂ vượt.**

Ba tầng khoá cứng, phải vượt **cả ba** mới bán được 1 bản:

1. **Không được tự phát hành.** Pháp luật TQ **cấm** doanh nghiệp có vốn nước ngoài (kể cả WFOE và liên doanh) kinh doanh dịch vụ **xuất bản trực tuyến** ⇒ **không thể tự xin 版号 (banhao)**. Bắt buộc phải có **đơn vị xuất bản nội địa** đứng tên nộp. `STATIC_CONFIRMED` (văn bản luật, đọc qua bản dịch BT3) [S127]
2. **Phải có 版号 trước khi bán**, không phải đăng ký sau. 版号 do **NPPA** cấp theo **đợt**; **bản nhập khẩu (import) đi đường riêng, ít hơn nhiều**: 2026 tới cuối tháng 9 là **~46 bản import trên tổng 1.571 版号 (~3%)**. `STATIC_CONFIRMED` (số liệu NPPA) + `BT3` [S126][S128]
3. **Kinh tế bị chia nhiều lớp**: store Android TQ thường lấy **~50%** (kèm điều kiện bắt buộc dùng SDK store), rồi **NPH nội địa lấy thêm**; thực nhận của dev nước ngoài thường rơi **30–50%** giá người dùng trả — có trường hợp **~20% hoặc thấp hơn**. `BT3` [S129]

⇒ Với một game shooter arcade nhỏ, chưa có IP, chưa có cộng đồng TQ: **chi phí để được xét (thời gian + hồ sơ + đối tác + chia doanh thu) lớn hơn nhiều so với doanh thu kỳ vọng**, và **không kiểm soát được thời điểm** (đợt cấp phép, không có hạn cam kết).

---

## 2. Cấu trúc pháp lý — cần biết chính xác

### 2.1 Ai được nộp

| Vai | Yêu cầu pháp lý | Ghi chú |
|---|---|---|
| **Đơn vị xuất bản (出版单位)** — "publisher" | Phải giữ **网络出版服务许可证** (Online Publishing Service Licence), phạm vi có **game** | Thường là **đơn vị nhà nước** hoặc tổ chức được cấp phép; **nhà đầu tư nước ngoài bị cấm** giữ loại giấy này |
| **Đơn vị vận hành (运营单位)** — "operator" | Phải có **ICP License (B25)** + **ICP Filing** + **Mobile App Filing** | Đơn vị nội địa; ký hợp đồng bản quyền với chủ IP nước ngoài |
| **Chủ bản quyền nước ngoài (ta)** | Không nộp được; phải **đăng ký hợp đồng bản quyền** tại **NACC** (国家版权局) trước | Hợp đồng bản quyền phải được **ghi nhận (著作权合同登记)** |

`STATIC_CONFIRMED` (luật) + `BT3` (hướng dẫn của cơ quan chính phủ NZ – MFAT, và các hãng luật) [S127][S131]

> **Chi tiết đáng chú ý:** hướng dẫn của MFAT (New Zealand) ghi rõ *"It is **not possible** to partner with an operator and publisher in **Hong Kong and Macao** to apply for an ISBN"*, và *"Foreign companies running an office or subsidiary in China also **cannot** apply"*. `BT3` [S131] ⇒ **không có đường vòng qua HK/Macau.**

### 2.2 Quy trình & thời gian

- Nộp **Sở xuất bản cấp tỉnh** → thẩm định → chuyển **NPPA** duyệt cuối. Hai tầng.
- **Hạn xử lý công bố: 80 ngày làm việc** kể từ khi **được nhận** hồ sơ. Đây là **hạn luật định**, **không phải thời gian thực tế**. `BT3` [S126]
- Thực tế với **bản import**: thường **6–8 tháng hoặc hơn**. `BT3` [S128]
- Lịch sử có **đóng băng**: 2018 và 2021–2022 (gần 8–9 tháng **0 giấy phép**). `BT3` [S126][S128]

### 2.3 Hồ sơ (10 mục theo NPPA, tóm lược)

Công văn đề nghị cấp tỉnh (1 bản/game) · đơn xin duyệt game internet do nước ngoài cấp phép · giấy ghi nhận hợp đồng bản quyền NACC · giấy phép kinh doanh + ICP của đơn vị vận hành · **≥10 ảnh chụp màn hình (có 1 ảnh tiêu đề)** · tài liệu **hệ thống chống nghiện** · **toàn bộ kịch bản tiếng Trung + danh sách từ cấm** · **tài khoản test cho giám định** · **3 bản gói cài** · tài liệu điện tử + **video demo**. `BT3` (diễn giải từ trang NPPA) [S126]

### 2.4 Nghĩa vụ sau khi được duyệt (vẫn phải làm nếu vào TQ)

- **Đăng ký tên thật (real-name)** bằng giấy tờ định danh của chính phủ cho **mọi** tài khoản; **cấm** phục vụ tài khoản ẩn danh/guest. `BT3` [S128]
- Tích hợp **SDK xác thực tên thật của NPPA** trước khi thương mại hoá.
- **Cắt phiên người chơi vị thành niên** theo khung giờ quy định (server-side).
- Server/backend **phải đặt trong đại lục**; thêm **APP filing** theo pipeline MIIT. Dữ liệu người chơi chịu **PIPL**. `BT3` [S126][S128]

> Với game của ta: **backend 3 store hiện tại không có** (G4 chưa chốt account/cloud save). Muốn vào TQ thì phải **dựng backend trong đại lục** — một hạng mục hoàn toàn mới, không nằm trong bất kỳ gate nào.

---

## 3. Kinh tế — vì sao "50% store" chưa phải con số cuối

| Lớp | Mức điển hình | Nhãn |
|---|---|---|
| Store Android TQ (liên doanh, bắt buộc SDK store) | **~50%** doanh thu | `BT3` [S129] |
| Apple App Store tại TQ | **30%** (15% nếu đủ điều kiện) — **nhưng phải có 版号 mới được xuất hiện** | `BT3` [S131] |
| NPH/đơn vị vận hành nội địa | **30–50%** phần còn lại, tuỳ mức đầu tư/PR | `BT3` [S129] |
| **Thực nhận của dev nước ngoài** | **~30–50%** giá người dùng trả; có trường hợp **~20% hoặc thấp hơn** | `BT3` [S129] |
| NPH trả cho dev theo mô hình ads (WeChat Mini Game) | **~50% doanh thu ads**, làm lại game bằng chi phí NPH | `BT3` [S129] |

**So sánh trực tiếp với 3 store đã chốt:**

| | Windows (MS) | Amazon | Huawei | **TQ đại lục** |
|---|---|---|---|---|
| Store lấy | **12%** (game) | 30% / 20% (SBAP nhỏ) | ~15% (quy đổi) | **~50% (Android)** |
| Thêm NPH | 0% | 0% | 0% | **30–50% phần còn lại** |
| Dev nhận (ước) | **~88%** | ~70–80% | ~85% | **~30–50%, có thể ~20%** |
| Thời gian tới doanh thu đầu | ngày–tuần | ngày–tuần | ngày–tuần | **6–8 tháng+, hoặc vô hạn nếu trượt đợt** |
| Ai kiểm soát việc ra mắt | **ta** | ta | ta | **NPPA + NPH** |

⇒ Cùng một bản game, **một bản bán ở TQ đại lục có thể mang về ít hơn 1/3 so với bán trên Microsoft Store**, và **ta không quyết được ngày ra mắt**.

---

## 4. Có ngoại lệ nào đáng theo dõi không?

| Ngoại lệ | Nội dung | Đánh giá |
|---|---|---|
| **Shanghai pilot** | Chính quyền Thượng Hải thí điểm coi **game do nước ngoài phát triển nhưng phát hành tại Thượng Hải** được xử lý **như game nội địa** (đường duyệt nhẹ hơn) | `BT3` (hãng luật Bird & Bird) [S130]. **Đáng theo dõi nhưng chưa đủ để đổi D2a**: vẫn cần đơn vị nội địa, vẫn phải có 版号, vẫn phải đặt server + tuân PIPL; và đây là **thí điểm**, chưa phải chế độ chung |
| **NPH Trung Quốc phát hành ra THẾ GIỚI** (không phải vào TQ) | Ví dụ Miracle Games phát hành game lên **Microsoft Store toàn cầu** (Cooking City, Snack Short) và vận hành luôn SDK ads Windows (MG Ads) | `BT3` [S123]. Đây là **hướng khác hoàn toàn**: không cần 版号, không cần ICP, nhưng **phải chia doanh thu và giao quyền vận hành**. **Không khuyến nghị** cho dự án này vì ta đã tự phát hành được trên MS Store (12%) — thuê NPH chỉ để "có người lo" là trả tiền cho việc mình làm được |
| **HK / Macau / Đài Loan** | Là **khu vực cấp phép riêng**, **không** chịu chế độ NPPA; HK/Macau không dùng để xin ISBN cho đại lục | `BT3` [S128][S131]. **Có thể** phát hành tiếng Trung phồn thể ở HK/TW như thị trường thường (qua store quốc tế) — **không cần** NPH-TQ. Đây là **hướng hợp lý nếu muốn có người chơi Trung văn** |

---

## 5. Điều kiện để mở lại (rõ ràng, để sau này không phải bàn lại từ đầu)

Chỉ nên mở lại D2a khi **đồng thời**:

1. Game đã có doanh thu ổn định ở ≥2 trong 3 store đã chốt (chứng minh sản phẩm sống), **và**
2. Có **đối tác nội địa** thật (đơn vị xuất bản có licence + đơn vị vận hành có ICP) chủ động đề nghị, **và**
3. Chấp nhận được **thực nhận ~30–50%** và **không kiểm soát ngày ra mắt**, **và**
4. Sẵn sàng **dựng backend trong đại lục** + tuân PIPL + real-name + chống nghiện.

**Không đủ 4 điều kiện ⇒ giữ D2a: không vào đại lục.**

---

## 6. Việc lane này KHÔNG làm (và vì sao)

- **Không** liên hệ NPH, **không** thu thập báo giá thật — đó là hành động thương mại, ngoài phạm vi research-only.
- **Không** đưa con số "doanh thu TQ kỳ vọng" — không có cơ sở, và đã cam kết không dự báo.
- **Không** mở lại D2a — tài liệu này **củng cố** D2a.

---

## 7. Nguồn mới của tài liệu này

| ID | Nguồn | Loại | Dùng cho |
|---|---|---|---|
| S126 | **NPPA** — 国产/进口网络游戏审批信息 (danh sách chính thức 2026) + thủ tục 出版境外著作权人授权的互联网游戏作品审批 | CP | 版号 là **phê duyệt trước**, hai tầng tỉnh→NPPA; **hạn luật định 80 ngày làm việc**; 10 mục hồ sơ; kênh import công bố theo **danh sách luỹ kế theo năm** |
| S127 | **《网络出版服务管理规定》** (NPPA+MIIT Order No. 5, hiệu lực 10/03/2016) — Điều 2, 7, 10, 27 | CP (luật; đọc qua bản dịch `BT3`) | Game là "ấn phẩm trực tuyến"; cần **网络出版服务许可证**; **Điều 10 cấm WFOE/liên doanh** làm dịch vụ xuất bản trực tuyến; **Điều 27** phải duyệt trước khi đưa lên mạng |
| S128 | Tổng hợp số liệu NPPA 2026 (tech-insider, Niko Partners, Digital Policy Alert) | BT3 | 2026 tới cuối 9/2026: **~1.571 版号, ~46 import (<3%)**; tháng 8/2026: 209 nội địa + **6 import**; tháng 9/2026: 206 nội địa + **3 import**; bản import thường **6–8 tháng+**; đóng băng 2018 & 2021–22; nghĩa vụ real-name + SDK NPPA + cắt phiên vị thành niên |
| S129 | Cơ cấu chia doanh thu TQ (gamedeveloper.com, appinchina, 21cloudbox, GamesBeat, eightsixgames) | BT3 | Store Android TQ **~50%**; NPH thêm **30–50%**; dev nước ngoài thực nhận **~30–50%**, có case **~20%**; mô hình ads WeChat Mini Game chia **~50%** |
| S130 | Bird & Bird — Shanghai pilot: game nước ngoài phát triển tại Thượng Hải xử lý như game nội địa | BT3 (hãng luật) | Có **thí điểm** nhẹ hơn cho Thượng Hải — **chưa phải chế độ chung**, không đủ đổi D2a |
| S131 | MFAT (New Zealand) — *Entering China's Mobile Gaming Market* + chinagamelegal | CP (cơ quan chính phủ) + BT3 | Dev nước ngoài **không** xin được ISBN; cần **operator có ICP (B25)** + **publisher có Web Publishing Service Licence**; **không thể** mượn HK/Macau; công ty có văn phòng tại TQ **cũng không** được nộp; App Store TQ **bắt buộc ISBN** |
