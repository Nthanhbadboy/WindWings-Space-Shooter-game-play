"""Seeded inverse serialization + narrow static vertex decoder for geometry #6.
provenance: arena/8141386a-windwings-space-shooter-game-p
Field order/layout is consulted from inherited UnityPy 1.25.4 full typetrees and
sprite-mesh/MeshHelper conventions. Exact original-object SHA equality is required;
this is byte corroboration, NOT clean-room schema discovery or native execution.
"""
from __future__ import annotations
import base64
import math
import struct

from tools.verify.geometry_8141386a_atlas_io import sha


class Bytes:
    def __init__(self):
        self.data = bytearray()
        self.spans = {}

    def add(self, value, name=None):
        start = len(self.data)
        self.data.extend(value)
        if name:
            self.spans[name] = dict(offset=start, size=len(value), sha256=sha(value))

    def pack(self, fmt, *values, name=None):
        self.add(struct.pack('<' + fmt, *values), name)

    def align(self):
        self.add(b'\0' * (-len(self.data) % 4))

    def string(self, text, name=None):
        start = len(self.data)
        encoded = text.encode('utf-8')
        self.pack('i', len(encoded))
        self.add(encoded)
        self.align()
        if name:
            self.spans[name] = dict(offset=start, size=len(self.data)-start,
                                    sha256=sha(self.data[start:]))

    def floats(self, value, axes, name=None):
        self.pack('f' * len(axes), *(value[x] for x in axes), name=name)

    def pointer(self, value, name=None):
        self.pack('iq', value['m_FileID'], value['m_PathID'], name=name)

    def render_key(self, value, name=None):
        guid, local = value
        self.pack('4Iq', *(guid[f'data[{i}]'] for i in range(4)), local, name=name)

    def byte_array(self, value, name):
        self.pack('i', len(value), name=name + '.count')
        self.add(value, name)
        self.align()

    def finish(self):
        return bytes(self.data), self.spans


def secondary(b, items):
    if items:
        raise ValueError('nonempty secondary texture layout outside corroborated domain')
    b.pack('i', 0)


def sprite_bytes(t):
    if t['m_Bones'] or t['m_RD']['m_Bindpose']:
        raise ValueError('nonempty bones/bindpose outside corroborated empty-array domain')
    b = Bytes()
    b.string(t['m_Name'], 'm_Name')
    b.floats(t['m_Rect'], ('x', 'y', 'width', 'height'), 'm_Rect')
    b.floats(t['m_Offset'], 'xy', 'm_Offset')
    b.floats(t['m_Border'], 'xyzw', 'm_Border')
    b.pack('f', t['m_PixelsToUnits'], name='m_PixelsToUnits')
    b.floats(t['m_Pivot'], 'xy', 'm_Pivot')
    b.pack('I', t['m_Extrude'])
    b.pack('?', t['m_IsPolygon'])
    b.align()
    b.render_key(t['m_RenderDataKey'], 'm_RenderDataKey')
    b.pack('i', len(t['m_AtlasTags']))
    for tag in t['m_AtlasTags']:
        b.string(tag)
    b.pointer(t['m_SpriteAtlas'], 'm_SpriteAtlas')
    rd = t['m_RD']
    b.pointer(rd['texture'], 'm_RD.texture')
    b.pointer(rd['alphaTexture'], 'm_RD.alphaTexture')
    secondary(b, rd['secondaryTextures'])
    b.pack('i', len(rd['m_SubMeshes']))
    for i, sub in enumerate(rd['m_SubMeshes']):
        b.pack('6I', *(sub[k] for k in ('firstByte', 'indexCount', 'topology',
                                       'baseVertex', 'firstVertex', 'vertexCount')))
        start = len(b.data)
        b.floats(sub['localAABB']['m_Center'], 'xyz')
        b.floats(sub['localAABB']['m_Extent'], 'xyz')
        b.spans[f'm_RD.m_SubMeshes[{i}].localAABB'] = dict(
            offset=start, size=24, sha256=sha(b.data[start:]))
    b.byte_array(bytes(rd['m_IndexBuffer']), 'm_RD.m_IndexBuffer')
    vd = rd['m_VertexData']
    b.pack('I', vd['m_VertexCount'], name='m_RD.m_VertexData.m_VertexCount')
    start = len(b.data)
    b.pack('i', len(vd['m_Channels']))
    for channel in vd['m_Channels']:
        b.pack('4B', *(channel[k] for k in ('stream', 'offset', 'format', 'dimension')))
    b.spans['m_RD.m_VertexData.m_Channels'] = dict(
        offset=start, size=len(b.data)-start, sha256=sha(b.data[start:]))
    b.byte_array(vertex_payload(vd), 'm_RD.m_VertexData.m_DataSize')
    b.pack('i', 0, name='m_RD.m_Bindpose.count')
    b.floats(rd['textureRect'], ('x', 'y', 'width', 'height'))
    b.floats(rd['textureRectOffset'], 'xy')
    b.floats(rd['atlasRectOffset'], 'xy')
    b.pack('I', rd['settingsRaw'])
    b.floats(rd['uvTransform'], 'xyzw')
    b.pack('f', rd['downscaleMultiplier'])
    b.pack('i', len(t['m_PhysicsShape']))
    for points in t['m_PhysicsShape']:
        b.pack('i', len(points))
        for point in points:
            b.floats(point, 'xy')
    b.pack('i', 0, name='m_Bones.count')
    return b.finish()


