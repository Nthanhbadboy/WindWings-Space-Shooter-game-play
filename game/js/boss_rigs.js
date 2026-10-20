// Boss rigs: 3 procedurally ANIMATED bosses (not static sprites).
// Each rig reads boss.anim (state/t/kick/blink), phase and enrage to drive
// its own motion: tentacle wave, spinning blades, articulated legs...
import { CONFIG } from './config.js';

const B = CONFIG.boss;

const PALETTES = {
  tyrant: ['#9b5cff', '#ff3c5a', '#b3123a'],
  dispatcher: ['#ff5a3c', '#c81e3c', '#8b0f2a'],
  omen: ['#b46cff', '#7a1fa2', '#5c0a86'],
};

function phaseColor(boss) {
  const pal = PALETTES[boss.type] || PALETTES.tyrant;
  return pal[Math.min(2, boss.phase - 1)];
}

/** Shared post-fx: charge tint + white hurt flash over the hull path. */
function overlays(boss, ctx, hullPath) {
  if (boss.attack && boss.attack.stage === 'telegraph' && boss.attack.data.flash) {
    ctx.globalAlpha = 0.35 + 0.3 * Math.sin(boss.time * 20);
    ctx.fillStyle = '#ff2b2b';
    hullPath();
    ctx.fill();
  }
  if (boss.hurtFlashT > 0) {
    ctx.globalAlpha = boss.hurtFlashT / B.hurtFlash;
    ctx.fillStyle = '#ffffff';
    hullPath();
    ctx.fill();
  }
  ctx.globalAlpha = 1;
}

