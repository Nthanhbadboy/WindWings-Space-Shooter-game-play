#!/usr/bin/env python3
"""The game store's keys: 25 literal keys, 11 indexed prefixes, 184 calls.

Report 143 counted the second store (`PlayerPreferences`, RVA-based, JSON-backed)
but refused to name its keys: the "nearest `slot_ref`" shortcut only resolved 6 of
42 candidates. This report replaces the shortcut with per-method register tracking:
`adrp` gives a page, a load from a page gives a string cell, a load from a cell
gives the literal (its text comes from the cell's `slot_ref.addend`), `mov`
propagates, and anything else that writes a register drops it.

That splits the 184 calls three ways:

* **115 literal** — the key is a compile-time string; 25 distinct keys.
* **43 computed** — the key is `String.Concat(<literal>, index)`; the *prefix* is
  recovered (11 distinct prefixes), the index is not part of the key text.
* **26 unknown** — the key arrives from a parameter or an unrelated call.

Two things to keep in mind: the earlier census said 174 because it only looked at
methods that carried a string `slot_ref`, and the store API list here is the same
ten RVAs 143 resolved, so the counts are comparable call-for-call apart from those
extra methods.
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

STORE = {0x13F1824: 'SetValue', 0x13F1930: 'GetValue', 0x13F1A04: 'SetInt',
         0x13F1A0C: 'SetFloat', 0x13F1A14: 'SetString', 0x13F1A1C: 'GetInt',
         0x13F1A24: 'GetFloat', 0x13F1A2C: 'GetString', 0x13F1A34: 'DeleteAll',
         0x13F1B44: 'DeleteKey'}

CONCAT = {33439876: 'Concat2', 33476172: 'ConcatObject3', 33476420: 'Concat3',
          33476644: 'Concat4', 33476908: 'ConcatArray'}

LITERAL_KEYS = ['VersionProfile', 'Local_Arena_Rank', 'FIRST_OPEN_ARENA', 'CountOpen',
                'FirstGetPower', 'FIRST_OPEN_PVP', 'HunterSeasonProgress',
                'HunterSeasonDies', 'IsFirstOpenQuest', 'TotalGemSpend',
                'Compensation', 'PREMIUM_DAILY_COLLECTED', 'PRO_ExpiryDateTime',
                'CanCollectPremiumGift', 'IsPremiumTag', 'CountThroughAds',
                'LastArenaPoints', 'TIME_EVENT_DOUBLE_ENDED', 'IS_FIRST_TIME_EVENT',
                'IsEventStarted', 'IS_BUY_EVENT_COMBO', 'TIME_VIDEO_ACTIVE',
                'VIDEO_CURRENT_INDEX', 'LUCKY_VALUE_4', 'LUCKY_VALUE_5']

COMPUTED_PREFIXES = ['ARENA_SHOP_ITEM_ID', 'ARENA_SHOP_ITEM_STOCK',
                     'HunterCollectProgress', 'PVP_SHOP_ITEM_ID',
                     'PVP_SHOP_ITEM_STOCK', 'Quest_Value_Key',
                     'Quest_Collect_Index', 'Quest_Check_Collect_Index',
                     'STOCK_EXCHANGE_EVENT1_', 'FIRST_FREE_BOX', None,
                     'GET_VIDEO_DONE', 'GET_VIDEO_UNLOCK']

# The six `GameDatas` setters that 143 listed as leaving `PlayerPrefs` must show up
# here as literal keys, otherwise the two reports contradict each other.
CROSS_CHECK = ['Compensation', 'CanCollectPremiumGift', 'IsPremiumTag',
               'CountThroughAds', 'LastArenaPoints', 'PREMIUM_DAILY_COLLECTED']


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def raw_paths():
    return tuple(sorted(str(path.relative_to(ROOT)) for path in ROOT.glob(RAW_GLOB)))


@lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@lru_cache(maxsize=None)
def strings():
    return {int(row['address'], 16): row['value']
            for row in json.loads((ROOT / STRINGS).read_text())}


def cell_maps(blob):
    """cell va -> (text, literal address) from that method's `slot_refs`."""
    texts = strings()
    out = {}
    for method in blob['methods']:
        for ref in method.get('slot_refs', []):
            if ref.get('addend') in texts:
                out[ref['slot_va']] = (texts[ref['addend']], ref['addend'])
    return out


