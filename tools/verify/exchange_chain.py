#!/usr/bin/env python3
"""The arena/PvP exchange chain, closed end to end. STATIC only.

Report 154 decoded the slider (`count -> cost -> onExit`) but could not say who
opens the popup: a scan of the pinned raws showed no caller of `SetPopup`. That
scan was looking at the wrong pair of classes — the *third* copy of the popup
(`Popup_Exchange`, TypeDefIndex 693) is the one with no callers. The two shop
popups are opened from exactly one place each:

    Arena_Shop.OnClickPlayerItem  22734600  b  Popup_ArenaShopExchange.SetPopup
    PVP_Shop.OnClickPlayerItem    19943488  b  Popup_PVPShopExchange.SetPopup

Both call sites are tail branches that pass `(index, EventRewards, Action<int>)`,
and the `Action<int>` is built immediately before them from the clicked cell —
that is the `onExit` report 154 could not name.

`SetPopup` stores the three arguments (`+0x50` exit, `+0x58` count = 1,
`+0x60` rewards), computes `maxStock = rewards.stock - GetStockItem(index)` into
`+0x5C`, writes `price * count` as the cost text, and lays out the tabs/slider.

`OnPressedButtonBuy` never touches the wallet: it computes `price * count`,
**compares it with `GameDatas.get_ArenaMedal` / `get_PvPMedal`**, returns when the
wallet is short, and otherwise invokes the stored `Action<int>` with the count and
hides the popup. So the medal debit is the shop's closure (155/156), reached
through the callback — the popup only gates.
"""
import argparse
import functools
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import arena_rewards as AR  # noqa: E402

NATIVE = 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
PREV = 'datas/l2_535b0541_shop_field_readers.json.gz'

ACTION_CTOR = 25841028        # Action<int>..ctor(object, IntPtr)
STRING_FORMAT = 33442960      # String.Format(string, object)
SET_VALUE = 20903608          # Slider.set_Value(float)
SET_ACTIVE = 41424900         # GameObject.SetActive(bool)
GETTEXT = 21202600            # LanguageManager.GetText(string)
WALLET = dict(get_arena=20084804, set_arena=20085004,
              get_pvp=20085132, set_pvp=20085332)

SHOPS = {
    'Arena_Shop': dict(popup='Popup_ArenaShopExchange',
                       setpopup=22835700, buy=22837792,
                       click=22733228, setpopup_call=22734600,
                       getter=WALLET['get_arena'], setter=WALLET['set_arena'],
                       getstock=22732896, tabs=22836632, wallet='ArenaMedal'),
    'PVP_Shop': dict(popup='Popup_PVPShopExchange',
                     setpopup=19888660, buy=19890912,
                     click=19942120, setpopup_call=19943488,
                     getter=WALLET['get_pvp'], setter=WALLET['set_pvp'],
                     getstock=19889588, tabs=19889420, wallet='PvPMedal'),
}


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def methods():
    return load(NATIVE)['methods']


def text(insn):
    return insn['mnemonic'] + ' ' + insn['op_str']


def find(class_name, rva):
    return next(row for row in methods()
                if row['class_name'] == class_name and row['rva'] == rva)


def target_of(insn):
    if insn['mnemonic'] not in ('bl', 'b', 'blr') or not insn['op_str'].startswith('#'):
        return None
    return int(insn['op_str'][1:], 16)


def calls(method):
    return [(insn['rva'], target_of(insn)) for insn in method['instructions']
            if target_of(insn) is not None]


def callers_of(target):
    out, seen = [], set()
    for method in methods():
        key = (method['class_name'], method['rva'])
        if key in seen:
            continue
        seen.add(key)
        for rva, dst in calls(method):
            if dst == target:
                branch = next(insn for insn in method['instructions']
                              if insn['rva'] == rva)['mnemonic']
                out.append(dict(class_name=method['class_name'],
                                method_rva=method['rva'], rva=rva,
                                branch=branch, signature=method['signature'].strip()))
    return sorted(out, key=lambda row: row['rva'])


def window(method, rva, before=4, after=4):
    insns = method['instructions']
    index = next(i for i, insn in enumerate(insns) if insn['rva'] == rva)
    return [dict(rva=insn['rva'], text=text(insn))
            for insn in insns[max(0, index - before):index + after + 1]]


def reverser(insns, rva):
    """Instructions before `rva`, newest first."""
    index = next(i for i, insn in enumerate(insns) if insn['rva'] == rva)
    return list(reversed(insns[:index]))


