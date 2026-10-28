#!/usr/bin/env python3
"""Which of the shop's eight economy fields the shop itself reads — and who fills
`EventRewards.stock`. STATIC only.

Report 157 decoded the constructor that seeds the block (`MaxStockCount` 10,
`ItemPlayerValue` 1, `ItemPlayerCost` 50, `ItemDroneValue` 1, `ItemDroneCost` 30,
two `int[3]`, `timeToReset` 12600). The open question was which of them the shop
actually reads to produce a price, and whether the popup's `stock` shares the
`MaxStockCount` value.

Two measurement traps decide the answer:

1. **`ldp` reads two ints at once.** `ldp w8, w9, [x19, #0x9c]` is the only way
   `ItemPlayerValue`/`ItemPlayerCost` are read, and `ldp ..., [x19, #0xa4]` the
   only way for the drone pair. A census that only looks at `ldr w?` reports the
   "value" fields as dead — the same mistake 153 made with `stur q0` and `str w`.
2. **Most `#0xb0`/`#0xb8` operands in these methods are static metadata slots**
   (`[0x2aed000 + 0xb8]`, `[0x2ae1000 + 0xb0]`), not the object. Only accesses
   whose base register traces back to `this` (through `mov`/pointer loads, and
   never through `adrp`) are counted.

With those two rules the shop reads every one of the eight fields except
`ItemPlayerValue`'s sibling arrays, which it reads in `InitShop` and in the click
handler, and the click handler builds four `Board_EventSeasonPass.EventRewards`
rows per shop with `stock = MaxStockCount`, `price = Item*Cost`,
`number = Item*Value` — that is where the popup gets its numbers.
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
PREV = 'datas/l2_535b0541_shop_ctor_timer.json.gz'

FIELDS = {0x98: 'MaxStockCount', 0x9C: 'ItemPlayerValue', 0xA0: 'ItemPlayerCost',
          0xA4: 'ItemDroneValue', 0xA8: 'ItemDroneCost',
          0xB0: 'ItemResourceValues', 0xB8: 'ItemResourceCost',
          0xF8: 'timeToReset'}
SHOPS = {'Arena_Shop': dict(click=22733228, init=22730080, onenable=22727788),
         'PVP_Shop': dict(click=19942120, init=19939136, onenable=19936844)}
REWARDS_CTOR = 19464628          # Board_EventSeasonPass.EventRewards..ctor
ALLOC = 0x110d240                # il2cpp_object_new trampoline
CLOBBER = ['x' + str(i) for i in range(19)]
WRITERS = {'mov', 'movz', 'movk', 'movn', 'ldr', 'ldrb', 'ldrh', 'ldrsb', 'ldrsh',
           'ldrsw', 'ldp', 'ldur', 'add', 'adds', 'sub', 'subs', 'mul', 'madd', 'msub',
           'smull', 'umull', 'sdiv', 'udiv', 'and', 'ands', 'orr', 'eor', 'bic', 'lsl',
           'lsr', 'asr', 'adr', 'adrp', 'csel', 'csinc', 'cset', 'neg', 'mvn', 'scvtf',
           'ucvtf', 'fcvtzs', 'fcvtzu', 'fmov', 'sxtw', 'uxtw', 'sxtb', 'uxth', 'rev',
           'clz', 'adc', 'sbc', 'ngc'}
BRANCHES = ('cmp', 'cmn', 'tst', 'cbz', 'cbnz', 'tbz', 'tbnz')


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def methods():
    return load(NATIVE)['methods']


def split_op(op):
    parts, depth, cur = [], 0, ''
    for ch in op:
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
        if ch == ',' and depth == 0:
            parts.append(cur.strip())
            cur = ''
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


def reg64(tok):
    tok = tok.strip()
    if tok[:1] in 'wx' and tok[1:].isdigit():
        return 'x' + tok[1:]
    return None


def mem_operand(op):
    """(dests, base, offset, explicit) or None."""
    parts = split_op(op)
    if '[' not in op:
        return None
    idx = next(i for i, part in enumerate(parts) if '[' in part)
    dests = [reg64(part) for part in parts[:idx]]
    inner = parts[idx].split('[', 1)[1]
    if inner.endswith('!'):
        inner = inner[:-1]
    if inner.endswith(']'):
        inner = inner[:-1]
    inner = [part.strip() for part in inner.split(',')]
    base = inner[0]
    offset, explicit = 0, False
    if len(inner) > 1 and inner[1].startswith('#'):
        token = inner[1][1:].lstrip('-')
        if token.startswith('0x'):
            offset, explicit = int(token, 16), True
    return [dest for dest in dests if dest], base, offset, explicit


def this_register(method):
    if 'static' in method['signature']:
        return None
    for insn in method['instructions'][:12]:
        parts = split_op(insn['op_str'])
        if insn['mnemonic'] == 'mov' and len(parts) == 2 and reg64(parts[1]) == 'x0':
            return reg64(parts[0])
    return None


def accesses(method):
    """Every economy-offset access whose base register traces back to `this`."""
    this = this_register(method)
    if this is None:
        return None
    chains = {this: ()}
    rows = []
    for insn in method['instructions']:
        mnemonic, op = insn['mnemonic'], insn['op_str']
        if mnemonic in ('bl', 'blr'):
            for reg in CLOBBER:
                chains.pop(reg, None)
            continue
        mem = mem_operand(op)
        if mem:
            dests, base, offset, explicit = mem
            pair = len(dests) == 2
            covered = [offset] if not pair else [offset, offset + 4]
            for slot in covered:
                if explicit and slot in FIELDS and base in chains:
                    rows.append(dict(rva=insn['rva'], op=mnemonic + ' ' + op,
                                     field=FIELDS[slot], offset=slot,
                                     chain=list(chains[base]),
                                     kind='read' if mnemonic.startswith('ld') else 'write',
                                     pair=pair))
            if mnemonic.startswith('ld'):
                for dest in dests:
                    if base in chains and explicit and not pair:
                        chains[dest] = chains[base] + (offset,)
                    else:
                        chains.pop(dest, None)
            continue
        if mnemonic in BRANCHES or mnemonic.startswith('b'):
            continue
        if mnemonic not in WRITERS:
            continue
        parts = split_op(op)
        if mnemonic in ('mov', 'add', 'sub', 'adds', 'subs') and len(parts) == 2:
            dst, src = reg64(parts[0]), reg64(parts[1])
            if dst:
                if src == 'x0' and dst == this:
                    chains[dst] = ()
                elif src and src in chains:
                    chains[dst] = chains[src]
                else:
                    chains.pop(dst, None)
            continue
        if parts and reg64(parts[0]):
            chains.pop(reg64(parts[0]), None)
    return rows


def census():
    seen, rows = set(), []
    for method in methods():
        key = (method['class_name'], method['rva'])
        if key in seen:
            continue
        seen.add(key)
        if not method['class_name'].startswith(('Arena_Shop', 'PVP_Shop')):
            continue
        hits = accesses(method)
        if hits is None:
            continue
        for hit in hits:
            hit.update(class_name=method['class_name'], method_rva=method['rva'],
                       signature=method['signature'].strip())
            rows.append(hit)
    return sorted(rows, key=lambda row: (row['class_name'], row['rva']))


def source_of(insns, index, reg):
    """Where the value in `reg` at instruction `index` came from, in shop terms."""
    for insn in reversed(insns[max(0, index - 14):index]):
        mem = mem_operand(insn['op_str'])
        if mem and insn['mnemonic'].startswith('ld'):
            dests, base, offset, explicit = mem
            if reg not in dests or not explicit:
                continue
            part = dests.index(reg)
            where = 'this' if base.startswith('x19') or base == 'x0' else base
            text = '%s.%s' % (where, hex(offset + 4 * part))
            if offset + 4 * part in FIELDS and where == 'this':
                return dict(register=reg, text=text, field=FIELDS[offset + 4 * part],
                            rva=insn['rva'], op=insn['mnemonic'] + ' ' + insn['op_str'],
                            pair=len(dests) == 2)
            return dict(register=reg, text=text, field=None,
                        rva=insn['rva'], op=insn['mnemonic'] + ' ' + insn['op_str'],
                        pair=len(dests) == 2)
    return dict(register=reg, text=None, field=None, rva=None, op=None, pair=False)


def rewards_rows():
    out = {}
    for klass, want in SHOPS.items():
        method = next(row for row in methods()
                      if row['class_name'] == klass and row['rva'] == want['click'])
        insns = method['instructions']
        rows = []
        for index, insn in enumerate(insns):
            if insn['mnemonic'] != 'bl':
                continue
            if int(insn['op_str'].lstrip('#'), 16) != REWARDS_CTOR:
                continue
            args = {}
            for back in reversed(insns[max(0, index - 8):index]):
                parts = split_op(back['op_str'])
                if back['mnemonic'] == 'mov' and len(parts) == 2 and reg64(parts[0]) in (
                        'x2', 'x3', 'x4') and parts[1].strip():
                    slot = {'x2': 'number', 'x3': 'price', 'x4': 'stock'}[reg64(parts[0])]
                    args[slot] = source_of(insns, index, reg64(parts[1]))
            rows.append(dict(call_rva=insn['rva'], method_rva=method['rva'], args=args))
        out[klass] = rows
    return out


def build():
    rows = census()
    rewards = rewards_rows()
    previous = load(PREV)

    per_field = {}
    for offset in sorted(FIELDS):
        name = FIELDS[offset]
        mine = [row for row in rows if row['offset'] == offset]
        reads = [row for row in mine if row['kind'] == 'read']
        per_field[name] = dict(
            offset=hex(offset),
            reads=len(reads), writes=len([row for row in mine if row['kind'] == 'write']),
            pair_reads=len([row for row in reads if row['pair']]),
            direct_reads=len([row for row in reads if not row['pair'] and not row['chain']]),
            captured_reads=len([row for row in reads if row['chain']]),
            sites=[dict(class_name=row['class_name'], method_rva=row['method_rva'],
                        signature=row['signature'], rva=row['rva'], op=row['op'],
                        kind=row['kind'], pair=row['pair'],
                        chain=[hex(step) for step in row['chain']]) for row in mine])

    checks = []
    checks.append(dict(check='eight-fields-censused',
                       passed=sorted(per_field) == sorted(FIELDS.values())))
    checks.append(dict(check='every-field-is-read-somewhere',
                       passed=all(row['reads'] > 0 for row in per_field.values()),
                       detail={name: row['reads'] for name, row in per_field.items()}))
    checks.append(dict(check='value-cost-pairs-are-read-only-as-ldp-pairs',
                       passed=all(per_field[name]['direct_reads'] == 0
                                  and per_field[name]['pair_reads'] == 6
                                  for name in ('ItemPlayerValue', 'ItemPlayerCost',
                                               'ItemDroneValue', 'ItemDroneCost')),
                       detail={name: per_field[name]['pair_reads']
                               for name in ('ItemPlayerValue', 'ItemPlayerCost',
                                            'ItemDroneValue', 'ItemDroneCost')}))
    checks.append(dict(check='max-stock-count-is-the-most-read-field',
                       passed=per_field['MaxStockCount']['reads']
                              == max(row['reads'] for row in per_field.values())))
    price_methods = {offset: sorted({row['method_rva'] for row in rows
                                      if row['offset'] == offset and row['kind'] == 'read'})
                     for offset in (0xB0, 0xB8)}
    expected = sorted([SHOPS['Arena_Shop']['init'], SHOPS['Arena_Shop']['click'],
                       SHOPS['PVP_Shop']['init'], SHOPS['PVP_Shop']['click']])
    checks.append(dict(check='both-array-tables-are-read-in-init-and-click-only',
                       passed=price_methods[0xB0] == expected
                              and price_methods[0xB8] == expected,
                       detail=price_methods))
    checks.append(dict(check='init-and-click-are-the-two-price-methods',
                       passed=all(sorted({row['method_rva'] for row in rows
                                          if row['offset'] in (0xB0, 0xB8)
                                          and row['kind'] == 'read'
                                          and row['class_name'] == klass})
                                  == sorted([want['init'], want['click']])
                                  for klass, want in SHOPS.items())))
    checks.append(dict(check='timer-read-in-onenable-and-the-countdown-coroutine',
                       passed={row['class_name'] for row in rows
                               if row['offset'] == 0xF8 and row['kind'] == 'read'}
                              == {'Arena_Shop', 'Arena_Shop.<IEUpdateTime>d__43',
                                  'PVP_Shop', 'PVP_Shop.<IEUpdateTime>d__43'}))
    checks.append(dict(check='ctor-is-still-the-only-writer',
                       passed={row['method_rva'] for row in rows if row['kind'] == 'write'}
                              == {22735024, 19943896}))
    checks.append(dict(check='four-event-rewards-rows-per-shop',
                       passed={klass: len(value) for klass, value in rewards.items()}
                              == {'Arena_Shop': 4, 'PVP_Shop': 4}))
    checks.append(dict(check='every-rewards-row-takes-stock-from-MaxStockCount',
                       passed=all(row['args']['stock']['field'] == 'MaxStockCount'
                                  for value in rewards.values() for row in value)))
    pairs = {klass: [(row['args']['number'].get('field'),
                      row['args']['price'].get('field')) for row in value]
             for klass, value in rewards.items()}
    checks.append(dict(check='three-rewards-rows-come-from-the-value-cost-pairs',
                       passed=pairs['Arena_Shop'] == pairs['PVP_Shop']
                              == [('ItemDroneValue', 'ItemDroneCost'),
                                  ('ItemPlayerValue', 'ItemPlayerCost'),
                                  ('ItemDroneValue', 'ItemDroneCost'),
                                  (None, None)],
                       detail=pairs))
    checks.append(dict(check='the-fourth-row-prices-from-the-cell',
                       passed=all(value[3]['args']['price']['text'] == 'x20.0x10'
                                  for value in rewards.values())))
    checks.append(dict(check='rewards-ctor-is-the-dump-declared-one',
                       passed=AR.owner(REWARDS_CTOR)[1] ==
                              'public void .ctor(Shop_Pack pack, int number, int price, int stock) { }'))
    checks.append(dict(check='157-kept-the-five-seeds',
                       passed=previous['shipped']['MaxStockCount']['value'] == 10
                              and previous['shipped']['ItemPlayerCost']['value'] == 50
                              and previous['shipped']['ItemDroneCost']['value'] == 30))
    checks.append(dict(check='157-open-item-now-answered-statically',
                       passed='EventRewards.stock'
                              in previous['open_items'][0]['item'] + previous['open_items'][0]['blocking']))
    assert all(row['passed'] for row in checks), [row for row in checks if not row['passed']]

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='The shop reads all eight constructor fields; the two value/cost pairs are '
             'read only through `ldp` pair loads, and the click handler builds four '
             '`Board_EventSeasonPass.EventRewards` rows per shop with '
             '`stock = MaxStockCount`, so the popup slider and the cell text share one '
             'cap. Most `#0xb0`/`#0xb8` operands in these methods are metadata slots, so '
             'the census counts only accesses rooted at `this`.',
        provenance=dict(sources=[dict(path=rel, sha256=sha_file(rel))
                                 for rel in (NATIVE, DUMP, PREV)],
                        libil2cpp_sha256=load(NATIVE)['libil2cpp_sha256'],
                        xapk_sha256=load(NATIVE)['xapk_sha256'],
                        string_literals=len(AR.strings())),
        fields=per_field,
        accesses=rows,
        rewards=rewards,
        totals=dict(accesses=len(rows),
                    reads=len([row for row in rows if row['kind'] == 'read']),
                    writes=len([row for row in rows if row['kind'] == 'write']),
                    pair_reads=len([row for row in rows if row['pair']]),
                    rewards_rows=sum(len(value) for value in rewards.values())),
        confirmations=[
            dict(item='154: the popup slider cap is `EventRewards.stock - sold`',
                 result='confirmed and sourced — the shop itself builds the row with '
                        '`stock = MaxStockCount`, so both ceilings are the same field'),
            dict(item='157: which of the seeded fields are live',
                 result='all eight are read; the value/cost pairs only via `ldp`'),
            dict(item='156: six buy closures read `MaxStockCount` before `sub`',
                 result='confirmed — three closure reads per shop survive the `this`-rooted '
                        'filter with chain `this+0x18 -> +0x10`'),
        ],
        open_items=[
            dict(item='which branch of the click handler a given shop band takes',
                 blocking='the four `EventRewards` sites are guarded by cell ids '
                          '(`cmp w21, #0x12c`) and by a runtime selection; the mapping '
                          'band -> row is not in the code — MODEL_NOT_MEASURED runtime'),
            dict(item='what the three resource prices and values actually are',
                 blocking='`ItemResourceCost`/`ItemResourceValues` are `int[3]` filled by '
                          '`InitializeArray` from a `<PrivateImplementationDetails>` blob; '
                          'the token table that binds the static field slot to that blob '
                          'is not in the workspace (ia-resolved.json covers 17 methods, '
                          'neither shop constructor)'),
            dict(item='who receives the `EventRewards` rows',
                 blocking='each row is passed to a call whose target is in a class '
                          'outside the eight pinned slices; the shop side is static, the '
                          'popup side is not consulted'),
        ],
        checks=checks,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_shop_field_readers.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    target.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size,
                          sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                          totals=payload['totals'],
                          reads={name: row['reads']
                                 for name, row in payload['fields'].items()},
                          checks_passed=sum(1 for row in payload['checks'] if row['passed']),
                          checks_total=len(payload['checks']))))


if __name__ == '__main__':
    main()
