# W0 — Asset listing (icon · key art · screenshot) cho 3 store

> **Vai:** art-planner (`arena/1b836828`) · **Ngày:** 2026-10-27 · **Trạng thái:** kế hoạch, **chưa vẽ gì**.
> **Đầu vào:** `docs/rollout/STORE_ASSETS_AND_LISTING_DRAFT.md` (nhánh `20330d0e`) — tài liệu đó **cố ý để trống số pixel** và
> giao lại: *"Session F điền cột số từ hướng dẫn chính thức hiện hành, ghi URL + ngày truy cập"*. Đây là phần điền số đó, cho
> **3 kênh launch**: Microsoft Store (Windows, premium) · Amazon Appstore (Fire tablet) · Huawei AppGallery (ngoài TQ).
>
> **Nhãn bằng chứng:** `STATIC_CONFIRMED` = đọc nguyên văn trên trang chính thức, có URL + ngày · `CONFLICTING` = nguồn official
> nói khác nhau **hoặc** yêu cầu store xung đột với thiết kế game · `INFERRED` = suy ra · `UNKNOWN` = chưa xác minh.
> **Không** con số nào dưới đây lấy từ trí nhớ hay từ "hướng dẫn bên thứ ba".

---

## 0. TL;DR

| Câu | Trả lời |
|---|---|
| W0 là gì | **27 slot** cho 3 store: **8 icon** (1 master + 7 export) · **4 key art** · **15 screenshot** |
| Tốn bao nhiêu | **35 h** (icon 9 · key art 15 · screenshot 9 · QA 2) — **không** nằm trong scope B 1.578,4 h |
| Chặn cái gì | Chặn **submit store**, **không** chặn gameplay (L2) ⇒ chạy song song W1 được |
| Khi nào làm | Icon + key art: ngay sau **S0** (không cần build). Screenshot: **chỉ sau khi có build thật của từng kênh** |
| Phát hiện lớn nhất | (1) Bảng cỡ của **Huawei phụ thuộc loại gói** (APK ≠ HarmonyOS) — 2 bộ số "khác nhau" trước đây **không phải mâu thuẫn**. (2) **MS desktop ≥ 1366×768** trong khi game là dọc 720×1280 ⇒ phải capture **≥ 768×1366** (§4 W0-R1). (3) **Amazon chỉ nhận 7 cỡ ngang** ⇒ game dọc phải capture ở khung ngang (§4 W0-R2) |

---

## 1. Bảng slot — số đã xác minh

### 1.1 Microsoft Store — Windows PC (MSIX)
Nguồn: `https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/screenshots-and-images`
· truy cập **2026-10-27** · `STATIC_CONFIRMED`.

| Slot | Kích thước | Định dạng | Bắt buộc? | Nguyên văn / ghi chú |
|---|---|---|---|---|
| Screenshot desktop | **≥ 1366 × 768** (hỗ trợ tới 3840×2160) | **.png**, ≤ 50 MB, *"landscape or portrait orientation"* | **1 ảnh là đủ submit**; tối đa **10** desktop; FAQ khuyến nghị **5–8** | *"Keep critical visuals and text in the top two-thirds"*; *"Don't add additional logos, icons, or marketing messages"*; caption ≤ 200 ký tự; **mỗi ngôn ngữ upload riêng** |
| Store logo — 2:3 Poster art | **720×1080** hoặc **1440×2160** | .png ≤ 50 MB | Game: *"strongly recommend"*; **bắt buộc nếu có Xbox** | Được chứa tên game, tên ở **2/3 trên**, tương phản chữ **4.5:1** |
| Store logo — 1:1 Box art | **1080×1080** hoặc **2160×2160** | .png ≤ 50 MB | Game: khuyến nghị; **bắt buộc nếu có Xbox** | Không có poster thì ảnh này thành logo chính; tên ở 2/3 trên |
| Store logo — 1:1 App tile icon | **300 × 300** | .png ≤ 50 MB | *"strongly recommend"* — FAQ: *"A Store logo is mandatory for submission"* | Không upload thì Store dùng icon trong package ⇒ **nên làm 300²** |
| 16:9 Super hero art | **1920×1080** hoặc **3840×2160** | .png | Khuyến nghị cho mọi app; **bắt buộc cho game nếu có trailer** | *"must not include the product's title or other text"*; **không hiện UI app**, không ảnh thiết bị; chi tiết ở **giữa**, tránh **1/3 dưới** |
| Xbox: branded key art 584×800 · titled hero 1920×1080 · featured square 1080×1080 | — | — | Chỉ khi publish Xbox | **Không** phải kênh launch ⇒ không làm |
| Holographic 2400×1200 | — | — | Chỉ khi hỗ trợ HoloLens | Không làm |
| Trailer (≤15) | video 1920×1080 · thumbnail .png 1920×1080 | mp4/mov ≤ 2 GB | Tuỳ chọn | **Ngoài W0** (cần kỹ năng khác) |

