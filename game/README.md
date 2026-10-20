# WindWings-style Vertical Shmup — Boss Fight Game (60 màn)

Game bắn máy bay dọc (vertical scrolling shoot 'em up) chạy web/mobile,
phong cách WindWings: Space Shooter (tham chiếu ảnh trong repo gốc +
branch `windwings-ui-ux-analysis`: BAO_CAO_UI_UX, Ramus captures, prototype).
Toàn bộ sprite vẽ bằng code (canvas 2D), không asset mạng, không dependency.

## Chiến dịch 60 màn

- **6 chương × 10 màn**; màn 10/20/30/40/50/60 là **BOSS**.
- Script wave sinh tất định theo seed của từng màn (deterministic, không random runtime).
- Độ khó tăng dần theo màn: HP/tốc độ/tốc độ đạn enemy scale có trần.
- **3 loại boss**, mỗi con có rig + animation riêng (không phải ảnh tĩnh):
  - `VOID TYRANT` / `TYRANT PRIME` (chương 1, 4): sứa — tentacle uốn sóng, thở, chớp mắt, cuộn râu khi charge, giật lùi khi bắn.
  - `CRIMSON DISPATCHER` / `WAR DISPATCHER` (chương 2, 5): chiến hạm — 2 đĩa lưỡi cưa quay (nhanh dần theo phase), pod mở khi charge, cánh xòe phase 2, lõi rực phase 3.
  - `OMEN WEAVER` / `OMEN OVERLORD` (chương 3, 6): nhện — 6 chân khớp 2 đoạn đu đưa, vòng halo ngược chiều (thêm vòng mỗi phase), đồng tử co lại khi charge.
- Cả 3 boss giữ FSM 3 phase (66%/33%) + enrage <10% + HARD RULE telegraph;
  phase đổi màu rig, phase 3 lộ lõi + vết nứt; transition = anim 'break'; bắn = recoil kick.
- **Title screen** nút CHƠI vàng kiểu Ramus → vào màn đã mở khóa cao nhất;
  **Level select** 6 trang chương: khóa/mở, sao 1–3 (theo số mạng còn lại), tiến trình lưu `localStorage`.
- Banner đầu màn: tên chương + số màn / tên BOSS.

## Chạy game (web export)

```bash
npm run serve          # python3 -m http.server 8000 --bind 0.0.0.0 --directory game
# mở http://localhost:8000 (hoặc host preview của sandbox)
```

## Test headless (không cần browser)

```bash
npm test               # node tools/headless_test.mjs — 66 test, cả soak 5 phút
```

## Điều khiển

| Input | Hành động |
|---|---|
| Kéo bất kỳ đâu trên màn hình | Di chuyển tàu + auto-fire khi giữ |
| Nút BOMB (phải dưới) / phím B | Bomb: clear đạn + 500 damage |
| Nút pause (trái trên) / P, Esc | Pause menu |
| WASD / mũi tên + Space (desktop) | Di chuyển + bắn |

## Cấu trúc code (mỗi file < 400 dòng)

```
game/
  index.html, css/style.css
  js/
    config.js        MOI constant (balance, wave timeline, boss patterns)
    config_campaign.js  constant 60 màn + screens (merge vào CONFIG)
    levels.js        generator 60 màn tất định (seed theo số màn)
    progress.js      unlock + sao, lưu localStorage
    utils.js         Timer (delta-time), weightedPick, math
    bg.js            starfield 3 lớp
    input.js         drag-anywhere + multi-touch + keyboard
    player.js        follow, auto-fire, weapon level 1-5, lives, hitbox nhỏ
    projectiles.js   Bullet (+homing missile, trail)
    enemies.js       5 loại: chaser/shooter/turret/formation/elite
    waves.js         timeline spawn cố định wave 1-5 -> boss
    powerups.js      drop 5%/1%, magnet 100px, collect
    boss.js          state machine: warning/enter/idle/attack/recover/transition/dead
    boss_attacks.js  8 pattern (aimed, fan, spiral, ring, laserSweep, homing, hellRing, laserCross)
    boss_rigs.js     3 rig boss animated (tyrant/dispatcher/omen) + anim theo phase
    telegraph.js     visual telegraph tự remove (HARD RULE: không damage trước khi hết telegraph)
    combat.js        collision, bomb, boss death sequence
    particles.js     particle + coin burst
    fx.js            popup, hurt feedback
    score.js         score + combo multiplier
    hud.js           HUD + level tag + banner màn + menu pause
    screens.js       title / level select / clear (sao) / defeat
    audio.js         placeholder silence (// TODO: add sound)
    game.js          loop delta-time, slow-mo, shake, flash, pause
tools/               headless test harness (stub canvas/DOM)
```

## Build APK/AAB

- **GitHub Actions**: `.github/workflows/android-apk.yml` — push tag `v*`
  (hoặc chạy tay ở tab Actions) → runner Ubuntu (node 22 + temurin 21)
  wrap `game/` bằng Capacitor, khóa portrait, `gradlew assembleDebug`,
  trả artifact `windwings-boss-fight-apk`.
- **Máy dev có Android SDK**: xem `docs/BUILD_ANDROID.md`
  (Capacitor wrap thư mục `game/` → gradle → APK/AAB).
