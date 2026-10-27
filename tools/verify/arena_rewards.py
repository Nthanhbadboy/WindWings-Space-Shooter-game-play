#!/usr/bin/env python3
"""`ArenaManager.rewards`: the ten shipped strings, and who reads them.

139 read the array as a handle — "string[10]" — and left two questions: the text of
each element, and the consumer. Both close here without new binaries:

* `ArenaManager..cctor` (rva 22692372) allocates `new string[10]` and then stores ten
  string literals into element slots `+0x20 + 8*i`. The literals are the reward tables
  themselves, and every one of them is in the pinned `stringliteral.json`.
* the same cell the class uses for its own statics (`0x2AE19D0`) appears in two other
  methods, and both read statics `+0x38` — that is the array, not a copy of it:
  `Board_Arena.SetRewards` (passes `rewards[rank]` to `GetRewards`) and
  `Popup_ArenaInfo.SetInfo` (uses `Length` to bound a row loop).
* `Board_Arena.GetRewards(string rankSetup, int userRank)` (rva 22795496) is the parser,
  and its literals spell the format out: strip `]`, `#`, `"`, split on `;`, then `[`,
  then `,`, then `:`, and pick `Medal` / `Gems`; the placement half is compared as a
  range when it carries `-`, otherwise as a single number.

The text of the ten strings is therefore not an interpretation — it is a shipped
constant, and the shipped parser agrees with how 139 read it (60 of 60 rows).
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

import meta_rewards as MR  # noqa: E402

ARENA_RAW = 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'
STRINGS = 'reverse-engineering/il2cpp/stringliteral.json'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
PREV = 'datas/l2_535b0541_arena_statics.json.gz'

KLASS_CELL = 0x2AE19D0          # ArenaManager's type usage, from its own ..cctor
STATICS_PTR = 0xB8
REWARDS_OFFSET = 0x38           # ArenaManager statics: rewards (string[10])
ARRAY_DATA = 0x20               # instance array payload starts here
NEWARR_HELPER = 0x110D09C
ELEMENT_WIDTH = 8
EXPECTED_REWARDS = 10


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def strings():
    return {int(row['address'], 16): row['value']
            for row in json.loads((ROOT / STRINGS).read_text())}


@functools.lru_cache(maxsize=None)
def method(klass, needle):
    for row in load(ARENA_RAW)['methods']:
        if row['class_name'] == klass and needle in row['signature']:
            return row
    raise AssertionError('%s %s not in the raw' % (klass, needle))


@functools.lru_cache(maxsize=None)
def cctor_of(klass='ArenaManager'):
    """The class's own (static) constructor, not the cached `<>c` one."""
    for row in load(ARENA_RAW)['methods']:
        if row['class_name'] == klass and '.cctor' in row['signature']:
            return row
    raise AssertionError('%s..cctor not in the raw' % klass)


@functools.lru_cache(maxsize=None)
def owner(rva):
    """(class, signature) for a method RVA, read out of dump.cs."""
    lines = MR.dump_text().split('\n')
    current = None
    for index, line in enumerate(lines):
        decl = re.search(r'\b(?:class|struct) ([\w<>`.=]+)[^\n]*// TypeDefIndex: \d+\s*$', line)
        if decl and '{' not in line:
            current = decl.group(1)
        if 'RVA: 0x%X ' % rva in line:
            return current, lines[index + 1].strip()
    return None, None


