# ĐO ĐẠC UI — WINDWINGS (bộ ảnh chụp thật, tháng 10/2026)

Nguồn: nhánh `windwings-ui-ux-analysis`, commit `14886d8` — 90+ ảnh chụp màn hình
Huawei Mate 20 X (**720×1496**, density 320) + 2 báo cáo.

Bản nằm trong nhánh làm việc này (bản rút gọn, 10 ảnh + 3 tài liệu): `docs/windwings-refs/v2/`.
Bộ đầy đủ 90+ ảnh vẫn nằm ở nhánh trên (không chép sang đây: 68 MB, không cần cho build).

| File | Màn |
|---|---|
| `01-home.jpg` | Home / hàng không |
| `02-gameplay.jpg`, `03-gameplay-2.jpg` | Trận đánh (2 khung) |
| `04-tech-tree.jpg` | Công nghệ — cây tech của NAM CHÂM |
| `05-skill-tree.jpg` | Tài năng — CHOÁNG |
| `06-level-map.jpg` | Bản đồ cấp độ + boss |
| `07-shop-gold.jpg` | Shop — đồng xu |
| `08-hangar-24.jpg` | Lưới 24 tàu |
| `09-upgrade.jpg`, `10-settings.jpg` | Nâng cấp, cài đặt |
| `BAO_CAO_UI_UX_WINDWINGS.md` | Báo cáo gốc (510 dòng) |
| `SHIPS_24_REFERENCE.md`, `SHIPS_24_WIREFRAME.svg` | 24 tàu + khung vẽ |

> Mọi số dưới đây **đo trên ảnh 720×1496**, đơn vị px trong khung đó. Muốn đổi sang
> tỉ lệ màn hình khác thì nhân với `chiều_rộng / 720`.

---

## 1. Màu đo được (không phải màu suy đoán)

| Vùng | Mã | Ghi chú |
|---|---|---|
| Thanh máu — đỉnh | `#cdea42` | vệt sáng trên cùng, cao ~4 px |
| Thanh máu — thân | `#a5cd0d` | màu chủ đạo, vàng-lá chua |
| Thanh máu — đáy | `#7fa303` | tối dần, tạo khối |
| Nền ô HUD | `#06122c` → `#0a1a38` | navy gần đen |
| Viền/rim cyan | `#46c6f4` (sáng) · `#2f9fe0` (thường) · `#14538c` (tối) | viền kép: sáng trên, tối dưới |
| Năng lượng | `#8fdcff` → `#3fa9ff` → `#1d64c8` | 5 đốt, đốt bật phát sáng |
| Vàng (xu, sao) | `#ffec22` (mặt) · `#ffc21f` (vành) · `#d68a00` (bóng) | xu có 3 vòng đồng tâm |
| Nút phụ (xanh) | `#6fa8ff` → `#2f6fe0` → `#1b3f8c` | nút tạm dừng, tab đang chọn |
| Nút chính (CHƠI) | `#ffe08a` → `#ffb700` → `#d97f00` | viền ngoài `#ffdf8a` + bóng cứng `#6b3f00` |
| Nút xanh lá (nâng cấp) | `#7df05a` → `#35c21a` → `#1c8a0c` | thường có mũi tên trắng |
| Đỏ cảnh báo | `#e23a2e` | badge, nút đồng ý |
| Chữ | `#ffffff` + bóng cứng `#050a18` / `#16233c` | không dùng chữ xám trên nền tối |

Nền gameplay: tinh vân xanh **rất tối**, chừa độ tương phản cho địch tím/hồng neon và
đạn đỏ. Nền không bao giờ sáng hơn 25 % độ sáng tuyệt đối.

---

## 2. HUD trong trận — hình học

Khung 720×1496. Toàn bộ HUD nằm trong dải **y 86…146** (60 px ≈ 4 % chiều cao) + bộ đếm địch.

| Khối | x | y | w | h | Ghi chú |
|---|---|---|---|---|---|
| Chân dung tàu | 16 | 88 | 74 | 58 | cắt vát góc trái 14 px, viền cyan 2 px |
| Thanh máu (vỏ) | 62 | 92 | 270 | 30 | **nghiêng −12°**, viền kép 2 px |
| Dải năng lượng | 66 | 126 | 224 | 15 | 5 đốt, mỗi đốt 44×15, nghiêng −26°, cách 4 px |
| Xu | 444 | 84 | 44 | 44 | icon + số 42 px nghiêng |
| Tạm dừng | 640 | 86 | 60 | 60 | bo 13 px, viền gradient xanh 3 px |
| Đếm địch | right 20 | 176 | — | 34 | số 30 px + đầu lâu 34 px |
| Nút kỹ năng | 22 | (đáy 210) | 78 | 78 | badge số "4" ở góc trên-trái |

**Vì sao nghiêng:** mọi thanh/ô của WindWings đều vát 10–26°. Đó là thứ tạo cảm giác
"buồng lái" thay vì "bảng điều khiển web". Không có thanh nào là hình chữ nhật đứng yên.

