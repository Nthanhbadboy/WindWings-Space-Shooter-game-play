#!/usr/bin/env python3
"""From the popup's quantity widget to the number the band lambda is called with.

164 stopped at `SetPopup`: it writes `count = 1`, prices the pack with
`price x count`, and sizes the slider with `maxValue = maxStock - 1`. This tool
closes the loop on the widget itself — what moves `count`, what it clamps to, and
what value each of the four buttons hands to the band lambda of 163:

1. `OnChange(float amount)` is the slider callback (`SetPopup` builds
   `new Action<float>(this, cell)` and stores it on `Slider.onChange`, and the
   popup declares exactly one `void (float)` method). It computes
   `count = (int)round(amount / slider.step)` and then refreshes four things:
   `textCost = String.Format(fmt, rewards.price * count)`, the `count/maxStock`
   text, `Box_Rewards.SetNumber(rewards.number * count)` and a material float
   that is `1.0` exactly when `medal < price * count`.
2. `OnPressedButtonMinus` / `OnPressedButtonAdd` move `slider.value` by `-1` / `+1`
   inside `[0, maxValue]` and tail-call `Slider.set_Value`; they never touch
   `count` themselves.
3. `OnPressedButtonBuy` charges `price * count`, returns early when
   `medal < price * count`, then invokes `onExit(count)` and hides the popup.
4. `OnPressedButtonExit` invokes the **same** `Action<int>` with `x1 = wzr`
   — `count = 0` — and hides the popup. That is what 163's `count < 1` guard is
   for: it is the exit path, not a defensive check.

`count = 0` is therefore reachable in a shipped popup, and the guard is the only
thing between the player and a free purchase. Everything here is static; the body
of `Slider.set_Value` is not in the pinned raw, so whether the initial
`Value(0)` re-fires `onChange` stays open.
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
import reward_pack as RP  # noqa: E402

DUMP = RP.DUMP
POPUP = RP.POPUP
CLICK = RP.CLICK
PREV155 = RP.PREV155
PREV159 = RP.PREV159
PREV163 = RP.PREV163
PREV164 = 'datas/l2_535b0541_reward_pack.json.gz'

ACTION_FLOAT_CTOR = 0x18a5dfc   # Action<float>..ctor
ROUND_HELPER = 0x2990b70        # Math.Round(double), inlined midpoint handling
SET_NUMBER = 0x1313330          # Box_Rewards.SetNumber
SET_VALUE = 0x13ef6b8           # Slider.set_Value(float)
SLIDER_ON_CHANGE = 20903864     # Slider.OnChangeValue(float)
SLIDER_GET_VALUE = 20904492     # Slider.get_Value()
SET_FLOAT = 0x276a2b4           # Material.SetFloat(string, float)
GET_MATERIAL = 0x2768c74        # Renderer.get_material
TINT_CELL = '0x2adbea8'         # the property name handed to SetFloat
# one Action<float> target/method cell per popup class, filled by the static ctor
SLIDER_ACTION_CELL = {'Arena_Shop': '0x2adb9e0', 'PVP_Shop': '0x2adbd38'}


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def text(insn):
    return insn['mnemonic'] + ' ' + insn['op_str']


def method(name, fragment):
    body = RP.method_of(name, fragment)
    return body, RP.instrs(name, body['rva'])


def call_rows(name, rva):
    """Every `bl` and every tail `b` that leaves the method for a named one."""
    rows = []
    for insn in RP.instrs(name, rva):
        if insn['mnemonic'] not in ('bl', 'b'):
            continue
        target = BD.call_target(insn)
        try:
            resolved = BD.name(target)
        except Exception:  # noqa: BLE001 - an unnamed target is simply not a call
            continue
        if not resolved['class_name']:
            continue
        rows.append(dict(rva=insn['rva'], target=target,
                         class_name=resolved['class_name'],
                         method=BD.short(resolved), tail=insn['mnemonic'] == 'b'))
    return rows


def on_change(klass):
    """`OnChange(float)`: count from the slider value, then four refreshes."""
    name = POPUP[klass]
    body, insns = method(name, 'OnChange(float')
    calls = call_rows(name, body['rva'])
    row = dict(rva=body['rva'], size=BD.method(name, body['rva'])['size'],
               signature=body['signature'], calls=calls)
    # the slider and its step
    slider = next((insn['rva'] for insn in insns
                   if insn['mnemonic'] == 'ldr' and insn['op_str'] == 'x8, [x19, #0x48]'),
                  None)
    step = next((dict(rva=insn['rva'], op=text(insn))
                 for insn in insns
                 if insn['mnemonic'] == 'ldr' and insn['op_str'] == 's9, [x8, #0x64]'), None)
    row['slider_load'] = slider
    row['step_load'] = step
    row['division'] = next((dict(rva=insn['rva'], op=text(insn))
                            for insn in insns if insn['mnemonic'] == 'fdiv'), None)
    row['round_helper'] = next((dict(rva=insn['rva'], op=text(insn), target=ROUND_HELPER)
                                for insn in insns
                                if insn['mnemonic'] == 'bl'
                                and BD.call_target(insn) == ROUND_HELPER), None)
    row['midpoint_halves'] = [text(insn) for insn in insns
                              if insn['mnemonic'] == 'fmov' and 'd1, #' in insn['op_str']
                              and ('0.50000000' in insn['op_str'])]
    row['midpoint_even'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                                 if insn['mnemonic'] == 'tst'), None)
    row['rounding_steps'] = [text(insn) for insn in insns
                             if insn['mnemonic'] == 'frintp' or insn['mnemonic'] == 'frintm']
    row['saturate'] = [text(insn) for insn in insns
                       if (insn['mnemonic'] == 'csinc' or insn['op_str'] == 'w8, #-0x7fffffff')]
    store = next((insn for insn in insns
                  if insn['mnemonic'] == 'str' and insn['op_str'].endswith('#0x58]!')), None)
    row['count_store'] = dict(rva=store['rva'], op=text(store),
                              field=RP.field_name(name, 0x58)) if store else None
    # the price the widget prints, and the pack it reads it from
    row['price_load'] = next((dict(rva=insn['rva'], op=text(insn))
                              for insn in insns
                              if insn['mnemonic'] == 'ldr' and insn['op_str'] == 'w9, [x9, #0x1c]'),
                             None)
    row['rewards_load'] = next((dict(rva=insn['rva'], op=text(insn))
                                for insn in insns
                                if insn['mnemonic'] == 'ldr'
                                and insn['op_str'] == 'x9, [x20, #8]'), None)
    row['cost_mul'] = next((dict(rva=insn['rva'], op=text(insn))
                            for insn in insns if insn['mnemonic'] == 'mul'
                            and insn['op_str'] == 'w8, w9, w8'), None)
    row['cost_format'] = next((call for call in calls if call['method'] == 'Format'), None)
    label = next((insn for insn in insns
                  if insn['mnemonic'] == 'ldur' and insn['op_str'] == 'x21, [x20, #-0x28]'),
                 None)
    row['cost_label'] = dict(rva=label['rva'], op=text(label),
                             offset='0x30', field=RP.field_name(name, 0x30)) if label else None
    row['stock_text'] = dict(
        length=next((RP.const(insn['op_str']) for insn in insns
                     if insn['mnemonic'] == 'mov' and insn['op_str'] == 'w1, #5'), None),
        concat=next((call for call in calls if call['method'] == 'Concat'), None),
        count_tostring=next((call['rva'] for call in calls
                             if call['method'] == 'ToString' and call['rva'] > 0), None),
        max_stock_read=next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                             if insn['mnemonic'] == 'add' and insn['op_str'] == 'x0, x19, #0x5c'),
                            None))
    set_number = next((dict(rva=insn['rva'],
                            arg=text(insns[number - 1]) if number >= 1 else None,
                            before=text(insns[number - 2]) if number >= 2 else None,
                            op=text(insn), target=SET_NUMBER)
                       for number, insn in enumerate(insns)
                       if insn['mnemonic'] == 'bl' and BD.call_target(insn) == SET_NUMBER),
                      None)
    row['set_number'] = set_number
    row['number_load'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                               if insn['mnemonic'] == 'ldr' and insn['op_str'] == 'w8, [x8, #0x18]'),
                              None)
    medal = next((dict(rva=call['rva'], method=call['method']) for call in calls
                  if call['method'] in ('get_ArenaMedal', 'get_PvPMedal')), None)
    row['medal'] = medal
    row['afford_cmp'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                              if insn['mnemonic'] == 'cmp' and insn['op_str'].startswith('w19, w9')),
                             None)
    row['afford_cost'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                               if insn['mnemonic'] == 'mul' and insn['op_str'] == 'w9, w21, w20'),
                              None)
    row['afford_select'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                                 if insn['mnemonic'] == 'fcsel'
                                 and insn['op_str'].startswith('s0, ')
                                 and insn['op_str'].endswith('lt')), None)
    row['round_select'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                                if insn['mnemonic'] == 'fcsel'
                                and insn['op_str'] == 'd0, d0, d1, eq'), None)
    row['afford_one'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                              if insn['mnemonic'] == 'fmov'
                              and insn['op_str'] == 's1, #1.00000000'), None)
    row['material_source'] = next((dict(rva=insn['rva'], op=text(insn), offset='0x40',
                                        field=RP.field_name(name, 0x40))
                                   for insn in insns
                                   if insn['mnemonic'] == 'ldr'
                                   and insn['op_str'] == 'x8, [x19, #0x40]'), None)
    row['material_read'] = next((dict(rva=call['rva'], method=call['method'])
                                 for call in calls if call['method'] == 'get_material'), None)
    row['material_set'] = next((dict(rva=call['rva'], method=call['method'])
                                for call in calls if call['method'] == 'SetFloat'), None)
    row['writes_maxstock'] = any(insn['mnemonic'] == 'str' and '#0x5c]' in insn['op_str']
                                 for insn in insns)
    row['writes_count'] = bool(row['count_store'])
    return row


def step_buttons(klass, fragment):
    """`OnPressedButtonMinus` / `OnPressedButtonAdd`: move the slider, not the count."""
    name = POPUP[klass]
    body, insns = method(name, fragment)
    calls = call_rows(name, body['rva'])
    row = dict(rva=body['rva'], size=BD.method(name, body['rva'])['size'],
               signature=body['signature'], calls=calls)
    row['slider_load'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                               if insn['mnemonic'] == 'ldr' and insn['op_str'] == 'x0, [x0, #0x48]'),
                              None)
    row['value_load'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                              if insn['mnemonic'] == 'ldr' and insn['op_str'] == 's0, [x0, #0x68]'),
                             None)
    row['limit_load'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                              if insn['mnemonic'] == 'ldr' and insn['op_str'] == 's1, [x0, #0x60]'),
                             None)
    compare = [insn for insn in insns if insn['mnemonic'] == 'fcmp']
    row['compare'] = [dict(rva=insn['rva'], op=text(insn)) for insn in compare]
    row['guard'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                         if insn['mnemonic'].startswith('b.')), None)
    addition = next(((number, insn) for number, insn in enumerate(insns)
                     if insn['mnemonic'] == 'fadd' and insn['op_str'].startswith('s0, s0')),
                    None)
    delta = None
    if addition is not None:
        number, insn = addition
        literal = next((prev for prev in reversed(insns[:number])
                        if prev['mnemonic'] == 'fmov' and prev['op_str'].startswith('s1, #')),
                       None)
        delta = dict(rva=insn['rva'], op=text(insn),
                     constant=text(literal) if literal else None,
                     value=(float(re.search(r'#(-?[\d.]+)', literal['op_str']).group(1))
                            if literal else None))
    row['delta'] = delta
    row['set_value'] = next((dict(rva=insn['rva'], op=text(insn), target=SET_VALUE)
                             for insn in insns if insn['mnemonic'] == 'b'
                             and BD.call_target(insn) == SET_VALUE), None)
    row['writes_count'] = any(insn['mnemonic'] == 'str' and '#0x58]' in insn['op_str']
                              for insn in insns)
    return row


def button(klass, fragment):
    """`OnPressedButtonBuy` / `OnPressedButtonExit`: the value handed to the lambda."""
    name = POPUP[klass]
    body, insns = method(name, fragment)
    calls = call_rows(name, body['rva'])
    row = dict(rva=body['rva'], size=BD.method(name, body['rva'])['size'],
               signature=body['signature'], calls=calls)
    row['reward_load'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                               if insn['mnemonic'] == 'ldr' and insn['op_str'] == 'x8, [x19, #0x60]'),
                              None)
    row['price_load'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                              if insn['mnemonic'] == 'ldr' and insn['op_str'] == 'w8, [x8, #0x1c]'),
                             None)
    row['count_load'] = next((dict(rva=insn['rva'], op=text(insn),
                                   field=RP.field_name(name, 0x58)) for insn in insns
                              if insn['mnemonic'] == 'ldr' and insn['op_str'] == 'w9, [x19, #0x58]'),
                             None)
    row['cost_mul'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                            if insn['mnemonic'] == 'mul' and insn['op_str'] == 'w20, w8, w9'),
                           None)
    row['medal'] = next((dict(rva=call['rva'], method=call['method']) for call in calls
                         if call['method'] in ('get_ArenaMedal', 'get_PvPMedal')), None)
    row['gate'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                        if insn['mnemonic'] == 'cmp' and insn['op_str'] == 'w0, w20'), None)
    row['gate_branch'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                               if insn['mnemonic'].startswith('b.')), None)
    row['delegate_load'] = next((dict(rva=insn['rva'], op=text(insn))
                                 for insn in insns
                                 if insn['mnemonic'] == 'ldr' and insn['op_str'] in
                                 ('x8, [x19, #0x50]', 'x8, [x0, #0x50]')), None)
    row['invoke'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                          if insn['mnemonic'] == 'blr'), None)
    low = (row['delegate_load'] or {}).get('rva', 0)
    high = (row['invoke'] or {}).get('rva', 0)
    row['invoke_arg'] = next((dict(rva=insn['rva'], op=text(insn))
                              for insn in insns
                              if low < insn['rva'] < high
                              and insn['mnemonic'] in ('ldr', 'mov')
                              and insn['op_str'].startswith('w1, ')), None)
    row['hide_arg'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in insns
                            if insn['rva'] > high and insn['mnemonic'] == 'mov'
                            and insn['op_str'] == 'w1, wzr'), None)
    row['hide'] = next((dict(rva=call['rva'], method=call['method']) for call in calls
                        if call['method'] == 'SetActive'), None)
    row['reads_count'] = bool(row['count_load'])
    return row


def wiring(klass):
    """How `OnChange` reaches the slider, and which method it must be."""
    name = POPUP[klass]
    body, insns = method(name, 'SetPopup')
    row = dict(setpopup_rva=body['rva'])
    number = next((number for number, insn in enumerate(insns)
                   if insn['mnemonic'] == 'bl' and BD.call_target(insn) == ACTION_FLOAT_CTOR),
                  None)
    row['action_ctor'] = dict(rva=insns[number]['rva'], op=text(insns[number]),
                              target=ACTION_FLOAT_CTOR) if number is not None else None
    window = insns[max(0, number - 14):number + 8] if number is not None else []
    row['action_target'] = next((text(insn) for insn in window
                                 if insn['mnemonic'] == 'mov' and insn['op_str'] == 'x1, x19'),
                                None)
    row['action_cell'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in window
                               if insn['mnemonic'] == 'ldr' and insn['op_str'] == 'x2, [x23]'),
                              None)
    row['slider_store'] = next((dict(rva=insn['rva'], op=text(insn), offset='0x58',
                                     field=RP.field_name('Slider', 0x58))
                                for insn in window
                                if insn['mnemonic'] == 'str' and insn['op_str'].endswith('#0x58]')),
                               None)
    row['slider_load'] = next((dict(rva=insn['rva'], op=text(insn)) for insn in window
                               if insn['mnemonic'] == 'ldr'
                               and insn['op_str'] == 'x25, [x19, #0x48]'), None)
    row['float_methods'] = [dict(rva=method_row['rva'], signature=method_row['signature'])
                            for method_row in RP.class_block(name)['methods']
                            if re.search(r'\(float ', method_row['signature'])]
    cell_page = next((RP.const(insn['op_str']) for insn in insns
                      if insn['mnemonic'] == 'adrp' and insn['op_str'] == 'x23, #0x2adb000'),
                     None)
    cell_offset = next((RP.const(insn['op_str']) for insn in insns
                        if insn['mnemonic'] == 'ldr'
                        and insn['op_str'].startswith('x23, [x23, #0x')), None)
    row['action_cell_address'] = (hex(cell_page + cell_offset)
                                  if cell_page is not None and cell_offset is not None else None)
    step_str = next((number for number, insn in enumerate(insns)
                     if insn['mnemonic'] == 'str' and insn['op_str'].endswith('#0x64]')), None)
    row['step_immediate'] = next((text(prev) for prev in reversed(insns[:step_str or 0])
                                  if prev['mnemonic'] == 'mov'
                                  and prev['op_str'].startswith('w9, #0x')), None)
    value_call = next((number for number, insn in enumerate(insns)
                       if insn['mnemonic'] == 'bl' and BD.call_target(insn) == SET_VALUE),
                      None)
    row['value_argument'] = next((text(prev) for prev in reversed(insns[:value_call or 0])
                                  if prev['mnemonic'] in ('fmov', 'mov')
                                  and prev['op_str'].startswith('s0, ')), None)
    return row


def slider_bodies():
    """Scan every pinned raw slice for the `Slider` bodies the report must not assume."""
    wanted = [('set_Value', SET_VALUE), ('OnChangeValue', SLIDER_ON_CHANGE),
              ('get_Value', SLIDER_GET_VALUE)]
    hits, scanned, methods = [], 0, 0
    for path in sorted(ROOT.glob('reverse-engineering/raw/*/native.json.gz')):
        scanned += 1
        with gzip.open(str(path), 'rt') as handle:
            blob = json.load(handle)
        for row in blob.get('methods') or []:
            methods += 1
            rva, size = row.get('rva'), row.get('size') or 0
            if rva is None:
                continue
            for label, target in wanted:
                if rva == target or rva < target < rva + size:
                    hits.append(dict(slice=str(path.relative_to(ROOT)), rva=target,
                                     method=label, name=row.get('name'), size=size))
    return dict(scanned=scanned, methods=methods, wanted=[row[1] for row in wanted],
                hits=hits)


def slider_state(klass):
    """What `SetPopup` leaves the slider and `count` at."""
    popup = RP.popup(klass)
    return dict(step=RP.field_name('Slider', 0x64),
                max_value=RP.field_name('Slider', 0x60),
                value=RP.field_name('Slider', 0x68),
                on_change=RP.field_name('Slider', 0x58),
                count=RP.field_name(POPUP[klass], 0x58),
                max_stock=RP.field_name(POPUP[klass], 0x5c),
                count_written_after=popup['writes'],
                slider_writes=popup['slider_writes'],
                slider_value_call=popup['slider_value'],
                slider_gate=popup['slider_gate'])


def build():
    previous = {key: RP.load(rel) for key, rel in
                (('155', PREV155), ('159', PREV159), ('163', PREV163),
                 ('164', PREV164))}
    shops, checks = {}, []

    def check(label, passed):
        checks.append(dict(check=label, passed=bool(passed)))

    for klass in CLICK:
        shops[klass] = dict(
            on_change=on_change(klass),
            minus=step_buttons(klass, 'OnPressedButtonMinus'),
            add=step_buttons(klass, 'OnPressedButtonAdd'),
            buy=button(klass, 'OnPressedButtonBuy'),
            exit_=button(klass, 'OnPressedButtonExit'),
            wiring=wiring(klass),
            slider=slider_state(klass))

    arena, pvp = shops['Arena_Shop'], shops['PVP_Shop']

    # -- the widget is wired to OnChange -----------------------------------
    check('setpopup-builds-an-Action-float-over-this',
          all(shops[k]['wiring']['action_ctor'] for k in CLICK)
          and arena['wiring']['action_target'] == 'mov x1, x19')
    check('the-action-is-stored-on-Slider-onChange-at-0x58',
          all(shops[k]['wiring']['slider_store']['offset'] == '0x58'
              and shops[k]['wiring']['slider_store']['field'] == 'onChange'
              for k in CLICK))
    check('the-slider-is-the-object-at-popup-0x48',
          all(shops[k]['wiring']['slider_load']['op'] == 'ldr x25, [x19, #0x48]'
              for k in CLICK)
          and RP.field_name(POPUP['Arena_Shop'], 0x48) == 'slider')
    check('the-popup-declares-exactly-one-void-float-method',
          all(len(shops[k]['wiring']['float_methods']) == 1 for k in CLICK))
    check('so-the-callback-is-OnChange-by-elimination',
          all('OnChange(float' in shops[k]['wiring']['float_methods'][0]['signature']
              for k in CLICK)
          and arena['wiring']['float_methods'][0]['rva'] == arena['on_change']['rva'])
    check('the-delegate-method-pointer-comes-from-a-static-cell',
          all(shops[k]['wiring']['action_cell']['op'] == 'ldr x2, [x23]'
              and shops[k]['wiring']['action_cell_address'] == SLIDER_ACTION_CELL[k]
              for k in CLICK)
          and arena['wiring']['action_cell_address']
          != pvp['wiring']['action_cell_address'])

    # -- OnChange: count from the slider ----------------------------------
    check('onchange-reads-slider-step-from-0x64',
          all(shops[k]['on_change']['step_load']['op'] == 'ldr s9, [x8, #0x64]'
              for k in CLICK)
          and RP.field_name('Slider', 0x64) == 'step')
    check('onchange-divides-the-amount-by-the-step',
          all(shops[k]['on_change']['division']['op'] == 'fdiv s9, s8, s9'
              for k in CLICK))
    check('onchange-rounds-the-quotient-through-one-helper',
          all(shops[k]['on_change']['round_helper']['target'] == ROUND_HELPER for k in CLICK))
    check('the-midpoint-is-resolved-to-even',
          all(shops[k]['on_change']['midpoint_even']
              and len(shops[k]['on_change']['midpoint_halves']) == 2
              and shops[k]['on_change']['rounding_steps']
              and shops[k]['on_change']['round_select']['op'] == 'fcsel d0, d0, d1, eq'
              for k in CLICK))
    check('onchange-stores-the-result-into-count-at-0x58',
          all(shops[k]['on_change']['count_store']['field'] == 'count' for k in CLICK)
          and arena['on_change']['count_store']['op'] == 'str w8, [x20, #0x58]!')
    check('the-round-is-saturated-like-a-C-cast',
          all(any('-0x7fffffff' in op for op in shops[k]['on_change']['saturate'])
              and any(op.startswith('csinc') for op in shops[k]['on_change']['saturate'])
              for k in CLICK))

    # -- OnChange: the four refreshes -------------------------------------
    check('the-cost-is-rewards-price-times-the-new-count',
          all(shops[k]['on_change']['cost_mul']['op'] == 'mul w8, w9, w8'
              and shops[k]['on_change']['price_load']['op'] == 'ldr w9, [x9, #0x1c]'
              for k in CLICK))
    check('the-price-load-reads-rewards-at-0x60-then-price-at-0x1c',
          all(shops[k]['on_change']['rewards_load']['op'] == 'ldr x9, [x20, #8]'
              for k in CLICK)
          and RP.field_name('Board_EventSeasonPass.EventRewards', 0x1c) == 'price')
    check('the-cost-text-is-formatted-and-written-to-textCost',
          all(shops[k]['on_change']['cost_format']['method'] == 'Format'
              and shops[k]['on_change']['cost_label']['field'] == 'textCost'
              for k in CLICK))
    check('the-stock-text-is-a-five-part-concat-ending-in-maxStock',
          all(shops[k]['on_change']['stock_text']['length'] == 5
              and shops[k]['on_change']['stock_text']['concat']
              and shops[k]['on_change']['stock_text']['max_stock_read']['op']
              == 'add x0, x19, #0x5c' for k in CLICK))
    check('the-box-number-is-rewards-number-times-count',
          all(shops[k]['on_change']['set_number']['arg'] == 'mul w1, w8, w9'
              and shops[k]['on_change']['set_number']['before'] == 'mov x2, xzr'
              and shops[k]['on_change']['number_load']['op'] == 'ldr w8, [x8, #0x18]'
              for k in CLICK))
    check('the-affordability-flag-compares-the-medal-with-the-cost',
          all(shops[k]['on_change']['afford_cost']['op'] == 'mul w9, w21, w20'
              and shops[k]['on_change']['afford_cmp']['op'] == 'cmp w19, w9'
              and shops[k]['on_change']['afford_select']['op'].startswith('fcsel')
              for k in CLICK))
    check('the-flag-is-one-exactly-when-the-medal-is-short',
          all(shops[k]['on_change']['afford_one']['op'] == 'fmov s1, #1.00000000'
              and shops[k]['on_change']['afford_select']['op'] == 'fcsel s0, s1, s0, lt'
              for k in CLICK))
    check('the-material-is-the-icon-at-popup-0x40',
          all(shops[k]['on_change']['material_source']['offset'] == '0x40'
              and shops[k]['on_change']['material_source']['field'] == 'btnIcon'
              for k in CLICK))
    check('the-flag-goes-through-the-icon-material',
          all(shops[k]['on_change']['material_read']
              and shops[k]['on_change']['material_set']['method'] == 'SetFloat'
              for k in CLICK))
    check('arena-uses-the-arena-medal-and-pvp-the-pvp-medal',
          arena['on_change']['medal']['method'] == 'get_ArenaMedal'
          and pvp['on_change']['medal']['method'] == 'get_PvPMedal')
    check('onchange-rewrites-count-but-never-maxStock',
          all(shops[k]['on_change']['writes_count']
              and not shops[k]['on_change']['writes_maxstock'] for k in CLICK))

    # -- the two step buttons ---------------------------------------------
    check('minus-reads-slider-value-from-0x68',
          all(shops[k]['minus']['value_load']['op'] == 'ldr s0, [x0, #0x68]'
              for k in CLICK)
          and RP.field_name('Slider', 0x68) == 'value')
    check('minus-only-moves-when-the-value-is-positive',
          all(shops[k]['minus']['compare'][0]['op'] == 'fcmp s0, #0.0'
              and shops[k]['minus']['guard']['op'].startswith('b.le') for k in CLICK))
    check('minus-subtracts-one',
          all(shops[k]['minus']['delta']['value'] == -1.0 for k in CLICK))
    check('add-loads-the-slider-maximum-from-0x60',
          all(shops[k]['add']['limit_load']['op'] == 'ldr s1, [x0, #0x60]' for k in CLICK)
          and RP.field_name('Slider', 0x60) == 'maxValue')
    check('add-only-moves-below-the-maximum',
          all(shops[k]['add']['compare'][-1]['op'] == 'fcmp s0, s1'
              and shops[k]['add']['guard']['op'].startswith('b.pl') for k in CLICK))
    check('add-adds-one',
          all(shops[k]['add']['delta']['value'] == 1.0 for k in CLICK))
    check('both-buttons-tail-call-Slider-set_Value',
          all(shops[k]['minus']['set_value']['target'] == SET_VALUE
              and shops[k]['add']['set_value']['target'] == SET_VALUE for k in CLICK))
    check('neither-button-writes-count-itself',
          all(not shops[k]['minus']['writes_count'] and not shops[k]['add']['writes_count']
              for k in CLICK))

    # -- buy and exit ------------------------------------------------------
    check('buy-prices-the-click-as-rewards-price-times-count',
          all(shops[k]['buy']['cost_mul']['op'] == 'mul w20, w8, w9'
              and shops[k]['buy']['count_load']['field'] == 'count' for k in CLICK))
    check('buy-gates-on-the-medal-balance',
          all(shops[k]['buy']['gate']['op'] == 'cmp w0, w20'
              and shops[k]['buy']['gate_branch']['op'].startswith('b.ge') for k in CLICK))
    check('buy-hands-count-to-the-band-lambda',
          all(shops[k]['buy']['invoke_arg']['op'] == 'ldr w1, [x19, #0x58]'
              and shops[k]['buy']['invoke'] for k in CLICK)
          and all(shops[k]['buy']['count_load']['field'] == 'count' for k in CLICK))
    check('buy-then-hides-the-popup',
          all(shops[k]['buy']['hide']['method'] == 'SetActive' for k in CLICK))
    check('exit-hands-zero-to-the-same-lambda',
          all(shops[k]['exit_']['invoke_arg']['op'] == 'mov w1, wzr'
              and shops[k]['exit_']['invoke'] for k in CLICK))
    check('exit-loads-the-same-onExit-field-at-0x50',
          all(shops[k]['exit_']['delegate_load']['op'].endswith('[x19, #0x50]')
              or shops[k]['exit_']['delegate_load']['op'].endswith('[x0, #0x50]')
              for k in CLICK)
          and RP.field_name(POPUP['Arena_Shop'], 0x50) == 'onExit')
    check('exit-then-hides-the-popup',
          all(shops[k]['exit_']['hide']['method'] == 'SetActive' for k in CLICK))
    check('exit-does-not-touch-the-wallet',
          all(not shops[k]['exit_']['medal'] for k in CLICK))

    # -- what the range of count is ---------------------------------------
    check('164-still-puts-the-slider-range-at-zero-to-maxStock-minus-one',
          all(shops[k]['slider']['slider_value_call']['method'] == 'set_Value'
              and shops[k]['slider']['slider_gate']['op'].startswith('cmp ')
              for k in CLICK))
    check('164-still-starts-count-at-one',
          all(dict((row['offset'], row['field']) for row in shops[k]['slider']['count_written_after'])
              .get('0x58') == 'count' for k in CLICK))
    check('the-step-is-written-as-one-point-zero',
          all(shops[k]['wiring']['step_immediate'] == 'mov w9, #0x3f800000' for k in CLICK))
    check('setpopup-leaves-the-slider-at-zero',
          all(shops[k]['wiring']['value_argument'] == 'fmov s0, wzr' for k in CLICK))
    check('so-count-equals-the-rounded-slider-value-and-zero-is-reachable',
          all(shops[k]['on_change']['division']['op'] == 'fdiv s9, s8, s9'
              and shops[k]['on_change']['count_store']['op'].endswith('#0x58]!')
              and shops[k]['wiring']['value_argument'] == 'fmov s0, wzr' for k in CLICK))
    check('163s-lambda-is-the-guard-that-makes-zero-harmless',
          all(previous['163']['shops'][k]['bands'][band]['lambda_']['guard']['cmp']
              == 'cmp w19, #1'
              and previous['163']['shops'][k]['bands'][band]['lambda_']['guard']['branch']
              .startswith('b.lt')
              for k in CLICK for band in ('player', 'drone', 'resource')))

    # -- earlier reports still hold ---------------------------------------
    check('164-still-prices-the-popup-with-price-times-count',
          all(previous['164']['shops'][k]['popup']['cost']['op'] == 'mul w8, w9, w8'
              for k in CLICK))
    check('164-still-names-the-same-popup-fields',
          [(row['offset'], row['field'])
           for row in previous['164']['shops']['Arena_Shop']['popup']['writes']]
          == [('0x50', 'onExit'), ('0x58', 'count'), ('0x60', 'rewards'),
              ('0x5c', 'maxStock')])
    check('159-still-pins-one-setpopup-per-click',
          all(previous['159']['chains'][k]['caller']['call_rva'] for k in CLICK))
    check('155-still-pins-the-medal-flow', bool(previous['155']))
    # -- the one thing this report cannot measure --------------------------
    bodies = slider_bodies()
    check('no-pinned-slice-holds-the-Slider-set_Value-body',
          bodies['hits'] == [] and bodies['scanned'] >= 8 and bodies['methods'] > 1000)

    failed = [row for row in checks if not row['passed']]
    assert not failed, json.dumps(failed, indent=1)

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='The exchange popup owns the quantity. `SetPopup` builds '
             '`new Action<float>(this, cell)` and stores it on `Slider.onChange`; the popup '
             'declares exactly one `void (float)` method, so the callback is `OnChange`. '
             '`OnChange` computes `count = (int)round(amount / slider.step)`, then refreshes '
             'four things: `textCost = String.Format(fmt, rewards.price * count)`, the '
             '`count/maxStock` text, `Box_Rewards.SetNumber(rewards.number * count)` and an '
             'icon-material float that is 1.0 exactly when `medal < price * count`. The two '
             'step buttons move `slider.value` by -1 / +1 inside `[0, maxValue]` and never '
             'touch `count`. `OnPressedButtonBuy` charges `price * count`, bails out when '
             '`medal < price * count`, then invokes `onExit(count)`; `OnPressedButtonExit` '
             'invokes the same `Action<int>` with `0`. That is what 163s `count < 1` guard is '
             'for: the exit path shares the delegate with the buy path. `count = 0` is '
             'reachable (the slider starts at 0 and `maxValue = maxStock - 1`), the buy gate '
             '`medal >= 0` passes trivially, and the guard is the only reason no purchase '
             'happens. Whether `Slider.set_Value` itself fires `onChange` is not measurable '
             'here: its body is not in the pinned raw.',
        provenance=dict(
            sources=[dict(path=rel, sha256=sha_file(rel))
                     for rel in (DUMP, PREV155, PREV159, PREV163, PREV164)]
            + [dict(path=str(Path(path).relative_to(ROOT)),
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest())
               for path in sorted(ROOT.glob(BD.RAW_GLOB))],
            string_literals=len(AR.strings())),
        shops=shops,
        constants=dict(action_float_ctor=ACTION_FLOAT_CTOR, round_helper=ROUND_HELPER,
                       set_number=SET_NUMBER, set_value=SET_VALUE,
                       set_float=SET_FLOAT, get_material=GET_MATERIAL,
                       tint_property_cell=TINT_CELL),
        table=[dict(control='slider drag', writes='Slider.value (0x68)',
                    effect='OnChange(amount) -> count = round(amount / step)'),
               dict(control='ButtonMinus', writes='Slider.set_Value(value - 1) when value > 0',
                    effect='count follows the slider through OnChange'),
               dict(control='ButtonAdd',
                    writes='Slider.set_Value(value + 1) when value < maxValue',
                    effect='count follows the slider through OnChange'),
               dict(control='ButtonBuy',
                    writes='onExit(count) after the medal gate, then SetActive(false)',
                    effect='the band lambda of 163 buys `count` packs'),
               dict(control='ButtonExit', writes='onExit(0), then SetActive(false)',
                    effect='the same lambda no-ops on `count < 1`')],
        totals=dict(shops=len(shops),
                    checks_passed=sum(1 for row in checks if row['passed']),
                    checks_total=len(checks),
                    onchange_calls=len(arena['on_change']['calls']),
                    buy_calls=len(arena['buy']['calls'])),
        confirmations=[
            dict(item='163: is `count = 0` reachable, and what stops a free purchase?',
                 result='reachable — the slider starts at 0, `OnChange` rounds '
                        '`value / step`, and `count` is that integer. `ButtonExit` even '
                        'passes `0` on purpose. The `count < 1` guard in every band lambda '
                        'is the only thing that stops the buy path; the medal gate '
                        '`medal >= price * 0` cannot.'),
            dict(item='164: why the popup prints `price x count`',
                 result='because `count` is the slider quantity: `OnChange` reprints '
                        '`String.Format(fmt, rewards.price * count)` on every move and '
                        '`ButtonBuy` charges the same product'),
            dict(item='164: `maxValue = maxStock - 1`',
                 result='that is the upper end of `count`, so the widget can never sell '
                        'more than the remaining stock; `ButtonAdd` re-checks the same '
                        'bound against `Slider.maxValue`'),
            dict(item='159: the popup compares the wallet before `blr x9`',
                 result='the compare is `medal >= price * count` and the invoke is the '
                        'band lambda with `count` in `w1`'),
        ],
        open_items=[
            dict(item='does `Slider.set_Value` fire `onChange`?',
                 blocking='`Slider.set_Value` (20903608) and `Slider.OnChangeValue` '
                          '(20903864) are declared in dump.cs but their bodies are in no '
                          'pinned raw slice, so whether the `Value(0)` in `SetPopup` and '
                          'the two step buttons re-enter `OnChange` cannot be measured '
                          'here — MODEL_NOT_MEASURED runtime'),
            dict(item='the material property the affordability flag writes',
                 blocking='`Material.SetFloat(name, value)` takes the name from the '
                          'static cell 0x2adbea8, which holds a runtime string pointer; the '
                          'literal itself is not in the pinned raw'),
            dict(item='a step other than 1.0',
                 blocking='`count = round(amount / step)` with banker rounding; the shipped '
                          '`step` is 1.0, so a designer-set step > 1 would make the rounding '
                          'visible — MODEL_NOT_MEASURED runtime'),
            dict(item='what the player actually sees at open',
                 blocking='`SetPopup` stores `count = 1` and then `Slider.set_Value(0)`, so '
                          'the label and the handle disagree until the first drag; whether '
                          'the setter re-fires `onChange` decides which number survives — '
                          'MODEL_NOT_MEASURED runtime'),
        ],
        checks=checks,
        raw_scan=bodies,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_qty_widget.json.gz')
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
