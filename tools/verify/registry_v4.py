#!/usr/bin/env python3
"""Report 180: registry-v4 — the final ledger of lane #29/#30, and the C1 correction.

Two jobs:

**C1 (149 vs 169/177).** 169 and 177 concluded that the six `Board_PVP` arrays ship but are
`NOT_BOUND`, because no *metadata usage table* exists in the repo. Report 149 had already
read them: the `InitializeArray` event carries the field identity, so `slot_va` ->
`field_id` -> `field-defaults.json` decodes to 24 bytes of data per array. This tool
re-derives that binding from `field-defaults.json` alone, without trusting 149's printed
values, and compares. Six of six match, including the float32 expansions. The three audit
items that 169 had merely narrowed (30, 39, 40) are therefore **CLOSED** by 149, and the
"needs the metadata usage table" blocker is withdrawn.

**C2 (registry-v4).** Every item the audit does not call `CLOSED` gets exactly one label
from {shipped-default, served, policy, missing-input, runtime-gated->USER} plus the step
that would settle it. The gate fails if a row is unlabelled, double-labelled, labelled
outside the five, or if the counts stop adding up to the 56 items of report 147. The
labels are derived from the audit verdict plus the drift contract's `kind`, so a verdict
that moves without the ledger moving trips the gate instead of drifting silently.
"""
import argparse
import functools
import gzip
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

ARTIFACT = 'datas/l2_535b0541_registry_v4.json.gz'
AUDIT_ART = 'datas/l2_535b0541_open_items_audit.json.gz'
DRIFT_ART = 'datas/l2_535b0541_audit_drift.json.gz'
RESIDUE_ART = 'datas/l2_535b0541_lane_residue.json.gz'
HUNTER_ART = 'datas/l2_535b0541_pvp_hunter_arrays.json.gz'
DEFAULTS = 'reverse-engineering/il2cpp/field-defaults.json'

LABELS = {
    'shipped-default': 'the value ships in the APK and is bound, or bindable, from pinned '
                       'bytes — no device and no network',
    'served': 'a remote payload writes the value at run time; the static side is complete',
    'policy': 'a static route may exist but needs an owner decision (metadata usage table, '
              'native probe, or similar) before it can be taken',
    'missing-input': 'the answer needs a raw or artifact that is not pinned in the repo',
    'runtime-gated→USER': 'only observable by running the game: device state, match state, '
                          'RNG, or what a player actually receives',
}

# label <- (audit verdict, drift contract kind). Order matters: the first match wins.
RULES = [
    dict(when='verdict == RUNTIME', label='runtime-gated→USER'),
    dict(when='kind == PIN-RAW', label='missing-input'),
    dict(when='kind == POLICY', label='policy'),
    dict(when='kind == INDEX', label='served'),
    dict(when='kind == DATA', label='served'),
]

# The three items 169 narrowed and 180 closes: their answer was already in 149.
C1_ITEMS = {30: 132, 39: 133, 40: 133}

# Per-item step, so the ledger says what would settle each row rather than restating it.
STEPS = {
    12: 'pin a raw that carries `MyLibrary.ToRoman` (21103836); 168 records bodies = 0 and '
        'two call sites, so the table is code we cannot read yet',
    18: 'serve the band/parameter config and read `[xConfig, #0x18]`; the length is not a '
        'literal in any pinned raw',
    19: 'same payload: the 20 literal call sites are static, the rest pass registers',
    27: 'needs the computed-key table: 146 gives 51 records over 14 prefixes, the index '
        'source is the shop/quest array length, which is served',
    34: 'serve `data-leagues` and read the first PvP league tab; no pinned code explains '
        'level 0 of rank 0',
    44: 'serve the tournament config that indexes the 14 medal rows',
    48: 'the same served table as 34; resolve both together',
    49: 'pin a raw that carries `LanguageManager.GetText` (21202600); 168 records bodies = 0 '
        'and 127 call sites',
    50: 'pin a wider raw set: `get_pathRoot` slots 0x2AEC9A0/0x2AEC9B0 are never '
        'dereferenced in the pinned raws',
    51: 'owner decision: `JsonParse.FromJson<object>` takes its type from metadata slot '
        '0x2AE1000 — try the `InitializeArray`-style join that fixed 30/39/40 first',
    52: 'owner decision: the class behind slot 0x2ADB958 is unnamed; same first attempt as 51',
    54: 'same as 27',
}

