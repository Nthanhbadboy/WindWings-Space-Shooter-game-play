"""R1/123 fresh original libunity bytes for fixed ef127 null-domain review.
provenance: arena/8141386a-windwings-space-shooter-game-p
Streamed read-only ZIP/mmap, bounded selected spans, original FDE/table/import
and selected relative-relocation equality. No global branch census in this cycle.
Reuses frozen own119 ELF reader, no producer extractor/tool execution, SDK,
graph/controller construction, native execution or APK modification.
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

RAW = ROOT / 'reverse-engineering/raw/geometry-8141386a/review-ef127'
TARGET = 0x6cf7b4


def collect(lib):
    peer = json.loads(gzip.decompress((RAW / 'peer-probe127.json.gz').read_bytes()))
    e = Elf(lib)
    try:
        spans = {}; wanted = peer['windows'] + peer['cells']
        for row in wanted:
            key = (row['va'], len(row['hex']) // 2)
            if key in spans:
                continue
            s = e.span(*key)
            if s['hex'] != row['hex'] or s['file_offset'] != row['file_offset']:
                raise ValueError('fresh original selected span differs from peer127')
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
        paths = ['tools/recovery/geometry_8141386a_review_ef127_bytes.py',
                 'tools/recovery/geometry_8141386a_review_ef123_bytes.py',
                 str((RAW / 'peer-probe127.json.gz').relative_to(ROOT))]
        return dict(schema=1, item=123, provenance=BRANCH, xapk_sha256=XAPK,
            libunity_sha256=UNITY, libunity_size=lib.stat().st_size,
            segments=e.segments, peer_selected_spans=list(spans.values()), selected_fdes=fdes,
            all_rela_total=sum(types.values()), rela_type_counts=dict(sorted(types.items())),
            target_addend_matches_all_rela_types=target_relas, selected_relative_relas=selected_relas,
            imports=imports, bounded_non_fde_entries=[r['entry'] for r in peer['followed'] if r['unwind'] is None],
            tool_pins={p: sha_file(ROOT / p) for p in paths},
            scope='Fresh selected original ELF byte/FDE/table/import and selected-relative-RELA equality for fixed127. Two PLT bounded windows are explicitly not function extents. No new global branch census, SDK/native execution, heap, serialized owner/motion reconstruction or runtime.')
    finally:
        e.close()


def recover(xapk):
    if sha_file(xapk) != XAPK:
        raise ValueError('original XAPK SHA mismatch')
    with scratch('review127-original-') as directory:
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
        print('fresh127 spans', len(result['peer_selected_spans']), 'FDEs', len(result['selected_fdes']),
              'selected RELAs', len(result['selected_relative_relas']), 'imports', len(result['imports']),
              'non-FDE entries', len(result['bounded_non_fde_entries']), 'bytes', output.stat().st_size, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--xapk', type=Path, required=True)
    recover(p.parse_args().xapk)
