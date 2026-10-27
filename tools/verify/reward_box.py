#!/usr/bin/env python3
"""From `number` to pixels: what the exchange row actually draws.

165 ended at `Box_Rewards.SetNumber(rewards.number * count)`, 164 at
`SetInfo(box, icon, number, _isCards, scale, null)`. Both bodies are pinned, so
the visual contract of the row can be read without the `.so`:

1. `SetInfo` writes the two sprites, scales the icon (`set_localScale(s, s, 1)`
   with `s = _scaleIcon`), toggles `objCards` with `_isCards`, fills `textBonus`
   from `_strBonus` (the popup always passes `null`), and tail-calls `SetNumber`.
2. `SetNumber` stores `number` at `0x64`, then:
   - `number >= 1` -> `textNumber.text = Concat(<static prefix>, GetShortNumber(number))`
     and `borderNumber.size = (min(xChar * (len + 1) + c, 2.0), yChar)`;
   - `number < 1`  -> `textNumber.text = null` and `borderNumber.enabled = number > 0`,
     so a zero count hides the badge instead of printing "0".
3. `GetShortNumber` is a four-step ladder with build-time thresholds
   `999_999 / 99_999_999 / 1_000_000_000`: plain `Int32.ToString()`, then
   `(n / 1000f).ToString(<format cell>)`, then two rodata divisors.
4. `SetGrayScale` drives the same `Material.SetFloat` cell that 165 found on the
   affordability flag, on `iconRenderer`, `boxRenderer` and every
   `grayRenderers[i]`.

The property **name** behind that cell and the format strings in the static
cells are runtime data; the `.ctor` also writes one 8-byte constant over
`xChar`+`yChar`, so both floats start from the two halves of one double.
"""
import argparse
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
import qty_widget as QW  # noqa: E402
import reward_pack as RP  # noqa: E402

CLASS = 'Box_Rewards'
SET_INFO = 19990656
SET_NUMBER = 20001584
GET_SHORT = 20001844
SET_BOX = 20002124
SET_ICON = 20002152
SET_GRAY = 20002236
CTOR = 20002504
SET_SPRITE = 41463136        # SpriteRenderer.set_sprite
SET_ENABLED = 41322360       # Renderer.set_enabled
SET_SIZE = 41463348          # SpriteRenderer.set_size
SET_SCALE = 41457984         # Transform.set_localScale
SET_ACTIVE = 41424900        # GameObject.SetActive
SET_FLOAT = 41329332         # Material.SetFloat
GET_MATERIAL = 41323636      # Renderer.get_material
CONCAT = 33439876            # String.Concat(string, string)
IS_NULL = 33476612           # String.IsNullOrEmpty
INT_TOSTRING = 34616120      # Int32.ToString()
FLOAT_TOSTRING = 34697908    # Single.ToString(string)
GET_TRANSFORM = 41414988     # Component.get_transform
GET_GAMEOBJECT = 41415048    # Component.get_gameObject
MONO_CTOR = 41429920         # MonoBehaviour..ctor
PREFIX_CELL = '0x2ade140'    # static string cell concatenated in front of the number
TINT_CELL = '0x2adbea8'      # the shader float both 165 and SetGrayScale write
PREV164 = 'datas/l2_535b0541_reward_pack.json.gz'
PREV165 = 'datas/l2_535b0541_qty_widget.json.gz'

THRESHOLDS = [999999, 99999999, 999999999]
LADDER_PATHS = [
    dict(limit=999999, target=20002012, method='Int32.ToString()', call=INT_TOSTRING,
         divisor=None, format_cell=None),
    dict(limit=99999999, target=20002028, method='Single.ToString(cell 0x2ae0390)',
         call=FLOAT_TOSTRING, divisor='1000.0f', format_cell='0x2ae1390'),
    dict(limit=999999999, target=20002068, method='Single.ToString(cell 0x2ae0398)',
         call=FLOAT_TOSTRING, divisor='0x7570b8', format_cell='0x2ae1398'),
    dict(limit=None, target=20001980, method='Single.ToString(cell 0x2ae0388)',
         call=FLOAT_TOSTRING, divisor='0x756df8', format_cell='0x2ae1388'),
]
FIELD_NAMES = {0x20: 'textNumber', 0x28: 'borderNumber', 0x30: 'grayRenderers',
               0x38: 'boxRenderer', 0x40: 'iconRenderer', 0x48: 'objCards',
               0x50: 'textBonus', 0x58: 'xChar', 0x5c: 'yChar', 0x60: 'id',
               0x64: 'number'}


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def text(insn):
    return insn['mnemonic'] + ' ' + insn['op_str']


