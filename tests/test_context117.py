import copy,gzip,json,struct,unittest
import capstone
from tools.verify import context117 as report,packed115,cliptime116
from tools.verify.context117_native import ContextFixture
from tools.verify.interpolation114_native import bits,floatbits

def patched(raw,pc,word):
    r=copy.deepcopy(raw)
    for w in r['windows']+r['cells']:
        b=bytearray.fromhex(w['hex']);i=pc-w['va']
        if 0<=i and i+4<=len(b):b[i:i+4]=struct.pack('<I',word);w['hex']=b.hex()
    return r
class NativeContext117(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.a=packed115.load_raw();cls.b=cliptime116.load_raw();cls.c=report.load_raw();cls.saved=json.load(gzip.open(report.OUT))
    def fixture(self,**kwargs):return ContextFixture(self.a,self.b,self.c,packed=packed115.synthetic_stream(),continuous=1,**kwargs)
    def decode(self,pc):return next(capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM).disasm(packed115.original_bytes(self.c,pc,4),pc))
    def test_01_input_pins(self):
        for path,h in self.saved['inputs'].items():self.assertEqual(report.digest(report.ROOT/path),h,path)
    def test_02_recovery_tool_pin(self):self.assertEqual(self.c['tool_sha256'],report.digest(report.ROOT/'tools/recovery/context117.py'))
    def test_03_deterministic_builder(self):self.assertEqual(report.build(),self.saved)
    def test_04_actual_fde_entries(self):
        for e in self.c['followed']:
            self.assertIsNotNone(e['unwind']);r=e['unwind'];delta,n=struct.unpack('<iI',bytes.fromhex(r['fde_hex'])[8:16]);self.assertEqual(r['fde_va']+8+delta,e['entry']);self.assertEqual(n,r['end']-r['start'])
    def test_05_constructor_vptr_store(self):self.assertEqual(self.decode(0xb69d4c).op_str,'x8, [x19]')
    def test_06_original_vtable_slot(self):self.assertEqual(self.fixture().q(0x10c4050),0xb6bf94)
    def test_07_virtual_slot_load(self):self.assertEqual(self.decode(0x6d3760).op_str,'x8, [x8, #0xa8]')
    def test_08_duration_is_stop_minus_start(self):
        f=self.fixture();f.configure_time(start=2,stop=4);f.configure_node(current=.5);self.assertEqual(f.acquire()['context']['current_bits'],bits(.25))
    def test_09_null_clip_blob_duration_zero(self):
        f=self.fixture();f.sq(f.native_clip+0x1e0,0);f.configure_node(current=7,previous=9);r=f.acquire();self.assertEqual((r['context']['current_bits'],r['context']['previous_bits']),(0,0))
    def test_10_context_calls_real_native_duration(self):self.assertIn(0xb6bf94,self.fixture().acquire()['run']['executed_addresses'])
    def test_11_no_duration_service_substitution(self):self.assertEqual(self.fixture().acquire()['external_calls'],[])
    def test_12_rounding_is_not_nearest_f32(self):
        f=self.fixture();f.configure_node(current=.7);r=f.acquire();self.assertEqual(r['context']['current_bits'],bits(.7)+1)
    def test_13_negative_ratio_ceiling(self):
        f=self.fixture();f.configure_node(current=-.7);self.assertEqual(f.acquire()['context']['current_bits'],bits(-.7))
    def test_14_positive_underflow_moves_to_min_subnormal(self):
        f=self.fixture();f.configure_node(current=1e-50);self.assertEqual(f.acquire()['context']['current_bits'],1)
    def test_15_negative_underflow_keeps_negative_zero(self):
        f=self.fixture();f.configure_node(current=-1e-50);self.assertEqual(f.acquire()['context']['current_bits'],0x80000000)
    def test_16_previous_clock_also_directed(self):
        f=self.fixture();f.configure_node(previous=.7);self.assertEqual(f.acquire()['context']['previous_bits'],bits(.7)+1)
    def test_17_zero_duration_both_zero(self):
        f=self.fixture();f.configure_time(start=1,stop=1);f.configure_node(current=7,previous=-3);r=f.acquire()['context'];self.assertEqual((r['current_bits'],r['previous_bits']),(0,0))
    def test_18_direction_negative_zero_bit_copy(self):
        f=self.fixture();f.configure_node(direction=-0.);self.assertEqual(f.acquire()['context']['direction_bits'],0x80000000)
    def test_19_context_offset_copy(self):
        f=self.fixture();f.configure_node(offset=.25);self.assertEqual(f.acquire()['context']['offset_bits'],bits(.25))
    def test_20_quantization_field_copy(self):
        f=self.fixture();f.configure_node(quantization=2);self.assertEqual(f.acquire()['context']['quantization_bits'],bits(2))
    def test_21_raw_flag_bytes_copy(self):
        f=self.fixture();f.configure_node(node_flag=7,parameter_flag=11,secondary_flag=13);r=f.acquire()['context'];self.assertEqual((r['node_flag'],r['parameter_flag'],r['secondary_flag']),(7,11,13))
    def test_22_prefill_does_not_supply_defined_context_fields(self):
        f=self.fixture();f.configure_node(current=.7);self.assertEqual(f.acquire(0)['context'],f.acquire(0xa5)['context'])
    def test_23_caller_context_pointer_selection_native(self):
        r=self.fixture().staged_sample();self.assertEqual([(s['entry'],s['stop_before']) for s in r['stages']],[(0x6d3924,0x6d3960),(0x6d39bc,0x6d39c0),(0x6d3a20,0x6d3a48)])
    def test_24_staged_query_load_is_native(self):self.assertEqual(self.decode(0x6d3a24).op_str,'s0, [sp, #0x1a0]')
    def test_25_real_context_to_real_time_to_real_stream(self):
        f=self.fixture();f.configure_node(current=.7);r=f.staged_sample();pcs={pc for s in r['stages'] for pc in s['run']['executed_addresses']}
        for a in (0x6d3744,0xb6bf94,0x6d2e94,0xb93158,0x6df270,0x6df310,0x6df768):self.assertIn(a,pcs)
    def test_26_phase_store_is_native(self):
        f=self.fixture();f.configure_node(current=.7);r=f.staged_sample();self.assertEqual(r['stored_phase_bits'],bits(.7)+1);self.assertIn(0x6d3a44,r['stages'][-1]['run']['executed_addresses'])
    def test_27_only_modff_substitution_in_staged_sample(self):
        r=self.fixture().staged_sample();self.assertEqual([c['symbol'] for c in r['external_calls']],['modff'])
    def test_28_original_source_count_and_bits(self):
        self.assertEqual(self.saved['counts']['source_channel_values'],930)
        for row in self.saved['source']['runs']:self.assertEqual(row['native']['output_bits'],row['stream_reference']['output_bits'])
    def test_29_source_rewind_and_same_time(self):
        r=self.saved['source']['runs'];self.assertEqual(r[2]['native']['output_bits'],r[7]['native']['output_bits']);self.assertEqual(r[7]['native']['output_bits'],r[8]['native']['output_bits'])
    def test_30_source_sub_end_double_can_round_up_to_loop_boundary(self):
        r=self.saved['source']['runs'][-1];self.assertLess(r['input']['requested_normalized_double'],1);self.assertEqual(r['native']['context']['current_bits'],bits(1));self.assertEqual(r['native']['sample_time_bits'],bits(0))
    def test_31_loop_flag_consumption_native(self):self.assertEqual(self.decode(0x6d3a20).op_str,'w8, [x19, #0x19d]')
    def test_32_synthetic_direction_controls_change_output(self):self.assertNotEqual(self.saved['synthetic_controls'][0]['native']['output_bits'],self.saved['synthetic_controls'][1]['native']['output_bits'])
    def test_33_negative_zero_control_matches_reverse(self):self.assertEqual(self.saved['synthetic_controls'][1]['native']['output_bits'],self.saved['synthetic_controls'][2]['native']['output_bits'])
    def test_34_original_context_offset_changes_time(self):self.assertNotEqual(self.saved['synthetic_controls'][0]['native']['sample_time_bits'],self.saved['synthetic_controls'][3]['native']['sample_time_bits'])
    def test_35_opcode_counterfactual_directed_conversion(self):
        pc=0x6d3798;word=0x14000000|((0x6d37fc-pc)//4);f=ContextFixture(patched(self.a,pc,word),patched(self.b,pc,word),patched(self.c,pc,word),packed=packed115.synthetic_stream(),continuous=1);f.configure_node(current=.7);self.assertEqual(f.acquire()['context']['current_bits'],bits(.7))
    def test_36_opcode_counterfactual_real_duration(self):
        pc=0xb6bfa4;word=struct.unpack('<I',packed115.original_bytes(self.c,pc,4))[0]^0x1000;f=ContextFixture(patched(self.a,pc,word),patched(self.b,pc,word),patched(self.c,pc,word),packed=packed115.synthetic_stream(),continuous=1);f.configure_time(start=2,stop=4);f.configure_node(current=.5);self.assertNotEqual(f.acquire()['context']['current_bits'],bits(.25))
    def test_37_rejected_candidate_not_executed(self):
        for r in self.saved['context_cases']:self.assertNotIn(0xb6a838,r['native']['run']['executed_addresses'])
    def test_38_duration_original_slot_read_receipt(self):self.assertIn(dict(va=0x10c4050,size=8),self.fixture().acquire()['run']['source_reads'])
    def test_39_relocated_fixture_base(self):
        f=self.fixture(base=0x7000000);f.configure_node(current=.7);self.assertEqual(f.acquire()['context']['current_bits'],bits(.7)+1)
    def test_40_no_observed_animator_promotion(self):
        self.assertIn('NOT observed Animator',self.saved['scope']);self.assertIn('manual original caller intervals',self.saved['source']['scope'])
if __name__=='__main__':unittest.main()
