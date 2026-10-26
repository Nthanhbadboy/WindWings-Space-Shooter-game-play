import copy,gzip,json,math,struct,unittest
import capstone
from tools.verify import packed115 as report
from tools.verify.packed115_native import PackedFixture,frame
from tools.verify.interpolation114_native import bits,floatbits,f32

def patched(raw,address,word):
    r=copy.deepcopy(raw);changed=0
    for span in r['windows']+r['cells']:
        b=bytearray.fromhex(span['hex']);i=address-span['va']
        if 0<=i and i+4<=len(b):b[i:i+4]=struct.pack('<I',word);span['hex']=b.hex();changed+=1
    assert changed
    return r

class NativePacked115(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.raw=report.load_raw();cls.saved=json.load(gzip.open(report.OUT))
    def fixture(self,continuous=1,discrete=0,**kwargs):return PackedFixture(self.raw,report.synthetic_stream(continuous,discrete),continuous,discrete,**kwargs)
    def decode(self,pc):
        return next(capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM).disasm(report.original_bytes(self.raw,pc,4),pc))
    def test_01_input_pins(self):
        for path,h in self.saved['inputs'].items():self.assertEqual(report.digest(report.ROOT/path),h,path)
    def test_02_recovery_tool_pin(self):self.assertEqual(self.raw['tool_sha256'],report.digest(report.ROOT/'tools/recovery/packed115.py'))
    def test_03_deterministic_builder(self):self.assertEqual(report.build(),self.saved)
    def test_04_original_fde_extents(self):
        for r in self.raw['function_extents']:
            delta,size=struct.unpack('<iI',bytes.fromhex(r['fde_hex'])[8:16]);self.assertEqual(r['fde_va']+8+delta,r['start']);self.assertEqual(size,r['end']-r['start'])
    def test_05_actual_native_entries_in_fde(self):
        starts={r['start'] for r in self.raw['function_extents']}
        for a in (0x6df02c,0x6df270,0x6df310,0x6df768):self.assertIn(a,starts)
    def test_06_native_type_record(self):
        t=self.saved['ownership']['native_type'];self.assertEqual((t['name'],t['class_id'],t['native_size']),('AnimationClip',74,592))
    def test_07_compiler_owner_field(self):self.assertEqual((self.decode(0xb6b948).mnemonic,self.decode(0xb6b948).op_str),('str','x0, [x19, #0x1e0]'))
    def test_08_serializer_same_owner_field(self):self.assertEqual(self.decode(0xb6dffc).op_str,'x0, x20, #0x1e0')
    def test_09_api_native_owner_read(self):self.assertEqual(self.decode(0xb6bbd0).op_str,'x8, [x19, #0x1e0]')
    def test_10_real_dispatch_calls_real_sampler(self):self.assertEqual(self.decode(0x6df2ac).op_str,'#0x6df310')
    def test_11_real_sampler_calls_real_selector(self):self.assertEqual(self.decode(0x6df328).op_str,'#0x6df768')
    def test_12_native_initialization_not_prefill(self):
        a=self.fixture(prefill=0);b=self.fixture(prefill=0xa5);self.assertEqual(a.initialized_hex,b.initialized_hex);self.assertEqual(bytes.fromhex(b.initialized_hex),bytes(20));self.assertEqual(b.allocator_calls,[dict(size=20,alignment=4)])
    def test_13_zero_hooks_during_sample(self):
        f=self.fixture();self.assertFalse(f.sinks);r=f.sample(.25);self.assertFalse(r['external_calls']);self.assertIn(0x6df768,r['run']['executed_addresses'])
    def test_14_scalar_cubic(self):self.assertEqual(self.fixture().sample(.25)['continuous_values'],[.15625])
    def test_15_vector_cubic(self):
        r=self.fixture(4).sample(.25);self.assertEqual(r['continuous_values'],[.15625,1.15625,2.15625,3.15625]);self.assertIn(0x6df3f0,r['run']['executed_addresses'])
    def test_16_vector_tail(self):
        r=self.fixture(5).sample(.25);self.assertEqual(r['continuous_values'][-1],4.15625);self.assertIn(0x6df3f0,r['run']['executed_addresses']);self.assertIn(0x6df43c,r['run']['executed_addresses'])
    def test_17_vector_two_groups(self):self.assertEqual(self.fixture(8).sample(.25)['continuous_values'],[i+.15625 for i in range(8)])
    def test_18_discrete_scalar_is_dword_copy(self):self.assertEqual(self.fixture(1,2).sample(.25)['output_bits'][1:],[1001,1002])
    def test_19_discrete_vector_copy(self):
        r=self.fixture(4,4).sample(.25);self.assertEqual(r['output_bits'][4:],[1004,1005,1006,1007]);self.assertIn(0x6df49c,r['run']['executed_addresses'])
    def test_20_discrete_vector_tail(self):self.assertEqual(self.fixture(5,5).sample(.25)['output_bits'][5:],[1005,1006,1007,1008,1009])
    def test_21_exact_boundary_includes_new_frame(self):self.assertEqual(self.fixture(1,1).sample(1)['output_bits'],[bits(1),2001])
    def test_22_negative_time_uses_initial_frame(self):self.assertEqual(self.fixture(1,1).sample(-.5)['output_bits'],[bits(0),101])
    def test_23_forward_cursor_retains_frame(self):
        f=self.fixture();a=f.sample(.25);b=f.sample(.5);self.assertEqual(a['next_frame_byte_offset'],b['next_frame_byte_offset']);self.assertEqual(b['continuous_values'],[.5])
    def test_24_rewind_replays_initial_frames(self):
        f=self.fixture();a=f.sample(.25);f.sample(1);b=f.sample(.25);self.assertEqual(a['output_bits'],b['output_bits']);self.assertEqual(a['next_frame_byte_offset'],b['next_frame_byte_offset'])
    def test_25_same_time_avoids_frame_updates(self):
        f=self.fixture();a=f.sample(.25);b=f.sample(.25);self.assertLess(b['run']['instruction_count'],a['run']['instruction_count']);self.assertEqual(a['cache'],b['cache']);self.assertNotIn(0x6df790,b['run']['executed_addresses'])
    def test_26_key_order_is_not_channel_order(self):self.assertEqual(self.fixture(3,2).sample(.25)['output_bits'],[bits(.15625),bits(1.15625),bits(2.15625),1003,1004])
    def test_27_sparse_frame_updates(self):
        b=frame(-3.4028234663852886e38,[(i,[0,0,0,bits(i)]) for i in range(3)])+frame(0,[(2,[0,0,0,bits(9)])])+frame(math.inf,[])
        self.assertEqual(PackedFixture(self.raw,b,3).sample(.5)['continuous_values'],[0,1,9])
    def test_28_original_words_copied_not_decoded_coefficients(self):
        row,stream,data=report.source_stream();self.assertEqual(hashlib_sha(data),self.saved['source']['packed_data_sha256']);self.assertEqual(len(data),9048);self.assertEqual((stream['curveCount'],stream['discreteCurveCount']),(92,1))
    def test_29_original_source_all_values_match_comparison(self):
        for row in self.saved['source']['runs']:self.assertEqual(row['native']['output_bits'],row['reference']['output_bits']);self.assertEqual(len(row['native']['output_bits']),93)
    def test_30_original_source_rewind(self):
        runs=self.saved['source']['runs'];self.assertEqual(runs[1]['native']['output_bits'],runs[-2]['native']['output_bits']);self.assertEqual(runs[-1]['native']['output_bits'],runs[-2]['native']['output_bits'])
    def test_31_original_source_actual_next_frame_selection(self):self.assertEqual([r['native']['next_frame_byte_offset'] for r in self.saved['source']['runs']],[3656,3656,3656,4272,4564,6040,7700,9040,3656,3656])
    def test_32_original_aggregate_entry_executed(self):
        for r in self.saved['source']['runs']:self.assertIn(0x6df270,r['native']['run']['executed_addresses']);self.assertIn(0x6df310,r['native']['run']['executed_addresses'])
    def test_33_arithmetic_opcode_counterfactual(self):
        op=struct.unpack('<I',report.original_bytes(self.raw,0x6df448,4))[0];raw=patched(self.raw,0x6df448,op^0x2000)
        self.assertNotEqual(PackedFixture(raw,report.synthetic_stream(),1).sample(.25)['continuous_values'],[.15625])
    def test_34_discrete_offset_counterfactual(self):
        op=struct.unpack('<I',report.original_bytes(self.raw,0x6df4ec,4))[0];raw=patched(self.raw,0x6df4ec,op-(4<<10))
        self.assertEqual(PackedFixture(raw,report.synthetic_stream(1,1),1,1).sample(.25)['output_bits'][1],bits(8))
    def test_35_changed_frame_index_changes_native_channel(self):
        b=frame(-3.4028234663852886e38,[(i,[0,0,0,bits(i)]) for i in range(2)])+frame(0,[(1,[0,0,0,bits(9)])])+frame(math.inf,[])
        a=PackedFixture(self.raw,b,2).sample(.5)['continuous_values'];c=bytearray(b);struct.pack_into('<I',c,56,0);d=PackedFixture(self.raw,bytes(c),2).sample(.5)['continuous_values'];self.assertEqual(a,[0,9]);self.assertEqual(d,[9,1])
    def test_36_base_relocation_invariance(self):self.assertEqual(self.fixture(base=0x7000000).sample(.25)['output_bits'],self.fixture().sample(.25)['output_bits'])
    def test_37_nonfinite_times_explicitly_excluded(self):
        f=self.fixture()
        for t in (math.inf,-math.inf,math.nan):
            with self.assertRaises(ValueError):f.sample(t)
    def test_38_nan_payload_discrete_is_preserved(self):
        b=frame(-3.4028234663852886e38,[(0,[0,0,0,0]),(1,[bits(3),bits(4),bits(5),0x7fc12345])])+frame(math.inf,[])
        self.assertEqual(PackedFixture(self.raw,b,1,1).sample(0)['output_bits'][1],0x7fc12345)
    def test_39_no_animationcurve_evaluator_in_sample_trace(self):
        for r in self.saved['source']['runs']:self.assertNotIn(0x952608,r['native']['run']['executed_addresses'])
    def test_40_no_engine_promotion(self):
        self.assertIn('NOT Unity engine',self.saved['scope']);self.assertIn('Dense sampler identified but unexecuted',self.saved['scope']);self.assertIn('NOT executed',self.saved['ownership']['scope'])

def hashlib_sha(b):
    import hashlib
    return hashlib.sha256(b).hexdigest()
if __name__=='__main__':unittest.main()
