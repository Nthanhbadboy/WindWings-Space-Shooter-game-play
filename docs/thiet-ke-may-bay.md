# Thiết kế máy bay 2D "giả 3D" — sổ tay + tư liệu cho AI

Tài liệu này ghi lại **cách nghĩ và cách làm** khi dựng tàu cho `prototype/shipdemo.html`
(bản thử 2D). Mục tiêu: người (hoặc AI) sau này đọc xong có thể tự thiết kế **máy bay
mới** cho cùng hệ mà không phải đoán lại từ đầu.

Đọc kèm: `prototype/src/shipdemo/` (code), `docs/nghien-cuu-sprite-dong.md` (bộ sprite
động tham khảo), `docs/previews/tau-*.gif` (kết quả).

---

## 1. Ba nguyên tắc gốc

1. **Chỉ 2D.** Không mesh, không phối cảnh, không shader. Mọi chuyển động là
   **dời / xoay / co giãn trong mặt phẳng**. Cái làm người xem tưởng 3D là **màu và sáng**,
   không phải hình học.
2. **Bộ phận rời, có khớp.** Mỗi thứ chuyển động phải có **khớp nhìn thấy được**: bản lề
   có bu-lông, xi-lanh, càng kẹp, cột sống, rãnh trượt. Không có "phép thuật" — thứ gì
   xoay thì phải có chỗ xoay, thứ gì thò ra thì phải có chỗ chứa nó.
3. **Súng phải có nòng, đạn phải có nguồn.** Tia laser chỉ được vẽ từ toạ độ do chính tàu
   khai báo trong `muzzles()`. Không bao giờ vẽ tia từ mép ảnh hay từ một điểm "chắc là
   đẹp". Đây là lỗi người dùng đã bắt: *"laser phải bắn ở đâu sao lại xuất hiện ở ngoài"*.

---

## 2. Kiến trúc code

```
src/shipdemo/
├── core.js        cảnh: nền sao, vị trí tàu, pha bắn, vẽ tia từ muzzles()
├── fx.js          đồ dùng chung: sao trôi, lửa 3 hình, laser, quầng sáng (glowDot)
├── ships/
│   ├── omen.js     tàu 1 — CÁNH DƠI  (dùng ảnh PNG, có bản vector dự phòng)
│   ├── biomech.js  tàu 2 — SINH CƠ   (vector, súng dưới cánh)
│   └── vertebra.js tàu 3 — XƯƠNG SỐNG(vector, sinh cơ ở thân)
└── parts.js       đường dẫn ảnh tách rời của omen
```

### Hợp đồng của một module tàu

| Thành phần | Kiểu | Bắt buộc | Ý nghĩa |
|---|---|---|---|
| `id` | string | ✓ | khoá để chọn tàu (`'omen'`) |
| `label` | string | ✓ | tên hiện trên tab, vd `'CÁNH DƠI'` |
| `usesArt` | boolean | | `true` = có thể dùng lớp ảnh PNG |
| `laserTint` | `[r,g,b]` | ✓ | màu tia laser của tàu |
| `muzzles(s, t, ph)` | `→ [{x, y, angle, scale?}]` | ✓ | **đầu nòng** trong hệ toạ độ cảnh (đã dời tới tâm tàu, **chưa** nhân scale) |
| `draw(ctx, {s, t, ph, img, art})` | void | ✓ | vẽ toàn bộ tàu; `s` = scale, ctx đã dời tới tâm tàu |
| `skeleton(ctx, s, t, ph)` | void | | khung xương debug: gốc xoay, ống xả, đầu nòng |

`ph` (pha) do `core.js` cấp:

```js
{ stage: 'idle' | 'windup' | 'fire' | 'recover', k, wing, charge, fire, recoil }
```

- `k` 0→1 trong từng đoạn; `charge` = độ gồng; `fire` = độ sáng của tia;
  `recoil` = độ giật; `wing` = độ ngóc cánh (−0.5 … 1).
- **Đừng** tự đếm thời gian trong module tàu; chỉ đọc `ph` + `t`.

### Hệ toạ độ

