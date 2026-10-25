import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path('tools/verify').resolve()))
from peer_spec_review import build


class PeerReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.raw=build()

    def test_pinned_rebuild(self):
        with gzip.open('reverse-engineering/raw/peer-review/spec-25c367aca.json.gz','rt') as f:
            self.assertEqual(json.load(f),self.raw)
        for s in self.raw['snapshots'].values():
            self.assertEqual(hashlib.sha256(s['text'].encode()).hexdigest(),s['sha256'])

    def test_shadowed_rules_are_real_output_not_guessed_visual_label(self):
        e=self.raw['experiments']
        self.assertEqual(e['Coda_A_no_eye']['category'],'ui')
        self.assertTrue(e['Coda_A_no_eye']['rule'].startswith('R14'))
        self.assertEqual(len(e['Coda_rows_in_output']),4)
        self.assertTrue(all(r['proposed_category']=='ui' and r['rule'].startswith('R14') for r in e['Coda_rows_in_output']))
        self.assertEqual(e['retained_original_count'],643)
        self.assertEqual(e['retained_original_confidences'],['A'])

    def test_native_fallback_is_not_mode0_array(self):
        a=self.raw['native_evidence']['resolved_normal_arrays']
        self.assertAlmostEqual(a['0']['float32'][0],0.2,places=6)
        self.assertAlmostEqual(a['2']['float32'][0],0.5,places=6)
        self.assertNotEqual(a['0']['slot'],a['2']['slot'])

    def test_skip_policy_is_not_a_strict_acceptance_gate(self):
        s=self.raw['snapshots']['tools/verify-claims.py']['text']
        self.assertIn('except Exception as e:',s)
        self.assertIn('c.status, c.why = "SKIP", f"đo lỗi:',s)
        self.assertIn('fails = [c for c in CLAIMS if c.status == "FAIL"]',s)

    def test_default_rebuild_does_not_need_peer_git_history(self):
        with patch('peer_spec_review.subprocess.check_output', side_effect=AssertionError('must not need git history')):
            self.assertEqual(build(),self.raw)
