"""Contracts for report 157: the shop constructor seeds `MaxStockCount`, and the shop
resets every 12600 s of wall-clock time recorded under one PlayerPrefs key."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import shop_ctor_timer as SCT  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_shop_ctor_timer.json.gz'
PIN_BYTES = 3741
PIN_SHA = '30c5c67865a0c137e41f0d3dad64cee8dd55f1e89a36d70a293c7d0cc7f57fc8'
CTORS = {'Arena_Shop': 22735024, 'PVP_Shop': 19943896}
ONENABLE = {'Arena_Shop': 22727788, 'PVP_Shop': 19936844}
SEED = {'MaxStockCount': 10, 'ItemPlayerValue': 1, 'ItemPlayerCost': 50,
        'ItemDroneValue': 1, 'ItemDroneCost': 30}


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(SCT.build(), sort_keys=True, separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', json.dumps(blob['open_items']))


class ConstructorSeeds(unittest.TestCase):
    def test_both_constructors_are_216_bytes(self):
        ctors = payload()['constructors']
        self.assertEqual(sorted(ctors), ['Arena_Shop', 'PVP_Shop'])
        for klass, rva in CTORS.items():
            self.assertEqual(ctors[klass]['rva'], rva)
            self.assertEqual(ctors[klass]['size'], 216)

    def test_four_ints_come_from_one_literal(self):
        for row in payload()['constructors'].values():
            self.assertEqual(row['literal']['va'], 7838608)
            self.assertEqual(row['literal']['hex'], '0a000000010000003200000001000000')
            self.assertEqual(row['literal']['ints'], [10, 1, 50, 1])

    def test_one_wide_store_writes_the_block(self):
        for row in payload()['constructors'].values():
            self.assertEqual(row['load']['op'], 'ldr q0, [x8, #0xb90]')
            self.assertEqual(row['wide_store']['op'], 'stur q0, [x19, #0x98]')
            self.assertEqual(row['wide_store']['covers'],
                             ['0x98', '0x9c', '0xa0', '0xa4'])

    def test_drone_cost_is_a_separate_scalar_store(self):
        for row in payload()['constructors'].values():
            self.assertEqual(row['drone_cost']['value'], 30)
            self.assertEqual(row['drone_cost']['op'],
                             'mov w8, #0x1e ; str w8, [x19, #0xa8]')

    def test_two_int3_arrays_per_shop(self):
        for row in payload()['constructors'].values():
            self.assertEqual(row['arrays']['lengths'], [3, 3])
            self.assertEqual([entry['offset'] for entry in row['arrays']['fields']],
                             ['0xb0', '0xb8'])
            self.assertEqual(len(row['arrays']['initialize_array_calls']), 2)

    def test_constructor_seeds_match_the_declared_fields(self):
        shipped = payload()['shipped']
        for name, value in SEED.items():
            self.assertEqual(shipped[name]['value'], value, name)
            self.assertFalse(shipped[name]['serialized'], name)
        self.assertEqual(shipped['MaxStockCount']['offset'], '0x98')
        self.assertEqual(shipped['ItemDroneCost']['offset'], '0xa8')
        for name in ('ItemResourceValues', 'ItemResourceCost'):
            self.assertEqual(shipped[name]['length'], 3)
            self.assertFalse(shipped[name]['serialized'], name)

    def test_all_private_so_no_prefab_override_path(self):
        blob = payload()
        for name in list(SEED) + ['ItemResourceValues', 'ItemResourceCost']:
            self.assertIn('private', blob['shipped'][name]['declared'], name)
        self.assertTrue(blob['constructors']['Arena_Shop']['timer']['field'].startswith(
            'private double'))
        self.assertIn('prefab data cannot override it', blob['note'])


class StockCapCorrection(unittest.TestCase):
    def test_only_the_two_constructors_store_into_0x98(self):
        stores = payload()['stores']
        self.assertEqual([row['class_name'] for row in stores],
                         ['Arena_Shop', 'PVP_Shop'])
        self.assertEqual([row['op'] for row in stores], ['stur q0, [x19, #0x98]'] * 2)
        self.assertEqual([row['rva'] for row in stores], [22735140, 19944012])
        self.assertEqual([row['method_rva'] for row in stores], [22735024, 19943896])

    def test_correction_targets_153_and_explains_the_miss(self):
        correction = payload()['correction']
        self.assertEqual(correction['target'], 153)
        self.assertIn('stur', correction['why_wrong'])
        self.assertEqual(correction['evidence']['values'], [10, 1, 50, 1])

    def test_153_really_said_there_was_no_writer(self):
        previous = SCT.load(SCT.PREV153)
        self.assertIn('no store instruction targets +0x98',
                      previous['stock_cap']['rule'])

    def test_cap_is_a_constant_named_by_the_field(self):
        cap = payload()['shipped']['MaxStockCount']
        self.assertEqual(cap['value'], 10)
        self.assertEqual(cap['declared'], 'private int MaxStockCount')


class ResetTimer(unittest.TestCase):
    def test_time_to_reset_is_12600_seconds(self):
        for row in payload()['constructors'].values():
            self.assertEqual(row['timer']['seconds'], 12600.0)
            self.assertEqual(row['timer']['offset'], '0xf8')
            self.assertEqual(row['timer']['store_rva'] > row['wide_store']['rva'], True)
        self.assertEqual(12600.0 / 3600.0, 3.5)

    def test_each_shop_reads_its_own_key(self):
        clocks = payload()['timer']
        keys = {klass: row['key']['name'] for klass, row in clocks.items()}
        self.assertEqual(keys, {'Arena_Shop': 'TIME_TO_RESET_ARENA_SHOP',
                                'PVP_Shop': 'TIME_TO_RESET_PVP_SHOP'})
        self.assertEqual([row['key']['cell'] for row in clocks.values()],
                         [46031920, 46031928])

    def test_onenable_sizes_and_call_sites(self):
        clocks = payload()['timer']
        for klass, rva in ONENABLE.items():
            self.assertEqual(clocks[klass]['onenable']['rva'], rva)
            self.assertEqual(clocks[klass]['onenable']['size'], 540)
        self.assertEqual(clocks['Arena_Shop']['calls']['get_elapsed']['rva'], 22727884)
        self.assertEqual(clocks['PVP_Shop']['calls']['get_elapsed']['rva'], 19936940)

    def test_reset_targets_are_the_resetshop_methods(self):
        clocks = payload()['timer']
        self.assertEqual(clocks['Arena_Shop']['calls']['reset']['target'], 22728328)
        self.assertEqual(clocks['PVP_Shop']['calls']['reset']['target'], 19937384)
        self.assertEqual(clocks['Arena_Shop']['calls']['init']['target'], 22730080)
        self.assertEqual(clocks['PVP_Shop']['calls']['init']['target'], 19939136)

    def test_minus_one_sentinel_and_the_threshold_are_both_tested(self):
        for row in payload()['timer'].values():
            self.assertEqual(row['sentinel']['op'], 'fmov d1, #-1.00000000 ; fcmp d0, d1')
            self.assertEqual(row['threshold']['op'], 'ldr d1, [x19, #0xf8]')
            self.assertEqual(row['branches']['not_equal']['target'],
                             row['branches']['enough']['target'])

    def test_init_path_never_stamps_the_clock(self):
        for row in payload()['timer'].values():
            self.assertLess(row['init_skip']['rva'], row['calls']['reset']['rva'])
            self.assertGreater(row['init_skip']['target'], row['calls']['save_time']['rva'])

    def test_countdown_uses_a_thousands_format(self):
        for row in payload()['timer'].values():
            self.assertIn('###,###,##0',
                          [entry['value'] for entry in row['other_strings']])


class PopupFamily(unittest.TestCase):
    def test_three_popups_share_one_layout(self):
        family = payload()['popup_family']
        self.assertEqual([row['class_name'] for row in family],
                         ['Popup_ArenaShopExchange', 'Popup_PVPShopExchange',
                          'Popup_Exchange'])
        shapes = {tuple((f['name'], f['offset']) for f in row['fields'])
                  for row in family}
        self.assertEqual(len(shapes), 1)
        shape = shapes.pop()
        self.assertEqual(dict(shape)['rewards'], '0x60')
        self.assertEqual(dict(shape)['maxStock'], '0x5c')
        self.assertEqual(dict(shape)['count'], '0x58')
        self.assertEqual(dict(shape)['onExit'], '0x50')

    def test_the_third_copy_is_outside_every_slice(self):
        family = payload()['popup_family']
        third = family[2]
        self.assertEqual(third['typedef_index'], 693)
        self.assertEqual(third['methods_in_slices'], 0)
        self.assertLess(third['last_rva'], third['slice_bounds'][0])
        self.assertEqual([row['methods_in_slices'] for row in family[:2]],
                         [row['method_count'] for row in family[:2]])


class ChecksAndConfirmations(unittest.TestCase):
    def test_every_check_passed(self):
        rows = payload()['checks']
        self.assertEqual(len(rows), 18)
        self.assertTrue(all(row['passed'] for row in rows), [r for r in rows if not r['passed']])

    def test_confirmations_cover_149_153_and_156(self):
        blob = '\n'.join(entry['item'] for entry in payload()['confirmations'])
        for report in ('149', '153', '156'):
            self.assertIn(report, blob)

    def test_open_items_flag_runtime_only_questions(self):
        rows = payload()['open_items']
        self.assertEqual(len(rows), 4)
        self.assertIn('MODEL_NOT_MEASURED runtime', json.dumps(rows[0]))


if __name__ == '__main__':
    unittest.main()
