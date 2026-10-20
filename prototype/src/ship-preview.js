/**
 * Trang xem trước máy bay 3D — hình chiếu trực giao nhìn thẳng từ trên xuống.
 * Tất cả chuyển động lấy từ `buildShip()`: cánh vỗ, thân nghiêng, lửa đuôi,
 * giật nòng, râu cảm biến, đèn định vị. Đạn sinh ra đúng vị trí đầu nòng.
 */
import * as THREE from 'three';
import { buildShip } from './shipmodel.js';

const $ = (id) => document.getElementById(id);
const stage = $('stage');
const canvas = $('view');

/* ------------------------------------------------------------- renderer */
let renderer;
try {
  renderer = new THREE.WebGLRenderer({
    canvas, antialias: true, alpha: true, powerPreference: 'high-performance',
  });
} catch (err) {
  $('fatal').classList.remove('hidden');
  throw err;
}
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;

const scene = new THREE.Scene();
const camera = new THREE.OrthographicCamera(-3, 3, 4, -4, 0.1, 80);
camera.up.set(0, 0, -1);

/* ---------------------------------------------------------------- helpers */
function makeCanvas(w, h) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  return c;
}
function texFrom(canvas) {
  const t = new THREE.CanvasTexture(canvas);
  t.colorSpace = THREE.SRGBColorSpace;
  t.needsUpdate = true;
  return t;
}
function radialTexture() {
  const c = makeCanvas(128, 128);
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.24, 'rgba(255,255,255,0.72)');
  g.addColorStop(0.55, 'rgba(255,255,255,0.20)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 128, 128);
  return texFrom(c);
}
function dotTexture() {
  const c = makeCanvas(32, 32);
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.4, 'rgba(255,255,255,0.75)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 32, 32);
  return texFrom(c);
}
function starTexture() {
  const c = makeCanvas(160, 160);
  const ctx = c.getContext('2d');
  ctx.translate(80, 80);
  ctx.globalCompositeOperation = 'lighter';
  const g = ctx.createRadialGradient(0, 0, 0, 0, 0, 78);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.2, 'rgba(255,233,170,0.85)');
  g.addColorStop(0.55, 'rgba(255,176,70,0.26)');
  g.addColorStop(1, 'rgba(255,150,40,0)');
  ctx.fillStyle = g;
  ctx.beginPath(); ctx.arc(0, 0, 78, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = 'rgba(255,250,226,0.98)';
  for (let i = 0; i < 4; i++) {
    ctx.rotate(Math.PI / 2);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(11, -9);
    ctx.lineTo(72, 0);
    ctx.lineTo(11, 9);
    ctx.closePath();
    ctx.fill();
  }
  return texFrom(c);
}
function boltTexture() {
  const w = 48; const h = 160;
  const c = makeCanvas(w, h);
  const ctx = c.getContext('2d');
  const g = ctx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0, 'rgba(160,235,255,0)');
  g.addColorStop(0.3, 'rgba(170,240,255,0.55)');
  g.addColorStop(0.7, 'rgba(255,255,255,1)');
  g.addColorStop(1, 'rgba(120,220,255,0)');
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.ellipse(w / 2, h / 2, 9, h / 2, 0, 0, Math.PI * 2);
  ctx.fill();
  const core = ctx.createLinearGradient(0, 0, 0, h);
  core.addColorStop(0, 'rgba(255,255,255,0)');
  core.addColorStop(0.35, 'rgba(255,255,255,0.9)');
  core.addColorStop(0.75, 'rgba(255,255,255,1)');
  core.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = core;
  ctx.beginPath();
  ctx.ellipse(w / 2, h / 2, 3.2, h / 2 - 2, 0, 0, Math.PI * 2);
  ctx.fill();
  return texFrom(c);
}

const TEX = {
  glow: radialTexture(),
  dot: dotTexture(),
  star: starTexture(),
  bolt: boltTexture(),
};

/* ------------------------------------------------------------------ scene */
const root = new THREE.Group();
scene.add(root);

