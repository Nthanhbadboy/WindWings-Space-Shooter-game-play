import { PLAYER_SHIPS, SHIP_BY_ID, SHIP_MAX_LEVEL, shipLevelMultipliers } from './ships.js';
import { CHAPTERS } from './content.js';
import { TEST_UNLOCK_ALL, TEST_RICH, TEST_RICH_COINS, TEST_RICH_GEMS } from './devflags.js';

const KEY = 'ww3d_profile_v3';
const LEGACY = 'ww3d_profile_v2';

/** Nâng cấp dùng vàng, áp dụng cho MỌI tàu. */
export const UPGRADES = {
  cannon: { name: 'PHÁO CHÍNH', desc: '+8% sát thương mỗi cấp', max: 20, base: 140, icon: '⚡' },
  armor: { name: 'GIÁP THÂN', desc: '+10% máu tối đa mỗi cấp', max: 20, base: 120, icon: '🛡' },
  shield: { name: 'KHIÊN NĂNG LƯỢNG', desc: '+1 khiên mỗi 3 cấp (tối đa 5)', max: 9, base: 180, icon: '💠' },
  drone: { name: 'DRONE HỘ VỆ', desc: 'Thêm 1 drone mỗi 2 cấp (tối đa 3)', max: 6, base: 240, icon: '🤖' },
  magnet: { name: 'TỪ TRƯỜNG', desc: '+12% bán kính hút vật phẩm', max: 5, base: 90, icon: '🧲' },
};

export const UPGRADE_KEYS = Object.keys(UPGRADES);
export const TOTAL_TECH_LEVELS = UPGRADE_KEYS.reduce((n, k) => n + UPGRADES[k].max, 0);

/** Giá nâng cấp bằng xu. */
export function upgradeCost(key, level) {
  const u = UPGRADES[key];
  if (!u) return Infinity;
  return Math.round((u.base * Math.pow(level + 1, 1.62)) / 10) * 10;
}

/** Giá nâng cấp bằng gem (rẻ hơn ~35% quy đổi, nhưng gem khan hiếm). */
export function upgradeGemCost(key, level) {
  return Math.max(1, Math.round(upgradeCost(key, level) / 420));
}

export function shipLevelCost(shipId, level) {
  const ship = SHIP_BY_ID[shipId];
  if (!ship) return Infinity;
  return Math.round((ship.price * 0.22 + 120 * Math.pow(level, 1.55)) / 10) * 10;
}

export function shipLevelGemCost(shipId, level) {
  return Math.max(1, Math.round(shipLevelCost(shipId, level) / 420));
}

const DEFAULT = () => ({
  version: 3,
  coins: 0,
  gems: 12,
  shipId: 'striker',
  ships: { striker: { lvl: 1, owned: true } },
  upgrades: { cannon: 0, armor: 0, shield: 0, drone: 0, magnet: 0 },
  best: { campaign: 0, endless: 0, bossrush: 0, daily: 0 },
  chapter: 1,
  progress: {},
  muted: false,
  music: true,
  totalCoins: 0,
  runs: 0,
  lastDaily: '',
  dailyStreak: 0,
});

export class Profile {
  constructor() {
    this.data = this._load();
    if (TEST_RICH) {
      this.data.coins = Math.max(this.data.coins || 0, TEST_RICH_COINS);
      this.data.gems = Math.max(this.data.gems || 0, TEST_RICH_GEMS);
    }
  }

  _load() {
    let raw = null;
    try {
      raw = localStorage.getItem(KEY) || localStorage.getItem(LEGACY);
    } catch { raw = null; }
    if (!raw) return DEFAULT();
    try {
      const parsed = JSON.parse(raw);
      const base = DEFAULT();
      return {
        ...base,
        ...parsed,
        ships: { ...base.ships, ...(parsed.ships || {}) },
        upgrades: { ...base.upgrades, ...(parsed.upgrades || {}) },
        best: { ...base.best, ...(parsed.best || {}) },
        gems: parsed.gems ?? base.gems,
      };
    } catch {
      return DEFAULT();
    }
  }

  save() {
    try { localStorage.setItem(KEY, JSON.stringify(this.data)); } catch { /* chế độ riêng tư */ }
  }

