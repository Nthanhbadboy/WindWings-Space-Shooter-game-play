#!/usr/bin/env python3
"""Report 173: stop the audit from drifting, and write the unblock contract.

170 taught `open_items_audit` to read 168/169 by hand. That fixes today's snapshot
and guarantees next week's drift: the audit can only see reports somebody remembered
to add. This gate is the mechanical half of the fix — it reads **every** lane artifact,
collects the statements that name an audit item (`n`) or overturn an earlier report, and
fails when one of them is not reflected in the audit.

Five rules, each of which 168 would have broken before 170 ran:

* `R1 coverage` — an artifact that names item numbers must map to a report the audit knows.
* `R2 closure`  — `closed[n]` must appear as that item's verdict, closed by that report.
* `R3 correction` — `corrected[n]` must be visible: in `records`, a restatement, or the reason.
* `R4 blocker`  — `blocked[n]` must not be closed by the same report that calls it blocked.
* `R5 target`   — a report-level correction must point at a report the audit can name.

The artifact also carries the **unblock contract**: for every item still open or
narrowed, the exact step that would settle it and who can take that step. Two of them
cannot be taken statically at all — the metadata usage table that would name the two
`Board_PVP` blobs is only reachable through a native probe, and the owner's order of
26/10 forbids probes. The gate records that as `POLICY`, not as "unknown".
"""
import argparse
import functools
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import open_items_audit as AUDIT  # noqa: E402

ARTIFACT = 'datas/l2_535b0541_audit_drift.json.gz'
GLOB = 'datas/l2_535b0541_*.json.gz'
SELF = 'l2_535b0541_audit_drift'
EXCLUDE = {'l2_535b0541_lane_closeout', 'l2_535b0541_open_items_audit'}

# Items the audit still lists as not-closed, with the exact step that would settle them.
CONTRACT = {
    9: dict(step='pin the served shop payload (prices and stock arrive over the network)',
            owner='owner', kind='DATA'),
    12: dict(step='pin a raw that carries `MyLibrary.ToRoman` (21103836); its two call '
                  'sites are already known', owner='AI-4', kind='PIN-RAW'),
    18: dict(step='the band upper bound is a serialized length (`[xConfig, #0x18]`)',
             owner='owner', kind='DATA'),
    19: dict(step='same: parameter index values come from the served config, only the 20 '
                  'literal sites are static', owner='owner', kind='DATA'),
    30: dict(step='the two `Board_PVP` blobs: needs the metadata usage table',
             owner='owner', kind='POLICY'),
    32: dict(step='widen the scan from calls to stores on the three counter cells '
                  '(0x50/0x54/0x58)', owner='AI-4', kind='SCAN'),
    34: dict(step='rank 0 level 0 has no reward row and no pinned code indexes it; '
                  'needs the served PvP league table', owner='owner', kind='DATA'),
    39: dict(step='the metadata usage table that names handle slot 0x2ae0010 '
                  '(`rewardValues`)', owner='owner', kind='POLICY'),
    40: dict(step='the same table for 0x2ae0018 (`rewardScales`)', owner='owner',
             kind='POLICY'),
    44: dict(step='what the 14 medal rows are indexed by is written in the served '
                  'tournament config, not in the cctor', owner='owner', kind='DATA'),
    48: dict(step='duplicate of 34; same served table', owner='owner', kind='DATA'),
    49: dict(step='pin a raw that carries `LanguageManager.GetText` (21202600); 127 call '
                  'sites are known', owner='AI-4', kind='PIN-RAW'),
    50: dict(step='`get_pathRoot` slots 0x2AEC9A0/0x2AEC9B0 are never dereferenced in the '
                  'pinned raws — needs a wider raw set', owner='AI-4', kind='PIN-RAW'),
    51: dict(step='`JsonParse.FromJson<object>` takes its type from slot 0x2AE1000, which '
                  'is not a string literal', owner='owner', kind='POLICY'),
    52: dict(step='the class behind slot 0x2ADB958 is not named by any pinned symbol',
             owner='owner', kind='POLICY'),
    27: dict(step='the per-key symbol needs the computed-key table; 146 already gives 51 '
                  'records over 14 prefixes', owner='AI-4', kind='INDEX'),
    54: dict(step='same as 27', owner='AI-4', kind='INDEX'),
}
DEFAULTS = {
    'RUNTIME': dict(step='device or served state — MODEL_NOT_MEASURED runtime',
                    owner='owner', kind='RUNTIME'),
    'NOTE': dict(step='not a gap: recorded so the index is complete', owner='AI-4',
                 kind='NOTE'),
}


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def audit():
    return load('datas/l2_535b0541_open_items_audit.json.gz')


