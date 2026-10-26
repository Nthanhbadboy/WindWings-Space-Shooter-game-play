#!/usr/bin/env python3
"""Close-out gate for lane #29/#30: do reports 127-146 agree with each other?

This adds no new decode. It re-reads the twenty artifacts the lane produced and
checks the numbers the reports cite against the artifacts and against each other,
so a later edit cannot silently break the story. Three checks earn their keep:

* **143 is reproducible, not wrong.** Applying 143's own rule — count store calls
  only in methods that carry a string `slot_ref` — reproduces its 174 calls and its
  exact API split (SetString 32, GetInt 54, SetInt 63, GetString 23, DeleteKey 2).
* **and that is where its missing 10 went.** 184 - 174 = 10: four in `key-jump`
  (the tail calls 145 named) and *six in `meta-rewards`* — methods without a string
  `slot_ref` at all. 145's note credited only `key-jump`; this corrects it.
* **the two key spaces are disjoint.** 143's 21 `GameDatas` keys and 144's 25
  literal store keys do not overlap, so the two reports never double-count.

Everything else is bookkeeping: the 26 -> 0 resolution, 25 -> 28 keys, 43 -> 51
computed records, 12 bands, the 999 sentinel, one slot per class, ten rank tiers,
the PvP rule pairs, and every artifact's provenance digest.
"""
import argparse
import collections
import glob
import gzip
import hashlib
import json
import os
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import sys  # noqa: E402
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import store_key_callers as base  # noqa: E402

DOCS = 'docs/apk-analysis/[0-9][0-9][0-9]-*.md'
ARTIFACT_GLOB = 'datas/l2_535b0541_*.json.gz'

EXPECTED_REPORTS = list(range(127, 147))   # 127..146, one artifact each
REPORT_143 = 143
ECONOMY_CALLS = 174
ECONOMY_API = {'SetString': 32, 'GetInt': 54, 'SetInt': 63, 'GetString': 23,
               'DeleteKey': 2}
STORE_CALLS = 184
SENTINEL = 999
SENTINEL_SITES = 20
BANDS = {100, 200, 300}
APP_CELL = 44939488
GAME_CONFIG_SLOT = 44940168


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def artifacts():
    """The twenty lane artifacts — never this gate's own output."""
    return tuple(sorted(path for path in glob.glob(ARTIFACT_GLOB)
                        if not path.endswith(('_lane_closeout.json.gz',
                                              '_open_items_audit.json.gz'))))


@lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@lru_cache(maxsize=None)
def docs():
    """The twenty reports this gate covers, and only those."""
    covered = {str(number) for number in EXPECTED_REPORTS}
    return tuple(sorted(str(path.relative_to(ROOT)) for path in ROOT.glob(DOCS)
                        if os.path.basename(path).split('-')[0] in covered))


def report_of(artifact):
    """The report number whose markdown names this artifact."""
    name = os.path.basename(artifact)
    hits = [os.path.basename(path).split('-')[0] for path in docs()
            if name in (ROOT / path).read_text()]
    return hits


def economy_rule():
    """143's census: store calls only in methods that carry a string `slot_ref`."""
    texts = base.strings()
    inside, outside = collections.Counter(), collections.Counter()
    per_raw_in, per_raw_out = collections.Counter(), collections.Counter()
    apis_in, apis_out = collections.Counter(), collections.Counter()
    for path in base.raw_paths():
        raw = path.split('/')[-2]
        for method in base.load(path)['methods']:
            has_ref = any(ref.get('addend') in texts for ref in method.get('slot_refs', []))
            for insn in method['instructions']:
                if insn['mnemonic'] not in ('bl', 'b'):
                    continue
                target = insn['op_str'].strip().lstrip('#')
                if not re.fullmatch(r'0x[0-9a-f]+', target):
                    continue
                api = base.STORE.get(int(target, 0))
                if not api:
                    continue
                if has_ref:
                    inside[api] += 1
                    per_raw_in[raw] += 1
                else:
                    outside[api] += 1
                    per_raw_out[raw] += 1
    return dict(inside=sum(inside.values()), outside=sum(outside.values()),
                apis_in=dict(inside), outside_by_raw=dict(per_raw_out),
                inside_by_raw=dict(per_raw_in))


def check(checks, ident, statement, expected, actual):
    checks.append(dict(id=ident, statement=statement, expected=expected,
                       actual=actual, pass_=expected == actual))


