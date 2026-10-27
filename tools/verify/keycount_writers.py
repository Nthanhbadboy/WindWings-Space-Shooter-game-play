#!/usr/bin/env python3
"""Who writes `GameDatas.KeyCount0/1/2` — and why item 32's premise is wrong.

132 recorded three setters for the quest keys and, in the same breath, an open item:
*"the branch scan sees calls, not stores; a writer that assigns statics 0x50/0x54/0x58
inline elsewhere would not appear"*. 176 answers that by scanning stores instead of calls,
and finds that the premise does not hold: `+0x50/+0x54/+0x58` are **instance fields**, not
statics. The chain every accessor walks is

    adrp x20, #0x2adb000 ; ldr x20, [x20, #0xaf8]     the singleton slot
    ldr x0, [x20]                                     the object behind it
    ldr x8, [x0, #0xb8]                               the holder the counters live in
    str w19, [x8, #0x50]                              KeyCount0

so "a direct static store" cannot exist. What *can* exist is another method that reaches
the holder and writes it, so the scan follows the chain: a register counts as the holder
only if it was loaded as `[slot]` then `[..., #0xb8]`, and only writes through such a
register are attributed to these three fields. Offsets alone are meaningless — 130 write
sites in the pinned raws use offsets 0x50/0x54/0x58 on *other* classes' objects.

Result over both pinned corpora: **six** writers, all in `GameDatas` — the three setters,
and the three getters, which cache the value they lazily load. No inline writer anywhere
else in 2,499 methods / 207,276 instructions of native disassembly or in the 139 class
slices / 138,226 instructions of asm.

Nothing is executed. What a device actually stores stays MODEL_NOT_MEASURED runtime.
"""
import argparse
import glob
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = 'datas/l2_535b0541_keycount_writers.json.gz'

NATIVE = 'reverse-engineering/raw/*/native.json.gz'
ASM = 'reverse-engineering/raw/il2cpp-consts/*.asm.txt'

SLOT_PAGE = 0x2adb000
SLOT_OFFSET = 0xaf8
HOLDER_ADDEND = 0xb8
FIELDS = {0x50: 'KeyCount0', 0x54: 'KeyCount1', 0x58: 'KeyCount2'}

GETTERS = {20070740: 'KeyCount0', 20071068: 'KeyCount1', 20071396: 'KeyCount2'}
SETTERS = {20070940: 'KeyCount0', 20071268: 'KeyCount1', 20071596: 'KeyCount2'}

WRITE = ('str', 'strb', 'strh', 'stur', 'stp')
LINE = re.compile(r'^\s+0x([0-9a-f]+):\s+(\S+)\s+(.*)$')


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def native_methods():
    """Every method of the eight pinned native scans, de-duplicated by (class, rva)."""
    out, seen = [], set()
    for path in sorted(ROOT.glob(NATIVE)):
        payload = json.loads(gzip.decompress(path.read_bytes()))
        for method in payload['methods']:
            key = (method['class_name'], method['rva'])
            if key in seen:
                continue
            seen.add(key)
            out.append(dict(source=path.parent.name, klass=method['class_name'],
                            rva=method['rva'], instructions=method['instructions']))
    return out


def asm_methods():
    """The 139 class slices, in the same shape."""
    out = []
    for path in sorted(ROOT.glob(ASM)):
        current = None
        for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
            if line.startswith(';;;'):
                current = dict(source='asm', klass=path.name[:-len('.asm.txt')],
                               signature=line[3:].strip(), instructions=[])
                out.append(current)
                continue
            if current is None:
                continue
            match = LINE.match(line)
            if match:
                current['instructions'].append(dict(rva=int(match.group(1), 16),
                                                    mnemonic=match.group(2),
                                                    op_str=match.group(3).strip()))
    return out