- Mọi toạ độ thiết kế dùng **hệ 512×512** (`BASE = 512`), tâm tàu ở `(256, 256)`.
- Lúc vẽ: `ctx.translate(-BASE*s/2, -BASE*s/2); ctx.scale(s, s)` (helper `drawInBase`).
- Lúc trả `muzzles()`: trả toạ độ **đã nhân `s` và đã trừ tâm**:
  `x: (bx - 256) * s`, `y: (by - 256) * s`.
- Muốn một điểm "dính" vào bộ phận xoay (cánh, sườn): dùng **một hàm frame** chung cho cả
  vẽ và tính toạ độ (`wingFrame(side, s, angle).map(bx, by)`), đừng tính hai lần hai kiểu.

---

## 2.5. Vật liệu & màu: đây là chỗ dễ "dại" nhất (D15)

**Vấn đề gặp phải:** tàu vẽ bằng vài mảng `fillStyle` một màu + một gradient đơn giản ⇒
nhìn "phẳng, màu dại, chưa ra công nghệ". Ảnh tham khảo trên mạng đẹp vì có **kết cấu
bề mặt**, không phải vì có nhiều màu.

**Quy tắc màu "công nghệ":**
1. **Nền ít bão hoà** (thép xanh-xám, gần đen ở vùng tối). Màu bão hoà KHÔNG phủ kín thân.
2. **Đúng một màu phát xạ** cho cả tàu (cyan của `biomech`, tím của `omen`, hổ phách của
   `vertebra`) — chỉ dùng ở khe, nòng, lõi, ống xả.
3. **Một ánh bù** ở phía đối diện nguồn sáng. Ví dụ `biomech`: sáng trên-trái màu lạnh,
   hắt **hổ phách ấm** từ động cơ phía dưới (complementary) ⇒ bề mặt "có đời sống".
4. **Không dùng màu tinh khiết** (`#00ffff`) cho mảng lớn; phát xạ lõi mới được gần trắng.

**Bộ hàm vật liệu dùng chung — `src/shipdemo/mat.js`:**

| Hàm | Cho ra cái gì |
|---|---|
| `techPlate(ctx, pts, opts)` | một tấm giáp: gradient chéo 4–6 màu + viền tối dày + rim gradient + bóng trong + phát xạ mép trong |
| `glowLine(ctx, pts, color, {w,a})` | đường năng lượng 4 lớp (quầng → lõi trắng) không cần `filter: blur` |
| `tube(ctx, x0, y0, x1, y1, w)` | ống tròn: sáng lệch trục trái, tối hai rìa → đọc ra hình trụ |
| `band`, `vents`, `rivets`, `specular` | đai ống, khe tản nhiệt phát sáng, đinh tán, vệt phản quang |

Bảng màu sẵn: `STEEL`, `BRONZE`, `CERAMIC`. Mỗi tàu chọn **một** bảng + **một** màu phát xạ.

**Thứ tự "nấu" một tấm giáp** (đừng bỏ bước nào):
nền tối → gradient khối → viền ngoài gần đen → bóng trong (clip) → rim sáng mảnh →
đường ghép tấm + đinh tán → (tuỳ chọn) phát xạ mép trong.

## 2.7. LUẬT SỐ MỘT: phải ra CHIẾN ĐẤU CƠ (D16)

Trước khi bàn màu hay chi tiết: người xem phải nhận ra **máy bay chiến đấu không gian**.
Nếu silhouette đọc thành "con cá", "viên đạn" hay "con bọ" thì mọi chi tiết đều vô nghĩa.
Muốn vậy **bắt buộc** dựng trên `ships/fighter.js` — bộ hình học chuẩn, đủ **6 bộ phận**:

| # | Bộ phận | Vai trò đọc hình |
|---|---|---|
| 1 | **mũi nhọn dài** | cho hướng bay; phải hẹp, dài, nhọn |
| 2 | **buồng lái** ngay sau mũi | dấu hiệu "có người lái" mạnh nhất |
| 3 | **thân thon** (~1/7 sải cánh) | nếu thân phình → đọc ra "cá/bọ" |
| 4 | **cánh xuôi ra sau** | mép trước là đường thẳng dài, mới ra "jet" |
| 5 | **cánh đuôi / vây** | tách khỏi "viên đạn" |
| 6 | **2 ống xả song song** | xác nhận "động cơ phản lực" |

