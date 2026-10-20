/**
 * Dựng ảnh xem trước của mô hình tàu bằng rasterizer phần mềm (không cần trình duyệt).
 *
 *   node tools/render_ship.mjs
 *
 * - Camera trực giao đặt trên đỉnh, up = -Z → đúng hình chiếu đứng nhìn từ trên xuống.
 * - Xuất 8 khung (cánh vỗ + bắn + lửa đuôi) + một ảnh tiếp xúc 4×2 vào tools/ship_preview/.
 */
import * as THREE from 'three';
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { buildShip } from '../src/shipmodel.js';

/* --------------------------------------------------------------- PNG */
const CRC = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();
const crc32 = (buf) => {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = CRC[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
};
const chunk = (type, data) => {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const td = Buffer.concat([Buffer.from(type, 'ascii'), data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(td), 0);
  return Buffer.concat([len, td, crc]);
};
function encodePNG(w, h, rgb) {
  const raw = Buffer.alloc((w * 3 + 1) * h);
  for (let y = 0; y < h; y++) {
    raw[y * (w * 3 + 1)] = 0;
    Buffer.from(rgb.buffer, rgb.byteOffset + y * w * 3, w * 3).copy(raw, y * (w * 3 + 1) + 1);
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0);
  ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8;
  ihdr[9] = 2;
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk('IHDR', ihdr),
    chunk('IDAT', zlib.deflateSync(raw, { level: 9 })),
    chunk('IEND', Buffer.alloc(0)),
  ]);
}

/* ----------------------------------------------------------- renderer */
const LIGHT = new THREE.Vector3(-0.52, 0.78, -0.46).normalize();
const tmpA = new THREE.Vector3();
const tmpB = new THREE.Vector3();
const tmpC = new THREE.Vector3();

function srgb(c) {
  const hex = c.getHex();
  return [((hex >> 16) & 255) / 255, ((hex >> 8) & 255) / 255, (hex & 255) / 255];
}

/** Sao nền cố định để 8 khung không bị "nhảy" sao. */
function makeStars(count) {
  let seed = 20261020;
  const rnd = () => {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    return seed / 4294967296;
  };
  return Array.from({ length: count }, () => ({
    x: rnd(), y: rnd(), r: 0.35 + rnd() * 0.95, a: 0.18 + rnd() * 0.72, blue: rnd(),
  }));
}
const STARS = makeStars(190);