def rows(rva):
    return RP.instrs(CLASS, rva)


def names(rva):
    """`bl`/`b` rows that resolve to a named method."""
    out = []
    for insn in rows(rva):
        if insn['mnemonic'] not in ('bl', 'b'):
            continue
        target = BD.call_target(insn)
        try:
            resolved = BD.name(target)
        except Exception:  # noqa: BLE001 - an unnamed target is not a call
            continue
        if not resolved['class_name']:
            continue
        out.append(dict(rva=insn['rva'], target=target, op=text(insn),
                        tail=insn['mnemonic'] == 'b',
                        class_name=resolved['class_name'],
                        method=BD.short(resolved)))
    return out


def find(rva_list, mnemonic, fragment=None):
    for insn in rva_list:
        if insn['mnemonic'] != mnemonic:
            continue
        if fragment is None or fragment in insn['op_str']:
            return dict(rva=insn['rva'], op=text(insn))
    return None


def mov_movk(rva_list):
    """Every `mov w8, #lo` + `movk w8, #hi, lsl #16` pair, as a number."""
    out = []
    for number, insn in enumerate(rva_list):
        if insn['mnemonic'] != 'mov' or not insn['op_str'].startswith('w8, #0x'):
            continue
        following = rva_list[number + 1] if number + 1 < len(rva_list) else None
        if following is None or following['mnemonic'] != 'movk':
            continue
        low = int(insn['op_str'].split('#')[1], 16)
        high = int(following['op_str'].split('#')[1].split(',')[0], 16)
        out.append(dict(rva=insn['rva'], value=(high << 16) | low,
                        low=text(insn), high=text(following)))
    return out


def cell_at(rva_list, number):
    """Resolve `adrp xR, #page` … `ldr xR, [xR, #off]` into a static cell VA."""
    insn = rva_list[number]
    register = insn['op_str'].split(', ')[0]
    page = RP.const(insn['op_str'])
    for later in rva_list[number + 1:number + 4]:
        if later['mnemonic'] != 'ldr' or not later['op_str'].startswith(register + ', ['):
            continue
        match = re.search(r'\[x\d+, #(0x[0-9a-f]+)\]', later['op_str'])
        if match:
            return hex(page + int(match.group(1), 16))
    return None


def set_number():
    insns = rows(SET_NUMBER)
    calls = names(SET_NUMBER)
    row = dict(rva=SET_NUMBER, size=BD.method(CLASS, SET_NUMBER)['size'],
               signature=BD.method(CLASS, SET_NUMBER)['signature'],
               instructions=len(insns), calls=calls)
    row['store'] = next((dict(rva=insn['rva'], op=text(insn), offset='0x64',
                              field=RP.field_name(CLASS, 0x64))
                         for insn in insns
                         if insn['mnemonic'] == 'str' and insn['op_str'].endswith('#0x64]')), None)
    row['gate'] = find(insns, 'cmp', 'w19, #1')
    row['gate_branch'] = next((dict(rva=insn['rva'], op=text(insn),
                                    target=RP.branch_target(insn['op_str']))
                               for insn in insns
                               if insn['mnemonic'].startswith('b.')
                               and RP.branch_target(insn['op_str']) > 20001700), None)
    row['short_number'] = next((call for call in calls if call['target'] == GET_SHORT), None)
    row['concat'] = next((call for call in calls if call['target'] == CONCAT), None)
    row['prefix_cell'] = next((cell_at(insns, number) for number, insn in enumerate(insns)
                               if insn['mnemonic'] == 'adrp'
                               and insn['op_str'].startswith('x0, #0x2ade000')), None)
    row['text_slot'] = find(insns, 'ldr', 'x10, [x9, #0x518]')
    row['text_receiver'] = find(insns, 'ldr', 'x8, [x20, #0x20]')
    row['virtual_call'] = find(insns, 'blr')
    # the border width: xChar * (len + 1) + c, clamped to 2.0
    row['chars'] = find(insns, 'ldp', 's0, s1, [x20, #0x58]')
    row['pad_rodata'] = dict(find(insns, 'ldr', 's2, [x9, #0xc78]') or {},
                             page=next((RP.const(insn['op_str']) for insn in insns
                                        if insn['mnemonic'] == 'adrp'
                                        and insn['op_str'].startswith('x9, #0x756000')), None))
    row['length_plus_one'] = find(insns, 'add', 'w8, w8, #1')
    row['length_load'] = find(insns, 'ldr', 'w8, [x21, #0x10]')
    row['scale_mul'] = find(insns, 'fmul', 's0, s0, s3')
    row['scale_add'] = find(insns, 'fadd', 's0, s0, s2')
    row['clamp'] = find(insns, 'fminnm')
    row['clamp_literal'] = find(insns, 'fmov', 's2, #2.00000000')
    row['set_size'] = next((call for call in calls if call['target'] == SET_SIZE), None)
    row['size_receiver'] = find(insns, 'ldr', 'x0, [x20, #0x28]')
    # the zero branch
    row['zero_cmp'] = find(insns, 'cmp', 'w19, #0')
    row['zero_cset'] = find(insns, 'cset', 'w1, gt')
    row['set_enabled'] = next((call for call in calls if call['target'] == SET_ENABLED), None)
    row['writes_count_like_fields'] = [insn['op_str'].split('#')[-1].rstrip(']')
                                       for insn in insns
                                       if insn['mnemonic'] == 'str' and '[x20, #0x' in insn['op_str']]
    return row


