import gzip,json,struct,unittest
from tools.verify import caller118 as report,packed115
from tools.verify.caller118_native import CallerFixture,StackCheckFailure
from tools.verify.interpolation114_native import bits

class NativeCaller118(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.raws=report.raws();cls.saved=json.load(gzip.open(report.OUT))
    def fixture(self,**kwargs):return CallerFixture(*self.raws,packed=packed115.synthetic_stream(),continuous=1,**kwargs)
    def test_01_pins(self):
        for p,h in self.saved['inputs'].items():self.assertEqual(report.digest(report.ROOT/p),h,p)
    def test_02_recovery_pin(self):self.assertEqual(self.raws[-1]['tool_sha256'],report.digest(report.ROOT/'tools/recovery/caller118.py'))
    def test_03_deterministic_builder(self):self.assertEqual(report.build(),self.saved)
    def test_04_full_caller_fde(self):
        r=next(x['unwind'] for x in self.raws[-1]['followed'] if x['entry']==0x6d38bc);self.assertEqual(r['end'],0x6d3ebc);delta,n=struct.unpack('<iI',bytes.fromhex(r['fde_hex'])[8:16]);self.assertEqual(r['fde_va']+8+delta,0x6d38bc);self.assertEqual(n,0x600)
    def test_05_entry_first_native_pc(self):
        f=self.fixture();f.run_full();self.assertEqual(f.visits[0],0x6d38bc)
    def test_06_last_native_pc_is_ret(self):self.assertEqual(self.fixture().run_full()['last_native_pc'],0x6d3eb4)
    def test_07_stack_restored(self):
        f=self.fixture();self.assertEqual(f.run_full()['stack_pointer_after'],f.base+0x1f000)
    def test_08_no_manual_stage_field(self):self.assertNotIn('stages',self.fixture().run_full())
    def test_09_tls_canary_native_read(self):
        f=self.fixture();f.run_full();self.assertIn((f.tls+40,8),f.reads)
    def test_10_good_canary_no_failure_call(self):self.assertEqual(self.fixture().run_full()['stack_failure_calls'],[])
    def test_11_fail_import_exact_identity(self):self.assertEqual(self.saved['failure_binding'],dict(plt=0x109acc0,slot=0x10e3d00,symbol='__stack_chk_fail'))
    def test_12_corrupt_canary_never_returns_success(self):
        f=self.fixture()
        with self.assertRaises(StackCheckFailure):f.run_full(corrupt_canary=True)
        self.assertIn(0x109acc0,f.visits);self.assertNotEqual(f.visits[-1],0x6d3eb4)
    def test_13_corrupt_canary_expected_failure_label(self):self.assertEqual(self.saved['corrupt_canary']['outcome'],'EXPECTED_FAILURE_NOT_SUCCESS')
    def test_14_native_duration(self):self.assertIn(0xb6bf94,self.fixture().run_full()['run']['executed_addresses'])
    def test_15_native_context(self):self.assertIn(0x6d3744,self.fixture().run_full()['run']['executed_addresses'])
    def test_16_native_time(self):self.assertIn(0xb93158,self.fixture().run_full()['run']['executed_addresses'])
    def test_17_native_stream(self):self.assertIn(0x6df768,self.fixture().run_full()['run']['executed_addresses'])
    def test_18_scratch_initializer_native(self):self.assertIn(0xb923ac,self.fixture().run_full()['run']['executed_addresses'])
    def test_19_directed_ratio_still_native(self):
        f=self.fixture();f.configure_node(current=.7);self.assertEqual(f.run_full()['context']['current_bits'],bits(.7)+1)
    def test_20_native_phase_store(self):
        f=self.fixture();f.configure_node(current=.7);self.assertEqual(f.run_full()['phase_bits'],bits(.7)+1)
    def test_21_only_modff_success_substitution(self):self.assertEqual([x['symbol'] for x in self.fixture().run_full()['external_calls']],['modff'])
    def test_22_pose_output_not_applied_on_current_only_branch(self):self.assertEqual(self.fixture().run_full()['pose_bytes_hex'],(b'\xa5'*0x150).hex())
    def test_23_skipped_conversion_bodies(self):
        pcs=self.fixture().run_full()['run']['executed_addresses']
        for pc in (0x6dc2e0,0xb94364,0x6d9394,0x6d32d0,0x6d31b0):self.assertNotIn(pc,pcs)
    def test_24_previous_sample_call_skipped(self):self.assertNotIn(0x6d3a1c,self.fixture().run_full()['run']['executed_addresses'])
    def test_25_no_pose_rig_indices_read(self):
        f=self.fixture();f.run_full();self.assertNotIn((f.rig+0x74,4),f.reads)
    def test_26_reject_previous_flag_domain(self):
        f=self.fixture();f.put(f.parameters+0x28,b'\1',False)
        with self.assertRaises(ValueError):f.run_full()
    def test_27_reject_pose_flag_domain(self):
        f=self.fixture();f.put(f.rig+0x80,b'\1',False)
        with self.assertRaises(ValueError):f.run_full()
    def test_28_frame_flag_propagation(self):self.assertEqual(self.fixture().run_full(flag=1)['frame_flag'],1)
    def test_29_frame_flag_or_retains_previous(self):
        f=self.fixture();f.run_full(flag=1);self.assertEqual(f.run_full(flag=0)['frame_flag'],1)
    def test_30_null_blob_skips_context_and_sampler(self):
        r=self.fixture().run_full(missing_blob=True);self.assertIsNone(r['context']);self.assertNotIn(0x6df310,r['run']['executed_addresses'])
    def test_31_null_blob_real_reset_path(self):
        pcs=self.fixture().run_full(missing_blob=True)['run']['executed_addresses']
        for pc in (0x6d3600,0x6dacf0,0xb92414):self.assertIn(pc,pcs)
    def test_32_null_blob_resets_frame_flag(self):self.assertEqual(self.fixture().run_full(missing_blob=True,flag=1)['frame_flag'],0)
    def test_33_null_reset_defined_fields(self):
        f=self.fixture();f.run_full(missing_blob=True);self.assertEqual(f.w(f.pose),0);self.assertEqual(f.w(f.pose+0x30),0);self.assertEqual(bytes(f.u.mem_read(f.pose+0x60,16)),struct.pack('<4f',1,1,1,1))
    def test_34_null_fallback_has_no_external_substitution(self):self.assertEqual(self.fixture().run_full(missing_blob=True)['external_calls'],[])
    def test_35_stack_prefill_invariance(self):
        a=self.fixture(stack_prefill=0).run_full();b=self.fixture(stack_prefill=0xa5).run_full();self.assertEqual((a['context'],a['output_bits']),(b['context'],b['output_bits']))
    def test_36_source_count_and_bit_equality(self):
        self.assertEqual(self.saved['counts']['source_channel_values'],930)
        for r in self.saved['source']['runs']:self.assertEqual(r['native']['output_bits'],r['reference']['output_bits'])
    def test_37_source_rewind_and_repeat(self):
        r=self.saved['source']['runs'];self.assertEqual(r[2]['native']['output_bits'],r[7]['native']['output_bits']);self.assertEqual(r[7]['native']['output_bits'],r[8]['native']['output_bits'])
    def test_38_source_every_call_full_ret(self):
        for r in self.saved['source']['runs']:self.assertEqual(r['native']['last_native_pc'],0x6d3eb4)
    def test_39_relocated_base(self):
        f=self.fixture(base=0x7000000);f.configure_node(current=.7);self.assertEqual(f.run_full()['phase_bits'],bits(.7)+1)
    def test_40_no_full_animator_promotion(self):self.assertIn('NOT full Animator',self.saved['scope']);self.assertIn('Synthetic node/rig flags/TLS',self.saved['source']['runs'][0]['native']['scope'])
if __name__=='__main__':unittest.main()
