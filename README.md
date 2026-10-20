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

> Lưu ý bản quyền: ảnh là tài sản của GCenter, chỉ dùng để minh họa gameplay.

---

## Game (vertical shmup build)

Bản build game bắn máy bay dọc theo spec boss fight nằm ở `game/` (web export,
Capacitor-ready cho APK — xem `docs/BUILD_ANDROID.md`). Chạy: `npm run serve`,
test headless: `npm test`. Ảnh trong repo này được dùng làm tham chiếu phong
cách (portrait shmup, boss tím/cam, đạn cyan vs đỏ/hồng).
