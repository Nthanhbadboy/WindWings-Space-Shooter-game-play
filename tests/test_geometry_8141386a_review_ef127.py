"""Own original null-domain path and strict sink/coverage/prefill boundaries.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
import gzip
import unittest
from tools.verify import l3_geometry_8141386a_review_ef127 as review
from tools.verify import l3_geometry_8141386a_review_ef127_native as native


class Guarded127Review(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.peer=native.read('peer-artifact127.json.gz');cls.rows=review.replay_audit(cls.peer)

    def test_deterministic_separate_artifact_and_documented_drift(self):
        v=review.build();self.assertEqual(review.OUTPUT.read_bytes(),gzip.compress(review.canonical(v)+b'\n',mtime=0))
        self.assertEqual(v['counts']['confirmed_published_return_pc_discrepancies'],1)
        self.assertEqual(v['counts']['new_canonical_numeric_contradictions'],0)

    def test_three_exact51_counts_and_original_pc_sets(self):
        self.assertEqual([r['native_instruction_count']for r in self.rows],[51,51,51])
        for r,p in zip(self.rows,self.peer['cases']):self.assertEqual(r['executed_addresses'],p['run']['executed_addresses'])
        self.assertTrue(all(r['pc_counts']==self.rows[0]['pc_counts']for r in self.rows))

    def test_native_selected_branches_not_staged_intervals(self):
        expected=[(0x6cf7e4,0x6ceeb0),(0x6ceec8,0x6ceee8),(0x6ceef0,0x6cef30),(0x6cef60,0x6cf7e8),(0x6cf7ec,0x6cff0c)]
        for r in self.rows:
            self.assertEqual([(e['from_pc'],e['to_pc'])for e in r['original_nonsequential_edges']],expected)
            self.assertEqual((r['entry_count'],r['emu_start_calls']),(1,1))
            self.assertEqual(r['chronological_native_pcs'][0],native.GB)

    def test_whole_fde_path_does_not_mean_all484_words_executed(self):
        for r in self.rows:
            self.assertEqual((r['body_coverage'][hex(native.GB)]['executed_unique'],r['body_coverage'][hex(native.GB)]['fde_instruction_words']),(28,484))
            self.assertEqual((r['body_coverage'][hex(native.CLEANUP)]['executed_unique'],r['body_coverage'][hex(native.CLEANUP)]['fde_instruction_words']),(23,45))

    def test_only_two_native_node_zero_stores(self):
        for r in self.rows:
            node=r['addresses']['node'];ws=[(w['pc'],w['address']-node,w['size'],w['value'])for w in r['native_memory_writes']if w['tier']=='PREPARED_NODE']
            self.assertEqual(ws,[(0x6cef48,0x1c0,8,0),(0x6cef4c,0x1c8,4,0)])
            self.assertEqual(r['node_after']['slot118'],0);self.assertEqual(r['node_after']['slot1a0'],0)

    def test_unbuilt_outputs_keep_a5_or_prepared_zero_not_native_clear(self):
        for r in self.rows:
            expected=int.from_bytes(bytes([r['prefill']])*8,'little')
            for key in ('slot128','slot130','slot138','slot140','slot180'):
                self.assertEqual(r['node_after'][key],expected);self.assertEqual(r['node_before'][key],expected)

    def test_null_free_is_one_explicit_sink_with_original_callsite_arguments(self):
        for r in self.rows:
            self.assertEqual(len(r['service_calls']),1);s=r['service_calls'][0]
            self.assertEqual((s['call_pc'],s['object'],s['label_va'],s['line']),(0x6cef44,0,0x12da21,0x24))
            self.assertEqual(s['category'],int.from_bytes(bytes([r['prefill']])*4,'little'))
            self.assertNotIn(native.FREE,r['executed_addresses'])
            self.assertEqual(r['host_pc_writes'],[dict(origin='SYNTHETIC_FREE_RETURN_TO_ORIGINAL_LR',from_pc=native.FREE,to_pc=0x6cef48)])

    def test_canary_actual_load_compare_path_and_nonzero_saved_registers(self):
        for r in self.rows:
            self.assertEqual(len(r['canary_checks']),1);c=r['canary_checks'][0]
            self.assertEqual((c['tls_value'],c['saved_value']),(native.CANARY,native.CANARY))
            self.assertEqual(c['compare_pc'],0x6cff14)
            self.assertEqual(r['callee_saved_before'],r['callee_saved_after'])
            self.assertTrue(all(r['callee_saved_before'].values()))

    def test_stack_restoration_and_original_ret_before_fixture_stop(self):
        for r in self.rows:
            self.assertEqual(r['last_native_pc'],0x6cff3c)
            self.assertEqual(r['stack_pointer_after'],r['base']+0x1f000)
            self.assertEqual(r['stop_pc'],r['addresses']['stop']);self.assertEqual(r['return_value'],0)
            self.assertNotIn(r['stop_pc'],r['executed_addresses'])

    def test_non_null_build_five_other_callees_and_failure_plt_do_not_execute(self):
        for r in self.rows:
            self.assertFalse([pc for pc in r['executed_addresses']if 0x6cf7f0<=pc<native.EPILOGUE])
            for a in review.CALLEES:
                if a!=native.CLEANUP:self.assertNotIn(a,r['executed_addresses'])
            self.assertNotIn(0x6cff40,r['executed_addresses']);self.assertNotIn(0x109acc0,r['executed_addresses'])

    def test_tampered_tls_takes_original_canary_failure_branch_and_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'original canary-failure branch reached'):native.replay(fault_canary=True)

    def test_missing_original_instruction_rejected_despite_mapped_zero_page(self):
        with self.assertRaisesRegex(ValueError,'uncaptured original127 instruction'):native.replay(drop_instruction=native.GB)

    def test_unprepared_tls_read_rejected_despite_mapped_zero_page(self):
        with self.assertRaisesRegex(ValueError,'uncaptured/unprepared original127 native data'):native.replay(fault_unprepared_tls=True)

    def test_disabling_free_sink_does_not_execute_captured_original_heap(self):
        with self.assertRaisesRegex(ValueError,'original heap prohibited'):native.replay(free_sink=False)

    def test_undeclared_variant_rejected_without_inventing_non_null_object(self):
        with self.assertRaisesRegex(ValueError,'outside three declared'):native.replay(prefill=1)
        with self.assertRaisesRegex(ValueError,'outside three declared'):native.replay(base=0x5000000)


if __name__=='__main__':unittest.main()
