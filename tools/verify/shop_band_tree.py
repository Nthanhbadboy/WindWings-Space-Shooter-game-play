#!/usr/bin/env python3
"""Which shop band a clicked cell belongs to, and which `EventRewards` row it builds.

Report 158 read the shop's reward fields and report 159 closed the popup chain, but both
left the selection question open: which `cell.id` reaches which row. `OnClickPlayerItem`
answers it in its first instructions:

    ldr  w1,  [x20, #0x64]     cell.id
    str  w1,  [x21, #0x18]     the display class keeps the id
    bl   Arena_Shop.GetIdItem
    bl   Arena_Shop.GetStockItem
    cmp  w8,  #0xc7            id <= 199 ?
    b.le  player block
    cmp  w8,  #0x12b           id <= 299 ?
    b.le  drone block
    …                          otherwise: resource block, index = id - 300

There are four `EventRewards..ctor` sites per shop, not three. The player block builds one
row from `ItemPlayerValue/ItemPlayerCost`, the drone block one from
`ItemDroneValue/ItemDroneCost`, and the resource block builds two: a first row that reuses
the *drone* fields (`+0xA4/+0xA8`) with a `Shop_Pack` stamped `GetIdItem()+1`, and a second
row whose value/cost come from the per-index `ItemResourceValues/ItemResourceCost` arrays
(`+0xB0/+0xB8`, indexed `id - 300`), with the pack price slot chosen by the index
(300 -> `+0x10`, 301 -> `+0x2C`, anything else -> `+0x44`). The last row built is the one
handed to `SetPopup`.

Every block also re-checks `sold ([cell+0x28]) < MaxStockCount (+0x98)` and the wallet
(`GameDatas.get_ArenaMedal` / `get_PvPMedal`) against the row total before building, so the
click handler gates as well, not only the popup's Buy button.
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

NATIVE = 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
PREV = 'datas/l2_535b0541_exchange_chain.json.gz'
PREV158 = 'datas/l2_535b0541_shop_field_readers.json.gz'

REWARDS_CTOR = 19464628
SETPOPUP = {'Arena_Shop': 22835700, 'PVP_Shop': 19888660}
CLICK = {'Arena_Shop': 22733228, 'PVP_Shop': 19942120}
GETID = 22732732
GETSTOCK = {'Arena_Shop': 22732896, 'PVP_Shop': 19889588}
WALLET_GET = {'Arena_Shop': 20084804, 'PVP_Shop': 20085132}
ID_THRESHOLDS = (0xC7, 0x12B)          # 199, 299
INDEX_BASE = 0x12C                     # 300
CELL_ID_FIELD = 0x64
PACK_CTOR = 20189848
MAXSTOCK_FIELD = 0x98
PLAYER_FIELDS = (0x9C, 0xA0)
DRONE_FIELDS = (0xA4, 0xA8)
RESOURCE_FIELDS = (0xB0, 0xB8)
DISPLAY_FIELDS = (0x14, 0x10)          # value at +0x14, cost at +0x10
PACK_SLOTS = {'player': [0x4C], 'drone': [0x48], 'resource-pre': [0x48],
              'resource-index': [0x10, 0x2C, 0x44]}
REG = re.compile(r'^[wx]\d+$')


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def methods():
    return load(NATIVE)['methods']


def find(class_name, rva):
    return next(row for row in methods()
                if row['class_name'] == class_name and row['rva'] == rva)


def text(insn):
    return insn['mnemonic'] + ' ' + insn['op_str']


def target_of(insn):
    if insn['mnemonic'] not in ('bl', 'b', 'blr') or not insn['op_str'].startswith('#'):
        return None
    return int(insn['op_str'][1:], 16)


def calls(method, fragment_check=None):
    rows = []
    for insn in method['instructions']:
        dst = target_of(insn)
        if dst is None:
            continue
        if fragment_check is None:
            rows.append((insn['rva'], dst))
        else:
            signature = AR.owner(dst)[1] or ''
            if fragment_check in signature:
                rows.append((insn['rva'], dst))
    return rows


IMMEDIATE = re.compile(r'#(0x[0-9a-f]+|\d+)')


def immediate(op):
    """First `#imm` operand, hex or decimal (`add w8, w8, #1` is decimal)."""
    found = IMMEDIATE.search(op)
    if found is None:
        return None
    value = found.group(1)
    return int(value, 16) if value.startswith('0x') else int(value)


def comparisons(method):
    """`cmp wX, #imm` followed by a conditional branch, with the branch target."""
    rows, last = [], None
    for insn in method['instructions']:
        mnemonic = insn['mnemonic']
        if mnemonic == 'cmp':
            last = insn
            continue
        if mnemonic.startswith('b.') or mnemonic in ('cbz', 'cbnz'):
            imm = immediate(last['op_str']) if last is not None else None
            rows.append(dict(compare=text(last) if last is not None else None,
                             compare_rva=last['rva'] if last is not None else None,
                             immediate=imm,
                             branch=text(insn), branch_rva=insn['rva'],
                             target=int(insn['op_str'].split('#')[-1], 16)))
            if mnemonic.startswith('b.'):
                last = None
            continue
        if mnemonic in ('bl', 'b', 'blr', 'ret'):
            last = None
    return rows


MEM = re.compile(r'\[(x\d+)(?:, #(0x[0-9a-f]+))?\]')
REGKEY = re.compile(r'^[wx](\d+)$')
PACK_SLOT_FIELDS = (0x10, 0x2C, 0x44, 0x48, 0x4C)
PACK_FIELDS = {}


def regkey(token):
    found = REGKEY.match(token.strip())
    return int(found.group(1)) if found else None


def dest_regs(insn):
    """Registers written by an instruction, as ints (w8 and x8 are the same slot)."""
    mnemonic = insn['mnemonic']
    parts = [part.strip() for part in insn['op_str'].split(',')]
    if mnemonic in ('str', 'stp', 'cmp', 'bl', 'b', 'blr', 'ret', 'cbz', 'cbnz',
                    'tbz', 'tbnz') or mnemonic.startswith('b.'):
        return []
    key = regkey(parts[0]) if parts else None
    if key is None:
        return []
    regs = [key]
    if mnemonic == 'ldp' and len(parts) > 1 and regkey(parts[1]) is not None:
        regs.append(regkey(parts[1]))
    return regs


def load_origin(insn, key):
    mem = MEM.search(insn['op_str'])
    if mem is None or mem.group(1) not in ('x19', 'x20', 'x21'):
        return None
    field = int(mem.group(2), 16) if mem.group(2) else 0
    parts = [part.strip() for part in insn['op_str'].split(',')]
    if insn['mnemonic'] == 'ldp' and len(parts) > 1 and regkey(parts[1]) == key:
        field += 4
    return dict(kind='shop' if mem.group(1) == 'x19' else 'display', field=field,
                base=mem.group(1), rva=insn['rva'], op=text(insn))


def branch_target(insn):
    mnemonic, op = insn['mnemonic'], insn['op_str']
    if not (mnemonic.startswith('b') or mnemonic in ('cbz', 'cbnz')):
        return None
    if '#0x' not in op:
        return None
    return int(op.split('#')[-1], 16)


def walk_rows(method):
    """Follow every reachable path and resolve each `EventRewards..ctor` argument.

    A plain backwards scan is not enough: the player/drone blocks overwrite the same
    registers as the resource block while sitting at higher addresses, so register
    provenance is only correct along the path that actually reaches the call.
    """
    insns = method['instructions']
    index = {insn['rva']: pos for pos, insn in enumerate(insns)}
    rows, seen, steps = {}, {}, 0
    stack = [(0, {}, {})]
    while stack:
        pos, regs, slots = stack.pop()
        while 0 <= pos < len(insns):
            steps += 1
            assert steps < 200000, 'path explosion'
            signature = (pos,
                         frozenset((key, value['kind'], value['field']) if value
                                   else (key,) for key, value in regs.items()),
                         frozenset((key, tuple(slot['slot'] for slot in value))
                                   for key, value in slots.items() if value))
            if seen.get(signature):
                break
            seen[signature] = True
            insn = insns[pos]
            mnemonic, dst = insn['mnemonic'], branch_target(insn)
            if mnemonic == 'bl' and target_of(insn) == REWARDS_CTOR:
                args = call_args(method, insn['rva'])
                row = dict(call_rva=insn['rva'],
                           args={key: args[key]['op'] for key in sorted(args)},
                           value=regs.get(regkey(args['2']['reg'])),
                           cost=regs.get(regkey(args['3']['reg'])),
                           maxstock=regs.get(regkey(args['4']['reg'])),
                           pack=args['1']['reg'],
                           pack_slots=list(slots.get(regkey(args['1']['reg']), [])))
                previous = rows.get(insn['rva'])
                if previous is None:
                    rows[insn['rva']] = row
                else:
                    for key in ('value', 'cost', 'maxstock', 'pack'):
                        assert previous[key] == row[key], (key, previous[key], row[key])
                    merged = {slot['rva']: slot for slot in previous['pack_slots']}
                    for slot in row['pack_slots']:
                        merged.setdefault(slot['rva'], slot)
                    previous['pack_slots'] = [merged[key] for key in sorted(merged)]
            if mnemonic in ('ldr', 'ldur', 'ldp'):
                for key in dest_regs(insn):
                    regs[key] = load_origin(insn, key)
                    slots[key] = []
            elif mnemonic == 'mov':
                parts = [part.strip() for part in insn['op_str'].split(',')]
                dest = regkey(parts[0])
                source = regkey(parts[1]) if len(parts) > 1 else None
                if dest is not None:
                    regs[dest] = regs.get(source) if source is not None else None
                    slots[dest] = []
            elif mnemonic == 'str':
                mem = MEM.search(insn['op_str'])
                key = regkey(mem.group(1)) if mem and mem.group(1) else None
                slot = int(mem.group(2), 16) if mem and mem.group(2) else None
                if key is not None and slot in PACK_SLOT_FIELDS:
                    slots.setdefault(key, []).append(dict(
                        rva=insn['rva'], slot=slot, op=text(insn),
                        field=PACK_FIELDS.get(slot),
                        stamps_id_plus_one=any(
                            other['mnemonic'] == 'add' and immediate(other['op_str']) == 1
                            for other in insns
                            if insn['rva'] - 0x20 <= other['rva'] < insn['rva'])))
            else:
                for key in dest_regs(insn):
                    regs[key] = None
                    slots[key] = []
            if mnemonic == 'ret':
                break
            if mnemonic == 'b':
                pos = index.get(dst, -1)
                continue
            if mnemonic.startswith('b.') or mnemonic in ('cbz', 'cbnz'):
                if dst in index:
                    stack.append((index[dst], dict(regs),
                                  {key: list(value) for key, value in slots.items()}))
            pos += 1
    return rows, steps


def call_args(method, call_rva):
    """The `mov` arguments feeding a call (`x1`..`x5`), keyed by argument index."""
    window = [insn for insn in method['instructions']
              if call_rva - 0x40 <= insn['rva'] < call_rva]
    args = {}
    for insn in window:
        if insn['mnemonic'] != 'mov':
            continue
        parts = [part.strip() for part in insn['op_str'].split(',')]
        if len(parts) != 2 or regkey(parts[0]) is None:
            continue
        args[parts[0][1:]] = dict(reg=parts[1], rva=insn['rva'], op=text(insn))
    return args


def role_of(row, player_start):
    value, cost = row['value'], row['cost']
    if value is None or cost is None:
        return 'unresolved'
    fields = (value['kind'], value['field'], cost['kind'], cost['field'])
    if fields == ('shop', PLAYER_FIELDS[0], 'shop', PLAYER_FIELDS[1]):
        return 'player'
    if fields == ('shop', DRONE_FIELDS[0], 'shop', DRONE_FIELDS[1]):
        return 'resource-pre' if row['call_rva'] < player_start else 'drone'
    if fields == ('display', DISPLAY_FIELDS[0], 'display', DISPLAY_FIELDS[1]):
        return 'resource-index'
    return 'unexpected'


def pack_layout():
    """Instance field names of `Shop_Pack` (TypeDefIndex 1032), from the pinned dump."""
    text = gzip.decompress((ROOT / DUMP).read_bytes()).decode('utf-8', 'replace')
    found = re.search(r'class Shop_Pack // TypeDefIndex: (\d+)\n\{(.*?)\n\}', text, re.S)
    assert found is not None, 'Shop_Pack missing from dump.cs'
    fields = {}
    for line in found.group(2).splitlines():
        parsed = re.match(r'\s*public (?!static)(\S+) (\w+); // (0x[0-9a-fA-F]+)$', line)
        if parsed is None:
            continue
        fields[int(parsed.group(3), 16)] = dict(name=parsed.group(2),
                                                type=parsed.group(1))
    return dict(class_name='Shop_Pack', typedef_index=int(found.group(1)),
                fields=fields)


def stock_gates(method):
    rows = []
    for insn in method['instructions']:
        if insn['mnemonic'] != 'ldr' or not insn['op_str'].endswith(
                '#%s]' % hex(MAXSTOCK_FIELD)):
            continue
        after = [i for i in method['instructions']
                 if insn['rva'] < i['rva'] <= insn['rva'] + 0x14]
        branch = next((i for i in after if i['mnemonic'] in ('b.ge', 'b.lt', 'b.gt',
                                                             'b.le')), None)
        if branch is None:
            continue
        rows.append(dict(maxstock_load=insn['rva'], op=text(insn),
                         branch_rva=branch['rva'], branch=text(branch),
                         target=int(branch['op_str'].split('#')[-1], 16)))
    return rows


def dispatch(klass, layout):
    PACK_FIELDS.clear()
    PACK_FIELDS.update({offset: row['name'] for offset, row in layout['fields'].items()})
    method = find(klass, CLICK[klass])
    comp = comparisons(method)
    thresholds = [row for row in comp
                  if row['immediate'] in ID_THRESHOLDS
                  and row['branch'].startswith('b.le')]
    assert [row['immediate'] for row in thresholds] == list(ID_THRESHOLDS), thresholds
    player_start, drone_start = thresholds[0]['target'], thresholds[1]['target']
    index = next(insn for insn in method['instructions']
                 if insn['mnemonic'] == 'sub' and immediate(insn['op_str']) == INDEX_BASE)
    equality = [row for row in comp if row['immediate'] in (0x12C, 0x12D)]
    setpopup = [(rva, dst) for rva, dst in calls(method) if dst == SETPOPUP[klass]]
    assert len(setpopup) == 1, setpopup
    id_source = next(insn for insn in method['instructions']
                     if insn['mnemonic'] == 'ldr'
                     and insn['op_str'].endswith('#%s]' % hex(CELL_ID_FIELD)))

    found, steps = walk_rows(method)
    rows = []
    for call_rva in sorted(found):
        row = found[call_rva]
        row['dst'] = REWARDS_CTOR
        row['role'] = role_of(row, player_start)
        rows.append(row)
    assert rows and all(row['role'] != 'unresolved' for row in rows), rows

    def region_of(rva):
        if player_start <= rva < drone_start:
            return 'player'
        if drone_start <= rva < equality[1]['branch_rva']:
            return 'drone'
        return 'resource'

    return dict(class_name=klass, method_rva=method['rva'], size=method['size'],
                signature=method['signature'].strip(), walk_steps=steps,
                thresholds=[dict(compare=row['compare'], compare_rva=row['compare_rva'],
                                 branch=row['branch'], branch_rva=row['branch_rva'],
                                 target=row['target'], limit=row['immediate'])
                            for row in thresholds],
                index=dict(rva=index['rva'], op=text(index), base=INDEX_BASE),
                id_source=dict(rva=id_source['rva'], op=text(id_source)),
                rows=rows,
                roles=[row['role'] for row in rows],
                last_row=rows[-1]['call_rva'],
                setpopup=[dict(rva=rva, region=region_of(rva),
                               after_last_row=rva > rows[-1]['call_rva'])
                          for rva, _ in setpopup],
                equality=[dict(rva=row['branch_rva'], op=row['branch'],
                               compare=row['compare'], target=row['target'],
                               slot={'0x12c': 0x10, '0x12d': 0x2C}.get(
                                   hex(row['immediate']), 0x44))
                          for row in equality],
                packs=[dict(rva=rva, target=dst) for rva, dst in calls(method)
                       if dst == PACK_CTOR],
                getid=calls(method, 'GetIdItem'),
                getstock=calls(method, 'GetStockItem'),
                wallet=[dict(rva=rva, target=dst,
                             op=text(next(i for i in method['instructions']
                                          if i['rva'] == rva)),
                             region=region_of(rva))
                        for rva, dst in calls(method) if dst == WALLET_GET[klass]],
                stock_gates=stock_gates(method))


def build():
    layout = pack_layout()
    bands = {klass: dispatch(klass, layout) for klass in CLICK}
    previous = load(PREV)
    previous158 = load(PREV158)

    def every(fn):
        return all(fn(bands[klass]) for klass in bands)

    checks = []

    def check(name, passed):
        checks.append(dict(check=name, passed=bool(passed)))

    check('two-id-thresholds-per-shop',
          every(lambda b: [row['limit'] for row in b['thresholds']] == list(ID_THRESHOLDS)))
    check('thresholds-are-199-and-299',
          every(lambda b: [row['limit'] for row in b['thresholds']] == [199, 299]))
    check('threshold-branches-are-b.le',
          every(lambda b: all(row['branch'].startswith('b.le')
                              for row in b['thresholds'])))
    check('resource-band-indexes-with-id-minus-300',
          every(lambda b: b['index']['base'] == 300))
    check('four-EventRewards-ctor-sites-per-shop',
          every(lambda b: len(b['rows']) == 4 and all(row['dst'] == REWARDS_CTOR
                                                      for row in b['rows'])))
    check('row-roles-are-resource-pre-player-drone-resource-index',
          every(lambda b: b['roles'] == ['resource-pre', 'player', 'drone',
                                         'resource-index']))
    check('player-row-reads-player-fields-0x9C-0xA0',
          every(lambda b: [(row['value']['kind'], row['value']['field'],
                            row['cost']['field'])
                           for row in b['rows'] if row['role'] == 'player']
                          == [('shop', 0x9C, 0xA0)]))
    check('drone-row-reads-drone-fields-0xA4-0xA8',
          every(lambda b: [(row['value']['kind'], row['value']['field'],
                            row['cost']['field'])
                           for row in b['rows'] if row['role'] == 'drone']
                          == [('shop', 0xA4, 0xA8)]))
    check('resource-pre-row-reuses-drone-fields',
          every(lambda b: [(row['value']['kind'], row['value']['field'],
                            row['cost']['field'])
                           for row in b['rows'] if row['role'] == 'resource-pre']
                          == [('shop', 0xA4, 0xA8)]))
    check('resource-index-row-reads-display-0x14-and-0x10',
          every(lambda b: [(row['value']['kind'], row['value']['field'],
                            row['cost']['field'])
                           for row in b['rows'] if row['role'] == 'resource-index']
                          == [('display', 0x14, 0x10)]))
    check('every-row-caps-at-MaxStockCount-0x98',
          every(lambda b: all(row['maxstock'] and row['maxstock']['field'] == MAXSTOCK_FIELD
                              for row in b['rows'])))
    check('pack-slots-follow-the-band',
          every(lambda b: {row['role']: sorted(slot['slot'] for slot in row['pack_slots'])
                           for row in b['rows']} == PACK_SLOTS))
    check('player-drone-and-pre-stamp-GetIdItem-plus-one',
          every(lambda b: all(slot['stamps_id_plus_one']
                              for row in b['rows'] if row['role'] != 'resource-index'
                              for slot in row['pack_slots'][-1:])))
    check('resource-band-tests-300-and-301',
          every(lambda b: [row['compare'] for row in b['equality']]
                          == ['cmp w21, #0x12c', 'cmp w21, #0x12d']))
    check('resource-index-slots-are-0x10-0x2C-0x44',
          every(lambda b: [row['slot'] for row in b['equality']] == [0x10, 0x2C]
                          and [slot['slot'] for row in b['rows']
                               if row['role'] == 'resource-index'
                               for slot in row['pack_slots']] == [0x10, 0x2C, 0x44]))
    check('pack-slots-name-a-currency-or-card-bucket',
          every(lambda b: all(slot['field'] in ('Gcoins', 'Energy', 'DroneExp',
                                               'DroneCards', 'PlayerCards')
                              for row in b['rows'] for slot in row['pack_slots'])))
    check('four-Shop_Pack-ctor-sites-per-click',
          every(lambda b: len(b['packs']) == 4
                          and all(row['target'] == PACK_CTOR for row in b['packs'])))
    check('each-band-checks-the-stock-cap',
          every(lambda b: len(b['stock_gates']) == 3))
    check('each-band-rechecks-the-wallet',
          every(lambda b: len(b['wallet']) == 3
                          and all(row['target'] == WALLET_GET[b['class_name']]
                                  for row in b['wallet'])))
    check('id-comes-from-cell-plus-0x64',
          every(lambda b: b['id_source']['op'] == 'ldr w1, [x20, #0x64]'))
    check('GetIdItem-and-GetStockItem-run-before-the-dispatch',
          every(lambda b: len(b['getid']) == 1 and len(b['getstock']) == 1
                          and b['getid'][0][0] < b['thresholds'][0]['compare_rva']
                          and b['getstock'][0][0] < b['thresholds'][0]['compare_rva']))
    check('setpopup-runs-once-after-the-last-row',
          every(lambda b: len(b['setpopup']) == 1
                          and b['setpopup'][0]['after_last_row']))
    check('159-still-holds-one-setpopup-call-per-click',
          every(lambda b: previous['chains'][b['class_name']]['caller']['call_rva']
                          == b['setpopup'][0]['rva']))
    check('158-still-reports-four-rows-per-shop',
          all(len(rows) == 4 for rows in previous158['rewards'].values()))
    check('159-still-reports-zero-wallet-writes-in-the-popup',
          previous['totals']['wallet_setter_calls_in_popups'] == 0)
    assert all(row['passed'] for row in checks), [row for row in checks if not row['passed']]

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='A click builds one `Shop_Pack` per band and two on the resource path '
             '(one per `EventRewards` row). The band decides which shop fields feed the row and which '
             '`Shop_Pack` slot carries the price: `PlayerCards +0x4C` for the player '
             'band, `DroneCards +0x48` for the drone band, and in the resource band '
             '`Gcoins +0x10` (id 300), `Energy +0x2C` (id 301) or `DroneExp +0x44` '
             '(any other id). `cell.+0x64` id selects the band inside `OnClickPlayerItem`: `id <= 199` '
             'builds the player row from `ItemPlayerValue/Cost`, `200 <= id <= 299` the '
             'drone row from `ItemDroneValue/Cost`, and `id >= 300` enters the resource '
             'block, which builds two rows — one reusing the drone fields and one indexed '
             '`id - 300` into `ItemResourceValues/Cost` with the pack price slot chosen by '
             'the index (300 -> +0x10, 301 -> +0x2C, other -> +0x44). The last row built '
             'is the one `SetPopup` receives. Each band gates on '
             '`sold [cell+0x28] < MaxStockCount [+0x98]` and on the wallet '
             '(`get_ArenaMedal` 20084804 / `get_PvPMedal` 20085132) before building.',
        provenance=dict(sources=[dict(path=rel, sha256=sha_file(rel))
                                 for rel in (NATIVE, DUMP, PREV, PREV158)],
                        libil2cpp_sha256=load(NATIVE)['libil2cpp_sha256'],
                        xapk_sha256=load(NATIVE)['xapk_sha256'],
                        string_literals=len(AR.strings())),
        bands=bands,
        pack_layout=dict(layout, ctor=PACK_CTOR),
        table=[dict(band='player', id_range='<= 199',
                    rows=['shop ItemPlayerValue+0x9C / ItemPlayerCost+0xA0'],
                    pack_slots=[0x4C]),
               dict(band='drone', id_range='200 .. 299',
                    rows=['shop ItemDroneValue+0xA4 / ItemDroneCost+0xA8'],
                    pack_slots=[0x48]),
               dict(band='resource', id_range='>= 300',
                    rows=['shop ItemDroneValue+0xA4 / ItemDroneCost+0xA8 (pre-row)',
                          'display +0x14 / +0x10 fed by ItemResourceValues+0xB0['
                          'id-300] / ItemResourceCost+0xB8[id-300]'],
                    pack_slots=[0x48, 0x10, 0x2C, 0x44])],
        totals=dict(rows_per_shop={klass: len(bands[klass]['rows']) for klass in bands},
                    rows_total=sum(len(bands[klass]['rows']) for klass in bands),
                    stock_gates={klass: len(bands[klass]['stock_gates']) for klass in bands},
                    wallet_gets={klass: len(bands[klass]['wallet']) for klass in bands},
                    pack_objects={klass: len(bands[klass]['packs']) for klass in bands},
                    checks_passed=sum(1 for row in checks if row['passed']),
                    checks_total=len(checks)),
        confirmations=[
            dict(item='158: three price paths, four rows per shop',
                 result='confirmed — the four rows are the player row, the drone row and '
                        'the resource block\'s two rows, and each reads the fields 158 '
                        'pinned'),
            dict(item='159: one `SetPopup` call per click, last row wins',
                 result='confirmed — a single `SetPopup` site, reached after the last '
                        '`EventRewards..ctor`'),
            dict(item='constructor signature',
                 result='`EventRewards..ctor(Shop_Pack pack, int number, int price, '
                        'int stock)` 19464628 — the three resolved arguments are '
                        '`number`, `price` and `stock` in that order'),
            dict(item='157: popups seed `MaxStockCount=10` and the ctor seeds the arrays',
                 result='not reopened — the click handler only reads `+0x98` as the cap'),
            dict(item='153: `id - 10001` band',
                 result='not on this path — the click handler keys on raw `cell.id` with '
                        '199/299 boundaries and `id - 300` for the resource arrays'),
        ],
        open_items=[
            dict(item='which ids actually exist in each band',
                 blocking='`cell.id` comes from serialized shop data (`cell+0x64`); the '
                          'code proves the boundaries only — MODEL_NOT_MEASURED runtime'),
            dict(item='whether `GetIdItem` (Arena 22732732 / PVP 19941788) is an '
                      'identity map',
                 blocking='the handler stores its result at display `+0x1C`, stamps '
                          '`+1` into the pack (`PlayerCards`/`DroneCards`) and the row '
                          'reads it back; the mapping table itself is data, not code'),
            dict(item='why the resource block builds a drone-shaped row',
                 blocking='the first row uses `ItemDroneValue/Cost` with a pack slot of '
                          '`+0x48`; which of the two rows the list renders is a UI-order '
                          'question outside this path'),
            dict(item='what `DroneExp +0x44` means for the other resource ids',
                 blocking='ids other than 300/301 store their price in the pack slot '
                          '`DroneExp`; whether those ids are drone-experience products '
                          'or simply reuse the slot is serialized data — '
                          'MODEL_NOT_MEASURED runtime'),
            dict(item='`itemResource` array length guard',
                 blocking='`b.hs` bails to 22734604 (out-of-range trap) when '
                          '`id - 300 >= values.Length`; the actual lengths live in the '
                          'serialized shop object — MODEL_NOT_MEASURED runtime'),
        ],
        checks=checks,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_shop_band_tree.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    target.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size,
                          sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                          checks_passed=payload['totals']['checks_passed'],
                          checks_total=payload['totals']['checks_total'],
                          rows={k: v['roles'] for k, v in payload['bands'].items()})))


if __name__ == '__main__':
    main()
