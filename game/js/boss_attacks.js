// Boss attack registry. Each entry:
//   start(boss, game)        -> data; pushes telegraph(s) unless enraged
//   active(boss, game, atk, dt) -> true when the attack is finished
// Telegraph durations come from config (x0.7 while enraged).
import { CONFIG } from './config.js';
import { angleTo, lerp, Timer } from './utils.js';
import { Telegraph } from './telegraph.js';
import { Bullet } from './projectiles.js';

const B = CONFIG.boss;
const A = B.attacks;
const DEG = Math.PI / 180;

export function bossBullet(game, x, y, angle, speed, radius) {
  speed *= game.bossBulletMul || 1;
  const c = CONFIG.enemies.bossBullet;
  game.enemyBullets.push(new Bullet({
    x, y,
    vx: Math.cos(angle) * speed,
    vy: Math.sin(angle) * speed,
    radius,
    life: c.life,
    color: c.color,
    glow: c.glow,
  }));
}

export function telegraphTime(boss, id) {
  const t = A[id].telegraph;
  return boss.enraged ? t * B.enrage.telegraphScale : t;
}

export const ATTACKS = {
  // --------------------------------------------- AIMED BARRAGE (phase 1)
  // Telegraph: boss red flash + faint aim line boss->player (0.4s).
  // Active: 3 aimed shots, 0.2s apart.
  aimed: {
    start(boss, game) {
      const angle = angleTo(boss.x, boss.y, game.player.x, game.player.y);
      const data = { angle, shotsLeft: A.aimed.shots, shotT: new Timer(0) };
      {
        game.telegraphs.push(new Telegraph('aimLine', telegraphTime(boss, 'aimed'), {
          x: boss.x, y: boss.y, angle,
          alphaFrom: 0.2, alphaTo: 0.7, lineWidth: 3,
        }));
      }
      data.flash = true; // boss body red-flash during telegraph
      return data;
    },
    active(boss, game, atk, dt) {
      const d = atk.data;
      if (d.shotsLeft <= 0) return true;
      d.shotT.update(dt);
      if (d.shotT.done) {
        const p = game.player;
        const ang = angleTo(boss.x, boss.y, p.x, p.y);
        bossBullet(game, boss.x, boss.y + boss.radius * 0.4, ang,
          A.aimed.bulletSpeed, A.aimed.bulletRadius);
        d.shotsLeft--;
        d.shotT.reset(A.aimed.shotInterval);
      }
      return false;
    },
  },

  // ---------------------------------------------- FAN SPREAD (phase 1)
  // Telegraph: 3 red lines fanning 30 deg (locked). Active: 3 bullets.
  fan: {
    start(boss, game) {
      const base = angleTo(boss.x, boss.y, game.player.x, game.player.y);
      const spread = (A.fan.spreadDeg * Math.PI) / 180;
      const angles = [-1, 0, 1].map((k) => base + k * spread);
      {
        game.telegraphs.push(new Telegraph('fanLines', telegraphTime(boss, 'fan'), {
          x: boss.x, y: boss.y, angles, alphaFrom: 0.2, alphaTo: 0.8,
        }));
      }
      return { angles };
    },
    active(boss, game, atk) {
      for (const ang of atk.data.angles) {
        bossBullet(game, boss.x, boss.y + boss.radius * 0.4, ang,
          A.fan.bulletSpeed, A.fan.bulletRadius);
      }
      return true;
    },
  },

  // --------------------------------------------- SPIRAL BULLETS (phase 2)
  // Telegraph: blue glow + orbiting motes. Active: 24 bullets over 4s,
  // each rotated so the stream spirals a full 360 deg.
  spiral: {
    start(boss, game) {
      const data = {
        emitted: 0,
        emitT: new Timer(0),
        dur: null,
        angle0: (boss.time * 1.7) % (Math.PI * 2),
      };
      {
        game.telegraphs.push(new Telegraph('spiralGlow', telegraphTime(boss, 'spiral'), {
          x: boss.x, y: boss.y, r: boss.radius * 1.3,
        }));
      }
      return data;
    },
    active(boss, game, atk, dt) {
      const c = A.spiral;
      const d = atk.data;
      if (!d.dur) d.dur = new Timer(c.duration);
      d.dur.update(dt);
      d.emitT.update(dt);
      const interval = c.duration / c.bullets;
      while (d.emitted < c.bullets && d.emitT.done) {
        const ang = d.angle0 + (d.emitted * c.totalTurnDeg / c.bullets) * DEG;
        bossBullet(game, boss.x, boss.y, ang, c.bulletSpeed, c.bulletRadius);
        d.emitted++;
        d.emitT.reset(interval);
      }
      return d.emitted >= c.bullets && d.dur.done;
    },
  },

  // ----------------------------------------------- RING BURST (phase 2)
  // Telegraph: expanding bright ring. Active: 16 bullets, full circle.
  ring: {
    start(boss, game) {
      {
        game.telegraphs.push(new Telegraph('ringGlow', telegraphTime(boss, 'ring'), {
          x: boss.x, y: boss.y, r0: 60, r1: boss.radius * 1.5,
        }));
      }
      return { offset: (boss.time * 2.3) % (Math.PI * 2) };
    },
    active(boss, game, atk) {
      const c = A.ring;
      for (let i = 0; i < c.bullets; i++) {
        const ang = atk.data.offset + (i * Math.PI * 2) / c.bullets;
        bossBullet(game, boss.x, boss.y, ang, c.bulletSpeed, c.bulletRadius);
      }
      return true;
    },
  },

  // --------------------------------------------- LASER SWEEP (phase 2)
  // Telegraph: thin red lane at fromX (1.2s). Active: beam sweeps to toX
  // over 0.5s; standing in the lane during the sweep costs a life.
  laserSweep: {
    start(boss, game) {
      const data = { t: null, beamX: A.laserSweep.fromX, hitDone: false };
      {
        game.telegraphs.push(new Telegraph('sweepLine', telegraphTime(boss, 'laserSweep'), {
          x: boss.x, y: boss.y, fromX: A.laserSweep.fromX, toX: A.laserSweep.toX,
        }));
      }
      return data;
    },
    active(boss, game, atk, dt) {
      const c = A.laserSweep;
      const d = atk.data;
      if (!d.t) {
        d.t = new Timer(c.fireTime);
        game.telegraphs.push(new Telegraph('beamV', c.fireTime, {
          halfWidth: c.halfWidth, ref: d,
        }));
      }
      d.t.update(dt);
      d.beamX = lerp(c.fromX, c.toX, d.t.progress);
      const p = game.player;
      if (!d.hitDone && p.alive && Math.abs(p.x - d.beamX) <= c.halfWidth + p.hitboxRadius) {
        d.hitDone = p.hit();
      }
      return d.t.done;
    },
  },

  // ------------------------------------------- HOMING MISSILES (phase 3)
  // Telegraph: red glow pods. Active: 2 missiles, trail, home for 2s.
  homing: {
    start(boss, game) {
      const data = { launched: 0, launchT: new Timer(0) };
      {
        game.telegraphs.push(new Telegraph('homingPods', telegraphTime(boss, 'homing'), {
          x: boss.x, y: boss.y, r: boss.radius,
        }));
      }
      return data;
    },
    active(boss, game, atk, dt) {
      const c = A.homing;
      const d = atk.data;
      d.launchT.update(dt);
      while (d.launched < c.count && d.launchT.done) {
        const s = d.launched === 0 ? -1 : 1;
        const bc = CONFIG.enemies.bossBullet;
        game.enemyBullets.push(new Bullet({
          x: boss.x + s * boss.radius * 0.95,
          y: boss.y + boss.radius * 0.35,
          vx: s * 60 * (game.bossBulletMul || 1),
          vy: c.speed * (game.bossBulletMul || 1),
          radius: c.bulletRadius,
          life: bc.life,
          color: bc.glow,
          glow: bc.color,
          trail: true,
          homing: { turnRate: c.turnRate, duration: c.homeTime },
          target: () => (game.player.alive ? game.player : null),
        }));
        d.launched++;
        d.launchT.reset(c.launchInterval);
      }
      return d.launched >= c.count;
    },
  },

  // ----------------------------------------- BULLET HELL RING (phase 3)
  // Telegraph: purple glow + ring flash. Active: 3 rings x 24 bullets.
  hellRing: {
    start(boss, game) {
      const data = { wavesDone: 0, waveT: new Timer(0) };
      {
        game.telegraphs.push(new Telegraph('hellGlow', telegraphTime(boss, 'hellRing'), {
          x: boss.x, y: boss.y, r: boss.radius * 1.3,
        }));
      }
      return data;
    },
    active(boss, game, atk, dt) {
      const c = A.hellRing;
      const d = atk.data;
      d.waveT.update(dt);
      while (d.wavesDone < c.waves && d.waveT.done) {
        const off = d.wavesDone * (c.ringOffsetDeg * DEG);
        for (let i = 0; i < c.bullets; i++) {
          const ang = off + (i * Math.PI * 2) / c.bullets;
          bossBullet(game, boss.x, boss.y, ang, c.bulletSpeed, c.bulletRadius);
        }
        d.wavesDone++;
        d.waveT.reset(c.waveInterval);
      }
      return d.wavesDone >= c.waves;
    },
  },

  // --------------------------------------------- LASER CROSS (phase 3)
  // Telegraph: X of two red lines (1.5s). Active: both beams fire 0.5s.
  laserCross: {
    start(boss, game) {
      const angles = A.laserCross.anglesDeg.map((a) => (a * Math.PI) / 180);
      const data = { angles, t: null, hitDone: false };
      {
        game.telegraphs.push(new Telegraph('crossLines', telegraphTime(boss, 'laserCross'), {
          x: boss.x, y: boss.y, angles, alphaFrom: 0.2, alphaTo: 0.9, lineWidth: 4,
        }));
      }
      return data;
    },
    active(boss, game, atk, dt) {
      const c = A.laserCross;
      const d = atk.data;
      if (!d.t) {
        d.t = new Timer(c.fireTime);
        for (const ang of d.angles) {
          game.telegraphs.push(new Telegraph('beamAng', c.fireTime, {
            x: boss.x, y: boss.y, angle: ang, halfWidth: c.halfWidth,
          }));
        }
      }
      d.t.update(dt);
      const p = game.player;
      if (!d.hitDone && p.alive) {
        for (const ang of d.angles) {
          const dx = p.x - boss.x;
          const dy = p.y - boss.y;
          const cross = Math.abs(dx * Math.sin(ang) - dy * Math.cos(ang));
          if (cross <= c.halfWidth + p.hitboxRadius) {
            d.hitDone = p.hit();
            break;
          }
        }
      }
      return d.t.done;
    },
  },
};
