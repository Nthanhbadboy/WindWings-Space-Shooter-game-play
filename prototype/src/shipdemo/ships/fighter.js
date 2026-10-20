/**
 * KHUNG CHIẾN ĐẤU CƠ — bộ hình học dùng chung để mọi tàu đều "ra dáng máy bay".
 *
 * Nhìn từ trên xuống, một chiến đấu cơ không gian PHẢI có đủ 6 thứ này, thiếu một là
 * người xem đọc thành "cá", "viên đạn" hoặc "con bọ":
 *
 *   1. MŨI NHỌN dài, hẹp dần về phía trước
 *   2. BUỒNG LÁI (ca-nô-pi) nằm ngay sau mũi, nhìn thấy rõ từ trên
 *   3. THÂN THON dài, bề ngang chỉ ~1/7 chiều dài
 *   4. CÁNH XUÔI RA SAU (swept), mép trước là một đường thẳng dài
 *   5. CÁNH ĐUÔI (2 vây) ở phía sau
 *   6. HAI ỐNG XẢ song song ở đuôi
 *
 * Toạ độ thiết kế trong hộp 512×512 (tâm 256,256). Tàu chiếm y ≈ 38…462.
 * Mọi hàm ở đây chỉ VẼ; hình học công khai trong `F` để tàu con tính đầu nòng.
 */

import { STEEL, glowLine, path, rivets, techPlate, tube, vents } from '../mat.js';

export const F = {
  /** mũi tàu */
  nose: [256, 38],
  /** thân: hẹp, dài */
  hull: [
    [256, 38], [264, 92], [272, 148], [281, 216], [285, 288],
    [281, 352], [273, 404], [266, 438], [246, 438], [239, 404],
    [231, 352], [227, 288], [231, 216], [240, 148], [248, 92],
  ],
  /** buồng lái: giọt nước, thấy rõ từ trên */
  canopy: [[256, 100], [271, 128], [275, 174], [256, 212], [237, 174], [241, 128]],
  /** cánh phải (xuôi ra sau). Trái = lật x qua trục 256 */
  wingR: [
    [279, 196], [318, 226], [392, 286], [470, 330],
    [452, 364], [370, 352], [306, 340], [284, 322],
  ],
  /** cánh mũi (canard) phải */
  canardR: [[273, 138], [330, 176], [322, 196], [276, 178]],
  /** vây đuôi phải */
  tailR: [[268, 392], [318, 448], [302, 460], [262, 424]],
  /** hai ống xả */
  engines: [[237, 441], [275, 441]],
  /** nan hoa hút gió trên hông thân */
  intakes: [[278, 214], [276, 268]],
  /** dầm treo vũ khí dưới cánh (điểm gắn nòng) */
  pylon: [96, 300],
};

export const mirrorPts = (pts) => pts.map(([x, y]) => [512 - x, y]);
export const wingPts = (sign) => (sign > 0 ? F.wingR : mirrorPts(F.wingR));
export const canardPts = (sign) => (sign > 0 ? F.canardR : mirrorPts(F.canardR));
export const tailPts = (sign) => (sign > 0 ? F.tailR : mirrorPts(F.tailR));

/** Thân + các tấm giáp chia đốt + nan hút gió. */
export function drawFuselage(ctx, o = {}) {
  const glow = o.glow || '96, 240, 255';
  const rim = o.rim || '185, 220, 245';

  // thân chính
  techPlate(ctx, F.hull, {
    ramp: o.ramp || ['#05090d', '#0a131b', '#15222c', '#21333f', '#334d5d'],
    light: [206, 50, 316, 430],
    edge: 7,
    rim,
  });

  // chia đốt: 4 tấm, tối dần về đuôi
  const segs = [
    [[248, 94], [264, 92], [271, 146], [241, 146]],
    [[241, 150], [271, 150], [280, 212], [232, 212]],
    [[232, 216], [280, 216], [284, 284], [228, 284]],
    [[228, 288], [284, 288], [280, 350], [232, 350]],
    [[232, 354], [280, 354], [272, 402], [240, 402]],
  ];
  segs.forEach((pts, i) => {
    techPlate(ctx, pts, {
      ramp: ['#04080c', '#080f15', '#101c25', '#1a2b37', '#263c4a'],
      light: [226, 90 + i * 60, 290, 150 + i * 60],
      edge: 2.6,
      rim: '120, 165, 195',
    });
  });

  // khe sáng giữa các đốt
  for (const [a, b] of [
    [[232, 212], [280, 212]],
    [[228, 284], [284, 284]],
    [[232, 350], [280, 350]],
  ]) glowLine(ctx, [a, b], glow, { w: 1.3, a: 0.16 + 0.5 * (o.open || 0) });

  // nan hút gió hai hông
  for (const sign of [-1, 1]) {
    vents(ctx, sign > 0 ? 272 : 232, 218, 8, 44, 4, glow, 0.32);
  }

  // sống lưng sáng
  glowLine(ctx, [[256, 96], [256, 200]], o.spineGlow || '210, 245, 255', { w: 1.1, a: 0.3 });

  // mép sáng bên trái (nguồn sáng trên-trái)
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.strokeStyle = 'rgba(210, 240, 255, 0.3)';
  ctx.lineWidth = 2.2;
  ctx.beginPath();
  ctx.moveTo(254, 52);
  ctx.lineTo(241, 150);
  ctx.lineTo(230, 220);
  ctx.stroke();
  ctx.restore();

  rivets(ctx, [[244, 260], [268, 260], [242, 330], [270, 330]], 'rgba(175, 205, 230, 0.4)', 1.9);
}

