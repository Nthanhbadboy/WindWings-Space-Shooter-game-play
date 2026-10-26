import copy,gc,gzip,json,math,unittest
from tools.verify.l3_chain_graph import ROOT,key
from tools.verify.l3_layout_math import f32
from tools.verify.l3_pause105 import source,frame,align,ident,F,snapshot
from tools.verify.l3_textured105 import build,uv_geometry,weights,texel_center_probe,shade,blend
from tools.verify.l3_visual_surface import digest,load

class PauseTextured105(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved=json.load(gzip.open(ROOT/'datas/l3_ef6b75ef105.json.gz'));cls.tex=json.loads((ROOT/'reverse-engineering/raw/l3-textured105/texture.json').read_bytes())
    @classmethod
    def tearDownClass(cls):del cls.saved,cls.tex;gc.collect()
    def test_01_complete_artifact_regenerates(self):self.assertEqual(build(),self.saved)
    def test_02_pins(self):
        for p,sha in self.saved['inputs'].items():self.assertEqual(digest(ROOT/p),sha,p)
        self.assertEqual(digest(ROOT/'tools/recovery/l3_textured105.py'),self.tex['tool_sha256'])
    def test_03_false_start_does_not_move_pause_markers(self):self.assertEqual(self.saved['chain']['before'],self.saved['chain']['after_start'])
    def test_04_align_actual_call_order(self):
        tr=self.saved['chain']['native']['trace'];a=[r for r in tr if r['operation']=='ObjectAnchor'];self.assertEqual([r['owner']['path_id'] for r in a],[597593,616420]);self.assertEqual([r['callsite'] for r in a],['0x12cb150','0x12cb160'])
    def test_05_align_size_independent_f32_arithmetic(self):
        x=self.saved['chain']['after_align'];top=x['597593']['world_matrix'][7];bottom=x['616420']['world_matrix'][7];self.assertEqual(x['493280']['m_Size']['y'],f32(abs(f32(top)-f32(bottom))));self.assertEqual(x['493280']['m_Size']['x'],f32(14.4))
    def test_06_align_offset_uses_current_markers(self):
        x=self.saved['chain']['after_align'];self.assertEqual(x['493280']['m_Offset']['y'],f32(f32(x['597593']['world_matrix'][7]+x['616420']['world_matrix'][7])*.5))
    def test_07_native_write_sequence_and_tail_call(self):
        tr=[r for r in self.saved['chain']['native']['trace'] if r['operation'].startswith('set')];self.assertEqual([(r['operation'],r['owner']['path_id']) for r in tr],[('set_size',493280),('set_offset',493280),('set_size',492598),('set_position',274606),('set_position',267691)]);self.assertEqual(tr[-1]['callsite'],'0x12cb454')
    def test_08_parentview_current_pose_propagates_to_actual_renderer(self):
        c=self.saved['chain'];dy=c['after_align']['267691']['world_matrix'][7]-c['before']['267691']['world_matrix'][7];self.assertEqual(dy,c['after_align']['549984']['world_matrix'][7]-c['before']['549984']['world_matrix'][7]);self.assertGreater(dy,0)
    def test_09_clip_alpha_does_not_erase_align_pose(self):
        c=self.saved['chain'];self.assertEqual(c['after_clip']['549984']['world_matrix'],c['after_align']['549984']['world_matrix']);self.assertEqual(c['after_clip']['549984']['m_Color']['a'],f32(.5797794461250305));self.assertEqual(c['after_clip']['493280'],c['after_align']['493280'])
    def test_10_disjoint_clip_align_order_not_scheduler_claim(self):
        c=self.saved['chain'];self.assertTrue(c['disjoint_write_commutation']);self.assertEqual(c['reordered_clip_before_align'],c['after_clip']);self.assertIn('caller-selected',c['order_scope'])
    def test_11_refresh_guard_is_not_unconditional_lifecycle_order(self):
        i=self.saved['refresh_guard']['instructions'];self.assertIn(dict(pc='0x12c9c50',mnemonic='ldrb',operands='w8, [x19, #0x188]'),i);self.assertIn(dict(pc='0x12c9c58',mnemonic='cbz',operands='w8, #0x12c9cac'),i);self.assertIn(dict(pc='0x12c9cb0',mnemonic='bl',operands='#0x12cb128'),i)
    def test_12_setter_bridge_not_tag_registration_proof(self):
        c=self.saved['custom_binding'];self.assertEqual(c['status'],'UNPROVED');self.assertEqual(c['setter_instructions'][-1]['mnemonic'],'br');self.assertEqual(c['setter_instructions'][-1]['operands'],'x2');self.assertEqual(c['binding'],dict(attribute=0,customType=23,typeID=212));self.assertIn('rejects by default',c['policy'])
    def test_13_source_atlas_texture_dimensions_and_pack_identity(self):self.assertEqual((self.tex['width'],self.tex['height']),(2048,1024));self.assertEqual(self.tex['texture']['path_id'],785);self.assertTrue(self.saved['textured']['crop_png_matches_pack'])
    def test_14_uvs_not_zero_meshhelper_placeholder(self):
        t=self.saved['textured'];self.assertEqual(t['source_zero_uv0'],[[0,0]]*4);self.assertEqual(len(t['geometry']['uvs']),4);self.assertTrue(all(u>0 and v>0 for u,v in t['geometry']['uvs']));self.assertEqual(len(t['geometry']['triangles']),2)
    def test_15_uv_source_rectangle_endpoints(self):
        uvs=self.saved['textured']['geometry']['uvs'];self.assertAlmostEqual(min(u for u,v in uvs),1310/2048,8);self.assertAlmostEqual(max(u for u,v in uvs),1566/2048,8);self.assertAlmostEqual(min(v for u,v in uvs),129/1024,8);self.assertAlmostEqual(max(v for u,v in uvs),252/1024,8)
    def test_16_shader_variant_cartesian_product(self):
        v=self.saved['textured']['shader_contract']['variants'];self.assertEqual(len(v),8);self.assertEqual({(r['platform'],r['pixel_snap'],r['external_alpha']) for r in v},{(p,s,a) for p in [5,9] for s in [False,True] for a in [False,True]})
    def test_17_source_texel_probe_barycentrics(self):
        for s in self.saved['textured']['samples']:
            p=s['probe'];self.assertAlmostEqual(sum(p['barycentric']),1.);self.assertGreaterEqual(min(p['barycentric']),0);uvs=self.saved['textured']['geometry']['uvs'];reconstructed=[sum(p['barycentric'][j]*uvs[p['triangle'][j]][i] for j in range(3)) for i in range(2)];self.assertAlmostEqual(reconstructed[0],p['uv'][0]);self.assertAlmostEqual(reconstructed[1],p['uv'][1])
    def test_18_actual_transparent_texel_rgb_premultiplies_to_zero(self):
        a=self.saved['textured']['samples'][0];self.assertEqual(a['source']['rgba8'],[255,134,2,0]);self.assertEqual(a['shader']['fragment'],[0,0,0,0]);self.assertEqual(a['over_half_gray'],[.5,.5,.5,1])
    def test_19_actual_opaque_texel_has_no_background_contribution(self):
        a=self.saved['textured']['samples'][1];self.assertEqual(a['source']['rgba8'],[224,117,35,255]);self.assertEqual(a['shader']['fragment'],[224/255,117/255,35/255,1]);self.assertEqual(a['over_half_gray'],a['shader']['fragment'])
    def test_20_actual_edge_alpha_not_binary_visibility(self):
        t=self.saved['textured']['samples'];self.assertEqual([t[i]['source']['rgba8'][3] for i in [5,6]],[12,26]);self.assertGreater(t[6]['shader']['fragment'][3],t[5]['shader']['fragment'][3]);self.assertGreater(t[5]['shader']['fragment'][3],0)
    def test_21_color_multiply_then_premultiply(self):self.assertEqual(shade([255]*4,[.5]*4,[.5]*4,[.5]*4)['fragment'],[.015625]*3+[.125])
    def test_22_external_alpha_interpolates_red_sample(self):self.assertEqual(shade([255,255,255,0],[1]*4,[1]*4,[1]*4,.5,.5)['fragment'],[.25]*4)
    def test_23_missing_external_sample_rejected(self):
        with self.assertRaises(ValueError):shade([255]*4,[1]*4,[1]*4,[1]*4,enable_external_alpha=1)
    def test_24_nonfinite_or_invalid_shader_input_rejected(self):
        for bad in [float('nan'),float('inf'),-1,2]:
            with self.assertRaises(ValueError):shade([255]*4,[bad]*4,[1]*4,[1]*4)
        with self.assertRaises(ValueError):shade([256]*4,[1]*4,[1]*4,[1]*4)
    def test_25_missing_pixel_not_synthesized(self):
        with self.assertRaises(ValueError):texel_center_probe(self.saved['textured']['geometry'],self.tex,dict(x=0,y=0,rgba8=[0]*4))
    def test_26_blend_premultiplied_rgb_and_alpha_factors(self):self.assertEqual(blend([.1,.2,.3,.5],[.2,.4,.6,.8]),[.2,.4,.6,.9])
    def test_27_degenerate_uv_and_nonfinite_rejected(self):
        with self.assertRaises(ValueError):weights([0,0],[[0,0]]*3)
        with self.assertRaises(ValueError):weights([float('nan'),0],[[0,0],[1,0],[0,1]])
    def test_28_sliced_and_packing_not_fake_uvs(self):
        renderer=dict(properties=dict(m_DrawMode=1));geometry={}
        with self.assertRaises(ValueError):uv_geometry(renderer,geometry,dict(x=1,y=0,z=1,w=0),10,10,1)
        renderer['properties']['m_DrawMode']=0
        with self.assertRaises(ValueError):uv_geometry(renderer,geometry,dict(x=1,y=0,z=1,w=0),10,10,5)
    def test_29_flip_changes_position_not_texture_identity(self):
        s=load()['sections'];r=copy.deepcopy(next(r for r in s['renderers'] if r['identity']['path_id']==563997 and r['identity']['serialized_file']==F));g=next(g for g in s['geometry'] if g['identity']['path_id']==2585 and g['identity']['serialized_file']==F);uv=self.tex['render_data']['uv_transform'];normal=uv_geometry(r,g,uv,2048,1024,1);r['properties']['m_FlipX']=True;flipped=uv_geometry(r,g,uv,2048,1024,1);self.assertEqual(normal['uvs'],flipped['uvs']);self.assertEqual([v[0] for v in flipped['vertices']],[-v[0] for v in normal['vertices']])
    def test_30_scopes_no_render_or_native_precision_promotion(self):
        self.assertIn('NOT Unity readback or render',self.saved['scope']);self.assertIn('no compile/link/GPU execution',self.saved['textured']['shader_contract']['scope']);self.assertIn('not observed',self.saved['textured']['shader_contract']['scope'])
    def test_31_qualified_material_shader_and_null_texture_env(self):
        t=self.saved['textured'];m=t['material'];self.assertEqual(m['identity'],dict(serialized_file='data.unity3d/globalgamemanagers.assets',path_id=2));self.assertEqual(m['shader'],t['shader_contract']['shader']);envs=dict(m['properties']['m_SavedProperties']['m_TexEnvs']);self.assertEqual(envs['_MainTex']['m_Texture']['m_PathID'],0);self.assertEqual(envs['_AlphaTex']['m_Texture']['m_PathID'],0)
