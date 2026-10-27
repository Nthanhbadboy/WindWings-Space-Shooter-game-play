"""Additive producer-erratum verification; original123 must stay immutable.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
import ast
import copy
import gzip
import json
import subprocess
import sys
import unittest
from unittest.mock import patch
from tools.verify import l3_geometry_8141386a_review_ef127_erratum as review
from tools.verify.geometry_8141386a_review_ef127_checks import decode_word


class Published127Erratum(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value=review.build();cls.old,cls.fresh=review.frozen_evidence();cls.words=cls.value['word_verification']
        cls.comments=review.validate_comments();cls.manifest=review.validate_publication()

    def test_deterministic_additive_artifact(self):
        self.assertEqual(review.OUTPUT.read_bytes(),gzip.compress(review.canonical(review.build())+b'\n',mtime=0))

    def test_bounded_upgrade_covers_one_label_not_runtime_or_new_cases(self):
        self.assertEqual(self.value['verdict'],'APPROVE_BOUNDED_EF127_NULL_ENTRY_RET_AFTER_VERIFIED_PRODUCER_ERRATUM_NOT_27_FULL')
        self.assertEqual(self.value['counts']['covered_label_errata_verified'],1)
        self.assertEqual(self.value['counts']['covered_label_blockers_remaining'],0)
        self.assertEqual((self.value['counts']['new_native_cases'],self.value['counts']['new_original_source_capture']),(0,0))

    def test_two_actual_comment_identities_and_producer_correction_scope(self):
        self.assertEqual(self.comments['producer']['id'],6436088881)
        self.assertEqual(self.comments['spec_ack']['id'],6436273516)
        self.assertEqual(self.value['producer_erratum']['correction_kind'],'ADDITIVE_RETURN_LABEL_SUPERSESSION_ONLY')
        self.assertIn('không regenerate artifact 127',self.comments['producer']['body'].replace('**',''))

    def test_tampered_comment_body_is_rejected(self):
        p=copy.deepcopy(self.comments['producer']);p['body']=p['body'].replace('b98d64','b98d68')
        with self.assertRaisesRegex(ValueError,'comment identity/body'):review.validate_comments(p,self.comments['spec_ack'])

    def test_wrong_comment_id_or_url_is_rejected(self):
        for field,val in [('id',6436088882),('html_url','https://example.invalid/not-publication')]:
            p=copy.deepcopy(self.comments['producer']);p[field]=val
            with self.assertRaisesRegex(ValueError,'comment identity/body'):review.validate_comments(p,self.comments['spec_ack'])

    def test_five_exact_publication_tip_git_identities(self):
        self.assertEqual(len(self.manifest['pins']),5)
        self.assertTrue(all(p['commit']=='5246e293c6375a3329244f1555e2d6d06d3c0303'for p in self.manifest['pins']))
        for p in self.manifest['pins']:
            data=(review.ROOT/p['snapshot']).read_bytes();source=data if p['encoding']=='gzip-as-source'else gzip.decompress(data)
            self.assertEqual(review.sha(source),p['source_sha256']);self.assertEqual(review.blob_id(source),p['git_blob'])

    def test_wrong_publication_tip_or_snapshot_is_rejected(self):
        m=copy.deepcopy(self.manifest);m['producer_publication_commit']='0'*40
        with self.assertRaisesRegex(ValueError,'pin coverage'):review.validate_publication(m)
        m=copy.deepcopy(self.manifest);m['pins'][0]['snapshot_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'snapshot'):review.validate_publication(m)

    def test_original212_byte_window_offset_and_exclusive_end(self):
        w=self.words['window']
        self.assertEqual((w['va'],w['file_offset'],w['size'],w['fde_end_exclusive']),(0xb98c98,12143768,212,0xb98d6c))
        self.assertTrue(self.words['own_original_matches_producer_window'])

    def test_ret_is_d64_and_old_d68_is_bl_to_stack_check_stub(self):
        self.assertEqual(self.words['corrected_return_pc'],0xb98d64)
        self.assertEqual(self.words['old_label_pc'],0xb98d68)
        self.assertEqual(self.words['old_label_actual_decode'],{'kind':'BL','target':0x109acc0,'text':'bl 0x109acc0'})
        rows={r['pc']:r['word_hex']for r in self.words['checked_words']}
        self.assertEqual(rows[0xb98d64],'c0035fd6');self.assertEqual(rows[0xb98d68],'d6071494')

    def test_canary_conditional_branch_naturally_targets_d68(self):
        b=self.words['canary_failure_branch']
        self.assertEqual((b['kind'],b['condition'],b['target']),('B_COND','ne',0xb98d68))

    def test_original_epilogue_load_and_add_sp_are_byte_checked(self):
        rows={r['pc']:r['word_hex']for r in self.words['checked_words']}
        self.assertEqual(rows[0xb98d5c],'fe1340f9');self.assertEqual(rows[0xb98d60],'ff430191')
        d=decode_word(int.from_bytes(bytes.fromhex(rows[0xb98d5c]),'little'),0xb98d5c)
        self.assertEqual((d['base_register'],d['register'],d['offset']),(31,30,0x20))

    def test_other_return_count_is_five_callees_plus_graph_not_six_callees(self):
        self.assertEqual(self.words['other_listed_callee_returns_verified'],5)
        self.assertEqual(self.words['graph_builder_return_verified'],1)
        self.assertEqual(len(self.words['checked_words']),11)

    def test_bounded53_word_scan_finds_one_ret_not_a_general_heuristic_fix(self):
        self.assertEqual(self.words['bounded_instruction_words_scanned'],53)
        self.assertEqual(self.words['return_instructions'],[0xb98d64])
        self.assertIn('not a general',self.words['boundary'])

    def test_changed_original_window_bytes_are_rejected(self):
        f=copy.deepcopy(self.fresh);w=next(r for r in f['peer_selected_spans']if r['va']==0xb98c98);w['hex']='00'+w['hex'][2:]
        with self.assertRaisesRegex(ValueError,'span equality'):review.word_audit(f)

    def test_wrong_fde_end_is_rejected(self):
        f=copy.deepcopy(self.fresh);next(r for r in f['selected_fdes']if r['start']==0xb98c98)['end_exclusive']+=4
        with self.assertRaisesRegex(ValueError,'exclusive-end'):review.word_audit(f)

    def test_original123_stays_conditional_with_the_historical_drift(self):
        self.assertIn('CORRECTION_PENDING',self.old['verdict'])
        self.assertEqual(self.old['counts']['confirmed_published_return_pc_discrepancies'],1)
        self.assertEqual(self.old['counts']['native_instructions'],[51,51,51])
        self.assertEqual(self.value['original_review']['historical_confirmed_return_metadata_drift'],1)

    def test_original_producer_artifact_and_generator_are_not_regenerated(self):
        p=review.read(review.RAW/'peer-artifact127.json.gz')
        self.assertEqual(p['graph_builder']['callees']['0xb98c98']['ret'],0xb98d68)
        self.assertEqual(review.sha_file(review.RAW/'peer-artifact127.json.gz'),review.PEER_ARTIFACT)
        self.assertIn('dict(ret=v-4,fde_end=v)',gzip.decompress((review.RAW/'peer-generator127.py.gz').read_bytes()).decode())

    def test_original_scientific_receipt_and_actual_ci_remain_original(self):
        r=review.read(review.BASE/'verification-123.json.gz');c=review.read(review.BASE/'scientific-ci-123.json.gz')
        self.assertEqual((r['full_tests']['count'],r['focused_tests']['count']),(1655,284))
        self.assertEqual(c['scientific_commit'],review.OWN_SCIENCE);self.assertIsNone(c['ci_test_count'])
        self.assertEqual(self.value['original_review']['scientific_commit'],review.OWN_SCIENCE)

    def test_comment_post_403_is_not_claimed_as_success(self):
        c=self.value['coordination'];self.assertIsNone(c['claim_comment_id'])
        self.assertEqual(c['status'],'POST_FAILED_HTTP_403_RESOURCE_NOT_ACCESSIBLE_BY_INTEGRATION')
        self.assertEqual(self.value['existing_claim'],6427652461)

    def test_new_addendum_has_no_native_or_producer_executable_imports(self):
        tree=ast.parse((review.ROOT/'tools/verify/l3_geometry_8141386a_review_ef127_erratum.py').read_bytes())
        names=[n.module for n in ast.walk(tree)if isinstance(n,ast.ImportFrom)]
        self.assertFalse(any(n and ('unicorn'in n or'tools.verify.graph127'in n or'Fixture'in n)for n in names))
        self.assertFalse(any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='emu_start'for n in ast.walk(tree)))

    def test_optional_live_api_check_is_read_only_and_rejects_changed_body(self):
        good=[json.dumps(self.comments['producer']).encode(),json.dumps(self.comments['spec_ack']).encode()]
        with patch.object(review.subprocess,'check_output',side_effect=good)as get:
            self.assertEqual(review.verify_api(),[6436088881,6436273516])
            self.assertEqual(get.call_count,2)
            self.assertTrue(all('--method'not in args.args[0]for args in get.call_args_list))
        bad=copy.deepcopy(self.comments['producer']);bad['body']+=' altered'
        with patch.object(review.subprocess,'check_output',return_value=json.dumps(bad).encode()):
            with self.assertRaisesRegex(ValueError,'publication body differs'):review.verify_api()

    def test_fetch_requires_explicit_git_flag_without_build_or_api(self):
        p=subprocess.run([sys.executable,'-m','tools.verify.l3_geometry_8141386a_review_ef127_erratum','--fetch'],cwd=review.ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        self.assertEqual(p.returncode,2);self.assertIn(b'--fetch requires --git',p.stderr)


if __name__=='__main__':unittest.main()
