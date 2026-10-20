/**
 * Tàu 1 — "OMEN" cánh dơi.
 *
 * Ảnh 3 mảnh (thân + 2 cánh) là lớp chính; nếu thiếu ảnh thì vẽ vector.
 *
 * Ý tưởng bắn (theo yêu cầu): KHÔNG gắn súng lên cánh nữa.
 *   - hai cánh gồng ngóc lên, đầu hai cánh chụm về phía mũi;
 *   - giáp ngực tách ra, để lộ rãnh năng lượng chạy lên thấu kính ở mũi;
 *   - năng lượng dồn ra trước mũi thành MỘT QUẢ CẦU (2D nhưng tô sáng/khối để
 *     nhìn như quả cầu 3D), hai tia năng lượng từ đầu cánh bơm vào quả cầu;
 *   - khai hỏa: cả quả cầu phóng một luồng laser lớn về phía trước.
 */

import { clamp01, drawFlame, flameFrame, glowDot } from '../fx.js';
import { glowLine, path, rivets, techPlate } from '../mat.js';

const BASE = 512;
const PIVOT = { l: [186, 252], r: [326, 252] };
const NOZZLE = [[214, 462], [298, 462]];

/**
 * Tâm quả cầu năng lượng — đúng chỗ BA ĐIỂM hội tụ: mũi tàu (256, 29) ở trên,
 * hai đầu cánh khi gồng hết cỡ ở (247, 72) và (265, 72) hai bên.
 * Đặt ở giữa để quả cầu "được ba đầu nhọn chụm vào" chứ không phải gắn lên mũi.
 */
const ORB = [256, 47];
/** Thấu kính ở đúng mũi tàu (đỉnh art thân). */
const LENS = [256, 30];

/** Đầu nhọn trên của hai cánh — chỗ phóng tia năng lượng vào quả cầu. */
const WING_TIP = { l: [162, 63], r: [350, 63] };

const drawInBase = (ctx, s, fn) => {
  ctx.save();
  ctx.translate(-BASE * s / 2, -BASE * s / 2);
  ctx.scale(s, s);
  fn();
  ctx.restore();
};

/** Khung xoay quanh gốc cánh — dùng chung cho vẽ và tính đầu cánh. */
function wingFrame(side, s, angle) {
  const [px, py] = PIVOT[side];
  const ox = (px - BASE / 2) * s;
  const oy = (py - BASE / 2) * s;
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  return {
    ox,
    oy,
    apply(ctx) {
      ctx.translate(ox, oy);
      ctx.rotate(angle);
      ctx.translate(-ox, -oy);
    },
    map(bx, by) {
      const vx = (bx - px) * s;
      const vy = (by - py) * s;
      return { x: ox + vx * cos - vy * sin, y: oy + vx * sin + vy * cos };
    },
  };
}

// ------------------------------------------------------------------ hình vector

function vectorWing(ctx, side, tint) {
  const dir = side === 'r' ? 1 : -1;
  const X = (x) => (dir === 1 ? x : BASE - x);

  ctx.beginPath();
  ctx.moveTo(X(298), 198);
  ctx.quadraticCurveTo(X(372), 156, X(452), 196);
  ctx.lineTo(X(474), 250);
  ctx.quadraticCurveTo(X(430), 262, X(446), 326);
  ctx.quadraticCurveTo(X(392), 296, X(372), 338);
  ctx.quadraticCurveTo(X(340), 300, X(310), 336);
  ctx.quadraticCurveTo(X(306), 268, X(298), 198);
  ctx.closePath();

  const g = ctx.createLinearGradient(X(300), 180, X(460), 330);
  g.addColorStop(0, '#3a4676');
  g.addColorStop(0.55, '#232c52');
  g.addColorStop(1, '#10152c');
  ctx.fillStyle = g;
  ctx.fill();
  ctx.strokeStyle = tint ? 'rgba(217, 180, 95, 0.55)' : '#d9b45f';
  ctx.lineWidth = 6;
  ctx.stroke();

  ctx.strokeStyle = 'rgba(226, 190, 110, 0.45)';
  ctx.lineWidth = 3;
  for (const [tx, ty] of [[452, 196], [474, 250], [446, 326], [372, 338]]) {
    ctx.beginPath();
    ctx.moveTo(X(326), 252);
    ctx.lineTo(X(tx), ty);
    ctx.stroke();
  }

  const tg = ctx.createRadialGradient(X(452), 208, 0, X(452), 208, 46);
  tg.addColorStop(0, 'rgba(150, 200, 255, 0.35)');
  tg.addColorStop(1, 'rgba(120, 90, 255, 0)');
  ctx.fillStyle = tg;
  ctx.beginPath();
  ctx.arc(X(452), 208, 46, 0, Math.PI * 2);
  ctx.fill();
}

