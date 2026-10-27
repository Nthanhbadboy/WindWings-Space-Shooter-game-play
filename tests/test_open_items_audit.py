"""Contracts for report 148 — and for 170, which taught the audit to read 168/169.

148 froze verdicts over the 56 items as they stood at 147. Two reports later the lane
had closed two more items and narrowed three, and the audit was still printing the old
verdicts, so 170 adds 168/169 to its `REPORTS`/`PROOFS` and re-derives every proof.
"""
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
PIN_SHA = '3b782ffa0f8605b7ea0632803ef662a9c792b9c0a59293aef1b7772fae33a0d3'
PIN_BYTES = 10748


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
        self.assertEqual(totals, {'items': 56, 'distinct_questions': 53, 'closed': 19,
                                  'restated': 6, 'actionable': 0, 'runtime': 20,
                                  'note': 1, 'still_open': 10, 'proofs': 28})

    def test_verdicts_partition_the_items(self):
        rows = payload()['items']
        self.assertEqual(sum(1 for row in rows if row['verdict'] == 'CLOSED'), 19)
        self.assertEqual(sum(1 for row in rows if row['verdict'] == 'OPEN'), 10)
        self.assertEqual({row['verdict'] for row in rows},
                         {'CLOSED', 'RESTATED', 'RUNTIME', 'NOTE', 'OPEN'})

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
        self.assertEqual(len(later), 19)
        earlier = [row for row in payload()['items'] if row['direction'] == 'earlier']
        self.assertEqual([row['report'] for row in earlier], [139])
        # the two 133 items used to sit here; 169 ran the route and narrowed them instead
        self.assertEqual(sorted(row['n'] for row in payload()['items']
                                if row['closer'] == 169), [30, 39, 40])

    def test_backing_split(self):
        self.assertEqual(payload()['verdict_backing']['declared'], 5)
        self.assertEqual(payload()['verdict_backing']['by_content'], 14)


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

    def test_the_two_blob_decodes_are_narrowed_by_169(self):
        rows = [row for row in payload()['items']
                if row['verdict'] == 'RESTATED' and row['closer'] == 169
                and 'per stage' in row['item']]
        self.assertEqual(sorted(row['item'] for row in rows),
                         ['amount per stage (rewardValues)',
                          'icon scale per stage (rewardScales)'])
        for row in rows:
            self.assertEqual(row['evidence'][0]['actual'], [982, 99, 7, 3, 4])

    def test_there_is_no_actionable_left(self):
        self.assertEqual([row for row in payload()['items']
                          if row['verdict'] == 'ACTIONABLE'], [])

    def test_the_rewards_consumer_is_closed_by_168(self):
        row = self.row(139, '`rewards` consumer')
        self.assertEqual((row['verdict'], row['closer']), ('CLOSED', 168))
        self.assertEqual(row['evidence'][0]['actual'], [22795496, 22793460, 22795328])

    def test_the_save_data_amount_is_closed_by_168(self):
        row = self.row(132, 'per-call pack amount')
        self.assertEqual((row['verdict'], row['closer']), ('CLOSED', 168))
        self.assertEqual(row['evidence'][0]['actual'], [1, 'mov w2, #1', 19187472])

    def test_the_pvp_stage_item_is_narrowed_by_169(self):
        row = self.row(132, 'PvP stage reward types')
        self.assertEqual((row['verdict'], row['closer']), ('RESTATED', 169))

    def test_the_shop_prices_are_served_not_shipped(self):
        row = self.row(127, 'medal shop prices')
        self.assertEqual(row['verdict'], 'RUNTIME')
        self.assertEqual(row['evidence'], [])
        self.assertIn('168', row['reason'])


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
        self.assertEqual(row['evidence']['by_semantics'], 20)
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

    def test_the_later_reports_are_read_but_not_hashed(self):
        """168 pins this artifact, so hashing 168 here would be a cycle."""
        labels = {row['label'] for row in payload()['items'] for row in row['evidence']}
        self.assertEqual(sorted(label for label in labels if '168' in label or '169' in label),
                         ['168-rewards-chain', '168-save-data',
                          '169-blob-census', '169-pvp-arrays'])

    def test_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])

    def test_records_are_declared_and_backed(self):
        records = payload()['records']
        self.assertEqual(len(records), 13)
        for row in records:
            if row['closes'] is not None:
                self.assertTrue(56 >= row['closes'] >= 1)

    def test_next_steps_are_named(self):
        steps = payload()['next_steps']
        self.assertEqual(len(steps), 3)
        self.assertIn('field-defaults.json', steps[0]['how'])


class ReportTable(unittest.TestCase):
    """175: the table stops being a hand-maintained list of the reports we remembered."""

    def test_the_table_has_no_holes(self):
        numbers = sorted(open_items_audit.REPORTS)
        self.assertEqual(numbers, list(range(numbers[0], numbers[-1] + 1)))

    def test_every_report_with_a_doc_is_named(self):
        docs = open_items_audit._doc_index()
        self.assertTrue(set(docs) <= set(open_items_audit.REPORTS))
        self.assertGreaterEqual(len(docs), 42)

    def test_the_pinned_names_survive_the_merge(self):
        # a doc filename is not always the artifact name; the pinned rows must win
        self.assertEqual(open_items_audit.REPORTS[134], 'pvp_manager_rules')
        self.assertEqual(open_items_audit.REPORTS[136], 'pvp_rank_api')
        self.assertEqual(open_items_audit.REPORTS[168], 'lane_residue')

    def test_the_two_numbers_173_got_wrong_are_150_and_149(self):
        self.assertEqual(open_items_audit.REPORTS[150], 'cell_identity')
        self.assertEqual(open_items_audit.REPORTS[149], 'pvp_hunter_arrays')

    def test_filling_the_table_does_not_move_the_artifact(self):
        # the table is an index: no item, no proof and no digest lives in it
        _, packed = open_items_audit.build(None)
        self.assertEqual(hashlib.sha256(packed).hexdigest(),
                         '3b782ffa0f8605b7ea0632803ef662a9c792b9c0a59293aef1b7772fae33a0d3')


if __name__ == '__main__':
    unittest.main()
