// HUD layer: score + combo, lives, bomb count, boss bar (3 segments),
// WARNING banner, and the pause / victory / defeat / quit menus.
import { CONFIG } from './config.js';

const UI = CONFIG.ui;
const M = CONFIG.menus;
const B = CONFIG.boss;
const CAM = CONFIG.campaign;
const S = CONFIG.screen;

export function drawHud(game, ctx) {
  const boss = game.boss;
  if (boss && boss.visible) drawBossBar(game, ctx);
  if (boss && boss.state === 'warning') drawWarning(game, ctx);
  drawScore(game, ctx);
  drawLives(game, ctx);
  drawBombs(game, ctx);
  drawMenu(game, ctx);
  if (game.state === 'playing' && !game.paused) {
    drawLevelTag(game, ctx);
    drawBanner(game, ctx);
  }
}

/** Small "LV n" tag under the bomb counter. */
function drawLevelTag(game, ctx) {
  const bc = UI.bombCount;
  ctx.save();
  ctx.fillStyle = '#9fb8d8';
  ctx.font = `bold ${bc.fontPx - 4}px sans-serif`;
  ctx.textAlign = 'center';
  ctx.fillText(`LV ${game.currentLevel}/60`, bc.x, bc.y + 34);
  ctx.restore();
}

/** Level start banner (chapter name + level/boss name), fades out. */
function drawBanner(game, ctx) {
  if (game.bannerT <= 0 || !game.level) return;
  const bn = CONFIG.screens.banner;
  const alpha = Math.min(1, game.bannerT / 0.5);
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.textAlign = 'center';
  ctx.fillStyle = game.level.tint;
  ctx.font = `bold ${bn.chapterFontPx}px sans-serif`;
  ctx.fillText(
    `CHUONG ${game.level.chapter}: ${CAM.chapterNames[game.level.chapter - 1]}`,
    S.width / 2, bn.chapterY
  );
  ctx.fillStyle = game.level.isBoss ? '#ff3c5a' : '#ffffff';
  ctx.font = `bold ${bn.levelFontPx}px sans-serif`;
  ctx.fillText(
    game.level.isBoss ? `BOSS: ${game.boss.bossName}` : `MAN ${game.currentLevel}`,
    S.width / 2, bn.levelY
  );
  ctx.restore();
}

/** 3-segment boss bar (one segment per phase), fills with HP. */
function drawBossBar(game, ctx) {
  const bar = UI.bossBar;
  const boss = game.boss;
  ctx.save();
  ctx.fillStyle = bar.bgColor;
  ctx.fillRect(bar.x, bar.y, bar.w, bar.h);
  ctx.fillStyle = bar.segmentColors[boss.phase - 1] || bar.segmentColors[0];
  ctx.fillRect(bar.x, bar.y, bar.w * boss.hpFrac, bar.h);
  ctx.fillStyle = bar.dividerColor;
  for (const f of [B.thresholds.phase3, B.thresholds.phase2]) {
    ctx.fillRect(bar.x + bar.w * f - 1.5, bar.y, 3, bar.h);
  }
  ctx.strokeStyle = 'rgba(255,255,255,0.5)';
  ctx.lineWidth = 2;
  ctx.strokeRect(bar.x, bar.y, bar.w, bar.h);
  ctx.fillStyle = bar.nameColor;
  ctx.font = `bold ${bar.nameFontPx}px sans-serif`;
  ctx.textAlign = 'center';
  ctx.fillText(game.boss.bossName || B.name, bar.x + bar.w / 2, bar.nameY);
  ctx.restore();
}

/** Flashing red WARNING banner during the 1s boss warning. */
function drawWarning(game, ctx) {
  const w = B.warning;
  const blink = Math.abs(Math.sin(game.boss.warnT * Math.PI * 5));
  ctx.save();
  ctx.globalAlpha = w.flashAlpha * blink * 0.6;
  ctx.fillStyle = '#ff2b2b';
  ctx.fillRect(0, 0, S.width, S.height);
  ctx.globalAlpha = 0.5 + 0.5 * blink;
  ctx.fillStyle = UI.warning.color;
  ctx.font = `bold ${UI.warning.fontPx}px sans-serif`;
  ctx.textAlign = 'center';
  ctx.fillText('WARNING', S.width / 2, S.height / 2 - 20);
  ctx.font = `bold ${UI.warning.subFontPx}px sans-serif`;
  ctx.fillText('BOSS APPROACHING', S.width / 2, S.height / 2 + 30);
  ctx.restore();
}