def walk(blob, raw_name):
    """Register-tracked scan of one raw."""
    cells = cell_maps(blob)
    records = []
    for method in blob['methods']:
        roles = {}
        for insn in method['instructions']:
            mnemonic, operand = insn['mnemonic'], insn['op_str']
            if mnemonic == 'adrp':
                found = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', operand)
                if found:
                    roles[found.group(1)] = ('page', int(found.group(2), 0))
                continue
            if mnemonic in ('ldr', 'ldrb', 'ldrh', 'ldrsw'):
                if ', [' not in operand:
                    continue
                dest, rest = operand.split(', ', 1)
                hit = re.fullmatch(r'\[(x\d+)(?:, #(0x[0-9a-f]+))?\]', rest)
                if not hit:
                    continue
                base = hit.group(1)
                offset = int(hit.group(2), 0) if hit.group(2) else 0
                role = roles.get(base)
                if mnemonic == 'ldr' and role and role[0] == 'page':
                    roles[dest] = ('cell', role[1] + offset)
                    continue
                if mnemonic == 'ldr' and role and role[0] == 'cell' and offset == 0:
                    text, addend = cells.get(role[1], (None, None))
                    roles[dest] = ('lit', text, addend)
                    continue
                roles.pop(dest, None)
                continue
            if mnemonic == 'mov':
                copy = re.fullmatch(r'(x\d+), (x\d+)', operand)
                if copy:
                    roles[copy.group(1)] = roles.get(copy.group(2))
                    continue
                clear = re.fullmatch(r'(x\d+), (xzr|wzr|#0x[0-9a-f]+|\d+)', operand)
                if clear:
                    roles.pop(clear.group(1), None)
                continue
            if mnemonic in ('bl', 'b'):
                target = operand.strip().lstrip('#')
                if not re.fullmatch(r'0x[0-9a-f]+', target):
                    continue
                address = int(target, 0)
                if address in STORE:
                    first, second = roles.get('x0'), roles.get('x1')
                    kind, key, prefix, literal = 'unknown', None, None, None
                    if first and first[0] == 'lit' and first[1]:
                        kind, key, literal = 'literal', first[1], first[2]
                    elif first and first[0] == 'lit':
                        kind = 'empty-cell'
                    elif first and first[0] == 'concat':
                        kind, prefix = 'computed', first[1]
                    records.append(dict(
                        raw=raw_name, class_name=method['class_name'],
                        signature=method['signature'].strip(),
                        method_rva=method['rva'], call_rva=insn['rva'],
                        tail=mnemonic == 'b', api=STORE[address], api_rva=address,
                        kind=kind, key=key, literal=literal, prefix=prefix,
                        default=(second[1] if second and second[0] == 'lit'
                                 and second[1] else None)))
                if mnemonic == 'bl':
                    if address in CONCAT:
                        args = [role[1] for role in (roles.get('x0'), roles.get('x1'))
                                if role and role[0] == 'lit' and role[1]]
                        roles['x0'] = ('concat', args[0] if args else None)
                    else:
                        roles['x0'] = ('ret', address)
                continue
            written = re.fullmatch(r'(x\d+), .*', operand)
            if written:
                roles.pop(written.group(1), None)
    return records


def scan():
    records = []
    for path in raw_paths():
        records.extend(walk(load(path), path.split('/')[-2]))
    return records


def key_rows(records, kind, group):
    rows = collections.OrderedDict()
    for record in records:
        if record['kind'] != kind:
            continue
        name = record[group]
        row = rows.setdefault(name, dict(**{group: name}, calls=[]))
        if group == 'key':
            assert row.get('literal', record['literal']) == record['literal']
            row['literal'] = record['literal']
        row['calls'].append(dict(
            raw=record['raw'], api=record['api'], tail=record['tail'],
            call_rva=record['call_rva'], method=record['signature'],
            method_rva=record['method_rva'], default=record['default']))
    return list(rows.values())


