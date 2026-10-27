"""Contracts for report 179: close audit item 32 against 178, without a cycle.

Item 32 — *"a direct static store outside these classes"* — was the last `OPEN` item whose
blocker was a scan. 178 ran the scan and the answer was **none**; this report closes the
item and regenerates the three artifacts in the only order that converges:

    open_items_audit (170)  ->  lane_residue (168)  ->  audit_drift (173)

168 hashes the audit, so it has to be regenerated; the audit reads 168's *content*, not its
hash, so the second pass reproduces the same bytes. These tests pin that fixed point, the
new totals, and the contract losing its only `SCAN` step.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import item32_closure as C  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_item32_closure.json.gz'
PIN_BYTES = 2020
PIN_SHA = '76c486b2e13e03a9e8dcf575ba85df43a5924c18024cd5cef63cc88703f8ec3e'

AUDIT_SHA = 'a7f7b51fddf91e4c6a840cd8e7706a420b6ff022ae3eb992c8b41d77330f0631'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        _, packed = C.build(None)
        self.assertEqual(packed, ARTIFACT.read_bytes())

    def test_every_check_passes(self):
        self.assertEqual([row['name'] for row in payload()['checks']
                          if not row['passed']], [])


class TheClosure(unittest.TestCase):
    def test_the_item_is_32_of_report_132(self):
        item = payload()['item']
        self.assertEqual((item['n'], item['report']), (32, 132))
        self.assertIn('static store outside', item['text'])

    def test_it_is_closed_by_178(self):
        item = payload()['item']
        self.assertEqual((item['verdict'], item['closer']), ('CLOSED', 178))

    def test_the_proof_is_the_store_census(self):
        evidence = payload()['item']['evidence']
        self.assertEqual([one['expected'] for one in evidence], [[0, 16, 6]])
        self.assertTrue(all(one['pass_'] for one in evidence))

    def test_the_order_is_audit_then_residue_then_drift(self):
        order = ' '.join(payload()['order'])
        self.assertLess(order.index('open_items_audit'), order.index('lane_residue'))
        self.assertLess(order.index('lane_residue'), order.index('audit_drift'))


class FixedPoint(unittest.TestCase):
    def test_the_audit_moved_once(self):
        before = payload()['fixed_point']['audit_before']
        after = payload()['fixed_point']['audit_after']
        self.assertEqual((before['closed'], after['closed']), (19, 20))
        self.assertEqual((before['still_open'], after['still_open']), (10, 9))
        self.assertEqual((before['proofs'], after['proofs']), (28, 29))

    def test_the_audit_on_disk_is_the_after(self):
        audit = ROOT / 'datas/l2_535b0541_open_items_audit.json.gz'
        self.assertEqual(hashlib.sha256(audit.read_bytes()).hexdigest(), AUDIT_SHA)

    def test_the_recorded_audit_hash_is_still_current(self):
        self.assertEqual(payload()['provenance']['audit']['sha256'], AUDIT_SHA)

    def test_the_closure_does_not_store_the_drift_hash(self):
        """173 hashes this file; storing its digest here would be the cycle 173 forbids."""
        self.assertNotIn('drift', payload()['provenance'])
        self.assertNotIn('audit_drift', json.dumps(payload()['provenance']))


class Contract(unittest.TestCase):
    def test_no_scan_step_is_left(self):
        self.assertEqual(payload()['contract_after']['scan'], [])

    def test_the_contract_shrank_by_one(self):
        self.assertEqual(payload()['contract_after']['items'], 36)
        self.assertEqual(payload()['fixed_point']['audit_before']['contract'], 37)

    def test_the_remaining_kinds(self):
        kinds = payload()['contract_after']['kinds']
        self.assertEqual(kinds, {'DATA': 6, 'INDEX': 2, 'NOTE': 1, 'PIN-RAW': 3,
                                 'POLICY': 5, 'RUNTIME': 19})

    def test_nine_items_stay_open(self):
        limits = ' '.join(payload()['limits'])
        self.assertIn('nine items still `OPEN`', limits)
        self.assertIn('MODEL_NOT_MEASURED', limits)
        self.assertIn('(18, 19, 34, 44, 48)', limits)

    def test_178_still_answers_the_question(self):
        self.assertEqual(payload()['item']['evidence'][0]['actual'], [0, 16, 6])


if __name__ == '__main__':
    unittest.main()
