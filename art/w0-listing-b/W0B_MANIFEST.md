# W0B — Store listing art · Variant B ("Solar Neon Arcade-Pop")

**Vai:** Art-designer-B · **Nhánh:** `arena/eca8588b-windwings-space-shooter-game-p` · **Ngày:** 2026-10-27  
**CLAIM:** [PR #12 comment 6444169382](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6444169382)

**Nguồn đã fetch + đọc (refspec tường minh):**
- `docs/rollout/SESSION_PROMPTS.md` + `docs/rollout/STORE_ASSETS_AND_LISTING_DRAFT.md` @ `c21b265547df02911e63c06b31cb83a76c5f03f9` (nhánh `arena/20330d0e-windwings-space-shooter-game-p`) — brief 3 store + copy listing §4 + luật không claim ngoài build.
- `art/w0-listing/W0_MANIFEST.md` + `art/w0-listing/w0_exports.json` @ `4a65378e0365ead255a342196319ce2acb4eea72` (nhánh `arena/5438fec9-windwings-space-shooter-game-p`) — chuẩn **đúng 25 slot** (tên file + kích thước px + mode màu + luật chữ từng store đã verify tài liệu chính chủ ngày 2026-10-27; giữ nguyên 100%, không tự đổi số).
- `docs/art-plan/ART_REDRAW_PLAN.md` + `docs/art-plan/W0_LISTING_ASSETS.md` @ `b4229f9e915ee68b62895e5e4214e1561c7fa338` (nhánh `arena/1b836828-windwings-space-shooter-game-p`) — chuẩn metadata (`source`, `license`, `author`, `recipe`) và giao thức đo `val · val_std · dark · chroma`.
- Contact sheets tham chiếu bố cục chung (tàu đơn đọc rõ phía dưới · đội hình địch/boss phía trên) — **không** dùng, cắt, hay trace bất kỳ PNG/atlas gốc nào của GCenter.

---

## 1. Định hướng thẩm mỹ Variant B — Độc lập & đối chọi trực diện với Variant A

Variant B được thiết kế độc lập hoàn toàn với Variant A (*Ink & Ember* tối khí-quyển) để phục vụ đối chiếu A/B:

| Trục đối chiếu | Variant A (`5438fec9` — *Ink & Ember*) | **Variant B (`eca8588b` — *Solar Neon Arcade-Pop*)** |
|---|---|---|
| **Tông sáng (`val`)** | Tối sâu khí-quyển (`0.088 – 0.215`) | **Sáng rực năng lượng cao (`0.649 – 0.871`)** |
| **Tỉ lệ tối (`dark`)** | Cao (`0.551 – 0.927`) | **Cực thấp, sạch bùn tối (`0.000 – 0.038`)** |
| **Độ tươi màu (`chroma = S·V`)** | Tiết chế đơn sắc (`0.042 – 0.116`) | **Arcade-pop tương phản cao (`0.265 – 0.608`)** |
| **Không gian & ánh sáng** | Khoảng không đen slate + 1 điểm nhấn cam | **Bầu trời quỹ đạo lam-ngọc đầy nắng, mây tầng sáng, hào quang neon** |
| **Tàu & Boss xuyên suốt** | Khai thẳng tàu lệch nhẹ giữa các master | **Đồng nhất 100% thiết kế tàu chính & boss trên cả 9 master** |
| **Wordmark `WindWings`** | Chữ phẳng DejaVu trắng + gạch cam | **Logo nghiêng khí-động học 2× supersampled, chuyển sắc vàng-cam mặt trời + viền navy + dải băng tốc độ neon cyan** |

### Bảng màu & công thức tô riêng của Variant B (`recipe`)

- **Bảng màu chủ đạo (*Solar Neon Arcade-Pop*):**
  - `sky-cerulean` `#1677FF` / `nebula-turquoise` `#00E5FF` — nền trời quỹ đạo & tầng mây rực sáng
  - `hull-pearl` `#F4F8FF` / `hull-azure` `#1E6BFF` — giáp trắng ngọc trai & xanh cobalt điện của tàu chính
  - `solar-gold` `#FFDC18` / `arcade-tangerine` `#FF6D00` — sọc cánh vàng, vật phẩm thưởng sao/kim cương, tâm vụ nổ
  - `neon-cyan` `#00F2FF` — bốn luồng laser tàu chính, vòng khiên năng lượng, siêu pháo plasma
  - `hyper-magenta` `#FF1E8A` / `royal-violet` `#7B2CBF` — giáp cơ-sinh-học của Boss/địch & màn đạn quạt
  - `navy-outline` `#060E2E` — nét cel-shading xanh đêm sắc gọn (thay viền đen đục)

- **Các `recipe` gắn trong metadata từng slot:**
  - `b_bg_solar_sky`: bầu trời quỹ đạo xanh lam-ngọc + mây tầng rực nắng + chân trời hành tinh sáng
  - `b_ship_pearl_azure`: tiêm kích cánh xuôi trắng ngọc trai – xanh cobalt, 2 sọc vàng trên cánh, buồng lái cyan, 4 pháo cánh, 2 động cơ lửa vàng
  - `b_boss_crimson_violet`: chiến hạm boss đỏ hồng – tím hoàng gia viền vàng + lõi năng lượng phát sáng
  - `b_enemy_crimson_wave`: biên đội tiêm kích địch chữ V đỏ-tím + pháo tháp cơ khí
  - `b_drone_item_gold`: cặp drone hộ tống tròn trắng-xanh-vàng đối xứng + chuỗi sao/kim cương vàng rơi
  - `b_bullet_neon_fan`: màn đạn quạt đối xứng hồng neon & vàng hổ phách đọc rõ trên nền sáng
  - `b_fx_neon_pop` / `b_fx_hyper_beam` / `b_fx_starburst_boom`: tia siêu plasma trắng-cyan, vòng xung kích & nổ sao cam-hồng arcade
  - `b_wordmark_solar_chrome`: chữ `WindWings` nghiêng tốc độ, viền `#060E2E`, hào quang `#00F2FF`, dải băng `#08143E` đảm bảo tương phản > 8:1 (vượt chuẩn 4.5:1)

---

## 2. Chuẩn kỹ thuật 25 slot — giữ nguyên 100% theo bảng đã verify của Variant A

Toàn bộ tên file, kích thước pixel, hệ màu (`RGB`/`RGBA`) và quy tắc chữ/vùng an toàn giữ giống hệt `art/w0-listing/W0_MANIFEST.md` (đã đối chiếu tài liệu chính chủ Microsoft Learn · Amazon Developer · Huawei Developer ngày **2026-10-27**):

- **Microsoft Store (8 file):** `ms_tile_icon_300x300.png` (không chữ) · `ms_box_art_1080x1080.png` (tên ở 2/3 trên, 1/3 dưới sạch chữ) · `ms_poster_art_720x1080.png` (tên ở 2/3 trên, tương phản ≥4.5:1, 1/3 dưới sạch) · `ms_super_hero_1920x1080.png` (cấm chữ/UI, hành động ở 2/3 trên) · `ms_screenshot_1..4_1920x1080.png` (khung dọc pillarbox khí-quyển sáng, không chữ marketing).
- **Amazon Appstore (7 file):** `amazon_icon_large_512x512.png` + `amazon_icon_small_114x114.png` (`RGBA`, tràn cạnh, không bo góc/viền, không chữ) · `amazon_promo_1024x500.png` (có tên `WindWings`, lề chữ ≥50px mọi phía, đọc rõ khi thu `300×146`) · `amazon_screenshot_1..4_800x1280.png` (không chữ marketing).
- **Huawei AppGallery (10 file):** `huawei_icon_512x512.png` (≤2 MB) + `huawei_icon_216x216.png` (≤500 KB) · `huawei_screenshot_1..4_450x800.png` (bảng APK, ≤2 MB) + `huawei_screenshot_1..4_720x1280.png` (bảng HarmonyOS, ≤2 MB). Không tạo promo Huawei (mobile không có slot).

---

## 3. Checklist xuất bản & Metadata từng asset (25 slot + 9 masters + 1 preview)

- **Metadata chung cho cả 25 asset:**
  - `license`: `"chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)"`
  - `author`: `"arena/eca8588b-windwings-space-shooter-game-p"`
  - `source` & `recipe` chi tiết từng file: xem bảng dưới và file máy-đọc [`w0b_exports.json`](w0b_exports.json).
- **Ảnh ghép toàn bộ 25 slot + legibility probes:** [`preview/w0_contact_sheet.png`](preview/w0_contact_sheet.png) (`1540×3096`, `3139 KB`).
- **9 master gốc không chữ (`masters/`):** `icon_master.png` (`1024×1024`) · `box_master.png` (`1024×1024`) · `poster_master.png` (`848×1264`) · `hero_master.png` (`1376×768`) · `promo_master.png` (`1376×768`) · `scene_s1_wave_master.png` · `scene_s2_boss_master.png` · `scene_s3_drone_master.png` · `scene_s4_beam_master.png` (`768×1376` ×4). Chạy lại `python3 build_w0b.py && python3 make_preview_b.py` tái tạo chính xác 100% bộ xuất.

| # | File | px | Mode | Dung lượng | Source master | Recipe | val | val_std | dark | chroma |
|---:|---|---:|:---:|---:|---|---|---:|---:|---:|---:|
| 1 | `microsoft-store/ms_tile_icon_300x300.png` | 300x300 | RGB | 189 KB | `masters/icon_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_fx_starburst_boom` | 0.846 | 0.227 | 0.034 | 0.597 |
| 2 | `microsoft-store/ms_box_art_1080x1080.png` | 1080x1080 | RGB | 1815 KB | `masters/box_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_boss_crimson_violet + b_fx_neon_pop + b_wordmark_solar_chrome` | 0.761 | 0.258 | 0.038 | 0.529 |
| 3 | `microsoft-store/ms_poster_art_720x1080.png` | 720x1080 | RGB | 1229 KB | `masters/poster_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_boss_crimson_violet + b_fx_neon_pop + b_wordmark_solar_chrome` | 0.780 | 0.261 | 0.034 | 0.550 |
| 4 | `microsoft-store/ms_super_hero_1920x1080.png` | 1920x1080 | RGB | 2972 KB | `masters/hero_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_boss_crimson_violet + b_fx_neon_pop` | 0.818 | 0.210 | 0.013 | 0.570 |
| 5 | `microsoft-store/ms_screenshot_1_1920x1080.png` | 1920x1080 | RGB | 1328 KB | `masters/scene_s1_wave_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_enemy_crimson_wave + b_fx_neon_pop` | 0.691 | 0.133 | 0.000 | 0.366 |
| 6 | `microsoft-store/ms_screenshot_2_1920x1080.png` | 1920x1080 | RGB | 1969 KB | `masters/scene_s2_boss_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_boss_crimson_violet + b_bullet_neon_fan` | 0.649 | 0.151 | 0.000 | 0.265 |
| 7 | `microsoft-store/ms_screenshot_3_1920x1080.png` | 1920x1080 | RGB | 1594 KB | `masters/scene_s3_drone_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_drone_item_gold + b_fx_neon_pop` | 0.657 | 0.159 | 0.000 | 0.335 |
| 8 | `microsoft-store/ms_screenshot_4_1920x1080.png` | 1920x1080 | RGB | 1401 KB | `masters/scene_s4_beam_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_fx_hyper_beam + b_fx_starburst_boom` | 0.696 | 0.140 | 0.000 | 0.359 |
| 9 | `amazon-appstore/amazon_icon_large_512x512.png` | 512x512 | RGBA | 553 KB | `masters/icon_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_fx_starburst_boom` | 0.844 | 0.227 | 0.037 | 0.591 |
| 10 | `amazon-appstore/amazon_icon_small_114x114.png` | 114x114 | RGBA | 36 KB | `masters/icon_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_fx_starburst_boom` | 0.851 | 0.202 | 0.009 | 0.608 |
| 11 | `amazon-appstore/amazon_promo_1024x500.png` | 1024x500 | RGB | 842 KB | `masters/promo_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_boss_crimson_violet + b_fx_neon_pop + b_wordmark_solar_chrome` | 0.762 | 0.267 | 0.032 | 0.530 |
| 12 | `amazon-appstore/amazon_screenshot_1_800x1280.png` | 800x1280 | RGB | 1322 KB | `masters/scene_s1_wave_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_enemy_crimson_wave + b_fx_neon_pop` | 0.855 | 0.151 | 0.008 | 0.562 |
| 13 | `amazon-appstore/amazon_screenshot_2_800x1280.png` | 800x1280 | RGB | 1738 KB | `masters/scene_s2_boss_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_boss_crimson_violet + b_bullet_neon_fan` | 0.820 | 0.189 | 0.013 | 0.464 |
| 14 | `amazon-appstore/amazon_screenshot_3_800x1280.png` | 800x1280 | RGB | 1504 KB | `masters/scene_s3_drone_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_drone_item_gold + b_fx_neon_pop` | 0.835 | 0.169 | 0.011 | 0.535 |
| 15 | `amazon-appstore/amazon_screenshot_4_800x1280.png` | 800x1280 | RGB | 1437 KB | `masters/scene_s4_beam_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_fx_hyper_beam + b_fx_starburst_boom` | 0.871 | 0.150 | 0.005 | 0.537 |
| 16 | `huawei-appgallery/huawei_icon_512x512.png` | 512x512 | RGB | 494 KB | `masters/icon_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_fx_starburst_boom` | 0.844 | 0.227 | 0.037 | 0.591 |
| 17 | `huawei-appgallery/huawei_icon_216x216.png` | 216x216 | RGB | 104 KB | `masters/icon_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_fx_starburst_boom` | 0.847 | 0.223 | 0.029 | 0.601 |
| 18 | `huawei-appgallery/huawei_screenshot_1_450x800.png` | 450x800 | RGB | 520 KB | `masters/scene_s1_wave_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_enemy_crimson_wave + b_fx_neon_pop` | 0.848 | 0.164 | 0.016 | 0.563 |
| 19 | `huawei-appgallery/huawei_screenshot_1_720x1280.png` | 720x1280 | RGB | 1188 KB | `masters/scene_s1_wave_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_enemy_crimson_wave + b_fx_neon_pop` | 0.848 | 0.151 | 0.007 | 0.562 |
| 20 | `huawei-appgallery/huawei_screenshot_2_450x800.png` | 450x800 | RGB | 721 KB | `masters/scene_s2_boss_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_boss_crimson_violet + b_bullet_neon_fan` | 0.815 | 0.208 | 0.031 | 0.469 |
| 21 | `huawei-appgallery/huawei_screenshot_2_720x1280.png` | 720x1280 | RGB | 1583 KB | `masters/scene_s2_boss_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_boss_crimson_violet + b_bullet_neon_fan` | 0.814 | 0.189 | 0.012 | 0.465 |
| 22 | `huawei-appgallery/huawei_screenshot_3_450x800.png` | 450x800 | RGB | 586 KB | `masters/scene_s3_drone_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_drone_item_gold + b_fx_neon_pop` | 0.828 | 0.183 | 0.022 | 0.537 |
| 23 | `huawei-appgallery/huawei_screenshot_3_720x1280.png` | 720x1280 | RGB | 1340 KB | `masters/scene_s3_drone_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_drone_item_gold + b_fx_neon_pop` | 0.830 | 0.166 | 0.010 | 0.538 |
| 24 | `huawei-appgallery/huawei_screenshot_4_450x800.png` | 450x800 | RGB | 579 KB | `masters/scene_s4_beam_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_fx_hyper_beam + b_fx_starburst_boom` | 0.865 | 0.163 | 0.014 | 0.540 |
| 25 | `huawei-appgallery/huawei_screenshot_4_720x1280.png` | 720x1280 | RGB | 1304 KB | `masters/scene_s4_beam_master.png` | `b_bg_solar_sky + b_ship_pearl_azure + b_fx_hyper_beam + b_fx_starburst_boom` | 0.865 | 0.149 | 0.005 | 0.539 |

**Kiểm chứng tự động các cổng kỹ thuật (`build_w0b.py`):**
- **Cổng khớp chuẩn A/B:** 25/25 tên file + `width×height` + mode (`RGB`/`RGBA`) khớp tuyệt đối `art/w0-listing/w0_exports.json` của A ✔
- **Cổng dung lượng:** nặng nhất `ms_super_hero_1920x1080.png` = `2.972 KB` (≤ 50 MB); `huawei_icon_216x216.png` = `104 KB` (≤ 500 KB); mọi screenshot/icon Huawei ≤ `1.583 KB` (≤ 2 MB) ✔
- **Cổng chữ & vùng an toàn:** chữ `WindWings` chỉ có ở đúng 3 slot (`ms_box_art_1080x1080` y ≤ 698px < 720px; `ms_poster_art_720x1080` y ≤ 520px < 720px; `amazon_promo_1024x500` lề chữ mọi cạnh ≥ 95px > 50px, đọc rõ ở `300×146`); 22 slot còn lại **hoàn toàn không chữ, không số, không UI giả** ✔

---

## 4. Copy listing — nguyên văn `STORE_ASSETS_AND_LISTING_DRAFT.md` §4 (không thêm claim)

Tên hiển thị trong 3 ảnh cho phép: **WindWings** *(working title — chờ xác nhận quyền + khả dụng tên trên từng store, draft §4)*.

- **Microsoft Store — Windows PC (premium, no ads):**
  - *Short:* “A premium, ad-free vertical arcade shooter. Pilot a starfighter, weave through enemy fire, and face boss encounters.”
  - *Long:* “Take command of a starfighter in a vertically scrolling arcade shooter. Dodge enemy formations, fire through incoming waves, and face boss encounters. The planned Windows edition is a premium, ad-free release. No paid loot boxes.”
- **Amazon Appstore — Fire tablet (free-to-play, rewarded-first):**
  - *Short:* “Pilot a starfighter through fast vertical battles. Dodge enemy fire, clear formations, and challenge boss encounters. Optional rewarded video.”
  - *Long:* “Launch into a vertical arcade space shooter. Pilot your starfighter through enemy formations, dodge incoming fire, and take on boss encounters. The planned Fire tablet release is free to play, with optional, opt-in rewarded video ads. No paid loot boxes.”
- **Huawei AppGallery — ngoài TQ đại lục (free-to-play, rewarded-first):**
  - *Short/Long:* như Amazon, câu cuối phần Long: “The planned AppGallery release is free to play, with optional, opt-in rewarded video ads. No paid loot boxes.”
- **4 cảnh gameplay concept (S1–S4, không đốt chữ vào ảnh):**
  - **S1:** Đội hình tiêm kích địch sóng đầu + đạn laser cyan kép (“Pilot a starfighter through fast vertical battles.”)
  - **S2:** Chiến hạm Boss + màn đạn quạt neon hồng/hổ phách (“Face boss encounters.”)
  - **S3:** Hai drone hộ tống đối xứng + chuỗi vật phẩm sao/kim cương vàng (“Dodge enemy fire, clear formations.”)
  - **S4:** Siêu pháo plasma xuyên tâm + nổ dây chuyền (“Weave through enemy fire.”)

---

## 5. Giới hạn khai thẳng trước khi chọn A/B

1. **Screenshot S1–S4 là khung CONCEPT định hướng thẩm mỹ**, chưa phải ảnh chụp từ bản build Godot 4.x thực tế. Trước khi nộp store phải chụp lại từ release build từng nền tảng (Windows / Fire tablet / HMS) theo đúng `STORE_ASSETS_AND_LISTING_DRAFT.md` §3 & §5.4 — **không upload nguyên trạng lên store**.
2. **Quyền tên & IP chưa chốt (Phase C USER-ONLY #3):** `WindWings` là working title; toàn bộ 9 master trong `masters/` là art mới 100%, không chứa bất kỳ texel/atlas nào của GCenter, nhưng vẫn ghi `license = chờ user xác nhận quyền tên/art`.
3. **Wordmark placeholder:** sử dụng font giấy phép mở `DejaVuSans-Bold` dựng hiệu ứng vector 2× làm placeholder thương hiệu; typeface cuối cùng thuộc quyết định brand của user.
4. **Phạm vi dừng đúng lệnh:** session này chỉ giao trọn gói **25 slot W0-listing + preview + masters**, **không** vẽ sang W1 in-game trước khi có kết quả chọn A/B.