# ---------------------------------------------------------------- the array
def cctor_elements():
    """The ten `str <literal>, [arr, #off]` writes that fill rewards, in order."""
    cctor = cctor_of()
    insns = cctor['instructions']
    slots = {ref['rva']: ref for ref in cctor['slot_refs']}

    # Each element is `adrp/ldr cell` -> `ldr x9,[x9]` -> `str x9,[x0,#off]`.
    pending = {}
    rows = []
    for insn in insns:
        adrp = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', insn['op_str'])
        if insn['mnemonic'] == 'adrp' and adrp:
            pending[adrp.group(1)] = int(adrp.group(2), 0)
            continue
        load = re.fullmatch(r'(x\d+), \[(x\d+), #(0x[0-9a-f]+)\]', insn['op_str'])
        if insn['mnemonic'] == 'ldr' and load:
            dest, base, offset = load.group(1), load.group(2), int(load.group(3), 16)
            if base in pending:
                pending[dest] = pending[base] + offset
                if dest != base:
                    pending.pop(base, None)
            continue
        deref = re.fullmatch(r'(x\d+), \[(x\d+)\]', insn['op_str'])
        if insn['mnemonic'] == 'ldr' and deref:
            src = pending.get(deref.group(2))
            if isinstance(src, int) and src >= 0x2A00000:
                pending[deref.group(1)] = src
            continue
        store = re.fullmatch(r'(x\d+), \[(x\d+), #(0x[0-9a-f]+)\]', insn['op_str'])
        if insn['mnemonic'] == 'str' and store:
            source, base, offset = store.group(1), store.group(2), int(store.group(3), 16)
            cell = pending.get(source)
            if base != 'x0' or offset < ARRAY_DATA or cell is None:
                continue
            ref = next((ref for ref in cctor['slot_refs']
                        if ref['slot_va'] == cell), None)
            addend = ref['addend'] if ref else None
            rows.append(dict(index=(offset - ARRAY_DATA) // ELEMENT_WIDTH,
                             cell=cell, addend=addend,
                             text=strings().get(addend),
                             store_rva=insn['rva'], store_offset=offset))

    # Sanity: the allocation right before the fills.
    newarr = [insn for insn in insns
              if insn['mnemonic'] == 'bl'
              and int(insn['op_str'].lstrip('#'), 16) == NEWARR_HELPER]
    length = [insn for insn in insns
              if insn['mnemonic'] == 'mov' and insn['op_str'].startswith('w1, #0xa')]
    assert len(rows) == EXPECTED_REWARDS, rows
    assert [row['index'] for row in rows] == list(range(EXPECTED_REWARDS))
    assert all(row['text'] for row in rows)
    return dict(rows=rows, newarr_rva=newarr[0]['rva'] if newarr else None,
                length_instruction=length[0]['rva'] if length else None,
                note='element index = (store offset - 0x20) / 8; the allocation is the '
                     '`bl` to the array helper immediately before the fills')


PLACEMENT = re.compile(r'#([0-9]+)(?:-([0-9]+))?\[Medal:([0-9]+),Gems:([0-9]+)\]')


def parse_text(text):
    """The same walk the shipped parser does, written out on the text."""
    bands = []
    for chunk in text.split(';'):
        cleaned = chunk.replace(']', '').replace('#', '').replace('"', '')
        placement, payload = cleaned.split('[')
        fields = {}
        for pair in payload.split(','):
            name, value = pair.split(':')
            fields[name] = int(value)
        low, _, high = placement.partition('-')
        bands.append(dict(placement=placement, low=int(low),
                          high=int(high) if high else int(low),
                          medal=fields['Medal'], gems=fields['Gems']))
    return bands


def previous_bands():
    prev = load(PREV)['rewards']
    out = {}
    for row in prev['rows']:
        out[row['rank']] = [(band['placement'], band['medal'], band['gems'])
                            for band in row['bands']]
    return out


# ---------------------------------------------------------------- consumers
def consumers():
    """Methods that reach `ArenaManager.rewards` through the class's own statics."""
    rows = []
    for target in load(ARENA_RAW)['methods']:
        insns = target['instructions']
        roles, hits = {}, []
        for insn in insns:
            mnemonic, operand = insn['mnemonic'], insn['op_str']
            adrp = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', operand)
            if mnemonic == 'adrp' and adrp:
                roles[adrp.group(1)] = ('page', int(adrp.group(2), 0))
                continue
            load_ = re.fullmatch(r'(x\d+), \[(x\d+)(?:, #(0x[0-9a-f]+))?\]', operand)
            if mnemonic in ('ldr', 'ldrsw') and load_:
                dest, base = load_.group(1), load_.group(2)
                offset = int(load_.group(3) or '0', 16)
                role = roles.get(base)
                if role and role[0] == 'page' and role[1] + offset == KLASS_CELL:
                    roles[dest] = ('cell',)
                elif role and role[0] == 'cell' and offset == 0:
                    roles[dest] = ('klass',)
                elif role and role[0] == 'klass' and offset == STATICS_PTR:
                    roles[dest] = ('statics',)
                elif role and role[0] == 'statics':
                    hits.append((insn['rva'], mnemonic, offset, operand))
                    roles.pop(dest, None)
                else:
                    roles.pop(dest, None)
                continue
            store_ = re.fullmatch(r'(?:[xw]\d+|wzr|xzr), \[(x\d+)(?:, #(0x[0-9a-f]+))?\]', operand)
            if mnemonic in ('str', 'strb', 'strh') and store_:
                base = store_.group(1)
                offset = int(store_.group(2) or '0', 16)
                role = roles.get(base)
                if role and role[0] == 'statics':
                    hits.append((insn['rva'], mnemonic, offset, operand))
                continue
            named = re.match(r'(x\d+),', operand)
            if named and mnemonic not in ('str', 'strb', 'strh', 'cmp', 'tst'):
                roles.pop(named.group(1), None)
        if not hits:
            continue
        fields = sorted({offset for _, _, offset, _ in hits})
        read = [row for row in hits if row[1] in ('ldr', 'ldrsw')]
        written = [row for row in hits if row[1] in ('str', 'strb')]
        rows.append(dict(class_name=target['class_name'],
                         signature=target['signature'].strip(), rva=target['rva'],
                         size=target['size'], fields=[hex(value) for value in fields],
                         reads_rewards=any(offset == REWARDS_OFFSET for _, _, offset, _ in read),
                         writes_rewards=any(offset == REWARDS_OFFSET for _, _, offset, _ in written),
                         access=[dict(rva=rva, mnemonic=mnemonic, offset=hex(offset),
                                      operand=operand)
                                 for rva, mnemonic, offset, operand in hits]))
    return rows


