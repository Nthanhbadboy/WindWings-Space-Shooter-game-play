#!/usr/bin/env python3
"""Scoped, byte-pinned static disassembly. Never launches the game or a device."""
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
BRANCH = 'arena/535b0541-windwings-space-shooter-game-p'
XAPK_SHA = 'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
SO_SHA = '9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99'
FAMILIES = ('Arena', 'Board_Arena', 'Popup_Arena', 'GP_PVP_Manager', 'PVP', 'Board_PVP',
            'Popup_PVP', 'Popup_PvP', 'PVPRank', 'PVPSummary', 'Map_Get_Datas',
            'Enemy_Data_Balance', 'Room', 'PlayerScore', 'PlayerChat', 'PVPPlayDatas',
            'UserDataLeagues', 'UserPointDataLeagues', 'SeasonRewards')


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
            rows.append(dict(class_name=cls[1], rva=int(match[1], 16), offset=int(match[2], 16), signature=match[3].strip()))
    return rows


def selected(name):
    return ('arena' in name.lower() or 'pvp' in name.lower() or
            any(name == f or name.startswith(f + '.') for f in FAMILIES))


def main():
    import capstone
    from elftools.elf.elffile import ELFFile
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--xapk', required=True)
    parser.add_argument('--output', default='reverse-engineering/raw/arena-pvp-535b0541/native.json.gz')
    args = parser.parse_args()
    assert sha_file(args.xapk) == XAPK_SHA
    dump_path = ROOT / 'reverse-engineering/il2cpp/dump.cs.gz'
    dump = gzip.decompress(dump_path.read_bytes())
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
            segments = [(s['p_vaddr'], s['p_offset'], s['p_filesz']) for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD']
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
            for row in rows:
                if not selected(row['class_name']) or not row['offset']:
                    continue
                end = ends.get(row['offset'])
                if end is None or end - row['offset'] > 262144:
                    raise ValueError('Unbounded method: ' + str(row))
                size = end - row['offset']
                binary.seek(row['offset'])
                code = binary.read(size)
                assert len(code) == size
                insns = [dict(rva=i.address, mnemonic=i.mnemonic, op_str=i.op_str) for i in engine.disasm(code, row['rva'])]
                # Preserve actual literal bytes, not the old rounded constant summaries.
                regs = {}
                literals = []
                slots, slot_refs, ia_events, ia_calls = {}, [], [], []
                pending_len = None
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
                            for v, o, length in segments:
                                if v <= va and va + n <= v + length:
                                    binary.seek(o + va - v)
                                    literals.append(dict(instruction_rva=i['rva'], va=va, hex=binary.read(n).hex()))
                                    break
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
                                slot_refs.append(dict(rva=i['rva'], slot_va=slot_va,
                                                      addend=addend, string=literal_string(addend)))
                                if match[1] == 'x1':
                                    ia_events.append(dict(rva=i['rva'], slot_va=slot_va,
                                                          addend=addend, length=pending_len))
                                regs[match[1]] = ('slot_value', addend)
                                continue
                    if i['mnemonic'] == 'bl' and i['op_str'] == '#0x205b07c':
                        ia_calls.append(i['rva'])
                    # Conservative invalidation avoids attributing stale ADRP bases.
                    dest = op.split(',')[0]
                    if i['mnemonic'] != 'adrp' and dest.startswith(('x', 'w')) and i['mnemonic'] not in ('cmp', 'str', 'stp', 'cbz', 'cbnz', 'tbnz', 'tbz'):
                        regs.pop('x' + dest[1:], None)
                    if i['mnemonic'] == 'bl':
                        for n in range(19):
                            regs.pop('x' + str(n), None)
                for call in ia_calls:
                    before = [e for e in ia_events if e['rva'] < call]
                    if not before:
                        continue
                    event = dict(before[-1])
                    event['initialize_rva'] = call
                    addend = event['addend']
                    head = read_va(addend, 64)
                    deref = read_va(addend, 8)
                    pointer = int.from_bytes(deref, 'little') if deref else 0
                    tail = read_va(pointer, 64) if pointer else None
                    event['blobs'] = [b.hex() for b in (head, tail) if b]
                    ia_events.append(event)
                records.append(dict(**row, size=size, sha256=hashlib.sha256(code).hexdigest(), bytes_hex=code.hex(),
                                    instructions=insns, literals=literals, slot_refs=slot_refs, initialization=ia_events))
    output = dict(schema=1, evidence='STATIC_ONLY_ORIGINAL_APK', xapk_sha256=XAPK_SHA,
                  libil2cpp_sha256=SO_SHA, dump_sha256=hashlib.sha256(dump).hexdigest(),
                  boundary='next distinct dump offset; no FDE, runtime, emulator, or device', methods=records)
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(output, separators=(',', ':'), sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(methods=len(records), classes=len({r['class_name'] for r in records}), bytes=target.stat().st_size, sha256=sha_file(target))))


if __name__ == '__main__':
    main()
