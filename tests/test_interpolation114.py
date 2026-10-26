import copy,gzip,json,math,struct,unittest
from tools.verify import interpolation114 as report
from tools.verify.interpolation114_native import CurveFixture,key,f32,bits
from tools.verify.balloon_animation import decode_stream

def patch(raw,address,data):
    r=copy.deepcopy(raw);changed=0
    for w in r['windows']+r['cells']:
        b=bytearray.fromhex(w['hex']);i=address-w['va']
        if 0<=i and i+len(data)<=len(b):b[i:i+len(data)]=data;w['hex']=b.hex();changed+=1
    assert changed;return r
class NativeInterpolation114(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.raw=report.load_raw();cls.saved=json.load(gzip.open(report.OUT));cls.smooth=[key(0,0),key(1,1)]
    def fixture(self,keys=None,**kwargs):return CurveFixture(self.raw,self.smooth if keys is None else keys,**kwargs)
    def test_01_input_pins(self):
        for p,h in self.saved['inputs'].items():self.assertEqual(report.digest(report.ROOT/p),h,p)
    def test_02_recovery_tool_pin(self):self.assertEqual(self.raw['tool_sha256'],report.digest(report.ROOT/'tools/recovery/interpolation114.py'))
    def test_03_deterministic_builder(self):self.assertEqual(report.build(),self.saved)
    def test_04_original_unwind_extents(self):
        base=self.raw['unwind_header']['va']
        for row in self.raw['followed']:
            r=row['unwind']
            if r:
                delta,size=struct.unpack('<iI',bytes.fromhex(r['fde_hex'])[8:16]);self.assertEqual(r['fde_va']+8+delta,row['entry']);self.assertEqual(size,r['end']-r['start']);self.assertEqual(base+struct.unpack('<i',bytes.fromhex(r['table_hex'])[:4])[0],r['start'])
    def test_05_registration_literal(self):
        occurrence=next(s for s in self.raw['strings'] if s['text']=='UnityEngine.AnimationCurve::Evaluate')['occurrences'];self.assertEqual(occurrence[0]['va'],0x1294c9)
    def test_06_api_wrapper_reaches_native(self):
        r=self.fixture().api(.25);self.assertEqual(r['value'],.15625);self.assertIn(0x952608,r['executed_addresses']);self.assertEqual(len(r['managed_bridge_calls']),1)
    def test_07_cold_cache_native_coefficients(self):
        r=self.fixture().evaluate(.25);self.assertEqual(r['cache']['coefficients'],[-2.,3.,0.,0.]);self.assertEqual(r['value'],.15625);self.assertFalse(r['math_import_calls'])
    def test_08_cache_hit_is_shorter(self):
        f=self.fixture();cold=f.evaluate(.25);hot=f.evaluate(.5);self.assertEqual(hot['value'],.5);self.assertLess(hot['instruction_count'],cold['instruction_count']);self.assertNotIn(0x952a80,hot['executed_addresses'])
    def test_09_cache_miss_executes_generator(self):self.assertIn(0x952a80,self.fixture().evaluate(.25)['executed_addresses'])
    def test_10_external_cache(self):self.assertEqual(self.fixture().evaluate(.25,True)['value'],.15625)
    def test_11_empty(self):self.assertEqual(self.fixture([]).evaluate(.25)['value'],0)
    def test_12_single(self):self.assertEqual(self.fixture([key(2,7)]).evaluate(-50)['value'],7)
    def test_13_linear(self):self.assertEqual(self.fixture([key(0,0,out_slope=1),key(1,1,in_slope=1)]).evaluate(.25)['value'],.25)
    def test_14_unweighted_ideal_comparison(self):
        for family in self.saved['families']:
            for native,ref in zip(family['runs'],family['hermite_reference']):self.assertAlmostEqual(native['value'],ref,places=6)
    def test_15_cache_duration_floor_is_not_direct_segment(self):
        f=self.fixture([key(0,0),key(1e-5,1)]);t=f32(5e-6);self.assertAlmostEqual(f.evaluate(t)['value'],.00725,places=7);self.assertEqual(f.segment(t)['value'],.5)
    def test_16_duration_floor_opcode_counterfactual(self):
        word=bits(1e-8);r=patch(self.raw,0x952aa4,struct.pack('<I',0x52800009|((word&65535)<<5)));r=patch(r,0x952aa8,struct.pack('<I',0x72a00009|((word>>16)<<5)))
        self.assertAlmostEqual(CurveFixture(r,[key(0,0),key(1e-5,1)]).evaluate(f32(5e-6))['value'],.5,places=6)
    def test_17_arithmetic_opcode_counterfactual(self):
        f=self.fixture();word=struct.unpack('<I',f.source(0x95265c,4))[0];r=patch(self.raw,0x95265c,struct.pack('<I',word^0x2000));self.assertNotEqual(CurveFixture(r,self.smooth).evaluate(.25)['value'],.15625)
    def test_18_tangent_load_counterfactual(self):
        word=struct.unpack('<I',self.fixture().source(0x952adc,4))[0];r=patch(self.raw,0x952adc,struct.pack('<I',word-(1<<10)));keys=[key(0,0,out_slope=2),key(1,1)];self.assertEqual(CurveFixture(r,keys).evaluate(.25)['cache']['coefficients'][2],0)
    def test_19_positive_infinity_step_left(self):self.assertEqual(self.fixture([key(0,2,out_slope=math.inf),key(1,7)]).evaluate(.25)['value'],2)
    def test_20_negative_infinity_step_right(self):self.assertEqual(self.fixture([key(0,2,out_slope=-math.inf),key(1,7)]).evaluate(.25)['value'],7)
    def test_21_positive_infinity_precedes_negative(self):self.assertEqual(self.fixture([key(0,2,out_slope=math.inf),key(1,7,in_slope=-math.inf)]).evaluate(.25)['value'],2)
    def test_22_raw_mode0_reflects(self):self.assertEqual(self.fixture([key(0,0,out_slope=1),key(1,1,in_slope=1)],pre=0).evaluate(-.25)['value'],.25)
    def test_23_raw_mode1_repeats(self):self.assertEqual(self.fixture([key(0,0,out_slope=1),key(1,1,in_slope=1)],post=1).evaluate(1.25)['value'],.25)
    def test_24_raw_mode2_clamps(self):self.assertEqual(self.fixture(post=2).evaluate(1.25)['value'],1)
    def test_25_weighted_quadratic_is_native(self):
        r=self.fixture([key(0,0,weighted_mode=2,out_weight=0),key(1,1,weighted_mode=1,in_weight=2/3)]).evaluate(.25);self.assertEqual(r['value'],.5);self.assertIn(0x951f60,r['executed_addresses']);self.assertFalse(r['math_import_calls'])
    def test_26_weighted_default_linear_x(self):
        r=self.fixture([key(0,0,weighted_mode=2),key(1,1,weighted_mode=1)]).evaluate(.25);self.assertAlmostEqual(r['value'],.15625,places=6);self.assertFalse(r['math_import_calls'])
    def test_27_general_weighted_requires_external_math(self):
        with self.assertRaises(Exception):self.fixture([key(0,0,weighted_mode=2,out_weight=.1),key(1,1,weighted_mode=1,in_weight=.7)]).evaluate(.25)
    def test_28_import_identities(self):
        bindings=self.fixture().enable_host_math();self.assertEqual([b['symbol'] for b in bindings],['atan2f','logf','exp','cosf'])
    def test_29_host_math_case_is_labeled(self):
        for case in self.saved['weighted']:
            if case['host_math_bridge']:self.assertTrue(any(r['math_import_calls'] for r in case['runs']));self.assertIn('NOT Android',case['scope'])
    def test_30_weighted_reference_comparison(self):
        for case in self.saved['weighted']:
            for r,ref in zip(case['runs'],case['reference']):self.assertAlmostEqual(r['value'],ref,delta=2e-5)
    def test_31_second_object_address(self):self.assertEqual(self.fixture(base=0x7000000).evaluate(.25)['value_bits'],bits(.15625))
    def test_32_missing_literal_rejected(self):
        r=copy.deepcopy(self.raw);r['cells']=[c for c in r['cells'] if not (c['va']<0x146d20 and c['va']+len(c['hex'])//2>0x146d10)]
        with self.assertRaises(Exception):CurveFixture(r,self.smooth).evaluate(2)
    def test_33_missing_generator_rejected(self):
        r=copy.deepcopy(self.raw);r['windows']=[w for w in r['windows'] if not w['va']<=0x952a80<w['va']+len(w['hex'])//2]
        with self.assertRaises(Exception):CurveFixture(r,self.smooth).evaluate(.25)
    def test_34_original_key_fixture(self):
        s=self.saved['source_curve'];self.assertEqual(s['identity']['path_id'],4783);self.assertEqual(len(s['serialized_curve']['m_Curve']),3)
        for r in s['runs']:self.assertAlmostEqual(r['run']['value'],r['hermite_reference'],delta=2e-6)
    def test_35_native_record_producer(self):
        r=self.fixture().produce_records(7);self.assertEqual(r['record_count'],3);self.assertEqual(r['records'][0]['time'],-3.4028234663852886e38);self.assertEqual(r['records'][1]['coeff'],[-2,3,0,0]);self.assertEqual(r['records'][2]['coeff'],[0,0,0,1]);self.assertIn(0x6c4360,r['run']['executed_addresses'])
    def test_36_native_packing_not_zero_fill(self):
        f=self.fixture();f.produce_records(7);a=f.pack_prepared_records(0);b=f.pack_prepared_records(0xa5);self.assertEqual(a['bytes_hex'],b['bytes_hex']);self.assertEqual(a['byte_count'],84)
    def test_37_native_frame_layout(self):
        p=self.saved['native_frame_packing'];data=bytes.fromhex(p['bytes_hex']);frames=decode_stream(struct.unpack('<'+'I'*(len(data)//4),data),8);self.assertEqual(frames,p['decoded_frames']);self.assertEqual([f['keys'][0]['index'] for f in frames],[7,7,7])
    def test_38_producer_index_counterfactual(self):self.assertEqual(self.fixture().produce_records(11)['records'][1]['index'],11)
    def test_39_original_stream_arithmetic_adapter_is_not_consumer(self):
        r=self.saved['streamed_adapter'];self.assertIn('NOT native StreamedClip',r['scope'])
        for v in r['runs']:self.assertAlmostEqual(v['native']['value'],v['float64_polynomial'],delta=2e-5)
    def test_40_no_animator_equivalence_promotion(self):self.assertIn('NO AnimationClip streamed/dense or Animator blending equivalence',self.saved['scope'])
if __name__=='__main__':unittest.main()
