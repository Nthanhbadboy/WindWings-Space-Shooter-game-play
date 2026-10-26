#!/usr/bin/env python3
"""The `GameDatas` save keys: 21 `PlayerPrefs` keys, 48 reads, 42 writes.

(The same pass also censuses the game's own store, `PlayerPreferences`: 174 calls
in 4 raws over 42 candidate keys. That slice is reported as a count only — its
keys come from indexed and default-argument positions, so the nearest-`slot_ref`
shortcut that works cleanly for `PlayerPrefs` is not trustworthy there.)


Report 142 left the currency keys as `not_decoded`, claiming the key slots carried
no `addend`. That was wrong: every one of those slots has a `slot_ref` whose
`addend` points into `stringliteral.json`, so the text is readable. This report
reads them, and the key set turns out to cover far more than the four currencies —
the whole `GameDatas` economy is `PlayerPrefs.GetInt` / `PlayerPrefs.SetInt` over
21 keys, each used on both sides.

Two methodology notes that matter for the next digger:

* **The write side is a tail call.** Every setter ends with `b #0x277CC10`
  (`PlayerPrefs.SetInt`) instead of `bl`, so a scan that only looks at `bl` sees
  48 reads and **zero** writes. Including `b` gives 42 writes.
* **`slot_refs.rva` points at the deref of the key cell**, and `slot_va` equals the
  `adrp page` + `ldr #offset` address exactly, so a key is resolved by taking the
  nearest preceding string-typed `slot_ref` for each `PlayerPrefs` call.
"""
import argparse
import collections
import gzip
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

RAW_GLOB = 'reverse-engineering/raw/*/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
STRINGS = 'reverse-engineering/il2cpp/stringliteral.json'

UNITY_PREFS = {
    41405456: 'SetInt', 41405600: 'GetInt', 41405668: 'SetFloat',
    41405820: 'GetFloat', 41405896: 'SetString', 41406040: 'GetString',
    41406108: 'GetString', 41406216: 'DeleteKey',
    41405244: 'TrySetInt', 41405312: 'TrySetFloat', 41405388: 'TrySetString',
}
GAME_PREFS = {
    0x13F1824: 'SetValue', 0x13F1930: 'GetValue', 0x13F1A04: 'SetInt',
    0x13F1A0C: 'SetFloat', 0x13F1A14: 'SetString', 0x13F1A1C: 'GetInt',
    0x13F1A24: 'GetFloat', 0x13F1A2C: 'GetString', 0x13F1A34: 'DeleteAll',
    0x13F1B44: 'DeleteKey',
}
STORES = {'unity-playerprefs': UNITY_PREFS, 'game-playerpreferences': GAME_PREFS}

CURRENCY = {
    'GCoins': dict(getter='GameDatas.get_Coins', getter_rva=20069516,
                   default=68999, cache=0x44, report=142),
    'Gems': dict(getter='GameDatas.get_Gems', getter_rva=20068904,
                 default=500, cache=0x48, report=142),
    'StarCount': dict(getter='GameDatas.get_StarCount', getter_rva=20075932,
                      default=0, cache=0x4C, report=142),
    'WingCoins': dict(getter='GameDatas.get_WingCoins', getter_rva=20070312,
                      default=999999, cache=0x5C, report=142),
}

SETTER_NO_PREFS = ['Compensation', 'IsCollectPremiumDailyGift',
                   'CanCollectPremiumGift', 'IsPremiumTag', 'CountThroughAds',
                   'LastArenaPoints']

CLASS_LINE = re.compile(r'\s*(?:public|private|internal)?\s*(?:static\s+)?'
                        r'(?:sealed\s+)?(?:abstract\s+)?(?:partial\s+)?'
                        r'(?:class|struct|enum|interface) ([\w\.<>`]+)')


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def raw_paths():
    return tuple(sorted(str(path.relative_to(ROOT)) for path in ROOT.glob(RAW_GLOB)))


@lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@lru_cache(maxsize=None)
def literals():
    return {int(row['address'], 16): row['value']
            for row in json.loads((ROOT / STRINGS).read_text())}


@lru_cache(maxsize=None)
def rva_index():
    index, current = {}, None
    lines = gzip.decompress((ROOT / DUMP).read_bytes()).decode(
        'utf-8', 'replace').split('\n')
    for position, line in enumerate(lines[:-1]):
        found = CLASS_LINE.match(line)
        if found:
            current = found.group(1)
        rva = re.search(r'// RVA: 0x([0-9A-Fa-f]+)', line)
        if rva:
            index.setdefault(int(rva.group(1), 16),
                             (current, lines[position + 1].strip()))
    return index


