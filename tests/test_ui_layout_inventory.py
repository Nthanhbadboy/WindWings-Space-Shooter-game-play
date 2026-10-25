import csv,gzip,hashlib,json,unittest
from collections import Counter
from tools.verify.ui_layout_inventory import ROOT,OUT,fingerprint
class Inventory(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads(gzip.decompress(OUT.read_bytes()));cls.files=[]
  for c in cls.d['file_chunks']:
   b=(ROOT/c['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==c['sha256'];rows=json.loads(gzip.decompress(b));assert len(rows)==c['rows'];cls.files.extend(rows)
 @classmethod
 def tearDownClass(cls):
  cls.d=None;cls.files=None
  import gc;gc.collect()
 def test_all_saved_sources_accounted(self):self.assertEqual({r['file'] for r in self.files},{p.name for p in (ROOT/'reverse-engineering/raw/ui').glob('*.json.gz')});self.assertEqual(len(self.files),55584)
 def test_all_source_hashes_not_just_samples(self):
  for r in self.files:self.assertEqual(hashlib.sha256((ROOT/'reverse-engineering/raw/ui'/r['file']).read_bytes()).hexdigest(),r['sha256'])
 def test_manifest_digest(self):self.assertEqual(hashlib.sha256(''.join(f"{r['file']} {r['sha256']}\n" for r in self.files).encode()).hexdigest(),self.d['source_manifest_sha256'])
 def test_generator_hash(self):self.assertEqual(hashlib.sha256((ROOT/'tools/verify/ui_layout_inventory.py').read_bytes()).hexdigest(),self.d['evidence']['tool_sha256'])
 def test_outside_has_no_extra_class_label_not_no_extra_states(self):self.assertEqual({r['screen'] for r in self.files if r['indexed']},{r['screen'] for r in self.files})
 def test_scope_counts(self):self.assertEqual(sum(r['indexed'] for r in self.files),797);self.assertEqual(self.d['totals']['outside_index_files'],54787)
 def test_no_unindexed_scoped_upgrade(self):self.assertEqual(self.d['totals'].get('outside_index_sprite_pptr_recorded',0),0);self.assertEqual(self.d['totals']['outside_index_sprite_name_only'],3843228)
 def test_font_gap_is_measured(self):self.assertEqual(self.d['totals']['outside_index_tmp_components'],1003504);self.assertEqual(self.d['totals']['outside_index_tmp_font_pptr_recorded'],0)
 def test_group_counts_recomputed(self):
  counts=Counter((r['screen'],r['topology_sha256']) for r in self.files)
  self.assertEqual(counts,Counter({(g['screen'],g['topology_sha256']):g['files'] for g in self.d['groups']}))
 def test_indexed_topology_candidates_not_bindings(self):self.assertEqual(sum(g['files']-g['indexed_files'] for g in self.d['groups'] if g['indexed_files']),14081);self.assertTrue(all('sprite_bindings' not in r for r in self.files))
 def test_projection_ignores_pptrs_so_is_NOT_identity(self):
  a=[dict(name='x',path='r/x',components=[dict(**{'class':'SpriteRenderer'},sprite='same',visual_properties={'m_Sprite':{'m_PathID':1}})])];b=json.loads(json.dumps(a));b[0]['components'][0]['visual_properties']['m_Sprite']['m_PathID']=2;self.assertEqual(fingerprint(a),fingerprint(b))
 def test_projection_preserves_transform_difference(self):
  a=[dict(name='x',path='r/x',local_pos=[1.,2.,3.])];b=[dict(name='x',path='r/x',local_pos=[1.,2.,4.])];self.assertNotEqual(fingerprint(a),fingerprint(b))
 def test_projection_preserves_activity(self):self.assertNotEqual(fingerprint([dict(active=0)]),fingerprint([dict(active=1)]))
 def test_projection_preserves_text(self):self.assertNotEqual(fingerprint([dict(components=[{'class':'TextMeshPro','text':'a'}])]),fingerprint([dict(components=[{'class':'TextMeshPro','text':'b'}])]))
 def test_pinned_index_matches(self):self.assertEqual(hashlib.sha256((ROOT/'reverse-engineering/raw/ui/_index.csv').read_bytes()).hexdigest(),self.d['evidence']['index_sha256'])
