// Bullets: one class covers player shots, enemy shots, boss shots and
// homing missiles (optional homing + trail rendering).
import { CONFIG } from './config.js';

const S = CONFIG.screen;

export class Bullet {
  /**
   * @param {object} o {x,y,vx,vy,radius,damage?,life,color,glow,
   *                    homing?:{turnRate, duration}, trail?:boolean,
   *                    target?:() => {x,y}|null}
   */
  constructor(o) {
    this.x = o.x;
    this.y = o.y;
    this.vx = o.vx;
    this.vy = o.vy;
    this.radius = o.radius;
    this.damage = o.damage || 0;   // informational: any hit costs a life
    this.life = o.life;
    this.color = o.color;
    this.glow = o.glow || o.color;
    this.homing = o.homing || null;
    this.target = o.target || null;
    this.trail = o.trail ? [] : null;
    this.dead = false;
  }

  update(dt) {
    if (this.homing && this.homing.duration > 0) {
      this.homing.duration -= dt;
      const t = this.target ? this.target() : null;
      if (t) {
        const want = Math.atan2(t.y - this.y, t.x - this.x);
        const cur = Math.atan2(this.vy, this.vx);
        let diff = want - cur;
        while (diff > Math.PI) diff -= Math.PI * 2;
        while (diff < -Math.PI) diff += Math.PI * 2;
        const maxTurn = this.homing.turnRate * dt;
        const turn = Math.max(-maxTurn, Math.min(maxTurn, diff));
        const sp = Math.hypot(this.vx, this.vy);
        const ang = cur + turn;
        this.vx = Math.cos(ang) * sp;
        this.vy = Math.sin(ang) * sp;
      }
    }
    if (this.trail) {
      this.trail.push({ x: this.x, y: this.y });
      if (this.trail.length > 8) this.trail.shift();
    }
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    this.life -= dt;
    if (
      this.life <= 0 ||
      this.x < -60 || this.x > S.width + 60 ||
      this.y < -60 || this.y > S.height + 60
    ) {
      this.dead = true;
    }
  }

  draw(ctx) {
    ctx.save();
    if (this.trail && this.trail.length > 1) {
      ctx.strokeStyle = this.glow;
      ctx.lineWidth = this.radius * 0.8;
      ctx.globalAlpha = 0.4;
      ctx.beginPath();
      ctx.moveTo(this.trail[0].x, this.trail[0].y);
      for (const p of this.trail) ctx.lineTo(p.x, p.y);
      ctx.stroke();
    }
    ctx.globalAlpha = 0.35;
    ctx.fillStyle = this.glow;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius * 1.8, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;
    ctx.fillStyle = this.color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}
