# BÁO CÁO PHÂN TÍCH UI/UX VÀ GAMEPLAY — WINDWINGS: HẢM ĐOÀI KHÔNG GIAN

**Game:** WindWings: Space Shooter / Hạm đội không gian  
**Package:** com.Wind.wings.Space.Shooter  
**Developer:** GCenter  
**Thiết bị test:** Huawei Mate 20 X (EVR-AL00), Android 10, phân giải 720×1496, density 320  
**Nội dung:** Mô tả chi tiết mọi màn hình đã chụp để AI khác có thể vẽ lại bản mô phỏng  
**Thư mục ảnh:** `D:\WindWings-Space-Shooter-game-play\ramus-capture\`

---

## 1. MÀM SPLASH / CHÀO (phone-01-launch.png)

- **Bố cục:** Trung tâm màn hình, không có nút bấm, tự chuyển sang Home sau vài giây
- **Nội dung:** Logo Unity (hình khối xoáy trắng trên nền đen)
- **Màu sắc:** Nền đen (#000000), logo trắng/xám
- **Font:** Không có chữ lớn, chỉ logo Unity

---

## 2. MÀM CHÍNH / HÀNG KHÔNG (HOME) (phone-02-01…04, phone-19-home-again.png)

### Vùng Status Bar (trên cùng, chiều cao ~60px)
| Vị trí | Thành phần | Màu sắc | Chữ |
|--------|-----------|---------|-----|
| Trên trái | Mũ VIP xanh lá + đồng hồ đếm ngược | Xanh lá, trắng | `PREMIUM`, `18:xx:xx` |
| Giữa trái | Sao vàng + số cấp | Vàng, trắng | `★ 6` |
| Giữa | Đồng xu + số | Vàng, trắng | `🪙 106.664` |
| Giữa phải | Ngọc xanh + số | Xanh dương, trắng | `💎 1.210` |
| Phải trên | Nút "SIÊU Ủ ĐẢI" + badge thông báo | Đỏ, trắng | `SIÊU Ủ ĐẢI` |

### Vùng chính (giữa màn hình)
- **Tàu S1 (màu xanh dương):** Vùng vuông bo góc bên trái, dưới đáy ghi `S1`
- **Tàu S2 (màu đỏ hồng):** Vùng vuông bo góc bên phải, dưới đáy ghi `S2`
- **NÂNG CẤP:** Chính giữa, giữa tâm vòng sáng nhấp nháy, có mũi tên vàng trỏ lên
- **Tàu phụ L (xanh lá cây):** Dưới bên trái, nhãn `L`
- **Ô R (khóa/trống):** Dưới bên phải, nhãn `R`

### Vùng dưới
- Nút lớn `CHƠI` (màu vàng cam, bo tròn, bóng caira) chính giữa
- Hai nút song song: `ĐẦU TRƯỜNG` (trái, xám, bị khóa) và `PVP` (phải, xám, bị khóa)
- Nút `MÓN HỢI` (quà tặng màu đỏ vàng) góc dưới trái
- Nút `VIP` (ánh sáng tím) góc dưới phải

### Tab điều hướng dưới cùng (bottom nav, cao ~150px)
- Món máy bay (đang chọn, có chấm đỏ thông báo)
- Nút kho (khóa)
- Tab `MÁY BAY` (đang chọn, xanh dương)
- Bảng hồ sơ
- Nút giỏ hàng (SHOP)

**Màu chủ đạo:** Nền xanh navy đậm (`#0a1a2e`), nút chính vàng cam (`#ffb700`), chữ trắng in đậm có viền.

---

## 3. MÀM CÀI ĐẶT (SETTINGS) (phone-03-settings.png)

- **Cách vào:** Nút bánh răng `CÀI ĐẶT` góc trên phải màn Home
- **Bố cục:** 8 ô vuông song song (2 hàng × 4 cột), mỗi ô có biểu tượng + tên
- **Các ô:**
  1. `DÀNH NHẬP` (trên trái) — có dấu chấm đỏ thông báo
  2. `CÀI ĐẶT` (trên phải) — mở menu cài đặt chi tiết
  3. `ĐỔI QUÀ` (dưới trái) — nhập mã giftcode
  4. `THÔNG TIN` (dưới phải) — thông tin nhóm phát triển

