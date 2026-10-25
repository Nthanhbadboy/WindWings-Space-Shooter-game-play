import gc,gzip,json,math,unittest
from tools.verify.l3_layout import build,load,constants,model_probe,native_probe,instance_probe,OUT
from tools.verify.l3_layout_math import safe_bounds,scaler_step,anchor_step,f32
from tools.verify.l3_layout_emulator import execute
from tools.verify.ui_composition import IDENTITY,trs
from tools.verify.l3_recipe import Recipes

class NativeLayoutMath(unittest.TestCase):
    def case(self,anchor=5,**kwargs):
        c=dict(anchor=anchor,local=[1.,2.,3.],parent=list(IDENTITY),ui_half_height=14.,ui_aspect=.8,fixed=False,main_half_height=14.,screen_height=2400,safe_rect=[0.,96.,1920.,2208.]);c.update(kwargs);return c
    def compare(self,case):
        m=model_probe(case);n=native_probe(case)
        for field in ('state','local','world','writes'):self.assertEqual(m[field],n[field],field)
        self.assertEqual(m['safe']['bounds'],n['safe']);return m,n
    def test_exact_constants_not_rounded_disassembly(self):
        self.assertEqual(constants()['min_aspect'],0.43478259444236755)
        self.assertEqual(constants()['clamp'],12.420000076293945)
        self.assertEqual(constants()['jump_table_hex'],'00090f03070d0a10')
    def test_all_declared_anchors_with_and_without_fixed_mode_against_native(self):
        for fixed in (False,True):
            for a in range(10):self.compare(self.case(a,fixed=fixed))
    def test_native_root_jump_table_corners_and_edges(self):
        r=constants()['roots'];self.assertEqual(r['3'],[-f32(5.4),-f32(9.6)]);self.assertEqual(r['7'],[f32(5.4),f32(9.6)]);self.assertEqual(r['8'],[-f32(5.4),0.])
    def test_left_right_write_world_x_only_without_local_z_restore(self):
        p=trs(dict(local_pos=[0,0,0],rotation=[0,math.sqrt(.5),0,math.sqrt(.5)],scale=[1,1,1]))
        m,n=self.compare(self.case(9,parent=p));self.assertEqual(len(m['writes']),1);self.assertNotEqual(m['local'][2],m['state']['cached_z'])
    def test_general_path_restores_cached_local_z_under_rotated_parent(self):
        p=trs(dict(local_pos=[2,3,4],rotation=[math.sqrt(.5),0,0,math.sqrt(.5)],scale=[2,3,4]))
        m,n=self.compare(self.case(5,parent=p));self.assertEqual(len(m['writes']),2);self.assertEqual(m['local'][2],3.)
    def test_none_and_center_are_not_skip_operations(self):
        state=dict(root=[0.,0.],real=[0.,0.],start=[1.,2.,3.],cached_z=3.)
        for a in (0,1):
            m,n=self.compare(self.case(a,local=[9.,8.,7.],state=state));self.assertEqual(m['local'],[1.,2.,3.])
    def test_root_position_cache_is_not_recaptured_every_call(self):
        m,n=self.compare(self.case(5));state=m['state'];m2,n2=self.compare(self.case(5,local=[30.,40.,50.],state=state))
        self.assertEqual(m2['state']['start'],state['start']);self.assertEqual(m2['local'],m['local'])
    def test_safe_area_uses_main_camera_not_clamped_ui_camera_height(self):
        m,n=self.compare(self.case(5,ui_half_height=8.,main_half_height=20.,fixed=True))
        self.assertEqual(m['safe']['bounds'],safe_bounds(2400,[0,96,1920,2208],20.)['bounds'])
    def test_safe_area_ignores_horizontal_rect_fields(self):
        a=safe_bounds(2400,[0,96,1920,2208],14.);b=safe_bounds(2400,[90,96,700,2208],14.)
        self.assertEqual(a,b)
    def test_nonzero_safe_cache_does_not_read_screen_or_main_camera(self):
        case=self.case(5,cached_safe=[12.,-11.],screen_height=None,safe_rect=None,main_half_height=None)
        m,n=self.compare(case);self.assertFalse(m['safe']['recomputed']);self.assertNotIn('get_safeArea',n['engine_stub_calls'])
    def test_either_zero_cache_value_forces_recompute(self):
        for cached in ([0.,-11.],[12.,0.]):
            m,n=self.compare(self.case(5,cached_safe=cached));self.assertTrue(m['safe']['recomputed']);self.assertEqual(n['engine_stub_calls']['get_safeArea'],1)
    def test_fixed_aspect_bounds_are_only_applied_to_horizontal_extent(self):
        for aspect in (.2,.43478259444236755,.6,.9):self.compare(self.case(7,ui_aspect=aspect,fixed=True))
    def test_left_anchor_does_not_need_safe_area_inputs(self):
        m,n=self.compare(self.case(8,safe_rect=None,screen_height=None,main_half_height=None));self.assertNotIn('get_safeArea',n['engine_stub_calls'])
    def test_object_scaler_preserves_width_for_both_modes(self):
        for full in (False,True):
            for clamp in (False,True):
                m=scaler_step([3.,4.],14.,full,clamp,constants());n=execute(('ObjectScaler','Start'),constants(),[0,0,0],IDENTITY,main_half_height=14.,size=[3.,4.],full=full,clamp=clamp)
                self.assertEqual(m,n['size']);self.assertEqual(m[0],3.)
    def test_runtime_mutable_clamp_override_matches_native(self):
        self.compare(self.case(6,fixed=True,clamp_value=10.))
        for v in (float('nan'),float('inf')):
            with self.assertRaises(ValueError):model_probe(self.case(6,fixed=True,clamp_value=v))
    def test_start_binds_main_before_guarded_anchor_call(self):
        for missing in (False,True):
            for play in (False,True):
                case=self.case(5);n=execute(('UIObjectAnchors','Start'),constants(),**case,ui_camera_null=missing,play_on_start=play)
                self.assertEqual(n['bound_ui_camera'],'main' if missing else 'explicit_stub')
                self.assertEqual(n['engine_stub_calls'].get('get_main',0),int(missing)+int(play))
                self.assertEqual(bool(n['writes']),play)
                if play:self.assertEqual(n['world'],model_probe(case)['world'])

    def test_native_static_constructor_sets_clamp_value(self):
        n=execute(('ObjectScaler','cctor'),dict(constants(),clamp=0.),[0,0,0],IDENTITY)
        self.assertEqual(n['clamp'],constants()['clamp'])
    def test_object_scaler_nonfull_mode_uses_current_size(self):
        a=scaler_step([3.,4.],14.,False,False,constants());b=scaler_step(a,14.,False,False,constants());self.assertNotEqual(a,b)
    def test_invalid_enum_or_camera_is_not_defaulted(self):
        for case in (self.case(-1),self.case(10),self.case(5,ui_aspect=0),self.case(5,ui_half_height=float('nan'))):
            with self.assertRaises(ValueError):model_probe(case)
    def test_singular_parent_is_not_replaced_by_identity(self):
        p=trs(dict(local_pos=[0,0,0],rotation=[0,0,0,1],scale=[0,1,1]))
        with self.assertRaises(ValueError):model_probe(self.case(5,parent=p))

class LayoutContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=load();cls.r=Recipes()
    @classmethod
    def tearDownClass(cls):cls.d=cls.r=None;gc.collect()
    def test_regeneration_includes_all_source_objects_and_native_checks(self):
        self.assertEqual(build(),self.d);self.assertLess(OUT.stat().st_size,5_000_000)
    def test_all_apk_target_header_scan_not_only_85_old_core_anchors(self):
        self.assertEqual(self.d['source_scan']['headers'],125453)
        self.assertEqual(self.d['counts']['classes'],{'UIObjectAnchors':584,'ObjectScaler':1})
        self.assertEqual(self.d['counts']['header_scan_errors'],1);self.assertEqual(self.d['counts']['read_errors'],0)
    def test_no_guessed_main_camera_for_null_pointer(self):
        self.assertEqual(self.d['counts']['camera_bindings'],{'runtime_Camera.main_fallback_NOT_selected':576,'explicit_serialized_camera':8})
        self.assertEqual(len(self.d['cameras']),6);self.assertEqual(self.d['counts']['main_tag_candidates'],4)
    def test_all_parent_poses_are_typed_and_bridge_is_explicitly_modeled(self):
        self.assertEqual(self.d['pose_errors'],[]);self.assertEqual(self.d['counts']['unmodeled_affine_bridges'],0)
        for i in self.d['instances']:self.assertEqual(len(i['world_matrix']),16)
    def test_pause_align_links_to_exact_top_and_bottom_components(self):
        p=self.r.recipe(10);items=p['native_layout']['instances'];ids={i['identity']['path_id']:i for i in items}
        for id in (597593,616420):
            self.assertTrue(any(c['owner']['path_id']==690342 and c['method']=='Align' for c in ids[id]['native_callers']))
    def test_actual_pause_top_anchor_probe_native_matches_model(self):
        i=next(i for i in self.d['instances'] if i['identity']['path_id']==597593)
        d=instance_probe(i,dict(ui_half_height=14.,ui_aspect=.45,main_half_height=14.,screen_height=2400,safe_rect=[0.,96.,1080.,2208.]))
        self.assertEqual(d['model']['world'],d['native']['world']);self.assertAlmostEqual(d['model']['world'][1],11.180000305175781)
        chain=self.d['camera_chain_check'];self.assertEqual(chain['predicted_half_height'],12.000000953674316);self.assertEqual(chain['probe']['model']['world'],chain['probe']['native']['world']);self.assertAlmostEqual(chain['probe']['model']['world'][1],9.34000015258789)
    def test_actual_background_renderer_and_size_write(self):
        i=next(i for i in self.d['instances'] if i['class_name']=='ObjectScaler')
        self.assertTrue(i['sprite_media']);self.assertTrue(i['materials']);self.assertEqual(i['renderer_properties']['m_DrawMode'],1)
        self.assertEqual(i['renderer']['path_id'],5105);self.assertEqual(i['identity']['serialized_file'],'data.unity3d/level2')
        d=instance_probe(i,dict(main_half_height=14.));self.assertEqual(d['model'],d['native']['size']);self.assertEqual(d['model'],[10.800000190734863,24.84000015258789])
        d=instance_probe(i,dict(main_half_height=14.,clamp_value=10.));self.assertEqual(d['model'],d['native']['size']);self.assertEqual(d['model'],[10.800000190734863,20.])

if __name__=='__main__':unittest.main()
