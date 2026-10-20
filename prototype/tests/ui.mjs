/* Kiểm thử UI + logic tiến trình trong jsdom (không cần trình duyệt). */
import { JSDOM } from 'jsdom';
import fs from 'node:fs';
import assert from 'node:assert';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const dom = new JSDOM(html, { url: 'http://localhost:5173/', pretendToBeVisual: true });
global.window = dom.window;
global.document = dom.window.document;
Object.defineProperty(global, 'navigator', { value: dom.window.navigator, configurable: true });
global.localStorage = dom.window.localStorage;
global.HTMLElement = dom.window.HTMLElement;
global.URL = dom.window.URL;

// Test phải chạy với logic khoá màn THẬT (devflags.js đang bật chế độ test)
globalThis.__WW_TEST_OVERRIDE__ = { unlockAll: false, autoFire: false, rich: false };

const { Profile, computeStats, coinsForRun, gemsForRun, UPGRADES, UPGRADE_KEYS, TOTAL_TECH_LEVELS, shipLevelCost, upgradeCost } = await import('../src/save.js');
const { PLAYER_SHIPS, SHIP_MAX_LEVEL } = await import('../src/ships.js');
const { levelInfo, CHAPTERS } = await import('../src/content.js');
const { UI } = await import('../src/ui.js');
const { Hud } = await import('../src/hud.js');

const profile = new Profile();
const sfx = {
  muted: false, volume: 0.55, musicVolume: 0.35,
  click() {}, coin() {}, error() {}, pickup() {},
  setMuted(v) { this.muted = v; },
  setMusic(v) { this.music = v; },
  setMusicVolume(v) { this.musicVolume = v; },
  setVolume(v) { this.volume = v; },
};
const starts = [];
const ui = new UI({ profile, sfx, onStart: (m, o) => starts.push([m, o]) });
const hud = new Hud();
hud.setUI(ui);

const text = (id) => document.getElementById(id).textContent.trim();
const qsa = (sel) => document.querySelectorAll(sel);
const click = (elOrId) => (typeof elOrId === 'string' ? document.getElementById(elOrId) : elOrId).click();

// ---------------------------------------------------------------- boot
assert.equal(profile.coins, 0);
assert.equal(profile.gems, 12, 'tặng 12 gem khởi đầu');
assert.equal(qsa('#bottomNav .nav-tab').length, 5, '5 tab điều hướng');
assert.deepEqual(UPGRADE_KEYS, ['cannon', 'armor', 'shield', 'drone', 'magnet']);
assert.equal(TOTAL_TECH_LEVELS, 60, 'tổng 60 cấp công nghệ');

// ---------------------------------------------------------------- home
ui.show('home');
assert.ok(document.getElementById('homeShipImg').src.includes('porthole_striker'), 'ảnh tàu đang dùng');
assert.equal(text('homeShipLvl'), 'L1');
assert.equal(text('curCoins'), '0');
assert.equal(text('curGems'), '12');
assert.equal(qsa('.mode-chips .chip').length, 3, '3 chế độ nhanh');
assert.equal(text('btnPlay'), 'CHƠI');

// chọn chế độ nhanh rồi bấm ĐẤU TRƯỜNG
click(qsa('.mode-chips .chip')[1]);
assert.equal(ui.quickMode, 'bossrush');
click('btnArena');
assert.deepEqual(starts[starts.length - 1], ['bossrush', {}], 'ĐẤU TRƯỜNG chạy chế độ đã chọn');

// PLAY mở bản đồ chiến dịch
click('btnPlay');
assert.ok(!document.getElementById('screen-map').classList.contains('hidden'), 'CHƠI mở bản đồ');
assert.equal(qsa('#chapterRow .chapter-chip').length, 6, '6 chương');
assert.equal(qsa('#chapterRow .chapter-chip')[1].disabled, true, 'chương 2 khoá');
assert.equal(qsa('#mapNodes .map-node').length, 10, '10 màn mỗi chương');
assert.equal(qsa('#mapNodes .map-node.locked').length, 9, 'chỉ màn 1 mở');
assert.ok(qsa('#mapNodes .map-node')[9].classList.contains('boss'), 'màn 10 là boss');
assert.equal(qsa('#mapNodes .map-node')[0].querySelectorAll('.node-stars img').length, 3, '3 sao trên node');

