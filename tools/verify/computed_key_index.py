#!/usr/bin/env python3
"""The index half of the 51 computed store keys: what bounds it, and where it stops.

145 named every key *prefix* (12 of them) but not the number appended to it. This
pass follows the index operand of each `String.Concat(<prefix>, index)` and sorts
the 39 call sites into three shapes:

* **band** — `add wR, wL, #band` with `wL` guarded by `cmp wL, <array length>`.
  `Arena_Shop.ResetShop` and `PVP_Shop.ResetShop` do this three times each, with
  bands **100 / 200 / 300**: the keys are `ARENA_SHOP_ITEM_ID100..`,
  `PVP_SHOP_ITEM_STOCK100..` and so on, one band per shop block.
* **helper parameter** — `String.Concat("SLOT_FREE_CARDS_", slot)`; the index is
  `TimeFreeRewardPack.Key(int slot)`'s argument, i.e. the caller's counter.
* **method parameter** — every shop/quest/video/stock accessor takes an `int`, so
  the key space is whatever the callers pass; the APK's own callers pass quest ids
  read from a field, loop counters, and the literal **999**.

The honest end state: the index half cannot be enumerated from code alone, because
the bounds are runtime list lengths (`[... + 0x18]` on a config object). What *is*
static — the three bands and the 999 sentinel — is pinned here.
"""
import argparse
import collections
import gzip
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import sys  # noqa: E402
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import store_key_callers as base  # noqa: E402

STRINGS = 'reverse-engineering/il2cpp/stringliteral.json'
PREV = 'datas/l2_535b0541_store_key_callers.json.gz'

BANDS = [100, 200, 300]
SHOPS = {'Arena_Shop': 'ARENA', 'PVP_Shop': 'PVP'}
SENTINEL = 999

SITES = 39
RECORDS = 51
BAND_ROWS = 12
SENTINEL_SITES = 20

SKIP_WRITES = {'str', 'strb', 'stp', 'stur', 'cmp', 'tst', 'bl', 'b', 'ret', 'cbz',
               'cbnz', 'tbz', 'tbnz', 'adrp', 'fmov', 'nop', 'b.eq', 'b.ne'}


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def census():
    return base.census(base.collect_statics())


@lru_cache(maxsize=None)
def sites():
    """(method_rva, call_rva) -> the 145 record(s) for that site."""
    out = collections.OrderedDict()
    for record in census():
        if record['kind'] != 'computed':
            continue
        out.setdefault((record['method_rva'], record['call_rva']), []).append(record)
    return out


def writes(ins, index, reg):
    """The last instruction before `index` that writes `reg` (stores excluded)."""
    for k in range(index - 1, max(-1, index - 60), -1):
        mnemonic, operand = ins[k]['mnemonic'], ' '.join(ins[k]['op_str'].split())
        if mnemonic in SKIP_WRITES:
            continue
        if operand.split(',')[0].strip() in (reg, 'x' + reg[1:]):
            return k
    return None


def guard(ins, reg):
    """`cmp reg, wT` + conditional branch, with whatever bounds wT."""
    for k in range(len(ins) - 1):
        mnemonic, operand = ins[k]['mnemonic'], ' '.join(ins[k]['op_str'].split())
        if mnemonic != 'cmp':
            continue
        parts = [part.strip() for part in operand.split(',')]
        if reg not in parts:
            continue
        other = parts[1] if parts[0] == reg else parts[0]
        condition = ins[k + 1]['mnemonic']
        if condition not in ('b.ge', 'b.gt', 'b.le', 'b.lt', 'b.hs', 'b.hi',
                             'b.ls', 'b.lo', 'b.eq', 'b.ne'):
            continue
        bound = writes(ins, k, other)
        row = dict(compare_rva=ins[k]['rva'], condition=condition, bound_register=other)
        if bound is not None:
            row['bound_instruction'] = ins[bound]['mnemonic'] + ' ' + ins[bound]['op_str']
            row['bound_rva'] = ins[bound]['rva']
            text = ' '.join(ins[bound]['op_str'].split())
            hit = re.fullmatch(r'w\d+, \[x\d+, #(0x[0-9a-f]+)\]', text)
            if ins[bound]['mnemonic'] == 'ldr' and hit:
                row['bound_offset'] = int(hit.group(1), 0)
                row['bound_kind'] = ('array-length' if int(hit.group(1), 0) == 0x18
                                     else 'field')
        return row
    return None