def atlas_bytes(t):
    b = Bytes()
    b.string(t['m_Name'], 'm_Name')
    start = len(b.data)
    b.pack('i', len(t['m_PackedSprites']))
    for pointer in t['m_PackedSprites']:
        b.pointer(pointer)
    b.spans['m_PackedSprites'] = dict(offset=start, size=len(b.data)-start,
                                     sha256=sha(b.data[start:]))
    start = len(b.data)
    b.pack('i', len(t['m_PackedSpriteNamesToIndex']))
    for name in t['m_PackedSpriteNamesToIndex']:
        b.string(name)
    b.spans['m_PackedSpriteNamesToIndex'] = dict(offset=start, size=len(b.data)-start,
                                              sha256=sha(b.data[start:]))
    start = len(b.data)
    b.pack('i', len(t['m_RenderDataMap']))
    for i, (render_key, rd) in enumerate(t['m_RenderDataMap']):
        entry_start = len(b.data)
        b.render_key(render_key)
        b.pointer(rd['texture'])
        b.pointer(rd['alphaTexture'])
        b.floats(rd['textureRect'], ('x', 'y', 'width', 'height'))
        b.floats(rd['textureRectOffset'], 'xy')
        b.floats(rd['atlasRectOffset'], 'xy')
        b.floats(rd['uvTransform'], 'xyzw')
        b.pack('fI', rd['downscaleMultiplier'], rd['settingsRaw'])
        secondary(b, rd['secondaryTextures'])
        b.spans[f'm_RenderDataMap[{i}]'] = dict(offset=entry_start,
                                               size=len(b.data)-entry_start,
                                               sha256=sha(b.data[entry_start:]))
    b.spans['m_RenderDataMap'] = dict(offset=start, size=len(b.data)-start,
                                     sha256=sha(b.data[start:]))
    b.string(t['m_Tag'])
    b.pack('?', t['m_IsVariant'])
    b.align()
    return b.finish()


def encoded_object(row):
    if row['type'] == 'Sprite':
        blob, spans = sprite_bytes(row['tree'])
    elif row['type'] == 'SpriteAtlas':
        blob, spans = atlas_bytes(row['tree'])
    else:
        return None, {}
    if sha(blob) != row['object_bytes_sha256']:
        raise ValueError('inverse serialization NOT original-hash-equal: ' + str(
            (row['serialized_file'], row['path_id'], row['type'], len(blob), sha(blob))))
    return blob, spans


def vertex_payload(vd):
    value = vd['m_DataSize']
    if value.get('encoding') != 'base64':
        raise ValueError('vertex payload encoding')
    return base64.b64decode(value['bytes_base64'], validate=True)


def decode_mesh(rd):
    """Independent small layout implementation; same disclosed layout convention as mesh75."""
    vd = rd['m_VertexData']
    n = vd['m_VertexCount']
    layout = [(i, c['stream'], c['offset'], c['format'], c['dimension'])
              for i, c in enumerate(vd['m_Channels']) if c['dimension']]
    if layout != [(0, 0, 0, 0, 3), (4, 1, 0, 0, 2)] or not 3 <= n <= 100000:
        raise ValueError('unsupported static Sprite vertex layout/count')
    payload = vertex_payload(vd)
    uv_start = (n * 12 + 15) // 16 * 16
    if len(payload) != uv_start + n * 8:
        raise ValueError('static Sprite payload extent')
    positions = [list(v) for v in struct.iter_unpack('<3f', payload[:n*12])]
    uvs = [list(v) for v in struct.iter_unpack('<2f', payload[uv_start:])]
    if not all(math.isfinite(x) for values in positions + uvs for x in values):
        raise ValueError('nonfinite static Sprite payload')
    indexes = bytes(rd['m_IndexBuffer'])
    triangles = []
    ranges = []
    for sub in rd['m_SubMeshes']:
        first, count = sub['firstByte'], sub['indexCount']
        if sub['topology'] != 0 or sub['baseVertex'] != 0 or count % 3 or first % 2:
            raise ValueError('unsupported Sprite triangle topology/base/offset')
        if first < 0 or first + count*2 > len(indexes):
            raise ValueError('index submesh extent')
        values = list(struct.iter_unpack('<3H', indexes[first:first+count*2]))
        if any(i >= n for tri in values for i in tri):
            raise ValueError('index out of vertex bounds')
        if not 0 <= sub['firstVertex'] <= sub['firstVertex'] + sub['vertexCount'] <= n:
            raise ValueError('submesh vertex extent')
        ranges.append((first, first + count*2))
        triangles.extend(list(t) for t in values)
    if not ranges or sorted(ranges)[0][0] != 0 or sorted(ranges)[-1][1] != len(indexes):
        raise ValueError('index buffer not fully covered')
    if any(a[1] != b[0] for a, b in zip(sorted(ranges), sorted(ranges)[1:])):
        raise ValueError('index buffer overlap/gap')
    minimum = [min(v[i] for v in positions) for i in range(3)]
    maximum = [max(v[i] for v in positions) for i in range(3)]
    return dict(positions=positions, source_uv0=uvs, triangles=triangles,
                vertex_count=n, index_count=sum(len(t) for t in triangles),
                minimum=minimum, maximum=maximum,
                span=[b-a for a, b in zip(minimum, maximum)],
                vertex_payload_sha256=sha(payload), index_payload_sha256=sha(indexes),
                stored_uv0_all_zero=all(v == 0 for uv in uvs for v in uv))
