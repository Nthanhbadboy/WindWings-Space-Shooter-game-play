import assert from 'node:assert/strict';
import { test, makeGame, frames, clearWaves, clearWavesKeepBoss, toCanvas,
  tapAt, buttonCenter, toBossIdle, forceAttack, CONFIG, spawnEnemy,
  Powerup, Bullet, menuButtons } from './harness.mjs';

// =========================================================== STEP 1 tests
test('boots and runs 300 frames without crashing', () => {
  const g = makeGame();
  // park the ship in a safe corner so the scripted waves don't clip it
  g.input.dragging = true;
  g.input.dragTarget.x = 80;
  g.input.dragTarget.y = 1080;
  frames(g, 300);
  assert.equal(g.state, 'playing');
  assert.equal(g.player.lives, CONFIG.player.lives);
});

test('drag anywhere: ship follows finger with offset, stays in bounds', () => {
  const g = makeGame();
  const c = toCanvas(g, 500, 900);
  g.canvas.emit('pointerdown', { pointerId: 1, ...c });
  assert.equal(g.input.dragging, true);
  frames(g, 90); // 1.5s -> converged
  assert.ok(Math.abs(g.player.x - 500) < 20, `x=${g.player.x}`);
  assert.ok(Math.abs(g.player.y - (900 + CONFIG.player.touchOffsetY)) < 20, `y=${g.player.y}`);
  // drag to a corner: clamped inside screen
  const c2 = toCanvas(g, -100, -100);
  g.canvas.emit('pointermove', { pointerId: 1, ...c2 });
  frames(g, 120);
  assert.ok(g.player.x >= CONFIG.player.spriteRadius - 1);
  assert.ok(g.player.y >= CONFIG.player.spriteRadius - 1);
  g.canvas.emit('pointerup', { pointerId: 1, ...c2 });
  assert.equal(g.input.dragging, false);
});

test('auto-fire: fires while touching, stops on release, cyan bullets up', () => {
  const g = makeGame();
  const c = toCanvas(g, 360, 900);
  g.canvas.emit('pointerdown', { pointerId: 2, ...c });
  frames(g, 60); // 1s at 0.12s cadence -> ~8 volleys (level 1 = 1 bullet)
  assert.ok(g.bullets.length >= 6 && g.bullets.length <= 9, `n=${g.bullets.length}`);
  const b = g.bullets[0];
  assert.ok(b.vy < 0, 'bullets fly up');
  assert.equal(b.color, CONFIG.player.bullet.color, 'cyan player bullet');
  g.canvas.emit('pointerup', { pointerId: 2, ...c });
  const n = g.bullets.length;
  frames(g, 30);
  assert.ok(g.bullets.length <= n, 'no fire after release');
});

test('hitbox much smaller than sprite (shmup standard)', () => {
  const g = makeGame();
  assert.ok(g.player.hitboxRadius <= g.player.spriteRadius / 3,
    `hitbox ${g.player.hitboxRadius} vs sprite ${g.player.spriteRadius}`);
});

test('keyboard fallback moves ship and fires', () => {
  const g = makeGame();
  const x0 = g.player.x;
  window.emit('keydown', { code: 'ArrowLeft' });
  frames(g, 30);
  assert.ok(g.player.x < x0);
  window.emit('keyup', { code: 'ArrowLeft' });
  window.emit('keydown', { code: 'Space' });
  frames(g, 30);
  assert.ok(g.bullets.length > 0, 'keyboard fire works');
  window.emit('keyup', { code: 'Space' });
});

test('pause freezes everything, resume continues', () => {
  const g = makeGame();
  g.input.dragging = true;
  g.input.dragTarget.x = 500;
  g.input.dragTarget.y = 900;
  g.input.firing = true;
  frames(g, 20);
  const x0 = g.player.x;
  const n0 = g.bullets.length;
  g.togglePause();
  frames(g, 60);
  assert.equal(g.player.x, x0);
  assert.equal(g.bullets.length, n0);
  g.togglePause();
  frames(g, 20);
  assert.ok(g.player.x !== x0 || g.bullets.length > n0, 'resumed');
});

// =========================================================== STEP 2 tests
test('wave 1 spawns V-formation (5 ships) at t=0', () => {
  const g = makeGame();
  frames(g, 2);
  assert.equal(g.enemies.length, 5, 'formation of 5');
  assert.ok(g.enemies.every((e) => e.type === 'formation'));
  const ys = g.enemies.map((e) => e.y);
  assert.ok(Math.max(...ys) - Math.min(...ys) > 50, 'V shape vertical offsets');
});

