# WindWings 3D — Spec asset & sprite (v1)

Tài liệu này là **hợp đồng hình ảnh** giữa bộ asset (`docs/asset-samples/`) và giao diện
(`prototype/`). Mọi thay đổi UI sau này phải bám theo đây, không tự thêm gradient "giả 3D".

- Ảnh tham chiếu đã cắt: `docs/windwings-refs/01…13*.jpg` (9 ảnh gốc 720×1496 trong Drive `WinWing-screenshot`).
- Bộ sinh asset: `docs/tools/make_assets.py` (icon, nền, bảng style) và `docs/tools/ship_sprites.py` (tàu).
- Bảng tổng hợp để xem nhanh: `docs/asset-styleboard.png` (1600×2940).
- Font: Barlow Condensed (OFL) — TTF trong `assets_samples/fonts/barlow_condensed/`, subset **latin + vietnamese**.

---

## 1. Nguyên tắc hình ảnh (bắt buộc)

1. **Tranh vẽ, không phải ảnh 3D.** Khối nằm ở *mảng màu phẳng + viền + ánh sáng*, không dùng bevel,
   inner-shadow dày hay gradient mô phỏng kim loại bóng.
2. **Bão hoà cao.** Accent rực (cam/gold, cyan, xanh lá, đỏ, tím) đặt trên nền navy sâu. Không dùng
   màu bùn, không giảm saturation toàn cục.
3. **Viền tối 2–5 px** quanh mọi hình (icon, tàu, nút) để tách khỏi nền.
4. **Ánh sáng từ trên–trái**: highlight ở cạnh trên/trái, bóng ở cạnh dưới/phải. Không có 2 nguồn sáng.
5. **Bóng đổ cứng, ngắn** (offset 2–4 px), không bóng mờ dài.
6. Nền là **tranh**: tinh vân, hành tinh, khoang tàu, starfield — không phải `linear-gradient` CSS.

## 2. Bảng màu (token)

| Token | Hex | Dùng cho |
|---|---|---|
| `bg.deep` | `#050B1E` | nền ngoài, letterbox |
| `bg.night` | `#070C1C` | nền màn hình |
| `bg.home` | `#0F1B43` | nền home/map |
| `bar` | `#131838` / `#171733` | top bar, bottom nav |
| `panel` | `#0C2452` | thân panel |
| `panel.deep` | `#0A1836` | panel lồng, hàng danh sách |
| `edge` | `#123265` | viền panel 1–2 px |
| `line` | `#2B6FD0` | đường kẻ, divider |
| `cyan` | `#6FD8FF` | chữ phụ, icon hệ thống, glow |
| `cyan.hi` | `#A7E6FF` | highlight cyan |
| `orange` | `#E49302` | CTA chính (PLAY / DEPLOY) |
| `gold` | `#F7A507` | sao, viền CTA, reward |
| `gold.hi` | `#FFD66B` | mép sáng của gold |
| `coin` | `#FDB507` | xu |
| `green` | `#18C11E` | CTA "miễn phí"/tiến trình |
| `blue` | `#0364CF` | CTA phụ (COLLECT thường) |
| `gem` | `#0F9ACC` | ngọc cyan |
| `red` | `#C81515` | badge PREMIUM, cảnh báo |
| `violet` | `#7A4BD0` | CTA premium, reward VIP |
| `text` | `#EAF4FF` | chữ chính |
| `muted` | `#7F93B8` | chữ phụ |
| `gray` | `#5B5F60` | khoá / chưa đạt |

## 3. Typography

- Family: **Barlow Condensed** 700/800/900 + 700 italic. Không dùng font system cho tiêu đề.
- Tiêu đề màn hình: 900, IN HOA, letter-spacing 0.5–1 px, màu `text`, bóng cứng `#050A18` offset (2,3).
- Số tiền/EXP: 900 italic, màu trắng; đơn vị (xu/ngọc) là icon 20–24 px đặt sau số.
- Nhãn nút: 800 IN HOA; nút chính 22–26 px, nút phụ 18–20 px.
- Nhãn nhỏ (caption, level): 700, 13–15 px, màu `muted`.

## 4. Icon (27 món, `docs/asset-samples/ic_*.png`, 192×192)

Khung 192, hình chiếm **72 %** (padding ~27 px mỗi cạnh). Thứ tự dựng:

