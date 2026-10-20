// Campaign + meta-screen constants (60 levels, chapter bosses, title/
// level-select/clear/defeat screens). Merged into CONFIG via CAMPAIGN_META.
export const CAMPAIGN_META = {
  campaign: {
    chapters: 6,
    levelsPerChapter: 10,
    chapterNames: [
      'BIEN GIOI XANH', 'VAN DAI LUA', 'TINH VAN TIM',
      'HOA NGUC DO', 'VUC SAU CAM', 'HAM DOI CUOI',
    ],
    bossEvery: 10,                       // level 10,20,...,60 = boss
    difficulty: {
      hpPerLevel: 0.035, speedPerLevel: 0.008, bulletPerLevel: 0.006,
      cap: 2.2,
    },
    bossHpByChapter: [1, 1.35, 1.7, 2.1, 2.6, 3.2],
    bossTypesByChapter: ['tyrant', 'dispatcher', 'omen', 'tyrant', 'dispatcher', 'omen'],
    bossNames: [
      'VOID TYRANT', 'CRIMSON DISPATCHER', 'OMEN WEAVER',
      'TYRANT PRIME', 'WAR DISPATCHER', 'OMEN OVERLORD',
    ],
    starTintByChapter: ['#58e6ff', '#ff9d3c', '#b46cff', '#ff3c5a', '#ffa03c', '#7df9ff'],
  },

  screens: {
    title: {
      logoFontPx: 74, subFontPx: 26,
      playButton: { x: 180, y: 820, w: 360, h: 96, label: 'CHOI', color: '#ffb700' },
      selectButton: { x: 230, y: 950, w: 260, h: 70, label: 'MAN CHOI', color: '#58e6ff' },
    },
    select: {
      cols: 5, cellW: 108, cellH: 96, gapX: 16, gapY: 18,
      firstX: 60, firstY: 430, fontPx: 30, starFontPx: 16,
      chapterFontPx: 40,
      arrow: { w: 90, h: 70, y: 700, leftX: 90, rightX: 540 },
      back: { x: 40, y: 60, w: 150, h: 60, label: 'QUAY LAI' },
    },
    banner: {
      time: 2.2, chapterY: 380, levelY: 450,
      chapterFontPx: 34, levelFontPx: 54,
    },
    clear: {
      starY: 470, starSize: 46, starGap: 70, starColor: '#ffd23e', starOff: 'rgba(255,255,255,0.2)',
      buttons: [
        { label: 'MAN KE TIEP', action: 'next' },
        { label: 'CHOI LAI', action: 'retry' },
        { label: 'MAN CHOI', action: 'select' },
      ],
    },
    defeatButtons: [
      { label: 'CHOI LAI', action: 'retry' },
      { label: 'MAN CHOI', action: 'select' },
    ],
    finalTitle: 'HOAN TAT CHIEN DICH!',
  },

};
