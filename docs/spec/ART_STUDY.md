# ART_STUDY — học thiết kế **từ mẫu gốc**, bằng số

> Nguồn: 42 contact sheet (`docs/assets/contact-sheets/`) dựng từ chính atlas trong APK,
> đối chiếu `docs/assets/sprites-index.csv` (2.197 sprite). Tool: `tools/art-study.py`.
> Kết quả từng sprite: `docs/assets/art-study.csv` (**2.112** dòng). Claim **AO1**.
>
> Cách dùng: mẫu gốc là **nguồn chuẩn để đo** (tỉ lệ, ngân sách màu, độ chênh sáng, độ lấp ô).
> Art của bản mới là **hình vẽ mới** dựng theo đúng các số đó — học bằng số, không cần chép hình.

---

## 1. Đo cái gì, trên bao nhiêu

| Thành phần | Cách đo |
|---|---|
| **Số màu** | gom màu theo lưới 32 bậc/kênh, đếm số ô màu khác nhau trong sprite |
| **Bão hoà / sáng** | trung bình `S` và `V` trên pixel của sprite |
| **Độ chênh sáng** (`val_std`) | độ lệch chuẩn `V` trong sprite ⇒ **độ sâu của gradient bóng** |
| **`dark_share`** | tỉ lệ pixel gần đen (`max(R,G,B) < 45`) ⇒ dấu vết **outline / viền tối** |
| **`fill`** | diện tích sprite / diện tích ô atlas ⇒ mật độ đóng gói |
| **`aspect`** | rộng:cao của **hộp bao** sprite |

**2.112** sprite · **12** nhóm · trung vị **55** màu · bão hoà trung vị **0,483** (claim **AO1**).

Tách nền bằng **flood fill từ viền ô** trên 2 màu caro của contact sheet. Vì một trong hai màu
caro là gần đen, cách này giữ được mảng đen **nằm trong** sprite (nếu chỉ so màu thì outline bị ăn).

---

## 2. Bảng tổng hợp — 12 nhóm

| nhóm | n | **màu** (p25·p50·p75) | bão hoà | sáng | **gradient** | `dark` | **fill** | aspect |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| `unclassified` | 1.542 | 40 · **57** · 83 | 0,53 | 0,60 | 0,21 | 0,002 | 0,27 | 0,97 |
| `atlas` (cả trang) | 132 | 41 · **80** · 159 | 0,33 | 0,42 | 0,21 | 0,057 | 0,39 | 1,00 |
| `background` | 108 | 31 · **37** · 54 | 0,30 | **0,33** | **0,12** | 0,074 | 0,41 | 1,00 |
| `fx` | 80 | 30 · **35** · 52 | **0,12** | 0,72 | 0,24 | 0,015 | **0,08** | 0,91 |
| `ui` | 73 | 40 · **52** · 85 | 0,29 | 0,41 | 0,26 | 0,095 | **0,87** | 1,00 |
| `bullet` | 67 | 24 · **39** · 53 | 0,53 | **0,26** | 0,24 | **0,493** | 0,22 | 1,03 |
| `bosses` | 32 | 116 · **130** · 148 | 0,58 | 0,54 | 0,21 | 0,009 | 0,31 | 0,99 |
| `enemy` | 31 | 15 · **30** · 57 | 0,53 | **0,76** | 0,23 | 0,008 | **0,10** | 0,86 |
| `ships` | 25 | 112 · **136** · 157 | 0,50 | 0,55 | 0,22 | 0,017 | 0,28 | 0,96 |
| `drones` | 13 | 100 · **114** · 126 | 0,55 | 0,66 | 0,23 | 0,012 | 0,24 | 1,00 |
| `font` | 5 | 2 · **2** · 13 | 0,00 | 0,25 | 0,09 | 0,405 | 0,03 | 1,11 |
| `items` | 4 | 49 · **70** · 81 | **0,70** | 0,64 | 0,22 | 0,009 | 0,17 | 1,12 |
| **toàn bộ** | **2.112** | — | **0,483** | **0,570** | **0,214** | 0,005 | 0,277 | 0,985 |

---

## 3. Sáu điều **đo được** (không phải cảm nhận)

### 3.1 "Độ chi tiết" tỉ lệ với **tầm quan trọng của chủ thể**

`enemy` **30** màu → `drones` **114** → `bosses` **130** → `ships` **136**. Chênh **≥ 4×**.

⇒ Luật dùng được: sprite nhỏ/nền (≤ 150 px) **30–60** màu; chủ thể chính (tàu, boss, drone)
**110–160** màu. Đừng vẽ boss 30 màu (chìm) hay enemy 130 màu (nhiễu).

### 3.2 Độ sâu gradient là **hằng số** — 0,21 – 0,26 cho **mọi** nhóm

`val_std` gần như không đổi giữa enemy (0,23), ships (0,22), bosses (0,21), UI (0,26), fx (0,24).
Chỉ nền (0,12) và font (0,09) là phẳng hơn.

⇒ Đây là "gradient bóng" của bản gốc, **định lượng**: mỗi khối tô bóng lệch khoảng **1/5 dải sáng**,
áp **đồng nhất** cho mọi loại sprite. Đây là thứ dễ tái tạo nhất mà vẫn giữ đúng "chất".

### 3.3 Thứ bậc **sáng** (ai nổi trước)

