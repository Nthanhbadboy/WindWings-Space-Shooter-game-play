// Campaign tests: 60 levels, boss-per-chapter with types + animation,
// progression/unlock, meta screens routing.
import assert from 'node:assert/strict';
import {
  test, makeGame, frames, clearWaves, tapAt, buttonCenter,
  toBossIdle, forceAttack, spawnEnemy, screenButtons,
  CONFIG, getLevel, TOTAL_LEVELS, Progress,
} from './harness.mjs';

// ------------------------------------------------------- level catalogue
test('campaign has exactly 60 levels, boss every 10th', () => {
  assert.equal(TOTAL_LEVELS, 60);
  for (let n = 1; n <= 60; n++) {
    const lv = getLevel(n);
    assert.equal(lv.number, n);
    assert.equal(lv.chapter, Math.ceil(n / 10));
    assert.equal(lv.isBoss, n % 10 === 0);
    assert.equal(!!lv.boss, lv.isBoss);
    assert.ok(lv.waves.length >= 4, `level ${n} has waves`);
  }
});

test('boss types cycle tyrant/dispatcher/omen, hp scales per chapter', () => {
  const types = [];
  for (let n = 10; n <= 60; n += 10) {
    const b = getLevel(n).boss;
    types.push(b.type);
    assert.ok(['tyrant', 'dispatcher', 'omen'].includes(b.type));
    assert.ok(b.name.length > 0);
  }
  assert.deepEqual(types, ['tyrant', 'dispatcher', 'omen', 'tyrant', 'dispatcher', 'omen']);
  const hps = [10, 20, 30, 40, 50, 60].map((n) => getLevel(n).boss.hpMul);
  for (let i = 1; i < hps.length; i++) assert.ok(hps[i] > hps[i - 1]);
});

test('level scripts are deterministic and distinct per level', () => {
  const a = JSON.stringify(getLevel(13).waves);
  assert.equal(a, JSON.stringify(getLevel(13).waves), 'same seed -> same script');
  assert.notEqual(a, JSON.stringify(getLevel(14).waves));
});

test('difficulty curve rises with caps', () => {
  let prevHp = 0;
  for (let n = 1; n <= 60; n++) {
    const m = getLevel(n).mods;
    assert.ok(m.hp >= prevHp);
    prevHp = m.hp;
    assert.ok(m.hp <= CONFIG.campaign.difficulty.cap + 1e-9);
    assert.ok(m.speed <= 1.6 + 1e-9 && m.bullet <= 1.6 + 1e-9);
  }
  assert.ok(getLevel(60).mods.hp > getLevel(2).mods.hp);
});

test('every spawn stays inside horizontal bounds (turrets enter offscreen)', () => {
  for (let n = 2; n <= 60; n++) {
    for (const w of getLevel(n).waves) {
      assert.ok(w.duration >= 10 && w.duration <= 16);
      assert.ok(w.spawns.length >= 3);
      for (const s of w.spawns) {
        if (s.type === 'turret') continue; // slides in from x=-40 / width+40
        assert.ok(
          s.x >= 70 && s.x <= CONFIG.screen.width - 70,
          `lvl ${n} spawn x=${s.x}`
        );
      }
    }
  }
});

test('per-level mods scale spawned enemy hp', () => {
  const g1 = makeGame(1);
  clearWaves(g1);
  const e1 = spawnEnemy(g1, 'chaser', { x: 300 });
  const g40 = makeGame(40);
  clearWaves(g40);
  const e40 = spawnEnemy(g40, 'chaser', { x: 300 });
  assert.equal(e1.hp, CONFIG.enemies.chaser.hp);
  assert.ok(e40.hp > e1.hp, 'level 40 chaser tougher');
});

// ------------------------------------------------------------ progression
test('progress: frontier unlock + best-stars memory', () => {
  const p = new Progress();
  assert.equal(p.unlocked, 1);
  assert.equal(p.isUnlocked(2), false);
  p.recordClear(1, 2);
  assert.equal(p.unlocked, 2);
  assert.equal(p.starsOf(1), 2);
  p.recordClear(1, 3);
  assert.equal(p.starsOf(1), 3, 'best stars kept');
  p.recordClear(1, 1);
  assert.equal(p.starsOf(1), 3, 'worse run does not downgrade');
  p.recordClear(2, 1);
  assert.equal(p.unlocked, 3);
});

test('non-boss level: waves cleared -> stars + clear screen', () => {
  const g = makeGame(2);
  clearWaves(g);
  g.waves.time = g.waves.endTime + 1;
  frames(g, 2);
  assert.equal(g.state, 'victory');
  assert.equal(g.lastStars, 3, 'no damage -> 3 stars');
});

test('boss level 20: dispatcher with chapter-scaled hp, boss begins after waves', () => {
  const g = makeGame(20);
  assert.equal(g.boss.type, 'dispatcher');
  assert.equal(g.boss.bossName, CONFIG.campaign.bossNames[1]);
  assert.equal(g.boss.maxHp, Math.round(CONFIG.boss.maxHp * CONFIG.campaign.bossHpByChapter[1]));
  clearWaves(g);
  g.waves.time = g.waves.endTime + 1;
  frames(g, 2);
  assert.notEqual(g.state, 'victory', 'boss level waits for boss death');
  assert.ok(['warning', 'enter', 'idle'].includes(g.boss.state));
});

