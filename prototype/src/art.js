/**
 * Đường dẫn ảnh dùng trong UI và trong màn chơi.
 * Mỗi `new URL('...', import.meta.url)` phải là **chuỗi tĩnh** thì Vite mới
 * đóng gói ảnh vào bản build (GitHub Pages) — đừng đổi thành hàm ghép chuỗi.
 */

/** Chân dung tàu (ô roster, hangar) */
export const SHIP_PORTRAIT = {
  striker: new URL('./art/striker.jpg', import.meta.url).href,
  zenith: new URL('./art/zenith.jpg', import.meta.url).href,
  challenger: new URL('./art/challenger.jpg', import.meta.url).href,
  spitfire: new URL('./art/spitfire.jpg', import.meta.url).href,
  insurgent: new URL('./art/insurgent.jpg', import.meta.url).href,
  executioner: new URL('./art/executioner.jpg', import.meta.url).href,
  omen: new URL('./art/omen.jpg', import.meta.url).href,
  dispatcher: new URL('./art/dispatcher.jpg', import.meta.url).href,
};
/** Chân dung trong khung cửa sổ tròn */
export const SHIP_PORTHOLE = {
  striker: new URL('./art/porthole_striker.jpg', import.meta.url).href,
  zenith: new URL('./art/porthole_zenith.jpg', import.meta.url).href,
  challenger: new URL('./art/porthole_challenger.jpg', import.meta.url).href,
  spitfire: new URL('./art/porthole_spitfire.jpg', import.meta.url).href,
  insurgent: new URL('./art/porthole_insurgent.jpg', import.meta.url).href,
  executioner: new URL('./art/porthole_executioner.jpg', import.meta.url).href,
  omen: new URL('./art/porthole_omen.jpg', import.meta.url).href,
  dispatcher: new URL('./art/porthole_dispatcher.jpg', import.meta.url).href,
};
/** Tàu nhìn từ trên xuống — dùng trong màn chơi */
export const SHIP_ART = {
  striker: new URL('./art/game/striker.png', import.meta.url).href,
  zenith: new URL('./art/game/zenith.png', import.meta.url).href,
  challenger: new URL('./art/game/challenger.png', import.meta.url).href,
  spitfire: new URL('./art/game/spitfire.png', import.meta.url).href,
  insurgent: new URL('./art/game/insurgent.png', import.meta.url).href,
  executioner: new URL('./art/game/executioner.png', import.meta.url).href,
  omen: new URL('./art/game/omen.png', import.meta.url).href,
  dispatcher: new URL('./art/game/dispatcher.png', import.meta.url).href,
};
/** Địch vẽ tay */
export const ENEMY_ART = {
  wasp: new URL('./art/game/enemy_wasp.png', import.meta.url).href,
  hornet: new URL('./art/game/enemy_hornet.png', import.meta.url).href,
  meteor: new URL('./art/game/meteor.png', import.meta.url).href,
};
/** Icon nâng cấp vẽ tay (medallion tròn, phong cách hoạt hình) */
export const TECH_ART = {
  cannon: new URL('./icons/art/tech_cannon.png', import.meta.url).href,
  armor: new URL('./icons/art/tech_armor.png', import.meta.url).href,
  shield: new URL('./icons/art/tech_shield.png', import.meta.url).href,
  drone: new URL('./icons/art/tech_drone.png', import.meta.url).href,
  magnet: new URL('./icons/art/tech_magnet.png', import.meta.url).href,
};
/** Icon UI */
export const ICONS = {
  armor: new URL('./icons/ic_armor.png', import.meta.url).href,
  cannon: new URL('./icons/ic_cannon.png', import.meta.url).href,
  check: new URL('./icons/ic_check.png', import.meta.url).href,
  clock: new URL('./icons/ic_clock.png', import.meta.url).href,
  coin: new URL('./icons/ic_coin.png', import.meta.url).href,
  crown: new URL('./icons/ic_crown.png', import.meta.url).href,
  drone: new URL('./icons/ic_drone.png', import.meta.url).href,
  flask: new URL('./icons/ic_flask.png', import.meta.url).href,
  gear: new URL('./icons/ic_gear.png', import.meta.url).href,
  gem: new URL('./icons/ic_gem.png', import.meta.url).href,
  gift: new URL('./icons/ic_gift.png', import.meta.url).href,
  globe: new URL('./icons/ic_globe.png', import.meta.url).href,
  info: new URL('./icons/ic_info.png', import.meta.url).href,
  install: new URL('./icons/ic_install.png', import.meta.url).href,
  lock: new URL('./icons/ic_lock.png', import.meta.url).href,
  magnet: new URL('./icons/ic_magnet.png', import.meta.url).href,
  map: new URL('./icons/ic_map.png', import.meta.url).href,
  music: new URL('./icons/ic_music.png', import.meta.url).href,
  pause: new URL('./icons/ic_pause.png', import.meta.url).href,
  pilot: new URL('./icons/ic_pilot.png', import.meta.url).href,
  plus: new URL('./icons/ic_plus.png', import.meta.url).href,
  shield: new URL('./icons/ic_shield.png', import.meta.url).href,
  skull: new URL('./icons/ic_skull.png', import.meta.url).href,
  sound: new URL('./icons/ic_sound.png', import.meta.url).href,
  speed: new URL('./icons/ic_speed.png', import.meta.url).href,
  star: new URL('./icons/ic_star.png', import.meta.url).href,
  trash: new URL('./icons/ic_trash.png', import.meta.url).href,
};
/** Boss: robot vẽ tay (nhìn từ trên xuống). */
export const BOSS_ART = {
  imperial: new URL('./art/game/boss_imperial.png', import.meta.url).href,
  pancake: new URL('./art/game/boss_pancake.png', import.meta.url).href,
  dreadnought: new URL('./art/game/boss_dreadnought.png', import.meta.url).href,
};

/**
 * Lớp nền — ẢNH THẬT, không vẽ lại (xem docs/nen-nhieu-lop.md):
 *   sky     : Hubble Ultra Deep Field 2560² (NASA/ESA, phạm vi công cộng)
 *             → lớp xa nhất, ĐỨNG YÊN TUYỆT ĐỐI
 *   nebulaA : Tarantula Nebula (30 Doradus) — teal/amber, 2560×2016
 *   nebulaB : Tarantula Nebula — vùng xanh tím, 1760×1188
 *   nebulaC : Carina "Mystic Mountain" (Hubble) — 1100×1650
 *   nebulaHaze : tinh vân xanh/lam làm mờ 22 px — sương màu phủ toàn khung
 *             → lớp thứ 2: sương + ba đám mây THẬT trôi 0,007–0,014 màn/giây; mép đã nướng
 *               vignette nên tan vào nền, không thấy khung ảnh
 *
 * Không còn Trái Đất: D20 bỏ hẳn, đã xoá cả file. Không còn mây vẽ tay trong cảnh 3D.
 */
export const BACKDROP_ART = {
  sky: new URL('./ui/sky_deep.jpg', import.meta.url).href,
  nebulaA: new URL('./ui/nebula_a.jpg', import.meta.url).href,
  nebulaB: new URL('./ui/nebula_b.jpg', import.meta.url).href,
  nebulaC: new URL('./ui/nebula_c.jpg', import.meta.url).href,
  nebulaHaze: new URL('./ui/nebula_haze.jpg', import.meta.url).href,
};