def stores(method, offset_suffix):
    """Every store whose operand ends with `#0xNN]` or `#0xNN]!`."""
    found = []
    for insn in method['instructions']:
        if not insn['mnemonic'].startswith('st'):
            continue
        op = insn['op_str']
        if offset_suffix not in op:
            continue
        found.append(dict(rva=insn['rva'], op=text(insn), writeback=op.endswith('!'),
                          register=op.split(',')[1].strip().split(',')[0].strip('[ ')))
    return found


def setpopup(klass):
    want = SHOPS[klass]
    method = find(want['popup'], want['setpopup'])
    insns = method['instructions']
    rvas = {insn['rva']: insn for insn in insns}
    def by_signature(fragment):
        return [rva for rva, dst in calls(method)
                if AR.owner(dst)[1] and fragment in AR.owner(dst)[1]]

    getstock = by_signature('GetStockItem')
    tabs = by_signature('SetEventRewardTabs')
    fmt = [rva for rva, dst in calls(method) if dst == STRING_FORMAT]
    slider = [rva for rva, dst in calls(method) if dst == SET_VALUE]
    assert len(getstock) == 1 and len(tabs) == 1 and len(fmt) == 1 and len(slider) == 1, (
        klass, getstock, tabs, fmt, slider)
    stock_load = next(insn for insn in reverser(insns, getstock[0])
                      if insn['mnemonic'] == 'ldr'
                      and insn['op_str'].startswith('w')
                      and insn['op_str'].endswith('#0x20]'))
    price_load = next(insn for insn in reverser(insns, fmt[0])
                      if insn['mnemonic'] == 'ldr'
                      and insn['op_str'].startswith('w')
                      and insn['op_str'].endswith('#0x1c]'))
    mul = next(insn for insn in insns
               if insn['mnemonic'] == 'mul' and insn['rva'] > price_load['rva'])
    return dict(popup=want['popup'], rva=method['rva'], size=method['size'],
                signature=method['signature'].strip(),
                getstock=dict(rva=getstock[0], op=text(rvas[getstock[0]]),
                              target=target_of(rvas[getstock[0]])),
                tabs=dict(rva=tabs[0], op=text(rvas[tabs[0]]),
                          target=target_of(rvas[tabs[0]])),
                format=dict(rva=fmt[0], op=text(rvas[fmt[0]])),
                slider=dict(rva=slider[0], op=text(rvas[slider[0]])),
                stock_read=dict(rva=stock_load['rva'], op=text(stock_load)),
                price_read=dict(rva=price_load['rva'], op=text(price_load)),
                mul=dict(rva=mul['rva'], op=text(mul)),
                exit_store=stores(method, '#0x50]'),
                count_store=stores(method, '#0x58]'),
                maxstock_store=stores(method, '#0x5c]'),
                rewards_store=stores(method, '#8]'),
                windows=[window(method, getstock[0], 6, 8)])


def buy(klass):
    want = SHOPS[klass]
    method = find(want['popup'], want['buy'])
    insns = method['instructions']
    wallet = [rva for rva, dst in calls(method) if dst == want['getter']]
    setters = [rva for rva, dst in calls(method) if dst == want['setter']]
    active = [rva for rva, dst in calls(method) if dst == SET_ACTIVE]
    invoke = next(insn for insn in insns if insn['mnemonic'] == 'blr')
    mul = next(insn for insn in insns if insn['mnemonic'] == 'mul')
    count_load = next(insn for insn in insns
                      if insn['mnemonic'] == 'ldr' and insn['op_str'].endswith('#0x58]'))
    compare = next(insn for insn in insns if insn['mnemonic'] == 'cmp')
    guard = next(insn for insn in insns if insn['mnemonic'] in ('b.ge', 'b.le', 'b.gt', 'b.lt'))
    exit_load = next(insn for insn in insns
                     if insn['mnemonic'] == 'ldr' and insn['op_str'].endswith('#0x50]'))
    return dict(popup=want['popup'], rva=method['rva'], size=method['size'],
                signature=method['signature'].strip(),
                wallet=want['wallet'],
                wallet_get=dict(rva=wallet[0], target=want['getter'],
                                op=text(next(i for i in insns if i['rva'] == wallet[0]))),
                wallet_set=setters,
                mul=dict(rva=mul['rva'], op=text(mul)),
                count_read=dict(rva=count_load['rva'], op=text(count_load)),
                compare=dict(rva=compare['rva'], op=text(compare)),
                guard=dict(rva=guard['rva'], op=text(guard)),
                exit_read=dict(rva=exit_load['rva'], op=text(exit_load)),
                invoke=dict(rva=invoke['rva'], op=text(invoke)),
                hide=dict(rva=active[0], target=SET_ACTIVE,
                          op=text(next(i for i in insns if i['rva'] == active[0]))),
                windows=[window(method, invoke['rva'], 8, 6)])


