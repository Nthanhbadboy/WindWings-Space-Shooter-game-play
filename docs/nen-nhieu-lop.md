# Nền nhiều lớp — làm cho màn chơi có chiều sâu

Mục tiêu: người chơi phải có cảm giác **đang ở trong không gian và đang lao về phía trước**,
không phải đang xem một tấm ảnh dán sau lưng tàu.

Bản vẽ tổng hợp: [`previews/lop-khong-gian.png`](previews/lop-khong-gian.png).

> **D20:** đã **bỏ hẳn Trái Đất, trạm, dầm và mọi mây vẽ tay**. Lớp xa nhất là ảnh Hubble
> 2560² đứng yên tuyệt đối; **lớp thứ 2 là ảnh tinh vân thật, trôi chậm**. Nguyên tắc: *vẽ không
> đẹp thì bỏ, không vẽ bù* — nên chỉ còn ảnh thật + hạt sáng.

---

## 1. Vì sao nền cũ trông phẳng

1. **Thiếu lớp gần.** Mọi thứ đều nằm sau vùng giao chiến, nên không có vật nào che ngang tàu.
   Không có che khuất thì mắt không có mốc để biết cái gì gần, cái gì xa.
2. **Lớp "xa" và lớp "gần" chạy gần bằng nhau.** Nếu hai lớp cùng tốc độ, não gộp chúng thành
   một mặt phẳng bất kể độ nét khác nhau.
3. **Không có phản ứng khi tàu di chuyển.** Camera đứng yên tuyệt đối nên nền chỉ là hình nền
   cuộn, không phải không gian có thể tích.

Ba lỗi trên không sửa được bằng cách "vẽ đẹp hơn" — phải sửa bằng **quan hệ giữa các lớp**.

---

## 2. Ảnh nguyên mẫu và bài học rút ra

Ảnh lưu trong [`nen-tham-chieu/`](nen-tham-chieu/); ảnh WindWings thật ở
[`windwings-refs/v2/02-gameplay.jpg`](windwings-refs/v2/02-gameplay.jpg).

| Ảnh | Nhìn thấy gì | Bài học |
|---|---|---|
| **WindWings thật** (gameplay) | tinh vân xanh thẫm → Trái Đất lớn → trạm không gian hai bên → đội hình địch → HUD | 5 lớp, nhưng **chỉ 1 lớp là "cảnh"** (Trái Đất); trạm nằm ở **rìa** và **cắt vào** vùng chơi → đó là lớp gần thật sự. |
| **CraftPix — nền dọc** | mỗi bảng là một cảnh riêng: tinh vân màu, sao, hành tinh, đá | Hành tinh **lớn gấp 30–60 lần** hạt đá. Tương quan kích thước là thứ tạo chiều sâu, không phải chi tiết. |
| **Parallax pixel** (Aamatniekss) | sao 3 độ sáng, tinh vân mờ, đá trôi | Ba cỡ sao + ba độ sáng = ba độ xa. Nền tối gần như đen để lớp gần nổi lên. |
| **Sky Force** | mây mù nhiều tầng + trạm khổng lồ + tàu | **Sương mù giữa các lớp**: lớp càng xa càng nhạt và ngả xanh. Không có sương thì các lớp "dính" vào nhau. |

Kết luận: chiều sâu = **chênh tốc độ** + **tương quan kích thước** + **che khuất** + **sương mù**.

---

## 3. Bóc lớp từ ảnh WindWings thật

| # | Lớp | Dấu hiệu nhận ra | Tốc độ cảm nhận |
|---|---|---|---|
| 1 | Tinh vân nền | mảng màu mềm, không có cạnh | gần như đứng yên |
| 2 | Trái Đất | khối lớn, tự xoay, có khí quyển | rất chậm, chỉ trôi khi tàu sang ngang |
| 3 | Trạm không gian | khối thép lớn ở **rìa dưới**, cắt vào mép màn hình | chậm hơn bụi, nhanh hơn Trái Đất |
| 4 | Địch + đạn | nét, tương phản cao, có bóng đổ | tốc độ gameplay |
| 5 | HUD | phẳng, luôn trên cùng | đứng yên |

Điểm quan trọng: **trạm không gian là lớp gần duy nhất** và nó chỉ chiếm hai góc dưới. Nó không
che giữa màn hình — đó là lý do có thể đưa lớp gần vào mà không phá gameplay.

