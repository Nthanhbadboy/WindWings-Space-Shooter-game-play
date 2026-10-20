// Input: drag ANYWHERE on screen to move + auto-fire while touching
// (standard mobile shmup). Bomb button bottom-right, pause top-left.
// Multi-touch via pointer events; keyboard fallback for desktop preview.
import { CONFIG } from './config.js';
import { dist } from './utils.js';

const BOMB = CONFIG.controls.bombButton;
const PAUSE = CONFIG.controls.pauseButton;
const S = CONFIG.screen;

const KEY_MOVE = {
  ArrowUp: [0, -1], KeyW: [0, -1],
  ArrowDown: [0, 1], KeyS: [0, 1],
  ArrowLeft: [-1, 0], KeyA: [-1, 0],
  ArrowRight: [1, 0], KeyD: [1, 0],
};
const KEY_FIRE = ['Space', 'KeyJ', 'KeyZ'];
const KEY_BOMB = ['KeyB', 'KeyX'];
const KEY_PAUSE = ['KeyP', 'Escape'];

export class Input {
  constructor(canvas, game) {
    this.canvas = canvas;
    this.game = game;
    // public state:
    this.dragging = false;          // finger down => move + auto-fire
    this.dragTarget = { x: CONFIG.player.startX, y: CONFIG.player.startY };
    this.keyMove = { x: 0, y: 0 };  // keyboard analog
    this.firing = false;            // dragging OR keyboard fire held
    this.bombQueued = false;        // edge flags consumed by Game
    this.pauseQueued = false;
    this.uiTap = null;              // tap for menu buttons
    // internal:
    this._pointers = new Map();     // pointerId -> role
    this._keys = new Set();
    this._keyFireHeld = false;
    this._attach();
  }

  _attach() {
    const c = this.canvas;
    c.addEventListener('pointerdown', (e) => this._onDown(e));
    c.addEventListener('pointermove', (e) => this._onMove(e));
    c.addEventListener('pointerup', (e) => this._onUp(e));
    c.addEventListener('pointercancel', (e) => this._onUp(e));
    window.addEventListener('keydown', (e) => this._onKey(e, true));
    window.addEventListener('keyup', (e) => this._onKey(e, false));
  }

  _pos(e) {
    const r = this.canvas.getBoundingClientRect();
    return {
      x: ((e.clientX - r.left) / Math.max(1, r.width)) * S.width,
      y: ((e.clientY - r.top) / Math.max(1, r.height)) * S.height,
    };
  }

  _blocked() {
    return this.game.paused || this.game.state !== 'playing';
  }

  _onDown(e) {
    if (e.preventDefault) e.preventDefault();
    const p = this._pos(e);
    if (this._blocked()) {
      this.uiTap = p;
      return;
    }
    if (dist(p.x, p.y, PAUSE.centerX, PAUSE.centerY) <= PAUSE.radius * 1.6) {
      this.pauseQueued = true;
      this._pointers.set(e.pointerId, 'pause');
    } else if (dist(p.x, p.y, BOMB.centerX, BOMB.centerY) <= BOMB.radius * 1.3) {
      this.bombQueued = true;
      this._pointers.set(e.pointerId, 'bomb');
    } else {
      // drag anywhere: ship chases the finger (offset so it stays visible)
      this._pointers.set(e.pointerId, 'drag');
      this.dragging = true;
      this._setDrag(p);
    }
    this._refreshFiring();
  }

  _onMove(e) {
    if (this._pointers.get(e.pointerId) !== 'drag') return;
    this._setDrag(this._pos(e));
  }

  _onUp(e) {
    const role = this._pointers.get(e.pointerId);
    if (role === 'drag') {
      let still = false;
      this._pointers.forEach((r, id) => {
        if (r === 'drag' && id !== e.pointerId) still = true;
      });
      if (!still) this.dragging = false;
    }
    this._pointers.delete(e.pointerId);
    this._refreshFiring();
  }

  _setDrag(p) {
    this.dragTarget.x = p.x;
    this.dragTarget.y = p.y + CONFIG.player.touchOffsetY;
  }

  _onKey(e, down) {
    if (down) this._keys.add(e.code);
    else this._keys.delete(e.code);
    if (down && KEY_PAUSE.includes(e.code)) this.pauseQueued = true;
    if (down && KEY_BOMB.includes(e.code) && !this._blocked()) this.bombQueued = true;
    this._keyFireHeld = KEY_FIRE.some((k) => this._keys.has(k));
    const km = { x: 0, y: 0 };
    for (const [code, vec] of Object.entries(KEY_MOVE)) {
      if (this._keys.has(code)) {
        km.x += vec[0];
        km.y += vec[1];
      }
    }
    const d = Math.hypot(km.x, km.y);
    if (d > 1) {
      km.x /= d;
      km.y /= d;
    }
    this.keyMove = km;
    this._refreshFiring();
  }

  _refreshFiring() {
    this.firing = this.dragging || this._keyFireHeld;
  }

  consumeBomb() {
    const v = this.bombQueued;
    this.bombQueued = false;
    return v;
  }

  consumePause() {
    const v = this.pauseQueued;
    this.pauseQueued = false;
    return v;
  }

  consumeUiTap() {
    const v = this.uiTap;
    this.uiTap = null;
    return v;
  }
}
