#!/usr/bin/env python3
"""Who hands out quest keys, and how. STATIC only.

Reports 130/131 fixed the *cost* side of the quest boxes (30 keys each, prices
6/20/100 gems per missing key). This one answers the *supply* side by combining
two pinned scans that no scoped family extraction can give on its own:

* a whole-`.text` branch scan (`call_sites.py`) for the six `GameDatas`
  KeyCount accessors, so every caller is known regardless of its class;
* the `SaveDataReward` jump table, so a pack value index can be tied to the
  KeyCount block that consumes it.

Result: keys are only ever *added* by reward screens applying a pack value at
index 16/17/18, and only ever *taken* by the box-opening button. No timer, no
idle regeneration.
"""
import argparse
import bisect
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

CALLS = 'reverse-engineering/raw/call-sites-535b0541/calls.json.gz'
JUMP = 'reverse-engineering/raw/key-jump-535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'

TABLE_VA = 0x779C4A          # jump table used by SaveDataReward's dispatch
TABLE_BASE_PAD = 0x124CA98   # `adr x10, #0x124ca98`

# a method gets the first role whose test passes, most specific first
ROLE_RULES = (
    ('spend', lambda cls, sig, sets: cls.startswith('Board_QuestRewards')
     and 'SaveDataReward' not in sig),
    ('grant_via_pack_value', lambda cls, sig, sets: 'SaveDataReward' in sig),
    ('grant_direct', lambda cls, sig, sets: bool(sets)),
    ('serialization', lambda cls, sig, sets: cls.startswith('DataPrefs')),
    ('cheat_guard', lambda cls, sig, sets: 'IsHasCheatResources' in sig),
    ('display_or_state', lambda cls, sig, sets: True),
)


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def dump_names():
    """rva -> declaration line, for naming call targets."""
    lines = gzip.decompress((ROOT / DUMP).read_bytes()).decode().split('\n')
    out = {}
    for index, line in enumerate(lines):
        rva = re.match(r'\s*// RVA: 0x([0-9A-F]+)', line)
        if rva and index + 1 < len(lines):
            out[int(rva.group(1), 16)] = lines[index + 1].strip()
    return out


def method_index():
    """sorted [(rva, class, signature)] so a call site can be attributed."""
    lines = gzip.decompress((ROOT / DUMP).read_bytes()).decode().split('\n')
    rows, current = [], ''
    for index, line in enumerate(lines):
        match = re.search(r'(?:class|struct|enum) (\S+).*?// TypeDefIndex:', line)
        if match:
            current = match.group(1)
        rva = re.match(r'\s*// RVA: 0x([0-9A-F]+)', line)
        if rva:
            rows.append((int(rva.group(1), 16), current,
                         lines[index + 1].strip() if index + 1 < len(lines) else ''))
    rows.sort()
    return rows, [row[0] for row in rows]


def role_of(cls, signature, targets):
    sets = [name for name in targets if name.startswith('set_')]
    for name, test in ROLE_RULES:
        if test(cls, signature, sets):
            return name
    raise AssertionError('unreachable')