function renderFrame(ship, { size = 640, supersample = 2 } = {}) {
  const W = size * supersample;
  const H = size * supersample;
  const pix = new Uint8Array(W * H * 3);
  const zbuf = new Float32Array(W * H).fill(Infinity);

  // nền: vũ trụ xanh đêm + quầng sáng sau tàu + sao
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const nx = (x / W - 0.5) * 2;
      const ny = (y / H - 0.5) * 2;
      const d = Math.min(1, Math.sqrt(nx * nx * 0.8 + ny * ny));
      const glow = Math.pow(1 - d, 2.6);
      const i = (y * W + x) * 3;
      pix[i] = Math.round(7 + glow * 12);
      pix[i + 1] = Math.round(12 + glow * 30);
      pix[i + 2] = Math.round(26 + glow * 62);
    }
  }
  for (const s of STARS) {
    const sx = s.x * W;
    const sy = s.y * H;
    const rad = s.r * supersample;
    const bright = s.a;
    const tint = s.blue > 0.6 ? [0.78, 0.9, 1.0] : [1.0, 0.95, 0.85];
    const minX = Math.max(0, Math.floor(sx - rad));
    const maxX = Math.min(W - 1, Math.ceil(sx + rad));
    const minY = Math.max(0, Math.floor(sy - rad));
    const maxY = Math.min(H - 1, Math.ceil(sy + rad));
    for (let y = minY; y <= maxY; y++) {
      for (let x = minX; x <= maxX; x++) {
        const dx = x + 0.5 - sx;
        const dy = y + 0.5 - sy;
        const fall = Math.max(0, 1 - Math.sqrt(dx * dx + dy * dy) / rad);
        if (fall <= 0) continue;
        const a = bright * fall * fall * 0.9;
        const i = (y * W + x) * 3;
        pix[i] = Math.min(255, pix[i] + bright * 255 * fall * 0.8 * tint[0]);
        pix[i + 1] = Math.min(255, pix[i + 1] + bright * 255 * fall * 0.8 * tint[1]);
        pix[i + 2] = Math.min(255, pix[i + 2] + bright * 255 * fall * 0.8 * tint[2]);
        void a;
      }
    }
  }

  const HALF = 3.12;
  const cam = new THREE.OrthographicCamera(-HALF, HALF, HALF, -HALF, 0.1, 100);
  cam.position.set(0, 12, 0.3);
  cam.up.set(0, 0, -1);
  cam.lookAt(0, 0, 0.3);
  cam.updateMatrixWorld(true);
  cam.updateProjectionMatrix();
  const vp = new THREE.Matrix4().multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse);

  const meshes = [];
  ship.root.traverse((o) => {
    if (o.isMesh && o.visible) meshes.push(o);
  });
  const opaque = meshes.filter((m) => !isTransparent(m));
  const clear = meshes.filter(isTransparent);

  function isTransparent(mesh) {
    if (Array.isArray(mesh.material)) return mesh.material.some((m) => m.transparent);
    return !!mesh.material.transparent;
  }

  const P = new THREE.Vector3();
  const Q = new THREE.Vector3();
  const R = new THREE.Vector3();
  const N = new THREE.Vector3();

  const drawList = (list, blend = false) => {
    for (const mesh of list) {
      const geo = mesh.geometry;
      const pos = geo.attributes.position;
      if (!pos) continue;
      const idx = geo.index;
      const total = idx ? idx.count : pos.count;
      const matArr = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      const groups = geo.groups.length
        ? geo.groups
        : [{ start: 0, count: total, materialIndex: 0 }];

      for (const grp of groups) {
        const material = matArr[grp.materialIndex] ?? matArr[0];
        if (!material || material.visible === false) continue;
        const col = srgb(material.color);
        const em = material.emissive ? srgb(material.emissive) : [0, 0, 0];
        const emI = material.emissiveIntensity ?? 0;
        const basic = !material.emissive;
        const alpha = material.opacity ?? 1;
        const additive = material.blending === THREE.AdditiveBlending;
        if (alpha <= 0.002) continue;
        const start = grp.start;
        const end = Math.min(total, grp.start + grp.count);

        for (let t = start; t < end; t += 3) {
          const i0 = idx ? idx.getX(t) : t;
          const i1 = idx ? idx.getX(t + 1) : t + 1;
          const i2 = idx ? idx.getX(t + 2) : t + 2;
          P.fromBufferAttribute(pos, i0).applyMatrix4(mesh.matrixWorld);
          Q.fromBufferAttribute(pos, i1).applyMatrix4(mesh.matrixWorld);
          R.fromBufferAttribute(pos, i2).applyMatrix4(mesh.matrixWorld);

          N.copy(Q).sub(P).cross(tmpC.copy(R).sub(P)).normalize();
          const lam = Math.abs(N.dot(LIGHT));
          const shade = basic ? 1 : 0.4 + 0.64 * lam;

          P.applyMatrix4(vp);
          Q.applyMatrix4(vp);
          R.applyMatrix4(vp);
          const x0 = (P.x * 0.5 + 0.5) * W;
          const y0 = (1 - (P.y * 0.5 + 0.5)) * H;
          const x1 = (Q.x * 0.5 + 0.5) * W;
          const y1 = (1 - (Q.y * 0.5 + 0.5)) * H;
          const x2 = (R.x * 0.5 + 0.5) * W;
          const y2 = (1 - (R.y * 0.5 + 0.5)) * H;
          const minX = Math.max(0, Math.floor(Math.min(x0, x1, x2)));
          const maxX = Math.min(W - 1, Math.ceil(Math.max(x0, x1, x2)));
          const minY = Math.max(0, Math.floor(Math.min(y0, y1, y2)));
          const maxY = Math.min(H - 1, Math.ceil(Math.max(y0, y1, y2)));
          if (minX > maxX || minY > maxY) continue;

          const area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0);
          if (Math.abs(area) < 1e-9) continue;
          const inv = 1 / area;

          const cr = Math.min(1, col[0] * shade + em[0] * emI);
          const cg = Math.min(1, col[1] * shade + em[1] * emI);
          const cb = Math.min(1, col[2] * shade + em[2] * emI);

          for (let y = minY; y <= maxY; y++) {
            for (let x = minX; x <= maxX; x++) {
              const px = x + 0.5;
              const py = y + 0.5;
              const w0 = ((x1 - px) * (y2 - py) - (x2 - px) * (y1 - py)) * inv;
              const w1 = ((x2 - px) * (y0 - py) - (x0 - px) * (y2 - py)) * inv;
              const w2 = 1 - w0 - w1;
              if (w0 < 0 || w1 < 0 || w2 < 0) continue;
              const z = w0 * P.z + w1 * Q.z + w2 * R.z;
              const o = y * W + x;
              if (blend) {
                if (z > zbuf[o] + 1e-4) continue;
                const dst = o * 3;
                if (additive) {
                  pix[dst] = Math.min(255, pix[dst] + cr * 255 * alpha);
                  pix[dst + 1] = Math.min(255, pix[dst + 1] + cg * 255 * alpha);
                  pix[dst + 2] = Math.min(255, pix[dst + 2] + cb * 255 * alpha);
                } else {
                  pix[dst] = Math.min(255, pix[dst] * (1 - alpha) + cr * 255 * alpha);
                  pix[dst + 1] = Math.min(255, pix[dst + 1] * (1 - alpha) + cg * 255 * alpha);
                  pix[dst + 2] = Math.min(255, pix[dst + 2] * (1 - alpha) + cb * 255 * alpha);
                }
              } else {
                if (z >= zbuf[o]) continue;
                zbuf[o] = z;
                const dst = o * 3;
                pix[dst] = cr * 255;
                pix[dst + 1] = cg * 255;
                pix[dst + 2] = cb * 255;
              }
            }
          }
        }
      }
    }
  };

  drawList(opaque, false);
  drawList(clear, true);

  // hạ mẫu (khử răng cưa)
  const out = new Uint8Array(size * size * 3);
  const n = supersample * supersample;
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      let r = 0;
      let g = 0;
      let b = 0;
      for (let sy = 0; sy < supersample; sy++) {
        for (let sx = 0; sx < supersample; sx++) {
          const i = ((y * supersample + sy) * W + (x * supersample + sx)) * 3;
          r += pix[i];
          g += pix[i + 1];
          b += pix[i + 2];
        }
      }
      const o = (y * size + x) * 3;
      out[o] = r / n;
      out[o + 1] = g / n;
      out[o + 2] = b / n;
    }
  }
  return { png: encodePNG(size, size, out), raw: out, size };
}

