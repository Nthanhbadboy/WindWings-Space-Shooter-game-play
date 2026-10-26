"""Contracts for report 144: the `PlayerPreferences` store's keys, by register tracking."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import game_store_keys  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_game_store_keys.json.gz'
PIN_SHA = '75974f5a3313f47a66daccc3973f39b1038a211f0e750f3b04691315ec7324ad'
KEYS = ['VersionProfile', 'Local_Arena_Rank', 'FIRST_OPEN_ARENA', 'CountOpen',
        'FirstGetPower', 'FIRST_OPEN_PVP', 'HunterSeasonProgress',
        'HunterSeasonDies', 'IsFirstOpenQuest', 'TotalGemSpend', 'Compensation',
        'PREMIUM_DAILY_COLLECTED', 'PRO_ExpiryDateTime', 'CanCollectPremiumGift',
        'IsPremiumTag', 'CountThroughAds', 'LastArenaPoints',
        'TIME_EVENT_DOUBLE_ENDED', 'IS_FIRST_TIME_EVENT', 'IsEventStarted',
        'IS_BUY_EVENT_COMBO', 'TIME_VIDEO_ACTIVE', 'VIDEO_CURRENT_INDEX',
        'LUCKY_VALUE_4', 'LUCKY_VALUE_5']
PREFIXES = ['ARENA_SHOP_ITEM_ID', 'ARENA_SHOP_ITEM_STOCK', 'HunterCollectProgress',
            'PVP_SHOP_ITEM_ID', 'PVP_SHOP_ITEM_STOCK', 'Quest_Value_Key',
            'Quest_Collect_Index', 'Quest_Check_Collect_Index',
            'STOCK_EXCHANGE_EVENT1_', 'FIRST_FREE_BOX', None, 'GET_VIDEO_DONE',
            'GET_VIDEO_UNLOCK']


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(game_store_keys.build_payload(), sort_keys=True))
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


class Store(unittest.TestCase):
    def test_class_and_apis(self):
        store = payload()['store']
        self.assertEqual(store['class'], 'PlayerPreferences')
        self.assertEqual(len(store['apis']), 10)
        self.assertEqual(store['apis']['20912644'], 'SetInt')
        self.assertEqual(store['apis']['20912660'], 'SetString')
        self.assertEqual(store['apis']['20912964'], 'DeleteKey')
        self.assertIn('JSON-backed', store['note'])


class Census(unittest.TestCase):
    def census(self):
        return payload()['census']

    def test_calls(self):
        self.assertEqual(self.census()['calls'], 184)

    def test_by_api(self):
        self.assertEqual(self.census()['by_api'],
                         {'SetInt': 67, 'GetInt': 58, 'SetString': 32,
                          'GetString': 25, 'DeleteKey': 2})

    def test_by_raw(self):
        self.assertEqual(self.census()['by_raw'],
                         {'meta-rewards-535b0541': 80, 'key-grant-535b0541': 49,
                          'arena-pvp-535b0541': 41, 'box-draw-535b0541': 10,
                          'key-jump-535b0541': 4})

    def test_by_kind(self):
        self.assertEqual(self.census()['by_kind'],
                         {'literal': 115, 'computed': 43, 'unknown': 26})

    def test_tail_calls(self):
        self.assertEqual(self.census()['tail_calls'], 51)

    def test_headline_counts(self):
        census = self.census()
        self.assertEqual(census['literal_keys'], 25)
        self.assertEqual(census['computed_prefixes'], 12)
        self.assertEqual(census['unknown_calls'], 26)

    def test_by_kind_sums_to_calls(self):
        self.assertEqual(sum(self.census()['by_kind'].values()), 184)


class LiteralKeys(unittest.TestCase):
    def test_names_in_first_appearance_order(self):
        self.assertEqual([row['key'] for row in payload()['literal_keys']], KEYS)

    def test_call_total(self):
        self.assertEqual(sum(len(row['calls']) for row in payload()['literal_keys']), 115)

    def test_every_row_has_literal(self):
        for row in payload()['literal_keys']:
            self.assertIsInstance(row['literal'], int, row['key'])

    def test_first_open_keys(self):
        rows = {row['key']: row for row in payload()['literal_keys']}
        self.assertEqual(rows['FIRST_OPEN_ARENA']['literal'], 46000200)
        self.assertEqual(rows['FIRST_OPEN_PVP']['literal'], 46000232)

    def test_version_profile_is_write_only(self):
        rows = {row['key']: row for row in payload()['literal_keys']}
        self.assertEqual({call['api'] for call in rows['VersionProfile']['calls']},
                         {'SetString'})
        self.assertEqual(len(rows['VersionProfile']['calls']), 6)

    def test_delete_key_pair(self):
        rows = {row['key']: row for row in payload()['literal_keys']}
        self.assertEqual({call['api'] for call in rows['TIME_VIDEO_ACTIVE']['calls']},
                         {'DeleteKey'})
        self.assertEqual(len(rows['TIME_VIDEO_ACTIVE']['calls']), 2)

    def test_expiry_key_carries_the_free_version_default(self):
        rows = {row['key']: row for row in payload()['literal_keys']}
        defaults = {call['default'] for call in rows['PRO_ExpiryDateTime']['calls']}
        self.assertIn('FREE_VERSION', defaults)


class ComputedKeys(unittest.TestCase):
    def test_prefixes_in_order(self):
        self.assertEqual([row['prefix'] for row in payload()['computed_keys']], PREFIXES)

    def test_call_total(self):
        self.assertEqual(sum(len(row['calls']) for row in payload()['computed_keys']), 43)

    def test_shop_prefixes(self):
        prefixes = {row['prefix']: row for row in payload()['computed_keys']}
        for name in ('ARENA_SHOP_ITEM_ID', 'ARENA_SHOP_ITEM_STOCK',
                     'PVP_SHOP_ITEM_ID', 'PVP_SHOP_ITEM_STOCK'):
            self.assertIn(name, prefixes)

    def test_one_concat_without_a_literal_first_argument(self):
        prefixes = [row['prefix'] for row in payload()['computed_keys']]
        self.assertEqual(prefixes.count(None), 1)


class UnknownCalls(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(payload()['unknown_calls']), 26)

    def test_key_jump_methods_are_present(self):
        methods = {row['method'] for row in payload()['unknown_calls']}
        self.assertTrue(any('SetRewards' in name for name in methods), methods)
        self.assertTrue(any('RandomCards' in name for name in methods), methods)


class Defaults(unittest.TestCase):
    def test_values(self):
        self.assertEqual(payload()['defaults']['values'],
                         {'FREE_VERSION': 22, 'OFF': 1})


class CrossCheck(unittest.TestCase):
    def test_six_keys_from_143(self):
        block = payload()['cross_check']
        self.assertEqual(block['report'], 143)
        self.assertEqual(sorted(block['keys']),
                         sorted(['Compensation', 'CanCollectPremiumGift',
                                 'IsPremiumTag', 'CountThroughAds',
                                 'LastArenaPoints', 'PREMIUM_DAILY_COLLECTED']))


class NotDecoded(unittest.TestCase):
    def test_three_items(self):
        self.assertEqual(len(payload()['not_decoded']), 3)

    def test_first_is_the_unknown_group(self):
        self.assertIn('26', payload()['not_decoded'][0]['item'])

    def test_second_is_the_index_half(self):
        self.assertIn('index', payload()['not_decoded'][1]['blocking'])

    def test_third_is_runtime(self):
        self.assertIn('MODEL_NOT_MEASURED runtime',
                      payload()['not_decoded'][2]['blocking'])


if __name__ == '__main__':
    unittest.main()
