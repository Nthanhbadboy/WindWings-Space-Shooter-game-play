"""Read-only original #6 byte recovery with bounded block cache and streamed records.
provenance: arena/8141386a-windwings-space-shooter-game-p
No UnityPy, bundle-wide inflation, media export, modifications or runtime. Acknowledged
ef UnityFS111/SerializedFile110 framing; typetree-seeded inverse serialization.
"""
from __future__ import annotations
import argparse
from collections import Counter, OrderedDict
import hashlib
import json
import mmap
from pathlib import Path
import resource
import shutil
import sqlite3
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.verify.geometry_8141386a_atlas_io import (
    RAW, BRANCH, canonical, identity, iter_arrays, iter_geometry, key, scratch,
    sha, sha_file, write_document,
)
from tools.verify.geometry_8141386a_atlas_sources import (
    XAPK, APK, DATA, APK_MEMBER, QUERY, PINS, verify_pins,
)
from tools.verify.l3_geometry_8141386a_atlas_binary import encoded_object
from tools.verify.serialized110_binary import header, parse
from tools.verify.unityfs111_binary import framing, block_bytes


class Bundle:
    """mmap only compressed bytes; at most 16 decoded blocks remain resident."""
    def __init__(self, path):
        self.handle = Path(path).open('rb')
        self.blob = mmap.mmap(self.handle.fileno(), 0, access=mmap.ACCESS_READ)
        self.frame = framing(self.blob)
        self.cache = OrderedDict()
        self.receipts = {}
        # The inherited framing reader permits up to 128MiB/block; this source lane
        # explicitly refuses that much larger working set.
        if any(b['uncompressed_size'] > 2*1024*1024 for b in self.frame['blocks']):
            self.close()
            raise ValueError('source block exceeds 2MiB incremental budget')
        self.cache_high_water = 0

    def close(self):
        self.blob.close()
        self.handle.close()

    def read(self, offset, size):
        if not 0 <= offset <= offset+size <= self.frame['uncompressed_size']:
            raise ValueError('logical bundle extent')
        result = bytearray()
        for b in self.frame['blocks']:
            start, stop = b['uncompressed_start'], b['uncompressed_start'] + b['uncompressed_size']
            if offset >= stop or offset+size <= start:
                continue
            number = b['index']
            if number not in self.cache:
                decoded = block_bytes(self.blob, b)
                packed = self.blob[b['physical_start']:b['physical_start']+b['compressed_size']]
                self.receipts[number] = dict(**b, compressed_sha256=sha(packed),
                                            decoded_sha256=sha(decoded))
                self.cache[number] = decoded
                if len(self.cache) > 16:
                    self.cache.popitem(last=False)
                self.cache_high_water = max(self.cache_high_water, len(self.cache))
            decoded = self.cache[number]
            self.cache.move_to_end(number)
            result.extend(decoded[max(0, offset-start):min(len(decoded), offset+size-start)])
        if len(result) != size:
            raise ValueError('logical bundle read consumption')
        return bytes(result)

    def object_hash(self, offset, size):
        h = hashlib.sha256()
        for p in range(0, size, 256*1024):
            h.update(self.read(offset+p, min(256*1024, size-p)))
        return h.hexdigest()


