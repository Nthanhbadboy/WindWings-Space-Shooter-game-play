// Wave timeline: deterministic spawn script (no randomness), 2s rest
// between waves; when the script ends and the screen is clear -> boss.
import { CONFIG } from './config.js';
import { spawnEnemy } from './enemies.js';

export class WaveManager {
  constructor(game, definitions) {
    this.game = game;
    this.definitions = definitions || CONFIG.waves.definitions;
    this.reset();
  }

  reset() {
    this.time = 0;
    this.bossRequested = false;
    this.events = [];
    let cursor = 0;
    for (const def of this.definitions) {
      for (const s of def.spawns) {
        this.events.push({ t: cursor + s.t, spawn: s, fired: false });
      }
      cursor += def.duration + CONFIG.waves.restBetween;
    }
    this.endTime = cursor;
  }

  update(dt) {
    this.time += dt;
    for (const ev of this.events) {
      if (!ev.fired && this.time >= ev.t) {
        ev.fired = true;
        spawnEnemy(this.game, ev.spawn.type, ev.spawn);
      }
    }
    if (
      !this.bossRequested &&
      this.time >= this.endTime &&
      this.game.enemies.length === 0
    ) {
      this.bossRequested = true;
      this.game.onWavesDone();
    }
  }
}