@functools.lru_cache(maxsize=None)
def artifacts():
    """Every lane artifact except the audit and its close-out, keyed by file stem."""
    out = {}
    for path in sorted(ROOT.glob(GLOB)):
        stem = path.name[:-len('.json.gz')]
        if stem in EXCLUDE or stem.startswith(SELF):
            continue
        out[stem] = load('datas/%s.json.gz' % stem)
    return out


def doc_index():
    """report number -> topic, read off `docs/apk-analysis/<n>-535b0541-<topic>.md`.

    170 taught the audit to name 168/169 by hand, so its table stops at 146 / 168 / 169 and
    every report after it is nameless (mục 4 of the report). The filenames already carry the
    number, so the gate reads them instead of asking somebody to keep a second list.
    """
    out = {}
    for path in sorted(ROOT.glob('docs/apk-analysis/*-535b0541-*.md')):
        match = re.match(r'(\d+)-535b0541-(.+)\.md$', path.name)
        if match:
            out[int(match.group(1))] = match.group(2).replace('-', '_')
    return out


@functools.lru_cache(maxsize=None)
def known_reports():
    """What the audit names, plus what the report filenames prove exists."""
    table = dict(AUDIT.REPORTS)
    for number, topic in doc_index().items():
        table.setdefault(number, topic)
    return table


def audit_report_of(stem):
    """The number **the audit's own table** can give this artifact, or None."""
    topic = stem.replace('l2_535b0541_', '')
    for number, name in AUDIT.REPORTS.items():
        if name == topic:
            return number
    return None


def report_of(stem):
    """The lane report number that wrote this artifact."""
    topic = stem.replace('l2_535b0541_', '')
    for number, name in known_reports().items():
        if name == topic:
            return number
    return None


def item_claims():
    """Statements that name an audit item by its column number."""
    rows = []
    for stem, payload in artifacts().items():
        report = report_of(stem)
        for key, kind in (('closed', 'closed'), ('corrected', 'corrected'),
                          ('blocked', 'blocked')):
            for entry in payload.get(key) or []:
                if 'n' not in entry:
                    continue
                rows.append(dict(artifact=stem, report=report, kind=kind, n=entry['n'],
                                 text=entry.get('how') or entry.get('now') or
                                      entry.get('why') or entry.get('item')))
    return rows


def report_claims():
    """Corrections that name another report instead of an item number."""
    rows = []
    for stem, payload in artifacts().items():
        for key in ('corrections', 'corrected'):
            for entry in payload.get(key) or []:
                if 'n' in entry or 'target' not in entry:
                    continue
                rows.append(dict(artifact=stem, report=report_of(stem),
                                 target=entry['target'],
                                 item=entry.get('item') or entry.get('field')))
    return rows


def audit_rows():
    return {row['n']: row for row in audit()['items']}


def records():
    return {(row['report'], row['kind'], row['closes']) for row in audit()['records']}


def run_rules(claims, targets, rows, known_reports, record_set):
    out = []
    for claim in claims:
        n = claim['n']
        row = rows.get(n)
        if claim['kind'] == 'closed':
            ok = (row is not None and row['verdict'] == 'CLOSED'
                  and row['closer'] == claim['report'])
            out.append(dict(rule='R2-closure', n=n, artifact=claim['artifact'],
                            report=claim['report'], passed=ok,
                            detail=dict(verdict=row['verdict'] if row else None,
                                        closer=row['closer'] if row else None)))
        elif claim['kind'] == 'corrected':
            ok = ((claim['report'], 'correction', n) in record_set
                  or (row is not None and row['verdict'] in ('RESTATED', 'CLOSED')
                      and row['closer'] == claim['report'])
                  or (row is not None and str(claim['report']) in (row['reason'] or '')))
            out.append(dict(rule='R3-correction', n=n, artifact=claim['artifact'],
                            report=claim['report'], passed=ok,
                            detail=dict(verdict=row['verdict'] if row else None)))
        else:
            ok = row is not None and not (row['verdict'] == 'CLOSED'
                                          and row['closer'] == claim['report'])
            out.append(dict(rule='R4-blocker', n=n, artifact=claim['artifact'],
                            report=claim['report'], passed=ok,
                            detail=dict(verdict=row['verdict'] if row else None)))
    for claim in claims:
        ok = claim['report'] in known_reports
        out.append(dict(rule='R1-coverage', n=claim['n'], artifact=claim['artifact'],
                        report=claim['report'], passed=ok, detail=None))
    for claim in targets:
        ok = claim['target'] in known_reports
        out.append(dict(rule='R5-target', n=None, artifact=claim['artifact'],
                        report=claim['report'], passed=ok, detail={'target': claim['target']}))
    return out


