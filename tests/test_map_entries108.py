import collections,gzip,json,unittest
from tools.verify.map_entries108 import ROOT,OUT,build,sha,normalize
from tools.verify.map_entries108_native import run
class MapEntries108(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=json.load(gzip.open(OUT))
 def test_01_regenerate(self):self.assertEqual(build(),self.r)
 def test_02_all_source_pins(self):
  for p,h in self.r['inputs'].items():self.assertEqual(sha(ROOT/p),h,p)
 def test_03_unique_576_identity_sites(self):self.assertEqual(len({r['initializer']['pc'] for r in self.r['bindings']}),576)
 def test_04_root_histogram(self):self.assertEqual(dict(collections.Counter(r['root'] for r in self.r['bindings'])),{'listMapDatas':243,'AllPvPStartMaps':100,'AllArenaStartMaps':63,'listMapBranchDatas':52,'listMapChallangeDatas':41,'listMapEndlessDatas':28,'listMapObstacleDatas':28,'AllArenaRandomMaps':20,'listMapTryPlayerDatas':1})
 def test_05_first_campaign_three(self):self.assertEqual([x['values'] for x in self.r['constructor_roots']['listMapDatas']['items'][:3]],[[25,9010],[164],[113,5]])
 def test_06_campaign250_not576_stages(self):self.assertEqual(len(self.r['constructor_roots']['listMapDatas']['items']),250)
 def test_07_campaign_243_ia_7_literal(self):self.assertEqual((sum(r['root']=='listMapDatas' for r in self.r['bindings']),sum(r['root']=='listMapDatas' for r in self.r['non_InitializeArray_leaves'])),(243,7))
 def test_08_campaign_zero_based_paths(self):self.assertEqual(sorted(r['index_path'][0] for r in self.r['bindings']+self.r['non_InitializeArray_leaves'] if r['root']=='listMapDatas'),list(range(250)))
 def test_09_actual_native_range(self):self.assertEqual(self.r['native_instructions'],25224)
 def test_10_source_store_unique(self):self.assertEqual((len(self.r['source_field_stores']),len({r['field'] for r in self.r['source_field_stores']})),(12,12))
 def test_11_campaign_source_store_not_heuristic_segment(self):self.assertEqual(next(r['pc'] for r in self.r['source_field_stores'] if r['field']=='listMapDatas'),'0x140e19c')
 def test_12_two_different_add_branches(self):
  x=self.r['capacity_crosscheck'];self.assertTrue(x['canonical_roots_equal']);a=collections.Counter(r['operation'] for r in x['zero_calls']);b=collections.Counter(r['operation'] for r in x['inline_calls']);self.assertEqual((a['List.Add'],b['List.Add']),(773,0))
 def test_13_allocation_census(self):
  c=collections.Counter(r['operation'] for r in self.r['capacity_crosscheck']['zero_calls']);self.assertEqual((c['newarray'],c['newobj'],c['InitializeArray']),(716,69,576))
 def test_14_no_resolver_or_classinit_during_fixture(self):self.assertFalse(any(r['operation'] in ['resolve','classinit'] for r in self.r['capacity_crosscheck']['zero_calls']))
 def test_15_all_array_allocations_unique(self):self.assertEqual(len({r['array_new_site'] for r in self.r['bindings']+self.r['non_InitializeArray_leaves']}),716)
 def test_16_existing715_values_match_without_using_as_identity(self):self.assertEqual(self.r['legacy_differential']['value_mismatches'],0);self.assertEqual(self.r['legacy_differential']['rows'],715)
 def test_17_map_metadata_resolved_by_rela(self):self.assertEqual(len([r for r in self.r['relocations'] if r['Name']=='Map_Get_Datas_TypeInfo']),1)
 def test_18_dictionary_not_wave_leaf(self):self.assertEqual((self.r['constructor_roots']['listIdBosses']['kind'],len(self.r['constructor_roots']['listIdBosses']['items'])),('dictionary',20))
 def test_19_dynamic_length_not_apk_default_zero(self):
  d=next(r for r in self.r['non_InitializeArray_leaves'] if r['root']=='mapChallangeIndexs');self.assertIn('FIXTURE_ONLY',d['length_status']);self.assertIn('not observed',self.r['external_static_policy']['source'])
 def test_20_alternative_external_length(self):
  roots=normalize(run(0,7));dynamic=roots.pop('mapChallangeIndexs');base=dict(self.r['constructor_roots']);base.pop('mapChallangeIndexs');self.assertEqual(roots,base);self.assertEqual(dynamic['values'],[0]*7)
 def test_21_invalid_capacity(self):
  with self.assertRaisesRegex(ValueError,'fixture capacity'):run(-1)
 def test_22_invalid_external_length(self):
  with self.assertRaisesRegex(ValueError,'fixture challenge length'):run(0,-1)
 def test_23_explicit_native_boundary(self):self.assertIn('synthetic metadata/allocator/List/Dictionary hooks',self.r['scope']);self.assertIn('NOT original',self.r['scope'])
 def test_24_no_chapter_stage_invented(self):self.assertIn('NOT original container implementation, live readback, chapter/stage/UI numbering',self.r['scope'])
 def test_25_consumer_same_field_and_signed_clamp(self):
  c=self.r['consumer_campaign_route'];self.assertEqual((c['static_offset'],c['field'],len(c['anchors'])),('0x28','listMapDatas',8));self.assertIn('Static source audit only',c['scope'])
if __name__=='__main__':unittest.main()