def build():
    calls, jump = load(CALLS), load(JUMP)
    rows, rvas = method_index()
    names = {t['rva']: t['name'] for t in calls['targets']}

    hits = []
    for hit in calls['hits']:
        index = bisect.bisect_right(rvas, hit['rva']) - 1
        if index < 0:
            raise AssertionError('call site before the first method')
        rva, cls, signature = rows[index]
        hits.append(dict(hit, target_name=names[hit['target']],
                         caller=dict(class_name=cls, method_rva=rva, signature=signature,
                                     role=role_of(cls, signature))))

    per_target = {}
    for hit in hits:
        bucket = per_target.setdefault(hit['target_name'], dict(bl=0, b=0, callers=set()))
        bucket[hit['kind']] += 1
        bucket['callers'].add((hit['caller']['class_name'], hit['caller']['method_rva']))
    summary = {name: dict(bl=b['bl'], b=b['b'], caller_methods=len(b['callers']))
               for name, b in per_target.items()}

    by_role = {}
    for hit in hits:
        row = by_role.setdefault(hit['caller']['role'], dict(hits=0, classes=set(),
                                                             methods=set()))
        row['hits'] += 1
        row['classes'].add(hit['caller']['class_name'])
        row['methods'].add((hit['caller']['class_name'], hit['caller']['method_rva']))
    roles = {name: dict(hits=row['hits'], classes=len(row['classes']),
                        methods=len(row['methods']),
                        class_names=sorted(row['classes'])) for name, row in by_role.items()}

    # --- jump table: which pack value index reaches which KeyCount block -----
    window = (jump.get('rodata_windows') or [None])[0]
    if not window or window['va'] != TABLE_VA:
        raise AssertionError('jump table window missing or moved')
    table = list(bytes.fromhex(window['hex']))
    if len(table) != 22:
        raise AssertionError('jump table length changed')

    save = next(m for m in jump['methods']
                if m['class_name'] == 'TimeFreeRewardPack' and 'SaveDataReward' in m['signature'])
    insns = save['instructions']
    by_rva = {one['rva']: one for one in insns}
    named = dump_names()
    default_pad = next((int(one['op_str'].lstrip('#'), 0) for one in insns[:40]
                        if one['mnemonic'] == 'b.hi'), None)
    if default_pad is None:
        raise AssertionError('dispatcher guard not found')

    def decode_pad(pad):
        """(getter, setter, adds_value) for the case block starting at `pad`."""
        calls = []
        for offset in range(0, 0x40, 4):
            one = by_rva.get(pad + offset)
            if not one or one['mnemonic'] not in ('bl', 'b'):
                continue
            target = int(one['op_str'].lstrip('#'), 0)
            calls.append((one['mnemonic'], target, named.get(target, f'rva {target}')))
        getter = next((c for c in calls if c[0] == 'bl'
                       and re.search(r'\b(get_|Get)', c[2])), None)
        setter = next((c for c in calls if c[0] == 'b'), None)
        adds = any(by_rva.get(pad + offset, {}).get('op_str') == 'w0, w0, w19'
                   for offset in range(0, 0x30, 4))
        return getter, setter, adds

    routing, blocks = {}, {}
    for index, byte in enumerate(table):
        pad = TABLE_BASE_PAD + 4 * byte
        if pad == default_pad:
            routing[index] = dict(pad=pad, getter=None, setter=None, add_rule=False,
                                  default=True)
            blocks.setdefault(('default', None, False), []).append(index)
            continue
        getter, setter, adds = decode_pad(pad)
        key = (getter[2] if getter else None, setter[2] if setter else None, adds)
        blocks.setdefault(key, []).append(index)
        routing[index] = dict(pad=pad, getter=(getter[2] if getter else None),
                              setter=(setter[2] if setter else None), add_rule=adds,
                            default=False)

    key_indices = {index: row['getter'] for index, row in routing.items()
                   if 'KeyCount' in (row['getter'] or '')}
    if key_indices != {16: 'public static int get_KeyCount0() { }',
                       17: 'public static int get_KeyCount1() { }',
                       18: 'public static int get_KeyCount2() { }'}:
        raise AssertionError(f'unexpected key routing: {key_indices}')
    for index in (16, 17, 18):
        if not routing[index]['add_rule']:
            raise AssertionError(f'index {index} does not add the pack value')
        if routing[index]['setter'] != f'public static void set_KeyCount{index - 16}(int value) {{ }}':
            raise AssertionError(f'index {index} does not write back KeyCount{index - 16}')

    arithmetic = {
        f'KeyCount{index - 16}': dict(index=index, pad=routing[index]['pad'],
                                      add='add w0, w0, w19',
                                      getter=routing[index]['getter'],
                                      setter=routing[index]['setter'])
        for index in (16, 17, 18)}

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Branch scan plus one pinned jump table. Nothing is executed; '
             'runtime amounts depend on which packs the player actually receives '
             '(MODEL_NOT_MEASURED runtime).',
        provenance=dict(
            sources=[dict(path=p, sha256=sha_file(p)) for p in (CALLS, JUMP, DUMP)],
            xapk_sha256=calls['provenance']['xapk_sha256'],
            libil2cpp_sha256=calls['provenance']['libil2cpp_sha256'],
            words_scanned=calls['method']['words_scanned'],
            segments=calls['method']['segments'],
            hits_total=len(hits)),
        targets=[dict(name=t['name'], rva=t['rva'], **summary.get(t['name'], {}))
                 for t in calls['targets']],
        roles=roles,
        supply=dict(
            rule='a reward screen applies one pack value per call: '
                 'set_KeyCountN(get_KeyCountN() + _value); index 16/17/18 selects N',
            index_routing={str(k): (v['getter'] or '').replace('public static int ', '')
                           .replace('public static void ', '').split('(')[0]
                           for k, v in routing.items()},
            default_pad=default_pad,
            default_indices=[k for k, v in routing.items() if v['default']],
            default_rule='indices that share the b.hi target fall through to `ret`: '
                         'SaveDataReward grants nothing for them',
            key_indices={str(k): v for k, v in key_indices.items()},
            table_hex=window['hex'],
            jump_table=dict(va=TABLE_VA, length=len(table), sha256=window['sha256'],
                            base_pad=TABLE_BASE_PAD,
                            rule='pad = 0x124ca98 + 4 * table[index], index <= 0x15'),
            method=dict(class_name='TimeFreeRewardPack', rva=save['rva'], size=save['size'],
                        signature=save['signature']),
            case_blocks={f'{getter} -> {setter}': indices
                         for (getter, setter, adds), indices in blocks.items()},
            arithmetic=arithmetic,
            spend=dict(rule='Board_QuestRewards.OnPressedButtonOpenNow subtracts '
                            'BoxKeyCost[typeBox] = 30 (report 129/130/131)',
                       callers=[h['rva'] for h in hits
                                if h['caller']['role'] == 'spend']),
            no_regeneration='no caller of set_KeyCountN adds a value that is not the '
                            'reward argument, and UpdateKey0/1/2 only animate the label',
        ),
        callers=[dict(call_rva=h['rva'], kind=h['kind'], target=h['target_name'],
                      class_name=h['caller']['class_name'],
                      method_rva=h['caller']['method_rva'],
                      signature=h['caller']['signature'], role=h['caller']['role'])
                 for h in hits],
        not_decoded=[
            dict(item='which packs a given player receives',
                 blocking='server/remote-config driven; MODEL_NOT_MEASURED runtime'),
            dict(item='per-call _value for the 20 SaveDataReward clones',
                 blocking='the argument comes from the pack table at runtime; the '
                          'rewrite (getter + value -> setter) is decoded, the operand is not'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_key_sources.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          hits=len(payload['callers']),
                          roles={k: v['methods'] for k, v in payload['roles'].items()},
                          routing=payload['supply']['index_routing'])))


if __name__ == '__main__':
    main()