### Màn Cài Đặt Chi Tiết (phone-04-general-settings.png)
- Điều khiển: tùy chọn đổi nút L/R
- Kích thả tay rời
- Nhạc nền: Bật/Tắt
- Âm thanh: Bật/Tắt
- Hình ảnh: Chất lượng

### Màn Ngôn Ngữ (phone-05-language.png)
- 10 lựa chọn ngôn ngữ, đang chọn **Tiếng Việt**

### Màn Hồ Sơ (phone-06-profile.png)
- Cấp độ: 2, Sao: 6
- Đấu trường, Công nghệ: 1/35
- Tàu chiến

### Màn Hỗ Trợ (phone-07-support.png)
- Mở ứng dụng Gmail

### Màn Đổi Quà (phone-08-giftcode.png)
- Ô nhập mã + nút `Trao đổi`

### Màn Thông Tin / Credits (phone-09-info.png)
- Nhóm phát hành, Thiết kế, Lập trình viên, Họa sĩ, Cân bằng
- Âm nhạc từ: freesound.org, opengameart.org, soundbible.com

### Màn Chính Sách Bảo Mật (phone-10-privacy.png)
- Mở trình duyệt Chrome

### Màn Cộng Đồng (phone-11-community.png)
- Fanpage + Group Facebook

---

## 4. MÀM HÀNG MÁY BAY / KHO CUNG CẤP (phone-12-tab1.png → phone-15-tab5.png)

- **5 tab ngang** ở trên cùng màn hình
- **Tab 2 bị khóa:** Yêu cầu cấp độ 25
- **Tab 4:** Nhiệm vụ
- **Tab 5:** Giá bán (chia 3 nhóm)

### Shop — Đồng Xu (phone-16-shop-gold.png)
| Số xu | Chi phí ngọc |
|-------|--------------|
| 2.250 | 30 |
| 6.560 | 80 |
| 18.600 | 200 |
| 120.000 | 1.000 |
| 202.500 | 1.500 |
| 326.000 | 2.000 |

### Shop — Ngọc Xanh (phone-17-shop-gems.png)
| Số ngọc | VIP | Giá (₫) |
|---------|-----|---------|
| 1.200 | +6 Điểm VIP | 31.000 ₫ |
| 3.000 | +15 Điểm VIP | 77.000 ₫ |
| 5.000 (HOT SALE) | +30 Điểm VIP | 91.000 ₫ |

Hạn mức: Số lần mua còn lại: 2

### Shop — Siêu Deal (phone-18-shop-deals.png)
| Gói | Số xu | VIP | Giá (₫) |
|-----|-------|-----|---------|
| 800.000 | +60 Điểm VIP | 161.000 ₫ |
| 4.000.000 | +240 Điểm VIP | 651.000 ₫ |
| 12.000.000 | +480 Điểm VIP | 1.450.000 ₫ |

---

## 5. MÀM PREMIUM VERSION (phone-20-home.png, phone-21-premium.png)

**Hiển thị:** Khi bấm biểu tượng VIP góc trên phải hoặc vào Home lần đầu

**Ưu đãi:**
- `+20` thẻ/item
- `+300` ngọc xanh
- `+10` thẻ khác

**Đặc quyền:**
- KHÔNG QUẢNG CÁO
- MIỄN PHÍ làn hồi sinh đấu-tier
- VÔ HẠN năng lượng chơi
- Nhận thêm X3 coin thu thụp

**3 gói đăng ký:**
| Thời gian | Điểm VIP | Giá (₫) |
|-----------|----------|---------|
| +3 NGÀY | +15 | 20.000 ₫ |
| +30 NGÀY | +30 | 350.000 ₫ |
| MÃI MÃI | +200 | 450.000 ₫ |

