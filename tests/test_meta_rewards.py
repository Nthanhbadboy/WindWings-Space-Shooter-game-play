"""Contracts for the daily/weekly meta reward decode (#30). STATIC evidence only."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/verify'))
import meta_rewards  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_meta_rewards.json.gz'


class MetaRewardsArtifact(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_bytes = ARTIFACT.read_bytes()
        cls.payload = json.loads(gzip.decompress(cls.raw_bytes))

    # -- provenance ------------------------------------------------------
    def test_evidence_is_static_only(self):
        self.assertEqual(self.payload['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('not runtime', self.payload['note'])

    def test_provenance_pins_original_bytes(self):
        prov = self.payload['provenance']
        self.assertEqual(prov['xapk_sha256'],
                         'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e')
        self.assertEqual(prov['libil2cpp_sha256'],
                         '9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99')
        self.assertEqual(prov['methods'], 540)
        self.assertEqual(prov['classes'], 70)

    def test_every_declared_source_sha_matches_file(self):
        for entry in self.payload['provenance']['sources']:
            digest = hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, entry['sha256'], entry['path'])

    def test_artifact_is_reproducible_from_pinned_sources(self):
        rebuilt = meta_rewards.build()
        self.assertEqual(rebuilt, self.payload)

    # -- metadata usage slots -------------------------------------------
    def test_metadata_usage_counts(self):
        summary = self.payload['metadata_usage']['summary']
        self.assertEqual(summary['slots'], 3447)
        self.assertEqual(summary['string_literals'], 551)
        self.assertEqual(summary['by_kind']['5'], summary['string_literals'])
        self.assertEqual(summary['unresolved'], 3447 - 551)

    def test_every_string_literal_slot_has_text(self):
        rows = [r for r in self.payload['metadata_usage']['rows'] if r['token_kind'] == 5]
        self.assertEqual(len(rows), 551)
        self.assertTrue(all(isinstance(r['string'], str) for r in rows))
        # 8 slots point at genuine empty literals; the rest carry text.
        self.assertEqual(sum(1 for r in rows if r['string']), 543)

    # -- InitializeArray tokens -----------------------------------------
    def test_initialize_array_all_resolved(self):
        summary = self.payload['initialize_arrays']['summary']
        self.assertEqual(summary['total'], 15)
        self.assertEqual(summary['ok'], 15)
        self.assertEqual(summary['status'], {'ok': 15})

    def test_initialize_array_blob_sizes_fit_declared_length(self):
        for methods in self.payload['initialize_arrays']['by_class'].values():
            for method in methods:
                for row in method['arrays']:
                    self.assertEqual(len(row['ints']), row['declared_length'])
                    self.assertGreaterEqual(row['declared_bytes'], 4 * row['declared_length'])
                    self.assertLess(row['default_bytes'], 4 * row['declared_length'] + 16)

    def test_initialize_array_tokens_are_field_usage(self):
        tokens = []
        for methods in self.payload['initialize_arrays']['by_class'].values():
            for method in methods:
                tokens.extend(method['arrays'])
        self.assertTrue(all(t['token_kind'] == 4 for t in tokens))
        self.assertTrue(all(t['token_source'] % 2 == 1 for t in tokens))

    # -- #29 unlocks now closed -----------------------------------------
    def test_arena_config_rank_split_string(self):
        value = self.payload['unlocks']['arena_config']['RankSplit']['value']['text']
        self.assertEqual(value, '20-45;15-45;15-45;10-45;10-45;10-45;10-45;10-45;10-45;10-45')

    def test_arena_config_season_time_string(self):
        value = self.payload['unlocks']['arena_config']['SeasonTime']['value']['text']
        self.assertEqual(value, '1440;2880;4320;7200;10080;11520;12960;14400;15840;17280')

    def test_arena_config_room_limits(self):
        config = self.payload['unlocks']['arena_config']
        self.assertEqual(config['MaxRoomCount']['value'], 50)
        self.assertEqual(config['MinRoomCount']['value'], 10)
        self.assertEqual(config['SummaryTime']['value'], 60.0)
        self.assertFalse(config['IsOpen']['value'])

    def test_arena_manager_rewards_are_ten_strings(self):
        values = self.payload['unlocks']['arena_manager_rewards']['value']['values']
        self.assertEqual(len(values), 10)
        self.assertTrue(all(v['kind'] == 'string' and v['text'].startswith('#1[Medal:') for v in values))

    def test_arena_reward_extremes(self):
        values = [v['text'] for v in self.payload['unlocks']['arena_manager_rewards']['value']['values']]
        self.assertIn('#46-50[Medal:60,Gems:20]', values[0])
        self.assertIn('#1[Medal:5000,Gems:1000]', values[9])
        self.assertIn('#46-50[Medal:440,Gems:80]', values[9])

    def test_max_rank_stars_lengths(self):
        items = self.payload['unlocks']['pvp_manager_max_rank_stars']['value']['items']
        self.assertEqual([i['length'] for i in items], [3, 3, 4, 4, 5, 5, 5, 5, 5, 5])

    def test_max_rank_stars_values(self):
        items = self.payload['unlocks']['pvp_manager_max_rank_stars']['value']['items']
        self.assertEqual([i['values'] for i in items],
                         [[3, 3, 3], [4, 4, 4], [4, 4, 4, 4], [5, 5, 5, 5]] + [[5] * 5] * 6)

    # -- meta statics ----------------------------------------------------
    def test_game_datas_sentinels(self):
        fields = self.payload['initializer_statics']['GameDatas']['fields']
        self.assertEqual(fields['timeRewards']['value'], 90000000)
        self.assertEqual(fields['vipPoints']['value'], -1)
        self.assertEqual(fields['isAdmin']['value'], 0)

    def test_game_datas_percent_graphics_are_floats(self):
        value = self.payload['initializer_statics']['GameDatas']['fields']['percentGraphics']['value']
        self.assertEqual(value['element_type'], 'float32')
        for got, want in zip(value['values'], (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)):
            self.assertAlmostEqual(got, want, places=5)

    def test_time_free_reward_pack(self):
        fields = self.payload['initializer_statics']['TimeFreeRewardPack']['fields']
        self.assertEqual(fields['keySysTime']['value']['text'], 'TimeFreePacks')
        self.assertEqual(fields['timeAds']['value'], 43200.0)
        self.assertEqual(fields['timeUpdate']['value'], 1)

    def test_popup_watch_videos(self):
        fields = self.payload['initializer_statics']['Popup_WatchVideos']['fields']
        self.assertEqual(fields['NumberSlots']['value'], 6)
        self.assertEqual(fields['coinXValue']['value'], 150)
        self.assertEqual(fields['gemBonus']['value'], 20)
        self.assertEqual(fields['duration']['value'], 900.0)

    # -- shop packs ------------------------------------------------------
    def test_pack_table_sizes(self):
        packs = self.payload['shop_packs']
        self.assertEqual(len(packs['PackDaily']), 3)
        self.assertEqual(len(packs['PackWeekly']), 5)
        self.assertEqual(len(packs['PackDailyVideo']), 3)
        self.assertEqual(len(packs['PackSpec']), 3)
        self.assertEqual(len(packs['BoxRewardsRoot']), 3)

    def test_weekly_pack_first_row(self):
        row = self.payload['shop_packs']['PackWeekly'][0]
        self.assertEqual({k: v for k, v in row.items() if v},
                         {'Gcoins': 25000, 'Gems': 300, 'Key1': 25, 'multipleBonus': 4})

    def test_video_pack_third_row(self):
        row = self.payload['shop_packs']['PackDailyVideo'][2]
        self.assertEqual({k: v for k, v in row.items() if v},
                         {'Gcoins': 10000, 'Gems': 25, 'PlayerCards': 3, 'DroneCards': 3})

    def test_free_gift_and_premium_daily(self):
        free = {k: v for k, v in self.payload['shop_packs']['FreeGift'].items() if v}
        premium = {k: v for k, v in self.payload['shop_packs']['PremiumDailyRewards'].items() if v}
        self.assertEqual(free, {'Gems': 500, 'Energy': 1000})
        self.assertEqual(premium, {'Gems': 300, 'DroneCards': 20, 'PlayerCards': 10})

    def test_season_pass_shop_rows(self):
        table = self.payload['event_season_pass']
        self.assertEqual(table['count'], 20)
        self.assertEqual(table['rows'][0], {'pack': {'Gcoins': 1}, 'number': 1000,
                                            'price': 10, 'stock': 100})
        self.assertEqual(table['rows'][19], {'pack': {'DeviceA': 1}, 'number': 1,
                                             'price': 2000, 'stock': 5})

    def test_season_pass_prices_are_positive(self):
        rows = self.payload['event_season_pass']['rows']
        self.assertTrue(all(row['price'] > 0 and row['stock'] > 0 for row in rows))

    # -- honesty ---------------------------------------------------------
    def test_gaps_name_the_missing_symbol(self):
        items = [gap['item'] for gap in self.payload['gaps']]
        self.assertIn('MAX_LEVEL_BP', items)
        self.assertTrue(any('MODEL_NOT_MEASURED runtime' in gap['note']
                            for gap in self.payload['gaps']))

    def test_no_unresolved_reward_claim(self):
        for row in self.payload['initialize_arrays']['by_class'].values():
            for method in row:
                for array in method['arrays']:
                    self.assertNotEqual(array['status'], 'blob_length_mismatch')


if __name__ == '__main__':
    unittest.main()
