// Score + combo multiplier: +0.5x per 5 kills without being hit, max 5x.
import { CONFIG } from './config.js';
import { spawnPopup } from './fx.js';

const SC = CONFIG.score;

export class ScoreManager {
  constructor(game) {
    this.game = game;
    this.reset();
  }

  reset() {
    this.score = 0;
    this.multiplier = 1;
    this.killsSinceHit = 0;
  }

  addKill(x, y) {
    const gain = Math.round(SC.perKill * this.multiplier);
    this.score += gain;
    spawnPopup(this.game, x, y, `+${gain}`);
    this.killsSinceHit++;
    if (this.killsSinceHit % SC.comboEvery === 0) {
      this.multiplier = Math.min(SC.comboMax, this.multiplier + SC.comboStep);
    }
  }

  addBossKill() {
    this.score += SC.bossKill;
    spawnPopup(this.game, this.game.boss ? this.game.boss.x : 360, 300, `+${SC.bossKill}`);
  }

  onPlayerHit() {
    this.multiplier = 1;
    this.killsSinceHit = 0;
  }
}
