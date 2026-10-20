import * as THREE from 'three';
import { PLAYER_SHIPS } from './ships.js';
import { computeStats, coinsForRun } from './save.js';
import { levelInfo, CHAPTERS, dailySetup, FORMATIONS } from './content.js';
import { bulletTexture, slashTexture, slashArcTexture, glowTexture } from './textures.js';
import { SHIP_PORTHOLE } from './art.js';

export const ENEMY = {
  // --- bắn ruồi: nhiều kiểu, có con bắn có con không ---
  // Địch "ruồi" nhỏ, nhiều con — có con bắn, có con chỉ bay
  swarm: { art: 'wasp', size: 0.62, hp: 10, speed: 11.0, radius: 0.38, score: 70, behavior: 'dive', wobble: 2.6, amp: 1.0, coins: 1 },
  skimmer: { art: 'wasp', size: 0.52, hp: 12, speed: 15.5, radius: 0.32, score: 90, behavior: 'dive', wobble: 4.4, amp: 3.0, coins: 1, tint: 0xa8ffe0 },
  drone: { art: 'wasp', size: 0.78, hp: 20, speed: 7.6, radius: 0.48, score: 120, behavior: 'dive', wobble: 1.5, amp: 1.6, coins: 2, tint: 0xbfe8ff },
  raider: { art: 'wasp', size: 0.74, hp: 26, speed: 12.5, radius: 0.45, score: 160, behavior: 'dive', wobble: 3.1, amp: 2.0, coins: 2, tint: 0xffc2e0 },
  gunner: { art: 'hornet', size: 1.05, hp: 38, speed: 6.0, radius: 0.6, score: 220, behavior: 'hover', zHold: -6.5, wobble: 0.8, amp: 2.2, fire: 2.1, coins: 3 },
  interceptor: { art: 'hornet', size: 0.92, hp: 32, speed: 10.5, radius: 0.52, score: 200, behavior: 'dive', wobble: 2.4, amp: 2.6, fire: 2.8, coins: 3, tint: 0xffd6a8 },
  bomber: { art: 'hornet', size: 1.45, hp: 110, speed: 4.6, radius: 0.9, score: 440, behavior: 'hover', zHold: -7.5, wobble: 0.5, amp: 1.4, fire: 3.2, coins: 5, tint: 0xc9a8ff },
  tank: { art: 'hornet', size: 1.7, hp: 90, speed: 3.8, radius: 1.0, score: 400, behavior: 'tank', wobble: 0.5, amp: 1.0, fire: 2.6, coins: 5, tint: 0x9fd0ff },
  brute: { art: 'hornet', size: 1.95, hp: 170, speed: 2.8, radius: 1.2, score: 600, behavior: 'tank', wobble: 0.35, amp: 0.7, coins: 7, tint: 0xffb0b0 },
  spinner: { art: 'hornet', size: 0.9, hp: 50, speed: 0, radius: 0.55, score: 250, behavior: 'orbit', zHold: -5.5, wobble: 1, amp: 1, coins: 3, tint: 0xff9ad5 },
  meteor: { art: 'meteor', size: 1.35, hp: 42, speed: 7.0, radius: 0.82, score: 80, behavior: 'drift', wobble: 0.8, amp: 0.6, coins: 2, spin: 0.9 },
};

export const BOSSES = {
  imperial: {
    name: 'SOÁI HẠM ĐỎ', hp: 1150, radius: 3.0, size: 7.2, art: 'imperial',
    color: 0xff7a4a, shapes: ['square', 'diamond'],
    patterns: ['fan', 'ring', 'slash', 'wall'],
  },
  pancake: {
    name: 'ONG CHÚA TINH VÂN', hp: 1450, radius: 3.2, size: 7.6, art: 'pancake',
    color: 0xff5fd2, shapes: ['hex', 'ring'],
    patterns: ['spiral', 'slash', 'ring', 'summon'],
  },
  dreadnought: {
    name: 'CHIẾN HẠM BÓNG ĐÊM', hp: 1900, radius: 3.4, size: 8.0, art: 'dreadnought',
    color: 0xb07bff, shapes: ['triangle', 'cross'],
    patterns: ['wall', 'slash', 'spiral', 'fan'],
  },
};

const MAX_WEAPON = 5;
/** Màu sương mù dùng để pha loãng địch ở xa → tạo chiều sâu. */
const DEPTH_HAZE = new THREE.Color(0x27547f);

/** Kiểu đạn của từng tàu (đổi theo tàu đang chọn). */
const FIRE_STYLE = {
  striker: 'bolt', zenith: 'star', challenger: 'heavy', spitfire: 'bolt',
  insurgent: 'heavy', executioner: 'star', omen: 'bolt', dispatcher: 'heavy',
};
const BEAM_STEPS = 24;

const MODE_LABEL = {
  campaign: 'CHIẾN DỊCH',
  endless: 'VÔ TẬN',
  bossrush: 'SĂN BOSS',
  daily: 'THỬ THÁCH NGÀY',
};

export class Game {
  constructor({ scene, camera, assets, hud, sfx, input, bounds, cameraBase, cameraTarget, profile, onResult }) {
    Object.assign(this, { scene, camera, assets, hud, sfx, input, bounds, cameraBase, cameraTarget, profile, onResult });

    this.state = 'menu';
    this.mode = 'campaign';
    this.shipId = profile?.shipId || 'striker';
    this.stats = null;
    /** Tốc độ game do slider trong màn tạm dừng điều chỉnh (0.7 – 1.4). */
    this.speedMul = 1;
    /** Tự bắn liên tục; tắt = chỉ bắn khi đang chạm/kéo. */
    this.autoFire = true;

    this.playerBullets = [];
    this.enemyBullets = [];
    this.enemies = [];
    this.pickups = [];
    this.explosions = [];
    this.sparks = [];
    this.trails = [];
    this.rings = [];
    this.shards = [];
    this.spawnQueue = [];
    this.drones = [];
    this.boss = null;

    this.elapsed = 0;
    this.shake = 0;
    this.score = 0;
    this.kills = 0;
    this.coinsEarned = 0;
    this.combo = 1;
    this.comboTimer = 0;
    this.wave = 0;
    this.nextWaveTimer = 0;
    this.isBossWave = false;
    this.player = null;
    this.objective = 'clear';
    this.surviveLeft = 0;
    this.level = null;
    this.modifiers = {};

    this._buildMaterials();
  }

  // ------------------------------------------------------------ materials
  _buildMaterials() {
    const t = this.assets.textures;

    this.mats = {
      playerBeams: this._beamMaterials(t.laserP, 0x9fe9ff),
      droneBeams: this._beamMaterials(t.laserG, 0x9dffc4),
      enemyBeams: this._beamMaterials(t.laserE, 0xff8f9f),
      explosion: t.explosion.map((map) => new THREE.SpriteMaterial({
        map, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 1,
      })),
      spark: Array.from({ length: 8 }, (_, i) => new THREE.SpriteMaterial({
        map: t.spark, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
        opacity: 1 - i / 8, color: 0x9fdcff,
      })),
      pickup: {
        weapon: new THREE.SpriteMaterial({ map: t.pickupWeapon, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: 0x9fe9ff }),
        heal: new THREE.SpriteMaterial({ map: t.pickupHeal, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: 0x9dffc4 }),
        shield: new THREE.SpriteMaterial({ map: t.pickupShield, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: 0x9fd0ff }),
        coin: new THREE.SpriteMaterial({ map: t.pickupCoin, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: 0xffe08a }),
        drone: new THREE.SpriteMaterial({ map: t.pickupDrone, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: 0x9fe9ff }),
      },
      engine: new THREE.SpriteMaterial({ map: t.engine, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: 0x58d8ff, opacity: 0.95 }),
      flash: new THREE.SpriteMaterial({ map: t.spark, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: 0xfff2c0 }),
      // đạn nhiều kiểu
      playerStars: this._beamMaterials(t.laserPStar, 0xd8f4ff),
      playerHeavy: this._beamMaterials(t.laserPHeavy, 0x9fe9ff),
      // hiệu ứng nổ
      ring: new THREE.SpriteMaterial({ map: t.spark, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: 0xbfe9ff }),
      ember: new THREE.SpriteMaterial({ map: t.dot, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: 0xffd27a }),
      chunk: new THREE.SpriteMaterial({ map: t.enemyArt?.meteor || t.spark, transparent: true, depthWrite: false, color: 0x9aa4b8 }),
      blade: new THREE.SpriteMaterial({
        map: slashTexture(), transparent: true, depthWrite: false,
        blending: THREE.AdditiveBlending, color: 0xfff2c8, opacity: 0,
      }),
      arc: new THREE.SpriteMaterial({
        map: slashArcTexture(), transparent: true, depthWrite: false,
        blending: THREE.AdditiveBlending, color: 0xfff0d0, opacity: 0,
      }),
    };
    /** cache vật liệu đạn hình học theo (shape + màu) */
    this._geoMats = new Map();
  }

  _beamMaterials(texture, color) {
    const arr = [];
    for (let i = 0; i < BEAM_STEPS; i++) {
      arr.push(new THREE.SpriteMaterial({
        map: texture, transparent: true, depthWrite: false,
        blending: THREE.AdditiveBlending, color, rotation: (i / BEAM_STEPS) * Math.PI * 2,
      }));
    }
    return arr;
  }

  /** Vật liệu đạn hình học (cache theo hình + màu). */
  _geoMat(shape, color) {
    const key = `${shape}:${color}`;
    let m = this._geoMats.get(key);
    if (!m) {
      m = new THREE.SpriteMaterial({
        map: bulletTexture(shape),
        color,
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        toneMapped: false,
      });
      this._geoMats.set(key, m);
    }
    return m;
  }