COUNTERS = ('items', 'distinct_questions', 'closed', 'restated', 'actionable', 'runtime',
            'note', 'still_open')


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def sha(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def defaults():
    return json.loads((ROOT / DEFAULTS).read_bytes())['fields']


def decode_binding():
    """Re-derive each array's bytes from `field-defaults.json` via 149's `field_id`.

    Deliberately does not read 149's `values`: the point is to check them.
    """
    fields, out = defaults(), []
    for row in load(HUNTER_ART)['arrays']:
        key = '<PrivateImplementationDetails>.' + row['blob']['field_id']
        entry = fields.get(key) or {}
        raw = (entry.get('raw') or '')
        declared = row['declared']
        data = bytes.fromhex(raw)[:24] if len(raw) >= 48 else b''
        if len(data) == 24:
            values = (list(struct.unpack('<6f', data)) if declared.startswith('float')
                      else list(struct.unpack('<6i', data)))
        else:
            values = None
        out.append(dict(field=row['field'].split('.')[-1], slot_va=row['slot_va'],
                        field_id=row['blob']['field_id'], declared=declared,
                        found=bool(entry), bytes_available=len(data),
                        values=values, published=row['values'],
                        agrees=values == row['values']))
    return out


def label_for(row, kind):
    for rule in RULES:
        name, _, want = rule['when'].partition(' == ')
        if name == 'verdict' and row['verdict'] == want:
            return rule['label']
        if name == 'kind' and kind == want:
            return rule['label']
    return None


def rows():
    audit = load(AUDIT_ART)
    plan = {item['n']: item for item in load(DRIFT_ART)['contract']}
    out = []
    for item in audit['items']:
        if item['verdict'] in ('CLOSED', 'NOTE'):
            continue
        kind = (plan.get(item['n']) or {}).get('kind')
        out.append(dict(n=item['n'], report=item['report'], item=item['item'],
                        verdict=item['verdict'], kind=kind, closer=item['closer'],
                        label=label_for(item, kind),
                        owner=(plan.get(item['n']) or {}).get('owner'),
                        step=STEPS.get(item['n'])
                        or (plan.get(item['n']) or {}).get('step')))
    return out


def build_payload():
    audit = load(AUDIT_ART)
    residue = load(RESIDUE_ART)
    binding = decode_binding()
    ledger = rows()
    plan = {item['n']: item for item in load(DRIFT_ART)['contract']}
    by_n = {item['n']: item for item in audit['items']}
    checks = []

    def check(name, passed, detail=None):
        checks.append(dict(name=name, passed=bool(passed), detail=detail))

    counts = {}
    for row in ledger:
        counts[row['label']] = counts.get(row['label'], 0) + 1

    # ---- C1
    check('every-array-field-id-resolves-in-field-defaults',
          all(row['found'] for row in binding), [row['field'] for row in binding
                                                 if not row['found']])
    check('every-array-has-twenty-four-bytes-of-data',
          all(row['bytes_available'] == 24 for row in binding),
          [row['bytes_available'] for row in binding])
    check('the-recomputed-values-agree-with-149',
          all(row['agrees'] for row in binding),
          [(row['field'], row['values'], row['published']) for row in binding
           if not row['agrees']])
    check('the-six-arrays-are-three-int-pairs-plus-one-float-pair',
          [row['declared'] for row in binding].count('float[]') == 1,
          [row['declared'] for row in binding])
    check('the-three-items-169-narrowed-are-closed-by-149',
          all(by_n[n]['verdict'] == 'CLOSED' and by_n[n]['closer'] == 149
              for n in C1_ITEMS),
          {n: (by_n[n]['verdict'], by_n[n]['closer']) for n in C1_ITEMS})
    check('the-three-closed-items-no-longer-block-on-the-metadata-table',
          all('metadata usage' not in (by_n[n]['blocking'] or '') for n in C1_ITEMS),
          {n: (by_n[n]['blocking'] or '')[:60] for n in C1_ITEMS})

    # ---- C2
    check('every-non-closed-item-is-in-the-ledger',
          len(ledger) + audit['totals']['closed'] + audit['totals']['note'] == 56
          and len(ledger) == len([item for item in audit['items']
                                  if item['verdict'] not in ('CLOSED', 'NOTE')]),
          dict(ledger=len(ledger), closed=audit['totals']['closed'],
               note=audit['totals']['note'], items=audit['totals']['items']))
    check('every-row-has-exactly-one-label',
          all(row['label'] in LABELS for row in ledger),
          [row['n'] for row in ledger if row['label'] not in LABELS])
    check('no-label-outside-the-five-is-used',
          set(counts) <= set(LABELS), sorted(counts))
    check('every-row-has-a-step-and-an-owner',
          all(row['step'] and row['owner'] for row in ledger),
          [row['n'] for row in ledger if not (row['step'] and row['owner'])])
    check('the-label-counts-add-up',
          sum(counts.values()) == len(ledger), counts)
    check('nothing-in-the-ledger-is-secretly-closed',
          all(row['verdict'] != 'CLOSED' for row in ledger),
          [row['n'] for row in ledger if row['verdict'] == 'CLOSED'])
    check('no-shipped-default-row-is-left',
          counts.get('shipped-default', 0) == 0,
          dict(shipped_default=counts.get('shipped-default', 0),
               why='the only three (30/39/40) are closed by 149'))
    absent = {entry['rva']: entry for entry in residue.get('absence') or []}
    named = {12: 21103836, 49: 21202600}
    check('the-two-code-shaped-gaps-are-recorded-absent-in-168',
          all(absent.get(rva, {}).get('bodies') == 0
              and absent.get(rva, {}).get('body_in_slices') == []
              for rva in named.values()),
          {n: absent.get(rva) for n, rva in named.items()})
    check('the-policy-rows-say-what-the-decision-is',
          all('owner decision' in (row['step'] or '')
              for row in ledger if row['label'] == 'policy'),
          [row['n'] for row in ledger
           if row['label'] == 'policy' and 'owner decision' not in (row['step'] or '')])
    check('the-runtime-rows-are-all-runtime-verdicts',
          all(row['verdict'] == 'RUNTIME' for row in ledger
              if row['label'] == 'runtime-gated→USER'),
          [row['n'] for row in ledger
           if row['label'] == 'runtime-gated→USER' and row['verdict'] != 'RUNTIME'])
    check('the-contract-still-has-no-scan-step',
          [n for n, item in plan.items() if item['kind'] == 'SCAN'] == [],
          [n for n, item in plan.items() if item['kind'] == 'SCAN'])
    check('the-audit-totals-still-partition-fifty-six',
          sum(audit['totals'][key] for key in COUNTERS[2:]) == 56, audit['totals'])
    check('the-drift-gate-is-green',
          [row['name'] for row in load(DRIFT_ART)['checks'] if not row['passed']] == [],
          len(load(DRIFT_ART)['checks']))

    return dict(
        schema='registry-v4/1',
        evidence='STATIC-ONLY: reads pinned artifacts plus `field-defaults.json`; the C1 '
                 'values are recomputed here, not copied from 149.',
        provenance=dict(branch='arena/535b0541-windwings-space-shooter-game-p',
                        audit=dict(path=AUDIT_ART, sha256=sha(AUDIT_ART)),
                        # 173 hashes every lane artifact, this one included, so its digest
                        # is deliberately absent here: recording it would make the pair
                        # chase each other forever. The gate reads 173's *content* instead.
                        drift=dict(path=DRIFT_ART,
                                   note='hashed by 173; not hashed back'),
                        residue=dict(path=RESIDUE_ART, sha256=sha(RESIDUE_ART)),
                        hunter=dict(path=HUNTER_ART, sha256=sha(HUNTER_ART)),
                        defaults=dict(path=DEFAULTS, sha256=sha(DEFAULTS))),
        taxonomy=dict(labels=LABELS, rules=RULES,
                      note='one label per row; the label is derived from the audit verdict '
                           'and the drift contract kind, so the ledger cannot drift from '
                           'the audit without this gate failing'),
        c1=dict(question='149 vs 169/177 — are the two `Board_PVP` blobs bound?',
                answer='bound: the InitializeArray event names the field, `field_id` '
                       'resolves in `field-defaults.json`, 24 bytes per array',
                join=['`Board_PVP..ctor` (19796420) -> `RuntimeHelpers.InitializeArray` '
                      '(33927292) event',
                      'event -> `slot_va` (0x2ae0008/10/18/30/38/40) + `field_id`',
                      '`field_id` -> `<PrivateImplementationDetails>.<id>` in '
                      '`field-defaults.json`',
                      'first 24 bytes -> 6 x int32, or 6 x float32 for `rewardScales`'],
                binding=binding,
                withdrawn='169/177: "`NOT_BOUND`, needs the metadata usage table" — the '
                          'table was never needed for this constructor; the event already '
                          'carries the identity, and 149 read it',
                closed_items={str(n): dict(report=report, closer=149,
                                           values=[row['values'] for row in binding
                                                   if row['field'] == field][0])
                              for n, (report, field) in
                              {30: (132, 'rewardIndexs'), 39: (133, 'rewardValues'),
                               40: (133, 'rewardScales')}.items()}),
        ledger=ledger,
        totals=dict(items=audit['totals']['items'], closed=audit['totals']['closed'],
                    note=audit['totals']['note'], ledger=len(ledger), by_label=counts),
        not_in_ledger=dict(note_items=[item['n'] for item in audit['items']
                                       if item['verdict'] == 'NOTE'],
                           why='a NOTE item is not a gap: the audit records it so the index '
                               'is complete, so it needs no label'),
        limits=['a label is a statement about the pinned corpus, not about the binary',
                'the two `policy` rows (51, 52) are the only ones where a cheap static '
                'route may still exist — they should be retried with the join that fixed '
                '30/39/40 before asking the owner for a probe',
                'every `runtime-gated→USER` row stays MODEL_NOT_MEASURED runtime'],
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
                          ledger=payload['totals']['ledger'],
                          by_label=payload['totals']['by_label'],
                          checks=len(payload['checks']), failing=len(failing),
                          names=failing), ensure_ascii=False))
    return 1 if failing else 0


if __name__ == '__main__':
    sys.exit(main())
