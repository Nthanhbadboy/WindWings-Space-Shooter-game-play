import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

import './style.css';
import { loadAssets, buildEnvironment } from './assets.js';
import { createWorld } from './world.js';
import { createBackdrop } from './backdrop.js';
import { Input } from './input.js';
import { Hud } from './hud.js';
import { Sfx } from './audio.js';
import { Game } from './game.js';
import { Profile } from './save.js';
import { UI } from './ui.js';
import { levelInfo, dailySetup, CHAPTERS } from './content.js';
import { TEST_AUTO_FIRE, TEST_UNLOCK_ALL } from './devflags.js';

const canvas = document.getElementById('scene');
const hud = new Hud();
const sfx = new Sfx();
const profile = new Profile();

let renderer, camera, composer, bloom, world, game, input, ui, backdrop;
const cameraBase = new THREE.Vector3();
const cameraTarget = new THREE.Vector3(0, 0, -6);
let idleTime = 0;
let framing = null;

boot().catch((err) => {
  console.error(err);
  hud.showError('Không khởi tạo được cảnh 3D.\n' + err.message);
});

async function boot() {
  if (!window.WebGLRenderingContext) throw new Error('Trình duyệt không hỗ trợ WebGL');

  renderer = new THREE.WebGLRenderer({
    canvas, antialias: true, powerPreference: 'high-performance', alpha: false,
  });
  const coarse = window.matchMedia('(pointer: coarse)').matches;
  const maxDpr = coarse ? 1.5 : 2;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, maxDpr));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.12;

  const scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(46, window.innerWidth / window.innerHeight, 0.1, 400);
  camera.position.set(0, 20, 10);
  scene.add(camera); // để lớp tinh vân (con của camera) được render

  sfx.setMuted(profile.muted);
  hud.setSoundIcon(profile.muted);

  const assets = await loadAssets((p) => hud.setLoading(p * 0.92));
  hud.setLoading(1);

  applyTheme(CHAPTERS[0].theme, scene);
  world = createWorld(scene, camera, assets.textures, CHAPTERS[0].theme);
  backdrop = createBackdrop(scene, camera, {
    sky: assets.textures.sky,
    nebulaA: assets.textures.nebulaA,
    nebulaB: assets.textures.nebulaB,
    nebulaC: assets.textures.nebulaC,
    nebulaHaze: assets.textures.nebulaHaze,
    dot: assets.textures.dot,
    enemyArt: assets.textures.enemyArt,
  });
  backdrop.setTheme(CHAPTERS[0].theme);

  composer = new EffectComposer(renderer);
  composer.setPixelRatio(Math.min(window.devicePixelRatio || 1, maxDpr));
  composer.addPass(new RenderPass(scene, camera));
  bloom = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 0.9, 0.55, 0.62);
  composer.addPass(bloom);
  composer.addPass(new OutputPass());

  input = new Input(canvas, camera);
  input.onFirstDrag = () => hud.hideJoystickHint();

  game = new Game({
    scene, camera, assets, hud, sfx, input,
    bounds: { x: 5, zMin: -16, zMax: 3.4 },
    cameraBase, cameraTarget,
    profile,
    onResult: () => hud.setCoins(profile.coins),
  });
  game.shipId = profile.shipId;

  ui = new UI({
    profile, sfx,
    onStart: (mode, opts) => startGame(mode, opts),
  });
  hud.setUI(ui);
  hud.onPauseShow = () => ui.renderPause(game);

  ui.onShipChange = (id) => { if (game) game.shipId = id; };
  ui.onSpeed = (v) => { if (game) game.speedMul = v; };
  ui.onSoundChange = (muted) => hud.setSoundIcon(muted);
  ui.onControlChange = () => applyControls();
  applyControls();

  applyFraming();
  game.cameraBase = cameraBase;
  game.bounds = framing.bounds;

  wireUi(scene, assets);
  document.getElementById('screen-loading').classList.add('hidden');
  ui.show('home');

  // TEST: nhắc rõ đang ở chế độ mở khoá + tự bắn
  if (TEST_UNLOCK_ALL || TEST_AUTO_FIRE) {
    console.info('[TEST MODE] mở khoá tất cả màn:', TEST_UNLOCK_ALL, '| tự động bắn:', TEST_AUTO_FIRE);
    ui.toast('CHẾ ĐỘ TEST · mở hết màn · tự động bắn');
  }

  window.addEventListener('resize', onResize);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && game.state === 'playing') game.pause();
  });

  if ('serviceWorker' in navigator && import.meta.env && import.meta.env.PROD) {
    const swUrl = new URL('sw.js', document.baseURI).href;
    navigator.serviceWorker.register(swUrl, { scope: './' }).catch(() => {});
  }

  const clock = new THREE.Clock();
  let fpsAcc = 0;
  let fpsFrames = 0;
  let degraded = false;

  function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    idleTime += dt;

    world.update(dt, idleTime);
    // Camera trôi theo tàu: tàu sang phải → nền trôi sang trái (lớp gần mạnh hơn lớp xa).
    const playerX = game.player?.group?.position?.x ?? 0;
    backdrop?.update(dt, idleTime, {
      focus: THREE.MathUtils.clamp(playerX / (game.bounds?.x || 6), -1, 1),
      // chỉ áp dụng slow-mo khi đang chơi, để menu không bị chậm theo
      speed: game.state === 'playing' ? (game.speedMul || 1) : 1,
    });

    if (game.state === 'playing' || game.state === 'paused' || game.state === 'over') {
      game.update(dt * (game.speedMul || 1));
    } else {
      camera.position.set(
        cameraBase.x + Math.sin(idleTime * 0.18) * 0.8,
        cameraBase.y + Math.cos(idleTime * 0.14) * 0.4,
        cameraBase.z,
      );
      camera.lookAt(cameraTarget);
    }

    composer.render();

    if (!degraded) {
      fpsAcc += dt;
      fpsFrames += 1;
      if (fpsFrames > 120) {
        const fps = fpsFrames / fpsAcc;
        if (fps < 40) {
          degraded = true;
          bloom.strength = 0.55;
          renderer.setPixelRatio(1);
          composer.setPixelRatio(1);
          onResize();
        }
        fpsAcc = 0;
        fpsFrames = 0;
      }
    }
  }

  animate();
  window.__game = game;
  window.__profile = profile;
  window.__sfx = sfx;
}

