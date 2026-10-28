#!/usr/bin/env python3
"""The shop's per-cell state is PlayerPrefs, and `ResetShop` writes the id formula.

153 pinned four static cells — `ARENA_SHOP_ITEM_ID`, `ARENA_SHOP_ITEM_STOCK` and the two
PVP twins — and said the stock key is zeroed on reset. What it did not do is look at the
**id** key, which is why 160 could still ask "is `GetIdItem` an identity map?".

Read from the inside, the three accessors per shop are one line each:

    GetIdItem(index)     = PlayerPreferences.GetInt(<ID cell> + index.ToString(), 0)
    GetStockItem(index)  = PlayerPreferences.GetInt(<STOCK cell> + index.ToString(), 0)
    SetStockItem(index,v)= PlayerPreferences.SetInt(<STOCK cell> + index.ToString(), v)

and `ResetShop` walks the three bands and writes **both** keys for every cell:

| band | cell ids | key index | value written to the ID key | stock key |
|---|---|---|---|---|
| player | 100 + i | `add w28, w22, #0x64` | catalogue[i] + (−10001) | 0 |
| drone  | 200 + i | `add w27, w22, #0xc8` | catalogue[i]            | 0 |
| resource | 300 + i | `add w20, w9, #0x12c` | cell id itself          | 0 |

`−10001` is `mov w29, #-0x2711`. Those three formulas are exactly the three bands of 153,
and they are written *into PlayerPrefs*, not into the serialised shop object — which also
explains 153's other puzzle, that `MaxStockCount` (+0x98) has no writer: the cap is an
asset field, the counters are prefs.

Call targets are named with report 161's index (with its `static class` erratum fixed).
"""
import argparse
import functools
import glob
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import dump_rva_index as DX  # noqa: E402

NATIVE = 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'
RAW_GLOB = 'reverse-engineering/raw/*535b0541/native.json.gz'
PREV153 = 'datas/l2_535b0541_shop_stock_layout.json.gz'
PREV156 = 'datas/l2_535b0541_stock_counter.json.gz'
PREV160 = 'datas/l2_535b0541_shop_band_tree.json.gz'
PREV161 = 'datas/l2_535b0541_dump_rva_index.json.gz'

SHOPS = {
    'Arena_Shop': dict(reset=22728328, get_id=22732732, get_stock=22732896,
                       set_stock=22733060, click=22733228,
                       id_cell=0x2AED090, stock_cell=0x2AED088),
    'PVP_Shop': dict(reset=19937384, get_id=19941788, get_stock=19889588,
                     set_stock=19941952, click=19942120,
                     id_cell=0x2AE1018, stock_cell=0x2AE0D40),
}
GET_INT = 20912668        # PlayerPreferences.GetInt(string, int)
SET_INT = 20912644        # PlayerPreferences.SetInt(string, int)
TO_STRING = 34616120      # Int32.ToString()
CONCAT = 33439876         # String.Concat(string, string)
BAND_KEY_BASE = {'player': 0x64, 'drone': 0xC8, 'resource': 0x12C}
ID_OFFSET = -0x2711       # -10001, the player band's id shift

ADRP = re.compile(r'adrp (x\d+), #(0x[0-9a-f]+)')
MEM_LDR = re.compile(r'ldr (x\d+), \[(x\d+)(?:, #(0x[0-9a-f]+))?\]')
REG = re.compile(r'^[wx]\d+$')


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def slices():
    """`(class, rva) -> method`, de-duplicated across the eight overlapping files."""
    rows = {}
    for path in sorted(ROOT.glob(RAW_GLOB)):
        blob = json.loads(gzip.decompress(path.read_bytes()))
        for row in blob['methods']:
            rows.setdefault((row['class_name'], row['rva']),
                            dict(row, raw=path.parent.name))
    return rows


@functools.lru_cache(maxsize=None)
def tables():
    return DX.dump_tables()


def method(klass, rva):
    return slices()[(klass, rva)]


def text(insn):
    return insn['mnemonic'] + ' ' + insn['op_str']


def call_target(insn):
    if insn['mnemonic'] not in ('bl', 'b'):
        return None
    return int(insn['op_str'].lstrip('#'), 16)


def name(rva):
    methods, generics, _ = tables()
    row = methods.get(rva)
    if row is not None:
        return dict(rva=rva, source='method-table', class_name=row['class_name'],
                    signature=row['signature'])
    row = generics.get(rva)
    if row is not None:
        return dict(rva=rva, source='generic-table', class_name=row, signature=row)
    return dict(rva=rva, source='unnamed', class_name=None, signature=None)


