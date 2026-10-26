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
    return any(name == f or name.startswith(f + '.') or name.startswith(f + '_') for f in FAMILIES)


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
                for i in insns:
                    op = i['op_str']
                    if i['mnemonic'] == 'adrp':
                        match = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', op)
                        if match:
                            regs[match[1]] = int(match[2], 16)
                    elif i['mnemonic'] == 'ldr':
                        match = re.fullmatch(r'([sd]\d+), \[(x\d+)(?:, #(0x[0-9a-f]+|\d+))?\]', op)
                        if match and match[2] in regs:
                            va = regs[match[2]] + int(match[3] or '0', 0)
                            n = 4 if match[1][0] == 's' else 8
                            for v, o, length in segments:
                                if v <= va and va + n <= v + length:
                                    binary.seek(o + va - v)
                                    literals.append(dict(instruction_rva=i['rva'], va=va, hex=binary.read(n).hex()))
                                    break
                    # Conservative invalidation avoids attributing stale ADRP bases.
                    dest = op.split(',')[0]
                    if i['mnemonic'] != 'adrp' and dest.startswith(('x', 'w')) and i['mnemonic'] not in ('cmp', 'str', 'stp', 'cbz', 'cbnz', 'tbnz', 'tbz'):
                        regs.pop('x' + dest[1:], None)
                    if i['mnemonic'] == 'bl':
                        for n in range(19):
                            regs.pop('x' + str(n), None)
                records.append(dict(**row, size=size, sha256=hashlib.sha256(code).hexdigest(), bytes_hex=code.hex(), instructions=insns, literals=literals))
    output = dict(schema=1, evidence='STATIC_ONLY_ORIGINAL_APK', xapk_sha256=XAPK_SHA,
                  libil2cpp_sha256=SO_SHA, dump_sha256=hashlib.sha256(dump).hexdigest(),
                  boundary='next distinct dump offset; no FDE, runtime, emulator, or device', methods=records)
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(output, separators=(',', ':'), sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(methods=len(records), classes=len({r['class_name'] for r in records}), bytes=target.stat().st_size, sha256=sha_file(target))))


if __name__ == '__main__':
    main()
