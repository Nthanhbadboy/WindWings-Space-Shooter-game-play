import copy,gc,json,math,unittest
from tools.verify.l3_chain_graph import Graph,ROOT,key,identity
from tools.verify.ui_composition import IDENTITY,trs
from tools.verify import l3_composition as c
from tools.verify.l3_composition_math import inverse,point,layer_gate,clip_polygon,project_geometry,viewport_parameters,sprite_geometry

class ProjectionMath(unittest.TestCase):
    def camera(self):return dict(properties={'orthographic':True,'orthographic size':1.,'near clip plane':.1,'far clip plane':10.,'m_NormalizedViewPortRect':{'x':0.,'y':0.,'width':1.,'height':1.}},serialized_world_matrix=list(IDENTITY))
    def project(self,vertices,camera=None):return project_geometry(vertices,[[0,1,2]],list(IDENTITY),camera or self.camera(),100,100)
    def test_layer_mask_uint32_and_invalid_layers(self):
        self.assertTrue(layer_gate(-1,31));self.assertFalse(layer_gate(32,0));self.assertTrue(layer_gate(32,5))
        for v in (-1,32,None,True):
            with self.assertRaises(ValueError):layer_gate(32,v)
    def test_affine_inverse_translation_rotation_scale(self):
        m=trs(dict(local_pos=[3,4,5],rotation=[0,0,math.sin(.3),math.cos(.3)],scale=[2,3,4]));v=point(inverse(m),point(m,[1,2,3]))
        for a,b in zip(v,[1,2,3]):self.assertAlmostEqual(a,b)
    def test_singular_matrix_not_replaced_by_identity(self):
        m=list(IDENTITY);m[0]=0
        with self.assertRaises(ValueError):inverse(m)
    def test_finite_affine_point_boundary(self):
        m=list(IDENTITY);m[15]=2
        with self.assertRaises(ValueError):point(m,[0,0,0])
        with self.assertRaises(ValueError):point(IDENTITY,[float('nan'),0,0])
    def test_center_triangle_projects(self):
        p=self.project([[-.5,-.5,1],[.5,-.5,1],[0,.5,1]]);self.assertTrue(p['intersects']);self.assertEqual(p['pixel_bounds'],[25.,25.,75.,75.])
    def test_crossing_triangle_all_vertices_outside_still_intersects(self):
        p=self.project([[-3,-3,1],[3,-3,1],[0,3,1]]);self.assertTrue(p['intersects']);self.assertEqual(p['pixel_bounds'],[0.,0.,100.,100.])
    def test_near_far_and_behind_camera_excluded(self):
        for z in (-1,0,.05,11):self.assertFalse(self.project([[-.5,-.5,z],[.5,-.5,z],[0,.5,z]])['intersects'])
    def test_triangle_crossing_near_plane_clipped(self):
        p=self.project([[-.5,-.5,-1],[.5,-.5,1],[0,.5,1]]);self.assertTrue(p['intersects']);self.assertTrue(all(v[2]>=.1-1e-12 for poly in p['clipped_polygons'] for v in poly['camera']))
    def test_offscreen_and_degenerate_have_no_area(self):
        self.assertFalse(self.project([[2,2,1],[3,2,1],[2,3,1]])['intersects']);self.assertFalse(self.project([[0,0,1]]*3)['intersects'])
    def test_camera_translation_is_not_ignored(self):
        cam=self.camera();cam['serialized_world_matrix'][3]=2;self.assertFalse(self.project([[-.5,-.5,1],[.5,-.5,1],[0,.5,1]],cam)['intersects'])
    def test_subviewport_aspect_and_pixel_origin(self):
        cam=self.camera();cam['properties']['m_NormalizedViewPortRect']={'x':.25,'y':.25,'width':.5,'height':.5};p=viewport_parameters(cam,200,100);self.assertEqual(p['pixel_rect'],[50,25,100,50]);self.assertEqual(p['half_width'],2.)
    def test_nonrigid_and_reflected_cameras_rejected(self):
        for scale in (2,-1):
            cam=self.camera();cam['serialized_world_matrix'][0]=scale
            with self.assertRaises(ValueError):viewport_parameters(cam,100,100)
    def test_invalid_projection_parameters_not_silently_defaulted(self):
        for w,h in [(0,100),(100,-1),(float('inf'),100)]:
            with self.assertRaises(ValueError):viewport_parameters(self.camera(),w,h)
        cam=self.camera();cam['properties']['orthographic']=False
        with self.assertRaises(ValueError):viewport_parameters(cam,100,100)
    def test_bad_triangle_index_rejected(self):
        with self.assertRaises(ValueError):project_geometry([[0,0,1]],[[0,1,2]],IDENTITY,self.camera(),100,100)
    def test_nonfinite_clipper_input_rejected(self):
        with self.assertRaises(ValueError):clip_polygon([[float('nan'),0,1]],1,1,.1,10)
    def test_unresolved_parent_is_not_a_root(self):
        tr=dict(serialized_file='f',path_id=1,type='Transform',tree={'m_LocalPosition':dict(x=0,y=0,z=0),'m_LocalRotation':dict(x=0,y=0,z=0,w=1),'m_LocalScale':dict(x=1,y=1,z=1),'m_Father':{'m_FileID':0,'m_PathID':99}})
        p=c.Poses(Graph([tr],[])).get(('f',1));self.assertEqual(p['status'],'unresolved_or_absent_parent');self.assertIsNone(p['matrix'])

