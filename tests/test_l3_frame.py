import copy,gc,gzip,json,math,unittest,zlib
from unittest.mock import patch
from tools.verify.l3_chain_graph import ROOT,key,identity
from tools.verify.ui_composition import IDENTITY
from tools.verify.l3_layout_math import f32
from tools.verify.l3_frame import Frame,scenarios
from tools.verify.l3_composition import merged_source
from tools.verify.l3_visual_surface import clip_probe

F='data.unity3d/level2';A='data.unity3d/sharedassets2.assets'
def ident(pid,file=F):return identity((file,pid))
class SharedFrame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.g=merged_source()[0];cls.saved=json.load(gzip.open(ROOT/'datas/l3_frame_cases.json.gz'))
    @classmethod
    def tearDownClass(cls):del cls.g,cls.saved;gc.collect()
    def frame(self,main=True):return Frame(1080,2400,ident(3976) if main else None,self.g)
    def clip_fixture(self,owner,typ,attribute,values,field=None):
        b=dict(status='unique_target',targets=[identity(owner)],binding_index=0,binding=dict(typeID=typ,attribute=attribute,isPPtrCurve=0),property_candidates=[dict(target=identity(owner),field=field)] if field else [])
        return dict(bindings=[dict(binding=b,channels=[dict(value=v) for v in values])])
    def test_01_saved_cases_regenerate(self):self.assertEqual(scenarios(),self.saved)
    def test_02_input_hashes(self):
        from tools.verify.l3_visual_surface import digest
        for path,sha in self.saved['inputs'].items():self.assertEqual(digest(ROOT/path),sha)
    def test_03_alert_size_alpha_and_footprint_share_state(self):
        a=self.saved['cases']['alert'];self.assertEqual(a['before']['current_size']['y'],19.200000762939453);self.assertEqual(a['after']['current_size']['y'],24.000001907348633);self.assertEqual(a['after']['current_color']['a'],f32(.3921568840742111));self.assertEqual(a['faded']['current_color']['a'],0.)
        self.assertGreater(a['before']['projection']['pixel_bounds'][1],239);self.assertEqual(a['after']['projection']['pixel_bounds'][1],0.);self.assertEqual(a['after']['projection'],a['faded']['projection'])
    def test_04_false_play_on_start_is_not_align(self):
        b=self.saved['cases']['border_info'];self.assertEqual(b['before']['world_matrix'],b['after_start']['world_matrix']);self.assertFalse(b['log'][1]['applied_position']);self.assertAlmostEqual(b['after_align']['world_matrix'][7],8.440000534057617)
    def test_05_parent_write_propagates_to_all_source_descendants(self):
        b=self.saved['cases']['border_info'];self.assertEqual(len(b['descendants_before']),320)
        for before,after in zip(b['descendants_before'],b['descendants_after']):self.assertEqual(before['transform'],after['transform']);self.assertAlmostEqual(after['matrix'][7]-before['matrix'][7],1.440000534057617)
    def test_06_child_projection_uses_changed_parent(self):
        b=self.saved['cases']['border_info'];p=b['child_projection_before'];q=b['child_projection_after'];self.assertEqual(p['renderer'],ident(5452));self.assertEqual(p['renderer'],q['renderer']);self.assertAlmostEqual(q['projection']['pixel_bounds'][1]-p['projection']['pixel_bounds'][1],144.0000419616667)
    def test_07_nonzero_border_kept_unsupported_not_fake_quad(self):self.assertEqual(self.saved['cases']['border_info']['after_align']['geometry']['status'],'not_generated')
    def test_08_direct_anchor_before_start_rejected(self):
        f=self.frame()
        with self.assertRaises(ValueError):f.anchor(ident(7048),[0,96,1080,2208])
        self.assertEqual(f.trees,{})
    def test_09_start_fallback_requires_explicit_main(self):
        f=self.frame(False)
        with self.assertRaises(ValueError):f.anchor(ident(7048),[0,96,1080,2208],start=True)
        self.assertIsNone(f.bindings[F,7048])
    def test_10_false_start_binds_without_initializing_anchor_cache(self):
        f=self.frame();f.anchor(ident(7048),[0,96,1080,2208],start=True);self.assertEqual(f.bindings[F,7048],(F,3976));self.assertNotIn((F,7048),f.states);self.assertEqual(f.safe,[0,0])
    def test_11_root_cache_not_recaptured_after_external_position_change(self):
        f=self.frame();f.resize_camera(ident(3976));f.anchor(ident(7048),[0,96,1080,2208],start=True);f.anchor(ident(7048),[0,96,1080,2208]);i=f.instance(ident(7048),'UIObjectAnchors');tr=key(i['transform']);state=copy.deepcopy(f.states[F,7048]);tree=copy.deepcopy(f.view.tree(tr));tree['m_LocalPosition']['y']=30.;f.trees[tr]=tree;f.anchor(ident(7048),[0,96,1080,2208]);self.assertEqual(f.states[F,7048]['start'],state['start']);self.assertAlmostEqual(f.matrix(tr)[7],8.440000534057617)
    def test_12_safe_cache_persists_when_camera_inputs_change(self):
        f=self.frame();f.resize_camera(ident(3976));f.anchor(ident(7048),[0,96,1080,2208],start=True);f.anchor(ident(7048),[0,96,1080,2208]);safe=list(f.safe);f.half[F,3976]=14.;n=f.anchor(ident(7048),[0,0,1080,2400]);self.assertEqual(f.safe,safe);self.assertNotIn('get_safeArea',n['engine_stub_calls'])
    def test_13_native_scaler_reads_current_renderer_size(self):
        f=self.frame();f.resize_camera(ident(3976));f.scaler(ident(6686));f.clip(ident(4647),ident(42,A),.0625);self.assertEqual(f.view.tree((F,5105))['m_Size']['y'],24.000001907348633);self.assertGreater(f.view.tree((F,5105))['m_Color']['a'],0.)
    def test_14_instances_isolated_raw_not_mutated(self):
        before=copy.deepcopy(self.g.tree((F,5105)));f=self.frame();f.clip(ident(4647),ident(42,A),.0625);self.assertEqual(self.g.tree((F,5105)),before);self.assertEqual(self.frame().view.tree((F,5105)),before)
    def test_15_atomic_failure_does_not_keep_earlier_valid_write(self):
        f=self.frame();sample=clip_probe(f.surface,ident(4647),ident(42,A),.0625);bad=copy.deepcopy(sample['bindings'][0]);bad['binding']['status']='unresolved_target';sample['bindings'].append(bad)
        with patch('tools.verify.l3_frame.clip_probe',return_value=sample):
            with self.assertRaises(ValueError):f.clip(ident(4647),ident(42,A),.0625)
        self.assertEqual(f.trees,{});self.assertEqual(f.refs,{});self.assertEqual(f.log,[])
    def test_16_nan_channel_not_applied(self):
        f=self.frame();sample=self.clip_fixture((F,5105),212,zlib.crc32(b'm_Color.a'),[float('nan')],'m_Color.a')
        with patch('tools.verify.l3_frame.clip_probe',return_value=sample):
            with self.assertRaises(ValueError):f.clip(ident(4647),ident(42,A),0.)
        self.assertEqual(f.trees,{})
    def test_17_transform_position_write_updates_current_world(self):
        f=self.frame();tr=key(f.instance(ident(7048),'UIObjectAnchors')['transform']);sample=self.clip_fixture(tr,4,1,[2.,11.,0.])
        with patch('tools.verify.l3_frame.clip_probe',return_value=sample):f.clip(ident(4647),ident(42,A),0.)
        self.assertAlmostEqual(f.matrix(tr)[7],11.)
    def test_18_invalid_quaternion_transaction_rejected(self):
        f=self.frame();tr=key(f.instance(ident(7048),'UIObjectAnchors')['transform']);sample=self.clip_fixture(tr,4,2,[0,0,0,0])
        with patch('tools.verify.l3_frame.clip_probe',return_value=sample):
            with self.assertRaises(ValueError):f.clip(ident(4647),ident(42,A),0.)
        self.assertEqual(f.trees,{})
    def test_19_euler_write_not_invented(self):
        f=self.frame();tr=key(f.instance(ident(7048),'UIObjectAnchors')['transform']);sample=self.clip_fixture(tr,4,4,[0,0,0])
        with patch('tools.verify.l3_frame.clip_probe',return_value=sample):
            with self.assertRaises(ValueError):f.clip(ident(4647),ident(42,A),0.)
    def test_20_mount_then_root_write_still_moves_root(self):
        f=self.frame();i=f.instance(ident(7048),'UIObjectAnchors');go=i['gameobject'];tr=key(i['transform']);world=list(IDENTITY);world[7]=10.;f.mount(go,world);sample=self.clip_fixture(tr,4,1,[0,11,0])
        with patch('tools.verify.l3_frame.clip_probe',return_value=sample):f.clip(ident(4647),ident(42,A),0.)
        self.assertAlmostEqual(f.matrix(tr)[7],14.)
    def test_21_anchor_start_capture_after_root_mount(self):
        f=self.frame();f.resize_camera(ident(3976));i=f.instance(ident(7048),'UIObjectAnchors');world=list(IDENTITY);world[7]=10.;f.mount(i['gameobject'],world);f.anchor(ident(7048),[0,96,1080,2208],start=True);f.anchor(ident(7048),[0,96,1080,2208]);self.assertEqual(f.states[F,7048]['start'][1],10.);self.assertAlmostEqual(f.matrix(key(i['transform']))[7],11.440000534057617)
    def test_22_invalid_mount_and_clamp_rejected(self):
        f=self.frame();world=list(IDENTITY);world[0]=0
        with self.assertRaises(ValueError):f.mount(ident(110),world)
        with self.assertRaises(ValueError):f.clamp=float('nan')
        self.assertEqual(f.mounts,{})
    def test_23_current_gameobject_activity_separate_from_footprint(self):
        f=self.frame();sample=self.clip_fixture((F,110),1,zlib.crc32(b'm_IsActive'),[0],'m_IsActive')
        with patch('tools.verify.l3_frame.clip_probe',return_value=sample):f.clip(ident(4647),ident(42,A),0.)
        p=f.project(ident(5105),ident(3976));self.assertFalse(p['serialized_chain_activity']);self.assertTrue(p['projection']['intersects'])
    def test_24_source_encoded_pointer_needs_explicit_policy(self):
        f=self.frame()
        with self.assertRaisesRegex(ValueError,'explicit field policy'):f.clip(ident(4695),ident(1609,'data.unity3d/resources.assets'),0.)
        self.assertEqual(f.trees,{})
    def test_25_source_pointer_with_explicit_policy_applies_object_not_index(self):
        f=self.frame();clip=ident(1609,'data.unity3d/resources.assets');bs=[b for b in f.surface['sections']['bindings'] if b['animator']==ident(4695) and b['clip']==clip and b['binding'].get('isPPtrCurve')];policy={b['binding_index']:'m_Sprite' for b in bs};writes=f.clip(ident(4695),clip,0.,pointer_fields=policy);pw=[w for w in writes if 'runtime_reference' in w];self.assertTrue(pw);self.assertTrue(all(w['resolution']=='explicit_custom_binding_field_policy' for w in pw));self.assertEqual(f.view.target(key(pw[0]['target']),'.m_Sprite'),key(pw[0]['runtime_reference']))
    def test_26_unknown_pointer_sample_not_null_clear(self):
        f=self.frame();sample=self.clip_fixture((F,5105),212,0,[None]);sample['bindings'][0]['binding']['binding']['isPPtrCurve']=1;sample['bindings'][0]['pptr_target']=None
        with patch('tools.verify.l3_frame.clip_probe',return_value=sample):
            with self.assertRaisesRegex(ValueError,'not a null write'):f.clip(ident(4647),ident(42,A),0.)
        self.assertEqual(f.refs,{})
    def test_27_invalid_clip_rejected_by_source_attachment(self):
        f=self.frame()
        with self.assertRaises(ValueError):f.clip(ident(4647),ident(99999,A),0.)
    def test_28_camera_lookup_and_dimensions_not_guessed(self):
        with self.assertRaises(ValueError):Frame(0,2400,source=self.g)
        with self.assertRaises(ValueError):Frame(1080,2400,ident(99999),self.g)
    def test_29_recipe_does_not_auto_execute_frame(self):
        from tools.verify.l3_recipe import Recipes
        r=Recipes().recipe(10);self.assertIn('frame_application',r);self.assertFalse(r['frame_application']['auto_execute']);self.assertTrue(r['frame_application']['requires_explicit_order_and_instance_context'])

if __name__=='__main__':unittest.main()
