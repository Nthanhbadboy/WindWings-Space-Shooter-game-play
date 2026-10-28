#!/usr/bin/env python3
"""One correction and one timer: the shop constructor *does* write `MaxStockCount`.

153 reported that `MaxStockCount` (+0x98) is read as the buy cap but never
written, and 156 leaned on that. The write exists — it is just not a `str w`:

    ldr  q0, [x8, #0xb90]     // literal 10, 1, 50, 1
    stur q0, [x19, #0x98]     // one 128-bit store covers 0x98, 0x9C, 0xA0, 0xA4

so the constructor ships the shop's whole economy block: `MaxStockCount` 10,
`ItemPlayerValue` 1, `ItemPlayerCost` 50, `ItemDroneValue` 1, plus
`ItemDroneCost` 30 from a separate `str w8, [x19, #0xA8]`, two `int[3]` arrays
and `timeToReset` = 12600.0. All five ints are private and carry no
`[SerializeField]`, so nothing in prefab data overrides them.

The same constructor value drives the reset clock: `OnEnable` reads
`MyLibrary.GetTotalSecondsTravelTime("TIME_TO_RESET_ARENA_SHOP")` (PVP:
`TIME_TO_RESET_PVP_SHOP`), and `elapsed == -1` or `elapsed >= 12600.0` runs
`ResetShop()`, otherwise `InitShop()`, then `UpdateSystemTimeSaved(key)`.
The shop therefore refreshes every 3.5 hours.
"""
import argparse
import functools
import gzip
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import arena_rewards as AR  # noqa: E402

NATIVE = 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
PREV153 = 'datas/l2_535b0541_shop_stock_layout.json.gz'

SHOPS = {'Arena_Shop': dict(ctor=22735024, onenable=22727788,
                            key='TIME_TO_RESET_ARENA_SHOP', key_cell=46031920),
         'PVP_Shop': dict(ctor=19943896, onenable=19936844,
                          key='TIME_TO_RESET_PVP_SHOP', key_cell=46031928)}
BLOCK = [('MaxStockCount', 0x98), ('ItemPlayerValue', 0x9C),
         ('ItemPlayerCost', 0xA0), ('ItemDroneValue', 0xA4)]
DRONE_COST = ('ItemDroneCost', 0xA8)
ARRAYS = [('ItemResourceValues', 0xB0), ('ItemResourceCost', 0xB8)]
TIMER_FIELD = 0xF8
GET_TRAVEL = 'GetTotalSecondsTravelTime'
SET_TRAVEL = 'UpdateSystemTimeSaved'


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def methods():
    return load(NATIVE)['methods']


def method(rva):
    return next(row for row in methods() if row['rva'] == rva)


def text(insn):
    return insn['mnemonic'] + ' ' + insn['op_str']


def field_block(klass):
    """`(name, offset, declared, serialized)` for the shipped default block."""
    lines = AR.MR.dump_text().split('\n')
    start = next(i for i, line in enumerate(lines)
                 if line.startswith('public class %s :' % klass))
    rows, serialized = {}, False
    for line in lines[start + 1:]:
        got = line.strip()
        if got.startswith('// Methods') or got == '}':
            break
        if got in ('[SerializeField]', '[HideInInspector]'):
            serialized = True
            continue
        match = re.match(r'(?:public|private|protected|internal)\s+(?:static\s+)?'
                         r'(\S+)\s+(\w+);\s*// (0x[0-9A-F]+)$', got)
        if match:
            rows[match.group(2)] = dict(offset=int(match.group(3), 16),
                                        declared_type=match.group(1),
                                        serialized=serialized,
                                        word=got.split(';')[0].strip())
            serialized = False
            continue
        if got and not got.startswith('['):
            serialized = False
    return rows


