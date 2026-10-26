#!/usr/bin/env python3
"""Scoped static disassembly for daily/weekly meta rewards. Never runs the game.

This is a *separate* extractor from `arena_pvp_native.py` on purpose: report 127
and its artifact are ACKed and pinned by SHA, so the #29 raw bytes must not be
regenerated. Everything here writes to its own path.

Two schema differences against the #29 extractor, both needed for reward tables:

* `initialize_arrays` records pair **each** `bl #0x205b07c` (InitializeArray) with
  the `ldr xN, [slot]` that actually feeds its `x1`. The #29 extractor appended
  the paired events back into the list it was filtering, so every call resolved
  to the first slot (`MaxRankStars` came out as ten copies of `[3,3,3]`). The
  slot pointer's 16 target bytes carry the encoded metadata token
  `(kind << 29) | source`, which is what resolves a `<PrivateImplementationDetails>`
  field and therefore its literal blob.
* `slot_refs` keeps the same 16 target bytes per slot, so a string literal slot
  can be resolved offline against `reverse-engineering/il2cpp/stringliteral.json`.
"""
import argparse
import gzip
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
XAPK_SHA = 'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
SO_SHA = '9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99'
FAMILIES = ('GameDatas', 'TimeFreeRewardPack', 'Board_QuestRewards', 'Popup_WatchVideos',
            'Board_EventSeasonPass', 'PVPReward', 'Bonus_Quest', 'GiftType', 'SeasonRewards',
            'Shop_Pack', 'PVP_Manager', 'ArenaConfig', 'ArenaManager')
ARRAY_NEW = 0x110d09c
INIT_ARRAY = 0x205b07c


def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def parse_rela(path):
    """R_AARCH64_RELATIVE addends keyed by slot VA (static metadata usages)."""
    out = {}
    with open(path, 'rb') as f:
        data = f.read()
    shoff = int.from_bytes(data[0x28:0x30], 'little')
    shentsize = int.from_bytes(data[0x3a:0x3c], 'little')
    shnum = int.from_bytes(data[0x3c:0x3e], 'little')
    for i in range(shnum):
        base = shoff + i * shentsize
        if base + 64 > len(data):
            break
        if int.from_bytes(data[base + 4:base + 8], 'little') != 4:
            continue
        off = int.from_bytes(data[base + 0x18:base + 0x20], 'little')
        size = int.from_bytes(data[base + 0x20:base + 0x28], 'little')
        entsize = int.from_bytes(data[base + 0x38:base + 0x40], 'little') or 24
        for pos in range(off, off + size - 23, entsize):
            r_off, r_info, r_add = (int.from_bytes(data[pos + k:pos + k + 8], 'little')
                                    for k in (0, 8, 16))
            if r_info & 0xffffffff == 1027:
                out[r_off] = r_add
    return out


def parse_dump(text):
    rows = []
    for block in text.split('// Namespace:'):
        cls = re.search(r'(?:class|struct|enum) (\S+).*?// TypeDefIndex:', block)
        if not cls:
            continue
        for match in re.finditer(r'// RVA: (0x[0-9A-Fa-f]+) Offset: (0x[0-9A-Fa-f]+)[^\n]*\n\s*([^\n]+)', block):
            rows.append(dict(class_name=cls[1], rva=int(match[1], 16), offset=int(match[2], 16),
                             signature=match[3].strip()))
    return rows


def selected(name, families=FAMILIES):
    return any(name == f or name.startswith(f + '.') for f in families)


