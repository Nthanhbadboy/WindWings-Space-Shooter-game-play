/**
 * Phòng thử UI — dựng lại HUD WindWings từ ảnh chụp thật.
 *
 * Mục đích: chỉnh hình bằng số đo (px trong khung 720×1496) rồi chồng lên ảnh gốc
 * để soi lệch. Khi khớp thì tê các giá trị trong `uikit.css` sang `style.css` của game.
 */
import './uikit.css';
import { ICONS, SHIP_ART } from './art.js';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

/* ---------------------------------------------------------------- scale khung */
const outer = $('#stageOuter');
const DESIGN_W = 720;
const DESIGN_H = 1496;

function fit() {
  const pad = 24;
  const k = Math.min(
    (window.innerWidth - pad) / DESIGN_W,
    (window.innerHeight - 132 - pad) / DESIGN_H,
    1,
  );
  const kk = Math.max(0.2, k);
  outer.style.transform = `scale(${kk})`;
  // hộp cha co lại đúng bằng kích thước sau scale để không tràn ngang
  const box = document.getElementById('stageBox');
  box.style.width = `${DESIGN_W * kk}px`;
  box.style.height = `${DESIGN_H * kk}px`;
}
window.addEventListener('resize', fit);
fit();

/* ------------------------------------------------------------------ ảnh tham chiếu */
const refShot = $('#refShot');
refShot.src = new URL('./uikit/gp1.jpg', import.meta.url).href;

const range = $('#refRange');
const refVal = $('#refVal');
const blink = $('#btnBlink');
let blinkTimer = null;

function setOverlay(v) {
  refShot.style.opacity = String(v / 100);
  range.value = String(v);
  refVal.textContent = `${v}%`;
}
range.addEventListener('input', () => {
  stopBlink();
  setOverlay(Number(range.value));
});

function stopBlink() {
  if (blinkTimer) clearInterval(blinkTimer);
  blinkTimer = null;
  blink.setAttribute('aria-pressed', 'false');
}
blink.addEventListener('click', () => {
  if (blinkTimer) { stopBlink(); return; }
  blink.setAttribute('aria-pressed', 'true');
  let on = false;
  blinkTimer = setInterval(() => {
    on = !on;
    refShot.style.opacity = on ? '1' : '0';
  }, 520);
});

/* ------------------------------------------------------------------------ lưới */
const stage = $('#stage');
$('#btnGrid').addEventListener('click', (e) => {
  const on = stage.classList.toggle('grid');
  e.currentTarget.setAttribute('aria-pressed', String(on));
});

/* ------------------------------------------------------------------ đổi màn thử */
$$('.lab-tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    $$('.lab-tab').forEach((t) => t.setAttribute('aria-selected', String(t === tab)));
    $$('.view').forEach((v) => { v.hidden = v.dataset.panel !== tab.dataset.view; });
    // màn linh kiện thì tắt ảnh chồng cho khỏi rối
    if (tab.dataset.view !== 'hud') setOverlay(0);
    stopBlink();
  });
});

/* --------------------------------------------------------------------- nội dung */
$('#portrait').src = SHIP_ART.omen;
$('#shipCard').src = SHIP_ART.striker;
$('#coinIco').src = ICONS.coin;
$('#skullIco').src = ICONS.skull;
$$('.coin-mini').forEach((i) => { i.src = ICONS.coin; });
$$('.star-mini').forEach((i) => { i.src = ICONS.star; });

const segBar = $('#segBar');
for (let i = 0; i < 5; i++) {
  const s = document.createElement('i');
  if (i < 2) s.className = 'on';
  segBar.appendChild(s);
}

// minh hoạ thanh máu co giãn: 100% → 18% → 100% để thấy mép vát
const hpFill = $('#hpFill');
const hpNum = $('#hpNum');
let hp = 100;
setInterval(() => {
  hp = hp > 30 ? hp - 0.9 : 100;
  hpFill.style.width = `${hp}%`;
  hpNum.textContent = Math.round((hp / 100) * 2500).toLocaleString('vi-VN').replace(/\u00a0/g, '.');
}, 260);