1. silhouette đa giác/ellipse; 2. gradient 2 điểm theo trục dọc *trong* silhouette;
3. mảng tối 25–40 % ở nửa dưới; 4. highlight bóng (ellipse trắng 60–85 %, lệch trên–trái);
5. viền tối 3–5 px; 6. viền sáng 1–2 px ở cạnh trên; 7. đổ bóng cứng (0, 4) màu `#050A18` 35 %.

| Tên | Hình | Màu chủ |
|---|---|---|
| `star` | sao 5 cánh, lõi sáng | `gold` → `#FFE08A` |
| `coin` | đĩa tròn + vành trong + rãnh chữ V | `coin` |
| `gem` | brilliant 6 cạnh, 3 facet | `gem` + `cyan.hi` |
| `flask` | bình cổ hẹp, chất lỏng phát sáng | `green` |
| `gear` | 8 răng, lỗ tròn | `#4FA8FF` |
| `lock` | ổ khoá, quai dày, lỗ khoá | `#5FC8F0` |
| `gift` | hộp quà, nơ vàng | `red` + `gold` |
| `crown` | vương miện 3 đỉnh | `gold` |
| `skull` | sọ + hốc mắt + răng | `#E9F1FA` |
| `shield` | khiên 5 cạnh, gờ trong | `#2A69C2` |
| `clock` | mặt đồng hồ + kim | `gold` |
| `pause` | 2 thanh tròn | `cyan` |
| `plus` | dấu cộng tròn | `green` |
| `check` | tick dày, đầu tròn | `#8CFF9A` |
| `drone` | quadcopter 4 rotor cyan, thân xanh | `green` |
| `pilot` | mũ phi công + kính cyan | trắng/`#2A69C2` |
| `map` | bản đồ gấp, đường route, ghim đỏ | giấy `#E8B85C` |
| `sound` | loa + 2 sóng | `cyan` |
| `music` | nốt nhạc đôi | `#B79BFF` |
| `install` | mũi tên xuống + khay | `green` |
| `globe` | địa cầu, lục địa xanh | `#3FA8E0` |
| `info` | chữ i trong vòng tròn | `#2A69C2` |
| `trash` | thùng rác đỏ | `red` |
| `speed` | 2 mũi tên nhanh | `gold` |
| `cannon` | đạn pháo: đầu đỏ, thân vàng, lửa | gold/red |
| `armor` | giáp ngực, gờ cam, lõi cyan | `#2A69C2` |
| `magnet` | nam châm chữ U, 2 cực bạc | `red` |

**Ánh xạ công nghệ:** `cannon → ic_cannon`, `armor → ic_armor`, `shield → ic_shield`,
`drone → ic_drone`, `magnet → ic_magnet` (dùng cho cả orb 5 cột và hàng danh sách).

Bản dùng trong game nằm ở `prototype/src/icons/` (cùng tên file, Vite tự băm khi build);
`prototype/src/thumbs/<tên tàu>.png` là sprite tàu 512 px ở mục 5.

Cỡ dùng: 24 px (HUD), 28–32 px (hàng reward), 40–48 px (thẻ reward), 64 px (empty state).
Xuất @2x/3x từ file 192 nên không cần vẽ lại.

## 5. Sprite tàu (8 tàu, 512×512, mũi hướng lên)

File: `docs/asset-samples/ship_<tên>.png` — nền trong suốt, ship chiếm ~88 % chiều cao.

Thứ tự dựng (`ship_sprites.render_ship`):

1. viền tối 5 px (dilate silhouette) — vẽ **dưới** cùng;
2. bóng đổ mềm dưới đuôi;
3. cánh: gradient dọc `light → base → dark`, mảng sáng ở mép trước, mảng tối ở mép sau, gân cánh `accent`;
4. pod/boom: gradient ngang, sáng hơn thân;
5. thân: gradient ngang theo bbox (`light` ở trái → `base` 34 % → `dark` 78 %), dải specular dọc;
6. dải `accent`, panel line, đinh tán, buồng lái (gradient + glow + highlight);
7. ống xả: ellipse tối + lõi `flame` + lửa 2 lớp (dài 2.4× ống xả);
8. rim light 1–2 px **bên trong** silhouette, chỉ góc trên–trái;
9. resize LANCZOS.