// node khoá không vào được
click(qsa('#mapNodes .map-node')[1]);
assert.equal(starts.length, 1, 'không vào màn khoá');
assert.ok(text('toast').includes('MỞ KHOÁ'), 'báo cần hạ màn trước');

click(qsa('#mapNodes .map-node')[0]);
assert.deepEqual(starts[starts.length - 1], ['campaign', { chapter: 1, level: 1 }], 'vào màn 1');

// thắng màn 1 -> mở màn 2
profile.setStars(1, 1, 3);
ui.renderMap();
assert.equal(qsa('#mapNodes .map-node.locked').length, 8, 'màn 2 mở sau khi thắng màn 1');
assert.ok(qsa('#mapNodes .map-node')[0].classList.contains('done'), 'màn 1 đánh dấu xong');
click(qsa('#mapNodes .map-node')[1]);
assert.deepEqual(starts[starts.length - 1], ['campaign', { chapter: 1, level: 2 }], 'vào màn 2');

// bấm CHƯƠNG chuyển chương đã mở
profile.unlockChapter(2);
ui.renderMap();
assert.equal(qsa('#chapterRow .chapter-chip')[1].disabled, false, 'mở chương 2');
click('btnMapChapters');
assert.equal(ui.chapter, 2, 'nút CHƯƠNG đổi chương');
click('btnMapChapters');
assert.equal(ui.chapter, 1, 'quay lại chương 1');
ui.chapter = 1;

// ---------------------------------------------------------------- hangar
ui.show('hangar');
assert.equal(qsa('#shipGrid .ship-cell').length, 8, '8 tàu');
assert.equal(qsa('#shipGrid .ship-cell.locked').length, 7, '7 tàu khoá ban đầu');
assert.ok(document.getElementById('hangarShipImg').src.includes('porthole_striker'));
assert.equal(text('specLvl'), `1/${SHIP_MAX_LEVEL}`);
assert.ok(text('specPerk').includes('+10% vàng'));

// chọn tàu khoá -> hiện giá mở khoá
click(qsa('#shipGrid .ship-cell')[1]);
assert.ok(text('btnBuyCoin').includes('MỞ KHOÁ'), 'nút mở khoá');
assert.ok(text('btnBuyCoin').includes('1.200'), 'giá 1.200 xu');

click('btnBuyCoin'); // thiếu xu
assert.equal(profile.isOwned('zenith'), false);
assert.ok(text('toast').includes('KHÔNG ĐỦ XU'), 'chặn mua khi thiếu xu');

profile.addCoins(5000);
ui.refreshChrome();
click('btnBuyCoin');
assert.equal(profile.isOwned('zenith'), true, 'mở khoá zenith');
assert.equal(profile.shipId, 'zenith', 'tự trang bị');
assert.equal(profile.coins, 5000 - 1200);

// lên cấp tàu bằng xu
const cost = shipLevelCost('zenith', 1);
const before = profile.coins;
click('btnBuyCoin');
assert.equal(profile.shipLevel('zenith'), 2, 'lên cấp tàu');
assert.equal(profile.coins, before - cost, 'trừ đúng giá');
assert.ok(text('toast').includes('CẤP 2'));

// lên cấp bằng gem
profile.addGems(40);
ui.renderHangar();
const gemsBefore = profile.gems;
click('btnBuyGem');
assert.equal(profile.shipLevel('zenith'), 3, 'lên cấp bằng gem');
assert.ok(profile.gems < gemsBefore);

// tàu đang dùng phản ánh lên trang chủ
ui.show('home');
assert.equal(text('homeShipLvl'), 'L3');
assert.ok(document.getElementById('homeShipImg').src.includes('porthole_zenith'));

// ---------------------------------------------------------------- tech
ui.show('tech');
assert.equal(qsa('#techGrid .orb').length, 5, '5 loại công nghệ');
assert.equal(qsa('#techRows .tech-row').length, 5);
assert.equal(text('techName'), 'PHÁO CHÍNH');
assert.equal(text('techTotal'), '0/60');