(D20: phần "cảnh" của bản gốc — Trái Đất + trạm + dầm — **bị bỏ hết** vì vẽ lại không đẹp bằng;
chỉ giữ lại *quan hệ lớp*: một lớp xa đứng yên, một lớp mây thật trôi, và một lớp gần che tàu.)

---

## 4. Mô hình 10 lớp của game

| Lớp | Nội dung | z (camera) | Tốc độ màn hình (màn/giây) |
|---|---|---|---|
| L0 | **ẢNH THẬT** — Hubble Ultra Deep Field 2560² | −320 | **0 — đứng yên tuyệt đối** |
| **L1** | **sương lớn + 3 đám tinh vân ẢNH THẬT trôi** (Tarantula, Carina) | −292…−308 | 0,007 → 0,014 |
| L2 | 150 sao nhỏ, lạnh | −260 | 0,006 |
| L3 | 95 sao | −170 | 0,010 |
| L4 | 48 sao ấm | −110 | 0,016 |
| L5 | mảnh vụn / thiên thạch | −110…−40 | 0,17 → 1,0 |
| L6 | bụi 4 tầng | −95…−20 | 0,07 → 1,56 |
| **L7** | **bụi lớn + vệt sáng — TRƯỚC cả tàu** | **−1,7…−4,8** | **2,2 → 4,1** |
| L8 | vùng giao chiến (Game vẽ) | 3…−16 | — |

Từ L2 tới L7, tốc độ tăng **~680 lần**. Đó là dải động cần có; nếu nén lại còn 20–30 lần thì
cả khung cảnh đọc ra một mặt phẳng.

---

## 5. Bốn cơ chế trong code (`src/backdrop.js`)

### 5.0 Lớp xa nhất là ẢNH THẬT và không bao giờ chuyển động

`sky` là mặt phẳng dán **Hubble Ultra Deep Field** (NASA/ESA, phạm vi công cộng — ảnh gốc
4000², xuất 2560²), nằm ở `z −320`, phủ kín khung theo kiểu `cover` (giữ đúng tỉ lệ, không
bóp méo).

- **Không xoay, không trôi, không parallax, không ăn theo `speed`.** Nó là "tấm nền của vũ trụ",
  không phải vật thể trong cảnh.
- Hạ sáng bằng `material.color = #9e9e9e` (62 %) — **không sửa file ảnh**, để đổi độ sáng chỉ
  cần sửa một số trong code.
- `setTheme` chỉ pha **8 %** màu chương vào ảnh — ảnh gốc vẫn là ảnh gốc.
- Gradientshader cũ vẫn còn làm phương án dự phòng khi thiếu ảnh (test node).

### 5.0b Lớp thứ 2 — ba đám tinh vân ẢNH THẬT, có trôi

Ảnh gốc 4k cắt thành ba đám (xem [`../prototype/src/ui/NGUON-ANH.md`](../prototype/src/ui/NGUON-ANH.md)):

| Texture | Ảnh gốc | Kích thước xuất | Vai trò |
|---|---|---|---|
| `nebula_a.jpg` | Tarantula Nebula (30 Doradus) 3840×2160 — teal/amber | 1920×1080 | đám lớn, phủ 75 % chiều cao màn |
| `nebula_b.jpg` | cùng ảnh, vùng xanh tím | 1440×972 | đám vừa, lệch trái |
| `nebula_c.jpg` | Carina "Mystic Mountain" (Hubble) | 960×1546 | đám dọc, chi tiết mạnh |

- **Mép ảnh được nướng vignette** (nhân với smoothstep 4 cạnh) nên khi cộng sáng mép tan hẳn
  vào nền — **không thấy khung chữ nhật**, không cần mask runtime.
- `AdditiveBlending`, `material.color = 0,72` + opacity 0,20–0,62 (sương đậm nhất, đám nhỏ nhạt
  nhất) → độ sáng nền giữ ở mức trung bình ~38/255, đủ tối để đạn và HUD nổi.
- **Có chuyển động thật**: trôi xuống 0,007–0,014 màn/giây (**0,5–1 % tốc độ lớp bụi nhanh nhất**),
  lắc ngang ±1 % biên độ, dịch theo `focus` 1,4 % (parallax yếu hơn lớp gần 13 lần).
- **Ngoại lệ có chủ ý:** theo luật `1/d²` thì tinh vân ở z −300 phải chậm hơn cả lớp sao z −260,
  tức gần như đứng im — mà D20 yêu cầu nhìn thấy nó chuyển động. Nên tinh vân được đẩy nhanh
  hơn luật, giống cách mảnh vụn được đẩy 2–4 lần. Đừng "sửa cho đúng luật" mà chưa xem bằng mắt.