---

## 6. MÀM NÂNG CẤP CÔNG NGHỆ — CƠ BẢN / TECH TREE (phone-37-tech-tree.png / test-now.png)

Đây là màn "Cơ bản" trong nâng cấp — Tech Tree của tàu **NAM CHẤM**.

### Bố cục chung
- **Tiêu đề lớn trên cùng:** `CÔNG NGHỆ CỦA TẤT CẢ CÁC MÁY BAY CHÍNH` (trắng, in đậm, căn giữa)
- **Tab tàu đang chọn:** `NAM CHẤM` | `Lv.1` (trái: tên tàu, phải: cấp độ)
- **Mô tả công nghệ:** `Tăng tỉ lệ hoạt động của nam chấm` (trắng, dưới tên tàu)
- **Biểu tượng tàu:** Hình nam chấm (tiểu phách) trên nền xanh, bên trái mô tả

### Danh sách công nghệ (bên phải, từ trên xuống)
Mỗi mục có hình lục giác số cấp, tên, thanh tiến trình, chi phí:

| STT | Tên công nghệ | Cấp | Chi phí | Trạng thái | Màu sắc |
|-----|---------------|-----|---------|------------|---------|
| 1 | Sức khỏe | 1 | 1.214 🪙 | Đã mở | Xanh dương |
| 2 | Đai-basic-chính | 1 | 2.042 🪙 | Đã mở | Xanh dương |
| 3 | Súng thường | 1 | 0 🪙 | **Đang chọn** | Xanh + mũi tên xanh trỏ lên |
| 4 | Nam chấm | 1 | 212 🪙 | **Đang chọn** | Xanh + đường dẫn màu vàng nối từ biểu tượng tàu |
| 5 | Vũ khí laser | 0 | 2.000 🪙 | Chưa mở (khóa) | Xám |

### Đường dẫn trực quan
- Đường màu vàng nối từ biểu tượng "U" (nam chấm) trên hình tàu bên trái đến ô "Nam chấm" bên phải
- Ô đang chọn có viền sáng xanh dương và mũi tên xanh hướng lên

### Vùng nút dưới cùng
- `CÓ BẢN` (nút xám, chưa bật)
- `TẢI NĂNG` (nút xanh dương, có chấm đỏ thông báo ở góc phải)
- `NÂNG CẤP` (nút xanh dương lớn, góc dưới phải)

### Footer (dưới cùng)
- `CÔNG NGHỆ: 1/35` (tổng công nghệ đã mở / tổng có sẵn)
- Sao vàng `6/30`
- Nút quay lại góc dưới trái (mũi tên xoay ngược, xanh dương)

---

## 7. MÀM TÀI NĂNG / SKILL TREE (tinang.png) ⭐ MỚI CHỤP

Đây là màn **Tài Năng** (Skill Tree), được chọn từ tab `SỬ DỤNG` trong màn nâng cấp công nghệ.

### Bố cục chung
- **Tiêu đề lớn trên cùng:** `CÔNG NGHỆ CỦA TẤT CẢ CÁC MÁY BAY CHÍNH` (trắng, in đậm, căn giữa)
- **Tab kỹ năng đang chọn:** `CHOÁNG` | `Lv.1` (trái: tên kỹ năng, phải: cấp độ)
- **Mô tả kỹ năng:** `Phông xa từ trường để quét dän, gây sát thương và làm tê liệt sung ké thú.` (trắng, dưới tên kỹ năng, chữ hơi bị méo do font game)
- **Biểu tượng kỹ năng:** Hình sóng/dấu xoáy trắng trên nền xanh đậm, bên trái mô tả

### Tab chức năng (trên trái, dưới tiêu đề)
- `SỬ DỤNG` — nút xanh dương, đang được chọn (highlight)

### Danh sách kỹ năng (bên phải, từ trên xuống)
Mỗi mục có hình lục giác số cấp, tên, thanh tiến trình, chi phí:

