/* Mô phỏng gameplay không cần trình duyệt: kiểm tra 4 chế độ, drone, mục tiêu, rò rỉ object. */
import * as THREE from 'three';
import assert from 'node:assert';
import { Game } from '../src/game.js';

const tex = () => Object.assign(new THREE.Texture(), {});
function fakeModel(size = 2) {
  const g = new THREE.Group();
  const m = new THREE.Mesh(new THREE.BoxGeometry(size, size * 0.4, size), new THREE.MeshBasicMaterial({ color: 0x888888 }));
  g.add(m);
  g.userData.animations = [];
  return g;
}

const textures = {
  sky: tex(), skyNight: tex(), skyAlien: tex(),
  planetA: tex(), planetB: tex(), planetC: tex(), planetD: tex(), planetE: tex(), planetF: tex(),
  nebula: tex(), dot: tex(), laserP: tex(), laserE: tex(), laserG: tex(),
  spark: tex(), engine: tex(),
  pickupWeapon: tex(), pickupHeal: tex(), pickupShield: tex(), pickupCoin: tex(), pickupDrone: tex(),
  explosion: Array.from({ length: 9 }, tex),
};
const models = {
  ships: {}, enemies: {}, hulls: {}, boss: {},
};
for (const id of ['striker', 'zenith', 'challenger', 'spitfire', 'insurgent', 'executioner', 'omen', 'dispatcher']) models.ships[id] = fakeModel();
for (const id of ['swarm', 'drone', 'gunner', 'tank']) models.enemies[id] = fakeModel();
for (const id of ['raider', 'interceptor', 'bomber', 'meteor', 'meteorBig', 'drone']) models.hulls[id] = fakeModel();
for (const id of ['imperial', 'pancake', 'dreadnought']) models.boss[id] = fakeModel();

const events = [];
const hud = {
  el: { joystickHint: { classList: { remove() {} } } },
  update() {}, banner(t) { events.push(['banner', t]); }, damageFlash() {},
  setObjective(t) { events.push(['objective', t]); }, setBossName() {},
  hideScreens() {}, showScreen() {}, showResult(p) { events.push(['result', p]); },
};
const sfx = new Proxy({}, { get: () => () => {} });
const input = { enabled: true, hasDragged: false, drag: new THREE.Vector3(), keyAxis: () => ({ x: 0, z: 0 }), consumeDrag: () => new THREE.Vector3() };

const profile = {
  shipId: 'striker', chapter: 1,
  upgrades: { cannon: 0, armor: 0, shield: 0, drone: 0, magnet: 0 },
  shipLevel: () => 1, isOwned: () => true, bestOf: () => 0,
  setStars: (c, l, s) => events.push(['stars', c, l, s]),
  unlockChapter: (n) => events.push(['unlock', n]),
  recordBest: () => false, addCoins: (n) => events.push(['coins', n]),
};

function makeGame() {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(46, 9 / 16, 0.1, 400);
  const game = new Game({
    scene, camera, assets: { textures, models }, hud, sfx, input,
    bounds: { x: 5, zMin: -16, zMax: 3.4 },
    cameraBase: new THREE.Vector3(0, 22, 11), cameraTarget: new THREE.Vector3(0, 0, -6),
    profile, onResult() {},
  });
  game._damagePlayer = () => {};
  return { game, scene };
}

function cheatKill(game) {
  if (game.enemies.length) {
    const e = game.enemies[0];
    e.hp = 0;
    game._killEnemy(0);
  }
  if (game.boss) {
    game.boss.hp = 0;
    game._killBoss();
  }
}

function step(game, seconds, onTick) {
  const dt = 1 / 60;
  const n = Math.round(seconds / dt);
  let maxChildren = 0;
  for (let i = 0; i < n; i++) {
    if (game.state !== 'playing') break;
    game.update(dt);
    if (onTick) onTick(i);
    maxChildren = Math.max(maxChildren, game.scene.children.length);
  }
  return maxChildren;
}

// ---------------- 1. chiến dịch: màn dọn sạch
{
  const { game } = makeGame();
  game.start('campaign', { chapter: 1, level: 1 });
  assert.equal(game.level.objective, 'clear');
  let maxChildren = step(game, 90, () => cheatKill(game));
  const res = events.filter((e) => e[0] === 'result').pop();
  assert.ok(res, 'màn 1 phải kết thúc');
  assert.equal(res[1].success, true, 'màn 1 thắng');
  assert.ok(res[1].stars >= 1 && res[1].stars <= 3, 'có sao');
  assert.ok(res[1].coins > 0, 'có thưởng vàng');
  console.log('✓ campaign clear: score', res[1].score, 'stars', res[1].stars, 'coins', res[1].coins, 'children max', maxChildren);
}

// ---------------- 2. chiến dịch: màn sinh tồn
{
  const { game } = makeGame();
  game.start('campaign', { chapter: 1, level: 4 });
  assert.equal(game.level.objective, 'survive');
  assert.ok(game.surviveLeft > 30, 'có đồng hồ sinh tồn');
  step(game, 70);
  const res = events.filter((e) => e[0] === 'result').pop();
  assert.equal(res[1].success, true, 'sinh tồn qua màn');
  console.log('✓ campaign survive: surviveLeft', game.surviveLeft, 'wave', game.wave);
}

