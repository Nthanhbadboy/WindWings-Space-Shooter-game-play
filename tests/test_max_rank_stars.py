"""Contracts for report 135: `PVP_Manager.MaxRankStars` — 10 star ladders, bound to bytes."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import max_rank_stars  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_max_rank_stars.json.gz'
PIN_SHA = '004898a23e08004f4ff595b1734605a5403293ee8d13691f5f3a8b55bd69a69c'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(max_rank_stars.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_four_sources(self):
        sources = payload()['provenance']['sources']
        self.assertEqual(len(sources), 4)
        for row in sources:
            self.assertEqual(len(row['sha256']), 64)
            self.assertTrue((ROOT / row['path']).exists())

    def test_binary_ids(self):
        prov = payload()['provenance']
        self.assertEqual(prov['xapk_sha256'][:8], 'f5d3c7a1')
        self.assertEqual(prov['libil2cpp_sha256'][:8], '9cb038e8')

    def test_method(self):
        method = payload()['method']
        self.assertEqual(method['rva'], 19916640)
        self.assertEqual(method['calls'], 10)


class CctorArrays(unittest.TestCase):
    def test_ten_arrays_in_order(self):
        rows = payload()['cctor_arrays']
        self.assertEqual([row['index'] for row in rows], list(range(10)))
        self.assertEqual([row['length'] for row in rows], [3, 3, 4, 4, 5, 5, 5, 5, 5, 5])
        self.assertEqual([row['initialize_rva'] for row in rows],
                         [19930288, 19930420, 19930540, 19930660, 19930780, 19930892,
                          19931004, 19931116, 19931228, 19931340])

    def test_token_is_odd_handle(self):
        for row in payload()['cctor_arrays']:
            self.assertEqual(row['token_source'], row['token'] & 0x7FFFFFFF)
            self.assertEqual(row['token_source'] % 2, 1)
            self.assertEqual(row['ordinal'], (row['token_source'] - 1) // 2)


class Blobs(unittest.TestCase):
    def blobs(self):
        return payload()['blobs']

    def test_five_distinct_blobs(self):
        rows = self.blobs()
        self.assertEqual(len(rows), 5)
        self.assertEqual([row['length'] for row in rows], [3, 3, 4, 4, 5])
        self.assertEqual([len(row['shared_by']) for row in rows], [1, 1, 1, 1, 6])
        self.assertEqual(len({row['field'] for row in rows}), 5)

    def test_name_is_sha256_of_declared_bytes(self):
        for row in self.blobs():
            data = bytes.fromhex(row['data_hex'])
            self.assertEqual(len(data), row['declared_bytes'])
            self.assertEqual(row['declared_bytes'], 4 * row['length'])
            self.assertEqual(hashlib.sha256(data).hexdigest().upper(), row['field'])

    def test_values_match_declared_bytes(self):
        for row in self.blobs():
            data = bytes.fromhex(row['data_hex'])
            ints = [int.from_bytes(data[i:i + 4], 'little') for i in range(0, len(data), 4)]
            self.assertEqual(ints, row['values'])

    def test_tokens_are_the_five_recorded_handles(self):
        self.assertEqual([row['token_source'] for row in self.blobs()], [13, 255, 1349, 749, 711])


class RankTable(unittest.TestCase):
    def test_star_ladders(self):
        rows = payload()['rank_table']
        self.assertEqual([row['rank'] for row in rows], list(range(10)))
        self.assertEqual([row['stars'] for row in rows],
                         [[3, 3, 3], [4, 4, 4], [4, 4, 4, 4], [5, 5, 5, 5]] +
                         [[5, 5, 5, 5, 5]] * 6)

    def test_six_last_ranks_share_one_blob(self):
        rows = payload()['rank_table']
        self.assertEqual([row['rank'] for row in rows if row['shared']], [4, 5, 6, 7, 8, 9])
        self.assertEqual(len({row['field'] for row in rows if row['shared']}), 1)

    def test_length_matches_reward_levels_for_nine_ranks(self):
        rows = payload()['rank_table']
        mismatched = [row['rank'] for row in rows if not row['length_matches_reward_levels']]
        self.assertEqual(mismatched, [0])
        self.assertTrue(all(row['length_matches_reward_levels'] for row in rows[1:]))

    def test_cells_hold_one_to_five_stars(self):
        for row in payload()['rank_table']:
            self.assertTrue(all(1 <= value <= 5 for value in row['stars']), row)


class Continuity(unittest.TestCase):
    def test_confirms_report_128(self):
        rows = payload()['confirmations']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['item'], '128 §3.4 MaxRankStars values')
        self.assertEqual(rows[0]['status'], 'CONFIRMED')

    def test_cross_checks(self):
        checks = payload()['cross_checks']
        self.assertTrue(checks['name_hash_all_match'])
        self.assertTrue(checks['declared_bytes_all_match'])
        self.assertEqual(checks['reward_level_length_match'], '9/10')
        self.assertEqual(checks['shared_by_six'], [4, 5, 6, 7, 8, 9])

    def test_open_items_name_the_blocker(self):
        items = {row['item']: row['blocking'] for row in payload()['not_decoded']}
        self.assertIn('the method that reads MaxRankStars', items)
        self.assertIn('+0x18', items['the method that reads MaxRankStars'])
        self.assertIn('ordering-only', items['the method that reads MaxRankStars'])
        self.assertIn('MODEL_NOT_MEASURED', items['how stars move during a match'])


if __name__ == '__main__':
    unittest.main()
