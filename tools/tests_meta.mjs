import assert from 'node:assert/strict';
import { test, makeGame, frames, clearWaves, clearWavesKeepBoss, toCanvas,
  tapAt, buttonCenter, toBossIdle, forceAttack, CONFIG, spawnEnemy,
  Powerup, Bullet, menuButtons } from './harness.mjs';

// =========================================================== STEP 7 tests
test('bomb: clears bullets, 500 dmg to enemies+boss, flash + slow-mo', () => {
  const g = toBossIdle(makeGame());
  clearWavesKeepBoss(g);
  spawnEnemy(g, 'elite', { x: 200, y: 400 }); // hp 80 -> dies to bomb
  spawnEnemy(g, 'chaser', { x: 500, y: 400 });
  g.enemyBullets.push(new Bullet({
    x: 300, y: 600, vx: 0, vy: 200, radius: 9, life: 5, color: '#ff4a6a',
  }));
  const bombs0 = g.player.bombs;
  const hp0 = g.boss.hp;
  assert.equal(g.useBomb(), true);
  assert.equal(g.player.bombs, bombs0 - 1);
  assert.equal(g.enemyBullets.length, 0, 'screen cleared');
  assert.equal(g.enemies.length, 0, 'enemies destroyed');
  assert.equal(g.boss.hp, hp0 - CONFIG.bomb.damage);
  assert.equal(g.timeScale, CONFIG.bomb.slowMo.scale, 'bomb slow-mo');
  assert.ok(g.flashes.some((f) => f.color === '#ffffff'), 'white flash');
});

test('bomb refused with 0 bombs or while paused', () => {
  const g = makeGame();
  clearWaves(g);
  g.player.bombs = 0;
  assert.equal(g.useBomb(), false);
  g.player.bombs = 2;
  g.togglePause();
  assert.equal(g.useBomb(), false);
  assert.equal(g.player.bombs, 2);
});

test('combo multiplier: +0.5x per 5 kills, caps 5x, resets on hit', () => {
  const g = makeGame();
  clearWaves(g);
  for (let i = 0; i < 5; i++) g.score.addKill(100, 100);
  assert.equal(g.score.multiplier, 1.5);
  assert.equal(g.score.score, 500);
  g.score.addKill(100, 100); // 6th kill at 1.5x
  assert.equal(g.score.score, 650);
  for (let i = 0; i < 40; i++) g.score.addKill(100, 100);
  assert.equal(g.score.multiplier, CONFIG.score.comboMax, 'caps at 5x');
  g.score.onPlayerHit();
  assert.equal(g.score.multiplier, 1);
});

test('bomb kill feeds combo and drops like a normal kill', () => {
  const g = makeGame();
  clearWaves(g);
  CONFIG.powerup.dropChance = 1;
  CONFIG.powerup.bombDropChance = 0;
  spawnEnemy(g, 'chaser', { x: 300, y: 400 });
  g.player.bombs = 1;
  g.useBomb();
  CONFIG.powerup.dropChance = 0.05;
  CONFIG.powerup.bombDropChance = 0.01;
  assert.equal(g.score.score, 100, 'bomb kill scores');
  assert.equal(g.powerups.length, 1, 'drop rolled');
});

// =========================================================== STEP 8 tests
test('pause button pauses; menu Resume/Restart/Quit all work', () => {
  const g = makeGame();
  clearWaves(g);
  g.score.score = 1234;
  tapAt(g, CONFIG.controls.pauseButton.centerX, CONFIG.controls.pauseButton.centerY);
  assert.equal(g.paused, true, 'paused via touch');
  let btns = menuButtons(g);
  assert.equal(btns.length, 3);
  tapAt(g, ...Object.values(buttonCenter(btns[0]))); // RESUME
  assert.equal(g.paused, false);
  tapAt(g, CONFIG.controls.pauseButton.centerX, CONFIG.controls.pauseButton.centerY);
  btns = menuButtons(g);
  tapAt(g, ...Object.values(buttonCenter(btns[2]))); // QUIT
  assert.equal(g.state, 'quit');
  btns = menuButtons(g);
  tapAt(g, ...Object.values(buttonCenter(btns[0]))); // PLAY AGAIN
  assert.equal(g.state, 'playing');
  assert.equal(g.score.score, 0, 'restart reset score');
});