const ship = buildShip();
ship.root.traverse((o) => {
  if (!o.isMesh) return;
  const transparent = Array.isArray(o.material)
    ? o.material.some((m) => m.transparent)
    : o.material.transparent;
  o.castShadow = !transparent;
  o.receiveShadow = true;
});
root.add(ship.root);

/* ánh sáng */
scene.add(new THREE.HemisphereLight(0xbcdcff, 0x241a2c, 0.85));

const key = new THREE.DirectionalLight(0xfff2dc, 2.9);
key.position.set(-5, 7, -4);
key.castShadow = true;
key.shadow.mapSize.set(window.innerWidth > 900 ? 2048 : 1024, window.innerWidth > 900 ? 2048 : 1024);
key.shadow.camera.left = -5;
key.shadow.camera.right = 5;
key.shadow.camera.top = 5;
key.shadow.camera.bottom = -5;
key.shadow.camera.near = 1;
key.shadow.camera.far = 26;
key.shadow.bias = -0.0007;
key.shadow.normalBias = 0.02;
key.target.position.set(0, 0, 0.4);
scene.add(key);
scene.add(key.target);

const rim = new THREE.DirectionalLight(0x58c8ff, 1.35);
rim.position.set(4, 4, 6);
scene.add(rim);

const fill = new THREE.DirectionalLight(0xff9650, 0.75);
fill.position.set(0, 2, 5);
scene.add(fill);

const engineLight = new THREE.PointLight(0xff8a3c, 2.4, 6, 1.9);
engineLight.position.set(0, 0.4, 2.2);
scene.add(engineLight);

/* nền: sàn đổ bóng + quầng sáng + sao */
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(26, 26),
  new THREE.ShadowMaterial({ color: 0x00030a, opacity: 0.32 }),
);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -0.62;
ground.receiveShadow = true;
ground.renderOrder = 2;
scene.add(ground);

const grid = new THREE.GridHelper(26, 26, 0x2c6c9c, 0x123a5a);
grid.material.transparent = true;
grid.material.opacity = 0.16;
grid.material.depthWrite = false;
grid.position.y = -0.615;
scene.add(grid);

const bay = new THREE.Group();
const ringMat = new THREE.MeshBasicMaterial({
  color: 0x63d8ff, transparent: true, opacity: 0.22, side: THREE.DoubleSide,
  blending: THREE.AdditiveBlending, depthWrite: false,
});
for (const [r0, r1, op] of [[2.5, 2.53, 0.22], [1.62, 1.645, 0.14]]) {
  const ring = new THREE.Mesh(new THREE.RingGeometry(r0, r1, 96), ringMat.clone());
  ring.material.opacity = op;
  ring.rotation.x = -Math.PI / 2;
  ring.position.y = -0.6;
  bay.add(ring);
}
for (let i = 0; i < 16; i++) {
  const tick = new THREE.Mesh(new THREE.PlaneGeometry(0.05, i % 4 === 0 ? 0.24 : 0.12), ringMat.clone());
  const a = (i / 16) * Math.PI * 2;
  tick.material.opacity = 0.26;
  tick.rotation.x = -Math.PI / 2;
  tick.rotation.z = -a;
  tick.position.set(Math.cos(a) * 2.62, -0.6, Math.sin(a) * 2.62);
  bay.add(tick);
}
scene.add(bay);

const pool = new THREE.Mesh(
  new THREE.PlaneGeometry(11, 11),
  new THREE.MeshBasicMaterial({
    map: TEX.glow, color: 0x2f6bff, transparent: true, opacity: 0.20,
    blending: THREE.AdditiveBlending, depthWrite: false,
  }),
);
pool.rotation.x = -Math.PI / 2;
pool.position.y = -0.6;
pool.renderOrder = 1;
scene.add(pool);