// sơ đồ tàu: 5 chấm nâng cấp trỏ đúng bộ phận, bấm là chọn
const pins = Array.from(qsa('#techBay .tap-pin'));
assert.equal(pins.length, 5, '5 chấm trên sơ đồ tàu');
assert.equal(pins.filter((p) => p.classList.contains('active')).length, 1, 'đúng 1 chấm đang chọn');
assert.ok(document.getElementById('techShipImg').src.includes(`art/game/${profile.shipId}`), 'sơ đồ dùng ảnh tàu trong trận');
click(pins.find((p) => p.dataset.key === 'armor'));
assert.equal(ui.techKey, 'armor', 'chạm bộ phận → chọn đúng nhánh');
assert.equal(text('techName'), 'GIÁP THÂN');
assert.ok(pins.find((p) => p.dataset.key === 'armor').classList.contains('active'), 'chấm đang chọn sáng lên');
assert.equal(pins.find((p) => p.dataset.key === 'armor').querySelector('i').textContent, '0', 'chấm hiện cấp hiện tại');

profile.addCoins(3000);
click(qsa('#techRows .tech-row')[2]); // khiên
assert.equal(text('techName'), 'KHIÊN NĂNG LƯỢNG');
const cannonCoins = profile.coins;
click('btnTechUpgrade');
assert.equal(profile.upgrades.shield, 1, 'mua công nghệ bằng xu');
assert.equal(profile.coins, cannonCoins - upgradeCost('shield', 0));
assert.equal(text('techTotal'), '1/60');
assert.equal(qsa('#techRows .tech-row')[2].querySelectorAll('.tr-bar i').length, 1);

const gems2 = profile.gems;
click('btnTechGem');
assert.equal(profile.upgrades.shield, 2, 'mua công nghệ bằng gem');
assert.ok(profile.gems < gems2);

// mua hết 1 nhánh -> nút TỐI ĐA
profile.data.upgrades.shield = UPGRADES.shield.max;
ui.renderTech();
assert.equal(text('btnTechUpgrade'), 'TỐI ĐA');
assert.equal(text('techLvl'), 'Lv.9');
profile.data.upgrades.shield = 2;

// ---------------------------------------------------------------- store
ui.show('store');
const d = ui.nextDaily();
assert.equal(text('dealCoins'), String(d.coins));
const coinsBefore = profile.coins;
click('btnClaimDaily');
const afterClaim = profile.coins;
assert.ok(afterClaim > coinsBefore, 'nhận quà ngày');
assert.ok(text('toast').includes('CHUỖI'), 'thông báo chuỗi ngày');
assert.equal(text('btnClaimDaily'), 'ĐÃ NHẬN HÔM NAY');
assert.equal(profile.data.dailyStreak, 1);
ui.claimDaily();
assert.ok(text('toast').includes('ĐÃ NHẬN'), 'không nhận 2 lần');
assert.equal(profile.coins, afterClaim);

// đổi gem -> xu
const g = profile.gems;
const c = profile.coins;
click('ex1');
assert.equal(profile.gems, g - 1);
assert.equal(profile.coins, c + 900);

// nút nhận bị khoá sau khi đã nhận trong ngày
assert.ok(document.getElementById('btnClaimDaily').disabled, 'nút nhận khoá sau khi nhận');

// ---------------------------------------------------------------- settings
ui.show('settings');
assert.equal(qsa('.settings-grid .sett-tile').length, 8);
click('settSound');
assert.equal(profile.muted, true, 'tắt âm thanh');
assert.equal(sfx.muted, true);
assert.ok(document.getElementById('settSound').classList.contains('off'));
click('settSound');
assert.equal(profile.muted, false);
click('settMusic');
assert.equal(profile.music, false, 'tắt nhạc');
click('settMusic');
assert.equal(profile.music, true);

// ---------------------------------------------------------------- profile
ui.show('profile');
assert.equal(text('profStars'), '3');
assert.equal(text('profTech'), `${profile.techLevels}/${TOTAL_TECH_LEVELS}`);
assert.equal(text('profRuns'), '0');
assert.ok(document.getElementById('profBoss').textContent.length > 0);

// ---------------------------------------------------------------- pause
ui.show('home');
const fakeGame = {
  mode: 'campaign', chapter: 1, wave: 2, score: 1200, surviveLeft: 0,
  level: levelInfo(1, 2), modifiers: null, daily: null,
  player: { hp: 90, maxHp: 100 },
};
ui.renderPause(fakeGame);
assert.ok(text('pauseStage').includes('MÀN 2'), 'pause hiện màn');
assert.equal(qsa('#pauseObjectives .objective-row').length, 3, '3 mục tiêu');
assert.equal(qsa('#pauseObjectives .objective-row.done').length, 3, 'máu 90% đạt cả 3 mốc');
hud.showScreen('pause');
assert.ok(!document.getElementById('screen-pause').classList.contains('hidden'));