function drawScore(game, ctx) {
  ctx.save();
  ctx.fillStyle = UI.score.color;
  ctx.font = `bold ${UI.score.fontPx}px sans-serif`;
  ctx.textAlign = 'left';
  ctx.fillText(`${game.score.score}`, UI.score.x, UI.score.y);
  if (game.score.multiplier > 1) {
    ctx.fillStyle = UI.combo.color;
    ctx.font = `bold ${UI.combo.fontPx}px sans-serif`;
    ctx.fillText(`COMBO x${game.score.multiplier.toFixed(1)}`, UI.combo.x, UI.combo.y);
  }
  ctx.restore();
}

function drawLives(game, ctx) {
  ctx.save();
  for (let i = 0; i < game.player.lives; i++) {
    const x = S.width - UI.lives.right - i * (UI.lives.iconSize * 2 + UI.lives.gap);
    const r = UI.lives.iconSize;
    ctx.fillStyle = UI.lives.color;
    ctx.beginPath();
    ctx.moveTo(x, UI.lives.y - r);
    ctx.lineTo(x - r * 0.8, UI.lives.y + r * 0.7);
    ctx.lineTo(x, UI.lives.y + r * 0.3);
    ctx.lineTo(x + r * 0.8, UI.lives.y + r * 0.7);
    ctx.closePath();
    ctx.fill();
  }
  ctx.restore();
}

function drawBombs(game, ctx) {
  const bc = UI.bombCount;
  ctx.save();
  ctx.fillStyle = bc.color;
  ctx.font = `bold ${bc.fontPx}px sans-serif`;
  ctx.textAlign = 'center';
  ctx.fillText(`BOMB x${game.player.bombs}`, bc.x, bc.y);
  ctx.restore();
}

// ------------------------------------------------------------------ menus
function menuInfo(game) {
  // victory/defeat/title/select overlays live in screens.js
  if (game.paused && game.state === 'playing') {
    return { title: M.pauseTitle, color: M.titleColor, buttons: M.pauseButtons };
  }
  return null;
}

export function menuButtons(game) {
  const info = menuInfo(game);
  if (!info) return [];
  const bw = M.button.w;
  const x = (S.width - bw) / 2;
  return info.buttons.map((b, i) => ({
    x,
    y: M.button.firstY + i * (M.button.h + M.button.gap),
    w: bw,
    h: M.button.h,
    label: b.label,
    action: b.action,
  }));
}

function drawMenu(game, ctx) {
  const info = menuInfo(game);
  if (!info) return;
  ctx.save();
  ctx.fillStyle = M.overlayColor;
  ctx.fillRect(0, 0, S.width, S.height);
  ctx.textAlign = 'center';
  ctx.fillStyle = info.color;
  ctx.font = `bold ${M.titleFontPx}px sans-serif`;
  ctx.fillText(info.title, S.width / 2, M.button.firstY - 120);
  if (info.score) {
    ctx.fillStyle = '#ffffff';
    ctx.font = `bold ${M.buttonFontPx}px sans-serif`;
    ctx.fillText(`SCORE ${game.score.score}`, S.width / 2, M.button.firstY - 60);
  }
  for (const b of menuButtons(game)) {
    ctx.fillStyle = M.button.color;
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(b.x, b.y, b.w, b.h, M.button.radius);
    else ctx.rect(b.x, b.y, b.w, b.h);
    ctx.fill();
    ctx.fillStyle = M.buttonTextColor;
    ctx.font = `bold ${M.buttonFontPx}px sans-serif`;
    ctx.textBaseline = 'middle';
    ctx.fillText(b.label, b.x + b.w / 2, b.y + b.h / 2);
    ctx.textBaseline = 'alphabetic';
  }
  ctx.restore();
}

export function handleUiTap(game, x, y) {
  for (const b of menuButtons(game)) {
    if (x >= b.x && x <= b.x + b.w && y >= b.y && y <= b.y + b.h) {
      game.audio.play('ui_click');
      applyAction(game, b.action);
      return true;
    }
  }
  return false;
}

function applyAction(game, action) {
  if (action === 'resume') game.togglePause();
  else if (action === 'restart') game.restart();
  else if (action === 'quit') {
    game.paused = false;
    game.state = 'menu';
  }
}
