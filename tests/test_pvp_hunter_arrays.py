"""Contracts for report 149: the six `Board_PVP..ctor` arrays."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import pvp_hunter_arrays  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_pvp_hunter_arrays.json.gz'
PIN_SHA = '034bb93bc8cd3585d07bc47d56a2465d90a205619b57acbef004e694a1333975'
PIN_BYTES = 3648


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


def array(name):
    for row in payload()['arrays']:
        if row['field'].endswith('.' + name):
            return row
    raise AssertionError(name)


class ArtifactPin(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces(self):
        rebuilt = json.loads(json.dumps(pvp_hunter_arrays.build(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        self.assertEqual(payload()['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', payload()['note'])


class Arrays(unittest.TestCase):
    def test_six_arrays_at_the_offsets_133_listed(self):
        rows = payload()['arrays']
        self.assertEqual(len(rows), 6)
        self.assertEqual([row['instance_offset'] for row in rows],
                         [408, 416, 424, 520, 528, 536])

    def test_names_and_types(self):
        self.assertEqual({row['field'].split('.')[1] for row in payload()['arrays']},
                         {'rewardIndexs', 'rewardValues', 'rewardScales',
                          'allBetCoinValues', 'allBetGemValues', 'allBetMedalValues'})
        self.assertEqual(array('rewardScales')['declared'], 'float[]')
        self.assertEqual(array('rewardScales')['element_type'], 'float32')
        for name in ('rewardIndexs', 'rewardValues', 'allBetCoinValues',
                     'allBetGemValues', 'allBetMedalValues'):
            self.assertEqual(array(name)['declared'], 'int[]', name)

    def test_values(self):
        self.assertEqual(array('rewardIndexs')['values'], [23, 0, 14, 1, 15, 18])
        self.assertEqual(array('rewardValues')['values'], [100, 10000, 10, 100, 10, 10])
        self.assertEqual(array('allBetCoinValues')['values'],
                         [500, 2000, 5000, 10000, 20000, 50000])
        self.assertEqual(array('allBetGemValues')['values'], [0, 10, 25, 50, 100, 500])
        self.assertEqual(array('allBetMedalValues')['values'], [0, 30, 50, 100, 200, 1000])

    def test_scales_are_binary32(self):
        """0.6 and 0.8 are not exact in f32; the report must keep the widened values."""
        values = array('rewardScales')['values']
        self.assertEqual([round(v, 3) for v in values], [1.0, 1.0, 0.6, 1.0, 0.6, 0.8])
        self.assertEqual(array('rewardScales')['blob']['default_raw_hex'][16:24],
                         '9a99193f')
        self.assertNotEqual(values[2], 0.6)

    def test_every_row_is_a_24_byte_blob(self):
        for row in payload()['arrays']:
            self.assertEqual(row['elements'], 6, row['field'])
            self.assertEqual(row['blob']['declared_bytes'], 24, row['field'])
            self.assertEqual(row['token']['kind'], 4, row['field'])
            self.assertEqual(row['token']['source'] % 2, 1, row['field'])
            self.assertEqual(row['token']['pid_type_index'], 2461, row['field'])


class Ladders(unittest.TestCase):
    def test_stage_ladder(self):
        rows = payload()['stage_table']
        self.assertEqual([(row['stage'], row['reward_type'], row['amount'])
                          for row in rows],
                         [(0, 23, 100), (1, 0, 10000), (2, 14, 10),
                          (3, 1, 100), (4, 15, 10), (5, 18, 10)])
        self.assertEqual([row['handler'] for row in rows],
                         ['set_PvPMedal', 'set_Coins', 'SetDroneCards',
                          'set_Gems', 'SetPlayerCards', 'set_KeyCount2'])

    def test_key_stage_is_the_one_133_named(self):
        cross = payload()['cross_checks']
        self.assertEqual(cross['key_stage_amount'],
                         {'stage': 5, 'type_id': 18, 'amount': 10})
        self.assertTrue(cross['key_stage_slot_matches_133'])

    def test_three_bet_ladders_with_their_index_fields(self):
        rows = payload()['bet_ladders']
        self.assertEqual([row['field'] for row in rows],
                         ['allBetCoinValues', 'allBetGemValues', 'allBetMedalValues'])
        self.assertEqual([row['index_field'] for row in rows],
                         ['betCoins', 'betGems', 'betMedals'])
        self.assertEqual([row['index_offset'] for row in rows], [0x1F8, 0x1FC, 0x200])

    def test_ladders_are_ascending_and_have_a_reader(self):
        for row in payload()['bet_ladders']:
            self.assertTrue(row['ascending'], row['field'])
            self.assertTrue(row['distinct'], row['field'])
            self.assertTrue(row['reader'], row['field'])
            self.assertIn(row['index_field'].replace('bet', 'OnChange'),
                          row['reader'][0]['signature'])

    def test_ladder_0_is_free_in_gems_and_medals(self):
        """Corroborates the labels: the cheapest entry costs coins only."""
        coin = array('allBetCoinValues')['values']
        gem = array('allBetGemValues')['values']
        medal = array('allBetMedalValues')['values']
        self.assertEqual((coin[0], gem[0], medal[0]), (500, 0, 0))


class CrossChecks(unittest.TestCase):
    def test_all_true(self):
        cross = payload()['cross_checks']
        for key in ('reward_indexs_blob_matches_133', 'reward_indexs_values_match_133',
                    'reward_indexs_domain', 'key_stage_slot_matches_133',
                    'scales_are_fractional', 'arena_raw_has_no_initialize_arrays'):
            self.assertTrue(cross[key], key)

    def test_the_other_raw_really_has_no_events(self):
        """This is why 133 called the handle slots unresolved — checked, not asserted."""
        raw = json.loads(gzip.decompress(
            (ROOT / 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz').read_bytes()))
        ctor = [m for m in raw['methods']
                if m['class_name'] == 'Board_PVP' and '.ctor' in m['signature']][0]
        self.assertFalse(ctor.get('initialize_arrays'))
        self.assertEqual(ctor['rva'], payload()['chain']['ctor']['rva'])

    def test_checks_all_pass(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 18)
        self.assertTrue(all(row['passed'] for row in checks))


class Provenance(unittest.TestCase):
    def test_five_sources(self):
        sources = payload()['provenance']['sources']
        self.assertEqual(len(sources), 5)
        for row in sources:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])

    def test_four_confirmations_record_what_closes(self):
        rows = payload()['confirmations']
        self.assertEqual(len(rows), 4)
        self.assertIn('rewardValues', rows[0]['item'])
        self.assertIn('bet_tables', rows[3]['item'])

    def test_what_stays_open(self):
        rows = payload()['not_decoded']
        self.assertEqual(len(rows), 3)
        self.assertTrue(any('MODEL_NOT_MEASURED' in row['blocking'] for row in rows))
        self.assertTrue(any('0x2ADF238' in row['item'] for row in rows))


if __name__ == '__main__':
    unittest.main()
