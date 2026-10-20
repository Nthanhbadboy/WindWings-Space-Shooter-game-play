# WindWings-style Vertical Shmup — Boss Fight Game

Game bắn máy bay dọc (vertical scrolling shoot 'em up) chạy web/mobile,
phong cách WindWings: Space Shooter (tham chiếu ảnh trong repo gốc).
Toàn bộ sprite vẽ bằng code (canvas 2D), không asset mạng, không dependency.

## Chạy game (web export)

```bash
npm run serve          # python3 -m http.server 8000 --bind 0.0.0.0 --directory game
# mở http://localhost:8000 (hoặc host preview của sandbox)
```

## Test headless (không cần browser)

```bash
npm test               # node tools/headless_test.mjs — 49 test, cả soak 5 phút
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
    telegraph.js     visual telegraph tự remove (HARD RULE: không damage trước khi hết telegraph)
    combat.js        collision, bomb, boss death sequence
    particles.js     particle + coin burst
    fx.js            popup, hurt feedback
    score.js         score + combo multiplier
    hud.js           HUD + menu pause/victory/defeat/quit
    audio.js         placeholder silence (// TODO: add sound)
    game.js          loop delta-time, slow-mo, shake, flash, pause
tools/               headless test harness (stub canvas/DOM)
```

## Build APK/AAB (máy có Android SDK)

Sandbox CI không có Java/Android SDK nên không build APK tại đây; web export
là deliverable chính. Trên máy dev: xem `docs/BUILD_ANDROID.md`
(Capacitor wrap thư mục `game/` → Android Studio/gradle → APK).