  get coins() { return this.data.coins; }
  get gems() { return this.data.gems || 0; }
  get shipId() { return this.data.shipId; }
  get upgrades() { return this.data.upgrades; }
  get chapter() {
    // TEST: mở khoá cả 3 chương mà không ghi vào save của người chơi
    if (TEST_UNLOCK_ALL) return CHAPTERS.length;
    return Math.max(1, this.data.chapter || 1);
  }
  get muted() { return !!this.data.muted; }
  get music() { return this.data.music !== false; }

  /** Tổng sao đã đạt (dùng cho thanh tiền tệ). */
  get totalStars() {
    return Object.values(this.data.progress || {}).reduce((n, v) => n + v, 0);
  }

  get techLevels() {
    return UPGRADE_KEYS.reduce((n, k) => n + (this.data.upgrades[k] || 0), 0);
  }

  setMuted(v) {
    this.data.muted = !!v;
    this.save();
  }

  setMusic(v) {
    this.data.music = !!v;
    this.save();
  }

  selectShip(id) {
    if (!SHIP_BY_ID[id] || !this.isOwned(id)) return false;
    this.data.shipId = id;
    this.save();
    return true;
  }

  shipRecord(id) {
    return this.data.ships[id] || { lvl: 1, owned: false };
  }

  isOwned(id) {
    if (id === 'striker') return true;
    return !!this.data.ships[id]?.owned;
  }

  shipLevel(id) {
    return this.isOwned(id) ? Math.max(1, this.data.ships[id]?.lvl || 1) : 1;
  }

  addCoins(n, { total = true } = {}) {
    const amount = Math.max(0, Math.round(n));
    this.data.coins += amount;
    if (total) this.data.totalCoins = (this.data.totalCoins || 0) + amount;
    this.save();
    return amount;
  }

  addGems(n) {
    const amount = Math.max(0, Math.round(n));
    this.data.gems = (this.data.gems || 0) + amount;
    this.save();
    return amount;
  }

  spend(n) {
    if (this.data.coins < n) return false;
    this.data.coins -= n;
    this.save();
    return true;
  }

  spendGems(n) {
    if ((this.data.gems || 0) < n) return false;
    this.data.gems -= n;
    this.save();
    return true;
  }

  buyShip(id) {
    const ship = SHIP_BY_ID[id];
    if (!ship || this.isOwned(id)) return { ok: false, reason: 'owned' };
    if (!this.spend(ship.price)) return { ok: false, reason: 'coins' };
    this.data.ships[id] = { lvl: 1, owned: true };
    this.data.shipId = id;
    this.save();
    return { ok: true };
  }

  levelShip(id, currency = 'coins') {
    if (!this.isOwned(id)) return { ok: false, reason: 'locked' };
    const lvl = this.shipLevel(id);
    if (lvl >= SHIP_MAX_LEVEL) return { ok: false, reason: 'max' };
    const paid = currency === 'gems'
      ? this.spendGems(shipLevelGemCost(id, lvl))
      : this.spend(shipLevelCost(id, lvl));
    if (!paid) return { ok: false, reason: currency === 'gems' ? 'gems' : 'coins' };
    this.data.ships[id] = { lvl: lvl + 1, owned: true };
    this.save();
    return { ok: true, level: lvl + 1 };
  }

  buyUpgrade(key, currency = 'coins') {
    const u = UPGRADES[key];
    if (!u) return { ok: false, reason: 'unknown' };
    const lvl = this.data.upgrades[key] || 0;
    if (lvl >= u.max) return { ok: false, reason: 'max' };
    const paid = currency === 'gems'
      ? this.spendGems(upgradeGemCost(key, lvl))
      : this.spend(upgradeCost(key, lvl));
    if (!paid) return { ok: false, reason: currency === 'gems' ? 'gems' : 'coins' };
    this.data.upgrades[key] = lvl + 1;
    this.save();
    return { ok: true, level: lvl + 1 };
  }

  unlockChapter(n) {
    if (n > this.chapter) {
      this.data.chapter = n;
      this.save();
    }
  }

  starsFor(chapter, level) {
    return this.data.progress?.[`${chapter}-${level}`] || 0;
  }