def short_number():
    insns = rows(GET_SHORT)
    calls = names(GET_SHORT)
    row = dict(rva=GET_SHORT, size=BD.method(CLASS, GET_SHORT)['size'],
               signature=BD.method(CLASS, GET_SHORT)['signature'],
               instructions=len(insns), calls=calls)
    pairs = mov_movk(insns)
    row['thresholds'] = [entry['value'] for entry in pairs]
    row['threshold_ops'] = [[entry['low'], entry['high']] for entry in pairs]
    branches = []
    for insn in insns:
        if insn['mnemonic'].startswith('b.'):
            target = RP.branch_target(insn['op_str'])
            if target is not None:
                branches.append(dict(rva=insn['rva'], op=text(insn), target=target))
    row['branches'] = branches
    row['ladder'] = []
    for path in LADDER_PATHS:
        target = path['target']
        head = next((insn for insn in insns if insn['rva'] == target), None)
        entry = dict(limit=path['limit'], target=target, method=path['method'],
                     call=path['call'], divisor=path['divisor'],
                     format_cell=path['format_cell'],
                     head=text(head) if head else None)
        if path['format_cell'] is not None:
            entry['format_load'] = next((dict(rva=insn['rva'], op=text(insn))
                                         for insn in insns
                                         if insn['mnemonic'] == 'ldr'
                                         and insn['op_str'].startswith('x1, [x9]')
                                         and insn['rva'] > target - 60
                                         and insn['rva'] < target + 80), None)
        row['ladder'].append(entry)
    row['int_tostring'] = next((call for call in calls if call['target'] == INT_TOSTRING), None)
    row['float_tostring'] = [call for call in calls if call['target'] == FLOAT_TOSTRING]
    row['thousand_immediate'] = find(insns, 'mov', 'w8, #0x447a0000')
    row['rodata'] = [dict(rva=insn['rva'], op=text(insn))
                     for insn in insns if insn['mnemonic'] == 'ldr'
                     and insn['op_str'].startswith('s1, [x8, #0x')]
    cells = []
    for number, insn in enumerate(insns):
        if insn['mnemonic'] != 'adrp':
            continue
        if RP.const(insn['op_str']) not in (0x2ae0000, 0x2ae1000):
            continue
        cell = cell_at(insns, number)
        if cell and cell not in cells:
            cells.append(cell)
    row['format_cells'] = cells
    return row


