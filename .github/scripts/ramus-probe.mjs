#!/usr/bin/env node
/**
 * ramus-probe.mjs — drive a Ramus Android session against a running Unity build
 * that has RamusBridge embedded, and write a machine-readable + human report.
 *
 *   node .github/scripts/ramus-probe.mjs --out reports/probe --label "PR #12"
 *
 * Two data paths, tried in order:
 *   1. HTTP  —  adb forward tcp:8080 tcp:8080  (needs an adb tunnel: RAMUS_API_KEY plan)
 *   2. logcat — lines emitted by the bridge every N seconds: `${'RAMUSB'}|{json}`
 *               (works on trial sessions, which have no adb)
 *
 * Exit code is 0 unless --strict is passed and neither path produced data.
 */

import { spawnSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
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
  else if (a === '--screenshots') opt.screenshots = Number(next());
  else if (a === '--help' || a === '-h') {
    console.log('usage: ramus-probe.mjs [--out DIR] [--label TEXT] [--base URL] [--wait-server SEC] [--wait-scene NAME] [--strict]');
    process.exit(0);
  }
}

const CLI = process.env.RAMUS_CLI || 'ramus-cli@0.1.17';
const SESSION = process.env.RAMUS_SESSION || '';
const OUT = path.resolve(opt.out);
mkdirSync(OUT, { recursive: true });

const result = {
  label: opt.label,
  startedAt: new Date().toISOString(),
  base: opt.base,
  transport: 'none',
  session: SESSION || null,
  app: {},
  bridge: {},
  logcat: { raw: [], states: [] },
  screenshots: [],
  errors: [],
  verdict: 'unknown',
};

const log = (msg) => console.log(`[probe] ${msg}`);
const fail = (msg, extra) => {
  result.errors.push(extra === undefined ? msg : `${msg}: ${extra}`);
  log(`ERROR ${msg}${extra === undefined ? '' : ` — ${extra}`}`);
};

// ── ramus cli ──────────────────────────────────────────────────────────────

function ramus(args, { allowFail = true, timeout = 180000 } = {}) {
  const full = [...args, ...(SESSION ? ['--session', SESSION] : [])];
  const r = spawnSync(process.platform === 'win32' ? 'npx.cmd' : 'npx', ['--yes', CLI, ...full], {
    encoding: 'utf8',
    timeout,
    maxBuffer: 32 * 1024 * 1024,
  });
  const out = (r.stdout || '').trim();
  const err = (r.stderr || '').trim();
  if (r.status !== 0 && !allowFail) throw new Error(`ramus ${args[0]} failed (${r.status}): ${err || out}`);
  if (r.status !== 0) result.errors.push(`ramus ${args.join(' ')} → exit ${r.status}: ${(err || out).slice(0, 400)}`);
  return { ok: r.status === 0, stdout: out, stderr: err, status: r.status };
}