test('final level clear hides NEXT button', () => {
  const g = makeGame(60);
  g.finishLevel();
  assert.equal(g.state, 'victory');
  const acts = screenButtons(g).map((b) => b.action);
  assert.ok(!acts.includes('next'));
  assert.ok(acts.includes('retry') && acts.includes('select'));
});

// ------------------------------------------------------- boss animation
test('boss anim states: idle -> charge -> fire recoil -> blink', () => {
  const g = toBossIdle(makeGame(10));
  assert.equal(g.boss.type, 'tyrant');
  assert.equal(g.boss.anim.state, 'idle');
  forceAttack(g, 'aimed');
  frames(g, 3);
  assert.equal(g.boss.anim.state, 'charge', 'telegraph drives charge anim');
  let n = 0;
  while (g.boss.attack && g.boss.attack.stage !== 'active' && n++ < 300) frames(g, 1);
  assert.equal(g.boss.anim.state, 'fire');
  assert.ok(g.boss.anim.kick > 0, 'recoil kick when firing');
  let blinked = false;
  for (let i = 0; i < 900 && !blinked; i++) {
    frames(g, 1);
    if (g.boss.anim.blink > 0) blinked = true;
  }
  assert.ok(blinked, 'idle blink animation fired');
  assert.ok(g.boss.anim.t > 3, 'anim clock advanced');
});

test('transition + enrage drive break/idle anim states', () => {
  const g = toBossIdle(makeGame(10));
  g.boss.hp = g.boss.maxHp * 0.5; // cross phase-2 threshold
  frames(g, 1);
  assert.equal(g.boss.anim.state, 'break', 'armor-break anim during transition');
  let n = 0;
  while (g.boss.state === 'transition' && n++ < 300) frames(g, 1);
  g.boss.hp = g.boss.maxHp * 0.05;
  g.boss._checkPhase();
  assert.equal(g.boss.enraged, true);
  frames(g, 2);
});

test('all 3 rigs render across phases + enrage without crashing', () => {
  const g = toBossIdle(makeGame(10));
  for (const type of ['tyrant', 'dispatcher', 'omen']) {
    g.boss.type = type;
    for (const phase of [1, 2, 3]) {
      g.boss.phase = phase;
      g.boss.enraged = phase === 3;
      g.boss.hurtFlashT = 0.05;
      frames(g, 5);
    }
    g.boss.enraged = false;
    g.boss.phase = 1;
  }
  // charge anim render too
  forceAttack(g, 'aimed');
  frames(g, 4);
});

// ---------------------------------------------------------- meta screens
test('title CHOI starts the highest unlocked level', () => {
  const g = makeGame(1);
  g.progress.unlocked = 5;
  g.state = 'menu';
  frames(g, 1); // renders title
  const mb = screenButtons(g);
  tapAt(g, ...Object.values(buttonCenter(mb[0])));
  assert.equal(g.state, 'playing');
  assert.equal(g.currentLevel, 5);
});

test('level select: paging, locked levels inert, unlocked starts level', () => {
  const g = makeGame(1);
  g.state = 'menu';
  tapAt(g, ...Object.values(buttonCenter(screenButtons(g)[1]))); // MAN CHOI
  assert.equal(g.state, 'select');
  frames(g, 1); // renders select
  const next = screenButtons(g).find((b) => b.action === 'nextChapter');
  tapAt(g, ...Object.values(buttonCenter(next)));
  assert.equal(g.selectChapter, 2);
  const lv20 = screenButtons(g).find((b) => b.action === 'level' && b.n === 20);
  tapAt(g, ...Object.values(buttonCenter(lv20)));
  assert.equal(g.state, 'select', 'locked level ignored');
  const prev = screenButtons(g).find((b) => b.action === 'prevChapter');
  tapAt(g, ...Object.values(buttonCenter(prev)));
  const lv1 = screenButtons(g).find((b) => b.action === 'level' && b.n === 1);
  tapAt(g, ...Object.values(buttonCenter(lv1)));
  assert.equal(g.state, 'playing');
  assert.equal(g.currentLevel, 1);
});

test('clear screen NEXT advances; RETRY replays same level', () => {
  const g = makeGame(3);
  g.finishLevel();
  frames(g, 1);
  const btns = screenButtons(g);
  const retry = btns.find((b) => b.action === 'retry');
  tapAt(g, ...Object.values(buttonCenter(retry)));
  assert.equal(g.currentLevel, 3);
  assert.equal(g.state, 'playing');
  g.finishLevel();
  const next = screenButtons(g).find((b) => b.action === 'next');
  tapAt(g, ...Object.values(buttonCenter(next)));
  assert.equal(g.currentLevel, 4);
  assert.equal(g.state, 'playing');
});

test('defeat screen renders and RETRY restarts the level', () => {
  const g = makeGame(7);
  for (let i = 0; i < 3; i++) {
    g.player.invulnT = 0;
    g.player.state = 'alive';
    g.player.hit();
    g.timeScale = 1;
    g._slowMo = null;
  }
  assert.equal(g.state, 'defeat');
  frames(g, 1); // renders defeat overlay
  const btns = screenButtons(g);
  tapAt(g, ...Object.values(buttonCenter(btns[0])));
  assert.equal(g.state, 'playing');
  assert.equal(g.currentLevel, 7);
  assert.equal(g.player.lives, CONFIG.player.lives);
});
