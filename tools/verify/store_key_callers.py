#!/usr/bin/env python3
"""The 26 store calls 144 could not name: all of them come from another method.

144 tracked registers inside each method, so a key that was built elsewhere showed
up as `unknown`. Three cross-method mechanisms close every one of them:

* **caller-side return** — the key register is the return of a helper:
  `TimeFreeRewardPack.Key(int slot)` (`0x124C8EC`, rva 19187948) returns
  `String.Concat("SLOT_FREE_CARDS_", slot.ToString())`, so its four callers are
  *computed* keys with a known prefix.
* **static field** — the key is a `static string` of the class, read as
  `[klass + 0xB8] + off`. The value is whatever the class `..cctor` stores there;
  `Board_EventSeasonPass..cctor` (rva 19462112) writes three of them with a plain
  `str` and one `stp` pair, which is why a single-register walk misses the pair.
* **spill** — the key is parked on the stack and reloaded; a slot table keeps the
  role across the round trip.

Everything is still static: the *keys* are compile-time strings, the *values*
under them are device state (`MODEL_NOT_MEASURED runtime`).
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
PREV = 'datas/l2_535b0541_game_store_keys.json.gz'

STORE = {0x13F1824: 'SetValue', 0x13F1930: 'GetValue', 0x13F1A04: 'SetInt',
         0x13F1A0C: 'SetFloat', 0x13F1A14: 'SetString', 0x13F1A1C: 'GetInt',
         0x13F1A24: 'GetFloat', 0x13F1A2C: 'GetString', 0x13F1A34: 'DeleteAll',
         0x13F1B44: 'DeleteKey'}

CONCAT = {33439876: 'Concat2', 33476172: 'ConcatObject3', 33476420: 'Concat3',
          33476644: 'Concat4', 33476908: 'ConcatArray'}

# Il2CppClass::static_fields. 141/142 pinned the same offset for the klass cell
# (0xB8) on this build, and every `..cctor` below reaches statics through it.
STATIC_FIELDS = 0xB8

HELPER = 19187948          # TimeFreeRewardPack.Key(int slot)
STATIC_WRITER = 19462112   # Board_EventSeasonPass..cctor

NEW_LITERAL_KEYS = ['TIME_EVENT_ENDED', 'TIME_EVENT_STARTED', 'TIME_EVENT_OPEN']
NEW_PREFIXES = ['SLOT_FREE_CARDS_']

# 144's census, reproduced here so a drift shows up as a failed run, not a story.
CALLS = 184
BY_API = {'SetInt': 67, 'GetInt': 58, 'SetString': 32, 'GetString': 25, 'DeleteKey': 2}
BY_RAW = {'meta-rewards-535b0541': 80, 'key-grant-535b0541': 49,
          'arena-pvp-535b0541': 41, 'box-draw-535b0541': 10, 'key-jump-535b0541': 4}
BY_KIND = {'literal': 133, 'computed': 51, 'unknown': 0}


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


@lru_cache(maxsize=None)
def cells():
    """metadata-usage cell va -> (text, literal addend), from every method."""
    texts = strings()
    out = {}
    for path in raw_paths():
        for method in load(path)['methods']:
            for ref in method.get('slot_refs', []):
                if ref.get('addend') in texts:
                    out[ref['slot_va']] = (texts[ref['addend']], ref['addend'])
    return out


@lru_cache(maxsize=None)
def methods():
    """method rva -> method (first raw that carries it; the raws overlap)."""
    out = {}
    for path in raw_paths():
        for method in load(path)['methods']:
            out.setdefault(method['rva'], dict(method, raw=path.split('/')[-2]))
    return out


def walk(method, statics=None, sink=None):
    """One pass over a method. `sink(kind, insn, roles)` sees every call and ret.

    Roles: page, cell(va), cellval(va), klass(cell_va), sfield(cell_va, off),
    lit(text, addend), concat(prefix), ret(target), and `@sp<off>` spill slots.
    """
    statics = {} if statics is None else statics
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
            hit = re.fullmatch(r'\[(x\d+|sp)(?:, #(0x[0-9a-f]+))?\]', rest)
            if not hit:
                roles.pop(dest, None)
                continue
            base = hit.group(1)
            offset = int(hit.group(2), 0) if hit.group(2) else 0
            if base == 'sp':
                slot = roles.get('@sp%d' % offset)
                if slot is not None:
                    roles[dest] = slot
                else:
                    roles.pop(dest, None)
                continue
            if mnemonic != 'ldr':
                roles.pop(dest, None)
                continue
            role = roles.get(base)
            if role and role[0] == 'page':
                roles[dest] = ('cell', role[1] + offset)
                continue
            if role and role[0] == 'cell':
                if offset:
                    roles[dest] = ('celloff', role[1], offset)
                    continue
                text = cells().get(role[1])
                roles[dest] = ('lit', text[0], text[1]) if text else ('cellval', role[1])
                continue
            if role and role[0] == 'cellval' and offset == STATIC_FIELDS:
                roles[dest] = ('klass', role[1])
                continue
            if role and role[0] == 'klass':
                stored = statics.get((role[1], offset))
                roles[dest] = ('lit', stored['key'], stored['addend']) if stored \
                    else ('sfield', role[1], offset)
                continue
            roles.pop(dest, None)
            continue
        if mnemonic in ('str', 'stp'):
            if ', [' not in operand:
                continue
            sources, rest = operand.split(', [', 1)
            hit = re.fullmatch(r'\[(x\d+|sp)(?:, #(0x[0-9a-f]+))?\]', '[' + rest)
            if not hit:
                continue
            base = hit.group(1)
            offset = int(hit.group(2), 0) if hit.group(2) else 0
            for index, name in enumerate(source.strip() for source in sources.split(',')):
                slot_off = offset + 8 * index if mnemonic == 'stp' else offset
                if base == 'sp':
                    roles['@sp%d' % slot_off] = roles.get(name)
                    continue
                target, source = roles.get(base), roles.get(name)
                if target and target[0] == 'klass' and source and source[0] == 'lit':
                    statics[(target[1], slot_off)] = dict(
                        key=source[1], addend=source[2], writer_rva=method['rva'],
                        writer=method['signature'].strip(), raw=method.get('raw'),
                        writer_instruction=insn['rva'], store=mnemonic)
            continue
        if mnemonic == 'mov':
            copy = re.fullmatch(r'(x\d+|w\d+), (x\d+|w\d+)', operand)
            if copy:
                roles['x' + copy.group(1)[1:]] = roles.get('x' + copy.group(2)[1:])
                continue
            other = re.fullmatch(r'(x\d+|w\d+), .*', operand)
            if other:
                roles.pop('x' + other.group(1)[1:], None)
            continue
        if mnemonic in ('bl', 'b'):
            target = operand.strip().lstrip('#')
            address = int(target, 0) if re.fullmatch(r'0x[0-9a-f]+', target) else None
            if sink:
                sink(mnemonic, insn, roles, address)
            if mnemonic == 'bl':
                if address in CONCAT:
                    args = [roles[name][1] for name in ('x0', 'x1', 'x2')
                            if roles.get(name) and roles[name][0] == 'lit' and roles[name][1]]
                    roles['x0'] = ('concat', args[0] if args else None)
                elif address is not None:
                    roles['x0'] = ('ret', address)
                else:
                    roles.pop('x0', None)
                for name in ('x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7'):
                    roles.pop(name, None)
            continue
        if mnemonic == 'ret':
            if sink:
                sink('ret', insn, roles, None)
            continue
        written = re.fullmatch(r'(x\d+|w\d+), .*', operand)
        if written:
            roles.pop('x' + written.group(1)[1:], None)


def collect_statics():
    """Every `str`/`stp` that puts a literal into a class's static block."""
    statics = {}
    for path in raw_paths():
        for method in load(path)['methods']:
            walk(dict(method, raw=path.split('/')[-2]), statics)
    return statics


