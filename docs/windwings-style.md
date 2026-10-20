# Phân tích style & bố cục WindWings (từ 9 ảnh trong Drive)

Tài liệu này ghi lại **những gì quan sát được** từ bộ ảnh `WinWing-screenshot` (9 ảnh, 720 × 1496, Android dọc)
để dựng lại UI cho prototype. Không chứa ảnh gốc (bản quyền GCenter), chỉ chứa số đo và mã màu.

---

## 1. Bảng màu (lấy mẫu bằng lượng tử hoá màu)

| Vai trò | Mã | Ghi chú |
|---|---|---|
| Nền sâu nhất | `#040d24` | đáy màn hình, viền ngoài |
| Nền chính | `#091640` → `#101c40` | hue 222–226, bão hoà 0.86 |
| Nền panel | `#032b5e` → `#0a255d` | khối nội dung |
| Viền phát sáng | `#3fccf6` / `#93e0fb` | 1px cyan, kèm glow |
| Xanh nhấn đậm | `#102f95`, `#173d71` | band tiêu đề, thanh tiến trình |
| Cam CTA (PLAY) | `#eba229` → `#b66a15` | gradient dọc, chữ nâu đậm |
| Xám phụ (ARENA/PVP) | `#54585b` → `#3a3a3e` | nút khoá / phụ |
| Vàng sao / xu | `#f4af28`, `#fed035` | |
| Xanh lá (nâng cấp được) | `#56d84a` | mũi tên lên |
| Đỏ (premium, boss, badge) | `#e8354a` | |
| Chữ | `#eaf6ff` | trắng hơi lạnh, có glow nhẹ |

## 2. Typography
- **Toàn bộ chữ IN HOA**, font condensed (Roboto Condensed / Oswald), weight 700–900.
- Tiêu đề màn: ~44px (≈ 6% chiều rộng 720) + glow cyan nhẹ.
- Nhãn nút: 26–30px, letter-spacing ~0.06em.
- Số liệu (xu, điểm): cùng cỡ tiêu đề, **tabular-nums**, màu trắng hoặc vàng.
- Không dùng chữ thường trong UI; mô tả phụ cũng in hoa cỡ nhỏ.

## 3. Hình khối & viền
- Mọi panel là **hình chữ nhật vát 4 góc** (cut-corner ~14px), không bo tròn.
- Viền kép: 1px cyan ngoài + 1px navy đậm trong; thêm `box-shadow` glow 8–12px.
- Tab tiêu đề dạng **hình thang** (cạnh xiên 20–30°), nền xanh đậm, chữ trắng.
- Nút chính: vát góc, gradient dọc, **highlight trắng mờ ở 40% trên**, đổ bóng dưới.
- Icon nút đáy: ô vuông 56px, viền cyan, nền navy, badge đỏ ở góc khi có thông báo.
- Khe cắm tàu: **vòng tròn** viền đồng/navy dày 6px, bên trong là ảnh tàu 3/4.

## 4. Bố cục từng màn (toạ độ theo % chiều cao 1496)

### 4.1 Khung chung
| Vùng | Vị trí | Nội dung |
|---|---|---|
| Thanh tiền tệ | y 4% – 9.7% | PREMIUM (đỏ + đồng hồ), ★, xu + nút `+`, gem + nút `+`, banner SUPER OFFER |
| Nội dung | y 10% – 93% | |
| Thanh điều hướng đáy | y 93.5% – 100% | 5 tab vuông: Hangar, Technology, Chapters (giữa, lớn hơn), Store, Settings |

### 4.2 HOME (`...59f70cd2...`)
- Trái trên: avatar + tên; giữa: nút LOG IN (có badge đỏ); phải: SETTINGS.
- **Hai khe tàu tròn lớn** đặt đối xứng hai bên (S1 / S2), đường kính ~34% chiều rộng.
- Giữa hai khe: **pod nâng cấp** hình tròn có 2 mũi tên cam chỉ lên, nhãn `UPGRADE`.
- Dưới: **khe module L / R** vuông 22% rộng (một khe khoá).
- **PLAY**: nút cam khổng lồ 49% rộng × 6.5% cao, giữa màn hình.
- Dưới PLAY: 2 nút xám `ARENA`, `PVP`.
- Hai góc dưới: `GOOD DEAL` (hộp quà đỏ) và `VIP` (khiên tím).

### 4.3 CHAPTERS / bản đồ màn (`...1e11e46...`)
- Nền: tinh vân xanh + hành tinh lớn bên trái.
- **Đường đi uốn khúc** nối các node tròn, node đã qua có vòng xanh lá + 3 sao bên phải.
- Node: vòng kim loại xám, số trắng ở giữa; node boss có **đầu lâu**.
- Đáy: `CHAPTERS` (giữa) và `UPGRADE` (phải); trái là nút back.

### 4.4 HANGAR / tàu (`...2f2c7176...`)
- Trên: tab chữ nhật `A  MACHINEGUN` + 5 mũi tên cấp.
- Trái: ảnh tàu 3D trên nền tối; phải: **ô xem trước hiệu ứng** (đạn/aura).
- Bảng chỉ số: `LVL. 3/30`, `ATK: 740`, thanh EXP chia 2 màu.
- Dưới: 2 nút `+1 lvl` — một trả **xu**, một trả **gem** (nút gem xanh đậm hơn).
- Lưới 4×4 khe tàu/drone, khe đang chọn có khung cyan + số thứ tự.