> **Đọc đúng câu "1366 × 768 or larger":** trang chỉ nói "lớn hơn hoặc bằng 1366×768" và cho phép cả portrait. Với game dọc,
> cách duy nhất thoả **cả hai cách đọc** là capture ở **≥ 768 × 1366** (ví dụ **1080 × 1920**) — xem W0-R1.

### 1.2 Amazon Appstore — Fire tablet
Nguồn: `https://developer.amazon.com/docs/app-submission/appstore-details.html` · truy cập **2026-10-27** · `STATIC_CONFIRMED`.

| Slot | Kích thước | Định dạng | Bắt buộc? | Nguyên văn / ghi chú |
|---|---|---|---|---|
| Small icon | **114 × 114** | **PNG trong suốt** | **Bắt buộc** (2 icon) | Có thể là bản giản lược của icon lớn |
| Large icon | **512 × 512** | **PNG trong suốt** | **Bắt buộc** | *"Do not just scale up the PNG image of your icon"*; **không viền, không bo góc**, key art ra tới mép |
| Screenshot | **3–10 ảnh**, chỉ nhận: **800×480 · 1024×600 · 1280×720 · 1280×800 · 1920×1080 · 1920×1200 · 2560×1600** | PNG **hoặc** JPEG, *"(landscape or portrait mode)"* | **Bắt buộc, ≥ 3** | *"Screenshots should reflect the app experience on the **tablet**"*; *"Show logical progression"*; che dữ liệu cá nhân bằng dữ liệu giả |
| Promotional image | **1024 × 500** | PNG/JPEG ngang | Tuỳ chọn | Chữ **≥ 50 px** cách mép; đọc được khi thu còn **300 × 146**; **nên có tên app**; **không** giá/screenshot/rating/button |
| Video (≤5) | — | — | Tuỳ chọn | **Ngoài W0** |
| Fire TV assets | — | — | Chỉ khi Fire TV | **Deferred** — không làm |

> 7 cỡ cho phép đều là **cỡ ngang**; câu "landscape or portrait mode" nằm ở cột Format. Với game dọc, đây là điểm **chưa rõ**
> (`CONFLICTING`) — xem W0-R2.

### 1.3 Huawei AppGallery — ngoài Trung Quốc đại lục
Nguồn: `https://developer.huawei.com/consumer/en/doc/app/agc-help-app-material-requirement-0000001146534651`
· trang ghi *"Last updated: 2026-04-01"* · đọc **2026-10-27** · `STATIC_CONFIRMED`.

**Bảng cỡ phụ thuộc LOẠI GÓI** — đây là lý do trước đây thấy "hai bộ số khác nhau":

| | **APK** (mobile) | **App HarmonyOS** (mobile/tablet) | **PC/2-in-1** |
|---|---|---|---|
| Icon | **216² hoặc 512²**, PNG **≤ 2 MB** / WebP ≤ 100 KB, vuông | **216²**, PNG **≤ 500 KB** | 216², ≤ 500 KB |
| Screenshot | **3–8** ảnh · **800×450 hoặc 450×800** · PNG/JPG **≤ 2 MB** · cạnh **320–3840** | **3–5** ảnh · ngang **1280×720** (16:9) ≤ 5 MB · dọc **720×1280** (9:16) ≤ 2 MB | 3–5 ảnh 1280×720 |
| Video giới thiệu | Tuỳ chọn 1–3, 1280×720 / 720×1280 | Tuỳ chọn 1–3 | — |

**Áp dụng cho repo này:** game Unity đóng **APK** ⇒ dùng cột APK (**450×800** cho bản dọc).
Nếu sau này mở thêm listing **HarmonyOS** thì cần **720×1280** — cùng một capture gốc, chỉ khác bước export.

