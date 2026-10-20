# Màn chơi mới — nền 3 lớp, tàu vẽ tay, “bắn ruồi”

Tài liệu mô tả đợt nâng cấp **cảnh gameplay** (không phải giao diện menu) cho `prototype/`.

## 1. Nền 3 lớp

| Lớp | Nội dung | Tệp / kỹ thuật |
|---|---|---|
| **Đáy** | Bầu trời gradient trong trẻo (có dither chống vệt), 4 tinh vân xa, **Trái Đất 3D** (mây, đèn thành phố, sương chân trời, quầng khí quyển) + 3 tầng sao parallax | `src/backdrop.js`: sky dùng `ShaderMaterial` gradient; Trái Đất là mặt cầu 96×56 với shader ngày/đêm; sao `THREE.Points` gắn vào camera, `depthTest` bật nên bị hành tinh che |
| **Giữa** | **Bụi sáng + mảnh vụn trôi THẲNG XUỐNG** theo trục Y của camera (4 tầng: 2 tầng hạt mờ xa, 2 tầng vệt sáng gần) | mọi lớp nằm trong không gian camera nên "xuống" luôn đúng hướng cuộn dọc màn hình ở mọi tỉ lệ máy |
| **Trên** | Vùng giao chiến: tàu, địch, đạn, nổ | `src/game.js` |

Bố cục Trái Đất đã được **kiểm tra bằng phép chiếu**: tâm `(0, -110, -40)`, bán kính `30` → vành hành tinh nằm ở **~60 % chiều cao màn hình**, hai bên mép tràn ra ngoài khung (390×844).

Ảnh nền:
- ~~`src/ui/earth.jpg` — sinh bằng `docs/tools/planet_art.py`~~ → **D19** thay bằng map NASA thật,
  **D20 bỏ hẳn Trái Đất** khỏi nền. Xem `prototype/src/ui/NGUON-ANH.md`.
- `src/ui/bg_nebula_1.jpg` — tinh vân vẽ tay, **nay chỉ dùng làm nền CSS của màn UI**, không còn
  trong cảnh 3D (D20).

## 2. Tàu trong màn chơi = ảnh vẽ tay

- 8 sprite top-down 512²: `src/art/game/<id>.png` (striker, zenith, challenger, spitfire, insurgent, executioner, omen, dispatcher).
  Sinh bằng `docs/tools/extract_game_sprites.py` từ ảnh gốc trong `docs/asset-samples/raw_sprite_*.png` (key nền magenta/lime → PNG trong suốt).
- `src/art.js` khai báo **URL tĩnh** cho từng ảnh — bắt buộc, vì Vite chỉ đóng gói được `new URL('chuỗi tĩnh', import.meta.url)`.
- `Game._createPlayer()` dựng `THREE.Sprite` với `textures.shipArt[cfg.ship.id]`, nên **đổi tàu là đổi ảnh trong màn chơi**.
- Drone hộ vệ dùng cùng ảnh, nhuộm cyan, nhỏ hơn 1.15 đơn vị.
- Nghiêng thân khi bay ngang: `sprite.material.rotation` (Sprite là billboard nên `group.rotation.z` không có tác dụng).

## 3. Địch kiểu “bắn ruồi” — 11 loại, kích cỡ ruồi

| Loại | Ảnh | Bắn? | Hành vi |
|---|---|---|---|
| `swarm` | wasp | ✗ | lao thẳng, lượn sin |
| `skimmer` | wasp (xanh) | ✗ | lao nhanh, lượn biên độ lớn |
| `drone` | wasp (lam) | ✗ | lao chậm hơn |
| `raider` | wasp (hồng) | ✗ | lao nhanh |
| `meteor` | meteor | ✗ | trôi + xoay |
| `spinner` | hornet (hồng) | ✗ | **lượn vòng tròn** quanh một điểm |
| `brute` | hornet (đỏ) | ✗ | ủi chậm, máu dày |
| `gunner` | hornet | ✓ | giữ khoảng cách, bắn ngắm |
| `interceptor` | hornet (cam) | ✓ | lao + bắn 2 tia |
| `bomber` | hornet (tím) | ✓ | bắn chùm 4 sao plasma |
| `tank` | hornet (lam) | ✓ | bắn 3 tia đạn nặng |

Pool địch được bổ sung thêm `skimmer`, `spinner`, `brute` ở mọi chế độ (`Game.start`).

**Cỡ:** tất cả đã thu nhỏ còn ~60 % trước đây (`swarm` 0.62, `skimmer` 0.52…) để đúng chất “ruồi”.

**Đường vào:**
- `from: 'top'` — sinh ở `z = zMin - 1.2` (ngoài mép trên), bay xuống.
- `from: 'left' | 'right'` — sinh ở `x = ±(bounds.x + 1.4)` (ngoài mép ngang), bay ngang qua màn hình và hơi chúi xuống, tự xoay sprite theo hướng bay.
- Mỗi đợt campaign/endless đều có thêm 2–5 con bay ngang vào từ hai mép (`_buildCampaignWave`, `_buildEndlessWave`).

