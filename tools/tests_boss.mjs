import assert from 'node:assert/strict';
import { test, makeGame, frames, clearWaves, clearWavesKeepBoss, toCanvas,
  tapAt, buttonCenter, toBossIdle, forceAttack, CONFIG, spawnEnemy,
  Powerup, Bullet, menuButtons } from './harness.mjs';

// =========================================================== STEP 5 tests
test('boss entry: warning 1s -> enter -> idle at entryY', () => {
  const g = makeGame();
  clearWaves(g);
  g.onStageClear();
  assert.equal(g.boss.state, 'warning');
  frames(g, 30);
  assert.equal(g.boss.state, 'warning', 'warning lasts ~1s');
  frames(g, 40);
  assert.equal(g.boss.state, 'enter');
  let n = 0;
  while (g.boss.state === 'enter' && n++ < 400) g.step(1 / 60);
  assert.equal(g.boss.state, 'idle');
  assert.equal(g.boss.y, CONFIG.boss.entryY);
});

test('boss invulnerable during warning/enter', () => {
  const g = makeGame();
  clearWaves(g);
  g.onStageClear();
  assert.equal(g.boss.hurt(100), false);
  frames(g, 70); // into enter
  assert.equal(g.boss.hurt(100), false);
  assert.equal(g.boss.hp, CONFIG.boss.maxHp);
});

test('aimed barrage: 0.4s telegraph first, then 3 shots 0.2s apart', () => {
  const g = toBossIdle(makeGame());
  forceAttack(g, 'aimed');
  let n = 0;
  while (g.boss.state !== 'attack' && n++ < 10) g.step(1 / 60);
  assert.ok(g.telegraphs.some((t) => t.type === 'aimLine'), 'aim line telegraph');
  frames(g, 20); // inside telegraph
  assert.equal(g.enemyBullets.length, 0, 'NO bullets before telegraph ends');
  n = 0;
  while (g.enemyBullets.length < 3 && n++ < 60) g.step(1 / 60);
  assert.equal(g.enemyBullets.length, 3, 'barrage of 3');
  n = 0;
  while (g.boss.state !== 'idle' && n++ < 120) g.step(1 / 60);
  assert.equal(g.boss.state, 'idle', 'recover -> idle');
});

test('fan spread: 3 locked lines telegraphed, bullets follow same angles', () => {
  const g = toBossIdle(makeGame());
  forceAttack(g, 'fan');
  let n = 0;
  while (!g.telegraphs.some((t) => t.type === 'fanLines') && n++ < 10) g.step(1 / 60);
  const tg = g.telegraphs.find((t) => t.type === 'fanLines');
  assert.equal(tg.p.angles.length, 3);
  frames(g, 24);
  assert.equal(g.enemyBullets.length, 0, 'no bullets during 0.8s telegraph');
  n = 0;
  while (g.enemyBullets.length < 3 && n++ < 30) g.step(1 / 60);
  const angs = g.enemyBullets.map((b) => Math.atan2(b.vy, b.vx));
  for (let i = 0; i < 3; i++) {
    assert.ok(Math.abs(angs[i] - tg.p.angles[i]) < 0.02, `bullet ${i} on telegraphed line`);
  }
});

test('boss takes bullet damage with white flash', () => {
  const g = toBossIdle(makeGame());
  const hp0 = g.boss.hp;
  g.bullets.push(new Bullet({
    x: g.boss.x, y: g.boss.y, vx: 0, vy: -1, radius: 6, damage: 10, life: 1,
    color: '#7df9ff',
  }));
  frames(g, 2);
  assert.equal(g.boss.hp, hp0 - 10);
  assert.ok(g.boss.hurtFlashT > 0, 'white flash on hurt');
});

test('boss death: staged explosions, 30 coins, white fade, victory', () => {
  const g = toBossIdle(makeGame());
  g.boss.hp = 1;
  g.boss.hurt(50);
  assert.equal(g.boss.state, 'dead');
  assert.equal(g.timeScale, CONFIG.boss.death.slowMo.scale, 'death slow-mo');
  frames(g, 60);
  assert.ok(g.particles.length >= 50, 'explosion particles');
  assert.equal(g.coins.length, CONFIG.boss.death.coins, 'coin burst');
  assert.ok(g.score.score >= CONFIG.score.bossKill, 'boss kill score');
  let n = 0;
  while (g.state !== 'victory' && n++ < 600) g.step(1 / 60);
  assert.equal(g.state, 'victory');
  assert.equal(g.victoryAlpha, 1);
});