def index_operand(method, call_rva):
    """(concat_rva, index_register, bind_rva, ins) for one computed store site."""
    ins = method['instructions']
    position = {x['rva']: i for i, x in enumerate(ins)}
    i = position[call_rva]
    concat = None
    for j in range(i - 1, max(-1, i - 20), -1):
        if ins[j]['mnemonic'] != 'bl':
            continue
        target = ins[j]['op_str'].strip().lstrip('#')
        if re.fullmatch(r'0x[0-9a-f]+', target) and int(target, 0) in base.CONCAT:
            concat = j
            break
    if concat is None:
        return None, None, None, ins
    helper = None
    for j in range(concat - 1, max(-1, concat - 12), -1):
        if ins[j]['mnemonic'] != 'bl':
            continue
        target = ins[j]['op_str'].strip().lstrip('#')
        if re.fullmatch(r'0x[0-9a-f]+', target) and int(target, 0) not in base.CONCAT:
            helper = j
            break
    if helper is None:
        return ins[concat]['rva'], None, None, ins
    # pattern C: the int is a static field — `ldr x0, [klass + 0xB8]`
    for j in range(helper - 1, max(-1, helper - 9), -1):
        static = re.fullmatch(r'x0, \[x\d+, #0xb8\]', ' '.join(ins[j]['op_str'].split()))
        if ins[j]['mnemonic'] == 'ldr' and static:
            return ins[concat]['rva'], 'static', ins[j]['rva'], ins
    # pattern A: `add x0, sp, #X` ... `str wN, [sp, #X]` — a boxed int on the stack
    for j in range(helper - 1, max(-1, helper - 12), -1):
        boxed = re.fullmatch(r'x0, sp, #(0x[0-9a-f]+)', ' '.join(ins[j]['op_str'].split()))
        if ins[j]['mnemonic'] == 'add' and boxed:
            slot = int(boxed.group(1), 0)
            for k in range(helper - 1, -1, -1):
                store = re.fullmatch(r'w(\d+), \[sp(?:, #(0x[0-9a-f]+))?\]',
                                     ' '.join(ins[k]['op_str'].split()))
                if ins[k]['mnemonic'] != 'str' or not store:
                    continue
                offset = int(store.group(2), 0) if store.group(2) else 0
                if offset == slot:
                    return ins[concat]['rva'], 'w' + store.group(1), ins[k]['rva'], ins
            return ins[concat]['rva'], None, None, ins
    # pattern B: `mov w0, wN` / `mov x0, xN` — the int is passed straight in
    for j in range(helper - 1, max(-1, helper - 8), -1):
        moved = re.fullmatch(r'[wx]0, ([wx]\d+)', ' '.join(ins[j]['op_str'].split()))
        if ins[j]['mnemonic'] == 'mov' and moved:
            return ins[concat]['rva'], 'w' + moved.group(1)[1:], ins[j]['rva'], ins
    return ins[concat]['rva'], None, None, ins


def shape(method, call_rva, prefix):
    concat_rva, register, bind_rva, ins = index_operand(method, call_rva)
    row = dict(method_rva=method['rva'], class_name=method['class_name'],
               method=method['signature'].strip(), call_rva=call_rva,
               prefix=prefix, concat_rva=concat_rva)
    if concat_rva is None:
        row.update(kind='helper', reason='the key is built inside the callee; the '
                                        'index is that callee\'s argument')
        return row
    if register == 'static':
        row.update(kind='static-field', bind_rva=bind_rva,
                   reason='the index is a static int field of a class, read through '
                          '`[klass + 0xB8]`')
        return row
    if register is None:
        row.update(kind='other', reason='the index operand is not a boxed int or a '
                                        'moved parameter')
        return row
    row['index_register'] = register
    position = {x['rva']: i for i, x in enumerate(ins)}
    bind = position[bind_rva]
    row['bind_rva'] = bind_rva
    if bind <= 8:
        row.update(kind='parameter', parameter=register,
                   note='the boxed slot holds the incoming argument')
        return row
    defined = writes(ins, bind, register)
    text = ' '.join(ins[defined]['op_str'].split()) if defined is not None else ''
    band = re.fullmatch(r'w\d+, w\d+, #(0x[0-9a-f]+|\d+)', text)
    if defined is not None and ins[defined]['mnemonic'] == 'add' and band:
        base_register = text.split(', ')[1]
        row.update(kind='band', band=int(band.group(1), 0), base_register=base_register,
                   add_rva=ins[defined]['rva'], guard=guard(ins, base_register))
        return row
    if defined is not None and ins[defined]['mnemonic'] == 'ldr' and '#0xb8' in text:
        row.update(kind='static-field', source_instruction='ldr ' + text,
                   source_rva=ins[defined]['rva'])
        return row
    if defined is not None and ins[defined]['mnemonic'] == 'ldr':
        loaded = re.fullmatch(r'[wx]\d+, \[([^]]+)\]', text)
        row.update(kind='field', source_instruction='ldr ' + text,
                   source_rva=ins[defined]['rva'],
                   source='[' + loaded.group(1) + ']' if loaded else None)
        return row
    if defined is not None and ins[defined]['mnemonic'] == 'mov':
        moved = re.fullmatch(r'[wx]\d+, ([wx]\d+)', text)
        if moved:
            if re.fullmatch(r'w[0-7]', moved.group(1)):
                row.update(kind='parameter', parameter=moved.group(1),
                           note='the index arrives as an argument and is moved here')
                return row
            inner = writes(ins, defined, 'w' + moved.group(1)[1:])
            inner_text = (' '.join(ins[inner]['op_str'].split())
                          if inner is not None else '')
            row.update(kind='counter', source_instruction='mov ' + text,
                       source_rva=ins[defined]['rva'],
                       inner_instruction=(ins[inner]['mnemonic'] + ' ' + inner_text)
                       if inner is not None else None,
                       inner_rva=ins[inner]['rva'] if inner is not None else None)
            return row
    row.update(kind='other', source_instruction=(ins[defined]['mnemonic'] + ' ' + text)
               if defined is not None else None,
               source_rva=ins[defined]['rva'] if defined is not None else None)
    return row