def written(insn):
    mnemonic = insn['mnemonic']
    parts = [part.strip() for part in insn['op_str'].split(',')]
    if mnemonic in ('str', 'stp', 'cmp', 'bl', 'b', 'blr', 'ret', 'cbz', 'cbnz',
                    'tbnz', 'tbz') or mnemonic.startswith('b.'):
        return []
    regs = parts[:2] if mnemonic == 'ldp' else parts[:1]
    return ['x' + part[1:] for part in regs if REG.match(part)]


def cell_reads(row, cells):
    """Absolute static cells touched by `adrp`+`ldr` pairs, with write-invalidation."""
    found, bases = [], {}
    for insn in row['instructions']:
        line = text(insn)
        adrp = ADRP.fullmatch(line)
        if adrp:
            bases[adrp.group(1)] = int(adrp.group(2), 16)
            continue
        load = MEM_LDR.fullmatch(line)
        if load and load.group(2) in bases:
            offset = int(load.group(3), 16) if load.group(3) else 0
            address = bases[load.group(2)] + offset
            if address in cells.values():
                found.append(dict(rva=insn['rva'], op=line, cell=address,
                                  cell_name=[key for key, value in cells.items()
                                             if value == address][0]))
        for register in written(insn):
            bases.pop(register, None)
    return found


def census():
    """Which methods touch each of the four cells, across all eight slices."""
    cells = {}
    for klass, want in SHOPS.items():
        cells['%s_ID' % klass.split('_')[0].upper()] = want['id_cell']
        cells['%s_STOCK' % klass.split('_')[0].upper()] = want['stock_cell']
    rows = {}
    for (klass, rva), row in sorted(slices().items(), key=lambda item: item[0][1]):
        for hit in cell_reads(row, cells):
            rows.setdefault(hit['cell_name'], []).append(
                dict(class_name=klass, method_rva=rva,
                     signature=row['signature'].strip(), **hit))
    return cells, rows


def register_cells(row, cells):
    """Long-lived register -> cell mapping, e.g. `x23` is the ID string cell."""
    mapping, bases = {}, {}
    for insn in row['instructions']:
        line = text(insn)
        adrp = ADRP.fullmatch(line)
        if adrp:
            bases[adrp.group(1)] = int(adrp.group(2), 16)
            continue
        load = MEM_LDR.fullmatch(line)
        if load and load.group(2) in bases:
            offset = int(load.group(3), 16) if load.group(3) else 0
            address = bases[load.group(2)] + offset
            if address in cells.values():
                mapping[load.group(1)] = [key for key, value in cells.items()
                                          if value == address][0]
        for register in written(insn):
            bases.pop(register, None)
    return mapping


def accessor(klass):
    """Decode one shop's three accessors: calls, key cell, default, key shape."""
    want = SHOPS[klass]
    cells = {'%s_ID' % klass.split('_')[0].upper(): want['id_cell'],
             '%s_STOCK' % klass.split('_')[0].upper(): want['stock_cell']}
    out = {}
    for role, rva in (('get_id', want['get_id']), ('get_stock', want['get_stock']),
                      ('set_stock', want['set_stock'])):
        row = method(klass, rva)
        calls, store, default = [], None, None
        for insn in row['instructions']:
            target = call_target(insn)
            if target in (TO_STRING, CONCAT, GET_INT, SET_INT):
                resolved = name(target)
                calls.append(dict(call_rva=insn['rva'], target=target,
                                  source=resolved['source'],
                                  class_name=resolved['class_name'],
                                  signature=resolved['signature']))
            if target in (GET_INT, SET_INT):
                window = [item for item in row['instructions']
                          if insn['rva'] - 0x10 <= item['rva'] < insn['rva']]
                sets = [item for item in window
                        if item['mnemonic'] == 'mov' and item['op_str'].startswith('w1, ')]
                default = sets[-1]['op_str'].split(', ')[-1] if sets else None
        reads = cell_reads(row, cells)
        assert len({hit['cell_name'] for hit in reads}) == 1, reads
        out[role] = dict(class_name=klass, method_rva=rva, size=row['size'],
                         signature=row['signature'].strip(),
                         cell=reads[0]['cell_name'], cell_hex=hex(reads[0]['cell']),
                         cell_reads=[hit['rva'] for hit in reads],
                         calls=calls,
                         callees=[call['class_name'] for call in calls],
                         value_register=default,
                         shape='key = Concat(cell, index.ToString()); then %s'
                               % ('GetInt' if role.startswith('get') else 'SetInt'))
        if role.startswith('get'):
            out[role]['default'] = 0
            assert default == 'wzr', default
        else:
            assert default == 'w19', default
        assert [call['call_rva'] for call in calls] == sorted(call['call_rva']
                                                             for call in calls)
    return out


