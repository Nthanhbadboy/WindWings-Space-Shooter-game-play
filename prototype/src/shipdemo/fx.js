/**
 * Hiệu ứng dùng chung cho cả hai tàu: nền sao, lửa đuôi 3 hình, tia laser.
 * Không phụ thuộc DOM, vẽ được bằng canvas 2D của trình duyệt lẫn node.
 */

export const FLAME_FRAMES = [0.74, 1.0, 0.84];
export const FLAME_FPS = 15;

export const clamp01 = (v) => Math.max(0, Math.min(1, v));

/** ease in-out mượt */
export const smooth = (t) => {
  const k = clamp01(t);
  return k * k * (3 - 2 * k);
};

/** số 0..1 có gia tốc nhẹ ở hai đầu (cảm giác servo) */
export const servo = (t) => {
  const k = clamp01(t);
  return k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
};

/** chỉ số hình lửa 0..2, an toàn cả khi t âm */
export const flameFrame = (t, offset = 0) => (((Math.floor(t * FLAME_FPS) + offset) % 3) + 3) % 3;

export function drawStars(ctx, W, H, t, speed = 1) {
  const g = ctx.createRadialGradient(W * 0.5, H * 0.42, 0, W * 0.5, H * 0.42, Math.max(W, H) * 0.78);
  g.addColorStop(0, '#101a3f');
  g.addColorStop(0.55, '#080d24');
  g.addColorStop(1, '#03060f');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);

  const blobs = [
    [0.18, 0.2, 0.42, 'rgba(90, 60, 190, 0.20)'],
    [0.82, 0.34, 0.34, 'rgba(30, 120, 190, 0.16)'],
    [0.5, 0.86, 0.5, 'rgba(150, 60, 160, 0.12)'],
  ];
  for (const [bx, by, br, col] of blobs) {
    const rg = ctx.createRadialGradient(W * bx, H * by, 0, W * bx, H * by, W * br);
    rg.addColorStop(0, col);
    rg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = rg;
    ctx.fillRect(0, 0, W, H);
  }

  const n = 42;
  for (let i = 0; i < n; i++) {
    const seed = i * 78.233;
    const x = (Math.sin(seed) * 0.5 + 0.5) * W;
    const span = H + 80;
    const y = ((Math.cos(seed * 1.7) * 0.5 + 0.5) * span + t * (26 + (i % 5) * 11) * speed) % span;
    const r = 0.6 + (i % 4) * 0.45;
    const a = 0.25 + (i % 3) * 0.2;
    ctx.fillStyle = `rgba(200, 230, 255, ${a})`;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }
}

/** 3 hình lửa — thuần vector, không hạt. */
export function drawFlame(ctx, x, y, w, len, frame, throttle, palette = {}) {
  const P = {
    glow: 'rgba(190, 160, 255, 0.42)',
    glowMid: 'rgba(120, 90, 255, 0.16)',
    glowOut: 'rgba(60, 40, 180, 0)',
    outer: 'rgba(118, 92, 255, 0.8)',
    mid: 'rgba(198, 178, 255, 0.95)',
    core: 'rgba(255, 255, 255, 0.95)',
    spark: 'rgba(170, 140, 255, 0.5)',
    ...palette,
  };
  const f = FLAME_FRAMES[((frame % 3) + 3) % 3] * throttle;
  const L = len * f;
  const g = ctx.createRadialGradient(x, y + L * 0.25, 0, x, y + L * 0.25, L * 0.85 + w * 1.2);
  g.addColorStop(0, P.glow);
  g.addColorStop(0.4, P.glowMid);
  g.addColorStop(1, P.glowOut);
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.ellipse(x, y + L * 0.3, L * 0.55 + w, L * 0.85, 0, 0, Math.PI * 2);
  ctx.fill();

  const tongue = (scaleW, scaleL, color) => {
    const ww = w * scaleW;
    const ll = L * scaleL;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(x - ww, y);
    ctx.quadraticCurveTo(x - ww * 0.55, y + ll * 0.62, x, y + ll);
    ctx.quadraticCurveTo(x + ww * 0.55, y + ll * 0.62, x + ww, y);
    ctx.closePath();
    ctx.fill();
  };
  tongue(1, 0.78, P.outer);
  tongue(0.56, 1, P.mid);
  tongue(0.26, 1.05, P.core);
  if (frame % 3 !== 2) {
    ctx.fillStyle = P.spark;
    const dy = frame % 3 === 0 ? 1.05 : 1.22;
    ctx.beginPath();
    ctx.ellipse(x - w * 0.3, y + L * dy, w * 0.26, L * 0.12, 0, 0, Math.PI * 2);
    ctx.fill();
    if (frame % 3 === 1) {
      ctx.beginPath();
      ctx.ellipse(x + w * 0.4, y + L * 0.98, w * 0.2, L * 0.09, 0, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

export function laserPath(ctx, x0, y0, x1, y1, width, color, coreAlpha) {
  ctx.lineCap = 'round';
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.beginPath();
  ctx.moveTo(x0, y0);
  ctx.lineTo(x1, y1);
  ctx.stroke();
  if (coreAlpha > 0) {
    ctx.strokeStyle = `rgba(255,255,255,${coreAlpha})`;
    ctx.lineWidth = Math.max(1, width * 0.32);
    ctx.stroke();
  }
}

/** quầng sáng tròn (dùng cho đầu nòng, lõi năng lượng) */
export function glowDot(ctx, x, y, r, inner, mid, outer) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, Math.max(0.001, r));
  g.addColorStop(0, inner);
  g.addColorStop(0.45, mid);
  g.addColorStop(1, outer);
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}