def caller_arguments(method_rva):
    """How every `bl <method_rva>` in the 8 raws feeds the first argument."""
    rows = []
    for path in base.raw_paths():
        for method in base.load(path)['methods']:
            ins = method['instructions']
            for i, insn in enumerate(ins):
                if insn['mnemonic'] != 'bl':
                    continue
                target = insn['op_str'].strip().lstrip('#')
                if not re.fullmatch(r'0x[0-9a-f]+', target) or int(target, 0) != method_rva:
                    continue
                defined = writes(ins, i, 'w0')
                text = ' '.join(ins[defined]['op_str'].split()) if defined is not None else ''
                row = dict(raw=path.split('/')[-2], class_name=method['class_name'],
                           caller=method['signature'].strip(), call_rva=insn['rva'])
                literal = re.fullmatch(r'w0, #(0x[0-9a-f]+|\d+)', text)
                if defined is not None and ins[defined]['mnemonic'] == 'mov' and literal:
                    row.update(kind='literal', value=int(literal.group(1), 0),
                               instruction_rva=ins[defined]['rva'])
                elif '#0x18' in text:
                    row.update(kind='length', instruction_rva=ins[defined]['rva'])
                elif re.fullmatch(r'w0, w\d+', text):
                    row.update(kind='register', source=text.split(', ')[1],
                               instruction_rva=ins[defined]['rva'])
                else:
                    row.update(kind='other', instruction=text or None,
                               instruction_rva=ins[defined]['rva'] if defined is not None else None)
                rows.append(row)
    return rows