## 4. Đạn nhiều kiểu

**Người chơi** — theo tàu (`FIRE_STYLE`):

| Kiểu | Tàu | Hình |
|---|---|---|
| `bolt` | striker, spitfire, omen | tia mảnh, nhanh |
| `star` | zenith, executioner | sao plasma 4 cánh |
| `heavy` | challenger, insurgent, dispatcher | đạn dày, chậm hơn, to hơn |

**Địch** — `_enemyShot(from, angle, speed, style)` với `bolt` / `star` (sao plasma) / `heavy` (lục giác cam).

**Boss** — `_geoShot()` / `_geoShotAngle()`: đạn hình học xoay, có bán kính va chạm và sát thương riêng từng viên.

## 5. Boss robot — chém + đạn hình học theo nhịp

Boss không còn là model GLB; giờ là **robot vẽ tay** (`src/art/game/boss_imperial|pancake|dreadnought.png`, 768²):

- **Nhịp:** `beat` giảm dần, mỗi phách gọi `_bossAttack()`. Pha 2 (≤ 50 % máu) rút phách 1.12 → 0.78 s, đổi hào quang sang đỏ, bắn vòng chào.
- **Đạn hình học** (sinh bằng canvas trong `src/textures.js`, không thêm file ảnh): `diamond`, `square`, `triangle`, `hex`, `star`, `ring`, `needle`, `cross`. Mỗi boss có 2 hình riêng + màu riêng.
- **5 kiểu đòn:** `fan` (quạt 5–7 viên), `ring` (vòng 14–18 viên + 1 viên to), `spiral` (3 tay xoắn), `wall` (tường đạn có 2 ô trống), `cross` (4 viên chữ thập), `summon` (gọi ruồi).
- **Chém:** `slash` → boss lao tới cột mục tiêu, cột cảnh báo đỏ nhấp nháy hẹp dần (0.5–0.66 s), rồi **chém** — luồng sáng dọc, 7 tia lửa, rung màn hình, sát thương 26 nếu đứng trong cột.
- Hào quang + lưỡi năng lượng là sprite sinh bằng canvas.

## 5b. Nổ “hoành tráng” — 5 lớp

`Game._boom()`:
1. 9 khung lửa (Kenney explosions)
2. **sóng xung kích** loang (sprite vòng, scale easing, mờ dần)
3. **tia lửa** bắn toả (6–12 hạt, có trọng lực + nảy)
4. **mảnh vỡ** xoay tít (3–6 sprite thiên thạch, rơi và nảy)
5. rung camera (`shake`) + flash lõi

Giới hạn `shards ≤ 70` để giữ FPS trên máy Android yếu.

## 6. Sửa lỗi “màn hình xám khi dính đạn”

**Nguyên nhân:** `hud.damageFlash()` gắn class `.on` cho `#flash` nhưng **không bao giờ gỡ**. CSS cũ:
```css
#flash { background: #ffdede; }
#flash.on { opacity: 0.5; }
```
→ lần trúng đạn đầu tiên là tấm phủ trắng hồng 50 % nằm vĩnh viễn trên màn hình (nhìn như bị xám).

**Cách sửa:**
- `#flash` đổi thành **vignette đỏ** ở rìa (không phủ trắng giữa màn hình).
- `.on` chạy animation `dmg-flash` **tự kết thúc về opacity 0** (`animation-fill-mode: both`).
- `damageFlash()` vẫn `setTimeout(…, 380)` gỡ class làm lưới an toàn.

## 7. Chạy & kiểm tra

```bash
cd prototype
npm run dev     # xem Live Preview
npm test        # mô phỏng gameplay + kiểm tra UI
npx vite build
```

Vì `art.js`/`ui.js`/`hud.js` khai báo URL tĩnh, ảnh sprite, porthole và 27 icon đều được **đóng gói vào `dist/`** (trước đây bản GitHub Pages bị 404 vì dùng `new URL` động).


## 8. Ghi chú kỹ thuật (đợt 2)

- `src/world.js` giờ chỉ còn **đèn** — toàn bộ bầu trời/hành tinh/tinh vân cũ đã bỏ.
- `src/textures.js`: đạn hình học, lưỡi chém, tinh vân, hạt bụi… đều **sinh bằng canvas lúc chạy**, không thêm file ảnh. Có fallback `DataTexture` để chạy được ngoài trình duyệt (test node).
- Không nạp GLB nào nữa (`assets.js` chỉ tải texture) → thời gian vào trận giảm mạnh.
- Trái Đất nằm ở `(0, -110, -40)`, bán kính 30; mặt trời lệch `(-0.86, 0.30, 0.42)` để thấy rõ đường phân giới ngày/đêm và đèn thành phố.

## 9. Đợt 3 — boss & tàu "sống", nền có trạm, icon vẽ tay