def contract(rows):
    """The unblock contract for everything the audit does not call closed."""
    out = []
    for n, row in sorted(rows.items()):
        if row['verdict'] == 'CLOSED':
            continue
        entry = CONTRACT.get(n) or DEFAULTS.get(row['verdict'],
                                                dict(step='not written yet', owner='AI-4',
                                                     kind='TODO'))
        out.append(dict(n=n, report=row['report'], item=row['item'], verdict=row['verdict'],
                        blocking=row['blocking'], **entry))
    return out


def check(rows, name, passed, detail=None):
    rows.append(dict(name=name, passed=bool(passed), detail=detail))


def build_payload():
    rows = audit_rows()
    claims = item_claims()
    targets = report_claims()
    known = set(known_reports())
    results = run_rules(claims, targets, rows, known, records())
    unread = sorted({row['detail']['target'] for row in results
                     if row['rule'] == 'R5-target' and not row['passed']})
    plan = contract(rows)

    checks = []
    check(checks, 'every-item-claim-was-evaluated',
          len(results) == len(claims) * 2 + len(targets),
          dict(claims=len(claims), targets=len(targets), rules=len(results)))
    check(checks, 'no-item-rule-fails',
          all(row['passed'] for row in results if row['rule'] != 'R5-target'),
          [row for row in results
           if row['rule'] != 'R5-target' and not row['passed']])
    check(checks, 'no-report-level-correction-points-at-an-unknown-report',
          unread == [], unread)
    check(checks, 'one-artifact-carries-item-claims',
          sorted({row['artifact'] for row in claims}) == ['l2_535b0541_lane_residue'],
          sorted({row['artifact'] for row in claims}))
    check(checks, 'that-artifact-maps-to-a-known-report',
          {row['report'] for row in claims} == {168}, sorted({row['report']
                                                              for row in claims}))
    check(checks, 'the-residue-report-gives-two-closures-two-corrections-five-blockers',
          [len([row for row in claims if row['kind'] == kind])
           for kind in ('closed', 'corrected', 'blocked')] == [2, 2, 5],
          [len([row for row in claims if row['kind'] == kind])
           for kind in ('closed', 'corrected', 'blocked')])
    check(checks, 'every-report-level-correction-names-its-target',
          all(row['detail']['target'] for row in results if row['rule'] == 'R5-target'),
          [row for row in results if row['rule'] == 'R5-target'])
    check(checks, 'the-contract-covers-everything-not-closed',
          len(plan) == len([row for row in rows.values() if row['verdict'] != 'CLOSED']),
          dict(plan=len(plan)))
    check(checks, 'the-contract-has-no-unwritten-step',
          [row for row in plan if row['kind'] == 'TODO'] == [],
          [row['n'] for row in plan if row['kind'] == 'TODO'])
    check(checks, 'five-items-need-an-owner-policy-decision',
          sorted(row['n'] for row in plan if row['kind'] == 'POLICY') == [30, 39, 40, 51, 52],
          [row['n'] for row in plan if row['kind'] == 'POLICY'])
    check(checks, 'three-items-need-a-raw-that-is-not-pinned',
          sorted(row['n'] for row in plan if row['kind'] == 'PIN-RAW') == [12, 49, 50],
          [row['n'] for row in plan if row['kind'] == 'PIN-RAW'])
    check(checks, 'six-items-are-served-data',
          sorted(row['n'] for row in plan if row['kind'] == 'DATA') == [9, 18, 19, 34, 44, 48],
          [row['n'] for row in plan if row['kind'] == 'DATA'])
    check(checks, 'one-item-is-a-wider-scan',
          [row['n'] for row in plan if row['kind'] == 'SCAN'] == [32],
          [row['n'] for row in plan if row['kind'] == 'SCAN'])
    check(checks, 'the-audit-still-has-fifty-six-items', len(rows) == 56, len(rows))
    unnamed = sorted(stem for stem in artifacts() if report_of(stem) is None)
    by_audit = sorted(stem for stem in artifacts() if audit_report_of(stem) is not None)
    # only reports that actually produced an artifact matter for R1; a doc without an
    # artifact (like the one you are reading) cannot carry an item claim.
    named_numbers = {report_of(stem) for stem in artifacts()} - {None}
    missing = sorted(set(range(min(known), max(named_numbers) + 1)) - set(AUDIT.REPORTS))
    conflicts = sorted(number for number, topic in doc_index().items()
                       if number in AUDIT.REPORTS and topic != AUDIT.REPORTS[number]
                       and topic in {stem.replace('l2_535b0541_', '') for stem in artifacts()})
    check(checks, 'every-artifact-maps-to-a-report-now-that-the-docs-are-the-index',
          unnamed == [], dict(unnamed=len(unnamed), artifacts=len(artifacts())))
    check(checks, 'the-audit-table-still-covers-127-to-146-whole',
          set(range(127, 147)) <= set(AUDIT.REPORTS),
          sorted(set(range(127, 147)) - set(AUDIT.REPORTS)))
    check(checks, 'the-blind-spot-starts-after-146',
          bool(missing) and min(missing) == 147, missing[:3])
    check(checks, 'the-docs-do-not-contradict-the-audit-on-a-shared-number',
          conflicts == [], conflicts)
    check(checks, 'the-gate-reads-every-lane-artifact',
          len(artifacts()) >= 40 and {'l2_535b0541_lane_residue',
                                      'l2_535b0541_cell_identity'} <= set(artifacts()),
          len(artifacts()))

    return dict(
        schema='l2/535b0541/audit-drift/1',
        evidence='STATIC_ONLY_ORIGINAL_APK',
        boundary=dict(branch='arena/535b0541-windwings-space-shooter-game-p',
                      watches='every datas/l2_535b0541_*.json.gz',
                      excludes=sorted(EXCLUDE | {SELF}),
                      note='a gate over artifacts, not a new decode'),
        totals=dict(artifacts=len(artifacts()), claims=len(claims), targets=len(targets),
                    rules=len(results),
                    failing=len([row for row in results
                                 if not row['passed'] and row['rule'] != 'R5-target']),
                    unread_targets=unread,
                    contract=len(plan),
                    checks_passed=sum(1 for row in checks if row['passed']),
                    checks_total=len(checks)),
        blind_spot=dict(
            artifacts=len(artifacts()),
            named_by_the_audit=len(by_audit),
            named_by_the_docs=len(artifacts()) - len(unnamed),
            unnamed_artifacts=unnamed,
            reports_the_audit_cannot_name=missing,
            docs_read=len(doc_index()),
            note='before 174 the gate could name 22/43 artifacts from AUDIT.REPORTS alone; '
                 'the index now comes from the report filenames, so 149 stops looking '
                 'invented and a missing doc becomes the tripwire instead',
        ),
        claims=claims,
        targets=targets,
        rules=results,
        contract=plan,
        limits=[
            'R1-R5 catch statements that name an item; a report that closes something '
            'without naming it is still invisible.',
            'the contract records who can act, not whether they will.',
            'POLICY is used where the only remaining route is a native probe, which the '
            'owner order of 26/10 forbids.',
        ],
        provenance=dict(
            inputs=[dict(path='datas/l2_535b0541_open_items_audit.json.gz',
                         sha256=sha_file('datas/l2_535b0541_open_items_audit.json.gz'))],
            artifacts=[dict(path='datas/%s.json.gz' % stem, sha256=sha_file(
                'datas/%s.json.gz' % stem)) for stem in sorted(artifacts())]),
        checks=checks,
    )


def build(output=None):
    payload = build_payload()
    blob = json.dumps(payload, sort_keys=True, indent=1, ensure_ascii=False).encode('utf-8')
    packed = gzip.compress(blob, mtime=0)
    if output:
        (ROOT / output).write_bytes(packed)
    return payload, packed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=ARTIFACT)
    args = parser.parse_args()
    payload, packed = build(args.output)
    print(json.dumps(dict(bytes=len(packed), sha256=hashlib.sha256(packed).hexdigest(),
                          **payload['totals'])))
    if payload['totals']['failing'] or payload['totals']['checks_passed'] != \
            payload['totals']['checks_total']:
        print(json.dumps([row for row in payload['rules'] if not row['passed']][:5]))
        print(json.dumps([row['name'] for row in payload['checks'] if not row['passed']]))
        raise SystemExit('gate failed')


if __name__ == '__main__':
    main()
