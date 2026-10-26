"""#6 independent static atlas/bounds replication + byte-witness counterexamples.
provenance: arena/8141386a-windwings-space-shooter-game-p
No whole-dataset fixture. Original sources and artifact arrays are streamed by row.
"""
from collections import Counter
from copy import deepcopy
import struct
import unittest

from tools.verify.geometry_8141386a_atlas_io import (
    RAW, canonical, identity, iter_arrays, iter_geometry, key, scratch, sha_file,
)
from tools.verify.l3_geometry_8141386a_atlas import (
    OUT, WITNESS, build, document_header, field_differences, render_key,
    resolve, static_zero, validate_witness,
)


def one(typ):
    return next(r for r, _ in iter_geometry() if r['type'] == typ)


def witness_for(row):
    return next(w for _, _, w in iter_arrays(WITNESS, {'objects'}) if key(w['identity']) == key(row))


class AtlasJoinPolicyTests(unittest.TestCase):
    def test_complete_key_is_guid_plus_local_id_not_name_or_partial_guid(self):
        k = [{'data[0]': 1, 'data[1]': 2, 'data[2]': 3, 'data[3]': 4}, 21300000]
        text = render_key(k)
        for i in range(4):
            changed = deepcopy(k)
            changed[0][f'data[{i}]'] += 1
            self.assertNotEqual(render_key(changed), text)
        changed = deepcopy(k)
        changed[1] += 1
        self.assertNotEqual(render_key(changed), text)
        reordered = [dict(reversed(list(k[0].items()))), k[1]]
        self.assertEqual(render_key(reordered), text)

    def test_malformed_guid_and_noninteger_key_reject(self):
        for value in (None, [dict(x=1), 1], [{'data[0]': 0, 'data[1]': 0, 'data[2]': 0, 'data[3]': 2**32}, 1],
                      [{'data[0]': 0, 'data[1]': 0, 'data[2]': 0, 'data[3]': 0}, 1.0]):
            with self.assertRaises(ValueError):
                render_key(value)

    def test_local_and_external_pptr_use_exact_owning_file(self):
        files = {'data.unity3d/a.assets', 'data.unity3d/b.assets'}
        ext = [dict(file_id=1, path='b.assets')]
        self.assertEqual(resolve('a.assets', ext, dict(m_FileID=0, m_PathID=7), files), ('data.unity3d/a.assets', 7))
        self.assertEqual(resolve('a.assets', ext, dict(m_FileID=1, m_PathID=7), files), ('data.unity3d/b.assets', 7))

    def test_no_basename_fallback_for_uncaptured_file(self):
        with self.assertRaisesRegex(ValueError, 'not captured'):
            resolve('a.assets', [dict(file_id=1, path='Library/unity default resources')],
                    dict(m_FileID=1, m_PathID=10202), {'data.unity3d/a.assets', 'other/unity default resources'})

    def test_ambiguous_invalid_external_pointer_rejects(self):
        files = {'data.unity3d/a.assets', 'data.unity3d/b.assets'}
        for ext, pointer in (([], dict(m_FileID=1, m_PathID=7)),
                             ([dict(file_id=1, path='a.assets'), dict(file_id=1, path='b.assets')], dict(m_FileID=1, m_PathID=7)),
                             ([], dict(m_FileID=-1, m_PathID=7))):
            with self.assertRaises(ValueError):
                resolve('a.assets', ext, pointer, files)

    def test_null_pointer_stays_null_not_a_default_mesh_or_texture(self):
        self.assertIsNone(resolve('a.assets', [], dict(m_FileID=0, m_PathID=0), {'data.unity3d/a.assets'}))

    def test_canonical_comparison_exposes_signed_zero_and_missing_null(self):
        diffs = field_differences(dict(x=-0.0, nullable=None), dict(x=0.0))
        self.assertEqual({d['field'] for d in diffs}, {'x', 'nullable'})
        self.assertEqual(field_differences(dict(x=[1.25]), dict(x=[1.25])), [])

    def test_serialized_zero_aabb_remains_distinct_from_static_vertex_bounds(self):
        row = one('Sprite')
        self.assertTrue(static_zero(row['tree']['m_RD']['m_SubMeshes']))
        changed = deepcopy(row['tree']['m_RD']['m_SubMeshes'])
        changed[0]['localAABB']['m_Extent']['x'] = 1
        self.assertFalse(static_zero(changed))
        self.assertFalse(static_zero([]))