`enemy 0,76` > `fx 0,72` > `drones 0,66` > `items 0,64` > `ships 0,55` ≈ `bosses 0,54` >
`atlas 0,42` ≈ `ui 0,41` > `background 0,33` > `bullet 0,26`.

⇒ Nền **luôn tối nhất**; sinh vật **sáng nhất**; **UI ngang đồ hoạ trang trí, không ngang nhân vật**.
`bullet` là **ngoại lệ có chủ đích**: thân tối (0,26) + viền sáng ⇒ đạn nổi trên nền tối mà không
chói. Làm đạn sáng đều là sai công thức này.

### 3.4 Thứ bậc **bão hoà** (ai được rực)

`items 0,70` > `bosses 0,58` > `drones 0,55` ≈ `enemy 0,53` ≈ `bullet 0,53` > `ships 0,50` >
`atlas 0,33` ≈ `background 0,30` ≈ `ui 0,29` > **`fx 0,12`**.

⇒ **UI và nền bị hạ bão hoà ~một nửa** so với nhân vật ⇒ mắt luôn quay về gameplay.
**FX gần như trắng** (0,12 = gần như vô sắc): hiệu ứng sáng bằng **độ sáng**, không bằng màu.

### 3.5 "Outline đen dày" **không** phải luật của sprite

`dark_share` của ships **0,017** · bosses **0,009** · enemy **0,008** — tức **~1 %** pixel gần đen,
không đủ cho một viền 3–4 px trên ô 150 px. Chỉ **bullet (0,493)** và **font (0,405)** là tối-dominant,
và ở hai nhóm đó lý do khác (đạn phát sáng trên nền tối / font trắng trên nền trong).

⇒ `ASSETS.md` §1.1 đang mô tả bản gốc "outline đen dày 3–4 px" — **số không ủng hộ**. Viền dày
(nếu có) nằm ở **một số icon UI**, không phải toàn bộ sprite. Ghi lại để đừng thiết kế theo niềm tin.

### 3.6 Đóng gói: **`fill`** quyết định atlas

`ui 0,87` (lấp gần kín ô) · `background 0,41` · `atlas 0,39` · `ships 0,28` · `bullet 0,22` ·
`enemy 0,10` · `fx 0,08`.

⇒ Nếu đóng atlas theo lưới đều (như contact sheet), **hiệu suất thật** chỉ ~28 % diện tích: một nửa
trang atlas là trong suốt. Bản mới nên **pack theo hình bao** (tight packing) cho `fx`, `enemy`,
`bullet`; chỉ `ui` mới cần ô đều.

---

## 4. Bảng luật cho **bản mới** (mỗi dòng kiểm được bằng tool)

| Luật | Số | Kiểm bằng |
|---|---|---|
| Màu: sprite phụ | **30 – 60** | `colors` |
| Màu: chủ thể chính (tàu/boss/drone) | **110 – 160** | `colors` |
| Gradient bóng mọi sprite | `val_std` **0,20 – 0,26** | `val_std` |
| Nền tối hơn nhân vật | `val` nền **≤ 0,35**, nhân vật **0,50 – 0,80** | `val` |
| UI không tranh với gameplay | `sat` UI **≤ 0,30**, nhân vật **0,50 – 0,60** | `sat` |
| FX sáng bằng độ sáng | `sat` fx **≤ 0,15**, `val` **≥ 0,65** | `sat`, `val` |
| Đạn: thân tối + viền sáng | `val` **0,22 – 0,30**, `dark` **≥ 0,35** | `val`, `dark_share` |
| Không viền đen toàn cục | `dark_share` sprite thường **≤ 0,03** | `dark_share` |
| Pack atlas theo hình bao cho fx/enemy/bullet | `fill` **0,08 – 0,28** ⇒ đừng dùng lưới đều | `fill` |

Chạy lại: `python3 tools/art-study.py --csv docs/assets/art-study.csv` → so bảng §2 của bản mới
với bảng §2 của mẫu gốc. Lệch khỏi cột nào thì sửa **art**, không sửa bảng.

---

## 5. Giới hạn của phép đo (ghi để không ảo tưởng)

- Contact sheet là **JPEG 150 px/ô**, không phải PNG gốc ⇒ sai số nén, và sprite lớn bị **thu nhỏ**,
  nên `dark_share` và `colors` là **cận dưới** so với asset thật.
- Một trong hai màu caro là gần đen ⇒ pixel đen **nằm trên ô caro đen** vẫn có thể bị tính là nền;
  `dark_share` vì thế **chỉ đọc được theo hướng "thấp là chắc chắn thấp"**.
- `colors` phụ thuộc lưới gom 32 bậc; so sánh **giữa các nhóm** là hợp lệ, so **tuyệt đối** thì không.
- 4 sprite `items` và 5 `font` ⇒ mẫu quá nhỏ, chỉ dùng để tham khảo.

---

## 6. Nối với phần đã có

- Bố cục màn/khung hình, ngân sách accent theo **khung**, vignette khung thưởng: `VISUAL_DESIGN.md`.
- Palette **của bản mới** (không lấy màu gốc): `ASSETS.md` §1.2 "Ink & Ember".
- Phân loại 2.197 asset (nhóm nào chưa rõ): `ASSET_TRIAGE.md`.