| STT | Tên kỹ năng | Cấp | Chi phí | Trạng thái | Màu sắc |
|-----|-------------|-----|---------|------------|---------|
| 1 | Nhiều-ten-lūra | 1 | 726 🪙 | Đang chọn | Xanh + mũi tên xanh trỏ lên |
| 2 | Choáng | 1 | 383 🪙 | Đang chọn | Xanh + nút mũi tên xanh hướng lên bên phải |
| 3 | Vô hình | — | — | Khóa (Cần đạt Vip 1) | Xám |
| 4 | Bom | — | — | Khóa (Cần đạt Vip 3) | Xám |
| 5 | Siêu Laze | — | — | Khóa (Cần đạt Vip 5) | Xám |
| 6 | Bom lớn | — | — | Khóa (Cần đạt Vip 6) | Xám |
| 7 | Vô hình II | — | — | Khóa (bán hiển thị) | Xám |

### Đường dẫn trực quan
- Ô kỹ năng đang chọn ("Choáng") có mũi tên xanh hướng lên ở góc phải
- Các kỹ năng khóa hiển thị chữ đỏ `Cần đạt Vip X` bên dưới tên

### Vùng bên trái (preview tàu)
- Hình vẽ tàu chiến wireframe xanh neon trên lưới tọa độ xám
- Các điểm sáng xanh neon xung quanh tàu (hiệu ứng kỹ năng)
- Biểu tượng `U` màu cam/vàng trên thân tàu

### Vùng nút dưới cùng
- `CÓ BẢN` (nút xám, chưa bật)
- `TẢI NĂNG` (nút xanh dương, có chấm đỏ thông báo ở góc phải)
- `NÂNG CẤP` (nút xanh dương lớn, góc dưới phải)

### Footer (dưới cùng)
- `CÔNG NGHỆ: 1/35` (tổng công nghệ đã mở / tổng có sẵn)
- Sao vàng `6/30`
- Nút quay lại góc dưới trái (mũi tên xoay ngược, xanh dương)

---

## 8. MÀM DIALOG THOÁT GAME (phone-38-exit-dialog.png)

- **Tiêu đề:** `THOÁT KHÔI TRÒ CHƠI` (trắng, to, trên nền xanh navy)
- **Nội dung:** `Bạn có chắc chắn muốn thoát khỏi trò chơi?`
- **2 nút:**
  - `ĐỒNG Ý` (màu đỏ, bên trái)
  - `HỦY BỎ` (màu vàng cam, bên phải)
- **Nút X đóng** góc trên phải (màu đỏ)

---

## 9. LUÔI DI CHUYỂN (NAVIGATION FLOW)

```
Splash (Unity logo)
   ↓ (tự động sau vài giây)
Home / Hàng Không
├─ Cài Đặt (bánh răng góc trên phải)
│  ├─ Chung: Điều khiển L/R, Kích thả tay rời, Nhạc, Âm thanh, Hình ảnh
│  ├─ Ngôn ngữ (10 lựa chọn, Tiếng Việt mặc định)
│  ├─ Hồ sơ (Cấp 2, Sao 6, Công nghệ 1/35)
│  ├─ Hỗ trợ (mở Gmail)
│  ├─ Đổi quà (nhập mã + Trao đổi)
│  ├─ Thông tin (credits: phát hành, thiết kế, lập trình, họa sĩ, âm nhạc)
│  ├─ Bảo mật (mở Chrome)
│  └─ Cộng đồng (Fanpage + Group FB)
├─ Hàng Máy Bay (5 tab, tab 2 khóa cấp 25)
│  ├─ Tab 1: Kho cung cấp
│  ├─ Tab 4: Nhiệm vụ
│  └─ Tab 5: Giá bán
│     ├─ Đồng xu (6 mức, 2.250 → 326.000)
│     ├─ Ngọc xanh (3 mức, +6 → +30 VIP)
│     └─ Siêu deal (3 mức VIP, 161.000 → 1.450.000 ₫)
├─ Nâng cấp / Công Nghệ (Tech Tree)
│  ├─ NAM CHẤM (Lv.1): Sức khỏe, Đai-basic-chính, Súng thường, Nam chấm, Vũ khí laser
│  └─ TÀI NĂNG / CHOÁNG (Lv.1): Nhiều-ten-lūra, Choáng, Vô hình, Bom, Siêu Laze, Bom lớn, Vô hình II
│     └─ Nút: CÓ BẢN / TẢI NĂNG / NÂNG CẤP
├─ Premium Version (3 ngày / 30 ngày / mãi mãi)
├─ CHƠI (nút lớn vàng cam, chưa vào được gameplay trong session test)
├─ Đầu Trường (khóa)
└─ PVP (khóa)
```

