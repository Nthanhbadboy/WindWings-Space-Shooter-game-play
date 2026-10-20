// Combat systems extracted from game.js: bullet collisions, bomb and the
// boss death sequence. Plain functions over the Game instance.
import { CONFIG } from './config.js';
import { sparks, burst, coinBurst } from './particles.js';

/** Player bullets vs boss + enemies. */
export function collideBullets(game) {
  for (const b of game.bullets) {
    if (b.dead) continue;
    if (game.boss && game.boss.vulnerable) {
      const bo = game.boss;
      const dx = b.x - bo.x;
      const dy = b.y - bo.y;
      const rr = b.radius + bo.radius * 0.8;
      if (dx * dx + dy * dy <= rr * rr) {
        b.dead = true;
        bo.hurt(b.damage);
        continue;
      }
    }
    for (const e of game.enemies) {
      if (e.dead) continue;
      const dx = b.x - e.x;
      const dy = b.y - e.y;
      const rr = b.radius + e.radius;
      if (dx * dx + dy * dy <= rr * rr) {
        b.dead = true;
        e.hurt(b.damage, game);
        break;
      }
    }
  }
  for (let i = game.bullets.length - 1; i >= 0; i--) {
    if (game.bullets[i].dead) game.bullets.splice(i, 1);
  }
  for (let i = game.enemies.length - 1; i >= 0; i--) {
    if (game.enemies[i].dead) game.enemies.splice(i, 1);
  }
}

/** Enemy/boss bullets vs the tiny player hitbox. */
export function collideEnemyBullets(game) {
  const p = game.player;
  for (const b of game.enemyBullets) {
    if (b.dead || !p.alive) continue;
    const dx = b.x - p.x;
    const dy = b.y - p.y;
    const rr = b.radius + p.hitboxRadius;
    if (dx * dx + dy * dy <= rr * rr) {
      if (p.hit()) b.dead = true;
    }
  }
  for (let i = game.enemyBullets.length - 1; i >= 0; i--) {
    if (game.enemyBullets[i].dead) game.enemyBullets.splice(i, 1);
  }
}

/** Bomb: clear bullets, 500 dmg everywhere, flash + slow-mo. */
export function useBomb(game) {
  if (game.state !== 'playing' || game.paused) return false;
  const p = game.player;
  if (!p.alive || p.bombs <= 0) return false;
  p.bombs--;
  const b = CONFIG.bomb;
  game.addFlash('#ffffff', b.flash.alpha, b.flash.dur);
  game.setSlowMo(b.slowMo.scale, b.slowMo.dur);
  for (const eb of game.enemyBullets) sparks(game, eb.x, eb.y, 3);
  game.enemyBullets.length = 0;
  for (const e of game.enemies) e.hurt(b.damage, game);
  for (let i = game.enemies.length - 1; i >= 0; i--) {
    if (game.enemies[i].dead) game.enemies.splice(i, 1);
  }
  if (game.boss && game.boss.vulnerable) game.boss.hurt(b.damage);
  game.audio.play('bomb_use');
  return true;
}

/** Boss died: slow-mo, staged explosions, coin burst, white fade, victory. */
export function updateBossDeath(game, dt) {
  const d = CONFIG.boss.death;
  const seq = game.bossDeath;
  seq.t += dt;
  while (seq.wave < d.explosionWaves && seq.t >= seq.wave * d.waveInterval) {
    burst(game, game.boss.x + (Math.random() - 0.5) * 120,
      game.boss.y + (Math.random() - 0.5) * 120, d.particlesPerWave);
    game.addShake(4, 0.2);
    seq.wave++;
  }
  if (!seq.coins && seq.t > 0.15) {
    seq.coins = true;
    coinBurst(game, game.boss.x, game.boss.y, d.coins);
  }
  game.victoryAlpha = Math.max(0, Math.min(1, (seq.t - d.overlayDelay) / d.fadeDuration));
  if (seq.t >= d.overlayDelay + d.fadeDuration && game.state === 'playing') {
    game.finishLevel();
  }
}