Bổ sung từ **Review guideline 1.9** (đã đọc trước đó): ≥ 3 screenshot khác nhau, đúng chiều, **không mờ/không méo/không nội dung
không liên quan**; 1.7–1.8: không badge gây nhầm, 1 icon lối tắt.

---

## 2. Việc phải làm — 4 lô, 27 slot, 35 h

| ID | Việc | Slot | Kích thước đích | Giờ |
|---|---|---|---:|---:|
| `L-ICON-01` | **Icon master** vẽ ở **1024²**, alpha | 1 | 1024×1024 | 6 |
| `L-ICON-02` | **7 export**: MS 300² · Amazon 512² · Amazon 114² · HMS 216² · HMS 512² · Windows `.ico` (16/24/32/48/256) · Android mipmap 48–192 | 7 | theo §1 | 2 |
| `L-ICON-03` | Review icon ở **48 px** và **114 px** (đọc được? có trùng app khác?) | 0 | — | 1 |
| `L-KEY-01` | **Hero 16:9 không chữ** (MS Super hero) | 1 | **3840×2160** (thu 1920×1080) | 5 |
| `L-KEY-02` | **Poster 2:3 có tên game** (MS) | 1 | **1440×2160** (thu 720×1080) | 4 |
| `L-KEY-03` | **Box 1:1 có tên game** (MS) | 1 | **2160×2160** (thu 1080²) | 4 |
| `L-KEY-04` | **Promo 1024×500** (Amazon, có tên app) | 1 | 1024×500 | 2 |
| `L-SHOT-01` | **Template + protocol chụp**: safe-area 3 tỉ lệ, checklist "không tutorial / không Premium / không giá" | 0 | — | 2 |
| `L-SHOT-02` | **15 screenshot**: capture + review + export đúng cỡ/format từng store | 15 | 5 MS (1080×1920) · 5 Amazon (1280×720) · 5 HMS (450×800) | 5 |
| `L-SHOT-03` | Review trên thiết bị thật + crop lại ảnh nào lệch safe-area | 0 | — | 2 |
| `L-QA` | **QA gói listing**: cỡ, format, alpha, mép, tên file, hero không chữ | 0 | — | 2 |
| **Σ** | | **27** | | **35** |

**Vì sao screenshot chỉ 5 h:** ảnh phải là **capture từ build thật** (`STORE_ASSETS` §3) — không vẽ lại art, chỉ đặt khung/safe-area
và export. "Vẽ" screenshot = ảnh sai sự thật, vi phạm chính sách store.

**Vì sao chọn bản lớn nhất của mỗi tỉ lệ (3840×2160, 1440×2160, 2160²):** MS cho **hoặc** nhỏ **hoặc** lớn — làm bản lớn rồi
thu nhỏ là 1 lần vẽ; làm cả hai là 2 lần. File `.ico` và mipmap là **asset build**, không phải slot listing, nhưng nằm cùng lô
vì dùng chung master.

### 2.1 Sổ slot máy đọc được — `w0-listing-slots.csv`

27 dòng, mỗi dòng **một file phải nộp**: `id · lot · store · slot · file · w · h · fmt · max_mb · alpha · required ·
artboard · notes · status`. Cột `w/h` là số để script so được; `max_mb` để trống = store **không nêu** giới hạn.

| Store / đích | slot | gồm |
|---|---:|---|
| **MS** | **9** | icon 300² · hero 3840×2160 · poster 1440×2160 · box 2160² · 5 screenshot 1080×1920 |
| **Amazon** | **8** | icon 512² · icon 114² · promo 1024×500 · 5 screenshot 1280×720 |
| **Huawei (APK)** | **7** | icon 216² · icon 512² · 5 screenshot 450×800 |
| **Build** (không phải listing) | **3** | master 1024² · `.ico` multi-res · mipmap 48–192 |
| **Σ** | **27** | |

**3 artboard gốc** sinh ra 27 file: ① `icon` (1 master → 5 file store + 2 build) · ② `key art A` (hero + promo) ·
③ `key art B` (poster + box). 15 screenshot là **capture**, không vẽ.

---

## 3. Chuẩn cho từng lô

