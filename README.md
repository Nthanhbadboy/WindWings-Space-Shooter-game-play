# WindWings: Space Shooter — Gameplay Image Collection

Bộ sưu tập ảnh gameplay của **WindWings: Space Shooter** (còn gọi là **WindWings: Galaxy Attack**, nhà phát hành **GCenter**, package `com.Wind.wings.Space.Shooter`), được thu thập từ nhiều nguồn và sắp xếp theo 6 danh mục để làm rõ gameplay.

## Cấu trúc thư mục

| Thư mục | Nội dung | Số ảnh |
|---|---|---|
| `Ship_Types/` | Các loại tàu vũ trụ playable, màn hình thu thập tàu | 3 |
| `Level_Screens/` | Ảnh chụp màn hình các màn chơi, HUD (điểm, thời gian, chapter), trận đấu | 33 |
| `Enemy_Types/` | Cảnh chiến đấu với kẻ thù ngoài hành tinh | 3 |
| `Upgrades_UI/` | Giao diện nâng cấp: Normal Cannon, Laser Weapon, Magnet, SuperPower, Health, Upgrade Technology | 2 |
| `Boss_Fighters/` | Boss ("EPIC BOSS FIGHT", boss cuối chapter 1) | 2 |
| `Backgrounds/` | Title screen, key art, logo banner, cảnh nền không gian | 12 |

**Tổng: 55 ảnh** (đã loại bỏ trùng lặp theo MD5 và loại bỏ ảnh không phải của game).

Tệp `image_manifest.csv` liệt kê đầy đủ: thư mục, tên file, nguồn (site + URL), tên file gốc, kích thước, định dạng, MD5, mức độ tin cậy và ghi chú (bao gồm cả text OCR nhận dạng được).

## Nguồn đã thu thập

