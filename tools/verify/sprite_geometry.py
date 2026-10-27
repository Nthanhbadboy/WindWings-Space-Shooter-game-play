"""File-scoped Sprite -> atlas render key -> texture rectangle, no pixel rendering."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'reverse-engineering/raw/sprite-geometry'


def load_objects():
    index = json.loads((RAW / 'index.json').read_text())
    rows, sources = [], []
    for chunk in index['files']:
        path = RAW / chunk['path']
        data = gzip.decompress(path.read_bytes())
        assert hashlib.sha256(data).hexdigest() == chunk['sha256_decompressed']
        group = [json.loads(line) for line in data.splitlines()]
        assert len(group) == chunk['rows']
        rows.extend(group)
        sources.append(chunk)
    assert Counter(r['type'] for r in rows) == index['counts']
    assert not index['errors'] and all(r['status'] == 'exported' for r in rows)
    return index, rows, sources


def resolve(owner, pointer, objects):
    if pointer['m_PathID'] == 0:
        return None
    file_id = pointer['m_FileID']
    name = owner['serialized_file']
    if file_id:
        candidates = [r['path'] for r in owner['externals'] if r['file_id'] == file_id]
        if len(candidates) != 1:
            raise ValueError('missing/ambiguous external file')
        name = candidates[0].replace('\\', '/').rsplit('/', 1)[-1]
    key = (name, pointer['m_PathID'])
    if key not in objects:
        raise ValueError('target absent in scoped geometry inventory: ' + str(key))
    return objects[key]


def settings(raw):
    # UnityPy1.25.4 SpriteSettings (preserved with wheel license under toolchain).
    return dict(raw=raw, packed=bool(raw & 1), packing_mode=(raw >> 1) & 1,
                packing_rotation=(raw >> 2) & 15, mesh_type=(raw >> 6) & 1)


def within(rect, width, height):
    return (rect['x'] >= 0 and rect['y'] >= 0 and rect['width'] > 0 and rect['height'] > 0
            and rect['x'] + rect['width'] <= width and rect['y'] + rect['height'] <= height)


def join_sprite(sprite, objects):
    tree = sprite['tree']
    atlas = resolve(sprite, tree['m_SpriteAtlas'], objects)
    route = 'sprite_render_data'
    if atlas is None and tree.get('m_AtlasTags'):
        candidates = [r for (f, _), r in objects.items() if f == sprite['serialized_file'] and r['type'] == 'SpriteAtlas' and r['tree']['m_Name'] == tree['m_AtlasTags'][0]]
        if len(candidates) != 1:
            raise ValueError('atlas tag not unique in owning file')
        atlas = candidates[0]
        route = 'owning_file_atlas_tag_and_render_key'
    data, owner = tree['m_RD'], sprite
    atlas_identity = None
    if atlas:
        if atlas['type'] != 'SpriteAtlas':
            raise ValueError('atlas pointer has wrong type')
        matches = [value for key, value in atlas['tree']['m_RenderDataMap'] if key == tree['m_RenderDataKey']]
        if len(matches) != 1:
            raise ValueError('missing/ambiguous atlas render key')
        data, owner = matches[0], atlas
        atlas_identity = dict(serialized_file=atlas['serialized_file'], path_id=atlas['path_id'], name=atlas['tree']['m_Name'])
        if route == 'sprite_render_data':
            route = 'atlas_pointer_and_render_key'
    texture = resolve(owner, data['texture'], objects)
    if texture is None or texture['type'] != 'Texture2D':
        raise ValueError('render texture missing/wrong type')
    alpha = resolve(owner, data['alphaTexture'], objects)
    if alpha and alpha['type'] != 'Texture2D':
        raise ValueError('alpha texture wrong type')
    dimensions = [texture['tree']['m_Width'], texture['tree']['m_Height']]
    return dict(serialized_file=sprite['serialized_file'], path_id=sprite['path_id'], name=tree['m_Name'],
                object_bytes_sha256=sprite['object_bytes_sha256'], route=route, atlas=atlas_identity,
                texture=dict(serialized_file=texture['serialized_file'], path_id=texture['path_id'], name=texture['tree']['m_Name'], dimensions=dimensions),
                alpha_texture=None if alpha is None else dict(serialized_file=alpha['serialized_file'], path_id=alpha['path_id']),
                source_rect=tree['m_Rect'], pivot=tree['m_Pivot'], border=tree['m_Border'],
                pixels_to_units=tree['m_PixelsToUnits'], texture_rect=data['textureRect'],
                texture_rect_offset=data['textureRectOffset'], atlas_rect_offset=data.get('atlasRectOffset'),
                uv_transform=data['uvTransform'], downscale_multiplier=data['downscaleMultiplier'],
                settings=settings(data['settingsRaw']), rect_within_texture=within(data['textureRect'], *dimensions),
                # Mesh/mask information is present in raw; a rectangle alone is not a reconstructed sprite.
                mesh_vertices=tree['m_RD']['m_VertexData']['m_VertexCount'])


def build():
    index, rows, sources = load_objects()
    objects = {}
    for row in rows:
        key = (row['serialized_file'], row['path_id'])
        if key in objects:
            raise ValueError('duplicate scoped object identity')
        objects[key] = row
    sprites, unresolved = [], []
    for row in rows:
        if row['type'] != 'Sprite':
            continue
        try:
            sprites.append(join_sprite(row, objects))
        except ValueError as exc:
            unresolved.append(dict(serialized_file=row['serialized_file'], path_id=row['path_id'], reason=str(exc)))
    return dict(status='PROVISIONAL_GEOMETRY_JOINS_NOT_PIXEL_CROP_VALIDATION', inputs_sha256=index['inputs_sha256'],
                sources=sources, object_counts=index['counts'], resolved=len(sprites), unresolved=unresolved,
                routes=dict(Counter(r['route'] for r in sprites)),
                rotation_codes=dict(Counter(str(r['settings']['packing_rotation']) for r in sprites)),
                packed_count=sum(r['settings']['packed'] for r in sprites),
                rect_outside=[dict(serialized_file=r['serialized_file'], path_id=r['path_id']) for r in sprites if not r['rect_within_texture']],
                sprites=sprites)


if __name__ == '__main__':
    result = build()
    with gzip.GzipFile(filename=str(RAW / 'resolved-geometry.json.gz'), mode='wb', mtime=0) as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2).encode())
    print(json.dumps({k: v for k, v in result.items() if k not in ('sprites', 'sources')}, indent=2))
    assert not result['unresolved'], 'Do not claim all sprites joined'