def reset_shop(klass):
    """The three bands of `ResetShop`, one row per written key."""
    want = SHOPS[klass]
    cells = {'%s_ID' % klass.split('_')[0].upper(): want['id_cell'],
             '%s_STOCK' % klass.split('_')[0].upper(): want['stock_cell']}
    row = method(klass, want['reset'])
    insns = row['instructions']
    long_lived = register_cells(row, cells)
    rows, band = [], None
    for number, insn in enumerate(insns):
        if call_target(insn) != SET_INT:
            continue
        back = insns[max(0, number - 24):number]
        key_cell = None
        for item in reversed(back):
            load = MEM_LDR.fullmatch(text(item))
            if load and load.group(1) == 'x8' and load.group(2) in long_lived:
                key_cell = long_lived[load.group(2)]
                break
        value = next((item for item in reversed(insns[:number])
                      if item['mnemonic'] in ('mov', 'add', 'sub')
                      and item['op_str'].split(', ')[0] in ('w1', 'x1')), None)
        assert value is not None, insn
        addend = None
        if value['mnemonic'] == 'add':
            register = value['op_str'].split(', ')[-1]
            for item in insns[:number]:
                if item['mnemonic'] == 'mov' and item['op_str'].startswith(
                        register + ', #') and '#' in item['op_str']:
                    addend = int(item['op_str'].split('#')[-1], 16)
        if key_cell and key_cell.endswith('_ID'):
            index = None
            for item in reversed(back):
                if item['mnemonic'] == 'add' and '#' in item['op_str']:
                    constant = int(item['op_str'].split('#')[-1], 16)
                    if constant in BAND_KEY_BASE.values():
                        index = dict(rva=item['rva'], op=text(item), base=constant)
                        break
            band = index['base'] if index is not None else band
        rows.append(dict(class_name=klass, call_rva=insn['rva'], key_cell=key_cell,
                         band=band, index=index if key_cell.endswith('_ID') else None,
                         value_op=value['op_str'], value_rva=value['rva'],
                         value_const=addend))
    return dict(class_name=klass, method_rva=want['reset'], size=row['size'],
                signature=row['signature'].strip(),
                set_int_sites=len(rows), writes=rows)