function vectorHull(ctx, tint) {
  ctx.beginPath();
  ctx.moveTo(256, 86);
  ctx.quadraticCurveTo(296, 190, 300, 268);
  ctx.quadraticCurveTo(302, 356, 272, 420);
  ctx.quadraticCurveTo(256, 436, 240, 420);
  ctx.quadraticCurveTo(210, 356, 212, 268);
  ctx.quadraticCurveTo(216, 190, 256, 86);
  ctx.closePath();
  const bg = ctx.createLinearGradient(206, 90, 306, 430);
  bg.addColorStop(0, '#4a5a92');
  bg.addColorStop(0.45, '#2a3358');
  bg.addColorStop(1, '#141a33');
  ctx.fillStyle = bg;
  ctx.fill();
  ctx.strokeStyle = tint ? 'rgba(232, 201, 119, 0.55)' : '#e8c977';
  ctx.lineWidth = 6;
  ctx.stroke();

  ctx.strokeStyle = 'rgba(170, 200, 255, 0.35)';
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(256, 104);
  ctx.lineTo(256, 400);
  ctx.stroke();

  ctx.beginPath();
  ctx.ellipse(256, 250, 27, 48, 0, 0, Math.PI * 2);
  const cg = ctx.createRadialGradient(256, 250, 3, 256, 250, 54);
  cg.addColorStop(0, 'rgba(255,255,255,0.95)');
  cg.addColorStop(0.42, 'rgba(196,120,255,0.92)');
  cg.addColorStop(1, 'rgba(110,44,200,0.18)');
  ctx.fillStyle = cg;
  ctx.fill();
  ctx.strokeStyle = 'rgba(232, 201, 119, 0.85)';
  ctx.lineWidth = 4;
  ctx.stroke();

  for (const [nx] of NOZZLE) {
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(nx - 24, 408, 48, 58, 14);
    else ctx.rect(nx - 24, 408, 48, 58);
    const ng = ctx.createLinearGradient(nx, 408, nx, 466);
    ng.addColorStop(0, '#39406b');
    ng.addColorStop(1, '#141a33');
    ctx.fillStyle = ng;
    ctx.fill();
    ctx.strokeStyle = 'rgba(160, 130, 230, 0.85)';
    ctx.lineWidth = 4;
    ctx.stroke();
    ctx.beginPath();
    ctx.ellipse(nx, 462, 18, 7, 0, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(150, 120, 255, 0.55)';
    ctx.fill();
  }
}

// ------------------------------------------------------------------ cơ cấu trên thân

/**
 * Rãnh năng lượng dọc sống mũi (phần "sinh cơ" của THÂN):
 * hai dải giáp hẹp trượt ra hai bên khi gồng, để lộ rãnh sáng chạy lên thấu kính.
 * Hẹp thôi để không che mất lớp art của thân.
 */
function drawSpineRail(ctx, s, t, ph) {
  const open = clamp01(ph.charge);
  const pulse = 0.5 + 0.5 * Math.sin(t * 5.2);
  drawInBase(ctx, s, () => {
    // hốc dẫn năng lượng phía dưới: tối, có rãnh sáng chạy lên
    techPlate(ctx, [
      [240, 96], [272, 96], [268, 168], [244, 168],
    ], {
      ramp: ['#04060c', '#080c16', '#101828', '#19243a', '#22314c'],
      light: [238, 96, 274, 170],
      edge: 3,
      rim: '170, 150, 230',
    });
    glowLine(ctx, [[256, 100], [256, 164]], '196, 150, 255', { w: 1.4, a: 0.16 + 0.5 * open });

    // HAI CÀNG NÒNG kim loại: thuôn nhỏ về phía thấu kính, hơi chụm vào trong
    for (const sign of [-1, 1]) {
      const slide = sign * (2.5 + 5 * open);
      const x0 = (sign > 0 ? 262 : 250) + slide;
      const inward = -sign * 1.6; // mũi chụm vào
      const pts = [
        [x0 - 3.6 + inward, 78], [x0 + 3.6 + inward, 78],
        [x0 + 5.6, 112], [x0 + 7.4, 158], [x0 - 7.4, 158], [x0 - 5.6, 112],
      ];
      techPlate(ctx, pts, {
        ramp: ['#05070f', '#0b1020', '#1a2038', '#2b3252', '#474f78', '#7d86b8'],
        light: [x0 - 7, 74, x0 + 7, 158],
        edge: 2.6,
        rim: '205, 215, 255',
      });
      // khấc trên càng
      ctx.strokeStyle = 'rgba(4, 6, 14, 0.8)';
      ctx.lineWidth = 1.6;
      for (let i = 0; i < 4; i++) {
        const k = i / 4;
        const y = 92 + i * 17;
        const w = 4.4 + 2.6 * k;
        ctx.beginPath();
        ctx.moveTo(x0 - w + inward * (1 - k), y);
        ctx.lineTo(x0 + w + inward * (1 - k), y);
        ctx.stroke();
      }
      // đinh tán
      rivets(ctx, [[x0 + inward * 0.8, 86], [x0, 150]], 'rgba(220, 210, 255, 0.4)', 1.5);
      // khe năng lượng mép trong (sáng lên khi gồng)
      glowLine(ctx, [[x0 - sign * 5, 86], [x0 - sign * 6.5, 150]], '205, 165, 255',
        { w: 1.1, a: 0.12 + 0.42 * open });
    }

    // chốt nối càng vào thân
    for (const y of [88, 148]) {
      for (const sign of [-1, 1]) {
        ctx.beginPath();
        ctx.arc(256 + sign * 12, y, 2.6, 0, Math.PI * 2);
        ctx.fillStyle = '#0a0e18';
        ctx.fill();
        ctx.strokeStyle = 'rgba(217, 180, 95, 0.8)';
        ctx.lineWidth = 1.2;
        ctx.stroke();
      }
    }

    // thấu kính ở mũi — nơi năng lượng rời thân
    glowDot(ctx, 256, 64, (7 + 7 * open) * (0.85 + 0.15 * pulse),
      `rgba(255,255,255,${0.3 + 0.35 * open})`,
      `rgba(200,150,255,${0.14 + 0.26 * open})`,
      'rgba(120,60,220,0)');
  });
}

// ------------------------------------------------------------------ quả cầu năng lượng

function orbPos(s) {
  return { x: (ORB[0] - BASE / 2) * s, y: (ORB[1] - BASE / 2) * s };
}

/**
 * Quả cầu trước mũi — tâm điểm của D14.
 *
 * Để "2D mà ăn gian 3D": vẽ 4 lớp
 *   1. quầng sáng lớn (cộng sáng)
 *   2. KHỐI CẦU có gradient lệch lên-trái (sáng trên, tím thẫm dưới) → bóng khối
 *   3. viền sáng mảnh ở rìa + chấm phản quang
 *   4. vành nghiêng xoay + tia lửa (cộng sáng)
 */
function drawOrb(ctx, s, t, ph) {
  const charge = clamp01(ph.charge);
  const collapse = ph.stage === 'fire' ? clamp01(ph.k * 2.2) : 0;
  const live = Math.max(charge * (1 - collapse), ph.stage === 'fire' ? Math.max(0, 1 - ph.k * 2.6) : 0);
  if (live < 0.02) return;

  const { x, y } = orbPos(s);
  const pulse = 0.5 + 0.5 * Math.sin(t * 7);
  const r = (10 + 19 * live + 1.6 * pulse) * s;

  // ---------- 1. quầng
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  const halo = ctx.createRadialGradient(x, y, 0, x, y, r * 3.8);
  halo.addColorStop(0, `rgba(186, 152, 255, ${0.3 * live})`);
  halo.addColorStop(0.35, `rgba(130, 92, 245, ${0.16 * live})`);
  halo.addColorStop(1, 'rgba(70, 30, 180, 0)');
  ctx.fillStyle = halo;
  ctx.beginPath();
  ctx.arc(x, y, r * 3.8, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // ---------- 2. khối cầu (vẽ thường, không cộng sáng → giữ được vùng tối)
  const body = ctx.createRadialGradient(x - r * 0.36, y - r * 0.4, r * 0.04, x - r * 0.05, y - r * 0.05, r * 1.1);
  body.addColorStop(0, `rgba(255,255,255,${0.99})`);
  body.addColorStop(0.13, `rgba(252,244,255,${0.96 * live + 0.02})`);
  body.addColorStop(0.38, `rgba(214,176,255,${0.9 * live + 0.03})`);
  body.addColorStop(0.68, `rgba(150,96,246,${0.88 * live + 0.02})`);
  body.addColorStop(0.9, `rgba(86,38,190,${0.86 * live})`);
  body.addColorStop(1, `rgba(44,14,116,${0.8 * live})`);
  ctx.fillStyle = body;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fill();

  // rìa tối phía dưới-phải cho ra khối
  const limb = ctx.createRadialGradient(x, y, r * 0.55, x, y, r);
  limb.addColorStop(0, 'rgba(40,10,90,0)');
  limb.addColorStop(1, `rgba(30,6,70,${0.55 * live})`);
  ctx.fillStyle = limb;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fill();

  ctx.save();
  ctx.globalCompositeOperation = 'lighter';

  // ---------- 3. viền sáng rìa + phản quang
  ctx.strokeStyle = `rgba(235, 220, 255, ${0.7 * live})`;
  ctx.lineWidth = Math.max(0.8, 1.3 * s);
  ctx.beginPath();
  ctx.arc(x, y, r * 0.98, Math.PI * 1.05, Math.PI * 1.72);
  ctx.stroke();
  ctx.strokeStyle = `rgba(190, 150, 255, ${0.45 * live})`;
  ctx.beginPath();
  ctx.arc(x, y, r * 0.98, Math.PI * 0.12, Math.PI * 0.55);
  ctx.stroke();

  const hl = ctx.createRadialGradient(x - r * 0.4, y - r * 0.44, 0, x - r * 0.4, y - r * 0.44, r * 0.34);
  hl.addColorStop(0, `rgba(255,255,255,${0.95 * live})`);
  hl.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = hl;
  ctx.beginPath();
  ctx.arc(x - r * 0.4, y - r * 0.44, r * 0.34, 0, Math.PI * 2);
  ctx.fill();

  // ---------- 4. vành nghiêng xoay (đọc ra chiều sâu)
  for (let i = 0; i < 2; i++) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(0.5 + i * 0.7 + t * (i ? -0.85 : 1.15));
    ctx.strokeStyle = i ? `rgba(196,166,255,${0.4 * live})` : `rgba(255,248,255,${0.6 * live})`;
    ctx.lineWidth = Math.max(0.8, (i ? 1.1 : 1.5) * s);
    ctx.beginPath();
    ctx.ellipse(0, 0, r * (1.45 + i * 0.3), r * 0.42, 0, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();
  }

  // dải xích đạo mờ → đọc ra mặt cầu nghiêng
  ctx.save();
  ctx.strokeStyle = `rgba(226, 200, 255, ${0.28 * live})`;
  ctx.lineWidth = Math.max(0.7, 1.1 * s);
  ctx.beginPath();
  ctx.ellipse(x, y, r * 0.99, r * 0.24, 0.18, 0, Math.PI * 2);
  ctx.stroke();
  ctx.strokeStyle = `rgba(150, 100, 240, ${0.22 * live})`;
  ctx.beginPath();
  ctx.ellipse(x, y, r * 0.86, r * 0.19, 0.18, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();

  // tia lửa quanh cầu
  for (let i = 0; i < 6; i++) {
    const a = t * (1.5 + i * 0.3) + (i * Math.PI * 2) / 6;
    const rr = r * (1.55 + 0.3 * Math.sin(t * 3.1 + i));
    ctx.beginPath();
    ctx.arc(x + Math.cos(a) * rr, y + Math.sin(a) * rr * 0.78, Math.max(0.7, 1.2 * s), 0, Math.PI * 2);
    ctx.fillStyle = `rgba(238, 224, 255, ${0.5 * live})`;
    ctx.fill();
  }
  ctx.restore();
}

/**
 * Ba "móng" năng lượng: mỗi điểm hội tụ (2 đầu cánh + thấu kính mũi) phóng một
 * dải sáng cong bọc lấy quả cầu. Đây là thứ làm người xem đọc ra "quả cầu do ba
 * đầu nhọn chụm vào", thay vì một quả bóng dán lên mũi.
 */
function drawClaws(ctx, s, t, ph) {
  const { x: ox, y: oy } = orbPos(s);
  const live = Math.max(0, clamp01(ph.charge) - (ph.stage === 'fire' ? ph.k * 2.6 : 0));
  if (live < 0.05) return;
  const pts = [];
  for (const side of ['l', 'r']) {
    const [tx, ty] = WING_TIP[side];
    pts.push(wingFrame(side, s, wingAngleFor(side, t, ph)).map(tx, ty));
  }
  pts.push({ x: (LENS[0] - BASE / 2) * s, y: (LENS[1] - BASE / 2) * s });

  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.lineCap = 'round';
  pts.forEach((p, i) => {
    const dx = p.x - ox;
    const dy = p.y - oy;
    const len = Math.hypot(dx, dy) || 1;
    const nx = -dy / len;
    const ny = dx / len;
    const bend = (i === 2 ? 1 : i ? -1 : 1) * 15 * s * (0.4 + 0.6 * live);
    const a = (0.25 + 0.5 * live) * (0.85 + 0.15 * Math.sin(t * 6 + i));
    ctx.beginPath();
    ctx.moveTo(p.x, p.y);
    ctx.quadraticCurveTo(
      ox + dx * 0.45 + nx * bend, oy + dy * 0.45 + ny * bend,
      ox + dx * 0.16, oy + dy * 0.16,
    );
    ctx.strokeStyle = `rgba(214, 178, 255, ${a * 0.6})`;
    ctx.lineWidth = Math.max(0.9, 2.2 * s);
    ctx.stroke();
    ctx.strokeStyle = `rgba(255, 252, 255, ${a})`;
    ctx.lineWidth = Math.max(0.5, 0.9 * s);
    ctx.stroke();
  });
  ctx.restore();
}

/** Hai tia năng lượng từ ĐẦU CÁNH chụm vào quả cầu (chỉ hiện khi đầu cánh đã chụm gần). */
function drawFeedArcs(ctx, s, t, ph) {
  const orb = orbPos(s);
  const lens = { x: (LENS[0] - BASE / 2) * s, y: (LENS[1] - BASE / 2) * s };
  const charge = clamp01(ph.charge);

  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.lineCap = 'round';

  const arc = (from, width, alpha, bend) => {
    if (alpha <= 0.01) return;
    const mx = (from.x + orb.x) / 2 + bend;
    const my = (from.y + orb.y) / 2;
    ctx.beginPath();
    ctx.moveTo(from.x, from.y);
    ctx.quadraticCurveTo(mx, my, orb.x, orb.y);
    ctx.strokeStyle = `rgba(196, 150, 255, ${alpha * 0.55})`;
    ctx.lineWidth = width;
    ctx.stroke();
    ctx.strokeStyle = `rgba(255, 255, 255, ${alpha * 0.9})`;
    ctx.lineWidth = Math.max(0.7, width * 0.34);
    ctx.stroke();

    const k = (t * 1.8) % 1;
    const px = (1 - k) * (1 - k) * from.x + 2 * (1 - k) * k * mx + k * k * orb.x;
    const py = (1 - k) * (1 - k) * from.y + 2 * (1 - k) * k * my + k * k * orb.y;
    ctx.beginPath();
    ctx.arc(px, py, Math.max(1, 1.7 * s), 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255,255,255,${alpha})`;
    ctx.fill();
  };

  // hai đầu cánh: càng chụm gần quả cầu thì tia càng rõ
  for (const side of ['l', 'r']) {
    const [tx, ty] = WING_TIP[side];
    const tip = wingFrame(side, s, wingAngleFor(side, t, ph)).map(tx, ty);
    const d = Math.hypot(tip.x - orb.x, tip.y - orb.y);
    const near = clamp01(1 - (d - 42 * s) / (95 * s));
    arc(tip, 1.7 * s, near * (0.22 + 0.5 * charge), (side === 'l' ? -1 : 1) * 6 * s);
  }

  // tia từ thấu kính mũi hắt lên quả cầu
  const dLens = Math.hypot(lens.x - orb.x, lens.y - orb.y) / s;
  arc(lens, 2.2 * s, (0.12 + 0.34 * charge) * clamp01(1 - (dLens - 40) / 120), 0);
  ctx.restore();
}

// ------------------------------------------------------------------ cơ cấu cánh

function wingAngleFor(side, t, ph) {
  const breath = Math.sin(t * 2.1) * 0.014 * (1 - Math.min(1, Math.abs(ph.wing) * 2));
  // gồng: cánh ngóc mạnh hơn để đầu cánh chụm về phía mũi
  const liftAngle = 0.03 + ph.wing * 0.42 + breath;
  const flap = Math.sin(t * 4.4) * 0.014 * (1 - Math.min(1, Math.abs(ph.wing) * 2));
  const buzz = Math.sin(t * 62) * 0.0038 * Math.abs(ph.wing) * (1 - Math.abs(ph.wing));
  return (side === 'l' ? 1 : -1) * (liftAngle + flap + buzz - ph.recoil * 0.055);
}

function drawPiston(ctx, side, s, angle, ph) {
  const dir = side === 'l' ? -1 : 1;
  const hullAnchor = [256 + dir * 34, 344];
  const wingAnchor = [256 + dir * 84, 322];
  const f = wingFrame(side, s, angle);
  const a = { x: (hullAnchor[0] - BASE / 2) * s, y: (hullAnchor[1] - BASE / 2) * s };
  const b = f.map(wingAnchor[0], wingAnchor[1]);

  ctx.save();
  ctx.lineCap = 'round';
  ctx.strokeStyle = '#11161f';
  ctx.lineWidth = 9 * s;
  ctx.beginPath();
  ctx.moveTo(a.x, a.y);
  ctx.lineTo(b.x, b.y);
  ctx.stroke();
  ctx.strokeStyle = '#6b7a99';
  ctx.lineWidth = 5.5 * s;
  ctx.beginPath();
  ctx.moveTo(a.x, a.y);
  ctx.lineTo(a.x + (b.x - a.x) * 0.55, a.y + (b.y - a.y) * 0.55);
  ctx.stroke();
  ctx.strokeStyle = ph.charge > 0.1 ? '#cfd8ff' : '#9aa8c6';
  ctx.lineWidth = 2.6 * s;
  ctx.beginPath();
  ctx.moveTo(a.x + (b.x - a.x) * 0.45, a.y + (b.y - a.y) * 0.45);
  ctx.lineTo(b.x, b.y);
  ctx.stroke();
  for (const p of [a, b]) {
    ctx.beginPath();
    ctx.arc(p.x, p.y, 4.2 * s, 0, Math.PI * 2);
    ctx.fillStyle = '#2b3550';
    ctx.fill();
    ctx.strokeStyle = '#d9b45f';
    ctx.lineWidth = 1.6 * s;
    ctx.stroke();
  }
  ctx.restore();
}

function drawHinge(ctx, side, s) {
  const [px, py] = PIVOT[side];
  const x = (px - BASE / 2) * s;
  const y = (py - BASE / 2) * s;
  const r = 12 * s;
  ctx.save();
  const g = ctx.createRadialGradient(x - r * 0.3, y - r * 0.35, r * 0.1, x, y, r);
  g.addColorStop(0, '#8fa0c2');
  g.addColorStop(0.6, '#35405c');
  g.addColorStop(1, '#151b29');
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fillStyle = g;
  ctx.fill();
  ctx.strokeStyle = '#d9b45f';
  ctx.lineWidth = 1.8;
  ctx.stroke();
  ctx.fillStyle = '#0d1220';
  ctx.beginPath();
  ctx.arc(x, y, r * 0.33, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#a9b9d8';
  for (let i = 0; i < 3; i++) {
    const a = -Math.PI / 2 + (i * Math.PI * 2) / 3;
    ctx.beginPath();
    ctx.arc(x + Math.cos(a) * r * 0.68, y + Math.sin(a) * r * 0.68, r * 0.13, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

// ------------------------------------------------------------------ module

export const omen = {
  id: 'omen',
  label: 'CÁNH DƠI',
  usesArt: true,
  laserTint: [205, 165, 255],

  /** Một "đầu nòng" duy nhất: tâm quả cầu năng lượng trước mũi. */
  muzzles(s, t, ph) {
    const { x, y } = orbPos(s);
    return [{ x, y, angle: 0, scale: 2.1 }];
  },

  draw(ctx, { s, t, ph, img, art }) {
    // lửa đuôi (3 hình) — vẽ trước để nằm sau thân
    const throttle = 0.78 + 0.3 * (0.5 + 0.5 * Math.sin(t * 2.4)) + ph.charge * 0.3;
    for (let i = 0; i < NOZZLE.length; i++) {
      const [nx, ny] = NOZZLE[i];
      drawFlame(ctx, (nx - BASE / 2) * s, (ny - BASE / 2) * s, 20 * s, 96 * s, flameFrame(t, i), throttle);
    }

    // cánh
    for (const side of ['l', 'r']) {
      const angle = wingAngleFor(side, t, ph);
      const f = wingFrame(side, s, angle);
      const stretch = 1 + ph.wing * 0.03 - ph.recoil * 0.02;
      const base = side === 'l' ? img.wingL : img.wingR;
      const dim = side === 'l' ? img.wingLDim : img.wingRDim;
      const canArt = art && base && base.width > 0;

      ctx.save();
      f.apply(ctx);
      ctx.scale(stretch, stretch);
      if (canArt) {
        const dimK = clamp01(ph.wing * 0.55 + ph.recoil * 0.35);
        drawInBase(ctx, s, () => {
          ctx.drawImage(base, 0, 0);
          if (dimK > 0.01 && dim && dim.width > 0) {
            ctx.globalAlpha = dimK * 0.75;
            ctx.drawImage(dim, 0, 0);
            ctx.globalAlpha = 1;
          }
        });
      } else {
        drawInBase(ctx, s, () => vectorWing(ctx, side));
      }
      ctx.restore();
    }

    // thân
    if (art && img.body && img.body.width > 0) {
      drawInBase(ctx, s, () => ctx.drawImage(img.body, 0, 0));
    } else {
      drawInBase(ctx, s, () => vectorHull(ctx));
    }

    // rãnh sống mũi (phần biến hình của thân); thấu kính nằm ở đầu rãnh
    drawSpineRail(ctx, s, t, ph);

    // cánh mũi (canard) + vây đuôi — đặt đúng chỗ trống giữa thân và cánh để NHÌN THẤY
    drawInBase(ctx, s, () => {
      const goldRim = 'rgba(217, 180, 95, 0.85)';
      for (const sign of [-1, 1]) {
        // canard: từ hông mũi hắt ra, nằm trong khoảng trống y≈118..170
        const canard = sign > 0
          ? [[292, 124], [352, 158], [344, 176], [290, 160]]
          : [[220, 124], [160, 158], [168, 176], [222, 160]];
        techPlate(ctx, canard, {
          ramp: ['#080a16', '#101426', '#1b2238', '#28324f', '#3b4a6e'],
          light: sign > 0 ? [292, 124, 352, 176] : [220, 124, 160, 176],
          edge: 3,
          rim: '190, 200, 245',
        });
        ctx.save();
        ctx.strokeStyle = goldRim;
        ctx.lineWidth = 1.8;
        path(ctx, canard);
        ctx.stroke();
        ctx.restore();
        glowLine(ctx, sign > 0 ? [[294, 130], [348, 160]] : [[218, 130], [164, 160]],
          '205, 165, 255', { w: 1.1, a: 0.4 });

        // vây đuôi: dựng đứng hai bên đuôi, viền vàng cho nổi trên nền tối
        const tail = sign > 0
          ? [[292, 372], [340, 424], [326, 440], [288, 402]]
          : [[220, 372], [172, 424], [186, 440], [224, 402]];
        techPlate(ctx, tail, {
          ramp: ['#06080f', '#0c1120', '#161d30', '#222b45', '#333f60'],
          light: sign > 0 ? [288, 372, 340, 440] : [224, 372, 172, 440],
          edge: 3,
          rim: '185, 195, 235',
        });
        ctx.save();
        ctx.strokeStyle = goldRim;
        ctx.lineWidth = 1.8;
        path(ctx, tail);
        ctx.stroke();
        ctx.restore();
        glowLine(ctx, sign > 0 ? [[294, 384], [330, 428]] : [[218, 384], [182, 428]],
          '205, 165, 255', { w: 1, a: 0.3 });
      }
    });

    // cơ cấu cánh
    for (const side of ['l', 'r']) drawPiston(ctx, side, s, wingAngleFor(side, t, ph), ph);
    for (const side of ['l', 'r']) drawHinge(ctx, side, s);

    // năng lượng bơm vào quả cầu + quả cầu
    drawFeedArcs(ctx, s, t, ph);
    drawClaws(ctx, s, t, ph);
    drawOrb(ctx, s, t, ph);
  },

  skeleton(ctx, s, t, ph) {
    ctx.strokeStyle = 'rgba(120, 230, 255, 0.8)';
    ctx.fillStyle = 'rgba(120, 230, 255, 0.9)';
    ctx.lineWidth = 1;
    for (const side of ['l', 'r']) {
      const [px, py] = PIVOT[side];
      const x = (px - BASE / 2) * s;
      const y = (py - BASE / 2) * s;
      ctx.beginPath();
      ctx.moveTo(x - 7, y);
      ctx.lineTo(x + 7, y);
      ctx.moveTo(x, y - 7);
      ctx.lineTo(x, y + 7);
      ctx.stroke();
    }
    for (const [nx, ny] of NOZZLE) {
      ctx.strokeStyle = 'rgba(255, 190, 90, 0.85)';
      ctx.beginPath();
      ctx.arc((nx - BASE / 2) * s, (ny - BASE / 2) * s, 6, 0, Math.PI * 2);
      ctx.stroke();
    }
    for (const m of this.muzzles(s, t, ph)) {
      ctx.strokeStyle = 'rgba(255, 120, 220, 0.95)';
      ctx.beginPath();
      ctx.arc(m.x, m.y, 6, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(m.x, m.y);
      ctx.lineTo(m.x, m.y - 34);
      ctx.stroke();
    }
  },
};

/** Giữ API cũ: vẽ tàu vector tĩnh. */
export function drawVectorShip(ctx, s) {
  drawInBase(ctx, s, () => {
    vectorWing(ctx, 'l');
    vectorWing(ctx, 'r');
    vectorHull(ctx);
  });
}

export { BASE, NOZZLE, PIVOT };
