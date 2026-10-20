/**
 * Tàu 2 — "VX-9 SINH CƠ": CHIẾN ĐẤU CƠ không gian, giáp lai sinh học.
 *
 * Dựng trên khung chiến đấu cơ chuẩn (`fighter.js`): mũi nhọn → buồng lái → thân thon →
 * cánh xuôi → cánh mũi → vây đuôi → 2 ống xả. Nhờ vậy dù thêm giáp sinh học, silhouette
 * vẫn đọc ra "máy bay chiến đấu", không phải con bọ hay viên đạn.
 *
 * Phần "sinh cơ" nằm TRÊN thân, không phá dáng: 2 tấm giáp vai trượt ra + xoay mở 3 nấc
 * để lộ lõi, gân sinh học toả ra, tua cảm biến ở đuôi.
 *
 * Súng: nòng nằm DƯỚI CÁNH (giấu), chỉ thò đầu nòng + 2 càng kẹp ra trước mép cánh.
 *
 * ⚠️ Mọi hàm vẽ dưới đây dùng HỆ THIẾT KẾ 512×512; `draw()` bọc một lần translate+scale.
 */

import { clamp01, drawFlame, flameFrame, glowDot, smooth } from '../fx.js';
import { BRONZE, STEEL, glowLine, rivets, techPlate } from '../mat.js';
import {
  F, drawCanard, drawCanopy, drawEngines, drawFuselage, drawTail, drawWing, mirrorPts,
} from './fighter.js';

const BASE = 512;
const C = BASE / 2;

const CYAN = '96, 240, 255';
const AMBER = '255, 176, 92';

const CORE = [256, 300];

// nòng dưới cánh
const BARREL_X = [340, 172];
const BARREL_Y = 330;
const BARREL_IDLE = 146;
const BARREL_GROW = 20;
const BARREL_KICK = 42;

const stepped = (v) => {
  const k = clamp01(v);
  const q = Math.round(k * 3) / 3;
  return q * 0.62 + k * 0.38;
};

function armorOpen(ph) {
  let v = 0;
  if (ph.stage === 'windup') v = smooth(ph.k * 1.05);
  else if (ph.stage === 'fire') v = 1 - 0.3 * clamp01(ph.k * 1.4);
  else if (ph.stage === 'recover') v = 0.7 * (1 - smooth(ph.k * 1.25));
  return stepped(v);
}

function barrelLen(open, ph) {
  return BARREL_IDLE + BARREL_GROW * open - BARREL_KICK * clamp01(ph.recoil);
}

// ------------------------------------------------------------------ nòng dưới cánh