def constructors():
    out = {}
    for klass, want in SHOPS.items():
        row = method(want['ctor'])
        insns = row['instructions']
        assert row['class_name'] == klass and '.ctor' in row['signature']
        load_insn = next(insn for insn in insns
                         if insn['mnemonic'] == 'ldr' and insn['op_str'].startswith('q0,'))
        literal = next(item for item in row['literals']
                       if item['instruction_rva'] == load_insn['rva'])
        values = struct.unpack('<4i', bytes.fromhex(literal['hex']))
        wide = next(insn for insn in insns
                    if insn['mnemonic'] == 'stur' and insn['op_str'].endswith('#0x98]'))
        drone = next(insn for insn in insns
                     if insn['mnemonic'] == 'str' and insn['op_str'].endswith('#0xa8]'))
        drone_value_insn = insns[insns.index(drone) - 1]
        high = next(insn for insn in insns
                    if insn['mnemonic'] == 'movk' and '0x40c8' in insn['op_str'])
        low = insns[insns.index(high) - 1]
        timer_store = next(insn for insn in insns
                           if insn['mnemonic'] == 'str' and insn['op_str'].endswith('#0xf8]'))
        arrays = [insn for insn in insns if insn['mnemonic'] == 'mov'
                  and insn['op_str'] == 'w1, #3']
        init_arrays = [insn for insn in insns if insn['mnemonic'] == 'bl'
                       and AR.owner(int(insn['op_str'].lstrip('#'), 16))[1]
                       and 'InitializeArray' in AR.owner(int(insn['op_str'].lstrip('#'), 16))[1]]
        packed = (int(high['op_str'].split('#')[1].split(',')[0], 16) << 48) | \
            int(low['op_str'].split('#')[1], 16)
        out[klass] = dict(
            rva=row['rva'], size=row['size'], signature=row['signature'].strip(),
            load=dict(rva=load_insn['rva'], op=text(load_insn)),
            literal=dict(va=literal['va'], hex=literal['hex'], ints=list(values)),
            wide_store=dict(rva=wide['rva'], op=text(wide),
                            covers=[hex(offset) for _, offset in BLOCK]),
            drone_cost=dict(field=DRONE_COST[0], offset=hex(DRONE_COST[1]),
                            value=int(drone_value_insn['op_str'].split('#')[1], 16),
                            rva=drone['rva'],
                            op=text(drone_value_insn) + ' ; ' + text(drone)),
            arrays=dict(fields=[dict(name=name, offset=hex(offset))
                                for name, offset in ARRAYS],
                        lengths=[int(insn['op_str'].split('#')[1], 16) for insn in arrays],
                        initialize_array_calls=[insn['rva'] for insn in init_arrays]),
            timer=dict(field=field_block(klass)['timeToReset']['word'],
                       offset=hex(TIMER_FIELD),
                       seconds=struct.unpack('<d', packed.to_bytes(8, 'little'))[0],
                       store_rva=timer_store['rva'],
                       op=text(low) + ' ; ' + text(high) + ' ; ' + text(timer_store)),
        )
        assert len(arrays) == 2 and len(init_arrays) == 2, (klass, arrays, init_arrays)
    return out


def timer(klass):
    want = SHOPS[klass]
    row = method(want['onenable'])
    insns = row['instructions']
    strings = {ref['addend']: AR.strings().get(ref['addend']) for ref in row['slot_refs']}
    keys = [value for value in strings.values() if value and value.startswith('TIME_TO_RESET')]
    assert keys and set(keys) == {want['key']}, keys
    calls = {}
    for insn in insns:
        if insn['mnemonic'] != 'bl':
            continue
        target = int(insn['op_str'].lstrip('#'), 16)
        operator, signature = AR.owner(target)
        if not signature:
            continue
        if GET_TRAVEL in signature:
            calls['get_elapsed'] = dict(rva=insn['rva'], target=target,
                                        signature=signature.strip())
        elif SET_TRAVEL in signature:
            calls['save_time'] = dict(rva=insn['rva'], target=target,
                                      signature=signature.strip())
        elif signature.strip() == 'public void InitShop() { }':
            calls['init'] = dict(rva=insn['rva'], target=target)
        elif signature.strip() == 'private void ResetShop() { }':
            calls['reset'] = dict(rva=insn['rva'], target=target)
    threshold_load = next(insn for insn in insns
                          if insn['mnemonic'] == 'ldr' and insn['op_str'].endswith('#0xf8]'))
    sentinel = next(insn for insn in insns
                    if insn['mnemonic'] == 'fmov' and insn['op_str'] == 'd1, #-1.00000000')
    compare = next(insn for insn in insns
                   if insn['mnemonic'] == 'fcmp' and insn['op_str'] == 'd0, d1')
    branch = next(insn for insn in insns if insn['mnemonic'] == 'b.ge')
    equal = next(insn for insn in insns if insn['mnemonic'] == 'b.eq')
    skip = next(insn for insn in insns
                if insn['mnemonic'] == 'b' and insn['rva'] < calls['save_time']['rva']
                and int(insn['op_str'].lstrip('#'), 16) > calls['save_time']['rva'])
    key_cell = int(want['key_cell'])
    refs = [ref['rva'] for ref in row['slot_refs'] if ref['addend'] == key_cell]
    read_rva = max(rva for rva in refs if rva < calls['get_elapsed']['rva'])
    stamp_rva = max(rva for rva in refs if rva < calls['save_time']['rva'])
    other = sorted({ref['addend'] for ref in row['slot_refs']} - {key_cell})
    return dict(onenable=dict(rva=row['rva'], size=row['size'],
                              signature=row['signature'].strip()),
                key=dict(name=want['key'], cell=key_cell,
                         slot_va=next(ref['slot_va'] for ref in row['slot_refs']
                                      if ref['addend'] == key_cell),
                         refs=refs, read_rva=read_rva, stamp_rva=stamp_rva,
                         unused_refs=[rva for rva in refs
                                      if rva not in (read_rva, stamp_rva)],
                         note='the same cell is read at the top and stamped at the '
                              'bottom; one key per shop. Extra slot refs are recorded '
                              'verbatim but a slot ref alone is not proof of a use.'),
                other_strings=[dict(cell=cell, value=AR.strings().get(cell),
                                    refs=[ref['rva'] for ref in row['slot_refs']
                                          if ref['addend'] == cell])
                               for cell in other],
                threshold=dict(field='timeToReset', offset=hex(TIMER_FIELD),
                               ldr_rva=threshold_load['rva'], op=text(threshold_load)),
                sentinel=dict(rva=sentinel['rva'], op=text(sentinel) + ' ; ' + text(compare)),
                branches=dict(not_equal=dict(rva=equal['rva'], op=text(equal),
                                             target=int(equal['op_str'].lstrip('#'), 16)),
                              enough=dict(rva=branch['rva'], op=text(branch),
                                          target=int(branch['op_str'].lstrip('#'), 16))),
                init_skip=dict(rva=skip['rva'], op=text(skip),
                               target=int(skip['op_str'].lstrip('#'), 16),
                               lands_after=calls['save_time']['rva'],
                               effect='InitShop() returns without stamping the clock — '
                                      'only a reset re-bases the stored time'),
                calls=calls,
                rule='elapsed = GetTotalSecondsTravelTime(key); if elapsed == -1 (no '
                     'record) or elapsed >= timeToReset (12600.0) -> ResetShop() then '
                     'UpdateSystemTimeSaved(key); else InitShop() and the branch over '
                     'the stamp leaves the stored time untouched')


