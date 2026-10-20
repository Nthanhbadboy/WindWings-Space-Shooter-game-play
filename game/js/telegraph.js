// Telegraphs: standalone visual warnings, timer-driven, auto-removed.
// HARD RULE: no boss attack deals damage before its telegraph finishes.
import { CONFIG } from './config.js';
import { Timer, lerp } from './utils.js';

const RED = '#ff2a2a';
const B = CONFIG.boss;

export class Telegraph {
  /** @param {string} type @param {number} duration @param {object} p params */
  constructor(type, duration, p = {}) {
    this.type = type;
    this.timer = new Timer(duration);
    this.p = p;
    this.done = false;
  }

  update(dt) {
    this.timer.update(dt);
    if (this.timer.done) this.done = true;
  }

  get progress() {
    return this.timer.progress;
  }

  draw(ctx) {
    switch (this.type) {
      case 'aimLine': return this._lines(ctx, [this.p.angle], this.p.len || 1400, RED);
      case 'fanLines': return this._lines(ctx, this.p.angles, this.p.len || 1400, RED);
      case 'crossLines': return this._lines(ctx, this.p.angles, 1800, RED);
      case 'sweepLine': return this._sweepLine(ctx);
      case 'ringGlow': return this._ringGlow(ctx);
      case 'spiralGlow': return this._glow(ctx, B.colors.telegraphGlowP2, true);
      case 'hellGlow': return this._glow(ctx, B.colors.telegraphGlowP3, false);
      case 'homingPods': return this._homingPods(ctx);
      case 'beamV': return this._beamV(ctx);
      case 'beamAng': return this._beamAng(ctx);
      default: return undefined;
    }
  }

  /** Rays from the anchor; alpha ramps up over the telegraph. */
  _lines(ctx, angles, len, color) {
    const a = lerp(this.p.alphaFrom ?? 0.25, this.p.alphaTo ?? 0.8, this.progress);
    ctx.save();
    ctx.globalAlpha = a;
    ctx.strokeStyle = color;
    ctx.lineWidth = this.p.lineWidth || 4;
    for (const ang of angles) {
      ctx.beginPath();
      ctx.moveTo(this.p.x, this.p.y);
      ctx.lineTo(this.p.x + Math.cos(ang) * len, this.p.y + Math.sin(ang) * len);
      ctx.stroke();
    }
    ctx.restore();
  }

  // Vertical laser lane: bright line at fromX + faint band over sweep range.
  _sweepLine(ctx) {
    const pr = this.progress;
    ctx.save();
    ctx.globalAlpha = 0.08 + pr * 0.1;
    ctx.fillStyle = RED;
    ctx.fillRect(Math.min(this.p.fromX, this.p.toX), 0,
      Math.abs(this.p.toX - this.p.fromX), CONFIG.screen.height);
    ctx.globalAlpha = lerp(0.25, 0.9, pr);
    ctx.strokeStyle = RED;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(this.p.fromX, 0);
    ctx.lineTo(this.p.fromX, CONFIG.screen.height);
    ctx.stroke();
    ctx.restore();
  }

  _ringGlow(ctx) {
    const pr = this.progress;
    const r = lerp(this.p.r0 || 60, this.p.r1 || 130, pr);
    ctx.save();
    ctx.globalAlpha = lerp(0.3, 0.9, pr);
    ctx.strokeStyle = B.colors.telegraphGlowP2;
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.arc(this.p.x, this.p.y, r, 0, Math.PI * 2);
    ctx.stroke();
    ctx.globalAlpha *= 0.4;
    ctx.fillStyle = B.colors.telegraphGlowP2;
    ctx.beginPath();
    ctx.arc(this.p.x, this.p.y, r * 0.8, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  /** Pulsing aura around the boss; spiral adds orbiting motes. */
  _glow(ctx, color, orbit) {
    const pr = this.progress;
    ctx.save();
    ctx.globalAlpha = lerp(0.25, 0.75, pr);
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(this.p.x, this.p.y, (this.p.r || 120) * (0.8 + pr * 0.3), 0, Math.PI * 2);
    ctx.globalAlpha *= 0.35;
    ctx.fill();
    if (orbit) {
      ctx.globalAlpha = lerp(0.4, 1, pr);
      for (let i = 0; i < 6; i++) {
        const a = pr * Math.PI * 4 + (i * Math.PI) / 3;
        const rr = (this.p.r || 120) * 0.9;
        ctx.beginPath();
        ctx.arc(this.p.x + Math.cos(a) * rr, this.p.y + Math.sin(a) * rr, 5, 0, Math.PI * 2);
        ctx.fill();
      }
    } else {
      const blink = Math.sin(pr * Math.PI * 8) > 0;
      ctx.globalAlpha = blink ? 0.8 : 0.2;
      ctx.strokeStyle = color;
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.arc(this.p.x, this.p.y, (this.p.r || 120) * 1.15, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.restore();
  }

  // Vertical firing laser lane (laser sweep active phase).
  _beamV(ctx) {
    const hw = this.p.halfWidth;
    const x = this.p.ref ? this.p.ref.beamX : this.p.x;
    ctx.save();
    ctx.globalAlpha = 0.85;
    ctx.fillStyle = RED;
    ctx.fillRect(x - hw, 0, hw * 2, CONFIG.screen.height);
    ctx.globalAlpha = 1;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(x - hw * 0.4, 0, hw * 0.8, CONFIG.screen.height);
    ctx.restore();
  }

  // Angled firing beam through the anchor (laser cross active phase).
  _beamAng(ctx) {
    const hw = this.p.halfWidth;
    ctx.save();
    ctx.translate(this.p.x, this.p.y);
    ctx.rotate(this.p.angle);
    ctx.globalAlpha = 0.85;
    ctx.fillStyle = RED;
    ctx.fillRect(-hw, -1000, hw * 2, 2000);
    ctx.globalAlpha = 1;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(-hw * 0.4, -1000, hw * 0.8, 2000);
    ctx.restore();
  }

  // Two glowing launch pods (homing missiles charging).
  _homingPods(ctx) {
    const pr = this.progress;
    const blink = 0.4 + 0.6 * Math.abs(Math.sin(pr * Math.PI * 6));
    ctx.save();
    ctx.globalAlpha = blink;
    ctx.fillStyle = RED;
    for (const s of [-1, 1]) {
      ctx.beginPath();
      ctx.arc(this.p.x + s * (this.p.r || 90) * 0.95, this.p.y + (this.p.r || 90) * 0.35,
        10 + pr * 6, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }
}