- **vgtimes.com/games/windwings-space-shooter/screenshots/** — trang có 7 ảnh chụp màn hình chính thức. Ảnh gốc của trang này lưu tại `files.vgtimes.com`, không tải trực tiếp được trong sandbox này (chỉ cho phép kết nối ra github.com / pypi.org), nên 7 ảnh đó — vốn là các screenshot chính thức trên Google Play — đã được thu thập từ các mirror của cùng bộ screenshot Google Play bên dưới.
- **Google Play (chính thức)** qua các mirror: Appbrain (đầy đủ 9 screenshot + Pro), LiteAPKs, Softonic, Apkmody, Apk.dog, ApkPure, TapTap, PlayMods, Modyolo, TyHacks, 9MOD, happymod, CafeBazaar, LDPlayer, BlueStacks
- **Kotaku** gallery (ảnh gốc 1920x1080, credit: GCenter)
- **Reddit r/Windwingsgame** (ảnh boss cuối chapter 1)
- **sbenny.com** (feature collage)

## Phương pháp phân loại

1. Tìm ảnh theo từng danh mục gameplay bằng image search (Brave), lưu về workspace.
2. Chạy **OCR (RapidOCR)** trên từng ảnh để đọc text trong game ("COLLECT YOUR SPACESHIP", "TRANSFORM IN BATTLE", "EPIC BOSS FIGHT", "NORMAL CANNON / LASER WEAPON / MAGNET", "SHOOT 'EM UP!!!", ...).
3. Phân loại theo: text OCR + ngữ cảnh trang nguồn (thứ tự screenshot trên Google Play) + kích thước/orientation.
4. Loại bỏ trùng lặp (MD5) và loại bỏ kết quả sai (game khác: Galaga, Galaxy Attack 2020, Monster Shooter, Universe Invader 2, Burning Sky, Aircraft Wargame, Flyff, Dead Space 2, Space Marine 2, Final Fantasy; ảnh watermark "PREMIUM FOREVER"; icon app; ảnh WindWings 2: Galaxy Revolution/sequel).

**Mức độ tin cậy** (có trong manifest):
- `high` — xác nhận bằng text OCR nhận dạng được trong ảnh.
- `medium` — ngữ cảnh nguồn rõ ràng (ví dụ: screenshot thứ N/9 trên Google Play, Reddit về boss chapter 1) nhưng chưa OCR xác nhận.
- `low` — suy luận từ ngữ cảnh tìm kiếm, **cần xem lại bằng mắt** (đánh dấu "verify" trong cột notes).

## Thông tin game (tham khảo)

- Top-down sci-fi shooter cho mobile (Android 4.4+), ~111 MB, 10M+ lượt tải, rating 4.7–4.8★
- Cốt truyện fantasy về người lính trong chiến tranh tương lai, bảo vệ Trái Đất
- Nhiều loại tàu vũ trụ với thuộc tính riêng, đổi tàu tức thì bằng 1 tap
- 60+ màn chơi, nhiều boss; enemy có pattern tấn công khác nhau
- Hệ thống nâng cấp: laser, mega-bomb, magnet, SuperPower, Health, Upgrade Technology
- Trang bị hỗ trợ (support devices); chế độ PvP (vs), BATTLE / CHALLENGE / ENDLESS / SPEED, hệ CHAPTERS
- Điều khiển: chạm kéo để di chuyển, tàu bắn tự động; thu thập power-up

## Scripts

- `organize_images.py` — script đã dùng để phân loại/dedup/dọn dẹp (giữ lại để minh bạch provenance).

## Dự án mã nguồn mở tham khảo

WindWings không có mã nguồn công khai (game đóng của GCenter). Danh sách các repo cùng thể loại — shmup dọc hoàn chỉnh, bản mobile/Android, bản web và engine hỗ trợ — kèm đối chiếu tính năng và gợi ý lộ trình làm bản tương tự: xem [`SIMILAR_OPEN_SOURCE_PROJECTS.md`](SIMILAR_OPEN_SOURCE_PROJECTS.md).

Bộ **infographic phân tích 13 repo** (bảng so sánh, thư viện ảnh gameplay, xếp hạng điểm phù hợp, bản đồ module → repo): xem [`repo-analysis/`](repo-analysis/README.md).

![So sánh 13 repo](repo-analysis/01_tong_quan_13_repo.png)

## Bộ asset mẫu (CC0) cho bản 3D

Để dựng prototype **galaxy shooter 3D** đủ đẹp trước khi tự vẽ art, repo có sẵn bộ asset mẫu **CC0 1.0** (Kenney + Quaternius): 11 tàu hero 3D đã tối ưu, enemy bay, hành tinh, skybox, chuỗi frame nổ, UI sci-fi và bộ điều khiển cảm ứng.

- Hướng dẫn, bảng pack, ghi công: [`assets_samples/README.md`](assets_samples/README.md)
- 8 ảnh contact sheet để xem nhanh: [`assets_samples/previews/`](assets_samples/previews/)
- So sánh trực tiếp với WindWings: `assets_samples/previews/08_windwings_vs_cc0.png`

![Đối chiếu WindWings với asset CC0](assets_samples/previews/08_windwings_vs_cc0.png)

## Game mẫu 3D cho điện thoại (`prototype/`)

Game **galaxy shooter dọc 3D** dựng bằng three.js + Vite, đóng gói được thành app Android (Capacitor/PWA).
Dùng đúng bộ asset CC0 trong `assets_samples/`.

**Đã có:**
- **8 tàu** trong hangar (mua bằng vàng, nâng cấp tới cấp 15, mỗi tàu một nội tại riêng)
- **5 nhánh nâng cấp** toàn cục: pháo, giáp, khiên, drone, từ trường
- **Drone hộ vệ** bay theo quỹ đạo, tự bắn; nhặt thêm drone trong trận
- **3 chương × 6 màn** (18 màn) với 3 kiểu mục tiêu: dọn sạch, sinh tồn, boss
- **4 chế độ**: Chiến dịch, Vô tận, Săn boss, Thử thách ngày (modifier đổi mỗi ngày)
- **3 boss** với 2 pha, đổi nền trời/hành tinh theo chương
- **Cảnh chơi 3 lớp**: bầu trời gradient trong trẻo + tinh vân + **Trái Đất 3D** (mây, đèn thành phố, quầng khí quyển) → **bụi/mảnh vụn trôi thẳng xuống** (cảm giác tiến lên) → vùng giao chiến
- **Tàu trong trận là ảnh vẽ tay**, đổi theo tàu đang chọn; **11 loại địch “ruồi” nhỏ**, có con bắn có con không, bay vào từ **mép trên hoặc hai mép ngang**
- **3 kiểu đạn** cho người chơi; địch/boss bắn **đạn hình học** (kim cương, vuông, lục giác, sao, vòng, thập tự…)
- **Boss là robot vẽ tay** có đòn **chém** (cột cảnh báo rồi chém) và 5 kiểu đạn theo **nhịp**; **sống động**: lao vào sân, đổi vị trí, nghiêng theo đà, lấy đà trước mỗi đòn, **đạn bay ra từ họng súng**, **vung đao có cung lửa + vệt mờ**, vệ tinh quay quanh, tan rã thành 9 mảng nổ; nổ 5 lớp (sóng xung kích, tia lửa, mảnh vỡ, rung màn hình)
- **Tàu trong trận "sống"**: cánh tách lớp và **vỗ nhẹ**, đèn định vị nháy, buồng lái thở, hai luồng lửa đúng ống xả bẻ theo lái, loé súng đầu cánh, vệt tốc độ, quầng khiên
- **Xưởng máy bay 3D** (`prototype/ship.html`): mô hình tàu dựng bằng code, **hình chiếu trực giao nhìn thẳng từ trên xuống**, cánh vỗ nhẹ + cánh tà gập theo bản lề + râu cảm biến rung, **lửa phản lực phụt theo ga**, **đạn rời đúng đầu nòng**; có thanh trượt vỗ cánh / ga / nghiêng thân / góc nhìn / tốc độ
- **Nền trạm không gian**: 3 vành trạm khổng lồ + 4 dầm bo hai mép trôi theo parallax, tinh vân dày hơn
- **Icon nâng cấp vẽ tay** (5 medallion hoạt hình) có animation; **màn Công nghệ là sơ đồ kỹ thuật**: 5 chấm gắn đúng bộ phận tàu, bấm vào là nâng cấp
- Sao (1–3), vàng, kỷ lục, lưu tiến trình trong máy

```bash
cd prototype
npm install
npm run dev        # http://localhost:5173  (game)
npm run dev:ship   # http://localhost:5180  (xưởng máy bay 3D — xem hình chiếu từ trên)
```
Windows: bấm đúp `prototype\run-windows.bat`.

- Chi tiết cảnh chơi mới: [`docs/gameplay-redesign.md`](docs/gameplay-redesign.md)
- Chi tiết hệ thống, cân bằng và **cách build APK**: [`prototype/README.md`](prototype/README.md)
- Build APK tự động: tab **Actions → Build Android debug APK**

## Chế độ test & chơi trên Android

**Cờ test (tạm thời)** — sửa `prototype/src/devflags.js`:

| Cờ | Tác dụng |
| --- | --- |
| `TEST_UNLOCK_ALL = true` | Mở cả 3 chương × 6 màn, không cần đủ sao |
| `TEST_AUTO_FIRE = true` | Luôn tự động bắn, bỏ qua lựa chọn trong Cài đặt |
| `TEST_RICH = false` | (tuỳ chọn) tặng 50 000 vàng + 500 gem lúc khởi động |

Đang bật cờ nào thì màn **Tạm dừng** hiện một dòng nhắc màu vàng, và lúc vào game có toast
“CHẾ ĐỘ TEST”. **Trước khi phát hành: đổi cả ba về `false`** (hoặc xoá file + các chỗ import).
Bộ test tự tắt cờ qua `globalThis.__WW_TEST_OVERRIDE__` nên vẫn kiểm tra đúng logic khoá màn.

**Android:**

- **Chơi được ngay trên web**: mở link GitHub Pages bằng Chrome trên Android → menu ⋮ → *Thêm vào màn hình chính* (game là PWA: toàn màn hình, khoá dọc, có icon riêng).
- **Chưa có file APK.** Workflow `.github/workflows/android-apk.yml` (Capacitor → `gradlew assembleDebug`) mới chỉ nằm trên nhánh phát triển, chưa lên `main`, nên GitHub chưa đăng ký workflow và chưa từng chạy → chưa có bản cài `.apk` nào.
  Muốn có APK: đưa nhánh phát triển vào `main` (merge PR) → tab **Actions → Build Android debug APK → Run workflow**, hoặc push tag `v1.0.0`; bản `.apk` nằm trong mục *Artifacts* của lần chạy đó.

## Lưu ý bản quyền

- Ảnh gameplay trong repo này là tài sản của **GCenter**, chỉ dùng để minh họa gameplay.
- Ảnh trong `repo-analysis/screenshots/` thuộc bản quyền tác giả từng repo, dùng cho mục đích so sánh/đánh giá.
- Không dịch ngược APK của WindWings để lấy code/asset.
- Toàn bộ asset trong `assets_samples/` là **CC0 1.0** (Kenney, Quaternius) — dùng thương mại tự do; chi tiết ở [`assets_samples/00_LICENSES/`](assets_samples/00_LICENSES/).
- Ảnh WindWings trong `assets_samples/previews/08_windwings_vs_cc0.png` chỉ dùng để **đối chiếu phong cách**, không phải asset được phép tái sử dụng.

---

## Nhánh làm việc này (arena/287e43b4…) — tổng hợp toàn repo

Nhánh này gộp **tất cả** tư liệu + code của 5 nhánh và nâng cấp game:

- **Chiến dịch 60 màn**: 6 chương × 10 màn (boss ở màn 10 mỗi chương,
  xoay vòng Imperial → Pancake → Dreadnought), bản đồ node 10 điểm/chương,
  độ khó + phần thưởng scale theo màn (`prototype/src/content.js`).
- **Boss 3 giai đoạn**: 66% máu → NỔI GIẬN (đổi màu lõi/hào quang, bắn
  nhanh), 33% → CUỒNG NỘ (vệ tinh quay gấp 2.4, đạn dày hơn 70%, nạp đòn
  0.18s). Boss vốn đã có rig "sống": nhập trận lao từ xa, thở, nghiêng theo
  đà, giật lùi khi bắn, loé họng súng, quầng kiếm, 2 vệ tinh orbit, sạc đòn
  sáng lõi — xem `docs/nghien-cuu-sprite-dong.md`.
- **HUD đúng số đo WindWings** (`docs/windwings-refs/v2/DO_DAC_UI.md`):
  chân dung tàu ô vát 74×58, thanh máu nghiêng −12° 3 dải màu + số italic
  nghiêng ngược, 5 đốt năng lượng nghiêng −26°, cụm xu icon 44px + số 42px,
  nút pause 60×60 viền gradient, đếm địch còn lại + đầu lâu — port từ
  `prototype/uikit.css` (phòng thử UI 1:1) vào `src/style.css`, scale theo
  khung thiết kế 720×1496 bằng `--u`.
- **Game 2D shmup** (spec boss-fight cũ) vẫn giữ ở `game/` + 66 test headless
  trong `tools/` (`npm test` ở root), CI APK riêng:
  `.github/workflows/android-apk-2d-game.yml`.
- CI: `android-apk.yml` (tag `v*` → APK WindWings 3D từ `prototype/`),
  `prototype-pages.yml` (push nhánh này → GitHub Pages).

Test prototype: `cd prototype && npm test` (mô phỏng gameplay + UI jsdom +
nền nhiều lớp). Ảnh tham chiếu WindWings thật: `docs/windwings-refs/`
(13 ảnh cắt) và `docs/windwings-refs/v2/` (10 ảnh + 3 tài liệu đo đạc).
