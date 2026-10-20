import { PLAYER_SHIPS, SHIP_BY_ID, SHIP_MAX_LEVEL } from './ships.js';
import {
  UPGRADES, UPGRADE_KEYS, TOTAL_TECH_LEVELS,
  upgradeCost, upgradeGemCost, shipLevelCost, shipLevelGemCost, computeStats,
} from './save.js';
import { CHAPTERS, MODES, levelInfo } from './content.js';
import { SHIP_PORTRAIT, SHIP_PORTHOLE, ICONS, TECH_ART, SHIP_ART } from './art.js';
import { TEST_AUTO_FIRE, TEST_UNLOCK_ALL } from './devflags.js';

const SHIP_IDS = ['striker', 'zenith', 'challenger', 'spitfire', 'insurgent', 'executioner', 'omen', 'dispatcher'];
// ảnh đã khai báo tĩnh trong art.js để Vite đóng gói được (bản GitHub Pages)
const ART = (id, kind = '') => (kind === 'porthole' ? SHIP_PORTHOLE[id] : SHIP_PORTRAIT[id]);
const THUMB = SHIP_PORTRAIT;
const PORTHOLE = SHIP_PORTHOLE;

const SCREENS = ['home', 'map', 'hangar', 'tech', 'store', 'settings', 'profile'];
const IN_GAME = ['pause', 'result'];

/** Đường đi của node trên bản đồ, % theo khung (0,0 = góc trên trái). */
const MAP_PATHS = {
  1: [[14, 92], [34, 84], [55, 88], [75, 78], [86, 62], [68, 52], [46, 55], [26, 45], [16, 28], [40, 13]],
  2: [[18, 90], [40, 92], [62, 84], [80, 70], [84, 52], [64, 46], [42, 50], [24, 38], [22, 20], [48, 10]],
  3: [[12, 88], [32, 92], [54, 84], [74, 76], [86, 58], [66, 48], [44, 52], [26, 42], [14, 26], [36, 12]],
  4: [[16, 92], [38, 86], [58, 90], [78, 80], [88, 64], [70, 54], [48, 58], [28, 48], [18, 30], [42, 14]],
  5: [[14, 90], [36, 92], [58, 86], [78, 74], [86, 56], [66, 46], [44, 50], [24, 40], [16, 24], [38, 10]],
  6: [[18, 92], [40, 88], [60, 92], [80, 82], [88, 66], [68, 56], [46, 60], [26, 50], [18, 32], [44, 15]],
};

const dailyKey = (d = new Date()) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

const num = (n) => Number(n || 0).toLocaleString('vi-VN');

const iconUrl = (name) => ICONS[name] || '';
const ICON = Object.fromEntries(
  ['star', 'coin', 'gem', 'lock', 'skull', 'drone', 'cannon', 'armor',
   'shield', 'magnet', 'pause', 'sound', 'music', 'check'].map((n) => [n, iconUrl(n)]),
);
const TECH_ICON = {
  cannon: TECH_ART.cannon, armor: TECH_ART.armor, shield: TECH_ART.shield,
  drone: TECH_ART.drone, magnet: TECH_ART.magnet,
};
const coinTag = (n) => `<img class="coin-ico" src="${ICON.coin}" alt="" /><b>${num(n)}</b>`;
const gemTag = (n) => `<img class="gem-ico" src="${ICON.gem}" alt="" /><b>${num(n)}</b>`;
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

