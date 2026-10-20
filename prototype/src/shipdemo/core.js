/**
 * Lõi hoạt cảnh 2D — khung cảnh + pha bắn, tàu do từng module trong `ships/` vẽ.
 *
 * Nguyên tắc: mọi thứ là hình 2D, chỉ trượt/xoay/co giãn trong mặt phẳng.
 * Laser luôn xuất phát từ ĐẦU NÒNG do chính tàu khai báo (`ship.muzzles()`),
 * nên không có tia nào mọc ra từ hư không.
 *
 * File này không đụng tới DOM: chạy được ở trình duyệt và ở node (xuất ảnh/GIF).
 */

import { clamp01, drawStars, glowDot, laserPath } from './fx.js';
import { omen } from './ships/omen.js';
import { biomech } from './ships/biomech.js';
import { vertebra } from './ships/vertebra.js';

export const SHIPS = [omen, biomech, vertebra];
export const shipById = (id) => SHIPS.find((s) => s.id === id) || omen;

/** Thời lượng từng đoạn của một phát bắn. */
export const FIRE_TIMELINE = { windup: 0.55, fire: 0.5, recover: 0.75 };
export const FIRE_TOTAL = FIRE_TIMELINE.windup + FIRE_TIMELINE.fire + FIRE_TIMELINE.recover;

/** Không bắn: chỉ thở + lửa nhấp nháy. */
export function idlePhase() {
  return { stage: 'idle', k: 0, wing: 0, charge: 0, fire: 0, recoil: 0 };
}

/**
 * Trạng thái kể từ lúc bấm bắn (giây).
 * gồng → khai hỏa → hồi.
 */
export function firePhase(elapsed) {
  const { windup, fire, recover } = FIRE_TIMELINE;
  if (elapsed < 0) return idlePhase();
  if (elapsed < windup) {
    const k = elapsed / windup;
    const e = clamp01(k) * clamp01(k) * (3 - 2 * clamp01(k));
    return { stage: 'windup', k, wing: e, charge: e, fire: 0, recoil: 0 };
  }
  if (elapsed < windup + fire) {
    const k = (elapsed - windup) / fire;
    return {
      stage: 'fire',
      k,
      // cánh GIỮ tư thế chụm thêm một nhịp để quả cầu không rời mũi,
      // rồi mới hạ xuống khi hết phát bắn
      wing: Math.max(-0.5, 1 - k * 1.5),
      charge: Math.max(0, 1 - k * 1.8),
      fire: k < 0.68 ? 1 : Math.max(0, 1 - (k - 0.68) / 0.32),
      recoil: k < 0.16 ? k / 0.16 : Math.max(0, 1 - (k - 0.16) / 0.45),
    };
  }
  const k = (elapsed - windup - fire) / recover;
  return { stage: 'recover', k: Math.min(1, k), wing: 0, charge: 0, fire: 0, recoil: 0 };
}

/** Ảnh có vẽ được không (HTMLImageElement, ImageBitmap, canvas…). */
export function canDraw(im) {
  if (!im) return false;
  const w = im.naturalWidth !== undefined ? im.naturalWidth : im.width;
  const h = im.naturalHeight !== undefined ? im.naturalHeight : im.height;
  return w > 0 && h > 0;
}

const BASE = 512;

/**
 * Vẽ toàn bộ khung hình.
 * @param {CanvasRenderingContext2D} ctx
 * @param {number} W rộng (px CSS)
 * @param {number} H cao (px CSS)
 * @param {number} t thời gian (giây)
 * @param {object} img ảnh tách rời (chỉ tàu dùng ảnh mới cần)
 * @param {{skeleton?:boolean, phase?:object, art?:boolean, ship?:string|object}} opts
 */