class SourceComposition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=c.load()
    @classmethod
    def tearDownClass(cls):del cls.d;c.load.cache_clear();gc.collect()
    def renderer(self,pid=5105,file='data.unity3d/level2'):return next(r for r in self.d['renderers'] if key(r['identity'])==(file,pid))
    def test_01_all_poses_known_from_merged_typed_parents(self):
        self.assertEqual(self.d['counts']['poses'],{'known_serialized_affine':11380});self.assertEqual(self.d['counts']['source_body_overlap_verified'],1760);self.assertEqual(self.d['counts']['merged_objects'],57480)
    def test_02_regeneration_matches_saved(self):self.assertEqual(c.build(),self.d)
    def test_03_source_hashes_match(self):
        for path,sha in self.d['inputs'].items():self.assertEqual(c.digest(ROOT/path),sha)
    def test_04_scene_template_separation(self):self.assertEqual(self.d['counts']['contexts'],{'serialized_scene':558,'asset_template_NOT_placed':10822})
    def test_05_game_main_camera_layer_split(self):
        pairs=[p for p in self.d['scene_mask_pairs'] if key(p['renderer'])==('data.unity3d/level2',5105)];self.assertEqual({p['camera']['path_id']:p['mask_includes_layer'] for p in pairs},{3975:False,3976:True})
    def test_06_depth_groups_preserve_clear_and_targets(self):
        group=next(g for g in self.d['scene_depth_groups'] if g['scene']=='data.unity3d/level2');self.assertEqual([g['depth'] for g in group['depth_groups']],[-1.,0.]);self.assertEqual([g['cameras'][0]['clear_flags'] for g in group['depth_groups']],[2,3]);self.assertNotIn('data.unity3d/sharedassets0.assets',{g['scene'] for g in self.d['scene_depth_groups']})
    def test_07_alert_native_scaler_to_geometry_camera_clip(self):
        p=c.alert_chain();self.assertEqual(p['predicted_half_height'],12.000000953674316);self.assertEqual(p['native_scaler']['model'],[10.800000190734863,24.000001907348633]);self.assertAlmostEqual(p['clip']['bindings'][0]['channels'][0]['value'],.3921568840742111)
        game,main=p['cameras'];self.assertFalse(game['layer_gate']);self.assertTrue(main['layer_gate']);self.assertTrue(main['projection']['intersects']);self.assertEqual(main['geometry']['status'],'modeled_zero_border_sliced_rectangle');self.assertAlmostEqual(main['projection']['camera_vertices'][0][2],21.)
        for a,b in zip(main['projection']['pixel_bounds'],[0,0,1080,2400]):self.assertAlmostEqual(a,b,places=3)
    def test_08_serialized_pose_includes_root_local_trs(self):self.assertEqual(self.renderer()['pose']['matrix'][11],1.)
    def test_09_asset_template_not_projected_into_scene_automatically(self):
        r=next(r for r in self.d['renderers'] if r['source_context']=='asset_template_NOT_placed' and r['type']=='SpriteRenderer')
        with self.assertRaises(ValueError):c.probe(r['identity'],identity(('data.unity3d/level2',3976)),1080,2400)
    def test_10_template_requires_explicit_full_world_matrix(self):
        r=next(r for r in self.d['renderers'] if r['source_context']=='asset_template_NOT_placed' and r['type']=='SpriteRenderer');p=c.probe(r['identity'],identity(('data.unity3d/level2',3976)),1080,2400,world_override=list(IDENTITY));self.assertTrue(p['world_override_supplied'])
    def test_11_no_cross_scene_automatic_projection(self):
        with self.assertRaises(ValueError):c.probe(identity(('data.unity3d/level2',5105)),identity(('data.unity3d/level1',39)),1080,2400)
    def test_12_unimplemented_sliced_border_not_a_fake_quad(self):
        renderer={'properties':{'m_DrawMode':1}};g={'geometry':{},'sprite_properties':{'m_Border':{'x':1,'y':0,'z':0,'w':0}}};self.assertEqual(sprite_geometry(renderer,g)['status'],'not_generated')
    def test_13_simple_geometry_flip_does_not_mutate_source(self):
        g={'geometry':{'m_Vertices':[[1,2,0],[2,2,0],[1,3,0]],'triangles':[[[0,1,2]]]},'sprite_properties':{}};p=sprite_geometry({'properties':{'m_DrawMode':0,'m_FlipX':True}},g);self.assertEqual(p['vertices'][0],[-1,2,0]);self.assertEqual(g['geometry']['m_Vertices'][0],[1,2,0])
    def test_14_invalid_source_screen_dimensions(self):
        for w in (0,1.5,True,float('nan'),2**31):
            with self.assertRaises(ValueError):c.alert_chain(w,2400)
    def test_15_recipe_keeps_camera_candidates_not_selected_stack(self):
        from tools.verify.l3_recipe import Recipes
        r=Recipes().recipe(10)['composition'];self.assertEqual(len(r['renderers']),8);self.assertEqual(len(r['camera_candidates']),6);self.assertIn('NOT automatically',r['camera_scope']);self.assertTrue(all(v['source_context']=='asset_template_NOT_placed' for v in r['renderers']))

if __name__=='__main__':unittest.main()
