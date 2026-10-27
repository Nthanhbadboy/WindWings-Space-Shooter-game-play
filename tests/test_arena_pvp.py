"""Contracts for the static Arena/PvP decode (report 127-arena-pvp-535b0541).

Every assertion re-derives a number the report states, from the pinned original
APK bytes recorded in `reverse-engineering/raw/arena-pvp-535b0541/native.json.gz`.
Nothing here starts the game, an emulator, or a device, and no test may present a
static value as runtime behaviour.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/verify'))
import arena_pvp  # noqa: E402
from arena_pvp_initializers import decode_class, class_layouts  # noqa: E402

NATIVE = arena_pvp.load_native()
DATA = json.loads(gzip.decompress((ROOT / 'datas/l2_535b0541_arena_pvp.json.gz').read_bytes()))


class ArtifactContract(unittest.TestCase):
    def test_evidence_level_is_static_only(self):
        self.assertEqual(DATA['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertEqual(DATA['runtime'], 'MODEL_NOT_MEASURED runtime')
        self.assertEqual(DATA['provenance']['xapk_sha256'],
                         'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e')
        self.assertEqual(DATA['provenance']['libil2cpp_sha256'],
                         '9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99')

    def test_raw_bytes_hash_matches_provenance(self):
        raw = (ROOT / DATA['provenance']['raw_path']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), DATA['provenance']['raw_sha256'])

    def test_every_method_row_is_addressable(self):
        rows = DATA['method_index']
        self.assertEqual(len(rows), DATA['inventory']['methods'])
        self.assertEqual(len({r['rva'] for r in rows}), len(rows))
        self.assertTrue(all(0 < r['size'] < 262144 for r in rows))
        self.assertTrue(all(len(r['sha256']) == 64 for r in rows))

    def test_not_decoded_items_are_declared_not_invented(self):
        items = {d['item'] for d in DATA['not_decoded']}
        self.assertIn('PVP_Manager.MaxRankStars array contents', items)
        self.assertIsNone(DATA['pvp']['rankStars']['values'])


class MapPoolContract(unittest.TestCase):
    def setUp(self):
        fields = DATA['map_pools']['fields']
        self.start = fields['AllArenaStartMaps']['tree']
        self.random = fields['AllArenaRandomMaps']['tree']
        self.pvp = fields['AllPvPStartMaps']['tree']
        self.tryplayer = fields['listMapTryPlayerDatas']['tree']

    def test_decode_reproduces_artifact(self):
        self.assertEqual(arena_pvp.decode_map_pools(NATIVE), DATA['map_pools'])

    def test_ten_arena_ranks_with_declining_start_lists(self):
        self.assertEqual(len(self.start['values']), 10)
        self.assertEqual([len(entry['values']) for entry in self.start['values']],
                         [8, 9, 8, 7, 6, 5, 5, 5, 5, 5])
        self.assertTrue(all(all(isinstance(map_id, int) for row in entry['values']
                                for map_id in row['values'])
                            for entry in self.start['values']))

    def test_random_pools_are_two_maps_per_rank(self):
        self.assertEqual(len(self.random['values']), 10)
        self.assertTrue(all(len(entry['values']) == 2 for entry in self.random['values']))

    def test_pvp_start_pool_is_ten_maps_per_rank(self):
        self.assertEqual(len(self.pvp['values']), 10)
        self.assertTrue(all(len(entry['values']) == 10 for entry in self.pvp['values']))

    def test_tryplayer_list_matches_its_literal_blob(self):
        self.assertEqual(len(self.tryplayer['values']), 1)
        self.assertEqual(self.tryplayer['values'][0]['values'], [5, 66, 9010])

    def test_pvp_random_accessor_reads_pvp_start_pool(self):
        """There is no AllPvPRandomMaps field in this build."""
        accessor = DATA['map_accessors']['GetListMapPvPRandom']
        self.assertTrue(accessor['uses_AllPvPStartMaps_for_random'])
        self.assertEqual(accessor['pool_offset'], '0x18')
        fields = class_layouts()['Map_Get_Datas']
        names = {name for name, _ in fields.values()}
        self.assertIn('AllPvPStartMaps', names)
        self.assertNotIn('AllPvPRandomMaps', names)

    def test_indexed_accessors_guard_rank_but_random_ones_do_not(self):
        for name in ('GetListMapArena', 'GetListMapPvP'):
            self.assertTrue(DATA['map_accessors'][name]['negative_rank_guarded'], name)
            self.assertTrue(DATA['map_accessors'][name]['out_of_range_falls_back_to_index_zero'], name)
        for name in ('GetListMapArenaRandom', 'GetListMapPvPRandom'):
            self.assertFalse(DATA['map_accessors'][name]['negative_rank_guarded'], name)
            self.assertFalse(DATA['map_accessors'][name]['out_of_range_falls_back_to_index_zero'], name)


class ScoreContract(unittest.TestCase):
    def test_artifact_samples_are_reproducible(self):
        for mode, enemy, rank, life, expected in DATA['score']['samples']:
            self.assertEqual(arena_pvp.score(mode, enemy, rank, life), expected,
                             (mode, enemy, rank, life))

    def test_unknown_enemy_returns_one(self):
        self.assertEqual(arena_pvp.score(6, 39000, 10, 0.0), 1)
        self.assertEqual(arena_pvp.score(6, 40001, 10, 3.0), 1)

    def test_rank_scale_tiers_come_from_the_loaded_roster_size(self):
        self.assertEqual(arena_pvp.score(5, 30001, 5), 45)     # 9 * 5
        self.assertEqual(arena_pvp.score(5, 30001, 14), 18)    # 9 * 2
        self.assertEqual(arena_pvp.score(5, 30001, 22), 9)     # 9 * 1
        self.assertEqual(arena_pvp.score(5, 30001, 28), 4)     # 9*0.5 = 4.5 -> ties to even
        self.assertEqual(arena_pvp.score(5, 30001, 40), 2)     # 9 * 0.2

    def test_enemy_tier_boundaries(self):
        self.assertEqual([arena_pvp.score(5, e, 0) for e in (30999, 35999, 36999, 37999, 38999, 39999)],
                         [45, 125, 325, 900, 30, 1500])
        self.assertEqual([arena_pvp.score(6, e, 0, 100.0) for e in (37999, 39999)], [1750, 1750])

    def test_pvp_time_factor_tiers(self):
        # base 9 * rank-scale 5 = 45, then the timeLife factor
        self.assertEqual(arena_pvp.score(6, 30001, 0, 0.0), 104)    # 45 * 2.3 = 103.5 -> 104
        self.assertEqual(arena_pvp.score(6, 30001, 0, 0.005), 104)
        self.assertEqual(arena_pvp.score(6, 30001, 0, 0.05), 90)    # 45 * 2.0
        self.assertEqual(arena_pvp.score(6, 30001, 0, 56.0), 45)    # beyond last tier -> 1.0
        self.assertEqual(arena_pvp.score(6, 30001, 0, 100.0), 45)

    def test_arena_score_ignores_time_life(self):
        self.assertEqual(arena_pvp.score(5, 35000, 10, 0.0), arena_pvp.score(5, 35000, 10, 30.0))

    def test_arena_dispatcher_requires_rank_six_for_pvp_math(self):
        """GetArenaScore uses PvP time math only when listStaticEmemies.Count == 6."""
        m = arena_pvp.method(NATIVE, 'Enemy_Data_Balance', 'GetArenaScore')
        text = [f"{i['mnemonic']} {i['op_str']}" for i in m['instructions']]
        self.assertIn('cmp w20, #6', text)
        self.assertIn('b #0x1320fbc', text)   # GetArenaPlayScore branch
        self.assertIn('b #0x1320cc4', text[:text.index('b #0x1320fbc')])  # GetPVPPlayScore branch

    def test_score_literals_trace_to_pinned_bytes(self):
        import struct
        literals = DATA['score']['constants']['GetPVPPlayScore']['literals']
        floats = {round(struct.unpack('<f', bytes.fromhex(row['hex']))[0], 5) for row in literals}
        self.assertTrue({2.3, 1.8, 1.6, 1.7, 2.8, 4.2, 1.4, 1.3, 1.2, 1.1, 0.56, 0.2, 0.1} <= floats, floats)
        self.assertIn(0.01, floats)
        self.assertTrue(all(row['instruction_rva'] and row['hex'] for row in literals))


class PointsCodecContract(unittest.TestCase):
    def test_round_trip_below_clamp(self):
        for rank in range(0, 10):
            for level in range(0, 5):
                for star in range(0, 5):
                    for point in (0, 37, 99):
                        total = arena_pvp.to_points(rank, level, star, point)
                        self.assertEqual(arena_pvp.to_points(**{
                            'rank': arena_pvp.data_from_points(total)['pvpRank'],
                            'level': arena_pvp.data_from_points(total)['pvpLevel'],
                            'star': arena_pvp.data_from_points(total)['pvpStars'],
                            'point': arena_pvp.data_from_points(total)['pvpPoints'],
                        }), total)

    def test_point_one_hundred_does_not_round_trip(self):
        total = arena_pvp.to_points(1, 2, 3, 100)
        self.assertEqual(arena_pvp.data_from_points(total)['pvpPoints'], 0)
        self.assertEqual(arena_pvp.to_points(1, 2, 3, 100), 1230100)

    def test_negative_point_clamps_to_zero(self):
        self.assertEqual(arena_pvp.to_points(1, 2, 3, -50), arena_pvp.to_points(1, 2, 3, 0))


class StaticsContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stats = {cls_name: decode_class(NATIVE, cls_name)
                     for cls_name in ('ArenaConfig', 'ArenaManager', 'PVP_Manager')}

    def value(self, cls, field):
        return self.stats[cls]['fields'][field]['value']

    def test_arena_config_room_bounds_and_summary_time(self):
        self.assertEqual(self.value('ArenaConfig', 'MaxRoomCount'), 50)
        self.assertEqual(self.value('ArenaConfig', 'MinRoomCount'), 10)
        self.assertEqual(self.value('ArenaConfig', 'SummaryTime'), 60.0)
        self.assertEqual(self.value('ArenaConfig', 'IsOpen'), 0)

    def test_arena_manager_bootstrap_constants(self):
        self.assertEqual(self.value('ArenaManager', 'MaxRoomCount'), 50)
        self.assertEqual(self.value('ArenaManager', 'MinUserCount'), 25)
        self.assertEqual(self.value('ArenaManager', 'SeasonSummaryTime'), 60.0)
        self.assertIsNone(self.value('ArenaManager', 'SeasonTimes'))
        self.assertIsNone(self.value('ArenaManager', 'RankUpIndexs'))
        self.assertIsNone(self.value('ArenaManager', 'RankDropIndexs'))

    def test_arena_reward_array_is_ten_slots(self):
        rewards = self.value('ArenaManager', 'rewards')
        self.assertEqual(rewards['length'], 10)
        self.assertEqual(len(rewards['values']), 10)
        self.assertTrue(all(v['kind'] == 'metadata' for v in rewards['values']))

    def test_pvp_scalars(self):
        scalars = {k: self.value('PVP_Manager', k) for k in
                   ('pvpMaxLife', 'pointReduceDie', 'RankShowCount', 'timePlay',
                    'timeStep', 'pvpTimeScale', 'IsOpen')}
        self.assertEqual(scalars, dict(pvpMaxLife=3, pointReduceDie=1500, RankShowCount=100,
                                       timePlay=160, timeStep=10, pvpTimeScale=1.0, IsOpen=0))

    def test_tournament_tables(self):
        self.assertEqual(DATA['pvp']['tournamentAddStarPoints'], [25, 10, 5, -1, -6, -12])
        rows = DATA['pvp']['tournamentRewardMedals']
        self.assertEqual(len(rows), 14)
        self.assertTrue(all(len(row) == 6 for row in rows))
        self.assertEqual(rows[0], [20, 12, 8, 5, 3, 2])
        self.assertEqual(rows[9], [100, 60, 40, 25, 15, 10])

    def test_all_rewards_rows_follow_their_medal_rule(self):
        rows = DATA['pvp']['allRewards']
        self.assertEqual(len(rows), 42)
        for row in rows:
            self.assertEqual(row['medal'], 100 * (row['rank'] + 1))
            if row['level']:
                self.assertEqual(row['gem'], 0)
        self.assertEqual((rows[0]['rank'], rows[0]['level'], rows[0]['medal']), (0, 2, 100))
        self.assertEqual((rows[-1]['rank'], rows[-1]['level'], rows[-1]['medal'], rows[-1]['gem']),
                         (9, 4, 1000, 0))

    def test_season_reward_brackets_are_contiguous(self):
        rows = DATA['pvp']['seasonRewards']
        self.assertEqual(len(rows), 10)
        cursor = 1
        numbers = []
        for row in rows:
            self.assertEqual(row['rankStart'], cursor)
            self.assertGreaterEqual(row['rankEnd'], row['rankStart'])
            cursor = row['rankEnd'] + 1
            self.assertEqual(len(row['gifts']), 1)
            self.assertTrue(all(gift['type'] == 1 for gift in row['gifts']))
            numbers.append(row['gifts'][0]['number'])
        self.assertEqual(cursor - 1, 3000)
        self.assertEqual(numbers, [2000, 1000, 500, 300, 200, 150, 100, 80, 50, 20])

    def test_room_predicates(self):
        self.assertEqual(DATA['rules']['room']['isFull'], 'players.Count >= max')
        self.assertEqual(DATA['rules']['room']['isEmpty'], 'players.Count == 0')
        room = arena_pvp.method(NATIVE, 'Room', 'IsFull')
        ops = [i['op_str'] for i in room['instructions'] if i['mnemonic'] == 'cset']
        self.assertEqual(ops, ['w0, ge'])


if __name__ == '__main__':
    unittest.main()