---

## 10. MÀU SẮC TỔNG THỂ (Palette để vẽ lại)

| Thành phần | Mô tả | Mã màu gợi ý |
|------------|-------|--------------|
| Nền chính | Xanh navy đậm | `#0a1a2e` / `#0f2a4a` |
| Nút chính (CHƠI, NÂNG CẤP) | Vàng cam, bóng caira | `#ffb700` / `#ffd700` |
| Nút thứ cấp (TẢI NĂNG) | Xanh dương sáng | `#00aaff` / `#1e90ff` |
| Nút bị khóa | Xám tối | `#555555` |
| Chữ chính | Trắng, in đậm, có viền | `#ffffff` |
| Số liệu tiền tệ | Vàng / Xanh cyan | `#ffd700` / `#00ffff` |
| Badge thông báo | Đỏ | `#ff0000` |
| Nút đồng ý | Đỏ | `#e74c3c` |
| Nút hủy bỏ | Vàng cam | `#f39c12` |
| VIP / Xanh lá | Xanh neon | `#00ff88` |
| Đường nối kỹ năng | Vàng sáng | `#ffd700` |
| Thanh tiến trình kỹ năng | Xanh dương graduates | `#00aaff` → `#00ffff` |

---

## 11. KIỂU CHỮ (Typography)

- Chữ in hoa, in đậm, có viền mỏng (outline)
- Kích thước lớn cho tiêu đề màn hình
- Kích thước trung bình cho nút bấm, tên công nghệ/kỹ năng
- Số liệu tiền tệ to, màu sắc nổi bật
- Chữ mô tả kỹ năng đôi khi hiển thị méo do font/game engine

---

## 12. TỔNG KẾT FILE ẢNH ĐÃ CHỤP