// ---------------------------------------------------------------- HUD
hud.hideScreens();
hud.update({ score: 12345, wave: 3, hpPct: 66, hpValue: 99, shields: 2, weapon: 4, bossPct: null, combo: 3, timer: 42, objective: 'SINH TỒN', coins: 7, drones: 2 });
assert.equal(text('score'), '12.345');
assert.equal(text('hpText'), '99');
assert.equal(text('hudTimer'), '42s');
assert.equal(text('objective'), 'SINH TỒN');
assert.equal(document.getElementById('hpFill').style.width, '66%');
assert.equal(qsa('#weaponDots .weapon-dot.on').length, 4);
assert.equal(qsa('#shieldDots .shield-dot:not(.on)').length, 3);
assert.equal(qsa('#droneDots .drone-dot.on').length, 2);
assert.ok(!document.getElementById('combo').classList.contains('hidden'));
assert.equal(text('hudCoins'), '7');

hud.setBossName('soái hạm đỏ');
assert.equal(text('bossName'), 'SOÁI HẠM ĐỎ');
hud.update({ score: 1, wave: 4, hpPct: 30, hpValue: 12, shields: 0, weapon: 1, bossPct: 55, combo: 1, coins: 8, drones: 0 });
assert.ok(!document.getElementById('bossBarWrap').classList.contains('hidden'), 'hiện thanh boss');
assert.equal(document.getElementById('bossFill').style.width, '55%');
assert.ok(document.getElementById('combo').classList.contains('hidden'), 'ẩn combo khi x1');
assert.ok(document.getElementById('hudTimer').classList.contains('hidden'), 'ẩn timer khi null');

hud.showResult({
  mode: 'campaign', modeLabel: 'CHIẾN DỊCH', success: true, score: 5000, best: 7000,
  newRecord: false, kills: 33, wave: 6, stars: 3, coins: 210, chapter: 1,
  level: levelInfo(1, 2), daily: null, onNext: () => {},
});
assert.ok(!document.getElementById('screen-result').classList.contains('hidden'));
assert.equal(qsa('#resStars img.on').length, 3);
assert.equal(text('resTitle'), 'MÀN 2 HOÀN THÀNH');
assert.equal(text('resCoins'), '+210');
assert.equal(text('resMode'), 'CH 1 · MÀN 2');
assert.ok(!document.getElementById('btnNextLevel').classList.contains('hidden'));
assert.ok(document.getElementById('btnNextLevel').textContent.includes('TIẾP'));

// ---------------------------------------------------------------- số liệu cân bằng
assert.ok(coinsForRun({ score: 5000, kills: 40, bosses: 1, mode: 'endless' }) > 0);
assert.ok(coinsForRun({ score: 5000, kills: 40, bosses: 1, mode: 'bossrush' }) > coinsForRun({ score: 5000, kills: 40, bosses: 1, mode: 'endless' }));
assert.equal(gemsForRun({ bosses: 2, stars: 3 }), 9);
assert.ok(gemsForRun({ bosses: 0, stars: 0, mode: 'daily' }) >= 2);

// ---------------------------------------------------------------- lưu trữ
const raw = JSON.parse(dom.window.localStorage.getItem('ww3d_profile_v3'));
assert.equal(raw.version, 3);
assert.equal(raw.shipId, 'zenith');
assert.equal(raw.progress['1-1'], 3);
assert.ok(raw.gems >= 0 && raw.coins >= 0);
assert.equal(dom.window.localStorage.getItem('ww3d_profile_v2'), null, 'không ghi vào key cũ');

// ---------------------------------------------------------------- di dời dữ liệu cũ
dom.window.localStorage.removeItem('ww3d_profile_v3');
dom.window.localStorage.setItem('ww3d_profile_v2', JSON.stringify({ coins: 4321, shipId: 'striker', ships: { striker: { lvl: 4, owned: true } } }));
const migrated = new Profile();
assert.equal(migrated.coins, 4321, 'đọc được dữ liệu v2');
assert.equal(migrated.shipLevel('striker'), 4);

