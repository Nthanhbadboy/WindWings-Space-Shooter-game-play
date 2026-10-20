// Enemies: 5 types (chaser, shooter, turret, formation, elite).
// Behaviors are plain update functions keyed by type (steps 2 & 4).
import { CONFIG } from './config.js';
import { angleTo, randRange } from './utils.js';
import { Bullet } from './projectiles.js';
import { burst } from './particles.js';
import { enemyHitFx } from './fx.js';

const S = CONFIG.screen;
const E = CONFIG.enemies;

export class Enemy {
  constructor(type, x, y, params = {}) {
    const base = E[type];
    const m = params.mods || { hp: 1, speed: 1, bullet: 1 };
    // shallow clone + per-level difficulty scaling; behaviors read this.cfg
    const c = Object.assign({}, base);
    c.hp = Math.max(1, Math.round(base.hp * m.hp));
    c.speed = base.speed * m.speed;
    if (base.bulletSpeed) c.bulletSpeed = base.bulletSpeed * m.bullet;
    if (base.aimedSpeed) c.aimedSpeed = base.aimedSpeed * m.bullet;
    this.type = type;
    this.cfg = c;
    this.x = x;
    this.y = y;
    this.x0 = x;
    this.hp = c.hp;
    this.radius = c.radius;
    this.flashT = 0;
    this.t = 0;
    this.dead = false;
    this.params = params;
    // per-type runtime state
    // per-type entry state
    this.state = 'move';
    if (type === 'shooter') {
      this.state = 'descend';
      this.params.stopY = params.stopY !== undefined
        ? params.stopY : randRange(c.stopYMin, c.stopYMax);
    }
    if (type === 'turret') this.state = 'enter';
    this.stateT = 0;
    this.fireT = type === 'elite' ? c.fireInterval : 0;
    this.dir = params.dir || 1;
  }

  update(dt, game) {
    this.t += dt;
    this.stateT += dt;
    if (this.flashT > 0) this.flashT -= dt;
    BEHAVIORS[this.type].update(this, dt, game);
  }

  hurt(dmg, game) {
    if (this.dead) return false;
    this.hp -= dmg;
    this.flashT = E.hitFlash;
    enemyHitFx(game, this.x, this.y);
    if (this.hp <= 0) this.die(game, false);
    return true;
  }

  die(game, noScore) {
    if (this.dead) return;
    this.dead = true;
    burst(game, this.x, this.y, E.deathParticles);
    game.audio.play('enemy_explosion');
    if (!noScore) {
      game.score.addKill(this.x, this.y);
      game.onEnemyKilled(this); // powerup/bomb drop rolls (step 3)
    }
  }

  draw(ctx) {
    ctx.save();
    ctx.translate(this.x, this.y);
    const r = this.radius;
    ctx.fillStyle = this.cfg.color;
    ctx.strokeStyle = this.cfg.outline;
    ctx.lineWidth = 3;
    this._shape(ctx, r);
    ctx.fill();
    ctx.stroke();
    if (this.flashT > 0) {
      ctx.globalAlpha = this.flashT / E.hitFlash;
      ctx.fillStyle = '#ffffff';
      this._shape(ctx, r);
      ctx.fill();
    }
    ctx.restore();
    ctx.globalAlpha = 1;
  }

