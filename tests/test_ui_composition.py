import gzip,hashlib,json,math,unittest
from tools.verify.ui_composition import ROOT,OUT,IDENTITY,hierarchy,trs,multiply,conjunction,build

def node(name,path,depth,active=1,pos=(0.,0.,0.),scale=(1.,1.,1.),rot=(0.,0.,0.,1.)):
 return dict(name=name,path=path,depth=depth,active=active,local_pos=list(pos),scale=list(scale),rotation=list(rot),components=[])
class Hierarchy(unittest.TestCase):
 def test_root_is_layout_frame_not_scene_world(self):
  r=hierarchy([node('r','r',0,pos=(100.,200.,0.)),node('a','r/a',1,pos=(2.,3.,4.))]);self.assertEqual(r[0]['layout_frame_matrix'],IDENTITY);self.assertEqual([r[1]['layout_frame_matrix'][k] for k in (3,7,11)],[2.,3.,4.])
 def test_parent_rotation_scale_and_child_translation(self):
  n=[node('r','r',0),node('p','r/p',1,pos=(10.,20.,0.),scale=(2.,3.,1.),rot=(0.,0.,math.sqrt(.5),math.sqrt(.5))),node('c','r/p/c',2,pos=(1.,2.,0.))];m=hierarchy(n)[2]['layout_frame_matrix'];self.assertAlmostEqual(m[3],4.);self.assertAlmostEqual(m[7],22.)
 def test_inactive_parent_suppresses_active_child(self):
  r=hierarchy([node('r','r',0),node('p','r/p',1,active=0),node('c','r/p/c',2)]);self.assertFalse(r[2]['activity_within_root'])
 def test_ambiguous_parent_never_first_wins(self):
  r=hierarchy([node('r','r',0),node('p','r/p',1),node('p','r/p',1),node('c','r/p/c',2)]);self.assertEqual(r[3]['parent_status'],'ambiguous_parent');self.assertIsNone(r[3]['layout_frame_matrix']);self.assertIsNone(r[3]['activity_within_root'])
 def test_inactive_child_with_unknown_parent_still_inactive(self):
  r=hierarchy([node('c','r/missing/c',2,active=0)]);self.assertFalse(r[0]['activity_within_root']);self.assertIsNone(r[0]['layout_frame_matrix'])
 def test_slash_in_node_name_is_not_an_extra_parent(self):
  r=hierarchy([node('r','r',0),node('TMP [a/b]','r/TMP [a/b]',1)]);self.assertEqual(r[1]['parent'],0)
 def test_slash_in_ancestor_name(self):
  r=hierarchy([node('r','r',0),node('a/b','r/a/b',1),node('c','r/a/b/c',2)]);self.assertEqual(r[2]['parent'],1)
 def test_depth_mismatch_not_parent(self):
  r=hierarchy([node('r','r',0),node('a','r/a',3)]);self.assertEqual(r[1]['parent_status'],'missing_parent')
 def test_unsorted_source_nodes(self):
  r=hierarchy([node('c','r/p/c',2),node('r','r',0),node('p','r/p',1)]);self.assertEqual(r[0]['parent'],2)
 def test_missing_trs_propagates(self):
  n=[node('r','r',0),node('p','r/p',1),node('c','r/p/c',2)];n[1]['scale']=None;self.assertIsNone(hierarchy(n)[2]['layout_frame_matrix'])
 def test_invalid_quaternion_no_identity_fallback(self):
  self.assertIsNone(trs(node('x','x',0,rot=(0.,0.,0.,0.))))
 def test_nonfinite_no_fake_coordinates(self):self.assertIsNone(trs(node('x','x',0,pos=(math.nan,0.,0.))))
 def test_zero_scale_is_preserved(self):self.assertEqual(trs(node('x','x',0,scale=(0.,1.,1.)))[0],0.)
 def test_negative_scale_is_preserved(self):self.assertEqual(trs(node('x','x',0,scale=(-1.,1.,1.)))[0],-1.)
 def test_three_valued_activity(self):self.assertIsNone(conjunction(True,None));self.assertFalse(conjunction(False,None));self.assertTrue(conjunction(True,True))
class CompositionEvidence(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads(gzip.decompress(OUT.read_bytes()));cls.records=[]
  for chunk in cls.d['chunks']:
   b=(ROOT/chunk['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==chunk['sha256'];rows=json.loads(gzip.decompress(b));assert len(rows)==chunk['rows'];cls.records.extend(rows)
 @classmethod
 def tearDownClass(cls):
  cls.d=None;cls.records=None
  import gc;gc.collect()
 def test_sources_pinned(self):
  self.assertEqual(len(self.d['sources']),797)
  for s in self.d['sources']:self.assertEqual(hashlib.sha256((ROOT/s['path']).read_bytes()).hexdigest(),s['sha256'])
 def test_regeneration(self):
  d=build();records=d.pop('records');self.assertEqual(len(records),len(self.records))
  for i,(actual,expected) in enumerate(zip(records,self.records)):self.assertEqual(actual,expected,f'record {i}')
  d['chunks']=self.d['chunks'];self.assertEqual(d,self.d)
 def test_enabled_unknown_not_default_true(self):self.assertTrue(all(r['renderer_enabled'] is None for r in self.records))
 def test_components_not_screens(self):self.assertEqual(len(self.records),100312)
 def test_fonts_and_materials_exact(self):self.assertEqual(self.d['references']['m_fontAsset:resolved_exact_scoped_pptr'],18467);self.assertEqual(self.d['references']['m_Materials:resolved_exact_scoped_pptr'],76802)
 def test_no_runtime_visibility_claim(self):self.assertTrue(all('visible' not in r and 'world_matrix' not in r for r in self.records))
 def test_ambiguous_matrix_kept_unknown(self):
  for r in self.records:
   if r['parent_status']=='ambiguous_parent':self.assertIsNone(r['layout_frame_matrix'])
