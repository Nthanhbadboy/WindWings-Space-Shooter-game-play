"""Own fixed126 source/byte/provenance checks; not runtime acceptance.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
import ast
import copy
import gzip
import json
import struct
import unittest

from tools.verify import l3_geometry_8141386a_review_ef126 as review
from tools.verify import l3_geometry_8141386a_review_ef126_native as native


class Fixed126Sources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.peer = native.read('peer-artifact126.json.gz')
        cls.probe = native.read('peer-probe126.json.gz')
        cls.fresh = native.read('fresh-original.json.gz')
        cls.audit = review.static_audit(cls.peer, cls.probe, cls.fresh)

    def test_fixed_selected_pin_identity(self):
        p = review.validate_pins()
        self.assertEqual(len(p['pins']), 9)
        self.assertEqual(p['scientific_commit'], review.SCI)
        self.assertEqual(p['report_commit'], review.REPORT)
        self.assertEqual(p['claim'], 6426714971)

    def test_gzip_source_wrappers_keep_original_git_blob_ids(self):
        for p in review.validate_pins()['pins']:
            b = (review.ROOT/p['snapshot']).read_bytes()
            original = b if p['encoding']=='gzip-as-source' else gzip.decompress(b)
            self.assertEqual(review.sha(original), p['source_sha256'])
            self.assertEqual(review.blob_id(original), p['git_blob'])

    def test_exact17_fresh_original_spans_and10_fdes(self):
        self.assertEqual(self.audit['fresh_matched_spans'], 17)
        self.assertEqual(self.audit['fresh_matched_fdes'], 10)
        for f in self.fresh['selected_fdes']:
            delta, size = struct.unpack_from('<iI', bytes.fromhex(f['fde_hex']), 8)
            self.assertEqual(f['fde_va']+8+delta, f['start'])
            self.assertEqual(f['start']+size, f['end_exclusive'])

    def test_two_actual_original_bls_and_all_executable_word_coverage(self):
        self.assertEqual([r['pc']for r in self.audit['direct_bls']], [0x6cef84,0x6cefe4])
        self.assertTrue(all(r['link']and r['target']==0x6cf7b4 for r in self.audit['direct_bls']))
        self.assertEqual(self.audit['executable_words_scanned'], 3456888)
        self.assertEqual([r['hex']for r in self.audit['direct_bls']], ['0c020094','f4010094'])

    def test_zero_target_addends_in_all_four_original_rela_types(self):
        self.assertEqual(self.audit['all_rela_total'], 29626)
        self.assertEqual(self.audit['rela_type_counts'], {'257':10,'1025':11,'1026':338,'1027':29267})
        self.assertEqual(self.audit['target_rela_matches_all_types'], 0)
        self.assertEqual(self.audit['selected_relative_relas'], 236)
        self.assertIn('not all indirect users', self.audit['boundary'])

    def test_fde_last_instructions_include_b_and_br_not_just_ret(self):
        f = {r['entry']:r for r in self.audit['executed_body_terminators']}
        self.assertEqual(f[0x6cef64]['kind'], 'B_TO_TAIL')
        self.assertEqual(f[0x6cefdc]['kind'], 'BR_X1_TO_SERVICE')
        self.assertEqual(f[0x6cefdc]['last_instruction_pc'], 0x6ceff8)
        self.assertEqual(f[0x6cefdc]['end_exclusive'], 0x6ceffc)
        self.assertEqual(f[0x5710ec]['last_instruction_pc'], 0x571128)

    def test_original_import_bytes_and_symbols(self):
        rows = self.audit['imports']
        self.assertEqual([r['name']for r in rows], ['__stack_chk_fail','memcpy','memset','sincosf'])
        for r in rows:
            self.assertEqual(bytes.fromhex(r['name_hex']), r['name'].encode()+b'\0')
            self.assertEqual(len(bytes.fromhex(r['symbol_hex'])), 24)

    def test_fresh_source_and_peer_ci_receipts_are_actual_exact_head_success(self):
        c = native.read('source-ci-receipt.json.gz')
        self.assertEqual((c['run']['id'],c['run']['head_sha'],c['run']['status'],c['run']['conclusion']),
            (40399243691,native.SOURCE_HEAD,'completed','success'))
        self.assertEqual(c['peer_verify_run']['head_sha'], review.SCI)
        self.assertEqual(c['peer_verify_run']['conclusion'], 'success')
        self.assertIsNone(c['ci_test_count'])
        self.assertEqual(c['fresh_original_sha256'], review.sha_file(native.RAW/'fresh-original.json.gz'))
        for path,digest in self.fresh['tool_pins'].items():
            self.assertEqual(review.sha_file(review.ROOT/path), digest)

    def test_inherited_n2_source_equality_does_not_promote_unresolved_edges(self):
        n = review.n2_audit(self.peer)
        self.assertEqual(n['upstream_commit'], review.N2_HEAD)
        self.assertEqual(n['owner']['controller']['path_id'], 1856)
        self.assertEqual(n['owner']['animator_component']['component_path_id'], 493584)
        self.assertEqual(n['owner']['hierarchy']['parent_chain_child_to_root'][-1]['gameobject_path_id'], 73241)
        self.assertTrue(n['unresolved_edges'])
        self.assertFalse(any(n['unresolved_edges'].values()))

    def test_malformed_pin_target_or_source_sha_rejected(self):
        m = copy.deepcopy(review.validate_pins());m['scientific_commit']='0'*40
        with self.assertRaisesRegex(ValueError, 'fixed ef126'):review.validate_pins(m)
        m = copy.deepcopy(review.validate_pins());m['pins'][0]['source_sha256']='0'*64
        with self.assertRaisesRegex(ValueError, 'source/Git'):review.validate_pins(m)

    def test_missing_span_or_wrong_fde_extent_rejected(self):
        f = copy.deepcopy(self.fresh);f['peer_selected_spans'].pop()
        with self.assertRaisesRegex(ValueError, 'span'):review.static_audit(self.peer,self.probe,f)
        f = copy.deepcopy(self.fresh);f['selected_fdes'][0]['end_exclusive']+=4
        with self.assertRaisesRegex(ValueError, 'FDE'):review.static_audit(self.peer,self.probe,f)

    def test_false_rela_or_nonlink_direct_reference_rejected(self):
        f = copy.deepcopy(self.fresh);f['target_addend_matches_all_rela_types']=[dict(addend=0x6cf7b4)]
        with self.assertRaisesRegex(ValueError, 'RELA'):review.static_audit(self.peer,self.probe,f)
        f = copy.deepcopy(self.fresh);f['target_direct_branches'][0]['link']=False
        with self.assertRaisesRegex(ValueError, 'BL'):review.static_audit(self.peer,self.probe,f)

    def test_no_producer_executable_module_or_fixture_imports(self):
        for p in ['tools/verify/l3_geometry_8141386a_review_ef126.py','tools/verify/l3_geometry_8141386a_review_ef126_native.py','tools/recovery/geometry_8141386a_review_ef126_bytes.py']:
            tree=ast.parse((review.ROOT/p).read_bytes())
            names=[x.module for x in ast.walk(tree)if isinstance(x,ast.ImportFrom)]
            self.assertFalse(any(n and any(t in n for t in ('bootstrap126','tag23_113_native','caller118_native','nodefactories124','vtable123'))for n in names))


if __name__=='__main__':unittest.main()
