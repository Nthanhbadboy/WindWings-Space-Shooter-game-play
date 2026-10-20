/**
 * Tàu 3 — "VERTEBRA" (XƯƠNG SỐNG): chiến đấu cơ với bộ giáp sinh cơ TRÊN THÂN.
 *
 * Cùng khung chiến đấu cơ chuẩn (`fighter.js`) nhưng đổi "chất":
 *   - giáp lưng chia thành 6 ĐỐT SỐNG; gồng lên thì các đốt TÁCH RA và 4 cặp SƯỜN
 *     nhấc lên, lộ cột năng lượng hổ phách chạy dọc thân;
 *   - nòng súng nằm TRONG thân, trượt thò ra khỏi mũi (súng trong thân hợp với tàu này);
 *   - màu: thép lạnh + hổ phách, ánh bù nhau.
 *
 * Vẫn đủ: mũi nhọn, buồng lái, cánh xuôi, cánh mũi, vây đuôi, 2 ống xả.
 */

import { clamp01, drawFlame, flameFrame, glowDot, smooth } from '../fx.js';
import { glowLine, rivets, techPlate } from '../mat.js';
import {
  F, drawCanard, drawCanopy, drawEngines, drawFuselage, drawTail, drawWing, mirrorPts,
} from './fighter.js';

const BASE = 512;
const C = BASE / 2;

const AMBER = '255, 186, 96';
const BONE = '#c9d3d6';

const SPINE_X = 256;
const BARREL_Y = 132;
const BARREL_IDLE = 58;
const BARREL_GROW = 20;
const BARREL_KICK = 26;

const stepped = (v) => {
  const k = clamp01(v);
  const q = Math.round(k * 3) / 3;
  return q * 0.6 + k * 0.4;
};

function ribOpen(ph) {
  let v = 0;
  if (ph.stage === 'windup') v = smooth(ph.k * 1.05);
  else if (ph.stage === 'fire') v = 1 - 0.26 * clamp01(ph.k * 1.5);
  else if (ph.stage === 'recover') v = 0.66 * (1 - smooth(ph.k * 1.2));
  return stepped(v);
}

function barrelLen(ph) {
  return BARREL_IDLE + BARREL_GROW * ribOpen(ph) - BARREL_KICK * clamp01(ph.recoil);
}

// ------------------------------------------------------------------ nòng trong thân