/** Buồng lái: kính có phản quang, khung xương. */
export function drawCanopy(ctx, o = {}) {
  const t = o.tint || '120, 200, 235';
  path(ctx, F.canopy);
  const g = ctx.createLinearGradient(238, 104, 274, 210);
  g.addColorStop(0, 'rgba(8, 18, 26, 0.98)');
  g.addColorStop(0.45, `rgba(${t}, 0.30)`);
  g.addColorStop(1, 'rgba(4, 10, 16, 0.98)');
  ctx.fillStyle = g;
  ctx.fill();
  ctx.strokeStyle = 'rgba(2, 5, 8, 0.95)';
  ctx.lineWidth = 4;
  ctx.stroke();
  ctx.strokeStyle = `rgba(${t}, 0.65)`;
  ctx.lineWidth = 1.4;
  ctx.stroke();

  // khung kính dọc
  ctx.strokeStyle = 'rgba(2, 6, 10, 0.8)';
  ctx.lineWidth = 2.2;
  ctx.beginPath();
  ctx.moveTo(256, 104);
  ctx.lineTo(256, 208);
  ctx.stroke();
  // phản quang chéo
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.strokeStyle = 'rgba(235, 255, 255, 0.55)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(246, 126);
  ctx.lineTo(262, 166);
  ctx.stroke();
  ctx.restore();
  // lõi sáng trong buồng lái
  const cg = ctx.createRadialGradient(256, 150, 2, 256, 150, 26);
  cg.addColorStop(0, `rgba(${t}, 0.55)`);
  cg.addColorStop(1, `rgba(${t}, 0)`);
  ctx.fillStyle = cg;
  ctx.beginPath();
  ctx.arc(256, 150, 26, 0, Math.PI * 2);
  ctx.fill();
}

/** Cánh xuôi + mép trước phát sáng + đèn đầu cánh + dầm treo. */
export function drawWing(ctx, sign, o = {}) {
  const pts = wingPts(sign);
  const glow = o.glow || '96, 240, 255';
  const light = sign > 0 ? [300, 200, 468, 360] : [212, 200, 44, 360];

  ctx.save();
  if (o.rotate) {
    const p = [256 + sign * 30, 250];
    ctx.translate(p[0], p[1]);
    ctx.rotate(o.rotate);
    ctx.translate(-p[0], -p[1]);
  }

  techPlate(ctx, pts, {
    ramp: o.ramp || ['#060b11', '#0c1620', '#17303c', '#26485a', '#3a6379', '#6f97ad'],
    light,
    edge: 6.5,
    rim: '190, 220, 245',
  });

  // tấm phụ mép sau (tối)
  const sub = sign > 0
    ? [[300, 336], [370, 350], [452, 362], [430, 340], [340, 322]]
    : mirrorPts([[300, 336], [370, 350], [452, 362], [430, 340], [340, 322]]);
  techPlate(ctx, sub, {
    ramp: ['#03070b', '#070e15', '#0e1b24', '#162a35', '#1f3a47'],
    light: sign > 0 ? [330, 325, 450, 365] : [182, 325, 62, 365],
    edge: 4,
    rim: '120, 165, 195',
  });

  // mép trước phát sáng (đường dẫn năng lượng)
  glowLine(ctx, sign > 0
    ? [[282, 198], [320, 228], [394, 288], [466, 330]]
    : [[230, 198], [192, 228], [118, 288], [46, 330]], glow, { w: 2, a: 0.4 + 0.35 * (o.open || 0) });

  // vệt phản quang kim loại
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.strokeStyle = 'rgba(225, 245, 255, 0.22)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  if (sign > 0) {
    ctx.moveTo(292, 208);
    ctx.lineTo(392, 292);
  } else {
    ctx.moveTo(220, 208);
    ctx.lineTo(120, 292);
  }
  ctx.stroke();
  ctx.restore();

  // gân chịu lực
  for (const [a, b] of sign > 0
    ? [[[300, 236], [400, 306]], [[320, 300], [420, 344]]]
    : [[[212, 236], [112, 306]], [[192, 300], [92, 344]]]) {
    ctx.strokeStyle = 'rgba(3, 7, 11, 0.7)';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(a[0], a[1]);
    ctx.lineTo(b[0], b[1]);
    ctx.stroke();
    ctx.strokeStyle = 'rgba(170, 205, 230, 0.2)';
    ctx.lineWidth = 1.1;
    ctx.stroke();
  }

  rivets(ctx, sign > 0
    ? [[322, 246], [374, 296], [430, 330]]
    : [[190, 246], [138, 296], [82, 330]], 'rgba(175, 205, 230, 0.42)', 2);

  // đèn định vị đầu cánh
  const tip = sign > 0 ? [464, 334] : [48, 334];
  const g = ctx.createRadialGradient(tip[0], tip[1], 0, tip[0], tip[1], 16);
  g.addColorStop(0, 'rgba(240, 255, 255, 0.9)');
  g.addColorStop(0.4, `rgba(${glow}, 0.5)`);
  g.addColorStop(1, `rgba(${glow}, 0)`);
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.arc(tip[0], tip[1], 16, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  ctx.restore();
}