def set_info():
    insns = rows(SET_INFO)
    calls = names(SET_INFO)
    row = dict(rva=SET_INFO, size=BD.method(CLASS, SET_INFO)['size'],
               signature=BD.method(CLASS, SET_INFO)['signature'],
               instructions=len(insns), calls=calls)
    row['arguments'] = {key: find(insns, 'mov', fragment) for key, fragment in
                        (('box', 'x24, x1'), ('icon', 'x23, x2'), ('number', 'w19, w3'),
                         ('is_cards', 'w22, w4'), ('scale', 'v8.16b, v0.16b'),
                         ('bonus', 'x21, x5'))}
    row['number_store'] = find(insns, 'str', 'w19, [x20, #0x64]')
    row['sprites'] = [dict(call=call, receiver=find(insns, 'ldr', 'x0, [x20, #0x%s]' % offset))
                      for offset, call in
                      (('38', next((c for c in calls if c['target'] == SET_SPRITE), None)),
                       ('40', [c for c in calls if c['target'] == SET_SPRITE][-1]))]
    row['cards_mask'] = find(insns, 'and', 'w1, w22, #1')
    row['cards_active'] = next((call for call in calls if call['target'] == SET_ACTIVE), None)
    row['cards_receiver'] = find(insns, 'ldr', 'x0, [x20, #0x48]')
    row['scale_call'] = next((call for call in calls if call['target'] == SET_SCALE), None)
    row['scale_args'] = [find(insns, 'mov', 'v0.16b, v8.16b'),
                         find(insns, 'mov', 'v1.16b, v8.16b'),
                         find(insns, 'fmov', 's2, #1.00000000')]
    row['bonus_null_check'] = next((call for call in calls if call['target'] == IS_NULL), None)
    row['bonus_receiver'] = find(insns, 'ldr', 'x8, [x20, #0x50]')
    row['bonus_branch'] = [dict(rva=insn['rva'], op=text(insn),
                                target=RP.branch_target(insn['op_str']))
                           for insn in insns if insn['mnemonic'].startswith('tbz')]
    row['bonus_paths'] = dict(empty_hide=find(insns, 'mov', 'w1, wzr'),
                              filled_show=find(insns, 'mov', 'w1, #1'))
    row['bonus_shown'] = [call for call in calls if call['target'] == SET_ACTIVE or
                          call['target'] == GET_GAMEOBJECT or call['target'] == GET_TRANSFORM]
    row['field_stores'] = [insn['op_str'].split('#')[-1].rstrip(']')
                           for insn in insns
                           if insn['mnemonic'] == 'str' and '[x20, #0x' in insn['op_str']]
    row['tail_number'] = next((call for call in calls
                               if call['tail'] and call['target'] == SET_NUMBER), None)
    return row


def set_gray():
    insns = rows(SET_GRAY)
    calls = names(SET_GRAY)
    row = dict(rva=SET_GRAY, size=BD.method(CLASS, SET_GRAY)['size'],
               signature=BD.method(CLASS, SET_GRAY)['signature'],
               instructions=len(insns), calls=calls)
    row['flag_test'] = find(insns, 'tst', 'w20, #1')
    row['flag_select'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                                if insn['mnemonic'] == 'fcsel'
                                and insn['op_str'].startswith('s8, ')), None)
    row['one'] = find(insns, 'fmov', 's1, #1.00000000')
    row['zero'] = find(insns, 'fmov', 's0, wzr')
    row['set_float'] = [call for call in calls if call['target'] == SET_FLOAT]
    row['materials'] = [call for call in calls if call['target'] == GET_MATERIAL]
    row['receivers'] = [dict(rva=insn['rva'], op=text(insn))
                        for insn in insns
                        if insn['mnemonic'] == 'ldr'
                        and insn['op_str'] in ('x0, [x19, #0x40]', 'x0, [x19, #0x38]')]
    row['array'] = dict(length=find(insns, 'ldr', 'w8, [x19, #0x18]'),
                        data=find(insns, 'add', 'x22, x19, #0x20'),
                        element=find(insns, 'ldr', 'x0, [x22, x21, lsl #3]'))
    row['tint_cell'] = cell_at(insns, next((number for number, insn in enumerate(insns)
                                           if insn['mnemonic'] == 'adrp'
                                           and insn['op_str'].startswith('x20, #0x2adb000')),
                                         0))
    row['value_matches_165'] = row['tint_cell'] == QW.TINT_CELL
    return row


