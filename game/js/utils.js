// Small math / helper utilities shared across the game.

export const clamp = (v, lo, hi) => (v < lo ? lo : v > hi ? hi : v);
export const lerp = (a, b, t) => a + (b - a) * t;
export const dist = (ax, ay, bx, by) => Math.hypot(bx - ax, by - ay);

export function angleTo(ax, ay, bx, by) {
  return Math.atan2(by - ay, bx - ax);
}

export function randRange(lo, hi) {
  return lo + Math.random() * (hi - lo);
}

export function randInt(lo, hi) {
  return Math.floor(randRange(lo, hi + 1));
}

/**
 * Weighted pick that never returns the same id `maxInRow` + 1 times
 * consecutively (checked against `history`, most recent last).
 * entries: [{ id, weight }]
 */
export function weightedPick(entries, history, maxInRow) {
  let pool = entries;
  const n = history.length;
  if (n >= maxInRow) {
    const last = history[n - 1];
    let streak = 1;
    for (let i = n - 2; i >= 0 && history[i] === last; i--) streak++;
    if (streak >= maxInRow) {
      const filtered = entries.filter((e) => e.id !== last);
      if (filtered.length > 0) pool = filtered;
    }
  }
  let total = 0;
  for (const e of pool) total += e.weight;
  let r = Math.random() * total;
  for (const e of pool) {
    r -= e.weight;
    if (r <= 0) return e.id;
  }
  return pool[pool.length - 1].id;
}

/**
 * Countdown timer driven by the update loop (never setTimeout/sleep).
 * Usage: const t = new Timer(1.5); t.update(dt); if (t.done) ...
 */
export class Timer {
  constructor(duration) {
    this.duration = Math.max(0, duration);
    this.t = 0;
    this.done = false;
  }
  update(dt) {
    if (this.done) return;
    this.t += dt;
    if (this.t >= this.duration) {
      this.t = this.duration;
      this.done = true;
    }
  }
  reset(duration) {
    if (duration !== undefined) this.duration = Math.max(0, duration);
    this.t = 0;
    this.done = false;
  }
  /** 0..1 progress */
  get progress() {
    return this.duration > 0 ? this.t / this.duration : 1;
  }
  get remaining() {
    return Math.max(0, this.duration - this.t);
  }
}
