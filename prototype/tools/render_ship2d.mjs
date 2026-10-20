/**
 * Xuất ảnh/GIF xem trước của bản thử tàu 2D — không cần trình duyệt.
 *
 *   npm run render:ship2d        (cần: npm i -D @napi-rs/canvas)
 *
 * - Vẽ 52 khung (20 hình/giây, một vòng 2,6 s) bằng chính lõi `src/shipdemo/core.js`.
 * - Ghép GIF lặp vô hạn → docs/previews/tau-omen-2d.gif
 * - Ghép bảng 6 khung + khung xương → docs/previews/tau-omen-2d-khung.jpg
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const outDir = path.resolve(root, '..', 'docs', 'previews');

let createCanvas;
let loadImage;
try {
  ({ createCanvas, loadImage } = await import('@napi-rs/canvas'));
} catch {
  console.error('Thiếu thư viện vẽ: npm i -D @napi-rs/canvas');
  process.exit(1);
}

const { drawScene, firePhase, idlePhase, FIRE_TOTAL } = await import(path.join(root, 'src/shipdemo/core.js'));

const ART = path.join(root, 'src/art/ship/omen');
const W = 420;
const H = 525;
const FPS = 20;
const CYCLE = 2.6;
const FIRE_START = 0.5;

const canvas = createCanvas(W, H);
const ctx = canvas.getContext('2d');

const imgs = {};
for (const [k, f] of Object.entries({
  body: 'body.png', bodyDim: 'body_dim.png',
  wingL: 'wing_l.png', wingLDim: 'wing_l_dim.png',
  wingR: 'wing_r.png', wingRDim: 'wing_r_dim.png',
})) imgs[k] = await loadImage(path.join(ART, f));

fs.mkdirSync(outDir, { recursive: true });

const total = Math.round(FPS * CYCLE);
const ships = [
  ['omen', 'tau-omen-2d'],
  ['biomech', 'tau-sinhco-2d'],
  ['vertebra', 'tau-xuong-2d'],
];

for (const [ship, name] of ships) {
  const tmp = fs.mkdtempSync('/tmp/ship2d-');
  for (let i = 0; i < total; i++) {
    const t = i / FPS;
    const elapsed = t - FIRE_START;
    const phase = elapsed >= 0 && elapsed <= FIRE_TOTAL ? firePhase(elapsed) : idlePhase();
    drawScene(ctx, W, H, t, imgs, { phase, ship });
    fs.writeFileSync(path.join(tmp, `f_${String(i).padStart(3, '0')}.png`), canvas.toBuffer('image/png'));
  }
  // khung xương để kiểm tra gốc xoay cánh / ống xả / đầu nòng
  drawScene(ctx, W, H, 1.0, imgs, { phase: firePhase(0.5), skeleton: true, ship });
  fs.writeFileSync(path.join(tmp, 'bones.png'), canvas.toBuffer('image/png'));

  console.log(`Đã vẽ ${total} khung (${ship}) vào ${tmp}`);
  console.log(`  python3 tools/ship2d_gif.py ${tmp} ${name}`);
}