test('chaser dives straight down at configured speed, despawns off-screen', () => {
  const g = makeGame();
  clearWaves(g);
  const e = spawnEnemy(g, 'chaser', { x: 360, y: 100 });
  const y0 = e.y;
  frames(g, 60); // 1s
  assert.ok(Math.abs(e.y - (y0 + CONFIG.enemies.chaser.speed)) < 8, `y=${e.y}`);
  e.y = CONFIG.screen.height + 50;
  frames(g, 2);
  assert.ok(!g.enemies.includes(e), 'despawned');
  assert.equal(g.score.score, 0, 'escape gives no score');
});

test('player bullets kill chaser: +100 score, popup, explosion', () => {
  const g = makeGame();
  clearWaves(g);
  g.player.invulnT = 0;
  const e = spawnEnemy(g, 'chaser', { x: 360, y: 600 });
  g.input.firing = true;
  let n = 0;
  while (!e.dead && n++ < 90) g.step(1 / 60);
  assert.ok(e.dead, 'chaser killed');
  assert.equal(g.score.score, 100, 'kill score');
  assert.ok(g.popups.length > 0, 'score popup');
  assert.ok(g.particles.length > 0, 'explosion particles');
});

test('body contact costs a life and destroys enemy without score', () => {
  const g = makeGame();
  clearWaves(g);
  g.player.invulnT = 0;
  g.player.x = 360;
  g.player.y = 1080;
  spawnEnemy(g, 'chaser', { x: 360, y: 1080 - 20 });
  frames(g, 2);
  assert.equal(g.player.lives, CONFIG.player.lives - 1, 'lost a life');
  assert.equal(g.score.score, 0, 'contact kill gives no score');
  assert.equal(g.enemies.length, 0, 'enemy destroyed');
  assert.equal(g.timeScale, CONFIG.fx.playerHit.slowMo.scale, 'slow-mo on hit');
  g.timeScale = 1;
  g._slowMo = null;
});

test('respawn after 1s with 3s invulnerability', () => {
  const g = makeGame();
  clearWaves(g);
  g.player.invulnT = 0;
  g.player.x = 360;
  g.player.y = 1080;
  spawnEnemy(g, 'chaser', { x: 360, y: 1060 });
  frames(g, 2);
  assert.equal(g.player.state, 'dead');
  g.timeScale = 1;
  g._slowMo = null;
  frames(g, 60); // 1s respawn delay
  assert.equal(g.player.state, 'alive', 'respawned');
  assert.ok(g.player.invulnT > 2.5, '3s i-frames');
  // invulnerable: contact does nothing now
  spawnEnemy(g, 'chaser', { x: g.player.x, y: g.player.y });
  frames(g, 2);
  assert.equal(g.player.lives, CONFIG.player.lives - 1, 'no second life lost');
});

test('stage clear triggers when timeline ends and screen empty', () => {
  const g = makeGame();
  clearWaves(g);
  g.waves.time = g.waves.endTime;
  frames(g, 2);
  assert.equal(g.stageCleared, true);
});

// =========================================================== STEP 3 tests
test('kill rolls power-up drop (forced 100% weapon)', () => {
  const g = makeGame();
  clearWaves(g);
  CONFIG.powerup.dropChance = 1;
  CONFIG.powerup.bombDropChance = 0;
  const e = spawnEnemy(g, 'chaser', { x: 300, y: 500 });
  e.hurt(999, g);
  CONFIG.powerup.dropChance = 0.05;
  CONFIG.powerup.bombDropChance = 0.01;
  assert.equal(g.powerups.length, 1);
  assert.equal(g.powerups[0].kind, 'weapon');
});

test('power-up falls slowly when far, magnets within 100px, collects', () => {
  const g = makeGame();
  clearWaves(g);
  const pu = new Powerup(100, 200, 'weapon');
  g.powerups.push(pu);
  frames(g, 30); // far from player -> plain fall
  assert.ok(Math.abs(pu.y - (200 + CONFIG.powerup.fallSpeed * 0.5)) < 6);
  // teleport near player -> magnet + collect
  pu.x = g.player.x + 60;
  pu.y = g.player.y - 40;
  frames(g, 40);
  assert.equal(g.player.weaponLevel, 2, 'level up on collect');
  assert.equal(g.powerups.length, 0, 'removed after collect');
});

test('weapon level caps at 5 and bomb pickup adds bomb', () => {
  const g = makeGame();
  clearWaves(g);
  g.player.weaponLevel = 5;
  const pu = new Powerup(g.player.x, g.player.y - 30, 'weapon');
  g.powerups.push(pu);
  frames(g, 30);
  assert.equal(g.player.weaponLevel, 5);
  const b0 = g.player.bombs;
  g.powerups.push(new Powerup(g.player.x, g.player.y - 30, 'bomb'));
  frames(g, 30);
  assert.equal(g.player.bombs, b0 + 1);
});

