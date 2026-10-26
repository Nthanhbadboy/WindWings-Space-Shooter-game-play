import gzip,hashlib,json,unittest
from tools.verify import review_row16_118 as v
class ReviewRow16_118(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.a=json.load(gzip.open(v.OUT))
    def test_regenerate(self):self.assertEqual(v.build(),self.a)
    def test_claim_and_assignment(self):
        x=self.a;self.assertEqual(x['claim'],6423892767);self.assertEqual(x['assignment'],[6423276716,6423721976,6424044328]);self.assertEqual(x['target_handoff'],6423177428)
    def test_target_commit_and_shas(self):
        x=self.a;self.assertEqual(x['target_commit'],'e3fbb4dbc679c5d07ff8c520f8e13827baeae53c');self.assertEqual(x['target_artifact']['sha256'],'c33ad8a80c35990cf5dd94165234878a62785a5bb39ddef5f2bb73752408019d');self.assertEqual(len(x['target_report']['sha256']),64)
    def test_tool_pin(self):self.assertEqual(self.a['inputs']['tools/verify/review_row16_118.py'],hashlib.sha256((v.ROOT/'tools/verify/review_row16_118.py').read_bytes()).hexdigest())
    def test_source_pins(self):
        c=self.a['checks'];self.assertEqual((c['source_pins'],c['source_pin_mismatches']),(1587,0))
    def test_source_pin_dataset_counts(self):
        self.assertEqual(self.a['checks']['source_pin_dataset_counts'],dict(new_native_renderer_shards=252,geometry_8141386a_other=6,l3_chain_context=901,l3_visual_surface_context=411,sprite_geometry_catalog=7,tool_pins=10,other=0))
    def test_shards(self):
        c=self.a['checks'];self.assertEqual((c['shards'],c['shard_compressed_bytes'],c['rows'],c['last_shard_rows']),(252,14813405,62815,65));self.assertEqual(c['row_count_histogram'],{'250':251,'65':1})
    def test_unique_identities(self):
        c=self.a['checks'];self.assertEqual((c['renderer_unique'],c['gameobject_unique'],c['object_size_total']),(62815,62815,12311740))
    def test_sprite_counts(self):
        c=self.a['checks'];self.assertEqual((c['nonnull_sprites'],c['null_sprites'],c['enabled_true'],c['native_index_enabled_true']),(61864,951,62426,62426))
    def test_context_counts(self):
        c=self.a['checks'];self.assertEqual(c['source_context_counts'],{'SERIALIZED_SCENE_NOT_RUNTIME':1377,'ASSET_FILE_NOT_RUNTIME_PLACEMENT':61438});self.assertEqual((c['scene_rows'],c['asset_rows']),(1377,61438))
    def test_status_counts(self):self.assertEqual(self.a['checks']['status_counts'],{'EXACT_ORIGINAL_SPRITE_IDENTITY':61864,'NULL_SPRITE':951})
    def test_file_counts(self):self.assertEqual(self.a['checks']['native_file_counts'],{'data.unity3d/level0':8,'data.unity3d/level1':4,'data.unity3d/level2':1036,'data.unity3d/level3':329,'data.unity3d/sharedassets0.assets':8,'data.unity3d/resources.assets':61430})
    def test_catalog_coverage(self):
        c=self.a['checks'];self.assertEqual((c['catalog_total'],c['union_sprites'],c['no_reference_rows'],c['no_reference_clean'],c['no_reference_with_atlas_membership']),(2185,1897,288,288,115));self.assertEqual(c['coverage_counts']['SCOPED_STATIC_REFERENCE_FOUND'],1897)
    def test_reference_overlap(self):
        c=self.a['checks'];self.assertEqual((c['native_ref_sprites'],c['additional_ref_sprites'],c['overlap_sprites'],c['union_sprites']),(1802,210,115,1897))
    def test_additional_categories(self):self.assertEqual(self.a['checks']['additional_category_counts'],{'ANIMATION_MAPPING_NOT_ACTIVE_SELECTION':892,'ATLAS_MEMBERSHIP_NOT_USAGE':1450,'SERIALIZED_COMPONENT_REFERENCE':3990})
    def test_root_tuples(self):
        c=self.a['checks'];self.assertEqual((c['root_sprite_rows'],c['root_distinct_tuples']),(1250,720))
    def test_supplied_schema_precision(self):
        c=self.a['checks'];self.assertFalse(c['class_id_field_present']);self.assertEqual(c['supplied_schema_class_ids'],['1','212'])
    def test_report_checks(self):self.assertTrue(all(self.a['checks']['report_checks'].values()))
    def test_description_notes(self):
        x=[y['id'] for y in self.a['description_precision_notes']];self.assertEqual(x,['D3','D1','D2']);self.assertEqual(self.a['counts']['description_precision_notes'],3)
    def test_bounded_gaps(self):
        x=self.a['not_independently_recomputed'];self.assertIn('captured_context_status counts',x);self.assertIn('captured_union object/edge overlap counts',x)
    def test_ci_runs(self):
        x=self.a['ci_runs'];self.assertTrue(all(y['conclusion']=='success' for y in x));self.assertEqual([y['run'] for y in x],[40364305678,40369514934,40369514990,40369528335,40369528435]);self.assertTrue(all(y['head_sha']==self.a['target_commit'] for y in x if y['run']!=40364305678))
    def test_source_recovery(self):
        x=self.a['source_recovery'];self.assertEqual((x['run'],x['head_sha'],x['conclusion']),(40364305678,'2beef6d63aba60732eb5b726ae4281f06f0c41bd','success'))
    def test_verdict(self):self.assertEqual(self.a['verdict'],'SUPPORTED_IN_VERIFIED_SCOPE_WITH_3_WORDING_PRECISION_NOTES_AND_BOUNDED_GAPS')
    def test_scope_not_runtime(self):
        s=self.a['scope'];self.assertIn('No runtime',s);self.assertIn('No selfACK or #27-full closure',s)