  _beamMat(set, angle) {
    let rot = -angle;
    rot = ((rot % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
    return set[Math.round((rot / (Math.PI * 2)) * BEAM_STEPS) % BEAM_STEPS];
  }

  // ------------------------------------------------------------ lifecycle
  /**
   * start('campaign', {chapter, level}) | start('endless') | start('bossrush') | start('daily')
   */
  start(mode = 'campaign', opts = {}) {
    this.mode = mode;
    this.modifiers = {};
    this.level = null;
    this.chapter = opts.chapter || this.profile?.chapter || 1;
    this.levelIndex = opts.level || 1;

    if (mode === 'campaign') {
      this.level = levelInfo(this.chapter, this.levelIndex);
      this.theme = this.level.theme;
      this.enemyPool = this.level.enemyPool || CHAPTERS[0].enemyPool;
    } else if (mode === 'daily') {
      this.daily = dailySetup();
      this.theme = this.daily.theme;
      this.enemyPool = this.daily.enemyPool;
      this.modifiers = this.daily.modifier;
    } else {
      this.theme = CHAPTERS[0].theme;
      this.enemyPool = ['swarm', 'drone', 'gunner', 'tank', 'raider', 'interceptor'];
    }

    // bắn ruồi: thêm loại địch vào mọi chế độ — có con bắn, có con chỉ bay
    this.enemyPool = [...new Set([...(this.enemyPool || []), 'swarm', 'skimmer', 'spinner', 'gunner', 'brute'])];

    this.reset();
    this.state = 'playing';
    this.hud.hideScreens();
    this.hud.setPortrait?.(SHIP_PORTHOLE[this.profile?.shipId || 'striker']);
    this.sfx.resume();

    if (mode === 'campaign' && this.level) {
      this.hud.setObjective(this._objectiveText());
      this.startWave(1);
    } else if (mode === 'bossrush') {
      this.hud.setObjective('HẠ GỤC CÁC BOSS');
      this.startWave(1);
    } else if (mode === 'daily') {
      this.hud.setObjective(this.daily.modifier.name.toUpperCase() + ' · ' + this.daily.modifier.desc);
      this.startWave(1);
    } else {
      this.hud.setObjective('SINH TỒN CÀNG LÂU CÀNG TỐT');
      this.startWave(1);
    }
  }

  reset() {
    this._clearDynamic();
    this.score = 0;
    this.kills = 0;
    this.coinsEarned = 0;
    this.combo = 1;
    this.comboTimer = 0;
    this.wave = 0;
    this.elapsed = 0;
    this.shake = 0;
    this.nextWaveTimer = 0;
    this.isBossWave = false;
    this.bossesKilled = 0;
    this.surviveLeft = 0;
    this.bossDeath = null;
    this._createPlayer();
    this._syncDrones();
    this.hud.update({
      score: 0, wave: 1, hpPct: 100, shields: this.player.shield,
      weapon: this.player.weapon, bossPct: null, combo: 1,
      objective: this.level ? this._objectiveText() : '',
      timer: null,
    });
  }

  _clearDynamic() {
    const remove = (obj) => { if (obj) this.scene.remove(obj); };
    this.playerBullets.forEach((b) => remove(b.s));
    this.enemyBullets.forEach((b) => { remove(b.s); b.s.material?.dispose?.(); });
    this.enemies.forEach((e) => remove(e.g));
    this.pickups.forEach((p) => remove(p.s));
    this.explosions.forEach((e) => remove(e.s));
    this.sparks.forEach((s) => remove(s.s));
    this.rings.forEach((r) => remove(r.s));
    this.shards.forEach((r) => remove(r.s));
    this.drones.forEach((d) => remove(d.g));
    if (this.boss) {
      this._disposeSlash(this.boss);
      remove(this.boss.g);
    }
    if (this.player) remove(this.player.group);
    (this.playerGhosts || []).forEach((g) => remove(g.s));
    this.playerBullets = [];
    this.enemyBullets = [];
    this.enemies = [];
    this.pickups = [];
    this.explosions = [];
    this.sparks = [];
    this.trails.forEach((tr) => remove(tr.s));
    this.trails = [];
    this.rings = [];
    this.shards = [];
    this.spawnQueue = [];
    this.drones = [];
    if (this.bossDeath) { remove(this.bossDeath.g); this.bossDeath = null; }
    this.boss = null;
    this.playerGhosts = [];
    this.player = null;
  }

  _createPlayer() {
    this.stats = computeStats(this.shipId, this.profile);
    const cfg = this.stats;
    // --- tàu vẽ tay: sprite phẳng hướng về camera, đổi theo tàu đang chọn ---
    const group = new THREE.Group();
    group.position.set(0, 0, this.bounds.zMax - 1.2);

    const art = this.assets.textures.shipArt?.[cfg.ship.id] || this.assets.textures.shipArt?.striker;
    const spriteMat = new THREE.SpriteMaterial({ transparent: true, depthWrite: false, toneMapped: false });
    if (art) spriteMat.map = art;
    const sprite = new THREE.Sprite(spriteMat);
    sprite.scale.set(3.05, 3.05, 1);
    group.add(sprite);

    // ---- hai cánh tách riêng để "vỗ" — tàu là vật sống, không phải tấm ảnh dán
    let wingL = null;
    let wingR = null;
    const src = art?.image;
    if (src && typeof document !== 'undefined' && src.width) {
      const S = src.width;
      const makeWingTex = (side) => {
        const c = document.createElement('canvas');
        c.width = c.height = S;
        const ctx = c.getContext('2d');
        if (!ctx) return null;
        ctx.drawImage(src, 0, 0, S, S);
        // chỉ giữ nửa cánh ngoài, mép trong mờ dần để giấu mối nối dưới thân
        ctx.globalCompositeOperation = 'destination-in';
        const inner = S * 0.44;
        const outer = side < 0 ? 0 : S;
        const grad = ctx.createLinearGradient(inner, 0, outer, 0);
        grad.addColorStop(0, 'rgba(255,255,255,0)');
        grad.addColorStop(0.32, 'rgba(255,255,255,1)');
        grad.addColorStop(1, 'rgba(255,255,255,1)');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, S, S);
        const tex = new THREE.CanvasTexture(c);
        tex.colorSpace = THREE.SRGBColorSpace;
        tex.needsUpdate = true;
        return tex;
      };
      const mk = (side) => {
        const tex = makeWingTex(side);
        if (!tex) return null;
        const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false }));
        sp.position.set(0, 0, -0.05);
        sp.scale.set(3.05, 3.05, 1);
        group.add(sp);
        return sp;
      };
      wingL = mk(-1);
      wingR = mk(1);
    }

    // đèn định vị hai đầu cánh + quầng buồng lái
    const navL = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glowTexture(), color: 0xff5a6a, transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending, opacity: 0.8,
    }));
    navL.position.set(-1.18, 0.18, 0.25);
    navL.scale.set(0.32, 0.32, 1);
    group.add(navL);
    const navR = new THREE.Sprite(navL.material.clone());
    navR.material.color.set(0x5affb0);
    navR.position.set(1.18, 0.18, 0.25);
    navR.scale.set(0.32, 0.32, 1);
    group.add(navR);

    const cockpit = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glowTexture(), color: 0x63d8ff, transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending, opacity: 0.5,
    }));
    cockpit.position.set(0, 0.34, 0.5);
    cockpit.scale.set(0.95, 1.15, 1);
    group.add(cockpit);

    // quầng sáng mờ dưới thân để tàu tách khỏi nền
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({
      map: this.assets.textures.spark, transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending, color: 0x1d4f80, opacity: 0.55,
    }));
    halo.position.set(0, -0.18, -0.05);
    halo.scale.set(3.9, 3.9, 1);
    group.add(halo);

    // Hai luồng lửa đặt đúng hai ống xả ở đuôi (trước đây đặt giữa thân nên tàu trông "dán")
    const flameL = new THREE.Sprite(this.mats.engine.clone());
    flameL.position.set(-0.37, -1.16, 1.2);
    flameL.scale.set(0.52, 1.15, 1);
    group.add(flameL);
    const flameR = new THREE.Sprite(this.mats.engine.clone());
    flameR.position.set(0.37, -1.16, 1.2);
    flameR.scale.set(0.52, 1.15, 1);
    group.add(flameR);
    // luồng lửa lớn phía sau (nhìn xuyên qua khe thân)
    const engine = new THREE.Sprite(this.mats.engine.clone());
    engine.position.set(0, -1.5, 0.4);
    engine.scale.set(1.15, 2.2, 1);
    engine.material.opacity = 0.5;
    group.add(engine);

    // khiên năng lượng (chỉ hiện khi còn lá chắn)
    const shieldBubble = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glowTexture(), color: 0x63c8ff, transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending, opacity: 0,
    }));
    shieldBubble.position.set(0, -0.05, -0.4);
    shieldBubble.scale.set(4.4, 4.4, 1);
    group.add(shieldBubble);

    // loé súng ở hai đầu cánh
    const muzzleL = new THREE.Sprite(this.mats.flash.clone());
    muzzleL.position.set(-1.0, 0.5, 1.3);
    muzzleL.scale.set(0.7, 0.7, 1);
    muzzleL.material.opacity = 0;
    group.add(muzzleL);
    const muzzleR = new THREE.Sprite(this.mats.flash.clone());
    muzzleR.position.set(1.0, 0.5, 1.3);
    muzzleR.scale.set(0.7, 0.7, 1);
    muzzleR.material.opacity = 0;
    group.add(muzzleR);

    this.scene.add(group);

    // vệt tốc độ: bản sao mờ của tàu khi lướt nhanh
    const ghostMat = new THREE.SpriteMaterial({
      transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending, opacity: 0,
      ...(art ? { map: art } : {}),
    });
    const ghosts = [];
    for (let i = 0; i < 5; i++) {
      const gs = new THREE.Sprite(ghostMat.clone());
      gs.scale.set(3.05, 3.05, 1);
      gs.visible = false;
      this.scene.add(gs);
      ghosts.push({ s: gs, life: 0, max: 0.22 });
    }
    this.playerGhosts = ghosts;
    const hpMul = this.modifiers?.player?.hpMul || 1;
    const maxHp = Math.max(20, Math.round(cfg.hp * hpMul));
    this.player = {
      cfg,
      group,
      sprite,
      halo,
      engine,
      wingL,
      wingR,
      navL,
      navR,
      cockpit,
      flameL,
      flameR,
      shieldBubble,
      muzzleL,
      muzzleR,
      muzzleT: 0,
      kick: 0,
      ghostT: 0,
      ghosts,
      hitT: 0,
      fireStyle: FIRE_STYLE[cfg.ship.id] || 'bolt',
      hp: maxHp,
      maxHp,
      shield: cfg.startShield,
      shieldCap: cfg.shieldCap,
      weapon: Math.min(MAX_WEAPON, cfg.weaponStart),
      fireCd: 0,
      invuln: 1.4,
      shieldCd: 0,
      vx: 0,
      vz: 0,
      tilt: 0,
      droneBonus: 0,
    };
    this.input.enabled = true;
    this.input.hasDragged = false;
    this.hud.el.joystickHint?.classList.remove('fade');
  }

  // ------------------------------------------------------------ drones
  _syncDrones() {
    const p = this.player;
    if (!p) return;
    const want = Math.min(3, p.cfg.drones + p.droneBonus);
    const art = this.assets.textures.shipArt?.[p.cfg.ship.id];
    while (this.drones.length < want) {
      const g = new THREE.Sprite(new THREE.SpriteMaterial({
        transparent: true, depthWrite: false, toneMapped: false,
        color: new THREE.Color(0xa8e8ff), opacity: 0.92,
      }));
      if (art) g.material.map = art;
      g.scale.set(1.15, 1.15, 1);
      this.scene.add(g);
      this.drones.push({ g, angle: (this.drones.length / Math.max(1, want)) * Math.PI * 2, fireCd: 0.2 + Math.random() * 0.4, t: Math.random() * 6 });
    }
    while (this.drones.length > want) {
      const d = this.drones.pop();
      this.scene.remove(d.g);
    }
  }

  _updateDrones(dt) {
    const p = this.player;
    if (!p) return;
    const t = this.elapsed;
    this.drones.forEach((d, i) => {
      const a = d.angle + t * 0.85;
      const rx = 1.55;
      const rz = 0.85;
      const targetX = p.group.position.x + Math.cos(a) * rx;
      const targetZ = p.group.position.z - 0.25 + Math.sin(a) * rz;
      const k = Math.min(1, dt * 7);
      d.g.position.x += (targetX - d.g.position.x) * k;
      d.g.position.z += (targetZ - d.g.position.z) * k;
      d.g.position.y = 1.05 + Math.sin(t * 2.4 + i) * 0.12;
      if (d.g.material) d.g.material.rotation = Math.sin(t * 3 + i) * 0.14;
      const pulse = 1 + Math.sin(t * 5 + i) * 0.05;
      const sc = 1.15 * pulse;
      d.g.scale.set(sc, sc, 1);

      d.fireCd -= dt;
      if (d.fireCd <= 0) {
        d.fireCd = 0.44;
        this._droneFire(d.g.position);
      }
    });
  }

  _droneFire(from) {
    const target = this._nearestEnemy(from);
    let angle = 0;
    if (target) {
      angle = Math.atan2(target.x - from.x, -(target.z - from.z));
      angle = THREE.MathUtils.clamp(angle, -0.5, 0.5);
    }
    const speed = 40;
    const vx = Math.sin(angle) * speed;
    const vz = -Math.cos(angle) * speed;
    const s = new THREE.Sprite(this._beamMat(this.mats.droneBeams, Math.atan2(vx, -vz)));
    s.position.set(from.x, 0.35, from.z - 0.4);
    s.scale.set(0.2, 1.05, 1);
    this.scene.add(s);
    this.playerBullets.push({
      s, vx, vz, dmg: Math.max(3, this.player.cfg.dmg * 0.32),
      life: 1.4, pierce: 0, drone: true,
    });
  }

  _nearestEnemy(from) {
    let best = null;
    let bestD = Infinity;
    for (const e of this.enemies) {
      const dz = from.z - e.g.position.z;
      if (dz < -1) continue; // chỉ bắn mục tiêu phía trước
      const d = Math.abs(e.g.position.x - from.x) + dz * 0.2;
      if (d < bestD) { bestD = d; best = e.g.position; }
    }
    if (!best && this.boss) best = this.boss.g.position;
    return best;
  }

  // ------------------------------------------------------------ pause / over
  pause() {
    if (this.state !== 'playing') return;
    this.state = 'paused';
    this.input.enabled = false;
    this.input.dragging = false;
    this.input.drag.set(0, 0, 0);
    this.hud.showScreen('pause');
  }

  resume() {
    if (this.state !== 'paused') return;
    this.state = 'playing';
    this.input.enabled = true;
    this.hud.hideScreens();
    this.sfx.resume();
  }

  togglePause() {
    if (this.state === 'playing') this.pause();
    else if (this.state === 'paused') this.resume();
  }

  gameOver(success = false) {
    if (this.state === 'over') return;
    this.state = 'over';
    this.input.enabled = false;
    this.sfx.gameOver();

    const scoreMul = (this.modifiers?.scoreMul || 1) * (this.mode === 'daily' ? 1 : 1);
    const finalScore = Math.round(this.score * scoreMul);
    const coins = Math.round(coinsForRun({ score: finalScore, kills: this.kills, bosses: this.bossesKilled || 0, mode: this.mode })
      * (1 + (this.player?.cfg?.coinsBonus || 0)) * (this.mode === 'daily' ? 2 : 1));

    let stars = 0;
    if (success) {
      const hpPct = this.player ? this.player.hp / this.player.maxHp : 0;
      stars = hpPct >= 0.8 ? 3 : hpPct >= 0.5 ? 2 : 1;
      if (this.level?.isBoss && stars < 3) stars = Math.min(3, stars + 1);
    }

    const record = this.profile ? this.profile.recordBest(this._bestKey(), finalScore) : false;
    if (coins > 0) this.profile?.addCoins(coins);

    if (success && this.mode === 'campaign' && this.level) {
      this.profile?.setStars(this.chapter, this.levelIndex, stars);
    }

    if (success && this.mode === 'campaign' && this.level?.isBoss) {
      this.profile?.unlockChapter(Math.min(CHAPTERS.length, this.chapter + 1));
    }

    this.hud.showResult({
      mode: this.mode,
      modeLabel: MODE_LABEL[this.mode] || '',
      success,
      score: finalScore,
      best: this.profile?.bestOf(this._bestKey()) || finalScore,
      newRecord: record,
      kills: this.kills,
      wave: this.wave,
      stars,
      coins,
      level: this.level,
      chapter: this.chapter,
      daily: this.daily,
      onNext: success && this.mode === 'campaign' && !this.level?.isBoss ? () => this.start('campaign', { chapter: this.chapter, level: this.levelIndex + 1 }) : null,
    });

    this.onResult?.({
      mode: this.mode, success, score: finalScore, coins, stars,
      chapter: this.chapter, level: this.levelIndex,
    });
  }

  _bestKey() {
    return this.mode === 'campaign' ? 'campaign' : this.mode;
  }

  // ------------------------------------------------------------ waves
  startWave(n) {
    this.wave = n;
    this.spawnQueue = [];
    this.nextWaveTimer = 0;

    if (this.mode === 'bossrush') {
      this.isBossWave = true;
      const roster = ['imperial', 'pancake', 'dreadnought', 'imperial', 'pancake', 'dreadnought'];
      const bossKey = roster[(n - 1) % roster.length];
      this.hud.banner(`BOSS ${n} · ${BOSSES[bossKey].name}`, true);
      this.sfx.boss();
      this.spawnQueue.push({ t: 1.0, kind: 'boss', x: 0, boss: bossKey, bossIndex: n });
      return;
    }

    if (this.mode === 'campaign') {
      const info = this.level;
      if (info.isBoss) {
        this.isBossWave = true;
        if (n === 1) {
          this.hud.banner('CẢNH BÁO BOSS', true);
          this.sfx.boss();
          this.spawnQueue.push({ t: 1.3, kind: 'boss', x: 0, boss: info.boss });
        }
        return;
      }
      const total = info.objective === 'survive' ? 1 : 2 + Math.min(3, Math.floor(info.difficulty));
      if (n > total) return;
      this.isBossWave = false;
      if (n === 1) {
        this.hud.banner(info.objective === 'survive' ? 'SINH TỒN' : `MÀN ${info.index}`);
        this.sfx.wave();
      }
      this._buildCampaignWave(info, n);
      return;
    }

    // endless / daily
    this.isBossWave = n % 5 === 0;
    if (this.isBossWave) {
      this.hud.banner('CẢNH BÁO BOSS', true);
      this.sfx.boss();
      const bossKey = n >= 20 ? 'dreadnought' : n >= 10 ? 'pancake' : 'imperial';
      this.spawnQueue.push({ t: 1.2, kind: 'boss', x: 0, boss: bossKey });
    } else {
      this.hud.banner(`ĐỢT ${n}`);
      this.sfx.wave();
      this._buildEndlessWave(n);
    }
  }

  _waveScale() {
    const base = this.mode === 'campaign' ? this.level.difficulty : 1 + (this.wave - 1) * 0.085;
    const daily = this.mode === 'daily' ? this.daily.difficulty : 1;
    return Math.min(2.6, base * daily);
  }

  _buildCampaignWave(info, n) {
    const xl = this.bounds.x;
    const q = this.spawnQueue;
    const pool = info.enemyPool || this.enemyPool;
    const hpScale = this._waveScale() * (this.modifiers.enemy?.hpMul || 1) * 0.92;
    const countMul = this.modifiers.spawn?.countMul || 1;
    const formation = FORMATIONS[(info.index + n) % FORMATIONS.length];
    const budget = Math.round((5 + info.index * 1.5 + n * 2) * countMul / (info.objective === 'survive' ? 2 : 1));

    const list = this._formationList(formation, budget, pool, xl);
    list.forEach((e, i) => q.push({ t: 0.2 + i * 0.16, kind: e.kind, x: e.x, hpScale }));

    // "ruồi" bay ngang vào từ hai mép màn hình
    const sideCount = 2 + Math.min(3, Math.floor(info.difficulty || 1));
    for (let i = 0; i < sideCount; i++) {
      q.push({
        t: 1.6 + i * 1.15,
        kind: i % 3 === 2 ? 'interceptor' : (i % 2 ? 'skimmer' : 'swarm'),
        from: i % 2 ? 'right' : 'left',
        hpScale: hpScale * 0.9,
      });
    }

    if (info.objective === 'survive') {
      this.surviveLeft = info.surviveTime;
      // tiếp viện trong lúc sinh tồn
      for (let t = 6; t < info.surviveTime; t += 5) {
        const k = pool[(t / 5) % pool.length | 0];
        const x = (Math.random() * 2 - 1) * xl * 0.75;
        q.push({ t, kind: k, x, hpScale });
      }
    }
  }

  _formationList(formation, budget, pool, xl) {
    const out = [];
    const pick = (i) => pool[i % pool.length];
    if (formation === 'line') {
      for (let i = 0; i < budget; i++) {
        const u = budget === 1 ? 0.5 : i / (budget - 1);
        out.push({ kind: pick(i), x: -xl * 0.82 + u * xl * 1.64 });
      }
    } else if (formation === 'vee') {
      const rows = Math.ceil(budget / 2);
      for (let i = 0; i < rows; i++) {
        out.push({ kind: pick(i), x: -i * xl * 0.16 });
        out.push({ kind: pick(i + 1), x: i * xl * 0.16 });
      }
    } else if (formation === 'snipers') {
      for (let i = 0; i < budget; i++) {
        out.push({ kind: i < budget / 2 ? 'gunner' : pick(i), x: i % 2 ? xl * 0.55 : -xl * 0.55 });
      }
    } else if (formation === 'tanks') {
      out.push({ kind: 'tank', x: -xl * 0.45 });
      out.push({ kind: 'bomber', x: xl * 0.45 });
      for (let i = 0; i < budget; i++) {
        out.push({ kind: i % 3 === 0 ? 'meteor' : pick(i), x: -xl * 0.8 + (i / Math.max(1, budget - 1)) * xl * 1.6 });
      }
    } else if (formation === 'ring') {
      const n = Math.min(14, budget + 2);
      for (let i = 0; i < n; i++) {
        const a = (i / n) * Math.PI * 2;
        out.push({ kind: pick(i), x: Math.cos(a) * xl * 0.8 });
      }
    } else {
      for (let i = 0; i < budget; i++) {
        out.push({ kind: pick(i * 2), x: -xl * 0.75 + Math.random() * xl * 1.5 });
        if (i % 3 === 0) out.push({ kind: 'swarm', x: Math.random() * xl * 1.2 - xl * 0.6 });
      }
    }
    return out;
  }

  _buildEndlessWave(n) {
    const xl = this.bounds.x;
    const q = this.spawnQueue;
    const pool = this.enemyPool;
    const hpScale = this._waveScale() * (this.modifiers.enemy?.hpMul || 1);
    const countMul = this.modifiers.spawn?.countMul || 1;
    const formation = FORMATIONS[(n - 1) % FORMATIONS.length];
    const budget = Math.round((4 + n * 0.9) * countMul);
    const list = this._formationList(formation, budget, pool, xl);
    list.forEach((e, i) => q.push({ t: 0.1 + i * 0.15, kind: e.kind, x: e.x, hpScale }));

    for (let i = 0; i < 2 + (n % 3); i++) {
      q.push({
        t: 1.2 + i * 1.3,
        kind: i % 2 ? 'skimmer' : 'swarm',
        from: i % 2 ? 'right' : 'left',
        hpScale: hpScale * 0.9,
      });
    }
  }

  // ------------------------------------------------------------ spawns
  _spawnEnemy(kind, x, hpScale = 1, opts = {}) {
    const cfg = ENEMY[kind] || ENEMY.swarm;
    const from = opts.from || 'top';
    const size = cfg.size * (cfg.art === 'meteor' ? 1.5 : 1.75);
    let z;
    if (from === 'top') {
      z = this.bounds.zMin - 1.2;
      x = x ?? (Math.random() * 2 - 1) * this.bounds.x * 0.8;
    } else {
      // bay ngang vào từ mép trái/phải
      x = from === 'left' ? -this.bounds.x - 1.4 : this.bounds.x + 1.4;
      z = opts.z ?? (Math.random() * 9 - 7);
    }

    const mat = new THREE.SpriteMaterial({
      transparent: true,
      depthWrite: false,
      toneMapped: false,
      color: new THREE.Color(cfg.tint || 0xffffff),
      rotation: Math.PI + (Math.random() - 0.5) * 0.4,
    });
    const enemyTex = this.assets.textures.enemyArt?.[cfg.art] || this.assets.textures.enemyArt?.wasp;
    if (enemyTex) mat.map = enemyTex;
    else mat.color.setHex(0xff5a7a);
    const g = new THREE.Sprite(mat);
    g.scale.set(size, size, 1);
    g.position.set(x, 0, z);
    this.scene.add(g);

    const hp = Math.max(1, Math.round(cfg.hp * hpScale));

    this.enemies.push({
      kind, cfg, g, mat, baseSize: size, hp, maxHp: hp, from,
      baseColor: new THREE.Color(cfg.tint || 0xffffff),
      dirX: from === 'left' ? 1 : from === 'right' ? -1 : 0,
      x0: x, z0: z, t: Math.random() * 5, bob: Math.random() * Math.PI * 2,
      fireCd: 0.9 + Math.random() * 1.8,
      radius: cfg.radius, score: cfg.score, coins: cfg.coins || 1,
      rotSpeed: (Math.random() - 0.5) * 1.2,
    });
  }

  _spawnBoss(key = 'imperial', index = 0) {
    const def = BOSSES[key] || BOSSES.imperial;
    const size = def.size || 7.4;

    const g = new THREE.Group();
    // xuất phát từ phía xa rồi lao vào sân đấu (xem _updateBoss)
    g.position.set(0, 5.6, -24);

    // hào quang phía sau
    const aura = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glowTexture(), color: def.color, transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending, opacity: 0.6,
    }));
    aura.scale.set(size * 1.9, size * 1.9, 1);
    aura.position.set(0, 0, -0.6);
    g.add(aura);

    // thân robot vẽ tay
    const art = this.assets.textures.bossArt?.[def.art || key];
    const mat = new THREE.SpriteMaterial({ transparent: true, depthWrite: false, toneMapped: false });
    if (art) mat.map = art;
    const sprite = new THREE.Sprite(mat);
    sprite.scale.set(size, size, 1);
    g.add(sprite);

    // lưỡi chém năng lượng (ẩn, chỉ hiện khi ra đòn cận chiến)
    const blade = new THREE.Sprite(this.mats.blade.clone());
    blade.scale.set(size * 1.05, size * 1.95, 1);
    blade.position.set(0, -2.5, 1.1);
    blade.material.opacity = 0;
    g.add(blade);

    // ---- các bộ phận "sống": lõi năng lượng, họng súng, quầng kiếm, vệ tinh
    const core = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glowTexture(), color: 0x59e6ff, transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending, opacity: 0.4,
    }));
    core.position.set(0, -size * 0.06, 0.8);
    core.scale.set(size * 0.5, size * 0.5, 1);
    core.renderOrder = 2;
    g.add(core);

    const coreHot = new THREE.Sprite(new THREE.SpriteMaterial({
      map: this.assets.textures.spark || glowTexture(), color: 0xffffff, transparent: true,
      depthWrite: false, blending: THREE.AdditiveBlending, opacity: 0.5,
    }));
    coreHot.position.set(0, -size * 0.06, 0.82);
    coreHot.scale.set(size * 0.16, size * 0.16, 1);
    coreHot.renderOrder = 3;
    g.add(coreHot);

    // loé họng súng máy (bên trái robot)
    const muzzle = new THREE.Sprite(new THREE.SpriteMaterial({
      map: this.assets.textures.spark || glowTexture(), color: 0xfff0c0, transparent: true,
      depthWrite: false, blending: THREE.AdditiveBlending, opacity: 0,
    }));
    muzzle.position.set(-size * 0.31, -size * 0.24, 0.95);
    muzzle.scale.set(size * 0.5, size * 0.5, 1);
    muzzle.renderOrder = 4;
    g.add(muzzle);

    // quầng lửa quanh lưỡi kiếm
    const sword = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glowTexture(), color: 0xffa54a, transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending, opacity: 0.2,
    }));
    sword.position.set(size * 0.31, size * 0.02, 0.9);
    sword.scale.set(size * 0.42, size * 0.62, 1);
    sword.renderOrder = 3;
    g.add(sword);

    // vệt chém hình lưỡi liềm (chỉ hiện lúc bổ xuống)
    const arc = new THREE.Sprite(this.mats.arc.clone());
    arc.position.set(0, 0, 0.7);
    arc.scale.set(size * 2.5, size * 2.5, 1);
    arc.material.opacity = 0;
    arc.renderOrder = 5;
    g.add(arc);

    // 2 vệ tinh bay vòng quanh boss
    const orbiters = [];
    for (let i = 0; i < 2; i++) {
      const orb = new THREE.Sprite(new THREE.SpriteMaterial({
        map: glowTexture(), color: def.color, transparent: true, depthWrite: false,
        blending: THREE.AdditiveBlending, opacity: 0.85,
      }));
      orb.scale.set(size * 0.24, size * 0.24, 1);
      orb.renderOrder = 3;
      g.add(orb);
      orbiters.push({ s: orb, ang: i * Math.PI + 0.6, r: size * 0.72, spin: i ? -0.85 : 0.85, fire: 1.6 + i * 0.9 });
    }

    this.scene.add(g);

    const waveScale = this.mode === 'campaign'
      ? this._waveScale()
      : this.mode === 'bossrush' ? 1 + (index - 1) * 0.75 : 1 + (this.wave - 1) * 0.12;
    const hp = Math.round(def.hp * waveScale);

    sprite.scale.set(size * 0.55, size * 0.55, 1);
    aura.scale.set(size * 1.9 * 0.55, size * 1.9 * 0.55, 1);

    this.boss = {
      key, def, g, sprite, aura, blade, size, hp, maxHp: hp, t: 0,
      beat: 1.6, queue: [], patternIndex: 0, phase: 1, phase2: false,
      radius: def.radius, name: def.name, zHome: -11.5,
      slash: null, color: def.color,
      // trạng thái diễn hoạt
      entering: true, enter: 0, enterDur: 1.2,
      tilt: 0, heading: 0, targetX: 0, targetZ: -11.5, moveT: 1.4,
      charge: 0, recoil: 0, flash: 0, action: null,
      core, coreHot, muzzle, sword, arc, orbiters, swing: 0, swingTrailT: 0,
    };
    this.hud.setBossName?.(def.name);
    this.sfx.boss();
  }

  // ------------------------------------------------------------ update
  update(dt) {
    if (this.state !== 'playing') return;
    this.elapsed += dt;
    this._updateCombo(dt);
    this._updateObjective(dt);
    this._updatePlayer(dt);
    this._updateDrones(dt);
    this._updateWave(dt);
    this._updateEnemies(dt);
    this._updateBoss(dt);
    this._updateBossDeath(dt);
    this._updateBullets(dt);
    this._updatePickups(dt);
    this._updateEffects(dt);
    this._collide();
    this._updateCamera(dt);

    this.hud.update({
      score: Math.round(this.score),
      wave: this.wave,
      remaining: this.enemies.length + this.spawnQueue.length + (this.boss ? 1 : 0),
      hpPct: this.player ? (this.player.hp / this.player.maxHp) * 100 : 0,
      hpValue: this.player ? this.player.hp : 0,
      shields: this.player ? this.player.shield : 0,
      weapon: this.player ? this.player.weapon : 1,
      bossPct: this.boss ? (this.boss.hp / this.boss.maxHp) * 100 : null,
      combo: this.combo,
      timer: this.surviveLeft > 0 ? Math.ceil(this.surviveLeft) : null,
      objective: this._objectiveText(),
    });
  }

  _objectiveText() {
    if (this.mode === 'campaign' && this.level) {
      if (this.level.isBoss) return 'HẠ GỤC BOSS';
      if (this.level.objective === 'survive') return 'SINH TỒN';
      return `DỌN SẠCH ${this.level.name}`;
    }
    if (this.mode === 'bossrush') return 'HẠ GỤC CÁC BOSS';
    if (this.mode === 'daily') return this.daily?.modifier?.name || '';
    return 'SINH TỒN CÀNG LÂU CÀNG TỐT';
  }

  _updateObjective(dt) {
    if (this.surviveLeft > 0) {
      this.surviveLeft -= dt;
      if (this.surviveLeft <= 0) {
        this.surviveLeft = 0;
        this._completeLevel();
      }
    }
  }

  _completeLevel() {
    if (this.state !== 'playing') return;
    // quét sạch địch còn lại rồi thắng
    this.enemies.forEach((e) => {
      this._boom(e.g.position.x, e.g.position.z, 1.2, false);
      this.scene.remove(e.g);
    });
    this.enemies = [];
    this.enemyBullets.forEach((b) => this.scene.remove(b.s));
    this.enemyBullets = [];
    this.spawnQueue = [];
    this.hud.banner('HOÀN THÀNH');
    this.gameOver(true);
  }

  _updateCombo(dt) {
    if (this.comboTimer > 0) {
      this.comboTimer -= dt;
      if (this.comboTimer <= 0) this.combo = 1;
    }
  }

  _updatePlayer(dt) {
    const p = this.player;
    if (!p) return;

    const axis = this.input.keyAxis();
    const drag = this.input.consumeDrag();
    let targetVx = axis.x * p.cfg.speed;
    let targetVz = axis.z * p.cfg.speed * 0.72;

    const stick = this.input.scheme === 'joystick' ? this.input.stick : null;
    if (stick && this.input.dragging && this.input.stickAmount() > 0.04) {
      const amount = this.input.stickAmount();
      const len = Math.max(0.0001, stick.length());
      targetVx = (stick.x / len) * p.cfg.speed * 1.45 * amount;
      targetVz = (stick.z / len) * p.cfg.speed * 1.1 * amount;
    }

    p.vx += (targetVx - p.vx) * Math.min(1, dt * 9);
    p.vz += (targetVz - p.vz) * Math.min(1, dt * 9);

    p.group.position.x += p.vx * dt + drag.x;
    p.group.position.z += p.vz * dt + drag.z;

    const b = this.bounds;
    p.group.position.x = THREE.MathUtils.clamp(p.group.position.x, -b.x, b.x);
    p.group.position.z = THREE.MathUtils.clamp(p.group.position.z, -2.2, b.zMax - 0.5);

    // ---- thân tàu "sống": nghiêng vào hướng bay, nhún nhẹ, co giãn theo tốc độ
    const nx = THREE.MathUtils.clamp(p.vx / p.cfg.speed, -1, 1);
    const roll = -nx * 0.26;
    const yaw = -nx * 0.2;
    p.tilt += (roll - p.tilt) * Math.min(1, dt * 7);
    const bob = Math.sin(this.elapsed * 2.4) * 0.05;
    p.kick = Math.max(0, p.kick - dt * 2.6);
    p.group.position.y = bob - p.kick * 0.22;
    p.sprite.material.rotation = p.tilt + Math.sin(this.elapsed * 1.55) * 0.016;
    const stretch = 1 + Math.min(0.1, Math.abs(p.vz) * 0.006);
    p.sprite.scale.set(
      3.05 * (1 - Math.abs(p.tilt) * 0.1 - Math.min(0.05, Math.abs(p.vx) * 0.003)),
      3.05 * stretch,
      1,
    );
    p.group.rotation.z = 0;
    p.group.rotation.y = yaw;

    // ---- hai luồng lửa: rung theo nhịp động cơ, dài ra khi tăng tốc
    const thrust = Math.min(1, (Math.abs(p.vz) + Math.abs(p.vx) * 0.5) / Math.max(1, p.cfg.speed));
    const flick = 0.86 + Math.sin(this.elapsed * 42) * 0.09 + Math.random() * 0.07;
    const len = (0.95 + thrust * 0.7) * flick;
    for (const [flame, side] of [[p.flameL, -1], [p.flameR, 1]]) {
      flame.scale.set(0.52 * flick, 1.15 * len, 1);
      flame.material.opacity = 0.62 + Math.random() * 0.3;
      flame.position.x = side * (0.37 + p.tilt * 0.28);
    }
    p.engine.scale.set(1.15 * flick, (1.6 + thrust * 1.1) * flick, 1);
    p.engine.material.opacity = 0.35 + Math.random() * 0.18;

    // cánh vỗ + nghiêng theo thân; hai luồng lửa bẻ theo hướng lái
    if (p.wingL && p.wingR) {
      const flap = Math.sin(this.elapsed * 5.2) * (0.075 + Math.min(0.095, Math.abs(p.vx) * 0.006));
      p.wingL.material.rotation = p.tilt - flap;
      p.wingR.material.rotation = p.tilt + flap;
      // bám đúng tỉ lệ thân để mối nối luôn nằm dưới vỏ
      p.wingL.scale.copy(p.sprite.scale);
      p.wingR.scale.copy(p.sprite.scale);
    }
    p.flameL.material.rotation = p.tilt * 0.9;
    p.flameR.material.rotation = p.tilt * 0.9;

    // đèn định vị nháy + buồng lái thở
    const blink = Math.sin(this.elapsed * 6.4) > 0.5 ? 1 : 0.2;
    p.navL.material.opacity = blink * 0.85;
    p.navR.material.opacity = (blink > 0.5 ? 0.2 : 0.85) * 0.85;
    p.cockpit.material.opacity = 0.32 + Math.abs(Math.sin(this.elapsed * 2.2)) * 0.22;

    // ---- khiên: quầng xanh nhấp nháy khi còn lá chắn
    const shieldOn = p.shield > 0;
    p.shieldBubble.material.opacity = shieldOn
      ? 0.12 + 0.05 * Math.sin(this.elapsed * 4.2) + Math.min(0.1, p.shield * 0.012)
      : 0;

    // ---- loé súng ở đầu cánh mỗi lần bắn
    if (p.muzzleT > 0) {
      p.muzzleT = Math.max(0, p.muzzleT - dt);
      const k = p.muzzleT / 0.08;
      for (const m of [p.muzzleL, p.muzzleR]) {
        m.material.opacity = k * 0.9;
        const ms = 0.55 + (1 - k) * 0.35;
        m.scale.set(ms, ms, 1);
        m.material.rotation = this.elapsed * 9 + (m === p.muzzleL ? 0 : 1.7);
      }
    } else {
      p.muzzleL.material.opacity = 0;
      p.muzzleR.material.opacity = 0;
    }

    // ---- vệt tốc độ khi lướt ngang / lao lên
    p.ghostT -= dt;
    const speedRatio = Math.hypot(p.vx, p.vz) / Math.max(1, p.cfg.speed);
    if (speedRatio > 0.42 && p.ghostT <= 0) {
      p.ghostT = 0.06;
      const gh = p.ghosts.find((g) => g.life <= 0) || p.ghosts[0];
      gh.life = gh.max;
      gh.s.visible = true;
      gh.s.position.copy(p.group.position);
      gh.s.position.y -= 0.05;
      gh.s.material.rotation = p.tilt;
      gh.s.scale.set(3.05, 3.05, 1);
    }
    for (const gh of p.ghosts) {
      if (gh.life <= 0) continue;
      gh.life -= dt;
      const k = Math.max(0, gh.life / gh.max);
      gh.s.material.opacity = k * 0.16;
      gh.s.scale.set(3.05 * (1 - (1 - k) * 0.08), 3.05 * (1 - (1 - k) * 0.08), 1);
      if (gh.life <= 0) gh.s.visible = false;
    }

    if (p.invuln > 0) {
      p.invuln -= dt;
      p.group.visible = Math.floor(this.elapsed * 16) % 2 === 0 || p.invuln <= 0;
    } else if (!p.group.visible) {
      p.group.visible = true;
    }

    // nhá đỏ khi trúng đạn
    if (p.hitT > 0) {
      p.hitT = Math.max(0, p.hitT - dt);
      const k = p.hitT / 0.22;
      p.sprite.material.color.setRGB(1, 1 - 0.6 * k, 1 - 0.6 * k);
      p.halo.material.opacity = 0.55 + 0.45 * k;
    }

    // khiên tự hồi chậm (tàu Zenith nhanh hơn)
    if (p.shield < p.shieldCap) {
      p.shieldCd += dt;
      const need = 16 / (p.cfg.shieldRegen || 1);
      if (p.shieldCd >= need) {
        p.shieldCd = 0;
        p.shield += 1;
        this.sfx.pickup?.();
      }
    }

    p.fireCd -= dt;
    if (p.fireCd <= 0 && (this.autoFire || this.input.dragging)) {
      this._fire();
      p.fireCd = p.cfg.fireRate;
    }
  }

  _fire() {
    const p = this.player;
    if (!p) return;
    const patterns = [
      [0],
      [-0.035, 0.035],
      [-0.11, 0, 0.11],
      [-0.17, -0.055, 0.055, 0.17],
      [-0.26, -0.13, 0, 0.13, 0.26],
    ];
    const angles = patterns[Math.min(patterns.length, p.weapon) - 1];
    const dmgMul = this.modifiers?.player?.dmgMul || 1;
    const dmg = p.cfg.dmg * dmgMul * (p.weapon >= 4 ? 0.85 : 1);

    // 3 kiểu đạn theo tàu: tia mảnh / sao plasma / đạn hạng nặng
    const style = p.fireStyle || 'bolt';
    const set = style === 'star' ? this.mats.playerStars
      : style === 'heavy' ? this.mats.playerHeavy
        : this.mats.playerBeams;
    const speed = style === 'heavy' ? 38 : style === 'star' ? 50 : 45;
    const size = style === 'star' ? [0.62, 0.62] : style === 'heavy' ? [0.46, 1.9] : [0.26, 1.55];

    angles.forEach((a) => {
      const vx = Math.sin(a) * speed;
      const vz = -Math.cos(a) * speed;
      const s = new THREE.Sprite(this._beamMat(set, Math.atan2(vx, -vz)));
      s.position.set(p.group.position.x + Math.sin(a) * 0.55, 0.36, p.group.position.z - 0.9);
      s.scale.set(size[0], size[1], 1);
      this.scene.add(s);
      this.playerBullets.push({ s, vx, vz, dmg, life: 1.8, pierce: p.cfg.pierce || 0, style });
    });

    const flash = new THREE.Sprite(this.mats.flash);
    flash.position.set(p.group.position.x, 0.4, p.group.position.z - 0.95);
    flash.scale.set(0.9, 0.9, 1);
    this.scene.add(flash);
    this.sparks.push({ s: flash, t: 0, life: 0.09, size: 0.9, grow: 1.8 });

    // giật nhẹ + loé đầu nòng
    p.kick = 1;
    p.muzzleT = 0.08;
    p.muzzleL.position.set(-1.0 + (Math.random() - 0.5) * 0.1, 0.5, 1.3);
    p.muzzleR.position.set(1.0 + (Math.random() - 0.5) * 0.1, 0.5, 1.3);

    this.sfx.shoot();
  }

  _updateWave(dt) {
    for (let i = this.spawnQueue.length - 1; i >= 0; i--) {
      const item = this.spawnQueue[i];
      item.t -= dt;
      if (item.t <= 0) {
        this.spawnQueue.splice(i, 1);
        if (item.kind === 'boss') this._spawnBoss(item.boss, item.bossIndex);
        else this._spawnEnemy(item.kind, item.x, item.hpScale ?? 1, { from: item.from, z: item.z });
      }
    }

    const cleared = this.spawnQueue.length === 0 && this.enemies.length === 0 && !this.boss;
    if (!cleared) { this.nextWaveTimer = 0; return; }

    // mục tiêu sinh tồn: không cần dọn sạch
    if (this.surviveLeft > 0) return;

    this.nextWaveTimer += dt;
    if (this.nextWaveTimer < (this.isBossWave ? 2.2 : 1.4)) return;
    this.nextWaveTimer = 0;

    if (this.mode === 'campaign' && this.level) {
      if (this.level.isBoss) {
        // boss đã chết -> thắng
        this._completeLevel();
        return;
      }
      const total = 2 + Math.min(3, Math.floor(this.level.difficulty));
      if (this.wave >= total) {
        this._completeLevel();
        return;
      }
      this.startWave(this.wave + 1);
      return;
    }

    if (this.mode === 'bossrush') {
      // hồi máu giữa các boss
      if (this.player) this.player.hp = Math.min(this.player.maxHp, this.player.hp + this.player.maxHp * 0.3);
      this.hud.banner('HỒI MÁU +30%');
      this.startWave(this.wave + 1);
      return;
    }

    this.startWave(this.wave + 1);
  }

  _updateEnemies(dt) {
    const p = this.player;
    for (let i = this.enemies.length - 1; i >= 0; i--) {
      const e = this.enemies[i];
      e.t += dt;
      if (e.mixer) e.mixer.update(dt);
      const g = e.g;

      const face = Math.PI; // sprite vẽ mũi hướng lên → lật 180° để chúi về người chơi

      if (e.from && e.from !== 'top') {
        // bay ngang qua màn hình, hơi chúi xuống
        g.position.x += e.dirX * e.cfg.speed * 0.95 * dt;
        g.position.z += e.cfg.speed * 0.34 * dt;
        g.position.y = Math.sin(e.t * 4 + e.bob) * 0.14;
        e.mat.rotation = face + e.dirX * 1.25 + Math.sin(e.t * 2 + e.bob) * 0.1;
        if (e.cfg.fire && e.t > 0.5) this._enemyFire(e, dt);
      } else if (e.cfg.behavior === 'dive') {
        g.position.z += e.cfg.speed * dt;
        const sway = Math.sin(e.t * e.cfg.wobble + e.bob);
        g.position.x = e.x0 + sway * e.cfg.amp;
        g.position.y = Math.sin(e.t * 1.8 + e.bob) * 0.2;
        e.mat.rotation = face + sway * 0.26;
        if (e.cfg.fire) this._enemyFire(e, dt);
      } else if (e.cfg.behavior === 'hover') {
        const targetZ = e.cfg.zHold - (this.wave >= 6 ? 1.2 : 0);
        g.position.z += (targetZ - g.position.z) * Math.min(1, dt * 1.6);
        g.position.x = e.x0 + Math.sin(e.t * e.cfg.wobble + e.bob) * e.cfg.amp;
        g.position.y = 0.35 + Math.sin(e.t * 2 + e.bob) * 0.16;
        e.mat.rotation = face + Math.sin(e.t * 0.9 + e.bob) * 0.12;
        if (e.cfg.fire) this._enemyFire(e, dt);
      } else if (e.cfg.behavior === 'tank') {
        g.position.z += e.cfg.speed * dt;
        const sway = Math.sin(e.t * e.cfg.wobble + e.bob);
        g.position.x = e.x0 + sway * e.cfg.amp;
        e.mat.rotation = face + sway * 0.1;
        if (e.cfg.fire) this._enemyFire(e, dt);
      } else if (e.cfg.behavior === 'drift') {
        g.position.z += e.cfg.speed * dt;
        g.position.x = e.x0 + Math.sin(e.t * e.cfg.wobble + e.bob) * e.cfg.amp;
        e.mat.rotation += dt * (e.cfg.spin || 0.8);
      } else if (e.cfg.behavior === 'orbit') {
        const R = 2.6 + Math.sin(e.t * 0.5 + e.bob) * 0.7;
        g.position.x = e.x0 + Math.cos(e.t * 0.95) * R;
        g.position.z = (e.cfg.zHold || -6) + Math.sin(e.t * 0.95) * 1.6;
        g.position.y = 0.3;
        e.mat.rotation = face - e.t * 0.95;
      }

      // sương mù theo độ xa: địch ở cuối màn mờ dần vào nền → cảm giác chiều sâu
      if (e.mat) {
        const k = THREE.MathUtils.clamp((3.5 - g.position.z) / 22, 0, 1) * 0.42;
        e.mat.color.copy(e.baseColor).lerp(DEPTH_HAZE, k);
      }

      // nhịp "thở" nhẹ cho sprite sống động
      if (e.mat && e.cfg.art !== 'meteor') {
        const k = 1 + Math.sin(e.t * 4.2 + e.bob) * 0.035;
        g.scale.set(e.baseSize * k, e.baseSize * k, 1);
      }

      if (g.position.z > this.bounds.zMax + 2.5
        || g.position.x > this.bounds.x + 4 || g.position.x < -this.bounds.x - 4) {
        this.scene.remove(g);
        this.enemies.splice(i, 1);
        continue;
      }

      if (p && p.invuln <= 0) {
        const dx = g.position.x - p.group.position.x;
        const dz = g.position.z - p.group.position.z;
        if (dx * dx + dz * dz < (e.radius + 0.75) ** 2) {
          this._boom(g.position.x, g.position.z, 1.7, false);
          this.scene.remove(g);
          this.enemies.splice(i, 1);
          this._damagePlayer(e.kind === 'meteor' ? 20 : 24, true);
        }
      }
    }
  }

  _enemyFire(e, dt) {
    e.fireCd -= dt;
    if (e.fireCd > 0) return;
    const p = this.player;
    if (!p) return;
    e.fireCd = (e.cfg.fire || 2.2) * (0.85 + Math.random() * 0.35);

    const from = e.g.position;
    const dx = p.group.position.x - from.x;
    const dz = p.group.position.z - from.z;
    const base = Math.atan2(dx, -dz);
    const speedMul = this.modifiers.enemy?.bulletSpeed || 1;

    if (e.kind === 'bomber') {
      // chùm sao plasma bung rộng
      for (const a of [-0.34, -0.12, 0.12, 0.34]) this._enemyShot(from, base + a, 10.5 * speedMul, 'star');
    } else if (e.kind === 'tank' || e.kind === 'brute') {
      for (const a of [-0.2, 0, 0.2]) this._enemyShot(from, base + a, 11.5 * speedMul, 'heavy');
    } else if (e.kind === 'interceptor') {
      for (const a of [-0.1, 0.1]) this._enemyShot(from, base + a, 14 * speedMul);
    } else {
      this._enemyShot(from, base, 13 * speedMul);
    }
    this.sfx.enemyShoot();
  }

  /**
   * Đạn hình học: diamond | square | triangle | hex | star | ring | needle | cross
   */
  _geoShot(x, z, vx, vz, shape = 'diamond', color = 0xff6a8a, opts = {}) {
    const mat = this._geoMat(shape, color).clone();
    mat.rotation = Math.random() * Math.PI * 2;
    const s = new THREE.Sprite(mat);
    const size = opts.size || 0.62;
    s.scale.set(size, size, 1);
    s.position.set(x, opts.y ?? 0.45, z);
    this.scene.add(s);
    this.enemyBullets.push({
      s, vx, vz, life: opts.life || 5.5, shape, spin: opts.spin ?? 1.6,
      r: opts.r ?? size * 0.42, dmg: opts.dmg ?? 11,
    });
    return s;
  }

  _geoShotAngle(from, angle, speed, shape, color, opts = {}) {
    const vx = Math.sin(angle) * speed;
    const vz = -Math.cos(angle) * speed;
    return this._geoShot(from.x, from.z + 0.7, vx, vz, shape, color, opts);
  }

  _enemyShot(from, angle, speed, style = 'bolt') {
    const vx = Math.sin(angle) * speed;
    const vz = -Math.cos(angle) * speed;
    if (style === 'star') {
      this._geoShot(from.x, from.z + 0.6, vx, vz, 'star', 0xff9ad5, { size: 0.66, spin: 2.4, dmg: 11 });
      return;
    }
    if (style === 'heavy') {
      this._geoShot(from.x, from.z + 0.6, vx, vz, 'hex', 0xffb36a, { size: 0.7, spin: 1.1, dmg: 12, r: 0.34 });
      return;
    }
    const s = new THREE.Sprite(this._beamMat(this.mats.enemyBeams, angle));
    s.position.set(from.x, 0.36, from.z + 0.6);
    s.scale.set(0.3, 1.15, 1);
    this.scene.add(s);
    this.enemyBullets.push({ s, vx, vz, life: 4.5, style, spin: 0, r: 0.42, dmg: 11 });
  }

  // ------------------------------------------------------------ boss
  /** Xoá cột cảnh báo chém nếu còn. */
  _disposeSlash(b) {
    const sl = b?.slash;
    if (!sl) return;
    [sl.warn, sl.core].forEach((sp) => {
      if (!sp) return;
      this.scene.remove(sp);
      sp.material.dispose?.();
    });
    if (b.arc) b.arc.material.opacity = 0;
    b.swing = 0;
    b.slash = null;
  }

  _updateBoss(dt) {
    const b = this.boss;
    if (!b) return;
    b.t += dt;
    const xl = this.bounds.x;

    // --- nhập trận: lao vào từ phía xa, dừng lại rung màn hình
    if (b.entering) {
      b.enter = Math.min(1, b.enter + dt / b.enterDur);
      const e = 1 - Math.pow(1 - b.enter, 3);
      b.g.position.z = THREE.MathUtils.lerp(-24, b.zHome, e);
      b.g.position.y = THREE.MathUtils.lerp(5.6, 0.6, e);
      const k = THREE.MathUtils.lerp(0.55, 1, e);
      b.sprite.scale.set(b.size * k, b.size * k, 1);
      b.aura.scale.set(b.size * 1.9 * k, b.size * 1.9 * k, 1);
      b.sprite.material.rotation = (1 - e) * Math.sin(b.t * 4) * 0.08;
      b.core.material.opacity = 0.2 + e * 0.4;
      if (e >= 1) {
        b.entering = false;
        this.shake = Math.max(this.shake, 0.7);
        b.moveT = 0.5;
      }
      return;
    }

    const hpFrac = b.hp / b.maxHp;
    if (b.phase === 1 && hpFrac <= 0.66) {
      // ---- GIAI ĐOẠN 2: nổi giận — đổi màu lõi + hào quang, bắn nhanh hơn
      b.phase = 2;
      b.phase2 = true;
      this.hud.banner('BOSS NỔI GIẬN', true);
      this.shake = 0.9;
      this.sfx.boss();
      b.aura.material.color.set(0xff4d4d);
      b.core.material.color.set(0xff5a6a);
      b.beat = 0.1;
      this._bossBurst(b, 'ring', 0);
    } else if (b.phase === 2 && hpFrac <= 0.33) {
      // ---- GIAI ĐOẠN 3: cuồng nộ — vệ tinh quay gấp, đạn dày, thân rực sáng
      b.phase = 3;
      this.hud.banner('GIAI ĐOẠN CUỐI · CUỒNG NỘ', true);
      this.shake = 1.2;
      this.sfx.boss();
      b.aura.material.color.set(0xff2b8a);
      b.core.material.color.set(0xffd23e);
      b.beat = 0.1;
      this._bossBurst(b, 'ring', 0);
      b.queue.push({ t: 0.35, name: 'ring', arg: 1 });
    }

    b.recoil = Math.max(0, b.recoil - dt * 3.6);
    b.flash = Math.max(0, b.flash - dt * 6);

    // --- nạp đòn: đứng lại, lõi sáng dần rồi bắn (tạo nhịp "lấy đà")
    if (b.action) {
      b.action.t += dt;
      b.charge = Math.min(1, b.action.t / b.action.dur);
      if (b.action.t >= b.action.dur) {
        const act = b.action;
        b.action = null;
        b.charge = 0;
        b.recoil = 1;
        b.flash = 1;
        this._bossBurst(b, act.name, 0);
        for (let i = 1; i < act.count; i++) b.queue.push({ t: i * 0.22, name: act.name, arg: i });
      }
    } else {
      b.charge = Math.max(0, b.charge - dt * 3);
    }

    // hàng đợi nhịp bắn
    for (let i = b.queue.length - 1; i >= 0; i--) {
      const q = b.queue[i];
      q.t -= dt;
      if (q.t <= 0) {
        b.queue.splice(i, 1);
        this._bossBurst(b, q.name, q.arg);
        b.recoil = 1;
        b.flash = 1;
      }
    }

    this._bossParts(b, dt);

    if (b.slash) {
      this._updateBossSlash(b, dt);
      return;
    }

    // --- di chuyển như đang chiến đấu: đổi vị trí, nghiêng theo đà
    b.moveT -= dt;
    if (b.moveT <= 0) {
      b.moveT = (b.phase >= 3 ? 1.1 : b.phase2 ? 1.4 : 2.2) + Math.random() * 1.3;
      const span = xl * (b.phase >= 3 ? 0.92 : b.phase2 ? 0.8 : 0.64);
      b.targetX = (Math.random() * 2 - 1) * span;
      b.targetZ = b.zHome + (Math.random() * 2 - 1) * 1.3 + (Math.random() < 0.32 ? 1.2 : 0);
    }
    const prevX = b.g.position.x;
    b.g.position.x += (b.targetX - b.g.position.x) * Math.min(1, dt * (b.phase >= 3 ? 2.9 : b.phase2 ? 2.3 : 1.6));
    b.heading = (b.g.position.x - prevX) / Math.max(dt, 1e-4);
    b.g.position.z += (b.targetZ - b.g.position.z) * Math.min(1, dt * 1.35);
    let tiltTarget = THREE.MathUtils.clamp(-b.heading * 0.055, -0.14, 0.14);
    // đang nạp đòn thì nghiêng nòng về phía người chơi
    if (b.action && this.player) {
      const aim = THREE.MathUtils.clamp((this.player.group.position.x - b.g.position.x) * 0.022, -0.13, 0.13);
      tiltTarget += aim;
    }
    b.tilt += (tiltTarget - b.tilt) * Math.min(1, dt * 5.5);

    const bob = Math.sin(b.t * (b.phase >= 3 ? 2.6 : b.phase2 ? 2.15 : 1.5)) * (b.phase >= 3 ? 0.32 : b.phase2 ? 0.26 : 0.2);
    b.g.position.y = 0.6 + bob + b.recoil * 0.5;

    // --- thân: thở + nghiêng + giật lùi khi bắn
    const breath = 1 + Math.sin(b.t * 1.8) * 0.016;
    const sx = b.size * breath * (1 + Math.abs(b.tilt) * 0.07);
    const sy = b.size * breath * (1 - Math.abs(b.tilt) * 0.05) * (1 - b.recoil * 0.02);
    b.sprite.scale.set(sx, sy, 1);
    b.sprite.material.rotation = b.tilt + Math.sin(b.t * 0.85) * 0.015;

    // nhịp: mỗi phách là một đợt đạn (không bắn khi đang nạp đòn)
    b.beat -= dt;
    if (b.beat <= 0 && b.queue.length === 0 && !b.action) {
      b.beat = b.phase >= 3 ? 0.62 : b.phase2 ? 0.78 : 1.12;
      this._bossAttack(b);
    }
  }

  /** Lõi, họng súng, kiếm, hào quang, vệ tinh — phần "sống" chạy mọi khung hình. */
  _bossParts(b, dt) {
    const t = b.t;

    // trúng đạn: thân giật nhẹ sang bên, loé trắng rất ngắn
    b.hitT = Math.max(0, (b.hitT || 0) - dt);
    const kick = b.hitT > 0 ? Math.sin(b.hitT * 120) * 0.12 * (b.hitDir || 1) : 0;
    b.sprite.position.x = kick;
    b.sprite.material.color.setRGB(1, 1, 1).lerp(DEPTH_HAZE, 0.1);
    if (b.hitT > 0) b.sprite.material.color.lerp(new THREE.Color(0xffd9d0), b.hitT / 0.11 * 0.35);
    // lõi sáng lên khi nạp đòn, đập theo nhịp tim
    const heat = b.charge;
    const coreScale = b.size * (0.46 + Math.sin(t * 3.2) * 0.02 + heat * 0.4);
    b.core.scale.set(coreScale, coreScale, 1);
    b.core.material.opacity = 0.3 + Math.sin(t * 3.4) * 0.07 + heat * 0.7;
    b.core.material.color.setHex(b.phase >= 3 ? 0xffd23e : b.phase2 ? 0xff5a6a : 0x59e6ff);
    const hotScale = b.size * (0.13 + heat * 0.22 + Math.abs(Math.sin(t * 6)) * 0.015);
    b.coreHot.scale.set(hotScale, hotScale, 1);
    b.coreHot.material.opacity = 0.35 + heat * 0.6;

    // họng súng + quầng kiếm bám theo góc xoay của thân
    const rot = b.sprite.material.rotation || 0;
    const rc = Math.cos(rot);
    const rs = Math.sin(rot);
    const spinPt = (ox, oy, z) => [ox * rc - oy * rs, ox * rs + oy * rc, z];
    const [gx, gy, gz] = spinPt(-0.31 * b.size, -0.22 * b.size, 0.95);
    b.muzzle.position.set(gx, gy, gz);
    const [wx, wy, wz] = spinPt(b.size * 0.31, b.size * 0.02, 0.9);
    b.sword.position.set(wx, wy, wz);

    // họng súng loé rồi tắt
    if (b.flash > 0) {
      b.muzzle.material.opacity = b.flash * 0.95;
      const ms = b.size * (0.24 + b.flash * 0.5);
      b.muzzle.scale.set(ms, ms, 1);
      b.muzzle.material.rotation = t * 11;
    } else if (b.muzzle.material.opacity !== 0) {
      b.muzzle.material.opacity = 0;
    }

    // kiếm phát sáng nhè nhẹ, rực lên khi sắp chém
    b.sword.material.opacity = 0.16 + Math.abs(Math.sin(t * 2.1)) * 0.1 + (b.slash ? 0.35 : 0) + b.charge * 0.2;
    const swScale = b.size * 0.42 * (1 + Math.sin(t * 4.4) * 0.05);
    b.sword.scale.set(swScale, swScale * 1.5, 1);

    // hào quang xoay, mạnh hơn ở pha 2
    b.aura.material.opacity = 0.4 + Math.sin(t * 3.1) * 0.08 + (b.phase >= 3 ? 0.35 : b.phase2 ? 0.2 : 0) + b.charge * 0.15;
    b.aura.material.rotation += dt * (b.phase >= 3 ? 1.4 : b.phase2 ? 0.9 : 0.45);

    // vệ tinh bay vòng và bắn tỉa
    const p = this.player;
    for (const o of b.orbiters) {
      o.ang += dt * o.spin * (b.phase >= 3 ? 2.4 : b.phase2 ? 1.7 : 1);
      const rr = o.r * (1 + Math.sin(t * 2 + o.ang) * 0.06);
      o.s.position.set(Math.cos(o.ang) * rr, Math.sin(o.ang) * rr * 0.55 - b.size * 0.01, 0.5);
      const os = b.size * (0.16 + Math.abs(Math.sin(t * 4 + o.ang)) * 0.05);
      o.s.scale.set(os, os, 1);
      o.fire -= dt;
      if (o.fire <= 0 && !b.slash && !b.entering && p && this.state === 'playing') {
        o.fire = (b.phase >= 3 ? 0.9 : b.phase2 ? 1.25 : 1.9) + Math.random() * 0.7;
        const from = new THREE.Vector3(b.g.position.x + o.s.position.x, 0.7, b.g.position.z + 0.5);
        const ang = Math.atan2(p.group.position.x - from.x, -(p.group.position.z - from.z));
        this._geoShotAngle(from, ang, 9.2, b.def.shapes[1] || b.def.shapes[0], b.color,
          { size: 0.46, spin: 2.4, dmg: 8 });
      }
    }
  }

  _bossAttack(b) {
    const patterns = b.def.patterns;
    const name = patterns[b.patternIndex % patterns.length];
    b.patternIndex += 1;

    if (name === 'slash') {
      this._bossStartSlash(b);
      return;
    }
    // lấy đà rồi bắn: 2–3 đợt nối tiếp theo nhịp
    const count = name === 'ring' || name === 'wall' ? 2 : 3;
    b.action = { name, count, t: 0, dur: b.phase >= 3 ? 0.18 : b.phase2 ? 0.24 : 0.4 };
    this.sfx.enemyShoot?.();
  }

  /** Toạ độ đầu nòng súng máy của boss (đã tính góc xoay thân). */
  _bossMuzzle(b) {
    const rot = b.sprite.material.rotation || 0;
    const ox = -0.31 * b.size;
    const oy = -0.22 * b.size;
    const c = Math.cos(rot);
    const sn = Math.sin(rot);
    return new THREE.Vector3(
      b.g.position.x + ox * c - oy * sn,
      0.85,
      b.g.position.z + 0.9,
    );
  }

  _bossBurst(b, name, arg = 0) {
    const p = this.player;
    if (!p) return;
    // đạn phải bay ra từ họng súng, không phải từ giữa bụng robot
    const from = this._bossMuzzle(b);
    const shapeA = b.def.shapes[0];
    const shapeB = b.def.shapes[1] || shapeA;
    const base = Math.atan2(p.group.position.x - from.x, -(p.group.position.z - from.z));
    const speedMul = b.phase >= 3 ? 1.3 : b.phase2 ? 1.14 : 1;

    if (name === 'fan') {
      const spread = b.phase >= 3 ? 0.5 : b.phase2 ? 0.42 : 0.34;
      const n = b.phase >= 3 ? 9 : b.phase2 ? 7 : 5;
      for (let i = 0; i < n; i++) {
        const a = base + (i / (n - 1) - 0.5) * 2 * spread;
        this._geoShotAngle(from, a, 13.2 * speedMul, shapeA, b.color, { size: 0.68, spin: 2.2, dmg: 12 });
      }
    } else if (name === 'ring') {
      const n = b.phase >= 3 ? 24 : b.phase2 ? 18 : 14;
      const off = arg * 0.22 + (b.phase2 ? b.t * 0.6 : 0);
      for (let i = 0; i < n; i++) {
        this._geoShotAngle(from, off + (i / n) * Math.PI * 2, 9.6 * speedMul, shapeB, b.color, { size: 0.6, spin: -1.8, dmg: 11 });
      }
      this._geoShotAngle(from, base, 12.5 * speedMul, shapeA, 0xfff0c0, { size: 0.86, spin: 3.4, dmg: 13 });
    } else if (name === 'spiral') {
      const arms = 3;
      const a0 = b.t * 2.2 + arg * 0.5;
      for (let i = 0; i < arms; i++) {
        this._geoShotAngle(from, a0 + (i / arms) * Math.PI * 2, 12.4 * speedMul, 'needle', 0x9fe9ff, { size: 0.62, spin: 0, dmg: 11 });
      }
    } else if (name === 'wall') {
      const cols = 9;
      const gap = (arg + Math.floor(Math.random() * 3)) % (cols - 2);
      const step = (this.bounds.x * 1.9) / (cols - 1);
      for (let i = 0; i < cols; i++) {
        if (i === gap || i === gap + 1) continue;
        const x = -this.bounds.x * 0.95 + i * step;
        this._geoShot(x, from.z + 1.2, 0, 10.6 * speedMul, 'square', 0xffb36a, { size: 0.72, spin: 1.4, dmg: 12 });
      }
    } else if (name === 'cross') {
      for (let i = 0; i < 4; i++) {
        this._geoShotAngle(from, base + (i / 4) * Math.PI * 2 + arg * 0.2, 10.2 * speedMul, 'cross', 0xffffff, { size: 0.86, spin: 1.2, dmg: 13 });
      }
    } else if (name === 'summon') {
      for (let i = 0; i < 3; i++) {
        if (this.enemies.length < 14) {
          this._spawnEnemy(i % 2 ? 'skimmer' : 'swarm',
            (i - 1) * this.bounds.x * 0.5, 0.8, { from: 'top' });
        }
      }
      this._geoShotAngle(from, base, 11.5 * speedMul, shapeA, b.color, { size: 0.66, spin: 3, dmg: 11 });
    }
    this.sfx.enemyShoot();
  }

  // ------------------------------------------------------------ boss: chém
  _bossStartSlash(b) {
    const p = this.player;
    if (!p || b.slash) return;
    const x = THREE.MathUtils.clamp(p.group.position.x * 0.85, -this.bounds.x * 0.9, this.bounds.x * 0.9);

    const mk = (sx, sy, op, color) => {
      const sp = new THREE.Sprite(new THREE.SpriteMaterial({
        map: glowTexture(), color, transparent: true, depthWrite: false,
        blending: THREE.AdditiveBlending, opacity: op,
      }));
      sp.position.set(x, 0.5, -4.6);
      sp.scale.set(sx, sy, 1);
      this.scene.add(sp);
      return sp;
    };

    b.slash = {
      t: 0, phase: 'windup', x, dur: b.phase >= 3 ? 0.42 : b.phase2 ? 0.5 : 0.66, struck: false,
      warn: mk(2.6, 15, 0.45, 0xff5535),
      core: mk(0.6, 15, 0.3, 0xfff0c0),
    };
    this.sfx.enemyShoot();
  }

  _updateBossSlash(b, dt) {
    const sl = b.slash;
    if (!sl) return;
    sl.t += dt;

    // lao tới cột mục tiêu
    const lean = THREE.MathUtils.clamp((sl.x - b.g.position.x) * 0.06, -0.18, 0.18);
    b.tilt += (lean - b.tilt) * Math.min(1, dt * 4);
    b.g.position.x += (sl.x - b.g.position.x) * Math.min(1, dt * 6);
    b.g.position.z += (-6.4 - b.g.position.z) * Math.min(1, dt * 4.2);
    b.g.position.y = 0.55 + Math.sin(b.t * 6) * 0.08;

    // ---- vung đao: kéo ra sau rồi bổ tới, kèm vệt mờ
    let swing;
    if (sl.phase === 'windup') {
      const k = Math.min(1, sl.t / sl.dur);
      swing = -0.26 * k;
    } else {
      const k = Math.min(1, sl.t / 0.22);
      const e = 1 - Math.pow(1 - k, 3);
      swing = sl.t < 0.22 ? -0.26 + e * 0.62 : Math.max(0, 0.36 * (1 - (sl.t - 0.22) / 0.3));
    }
    sl.swing = swing;
    b.swing = swing;
    b.sprite.material.rotation = b.tilt + swing;
    const sq = 1 + Math.abs(swing) * 0.16;
    b.sprite.scale.set(b.size * sq, b.size * (1 + Math.abs(swing) * 0.06), 1);

    // cung lửa quét theo đao
    if (b.arc) {
      const windK = Math.min(1, sl.t / sl.dur);
      const strikeK = sl.phase === 'strike' ? Math.min(1, sl.t / 0.34) : 0;
      // quét cung lửa từ sau ra trước (≈120°)
      b.arc.material.rotation = sl.phase === 'windup' ? -0.95 + windK * 0.15 : -0.8 + strikeK * 2.15;
      b.arc.material.opacity = sl.phase === 'windup'
        ? 0.08 + 0.22 * windK
        : Math.max(0, 0.98 - strikeK * 1.05);
      const as = b.size * (2.35 + strikeK * 0.9);
      b.arc.scale.set(as, as, 1);
      b.arc.position.y = -b.size * 0.06;
    }

    // vệt mờ của thân+đao trong lúc bổ
    if (sl.phase === 'strike' && sl.t < 0.3) {
      sl.trail = (sl.trail || 0) - dt;
      if (sl.trail <= 0) {
        sl.trail = 0.03;
        this._bossSwingTrail(b);
      }
    }

    if (sl.phase === 'windup') {
      const k = Math.min(1, sl.t / sl.dur);
      b.charge = k;
      this.shake = Math.max(this.shake, 0.08 + k * 0.22);
      sl.warn.material.opacity = (0.18 + 0.4 * k) * (0.55 + 0.45 * Math.abs(Math.sin(sl.t * 22)));
      sl.warn.scale.x = 2.9 - k * 0.6;
      sl.core.material.opacity = 0.2 + 0.5 * k;
      b.blade.material.opacity = 0.25 + 0.55 * k;
      b.blade.material.rotation = -0.25 + k * 0.5;

      if (k >= 1) {
        sl.phase = 'strike';
        sl.t = 0;
        b.charge = 0;
        b.recoil = 1;
        b.flash = 1;
        sl.warn.material.opacity = 1;
        sl.warn.scale.set(3.6, 16, 1);
        sl.core.material.opacity = 1;
        b.blade.material.opacity = 1;
        this.shake = Math.max(this.shake, 0.7);
        this.sfx.explode(false);

        for (let i = 0; i < 7; i++) {
          this._hitSpark(sl.x + (Math.random() - 0.5) * 1.8, -6.2 + i * 1.5, 1.1);
        }
        const p = this.player;
        if (p && p.invuln <= 0 && Math.abs(p.group.position.x - sl.x) < 1.5 && p.group.position.z > -7.2) {
          this._damagePlayer(26, true);
        }
      }
    } else {
      const k = Math.min(1, sl.t / 0.5);
      sl.warn.material.opacity = (1 - k) * 0.9;
      sl.core.material.opacity = (1 - k) * 0.85;
      b.blade.material.opacity = 1 - k;
      if (k >= 1) {
        [sl.warn, sl.core].forEach((sp) => {
          this.scene.remove(sp);
          sp.material.dispose?.();
        });
        b.slash = null;
        b.blade.material.opacity = 0;
        b.beat = Math.min(b.beat, 0.45);
      }
    }
  }

  /** Bản sao mờ của boss ở góc xoay hiện tại → cảm giác đao chuyển động thật. */
  _bossSwingTrail(b) {
    const map = b.sprite.material.map;
    if (!map) return;
    const mat = new THREE.SpriteMaterial({
      map, transparent: true, depthWrite: false, opacity: 0.3,
      color: 0xffb070, blending: THREE.AdditiveBlending,
    });
    const sp = new THREE.Sprite(mat);
    sp.position.copy(b.g.position);
    sp.position.z -= 0.06;
    sp.scale.copy(b.sprite.scale);
    sp.material.rotation = b.sprite.material.rotation;
    this.scene.add(sp);
    this.trails.push({ s: sp, t: 0, life: 0.2, opacity: 0.34 });
  }

  // ------------------------------------------------------------ bullets
  _updateBullets(dt) {
    const zMax = this.bounds.zMax + 4;
    const zMin = this.bounds.zMin - 6;

    for (let i = this.playerBullets.length - 1; i >= 0; i--) {
      const b = this.playerBullets[i];
      b.s.position.x += b.vx * dt;
      b.s.position.z += b.vz * dt;
      b.life -= dt;
      if (b.life <= 0 || b.s.position.z < zMin || Math.abs(b.s.position.x) > this.bounds.x + 6) {
        this.scene.remove(b.s);
        this.playerBullets.splice(i, 1);
      }
    }

    const p = this.player;
    for (let i = this.enemyBullets.length - 1; i >= 0; i--) {
      const b = this.enemyBullets[i];
      b.s.position.x += b.vx * dt;
      b.s.position.z += b.vz * dt;
      b.life -= dt;
      if (b.spin) b.s.material.rotation += b.spin * dt;
      if (b.s.position.z > zMax || b.s.position.z < zMin || b.life <= 0
        || Math.abs(b.s.position.x) > this.bounds.x + 9) {
        this.scene.remove(b.s);
        b.s.material.dispose?.();
        this.enemyBullets.splice(i, 1);
        continue;
      }
      if (p && p.invuln <= 0) {
        const dx = b.s.position.x - p.group.position.x;
        const dz = b.s.position.z - p.group.position.z;
        const rr = (b.r || 0.42) + 0.5;
        if (dx * dx + dz * dz < rr * rr) {
          this.scene.remove(b.s);
          b.s.material.dispose?.();
          this.enemyBullets.splice(i, 1);
          this._damagePlayer(b.dmg || 11, false);
        }
      }
    }
  }

  // ------------------------------------------------------------ pickups
  _updatePickups(dt) {
    const p = this.player;
    const magnet = (p?.cfg.magnetR || 4.2) * (this.pickupBoost || 1);
    for (let i = this.pickups.length - 1; i >= 0; i--) {
      const it = this.pickups[i];
      it.t += dt;
      it.s.position.z += 2.4 * dt;
      it.s.position.y = 0.55 + Math.sin(it.t * 3) * 0.14;
      it.s.material.rotation += dt * 1.2;

      if (p) {
        const dx = p.group.position.x - it.s.position.x;
        const dz = p.group.position.z - it.s.position.z;
        const d2 = dx * dx + dz * dz;
        if (d2 < magnet * magnet) {
          const k = Math.min(1, dt * 4.5);
          it.s.position.x += dx * k;
          it.s.position.z += dz * k;
        }
        if (d2 < 1.15 * 1.15) {
          this._collect(it.kind);
          this.scene.remove(it.s);
          this.pickups.splice(i, 1);
          continue;
        }
      }

      if (it.s.position.z > this.bounds.zMax + 2 || it.t > 16) {
        this.scene.remove(it.s);
        this.pickups.splice(i, 1);
      }
    }
  }

  _collect(kind) {
    const p = this.player;
    if (!p) return;
    if (kind === 'weapon') {
      p.weapon = Math.min(MAX_WEAPON, p.weapon + 1);
      this.hud.banner('VŨ KHÍ CẤP ' + p.weapon);
    } else if (kind === 'heal') {
      p.hp = Math.min(p.maxHp, p.hp + Math.round(p.maxHp * 0.3));
      this.hud.banner('+' + Math.round(p.maxHp * 0.3) + ' MÁU');
    } else if (kind === 'shield') {
      p.shield = Math.min(p.shieldCap, p.shield + 1);
    } else if (kind === 'coin') {
      this.coinsEarned += 12;
      this.score += 40;
    } else if (kind === 'drone') {
      p.droneBonus = Math.min(3, p.droneBonus + 1);
      this._syncDrones();
      this.hud.banner('+1 DRONE');
    }
    this.sfx.pickup();
  }

  // ------------------------------------------------------------ fx
  _boom(x, z, size = 1.6, big = false) {
    const s = new THREE.Sprite(this.mats.explosion[0]);
    s.position.set(x, 0.55, z);
    s.scale.set(size, size, 1);
    this.scene.add(s);
    this.explosions.push({ s, t: 0, frame: 0, size, big });

    const flash = new THREE.Sprite(this.mats.flash);
    flash.position.set(x, 0.6, z);
    flash.scale.set(size * 1.5, size * 1.5, 1);
    this.scene.add(flash);
    this.sparks.push({ s: flash, t: 0, life: 0.16, size: size * 1.5, grow: 1.6 });

    // sóng xung kích loang ra
    const ring = new THREE.Sprite(this.mats.ring.clone());
    ring.position.set(x, 0.42, z);
    ring.scale.set(size * 0.5, size * 0.5, 1);
    ring.material.opacity = 0.9;
    this.scene.add(ring);
    this.rings.push({ s: ring, t: 0, life: big ? 0.52 : 0.34, size: size * (big ? 3.2 : 2.1) });

    // tia lửa bắn toả
    const embers = big ? 10 : 5;
    for (let i = 0; i < embers && this.shards.length < 40; i++) {
      const a = Math.random() * Math.PI * 2;
      const sp = (big ? 8.5 : 5.5) * (0.45 + Math.random());
      const mat = this.mats.ember.clone();
      const sp2 = new THREE.Sprite(mat);
      sp2.position.set(x, 0.5, z);
      const sc = (big ? 0.5 : 0.32) * (0.7 + Math.random() * 0.7);
      sp2.scale.set(sc, sc, 1);
      this.scene.add(sp2);
      this.shards.push({
        s: sp2, t: 0, life: (big ? 0.62 : 0.42) + Math.random() * 0.3,
        vx: Math.cos(a) * sp, vz: Math.sin(a) * sp, vy: 1.8 + Math.random() * 2.6,
        grav: -11, size: sc, spin: 0, kind: 'spark',
      });
    }

    // mảnh vỡ xoay tít
    const chunks = big ? 5 : 3;
    for (let i = 0; i < chunks && this.shards.length < 50; i++) {
      const a = Math.random() * Math.PI * 2;
      const sp = (big ? 4.6 : 3.0) * (0.4 + Math.random());
      const mat = this.mats.chunk.clone();
      const c = new THREE.Sprite(mat);
      c.position.set(x, 0.4, z);
      const sc = (big ? 0.52 : 0.3) * (0.6 + Math.random() * 0.8);
      c.scale.set(sc, sc, 1);
      this.scene.add(c);
      this.shards.push({
        s: c, t: 0, life: 0.9 + Math.random() * 0.5,
        vx: Math.cos(a) * sp, vz: Math.sin(a) * sp, vy: 2.4 + Math.random() * 2.0,
        grav: -14, size: sc, spin: (Math.random() - 0.5) * 9, kind: 'chunk',
      });
    }

    this.shake = Math.min(1.2, this.shake + (big ? 0.75 : 0.26));
    this.sfx.explode(big);
  }

  _updateEffects(dt) {
    for (let i = this.explosions.length - 1; i >= 0; i--) {
      const e = this.explosions[i];
      e.t += dt;
      const frame = Math.floor(e.t / 0.055);
      if (frame > 8) {
        this.scene.remove(e.s);
        this.explosions.splice(i, 1);
        continue;
      }
      e.s.material = this.mats.explosion[frame];
      const grow = e.size * (1 + e.t * 0.9);
      e.s.scale.set(grow, grow, 1);
    }

    for (let i = this.rings.length - 1; i >= 0; i--) {
      const r = this.rings[i];
      r.t += dt;
      const k = r.t / r.life;
      if (k >= 1) {
        this.scene.remove(r.s);
        this.rings.splice(i, 1);
        continue;
      }
      const e = 1 - Math.pow(1 - k, 3);
      const sc = r.size * (0.22 + e * 0.95);
      r.s.scale.set(sc, sc, 1);
      r.s.material.opacity = Math.pow(1 - k, 1.5) * 0.95;
    }

    for (let i = this.shards.length - 1; i >= 0; i--) {
      const sh = this.shards[i];
      sh.t += dt;
      const k = sh.t / sh.life;
      if (k >= 1) {
        this.scene.remove(sh.s);
        this.shards.splice(i, 1);
        continue;
      }
      sh.vy += sh.grav * dt;
      sh.s.position.x += sh.vx * dt;
      sh.s.position.z += sh.vz * dt;
      sh.s.position.y += sh.vy * dt;
      if (sh.s.position.y < 0.06) { sh.s.position.y = 0.06; sh.vy *= -0.34; sh.vx *= 0.62; sh.vz *= 0.62; }
      sh.vx *= 1 - dt * 1.1;
      sh.vz *= 1 - dt * 1.1;
      sh.s.material.opacity = 1 - k;
      if (sh.kind === 'chunk') sh.s.material.rotation += sh.spin * dt;
      const sc = sh.size * (1 + k * 0.35);
      sh.s.scale.set(sc, sc, 1);
    }

    for (let i = this.trails.length - 1; i >= 0; i--) {
      const tr = this.trails[i];
      tr.t += dt;
      const k = tr.t / tr.life;
      if (k >= 1) {
        this.scene.remove(tr.s);
        tr.s.material.dispose?.();
        this.trails.splice(i, 1);
        continue;
      }
      tr.s.material.opacity = (1 - k) * tr.opacity;
    }

    for (let i = this.sparks.length - 1; i >= 0; i--) {
      const sp = this.sparks[i];
      sp.t += dt;
      const k = sp.t / sp.life;
      if (k >= 1) {
        this.scene.remove(sp.s);
        this.sparks.splice(i, 1);
        continue;
      }
      const s = sp.size * (1 + k * sp.grow);
      sp.s.scale.set(s, s, 1);
      const idx = Math.min(7, Math.floor(k * 8));
      if (sp.s.material !== this.mats.spark[idx]) sp.s.material = this.mats.spark[idx];
    }
  }

  // ------------------------------------------------------------ combat
  _collide() {
    for (let i = this.playerBullets.length - 1; i >= 0; i--) {
      const b = this.playerBullets[i];
      let hit = false;

      for (let j = this.enemies.length - 1; j >= 0; j--) {
        const e = this.enemies[j];
        const dx = b.s.position.x - e.g.position.x;
        const dz = b.s.position.z - e.g.position.z;
        if (dx * dx + dz * dz < (e.radius + 0.3) ** 2) {
          e.hp -= b.dmg;
          this._hitSpark(b.s.position.x, b.s.position.z, 0.55);
          this.sfx.hit();
          if (e.hp <= 0) this._killEnemy(j);
          if (b.pierce > 0) b.pierce -= 1;
          else hit = true;
          break;
        }
      }

      if (!hit && this.boss) {
        const dx = b.s.position.x - this.boss.g.position.x;
        const dz = b.s.position.z - this.boss.g.position.z;
        if (dx * dx + dz * dz < (this.boss.radius + 0.3) ** 2) {
          this.boss.hp -= b.dmg;
          // phản ứng khi trúng đạn: rung + loé nhẹ
          this.boss.hitT = 0.11;
          this.boss.hitDir = Math.sign(dx) || 1;
          this._hitSpark(b.s.position.x, b.s.position.z, 0.5);
          this.sfx.hit();
          if (this.boss.hp <= 0) this._killBoss();
          hit = true;
        }
      }

      if (hit) {
        this.scene.remove(b.s);
        this.playerBullets.splice(i, 1);
      }
    }

    // va chạm tàu địch với drone
    const p = this.player;
    if (!p) return;
    for (const d of this.drones) {
      for (let j = this.enemies.length - 1; j >= 0; j--) {
        const e = this.enemies[j];
        const dx = d.g.position.x - e.g.position.x;
        const dz = d.g.position.z - e.g.position.z;
        if (dx * dx + dz * dz < (e.radius + 0.35) ** 2) {
          e.hp -= p.cfg.dmg * 0.6;
          this._hitSpark(e.g.position.x, e.g.position.z, 0.6);
          if (e.hp <= 0) this._killEnemy(j);
          break;
        }
      }
    }
  }

  _hitSpark(x, z, size) {
    const s = new THREE.Sprite(this.mats.spark[2]);
    s.position.set(x, 0.4, z);
    s.scale.set(size, size, 1);
    this.scene.add(s);
    this.sparks.push({ s, t: 0, life: 0.16, size, grow: 1.2 });
  }

  _killEnemy(index) {
    const e = this.enemies[index];
    if (!e) return;
    const { x, z } = e.g.position;
    this.scene.remove(e.g);
    this.enemies.splice(index, 1);

    this._boom(x, z, e.kind === 'tank' || e.kind === 'bomber' ? 2.8 : 1.5, e.kind === 'tank' || e.kind === 'bomber');
    this.score += Math.round(e.score * this.combo);
    this.coinsEarned += e.coins || 1;
    this.kills += 1;
    this.combo = Math.min(5, this.combo + 1);
    this.comboTimer = 2.2;

    const roll = Math.random();
    if (roll < 0.08) this._dropPickup(x, z, 'weapon');
    else if (roll < 0.13) this._dropPickup(x, z, 'heal');
    else if (roll < 0.16) this._dropPickup(x, z, 'shield');
    else if (roll < 0.24) this._dropPickup(x, z, 'coin');
    else if (roll < 0.255) this._dropPickup(x, z, 'drone');
  }

  _killBoss() {
    const b = this.boss;
    if (!b) return;
    this._disposeSlash(b);
    const { x, z } = b.g.position;
    // xoá khỏi danh sách chiến đấu ngay (không bắn/không va chạm nữa)
    this.boss = null;
    this.bossesKilled = (this.bossesKilled || 0) + 1;
    // ... nhưng thân máy vẫn nổ tung dần trên màn hình
    this.bossDeath = {
      g: b.g, sprite: b.sprite, aura: b.aura, core: b.core, coreHot: b.coreHot,
      sword: b.sword, orbiters: b.orbiters, size: b.size,
      x, z, t: 0, dur: b.phase >= 3 ? 2.0 : b.phase2 ? 1.7 : 1.4, spawned: 0,
    };
    this.shake = Math.max(this.shake, 1.15);
    this.score += 4000 + this.wave * 250;
    this.coinsEarned += 90;
    this.kills += 1;
    this.hud.banner('BOSS ĐÃ BỊ HẠ');
    this._dropPickup(x, z, 'weapon');
    this._dropPickup(x + 1.2, z, 'heal');
    this._dropPickup(x - 1.2, z, 'coin');
    this._dropPickup(x + 2.2, z, 'coin');

    if (this.mode === 'campaign' && this.level?.isBoss) {
      setTimeout(() => this._completeLevel(), 700);
    }
  }

  /** Cảnh boss tan rã: thân xoay trôi, nổ từng mảng, cuối cùng là một cú lớn. */
  _updateBossDeath(dt) {
    const d = this.bossDeath;
    if (!d) return;
    d.t += dt;
    const k = Math.min(1, d.t / d.dur);

    d.sprite.material.rotation += dt * (0.5 + k * 1.8);
    d.sprite.material.color.setRGB(1, 1 - k * 0.75, 1 - k * 0.9);
    d.g.position.y += dt * 0.45 * k;
    d.g.position.z -= dt * 0.7;
    d.aura.material.opacity = 0.45 * (1 - k);
    d.core.material.opacity = (0.5 + Math.abs(Math.sin(d.t * 26)) * 0.5) * (1 - k * 0.8);
    d.core.scale.multiplyScalar(1 + dt * 0.8);
    if (d.sword) d.sword.material.opacity = 0.25 * (1 - k);

    for (const o of d.orbiters || []) {
      o.ang += dt * 4.5;
      o.s.position.set(Math.cos(o.ang) * d.size * 0.95, Math.sin(o.ang * 1.7) * d.size * 0.4, 0.6);
      o.s.material.opacity = 0.85 * (1 - k);
    }

    // nổ lần lượt khắp thân máy
    const steps = 9;
    while (d.spawned < steps && d.t > (d.spawned + 0.5) * (d.dur / steps)) {
      d.spawned += 1;
      const dx = (Math.random() - 0.5) * d.size * 0.85;
      const dz = (Math.random() - 0.5) * d.size * 0.35;
      this._boom(d.x + dx, d.z + dz, 1.5 + Math.random() * 1.3, d.spawned % 3 === 0);
      this.shake = Math.max(this.shake, 0.35);
    }

    if (k >= 1) {
      this._boom(d.x, d.z, 4.4, true);
      this.scene.remove(d.g);
      this.bossDeath = null;
      this.shake = Math.max(this.shake, 0.85);
    }
  }

  _dropPickup(x, z, kind) {
    const mat = this.mats.pickup[kind].clone();
    const s = new THREE.Sprite(mat);
    s.position.set(x, 0.55, z);
    s.scale.set(1.1, 1.1, 1);
    this.scene.add(s);
    this.pickups.push({ s, kind, t: 0 });
  }

  _damagePlayer(amount, collision) {
    const p = this.player;
    if (!p || this.state !== 'playing') return;
    if (p.invuln > 0) return;

    if (p.shield > 0) {
      p.shield -= 1;
      p.shieldCd = 0;
      p.invuln = 1.0;
      this.sfx.hit();
      this.hud.damageFlash();
      this.shake = Math.max(this.shake, 0.35);
      return;
    }

    p.hp -= amount;
    p.invuln = 1.25;
    p.hitT = 0.22;
    this.sfx.damage();
    this.hud.damageFlash();
    this.shake = Math.max(this.shake, collision ? 0.85 : 0.5);

    if (p.hp <= 0) {
      p.hp = 0;
      this._boom(p.group.position.x, p.group.position.z, 3.2, true);
      p.group.visible = false;
      this.gameOver(false);
    }
  }

  // ------------------------------------------------------------ camera
  _updateCamera(dt) {
    const cam = this.camera;
    if (this.shake > 0.001) {
      this.shake = Math.max(0, this.shake - dt * 1.8);
      const s = this.shake * 0.5;
      cam.position.set(
        this.cameraBase.x + (Math.random() - 0.5) * s,
        this.cameraBase.y + (Math.random() - 0.5) * s,
        this.cameraBase.z + (Math.random() - 0.5) * s * 0.6,
      );
    } else {
      cam.position.copy(this.cameraBase);
    }
    cam.lookAt(this.cameraTarget);
  }
}