// =========================================================== STEP 6 tests
test('phase 2 transition at 66%: effects, recolor, cooldown 1.2, drop', () => {
  const g = toBossIdle(makeGame());
  g.boss.hurt(CONFIG.boss.maxHp * 0.35); // -> 65%
  frames(g, 1); // phase check runs on the next update tick
  assert.equal(g.boss.state, 'transition');
  assert.equal(g.boss.phase, 2, 'sprite recolor phase');
  assert.equal(g.timeScale, CONFIG.boss.transition.slowMo.scale, 'transition slow-mo');
  assert.ok(g.flashes.length > 0, 'white flash');
  assert.equal(g.shake.amp, CONFIG.boss.transition.shake.amp);
  let n = 0;
  while (g.boss.state === 'transition' && n++ < 300) g.step(1 / 60);
  assert.equal(g.boss.state, 'idle');
  assert.equal(g.boss.cooldownTime, CONFIG.boss.phases[2].cooldown);
  assert.equal(g.powerups.length, 1, 'guaranteed power-up drop');
});

test('phase 3 transition at 33%: heals 5%, dark overlay fades in/out', () => {
  const g = toBossIdle(makeGame());
  g.boss.phase = 2;
  g.boss.hp = CONFIG.boss.maxHp * 0.34;
  g.boss.hurt(CONFIG.boss.maxHp * 0.01); // -> 33%
  frames(g, 1); // transition (and heal) start on next update tick
  assert.equal(g.boss.phase, 3);
  const healed = g.boss.hp;
  assert.ok(Math.abs(healed - CONFIG.boss.maxHp * 0.38) < 1, `healed to ${healed}`);
  let sawDark = 0;
  let n = 0;
  while (g.boss.state === 'transition' && n++ < 300) {
    g.step(1 / 60);
    sawDark = Math.max(sawDark, g.darkOverlay);
  }
  assert.ok(sawDark > 0.3, `dark overlay peaked ${sawDark}`);
  assert.equal(g.darkOverlay, 0, 'overlay cleared after transition');
  assert.equal(g.boss.cooldownTime, CONFIG.boss.phases[3].cooldown);
});

test('spiral: 0.6s glow telegraph then 24 bullets over 4s', () => {
  const g = toBossIdle(makeGame());
  g.boss.phase = 2;
  forceAttack(g, 'spiral');
  let n = 0;
  while (!g.telegraphs.some((t) => t.type === 'spiralGlow') && n++ < 10) g.step(1 / 60);
  frames(g, 30);
  assert.equal(g.enemyBullets.length, 0, 'nothing during telegraph');
  const seen = new Set();
  n = 0;
  while (g.boss.state === 'attack' && n++ < 400) {
    g.step(1 / 60);
    for (const b of g.enemyBullets) seen.add(b);
  }
  assert.equal(seen.size, 24, 'full spiral');
});

test('ring burst: expanding ring telegraph then 16 bullets 360deg', () => {
  const g = toBossIdle(makeGame());
  g.boss.phase = 2;
  forceAttack(g, 'ring');
  let n = 0;
  while (!g.telegraphs.some((t) => t.type === 'ringGlow') && n++ < 10) g.step(1 / 60);
  n = 0;
  while (g.enemyBullets.length === 0 && n++ < 80) g.step(1 / 60);
  assert.equal(g.enemyBullets.length, 16);
  const angs = g.enemyBullets.map((b) => Math.atan2(b.vy, b.vx)).sort((a, b) => a - b);
  const gap = angs[1] - angs[0];
  assert.ok(Math.abs(gap - (Math.PI * 2) / 16) < 0.01, 'even 360 spread');
});

test('laser sweep: lane telegraph 1.2s, sweep fires 0.5s, lane kills', () => {
  const g = toBossIdle(makeGame());
  g.boss.phase = 2;
  g.player.invulnT = 0;
  g.player.x = CONFIG.boss.attacks.laserSweep.fromX; // stand in the lane
  g.player.y = 1000;
  forceAttack(g, 'laserSweep');
  let n = 0;
  while (!g.telegraphs.some((t) => t.type === 'sweepLine') && n++ < 10) g.step(1 / 60);
  frames(g, 60); // inside telegraph
  assert.equal(g.player.lives, CONFIG.player.lives, 'safe during telegraph');
  n = 0;
  while (g.player.lives === CONFIG.player.lives && n++ < 120) g.step(1 / 60);
  assert.ok(g.player.lives < CONFIG.player.lives, 'swept beam hit the lane');
});

test('laser sweep dodged by hiding outside the swept lane range', () => {
  const g = toBossIdle(makeGame());
  g.boss.phase = 2;
  g.player.invulnT = 0;
  g.input.dragging = true;
  g.input.dragTarget.x = 690; // outside [fromX..toX] sweep range
  g.input.dragTarget.y = 1000;
  forceAttack(g, 'laserSweep');
  let n = 0;
  while (g.boss.state === 'attack' && n++ < 200) g.step(1 / 60);
  frames(g, 30);
  g.timeScale = 1; g._slowMo = null;
  assert.ok(g.player.x > CONFIG.boss.attacks.laserSweep.toX + 20, `x=${g.player.x}`);
  assert.equal(g.player.lives, CONFIG.player.lives, 'dodged the sweep');
});

