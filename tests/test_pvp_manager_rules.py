"""Contracts for report 134: `PVP_Manager..cctor` rules and the five static tables."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import pvp_manager_rules  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_pvp_manager_rules.json.gz'
PIN_SHA = '5e8feef0dba53bbd863763c32531e2d8a8449b583e51310d6fc409a1e439a546'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(pvp_manager_rules.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_three_sources(self):
        sources = payload()['provenance']['sources']
        self.assertEqual(len(sources), 3)
        for row in sources:
            self.assertEqual(len(row['sha256']), 64)
            self.assertTrue((ROOT / row['path']).exists())

    def test_binary_ids(self):
        prov = payload()['provenance']
        self.assertEqual(prov['xapk_sha256'][:8], 'f5d3c7a1')
        self.assertEqual(prov['libil2cpp_sha256'][:8], '9cb038e8')

    def test_method_identity(self):
        method = payload()['method']
        self.assertEqual(method['rva'], 19916640)
        self.assertEqual(method['size'], 19944)
        self.assertEqual(method['sha256'][:8], '74a43a93')


class Rules(unittest.TestCase):
    def rows(self):
        return {row['field']: row for row in payload()['rules']['fields']}

    def test_six_scalar_stores(self):
        self.assertEqual(sorted(self.rows()),
                         ['IsOpen', 'RankShowCount', 'pvpDatas', 'pvpMaxLife',
                          'pvpTimeScale', 'timePlay'])

    def test_match_defaults(self):
        rows = self.rows()
        self.assertEqual(rows['pvpMaxLife']['value'], 3)
        self.assertEqual(rows['pvpMaxLife']['partner_value'], 1500)
        self.assertEqual(rows['timePlay']['value'], 160)
        self.assertEqual(rows['timePlay']['partner_value'], 10)
        self.assertEqual(rows['RankShowCount']['value'], 100)
        self.assertEqual(rows['pvpTimeScale']['value'], 1.0)
        self.assertIs(rows['IsOpen']['value'], False)
        self.assertIsNone(rows['pvpDatas']['value'])

    def test_pairs_are_int_pairs_not_doubles(self):
        pairs = {tuple(row['fields']): row for row in payload()['rules']['coalesced_int_pairs']}
        self.assertEqual(set(pairs), {('pvpMaxLife', 'pointReduceDie'),
                                      ('timePlay', 'timeStep')})
        self.assertEqual(pairs[('pvpMaxLife', 'pointReduceDie')]['hex'], '03000000dc050000')
        self.assertEqual(pairs[('timePlay', 'timeStep')]['hex'], 'a00000000a000000')
        self.assertEqual(pairs[('pvpMaxLife', 'pointReduceDie')]['words'], [3, 1500])
        self.assertEqual(pairs[('timePlay', 'timeStep')]['pool_va'], 7698896)

    def test_offsets_match_declarations(self):
        rows = self.rows()
        self.assertEqual(rows['pvpMaxLife']['offset'], 0x28)
        self.assertEqual(rows['RankShowCount']['offset'], 0x30)
        self.assertEqual(rows['pvpDatas']['offset'], 0x38)
        self.assertEqual(rows['timePlay']['offset'], 0x40)
        self.assertEqual(rows['pvpTimeScale']['offset'], 0x48)
        self.assertEqual(rows['IsOpen']['offset'], 0x4C)

    def test_float_comes_from_bits(self):
        row = self.rows()['pvpTimeScale']
        self.assertEqual(row['kind'], 'float_bits')
        self.assertEqual(row['bits'], 0x3F800000)


class Seasons(unittest.TestCase):
    def entries(self):
        return payload()['tables']['all_season_rewards']['entries']

    def test_ten_adjacent_bands(self):
        entries = self.entries()
        self.assertEqual([row['rank_start'] for row in entries],
                         [1, 2, 4, 6, 11, 51, 101, 201, 501, 1251])
        self.assertEqual([row['rank_end'] for row in entries],
                         [1, 3, 5, 10, 50, 100, 200, 500, 1250, 3000])
        for left, right in zip(entries, entries[1:]):
            self.assertEqual(left['rank_end'] + 1, right['rank_start'])

    def test_every_band_grants_gems(self):
        entries = self.entries()
        self.assertEqual({row['gifts'][0]['type_name'] for row in entries}, {'Gems'})
        self.assertEqual([row['gifts'][0]['number'] for row in entries],
                         [2000, 1000, 500, 300, 200, 150, 100, 80, 50, 20])

    def test_first_band_uses_movi(self):
        first = self.entries()[0]
        self.assertEqual(first['rank_kind'], 'movi')
        self.assertEqual((first['rank_start'], first['rank_end']), (1, 1))


class SmallTables(unittest.TestCase):
    def test_star_points(self):
        table = payload()['tables']['tournament_add_star_points']
        self.assertEqual(table['values'], [25, 10, 5, -1, -6, -12])
        self.assertEqual(table['assign_rva'], 19920420)

    def test_medal_grid(self):
        table = payload()['tables']['tournament_reward_medals']
        self.assertEqual(len(table['rows']), 14)
        self.assertTrue(all(len(row) == 6 for row in table['rows']))
        self.assertEqual(table['rows'][0], [20, 12, 8, 5, 3, 2])
        self.assertEqual(table['rows'][-1], [100, 60, 40, 25, 15, 10])
        self.assertEqual(table['rows'][-5:], [[100, 60, 40, 25, 15, 10]] * 5)

    def test_max_rank_stars_is_structure_only(self):
        table = payload()['tables']['max_rank_stars']
        self.assertEqual(table['lengths'], [3, 3, 4, 4, 5, 5, 5, 5, 5, 5])
        self.assertIsNone(table['values'])
        self.assertIn('ia-resolved.json', table['blocking'])


class Rewards(unittest.TestCase):
    def entries(self):
        return payload()['tables']['all_rewards']['entries']

    def test_forty_three_rows(self):
        self.assertEqual(len(self.entries()), 43)

    def test_first_row_is_rank_zero_level_one(self):
        first = self.entries()[0]
        self.assertEqual((first['rank'], first['level'], first['medal'], first['gem']),
                         (0, 1, 100, 0))
        self.assertEqual(first['pool_hex'], '00000000010000006400000000000000')

    def test_medal_is_hundred_times_rank_plus_one(self):
        for row in self.entries():
            self.assertEqual(row['medal'], 100 * (row['rank'] + 1))

    def test_gems_only_on_level_zero(self):
        for row in self.entries():
            self.assertEqual(row['gem'] != 0, row['level'] == 0)
        gems = {row['rank']: row['gem'] for row in self.entries() if row['level'] == 0}
        self.assertEqual(gems, {1: 200, 2: 600, 3: 900, 4: 1200, 5: 1400,
                                6: 1600, 7: 1800, 8: 1900, 9: 2000})

    def test_ranks_cover_zero_to_nine(self):
        self.assertEqual(sorted({row['rank'] for row in self.entries()}), list(range(10)))


class Counts(unittest.TestCase):
    def test_identity_totals(self):
        blob = payload()
        totals = blob['totals']
        self.assertEqual(totals['object_ctor'], 53)
        self.assertEqual(totals['add_ref'], 87)
        self.assertEqual(totals['add_int'], 90)
        self.assertEqual(totals['initialize_array'], 10)
        checks = blob['cross_checks']
        self.assertEqual(totals['object_ctor'], checks['seasons'] + checks['rewards'])
        self.assertEqual(totals['add_ref'],
                         checks['seasons'] + checks['seasons'] + checks['medal_rows']
                         + checks['star_arrays'] + checks['rewards'])
        self.assertEqual(totals['add_int'], 6 + 14 * 6)

    def test_cross_checks(self):
        checks = payload()['cross_checks']
        self.assertEqual(checks['rewards'], 43)
        self.assertEqual(checks['seasons'], 10)
        self.assertEqual(checks['medal_columns'], 84)
        self.assertEqual(checks['star_arrays'], 10)

    def test_table_write_sites(self):
        sites = payload()['statics']['table_write_sites']
        self.assertEqual(sites, {'AllSeasonRewards': 19919772,
                                 'TournamentAddStarPoints': 19920420,
                                 'TournamentRewardMedals': 19930240,
                                 'MaxRankStars': 19931460,
                                 'AllRewards': 19936528})
        self.assertEqual(payload()['statics']['write_count'], 11)


class Correction(unittest.TestCase):
    def test_reward_row_count_correction_recorded(self):
        rows = payload()['corrections']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['item'], 'AllRewards row count')
        self.assertIn('42', rows[0]['report_127'])
        self.assertIn('43', rows[0]['measured'])

    def test_open_items_are_blockers_not_guesses(self):
        items = {row['item']: row['blocking'] for row in payload()['not_decoded']}
        self.assertIn('MaxRankStars values', items)
        self.assertIn('MODEL_NOT_MEASURED', items['how remote config rewrites these defaults'])


if __name__ == '__main__':
    unittest.main()
