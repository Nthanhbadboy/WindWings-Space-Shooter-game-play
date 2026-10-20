/**
 * Nội dung game: chương, màn, chế độ chơi, modifier.
 * Tất cả số liệu cân bằng nằm ở đây để dễ chỉnh.
 */

export const CHAPTERS = [
  {
    id: 1,
    name: 'VÀNH ĐAI SAO MỘC',
    sub: 'Tàn dư hạm đội Đỏ',
    levels: 10,
    theme: { sky: 'sky', nebula: [0x6a3fd0, 0x1f6fa8], starColor: 0xcfe9ff, fog: 0.85 },
    boss: 'imperial',
    enemyPool: ['swarm', 'drone', 'gunner', 'raider'],
    tint: '#59d8ff',
  },
  {
    id: 2,
    name: 'TINH VÂN XANH',
    sub: 'Bầy ký sinh tinh vân',
    levels: 10,
    theme: { sky: 'skyNight', nebula: [0x2fc6a0, 0x2a4bd8], starColor: 0xbfe8ff, fog: 0.6 },
    boss: 'pancake',
    enemyPool: ['swarm', 'drone', 'interceptor', 'bomber'],
    tint: '#5dffa8',
  },
  {
    id: 3,
    name: 'VÙNG TỐI',
    sub: 'Hạm đội bóng đêm',
    levels: 10,
    theme: { sky: 'skyAlien', nebula: [0xff4d6d, 0x6a3fd0], starColor: 0xffd8c2, fog: 0.45 },
    boss: 'dreadnought',
    enemyPool: ['gunner', 'tank', 'bomber', 'drone'],
    tint: '#ff8f6a',
  },
  {
    id: 4,
    name: 'BIỂN TIỂU HÀNH TINH',
    sub: 'Hạm đội Đỏ tái hợp',
    levels: 10,
    theme: { sky: 'sky', nebula: [0xffa64d, 0x8c2f1f], starColor: 0xffe6c2, fog: 0.7 },
    boss: 'imperial',
    enemyPool: ['raider', 'swarm', 'tank', 'interceptor'],
    tint: '#ffc46a',
  },
  {
    id: 5,
    name: 'LÒ PHẢN VẬT CHẤT',
    sub: 'Bầy ký sinh tiến hoá',
    levels: 10,
    theme: { sky: 'skyNight', nebula: [0x4de1ff, 0x1b3fa0], starColor: 0xd8f4ff, fog: 0.5 },
    boss: 'pancake',
    enemyPool: ['interceptor', 'gunner', 'bomber', 'drone'],
    tint: '#7fe0ff',
  },
  {
    id: 6,
    name: 'TRÁI TIM HẠM ĐỘI',
    sub: 'Tổng hành dinh bóng đêm',
    levels: 10,
    theme: { sky: 'skyAlien', nebula: [0xd02aff, 0x2a0a4d], starColor: 0xf4d8ff, fog: 0.35 },
    boss: 'dreadnought',
    enemyPool: ['tank', 'gunner', 'bomber', 'raider'],
    tint: '#d68aff',
  },
];

export const TOTAL_LEVELS = CHAPTERS.reduce((n, c) => n + c.levels, 0);

export const MODES = [
  {
    id: 'campaign',
    name: 'CHIẾN DỊCH',
    desc: '60 màn qua 6 chương, mỗi chương có boss riêng',
    icon: '🗺',
    unlocked: true,
  },
  {
    id: 'endless',
    name: 'VÔ TẬN',
    desc: 'Sinh tồn càng lâu càng nhiều điểm, đội hình ngẫu nhiên',
    icon: '∞',
    unlocked: true,
  },
  {
    id: 'bossrush',
    name: 'SĂN BOSS',
    desc: 'Chuỗi boss liên tiếp, không có màn thường',
    icon: '☠',
    unlocked: true,
  },
  {
    id: 'daily',
    name: 'THỬ THÁCH NGÀY',
    desc: 'Mỗi ngày một bộ quy tắc khác nhau, thưởng vàng gấp đôi',
    icon: '★',
    unlocked: true,
  },
];

/** Level trong chương: màn cuối là boss. */
export function levelInfo(chapter, index) {
  const ch = CHAPTERS.find((c) => c.id === chapter) || CHAPTERS[0];
  const isBoss = index >= ch.levels;
  const difficulty = 1 + (chapter - 1) * 0.42 + (index - 1) * 0.075;
  return {
    chapter: ch.id,
    index,
    isBoss,
    name: isBoss ? `BOSS · ${ch.name}` : `${ch.name} · ${index}`,
    objective: isBoss ? 'boss' : index % 4 === 0 ? 'survive' : 'clear',
    surviveTime: 34 + chapter * 4,
    difficulty,
    reward: Math.round((70 + index * 26 + chapter * 55) * (isBoss ? 2.4 : 1)),
    theme: ch.theme,
    enemyPool: ch.enemyPool,
    boss: ch.boss,
  };
}

export const DAILY_MODIFIERS = [
  {
    id: 'glass', name: 'GIÁP GIẤY', desc: 'Sát thương ×1.8 nhưng máu chỉ còn 55%',
    player: { dmgMul: 1.8, hpMul: 0.55 },
    scoreMul: 1.3,
  },
  {
    id: 'rush', name: 'ĐẠN NHANH', desc: 'Đạn địch nhanh hơn 35%, đổi lại +30% điểm',
    enemy: { bulletSpeed: 1.35 },
    scoreMul: 1.3,
  },
  {
    id: 'swarm', name: 'BẦY ĐÀN', desc: 'Địch đông gấp rưỡi nhưng yếu hơn',
    spawn: { countMul: 1.5, hpMul: 0.72, scoreMul: 1.15 },
    scoreMul: 1.2,
  },
  {
    id: 'tank', name: 'THÉP DÀY', desc: 'Địch trâu gấp đôi, +60% điểm',
    enemy: { hpMul: 2 },
    scoreMul: 1.6,
  },
  {
    id: 'fog', name: 'SƯƠNG MÙ', desc: 'Tầm nhìn giảm, +25% điểm',
    world: { fog: true },
    scoreMul: 1.25,
  },
  {
    id: 'sniper', name: 'XẠ THỦ', desc: 'Chỉ địch bắn tỉa, đạn nhanh, +45% điểm',
    pool: ['gunner', 'tank'],
    scoreMul: 1.45,
  },
];

/** Chọn modifier theo ngày (giờ máy người chơi) — ổn định cả ngày. */
export function dailySetup(date = new Date()) {
  const seed = Number(`${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}`);
  const mod = DAILY_MODIFIERS[seed % DAILY_MODIFIERS.length];
  const chapter = CHAPTERS[(seed + 1) % CHAPTERS.length];
  return {
    id: 'daily',
    date: `${String(date.getDate()).padStart(2, '0')}/${String(date.getMonth() + 1).padStart(2, '0')}/${date.getFullYear()}`,
    seed,
    modifier: mod,
    theme: chapter.theme,
    enemyPool: mod.pool || chapter.enemyPool,
    difficulty: 1.15 + (seed % 7) * 0.07,
  };
}

/** Bảng đội hình dùng chung cho chế độ vô tận / boss rush. */
export const FORMATIONS = ['line', 'vee', 'snipers', 'tanks', 'mixed', 'ring'];