def chain_writers(instructions):
    """Writes through a register that walked slot -> [slot] -> [.., #0xb8]."""
    state, hits = {}, []
    for insn in instructions:
        mnemonic, op_str, rva = insn['mnemonic'], insn['op_str'], insn['rva']
        adrp = re.match(r'^(x\d+), #(0x[0-9a-f]+)$', op_str)
        if mnemonic == 'adrp' and adrp:
            state[adrp.group(1)] = ('page', int(adrp.group(2), 16))
            continue
        load = re.match(r'^(x\d+), \[(x\d+)(?:, #(0x[0-9a-f]+))?\]$', op_str)
        if mnemonic == 'ldr' and load:
            dst, base = load.group(1), load.group(2)
            offset = int(load.group(3), 16) if load.group(3) else 0
            base_tag = state.get(base)
            if base_tag == ('page', SLOT_PAGE) and offset == SLOT_OFFSET:
                state[dst] = ('slot', None)
            elif base_tag == ('slot', None) and offset == 0:
                state[dst] = ('behind', None)
            elif base_tag == ('behind', None) and offset == HOLDER_ADDEND:
                state[dst] = ('holder', None)
            else:
                state.pop(dst, None)
            continue
        written = re.match(r'^(x\d+|w\d+)', op_str)
        if written and mnemonic not in ('cmp', 'tst', 'fcmp', 'fmov', 'movk', 'movz', 'movn'):
            state.pop(written.group(1), None)
        if mnemonic.startswith(WRITE):
            for base, offset in re.findall(r'\[(x\d+)(?:, #(0x[0-9a-f]+))?\]', op_str):
                if not offset or int(offset, 16) not in FIELDS:
                    continue
                cell = int(offset, 16)
                if state.get(base) == ('holder', None):
                    hits.append(dict(rva=rva, mnemonic=mnemonic, op=op_str, offset=cell,
                                     field=FIELDS[cell], kind='holder'))
                elif state.get(base) == ('page', SLOT_PAGE):
                    hits.append(dict(rva=rva, mnemonic=mnemonic, op=op_str, offset=cell,
                                     field=FIELDS[cell], kind='static-cell'))
    return hits


def offset_only(instructions):
    """Writes at the three offsets through *any* base — the naive scan, for contrast."""
    out = []
    for insn in instructions:
        if not insn['mnemonic'].startswith(WRITE):
            continue
        for offset in re.findall(r'\[x\d+, #(0x[0-9a-f]+)\]', insn['op_str']):
            if int(offset, 16) in FIELDS:
                out.append(insn['rva'])
    return out


def collect():
    native, asm = native_methods(), asm_methods()
    writers, naive, static_cell = [], 0, []
    for method in native:
        hits = chain_writers(method['instructions'])
        naive += len(offset_only(method['instructions']))
        for hit in hits:
            if hit['kind'] == 'static-cell':
                static_cell.append(dict(klass=method['klass'], rva=hit['rva']))
                continue
            role = ('setter' if method['rva'] in SETTERS
                    else 'getter' if method['rva'] in GETTERS else 'other')
            writers.append(dict(klass=method['klass'], method_rva=method['rva'], role=role,
                                rva=hit['rva'], op=hit['op'], offset=hit['offset'],
                                field=hit['field'], source=method['source']))
    asm_rvas = []
    for method in asm:
        for hit in chain_writers(method['instructions']):
            if hit['kind'] == 'holder':
                asm_rvas.append(hit['rva'])
    return dict(native=native, asm=asm, writers=writers, naive=naive,
                static_cell=static_cell, asm_rvas=sorted(set(asm_rvas)))


