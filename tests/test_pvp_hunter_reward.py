"""Contracts for report 133: the PvP hunter reward table and its six slots."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import pvp_hunter_reward  # noqa: E402
import key_sources  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_pvp_hunter_reward_table.json.gz'
PIN_SHA = '4649f273aacb59fa063e691d5d2726aab932bc8da48174668963887fa5bdfa79'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(pvp_hunter_reward.build_payload(), sort_keys=True))
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


class Constructor(unittest.TestCase):
    def test_six_arrays_of_six(self):
        rows = payload()['table']['arrays']
        self.assertEqual([row['field'] for row in rows],
                         ['rewardIndexs', 'rewardValues', 'rewardScales',
                          'allBetCoinValues', 'allBetGemValues', 'allBetMedalValues'])
        self.assertEqual([row['store_offset'] for row in rows],
                         [0x198, 0x1A0, 0x1A8, 0x208, 0x210, 0x218])
        self.assertEqual([row['length'] for row in rows], [6] * 6)

    def test_offsets_match_declarations(self):
        lines = key_sources.dump_lines()
        fields = key_sources.field_offsets(lines, 'Board_PVP')
        for row in payload()['table']['arrays']:
            self.assertEqual(fields[row['field']], row['store_offset'], row['field'])

    def test_initialize_array_sites(self):
        rvas = [row['initarray_rva'] for row in payload()['table']['arrays']]
        self.assertEqual(rvas, sorted(rvas))
        self.assertTrue(all(19796420 <= rva < 19796920 for rva in rvas))


class RewardIndexs(unittest.TestCase):
    def test_values(self):
        self.assertEqual(payload()['table']['reward_indexs']['values'],
                         [23, 0, 14, 1, 15, 18])

    def test_identification_is_unique(self):
        row = payload()['table']['reward_indexs']
        self.assertEqual(row['candidates_scanned'], 48)
        self.assertGreater(row['pid_blobs'], 900)
        self.assertIn('only six-int', row['identification'])
        self.assertEqual(len(bytes.fromhex(row['raw'])), 32)

    def test_domain_is_exactly_the_handled_ids(self):
        row = payload()['table']['reward_indexs']
        self.assertEqual(row['value_domain'], [0, 1, 14, 15, 18, 23])
        self.assertEqual(sorted(payload()['handlers'], key=int),
                         ['0', '1', '14', '15', '18', '23'])

    def test_gift_type_labels_match_the_enum(self):
        lines = key_sources.dump_lines()
        enum = key_sources.enum_values(lines, 'GiftType')
        for type_id in [int(k) for k in payload()['handlers']]:
            self.assertEqual(key_sources.GIFT_TYPES[type_id], enum[type_id])


class Stages(unittest.TestCase):
    def test_six_stages_in_blob_order(self):
        stages = payload()['stages']
        self.assertEqual([row['type_id'] for row in stages], [23, 0, 14, 1, 15, 18])
        self.assertEqual([row['collectible_point'] for row in stages],
                         [1, 3, 5, 7, 9, 11])

    def test_only_the_last_slot_pays_keys(self):
        stages = payload()['stages']
        granted = [row['slot'] for row in stages if row['granted']]
        self.assertEqual(granted, [5])
        self.assertEqual(stages[5]['granted'], 'KeyCount2')
        self.assertEqual(stages[5]['handler'], 'set_KeyCount2')
        self.assertEqual(payload()['key_stage']['slot'], 5)
        self.assertEqual(payload()['key_stage']['collectible_point'], 11)

    def test_no_stage_pays_key0_or_key1(self):
        for row in payload()['stages']:
            self.assertNotIn(row['handler'], ('set_KeyCount0', 'set_KeyCount1'))


class Points(unittest.TestCase):
    def test_marker_arithmetic(self):
        points = payload()['points']
        self.assertEqual(points['total_markers'], 12)
        self.assertTrue(all(points['checks'].values()), points['checks'])
        self.assertIn('(marker - 1) / 2', points['rule'])
        self.assertEqual(points['clickable'], 'odd markers only')


class Gate(unittest.TestCase):
    def test_season_accessors(self):
        gate = payload()['gate']
        self.assertEqual((gate['season_getter'], gate['season_setter'], gate['season_dies']),
                         (19784460, 19794028, 19784352))
        self.assertIn('SeasonProgress', gate['collectable'])
        self.assertIn('SeasonDies', gate['visible'])
        self.assertIn('1.5', gate['progress_bar'])


class Blockers(unittest.TestCase):
    def test_amounts_and_scales_not_bound(self):
        table = payload()['table']
        for name in ('reward_values', 'reward_scales'):
            self.assertEqual(table[name]['status'], 'NOT_BOUND')
            self.assertTrue(table[name]['blocking'])

    def test_bet_tables_not_bound(self):
        bet = payload()['table']['bet_tables']
        self.assertEqual(bet['status'], 'NOT_BOUND')
        self.assertEqual(bet['candidate_pool'], {'six_int_blobs': 48, 'ascending': 18})
        self.assertEqual([row['offset'] for row in bet['fields']], [0x208, 0x210, 0x218])

    def test_not_decoded_all_carry_a_blocker(self):
        rows = payload()['not_decoded']
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertTrue(row['blocking'])
        self.assertTrue(any('MODEL_NOT_MEASURED runtime' in row['blocking'] for row in rows))


if __name__ == '__main__':
    unittest.main()
