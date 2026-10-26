"""#7 actual original builtin meshes + seeded-schema/byte-layout counterexamples.
provenance: arena/8141386a-windwings-space-shooter-game-p
Only two small Mesh fixtures, not all Sprite/Graph/bundle data.
"""
from copy import deepcopy
import gzip
import json
import struct
import unittest
from tools.verify.geometry_8141386a_atlas_io import canonical,sha
from tools.verify.l3_geometry_8141386a_builtin import build,OUTPUT,WITNESS
from tools.verify.l3_geometry_8141386a_builtin_mesh import corroborate,decode,payload,normalize_capture


def small_mesh(pid):
    w=json.loads(gzip.decompress(WITNESS.read_bytes()))
    return next(m for m in w['external_resource']['selected_meshes'] if m['path_id']==pid)


class BuiltinActual(unittest.TestCase):
    def test_reproduction_and_seven_resolutions(self):
        v=build();self.assertEqual(v,json.loads(gzip.decompress(OUTPUT.read_bytes())))
        self.assertEqual(v['summary']['resolved_original_builtin_refs'],7)
        self.assertEqual(v['summary']['target_path_id_histogram'],{'10210':6,'10202':1})
        self.assertEqual(v['summary']['mesh_fully_consumed_bytes'],2428)
        self.assertEqual(v['summary']['mesh_vertices'],28);self.assertEqual(v['summary']['mesh_indices'],42)
        self.assertEqual(v['summary']['differences'],0)

    def test_actual_apk_file_falsifies_bundle_only_absence(self):
        v=build();self.assertIn('FALSIFIED',v['initial_hypothesis']['conclusion'])
        self.assertEqual(v['source']['standalone_apk_entry'],'assets/bin/Data/unity default resources')
        self.assertEqual(v['source']['standalone_declared_unity_version'],'2022.3.54f1')
        for r in v['references']:
            self.assertEqual(r['resolution']['status'],'RESOLVED_ORIGINAL_STANDALONE_MESH')
            self.assertEqual(r['original_pointer_span']['size'],12)
            self.assertEqual(r['original_pointer_span']['hex'],struct.pack('<iq',r['pointer']['m_FileID'],r['pointer']['m_PathID']).hex())
            self.assertIsNone(r['runtime_use']);self.assertIsNone(r['scene_vertices']);self.assertIsNone(r['runtime_bounds'])

    def test_original_quad_is_not_an_idealized_z_zero_substitute(self):
        m=small_mesh(10210);g=corroborate(m)['geometry']
        self.assertEqual(m['tree']['m_Name'],'Quad');self.assertEqual(g['vertex_count'],4)
        self.assertEqual(g['index_count'],6)
        self.assertEqual(g['minimum'],[-.5,-.5,-3.0616168005906746e-17])
        self.assertEqual(g['maximum'],[.5,.5,3.0616168005906746e-17])
        self.assertTrue(any(p[2]!=0 for p in g['positions']))

    def test_original_cube_retains_face_vertices_and_uv1(self):
        m=small_mesh(10202);g=corroborate(m)['geometry']
        self.assertEqual(m['tree']['m_Name'],'Cube');self.assertEqual(g['vertex_count'],24)
        self.assertEqual(g['index_count'],36);self.assertIn('5',g['channels'])
        self.assertEqual(g['minimum'],[-.5,-.5,-.5]);self.assertEqual(g['maximum'],[.5,.5,.5])
        self.assertEqual(len({tuple(p) for p in g['positions']}),8)

    def test_whole_mesh_decode_and_typed_aabb_spans(self):
        for pid,offset in ((10202,1756),(10210,544)):
            m=small_mesh(pid);p=corroborate(m);b=bytes.fromhex(m['original_hex'])
            self.assertEqual(p['shared_schema_decode']['fully_consumed_bytes'],len(b))
            self.assertTrue(p['shared_schema_decode']['captured_tree_equal'])
            a=next(r for r in p['typed_root_spans'] if r['field']=='m_LocalAABB')
            self.assertEqual(a['offset'],offset);self.assertEqual(a['size'],24)
            self.assertEqual(a['sha256'],sha(b[offset:offset+24]))
            for spans in p['original_payload_spans'].values():self.assertEqual(len(spans),1)

    def test_corrupted_original_or_fabricated_name_rejected(self):
        m=small_mesh(10210);m['original_hex']='ff'+m['original_hex'][2:]
        with self.assertRaises(ValueError):corroborate(m)
        m=small_mesh(10210);m['tree']['m_Name']='GuessedQuad'
        with self.assertRaises(ValueError):corroborate(m)

    def test_supplied_schema_pin_and_whole_extent_are_required(self):
        m=small_mesh(10202);m['schema_sha256']='0'*64
        with self.assertRaises(ValueError):corroborate(m)
        m=small_mesh(10202);b=bytes.fromhex(m['original_hex'])[:-4];m.update(original_hex=b.hex(),object_sha256=sha(b),byte_size=len(b))
        with self.assertRaises(ValueError):corroborate(m)

    def test_external_compressed_or_unknown_channels_fail_closed(self):
        for mutation in ('stream','compression','format'):
            t=deepcopy(small_mesh(10210)['tree'])
            if mutation=='stream':t['m_StreamData']['size']=16
            elif mutation=='compression':t['m_MeshCompression']=1
            else:t['m_VertexData']['m_Channels'][0]['format']=1
            with self.assertRaises(ValueError):decode(t)

    def test_index_and_submesh_tampering_rejected(self):
        t=deepcopy(small_mesh(10210)['tree']);t['m_SubMeshes'][0]['indexCount']=7
        with self.assertRaises(ValueError):decode(t)
        t=deepcopy(small_mesh(10210)['tree']);t['m_SubMeshes'][0]['baseVertex']=1
        with self.assertRaises(ValueError):decode(t)
        t=deepcopy(small_mesh(10210)['tree']);t['m_IndexFormat']=3
        with self.assertRaises(ValueError):decode(t)

    def test_synthetic_uint32_layout_fixture_not_original_geometry_claim(self):
        t=deepcopy(small_mesh(10210)['tree']);want=decode(t)
        indexes=[v[0] for v in struct.iter_unpack('<H',payload(t['m_IndexBuffer']))]
        t['m_IndexFormat']=1;t['m_IndexBuffer']=list(struct.pack('<'+'I'*len(indexes),*indexes))
        got=decode(t);self.assertEqual(got['positions'],want['positions']);self.assertEqual(got['triangles'],want['triangles'])

    def test_vertex_extent_nan_and_index_gap_are_rejected(self):
        t=deepcopy(small_mesh(10210)['tree']);t['m_VertexData']['m_VertexCount']+=1
        with self.assertRaises(ValueError):decode(t)
        t=deepcopy(small_mesh(10210)['tree']);b=bytearray(payload(t['m_VertexData']['m_DataSize']));b[:4]=struct.pack('<f',float('nan'));t['m_VertexData']['m_DataSize']=list(b)
        with self.assertRaises(ValueError):decode(t)
        t=deepcopy(small_mesh(10210)['tree']);t['m_SubMeshes'][0]['firstByte']=2
        with self.assertRaises(ValueError):decode(t)


if __name__=='__main__':unittest.main()