function drawBarrel(ctx, open, ph) {
  const x = SPINE_X;
  const y0 = BARREL_Y;
  const L = barrelLen(ph);
  const y1 = y0 - L;
  const hw = 6.4;

  techPlate(ctx, [[x - hw, y1], [x + hw, y1], [x + hw, y0], [x - hw, y0]], {
    ramp: ['#07090b', '#101418', '#1d2429', '#333f47', '#5a6d77', '#a9bcc4'],
    light: [x - hw, y1, x + hw, y0],
    edge: 2.8,
    rim: '205, 230, 240',
  });
  for (const k of [0.34, 0.6]) {
    const yy = y1 + L * k;
    ctx.strokeStyle = 'rgba(5, 8, 10, 0.85)';
    ctx.lineWidth = 2.2;
    ctx.beginPath();
    ctx.moveTo(x - hw, yy);
    ctx.lineTo(x + hw, yy);
    ctx.stroke();
  }
  glowLine(ctx, [[x, y1 + 14], [x, y1 + L - 10]], AMBER, { w: 1.2, a: 0.3 + 0.5 * open });

  // khoá đầu nòng
  techPlate(ctx, [
    [x - hw - 3.6, y1], [x + hw + 3.6, y1],
    [x + hw + 3.6, y1 + 10], [x - hw - 3.6, y1 + 10],
  ], {
    ramp: ['#06080a', '#0e1316', '#242c31', '#4a5a63', '#8ba0aa', '#dceaf0'],
    light: [x - hw, y1, x + hw, y1 + 10],
    edge: 2.6,
    rim: '215, 240, 250',
  });
  ctx.beginPath();
  ctx.ellipse(x, y1 + 2, hw - 1, 2.5, 0, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(3, 5, 7, 0.97)';
  ctx.fill();
  ctx.beginPath();
  ctx.ellipse(x, y1 + 2, (hw - 3) * (0.35 + 0.65 * open), 1.2, 0, 0, Math.PI * 2);
  ctx.fillStyle = `rgba(255, 250, 235, ${0.3 + 0.65 * open})`;
  ctx.fill();
  glowDot(ctx, x, y1 + 2, 4 + 9 * open,
    `rgba(255, 250, 235, ${0.14 + 0.4 * open})`,
    `rgba(${AMBER}, ${0.08 + 0.22 * open})`,
    'rgba(190, 110, 20, 0)');
}

// ------------------------------------------------------------------ cột sống + sườn

function drawSpine(ctx, t, open) {
  const x = SPINE_X;
  const yTop = 156;
  const yBot = 384;
  const pulse = 0.5 + 0.5 * Math.sin(t * 3.6);

  // lòng cột
  const w = 5 + 7 * open;
  ctx.beginPath();
  if (ctx.roundRect) ctx.roundRect(x - w, yTop, w * 2, yBot - yTop, w);
  else ctx.rect(x - w, yTop, w * 2, yBot - yTop);
  ctx.fillStyle = 'rgba(4, 6, 7, 0.95)';
  ctx.fill();

  // năng lượng trong cột
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  const g = ctx.createLinearGradient(0, yTop, 0, yBot);
  g.addColorStop(0, `rgba(255, 244, 220, ${0.28 + 0.5 * open})`);
  g.addColorStop(0.45, `rgba(${AMBER}, ${0.16 + 0.4 * open})`);
  g.addColorStop(1, `rgba(190, 96, 20, ${0.07 + 0.18 * open})`);
  ctx.fillStyle = g;
  ctx.beginPath();
  if (ctx.roundRect) ctx.roundRect(x - w * 0.5, yTop + 4, w, yBot - yTop - 8, w * 0.5);
  else ctx.rect(x - w * 0.5, yTop + 4, w, yBot - yTop - 8);
  ctx.fill();

  // xung chạy dọc khi mở
  if (open > 0.2) {
    const k = (t * 1.6) % 1;
    const yy = yBot + (yTop - yBot) * k;
    const sg = ctx.createRadialGradient(x, yy, 0, x, yy, 22);
    sg.addColorStop(0, `rgba(255, 250, 235, ${0.5 * open})`);
    sg.addColorStop(1, 'rgba(255, 190, 90, 0)');
    ctx.fillStyle = sg;
    ctx.beginPath();
    ctx.arc(x, yy, 22, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();

  // 6 đốt sống — tách ra theo độ mở
  for (let i = 0; i < 6; i++) {
    const yy = (yTop + 18 + i * 38);
    const spread = 1 + open * 0.22;
    const ww = 12 * spread;
    ctx.beginPath();
    ctx.moveTo(x - ww, yy);
    ctx.lineTo(x - ww * 0.55, yy - 7);
    ctx.lineTo(x + ww * 0.55, yy - 7);
    ctx.lineTo(x + ww, yy);
    ctx.lineTo(x + ww * 0.55, yy + 7);
    ctx.lineTo(x - ww * 0.55, yy + 7);
    ctx.closePath();
    const dg = ctx.createLinearGradient(x - ww, yy - 7, x + ww, yy + 7);
    dg.addColorStop(0, 'rgba(20, 30, 36, 0.95)');
    dg.addColorStop(0.5, 'rgba(56, 76, 86, 0.95)');
    dg.addColorStop(1, 'rgba(10, 16, 20, 0.95)');
    ctx.fillStyle = dg;
    ctx.fill();
    ctx.strokeStyle = `rgba(200, 226, 240, ${0.5 + 0.3 * open})`;
    ctx.lineWidth = 1.8;
    ctx.stroke();
    // gai giữa phát sáng
    ctx.beginPath();
    ctx.moveTo(x, yy - 7);
    ctx.lineTo(x, yy + 7);
    ctx.strokeStyle = `rgba(255, 240, 210, ${0.25 + 0.5 * open})`;
    ctx.lineWidth = 1.4;
    ctx.stroke();
    // khớp nối đốt dưới
    if (i < 5) {
      ctx.beginPath();
      ctx.moveTo(x, yy + 8);
      ctx.lineTo(x, yy + 38 - 9);
      ctx.strokeStyle = 'rgba(150, 172, 184, 0.45)';
      ctx.lineWidth = 1.6;
      ctx.stroke();
    }
  }

  glowDot(ctx, x, (yTop + yBot) / 2, 26,
    `rgba(255, 248, 232, ${0.04 + 0.08 * open * (0.6 + 0.4 * pulse)})`,
    `rgba(${AMBER}, ${0.03 + 0.06 * open})`,
    'rgba(190, 110, 20, 0)');
}

function drawRibs(ctx, sign, open) {
  // sườn nằm TRONG silhouette thân, xoay quanh khớp sát cột sống
  const hinge = [SPINE_X + sign * 12, 300];
  ctx.save();
  ctx.translate(hinge[0], hinge[1]);
  ctx.rotate(open * 0.2 * sign);
  ctx.translate(-hinge[0], -hinge[1]);

  const pairs = [
    { y: 196, len: 34, thick: 5.5, drop: 10 },
    { y: 240, len: 40, thick: 6, drop: 12 },
    { y: 288, len: 36, thick: 5.5, drop: 11 },
    { y: 336, len: 28, thick: 5, drop: 9 },
  ];
  for (const { y, len, thick, drop } of pairs) {
    const x0 = SPINE_X + sign * 14;
    const x1 = SPINE_X + sign * (14 + len);
    ctx.beginPath();
    ctx.moveTo(x0, y);
    ctx.quadraticCurveTo(SPINE_X + sign * (14 + len * 0.62), y + drop * 1.4, x1, y + drop);
    ctx.lineCap = 'round';
    ctx.strokeStyle = 'rgba(3, 6, 8, 0.95)';
    ctx.lineWidth = thick + 4;
    ctx.stroke();
    ctx.strokeStyle = BONE;
    ctx.lineWidth = thick;
    ctx.stroke();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.22)';
    ctx.lineWidth = thick * 0.26;
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(x1, y + drop, thick * 0.5, 0, Math.PI * 2);
    ctx.fillStyle = '#aeb9bd';
    ctx.fill();
  }
  // đường sáng lộ ra dưới sườn
  if (open > 0.05) {
    for (const [y, L] of [[196, 30], [240, 36], [288, 32], [336, 24]]) {
      glowLine(ctx, [[SPINE_X + sign * 16, y + 6], [SPINE_X + sign * (16 + L), y + 6]], AMBER,
        { w: 2.4, a: 0.1 + 0.3 * open });
    }
  }
  ctx.restore();
}

// ------------------------------------------------------------------ module

export const vertebra = {
  id: 'vertebra',
  label: 'XƯƠNG SỐNG',
  usesArt: false,
  laserTint: [255, 205, 120],

  muzzles(s, t, ph) {
    const L = barrelLen(ph);
    return [{ x: (SPINE_X - C) * s, y: (BARREL_Y - L - C) * s, angle: 0, scale: 1.35 }];
  },

  draw(ctx, { s, t, ph }) {
    const open = ribOpen(ph);

    ctx.save();
    ctx.translate(-C * s, -C * s);
    ctx.scale(s, s);

    drawEngines(ctx, { glow: AMBER });
    for (let i = 0; i < F.engines.length; i++) {
      const [ex, ey] = F.engines[i];
      drawFlame(ctx, ex, ey + 12, 14, 82, flameFrame(t, i), 0.8 + 0.35 * open, {
        glow: 'rgba(255, 210, 140, 0.3)',
        glowMid: 'rgba(240, 150, 40, 0.12)',
        glowOut: 'rgba(190, 90, 10, 0)',
        outer: 'rgba(250, 160, 50, 0.82)',
        mid: 'rgba(255, 226, 170, 0.95)',
        core: 'rgba(255, 255, 255, 0.95)',
        spark: 'rgba(255, 200, 120, 0.62)',
      });
    }

    for (const sign of [-1, 1]) drawWing(ctx, sign, { glow: AMBER, open, rotate: open * 0.05 * sign });
    for (const sign of [-1, 1]) drawCanard(ctx, sign, { glow: AMBER });
    for (const sign of [-1, 1]) drawTail(ctx, sign, { glow: AMBER });

    drawFuselage(ctx, {
      glow: AMBER,
      open,
      spineGlow: '255, 236, 200',
      rim: '200, 226, 240',
    });

    // sinh cơ trên thân
    drawRibs(ctx, -1, open);
    drawRibs(ctx, 1, open);
    drawSpine(ctx, t, open);
    drawBarrel(ctx, open, ph);

    // tấm giáp hông (che gốc sườn khi khép)
    for (const sign of [-1, 1]) {
      const pts = sign > 0
        ? [[266, 210], [300, 250], [298, 344], [266, 372]]
        : mirrorPts([[266, 210], [300, 250], [298, 344], [266, 372]]);
      techPlate(ctx, pts, {
        ramp: ['#04080a', '#080f13', '#101b20', '#1a2b33', '#233a44'],
        light: sign > 0 ? [268, 210, 300, 372] : [244, 210, 212, 372],
        edge: 4.5,
        rim: '150, 190, 210',
      });
      glowLine(ctx, sign > 0 ? [[272, 240], [296, 286]] : [[240, 240], [216, 286]], AMBER,
        { w: 1.2, a: 0.12 + 0.35 * open });
      rivets(ctx, sign > 0 ? [[286, 320], [278, 356]] : [[226, 320], [234, 356]],
        'rgba(175, 200, 215, 0.42)', 1.8);
    }

    // buồng lái vẽ sau cùng, nằm trên sống lưng
    drawCanopy(ctx, { tint: '150, 210, 240' });

    ctx.restore();
  },

  skeleton(ctx, s, t, ph) {
    ctx.strokeStyle = 'rgba(120, 230, 255, 0.8)';
    ctx.lineWidth = 1;
    for (const m of this.muzzles(s, t, ph)) {
      ctx.beginPath();
      ctx.arc(m.x, m.y, 5, 0, Math.PI * 2);
      ctx.stroke();
    }
    for (const [ex, ey] of F.engines) {
      ctx.strokeStyle = 'rgba(255, 190, 90, 0.85)';
      ctx.beginPath();
      ctx.arc((ex - C) * s, (ey - C) * s, 6, 0, Math.PI * 2);
      ctx.stroke();
    }
  },
};
