#!/usr/bin/env node
/**
 * ramus-probe.mjs — drive a Ramus Android session against a running Unity build
 * that has RamusBridge embedded, and write a machine-readable + human report.
 *
 *   node .github/scripts/ramus-probe.mjs --out reports/probe --label "PR #12"
 *
 * Two data paths, tried in order:
 *   1. HTTP   — adb forward tcp:8080 tcp:8080        (signed-in key / adb tunnel)
 *   2. logcat — `${'RAMUSB'}|{json}` lines emitted by the bridge (works on the
 *               anonymous trial, which has no adb)
 *
 * Modes:
 *   --mode auto    (default) trial when RAMUS_API_KEY is unset, else key
 *   --mode trial   never wait long for HTTP; poll logcat instead
 *   --mode key     HTTP is expected; an unreachable bridge is an error
 *
 * Exit code is 0 unless --strict is passed and neither path produced data.
 */

import { spawnSync } from 'node:child_process';
import { appendFileSync, mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';

// ── cli ────────────────────────────────────────────────────────────────────

const argv = process.argv.slice(2);
const opt = {
  out: 'reports/probe',
  label: 'runtime probe',
  base: process.env.RAMUS_BRIDGE_BASE || 'http://127.0.0.1:8080',
  waitServer: 90,
  waitScene: '',
  strict: false,
  screenshots: 2,
  mode: 'auto',
  logcatWait: 60,
  budget: 0,
  statics: 'Stage_Datas,Player_Get_Datas,Enemy_Get_Datas,Stage_Get_Datas',
  // Contract test: reuse the whole pipeline without a device.
  offline: false,
  logcatFixture: '',
};

for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  const next = () => argv[++i];
  if (a === '--out') opt.out = next();
  else if (a === '--label') opt.label = next();
  else if (a === '--base') opt.base = next();
  else if (a === '--wait-server') opt.waitServer = Number(next());
  else if (a === '--wait-scene') opt.waitScene = next();
  else if (a === '--strict') opt.strict = true;
  else if (a === '--offline') opt.offline = true;
  else if (a === '--logcat-fixture') opt.logcatFixture = next();
  else if (a === '--screenshots') opt.screenshots = Number(next());
  else if (a === '--mode') opt.mode = next();
  else if (a === '--logcat-wait') opt.logcatWait = Number(next());
  else if (a === '--budget') opt.budget = Number(next());
  else if (a === '--statics') opt.statics = next();
  else if (a === '--help' || a === '-h') {
    console.log('usage: ramus-probe.mjs [--out DIR] [--label TEXT] [--base URL] [--mode auto|key|trial]');
    console.log('                         [--wait-server SEC] [--logcat-wait SEC] [--wait-scene NAME] [--budget SEC] [--strict]');
    console.log('                         [--statics "Stage_Datas,Player_Get_Datas,..."]');
    process.exit(0);
  }
}

const MODE = opt.mode === 'auto' ? (process.env.RAMUS_API_KEY ? 'key' : 'trial') : opt.mode;
const CLI = process.env.RAMUS_CLI || 'ramus-cli@0.1.17';
const SESSION = process.env.RAMUS_SESSION || '';
const OUT = path.resolve(opt.out);
mkdirSync(OUT, { recursive: true });

const result = {
  label: opt.label,
  mode: MODE,
  startedAt: new Date().toISOString(),
  base: opt.base,
  transport: 'none',
  session: SESSION || null,
  trialExpiresAt: process.env.RAMUS_TRIAL_EXPIRES || null,
  app: {},
  bridge: {},
  logcat: { raw: [], states: [] },
  screenshots: [],
  notes: [],
  errors: [],
  verdict: 'unknown',
};

const log = (msg) => console.log(`[probe] ${msg}`);
const note = (msg) => {
  result.notes.push(msg);
  log(`note  ${msg}`);
};
const fail = (msg, extra) => {
  const line = extra === undefined ? msg : `${msg}: ${extra}`;
  if (!result.errors.includes(line)) result.errors.push(line);
  log(`ERROR ${msg}${extra === undefined ? '' : ` — ${extra}`}`);
};

// ── ramus cli ──────────────────────────────────────────────────────────────

function ramus(args, { allowFail = true, timeout = 180000 } = {}) {
  if (opt.offline) return { ok: false, stdout: '', stderr: 'offline mode', status: 127 };
  const full = [...args, ...(SESSION ? ['--session', SESSION] : [])];
  const r = spawnSync(process.platform === 'win32' ? 'npx.cmd' : 'npx', ['--yes', CLI, ...full], {
    encoding: 'utf8',
    timeout,
    maxBuffer: 32 * 1024 * 1024,
  });
  const out = (r.stdout || '').trim();
  const err = (r.stderr || '').trim();
  if (r.status !== 0 && !allowFail) throw new Error(`ramus ${args[0]} failed (${r.status}): ${err || out}`);
  if (r.status !== 0) {
    const detail = (err || out).slice(0, 400);
    if (result.errors.filter((e) => e.startsWith(`ramus ${args[0]}`)).length > 2) return { ok: false, stdout: out, stderr: err, status: r.status };
    if (/trial_restricted/.test(detail)) note('the anonymous trial cannot use this command (adb/dev are key-only)');
    else if (/unauthorized|401|trial (expired|has ended)/i.test(detail)) note(`trial credential problem: ${detail}`);
    result.errors.push(`ramus ${args.join(' ')} → exit ${r.status}: ${detail}`);
  }
  return { ok: r.status === 0, stdout: out, stderr: err, status: r.status };
}

// ── http ───────────────────────────────────────────────────────────────────

async function get(pathname, timeoutMs = 8000) {
  const url = `${opt.base.replace(/\/$/, '')}${pathname}`;
  const ac = new AbortController();
  const timer = setTimeout(() => ac.abort(), timeoutMs);
  try {
    const res = await fetch(url, { signal: ac.signal, headers: { Accept: 'application/json, image/png' } });
    const type = res.headers.get('content-type') || '';
    if (type.startsWith('image/')) {
      const buf = Buffer.from(await res.arrayBuffer());
      return { status: res.status, image: buf };
    }
    return { status: res.status, json: await res.json() };
  } catch (e) {
    return { status: 0, error: e.name === 'AbortError' ? `timeout ${timeoutMs}ms` : String(e.message || e) };
  } finally {
    clearTimeout(timer);
  }
}