// ------------------------------------------------------------ theme
function applyTheme(theme, scene) {
  // nền 3 lớp do backdrop.js dựng; ở đây chỉ cần bỏ skybox cũ
  buildEnvironment(null, scene);
}

function themeForMode(mode, opts) {
  if (mode === 'campaign') {
    const info = levelInfo(opts.chapter || profile.chapter, opts.level || 1);
    return info.theme;
  }
  if (mode === 'daily') return dailySetup().theme;
  return CHAPTERS[0].theme;
}

function startGame(mode, opts = {}) {
  const theme = themeForMode(mode, opts);
  applyTheme(theme, game.scene);
  world.setTheme(theme);
  backdrop?.setTheme(theme);
  ui.hideAll();
  document.getElementById('screen-pause')?.classList.add('hidden');
  document.getElementById('screen-result')?.classList.add('hidden');
  sfx.resume();
  game.start(mode, opts);
}

// ------------------------------------------------------------ camera framing
function applyFraming() {
  const aspect = window.innerWidth / window.innerHeight;
  camera.aspect = aspect;
  camera.updateProjectionMatrix();

  const target = new THREE.Vector3(0, 0, -6);
  const pitch = THREE.MathUtils.degToRad(52);
  const dir = new THREE.Vector3(0, -Math.sin(pitch), -Math.cos(pitch));
  const pts = [new THREE.Vector3(-5, 0, 3.4), new THREE.Vector3(5, 0, 3.4), new THREE.Vector3(0, 0, -15.5)];

  const setD = (d) => {
    camera.position.copy(target).addScaledVector(dir, -d);
    camera.lookAt(target);
    camera.updateMatrixWorld(true);
    camera.updateProjectionMatrix();
  };

  let lo = 8;
  let hi = 150;
  for (let i = 0; i < 34; i++) {
    const mid = (lo + hi) / 2;
    setD(mid);
    let max = 0;
    for (const p of pts) {
      const q = p.clone().project(camera);
      max = Math.max(max, Math.abs(q.x), Math.abs(q.y));
    }
    if (max > 0.94) lo = mid; else hi = mid;
  }
  setD(hi);

  let a = 0;
  let b = 60;
  for (let i = 0; i < 30; i++) {
    const mid = (a + b) / 2;
    const q = new THREE.Vector3(mid, 0, 2.2).project(camera);
    if (Math.abs(q.x) <= 0.97) a = mid; else b = mid;
  }

  framing = {
    cameraBase: camera.position.clone(),
    cameraTarget: target,
    bounds: { x: Math.min(8.5, a * 0.9), zMin: -16, zMax: 3.4 },
  };
  if (world) world.layout(aspect);
  cameraBase.copy(framing.cameraBase);
  cameraTarget.copy(target);
}