test('homing missiles: 2 trailed missiles steer toward player', () => {
  const g = toBossIdle(makeGame());
  g.boss.phase = 3;
  forceAttack(g, 'homing');
  let n = 0;
  while (g.enemyBullets.length < 2 && n++ < 120) g.step(1 / 60);
  assert.equal(g.enemyBullets.length, 2, 'two missiles');
  assert.ok(g.enemyBullets.every((b) => b.homing && b.trail), 'homing + trail');
  const m = g.enemyBullets[1]; // right pod: vx starts positive
  const vx0 = m.vx;
  assert.ok(vx0 > 0);
  g.player.x = 100; // yank player hard left
  frames(g, 45);
  assert.ok(m.vx < vx0 - 100, `missile turned left: ${vx0} -> ${m.vx}`);
});

test('bullet hell ring: purple glow then 3 waves x 24 bullets', () => {
  const g = toBossIdle(makeGame());
  g.boss.phase = 3;
  forceAttack(g, 'hellRing');
  let n = 0;
  while (!g.telegraphs.some((t) => t.type === 'hellGlow') && n++ < 10) g.step(1 / 60);
  const seen = new Set();
  n = 0;
  while (g.boss.state === 'attack' && n++ < 200) {
    g.step(1 / 60);
    for (const b of g.enemyBullets) seen.add(b);
  }
  assert.equal(seen.size, 72, '3 x 24 bullets');
});

test('laser cross: X telegraph 1.5s, beams kill on the lines only', () => {
  const g = toBossIdle(makeGame());
  g.boss.phase = 3;
  g.player.invulnT = 0;
  // stand on the 45deg line through the boss
  g.player.x = g.boss.x + 300;
  g.player.y = g.boss.y + 300;
  forceAttack(g, 'laserCross');
  let n = 0;
  while (!g.telegraphs.some((t) => t.type === 'crossLines') && n++ < 10) g.step(1 / 60);
  frames(g, 80);
  assert.equal(g.player.lives, CONFIG.player.lives, 'safe during 1.5s telegraph');
  n = 0;
  while (g.player.lives === CONFIG.player.lives && n++ < 60) g.step(1 / 60);
  assert.ok(g.player.lives < CONFIG.player.lives, 'cross beam hit on the line');
});

test('enrage below 10%: cooldown 0.5, telegraphs x0.7, continuous shake', () => {
  const g = toBossIdle(makeGame());
  g.boss.phase = 3;
  g.boss.hp = CONFIG.boss.maxHp * 0.09;
  frames(g, 2);
  assert.equal(g.boss.enraged, true);
  assert.equal(g.boss.cooldownTime, CONFIG.boss.enrage.cooldown);
  assert.equal(g.continuousShake, CONFIG.boss.enrage.continuousShake);
  forceAttack(g, 'fan');
  let n = 0;
  while (g.boss.state !== 'attack' && n++ < 10) g.step(1 / 60);
  const tg = g.telegraphs.find((t) => t.type === 'fanLines');
  assert.ok(tg, 'telegraph still shown in enrage');
  assert.ok(Math.abs(tg.timer.duration
    - CONFIG.boss.attacks.fan.telegraph * CONFIG.boss.enrage.telegraphScale) < 1e-6,
  'telegraph shortened 30%');
});

test('pattern picker never repeats 3x in a row (phase 2 weights)', () => {
  const g = toBossIdle(makeGame());
  g.boss.phase = 2;
  for (let i = 0; i < 400; i++) {
    const id = g.boss._pickPattern();
    g.boss.patternHistory.push(id);
    if (g.boss.patternHistory.length > 3) g.boss.patternHistory.shift();
    const h = g.boss.patternHistory;
    if (h.length === 3) {
      assert.ok(!(h[0] === h[1] && h[1] === h[2]), `3x repeat ${h.join(',')}`);
    }
  }
});

test('pause mid boss-attack freezes telegraph, no damage while paused', () => {
  const g = toBossIdle(makeGame());
  forceAttack(g, 'fan');
  let n = 0;
  while (!g.telegraphs.length && n++ < 10) g.step(1 / 60);
  const tg = g.telegraphs[0];
  g.togglePause();
  const t0 = tg.timer.t;
  const bullets0 = g.enemyBullets.length;
  frames(g, 60);
  assert.equal(tg.timer.t, t0, 'telegraph frozen');
  assert.equal(g.enemyBullets.length, bullets0);
  g.togglePause();
  n = 0;
  while (g.enemyBullets.length === bullets0 && n++ < 90) g.step(1 / 60);
  assert.ok(g.enemyBullets.length > bullets0, 'attack resolves after resume');
});

