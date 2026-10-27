# W0 — Store listing art (lô 1, chờ user duyệt)

**Vai:** Art-designer · **Nhánh:** `arena/5438fec9-windwings-space-shooter-game-p` · **Ngày:** 2026-10-27
**CLAIM:** [PR #12 comment 6443346351](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6443346351)
**Nguồn đã fetch + đọc (refspec tường minh):**
- `docs/art-plan/ART_REDRAW_PLAN.md` + `art-planner.csv` @ `971a7eea8` (nhánh `1b836828`) — palette **Ink & Ember** §4.4, 9 công thức tô §4.5, chuẩn §4.6–4.7, giao thức đo §4.9. *Không sửa plan.*
- `docs/rollout/STORE_ASSETS_AND_LISTING_DRAFT.md` + `SESSION_PROMPTS.md` @ `8777bfa3e` (nhánh `20330d0e`) — brief 3 store + copy §4; ACK nhận brief từ `a5a74747` (STATUS:XONG `6443272336`).
- Contact sheets `ships-01 / bosses-01 / background-01` + capture `live_1_Game.png` (nhánh `20330d0e`) — **chỉ tham chiếu bố cục** (tàu đơn đọc rõ trên nền vũ trụ · boss trên / tàu dưới). **Không** dùng PNG/atlas gốc làm asset, không trace.

**Metadata mỗi asset (plan §4.7):** `source` = master trong `masters/` (art mới sinh bằng AI theo prompt bám palette/recipe, hoàn thiện xác định bằng `build_w0.py`) · `license` = nội bộ dự án, chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3) · `author` = Art-designer `arena/5438fec9` · `recipe` = nền `bg`, tàu `ship`, đạn `bullet`, drone `drone`, boss `boss` (plan §4.5).

---

## 1. Kích thước kỹ thuật — đã tra nguồn CHÍNH CHỦ (draft §3 để UNVERIFIED)

Draft §3/§6 ghi rõ px/count/format từng store là **UNVERIFIED** và cấm thay bằng số nhớ/bên thứ ba. Lô này tra lại từ tài liệu chính chủ, truy cập **2026-10-27**:

