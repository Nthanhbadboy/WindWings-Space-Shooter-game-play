import * as THREE from 'three';

/**
 * Texture sinh bằng canvas lúc chạy — không thêm file ảnh nào vào repo.
 * Mọi hàm đều "lazy" + cache, và tự trả `null` khi không có DOM (test node).
 */
const cache = new Map();
/** Texture 1×1 trắng — dùng khi chạy ngoài trình duyệt (test node). */
let fallback = null;
function fallbackTex() {
  if (!fallback) {
    fallback = new THREE.DataTexture(new Uint8Array([255, 255, 255, 255]), 1, 1);
    fallback.colorSpace = THREE.SRGBColorSpace;
    fallback.needsUpdate = true;
  }
  return fallback;
}

function make(size, draw) {
  if (typeof document === 'undefined') return fallbackTex();
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const ctx = c.getContext('2d');
  if (!ctx) return fallbackTex();
  draw(ctx, size);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.needsUpdate = true;
  return t;
}

function cached(key, size, draw) {
  if (cache.has(key)) return cache.get(key);
  const t = make(size, draw);
  cache.set(key, t);
  return t;
}

const OUTLINE = '#0b1030';

/** Đạn hình học: diamond | square | triangle | hex | star | ring | cross | needle */
export function bulletTexture(shape = 'diamond') {
  return cached(`bullet:${shape}`, 128, (ctx, S) => {
    const c = S / 2;
    ctx.clearRect(0, 0, S, S);
    ctx.lineJoin = 'round';
    ctx.lineWidth = 7;
    ctx.strokeStyle = OUTLINE;

    const poly = (pts) => {
      ctx.beginPath();
      pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
      ctx.closePath();
    };

    let pts = null;
    if (shape === 'diamond') pts = [[c, 12], [S - 14, c], [c, S - 12], [14, c]];
    else if (shape === 'square') pts = [[26, 26], [S - 26, 26], [S - 26, S - 26], [26, S - 26]];
    else if (shape === 'triangle') pts = [[c, 10], [S - 16, S - 20], [16, S - 20]];
    else if (shape === 'hex') {
      pts = [];
      for (let i = 0; i < 6; i++) {
        const a = (i / 6) * Math.PI * 2 + Math.PI / 6;
        pts.push([c + Math.cos(a) * (c - 14), c + Math.sin(a) * (c - 14)]);
      }
    } else if (shape === 'star') {
      pts = [];
      for (let i = 0; i < 10; i++) {
        const a = (i / 10) * Math.PI * 2 - Math.PI / 2;
        const r = i % 2 ? (c - 44) : (c - 12);
        pts.push([c + Math.cos(a) * r, c + Math.sin(a) * r]);
      }
    } else if (shape === 'cross') {
      const w = 16;
      pts = [[c - w, 12], [c + w, 12], [c + w, c - w], [S - 12, c - w], [S - 12, c + w],
        [c + w, c + w], [c + w, S - 12], [c - w, S - 12], [c - w, c + w], [12, c + w],
        [12, c - w], [c - w, c - w]];
    } else if (shape === 'needle') {
      pts = [[c, 6], [c + 17, S * 0.55], [c, S - 8], [c - 17, S * 0.55]];
    }

    ctx.shadowColor = '#ffffff';
    ctx.shadowBlur = 22;

    if (shape === 'ring') {
      ctx.beginPath();
      ctx.arc(c, c, c - 20, 0, Math.PI * 2);
      ctx.lineWidth = 16;
      ctx.strokeStyle = '#ffffff';
      ctx.stroke();
      ctx.shadowBlur = 0;
      ctx.lineWidth = 4;
      ctx.strokeStyle = OUTLINE;
      ctx.beginPath();
      ctx.arc(c, c, c - 12, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(c, c, c - 28, 0, Math.PI * 2);
      ctx.stroke();
      return;
    }

    if (pts) {
      poly(pts);
      const g = ctx.createLinearGradient(0, 0, 0, S);
      g.addColorStop(0, '#ffffff');
      g.addColorStop(0.55, '#ffffff');
      g.addColorStop(1, '#e6f1ff');
      ctx.fillStyle = g;
      ctx.fill();
      ctx.shadowBlur = 0;
      ctx.stroke();
      // lõi sáng
      ctx.globalAlpha = 0.9;
      ctx.beginPath();
      ctx.arc(c, c, S * 0.11, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.fill();
      ctx.globalAlpha = 1;
    }
  });
}

/** Vệt chém hình lưỡi liềm (dùng cho đòn cận chiến của boss). */
export function slashTexture() {
  return cached('slash', 512, (ctx, S) => {
    const c = S / 2;
    ctx.clearRect(0, 0, S, S);
    ctx.translate(c, c);

    // cung tròn dày, hai đầu vuốt nhọn
    const drawArc = (radius, width, color, blur) => {
      ctx.beginPath();
      ctx.lineWidth = width;
      ctx.lineCap = 'round';
      ctx.strokeStyle = color;
      ctx.shadowColor = color;
      ctx.shadowBlur = blur;
      ctx.arc(0, 0, radius, -Math.PI * 0.86, -Math.PI * 0.14);
      ctx.stroke();
    };

    drawArc(S * 0.34, S * 0.16, 'rgba(255,120,60,0.55)', 60);
    drawArc(S * 0.35, S * 0.09, 'rgba(255,190,90,0.9)', 40);
    drawArc(S * 0.36, S * 0.035, '#fffdf2', 24);

    // đầu lưỡi sáng
    ctx.shadowBlur = 40;
    ctx.shadowColor = '#fff3c4';
    ctx.beginPath();
    ctx.arc(0, 0, S * 0.36, -Math.PI * 0.82, -Math.PI * 0.18);
    ctx.lineWidth = 6;
    ctx.strokeStyle = '#ffffff';
    ctx.stroke();
  });
}

/** Tinh vân mềm (nhiều đám mây tròn chồng nhau + hạt bụi) — dùng cho lớp nền xa. */
export function nebulaTexture(seed = 1) {
  return cached(`nebula:${seed}`, 512, (ctx, S) => {
    let st = seed * 9301 + 49297;
    const rnd = () => {
      st = (st * 9301 + 49297) % 233280;
      return st / 233280;
    };
    ctx.clearRect(0, 0, S, S);
    ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 26; i++) {
      const x = S * (0.15 + rnd() * 0.7);
      const y = S * (0.15 + rnd() * 0.7);
      const r = S * (0.10 + rnd() * 0.22);
      const g = ctx.createRadialGradient(x, y, 0, x, y, r);
      const hue = 200 + rnd() * 90;      // xanh lam → tím
      const a = 0.05 + rnd() * 0.10;
      g.addColorStop(0, `hsla(${hue}, 90%, 72%, ${a})`);
      g.addColorStop(0.55, `hsla(${hue}, 88%, 58%, ${a * 0.5})`);
      g.addColorStop(1, `hsla(${hue}, 80%, 40%, 0)`);
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }
    // hạt sáng li ti
    for (let i = 0; i < 160; i++) {
      const x = rnd() * S;
      const y = rnd() * S;
      const r = rnd() * 1.4 + 0.3;
      ctx.fillStyle = `rgba(220,236,255,${0.15 + rnd() * 0.4})`;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalCompositeOperation = 'source-over';
    // vignette để sprite hoà vào nền, không thấy viền vuông
    const vg = ctx.createRadialGradient(S / 2, S / 2, S * 0.18, S / 2, S / 2, S * 0.5);
    vg.addColorStop(0, 'rgba(0,0,0,0)');
    vg.addColorStop(1, 'rgba(0,0,0,1)');
    ctx.globalCompositeOperation = 'destination-out';
    ctx.fillStyle = vg;
    ctx.fillRect(0, 0, S, S);
    ctx.globalCompositeOperation = 'source-over';
  });
}

/** Hạt bụi tròn mềm. */
export function moteTexture() {
  return cached('mote', 64, (ctx, S) => {
    const g = ctx.createRadialGradient(S / 2, S / 2, 0, S / 2, S / 2, S / 2);
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(0.35, 'rgba(214,238,255,0.75)');
    g.addColorStop(1, 'rgba(160,200,255,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, S, S);
  });
}

/** Vệt sáng dọc (bụi bay xuống tạo cảm giác lao đi). */
export function streakTexture() {
  return cached('streak', 64, (ctx, S) => {
    const g = ctx.createLinearGradient(0, 0, 0, S);
    g.addColorStop(0, 'rgba(255,255,255,0)');
    g.addColorStop(0.45, 'rgba(220,240,255,0.95)');
    g.addColorStop(0.6, 'rgba(255,255,255,0.75)');
    g.addColorStop(1, 'rgba(180,215,255,0)');
    ctx.fillStyle = g;
    const w = S * 0.22;
    ctx.fillRect((S - w) / 2, 0, w, S);
  });
}

/** Vệt chém hình trăng lưỡi liềm — dùng cho đòn chém của boss. */
export function slashArcTexture() {
  return cached('slashArc', 512, (ctx, S) => {
    const c = S / 2;
    const rOut = S * 0.47;
    const rIn = S * 0.29;
    const a0 = -Math.PI * 0.46;
    const a1 = Math.PI * 0.46;
    ctx.save();
    ctx.shadowColor = 'rgba(255,170,80,0.95)';
    ctx.shadowBlur = S * 0.09;
    const g = ctx.createLinearGradient(0, 0, S, S);
    g.addColorStop(0, 'rgba(255,255,255,0.95)');
    g.addColorStop(0.45, 'rgba(255,226,160,0.98)');
    g.addColorStop(1, 'rgba(255,110,50,0.55)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(c, c, rOut, a0, a1);
    ctx.arc(c, c, rIn, a1, a0, true);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
    // lõi trắng mảnh ở giữa cung
    ctx.strokeStyle = 'rgba(255,255,255,0.95)';
    ctx.lineWidth = S * 0.035;
    ctx.beginPath();
    ctx.arc(c, c, (rOut + rIn) / 2, a0 * 0.94, a1 * 0.94);
    ctx.stroke();
    // tia lửa văng
    ctx.fillStyle = 'rgba(255,240,200,0.8)';
    for (let i = 0; i < 26; i++) {
      const a = a0 + Math.random() * (a1 - a0);
      const r = rOut + Math.random() * S * 0.05;
      ctx.beginPath();
      ctx.arc(c + Math.cos(a) * r, c + Math.sin(a) * r, 1 + Math.random() * 3, 0, Math.PI * 2);
      ctx.fill();
    }
  });
}

/** Quầng sáng tròn mềm (nền, hào quang, lõi boss). */
export function glowTexture() {
  return cached('glow', 256, (ctx, S) => {
    const g = ctx.createRadialGradient(S / 2, S / 2, 0, S / 2, S / 2, S / 2);
    g.addColorStop(0, 'rgba(255,255,255,0.95)');
    g.addColorStop(0.28, 'rgba(190,225,255,0.42)');
    g.addColorStop(0.62, 'rgba(120,170,255,0.13)');
    g.addColorStop(1, 'rgba(80,120,255,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, S, S);
  });
}

/** Đốm sao 4 cánh lấp lánh. */
export function sparkleTexture() {
  return cached('sparkle', 128, (ctx, S) => {
    const c = S / 2;
    const g = ctx.createRadialGradient(c, c, 0, c, c, c);
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(0.22, 'rgba(220,240,255,0.55)');
    g.addColorStop(1, 'rgba(160,200,255,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, S, S);
    ctx.fillStyle = 'rgba(255,255,255,0.95)';
    ctx.beginPath();
    ctx.moveTo(c, 4); ctx.lineTo(c + 4, c - 4); ctx.lineTo(S - 4, c);
    ctx.lineTo(c + 4, c + 4); ctx.lineTo(c, S - 4); ctx.lineTo(c - 4, c + 4);
    ctx.lineTo(4, c); ctx.lineTo(c - 4, c - 4);
    ctx.closePath();
    ctx.fill();
  });
}

/** Vỏ kim loại của trạm không gian khổng lồ (panel + đinh tán + vết xước). */
export function hullTexture() {
  return cached('hull', 512, (ctx, S) => {
    ctx.fillStyle = '#161f2e';
    ctx.fillRect(0, 0, S, S);
    const cols = 4;
    const rows = 4;
    const w = S / cols;
    const h = S / rows;
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const v = 20 + Math.random() * 12;
        ctx.fillStyle = `rgb(${Math.round(v + 6)},${Math.round(v + 14)},${Math.round(v + 28)})`;
        ctx.fillRect(x * w + 2, y * h + 2, w - 4, h - 4);
        // gờ sáng phía trên + bóng phía dưới → khối kim loại
        ctx.fillStyle = 'rgba(130,170,220,0.12)';
        ctx.fillRect(x * w + 2, y * h + 2, w - 4, 3);
        ctx.fillStyle = 'rgba(0,0,0,0.38)';
        ctx.fillRect(x * w + 2, y * h + h - 6, w - 4, 4);
        // đinh tán hai bên
        ctx.fillStyle = 'rgba(160,195,235,0.20)';
        for (let i = 0; i < 3; i++) {
          const px = x * w + 7 + Math.random() * (w - 14);
          const py = y * h + 9 + Math.random() * (h - 18);
          ctx.beginPath();
          ctx.arc(px, py, 2, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }
    // vết xước chéo
    ctx.strokeStyle = 'rgba(170,210,255,0.07)';
    ctx.lineWidth = 1.5;
    for (let i = 0; i < 14; i++) {
      const x = Math.random() * S;
      const y = Math.random() * S;
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x + 20 + Math.random() * 40, y + 8 + Math.random() * 20);
      ctx.stroke();
    }
  });
}

export const SHAPES = ['diamond', 'square', 'triangle', 'hex', 'star', 'ring', 'needle'];