async function waitForBridge(seconds) {
  const deadline = Date.now() + seconds * 1000;
  let attempt = 0;
  while (Date.now() < deadline) {
    attempt++;
    const r = await get('/health', 4000);
    if (r.status === 200 && r.json) return r.json;
    if (attempt % 5 === 0) log(`waiting for bridge… (${Math.round((deadline - Date.now()) / 1000)}s left)`);
    await new Promise((r2) => setTimeout(r2, 3000));
  }
  return null;
}

// ── logcat fallback ────────────────────────────────────────────────────────

/**
 * `ramus logcat` answers with JSON — {"lines":[{"stamp","stream","text"}]} —
 * not with plain text. Treating it as text made every regex run against JSON
 * punctuation, the tag histogram report one bucket called "other", and the
 * "did it start" table compare against escaped strings. Accept both shapes.
 */
function logcatLines(raw) {
  const text = String(raw || '');
  try {
    const d = JSON.parse(text);
    const arr = Array.isArray(d) ? d : Array.isArray(d.lines) ? d.lines : null;
    if (arr) {
      return arr.map((l) => {
        if (typeof l === 'string') return l;
        const stamp = l.stamp || l.time || '';
        const stream = l.stream || '';
        const body = l.text || l.message || l.msg || '';
        return `${stamp} ${stream} ${body}`.replace(/\s+/g, ' ').trim();
      }).filter(Boolean);
    }
  } catch { /* not JSON: plain text (older CLI, or an error message) */ }
  return text.split('\n').map((l) => l.trim()).filter(Boolean);
}

function readLogcatStates(limit = 500) {
  // The CLI rejects --limit > 500 ("limit must be at most 500").
  const r = opt.logcatFixture
    ? { ok: true, stdout: readFileSync(opt.logcatFixture, 'utf8'), stderr: '' }
    : ramus(['logcat', '--limit', String(Math.min(limit, 500))]);
  const text = `${r.stdout}\n${r.stderr}`;
  const lines = logcatLines(text);
  result.logcat.rawJson = text.slice(0, 4000);
  result.logcat.rawAll = lines.join('\n');
  if (r.ok) {
    try { writeFileSync(path.join(OUT, 'logcat.txt'), lines.join('\n')); } catch { /* best effort */ }
  }
  result.logcat.raw = lines.filter((l) => l.includes('RAMUSB')).slice(-120);

  // Which buffers did the transport actually return? Unity, ActivityManager and
  // app crashes log to `main`/`crash`; the trial only ever returned `system` in
  // run 39925095796. Saying "no Unity line" when `main` was never read would be
  // a claim the data cannot support.
  try {
    const d = JSON.parse(text);
    const arr = Array.isArray(d) ? d : Array.isArray(d.lines) ? d.lines : [];
    const streams = {};
    for (const l of arr) {
      const k = (l && (l.stream || l.buffer)) || 'unknown';
      streams[k] = (streams[k] || 0) + 1;
    }
    result.logcat.streams = streams;
  } catch {
    result.logcat.streams = { text: lines.length };
  }
  // Keep a bounded copy of everything, so the report can show what the device
  // actually logged instead of only what we managed to parse.
  result.logcat.lines = lines.slice(-500);
  const states = [];
  for (const line of lines) {
    const at = line.indexOf('RAMUSB|');
    if (at < 0) continue;
    const payload = line.slice(at + 'RAMUSB|'.length).trim();
    try {
      states.push({ line: line.slice(0, at).trim(), state: JSON.parse(payload) });
    } catch {
      result.errors.push(`unparsable RAMUSB line: ${payload.slice(0, 120)}`);
    }
  }
  result.logcat.states = states;
  return states;
}

/** Ask logcat for only the lines that matter (`--filter` scans the scrollback). */
function logcatFiltered(needle, limit = 500) {
  const r = ramus(['logcat', '--limit', String(Math.min(limit, 500)), '--filter', needle]);
  if (!r.ok) return null;
  return logcatLines(r.stdout).slice(-60);
}

/** Poll logcat until the bridge mirrors at least one state line. */
async function waitForLogcat(seconds) {
  const deadline = Date.now() + seconds * 1000;
  let launched = false;
  let attempt = 0;
  while (Date.now() < deadline) {
    attempt++;
    const states = readLogcatStates();
    if (states.length > 0) return states;

    if (!launched && attempt >= 2) {
      launched = true;
      // A crash, HOME press or a slow first boot leaves the app in the background.
      const r = opt.offline
        ? { ok: true, stdout: '', stderr: '', status: 0 }
        : ramus(['app', 'launch']);
      // Keep the answer: on a trial this is the only statement about whether the
      // activity could be started at all.
      result.launch = {
        ok: r.ok,
        code: r.status ?? null,
        stdout: String(r.stdout || '').slice(0, 600),
        stderr: String(r.stderr || '').slice(0, 600),
      };
      if (r.ok) note('sent `app launch` because no bridge line appeared yet');
      else fail('app launch failed', `${String(r.stderr || r.stdout || '').slice(0, 200)}`);
    }

    const left = Math.round((deadline - Date.now()) / 1000);
    log(`waiting for RAMUSB logcat line… (${left}s left)`);
    await new Promise((resolve) => setTimeout(resolve, 5000));
  }
  return readLogcatStates();
}

// ── screenshots / ui ───────────────────────────────────────────────────────

function screenshot(n) {
  const file = path.join(OUT, `screen-${String(n).padStart(2, '0')}.jpg`);
  const r = ramus(['screenshot', '--out', file]);
  if (!r.ok) return false;
  result.screenshots.push(path.basename(file));

  // A JPEG that never changes while the app is "launched" is the difference
  // between "the game is showing" and "the launcher never moved".
  try {
    const buf = readFileSync(file);
    const sha = createHash('sha256').update(buf).digest('hex');
    result.screens = result.screens || [];
    const prev = result.screens[result.screens.length - 1];
    result.screens.push({
      file: path.basename(file),
      bytes: statSync(file).size,
      sha256: sha.slice(0, 16),
      sameAsPrevious: prev ? prev.sha256 === sha.slice(0, 16) : null,
    });
  } catch { /* screenshot bookkeeping is best effort */ }
  return true;
}

/** Ask the CLI what the device/session looks like — cheap, and it may name the ABI. */
function sessionStatus() {
  const r = ramus(['session', 'status']);
  if (!r.ok) return null;
  try {
    const parsed = JSON.parse(r.stdout);
    result.sessionStatus = parsed;
    return parsed;
  } catch {
    result.sessionStatus = { raw: String(r.stdout).slice(0, 2000) };
    return result.sessionStatus;
  }
}