/* ---------------------------------------------------------------- main */
const outDir = path.join(process.cwd(), 'tools', 'ship_preview');
fs.mkdirSync(outDir, { recursive: true });

const ship = buildShip();
ship.root.updateMatrixWorld(true);

const frames = 8;
const SIZE = 640;
const results = [];
for (let i = 0; i < frames; i++) {
  const t = (i / frames) * 1.2;
  const firing = i % 2 === 0;
  const pose = { flap: 1, throttle: 0.85, firing, bank: Math.sin(t * 1.4) * 0.35 };
  // vài bước làm ấm để chớp đầu nòng / độ giật ổn định trước khi chụp
  for (let warm = 0; warm < 8; warm++) ship.update(1 / 60, t, pose);
  const res = renderFrame(ship, { size: SIZE });
  const file = path.join(outDir, `frame_${String(i).padStart(2, '0')}.png`);
  fs.writeFileSync(file, res.png);
  results.push(res);
}
console.log('frames:', results.length, '→', outDir);

// ảnh tiếp xúc 4×2
const gap = 12;
const sheetW = 4 * SIZE + 5 * gap;
const sheetH = 2 * SIZE + 3 * gap;
const sheet = new Uint8Array(sheetW * sheetH * 3);
for (let i = 0; i < sheet.length; i += 3) {
  sheet[i] = 6; sheet[i + 1] = 10; sheet[i + 2] = 22;
}
for (let i = 0; i < results.length; i++) {
  const col = i % 4;
  const row = Math.floor(i / 4);
  const ox = gap + col * (SIZE + gap);
  const oy = gap + row * (SIZE + gap);
  const raw = results[i].raw;
  for (let y = 0; y < SIZE; y++) {
    for (let x = 0; x < SIZE; x++) {
      const s = (y * SIZE + x) * 3;
      const d = ((oy + y) * sheetW + ox + x) * 3;
      sheet[d] = raw[s];
      sheet[d + 1] = raw[s + 1];
      sheet[d + 2] = raw[s + 2];
    }
  }
  // viền cyan mảnh
  for (let x = 0; x < SIZE; x++) {
    for (const yy of [oy - 1, oy + SIZE]) {
      if (yy < 0 || yy >= sheetH) continue;
      const d = (yy * sheetW + ox + x) * 3;
      sheet[d] = 34; sheet[d + 1] = 92; sheet[d + 2] = 120;
    }
  }
}
fs.writeFileSync(path.join(outDir, 'sheet.png'), encodePNG(sheetW, sheetH, sheet));
console.log('sheet:', path.join(outDir, 'sheet.png'));