Thư mục: `D:\WindWings-Space-Shooter-game-play\ramus-capture\`

| File | Màn hình |
|------|----------|
| phone-01-launch.png | Splash / Unity logo |
| phone-02-01…04.png | Loading → Home |
| phone-03-settings.png | Menu cài đặt (8 ô) |
| phone-04-general-settings.png | Cài đặt chung |
| phone-05-language.png | Ngôn ngữ (Tiếng Việt) |
| phone-06-profile.png | Hồ sơ (Cấp 2, Sao 6) |
| phone-07-support.png | Hỗ trợ (Gmail) |
| phone-08-giftcode.png | Đổi quà |
| phone-09-info.png | Thông tin nhóm phát triển |
| phone-10-privacy.png | Chính sách bảo mật (Chrome) |
| phone-11-community.png | Cộng đồng (Facebook) |
| phone-12…15.png | Tab hangar (1,2 khóa,4,5) |
| phone-16…18.png | Shop: Xu, Ngọc, Siêu deal |
| phone-19…25.png | Home, Premium, Level, Shop |
| phone-26…36.png | Thử thao tác nâng cấp |
| phone-37-tech-tree.png | Tech Tree NAM CHẤM (cơ bản) |
| phone-38-exit-dialog.png | Dialog thoát game |
| tinang.png | **TÀI NĂNG / CHOÁNG (skill tree)** |

---

## 13. ĐỀ XUẤT CHO AI VẼ LẠI (Prototype three.js)

1. **HUD trên cùng:** Luôn hiển thị đồng xu, ngọc, sao/VIP, đồng hồ đếm ngược Premium
2. **Màn Home:** 2 tàu lựa chọn (S1/S2), nút CHƠI lớn ở giữa, các nút phụ bị khóa
3. **Màn Tech Tree (Cơ bản):** Danh sách công nghệ dọc, mỗi mục có cấp độ, chi phí, nút mũi tên nâng cấp, đường dẫn màu vàng nối từ tàu
4. **Màn Tài Năng (Skill Tree):** Danh sách kỹ năng dọc, mỗi mục có cấp độ, chi phí, trạng thái khóa (Vip X), preview tàu bên trái với hiệu ứng kỹ năng
5. **Màn Shop:** 3 tab (Xu, Ngọc, Siêu deal), mỗi ô hiển thị số lượng + giá + badge VIP
6. **Màn Premium:** Popup 3 gói đăng ký với danh sách ưu đãi (không quảng cáo, hồi sinh, năng lượng, x3 coin)
7. **Màu sắc:** Dùng palette ở mục 10
8. **Phông chữ:** In đậm, viền xanh, chữ trắng/cyan cho số liệu

---

**Lưu ý:** Các nút trên màn nâng cấp công nghệ/tài năng không phản hồi khi điều khiển qua adb (có thể do overlay hiệu ứng hoặc thiếu điều kiện mở khóa). Để vào màn gameplay (CHƠI), cần thao tác trực tiếp trên máy thật hoặc kiểm tra thêm điều kiện mở khóa.

---

## 14. MÀM GAMEPLAY / TRẬN ĐẤU (gp1.png…gp6.png, gameplay_now.png) ⭐

Đây là màn chơi chính sau khi bấm **CHƠI** từ màn Home, chọn cấp độ 2.

### Bố cục màn hình (720×1496)

**Vùng trên cùng (Status bar chơi):**
| Vị trí | Thành phần | Màu sắc | Chữ |
|--------|-----------|---------|-----|
| Trên trái | Biểu tượng tàu + thanh máu xanh lá | Xanh lá, trắng | `2500` (máu/hp) |
| Giữa phải | Đồng xu + số điểm | Vàng, trắng | `462` → `477` (tăng khi nhặt coin) |
| Phải trên | Nút `II` (Pause) trong ô xanh dương | Xanh dương, trắng | `II` |
| Phải dưới status | Số đếm ngược enemies + hình xương rồng | Trắng, xám | `110` → `109` → `107` |

**Vùng chính (trung tâm màn hình):**
- **Tàu người chơi:** Màu xanh dương/bạc, động cơ vàng, ở đáy giữa màn hình, di chuyển theo ngón tay (touch to move)
- **Tàu phụ L:** Màu xanh lá cây, nhỏ, bên trái tàu chính
- **Đối phương (dàn kết):** Tàu mỹ màu tím hồng, arranged theo lưới 5 cột × nhiều hàng ở phía trên
- **Boss (dưới bên phải):** Tau lớn màu vàng xám, có đầu xương rồng, thanh máu đỏ trên đầu (`255` HP)
- **Trái đất:** Hình Trái Đất ở giữa dưới màn hình (nền)
- **2 trạm không gian:** Hai khối thép lớn hai bên trái/phải (decor, không va chạm)
- **Các asteroid:** Hình đá nhỏ bay xung quanh

**Vùng dưới trái (nút kỹ năng):**
| Vị trí | Tên | Mô tả |
|--------|-----|-------|
| Bên dưới trái | Nút `4` + hình tàu | Kỹ năng Ultimate / đặc biệt |
| Dưới nút 4 | Nút tròn hình hình tròn | Kỹ năng hỗ trợ (có thể là shield/dash) |

### Hiệu ứng trực quan
- **PháDestroy:** Khi bắn trúng đối phương → hình nổ màu vàng/cam, rơi đồng xu vàng
- **Di chuyển coin:** Có trails màu cam/xanh nối từ coin đến tàu người chơi (hiệu ứng hút tự động)
- **Đạn:** Tàu người chơi bắn liên tục (auto-fire), đau màu xanh lá/cyan
- **Đạn địch:** Đỏ, có quỹ đạo rải khắp màn hình (bullet hell)
- **HP bar đối phương:** Thanh đ�m đỏ trên đầu mỗi boss/enemy lớn
- **Sao đánh giá:** 3 sao vàng dưới từng boss/enemy khi đánh xong

### Cơ chế chơi (Gameplay)
- **Điều khiển:** Chạm giữ và di chuyển trên màn hình → tàu di chuyển theo
- **Tấn công:** Tự động bắn liên tục (auto-shoot)
- **Mục tiêu:** Phá toàn bộ dàn kết + boss, đếm ngược số enemies từ 110 xuống 0
- **Phần thưởng:** Nhặt đồng xu vàng rơi từ đối phương bị phá
- **Thua:** Máu người chơi (`2500`) giảm khi bị trúng đạn địch (chưa thấy màn Game Over)

### Màu sắc gameplay
| Thành phần | Màu |
|------------|-----|
| Nền không gian | Xanh đen sâu (`#0a1a2e`) |
| Tàu người chơi | Xanh dương + vàng engine |
| Tàu đối phương | Tím hồng neon (`#cc00ff`) |
| Đạn địch | Đỏ (`#ff0000`) |
| Đạn mình | Xanh lá/Cyan |
| Nổ phá | Vàng/Cam (`#ffd700` → `#ff4500`) |
| Đồng xu | Vàng sáng (`#ffd700`) |
| HP bar máu | Đỏ (`#e74c3c`) |
| Thanh máu người chơi | Xanh lá (`#00ff88`) |