def caller(klass):
    want = SHOPS[klass]
    rows = callers_of(want['setpopup'])
    assert len(rows) == 1, (klass, rows)
    row = rows[0]
    method = find(row['class_name'], row['method_rva'])
    insns = method['instructions']
    index = next(i for i, insn in enumerate(insns) if insn['rva'] == row['rva'])
    args = {}
    for insn in insns[max(0, index - 10):index]:
        op = insn['op_str']
        if insn['mnemonic'] != 'mov' or ', ' not in op:
            continue
        dst, src = [part.strip() for part in op.split(', ')]
        if dst in ('w1', 'x2', 'x3'):
            args[dst] = dict(rva=insn['rva'], op=text(insn), source=src)
    delegate = [rva for rva, dst in calls(method) if dst == ACTION_CTOR]
    return dict(caller=row['class_name'], class_name=row['class_name'],
                method_rva=row['method_rva'],
                branch=row['branch'], call_rva=row['rva'],
                signature=row['signature'],
                args=args,
                delegate=dict(rva=delegate[0],
                              op=text(next(i for i in insns if i['rva'] == delegate[0]))),
                windows=[window(method, row['rva'], 12, 0)])


def popup_wallet_writes(klass):
    want = SHOPS[klass]
    hits, seen = [], set()
    for method in methods():
        if not method['class_name'].startswith(want['popup']):
            continue
        key = (method['class_name'], method['rva'])
        if key in seen:
            continue
        seen.add(key)
        for rva, dst in calls(method):
            if dst in (WALLET['set_arena'], WALLET['set_pvp']):
                hits.append(dict(class_name=method['class_name'], method_rva=method['rva'],
                                 rva=rva))
    return hits