Thiếu **bất kỳ** mục nào là hỏng: bản trước của `vertebra` (thân giọt nước + sườn) đọc
thành con bọ; bản `biomech` đầu tiên (thân bầu + cánh lá) đọc thành cá đuối.

**Thứ tự vẽ để không bị che:** động cơ/lửa → nòng dưới cánh → cánh xuôi → cánh mũi →
vây đuôi → thân → lõi/giáp → **buồng lái sau cùng**. Buồng lái luôn nằm trên cùng.

**Tỉ lệ vàng** (hộp 512, tàu chiếm y 38…462): mũi `y 38`, buồng lái `y 100…212`,
gốc cánh `y 196…226`, sải cánh tới `x 470/42`, vây đuôi `y 392…460`, ống xả `y 441`.

Có khung rồi thì **cá tính đặt lên trên khung**: `biomech` thêm giáp vai + lõi; `vertebra`
thêm đốt sống + sườn; `omen` giữ cánh dơi làm cánh chính và thêm canard/vây đuôi nhỏ.

## 3. Bốn kiểu "súng" đã dùng — chọn theo dáng tàu

| Kiểu | Dùng ở | Cách đọc ra | Khi nào nên chọn |
|---|---|---|---|
| **Cầu năng lượng hội tụ** | `omen` | 2 đầu cánh + mũi tàu chụm vào một quả cầu trước mũi; cầu sáng dần rồi bắn | tàu có **cánh nhọn** và mũi nhọn; muốn "phép thuật công nghệ" |
| **Nòng dưới cánh** | `biomech` | chỉ thấy **đầu nòng thò ra trước mép cánh** + 2 càng kẹp; phần giữa bị cánh che | tàu có **cánh to bản**, và **súng thiết kế xấu** (nòng thô, hộp to) → giấu đi |
| **Nòng trong thân** | `vertebra` | nòng trượt ra khỏi **mũi**, chạy trong rãnh cột sống | thân dài, muốn sinh cơ ở **thân** |
| **Cầu hội tụ + cánh dơi** | `omen` | 2 đầu cánh + mũi chụm vào quả cầu trước mũi | tàu có cánh mảnh, hữu cơ — **không** gắn hộp súng |
| **Tháp pháo trên thân** | (bản cũ, đã bỏ) | tháp tròn + nòng nhô lên | chỉ khi thân đủ rộng và tháp **không** mọc trên cánh |

**Bài học bị người dùng chê (D14):** tháp pháo **mọc trên mặt cánh dơi** ⇒ nhìn xấu, vì
cánh dơi vốn là chi tiết mảnh, có gu; gắn hộp kim loại lên là phá dáng.

**Nguyên tắc "súng đẹp thì khoe, súng xấu thì giấu" (D15):**
- **Súng/nòng được thiết kế đẹp** (thuôn, nhiều đốt, có khoá nòng, có khe năng lượng) →
  **khoe ra**: đặt trên thân, hai bên mũi, hoặc thành cụm đối xứng nhìn thấy rõ.
- **Súng thô/xấu, hoặc không hợp dáng tàu** → **giấu dưới cánh / trong thân**, chỉ để lộ
  đầu nòng + cơ cấu kẹp.
- Cánh **mảnh, có gu** (cánh dơi) → không gắn hộp lên; dùng **hội tụ năng lượng**.
- Cánh **to bản, thiên kim loại** → giấu nòng dưới cánh là hợp lý.

### 3.1 Cầu năng lượng hội tụ (công thức 4 lớp)

Vẽ **theo thứ tự**, lớp 1 và 3–4 dùng `globalCompositeOperation = 'lighter'`, lớp 2 vẽ thường
để giữ được vùng tối:

1. **quầng**: `createRadialGradient` bán kính `≈3.8r`, alpha thấp.
2. **khối cầu**: gradient lệch **lên-trái** (`x − 0.36r, y − 0.40r`) → trắng → tím nhạt →
   tím → tím thẫm ở rìa. Đây là thứ tạo cảm giác **khối**, không phải hình tròn phẳng.