def main():
    import capstone
    from elftools.elf.elffile import ELFFile
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--xapk', required=True)
    parser.add_argument('--output', default='reverse-engineering/raw/meta-rewards-535b0541/native.json.gz')
    parser.add_argument('--extra-families', default='',
                        help='comma list appended to FAMILIES (default set unchanged)')
    parser.add_argument('--families-only', default='',
                        help='replace FAMILIES entirely (keeps this raw minimal)')
    parser.add_argument('--rodata', action='append', default=[],
                        help='VA:LEN literal window to pin from read-only segments')
    args = parser.parse_args()
    families = ([f for f in args.families_only.split(',') if f] or list(FAMILIES)) \
        + [f for f in args.extra_families.split(',') if f]
    assert sha_file(args.xapk) == XAPK_SHA
    dump = gzip.decompress((ROOT / 'reverse-engineering/il2cpp/dump.cs.gz').read_bytes())
    rows = parse_dump(dump.decode())
    offsets = sorted({r['offset'] for r in rows if r['offset']})
    ends = dict(zip(offsets, offsets[1:]))
    records = []
    with tempfile.TemporaryDirectory() as folder:
        folder = Path(folder)
        so = folder / 'libil2cpp.so'
        with zipfile.ZipFile(args.xapk) as outer:
            for entry in outer.namelist():
                if not entry.endswith('.apk'):
                    continue
                part_path = folder / 'part.apk'
                with outer.open(entry) as src, open(part_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                with zipfile.ZipFile(part_path) as part:
                    member = 'lib/arm64-v8a/libil2cpp.so'
                    if member in part.namelist():
                        with part.open(member) as src, open(so, 'wb') as dst:
                            shutil.copyfileobj(src, dst)
                        break
        assert sha_file(so) == SO_SHA
        with open(so, 'rb') as binary:
            elf = ELFFile(binary)
            segments = [(s['p_vaddr'], s['p_offset'], s['p_filesz'])
                        for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD']
            engine = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
            relocs = parse_rela(so)


            def read_va(va, n):
                for v, o, length in segments:
                    if v <= va and va + n <= v + length:
                        binary.seek(o + va - v)
                        return binary.read(n)
                return None

            def literal_string(va):
                header = read_va(va, 0x14)
                if not header:
                    return None
                length = int.from_bytes(header[0x10:0x14], 'little')
                if not 0 <= length < 256:
                    return None
                body = read_va(va + 0x14, 2 * length)
                if body is None:
                    return None
                try:
                    text = body.decode('utf-16-le')
                except UnicodeDecodeError:
                    return None
                return text if text.isprintable() and text else None

            windows = []
            for spec in args.rodata:
                va_text, length_text = spec.split(':')
                va = int(va_text, 0)
                data = read_va(va, int(length_text, 0))
                if data is None:
                    raise ValueError('rodata window outside PT_LOAD: ' + spec)
                windows.append(dict(va=va, length=len(data), hex=data.hex(),
                                    sha256=hashlib.sha256(data).hexdigest()))
            for row in rows:
                if not selected(row['class_name'], families) or not row['offset']:
                    continue
                end = ends.get(row['offset'])
                if end is None or end - row['offset'] > 262144:
                    raise ValueError('Unbounded method: ' + str(row))
                size = end - row['offset']
                binary.seek(row['offset'])
                code = binary.read(size)
                assert len(code) == size
                insns = [dict(rva=i.address, mnemonic=i.mnemonic, op_str=i.op_str)
                         for i in engine.disasm(code, row['rva'])]
                regs, tokens = {}, {}
                literals, slots, slot_refs, init_events = [], {}, [], []
                pending_len, pending_new = None, None
                for i in insns:
                    op = i['op_str']
                    if i['mnemonic'] == 'adrp':
                        match = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', op)
                        if match:
                            regs[match[1]] = int(match[2], 16)
                    elif i['mnemonic'] == 'ldr':
                        match = re.fullmatch(r'([sdq]\d+), \[(x\d+)(?:, #(0x[0-9a-f]+|\d+))?\]', op)
                        if match and match[2] in regs:
                            va = regs[match[2]] + int(match[3] or '0', 0)
                            n = {'s': 4, 'd': 8, 'q': 16}[match[1][0]]
                            chunk = read_va(va, n)
                            if chunk:
                                literals.append(dict(instruction_rva=i['rva'], va=va, hex=chunk.hex()))
                    if i['mnemonic'] in ('mov', 'movz'):
                        match = re.fullmatch(r'w1, #(\d+)', op)
                        if match:
                            pending_len = int(match.group(1))
                    if i['mnemonic'] == 'ldr':
                        match = re.fullmatch(r'(x\d+), \[(x\d+)(?:, #(0x[0-9a-f]+|\d+))?\]', op)
                        if match and isinstance(regs.get(match[2]), int):
                            slots[match[1]] = regs[match[2]] + int(match[3] or '0', 0)
                        elif match and match[2] in slots and not match[3]:
                            slot_va = slots[match[2]]
                            addend = relocs.get(slot_va)
                            if addend is not None:
                                head = read_va(addend, 16) or b''
                                lo = int.from_bytes(head[:8], 'little') if len(head) >= 8 else None
                                hi = int.from_bytes(head[8:16], 'little') if len(head) == 16 else None
                                slot_refs.append(dict(rva=i['rva'], slot_va=slot_va, addend=addend,
                                                      token_lo=lo, token_hi=hi,
                                                      string=literal_string(addend)))
                                tokens[match[1]] = dict(slot_va=slot_va, addend=addend,
                                                        token_lo=lo, token_hi=hi)
                                regs[match[1]] = ('slot_value', addend)
                                continue
                    if i['mnemonic'] == 'bl':
                        target = i['op_str'].strip().lstrip('#')
                        if re.fullmatch(r'(0x[0-9a-f]+|\d+)', target):
                            target = int(target, 0)
                        if target == ARRAY_NEW:
                            pending_new = dict(array_new_rva=i['rva'], length=pending_len)
                            pending_len = None
                        elif target == INIT_ARRAY and pending_new is not None and 'x1' in tokens:
                            token = tokens['x1']
                            blob = read_va(token['addend'], 64)
                            init_events.append(dict(
                                rva=i['rva'], initialize_rva=i['rva'],
                                slot_va=token['slot_va'], addend=token['addend'],
                                token_lo=token['token_lo'], token_hi=token['token_hi'],
                                length=pending_new['length'],
                                array_new_rva=pending_new['array_new_rva'],
                                blobs=[blob.hex()] if blob else []))
                            pending_new = None
                    # Conservative invalidation avoids attributing stale ADRP bases.
                    dest = op.split(',')[0]
                    if i['mnemonic'] != 'adrp' and dest.startswith(('x', 'w')) and \
                            i['mnemonic'] not in ('cmp', 'str', 'stp', 'cbz', 'cbnz', 'tbnz', 'tbz'):
                        regs.pop('x' + dest[1:], None)
                    if i['mnemonic'] == 'bl':
                        for n in range(19):
                            regs.pop('x' + str(n), None)
                            tokens.pop('x' + str(n), None)
                records.append(dict(**row, size=size, sha256=hashlib.sha256(code).hexdigest(),
                                    bytes_hex=code.hex(), instructions=insns, literals=literals,
                                    slot_refs=slot_refs, initialize_arrays=init_events))
    output = dict(schema=2, evidence='STATIC_ONLY_ORIGINAL_APK', xapk_sha256=XAPK_SHA,
                  libil2cpp_sha256=SO_SHA, dump_sha256=hashlib.sha256(dump).hexdigest(),
                  boundary='next distinct dump offset; no FDE, runtime, emulator, or device',
                  families=families, rodata_windows=windows, methods=records)
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(output, separators=(',', ':'), sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(methods=len(records), classes=len({r['class_name'] for r in records}),
                          initialize_arrays=sum(len(r['initialize_arrays']) for r in records),
                          bytes=target.stat().st_size, sha256=sha_file(target))))


if __name__ == '__main__':
    main()
