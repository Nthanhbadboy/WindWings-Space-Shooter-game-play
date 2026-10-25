import gzip,json,unittest
from tools.verify.ui_l3_bindings import build,OUT,match
class DrawingBindings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=json.loads(gzip.decompress(OUT.read_bytes()))
    def test_regenerates(self):self.assertEqual(build(),self.data)
    def test_inventory_not_coverage(self):self.assertEqual(self.data['inventory'],dict(layout_files_present=55584,indexed_files=797,unindexed_files=54787))
    def test_sources_preserved(self):self.assertEqual(len(self.data['sources']),797);self.assertTrue(all(len(s['sha256'])==64 for s in self.data['sources']))
    def test_observation_count_not_unique_sprites(self):self.assertEqual(len(self.data['uses']),76806);self.assertEqual(self.data['counts']['resolved_exact_scoped_pptr'],75749)
    def test_null_not_missing_or_visible(self):self.assertEqual(self.data['counts']['null'],1057)
    def test_every_exact_binding_file_scoped(self):
        for u in self.data['uses']:
            if u['sprite']['status']=='resolved_exact_scoped_pptr':self.assertTrue(u['sprite']['target_file']);self.assertIn('path_id',u['sprite']);self.assertNotIn('visible',u)
    def test_unique_identity_coverage(self):self.assertEqual(len({(u['sprite']['target_file'],u['sprite']['path_id']) for u in self.data['uses'] if u['sprite']['status']=='resolved_exact_scoped_pptr'}),1099)
    def test_name_unique_never_exact(self):self.assertEqual(match({},dict(sprite='x'),[],{'x':[dict(serialized_file='a',path_id=1)]},{})['status'],'name_candidate_only')
    def test_name_duplicate_not_first_wins(self):self.assertEqual(match({},dict(sprite='x'),[],{'x':[1,2]},{})['status'],'ambiguous_name')
    def test_name_missing_not_invented(self):self.assertEqual(match({},dict(sprite='x'),[],{},{})['status'],'name_not_in_scoped_catalog')
    def test_pptr_without_scope_not_name_fallback(self):self.assertEqual(match({},dict(sprite='x',visual_properties={'m_Sprite':{'m_FileID':0,'m_PathID':1}}),[],{'x':[1]},{})['status'],'owner_scope_missing')
    def test_null_pptr_not_name_fallback(self):self.assertEqual(match({},dict(sprite='x',visual_properties={'m_Sprite':{'m_FileID':0,'m_PathID':0}}),[],{'x':[1]},{})['status'],'null')
