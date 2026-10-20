// Player ship: drag-to-move with snappy follow, auto-fire while touching,
// weapon levels 1-5, lives + respawn i-frames, tiny shmup hitbox.
import { CONFIG } from './config.js';
import { clamp } from './utils.js';
import { Bullet } from './projectiles.js';
import { burst } from './particles.js';
import { playerHitFx } from './fx.js';

const P = CONFIG.player;
const S = CONFIG.screen;
const DEG = Math.PI / 180;

export class Player {
  constructor(game) {
    this.game = game;
    this.reset();
  }

  reset() {
    this.x = P.startX;
    this.y = P.startY;
    this.spriteRadius = P.spriteRadius;
    this.hitboxRadius = P.hitboxRadius;
    this.weaponLevel = 1;
    this.lives = P.lives;
    this.bombs = P.bombsInitial;
    this.state = 'alive';        // alive | dead(respawning) | gone
    this.respawnT = 0;
    this.invulnT = P.respawnInvuln * 0.33; // brief spawn grace at round start
    this.fireT = 0;
    this.engine = 0;
  }

  get alive() {
    return this.state === 'alive';
  }

  update(dt, input) {
    this.engine += dt;
    if (this.state === 'dead') {
      this.respawnT -= dt;
      if (this.respawnT <= 0) {
        this.state = 'alive';
        this.x = P.startX;
        this.y = P.startY;
        this.invulnT = P.respawnInvuln; // 3s blinking i-frames
      }
      return;
    }
    if (this.state === 'gone') return;

    // ---- movement: chase finger (or keyboard) ----
    if (input.dragging) {
      const k = Math.min(1, P.followRate * dt);
      let dx = (input.dragTarget.x - this.x) * k;
      let dy = (input.dragTarget.y - this.y) * k;
      const d = Math.hypot(dx, dy);
      const cap = P.maxFollowSpeed * dt;
      if (d > cap) {
        dx = (dx / d) * cap;
        dy = (dy / d) * cap;
      }
      this.x += dx;
      this.y += dy;
    } else if (input.keyMove.x || input.keyMove.y) {
      this.x += input.keyMove.x * P.keySpeed * dt;
      this.y += input.keyMove.y * P.keySpeed * dt;
    }
    this.x = clamp(this.x, P.spriteRadius, S.width - P.spriteRadius);
    this.y = clamp(this.y, P.spriteRadius, S.height - P.spriteRadius);

    if (this.invulnT > 0) this.invulnT -= dt;

    // ---- auto-fire while touching ----
    if (input.firing) {
      this.fireT -= dt;
      while (this.fireT <= 0) {
        this._fireVolley();
        this.fireT += P.fireInterval;
      }
    } else {
      this.fireT = 0;
    }
  }

  _fireVolley() {
    const lvl = P.weaponLevels[this.weaponLevel] || P.weaponLevels[1];
    const b = P.bullet;
    for (let i = 0; i < lvl.angles.length; i++) {
      const a = lvl.angles[i] * DEG;
      const off = lvl.offsets ? lvl.offsets[i] : 0;
      this.game.bullets.push(new Bullet({
        x: this.x + off,
        y: this.y - P.spriteRadius,
        vx: Math.sin(a) * b.speed,
        vy: -Math.cos(a) * b.speed,
        radius: b.radius,
        damage: b.damage,
        life: b.life,
        color: b.color,
        glow: b.glow,
      }));
    }
    if (lvl.sideLasers) {
      const l = P.sideLaser;
      for (const s of [-1, 1]) {
        this.game.bullets.push(new Bullet({
          x: this.x + s * l.offsetX,
          y: this.y - P.spriteRadius * 0.5,
          vx: 0,
          vy: -l.speed,
          radius: l.radius,
          damage: l.damage,
          life: b.life,
          color: l.color,
          glow: l.glow,
        }));
      }
    }
    this.game.audio.play('player_shoot');
  }

  /** Lose one life. Returns false if invulnerable / already dead. */
  hit() {
    if (!this.alive || this.invulnT > 0) return false;
    this.lives--;
    burst(this.game, this.x, this.y, CONFIG.enemies.deathParticles, { speedMul: 0.8 });
    playerHitFx(this.game, this.x, this.y);
    this.game.onPlayerHit(); // combo reset
    if (this.lives <= 0) {
      this.state = 'gone';
      this.game.audio.play('player_death');
      this.game.onPlayerDefeat();
    } else {
      this.state = 'dead';
      this.respawnT = P.respawnDelay;
    }
    return true;
  }

  draw(ctx, focused) {
    if (this.state !== 'alive') return;
    const blink = this.invulnT > 0 && Math.floor(this.invulnT * 10) % 2 === 0;
    ctx.save();
    ctx.translate(this.x, this.y);
    if (blink) ctx.globalAlpha = 0.4;

    // engine flame
    const f = 10 + Math.sin(this.engine * 30) * 4;
    ctx.fillStyle = P.colors.engine;
    ctx.beginPath();
    ctx.moveTo(-8, 18);
    ctx.lineTo(0, 18 + f);
    ctx.lineTo(8, 18);
    ctx.closePath();
    ctx.fill();

    // hull
    ctx.fillStyle = P.colors.body;
    ctx.beginPath();
    ctx.moveTo(0, -30);
    ctx.lineTo(-22, 18);
    ctx.lineTo(-8, 12);
    ctx.lineTo(0, 16);
    ctx.lineTo(8, 12);
    ctx.lineTo(22, 18);
    ctx.closePath();
    ctx.fill();

    // cockpit
    ctx.fillStyle = P.colors.accent;
    ctx.beginPath();
    ctx.moveTo(0, -18);
    ctx.lineTo(-6, 2);
    ctx.lineTo(6, 2);
    ctx.closePath();
    ctx.fill();

    // tiny visible hitbox dot while focused (touching)
    if (focused) {
      ctx.globalAlpha = 1;
      ctx.fillStyle = P.colors.hitbox;
      ctx.beginPath();
      ctx.arc(0, 0, this.hitboxRadius * 0.6, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
    ctx.globalAlpha = 1;
  }
}
