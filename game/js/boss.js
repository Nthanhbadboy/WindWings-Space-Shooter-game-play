// Boss state machine: hidden -> warning -> enter -> idle -> attack
// (telegraph -> active) -> recover -> idle ... -> dead.
// Phase transitions / enrage land in step 6. All timers are delta-driven.
import { CONFIG } from './config.js';
import { Timer, weightedPick } from './utils.js';
import { Powerup } from './powerups.js';
import { ATTACKS, telegraphTime } from './boss_attacks.js';

const B = CONFIG.boss;
const S = CONFIG.screen;

export class Boss {
  constructor(game) {
    this.game = game;
    this.reset();
  }

  reset() {
    this.x = S.width / 2;
    this.y = -180;
    this.radius = B.radius;
    this.hp = B.maxHp;
    this.phase = 1;
    this.enraged = false;
    this.state = 'hidden';       // hidden|warning|enter|idle|attack|recover|transition|dead
    this.warnT = 0;
    this.attack = null;
    this.cooldown = new Timer(0);
    this.recoverT = new Timer(B.recover);
    this.transT = new Timer(0);
    this.pendingPhase = 1;
    this.patternHistory = [];
    this.forcePattern = null;    // test hook
    this.hurtFlashT = 0;
    this.time = 0;
    this.bobT = 0;
    this.spin = 0;
    this.deathT = 0;
  }

  get visible() {
    return this.state !== 'hidden';
  }

  get alive() {
    return this.state !== 'dead' && this.state !== 'hidden' && this.hp > 0;
  }

  get vulnerable() {
    return this.state === 'idle' || this.state === 'attack'
      || this.state === 'recover' || this.state === 'transition';
  }

  get hpFrac() {
    return Math.max(0, Math.min(1, this.hp / B.maxHp));
  }

  get cooldownTime() {
    if (this.enraged) return B.enrage.cooldown;
    return B.phases[this.phase].cooldown;
  }

  /** Called by the game when waves are cleared. */
  begin() {
    this.state = 'warning';
    this.warnT = 0;
    this.game.audio.play('boss_warning');
    this.game.audio.setMusic('music_boss');
  }

  // ---------------------------------------------------------------- update
  update(dt) {
    this.time += dt;
    this._checkPhase();
    if (this.hurtFlashT > 0) this.hurtFlashT -= dt;
    switch (this.state) {
      case 'warning':
        this.warnT += dt;
        if (this.warnT >= B.warning.duration) {
          this.state = 'enter';
          this.y = -180;
        }
        break;
      case 'enter':
        this.y += B.entrySpeed * dt;
        if (this.y >= B.entryY) {
          this.y = B.entryY;
          this.state = 'idle';
          this.cooldown.reset(this.cooldownTime * 0.6);
        }
        break;
      case 'idle':
        this._moveIdle(dt);
        this.cooldown.update(dt);
        if (this.cooldown.done) this._startAttack();
        break;
      case 'attack':
        this._moveIdle(dt, 0.35); // slower drift while attacking
        this._updateAttack(dt);
        break;
      case 'recover':
        this._moveIdle(dt);
        this.recoverT.update(dt);
        if (this.recoverT.done) {
          this.state = 'idle';
          this.cooldown.reset(this.cooldownTime);
        }
        break;
      case 'transition':
        this.transT.update(dt);
        if (this.pendingPhase === 3) {
          // dark overlay fades in and out across the transition
          this.game.darkOverlay = B.transition.p3DarkAlpha
            * Math.sin(Math.PI * this.transT.progress);
        }
        if (this.transT.done) this._finishTransition();
        break;
      default:
        break;
    }
  }

  /** Threshold checks: phase transitions + enrage. */
  _checkPhase() {
    if (this.state === 'hidden' || this.state === 'warning'
      || this.state === 'enter' || this.state === 'dead'
      || this.state === 'transition') return;
    const f = this.hpFrac;
    if (this.phase === 1 && f <= B.thresholds.phase2) this._startTransition(2);
    else if (this.phase === 2 && f <= B.thresholds.phase3) this._startTransition(3);
    if (this.phase === 3 && !this.enraged && f < B.thresholds.enrage) {
      this.enraged = true;
      this.game.continuousShake = B.enrage.continuousShake;
    }
  }

  _startTransition(to) {
    const tr = B.transition;
    this.pendingPhase = to;
    this.state = 'transition';
    this.transT.reset(tr.duration);
    this._cancelAttack();
    this.game.addShake(tr.shake.amp, tr.shake.dur);
    this.game.addFlash('#ffffff', tr.flashAlpha, tr.whiteFlash);
    this.game.setSlowMo(tr.slowMo.scale, tr.slowMo.dur);
    this.game.audio.play('boss_growl');
    this.phase = to; // sprite recolors immediately
    if (to === 3) {
      this.hp = Math.min(B.maxHp, this.hp + B.maxHp * B.phase3HealPct);
      this.game.addFlash('#ff2b2b', 0.5, 0.3);
    }
  }

  _finishTransition() {
    this.game.darkOverlay = 0;
    this.state = 'idle';
    this.cooldown.reset(this.cooldownTime);
    // guaranteed boss power-up drop on each phase transition
    this.game.powerups.push(new Powerup(this.x, this.y + this.radius, 'weapon'));
  }

  _cancelAttack() {
    if (!this.attack) return;
    for (const tg of this.attack.data._tg || []) {
      const i = this.game.telegraphs.indexOf(tg);
      if (i >= 0) this.game.telegraphs.splice(i, 1);
    }
    this.attack = null;
  }