3. **viền sáng rìa** (2 cung tròn, không viền kín) + **chấm phản quang** lệch lên-trái.
4. **vành nghiêng xoay** (2 ellipse mảnh, quay ngược chiều nhau) + 6 tia lửa nhỏ quay quanh.

Cộng thêm **3 "móng" năng lượng** cong từ 3 điểm hội tụ vào cầu (`drawClaws`) và 2 tia
năng lượng có hạt sáng chạy dọc (`drawFeedArcs`) — đó là thứ khiến người xem hiểu
"ba đầu nhọn đang chụm vào quả cầu".

Toạ độ chuẩn của `omen`: mũi `(256, 29)`; đầu cánh khi gồng hết `≈(247, 72)` và
`(265, 72)`; **tâm cầu `(256, 47)`** — đặt ở giữa ba điểm, không dán lên mũi.

### 3.2 Nòng dưới cánh

Thứ tự vẽ quyết định "nằm dưới": `động cơ → nòng → cánh → thân → càng kẹp`.
Phần nòng bị cánh che là **chủ ý**; chỉ để lộ **đầu nòng + khoá nòng** ở trước mép cánh
và **đuôi nòng** ở sau. Thêm 2 **càng kẹp** trượt ra khi gồng để giải thích cơ cấu.

### 3.3 Nòng trong thân

Nòng nằm trong **rãnh cột sống**, trượt dọc rãnh. Gồng → nòng thò ra; bắn → giật lùi
(vẫn còn trong thân). Nhìn từ trên xuống chỉ thấy đầu nòng + khoá nòng + rãnh sáng.

---

## 4. Ngữ pháp chuyển động

| Lớp | Nhịp | Biên độ gợi ý |
|---|---|---|
| thân | `sin(t·1.9)` nhún + nghiêng `sin(t·1.15)·0.012 rad` | 2–3% kích thước |
| cánh | thở `sin(t·2.1)·0.014` + vỗ `sin(t·4.4)·0.014` (tắt dần khi gồng) | 1–2° |
| gồng | 0 → 1 trong `windup 0.55 s` | cánh ngóc 0.42 rad (omen) |
| bắn | `fire 0.5 s` | cánh bật xuống, giáp khép 1 nấc, nòng giật |
| hồi | `recover 0.75 s` | về 0 |
| lửa đuôi | **3 hình**, 15 hình/giây, 2 ống **lệch pha 1 khung** | dài 96 đơn vị |
| chớp đầu nòng | **3 hình**: to → vừa → tắt (theo `k < 0.1 / 0.24 / 0.4`) | — |
| cơ cấu (giáp, sườn, đốt sống) | **3 nấc** qua `stepped()` = `round(k*3)/3` pha với `k` | — |

`stepped()` là mẹo quan trọng: chia 3 nấc rồi trộn với giá trị mượt (60/40) ⇒ cảm giác
**bản lề khoá** chứ không phải cao su. Học từ bộ sprite động: 15 khung = 5 tư thế × 3 khung lửa.

---

## 5. Công thức "2D mà tưởng 3D"

1. **Viền tối dày + viền sáng một bên.** `stroke` đen 6–8 đơn vị bao ngoài silhouette, rồi
   một `stroke` sáng alpha ~0.45–0.55 **chỉ ở mép hướng sáng** (giả định sáng từ trên-trái).
2. **Gradient chéo, không gradient dọc.** `createLinearGradient` từ góc trên-trái xuống
   dưới-phải, 3–5 điểm dừng; mép dưới luôn tối gần như đen.
3. **Ánh sáng cục bộ đúng chỗ**: quầng ở đầu nòng, ở ống xả, ở lõi; dùng `lighter` +
   `glowDot()`; **không** rải sáng đều cả tàu.
4. **Lớp tối khi biến hình** (`*_dim.png` của omen): cánh cụp vào thì tối đi ⇒ đọc ra khối.
5. **Bóng mờ dưới thân** (`ellipse` đen alpha 0.35 ngay dưới tàu) ⇒ tàu "nổi" khỏi nền.
6. **Vành nghiêng xoay** trên quả cầu / lõi ⇒ tín hiệu chiều sâu mạnh nhất trong 2D.