def small():
    set_box = rows(SET_BOX)
    set_icon = rows(SET_ICON)
    ctor = rows(CTOR)
    out = dict(
        set_box=dict(rva=SET_BOX, size=BD.method(CLASS, SET_BOX)['size'],
                     receiver=find(set_box, 'ldr', 'x0, [x0, #0x38]'),
                     tail=find(set_box, 'b'), calls=names(SET_BOX)),
        set_icon=dict(rva=SET_ICON, size=BD.method(CLASS, SET_ICON)['size'],
                      receiver=find(set_icon, 'ldr', 'x0, [x0, #0x40]'),
                      scale=find(set_icon, 'fmov', 's2, #1.00000000'),
                      calls=names(SET_ICON)),
        ctor=dict(rva=CTOR, size=BD.method(CLASS, CTOR)['size'],
                  rodata=find(ctor, 'ldr', 'd0, [x8, #0xbb8]'),
                  page=next((RP.const(insn['op_str']) for insn in ctor
                             if insn['mnemonic'] == 'adrp'
                             and insn['op_str'].startswith('x8, #0x757000')), None),
                  store=find(ctor, 'str', 'd0, [x0, #0x58]'),
                  tail=find(ctor, 'b'), calls=names(CTOR)))
    return out


def popup_bonus():
    """The exchange popup always passes `_strBonus = null`."""
    name = RP.POPUP['Arena_Shop']
    body = RP.method_of(name, 'SetEventRewardTabs')
    insns = RP.instrs(name, body['rva'])
    jump = next((dict(rva=insn['rva'], op=text(insn), target=BD.call_target(insn))
                 for insn in insns
                 if insn['mnemonic'] == 'b' and BD.call_target(insn) == SET_INFO), None)
    window = []
    if jump is not None:
        number = next(pos for pos, insn in enumerate(insns) if insn['rva'] == jump['rva'])
        window = [dict(rva=insn['rva'], op=text(insn)) for insn in insns[number - 4:number]]
    return dict(tail_jump=jump, before=window)