function starLayer(count, spread, y, size, opacity) {
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(count * 3);
  const col = new Float32Array(count * 3);
  const palette = [
    new THREE.Color(0xbcdcff), new THREE.Color(0xffffff),
    new THREE.Color(0xffe7bd), new THREE.Color(0x9fb6ff),
  ];
  for (let i = 0; i < count; i++) {
    pos[i * 3] = (Math.random() - 0.5) * spread;
    pos[i * 3 + 1] = y + Math.random() * 0.4;
    pos[i * 3 + 2] = (Math.random() - 0.5) * spread * 0.75;
    const c = palette[(Math.random() * palette.length) | 0].clone().multiplyScalar(0.55 + Math.random() * 0.6);
    col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b;
  }
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const mat = new THREE.PointsMaterial({
    map: TEX.dot, size, transparent: true, opacity, vertexColors: true,
    blending: THREE.AdditiveBlending, depthWrite: false, sizeAttenuation: true,
  });
  const points = new THREE.Points(geo, mat);
  scene.add(points);
  return points;
}
starLayer(520, 30, -1.2, 0.085, 0.85);
starLayer(220, 22, -0.95, 0.16, 0.5);

/* ------------------------------------------------- phụ tùng phát sáng gắn tàu */
const sprite = (map, color, opacity, scale) => {
  const s = new THREE.Sprite(new THREE.SpriteMaterial({
    map, color, transparent: true, opacity,
    blending: THREE.AdditiveBlending, depthWrite: false,
  }));
  s.scale.setScalar(scale);
  return s;
};

const engineGlows = ship.parts.engines.map((e) => {
  const s = sprite(TEX.glow, 0xff8236, 0.7, 1.15);
  s.position.set(e.gx, 0.02, 2.06);
  ship.body.add(s);
  return s;
});

const podGlows = ship.parts.wings.map((w) => {
  const s = sprite(TEX.glow, 0x63d8ff, 0.55, 0.34);
  s.position.set(0, 0.03, -0.2);
  w.pod.add(s);
  const nav = sprite(TEX.glow, w.sign > 0 ? 0x5cffa8 : 0xff5a6a, 0.75, 0.26);
  nav.position.set(w.sign * 0.1, 0.02, 0.22);
  w.pod.add(nav);
  return s;
});

const canopyGlow = sprite(TEX.glow, 0x63d8ff, 0.24, 0.9);
canopyGlow.position.set(0, 0.39, -0.74);
ship.body.add(canopyGlow);

const gunGlows = ship.parts.guns.map((g) => {
  const s = sprite(TEX.star, 0xffd166, 0, 0.7);
  s.position.set(g.gx, 0.1, -1.84);
  ship.body.add(s);
  return s;
});

/* --------------------------------------------------------- marker đầu nòng */
const markerGeo = new THREE.RingGeometry(0.1, 0.125, 28);
const markerMat = new THREE.MeshBasicMaterial({
  color: 0x63d8ff, transparent: true, opacity: 0.85, side: THREE.DoubleSide,
  blending: THREE.AdditiveBlending, depthWrite: false,
});
const markers = [0, 1].map(() => {
  const m = new THREE.Mesh(markerGeo, markerMat);
  m.rotation.x = -Math.PI / 2;
  m.position.y = 0.08;
  root.add(m);
  return m;
});

/* ------------------------------------------------------------- đạn + chớp */
const boltMat = new THREE.SpriteMaterial({
  map: TEX.bolt, color: 0xd8f8ff, transparent: true,
  blending: THREE.AdditiveBlending, depthWrite: false,
});
const bullets = [];
const effects = [];
const forward = new THREE.Vector3();

const MUZZLE_TIP = new THREE.Vector3();

function spawnBullet(muzzle, dir) {
  const group = new THREE.Group();
  const core = new THREE.Sprite(boltMat);
  core.scale.set(0.19, 0.95, 1);
  group.add(core);
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({
    map: TEX.glow, color: 0x9fe9ff, transparent: true, opacity: 0.75,
    blending: THREE.AdditiveBlending, depthWrite: false,
  }));
  halo.scale.setScalar(0.42);
  group.add(halo);
  group.position.copy(muzzle).addScaledVector(dir, 0.12);
  group.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
  scene.add(group);
  bullets.push({ s: group, halo, v: dir.clone().multiplyScalar(11), life: 0, max: 1.2 });
}