---

## 6. Áp ý tưởng "sinh cơ" (biomech) cho tàu mới

Sinh cơ **không phải** cứ thêm gai thịt. Nó là **bốn mẫu cơ cấu** sau, dùng đúng chỗ:

| Mẫu | Đặt ở đâu | Vì sao hợp lý | Chuyển động |
|---|---|---|---|
| **Cột sống + đốt** | dọc trục thân | thân tàu vốn đã đối xứng trục; cột sống = đường năng lượng | các đốt **tách ra theo 3 nấc** |
| **Sườn ôm** | hai bên thân, **bên trong** silhouette | sườn là chi tiết "dính" vào giáp, không thò ra ngoài | xoay quanh khớp sát cột sống, nhấc lên lộ đường sáng |
| **Tấm giáp trượt** | vai / hông | như cửa giáp của máy móc | trượt ra + xoay mở, có xi-lanh dẫn động |
| **Gân / tua cảm biến** | đuôi, mép sau | chuyển động nhỏ, gợi "sống" mà không phá dáng | đung đưa `sin(t·1.7)` biên độ nhỏ |

**Giới hạn bắt buộc:**
- Sinh cơ **không được phá silhouette**. Sườn/gai phải nằm **trong** hoặc **sát** mép giáp;
  thứ thò ra ngoài chỉ được là **nòng súng** và **đầu cánh**.
- Mỗi chi tiết sinh cơ phải có **lý do cơ khí**: cột sống dẫn năng lượng, sườn giữ giáp,
  tua là cảm biến. Không có chi tiết "để cho ngầu".
- Màu: chọn **một cặp** (năng lượng + ánh kim) rồi giữ đúng cặp đó cho cả tàu.
  `biomech` = ngọc lam + xám thép; `vertebra` = hổ phách + xương ngà.

---

## 7. Quy trình 7 bước để làm một tàu mới

1. **Chọn kiểu súng trước** (mục 3) — vì nó quyết định hình dáng thân/cánh.
2. **Vẽ silhouette 512×512 bằng số**: liệt kê các điểm mốc (mũi, vai, gốc cánh, đuôi),
   kiểm tra đối xứng qua `x = 256`.
3. **Đặt khớp**: gốc xoay cánh, khớp sườn, rãnh trượt giáp, gốc nòng. Ghi thành hằng số
   đầu file (`PIVOT`, `SPINE_X`, `BARREL_Y`…).
4. **Viết `muzzles()` trước `draw()`** — làm ngược lại rất dễ sinh ra tia "từ hư không".
5. **Vẽ theo thứ tự lớp**: xa → gần (`động cơ → bộ phận dưới → cánh → thân → giáp → chi
   tiết trên → nòng/quả cầu`). Ghi chú lý do ở từng lớp.
6. **Gắn chuyển động**: thân/cánh đọc `ph`; cơ cấu dùng `stepped()`; lửa dùng `flameFrame(t, i)`.
7. **Chạy QA** (mục 9) rồi xuất GIF xem bằng mắt.

---

## 8. Thẻ mô tả tàu (mẫu điền — đưa cho AI khác)

```yaml
id: ten-tau
label: TÊN HIỆN TRÊN TAB
vai_tro: (bắn tỉa / cận chiến / oanh tạc …)
kieu_sung: hoi_tu_nang_luong | nong_duoi_canh | nong_trong_than
mau_nang_luong: [r, g, b]
mau_anh_kim: '#rrggbb'
silhouette:
  mui: [x, y]            # mũi tàu
  vai: [x, y]
  goc_canh: [x, y]       # nếu có cánh xoay
  duoi: [x, y]
  rong_toi_da: px        # bề ngang lớn nhất ở hệ 512
khop:
  canh:  [x, y] + bien_do_rad
  suon:  [x, y] + goc_mo_rad
  nong:  dai_nghi + dai_khi_gong + do_giat
sinh_co:
  - cot_song: co / khong
  - suon: so_cap
  - tam_giap_truot: co / khong
  - tua_cam_bien: so_sai
giong_di: (1 câu mô tả cảm giác muốn người xem thấy)
```

