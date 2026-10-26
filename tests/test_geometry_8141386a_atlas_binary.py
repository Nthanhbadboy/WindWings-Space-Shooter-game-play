"""Geometry #6 source-layout/streaming tests, not native remap/skinning acceptance.
provenance: arena/8141386a-windwings-space-shooter-game-p
Fixtures select ONE source tree at a time; no full Graph/dataset fixture.
"""
import base64
from collections import Counter, OrderedDict
from copy import deepcopy
import io
import json
import struct
import unittest

from tools.verify.geometry_8141386a_atlas_io import (
    RAW, JsonStream, iter_arrays, iter_arrays_handle, iter_geometry, scratch,
    sha_file, write_document,
)
from tools.verify.geometry_8141386a_atlas_sources import QUERY, PINS, build, verify_pins
from tools.verify.l3_geometry_8141386a_atlas_binary import (
    decode_mesh, encoded_object, sprite_bytes, vertex_payload,
)
from tools.recovery.geometry_8141386a_atlas_bytes import Bundle


def one_sprite():
    return next(r for r, _ in iter_geometry() if r['type'] == 'Sprite')


class AtlasSourceBinaryTests(unittest.TestCase):
    def test_full_inverse_serialization_matches_each_original_captured_hash_streamed(self):
        counts = Counter()
        for row, _ in iter_geometry():
            blob, spans = encoded_object(row)
            if blob is not None:
                counts[row['type']] += 1
                self.assertTrue(spans)
        self.assertEqual(counts, {'Sprite': 2185, 'SpriteAtlas': 66})

    def test_source_query_and_pin_determinism(self):
        with scratch('test-') as directory:
            query, pins = directory / 'q.gz', directory / 'p.json'
            value = build(query, pins)
            self.assertEqual(sha_file(query), sha_file(QUERY))
            self.assertEqual(pins.read_bytes(), PINS.read_bytes())
            self.assertEqual(value['inverse_serialization_original_hash_equal'], {'Sprite': 2185, 'SpriteAtlas': 66})
        verify_pins()

    def test_query_contains_every_identity_once(self):
        seen, counts = set(), Counter()
        for _, _, row in iter_arrays(QUERY, {'objects'}):
            k = tuple(row['identity'].values())
            self.assertNotIn(k, seen)
            seen.add(k)
            counts[row['type']] += 1
        self.assertEqual(dict(counts), json.loads(PINS.read_bytes())['source_counts'])

    def test_source_scalar_mutation_does_not_pass_object_hash(self):
        row = one_sprite()
        row['tree']['m_PixelsToUnits'] += 1
        with self.assertRaisesRegex(ValueError, 'NOT original-hash-equal'):
            encoded_object(row)

    def test_counts_have_exact_typed_offsets_in_whole_sprite(self):
        row = one_sprite()
        blob, spans = sprite_bytes(row['tree'])
        for name in ('m_Bones.count', 'm_RD.m_Bindpose.count'):
            self.assertEqual(struct.unpack_from('<i', blob, spans[name]['offset'])[0], 0)
            self.assertEqual(spans[name]['size'], 4)
        self.assertEqual(spans['m_Bones.count']['offset'] + 4, len(blob))

    def test_nonempty_bone_bindpose_domain_fails_closed(self):
        for field in ('bones', 'bindpose'):
            tree = one_sprite()['tree']
            (tree['m_Bones'] if field == 'bones' else tree['m_RD']['m_Bindpose']).append({})
            with self.assertRaisesRegex(ValueError, 'outside corroborated'):
                sprite_bytes(tree)

    def test_exact_static_positions_and_bounds_are_not_serialized_zero_aabb(self):
        row = one_sprite()
        mesh = decode_mesh(row['tree']['m_RD'])
        self.assertEqual(mesh['vertex_count'], 4)
        self.assertEqual(mesh['index_count'], 6)
        self.assertNotEqual(mesh['minimum'], mesh['maximum'])
        self.assertTrue(mesh['stored_uv0_all_zero'])
        self.assertEqual(row['tree']['m_RD']['m_SubMeshes'][0]['localAABB']['m_Center'], dict(x=0.0, y=0.0, z=0.0))

    def test_vertex_layout_and_payload_extent_fail_closed(self):
        rd = one_sprite()['tree']['m_RD']
        rd['m_VertexData']['m_Channels'][0]['dimension'] = 2
        with self.assertRaisesRegex(ValueError, 'layout/count'):
            decode_mesh(rd)
        rd = one_sprite()['tree']['m_RD']
        payload = vertex_payload(rd['m_VertexData'])[:-1]
        rd['m_VertexData']['m_DataSize']['bytes_base64'] = base64.b64encode(payload).decode()
        with self.assertRaisesRegex(ValueError, 'payload extent'):
            decode_mesh(rd)

    def test_bad_triangle_and_index_extent_fail_closed(self):
        rd = one_sprite()['tree']['m_RD']
        rd['m_IndexBuffer'][:2] = [255, 255]
        with self.assertRaisesRegex(ValueError, 'index out of vertex bounds'):
            decode_mesh(rd)
        rd = one_sprite()['tree']['m_RD']
        rd['m_SubMeshes'][0]['firstByte'] = len(rd['m_IndexBuffer'])
        with self.assertRaisesRegex(ValueError, 'index submesh extent'):
            decode_mesh(rd)

    def test_nonfinite_vertex_and_topology_fail_closed(self):
        rd = one_sprite()['tree']['m_RD']
        payload = bytearray(vertex_payload(rd['m_VertexData']))
        struct.pack_into('<f', payload, 0, float('nan'))
        rd['m_VertexData']['m_DataSize']['bytes_base64'] = base64.b64encode(payload).decode()
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            decode_mesh(rd)
        rd = one_sprite()['tree']['m_RD']
        rd['m_SubMeshes'][0]['topology'] = 1
        with self.assertRaisesRegex(ValueError, 'topology'):
            decode_mesh(rd)

    def test_source_witness_role_does_not_invent_texture_bytes(self):
        row = next(r for r, _ in iter_geometry() if r['type'] == 'Texture2D')
        self.assertEqual(encoded_object(row), (None, {}))


