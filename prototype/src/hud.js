import { ICONS } from './art.js';

// ảnh khai báo tĩnh trong art.js — Vite mới đóng gói được cho bản GitHub Pages
const ICON = {
  pause: ICONS.pause,
  sound: ICONS.sound,
  star: ICONS.star,
  skull: ICONS.skull,
};

/** HUD trong trận + các màn hình gắn với trận (tạm dừng, kết quả). */
export class Hud {
  constructor() {
    const $ = (id) => document.getElementById(id);
    this.el = {
      hud: $('hud'),
      score: $('score'),
      combo: $('combo'),
      hpText: $('hpText'),
      hpFill: $('hpFill'),
      shieldDots: $('shieldDots'),
      weaponDots: $('weaponDots'),
      droneDots: $('droneDots'),
      hudCoins: $('hudCoins'),
      wave: $('wave'),
      waveLabel: $('waveLabel'),
      hudTimer: $('hudTimer'),
      objective: $('objective'),
      bossWrap: $('bossBarWrap'),
      bossName: $('bossName'),
      bossFill: $('bossFill'),
      banner: $('banner'),
      flash: $('flash'),
      joystickHint: $('joystickHint'),
      btnPause: $('btnPause'),
      btnSound: $('btnSound'),
      portrait: $('portrait'),
      enemySkull: $('enemySkull'),
      loadingFill: $('loadingFill'),
      loadingText: $('loadingText'),
      screens: {
        load: $('screen-loading'),
        pause: $('screen-pause'),
        result: $('screen-result'),
      },
      resKicker: $('resKicker'),
      resMode: $('resMode'),
      resTitle: $('resTitle'),
      resStars: $('resStars'),
      resScore: $('resScore'),
      resBest: $('resBest'),
      resKills: $('resKills'),
      resCoins: $('resCoins'),
      btnNextLevel: $('btnNextLevel'),
      errorBox: $('errorBox'),
      curCoins: $('curCoins'),
    };

    this.last = {
      score: -1, wave: -1, hp: -1, shields: -1, weapon: -1, boss: -1,
      combo: -1, coins: -1, timer: -2, objective: '', drones: -1,
    };
    this.shieldEls = [];
    this.weaponEls = [];
    this.droneEls = [];
    this._buildShieldDots(5);
    this._buildWeaponDots(5);
    this._buildDroneDots(3);
    this.setIcons();
    this.ui = null;
    this.onPauseShow = null;
  }

  setUI(ui) { this.ui = ui; }

  setIcons() {
    const pause = this.el.btnPause?.querySelector('img');
    const sound = this.el.btnSound?.querySelector('img');
    if (pause) pause.src = ICON.pause;
    if (sound) sound.src = ICON.sound;
    if (this.el.enemySkull) this.el.enemySkull.src = ICON.skull;
  }

  /** Chân dung tàu trong HUD (ô vát 74x58, DO_DAC_UI §2). */
  setPortrait(src) {
    if (this.el.portrait && src) this.el.portrait.src = src;
  }

  setSoundIcon(muted) {
    const img = this.el.btnSound?.querySelector('img');
    this.el.btnSound?.classList.toggle('is-off', !!muted);
  }

  _buildShieldDots(count) {
    this.el.shieldDots.innerHTML = '';
    this.shieldEls = [];
    for (let i = 0; i < count; i++) {
      const s = document.createElement('span');
      s.className = 'shield-dot'; // .ww-seg span — đốt năng lượng nghiêng -26°
      this.el.shieldDots.appendChild(s);
      this.shieldEls.push(s);
    }
  }

  _buildWeaponDots(count) {
    this.el.weaponDots.innerHTML = '';
    this.weaponEls = [];
    for (let i = 0; i < count; i++) {
      const s = document.createElement('span');
      s.className = 'weapon-dot';
      this.el.weaponDots.appendChild(s);
      this.weaponEls.push(s);
    }
  }

  _buildDroneDots(count) {
    this.el.droneDots.innerHTML = '';
    this.droneEls = [];
    for (let i = 0; i < count; i++) {
      const s = document.createElement('span');
      s.className = 'drone-dot';
      this.el.droneDots.appendChild(s);
      this.droneEls.push(s);
    }
  }

  /** name: 'pause' | 'result' (bỏ trống = quay lại HUD) */
  showScreen(name) {
    Object.entries(this.el.screens).forEach(([key, node]) => {
      if (!node) return;
      if (key === 'load') {
        node.classList.toggle('hidden', name !== 'load');
        return;
      }
      node.classList.toggle('hidden', key !== name);
    });
    const inGame = name === 'pause' || name === 'result';
    this.el.hud.classList.toggle('hidden', inGame);
    if (name === 'pause') this.onPauseShow?.();
    if (inGame) this.ui?.hideChrome?.();
  }

  hideScreens() {
    Object.values(this.el.screens).forEach((n) => n?.classList.add('hidden'));
    this.ui?.hideAll?.();
    this.el.hud.classList.remove('hidden');
  }

  setLoading(pct) {
    const v = Math.round(pct * 100);
    if (this.el.loadingFill) this.el.loadingFill.style.width = `${v}%`;
    if (this.el.loadingText) this.el.loadingText.textContent = `${v}%`;
  }

  setObjective(text) {
    if (text === this.last.objective) return;
    this.el.objective.textContent = text || '';
    this.last.objective = text;
  }

  setCoins(n) {
    if (this.el.hudCoins) this.el.hudCoins.textContent = String(n);
    if (this.el.curCoins) this.el.curCoins.textContent = Number(n).toLocaleString('vi-VN');
    this.last.coins = n;
  }