- Trôi hết màn thì **sinh lại ở mép trên** với vị trí ngang ngẫu nhiên → lớp không bao giờ trống.
- **Không xoay.** Xoay ảnh tinh vân là thứ khiến mắt nhận ra "đây là ảnh dán".

Bố cục thử bằng chính các ảnh thật (ghép bằng PIL, không phải ảnh render của game):
[`previews/nen-d20-chuyen-dong.jpg`](previews/nen-d20-chuyen-dong.jpg) — ba khung t = 0 / 10 / 20 s,
dựng lại đúng toạ độ, độ mờ và phép cộng sáng của `backdrop.js`.

### 5.1 Một luật cuộn cho lớp tĩnh

```
tốc độ thế giới (đv/giây) = SCROLL / depth        SCROLL = 610
```

Chiều cao màn hình tại độ sâu `d` là `2·tan(fov/2)·d`, nên tốc độ **trên màn hình**:

```
screenSpeed(d) = SCROLL / (2·tan(fov/2)·d²)  ∝ 1/d²
```

Tức lớp gần không chỉ nhanh hơn tuyến tính — nó nhanh hơn theo bình phương. Đây là kiểu phóng
đại mà game bắn súng dọc vẫn dùng để "đã mắt" hơn thực tế.

Áp dụng cho: bụi (L6). Mảnh vụn (L5) là **đạo cụ** nên được đẩy nhanh hơn luật ~2–4 lần cho có
nhịp — đã ghi rõ trong code, đừng "sửa cho đúng luật" mà không xem lại bằng mắt.

### 5.2 Lớp gần thật sự (L7)

- 14 sprite bụi lớn + 7 vệt sáng, đặt ở `z = −1,7…−4,8` (tàu cách camera ~7 đơn vị) → **luôn
  vẽ đè lên tàu và đạn**.
- Chỉ sinh ở **rìa**: `|x| ≥ 0,58·nửa bề rộng`, không bao giờ ở giữa màn hình.
- Độ mờ 5–13 %, cộng sáng (additive) → không che thông tin gameplay.
- `renderOrder = 30/31`, `depthTest = true` → vẫn bị che nếu có gì gần hơn.

### 5.3 Camera trôi theo tàu (focus parallax)

`main.js` truyền `focus = playerX / bounds.x` (−1…1) xuống `backdrop.update`. Mỗi lớp dịch
ngang **ngược chiều** tàu, biên độ tăng dần khi tới gần:

| Lớp | Hệ số (× nửa bề rộng lớp) | Độ dịch trên màn hình khi tàu ở mép |
|---|---|---|
| tinh vân (L1) | 0,014 | ~1,4 % |
| lớp gần (L7) | 0,18 | ~9 % |

Giá trị được làm mượt (`lerp` hệ số 4,5/s) để không giật khi tàu đổi hướng.

Ngoài ra `speed` (hệ số làm chậm của game) được truyền xuống, nên nút **CHẬM 0,28×** làm cả nền
chậm lại — trước đây nền vẫn chạy 1× nên hiệu ứng slow-mo bị "lệch".

---

## 6. Quy tắc không được vi phạm

1. **Không lớp nào được cùng tốc độ với lớp khác.** Hai lớp cùng tốc độ = một lớp.
2. **Lớp gần phải che tàu.** Nếu không có gì che ngang tàu thì không có chiều sâu thật.
3. **Lớp gần không được vào giữa màn hình.** Chỉ rìa; opacity ≤ 15 %.
4. **Tương quan kích thước phải giữ**: đám tinh vân ≫ tàu ≫ sao. Thu nhỏ đám mây là mất ngay
   cảm giác "khổng lồ" (D20: Trái Đất/trạm đã bỏ, đừng thêm lại).
5. **Nền tối hơn HUD và địch.** Lớp xa nhất gần như đen; mọi thứ cần đọc phải sáng hơn nền.
6. **Sương mù thay cho viền nét ở lớp xa**: lớp xa ngả màu tinh vân và giảm tương phản, không
   thêm chi tiết.

---

## 7. Chỉnh ở đâu