def recover(path):
    verify_pins()
    if sha_file(path) != XAPK:
        raise ValueError('original XAPK SHA mismatch')
    counts = Counter()
    with scratch('recover-') as directory:
        # Nested ZIP members are copied to disk, never outer.read()/inner.read().
        apk_path, bundle_path = directory / 'base.apk', directory / 'data.unity3d'
        with zipfile.ZipFile(path) as outer:
            with outer.open(APK_MEMBER) as src, apk_path.open('wb') as dst:
                shutil.copyfileobj(src, dst, 1024*1024)
        if sha_file(apk_path) != APK:
            raise ValueError('original APK SHA mismatch')
        with zipfile.ZipFile(apk_path) as inner:
            with inner.open('assets/bin/Data/data.unity3d') as src, bundle_path.open('wb') as dst:
                shutil.copyfileobj(src, dst, 1024*1024)
        if sha_file(bundle_path) != DATA:
            raise ValueError('original bundle SHA mismatch')

        db = sqlite3.connect(directory / 'selection.sqlite')
        db.execute('PRAGMA cache_size=-4096')
        db.execute('CREATE TABLE objects(file TEXT, pid INTEGER, query TEXT, raw TEXT, entry TEXT, PRIMARY KEY(file,pid))')
        for _, _, q in iter_arrays(QUERY, {'objects'}):
            db.execute('INSERT INTO objects(file,pid,query) VALUES(?,?,?)', (*key(q['identity']), canonical(q).decode()))
        for row, _ in iter_geometry():
            changed = db.execute('UPDATE objects SET raw=? WHERE file=? AND pid=?',
                                 (canonical(row).decode(), *key(row))).rowcount
            if changed != 1:
                raise ValueError('raw/query identity mismatch')
        db.commit()
        if db.execute('SELECT count(*) FROM objects WHERE raw IS NULL').fetchone()[0]:
            raise ValueError('query outside captured raw inventory')
        bundle = Bundle(bundle_path)
        try:
            files = []
            for (file,) in db.execute('SELECT DISTINCT file FROM objects ORDER BY file').fetchall():
                nodes = [n for n in bundle.frame['nodes'] if 'data.unity3d/' + n['path'] == file]
                if len(nodes) != 1:
                    raise ValueError('ambiguous/missing original owning file')
                node = nodes[0]
                h = header(bundle.read(node['offset'], 48))
                if h['data_offset'] > 32*1024*1024 or h['endian'] != '<' or h['file_size'] != node['size']:
                    raise ValueError('unsupported file/header budget')
                prefix = bundle.read(node['offset'], h['data_offset'])
                table = parse(prefix)
                wanted = {r[0] for r in db.execute('SELECT pid FROM objects WHERE file=?', (file,))}
                entries = [e for e in table['objects'] if e['path_id'] in wanted]
                if len(entries) != len(wanted):
                    raise ValueError('original object inventory is incomplete')
                # Compare the actual external file table, not a name-guessing global resolver.
                actual_external_paths = [e['path'] for e in table['externals']]
                for (raw,) in db.execute('SELECT raw FROM objects WHERE file=?', (file,)):
                    row = json.loads(raw)
                    if [e['path'] for e in row['externals']] != actual_external_paths:
                        raise ValueError('original/captured owning-file external table differs')
                files.append(dict(serialized_file=file, node=node, header=h,
                                  metadata_prefix_sha256=sha(prefix), object_count=len(table['objects']),
                                  selected_count=len(entries), externals=table['externals']))
                del table, prefix
                for e in entries:
                    db.execute('UPDATE objects SET entry=? WHERE file=? AND pid=?',
                               (canonical(dict(**e, bundle_logical_offset=node['offset']+e['byte_start'])).decode(), file, e['path_id']))
                db.commit()
            pin_paths = ['tools/recovery/geometry_8141386a_atlas_bytes.py',
                         'tools/verify/geometry_8141386a_atlas_sources.py',
                         'tools/verify/geometry_8141386a_atlas_io.py',
                         'tools/verify/l3_geometry_8141386a_atlas_binary.py',
                         'tools/verify/serialized110_binary.py', 'tools/verify/unityfs111_binary.py',
                         str(QUERY.relative_to(ROOT)), str(PINS.relative_to(ROOT))]

            def object_rows():
                cursor = db.execute('SELECT file,pid,query,raw,entry FROM objects ORDER BY file,pid')
                for file, pid, q, raw, entry in cursor:
                    q, row, e = json.loads(q), json.loads(raw), json.loads(entry)
                    if e['class_id'] != q['class_id']:
                        raise ValueError('original class mismatch')
                    original_sha = bundle.object_hash(e['bundle_logical_offset'], e['byte_size'])
                    if original_sha != q['expected_object_sha256']:
                        raise ValueError('original object SHA differs from capture')
                    result = dict(identity=identity((file, pid)), type=row['type'],
                                  object_table_entry=e, object_sha256=original_sha,
                                  fresh_sha_matches_capture=True)
                    expected, spans = encoded_object(row)
                    if expected is not None:
                        if len(expected) != e['byte_size'] or len(expected) != q['reencoded_byte_size']:
                            raise ValueError('inverse serialization extent mismatch')
                        actual = bundle.read(e['bundle_logical_offset'], e['byte_size'])
                        if expected != actual:
                            raise ValueError('inverse serialization differs from original bytes')
                        result['whole_inverse_serialization_byte_equal'] = True
                        # Keep original full binary data for all map/packed arrays and every
                        # static vertex/index buffer, plus typed scalar/count fields. Per-map
                        # entry offsets/SHA remain, without duplicating their aggregate hex.
                        for name, span in spans.items():
                            a, z = span['offset'], span['offset'] + span['size']
                            part = actual[a:z]
                            if sha(part) != span['sha256']:
                                raise ValueError('span SHA mismatch')
                            if not name.startswith('m_RenderDataMap['):
                                span['hex'] = part.hex()
                        result['spans'] = spans
                        if row['type'] == 'Sprite':
                            result['empty_counts_read_from_original'] = {
                                name: struct.unpack_from('<i', actual, spans[name]['offset'])[0]
                                for name in ('m_Bones.count', 'm_RD.m_Bindpose.count')}
                    else:
                        result['whole_inverse_serialization_byte_equal'] = None
                        result['scope'] = 'Whole original Texture2D object hash only; no image decode'
                    counts[row['type']] += 1
                    if sum(counts.values()) % 250 == 0:
                        print(sum(counts.values()), 'original objects verified; cache blocks', len(bundle.cache), flush=True)
                    yield result

            def blocks():
                for number in sorted(bundle.receipts):
                    yield bundle.receipts[number]

            header_value = dict(schema=1, item=6, provenance=BRANCH, xapk_sha256=XAPK,
                                apk_sha256=APK, apk_member=APK_MEMBER, bundle_sha256=DATA,
                                files=files, query_sha256=sha_file(QUERY),
                                tool_pins={p: sha_file(ROOT / p) for p in pin_paths},
                                scope='Fresh original whole-object hashes; complete seeded Sprite/SpriteAtlas byte equality and original map/vertex/count spans. NOT native remap/skinning/readback/render.')
            write_document(RAW / 'byte-witness.json.gz', header_value,
                           [('objects', object_rows()), ('block_receipts', blocks())])
            print('Original counts:', dict(counts), 'cache high water:', bundle.cache_high_water,
                  'peak RSS KiB:', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, flush=True)
        finally:
            bundle.close()
            db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--xapk', type=Path, required=True)
    recover(parser.parse_args().xapk)