| Store / slot | Yêu cầu chính chủ | Nguồn |
|---|---|---|
| **Microsoft** 1:1 App tile icon (store logo) | **300×300** PNG, ≤50 MB, strongly recommended | [learn.microsoft.com — MSIX screenshots-and-images](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/screenshots-and-images) |
| **Microsoft** 1:1 Box art | **1080×1080** hoặc 2160×2160 PNG; được ghi tên game; không chữ/hình chính ở 1/3 dưới | như trên |
| **Microsoft** 2:3 Poster art | **720×1080** hoặc 1440×2160 PNG; được ghi tên (tương phản 4.5:1); 1/3 dưới sạch | như trên |
| **Microsoft** 16:9 Super hero art | **1920×1080** hoặc 3840×2160 PNG; **cấm** tên game/chữ; chi tiết chính ở giữa, tránh 1/3 dưới | như trên |
| **Microsoft** Desktop screenshots | PNG, **≥1366×768**, hỗ trợ tới 3840×2160; 1 bắt buộc, ≤10, khuyến nghị ≥4; không logo/thông điệp marketing; hình chính ở 2/3 trên | như trên |
| **Amazon** icon nhỏ / lớn | **114×114** và **512×512**, PNG (transparent); key art tràn cạnh, không bo góc/viền | [developer.amazon.com — Add Appstore Details](https://developer.amazon.com/docs/app-submission/appstore-details.html) |
| **Amazon** screenshots (tablet) | 3–10 ảnh PNG/JPEG (landscape **hoặc portrait**); cỡ cho phép: 800×480 · 1024×600 · **1280×800** · 1920×1080 · 1920×1200 · 2560×1600 | như trên |
| **Amazon** Promotional Image | **1024×500** PNG/JPEG landscape; **phải** có tên app; chữ cách mép ≥50px; đọc rõ ở 300×146 | như trên |
| **Huawei** icon (APK mobile) | **216×216 hoặc 512×512** PNG ≤2 MB (bảng HarmonyOS: 216×216 PNG ≤500 KB) | [developer.huawei.com — Specifications for App Visual Assets](https://developer.huawei.com/consumer/en/doc/app/agc-help-app-material-requirement-0000001146534651) (cập nhật 2026-04-01) |
| **Huawei** screenshots (APK mobile) | 3–8 ảnh **800×450 hoặc 450×800** PNG/JPG ≤2 MB; cạnh 320–3840px (bảng HarmonyOS: portrait **720×1280**, 3–5) | như trên |
| **Huawei** promo/feature (mobile) | **Không có slot** trong bảng mobile APK/HarmonyOS (chỉ Vision/telematics có) → **N/A, không bịa** | như trên |

**Quyết định suy luận (khai rõ để user/verifier bắt bẻ):**
1. **Amazon screenshot 800×1280** = đọc portrait của cỡ cho phép `1280×800` (docs ghi format “landscape or portrait mode”; game là shmup dọc). Nếu console Fire bắt landscape, xuất lại từ cùng master sang 1920×1200 pillarbox trong 1 bước (`build_w0.py`).
2. **Huawei giao 2 bộ screenshot**: 450×800 (đúng chữ bảng APK) + 720×1280 (đúng chữ bảng HarmonyOS) — cùng 4 cảnh, sinh từ cùng master, không tốn thêm art.
3. **Microsoft screenshot 1920×1080** = khung dọc pillarbox trên nền mờ của chính cảnh (cách bản Windows của shmup dọc trình bày thật), không chữ marketing theo luật slot.
4. **Không làm**: trailer + thumbnail MS 1920×1080 (chưa có trailer), slot Xbox/Holographic (ngoài launch target), Fire TV assets (draft hoãn), Huawei promo (không có slot).

## 2. Checklist xuất bản — 25 file / 3 store (đo §4.9 rút gọn trên khung đặc)

Số đo `val · val_std · dark · chroma` tính toàn khung (ảnh listing không alpha — khai adapt từ §4.9; dải tham chiếu nền của plan §4.3: val 0,15–0,25 · dark ≥0,55 · chroma ≤0,12). Chi tiết máy-đọc: [`w0_exports.json`](w0_exports.json). Xem toàn bộ: [`preview/w0_contact_sheet.png`](preview/w0_contact_sheet.png).

| File | px | Dung lượng | val | val_std | dark | chroma |
|---|---:|---:|---:|---:|---:|---:|
| `microsoft-store/ms_tile_icon_300x300.png` | 300x300 | 104 KB | 0.192 | 0.191 | 0.747 | 0.09 |
| `microsoft-store/ms_box_art_1080x1080.png` | 1080x1080 | 1117 KB | 0.205 | 0.183 | 0.57 | 0.099 |
| `microsoft-store/ms_poster_art_720x1080.png` | 720x1080 | 726 KB | 0.192 | 0.181 | 0.673 | 0.077 |
| `microsoft-store/ms_super_hero_1920x1080.png` | 1920x1080 | 1888 KB | 0.154 | 0.105 | 0.696 | 0.084 |
| `microsoft-store/ms_screenshot_1_1920x1080.png` | 1920x1080 | 736 KB | 0.088 | 0.077 | 0.926 | 0.042 |
| `microsoft-store/ms_screenshot_2_1920x1080.png` | 1920x1080 | 1070 KB | 0.116 | 0.121 | 0.842 | 0.06 |
| `microsoft-store/ms_screenshot_3_1920x1080.png` | 1920x1080 | 792 KB | 0.089 | 0.084 | 0.896 | 0.046 |
| `microsoft-store/ms_screenshot_4_1920x1080.png` | 1920x1080 | 742 KB | 0.091 | 0.14 | 0.927 | 0.05 |
| `amazon-appstore/amazon_icon_large_512x512.png` | 512x512 | 321 KB | 0.192 | 0.194 | 0.756 | 0.09 |
| `amazon-appstore/amazon_icon_small_114x114.png` | 114x114 | 21 KB | 0.192 | 0.179 | 0.73 | 0.088 |
| `amazon-appstore/amazon_promo_1024x500.png` | 1024x500 | 545 KB | 0.187 | 0.19 | 0.675 | 0.088 |
| `amazon-appstore/amazon_screenshot_1_800x1280.png` | 800x1280 | 912 KB | 0.154 | 0.111 | 0.768 | 0.07 |
| `amazon-appstore/amazon_screenshot_2_800x1280.png` | 800x1280 | 1183 KB | 0.215 | 0.189 | 0.551 | 0.116 |
| `amazon-appstore/amazon_screenshot_3_800x1280.png` | 800x1280 | 1009 KB | 0.171 | 0.122 | 0.683 | 0.085 |
| `amazon-appstore/amazon_screenshot_4_800x1280.png` | 800x1280 | 986 KB | 0.191 | 0.234 | 0.756 | 0.097 |
| `huawei-appgallery/huawei_icon_512x512.png` | 512x512 | 284 KB | 0.192 | 0.194 | 0.756 | 0.09 |
| `huawei-appgallery/huawei_icon_216x216.png` | 216x216 | 57 KB | 0.192 | 0.189 | 0.74 | 0.089 |
| `huawei-appgallery/huawei_screenshot_1_450x800.png` | 450x800 | 323 KB | 0.151 | 0.109 | 0.78 | 0.069 |
| `huawei-appgallery/huawei_screenshot_1_720x1280.png` | 720x1280 | 825 KB | 0.151 | 0.11 | 0.781 | 0.069 |
| `huawei-appgallery/huawei_screenshot_2_450x800.png` | 450x800 | 428 KB | 0.21 | 0.184 | 0.569 | 0.113 |
| `huawei-appgallery/huawei_screenshot_2_720x1280.png` | 720x1280 | 1074 KB | 0.21 | 0.184 | 0.57 | 0.113 |
| `huawei-appgallery/huawei_screenshot_3_450x800.png` | 450x800 | 360 KB | 0.17 | 0.117 | 0.684 | 0.084 |
| `huawei-appgallery/huawei_screenshot_3_720x1280.png` | 720x1280 | 927 KB | 0.17 | 0.117 | 0.685 | 0.084 |
| `huawei-appgallery/huawei_screenshot_4_450x800.png` | 450x800 | 347 KB | 0.183 | 0.225 | 0.767 | 0.094 |
| `huawei-appgallery/huawei_screenshot_4_720x1280.png` | 720x1280 | 906 KB | 0.183 | 0.225 | 0.767 | 0.094 |

- **Cổng dung lượng:** mọi file dưới trần slot (nặng nhất MS hero 1.888 KB ≤ 50 MB; Huawei icon 216 = 57 KB ≤ 500 KB; screenshot Huawei ≤ 428 KB ≤ 2 MB) ✔
- **Cổng chữ:** chữ `WindWings` chỉ xuất hiện ở 3 slot cho phép/yêu cầu (MS box, MS poster, Amazon promo) — MS hero + mọi screenshot + mọi icon **không chữ** ✔ · Amazon promo: chữ cách mép >50px, đọc rõ ở 300×146 (probe ở cuối contact sheet) ✔ · icon 114px đọc rõ silhouette ✔
- **Cổng màu (tham chiếu):** khung portrait val 0,15–0,22 · dark 0,55–0,78 · chroma ≤0,12 — nằm trong dải nền §4.3 (khung tối tĩnh, 1 accent nóng ember) ✔ · bộ MS pillarbox tối hơn (val ~0,09 do hai dải mờ hai bên) — khai rõ, chỉ là khung trình bày.

**7 master nguồn** (`masters/`, giữ để xuất lại mọi cỡ): `icon_master` 1024² · `hero_master` 1376×768 · `poster_master` 848×1264 · `scene_s1_wave / s2_boss / s3_drone / s4_beam` 768×1376. Script: [`build_w0.py`](build_w0.py) + [`make_preview.py`](make_preview.py) (chạy lại = ra đúng bộ này).

4 cảnh screenshot (dùng chung 3 store, chỉ đổi khung px): **S1** đội hình sóng đầu · **S2** boss + mưa đạn quạt · **S3** drone hộ tống + pickup vàng · **S4** tia plasma + nổ.

## 3. Copy listing — nguyên văn draft §4 (không thêm claim)

Tên hiển thị trong ảnh: **WindWings** *(working title — chờ xác nhận quyền + khả dụng tên trên store, draft §4)*.

- **Microsoft Store (premium, no ads):** Short — “A premium, ad-free vertical arcade shooter. Pilot a starfighter, weave through enemy fire, and face boss encounters.” · Long — “Take command of a starfighter in a vertically scrolling arcade shooter. Dodge enemy formations, fire through incoming waves, and face boss encounters. The planned Windows edition is a premium, ad-free release. No paid loot boxes.”
- **Amazon Appstore (Fire tablet, F2P rewarded-first):** Short — “Pilot a starfighter through fast vertical battles. Dodge enemy fire, clear formations, and challenge boss encounters. Optional rewarded video.” · Long — “Launch into a vertical arcade space shooter. Pilot your starfighter through enemy formations, dodge incoming fire, and take on boss encounters. The planned Fire tablet release is free to play, with optional, opt-in rewarded video ads. No paid loot boxes.”
- **Huawei AppGallery (ngoài TQ đại lục, F2P rewarded-first):** Short/Long như Amazon, thay câu cuối phần Long bằng “The planned AppGallery release is free to play, with optional, opt-in rewarded video ads. No paid loot boxes.”
- **Caption screenshot đề xuất** (MS cho phép ≤200 ký tự/ảnh; chỉ dùng cụm đã có trong draft, không claim mới): S1 “Pilot a starfighter through fast vertical battles.” · S2 “Face boss encounters.” · S3 “Dodge enemy fire, clear formations.” · S4 “Weave through enemy fire.” — **không** đốt chữ vào ảnh (luật slot MS/Amazon + draft “avoid putting required store copy inside the image”).

## 4. Giới hạn phải biết trước khi duyệt (không giấu)

1. **Screenshot = khung CONCEPT**, không phải capture từ bản Godot (chưa có build). Draft §3/§5 yêu cầu chụp lại từ release build từng nền tảng trước khi nộp store — bộ này dùng để chốt style/bố cục/cỡ px và thay 1-1 khi có build. **Không upload nguyên trạng lên store.**
2. **Quyền IP chưa chốt** (USER-ONLY #3): tên `WindWings` trong ảnh là working title; art là hình mới hoàn toàn (không asset GCenter) nhưng chưa phải clearance.
3. **Lệch style đã biết:** master sinh bằng AI nên (a) silhouette tàu hơi hướng “tiêm kích” và chi tiết tàu chưa đồng nhất 100% giữa 7 master, (b) còn nét viền tối mảnh quanh khối — plan §4.6 cấm outline đen toàn cục cho **sprite in-game**; ở art listing cỡ lớn điều này giúp đọc hình, nhưng W1 sprite sẽ tuân §4.6 nghiêm (viền âm `ink-900` chỉ cạnh khuất sáng, đo `dark ≤0,10` trên mask alpha).
4. **Chữ thương hiệu** dùng DejaVu Sans Bold (font sẵn có, giấy phép tự do) làm placeholder wordmark — typeface brand cuối là quyết định của user.
5. Master cảnh rộng 768px → screenshot Amazon 800px gần như 1:1; MS hero 1920 upscale ×1,4 từ 1376 — đủ cho lô duyệt; bản nộp cuối nên vẽ/chụp lại ở độ phân giải gốc cao hơn.

## 5. Việc kế (chờ lệnh)

- **W1 — PLAYER 48 đơn vị** (P-SHIP 25 · P-DRONE 13 · P-BULLET 8 · P-FX 2) theo `target_px` + `recipe` từng dòng planner — chỉ bắt đầu sau khi user duyệt style lô W0 này.