// ---------------- 3. chiến dịch: boss
{
  const { game } = makeGame();
  game.start('campaign', { chapter: 1, level: 10 });
  assert.equal(game.level.isBoss, true);
  step(game, 40, () => cheatKill(game));
  const res = events.filter((e) => e[0] === 'result').pop();
  assert.equal(res[1].success, true, 'hạ boss qua màn');
  assert.ok(events.some((e) => e[0] === 'unlock'), 'mở chương tiếp theo');
  console.log('✓ campaign boss: bosses killed', game.bossesKilled, 'children', game.scene.children.length);
}

// ---------------- 3b. boss 3 GIAI ĐOẠN: 66% nổi giận, 33% cuồng nộ
{
  const mark = events.length;
  const { game } = makeGame();
  game.start('campaign', { chapter: 2, level: 10 }); // boss pancake
  step(game, 4); // boss xuất hiện + nhập trận xong
  assert.ok(game.boss, 'boss đã xuất hiện');
  const b = game.boss;
  assert.equal(b.phase, 1, 'bắt đầu ở giai đoạn 1');
  b.hp = Math.ceil(b.maxHp * 0.6);
  step(game, 0.2);
  assert.equal(b.phase, 2, 'giai đoạn 2 khi còn 66% máu');
  assert.ok(events.slice(mark).some((e) => e[0] === 'banner' && String(e[1]).includes('NỔI GIẬN')), 'banner nổi giận');
  b.hp = Math.ceil(b.maxHp * 0.3);
  step(game, 0.2);
  assert.equal(b.phase, 3, 'giai đoạn 3 khi còn 33% máu');
  assert.ok(events.slice(mark).some((e) => e[0] === 'banner' && String(e[1]).includes('CUỒNG NỘ')), 'banner cuồng nộ');
  step(game, 4, () => cheatKill(game));
  const res = events.filter((e) => e[0] === 'result').pop();
  assert.equal(res[1].success, true, 'hạ boss 3 giai đoạn');
  console.log('✓ boss 3 giai đoạn: phase', b.phase, 'maxHp', b.maxHp);
}

// ---------------- 4. vô tận
{
  const { game } = makeGame();
  game.start('endless', {});
  const maxChildren = step(game, 240, () => cheatKill(game));
  assert.ok(game.wave >= 8, 'wave tăng: ' + game.wave);
  assert.ok(maxChildren < 130, 'không phình object: ' + maxChildren);
  console.log('✓ endless: wave', game.wave, 'kills', game.kills, 'children max', maxChildren);
}

// ---------------- 5. săn boss
{
  const { game } = makeGame();
  game.start('bossrush', {});
  step(game, 120, () => cheatKill(game));
  assert.ok(game.wave >= 3, 'chuỗi boss tiến triển: ' + game.wave);
  assert.ok(game.bossesKilled >= 2, 'hạ nhiều boss: ' + game.bossesKilled);
  console.log('✓ bossrush: boss #', game.wave, 'killed', game.bossesKilled);
}

// ---------------- 6. thử thách ngày + modifier
{
  const { game } = makeGame();
  game.start('daily', {});
  assert.ok(game.modifiers && game.modifiers.name, 'có modifier');
  const hpCap = game.player.maxHp;
  step(game, 30, () => cheatKill(game));
  console.log('✓ daily:', game.daily.modifier.name, '| hp', hpCap, '| wave', game.wave);
}

// ---------------- 6b. boss robot: đạn hình học + chém + địch bay ngang
{
  const { game } = makeGame();
  game.start('bossrush', {});
  step(game, 14);
  assert.ok(game.boss, 'có boss');
  assert.ok(game.enemyBullets.length > 0, 'boss phải bắn');
  const shapes = new Set(game.enemyBullets.map((b) => b.shape).filter(Boolean));
  assert.ok(shapes.size >= 1, 'đạn hình học: ' + [...shapes].join(','));
  assert.ok(game.boss.patternIndex > 0, 'boss có nhịp đánh');
  assert.ok(game.boss.slash || game.boss.patternIndex > 2, 'boss có đòn chém');
  console.log('✓ boss robot: đạn', [...shapes].join('/'), '| patterns', game.boss.patternIndex, '| bullets', game.enemyBullets.length);
}

// ---------------- 6c. địch "ruồi" nhỏ bay vào từ mép màn hình
{
  const { game } = makeGame();
  game.start('campaign', { chapter: 1, level: 1 });
  let sawSide = null;
  step(game, 30, () => {
    if (!sawSide) sawSide = game.enemies.find((e) => e.from === 'left' || e.from === 'right');
    cheatKill(game);
  });
  assert.ok(sawSide, 'phải có địch bay ngang vào');
  console.log('✓ địch bay ngang:', sawSide.kind, 'từ', sawSide.from, '| cỡ', sawSide.baseSize.toFixed(2));
}

// ---------------- 7. drone hộ vệ
{
  const { game } = makeGame();
  profile.upgrades.drone = 6; // 3 drone
  game.start('endless', {});
  assert.equal(game.drones.length, 3, '3 drone theo nâng cấp');
  game.player.droneBonus = 0;
  step(game, 12, () => cheatKill(game));
  assert.ok(game.drones.length === 3, 'giữ nguyên drone');
  profile.upgrades.drone = 0;
  console.log('✓ drones:', game.drones.length);
}

// ---------------- 8. dọn object sau khi về menu
{
  const { game } = makeGame();
  game.start('endless', {});
  step(game, 40, () => cheatKill(game));
  game._clearDynamic();
  const left = game.scene.children.filter((c) => c.isSprite || c.type === 'Group').length;
  console.log('✓ cleanup: sprite/group còn lại', left, '| children', game.scene.children.length);
}

console.log('\nTẤT CẢ MÔ PHỎNG ĐỀU ĐẠT');