---

## 15. LUÔI DI CHUYỂN ĐẦY ĐỦ (FULL NAVIGATION FLOW)

```
Splash (Unity logo)
   ↓ (tự động sau vài giây)
Home / Hàng Không
├─ Cài Đặt (bánh răng góc trên phải)
│  ├─ Chung: Điều khiển L/R, Kích thả tay rời, Nhạc, Âm thanh, Hình ảnh
│  ├─ Ngôn ngữ (10 lựa chọn, Tiếng Việt mặc định)
│  ├─ Hồ sơ (Cấp 2, Sao 6, Công nghệ 1/35)
│  ├─ Hỗ trợ (mở Gmail)
│  ├─ Đổi quà (nhập mã + Trao đổi)
│  ├─ Thông tin (credits)
│  ├─ Bảo mật (mở Chrome)
│  └─ Cộng đồng (Fanpage + Group FB)
├─ Hàng Máy Bay (5 tab, tab 2 khóa cấp 25)
│  ├─ Tab 1: Kho cung cấp
│  ├─ Tab 4: Nhiệm vụ
│  └─ Tab 5: Giá bán (Đồng xu, Ngọc xanh, Siêu deal)
├─ Nâng cấp / Công Nghệ (Tech Tree)
│  ├─ NAM CHẤM (Lv.1): Sức khỏe, Đai-basic-chính, Súng thường, Nam chấm, Vũ khí laser
│  └─ TÀI NĂNG / CHOÁNG (Lv.1): Nhiều-ten-lūra, Choáng, Vô hình, Bom, Siêu Laze, Bom lớn, Vô hình II
├─ Premium Version (3 ngày / 30 ngày / mãi mãi)
├─ CHƠI
│  ├─ Level Map (cấp 2,3,4,6 + Boss)
│  └─ GAMEPLAY (Trận bắn thật)
│     ├─ Touch di chuyển tàu + auto-fire
│     ├─ Phá dàn kết + boss (đếm ngược enemies)
│     ├─ Nhặt đồng xu
│     ├─ Pause (II)
│     └─ HUD: Máu 2500, Coin, Enemy count
├─ Đầu Trường (khóa)
└─ PVP (khóa)
```

---

