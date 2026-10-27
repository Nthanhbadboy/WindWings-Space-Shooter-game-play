#!/usr/bin/env python3
"""From a `Shop_Pack` to the reward row the exchange popup actually shows.

163 left two things open: which `Shop_Pack` fields the click writes (`+0x10`
`+0x2c` `+0x44` `+0x48` `+0x4c`) and what the four `Shop_Pack` +
`Board_EventSeasonPass.EventRewards` pairs per shop (counted by 160) are for. This
tool answers both from the pinned bytes and follows the value one step further:
`Popup_*ShopExchange.SetPopup` → `SetEventRewardTabs`.

The chain, measured:

1. `Shop_Pack` has 28 `int` fields (0x10..0x7C). 129 already pinned the
   index → field order for 27 of them (`GetValueByIndex`), so this report reuses
   that table instead of re-deriving it; `multipleBonus` (0x7C) has no index.
2. Each band writes **one** field on a fresh pack: `PlayerCards` / `DroneCards` =
   `locals.itemId + 1` for the card bands, and `Gcoins` / `Energy` / `DroneExp` =
   `locals.itemValue` for the wallet band.
3. Each pack is wrapped in `EventRewards(pack, number, price, stock)` where
   `number`/`price` come from the shop's economy fields and `stock` is
   `MaxStockCount` (157 pinned 1/50/1/30/10).
4. The resource path builds a **second** pack + `EventRewards` and drops it: the
   allocation result is never copied out of `x0` before `x0` is overwritten, so
   only the wallet pack reaches the popup. Reading the first pair as "resource
   items show drone cards" would be wrong.
5. `SetPopup` names every popup field it touches: `onExit`, `count = 1`,
   `maxStock = rewards.stock - GetStockItem(index)`, `rewards`,
   `textCost = String.Format(fmt, rewards.price * count)`, `textStock` from
   `count`/`maxStock`, slider `maxValue = maxStock - 1`, `step = 1`, `Value = 0`,
   hidden when `maxStock <= 1`.
6. `SetEventRewardTabs` renders **only** `GetListIndexRewards(pack)[0]` — the
   first non-zero slot in 129's order — and uses `value - 1` as the icon index.
   Which of the nine drawn pads a given index lands on needs the 21-byte jump
   table at VA 0x779E50, which is not in the pinned raw set: that stays open.

Everything here is static; anything that needs the game to run is marked
`MODEL_NOT_MEASURED runtime`.
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

import arena_rewards as AR  # noqa: E402
import buy_delegate as BD  # noqa: E402
import dump_rva_index as DX  # noqa: E402

DUMP = DX.DUMP
PREV129 = 'datas/l2_535b0541_pack_index.json.gz'
PREV155 = 'datas/l2_535b0541_medal_flow.json.gz'
PREV157 = 'datas/l2_535b0541_shop_ctor_timer.json.gz'
PREV159 = 'datas/l2_535b0541_exchange_chain.json.gz'
PREV160 = 'datas/l2_535b0541_shop_band_tree.json.gz'
PREV162 = 'datas/l2_535b0541_shop_prefs_keys.json.gz'
PREV163 = 'datas/l2_535b0541_buy_delegate.json.gz'

CLICK = {'Arena_Shop': 22733228, 'PVP_Shop': 19942120}
POPUP = {'Arena_Shop': 'Popup_ArenaShopExchange', 'PVP_Shop': 'Popup_PVPShopExchange'}
PACK_CTOR = 0x1341298      # Shop_Pack..ctor
ER_CTOR = 0x12901b4        # Board_EventSeasonPass.EventRewards..ctor(Shop_Pack,int,int,int)
ALLOC = 0x110d240          # object allocation helper
SET_INFO = 0x1310880       # Box_Rewards.SetInfo(Sprite, Sprite, int, bool, float, string)
ARRAY_NEW = 0x110d09c      # `newarr` helper
INDEX_SLOTS = 27           # 129: GetValueByIndex covers 0..26
ECONOMY = {0x98: 'MaxStockCount', 0x9C: 'ItemPlayerValue', 0xA0: 'ItemPlayerCost',
           0xA4: 'ItemDroneValue', 0xA8: 'ItemDroneCost'}
ECONOMY_DEFAULT = {'MaxStockCount': 10, 'ItemPlayerValue': 1, 'ItemPlayerCost': 50,
                   'ItemDroneValue': 1, 'ItemDroneCost': 30}
SPRITE_FIELDS = {0x20: 'allSpriteRewards', 0x28: 'allRankSprites',
                 0x30: 'listSpriteDrones', 0x38: 'listSpritePlayers',
                 0x40: 'listAvatars', 0x48: 'allDeviceIcons',
                 0x50: 'cardPlayerRandomSprite', 0x58: 'cardDroneRandomSprite',
                 0x60: 'itemRandomSprite'}
MEM = re.compile(r'\[(x\d+)(?:, #(-?0x[0-9a-f]+|-?\d+))?\]!?')


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def dump_lines():
    return gzip.decompress((ROOT / DUMP).read_bytes()).decode('utf-8', 'replace').splitlines()


def class_block(name):
    """Fields and methods of one `dump.cs` class, up to its closing brace."""
    lines = dump_lines()
    head = re.compile(r'^(?:public |private |internal |protected )?(?:static )?(?:sealed )?'
                      r'(?:abstract )?(?:partial )?(?:class|struct) %s(?: |:|$)' % re.escape(name))
    start = next(n for n, line in enumerate(lines) if head.match(line))
    block = []
    for line in lines[start + 1:]:
        if line == '}':
            break
        block.append(line)
    fields, methods, pending = [], [], None
    for line in block:
        field = re.match(r'^\s*(?:\[[^\]]*\]\s*)?(?:public |private |internal |protected )'
                         r'(?:static )?([\w<>\[\].]+) (\w+); // (0x[0-9A-Fa-f]+)', line)
        if field:
            fields.append(dict(type=field.group(1), name=field.group(2),
                               offset=int(field.group(3), 16),
                               static=('static' in line)))
            continue
        rva = re.match(r'^\s*// RVA: (0x[0-9a-fA-F]+)', line)
        if rva:
            pending = int(rva.group(1), 16)
            continue
        signature = re.match(r'^\s*(?:internal|public|private|protected) (.+\{ \})$', line)
        if signature and pending is not None:
            methods.append(dict(rva=pending, signature=signature.group(1)))
            pending = None
    return dict(fields=fields, methods=methods)


@functools.lru_cache(maxsize=None)
def classes():
    return {name: class_block(name) for name in
            ('Shop_Pack', 'Board_EventSeasonPass.EventRewards', 'Shop_Cell', 'Box_Rewards',
             'DataShopPack', 'Arena_Shop', 'PVP_Shop', 'Slider',
             'Arena_Shop.<>c__DisplayClass31_0', 'PVP_Shop.<>c__DisplayClass31_0',
             'Arena_Shop.<>c__DisplayClass31_1', 'PVP_Shop.<>c__DisplayClass31_1',
             'Arena_Shop.<>c__DisplayClass31_3', 'PVP_Shop.<>c__DisplayClass31_3',
             POPUP['Arena_Shop'], POPUP['PVP_Shop'])}


def method_of(klass, fragment):
    hits = [row for row in classes()[klass]['methods'] if fragment in row['signature']]
    assert len(hits) == 1, (klass, fragment, hits)
    return hits[0]


def field_name(klass, offset):
    block = classes().get(klass)
    if block is None:
        return None
    return next((row['name'] for row in block['fields']
                 if row['offset'] == offset and not row['static']), None)


def instrs(klass, rva):
    return BD.method(klass, rva)['instructions']


def text(insn):
    return insn['mnemonic'] + ' ' + insn['op_str']


def const(op_str):
    found = re.search(r'#(0x[0-9a-fA-F]+|\d+)', op_str)
    return int(found.group(1), 0) if found else None


def regs_of(op_str):
    return re.findall(r'\b([wx]\d+)\b', op_str)


def pack_table():
    """The 28 instance fields of `Shop_Pack`, in offset order."""
    order = {row['index']: row for row in load(PREV129)['value_index']['entries']}
    fields = [row for row in classes()['Shop_Pack']['fields'] if not row['static']]
    fields.sort(key=lambda row: row['offset'])
    rows = []
    for row in fields:
        index = next((key for key, entry in order.items()
                      if entry['field'] == row['name']), None)
        rows.append(dict(offset=hex(row['offset']), offset_int=row['offset'],
                         name=row['name'], index=index,
                         indexed=index is not None,
                         nine_table_offset=order[index]['offset'] if index is not None else None))
    return dict(fields=rows, indexed=sum(1 for row in rows if row['indexed']),
                unindexed=[row['name'] for row in rows if not row['indexed']],
                index_order=[order[key]['field'] for key in sorted(order)])


def defines(item, reg):
    """True when `item` writes `reg` (including the two halves of an `ldp`)."""
    mnemonic = item['mnemonic']
    if mnemonic in ('str', 'strb', 'stur', 'stp', 'cmp', 'cmn', 'tst', 'b', 'bl', 'ret',
                    'br', 'cbz', 'cbnz', 'tbz', 'tbnz') or mnemonic.startswith('b.'):
        return False
    if mnemonic == 'ldp':
        return reg in item['op_str'].split(', [')[0].split(', ')
    return item['op_str'].split(', ')[0].strip() == reg


def definition_of(insns, number, reg):
    """Nearest preceding instruction that writes `reg`."""
    return next((item for item in reversed(insns[:number]) if defines(item, reg)), None)


def resolve(insns, index, rva, depth=0):
    """Describe where a value register came from, within the click handler."""
    number = next((n for n, insn in enumerate(insns) if insn['rva'] == rva), None)
    if number is None or depth > 5:
        return dict(kind='unknown')
    insn = insns[number]
    mnemonic, op_str = insn['mnemonic'], insn['op_str']
    if mnemonic in ('ldr', 'ldrsw'):
        mem = MEM.search(op_str)
        base = mem.group(1) if mem else None
        offset = int(mem.group(2), 16) if mem and mem.group(2) else 0
        if base == 'x19':
            name = field_name('Arena_Shop', offset)
            return dict(kind='shop-field', name=name, offset=hex(offset),
                        default=ECONOMY_DEFAULT.get(name), rva=rva, op=text(insn))
        if base == 'x20':
            name = (field_name('Arena_Shop.<>c__DisplayClass31_0', offset)
                    or next((field_name(klass_name, offset)
                             for klass_name in ('Arena_Shop.<>c__DisplayClass31_1',
                                                'PVP_Shop.<>c__DisplayClass31_1')
                             if field_name(klass_name, offset)), None))
            return dict(kind='closure-field', name=name or 'locals@%s' % hex(offset),
                        offset=hex(offset), rva=rva, op=text(insn))
        if base == 'x8' and offset == 0x1C:
            return dict(kind='closure-field', name='itemId', offset=hex(offset),
                        rva=rva, op=text(insn))
        return dict(kind='memory', name=None, offset=hex(offset), rva=rva, op=text(insn))
    if mnemonic == 'ldp':
        mem = MEM.search(op_str)
        base = mem.group(1) if mem else None
        offset = int(mem.group(2), 16) if mem and mem.group(2) else 0
        halves = op_str.split(', [')[0].split(', ')
        written = [part for part in halves if part.startswith(('w', 'x'))]
        return dict(kind='ldp', rva=rva, op=text(insn), base=base,
                    offsets=[hex(offset + 4 * n) for n in range(len(written))],
                    fields=[field_name('Arena_Shop', offset + 4 * n)
                            if base == 'x19' else None for n in range(len(written))])
    if mnemonic == 'mov':
        target, source = [part.strip() for part in op_str.split(', ')]
        if source.startswith('#'):
            return dict(kind='constant', name=None, value=const(source), rva=rva,
                        op=text(insn))
        previous = definition_of(insns, number, source)
        return resolve(insns, index, previous['rva'], depth + 1) \
            if previous is not None else dict(kind='register', name=source, rva=rva,
                                              op=text(insn))
    if mnemonic in ('add', 'sub', 'mul', 'msub', 'madd'):
        parts = [part.strip() for part in op_str.split(', ')]
        operands = []
        for operand in parts[1:]:
            if operand.startswith('#'):
                operands.append(dict(kind='constant', value=const(operand)))
                continue
            previous = definition_of(insns, number, operand)
            operands.append(resolve(insns, index, previous['rva'], depth + 1)
                            if previous is not None else dict(kind='register'))
        return dict(kind=mnemonic, name=None, rva=rva, op=text(insn), operands=operands)
    return dict(kind=mnemonic, name=None, rva=rva, op=text(insn))


def packs(klass):
    """Every `Shop_Pack` a click builds, the field it writes, and its EventRewards."""
    insns = instrs(klass, CLICK[klass])
    index = {insn['rva']: n for n, insn in enumerate(insns)}
    walk = BD.paths(klass)
    reach = {band: BD.reach(insns, index, walk['bands'][band]['entry_rva'])
             for band in BD.BANDS}
    sites = []
    for number, insn in enumerate(insns):
        if insn['mnemonic'] != 'bl' or BD.call_target(insn) != PACK_CTOR:
            continue
        pack_reg = next((insns[n]['op_str'].split(', ')[0] for n in range(max(0, number - 4),
                                                                        number)
                         if insns[n]['mnemonic'] == 'mov'
                         and insns[n]['op_str'].endswith(', x0')), None)
        stores, reward = pack_flow(insns, index, insn['rva'], pack_reg)
        # the value written is the register the store took: describe it
        for store in stores:
            source = store['op'].split(' ', 1)[1].split(',')[0].strip()
            path = path_to(insns, index, index[insn['rva']] + 1, stop_at=store['rva'])
            origin = next((item for item in reversed(path) if defines(item, source)), None)
            store['value'] = resolve(insns, index, origin['rva']) if origin else None
            store['value_register'] = source
        sites.append(dict(pack_ctor=insn['rva'], pack_register=pack_reg,
                          bands=sorted(band for band in reach if insn['rva'] in reach[band]),
                          stores=stores, event_rewards=reward))
    return sites



def pack_flow(insns, index, start, pack_reg):
    """Stores into `pack_reg` and the EventRewards that consumes it.

    Follows the control flow rather than the text order: the wallet pack is built
    early and its `EventRewards` lives in the shared tail, so a textual window would
    attribute the next branch's pack to it.
    """
    stores, reward, seen = [], None, set()
    queue = [(index[start] + 1) if index[start] + 1 < len(insns) else None]
    while queue:
        number = queue.pop(0)
        while number is not None and number < len(insns) and number not in seen:
            seen.add(number)
            item = insns[number]
            mnemonic = item['mnemonic']
            if mnemonic == 'ret':
                break
            target = BD.call_target(item)
            if mnemonic == 'bl' and target == ER_CTOR:
                window = insns[max(0, number - 6):number]
                if any(other['mnemonic'] == 'mov'
                       and other['op_str'].strip() == 'x1, %s' % pack_reg for other in window):
                    reward = reward or item['rva']
            if mnemonic == 'bl' and target == PACK_CTOR:
                break
            if pack_reg and mnemonic == 'str' and (', [%s,' % pack_reg) in item['op_str']:
                offset = int(item['op_str'].split('#')[1].rstrip(']'), 16)
                stores.append(dict(rva=item['rva'], op=text(item), offset=hex(offset),
                                   offset_int=offset, field=field_name('Shop_Pack', offset)))
            if mnemonic == 'b':
                number = index.get(branch_target(item['op_str']))
                continue
            if mnemonic.startswith('b.') or mnemonic in ('cbz', 'cbnz', 'tbz', 'tbnz'):
                target = branch_target(item['op_str'])
                if target in index:
                    queue.append(index[target])
            number += 1
    return stores, reward


def kept(insns, index, alloc_rva, ctor_rva):
    """True when the freshly allocated object is copied out of `x0` before the ctor.

    `EventRewards` is allocated by `0x110d240` and its ctor takes the object in `x0`
    as `this`. A kept object is copied to a callee-saved register first
    (`mov x21, x0`); the resource path's drone-card reward is not, so its pointer is
    gone as soon as `x0` is reused.
    """
    if alloc_rva is None:
        return False
    for insn in insns[index[alloc_rva] + 1:index[ctor_rva]]:
        if insn['mnemonic'] == 'mov' and insn['op_str'].split(', ')[1].strip() == 'x0' \
                and insn['op_str'].split(', ')[0].strip() != 'x0':
            return True
    return False


def rewards(klass, built_packs):
    """Every `EventRewards(pack, number, price, stock)` the click builds."""
    insns = instrs(klass, CLICK[klass])
    index = {insn['rva']: n for n, insn in enumerate(insns)}
    walk = BD.paths(klass)
    reach = {band: BD.reach(insns, index, walk['bands'][band]['entry_rva'])
             for band in BD.BANDS}
    rows = []
    for number, insn in enumerate(insns):
        if insn['mnemonic'] != 'bl' or BD.call_target(insn) != ER_CTOR:
            continue
        window = insns[max(0, number - 16):number]
        args = {}
        for item in window:
            if item['mnemonic'] == 'mov' and re.fullmatch(r'[xw]\d+, [xw]\d+', item['op_str']):
                target, source = [part.strip() for part in item['op_str'].split(', ')]
                args[target] = source
        origin = {}
        for slot, name in (('w2', 'number'), ('w3', 'price'), ('w4', 'stock')):
            source = args.get(slot)
            if source is None:
                origin[name] = dict(kind='missing', name=None)
                continue
            definition = next((item for item in reversed(window)
                               if item['mnemonic'] in ('ldr', 'ldrsw', 'ldp', 'mov')
                               and defines(item, source)
                               and item['rva'] < insn['rva']), None)
            if definition is None:
                origin[name] = dict(kind='register', name=source)
            elif definition['mnemonic'] == 'ldp':
                # `ldp wA, wB, [x19, #off]`: the first half is `off`, the second `off+4`
                offset = int(MEM.search(definition['op_str']).group(2), 16)
                halves = definition['op_str'].split(', [')[0].split(', ')
                bumped = offset + 4 * halves.index(source)
                origin[name] = dict(kind='shop-field',
                                    name=field_name('Arena_Shop', bumped),
                                    offset=hex(bumped),
                                    default=ECONOMY_DEFAULT.get(field_name('Arena_Shop',
                                                                           bumped)),
                                    op=text(definition))
            else:
                origin[name] = resolve(insns, index, definition['rva'])
            if origin[name].get('kind') == 'register':
                # the shared tail reads `number` straight out of the register the
                # branch used to fill the pack slot: same source as that store
                twin = next((row for row in built_packs.get(klass, [])
                             for row in row['stores']
                             if row['value_register'] == source), None)
                if twin is not None:
                    origin[name] = dict(kind='closure-field',
                                        name=(twin['value'] or {}).get('name'),
                                        offset=(twin['value'] or {}).get('offset'),
                                        via=twin['field'], op=twin['op'])
        pack_reg = args.get('x1')
        rows.append(dict(rva=insn['rva'],
                         bands=sorted(band for band in reach if insn['rva'] in reach[band]),
                         pack_register=pack_reg,
                         number=origin['number'], price=origin['price'],
                         stock=origin['stock'],
                         kept=kept(insns, index,
                                   next((item['rva'] for item in reversed(window)
                                         if item['mnemonic'] == 'bl'
                                         and BD.call_target(item) == ALLOC), None),
                                   insn['rva']),
                         alloc_rva=next((item['rva'] for item in reversed(window)
                                         if item['mnemonic'] == 'bl'
                                         and BD.call_target(item) == ALLOC), None)))
    return rows


BRANCH = re.compile(r'#(0x[0-9a-f]+)')


def branch_target(op_str):
    """The `#0x...` a branch jumps to (works for `b`, `b.cond`, `cbz`, `cbnz`)."""
    hits = BRANCH.findall(op_str)
    return int(hits[-1], 16) if hits else None


def mem_offset(mem):
    raw = mem.group(2)
    return int(raw, 0) if raw else 0


def popup(klass):
    """`SetPopup`: every field it stores, the cost text, the slider, the tabs hook."""
    name = POPUP[klass]
    body = method_of(name, 'SetPopup')
    insns = instrs(name, body['rva'])
    calls = [dict(rva=insn['rva'], target=BD.call_target(insn),
                  class_name=BD.name(BD.call_target(insn))['class_name'],
                  method=BD.short(BD.name(BD.call_target(insn))))
             for insn in insns if insn['mnemonic'] == 'bl']
    # `x19` is `this`; the popup uses pre-indexed stores through a copy (`x21`/`x22`)
    alias, writes, reads = {'x0': 0}, [], []
    for insn in insns:
        mnemonic, op = insn['mnemonic'], insn['op_str']
        if mnemonic == 'mov' and re.fullmatch(r'x\d+, x\d+', op):
            target, source = [part.strip() for part in op.split(', ')]
            if source in alias:
                alias[target] = alias[source]
            else:
                alias.pop(target, None)
            continue
        destination = op.split(', ')[0].strip() if ', ' in op else None
        if destination and mnemonic in ('ldr', 'ldur', 'ldrb', 'ldrsw', 'add', 'sub', 'adrp',
                                        'adr', 'mul', 'msub', 'madd', 'scvtf', 'mov', 'fmov'):
            alias.pop(destination, None)
        mem = MEM.search(op)
        if mem is None or mem.group(1) not in alias:
            continue
        offset = alias[mem.group(1)] + mem_offset(mem)
        row = dict(rva=insn['rva'], op=text(insn), offset=hex(offset),
                   field=field_name(name, offset))
        if mnemonic in ('str', 'strb'):
            writes.append(row)
            if op.rstrip().endswith('!'):
                alias[mem.group(1)] = offset
        elif mnemonic in ('ldr', 'ldur', 'ldrb', 'ldrsw'):
            reads.append(row)
    cost = {}
    for number, insn in enumerate(insns):
        if insn['mnemonic'] != 'mul':
            continue
        loads = []
        for operand in [part.strip() for part in insn['op_str'].split(', ')][1:]:
            previous = definition_of(insns, number, operand)
            loads.append(dict(register=operand, op=text(previous) if previous else None))
        after = next((row for row in calls if row['rva'] > insn['rva'] and row['method']), None)
        # the formatted string lands on the `text*` label loaded last before `Format`
        target = next((row for row in reversed(reads)
                       if after and row['rva'] < after['rva']
                       and (row['field'] or '').startswith('text')), None)
        cost = dict(rva=insn['rva'], op=text(insn), operands=loads,
                    formatted_by=after['method'] if after else None,
                    formatted_at=after['rva'] if after else None,
                    written_to=target)
        break
    remaining = {}
    for number, insn in enumerate(insns):
        if insn['mnemonic'] != 'bl' or BD.short(BD.name(BD.call_target(insn))) != 'GetStockItem':
            continue
        sub = insns[number + 1] if number + 1 < len(insns) else None
        if sub is None or sub['mnemonic'] != 'sub':
            continue
        operands = [part.strip() for part in sub['op_str'].split(', ')]
        minuend = definition_of(insns, number + 1, operands[1])
        store = next((row for row in writes
                      if row['rva'] > sub['rva'] and row['offset'] == hex(0x5c)), None)
        remaining = dict(call_rva=insn['rva'], sub_rva=sub['rva'], op=text(sub),
                         minuend=text(minuend) if minuend else None,
                         minuend_register=operands[1],
                         subtrahend=operands[2],
                         stored_as=store['op'] if store else None,
                         stored_offset=store['offset'] if store else None,
                         stored_field=store['field'] if store else None)
        break
    slider = []
    for insn in insns:
        mem = MEM.search(insn['op_str'])
        if insn['mnemonic'] in ('str', 'strb') and mem and mem.group(1) == 'x0':
            offset = mem_offset(mem)
            slider.append(dict(rva=insn['rva'], op=text(insn), offset=hex(offset),
                               field=field_name('Slider', offset)))
    gate = None
    for number, item in enumerate(insns):
        if item['mnemonic'] != 'cmp' or not re.fullmatch(r'w\d+, #1', item['op_str']):
            continue
        source = definition_of(insns, number, item['op_str'].split(', ')[0])
        mem = MEM.search(source['op_str']) if source else None
        if mem and mem_offset(mem) == 0x5c:
            gate = dict(rva=item['rva'], op=text(item), source=text(source),
                        branch=text(insns[number + 1]))
            break
    value_call = next((row for row in calls if row['method'] == 'set_Value'), None)
    return dict(class_name=name, rva=body['rva'], size=BD.method(name, body['rva'])['size'],
                signature=body['signature'], writes=writes, reads=reads, calls=calls,
                cost=cost, remaining=remaining, slider_writes=slider,
                slider_gate=gate, slider_value=value_call,
                tabs_rva=method_of(name, 'SetEventRewardTabs')['rva'],
                tabs_call_rva=next(row['rva'] for row in calls
                                   if row['method'] == 'SetEventRewardTabs'),
                buy_rva=method_of(name, 'OnPressedButtonBuy')['rva'],
                exit_rva=method_of(name, 'OnPressedButtonExit')['rva'],
                change_rva=method_of(name, 'OnChange')['rva'])


def successors(insns, index, number):
    item = insns[number]
    mnemonic = item['mnemonic']
    if mnemonic in ('ret', 'br'):
        return []
    target = branch_target(item['op_str']) if mnemonic in ('b', 'cbz', 'cbnz', 'tbz', 'tbnz') \
        or mnemonic.startswith('b.') else None
    if mnemonic == 'b':
        return [index[target]] if target in index else []
    fallthrough = [number + 1] if number + 1 < len(insns) else []
    if mnemonic.startswith('b.') or mnemonic in ('cbz', 'cbnz', 'tbz', 'tbnz'):
        return fallthrough + ([index[target]] if target in index else [])
    return fallthrough


def path_to(insns, index, start, stop_rva=None, stop_at=None):
    """Shortest path from `start` to the call of `stop_rva` or the `stop_at` rva."""
    queue, seen = [(start,)], {start}
    while queue:
        path = queue.pop(0)
        item = insns[path[-1]]
        if stop_at is not None and item['rva'] == stop_at:
            return [insns[number] for number in path]
        if stop_rva is not None and item['mnemonic'] in ('b', 'bl') \
                and BD.call_target(item) == stop_rva:
            return [insns[number] for number in path]
        for nxt in successors(insns, index, path[-1]):
            if nxt in seen:
                continue
            seen.add(nxt)
            queue.append(path + (nxt,))
    return []


def tabs(klass):
    """`SetEventRewardTabs`: which index is drawn and what each of the nine pads asks for."""
    name = POPUP[klass]
    body = method_of(name, 'SetEventRewardTabs')
    insns = instrs(name, body['rva'])
    index = {insn['rva']: number for number, insn in enumerate(insns)}
    calls = [dict(rva=insn['rva'], target=BD.call_target(insn),
                  **{key: BD.name(BD.call_target(insn))[key]
                     for key in ('class_name', 'signature')})
             for insn in insns if insn['mnemonic'] == 'bl']
    box_stub = next(row['target'] for row in calls
                    if row['signature'] and 'GetBoxSpriteGeneral' in row['signature'])
    picks = {}
    for number, insn in enumerate(insns):
        if insn['mnemonic'] != 'bl':
            continue
        callee = BD.short(BD.name(BD.call_target(insn)))
        after = insns[number + 1:number + 6]
        if callee == 'GetListIndexRewards':
            picks['list_rva'] = insn['rva']
            picks['length_load'] = next((text(item) for item in after
                                         if item['mnemonic'] == 'ldr'), None)
            picks['empty_skip'] = next((text(item) for item in after
                                        if item['mnemonic'] in ('cbz', 'cbnz')), None)
            picks['element'] = next((dict(rva=item['rva'], op=text(item))
                                     for item in insns[number:number + 14]
                                     if item['mnemonic'] == 'ldr'
                                     and item['op_str'].startswith('w20, [x0, #0x20]')),
                                    None)
        if callee == 'GetValueByIndex':
            picks['value_rva'] = insn['rva']
            picks['minus_one'] = next((dict(rva=item['rva'], op=text(item))
                                       for item in insns[number + 1:number + 12]
                                       if item['mnemonic'] == 'sub'), None)
    # `w19` carries `rewards.number` into every pad
    reward_number = next((dict(rva=insn['rva'], op=text(insn),
                               field='Board_EventSeasonPass.EventRewards.number',
                               loaded_from='ldr x8, [x21, #0x60]  ; popup.rewards')
                          for insn in insns
                          if insn['mnemonic'] == 'ldr' and insn['op_str'] == 'w19, [x8, #0x18]'),
                         None)
    pads = []
    for number, insn in enumerate(insns):
        if insn['mnemonic'] != 'bl' or BD.call_target(insn) != box_stub:
            continue
        pad_start = number
        while pad_start and insns[pad_start - 1]['mnemonic'] not in ('b', 'ret', 'br'):
            pad_start -= 1
        path = path_to(insns, index, pad_start, SET_INFO)
        box_arg, box_arg_kind = None, None
        icon, number_source, is_cards, scale_loads = None, None, None, []
        pages = {}
        for position, item in enumerate(path):
            mnemonic, op = item['mnemonic'], item['op_str']
            if mnemonic == 'adrp':
                pages[op.split(', ')[0]] = const(op)
            elif mnemonic == 'bl' and BD.call_target(item) == box_stub:
                box_arg = next((prev['op_str'].split(', ')[1] for prev in reversed(path[:position])
                                if prev['mnemonic'] == 'mov'
                                and prev['op_str'].startswith('w1, ')), None)
                box_arg_kind = 'ladder index' if box_arg == 'w20' else 'constant'
            elif mnemonic == 'ldr' and op.startswith('x2, [x8'):
                offset = mem_offset(MEM.search(op))
                array = next((SPRITE_FIELDS[mem_offset(MEM.search(prev['op_str']))]
                              for prev in reversed(path[:position])
                              if prev['mnemonic'] == 'ldr'
                              and prev['op_str'].startswith('x8, [x8, #0x')
                              and mem_offset(MEM.search(prev['op_str'])) in SPRITE_FIELDS),
                             None)
                stepping = next((prev['op_str'].split(', ')[2].split(',')[0]
                                 for prev in reversed(path[max(0, position - 4):position])
                                 if prev['mnemonic'] == 'add'
                                 and ('lsl #3' in prev['op_str']
                                      or 'sxtw #3' in prev['op_str'])),
                                None)
                if stepping:
                    icon = '%s[%s]' % (array, {'w22': 'value - 1',
                                               'x20': 'ladder index'}.get(stepping, stepping))
                elif array:
                    icon = '%s[%d]' % (array, (offset - 0x20) // 8)
                elif offset in SPRITE_FIELDS:
                    icon = SPRITE_FIELDS[offset]
                else:
                    icon = 'element@%s' % hex(offset)
            elif mnemonic == 'fmov' and op.startswith('s0, #'):
                literal = re.search(r'#([-\d.]+)', op)
                scale_loads.append(dict(rva=item['rva'], op=text(item), kind='immediate',
                                        value=float(literal.group(1)) if literal else None))
            elif mnemonic == 'ldr' and op.startswith('s0, ['):
                mem = MEM.search(op)
                page = pages.get(mem.group(1))
                scale_loads.append(dict(rva=item['rva'], op=text(item), kind='rodata',
                                        value=hex(page + mem_offset(mem)) if page else None))
            elif mnemonic == 'mov' and op.startswith('w3, '):
                number_source = op.split(', ')[1]
            elif mnemonic == 'mov' and op.startswith('w4, '):
                is_cards = op.split(', ')[1]
        scale = scale_loads[-1] if scale_loads else None
        pads.append(dict(call_rva=insn['rva'], pad_rva=insns[pad_start]['rva'],
                         box_arg=box_arg, box_arg_kind=box_arg_kind,
                         box_arg_value=(None if box_arg == 'w20' else const(box_arg or '')),
                         box=('GetBoxSpriteGeneral(%s)' % box_arg) if box_arg else None,
                         icon=icon, number=number_source,
                         is_cards=(None if is_cards is None
                                   else is_cards not in ('wzr', '#0')),
                         scale=scale, scale_loads=scale_loads,
                         overwritten_scale=[row for row in scale_loads[:-1]
                                            if row['kind'] == 'rodata']))
    dispatch = {}
    for number, insn in enumerate(insns):
        if insn['mnemonic'] == 'cmp' and insn['op_str'].startswith('w20, #0x'):
            dispatch['bound'] = dict(rva=insn['rva'], op=text(insn),
                                     limit=const(insn['op_str']))
            dispatch['branch'] = next((dict(rva=item['rva'], op=text(item))
                                       for item in insns[number + 1:number + 3]
                                       if item['mnemonic'].startswith('b.')), None)
        if insn['mnemonic'] == 'adrp' and insn['op_str'] == 'x8, #0x779000':
            dispatch.setdefault('table', {})['page'] = insn['rva']
        if insn['mnemonic'] == 'add' and insn['op_str'].startswith('x8, x8, #0x'):
            dispatch.setdefault('table', {})['offset_rva'] = insn['rva']
            dispatch['table']['offset'] = const(insn['op_str'])
        if insn['mnemonic'] == 'adr' and insn['op_str'].startswith('x9, #0x'):
            dispatch.setdefault('table', {})['base_rva'] = insn['rva']
            dispatch['table']['base'] = const(insn['op_str'])
        if insn['mnemonic'] == 'br':
            dispatch['br'] = dict(rva=insn['rva'], op=text(insn))
    table_va = (0x779000 + dispatch['table']['offset']) if 'table' in dispatch else None
    return dict(class_name=name, rva=body['rva'], size=BD.method(name, body['rva'])['size'],
                signature=body['signature'], picks=picks, reward_number=reward_number,
                dispatch=dispatch,
                table_va=hex(table_va) if table_va else None,
                table_bytes=dispatch.get('bound', {}).get('limit'),
                pads=pads, set_info=BD.name(SET_INFO)['signature'],
                calls=[dict(rva=row['rva'], method=BD.short(row)) for row in calls])


def wallet_guards(klass, pack_rva, reward_rva):
    """The `cmp` instructions that guard the wallet pack's three slot stores."""
    insns = instrs(klass, CLICK[klass])
    inside = [item for item in insns if pack_rva < item['rva'] < reward_rva]
    return [dict(rva=item['rva'], op=text(item))
            for item in inside
            if item['mnemonic'] == 'cmp' and item['op_str'].startswith('w21, #0x')]


