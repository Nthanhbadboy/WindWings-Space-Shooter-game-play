// Campaign: 60 levels (6 chapters x 10). Deterministic per-level wave
// scripts (seeded RNG), difficulty curve, chapter bosses every 10 levels.
import { CONFIG } from './config.js';

const C = CONFIG.campaign;
const S = CONFIG.screen;

/** Small deterministic PRNG (mulberry32). */
function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const px = (r, lo, hi) => lo + Math.floor(r() * (hi - lo + 1));
const clampX = (x) => Math.max(70, Math.min(S.width - 70, x));

// ------------------------------------------------------------ spawn bits
function chaserLine(r, t, count) {
  const out = [];
  const x0 = px(r, 120, 600);
  for (let i = 0; i < count; i++) {
    out.push({ t: t + i * 0.3, type: 'chaser', x: clampX(x0 + (i % 2 ? 90 : -90) * (i > 2 ? 1 : 0.5)) });
  }
  return out;
}

function formationV(r, t) {
  return [{ t, type: 'formation', x: px(r, 200, 520) }];
}

function shooterPair(r, t, n) {
  const out = [];
  for (let i = 0; i < n; i++) out.push({ t: t + i * 0.6, type: 'shooter', x: px(r, 140, 580) });
  return out;
}

function turretCross(r, t) {
  return [
    { t, type: 'turret', x: -40, dir: 1 },
    { t: t + 0.8, type: 'turret', x: S.width + 40, dir: -1 },
  ];
}

function eliteGuard(r, t, n) {
  const out = [];
  for (let i = 0; i < n; i++) out.push({ t: t + i * 1.4, type: 'elite', x: px(r, 180, 540) });
  return out;
}

/** One 10-16s wave; pool widens with chapter. */
function makeWave(r, chapter, waveIndex) {
  const spawns = [];
  let t = 0;
  const beats = 3 + Math.min(3, chapter);
  for (let b = 0; b < beats; b++) {
    const roll = r();
    if (roll < 0.28) spawns.push(...chaserLine(r, t, 3 + Math.min(3, chapter)));
    else if (roll < 0.5) spawns.push(...formationV(r, t));
    else if (roll < 0.7 && chapter >= 2) spawns.push(...shooterPair(r, t, 1 + (chapter > 2 ? 1 : 0)));
    else if (roll < 0.85 && chapter >= 3) spawns.push(...turretCross(r, t));
    else if (chapter >= 4) spawns.push(...eliteGuard(r, t, 1));
    else spawns.push(...chaserLine(r, t, 4));
    t += 2.4 + r() * 1.6;
  }
  // opening wave of chapter 1 stays handcrafted-friendly: formation first
  if (chapter === 1 && waveIndex === 0) {
    spawns.unshift({ t: 0, type: 'formation', x: 360 });
  }
  spawns.sort((a, b) => a.t - b.t);
  return { duration: Math.max(10, Math.min(16, t + 4)), spawns };
}

function difficultyMods(n) {
  const d = C.difficulty;
  const cap = d.cap;
  return {
    hp: Math.min(cap, 1 + (n - 1) * d.hpPerLevel),
    speed: Math.min(1.6, 1 + (n - 1) * d.speedPerLevel),
    bullet: Math.min(1.6, 1 + (n - 1) * d.bulletPerLevel),
  };
}

/** Full level definition. Level 1 keeps the handcrafted onboarding script. */
export function getLevel(n) {
  const total = C.chapters * C.levelsPerChapter;
  const num = Math.max(1, Math.min(total, n));
  const chapter = Math.ceil(num / C.levelsPerChapter);
  const idx = ((num - 1) % C.levelsPerChapter) + 1;
  const isBoss = idx === C.bossEvery;
  const r = rng(num * 7919 + 13);

  let waves;
  if (num === 1) waves = CONFIG.waves.definitions;
  else {
    const waveCount = isBoss ? 4 : 5;
    waves = [];
    for (let w = 0; w < waveCount; w++) waves.push(makeWave(r, chapter, w));
  }

  const boss = isBoss
    ? {
      type: C.bossTypesByChapter[chapter - 1],
      name: C.bossNames[chapter - 1],
      hpMul: C.bossHpByChapter[chapter - 1],
    }
    : null;

  return {
    number: num,
    chapter,
    indexInChapter: idx,
    isBoss,
    boss,
    mods: difficultyMods(num),
    waves,
    tint: C.starTintByChapter[chapter - 1],
    label: `CH${chapter}-${String(idx).padStart(2, '0')}`,
  };
}

export const TOTAL_LEVELS = C.chapters * C.levelsPerChapter;
