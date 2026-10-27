"""Contracts for report 140: ArenaConfig defaults, the shipped season table, the gate chain."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import arena_config  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_arena_config.json.gz'
PIN_SHA = 'd3552cea30dfecbef34c325e67e43db382c022238da3f6ad2fa79540985b56dc'
DURATIONS = [1440, 2880, 4320, 7200, 10080, 11520, 12960, 14400, 15840, 17280]
LOWS = [20, 15, 15, 10, 10, 10, 10, 10, 10, 10]


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(arena_config.build_payload(), sort_keys=True))
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
    def test_six_fields(self):
        fields = payload()['layout']['fields']
        self.assertEqual([field['name'] for field in fields],
                         ['RankSplit', 'SeasonTime', 'MaxRoomCount', 'MinRoomCount',
                          'SummaryTime', 'IsOpen'])
        self.assertEqual([field['offset'] for field in fields],
                         [0x0, 0x8, 0x10, 0x14, 0x18, 0x1C])

    def test_slots_in_decimal(self):
        slots = payload()['layout']['slots']
        self.assertEqual(slots['arena_config']['decimal'], 0x2AECA98)
        self.assertEqual(slots['arena_manager']['decimal'], 0x2AE19D0)


class Cctor(unittest.TestCase):
    def test_pinned_body(self):
        blob = payload()['cctor']
        self.assertEqual((blob['rva'], blob['size']), (22726640, 164))
        self.assertEqual(len(blob['sha256']), 64)

    def test_six_writes(self):
        writes = payload()['cctor']['writes']
        self.assertEqual([row['offset'] for row in writes],
                         [0x0, 0x8, 0x10, 0x14, 0x18, 0x1C])

    def test_values(self):
        values = {row['field']: row['value'] for row in payload()['cctor']['writes']}
        self.assertEqual(values['RankSplit'].split(';')[:2], ['20-45', '15-45'])
        self.assertEqual(values['SeasonTime'].split(';')[0], '1440')
        self.assertEqual(values['MaxRoomCount'], 50)
        self.assertEqual(values['MinRoomCount'], 10)
        self.assertEqual(values['SummaryTime'], 60.0)
        self.assertIs(values['IsOpen'], False)

    def test_packed_literal(self):
        packed = payload()['cctor']['packed_literal']
        self.assertEqual(packed['hex'], '320000000a000000')
        self.assertEqual(packed['decoded'], {'MaxRoomCount': 50, 'MinRoomCount': 10})

    def test_float_literal(self):
        literal = payload()['cctor']['summary_literal']
        self.assertEqual(literal['bits'], '0x42700000')
        self.assertEqual(literal['value'], 60.0)
        self.assertIn('not an address', literal['note'])


class Seasons(unittest.TestCase):
    def test_ten_seasons(self):
        self.assertEqual(payload()['seasons']['count'], 10)

    def test_durations(self):
        self.assertEqual([row['minutes'] for row in payload()['seasons']['rows']],
                         DURATIONS)

    def test_whole_days(self):
        for row in payload()['seasons']['rows']:
            self.assertEqual(row['days'], float(row['minutes'] // 1440))

    def test_rank_windows(self):
        rows = payload()['seasons']['rows']
        self.assertEqual([row['rank_low'] for row in rows], LOWS)
        self.assertTrue(all(row['rank_high'] == 45 for row in rows))

    def test_totals(self):
        totals = payload()['seasons']['totals']
        self.assertEqual(totals['first_minutes'], 1440)
        self.assertEqual(totals['last_minutes'], 17280)
        self.assertEqual(totals['unique_durations'], 10)


class UnitProof(unittest.TestCase):
    def test_add_minutes_signature(self):
        call = payload()['unit_proof']['call']
        self.assertEqual(call['rva'], 34499824)
        self.assertEqual(call['signature'], 'public DateTime AddMinutes(double value) { }')

    def test_four_witnesses(self):
        rvas = [row['instruction_rva'] for row in payload()['unit_proof']['witnesses']]
        self.assertEqual(rvas, [22721052, 22721096, 22708728, 22708776])

    def test_verdict(self):
        self.assertIn('minutes', payload()['unit_proof']['verdict'])


class GateChain(unittest.TestCase):
    def test_five_steps(self):
        steps = payload()['gate_chain']['steps']
        self.assertEqual([row['rva'] for row in steps],
                         [22810692, 22810696, 22810700, 22810736, 22810796])

    def test_reads_arena_config_is_open(self):
        self.assertEqual(payload()['gate_chain']['steps'][0]['reads'],
                         'ArenaConfig.IsOpen')

    def test_calls_get_configs_then_game_config(self):
        steps = payload()['gate_chain']['steps']
        self.assertEqual(steps[2]['target_rva'], 22782048)
        self.assertEqual(steps[4]['target_rva'], 22798808)
        self.assertEqual(steps[4]['signature'],
                         'private void GetGameConfig(Action<bool> success) { }')

    def test_game_config_slot(self):
        slot = payload()['gate_chain']['game_config_slot']
        self.assertEqual(slot['decimal'], 44939488)


class Access(unittest.TestCase):
    def test_three_writers(self):
        writers = {(row['class_name'], row['name'])
                   for row in payload()['access']['writers']}
        self.assertEqual(writers, {('ArenaConfig', '.cctor'),
                                   ('ArenaManager', 'LoadRemoteConfigs'),
                                   ('ArenaManager.<>c__DisplayClass44_0',
                                    '<LoadRemoteConfigs>g__OnListCountLoaded|0')})

    def test_two_readers(self):
        readers = {row['name'] for row in payload()['access']['readers']}
        self.assertEqual(readers, {'MoveNext', 'GetConfigs'})

    def test_get_configs_is_not_a_config_writer(self):
        row = [item for item in payload()['access']['arena_config']
               if item['rva'] == 22782048][0]
        self.assertEqual([item for item in row['accesses'] if item['kind'] == 'write'], [])

    def test_get_configs_writes_arena_manager(self):
        row = [item for item in payload()['access']['arena_manager']
               if item['rva'] == 22782048][0]
        writes = {item['offset'] for item in row['accesses'] if item['kind'] == 'write'}
        self.assertEqual(writes, {0x4, 0x8, 0x10, 0x18, 0x28, 0x30})


class Method(unittest.TestCase):
    def test_slot_keyed(self):
        self.assertTrue(payload()['method']['slot_keyed'])

    def test_regression_witness(self):
        witness = payload()['method']['regression_witness']
        self.assertEqual(witness['rva'], 22782328)
        self.assertIn('ArenaManager', witness['correct_result'])
        self.assertIn('ArenaConfig', witness['naive_result'])


class CrossChecks(unittest.TestCase):
    def test_season_times_match_139_bridge(self):
        cross = payload()['cross_checks']['arena_manager_season_times']
        self.assertEqual(cross['minutes'], DURATIONS)

    def test_summary_time_agrees(self):
        cross = payload()['cross_checks']['summary_time_matches_139']
        self.assertEqual(cross['arena_config'], cross['arena_manager'])

    def test_room_counts(self):
        counts = payload()['cross_checks']['room_counts']
        self.assertEqual(counts['arena_config'], {'MaxRoomCount': 50, 'MinRoomCount': 10})
        self.assertEqual(counts['arena_manager'], {'MaxRoomCount': 50, 'MinUserCount': 10})


class Open(unittest.TestCase):
    def test_two_open_items(self):
        self.assertEqual(len(payload()['not_decoded']), 2)

    def test_game_config_class_unnamed(self):
        rows = payload()['not_decoded']
        self.assertIn('0x2ADB8E0', rows[0]['item'])

    def test_remote_overrides_are_runtime(self):
        self.assertIn('MODEL_NOT_MEASURED runtime', payload()['not_decoded'][1]['blocking'])


if __name__ == '__main__':
    unittest.main()