def rewards_reader():
    """`Board_Arena.SetRewards`: index, guard, and the call that consumes the string."""
    target = method('Board_Arena', 'SetRewards')
    insns = target['instructions']
    start = next(k for k, insn in enumerate(insns)
                 if insn['mnemonic'] == 'ldr' and insn['op_str'].endswith('#0x38]'))
    window = insns[start:start + 16]
    calls = []
    for insn in window:
        if insn['mnemonic'] == 'bl':
            rva = int(insn['op_str'].lstrip('#'), 16)
            klass, signature = owner(rva)
            calls.append(dict(rva=rva, klass=klass, signature=signature))
    return dict(method=dict(rva=target['rva'], size=target['size'],
                            signature=target['signature'].strip()),
                read_rva=insns[start]['rva'],
                window=[dict(rva=insn['rva'], mnemonic=insn['mnemonic'],
                             operand=insn['op_str']) for insn in window],
                calls=calls,
                rule='idx = userProfile.arenaRank (+0x1c); guard against '
                     'RankUpIndexs.Length, idx > 8 and userProfile.status (+0x28) > '
                     'RankUpIndexs[idx]; then rewards[idx] and +0x28 go to GetRewards')


def parser():
    """`Board_Arena.GetRewards`: the literals that define the format."""
    target = method('Board_Arena', 'GetRewards')
    literals = []
    for ref in target['slot_refs']:
        addend = ref.get('addend')
        literals.append(dict(instruction_rva=ref['rva'], cell=ref['slot_va'],
                             addend=addend, text=strings().get(addend)))
    splits = [dict(rva=insn['rva'], char=chr(int(insn['op_str'].split('#')[1], 16)))
              for insn in target['instructions']
              if insn['mnemonic'] == 'mov' and re.fullmatch(r'w1, #0x[0-9a-f]+',
                                                            insn['op_str'])
              and 0x20 <= int(insn['op_str'].split('#')[1], 16) < 0x7f]
    return dict(method=dict(rva=target['rva'], size=target['size'],
                            signature=target['signature'].strip()),
                literals=literals,
                separators=splits,
                rule='Replace("]","") Replace("#","") Replace("\\"","") then Split(\';\') '
                     '-> Split(\'[\') -> Split(\',\') -> Split(\':\'); "Medal" goes to '
                     'ArenaRewards+0x10 and "Gems" to +0x14; the placement is a range '
                     'when it contains \'-\', otherwise a single number')


def census(consumers):
    """Which statics offset is read, which is written, and what 139 called it."""
    names = {hex(row['offset']): row['name']
             for row in load(PREV)['layout']['arena_manager']}
    out = {}
    for row in consumers:
        for access in row['access']:
            slot = out.setdefault(access['offset'], dict(
                offset=access['offset'], field=names.get(access['offset']),
                reads=[], writes=[]))
            bucket = 'writes' if access['mnemonic'].startswith('str') else 'reads'
            entry = dict(rva=access['rva'], klass=row['class_name'])
            if entry not in slot[bucket]:
                slot[bucket].append(entry)
    return [out[key] for key in sorted(out, key=lambda text: int(text, 16))]


