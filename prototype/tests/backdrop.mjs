/**
 * Kiểm tra nền nhiều lớp ở môi trường node (không cần WebGL):
 *   1. dựng được, update 120 khung không lỗi / không NaN
 *   2. lớp bụi gần đi nhanh hơn lớp xa (parallax thật)
 *   3. lớp gần nằm TRƯỚC vùng giao chiến (z −1,7…−4,8 so với tàu ~−7)
 *   4. camera trôi theo tàu: focus dương → nền dịch sang trái
 *   5. hệ số làm chậm làm nền chậm theo
 *   6. L0 = ảnh thật độ phân giải cao, ĐỨNG YÊN tuyệt đối (D19 giữ nguyên)
 *   7. KHÔNG còn Trái Đất, KHÔNG còn trạm/dầm/tinh vân vẽ tay (D20)
 *   8. L1 = tinh vân ẢNH THẬT, CÓ chuyển động, không xoay, chạy vòng liền mạch (D20)
 */
import * as THREE from 'three';
import { createBackdrop } from '../src/backdrop.js';

const ok = (name, cond, extra = '') => {
  console.log(`${cond ? '✓' : '✗'} ${name}${extra ? ` — ${extra}` : ''}`);
  if (!cond) process.exitCode = 1;
  return cond;
};

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(46, 390 / 844, 0.1, 600);
scene.add(camera);

const bg = createBackdrop(scene, camera, {});
ok('dựng được nền', !!bg && !!bg.nearField);

// setTheme không được ném lỗi ở cả hai chế độ (có ảnh / gradient dự phòng)
let themeOk = true;
try {
  bg.setTheme({ nebula: [0x3f6fd0, 0x1f6fa8], fog: 0.9, starColor: 0xffffff });
} catch (e) {
  themeOk = false;
}
ok('setTheme chạy được khi thiếu ảnh (gradient dự phòng)', themeOk);

// 1. chạy 120 khung
let nan = false;
for (let i = 0; i < 120; i++) {
  bg.update(1 / 60, i / 60, { focus: 0.8, speed: 1 });
  for (const o of bg.nearField.children) {
    if (!Number.isFinite(o.position.x) || !Number.isFinite(o.position.y)) nan = true;
  }
  for (const o of bg.debris) {
    if (!Number.isFinite(o.s.position.x) || !Number.isFinite(o.s.position.y)) nan = true;
  }
}
ok('120 khung không NaN', !nan);

// 2. parallax: tốc độ màn hình = speed / (2 * hh) — phải tăng khi depth giảm
const speeds = bg.dustLayers
  .map((d) => ({ depth: d.depth, screen: d.speed / (2 * d.hh) }))
  .sort((a, b) => b.depth - a.depth);
let mono = true;
for (let i = 1; i < speeds.length; i++) if (speeds[i].screen <= speeds[i - 1].screen) mono = false;
ok(
  'lớp gần nhanh hơn lớp xa',
  mono,
  speeds.map((s) => `z${Math.round(s.depth)}:${s.screen.toFixed(2)}`).join(' › '),
);

// 3. lớp gần ở phía trước tàu
const zs = bg.nearField.children.map((o) => o.position.z);
ok(
  'lớp gần nằm trước tàu (z > −5, tàu ~ −7)',
  zs.every((z) => z < 0 && z > -5),
  `z ${Math.min(...zs).toFixed(1)}…${Math.max(...zs).toFixed(1)}`,
);

// 4. focus parallax ngược chiều
bg.update(1 / 60, 2, { focus: 1, speed: 1 });
for (let i = 0; i < 90; i++) bg.update(1 / 60, 2 + i / 60, { focus: 1, speed: 1 });
const shiftRight = bg.nearField.position.x;
bg.update(1 / 60, 4, { focus: -1, speed: 1 });
for (let i = 0; i < 90; i++) bg.update(1 / 60, 4 + i / 60, { focus: -1, speed: 1 });
const shiftLeft = bg.nearField.position.x;
ok('tàu sang phải → nền trôi sang trái', shiftRight < 0 && shiftLeft > 0,
  `${shiftRight.toFixed(3)} / ${shiftLeft.toFixed(3)}`);

// 5. CHẬM: nền phải chậm theo
const probe = (scale) => {
  const sp = bg.nearField.children[0];
  sp.position.y = 0; // đặt giữa màn hình để không chạm mép cuộn
  for (let i = 0; i < 6; i++) bg.update(1 / 60, 20 + i / 60, { focus: 0, speed: scale });
  return Math.abs(sp.position.y);
};
const fastDy = probe(1);
const slowDy = probe(0.28);
ok('hệ số 0,28 làm nền chậm theo', slowDy < fastDy * 0.5, `${fastDy.toFixed(4)} vs ${slowDy.toFixed(4)}`);