## 16. TỔNG KẾT FILE ẢNH ĐÃ CHỤP (CẬP NHẬT)

Thư mục: `D:\WindWings-Space-Shooter-game-play\ramus-capture\`

| File | Màn hình |
|------|----------|
| phone-01-launch.png | Splash / Unity logo |
| phone-02-01…04.png | Loading → Home |
| phone-03-settings.png | Menu cài đặt (8 ô) |
| phone-04-general-settings.png | Cài đặt chung |
| phone-05-language.png | Ngôn ngữ (Tiếng Việt) |
| phone-06-profile.png | Hồ sơ (Cấp 2, Sao 6) |
| phone-07-support.png | Hỗ trợ (Gmail) |
| phone-08-giftcode.png | Đổi quà |
| phone-09-info.png | Thông tin nhóm phát triển |
| phone-10-privacy.png | Chính sách bảo mật (Chrome) |
| phone-11-community.png | Cộng đồng (Facebook) |
| phone-12…15.png | Tab hangar (1,2 khóa,4,5) |
| phone-16…18.png | Shop: Xu, Ngọc, Siêu deal |
| phone-19…25.png | Home, Premium, Level, Shop |
| phone-26…36.png | Thử thao tác nâng cấp |
| phone-37-tech-tree.png | Tech Tree NAM CHẤM (cơ bản) |
| phone-38-exit-dialog.png | Dialog thoát game |
| tinang.png | **TÀI NĂNG / CHOÁNG (skill tree)** |
| lv2_final.png | **Level Map** (cấp 2,3,4,6 + Boss) |
| lv2_play2…4.png | Thử vào level 2 (chưa thành công qua adb) |
| gameplay_now.png | **GAMEPLAY** (trận bắn thật) |
| gp1.png…gp6.png | **GAMEPLAY frames** (6 khung hình liên tiếp) |

---

## 17. ĐỀ XUẤT CHO AI VẼ LẠI (Prototype three.js) — CẬP NHẬT

1. **HUD trên cùng:** Máu người chơi (bar xanh lá), đồng xu điểm, nút Pause, đếm ngược số enemies
2. **Màn Home:** 2 tàu lựa chọn (S1/S2), nút CHƠI lớn ở giữa, các nút phụ bị khóa
3. **Màn Tech Tree (Cơ bản):** Danh sách công nghệ dọc, mỗi mục có cấp độ, chi phí, nút mũi tên nâng cấp, đường dẫn màu vàng nối từ tàu
4. **Màn Tài Năng (Skill Tree):** Danh sách kỹ năng dọc, mỗi mục có cấp độ, chi phí, trạng thái khóa (Vip X), preview tàu bên trái với hiệu ứng kỹ năng
5. **Màn Shop:** 3 tab (Xu, Ngọc, Siêu deal), mỗi ô hiển thị số lượng + giá + badge VIP
6. **Màn Premium:** Popup 3 gói đăng ký với danh sách ưu đãi (không quảng cáo, hồi sinh, năng lượng, x3 coin)
7. **Màn Level Map:** Các nút cấp độ tròn (2,3,4,6), boss dưới cùng, đường nối màu xanh cyan
8. **Màn Gameplay:**
   - Tàu người chơi ở đáy giữa, di chuyển theo touch
   - Dàn kết đối phương ở trên (lưới 5 cột)
   - Boss dưới bên phải với HP bar đỏ
   - Đồng xu rơi từ đối phương bị phá (có trail hút về tàu)
   - Auto-fire (bắn liên tục không cần nút bắn)
   - Nút kỹ năng góc dưới trái (Ultimate + hỗ trợ)
   - Nút Pause góc trên phải
9. **Màu sắc:** Dùng palette ở mục 10 và 14
10. **Phông chữ:** In đậm, viền xanh, chữ trắng/cyan cho số liệu

---

File báo cáo đã được lưu và cập nhật đầy đủ tại:  
`D:\WindWings-Space-Shooter-game-play\ramus-capture\BAO_CAO_UI_UX_WINDWINGS.md`