def map_pool_bridge():
    """`RankMapsIndex` is filled from the per-rank config's `indexMap`, not from a literal."""
    target = method('Board_Arena.<>c__DisplayClass69_0', 'WaitToLoadConfigMaps')
    insns = target['instructions']
    read = next(insn for insn in insns
                if insn['mnemonic'] == 'ldr' and insn['op_str'].endswith('#0x24]'))
    write = next(insn for insn in insns
                 if insn['mnemonic'] == 'str' and insn['op_str'].endswith('#0x20]'))
    return dict(method=dict(rva=target['rva'], size=target['size'],
                            signature=target['signature'].strip()),
                read=dict(rva=read['rva'], operand=read['op_str'],
                          field='ArenaRankSetup.indexMap (+0x24)'),
                write=dict(rva=write['rva'], operand=write['op_str'],
                           field='ArenaManager.RankMapsIndex (+0x20)'),
                rule='each `ArenaRankSetup` carries its own `indexMap`, and the callback '
                     'for the last one loads writes it straight into `RankMapsIndex`; the '
                     'map-pool index is therefore served per rank, not compiled in')


def build():
    array = cctor_elements()
    parsed = []
    for row in array['rows']:
        bands = parse_text(row['text'])
        parsed.append(dict(row, bands=bands, band_count=len(bands),
                           shape=re.sub(r'[0-9]+', 'N', row['text'])[:40]))

    prev = previous_bands()
    comparisons = []
    for row in parsed:
        mine = [(band['placement'], band['medal'], band['gems']) for band in row['bands']]
        comparisons.append(dict(rank=row['index'], text_bands=mine,
                                report_139=prev[row['index']],
                                match=mine == prev[row['index']]))
    assert all(row['match'] for row in comparisons)

    used = consumers()
    reader = rewards_reader()
    slots = census(used)
    bridge = map_pool_bridge()
    formatter = parser()
    prev_artifact = load(PREV)

    checks = []
    checks.append(dict(check='ten-elements', passed=len(array['rows']) == EXPECTED_REWARDS))
    checks.append(dict(check='element-order-from-offsets',
                       passed=[row['index'] for row in array['rows']]
                              == list(range(EXPECTED_REWARDS))))
    checks.append(dict(check='every-literal-is-pinned',
                       passed=all(row['text'] for row in array['rows'])))
    checks.append(dict(check='every-rank-has-six-bands',
                       passed=[row['band_count'] for row in parsed] == [6] * EXPECTED_REWARDS))
    checks.append(dict(check='text-matches-139',
                       passed=all(row['match'] for row in comparisons)))
    checks.append(dict(check='monotonic-ladder',
                       passed=all(parsed[rank]['bands'][0]['medal']
                                  < parsed[rank + 1]['bands'][0]['medal']
                                  for rank in range(EXPECTED_REWARDS - 1))))
    checks.append(dict(check='two-consumers',
                       passed=sorted(row['class_name'] for row in used
                                     if row['reads_rewards'] and '.cctor' not in row['signature'])
                              == ['Board_Arena', 'Popup_ArenaInfo']))
    checks.append(dict(check='only-the-cctor-writes-it',
                       passed=[row['class_name'] for row in used if row['writes_rewards']]
                              == ['ArenaManager']))
    checks.append(dict(check='nine-methods-touch-the-statics', passed=len(used) == 9))
    checks.append(dict(check='six-offsets-are-written',
                       passed=sorted(row['offset'] for row in slots if row['writes'])
                              == ['0x0', '0x18', '0x20', '0x28', '0x30', '0x38']))
    checks.append(dict(check='census-covers-every-field-139-named',
                       passed=[row['field'] for row in slots]
                              == ['IsOpen', 'SeasonTimes', 'RankMapsIndex', 'RankUpIndexs',
                                  'RankDropIndexs', 'rewards']))
    checks.append(dict(check='map-pool-index-comes-from-the-rank-setup',
                       passed=bridge['read']['field'] == 'ArenaRankSetup.indexMap (+0x24)'
                              and bridge['write']['field']
                              == 'ArenaManager.RankMapsIndex (+0x20)'))
    checks.append(dict(check='reader-is-setrewards',
                       passed='SetRewards' in reader['method']['signature']))
    checks.append(dict(check='reader-calls-getrewards',
                       passed=any('GetRewards' in (call['signature'] or '')
                                  for call in reader['calls'])))
    checks.append(dict(check='parser-separators',
                       passed={row['char'] for row in formatter['separators']}
                              == {';', '[', ',', ':', '-'}))
    checks.append(dict(check='parser-names-both-fields',
                       passed={row['text'] for row in formatter['literals']}
                              >= {'Medal', 'Gems', ']', '#', '"'}))
    assert all(row['passed'] for row in checks), [row for row in checks
                                                 if not row['passed']]

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='The ten reward strings are shipped constants and the shipped parser reads '
             'them with the format below; 139\'s reading of the same array is reproduced '
             '60 rows for 60. Who actually wins what in a match is '
             'MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            sources=[dict(path=path, sha256=sha_file(path))
                     for path in (ARENA_RAW, STRINGS, DUMP, PREV)],
            libil2cpp_sha256=load(ARENA_RAW)['libil2cpp_sha256'],
            xapk_sha256=load(ARENA_RAW)['xapk_sha256'],
            string_literals=len(strings())),
        array=array,
        rewards=parsed,
        parse=dict(format='#<low>[-<high>][Medal:<int>,Gems:<int>] joined by ";"',
                   steps=['Replace("]", "")', 'Replace("#", "")', 'Replace(\'"\', "")',
                          'Split(\';\')', 'Split(\'[\')', 'Split(\',\')',
                          'Split(\':\')', 'int.Parse'],
                   placement='range when the placement contains \'-\', else equality',
                   arena_rewards_fields=dict(medal=0x10, gems=0x14),
                   evidence=formatter),
        consumers=used,
        census=slots,
        census_boundary=dict(
            covered='single-register `ldr`/`str`/`strb`/`strh` off the statics base',
            not_covered='`.cctor`\'s `stur d0,[x8,#4]` and `stp ..., [x8,#0x10]`, which '
                        'cover `MaxRoomCount`/`MinUserCount` and `SeasonSummaryTime` and '
                        'are already pinned in 139',
            refill=dict(method='Board_Arena.GetConfigs', rva=22782048,
                        stores=[22782328, 22782576, 22782600],
                        rule='`SeasonTimes` (+0x18), `RankUpIndexs` (+0x28) and '
                             '`RankDropIndexs` (+0x30) are re-allocated and installed from '
                             'the served `ArenaConfig` strings on every config load; only '
                             '`rewards` is written once, by `.cctor`')),
        map_pool=bridge,
        reader=reader,
        cross_checks=dict(rows=sum(row['band_count'] for row in parsed),
                          match_139=all(row['match'] for row in comparisons),
                          first_band_by_rank=[row['bands'][0]['medal'] for row in parsed],
                          last_band_by_rank=[row['bands'][-1]['medal'] for row in parsed],
                          previous_artifact_rewards=int(prev_artifact['rewards']['count'])),
        checks=checks,
        confirmations=[
            dict(item='139 `+0x20 RankMapsIndex` had no writer in the read census',
                 result='found — `Board_Arena.<>c__DisplayClass69_0` (rva 22807856) stores '
                        '`ArenaRankSetup.indexMap` into it; `+0x0 IsOpen` and `+0x20` are '
                        'the only statics the read-only walk could not see written'),
            dict(item='139 `rewards` = string[10] array handle',
                 result='confirmed — ten literals, and the format of each one is a '
                        'semicolon-joined list of six placement bands'),
            dict(item='139 band table (medal/gems per placement)',
                 result='confirmed 60/60 by reading the shipped strings themselves'),
            dict(item='148 #11 `rewards` consumer',
                 result='closed — `Board_Arena.SetRewards` reads statics +0x38 and passes '
                        'rewards[arenaRank] to `GetRewards`; `Popup_ArenaInfo.SetInfo` '
                        'reads the same cell for its Length'),
        ],
        open_items=[
            dict(item='which band a player lands in during a real season',
                 blocking='the code proves the lookup rule; the placement input is the '
                          'served rank and the played result — MODEL_NOT_MEASURED runtime'),
            dict(item='the value of the first guard (`RankUpIndexs`)',
                 blocking='`RankUpIndexs` is null in the build and filled by '
                          '`Board_Arena.GetConfigs` from the served `RankSplit` string, so '
                          'the guard cannot be evaluated statically'),
            dict(item='`ArenaUserProfile.status` is used as a position',
                 blocking='the field at +0x28 is declared `status` yet is compared against '
                          'the band bounds as if it were the player\'s placement; the name '
                          'and the use disagree and neither is resolved here'),
        ],
    )


def main():
    parser_ = argparse.ArgumentParser()
    parser_.add_argument('--output', default='datas/l2_535b0541_arena_rewards.json.gz')
    args = parser_.parse_args()
    payload = build()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    target.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size,
                          sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                          rewards=len(payload['rewards']),
                          bands=payload['cross_checks']['rows'],
                          checks_passed=sum(1 for row in payload['checks'] if row['passed']),
                          checks_total=len(payload['checks']),
                          top=[row['bands'][0]['medal'] for row in payload['rewards']])))


if __name__ == '__main__':
    main()
