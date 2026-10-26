"""Contracts for the pack-index / energy-exchange decode (#30-followup). STATIC only."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/verify'))
import pack_index  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_pack_index.json.gz'

FIELDS = ['Gcoins', 'Gems', 'Item0', 'Item1', 'Item2', 'Item3', 'Overdrive', 'Energy',
          'DeviceC', 'DeviceB', 'DeviceA', 'DeviceS', 'DeviceSS', 'DroneExp', 'DroneCards',
          'PlayerCards', 'Key0', 'Key1', 'Key2', 'WingCoins', 'VipPoint', 'TimeRewards',
          'ArenaMedal', 'PvPMedal', 'TryDrone', 'TryShip', 'Premium']


class PackIndexArtifact(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(gzip.decompress(ARTIFACT.read_bytes()))

    # -- provenance ------------------------------------------------------
    def test_static_only(self):
        self.assertEqual(self.payload['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('Static decode only', self.payload['note'])

    def test_sources_match_files(self):
        for entry in self.payload['provenance']['sources']:
            digest = hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, entry['sha256'], entry['path'])

    def test_30_raw_pin_untouched(self):
        # The #30 artifact cites this SHA; this follow-up must not regenerate it.
        pinned = next(s for s in self.payload['provenance']['sources']
                      if s['path'].endswith('meta-rewards-535b0541/native.json.gz'))
        self.assertEqual(pinned['sha256'],
                         'e91a8c7664666f349042d78994b7ecd53ae8e67e243c4bf3326f8cab232d4937')

    def test_artifact_is_reproducible(self):
        self.assertEqual(pack_index.build(), self.payload)

    # -- index table -----------------------------------------------------
    def test_index_table_is_the_27_int_fields(self):
        entries = self.payload['value_index']['entries']
        self.assertEqual([row['field'] for row in entries], FIELDS)
        self.assertEqual([row['index'] for row in entries], list(range(27)))
        self.assertEqual([row['offset'] for row in entries],
                         [hex(0x10 + 4 * i) for i in range(27)])

    def test_multiple_bonus_is_not_indexable(self):
        self.assertEqual(self.payload['value_index']['ignored_fields'], ['multipleBonus'])
        self.assertEqual(self.payload['value_index']['max_index'], 26)

    def test_out_of_range_returns_zero(self):
        self.assertIn('returns 0', self.payload['value_index']['out_of_range']['rule'])

    def test_jump_table_is_pinned_and_linear(self):
        table = self.payload['value_index']['jump_table']
        self.assertEqual(table['length'], 27)
        self.assertEqual(len(bytes.fromhex(table['hex'])), 27)
        self.assertEqual(table['entries'], [0, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 38,
                                            41, 44, 47, 50, 53, 56, 59, 62, 65, 68, 71, 74, 77, 80])
        for row in self.payload['value_index']['entries']:
            self.assertEqual(row['target_rva'], 0x1344280 + 4 * row['jump_entry'])

    # -- rules -----------------------------------------------------------
    def test_index_rewards_drops_zeros(self):
        rule = self.payload['rules']['get_list_index_rewards']
        self.assertIn('value >= 1', rule['rule'])
        self.assertEqual(rule['rva'], 20199416)

    def test_random_rewards_double_weights_drone_exp(self):
        rule = self.payload['rules']['get_list_index_random_rewards']
        self.assertEqual(rule['weight_bias']['index'], 13)
        self.assertEqual(rule['weight_bias']['field'], 'DroneExp')
        self.assertEqual(rule['weight_bias']['condition'], 'typeBox == 0')
        self.assertIn('with replacement', rule['duplicates'])

    def test_random_uses_unity_random_range(self):
        self.assertEqual(self.payload['call_targets']['random_range']['name'],
                         'UnityEngine.Random.Range(int,int)')
        self.assertEqual(self.payload['call_targets']['random_range']['rva'], 0x277D2C0)

    def test_add_packs_skips_multiple_bonus(self):
        rule = self.payload['rules']['add_packs']
        self.assertEqual(rule['excluded'], ['multipleBonus'])
        self.assertEqual(rule['covered'], '0x10-0x78')

    def test_box_rewards_gated_on_pro_and_mutates(self):
        rule = self.payload['rules']['box_rewards']
        self.assertIn('IsProVersion', rule['rule'])
        self.assertTrue(rule['mutates_static'])
        self.assertIn('untouched', rule['non_pro'])

    def test_login_variant_selection(self):
        rule = self.payload['rules']['login_rewards']['rule']
        self.assertIn('get_ResetDailyGiftCount() == 0', rule)
        self.assertIn('allLogInRewardsRoot', rule)

    # -- energy economy --------------------------------------------------
    def test_exchange_formula(self):
        exchange = self.payload['energy_economy']['exchange']
        self.assertEqual(exchange['numerator'], 30)
        self.assertEqual(exchange['denominator'], 100)
        self.assertEqual(exchange['non_pro_value'], -1)
        self.assertEqual(exchange['rva'], 19432384)

    def test_energy_constants(self):
        economy = self.payload['energy_economy']
        self.assertEqual(economy['cost_buy_energy']['value'], 30)
        self.assertEqual(economy['value_buy_energy']['value'], 50)
        self.assertEqual(economy['value_free_energy']['value'], 30)

    def test_exchange_samples(self):
        def gain(energy):
            return (energy * 30) // 100
        self.assertEqual([gain(e) for e in (0, 1, 3, 20, 50, 100)], [0, 0, 0, 6, 15, 30])
        boxes = self.payload['samples']['boxes_energy_conversion']
        self.assertEqual([row['gems_gained'] for row in boxes], [6, 0, 0])

    def test_login_first_pack_carries_50_energy(self):
        first = self.payload['samples']['login_root_energy_conversion'][0]
        self.assertEqual(first['Energy'], 50)
        self.assertEqual(first['gems_gained'], 15)
        self.assertEqual(first['Gems_after'], first['Gems_before'] + 15)

    # -- samples ---------------------------------------------------------
    def test_weekly_first_pack_indices(self):
        row = self.payload['samples']['index_lists']['PackWeekly'][0]
        self.assertEqual(row['indices'], [0, 1, 17])
        self.assertEqual(row['nonzero'], ['Gcoins', 'Gems', 'Key1'])

    def test_video_third_pack_indices(self):
        row = self.payload['samples']['index_lists']['PackDailyVideo'][2]
        self.assertEqual(row['indices'], [0, 1, 14, 15])

    def test_every_sample_index_maps_to_nonzero_field(self):
        entries = {row['index']: row['field'] for row in self.payload['value_index']['entries']}
        for table, rows in self.payload['samples']['index_lists'].items():
            for row in rows:
                self.assertEqual([entries[i] for i in row['indices']], row['nonzero'], table)
                self.assertEqual(row['indices'], sorted(set(row['indices'])), table)

    # -- honesty ---------------------------------------------------------
    def test_gaps_are_named(self):
        items = [gap['item'] for gap in self.payload['not_decoded']]
        self.assertIn('typeBox runtime value', items)
        self.assertIn('actual random draws', items)
        draws = next(g for g in self.payload['not_decoded'] if g['item'] == 'actual random draws')
        self.assertIn('runtime', draws['blocking'])


if __name__ == '__main__':
    unittest.main()
