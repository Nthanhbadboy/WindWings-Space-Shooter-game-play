// Feedback FX: score/damage popups, player-hit reaction, kill feedback.
// Everything is timer-based inside the update loop (no setTimeout).
import { CONFIG } from './config.js';
import { sparks } from './particles.js';

const FX = CONFIG.fx;
const POP = FX.popup;

/** Floating number: rises and fades out. */
export class Popup {
  constructor(x, y, text, color) {
    this.x = x;
    this.y = y;
    this.text = text;
    this.color = color;
    this.t = 0;
    this.done = false;
  }

  update(dt) {
    this.t += dt;
    this.y -= POP.riseSpeed * dt;
    if (this.t >= POP.life) this.done = true;
  }

  draw(ctx) {
    const k = this.t / POP.life;
    ctx.save();
    ctx.globalAlpha = 1 - k * k;
    ctx.font = `bold ${POP.fontPx}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.lineWidth = 4;
    ctx.strokeStyle = 'rgba(0,0,0,0.7)';
    ctx.strokeText(this.text, this.x, this.y);
    ctx.fillStyle = this.color;
    ctx.fillText(this.text, this.x, this.y);
    ctx.restore();
  }
}

export function spawnPopup(game, x, y, text, color) {
  game.popups.push(new Popup(x, y, text, color || POP.color));
}

export function updatePopups(game, dt) {
  for (let i = game.popups.length - 1; i >= 0; i--) {
    game.popups[i].update(dt);
    if (game.popups[i].done) game.popups.splice(i, 1);
  }
}

export function drawPopups(game, ctx) {
  for (const p of game.popups) p.draw(ctx);
}

// ------------------------------------------------------------- reactions

/** Player lost a life: shake 6px/0.25s, red flash 0.15s, slow-mo 0.2s. */
export function playerHitFx(game, x, y) {
  const f = FX.playerHit;
  game.addShake(f.shake.amp, f.shake.dur);
  game.addFlash('#ff2b2b', f.redFlashAlpha, f.redFlash);
  game.setSlowMo(f.slowMo.scale, f.slowMo.dur);
  game.audio.play('player_hit');
}

/** Enemy took damage: white flash handled on enemy + small spark burst. */
export function enemyHitFx(game, x, y) {
  sparks(game, x, y, CONFIG.enemies.hitParticles);
  game.audio.play('enemy_hit');
}