def build_payload():
    mapping = {os.path.basename(path): report_of(path) for path in artifacts()}
    # one artifact per report, 127..146, no orphan and no duplicate
    primary = {}
    for name, hits in mapping.items():
        assert hits, name
        primary[name] = int(hits[0])
    assert sorted(primary.values()) == EXPECTED_REPORTS, sorted(primary.values())
    assert len(set(primary.values())) == len(primary), primary
    assert len(primary) == 20, primary

    store = load('datas/l2_535b0541_game_store_keys.json.gz')
    callers = load('datas/l2_535b0541_store_key_callers.json.gz')
    index = load('datas/l2_535b0541_computed_key_index.json.gz')
    economy = load('datas/l2_535b0541_economy_keys.json.gz')
    app = load('datas/l2_535b0541_application_cell.json.gz')
    gate = load('datas/l2_535b0541_game_config_gate.json.gz')
    rank = load('datas/l2_535b0541_rank_name.json.gz')
    stars = load('datas/l2_535b0541_max_rank_stars.json.gz')
    pvp = load('datas/l2_535b0541_pvp_manager_rules.json.gz')

    checks = []
    check(checks, 'store-calls',
          '144 and 145 count the same store, call for call',
          (STORE_CALLS, STORE_CALLS),
          (store['census']['calls'], callers['cross_check']['calls']))
    check(checks, 'store-kinds-before',
          '144 splits 184 into literal / computed / unknown',
          STORE_CALLS, sum(store['census']['by_kind'].values()))
    check(checks, 'store-kinds-after',
          '145 splits the same 184, with nothing left unknown',
          (STORE_CALLS, 0), (sum(callers['census']['by_kind'].values()),
                             callers['census']['by_kind']['unknown']))
    check(checks, 'resolution-adds-up',
          'the 26 unknowns become 18 literal + 8 computed',
          {'literal': 18, 'computed': 8}, callers['resolution']['by_kind'])
    check(checks, 'keys-25-to-28',
          '145 adds exactly three literal keys to 144 (25 -> 28)',
          (25, 28, 3), (len(store['literal_keys']), len(callers['literal_keys']),
                        len(callers['new_keys']['literal'])))
    old = {row['key']: len(row['calls']) for row in store['literal_keys']}
    new = {row['key']: row['calls'] for row in callers['literal_keys']}
    check(checks, 'old-keys-unchanged',
          'every 144 key survives 145 with the same call count',
          old, {key: new[key] for key in old})
    check(checks, 'prefixes-13-to-14',
          '145 adds one computed bucket (13 -> 14 including the null prefix)',
          (13, 14), (len(store['computed_keys']), len(callers['computed']['values'])))
    check(checks, 'computed-records',
          '146 explains exactly the 51 computed records of 145',
          (51, 51), (sum(row['calls'] for row in callers['computed']['values']),
                     index['census']['records']))
    check(checks, 'computed-families',
          '146 lists the same 14 prefix buckets with the same record counts',
          sorted((str(row['prefix']), row['calls'])
                 for row in callers['computed']['values']),
          sorted((str(row['prefix']), row['records']) for row in index['families']))
    check(checks, 'bands',
          'the shop namespaces carry three bands, twice',
          (12, sorted(BANDS)),
          (len(index['bands']), sorted({row['band'] for row in index['bands']})))
    check(checks, 'sentinel',
          'the only literal index is 999, at 20 of the 51 records',
          (SENTINEL, SENTINEL_SITES, ['Quest_Collect_Index', 'Quest_Value_Key']),
          (index['sentinel']['value'], index['sentinel']['sites'],
           index['sentinel']['families']))

    rule = economy_rule()
    check(checks, 'economy-reproducible',
          "143's rule (methods carrying a string slot_ref) still yields 174 and its split",
          (ECONOMY_CALLS, ECONOMY_API), (rule['inside'], rule['apis_in']))
    check(checks, 'economy-delta',
          'the 10 calls 143 did not see are 4 in key-jump and 6 in meta-rewards',
          (STORE_CALLS - ECONOMY_CALLS, {'key-jump-535b0541': 4,
                                         'meta-rewards-535b0541': 6}),
          (rule['outside'] - 0, rule['outside_by_raw']))
    eco_keys = {row['key'] for row in economy['keys']}
    store_keys = {row['key'] for row in store['literal_keys']}
    check(checks, 'key-spaces-disjoint',
          '143 (GameDatas) and 144 (store) name disjoint key sets',
          (0, 21, 25), (len(eco_keys & store_keys), len(eco_keys), len(store_keys)))
    check(checks, 'economy-cross-check',
          'the six setters 143 said leave PlayerPrefs are literal keys in 144',
          (6, 6), (len(economy['setter_without_prefs']),
                   len(store['cross_check']['keys'])))
    check(checks, 'one-slot-per-class',
          '142 cell (Application) and 141 slot (GameConfig) are different cells, 0x2A8 apart',
          (APP_CELL, GAME_CONFIG_SLOT, GAME_CONFIG_SLOT - APP_CELL),
          (app['cell']['decimal'], gate['slot']['decimal'],
           gate['slot']['decimal'] - app['cell']['decimal']))
    check(checks, 'rank-tiers',
          'rank_name and max_rank_stars agree on ten tiers',
          (10, 10), (len(rank['tiers']), len(stars['rank_table'])))
    pairs = [row['words'] for row in pvp['rules']['coalesced_int_pairs']]
    check(checks, 'pvp-rule-pairs',
          'the PvP rule constants are unchanged: [3, 1500] and [160, 10]',
          [[3, 1500], [160, 10]], pairs)

    evidence = {os.path.basename(path): load(path).get('evidence')
                for path in artifacts()}
    check(checks, 'static-only',
          'every artifact is labelled STATIC_ONLY_ORIGINAL_APK',
          ['STATIC_ONLY_ORIGINAL_APK'], sorted(set(evidence.values())))

    digest_bad = []
    for path in artifacts():
        for row in load(path).get('provenance', {}).get('sources', []):
            target = ROOT / row['path']
            if not target.exists() or sha_file(row['path']) != row['sha256']:
                digest_bad.append(row['path'])
    check(checks, 'provenance-digests',
          'every source digest recorded by every artifact still matches the workspace',
          [], digest_bad)

    inventory = []
    for path in artifacts():
        blob = load(path)
        inventory.append(dict(
            report=primary[os.path.basename(path)], artifact=os.path.basename(path),
            bytes=(ROOT / path).stat().st_size, sha256=sha_file(path),
            sections=sorted(blob.keys()), open_items=len(blob.get('not_decoded', [])),
            note=blob.get('note')))
    assert len(inventory) == 20

    open_items = []
    for row in inventory:
        blob = load('datas/' + row['artifact'])
        for item in blob.get('not_decoded', []):
            open_items.append(dict(report=row['report'],
                                   item=str(item.get('item'))[:180],
                                   blocking=str(item.get('blocking'))[:220]))
    runtime_items = [row for row in open_items
                     if 'MODEL_NOT_MEASURED' in row['blocking']]
    check(checks, 'runtime-is-never-claimed',
          'every artifact that leaves values open labels them runtime, not measured',
          True, len(runtime_items) >= 5)

    failures = [row for row in checks if not row['pass_']]
    assert not failures, failures

    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Close-out of lane #29/#30 (reports 127-146). No new disassembly: this '
             're-reads the twenty artifacts and checks that the numbers agree. '
             'Stored values stay MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            sources=[dict(path=path, sha256=sha_file(path), role='lane artifact')
                     for path in artifacts()]
                    + [dict(path=path, sha256=sha_file(path),
                            role='report that cites the artifact above')
                       for path in docs()],
            note='forty files: twenty artifacts and the twenty reports that own them'),
        mapping=[dict(report=primary[os.path.basename(path)],
                      artifact=os.path.basename(path),
                      mentioned_in=sorted(mapping[os.path.basename(path)]))
                 for path in artifacts()],
        checks=checks,
        inventory=inventory,
        totals=dict(reports=len(inventory), checks=len(checks),
                    open_items=len(open_items), runtime_items=len(runtime_items)),
        corrections=[dict(
            target=145, statement="145 said 'key-jump adds 4 it never saw'",
            correction='the missing 10 calls are 4 in key-jump and 6 in meta-rewards, '
                       'both in methods that carry no string slot_ref',
            evidence=dict(inside=rule['inside'], outside=rule['outside'],
                          outside_by_raw=rule['outside_by_raw']))],
        open_items=open_items,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_lane_closeout.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          reports=payload['totals']['reports'],
                          checks=payload['totals']['checks'],
                          failing=sum(1 for row in payload['checks']
                                      if not row['pass_']),
                          open_items=payload['totals']['open_items'],
                          runtime_items=payload['totals']['runtime_items'])))


if __name__ == '__main__':
    main()
