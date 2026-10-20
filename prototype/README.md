# WindWings 3D — bản dựng game mobile

Galaxy shooter dọc 3D chạy trên trình duyệt và đóng gói được thành **app Android**.

**Chơi trực tiếp:** https://nthanhbadboy.github.io/WindWings-Space-Shooter-game-play/
(bản build tự động từ nhánh `arena/d2148f4d-windwings-space-shooter-game-p` mỗi khi `prototype/**` thay đổi)
**Art giao diện là bộ vẽ riêng** trong [`../docs/asset-samples/`](../docs/asset-samples/) (27 icon, 8 sprite tàu,
3 nền tinh vân) — quy tắc dựng ở [`../docs/windwings-ui-spec.md`](../docs/windwings-ui-spec.md).
Mô hình 3D & texture lấy từ bộ CC0 trong [`../assets_samples/`](../assets_samples/) (Kenney + Quaternius).

---

## Chạy

### Windows — nhanh nhất
Bấm đúp **`prototype\run-windows.bat`** (cần cài [Node.js LTS](https://nodejs.org/) trước).

### Mọi hệ điều hành
```bash
cd prototype
npm install
npm run dev          # http://localhost:5173
```
> PowerShell 5.1 không hiểu `&&` → gõ từng dòng như trên.

### Chơi trên điện thoại trong cùng wifi
```bash
npm run dev -- --host
```
Mở `http://<IP-máy-tính>:5173` trên điện thoại.

---

## Giao diện

Bố cục và bảng màu bám theo ảnh chụp **WindWings** — phân tích ở
[`../docs/windwings-style.md`](../docs/windwings-style.md), quy tắc asset ở
[`../docs/windwings-ui-spec.md`](../docs/windwings-ui-spec.md), 13 ảnh cắt tham chiếu trong
[`../docs/windwings-refs/`](../docs/windwings-refs/).

| Màn | Nội dung |
|---|---|
| Thanh trên | PREMIUM (đếm ngược quà ngày) · sao · xu · gem (icon vẽ tay) |
| Home | 2 khoang tàu S1/S2, pod **NÂNG CẤP** ở giữa, khoang L/R cho drone, **CHƠI** (cam), ĐẤU TRƯỜNG + PVP, 3 chip chế độ nhanh |
| Chiến dịch | bản đồ node uốn khúc, sao dưới mỗi node, node boss đầu lâu |
| Hangar | 8 tàu, bảng LVL/ATK/HP/TỐC ĐỘ, thanh cấp, 2 nút mua bằng xu / gem |
| Công nghệ | 5 nhánh, lục giác cấp, thanh tiến trình, tổng `x/60` |
| Cửa hàng | quà hằng ngày (chuỗi 7 ngày) + đổi gem → xu |
| Cài đặt | lưới 8 ô icon |
| Pause | mục tiêu có sao, chọn JOYSTICK/KÉO + TỰ BẮN/BẮN TAY, 3 thanh trượt |

Thanh trên và thanh điều hướng đáy (5 tab: HANGAR · CÔNG NGHỆ · CHIẾN DỊCH · CỬA HÀNG · CÀI ĐẶT)
giữ nguyên trên mọi màn ngoài trận, đúng kiểu WindWings.

### Bộ asset
```bash
python3 docs/tools/make_assets.py     # 27 icon 192px + 3 nền 900x1600 + bảng style
python3 docs/tools/ship_sprites.py    # 8 sprite tàu 512px
```
- Icon dùng trong game: `prototype/src/icons/ic_*.png`
- Sprite tàu: `prototype/src/thumbs/<tên>.png` (512px, nền trong suốt)
- Font: Barlow Condensed OFL, subset **latin + vietnamese**, trong `prototype/src/fonts/`
- Bảng duyệt tổng hợp: `docs/asset-styleboard.png`

---

## Hệ thống trong game

### 8 tàu (hangar)
| Tàu | Giá | Nội tại |
|---|---|---|
| STRIKER | 0 | +10% vàng nhận được |
| ZENITH | 1.200 | Khiên hồi nhanh gấp đôi |
| CHALLENGER | 2.000 | +1 khiên tối đa |
| SPITFIRE | 3.200 | Bắt đầu với vũ khí cấp 2 |
| INSURGENT | 4.500 | Hút vật phẩm xa hơn 60% |
| EXECUTIONER | 6.000 | Đạn xuyên 1 mục tiêu |
| OMEN | 8.000 | +1 drone hộ vệ |
| DISPATCHER | 10.000 | +2 drone hộ vệ |

Mỗi tàu lên được **cấp 1 → 15**: +5% máu, +5% sát thương, +2% tốc độ mỗi cấp.

### 5 nhánh nâng cấp (áp dụng cho mọi tàu)
| Nhánh | Tác dụng | Tối đa |
|---|---|---|
| PHÁO CHÍNH | +8% sát thương / cấp | 20 |
| GIÁP THÂN | +10% máu / cấp | 20 |
| KHIÊN NĂNG LƯỢNG | +1 khiên mỗi 3 cấp (tối đa 5) | 9 |
| DRONE HỘ VỆ | +1 drone mỗi 2 cấp (tối đa 3) | 6 |
| TỪ TRƯỜNG | +12% bán kính hút vật phẩm | 5 |

### Drone hộ vệ
Bay theo quỹ đạo quanh tàu, tự nhắm địch gần nhất, bắn đạn xanh.
Có từ nâng cấp, từ nội tại tàu, hoặc nhặt vật phẩm **DRONE** rơi trong trận (tạm thời cho lượt đó).

### 4 chế độ
| Chế độ | Cách chơi |
|---|---|
| **CHIẾN DỊCH** | 3 chương × 6 màn = 18 màn. Màn 6 mỗi chương là boss. Có sao (1–3) theo % máu còn lại, mở khoá màn kế tiếp |
| **VÔ TẬN** | Sinh tồn, đợt địch mạnh dần, boss mỗi 5 đợt (Imperial → Pancake → Dreadnought) |
| **SĂN BOSS** | Chuỗi boss liên tiếp, hồi 30% máu giữa các boss |
| **THỬ THÁCH NGÀY** | Mỗi ngày một modifier (giáp giấy, đạn nhanh, bầy đàn, thép dày, sương mù, xạ thủ), thưởng vàng ×2 |

### Mục tiêu màn
- **DỌN SẠCH** — hạ hết các đợt địch.
- **SINH TỒN** — sống sót hết đồng hồ đếm ngược.
- **BOSS** — hạ boss cuối chương (đổi nền trời, hành tinh theo chương).

### Trong trận
Tự động bắn (đổi được sang **bắn tay** trong Pause), nâng vũ khí 1→5 tia, khiên hấp thụ 1 đòn, combo ×5,
pickup (vũ khí / máu / khiên / vàng / drone), nổ nhiều frame, bloom, rung camera,
boss 2 pha (dưới 50% máu nổi giận, bắn nhanh hơn).

### Điều khiển
| | |
|---|---|
| Điện thoại | Mặc định **JOYSTICK**: chạm & kéo bất kỳ đâu, tàu chạy theo hướng cần. Chọn **KÉO** trong Pause để tàu dời đúng 1:1 theo ngón tay. Nút ⏸ / loa ở góc dưới phải. |
| Bàn phím | `WASD` / mũi tên, `P` hoặc `Esc` tạm dừng, `M` tắt tiếng, `Enter` chơi lại |

---

## Đóng gói Android

### Cách 1 — PWA (nhanh nhất, không cần build)
Mở game bằng Chrome trên Android → menu **⋮** → **Thêm vào màn hình chính**.
Game chạy toàn màn hình, có icon riêng, vào được khi mất mạng (khung + asset đã cache).
Trong game cũng có ô **CÀI APP** ở phần Cài đặt.

### Cách 2 — APK bằng GitHub Actions (không cần cài Android Studio)
1. Vào tab **Actions** → workflow **Build Android debug APK** → **Run workflow**.
2. Đợi ~5–8 phút, tải file `windwings3d-debug-apk` ở mục **Artifacts**.
3. Cài APK lên máy (bật “Cài từ nguồn không xác định”).

Workflow dùng Capacitor, tự tạo project Android, khoá **màn hình dọc**, đóng gói `prototype/dist`.

### Cách 3 — build tại máy
```bash
cd prototype
npm run build
npm i -D @capacitor/core @capacitor/cli @capacitor/android
npx cap add android
npx cap sync android
cd android && ./gradlew assembleDebug      # Windows: gradlew.bat assembleDebug
# APK: android/app/build/outputs/apk/debug/app-debug.apk
```
Yêu cầu: JDK 21 + Android SDK (Android Studio).

> `capacitor.config.json` đã có sẵn: appId `com.windwings3d.game`, webDir `dist`.

---

## Cấu trúc code

```
prototype/
├── index.html              HUD + 6 màn hình UI (home, hangar, nâng cấp, chương, kết quả, cài đặt)
├── ship.html               Xưởng máy bay: mô hình 3D + hình chiếu trực giao nhìn từ trên
├── shipdemo.html           Bản thử 2D: 2 tàu, cánh gồng + laser từ đầu nòng
├── uikit.html              Phòng thử UI: HUD + linh kiện, chồng ảnh chụp thật để soi lệch
├── capacitor.config.json   cấu hình đóng gói Android
├── src/
│   ├── main.js             renderer, camera, bloom, vòng lặp, điều phối màn hình
│   ├── shipmodel.js        mô hình tàu 3D dựng bằng code (thân, cánh, động cơ, súng) + diễn hoạt
│   ├── ship-preview.js     trang xưởng máy bay: camera trực giao, đạn đúng đầu nòng, thanh trượt
│   ├── ship-preview.css    giao diện xưởng máy bay
│   ├── shipdemo/core.js    cảnh + pha bắn + laser từ đầu nòng
│   ├── shipdemo/fx.js      sao, lửa 3 hình, tia laser, quầng sáng
│   ├── shipdemo/mat.js     vật liệu: tấm giáp, đường năng lượng, ống tròn, đinh tán
│   ├── shipdemo/ships/     fighter.js (khung chiến đấu cơ) · omen · biomech · vertebra
│   ├── shipdemo/parts.js   đường dẫn 3 mảnh tàu đã cắt
│   ├── ships.js            8 tàu: chỉ số gốc, giá, nội tại, hướng mũi
│   ├── save.js             Profile (localStorage): vàng, tàu, nâng cấp, sao, kỷ lục
│   ├── content.js          3 chương, 18 màn, 4 chế độ, modifier ngày
│   ├── game.js             gameplay: player, drone, địch, boss, va chạm, mục tiêu
│   ├── ui.js               hangar / nâng cấp / bản đồ chương / home
│   ├── hud.js              HUD trong trận + màn kết quả
│   ├── world.js            đèn, sao, hành tinh, tinh vân, đổi theme
│   ├── assets.js           tải & chuẩn hoá model, texture, PMREM
│   ├── input.js            bàn phím + kéo chạm trên mặt phẳng y=0
│   ├── audio.js            SFX tổng hợp WebAudio
│   └── thumbs/*.png        ảnh 8 tàu cho hangar (render từ GLB)
```

## Chỉnh cân bằng

| Muốn đổi | Sửa ở |
|---|---|
| Chỉ số 8 tàu | `src/ships.js` → `base`, `perk`, `price` |
| Cấp tàu / giá nâng cấp | `src/ships.js` (`shipLevelMultipliers`), `src/save.js` (`upgradeCost`, `shipLevelCost`) |
| Nội dung nâng cấp | `src/save.js` → `UPGRADES` |
| Chương, màn, mục tiêu | `src/content.js` → `CHAPTERS`, `levelInfo()` |
| Modifier hàng ngày | `src/content.js` → `DAILY_MODIFIERS` |
| Máu/tốc độ địch | `src/game.js` → `ENEMY` |
| Boss | `src/game.js` → `BOSSES` |
| Vàng nhận sau trận | `src/save.js` → `coinsForRun()` |
| Vùng chơi / camera | `src/main.js` → `applyFraming()` |
| Bloom | `src/main.js` (`UnrealBloomPass`) |

## Xưởng máy bay (mô hình 3D)

`ship.html` là trang xem trước **riêng cho máy bay**, không đụng tới gameplay:
mô hình 3D dựng hoàn toàn bằng code trong `src/shipmodel.js` (không cần file GLB),
nhìn bằng **camera trực giao đúng hình chiếu đứng từ trên xuống**.

```bash
cd prototype
npm run dev:ship     # http://localhost:5180  (mở thẳng trang xưởng)
npm run render:ship  # xuất 8 khung + ảnh tiếp xúc vào tools/ship_preview/ (không cần trình duyệt)
```

**Máy bay "sống" — những gì đang chạy:**
- **Cánh vỗ nhẹ**: mỗi bên cánh quay quanh gốc cánh (trục Z) kèm quét cánh (trục Y), đầu cánh nhấc lên hạ xuống thấy rõ ở góc nghiêng.
- **Cánh tà sau** gập theo một bản lề thật, nhịp chậm hơn nhịp vỗ.
- **Thân rung**: thân tàu lắc rất nhẹ, chúi theo lái (`bank`), phi công ngồi trong buồng lái.
- **Lửa đuôi phụt**: hai luồng phản lực dài/ngắn theo **ga**, nhấp nháy 43 Hz, có lõi sáng, quầng quanh miệng ống, tia lửa.
- **Nòng súng giật** khi bắn, có chớp đầu nòng; **đạn sinh ra đúng vị trí đầu nòng** lấy từ `getMuzzles()` (đã kiểm chứng bằng toạ độ thực, không phải vẽ ước lượng).
- **Chi tiết rung**: râu cảm biến ở mũi, ăng-ten đuôi, đèn định vị nháy, buồng lái "thở".
- Thanh trượt: **Vỗ cánh · Ga · Nghiêng thân · Góc nhìn (0–55°) · Tốc độ**; nút bật/tắt khai hỏa, đánh dấu đầu nòng, chú thích, tạm dừng.

## Thử tàu 2D (shipdemo.html)

Bản thử **độc lập**, không đụng gameplay: chỉ để xem hai con tàu có "sống" không.

```bash
cd prototype
npm run dev:ship2d     # http://localhost:5190  (mở thẳng trang thử)
```

Trang có 3 tàu, đổi bằng ba nút trên cùng:

| | Tàu 1 — CÁNH DƠI (`omen`) | Tàu 2 — SINH CƠ (`biomech`) | Tàu 3 — XƯƠNG SỐNG (`vertebra`) |
|---|---|---|---|
| Hình | 3 mảnh PNG cắt từ `omen.png` (hoặc vector nếu thiếu ảnh) | vector | vector |
| Cánh | xoay quanh gốc cánh, gồng thì **2 đầu nhọn chụm về mũi** | cánh liền khối, hạ xuống khi giáp mở | cánh lái ngắn, hạ xuống khi gồng |
| Súng | **quả cầu năng lượng** trước mũi: 2 đầu cánh + mũi chụm vào | **nòng giấu dưới cánh**, chỉ thò đầu ra trước mép cánh + 2 càng kẹp | **nòng chạy trong cột sống**, thò ra ở mũi |
| Sinh cơ | **rãnh sống mũi**: 2 dải giáp hẹp trượt ra, lộ rãnh sáng lên thấu kính | **2 tấm giáp lưng trượt + xoay mở 3 nấc**, lộ lõi | **6 đốt sống tách ra**, **4 cặp sườn nhấc lên**, lộ cột năng lượng |
| Laser | **1 tia** phóng từ **tâm quả cầu** | **2 tia** phóng từ **đầu nòng dưới cánh** | **1 tia** phóng từ **đầu nòng ở mũi** |
| Lửa đuôi | 3 hình, tím | 3 hình, ngọc lam | 3 hình, hổ phách |

**Nguyên tắc: hoàn toàn 2D.** Mọi cử động chỉ là trượt/xoay/co giãn **trong mặt phẳng** —
không có mesh 3D nào. Ảo giác khối đến từ màu: lớp tối khi gồng, viền tối + viền sáng
một bên, quầng sáng quanh ống xả và đầu nòng, bóng mờ dưới thân.

**Laser luôn có nguồn.** Mỗi tàu tự khai báo `muzzles()` — toạ độ điểm phát sau khi đã tính
đủ chuyển động (tâm quả cầu của omen, đầu nòng dưới cánh của biomech). Cảnh chỉ việc vẽ tia
từ đúng điểm đó, nên không còn tia nào "mọc ra từ hư không" ở mép ảnh.

### Khung chiến đấu cơ chuẩn + bộ vật liệu (D15/D16)

Ba tàu **không còn mỗi tàu một khung riêng**. `ships/fighter.js` giữ một khung chung đúng
silhouette chiến đấu cơ — mũi nhọn `y38`, buồng lái `y100…212`, gốc cánh `y196…226`,
sải cánh tới `x470/42`, vây đuôi `y392…460`, 2 ống xả `y441` — và cung cấp
`drawFuselage / drawCanopy / drawWing / drawCanard / drawTail / drawEngines / drawPylon`.
Tàu nào cũng dựng trên khung đó rồi mới thêm cái riêng (cầu năng lượng, giáp sinh cơ, đốt sống).
Luật: **mỗi `draw()` chỉ bước vào hệ thiết kế 512 MỘT lần**, sau đó mọi hàm con dùng số 512
— trộn `*s` vào là tàu vỡ hình.

`ships/mat.js` lo bề mặt: `STEEL / BRONZE / CERAMIC`, `techPlate()` (nền tối → gradient chéo →
viền ngoài gần đen → bóng trong → rim sáng mảnh → đường ghép + đinh tán), `tube`, `band`,
`vents`, `glowLine`. Công thức màu "ra chất công nghệ" là **nền ít bão hoà + đúng MỘT màu phát
xạ + đúng MỘT ánh bù** đối diện nguồn sáng; cấm màu tinh khiết cho mảng lớn.


Cụm pháo gắn trên mặt cánh đọc rất "dán thêm" và che mất hình cánh dơi. Cách làm lại vẫn
giữ nguyên tinh thần "mọi thứ phải có chỗ phát ra":

- **Omen — quả cầu năng lượng trước mũi.** Khi gồng, hai cánh khép lên (góc +0,45 rad) nên
  **hai đầu nhọn của cánh chụm sát sống mũi**; thân mở **rãnh sống mũi** (hai dải giáp hẹp
  trượt ra, các đốt co lại) để năng lượng chạy lên thấu kính ở mũi. Hai đầu cánh + mũi tạo
  thành một **quả cầu** ngay trước mũi; khai hỏa thì cả quả cầu phóng **một tia** duy nhất.
  Quả cầu vẽ 4 lớp (quầng cộng sáng → khối cầu gradient lệch sáng → viền + phản quang → vành
  xoay + tia lửa) nên **2D phẳng mà vẫn đọc ra khối**; tâm cầu chính là `muzzles()`.
- **Biomech — nòng thò ra từ DƯỚI cánh.** Nòng là ống lồng trượt: vẽ **trước** cánh nên phần
  giữa bị cánh che, chỉ thấy **đầu nòng thò ra trước mép trước cánh** và đuôi nòng sau mép sau.
  Gồng → nòng trượt ra thêm (+34); bắn → giật lùi (−55, lùi sâu hơn cả lúc nghỉ) rồi về.
  Nhìn từ trên xuống không có khối nào "mọc" trên mặt cánh, đúng ý "súng nằm dưới cánh".

| Bộ phận | Cử động |
|---|---|
| Cánh | xoay quanh gốc cánh; có **xi-lanh** nối thân–cánh dài ra ngắn lại theo góc cánh, **bản lề** có bu-lông che mối nối |
| Đuôi phản lực | **đúng 3 hình lửa**, 15 hình/giây, hai ống lệch pha; có quầng, có đốm lửa rơi |
| Thân | nhún lên xuống + nghiêng rất nhẹ; lúc bắn thì giật lùi |
| Quả cầu (omen) | to dần theo độ gồng, vành nghiêng xoay, xẹp lại khi tia bắn ra |
| Nòng dưới cánh (biomech) | trượt ra/vào, có khoá đầu nòng + khe xả, miệng nòng sáng dần khi gồng |
| Chớp nòng | **chớp 3 hình** to→vừa→tắt khi khai hỏa |
| Lửa / đạn | không hạt (particle), không shader — chỉ ảnh + hình vector |

Nút trên trang: **TỰ BẮN** · **BẮN LASER** · **XƯƠNG** (hiện gốc xoay, ống xả, tâm quả cầu/đầu nòng)
· **CHẬM** (0,28×) · **DỪNG** · **ẢNH/VẼ** (chỉ tàu 1) · thanh **TỐC ĐỘ**.

**Không bao giờ mất hình.** Vòng vẽ chạy **ngay** (không chờ ảnh); tàu 1 có bản vector
nên ảnh lỗi vẫn hiện tàu, kèm hộp lỗi đỏ. Góc trái dưới có dòng
`CÁNH DƠI · ẢNH 6/6 · 480×600` để biết trang đang vẽ kiểu gì.

```bash
npm run render:ship2d                          # vẽ 52 khung × 3 tàu (+ khung xương) vào /tmp, in lệnh ghép
python3 tools/ship2d_gif.py /tmp/ship2d-xxxx tau-omen-2d
python3 tools/ship2d_gif.py /tmp/ship2d-yyyy tau-sinhco-2d
python3 tools/ship2d_gif.py /tmp/ship2d-zzzz tau-xuong-2d
```

Ảnh xem trước có sẵn:
[`tau-omen-2d.gif`](../docs/previews/tau-omen-2d.gif) ·
[`tau-sinhco-2d.gif`](../docs/previews/tau-sinhco-2d.gif) ·
[`tau-xuong-2d.gif`](../docs/previews/tau-xuong-2d.gif) ·
bảng khung `*-khung.jpg`.

**Sổ tay thiết kế** (đọc trước khi làm tàu mới — hợp đồng module, 4 kiểu súng, ngữ pháp
chuyển động, công thức "2D tưởng 3D", cách áp sinh cơ, mẫu thẻ mô tả tàu cho AI, checklist QA):
[`../docs/thiet-ke-may-bay.md`](../docs/thiet-ke-may-bay.md).

Ghi chú nghiên cứu bộ sprite động tham khảo (cấu trúc 15 khung = 5 tư thế × 3 khung lửa,
bài học về tách lớp/nhịp): [`../docs/nghien-cuu-sprite-dong.md`](../docs/nghien-cuu-sprite-dong.md).

## Giới hạn hiện tại
- Địch gồm 4 sinh vật bay (có animation) + 3 phi thuyền Kenney + thiên thạch — chưa phải art riêng kiểu WindWings.
- Boss dùng lại model tàu (Imperial / Pancake), chưa có model boss riêng nhiều giai đoạn.
- Chưa có PvP, liên minh, sự kiện, cửa hàng theo mùa.
- Âm thanh là synth tạm; chưa có nhạc nền.
- Chưa có đồng bộ đám mây (tiến trình lưu trong máy).

## Bước tiếp theo đề xuất
1. Thay 3 phi thuyền địch bằng model riêng + thêm boss 3 giai đoạn có điểm yếu phát sáng.
2. Thêm nhạc nền + SFX thật (Kenney Audio, CC0).
3. Thêm shop giữa các màn, hòm vật phẩm, trang bị phụ (module tên lửa, khiên phản đòn).
4. Đồng bộ tiến trình (Firebase/Supabase) + bảng xếp hạng tuần.
5. Phát hành APK ký (release keystore) lên Google Play.

## Phòng thử UI (`uikit.html`)

Mở `prototype/uikit.html` (hoặc `/uikit.html` trên bản Pages). Trang dựng lại **HUD trong trận**
và một bộ linh kiện (nút CHƠI, hàng công nghệ, node bản đồ, ô tàu) theo đúng số đo trên ảnh chụp
thật 720×1496:

- **Thanh trượt "Ảnh gốc"** chồng ảnh `gp1.png` lên bài dựng (0–100 %), **NHÁY** để bật/tắt liên tục
  → soi lệch biên bằng mắt.
- **Lưới 40** bật lưới 40 px trong khung thiết kế để đọc toạ độ.
- Khung thiết kế luôn là **720×1496** rồi scale vừa cửa sổ, nên mọi số trong `src/uikit.css`
  là px trong khung đó.

Số đo, mã màu, công thức từng linh kiện: [`../docs/windwings-refs/v2/DO_DAC_UI.md`](../docs/windwings-refs/v2/DO_DAC_UI.md)
(ảnh tham chiếu cùng thư mục). Duyệt hình xong thì tê khối HUD sang `src/style.css` + `index.html`,
giữ nguyên id để `hud.js` không phải sửa.

## Chiều sâu nền — 10 lớp

Nền màn chơi chia **10 lớp**, tất cả theo một luật cuộn `tốc độ thế giới = SCROLL / độ sâu`
(`backdrop.js`, `SCROLL = 610`), cộng thêm **lớp gần vẽ đè lên tàu** và **camera trôi theo tàu**
(`focus` truyền từ `main.js`). Số liệu từng lớp, ảnh tham chiếu và 3 bước kiểm tra bằng mắt:
[`../docs/nen-nhieu-lop.md`](../docs/nen-nhieu-lop.md) ·
[`../docs/previews/lop-khong-gian.png`](../docs/previews/lop-khong-gian.png).
