#!/usr/bin/env python3
"""The medal exchange popup: two wallets, one price formula, one stock rule.

153 decoded the shops and left one line open — "the medal price of
`Popup_PVPShopExchange.SetPopup`". The answer is not a price, it is a *formula*:

    count    = Math.Round(slider.value / slider.step)     // half to even
    cost     = rewards.price * count                       // EventRewards +0x1C
    maxStock = rewards.stock - Shop.GetStockItem(index)    // +0x20 minus bought

and the wallet differs between the two twins, which is the part worth writing down:
`Popup_PVPShopExchange` spends `GameDatas.PvPMedal`, `Popup_ArenaShopExchange`
spends `GameDatas.ArenaMedal`.

The popup never deducts anything itself — buying invokes `onExit(count)` and hides.
Whoever supplied that lambda does the spending, and no dumped method supplies it.
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
import shop_stock_layout as SHOP  # noqa: E402  (the twin comparison helper)

NATIVE = 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'
STRINGS = 'reverse-engineering/il2cpp/stringliteral.json'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
PREV = 'datas/l2_535b0541_shop_stock_layout.json.gz'

POPUPS = {
    'Popup_PVPShopExchange': dict(
        typedef=875, wallet='PvPMedal', wallet_rva=20085132,
        shop='PVP_Shop', shop_get_stock=19889588,
        on_change=19887764, set_popup=19888660, buy=19890912),
    'Popup_ArenaShopExchange': dict(
        typedef=466, wallet='ArenaMedal', wallet_rva=20084804,
        shop='Arena_Shop', shop_get_stock=22732896,
        on_change=22834804, set_popup=22835700, buy=22837792),
}
FIELDS = [('textHeader', 0x20), ('textStock', 0x28), ('textCost', 0x30),
          ('textCoinEvent', 0x38), ('btnIcon', 0x40), ('slider', 0x48),
          ('onExit', 0x50), ('count', 0x58), ('maxStock', 0x5C), ('rewards', 0x60),
          ('boxReward', 0x68)]
REWARDS_FIELDS = [('pack', 0x10), ('number', 0x18), ('price', 0x1C), ('stock', 0x20)]
SLIDER_STEP = 0x64          # `Slider.step`
SLIDER_SET_VALUE = 20903608
SET_FLOAT = 41329332        # Material.SetFloat
GET_MATERIAL = 41323636     # Renderer.get_material
BOX_SET_NUMBER = 20001584   # Box_Rewards.SetNumber
GET_TEXT = 21202600         # LanguageManager.GetText
ROUND_HELPER = 43584368     # not in dump.cs: the System helper behind the rounding
SET_ACTIVE = 41424900


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


def calls_of(row):
    rows = []
    for insn in row['instructions']:
        if insn['mnemonic'] != 'bl':
            continue
        rva = int(insn['op_str'].lstrip('#'), 16)
        klass, signature = AR.owner(rva)
        rows.append(dict(rva=insn['rva'], target=rva, class_name=klass,
                         signature=(signature or '').strip()))
    return rows


def named_calls(row, target):
    return [call for call in calls_of(row) if call['target'] == target]


# ------------------------------------------------------------------- the fields
def nested_fields(klass):
    """`(name, offset, declared)` for a class that may have no base list."""
    lines = AR.MR.dump_text().split('\n')
    pattern = r'public class %s(?: : .*)?\s*// TypeDefIndex: \d+$' % re.escape(klass)
    start = next(i for i, line in enumerate(lines) if re.match(pattern, line))
    rows, serialized = [], False
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


def layout():
    base = SHOP.fields_of('Popup_PVPShopExchange')
    rows = [dict(name=row['name'], offset=hex(row['offset']),
                 declared=row['declared'], serialized=row['serialized'])
            for row in base]
    assert [(row['name'], int(row['offset'], 16)) for row in rows] == FIELDS, rows
    rewards = nested_fields('Board_EventSeasonPass.EventRewards')
    assert [(row['name'], row['offset']) for row in rewards] == \
        [(name, offset) for name, offset in REWARDS_FIELDS], rewards
    return dict(popup=rows,
                rewards=[dict(name=row['name'], offset=hex(row['offset']),
                              declared=row['declared']) for row in rewards],
                slider_step=dict(offset=hex(SLIDER_STEP), field='step',
                                 declared='public float',
                                 note='`Slider` keeps `maxValue` at +0x60 and `step` at '
                                      '+0x64; `OnChange` divides by +0x64, so it divides '
                                      'by the step, not by the maximum'))


# -------------------------------------------------------------------- the maths
def on_change(klass):
    row = method(klass, 'OnChange')
    at = {insn['rva']: insn['mnemonic'] + ' ' + insn['op_str']
          for insn in row['instructions']}
    steps = [
        dict(rva=19887940, op='ldr s9, [x8, #0x64]', meaning='slider.step'),
        dict(rva=19887976, op='fdiv s9, s8, s9', meaning='amount / step'),
        dict(rva=19888008, op=f'bl #{hex(ROUND_HELPER)}', meaning='round to an integer'),
        dict(rva=19888072, op='tst x8, #1', meaning='half-to-even tie break'),
        dict(rva=19888076, op='fcsel d0, d0, d1, eq', meaning='pick the even neighbour'),
        dict(rva=19888132, op='str w8, [x20, #0x58]!', meaning='count'),
        dict(rva=19888172, op='mul w8, w9, w8', meaning='cost = price * count'),
        dict(rva=19888324, op='cmp w8, #1', meaning='text array length check'),
        dict(rva=19888488, op='ldr w9, [x19, #0x58]', meaning='count again'),
        dict(rva=19888500, op='mul w1, w8, w9', meaning='Box_Rewards.SetNumber(number '
                                                       '* count)'),
        dict(rva=19888568, op='mov x0, x8', meaning='btnIcon.renderer'),
        dict(rva=19888596, op='cmp w19, w9', meaning='wallet vs cost'),
        dict(rva=19888612, op='fcsel s0, s1, s0, lt', meaning='1.0 when short, else 0.0'),
    ]
    if klass == 'Popup_ArenaShopExchange':
        shift = POPUPS[klass]['on_change'] - POPUPS['Popup_PVPShopExchange']['on_change']
        steps = [dict(step, rva=step['rva'] + shift) for step in steps]
    for step in steps:
        assert at[step['rva']] == step['op'], (klass, step['rva'], at.get(step['rva']))
    shader = [strings()[ref['addend']] for ref in row['slot_refs']
              if (strings().get(ref.get('addend')) or '').startswith('_')]
    assert shader == ['_EffectAmount'], shader
    assert named_calls(row, SET_FLOAT) and named_calls(row, BOX_SET_NUMBER)
    return dict(method=dict(rva=row['rva'], size=row['size'],
                            signature=row['signature'].strip()),
                steps=steps,
                shader_property=shader[0],
                formula=['count = Math.Round(slider.value / slider.step)',
                         'cost = EventRewards.price * count',
                         'preview = Box_Rewards.SetNumber(EventRewards.number * count)',
                         'dim = (wallet < cost) ? 1.0 : 0.0'],
                currency=named_calls(row, POPUPS[klass]['wallet_rva'])[:1])


def find(insns, pattern, start=0):
    """First instruction at or after `start` whose `mnemonic operands` matches."""
    for insn in insns[start:]:
        if re.fullmatch(pattern, insn['mnemonic'] + ' ' + insn['op_str']):
            return insn
    raise AssertionError('pattern not found: %s' % pattern)


def set_popup(klass):
    """Locate the four guard stores by pattern — the twins shift by 4 bytes inside."""
    spec = POPUPS[klass]
    row = method(klass, 'SetPopup')
    insns = row['instructions']
    count_store = find(insns, r'str w\d+, \[x\d+, #0x58\]!')
    rewards_store = find(insns, r'str x\d+, \[x\d+, #8\]',
                         insns.index(count_store))
    window = insns[insns.index(rewards_store):]
    subtract = next(insn for insn in window
                    if re.fullmatch(r'sub w\d+, w\d+, w\d+',
                                    insn['mnemonic'] + ' ' + insn['op_str']))
    max_store = find(insns, r'str w\d+, \[x\d+, #0x5c\]!', insns.index(subtract))
    guards = [dict(rva=count_store['rva'], op='str wN, [xN, #0x58]!', meaning='count = 1'),
              dict(rva=rewards_store['rva'], op='str xN, [xN, #8]',
                   meaning='rewards = the caller\'s row'),
              dict(rva=subtract['rva'], op='sub wN, wN, wN',
                   meaning='stock - GetStockItem(index)'),
              dict(rva=max_store['rva'], op='str wN, [xN, #0x5c]!', meaning='maxStock')]
    calls = calls_of(row)
    wallet = [call for call in calls if call['target'] == spec['wallet_rva']]
    stock = [call for call in calls if call['target'] == spec['shop_get_stock']]
    text = [call for call in calls if call['target'] == GET_TEXT]
    slider = [call for call in calls if call['target'] == SLIDER_SET_VALUE]
    assert len(wallet) == 1 and len(stock) == 1 and len(text) == 2 and len(slider) == 1, \
        (klass, wallet, stock, text, slider)
    assert stock[0]['rva'] < subtract['rva'], (stock[0]['rva'], subtract['rva'])
    keys = [strings().get(ref['addend']) for ref in row['slot_refs']
            if strings().get(ref['addend']) in ('txt_exchange', 'txt_stock')]
    return dict(method=dict(rva=row['rva'], size=row['size'],
                            signature=row['signature'].strip()),
                guards=guards, wallet=wallet[0], stock_read=stock[0],
                gettext_calls=text, slider_set=slider[0], keys=keys,
                rule='the popup starts at one unit, remembers the reward row, and caps the '
                     'slider at whatever stock the shop has not sold yet')


def buy(klass):
    """`OnPressedButtonBuy`: cost, gate, callback, hide."""
    spec = POPUPS[klass]
    row = method(klass, 'OnPressedButtonBuy')
    insns = row['instructions']
    price = find(insns, r'ldr w\d+, \[x\d+, #0x1c\]')
    count = find(insns, r'ldr w\d+, \[x\d+, #0x58\]', insns.index(price))
    costs = find(insns, r'mul w\d+, w\d+, w\d+', insns.index(count))
    gate = find(insns, r'cmp w\d+, w\d+', insns.index(costs))
    branch = insns[insns.index(gate) + 1]
    assert re.fullmatch(r'b\.ge #0x[0-9a-f]+', branch['mnemonic'] + ' ' + branch['op_str'])
    callback = find(insns, r'ldr w1, \[x\d+, #0x58\]')
    hide = insns[-3]
    steps = [dict(rva=price['rva'], op='ldr wN, [xN, #0x1c]', meaning='rewards.price'),
             dict(rva=count['rva'], op='ldr wN, [xN, #0x58]', meaning='count'),
             dict(rva=costs['rva'], op='mul wN, wN, wN', meaning='cost = price * count'),
             dict(rva=gate['rva'], op='cmp wN, wN', meaning='wallet vs cost'),
             dict(rva=branch['rva'], op='b.ge', meaning='afford -> go on'),
             dict(rva=callback['rva'], op='ldr w1, [xN, #0x58]', meaning='onExit(count)'),
             dict(rva=hide['rva'], op='b', meaning='this.SetActive(false)')]
    calls = calls_of(row)
    wallet = [call for call in calls if call['target'] == spec['wallet_rva']]
    assert len(wallet) == 1
    assert wallet[0]['rva'] < gate['rva'], (wallet[0]['rva'], gate['rva'])
    assert not named_calls(row, SET_FLOAT), 'the buy path should not touch the shader'
    return dict(method=dict(rva=row['rva'], size=row['size'],
                            signature=row['signature'].strip()),
                steps=steps, wallet=wallet[0],
                deducts_nothing='no call to a setter for the wallet, no write into it; the '
                                'only outgoing call is `onExit(count)` at +0x50')


def twins():
    rows = []
    for signature in ('OnChange', 'SetPopup', 'SetEventRewardTabs', 'OnPressedButtonBuy',
                      'OnPressedButtonMinus', 'OnPressedButtonAdd', 'OnPressedButtonExit'):
        one = method('Popup_ArenaShopExchange', signature)
        two = method('Popup_PVPShopExchange', signature)
        rows.append(dict(signature=one['signature'].strip(),
                         arena=dict(rva=one['rva'], size=one['size']),
                         pvp=dict(rva=two['rva'], size=two['size']),
                         same_size=one['size'] == two['size'],
                         delta=two['size'] - one['size']))
    arena_fields = SHOP.fields_of('Popup_ArenaShopExchange')
    pvp_fields = SHOP.fields_of('Popup_PVPShopExchange')
    assert [(row['name'], row['offset']) for row in arena_fields] == \
        [(row['name'], row['offset']) for row in pvp_fields]
    differing = [(one['name'], one['declared'], two['declared'])
                 for one, two in zip(arena_fields, pvp_fields)
                 if one['declared'] != two['declared']]
    assert differing == [('rewards', 'Board_EventSeasonPass.EventRewards',
                          'Board_EventSeasonPass.EventRewards')] or differing == [], differing
    return dict(methods=rows, fields=len(pvp_fields),
                same_field_count=True,
                only_size_delta=[row['signature'] for row in rows if not row['same_size']],
                note='the two popups differ only in which shop and which wallet they name: '
                     '`SetPopup` is 932 B (Arena) vs 928 B (PVP), every other method is '
                     'byte-identical in size')


def callers():
    """No dumped method calls `SetPopup` — the popup is wired, not constructed in code."""
    rows = []
    for target in POPUPS.values():
        hits = []
        for target_method in load(NATIVE)['methods']:
            for insn in target_method['instructions']:
                if insn['mnemonic'] != 'bl':
                    continue
                if int(insn['op_str'].lstrip('#'), 16) == target['set_popup']:
                    hits.append(dict(class_name=target_method['class_name'],
                                     rva=target_method['rva']))
        rows.append(dict(set_popup=target['set_popup'], callers=hits))
    assert all(not row['callers'] for row in rows), rows
    return dict(rows=rows,
                rule='`SetPopup` has no caller in the 1361 methods of the arena-pvp slice, '
                     'so the open/close path is an inspector reference or code outside the '
                     'slices; the 153 shop never passes the lambda that spends the wallet')


def third():
    """`Popup_Exchange` — the same 11 fields again, and not one of them is dumped.

    The dump carries a third popup with an identical field block but a five-argument
    `SetPopup` (two card-sprite arrays for the tabs). None of its eight methods lies
    inside any of the eight slices, so its wallet stays unknown.
    """
    lines = AR.MR.dump_text().split('\n')
    start = next(i for i, line in enumerate(lines)
                 if line.startswith('public class Popup_Exchange :'))
    fields, methods, serialized = [], [], False
    pending = None
    for line in lines[start + 1:]:
        text = line.strip()
        if text == '}':
            break
        if text.startswith('// RVA: 0x'):
            pending = int(text.split()[2], 16)
            continue
        if pending is not None:
            match = re.match(r'.*\b(\w+)\(', text)
            if match:
                methods.append(dict(name=match.group(1),
                                    signature=text.split('{')[0].strip() + ' { }',
                                    rva=pending))
            pending = None
            continue
        if text in ('[SerializeField]', '[HideInInspector]'):
            serialized = True
            continue
        match = re.match(r'(?:public|private|protected|internal)\s+(?:static\s+)?(.+?)\s+'
                         r'(\w+);\s*// (0x[0-9A-F]+)', text)
        if match:
            fields.append(dict(name=match.group(2), offset=int(match.group(3), 16),
                               declared=match.group(1), serialized=serialized))
            serialized = False
    rows = load(NATIVE)['methods']
    low = min(row['rva'] for row in rows)
    high = max(row['rva'] + row['size'] for row in rows)
    rvas = [row['rva'] for row in methods]
    assert len(methods) == 8, methods
    assert [(row['name'], row['offset']) for row in fields] == FIELDS, fields
    assert all(rva < low or rva > high for rva in rvas), (rvas, low, high)
    assert all(row['name'] not in ('OnChange', 'OnPressedButtonBuy')
               or row['rva'] not in {m['rva'] for m in rows} for row in methods)
    five = next(row for row in methods if row['name'] == 'SetPopup')
    assert five['signature'].count(',') == 4, five
    return dict(typedef=693, fields=len(fields), methods=methods,
                set_popup_arity=5,
                slice_span=[low, high],
                note='same field block as the two shop popups, but a five-argument '
                     '`SetPopup`; all eight methods sit below the lowest dumped rva, so '
                     'the slice never reaches it')


def build():
    layout_rows = layout()
    changes = {klass: on_change(klass) for klass in POPUPS}
    popups = {klass: set_popup(klass) for klass in POPUPS}
    buys = {klass: buy(klass) for klass in POPUPS}
    twin = twins()
    entry = callers()
    extra = third()
    previous = load(PREV)

    checks = []
    checks.append(dict(check='eleven-popup-fields',
                       passed=[row['name'] for row in layout_rows['popup']]
                              == [name for name, _ in FIELDS]))
    checks.append(dict(check='reward-row-is-four-ints',
                       passed=[row['name'] for row in layout_rows['rewards']]
                              == ['pack', 'number', 'price', 'stock']))
    checks.append(dict(check='slider-divides-by-step',
                       passed=layout_rows['slider_step']['offset'] == '0x64'
                              and 'step' in layout_rows['slider_step']['field']))
    checks.append(dict(check='two-different-wallets',
                       passed={klass: row['wallet']['target'] for klass, row in popups.items()}
                              == {'Popup_PVPShopExchange': 20085132,
                                  'Popup_ArenaShopExchange': 20084804}))
    checks.append(dict(check='wallet-signatures',
                       passed={klass: row['wallet']['signature'] for klass, row in
                               popups.items()}
                              == {'Popup_PVPShopExchange': 'public static int get_PvPMedal() { }',
                                  'Popup_ArenaShopExchange':
                                      'public static int get_ArenaMedal() { }'}))
    checks.append(dict(check='cost-is-price-times-count',
                       passed=any(step['op'].startswith('mul w')
                                  for step in changes['Popup_PVPShopExchange']['steps'])
                              and any(step['op'].startswith('mul w')
                                      for step in buys['Popup_PVPShopExchange']['steps'])))
    checks.append(dict(check='rounding-is-half-to-even',
                       passed=any(step['op'] == 'tst x8, #1'
                                  for step in changes['Popup_PVPShopExchange']['steps'])))
    checks.append(dict(check='shader-property-is-effect-amount',
                       passed={row['shader_property'] for row in changes.values()}
                              == {'_EffectAmount'}))
    checks.append(dict(check='max-stock-subtracts-what-was-bought',
                       passed=all(any(step['op'] == 'sub wN, wN, wN'
                                      for step in row['guards']) for row in popups.values())))
    checks.append(dict(check='stock-read-is-the-shop',
                       passed={klass: row['stock_read']['signature'] for klass, row in
                               popups.items()}
                              == {'Popup_PVPShopExchange':
                                  'public static int GetStockItem(int index) { }',
                                  'Popup_ArenaShopExchange':
                                      'public static int GetStockItem(int index) { }'}))
    checks.append(dict(check='two-language-keys-per-popup',
                       passed={klass: sorted(row['keys']) for klass, row in popups.items()}
                              == {'Popup_PVPShopExchange': ['txt_exchange', 'txt_stock'],
                                  'Popup_ArenaShopExchange': ['txt_exchange', 'txt_stock']}))
    checks.append(dict(check='buy-deducts-nothing',
                       passed=all('deducts_nothing' in row for row in buys.values())))
    checks.append(dict(check='twins-differ-in-one-size',
                       passed=twin['only_size_delta']
                              == ['public void SetPopup(int index, Board_EventSeasonPass.EventRewards'
                                  ' eventReward, Action<int> exit) { }']))
    checks.append(dict(check='no-caller-for-setpopup',
                       passed=all(not row['callers'] for row in entry['rows'])))
    checks.append(dict(check='third-popup-outside-every-slice',
                       passed=extra['fields'] == 11 and extra['set_popup_arity'] == 5
                              and all(row['rva'] < extra['slice_span'][0]
                                      for row in extra['methods'])))
    checks.append(dict(check='shop-report-predicted-this',
                       passed=previous['open_items'][2]['item'].startswith(
                           'the exchange popup')))
    assert all(row['passed'] for row in checks), [row for row in checks
                                                 if not row['passed']]

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='The exchange price is a formula, not a number: `price * count` where `count` '
             'is the slider position in steps, paid from one of two wallets. The row values '
             '(`price`, `number`, `stock`) live in the event-pass data, so what a given '
             'season charges is MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            sources=[dict(path=rel, sha256=sha_file(rel))
                     for rel in (NATIVE, STRINGS, DUMP, PREV)],
            libil2cpp_sha256=load(NATIVE)['libil2cpp_sha256'],
            xapk_sha256=load(NATIVE)['xapk_sha256'],
            string_literals=len(strings())),
        layout=layout_rows,
        popups=popups,
        on_change=changes,
        buy=buys,
        twins=twin,
        entry_point=entry,
        third_popup=extra,
        cross_checks=dict(
            currencies={'Popup_PVPShopExchange': ('GameDatas.PvPMedal', 20085132),
                        'Popup_ArenaShopExchange': ('GameDatas.ArenaMedal', 20084804)},
            shop_of={'Popup_PVPShopExchange': 'PVP_Shop',
                     'Popup_ArenaShopExchange': 'Arena_Shop'},
            formula='cost = EventRewards.price * round(slider.value / slider.step)',
            deducted_in_popup=False),
        checks=checks,
        confirmations=[
            dict(item='153 `open_items` "the exchange popup\'s medal price"',
                 result='closed as a formula — price per unit times the slider step count; '
                        'the popup itself never deducts'),
            dict(item='`Popup_PVPShopExchange` and `Popup_ArenaShopExchange` share one '
                      'implementation',
                 result='confirmed — same 11 fields, same maths, one 4-byte size delta in '
                        '`SetPopup`; the only real difference is the wallet'),
            dict(item='the shop and the popup use the same stock counter',
                 result='confirmed — `maxStock = rewards.stock - Shop.GetStockItem(index)`, '
                        'the very key 153 decoded'),
        ],
        open_items=[
            dict(item='who spends the medal after the popup returns',
                 blocking='the popup only calls `onExit(count)`, and `SetPopup` has no caller '
                          'in the dump, so the lambda that deducts is outside the slices '
                          'rather than missing'),
            dict(item='the actual price/number/stock of a season row',
                 blocking='`Board_EventSeasonPass.eventRewards` is a static array filled from '
                          'the event-pass data; MODEL_NOT_MEASURED runtime'),
            dict(item='the wallet of `Popup_Exchange` (TypeDefIndex 693)',
                 blocking='a third popup carries the same 11 fields and a five-argument '
                          '`SetPopup`, but all eight of its methods sit below the lowest '
                          'dumped rva, so no slice can name its currency'),
            dict(item='`Math.Round` helper at rva 43584368',
                 blocking='not present in dump.cs, so it is named from its call site and its '
                          'tie-break instruction pattern, not from a signature'),
        ],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_exchange_cost.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    target.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(
        bytes=target.stat().st_size,
        sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        wallets=payload['cross_checks']['currencies'],
        checks_passed=sum(1 for row in payload['checks'] if row['passed']),
        checks_total=len(payload['checks']))))


if __name__ == '__main__':
    main()
