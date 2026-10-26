"""Contracts for report 152: `ArenaConfig` — the shipped season ladder."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import arena_config_ladders  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_arena_config_ladders.json.gz'
PIN_BYTES = 4743
PIN_SHA = 'cc6bc93a3d83bbe897cf59e6eb321f0527723b8fb6d2ab9e94e6d918c6eb052a'
UP = [20, 15, 15, 10, 10, 10, 10, 10, 10, 10]
MINUTES = [1440, 2880, 4320, 7200, 10080, 11520, 12960, 14400, 15840, 17280]


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(arena_config_ladders.build(), sort_keys=True,
                          separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_five_sources(self):
        self.assertEqual(len(payload()['provenance']['sources']), 5)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])

    def test_upstream_reports_are_139_and_151(self):
        paths = [row['path'] for row in payload()['provenance']['sources']]
        self.assertIn('datas/l2_535b0541_arena_rewards.json.gz', paths)
        self.assertIn('datas/l2_535b0541_arena_statics.json.gz', paths)


class Cctor(unittest.TestCase):
    def test_pinned_body(self):
        body = payload()['arena_config']['cctor']
        self.assertEqual((body['rva'], body['size']), (22726640, 164))
        self.assertEqual(len(body['sha256']), 64)

    def test_six_offsets_seven_values(self):
        writes = payload()['arena_config']['cctor']['writes']
        self.assertEqual([row['offset'] for row in writes],
                         [0x0, 0x8, 0x10, 0x14, 0x18, 0x1C])
        self.assertEqual([row['field'] for row in writes],
                         ['RankSplit', 'SeasonTime', 'MaxRoomCount', 'MinRoomCount',
                          'SummaryTime', 'IsOpen'])
        self.assertEqual(writes[2]['rva'], writes[3]['rva'])

    def test_packed_literal(self):
        packed = payload()['arena_config']['cctor']['packed_literal']
        self.assertEqual(packed['hex'], '320000000a000000')
        self.assertEqual(packed['decoded'], {'MaxRoomCount': 50, 'MinRoomCount': 10})
        self.assertEqual(packed['va'], 7696928)

    def test_summary_time_is_60f(self):
        self.assertEqual(payload()['arena_config']['cctor']['summary_time'], 60.0)
        write = payload()['arena_config']['cctor']['writes'][4]
        self.assertEqual(write['source'], {'imm': '0x42700000'})

    def test_is_open_false(self):
        self.assertEqual(payload()['arena_config']['cctor']['writes'][5]['source'],
                         {'value': False})

    def test_field_offsets_match_139(self):
        self.assertEqual([row['offset'] for row in payload()['arena_config']['fields']],
                         ['0x0', '0x8', '0x10', '0x14', '0x18', '0x1c'])


class Ladders(unittest.TestCase):
    def test_rank_split_text(self):
        blob = payload()['ladders']['rank_split']
        self.assertEqual(blob['text'], ';'.join('%d-45' % up for up in UP))
        self.assertEqual(blob['seasons'], 10)

    def test_up_bounds(self):
        self.assertEqual(payload()['ladders']['observed']['up_by_season'], UP)

    def test_down_bound_is_45_everywhere(self):
        self.assertEqual(set(payload()['ladders']['observed']['down_by_season']), {45})

    def test_season_time_text(self):
        blob = payload()['ladders']['season_times']
        self.assertEqual(blob['text'], ';'.join(str(v) for v in MINUTES))
        self.assertEqual(blob['seasons'], 10)

    def test_minutes_are_whole_days(self):
        rows = payload()['ladders']['season_times']['rows']
        self.assertTrue(all(row['whole_days'] for row in rows))
        self.assertEqual([int(row['days']) for row in rows],
                         [1, 2, 3, 5, 7, 8, 9, 10, 11, 12])
        self.assertEqual(payload()['ladders']['observed']['total_days'], 68)

    def test_seasons_monotonically_longer(self):
        values = payload()['ladders']['observed']['minutes_by_season']
        self.assertEqual(values, sorted(values))

    def test_windows_are_contiguous_and_widen(self):
        rows = payload()['ladders']['rank_split']['rows']
        self.assertTrue(all(row['up'] < row['down'] for row in rows))
        self.assertEqual([row['widths'] for row in rows],
                         sorted(row['widths'] for row in rows))


class Units(unittest.TestCase):
    def test_unit_is_minutes(self):
        blob = payload()['units']
        self.assertEqual(blob['unit'], 'minutes')
        self.assertIn('DateTime.AddMinutes(double)', blob['chain'])

    def test_addminutes_rva(self):
        self.assertEqual(payload()['units']['method']['rva'], 22720624)
        add = next(fact for fact in payload()['units']['facts']
                   if fact['rva'] == 22721096)
        self.assertEqual(add['rva'], 22721096)
        self.assertEqual(add['op'], 'bl #0x20e6cf0')

    def test_chain_ends_in_the_rank_setup(self):
        chain = payload()['units']['chain']
        self.assertIn('SeasonTimes[season] (int)', chain[0])
        self.assertIn('seasonEnd', chain[-1])

    def test_season_end_is_a_tobinary_long(self):
        facts = payload()['season_end']['facts']
        self.assertEqual([fact['rva'] for fact in facts],
                         [22717660, 22717688, 22717732, 22717760])
        self.assertIn('ToInt64', facts[1]['meaning'])
        self.assertIn('FromBinary', facts[2]['meaning'])


class Semantics(unittest.TestCase):
    def test_four_rules(self):
        rules = payload()['semantics']['rules']
        self.assertEqual(len(rules), 4)
        self.assertEqual(rules[0]['effect'], 'arenaRank = min(arenaRank + 1, 9)')
        self.assertEqual(rules[2]['effect'], 'arenaRank = max(arenaRank - 1, 0)')

    def test_promotion_branches_on_the_up_bound(self):
        steps = {row['rva']: row['op'] for row in payload()['semantics']['steps']}
        self.assertEqual(steps[22719892], 'b.le #0x15aaec4')
        self.assertEqual(steps[22720212], 'str w9, [x8, #0x1c]')

    def test_demotion_reads_the_drop_array(self):
        steps = {row['rva']: row['op'] for row in payload()['semantics']['steps']}
        self.assertEqual(steps[22719928], 'ldr x10, [x9, #0x30]')
        self.assertEqual(steps[22719968], 'sub w9, w9, #1')
        self.assertEqual(steps[22719972], 'bic w9, w9, w9, asr #31')

    def test_reset_writes_minus_one(self):
        steps = {row['rva']: row['op'] for row in payload()['semantics']['steps']}
        self.assertEqual(steps[22720220], 'str w9, [x8, #0x28]')
        self.assertEqual(steps[22720224], 'str w9, [x8, #0x20]')


class Census(unittest.TestCase):
    def test_scope(self):
        blob = payload()['census']
        self.assertEqual(blob['slices'], 8)
        self.assertEqual(blob['methods_dumped'], 2499)
        self.assertIn('not the whole binary', blob['scope'])

    def test_nine_methods(self):
        self.assertEqual(payload()['census']['methods_touching'], 9)
        self.assertEqual(len(payload()['census']['rows']), 9)

    def test_summary_time_is_never_read(self):
        silent = {row['offset']: row['field']
                  for row in payload()['census']['never_touched']}
        self.assertEqual(silent, {'0x4': 'MaxRoomCount', '0x8': 'MinUserCount',
                                  '0x10': 'SeasonSummaryTime'})

    def test_helpers_resolve_to_the_right_classes(self):
        roles = {row['rva']: row['signature'] for row in payload()['helpers']}
        self.assertIn('AddMinutes', roles[34499824])
        self.assertIn('ToBinary', roles[34503640])
        self.assertIn('FromBinary', roles[34502572])
        self.assertIn('ToInt64', roles[34376300])


class Findings(unittest.TestCase):
    def test_all_checks_pass(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 20)
        self.assertTrue(all(row['passed'] for row in checks), checks)

    def test_four_confirmations(self):
        self.assertEqual(len(payload()['confirmations']), 4)

    def test_three_open_items(self):
        rows = payload()['open_items']
        self.assertEqual(len(rows), 3)
        self.assertIn('MODEL_NOT_MEASURED runtime', rows[0]['blocking'])
        self.assertIn('bounded negative', rows[1]['blocking'])

    def test_reward_band_and_demote_bound_agree(self):
        cross = payload()['cross_checks']
        self.assertEqual(cross['last_reward_band_low'], 46)
        self.assertEqual(cross['down_bound'], 45)

    def test_rvas_are_integers(self):
        self.assertIsInstance(payload()['units']['method']['rva'], int)
        self.assertIsInstance(payload()['arena_config']['cctor']['rva'], int)


if __name__ == '__main__':
    unittest.main()
