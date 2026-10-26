import copy,gzip,json,math,unittest
from tools.verify.l3_chain_graph import ROOT
from tools.verify.ui_composition import IDENTITY,sequential_sum
from tools.verify.l3_shader106 import build,requests,canonical,sha,RAW
from tools.verify.l3_shader106_math import vertex,round_even,interpolate,footprint,bilinear,fragment
from tools.verify.l3_textured105 import blend

class Shader106(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.saved=json.load(gzip.open(ROOT/'datas/l3_ef6b75ef106.json.gz'));cls.raw=json.loads((RAW/'samples.json').read_bytes())
    def v(self,p=None,uv=None,**kw):
        args=dict(position=p or [.25,-.25,.1,1],uv=uv or [.2,.8],vertex_color=[1]*4,material_color=[1]*4,renderer_color=[1]*4,flip=[1,1],object_to_world=IDENTITY,matrix_vp=IDENTITY,screen=[1080,2400],pixel_snap=False);args.update(kw);return vertex(**args)
    def test_01_saved_regenerates(self):self.assertEqual(build(),self.saved)
    def test_02_all_input_and_recovery_pins(self):
        for p,h in self.saved['inputs'].items():self.assertEqual(sha(ROOT/p),h,p)
        for key,p in [('tool_sha256','tools/recovery/l3_shader106.py'),('request_generator_sha256','tools/verify/l3_shader106.py'),('math_tool_sha256','tools/verify/l3_shader106_math.py'),('previous_artifact_sha256','datas/l3_ef6b75ef105.json.gz')]:self.assertEqual(sha(ROOT/p),self.raw[key])
    def test_03_source_plan_matches_recovery(self):self.assertEqual(canonical(requests()),canonical(self.raw['requests']))
    def test_04_source_texture_matches_previous_decode(self):
        old=json.loads((ROOT/'reverse-engineering/raw/l3-textured105/texture.json').read_bytes());self.assertEqual(self.raw['texture_raw_sha256'],old['texture_raw_sha256']);self.assertEqual(self.raw['rgba_sha256'],old['rgba_sha256']);self.assertEqual([self.raw['width'],self.raw['height']],[2048,1024])
    def test_05_source_variants_have_snap_and_external_paths(self):
        vs=self.saved['source']['variants'];self.assertEqual(len(vs),8);self.assertEqual({(v['platform'],v['pixel_snap'],v['external_alpha']) for v in vs},{(p,s,a) for p in [5,9] for s in [False,True] for a in [False,True]})
    def test_06_vertex_identity_and_uv_passthrough(self):
        v=self.v();self.assertEqual(v['clip'],[.25,-.25,.1,1]);self.assertEqual(v['uv'],[.2,.8]);self.assertEqual(v['window'],[675.,900.])
    def test_07_flip_before_object_translation(self):
        m=list(IDENTITY);m[3]=3;m[7]=5;v=self.v(flip=[-1,-1],object_to_world=m);self.assertEqual(v['world'],[2.75,5.25,.1,1])
    def test_08_object_and_vp_columns_not_transposed(self):
        o=[2,0,0,3,0,4,0,5,0,0,6,7,0,0,0,1];vp=[10,0,0,11,0,20,0,13,0,0,30,17,0,0,0,1];v=self.v(p=[1,2,3,1],object_to_world=o,matrix_vp=vp);self.assertEqual(v['world'],[5,13,25,1]);self.assertEqual(v['clip'],[61,273,767,1])
    def test_09_source_color_multiply_order(self):self.assertEqual(self.v(vertex_color=[.5]*4,material_color=[.5]*4,renderer_color=[.5]*4)['varying_color'],[.125]*4)
    def test_10_round_even_positive_negative_half_ties(self):
        for x,y in [(-2.5,-2),(-1.5,-2),(-.5,0),(.5,0),(1.5,2),(2.5,2),(3.5,4)]:self.assertEqual(round_even(x),y)
    def test_11_round_even_not_nearest_away_from_zero(self):self.assertEqual(round_even(.499999),0);self.assertEqual(round_even(.500001),1);self.assertEqual(round_even(-.500001),-1)
    def test_12_pixel_snap_preserves_clip_zw_uv_color(self):
        p=[.1234,-.2345,.456,1];a=self.v(p=p);b=self.v(p=p,pixel_snap=True);self.assertEqual(a['clip'][2:],b['clip'][2:]);self.assertEqual(a['uv'],b['uv']);self.assertEqual(a['varying_color'],b['varying_color']);self.assertNotEqual(a['clip'][:2],b['clip'][:2])
    def test_13_pixel_snap_source_coordinates_and_half_pixel_bound(self):
        a=self.saved['vertices']['False'];b=self.saved['vertices']['True']
        for before,after in zip(a,b):
            for x,y in zip(before['window'],after['window']):self.assertLessEqual(abs(x-y),.500000001);self.assertAlmostEqual(y,round(y),10)
            self.assertEqual(before['clip'][2:],after['clip'][2:]);self.assertEqual(before['uv'],after['uv'])
    def test_14_pixel_snap_divides_then_restores_nonunit_w(self):
        vp=list(IDENTITY);vp[14]=.25;v=self.v(p=[.1234,-.2345,2.,1],matrix_vp=vp,pixel_snap=True);self.assertEqual(v['clip'][3],1.5)
        for i,dim in enumerate([1080,2400]):self.assertEqual(v['clip'][i],1.5*(v['snap']['rounded'][i]/(dim*.5)))
    def test_15_no_undefined_w_or_nonaffine_object_guess(self):
        vp=list(IDENTITY);vp[15]=0
        with self.assertRaises(ValueError):self.v(matrix_vp=vp)
        o=list(IDENTITY);o[12]=1
        with self.assertRaises(ValueError):self.v(object_to_world=o)
        with self.assertRaises(ValueError):self.v(p=[1,2,3,0])
    def test_16_invalid_input_dimensions_and_variant_rejected(self):
        for size in [[0,1],[True,2],[1.,2],[2**21,2]]:
            with self.assertRaises(ValueError):self.v(screen=size)
        with self.assertRaises(ValueError):self.v(pixel_snap=1)
        with self.assertRaises(ValueError):self.v(p=[math.nan,0,0,1])
        with self.assertRaises(ValueError):round_even(2**25)
    def test_17_perspective_correct_varying_not_linear_uv(self):
        vs=[self.v(uv=[0,0]),self.v(uv=[1,0]),self.v(uv=[0,1])]
        for v,w in zip(vs,[1,2,4]):v['clip'][3]=w
        r=interpolate(vs,[1/3]*3);self.assertAlmostEqual(r['uv'][0],2/7);self.assertAlmostEqual(r['uv'][1],1/7);self.assertNotEqual(r['uv'],[1/3,1/3])
    def test_18_interpolated_color_uses_same_perspective_weights(self):
        vs=[self.v() for _ in range(3)]
        for v,w,c in zip(vs,[1,2,4],[[1,0,0,1],[0,1,0,1],[0,0,1,1]]):v['clip'][3]=w;v['varying_color']=c
        self.assertAlmostEqual(interpolate(vs,[1/3]*3)['varying_color'][0],4/7)
    def test_19_outside_triangle_or_nonpositive_w_rejected(self):
        vs=[self.v() for _ in range(3)]
        with self.assertRaises(ValueError):interpolate(vs,[-.1,.5,.6])
        vs[0]['clip'][3]=-1
        with self.assertRaises(ValueError):interpolate(vs,[1/3]*3)
    def test_20_actual_same_fixed_pixel_snap_changes_uv_and_filtered_color(self):
        rows={r['name']:r for r in self.saved['queries']};changed=[]
        for i in range(7):
            a,b=rows[f'source_seed{i}_snap0'],rows[f'source_seed{i}_snap1'];self.assertEqual(a['window'],b['window']);self.assertNotEqual(a['uv'],b['uv']);changed.append(a['filtered']['rgba']!=b['filtered']['rgba'])
        self.assertTrue(any(changed))
    def test_21_counts_recounted_not_only_header(self):
        d=self.saved;self.assertEqual(d['counts']['vertices_per_variant'],len(d['vertices']['False']));self.assertEqual(d['counts']['fixed_pixel_queries'],len(d['queries']));self.assertEqual(d['counts']['unique_decoded_pixels'],len(d['pixels']));self.assertEqual(len(d['pixels']),len({(p['x'],p['y']) for p in d['pixels']}));self.assertEqual(len(d['queries']),14)
    def test_22_center_vs_four_equal_weights(self):
        f=footprint([.5,.5],[2,2]);self.assertEqual([t['weight'] for t in f['taps']],[.25]*4)
        f=footprint([.25,.25],[2,2]);self.assertEqual([t['weight'] for t in f['taps']],[1,0,0,0])
    def test_23_known_rgba_checker_bilinear(self):
        pixels={(0,0):[255,0,0,0],(1,0):[0,255,0,255],(0,1):[0,0,255,255],(1,1):[255,255,255,0]};self.assertEqual(bilinear([.5,.5],[2,2],pixels)['rgba'],[.5,.5,.5,.5])
    def test_24_filter_before_premultiply_not_reverse(self):
        pixels={(0,0):[255,0,0,0],(1,0):[0,0,255,255],(0,1):[255,0,0,0],(1,1):[0,0,255,255]};filtered=bilinear([.5,.5],[2,2],pixels)['rgba'];actual=fragment(filtered,[1]*4);self.assertEqual(actual,[.25,0,.25,.5]);self.assertNotEqual(actual,[0,0,.5,.5])
    def test_25_actual_four_neighbor_mean_independent(self):
        r=next(r for r in self.saved['sampler_only'] if r['name']=='four_equal_weights');pixels={(p['x'],p['y']):p['rgba8'] for p in self.saved['pixels']}
        for i,v in enumerate(r['filtered']['rgba']):self.assertAlmostEqual(v,sequential_sum(pixels[tuple(t['xy'])][i]/255 for t in r['filtered']['taps'])/4)
    def test_26_clamp_to_full_texture_not_sprite_crop(self):
        rows={r['name']:r for r in self.saved['sampler_only']};lo=rows['texture_clamp_low']['filtered'];hi=rows['texture_clamp_high']['filtered'];self.assertEqual({tuple(t['xy']) for t in lo['taps']},{(0,0)});self.assertEqual({tuple(t['xy']) for t in hi['taps']},{(2047,1023)});self.assertTrue(any(t['xy'][0]<1310 for t in rows['atlas_rect_left_neighbor']['filtered']['taps']))
    def test_27_missing_pixel_never_becomes_null_or_black(self):
        with self.assertRaises(ValueError):bilinear([.5,.5],[2,2],{(0,0):[0]*4})
    def test_28_unknown_wrap_nonfinite_or_bad_pixels_rejected(self):
        px={(0,0):[0]*4}
        with self.assertRaises(ValueError):bilinear([0,0],[1,1],px,wrap_u=0)
        with self.assertRaises(ValueError):bilinear([math.inf,0],[1,1],px)
        with self.assertRaises(ValueError):bilinear([3,0],[1,1],px)
        with self.assertRaises(ValueError):bilinear([0,0],[1,1],{(0,0):[256]*4})
    def test_29_external_alpha_then_tint_then_premultiply(self):self.assertEqual(fragment([1,1,1,0],[.5]*4,.8,.5),[.1,.1,.1,.2])
    def test_30_missing_external_or_invalid_fragment_rejected(self):
        with self.assertRaises(ValueError):fragment([1]*4,[1]*4,enable_external_alpha=1)
        with self.assertRaises(ValueError):fragment([math.nan]*4,[1]*4)
        with self.assertRaises(ValueError):fragment([1]*4,[1]*4,enable_external_alpha=math.nan)
    def test_31_actual_filtered_fragment_premul_and_over(self):
        for row in self.saved['queries']:
            self.assertEqual(row['fragment'],fragment(row['filtered']['rgba'],row['varying']['varying_color']));self.assertEqual(row['over_half_gray'],blend(row['fragment'],[.5,.5,.5,1.]));self.assertGreaterEqual(row['fragment'][3],0);self.assertLessEqual(row['fragment'][3],1)
    def test_32_no_gpu_or_engine_policy_promotion(self):
        d=self.saved;self.assertIn('NOT Unity readback or render',d['scope']);self.assertIn('UNPROVED',d['custom_binding_status']);self.assertIn('no inferred sRGB',d['texture']['scope']);self.assertIn('not actual runtime',d['uniform_scope']);self.assertIn('NOT arbitrary GLSL interpreter',d['source']['scope'])