def build_payload():
    records = scan()
    assert len(records) == 184, len(records)

    by_api = collections.Counter(record['api'] for record in records)
    assert by_api == {'SetInt': 67, 'GetInt': 58, 'SetString': 32, 'GetString': 25,
                      'DeleteKey': 2}, dict(by_api)
    by_raw = collections.Counter(record['raw'] for record in records)
    assert by_raw == {'meta-rewards-535b0541': 80, 'key-grant-535b0541': 49,
                      'arena-pvp-535b0541': 41, 'box-draw-535b0541': 10,
                      'key-jump-535b0541': 4}, dict(by_raw)
    by_kind = collections.Counter(record['kind'] for record in records)
    assert by_kind == {'literal': 115, 'computed': 43, 'unknown': 26}, dict(by_kind)
    assert sum(1 for record in records if record['tail']) == 51

    literal_rows = key_rows(records, 'literal', 'key')
    assert [row['key'] for row in literal_rows] == LITERAL_KEYS, [row['key']
                                                                  for row in literal_rows]
    computed_rows = key_rows(records, 'computed', 'prefix')
    prefixes = [row['prefix'] for row in computed_rows]
    assert prefixes == COMPUTED_PREFIXES, prefixes
    assert sum(len(row['calls']) for row in computed_rows) == 43
    assert all(row['calls'] for row in computed_rows)
    for name in CROSS_CHECK:
        assert name in [row['key'] for row in literal_rows], name

    defaults = collections.Counter(record['default'] for record in records
                                   if record['default'])
    assert len(defaults) >= 1

    unknown = [dict(raw=record['raw'], api=record['api'], call_rva=record['call_rva'],
                    method=record['signature'], method_rva=record['method_rva'])
               for record in records if record['kind'] == 'unknown']
    assert len(unknown) == 26

    blob = load(next(path for path in raw_paths() if 'arena-pvp' in path))
    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Keys are static strings; the values in the store are device state — '
             'MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            xapk_sha256=blob['xapk_sha256'],
            libil2cpp_sha256=blob['libil2cpp_sha256'],
            dump_sha256=blob['dump_sha256'],
            sources=[dict(path=path, sha256=sha_file(path),
                          role='store call sites, key cells and their slot_refs')
                     for path in raw_paths()]
                    + [dict(path=STRINGS, sha256=sha_file(STRINGS),
                            role='key text per cell addend'),
                       dict(path=DUMP, sha256=sha_file(DUMP),
                            role='the ten PlayerPreferences RVAs and the '
                                 'String.Concat RVAs')]),
        store=dict(**{'class': 'PlayerPreferences', 'apis': STORE},
                   note='game store, not Unity `PlayerPrefs`: JSON-backed with '
                        'GetRawData / SaveToDisk / LoadFromDisk'),
        census=dict(calls=len(records), by_api=dict(by_api), by_raw=dict(by_raw),
                    by_kind=dict(by_kind), tail_calls=51,
                    literal_keys=len(literal_rows),
                    computed_prefixes=len([name for name in prefixes if name]),
                    unknown_calls=len(unknown),
                    note='register tracking, one role per register; a role is '
                         'dropped by any write the walk does not model'),
        literal_keys=literal_rows,
        computed_keys=computed_rows,
        unknown_calls=unknown,
        defaults=dict(values=dict(defaults),
                      note='second argument of the Get* calls when it is a literal'),
        cross_check=dict(report=143,
                         keys=[row['key'] for row in literal_rows
                               if row['key'] in CROSS_CHECK],
                         note='the six GameDatas setters that 143 said leave '
                              '`PlayerPrefs` all use literal keys here'),
        not_decoded=[
            dict(item='26 calls whose key is not a literal or a concat prefix',
                 blocking='the key arrives as a parameter or from an unrelated call '
                          'inside the method; naming them needs either the caller '
                          'set or a cross-method value pass'),
            dict(item='the index half of the 43 computed keys',
                 blocking='`String.Concat(<prefix>, index)` builds the key at run '
                          'time; the index is bounded by the shop/quest array length, '
                          'which is a different decode'),
            dict(item='stored values',
                 blocking='device state, not in the APK — MODEL_NOT_MEASURED runtime'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_game_store_keys.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                               sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          calls=payload['census']['calls'],
                          literal=payload['census']['literal_keys'],
                          prefixes=payload['census']['computed_prefixes'],
                          unknown=payload['census']['unknown_calls'])))


if __name__ == '__main__':
    main()