/** Cánh mũi nhỏ (canard). */
export function drawCanard(ctx, sign, o = {}) {
  const pts = canardPts(sign);
  techPlate(ctx, pts, {
    ramp: o.ramp || ['#050a0f', '#0a141c', '#132430', '#1d3745', '#2a4c5d'],
    light: sign > 0 ? [276, 140, 330, 200] : [236, 140, 182, 200],
    edge: 4,
    rim: '170, 205, 230',
  });
  glowLine(ctx, sign > 0
    ? [[276, 142], [326, 178]]
    : [[236, 142], [186, 178]], o.glow || '96, 240, 255', { w: 1.2, a: 0.45 });
}

/** Vây đuôi. */
export function drawTail(ctx, sign, o = {}) {
  const pts = tailPts(sign);
  techPlate(ctx, pts, {
    ramp: ['#04080c', '#091118', '#11202a', '#1b3340', '#274a5a'],
    light: sign > 0 ? [266, 394, 320, 460] : [246, 394, 192, 460],
    edge: 5,
    rim: '165, 200, 225',
  });
  glowLine(ctx, sign > 0
    ? [[270, 396], [314, 448]]
    : [[242, 396], [198, 448]], o.glow || '96, 240, 255', { w: 1.1, a: 0.35 });
}

/** Hai ống xả: vỏ động cơ + miệng loa. */
export function drawEngines(ctx, o = {}) {
  const glow = o.glow || '96, 240, 255';
  F.engines.forEach(([ex, ey]) => {
    // vỏ
    techPlate(ctx, [
      [ex - 15, ey - 46], [ex + 15, ey - 46], [ex + 14, ey + 12], [ex - 14, ey + 12],
    ], {
      ramp: ['#04080c', '#0a1219', '#16242e', '#223a48', '#33586a'],
      light: [ex - 15, ey - 46, ex + 15, ey + 12],
      edge: 3.6,
      rim: '185, 215, 240',
    });
    // miệng loa
    ctx.beginPath();
    ctx.ellipse(ex, ey + 10, 13, 5, 0, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(1, 4, 7, 0.98)';
    ctx.fill();
    const g = ctx.createRadialGradient(ex, ey + 10, 0, ex, ey + 10, 13);
    g.addColorStop(0, 'rgba(240, 255, 255, 0.9)');
    g.addColorStop(0.4, `rgba(${glow}, 0.5)`);
    g.addColorStop(1, `rgba(${glow}, 0)`);
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.ellipse(ex, ey + 10, 13, 5, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    // đai nhiệt
    for (const dy of [-34, -20]) {
      ctx.strokeStyle = 'rgba(3, 7, 10, 0.75)';
      ctx.lineWidth = 2.4;
      ctx.beginPath();
      ctx.moveTo(ex - 15, ey + dy);
      ctx.lineTo(ex + 15, ey + dy);
      ctx.stroke();
    }
  });
}

/** Dầm treo vũ khí dưới cánh (ống tròn nhỏ thò ra trước mép cánh). */
export function drawPylon(ctx, sign, o = {}) {
  const x = sign > 0 ? F.pylon[0] : 512 - F.pylon[0];
  tube(ctx, x, F.pylon[1], x, o.length || 196, 10, { edge: 3 });
}

export { STEEL };
