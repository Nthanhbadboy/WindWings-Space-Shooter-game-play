"""#7 streamed grep and scoped resolver counterexamples, not engine mesh guesses.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from collections import Counter
import gzip
import struct
import unittest
from tools.verify.geometry_8141386a_atlas_io import canonical
from tools.verify.geometry_8141386a_builtin_sources import load,select,SELECTED,DEFAULT_PATH
from tools.verify.l3_geometry_8141386a_builtin_binary import pointer_spans,packaged_target


class BuiltinSources(unittest.TestCase):
    def test_streamed_selection_reproduction(self):
        self.assertEqual(select(),load())

    def test_actual_particle_reference_scope(self):
        v=load()
        self.assertEqual(v['summary'],dict(ParticleSystemRenderer=954,nonnull_mesh_refs=17,builtin_mesh_refs=7,other_mesh_refs=10))
        self.assertEqual(len(v['records']),7)
        self.assertEqual(Counter(r['refs'][0]['pointer']['m_PathID'] for r in v['records']),{10210:6,10202:1})
        self.assertEqual(Counter(r['record']['tree']['m_RenderMode'] for r in v['records']),{1:4,0:3})

    def test_each_original_capture_link_is_unresolved_not_default_replaced(self):
        v=load()
        for r in v['original_unresolved_links']:
            self.assertEqual(r['record']['status'],'unresolved')
            self.assertIn('FileNotFoundError',r['record']['error'])
        self.assertTrue(all(r['refs'][0]['external_path']==DEFAULT_PATH for r in v['records']))

    def test_seeded_pointer_byte_matches_keep_ambiguity(self):
        p=dict(m_FileID=2,m_PathID=10210);b=struct.pack('<iq',2,10210)
        one=pointer_spans(b'\xff'*4+b+b'\xfe'*4,p)
        self.assertTrue(one['unique_aligned_match']);self.assertEqual(one['aligned_candidates'][0]['offset'],4)
        two=pointer_spans(b+b,p)
        self.assertFalse(two['unique_aligned_match']);self.assertEqual(len(two['aligned_candidates']),2)
        self.assertEqual(pointer_spans(b'\xff'+b,p)['aligned_candidates'],[])
        self.assertEqual(pointer_spans(b'\xff'*40,p)['aligned_candidates'],[])

    def test_absent_file_proof_does_not_invent_mesh_or_vertex_bounds(self):
        d=packaged_target(DEFAULT_PATH,10210,[dict(path='resources.assets')],[])
        self.assertEqual(d['status'],'NOT_PRESENT_AS_BUNDLE_NODE');self.assertIsNone(d['geometry'])
        self.assertIn('engine builtin',d['missing'])

    def test_packaged_exact_target_counterexample_is_not_false_absence(self):
        nodes=[dict(path=DEFAULT_PATH)]
        files=[dict(serialized_file='data.unity3d/'+DEFAULT_PATH,mesh_objects=[dict(path_id=10210,class_id=43)])]
        self.assertEqual(packaged_target(DEFAULT_PATH,10210,nodes,files)['status'],'PACKAGED_MESH_TARGET_REQUIRES_DECODE')
        self.assertIsNone(packaged_target(DEFAULT_PATH,10210,nodes,files)['geometry'])

    def test_same_pathid_other_file_is_not_a_resolution(self):
        files=[dict(serialized_file='data.unity3d/resources.assets',mesh_objects=[dict(path_id=10210,class_id=43)])]
        self.assertEqual(packaged_target(DEFAULT_PATH,10210,[dict(path='resources.assets')],files)['status'],'NOT_PRESENT_AS_BUNDLE_NODE')

    def test_present_file_without_matching_mesh_stays_unknown(self):
        nodes=[dict(path=DEFAULT_PATH)];files=[dict(serialized_file='data.unity3d/'+DEFAULT_PATH,mesh_objects=[])]
        self.assertEqual(packaged_target(DEFAULT_PATH,10210,nodes,files)['status'],'NO_MESH_AT_EXACT_FILE_AND_PATH_ID')
        with self.assertRaises(ValueError):packaged_target(DEFAULT_PATH,10210,nodes,[])


if __name__=='__main__':unittest.main()
