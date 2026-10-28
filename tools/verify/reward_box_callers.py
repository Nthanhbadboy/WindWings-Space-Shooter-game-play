#!/usr/bin/env python3
"""Who draws a reward row: every call site of the seven `Box_Rewards` methods.

166 decoded what the row *draws* (`SetInfo` -> `SetNumber` -> `GetShortNumber`).
It left the other half of the question open: **which screens own a row, and who
turns the grey flag on**. Both are xref questions, and the eight pinned slices
answer them without the `.so`:

1. `SetInfo` has **30** call sites after dedupe (**33** raw, because the slices
   overlap) in **10** caller methods across **6** classes: the two shop-exchange
   popups (tail `b`), `Popup_PVPRewards.SetRewards` (2), `Board_PVP.SetupHunters`,
   `TimeFreeRewardPack` (`SetRewards` + `GetRewards`), `Board_EventSeasonPass`
   (`SetEventRewardTabs` + `SetRewards(int, int)`) and the quest board
   (`Board_QuestRewards.OnPressedButtonOpenNow` + its `<OpenBox>d__43` state
   machine, 13 sites on its own).
2. `SetNumber` has **4**: the two `OnChange` bodies 165 pinned, the tail call
   inside `SetInfo`, and one direct `bl` from `Board_EventSeasonPass`.
   `GetShortNumber` has exactly **1**, the `bl` inside `SetNumber`.
3. `SetBoxSprite`, `SetIconSprite`, `SetGrayScale` and `.ctor` have **zero** call
   sites in the eight pinned slices. That is "not in the pinned slices", not
   "does not exist": the grey flag 165 measured is written inline in the popup
   with `Material.SetFloat`, so the row's own setter is unused at these sites.
4. Every one of the 30 `SetInfo` sites passes **`x5 = xzr`** — the bonus text is
   never filled anywhere in the pinned slices, which is 164/166's "the popup
   passes null" promoted to "every caller passes null".
5. `_isCards` is a literal `wzr` / `#1` at 29 sites and a computed `cset w4, eq`
   at exactly one (`Board_PVP.SetupHunters`). `_scaleIcon` is a literal
   `1.0` / `1.25` / `1.5` or one of two rodata floats (`0x756c14`, `0x756f10`);
   `_number` is a local, a field load, the literal `1`, or — once — the return
   of the preceding call.

Everything here is call-site bookkeeping; the rodata *values* and the field
semantics behind each load stay `MODEL_NOT_MEASURED runtime`.
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

import buy_delegate as BD  # noqa: E402

CLASS = 'Box_Rewards'
TARGETS = [('SetInfo', 19990656), ('SetNumber', 20001584), ('GetShortNumber', 20001844),
           ('SetBoxSprite', 20002124), ('SetIconSprite', 20002152),
           ('SetGrayScale', 20002236), ('.ctor', 20002504)]
TARGET_RVA = dict(TARGETS)
TARGET_OF = {rva: name for name, rva in TARGETS}
SIGNATURES = {
    'SetInfo': 'void SetInfo(Sprite _boxSpr, Sprite _iconSpr, int _number, '
               'bool _isCards = False, float _scaleIcon = 1, string _strBonus) { }',
    'SetNumber': 'void SetNumber(int _number) { }',
    'GetShortNumber': 'string GetShortNumber(int number) { }',
    'SetBoxSprite': 'void SetBoxSprite(Sprite sprite) { }',
    'SetIconSprite': 'void SetIconSprite(Sprite sprite, float scale) { }',
    'SetGrayScale': 'void SetGrayScale(bool gray) { }',
    '.ctor': '.ctor() { }',
}
# AAPCS: `x0` is the receiver, then the arguments in order. `SetInfo` takes
# (Sprite, Sprite, int, bool, float, string) -> x1, x2, w3, w4, s0, x5; `SetNumber`
# and `GetShortNumber` take their single int in w1.
ARGS = {
    'SetInfo': [('this', ('x0',)), ('box', ('x1', 'w1')), ('icon', ('x2', 'w2')),
                ('number', ('w3',)), ('isCards', ('w4',)), ('scale', ('s0',)),
                ('bonus', ('x5', 'w5'))],
    'SetNumber': [('this', ('x0',)), ('number', ('w1',))],
    'GetShortNumber': [('this', ('x0',)), ('number', ('w1',))],
}
ARG_REGS = ARGS['SetInfo']

# Mnemonics that never write their first operand register (`str [x0], w1`,
# `cbz x0, …`, `cmp w3, w9` all mention a register without defining it).
NON_WRITERS = {'str', 'stp', 'stur', 'strb', 'strh', 'cmp', 'cmn', 'tst', 'fcmp', 'fcmpe',
               'cbz', 'cbnz', 'tbz', 'tbnz', 'b', 'bl', 'blr', 'br', 'ret', 'fcsel_never'}
BRANCHES = {'b', 'bl', 'b.eq', 'b.ne', 'b.lt', 'b.le', 'b.gt', 'b.ge', 'b.hi', 'b.hs',
            'b.lo', 'b.ls', 'b.pl', 'b.mi', 'b.vs', 'b.vc', 'cbz', 'cbnz', 'tbz', 'tbnz'}

PREV165 = 'datas/l2_535b0541_qty_widget.json.gz'
PREV166 = 'datas/l2_535b0541_reward_box.json.gz'
ARTIFACT = 'datas/l2_535b0541_reward_box_callers.json.gz'


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def slices():
    """Every slice blob, in name order, with the slice name kept."""
    out = []
    for path in sorted(ROOT.glob(BD.RAW_GLOB)):
        out.append((path.parent.name, json.loads(gzip.decompress(path.read_bytes()))))
    return tuple(out)


@functools.lru_cache(maxsize=None)
def membership():
    """`(class, rva)` -> the slices that contain that method."""
    index = {}
    for name, blob in slices():
        for row in blob['methods']:
            index.setdefault((row['class_name'], row['rva']), set()).add(name)
    return index


@functools.lru_cache(maxsize=None)
def raw_sites():
    """Every `bl`/`b` to one of the seven methods, one entry per slice hit."""
    out = []
    for name, blob in slices():
        for row in blob['methods']:
            for insn in row['instructions']:
                target = BD.call_target(insn)
                if target in TARGET_OF:
                    out.append(dict(slice=name, class_name=row['class_name'],
                                    caller=row['rva'], call=insn['rva'],
                                    target=target, tail=insn['mnemonic'] == 'b'))
    return out


@functools.lru_cache(maxsize=None)
def methods():
    """The deduped method table: `(class, rva)` -> row (first slice wins)."""
    return BD.slices()


def text(insn):
    return insn['mnemonic'] + ' ' + insn['op_str']


def defines(insn, registers):
    """Does this instruction write one of `registers`?"""
    mnemonic = insn['mnemonic']
    if mnemonic in NON_WRITERS or mnemonic.startswith('b.') or mnemonic.startswith('csel'):
        return False
    head = insn['op_str'].split(', ')
    if mnemonic in ('ldp', 'ldnp') and len(head) > 1:
        return head[0] in registers or head[1] in registers
    return head[0] in registers


def last_def(insns, index, registers):
    """Index of the closest preceding instruction that defines one of `registers`."""
    for number in range(index - 1, -1, -1):
        if defines(insns[number], registers):
            return number
    return None


def page_of(insns, index, register):
    """The `adrp` page of `register`, only if its last write *is* that `adrp`.

    Scanning backwards for any `adrp` is wrong: the register is reused all over
    the method, and a stale page would turn a plain field load into a fake
    address (`[x0, #0x18]` would become `0x2adb018`).
    """
    number = last_def(insns, index, {register})
    if number is None:
        return None
    insn = insns[number]
    if insn['mnemonic'] == 'adrp' and insn['op_str'].split(',')[0] == register:
        return BD.const(insn['op_str'])
    return None


def preceding_call(insns, index):
    """The closest `bl` before `index`, resolved to a name."""
    for number in range(index - 1, -1, -1):
        insn = insns[number]
        if insn['mnemonic'] != 'bl':
            continue
        target = BD.call_target(insn)
        try:
            resolved = BD.name(target)
        except Exception:  # noqa: BLE001 - an unnamed target stays unnamed
            resolved = dict(class_name=None, signature=None)
        return dict(rva=target, class_name=resolved['class_name'],
                    signature=resolved['signature'],
                    op=text(insn))
    return None


def classify(insns, index, argument, registers):
    """What the last write to the argument register was."""
    number = last_def(insns, index, set(registers))
    if number is None:
        return None
    insn = insns[number]
    op, mnemonic = insn['op_str'], insn['mnemonic']
    row = dict(rva=insn['rva'], op=text(insn), kind='other', detail=None)
    if mnemonic == 'mov' and re.search(r', (wzr|xzr)$', op):
        row.update(kind='zero', detail=0)
    elif mnemonic == 'mov' and re.match(r'^[wx]\d+, #', op):
        row.update(kind='literal', detail=BD.const(op))
    elif mnemonic == 'mov' and re.match(r'^[wx]\d+, [wx]\d+$', op):
        source = op.split(', ')[1]
        call = preceding_call(insns, number)
        if source in ('w0', 'x0') and call is not None:
            row.update(kind='call-return', detail=call)
        else:
            row.update(kind='local', detail=source)
    elif mnemonic == 'fmov' and re.match(r'^s\d+, #', op):
        row.update(kind='float', detail=op.split('#')[1])
    elif mnemonic == 'cset':
        row.update(kind='flag', detail=op.split(', ')[1])
    elif mnemonic in ('ldr', 'ldrb', 'ldrh') and '[' in op:
        match = re.search(r'\[([wx]\d+)(?:, #(0x[0-9a-f]+|-?\d+))?\]', op)
        base = match.group(1) if match else None
        offset = int(match.group(2), 0) if match and match.group(2) else None
        page = page_of(insns, number, base) if base else None
        if page is not None and offset is not None:
            # a literal in the image, not a field of an object
            row.update(kind='rodata', detail=hex(page + offset))
        elif offset is not None:
            row.update(kind='field', detail=dict(offset=hex(offset), base=base))
        else:
            row.update(kind='load', detail=match.group(0) if match else op)
    return row


def reads_register(insn, register):
    """Does this instruction read `register` (not merely write it)?"""
    if register not in insn['op_str']:
        return False
    parts = insn['op_str'].split(', ')
    if defines(insn, {register}):
        return any(register in part for part in parts[1:])
    return True


def prefix_chain():
    """How `SetNumber` builds the first argument of `String.Concat(string, string)`.

    166 called cell `0x2ade140` "the prefix cell". The load is two dereferences
    deep (`ldr x21, [0x2ade140]` then `ldr x8, [x21]`), so the cell holds a slot
    and the slot holds the string; what the cell *is* stays runtime data.
    """
    insns = methods()[(CLASS, TARGET_RVA['SetNumber'])]['instructions']
    index = {insn['rva']: number for number, insn in enumerate(insns)}
    cell_load = next((insn for insn in insns
                      if insn['mnemonic'] == 'ldr' and insn['op_str'] == 'x21, [x21, #0x140]'),
                     None)
    page = next((insn for insn in insns
                 if insn['mnemonic'] == 'adrp' and insn['op_str'] == 'x21, #0x2ade000'), None)
    second = next((insn for insn in insns
                   if insn['mnemonic'] == 'ldr' and insn['op_str'] == 'x8, [x21]'), None)
    move = next((insn for insn in insns
                 if insn['mnemonic'] == 'mov' and insn['op_str'] == 'x0, x8'), None)
    concat = next((insn for insn in insns if insn['mnemonic'] == 'bl'
                   and BD.call_target(insn) == 33439876), None)
    call = next((insn for insn in insns if insn['mnemonic'] == 'bl'
                 and BD.call_target(insn) == TARGET_RVA['GetShortNumber']), None)
    gate = next((insn for insn in insns
                 if insn['mnemonic'] == 'b.lt'), None)
    stale = [insn for insn in insns if call and gate
             and gate['rva'] < insn['rva'] < call['rva'] and defines(insn, {'x0'})]
    body = methods()[(CLASS, TARGET_RVA['GetShortNumber'])]['instructions']
    # `this` is live only until x0 is first written; after that x0 is scratch.
    first_write = next((number for number, insn in enumerate(body)
                        if defines(insn, {'x0'})), len(body))
    this_reads = [insn for insn in body[:first_write] if reads_register(insn, 'x0')]
    return dict(cell='0x2ade140',
                page=dict(rva=page['rva'], op=text(page)) if page else None,
                first_load=dict(rva=cell_load['rva'], op=text(cell_load)) if cell_load else None,
                second_load=dict(rva=second['rva'], op=text(second)) if second else None,
                move_to_x0=dict(rva=move['rva'], op=text(move)) if move else None,
                concat=dict(rva=concat['rva'], op=text(concat),
                            target=BD.call_target(concat),
                            signature=BD.name(BD.call_target(concat))['signature'])
                if concat else None,
                get_short_call=dict(rva=call['rva'], op=text(call)) if call else None,
                x0_writes_before_the_call=[dict(rva=insn['rva'], op=text(insn))
                                           for insn in stale],
                get_short_reads_this=len(this_reads),
                get_short_first_x0_write=dict(rva=body[first_write]['rva'],
                                              op=text(body[first_write]))
                if first_write < len(body) else None)


def call_sites():
    """The deduped call-site table, in target order."""
    seen = {}
    for raw in raw_sites():
        key = (raw['target'], raw['class_name'], raw['caller'], raw['call'])
        entry = seen.setdefault(key, dict(raw, slices=set()))
        entry['slices'].add(raw['slice'])
    out = []
    for (target, class_name, caller, call), entry in seen.items():
        row = methods()[(class_name, caller)]
        insns = row['instructions']
        position = next(number for number, insn in enumerate(insns) if insn['rva'] == call)
        resolved = BD.name(caller)
        entry = dict(target=target, method=TARGET_OF[target],
                     class_name=class_name, caller=caller,
                     signature=resolved['signature'], call=call,
                     tail=entry['tail'],
                     slices=sorted(entry['slices']),
                     arguments=dict((name, classify(insns, position, name, registers))
                                    for name, registers in ARGS[TARGET_OF[target]]))
        out.append(entry)
    out.sort(key=lambda row: (row['target'], row['caller'], row['call']))
    return out


def by_target(sites, name):
    return [row for row in sites if row['method'] == name]


def rollup(sites):
    """Per-target and per-class counts."""
    targets = {}
    for name, rva in TARGETS:
        rows = by_target(sites, name)
        targets[name] = dict(rva=rva, sites=len(rows),
                             callers=len({row['caller'] for row in rows}),
                             classes=sorted({row['class_name'] for row in rows}),
                             raw_sites=sum(1 for raw in raw_sites() if raw['target'] == rva),
                             tails=sum(1 for row in rows if row['tail']))
    classes = {}
    for row in sites:
        bucket = classes.setdefault(row['class_name'], dict(sites=0, methods=set()))
        bucket['sites'] += 1
        bucket['methods'].add(row['caller'])
    for bucket in classes.values():
        bucket['methods'] = sorted(bucket['methods'])
    return dict(targets=targets, classes=classes,
                sites=len(sites), raw=len(raw_sites()),
                unique_methods=len(methods()), multi_slice=sum(
                    1 for rows in membership().values() if len(rows) > 1))


def argument_table(sites):
    """`argument -> kind -> count`, over the `SetInfo` sites."""
    table = {}
    for name, _ in ARG_REGS:
        bucket = {}
        for row in by_target(sites, 'SetInfo'):
            profile = row['arguments'].get(name) or dict(kind='absent')
            key = profile['kind']
            if name == 'scale' and key == 'float':
                key = 'float %s' % profile['detail']
            if name == 'number' and key == 'literal':
                key = 'literal %d' % profile['detail']
            if name == 'isCards' and key == 'zero':
                key = 'zero (wzr, false)'
            bucket[key] = bucket.get(key, 0) + 1
        table[name] = bucket
    return table


def previous():
    """The pinned conclusions of 165/166 this table has to agree with."""
    qty = load(PREV165)
    box = load(PREV166)
    return dict(
        set_number=box['constants']['set_number'],
        get_short=box['constants']['get_short'],
        set_info=box['constants']['set_info'],
        info_tail=box['set_info']['calls'][-1],
        arena_on_change=qty['shops']['Arena_Shop']['on_change']['set_number'],
        pvp_on_change=qty['shops']['PVP_Shop']['on_change']['set_number'],
        popup_tail=box['popup']['tail_jump'],
        popup_before=box['popup']['before'],
        box_totals=box['totals'], qty_totals=qty['totals'])


def plain(value):
    """JSON-safe copy: sets become sorted lists, tuples become lists."""
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted(plain(item) for item in value)
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    return value


def check(rows, name, passed, detail=None):
    rows.append(dict(name=name, passed=bool(passed), detail=plain(detail)))


def run_checks(sites, stats):
    checks = []
    previous_ = previous()

    # -- the seven methods -------------------------------------------------
    named = {BD.name(rva)['class_name'] for _, rva in TARGETS}
    check(checks, 'all-seven-targets-are-box_rewards', named == {CLASS}, sorted(named))
    heads = {name: (BD.name(rva)['signature'] or '').split('(')[0].split()[-1]
             for name, rva in TARGETS}
    check(checks, 'signatures-match-the-dump',
          heads == {name: SIGNATURES[name].split('(')[0].split()[-1] for name, _ in TARGETS},
          heads)
    sizes = {name: BD.method(CLASS, rva)['size'] for name, rva in TARGETS}
    check(checks, 'method-sizes-match-166', sizes['SetInfo'] == 420 and sizes['SetNumber'] == 260
          and sizes['GetShortNumber'] == 280 and sizes['SetGrayScale'] == 268,
          {name: size for name, size in sizes.items()})

    # -- dedupe ------------------------------------------------------------
    check(checks, 'slices-overlap-so-sites-need-dedupe',
          stats['multi_slice'] > 0 and stats['raw'] > stats['sites'],
          dict(unique_methods=stats['unique_methods'], multi_slice=stats['multi_slice'],
               raw=stats['raw'], sites=stats['sites']))
    check(checks, 'every-raw-hit-maps-to-a-deduped-site',
          len({(raw['target'], raw['class_name'], raw['caller'], raw['call']) for raw in raw_sites()})
          == stats['sites'], stats['sites'])
    check(checks, 'no-duplicate-call-rows',
          len({(row['target'], row['caller'], row['call']) for row in sites}) == len(sites),
          len(sites))

    # -- SetInfo -----------------------------------------------------------
    info = by_target(sites, 'SetInfo')
    check(checks, 'setinfo-has-30-unique-call-sites', len(info) == 30, len(info))
    check(checks, 'setinfo-callers-are-10-methods', len({row['caller'] for row in info}) == 10,
          sorted({row['caller'] for row in info}))
    check(checks, 'setinfo-callers-span-8-classes',
          sorted({row['class_name'] for row in info}) ==
          sorted(['Board_EventSeasonPass', 'Board_PVP', 'Board_QuestRewards',
                  'Board_QuestRewards.<OpenBox>d__43', 'Popup_ArenaShopExchange',
                  'Popup_PVPShopExchange', 'Popup_PVPRewards', 'TimeFreeRewardPack']),
          sorted({row['class_name'] for row in info}))
    quest = [row for row in info if row['class_name'].startswith('Board_QuestRewards')]
    check(checks, 'the-quest-box-state-machine-owns-13-rows',
          sum(1 for row in quest if row['class_name'].endswith('<OpenBox>d__43')) == 13
          and len(quest) == 14, len(quest))
    pass_board = [row for row in info if row['class_name'] == 'Board_EventSeasonPass']
    check(checks, 'the-event-pass-board-owns-9-rows', len(pass_board) == 9, len(pass_board))
    check(checks, 'three-sites-pass-a-null-box-sprite',
          sum(1 for row in info if (row['arguments']['box'] or {}).get('kind') == 'zero') == 3,
          [dict(caller=row['caller'], rva=row['call']) for row in info
           if (row['arguments']['box'] or {}).get('kind') == 'zero'])
    check(checks, 'only-the-two-shop-popups-tail-call-setinfo',
          sorted(row['class_name'] for row in info if row['tail']) ==
          ['Popup_ArenaShopExchange', 'Popup_PVPShopExchange'],
          [row['class_name'] for row in info if row['tail']])
    check(checks, 'every-setinfo-site-passes-a-null-bonus',
          all((row['arguments']['bonus'] or {}).get('op') == 'mov x5, xzr' for row in info),
          sorted({(row['arguments']['bonus'] or {}).get('op') for row in info}))
    check(checks, 'the-isCards-badge-is-a-literal-except-once',
          sum(1 for row in info if (row['arguments']['isCards'] or {}).get('kind') == 'flag') == 1,
          argument_table(sites)['isCards'])
    check(checks, 'the-one-computed-badge-is-board_pvp',
          [row['class_name'] for row in info
           if (row['arguments']['isCards'] or {}).get('kind') == 'flag'] == ['Board_PVP'],
          [row['class_name'] for row in info
           if (row['arguments']['isCards'] or {}).get('kind') == 'flag'])
    scales = {(row['arguments']['scale'] or {}).get('detail')
              for row in info if (row['arguments']['scale'] or {}).get('kind') == 'rodata'}
    check(checks, 'two-rodata-floats-are-used-as-the-icon-scale',
          scales == {'0x756c14', '0x756f10'}, sorted(scales))
    check(checks, 'the-literal-scales-are-1-1.25-and-1.5',
          {row['arguments']['scale']['detail'] for row in info
           if (row['arguments']['scale'] or {}).get('kind') == 'float'} ==
          {'1.00000000', '1.25000000', '1.50000000'},
          sorted({row['arguments']['scale']['detail'] for row in info
                  if (row['arguments']['scale'] or {}).get('kind') == 'float'}))
    check(checks, 'one-site-takes-its-number-from-the-preceding-call',
          sum(1 for row in info
              if (row['arguments']['number'] or {}).get('kind') == 'call-return') == 1,
          [dict(caller=row['caller'], rva=row['call'], arg=row['arguments']['number'])
           for row in info if (row['arguments']['number'] or {}).get('kind') == 'call-return'])
    check(checks, 'three-sites-hardcode-number-one',
          sum(1 for row in info if (row['arguments']['number'] or {}).get('kind') == 'literal'
              and row['arguments']['number']['detail'] == 1) == 3,
          [dict(caller=row['caller'], rva=row['call']) for row in info
           if (row['arguments']['number'] or {}).get('kind') == 'literal'
           and row['arguments']['number']['detail'] == 1])

    # -- SetNumber / GetShortNumber ---------------------------------------
    number = by_target(sites, 'SetNumber')
    check(checks, 'setnumber-has-4-call-sites', len(number) == 4, len(number))
    check(checks, 'setnumber-callers-are-the-two-onchange-bodies-plus-two',
          sorted((row['class_name'], row['call']) for row in number) ==
          [('Board_EventSeasonPass', 19440912), ('Box_Rewards', 19991068),
           ('Popup_ArenaShopExchange', 22835544), ('Popup_PVPShopExchange', 19888504)],
          sorted((row['class_name'], row['call']) for row in number))
    check(checks, 'the-box_rewards-caller-is-the-setinfo-tail-call',
          [row['call'] for row in number if row['class_name'] == CLASS] == [19991068]
          and [row for row in number if row['class_name'] == CLASS][0]['tail'],
          [row for row in number if row['class_name'] == CLASS])
    popup_number = [row['arguments']['number'] for row in number
                    if row['class_name'].startswith('Popup_')]
    check(checks, 'the-two-shop-popups-pass-a-product',
          [profile['op'] for profile in popup_number] == ['mul w1, w8, w9'] * 2,
          [profile['op'] for profile in popup_number])
    check(checks, '165-onchange-call-sites-match',
          {row['call'] for row in number if row['class_name'].startswith('Popup_')} ==
          {previous_['arena_on_change']['rva'], previous_['pvp_on_change']['rva']},
          {row['call'] for row in number if row['class_name'].startswith('Popup_')})
    short = by_target(sites, 'GetShortNumber')
    check(checks, 'getshortnumber-has-exactly-one-caller',
          len(short) == 1 and short[0]['class_name'] == CLASS
          and short[0]['caller'] == previous_['set_number'] and short[0]['call'] == 20001656,
          short)
    check(checks, 'the-short-number-caller-is-setnumber-itself',
          short and short[0]['method'] == 'GetShortNumber'
          and short[0]['signature'].split('(')[0].split()[-1] == 'SetNumber',
          short[0]['signature'] if short else None)

    # -- the four with no call site ---------------------------------------
    quiet = ['SetBoxSprite', 'SetIconSprite', 'SetGrayScale', '.ctor']
    check(checks, 'four-methods-have-no-call-site-in-the-pinned-slices',
          all(not by_target(sites, name) for name in quiet),
          {name: len(by_target(sites, name)) for name in quiet})
    check(checks, 'no-call-site-is-not-a-proof-of-dead-code',
          all(not by_target(sites, name) for name in quiet) and stats['multi_slice'] > 0,
          'eight slices are a sample, not the whole image')
    check(checks, 'the-grey-flag-165-measured-is-written-inline-not-through-setgrayscale',
          previous_['set_number'] == 20001584
          and any(call['method'] == 'SetFloat' for call in
                  load(PREV165)['shops']['Arena_Shop']['on_change']['calls']),
          'popup writes Material.SetFloat directly')

    # -- how the prefix is loaded, and why a stale x0 is harmless --------
    chain = prefix_chain()
    check(checks, 'setnumber-loads-the-prefix-through-two-dereferences',
          chain['page'] and chain['first_load'] and chain['second_load']
          and chain['page']['rva'] < chain['first_load']['rva'] < chain['second_load']['rva'],
          chain)
    check(checks, 'the-prefix-and-the-shortened-number-feed-string-concat',
          chain['concat'] and chain['concat']['target'] == 33439876
          and 'Concat' in (chain['concat']['signature'] or '')
          and chain['move_to_x0']['rva'] < chain['concat']['rva'],
          chain['concat'])
    check(checks, 'getshortnumber-never-reads-this',
          chain['get_short_reads_this'] == 0, chain['get_short_reads_this'])
    check(checks, 'the-getshortnumber-call-leaves-x0-stale',
          chain['x0_writes_before_the_call'] == [], chain['x0_writes_before_the_call'])

    # -- agreement with 164/165/166 ---------------------------------------
    check(checks, '166-constants-still-pin-the-same-rvas',
          previous_['set_info'] == 19990656 and previous_['get_short'] == 20001844
          and previous_['set_number'] == 20001584,
          [previous_['set_info'], previous_['get_short'], previous_['set_number']])
    check(checks, '166-setinfo-tail-agrees-with-this-table',
          previous_['info_tail']['target'] == 20001584 and previous_['info_tail']['tail'],
          previous_['info_tail'])
    check(checks, '166-popup-tail-is-the-same-setinfo-site',
          previous_['popup_tail']['target'] == 19990656
          and previous_['popup_tail']['rva'] == 22837708
          and [row['op'] for row in previous_['popup_before'][1:3]] ==
          ['mov x5, xzr', 'mov x6, xzr'],
          previous_['popup_tail'])
    check(checks, 'previous-artifacts-keep-their-totals',
          previous_['box_totals']['fields'] == 11 and previous_['box_totals']['methods'] == 7
          and previous_['qty_totals']['shops'] == 2, previous_['qty_totals'])
    check(checks, 'the-popup-row-is-one-of-the-30-setinfo-sites',
          any(row['class_name'] == 'Popup_ArenaShopExchange' for row in info), len(info))
    return checks


def build(output):
    sites = call_sites()
    stats = rollup(sites)
    checks = run_checks(sites, stats)
    payload = dict(
        schema=1,
        boundary='static xref over the eight pinned slices; no FDE, runtime, emulator, or device',
        evidence='STATIC_ONLY_ORIGINAL_APK',
        class_=dict(name=CLASS, methods=[dict(name=name, rva=rva,
                                             signature=SIGNATURES[name],
                                             size=BD.method(CLASS, rva)['size'])
                                         for name, rva in TARGETS]),
        targets=stats['targets'], classes=stats['classes'],
        totals=dict(sites=stats['sites'], raw_hits=stats['raw'],
                    unique_methods=stats['unique_methods'],
                    multi_slice_methods=stats['multi_slice'],
                    slices=len(slices()),
                    checks_passed=sum(1 for row in checks if row['passed']),
                    checks_total=len(checks)),
        prefix=prefix_chain(),
        arguments=argument_table(sites),
        calls=sites,
        confirmations=[
            dict(item='165/166: the shop row is drawn by one of two popups',
                 result='both `SetEventRewardTabs` bodies are in the table and both reach '
                        '`SetInfo` with a tail `b`; the number comes from `OnChange`'),
            dict(item='166: the popup passes a null bonus',
                 result='all 30 `SetInfo` sites pass `x5 = xzr`, so the bonus text is empty '
                        'everywhere in the pinned slices'),
            dict(item='165: `SetNumber(rewards.number * count)`',
                 result='both shop popups pass `mul w1, w8, w9` at the call site, so the row '
                        'receives a product, not the bare `number`'),
            dict(item='166: who turns the grey flag on',
                 result='nobody calls `SetGrayScale` in the pinned slices; 165\'s popup writes '
                        '`Material.SetFloat` inline instead'),
        ],
        open_items=[
            dict(item='what cell 0x2ade140 actually holds',
                 status='MODEL_NOT_MEASURED runtime',
                 note='166 labelled it the prefix cell; the load here is two dereferences '
                      '(cell -> slot -> string) and the same cell is handed to the runtime '
                      'helper 17879080 right after the `tbnz` gate, so the label is a load '
                      'site, not a proven string object'),
            dict(item='the value behind rodata floats 0x756c14 / 0x756f10',
                 status='MODEL_NOT_MEASURED runtime',
                 note='no rodata window in the eight slices covers either address'),
            dict(item='what each caller\'s `this` row is (field offsets per class)',
                 status='MODEL_NOT_MEASURED',
                 note='the table records the register and the load, not the owning class field'),
            dict(item='whether `SetGrayScale` / `SetIconSprite` / `SetBoxSprite` have callers '
                      'outside the eight slices',
                 status='not consulted', note='eight pinned slices are a sample, not the image'),
        ],
        provenance=dict(
            dump=dict(path=BD.DUMP, sha256=sha_file(BD.DUMP)),
            slices=[dict(path='reverse-engineering/raw/%s/native.json.gz' % name,
                         sha256=sha_file('reverse-engineering/raw/%s/native.json.gz' % name))
                    for name, _ in slices()],
            previous=[dict(path=PREV165, sha256=sha_file(PREV165)),
                      dict(path=PREV166, sha256=sha_file(PREV166))]),
        checks=checks,
    )
    blob = json.dumps(payload, sort_keys=True, indent=1, ensure_ascii=False).encode('utf-8')
    packed = gzip.compress(blob, mtime=0)
    if output:
        (ROOT / output).write_bytes(packed)
    return payload, packed


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--output', default=ARTIFACT)
    args = parser.parse_args()
    payload, packed = build(args.output)
    failed = [row for row in payload['checks'] if not row['passed']]
    print(json.dumps(dict(bytes=len(packed), sha256=hashlib.sha256(packed).hexdigest(),
                          checks_passed=payload['totals']['checks_passed'],
                          checks_total=payload['totals']['checks_total'],
                          failed=[row['name'] for row in failed]), indent=1))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