| Tàu | base | light | dark | accent | canopy | flame |
|---|---|---|---|---|---|---|
| striker | `#E49302` | `#FFD066` | `#8C4C00` | `#F2F9FF` | `#6FE6FF` | `#7FE0FF` |
| zenith | `#2A69C2` | `#8FD8FF` | `#0E2E60` | `#FFC04A` | `#7FE6FF` | `#8FD8FF` |
| challenger | `#B23BC8` | `#F29BFF` | `#54105E` | `#F2F9FF` | `#FFD066` | `#FFB0F0` |
| spitfire | `#18B03C` | `#8CF07A` | `#074F18` | `#F7A507` | `#7FE6FF` | `#8CFF9B` |
| insurgent | `#C81515` | `#FF7A5E` | `#5C0505` | `#C9D3DE` | `#FFC04A` | `#FFB07A` |
| executioner | `#5B3FA8` | `#B79BFF` | `#22103F` | `#FFD34D` | `#FFC04A` | `#C9B0FF` |
| omen | `#17327A` | `#6F9BFF` | `#050C22` | `#FFC93C` | `#8FE9FF` | `#8FE9FF` |
| dispatcher | `#0E7FA8` | `#7FE6FF` | `#03303F` | `#FF8A2B` | `#B6F3FF` | `#7FE6FF` |

Bố cục đọc được: striker = mũi nhọn + cánh thẳng; zenith = delta liền; challenger = 2 boom;
spitfire = 4 cánh X; insurgent = giáp hộp; executioner = thân giáo + canard; omen = cánh dơi;
dispatcher = thân rộng + 2 pod + 4 ống xả.

Cỡ dùng: 96–120 px (roster), 140–180 px (map/boss), 200–300 px (hangar, kết quả).
Không xoay sprite quá ±12°; muốn hướng khác thì vẽ silhouette mới.

## 6. Chrome: panel, nút, node, thẻ

- **Panel**: nền `panel` phẳng, viền `edge` 1–2 px, 4 góc vát 10–14 px (clip-path), **không** bo tròn đều;
  header ribbon hình thang (như ảnh 11) màu `#0F3A86`, chữ 800 IN HOA.
- **Nút chính**: cao 56–64 px, bo 10 px, nền `orange` + dải sáng 40 % ở 1/3 trên + viền `gold.hi` 2 px
  + bóng cứng (0,3) + chữ trắng 800. Nút phụ: `blue` / `green` / `gray` cùng công thức.
  Trạng thái khoá: `gray`, chữ `muted`, không glow.
- **Porthole**: ảnh `ring_porthole.png` làm nền `.slot-ring`, tàu đặt trong lòng (68 %),
  khoá thì giảm sáng 40 %; không vẽ vành bằng gradient CSS.
- **Hàng reward**: cao 56 px, nền `panel.deep`, viền trái 4 px màu theo loại (star/gold, coin/gold, gem/cyan),
  icon 32 px, chữ 700, số 900 italic căn phải.
- **Node màn (map)**: hình tròn 84–104 px, vành ribbed 8 px màu `#54595D`, lõi `#0B1A36`, số 900 trắng;
  trạng thái: xong = vành `green` + 3 sao vàng; hiện tại = vành `green` phát sáng + nhịp; khoá = xám, số `muted`.
  Node boss = đầu lâu 56 px trên đĩa đỏ sẫm, không số.
  Đường nối: 3 px `line` 60 %, chỉ nối node đã mở.
- **Thẻ reward (daily)**: 168×196, nền `violet` hoặc `blue`, ribbon `x10`/`x1` chéo góc dưới–phải,
  viền `gold.hi` khi claimable, `gray` khi chưa tới.
- **Badge**: chấm đỏ 10 px + viền navy 2 px, đặt góc trên–phải icon, không đè hình.

## 7. Nền

- **Nebula (map/home)**: 3–5 ellipse màu `#2158FF/#6A2FE0/#D040E8/#12A6E8` alpha 25–40 %, blur lớn,
  1 dải chéo hồng, hành tinh có khí quyển + vân mây + bóng tối nửa phải, 120–260 sao 1–3 px + 6 sao lấp lánh.
  Sinh bằng `plate_nebula(w,h,seed)` — seed cố định để mỗi màn khác nhau nhưng tái lập được.
- **Hangar**: nền navy, quầng ấm cam dưới sàn, sàn lục giác viền `orange`, 2 vòng docking ribbed có vạch vàng,
  vạch hazard hai bên, trụ trung tâm có đèn cyan.