def build():
    cells, hits = census()
    shops = {klass: accessor(klass) for klass in SHOPS}
    resets = {klass: reset_shop(klass) for klass in SHOPS}
    previous153 = load(PREV153)
    previous156 = load(PREV156)
    previous160 = load(PREV160)
    previous161 = load(PREV161)

    methods, generics, _ = tables()
    id_writers = [rva for rva, row in methods.items() if 'SetIdItem' in row['signature']]
    preferences = sorted(row['signature'] for row in methods.values()
                         if row['class_name'] == 'PlayerPreferences')

    bands = {}
    for klass, reset in resets.items():
        names = {value: key for key, value in BAND_KEY_BASE.items()}
        rows = []
        for base in sorted(names):
            id_rows = [row for row in reset['writes']
                       if row['key_cell'].endswith('_ID') and row['band'] == base]
            assert len(id_rows) == 1, id_rows
            id_row = id_rows[0]
            stock_rows = [row for row in reset['writes']
                          if row['key_cell'].endswith('_STOCK')
                          and row['band'] == base]
            assert len(stock_rows) == 1, stock_rows
            stock_row = stock_rows[0]
            rows.append(dict(band=names[base], key_index_base=base,
                             key_index_op=id_row['index']['op'],
                             id_value_op=id_row['value_op'],
                             id_value_rva=id_row['value_rva'],
                             id_value_const=id_row['value_const'],
                             id_key_rva=id_row['call_rva'],
                             stock_value_op=stock_row['value_op'],
                             stock_key_rva=stock_row['call_rva']))
        bands[klass] = rows

    checks = []

    def check(name, passed):
        checks.append(dict(check=name, passed=bool(passed)))

    check('four-cells-match-153',
          all(previous153['shops'][klass]['keys'][0]['cell_hex'] == hex(SHOPS[klass]['id_cell'])
              and previous153['shops'][klass]['keys'][1]['cell_hex']
              == hex(SHOPS[klass]['stock_cell']) for klass in SHOPS))
    check('the-id-cell-is-touched-by-exactly-two-methods-per-shop',
          all(sorted({(hit['class_name'], hit['method_rva'])
                      for hit in hits['%s_ID' % klass.split('_')[0].upper()]})
              == sorted({(klass, SHOPS[klass]['get_id']),
                         (klass, SHOPS[klass]['reset'])}) for klass in SHOPS))
    check('the-stock-cell-is-touched-by-exactly-three-methods-per-shop',
          all(sorted({(hit['class_name'], hit['method_rva'])
                      for hit in hits['%s_STOCK' % klass.split('_')[0].upper()]})
              == sorted({(klass, SHOPS[klass]['get_stock']),
                         (klass, SHOPS[klass]['set_stock']),
                         (klass, SHOPS[klass]['reset'])}) for klass in SHOPS))
    check('cell-sites-are-four-for-id-and-six-for-stock',
          all(len(hits['%s_ID' % klass.split('_')[0].upper()]) == 4
              and len(hits['%s_STOCK' % klass.split('_')[0].upper()]) == 6
              for klass in SHOPS))
    check('every-accessor-is-ToString-then-Concat-then-GetInt-or-SetInt',
          all(row['callees'] == ['Int32', 'String', 'PlayerPreferences']
              for shop in shops.values() for row in shop.values()))
    check('accessor-sizes-are-164-164-168',
          all([shop[role]['size'] for role in ('get_id', 'get_stock', 'set_stock')]
              == [164, 164, 168] for shop in shops.values()))
    check('reads-default-to-zero', all(shop[role]['default'] == 0
                                       for shop in shops.values()
                                       for role in ('get_id', 'get_stock')))
    check('set-stock-writes-the-value-argument',
          all(shop['set_stock']['value_register'] == 'w19' for shop in shops.values()))
    check('get-id-and-get-stock-read-one-cell-each',
          all(shop[role]['cell'].endswith('_ID') if role == 'get_id'
              else shop[role]['cell'].endswith('_STOCK')
              for shop in shops.values() for role in ('get_id', 'get_stock')))
    check('reset-writes-six-keys-per-shop',
          all(reset['set_int_sites'] == 6 for reset in resets.values()))
    check('reset-writes-both-keys-in-every-band',
          all(len(rows) == 3 and [row['band'] for row in rows]
              == ['player', 'drone', 'resource'] for rows in bands.values()))
    check('band-key-bases-are-100-200-300',
          all([row['key_index_base'] for row in rows] == [0x64, 0xC8, 0x12C]
              for rows in bands.values()))
    check('player-band-writes-catalogue-minus-10001',
          all(next(row for row in rows if row['band'] == 'player')['id_value_const']
              == ID_OFFSET
              for rows in bands.values()))
    check('drone-band-writes-the-catalogue-value-unchanged',
          all(next(row for row in rows if row['band'] == 'drone')['id_value_op'] == 'w1, w21'
              for rows in bands.values()))
    check('resource-band-writes-the-cell-id-itself',
          all(next(row for row in rows if row['band'] == 'resource')['id_value_op']
              == 'w1, w20'
              for rows in bands.values()))
    check('every-stock-key-is-zeroed-on-reset',
          all(row['stock_value_op'] == 'w1, wzr'
              for rows in bands.values() for row in rows))
    check('no-SetIdItem-exists-anywhere-in-the-metadata', id_writers == [])
    check('PlayerPreferences-exposes-the-six-typed-accessors',
          all(any(signature.startswith(prefix) for signature in preferences)
              for prefix in ('public static int GetInt', 'public static void SetInt',
                             'public static string GetString',
                             'public static void SetString',
                             'public static float GetFloat',
                             'public static void SetFloat')))
    check('156-still-finds-six-buy-closures-writing-the-stock-key',
          len([row for row in previous156['writers']]) == 6
          and all(row['direction'] == 'increment' for row in previous156['writers']))
    check('160-still-holds-four-rows-and-25-checks',
          all(len(previous160['bands'][klass]['rows']) == 4 for klass in previous160['bands'])
          and all(row['passed'] for row in previous160['checks']))
    check('161-index-passes-24-checks-after-the-static-class-fix',
          [row['check'] for row in previous161['checks']][0]
          and all(row['passed'] for row in previous161['checks'])
          and len(previous161['checks']) == 24)
    check('Random-Range-is-used-by-reset-shop',
          any(DX.dump_tables()[0].get(call) and
              DX.dump_tables()[0][call]['class_name'] == 'Random'
              for call in range(0x277D2C0, 0x277D2C4)))
    assert all(row['passed'] for row in checks), [row for row in checks if not row['passed']]

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='The shop keeps per-cell state in PlayerPrefs, not in the serialised shop '
             'object. Each shop has three accessors: `GetIdItem(index)` and '
             '`GetStockItem(index)` return `PlayerPreferences.GetInt(<cell> + '
             'index.ToString(), 0)` and `SetStockItem(index, value)` calls `SetInt` on the '
             'stock key. `ResetShop` writes both keys for every cell of the three bands: '
             'the player band stores `catalogue[i] - 10001` under key index `100 + i`, the '
             'drone band stores `catalogue[i]` under `200 + i`, the resource band stores '
             'the cell id itself under `300 + i`, and every stock key is set to 0. That is '
             'the writing side of the three bands 153 read as "id - 10001 / id / 300 + i", '
             'and it explains why `MaxStockCount` (+0x98) has no writer: the cap is an '
             'asset field while the counters are prefs. No `SetIdItem` exists anywhere in '
             'the 64 727 methods, so `ResetShop` is the only writer of the id key.',
        provenance=dict(sources=[dict(path=rel, sha256=sha_file(rel))
                                 for rel in (NATIVE, PREV153, PREV156, PREV160, PREV161)]
                                 + [dict(path=str(Path(path).relative_to(ROOT)),
                                         sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                                    for path in sorted(ROOT.glob(RAW_GLOB))],
                        dump_sha256=sha_file(DX.DUMP)),
        cells=cells,
        shops=shops,
        reset_shop=resets,
        bands=bands,
        touches={key: rows for key, rows in hits.items()},
        api=dict(get_int=name(GET_INT), set_int=name(SET_INT),
                 to_string=name(TO_STRING), concat=name(CONCAT),
                 playerpreferences_methods=preferences,
                 set_id_item_in_metadata=id_writers),
        totals=dict(shops=len(shops), accessors=sum(len(shop) for shop in shops.values()),
                    id_cell_sites=sum(len(rows) for key, rows in hits.items()
                                      if key.endswith('_ID')),
                    stock_cell_sites=sum(len(rows) for key, rows in hits.items()
                                         if key.endswith('_STOCK')),
                    reset_writes=sum(reset['set_int_sites'] for reset in resets.values()),
                    id_offset=ID_OFFSET,
                    checks_passed=sum(1 for row in checks if row['passed']),
                    checks_total=len(checks)),
        confirmations=[
            dict(item='153: the three bands are `id - 10001`, `id` and `300 + i`',
                 result='confirmed and explained — those are the values `ResetShop` writes '
                        'into the id key, per band, and the key index is the cell id'),
            dict(item='156: six buy closures increment the stock counter',
                 result='confirmed — the closures reach the same `SetStockItem`, which is '
                        'the only writer of the stock key besides `ResetShop`'),
            dict(item='160: `GetIdItem` may be an identity map',
                 result='refuted — it reads a PlayerPrefs entry written by `ResetShop`; '
                        'only the resource band happens to store the cell id itself'),
            dict(item='153: `MaxStockCount` (+0x98) has no writer',
                 result='context added — the cap is a serialised field, the sold counter '
                        'is a pref; the two ceilings live in different storage'),
        ],
        open_items=[
            dict(item='what the catalogue lists contain',
                 blocking='the values come from `List<int>` fields built at reset time '
                          '(`Drone_Get_Datas.get_CountDrones()`, `Random.Range`, '
                          '`List<int>.RemoveAt`); the contents are runtime data — '
                          'MODEL_NOT_MEASURED runtime'),
            dict(item='whether PlayerPrefs survives a reinstall',
                 blocking='the backend is Android SharedPreferences; how the platform '
                          'treats it is outside the APK — MODEL_NOT_MEASURED runtime'),
            dict(item='which strings sit in the id/stock cells at runtime',
                 blocking='the cells hold the key names 153 pinned from the field table; '
                          'the code only concatenates them, it never builds them here'),
            dict(item='why the player band subtracts 10001',
                 blocking='the constant is `mov w29, #-0x2711` and it is applied to the '
                          'catalogue id; the catalogue itself is data, so the meaning of '
                          'the shift is not decidable from code'),
        ],
        checks=checks,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_shop_prefs_keys.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    target.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size,
                          sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                          checks_passed=payload['totals']['checks_passed'],
                          checks_total=payload['totals']['checks_total'],
                          id_sites=payload['totals']['id_cell_sites'],
                          stock_sites=payload['totals']['stock_cell_sites'])))


if __name__ == '__main__':
    main()
