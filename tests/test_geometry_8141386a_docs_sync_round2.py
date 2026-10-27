"""H4 text-review bookkeeping regressions; not original-native/semantic proofs.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
import copy
import gzip
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools.verify import l3_geometry_8141386a_docs_sync_round2 as h4


class H4PinnedTextReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = h4.load_sources()
        cls.plan = json.loads((h4.RAW / 'review-map.json').read_bytes())
        cls.value = h4.build()

    def test_deterministic_artifact(self):
        self.assertEqual(h4.OUTPUT.read_bytes(), gzip.compress(h4.canonical(h4.build()) + b'\n', mtime=0))

    def test_human_classification_counts_not_semantic_inference(self):
        c = self.value['counts']
        self.assertEqual((c['archived_full_text_documents'], c['compared_assertions'], c['exact_citations']), (35, 20, 72))
        self.assertEqual(c['classifications'], {'SYNCED': 13, 'DRIFT': 4, 'PARTIALLY_SYNCED': 3})
        self.assertEqual(c['producer_actionable_assertions'], 7)
        self.assertIn('human input', ' '.join(self.value['limits']))

    def test_all_original_document_hashes_and_git_blob_ids(self):
        for source in self.sources.values():
            p = source['pin']
            self.assertEqual(h4.sha(source['data']), p['source_sha256'])
            self.assertEqual(h4.git_blob_id(source['data']), p['git_blob'])
            self.assertEqual(len(source['text'].splitlines()), p['line_count'])

    def test_role_and_fixed_commit_coverage(self):
        self.assertEqual(h4.Counter(s['pin']['role'] for s in self.sources.values()), h4.ROLE_COUNTS)
        for s in self.sources.values():
            self.assertEqual(s['pin']['commit'], h4.ROLE_COMMITS[s['pin']['role']])

    def test_all_72_quotes_reconstruct_at_exact_pinned_lines(self):
        for case in self.value['cases']:
            for c in case['citations']:
                lines = self.sources[c['source']]['text'].splitlines(keepends=True)
                q = ''.join(lines[c['start_line']-1:c['end_line']])
                self.assertEqual(q, c['quote'])
                self.assertEqual(h4.sha(q.encode()), c['quote_sha256'])
                self.assertIn(c['commit'], c['url'])
                self.assertLessEqual(c['start_line'], c['anchor_line'])
                self.assertLessEqual(c['anchor_line'], c['end_line'])

    def test_header87_resolves_by_heading_not_physical_order(self):
        hs = self.value['published_text_checks']['data_sync_headers_in_file_order']
        self.assertEqual(len(hs), 12)
        self.assertEqual(hs[-1]['section'], '24.87')
        self.assertGreater(hs[-1]['line'], next(h['line'] for h in hs if h['section']=='24.96'))

    def test_published_n1_table_counts_only(self):
        c = self.value['published_text_checks']
        self.assertEqual(c['n1_published_rows'], 16)
        self.assertEqual(c['n1_published_classifications'], {'CONFIRMED': 9, 'SUPERSEDED': 6, 'UNVERIFIABLE': 1})
        self.assertIn('No native', c['boundary'])

    def test_published_g6_table_and_145_arithmetic_only(self):
        c = self.value['published_text_checks']
        self.assertEqual(c['g6_published_blob_lengths'], [4, 7, 7, 7, 24])
        self.assertEqual(c['g6_published_int32_sum'], 49)
        a = c['corrected145_published_arithmetic']
        self.assertEqual(a['full_calls']-a['corrected'], a['key_jump']+a['meta_rewards'])
        self.assertEqual(a['gap'], 10)

    def test_snapshot_mutation_rejected(self):
        p = next(iter(self.sources.values()))['pin']
        with self.assertRaisesRegex(ValueError, 'snapshot SHA'):
            h4.validate_snapshot(p, (h4.ROOT/p['snapshot']).read_bytes()+b'x')

    def test_source_sha_mutation_rejected(self):
        p = copy.deepcopy(next(iter(self.sources.values()))['pin']); p['source_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'Markdown size/SHA'):
            h4.validate_snapshot(p, (h4.ROOT/p['snapshot']).read_bytes())

    def test_git_blob_identity_mutation_rejected(self):
        p = copy.deepcopy(next(iter(self.sources.values()))['pin']); p['git_blob'] = '0'*40
        with self.assertRaisesRegex(ValueError, 'Git blob'):
            h4.validate_snapshot(p, (h4.ROOT/p['snapshot']).read_bytes())

    def test_line_count_mutation_rejected(self):
        p = copy.deepcopy(next(iter(self.sources.values()))['pin']); p['line_count'] += 1
        with self.assertRaisesRegex(ValueError, 'line count'):
            h4.validate_snapshot(p, (h4.ROOT/p['snapshot']).read_bytes())

    def test_gzip_read_has_explicit_size_bound(self):
        data = b'x'*(h4.MAX_TEXT+1); packed = gzip.compress(data, mtime=0)
        p = dict(snapshot='oversized.md.gz', snapshot_sha256=h4.sha(packed), size=len(data),
                 source_sha256=h4.sha(data), path='docs/spec/oversized.md')
        with self.assertRaisesRegex(ValueError, 'Markdown size/SHA'):
            h4.validate_snapshot(p, packed)

    def test_missing_anchor_rejected(self):
        c = copy.deepcopy(self.plan['cases'][0]['citations'][0]); c['needle'] = 'NONEXISTENT H4 QUOTE'
        with self.assertRaisesRegex(ValueError, 'exactly once'):
            h4.locate(c, self.sources)

    def test_ambiguous_anchor_rejected(self):
        c = copy.deepcopy(self.plan['cases'][0]['citations'][0]); c['needle'] = '|'
        with self.assertRaisesRegex(ValueError, 'exactly once'):
            h4.locate(c, self.sources)

    def test_unbounded_or_noninteger_quote_context_rejected(self):
        for wrong in (-1, 9, True, '1'):
            c = copy.deepcopy(self.plan['cases'][0]['citations'][0]); c['before'] = wrong
            with self.assertRaisesRegex(ValueError, 'unbounded'):
                h4.locate(c, self.sources)

    def test_wrong_review_provenance_rejected(self):
        p = copy.deepcopy(self.plan); p['provenance'] = 'another-branch'
        with self.assertRaisesRegex(ValueError, 'provenance'):
            h4.review(p, self.sources)

    def test_duplicate_assertion_ids_rejected(self):
        p = copy.deepcopy(self.plan); p['cases'][1]['id'] = 'H4-01'
        with self.assertRaisesRegex(ValueError, 'coverage'):
            h4.review(p, self.sources)

    def test_unknown_classification_rejected(self):
        p = copy.deepcopy(self.plan); p['cases'][0]['verdict'] = 'NATIVE_PROVEN'
        with self.assertRaisesRegex(ValueError, 'classification'):
            h4.review(p, self.sources)

    def test_priority_must_match_declared_status(self):
        p = copy.deepcopy(self.plan); p['cases'][0]['priority'] = 'NONE'
        with self.assertRaisesRegex(ValueError, 'priority inconsistent'):
            h4.review(p, self.sources)

    def test_assertions_need_paired_citations_and_spec_side(self):
        p = copy.deepcopy(self.plan); p['cases'][0]['citations'] = p['cases'][0]['citations'][:1]
        with self.assertRaisesRegex(ValueError, 'paired citations'):
            h4.review(p, self.sources)
        p = copy.deepcopy(self.plan)
        p['cases'][0]['citations'] = [p['cases'][0]['citations'][3]]*2
        with self.assertRaisesRegex(ValueError, 'producer-spec'):
            h4.review(p, self.sources)

    def test_git_byte_comparison_unit_stub_detects_mismatch(self):
        # Stub tests comparison behavior only; CLI --git is the real Git-byte gate.
        with patch.object(h4.subprocess, 'run', return_value=SimpleNamespace(returncode=0)), \
             patch.object(h4.subprocess, 'check_output', return_value=b'changed document'):
            with self.assertRaisesRegex(ValueError, 'actual pinned Git bytes'):
                h4.verify_git(self.sources)

    def test_missing_git_commit_never_silently_network_fetches(self):
        with patch.object(h4.subprocess, 'run', return_value=SimpleNamespace(returncode=1)) as run:
            with self.assertRaisesRegex(ValueError, 'fetch explicitly'):
                h4.verify_git(self.sources)
            self.assertEqual(run.call_count, 1)

    def test_scope_and_archive_coverage_do_not_claim_native_acceptance(self):
        c = self.value['counts']
        self.assertEqual([c[k] for k in ('native_executions','raw_artifacts_inspected','runtime_or_readback_measurements')], [0,0,0])
        self.assertTrue(self.value['archived_not_cited_claim_by_claim'])
        self.assertIn('PARTIALLY_SYNCED', self.value['verdict'])
        self.assertIn('ef126', ' '.join(self.value['out_of_scope']))
        self.assertIn('No producer correction is claimed applied', ' '.join(self.value['limits']))
        for k in ('H4-01','H4-07','H4-08','H4-19'):
            self.assertEqual(next(r for r in self.value['cases'] if r['id']==k)['verdict'], 'DRIFT')


if __name__ == '__main__':
    unittest.main()
