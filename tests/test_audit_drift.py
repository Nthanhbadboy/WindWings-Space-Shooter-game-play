"""Contracts for report 173: the drift gate over the lane artifacts.

170 taught `open_items_audit` to read 168/169 by hand, which fixes one snapshot and
guarantees the next drift. This gate reads *every* `datas/l2_535b0541_*.json.gz`,
takes the statements that name an audit item, and checks them against the audit rows.
The tests below pin the artifact bytes, then drive each rule with synthetic rows so
the rule, not the snapshot, is what is being tested.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import audit_drift as AD  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_audit_drift.json.gz'
PIN_BYTES = 7733
PIN_SHA = '86e4888a80a85efd9183c11a7924e62650c9a148dd44de3a7402b9cd923bafa8'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


def synthetic_row(n, verdict='OPEN', closer=None, reason=''):
    return dict(n=n, verdict=verdict, closer=closer, reason=reason, item='x', report=1,
                blocking=None)


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        _, packed = AD.build(None)
        self.assertEqual(packed, ARTIFACT.read_bytes())

    def test_static_only(self):
        self.assertEqual(payload()['evidence'], 'STATIC_ONLY_ORIGINAL_APK')

    def test_schema(self):
        self.assertEqual(payload()['schema'], 'l2/535b0541/audit-drift/1')


class PayloadShape(unittest.TestCase):
    def test_every_check_passes(self):
        body = payload()
        self.assertEqual(body['totals']['checks_passed'], body['totals']['checks_total'])
        self.assertEqual([row['name'] for row in body['checks'] if not row['passed']], [])

    def test_check_names_are_the_nineteen(self):
        self.assertEqual(len(payload()['checks']), 19)
        names = [row['name'] for row in payload()['checks']]
        self.assertIn('the-gate-reads-every-lane-artifact', names)
        self.assertIn('the-audit-table-still-covers-127-to-146-whole', names)
        self.assertIn('the-audit-names-every-report-that-produced-an-artifact', names)
        self.assertIn('no-report-level-correction-points-at-an-unknown-report', names)

    def test_totals_are_the_artifact(self):
        totals = payload()['totals']
        self.assertEqual(totals['artifacts'], 49)
        self.assertEqual(totals['claims'], 9)
        self.assertEqual(totals['targets'], 2)
        self.assertEqual(totals['contract'], 33)
        self.assertEqual(totals['failing'], 0)

    def test_rules_count_covers_every_claim_twice(self):
        body = payload()
        self.assertEqual(len(body['rules']),
                         2 * len(body['claims']) + len(body['targets']))
        self.assertEqual(body['totals']['rules'], len(body['rules']))


class Coverage(unittest.TestCase):
    def test_artifacts_skip_the_audit_the_closeout_and_self(self):
        stems = set(AD.artifacts())
        self.assertNotIn('l2_535b0541_lane_closeout', stems)
        self.assertNotIn('l2_535b0541_open_items_audit', stems)
        self.assertNotIn('l2_535b0541_audit_drift', stems)

    def test_the_gate_reads_every_lane_artifact(self):
        stems = set(AD.artifacts())
        self.assertGreaterEqual(len(stems), 40)
        self.assertLessEqual({'l2_535b0541_lane_residue', 'l2_535b0541_cell_identity'},
                             stems)

    def test_report_of_reads_the_docs_and_the_audit_together(self):
        self.assertEqual(AD.report_of('l2_535b0541_lane_residue'), 168)
        self.assertEqual(AD.report_of('l2_535b0541_cell_identity'), 150)
        self.assertEqual(AD.report_of('l2_535b0541_pvp_hunter_arrays'), 149)
        self.assertIsNone(AD.report_of('l2_535b0541_no_such_topic'))

    def test_the_audit_names_cell_identity_now_that_the_docs_fill_its_table(self):
        self.assertEqual(AD.audit_report_of('l2_535b0541_cell_identity'), 150)
        self.assertEqual(AD.audit_report_of('l2_535b0541_pvp_hunter_arrays'), 149)
        self.assertEqual(AD.audit_report_of('l2_535b0541_lane_residue'), 168)

    def test_claims_come_from_the_residue_report(self):
        claims = AD.item_claims()
        self.assertEqual({row['artifact'] for row in claims},
                         {'l2_535b0541_lane_residue'})
        self.assertEqual({row['report'] for row in claims}, {168})

    def test_claim_kinds_are_two_two_five(self):
        claims = AD.item_claims()
        for kind, want in (('closed', 2), ('corrected', 2), ('blocked', 5)):
            self.assertEqual(len([row for row in claims if row['kind'] == kind]), want)

    def test_report_targets_are_the_two_the_audit_cannot_name(self):
        targets = AD.report_claims()
        self.assertEqual(sorted(row['target'] for row in targets), [138, 149])
        self.assertEqual({row['artifact'] for row in targets},
                         {'l2_535b0541_cell_identity'})


class BlindSpot(unittest.TestCase):
    """173 measured 22/43; 174 moved the index to the report filenames, so it is 43/43."""

    def test_every_artifact_is_named_by_the_docs(self):
        body = payload()['blind_spot']
        self.assertEqual(body['unnamed_artifacts'], [])
        self.assertEqual(body['named_by_the_docs'], 49)
        self.assertEqual(body['artifacts'], 49)

    def test_the_audit_alone_now_names_all_of_them(self):
        self.assertEqual(payload()['blind_spot']['named_by_the_audit'], 49)

    def test_nothing_is_left_unnamed(self):
        # 175 filled the audit's table from the report filenames, so the window is empty
        self.assertEqual(payload()['blind_spot']['reports_the_audit_cannot_name'], [])
        self.assertEqual(payload()['blind_spot']['named_by_the_docs'], 49)

    def test_no_correction_now_points_at_an_unnamed_report(self):
        self.assertEqual(payload()['totals']['unread_targets'], [])

    def test_a_missing_doc_is_now_the_tripwire(self):
        index = AD.doc_index()
        self.assertEqual(index[149], 'pvp_hunter_arrays')
        self.assertEqual(index[150], 'cell_identity')
        # 133 is the first report with a `<n>-535b0541-<topic>.md` filename.
        added = sorted(set(AD.known_reports()) - set(AD.AUDIT.REPORTS))
        self.assertEqual(added, [n for n in range(133, 175) if n not in AD.AUDIT.REPORTS])


class RuleSemantics(unittest.TestCase):
    """Each rule is driven with synthetic rows so it is the rule under test."""

    def run_one(self, claim, row, records=(), known=(1,)):
        return AD.run_rules([claim], [], {row['n']: row}, set(known), set(records))

    def test_r1_rejects_a_report_the_audit_never_wrote(self):
        claim = dict(artifact='a', report=None, kind='blocked', n=1, text='t')
        out = self.run_one(claim, synthetic_row(1))
        self.assertFalse([row for row in out if row['rule'] == 'R1-coverage'][0]['passed'])

    def test_r1_accepts_a_known_report(self):
        claim = dict(artifact='a', report=1, kind='blocked', n=1, text='t')
        out = self.run_one(claim, synthetic_row(1))
        self.assertTrue([row for row in out if row['rule'] == 'R1-coverage'][0]['passed'])

    def test_r2_needs_the_closed_verdict_and_the_closer(self):
        claim = dict(artifact='a', report=7, kind='closed', n=1, text='t')
        out = self.run_one(claim, synthetic_row(1, 'CLOSED', 7))
        self.assertTrue([row for row in out if row['rule'] == 'R2-closure'][0]['passed'])
        out = self.run_one(claim, synthetic_row(1, 'CLOSED', 8))
        self.assertFalse([row for row in out if row['rule'] == 'R2-closure'][0]['passed'])
        out = self.run_one(claim, synthetic_row(1, 'OPEN'))
        self.assertFalse([row for row in out if row['rule'] == 'R2-closure'][0]['passed'])

    def test_r3_accepts_a_record_a_closer_or_a_reason(self):
        claim = dict(artifact='a', report=7, kind='corrected', n=1, text='t')
        by_record = self.run_one(claim, synthetic_row(1), records=[(7, 'correction', 1)])
        self.assertTrue([row for row in by_record if row['rule'] == 'R3-correction'][0]['passed'])
        by_closer = self.run_one(claim, synthetic_row(1, 'RESTATED', 7))
        self.assertTrue([row for row in by_closer if row['rule'] == 'R3-correction'][0]['passed'])
        by_reason = self.run_one(claim, synthetic_row(1, 'OPEN', reason='see 7'))
        self.assertTrue([row for row in by_reason if row['rule'] == 'R3-correction'][0]['passed'])

    def test_r3_rejects_a_correction_nobody_recorded(self):
        claim = dict(artifact='a', report=7, kind='corrected', n=1, text='t')
        out = self.run_one(claim, synthetic_row(1, 'OPEN', reason='see 6'))
        self.assertFalse([row for row in out if row['rule'] == 'R3-correction'][0]['passed'])

    def test_r4_rejects_closing_what_the_same_report_calls_blocked(self):
        claim = dict(artifact='a', report=7, kind='blocked', n=1, text='t')
        out = self.run_one(claim, synthetic_row(1, 'CLOSED', 7))
        self.assertFalse([row for row in out if row['rule'] == 'R4-blocker'][0]['passed'])
        out = self.run_one(claim, synthetic_row(1, 'RUNTIME'))
        self.assertTrue([row for row in out if row['rule'] == 'R4-blocker'][0]['passed'])

    def test_r4_rejects_a_blocker_on_an_item_the_audit_does_not_have(self):
        claim = dict(artifact='a', report=7, kind='blocked', n=99, text='t')
        out = AD.run_rules([claim], [], {}, {1}, set())
        self.assertFalse([row for row in out if row['rule'] == 'R4-blocker'][0]['passed'])

    def test_r5_needs_a_target_and_a_known_target(self):
        claim = dict(artifact='a', report=7, target=None, item='t')
        out = AD.run_rules([], [claim], {}, {1}, set())
        self.assertFalse(out[0]['passed'])
        claim = dict(artifact='a', report=7, target=99, item='t')
        out = AD.run_rules([], [claim], {}, {1}, set())
        self.assertFalse(out[0]['passed'])
        claim = dict(artifact='a', report=7, target=1, item='t')
        out = AD.run_rules([], [claim], {}, {1}, set())
        self.assertTrue(out[0]['passed'])


class Contract(unittest.TestCase):
    def setUp(self):
        self.plan = {row['n']: row for row in payload()['contract']}
        self.rows = AD.audit_rows()

    def test_covers_everything_the_audit_does_not_call_closed(self):
        want = {n for n, row in self.rows.items() if row['verdict'] != 'CLOSED'}
        self.assertEqual(set(self.plan), want)

    def test_no_unwritten_step(self):
        self.assertEqual([n for n, row in self.plan.items() if row['kind'] == 'TODO'], [])

    def test_every_row_names_an_owner(self):
        self.assertEqual({row['owner'] for row in self.plan.values()}, {'AI-4', 'owner'})

    def test_kind_counts(self):
        counts = {}
        for row in self.plan.values():
            counts[row['kind']] = counts.get(row['kind'], 0) + 1
        self.assertEqual(counts['RUNTIME'], 19)
        self.assertEqual(counts['POLICY'], 2)   # 180 closed 30/39/40
        self.assertEqual(counts['DATA'], 6)
        self.assertEqual(counts['PIN-RAW'], 3)
        # 179 closed item 32, the only SCAN step in the contract
        self.assertNotIn('SCAN', counts)
        self.assertEqual(counts['TODO'] if 'TODO' in counts else 0, 0)

    def test_the_two_policy_items_are_the_metadata_slots(self):
        self.assertEqual(sorted(n for n, row in self.plan.items()
                                if row['kind'] == 'POLICY'), [51, 52])

    def test_the_six_data_items_are_served_payloads(self):
        self.assertEqual(sorted(n for n, row in self.plan.items()
                                if row['kind'] == 'DATA'), [9, 18, 19, 34, 44, 48])

    def test_device_state_is_labelled_runtime(self):
        for row in self.plan.values():
            if row['kind'] == 'RUNTIME':
                self.assertIn('MODEL_NOT_MEASURED', row['step'])

    def test_policy_rows_say_why_a_probe_is_the_only_route(self):
        for row in self.plan.values():
            if row['kind'] == 'POLICY':
                self.assertTrue('table' in row['step'] or 'slot' in row['step'])

    def test_item_nine_is_served_data_not_a_second_group(self):
        self.assertEqual(self.plan[9]['kind'], 'DATA')
        self.assertIn('served shop payload', self.plan[9]['step'])


class Provenance(unittest.TestCase):
    def test_input_hash_is_the_audit_file(self):
        body = payload()
        path = ROOT / body['provenance']['inputs'][0]['path']
        self.assertEqual(body['provenance']['inputs'][0]['sha256'],
                         hashlib.sha256(path.read_bytes()).hexdigest())

    def test_every_listed_artifact_hashes_to_the_file_on_disk(self):
        rows = payload()['provenance']['artifacts']
        self.assertEqual(len(rows), payload()['totals']['artifacts'])
        for row in rows:
            path = ROOT / row['path']
            self.assertTrue(path.exists(), row['path'])
            self.assertEqual(row['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_the_gate_does_not_hash_itself(self):
        paths = [row['path'] for row in payload()['provenance']['artifacts']]
        self.assertNotIn('datas/l2_535b0541_audit_drift.json.gz', paths)

    def test_limits_name_the_blind_spot(self):
        limits = ' '.join(payload()['limits'])
        self.assertIn('without naming it is still invisible', limits)
        self.assertIn('native probe', limits)


if __name__ == '__main__':
    unittest.main()