function enrageAura(boss, ctx, r) {
  if (!boss.enraged) return;
  ctx.save();
  ctx.globalAlpha = 0.25 + 0.2 * Math.sin(boss.time * 14);
  ctx.strokeStyle = B.colors.enragePulse;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.arc(0, 0, r * 1.5 + Math.sin(boss.time * 9) * 8, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();
}

// ---------------------------------------------------------- RIG: TYRANT
// Jellyfish dome + waving tentacles; breathes, blinks, curls when charging.
function drawTyrant(boss, ctx, r) {
  const a = boss.anim;
  const color = phaseColor(boss);
  const breathe = 1 + Math.sin(boss.time * 2.2) * 0.03;
  const curl = bossCharge(boss);
  ctx.scale(breathe, breathe);
  ctx.translate(0, -10 * a.kick); // recoil kick
  enrageAura(boss, ctx, r);

  // tentacles (more of them, and longer, in later phases)
  const legs = 4 + boss.phase;
  ctx.strokeStyle = color;
  ctx.lineWidth = 10;
  ctx.lineCap = 'round';
  for (const s of [-1, 1]) {
    for (let i = 0; i < legs; i++) {
      const wig = Math.sin(boss.time * 3 + i * 0.9) * 8 * (1 - curl * 0.6);
      const reach = 1.35 + i * 0.1 + boss.phase * 0.08;
      ctx.beginPath();
      ctx.moveTo(s * r * 0.5, -r * 0.2 + i * (r * 1.1 / legs));
      ctx.quadraticCurveTo(
        s * r * (1.1 + i * 0.1), -r * 0.5 + i * r * 0.26 + wig,
        s * r * reach * (1 - curl * 0.25), r * 0.1 + i * r * 0.24 + wig
      );
      ctx.stroke();
    }
  }

  // dome hull
  const hull = () => {
    ctx.beginPath();
    ctx.ellipse(0, 0, r * 0.78, r * 0.92, 0, 0, Math.PI * 2);
  };
  ctx.fillStyle = color;
  hull();
  ctx.fill();
  ctx.strokeStyle = B.colors.outline;
  ctx.lineWidth = 5;
  hull();
  ctx.stroke();

  // brow
  ctx.fillStyle = B.colors.outline;
  ctx.beginPath();
  ctx.ellipse(0, -r * 0.45, r * 0.6, r * 0.34, 0, Math.PI, 0);
  ctx.fill();

  // eyes (blink) + core (exposed in phase 3)
  const eyeH = a.blink > 0 ? 0.2 : 1;
  ctx.fillStyle = B.colors.core;
  for (const s of [-1, 1]) {
    ctx.save();
    ctx.translate(s * r * 0.3, -r * 0.12);
    ctx.scale(1, eyeH);
    ctx.beginPath();
    ctx.arc(0, 0, r * 0.14, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
  const coreR = r * (boss.phase >= 3 ? 0.3 : 0.2) * (1 + 0.15 * Math.sin(boss.time * 5));
  ctx.globalAlpha = boss.phase >= 3 ? 1 : 0.85;
  ctx.beginPath();
  ctx.arc(0, r * 0.3, coreR, 0, Math.PI * 2);
  ctx.fill();
  ctx.globalAlpha = 1;
  if (boss.phase >= 3) crackLines(ctx, r, boss.time);
  overlays(boss, ctx, hull);
}

// ------------------------------------------------------ RIG: DISPATCHER
// Angular warship with twin spinning blade discs; pods open when charging.
function drawDispatcher(boss, ctx, r) {
  const a = boss.anim;
  const color = phaseColor(boss);
  const cp = bossCharge(boss);
  const wing = 1 + (boss.phase - 1) * 0.12;
  ctx.translate(0, -12 * a.kick);
  ctx.rotate(Math.sin(boss.time * 0.8) * 0.03);
  enrageAura(boss, ctx, r);

  // wings
  ctx.fillStyle = color;
  for (const s of [-1, 1]) {
    ctx.save();
    ctx.scale(s * wing, 1);
    ctx.beginPath();
    ctx.moveTo(r * 0.3, -r * 0.2);
    ctx.lineTo(r * 1.35, r * 0.05);
    ctx.lineTo(r * 1.05, r * 0.5);
    ctx.lineTo(r * 0.3, r * 0.45);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  // spinning blade discs (faster each phase)
  const spin = boss.time * (2 + boss.phase * 2);
  for (const s of [-1, 1]) {
    ctx.save();
    ctx.translate(s * r * 0.95, r * 0.1);
    ctx.rotate(spin * s);
    ctx.fillStyle = B.colors.outline;
    for (let i = 0; i < 4; i++) {
      ctx.rotate(Math.PI / 2);
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(r * 0.34, r * 0.08);
      ctx.lineTo(r * 0.3, -r * 0.08);
      ctx.closePath();
      ctx.fill();
    }
    ctx.restore();
  }

  // hull
  const hull = () => {
    ctx.beginPath();
    ctx.moveTo(0, -r * 0.95);
    ctx.lineTo(r * 0.55, -r * 0.35);
    ctx.lineTo(r * 0.5, r * 0.6);
    ctx.lineTo(0, r * 0.9);
    ctx.lineTo(-r * 0.5, r * 0.6);
    ctx.lineTo(-r * 0.55, -r * 0.35);
    ctx.closePath();
  };
  ctx.fillStyle = color;
  hull();
  ctx.fill();
  ctx.strokeStyle = B.colors.outline;
  ctx.lineWidth = 5;
  hull();
  ctx.stroke();

  // charge pods slide open
  const open = cp * r * 0.22;
  ctx.fillStyle = B.colors.outline;
  for (const s of [-1, 1]) {
    ctx.fillRect(s * (r * 0.28 + open) - r * 0.09, -r * 0.1, r * 0.18, r * 0.42);
  }
  // cockpit light blinks; phase 3 exposes burning core
  ctx.fillStyle = a.blink > 0 ? '#ffffff' : B.colors.core;
  ctx.beginPath();
  ctx.arc(0, -r * 0.35, r * 0.12, 0, Math.PI * 2);
  ctx.fill();
  if (boss.phase >= 3) {
    ctx.fillStyle = B.colors.core;
    ctx.globalAlpha = 0.75 + 0.25 * Math.sin(boss.time * 8);
    ctx.beginPath();
    ctx.arc(0, r * 0.25, r * 0.22, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;
    crackLines(ctx, r, boss.time);
  }
  overlays(boss, ctx, hull);
}

// ----------------------------------------------------------- RIG: OMEN
// Spider core: articulated legs, rotating halos, iris that narrows charging.
function drawOmen(boss, ctx, r) {
  const a = boss.anim;
  const color = phaseColor(boss);
  const cp = bossCharge(boss);
  ctx.translate(0, -8 * a.kick);
  enrageAura(boss, ctx, r);

  // halo rings (one more per phase, counter-rotating)
  for (let h = 0; h < boss.phase; h++) {
    ctx.save();
    ctx.rotate(boss.time * (h % 2 ? -1.4 : 1.1) * (1 + h * 0.3));
    ctx.strokeStyle = color;
    ctx.globalAlpha = 0.5;
    ctx.lineWidth = 4;
    ctx.setLineDash([r * 0.5, r * 0.35]);
    ctx.beginPath();
    ctx.arc(0, 0, r * (1.15 + h * 0.22), 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();
  }

  // articulated legs: 2 segments, waving
  const legs = 6;
  ctx.strokeStyle = color;
  ctx.lineWidth = 8;
  ctx.lineCap = 'round';
  for (let i = 0; i < legs; i++) {
    const base = (i / legs) * Math.PI * 2 + Math.PI / 6;
    const sway = Math.sin(boss.time * 2.6 + i * 1.3) * 0.16;
    const a1 = base + sway;
    const kx = Math.cos(a1) * r * 0.95;
    const ky = Math.sin(a1) * r * 0.95;
    const a2 = a1 + 0.7 + sway * 2;
    ctx.beginPath();
    ctx.moveTo(Math.cos(base) * r * 0.5, Math.sin(base) * r * 0.5);
    ctx.lineTo(kx, ky);
    ctx.lineTo(kx + Math.cos(a2) * r * 0.6, ky + Math.sin(a2) * r * 0.6);
    ctx.stroke();
  }

  // orb body
  const hull = () => {
    ctx.beginPath();
    ctx.arc(0, 0, r * 0.62, 0, Math.PI * 2);
  };
  ctx.fillStyle = color;
  hull();
  ctx.fill();
  ctx.strokeStyle = B.colors.outline;
  ctx.lineWidth = 5;
  hull();
  ctx.stroke();

  // iris: narrows while charging, blinks idle
  const iris = (a.blink > 0 ? 0.15 : 1) * (1 - cp * 0.55);
  ctx.fillStyle = B.colors.core;
  ctx.save();
  ctx.scale(1, Math.max(0.12, iris));
  ctx.beginPath();
  ctx.arc(0, 0, r * 0.3, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
  ctx.fillStyle = '#04050d';
  ctx.save();
  ctx.scale(1, Math.max(0.12, iris));
  ctx.beginPath();
  ctx.arc(0, 0, r * 0.12, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
  if (boss.phase >= 3) crackLines(ctx, r * 0.8, boss.time);
  overlays(boss, ctx, hull);
}

/** Jagged crack lines for phase 3 (armor breaking apart). */
function crackLines(ctx, r, time) {
  ctx.save();
  ctx.globalAlpha = 0.5 + 0.3 * Math.sin(time * 6);
  ctx.strokeStyle = '#ffd23e';
  ctx.lineWidth = 2.5;
  for (let i = 0; i < 5; i++) {
    const a = (i / 5) * Math.PI * 2 + 0.4;
    ctx.beginPath();
    ctx.moveTo(Math.cos(a) * r * 0.2, Math.sin(a) * r * 0.2);
    ctx.lineTo(Math.cos(a + 0.25) * r * 0.55, Math.sin(a + 0.25) * r * 0.55);
    ctx.lineTo(Math.cos(a + 0.1) * r * 0.9, Math.sin(a + 0.1) * r * 0.9);
    ctx.stroke();
  }
  ctx.restore();
}

function bossCharge(boss) {
  if (boss.attack && boss.attack.stage === 'telegraph') return boss.attack.timer.progress;
  return 0;
}

const RIGS = { tyrant: drawTyrant, dispatcher: drawDispatcher, omen: drawOmen };

export function drawBossRig(boss, ctx) {
  ctx.save();
  ctx.translate(boss.x, boss.y);
  const rig = RIGS[boss.type] || RIGS.tyrant;
  rig(boss, ctx, boss.radius);
  ctx.restore();
}