test('volley shapes per weapon level (1/2/3/5/5+2 lasers)', () => {
  const expected = { 1: 1, 2: 2, 3: 3, 4: 5, 5: 7 };
  for (const [lvl, n] of Object.entries(expected)) {
    const g = makeGame();
    clearWaves(g);
    g.player.weaponLevel = Number(lvl);
    g.input.firing = true;
    frames(g, 1);
    assert.equal(g.bullets.length, n, `level ${lvl} fires ${n}`);
  }
});

// =========================================================== STEP 4 tests
test('shooter: descends, stops, fires aimed bullet after 2s pause', () => {
  const g = makeGame();
  clearWaves(g);
  const e = spawnEnemy(g, 'shooter', { x: 360, y: -40, stopY: 300 });
  let n = 0;
  while (e.y < 299 && n++ < 300) g.step(1 / 60);
  assert.ok(Math.abs(e.y - 300) < 4, `stopped at ${e.y}`);
  frames(g, 60); // 1s into the 2s pause: no shots yet
  assert.equal(g.enemyBullets.length, 0, 'no shot during pause');
  n = 0;
  while (g.enemyBullets.length === 0 && n++ < 90) g.step(1 / 60);
  assert.ok(g.enemyBullets.length > 0, 'aimed shot after pause');
  const b = g.enemyBullets[0];
  assert.equal(b.color, CONFIG.enemies.bullet.color, 'red/pink enemy bullet');
  assert.ok(b.vy > 0, 'aimed downward at player');
});

test('turret: enters from side, patrols, stops 1s, 3-way spread', () => {
  const g = makeGame();
  clearWaves(g);
  const e = spawnEnemy(g, 'turret', { x: -40, dir: 1 });
  let n = 0;
  while (e.state !== 'stop' && n++ < 600) g.step(1 / 60);
  assert.equal(e.state, 'stop');
  frames(g, 3);
  assert.equal(g.enemyBullets.length, 3, '3-way spread');
  const xs = g.enemyBullets.map((b) => b.vx);
  assert.ok(Math.abs(xs[1]) < 1e-6 && xs[0] !== 0 && Math.sign(xs[0]) !== Math.sign(xs[2]),
    'fan left/center/right');
  n = 0;
  while (e.state === 'stop' && n++ < 120) g.step(1 / 60);
  assert.equal(e.dir, -1, 'reverses after stop');
});

test('elite: zigzag movement and 5-way + aimed volley', () => {
  const g = makeGame();
  clearWaves(g);
  const e = spawnEnemy(g, 'elite', { x: 360, y: 100 });
  const seen = new Set();
  let n = 0;
  while (g.enemyBullets.length === 0 && n++ < 300) {
    g.step(1 / 60);
    seen.add(Math.sign(e.x - e.x0));
  }
  assert.ok(seen.has(1) && seen.has(-1), 'zigzag both directions');
  assert.equal(g.enemyBullets.length, 6, '5 spread + 1 aimed');
});

test('tiny hitbox: bullet 20px off center misses, 0px hits', () => {
  const g = makeGame();
  clearWaves(g);
  g.player.invulnT = 0;
  g.enemyBullets.push(new Bullet({
    x: g.player.x + 20, y: g.player.y - 100, vx: 0, vy: 400,
    radius: CONFIG.enemies.bullet.radius, life: 3,
    color: '#ff4a6a',
  }));
  frames(g, 30);
  assert.equal(g.player.lives, CONFIG.player.lives, 'near-miss does not hit');
  g.player.invulnT = 0;
  g.enemyBullets.push(new Bullet({
    x: g.player.x, y: g.player.y - 100, vx: 0, vy: 400,
    radius: CONFIG.enemies.bullet.radius, life: 3,
    color: '#ff4a6a',
  }));
  frames(g, 30);
  assert.equal(g.player.lives, CONFIG.player.lives - 1, 'direct hit costs a life');
});

test('wave timeline covers all 5 enemy types across waves 1-5', () => {
  const types = new Set();
  for (const def of CONFIG.waves.definitions) {
    for (const s of def.spawns) types.add(s.type);
  }
  for (const t of ['chaser', 'shooter', 'turret', 'formation', 'elite']) {
    assert.ok(types.has(t), `missing ${t}`);
  }
  assert.equal(CONFIG.waves.definitions.length, 5);
});

