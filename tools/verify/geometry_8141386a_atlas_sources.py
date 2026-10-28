"""Stream original-byte queries for #6 replication, without loading all Sprite trees.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

from tools.verify.geometry_8141386a_atlas_io import (
    ROOT, RAW, BRANCH, canonical, full_file, identity, iter_geometry, key,
    scratch, sha_file, write_document,
)
from tools.verify.l3_geometry_8141386a_atlas_binary import encoded_object

XAPK = 'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
APK = '6843e79347f5b0bb68e4a2f9e1b1a3152e31d0875d4821b9928ad5799a95e1e1'
DATA = '7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7'
APK_MEMBER = 'com.Wind.wings.Space.Shooter.apk'
CLASSES = {'Sprite': 213, 'SpriteAtlas': 687078895, 'Texture2D': 28}
QUERY = RAW / 'byte-queries.json.gz'
PINS = RAW / 'source-pins.json'
PEER = RAW / 'peer-af518716b7.json.gz'
PEER_SHA = '8d320f1458f8966ca9acfc11a166194cf9e4e77380db1b8f990e68f0d5338e65'
PEER_HEAD = 'af518716b7f3f4a5d69a6a87ca75e2e8ee2692f6'


def build(query, pins):
    folder = ROOT / 'reverse-engineering/raw/sprite-geometry'
    index = json.loads((folder / 'index.json').read_bytes())
    if index['inputs_sha256']['data.unity3d'] != DATA:
        raise ValueError('geometry package identity drift')
    counts, serialized = Counter(), Counter()
    seen = set()

    def rows():
        for row, location in iter_geometry():
            k = key(row)
            if k in seen or row['context_status'] != 'resolved':
                raise ValueError('duplicate/unresolved geometry identity')
            seen.add(k)
            counts[row['type']] += 1
            expected, _ = encoded_object(row)
            if expected is not None:
                serialized[row['type']] += 1
            yield dict(identity=identity(k), type=row['type'], class_id=CLASSES[row['type']],
                       expected_object_sha256=row['object_bytes_sha256'],
                       reencoded_byte_size=len(expected) if expected is not None else None,
                       raw_location=location)

    write_document(query, dict(schema=1, item=6, provenance=BRANCH,
                              xapk_sha256=XAPK, apk_sha256=APK, bundle_sha256=DATA,
                              apk_member=APK_MEMBER, scope='Read-only original objects; seeded inverse serialization, not runtime'),
                   [('objects', rows())])
    if counts != index['counts']:
        raise ValueError('raw inventory differs from index')
    paths = ['reverse-engineering/raw/sprite-geometry/index.json',
             'tools/verify/geometry_8141386a_atlas_io.py',
             'tools/verify/l3_geometry_8141386a_atlas_binary.py',
             'tools/recovery/geometry_8141386a_atlas_bytes.py',
             'tools/verify/unityfs111_binary.py', 'tools/verify/serialized110_binary.py']
    paths.extend(str((folder / c['path']).relative_to(ROOT)) for c in index['files'])
    value = dict(schema=1, item=6, provenance=BRANCH, source_counts=dict(counts),
                 inverse_serialization_original_hash_equal=dict(serialized),
                 query_sha256=sha_file(query),
                 source_pins={p: sha_file(ROOT / p) for p in sorted(paths)},
                 lineage='Shared raw Sprite-geometry UnityPy1.25.4 capture/schema; mesh75/MeshHelper conventions; ef111/110 framing. Not clean-room discovery. No peer tree import.')
    Path(pins).write_bytes(canonical(value) + b'\n')
    return value


def verify_pins():
    value = json.loads(PINS.read_bytes())
    if value['provenance'] != BRANCH or sha_file(QUERY) != value['query_sha256']:
        raise ValueError('atlas source provenance/query drift')
    for p, digest in value['source_pins'].items():
        if sha_file(ROOT / p) != digest:
            raise ValueError('atlas source pin drift: ' + p)
    if sha_file(PEER) != PEER_SHA:
        raise ValueError('handed-off primary #6 snapshot drift')
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    with scratch('source-') as directory:
        q, p = directory / 'queries.gz', directory / 'pins.json'
        value = build(q, p)
        for expected, actual in ((q, QUERY), (p, PINS)):
            if args.check:
                if not actual.exists() or sha_file(expected) != sha_file(actual):
                    raise SystemExit('atlas source/query drift: ' + str(actual))
            else:
                actual.parent.mkdir(parents=True, exist_ok=True)
                expected.replace(actual)
    verify_pins()
    print(value['source_counts'], 'objects;', value['inverse_serialization_original_hash_equal'],
          'full inverse serialization matches original captured SHA')