function spawnFlash(muzzle, dir, color) {
  const s = sprite(TEX.star, color, 0.9, 0.3);
  s.position.copy(muzzle).addScaledVector(dir, 0.05);
  scene.add(s);
  effects.push({ s, life: 0, max: 0.09 });
  const ringGeo = new THREE.RingGeometry(0.04, 0.06, 20);
  const ring = new THREE.Mesh(ringGeo, markerMat.clone());
  ring.material.color.set(0xffe0a0);
  ring.rotation.x = -Math.PI / 2;
  ring.position.copy(muzzle);
  scene.add(ring);
  effects.push({ ring, life: 0, max: 0.16 });
}

/* ----------------------------------------------------------------- camera */
const CAM_TARGET = new THREE.Vector3(0, 0, 0.95);
const CAM_DIST = 16;
let halfW = 4;
let halfH = 4;

function applyCamera() {
  const aspect = Math.max(0.35, stage.clientWidth / Math.max(1, stage.clientHeight));
  const portrait = aspect < 0.95;
  halfH = portrait ? 5.25 : 4.12;
  halfW = halfH * aspect;
  if (halfW < 2.3) {
    halfW = 2.3;
    halfH = halfW / aspect;
  }
  CAM_TARGET.set(0, 0, portrait ? 1.28 : 0.95);
  camera.left = -halfW;
  camera.right = halfW;
  camera.top = halfH;
  camera.bottom = -halfH;
  camera.updateProjectionMatrix();

  const a = THREE.MathUtils.degToRad(state.tilt);
  camera.position.set(0, Math.cos(a) * CAM_DIST, CAM_TARGET.z + Math.sin(a) * CAM_DIST);
  camera.up.set(0, Math.sin(a), -Math.cos(a));
  camera.lookAt(CAM_TARGET);
  camera.updateMatrixWorld();
}

function resize() {
  const w = stage.clientWidth;
  const h = stage.clientHeight;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(w, h, false);
  applyCamera();
}

/* --------------------------------------------------------------- điều khiển */
const state = {
  flap: 1, throttle: 0.75, bank: 0, tilt: 0, speed: 1,
  fire: true, markers: true, labels: true, paused: false,
};

function fmtPct(v) { return `${Math.round(v * 100)}%`; }

function syncUi() {
  $('flap').value = String(state.flap);
  $('throttle').value = String(state.throttle);
  $('bank').value = String(state.bank);
  $('tilt').value = String(state.tilt);
  $('speed').value = String(state.speed);
  $('flapVal').textContent = fmtPct(state.flap);
  $('throttleVal').textContent = fmtPct(state.throttle);
  $('bankVal').textContent = `${Math.round(state.bank * 9)}°`;
  $('tiltVal').textContent = `${state.tilt}°`;
  $('speedVal').textContent = `${state.speed.toFixed(2).replace(/0$/, '')}×`;
  $('fireBtn').classList.toggle('on', state.fire);
  $('markerBtn').classList.toggle('on', state.markers);
  $('labelBtn').classList.toggle('on', state.labels);
  $('pauseBtn').classList.toggle('on', state.paused);
  $('pauseBtn').lastChild.textContent = state.paused ? 'TIẾP TỤC' : 'TẠM DỪNG';
  $('labels').classList.toggle('off', !state.labels);
  $('viewChip').innerHTML = `<i></i>TRỰC GIAO ${state.tilt}°`;
  markers.forEach((m) => { m.visible = state.markers; });
  applyCamera();
}

$('flap').addEventListener('input', (e) => { state.flap = parseFloat(e.target.value); syncUi(); });
$('throttle').addEventListener('input', (e) => { state.throttle = parseFloat(e.target.value); syncUi(); });
$('bank').addEventListener('input', (e) => { state.bank = parseFloat(e.target.value); syncUi(); });
$('tilt').addEventListener('input', (e) => { state.tilt = parseFloat(e.target.value); syncUi(); });
$('speed').addEventListener('input', (e) => { state.speed = parseFloat(e.target.value); syncUi(); });