function onResize() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  renderer.setSize(w, h);
  composer.setSize(w, h);
  applyFraming();
  backdrop?.resize(w, h);
  if (game) {
    game.cameraBase = cameraBase;
    game.cameraTarget = cameraTarget;
    game.bounds = framing.bounds;
  }
}

// ------------------------------------------------------------ UI wiring
function wireUi() {
  const $ = (id) => document.getElementById(id);

  $('btnPause').addEventListener('click', () => {
    sfx.resume();
    game.togglePause();
  });
  $('btnResume').addEventListener('click', () => game.resume());
  $('btnRestartPause').addEventListener('click', () => startGame(game.mode, { chapter: game.chapter, level: game.levelIndex }));
  $('btnMenuPause').addEventListener('click', () => toMenu());
  $('btnReplay').addEventListener('click', () => startGame(game.mode, { chapter: game.chapter, level: game.levelIndex }));
  $('btnMenuOver').addEventListener('click', () => toMenu());

  $('btnSound').addEventListener('click', () => {
    sfx.resume();
    sfx.setMuted(!sfx.muted);
    profile.setMuted(sfx.muted);
    hud.setSoundIcon(sfx.muted);
  });

  window.addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    if (k === 'p' || k === 'escape') {
      if (game.state === 'playing' || game.state === 'paused') game.togglePause();
    } else if (k === 'enter') {
      if (game.state === 'over') startGame(game.mode, { chapter: game.chapter, level: game.levelIndex });
    } else if (k === 'm') {
      sfx.resume();
      sfx.setMuted(!sfx.muted);
      profile.setMuted(sfx.muted);
      hud.setSoundIcon(sfx.muted);
    }
  });
}

function toMenu() {
  game.state = 'menu';
  game.input.enabled = false;
  game._clearDynamic();
  document.getElementById('screen-pause')?.classList.add('hidden');
  document.getElementById('screen-result')?.classList.add('hidden');
  hud.el.hud.classList.add('hidden');
  ui.show('home');
  hud.setCoins?.(profile.coins);
  world.setTheme(CHAPTERS[0].theme);
  applyTheme(CHAPTERS[0].theme, game.scene, game.assets, renderer);
}

/** Áp dụng lựa chọn điều khiển trong màn tạm dừng. */
function applyControls() {
  if (!input || !game || !ui) return;
  input.setScheme(ui.control);
  // TEST: ép tự động bắn
  game.autoFire = TEST_AUTO_FIRE ? true : ui.autofire;
  game.speedMul = ui.speed / 100;
}