  setStars(chapter, level, stars) {
    if (!this.data.progress) this.data.progress = {};
    const key = `${chapter}-${level}`;
    const prev = this.data.progress[key] || 0;
    if (stars > prev) {
      this.data.progress[key] = stars;
      this.data.gems = (this.data.gems || 0) + Math.max(0, stars - prev);
      this.save();
    }
  }

  isLevelUnlocked(chapter, level) {
    if (TEST_UNLOCK_ALL) return true; // TEST: chơi màn nào cũng được
    if (chapter > this.chapter) return false;
    if (level <= 1) return true;
    return this.starsFor(chapter, level - 1) > 0;
  }

  starsInChapter(chapter) {
    const levels = CHAPTERS[chapter - 1]?.levels || 10;
    let n = 0;
    for (let i = 1; i <= levels; i++) n += this.starsFor(chapter, i);
    return n;
  }

  recordBest(mode, score) {
    const best = this.data.best[mode] || 0;
    this.data.runs = (this.data.runs || 0) + 1;
    if (score > best) {
      this.data.best[mode] = score;
      this.save();
      return true;
    }
    this.save();
    return false;
  }

  bestOf(mode) {
    return this.data.best[mode] || 0;
  }

  /** Nhận quà ngày: trả về null nếu hôm nay đã nhận. */
  claimDaily(todayKey) {
    if (this.data.lastDaily === todayKey) return null;
    const streak = (this.data.dailyStreak || 0) % 7 + 1;
    const coins = 260 + streak * 140;
    const gems = 2 + Math.floor(streak / 2);
    this.data.lastDaily = todayKey;
    this.data.dailyStreak = streak;
    this.addCoins(coins);
    this.addGems(gems);
    this.save();
    return { streak, coins, gems };
  }

  reset() {
    this.data = DEFAULT();
    this.save();
  }
}

/** Chỉ số cuối cùng của tàu sau khi cộng cấp tàu + nâng cấp toàn cục + nội tại. */
export function computeStats(shipId, profile) {
  const ship = SHIP_BY_ID[shipId] || PLAYER_SHIPS[0];
  const lvl = profile.shipLevel(ship.id);
  const up = profile.upgrades;
  const m = shipLevelMultipliers(lvl);
  const perk = ship.perk || {};

  const shieldCap = 2 + (perk.shieldMax || 0) + Math.floor((up.shield || 0) / 3);
  const startShield = Math.min(shieldCap, Math.floor((up.shield || 0) / 3));

  return {
    ship,
    level: lvl,
    hp: Math.round(ship.base.hp * m.hp * (1 + 0.1 * (up.armor || 0))),
    dmg: +(ship.base.dmg * m.dmg * (1 + 0.08 * (up.cannon || 0))).toFixed(2),
    speed: +(ship.base.speed * m.speed).toFixed(2),
    fireRate: Math.max(0.07, +(ship.base.fireRate * (1 - 0.008 * (lvl - 1))).toFixed(3)),
    shieldCap: Math.min(5, shieldCap),
    startShield: Math.min(5, startShield),
    drones: Math.min(3, Math.floor((up.drone || 0) / 2) + (perk.droneBonus || 0)),
    magnetR: 4.2 * (1 + 0.12 * (up.magnet || 0) + (perk.magnet || 0)),
    pierce: perk.pierce || 0,
    weaponStart: 1 + (perk.weaponStart || 0),
    shieldRegen: perk.shieldRegen || 1,
    coinsBonus: perk.coins || 0,
  };
}

/** Vàng nhận được sau một lượt chơi. */
export function coinsForRun({ score, kills, bosses, mode }) {
  const modeMul = mode === 'bossrush' ? 1.25 : mode === 'campaign' ? 1.1 : 1;
  return Math.round((score / 55 + kills * 1.4 + bosses * 220) * modeMul);
}

/** Gem nhận sau lượt chơi (khan hiếm hơn vàng nhiều). */
export function gemsForRun({ bosses, stars = 0, mode }) {
  return Math.max(0, Math.round(bosses * 3 + stars * 1 + (mode === 'daily' ? 2 : 0)));
}
