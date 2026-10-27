#!/usr/bin/env python3
"""Report 178: the key counters are *static fields*, and 176 read the second hop wrong.

176 answered the question "who else stores to 0x50/0x54/0x58" with six writers and a
premise: *"instance fields `+0x50/+0x54/+0x58` on `[object behind slot 0x2adb000+0xaf8] +
0xb8`; `KeyCount0/1/2` are properties, not statics"*. The six sites are right; the premise
is inverted, and `dump.cs` says so in one line:

    public class GameDatas : MonoBehaviour            // TypeDefIndex: 249
        private static int keyCount0; // 0x50
        private static int keyCount1; // 0x54
        private static int keyCount2; // 0x58

`+0xb8` is not an object field. It is `Il2CppClass::static_fields`, and the accessor is the
canonical IL2CPP static sequence:

    adrp  x20, #0x2adb000            ; page of the TypeInfo cell
    ldr   x20, [x20, #0xaf8]         ; x20 = &GameDatas_c   (TypeInfo slot)
    ldr   x8,  [x20]                 ; x8  = GameDatas_c*
    ldr   w9,  [x8,  #0xe0]          ; cctor gate
    cbnz  w9,  +                     ;
    mov   x0,  x8                    ;
    bl    #0x110d12c                 ; init class
    ldr   x9,  [x8,  #0xb8]          ; static_fields  <-- the hop 176 called "the object"
    str   w19, [x9,  #0x50]          ; keyCount0

This is the same trap as 172, one hop deeper: `+0xb8` is shape-identical to an object field,
so a base-register trace that stops at the first `ldr` files a static write as an instance
write. The gate classifies every store to those three offsets in the 1788-method corpus by
tracing the base register back through `+0xb8` to the TypeInfo cell.

Answer to item 32 ("a direct static store outside these classes"): there is none. The six
GameDatas accessors are the only stores into GameDatas' static block at 0x50/0x54/0x58;
the other ten static-block stores hit *other classes'* blocks at the same offsets, which is
what makes an offset-only scan look like it found something.
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

ARTIFACT = 'datas/l2_535b0541_counter_static_writers.json.gz'
SELF = 'l2_535b0541_counter_static_writers'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
PREV = 'datas/l2_535b0541_keycount_writers.json.gz'

WANT = (0x50, 0x54, 0x58)
STATIC_HOP = 0xb8
CCTOR_GATE = 0xe0
CLASS_INIT = 0x110d12c
TYPEINFO_CELL = ('0x2adb000', '0xaf8')
FIELDS = {0x50: 'keyCount0', 0x54: 'keyCount1', 0x58: 'keyCount2'}
ACCESSORS = {0x50: ('KeyCount0', 20070740, 20070940),
             0x54: ('KeyCount1', 20071068, 20071268),
             0x58: ('KeyCount2', 20071396, 20071596)}

MEM = re.compile(r'\[x(\d+)(?:, #(0x[0-9a-f]+|\d+))?\]')
IMM = re.compile(r'#(0x[0-9a-f]+|\d+)')
STORES = ('str', 'strb', 'strh', 'stur', 'stp')
DESTS = ('adrp', 'mov', 'ldr', 'ldrb', 'ldrh', 'ldrsw', 'ldur', 'add', 'sub',
         'movz', 'movk', 'orr', 'and', 'csel', 'sxtw', 'uxtw', 'mul', 'lsl')
TRACK = ('adrp', 'mov', 'ldr', 'ldrb', 'ldrh', 'ldrsw', 'ldur', 'add', 'sub',
         'movz', 'movk', 'orr', 'and', 'csel', 'sxtw', 'uxtw', 'mul', 'lsl', 'ldp')


def num(text):
    return int(text, 16) if text.startswith('0x') else int(text)


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def corpus():
    return BD.slices()


def definitions(instructions):
    """register -> [(index, mnemonic, op_str, rva)] in program order.

    A flat "last writer" map is enough for one hop and wrong for three: after
    `ldr x20,[x20,#0xaf8]` the register is both the source and the destination, so the
    history has to be kept per register, not per instruction.
    """
    out = {}
    for index, insn in enumerate(instructions):
        op = insn.get('op_str') or ''
        if insn['mnemonic'] not in TRACK:
            continue
        first = op.split(',')[0].strip()
        if re.fullmatch(r'x\d+|w\d+', first):
            out.setdefault(first[1:], []).append(
                (index, insn['mnemonic'], op, insn['rva']))
    return out


def at(history, reg, index):
    """The instruction that last wrote `reg` before `index`."""
    rows = history.get(reg) or []
    best = None
    for row in rows:
        if row[0] < index:
            best = row
        else:
            break
    return best


def trace(history, index, reg, depth=0):
    """Follow `#0xb8` (static_fields) down to the TypeInfo cell, at most three hops."""
    chain = dict(static_from=None, klass_from=None, cell=None, hops=0)
    src = at(history, reg, index)
    if not src or depth > 3:
        return dict(chain, kind='unknown')
    _, mnemonic, op, _ = src
    if mnemonic == 'adrp':
        return dict(chain, kind='cell')
    match = re.search(r'\[x(\d+), #0x([0-9a-f]+)\]', op)
    if not (mnemonic in ('ldr', 'ldur', 'ldrsw') and match
            and int(match.group(2), 16) == STATIC_HOP):
        return dict(chain, kind='instance')
    chain['static_from'] = op
    chain['hops'] = 1
    inner = at(history, match.group(1), src[0])
    if inner:
        chain['klass_from'] = inner[2]
        chain['hops'] = 2
        # a `ldr xK, [xT, #cell]` where xT came from `adrp` is the TypeInfo slot itself
        deref = re.search(r'\[x(\d+)(?:, #0x([0-9a-f]+))?\]', inner[2])
        if deref and deref.group(2) is not None:
            outer = at(history, deref.group(1), inner[0])
            if outer and outer[1] == 'adrp':
                page = IMM.search(outer[2])
                chain['cell'] = [num(page.group(1)) if page else None,
                                 int(deref.group(2), 16)]
        elif deref:
            # `ldr xK, [xT]` -> the slot was loaded one instruction earlier
            outer = at(history, deref.group(1), inner[0])
            if outer:
                slot = re.search(r'\[x(\d+), #0x([0-9a-f]+)\]', outer[2])
                base = at(history, slot.group(1), outer[0]) if slot else None
                if slot and base and base[1] == 'adrp':
                    page = IMM.search(base[2])
                    chain['cell'] = [hex(num(page.group(1))) if page else None,
                                     hex(int(slot.group(2), 16))]
    return dict(chain, kind='static-block')


def stores():
    """Every `str*` into 0x50/0x54/0x58 in the whole pinned corpus, with its base chain."""
    out = []
    for (klass, rva), payload in corpus().items():
        insns = payload['instructions']
        history = definitions(insns)
        for index, insn in enumerate(insns):
            if insn['mnemonic'] not in STORES:
                continue
            op = insn.get('op_str') or ''
            if op.rstrip().endswith('!'):
                continue                      # stack push, no base register
            for hit in MEM.finditer(op):
                if hit.group(2) is None:
                    continue
                offset = num(hit.group(2))
                if offset not in WANT:
                    continue
                chain = trace(history, index, hit.group(1))
                out.append(dict(klass=klass, method_rva=rva, rva=insn['rva'],
                                offset=offset, mnemonic=insn['mnemonic'], op=op,
                                kind=chain['kind'], static_from=chain['static_from'],
                                klass_from=chain['klass_from'], cell=chain['cell'],
                                hops=chain['hops']))
    return out


def cctor_gated(klass, rva):
    """`ldr w_, [klass, #0xe0]` + `bl 0x110d12c` in the same method is the cctor gate."""
    payload = corpus()[(klass, rva)]
    insns = payload['instructions']
    gate = any(i['mnemonic'] in ('ldr', 'ldur') and '#0xe0]' in (i.get('op_str') or '')
               for i in insns)
    init = any(BD.call_target(i) == CLASS_INIT for i in insns)
    return dict(gate=gate, init=init)


def declared():
    """`dump.cs` field block of GameDatas: name -> offset, and whether it is static."""
    text = gzip.decompress((ROOT / DUMP).read_bytes()).decode('utf-8', 'replace')
    head = text.find('public class GameDatas')
    body = text[head:text.find('// Properties', head)]
    out = {}
    for line in body.splitlines():
        hit = re.match(r'\s*(public|private|protected|internal)( static)? (\w[\w<>\[\]]*) (\w+); // 0x([0-9A-F]+)',
                       line)
        if hit:
            out[hit.group(4)] = dict(offset=int(hit.group(5), 16), static=bool(hit.group(2)))
    return out


def previous():
    return json.loads(gzip.decompress((ROOT / PREV).read_bytes()))


def build_payload():
    rows = stores()
    fields = declared()
    prev = previous()
    checks = []

    def check(name, passed, detail=None):
        checks.append(dict(name=name, passed=bool(passed), detail=detail))

    counts = {kind: sum(1 for row in rows if row['kind'] == kind)
              for kind in ('cell', 'static-block', 'instance', 'unknown')}
    counters = [row for row in rows
                if row['kind'] == 'static-block' and row['klass'] == 'GameDatas']
    others = [row for row in rows
              if row['kind'] == 'static-block' and row['klass'] != 'GameDatas']
    by_offset = {hex(offset): sum(1 for row in rows if row['offset'] == offset)
                 for offset in WANT}
    gates = {row['rva']: cctor_gated(row['klass'], row['method_rva']) for row in counters}
    by_fifty_four = [row for row in rows
                     if row['offset'] == 0x54 and row['kind'] == 'static-block']

    check('the-corpus-is-1788-methods', len(corpus()) == 1788, len(corpus()))
    check('the-corpus-is-159059-instructions',
          sum(len(p['instructions']) for p in corpus().values()) == 159059,
          sum(len(p['instructions']) for p in corpus().values()))
    check('there-are-102-stores-at-the-three-offsets', len(rows) == 102, len(rows))
    check('every-store-is-classified', sum(counts.values()) == len(rows), counts)
    check('no-store-writes-a-metadata-cell', counts['cell'] == 0, counts['cell'])
    check('sixteen-stores-go-through-a-static-fields-block',
          counts['static-block'] == 16, counts['static-block'])
    check('the-six-key-counters-are-among-them', len(counters) == 6, len(counters))
    check('all-six-go-through-one-typeinfo-cell',
          {tuple(row['cell']) for row in counters} == {TYPEINFO_CELL},
          sorted({tuple(row['cell']) for row in counters}))
    check('the-other-ten-go-through-other-cells',
          len(others) == 10 and all(tuple(row['cell']) != TYPEINFO_CELL for row in others),
          sorted({row['klass'] for row in others}))
    check('every-counter-write-is-cctor-gated',
          all(value['gate'] and value['init'] for value in gates.values()),
          {str(k): v for k, v in gates.items()})
    check('the-offsets-are-the-three-declared-static-fields',
          all(fields.get(FIELDS[offset], {}).get('offset') == offset
              and fields[FIELDS[offset]]['static'] for offset in WANT),
          {FIELDS[offset]: fields.get(FIELDS[offset]) for offset in WANT})
    check('the-one-unknown-base-is-not-a-counter-store',
          counts['unknown'] == 1
          and [row['klass'] for row in rows if row['kind'] == 'unknown'] != ['GameDatas'],
          [(row['klass'], row['rva']) for row in rows if row['kind'] == 'unknown'])
    check('only-gamedatas-writes-0x54-through-a-static-block',
          len(by_fifty_four) == 2 and {row['klass'] for row in by_fifty_four} == {'GameDatas'},
          [(row['klass'], row['rva']) for row in by_fifty_four])
    check('this-agrees-with-176-on-the-six-sites',
          sorted((row['rva'], row['offset']) for row in counters)
          == sorted((row['rva'], row['offset']) for row in prev['writers']),
          [row['rva'] for row in counters])

    return dict(
        schema='counter-static-writers/1',
        evidence='STATIC-ONLY: pinned asm slices + dump.cs; no device, no probe.',
        provenance=dict(branch='arena/535b0541-windwings-space-shooter-game-p',
                        corpus='datas/l2_535b0541_*.json.gz scans (1788 methods)',
                        dump=DUMP, dump_sha256=sha_file(DUMP),
                        previous=PREV, previous_sha256=sha_file(PREV)),
        chain=dict(typeinfo_cell=list(TYPEINFO_CELL),
                   static_hop=hex(STATIC_HOP), cctor_gate=hex(CCTOR_GATE),
                   class_init=hex(CLASS_INIT)),
        corpus=dict(methods=len(corpus()),
                    instructions=sum(len(p['instructions']) for p in corpus().values()),
                    classes=len({klass for klass, _ in corpus()})),
        census=dict(stores=len(rows), **counts, by_offset=by_offset,
                    methods=len({row['method_rva'] for row in rows}),
                    classes=len({row['klass'] for row in rows})),
        counters=[dict(field=FIELDS[row['offset']], klass=row['klass'],
                       offset=row['offset'], rva=row['rva'], method_rva=row['method_rva'],
                       mnemonic=row['mnemonic'], op=row['op'],
                       accessor=ACCESSORS[row['offset']][0],
                       cell=row['cell'], static_from=row['static_from'],
                       klass_from=row['klass_from'], cctor=gates[row['rva']])
                  for row in counters],
        other_static_blocks=[dict(klass=row['klass'], rva=row['rva'],
                                  method_rva=row['method_rva'], offset=row['offset'],
                                  op=row['op'], cell=row['cell'])
                             for row in others],
        declared={name: value for name, value in fields.items()
                  if name in FIELDS.values()},
        premise=dict(
            claimed_by_176='instance fields +0x50/+0x54/+0x58 on the object behind '
                           'slot 0x2adb000+0xaf8, then +0xb8; "properties, not statics"',
            actual='`+0xb8` is `Il2CppClass::static_fields`; keyCount0/1/2 are the '
                   '`private static` fields at 0x50/0x54/0x58 of GameDatas '
                   '(TypeDefIndex 249); the accessors are static, and the write is '
                   'cctor-gated',
            unchanged='the six store sites (20070896, 20071048, 20071224, 20071376, '
                      '20071552, 20071704) and their fields'),
        item_32=dict(
            asked='a direct static store outside these classes',
            answer='none in the corpus: six stores into GameDatas\' static block, all '
                   'inside the three accessors; the other ten static-block stores hit '
                   'other classes at the same offsets',
            outside_stores=[row['rva'] for row in counters
                            if row['klass'] != 'GameDatas']),
        closures=[dict(n=32, source=132,
                       item='a direct static store outside these classes',
                       verdict='CLOSED',
                       evidence=dict(cell_stores=0, static_block=16, gamedatas=6,
                                     outside_stores=[],
                                     note='the counters are `private static` fields, so '
                                          'the item\'s premise was the answer'))],
        limits=['a base register supplied as an argument stays `unknown` (1 hit: '
                'Box_Rewards 20002516, a 128-bit store)',
                'the corpus is the pinned slices, so a writer in a method no scan '
                'contains is still invisible',
                'the value in the static block after a match stays '
                'MODEL_NOT_MEASURED runtime'],
        checks=checks,
    )


def build(output=None):
    payload = build_payload()
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=1).encode()
    packed = gzip.compress(blob, 9, mtime=0)
    if output:
        (ROOT / output).write_bytes(packed)
    return payload, packed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    payload, packed = build(ARTIFACT if args.write else None)
    failing = [row['name'] for row in payload['checks'] if not row['passed']]
    print(json.dumps(dict(bytes=len(packed), sha256=hashlib.sha256(packed).hexdigest(),
                          stores=payload['census']['stores'],
                          static_block=payload['census']['static-block'],
                          checks=len(payload['checks']), failing=len(failing),
                          names=failing), ensure_ascii=False))
    return 1 if failing else 0


if __name__ == '__main__':
    sys.exit(main())