def scan():
    """Every persisted-property call in the pinned raws, with the key it uses."""
    texts = literals()
    records = []
    for path in raw_paths():
        blob = load(path)
        for method in blob['methods']:
            refs = sorted(
                (ref['rva'], texts[ref['addend']], ref['addend'], ref['slot_va'])
                for ref in method.get('slot_refs', [])
                if ref.get('addend') in texts)
            if not refs:
                continue
            for insn in method['instructions']:
                if insn['mnemonic'] not in ('bl', 'b'):
                    continue
                operand = insn['op_str'].strip()
                if not re.fullmatch(r'#0x[0-9a-f]+', operand):
                    continue
                target = int(operand.lstrip('#'), 16)
                store = next((name for name, table in STORES.items()
                              if target in table), None)
                if store is None:
                    continue
                before = [ref for ref in refs if ref[0] <= insn['rva']]
                near = before[-1] if before else None
                records.append(dict(
                    raw=path.split('/')[-2], class_name=method['class_name'],
                    signature=method['signature'].strip(),
                    method_rva=method['rva'], call_rva=insn['rva'],
                    tail=insn['mnemonic'] == 'b', store=store,
                    api=STORES[store][target], api_rva=target,
                    key=near[1] if near else None,
                    literal=near[2] if near else None,
                    slot_va=near[3] if near else None,
                    ref_rva=near[0] if near else None,
                    gap=insn['rva'] - near[0] if near else None))
    return records


def keys_table(records):
    """One row per key: literal address, slot, reads and writes."""
    table = collections.OrderedDict()
    for record in sorted(records, key=lambda row: row['key']):
        row = table.setdefault(record['key'], dict(
            key=record['key'], literal=record['literal'],
            slot_va=record['slot_va'], reads=[], writes=[]))
        assert row['literal'] == record['literal'], record['key']
        assert row['slot_va'] == record['slot_va'], record['key']
        entry = dict(raw=record['raw'], api=record['api'], call_rva=record['call_rva'],
                     method=record['signature'], method_rva=record['method_rva'],
                     ref_rva=record['ref_rva'], gap=record['gap'])
        row['reads' if record['api'].startswith('Get') else 'writes'].append(entry)
    return list(table.values())


def setters_without_prefs():
    """`GameDatas` setters in dump.cs that never touch PlayerPrefs."""
    lines = gzip.decompress((ROOT / DUMP).read_bytes()).decode(
        'utf-8', 'replace').split('\n')
    start = next(index for index, line in enumerate(lines)
                 if re.match(r'\s*public class GameDatas ', line))
    out, pinned = [], set()
    for path in raw_paths():
        for method in load(path)['methods']:
            pinned.add(method['rva'])
    for position in range(start, len(lines)):
        found = re.search(r'// RVA: 0x([0-9A-Fa-f]+)', lines[position])
        if not found:
            continue
        signature = lines[position + 1].strip()
        if not signature.startswith('public static void set_'):
            continue
        name = signature.split('(')[0].split('set_')[1]
        if name in SETTER_NO_PREFS:
            out.append(dict(name=name, rva=int(found.group(1), 16),
                            pinned=int(found.group(1), 16) in pinned))
    return out


def slice_census(records):
    return dict(calls=len(records),
                apis=dict(collections.Counter(record['api'] for record in records)),
                per_raw=dict(collections.Counter(record['raw'] for record in records)),
                tails=sum(1 for record in records if record['tail']))


