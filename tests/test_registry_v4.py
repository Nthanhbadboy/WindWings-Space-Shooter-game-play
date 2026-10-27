"""Contracts for report 180: registry-v4, and the C1 correction (149 beats 169/177).

C1: 169/177 said the six `Board_PVP` arrays are `NOT_BOUND` and would need a metadata usage
table. 149 had already decoded them through the `InitializeArray` event's `field_id`. The
registry re-derives all six from `field-defaults.json` without trusting 149's printed values.

C2: every item the audit does not call `CLOSED` carries exactly one of five labels plus the
step that would settle it; the counts still add up to the 56 items of report 147.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import registry_v4 as REG  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_registry_v4.json.gz'
PIN_BYTES = 4851
PIN_SHA = 'bcd0e0fd95af375b8841021856209eb701d284bf013966d48f868e9143e21a96'

FIVE = {'shipped-default', 'served', 'policy', 'missing-input', 'runtime-gated→USER'}


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        _, packed = REG.build(None)
        self.assertEqual(packed, ARTIFACT.read_bytes())

    def test_every_check_passes(self):
        self.assertEqual([row['name'] for row in payload()['checks']
                          if not row['passed']], [])


class C1(unittest.TestCase):
    def test_every_array_resolves_through_field_defaults(self):
        binding = payload()['c1']['binding']
        self.assertEqual(len(binding), 6)
        self.assertTrue(all(row['found'] for row in binding))

    def test_all_six_are_twenty_four_bytes_of_six_elements(self):
        binding = payload()['c1']['binding']
        self.assertEqual({row['bytes_available'] for row in binding}, {24})
        self.assertTrue(all(row['agrees'] for row in binding))

    def test_the_values_are_the_published_ones(self):
        values = {row['field']: row['values'] for row in payload()['c1']['binding']}
        self.assertEqual(values['rewardIndexs'], [23, 0, 14, 1, 15, 18])
        self.assertEqual(values['rewardValues'], [100, 10000, 10, 100, 10, 10])
        self.assertEqual(values['allBetCoinValues'],
                         [500, 2000, 5000, 10000, 20000, 50000])
        self.assertEqual(values['allBetGemValues'], [0, 10, 25, 50, 100, 500])
        self.assertEqual(values['allBetMedalValues'], [0, 30, 50, 100, 200, 1000])

    def test_the_float_array_keeps_its_f32_expansion(self):
        values = {row['field']: row['values'] for row in payload()['c1']['binding']}
        scales = values['rewardScales']
        self.assertEqual(scales, [1.0, 1.0, 0.6000000238418579, 1.0,
                                  0.6000000238418579, 0.800000011920929])
        self.assertNotEqual(scales[2], 0.6)

    def test_the_three_items_are_closed_by_149(self):
        closed = payload()['c1']['closed_items']
        self.assertEqual(sorted(int(n) for n in closed), [30, 39, 40])
        self.assertTrue(all(row['closer'] == 149 for row in closed.values()))

    def test_the_old_blocker_is_withdrawn_in_writing(self):
        self.assertIn('NOT_BOUND', payload()['c1']['withdrawn'])
        self.assertIn('metadata usage', payload()['c1']['withdrawn'])

    def test_the_join_is_spelled_out(self):
        self.assertEqual(len(payload()['c1']['join']), 4)


class Ledger(unittest.TestCase):
    def test_thirty_two_rows(self):
        self.assertEqual(payload()['totals']['ledger'], 32)
        self.assertEqual(len(payload()['ledger']), 32)

    def test_the_counts_add_up_to_fifty_six(self):
        totals = payload()['totals']
        self.assertEqual(totals['closed'] + totals['note'] + totals['ledger'],
                         totals['items'])
        self.assertEqual(totals['items'], 56)

    def test_every_row_is_one_of_the_five_labels(self):
        labels = {row['label'] for row in payload()['ledger']}
        self.assertTrue(labels <= FIVE, labels)

    def test_the_label_counts(self):
        self.assertEqual(payload()['totals']['by_label'],
                         {'runtime-gated→USER': 20, 'served': 7,
                          'missing-input': 3, 'policy': 2})

    def test_nothing_is_left_unlabelled_or_unstepped(self):
        for row in payload()['ledger']:
            self.assertTrue(row['label'], row['n'])
            self.assertTrue(row['step'], row['n'])
            self.assertTrue(row['owner'], row['n'])

    def test_no_row_is_closed_or_a_note(self):
        for row in payload()['ledger']:
            self.assertNotIn(row['verdict'], ('CLOSED', 'NOTE'), row['n'])

    def test_the_note_item_is_named_but_not_labelled(self):
        self.assertEqual(payload()['not_in_ledger']['note_items'], [56])

    def test_shipped_default_is_empty_because_the_three_are_closed(self):
        self.assertEqual(payload()['totals']['by_label'].get('shipped-default', 0), 0)

    def test_the_served_rows_are_the_config_dependants(self):
        served = sorted(row['n'] for row in payload()['ledger']
                        if row['label'] == 'served')
        self.assertEqual(served, [18, 19, 27, 34, 44, 48, 54])

    def test_the_missing_input_rows_are_the_unpinned_raws(self):
        missing = sorted(row['n'] for row in payload()['ledger']
                         if row['label'] == 'missing-input')
        self.assertEqual(missing, [12, 49, 50])

    def test_the_policy_rows_carry_an_owner_decision(self):
        rows = [row for row in payload()['ledger'] if row['label'] == 'policy']
        self.assertEqual(sorted(row['n'] for row in rows), [51, 52])
        self.assertTrue(all('owner decision' in row['step'] for row in rows))

    def test_the_policy_note_points_at_the_cheap_retry(self):
        limits = ' '.join(payload()['limits'])
        self.assertIn('30/39/40', limits)
        self.assertIn('MODEL_NOT_MEASURED runtime', limits)


class NoCycle(unittest.TestCase):
    def test_the_registry_does_not_store_the_drift_digest(self):
        """173 hashes this artifact; hashing it back would never converge."""
        self.assertNotIn('sha256', payload()['provenance']['drift'])

    def test_the_gate_still_records_the_taxonomy(self):
        taxonomy = payload()['taxonomy']
        self.assertEqual(set(taxonomy['labels']), FIVE)
        self.assertEqual(len(taxonomy['rules']), 5)


if __name__ == '__main__':
    unittest.main()
