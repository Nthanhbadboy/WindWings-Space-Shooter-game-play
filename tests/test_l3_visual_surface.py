import gc,gzip,hashlib,json,math,subprocess,sys,unittest
from pathlib import Path
from tools.verify.l3_chain_graph import ROOT,key,identity
from tools.verify import l3_visual_surface as s

class VisualSurface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=s.load();cls.sec=cls.d['sections']
    @classmethod
    def tearDownClass(cls):del cls.d,cls.sec;s.load.cache_clear();gc.collect()
    def row(self,section,file,pid):return next(r for r in self.sec[section] if key(r['identity'])==(file,pid))
    def alert(self,pid,time):return s.clip_probe(self.d,identity(('data.unity3d/level2',4647)),identity(('data.unity3d/sharedassets2.assets',pid)),time)
    def test_01_counts_are_bounded_scope_not_all_apk(self):
        self.assertEqual(self.d['counts']['objects'],56714);self.assertEqual(self.d['counts']['roots'],585);self.assertEqual(len(self.d['source_gameobjects']),16061)
    def test_02_regeneration_equal_saved(self):self.assertEqual(s.build(),self.d)
    def test_03_input_hashes_current(self):
        for path,sha in self.d['inputs'].items():self.assertEqual(s.digest(ROOT/path),sha,path)
    def test_04_zero_read_failures_one_header_only(self):
        self.assertEqual(self.d['source_read_failures'],[]);self.assertEqual(len(self.d['source_header_only']),1);self.assertEqual(self.d['source_header_only'][0]['class_name'],'Player_Attack_2')
    def test_05_seven_builtin_particle_mesh_refs_not_silenced(self):
        self.assertEqual(len(self.d['unresolved_edges']),7)
        for l in self.d['unresolved_edges']:self.assertEqual(l['owner']['type'],'ParticleSystemRenderer');self.assertEqual(l['location'],'.m_Mesh');self.assertIn('unity default resources',l['error'])
    def test_06_all_geometry_decoded_not_identity_only(self):
        self.assertEqual(self.d['counts']['geometry_status'],{'decoded_numeric_geometry_not_render':1391});self.assertEqual(sum(g['type']=='Mesh' for g in self.sec['geometry']),2)
    def test_07_geometry_indices_within_vertex_arrays(self):
        for r in self.sec['geometry']:
            g=r['geometry'];self.assertEqual(len(g['m_Vertices']),g['vertex_count'])
            for v in g['m_Vertices']:self.assertTrue(all(math.isfinite(n) for n in v))
            for submesh in g['triangles']:
                for face in submesh:self.assertTrue(all(0<=i<g['vertex_count'] for i in face))
    def test_08_geometry_preserves_source_not_obj_axis_flip(self):
        r=self.row('geometry','data.unity3d/resources.assets',848);self.assertEqual(r['geometry']['vertex_count'],146);self.assertTrue(r['raw_location'])
    def test_09_shader_analysis_success_not_valid_replacement(self):
        self.assertEqual(self.d['counts']['shader_analysis_status'],{'UnityPy_decompiled_analysis_NOT_valid_shader_or_render':17});self.assertIn('TextMeshPro/Distance Field',{s['name'] for s in self.sec['shaders']})
    def test_10_shader_source_redacts_integer_byte_buffers(self):
        r=self.row('shaders','data.unity3d/Resources/unity_builtin_extra',10753);p=ROOT/r['raw_location']['path'];raw=[json.loads(l) for l in gzip.decompress(p.read_bytes()).splitlines()][r['raw_location']['row']]
        self.assertTrue(raw['tree']['compressedBlob']['binary_buffer_omitted']);self.assertIn('not* a valid shader file',raw['shader_analysis']['text']);self.assertEqual(hashlib.sha256(raw['shader_analysis']['text'].encode()).hexdigest(),raw['shader_analysis']['sha256'])
    def test_11_alert_renderer_sprite_material_chain(self):
        r=self.row('renderers','data.unity3d/level2',5105);self.assertEqual(r['gameobject_properties']['m_Name'],'Alert');self.assertEqual(r['properties']['m_Color']['a'],0);self.assertEqual(key(r['sprite']),('data.unity3d/sharedassets2.assets',114));self.assertTrue(r['sprite_media'])
        m=self.row('materials',*key(r['materials'][0]));shader=self.row('shaders',*key(m['shader']));self.assertEqual(shader['name'],'Sprites/Default');blend=shader['subshaders'][0]['passes'][0]['state']['rtBlend0'];self.assertEqual(blend['srcBlend']['val'],1);self.assertEqual(blend['destBlend']['val'],10)
    def test_12_alert_controller_has_three_states(self):
        a=self.row('animators','data.unity3d/level2',4647);c=self.row('controllers',*key(a['controllers'][0]));self.assertEqual(c['name'],'Alert');self.assertEqual(c['machines'][0]['default_state_index'],0);self.assertEqual([v['name_candidates'] for v in c['machines'][0]['states']],[['none'],['alert'],['fade']])
    def test_13_alert_alpha_rises_over_explicit_clip(self):
        for t,v in [(0.,0.),(.0625,.392156884),(.125,.784313738)]:
            p=self.alert(42,t);b=p['bindings'][0];self.assertAlmostEqual(b['channels'][0]['value'],v,places=6);self.assertEqual(b['binding']['property_candidates'][0]['field'],'m_Color.a');self.assertEqual(key(b['binding']['targets'][0]),('data.unity3d/level2',5105))
    def test_14_fade_alpha_falls_none_zero(self):
        self.assertAlmostEqual(self.alert(43,0.)['bindings'][0]['channels'][0]['value'],.784313738);self.assertEqual(self.alert(43,.25)['bindings'][0]['channels'][0]['value'],0.);self.assertEqual(self.alert(44,0.)['bindings'][0]['channels'][0]['value'],0.)
    def test_15_clip_probe_rejects_wrong_file_identity(self):
        with self.assertRaises(ValueError):s.clip_probe(self.d,identity(('wrong',4647)),identity(('data.unity3d/sharedassets2.assets',42)),0.)
    def test_16_clip_probe_rejects_unattached_clip(self):
        with self.assertRaises(ValueError):self.alert(999999,0.)
    def test_17_clip_probe_rejects_nonfinite_and_outside_time(self):
        for t in (-.01,.126,float('nan'),float('inf')):
            with self.assertRaises(ValueError):self.alert(42,t)
    def test_18_discrete_pointer_probe_not_float_blending(self):
        b=next(b for b in self.sec['bindings'] if b['binding'].get('isPPtrCurve'));m=next(m for m in self.sec['motion'] if key(m['identity'])==key(b['clip']));p=s.clip_probe(self.d,b['animator'],b['clip'],m['start']);v=p['bindings'][b['binding_index']];self.assertIn('pptr_target',v)
        value=v['channels'][0]['value'];self.assertTrue(value is None or float(value).is_integer())
    def test_19_all_clips_decode_and_binding_gaps_stay_explicit(self):
        self.assertEqual(self.d['counts']['motion_status'],{'numeric_stream_dense_constant_decoded_not_playback':348});self.assertEqual(self.d['counts']['binding_status'],{'unique_target':74916,'unresolved_target':4983,'ambiguous_targets':8})
    def test_20_static_fonts_glyphs_and_atlas_media(self):
        self.assertEqual(len(self.sec['fonts']),7);self.assertEqual(sum(len(f['characters']) for f in self.sec['fonts']),2354)
        for f in self.sec['fonts']:
            self.assertTrue(f['atlases']);self.assertTrue(all(a['media'] for a in f['atlases']));self.assertTrue(f['face'])
    def test_21_vietnamese_glyph_lookup_has_actual_rects(self):
        p=s.glyph_probe(self.d,self.d['default_font'],'Tiếp tục');self.assertTrue(all(v['status']=='static_glyph_and_atlas' for v in p['glyphs']));self.assertTrue(all(v['match']['atlas']['media'] for v in p['glyphs']));self.assertEqual(p['glyphs'][2]['codepoint'],7871)
    def test_22_absent_static_glyph_not_impossible_runtime(self):
        p=s.glyph_probe(self.d,self.d['default_font'],'\U0010ffff');self.assertEqual(p['glyphs'][0]['status'],'absent_in_selected_static_asset_chain');self.assertIsNone(p['glyphs'][0]['match'])
    def test_23_bad_font_identity_rejected(self):
        with self.assertRaises(ValueError):s.glyph_probe(self.d,identity(('wrong',1)),'A')
    def test_24_particle_modules_have_source_and_renderer_not_simulation(self):
        self.assertEqual(len(self.sec['particles']),954)
        for p in self.sec['particles']:self.assertTrue(p['raw_location']);self.assertTrue(p['modules']);self.assertEqual(len(p['renderers']),1);self.assertIn('not simulation',p['scope'])
    def test_25_pause_recipe_joins_surface_and_global_font_candidates(self):
        from tools.verify.l3_recipe import Recipes
        r=Recipes().recipe(10);v=r['visual_surface'];self.assertEqual(len(v['renderers']),8);self.assertEqual(len(v['texts']),3);self.assertEqual(len(v['geometry']),5);self.assertEqual(len(v['fonts']),7);self.assertIn('NOT automatically',v['font_bank_scope']);self.assertEqual(v['sha256'],s.digest(s.OUT))
    def test_28_selected_raw_snapshots_keep_header_and_programs(self):
        p=s.recipe_surface({('data.unity3d/level2',110)});rows=s.selected_raw_objects(p);self.assertTrue(any(r['type']=='Shader' and r.get('shader_analysis') for r in rows));self.assertTrue(any(r['path_id']==4647 and r['type']=='Animator' for r in rows));self.assertEqual(len({key(r) for r in rows}),len(rows))
    def test_26_outside_scope_not_faked_empty_complete_scene(self):
        k=('not_in_source',123);p=s.recipe_surface({k});self.assertEqual(p['coverage']['outside_this_surface_scope'],[identity(k)]);self.assertEqual(p['coverage']['snapshotted_in_this_surface_scope'],0)
    def test_27_cli_explicit_alert_time(self):
        p=subprocess.run([sys.executable,'-m','tools.verify.l3_visual_surface','--file','data.unity3d/level2','--animator','4647','--clip','42','--clip-file','data.unity3d/sharedassets2.assets','--time','.0625'],cwd=ROOT,capture_output=True,text=True,check=True);d=json.loads(p.stdout);self.assertAlmostEqual(d['bindings'][0]['channels'][0]['value'],.392156884)

if __name__=='__main__':unittest.main()