/**
 * `ramus snapshot --raw` may return the XML bare or wrapped in JSON with escaped
 * quotes. The first version only matched bare XML, so every report said
 * "packages: —" even when the tree named the foreground package.
 */
function unwrapXml(raw) {
  const text = String(raw || '');
  try {
    const d = JSON.parse(text);
    for (const key of ['xml', 'raw', 'ui', 'tree', 'snapshot', 'data']) {
      if (typeof d[key] === 'string') return d[key];
    }
    if (typeof d === 'string') return d;
  } catch { /* not JSON */ }
  // Escaped XML inside a JSON-ish blob: undo the escaping and keep going.
  return text.replace(/\\"/g, '"').replace(/\\n/g, '\n').replace(/\\t/g, '\t');
}

function snapshotUi(tag) {
  const r = ramus(['snapshot'], { timeout: 60000 });
  if (r.ok && r.stdout) {
    writeFileSync(path.join(OUT, `ui-${tag}.json`), r.stdout);
    // What is on screen is independent evidence: a game UI and the launcher
    // look nothing alike, and it costs one call that already happened.
    result.ui = result.ui || {};
    const pkgRe = new RegExp((process.env.RAMUS_PACKAGE || 'com\\.wind').replace(/\./g, '\\.'), 'i');
    result.ui[tag] = {
      bytes: r.stdout.length,
      mentionsPackage: pkgRe.test(r.stdout),
      looksLikeLauncher: /launcher|home screen|all apps|workspace/i.test(r.stdout),
      head: r.stdout.slice(0, 600),
    };
  }

  // The raw XML names the foreground package in its node attributes, which is
  // the only direct statement about what is actually in front of the user.
  const raw = ramus(['snapshot', '--raw'], { timeout: 60000 });
  if (raw.ok && raw.stdout) {
    writeFileSync(path.join(OUT, `ui-${tag}.xml`), raw.stdout);
    const xml = unwrapXml(raw.stdout);
    const pkgs = [...new Set([...xml.matchAll(/package="([^"]+)"/g)].map((m) => m[1]))];
    const texts = [...new Set([...xml.matchAll(/text="([^"]+)"/g)].map((m) => m[1]))]
      .filter((t) => t.trim()).slice(0, 12);
    result.ui = result.ui || {};
    result.ui[tag] = Object.assign(result.ui[tag] || { bytes: 0 }, {
      packages: pkgs,
      texts,
      // The CLI may answer with JSON, exactly like `logcat` did. Keeping the head
      // means a future format change is visible instead of silently empty.
      head: raw.stdout.slice(0, 300).replace(/\s+/g, ' '),
    });
  }
  return r.ok;
}

// ── system dialogs ─────────────────────────────────────────────────────────

/**
 * Android shows a one-time "Viewing full screen / Got it" confirmation when an
 * app enters immersive mode. It sits in front of the game, keeps the UI dump
 * pointing at com.android.systemui, and holds the frame perfectly still — which
 * is exactly what three identical screenshots looked like.
 *
 * Returns a short description when a dialog was dismissed.
 */
function dismissSystemDialog(tag) {
  // The XML carries pixel bounds, and `tap` also accepts normalised coordinates.
  // Tapping a ref needs a matching `--gen`, which the snapshot generation had
  // already invalidated by the time we act — coordinates do not have that
  // problem ("found \"Got it\" but tap failed" in run 39931344041).
  let xml = '';
  try {
    xml = unwrapXml(readFileSync(path.join(OUT, `ui-${tag}.xml`), 'utf8'));
  } catch {
    return null;
  }

  const wanted = /got it|ok/i;
  const nodes = [...xml.matchAll(/<node\b[^>]*>/g)].map((m) => m[0]);
  let target = null;
  let screen = null;

  for (const node of nodes) {
    const bounds = node.match(/bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"/);
    if (!bounds) continue;
    const [x1, y1, x2, y2] = bounds.slice(1).map(Number);
    if (!screen || x2 > screen[0] || y2 > screen[1]) screen = [x2, y2];
    const text = (node.match(/text="([^"]*)"/) || [])[1] || '';
    if (wanted.test(text) && !target) target = { text, x1, y1, x2, y2 };
  }
  if (!target || !screen) return null;

  const cx = (target.x1 + target.x2) / 2 / screen[0];
  const cy = (target.y1 + target.y2) / 2 / screen[1];
  const point = `${cx.toFixed(3)},${cy.toFixed(3)}`;

  // --expect-gone makes the CLI verify the dismissal instead of trusting it.
  let r = ramus(['tap', point, '--expect-gone', target.text], { timeout: 60000 });
  if (!r.ok) {
    const first = String(r.stderr || r.stdout || '').slice(0, 200);
    r = ramus(['tap', point], { timeout: 60000 });
    if (!r.ok) return `found "${target.text}" at ${point} but tap failed: ${first}`;
    return `tapped "${target.text}" at ${point} (no verification)`;
  }
  return `dismissed "${target.text}" at ${point} (verified gone)`;
}

/**
 * Grab everything the transport will give us about the app, right now.
 *
 * The plain dump is dominated by system chatter and its scrollback evicts app
 * lines within seconds. Calling `--filter` for a handful of needles immediately
 * after an event is the only way the trial transport ever shows app lines —
 * one such query already surfaced `D/VRI[MessagingUnityPlayerActivity]`.
 */
function captureBurst(reason) {
  const pkg = process.env.RAMUS_PACKAGE || 'com.wind.wings.Space.Shooter';
  const needles = [
    ['package', pkg],
    ['unity', 'Unity'],
    ['il2cpp', 'il2cpp'],
    ['androidRuntime', 'AndroidRuntime'],
    ['fatal', 'FATAL'],
    ['anr', 'ANR'],
    ['wind', 'Wind'],
    ['died', 'died'],
  ];
  const hits = {};
  for (const [label, needle] of needles) {
    const rows = logcatFiltered(needle, 500);
    if (Array.isArray(rows) && rows.length) hits[label] = rows.slice(-20);
  }
  const entry = { reason, at: new Date().toISOString(), hits };
  result.bursts = result.bursts || [];
  result.bursts.push(entry);
  note(`logcat burst "${reason}": ${Object.keys(hits).length}/${needles.length} needles hit`);
  return entry;
}

/**
 * Tap through first-run dialogs (Android immersive confirmation, the game's own
 * consent screen, ...). Every tap is verified by a fresh snapshot; the loop stops
 * as soon as nothing matching is on screen.
 *
 * This is what stopped the probe at run 39930806984: the immersive confirmation
 * held the frame still, so three screenshots were byte-identical and the report
 * concluded "the app never started". It had started.
 */
function advanceDialogs(maxSteps = 4) {
  const actionable = /^(got it|ok|continue|allow|accept|i agree|agree|start|next|play)$/i;
  const done = [];
  for (let step = 0; step < maxSteps; step++) {
    const tag = `dialog-${step}`;
    if (!snapshotUi(tag)) break;
    let xml = '';
    try {
      xml = unwrapXml(readFileSync(path.join(OUT, `ui-${tag}.xml`), 'utf8'));
    } catch {
      break;
    }

    const nodes = [...xml.matchAll(/<node\b[^>]*>/g)].map((m) => m[0]);
    let screen = null;
    let target = null;
    for (const node of nodes) {
      const b = node.match(/bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"/);
      if (!b) continue;
      const [x1, y1, x2, y2] = b.slice(1).map(Number);
      if (!screen || x2 > screen[0] || y2 > screen[1]) screen = [x2, y2];
      const text = ((node.match(/text="([^"]*)"/) || [])[1] || '').trim();
      // Prefer the widest match (a real button), ignore empty labels.
      if (text && actionable.test(text) && !target) target = { text, x1, y1, x2, y2 };
    }
    if (!target || !screen) break;

    const point = `${((target.x1 + target.x2) / 2 / screen[0]).toFixed(3)},${((target.y1 + target.y2) / 2 / screen[1]).toFixed(3)}`;
    const r = ramus(['tap', point], { timeout: 60000 });
    if (!r.ok) {
      done.push({ text: target.text, point, after: 'tap failed' });
      break;
    }
    // Let the next screen render before observing it.
    const until = Date.now() + 2500;
    while (Date.now() < until) { /* synchronous wait on purpose */ }

    // Who is in front now? This is what shows the moment the app disappears.
    snapshotUi(`${tag}-after`);
    const after = (result.ui && result.ui[`${tag}-after`] && result.ui[`${tag}-after`].packages) || [];
    screenshot(10 + step);
    const stillFront = after.some((x) => /wind|wings/i.test(x));
    done.push({
      text: target.text,
      point,
      after: after.length ? after.join(', ') : 'unknown',
      appStillFront: stillFront,
    });

    if (!stillFront) {
      // This is the moment the app left the screen. Whatever the transport still
      // holds about it has to be taken now — a second later it is evicted.
      captureBurst(`after tap "${target.text}"`);
      break;
    }
  }
  return done;
}

// ── main ───────────────────────────────────────────────────────────────────

async function main() {
  log(`label="${opt.label}" mode=${MODE} out=${OUT}`);
  if (SESSION) log(`session=${SESSION}`);
  if (MODE === 'trial') {
    note('anonymous trial: no adb tunnel, so the bridge is read through logcat mirrors');
    if (result.trialExpiresAt) note(`trial credential expires at ${result.trialExpiresAt}`);
  }

  // Never let the logcat wait outlive the credential.
  if (opt.budget > 0) {
    result.budgetSeconds = opt.budget;
    if (opt.budget < 300) note(`only ${opt.budget}s of credential budget left`);
    opt.logcatWait = Math.max(20, Math.min(opt.logcatWait, opt.budget - 45));
    opt.waitServer = Math.max(3, Math.min(opt.waitServer, opt.budget - 60));
  }

  if (!opt.offline) {
    sessionStatus();
    screenshot(0);
  }

  // HTTP first — but on a trial there is no tunnel, so only one cheap attempt.
  let health = null;
  if (MODE === 'trial') {
    const quick = await get('/health', 4000);
    if (quick.status === 200) health = quick.json;
  } else {
    health = await waitForBridge(opt.waitServer);
  }

  if (health && opt.waitScene) {
    const waited = await get(`/wait?scene=${encodeURIComponent(opt.waitScene)}&timeout=120000`, 130000);
    log(`wait scene "${opt.waitScene}" → ${waited.json ? JSON.stringify(waited.json) : waited.error}`);
  }

  if (health) {
    result.transport = 'http';
    result.bridge.health = health;

    const calls = {
      state: '/state',
      metrics: '/metrics',
      scene: '/scene?max=200',
      hierarchy: '/hierarchy?depth=3&max=1500',
      findSub: '/find?name=Sub&max=40',
      findBoard: '/find?name=Board&max=40',
      logs: '/logs?n=150',
    };
    for (const [key, url] of Object.entries(calls)) {
      const r = await get(url, 15000);
      if (r.json) result.bridge[key] = r.json;
      else fail(`GET ${url}`, r.error || `status ${r.status}`);
    }

    // Game state via reflection — one call per type, keep going if one fails.
    const types = opt.statics.split(',').map((t) => t.trim()).filter(Boolean).slice(0, 12);
    result.bridge.staticsByType = {};
    for (const type of types) {
      const r = await get(`/statics?type=${encodeURIComponent(type)}&max=200`, 15000);
      if (r.json && r.json.ok) {
        result.bridge.staticsByType[type] = r.json;
        const n = r.json.written ?? Object.keys(r.json.fields || {}).length;
        log(`statics ${type}: ${n} field(s)`);
      } else if (r.json) {
        note(`statics ${type}: ${r.json.error || 'not ok'}`);
      } else {
        fail(`GET /statics?type=${type}`, r.error || `status ${r.status}`);
      }
    }
    result.bridge.statics = Object.values(result.bridge.staticsByType)[0] || {};

    const shot = await get('/screenshot', 20000);
    if (shot.image && shot.image.length > 100) {
      const file = path.join(OUT, 'screen-ingame.png');
      writeFileSync(file, shot.image);
      result.screenshots.push(path.basename(file));
    } else if (shot.error) {
      fail('GET /screenshot', shot.error);
    }
  } else {
    if (MODE === 'trial') {
      note(`bridge HTTP not reachable at ${opt.base} (expected on a trial: no adb) — reading logcat`);
    } else {
      fail(`bridge unreachable at ${opt.base}`, 'falling back to logcat');
    }

    const states = await waitForLogcat(opt.logcatWait);
    if (states.length > 0) {
      result.transport = 'logcat';
      result.bridge.health = states[states.length - 1].state;
      note(`recovered ${states.length} RAMUSB state line(s) from logcat`);
    } else {
      fail('no RAMUSB logcat line found', 'is RamusBridge.dll inside this APK? see runtime-probe/README.md');
    }
  }

  if (!opt.offline) {
    snapshotUi('before');
    if (opt.screenshots > 1) screenshot(1);

    // The immersive-mode confirmation blocks the view of the game itself.
    const dismissed = dismissSystemDialog('before');
    if (dismissed) {
      note(`system dialog: ${dismissed}`);
      result.dialog = dismissed;
    } else {
      note('no immersive/system dialog found on screen');
    }
    // Then tap through whatever the game itself puts up (consent, "play", ...).
    const advanced = advanceDialogs();
    if (advanced.length) {
      result.dialogs = advanced;
      note(`tapped through: ${advanced.join(' → ')}`);
    }
    snapshotUi('after-dialog');
    screenshot(2);

    // If the app already left, ask one question: is it reproducible? Relaunch and
    // watch for ~8 s. A second death at the same point is a crash loop; staying up
    // would mean the first exit was a one-off.
    const afterPkgs = (result.ui['after-dialog'] && result.ui['after-dialog'].packages) || [];
    if (!afterPkgs.some((x) => /wind|wings/i.test(x))) {
      note('app is not in the foreground — relaunching once to test reproducibility');
      const rel = ramus(['app', 'launch'], { timeout: 60000 });
      const t0 = Date.now();
      let cameBack = false;
      let wentAway = null;
      for (let i = 0; i < 8; i++) {
        const until = Date.now() + 1000;
        while (Date.now() < until) { /* wait one second between observations */ }
        const tag = `relaunch-${i}`;
        if (!snapshotUi(tag)) continue;
        const pk = (result.ui[tag] && result.ui[tag].packages) || [];
        const front = pk.some((x) => /wind|wings/i.test(x));
        if (front && !cameBack) cameBack = true;
        if (cameBack && !front) { wentAway = Math.round((Date.now() - t0) / 1000); break; }
      }
      screenshot(20);
      result.relaunch = {
        ok: rel.ok,
        cameBack,
        diedAfterSeconds: wentAway,
        aliveAfterSeconds: cameBack && wentAway == null ? 8 : null,
      };
      note(`relaunch: cameBack=${cameBack} diedAfter=${wentAway ?? 'n/a'}s`);
      captureBurst('after relaunch');
    }
  }

  // The plain dump is the last 500 lines of everything, which on a fresh boot is
  // almost entirely system spam. These two queries look at the whole scrollback.
  const pkgName = process.env.RAMUS_PACKAGE || 'com.wind.wings.Space.Shooter';
  result.logcat.filtered = opt.offline ? null : {
    package: logcatFiltered(pkgName),
    unity: logcatFiltered('Unity'),
    androidRuntime: logcatFiltered('AndroidRuntime'),
  };

  readLogcatStates();

  // ── verdict ──
  const h = result.bridge.health || {};
  const scene = h.scene || (result.bridge.scene && result.bridge.scene.name) || '';
  const fps = Number(h.fps || 0);
  const reachable = result.transport !== 'none';
  const crashed = result.errors.some((e) => /crash|died|not running/i.test(e));

  result.budgetSeconds = opt.budget || null;
  // Did the process even start? Decides "bridge missing" vs "game crashed".
  const rawLog = result.logcat.rawAll || '';
  const pkgRe = new RegExp((process.env.RAMUS_PACKAGE || 'com.wind').replace(/\./g, '\\.'), 'i');
  // Only real app-level failures: Ramus's own screenshot tooling logs through
  // AndroidRuntime too ("Using default boot image", uiautomator), which used to
  // show up as if the game had crashed.
  const NOISE_RE = /uiautomator|Using default boot image|lock profiling|com\.android\.commands|Shutting down VM|app_process|ClassLoaderContext/i;
  const CRASH_RE = /FATAL EXCEPTION|UnsatisfiedLinkError|NO_MATCHING_ABIS|dlopen failed|SIGSEGV|is 32-bit instead of 64-bit/i;
  const signals = {
    // "UnityPlayerActivity" is not a Unity log — require an actual Unity tag/version.
    unity: /[VDIWE]\/Unity\s*:|UnityMain|Unity\s*\d{4}\.\d|il2cpp_init|libunity\.so/i.test(rawLog),
    il2cpp: /il2cpp/i.test(rawLog),
    package: pkgRe.test(rawLog),
    nativeFailure: /UnsatisfiedLinkError|NO_MATCHING_ABIS|dlopen failed|SIGSEGV|is 32-bit instead of 64-bit/i.test(rawLog),
    fatal: /FATAL EXCEPTION/i.test(rawLog),
    // Proof that the system actually started the activity, independent of logcat noise.
    foreground: new RegExp(`Displayed (${pkgRe.source})|Start proc [0-9]+:(${pkgRe.source})`, 'i').test(rawLog),
    activityManager: /ActivityTaskManager|ActivityManager/i.test(rawLog),
    // A full-screen confirmation is only raised for an app that is on screen.
    immersiveDialog: /Viewing full screen|To exit, swipe down/i.test(
      JSON.stringify(result.ui || {}) + rawLog),

    // ── what the device says about itself and about this app ──────────────
    // Seen in the live device console on 23/10: the emulator is x86_64 while the
    // APK ships only lib/arm64 — yet the app ran, so a translation layer exists.
    deviceX86: /Unexpected CPU variant for x86: x86_64|\/lib\/x86_64|\/lib\/x86\//.test(rawLog),
    deviceArm64: /\/lib\/arm64|arm64-v8a|ro\.product\.cpu\.abi/.test(rawLog),
    // nativeloader prints the library path it configured for the app's APK.
    appLibPath: (rawLog.match(/library_path=([^,\s]*(?:arm64|x86)[^,\s]*)/i) || [])[1] || null,
    // DNS refused for an app uid: the game cannot reach its backend or consent host.
    networkBlocked: /network access blocked/i.test(rawLog),
    // WindowManager closes the app's task with a timestamp — the moment it went.
    taskClose: (rawLog.match(/type = CLOSE[\s\S]{0,4000}?cmp=([^/\s]+)\/([^\s},]+)/i) || [])
      .slice(1).join('/') || null,
    excerpts: rawLog
      .split('\n')
      .filter((l) => CRASH_RE.test(l) && !NOISE_RE.test(l))
      .slice(-4)
      .map((l) => l.trim().slice(0, 220)),
  };

  // ── logcat evidence: what the device said, not just which regexes matched ──
  const all = rawLog.split('\n').filter((l) => l.trim());
  const tags = new Map();
  for (const line of all) {
    // "10-23 08:12:42.123  1234  1234 I Unity   : msg" and "I/Unity(1234): msg"
    const m = line.match(/\s[VDIWEF]\/([A-Za-z0-9_.\-]+)/) || line.match(/\s[VDIWEF]\s+([A-Za-z0-9_.\-]+)\s*:/);
    const tag = m ? m[1] : 'other';
    tags.set(tag, (tags.get(tag) || 0) + 1);
  }
  signals.logcat = {
    lines: all.length,
    bytes: rawLog.length,
    // Which buffers the transport returned (`system` only on a trial run so far).
    streams: result.logcat.streams || null,
    topTags: [...tags.entries()].sort((a, b) => b[1] - a[1]).slice(0, 12),
    packageLines: all.filter((l) => pkgRe.test(l)).slice(-6).map((l) => l.slice(0, 200)),
    head: all.slice(0, 6).map((l) => l.slice(0, 200)),
    tail: all.slice(-25).map((l) => l.slice(0, 200)),
  };
  result.app = {
    signals,
    scene,
    fps,
    frame: h.frame ?? null,
    uptime: h.uptime ?? null,
    package: process.env.RAMUS_PACKAGE || 'com.wind.wings.Space.Shooter',
    sessionAlive: !crashed,
  };

  if (!reachable) result.verdict = 'bridge-unreachable';
  else if (crashed) result.verdict = 'app-unstable';
  else if (fps > 0 && fps < 20) result.verdict = 'degraded';
  else result.verdict = 'ok';

  // ── write artefacts ──
  writeFileSync(path.join(OUT, 'summary.json'), JSON.stringify(result, null, 2));
  writeFileSync(path.join(OUT, 'report.md'), renderReport(result));
  log(`verdict=${result.verdict} transport=${result.transport} scene="${scene}" fps=${fps}`);
  if (process.env.GITHUB_STEP_SUMMARY) {
    try {
      appendFileSync(process.env.GITHUB_STEP_SUMMARY, renderReport(result));
    } catch { /* summary is best-effort */ }
  }

  if (opt.strict && !reachable) process.exitCode = 1;
}

function renderReport(r) {
  const sigPkg = (r.app && r.app.package) || process.env.RAMUS_PACKAGE || 'com.wind.wings.Space.Shooter';
  const h = r.bridge.health || {};
  const sc = r.bridge.scene || {};
  const st = r.bridge.statics || {};
  const mirrorRoots = Array.isArray(h.roots) ? h.roots : [];
  const roots = Array.isArray(sc.roots) && sc.roots.length ? sc.roots.length : (h.rootCount ?? mirrorRoots.length);
  const subs = r.bridge.findSub && typeof r.bridge.findSub.count === 'number' ? r.bridge.findSub.count : '—';
  const logs = Array.isArray(r.bridge.logs && r.bridge.logs.logs) ? r.bridge.logs.logs.length : 0;
  const trial = r.mode === 'trial';

  const lines = [];
  lines.push(`# Runtime probe — ${r.label}`);
  lines.push('');
  lines.push(`- **verdict:** \`${r.verdict}\``);
  lines.push(`- **mode:** \`${r.mode}\`${trial ? ' (anonymous trial — no adb)' : ' (signed-in key)'}`);
  lines.push(`- **transport:** \`${r.transport}\` (${r.transport === 'http' ? 'adb forward → 127.0.0.1:8080' : r.transport === 'logcat' ? 'logcat mirror (RAMUSB)' : 'none'})`);
  lines.push(`- **started:** ${r.startedAt}`);
  lines.push(`- **session:** \`${r.session || 'n/a'}\``);
  if (r.trialExpiresAt) lines.push(`- **trial expires:** ${r.trialExpiresAt}`);
  lines.push('');
  lines.push('| metric | value |');
  lines.push('| --- | --- |');
  lines.push(`| scene | \`${h.scene ?? '—'}\` |`);
  lines.push(`| fps | ${h.fps ?? '—'} |`);
  lines.push(`| avg / max frame | ${fmt(h.avgFrameMs)} / ${fmt(h.maxFrameMs)} ms |`);
  lines.push(`| frame count | ${h.frame ?? '—'} |`);
  lines.push(`| uptime | ${fmt(h.uptime)} s |`);
  lines.push(`| unity | \`${h.unity ?? '—'}\` |`);
  lines.push(`| platform | \`${h.platform ?? '—'}\` |`);
  lines.push(`| timeScale | ${h.timeScale ?? h.ts ?? '—'} |`);
  lines.push(`| root objects | ${roots} |`);
  lines.push(`| objects named *Sub* | ${subs} |`);
  lines.push(`| in-game log lines | ${logs} |`);
  lines.push(`| logcat RAMUSB lines | ${r.logcat.states.length} |`);
  lines.push('');

  if (mirrorRoots.length && !(Array.isArray(sc.roots) && sc.roots.length)) {
    lines.push('## Scene roots (from the logcat mirror)');
    lines.push('');
    lines.push('| # | name | active |');
    lines.push('| --- | --- | --- |');
    mirrorRoots.slice(0, 20).forEach((n, i) => {
      lines.push(`| ${i} | \`${n.n}\` | ${n.a} |`);
    });
    if ((h.rootCount ?? 0) > mirrorRoots.length) lines.push('');
    if ((h.rootCount ?? 0) > mirrorRoots.length) lines.push(`_… ${h.rootCount - mirrorRoots.length} more root object(s) not mirrored (\`mirror_roots\`)._`);
    lines.push('');
  }

  if (Array.isArray(sc.roots) && sc.roots.length) {
    lines.push('## Scene roots');
    lines.push('');
    lines.push('| # | name | active | children | components |');
    lines.push('| --- | --- | --- | --- | --- |');
    sc.roots.slice(0, 20).forEach((n, i) => {
      lines.push(`| ${i} | \`${n.name}\` | ${n.active} | ${n.children} | ${(n.components || []).join(', ')} |`);
    });
    lines.push('');
  }

  const byType = r.bridge.staticsByType || (st && st.fields ? { [st.type || 'statics']: st } : {});
  const typeNames = Object.keys(byType).filter((k) => byType[k] && byType[k].fields && Object.keys(byType[k].fields).length);
  if (typeNames.length) {
    lines.push('## Static game state (`/statics`)');
    lines.push('');
    for (const type of typeNames) {
      lines.push(`### \`${type}\``);
      lines.push('');
      for (const [k, v] of Object.entries(byType[type].fields).slice(0, 30)) {
        lines.push(`- \`${k}\` = ${JSON.stringify(v)}`);
      }
      lines.push('');
    }
  }

  if (r.screenshots.length) {
    lines.push('## Artifacts');
    lines.push('');
    for (const s of r.screenshots) lines.push(`- \`${s}\``);
    lines.push('- `summary.json` — full payloads (health, scene, hierarchy, logs)');
    lines.push('');
  }

  const sig = r.app.signals;
  let sigAbis = 'unknown';
  try {
    const inv = readFileSync(path.join(OUT, 'apk-inventory.txt'), 'utf8');
    const m = inv.match(/^abis:\s*(.+?)\s+\+/m) || inv.match(/^abis:\s*(\S+)/m);
    if (m) sigAbis = m[1].trim();
  } catch { /* inventory optional */ }
  if (sig) {
    lines.push('## Did the app start?');
    lines.push('');
    lines.push('| signal | seen in logcat |');
    lines.push('| --- | --- |');
    lines.push(`| Unity banner | ${yn(sig.unity)} |`);
    lines.push(`| il2cpp | ${yn(sig.il2cpp)} |`);
    lines.push(`| package mentioned | ${yn(sig.package)} |`);
    lines.push(`| native load failure | ${yn(sig.nativeFailure)} |`);
    lines.push(`| fatal exception | ${yn(sig.fatal)} |`);
    lines.push(`| activity started (Displayed/Start proc) | ${yn(sig.foreground)} |`);
    lines.push(`| immersive full-screen dialog (app was in front) | ${yn(sig.immersiveDialog)} |`);
    lines.push(`| device is x86_64 | ${yn(sig.deviceX86)} |`);
    lines.push(`| device also advertises arm64 | ${yn(sig.deviceArm64)} |`);
    if (sig.appLibPath) lines.push(`| app library path | \`${String(sig.appLibPath).slice(0, 120)}\` |`);
    lines.push(`| network blocked (DNS refused) | ${sig.networkBlocked ? '**yes**' : 'no'} |`);
    if (sig.taskClose) lines.push(`| window manager closed this task | \`${sig.taskClose}\` |`);
    lines.push('');
    if (Array.isArray(sig.excerpts) && sig.excerpts.length) {
      lines.push('```');
      for (const e of sig.excerpts) lines.push(e);
      lines.push('```');
      lines.push('');
    }

    if (r.launch) {
      lines.push(`app launch: ${r.launch.ok ? 'ok' : 'failed (exit ' + r.launch.code + ')'}`);
      const out = (r.launch.stderr || r.launch.stdout || '').trim();
      if (out) {
        lines.push('```');
        lines.push(out.slice(0, 400));
        lines.push('```');
      }
      lines.push('');
    }

    if (r.relaunch) {
      const rel = r.relaunch;
      lines.push('### Relaunch test');
      lines.push('');
      lines.push(`| relaunch sent | came back | died after | alive at end |`);
      lines.push('| --- | --- | --- | --- |');
      lines.push(`| ${rel.ok ? 'ok' : 'failed'} | ${yn(rel.cameBack)} | ${
        rel.diedAfterSeconds != null ? rel.diedAfterSeconds + ' s' : '—'} | ${
        rel.aliveAfterSeconds != null ? '≥ 8 s' : 'no'} |`);
      lines.push('');
      if (rel.cameBack && rel.diedAfterSeconds != null) {
        lines.push(`> **Reproducible.** The app started again and left the screen after ~${
          rel.diedAfterSeconds}s — same behaviour as the first run.`);
        lines.push('');
      }
    }

    if (Array.isArray(r.bursts) && r.bursts.length) {
      for (const b of r.bursts) {
        const keys = Object.keys(b.hits || {});
        lines.push(`<details><summary>logcat burst — ${b.reason} (${keys.length} needle(s) hit)</summary>`);
        lines.push('');
        if (!keys.length) {
          lines.push('_No app-related line in any buffer the transport exposes._');
        }
        for (const k of keys) {
          lines.push(`**${k}**`);
          lines.push('```');
          for (const l of b.hits[k]) lines.push(String(l).slice(0, 220));
          lines.push('```');
        }
        lines.push('</details>');
        lines.push('');
      }
    }

    if (Array.isArray(r.dialogs) && r.dialogs.length) {
      lines.push('| # | tapped | at | foreground after | app still in front |');
      lines.push('| --- | --- | --- | --- | --- |');
      r.dialogs.forEach((d, i) => {
        if (typeof d === 'string') {
          lines.push(`| ${i} | ${d} | | | |`);
          return;
        }
        lines.push(`| ${i} | ${d.text} | ${d.point} | \`${d.after}\` | ${
          d.appStillFront == null ? '—' : yn(d.appStillFront)} |`);
      });
      lines.push('');
      const lost = r.dialogs.findIndex((d) => typeof d === 'object' && d.appStillFront === false);
      if (lost >= 0) {
        lines.push(`> **The app left the foreground after tap ${lost}.** The UI tree then`);
        lines.push('> belonged to another package, so the game finished or died at that point.');
        lines.push('> The trial transport exposes no `main`/`crash` buffer, so the reason is not');
        lines.push('> in this report — that needs adb (key mode).');
        lines.push('');
      }
    }

    if (r.dialog) {
      lines.push(`> **System dialog:** ${r.dialog}`);
      lines.push('>');
      lines.push('> An immersive-mode confirmation ("Viewing full screen") is shown by Android');
      lines.push('> when an app goes full-screen. Its presence means the app reached the point');
      lines.push('> of requesting immersive mode — it was in the foreground.');
      lines.push('');
    }

    if (Array.isArray(r.screens) && r.screens.length) {
      lines.push('| screenshot | bytes | sha256 | unchanged |');
      lines.push('| --- | --- | --- | --- |');
      for (const sc of r.screens) {
        lines.push(`| ${sc.file} | ${sc.bytes} | \`${sc.sha256}\` | ${sc.sameAsPrevious == null ? '—' : yn(sc.sameAsPrevious)} |`);
      }
      lines.push('');
      const still = r.screens.filter((x) => x.sameAsPrevious === true).length;
      if (r.screens.length > 1 && still === r.screens.length - 1) {
        lines.push('> **The screen never changed** between the two shots. Combined with');
        lines.push('> `app launch: ok`, that means the CLI accepted the request but the');
        lines.push('> foreground window did not become the game.');
        lines.push('');
      }
    }

    if (r.sessionStatus) {
      lines.push('<details><summary>session status (full)</summary>');
      lines.push('');
      lines.push('```json');
      lines.push(JSON.stringify(r.sessionStatus, null, 2).slice(0, 1800));
      lines.push('```');
      lines.push('</details>');
      lines.push('');
    }

    // What is on screen — a game UI and a launcher look nothing alike.
    if (r.ui && Object.keys(r.ui).length) {
      lines.push('| ui snapshot | value |');
      lines.push('| --- | --- |');
      for (const [tag, v] of Object.entries(r.ui)) {
        const pkgs = Array.isArray(v.packages) && v.packages.length ? v.packages.join(', ') : '—';
        const onlySystem = Array.isArray(v.packages) && v.packages.length > 0
          && v.packages.every((x) => /systemui/i.test(x));
        lines.push(`| ${tag} | ${v.bytes} B · packages: \`${pkgs}\` · mentions app: ${yn(v.mentionsPackage)} · looks like launcher: ${yn(v.looksLikeLauncher)} |`);
        if (Array.isArray(v.texts) && v.texts.length) {
          lines.push(`| | text on screen: ${v.texts.map((t) => `\`${String(t).slice(0, 40)}\``).join(' · ')} |`);
        }
        if (onlySystem) {
          lines.push('| | *only SystemUI — a dialog or overlay is covering the app* |');
        }
      }
      lines.push('');
    }

    // --filter looks past the last-500-line window instead of inside it.
    const fl = r.logcat && r.logcat.filtered;
    if (fl) {
      for (const [key, rows] of Object.entries(fl)) {
        if (!Array.isArray(rows)) continue;
        lines.push(`<details><summary>logcat --filter ${key} — ${rows.length} line(s)</summary>`);
        lines.push('');
        lines.push('```');
        for (const l of rows.slice(-40)) lines.push(l.slice(0, 200));
        lines.push('```');
        lines.push('</details>');
        lines.push('');
      }
    }

    // Raw device output. Without this the report only says which regexes did not
    // match, which cannot distinguish "never launched" from "crashed silently".
    const lc = sig.logcat;
    if (lc && lc.lines) {
      lines.push(`<details><summary>logcat evidence — ${lc.lines} line(s), ${lc.bytes} B</summary>`);
      lines.push('');
      if (lc.topTags && lc.topTags.length) {
        lines.push('tag histogram:');
        lines.push('```');
        for (const [tag, n] of lc.topTags) lines.push(`${String(n).padStart(5)}  ${tag}`);
        lines.push('```');
        lines.push('');
      }
      if (lc.packageLines && lc.packageLines.length) {
        lines.push(`lines mentioning \`${sigPkg}\` (last ${lc.packageLines.length}):`);
        lines.push('```');
        for (const l of lc.packageLines) lines.push(l);
        lines.push('```');
        lines.push('');
      }
      lines.push('first 6 lines:');
      lines.push('```');
      for (const l of lc.head || []) lines.push(l);
      lines.push('```');
      lines.push('last 25 lines:');
      lines.push('```');
      for (const l of lc.tail || []) lines.push(l);
      lines.push('```');
      lines.push('</details>');
      lines.push('');
    }
    const streams = (sig.logcat && sig.logcat.streams) || null;
    if (streams) {
      const parts = Object.entries(streams).map(([k, v]) => `${k}=${v}`).join(', ');
      lines.push(`streams returned: ${parts}`);
      lines.push('');
      if (!streams.main && !streams.crash) {
        lines.push('> **Transport limitation, not a result.** Every line came from the `system`');
        lines.push('> buffer; Unity, ActivityManager and crash reports go to `main`/`crash`.');
        lines.push('> With no `main` lines, "no Unity" / "no package" says nothing about the game —');
        lines.push('> it only says this transport never looked at the buffer where the game logs.');
        lines.push('');
      }
    }

    if (!sig.package && !sig.unity) {
      lines.push('> **Not proven:** no Unity or package line appeared in the last 500 logcat lines.');
      lines.push('> That is consistent with the game never starting, but it does not identify the');
      lines.push('> cause. Candidates, none confirmed by this run:');
      lines.push('>');
      lines.push('> - ABI mismatch — this build ships `lib/arm64-v8a` only and Ramus documents');
      lines.push(`>   x86_64 emulators (ABI in this APK: \`${sigAbis}\`);`);
      lines.push('> - the launcher never started the activity (`ramus app launch` is best effort);');
      lines.push('> - the process died before Unity initialised, with the crash outside the captured');
      lines.push('>   window — `logcat` only returns the last 500 lines.');
      lines.push('>');
      lines.push('> To decide it, capture `adb logcat` on a device that has adb, or read');
      lines.push('> `logcat.txt` in the artifact in full.');
      lines.push('');
    }
  }

  if (r.notes.length) {
    lines.push('## Notes');
    lines.push('');
    for (const n of r.notes) lines.push(`- ${n}`);
    lines.push('');
  }

  if (r.errors.length) {
    lines.push('## Errors');
    lines.push('');
    for (const e of r.errors.slice(0, 30)) lines.push(`- ${e}`);
    if (r.errors.length > 30) lines.push(`- … ${r.errors.length - 30} more (see summary.json)`);
    lines.push('');
  }

  if (trial && r.transport === 'logcat') {
    lines.push('> Trial runs only get scene / fps / frame / timeScale / root object names. Hierarchy, components and');
    lines.push('> `/statics` need the HTTP path, which needs an adb tunnel (`RAMUS_API_KEY`).');
    lines.push('');
  }

  lines.push('---');
  lines.push('');
  lines.push('Generated by `runtime-probe/` (embedded C# bridge + `ramus-probe.mjs`).');
  return `${lines.join('\n')}\n`;
}

const yn = (v) => (v ? '**yes**' : 'no');

const fmt = (v) => (typeof v === 'number' ? Math.round(v * 100) / 100 : (v ?? '—'));

main().catch((e) => {
  result.errors.push(`fatal: ${e && e.stack ? e.stack.split('\n')[0] : String(e)}`);
  result.verdict = 'error';
  try {
    mkdirSync(OUT, { recursive: true });
    writeFileSync(path.join(OUT, 'summary.json'), JSON.stringify(result, null, 2));
    writeFileSync(path.join(OUT, 'report.md'), renderReport(result));
  } catch { /* nothing else we can do */ }
  console.error(e);
  process.exitCode = 1;
});