- Không dùng ảnh photo, không dùng texture nhiễu hạt.

## 8. Đóng gói & quy ước file

```
docs/asset-samples/ic_<tên>.png      192×192  (icon, 27 file)
docs/asset-samples/ship_<tên>.png    512×512  (tàu, 8 file)
docs/asset-samples/bg_nebula_<n>.jpg 900×1600 (nền dọc, 3 biến thể seed)
docs/asset-samples/ring_porthole.png  512×512 (vành cửa sổ khoang tàu, lòng trong suốt)
docs/asset-styleboard.png            1600×2940 (bảng duyệt)
docs/tools/make_assets.py            sinh icon + nền + bảng
docs/tools/ship_sprites.py           sinh 8 sprite tàu
```

- Tên file: snake_case, không dấu, không khoảng trắng. Không đổi tên sau khi UI đã tham chiếu.
- UI dùng `<img>` + `width/height` cố định (tránh layout shift), `image-rendering: auto`.
- CSS chỉ được dùng cho: viền, bo góc, clip-path, chữ, màu nền phẳng, glow bằng `box-shadow`.
  **Cấm** `linear-gradient` nhiều lớp mô phỏng khối 3D cho nút/panel/icon.
- Nếu cần atlas cho APK: pack theo lưới 8 cột, cell 256, kèm `atlas.json` (`frame{x,y,w,h}`, `pivot`);
  hiện tại dùng file rời để đơn giản và cache tốt.

## 9. Áp dụng vào các màn

| Màn | Asset |
|---|---|
| Home | nền nebula, panel nhiệm vụ (6), 2 porthole + `ship_*`, 2 slot tiến hoá, CTA `orange`, nav icon |
| Hangar | nền hangar, vòng docking, sprite tàu, panel chỉ số (`star`/fist), thanh EXP |
| Roster | ô 96 px nền `panel`, sprite, dải sao, badge cấp, khoá = sprite giảm sáng 40 % + `ic_lock` |
| Tech/Công nghệ | 5 cột icon tròn 72 px (mở = nền `blue` + viền `cyan`), hàng cấp + nút `+1` |
| Map | nền nebula theo chương, node (6), đường nối, sao dưới node, node boss `ic_skull` |
| Pause | panel vát góc, hàng reward, tile điều khiển (viền `orange` khi chọn) |
| Settings / Daily | lưới thẻ settings (icon cyan 40 px), hàng daily (6) + thẻ reward |

## 10. Checklist trước khi merge UI

- [ ] Không còn emoji làm icon trong UI.
- [ ] `linear-gradient` chỉ dùng **theo trục dọc, 3 điểm màu** cho thanh/nút (khối), không dùng gradient chéo bóng bẩy trên panel/icon.
- [ ] Mọi ảnh có `alt` rỗng (trang trí) hoặc `alt` mô tả (nội dung).
- [ ] Icon hiển thị đúng 24/32/48 px, không méo tỉ lệ.
- [ ] Đo trên 360×640: không tràn ngang, tap target ≥ 42 px.
- [ ] Ảnh mới đều nằm trong repo, không hotlink.

---

## 11. Bản v2 — HUD trong trận (đo từ ảnh chụp thật 10/2026)

Bộ ảnh mới (90+ ảnh 720×1496, nhánh `windwings-ui-ux-analysis`) cho thấy HUD trong trận
khác hẳn phần menu đã spec ở trên. Số đo đầy đủ + mã màu + công thức từng linh kiện:
[`windwings-refs/v2/DO_DAC_UI.md`](windwings-refs/v2/DO_DAC_UI.md).

Tóm tắt 4 thay đổi so với v1:

1. **Vát là mặc định**: thanh máu nghiêng −12°, đốt năng lượng −26°, thanh công nghệ −14°,
   ô chân dung cắt góc 14 px. Không còn khối chữ nhật đứng.
2. **Viền kép 2 px** (sáng trên / tối dưới) thay cho viền 1 px.
3. **Số nghiêng 900 + bóng cứng 3–4 px**, cỡ 30–42 px — to hơn hẳn bản v1 (20 px).
4. **HUD là một dải cao 60 px** ở y 86…146, không phải 3 hộp rời.

Duyệt hình tại `prototype/uikit.html` (có thanh trượt chồng ảnh gốc + nút NHÁY để soi lệch).