POPUPS = ['Popup_ArenaShopExchange', 'Popup_PVPShopExchange', 'Popup_Exchange']


def popup_family():
    """The exchange popups: same field shape, only two of the three are in the slices."""
    lines = AR.MR.dump_text().splitlines()
    spans = [(row['rva'], row['rva'] + row['size']) for row in methods()]
    low, high = min(start for start, _ in spans), max(end for _, end in spans)
    out = []
    for name in POPUPS:
        head = next(i for i, line in enumerate(lines)
                    if line.startswith('public class %s :' % name))
        fields, rvas = [], []
        for line in lines[head + 1:]:
            got = line.strip()
            if got == '}':
                break
            match = re.match(r'(?:public|private|protected|internal)\s+(?:static\s+)?'
                             r'(\S+)\s+(\w+);\s*// (0x[0-9A-F]+)$', got)
            if match:
                fields.append(dict(name=match.group(2), offset=hex(int(match.group(3), 16)),
                                   declared_type=match.group(1)))
            routine = re.match(r'// RVA: (0x[0-9A-F]+)', got)
            if routine:
                rvas.append(int(routine.group(1), 16))
        inside = [rva for rva in rvas if low <= rva <= high]
        out.append(dict(class_name=name,
                        typedef_index=int(re.search(r'TypeDefIndex: (\d+)',
                                                    lines[head]).group(1)),
                        fields=fields, method_count=len(rvas),
                        first_rva=min(rvas), last_rva=max(rvas),
                        methods_in_slices=len(inside), slice_bounds=[low, high]))
    return out


def writes_census():
    """Every store that touches +0x98 anywhere in the slice."""
    rows = []
    for row in methods():
        for insn in row['instructions']:
            if insn['mnemonic'].startswith('st') and insn['op_str'].endswith('#0x98]'):
                rows.append(dict(class_name=row['class_name'],
                                 signature=row['signature'].strip(),
                                 method_rva=row['rva'], rva=insn['rva'],
                                 op=text(insn)))
    return rows


