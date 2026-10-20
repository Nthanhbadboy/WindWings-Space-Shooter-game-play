// Scrolling starfield background (WindWings-style space), drawn with code.
import { CONFIG } from './config.js';
import { randRange } from './utils.js';

const S = CONFIG.screen;

export class StarField {
  constructor() {
    this.layers = CONFIG.stars.layers.map((cfg) => ({
      cfg,
      stars: Array.from({ length: cfg.count }, () => this._makeStar(true)),
    }));
  }

  _makeStar(anywhere) {
    return {
      x: randRange(0, S.width),
      y: anywhere ? randRange(0, S.height) : -4,
    };
  }

  update(dt) {
    for (const layer of this.layers) {
      for (let i = 0; i < layer.stars.length; i++) {
        const s = layer.stars[i];
        s.y += layer.cfg.speed * dt;
        if (s.y > S.height + 4) layer.stars[i] = this._makeStar(false);
      }
    }
  }

  draw(ctx) {
    ctx.fillStyle = S.background;
    ctx.fillRect(0, 0, S.width, S.height);
    for (const layer of this.layers) {
      ctx.globalAlpha = layer.cfg.alpha;
      ctx.fillStyle = '#ffffff';
      for (const s of layer.stars) {
        ctx.fillRect(s.x, s.y, layer.cfg.size, layer.cfg.size);
      }
    }
    ctx.globalAlpha = 1;
  }
}