$('fireBtn').addEventListener('click', () => { state.fire = !state.fire; syncUi(); });
$('markerBtn').addEventListener('click', () => { state.markers = !state.markers; syncUi(); });
$('labelBtn').addEventListener('click', () => { state.labels = !state.labels; syncUi(); });
$('pauseBtn').addEventListener('click', () => { state.paused = !state.paused; syncUi(); });
$('resetBtn').addEventListener('click', () => {
  Object.assign(state, { flap: 1, throttle: 0.75, bank: 0, tilt: 0, speed: 1, fire: true, markers: true, labels: true, paused: false });
  simTime = 0;
  clearBullets();
  syncUi();
});

function clearBullets() {
  for (const b of bullets) scene.remove(b.s);
  bullets.length = 0;
  for (const e of effects) {
    scene.remove(e.s || e.ring);
    if (e.s?.material) e.s.material.dispose();
    if (e.ring) e.ring.material.dispose();
  }
  effects.length = 0;
}

window.addEventListener('keydown', (e) => {
  if (e.code === 'Space') { e.preventDefault(); state.paused = !state.paused; syncUi(); }
  else if (e.key === 'f' || e.key === 'F') { state.fire = !state.fire; syncUi(); }
  else if (e.key === 'l' || e.key === 'L') { state.labels = !state.labels; syncUi(); }
  else if (e.key === 'm' || e.key === 'M') { state.markers = !state.markers; syncUi(); }
});

/* ------------------------------------------------------------ nhãn bộ phận */
const LABEL_ANCHORS = {
  wing: new THREE.Vector3(1.3, 0.22, 0.15),
  engine: new THREE.Vector3(0.36, 0.06, 2.3),
  gun: new THREE.Vector3(-0.68, 0.1, -2.0),
  canopy: new THREE.Vector3(0, 0.34, -0.78),
};
const labelEls = [...document.querySelectorAll('.plabel')];
const projected = new THREE.Vector3();

function updateLabels() {
  if (!state.labels) return;
  const w = stage.clientWidth;
  const h = stage.clientHeight;
  for (const el of labelEls) {
    projected.copy(LABEL_ANCHORS[el.dataset.key]);
    ship.body.localToWorld(projected);
    projected.project(camera);
    const pad = w < 620 ? 150 : 185;
    let x = (projected.x * 0.5 + 0.5) * w;
    if (el.dataset.dir === 'right') x = Math.min(x, w - pad);
    else x = Math.max(x, pad);
    el.style.left = `${x}px`;
    el.style.top = `${(-projected.y * 0.5 + 0.5) * h}px`;
    el.style.opacity = projected.z > 1 ? '0' : '1';
  }
}

/* ------------------------------------------------------------------ vòng lặp */
let simTime = 0;
let last = performance.now();
let fireAcc = 0;
let shot = 0;
let fpsAcc = 0;
let fpsFrames = 0;
const muzzles = [new THREE.Vector3(), new THREE.Vector3()];

syncUi();
resize();
window.addEventListener('resize', resize);
ship.update(1 / 60, 0, { flap: state.flap, throttle: state.throttle, firing: false, bank: state.bank });