def build_payload():
    data = collect()
    native, asm, writers = data['native'], data['asm'], data['writers']
    chain = []
    for method in native:
        if method['rva'] != 20070940:
            continue
        for insn in method['instructions']:
            if insn['rva'] <= 20071048:
                chain.append(dict(rva=insn['rva'], op=insn['op_str']))

    checks = []

    def check(name, passed, detail=None):
        checks.append(dict(name=name, passed=bool(passed), detail=detail))

    files = len(list(ROOT.glob(ASM)))
    check('six-scans-survive-de-duplication',
          len({m['source'] for m in native}) == 6, len({m['source'] for m in native}))
    check('native-coverage-is-1788-methods', len(native) == 1788, len(native))
    check('native-coverage-is-159059-instructions',
          sum(len(m['instructions']) for m in native) == 159059,
          sum(len(m['instructions']) for m in native))
    check('asm-files-read-are-139', files == 139, files)
    check('asm-coverage-is-138226-instructions',
          sum(len(m['instructions']) for m in asm) == 138226,
          sum(len(m['instructions']) for m in asm))
    check('exactly-six-writers', len(writers) == 6, len(writers))
    check('every-writer-is-in-GameDatas', {w['klass'] for w in writers} == {'GameDatas'},
          sorted({w['klass'] for w in writers}))
    check('every-writer-is-a-known-accessor',
          all(w['role'] in ('getter', 'setter') for w in writers),
          [w['role'] for w in writers])
    check('three-getters-and-three-setters',
          sorted(w['role'] for w in writers) == ['getter'] * 3 + ['setter'] * 3,
          sorted(w['role'] for w in writers))
    check('each-accessor-writes-its-own-field',
          all(FIELDS[w['offset']] == w['field'] ==
              (GETTERS | SETTERS).get(w['method_rva']) for w in writers),
          [(w['method_rva'], w['field']) for w in writers])
    check('the-asm-slices-agree-on-the-six-sites',
          data['asm_rvas'] == sorted(w['rva'] for w in writers), data['asm_rvas'])
    check('no-static-cell-write-exists', data['static_cell'] == [], data['static_cell'])
    check('the-naive-offset-scan-is-useless-here', data['naive'] > 100, data['naive'])
    check('the-chain-is-reproduced-from-the-bytes',
          [row['op'] for row in chain][:6] ==
          ['x30, x21, [sp, #-0x20]!', 'x20, x19, [sp, #0x10]', 'x21, #0x2ce1000',
           'x20, #0x2adb000', 'w8, [x21, #0x5f6]', 'x20, [x20, #0xaf8]'],
          [row['op'] for row in chain][:6])

    return {
        'schema': 'l2/535b0541/keycount-writers/1',
        'evidence': 'STATIC_ONLY_ORIGINAL_APK',
        'note': 'Item 32 asked for a direct static store at 0x50/0x54/0x58. There is no '
                'static cell to store into: the fields hang off the object behind slot '
                '0x2adb000+0xaf8. A chain-aware scan of every pinned method finds six '
                'writers, all accessors of the same class.',
        'premise': dict(
            claimed='a writer that assigns statics 0x50/0x54/0x58 inline elsewhere',
            actual='instance fields +0x50/+0x54/+0x58 on `[object behind slot 0x2adb000'
                   '+0xaf8] + 0xb8`; "KeyCount0/1/2" are properties, not statics',
            chain=[dict(step='singleton slot', page=SLOT_PAGE, offset=SLOT_OFFSET),
                   dict(step='object behind it', addend=0),
                   dict(step='counter holder', addend=HOLDER_ADDEND)],
            window=chain),
        'writers': sorted(writers, key=lambda row: row['rva']),
        'coverage': dict(
            native=dict(scans=sorted({m['source'] for m in native}),
                        scans_on_disk=len(list(ROOT.glob(NATIVE))), methods=len(native),
                        instructions=sum(len(m['instructions']) for m in native),
                        note='the eight files overlap; methods are de-duplicated by '
                             '(class, rva), which leaves six distinct scan origins'),
            asm=dict(files=files, slices_with_header=len({m['klass'] for m in asm}),
                     instructions=sum(len(m['instructions']) for m in asm)),
            naive_offset_only_writes=data['naive'],
            note='offsets alone match %d writes in the pinned raws; only the ones that walk '
                 'the chain belong to these three fields' % data['naive']),
        'limits': [
            'coverage is the corpus, not the binary: a writer inside a method that no '
            'pinned scan contains is still invisible, so item 32 narrows instead of closing.',
            'the getters write because they cache the lazily loaded value; that is a '
            'second writer per field, not a second source of truth.',
            'device state after any of this stays MODEL_NOT_MEASURED runtime.',
        ],
        'provenance': dict(
            xapk_sha256='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e',
            inputs=[dict(path=str(path.relative_to(ROOT)), sha256=sha_file(
                str(path.relative_to(ROOT)))) for path in sorted(ROOT.glob(NATIVE))],
            asm=[dict(path=str(path.relative_to(ROOT)), sha256=sha_file(
                str(path.relative_to(ROOT)))) for path in sorted(ROOT.glob(ASM))]),
        'checks': checks,
    }


def build(output=None):
    payload = build_payload()
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
    packed = gzip.compress(blob, mtime=0)
    if output:
        (ROOT / output).write_bytes(packed)
    return payload, packed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=ARTIFACT)
    args = parser.parse_args()
    payload, packed = build(args.output)
    failed = [row for row in payload['checks'] if not row['passed']]
    print(json.dumps(dict(bytes=len(packed),
                          sha256=hashlib.sha256(packed).hexdigest(),
                          writers=len(payload['writers']),
                          checks=len(payload['checks']),
                          failing=len(failed))))
    if failed:
        print(json.dumps([row['name'] for row in failed]))
        raise SystemExit('gate failed')


if __name__ == '__main__':
    main()