test('restart from pause resets lives/bombs/player', () => {
  const g = makeGame();
  clearWaves(g);
  g.player.lives = 1;
  g.player.bombs = 0;
  g.togglePause();
  const btns = menuButtons(g);
  tapAt(g, ...Object.values(buttonCenter(btns[1]))); // RESTART
  assert.equal(g.paused, false);
  assert.equal(g.player.lives, CONFIG.player.lives);
  assert.equal(g.player.bombs, CONFIG.player.bombsInitial);
});

test('defeat screen after 3 lives lost, play again recovers', () => {
  const g = makeGame();
  clearWaves(g);
  for (let i = 0; i < 3; i++) {
    g.player.invulnT = 0;
    g.player.state = 'alive'; // skip respawn wait between test hits
    g.player.hit();
    g.timeScale = 1;
    g._slowMo = null;
  }
  assert.equal(g.state, 'defeat');
  const btns = menuButtons(g);
  assert.ok(btns.length >= 1);
  tapAt(g, ...Object.values(buttonCenter(btns[0])));
  assert.equal(g.state, 'playing');
  assert.equal(g.player.lives, CONFIG.player.lives);
});

test('victory screen after boss death, play again restarts run', () => {
  const g = toBossIdle(makeGame());
  g.boss.hp = 1;
  g.boss.hurt(10);
  let n = 0;
  while (g.state !== 'victory' && n++ < 600) g.step(1 / 60);
  assert.equal(g.state, 'victory');
  const btns = menuButtons(g);
  tapAt(g, ...Object.values(buttonCenter(btns[0])));
  assert.equal(g.state, 'playing');
  assert.equal(g.boss.state, 'hidden');
  assert.equal(g.boss.hp, CONFIG.boss.maxHp);
});

test('taps during gameplay never trigger menu actions', () => {
  const g = makeGame();
  clearWaves(g);
  tapAt(g, 360, 560 + 42); // where RESUME would sit if a menu were open
  assert.equal(g.state, 'playing');
  assert.equal(g.paused, false);
});

test('5-minute soak: entity pools stay bounded (no leak), no crash', () => {
  const g = makeGame();
  g.input.firing = true;
  let maxB = 0;
  let maxEB = 0;
  let maxP = 0;
  let maxPop = 0;
  const minutes = 5;
  for (let i = 0; i < 60 * 60 * minutes; i++) {
    g.player.invulnT = 1; // god mode: soak systems, not survival
    g.input.dragTarget.x = 360 + Math.sin(i / 90) * 260;
    g.input.dragTarget.y = 1000 + Math.cos(i / 70) * 60;
    g.input.dragging = true;
    g.step(1 / 60);
    if (g.state !== 'playing') break; // victory reached: soak done
    maxB = Math.max(maxB, g.bullets.length);
    maxEB = Math.max(maxEB, g.enemyBullets.length);
    maxP = Math.max(maxP, g.particles.length);
    maxPop = Math.max(maxPop, g.popups.length);
  }
  assert.ok(maxB < 300, `player bullets bounded (${maxB})`);
  assert.ok(maxEB < 900, `enemy bullets bounded (${maxEB})`);
  assert.ok(maxP < 2500, `particles bounded (${maxP})`);
  assert.ok(maxPop < 120, `popups bounded (${maxPop})`);
  assert.ok(g.telegraphs.length < 30, 'telegraphs bounded');
  assert.ok(g.powerups.length < 40, 'powerups bounded');
});

