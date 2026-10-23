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
import { appendFileSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
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

function readLogcatStates(limit = 500) {
  // The CLI rejects --limit > 500 ("limit must be at most 500").
  const r = ramus(['logcat', '--limit', String(Math.min(limit, 500))]);
  const text = `${r.stdout}\n${r.stderr}`;
  result.logcat.rawAll = text;
  if (r.ok) {
    try { writeFileSync(path.join(OUT, 'logcat.txt'), text); } catch { /* best effort */ }
  }
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
      const r = ramus(['app', 'launch']);
      if (r.ok) note('sent `app launch` because no bridge line appeared yet');
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

  screenshot(0);

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

  snapshotUi('before');
  if (opt.screenshots > 1) screenshot(1);

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
    excerpts: rawLog
      .split('\n')
      .filter((l) => CRASH_RE.test(l) && !NOISE_RE.test(l))
      .slice(-4)
      .map((l) => l.trim().slice(0, 220)),
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
    lines.push('');
    if (Array.isArray(sig.excerpts) && sig.excerpts.length) {
      lines.push('```');
      for (const e of sig.excerpts) lines.push(e);
      lines.push('```');
      lines.push('');
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
