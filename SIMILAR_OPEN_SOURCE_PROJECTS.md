# Các dự án mã nguồn mở tương tự *WindWings: Space Shooter*

> Khảo sát ngày **2026-10-20** bằng GitHub Search API (`gh search repos`, topic `space-shooter`, `shoot-em-up`, `shmup`), GitHub REST API (số star / license / lần push cuối) và tìm kiếm web.
> Số star chỉ là tương đối, thay đổi theo thời gian.

## Kết luận nhanh

**Không tồn tại mã nguồn công khai của *WindWings: Space Shooter*.** Đây là game thương mại đóng của **GCenter** (package `com.Wind.wings.Space.Shooter`), không có repo chính thức, không có bản open-source.

Tìm `windwings` trên GitHub chỉ trả về:

| Kết quả | Liên quan? |
|---|---|
| `Nthanhbadboy/WindWings-Space-Shooter-game-play` | Chính repo ảnh gameplay này |
| `Gocciaplay/trucchi-per-wind-wings-space-shooter` | Trang cheat tiếng Ý, không có code game |
| `Windwings0711/*`, `GreateLi/windws_zlib`, … | Trùng tên "windws/windwings", không liên quan |

Vì vậy phần còn lại là các dự án **cùng thể loại** (vertical shoot 'em up / space shooter) có thể dùng để học hoặc làm nền cho một bản tương tự.

---

## 1. Nhóm gần nhất về chiều sâu gameplay

Những dự án này có đủ bộ: nhiều màn, nâng cấp vũ khí, nhiều loại tàu, boss, tiến trình chơi — tức là "khung xương" gần với WindWings nhất.

| Repo | Stack | License | ★ | Vì sao đáng xem |
|---|---|---|---|---|
| [opentyrian/opentyrian](https://github.com/opentyrian/opentyrian) | C + SDL2 | GPL-2.0 | 591 | Bản port mã nguồn mở của **Tyrian** — shmup dọc kinh điển: story mode, arcade 1–2 người, netplay, **shop mua/nâng cấp tàu & vũ khí giữa màn**, rất nhiều weapon và boss. Sát mô hình "campaign + nâng cấp" nhất. Kèm sẵn data freeware Tyrian 2.1. |
| [taisei-project/taisei](https://github.com/taisei-project/taisei) | C11 + SDL3 + OpenGL | MIT-style | 1.656 | Bullet hell hoàn chỉnh: nhiều nhân vật, **boss nhiều phase với spell card**, replay, practice mode, chạy cả WebGL. Tài liệu tham khảo tốt nhất cho pattern đạn và thiết kế boss. |
| [brunonymous/Powermanga](https://github.com/brunonymous/Powermanga) | C/C++ + SDL | GPL-3.0 | 29 | 41 màn, 200+ sprite, ~60 loại enemy, 40 thiên thạch, power-up vũ khí, boss cuối màn. Rất giống cấu trúc "chapter → màn → boss" của WindWings. |
| [thetawavegame/thetawave](https://github.com/thetawavegame/thetawave) | Rust + Bevy | MIT | 183 | Space shooter vật lý, level sinh ngẫu nhiên, nhiều nhân vật, co-op, power-up, thanh "defense bar" bảo vệ hành tinh. Code hiện đại, dễ đọc. |
| [crystal-bit/space-shooter](https://github.com/crystal-bit/space-shooter) | Godot 3 (GDScript) | GPL-3.0 (code) | 42 | Project Godot hoàn chỉnh do cộng đồng làm trong Hacktoberfest, có art + nhạc + particle. Lưu ý: asset có giấy phép riêng. |
| [godotrecipes/classic_shmup](https://github.com/godotrecipes/classic_shmup) | Godot 4 (GDScript) | MIT | 32 | Project tutorial shmup cổ điển, gọn và dễ đọc — điểm khởi đầu tốt nếu muốn dựng prototype nhanh. |
| [NagaChiang/ThroughGalaxies](https://github.com/NagaChiang/ThroughGalaxies) | C# (Unity) | GPL-3.0 | 23 | Shmup khó, có **chuyển/nâng cấp vũ khí** và boss dày. |

---

## 2. Nhóm mobile / Android (sát trải nghiệm WindWings)

WindWings là game mobile điều khiển cảm ứng, tàu tự bắn. Nhóm này khớp nhất về **control scheme + vòng lặp chơi**.

| Repo | Stack | License | ★ | Điểm khớp với WindWings |
|---|---|---|---|---|
| [KaeruCT/RaumBaller](https://github.com/KaeruCT/RaumBaller) | Java (JGame-derived), Android | GPL-3.0 | 23 | **Rất sát**: chạm để di chuyển, **tàu tự bắn**, 3 tàu để chọn, pháo **tự nâng cấp theo điểm**. Có trên F-Droid và bản browser (TeaVM). |
| [acourreges/exp3d](https://github.com/acourreges/exp3d) | Java thuần, OpenGL ES, Android + desktop + WebGL | GPL (code), asset proprietary | 88 | Game Android thương mại 2013 được mở source: kiến trúc engine tự viết, **object pooling, 60 FPS không GC pause** — rất đáng học cho mobile. |
| [emre-cil/interstellar-enemies](https://github.com/emre-cil/interstellar-enemies) | Java + libGDX, Android | MIT | 6 | Project mobile hoàn chỉnh, nhỏ, dễ đọc; có GIF gameplay trong README. |
| [lazybigcat0624/atomic-laser-attack](https://github.com/lazybigcat0624/atomic-laser-attack) | Java + libGDX, Android | Chưa rõ | 0 | **Touch + auto-fire + hệ thống nâng cấp + 3 màn**, từng phát hành trên Google Play. Ít star nhưng đúng mô tả gameplay. |
| [hynra/Space-Sonic](https://github.com/hynra/Space-Sonic) | C# (Unity), mobile | Chưa rõ | 17 | Space shooter 2D cho mobile làm bằng Unity. |
| [DevaDeveloper/Galaxy-Shooter-Android-Game](https://github.com/DevaDeveloper/Galaxy-Shooter-Android-Game) | C# (Unity), Android | Chưa rõ | 1 | Bản Galaxy Shooter đóng gói cho Android. |
| [GeetMark/Galaxy-Shooter-Android-Game](https://github.com/GeetMark/Galaxy-Shooter-Android-Game) | Kotlin + Canvas API | Chưa rõ | 0 | Nếu muốn làm **không cần game engine**, đây là ví dụ Android thuần. |
| [ufrshubham/spacescape](https://github.com/ufrshubham/spacescape) | Dart + Flutter + **Flame 1.30** | MIT | 135 | Space shooter top-down đa nền tảng, một codebase chạy Android/iOS/web — hướng đi nhanh nếu muốn mobile + web. |
| [Dreaming381/lsss-wip](https://github.com/Dreaming381/lsss-wip) | C# + Unity DOTS/ECS | MIT | 244 | Sample Unity DOTS của Latios: hàng nghìn entity, tối ưu cho mobile. Tham khảo khi cần hiệu năng cao. |
| [UnityTechnologies/SpaceShooterECS](https://github.com/UnityTechnologies/SpaceShooterECS) | C# + Unity ECS | Unity Companion License | 153 | Sample chính thức của Unity (GDC 2018) — kiến trúc ECS cho shooter. |
| [Yecats/SuperSpaceShooter](https://github.com/Yecats/SuperSpaceShooter) | C# (Unity) | MIT | 39 | Demo Unity đơn giản: audio, animation, AI, UI — tốt để học phần "cảm giác game". |

---

## 3. Nhóm web / HTML5 (chạy thử nhanh, không cần build mobile)

| Repo | Stack | License | ★ | Ghi chú |
|---|---|---|---|---|
| [tsherif/space-shooter.c](https://github.com/tsherif/space-shooter.c) | C11 + OpenGL/WebGL (Emscripten) | MIT | 1.378 | Cực gọn, chạy Windows/Linux/Web, có tài liệu kiến trúc. Kinh điển để đọc code shooter "từ số 0". |
| [code0wl/Multiplayer-Phaser-game](https://github.com/code0wl/Multiplayer-Phaser-game) | TypeScript + Phaser + Socket.io | MIT | 130 | Space shooter **multiplayer realtime** — tham khảo nếu muốn làm chế độ PvP/versus như WindWings. |
| [flo-bit/shadow-shmup](https://github.com/flo-bit/shadow-shmup) | TypeScript + **PixiJS 8 + Rapier2D** + Vite | Chưa rõ | 10 | Shmup top-down roguelike, hiệu ứng neon, vật lý thật. |
| [jaredyork/CoursePhaser3SpaceShooter](https://github.com/jaredyork/CoursePhaser3SpaceShooter) | JavaScript + Phaser 3 | Chưa rõ | 24 | Code cuối khóa "Build a Space Shooter with Phaser 3". |
| [bettercallazamat/js-retro-shooter](https://github.com/bettercallazamat/js-retro-shooter) | JavaScript + Webpack | GPL-3.0 | 10 | Shooter cuộn dọc lấy cảm hứng Astro Warriors. |
| [brandonto/sdl-space-shooter](https://github.com/brandonto/sdl-space-shooter) | C++ + SDL2 | MIT | 25 | Shooter 2D gọn, có level/enemy cấu hình bằng XML. |
| [Amegma/Galaxy-Attack](https://github.com/Amegma/Galaxy-Attack) | Python + Pygame | MIT | 44 | "Galaxy Attack" kiểu Space Invaders — cùng tên gọi, khác gameplay. |
| [KaeruCT/pixelshooter](https://github.com/KaeruCT/pixelshooter) | Java | GPL-2.0 | 2 | Tiền thân của RaumBaller, cùng tác giả. |

---

## 4. Công cụ / engine hỗ trợ làm shmup

| Repo | Dùng để |
|---|---|
| [Dark-Peace/BulletUpHell](https://github.com/Dark-Peace/BulletUpHell) (GDScript, MIT, ★369) | Plugin Godot 3/4 tạo **pattern đạn** phức tạp bằng resource, không cần code nhiều: pattern, homing, laser, animation, âm thanh. |
| [quinnvoker/qurobullet](https://github.com/quinnvoker/qurobullet) (C++, MIT, ★182, đã archive) | Module projectile/pattern đạn cho Godot; vẫn tham khảo tốt dù không còn cập nhật. |
| [kenney.nl – Space Shooter Redux](https://kenney.nl/assets/space-shooter-redux) | Bộ art CC0 (tàu, đạn, enemy, UI) được dùng trong rất nhiều repo kể trên; thay thế hợp pháp cho asset của WindWings. |
| [michelpereira/awesome-open-source-games](https://github.com/michelpereira/awesome-open-source-games) | Danh sách tổng hợp game open-source, mục Arcade/Shooter. |

---

## 5. Đối chiếu tính năng WindWings → repo nên đọc

| Tính năng trong WindWings | Repo tham khảo |
|---|---|
| Chạm–kéo di chuyển, tàu tự bắn | `RaumBaller`, `atomic-laser-attack` |
| Nhiều tàu, đổi tàu bằng 1 tap | `RaumBaller` (3 tàu), `opentyrian` (chọn tàu arcade) |
| Nâng cấp: Normal Cannon, Laser, Magnet, SuperPower, Health, Technology | `opentyrian` (shop giữa màn), `Powermanga` (power-up) |
| Enemy wave / đội hình / pattern bắn | `taisei`, `BulletUpHell`, `Powermanga` |
| Boss cuối chapter, nhiều phase | `taisei`, `Powermanga`, `ThroughGalaxies` |
| Nhiều chapter + HUD điểm/thời gian | `exp3d`, `spacescape`, `thetawave` |
| Chế độ PvP "vs" | `code0wl/Multiplayer-Phaser-game` (realtime), hoặc tự làm async/ghost |
| Lưu tiến trình, mở khóa | `exp3d`, `opentyrian` (save game) |
| Tối ưu mobile 60 FPS | `exp3d` (object pooling), `lsss-wip` (DOTS/ECS) |

---

## 6. Nếu muốn tự làm một bản "WindWings-like"

1. **Chọn engine**
   - Mobile 2D nhanh: **Godot 4** (`godotrecipes/classic_shmup` + `BulletUpHell`) hoặc **Flutter/Flame** (`spacescape`).
   - Unity: `lsss-wip` / `SpaceShooterECS` nếu cần ECS, `SuperSpaceShooter` nếu cần mẫu cơ bản.
   - Web: **Phaser 3** (`code0wl`, `jaredyork`) hoặc **PixiJS + Rapier** (`shadow-shmup`).
2. **Dựng core loop trước**: player → đạn → enemy spawn → va chạm → điểm → game over. Chưa cần art đẹp.
3. **Thêm điều khiển cảm ứng**: kéo trực tiếp (offset để ngón tay không che tàu) + auto-fire; tham khảo `RaumBaller`.
4. **Thêm nâng cấp**: bảng chỉ số vũ khí/tàu, shop giữa màn (mô hình `opentyrian`).
5. **Thêm pattern & boss**: dùng `BulletUpHell` để định nghĩa pattern; boss theo phase giống `taisei`.
6. **Meta progression**: lưu JSON/SQLite (level, vàng, tàu mở khóa, upgrade level).
7. **Polish**: screen shake, hit-stop, particle, flash trắng khi trúng đạn, pooling đạn.

---

## 7. Lưu ý bản quyền

- WindWings và toàn bộ art/âm thanh thuộc **GCenter**. Repo này chỉ lưu ảnh để mô tả gameplay.
- **Không** dịch ngược APK để lấy code/asset rồi phát hành lại — vi phạm bản quyền và điều khoản Google Play.
- Học **cơ chế gameplay** (ý tưởng không được bảo hộ bản quyền) là hợp pháp; nhưng phải tự làm hoặc dùng asset có giấy phép rõ ràng (CC0/MIT/GPL phù hợp).
- Khi tái sử dụng code: giữ đúng license. GPL-3.0/GPL-2.0 → dự án phái sinh cũng phải GPL. MIT → chỉ cần giữ copyright notice. "Chưa rõ license" → không nên dùng cho sản phẩm phát hành.

---

## Phụ lục: lệnh tìm kiếm đã dùng

```bash
gh search repos "space shooter" --sort stars
gh search repos --topic space-shooter --sort stars
gh search repos --topic shoot-em-up --sort stars
gh search repos --topic shmup --sort stars
gh search repos "windwings"
gh search repos "space shooter" --language GDScript --sort stars
gh search repos "space shooter" --language Java --sort stars
gh api repos/<owner>/<repo> --jq '[.full_name,.stargazers_count,.language,.license.spdx_id,.pushed_at]'
```

Gợi ý mở rộng: thêm `--topic android-game`, `--topic libgdx`, `--topic phaser3`, hoặc tìm theo từ khóa `vertical shmup`, `bullet hell godot`, `shoot em up unity`.