  /** Phase movement: p1 horizontal bob; p2 slight spin; p3 pulse (draw). */
  _moveIdle(dt, scale = 1) {
    this.bobT += dt;
    if (this.phase === 1) {
      const bob = B.phases[1].bob;
      this.x = S.width / 2 + Math.sin(this.bobT * Math.PI * 2 * bob.freq) * bob.amp * scale;
    } else if (this.phase === 2) {
      this.spin += (B.phases[2].spinDegPerSec * Math.PI / 180) * dt;
    }
  }

  // ---------------------------------------------------------------- attack
  _pickPattern() {
    if (this.forcePattern) {
      const id = this.forcePattern;
      this.forcePattern = null;
      return id;
    }
    const weights = B.patternWeights[this.phase].filter((e) => ATTACKS[e.id]);
    return weightedPick(weights, this.patternHistory, B.maxSamePatternInRow);
  }

  _startAttack() {
    const id = this._pickPattern();
    const def = ATTACKS[id];
    if (!def) {
      this.cooldown.reset(this.cooldownTime);
      return;
    }
    this.patternHistory.push(id);
    if (this.patternHistory.length > 3) this.patternHistory.shift();
    const before = this.game.telegraphs.length;
    const data = def.start(this, this.game) || {};
    data._tg = this.game.telegraphs.slice(before); // telegraphs owned by this attack
    this.attack = {
      id,
      def,
      stage: 'telegraph',
      timer: new Timer(telegraphTime(this, id)),
      data,
    };
    this.state = 'attack';
  }

  _updateAttack(dt) {
    const atk = this.attack;
    if (atk.stage === 'telegraph') {
      atk.timer.update(dt);
      if (atk.timer.done) atk.stage = 'active';
      return;
    }
    // HARD RULE: damage only happens in 'active', i.e. after the telegraph
    const done = atk.def.active(this, this.game, atk, dt);
    if (done) {
      this.attack = null;
      this.state = 'recover';
      this.recoverT.reset(B.recover);
    }
  }

  // ---------------------------------------------------------------- damage
  hurt(dmg) {
    if (this.state === 'dead' || this.state === 'hidden') return false;
    if (this.state === 'warning' || this.state === 'enter') return false; // entry i-frames
    this.hp -= dmg;
    this.hurtFlashT = B.hurtFlash;
    this.game.audio.play('boss_hit');
    if (this.hp <= 0) {
      this.hp = 0;
      this.die();
    }
    return true;
  }

  die() {
    this.state = 'dead';
    this._cancelAttack();
    this.game.continuousShake = 0;
    this.deathT = 0;
    this.game.audio.play('boss_death');
    this.game.onBossDeath();
  }

  // ----------------------------------------------------------------- draw
  draw(ctx) {
    if (!this.visible || this.state === 'dead') return;
    const r = this.radius;
    const color = this.phase >= 3 ? B.colors.phase3
      : this.phase === 2 ? B.colors.phase2 : B.colors.phase1;
    const pulse = this.phase === 3 ? 1 + Math.sin(this.time * Math.PI * 2
      * B.phases[3].pulseFreq) * 0.04 : 1;

    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.scale(pulse, pulse);
    ctx.rotate(this.phase === 2 ? Math.sin(this.spin) * 0.08 : 0);

    // tentacle wings (4 per side)
    ctx.strokeStyle = color;
    ctx.lineWidth = 10;
    ctx.lineCap = 'round';
    for (const s of [-1, 1]) {
      for (let i = 0; i < 4; i++) {
        const wig = Math.sin(this.time * 3 + i) * 8;
        ctx.beginPath();
        ctx.moveTo(s * r * 0.5, -r * 0.2 + i * r * 0.22);
        ctx.quadraticCurveTo(
          s * r * (1.1 + i * 0.12), -r * 0.5 + i * r * 0.3 + wig,
          s * r * (1.35 + i * 0.1), r * 0.1 + i * r * 0.28 + wig
        );
        ctx.stroke();
      }
    }

    // dome hull
    ctx.fillStyle = color;
    ctx.strokeStyle = B.colors.outline;
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.ellipse(0, 0, r * 0.78, r * 0.92, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // brow plates
    ctx.fillStyle = B.colors.outline;
    ctx.beginPath();
    ctx.ellipse(0, -r * 0.45, r * 0.6, r * 0.34, 0, Math.PI, 0);
    ctx.fill();

    // eyes / core
    const eye = 0.8 + 0.2 * Math.sin(this.time * 5);
    ctx.fillStyle = B.colors.core;
    ctx.globalAlpha = eye;
    for (const s of [-1, 1]) {
      ctx.beginPath();
      ctx.arc(s * r * 0.3, -r * 0.12, r * 0.14, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.beginPath();
    ctx.arc(0, r * 0.3, r * 0.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;

    // red flash tint while an aimed-barrage telegraph charges
    if (this.attack && this.attack.stage === 'telegraph' && this.attack.data.flash) {
      ctx.globalAlpha = 0.35 + 0.3 * Math.sin(this.time * 20);
      ctx.fillStyle = '#ff2b2b';
      ctx.beginPath();
      ctx.ellipse(0, 0, r * 0.78, r * 0.92, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 1;
    }

    // white hurt flash (0.2s)
    if (this.hurtFlashT > 0) {
      ctx.globalAlpha = this.hurtFlashT / B.hurtFlash;
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.ellipse(0, 0, r * 0.78, r * 0.92, 0, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
    ctx.globalAlpha = 1;
  }
}
