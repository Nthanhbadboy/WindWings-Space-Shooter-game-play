// Game root: logical-resolution canvas, delta-time loop with global
// timeScale (slow-mo), pause, entity pools, camera shake, flashes.
// Entity systems (enemies/waves/boss/powerups/HUD) plug into update/render.
import { CONFIG } from './config.js';
import { StarField } from './bg.js';
import { Input } from './input.js';
import { Player } from './player.js';
import { ScoreManager } from './score.js';
import { AudioManager } from './audio.js';
import { updateEnemies } from './enemies.js';
import { WaveManager } from './waves.js';
import { getLevel } from './levels.js';
import { Progress } from './progress.js';
import { drawScreens, handleScreenTap } from './screens.js';
import { Boss } from './boss.js';
import { drawHud, handleUiTap } from './hud.js';
import { burst, coinBurst } from './particles.js';
import { rollDrop, updatePowerups, drawPowerups } from './powerups.js';
import { updatePopups, drawPopups } from './fx.js';
import { updateParticles, drawParticles } from './particles.js';
import { collideBullets, collideEnemyBullets, useBomb, updateBossDeath } from './combat.js';

const S = CONFIG.screen;

export class Game {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.viewScale = 1;

    this.audio = new AudioManager();
    this.input = new Input(canvas, this);
    this.bg = new StarField();
    this.score = new ScoreManager(this);
    this.player = new Player(this);
    this.waves = new WaveManager(this, CONFIG.waves.definitions);
    this.boss = new Boss(this);
    this.stageCleared = false;
    this.bossDeath = null;     // death sequence tracker
    this.victoryAlpha = 0;

    // campaign meta (60 levels)
    this.progress = new Progress();
    this.currentLevel = 1;
    this.level = null;
    this.selectChapter = 1;
    this.lastStars = 0;
    this.bannerT = 0;
    this.levelMods = { hp: 1, speed: 1, bullet: 1 };
    this.bossBulletMul = 1;

    this.state = 'menu';   // menu | select | playing | victory | defeat
    this.paused = false;
    this.timeScale = 1;
    this._slowMo = null;      // {remaining} in REAL seconds

    // entity pools
    this.bullets = [];
    this.enemyBullets = [];
    this.enemies = [];
    this.powerups = [];
    this.telegraphs = [];
    this.particles = [];
    this.popups = [];
    this.coins = [];

    this.shake = { amp: 0, dur: 0, t: 0, ox: 0, oy: 0 };
    this.continuousShake = 0;  // enrage rumble (step 6)
    this.flashes = [];         // {color, alpha, dur, t}
    this.darkOverlay = 0;      // phase-3 screen-darken alpha