---

## 3. Công thức linh kiện

### 3.1 Thanh máu
1. Vỏ = gradient dọc `#6fd4ff → #2f9fe0 → #14538c`, `padding: 2px`, `transform: skewX(-12deg)`.
2. Ruột = `#06122c` + inner-shadow tối.
3. Fill = 3 dải `#cdea42 / #a5cd0d / #7fa303`, thêm **vạch chia 26 px** mờ 28 %.
4. Số = 30 px, 900 **italic**, chữ trắng, bóng cứng `0 3px 0 #1e2c05`; số phải **nghiêng ngược**
   (`skewX(+12deg)`) để không bị xiên theo thanh.

### 3.2 Nút chính
- Cao 104 px, bo 20 px, chữ 48 px 900 italic.
- Viền kép: `0 0 0 4px #2b1a00` + `0 0 0 6px #ffdf8a`.
- Bóng cứng `0 10px 0 #6b3f00` (không dùng bóng mờ dài).
- Vệt sáng elip ở 1/3 trên (`::after`) — đây là thứ duy nhất được phép "bóng".

### 3.3 Hàng công nghệ
- Lục giác cấp 58×58, cắt 6 cạnh, gradient `#17458a → #0a1f44`, số 28 px nghiêng.
- Tên 30 px 800 italic, bóng cứng 3 px.
- Thanh tiến trình 26 px, nghiêng −14°, nền có **gạch chéo 45°** ở phần chưa mở; phần đã mở là
  gradient xanh.
- Giá: icon xu 24 px + số 24 px, canh phải; nút cộng xanh lá 74×52 cắt vát hai đầu.

### 3.4 Node bản đồ
- Tròn 88 px, 3 lớp: lõi sáng lệch trên, thân navy, vành 5 px.
- Vành: đã xong `#35c21a` · đang mở `#ffc21f` · chưa mở `#2b6fd0`.
- Đường nối 4 px gradient `#7fe0ff → #2f9fe0` + quầng.
- Sao 26 px đặt dưới node, không đặt trong node.

### 3.5 Ô tàu (khoang)
- 150×150, cắt 8 góc 18 px (kiểu "khoang ghép"), viền cyan 2 px.
- Nền radial `#1d3a68 → #0a1730`; tàu PNG đổ bóng mềm 6 px.

---

## 4. Luật hình ảnh v2 (bổ sung cho `windwings-ui-spec.md`)

1. **Vát, không vuông.** Thanh/ô nghiêng 10–26° hoặc cắt góc 14–18 px.
2. **Viền kép 2 px**: sáng ở trên, tối ở dưới. Một viền đơn không đủ dày để đọc trên nền tinh vân.
3. **Số phải nghiêng và có bóng cứng 3–4 px.** Số không bóng sẽ chìm vào nền.
4. **Một nguồn sáng trên–trái**; vệt sáng chỉ ở 1/3 trên, không viền sáng mép dưới.
5. **Glow chỉ dành cho thứ đang bật**: đốt năng lượng, vành node đang mở, đạn. Không glow đại trà.
6. Nền gameplay tối hơn nền menu 2 nấc — HUD là thứ sáng nhất trên màn.

---

## 5. Phòng thử UI (đối chiếu 1:1)

`prototype/uikit.html` — dựng lại HUD + linh kiện đúng toạ độ trên, có **thanh trượt chồng ảnh gốc**
(`gp1.png`) và nút **NHÁY** để soi lệch biên. Đây là nơi duyệt hình trước khi tê vào `style.css`.

Khi đã duyệt: chép khối HUD trong `src/uikit.css` sang `src/style.css`, thay markup `.hud-top`
trong `index.html`. Giữ nguyên id (`hpText`, `hpFill`, `shieldDots`, `hudCoins`, `btnPause`…)
để `hud.js` không phải sửa.

---

## 6. Chênh lệch với HUD hiện tại của game (việc phải làm)

| Hạng mục | Hiện tại | WindWings | Ưu tiên |
|---|---|---|---|
| Thanh máu | hộp chữ nhật 12 px, viền trái cyan | vát −12°, cao 30 px, 3 dải màu, số 30 px | **cao** |
| Chân dung tàu | không có | ô vát 74×58 cạnh thanh máu | **cao** |
| Năng lượng | 5 chấm 14×6 | 5 đốt 44×15 nghiêng, phát sáng | vừa |
| Điểm / xu | 2 hộp riêng, chữ 20 px | 1 cụm icon 44 px + số 42 px | **cao** |
| Tạm dừng | nút icon 40 px | ô 60×60 viền gradient, 2 thanh trắng | vừa |
| Đếm địch | số trong hộp "ĐỢT" | số 30 px + đầu lâu, không hộp | vừa |
| Boss bar | thanh phẳng giữa màn | (ảnh chụp chưa có) — giữ, nhưng cho vát + viền kép | thấp |
| Nút kỹ năng | không có | ô 78 px + badge số | thấp |