function tick(now) {
  const dtReal = Math.min(0.05, (now - last) / 1000);
  last = now;
  const dt = state.paused ? 0 : dtReal * state.speed;
  simTime += dt;

  ship.update(dt, simTime, {
    flap: state.flap,
    throttle: state.throttle,
    firing: state.fire && !state.paused,
    bank: state.bank,
  });

  // lấy vị trí đầu nòng THẬT sau khi cập nhật khung xương
  const raw = ship.getMuzzles();
  for (let i = 0; i < 2; i++) muzzles[i].copy(raw[i]);

  if (state.markers) {
    markers.forEach((m, i) => {
      m.position.set(muzzles[i].x, 0.08, muzzles[i].z);
      const s = 1 + Math.sin(simTime * 6 + i * Math.PI) * 0.12;
      m.scale.setScalar(s);
      m.rotation.z = simTime * 1.2 + i;
    });
  }

  // bắn: mỗi phát sinh đúng tại một đầu nòng, luân phiên trái/phải
  if (state.fire && !state.paused) {
    fireAcc += dt;
    const interval = 0.095;
    let guard = 0;
    while (fireAcc >= interval && guard < 6) {
      fireAcc -= interval;
      guard++;
      const i = shot % 2;
      shot++;
      MUZZLE_TIP.copy(muzzles[i]);
      forward.set(0, 0, -1).applyQuaternion(ship.body.quaternion).normalize();
      spawnBullet(MUZZLE_TIP, forward);
      spawnFlash(MUZZLE_TIP, forward, 0xffd166);
    }
  } else {
    fireAcc = 0;
  }

  // đạn
  for (let i = bullets.length - 1; i >= 0; i--) {
    const b = bullets[i];
    b.life += dt;
    b.s.position.addScaledVector(b.v, dt);
    const fade = Math.min(1, (b.max - b.life) * 5);
    b.halo.material.opacity = 0.45 + fade * 0.35;
    if (b.life > b.max || b.s.position.z < -10) {
      scene.remove(b.s);
      b.halo.material.dispose();
      bullets.splice(i, 1);
    }
  }

  // chớp đầu nòng
  for (let i = effects.length - 1; i >= 0; i--) {
    const e = effects[i];
    e.life += dt;
    const k = 1 - e.life / e.max;
    if (e.s) {
      e.s.material.opacity = Math.max(0, k);
      e.s.scale.setScalar(0.16 + (1 - k) * 0.3);
    }
    if (e.ring) {
      e.ring.material.opacity = Math.max(0, k * 0.9);
      e.ring.scale.setScalar(1 + (1 - k) * 2.6);
    }
    if (e.life >= e.max) {
      scene.remove(e.s || e.ring);
      if (e.s) e.s.material.dispose();
      if (e.ring) e.ring.material.dispose();
      effects.splice(i, 1);
    }
  }

  // lửa / quầng động cơ
  const t = simTime;
  const flick = 0.86 + Math.sin(t * 41) * 0.08 + Math.sin(t * 17.3) * 0.06;
  engineGlows.forEach((s, i) => {
    const k = (0.5 + state.throttle * 1.05) * (0.9 + (i ? 0.04 : 0) - 0.05 + Math.sin(t * 43 + i) * 0.06);
    s.scale.setScalar(Math.max(0.2, 0.75 + k * 0.9));
    s.material.opacity = 0.35 + state.throttle * 0.55;
  });
  engineLight.intensity = (1.1 + state.throttle * 2.6) * flick;
  engineLight.position.set(0, 0.35, 1.9 + Math.sin(t * 1.7) * 0.1);

  podGlows.forEach((s, i) => {
    s.material.opacity = 0.35 + Math.abs(Math.sin(t * 3.1 + i * 2)) * 0.4;
  });
  canopyGlow.material.opacity = 0.16 + Math.abs(Math.sin(t * 2.2)) * 0.22;

  gunGlows.forEach((s, i) => {
    const f = ship.parts.guns[i].flash.material.opacity;
    s.material.opacity = Math.min(0.9, f * 1.4);
    s.scale.setScalar(0.16 + f * 0.3);
    s.visible = f > 0.02;
  });

  // pool sáng dưới tàu
  pool.material.opacity = 0.14 + state.throttle * 0.12;

  updateLabels();
  renderer.render(scene, camera);

  fpsAcc += dtReal;
  fpsFrames++;
  if (fpsAcc > 0.5) {
    $('fpsChip').textContent = `${Math.round(fpsFrames / fpsAcc)} FPS`;
    fpsAcc = 0;
    fpsFrames = 0;
  }
  window.__SHIP_LAB__ = { ship, scene, camera, state, renderer, bullets, muzzles, markers };
requestAnimationFrame(tick);
}

document.addEventListener('visibilitychange', () => { last = performance.now(); });
canvas.addEventListener('webglcontextlost', (e) => {
  e.preventDefault();
  $('fatal').classList.remove('hidden');
});

window.__SHIP_LAB__ = { ship, scene, camera, state, renderer, bullets, muzzles, markers };
requestAnimationFrame(tick);
