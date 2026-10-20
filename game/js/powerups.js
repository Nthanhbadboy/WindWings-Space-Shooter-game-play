// Power-ups: fall from killed enemies, magnet toward the player when
// close, collect -> weapon level up (max 5) or +1 bomb.
import { CONFIG } from './config.js';
import { dist } from './utils.js';
import { spawnPopup } from './fx.js';

const PU = CONFIG.powerup;
const P = CONFIG.player;
const S = CONFIG.screen;

export class Powerup {
  constructor(x, y, kind) {
    this.x = x;
    this.y = y;
    this.kind = kind; // 'weapon' | 'bomb'
    this.radius = PU.radius;
    this.t = 0;
    this.done = false;
  }

  update(dt, game) {
    this.t += dt;
    const p = game.player;
    const d = p.alive ? dist(this.x, this.y, p.x, p.y) : Infinity;
    if (d <= P.magnetRadius) {
      // magnet: fly to the player
      const ux = (p.x - this.x) / Math.max(1, d);
      const uy = (p.y - this.y) / Math.max(1, d);
      this.x += ux * PU.magnetSpeed * dt;
      this.y += uy * PU.magnetSpeed * dt;
    } else {
      this.y += PU.fallSpeed * dt;
    }
    if (this.y > S.height + 40) {
      this.done = true;
      return;
    }
    if (p.alive && d <= P.pickupRadius) this._collect(game);
  }

  _collect(game) {
    this.done = true;
    game.audio.play('powerup_collect');
    if (this.kind === 'weapon') {
      if (game.player.weaponLevel < 5) {
        game.player.weaponLevel++;
        spawnPopup(game, game.player.x, game.player.y - 40, `POWER ${game.player.weaponLevel}`);
      } else {
        spawnPopup(game, game.player.x, game.player.y - 40, 'MAX');
      }
    } else {
      game.player.bombs++;
      spawnPopup(game, game.player.x, game.player.y - 40, 'BOMB +1');
    }
  }

  draw(ctx) {
    const c = PU.colors;
    const pulse = 1 + Math.sin(this.t * 6) * 0.12;
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.scale(pulse, pulse);
    ctx.globalAlpha = 0.35;
    ctx.fillStyle = this.kind === 'weapon' ? c.weapon : c.bomb;
    ctx.beginPath();
    ctx.arc(0, 0, this.radius * 1.6, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;
    ctx.fillStyle = this.kind === 'weapon' ? c.weapon : c.bomb;
    ctx.strokeStyle = c.rim;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = '#04050d';
    ctx.font = `bold ${PU.fontPx}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(this.kind === 'weapon' ? PU.labels.weapon : PU.labels.bomb, 0, 1);
    ctx.restore();
  }
}

/** Drop roll after an enemy kill: 5% weapon, 1% bomb. */
export function rollDrop(game, enemy) {
  if (Math.random() < PU.bombDropChance) {
    game.powerups.push(new Powerup(enemy.x, enemy.y, 'bomb'));
  } else if (Math.random() < PU.dropChance) {
    game.powerups.push(new Powerup(enemy.x, enemy.y, 'weapon'));
  }
}

export function updatePowerups(game, dt) {
  for (let i = game.powerups.length - 1; i >= 0; i--) {
    game.powerups[i].update(dt, game);
    if (game.powerups[i].done) game.powerups.splice(i, 1);
  }
}

export function drawPowerups(game, ctx) {
  for (const pu of game.powerups) pu.draw(ctx);
}
