#!/usr/bin/env python3
"""Targeted original-APK sprite/atlas geometry; no pixels, font programs or audio.

Full Sprite/SpriteAtlas typetrees, projected Texture2D metadata. Each PPtr stays
file-scoped. Never infer crop cells from names. Errors are preserved and fail CI.
"""
import base64
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

DATA = Path('/tmp/apk/extract')
OUT = Path('reverse-engineering/raw/sprite-geometry')
PIN = '7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7'
TEXTURE_FIELDS = {'m_Name', 'm_Width', 'm_Height', 'm_CompleteImageSize', 'm_TextureFormat',
                  'm_MipCount', 'm_IsReadable', 'm_ImageCount', 'm_TextureDimension',
                  'm_StreamingMipmaps', 'm_StreamingMipmapsPriority', 'm_ColorSpace',
                  'm_PlatformBlob', 'm_StreamData'}


def json_binary(value):
    if isinstance(value, (bytes, bytearray)):
        return dict(encoding='base64', bytes_base64=base64.b64encode(value).decode())
    raise TypeError(type(value).__name__)


def main():
    import UnityPy
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'apk-analyze'))
    from ui_render_context import file_context
    inputs = {n: hashlib.sha256((DATA / n).read_bytes()).hexdigest() for n in ('data.unity3d', 'libil2cpp.so', 'global-metadata.dat')}
    assert inputs['data.unity3d'] == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    env = UnityPy.load(str(DATA / 'data.unity3d'))
    counts, rows, errors = Counter(), [], []
    for obj in env.objects:
        kind = obj.type.name
        if kind not in ('Sprite', 'SpriteAtlas', 'Texture2D'):
            continue
        row = dict(file_context(obj), path_id=obj.path_id, type=kind,
                   object_bytes_sha256=hashlib.sha256(obj.get_raw_data()).hexdigest())
        try:
            tree = obj.read_typetree()
            row.update(status='exported', tree=tree if kind != 'Texture2D' else {k: v for k, v in tree.items() if k in TEXTURE_FIELDS},
                       projection='full_typetree' if kind != 'Texture2D' else 'metadata_only_no_image_data')
        except Exception as exc:
            row.update(status='unresolved', error=repr(exc))
            errors.append(dict(serialized_file=row['serialized_file'], path_id=row['path_id'], type=kind, error=repr(exc)))
        rows.append(row)
        counts[kind] += 1
    # Deterministic chunks, no silently truncated export and no tracked file >5MB.
    rows.sort(key=lambda r: (r['type'], r['serialized_file'], r['path_id']))
    files = []
    for start in range(0, len(rows), 500):
        chunk = rows[start:start + 500]
        payload = ''.join(json.dumps(r, ensure_ascii=False, default=json_binary, allow_nan=False) + '\n' for r in chunk).encode()
        path = OUT / f'objects-{start // 500:03}.jsonl.gz'
        encoded = gzip.compress(payload, mtime=0)
        assert len(encoded) < 5_000_000
        path.write_bytes(encoded)
        files.append(dict(path=path.name, rows=len(chunk), sha256_decompressed=hashlib.sha256(payload).hexdigest()))
    index = dict(status='PROVISIONAL_RAW_NOT_CROP_VALIDATION', inputs_sha256=inputs,
                 unitypy_version=UnityPy.__version__, counts=dict(counts), files=files, errors=errors)
    (OUT / 'index.json').write_text(json.dumps(index, indent=2) + '\n')
    print(json.dumps(dict(counts=counts, errors=errors)))
    assert rows and counts['Sprite'] and not errors, 'Missing/error records; do not claim complete geometry'


if __name__ == '__main__':
    main()
