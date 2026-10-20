/**
 * Định nghĩa 8 tàu người chơi (model Quaternius CC0).
 * `yaw` = hướng cần xoay để mũi tàu chỉ về -Z (lên trên màn hình).
 * Đã kiểm tra bằng hình học: mũi là đầu hẹp của tiết diện dọc trục Z.
 */

export const PLAYER_SHIPS = [
  {
    id: 'striker', name: 'STRIKER', role: 'Cân bằng', price: 0, yaw: 0,
    base: { hp: 100, speed: 11.5, fireRate: 0.135, dmg: 12 },
    perk: { text: '+10% vàng nhận được', coins: 0.1 },
    ui: { hp: 62, speed: 62, dps: 62 },
  },
  {
    id: 'zenith', name: 'ZENITH', role: 'Trinh sát nhanh', price: 1200, yaw: Math.PI,
    base: { hp: 82, speed: 14.8, fireRate: 0.105, dmg: 10 },
    perk: { text: 'Khiên hồi nhanh gấp đôi', shieldRegen: 2 },
    ui: { hp: 42, speed: 96, dps: 70 },
  },
  {
    id: 'challenger', name: 'CHALLENGER', role: 'Thiết giáp', price: 2000, yaw: Math.PI,
    base: { hp: 150, speed: 8.8, fireRate: 0.19, dmg: 18 },
    perk: { text: '+1 khiên tối đa', shieldMax: 1 },
    ui: { hp: 96, speed: 40, dps: 88 },
  },
  {
    id: 'spitfire', name: 'SPITFIRE', role: 'Hỏa lực mạnh', price: 3200, yaw: Math.PI,
    base: { hp: 108, speed: 10.6, fireRate: 0.125, dmg: 15 },
    perk: { text: 'Bắt đầu với vũ khí cấp 2', weaponStart: 1 },
    ui: { hp: 66, speed: 58, dps: 90 },
  },
  {
    id: 'insurgent', name: 'INSURGENT', role: 'Cơ động', price: 4500, yaw: Math.PI,
    base: { hp: 96, speed: 13.4, fireRate: 0.112, dmg: 13 },
    perk: { text: 'Nhặt vật phẩm xa hơn 60%', magnet: 0.6 },
    ui: { hp: 52, speed: 88, dps: 78 },
  },
  {
    id: 'executioner', name: 'EXECUTIONER', role: 'Oanh tạc', price: 6000, yaw: Math.PI,
    base: { hp: 132, speed: 9.4, fireRate: 0.165, dmg: 21 },
    perk: { text: 'Đạn xuyên 1 mục tiêu', pierce: 1 },
    ui: { hp: 84, speed: 46, dps: 100 },
  },
  {
    id: 'omen', name: 'OMEN', role: 'Chiến đấu cơ hạng nặng', price: 8000, yaw: Math.PI,
    base: { hp: 124, speed: 12.2, fireRate: 0.108, dmg: 16 },
    perk: { text: '+1 drone hộ vệ', droneBonus: 1 },
    ui: { hp: 78, speed: 76, dps: 96 },
  },
  {
    id: 'dispatcher', name: 'DISPATCHER', role: 'Soái hạm mini', price: 10000, yaw: Math.PI,
    base: { hp: 142, speed: 10.2, fireRate: 0.13, dmg: 14 },
    perk: { text: '+2 drone hộ vệ', droneBonus: 2 },
    ui: { hp: 88, speed: 54, dps: 84 },
  },
];

export const SHIP_BY_ID = Object.fromEntries(PLAYER_SHIPS.map((s) => [s.id, s]));

export const SHIP_MAX_LEVEL = 15;

/** Cấp tàu: +5% máu & sát thương, +2% tốc độ mỗi cấp. */
export function shipLevelMultipliers(level = 1) {
  const n = Math.max(0, Math.min(SHIP_MAX_LEVEL, level) - 1);
  return { hp: 1 + 0.05 * n, dmg: 1 + 0.05 * n, speed: 1 + 0.02 * n };
}
