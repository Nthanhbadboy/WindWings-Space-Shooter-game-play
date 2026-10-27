#!/usr/bin/env python3
"""Report 179: close audit item 32 against 178, and prove the closure does not cycle.

Item 32 is the last `OPEN` item whose blocker was a *scan* rather than device state or a
served payload:

    "a direct static store outside these classes"  (report 132, item 32)

178 answered it with a store census over the whole 1788-method corpus: 102 stores land on
0x50/0x54/0x58, **none** writes a metadata cell, 16 go through a `static_fields` hop, and
exactly 6 of those are the `GameDatas` counters — so nothing outside the three accessors
stores into them. Item 32 is therefore `CLOSED` by 178.

Closing it changes three artifacts in a fixed order, and the order is the interesting part:

1. `open_items_audit` (170) re-evaluates the item and its proof -> new bytes.
2. `lane_residue` (168) *hashes the audit* into its provenance, so it must be regenerated —
   and because the audit reads 168's **content** (not its hash), the audit does not move
   again. That is the cycle 173 warned about, and it stops after one pass.
3. `audit_drift` (173) hashes every lane artifact, so it goes last.

This gate pins the fixed point: re-running the audit after 168 is regenerated must produce
the same bytes, and 168's recorded audit hash must equal the audit on disk.
"""
import argparse
import functools
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import audit_drift as DRIFT  # noqa: E402
import lane_residue as RESIDUE  # noqa: E402
import open_items_audit as AUDIT  # noqa: E402

ARTIFACT = 'datas/l2_535b0541_item32_closure.json.gz'
AUDIT_ART = 'datas/l2_535b0541_open_items_audit.json.gz'
DRIFT_ART = 'datas/l2_535b0541_audit_drift.json.gz'
RESIDUE_ART = 'datas/l2_535b0541_lane_residue.json.gz'
WRITERS_ART = 'datas/l2_535b0541_counter_static_writers.json.gz'
CLOSEOUT_ART = 'datas/l2_535b0541_lane_closeout.json.gz'

N = 32
CLOSER = 178
BEFORE = dict(bytes=10748,
              sha256='3b782ffa0f8605b7ea0632803ef662a9c792b9c0a59293aef1b7772fae33a0d3',
              closed=19, still_open=10, proofs=28, contract=37, residue_bytes=4902)
