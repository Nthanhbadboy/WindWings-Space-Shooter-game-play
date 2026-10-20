// Boss state machine: hidden -> warning -> enter -> idle -> attack
// (telegraph -> active) -> recover -> idle ... -> dead.
// Phase transitions / enrage land in step 6. All timers are delta-driven.
import { CONFIG } from './config.js';
import { Timer, weightedPick } from './utils.js';
import { Powerup } from './powerups.js';
import { ATTACKS, telegraphTime } from './boss_attacks.js';
import { drawBossRig } from './boss_rigs.js';

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
    this.type = 'tyrant';
    this.bossName = B.name;
    this.hpMul = 1;
    this.maxHp = B.maxHp;
    this.hp = B.maxHp;
    this.anim = { state: 'enter', t: 0, kick: 0, blink: 0, blinkT: 2.5 };
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
    return Math.max(0, Math.min(1, this.hp / this.maxHp));
  }

  get cooldownTime() {
    if (this.enraged) return B.enrage.cooldown;
    return B.phases[this.phase].cooldown;
  }

  /** Apply per-level boss config {type,name,hpMul} or null for default. */
  configure(cfg) {
    if (!cfg) {
      this.type = 'tyrant';
      this.bossName = B.name;
      this.hpMul = 1;
    } else {
      this.type = cfg.type;
      this.bossName = cfg.name;
      this.hpMul = cfg.hpMul;
    }
    this.maxHp = Math.round(B.maxHp * this.hpMul);
    this.hp = this.maxHp;
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
    this._updateAnim(dt); // runs last: reflects this frame's FSM state
  }

  /** Procedural animation clock: blink, recoil kick, state label. */
  _updateAnim(dt) {
    const a = this.anim;
    a.t += dt;
    a.kick = Math.max(0, a.kick - dt * 4);
    a.blinkT -= dt;
    if (a.blinkT <= 0) {
      a.blink = 0.12;
      a.blinkT = 2 + Math.random() * 3;
    }
    if (a.blink > 0) a.blink -= dt;
    let st = 'idle';
    if (this.state === 'warning' || this.state === 'enter') st = 'enter';
    else if (this.state === 'attack') st = this.attack && this.attack.stage === 'telegraph' ? 'charge' : 'fire';
    else if (this.state === 'transition') st = 'break';
    else if (this.state === 'dead') st = 'die';
    if (st === 'fire' && a.state !== 'fire') a.kick = 1; // recoil on shot
    a.state = st;
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
      this.hp = Math.min(this.maxHp, this.hp + this.maxHp * B.phase3HealPct);
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
    drawBossRig(this, ctx);
  }
}