class AtlasStreamingTests(unittest.TestCase):
    def test_incremental_array_reads_with_one_character_chunks(self):
        source = {'header': {'x': 1}, 'skip': [{'v': i} for i in range(40)],
                  'rows': [dict(v='é中\\\"'), 1e12, -0.00025, True, None, [1, 2]]}
        rows = list(iter_arrays_handle(io.StringIO(json.dumps(source)), {'rows'}, chunk=1))
        self.assertEqual([r[2] for r in rows], source['rows'])
        self.assertEqual([r[1] for r in rows], list(range(6)))

    def test_missing_requested_array_and_trailing_content_reject(self):
        for data in ('{"other":[]}', '{"rows":[]} extra'):
            with self.assertRaises(ValueError):
                list(iter_arrays_handle(io.StringIO(data), {'rows'}, chunk=2))

    def test_duplicate_fields_and_truncated_json_reject(self):
        for data in ('{"rows":[],"rows":[]}', '{"rows":[{"x":1}', '{"rows":[1,]}'):
            with self.assertRaises(ValueError):
                list(iter_arrays_handle(io.StringIO(data), {'rows'}, chunk=3))

    def test_nonfinite_and_value_budget_reject(self):
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            list(iter_arrays_handle(io.StringIO('{"rows":[NaN]}'), {'rows'}))
        s = JsonStream(io.StringIO('"' + 'x'*100 + '"'), chunk=8, budget=32)
        with self.assertRaisesRegex(ValueError, 'budget'):
            s.value()

    def test_streamed_output_is_byte_deterministic(self):
        with scratch('test-') as directory:
            for name in ('a.gz', 'b.gz'):
                write_document(directory/name, {'header': 1},
                               [('rows', (dict(v=i) for i in range(503)))])
            self.assertEqual(sha_file(directory/'a.gz'), sha_file(directory/'b.gz'))
            self.assertEqual(sum(1 for _ in iter_arrays(directory/'a.gz', {'rows'})), 503)

    def test_synthetic_block_cache_has_fixed_sixteen_block_bound(self):
        # Synthetic uncompressed blocks, not an APK/readback fixture.
        b = Bundle.__new__(Bundle)
        b.blob = bytes(range(20)) * 32
        b.cache, b.receipts = OrderedDict(), {}
        b.cache_high_water = 0
        b.frame = dict(uncompressed_size=len(b.blob), blocks=[dict(
            index=i, physical_start=i*32, compressed_size=32,
            uncompressed_start=i*32, uncompressed_size=32, flags=0) for i in range(20)])
        for i in range(20):
            self.assertEqual(b.read(i*32, 32), b.blob[i*32:i*32+32])
        self.assertEqual(b.cache_high_water, 16)
        self.assertEqual(len(b.cache), 16)
        self.assertEqual(len(b.receipts), 20)
        self.assertEqual(b.object_hash(0, len(b.blob)), __import__('hashlib').sha256(b.blob).hexdigest())
        with self.assertRaises(ValueError):
            b.read(-1, 4)


if __name__ == '__main__':
    unittest.main()