export function drawScene(ctx, W, H, t, img = {}, opts = {}) {
  const ph = opts.phase || idlePhase();
  const ship = typeof opts.ship === 'string' || !opts.ship ? shipById(opts.ship) : opts.ship;
  const skeleton = !!opts.skeleton;

  drawStars(ctx, W, H, t, 1);

  // ------------------------------------------------ kích thước & vị trí
  const R = (W / H > 1.5 ? H : W) * 0.82;
  const s = R / BASE;
  const bob = Math.sin(t * 1.9) * 2.4 * Math.min(W, H) * 0.01;
  const lift = ph.charge * 10 + -ph.recoil * 9;
  const cx = W / 2;
  const cy = H * 0.52 + bob + lift * (H / 600);
  const tilt = Math.sin(t * 1.15) * 0.012 - ph.recoil * 0.01;

  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(tilt);

  // ------------------------------------------------ bóng đổ (giả 3D)
  ctx.save();
  ctx.globalAlpha = 0.35 + ph.charge * 0.15;
  const sh = ctx.createRadialGradient(0, BASE * s * 0.46, 0, 0, BASE * s * 0.46, BASE * s * 0.42);
  sh.addColorStop(0, 'rgba(10, 4, 30, 0.85)');
  sh.addColorStop(1, 'rgba(10, 4, 30, 0)');
  ctx.fillStyle = sh;
  ctx.beginPath();
  ctx.ellipse(0, BASE * s * 0.47, BASE * s * 0.34, BASE * s * 0.1, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // ------------------------------------------------ tàu tự vẽ (thân, cánh, pháo, lửa)
  ship.draw(ctx, { s, t, ph, img, art: opts.art !== false });

  // ------------------------------------------------ đầu nòng: quầng năng lượng
  const muzzles = ship.muzzles(s, t, ph);
  const [lr, lg, lb] = ship.laserTint || [196, 150, 255];

  if (ph.charge > 0.03) {
    // quầng gồng quanh tàu
    const glowR = (86 + 64 * ph.charge) * s;
    const gg = ctx.createRadialGradient(0, 0, 0, 0, 0, glowR);
    gg.addColorStop(0, `rgba(${lr}, ${lg}, ${lb}, ${0.16 * ph.charge})`);
    gg.addColorStop(1, `rgba(${lr}, ${lg}, ${lb}, 0)`);
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = gg;
    ctx.beginPath();
    ctx.arc(0, 0, glowR, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    for (const m of muzzles) {
      // quầng gồng ở đầu nòng: vừa phải, vì tàu đã tự vẽ quả cầu/lõi của nó
      glowDot(ctx, m.x, m.y,
        (11 + 13 * ph.charge) * s,
        `rgba(255,255,255,${0.3 * ph.charge})`,
        `rgba(${lr},${lg},${lb},${0.18 * ph.charge})`,
        `rgba(${lr},${lg},${lb},0)`);
    }
  }

  // ------------------------------------------------ laser bắn từ đúng đầu nòng
  if (ph.fire > 0.02) {
    const len = H * 1.35;
    const burst = Math.min(1, ph.fire * 1.6);
    const width = Math.max(4, H * 0.012);
    for (const m of muzzles) {
      const dx = Math.sin(m.angle || 0);
      const dy = -Math.cos(m.angle || 0);
      const tipX = m.x + dx * len * (0.35 + 0.65 * burst);
      const tipY = m.y + dy * len * (0.35 + 0.65 * burst);
      ctx.save();
      ctx.globalCompositeOperation = 'lighter';
      laserPath(ctx, m.x, m.y, tipX, tipY, width * 2.6, `rgba(${lr}, ${lg}, ${lb}, ${0.22 * ph.fire})`, 0);
      laserPath(ctx, m.x, m.y, tipX, tipY, width, `rgba(${lr}, ${lg}, ${lb}, ${0.7 * ph.fire})`, 0.95 * ph.fire);
      ctx.restore();

      // chớp đầu nòng: đúng 3 hình như sprite tham khảo (to → vừa → tắt)
      const step = ph.stage === 'fire'
        ? (ph.k < 0.1 ? 0 : ph.k < 0.24 ? 1 : ph.k < 0.4 ? 2 : -1)
        : -1;
      if (step >= 0) {
        const F = [
          { r: 1.6, a: 1.0 },
          { r: 1.05, a: 0.82 },
          { r: 0.62, a: 0.55 },
        ][step];
        glowDot(ctx, m.x, m.y,
          (20 + 22 * F.r) * s,
          `rgba(255,255,255,${0.7 * F.a})`,
          `rgba(${lr},${lg},${lb},${0.34 * F.a})`,
          `rgba(${lr},${lg},${lb},0)`);
      }
    }
  }

  ctx.restore();

  // ------------------------------------------------ khung xương (tuỳ chọn)
  if (skeleton && ship.skeleton) {
    ctx.save();
    ctx.translate(cx, cy);
    ship.skeleton(ctx, s, t, ph);
    ctx.restore();
  }
}