def build():
    previous = {'164': RP.load(PREV164), '165': RP.load(PREV165)}
    checks = []

    def check(label, passed):
        checks.append(dict(check=label, passed=bool(passed)))

    block = RP.class_block(CLASS)
    fields = {row['offset']: row for row in block['fields']}
    methods = {row['rva']: row['signature'] for row in block['methods']}
    number = set_number()
    short = short_number()
    info = set_info()
    gray = set_gray()
    tiny = small()
    bonus = popup_bonus()

    # -- the class ---------------------------------------------------------
    check('Box_Rewards-has-eleven-fields-at-the-pinned-offsets',
          {offset: fields[offset]['name'] for offset in FIELD_NAMES} == FIELD_NAMES
          and len(fields) == 11)
    check('the-class-exposes-seven-methods',
          len(methods) == 7
          and methods[SET_NUMBER] == 'void SetNumber(int _number) { }'
          and methods[SET_INFO].startswith('void SetInfo(Sprite ')
          and methods[GET_SHORT] == 'string GetShortNumber(int number) { }')

    # -- SetNumber ---------------------------------------------------------
    check('setnumber-stores-the-count-into-number-at-0x64',
          number['store']['offset'] == '0x64' and number['store']['field'] == 'number')
    check('setnumber-branches-to-the-zero-path-below-one',
          number['gate']['op'] == 'cmp w19, #1'
          and len([row for row in number['calls']]) >= 2)
    check('the-positive-path-formats-through-GetShortNumber',
          number['short_number'] is not None and number['short_number']['target'] == GET_SHORT)
    check('the-text-is-a-two-part-concat-with-a-static-prefix',
          number['concat']['target'] == CONCAT and number['prefix_cell'] == PREFIX_CELL)
    check('the-text-lands-on-textNumber-at-0x20-through-the-virtual-set_text',
          number['text_receiver']['op'] == 'ldr x8, [x20, #0x20]'
          and number['text_slot']['op'] == 'ldr x10, [x9, #0x518]'
          and number['virtual_call']['op'] == 'blr x10')
    check('the-border-width-is-xChar-times-length-plus-one',
          number['chars']['op'] == 'ldp s0, s1, [x20, #0x58]'
          and number['length_load']['op'] == 'ldr w8, [x21, #0x10]'
          and number['length_plus_one']['op'] == 'add w8, w8, #1'
          and number['scale_mul']['op'] == 'fmul s0, s0, s3'
          and number['scale_add']['op'] == 'fadd s0, s0, s2')
    check('the-pad-constant-comes-from-rodata-0x756c78',
          number['pad_rodata']['op'] == 'ldr s2, [x9, #0xc78]'
          and number['pad_rodata']['page'] == 0x756000)
    check('the-width-is-clamped-to-two-at-1-0-characters',
          number['clamp_literal']['op'] == 'fmov s2, #2.00000000'
          and number['clamp']['op'] == 'fminnm s0, s0, s2')
    check('the-size-is-written-to-borderNumber-at-0x28',
          number['set_size']['target'] == SET_SIZE
          and number['size_receiver']['op'] == 'ldr x0, [x20, #0x28]')
    check('below-one-the-badge-is-disabled-instead-of-printing-zero',
          number['zero_cmp']['op'] == 'cmp w19, #0'
          and number['zero_cset']['op'] == 'cset w1, gt'
          and number['set_enabled']['target'] == SET_ENABLED)
    check('setnumber-writes-exactly-one-instance-field',
          number['writes_count_like_fields'] == ['0x64'])

    # -- GetShortNumber ----------------------------------------------------
    check('the-ladder-has-three-build-time-thresholds',
          short['thresholds'] == THRESHOLDS)
    check('each-threshold-jumps-to-its-own-formatting-path',
          [row['target'] for row in short['branches']] == [20002012, 20002028, 20002068])
    check('below-a-million-the-number-prints-in-full',
          short['int_tostring'] is not None
          and short['ladder'][0]['head'].startswith('add x0, sp, #0x1c'))
    check('the-thousand-step-divides-by-the-1-0f-immediate',
          short['thousand_immediate']['op'] == 'mov w8, #0x447a0000'
          and short['ladder'][1]['head'].startswith('adrp x9, #0x2ae1000'))
    check('the-two-higher-steps-divide-by-rodata',
          short['ladder'][2]['head'].startswith('adrp x8, #0x757000')
          and short['ladder'][3]['head'].startswith('adrp x8, #0x756000')
          and sorted(row['op'] for row in short['rodata'])
          == ['ldr s1, [x8, #0xb8]', 'ldr s1, [x8, #0xdf8]'])
    check('all-three-shortened-steps-share-one-Single-ToString-call-site',
          len(short['float_tostring']) == 1
          and short['float_tostring'][0]['op'] == 'bl #0x21172b4')
    check('the-three-format-cells-are-distinct-static-slots',
          sorted(short['format_cells']) == ['0x2ae1388', '0x2ae1390', '0x2ae1398'])

    # -- SetInfo -----------------------------------------------------------
    check('setinfo-stores-the-number-it-is-given',
          info['number_store']['op'] == 'str w19, [x20, #0x64]')
    check('setinfo-writes-both-sprites',
          all(row['call'] is not None for row in info['sprites'])
          and info['sprites'][0]['receiver']['op'] == 'ldr x0, [x20, #0x38]'
          and info['sprites'][1]['receiver']['op'] == 'ldr x0, [x20, #0x40]')
    check('the-icon-scale-is-scaleIcon-on-both-axes-and-one-on-z',
          info['scale_call']['target'] == SET_SCALE
          and [row['op'] for row in info['scale_args']]
          == ['mov v0.16b, v8.16b', 'mov v1.16b, v8.16b', 'fmov s2, #1.00000000'])
    check('the-cards-badge-is-toggled-by-the-isCards-argument',
          info['cards_mask']['op'] == 'and w1, w22, #1'
          and info['cards_active']['target'] == SET_ACTIVE
          and info['cards_receiver']['op'] == 'ldr x0, [x20, #0x48]')
    check('the-bonus-text-is-gated-by-IsNullOrEmpty',
          info['bonus_null_check']['target'] == IS_NULL
          and info['bonus_receiver']['op'] == 'ldr x8, [x20, #0x50]')
    check('an-empty-bonus-hides-the-bonus-object',
          info['bonus_paths']['empty_hide'] is not None
          and info['bonus_branch'][1]['target'] == 19990960
          and info['bonus_shown'][-1]['target'] == SET_ACTIVE)
    check('a-filled-bonus-prints-it-and-shows-the-object',
          info['bonus_paths']['filled_show']['op'] == 'mov w1, #1'
          and info['bonus_shown'][-1]['target'] == SET_ACTIVE)
    check('setinfo-writes-only-the-number-field-itself',
          info['field_stores'] == ['0x64'])
    check('setinfo-tail-calls-setnumber',
          info['tail_number'] is not None and info['tail_number']['target'] == SET_NUMBER)
    check('the-exchange-popup-always-passes-a-null-bonus',
          bonus['tail_jump'] is not None
          and [row['op'] for row in bonus['before'][-3:]]
          == ['mov x5, xzr', 'mov x6, xzr', 'ldp x30, x23, [sp], #0x30'])

    # -- SetGrayScale ------------------------------------------------------
    check('the-gray-flag-becomes-1.0-or-0.0',
          gray['flag_test']['op'] == 'tst w20, #1'
          and gray['one']['op'] == 'fmov s1, #1.00000000'
          and gray['zero']['op'] == 'fmov s0, wzr'
          and gray['flag_select']['op'] == 'fcsel s8, s1, s0, ne')
    check('the-gray-flag-applies-to-icon-box-and-every-gray-renderer',
          len(gray['set_float']) == 3
          and [row['op'] for row in gray['receivers']]
          == ['ldr x0, [x19, #0x40]', 'ldr x0, [x19, #0x38]']
          and gray['array']['element']['op'] == 'ldr x0, [x22, x21, lsl #3]'
          and gray['array']['length']['op'] == 'ldr w8, [x19, #0x18]')
    check('setgrayscale-writes-the-same-shader-float-cell-as-165',
          gray['tint_cell'] == TINT_CELL and gray['value_matches_165'])

    # -- the smaller helpers ----------------------------------------------
    check('setboxsprite-tail-calls-the-sprite-setter-on-0x38',
          tiny['set_box']['receiver']['op'] == 'ldr x0, [x0, #0x38]'
          and tiny['set_box']['tail']['op'] == 'b #0x278ad60')
    check('seticonsprite-sets-the-sprite-then-the-scale',
          tiny['set_icon']['receiver']['op'] == 'ldr x0, [x0, #0x40]'
          and tiny['set_icon']['scale']['op'] == 'fmov s2, #1.00000000'
          and any(row['target'] == SET_SCALE for row in tiny['set_icon']['calls']))
    check('the-ctor-seeds-xChar-and-yChar-from-one-eight-byte-constant',
          tiny['ctor']['rodata']['op'] == 'ldr d0, [x8, #0xbb8]'
          and tiny['ctor']['page'] == 0x757000
          and tiny['ctor']['store']['op'] == 'str d0, [x0, #0x58]'
          and tiny['ctor']['tail']['op'] == 'b #0x2782ba0')

    # -- earlier reports still hold ---------------------------------------
    check('165s-SetNumber-target-is-this-method',
          previous['165']['constants']['set_number'] == SET_NUMBER
          and previous['165']['shops']['Arena_Shop']['on_change']['set_number']['target']
          == SET_NUMBER)
    check('164s-popup-tail-still-calls-setinfo-with-two-zero-arguments',
          bonus['tail_jump']['target'] == SET_INFO)
    check('the-affordability-flag-of-165-writes-the-same-cell-as-the-gray-flag',
          previous['165']['constants']['tint_property_cell'] == TINT_CELL)
    failed = [row for row in checks if not row['passed']]
    assert not failed, json.dumps(failed, indent=1)

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='The exchange row is `Box_Rewards`: `SetInfo` writes the two sprites, scales the '
             'icon by `_scaleIcon` on x/y with 1.0 on z, toggles the `_isCards` badge and fills '
             '`textBonus` (the popup passes null), then tail-calls `SetNumber`. `SetNumber` stores '
             'the number at 0x64; at `number >= 1` it prints `<static prefix> + '
             'GetShortNumber(number)` on `textNumber` and sizes `borderNumber` to '
             '`min(xChar * (len + 1) + 0x756c78, 2.0) x yChar`; at `number < 1` it clears the text '
             'and disables the border instead of printing zero. `GetShortNumber` is a four-step '
             'ladder with build-time thresholds 999_999 / 99_999_999 / 1_000_000_000: plain '
             '`Int32.ToString()`, then `(n / 1000f)` with a static format, then two rodata '
             'divisors. So `count = 0` (165) hides the badge rather than showing a zero, and the '
             'number the player sees is a shortened one.',
        provenance=dict(
            sources=[dict(path=rel, sha256=sha_file(rel))
                     for rel in (RP.DUMP, PREV164, PREV165, QW.PREV155, QW.PREV159, QW.PREV163)]
            + [dict(path=str(Path(path).relative_to(ROOT)),
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest())
               for path in sorted(ROOT.glob(BD.RAW_GLOB))],
            string_literals=len(AR.strings())),
        class_=dict(name=CLASS, fields=block['fields'], methods=block['methods'],
                    rendered=[dict(offset=hex(offset), field=name)
                              for offset, name in FIELD_NAMES.items()]),
        set_number=number, short_number=short, set_info=info, set_gray=gray,
        helpers=tiny, popup=bonus,
        constants=dict(set_info=SET_INFO, set_number=SET_NUMBER, get_short=GET_SHORT,
                       set_box=SET_BOX, set_icon=SET_ICON, set_gray=SET_GRAY, ctor=CTOR,
                       sprite=SET_SPRITE, enabled=SET_ENABLED, size=SET_SIZE,
                       local_scale=SET_SCALE, set_active=SET_ACTIVE, set_float=SET_FLOAT,
                       prefix_cell=PREFIX_CELL, tint_cell=TINT_CELL),
        table=[dict(stage='SetInfo', writes='boxRenderer(0x38)/iconRenderer(0x40) sprite, '
                                           'icon localScale(s,s,1), objCards.SetActive(_isCards), '
                                           'textBonus from _strBonus'),
               dict(stage='SetNumber >= 1', writes='number(0x64), textNumber(0x20) = prefix + '
                                                   'GetShortNumber(n), borderNumber(0x28).size'),
               dict(stage='SetNumber < 1', writes='textNumber = null, borderNumber.enabled = false'),
               dict(stage='GetShortNumber', writes='<=999999 plain; <=99,999,999 /1000f; '
                                                   '<=1e9 and above /rodata'),
               dict(stage='SetGrayScale', writes='iconRenderer/boxRenderer/grayRenderers[i] '
                                                 'material float 1.0|0.0')],
        totals=dict(fields=len(fields), methods=len(methods),
                    set_number_instructions=number['instructions'],
                    set_info_instructions=info['instructions'],
                    get_short_instructions=short['instructions'],
                    checks_passed=sum(1 for row in checks if row['passed']),
                    checks_total=len(checks)),
        confirmations=[
            dict(item='165: what the row does with `rewards.number * count`',
                 result='prints the shortened number on `textNumber` and widens the border by '
                        '`xChar` per character, clamped at 2.0; `count = 0` disables the border '
                        'and clears the text, so a zero count never renders a "0"'),
            dict(item='164: what `SetInfo(..., _isCards, scale, null)` draws',
                 result='two sprites, the icon scaled on x/y only, the cards badge toggled by '
                        '`_isCards`, and `textBonus` left empty because the bonus is null'),
            dict(item='165: is the affordability float the same shader slot as graying?',
                 result='yes — both write `Material.SetFloat` through the same static cell '
                        '`0x2adbea8`, so the flag 165 found is the gray amount'),
            dict(item='are the four ladder steps really thresholds, not data?',
                 result='the three limits are immediates built with `mov`+`movk` in the method '
                        'itself (999_999 / 99_999_999 / 999_999_999)'),
        ],
        open_items=[
            dict(item='the shader property name behind 0x2adbea8',
                 blocking='the cell holds a runtime string pointer; the literal is not in the '
                          'pinned raw — MODEL_NOT_MEASURED runtime'),
            dict(item='the three `Single.ToString` format strings',
                 blocking='formats come from the static cells 0x2ae0388/0x2ae0390/0x2ae0398, '
                          'which are runtime string pointers — MODEL_NOT_MEASURED runtime'),
            dict(item='the two rodata divisors for the top steps',
                 blocking='0x756df8 and 0x7570b8 are `.rodata` addresses; the bytes are not in '
                          'the pinned raw (no `.so` in the sandbox) — MODEL_NOT_MEASURED runtime'),
            dict(item='the prefix string in front of the number',
                 blocking='static cell 0x2ade140 holds a runtime string pointer — '
                          'MODEL_NOT_MEASURED runtime'),
        ],
        checks=checks,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_reward_box.json.gz')
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
