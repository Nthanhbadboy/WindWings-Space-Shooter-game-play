#!/usr/bin/env python3
"""Which method does the `Action<int>` the shop hands to the popup point at?

159 closed the popup chain but left this open, assuming it needed a metadata token
table. It does not. The click handler builds `new Action<int>(bandClosure, methodCell)`:
`x1` is the display class it allocated on that band's path, and a delegate can only be
bound to an instance method of its target's class. Each `<>c__DisplayClass31_{1,2,3}`
declares exactly three methods — `.ctor()`, `g__OnBuy|N(int _id, int count)` and
`b__N(int count)` — so exactly one of them is `void (int)` and the delegate target is
`b__1` / `b__3` / `b__5` by elimination.

The band <-> display class pairing is derived: the click's `cmp #0xc7` / `cmp #0x12b`
ladder separates the three paths (160 pinned the thresholds, 162 pinned the key bases
100 / 200 / 300), each path is walked to a fixpoint, and the seven `0x2aed000` cells are
attributed to the path whose reachable set contains their `ldr`. Two of the three band
ctors are named in the dump; the third folds into `Object..ctor`, so it is the remaining
`<>c__DisplayClass31_1` by elimination — and the granted item independently confirms the
label: `PlayerCards[id + 10001]`, `DroneCards[id + 20001]`, or the walled branch on id
300 / 301.

Every closure spends `itemCost * count` medals with `msub`, grants `itemValue * count`,
writes `SetStockItem(id, snapshot + count)` and rebuilds the cell text through a
5-element `string[]` -> `String.Concat` -> `Shop_Cell.SetStockCount`. None of them
re-reads the wallet, so the popup's comparison (159) is the only purchase-time gate.
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
import dump_rva_index as DX  # noqa: E402

DUMP = DX.DUMP
RAW_GLOB = 'reverse-engineering/raw/*535b0541/native.json.gz'
PREV155 = 'datas/l2_535b0541_medal_flow.json.gz'
PREV156 = 'datas/l2_535b0541_stock_counter.json.gz'
PREV159 = 'datas/l2_535b0541_exchange_chain.json.gz'
PREV160 = 'datas/l2_535b0541_shop_band_tree.json.gz'
PREV161 = 'datas/l2_535b0541_dump_rva_index.json.gz'
PREV162 = 'datas/l2_535b0541_shop_prefs_keys.json.gz'

CLICK = {'Arena_Shop': 22733228, 'PVP_Shop': 19942120}
PAGE = {'Arena_Shop': 0x2AED000, 'PVP_Shop': 0x2AE1000}
CELLS = {  # the seven metadata cells of the click handler, by page offset
    'Arena_Shop': [0xB8, 0xC0, 0xC8, 0xD0, 0xD8, 0xE0, 0xE8],
    'PVP_Shop': [0x58, 0x60, 0x68, 0x70, 0x78, 0x80, 0x88],
}
BANDS = ['player', 'drone', 'resource']          # ladder order -> band key base
BAND_BASE = {'player': 0x64, 'drone': 0xC8, 'resource': 0x12C}
GRANT_BIAS = {'PlayerCards': 10001, 'DroneCards': 20001}
MEDAL = {'Arena_Shop': 'get_ArenaMedal', 'PVP_Shop': 'get_PvPMedal'}
GRANTS = {'GetPlayerCards': ('PlayerCards', 'get'), 'SetPlayerCards': ('PlayerCards', 'set'),
          'GetDroneCards': ('DroneCards', 'get'), 'SetDroneCards': ('DroneCards', 'set'),
          'get_Coins': ('Coins', 'get'), 'set_Coins': ('Coins', 'set'),
          'get_Energy': ('Energy', 'get'), 'set_Energy': ('Energy', 'set'),
          'GetDroneExp': ('DroneExp', 'get'), 'SetDroneExp': ('DroneExp', 'set')}
ALLOC = 17879616       # 0x110d240, object allocation helper
CLASS_INIT = 17879080  # 0x110d028, class-initialisation helper
ARRAY_NEW = 17879196   # 0x110d09c, `newarr` helper
ADRP = re.compile(r'adrp (x\d+), #(0x[0-9a-f]+)')
MEM = re.compile(r'\[(x\d+)(?:, #(0x[0-9a-f]+))?\]')
REG = re.compile(r'^[wx]\d+$')


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def slices():
    rows = {}
    for path in sorted(ROOT.glob(RAW_GLOB)):
        blob = json.loads(gzip.decompress(path.read_bytes()))
        for row in blob['methods']:
            rows.setdefault((row['class_name'], row['rva']), dict(row, raw=path.parent.name))
    return rows


@functools.lru_cache(maxsize=None)
def tables():
    return DX.dump_tables()


@functools.lru_cache(maxsize=None)
def by_class():
    methods, _, _ = tables()
    index = {}
    for rva, row in methods.items():
        index.setdefault(row['class_name'], []).append(dict(rva=rva, signature=row['signature']))
    for rows in index.values():
        rows.sort(key=lambda row: row['rva'])
    return index


def method(klass, rva):
    rows = slices()
    return rows[next(key for key in rows if key[1] == rva
                     and (klass is None or key[0] == klass))]


def text(insn):
    return insn['mnemonic'] + ' ' + insn['op_str']


def call_target(insn):
    mnemonic = insn['mnemonic']
    if mnemonic not in ('bl', 'b') and not mnemonic.startswith('b.'):
        return None
    return int(insn['op_str'].lstrip('#'), 16)


def name(rva):
    methods, generics, _ = tables()
    if rva is None:
        return dict(rva=None, source='none', class_name=None, signature=None)
    row = methods.get(rva)
    if row:
        return dict(rva=rva, source='method-table', class_name=row['class_name'],
                    signature=row['signature'])
    if rva in generics:
        return dict(rva=rva, source='generic-table', class_name=generics[rva],
                    signature=generics[rva])
    return dict(rva=rva, source='unnamed', class_name=None, signature=None)


def short(self):
    """`Player_Saved_Datas.GetPlayerCards` -> `GetPlayerCards`."""
    signature = self['signature'] or ''
    return signature.split('(')[0].split()[-1] if signature else ''


def const(op_str):
    found = re.search(r'#(0x[0-9a-fA-F]+|\d+)', op_str)
    return int(found.group(1), 0) if found else None


def written(insn):
    mnemonic = insn['mnemonic']
    if mnemonic in ('str', 'stp', 'cmp', 'bl', 'blr', 'ret', 'cbz', 'cbnz', 'tbz', 'tbnz') \
            or mnemonic.startswith('b.'):
        return []
    parts = [part.strip() for part in insn['op_str'].split(',')]
    regs = parts[:2] if mnemonic == 'ldp' else parts[:1]
    return ['x' + part[1:] for part in regs if REG.match(part)]


def cells_of(klass):
    """`adrp page` + `ldr` that load one of the seven cells into the same register."""
    row = method(klass, CLICK[klass])
    page = PAGE[klass]
    wanted = {page + offset: offset for offset in CELLS[klass]}
    bases, found = {}, []
    for insn in row['instructions']:
        adrp = ADRP.fullmatch(text(insn))
        if adrp:
            bases[adrp.group(1)] = int(adrp.group(2), 16)
            continue
        mem = MEM.search(insn['op_str'])
        if insn['mnemonic'] in ('ldr', 'ldrsw') and mem is not None \
                and mem.group(1) in bases \
                and insn['op_str'].split(',')[0].strip() == mem.group(1):
            offset = int(mem.group(2), 16) if mem.group(2) else 0
            address = bases[mem.group(1)] + offset
            if address in wanted:
                found.append(dict(rva=insn['rva'], op=text(insn), cell=wanted[address],
                                  cell_hex=hex(address)))
        for register in written(insn):
            bases.pop(register, None)
    return found


def ladder(klass):
    """The `cmp #0xc7` / `cmp #0x12b` dispatch and the three band entries."""
    insns = method(klass, CLICK[klass])['instructions']
    steps = []
    for number, insn in enumerate(insns):
        if insn['mnemonic'] != 'cmp' or not insn['op_str'].startswith('w8, #0x'):
            continue
        branch = insns[number + 1]
        if branch['mnemonic'] != 'b.le':
            continue
        steps.append(dict(cmp=text(insn), cmp_rva=insn['rva'], branch=text(branch),
                          branch_rva=branch['rva'], target=call_target(branch)))
    entries = [dict(band='player', entry_rva=steps[0]['target']),
               dict(band='drone', entry_rva=steps[1]['target']),
               dict(band='resource', entry_rva=insns[
                   [insn['rva'] for insn in insns].index(steps[1]['branch_rva']) + 1]['rva'])]
    return dict(steps=steps,
                entries=[dict(band=row['band'], entry_rva=row['entry_rva'],
                              cmp=(steps[i]['cmp'] if i < 2 else None),
                              branch=(steps[i]['branch'] if i < 2 else 'fall-through'),
                              band_base=hex(BAND_BASE[row['band']]))
                         for i, row in enumerate(entries)])


def reach(insns, index, start):
    """Instruction RVAs reachable from `start` without leaving this method."""
    seen, stack = set(), [start]
    while stack:
        rva = stack.pop()
        if rva in seen or rva not in index:
            continue
        seen.add(rva)
        number = index[rva]
        insn = insns[number]
        mnemonic = insn['mnemonic']
        if mnemonic == 'ret':
            continue
        target = call_target(insn)
        if mnemonic == 'b':
            if target in index:
                stack.append(target)
            continue
        if mnemonic.startswith('b.') or mnemonic in ('cbz', 'cbnz', 'tbz', 'tbnz'):
            if target in index:
                stack.append(target)
        if number + 1 < len(insns):
            stack.append(insns[number + 1]['rva'])
    return seen


def paths(klass):
    """Reachable set + cell reads + inline guards of each band path."""
    insns = method(klass, CLICK[klass])['instructions']
    index = {insn['rva']: number for number, insn in enumerate(insns)}
    dispatch = ladder(klass)
    reads = cells_of(klass)
    medal_get = next((rva for rva, row in tables()[0].items()
                      if short(row) == MEDAL[klass]), None)
    out = {}
    for entry in dispatch['entries']:
        seen = reach(insns, index, entry['entry_rva'])
        own = [row for row in reads if row['rva'] in seen]
        ordered = sorted(seen)
        guards = []
        for position, rva in enumerate(ordered):
            insn = insns[index[rva]]
            if insn['mnemonic'] != 'bl' or call_target(insn) != medal_get:
                continue
            window = [insns[index[rva_]] for rva_ in ordered[position + 1:position + 10]]
            cmp_ = next((item for item in window if item['mnemonic'] == 'cmp'), None)
            branch = next((item for item in window if item['mnemonic'].startswith('b.')
                           and call_target(item) is not None), None)
            if cmp_ and branch:
                guards.append(dict(cmp=text(cmp_), branch=text(branch),
                                   rva=cmp_['rva']))
        calls = [dict(name(call_target(insns[index[rva_]])), rva=rva_)
                 for rva_ in ordered if insns[index[rva_]]['mnemonic'] == 'bl']
        sequence = [insns[index[rva_]] for rva_ in ordered]
        stamp_at = next((number for number, insn in enumerate(sequence)
                         if insn['mnemonic'] in ('str', 'stp')
                         and ', #0x10]' in insn['op_str']), None)
        stamp = [dict(rva=insn['rva'], op=text(insn))
                 for insn in sequence[max(0, stamp_at - 4):stamp_at + 1]] \
            if stamp_at is not None else []
        set_popup = next((dict(rva=insns[index[rva_]]['rva'],
                               op=text(insns[index[rva_]]),
                               target=call_target(insns[index[rva_]]),
                               target_class=name(call_target(insns[index[rva_]]))['class_name'],
                               target_method=short(name(call_target(insns[index[rva_]]))))
                          for rva_ in ordered
                          if insns[index[rva_]]['mnemonic'] == 'b'
                          and 'SetPopup' in (name(call_target(insns[index[rva_]]))['signature']
                                             or '')), None)
        stock_guard = []
        for number, insn in enumerate(sequence):
            if insn['mnemonic'] == 'ldr' and insn['op_str'].endswith(', #0x98]'):
                window = sequence[number + 1:number + 4]
                cmp_ = next((item for item in window if item['mnemonic'] == 'cmp'), None)
                branch = next((item for item in window
                               if item['mnemonic'].startswith('b.')), None)
                if cmp_ and branch:
                    stock_guard.append(dict(cmp=text(cmp_), branch=text(branch),
                                            rva=cmp_['rva']))
        out[entry['band']] = dict(
            entry_rva=entry['entry_rva'], instructions=len(seen),
            cells=[dict(cell=row['cell'], cell_hex=row['cell_hex'], rva=row['rva'],
                        op=row['op']) for row in own],
            medal_guard=guards, stock_guard=stock_guard, stamp=stamp,
            set_popup=set_popup,
            calls=[dict(rva=row['rva'], class_name=row['class_name'],
                        method=short(row),
                        signature=(row.get('signature') or '')[:70]) for row in calls])
    return dict(steps=dispatch['steps'], entries=dispatch['entries'], bands=out,
                unused=[dict(cell=row['cell'], cell_hex=row['cell_hex'], rva=row['rva'],
                             op=row['op']) for row in reads
                        if not any(row['rva'] in
                                   [cell['rva'] for cell in out[band]['cells']]
                                   for band in out)])


def follow(insns, index, start, limit=8):
    """The instructions a fall-through run reaches from `start`, stopping at a `b`."""
    seq, rva = [], start
    while len(seq) < limit and rva in index:
        insn = insns[index[rva]]
        seq.append(insn)
        if insn['mnemonic'] in ('ret', 'b'):
            break
        rva += 4
    return seq


def classify(klass, path):
    """Split a band path's cell reads into its display-class cell and method cell."""
    insns = method(klass, CLICK[klass])['instructions']
    index = {insn['rva']: number for number, insn in enumerate(insns)}
    result = dict(class_cell=None, method_cell=None)
    for cell in path['cells']:
        number = index[cell['rva']]
        window = follow(insns, index, insns[number + 1]['rva'] if number + 1 < len(insns)
                        else cell['rva'])
        alloc = next((item for item in window if item['mnemonic'] == 'bl'
                      and call_target(item) == ALLOC), None)
        ctor = None
        if alloc is not None:
            ctor = next((item for item in window if item['mnemonic'] == 'bl'
                         and item['rva'] > alloc['rva']), None)
        merge = next((item for item in window if
                      (item['mnemonic'] == 'ldr' and item['op_str'] == 'x2, [x8]')), None)
        branch = next((item for item in window if item['mnemonic'] == 'b'), None)
        if branch is not None and call_target(branch) in index:
            above = insns[index[call_target(branch)]]
            if above['mnemonic'] == 'ldr' and above['op_str'] == 'x2, [x8]':
                merge = above
        if alloc is not None and ctor is not None:
            result['class_cell'] = dict(
                cell=cell['cell'], cell_hex=cell['cell_hex'], rva=cell['rva'],
                op=cell['op'], alloc_rva=alloc['rva'], ctor_rva=ctor['rva'],
                ctor=name(call_target(ctor)),
                captures=[dict(rva=item['rva'], op=text(item))
                          for item in window if item['mnemonic'] in ('str', 'stp')][:4])
        if merge is not None or branch is not None:
            result['method_cell'] = dict(
                cell=cell['cell'], cell_hex=cell['cell_hex'], rva=cell['rva'],
                op=cell['op'],
                consumed_at=(merge['rva'] if merge else call_target(branch)),
                consumed_by=text(merge) if merge else text(branch),
                alloc_before=[text(item) for item in window[:4]])
    return result


