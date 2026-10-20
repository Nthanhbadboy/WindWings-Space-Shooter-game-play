import * as THREE from 'three';
import { SHIP_ART, ENEMY_ART, BOSS_ART, BACKDROP_ART } from './art.js';

/** Ghép đường dẫn asset trong assets_samples/ (Vite đang serve thư mục đó làm public). */
const BASE = (import.meta.env && import.meta.env.BASE_URL) || '/';
export const url = (path) => BASE + path.split('/').map(encodeURIComponent).join('/');

const TEX = {
  dot: '03_ui/kenney_ui_scifi/dotWhite.png',
  laserP: '01_2d_sprites/kenney_space_shooter_remastered/Lasers/laserBlue01.png',
  laserE: '01_2d_sprites/kenney_space_shooter_remastered/Lasers/laserRed01.png',
  laserG: '01_2d_sprites/kenney_space_shooter_remastered/Lasers/laserGreen01.png',
  laserPStar: '01_2d_sprites/kenney_space_shooter_remastered/Lasers/laserBlue08.png',
  laserPHeavy: '01_2d_sprites/kenney_space_shooter_remastered/Lasers/laserBlue13.png',
  spark: '02_fx/kenney_light_masks/circle_rings_a.png',
  engine: '02_fx/kenney_particles/flame_05.png',
  pickupWeapon: '01_2d_sprites/kenney_space_shooter_remastered/Power-ups/powerupBlue_star.png',
  pickupHeal: '01_2d_sprites/kenney_space_shooter_remastered/Power-ups/powerupGreen_shield.png',
  pickupShield: '01_2d_sprites/kenney_space_shooter_remastered/Power-ups/pill_blue.png',
  pickupCoin: '01_2d_sprites/kenney_space_shooter_remastered/Power-ups/powerupYellow_bolt.png',
  pickupDrone: '01_2d_sprites/kenney_space_shooter_remastered/Power-ups/powerupBlue_bolt.png',
};

export async function loadAssets(onProgress = () => {}) {
  const manager = new THREE.LoadingManager();
  const texLoader = new THREE.TextureLoader(manager);
  const jobs = [];
  const textures = {};
  const models = { ships: {}, enemies: {}, hulls: {}, boss: {} };

  const addTex = (key, path, srgb = true) => {
    jobs.push(async () => {
      const t = await texLoader.loadAsync(url(path));
      if (srgb) t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = 4;
      textures[key] = t;
    });
  };

  /** Ảnh đã được Vite đóng gói sẵn (URL tuyệt đối) — không ghép BASE. */
  const addTexAbs = (bucket, key, src) => {
    jobs.push(async () => {
      const t = await texLoader.loadAsync(src);
      t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = 4;
      bucket[key] = t;
    });
  };

  Object.entries(TEX).forEach(([k, v]) => addTex(k, v));

  // sprite vẽ tay dùng trong màn chơi
  textures.shipArt = {};
  textures.enemyArt = {};
  textures.bossArt = {};
  Object.entries(SHIP_ART).forEach(([id, src]) => addTexAbs(textures.shipArt, id, src));
  Object.entries(ENEMY_ART).forEach(([id, src]) => addTexAbs(textures.enemyArt, id, src));
  Object.entries(BOSS_ART).forEach(([id, src]) => addTexAbs(textures.bossArt, id, src));

  // nền — ảnh thật (xem art.js → BACKDROP_ART): L0 đứng yên + L1 sương và ba đám tinh vân trôi
  addTexAbs(textures, 'sky', BACKDROP_ART.sky);
  addTexAbs(textures, 'nebulaA', BACKDROP_ART.nebulaA);
  addTexAbs(textures, 'nebulaB', BACKDROP_ART.nebulaB);
  addTexAbs(textures, 'nebulaC', BACKDROP_ART.nebulaC);
  addTexAbs(textures, 'nebulaHaze', BACKDROP_ART.nebulaHaze);

  // 9 frame nổ
  textures.explosion = [];
  for (let i = 0; i < 9; i++) {
    jobs.push(async () => {
      const t = await texLoader.loadAsync(url(
        `02_fx/kenney_explosions/Regular explosion/regularExplosion0${i}.png`));
      t.colorSpace = THREE.SRGBColorSpace;
      textures.explosion[i] = t;
    });
  }

  // Toàn bộ tàu / địch / boss giờ là sprite vẽ tay → KHÔNG nạp GLB nữa.
  // (giữ object rỗng cho code cũ và cho test)
  let done = 0;
  await Promise.all(jobs.map((job) => job().then(() => {
    done += 1;
    onProgress(done / jobs.length);
  })));

  return { textures, models, manager };
}

function cap(id) {
  return id.charAt(0).toUpperCase() + id.slice(1);
}

/**
 * Toàn bộ cảnh chơi giờ vẽ bằng sprite + shader riêng, không còn model PBR,
 * nên bỏ skybox/PMREM: nền do `backdrop.js` lo (xem docs/gameplay-redesign.md).
 */
export function buildEnvironment(_renderer, scene) {
  scene.background = null;
  scene.environment = null;
}
