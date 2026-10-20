// Campaign progress: unlocked level + stars per level, persisted in
// localStorage when available (headless tests run without it).
import { TOTAL_LEVELS } from './levels.js';

const KEY = 'windwings_shmup_save_v1';

export class Progress {
  constructor() {
    this.unlocked = 1;
    this.stars = {}; // levelNumber -> 1..3
    this.load();
  }

  load() {
    try {
      if (typeof localStorage === 'undefined') return;
      const raw = localStorage.getItem(KEY);
      if (!raw) return;
      const data = JSON.parse(raw);
      if (data && data.unlocked >= 1) this.unlocked = Math.min(TOTAL_LEVELS, data.unlocked);
      if (data && data.stars) this.stars = data.stars;
    } catch (e) {
      // corrupted save -> start fresh
    }
  }

  save() {
    try {
      if (typeof localStorage === 'undefined') return;
      localStorage.setItem(KEY, JSON.stringify({ unlocked: this.unlocked, stars: this.stars }));
    } catch (e) {
      // storage unavailable (private mode) -> play without persistence
    }
  }

  isUnlocked(n) {
    return n <= this.unlocked;
  }

  starsOf(n) {
    return this.stars[n] || 0;
  }

  /** Record a cleared level; returns true if it was a new best. */
  recordClear(n, stars) {
    const best = Math.max(this.starsOf(n), stars);
    this.stars[n] = best;
    if (n === this.unlocked && this.unlocked < TOTAL_LEVELS) this.unlocked = n + 1;
    this.save();
    return best;
  }

  reset() {
    this.unlocked = 1;
    this.stars = {};
    this.save();
  }
}
