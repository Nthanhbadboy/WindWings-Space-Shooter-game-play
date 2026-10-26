"""Own fixed127 source/word/field/correction-context checks, not runtime acceptance.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
import ast
import copy
import gzip
import json
import struct
import unittest
from tools.verify import l3_geometry_8141386a_review_ef127 as review
from tools.verify import l3_geometry_8141386a_review_ef127_native as native
from tools.verify.geometry_8141386a_review_ef127_checks import decode_word,normalize


class Fixed127Sources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.peer=native.read('peer-artifact127.json.gz');cls.probe=native.read('peer-probe127.json.gz');cls.fresh=native.read('fresh-original.json.gz')
        cls.static=review.static_audit(cls.peer,cls.probe,cls.fresh);cls.manifest=review.validate_pins();cls.context=review.context_audit(cls.manifest)

    def test_eight_selected_sources_and_two_context_text_roles(self):
        self.assertEqual(len(self.manifest['pins']),8)
        c=[p for p in self.manifest['pins']if p['role']=='published_text_only_not_native_verification']
        self.assertEqual(len(c),2)
        self.assertEqual({p['commit']for p in c},{review.CONTEXT128,review.CONTEXT129})

    def test_source_wrappers_keep_exact_original_git_blob_ids(self):
        for p in self.manifest['pins']:
            b=(review.ROOT/p['snapshot']).read_bytes();original=b if p['encoding']=='gzip-as-source'else gzip.decompress(b)
            self.assertEqual(review.sha(original),p['source_sha256']);self.assertEqual(review.blob_id(original),p['git_blob'])

    def test_104_spans_37_fdes_and_two_bounded_plt_entries(self):
        self.assertEqual((self.static['fresh_spans'],self.static['fresh_fdes']),(104,37))
        self.assertEqual(self.static['bounded_non_fde_entries'],[0x109acc0,0x109ace0])
        self.assertEqual((self.static['selected_imports'],self.static['selected_relative_relas']),(56,11))

    def test_original_fde_initial_location_and_exclusive_range_arithmetic(self):
        for f in self.fresh['selected_fdes']:
            delta,n=struct.unpack_from('<iI',bytes.fromhex(f['fde_hex']),8)
            self.assertEqual(f['fde_va']+8+delta,f['start']);self.assertEqual(f['start']+n,f['end_exclusive'])

    def test_confirmed_b98c98_ret_metadata_drift_is_not_silently_passed(self):
        ds=self.static['confirmed_return_pc_discrepancies'];self.assertEqual(len(ds),1);d=ds[0]
        self.assertEqual((d['entry'],d['published_ret_pc'],d['actual_ret_pc']),(0xb98c98,0xb98d68,0xb98d64))
        self.assertEqual(d['actual_ret_word_hex'],'c0035fd6');self.assertEqual(d['published_ret_word_hex'],'d6071494')
        self.assertEqual(d['published_ret_actual_decode']['target'],0x109acc0)
        self.assertEqual(d['status'],'CONFIRMED_RETURN_PC_METADATA_DRIFT')
        self.assertEqual(sum(r['status']=='MATCH'for r in self.static['six_callees']),5)

    def test_rewriting_original_ret_metadata_is_rejected_not_rebased(self):
        p=copy.deepcopy(self.peer);p['graph_builder']['callees']['0xb98c98']['ret']=0xb98d64
        with self.assertRaisesRegex(ValueError,'reported-metadata snapshot changed'):
            review.static_audit(p,self.probe,self.fresh)

    def test_graph_ret_is_before_failure_bl_and_not_end_minus_four(self):
        self.assertEqual(self.static['graph_ret_pc'],0x6cff3c)
        self.assertEqual(self.static['graph_failure_bl_pc'],0x6cff40)
        self.assertEqual(self.static['graph_fde_end_exclusive'],0x6cff44)

    def test_all33_machine_words_and_independent_operand_decodes(self):
        self.assertEqual(len(self.static['witnesses']),33)
        for w in self.static['witnesses']:
            self.assertEqual(normalize(w['published_text']),normalize(w['own_decode']['text']))
        decoded={w['pc']:w['own_decode']for w in self.static['witnesses']}
        self.assertEqual(decoded[0x6cf7ec]['target'],0x6cff0c)
        self.assertEqual(decoded[0x6cff18]['target'],0x6cff40)
        self.assertEqual(decoded[0x6cef44]['target'],0x3c9438)

    def test_unknown_instruction_subset_is_not_guessed(self):
        with self.assertRaisesRegex(ValueError,'outside declared33'):decode_word(0,0x1000)
        self.assertEqual(decode_word(0x941407d6,0xb98d68)['kind'],'BL')
        self.assertEqual(decode_word(0xd65f03c0,0xb98d64)['kind'],'RET')

    def test_11_roles_only_six_individual_witnesses_not_all_proven(self):
        self.assertEqual(len(self.static['published_field_roles']),11)
        self.assertEqual(self.static['field_roles_with_individual_witness'],6)
        self.assertEqual(self.static['field_roles_without_individual_witness'],5)

    def test_five_prerequisite_labels_and17_exact_published_citations(self):
        self.assertEqual([r['id']for r in self.context['entries']],['M1','M2','M3','M4','M5'])
        self.assertEqual(self.context['exact_citations'],17)
        self.assertTrue(self.context['classification_is_human_not_machine_truth'])
        self.assertEqual(sum(r['status']=='PUBLISHED_SUPERSESSION'for r in self.context['entries']),2)
        for r in self.context['entries']+self.context['precision_notes']:
            for c in r['citations']:
                self.assertEqual(review.sha(c['quote'].encode()),c['quote_sha256'])
                self.assertEqual(c['evidence_grade'],'PUBLISHED_TEXT_ONLY_NOT_OWN_NATIVE_OR_SERIALIZED_VERIFICATION')

    def test_published_128_129_supersessions_not_native_or_serialized_reverification(self):
        rows={r['id']:r for r in self.context['entries']}
        self.assertIn('M2a serialized content AVAILABLE',rows['M2']['conclusion'])
        self.assertIn('M1b',rows['M1']['conclusion']);self.assertIn('registry',rows['M1']['conclusion'])
        self.assertIn('not proven sufficient',self.context['limit'])

    def test_duplicate_or_absent_published_locator_rejected(self):
        plan=json.loads((native.RAW/'context-review.json').read_bytes());plan['entries'][0]['selectors'][0]['needle']='not a real source quote'
        with self.assertRaisesRegex(ValueError,'not unique'):review.context_audit(self.manifest,plan)
        plan=json.loads((native.RAW/'context-review.json').read_bytes());plan['authority']='NATIVE_VERIFIED'
        with self.assertRaisesRegex(ValueError,'evidence grade'):review.context_audit(self.manifest,plan)

    def test_wrong_pin_sha_or_context_role_rejected(self):
        m=copy.deepcopy(self.manifest);m['pins'][0]['source_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'source/Git'):review.validate_pins(m)
        m=copy.deepcopy(self.manifest);m['pins'][-1]['role']='native_source'
        with self.assertRaisesRegex(ValueError,'promoted'):review.validate_pins(m)

    def test_missing_fresh_span_or_wrong_fde_rejected(self):
        f=copy.deepcopy(self.fresh);f['peer_selected_spans'].pop()
        with self.assertRaisesRegex(ValueError,'coverage'):review.static_audit(self.peer,self.probe,f)
        f=copy.deepcopy(self.fresh);f['selected_fdes'][0]['end_exclusive']+=4
        with self.assertRaisesRegex(ValueError,'FDE'):review.static_audit(self.peer,self.probe,f)

    def test_actual_original_source_and_peer_scientific_ci(self):
        c=native.read('source-ci-receipt.json.gz')
        self.assertEqual((c['run']['id'],c['run']['head_sha'],c['run']['status'],c['run']['conclusion']),(native.SOURCE_RUN,native.SOURCE_HEAD,'completed','success'))
        self.assertEqual(c['peer_verify_run']['head_sha'],review.SCI);self.assertEqual(c['peer_verify_run']['conclusion'],'success');self.assertIsNone(c['ci_test_count'])
        self.assertEqual(c['fresh_original_sha256'],review.sha_file(native.RAW/'fresh-original.json.gz'))
        for p,h in self.fresh['tool_pins'].items():self.assertEqual(review.sha_file(review.ROOT/p),h)

    def test_no_producer_fixture_or_executable_imports_and_single_emulator_start(self):
        for p in ['tools/verify/l3_geometry_8141386a_review_ef127.py','tools/verify/l3_geometry_8141386a_review_ef127_native.py','tools/recovery/geometry_8141386a_review_ef127_bytes.py']:
            t=ast.parse((review.ROOT/p).read_bytes());names=[n.module for n in ast.walk(t)if isinstance(n,ast.ImportFrom)]
            self.assertFalse(any(n and any(v in n for v in ('tag23_113_native','caller118_native','tools.verify.graph127','nodefactories124','vtable123'))for n in names))
            if p.endswith('_native.py'):
                self.assertEqual(sum(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='emu_start'for n in ast.walk(t)),1)


if __name__=='__main__':unittest.main()