def build_payload():
    previous = base.load(PREV)
    counts = collections.Counter(record['prefix'] for record in census()
                                 if record['kind'] == 'computed')
    assert sum(counts.values()) == RECORDS, sum(counts.values())
    rows = [shape(base.methods()[method_rva], call_rva, records[0]['prefix'])
            for (method_rva, call_rva), records in sites().items()]
    assert len(rows) == SITES, len(rows)

    band_rows = [row for row in rows if row['kind'] == 'band']
    assert len(band_rows) == BAND_ROWS, len(band_rows)
    assert {row['band'] for row in band_rows} == set(BANDS)
    assert {row['class_name'] for row in band_rows} == set(SHOPS)
    assert all(row['guard'] and row['guard'].get('bound_kind') == 'array-length'
               for row in band_rows), [row for row in band_rows if not row['guard']]

    band_table = collections.OrderedDict()
    for row in band_rows:
        key = (row['class_name'], row['band'], row['prefix'])
        band_table.setdefault(key, []).append(row['call_rva'])
    bands = [dict(shop=shop, namespace=SHOPS[shop], band=band, prefix=prefix,
                  sites=len(calls), call_rvas=calls,
                  guard_rva=next(row['guard']['compare_rva'] for row in band_rows
                                 if row['class_name'] == shop and row['band'] == band),
                  bound_instruction=next(row['guard']['bound_instruction']
                                         for row in band_rows
                                         if row['class_name'] == shop and row['band'] == band))
             for (shop, band, prefix), calls in band_table.items()]
    assert len(bands) == 12, len(bands)

    parameter_methods = collections.OrderedDict()
    for row in rows:
        if row['kind'] != 'parameter':
            continue
        parameter_methods.setdefault(row['method_rva'], dict(
            method_rva=row['method_rva'], class_name=row['class_name'],
            method=row['method'], prefix=row['prefix']))['sites'] = \
            parameter_methods.get(row['method_rva'], {}).get('sites', 0) + 1
    for key, row in parameter_methods.items():
        calls = caller_arguments(key)
        row['callers'] = len(calls)
        row['by_kind'] = dict(collections.Counter(call['kind'] for call in calls))
        row['literal_values'] = sorted({call['value'] for call in calls
                                        if call['kind'] == 'literal'})
        row['sentinel_sites'] = [dict(caller=call['caller'], call_rva=call['call_rva'])
                                 for call in calls
                                 if call['kind'] == 'literal' and call['value'] == SENTINEL]

    sentinels = sum(row['by_kind'].get('literal', 0) and len(row['sentinel_sites']) or 0
                    for row in parameter_methods.values())
    literal_999 = sum(len(row['sentinel_sites']) for row in parameter_methods.values())
    assert literal_999 == SENTINEL_SITES, literal_999

    families = []
    for prefix, count in counts.items():
        members = [row for row in rows if row['prefix'] == prefix]
        kinds = dict(collections.Counter(row['kind'] for row in members))
        families.append(dict(prefix=prefix, records=count, sites=len(members),
                             shapes=kinds,
                             statically_enumerable=bool(kinds.get('band'))))

    duplicates = []
    by_site = collections.OrderedDict()
    for record in census():
        if record['kind'] == 'computed':
            by_site.setdefault((record['method_rva'], record['call_rva']), []).append(record)
    for (method_rva, call_rva), group in by_site.items():
        raws = sorted({record['raw'] for record in group})
        if len(raws) > 1:
            duplicates.append(dict(method_rva=method_rva, call_rva=call_rva,
                                   prefix=group[0]['prefix'], raws=raws))
    assert len(duplicates) == 12, len(duplicates)

    blob = base.load(base.raw_paths()[0])
    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='The index appended to a computed key is a runtime value; what is '
             'static is the band set and the sentinel — stored values stay '
             'MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            xapk_sha256=blob['xapk_sha256'],
            dump_sha256=blob['dump_sha256'],
            libil2cpp_sha256=blob['libil2cpp_sha256'],
            sources=[dict(path=path, sha256=sha_file(path),
                          role='store call sites, index operands and guards')
                     for path in base.raw_paths()]
                    + [dict(path=STRINGS, sha256=sha_file(STRINGS),
                            role='key prefixes and literals'),
                       dict(path=PREV, sha256=sha_file(PREV),
                            role='the 51 computed records and their sites')]),
        census=dict(records=RECORDS, sites=SITES,
                    duplicates=duplicates,
                    by_prefix=[dict(prefix=name, records=count)
                               for name, count in counts.items()],
                    note='from the 145 artifact: 51 computed records collapse to 39 '
                         'sites because key-jump and meta-rewards share one binary'),
        bands=bands,
        band_note='index = band + loop counter; the counter is bounded by an array '
                  'length read from a config object, so the band namespace is static '
                  'and the count is not',
        sites=rows,
        parameters=[dict(**row) for row in parameter_methods.values()],
        sentinel=dict(value=SENTINEL, sites=literal_999,
                      families=sorted({row['prefix'] for row in parameter_methods.values()
                                       if row['sentinel_sites']}),
                      note='quest keys are also written with index 999 — a sentinel '
                           'slot, not a quest id'),
        families=families,
        not_decoded=[
            dict(item='the upper bound of every band and every parameter list',
                 blocking='it is a runtime length: `ldr wT, [xConfig, #0x18]` on a '
                          'config object; the array contents come from serialized '
                          'data, so the count needs the data decode, not the code'),
            dict(item='the value of a parameter index at run time',
                 blocking='callers pass registers (quest id field, loop counters, a '
                          'static counter); only the literal ones are visible '
                          'statically — %d sites pass 999' % literal_999),
            dict(item='stored values',
                 blocking='device state — MODEL_NOT_MEASURED runtime'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_computed_key_index.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          records=payload['census']['records'],
                          sites=payload['census']['sites'],
                          bands=len(payload['bands']),
                          parameters=len(payload['parameters']),
                          sentinel=payload['sentinel']['sites'],
                          families=len(payload['families']))))


if __name__ == '__main__':
    main()