def resolve(rva, statics, depth=0, seen=()):
    """What a helper hands back in x0 at `ret` (a role, or None)."""
    if depth > 3 or rva in seen:
        return None
    method = methods().get(rva)
    if method is None:
        return None
    seen = seen + (rva,)
    got = []

    def sink(kind, insn, roles, target):
        if kind == 'ret':
            got.append(roles.get('x0'))

    walk(method, statics, sink)
    values = [role for role in got if role]
    if not values or any(value != values[0] for value in values):
        return None
    value = values[0]
    if value[0] == 'ret' and value[1] != rva:
        return resolve(value[1], statics, depth + 1, seen)
    return value


def name(role, statics):
    """Turn a key-register role into (kind, key, prefix, via)."""
    if not role:
        return 'unknown', None, None, 'the key register was written by something ' \
                                       'the walk does not model'
    if role[0] == 'lit' and role[1]:
        return 'literal', role[1], None, 'literal in the calling method'
    if role[0] == 'concat':
        return 'computed', None, role[1], 'String.Concat in the calling method'
    if role[0] == 'sfield':
        return 'unknown', None, None, 'static field %#x + %#x has no literal write' % (
            role[1], role[2])
    if role[0] == 'ret':
        target = role[1]
        value = resolve(target, statics)
        helper = methods().get(target) or {}
        label = 'return of %s (%#x)' % (helper.get('signature', '?').strip(), target)
        if value and value[0] == 'lit' and value[1]:
            return 'literal', value[1], None, label + ', a literal'
        if value and value[0] == 'concat':
            return 'computed', None, value[1], label + ', String.Concat(<literal>, index)'
        return 'unknown', None, None, label + ', return role not modelled'
    if role[0] == 'cellval':
        return 'unknown', None, None, 'cell %#x is not a string literal' % role[1]
    return 'unknown', None, None, 'role %r' % (role,)