def resource_locals(klass):
    """How the resource band fills `itemCost` / `itemValue` before the click."""
    insns = instrs(klass, CLICK[klass])
    index = {insn['rva']: number for number, insn in enumerate(insns)}
    rows = {}
    for number, insn in enumerate(insns):
        if insn['mnemonic'] not in ('str', 'strb'):
            continue
        mem = MEM.search(insn['op_str'])
        if mem is None or mem.group(1) != 'x20' or mem_offset(mem) not in (0x10, 0x14):
            continue
        source = insn['op_str'].split(', ')[0]
        load = definition_of(insns, number, source)
        array = None
        for previous in reversed(insns[max(0, number - 30):number]):
            if previous['mnemonic'] == 'ldr' and previous['op_str'].startswith('x9, [x19, #0x'):
                candidate = mem_offset(MEM.search(previous['op_str']))
                if field_name('Arena_Shop', candidate) in ('ItemResourceCost',
                                                           'ItemResourceValues'):
                    array = field_name('Arena_Shop', candidate)
                    break
        stride = next((text(previous) for previous in reversed(insns[max(0, number - 30):number])
                       if previous['mnemonic'] == 'add' and 'lsl #2' in previous['op_str']), None)
        rows[hex(mem_offset(MEM.search(insn['op_str'])))] = dict(
            store=dict(rva=insn['rva'], op=text(insn)), field_name=field_name(
                '%s.<>c__DisplayClass31_3' % klass,
                mem_offset(MEM.search(insn['op_str']))),
            value_load=text(load) if load else None, array=array, stride=stride,
            index_from=next((dict(op=text(previous),
                                  base=const(previous['op_str']))
                             for previous in reversed(insns[:number])
                             if previous['mnemonic'] == 'sub'
                             and previous['op_str'].startswith('w8, w8, #0x')),
                            None),
            cell_id_load=next((text(previous) for previous in reversed(insns[:number])
                               if previous['mnemonic'] == 'ldr'
                               and previous['op_str'] == 'w8, [x21, #0x18]'), None))
    return rows


