/**
 * "Vật liệu" dùng chung cho các tàu — bộ hàm vẽ cho ra cảm giác KIM LOẠI + CÔNG NGHỆ
 * thay vì các mảng phẳng một màu (kiểu "màu dại").
 *
 * Công thức chung của một tấm giáp (techPlate):
 *   1. nền tối gần đen            → giữ độ sâu, không bị "bệt"
 *   2. gradient chéo 4–5 điểm dừng → khối
 *   3. viền ngoài gần đen, dày    → tách khỏi nền
 *   4. bóng trong (inner shadow)  → mép dưới tối đi, đọc ra độ dày
 *   5. viền sáng (rim) chạy gradient, mảnh → ánh kim loại bắt sáng
 *   6. đường ghép tấm + đinh tán  → chi tiết cơ khí
 *
 * Màu "công nghệ" = NỀN ÍT BÃO HOÀ + MỘT phát xạ bão hoà nhỏ + MỘT ánh bù (complementary)
 * ở phía đối diện nguồn sáng. Đừng phủ kín thân bằng màu bão hoà.
 */

export const clamp01 = (v) => Math.max(0, Math.min(1, v));

/** Bảng màu thép: từ gần đen tới điểm sáng nhất. */
export const STEEL = ['#05090d', '#0a121a', '#17242f', '#2b4152', '#4d6c82', '#8aa9c0'];
/** Bảng màu đồng/thau (cho tàu "cơ khí nặng"). */
export const BRONZE = ['#0a0705', '#14100a', '#2a2118', '#453524', '#6d543a', '#b08f5f'];
/** Bảng màu gốm trắng (cho tàu "cao cấp"). */
export const CERAMIC = ['#0b0e12', '#1a222b', '#33424f', '#5b7285', '#93aec1', '#dfeef8'];

export const rgb = (s) => s; // màu đã là chuỗi CSS

/** Dựng path đa giác (không fill/stroke). */
export function path(ctx, pts) {
  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  ctx.closePath();
}

/** Path đường gấp khúc (không close). */
export function line(ctx, pts) {
  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
}

const grad = (ctx, p, colors) => {
  const g = ctx.createLinearGradient(p[0], p[1], p[2], p[3]);
  const n = colors.length;
  colors.forEach((c, i) => g.addColorStop(n === 1 ? 0 : i / (n - 1), c));
  return g;
};

/**
 * Một tấm giáp "có vật liệu".
 * @param {CanvasRenderingContext2D} ctx
 * @param {number[][]} pts đa giác
 * @param {object} o
 *   ramp   mảng màu nền (mặc định STEEL)
 *   light  [x0,y0,x1,y1] hướng sáng của gradient (mặc định từ trên-trái xuống dưới-phải)
 *   rim    'r,g,b' màu viền sáng
 *   rimSide 'top'|'left'|'right'|'both' — cạnh bắt sáng
 *   edge   độ dày viền tối ngoài
 *   panel  true → thêm đường ghép
 *   glow   'r,g,b' nếu mép trong phát sáng (tuỳ chọn)
 *   alpha  độ đục lớp nền
 */
export function techPlate(ctx, pts, o = {}) {
  const ramp = o.ramp || STEEL;
  const light = o.light || [-40, -60, 90, 120];
  const edge = o.edge == null ? 6 : o.edge;
  const rim = o.rim || '150, 200, 235';

  ctx.save();
  path(ctx, pts);
  ctx.fillStyle = grad(ctx, light, ramp);
  ctx.globalAlpha = o.alpha == null ? 1 : o.alpha;
  ctx.fill();
  ctx.globalAlpha = 1;

  // bóng trong: phủ một gradient tối từ phía dưới-phải, cắt theo path
  ctx.save();
  path(ctx, pts);
  ctx.clip();
  const sh = ctx.createLinearGradient(light[0] + 160, light[1] + 200, light[0], light[1] - 60);
  sh.addColorStop(0, 'rgba(0, 0, 0, 0.55)');
  sh.addColorStop(0.55, 'rgba(0, 0, 0, 0.12)');
  sh.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = sh;
  ctx.fillRect(-400, -400, 1024, 1024);
  ctx.restore();

  // viền tối ngoài
  if (edge > 0) {
    path(ctx, pts);
    ctx.strokeStyle = 'rgba(2, 4, 7, 0.95)';
    ctx.lineWidth = edge;
    ctx.lineJoin = 'round';
    ctx.stroke();
  }

  // viền sáng: gradient dọc theo hướng sáng nên cạnh sáng tự nổi lên
  path(ctx, pts);
  const rimGrad = ctx.createLinearGradient(light[0], light[1], light[0] + 200, light[1] + 260);
  rimGrad.addColorStop(0, `rgba(${rim}, 0.85)`);
  rimGrad.addColorStop(0.45, `rgba(${rim}, 0.28)`);
  rimGrad.addColorStop(1, `rgba(${rim}, 0.06)`);
  ctx.strokeStyle = rimGrad;
  ctx.lineWidth = 1.7;
  ctx.stroke();

  // phát xạ mép trong
  if (o.glow) {
    path(ctx, pts);
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    for (const [w, a] of [[7, 0.06], [3.4, 0.12], [1.4, 0.3]]) {
      ctx.strokeStyle = `rgba(${o.glow}, ${a})`;
      ctx.lineWidth = w;
      ctx.stroke();
    }
    ctx.restore();
  }
  ctx.restore();
}

