// =====================================================================
// CONFIG — every gameplay constant lives here (no magic numbers in code).
// Vertical shmup (WindWings-style) spec: waves, power-ups, bomb, 3-phase boss.
// =====================================================================
export const CONFIG = {
  screen: {
    width: 720,
    height: 1280,
    maxDelta: 0.05,        // clamp frame delta (s) vs lag spikes
    background: '#04050d',
  },

  stars: {
    layers: [
      { count: 40, speed: 40, size: 1.2, alpha: 0.35 },
      { count: 28, speed: 90, size: 1.8, alpha: 0.55 },
      { count: 18, speed: 170, size: 2.6, alpha: 0.85 },
    ],
  },

  player: {
    startX: 360,
    startY: 1080,
    spriteRadius: 26,
    hitboxRadius: 7,          // shmup standard: hitbox ~1/4 of sprite
    followRate: 14,           // exponential follow toward touch target (snappy)
    maxFollowSpeed: 1700,
    keySpeed: 430,            // keyboard fallback (desktop preview)
    touchOffsetY: -80,        // ship hovers above the finger
    lives: 3,
    respawnDelay: 1.0,
    respawnInvuln: 3.0,       // blinking i-frames after respawn
    fireInterval: 0.12,       // auto-fire cadence while touching
    magnetRadius: 100,        // power-ups get pulled in
    pickupRadius: 34,
    bombsInitial: 2,
    bullet: {
      speed: 950, damage: 10, radius: 6, life: 2.0,
      color: '#7df9ff', glow: '#2ad4ff',
    },
    sideLaser: {              // weapon level 5 extra streams
      damage: 5, offsetX: 34, speed: 1100, radius: 4,
      color: '#b46cff', glow: '#8a2be2',
    },
    weaponLevels: {
      1: { angles: [0] },
      2: { angles: [0, 0], offsets: [-12, 12] },            // 2 parallel
      3: { angles: [-15, 0, 15] },                          // 3 spread 15deg
      4: { angles: [-30, -15, 0, 15, 30] },                 // 5 spread 30deg
      5: { angles: [-30, -15, 0, 15, 30], sideLasers: true },
    },
    colors: { body: '#58e6ff', accent: '#eaffff', engine: '#ff9d3c', hitbox: '#ffffff' },
  },

  bomb: {
    damage: 500,
    flash: { alpha: 0.9, dur: 0.3 },
    slowMo: { scale: 0.3, dur: 0.5 },
  },

  powerup: {
    dropChance: 0.05, bombDropChance: 0.01,
    fallSpeed: 90, magnetSpeed: 430,
    radius: 16,
    colors: { weapon: '#3ddc5a', bomb: '#ffd23e', rim: '#ffffff' },
    labels: { weapon: 'P', bomb: 'B' },
    fontPx: 18,
  },

  enemies: {
    chaser: {
      hp: 10, speed: 420, radius: 20, color: '#ff5a3c', outline: '#7a1408',
    },
    shooter: {
      hp: 20, speed: 190, radius: 22, color: '#ff3c78', outline: '#6d0a2c',
      stopYMin: 220, stopYMax: 520, pauseBeforeFire: 2.0,
      fireInterval: 1.4, bulletSpeed: 270, driftSpeed: 26,
    },
    turret: {
      hp: 30, speed: 150, radius: 24, color: '#c850ff', outline: '#3c0a63',
      patrolY: 210, moveTime: 1.6, stopTime: 1.0,
      spreadCount: 3, spreadDeg: 25, fireInterval: 1.0, bulletSpeed: 250,
    },
    formation: {
      hp: 10, speed: 300, radius: 18, color: '#ffa03c', outline: '#6b3305',
      count: 5, spacingX: 74, spacingY: 52, swayAmp: 26, swayFreq: 1.2,
    },
    elite: {
      hp: 80, speed: 95, radius: 30, color: '#ff2b2b', outline: '#4d0505',
      zigzagAmp: 130, zigzagFreq: 0.45, stopY: 300,
      fireInterval: 2.2, spreadCount: 5, spreadDeg: 40,
      bulletSpeed: 260, aimedSpeed: 320,
    },
    bullet: { radius: 9, life: 7, color: '#ff4a6a', glow: '#ff9ab5' },
    bossBullet: { life: 9, color: '#b46cff', glow: '#ff9d3c' },
    hitFlash: 0.1,
    hitParticles: 5,
    deathParticles: 20,
    contactKill: true,   // touching an enemy body costs a life (shmup default)
  },

  waves: {
    restBetween: 2.0,
    // deterministic spawn timeline: t is seconds since the wave starts
    definitions: [
      {
        duration: 12,
        spawns: [
          { t: 0, type: 'formation', x: 360 },
          { t: 2.0, type: 'chaser', x: 150 }, { t: 2.3, type: 'chaser', x: 570 },
          { t: 5.0, type: 'formation', x: 250 },
          { t: 8.0, type: 'chaser', x: 120 }, { t: 8.3, type: 'chaser', x: 240 },
          { t: 8.6, type: 'chaser', x: 360 }, { t: 8.9, type: 'chaser', x: 480 },
          { t: 9.2, type: 'chaser', x: 600 },
        ],
      },
      {
        duration: 12,
        spawns: [
          { t: 0, type: 'chaser', x: 100 }, { t: 0.3, type: 'chaser', x: 200 },
          { t: 0.6, type: 'chaser', x: 520 }, { t: 0.9, type: 'chaser', x: 620 },
          { t: 3.0, type: 'formation', x: 360 },
          { t: 6.0, type: 'chaser', x: 360 }, { t: 6.3, type: 'chaser', x: 260 },
          { t: 6.6, type: 'chaser', x: 460 },
          { t: 8.5, type: 'formation', x: 470 },
        ],
      },
      {
        duration: 14,
        spawns: [
          { t: 0, type: 'shooter', x: 200 }, { t: 0.5, type: 'shooter', x: 520 },
          { t: 3.0, type: 'chaser', x: 120 }, { t: 3.3, type: 'chaser', x: 600 },
          { t: 5.5, type: 'shooter', x: 360 },
          { t: 8.0, type: 'chaser', x: 240 }, { t: 8.3, type: 'chaser', x: 480 },
          { t: 10.0, type: 'shooter', x: 150 }, { t: 10.5, type: 'shooter', x: 570 },
        ],
      },
      {
        duration: 14,
        spawns: [
          { t: 0, type: 'turret', x: -40, dir: 1 },
          { t: 1.0, type: 'turret', x: 760, dir: -1 },
          { t: 4.0, type: 'shooter', x: 360 },
          { t: 7.0, type: 'chaser', x: 150 }, { t: 7.3, type: 'chaser', x: 360 },
          { t: 7.6, type: 'chaser', x: 570 },
          { t: 10.0, type: 'shooter', x: 200 }, { t: 10.5, type: 'shooter', x: 520 },
        ],
      },
      {
        duration: 16,
        spawns: [
          { t: 0, type: 'elite', x: 220 }, { t: 1.5, type: 'elite', x: 500 },
          { t: 4.0, type: 'formation', x: 360 },
          { t: 7.0, type: 'chaser', x: 120 }, { t: 7.3, type: 'chaser', x: 240 },
          { t: 7.6, type: 'chaser', x: 480 }, { t: 7.9, type: 'chaser', x: 600 },
          { t: 10.0, type: 'shooter', x: 360 },
          { t: 12.0, type: 'formation', x: 200 }, { t: 12.5, type: 'formation', x: 520 },
        ],
      },
    ],
  },

  boss: {
    name: 'VOID TYRANT',
    maxHp: 9000,
    radius: 92,
    entryY: 260,
    entrySpeed: 170,
    warning: { duration: 1.0, flashAlpha: 0.45 },
    thresholds: { phase2: 0.66, phase3: 0.33, enrage: 0.10 },
    phase3HealPct: 0.05,
    transition: {
      duration: 1.5,
      shake: { amp: 5, dur: 1.5 },
      whiteFlash: 0.2, flashAlpha: 0.85,
      slowMo: { scale: 0.3, dur: 0.3 },
      p3DarkAlpha: 0.5,
    },
    hurtFlash: 0.2,
    recover: 0.4,
    phases: {
      1: { cooldown: 1.5, bob: { amp: 100, freq: 0.35 } },
      2: { cooldown: 1.2, spinDegPerSec: 12 },
      3: { cooldown: 0.8, pulseFreq: 1.6 },
    },
    enrage: { cooldown: 0.5, telegraphScale: 0.7, continuousShake: 2 },
    patternWeights: {
      1: [{ id: 'aimed', weight: 60 }, { id: 'fan', weight: 40 }],
      2: [
        { id: 'spiral', weight: 40 }, { id: 'ring', weight: 35 },
        { id: 'laserSweep', weight: 25 },
      ],
      3: [
        { id: 'homing', weight: 40 }, { id: 'hellRing', weight: 35 },
        { id: 'laserCross', weight: 25 },
      ],
    },
    maxSamePatternInRow: 2,
    attacks: {
      aimed: {
        telegraph: 0.4, shots: 3, shotInterval: 0.2,
        bulletSpeed: 420, bulletRadius: 12,
      },
      fan: {
        telegraph: 0.8, count: 3, spreadDeg: 30,
        bulletSpeed: 340, bulletRadius: 12,
      },
      spiral: {
        telegraph: 0.6, duration: 4.0, bullets: 24, totalTurnDeg: 360,
        bulletSpeed: 220, bulletRadius: 11,
      },
      laserSweep: {
        telegraph: 1.2, fireTime: 0.5, halfWidth: 16,
        fromX: 90, toX: 630,
      },
      ring: {
        telegraph: 0.8, bullets: 16, bulletSpeed: 260, bulletRadius: 12,
      },
      homing: {
        telegraph: 0.6, count: 2, launchInterval: 0.4,
        speed: 300, turnRate: 3.2, homeTime: 2.0, bulletRadius: 13,
      },
      hellRing: {
        telegraph: 1.0, waves: 3, waveInterval: 0.45,
        bullets: 24, bulletSpeed: 240, bulletRadius: 12, ringOffsetDeg: 7.5,
      },
      laserCross: {
        telegraph: 1.5, fireTime: 0.5, halfWidth: 16, anglesDeg: [45, -45],
      },
    },
    colors: {
      phase1: '#9b5cff', phase2: '#ff3c5a', phase3: '#b3123a',
      core: '#7dff6a', outline: '#221033',
      telegraphGlowP2: '#3cc8ff', telegraphGlowP3: '#b46cff',
    },
    death: {
      slowMo: { scale: 0.2, dur: 1.5 },
      explosionWaves: 5, particlesPerWave: 50, waveInterval: 0.25,
      coins: 30, overlayDelay: 1.2, fadeDuration: 1.2,
    },
  },

  score: {
    perKill: 100, bossKill: 10000,
    comboEvery: 5, comboStep: 0.5, comboMax: 5,
  },

  fx: {
    playerHit: {
      shake: { amp: 6, dur: 0.25 },
      redFlash: 0.15, redFlashAlpha: 0.35,
      slowMo: { scale: 0.3, dur: 0.2 },
    },
    explosion: {
      colors: ['#ffd23e', '#ff9d3c', '#ff5a3c', '#ffffff', '#58e6ff', '#b46cff'],
      minSpeed: 50, maxSpeed: 420,
      lifeMin: 0.35, lifeMax: 0.9, sizeMin: 2, sizeMax: 6,
    },
    coin: {
      minSpeed: 100, maxSpeed: 360, life: 1.6,
      radius: 11, color: '#ffd23e', edge: '#b8860b', gravity: 260, spin: 7,
    },
    popup: { riseSpeed: 90, life: 0.7, fontPx: 30, color: '#ffd23e', takenColor: '#ff3b3b' },
  },

  controls: {
    bombButton: {
      centerX: 640, centerY: 1150, radius: 52,
      label: 'BOMB', color: 'rgba(255,210,62,0.28)', rim: 'rgba(255,220,90,0.85)',
    },
    pauseButton: { centerX: 46, centerY: 44, radius: 26, color: 'rgba(255,255,255,0.85)' },
  },

  ui: {
    score: { x: 92, y: 58, fontPx: 34, color: '#ffffff' },
    combo: { x: 92, y: 94, fontPx: 24, color: '#ffd23e' },
    lives: { right: 30, y: 46, iconSize: 17, gap: 12, color: '#58e6ff' },
    bombCount: { x: 640, y: 1078, fontPx: 22, color: '#ffd23e' },
    bossBar: {
      x: 150, y: 112, w: 420, h: 20,
      bgColor: 'rgba(255,255,255,0.14)', dividerColor: 'rgba(0,0,0,0.85)',
      segmentColors: ['#9b5cff', '#ff3c5a', '#b3123a'],
      nameY: 152, nameFontPx: 20, nameColor: '#d8c9ff',
    },
    warning: { fontPx: 76, color: '#ff2b2b', subFontPx: 30 },
  },

  menus: {
    overlayColor: 'rgba(4,5,13,0.80)',
    titleFontPx: 64, buttonFontPx: 32,
    titleColor: '#ffffff', buttonTextColor: '#04050d',
    button: { w: 360, h: 84, gap: 26, firstY: 560, color: '#58e6ff', radius: 16 },
    pauseTitle: 'PAUSED',
    pauseButtons: [
      { label: 'RESUME', action: 'resume' },
      { label: 'RESTART', action: 'restart' },
      { label: 'QUIT', action: 'quit' },
    ],
    victoryTitle: 'VICTORY!', victoryColor: '#ffd23e',
    defeatTitle: 'DEFEAT', defeatColor: '#ff3b3b',
    endButtons: [
      { label: 'PLAY AGAIN', action: 'restart' },
      { label: 'QUIT', action: 'quit' },
    ],
    quitTitle: 'GAME QUIT',
    quitButtons: [{ label: 'PLAY AGAIN', action: 'restart' }],
  },

  audio: {
    masterVolume: 0.8,
    sfx: [
      'player_shoot', 'player_hit', 'player_death',
      'enemy_hit', 'enemy_explosion',
      'powerup_collect', 'bomb_use',
      'boss_warning', 'boss_growl', 'boss_hit', 'boss_death',
      'ui_click', 'ui_pause',
    ],
    music: ['music_stage', 'music_boss'],
  },
};
