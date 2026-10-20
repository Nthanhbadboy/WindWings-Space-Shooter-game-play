// Particles + coin burst sprites. Timer-driven, pooled in plain arrays
// (dead items spliced out every frame => no leak).
import { CONFIG } from './config.js';
import { randRange } from './utils.js';

const FX = CONFIG.fx;

export class Particle {
  constructor(x, y, vx, vy, life, size, color, gravity) {
    this.x = x;
    this.y = y;
    this.vx = vx;
    this.vy = vy;
    this.life = life;
    this.maxLife = life;
    this.size = size;
    this.color = color;
    this.gravity = gravity || 0;
    this.done = false;
  }

  update(dt) {
    this.life -= dt;
    if (this.life <= 0) {
      this.done = true;
      return;
    }
    this.vy += this.gravity * dt;
    this.x += this.vx * dt;
    this.y += this.vy * dt;
  }

  draw(ctx) {
    const k = Math.max(0, this.life / this.maxLife);
    ctx.globalAlpha = k;
    ctx.fillStyle = this.color;
    const s = this.size * (0.5 + k * 0.5);
    ctx.fillRect(this.x - s / 2, this.y - s / 2, s, s);
    ctx.globalAlpha = 1;
  }
}

/** Radial explosion burst. */
export function burst(game, x, y, count, opts) {
  const e = FX.explosion;
  const colors = (opts && opts.colors) || e.colors;
  const speedMul = (opts && opts.speedMul) || 1;
  for (let i = 0; i < count; i++) {
    const a = Math.random() * Math.PI * 2;
    const sp = randRange(e.minSpeed, e.maxSpeed) * speedMul;
    game.particles.push(new Particle(
      x, y,
      Math.cos(a) * sp, Math.sin(a) * sp,
      randRange(e.lifeMin, e.maxLife),
      randRange(e.sizeMin, e.sizeMax),
      colors[i % colors.length],
      0
    ));
  }
}

/** Small hit sparks (enemy damage feedback). */
export function sparks(game, x, y, count) {
  for (let i = 0; i < count; i++) {
    const a = Math.random() * Math.PI * 2;
    const sp = randRange(40, 180);
    game.particles.push(new Particle(
      x, y, Math.cos(a) * sp, Math.sin(a) * sp,
      randRange(0.15, 0.35), randRange(1.5, 3.5), '#ffffff', 0
    ));
  }
}

/** Gold coin sprite flying out (boss death reward burst). */
export class Coin {
  constructor(x, y) {
    const c = FX.coin;
    const a = Math.random() * Math.PI * 2;
    const sp = randRange(c.minSpeed, c.maxSpeed);
    this.x = x;
    this.y = y;
    this.vx = Math.cos(a) * sp;
    this.vy = Math.sin(a) * sp - 120;
    this.life = c.life;
    this.spin = Math.random() * Math.PI;
    this.done = false;
  }

  update(dt) {
    this.life -= dt;
    if (this.life <= 0) {
      this.done = true;
      return;
    }
    const c = FX.coin;
    this.vy += c.gravity * dt;
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    this.spin += c.spin * dt;
  }

  draw(ctx) {
    const c = FX.coin;
    const k = Math.max(0, Math.min(1, this.life / (c.life * 0.4)));
    const squish = Math.abs(Math.cos(this.spin));
    ctx.save();
    ctx.globalAlpha = k;
    ctx.translate(this.x, this.y);
    ctx.scale(Math.max(0.15, squish), 1);
    ctx.fillStyle = c.color;
    ctx.strokeStyle = c.edge;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(0, 0, c.radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.restore();
    ctx.globalAlpha = 1;
  }
}

export function coinBurst(game, x, y, count) {
  for (let i = 0; i < count; i++) game.coins.push(new Coin(x, y));
}

export function updateParticles(game, dt) {
  for (let i = game.particles.length - 1; i >= 0; i--) {
    game.particles[i].update(dt);
    if (game.particles[i].done) game.particles.splice(i, 1);
  }
  for (let i = game.coins.length - 1; i >= 0; i--) {
    game.coins[i].update(dt);
    if (game.coins[i].done) game.coins.splice(i, 1);
  }
}

export function drawParticles(game, ctx) {
  for (const p of game.particles) p.draw(ctx);
  for (const c of game.coins) c.draw(ctx);
}