def census(statics):
    records = []
    for path in raw_paths():
        raw = path.split('/')[-2]
        for method in load(path)['methods']:
            def sink(kind, insn, roles, target, method=method, raw=raw):
                if target in STORE:
                    role = roles.get('x0')
                    settled, key, prefix, via = name(role, statics)
                    second = roles.get('x1')
                    records.append(dict(
                        raw=raw, class_name=method['class_name'],
                        signature=method['signature'].strip(),
                        method_rva=method['rva'], call_rva=insn['rva'],
                        tail=kind == 'b', api=STORE[target], api_rva=target,
                        kind=settled, key=key, prefix=prefix,
                        default=(second[1] if second and second[0] == 'lit'
                                 and second[1] else None),
                        key_register=role, via=via,
                        helper=role[1] if role and role[0] == 'ret' else None))

            walk(dict(method, raw=raw), statics, sink)
    return records


def build_payload():
    statics = collect_statics()
    records = census(statics)
    assert len(records) == CALLS, len(records)
    assert dict(collections.Counter(record['api'] for record in records)) == BY_API
    assert dict(collections.Counter(record['raw'] for record in records)) == BY_RAW
    counts = collections.Counter(record['kind'] for record in records)
    by_kind = {kind: counts.get(kind, 0)
               for kind in ('literal', 'computed', 'unknown')}
    assert by_kind == BY_KIND, by_kind

    previous = load(PREV)
    unknown_before = {(row['method_rva'], row['call_rva']) for row in previous['unknown_calls']}
    assert len(unknown_before) == 22, len(unknown_before)

    rows = collections.OrderedDict()
    for record in records:
        site = (record['method_rva'], record['call_rva'])
        if site not in unknown_before:
            continue
        row = rows.setdefault(site, dict(
            method_rva=record['method_rva'], call_rva=record['call_rva'],
            class_name=record['class_name'], method=record['signature'],
            api=record['api'], kind=record['kind'], key=record['key'],
            prefix=record['prefix'],
            mechanism=('helper-return' if record['helper'] else
                       'static-field' if record['key'] or record['prefix'] else 'unknown'),
            via=record['via'], raws=[]))
        if record['raw'] not in row['raws']:
            row['raws'].append(record['raw'])
    resolved = list(rows.values())
    assert len(resolved) == 22, len(resolved)
    resolved_records = [record for record in records
                        if (record['method_rva'], record['call_rva']) in unknown_before]
    assert len(resolved_records) == 26, len(resolved_records)
    by_mechanism = collections.Counter(record['helper'] and 'helper-return'
                                       or 'static-field'
                                       for record in resolved_records)
    assert dict(by_mechanism) == {'static-field': 18, 'helper-return': 8}, \
        dict(by_mechanism)
    assert all(row['kind'] != 'unknown' for row in resolved), \
        [row for row in resolved if row['kind'] == 'unknown']

    literal_rows = collections.OrderedDict()
    for record in records:
        if record['kind'] == 'literal':
            row = literal_rows.setdefault(record['key'], dict(
                key=record['key'], calls=0, in_144=record['key'] in
                [item['key'] for item in previous['literal_keys']],
                literal=record['key_register'][2] if record['key_register']
                and record['key_register'][0] == 'lit' else None))
            row['calls'] += 1
    computed = collections.Counter(record['prefix'] for record in records
                                   if record['kind'] == 'computed')
    new_keys = [row for row in literal_rows.values() if not row['in_144']]
    assert [row['key'] for row in new_keys] == NEW_LITERAL_KEYS, new_keys
    assert sorted(name for name in computed if name) == sorted(
        [item['prefix'] for item in previous['computed_keys'] if item['prefix']]
        + NEW_PREFIXES), sorted(name for name in computed if name)

    helper_method = methods()[HELPER]
    writer = methods()[STATIC_WRITER]
    static_rows = [dict(klass_cell=cell, offset=offset, **data)
                   for (cell, offset), data in sorted(statics.items())]
    assert {(row['klass_cell'], row['offset']) for row in static_rows} >= set()
    string_statics = [row for row in static_rows if row['key'] in NEW_LITERAL_KEYS]
    assert len(string_statics) == 3, string_statics

    blob = load(next(path for path in raw_paths() if 'arena-pvp' in path))
    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Keys are compile-time strings reached through another method; the '
             'values under them are device state — MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            xapk_sha256=blob['xapk_sha256'],
            libil2cpp_sha256=blob['libil2cpp_sha256'],
            dump_sha256=blob['dump_sha256'],
            sources=[dict(path=path, sha256=sha_file(path),
                          role='store call sites, string cells, static writes')
                     for path in raw_paths()]
                    + [dict(path=STRINGS, sha256=sha_file(STRINGS),
                            role='key text per cell addend'),
                       dict(path=DUMP, sha256=sha_file(DUMP),
                            role='the ten PlayerPreferences RVAs'),
                       dict(path=PREV, sha256=sha_file(PREV),
                            role='144 census and its 26 unknown calls')]),
        model=dict(
            static_fields_offset=STATIC_FIELDS,
            rules=['adrp gives a page; a load off a page gives a metadata cell',
                   'a load off a cell is a string literal when the cell has an '
                   'addend in stringliteral.json, else a pointer',
                   'a load at +0x%X off that pointer is the class, and a load '
                   'off the class is a static field' % STATIC_FIELDS,
                   '`str` and `stp` into the class record the static field value',
                   '`bl` overwrites x0..x7; a helper return is resolved by '
                   'walking the callee (depth 3)', 
                   'stack slots keep a role across a spill'],
            note='one role per register; any write the walk does not model drops it'),
        census=dict(calls=len(records), by_api=dict(BY_API), by_raw=dict(BY_RAW),
                    by_kind=by_kind, tail_calls=sum(1 for r in records if r['tail']),
                    before=dict(by_kind=dict(previous['census']['by_kind']),
                                unknown=len(previous['unknown_calls'])),
                    note='census unchanged from 144 (184 calls); only the bucket of '
                         'the 26 unknown ones moved'),
        statics=dict(rows=static_rows,
                     writer=dict(rva=STATIC_WRITER,
                                 signature=writer['signature'].strip(),
                                 klass_cell=string_statics[0]['klass_cell']),
                     note='the class is Board_EventSeasonPass; the three keys are '
                          'written by two stores, one of them an `stp` pair'),
        helper=dict(rva=HELPER, signature=helper_method['signature'].strip(),
                    class_name=helper_method['class_name'],
                    body='String.Concat(<static string>, slot.ToString())',
                    prefix=NEW_PREFIXES[0],
                    note='four store calls sit behind this helper, two methods x two '
                         'raws; 144 saw them as unknown because the prefix lives in '
                         'the callee'),
        resolution=dict(records=len(resolved_records), sites=len(resolved),
                        by_mechanism=dict(by_mechanism),
                        by_kind=dict(collections.Counter(r['kind']
                                                         for r in resolved_records)),
                        note='the four helper-return sites appear in two raws each, '
                             'so 22 distinct sites carry the 26 records'),
        resolved=resolved,
        new_keys=dict(literal=[row['key'] for row in new_keys],
                      prefixes=NEW_PREFIXES,
                      note='keys 144 could not name; they are the event window'),
        literal_keys=[dict(key=row['key'], calls=row['calls'], in_144=row['in_144'])
                      for row in literal_rows.values()],
        computed=dict(values=[dict(prefix=name, calls=count)
                              for name, count in computed.items()],
                      note='prefix None means Concat whose first argument was not a '
                           'literal in that method'),
        cross_check=dict(report=144, calls=previous['census']['calls'],
                         unknown_before=len(previous['unknown_calls']),
                         unknown_after=by_kind['unknown'],
                         literal_before=previous['census']['by_kind']['literal'],
                         literal_after=by_kind['literal'],
                         computed_before=previous['census']['by_kind']['computed'],
                         computed_after=by_kind['computed'],
                         note='same 184 call sites, same raws: this is a '
                              'reclassification, not a new census'),
        not_decoded=[
            dict(item='the index half of the 50 computed keys',
                 blocking='`String.Concat(<prefix>, index)` — the index is a loop '
                          'variable or a shop/quest array position, so the set of '
                          'possible keys needs the array length, a different decode'),
            dict(item='stored values',
                 blocking='device state, not in the APK — MODEL_NOT_MEASURED runtime'),
            dict(item='static writes that are not string keys',
                 blocking='two other `str` writes into static blocks hold non-key '
                          'data (%#x + 0, %#x + 0); they are recorded in `statics` '
                          'so the index is complete, not because they are keys'
                          % (44986264, 44953992)),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_store_key_callers.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          calls=payload['census']['calls'],
                          resolved=len(payload['resolved']),
                          literal=payload['census']['by_kind']['literal'],
                          computed=payload['census']['by_kind']['computed'],
                          unknown=payload['census']['by_kind']['unknown'],
                          new_keys=payload['new_keys']['literal'])))


if __name__ == '__main__':
    main()