Ví dụ đã làm — `vertebra`: *"một con thú xương sống bọc giáp, thở bằng năng lượng hổ phách,
súng chạy trong xương sống và chỉ thò mõm ra ở mũi"*.

---

## 9. Kiểm tra trước khi giao (QA)

Không có trình duyệt trong môi trường này, nên QA bằng ba lớp:

1. **Harness chặn lỗi toán** — bọc `ctx` bằng object thuần (⚠️ **không dùng `Proxy`**, napi
   không unwrap được), ném lỗi khi gặp số không hữu hạn, bán kính âm, `drawImage` với ảnh rỗng.
   Quét: 3 tàu × ảnh/vector × 4 khổ (dọc/ngang) × 6 pha × 4 mốc thời gian → 1728 trường hợp.
2. **Bundle thật** — build `vite`, rồi chạy chính file `dist/assets/shipdemo-*.js` trong
   `jsdom` + `@napi-rs/canvas` (giả lập `Image`), bấm tab đổi tàu, chạy 40 khung, đọc
   `#errBox` / `#dbgPill` / `window.__shipDemo.loaded`.
3. **GIF** — `npm run render:ship2d` rồi `python3 tools/ship2d_gif.py <thư mục> <tên>`,
   xem bằng mắt (đây là bước bắt được "xấu"/"vô lý" — thứ test không bắt được).

Checklist nhanh:

- [ ] Không có số không hữu hạn / bán kính âm ở mọi khổ + mọi pha
- [ ] `muzzles()` khớp đúng đầu nòng ở **mọi** pha (bật `XƯƠNG` để thấy chấm hồng)
- [ ] Mọi bộ phận chuyển động đều có khớp nhìn thấy
- [ ] Tàu vẫn đọc được khi **thiếu ảnh** (đường vector dự phòng)
- [ ] Lửa đuôi đúng 3 hình; chớp nòng đúng 3 hình; cơ cấu đúng 3 nấc
- [ ] Silhouette không bị chi tiết sinh cơ phá vỡ
- [ ] `npm test` (sim + ui của game 3D) vẫn xanh

---

## 10. Tư liệu tham khảo

- **Bộ sprite động** (học nhịp & tách lớp): *Pixel SHMUP Free*, 15 khung tàu = 5 tư thế ×
  3 khung lửa, kèm 8 khung nổ — xem `docs/nghien-cuu-sprite-dong.md`. Không phát hành lại.
- **Kenney — Space Shooter Extension** (CC0): atlas `spaceShooter2_spritesheet.png` + XML;
  tham khảo cách đóng gói sprite.
- **Quaternius** (CC0): model 3D tàu — dùng cho bản 3D, không dùng ở đây.
- Ảnh concept tham khảo (chỉ để lấy ý tưởng, **không** đưa vào repo):
  - tàu giáp xám có đường năng lượng phát sáng dọc mép tấm (ý tưởng "giáp + rãnh sáng");
  - bản vẽ line-art tàu "Mantis" nhiều tấm giáp xếp lớp (ý tưởng chia đốt thân);
  - ảnh sinh cơ tối, ánh lạnh + điểm ấm (ý tưởng ánh bù hổ phách ở đuôi `biomech`).

## 11. Những lỗi đã mắc (để không lặp lại)

| Lỗi | Hậu quả | Cách tránh |
|---|---|---|
| Vẽ laser từ mép cánh theo toạ độ ước lượng | tia "mọc từ hư không" | `muzzles()` + vẽ chấm debug bằng `XƯƠNG` |
| Gắn tháp pháo lên cánh mảnh | phá dáng, bị chê xấu | chọn kiểu súng theo **độ dày** của cánh |
| Vẽ tàu sau khi `await` ảnh | mất hình nếu ảnh lỗi | vẽ ngay bằng vector, ảnh là lớp phủ |
| Dùng `Proxy` bọc `CanvasRenderingContext2D` | napi panic | bọc bằng object thuần |
| Chi tiết sinh cơ thò ra ngoài silhouette | rối, mất dáng | sườn/gai nằm trong hoặc sát mép giáp |
