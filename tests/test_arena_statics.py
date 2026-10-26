"""Contracts for report 139: ArenaManager statics, the payout table, the config bridge."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import arena_statics  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_arena_statics.json.gz'
PIN_SHA = '261eca3a7268b5450fed691b224edaf09979a1ff9ca8662fd9ab68f48399a4b5'
PLACEMENTS = ['1', '2', '3-4', '5-10', '11-45', '46-50']


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(arena_statics.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_three_sources(self):
        self.assertEqual(len(payload()['provenance']['sources']), 3)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])


class Layout(unittest.TestCase):
    def test_arena_manager_fields(self):
        fields = payload()['layout']['arena_manager']
        self.assertEqual([field['name'] for field in fields],
                         ['IsOpen', 'MaxRoomCount', 'MinUserCount', 'SeasonSummaryTime',
                          'SeasonTimes', 'RankMapsIndex', 'RankUpIndexs', 'RankDropIndexs',
                          'rewards'])
        self.assertEqual([field['offset'] for field in fields],
                         [0x0, 0x4, 0x8, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38])

    def test_arena_config_fields(self):
        fields = payload()['layout']['arena_config']
        self.assertEqual([field['name'] for field in fields],
                         ['RankSplit', 'SeasonTime', 'MaxRoomCount', 'MinRoomCount',
                          'SummaryTime', 'IsOpen'])
        self.assertEqual([field['offset'] for field in fields],
                         [0x0, 0x8, 0x10, 0x14, 0x18, 0x1C])

    def test_slots_in_decimal(self):
        slots = payload()['layout']['slots']
        self.assertEqual(slots['arena_manager']['decimal'], 0x2AE19D0)
        self.assertEqual(slots['arena_config']['decimal'], 0x2AECA98)


class Cctor(unittest.TestCase):
    def test_pinned_body(self):
        blob = payload()['cctor']
        self.assertEqual((blob['rva'], blob['size']), (22692372, 516))
        self.assertEqual(len(blob['sha256']), 64)

    def test_nine_writes_covering_every_field(self):
        writes = payload()['cctor']['writes']
        self.assertEqual(len(writes), 9)
        self.assertEqual([row['offset'] for row in writes],
                         [0x0, 0x4, 0x8, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38])

    def test_values(self):
        values = {row['field']: row['value'] for row in payload()['cctor']['writes']}
        self.assertIs(values['IsOpen'], False)
        self.assertEqual(values['MaxRoomCount'], 50)
        self.assertEqual(values['MinUserCount'], 25)
        self.assertEqual(values['SeasonSummaryTime'], 60.0)
        self.assertEqual(values['RankMapsIndex'], 0)
        self.assertIsNone(values['SeasonTimes'])
        self.assertIsNone(values['RankUpIndexs'])
        self.assertIsNone(values['RankDropIndexs'])
        self.assertEqual(values['rewards'], 'string[10]')

    def test_packed_literal(self):
        packed = payload()['cctor']['packed_literal']
        self.assertEqual(packed['hex'], '3200000019000000')
        self.assertEqual(packed['decoded'], {'MaxRoomCount': 50, 'MinUserCount': 25})
        self.assertIn('5.3e-313', packed['note'])

    def test_double_literal(self):
        double = payload()['cctor']['double_literal']
        self.assertEqual(double['bit_pattern'], '0x404E000000000000')
        self.assertEqual(double['value'], 60.0)

    def test_newarr(self):
        newarr = payload()['cctor']['newarr']
        self.assertEqual((newarr['rva'], newarr['length']), (22692604, 10))


class Rewards(unittest.TestCase):
    def test_ten_rows_six_bands(self):
        rewards = payload()['rewards']
        self.assertEqual(rewards['count'], 10)
        self.assertEqual(rewards['bands'], PLACEMENTS)

    def test_rank_order(self):
        self.assertEqual([row['rank'] for row in payload()['rewards']['rows']],
                         list(range(10)))

    def test_first_row_values(self):
        bands = payload()['rewards']['rows'][0]['bands']
        self.assertEqual([(b['placement'], b['medal'], b['gems']) for b in bands],
                         [('1', 680, 250), ('2', 460, 180), ('3-4', 320, 120),
                          ('5-10', 200, 80), ('11-45', 120, 50), ('46-50', 60, 20)])

    def test_top_row_values(self):
        bands = payload()['rewards']['rows'][9]['bands']
        self.assertEqual([(b['placement'], b['medal'], b['gems']) for b in bands],
                         [('1', 5000, 1000), ('2', 3380, 720), ('3-4', 2350, 480),
                          ('5-10', 1470, 320), ('11-45', 880, 200), ('46-50', 440, 80)])

    def test_monotonic_down_a_band(self):
        rows = payload()['rewards']['rows']
        for column in range(6):
            medals = [row['bands'][column]['medal'] for row in rows]
            gems = [row['bands'][column]['gems'] for row in rows]
            self.assertEqual(medals, sorted(medals))
            self.assertEqual(gems, sorted(gems))

    def test_every_element_store_pinned(self):
        rvas = [row['element_rva'] for row in payload()['rewards']['rows']]
        self.assertEqual(rvas[0], 22692640)
        self.assertEqual(rvas[-1], 22692852)
        self.assertEqual(len(set(rvas)), 10)


class Bridge(unittest.TestCase):
    def setUp(self):
        self.method = payload()['config_bridge']['method']

    def test_pinned_body(self):
        self.assertEqual((self.method['rva'], self.method['size']), (22782048, 800))

    def test_reads_arena_config(self):
        reads = [(row['offset'], row['field']) for row in self.method['reads']]
        self.assertEqual(reads, [(0x10, 'MaxRoomCount'), (0x14, 'MinRoomCount'),
                                 (0x18, 'SummaryTime'), (0x8, 'SeasonTime'),
                                 (0x0, 'RankSplit')])

    def test_writes_arena_manager(self):
        writes = [(row['offset'], row['field']) for row in self.method['writes']]
        self.assertEqual(writes, [(0x4, 'MaxRoomCount'), (0x8, 'MinUserCount'),
                                  (0x10, 'SeasonSummaryTime'), (0x18, 'SeasonTimes'),
                                  (0x28, 'RankUpIndexs'), (0x30, 'RankDropIndexs')])

    def test_pipeline_steps(self):
        steps = [row['step'] for row in self.method['pipeline']]
        self.assertIn('Split(\';\')', steps)
        self.assertIn('Split(\'-\')', steps)
        self.assertEqual(steps.count('Int32.Parse'), 1)
        self.assertEqual(sum('Int32.Parse' in step for step in steps), 3)

    def test_quote_strip_first(self):
        first = self.method['pipeline'][1]
        self.assertIn('Replace', first['step'])
        self.assertEqual(first['signature'], 'public string Replace(string oldValue, string newValue) { }')


class Corrections(unittest.TestCase):
    def test_gate_belongs_to_arena_config(self):
        rows = payload()['corrections']
        self.assertEqual(len(rows), 1)
        self.assertIn('ArenaConfig.IsOpen', rows[0]['measured'])
        self.assertIn('0x2AECA98', rows[0]['measured'])

    def test_confirmation_of_127(self):
        rows = payload()['confirmations']
        self.assertIn('Board_Arena.GetConfigs', rows[0]['result'])


class Open(unittest.TestCase):
    def test_three_open_items(self):
        self.assertEqual(len(payload()['not_decoded']), 3)

    def test_to_roman_sweep(self):
        sweep = payload()['to_roman_sweep']
        self.assertEqual(sweep['rva'], 21103836)
        self.assertEqual(sweep['found_in'], [])
        self.assertGreaterEqual(sweep['raws_searched'], 8)


if __name__ == '__main__':
    unittest.main()