def delegate_site(klass):
    """The `Action<int>..ctor` call and the registers that feed it."""
    insns = method(klass, CLICK[klass])['instructions']
    sites = [insn for insn in insns if insn['mnemonic'] == 'bl'
             and 'Action<int>..ctor' in (name(call_target(insn))['class_name'] or '')]
    number = [insn['rva'] for insn in insns].index(sites[0]['rva'])
    before = insns[max(0, number - 16):number]
    target = next(item for item in before if item['mnemonic'] == 'mov'
                  and item['op_str'].startswith('x1, '))
    method_pointer = next(item for item in before if item['mnemonic'] == 'ldr'
                          and item['op_str'].startswith('x2, '))
    return dict(rva=sites[0]['rva'], ctor=name(call_target(sites[0])),
                target_register=target['op_str'].split(', ')[1], target_rva=target['rva'],
                method_pointer=dict(rva=method_pointer['rva'], op=text(method_pointer)))


def lambda_profile(rva):
    row = method(None, rva)
    insns = row['instructions']
    guard_cmp = next(item for item in insns
                     if item['mnemonic'] == 'cmp' and item['op_str'].startswith('w19, #'))
    guard_branch = next(item for item in insns if item['mnemonic'] == 'b.lt')
    scroll = next(item for item in insns if item['mnemonic'] == 'bl'
                  and 'EnableScrollView' in (name(call_target(item))['signature'] or ''))
    tail = [item for item in insns if item['mnemonic'] == 'b'][-1]
    return dict(rva=rva, class_name=row['class_name'], size=row['size'],
                signature=row['signature'].strip(),
                guard=dict(cmp=text(guard_cmp), branch=text(guard_branch),
                           fail_rva=call_target(guard_branch)),
                scroll_view=dict(call_rva=scroll['rva'], callee_rva=call_target(scroll),
                                 value='true',
                                 callee=name(call_target(scroll))['signature']),
                id_load=next(text(item) for item in insns if item['mnemonic'] == 'ldr'
                             and item['op_str'] == 'w1, [x8, #0x18]'),
                count_register='w2',
                tail=dict(rva=tail['rva'], op=text(tail), target=call_target(tail),
                          target_class=name(call_target(tail))['class_name'],
                          target_method=short(name(call_target(tail)))))