export class UI {
  constructor({ profile, sfx, onStart, onSpeed }) {
    this.profile = profile;
    this.sfx = sfx;
    this.onStart = onStart;
    this.onSpeed = onSpeed || null;
    this.onShipChange = null;
    this.onControlChange = null;

    this.selectedShip = profile.shipId;
    // TEST: mở khoá hết nhưng vẫn bắt đầu từ chương 1 cho dễ theo dõi
    this.chapter = TEST_UNLOCK_ALL ? 1 : profile.chapter;
    this.techKey = 'cannon';
    this.quickMode = 'endless';
    this.installEvent = null;
    this.current = null;

    if (typeof localStorage !== 'undefined') {
      this.control = localStorage.getItem('ww3d_control') || 'joystick';
      // TEST: luôn tự động bắn dù người chơi từng chọn "bắn tay"
      this.autoFire = TEST_AUTO_FIRE || localStorage.getItem('ww3d_autofire') !== '0';
      const sp = Number(localStorage.getItem('ww3d_speed') || '100');
      this.speed = Number.isFinite(sp) ? sp : 100;
    } else {
      this.control = 'joystick';
      this.autoFire = true;
      this.speed = 100;
    }

    const $ = (id) => document.getElementById(id);
    this.el = {
      metaChrome: $('metaChrome'),
      screens: Object.fromEntries(SCREENS.map((id) => [id, $(`screen-${id}`)])),
      navTabs: Array.from(document.querySelectorAll('#bottomNav .nav-tab')),
      curStars: $('curStars'),
      curCoins: $('curCoins'),
      curGems: $('curGems'),
      premiumTime: $('premiumTime'),
      btnDaily: $('btnDaily'),
      storeBadge: $('storeBadge'),
      toast: $('toast'),

      // home
      homeShipImg: $('homeShipImg'),
      homeShip2Img: $('homeShip2Img'),
      homeShipLvl: $('homeShipLvl'),
      slotS1: $('slotS1'),
      slotS2: $('slotS2'),
      slotL: $('slotL'),
      slotR: $('slotR'),
      btnPlay: $('btnPlay'),
      btnArena: $('btnArena'),
      btnPvp: $('btnPvp'),
      btnDeal: $('btnDeal'),
      btnVip: $('btnVip'),
      btnProfile: $('btnProfile'),
      btnLogin: $('btnLogin'),
      btnSettingsHome: $('btnSettingsHome'),
      upgradePod: $('btnUpgradePod'),

      // map
      chapterRow: $('chapterRow'),
      mapNodes: $('mapNodes'),
      mapLine: $('mapLine'),
      btnMapChapters: $('btnMapChapters'),
      btnMapUpgrade: $('btnMapUpgrade'),

      // hangar
      shipTabName: $('shipTabName'),
      shipTabPips: $('shipTabPips'),
      hangarShipImg: $('hangarShipImg'),
      specLvl: $('specLvl'),
      specAtk: $('specAtk'),
      specHp: $('specHp'),
      specSpd: $('specSpd'),
      expFill: $('expFill'),
      expText: $('expText'),
      specPerk: $('specPerk'),
      btnBuyCoin: $('btnBuyCoin'),
      btnBuyGem: $('btnBuyGem'),
      shipGrid: $('shipGrid'),

      // tech
      techEmblem: $('techEmblem'),
      techName: $('techName'),
      techDesc: $('techDesc'),
      techLvl: $('techLvl'),
      techGrid: $('techGrid'),
      techRows: $('techRows'),
      techTotal: $('techTotal'),
      btnTechUpgrade: $('btnTechUpgrade'),
      btnTechGem: $('btnTechGem'),

      // store
      dealStreak: $('dealStreak'),
      dealCoins: $('dealCoins'),
      dealGems: $('dealGems'),
      btnClaimDaily: $('btnClaimDaily'),
      ex1: $('ex1'),
      ex5: $('ex5'),

      // settings
      settSound: $('settSound'),
      settMusic: $('settMusic'),
      settProfile: $('settProfile'),
      settInstall: $('settInstall'),
      settLang: $('settLang'),
      settAbout: $('settAbout'),
      settPrivacy: $('settPrivacy'),
      settReset: $('settReset'),

      // pause
      pauseStage: $('pauseStage'),
      pauseDiff: $('pauseDiff'),
      pauseObjectives: $('pauseObjectives'),
      ctrlBtns: Array.from(document.querySelectorAll('#screen-pause .ctrl-btn')),
      testNote: $('testNote'),
      techShipImg: $('techShipImg'),
      tapPins: Array.from(document.querySelectorAll('#techBay .tap-pin')),
      sliderMusic: $('sliderMusic'),
      sliderSound: $('sliderSound'),
      sliderSpeed: $('sliderSpeed'),
      speedVal: $('speedVal'),
      mMusic: $('mMusic'),
      mSound: $('mSound'),
      mSpeed: $('mSpeed'),
      speedVal2: $('speedVal2'),

      // profile
      profStage: $('profStage'),
      profStars: $('profStars'),
      profTech: $('profTech'),
      profRuns: $('profRuns'),
      profCampaign: $('profCampaign'),
      profEndless: $('profEndless'),
      profBoss: $('profBoss'),
      profDaily: $('profDaily'),

      // modal
      dailyModal: $('dailyModal'),
      dailyList: $('dailyList'),
      btnClaimDaily2: $('btnClaimDaily2'),
      btnCloseDaily: $('btnCloseDaily'),
      infoModal: $('infoModal'),
      infoTitle: $('infoTitle'),
      infoBody: $('infoBody'),
      btnCloseInfo: $('btnCloseInfo'),
      btnInfoOk: $('btnInfoOk'),
      resetModal: $('modalReset'),
      btnCloseReset: $('btnCloseReset'),
      btnResetNo: $('btnResetNo'),
      btnResetYes: $('btnResetYes'),
    };

    // TEST: nhắc rõ đang bật cờ test (tự ẩn khi tắt cờ)
    if (this.el.testNote && (TEST_UNLOCK_ALL || TEST_AUTO_FIRE)) {
      const bits = [];
      if (TEST_UNLOCK_ALL) bits.push('mở hết màn');
      if (TEST_AUTO_FIRE) bits.push('luôn tự bắn');
      this.el.testNote.textContent = `CHẾ ĐỘ TEST · ${bits.join(' · ')}`;
      this.el.testNote.classList.remove('hidden');
    }

    this._wire();
    this.refreshChrome();
    this._startClock();
    this.renderHome();
  }

