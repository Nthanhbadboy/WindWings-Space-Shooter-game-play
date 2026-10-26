"""Contracts for report 148: the open-items audit of lane #29/#30."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import open_items_audit  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_open_items_audit.json.gz'
PIN_SHA = '5416035aca0dbab8090abe64ef16aa191a5cf1e87ba1c26b7bef3a6168ed80ca'
PIN_BYTES = 10010


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces(self):
        rebuilt = json.loads(json.dumps(open_items_audit.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        self.assertEqual(payload()['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', payload()['note'])


class Coverage(unittest.TestCase):
    def test_every_closed_out_item_is_audited_once(self):
        rows = payload()['items']
        self.assertEqual(len(rows), 56)
        pairs = [(row['report'], row['item']) for row in rows]
        self.assertEqual(len(set(pairs)), 56)

    def test_column_numbers_are_the_closeout_columns(self):
        """`n` is the item's position in 147, so the two can be read side by side."""
        closeout = json.loads(gzip.decompress(
            (ROOT / 'datas/l2_535b0541_lane_closeout.json.gz').read_bytes()))
        columns = {(row['report'], row['item']): index
                   for index, row in enumerate(closeout['open_items'], 1)}
        for row in payload()['items']:
            self.assertEqual(row['n'], columns[(row['report'], row['item'])], row['item'])
        self.assertEqual(sorted(row['n'] for row in payload()['items']), list(range(1, 57)))

    def test_matches_the_closeout_inventory(self):
        closeout = json.loads(gzip.decompress(
            (ROOT / 'datas/l2_535b0541_lane_closeout.json.gz').read_bytes()))
        expected = {(row['report'], row['item']) for row in closeout['open_items']}
        self.assertEqual({(row['report'], row['item']) for row in payload()['items']},
                         expected)

    def test_text_comes_from_the_source_artifact(self):
        """148 must not inherit 147's 220-char cut or its `str(None)` rows."""
        for row in payload()['items']:
            source = open_items_audit.item_text(row['report'], row['item'])
            self.assertEqual(row['blocking'], source.get('blocking'), row['item'])

    def test_no_row_keeps_the_string_none(self):
        self.assertFalse([row for row in payload()['items']
                          if row['blocking'] == 'None'])


class Verdicts(unittest.TestCase):
    def test_totals(self):
        totals = payload()['totals']
        self.assertEqual(totals, {'items': 56, 'distinct_questions': 53, 'closed': 17,
                                  'restated': 3, 'actionable': 2, 'runtime': 19,
                                  'note': 1, 'still_open': 14, 'proofs': 24})

    def test_verdicts_partition_the_items(self):
        rows = payload()['items']
        self.assertEqual(sum(1 for row in rows if row['verdict'] == 'CLOSED'), 17)
        self.assertEqual(sum(1 for row in rows if row['verdict'] == 'OPEN'), 14)
        self.assertEqual({row['verdict'] for row in rows},
                         {'CLOSED', 'RESTATED', 'ACTIONABLE', 'RUNTIME', 'NOTE',
                          'OPEN'})

    def test_every_claimed_verdict_has_a_passing_proof(self):
        for row in payload()['items']:
            if row['verdict'] in ('CLOSED', 'RESTATED', 'ACTIONABLE'):
                self.assertTrue(row['evidence'], row['item'])
                self.assertTrue(all(e['pass_'] for e in row['evidence']), row['item'])
            else:
                self.assertEqual(row['evidence'], [], row['item'])

    def test_closure_always_points_at_a_known_report(self):
        for row in payload()['items']:
            if row['closer'] is not None:
                self.assertIn(row['closer'], open_items_audit.REPORTS)
                self.assertNotEqual(row['closer'], row['report'])

    def test_most_closures_come_from_a_later_report(self):
        later = [row for row in payload()['items']
                 if row['verdict'] == 'CLOSED' and row['direction'] == 'later']
        self.assertEqual(len(later), 17)
        earlier = [row for row in payload()['items'] if row['direction'] == 'earlier']
        self.assertEqual([row['report'] for row in earlier], [139, 133, 133])

    def test_backing_split(self):
        self.assertEqual(payload()['verdict_backing']['declared'], 5)
        self.assertEqual(payload()['verdict_backing']['by_content'], 12)