def build():
    ctor = constructors()
    clocks = {klass: timer(klass) for klass in SHOPS}
    stores = writes_census()
    fields = field_block('Arena_Shop')
    previous = load(PREV153)

    shipped = {}
    for name, offset in BLOCK:
        row = fields[name]
        assert row['offset'] == offset and row['declared_type'] == 'int'
        assert not row['serialized'], row
        shipped[name] = dict(offset=hex(offset), declared=row['word'],
                             serialized=False,
                             value=ctor['Arena_Shop']['literal']['ints'][
                                 [item[1] for item in BLOCK].index(offset)])
    drone = fields[DRONE_COST[0]]
    assert drone['offset'] == DRONE_COST[1] and not drone['serialized']
    shipped[DRONE_COST[0]] = dict(offset=hex(DRONE_COST[1]), declared=drone['word'],
                                  serialized=False,
                                  value=ctor['Arena_Shop']['drone_cost']['value'])
    for name, offset in ARRAYS:
        assert fields[name]['offset'] == offset and not fields[name]['serialized']
        shipped[name] = dict(offset=hex(offset), declared=fields[name]['word'],
                             serialized=False, length=3)
    assert fields['timeToReset']['offset'] == TIMER_FIELD
    assert fields['timeToReset']['declared_type'] == 'double'

    checks = []
    checks.append(dict(check='both-constructors-are-216-bytes',
                       passed={klass: (row['size'], row['signature'])
                               for klass, row in ctor.items()}
                              == {'Arena_Shop': (216, 'public void .ctor() { }'),
                                  'PVP_Shop': (216, 'public void .ctor() { }')}))
    checks.append(dict(check='same-literal-in-both',
                       passed=ctor['Arena_Shop']['literal'] == ctor['PVP_Shop']['literal']
                              and ctor['Arena_Shop']['literal']['va'] == 7838608))
    checks.append(dict(check='four-ints-are-10-1-50-1',
                       passed=ctor['Arena_Shop']['literal']['ints'] == [10, 1, 50, 1]))
    checks.append(dict(check='one-wide-store-writes-the-block',
                       passed=[row['wide_store']['op'] for row in ctor.values()]
                              == ['stur q0, [x19, #0x98]'] * 2))
    checks.append(dict(check='block-maps-to-five-unsigned-defaults',
                       passed=(shipped['MaxStockCount']['value'],
                               shipped['ItemPlayerValue']['value'],
                               shipped['ItemPlayerCost']['value'],
                               shipped['ItemDroneValue']['value'],
                               shipped['ItemDroneCost']['value']) == (10, 1, 50, 1, 30)))
    checks.append(dict(check='none-of-them-is-serialized',
                       passed=not any(row['serialized'] for row in shipped.values())))
    checks.append(dict(check='two-int3-arrays',
                       passed={klass: (row['arrays']['lengths'],
                                       len(row['arrays']['initialize_array_calls']))
                               for klass, row in ctor.items()}
                              == {'Arena_Shop': ([3, 3], 2), 'PVP_Shop': ([3, 3], 2)}))
    checks.append(dict(check='timer-is-12600-seconds',
                       passed={klass: row['timer']['seconds'] for klass, row in ctor.items()}
                              == {'Arena_Shop': 12600.0, 'PVP_Shop': 12600.0}
                              and 12600.0 / 3600 == 3.5))
    checks.append(dict(check='only-the-two-constructors-store-0x98',
                       passed=[row['class_name'] for row in stores]
                              == ['Arena_Shop', 'PVP_Shop']))
    checks.append(dict(check='153-said-there-was-no-writer',
                       passed='no store instruction targets +0x98'
                              in previous['stock_cap']['rule']))
    checks.append(dict(check='each-shop-own-reset-key',
                       passed={klass: (row['key']['name'], row['key']['cell'],
                                       len(row['key']['refs']))
                               for klass, row in clocks.items()}
                              == {'Arena_Shop': ('TIME_TO_RESET_ARENA_SHOP', 46031920, 3),
                                  'PVP_Shop': ('TIME_TO_RESET_PVP_SHOP', 46031928, 3)}))
    checks.append(dict(check='timer-gates-reset-vs-init',
                       passed=all(row['threshold']['ldr_rva'] < row['branches']['enough']['rva']
                                  and row['branches']['enough']['target']
                                  == row['calls']['reset']['rva'] - 4
                                  and row['calls']['init']['rva'] < row['branches']['enough']['target']
                                  < row['calls']['save_time']['rva']
                                  for row in clocks.values())))
    checks.append(dict(check='init-path-skips-the-clock-stamp',
                       passed=all(row['init_skip']['rva'] < row['calls']['reset']['rva']
                                  and row['init_skip']['target'] > row['calls']['save_time']['rva']
                                  for row in clocks.values())))
    checks.append(dict(check='countdown-format-string',
                       passed=all(any(entry['value'] == '###,###,##0'
                                      for entry in row['other_strings'])
                                  for row in clocks.values())))
    checks.append(dict(check='minus-one-also-resets',
                       passed=all(row['sentinel']['op'] == 'fmov d1, #-1.00000000 ; '
                                                           'fcmp d0, d1'
                                  for row in clocks.values())))
    checks.append(dict(check='both-branches-land-on-reset',
                       passed=all(row['branches']['not_equal']['target']
                                  == row['branches']['enough']['target']
                                  for row in clocks.values())))
    family = popup_family()
    checks.append(dict(check='two-popups-in-the-slices-one-outside',
                       passed=[row['methods_in_slices'] for row in family]
                              == [family[0]['method_count'], family[1]['method_count'], 0]
                              and family[2]['last_rva'] < family[2]['slice_bounds'][0]))
    checks.append(dict(check='the-third-popup-carries-the-same-rewards-field',
                       passed='rewards' in [row['name'] for row in family[2]['fields']]
                              and 'maxStock' in [row['name'] for row in family[2]['fields']]))
    assert all(row['passed'] for row in checks), [row for row in checks if not row['passed']]

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='`MaxStockCount` (+0x98) does have a writer: the shop constructor stores a '
             'four-int literal with one `stur q0`, so the shop ships 10 stock units, '
             'value 1 / cost 50 for player items and value 1 / cost 30 for drones, two '
             '`int[3]` tables, and a 12600 s reset clock. All of it is private and '
             'unserialized, so prefab data cannot override it. 153 had reported the '
             'field as unwritten.',
        provenance=dict(
            sources=[dict(path=rel, sha256=sha_file(rel))
                     for rel in (NATIVE, DUMP, PREV153)],
            libil2cpp_sha256=load(NATIVE)['libil2cpp_sha256'],
            xapk_sha256=load(NATIVE)['xapk_sha256'],
            string_literals=len(AR.strings())),
        constructors=ctor,
        shipped=shipped,
        timer=clocks,
        stores=stores,
        popup_family=family,
        correction=dict(
            target=153,
            claim='`MaxStockCount` (+0x98) is read as the buy cap but has no writer '
                  'in the 2499 dumped methods',
            why_wrong='the writer is `stur q0, [x19, #0x98]` — a 128-bit store, so a '
                      'search for `str w?, [x?, #0x98]` cannot see it',
            evidence=dict(arena_ctor=22735024, arena_store=22735140,
                          pvp_ctor=19943896, pvp_store=19944012,
                          literal_va=7838608, values=[10, 1, 50, 1]),
            consequence='the slot text ceiling is the constant 10 minus the sold '
                        'counter, while the exchange popup ceiling is '
                        '`EventRewards.stock` minus the same counter'),
        checks=checks,
        confirmations=[
            dict(item='156: the slot text is `MaxStockCount - sold`',
                 result='confirmed and now quantified — `MaxStockCount` is 10, shipped '
                        'by the constructor, so that text counts down from 10'),
            dict(item='153: the shop refreshes by writing the stock key to 0',
                 result='confirmed as the action, and now timed — `ResetShop` runs when '
                        'the stored elapsed time reaches 12600 s (3.5 h) or is absent'),
            dict(item='149/150: the arena shop and the PvP shop are one class twice',
                 result='confirmed on the constructor — both are 216 bytes and share one '
                        'literal, so the economy defaults are identical for both shops'),
        ],
        open_items=[
            dict(item='whether the shipped 10 stock units and the season `stock` field '
                      'are ever equal',
                 blocking='`MaxStockCount` is a build-time 10 and `EventRewards.stock` '
                          'comes from event-pass data; nothing in the dump compares '
                          'them — MODEL_NOT_MEASURED runtime'),
            dict(item='what happens to `sold` when the reset fires mid-session',
                 blocking='`OnEnable` is what re-reads the clock, so a shop that stays '
                          'open across the 3.5 h boundary is not covered by this path'),
            dict(item='what `MyLibrary.GetTotalSecondsTravelTime` does with the key when '
                      'the device clock moves backwards',
                 blocking='the helper (0x1420A38) is in the shared library, not in these '
                          'slices, so only the call and the -1 sentinel are evidence'),
            dict(item='which wallet the third exchange popup spends (`Popup_Exchange`, '
                      'TypeDefIndex 693)',
                 blocking='all of its methods sit below the lowest slice RVA and it is not '
                          'one of the eight dumped slices, so its buy path is not consulted '
                          'here'),
        ],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_shop_ctor_timer.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    target.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(
        bytes=target.stat().st_size,
        sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        shipped={name: row.get('value', row.get('length'))
                 for name, row in payload['shipped'].items()},
        timer=payload['constructors']['Arena_Shop']['timer']['seconds'],
        checks_passed=sum(1 for row in payload['checks'] if row['passed']),
        checks_total=len(payload['checks']))))


if __name__ == '__main__':
    main()