  // ---------------------------------------------------------------- chrome
  _startClock() {
    const tick = () => {
      const now = new Date();
      const next = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1, 0, 0, 0);
      const left = Math.max(0, Math.floor((next - now) / 1000));
      const h = String(Math.floor(left / 3600)).padStart(2, '0');
      const m = String(Math.floor((left % 3600) / 60)).padStart(2, '0');
      const s = String(left % 60).padStart(2, '0');
      if (this.el.premiumTime) this.el.premiumTime.textContent = `${h}:${m}:${s}`;
      if (left === 0) this.refreshChrome();
    };
    tick();
    this._clock = setInterval(tick, 1000);
    if (this._clock && this._clock.unref) this._clock.unref();
  }

  refreshChrome() {
    const p = this.profile;
    if (this.el.curStars) this.el.curStars.textContent = num(p.totalStars);
    if (this.el.curCoins) this.el.curCoins.textContent = num(p.coins);
    if (this.el.curGems) this.el.curGems.textContent = num(p.gems);
    const claimed = p.data.lastDaily === dailyKey();
    if (this.el.storeBadge) this.el.storeBadge.classList.toggle('hidden', claimed);
    if (this.el.btnDaily) this.el.btnDaily.querySelector('.dot')?.classList.toggle('hidden', claimed);
    const mute = p.muted;
    this._setState(this.el.settSound, !mute ? 'BẬT' : 'TẮT', !mute);
    this._setState(this.el.settMusic, p.music ? 'BẬT' : 'TẮT', p.music);
  }

  hideChrome() {
    this.el.metaChrome?.classList.add('hidden');
  }

  hideAll() {
    SCREENS.forEach((id) => this.el.screens[id]?.classList.add('hidden'));
    IN_GAME.forEach((id) => document.getElementById(`screen-${id}`)?.classList.add('hidden'));
    this.el.metaChrome?.classList.add('hidden');
    this._closeModals();
  }

  show(name) {
    if (!SCREENS.includes(name)) return;
    this.current = name;
    SCREENS.forEach((id) => this.el.screens[id]?.classList.toggle('hidden', id !== name));
    IN_GAME.forEach((id) => document.getElementById(`screen-${id}`)?.classList.add('hidden'));
    document.getElementById('screen-loading')?.classList.add('hidden');
    this.el.metaChrome?.classList.remove('hidden');
    this.el.navTabs.forEach((t) => t.classList.toggle('active', t.dataset.goto === name));
    this.refreshChrome();

    if (name === 'home') this.renderHome();
    else if (name === 'map') this.renderMap();
    else if (name === 'hangar') this.renderHangar();
    else if (name === 'tech') this.renderTech();
    else if (name === 'store') this.renderStore();
    else if (name === 'settings') this.renderSettings();
    else if (name === 'profile') this.renderProfile();
    const sc = this.el.screens[name];
    if (sc) sc.scrollTop = 0;
  }

  toast(msg, ms = 1800) {
    const t = this.el.toast;
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(this._toastT);
    this._toastT = setTimeout(() => t.classList.remove('show'), ms);
  }

  _setState(tile, label, on) {
    if (!tile) return;
    tile.classList.toggle('off', !on);
    let s = tile.querySelector('.sett-state');
    if (!s) {
      s = document.createElement('span');
      s.className = 'sett-state';
      tile.appendChild(s);
    }
    s.textContent = label;
  }

  _modal(name, open) {
    const node = name === 'daily' ? this.el.dailyModal
      : name === 'reset' ? this.el.resetModal
      : this.el.infoModal;
    node?.classList.toggle('hidden', !open);
  }

  _closeModals() {
    this._modal('daily', false);
    this._modal('info', false);
  }

  openInfo(title, body) {
    if (!this.el.infoModal) return;
    this.el.infoTitle.textContent = title;
    this.el.infoBody.textContent = body;
    this._modal('info', true);
  }

  // ---------------------------------------------------------------- wiring
  _wire() {
    const click = (node, fn) => node?.addEventListener('click', (e) => {
      e.preventDefault();
      this.sfx?.click?.();
      fn(e);
    });

    document.addEventListener('click', (e) => {
      const go = e.target.closest?.('[data-goto]');
      if (go && !go.disabled) {
        e.preventDefault();
        this.sfx?.click?.();
        this.show(go.dataset.goto);
      }
    });

    // ---- home
    this.el.tapPins.forEach((pin) => {
      click(pin, () => {
        this.techKey = pin.dataset.key;
        this.renderTech();
      });
    });

    click(this.el.btnPlay, () => this.show('map'));
    click(this.el.btnArena, () => this.startMode(this.quickMode));
    click(this.el.btnPvp, () => this.toast('PVP SẼ MỞ Ở BẢN CẬP NHẬT SAU'));
    click(this.el.btnDeal, () => { this.show('store'); this.openDaily(); });
    click(this.el.btnVip, () => this.openInfo('VIP', 'Gói VIP đang được chuẩn bị.\nHiện tại mọi nâng cấp đều mua bằng xu và gem kiếm trong game — không có nội dung trả phí.'));
    click(this.el.btnProfile, () => this.show('profile'));
    click(this.el.btnLogin, () => this.openInfo('ĐĂNG NHẬP', 'Bản chơi này lưu tiến trình ngay trên máy (localStorage), không cần tài khoản.\nKhi phát hành APK chính thức, đăng nhập Google Play Games sẽ đồng bộ hồ sơ giữa các thiết bị.'));
    click(this.el.btnSettingsHome, () => this.show('settings'));
    click(this.el.upgradePod, () => this.show('tech'));
    click(this.el.slotS1, () => this.show('hangar'));
    click(this.el.slotS2, () => this.toast('KHOANG S2: MỞ KHI CÓ DRONE HỘ VỆ'));
    click(this.el.slotL, () => this.show('hangar'));
    click(this.el.slotR, () => this.toast('KHOANG R: PVP ĐANG PHÁT TRIỂN'));

    document.querySelectorAll('.mode-chips .chip').forEach((chip) => {
      click(chip, () => {
        this.quickMode = chip.dataset.mode || 'endless';
        document.querySelectorAll('.mode-chips .chip').forEach((c) => c.classList.toggle('active', c === chip));
        this.sfx?.click?.();
      });
    });

    // ---- map
    click(this.el.btnMapChapters, () => {
      const max = Math.min(CHAPTERS.length, this.profile.chapter);
      if (max <= 1) {
        this.toast('HẠ BOSS CHƯƠNG 1 ĐỂ MỞ CHƯƠNG 2');
        return;
      }
      this.chapter = this.chapter >= max ? 1 : this.chapter + 1;
      this.renderMap();
      const ch = CHAPTERS[this.chapter - 1];
      this.toast(`CHƯƠNG ${this.chapter} · ${ch.name}`);
    });
    click(this.el.btnMapUpgrade, () => this.show('tech'));

    // ---- hangar
    click(this.el.btnBuyCoin, () => this.buyShip('coins'));
    click(this.el.btnBuyGem, () => this.buyShip('gems'));

    // ---- tech
    click(this.el.btnTechUpgrade, () => this.upgradeTech('coins'));
    click(this.el.btnTechGem, () => this.upgradeTech('gems'));

    // ---- store
    click(this.el.btnClaimDaily, () => this.claimDaily());
    click(this.el.btnClaimDaily2, () => this.claimDaily());
    click(this.el.btnCloseDaily, () => this._modal('daily', false));
    click(this.el.ex1, () => this.exchange(1));
    click(this.el.ex5, () => this.exchange(5));

    // ---- settings
    click(this.el.settSound, () => {
      const muted = !this.sfx.muted;
      this.sfx.setMuted(muted);
      this.profile.setMuted(muted);
      this.onSoundChange?.(muted);
      this.refreshChrome();
      this.toast(muted ? 'ĐÃ TẮT ÂM THANH' : 'ĐÃ BẬT ÂM THANH');
    });
    click(this.el.settMusic, () => {
      const on = !this.profile.music;
      this.profile.setMusic(on);
      this.sfx.setMusic?.(on);
      this.refreshChrome();
      this.toast(on ? 'ĐÃ BẬT NHẠC NỀN' : 'ĐÃ TẮT NHẠC NỀN');
    });
    click(this.el.settProfile, () => this.show('profile'));
    click(this.el.settInstall, () => this.install());
    click(this.el.settLang, () => this.openInfo('NGÔN NGỮ', 'Hiện có: Tiếng Việt.\nBản tiếng Anh sẽ được thêm cùng lúc phát hành APK.'));
    click(this.el.settAbout, () => this.openInfo('GIỚI THIỆU', 'WINDWINGS 3D — galaxy shooter dọc màn hình.\n\nĐồ hoạ 3D: three.js\nMô hình: Quaternius (CC0 1.0)\nGiao diện & hiệu ứng: Kenney (CC0 1.0)\n\nPhiên bản 1.0 · làm cho Android, chơi được trên web.'));
    click(this.el.settPrivacy, () => this.openInfo('RIÊNG TƯ', 'Game không gửi dữ liệu lên máy chủ.\nToàn bộ tiến trình (xu, gem, tàu, sao) nằm trong localStorage của thiết bị và bị xoá khi bạn xoá dữ liệu trình duyệt hoặc dùng nút XOÁ DỮ LIỆU.'));
    click(this.el.settReset, () => this._modal('reset', true));
    click(this.el.btnCloseReset, () => this._modal('reset', false));
    click(this.el.btnResetNo, () => this._modal('reset', false));
    click(this.el.btnResetYes, () => {
      this.profile.reset();
      this.selectedShip = this.profile.shipId;
      this.chapter = TEST_UNLOCK_ALL ? 1 : this.profile.chapter;
      this.onShipChange?.(this.profile.shipId);
      this._modal('reset', false);
      this.refreshChrome();
      this.show('home');
      this.toast('ĐÃ XOÁ DỮ LIỆU');
    });

    // ---- modal
    click(this.el.btnCloseInfo, () => this._modal('info', false));
    click(this.el.btnInfoOk, () => this._modal('info', false));
    [this.el.dailyModal, this.el.resetModal].forEach((m) => m?.addEventListener('click', (e) => {
      if (e.target === m) m.classList.add('hidden');
    }));

    // ---- pause controls
    this.el.ctrlBtns.forEach((btn) => {
      click(btn, () => {
        const key = btn.dataset.ctrl;
        if (key === 'joystick' || key === 'drag') {
          this.control = key;
          this.el.ctrlBtns.forEach((b) => {
            if (b.dataset.ctrl === 'joystick' || b.dataset.ctrl === 'drag') b.classList.toggle('active', b === btn);
          });
        } else if (key === 'fire' || key === 'manual') {
          if (TEST_AUTO_FIRE) {
            this.autoFire = true;
            this.toast('ĐANG BẬT TỰ ĐỘNG BẮN (chế độ test)');
          } else {
            this.autoFire = key === 'fire';
          }
          this.el.ctrlBtns.forEach((b) => {
            if (b.dataset.ctrl === 'fire' || b.dataset.ctrl === 'manual') b.classList.toggle('active', b === btn);
          });
        }
        try {
          localStorage.setItem('ww3d_control', this.control);
          localStorage.setItem('ww3d_autofire', this.autoFire ? '1' : '0');
        } catch { /* chế độ riêng tư */ }
        this.onControlChange?.(this.control, this.autoFire);
      });
    });

    const slider = (node, fn) => node?.addEventListener('input', () => fn(Number(node.value)));
    const sliderSound = (v) => {
      this.sfx.setVolume(v / 100);
      if (v > 0 && this.sfx.muted) {
        this.sfx.setMuted(false);
        this.profile.setMuted(false);
        this.refreshChrome();
      }
    };
    const sliderMusic = (v) => this.sfx.setMusicVolume?.(v / 100);
    const sliderSpeed = (v) => {
      this.speed = v;
      if (this.el.speedVal) this.el.speedVal.textContent = (v / 100).toFixed(1);
      if (this.el.speedVal2) this.el.speedVal2.textContent = (v / 100).toFixed(1);
      try { localStorage.setItem('ww3d_speed', String(v)); } catch { /* bỏ qua */ }
      this.onSpeed?.(v / 100);
    };
    slider(this.el.sliderSound, sliderSound);
    slider(this.el.mSound, sliderSound);
    slider(this.el.sliderMusic, sliderMusic);
    slider(this.el.mMusic, sliderMusic);
    slider(this.el.sliderSpeed, sliderSpeed);
    slider(this.el.mSpeed, sliderSpeed);

    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      this.installEvent = e;
      this.el.settInstall?.classList.add('ready');
    });
  }

  _syncSliders() {
    const pctOf = (v) => Math.round(Math.max(0, Math.min(1, v)) * 100);
    const vol = String(pctOf(this.sfx.volume ?? 0.55));
    const mus = String(pctOf(this.sfx.musicVolume ?? 0.35));
    [this.el.sliderSound, this.el.mSound].forEach((n) => { if (n) n.value = vol; });
    [this.el.sliderMusic, this.el.mMusic].forEach((n) => { if (n) n.value = mus; });
    [this.el.sliderSpeed, this.el.mSpeed].forEach((n) => { if (n) n.value = String(this.speed); });
    if (this.el.speedVal) this.el.speedVal.textContent = (this.speed / 100).toFixed(1);
    if (this.el.speedVal2) this.el.speedVal2.textContent = (this.speed / 100).toFixed(1);
    this.el.ctrlBtns.forEach((b) => {
      const key = b.dataset.ctrl;
      if (key === 'joystick' || key === 'drag') b.classList.toggle('active', key === this.control);
      if (key === 'fire' || key === 'manual') {
        const auto = TEST_AUTO_FIRE ? true : this.autoFire;
        b.classList.toggle('active', (key === 'fire') === auto);
      }
    });
  }

  // ---------------------------------------------------------------- starts
  startMode(mode) {
    if (mode === 'campaign') {
      this.show('map');
      return;
    }
    this.sfx?.click?.();
    this.onStart(mode, {});
  }

  startLevel(chapter, level) {
    this.sfx?.click?.();
    this.onStart('campaign', { chapter, level });
  }

  // ---------------------------------------------------------------- home
  renderHome() {
    const p = this.profile;
    const id = p.shipId;
    const ship = SHIP_BY_ID[id] || PLAYER_SHIPS[0];
    if (this.el.homeShipImg) this.el.homeShipImg.src = PORTHOLE[id] || PORTHOLE.striker;
    if (this.el.homeShipLvl) this.el.homeShipLvl.textContent = `L${p.shipLevel(id)}`;
    if (this.el.homeShip2Img) {
      const next = PLAYER_SHIPS.find((s) => !p.isOwned(s.id)) || ship;
      this.el.homeShip2Img.src = PORTHOLE[next.id] || PORTHOLE.striker;
    }
    if (this.el.slotS2) this.el.slotS2.classList.add('locked');

    const st = computeStats(id, p);
    const drones = st.drones;
    if (this.el.slotL) {
      this.el.slotL.classList.toggle('locked', drones <= 0);
      const icon = this.el.slotL.querySelector('.module-ico');
      const lbl = this.el.slotL.querySelector('.module-lbl');
      if (icon) {
        icon.src = drones > 0 ? ICON.drone : ICON.lock;
        icon.classList.toggle('is-lock', drones <= 0);
      }
      if (lbl) lbl.textContent = drones > 0 ? `DRONE ${drones}` : 'DRONE';
    }
    document.querySelectorAll('.mode-chips .chip').forEach((c) => c.classList.toggle('active', c.dataset.mode === this.quickMode));
    this.refreshChrome();
  }

  // ---------------------------------------------------------------- map
  renderMap() {
    const p = this.profile;
    const maxCh = Math.min(CHAPTERS.length, p.chapter);
    if (this.chapter > maxCh) this.chapter = maxCh;
    if (this.chapter < 1) this.chapter = 1;

    if (this.el.chapterRow) {
      this.el.chapterRow.innerHTML = '';
      CHAPTERS.forEach((ch) => {
        const unlocked = ch.id <= p.chapter;
        const b = document.createElement('button');
        b.type = 'button';
        b.className = `chapter-chip${ch.id === this.chapter ? ' active' : ''}`;
        b.disabled = !unlocked;
        b.classList.toggle('locked', !unlocked);
        b.innerHTML = `<b>CH ${ch.id}</b><small>${esc(ch.name)}</small>`;
        b.addEventListener('click', () => {
          this.chapter = ch.id;
          this.sfx?.click?.();
          this.renderMap();
        });
        this.el.chapterRow.appendChild(b);
      });
    }

    const ch = CHAPTERS[this.chapter - 1];
    const path = MAP_PATHS[ch.id] || MAP_PATHS[1];
    if (this.el.mapLine) {
      this.el.mapLine.setAttribute('points', path.map(([x, y]) => `${x},${y}`).join(' '));
    }

    if (this.el.mapNodes) {
      this.el.mapNodes.innerHTML = '';
      const currentLevel = (() => {
        for (let i = 1; i <= ch.levels; i++) {
          if (p.isLevelUnlocked(ch.id, i) && p.starsFor(ch.id, i) === 0) return i;
        }
        return ch.levels;
      })();

      for (let i = 1; i <= ch.levels; i++) {
        const info = levelInfo(ch.id, i);
        const stars = p.starsFor(ch.id, i);
        const unlocked = p.isLevelUnlocked(ch.id, i);
        const [x, y] = path[i - 1] || [50, 50];
        const node = document.createElement('button');
        node.type = 'button';
        node.className = [
          'map-node',
          info.isBoss ? 'boss' : '',
          !unlocked ? 'locked' : '',
          stars > 0 ? 'done' : '',
          unlocked && i === currentLevel && stars === 0 ? 'current' : '',
        ].filter(Boolean).join(' ');
        node.style.left = `${x}%`;
        node.style.top = `${y}%`;
        node.dataset.level = String(i);
        node.innerHTML = `
          ${info.isBoss
            ? `<img class="node-skull" src="${ICON.skull}" alt="boss" />`
            : `<span class="node-num">${i}</span>`}
          <span class="node-stars">${[1, 2, 3]
            .map((n) => `<img class="${n <= stars ? 'on' : ''}" src="${ICON.star}" alt="" />`)
            .join('')}</span>`;
        node.addEventListener('click', () => {
          if (!unlocked) {
            this.sfx?.error?.();
            this.toast('HẠ MÀN TRƯỚC ĐỂ MỞ KHOÁ');
            return;
          }
          this.startLevel(ch.id, i);
        });
        this.el.mapNodes.appendChild(node);
      }
    }
    this.refreshChrome();
  }

  // ---------------------------------------------------------------- hangar
  renderHangar() {
    const p = this.profile;
    if (!SHIP_BY_ID[this.selectedShip]) this.selectedShip = p.shipId;
    const id = this.selectedShip;
    const ship = SHIP_BY_ID[id];
    const owned = p.isOwned(id);
    const lvl = p.shipLevel(id);
    const st = computeStats(id, p);

    if (this.el.shipTabName) this.el.shipTabName.textContent = ship.name;
    if (this.el.shipTabPips) {
      const on = Math.ceil(lvl / 3);
      this.el.shipTabPips.innerHTML = [0, 1, 2, 3, 4].map((i) => `<i class="${i < on ? 'on' : ''}"></i>`).join('');
    }
    if (this.el.hangarShipImg) this.el.hangarShipImg.src = PORTHOLE[id] || PORTHOLE.striker;
    if (this.el.specLvl) this.el.specLvl.textContent = `${lvl}/${SHIP_MAX_LEVEL}`;
    if (this.el.specAtk) this.el.specAtk.textContent = String(st.dmg);
    if (this.el.specHp) this.el.specHp.textContent = num(st.hp);
    if (this.el.specSpd) this.el.specSpd.textContent = String(st.speed);
    if (this.el.expFill) this.el.expFill.style.width = `${Math.round((lvl / SHIP_MAX_LEVEL) * 100)}%`;
    if (this.el.expText) this.el.expText.textContent = owned ? `CẤP ${lvl} / ${SHIP_MAX_LEVEL}` : 'CHƯA SỞ HỮU';
    if (this.el.specPerk) this.el.specPerk.textContent = `✦ ${ship.perk.text} · ${ship.role}`;

    const maxed = lvl >= SHIP_MAX_LEVEL;
    if (this.el.btnBuyCoin) {
      if (!owned) this.el.btnBuyCoin.innerHTML = `<span>MỞ KHOÁ</span>${coinTag(ship.price)}`;
      else if (maxed) this.el.btnBuyCoin.innerHTML = '<span>TỐI ĐA</span>';
      else this.el.btnBuyCoin.innerHTML = `<span>+1 CẤP</span>${coinTag(shipLevelCost(id, lvl))}`;
      this.el.btnBuyCoin.disabled = owned && maxed;
    }
    if (this.el.btnBuyGem) {
      if (!owned) {
        const gems = Math.max(1, Math.round(ship.price / 420));
        this.el.btnBuyGem.innerHTML = `<span>MỞ KHOÁ</span>${gemTag(gems)}`;
      } else if (maxed) this.el.btnBuyGem.innerHTML = '<span>TỐI ĐA</span>';
      else this.el.btnBuyGem.innerHTML = `<span>+1 CẤP</span>${gemTag(shipLevelGemCost(id, lvl))}`;
      this.el.btnBuyGem.disabled = owned && maxed;
    }

    if (this.el.shipGrid) {
      this.el.shipGrid.innerHTML = '';
      PLAYER_SHIPS.forEach((s) => {
        const isOwned = p.isOwned(s.id);
        const cell = document.createElement('button');
        cell.type = 'button';
        const equipped = s.id === p.shipId;
        cell.className = `ship-cell${equipped ? ' on' : ''}${isOwned ? '' : ' locked'}`;
        cell.dataset.ship = s.id;
        cell.innerHTML = `
          <img src="${THUMB[s.id]}" alt="${esc(s.name)}" />
          ${isOwned ? `<span class="cell-lvl">Lv.${p.shipLevel(s.id)}</span>`
                    : `<img class="cell-lock" src="${ICON.lock}" alt="" />`}
          <span class="cell-name">${esc(s.name)}</span>`;
        cell.addEventListener('click', () => {
          this.sfx?.click?.();
          this.selectedShip = s.id;
          if (isOwned) {
            if (p.shipId !== s.id) {
              p.selectShip(s.id);
              this.onShipChange?.(s.id);
              this.toast(`ĐÃ TRANG BỊ ${s.name}`);
            }
          } else {
            this.toast(`${s.name} · MỞ KHOÁ BẰNG ◆${num(s.price)}`);
          }
          this.renderHangar();
          this.refreshChrome();
        });
        this.el.shipGrid.appendChild(cell);
      });
    }
    this.refreshChrome();
  }

  buyShip(currency) {
    const id = this.selectedShip;
    const p = this.profile;
    const ship = SHIP_BY_ID[id];
    if (!ship) return;

    // chưa sở hữu -> mở khoá
    if (!p.isOwned(id)) {
      if (currency === 'gems') {
        const gems = Math.max(1, Math.round(ship.price / 420));
        if (!p.spendGems(gems)) { this.toast(`KHÔNG ĐỦ GEM ◈${num(gems)}`); return; }
        p.data.ships[id] = { lvl: 1, owned: true };
        p.data.shipId = id;
        p.save();
        this.onShipChange?.(id);
        this.sfx?.coin?.();
        this.toast(`ĐÃ MỞ KHOÁ ${ship.name}`);
      } else {
        const res = p.buyShip(id);
        if (!res.ok) {
          this.toast(res.reason === 'coins' ? `KHÔNG ĐỦ XU ◆${num(ship.price)}` : 'KHÔNG THỂ MỞ KHOÁ');
          this.renderHangar();
          return;
        }
        this.onShipChange?.(p.shipId);
        this.sfx?.coin?.();
        this.toast(`ĐÃ MỞ KHOÁ ${ship.name}`);
      }
      this.renderHangar();
      return;
    }

    // đã sở hữu -> lên cấp
    const res = p.levelShip(id, currency);
    if (res.ok) {
      this.sfx?.coin?.();
      this.toast(`${ship.name} · CẤP ${res.level}/${SHIP_MAX_LEVEL}`);
    } else if (res.reason === 'coins') this.toast('KHÔNG ĐỦ XU ◆');
    else if (res.reason === 'gems') this.toast('KHÔNG ĐỦ GEM ◈');
    else if (res.reason === 'max') this.toast('ĐÃ ĐẠT CẤP TỐI ĐA');
    this.renderHangar();
  }

  // ---------------------------------------------------------------- tech
  renderTech() {
    const p = this.profile;
    const key = UPGRADES[this.techKey] ? this.techKey : UPGRADE_KEYS[0];
    this.techKey = key;
    const u = UPGRADES[key];
    const lvl = p.upgrades[key] || 0;
    const maxed = lvl >= u.max;

    if (this.el.techEmblem) {
      this.el.techEmblem.innerHTML = `<img src="${TECH_ICON[key] || ICON.cannon}" alt="" />`;
    }
    if (this.el.techShipImg) {
      this.el.techShipImg.src = SHIP_ART[this.profile.shipId] || SHIP_ART.striker;
    }
    this.el.tapPins.forEach((pin) => {
      const k = pin.dataset.key;
      const lv = p.upgrades[k] || 0;
      pin.classList.toggle('active', k === key);
      const lvEl = pin.querySelector('i');
      if (lvEl) lvEl.textContent = lv;
    });

    if (this.el.techName) this.el.techName.textContent = u.name;
    if (this.el.techDesc) this.el.techDesc.textContent = u.desc;
    if (this.el.techLvl) this.el.techLvl.textContent = `Lv.${lvl}`;

    if (this.el.techGrid) {
      this.el.techGrid.innerHTML = '';
      UPGRADE_KEYS.forEach((k) => {
        const orb = document.createElement('button');
        orb.type = 'button';
        const lvK = p.upgrades[k] || 0;
        orb.className = `orb${k === key ? ' active' : ''}${lvK > 0 ? ' unlocked' : ''}`;
        orb.innerHTML = `<img src="${TECH_ICON[k] || ICON.cannon}" alt="${esc(UPGRADES[k].name)}" />` +
          `<span class="orb-lvl">${lvK}</span>`;
        orb.addEventListener('click', () => {
          this.techKey = k;
          this.sfx?.click?.();
          this.renderTech();
        });
        this.el.techGrid.appendChild(orb);
      });
    }

    if (this.el.techRows) {
      this.el.techRows.innerHTML = '';
      UPGRADE_KEYS.forEach((k) => {
        const def = UPGRADES[k];
        const lv = p.upgrades[k] || 0;
        const row = document.createElement('div');
        row.className = `tech-row${k === key ? ' active' : ''}`;
        row.dataset.key = k;
        row.innerHTML = `
          <img class="tr-ico" src="${TECH_ICON[k] || ICON.cannon}" alt="" />
          <div class="tr-body">
            <div class="tr-name">${def.name} · Lv.${lv}/${def.max}</div>
            <div class="tr-bar"><i style="width:${Math.round((lv / def.max) * 100)}%"></i></div>
            <div class="tr-sub">${lv >= def.max ? 'ĐÃ TỐI ĐA' : `◆${num(upgradeCost(k, lv))} / ◈${num(upgradeGemCost(k, lv))}`}</div>
          </div>
          <button class="tech-arrow" ${lv >= def.max ? 'disabled' : ''} aria-label="Nâng ${def.name}"></button>`;
        row.addEventListener('click', (e) => {
          this.techKey = k;
          if (e.target.closest('.tech-arrow')) this.upgradeTech('coins');
          else { this.sfx?.click?.(); this.renderTech(); }
        });
        this.el.techRows.appendChild(row);
      });
    }

    if (this.el.techTotal) this.el.techTotal.textContent = `${p.techLevels}/${TOTAL_TECH_LEVELS}`;
    if (this.el.btnTechUpgrade) {
      this.el.btnTechUpgrade.innerHTML = maxed ? '<b>TỐI ĐA</b>' : coinTag(upgradeCost(key, lvl));
      this.el.btnTechUpgrade.disabled = maxed;
    }
    if (this.el.btnTechGem) {
      this.el.btnTechGem.innerHTML = maxed ? '<b>TỐI ĐA</b>' : gemTag(upgradeGemCost(key, lvl));
      this.el.btnTechGem.disabled = maxed;
    }
    this.refreshChrome();
  }

  upgradeTech(currency) {
    const key = this.techKey;
    const res = this.profile.buyUpgrade(key, currency);
    if (res.ok) {
      this.sfx?.coin?.();
      this.toast(`${UPGRADES[key].name} · Lv.${res.level}`);
      const pin = this.el.tapPins?.find((n) => n.dataset.key === key);
      if (pin) {
        pin.classList.add('upgraded');
        setTimeout(() => pin.classList.remove('upgraded'), 1100);
      }
    } else if (res.reason === 'coins') this.toast('KHÔNG ĐỦ XU ◆');
    else if (res.reason === 'gems') this.toast('KHÔNG ĐỦ GEM ◈');
    else if (res.reason === 'max') this.toast('ĐÃ ĐẠT CẤP TỐI ĐA');
    this.renderTech();
  }

  // ---------------------------------------------------------------- store
  nextDaily() {
    const claimed = this.profile.data.lastDaily === dailyKey();
    const streak = (this.profile.data.dailyStreak || 0) % 7 + 1;
    return { claimed, streak, coins: 260 + streak * 140, gems: 2 + Math.floor(streak / 2) };
  }

  renderStore() {
    const d = this.nextDaily();
    if (this.el.dealStreak) this.el.dealStreak.textContent = `Chuỗi ${this.profile.data.dailyStreak || 0} ngày`;
    if (this.el.dealCoins) this.el.dealCoins.textContent = num(d.coins);
    if (this.el.dealGems) this.el.dealGems.textContent = num(d.gems);
    if (this.el.btnClaimDaily) {
      this.el.btnClaimDaily.textContent = d.claimed ? 'ĐÃ NHẬN HÔM NAY' : 'NHẬN';
      this.el.btnClaimDaily.disabled = d.claimed;
    }
    if (this.el.ex1) this.el.ex1.disabled = this.profile.gems < 1;
    if (this.el.ex5) this.el.ex5.disabled = this.profile.gems < 5;
    this.refreshChrome();
  }

  openDaily() {
    const p = this.profile;
    const d = this.nextDaily();
    const doneUpTo = d.claimed ? (p.data.dailyStreak || 0) : (p.data.dailyStreak || 0) % 7;
    if (this.el.dailyList) {
      this.el.dailyList.innerHTML = '';
      for (let i = 1; i <= 7; i++) {
        const isDone = i <= doneUpTo;
        const isToday = !d.claimed && i === d.streak;
        const row = document.createElement('div');
        row.className = 'daily-row';
        row.innerHTML = `
          <div>
            <b>NGÀY ${i}</b>
            <div class="daily-rew"><span class="c">◆${num(260 + i * 140)}</span><span class="g">◈${num(2 + Math.floor(i / 2))}</span></div>
          </div>
          <span class="daily-state ${isDone ? 'done' : isToday ? 'today' : 'locked'}">${isDone ? 'ĐÃ NHẬN' : isToday ? 'HÔM NAY' : 'CHƯA TỚI'}</span>`;
        this.el.dailyList.appendChild(row);
      }
    }
    if (this.el.btnClaimDaily2) {
      this.el.btnClaimDaily2.textContent = d.claimed ? 'ĐÃ NHẬN HÔM NAY' : 'NHẬN HÔM NAY';
      this.el.btnClaimDaily2.disabled = d.claimed;
    }
    this._modal('daily', true);
  }

  claimDaily() {
    const res = this.profile.claimDaily(dailyKey());
    if (!res) {
      this.toast('HÔM NAY ĐÃ NHẬN RỒI');
      this.renderStore();
      return;
    }
    this.sfx?.coin?.();
    this.toast(`+◆${num(res.coins)}  +◈${res.gems} · CHUỖI ${res.streak} NGÀY`);
    this.renderStore();
    this.openDaily();
  }

  exchange(gems) {
    if (!this.profile.spendGems(gems)) {
      this.toast('KHÔNG ĐỦ GEM ◈');
      return;
    }
    this.profile.addCoins(gems * 900);
    this.sfx?.coin?.();
    this.toast(`+◆${num(gems * 900)}`);
    this.renderStore();
  }

  // ---------------------------------------------------------------- settings
  renderSettings() {
    this._syncSliders();
    this.refreshChrome();
  }

  install() {
    if (this.installEvent) {
      this.installEvent.prompt();
      this.installEvent.userChoice?.finally(() => { this.installEvent = null; });
      return;
    }
    this.openInfo('CÀI APP', 'Trên Android (Chrome):\n1. Mở menu ⋮ góc trên phải\n2. Chọn "Thêm vào Màn hình chính"\n3. Mở app từ icon vừa tạo\n\nBản APK: tải artifact windwings3d-debug-apk trong tab Actions của GitHub repo.');
  }

  // ---------------------------------------------------------------- profile
  renderProfile() {
    const p = this.profile;
    if (this.el.profStage) this.el.profStage.textContent = String(p.chapter);
    if (this.el.profStars) this.el.profStars.textContent = num(p.totalStars);
    if (this.el.profTech) this.el.profTech.textContent = `${p.techLevels}/${TOTAL_TECH_LEVELS}`;
    if (this.el.profRuns) this.el.profRuns.textContent = num(p.data.runs || 0);
    if (this.el.profCampaign) this.el.profCampaign.textContent = num(p.bestOf('campaign'));
    if (this.el.profEndless) this.el.profEndless.textContent = num(p.bestOf('endless'));
    if (this.el.profBoss) this.el.profBoss.textContent = num(p.bestOf('bossrush'));
    if (this.el.profDaily) this.el.profDaily.textContent = num(p.bestOf('daily'));
    this.refreshChrome();
  }

  // ---------------------------------------------------------------- pause
  renderPause(game) {
    this._syncSliders();
    if (!game) return;
    const p = this.profile;
    const campaign = game.mode === 'campaign' && game.level;
    if (this.el.pauseStage) {
      this.el.pauseStage.textContent = campaign
        ? `CH ${game.chapter || p.chapter} · MÀN ${game.level.index}${game.level.isBoss ? ' · BOSS' : ''}`
        : (MODES.find((m) => m.id === game.mode)?.name || String(game.mode).toUpperCase());
    }
    if (this.el.pauseDiff) {
      const mod = game.modifiers?.name;
      const diff = (game.level?.difficulty || game.daily?.difficulty || 1);
      const tag = diff >= 2.2 ? 'KHÓ' : diff >= 1.5 ? 'THƯỜNG+' : 'THƯỜNG';
      this.el.pauseDiff.textContent = `[${mod || tag}]`;
    }
    if (this.el.pauseObjectives) {
      const hpPct = game.player ? (game.player.hp / game.player.maxHp) * 100 : 0;
      const reward = game.level?.reward || 0;
      const rows = [];
      const row = (on, text, prog) => `
        <div class="objective-row${on ? ' done' : ''}">
          <img src="${ICON.star}" alt="" style="opacity:${on ? 1 : 0.4}" />
          <span>${esc(text)}</span>
          <b>${esc(prog || '')}</b>
        </div>`;
      if (campaign) {
        const done = game.level.objective === 'survive'
          ? `${Math.max(0, Math.ceil(game.surviveLeft || 0))}s`
          : `ĐỢT ${game.wave}`;
        rows.push(row(true, game.level.objective === 'survive' ? 'SINH TỒN ĐỦ THỜI GIAN' : game.level.isBoss ? 'HẠ GỤC BOSS' : 'DỌN SẠCH ĐỢT', done));
        rows.push(row(hpPct >= 80, 'KẾT THÚC VỚI MÁU ≥ 80%', `${Math.round(hpPct)}%`));
        rows.push(row(hpPct >= 50, 'KẾT THÚC VỚI MÁU ≥ 50%', reward ? `◆${num(reward)}` : ''));
      } else {
        rows.push(row(false, 'SỐNG SÓT LÂU NHẤT', `ĐỢT ${game.wave}`));
        rows.push(row(hpPct >= 80, 'GIỮ MÁU ≥ 80%', `${Math.round(hpPct)}%`));
        rows.push(row(true, 'NHẬN XU THEO ĐIỂM', `◆${num(Math.round(game.score / 55))}`));
      }
      this.el.pauseObjectives.innerHTML = rows.join('');
    }
  }
}
