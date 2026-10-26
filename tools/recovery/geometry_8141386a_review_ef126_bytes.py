"""R1/122 fresh original libunity bytes for fixed ef126 dispatch review.
provenance: arena/8141386a-windwings-space-shooter-game-p
Streamed read-only ZIP/mmap, bounded selected spans, executable direct-branch and
all-RELA target census. Reuses frozen own119 ELF reader, no producer extractor/tool
execution, SDK, graph/controller construction, native execution or APK modification.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import shutil
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.verify.geometry_8141386a_atlas_io import BRANCH, canonical, sha_file, scratch
from tools.recovery.geometry_8141386a_review_ef123_bytes import Elf, XAPK, UNITY

RAW = ROOT / 'reverse-engineering/raw/geometry-8141386a/review-ef126'
TARGET = 0x6cf7b4


def collect(lib):
    peer = json.loads(gzip.decompress((RAW / 'peer-probe126.json.gz').read_bytes()))
    e = Elf(lib)
    try:
        spans = {}; wanted = peer['windows'] + peer['cells']
        for row in wanted:
            key = (row['va'], len(row['hex']) // 2)
            if key in spans:
                continue
            s = e.span(*key)
            if s['hex'] != row['hex'] or s['file_offset'] != row['file_offset']:
                raise ValueError('fresh original selected span differs from peer126')
            spans[key] = s
        fdes = e.selected_fdes({r['entry'] for r in peer['followed']})
        selected_relas = []; target_relas = []; imports = []; types = Counter()
        selected_imports = {r['address'] for r in peer['imports']}
        for r in e.relas():
            types[r['type']] += 1
            if r['addend'] == TARGET:
                target_relas.append(r)
            if r['type'] == 1027 and any(a <= r['address'] < a + n for a, n in spans):
                selected_relas.append(r)
            if r['type'] == 1026 and r['address'] in selected_imports:
                # Independent original dynamic-symbol/string bytes, not peer labels.
                rela_sec = next(s for s in e.sections if s[1] == 4 and s[4] <= r['file_offset'] < s[4] + s[5])
                symbols = e.sections[rela_sec[6]]
                sym = symbols[4] + r['symbol'] * symbols[9]
                name_off = struct.unpack_from('<I', e.b, sym)[0]
                strings = e.sections[symbols[6]]
                name_pos = strings[4] + name_off
                end = e.b.find(b'\0', name_pos, strings[4] + strings[5])
                if end < name_pos:
                    raise ValueError('unterminated original import name')
                imports.append(dict(address=r['address'], name=e.b[name_pos:end].decode(),
                    symbol_entry_offset=sym, symbol_hex=e.b[sym:sym+24].hex(),
                    name_file_offset=name_pos, name_hex=e.b[name_pos:end+1].hex(), rela=r))
        refs = []; scanned = 0
        for segment in e.segments:
            if not segment['flags'] & 1:
                continue
            for off in range(segment['offset'], segment['offset'] + segment['filesz'] - 3, 4):
                scanned += 1
                word = struct.unpack_from('<I', e.b, off)[0]
                if word & 0x7c000000 != 0x14000000:
                    continue
                imm = word & 0x3ffffff
                if imm & (1 << 25):
                    imm -= 1 << 26
                pc = segment['va'] + off - segment['offset']
                if pc + imm * 4 != TARGET:
                    continue
                owners = [f for f in fdes if f['start'] <= pc < f['end_exclusive']]
                if len(owners) != 1:
                    raise ValueError('direct reference not covered by exactly one selected original FDE')
                refs.append(dict(pc=pc, target=TARGET, link=bool(word & 0x80000000),
                    file_offset=off, hex=e.b[off:off+4].hex(), owner_start=owners[0]['start'],
                    owner_end_exclusive=owners[0]['end_exclusive']))
        paths = ['tools/recovery/geometry_8141386a_review_ef126_bytes.py',
                 'tools/recovery/geometry_8141386a_review_ef123_bytes.py',
                 str((RAW / 'peer-probe126.json.gz').relative_to(ROOT))]
        return dict(schema=1, item=122, provenance=BRANCH, xapk_sha256=XAPK,
            libunity_sha256=UNITY, libunity_size=lib.stat().st_size,
            segments=e.segments, peer_selected_spans=list(spans.values()), selected_fdes=fdes,
            all_rela_total=sum(types.values()), rela_type_counts=dict(sorted(types.items())),
            target_addend_matches_all_rela_types=target_relas, selected_relative_relas=selected_relas,
            imports=imports, executable_instruction_words_scanned=scanned, target_direct_branches=refs,
            tool_pins={p: sha_file(ROOT / p) for p in paths},
            scope='Fresh selected original ELF bytes/FDEs/imports plus whole file-backed executable B/BL and all ELF RELA addend target census. Not a whole-program invocation/non-use proof, native execution, original controller instance or runtime.')
    finally:
        e.close()


def recover(xapk):
    if sha_file(xapk) != XAPK:
        raise ValueError('original XAPK SHA mismatch')
    with scratch('review126-original-') as directory:
        lib = directory / 'libunity.so'; found = []
        with zipfile.ZipFile(xapk) as outer:
            for i, member in enumerate(sorted(n for n in outer.namelist() if n.endswith('.apk'))):
                part = directory / f'part-{i}.apk'
                with outer.open(member) as src, part.open('wb') as dst:
                    shutil.copyfileobj(src, dst, 1024 * 1024)
                with zipfile.ZipFile(part) as inner:
                    entry = 'lib/arm64-v8a/libunity.so'
                    if entry not in inner.namelist():
                        continue
                    if found:
                        raise ValueError('ambiguous original libunity input')
                    with inner.open(entry) as src, lib.open('wb') as dst:
                        shutil.copyfileobj(src, dst, 1024 * 1024)
                    if sha_file(lib) != UNITY:
                        raise ValueError('original libunity SHA mismatch')
                    found.append(dict(apk_member=member, entry=entry))
        if len(found) != 1:
            raise ValueError('original libunity input absent')
        result = collect(lib); result['input'] = found[0]
        output = RAW / 'fresh-original.json.gz'
        output.write_bytes(gzip.compress(canonical(result) + b'\n', mtime=0))
        print('fresh126 spans', len(result['peer_selected_spans']), 'FDEs', len(result['selected_fdes']),
              'target direct branches', len(result['target_direct_branches']), 'all-type target RELAs',
              len(result['target_addend_matches_all_rela_types']), 'bytes', output.stat().st_size, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--xapk', type=Path, required=True)
    recover(p.parse_args().xapk)