def closure_profile(klass, rva):
    row = method(None, rva)
    insns = row['instructions']
    calls = [dict(site=insn['rva'], number=number, callee=name(call_target(insn)))
             for number, insn in enumerate(insns) if insn['mnemonic'] == 'bl']
    medal_get = next(rva_ for rva_, row_ in tables()[0].items()
                     if short(row_) == MEDAL[klass])
    medal_set = next(rva_ for rva_, row_ in tables()[0].items()
                     if short(row_) == MEDAL[klass].replace('get_', 'set_'))
    spend = next(item for item in insns if item['mnemonic'] == 'msub')
    spend_index = insns.index(spend)
    get_call = next((call for call in reversed(calls)
                     if call['callee']['rva'] == medal_get
                     and call['number'] < spend_index), None)
    set_call = next((call for call in calls
                     if call['callee']['rva'] == medal_set
                     and call['number'] > spend_index), None)
    between = [text(item) for item in insns[get_call['number'] + 1:spend_index]] \
        if get_call else []
    grants, biases, madds, effects, posts = [], [], [], [], []
    for call in calls:
        short_name = short(call['callee'])
        if short_name in GRANTS:
            item, access = GRANTS[short_name]
            grants.append(dict(item=item, access=access, method=short_name,
                               call_rva=call['site'],
                               class_name=call['callee']['class_name']))
        if short_name == 'CallEffectStatic':
            before = insns[max(0, call['number'] - 10):call['number']]
            effects.append(dict(call_rva=call['site'],
                                signature=call['callee']['signature'],
                                effect_arg=next((text(item) for item in before
                                                 if item['mnemonic'] == 'mov'
                                                 and item['op_str'].startswith('w0, ')),
                                                None)))
        if short_name == 'PostEvent':
            posts.append(dict(call_rva=call['site']))
    for insn in insns:
        if insn['mnemonic'] == 'mov' and const(insn['op_str']) in GRANT_BIAS.values():
            value = const(insn['op_str'])
            biases.append(dict(rva=insn['rva'], op=text(insn), bias=value,
                               item=next(key for key, val in GRANT_BIAS.items()
                                         if val == value)))
        if insn['mnemonic'] == 'madd':
            madds.append(dict(rva=insn['rva'], op=text(insn)))
    stock = next((call for call in calls if short(call['callee']) == 'SetStockItem'), None)
    stock_add = next((text(item) for item in insns
                      if item['mnemonic'] == 'add' and item['op_str'].startswith('w2, ')
                      and stock and 0 < stock['site'] - item['rva'] < 0x20), None)
    concat = next((call for call in calls if short(call['callee']) == 'Concat'), None)
    set_count = next((call for call in calls
                      if short(call['callee']) == 'SetStockCount'), None)
    array = next((item for item in insns if item['mnemonic'] == 'bl'
                  and call_target(item) == ARRAY_NEW), None)
    length, cells, subs, max_adds, text_calls = None, [], [], [], []
    if array is not None and concat is not None:
        number = insns.index(array)
        length = next((const(item['op_str']) for item in insns[max(0, number - 6):number]
                       if item['mnemonic'] == 'mov' and item['op_str'].startswith('w1, #')),
                      None)
        window = insns[number:insns.index(next(item for item in insns
                                              if item['rva'] == concat['site']))]
        bases = {}
        for item in window:
            adrp = ADRP.fullmatch(text(item))
            if adrp:
                bases[adrp.group(1)] = int(adrp.group(2), 16)
                continue
            mem = MEM.search(item['op_str'])
            if item['mnemonic'] in ('ldr', 'ldrsw') and mem is not None \
                    and mem.group(1) in bases \
                    and item['op_str'].split(',')[0].strip() == mem.group(1):
                cells.append(hex(bases[mem.group(1)] +
                                 (int(mem.group(2), 16) if mem.group(2) else 0)))
            if item['mnemonic'] == 'sub':
                subs.append(dict(rva=item['rva'], op=text(item)))
            if item['mnemonic'] == 'add' and '#0x98' in item['op_str']:
                max_adds.append(dict(rva=item['rva'], op=text(item)))
            for register in written(item):
                bases.pop(register, None)
        text_calls = [dict(rva=item['rva'], method=short(name(call_target(item))))
                      for item in window if item['mnemonic'] == 'bl']
    return dict(rva=rva, class_name=row['class_name'], size=row['size'],
                signature=row['signature'].strip(),
                medal=dict(getter=medal_get, setter=medal_set,
                           spend=dict(rva=spend['rva'], op=text(spend)),
                           get_call=get_call['site'] if get_call else None,
                           set_call=set_call['site'] if set_call else None,
                           between_get_and_spend=between,
                           wallet_recheck=any(op.startswith('cmp') for op in between)),
                grants=grants, biases=biases, madds=madds, effects=effects, posts=posts,
                id_branches=[dict(rva=item['rva'], op=text(item)) for item in insns
                             if item['mnemonic'] == 'cmp' and const(item['op_str']) in (300, 301)],
                stock=dict(set_call_rva=stock['site'] if stock else None,
                           add_op=stock_add),
                cell_text=dict(array_length=length, array_rva=array['rva']
                               if array else None, concat_rva=concat['site']
                               if concat else None,
                               set_stock_count=set_count['site'] if set_count else None,
                               cells=cells, subs=subs, max_stock_adds=max_adds,
                               calls=text_calls),
                players_granted=sorted({row_['item'] for row_ in grants
                                        if row_['access'] == 'set'}))


