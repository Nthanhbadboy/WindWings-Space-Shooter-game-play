"""Gate1 source/catalogue/acceptance-boundary tests, not user acceptance.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
import ast
from collections import Counter
import copy
import gzip
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from tools.verify import l3_geometry_8141386a_gate1_phase_a as review


class Gate1PackageReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest,cls.src=review.sources();cls.pubs=review.comments()
        cls.text=cls.src['spec-tools__verify-claims.py.gz']['data'].decode()
        cls.rows=review.declarations(cls.text)
        cls.joined,cls.counts=review.join_report(cls.rows,cls.pubs['producer-numeric-table']['body'])
        cls.plan=json.loads((review.RAW/'review-map.json').read_bytes())
        cls.curation=review.review_plan(cls.src,cls.pubs)
        cls.value=review.build()

    def test_deterministic_complete_artifact(self):
        self.assertEqual(review.OUTPUT.read_bytes(),gzip.compress(review.canonical(review.build())+b'\n',mtime=0))

    def test_not_ready_is_review_recommendation_not_gate_self_ack(self):
        self.assertEqual(self.value['verdict'],'NOT_READY')
        self.assertFalse(self.curation['user_gate_approval'])
        self.assertFalse(self.curation['machine_semantic_acceptance_proof'])
        self.assertIn('user decision',self.curation['review_limits'][-1])

    def test_whole211_registration_rows_209_unique_ids(self):
        self.assertEqual(len(self.rows),211)
        self.assertEqual(len({r['id']for r in self.rows}),209)
        self.assertEqual(len({r['row_key']for r in self.rows}),211)
        self.assertTrue(all(not r['independent_raw_remeasurement']for r in self.rows))

    def test_all36_complete_claim_target_files_are_archived(self):
        targets={r['doc']for r in self.rows};available={p['path']for p in self.manifest['pins']if p['commit']==review.SPEC}
        self.assertEqual(len(targets),36);self.assertTrue(targets<=available)

    def test_published209pass2skip_is_not_211pass_or_209_distinct_passes(self):
        self.assertEqual(self.counts['reported_status_counts'],{'PASS':209,'SKIP':2})
        self.assertEqual(self.counts['distinct_id_status_counts'],{'PASS':207,'SKIP':2})
        self.assertEqual(self.counts['skipped_ids'],['B9','F4'])

    def test_duplicate_ge1_ge2_occurrences_preserved_not_dict_dropped(self):
        self.assertEqual(Counter(r['id']for r in self.rows)['GE1'],2)
        self.assertEqual(self.counts['duplicate_ids'],{'GE1':2,'GE2':2})
        self.assertEqual([r['row_key']for r in self.rows if r['id']=='GE1'],['GE1#1','GE1#2'])

    def test_direct_function_redefinitions_are_bound_at_registration(self):
        r=[r for r in self.rows if r['id']=='GE1']
        self.assertNotEqual(r[0]['direct_function_binding']['start_line'],r[1]['direct_function_binding']['start_line'])
        self.assertTrue(all(x['direct_function_binding']['semantics']=='FUNCTION_OBJECT_BOUND_AT_REGISTRATION_NOT_EXECUTED'for x in r))

    def test_archived_code_is_ast_only_not_executed(self):
        dangerous='raise RuntimeError("archived verifier must stay inert")\n'+self.text
        self.assertEqual(len(review.declarations(dangerous)),211)

    def test_nested_or_conditional_claims_are_not_guessed_as_registrations(self):
        text=self.text+'\nif False:\n    claim("UNREACHED", "x", "y", 1, lambda: 1)\n'
        with self.assertRaisesRegex(ValueError,'nested/conditional'):review.declarations(text)

    def test_dropping_one_registration_is_detected(self):
        text=self.text.replace(self.rows[-1]['source_quote'],'',1)
        with self.assertRaisesRegex(ValueError,'211-row'):review.declarations(text)

    def test_reported_order_or_claim_identity_drift_is_detected(self):
        rows=copy.deepcopy(self.rows);rows[0]['id']='OTHER'
        with self.assertRaisesRegex(ValueError,'ordinal/CID'):review.join_report(rows,self.pubs['producer-numeric-table']['body'])

    def test_reporting_intentional_skip_as_pass_is_detected(self):
        body=self.pubs['producer-numeric-table']['body'];line=next(r['reported_result']['quote']for r in self.joined if r['id']=='B9')
        body=body.replace(line,line.replace('SKIP','PASS'),1)
        with self.assertRaisesRegex(ValueError,'209/0/2'):review.join_report(self.rows,body)

    def test_dropping_duplicate_result_row_is_detected(self):
        body=self.pubs['producer-numeric-table']['body'];line=next(r['reported_result']['quote']for r in self.joined if r['row_key']=='GE1#1')
        with self.assertRaisesRegex(ValueError,'every declared row'):review.join_report(self.rows,body.replace(line+'\n','',1))

    def test_every_declaration_has_exact_original_source_line_hash(self):
        lines=self.text.splitlines(keepends=True)
        for r in self.rows:
            body=''.join(lines[r['source_start_line']-1:r['source_end_line']])
            self.assertEqual(body,r['source_quote']);self.assertEqual(review.sha(body.encode()),r['source_quote_sha256'])

    def test_16_domain_rows_have_explicit_evidence_and_scope(self):
        self.assertEqual(len(self.curation['domain_matrix']),16)
        self.assertEqual({r['evidence_label']for r in self.curation['domain_matrix']},review.LABELS)
        self.assertFalse(any(r['independent_remeasurement']for r in self.curation['domain_matrix']))

    def test_each_of_five_blocking_findings_has_owner_and_exit_condition(self):
        blockers=[f for f in self.curation['findings']if f['blocking']]
        self.assertEqual(len(blockers),5)
        self.assertEqual({f['condition']for f in blockers},{r['id']for r in self.curation['blocking_conditions']})
        self.assertTrue(all(r['owner']and r['required']for r in self.curation['blocking_conditions']))

    def test_accepted27_and_cross_build_limits_are_preserved_not_reopened(self):
        holds={r['id']:r for r in self.curation['preserved_boundaries']}
        self.assertIn('does not reopen',holds['HOLD-01']['summary'])
        self.assertIn('runtime1.0.69 vs static1.3.118',holds['HOLD-02']['summary'])
        self.assertIn('not same-build parity',holds['HOLD-02']['summary'])
        self.assertEqual(self.value['counts']['new_runtime_measurements'],0)

    def test_historical_runtime_is_not_promoted_to_target_same_build(self):
        p=copy.deepcopy(self.plan);next(r for r in p['domain_matrix']if r['id']=='D13')['applicability']='SAME_BUILD_PARITY'
        with self.assertRaisesRegex(ValueError,'same-build'):review.review_plan(self.src,self.pubs,p)

    def test_missing_citation_cannot_support_a_domain_acceptance_claim(self):
        p=copy.deepcopy(self.plan);p['domain_matrix'][0]['selectors']=[]
        with self.assertRaisesRegex(ValueError,'uncited'):review.review_plan(self.src,self.pubs,p)

    def test_publication_review_cannot_be_relabelled_fresh_measurement(self):
        p=copy.deepcopy(self.plan);p['domain_matrix'][0]['independent_remeasurement']=True
        with self.assertRaisesRegex(ValueError,'fresh measurement'):review.review_plan(self.src,self.pubs,p)

    def test_ready_verdict_with_unresolved_blocking_list_is_rejected(self):
        p=copy.deepcopy(self.plan);p['verdict']='READY_FOR_GATE1'
        with self.assertRaisesRegex(ValueError,'verdict/blocking'):review.review_plan(self.src,self.pubs,p)

    def test_wrong_source_commit_identity_is_rejected(self):
        m=copy.deepcopy(self.manifest);m['spec_commit']='0'*40
        with self.assertRaisesRegex(ValueError,'source identity'):review.sources(m)

    def test_wrong_snapshot_sha_is_rejected(self):
        m=copy.deepcopy(self.manifest);m['pins'][0]['snapshot_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'compressed identity'):review.sources(m)

    def test_all61_original_git_blob_hashes_match_retained_sources(self):
        self.assertEqual(len(self.manifest['pins']),61)
        for p in self.manifest['pins']:
            packed=(review.ROOT/p['snapshot']).read_bytes();data=packed if p['encoding']=='gzip-as-source'else review.unpack(review.ROOT/p['snapshot'])
            self.assertEqual(review.blob_id(data),p['git_blob']);self.assertEqual(review.sha(data),p['source_sha256'])

    def test_decoded_source_budget_is_bounded_before_full_decompression(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'oversize.gz';p.write_bytes(gzip.compress(b'x'*2_000_001,mtime=0))
            with self.assertRaisesRegex(ValueError,'decoded source budget'):review.unpack(p)

    def test_publication_array_conflict_matches_same_fields_and_declared_input_digests(self):
        c=self.value['published_reward_conflict'];self.assertEqual([r['offset']for r in c['fields']],[416,424])
        self.assertEqual(c['fields'][0]['artifact149_values'],[100,10000,10,100,10,10])
        self.assertEqual(c['artifact169_float_candidates'],4)
        self.assertEqual(c['shared_declared_input_sha256']['reverse-engineering/il2cpp/field-defaults.json'],'05a51c9bc32bd5f0c42ef4822e36f838dab931ec2213298a56d3aaf6e7be4d27')

    def test_published_conflict_does_not_choose_a_raw_derivation_winner(self):
        c=self.value['published_reward_conflict'];self.assertIn('NO_WINNER_SELECTED',c['status'])
        self.assertIn('NOT rehashing raw inputs',c['boundary'])
        self.assertEqual(self.value['counts']['independently_rerun_producer_claims'],0)

    def test_registry_totals_are_pinned_snapshot_not_latest_semantic_closure(self):
        r=self.value['registry_publication'];self.assertEqual(r['summary']['items'],56)
        self.assertEqual(r['summary']['closed'],19);self.assertEqual(r['summary']['still_open'],10)
        self.assertIn('not a latest-all-work',r['scope'])

    def test_actual_spec_ci_and_pr16_vehicle_are_not_gate_or_runtime_acceptance(self):
        c=self.value['actual_ci_metadata'];self.assertEqual(c['head'],review.SPEC);self.assertEqual(c['status'],'success');self.assertIsNone(c['ci_test_count'])
        p=self.value['pr16_metadata'];self.assertTrue(p['is_draft']);self.assertFalse(p['merge_or_acceptance_inferred'])
        self.assertIn('NOT an immutable',c['source_binding'])

    def test_59_quote_receipts_have_correct_hashes_and_source_only_grade(self):
        all_quotes=[c for g in ('findings','preserved_boundaries','domain_matrix')for r in self.curation[g]for c in r['citations']]
        self.assertEqual(len(all_quotes),59)
        for q in all_quotes:
            self.assertEqual(review.sha(q['quote'].encode()),q['quote_sha256'])
            self.assertIn('NOT_FRESH_RAW_NATIVE_RUNTIME',q['evidence_grade'])

    def test_absent_or_ambiguous_source_locator_is_rejected(self):
        p=copy.deepcopy(self.plan);p['findings'][0]['selectors'][0]['needle']='not an actual published quote'
        with self.assertRaisesRegex(ValueError,'not unique'):review.review_plan(self.src,self.pubs,p)

    def test_no_peer_code_execution_or_native_emulator_in_review_tool(self):
        text=(review.ROOT/'tools/verify/l3_geometry_8141386a_gate1_phase_a.py').read_text();tree=ast.parse(text)
        self.assertFalse(any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id in ('exec','eval','compile','__import__')for n in ast.walk(tree)))
        self.assertFalse(any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='emu_start'for n in ast.walk(tree)))
        self.assertEqual(self.value['counts']['new_native_cases'],0)

    def test_fetch_requires_explicit_git_flag(self):
        p=subprocess.run([sys.executable,'-m','tools.verify.l3_geometry_8141386a_gate1_phase_a','--fetch'],cwd=review.ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        self.assertEqual(p.returncode,2);self.assertIn(b'--fetch requires --git',p.stderr)


if __name__=='__main__':unittest.main()