function drawUnderBarrel(ctx, x, open, ph) {
  const y0 = BARREL_Y;
  const L = barrelLen(open, ph);
  const y1 = y0 - L;
  const hw = 6.5;

  techPlate(ctx, [[x - hw, y1], [x + hw, y1], [x + hw, y0], [x - hw, y0]], {
    ramp: ['#02060a', '#081018', '#16232e', '#2f4457', '#5f7f97', '#b9d4e6'],
    light: [x - hw, y1, x + hw, y0],
    edge: 2.8,
    rim: '195, 225, 248',
  });

  for (const k of [0.32, 0.58]) {
    const yy = y1 + L * k;
    ctx.strokeStyle = 'rgba(2, 6, 9, 0.85)';
    ctx.lineWidth = 2.4;
    ctx.beginPath();
    ctx.moveTo(x - hw, yy);
    ctx.lineTo(x + hw, yy);
    ctx.stroke();
    ctx.strokeStyle = 'rgba(200, 232, 255, 0.2)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x - hw, yy + 1.5);
    ctx.lineTo(x + hw, yy + 1.5);
    ctx.stroke();
  }

  glowLine(ctx, [[x + hw * 0.5, y1 + 14], [x + hw * 0.5, y1 + L - 10]], CYAN,
    { w: 1.1, a: 0.22 + 0.45 * open });

  // khoá đầu nòng
  techPlate(ctx, [
    [x - hw - 3.5, y1], [x + hw + 3.5, y1],
    [x + hw + 3.5, y1 + 10], [x - hw - 3.5, y1 + 10],
  ], {
    ramp: ['#03070b', '#0b141c', '#20313f', '#44606f', '#87a6bb', '#d6ebfa'],
    light: [x - hw, y1, x + hw, y1 + 10],
    edge: 2.6,
    rim: '210, 240, 255',
  });

  for (const dy of [3.6, 7]) {
    ctx.strokeStyle = 'rgba(2, 5, 8, 0.9)';
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    ctx.moveTo(x - hw - 3, y1 + dy);
    ctx.lineTo(x + hw + 3, y1 + dy);
    ctx.stroke();
  }

  ctx.beginPath();
  ctx.ellipse(x, y1 + 2, hw - 1, 2.6, 0, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(1, 4, 6, 0.97)';
  ctx.fill();
  ctx.beginPath();
  ctx.ellipse(x, y1 + 2, (hw - 3) * (0.35 + 0.65 * open), 1.3, 0, 0, Math.PI * 2);
  ctx.fillStyle = `rgba(240, 255, 255, ${0.3 + 0.65 * open})`;
  ctx.fill();
  glowDot(ctx, x, y1 + 2, 4 + 9 * open,
    `rgba(235, 255, 255, ${0.14 + 0.4 * open})`,
    `rgba(${CYAN}, ${0.08 + 0.22 * open})`,
    'rgba(10, 150, 190, 0)');
}

function drawClamp(ctx, x, open) {
  const L = BARREL_IDLE + BARREL_GROW * open;
  const yClamp = BARREL_Y - L + 26;
  const spread = 10 + 8 * open;

  for (const sign of [-1, 1]) {
    const cx = x + sign * spread;
    techPlate(ctx, [
      [cx - 4.5, yClamp - 6], [cx + 4.5, yClamp - 6],
      [cx + 3.6, yClamp + 13], [cx - 3.6, yClamp + 13],
    ], { light: [cx - 5, yClamp - 6, cx + 5, yClamp + 13], edge: 2.4, rim: '175, 210, 235' });
    ctx.beginPath();
    ctx.arc(cx, yClamp + 13, 2.6, 0, Math.PI * 2);
    ctx.fillStyle = '#0a1118';
    ctx.fill();
    ctx.strokeStyle = `rgba(${CYAN}, ${0.3 + 0.4 * open})`;
    ctx.lineWidth = 1.1;
    ctx.stroke();
  }
  ctx.strokeStyle = `rgba(150, 185, 215, ${0.3 + 0.2 * open})`;
  ctx.lineWidth = 1.3;
  ctx.beginPath();
  ctx.moveTo(x - spread + 4.5, yClamp + 9);
  ctx.lineTo(x + spread - 4.5, yClamp + 9);
  ctx.stroke();
}

// ------------------------------------------------------------------ lõi sinh học

function drawCore(ctx, t, open) {
  const x = CORE[0];
  const y = CORE[1];
  const pulse = 0.5 + 0.5 * Math.sin(t * 3.1);

  ctx.beginPath();
  ctx.ellipse(x, y, 20, 26, 0, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(1, 6, 9, 0.97)';
  ctx.fill();

  for (const [rr, ramp, lw] of [[24, BRONZE, 5.5], [19.5, STEEL, 4]]) {
    ctx.beginPath();
    ctx.ellipse(x, y, rr, rr * 1.25, 0, 0, Math.PI * 2);
    const g = ctx.createLinearGradient(x - rr, y - rr, x + rr, y + rr);
    g.addColorStop(0, ramp[5]);
    g.addColorStop(0.45, ramp[3]);
    g.addColorStop(1, ramp[1]);
    ctx.strokeStyle = g;
    ctx.lineWidth = lw;
    ctx.stroke();
  }

  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 5; i++) {
    const a = (i / 5) * Math.PI * 2 + Math.sin(t * 1.2 + i) * 0.06;
    ctx.strokeStyle = `rgba(${CYAN}, ${0.08 + 0.3 * open})`;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(x + Math.cos(a) * 9, y + Math.sin(a) * 12);
    ctx.quadraticCurveTo(
      x + Math.cos(a) * 20, y + Math.sin(a) * 26,
      x + Math.cos(a + 0.35) * 27, y + Math.sin(a + 0.4) * 36,
    );
    ctx.stroke();
  }
  ctx.restore();

  const r = 7 + 9 * open + 2 * pulse;
  glowDot(ctx, x, y, Math.max(1, r * 3),
    `rgba(245, 255, 255, ${0.5 + 0.45 * open})`,
    `rgba(${CYAN}, ${0.28 + 0.38 * open})`,
    'rgba(10, 130, 180, 0)');
  ctx.beginPath();
  ctx.ellipse(x, y, r * 0.5, r * 0.76, 0, 0, Math.PI * 2);
  ctx.fillStyle = `rgba(255, 255, 255, ${0.7 + 0.3 * open})`;
  ctx.fill();
}

/** Giáp vai: 2 tấm trên gốc cánh, trượt ra + xoay mở. */
function drawArmor(ctx, open) {
  for (const sign of [-1, 1]) {
    const pivot = [256 + sign * 40, 236];
    const slide = open * 20 * sign;
    ctx.save();
    ctx.translate(pivot[0] + slide, pivot[1]);
    ctx.rotate(open * 0.14 * sign);
    ctx.translate(-pivot[0], -pivot[1]);

    const pts = sign > 0
      ? [[282, 214], [344, 236], [356, 292], [318, 316], [284, 300], [278, 250]]
      : mirrorPts([[282, 214], [344, 236], [356, 292], [318, 316], [284, 300], [278, 250]]);

    techPlate(ctx, pts, {
      ramp: ['#04080c', '#0a1219', '#16242e', '#263c4b', '#3f5f72', '#7ba0b8'],
      light: sign > 0 ? [284, 216, 356, 316] : [228, 216, 156, 316],
      edge: 6,
      rim: '195, 225, 250',
    });

    const sub = sign > 0
      ? [[300, 240], [340, 254], [346, 288], [310, 292]]
      : mirrorPts([[300, 240], [340, 254], [346, 288], [310, 292]]);
    techPlate(ctx, sub, {
      ramp: ['#03060a', '#070d13', '#0d1820', '#152430', '#1e3340'],
      light: sign > 0 ? [300, 240, 346, 292] : [212, 240, 166, 292],
      edge: 3.4,
      rim: '125, 165, 195',
    });

    glowLine(ctx, sign > 0 ? [[286, 288], [304, 312]] : [[226, 288], [208, 312]], AMBER,
      { w: 1.4, a: 0.12 + 0.45 * open });
    glowLine(ctx, sign > 0 ? [[292, 224], [338, 244]] : [[220, 224], [174, 244]], CYAN,
      { w: 1.4, a: 0.2 + 0.4 * open });
    rivets(ctx, sign > 0 ? [[334, 266], [318, 300]] : [[178, 266], [194, 300]]);
    ctx.restore();
  }
}

function drawOrganic(ctx, t, open) {
  ctx.save();
  ctx.strokeStyle = `rgba(190, 220, 245, ${0.4 + 0.3 * open})`;
  ctx.lineWidth = 1.8;
  ctx.lineCap = 'round';
  for (const sign of [-1, 1]) {
    ctx.beginPath();
    ctx.moveTo(256 + sign * 18, 206);
    ctx.lineTo(256 + sign * (34 + 14 * open), 238);
    ctx.stroke();
  }
  ctx.restore();

  for (let i = 0; i < 3; i++) {
    const x = 256 + (i - 1) * 16;
    const y = 430;
    const sway = Math.sin(t * 1.7 + i * 0.9) * 6;
    glowLine(ctx, [[x, y], [x + sway * 0.5, y + 18], [x + sway, y + 34]], CYAN,
      { w: 1.3, a: 0.08 + 0.2 * open });
  }
}

// ------------------------------------------------------------------ module

export const biomech = {
  id: 'biomech',
  label: 'SINH CƠ',
  usesArt: false,
  laserTint: [120, 245, 255],

  muzzles(s, t, ph) {
    const open = armorOpen(ph);
    const L = barrelLen(open, ph);
    return BARREL_X.map((x0) => ({
      x: (x0 - C) * s,
      y: (BARREL_Y - L - C) * s,
      angle: 0,
      side: x0 < C ? 'l' : 'r',
    }));
  },

  draw(ctx, { s, t, ph }) {
    const open = armorOpen(ph);

    // một lần vào hệ thiết kế 512
    ctx.save();
    ctx.translate(-C * s, -C * s);
    ctx.scale(s, s);

    // ---- động cơ + lửa (3 hình)
    drawEngines(ctx, { glow: CYAN });
    for (let i = 0; i < F.engines.length; i++) {
      const [ex, ey] = F.engines[i];
      drawFlame(ctx, ex, ey + 12, 14, 86, flameFrame(t, i), 0.8 + 0.35 * open, {
        glow: 'rgba(120, 235, 255, 0.3)',
        glowMid: 'rgba(70, 170, 240, 0.13)',
        glowOut: 'rgba(30, 90, 180, 0)',
        outer: 'rgba(70, 190, 255, 0.8)',
        mid: 'rgba(185, 240, 255, 0.95)',
        core: 'rgba(255, 255, 255, 0.96)',
        spark: 'rgba(140, 225, 255, 0.65)',
      });
    }

    // ---- nòng dưới cánh (phần giữa bị cánh che)
    for (const x0 of BARREL_X) drawUnderBarrel(ctx, x0, open, ph);

    // ---- cánh xuôi / cánh mũi / vây đuôi
    for (const sign of [-1, 1]) drawWing(ctx, sign, { glow: CYAN, open, rotate: open * 0.05 * sign });
    for (const sign of [-1, 1]) drawCanard(ctx, sign, { glow: CYAN });
    for (const sign of [-1, 1]) drawTail(ctx, sign, { glow: CYAN });

    // ---- thân + buồng lái + lõi
    drawFuselage(ctx, { glow: CYAN, open });
    drawCore(ctx, t, open);
    drawCanopy(ctx, { tint: '150, 232, 255' });

    // ---- giáp vai + càng kẹp + chi tiết sinh học
    drawArmor(ctx, open);
    for (const x0 of BARREL_X) drawClamp(ctx, x0, open);
    drawOrganic(ctx, t, open);

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