// ------------------------------------------------------------------ D20
const fakeSky = new THREE.Texture();
fakeSky.image = { width: 2560, height: 2560 };
const fakeNebs = ['nebulaA', 'nebulaB', 'nebulaC', 'nebulaHaze'].map(() => {
  const t = new THREE.Texture();
  t.image = { width: 1920, height: 1080 };
  return t;
});

const scene2 = new THREE.Scene();
const cam2 = new THREE.PerspectiveCamera(46, 390 / 844, 0.1, 600);
scene2.add(cam2);
const bg2 = createBackdrop(scene2, cam2, {
  sky: fakeSky, nebulaA: fakeNebs[0], nebulaB: fakeNebs[1], nebulaC: fakeNebs[2],
  nebulaHaze: fakeNebs[3],
});
bg2.resize(390, 844);

// 6. nền xa: ảnh thật, phủ kín, đứng yên
ok('L0 dùng ảnh thật (Deep Field 2560²)', bg2.sky.material.map === fakeSky);
ok('ảnh nền ≥ 2000 px', fakeSky.image.width >= 2000 && fakeSky.image.height >= 2000,
  `${fakeSky.image.width}×${fakeSky.image.height}`);
const ratio = bg2.sky.scale.x / bg2.sky.scale.y;
ok('nền xa phủ kín mà không bóp méo', Math.abs(ratio - 1) < 0.01, `tỉ lệ ${ratio.toFixed(3)}`);

const before = { x: bg2.sky.position.x, y: bg2.sky.position.y, rz: bg2.sky.rotation.z };
for (let i = 0; i < 180; i++) bg2.update(1 / 60, i / 60, { focus: 1, speed: 1 });
const still = bg2.sky.position.x === before.x && bg2.sky.position.y === before.y
  && bg2.sky.rotation.z === before.rz;
ok('L0 TUYỆT ĐỐI không chuyển động', still, `x ${bg2.sky.position.x}`);

// 7. đã bỏ Trái Đất + trạm/dầm/tinh vân vẽ tay
ok('không còn lớp Trái Đất', !('earth' in bg2) && !('earthClouds' in bg2));
ok('không còn trạm/dầm vẽ tay', !('struct' in bg2));

// 8. L1 = tinh vân ảnh thật, có chuyển động
const clouds = bg2.nebula;
ok('L1 có ≥ 3 đám tinh vân', clouds.length >= 3, `${clouds.length} đám`);
ok('L1 toàn ảnh thật', clouds.every((c) => fakeNebs.includes(c.mesh.material.map)));
ok('L1 nằm giữa L0 và các lớp sao',
  clouds.every((c) => c.mesh.position.z > bg2.sky.position.z && Math.abs(c.mesh.position.z) < 320),
  `sky z${bg2.sky.position.z} → neb z${clouds.map((c) => c.mesh.position.z).join(',')}`);

const y0 = clouds.map((c) => c.mesh.position.y);
for (let i = 0; i < 60; i++) bg2.update(1 / 60, 10 + i / 60, { focus: 0, speed: 1 });
ok('L1 có chuyển động trôi', clouds.every((c, i) => c.mesh.position.y !== y0[i]));

// xa hơn phải trôi chậm hơn — nếu không thì mắt đọc sai thứ tự lớp
let ordered = true;
for (const a of clouds) {
  for (const b of clouds) {
    if (a.def.z > b.def.z && a.speed > b.speed) ordered = false;
    if (a.def.z < b.def.z && a.speed < b.speed) ordered = false;
  }
}
ok('L1 xa hơn → trôi chậm hơn', ordered,
  clouds.map((c) => `z${c.def.z}:${c.speed}`).join(' › '));

const noRot = clouds.every((c) => c.mesh.rotation.z === 0 && c.mesh.rotation.x === 0);
ok('L1 không xoay (chỉ trôi dọc + parallax ngang)', noRot);

// 9. trôi hết màn hình thì tái sinh ở trên, không mất lớp, không NaN
let inBounds = true;
for (let i = 0; i < 4000; i++) {
  bg2.update(1 / 30, 30 + i / 30, { focus: 0.6, speed: 1 });
  for (const c of clouds) {
    const vh = 2 * Math.tan(THREE.MathUtils.degToRad(46 / 2)) * c.def.z;
    if (!Number.isFinite(c.mesh.position.y) || Math.abs(c.mesh.position.y) > vh * 1.4) inBounds = false;
  }
}
ok('đám tinh vân tái sinh đúng biên, không trôi mất', inBounds);

console.log(process.exitCode ? '\nCÓ LỖI' : '\nNỀN NHIỀU LỚP: ĐẠT');