# The audit keeps moving after 179 (180 closed 30/39/40), so the "after" side is measured
# from the artifact at build time instead of being frozen here. Only the state 179 started
# from is history and stays pinned.
def after():
    live = load(AUDIT_ART)
    return dict(bytes=(ROOT / AUDIT_ART).stat().st_size, sha256=sha(AUDIT_ART),
                closed=live['totals']['closed'], still_open=live['totals']['still_open'],
                proofs=live['totals']['proofs'],
                contract=len(load(DRIFT_ART)['contract']),
                residue_bytes=(ROOT / RESIDUE_ART).stat().st_size)


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def sha(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def build_payload():
    audit = load(AUDIT_ART)
    drift = load(DRIFT_ART)
    residue = load(RESIDUE_ART)
    writers = load(WRITERS_ART)
    closeout = load(CLOSEOUT_ART)

    row = next(item for item in audit['items'] if item['n'] == N)
    plan = {item['n']: item for item in drift['contract']}
    source_text = [entry for entry in (AUDIT.art(132).get('not_decoded') or [])
                   + (AUDIT.art(132).get('gaps') or [])
                   if entry.get('item') == row['item']]
    _, rebuilt_audit = AUDIT.build(None)
    _, rebuilt_residue = RESIDUE.build(None)
    checks = []

    def check(name, passed, detail=None):
        checks.append(dict(name=name, passed=bool(passed), detail=detail))

    state = after()
    check('the-audit-is-the-regenerated-one',
          rebuilt_audit == (ROOT / AUDIT_ART).read_bytes(),
          dict(bytes=len(rebuilt_audit), sha256=hashlib.sha256(rebuilt_audit).hexdigest()))
    check('the-audit-still-has-56-items', audit['totals']['items'] == 56,
          audit['totals']['items'])
    check('item-32-is-closed-by-178',
          (row['verdict'], row['closer'], row['report']) == ('CLOSED', CLOSER, 132),
          dict(verdict=row['verdict'], closer=row['closer'], report=row['report']))
    check('the-closure-carries-a-proof-that-passes',
          bool(row['evidence']) and all(one['pass_'] for one in row['evidence']),
          [dict(label=one['label'], expected=one['expected'], actual=one['actual'])
           for one in row['evidence']])
    check('the-proof-reads-the-store-census',
          [one['expected'] for one in row['evidence']] == [[0, 16, 6]],
          [one['expected'] for one in row['evidence']])
    check('the-closure-moved-one-verdict-and-more-came-later',
          audit['totals']['closed'] >= BEFORE['closed'] + 1
          and audit['totals']['still_open'] == BEFORE['still_open'] - 1
          and audit['totals']['proofs'] >= BEFORE['proofs'] + 1,
          dict(closed=audit['totals']['closed'], still_open=audit['totals']['still_open'],
               proofs=audit['totals']['proofs']))
    check('the-verdicts-still-partition-the-items',
          sum(audit['totals'][key] for key in
              ('closed', 'restated', 'actionable', 'runtime', 'note', 'still_open')) == 56,
          audit['totals'])
    check('the-contract-keeps-no-scan-step',
          N not in plan and [n for n, item in plan.items() if item['kind'] == 'SCAN'] == [],
          dict(contract=len(plan), scan=[n for n, item in plan.items()
                                         if item['kind'] == 'SCAN']))
    check('no-drift-rule-fails-after-the-closure',
          [check['name'] for check in drift['checks'] if not check['passed']] == [],
          dict(checks=len(drift['checks'])))
    # 173 hashes every lane artifact, this one included, so its digest is pinned by the
    # test and never stored here: a stored digest would be the cycle 173 exists to stop.

    check('regenerating-168-does-not-move-the-audit-again',
          rebuilt_residue == (ROOT / RESIDUE_ART).read_bytes()
          and len(rebuilt_audit) == state['bytes'],
          dict(residue_bytes=len(rebuilt_residue),
               audit_sha256=hashlib.sha256(rebuilt_audit).hexdigest()))
    check('168-records-the-audit-hash-it-read',
          [row['sha256'] for row in residue['provenance']['inputs']
           if row['path'] == AUDIT_ART] == [state['sha256']],
          [row['sha256'] for row in residue['provenance']['inputs']
           if row['path'] == AUDIT_ART])
    check('147-row-is-unchanged-by-the-closure',
          len(closeout.get('open_items') or []) == 56
          and sha(CLOSEOUT_ART) == '3b815fc91d8f21f2191aa4dd558aabac82f67d09adb0f24e3ce54da27a8ecadd',
          dict(items=len(closeout.get('open_items') or []), sha256=sha(CLOSEOUT_ART)))
    check('178-still-pins-the-same-census',
          (writers['census']['stores'], writers['census']['cell'],
           writers['census']['static-block']) == (102, 0, 16),
          dict(stores=writers['census']['stores'], cell=writers['census']['cell'],
               static_block=writers['census']['static-block']))
    check('the-item-text-is-still-132s-own-words',
          len(source_text) == 1 and source_text[0]['item'] == row['item'],
          [entry.get('item') for entry in source_text])

    return dict(
        schema='item-closure/1',
        evidence='STATIC-ONLY: reads the pinned artifacts; no disassembly here.',
        provenance=dict(branch='arena/535b0541-windwings-space-shooter-game-p',
                        audit=dict(path=AUDIT_ART, sha256=sha(AUDIT_ART),
                                   note='measured at build; 180 moved the audit past this '
                                        'report, so the digest here is not a 179-only pin'),
                        # 173 is deliberately absent: it hashes this artifact, so a digest
                        # of it here would be the cycle 173 exists to prevent.
                        residue=dict(path=RESIDUE_ART, sha256=sha(RESIDUE_ART)),
                        writers=dict(path=WRITERS_ART, sha256=sha(WRITERS_ART)),
                        closeout=dict(path=CLOSEOUT_ART, sha256=sha(CLOSEOUT_ART))),
        item=dict(n=N, report=row['report'], text=row['item'],
                  blocking=row['blocking'], verdict=row['verdict'],
                  closer=row['closer'], reason=row['reason'],
                  evidence=row['evidence']),
        order=['open_items_audit (170) re-evaluates the item',
               'lane_residue (168) is regenerated because it hashes the audit',
               'audit_drift (173) is regenerated because it hashes every artifact'],
        fixed_point=dict(audit_before=BEFORE, audit_after=state,
                         report='179', superseded_by=180,
                         note='the audit reads 168\'s content, not its hash, so the '
                              'second pass reproduces the same bytes'),
        contract_after=dict(items=len(plan),
                            scan=[n for n, item in plan.items()
                                  if item['kind'] == 'SCAN'],
                            kinds={kind: sum(1 for item in plan.values()
                                             if item['kind'] == kind)
                                   for kind in sorted({item['kind']
                                                       for item in plan.values()})}),
        limits=['the nine items still `OPEN` are untouched: five need a served payload '
                '(18, 19, 34, 44, 48), two need a raw that is not pinned (49, 50) and two '
                'need an owner decision on the metadata usage table (51, 52)',
                'closing an item is a statement about the pinned corpus, not about the '
                'binary: a store inside a method no scan contains stays invisible',
                'the value any of these items would reveal on a device stays '
                'MODEL_NOT_MEASURED runtime'],
        checks=checks,
    )


def build(output=None):
    payload = build_payload()
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=1).encode()
    packed = gzip.compress(blob, 9, mtime=0)
    if output:
        (ROOT / output).write_bytes(packed)
    return payload, packed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    payload, packed = build(ARTIFACT if args.write else None)
    failing = [row['name'] for row in payload['checks'] if not row['passed']]
    print(json.dumps(dict(bytes=len(packed), sha256=hashlib.sha256(packed).hexdigest(),
                          checks=len(payload['checks']), failing=len(failing),
                          names=failing), ensure_ascii=False))
    return 1 if failing else 0


if __name__ == '__main__':
    sys.exit(main())