// ---------------------------------------------------------------- chỉ số
const zero = { shipLevel: () => 1, upgrades: { cannon: 0, armor: 0, shield: 0, drone: 0, magnet: 0 } };
const base = computeStats('striker', zero);
const up = { shipLevel: () => 1, upgrades: { cannon: 5, armor: 5, shield: 9, drone: 6, magnet: 5 } };
const boosted = computeStats('striker', up);
assert.ok(boosted.dmg > base.dmg, 'pháo tăng sát thương');
assert.ok(boosted.hp > base.hp, 'giáp tăng máu');
assert.equal(boosted.shieldCap, 5, 'khiên tối đa 5');
assert.equal(boosted.drones, 3, 'drone tối đa 3');
assert.ok(boosted.magnetR > base.magnetR, 'từ trường tăng bán kính');
assert.equal(boosted.weaponStart, 1);

// tàu đặc biệt
assert.equal(computeStats('spitfire', zero).weaponStart, 2, 'spitfire bắt đầu vũ khí 2');
assert.equal(computeStats('omen', zero).drones, 1, 'omen +1 drone');
assert.equal(computeStats('dispatcher', zero).drones, 2, 'dispatcher +2 drone');
assert.equal(computeStats('executioner', zero).pierce, 1, 'executioner xuyên đạn');

// toàn bộ id trong index.html đều tồn tại (không có null trong UI)
const ids = ['hpText', 'hpFill', 'shieldDots', 'score', 'combo', 'hudCoins', 'wave', 'portrait', 'enemySkull',
  'hudTimer', 'objective', 'bossBarWrap', 'bossName', 'bossFill', 'weaponDots', 'droneDots', 'banner',
  'joystickHint', 'btnSound', 'btnPause', 'btnPlay', 'btnArena', 'btnPvp', 'btnDeal', 'btnVip',
  'chapterRow', 'mapCanvas', 'mapLine', 'mapNodes', 'shipGrid', 'techGrid', 'techRows', 'techTotal',
  'btnTechUpgrade', 'btnTechGem', 'dailyDeal', 'btnClaimDaily', 'ex1', 'ex5', 'sliderMusic',
  'mSound', 'mMusic', 'mSpeed', 'resStars', 'resScore', 'resBest', 'resKills', 'resCoins', 'btnNextLevel',
  'modalReset', 'infoModal', 'hud', 'metaChrome', 'toast', 'errorBox', 'curStars', 'curCoins', 'curGems',
  'premiumTime', 'storeBadge', 'slotL', 'slotR', 'slotS1', 'slotS2', 'homeShipImg', 'homeShipLvl',
  'hangarShipImg', 'specLvl', 'specAtk', 'specHp', 'specSpd', 'expFill', 'expText', 'specPerk',
  'btnBuyCoin', 'btnBuyGem', 'btnMapChapters', 'btnMapUpgrade', 'pauseStage', 'pauseDiff',
  'pauseObjectives', 'settSound', 'settMusic', 'settInstall', 'settProfile', 'settLang', 'settAbout',
  'settPrivacy', 'settReset', 'profStage', 'profStars', 'profTech', 'profRuns', 'profCampaign',
  'profEndless', 'profBoss', 'profDaily', 'btnReplay', 'btnMenuOver', 'btnResume', 'btnRestartPause',
  'btnMenuPause', 'btnCloseInfo', 'btnResetYes', 'btnResetNo', 'btnCloseReset', 'objective', 'screen-loading'];
const missing = ids.filter((id) => !document.getElementById(id));
assert.deepEqual(missing, [], `id thiếu: ${missing.join(', ')}`);

// dọn timer
clearInterval(ui._clock);

console.log('✓ UI OK — 8 tàu, 5 nhánh công nghệ (60 cấp), 60 màn/6 chương, 4 chế độ, HUD WindWings, tiến trình v3');
console.log('  coins', profile.coins, '| gems', profile.gems, '| zenith lvl', profile.shipLevel('zenith'), '| stars 1-1', profile.starsFor(1, 1));
console.log('  stats striker', JSON.stringify({ hp: base.hp, dmg: base.dmg, speed: base.speed }));
console.log('  levelInfo(1,10)', JSON.stringify({ name: levelInfo(1, 10).name, objective: levelInfo(1, 10).objective, reward: levelInfo(1, 10).reward }));
