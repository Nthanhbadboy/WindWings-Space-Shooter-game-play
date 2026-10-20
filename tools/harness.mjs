// =====================================================================
// Headless test harness: stubs enough browser API (canvas 2D, DOM, window
// events) to import game modules in Node and drive the loop deterministically.
// Run: node tools/headless_test.mjs   (npm test)
// =====================================================================
import assert from 'node:assert/strict';

// ---------------------------------------------------------------- stubs
function makeCtxStub(canvas) {
  const gradient = { addColorStop() {} };
  const target = {
    canvas,
    measureText: () => ({ width: 8 }),
    createLinearGradient: () => gradient,
    createRadialGradient: () => gradient,
    createPattern: () => null,
  };
  const noop = () => {};
  return new Proxy(target, {
    get(t, p) {
      if (p in t) return t[p];
      return noop;
    },
    set(t, p, v) {
      t[p] = v;
      return true;
    },
  });
}

function makeCanvasStub(w = 720, h = 1280) {
  const listeners = {};
  return {
    width: w,
    height: h,
    style: {},
    listeners,
    getContext() {
      if (!this._ctx) this._ctx = makeCtxStub(this);
      return this._ctx;
    },
    addEventListener(type, fn) {
      (listeners[type] = listeners[type] || []).push(fn);
    },
    removeEventListener() {},
    getBoundingClientRect() {
      return { left: 0, top: 0, width: w, height: h, right: w, bottom: h };
    },
    setPointerCapture() {},
    releasePointerCapture() {},
    emit(type, ev) {
      for (const fn of listeners[type] || []) fn({ preventDefault() {}, ...ev });
    },
  };
}

function setupGlobals() {
  const winListeners = {};
  globalThis.window = {
    innerWidth: 720,
    innerHeight: 1280,
    devicePixelRatio: 1,
    addEventListener(type, fn) {
      (winListeners[type] = winListeners[type] || []).push(fn);
    },
    removeEventListener() {},
    requestAnimationFrame: () => 1,
    cancelAnimationFrame: () => {},
    emit(type, ev) {
      for (const fn of winListeners[type] || []) fn({ preventDefault() {}, ...ev });
    },
  };
  globalThis.document = {
    getElementById: () => makeCanvasStub(),
    createElement: () => makeCanvasStub(8, 8),
    addEventListener() {},
    body: { appendChild() {}, style: {} },
    documentElement: { style: {} },
  };
  Object.defineProperty(globalThis, 'navigator', {
    value: { maxTouchPoints: 5, userAgent: 'node-headless' },
    configurable: true,
  });
  globalThis.requestAnimationFrame = () => 1;
  globalThis.cancelAnimationFrame = () => {};
}

setupGlobals();
const { Game } = await import('../game/js/game.js');
const { CONFIG } = await import('../game/js/config.js');
const { spawnEnemy } = await import('../game/js/enemies.js');
const { Powerup } = await import('../game/js/powerups.js');
const { Bullet } = await import('../game/js/projectiles.js');
const { menuButtons } = await import('../game/js/hud.js');
const { screenButtons } = await import('../game/js/screens.js');
const { getLevel, TOTAL_LEVELS } = await import('../game/js/levels.js');
const { Progress } = await import('../game/js/progress.js');

// ------------------------------------------------------------- helpers
function makeGame(level = 1) {
  const g = new Game(makeCanvasStub());
  g.startLevel(level);
  return g;
}

function frames(g, n, dt = 1 / 60) {
  for (let i = 0; i < n; i++) g.step(dt);
}

function clearWaves(g) {
  g.waves.events.length = 0; // stop the scripted timeline for isolated tests
  g.enemies.length = 0;
}

function clearWavesKeepBoss(g) {
  g.waves.events.length = 0;
  g.enemies.length = 0;
}

function toCanvas(g, x, y) {
  const r = g.canvas.getBoundingClientRect();
  return {
    clientX: (x / CONFIG.screen.width) * r.width,
    clientY: (y / CONFIG.screen.height) * r.height,
  };
}

const tests = [];
function test(name, fn) {
  tests.push({ name, fn });
}

function toBossIdle(g) {
  clearWaves(g);
  g.onStageClear();
  let n = 0;
  while (g.boss.state !== 'idle' && n++ < 600) g.step(1 / 60);
  assert.equal(g.boss.state, 'idle', 'boss reached idle');
  return g;
}

function forceAttack(g, id) {
  g.boss.forcePattern = id;
  g.boss.cooldown.reset(0);
}

function tapAt(g, x, y, id = 9) {
  const c = toCanvas(g, x, y);
  g.canvas.emit('pointerdown', { pointerId: id, ...c });
  g.canvas.emit('pointerup', { pointerId: id, ...c });
  g.step(1 / 60); // let the game consume the tap
}

function buttonCenter(b) {
  const r = b.rect || b;
  return { x: r.x + r.w / 2, y: r.y + r.h / 2 };
}


// ------------------------------------------------------------- exports
export {
  test, tests, makeGame, frames, clearWaves, clearWavesKeepBoss, toCanvas,
  tapAt, buttonCenter, toBossIdle, forceAttack,
  Game, CONFIG, spawnEnemy, Powerup, Bullet, menuButtons,
  screenButtons, getLevel, TOTAL_LEVELS, Progress,
};