**Boss không còn đứng im.** Mỗi boss giờ có một vòng đời diễn hoạt riêng:

- **Nhập trận**: lao từ `z = -24, y = 5.6` vào sân, phóng to dần rồi rung màn hình khi dừng.
- **Di chuyển**: cứ 1,4–3,5 s chọn điểm đứng mới (rộng 64–80 % bề ngang), trượt có quán tính, **nghiêng thân theo đà**, nhô lên hạ xuống theo nhịp thở.
- **Lấy đà trước mỗi đòn**: đứng khựng lại 0,24–0,40 s, lõi năng lượng ở ngực sáng dần rồi mới bắn → người chơi đọc được đòn.
- **Giật lùi + loé họng súng** mỗi loạt đạn; **trúng đạn thì thân giật và loé trắng**.
- **2 vệ tinh** bay vòng quanh, tự bắn tỉa; pha 2 quay nhanh hơn, hào quang đỏ.
- **Chém**: nghiêng người dồn về cột cảnh báo, rung nhẹ khi lấy đà, rồi bổ xuống.
- **Tan rã**: thân xoay trôi, nổ 9 mảng theo nhịp, vệ tinh văng ra, kết bằng một cú nổ lớn.

**Tàu người chơi**:

- Sửa lỗi lớn: luồng lửa trước đây nằm **giữa thân** — giờ là **hai luồng ở đúng hai ống xả**, dài/ngắn theo tốc độ.
- Nghiêng vào hướng bay (giới hạn 0,26 rad để ảnh vẽ không bị "tấm bìa"), co giãn theo tốc độ dọc, nhún nhẹ khi đứng yên.
- **Loé súng** ở hai đầu cánh mỗi lần bắn + **vệt tốc độ** (5 bản sao mờ) khi lướt nhanh.
- **Quầng khiên** xanh nhấp nháy khi còn lá chắn.

**Nền — trạm không gian khổng lồ** (theo ảnh tham chiếu màn chơi):

- 3 **vành trạm** (torus có vỏ panel kim loại + viền phát sáng + 26 đèn) ở ba độ xa, trôi xuống và xoay rất chậm → parallax.
- 4 **dầm bo** hai mép màn hình (gần hơn, trôi nhanh hơn), mép trong ăn vào 28 % nửa bề ngang.
- Thêm 2 đám tinh vân gần (z −120, −128) để màu sắc dày hơn; màu vành/dầm ăn theo theme từng chương.

**Icon nâng cấp**: 5 medallion vẽ tay (`src/icons/art/tech_*.png`, 256², nền trong suốt tròn) thay icon phẳng CC0; orb có animation nhấp nhô + quầng sáng, icon đang chọn có thêm hiệu ứng loé.

## 10. Đợt 4 — tàu "sống", bắn/chém đúng chỗ, màn nâng cấp thành sơ đồ kỹ thuật

**Tàu trong trận (giờ là vật thể có cử động):**

- Ảnh tàu được **cắt thành 3 lớp lúc chạy**: thân + hai cánh (mặt nạ gradient, mép trong mờ nên mối nối luôn nằm dưới vỏ).
- Hai cánh **vỗ nhẹ** theo nhịp (biên độ tăng khi lướt nhanh), cộng thêm nghiêng theo hướng bay → không còn cảm giác "tấm ảnh dán".
- **Đèn định vị** đỏ/lá nhấp nháy ở hai đầu cánh, **quầng buồng lái** thở theo nhịp.
- Hai luồng lửa đúng ống xả, **bẻ hướng theo lái**; vệt tốc độ, loé súng, quầng khiên giữ nguyên từ đợt trước.

**Boss bắn từ súng, chém có cử động:**

- Mọi loạt đạn giờ xuất phát từ **họng súng máy** (toạ độ đã quay theo góc nghiêng thân), khớp với chớp lửa ở đầu nòng.
- Đang nạp đòn thì boss **nghiêng nòng về phía người chơi**.
- Đòn chém: kéo đao ra sau → **vung tới**, thân xoay theo, **cung lửa lưỡi liềm quét ~120°**, kèm **vệt mờ** của thân+đao (5–8 bản sao mờ mỗi nhịp) và rung màn hình.

**Màn Công nghệ = sơ đồ kỹ thuật của tàu:**

- Khung "buồng kỹ thuật": lưới, vạch quét chạy, bốn góc ngoặc, quầng sáng.
- Ảnh tàu đang dùng (đúng tàu đã chọn) ở giữa, **5 chấm nâng cấp** gắn đúng bộ phận: từ trường (mũi), khiên (vai phải), pháo (cánh trái), giáp (buồng lái), drone (mạn phải).
- Chấm đang chọn sáng vàng + vòng lan; mỗi chấm hiện **cấp hiện tại**; nâng cấp thành công thì chấm **nảy** hai nhịp.
- Bấm chấm trên sơ đồ = chọn nhánh đó (đồng bộ với hàng orb và danh sách bên dưới).