### 3.1 Icon (1 master → 7 export)
- Vẽ ở **1024²**, nền **trong suốt** (Amazon bắt buộc alpha; HMS và MS nhận alpha).
- **Không** bo góc, **không** viền, **không** chữ, **không** badge — store tự cắt/bo theo hệ điều hành (Amazon: *"Do not include borders or rounded corners"*).
- Chủ thể: **1 tàu** dùng đúng recipe `ship` (§4.5 plan) — không dùng nguyên hình gốc, không trace.
- Đọc được ở **48 px**: nếu thu còn 48 px chỉ thấy 1 đốm màu ⇒ sai (Amazon cho phép làm bản giản lược riêng cho 114²).
- Tương phản nền–chủ thể ≥ 4,5:1 (cổng **G-C**, `tools/design-metrics.py`).
- Key art **ra tới mép** khung (Amazon), không để "viền trắng" quanh chủ thể.

### 3.2 Key art (2 bố cục gốc → 4 artboard)
- **Bố cục 1** (hero + promo): tàu player + cụm enemy + 1 lớp nền parallax — đúng 3 lớp của plan §4.7; **không UI**, không khung thiết bị.
- **Bố cục 2** (poster + box): tàu + silhouette boss, chừa vùng đặt tên ở **2/3 trên**.
- **Hero: tuyệt đối không chữ** (`STATIC_CONFIRMED`); poster/box/promo **có** tên, chữ tương phản **4.5:1**, cách mép **≥ 50 px**.
- Tránh chi tiết quan trọng ở **1/3 dưới** của cả 4 artboard (MS phủ gradient; Amazon hay crop).
- Palette **chỉ** §4.4 plan (ink-900 … gold, `paper`), 1 accent nóng/khung.

### 3.3 Screenshot (15 = 5 ảnh × 3 store)
- **Chỉ capture từ build thật, đúng kênh**: Windows → MS; Fire tablet → Amazon; APK → HMS. Không dùng ảnh 720×1496 của bản
  Android modded (`STORE_ASSETS` §2 cấm rõ), không upscale, không ghép giả.
- 5 ảnh theo **"logical progression"** (Amazon) = **"showcase key features"** (MS): ① gameplay sạch ② cụm enemy dày ③ boss
  ④ nâng cấp/shop ⑤ màn meta.
- **Không** có: tutorial overlay, Premium welcome modal, giá, rating, khung thiết bị giả, tính năng chưa có, thông tin cá nhân thật.
- Safe area: HUD + chi tiết quan trọng trong **2/3 trên**.
- Tên file: `<store>_<slot>_<w>x<h>.<ext>` + sidecar JSON (`source` · `build_id` · `device` · `license`).

### 3.4 Cỡ capture → cỡ export

| Store | Capture gốc | Export | Vì sao |
|---|---|---|---|
| MS | **1080 × 1920** (portrait, ≥ 768×1366) | 1080×1920 | thoả "1366×768 or larger" theo cả 2 cách đọc; chi tiết ở 2/3 trên |
| Amazon | **1280 × 720** (khung ngang, gameplay dọc đặt giữa) | 1280×720 | chỉ 7 cỡ ngang được nhận (W0-R2) |
| HMS (APK) | **1080 × 1920** | **450 × 800** (thu nhỏ) + 216² icon | size APK: 450×800, ≤ 2 MB; thu nhỏ hợp lệ, phóng to thì không |
| HMS (HarmonyOS, nếu mở sau) | 1080×1920 | 720×1280 | cùng capture, khác export |

---

## 4. Rủi ro — 5 mục, 2 mục cần user quyết

