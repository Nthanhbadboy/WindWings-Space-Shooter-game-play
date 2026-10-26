"""Contracts for report 155: the medal wallet — one static, clamped at zero, 30 callers."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import medal_flow  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_medal_flow.json.gz'
PIN_BYTES = 5086
PIN_SHA = 'fab987d2f939e00a3ad2d36b5aea474acdabcedbabcbc136c3f538dcd730d393'
WALLETS = {'ArenaMedal': ('arenaMedal', '0x9c', 20084804, 20085004),
           'PvPMedal': ('pvpMedal', '0xa0', 20085132, 20085332)}


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(medal_flow.build(), sort_keys=True, separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', json.dumps(blob['open_items']))


class Provenance(unittest.TestCase):
    def test_eleven_sources(self):
        rows = payload()['provenance']
        self.assertEqual(rows['slices'], 8)
        self.assertEqual(len(rows['sources']), 11)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])

    def test_previous_report_is_154(self):
        paths = [row['path'] for row in payload()['provenance']['sources']]
        self.assertIn('datas/l2_535b0541_exchange_cost.json.gz', paths)


class Declared(unittest.TestCase):
    def test_the_two_statics(self):
        rows = payload()['declared']
        self.assertEqual({name: (row['field'], row['offset'])
                          for name, row in rows.items()},
                         {name: (want[0], want[1]) for name, want in WALLETS.items()})

    def test_both_are_private_static_int(self):
        for row in payload()['declared'].values():
            self.assertEqual(row['declared'], 'private static int ' + row['field'])


class Accessors(unittest.TestCase):
    def test_rvas(self):
        for name, (_, _, getter, setter) in WALLETS.items():
            row = payload()['accessors'][name]
            self.assertEqual((row['getter']['rva'], row['setter']['rva']),
                             (getter, setter))

    def test_getter_loads_its_own_offline_slot(self):
        for name, (_, offset, _, _) in WALLETS.items():
            row = payload()['accessors'][name]
            self.assertTrue(row['field_load']['op'].endswith('#%s]' % offset))
            self.assertTrue(row['cache_store']['op'].endswith('#%s]' % offset))

    def test_minus_one_is_the_sentinel(self):
        for row in payload()['accessors'].values():
            self.assertEqual(row['sentinel']['op'], 'cmn w9, #1')
            self.assertIn('never loaded', row['sentinel']['meaning'])

    def test_lazy_load_is_playerprefs_getint(self):
        for row in payload()['accessors'].values():
            self.assertEqual(row['lazy_load']['class_name'], 'PlayerPrefs')
            self.assertIn('GetInt', row['lazy_load']['signature'])

    def test_setter_clamps_at_zero(self):
        for row in payload()['accessors'].values():
            self.assertEqual(row['clamp']['op'], 'bic w19, w19, w19, asr #31')

    def test_persist_is_a_tail_call(self):
        for row in payload()['accessors'].values():
            self.assertEqual(row['persist']['rva'], row['persist']['rva'])
            self.assertIn('SetInt', row['persist']['signature'])
            self.assertIn('tail', row['persist']['note'])

    def test_keys_are_the_reported_names(self):
        for name, row in payload()['accessors'].items():
            self.assertEqual(row['key']['name'], name)
            self.assertIsInstance(row['key']['slot_va'], int)


class Cctor(unittest.TestCase):
    def test_both_seeded_to_minus_one(self):
        row = payload()['cctor']
        self.assertEqual((row['rva'], row['size']), (20085468, 244))
        self.assertEqual(row['pvp_medal']['value'], -1)
        self.assertEqual(row['arena_medal']['value'], -1)

    def test_arena_sentinel_rides_a_wide_store(self):
        row = payload()['cctor']
        self.assertEqual(row['arena_medal']['op'], 'str x22, [x8, #0x98]')
        self.assertIn('campaignPoints', row['note'])


class Counts(unittest.TestCase):
    def test_call_census(self):
        rows = payload()['counts']
        self.assertEqual((rows['raw_bl'], rows['calls'], rows['pairs'], rows['methods']),
                         (61, 53, 42, 30))

    def test_write_split(self):
        rows = payload()['counts']
        self.assertEqual((rows['writers'], rows['credit'], rows['deduct']), (12, 5, 7))

    def test_per_wallet(self):
        rows = payload()['counts']['per_wallet']
        self.assertEqual(rows['ArenaMedal'], {'pairs': 21, 'writes': 4})
        self.assertEqual(rows['PvPMedal'], {'pairs': 32, 'writes': 8})


class WhoWrites(unittest.TestCase):
    def test_six_shop_closures(self):
        rows = payload()['clusters']['shop_deduct']
        self.assertEqual(len(rows), 6)
        self.assertEqual(sorted({row['class_name'].split('.')[0] for row in rows}),
                         ['Arena_Shop', 'PVP_Shop'])
        self.assertTrue(all(row['op'].startswith('msub w0, ') for row in rows))

    def test_one_deduction_outside_the_shops(self):
        rows = payload()['clusters']['deduct_not_shop']
        self.assertEqual([(row['class_name'], row['op']) for row in rows],
                         [('Board_RoomPVP', 'sub w0, w0, w8')])

    def test_five_credits(self):
        rows = payload()['clusters']['credits']
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(row['op'].startswith('add w0, ') for row in rows))
        self.assertEqual(len([row for row in rows if row['op'].endswith('lsl #1')]), 1)

    def test_exchange_popups_only_read(self):
        self.assertEqual(payload()['clusters']['exchange_writes'], [])
        self.assertEqual(len(payload()['clusters']['popup_reads']), 6)

    def test_write_methods(self):
        self.assertEqual(payload()['clusters']['write_methods'], 12)


class Callers(unittest.TestCase):
    def test_one_row_per_call(self):
        self.assertEqual(len(payload()['callers']), 53)

    def test_every_writer_names_its_value_source(self):
        for row in payload()['callers']:
            if row['api'] == 'set':
                self.assertIn(row['effect'], ('credit', 'deduct'))
                self.assertIsInstance(row['value_from']['rva'], int)
            else:
                self.assertEqual(row['effect'], 'read')

    def test_shop_rows_subtract_price_times_count(self):
        rows = [row for row in payload()['callers']
                if row['api'] == 'set' and 'Shop.' in row['class_name']]
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(row['value_from']['op'] == 'msub w0, w8, w21, w0'
                            for row in rows))

    def test_rvas_are_integers(self):
        for row in payload()['callers']:
            self.assertIsInstance(row['call_rva'], int)
            self.assertIsInstance(row['method_rva'], int)


class Lockstep(unittest.TestCase):
    def test_four_methods_touch_all_three_wallets(self):
        rows = sorted(row['class_name'] + ' ' + row['signature'].split('(')[0]
                      for row in payload()['companions']
                      if {'Coins', 'Gems'} <= {name for name, _ in row['others']})
        self.assertEqual(rows, ['Board_PVP private void CollectGifts',
                                'Board_PVP private void OnClickHunterCollect',
                                'Board_RoomPVP public void ShowPlayer',
                                'PVP_Endgame private void AddBetValues'])

    def test_bet_scalars(self):
        rows = payload()['bet_statics']
        self.assertEqual([(row['name'], row['offset']) for row in rows],
                         [('betCoinValues', '0x10'), ('betGemValues', '0x14'),
                          ('betMedalValues', '0x18')])

    def test_add_bet_values_doubles_the_bet(self):
        row = next(row for row in payload()['clusters']['credits']
                   if row['class_name'] == 'PVP_Endgame')
        self.assertEqual(row['op'], 'add w0, w0, w8, lsl #1')


class FieldWrites(unittest.TestCase):
    def test_ten_stores_and_all_but_two_are_accessors(self):
        rows = payload()['field_writes']
        self.assertEqual(len(rows), 10)
        self.assertEqual(len([row for row in rows if not row['accessor']]), 2)

    def test_the_two_others_are_the_cctor(self):
        rows = [row for row in payload()['field_writes'] if not row['accessor']]
        self.assertTrue(all(row['signature'] == 'private static void .cctor() { }'
                            for row in rows))


class Findings(unittest.TestCase):
    def test_all_checks_pass(self):
        rows = payload()['checks']
        self.assertEqual(len(rows), 16)
        self.assertTrue(all(row['passed'] for row in rows), rows)

    def test_three_confirmations(self):
        self.assertEqual(len(payload()['confirmations']), 3)
        self.assertIn('154', payload()['confirmations'][0]['item'])

    def test_three_open_items(self):
        rows = payload()['open_items']
        self.assertEqual(len(rows), 3)
        self.assertIn('SetPopup', rows[0]['blocking'])
        self.assertIn('0x2ADC840', rows[1]['item'])


if __name__ == '__main__':
    unittest.main()