function ramusJson(args) {
  const r = ramus(args);
  if (!r.ok || !r.stdout) return null;
  try {
    const start = r.stdout.indexOf('{');
    return start >= 0 ? JSON.parse(r.stdout.slice(start)) : null;
  } catch {
    return null;
  }
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

function readLogcatStates(limit = 800) {
  const r = ramus(['logcat', '--limit', String(limit)]);
  const text = `${r.stdout}\n${r.stderr}`;
  result.logcat.raw = text.split('\n').filter((l) => l.includes('RAMUSB')).slice(-120);
  const states = [];
  for (const line of text.split('\n')) {
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

// ── screenshots / ui ───────────────────────────────────────────────────────

function screenshot(n) {
  const file = path.join(OUT, `screen-${String(n).padStart(2, '0')}.jpg`);
  const r = ramus(['screenshot', '--out', file]);
  if (r.ok) result.screenshots.push(path.basename(file));
  return r.ok;
}

function snapshotUi(tag) {
  const r = ramus(['snapshot'], { timeout: 60000 });
  if (r.ok && r.stdout) writeFileSync(path.join(OUT, `ui-${tag}.json`), r.stdout);
  return r.ok;
}

// ── main ───────────────────────────────────────────────────────────────────

async function main() {
  log(`label="${opt.label}" out=${OUT}`);
  if (SESSION) log(`session=${SESSION}`);

  screenshot(0);

  // Try the HTTP path first.
  let health = await waitForBridge(opt.waitServer);
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
      statics: '/statics?type=Stage_Datas&max=200',
      logs: '/logs?n=150',
    };
    for (const [key, url] of Object.entries(calls)) {
      const r = await get(url, 15000);
      if (r.json) result.bridge[key] = r.json;
      else fail(`GET ${url}`, r.error || `status ${r.status}`);
    }

    // PNG straight from the game (handy when Ramus screenshots are JPEG-only).
    const shot = await get('/screenshot', 20000);
    if (shot.image && shot.image.length > 100) {
      const file = path.join(OUT, 'screen-ingame.png');
      writeFileSync(file, shot.image);
      result.screenshots.push(path.basename(file));
    } else if (shot.error) {
      fail('GET /screenshot', shot.error);
    }
  } else {
    // Fall back to logcat mirroring.
    fail(`bridge unreachable at ${opt.base}`, 'falling back to logcat');
    const states = readLogcatStates();
    if (states.length > 0) {
      result.transport = 'logcat';
      result.bridge.health = states[states.length - 1].state;
      log(`recovered ${states.length} RAMUSB state line(s) from logcat`);
    }
  }

  snapshotUi('before');
  if (opt.screenshots > 1) screenshot(1);

  // Collect a second logcat slice regardless — it explains crashes and scene loads.
  readLogcatStates();

  // ── verdict ──
  const h = result.bridge.health || {};
  const scene = h.scene || (result.bridge.scene && result.bridge.scene.name) || '';
  const fps = Number(h.fps || 0);
  const reachable = result.transport !== 'none';
  const crashed = result.errors.some((e) => /crash|died|not running/i.test(e));

  result.app = {
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
      const { appendFileSync } = await import('node:fs');
      appendFileSync(process.env.GITHUB_STEP_SUMMARY, renderReport(result));
    } catch { /* summary is best-effort */ }
  }

  if (opt.strict && !reachable) process.exitCode = 1;
}

function renderReport(r) {
  const h = r.bridge.health || {};
  const sc = r.bridge.scene || {};
  const m = r.bridge.metrics || {};
  const st = r.bridge.statics || {};
  const roots = Array.isArray(sc.roots) ? sc.roots.length : 0;
  const subs = r.bridge.findSub && typeof r.bridge.findSub.count === 'number' ? r.bridge.findSub.count : '—';
  const logs = Array.isArray(r.bridge.logs && r.bridge.logs.logs) ? r.bridge.logs.logs.length : 0;

  const lines = [];
  lines.push(`# Runtime probe — ${r.label}`);
  lines.push('');
  lines.push(`- **verdict:** \`${r.verdict}\``);
  lines.push(`- **transport:** \`${r.transport}\` (${r.transport === 'http' ? 'adb forward → 127.0.0.1:8080' : r.transport === 'logcat' ? 'logcat mirror (RAMUSB)' : 'none'})`);
  lines.push(`- **started:** ${r.startedAt}`);
  lines.push(`- **session:** \`${r.session || 'n/a'}\``);
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
  lines.push(`| timeScale | ${h.timeScale ?? '—'} |`);
  lines.push(`| root objects (cap 200) | ${roots} |`);
  lines.push(`| objects named *Sub* | ${subs} |`);
  lines.push(`| in-game log lines | ${logs} |`);
  lines.push(`| logcat RAMUSB lines | ${r.logcat.states.length} |`);
  lines.push('');

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

  if (st.fields && typeof st.fields === 'object' && Object.keys(st.fields).length) {
    lines.push('## Static game state (`/statics?type=Stage_Datas`)');
    lines.push('');
    for (const [k, v] of Object.entries(st.fields).slice(0, 25)) lines.push(`- \`${k}\` = ${JSON.stringify(v)}`);
    lines.push('');
  }

  if (r.screenshots.length) {
    lines.push('## Artifacts');
    lines.push('');
    for (const s of r.screenshots) lines.push(`- \`${s}\``);
    lines.push('- `summary.json` — full payloads (health, scene, hierarchy, logs)');
    lines.push('');
  }

  if (r.errors.length) {
    lines.push('## Errors');
    lines.push('');
    for (const e of r.errors.slice(0, 30)) lines.push(`- ${e}`);
    if (r.errors.length > 30) lines.push(`- … ${r.errors.length - 30} more (see summary.json)`);
    lines.push('');
  }

  lines.push('---');
  lines.push('');
  lines.push('Generated by `runtime-probe/` (embedded C# bridge + `ramus-probe.mjs`).');
  return `${lines.join('\n')}\n`;
}

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