| Muốn đổi | Sửa |
|---|---|
| Tốc độ cuộn tổng thể của nền | `backdrop.js` → `SCROLL` (610). Tăng = bay nhanh hơn. |
| Số lượng / cỡ sao | `starLayers` (`makeStarLayer(150, 260, 1, 4.0, 0.012, …)`) |
| Bụi 4 tầng | 4 dòng `makeDust(...)` |
| Lớp gần | khối `LỚP GẦN` (số sprite, `screenSpeed`, độ mờ) |
| Biên độ trôi theo tàu | `update()` → các số 0,02 / 0,05 / 0,10 / 0,18 |
| Đám tinh vân (vị trí/cỡ/tốc độ/độ đậm) | `backdrop.js` → `CLOUD_DEFS` + `NEB_K` |
| Màu tinh vân theo chương | `setTheme()` + `content.js` → `CHAPTERS[].theme` |

---

## 8. Kiểm tra bằng mắt (3 bước)

1. Vào màn chơi, **đứng yên 5 giây**: phải thấy ít nhất **3 tốc độ khác nhau** cùng lúc
   (sao gần như đứng, bụi vừa, vệt sáng vụt qua).
2. **Vuốt tàu sang hai mép**: nền phải trôi ngược lại, và mép màn hình trôi mạnh hơn tâm.
3. **Bấm CHẬM**: cả nền phải chậm theo, không chỉ tàu/địch.

Nếu bước 1 chỉ thấy một tốc độ → kiểm tra lại `SCROLL` và các dòng `makeDust`.
Nếu bước 2 không thấy gì → `main.js` chưa truyền `focus` xuống `backdrop.update`.

---

## 9. Bảng định lượng (yêu cầu D20) — mọi thứ đo được, không có từ mơ hồ

| Lớp | Ảnh / nguồn | Tốc độ (màn/giây) | Tỉ lệ so với lớp nhanh nhất | Vòng lặp | Ghi chú |
|---|---|---|---|---|---|
| L0 nền vũ trụ | Hubble Ultra Deep Field, 2560×2560 | **0** | 0 | không lặp — một tấm duy nhất | đứng yên tuyệt đối, phủ `cover` |
| L1 tinh vân | sương tinh vân xanh/lam (làm mờ 22 px) + Tarantula ×2, Carina ×1 — ảnh thật, nướng vignette | 0,007 – 0,014 | 0,5 – 0,9 % | trôi hết 2,7 màn thì sinh lại ở mép trên, x ngẫu nhiên | cộng sáng, không xoay |
| L2 sao xa | điểm sao 150 hạt | 0,006 | 0,4 % | quấn vòng ±hh | nhấp nháy 0,6 ± 0,06 |
| L3 sao giữa | 95 hạt | 0,010 | 0,6 % | quấn vòng | — |
| L4 sao gần | 48 hạt, màu ấm | 0,016 | 1 % | quấn vòng | — |
| L5 mảnh vụn | texture thiên thạch, 10 sprite | 0,17 – 1,0 | 11 – 64 % | sinh lại ở mép trên | tự xoay chậm |
| L6 bụi 4 tầng | hạt sáng | 0,07 – 1,56 | 4 – 100 % | quấn vòng | — |
| L7 lớp gần | 14 mote + 7 vệt, **trước cả tàu** | 2,2 – 4,1 | 141 – 263 % | sinh lại ở mép | chỉ ở `|x| ≥ 0,58·hw` |

Quy ước tốc độ: **1 đơn vị = một chiều cao màn hình mỗi giây**, đo trên màn hình chứ không phải
trong không gian 3D. Nhìn cột "tỉ lệ" là thấy dải động ~440 lần giữa L1 và L7 — đó là thứ mắt đọc
thành chiều sâu; nếu nén còn 20–30 lần thì cảnh sẽ dẹt lại.

**Bốn hiệu ứng chuyển động của bản mẫu, đối chiếu với game:**

| Hiệu ứng trong bản mẫu | Game làm gì | Vì sao |
|---|---|---|
| camera dolly forward | **không có** — game bắn súng dọc nhìn từ trên, camera cố định, thế giới trôi xuống | đổi sang dolly sẽ phá gameplay 2D thuần (D12) |
| cuộn vô hạn kiểu tile | trôi hết khung thì **sinh lại ở mép đối diện** | không cần ảnh tileable, không thấy mối nối |
| speed lines | 7 vệt sáng dài ở hai rìa (L7) | tạo cảm giác tốc độ mà không tốn post-process |
| motion blur ở rìa | **không dùng post-process**; mép màn hình tối dần bằng lớp gần + bloom | blur toàn khung ở 60 fps trên Android tụt khung hình |
