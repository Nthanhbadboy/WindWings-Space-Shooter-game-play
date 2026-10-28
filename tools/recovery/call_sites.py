#!/usr/bin/env python3
"""Whole-`.text` branch scan: who calls a given set of RVAs. Static bytes only.

Scoped family extraction answers "what is inside these classes"; it cannot answer
"who else calls this setter", because the caller may live in any class. This tool
inverts the problem: it walks every executable segment and decodes only the
AArch64 branch encodings, so finding callers costs one linear pass and no
capstone dependency.

    bl  : 0x94000000 | imm26      (call, x30 written)
    b   : 0x14000000 | imm26      (tail call / jump)

Both use a signed 26-bit word offset relative to the instruction address, so a
hit is `pc + sign_extend(imm26) * 4`. Everything else in the segment is skipped
by 4 bytes, which is exactly the A64 fixed width — no alignment guessing.
"""
import argparse
import gzip
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
XAPK_SHA = 'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
SO_SHA = '9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99'
BL, B = 0x94000000, 0x14000000
MASK = 0xFC000000


def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def extract_so(xapk, folder):
    """Pull lib/arm64-v8a/libil2cpp.so out of the (nested) XAPK."""
    so = Path(folder) / 'libil2cpp.so'
    with zipfile.ZipFile(xapk) as outer:
        for entry in outer.namelist():
            if not entry.endswith('.apk'):
                continue
            part_path = Path(folder) / 'part.apk'
            with outer.open(entry) as src, open(part_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            with zipfile.ZipFile(part_path) as part:
                member = 'lib/arm64-v8a/libil2cpp.so'
                if member in part.namelist():
                    with part.open(member) as src, open(so, 'wb') as dst:
                        shutil.copyfileobj(src, dst)
                    return so
    raise SystemExit('libil2cpp.so not found inside the XAPK')


def segments(so):
    """[(vaddr, offset, filesz, flags)] for every PT_LOAD of the shared object."""
    from elftools.elf.elffile import ELFFile
    with open(so, 'rb') as binary:
        elf = ELFFile(binary)
        return [(s['p_vaddr'], s['p_offset'], s['p_filesz'], s['p_flags'])
                for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD']


def scan(so, targets):
    """Every branch whose destination is one of `targets`."""
    wanted = set(targets)
    hits, scanned = [], []
    with open(so, 'rb') as binary:
        for vaddr, offset, size, flags in segments(so):
            if not flags & 0x1:          # PF_X only: code lives in executable loads
                continue
            binary.seek(offset)
            data = binary.read(size)
            words = memoryview(data[:len(data) // 4 * 4]).cast('I')
            scanned.append(dict(vaddr=vaddr, filesz=size, words=len(words)))
            for index, word in enumerate(words):
                if word & MASK not in (BL, B):
                    continue
                imm = word & 0x03FFFFFF
                if imm & 0x02000000:
                    imm -= 0x04000000
                pc = vaddr + 4 * index
                destination = pc + 4 * imm
                if destination in wanted:
                    hits.append(dict(rva=pc, target=destination,
                                     kind='bl' if word & MASK == BL else 'b',
                                     word=word))
    return hits, scanned


def build(xapk, target_specs):
    """target_specs: [(name, rva)]."""
    assert sha_file(xapk) == XAPK_SHA, 'unexpected XAPK bytes'
    with tempfile.TemporaryDirectory() as folder:
        so = extract_so(xapk, folder)
        so_sha = sha_file(so)
        assert so_sha == SO_SHA, 'unexpected libil2cpp.so bytes'
        hits, scanned = scan(so, [rva for _, rva in target_specs])
    # the temporary directory is gone past this point: keep only the hash
    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Branch-encoding scan of the pinned original libil2cpp.so. '
             'It reports callers only; what each caller does is not decoded here.',
        provenance=dict(xapk_sha256=sha_file(xapk), libil2cpp_sha256=so_sha),
        method=dict(encodings={'bl': hex(BL), 'b': hex(B), 'mask': hex(MASK)},
                    rule='destination = pc + 4 * sign_extend(imm26)',
                    segments=scanned,
                    words_scanned=sum(s['words'] for s in scanned)),
        targets=[dict(name=name, rva=rva) for name, rva in target_specs],
        hits=sorted(hits, key=lambda h: (h['target'], h['rva'])),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--xapk', required=True)
    parser.add_argument('--target', action='append', required=True,
                        help='NAME=0xRVA, repeatable')
    parser.add_argument('--output',
                        default='reverse-engineering/raw/call-sites-535b0541/calls.json.gz')
    args = parser.parse_args()
    specs = []
    for spec in args.target:
        name, rva = spec.split('=')
        specs.append((name, int(rva, 0)))
    payload = build(args.xapk, specs)
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(target),
                          words=payload['method']['words_scanned'],
                          hits=len(payload['hits']))))


if __name__ == '__main__':
    main()