def build_payload():
    records = scan()
    assert records, 'no persisted-property call found'
    unity = [record for record in records if record['store'] == 'unity-playerprefs']
    game = [record for record in records if record['store'] == 'game-playerpreferences']
    assert len(unity) == 90 and len(game) == 174, (len(unity), len(game))

    # Unity PlayerPrefs slice: every key resolves with a tight offset.
    assert all(record['key'] for record in unity), unity
    census = slice_census(unity)
    assert census['apis'] == {'GetInt': 48, 'SetInt': 42}, census['apis']
    assert census['tails'] == 42
    assert census['per_raw'] == {'key-grant-535b0541': 45,
                                 'meta-rewards-535b0541': 45}, census['per_raw']
    assert all(record['tail'] == (record['api'] == 'SetInt') for record in unity)

    gaps = collections.Counter(record['gap'] for record in unity)
    assert gaps == {4: 46, 8: 2, 12: 40, 36: 2}, dict(gaps)
    read_gaps = collections.Counter(record['gap'] for record in unity
                                    if not record['tail'])
    write_gaps = collections.Counter(record['gap'] for record in unity
                                     if record['tail'])
    assert read_gaps == {4: 46, 36: 2}, dict(read_gaps)
    assert write_gaps == {8: 2, 12: 40}, dict(write_gaps)

    table = keys_table(unity)
    assert len(table) == 21, len(table)
    assert all(row['reads'] and row['writes'] for row in table)
    keys = [row['key'] for row in table]
    for name in CURRENCY:
        assert name in keys, name

    # The currency keys are the same cells 142 read, so tie the two reports together.
    for row in table:
        if row['key'] not in CURRENCY:
            continue
        spec = CURRENCY[row['key']]
        getters = {entry['method_rva'] for entry in row['reads']}
        assert getters == {spec['getter_rva']}, (row['key'], getters)

    # Game store slice: census only — the key heuristic is not trustworthy there.
    game_census = slice_census(game)
    assert game_census['apis'] == {'SetInt': 63, 'GetInt': 54, 'SetString': 32,
                                   'GetString': 23, 'DeleteKey': 2}, game_census
    assert game_census['per_raw'] == {'meta-rewards-535b0541': 74,
                                      'key-grant-535b0541': 49,
                                      'arena-pvp-535b0541': 41,
                                      'box-draw-535b0541': 10}, game_census['per_raw']
    game_keys = {record['key'] for record in game if record['key']}
    tight = {record['key'] for record in game
             if record['key'] and record['gap'] is not None and record['gap'] <= 8}
    assert len(game_keys) == 42 and len(tight) == 6, (len(game_keys), len(tight))
    assert sum(1 for record in game if not record['key']) == 11

    idx = rva_index()
    no_prefs = setters_without_prefs()
    assert len(no_prefs) == 6, no_prefs
    assert all(row['pinned'] for row in no_prefs), no_prefs
    for row in no_prefs:
        assert idx.get(row['rva'], ('', ''))[1].startswith(
            'public static void set_%s(' % row['name']), row

    blob = load(next(path for path in raw_paths() if 'key-grant' in path))
    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Keys, call sites and value flow are static; the stored numbers are '
             'whatever the device had — MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            xapk_sha256=blob['xapk_sha256'],
            libil2cpp_sha256=blob['libil2cpp_sha256'],
            dump_sha256=blob['dump_sha256'],
            sources=[dict(path=path, sha256=sha_file(path),
                          role='persisted-property call sites and key slot_refs')
                     for path in raw_paths()]
                    + [dict(path=STRINGS, sha256=sha_file(STRINGS),
                            role='key text per slot_ref addend'),
                       dict(path=DUMP, sha256=sha_file(DUMP),
                            role='the 13 PlayerPrefs RVAs, the 10 '
                                 'PlayerPreferences RVAs and the setter census')]),
        census=dict(unity_playerprefs=dict(census,
                                          keys=len(table),
                                          gap_histogram={str(gap): count
                                                         for gap, count in gaps.items()},
                                          read_gap_histogram={str(gap): count for gap,
                                                              count in read_gaps.items()},
                                          write_gap_histogram={str(gap): count
                                                               for gap, count in
                                                               write_gaps.items()},
                                          note='all 42 writes are tail calls (`b`), '
                                               'all 48 reads are `bl` — a bl-only '
                                               'scan sees no writes at all'),
                     game_playerpreferences=dict(
                         game_census, distinct_keys=len(game_keys),
                         keys_resolved_tightly=len(tight),
                         unresolved=sum(1 for record in game if not record['key']),
                         note='census only: the game store is called from many '
                              'shapes (indexed keys, default string arguments), so '
                              'the nearest-ref heuristic is not trusted here'),
                     stores=dict(unity='PlayerPrefs',
                                 game='PlayerPreferences')),
        keys=table,
        currency=dict(rows=[dict(key=name, **spec) for name, spec in CURRENCY.items()],
                      note='the four keys 142 stopped at; this report resolves the '
                           'text, 142 could not'),
        setter_without_prefs=no_prefs,
        corrections=[dict(
            item='142 not_decoded: "the PlayerPrefs key literals are not attached '
                 'to any pinned dereference, so the text is not read here"',
            measured=[dict(key=row['key'], literal=row['literal'],
                           slot_va=row['slot_va']) for row in table
                      if row['key'] in CURRENCY],
            why='every one of those slots has a `slot_ref` whose `addend` resolves '
                'in `stringliteral.json`; report 142 recorded the cell addresses but '
                'never consulted the addend',
            impact='the four currency keys are GCoins / Gems / StarCount / WingCoins, '
                   'and the same GameDatas block carries 17 more keys on both read '
                   'and write')],
        not_decoded=[
            dict(item='stored values of the 21 keys',
                 blocking='they live in the device save, not in the APK — '
                          'MODEL_NOT_MEASURED runtime'),
            dict(item='keys of the 174 game-store calls',
                 blocking='the game store is invoked with indexed keys '
                          '(`KEY_` + index) and default string arguments, so 11 '
                          'calls resolve to no key and only 6 of 42 candidate keys '
                          'sit within 8 instructions of their slot_ref — this needs '
                          'a per-method register pass, not the nearest-ref shortcut'),
            dict(item='PlayerPrefs string/float/DeleteKey sites',
                 blocking='the 13 PlayerPrefs APIs are resolved, but only GetInt and '
                          'SetInt occur in the 8 pinned raws; the other call sites '
                          'sit in methods outside the pinned families'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_economy_keys.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                               sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          keys=payload['census']['unity_playerprefs']['keys'],
                          calls=payload['census']['unity_playerprefs']['calls'],
                          apis=payload['census']['unity_playerprefs']['apis'])))


if __name__ == '__main__':
    main()
