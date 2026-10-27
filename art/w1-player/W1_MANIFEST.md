# W1 — PLAYER lane: 48 sprite in-game (lô 2, khép lane Art-designer)

**Vai:** Art-designer · **Nhánh:** `arena/5438fec9-windwings-space-shooter-game-p` · **Ngày:** 2026-10-27
**CLAIM:** [PR #12 comment 6443346351](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6443346351) · **Vào W1:** [PROGRESS 6444201870](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6444201870) (user duyệt tiếp sau [HANDOFF W0 6443565387](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6443565387) @ `4a65378e`)
**Work-order:** `art-planner.csv` + `ART_REDRAW_PLAN.md` @ `971a7eea8` (nhánh `1b836828`) — palette §4.4, recipe §4.5, chuẩn khối/viền §4.6, canvas+tên §4.7, đo §4.9, cổng §4.10. Không sửa plan; không đụng `docs/spec/` · `datas/` · `tools/` · `tests/`.

**Metadata (plan §4.7):** `source` = [`build_w1.py`](build_w1.py) (tham số cố định, chạy lại ra đúng bộ này) · `license` = nội bộ dự án, chờ USER-ONLY #3 · `author` = Art-designer `arena/5438fec9` · `recipe` = cột `recipe` trong [`w1_units.csv`](w1_units.csv) từng unit.

---

## 1. Checklist 48 đơn vị — khớp planner, kèm `target_px` + `recipe`

| Batch (planner) | Row | Đơn vị | `target_px` | Giao | `recipe` | Thư mục |
|---|---|---:|---:|---|---|---|
| P-SHIP | AP-0016 (glyph 25 tàu) | 25 | 256 | 25 × 256×256 RGBA | `ship` | `sprites/ships/` |
| P-DRONE | AP-0011 (glyph 13 drone) | 13 | 128 | 13 × 128×128 RGBA | `drone` | `sprites/drones/` |
| P-BULLET | AP-0002…0009 (8 nhóm) | 8 | 32 | 6 × 32×32 + 2 beam 32×512 RGBA | `bullet` | `sprites/bullets/` |
| P-FX | AP-0013, AP-0014 | 2 | 128 | 2 × 128×128 RGBA | `fx` | `sprites/fx/` |
| **Tổng** | | **48** | | **48 file · 1.344 KB** | | |

- **Tàu ×25** = 5 họ silhouette × 5 biến thể tham số: `dart · delta · broad · crescent · twinboom` (cột `variant` trong CSV). Mũi hướng **lên** (top-down), 1 khối thân + ≤2 khối phụ, 1–3 họng xả.
- **Drone ×13** = 5 họ (`hexpod · crescent · twinpod · capsule · orb-ring`) × biến thể con v0–v2 (xoay hex, đổi cung/khoảng pod/độ dài capsule/độ dẹt vòng), lõi `gold`.
- **Đạn ×8** — tên file mới theo chức năng (plan §4.7 cấm tên gốc trong tên file; tên gốc chỉ nằm ở cột `planner_base` để truy vết):

| Row | planner_base (truy vết) | File giao | px | val | val_std | dark | chroma |
|---|---|---|---:|---:|---:|---:|---:|
| AP-0002 | drone_laser | `player_bullet_dronebolt_32@emberdim.png` | 32×32 | 0.280 | 0.200 | 0.430 | 0.085 |
| AP-0003 | laser | `player_bullet_beam_32x512@emberdim.png` | 32×512 | 0.285 | 0.210 | 0.500 | 0.096 |
| AP-0004 | laserbeam_player | `player_bullet_beamheavy_32x512@emberdim.png` | 32×512 | 0.320 | 0.208 | 0.417 | 0.101 |
| AP-0005 | plasmagun | `player_bullet_plasmaorb_32@emberdim.png` | 32×32 | 0.266 | 0.200 | 0.481 | 0.103 |
| AP-0006 | rocket | `player_bullet_missile_32@emberdim.png` | 32×32 | 0.251 | 0.183 | 0.450 | 0.116 |
| AP-0007 | blt_player_5. | `player_bullet_boltmk5_32@emberdim.png` | 32×32 | 0.256 | 0.199 | 0.507 | 0.087 |
| AP-0008 | drone_laser_child | `player_bullet_childbolt_32@emberdim.png` | 32×32 | 0.273 | 0.196 | 0.471 | 0.089 |
| AP-0009 | plasma_beam_flare_green | `player_bullet_beamflare_32@emberdim.png` | 32×32 | 0.251 | 0.175 | 0.471 | 0.094 |
| AP-0013 | afterburner | `player_fx_engineplume_128@paper.png` | 128×128 | 0.768 | 0.246 | 0.000 | 0.068 |
| AP-0014 | shooter | `player_fx_muzzleflash_128@paper.png` | 128×128 | 0.851 | 0.187 | 0.000 | 0.083 |

- Beam = **tile dọc chu kỳ 64px** (nối đầu–đuôi không mối), đúng ngoại lệ §4.7 `laser 32×512`; `target_px=32` trong planner là bậc giá theo cạnh lớn nhất — ghi cả hai trong CSV (`target_px` vs `delivered_px`).
- FX plume hướng **xuống** (gắn dưới họng xả tàu); muzzle flash đối xứng tâm. Kiểm độc lập sau khi sinh: **48/48 file RGBA, đúng px khai báo, 4 góc alpha = 0**.

## 2. Cách vẽ (để verifier tái lập, không phải "cảm giác")

Sprite vector phẳng vẽ bằng code (`build_w1.py`, Pillow, siêu mẫu ×4 rồi hạ LANCZOS): hình khối đối xứng theo tham số, tô **đúng hex Ink & Ember** với tỉ lệ diện tích bám recipe §4.5, 3 tông + 1 accent + rim sáng phía trên–trái (nguồn sáng duy nhất), **viền âm `ink-900` 1px chỉ ở cạnh dưới–phải khuất sáng** (không outline đen toàn cục, §4.6), grain giấy ±3,7% (≤6%). Không dùng PNG/atlas/hình gốc nào; contact sheet gốc chỉ dùng ở W0 để tham chiếu bố cục.

## 3. Cổng đo (plan §4.10) — kết quả

**G-A (máy, §4.9 trên PNG alpha, mask `alpha>0,5`): PASS 48/48** (luật: sai ≤1 chỉ số trong `val · val_std · dark · chroma`).
Phân bố chỉ số lệch duy nhất: `val_std` ×27 · `chroma` ×6 · `val` ×4 · `dark` ×1 · sạch cả 4 ×10.
Dải đo theo batch (chi tiết từng unit: `w1_units.csv` / `.json`):

| Batch | val (§4.3) | val_std | dark | chroma | fill |
|---|---|---|---|---|---|
| P-SHIP (0,46–0,52 · 0,24–0,30 · ≤0,10 · 0,19–0,23) | 0,474–0,517 | 0,202–0,243 | 0,023–0,057 | 0,197–0,228 | 0,239–0,366 |
| P-DRONE (0,45–0,52 · 0,22–0,26 · ≤0,08 · 0,18–0,22) | 0,434–0,489 | 0,202–0,234 | 0,021–0,086 | 0,189–0,228 | 0,173–0,257 |
| P-BULLET (0,25–0,30 · 0,18–0,26 · ≥0,40 · ≤0,12) | 0,251–0,320 | 0,175–0,210 | 0,417–0,507 | 0,085–0,116 | 0,185–0,750 |
| P-FX (0,70–0,90 · 0,15–0,25 · ≤0,02 · ≤0,08) | 0,768–0,851 | 0,187–0,246 | 0,000 | 0,068–0,083 | 0,145–0,224 |

**G-B (silhouette 64px):** bằng chứng [`preview/w1_silhouettes_64.png`](preview/w1_silhouettes_64.png) — 5 họ tàu phân biệt rõ ở 64px đen (dart hẹp · delta tam giác rộng · broad bè · crescent cánh tiến · twinboom hai pod); 5 họ drone phân biệt rõ. Trong cùng họ, biến thể khác nhau ở bề rộng cánh/vị trí đầu cánh/số họng xả — phân biệt được khi đặt cạnh nhau, yếu hơn khác họ (khai ở §4).
**G-E (pháp lý):** không logo bên thứ ba, không hình gốc, tên file mới toàn bộ ✔.
**G-F (đọc 0,2s):** mock gameplay 720×1280 chỉ từ sprite W1 [`preview/w1_gameplay_mock_720x1280.png`](preview/w1_gameplay_mock_720x1280.png) — tàu/drone/beam đọc rõ trên nền ink; đạn thân tối đọc bằng viền sáng (đặc tính recipe, khai ở §4).
**G-C:** chưa chạy `tools/design-metrics.py` (tool nằm ở nhánh spec — đường cấm sửa, và không có trong nhánh này) → để verifier `ef6b75ef` chạy trên thư mục preview nếu cần. **G-D:** N/A (sprite không 9-slice).

Ảnh tổng: [`preview/w1_ships_contact.png`](preview/w1_ships_contact.png) (25 tàu) · [`preview/w1_small_contact.png`](preview/w1_small_contact.png) (13 drone + 8 đạn phóng 4× nearest + 2 FX). Script preview: [`make_w1_preview.py`](make_w1_preview.py).

## 4. Lệch & giới hạn — khai thẳng

1. **25 tàu vs `kept_records=16`:** planner scope-B chỉ giữ 16/25 bản ghi tàu, nhưng work-order user chốt 48 đơn vị (= 25 thiết kế). Đã làm đủ 25; art-planner (`1b836828`) có thể đánh dấu 9 chiếc là full-parity khi đối soát khối lượng.
2. **`val_std` là chỉ số lệch hệ thống** (27/48 lệch duy nhất ở chỉ số này, tàu 0,20–0,24 so với dải 0,24–0,30): plan §4.3 tự ghi `val_std` đo trên contact-sheet JPEG 150px là **số tương đối, không chấm tuyệt đối một ảnh**. Tôi đo trên texel PNG theo §4.9 nên số thấp hơn baseline JPEG; G-A vẫn PASS nhờ luật ≤1 chỉ số. Nếu director muốn, đây là ứng viên "đo lại baseline" ở pilot S0 — không tự sửa bảng.
3. **Số màu `colors_q32` cao hơn dải §4.3** (tàu 541–644 so với 110–160): do grain + gradient sáng + khử răng cưa; số màu **không** nằm trong 4 chỉ số G-A. Cần giảm màu cho atlas thì tắt grain/reduce gradient trong `build_w1.py` và đo lại — đổi 1 tham số, chưa làm vì không có lệnh.
4. **Buồng lái teal ≤4% diện tích** trên tàu: recipe `ship` thuần không có teal; đây là rim/accent nhận diện giữ liên tục với art W0 đã được duyệt, nằm trong ngân sách rim ≤5% của §4.6 và chroma đo được vẫn trong dải. Muốn thuần recipe thì thay teal bằng `ink-700`+glint `paper` (1 dòng code).
5. **Biến thể trong họ là tham số, không phải 25 bản vẽ tay độc lập:** planner đo `de_est` cho thấy gốc là thiết kế riêng; bộ này là 5 họ × 5 bộ tham số khác nhau đo được (bề rộng/đầu cánh/mũi/họng xả). Đạt chuẩn L2 (đúng kích thước/silhouette/số đo) và dùng được ngay; mức "mỗi tàu một cá tính vẽ tay" là việc polish L3 nếu user duyệt thêm giờ.
6. **Pivot = tâm canvas, ảnh chưa trim:** plan §4.7 yêu cầu đọc `sprite_mesh_contract` (nằm ở nhánh spec, tôi không có file này trong tay) — giao canvas đầy đủ để Godot-coder/verifier đặt pivot theo contract mà không mất thông tin. Đạn thân tối (`ink-900` 45%) trên nền game tối đọc bằng viền `ink-300` — đúng luật recipe `bullet` ("thân tối + viền sáng", mẫu gốc `dark 0,493`), nhưng nếu playtest thấy chìm thì tăng viền là chỉnh nhỏ.
7. **AP-0014 `shooter` (bằng chứng G2)** được diễn giải là muzzle-flash theo lane P-FX; nếu triage sau này xác định khác, chỉ phải vẽ lại 1 unit này. Mock gameplay dùng drone lật 180° làm địch tượng trưng — **chỉ là ảnh mock**, không phải asset enemy (lane ENEMY ngoài work-order).

## 5. Bàn giao cho Godot-coder (khi CLAIM mở)

Import nguyên thư mục `sprites/`; hướng sprite: tàu/đạn mũi lên (+Y màn hình đi lên = hướng bay), plume gắn dưới đuôi hướng xuống, beam kéo dọc bằng tile 64px. Mọi sprite đã chừa biên trong suốt quanh hình (fill ở CSV) — pack atlas theo hình bao như §4.8 (padding 4px do packer thêm). Tên file: `player_<vai>_<biến thể>_<size>@<accent>.png` (snake_case, §4.7).

## 6. REDO lần-149 — nâng render 2.5D (2026-10-27, thay bản phẳng @`8e6cd2f5`)

**Căn cứ:** STYLE-CORRECTION lần-149 ([PR #12 comment 6446004160](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6446004160) + draft `238f2b41c`): bản phẳng bị chốt không đạt độ giàu thị giác 2.5D như gốc. ACK của tôi: [6446368163](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6446368163). User lệnh: theo đúng style, tham khảo gốc APK đã phân tích, không chờ duyệt.

**Cách làm:** giữ nguyên bố cục/silhouette/palette Ink & Ember/tên file; thay `light_pass` phẳng bằng pass render 2.5D dùng chung [`../render25d.py`](../render25d.py) (numpy, tất định): gradient key-light trên-trái nhiều bậc trên từng mảng · bevel nâng tâm mảng theo khoảng cách-tới-mép · AO ở mép trong + gầm · rim-light cạnh trên/trái · seam panel 1px + highlight bậc thang dọc ranh giới màu (đường panel) · vệt bóng specular trên kim loại/paper. Hệ số sáng kẹp [0,74–1,50] nên `ink-500` không bao giờ bị shading đẩy qua vạch dark<45. Beam 32×512 dùng chế độ `tile_y` (đóng băng ramp dọc + khoảng cách cuốn vòng) — **vẫn lát dọc không mối**. Đạn 32px tắt AO mép (vỏ sáng mỏng, AO sẽ ăn mất vỏ); FX chỉ shading rất nhẹ (recipe fx cấm dark >0,02). Chạy lại: `/home/user/.venv/bin/python build_w1.py` (cần numpy).

**Cổng:** G-A **PASS 48/48** (đo §4.9 như cũ). Dải đo mới: P-SHIP val 0,480–0,518 · std 0,199–0,235 · dark 0,025–0,061 · chroma 0,197–0,223 · P-DRONE val 0,448–0,506 · std 0,204–0,239 · dark 0,022–0,089 · chroma 0,192–0,233 · P-BULLET val 0,250–0,295 · std 0,196–0,211 · dark 0,417–0,531 · chroma 0,084–0,120 · P-FX val 0,789–0,856 · std 0,199–0,257 · dark 0 · chroma 0,066–0,082. Số ở §1/§3 là bản phẳng, giữ để truy vết; số hiện hành ở `w1_units.csv`/`.json`. Tổng 48 file = 1.421,6 KB; kiểm độc lập: 48/48 tồn tại, RGBA đúng px, bytes khớp CSV.

**Bảng so sánh cạnh tranh (điều kiện lần-149):** [`preview/w1_compare_vs_original.png`](preview/w1_compare_vs_original.png) (script [`make_w1_compare.py`](make_w1_compare.py)) — 7 cặp: bản redo ↔ sprite gốc gần nhất theo dáng cắt từ contact sheet phân tích (`ships-01` #19/#3/#14/#21/#25, `drones-01` #4/#5), cùng tỉ lệ hiển thị. Ảnh gốc trong bảng là **tư liệu đối chiếu nội bộ, không phải asset game**; thư mục `sprites/` không chứa hình gốc nào. Preview cũ (contact/silhouette/mock) đã sinh lại từ bản redo.

**Khoảng cách còn lại so với gốc — khai thẳng:** kỹ thuật render đã cùng họ 2.5D (gradient/AO/rim/seam/gloss đều có và nhìn thấy trên bảng so sánh), nhưng gốc vẫn giàu hơn ở (1) mật độ chia panel vẽ tay trong từng mảng, (2) mảng sáng specular cục bộ mạnh, (3) thân nhiều màu — điểm (3) bị luật palette cấm (chỉ Ink & Ember, §5 VISUAL_DESIGN). `val_std` vẫn là chỉ số lệch hệ thống duy nhất của tàu (0,20–0,24 so với 0,24–0,30) — cùng ghi chú baseline JPEG ở §4.2; `colors_q32` tăng tiếp (tàu ~650–780) vì gradient nhiều bậc chính là yêu cầu lần-149 — chỉ số gradient-stop/outline/detail-density chính thức chờ `measure_asset.py` mở rộng của nhánh `1b836828`, tôi chỉ tiêu thụ.