### 4.5 TECHNOLOGY (`...c9801a...` và `...289d6a...`)
- Panel trên: tên công nghệ + `Lvl.1` + mô tả 1 dòng.
- Giữa: **sơ đồ tàu hologram cyan** + đường vàng nối tới các chỉ số.
- Phải: danh sách dọc, mỗi dòng = **badge lục giác** cấp + tên + thanh tiến trình + giá.
- Dòng nâng cấp được: mũi tên xanh lá ở cuối; dòng khoá: chữ đỏ `Unlock At Vip 3`.
- Đáy: `BASIC` / `TALENTS` + `TECHNOLOGY: 1/35`.

### 4.6 PAUSE (`...383f320f...`)
- Tiêu đề `PAUSE` có 2 vạch cyan hai bên.
- Khối 1: `STAGE 3 [NORMAL]` + 3 dòng mục tiêu, mỗi dòng có **sao vàng/xám** + phần thưởng (xu/gem).
- Khối 2: `CONTROLS` / `BUTTONS` — 4 ô chọn, ô đang chọn có viền cam + dấu ✓.
- Khối 3: thanh trượt `MUSIC`, `SOUND`, `GAME SPEED` (fill cyan, núm vuông).
- Đáy: `RESTART` (xanh) + `RESUME` (cam).

### 4.7 SETTINGS (`...d3342a4f...`)
- Lưới 2 cột × 4 hàng, mỗi ô = icon phát sáng lớn + nhãn in hoa.
- Nền ô là gradient navy, viền cyan mảnh.

### 4.8 LOG IN EVERY DAY (`...dbdef978...`)
- Modal có band tiêu đề + nút X đỏ góc phải.
- 4 khối phần thưởng, mỗi khối: tiêu đề + `Day 1/n` + 2–3 ô vật phẩm + nút `COLLECT` (cyan) / `NOT REACHED` (xám) / `PREMIUM` (tím).

## 5. Nguyên tắc tương tác
- Mọi thứ bấm được đều ≥ 44px, có hiệu ứng nhấn (sáng lên + scale 0.98).
- Trạng thái khoá: **làm xám + ổ khoá**, không ẩn.
- Badge đỏ ở tab khi có phần thưởng chưa nhận.
- Nút CTA chính luôn **cam**, hành động phụ **xám**, nâng cấp **xanh lá**.

---

## 6. Đã áp dụng vào prototype

| Màn WindWings | Màn prototype | Ghi chú |
|---|---|---|
| Thanh tiền tệ | `#topBar` | PREMIUM → đồng hồ đếm quà ngày; ★ tổng sao; ◆ xu; ◈ gem; nút `+` nhảy sang Cửa hàng |
| Thanh điều hướng đáy | `#bottomNav` | 5 tab: HANGAR · CÔNG NGHỆ · CHIẾN DỊCH · CỬA HÀNG · CÀI ĐẶT, badge đỏ khi chưa nhận quà |
| HOME | `#screen-home` | S1 = tàu đang dùng, S2 = khoang khoá, pod NÂNG CẤP → Công nghệ, L/R = drone, CHƠI (cam) → bản đồ, ĐẤU TRƯỜNG → chế độ nhanh đang chọn, PVP khoá |
| CHAPTERS | `#screen-map` | 3 chip chương, đường polyline uốn khúc, node sao + node boss ☠, màn khoá mờ + 🔒 |
| HANGAR | `#screen-hangar` | tab chữ S + pips, ảnh tàu, bảng LVL/ATK/HP/TỐC ĐỘ, thanh cấp, 2 nút mua (xu / gem), lưới 4×2 tàu |
| TECHNOLOGY | `#screen-tech` | đầu thẻ + 5 orb lục giác, 5 dòng tiến trình, nút xu + gem, tổng `x/60` |
| STORE | `#screen-store` | thẻ quà ngày (chuỗi 7 mốc) + đổi gem → xu |
| SETTINGS | `#screen-settings` | lưới 2×4 icon phát sáng, 2 ô bật/tắt hiện trạng thái |
| PAUSE | `#screen-pause` | `CH x · MÀN y`, 3 dòng mục tiêu có sao, 4 ô điều khiển có ✓ cam, 3 thanh trượt |
| LOG IN EVERY DAY | modal `#dailyModal` | 7 mốc, mốc đã nhận / hôm nay / chưa tới, nút NHẬN |
| KẾT QUẢ | `#screen-result` | 3 sao, 4 ô điểm/kỷ lục/hạ địch/thưởng, nút MÀN TIẾP |

## 7. Ghi chú kỹ thuật

- Toàn bộ icon trong HUD lấy qua `url()` của `src/assets.js` (đi theo `BASE_URL`) nên chạy đúng cả khi
  GitHub Pages phục vụ ở thư mục con `/<repo>/`.
- Thanh máu / khiên / tiến trình vẽ bằng CSS thuần (không phụ thuộc ảnh trong `assets_samples/`),
  nhờ vậy bản `dist/` không còn URL tuyệt đối `/03_ui/...`.
- Font hệ thống condensed (Roboto Condensed / Oswald nếu máy có) — không tải font ngoài, hợp với APK offline.
- Mọi vùng bấm ≥ 42px; trạng thái khoá = làm xám + 🔒 (không ẩn), đúng nguyên tắc ở mục 5.