| # | Rủi ro | Nhãn | Tác động | Xử lý |
|---|---|---|---|---|
| **W0-R1** | Game **dọc 720×1280**, MS yêu cầu desktop **≥ 1366×768** | `CONFLICTING` (yêu cầu cỡ × tỉ lệ game) | Nếu capture 720×1280 → **không đạt**; MS không có screenshot hợp lệ | **Capture Windows ở 1080×1920** (mỗi cạnh ≥ min tương ứng) và **xác nhận trong Partner Center** lúc submit. Không cần đổi layout game; nếu Partner Center từ chối → **cần user quyết** (build landscape có viền, hoặc bỏ MS) |
| **W0-R2** | Amazon chỉ liệt kê **7 cỡ ngang**; game dọc | `CONFLICTING` | 5 slot Amazon | Chụp ở **1280×720 khung ngang** (gameplay dọc giữa, nền brand) — cách duy nhất không phải đoán; nếu Amazon từ chối → **cần user quyết** (bỏ Amazon, hoặc build landscape cho Fire) |
| **W0-R3** | Huawei: bảng cỡ **theo loại gói**; APK chỉ nhận **450×800**, ≤ **2 MB** | `STATIC_CONFIRMED` | 5 slot HMS | Export **450×800** từ capture 1080×1920; kiểm dung lượng ≤ 2 MB; nếu mở HarmonyOS thì export thêm 720×1280 |
| **W0-R4** | **Quyền IP chưa xác nhận** (Phase C USER-ONLY #3) | `STATIC_CONFIRMED` (STORE_ASSETS §2) | Chặn **toàn bộ** W0 | Không export/công bố trước khi user xác nhận; nếu không clear ⇒ thay bằng art user sở hữu |
| **W0-R5** | 3 store × 3 bộ cỡ/format ⇒ dễ export sai | `INFERRED` | 1 vòng làm lại ~2 h | `L-QA` + checklist §3; script so tên file với bảng §1 |

**Không nằm trong W0 (đừng cộng giờ vào đây):** trailer/video · Fire TV asset · Xbox asset · ảnh bản địa hoá theo ngôn ngữ
(MS **bắt buộc upload riêng từng ngôn ngữ** — ~0,3 h/ảnh/ngôn ngữ, làm sau) · rating questionnaire & data-safety form (Gate-6).

---

## 5. Cổng nghiệm thu W0 (`A-L`)

| Mã | Kiểm cái gì | Ngưỡng | Cách kiểm |
|---|---|---|---|
| **A-L1** | Đúng cỡ/format/dung lượng của **đúng store** | sai 1 slot = FAIL | script so danh sách file với §1 |
| **A-L2** | Hero 16:9 **không chữ** | 0 ký tự | mắt + OCR |
| **A-L3** | Safe area: chi tiết ở 2/3 trên; chữ cách mép ≥ 50 px | 100 % slot | mắt, 1 ảnh/lần |
| **A-L4** | Không logo bên thứ ba, không giá, không rating, không badge, không khung thiết bị | 0 vi phạm | checklist thủ công |
| **A-L5** | Đọc được ở thumbnail: icon 48 px · promo 300×146 · screenshot 20 % | 3/3 | mắt, 1 lượt/lô |
| **A-L6** | Screenshot là **capture build thật**, đúng kênh/thiết bị | 15/15 có `build_id` + `device` | đối chiếu sidecar |
| **A-L7** | Rights: mỗi file có `source`/`license`/`author` | 27/27 | sidecar JSON |
| **A-L8** | **2.5D**: icon + key art + promo qua 3 chỉ số style (`grad_stops` · `outline_px` · `detail`, dải §4.5b của plan) **và** có **bảng so kế cạnh gốc** (G-H) với contact sheet | máy + 1 bảng/lô | `measure_asset.py --dir … --class ui --style` (icon) · `--class bg` (key art) |

---

## 6. Cần user quyết (chặn, không phải việc của art)

1. **Windows**: chấp nhận **capture 1080×1920** + xác nhận trong Partner Center? Nếu không → bỏ MS hoặc build landscape
   (ảnh hưởng **5 slot + ~3 h**).
2. **Amazon**: chấp nhận **screenshot khung ngang 1280×720** cho game dọc? Nếu không → bỏ Amazon hoặc build landscape cho Fire.
3. **Rights** (Phase C USER-ONLY #3): xác nhận quyền tên `WindWings`, art gốc, nội dung — **trước** khi export file nào.
4. **Có làm trailer không**: nếu có thì phải có hero art + thumbnail 1920×1080 (ngoài 35 h này).

---

## 7. Cách nối vào planner

`docs/art-plan/art-planner.csv` — 4 dòng cuối `AP-0652`…`AP-0655`, `lane = LISTING`, `wave = W0`, `unit = listing`,
cột riêng **`h_w0`** (giờ) và **`w0_slots`** (slot). Mọi cột `h_*` khác = **0** để các tổng của scope B
(2.185 bản ghi · 801 kept · 1.578,4 h · 1.610,4 h gồm S0) **không đổi** — W0 là **sổ riêng**.

Kiểm lại: `Σ h_w0 = 35,0` · `Σ w0_slots = 27` · `Σ n_records` vẫn 2.185 · file vẫn 36 cột.
Danh sách 27 file: `w0-listing-slots.csv` (27 dòng = 8 icon + 4 key art + 15 screenshot).