def build():
    previous = {key: load(rel) for key, rel in
                (('129', PREV129), ('155', PREV155), ('157', PREV157), ('159', PREV159),
                 ('160', PREV160), ('162', PREV162), ('163', PREV163))}
    table = pack_table()
    shops, checks = {}, []

    def check(label, passed):
        checks.append(dict(check=label, passed=bool(passed)))

    built_packs = {klass: packs(klass) for klass in CLICK}
    for klass in CLICK:
        wrapped = rewards(klass, built_packs)
        shops[klass] = dict(click=CLICK[klass], packs=built_packs[klass],
                            rewards=wrapped, popup=popup(klass), tabs=tabs(klass),
                            locals=resource_locals(klass))
    every = [(klass, row) for klass in shops for row in shops[klass]['packs']]
    single = [(klass, row) for klass, row in every if len(row['stores']) == 1]
    wallet = [(klass, row) for klass, row in every if len(row['stores']) > 1]

    # -- the field table ---------------------------------------------------
    check('shop-pack-has-28-instance-fields', len(table['fields']) == 28)
    check('the-27-indexable-fields-match-129s-table',
          table['indexed'] == INDEX_SLOTS
          and table['index_order'] == [row['name'] for row in table['fields']
                                       if row['indexed']])
    check('multipleBonus-is-the-only-field-without-an-index',
          table['unindexed'] == ['multipleBonus'])
    check('every-index-offset-equals-the-field-offset',
          all(row['nine_table_offset'] == row['offset'] for row in table['fields']
              if row['indexed']))

    # -- packs -------------------------------------------------------------
    check('each-shop-builds-four-shop-packs', all(len(shops[k]['packs']) == 4 for k in shops))
    check('each-shop-wraps-four-event-rewards',
          all(len(shops[k]['rewards']) == 4 for k in shops))
    check('six-of-the-eight-packs-write-exactly-one-field', len(single) == 6)
    check('the-two-remaining-packs-are-the-wallet-packs', len(wallet) == 2
          and all(row['bands'] == ['resource'] for _, row in wallet))
    check('every-written-field-exists-in-the-table',
          all(store['field'] for _, row in every for store in row['stores']))
    check('the-written-fields-are-the-five-163-suspected',
          sorted({store['field'] for _, row in every for store in row['stores']})
          == ['DroneCards', 'DroneExp', 'Energy', 'Gcoins', 'PlayerCards'])
    check('the-player-band-writes-PlayerCards-at-0x4c',
          all([(store['offset'], store['field']) for store in row['stores']]
              == [('0x4c', 'PlayerCards')]
              for k in shops for row in shops[k]['packs'] if row['bands'] == ['player']))
    check('the-drone-band-writes-DroneCards-at-0x48',
          all([(store['offset'], store['field']) for store in row['stores']]
              == [('0x48', 'DroneCards')]
              for k in shops for row in shops[k]['packs'] if row['bands'] == ['drone']))
    check('the-wallet-pack-writes-Gcoins-Energy-DroneExp',
          all([(store['offset'], store['field']) for store in row['stores']]
              == [('0x10', 'Gcoins'), ('0x2c', 'Energy'), ('0x44', 'DroneExp')]
              for _, row in wallet))
    check('the-card-packs-store-itemId-plus-one',
          all('add' in (store['value'] or {}).get('op', '')
              and '+1' not in store['value']['op']
              and store['value']['op'].endswith('#1')
              for _, row in every for store in row['stores']
              if store['field'] in ('PlayerCards', 'DroneCards')))
    check('the-card-packs-raise-the-cell-id-by-one',
          all(store['value']['operands'][0]['kind'] == 'closure-field'
              and store['value']['operands'][0]['name'] == 'itemId'
              for _, row in every for store in row['stores']
              if store['field'] in ('PlayerCards', 'DroneCards')))
    check('the-wallet-slots-copy-the-locals-itemValue',
          all(store['value']['kind'] == 'closure-field'
              and store['value']['name'] == 'itemValue'
              for _, row in wallet for store in row['stores']))
    check('the-wallet-pack-picks-its-slot-with-300-and-301',
          all([item['op'] for item in
               wallet_guards(klass, row['pack_ctor'], row['event_rewards'])]
              == ['cmp w21, #0x12c', 'cmp w21, #0x12d'] for klass, row in wallet))
    check('the-resource-path-builds-two-different-packs',
          all(len([row for row in shops[k]['packs'] if row['bands'] == ['resource']]) == 2
              for k in shops))
    check('the-resource-locals-come-from-the-two-resource-arrays',
          all(shops[k]['locals']['0x10']['array'] == 'ItemResourceCost'
              and shops[k]['locals']['0x14']['array'] == 'ItemResourceValues'
              for k in shops))
    check('the-resource-locals-are-indexed-by-cell-id-minus-300',
          all(shops[k]['locals'][slot]['index_from']['base'] == 300
              and shops[k]['locals'][slot]['cell_id_load'] == 'ldr w8, [x21, #0x18]'
              for k in shops for slot in ('0x10', '0x14')))
    check('the-resource-locals-are-named-itemCost-and-itemValue',
          all(shops[k]['locals'][slot]['field_name'] == name
              for k in shops for slot, name in (('0x10', 'itemCost'), ('0x14', 'itemValue'))))

    # -- event rewards -----------------------------------------------------
    check('every-event-rewards-names-its-pack-register',
          all(row['pack_register'] for k in shops for row in shops[k]['rewards']))
    check('number-comes-from-an-economy-field-or-the-locals',
          all(row['number']['name'] in ('ItemPlayerValue', 'ItemDroneValue', 'itemValue')
              for k in shops for row in shops[k]['rewards']))
    check('price-comes-from-an-economy-field-or-the-locals',
          all(row['price']['name'] in ('ItemPlayerCost', 'ItemDroneCost', 'itemCost')
              for k in shops for row in shops[k]['rewards']))
    check('stock-is-always-MaxStockCount',
          all(row['stock']['name'] == 'MaxStockCount'
              for k in shops for row in shops[k]['rewards']))
    check('the-player-band-wraps-with-ItemPlayerValue-and-ItemPlayerCost',
          all([(row['number']['name'], row['price']['name'])
               for row in shops[k]['rewards'] if row['bands'] == ['player']]
              == [('ItemPlayerValue', 'ItemPlayerCost')] for k in shops))
    check('the-drone-band-wraps-with-ItemDroneValue-and-ItemDroneCost',
          all([(row['number']['name'], row['price']['name'])
               for row in shops[k]['rewards'] if row['bands'] == ['drone']]
              == [('ItemDroneValue', 'ItemDroneCost')] for k in shops))
    check('the-dropped-pack-wraps-with-the-drone-economy-too',
          all((row['number']['name'], row['price']['name']) == ('ItemDroneValue',
                                                                'ItemDroneCost')
              for k in shops for row in shops[k]['rewards']
              if row['bands'] == ['resource'] and not row['kept']))
    check('the-wallet-pack-wraps-with-the-locals-cost-and-value',
          all([(row['number']['name'], row['price']['name'])
               for row in shops[k]['rewards']
               if row['bands'] == ['resource'] and row['kept']]
              == [('itemValue', 'itemCost')] for k in shops))
    check('the-wallet-number-is-read-from-locals-0x14',
          all(row['number']['offset'] == '0x14' and row['price']['offset'] == '0x10'
              for k in shops for row in shops[k]['rewards']
              if row['number']['kind'] == 'closure-field'))
    check('one-event-rewards-per-shop-is-built-and-dropped',
          all(sum(1 for row in shops[k]['rewards'] if not row['kept']) == 1 for k in shops))
    check('the-dropped-one-is-the-resource-paths-drone-card-pack',
          all([(row['bands'], row['kept']) for row in shops[k]['rewards']
               if not row['kept']] == [(['resource'], False)] for k in shops))
    check('exactly-three-event-rewards-per-shop-survive',
          all(sum(1 for row in shops[k]['rewards'] if row['kept']) == 3 for k in shops))
    check('157s-constants-score-every-shop-field',
          all(row['number']['default'] is not None and row['price']['default'] is not None
              for k in shops for row in shops[k]['rewards']
              if row['number']['kind'] == 'shop-field'))
    check('the-embedded-economy-makes-value-times-cost-one-purchase',
          ECONOMY_DEFAULT['ItemPlayerValue'] * ECONOMY_DEFAULT['ItemPlayerCost'] == 50
          and ECONOMY_DEFAULT['ItemDroneValue'] * ECONOMY_DEFAULT['ItemDroneCost'] == 30)

    # -- the popup ---------------------------------------------------------
    arena = shops['Arena_Shop']['popup']
    tab = shops['Arena_Shop']['tabs']
    live = [row['method'] for row in arena['calls'] if row['method']]
    check('setpopup-writes-onExit-count-rewards-and-maxStock',
          [(row['offset'], row['field']) for row in arena['writes']]
          == [('0x50', 'onExit'), ('0x58', 'count'), ('0x60', 'rewards'), ('0x5c', 'maxStock')])
    check('every-store-target-names-a-popup-field',
          all(row['field'] for row in arena['writes']))
    check('the-shown-cost-is-rewards-price-times-count',
          arena['cost']['op'] == 'mul w8, w9, w8'
          and arena['cost']['operands'][0]['op'] == 'ldr w9, [x20, #0x1c]'
          and arena['cost']['operands'][1]['op'] == 'ldur w8, [x21, #-4]')
    check('the-price-load-is-the-rewards-price-at-0x1c',
          field_name('Board_EventSeasonPass.EventRewards', 0x1c) == 'price')
    check('the-second-factor-reloads-count-from-0x58',
          arena['reads'] and any(row['offset'] == '0x58' and row['op'].startswith('ldur')
                                 for row in arena['reads']))
    check('the-cost-is-formatted-by-String.Format',
          arena['cost']['formatted_by'] == 'Format')
    check('the-formatted-cost-lands-on-textCost',
          arena['cost']['written_to']['field'] == 'textCost'
          and arena['cost']['written_to']['offset'] == '0x30')
    check('the-remaining-stock-is-rewards-stock-minus-the-sold-counter',
          arena['remaining']['op'] == 'sub w8, w23, w0'
          and arena['remaining']['minuend'] == 'ldr w23, [x20, #0x20]'
          and 'GetStockItem' in live)
    check('the-remaining-value-is-stored-into-maxStock',
          arena['remaining']['stored_as'] == 'str w8, [x21, #0x5c]!'
          and arena['remaining']['stored_field'] == 'maxStock')
    check('the-stock-label-concats-count-and-maxStock',
          any(row['method'] == 'Concat' for row in arena['calls'])
          and any(row['field'] == 'textStock' for row in arena['reads']))
    check('the-slider-gets-step-and-maxValue',
          [(row['offset'], row['field']) for row in arena['slider_writes']]
          == [('0x64', 'step'), ('0x60', 'maxValue')])
    check('the-slider-step-is-one-point-zero',
          arena['slider_value'] is not None
          and any(text(item).startswith('mov w9, #0x3f800000')
                  for item in instrs(POPUP['Arena_Shop'],
                                     method_of(POPUP['Arena_Shop'], 'SetPopup')['rva'])))
    check('the-slider-max-is-maxStock-minus-one-as-a-float',
          any(text(item) == 'sub w8, w8, #1'
              for item in instrs(POPUP['Arena_Shop'],
                                 method_of(POPUP['Arena_Shop'], 'SetPopup')['rva'])))
    check('the-slider-value-is-reset-to-zero',
          arena['slider_value']['method'] == 'set_Value')
    check('the-slider-is-hidden-when-maxStock-is-not-above-one',
          arena['slider_gate']['op'] == 'cmp w20, #1'
          and arena['slider_gate']['source'] == 'ldr w20, [x19, #0x5c]'
          and arena['slider_gate']['branch'].startswith('b.le'))
    check('the-medal-balance-goes-on-textCoinEvent',
          'get_ArenaMedal' in live
          and any(row['field'] == 'textCoinEvent' for row in arena['reads']))
    check('the-header-is-a-localised-string',
          'GetText' in live and any(row['field'] == 'textHeader' for row in arena['reads']))
    check('the-popup-subscribes-its-own-float-handler',
          'Action<float>..ctor' in live)
    check('setpopup-builds-the-tabs-activates-and-resets-the-slider',
          live.index('SetEventRewardTabs') < live.index('SetActive')
          < live.index('set_Value'))
    check('the-pvp-popup-writes-the-same-four-fields',
          [(row['offset'], row['field']) for row in shops['PVP_Shop']['popup']['writes']]
          == [(row['offset'], row['field']) for row in arena['writes']])
    check('the-pvp-popup-shows-the-pvp-medal',
          'get_PvPMedal' in [row['method'] for row in shops['PVP_Shop']['popup']['calls']])
    check('the-pvp-popup-gates-its-slider-the-same-way',
          shops['PVP_Shop']['popup']['slider_gate']['op'] == 'cmp w21, #1'
          and shops['PVP_Shop']['popup']['slider_gate']['source'] == 'ldr w21, [x19, #0x5c]')

    # -- the tabs ----------------------------------------------------------
    check('only-the-first-reward-index-is-drawn',
          tab['picks']['element']['op'] == 'ldr w20, [x0, #0x20]')
    check('the-index-array-is-length-checked-first',
          tab['picks']['length_load'] == 'ldr w8, [x0, #0x18]'
          and tab['picks']['empty_skip'] == 'cbz x0, #0x15c79d0')
    check('the-icon-index-is-the-value-minus-one',
          tab['picks']['minus_one']['op'] == 'sub w22, w0, #1')
    check('the-dispatch-is-a-jump-table-of-21-entries',
          tab['dispatch']['bound']['op'] == 'cmp w20, #0x15'
          and tab['dispatch']['bound']['limit'] == 21)
    check('the-jump-table-lives-at-va-0x779e50',
          tab['table_va'] == '0x779e50' and tab['table_bytes'] == 21)
    check('the-jump-table-index-is-the-reward-index',
          tab['dispatch']['branch']['op'].startswith('b.hi'))
    check('nine-pads-call-Box_Rewards-SetInfo',
          len(tab['pads']) == 9
          and 'public void SetInfo(Sprite _boxSpr, Sprite _iconSpr, int _number, '
              'bool _isCards = False, float _scaleIcon = 1, string _strBonus)'
              in tab['set_info'])
    check('every-pad-asks-DataShopPack-for-a-box-sprite',
          all(row['box'] and row['box'].startswith('GetBoxSpriteGeneral(')
              for row in tab['pads']))
    check('three-pads-pass-the-ladder-index-to-the-box-sprite',
          [row['box_arg'] for row in tab['pads']].count('w20') == 3)
    check('the-six-constant-box-pads-are-6-14-15-19-20-21',
          sorted(row['box_arg_value'] for row in tab['pads']
                 if row['box_arg_value'] is not None) == [6, 14, 15, 19, 20, 21])
    check('the-icon-sprites-are-the-nine-measured-ones',
          [row['icon'] for row in tab['pads']]
          == ['allSpriteRewards[ladder index]', 'allSpriteRewards[ladder index]',
              'itemRandomSprite', 'allSpriteRewards[6]',
              'listSpriteDrones[value - 1]', 'listSpritePlayers[value - 1]',
              'allSpriteRewards[19]', 'allSpriteRewards[20]', 'allSpriteRewards[21]'])
    check('only-the-two-card-pads-set-isCards',
          [row['is_cards'] for row in tab['pads']]
          == [False, False, False, False, True, True, False, False, False])
    check('every-pad-shows-the-rewards-number',
          tab['reward_number']['field'] == 'Board_EventSeasonPass.EventRewards.number'
          and all(row['number'] == 'w19' for row in tab['pads']))
    check('the-nine-icon-scales-are-measured',
          [str((row['scale'] or {}).get('value')) for row in tab['pads']]
          == ['0x756c14', '1.0', '0x756cac', '0x756f10', '1.0', '1.0', '1.25', '1.5',
              '1.25'])
    check('three-scales-are-rodata-floats',
          [row['scale']['value'] for row in tab['pads']
           if (row['scale'] or {}).get('kind') == 'rodata']
          == [hex(value) for value in (0x756c14, 0x756cac, 0x756f10)])
    check('the-pvp-pads-mirror-the-arena-pads',
          [(row['box_arg'], row['icon'], row['is_cards'], (row['scale'] or {}).get('value'))
           for row in shops['PVP_Shop']['tabs']['pads']]
          == [(row['box_arg'], row['icon'], row['is_cards'], (row['scale'] or {}).get('value'))
              for row in tab['pads']])

    # -- earlier reports still hold ---------------------------------------
    check('129-still-pins-the-same-index-order',
          [row['field'] for row in previous['129']['value_index']['entries']]
          == table['index_order'])
    check('157-still-pins-the-five-economy-constants',
          all(previous['157']['shipped'][name]['value'] == value
              for name, value in ECONOMY_DEFAULT.items()))
    check('160-still-counts-four-packs-and-four-rewards',
          all(len(previous['160']['bands'][k]['packs']) == 4 for k in CLICK))
    check('160s-four-pack-sites-are-the-four-measured-here',
          all(sorted(row['rva'] for row in previous['160']['bands'][k]['packs'])
              == sorted(row['pack_ctor'] for row in shops[k]['packs']) for k in CLICK))
    check('163-still-names-the-delegate-cells',
          all(previous['163']['shops'][k]['bands'][b]['method_cell']
              for k in CLICK for b in BD.BANDS))
    check('163-still-pins-the-three-lambdas-this-report-uses',
          [previous['163']['shops']['Arena_Shop']['bands'][b]['lambda_']['signature']
           for b in ('player', 'drone', 'resource')]
          == ['internal void <OnClickPlayerItem>b__1(int count) { }',
              'internal void <OnClickPlayerItem>b__3(int count) { }',
              'internal void <OnClickPlayerItem>b__5(int count) { }'])
    check('162-still-passes-22-checks',
          len(previous['162']['checks']) == 22
          and all(row['passed'] for row in previous['162']['checks']))
    check('159-still-pins-one-setpopup-per-click',
          all(previous['159']['chains'][k]['caller']['call_rva'] for k in CLICK))
    check('155-still-pins-the-medal-flow', bool(previous['155']))
    failed = [row for row in checks if not row['passed']]
    assert not failed, json.dumps(failed, indent=1)

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Each shop click builds four `Shop_Pack`s and wraps them in '
             '`EventRewards(pack, number, price, stock)`. Three survive and reach '
             '`SetPopup`: the player band writes `+0x4C PlayerCards = itemId + 1` and '
             'wraps it with `(ItemPlayerValue, ItemPlayerCost)`; the drone band writes '
             '`+0x48 DroneCards = itemId + 1` with `(ItemDroneValue, ItemDroneCost)`; and '
             'the resource band writes exactly one of `+0x10 Gcoins`, `+0x2C Energy`, '
             '`+0x44 DroneExp` = `itemValue`, chosen by `cmp w21, #0x12C` / `#0x12D`, and '
             'wraps it with `(itemValue, itemCost)` where those two locals are '
             '`ItemResourceValues[id - 300]` / `ItemResourceCost[id - 300]`. `stock` is '
             'always `MaxStockCount`. The fourth pack — a drone-card pack built earlier '
             'on the resource path — is wrapped too, then dropped: its `EventRewards` '
             'allocation is never copied out of `x0`, so only three rows reach the '
             'popup. `SetPopup` then shows `String.Format(fmt, rewards.price * count)` '
             'on `textCost` with `count = 1`, `maxStock = rewards.stock - '
             'GetStockItem(index)` on `textStock`, sets the slider to `maxValue = '
             'maxStock - 1`, `step = 1`, `Value(0)`, hides it when `maxStock <= 1`, and '
             'draws exactly one reward row — `GetListIndexRewards(pack)[0]` — through a '
             '21-entry jump table at VA 0x779E50 to nine pads, each of which calls '
             '`DataShopPack.GetBoxSpriteGeneral(k)` for the box frame and picks the icon '
             'from `allSpriteRewards` / `listSpriteDrones` / `listSpritePlayers`; the two '
             'card pads also set `_isCards`. Which index lands on which pad still needs '
             'those 21 jump-table bytes, which are not in the pinned raw set.',
        provenance=dict(
            sources=[dict(path=rel, sha256=sha_file(rel))
                     for rel in (DUMP, PREV129, PREV155, PREV157, PREV159, PREV160,
                                 PREV162, PREV163)]
            + [dict(path=str(Path(path).relative_to(ROOT)),
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest())
               for path in sorted(ROOT.glob(BD.RAW_GLOB))],
            string_literals=len(AR.strings())),
        pack_table=table,
        economy=dict(fields=ECONOMY, defaults=ECONOMY_DEFAULT,
                     source='157 shop constructor constants'),
        shops=shops,
        table=[dict(band='player', pack_field='+0x4C PlayerCards = itemId + 1',
                    reward='EventRewards(pack, ItemPlayerValue, ItemPlayerCost, '
                           'MaxStockCount)', kept=True),
               dict(band='drone', pack_field='+0x48 DroneCards = itemId + 1',
                    reward='EventRewards(pack, ItemDroneValue, ItemDroneCost, '
                           'MaxStockCount)', kept=True),
               dict(band='resource (first)', pack_field='+0x48 DroneCards = itemId + 1',
                    reward='EventRewards(pack, ItemDroneValue, ItemDroneCost, '
                           'MaxStockCount)', kept=False),
               dict(band='resource (second)',
                    pack_field='one of +0x10 Gcoins / +0x2C Energy / +0x44 DroneExp = '
                               'itemValue',
                    reward='EventRewards(pack, itemValue, itemCost, MaxStockCount)',
                    kept=True)],
        totals=dict(shops=len(shops), packs=len(every),
                    rewards=sum(len(shops[k]['rewards']) for k in shops),
                    dropped=sum(1 for k in shops for row in shops[k]['rewards']
                                if not row['kept']),
                    pack_fields=len(table['fields']), indexed_fields=table['indexed'],
                    pads=len(tab['pads']), popup_writes=len(arena['writes']),
                    checks_passed=sum(1 for row in checks if row['passed']),
                    checks_total=len(checks)),
        confirmations=[
            dict(item='163: `Shop_Pack +0x48/+0x4C` were unidentified',
                 result='named — 0x48 `DroneCards`, 0x4C `PlayerCards`, plus 0x10 '
                        '`Gcoins`, 0x2C `Energy`, 0x44 `DroneExp`'),
            dict(item='160: four `Shop_Pack` + four `EventRewards` per shop',
                 result='accounted for — player, drone, resource-wallet, and one '
                        'resource-path pack that is built and dropped'),
            dict(item='157: the economy fields are 1 / 50 / 1 / 30 / 10',
                 result='`number` and `price` come from those fields, `stock` is always '
                        '`MaxStockCount`'),
            dict(item='162: the sold counter is a PlayerPref',
                 result='the popup recomputes `rewards.stock - GetStockItem(index)` at '
                        'open time, so the pref is the live source, not a cached field'),
            dict(item='163: the buy deducts `itemCost * count`',
                 result='the card bands charge `(ItemPlayerValue * ItemPlayerCost) * '
                        'count` while the popup prints `ItemPlayerCost * count`; at the '
                        'embedded `ItemPlayerValue = 1` they agree, and a designer-set '
                        'value > 1 would make the popup print 1/value of the deduction. '
                        'The wallet band is consistent at any value because its price '
                        'is already the per-unit `ItemResourceCost[id - 300]`'),
            dict(item='129: the 27-slot index order',
                 result='reused, not re-derived — every pack field written by a click '
                        'has an index, and the drawn row uses index 0'),
        ],
        open_items=[
            dict(item='which pad each reward index lands on',
                 blocking='the 21 dispatch bytes at VA 0x779E50 are not in the pinned '
                          'raw set and the original APK is not in this workspace, so no '
                          'new rodata window can be pinned — the nine pads themselves '
                          'are measured, the index -> pad edges are not'),
            dict(item='the three float literals the pads load from .rodata',
                 blocking='VA 0x756C14 / 0x756CAC / 0x756F10 are read as `ldr s0, '
                          '[xN, #...]`; without the .so the values are unknown, though '
                          'five other pads use `fmov s0, #1.0 / #1.25 / #1.5`'),
            dict(item='whether the dropped resource pack ever matters',
                 blocking='the allocation is provably unused in the click handler, but '
                          'whether some other caller reads it is a runtime question — '
                          'MODEL_NOT_MEASURED runtime'),
            dict(item='a pack with two non-zero slots',
                 blocking='`SetEventRewardTabs` draws only `array[0]`, so a second slot '
                          'would be invisible; every click-built pack sets exactly one '
                          'field, so no shipped path reaches that case — '
                          'MODEL_NOT_MEASURED runtime'),
            dict(item='the exact display class behind the player band locals',
                 blocking='the player path allocates its closure through '
                          '`Object::.ctor` (the empty ctor was inlined) while the drone '
                          'and resource paths call `<>c__DisplayClass31_2` / `_3` '
                          'directly; the layout `itemCost 0x10 / itemValue 0x14 / '
                          'CS$<>8__localsN 0x18` is identical in all three, and 163 '
                          'pinned `_1` for the player lambda'),
        ],
        checks=checks,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_reward_pack.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    target.write_bytes(gzip.compress(
        json.dumps(payload, sort_keys=True, separators=(',', ':')).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size,
                          sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                          checks_passed=payload['totals']['checks_passed'],
                          checks_total=payload['totals']['checks_total'])))


if __name__ == '__main__':
    main()