class AtlasOriginalWitnessTests(unittest.TestCase):
    def test_source_witness_is_original_not_vehicle_or_runtime(self):
        header = document_header(WITNESS)
        self.assertEqual(header['item'], 6)
        self.assertEqual(header['bundle_sha256'], '7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7')
        self.assertIn('NOT native', header['scope'])
        self.assertTrue(header['files'])

    def test_complete_original_sprite_and_atlas_spans(self):
        for typ in ('Sprite', 'SpriteAtlas'):
            row = one(typ)
            validate_witness(row, witness_for(row))

    def test_forged_original_hash_is_not_accepted(self):
        row = one('Sprite')
        w = witness_for(row)
        w['object_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'fresh original SHA'):
            validate_witness(row, w)

    def test_span_hex_corruption_and_missing_span_fail_closed(self):
        row = one('Sprite')
        w = witness_for(row)
        w['spans']['m_RD.m_VertexData.m_DataSize']['hex'] = 'ff'
        with self.assertRaisesRegex(ValueError, 'span hex invalid'):
            validate_witness(row, w)
        w = witness_for(row)
        del w['spans']['m_Bones.count']
        with self.assertRaisesRegex(ValueError, 'span extent'):
            validate_witness(row, w)

    def test_original_empty_counts_are_scoped_and_typed(self):
        row = one('Sprite')
        w = witness_for(row)
        for field in ('m_Bones.count', 'm_RD.m_Bindpose.count'):
            self.assertEqual(struct.unpack('<i', bytes.fromhex(w['spans'][field]['hex']))[0], 0)
        w['empty_counts_read_from_original']['m_Bones.count'] = 1
        with self.assertRaisesRegex(ValueError, 'empty counts'):
            validate_witness(row, w)

    def test_texture_hash_only_is_not_falsely_claimed_reencoded(self):
        row = one('Texture2D')
        w = witness_for(row)
        validate_witness(row, w)
        w['whole_inverse_serialization_byte_equal'] = True
        with self.assertRaisesRegex(ValueError, 'hash-only Texture2D'):
            validate_witness(row, w)


class AtlasArtifactTests(unittest.TestCase):
    def test_full_streaming_reproduction_and_all_pins(self):
        with scratch('test-artifact-') as directory:
            h = build(directory/'artifact.gz')
            self.assertEqual(sha_file(directory/'artifact.gz'), sha_file(OUT))
            self.assertEqual(h['summary']['differences'], 0)

    def test_all_static_sprite_array_invariants_and_no_runtime_deformation(self):
        counts = Counter()
        for _, _, r in iter_arrays(OUT, {'sprites'}):
            positions = r['source_positions']
            b = r['bounds']
            self.assertEqual(len(positions), b['vertex_count'])
            self.assertEqual([min(p[i] for p in positions) for i in range(3)], b['minimum'])
            self.assertEqual([max(p[i] for p in positions) for i in range(3)], b['maximum'])
            self.assertTrue(all(0 <= i < len(positions) for t in r['triangle_indices'] for i in t))
            self.assertEqual(r['bones'], 0)
            self.assertEqual(r['bindposes'], 0)
            self.assertIsNone(r['live_remap'])
            self.assertIsNone(r['runtime_deformed_bounds'])
            self.assertIn('not runtime-deformed', r['bounds_scope'])
            self.assertEqual(r['active_channels'], [0, 4])
            self.assertTrue(r['serialized_submesh_zero'])
            counts['vertices'] += len(positions)
            counts['indices'] += sum(len(t) for t in r['triangle_indices'])
            counts['sprites'] += 1
            counts[r['route']] += 1
        self.assertEqual(counts, dict(vertices=27072, indices=73125, sprites=2185,
                                     atlas_pointer_and_exact_render_data_key=1550, direct_sprite_render_data=635))

    def test_all_static_atlas_pointers_and_maps_reconcile(self):
        atlas_count = packed = names = entries = 0
        for _, _, a in iter_arrays(OUT, {'atlases'}):
            atlas_count += 1
            packed += a['packed_count']
            names += a['names_count']
            entries += a['map_count']
            self.assertTrue(a['names_match'])
        self.assertEqual((atlas_count, packed, names, entries), (66, 1550, 1550, 1550))
        h = document_header(OUT, 'atlases')
        self.assertEqual(h['summary']['unmatched_packed_pointers'], 0)
        self.assertEqual(h['summary']['unmatched_atlas_map_rows'], 0)
        self.assertEqual(h['summary']['bound_texture_pointer_resolutions'], 2185)

    def test_primary_and_mesh_comparisons_all_match_without_using_peer_as_source(self):
        counts = Counter()
        for _, _, r in iter_arrays(OUT, {'comparisons'}):
            self.assertTrue(r['matched'])
            counts[r['comparison_kind']] += 1
        self.assertEqual(counts, dict(primary_atlas=66, primary_bounds=2185, primary_mapping=1550, mesh75=2185))
        self.assertEqual(list(iter_arrays(OUT, {'differences'})), [])
        self.assertIn('NOT live-remapped', document_header(OUT, 'atlases')['boundary'])

    def test_raw102_overlap_is_disclosed_and_streamed(self):
        counts = Counter()
        for _, _, r in iter_arrays(OUT, {'raw102_crosschecks'}):
            self.assertTrue(r['matched'])
            counts[r['type']] += 1
        self.assertEqual(counts, dict(Sprite=1389, SpriteAtlas=44))
        h = document_header(OUT, 'atlases')
        self.assertIn('Shared raw', h['lineage'])
        self.assertIn('not independent schema discovery', h['lineage'])

    def test_remaining_native_inputs_are_explicit_not_a_global_absence_claim(self):
        h = document_header(OUT, 'atlases')
        self.assertEqual(len(h['missing_for_native_closure']), 2)
        self.assertIn('actual state/instance', h['missing_for_native_closure'][0])
        self.assertIn('Empty arrays only describe', h['missing_for_native_closure'][1])
        self.assertEqual(h['primary_comparison']['handoff_comment'], 6416037439)


if __name__ == '__main__':
    unittest.main()
