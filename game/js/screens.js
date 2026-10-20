// Meta screens: TITLE (Ramus-style big yellow CHOI button), LEVEL SELECT
// (60 levels, 6 chapter pages, locks + stars), LEVEL CLEAR, DEFEAT.
import { CONFIG } from './config.js';
import { getLevel, TOTAL_LEVELS } from './levels.js';

const M = CONFIG.menus;
const SC = CONFIG.screens;
const S = CONFIG.screen;
const CAM = CONFIG.campaign;

function bigButton(ctx, r, label, color, textColor) {
  ctx.fillStyle = color;
  ctx.beginPath();
  if (ctx.roundRect) ctx.roundRect(r.x, r.y, r.w, r.h, 16);
  else ctx.rect(r.x, r.y, r.w, r.h);
  ctx.fill();
  ctx.strokeStyle = 'rgba(4,5,13,0.6)';
  ctx.lineWidth = 4;
  ctx.stroke();
  ctx.fillStyle = textColor || M.buttonTextColor;
  ctx.font = `bold ${M.buttonFontPx}px sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(label, r.x + r.w / 2, r.y + r.h / 2);
  ctx.textBaseline = 'alphabetic';
}

function star(ctx, x, y, r, filled) {
  ctx.save();
  ctx.translate(x, y);
  ctx.beginPath();
  for (let i = 0; i < 10; i++) {
    const rr = i % 2 === 0 ? r : r * 0.45;
    const a = (i * Math.PI) / 5 - Math.PI / 2;
    ctx[i === 0 ? 'moveTo' : 'lineTo'](Math.cos(a) * rr, Math.sin(a) * rr);
  }
  ctx.closePath();
  ctx.fillStyle = filled ? SC.clear.starColor : SC.clear.starOff;
  ctx.fill();
  ctx.restore();
}

// ---------------------------------------------------------------- title
function drawTitle(game, ctx) {
  ctx.fillStyle = M.overlayColor;
  ctx.fillRect(0, 0, S.width, S.height);
  ctx.textAlign = 'center';
  ctx.fillStyle = '#ffb700';
  ctx.font = `bold ${SC.title.logoFontPx}px sans-serif`;
  ctx.fillText('WINDWINGS', S.width / 2, 520);
  ctx.fillStyle = '#58e6ff';
  ctx.font = `bold ${SC.title.subFontPx}px sans-serif`;
  ctx.fillText('BOSS FIGHT - 60 MAN', S.width / 2, 590);
  const pb = SC.title.playButton;
  bigButton(ctx, pb, pb.label, pb.color);
  const sb = SC.title.selectButton;
  bigButton(ctx, sb, sb.label, sb.color);
  ctx.fillStyle = '#9fb8d8';
  ctx.font = '22px sans-serif';
  ctx.fillText(
    `DA MO KHOA: ${game.progress.unlocked}/${TOTAL_LEVELS}`,
    S.width / 2, 1090
  );
}

// --------------------------------------------------------- level select
function cellRect(i) {
  const SL = SC.select;
  const col = i % SL.cols;
  const row = Math.floor(i / SL.cols);
  return {
    x: SL.firstX + col * (SL.cellW + SL.gapX),
    y: SL.firstY + row * (SL.cellH + SL.gapY),
    w: SL.cellW,
    h: SL.cellH,
  };
}

function drawSelect(game, ctx) {
  const SL = SC.select;
  const ch = game.selectChapter;
  ctx.fillStyle = M.overlayColor;
  ctx.fillRect(0, 0, S.width, S.height);
  ctx.textAlign = 'center';
  ctx.fillStyle = '#9fb8d8';
  ctx.font = '22px sans-serif';
  ctx.fillText(`TRANG ${ch}/${CAM.chapters}`, S.width / 2, 250);
  ctx.fillStyle = CAM.starTintByChapter[ch - 1];
  ctx.font = `bold ${SL.chapterFontPx}px sans-serif`;
  ctx.fillText(`CHUONG ${ch}: ${CAM.chapterNames[ch - 1]}`, S.width / 2, 340);

  for (let i = 0; i < CAM.levelsPerChapter; i++) {
    const n = (ch - 1) * CAM.levelsPerChapter + i + 1;
    const r = cellRect(i);
    const lv = getLevel(n);
    const unlocked = game.progress.isUnlocked(n);
    ctx.fillStyle = unlocked
      ? (lv.isBoss ? 'rgba(200,30,60,0.35)' : 'rgba(88,230,255,0.12)')
      : 'rgba(255,255,255,0.05)';
    ctx.fillRect(r.x, r.y, r.w, r.h);
    ctx.strokeStyle = unlocked ? (lv.isBoss ? '#ff3c5a' : '#58e6ff') : '#3a4a63';
    ctx.lineWidth = 3;
    ctx.strokeRect(r.x, r.y, r.w, r.h);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    if (unlocked) {
      ctx.fillStyle = lv.isBoss ? '#ff3c5a' : '#ffffff';
      ctx.font = `bold ${SL.fontPx}px sans-serif`;
      ctx.fillText(lv.isBoss ? 'BOSS' : String(n), r.x + r.w / 2, r.y + r.h / 2 - 14);
      const st = game.progress.starsOf(n);
      for (let k = 0; k < 3; k++) {
        star(ctx, r.x + r.w / 2 + (k - 1) * 24, r.y + r.h - 22, 9, k < st);
      }
    } else {
      // padlock glyph
      const cx = r.x + r.w / 2;
      const cy = r.y + r.h / 2;
      ctx.strokeStyle = '#5a6a83';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.arc(cx, cy - 8, 10, Math.PI, 0);
      ctx.stroke();
      ctx.fillStyle = '#5a6a83';
      ctx.fillRect(cx - 14, cy, 28, 22);
    }
    ctx.textBaseline = 'alphabetic';
  }

  const ar = SL.arrow;
  bigButton(ctx, { x: ar.leftX, y: ar.y, w: ar.w, h: ar.h }, '<', '#22304a', '#ffffff');
  bigButton(ctx, { x: ar.rightX, y: ar.y, w: ar.w, h: ar.h }, '>', '#22304a', '#ffffff');
  const b = SL.back;
  bigButton(ctx, b, b.label, '#22304a', '#ffffff');
}

// ---------------------------------------------------- clear + defeat
function endButtonRect(i) {
  return {
    x: (S.width - M.button.w) / 2,
    y: M.button.firstY + i * (M.button.h + M.button.gap),
    w: M.button.w,
    h: M.button.h,
  };
}

function endButtonsFor(game) {
  if (game.state === 'victory') {
    const isLast = game.currentLevel >= TOTAL_LEVELS;
    return isLast ? SC.clear.buttons.slice(1) : SC.clear.buttons;
  }
  return SC.defeatButtons;
}

function drawClear(game, ctx) {
  ctx.fillStyle = M.overlayColor;
  ctx.fillRect(0, 0, S.width, S.height);
  ctx.textAlign = 'center';
  const isLast = game.currentLevel >= TOTAL_LEVELS;
  ctx.fillStyle = M.victoryColor;
  ctx.font = `bold ${M.titleFontPx}px sans-serif`;
  ctx.fillText(isLast ? SC.finalTitle : 'HOAN TAT MAN!', S.width / 2, 330);
  ctx.fillStyle = '#9fb8d8';
  ctx.font = 'bold 30px sans-serif';
  ctx.fillText(getLevel(game.currentLevel).label, S.width / 2, 390);
  const cl = SC.clear;
  for (let k = 0; k < 3; k++) {
    star(ctx, S.width / 2 + (k - 1) * cl.starGap, cl.starY, cl.starSize, k < game.lastStars);
  }
  ctx.fillStyle = '#ffffff';
  ctx.font = `bold ${M.buttonFontPx}px sans-serif`;
  ctx.fillText(`SCORE ${game.score.score}`, S.width / 2, 545 - M.button.gap);
  endButtonsFor(game).forEach((b, i) => {
    bigButton(ctx, endButtonRect(i), b.label, i === 0 ? '#ffd23e' : M.button.color);
  });
}

function drawDefeat(game, ctx) {
  ctx.fillStyle = M.overlayColor;
  ctx.fillRect(0, 0, S.width, S.height);
  ctx.textAlign = 'center';
  ctx.fillStyle = M.defeatColor;
  ctx.font = `bold ${M.titleFontPx}px sans-serif`;
  ctx.fillText(M.defeatTitle, S.width / 2, 380);
  ctx.fillStyle = '#ffffff';
  ctx.font = `bold ${M.buttonFontPx}px sans-serif`;
  ctx.fillText(`SCORE ${game.score.score}`, S.width / 2, 460);
  endButtonsFor(game).forEach((b, i) => {
    bigButton(ctx, endButtonRect(i), b.label, M.button.color);
  });
}

// ---------------------------------------------------------------- taps
export function screenButtons(game) {
  const out = [];
  if (game.state === 'menu') {
    out.push({ action: 'play', rect: SC.title.playButton });
    out.push({ action: 'select', rect: SC.title.selectButton });
  } else if (game.state === 'select') {
    out.push({ action: 'back', rect: SC.select.back });
    const ar = SC.select.arrow;
    out.push({ action: 'prevChapter', rect: { x: ar.leftX, y: ar.y, w: ar.w, h: ar.h } });
    out.push({ action: 'nextChapter', rect: { x: ar.rightX, y: ar.y, w: ar.w, h: ar.h } });
    for (let i = 0; i < CAM.levelsPerChapter; i++) {
      const n = (game.selectChapter - 1) * CAM.levelsPerChapter + i + 1;
      out.push({ action: 'level', n, rect: cellRect(i) });
    }
  } else if (game.state === 'victory' || game.state === 'defeat') {
    endButtonsFor(game).forEach((b, i) => {
      out.push({ action: b.action, rect: endButtonRect(i) });
    });
  }
  return out;
}

export function handleScreenTap(game, x, y) {
  for (const b of screenButtons(game)) {
    const r = b.rect;
    if (x >= r.x && x <= r.x + r.w && y >= r.y && y <= r.y + r.h) {
      game.audio.play('ui_click');
      applyScreenAction(game, b.action, b.n);
      return true;
    }
  }
  return false;
}

function applyScreenAction(game, action, n) {
  if (action === 'play') game.startLevel(game.progress.unlocked);
  else if (action === 'select') {
    game.state = 'select';
    game.selectChapter = Math.ceil(game.progress.unlocked / CAM.levelsPerChapter);
  } else if (action === 'back') game.state = 'menu';
  else if (action === 'prevChapter') game.selectChapter = Math.max(1, game.selectChapter - 1);
  else if (action === 'nextChapter') game.selectChapter = Math.min(CAM.chapters, game.selectChapter + 1);
  else if (action === 'level') {
    if (game.progress.isUnlocked(n)) game.startLevel(n);
  } else if (action === 'next') {
    if (game.currentLevel < TOTAL_LEVELS) game.startLevel(game.currentLevel + 1);
    else game.state = 'menu';
  } else if (action === 'retry') game.startLevel(game.currentLevel);
}

export function drawScreens(game, ctx) {
  if (game.state === 'menu') drawTitle(game, ctx);
  else if (game.state === 'select') drawSelect(game, ctx);
  else if (game.state === 'victory') drawClear(game, ctx);
  else if (game.state === 'defeat') drawDefeat(game, ctx);
}