    this._boundResize = () => this.resize();
    if (typeof window !== 'undefined' && window.addEventListener) {
      window.addEventListener('resize', this._boundResize);
    }
    this.resize();
    this.reset();
    this.state = 'menu';
  }

  /** Begin one of the 60 campaign levels (boss every 10th). */
  startLevel(n) {
    this.currentLevel = n;
    this.level = getLevel(n);
    this.levelMods = this.level.mods;
    this.bossBulletMul = this.level.mods.bullet;
    this.reset();
    this.boss.configure(this.level.boss);
    this.waves = new WaveManager(this, this.level.waves);
    this.bannerT = CONFIG.screens.banner.time;
    this.state = 'playing';
  }

  /** Waves finished: boss stage on boss levels, else level complete. */
  onWavesDone() {
    this.stageCleared = true;
    if (this.level && this.level.isBoss) this.boss.begin();
    else this.finishLevel();
  }

  /** Level complete: award stars (by lives left), unlock next level. */
  finishLevel() {
    if (this.state !== 'playing') return;
    this.lastStars = Math.max(1, Math.min(3, this.player.lives));
    this.progress.recordClear(this.currentLevel, this.lastStars);
    this.state = 'victory';
  }

  // ------------------------------------------------------------------ loop
  start() {
    this._lastTs = null;
    const loop = (ts) => {
      this._raf = requestAnimationFrame(loop);
      if (this._lastTs === null) this._lastTs = ts;
      const dtReal = (ts - this._lastTs) / 1000;
      this._lastTs = ts;
      this.step(dtReal);
    };
    this._raf = requestAnimationFrame(loop);
  }

  step(dtReal) {
    if (!(dtReal > 0)) dtReal = 0;
    dtReal = Math.min(dtReal, S.maxDelta);

    if (this._slowMo) {
      this._slowMo.remaining -= dtReal;
      if (this._slowMo.remaining <= 0) {
        this._slowMo = null;
        this.timeScale = 1;
      }
    }

    if (this.input.consumePause()) this.togglePause();
    if (this.input.consumeBomb()) this.useBomb();
    if (this.state !== 'playing' || this.paused) {
      const tap = this.input.consumeUiTap();
      if (tap) {
        if (this.paused) handleUiTap(this, tap.x, tap.y);
        else handleScreenTap(this, tap.x, tap.y);
      }
    }

    const frozen = this.paused || this.state !== 'playing';
    const dt = frozen ? 0 : dtReal * this.timeScale;
    if (dt > 0) this.update(dt);
    this.render();
  }

  update(dt) {
    this.bg.update(dt);
    this.bannerT = Math.max(0, this.bannerT - dt);
    this.player.update(dt, this.input);
    if (this.waves) this.waves.update(dt);
    updateEnemies(this, dt);
    updatePowerups(this, dt);
    if (this.boss) this.boss.update(dt);
    this._updateBullets(dt);
    collideBullets(this);
    collideEnemyBullets(this);
    if (this.bossDeath) updateBossDeath(this, dt);
    this._updateTelegraphs(dt);
    updateParticles(this, dt);
    updatePopups(this, dt);
    this._updateShake(dt);
    this._updateFlashes(dt);
  }

  _updateBullets(dt) {
    for (let i = this.bullets.length - 1; i >= 0; i--) {
      const b = this.bullets[i];
      b.update(dt);
      if (b.dead) this.bullets.splice(i, 1);
    }
    for (let i = this.enemyBullets.length - 1; i >= 0; i--) {
      const b = this.enemyBullets[i];
      b.update(dt);
      if (b.dead) this.enemyBullets.splice(i, 1);
    }
  }

  _updateTelegraphs(dt) {
    for (let i = this.telegraphs.length - 1; i >= 0; i--) {
      const tg = this.telegraphs[i];
      tg.update(dt);
      if (tg.done) this.telegraphs.splice(i, 1); // self-removing effects
    }
  }

  // --------------------------------------------------------- event hooks
  onPlayerHit() {
    this.score.onPlayerHit();
  }

  /** Enemy died to bullets: drop rolls (5% weapon / 1% bomb). */
  onEnemyKilled(enemy) {
    rollDrop(this, enemy);
  }

  onPlayerDefeat() {
    this.state = 'defeat'; // overlay flow in step 8
  }

  /** Boss died: kick off the death sequence (combat.js drives it). */
  onBossDeath() {
    const d = CONFIG.boss.death;
    this.bossDeath = { t: 0, wave: 0, coins: false };
    this.setSlowMo(d.slowMo.scale, d.slowMo.dur);
    this.score.addBossKill();
    this.enemyBullets.length = 0;
    this.enemies.length = 0;
  }

  onStageClear() {
    this.stageCleared = true;
    this.boss.begin(); // warning -> entry (manual/test hook)
  }

  // ------------------------------------------------------------- fx hooks
  addShake(amp, dur) {
    if (amp >= this.shake.amp || this.shake.t >= this.shake.dur) {
      this.shake.amp = amp;
      this.shake.dur = dur;
      this.shake.t = 0;
    }
  }

  _updateShake(dt) {
    const sh = this.shake;
    let ox = 0;
    let oy = 0;
    if (this.continuousShake > 0) {
      ox += (Math.random() * 2 - 1) * this.continuousShake;
      oy += (Math.random() * 2 - 1) * this.continuousShake;
    }
    if (sh.t < sh.dur) {
      sh.t += dt;
      const k = Math.max(0, 1 - sh.t / sh.dur);
      const a = sh.amp * k;
      ox += (Math.random() * 2 - 1) * a;
      oy += (Math.random() * 2 - 1) * a;
    }
    sh.ox = ox;
    sh.oy = oy;
  }

  addFlash(color, alpha, dur) {
    this.flashes.push({ color, alpha, dur, t: 0 });
  }

  _updateFlashes(dt) {
    for (let i = this.flashes.length - 1; i >= 0; i--) {
      const f = this.flashes[i];
      f.t += dt;
      if (f.t >= f.dur) this.flashes.splice(i, 1);
    }
  }

  setSlowMo(scale, durReal) {
    this.timeScale = scale;
    this._slowMo = { remaining: durReal };
  }

  /** Bomb: see combat.js. */
  useBomb() {
    return useBomb(this);
  }

  // ------------------------------------------------------------- controls
  togglePause() {
    if (this.state !== 'playing') return;
    this.paused = !this.paused;
    this.audio.play('ui_pause');
  }

  reset() {
    this.paused = false;
    this.state = 'playing';
    this.timeScale = 1;
    this._slowMo = null;
    this.bullets.length = 0;
    this.enemyBullets.length = 0;
    this.enemies.length = 0;
    this.powerups.length = 0;
    this.telegraphs.length = 0;
    this.particles.length = 0;
    this.popups.length = 0;
    this.coins.length = 0;
    this.flashes.length = 0;
    this.shake = { amp: 0, dur: 0, t: 0, ox: 0, oy: 0 };
    this.continuousShake = 0;
    this.darkOverlay = 0;
    this.score.reset();
    this.player.reset();
    if (this.waves) this.waves.reset();
    if (this.boss) this.boss.reset();
    this.bossDeath = null;
    this.victoryAlpha = 0;
    this.stageCleared = false;
    this.audio.setMusic('music_stage');
  }

  restart() {
    this.startLevel(this.currentLevel);
  }

  // ---------------------------------------------------------------- render
  resize() {
    if (typeof window === 'undefined') return;
    const vw = window.innerWidth || S.width;
    const vh = window.innerHeight || S.height;
    const dpr = window.devicePixelRatio || 1;
    const fit = Math.min(vw / S.width, vh / S.height);
    const cssW = S.width * fit;
    const cssH = S.height * fit;
    this.canvas.style.width = `${cssW}px`;
    this.canvas.style.height = `${cssH}px`;
    this.canvas.width = Math.round(cssW * dpr);
    this.canvas.height = Math.round(cssH * dpr);
    this.viewScale = (cssW * dpr) / S.width;
  }

  render() {
    const ctx = this.ctx;
    ctx.setTransform(this.viewScale, 0, 0, this.viewScale, 0, 0);
    this.bg.draw(ctx);
    ctx.save();
    ctx.translate(this.shake.ox, this.shake.oy);
    for (const tg of this.telegraphs) tg.draw(ctx);
    for (const b of this.enemyBullets) b.draw(ctx);
    drawPowerups(this, ctx);
    for (const b of this.bullets) b.draw(ctx);
    this.player.draw(ctx, this.input.dragging);
    drawParticles(this, ctx);
    ctx.restore();
    if (this.darkOverlay > 0) {
      ctx.globalAlpha = this.darkOverlay;
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, S.width, S.height);
      ctx.globalAlpha = 1;
    }
    drawPopups(this, ctx);
    this._drawFlashes(ctx);
    if (this.victoryAlpha > 0) {
      ctx.globalAlpha = this.victoryAlpha;
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, S.width, S.height);
      ctx.globalAlpha = 1;
    }
    drawHud(this, ctx);
    drawScreens(this, ctx);
    if (this.state === 'playing' && !this.paused) this._drawControls(ctx);
  }

  _drawFlashes(ctx) {
    for (const f of this.flashes) {
      const k = Math.max(0, 1 - f.t / f.dur);
      ctx.globalAlpha = f.alpha * k;
      ctx.fillStyle = f.color;
      ctx.fillRect(0, 0, S.width, S.height);
    }
    ctx.globalAlpha = 1;
  }

  _drawControls(ctx) {
    const b = CONFIG.controls.bombButton;
    const p = CONFIG.controls.pauseButton;
    ctx.save();
    ctx.globalAlpha = 0.65;
    ctx.fillStyle = b.color;
    ctx.strokeStyle = b.rim;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(b.centerX, b.centerY, b.radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = '#ffffff';
    ctx.font = `bold ${Math.round(b.radius * 0.34)}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(b.label, b.centerX, b.centerY);

    ctx.globalAlpha = 0.8;
    ctx.strokeStyle = p.color;
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(p.centerX - 8, p.centerY - 10);
    ctx.lineTo(p.centerX - 8, p.centerY + 10);
    ctx.moveTo(p.centerX + 8, p.centerY - 10);
    ctx.lineTo(p.centerX + 8, p.centerY + 10);
    ctx.stroke();
    ctx.restore();
  }
}