class SpecificClosures(unittest.TestCase):
    def row(self, report, startswith):
        for row in payload()['items']:
            if row['report'] == report and row['item'].startswith(startswith):
                return row
        raise AssertionError(startswith)

    def test_currency_keys_closed_by_143(self):
        row = self.row(142, 'PlayerPrefs key strings')
        self.assertEqual((row['verdict'], row['closer']), ('CLOSED', 143))

    def test_box_tables_closed_by_131(self):
        row = self.row(130, 'contents of BoxKeyCost')
        self.assertEqual((row['verdict'], row['closer']), ('CLOSED', 131))
        actual = row['evidence'][0]['actual']
        self.assertEqual(actual['BoxKeyCost'], [30, 30, 30])
        self.assertEqual(actual['KeyPrices'], [6, 20, 100])
        self.assertEqual(actual['NumberRewards'], [5, 6, 9])

    def test_rank_reader_closed_by_136(self):
        row = self.row(135, 'the method that reads MaxRankStars')
        self.assertEqual((row['verdict'], row['closer']), ('CLOSED', 136))

    def test_gettext_is_code_not_device(self):
        row = self.row(137, 'GetText key-missing behaviour')
        self.assertEqual(row['verdict'], 'OPEN')
        self.assertIn('21202600', row['reason'])

    def test_the_two_blob_decodes_are_actionable(self):
        rows = [row for row in payload()['items'] if row['verdict'] == 'ACTIONABLE']
        self.assertEqual([row['item'] for row in rows],
                         ['amount per stage (rewardValues)',
                          'icon scale per stage (rewardScales)'])
        self.assertEqual(rows[0]['evidence'][0]['actual'], [10493, 'NOT_BOUND'])


class LaneCorrections(unittest.TestCase):
    def test_three_corrections_all_target_147(self):
        rows = payload()['corrections']
        self.assertEqual(len(rows), 3)
        self.assertEqual({row['target'] for row in rows}, {147})

    def test_the_runtime_arithmetic_is_spelled_out(self):
        row = [row for row in payload()['corrections']
               if row['item'].startswith('`runtime_items')][0]
        self.assertEqual(row['evidence']['as_counted'], 17)
        self.assertEqual(row['evidence']['tagged_in_source'], 18)
        self.assertEqual(row['evidence']['by_semantics'], 19)
        self.assertEqual(row['evidence']['untagged_runtime'], [37, 38])
        self.assertEqual(row['evidence']['mistagged'], [49])

    def test_the_text_defect_is_bounded(self):
        row = [row for row in payload()['corrections']
               if 'stringified' in row['item']][0]
        self.assertEqual(row['evidence']['nulls_as_string'], 5)
        self.assertEqual(row['evidence']['null_reports'], [127] * 5)
        self.assertEqual(row['evidence']['cut'], [130, 136, 141, 143])
        self.assertEqual(row['evidence']['cut_at'], 220)

    def test_duplicates(self):
        rows = payload()['duplicates']
        self.assertEqual([row['n'] for row in rows], [[3, 25], [27, 54], [34, 48]])


class Provenance(unittest.TestCase):
    def test_twenty_one_sources(self):
        sources = payload()['provenance']['sources']
        self.assertEqual(len(sources), 21)
        self.assertEqual(sum(1 for row in sources if row['role'] == 'lane artifact'), 20)

    def test_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])

    def test_records_are_declared_and_backed(self):
        records = payload()['records']
        self.assertEqual(len(records), 11)
        for row in records:
            if row['closes'] is not None:
                self.assertTrue(56 >= row['closes'] >= 1)

    def test_next_steps_are_named(self):
        steps = payload()['next_steps']
        self.assertEqual(len(steps), 3)
        self.assertIn('field-defaults.json', steps[0]['how'])


if __name__ == '__main__':
    unittest.main()
