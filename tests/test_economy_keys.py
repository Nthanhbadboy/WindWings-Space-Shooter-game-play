"""Contracts for report 143: the 21 `PlayerPrefs` keys behind `GameDatas`."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import economy_keys  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_economy_keys.json.gz'
PIN_SHA = 'c655860a23529ab8954d69311948735d481aff638d090095eccfc13f3a6eb8f8'
KEYS = ['ArenaMedal', 'ArenaPoints', 'AutoChangePlayer', 'AutoChangePosition',
        'CampaignPoints', 'CoinEvent1', 'ControlType', 'Energy', 'GCoins', 'Gems',
        'GraphicsLevel', 'KeyCount0', 'KeyCount1', 'KeyCount2', 'OverDrive',
        'PvPMedal', 'StarCount', 'TimeRewards', 'UILeftRight', 'VipPoints',
        'WingCoins']


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(economy_keys.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_ten_sources(self):
        self.assertEqual(len(payload()['provenance']['sources']), 10)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])


class UnityCensus(unittest.TestCase):
    def census(self):
        return payload()['census']['unity_playerprefs']

    def test_calls_and_apis(self):
        census = self.census()
        self.assertEqual(census['calls'], 90)
        self.assertEqual(census['apis'], {'GetInt': 48, 'SetInt': 42})

    def test_every_write_is_a_tail_call(self):
        self.assertEqual(self.census()['tails'], 42)
        self.assertIn('tail', self.census()['note'])

    def test_per_raw(self):
        self.assertEqual(self.census()['per_raw'],
                         {'key-grant-535b0541': 45, 'meta-rewards-535b0541': 45})

    def test_gap_histograms(self):
        census = self.census()
        self.assertEqual(census['read_gap_histogram'], {'4': 46, '36': 2})
        self.assertEqual(census['write_gap_histogram'], {'8': 2, '12': 40})
        self.assertEqual(census['gap_histogram'],
                         {'4': 46, '8': 2, '12': 40, '36': 2})

    def test_key_count(self):
        self.assertEqual(self.census()['keys'], 21)


class Keys(unittest.TestCase):
    def test_names(self):
        self.assertEqual([row['key'] for row in payload()['keys']], KEYS)

    def test_every_key_has_both_sides(self):
        for row in payload()['keys']:
            self.assertTrue(row['reads'], row['key'])
            self.assertTrue(row['writes'], row['key'])

    def test_reads_and_writes_match(self):
        for row in payload()['keys']:
            self.assertEqual({entry['api'] for entry in row['reads']}, {'GetInt'})
            self.assertEqual({entry['api'] for entry in row['writes']}, {'SetInt'})

    def test_currency_keys(self):
        rows = {row['key']: row for row in payload()['keys']}
        self.assertEqual(rows['GCoins']['slot_va'], 44941536)
        self.assertEqual(rows['Gems']['slot_va'], 44941496)
        self.assertEqual(rows['StarCount']['slot_va'], 44941512)
        self.assertEqual(rows['WingCoins']['slot_va'], 44941776)

    def test_currency_literals(self):
        rows = {row['key']: row for row in payload()['keys']}
        self.assertEqual(rows['GCoins']['literal'], 46002640)
        self.assertEqual(rows['Gems']['literal'], 46003168)
        self.assertEqual(rows['StarCount']['literal'], 46029696)
        self.assertEqual(rows['WingCoins']['literal'], 46045488)

    def test_key_differs_from_property_name(self):
        rows = {row['key']: row for row in payload()['keys']}
        self.assertEqual(rows['ControlType']['reads'][0]['method'],
                         'public static int get_TypeControl() { }')

    def test_setter_rvas(self):
        rows = {row['key']: row for row in payload()['keys']}
        self.assertEqual({entry['method_rva'] for entry in rows['GCoins']['writes']},
                         {20069860})
        self.assertEqual({entry['method_rva'] for entry in rows['Gems']['writes']},
                         {20069244})


class Currency(unittest.TestCase):
    def test_four_rows(self):
        rows = payload()['currency']['rows']
        self.assertEqual([row['key'] for row in rows],
                         ['GCoins', 'Gems', 'StarCount', 'WingCoins'])

    def test_defaults_agree_with_142(self):
        rows = {row['key']: row for row in payload()['currency']['rows']}
        self.assertEqual(rows['GCoins']['default'], 68999)
        self.assertEqual(rows['Gems']['default'], 500)
        self.assertEqual(rows['StarCount']['default'], 0)
        self.assertEqual(rows['WingCoins']['default'], 999999)

    def test_getter_rvas(self):
        rows = {row['key']: row for row in payload()['currency']['rows']}
        self.assertEqual(rows['GCoins']['getter_rva'], 20069516)
        self.assertEqual(rows['WingCoins']['getter_rva'], 20070312)


class SecondStore(unittest.TestCase):
    def census(self):
        return payload()['census']['game_playerpreferences']

    def test_calls(self):
        census = self.census()
        self.assertEqual(census['calls'], 174)
        self.assertEqual(census['apis'],
                         {'SetInt': 63, 'GetInt': 54, 'SetString': 32,
                          'GetString': 23, 'DeleteKey': 2})

    def test_per_raw(self):
        self.assertEqual(self.census()['per_raw'],
                         {'meta-rewards-535b0541': 74, 'key-grant-535b0541': 49,
                          'arena-pvp-535b0541': 41, 'box-draw-535b0541': 10})

    def test_keys_not_settled(self):
        census = self.census()
        self.assertEqual(census['distinct_keys'], 42)
        self.assertEqual(census['keys_resolved_tightly'], 6)
        self.assertEqual(census['unresolved'], 11)
        self.assertIn('not trusted', census['note'])

    def test_setters_without_playerprefs(self):
        rows = {row['name']: row for row in payload()['setter_without_prefs']}
        self.assertEqual(sorted(rows),
                         ['CanCollectPremiumGift', 'Compensation',
                          'CountThroughAds', 'IsCollectPremiumDailyGift',
                          'IsPremiumTag', 'LastArenaPoints'])
        self.assertTrue(all(row['pinned'] for row in rows.values()))


class Corrections(unittest.TestCase):
    def test_142_correction(self):
        rows = payload()['corrections']
        self.assertEqual(len(rows), 1)
        self.assertIn('142', rows[0]['item'])
        self.assertEqual({row['key'] for row in rows[0]['measured']},
                         {'GCoins', 'Gems', 'StarCount', 'WingCoins'})
        self.assertIn('addend', rows[0]['why'])


class NotDecoded(unittest.TestCase):
    def test_three_items(self):
        self.assertEqual(len(payload()['not_decoded']), 3)

    def test_first_is_runtime(self):
        self.assertIn('MODEL_NOT_MEASURED runtime',
                      payload()['not_decoded'][0]['blocking'])

    def test_second_is_the_game_store(self):
        blocking = payload()['not_decoded'][1]['blocking']
        self.assertIn('174', payload()['not_decoded'][1]['item'] + blocking)


if __name__ == '__main__':
    unittest.main()