  _shape(ctx, r) {
    switch (this.type) {
      case 'chaser': // downward dart
        ctx.beginPath();
        ctx.moveTo(0, r);
        ctx.lineTo(-r * 0.8, -r * 0.7);
        ctx.lineTo(0, -r * 0.25);
        ctx.lineTo(r * 0.8, -r * 0.7);
        ctx.closePath();
        break;
      case 'formation': // small diamond
        ctx.beginPath();
        ctx.moveTo(0, r);
        ctx.lineTo(-r * 0.9, 0);
        ctx.lineTo(0, -r);
        ctx.lineTo(r * 0.9, 0);
        ctx.closePath();
        break;
      case 'shooter': // wide body + wings
        ctx.beginPath();
        ctx.moveTo(0, r);
        ctx.lineTo(-r, r * 0.1);
        ctx.lineTo(-r * 0.6, -r * 0.8);
        ctx.lineTo(r * 0.6, -r * 0.8);
        ctx.lineTo(r, r * 0.1);
        ctx.closePath();
        break;
      case 'turret': // hexagon turret
        ctx.beginPath();
        for (let i = 0; i < 6; i++) {
          const a = (Math.PI / 3) * i + Math.PI / 6;
          const px = Math.cos(a) * r;
          const py = Math.sin(a) * r;
          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.closePath();
        break;
      default: { // elite: big spiked hull
        ctx.beginPath();
        ctx.moveTo(0, r);
        ctx.lineTo(-r * 0.9, r * 0.2);
        ctx.lineTo(-r * 1.1, -r * 0.5);
        ctx.lineTo(-r * 0.35, -r * 0.9);
        ctx.lineTo(r * 0.35, -r * 0.9);
        ctx.lineTo(r * 1.1, -r * 0.5);
        ctx.lineTo(r * 0.9, r * 0.2);
        ctx.closePath();
        break;
      }
    }
  }
}

// ------------------------------------------------------------- helpers
function enemyBullet(game, e, angle, speed) {
  const b = E.bullet;
  game.enemyBullets.push(new Bullet({
    x: e.x,
    y: e.y + e.radius * 0.4,
    vx: Math.cos(angle) * speed,
    vy: Math.sin(angle) * speed,
    radius: b.radius,
    life: b.life,
    color: b.color,
    glow: b.glow,
  }));
}

const DOWN = Math.PI / 2;

// ------------------------------------------------------------- behaviors
const BEHAVIORS = {
  // Fly straight down, fast. No shooting.
  chaser: {
    update(e, dt) {
      e.y += e.cfg.speed * dt;
      if (e.y > S.height + 60) e.dead = true; // escaped, no score
    },
  },
  // V-formation unit: dives with a gentle sway, keeps its lane.
  formation: {
    update(e, dt) {
      e.y += e.cfg.speed * dt;
      e.x = e.x0 + Math.sin(e.t * Math.PI * 2 * e.cfg.swayFreq) * e.cfg.swayAmp;
      if (e.y > S.height + 60) e.dead = true;
    },
  },
  // Descend -> stop 2s -> aimed shots while drifting down slowly.
  shooter: {
    update(e, dt, game) {
      const c = e.cfg;
      if (e.state === 'descend') {
        e.y += c.speed * dt;
        if (e.y >= e.params.stopY) {
          e.state = 'pause';
          e.stateT = 0;
        }
      } else if (e.state === 'pause') {
        if (e.stateT >= c.pauseBeforeFire) {
          e.state = 'fire';
          e.fireT = 0;
        }
      } else {
        e.fireT -= dt;
        if (e.fireT <= 0) {
          const p = game.player;
          enemyBullet(game, e, angleTo(e.x, e.y, p.x, p.y), c.bulletSpeed);
          e.fireT += c.fireInterval;
        }
        e.y += c.driftSpeed * dt;
        if (e.y > S.height + 60) e.dead = true;
      }
    },
  },
  // Horizontal patrol with 1s firing stops (3-way spread).
  turret: {
    update(e, dt, game) {
      const c = e.cfg;
      if (e.state === 'enter') {
        e.x += e.dir * c.speed * 1.6 * dt;
        const inside = e.x > 60 && e.x < S.width - 60;
        if (inside) {
          e.state = 'move';
          e.stateT = 0;
        }
      } else if (e.state === 'move') {
        e.x += e.dir * c.speed * dt;
        if (e.stateT >= c.moveTime) {
          e.state = 'stop';
          e.stateT = 0;
          e.fireT = 0;
        }
      } else {
        e.fireT -= dt;
        if (e.fireT <= 0) {
          const half = (c.spreadDeg * Math.PI) / 180;
          for (let i = 0; i < c.spreadCount; i++) {
            const a = DOWN + (i - (c.spreadCount - 1) / 2) * half;
            enemyBullet(game, e, a, c.bulletSpeed);
          }
          e.fireT += c.fireInterval;
        }
        if (e.stateT >= c.stopTime) {
          e.dir *= -1;
          e.state = 'move';
          e.stateT = 0;
        }
      }
    },
  },
  // Slow zigzag descent, 5-way spread + aimed shot.
  elite: {
    update(e, dt, game) {
      const c = e.cfg;
      e.y += c.speed * dt * (e.y < c.stopY ? 1 : 0.35);
      e.x = e.x0 + Math.sin(e.t * Math.PI * 2 * c.zigzagFreq) * c.zigzagAmp;
      e.fireT -= dt;
      if (e.fireT <= 0 && e.y > 0) {
        const half = (c.spreadDeg * Math.PI) / 180;
        for (let i = 0; i < c.spreadCount; i++) {
          const a = DOWN + (i - (c.spreadCount - 1) / 2) * (half / 2);
          enemyBullet(game, e, a, c.bulletSpeed);
        }
        const p = game.player;
        enemyBullet(game, e, angleTo(e.x, e.y, p.x, p.y), c.aimedSpeed);
        e.fireT += c.fireInterval;
      }
      if (e.y > S.height + 60) e.dead = true;
    },
  },
};

/** Spawn helper. 'formation' creates the full 5-ship V at once. */
export function spawnEnemy(game, type, params = {}) {
  params = Object.assign({}, params, { mods: game.levelMods || null });
  if (type === 'formation') {
    const c = E.formation;
    for (let i = -2; i <= 2; i++) {
      const x = params.x + i * c.spacingX;
      const y = -60 - Math.abs(i) * c.spacingY; // leader lowest => V shape
      game.enemies.push(new Enemy('formation', x, y, params));
    }
    return null;
  }
  const e = new Enemy(type, params.x, params.y !== undefined ? params.y : -60, params);
  game.enemies.push(e);
  return e;
}

export function updateEnemies(game, dt) {
  const p = game.player;
  for (let i = game.enemies.length - 1; i >= 0; i--) {
    const e = game.enemies[i];
    e.update(dt, game);
    // body contact costs a life (shmup default), enemy dies without score
    if (!e.dead && E.contactKill && p.alive) {
      const dx = e.x - p.x;
      const dy = e.y - p.y;
      const rr = e.radius + p.hitboxRadius;
      if (dx * dx + dy * dy <= rr * rr) {
        if (p.hit()) e.die(game, true);
      }
    }
    if (e.dead) game.enemies.splice(i, 1);
  }
}