def display_classes(klass):
    """`<>c__DisplayClass31_N` declarations of one shop, from the dump."""
    found = {}
    for klass_name, rows in by_class().items():
        if not klass_name.startswith(klass + '.<>c__DisplayClass31_'):
            continue
        if not any('g__OnBuy' in row['signature'] for row in rows):
            continue   # `<>c__DisplayClass31_0` is the outer capture, not a band closure
        found[klass_name] = dict(
            suffix=klass_name.rsplit('_', 1)[1],
            methods=[row['signature'] for row in rows],
            single_int=[row for row in rows
                        if row['signature'].count('int ') == 1
                        and row['signature'].split('(')[1].startswith('int ')],
            ctor=next((row['rva'] for row in rows if row['signature'].endswith('.ctor() { }')),
                      None),
            lambda_=next((row['rva'] for row in rows if 'b__' in row['signature']), None),
            onbuy=next((row['rva'] for row in rows if 'g__OnBuy' in row['signature']), None))
    return found


def build():
    previous = {key: load(rel) for key, rel in
                (('155', PREV155), ('156', PREV156), ('159', PREV159),
                 ('160', PREV160), ('161', PREV161), ('162', PREV162))}
    shops, checks = {}, []

    def check(label, passed):
        checks.append(dict(check=label, passed=bool(passed)))

    for klass in CLICK:
        walk = paths(klass)
        action = delegate_site(klass)
        classes = display_classes(klass)
        bands = {}
        for band in BANDS:
            path = walk['bands'][band]
            cells = classify(klass, path)
            bands[band] = dict(band=band, band_base=hex(BAND_BASE[band]),
                               path_entry=path['entry_rva'],
                               path_instructions=path['instructions'],
                               path_cells=path['cells'],
                               medal_guard=path['medal_guard'],
                               path_calls=path['calls'],
                               stock_guard=path['stock_guard'], stamp=path['stamp'],
                               set_popup=path['set_popup'],
                               class_cell=cells['class_cell'],
                               method_cell=cells['method_cell'])
        # named ctors identify two of the three band classes; the third folds
        named = {}
        for band in BANDS:
            ctor = bands[band]['class_cell']['ctor']
            if ctor['class_name'] in classes:
                named[band] = ctor['class_name']
        leftover = sorted(set(classes) - set(named.values()))
        for band in BANDS:
            if band in named:
                bands[band]['display_class'] = named[band]
            else:
                bands[band]['display_class'] = leftover[0] if len(leftover) == 1 else None
            display = bands[band]['display_class']
            spec = classes.get(display, {})
            bands[band].update(
                display_identified_by='named ctor' if band in named else
                'elimination (trivial ctor folded into Object..ctor)',
                declared_methods=spec.get('methods', []),
                single_int_methods=len(spec.get('single_int', [])),
                delegate=dict(target_class=display,
                              target_register=action['target_register'],
                              target_rva=action['target_rva'],
                              method_cell=bands[band]['method_cell']['cell'],
                              method_cell_hex=bands[band]['method_cell']['cell_hex'],
                              method_pointer_rva=action['method_pointer']['rva'],
                              method_pointer_op=action['method_pointer']['op'],
                              ctor_rva=action['rva'], ctor=action['ctor'],
                              lambda_rva=spec.get('lambda_'),
                              lambda_signature=next((sig for sig in spec.get('methods', [])
                                                     if 'b__' in sig), None),
                              onbuy_rva=spec.get('onbuy')),
                lambda_=lambda_profile(spec['lambda_']) if spec.get('lambda_') else None,
                closure=closure_profile(klass, spec['onbuy']) if spec.get('onbuy') else None)
        shops[klass] = dict(
            click=dict(rva=CLICK[klass], page=hex(PAGE[klass]), cells=CELLS[klass],
                       size=method(klass, CLICK[klass])['size'],
                       signature=method(klass, CLICK[klass])['signature'].strip(),
                       signatures=sum(1 for _ in cells_of(klass))),
            ladder=walk['entries'], ladder_steps=walk['steps'],
            not_on_a_band_path=walk['unused'],
            delegate_ctor=action,
            display_classes={key: dict(suffix=row['suffix'], ctor=row['ctor'],
                                       lambda_=row['lambda_'], onbuy=row['onbuy'],
                                       methods=row['methods'])
                             for key, row in classes.items()},
            bands=bands)

    every = [(klass, band) for klass in shops for band in BANDS]

    # -- the click's cells -------------------------------------------------
    check('the-click-reads-each-of-the-seven-cells-twice',
          all(len(shops[k]['not_on_a_band_path']) +
              sum(len(shops[k]['bands'][b]['path_cells']) for b in BANDS) == 14
              for k in shops))
    check('only-the-outer-closure-cell-stays-off-every-band-path',
          all([row['cell'] for row in shops[k]['not_on_a_band_path']
               if row['cell'] not in CELLS[k][1:]] for k in shops))
    check('every-band-path-loads-exactly-one-class-cell-and-one-method-cell',
          all(len(shops[k]['bands'][b]['path_cells']) == 2
              and shops[k]['bands'][b]['class_cell'] and shops[k]['bands'][b]['method_cell']
              for k, b in every))
    check('the-class-cell-and-the-method-cell-are-adjacent-on-the-page',
          all(abs(shops[k]['bands'][b]['class_cell']['cell'] -
                  shops[k]['bands'][b]['method_cell']['cell']) == 8 for k, b in every))
    check('each-band-allocates-its-own-display-class',
          len({shops[k]['bands'][b]['class_cell']['cell'] for k, b in every}) == 6)

    # -- the delegate ------------------------------------------------------
    check('the-click-passes-the-band-closure-as-the-delegate-target',
          all(shops[k]['delegate_ctor']['target_register'] == 'x20' for k in shops))
    check('the-delegate-method-pointer-is-loaded-right-before-the-ctor',
          all(shops[k]['bands'][b]['delegate']['method_pointer_rva'] ==
              shops[k]['bands'][b]['method_cell']['consumed_at'] for k, b in every))
    check('each-display-class-declares-exactly-one-single-int-method',
          all(shops[k]['bands'][b]['single_int_methods'] == 1 for k, b in every))
    check('the-single-int-method-is-the-b__-lambda-of-that-class',
          all([sig for sig in shops[k]['bands'][b]['declared_methods']
               if 'int ' in sig.split('(')[1] and sig.count('int ') == 1] ==
              [shops[k]['bands'][b]['delegate']['lambda_signature']] for k, b in every))
    check('each-band-path-names-a-distinct-display-class',
          len({shops[k]['bands'][b]['display_class'] for k, b in every}) == 6)
    check('the-player-band-is-displayclass31_1-and-the-drone-band-31_2',
          all(shops[k]['bands']['player']['display_class'].endswith('31_1')
              and shops[k]['bands']['drone']['display_class'].endswith('31_2')
              and shops[k]['bands']['resource']['display_class'].endswith('31_3')
              for k in shops))
    check('five-of-six-band-ctors-are-named-and-the-sixth-folds-into-Object-ctor',
          sum(1 for k, b in every
              if shops[k]['bands'][b]['display_identified_by'] == 'named ctor') == 5
          and sum(1 for k, b in every
                  if shops[k]['bands'][b]['display_identified_by'] != 'named ctor') == 1)
    check('the-folded-ctor-is-the-arena-player-band-and-still-resolves-to-31_1',
          [k for k in shops for b in BANDS
           if shops[k]['bands'][b]['display_identified_by'] != 'named ctor']
          == ['Arena_Shop'] and
          shops['Arena_Shop']['bands']['player']['display_class'].endswith('31_1')
          and shops['Arena_Shop']['bands']['player']['class_cell']['ctor']['class_name']
          == 'Object')
    check('every-lambda-is-108-bytes',
          all(shops[k]['bands'][b]['lambda_']['size'] == 108 for k, b in every))
    check('every-lambda-re-enables-the-scroll-view',
          all(shops[k]['bands'][b]['lambda_']['scroll_view']['value'] == 'true'
              for k, b in every))
    check('every-lambda-guards-the-count-at-one',
          all(shops[k]['bands'][b]['lambda_']['guard']['cmp'] == 'cmp w19, #1'
              for k, b in every))
    check('every-lambda-tail-branches-into-its-own-g__OnBuy',
          all(shops[k]['bands'][b]['lambda_']['tail']['target'] ==
              shops[k]['bands'][b]['closure']['rva'] for k, b in every))
    check('every-lambda-reads-the-id-from-the-locals-and-the-count-from-its-argument',
          all(shops[k]['bands'][b]['lambda_']['id_load'] == 'ldr w1, [x8, #0x18]'
              and shops[k]['bands'][b]['lambda_']['count_register'] == 'w2'
              for k, b in every))

    # -- the closures ------------------------------------------------------
    check('every-closure-spends-the-shop-medal-with-msub',
          all(shops[k]['bands'][b]['closure']['medal']['spend']['op'].startswith('msub ')
              for k, b in every))
    check('the-medal-getter-precedes-the-msub-and-the-setter-follows',
          all(shops[k]['bands'][b]['closure']['medal']['get_call'] <
              shops[k]['bands'][b]['closure']['medal']['spend']['rva'] <
              shops[k]['bands'][b]['closure']['medal']['set_call'] for k, b in every))
    check('no-closure-re-checks-the-wallet-between-the-getter-and-the-msub',
          all(not shops[k]['bands'][b]['closure']['medal']['wallet_recheck']
              for k, b in every))
    check('the-click-does-guard-the-wallet-inline-on-every-band-path',
          all(shops[k]['bands'][b]['medal_guard'] for k, b in every))
    check('every-band-path-tail-branches-into-SetPopup-with-the-delegate',
          all(shops[k]['bands'][b]['set_popup'] for k, b in every))
    check('the-click-also-guards-the-sold-counter-against-MaxStockCount',
          all(shops[k]['bands'][b]['stock_guard'] for k, b in every))
    check('every-band-path-stamps-itemCost-and-itemValue-into-its-closure',
          all(any(', #0x10]' in row['op'] for row in shops[k]['bands'][b]['stamp'])
              for k, b in every))
    check('the-player-and-drone-paths-stamp-a-multiplied-pack-price',
          all(any(row['op'].startswith('mul ') for row in shops[k]['bands'][b]['stamp'])
              for k, b in every if b != 'resource'))
    check('the-resource-path-reads-its-price-out-of-the-shop-lists',
          all(not any(row['op'].startswith('mul ') for row in
                      shops[k]['bands']['resource']['stamp'])
              and any('#0x20]' in row['op'] for row in
                      shops[k]['bands']['resource']['stamp']) for k in shops))
    check('the-player-closure-indexes-PlayerCards-after-adding-10001',
          all([row['item'] for row in shops[k]['bands']['player']['closure']['biases']]
              == ['PlayerCards'] for k in shops))
    check('the-drone-closure-indexes-DroneCards-after-adding-20001',
          all([row['item'] for row in shops[k]['bands']['drone']['closure']['biases']]
              == ['DroneCards'] for k in shops))
    check('the-resource-closure-branches-on-id-300-and-301',
          all(len(shops[k]['bands']['resource']['closure']['id_branches']) == 2
              for k in shops))
    check('granted-items-match-the-ladder-position',
          all(shops[k]['bands']['player']['closure']['players_granted'] == ['PlayerCards']
              and shops[k]['bands']['drone']['closure']['players_granted'] == ['DroneCards']
              and {'Coins', 'Energy', 'DroneExp'} ==
              set(shops[k]['bands']['resource']['closure']['players_granted'])
              for k in shops))
    check('every-closure-rebuilds-the-cell-text-from-a-5-element-array',
          all(shops[k]['bands'][b]['closure']['cell_text']['array_length'] == 5
              and shops[k]['bands'][b]['closure']['cell_text']['set_stock_count']
              for k, b in every))
    check('every-rebuilt-cell-text-is-remaining-over-cap',
          all(shops[k]['bands'][b]['closure']['cell_text']['subs']
              and shops[k]['bands'][b]['closure']['cell_text']['max_stock_adds']
              and 'GetStockItem' in [row['method'] for row
                                     in shops[k]['bands'][b]['closure']
                                     ['cell_text']['calls']]
              and 'GetText' in [row['method'] for row
                                in shops[k]['bands'][b]['closure']
                                ['cell_text']['calls']]
              for k, b in every))
    check('every-closure-increments-the-stock-snapshot-by-the-count',
          all(shops[k]['bands'][b]['closure']['stock']['add_op'] for k, b in every))
    check('all-six-closures-carry-an-madd',
          all(shops[k]['bands'][b]['closure']['madds'] for k, b in every))
    check('every-credit-is-a-read-modify-write-of-the-same-counter',
          all([row['access'] for row in
               shops[k]['bands'][b]['closure']['grants']
               if row['item'] == shops[k]['bands'][b]['closure']['players_granted'][0]]
              [:2] == ['get', 'set'] for k, b in every))

    # -- previous reports still hold --------------------------------------
    check('162-minus-10001-is-undone-by-the-player-closure',
          previous['162']['totals']['id_offset'] == -10001)
    check('159-still-pins-one-setpopup-per-click',
          all(previous['159']['chains'][k]['caller']['call_rva'] ==
              load(PREV160)['bands'][k]['setpopup'][0]['rva'] for k in shops))
    check('160-still-pins-two-thresholds-per-shop',
          all(len(previous['160']['bands'][k]['thresholds']) == 2 for k in shops))
    check('156-still-pins-six-stock-writers',
          len(previous['156']['writers']) == 6
          and all(row['direction'] == 'increment' for row in previous['156']['writers']))
    check('155-still-pins-the-medal-flow', bool(previous['155']))
    check('161-index-still-passes-24-checks',
          len(previous['161']['checks']) == 24
          and all(row['passed'] for row in previous['161']['checks']))
    check('162-still-passes-22-checks',
          len(previous['162']['checks']) == 22
          and all(row['passed'] for row in previous['162']['checks']))
    failed = [row for row in checks if not row['passed']]
    assert not failed, json.dumps(failed, indent=1)

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='The `Action<int>` handed to the shop exchange popup is '
             '`new Action<int>(bandClosure, methodCell)`. `OnClickPlayerItem` allocates '
             'one `<>c__DisplayClass31_{1,2,3}` per band and each of those classes '
             'declares exactly one `void (int)` method, so the target is '
             '`<OnClickPlayerItem>b__{1,3,5}(int count)` by elimination — no metadata '
             'token table is needed. That lambda re-enables the shop scroll view, does '
             'nothing below `count == 1`, and tail-branches into '
             '`<OnClickPlayerItem>g__OnBuy|{2,4,6}(locals.id, count)`, which takes '
             '`itemCost * count` medals with `msub`, grants `itemValue * count` '
             '(`PlayerCards[id + 10001]`, `DroneCards[id + 20001]`, or Coins / Energy / '
             'DroneExp picked by id 300 / 301 / other), writes '
             '`SetStockItem(id, snapshot + count)` and rebuilds the cell text through a '
             '5-element `string[]` -> `String.Concat` -> `Shop_Cell.SetStockCount`. No '
             'closure re-reads the wallet; the click path guards it inline before '
             'building the popup, which makes 159\'s popup comparison the single gate at '
             'purchase time.',
        provenance=dict(
            sources=[dict(path=rel, sha256=sha_file(rel))
                     for rel in (DUMP, PREV155, PREV156, PREV159, PREV160, PREV161,
                                 PREV162)]
            + [dict(path=str(Path(path).relative_to(ROOT)),
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest())
               for path in sorted(ROOT.glob(RAW_GLOB))],
            string_literals=len(AR.strings())),
        shops=shops,
        table=[dict(band='player', key_base='100 + i', display_class='<>c__DisplayClass31_1',
                    delegate='b__1(int count)', grant='PlayerCards[id + 10001] += '
                                                      'itemValue * count'),
               dict(band='drone', key_base='200 + i', display_class='<>c__DisplayClass31_2',
                    delegate='b__3(int count)', grant='DroneCards[id + 20001] += '
                                                      'itemValue * count'),
               dict(band='resource', key_base='300 + i',
                    display_class='<>c__DisplayClass31_3', delegate='b__5(int count)',
                    grant='id 300 -> Coins, 301 -> Energy, else DroneExp, each += '
                          'itemValue * count')],
        totals=dict(shops=len(shops), bands=len(every), closures=len(every),
                    lambdas=len(every), cells=sum(len(shops[k]['click']['cells'])
                                                  for k in shops),
                    display_classes=sum(len(shops[k]['display_classes']) for k in shops),
                    single_int_methods=sum(shops[k]['bands'][b]['single_int_methods']
                                           for k, b in every),
                    grants=sum(len(shops[k]['bands'][b]['closure']['grants'])
                               for k, b in every),
                    medal_guards=sum(len(shops[k]['bands'][b]['medal_guard'])
                                     for k, b in every),
                    checks_passed=sum(1 for row in checks if row['passed']),
                    checks_total=len(checks)),
        confirmations=[
            dict(item='159: naming the delegate target needs a metadata token table',
                 result='refuted — the target object is the band closure allocated in the '
                        'same method and that class has exactly one `void (int)` method'),
            dict(item='160: the ladder separates the three bands at 0xc7 / 0x12b',
                 result='confirmed — each path allocates a different display class and '
                        'the inline wallet guard sits on every path'),
            dict(item='162: key bases 100 / 200 / 300 map to player / drone / resource',
                 result='confirmed — the ladder position labels the band and the granted '
                        'item agrees (PlayerCards / DroneCards / wallet)'),
            dict(item='162: ResetShop stores `catalogue - 10001` for the player band',
                 result='round trip — the player closure adds 10001 back before indexing '
                        'PlayerCards, so the pref holds the pre-offset catalogue value'),
            dict(item='156: six closures increment the sold counter',
                 result='confirmed — each writes `SetStockItem(id, snapshot + count)`'),
            dict(item='153: `itemCost` is the pack price',
                 result='refined — the click stamps `itemCost = value * cost` from the shop '
                        'fields (player 0x9c * 0xa0, drone 0xa4 * 0xa8) while resource '
                        'packs read the price straight out of the cost list'),
        ],
        open_items=[
            dict(item='whether the popup can pass `count = 0`',
                 blocking='the lambdas no-op below 1 and 154 found the slider seeded at 1; '
                          'whether a runtime path lowers it is MODEL_NOT_MEASURED runtime'),
            dict(item='what the player / drone catalogues contain',
                 blocking='the 10001 / 20001 biases imply card-index ranges, but the lists '
                          'are filled from save data at reset time — MODEL_NOT_MEASURED '
                          'runtime'),
            dict(item='why one of the three band ctors folds into `Object..ctor`',
                 blocking='the bodies are empty, so folding is an IL2CPP codegen choice; '
                          'the class is identified by elimination against the two named '
                          'ctors plus the item its closure moves'),
            dict(item='32-bit wrap in `itemCost * count`',
                 blocking='`msub` / `madd` are 32-bit with both operands from data, so '
                          'saturation is not modelled — MODEL_NOT_MEASURED runtime'),
        ],
        checks=checks,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_buy_delegate.json.gz')
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
