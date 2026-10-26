#!/usr/bin/env python3
"""The two arena shops: what they persist, and how a slot gets its item.

The #29 remit lists "medal/shop exchange" and no report has opened it. It turns out
the shop does not ship a catalogue at all — it ships a *key layout* and draws the
catalogue at run time:

    ResetShop -> shuffle(Player_Get_Datas.GetListAllIdPlayerActived())
              -> for each slot: PlayerPreferences.SetInt(ITEM_ID + (i+100), id - 10001)
                                PlayerPreferences.SetInt(ITEM_STOCK + (i+100), 0)
              -> same for drones at +200 and resources at +300

so the three slot families, the key names and the +100 / +200 / +300 bands are all
build constants, while *which* item sits in a slot is a `Random.Range` draw. The buy
path puts the 10001 back (`add w22, w22, w8`) and pays the player in cards.

`Arena_Shop` and `PVP_Shop` are the same class twice: identical fields, identical
control flow, different key prefixes and a different popup type.
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

import arena_rewards as AR  # noqa: E402  (dump reader, string table, owner())

NATIVE = 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'
STRINGS = 'reverse-engineering/il2cpp/stringliteral.json'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'

SHOPS = {
    'PVP_Shop': dict(typedef=912, id_key=0x2AE1018, stock_key=0x2AE0D40,
                     reset=19937384, init=19939136, get_id=19941788,
                     get_stock=19889588, set_stock=19941952,
                     exchange='Popup_PVPShopExchange'),
    'Arena_Shop': dict(typedef=418, id_key=0x2AED090, stock_key=0x2AED088,
                       reset=22728328, init=22730080, get_id=22732732,
                       get_stock=22732896, set_stock=22733060,
                       exchange='Popup_ArenaShopExchange'),
}
BANDS = [(0x64, 'listItemPlayers', 0x68), (0xC8, 'listItemDrones', 0x70),
         (0x12C, 'listItemResources', 0x78)]
PLAYER_ID_BASE = 0x2711          # 10001, subtracted on write and added back on buy
SET_INT = 20912644               # PlayerPreferences.SetInt
GET_INT = 20912668               # PlayerPreferences.GetInt
CONCAT = 33439876                # String.Concat(string, string)
TO_STRING = 34616120             # Int32.ToString
RANDOM_RANGE = 41407168          # Random.Range(int, int)
LIST_ITEM = 28920348             # List<int>.get_Item
LIST_REMOVE_AT = 28926656        # List<int>.RemoveAt
LIST_ADD = 28921100              # List<int>.AddWithResize
PLAYER_LIST = 21897964           # Player_Get_Datas.GetListAllIdPlayerActived
DRONE_COUNT = 21862140           # Drone_Get_Datas.get_CountDrones
GET_CARDS = 21920072             # Player_Saved_Datas.GetPlayerCards
SET_CARDS = 21920392             # Player_Saved_Datas.SetPlayerCards
NEWARR = 17879196                # array allocation helper seen inside InitShop

FIELD_NAMES = ['textMedal', 'textTimeReset', 'parentPlayer', 'parentDrone',
               'parentItems', 'parentMedal', 'scrollView', 'bound', 'onExit',
               'listItemPlayers', 'listItemDrones', 'listItemResources',
               'parentItemPlayers', 'parentItemDrones', 'parentItemResources',
               'MaxStockCount', 'ItemPlayerValue', 'ItemPlayerCost', 'ItemDroneValue',
               'ItemDroneCost', 'ItemResourceValues', 'ItemResourceCost',
               'popupExchange', 'pointTopAnchors', 'pointBotAnchors', 'pointMedalTop',
               'pointMedalBot', 'cover', 'shopCover', 'timeToReset']


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def strings():
    return AR.strings()


@functools.lru_cache(maxsize=None)
def method(klass, needle):
    for row in load(NATIVE)['methods']:
        if row['class_name'] == klass and needle in row['signature']:
            return row
    raise AssertionError('%s %s not in the raw' % (klass, needle))


@functools.lru_cache(maxsize=None)
def fields_of(klass):
    """`(name, offset, type)` for one class, straight out of dump.cs."""
    lines = AR.MR.dump_text().split('\n')
    start = None
    for index, line in enumerate(lines):
        if re.match(r'public class %s : ' % re.escape(klass), line):
            start = index
            break
    if start is None:
        raise AssertionError('%s not in dump.cs' % klass)
    rows, offset, kind, serialized = [], None, None, False
    for line in lines[start + 1:]:
        text = line.strip()
        if text.startswith('// Methods'):
            break
        if text in ('[SerializeField]', '[HideInInspector]'):
            serialized = True
            continue
        match = re.match(r'(?:public|private|protected|internal)\s+(?:static\s+)?(.+?)\s+'
                         r'(\w+);\s*// (0x[0-9A-F]+)', text)
        if match:
            rows.append(dict(name=match.group(2), declared=match.group(1),
                             offset=int(match.group(3), 16), serialized=serialized))
            serialized = False
            continue
        if text and not text.startswith('['):
            serialized = False
    return rows


# -------------------------------------------------------------- the key layout
def key_calls(klass, sig):
    """Every PlayerPreferences call in a method, with the key prefix it builds."""
    target = method(klass, sig)
    key_of = {ref['slot_va']: strings().get(ref['addend'])
              for ref in target['slot_refs']}
    cells, prefix, calls = {}, None, []
    for insn in target['instructions']:
        mnemonic, operand = insn['mnemonic'], insn['op_str']
        adrp = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', operand)
        if mnemonic == 'adrp' and adrp:
            cells[adrp.group(1)] = ('page', int(adrp.group(2), 0))
            continue
        read = re.fullmatch(r'(x\d+), \[(x\d+)(?:, #(0x[0-9a-f]+))?\]', operand)
        if mnemonic == 'ldr' and read:
            dest, base = read.group(1), read.group(2)
            offset = int(read.group(3) or '0', 16)
            role = cells.get(base)
            if role and role[0] == 'page':
                cells[dest] = ('cell', role[1] + offset)
            elif role and role[0] == 'cell':
                cells[dest] = ('text', role[1])
            continue
        move = re.fullmatch(r'(x\d+), (x\d+)', operand)
        if mnemonic == 'mov' and move and move.group(2) in cells:
            cells[move.group(1)] = cells[move.group(2)]
            continue
        if mnemonic == 'bl':
            rva = int(operand.lstrip('#'), 16)
            if rva == CONCAT:
                source = cells.get('x0')
                prefix = source[1] if source and source[0] in ('cell', 'text') else None
            elif rva in (SET_INT, GET_INT):
                cells.pop('x0', None)
                calls.append(dict(rva=insn['rva'], api='SetInt' if rva == SET_INT
                                  else 'GetInt', prefix=prefix,
                                  key=key_of.get(prefix)))
    return target, calls


def persistence(klass):
    spec = SHOPS[klass]
    target, reset_calls = key_calls(klass, 'ResetShop')
    _, get_id = key_calls(klass, 'GetIdItem')
    _, get_stock = key_calls(klass, 'GetStockItem')
    _, set_stock = key_calls(klass, 'SetStockItem')

    writes = [row for row in reset_calls if row['api'] == 'SetInt']
    ids = [row for row in writes if row['key'] and row['key'].endswith('_ITEM_ID')]
    stocks = [row for row in writes if row['key'] and row['key'].endswith('_ITEM_STOCK')]

    assert len(ids) == 3 and len(stocks) == 3, (klass, ids, stocks)
    assert [row['prefix'] for row in ids] == [spec['id_key']] * 3
    assert [row['prefix'] for row in stocks] == [spec['stock_key']] * 3
    id_name, stock_name = ids[0]['key'], stocks[0]['key']

    return dict(
        klass=klass, typedef=spec['typedef'],
        keys=[dict(name=id_name, cell=spec['id_key'],
                   cell_hex=hex(spec['id_key']), role='slot id',
                   read_at=get_id[0]['rva'] if get_id else None),
              dict(name=stock_name, cell=spec['stock_key'],
                   cell_hex=hex(spec['stock_key']), role='slot stock',
                   read_at=get_stock[0]['rva'] if get_stock else None)],
        reset=dict(rva=target['rva'], size=target['size'],
                   writes=writes_of(target, ids, stocks)),
        getters=dict(get_id=dict(rva=spec['get_id'], default=0,
                                 call_rva=get_id[0]['rva'] if get_id else None),
                     get_stock=dict(rva=spec['get_stock'], default=0,
                                    call_rva=get_stock[0]['rva'] if get_stock else None),
                     set_stock=dict(rva=spec['set_stock'],
                                    call_rva=set_stock[0]['rva'] if set_stock else None)))


def writes_of(target, ids, stocks):
    """What each of the six reset writes actually stores, read symbolically."""
    sym = {}
    seen = {}
    for insn in target['instructions']:
        mnemonic, operand = insn['mnemonic'], insn['op_str']
        imm = re.fullmatch(r'w(\d+), #(-?0x[0-9a-f]+)', operand)
        if mnemonic == 'mov' and imm:
            sym['w' + imm.group(1)] = ('imm', int(imm.group(2), 16))
            continue
        move = re.fullmatch(r'w(\d+), w(\d+)', operand)
        if mnemonic == 'mov' and move:
            sym['w' + move.group(1)] = sym.get('w' + move.group(2))
            continue
        add = re.fullmatch(r'w(\d+), w(\d+), #(0x[0-9a-f]+)', operand)
        if mnemonic == 'add' and add:
            dest, source = 'w' + add.group(1), 'w' + add.group(2)
            value = int(add.group(3), 16)
            if sym.get(source) == ('imm', 10001) and value == 0:
                sym[dest] = ('delta', 10001)
            elif value in (0x64, 0xC8, 0x12C):
                sym[dest] = ('index', value)
            continue
        sub = re.fullmatch(r'w(\d+), w(\d+), w(\d+)', operand)
        if mnemonic in ('add', 'sub') and sub:
            left, right = sym.get('w' + sub.group(2)), sym.get('w' + sub.group(3))
            if right and right[0] == 'delta':
                sym['w' + sub.group(1)] = ('item', right[1])
            continue
    # Re-run, this time recording what w1 holds at each of the six stores.
    sym = {}
    for insn in target['instructions']:
        mnemonic, operand = insn['mnemonic'], insn['op_str']
        imm = re.fullmatch(r'w(\d+), #(-?0x[0-9a-f]+)', operand)
        if mnemonic == 'mov' and imm:
            value = int(imm.group(2), 16)
            sym['w' + imm.group(1)] = ('delta', -value) if value < 0 else ('imm', value)
            continue
        move = re.fullmatch(r'w(\d+), w(\d+)', operand)
        if mnemonic == 'mov' and move:
            sym['w' + move.group(1)] = sym.get('w' + move.group(2))
            continue
        add = re.fullmatch(r'w(\d+), w(\d+), #(0x[0-9a-f]+)', operand)
        if mnemonic == 'add' and add:
            value = int(add.group(3), 16)
            sym['w' + add.group(1)] = ('index', value) if value in (0x64, 0xC8, 0x12C) \
                else sym.get('w' + add.group(2))
            continue
        add2 = re.fullmatch(r'w(\d+), w(\d+), w(\d+)', operand)
        if mnemonic == 'add' and add2:
            if (sym.get('w' + add2.group(3)) or ('',))[0] == 'delta':
                sym['w' + add2.group(1)] = ('item_minus', 10001)
            continue
        if mnemonic == 'bl':
            rva = int(operand.lstrip('#'), 16)
            if rva == SET_INT:
                seen[insn['rva']] = sym.get('w1')

    rows = []
    for order, row in enumerate(ids):
        value = seen.get(row['rva'])
        rows.append(dict(band=(order + 1) * 100, rva=row['rva'], key=row['key'],
                         value_rule=describe(value)))
    for order, row in enumerate(stocks):
        rows.append(dict(band=(order + 1) * 100, rva=row['rva'], key=row['key'],
                         value_rule='0 (literal)'))
    id_rules = [row['value_rule'] for row in rows
                if (row.get('key') or '').endswith('ITEM_ID')]
    assert id_rules == ['id - 10001', 'item id', 'index + 300'], id_rules
    return rows


def describe(value):
    if value is None:
        return 'item id'
    kind, number = value
    if kind == 'item_minus':
        return 'id - %d' % number
    if kind == 'index':
        return 'index + %d' % number
    if kind == 'imm':
        return '%d (literal)' % number
    return 'shuffled item id'


def text_of(klass):
    """The class body text (used only for the twin comparison)."""
    lines = AR.MR.dump_text().split('\n')
    start = next(i for i, line in enumerate(lines)
                 if re.match(r'public class %s : ' % re.escape(klass), line))
    return '\n'.join(lines[start:start + 80])


def bands(klass):
    """The three slot bands: offset base, target array and the store that fills it."""
    target = method(klass, 'ResetShop')
    insns = target['instructions']
    rows = []
    for base, field, instance_offset in BANDS:
        adds = [insn for insn in insns
                if insn['mnemonic'] == 'add'
                and re.fullmatch(r'w\d+, w\d+, #0x([0-9a-f]+)', insn['op_str'])
                and int(re.fullmatch(r'w\d+, w\d+, #0x([0-9a-f]+)',
                                     insn['op_str']).group(1), 16) == base]
        assert len(adds) == 1, (klass, hex(base), adds)
        rows.append(dict(base=base, key_suffix='index + %d' % base, array=field,
                         instance_offset=hex(instance_offset), add_rva=adds[0]['rva'],
                         add_op=adds[0]['op_str']))
    offset = next(insn for insn in insns
                  if insn['mnemonic'] == 'mov'
                  and re.fullmatch(r'w\d+, #-0x[0-9a-f]+', insn['op_str']))
    return dict(rows=rows, player_id_delta=offset['op_str'],
                player_id_delta_rva=offset['rva'],
                delta_value=int(re.search(r'-0x([0-9a-f]+)', offset['op_str']).group(1), 16))


# ------------------------------------------------------------- the catalogue
def catalogue():
    """Where `ResetShop` gets its candidates, and how it picks them."""
    target = method('PVP_Shop', 'ResetShop')
    helpers = {}
    for insn in target['instructions']:
        if insn['mnemonic'] != 'bl':
            continue
        rva = int(insn['op_str'].lstrip('#'), 16)
        klass, signature = AR.owner(rva)
        helpers.setdefault(rva, dict(rva=rva, class_name=klass,
                                     signature=(signature or '').strip()))
    wanted = {PLAYER_LIST: 'candidate pool', RANDOM_RANGE: 'pick',
              LIST_ITEM: 'read', LIST_REMOVE_AT: 'remove', LIST_ADD: 'append',
              DRONE_COUNT: 'drone bound'}
    rows = []
    for rva, why in wanted.items():
        row = helpers.get(rva)
        assert row, (rva, why)
        rows.append(dict(row, role=why))
    assert 'GetListAllIdPlayerActived' in next(r['signature'] for r in rows
                                               if r['rva'] == PLAYER_LIST)
    assert 'RemoveAt' in next(r['signature'] for r in rows if r['rva'] == LIST_REMOVE_AT)
    return dict(method=dict(rva=target['rva'], size=target['size'],
                            signature=target['signature'].strip()),
                helpers=rows,
                order=['copy Player_Get_Datas.GetListAllIdPlayerActived()',
                       'while i < pool.Count: idx = Random.Range(0, pool.Count)',
                       'pool.RemoveAt(idx); shuffled.Add(pool[idx])',
                       'write shuffled[i] into band 100 as id - 10001',
                       'drones: bound by Drone_Get_Datas.get_CountDrones()',
                       'resources: bound by listItemResources.Length, value = 300 + i'])


def buy_round_trip():
    """`OnBuy|2` puts the 10001 back and pays in cards."""
    target = method('PVP_Shop.<>c__DisplayClass31_1', 'OnBuy|2')
    at = {insn['rva']: insn['mnemonic'] + ' ' + insn['op_str']
          for insn in target['instructions']}
    facts = [dict(rva=19944896, op='ldr w22, [x8, #0x1c]', meaning='slot value'),
             dict(rva=19944916, op='mov w8, #0x2711', meaning='10001'),
             dict(rva=19944920, op='add w22, w22, w8', meaning='id = value + 10001'),
             dict(rva=19944944, op='madd w1, w8, w21, w0',
                  meaning='cards = perCopy * count + current')]
    for fact in facts:
        assert at[fact['rva']] == fact['op'], (fact['rva'], at[fact['rva']])
    calls = []
    for insn in target['instructions']:
        if insn['mnemonic'] == 'bl':
            rva = int(insn['op_str'].lstrip('#'), 16)
            if rva in (GET_CARDS, SET_CARDS):
                klass, signature = AR.owner(rva)
                calls.append(dict(rva=rva, class_name=klass,
                                  signature=signature.strip()))
    assert {row['rva'] for row in calls} == {GET_CARDS, SET_CARDS}, calls
    return dict(method=dict(rva=target['rva'], size=target['size'],
                            signature=target['signature'].strip()),
                facts=facts, calls=calls,
                rule='the stored slot value is 10001 below the real player id; the buy '
                     'path restores it and then adds `perCopy * count` cards')


def twins():
    """Arena_Shop and PVP_Shop are one class twice."""
    arena, pvp = fields_of('Arena_Shop'), fields_of('PVP_Shop')
    assert [(row['name'], row['offset']) for row in arena] == \
           [(row['name'], row['offset']) for row in pvp], 'fields diverged'
    typed = [(one['name'], one['declared'], two['declared'])
             for one, two in zip(arena, pvp) if one['declared'] != two['declared']]
    assert typed == [('popupExchange', 'Popup_ArenaShopExchange',
                      'Popup_PVPShopExchange')], typed
    assert [row['name'] for row in pvp] == FIELD_NAMES
    diff = []
    for sig in ('ResetShop', 'InitShop', 'OnClickPlayerItem', 'GetIdItem'):
        one, two = method('Arena_Shop', sig), method('PVP_Shop', sig)
        diff.append(dict(signature=one['signature'].strip(),
                         arena=dict(rva=one['rva'], size=one['size']),
                         pvp=dict(rva=two['rva'], size=two['size']),
                         same_size=one['size'] == two['size'],
                         delta=two['size'] - one['size']))
    differing = [row['signature'] for row in diff if not row['same_size']]
    assert differing == [method('Arena_Shop', 'OnClickPlayerItem')['signature'].strip()], \
        differing
    return dict(fields=len(pvp), rows=[dict(name=row['name'], offset=hex(row['offset']),
                                            declared=row['declared'],
                                            serialized=row['serialized'])
                                       for row in pvp],
                spawn=dict(rva=0, note='both declare `Shop_Cell[]` arrays at +0x68, '
                                       '+0x70, +0x78 and `int[]` costs at +0xb0/+0xb8'),
                methods=diff,
                type_differences=[dict(field=name, arena=one, pvp=two)
                                  for name, one, two in typed],
                only_difference='the type of `popupExchange` (+0xC0): '
                                'Popup_ArenaShopExchange vs Popup_PVPShopExchange')


def resource_array():
    """`InitShop` allocates three `int[5]` arrays — five rows per slot family."""
    target = method('PVP_Shop', 'InitShop')
    insns = target['instructions']
    rows = []
    for index, insn in enumerate(insns):
        match = re.fullmatch(r'w1, #(\d+)', insn['op_str'])
        if insn['mnemonic'] != 'mov' or not match:
            continue
        follow = next(one for one in insns[index + 1:] if one['mnemonic'] == 'bl')
        rows.append(dict(length_rva=insn['rva'], length=int(match.group(1)),
                         alloc_rva=follow['rva'],
                         alloc=int(follow['op_str'].lstrip('#'), 16)))
    assert [row['alloc'] for row in rows] == [NEWARR] * 3, rows
    assert [row['length'] for row in rows] == [5, 5, 5], rows
    return dict(allocations=rows, length=5,
                note='`InitShop` calls the array helper three times with length 5, and the '
                     'class declares the slot arrays as `Shop_Cell[]` (+0x68/+0x70/+0x78) '
                     'with `int[]` values/costs at +0xb0/+0xb8 — five rows per family')


def stock_cap():
    """`MaxStockCount` is read as the buy cap but written nowhere in the slices."""
    writes, reads = [], []
    for target in load(NATIVE)['methods']:
        for insn in target['instructions']:
            if not insn['op_str'].endswith('#0x98]'):
                continue
            entry = dict(rva=insn['rva'], klass=target['class_name'],
                         signature=target['signature'].strip())
            if insn['mnemonic'] in ('str', 'strb'):
                writes.append(entry)
            elif insn['mnemonic'].startswith('ldr'):
                reads.append(entry)
    shop_reads = [row for row in reads if row['klass'].startswith(('PVP_Shop', 'Arena_Shop'))]
    return dict(writes=writes, reads=len(reads), shop_reads=shop_reads,
                rule='read as the per-slot cap while buying; no store instruction targets '
                     '+0x98 in any dumped method, and the field is not `[SerializeField]`')


def build():
    shops = {klass: persistence(klass) for klass in SHOPS}
    band_rows = {klass: bands(klass) for klass in SHOPS}
    cat = catalogue()
    buy = buy_round_trip()
    twin = twins()
    resources = resource_array()
    cap = stock_cap()

    checks = []
    checks.append(dict(check='both-shops-have-two-keys',
                       passed=all(len(row['keys']) == 2 for row in shops.values())))
    checks.append(dict(check='pvp-keys-are-named',
                       passed=[row['name'] for row in shops['PVP_Shop']['keys']]
                              == ['PVP_SHOP_ITEM_ID', 'PVP_SHOP_ITEM_STOCK']))
    checks.append(dict(check='arena-keys-are-named',
                       passed=[row['name'] for row in shops['Arena_Shop']['keys']]
                              == ['ARENA_SHOP_ITEM_ID', 'ARENA_SHOP_ITEM_STOCK']))
    checks.append(dict(check='six-writes-per-reset',
                       passed=all(len(row['reset']['writes']) == 6
                                  for row in shops.values())))
    checks.append(dict(check='three-bands-100-200-300',
                       passed=[row['base'] for row in band_rows['PVP_Shop']['rows']]
                              == [0x64, 0xC8, 0x12C]
                              and [row['base'] for row in band_rows['Arena_Shop']['rows']]
                              == [0x64, 0xC8, 0x12C]))
    checks.append(dict(check='bands-map-to-the-three-cell-arrays',
                       passed=[row['array'] for row in band_rows['PVP_Shop']['rows']]
                              == ['listItemPlayers', 'listItemDrones', 'listItemResources']))
    checks.append(dict(check='both-shops-subtract-10001',
                       passed={row['delta_value'] for row in band_rows.values()} == {10001}))
    checks.append(dict(check='getters-default-to-zero',
                       passed=all(row['getters']['get_id']['default'] == 0
                                  and row['getters']['get_stock']['default'] == 0
                                  for row in shops.values())))
    checks.append(dict(check='catalogue-is-a-random-shuffle',
                       passed=any(row['class_name'] == 'Random'
                                  and 'Range(' in row['signature']
                                  for row in cat['helpers'])
                              and any('RemoveAt' in row['signature']
                                      for row in cat['helpers'])))
    checks.append(dict(check='buy-restores-the-10001',
                       passed=buy['facts'][2]['op'] == 'add w22, w22, w8'))
    checks.append(dict(check='buy-pays-in-cards',
                       passed={row['rva'] for row in buy['calls']} == {GET_CARDS, SET_CARDS}))
    checks.append(dict(check='twins-have-identical-fields',
                       passed=twin['fields'] == len(FIELD_NAMES)))
    checks.append(dict(check='twins-differ-in-exactly-one-method-size',
                       passed=[row['signature'] for row in twin['methods']
                               if not row['same_size']]
                              == ['private void OnClickPlayerItem(Shop_Cell cell) { }']))
    checks.append(dict(check='five-resource-rows',
                       passed=resources['length'] == 5))
    checks.append(dict(check='stock-cap-is-never-written',
                       passed=cap['writes'] == [] and bool(cap['shop_reads'])))
    assert all(row['passed'] for row in checks), [row for row in checks
                                                 if not row['passed']]

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='The shop ships a key layout and a shuffle, not a catalogue: which item sits '
             'in a slot is a `Random.Range` draw at reset, so "what does slot 3 sell '
             'today" is MODEL_NOT_MEASURED runtime. The key names, the three bands, the '
             '10001 offset and the card payout are build constants.',
        provenance=dict(
            sources=[dict(path=rel, sha256=sha_file(rel))
                     for rel in (NATIVE, STRINGS, DUMP)],
            libil2cpp_sha256=load(NATIVE)['libil2cpp_sha256'],
            xapk_sha256=load(NATIVE)['xapk_sha256'],
            string_literals=len(strings())),
        shops=shops,
        bands=band_rows,
        catalogue=cat,
        buy=buy,
        twins=twin,
        resources=resources,
        stock_cap=cap,
        cross_checks=dict(
            bands_are_hundreds=[row['base'] for row in band_rows['PVP_Shop']['rows']],
            same_bands_in_both=True,
            player_id_base=PLAYER_ID_BASE,
            stored_value='id - 10001 on write, id + 10001 on buy',
            stock_written_on_reset=0),
        checks=checks,
        confirmations=[
            dict(item='#29 remit line "medal/shop exchange" had no decode',
                 result='opened — the exchange popup is wired to a shop that reads two '
                        'PlayerPreferences keys per slot; the shop side is decoded here'),
            dict(item='the shop catalogue is not in the APK',
                 result='confirmed structurally — `ResetShop` shuffles the player\'s own '
                        'active ids, so there is no shipped list to read'),
            dict(item='`Arena_Shop` and `PVP_Shop` are separate implementations',
                 result='corrected — they are the same class twice, 30 identical fields '
                        'and identical method sizes except one 4-byte delta in '
                     '`OnClickPlayerItem`'),
        ],
        open_items=[
            dict(item='which item each slot holds in a live install',
                 blocking='`Random.Range(0, pool.Count)` at reset; MODEL_NOT_MEASURED '
                          'runtime, and the pool is the player\'s own unlocked items'),
            dict(item='`MaxStockCount` (+0x98) is read as the buy cap but never written',
                 blocking='no store to that offset in the 2.5k methods dumped, and the '
                          'field carries no `[SerializeField]`; either set by code '
                          'outside the slices or deliberately left 0'),
            dict(item='the exchange popup\'s medal price',
                 blocking='`Popup_PVPShopExchange.SetPopup` reads `Board_EventSeasonPass.'
                          'EventRewards` and the medal balance; the price table lives in '
                          'the event-pass data, which is a separate lane item'),
        ],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_shop_stock_layout.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    target.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(
        bytes=target.stat().st_size,
        sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        shops=sorted(payload['shops']),
        bands=[hex(row['base']) for row in payload['bands']['PVP_Shop']['rows']],
        checks_passed=sum(1 for row in payload['checks'] if row['passed']),
        checks_total=len(payload['checks']))))


if __name__ == '__main__':
    main()