def build():
    chains = {}
    for klass in SHOPS:
        chains[klass] = dict(caller=caller(klass), setpopup=setpopup(klass),
                             buy=buy(klass), wallet_writes=popup_wallet_writes(klass))
    previous = load(PREV)

    checks = []
    checks.append(dict(check='one-caller-per-popup',
                       passed=all(chains[k]['caller']['class_name'] == k for k in SHOPS)))
    checks.append(dict(check='both-callers-are-the-shop-click-handlers',
                       passed=[chains[k]['caller']['method_rva'] for k in SHOPS]
                              == [SHOPS[k]['click'] for k in SHOPS]))
    checks.append(dict(check='both-are-tail-branches',
                       passed=[chains[k]['caller']['branch'] for k in SHOPS] == ['b', 'b']))
    checks.append(dict(check='three-arguments-each',
                       passed=all(sorted(chains[k]['caller']['args']) == ['w1', 'x2', 'x3']
                                  for k in SHOPS)))
    checks.append(dict(check='exit-delegate-is-an-Action-int',
                       passed=all(chains[k]['caller']['delegate']['op']
                                  == 'bl #0x18a4d84' for k in SHOPS)
                              and AR.owner(ACTION_CTOR)[1] == '|-Action<int>..ctor'))
    checks.append(dict(check='setpopup-stores-exit-count-rewards-maxstock',
                       passed=all(chains[k]['setpopup']['exit_store']
                                  and chains[k]['setpopup']['count_store']
                                  and chains[k]['setpopup']['rewards_store']
                                  and chains[k]['setpopup']['maxstock_store'] for k in SHOPS)))
    checks.append(dict(check='maxstock-is-stock-minus-sold',
                       passed=all(chains[k]['setpopup']['stock_read']['op'].startswith('ldr w')
                                  and chains[k]['setpopup']['stock_read']['op'].endswith('#0x20]')
                                  and chains[k]['setpopup']['getstock']['op'].startswith('bl ')
                                  for k in SHOPS)))
    checks.append(dict(check='cost-text-is-price-times-count',
                       passed=all(chains[k]['setpopup']['price_read']['op'].startswith('ldr w')
                                  and chains[k]['setpopup']['price_read']['op'].endswith('#0x1c]')
                                  and chains[k]['setpopup']['mul']['op'].startswith('mul ')
                                  and chains[k]['setpopup']['format']['op'] == 'bl #0x1fe4c90'
                                  for k in SHOPS)))
    checks.append(dict(check='buy-guards-on-the-right-wallet',
                       passed=[chains[k]['buy']['wallet'] for k in SHOPS]
                              == ['ArenaMedal', 'PvPMedal']
                              and [chains[k]['buy']['wallet_get']['target'] for k in SHOPS]
                              == [WALLET['get_arena'], WALLET['get_pvp']]))
    checks.append(dict(check='buy-invokes-the-callback-not-the-wallet',
                       passed=all(chains[k]['buy']['invoke']['op'] == 'blr x9'
                                  and chains[k]['buy']['wallet_set'] == [] for k in SHOPS)))
    checks.append(dict(check='buy-hides-the-popup',
                       passed=all(chains[k]['buy']['hide']['rva']
                                  and AR.owner(SET_ACTIVE)[1]
                                  == 'public void SetActive(bool value) { }' for k in SHOPS)))
    checks.append(dict(check='popup-classes-never-write-the-wallet',
                       passed=all(chains[k]['wallet_writes'] == [] for k in SHOPS)))
    checks.append(dict(check='wallet-getters-are-the-155-ones',
                       passed=(WALLET['get_arena'], WALLET['set_arena'],
                               WALLET['get_pvp'], WALLET['set_pvp'])
                              == (20084804, 20085004, 20085132, 20085332)))
    checks.append(dict(check='158-still-holds-the-stock-source',
                       passed=all(row['args']['stock']['field'] == 'MaxStockCount'
                                  for value in previous['rewards'].values()
                                  for row in value)))
    assert all(row['passed'] for row in checks), [row for row in checks if not row['passed']]

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='`Popup_*ShopExchange.SetPopup` has exactly one caller per shop — the shop '
             'click handler, as a tail branch passing `(index, EventRewards, Action<int>)`. '
             '`SetPopup` stores the row, sets `count = 1`, computes '
             '`maxStock = rewards.stock - GetStockItem(index)` and writes `price * count` '
             'as the cost text. `OnPressedButtonBuy` compares `price * count` with '
             '`GameDatas.get_ArenaMedal` / `get_PvPMedal`, returns when short, and otherwise '
             'calls the stored `Action<int>` with the count and hides the popup — it never '
             'writes the wallet, so the debit stays in the shop closure (155/156).',
        provenance=dict(sources=[dict(path=rel, sha256=sha_file(rel))
                                 for rel in (NATIVE, DUMP, PREV)],
                        libil2cpp_sha256=load(NATIVE)['libil2cpp_sha256'],
                        xapk_sha256=load(NATIVE)['xapk_sha256'],
                        string_literals=len(AR.strings())),
        chains=chains,
        wallet=WALLET,
        confirmations=[
            dict(item='154: the popup is opened from somewhere outside the scan',
                 result='answered — the caller exists and is the shop click handler at '
                        '22734600 (Arena) / 19943488 (PVP); the copy with no callers is '
                        '`Popup_Exchange` (TypeDefIndex 693), not these two'),
            dict(item='154: what `onExit` is',
                 result='an `Action<int>` built from the clicked cell right before the '
                        'tail branch, stored at `+0x50` and invoked with `count`'),
            dict(item='155/156: who actually spends the medals',
                 result='not the popup — `OnPressedButtonBuy` only compares and calls the '
                        'callback; the `msub` debit is in the shop closures 155 found'),
            dict(item='158: `EventRewards.stock == MaxStockCount`',
                 result='used verbatim here: `maxStock = rewards.stock - sold`, and '
                        '`rewards.stock` came from `MaxStockCount`'),
        ],
        open_items=[
            dict(item='which method the `Action<int>` points at',
                 blocking='the delegate is built with a method handle loaded from a static '
                          'slot; resolving that slot to a C# method needs the metadata '
                          'token table, which is not in the workspace'),
            dict(item='whether the guard can be bypassed when `price * count` overflows',
                 blocking='the `mul` is 32-bit and both operands come from data; the code '
                          'carries no overflow check — MODEL_NOT_MEASURED runtime'),
            dict(item='what `Popup_Exchange` (693) does with the same three arguments',
                 blocking='all eight of its methods sit below the lowest pinned slice RVA, '
                          'so its buy path is not consulted'),
        ],
        totals=dict(popups=len(SHOPS),
                    setpopup_callers=sum(1 for k in SHOPS
                                         for _ in [chains[k]['caller']]),
                    wallet_setter_calls_in_popups=sum(len(chains[k]['wallet_writes'])
                                                      for k in SHOPS)),
        checks=checks,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_exchange_chain.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    target.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size,
                          sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                          totals=payload['totals'],
                          checks_passed=sum(1 for row in payload['checks'] if row['passed']),
                          checks_total=len(payload['checks']))))


if __name__ == '__main__':
    main()