  setBossName(name) {
    if (!name) return;
    this.el.bossName.textContent = String(name).toUpperCase();
  }

  update({ score, wave, remaining = null, hpPct, hpValue, shields, weapon, bossPct, combo = 1, timer = null, objective = null, coins = null, drones = null }) {
    if (score !== undefined && score !== this.last.score) {
      this.el.score.textContent = score.toLocaleString('vi-VN');
      this.last.score = score;
    }
    if (combo !== this.last.combo) {
      this.el.combo.textContent = `x${combo}`;
      this.el.combo.classList.toggle('hidden', combo <= 1);
      this.last.combo = combo;
    }
    // WindWings hiển thị SỐ ĐỊCH CÒN LẠI (kèm đầu lâu); fallback = số đợt
    const wv = remaining !== null && remaining !== undefined ? remaining : wave;
    if (wv !== undefined && wv !== this.last.wave) {
      this.el.wave.textContent = String(wv);
      this.last.wave = wv;
    }
    if (hpPct !== undefined) {
      const hp = Math.round(hpPct);
      if (hp !== this.last.hp) {
        this.el.hpFill.style.width = `${Math.max(0, Math.min(100, hp))}%`;
        this.el.hpFill.classList.toggle('low', hp <= 25);
        this.el.hpFill.classList.toggle('mid', hp > 25 && hp <= 50);
        this.last.hp = hp;
      }
    }
    if (hpValue !== undefined) this.el.hpText.textContent = String(Math.max(0, Math.round(hpValue)));
    if (shields !== undefined && shields !== this.last.shields) {
      this.shieldEls.forEach((el, i) => el.classList.toggle('on', i < shields));
      this.last.shields = shields;
    }
    if (weapon !== undefined && weapon !== this.last.weapon) {
      this.weaponEls.forEach((el, i) => el.classList.toggle('on', i < weapon));
      this.last.weapon = weapon;
    }
    if (drones !== null && drones !== undefined && drones !== this.last.drones) {
      this.droneEls.forEach((el, i) => el.classList.toggle('on', i < drones));
      this.last.drones = drones;
    }
    if (timer !== this.last.timer) {
      const show = timer !== null && timer !== undefined;
      this.el.hudTimer.classList.toggle('hidden', !show);
      this.el.hudTimer.textContent = show ? `${Math.max(0, Math.ceil(timer))}s` : '';
      this.last.timer = timer;
    }
    if (objective !== null && objective !== undefined) this.setObjective(objective);
    if (coins !== null && coins !== undefined && coins !== this.last.coins) this.setCoins(coins);
    if (bossPct === null || bossPct === undefined) {
      this.el.bossWrap.classList.add('hidden');
      this.last.boss = -1;
    } else {
      this.el.bossWrap.classList.remove('hidden');
      const b = Math.round(bossPct);
      if (b !== this.last.boss) {
        this.el.bossFill.style.width = `${Math.max(0, Math.min(100, b))}%`;
        this.last.boss = b;
      }
    }
  }

  banner(text, danger = false) {
    const b = this.el.banner;
    if (!b) return;
    b.textContent = text;
    b.classList.remove('show', 'danger');
    void b.offsetWidth;
    b.classList.add('show');
    if (danger) b.classList.add('danger');
  }

  damageFlash() {
    const f = this.el.flash;
    if (!f) return;
    f.classList.remove('on');
    void f.offsetWidth;
    f.classList.add('on');
    // dọn lớp phủ chắc chắn (animation đã tự về 0, đây là lưới an toàn)
    clearTimeout(this._flashTimer);
    this._flashTimer = setTimeout(() => f.classList.remove('on'), 380);
  }

  showResult({ mode, modeLabel, success, score, best, newRecord, kills, wave, stars, coins, level, chapter, daily, onNext }) {
    const el = this.el;
    el.resKicker.textContent = newRecord ? 'KỶ LỤC MỚI' : (modeLabel || 'KẾT THÚC');
    el.resTitle.textContent = success ? 'HOÀN THÀNH' : 'TÀU ĐÃ BỊ HẠ';
    if (success && level) el.resTitle.textContent = `MÀN ${level.index} HOÀN THÀNH`;
    if (success && daily) el.resTitle.textContent = 'THỬ THÁCH HOÀN THÀNH';

    if (el.resMode) {
      if (level) el.resMode.textContent = `CH ${chapter || level.chapter} · MÀN ${level.index}`;
      else if (mode === 'daily') el.resMode.textContent = daily?.modifier?.name || 'HẰNG NGÀY';
      else el.resMode.textContent = `ĐỢT ${wave || 1}`;
    }

    el.resStars.innerHTML = '';
    if (success) {
      for (let i = 0; i < 3; i++) {
        const s = document.createElement('img');
        s.src = ICON.star;
        s.alt = '';
        s.className = i < stars ? 'on' : '';
        el.resStars.appendChild(s);
      }
      el.resStars.classList.remove('hidden');
    } else {
      el.resStars.classList.add('hidden');
    }

    el.resScore.textContent = score.toLocaleString('vi-VN');
    el.resBest.textContent = best.toLocaleString('vi-VN');
    el.resKills.textContent = String(kills);
    el.resCoins.textContent = `+${coins.toLocaleString('vi-VN')}`;

    el.btnNextLevel.classList.toggle('hidden', !onNext);
    el.btnNextLevel.onclick = onNext ? () => onNext() : null;

    this.showScreen('result');
  }

  hideJoystickHint() {
    this.el.joystickHint?.classList.add('hide');
  }

  showError(message) {
    if (!this.el.errorBox) return;
    this.el.errorBox.textContent = message;
    this.el.errorBox.classList.remove('hidden');
  }
}