/** Đường năng lượng phát sáng nhiều lớp (không cần filter blur). */
export function glowLine(ctx, pts, color, o = {}) {
  const w = o.w || 2;
  const a = o.a == null ? 0.9 : o.a;
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.lineCap = o.cap || 'round';
  line(ctx, pts);
  for (const [mul, alpha] of [[5, 0.05], [3, 0.1], [1.8, 0.22], [1, 0.55]]) {
    ctx.strokeStyle = `rgba(${color}, ${alpha * a})`;
    ctx.lineWidth = w * mul;
    ctx.stroke();
  }
  ctx.strokeStyle = `rgba(255, 255, 255, ${0.55 * a})`;
  ctx.lineWidth = Math.max(0.6, w * 0.4);
  ctx.stroke();
  ctx.restore();
}

/** Đinh tán nhỏ dọc theo đường. */
export function rivets(ctx, pts, color = 'rgba(180, 205, 230, 0.55)', r = 2.2) {
  ctx.save();
  ctx.fillStyle = color;
  for (const [x, y] of pts) {
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

/** Khe tản nhiệt phát sáng. */
export function vents(ctx, x, y, w, h, n, color = '90, 240, 255', a = 0.55) {
  const gap = h / n;
  ctx.save();
  for (let i = 0; i < n; i++) {
    const yy = y + i * gap;
    ctx.fillStyle = `rgba(4, 8, 12, 0.9)`;
    ctx.fillRect(x, yy, w, gap * 0.55);
    ctx.fillStyle = `rgba(${color}, ${a})`;
    ctx.fillRect(x + 1, yy + gap * 0.1, w - 2, gap * 0.22);
  }
  ctx.restore();
}

/** Ống tròn: sáng lệch trục trái, tối ở hai rìa → đọc ra hình trụ. */
export function tube(ctx, x0, y0, x1, y1, width, o = {}) {
  const ramp = o.ramp || STEEL;
  const dx = x1 - x0;
  const dy = y1 - y0;
  const len = Math.hypot(dx, dy) || 1;
  const nx = (-dy / len) * width * 0.5;
  const ny = (dx / len) * width * 0.5;
  const pts = [
    [x0 + nx, y0 + ny], [x1 + nx, y1 + ny],
    [x1 - nx, y1 - ny], [x0 - nx, y0 - ny],
  ];
  techPlate(ctx, pts, {
    ramp,
    light: [x0 + nx * 1.4, y0 + ny * 1.4, x1 - nx * 1.2, y1 - ny * 1.2],
    rim: o.rim || '170, 200, 225',
    edge: o.edge == null ? 3.4 : o.edge,
  });
  // đường bóng dọc ống
  ctx.save();
  ctx.globalAlpha = 0.45;
  ctx.strokeStyle = 'rgba(255,255,255,0.10)';
  ctx.lineWidth = Math.max(0.8, width * 0.12);
  ctx.beginPath();
  ctx.moveTo(x0 + nx * 0.45, y0 + ny * 0.45);
  ctx.lineTo(x1 + nx * 0.45, y1 + ny * 0.45);
  ctx.stroke();
  ctx.restore();
  return pts;
}

/** Vòng đai quanh ống. */
export function band(ctx, x, y, halfW, o = {}) {
  const h = o.h || 9;
  techPlate(ctx, [
    [x - halfW - 2, y], [x + halfW + 2, y],
    [x + halfW + 2, y + h], [x - halfW - 2, y + h],
  ], { ramp: o.ramp || STEEL, light: [x - halfW, y, x + halfW, y + h], edge: 2.4, rim: o.rim });
}

/** Sọc phản quang (specular) mảnh trên bề mặt phẳng. */
export function specular(ctx, pts, color = '255, 255, 255', a = 0.5) {
  ctx.save();
  line(ctx, pts);
  ctx.globalCompositeOperation = 'lighter';
  ctx.strokeStyle = `rgba(${color}, ${a})`;
  ctx.lineWidth = 1.2;
  ctx.stroke();
  ctx.restore();
}
