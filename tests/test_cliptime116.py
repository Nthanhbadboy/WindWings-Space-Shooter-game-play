import copy,gzip,json,struct,unittest
import capstone
from tools.verify import cliptime116 as report,packed115
from tools.verify.cliptime116_native import ClipFixture
from tools.verify.interpolation114_native import bits,floatbits

def patch(raw,address,word):
    raw=copy.deepcopy(raw)
    for w in raw['windows']+raw['cells']:
        i=address-w['va'];b=bytearray.fromhex(w['hex'])
        if 0<=i and i+4<=len(b):b[i:i+4]=struct.pack('<I',word);w['hex']=b.hex()
    return raw
class NativeClipTime116(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.a=packed115.load_raw();cls.b=report.load_raw();cls.saved=json.load(gzip.open(report.OUT));cls.dense=dict(frames=3,curves=2,rate=2,begin=.5,samples=[0,10,10,20,20,30])
    def fixture(self,**kwargs):return ClipFixture(self.a,self.b,dense=self.dense,**kwargs)
    def test_01_all_input_pins(self):
        for path,h in self.saved['inputs'].items():self.assertEqual(report.digest(report.ROOT/path),h,path)
    def test_02_recovery_tool_pin(self):self.assertEqual(self.b['tool_sha256'],report.digest(report.ROOT/'tools/recovery/cliptime116.py'))
    def test_03_deterministic_builder(self):self.assertEqual(report.build(),self.saved)
    def test_04_native_fde_extents(self):
        for entry in self.b['followed']:
            r=entry['unwind']
            if r:
                delta,n=struct.unpack('<iI',bytes.fromhex(r['fde_hex'])[8:16]);self.assertEqual(r['fde_va']+8+delta,entry['entry']);self.assertEqual(n,r['end']-r['start'])
    def test_05_exact_import_identities(self):self.assertEqual([x['symbol'] for x in self.saved['bindings']],['modff','memcpy'])
    def test_06_nonempty_dense_is_labelled_synthetic(self):self.assertIn('Synthetic',self.saved['dense']['scope'])
    def test_07_original_source_dense_is_empty(self):
        d=self.saved['source']['dense_metadata'];self.assertEqual((d['m_FrameCount'],d['m_CurveCount'],d['m_SampleArray']),(420,0,[]))
    def test_08_actual_full_source_time_chain_executed(self):
        for r in self.saved['source']['runs']:
            pc=r['native']['run']['executed_addresses']
            for a in (0x6d2e94,0xb93158,0x6df270,0x6df310,0x6df768):self.assertIn(a,pc)
            self.assertNotIn(0x6df518,pc)
    def test_09_positive_integer_loops_to_start(self):
        r=self.fixture().helper(1);self.assertEqual((r['sample_time'],r['phase'],r['cycles']),(0,0,1))
    def test_10_negative_integer_is_not_python_modulo(self):
        r=self.fixture().helper(-1);self.assertEqual((r['sample_time'],r['phase'],r['cycles']),(1,1,-2));self.assertNotEqual(r['phase'],-1%1)
    def test_11_negative_fraction(self):
        r=self.fixture().helper(-.25);self.assertEqual((r['phase'],r['cycles']),(.75,-1))
    def test_12_nonloop_clamps(self):
        f=self.fixture();self.assertEqual(f.helper(-.25,loop=False)['phase'],0);self.assertEqual(f.helper(1.25,loop=False)['phase'],1)
    def test_13_loop_offset(self):self.assertEqual(self.fixture().helper(.25,offset=.5)['phase'],.75)
    def test_14_nonloop_ignores_offset_for_phase(self):self.assertEqual(self.fixture().helper(.25,offset=.5,loop=False)['phase'],.25)
    def test_15_negative_direction(self):self.assertEqual(self.fixture().helper(.25,direction=-1)['phase'],.75)
    def test_16_direction_negative_zero_signbit(self):self.assertEqual(self.fixture().helper(.25,direction=-0.)['phase'],.75)
    def test_17_reverse_cycles(self):self.assertEqual(self.fixture().helper(-.25,direction=-1)['cycles'],1)
    def test_18_start_stop_map_normalized_query(self):self.assertEqual(self.fixture().helper(.25,start=2,stop=4)['sample_time'],2.5)
    def test_19_native_round_ties_away(self):self.assertEqual(self.fixture().helper(.25,quantization_rate=2)['sample_time'],.5)
    def test_20_quantized_return_can_exceed_stop(self):
        r=self.fixture().helper(1,start=.1,stop=.9,quantization_rate=2,loop=False);self.assertEqual((r['sample_time'],r['phase']),(1,1))
    def test_21_zero_duration_keeps_phase(self):
        r=self.fixture().helper(.25,start=2,stop=2,quantization_rate=2);self.assertEqual((r['sample_time'],r['phase']),(2,.25))
    def test_22_negative_duration_disables_quantization(self):self.assertEqual(self.fixture().helper(.25,start=4,stop=2,quantization_rate=2)['sample_time'],3.5)
    def test_23_dense_interpolation(self):self.assertEqual(self.fixture().sample(.75)['output_bits'],[bits(5),bits(15)])
    def test_24_dense_negative_half_frame_extrapolates(self):self.assertEqual(self.fixture().sample(.25)['output_bits'],[bits(-5),bits(5)])
    def test_25_dense_far_before_begin_same_clamped_rows(self):self.assertEqual(self.fixture().sample(0)['output_bits'],[bits(0),bits(10)])
    def test_26_dense_after_last_frame(self):self.assertEqual(self.fixture().sample(2)['output_bits'],[bits(20),bits(30)])
    def test_27_dense_modff_receipt(self):
        r=self.fixture().sample(.25);self.assertEqual(r['external_calls'],[dict(symbol='modff',input_bits=bits(-.5),fraction_bits=bits(-.5),integer_bits=bits(-0.))])
    def test_28_mixed_order(self):
        r=self.saved['mixed']['runs'][0];self.assertEqual(r['output_bits'],[bits(.15625),1001,bits(5),bits(15),bits(77),0x7fc12345])
    def test_29_constant_nan_payload_preserved(self):self.assertEqual(self.fixture(constant=[0x7fc12345]).sample(.75)['output_bits'][-1],0x7fc12345)
    def test_30_original_aggregate_initializer_sets_constant_count(self):
        f=self.fixture(constant=[1,2]);self.assertEqual(f.w(f.cache+24),2);self.assertEqual(f.allocations,[dict(size=32,alignment=8)])
    def test_31_prefill_does_not_supply_outputs(self):self.assertEqual(self.fixture(prefill=0).sample(.75)['output_bits'],self.fixture(prefill=0xa5).sample(.75)['output_bits'])
    def test_32_source_wraps_one_to_zero(self):
        runs=self.saved['source']['runs'];self.assertEqual(runs[0]['native']['output_bits'],runs[4]['native']['output_bits']);self.assertEqual(runs[4]['native']['stream_last_time'],0)
    def test_33_source_rewind_and_repeat(self):
        runs=self.saved['source']['runs'];self.assertEqual(runs[1]['native']['output_bits'],runs[-1]['native']['output_bits']);self.assertEqual(runs[-2]['native']['output_bits'],runs[-1]['native']['output_bits'])
    def test_34_source_values_all_match_separate_comparison(self):
        self.assertEqual(self.saved['counts']['source_channel_values'],930)
        for r in self.saved['source']['runs']:self.assertEqual(r['native']['output_bits'],r['stream_reference']['output_bits'])
    def test_35_missing_import_bridge_is_rejected(self):
        with self.assertRaises(Exception):self.fixture(bridge=False).helper(.25)
    def test_36_time_arithmetic_opcode_counterfactual(self):
        pc=0xb9323c;word=struct.unpack('<I',packed115.original_bytes(self.b,pc,4))[0];f=ClipFixture(patch(self.a,pc,word^0x2000),patch(self.b,pc,word^0x2000),dense=self.dense)
        self.assertNotEqual(f.helper(.25)['sample_time'],.25)
    def test_37_dense_arithmetic_opcode_counterfactual(self):
        pc=0x6df55c;word=struct.unpack('<I',packed115.original_bytes(self.b,pc,4))[0];f=ClipFixture(patch(self.a,pc,word^0x2000),patch(self.b,pc,word^0x2000),dense=self.dense)
        self.assertNotEqual(f.sample(.75)['output_bits'],[bits(5),bits(15)])
    def test_38_serialized_native_cycle_offset_anchor(self):
        b=packed115.original_bytes(self.b,0xb705a4,4);i=next(capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM).disasm(b,0xb705a4));self.assertEqual(i.op_str,'x3, x20, #0x608')
    def test_39_no_runtime_promotion(self):
        self.assertIn('NOT Android-libm parity',self.saved['scope']);self.assertIn('NOT actual Animator context',self.saved['source']['scope'])
    def test_40_actual_negative_relative_pointer_is_consumed(self):
        f=self.fixture();self.assertTrue(f.q(f.blob+0x5f0)&(1<<63));self.assertEqual(f.sample(.75,True,False)['output_bits'],[bits(5),bits(15)])
if __name__=='__main__':unittest.main()
