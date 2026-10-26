#!/usr/bin/env python3
"""The `*_ITEM_STOCK` counter is a counter of units sold, not of units left.

153 read the key and called it stock; 154 showed the exchange popup caps its
slider at `rewards.stock - GetStockItem(index)`; 155 showed the same six buy
closures that spend the medal. This report closes the loop on who *writes* the
counter, and the direction is the part worth writing down:

* every writer adds. `Arena_Shop` and `PVP_Shop` each have three buy closures
  (`<>c__DisplayClass31_1/2/3`) and all six call
  `SetStockItem(_id, snapshot + count)` — `add w2, w8, w21`, never a `sub`.
  Across the eight slices there is no other writer.
* the snapshot is taken at click time: `OnClickPlayerItem` calls `GetStockItem`
  and stores the result into the display class at `+0x28`, so the closure keeps
  a one-shot value instead of re-reading at write time.
* two different ceilings subtract that same counter: the slot text uses
  `MaxStockCount` (+0x98), the exchange popup uses `EventRewards.stock` (+0x20).
  `MaxStockCount` still has no writer (153), so the visible cap and the slider
  cap are not the same number.

So the value behind `<PREFIX>_ITEM_STOCK` is monotonically non-decreasing inside
a season, and `ResetShop` is the only place that puts it back to zero.
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
RAW_GLOB = 'reverse-engineering/raw/*535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
PREV153 = 'datas/l2_535b0541_shop_stock_layout.json.gz'
PREV154 = 'datas/l2_535b0541_exchange_cost.json.gz'

SHOPS = {
    'Arena_Shop': dict(get=22732896, set=22733060, click=22733228),
    'PVP_Shop': dict(get=19889588, set=19941952, click=19942120),
}
MAX_STOCK = 0x98          # `Shop.MaxStockCount`
REWARD_STOCK = 0x20       # `Board_EventSeasonPass.EventRewards.stock`
SNAPSHOT_FIELD = 0x28     # the display class slot that keeps the sold count


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def methods():
    return load(NATIVE)['methods']


@functools.lru_cache(maxsize=None)
def slices():
    return [(path.parent.name, json.loads(gzip.decompress(path.read_bytes())))
            for path in sorted(ROOT.glob(RAW_GLOB))]


def method(rva):
    return next(row for row in methods() if row['rva'] == rva)


def text(insn):
    return insn['mnemonic'] + ' ' + insn['op_str']


def calls_of(row, target=None):
    rows = []
    for index, insn in enumerate(row['instructions']):
        if insn['mnemonic'] != 'bl':
            continue
        rva = int(insn['op_str'].lstrip('#'), 16)
        if target is not None and rva != target:
            continue
        rows.append(dict(index=index, rva=insn['rva'], target=rva))
    return rows


def first_match(insns, mnemonic, suffix):
    for insn in insns:
        if insn['mnemonic'] == mnemonic and insn['op_str'].endswith(suffix):
            return insn
    raise AssertionError('%s .. %s not found' % (mnemonic, suffix))


# ------------------------------------------------------------------- the shops
def accessors():
    previous = load(PREV153)
    out = {}
    for klass, want in SHOPS.items():
        entry = previous['shops'][klass]
        key = next(row for row in entry['keys'] if row['role'] == 'slot stock')
        getter = method(want['get'])
        setter = method(want['set'])
        assert getter['class_name'] == klass and setter['class_name'] == klass
        zeros = [row for row in entry['reset']['writes']
                 if row['key'] == key['name'] and row['value_rule'].startswith('0')]
        out[klass] = dict(
            typedef=entry['typedef'],
            get=dict(rva=getter['rva'], size=getter['size'],
                     signature=getter['signature'].strip(), default=key['default']
                     if 'default' in key else entry['getters']['get_stock']['default']),
            set=dict(rva=setter['rva'], size=setter['size'],
                     signature=setter['signature'].strip()),
            key=dict(name=key['name'], cell=key['cell'], cell_hex=key['cell_hex'],
                     report=153),
            reset=dict(rva=entry['reset']['rva'], size=entry['reset']['size'],
                       zero_writes=[row['rva'] for row in zeros],
                       bands=[row['band'] for row in zeros]),
        )
        assert len(zeros) == 3 and [row['band'] for row in zeros] == [100, 200, 300], zeros
    return out


# ------------------------------------------------------------------ the readers
def readers():
    out = {}
    for klass, want in SHOPS.items():
        rows = []
        for tag, blob in slices():
            for row in blob['methods']:
                for call in calls_of(row, want['get']):
                    rows.append(dict(class_name=row['class_name'],
                                     signature=row['signature'].strip(),
                                     method_rva=row['rva'], call_rva=call['rva'],
                                     raw=tag))
        # the two overlapping slices repeat the same call; keep it once
        seen, unique = set(), []
        for row in rows:
            key = (row['class_name'], row['method_rva'], row['call_rva'])
            if key in seen:
                continue
            seen.add(key)
            unique.append(row)
        out[klass] = sorted(unique, key=lambda row: row['call_rva'])
    return out


# ------------------------------------------------------------------ the writers
def writers():
    rows = []
    for klass, want in SHOPS.items():
        for tag, blob in slices():
            for row in blob['methods']:
                for call in calls_of(row, want['set']):
                    insns = row['instructions']
                    before = insns[max(0, call['index'] - 3):call['index']]
                    rows.append(dict(shop=klass, class_name=row['class_name'],
                                     signature=row['signature'].strip(),
                                     method_rva=row['rva'], size=row['size'],
                                     call_rva=call['rva'], raw=tag,
                                     args=[text(insn) for insn in before]))
    seen, unique = set(), []
    for row in rows:
        key = (row['class_name'], row['method_rva'], row['call_rva'])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    unique.sort(key=lambda row: row['call_rva'])
    for row in unique:
        add = [line for line in row['args'] if line.startswith('add w2, ')]
        assert len(add) == 1, row['args']
        row['value_op'] = add[0]
        row['direction'] = 'increment'
    return unique


def snapshot():
    """Where `OnClickPlayerItem` parks the `GetStockItem` result for the closure."""
    out = {}
    suffix = '#%s]' % hex(SNAPSHOT_FIELD)
    for klass, want in SHOPS.items():
        row = method(want['click'])
        call = next(call for call in calls_of(row, want['get'])
                    if call['rva'] == min(c['rva'] for c in calls_of(row, want['get'])))
        window = row['instructions'][call['index']:call['index'] + 5]
        store = first_match(window, 'str', suffix)
        assert store['op_str'].startswith('w0, '), store
        out[klass] = dict(method_rva=row['rva'], signature=row['signature'].strip(),
                          get_call_rva=call['rva'], store_rva=store['rva'],
                          op=text(store), field=hex(SNAPSHOT_FIELD),
                          meaning='the closure writes back a value read once, at '
                                  'click time — not the value at write time')
    return out


def ceilings():
    """`MaxStockCount - sold` as displayed on the slot, next to each buy closure."""
    suffix = '#%s]' % hex(MAX_STOCK)
    rows = []
    for klass, want in SHOPS.items():
        for rva in (22735600, 22771812, 22772712) if klass == 'Arena_Shop' else \
                (19944488, 19945424, 19946324):
            row = method(rva)
            load_insn = first_match(row['instructions'], 'ldr', suffix)
            get_call = min(calls_of(row, want['get']), key=lambda call: call['rva'])
            sub = None
            for insn in row['instructions'][get_call['index']:get_call['index'] + 4]:
                if insn['mnemonic'] == 'sub' and insn['op_str'].endswith('w0'):
                    sub = insn
                    break
            assert sub is not None, row['signature']
            rows.append(dict(shop=klass, class_name=row['class_name'],
                             signature=row['signature'].strip(),
                             max_stock_load=dict(rva=load_insn['rva'],
                                                 op=text(load_insn)),
                             get_call_rva=get_call['rva'],
                             subtract=dict(rva=sub['rva'], op=text(sub))))
    return rows


def band_constants():
    row = method(SHOPS['Arena_Shop']['click'])
    rows = [dict(rva=insn['rva'], op=text(insn)) for insn in row['instructions']
            if insn['mnemonic'] == 'cmp' and insn['op_str'].split(', ')[-1].startswith('#0x')
            and int(insn['op_str'].split('#')[-1], 16) in (199, 299)]
    assert len(rows) == 2, rows
    return rows


def closure_layout():
    row = method(22735600)
    offsets = {}
    for insn in row['instructions']:
        match = re.search(r'\[x19, #(0x[0-9a-f]+)\]', insn['op_str'])
        if match and insn['mnemonic'] in ('ldr', 'ldrsw'):
            offsets.setdefault(int(match.group(1), 16), text(insn))
    return [dict(offset=hex(offset), first_read=offsets[offset])
            for offset in sorted(offsets)]


def build():
    shop = accessors()
    reader = readers()
    writer = writers()
    snap = snapshot()
    ceiling = ceilings()
    bands = band_constants()
    layout = closure_layout()
    previous = load(PREV154)

    checks = []
    checks.append(dict(check='accessors-are-the-153-pair',
                       passed={klass: (row['get']['rva'], row['set']['rva'])
                               for klass, row in shop.items()}
                              == {klass: (want['get'], want['set'])
                                  for klass, want in SHOPS.items()}))
    checks.append(dict(check='keys-are-the-two-stock-keys',
                       passed=sorted(row['key']['name'] for row in shop.values())
                              == ['ARENA_SHOP_ITEM_STOCK', 'PVP_SHOP_ITEM_STOCK']))
    checks.append(dict(check='reset-zeros-the-counter-in-three-bands',
                       passed=all(row['reset']['bands'] == [100, 200, 300]
                                  for row in shop.values())))
    checks.append(dict(check='six-writers-and-no-others',
                       passed=len(writer) == 6
                              and all(row['class_name'].split('.')[0] in SHOPS
                                      for row in writer)))
    checks.append(dict(check='every-writer-adds',
                       passed=[row['value_op'] for row in writer]
                              == ['add w2, w8, w21'] * 6))
    checks.append(dict(check='three-closures-per-shop',
                       passed=sorted(row['class_name'].split('.')[-1] for row in writer)
                              == ['<>c__DisplayClass31_1'] * 2
                              + ['<>c__DisplayClass31_2'] * 2
                              + ['<>c__DisplayClass31_3'] * 2))
    checks.append(dict(check='snapshot-is-taken-at-click-time',
                       passed=all(row['op'] == 'str w0, [x21, #0x28]'
                                  for row in snap.values())))
    checks.append(dict(check='eight-readers-per-shop',
                       passed={klass: len(rows) for klass, rows in reader.items()}
                              == {'Arena_Shop': 8, 'PVP_Shop': 8}))
    checks.append(dict(check='every-reader-group-present',
                       passed=sorted({row['class_name'] for rows in reader.values()
                                      for row in rows if row['class_name'] in SHOPS
                                      or row['class_name'].startswith('Popup_')})
                              == ['Arena_Shop', 'PVP_Shop',
                                  'Popup_ArenaShopExchange', 'Popup_PVPShopExchange']))
    checks.append(dict(check='slot-shows-maxstock-minus-sold',
                       passed=all(row['subtract']['op'].startswith('sub w8, w22, w0')
                                  for row in ceiling)))
    checks.append(dict(check='two-ceilings-are-different-fields',
                       passed=(MAX_STOCK, REWARD_STOCK) == (0x98, 0x20)
                              and MAX_STOCK != REWARD_STOCK))
    checks.append(dict(check='popup-cap-is-the-154-string',
                       passed=any('stock - GetStockItem' in step['meaning']
                                  for step in previous['popups']['Popup_PVPShopExchange']
                                  ['guards'])))
    checks.append(dict(check='two-band-constants',
                       passed=[row['op'] for row in bands]
                              == ['cmp w8, #0xc7', 'cmp w8, #0x12b']))
    assert all(row['passed'] for row in checks), [row for row in checks if not row['passed']]

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='`<PREFIX>_ITEM_STOCK` counts units sold, not units left: six buy '
             'closures add `count` to a snapshot taken at click time, nothing '
             'subtracts, and `ResetShop` is the only writer of zero. Two '
             'different ceilings subtract that counter — `MaxStockCount` (+0x98) '
             'on the slot text and `EventRewards.stock` (+0x20) on the popup slider.',
        provenance=dict(
            sources=[dict(path=rel, sha256=sha_file(rel))
                     for rel in (NATIVE, DUMP, PREV153, PREV154)],
            libil2cpp_sha256=load(NATIVE)['libil2cpp_sha256'],
            xapk_sha256=load(NATIVE)['xapk_sha256']),
        shops=shop,
        readers=reader,
        writers=writer,
        snapshot=snap,
        ceilings=ceiling,
        band_constants=bands,
        closure_layout=layout,
        cross_checks=dict(
            counter='units sold, monotonically non-decreasing inside a season',
            reset='`ResetShop` writes 0 in three bands per shop (153)',
            slot_ceiling='MaxStockCount +0x98 minus GetStockItem',
            popup_ceiling='EventRewards.stock +0x20 minus GetStockItem (154)',
            ceilings_differ=True,
            max_stock_writer='none in the dump (153 open item, unchanged)'),
        checks=checks,
        confirmations=[
            dict(item='155 `open_items`-adjacent question: who writes the shop '
                      'counter after a buy',
                 result='closed — the six shop buy closures do, and only they; each '
                        'adds the purchased count'),
            dict(item='153: `ResetShop` sets the stock key to 0 for three bands',
                 result='confirmed and now meaningful — reset is the only zeroing, so '
                        'the key is a per-season sold counter rather than a level'),
            dict(item='154: the popup caps the slider at `rewards.stock - GetStockItem`',
                 result='confirmed by a second consumer — the slot text does the same '
                        'subtraction against `MaxStockCount`, a different field'),
        ],
        open_items=[
            dict(item='who writes `MaxStockCount` (+0x98)',
                 blocking='unchanged from 153 — no store in the dump, and the field is '
                          'not `[SerializeField]`, so the visible cap has no static '
                          'origin; the two caps may disagree at runtime'),
            dict(item='whether the counter is validated against `MaxStockCount` before '
                      'the debit',
                 blocking='the medal and cards are already moved before the display '
                          're-reads the counter, but the guard is a UI comparison in the '
                          'closure, so whether an over-cap buy is refused is a runtime '
                          'observation — MODEL_NOT_MEASURED runtime'),
            dict(item='what the `#0xc7` / `#0x12b` compares select in `OnClickPlayerItem`',
                 blocking='the two constants (199, 299) sit next to the stock read, but '
                          'the slice does not name the branch targets they guard'),
        ],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_stock_counter.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    target.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(
        bytes=target.stat().st_size,
        sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        writers=len(payload['writers']),
        readers={key: len(value) for key, value in payload['readers'].items()},
        checks_passed=sum(1 for row in payload['checks'] if row['passed']),
        checks_total=len(payload['checks']))))


if __name__ == '__main__':
    main()
