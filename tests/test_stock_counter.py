"""Contracts for report 156: the shop key is a counter of units sold, not of units left."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import stock_counter  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_stock_counter.json.gz'
PIN_BYTES = 3019
PIN_SHA = 'df6ee0ebbdd61e769d3cf4257ee6648aaaf3e80f069ac2654e721096b128059b'
ACCESSORS = {'Arena_Shop': (22732896, 22733060, 418, 'ARENA_SHOP_ITEM_STOCK'),
             'PVP_Shop': (19889588, 19941952, 912, 'PVP_SHOP_ITEM_STOCK')}


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(stock_counter.build(), sort_keys=True, separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', json.dumps(blob['open_items']))


class Provenance(unittest.TestCase):
    def test_four_sources(self):
        rows = payload()['provenance']['sources']
        self.assertEqual(len(rows), 4)

    def test_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])

    def test_previous_reports_are_153_and_154(self):
        paths = [row['path'] for row in payload()['provenance']['sources']]
        self.assertIn('datas/l2_535b0541_shop_stock_layout.json.gz', paths)
        self.assertIn('datas/l2_535b0541_exchange_cost.json.gz', paths)


class Shops(unittest.TestCase):
    def test_accessors(self):
        for klass, (getter, setter, typedef, key) in ACCESSORS.items():
            row = payload()['shops'][klass]
            self.assertEqual((row['get']['rva'], row['set']['rva'], row['typedef']),
                             (getter, setter, typedef))
            self.assertEqual(row['key']['name'], key)

    def test_get_and_set_sizes(self):
        for klass, (_, _, _, _) in ACCESSORS.items():
            row = payload()['shops'][klass]
            self.assertEqual((row['get']['size'], row['set']['size']), (164, 168))

    def test_key_cells(self):
        self.assertEqual(payload()['shops']['Arena_Shop']['key']['cell_hex'], '0x2aed088')
        self.assertEqual(payload()['shops']['PVP_Shop']['key']['cell_hex'], '0x2ae0d40')

    def test_reset_zeroes_three_bands(self):
        for row in payload()['shops'].values():
            self.assertEqual(row['reset']['bands'], [100, 200, 300])
            self.assertEqual(len(row['reset']['zero_writes']), 3)
            self.assertEqual(row['reset']['size'], 1752)


class Writers(unittest.TestCase):
    def test_six(self):
        self.assertEqual(len(payload()['writers']), 6)

    def test_three_per_shop(self):
        names = sorted(row['class_name'].split('.')[-1] for row in payload()['writers'])
        self.assertEqual(names, ['<>c__DisplayClass31_1'] * 2
                         + ['<>c__DisplayClass31_2'] * 2
                         + ['<>c__DisplayClass31_3'] * 2)

    def test_all_increment(self):
        for row in payload()['writers']:
            self.assertEqual(row['value_op'], 'add w2, w8, w21')
            self.assertEqual(row['direction'], 'increment')

    def test_call_rvas(self):
        self.assertEqual(sorted(row['call_rva'] for row in payload()['writers']),
                         [19945012, 19945912, 19947092, 22736116, 22772300, 22773480])


class Readers(unittest.TestCase):
    def test_eight_per_shop(self):
        self.assertEqual({klass: len(rows)
                          for klass, rows in payload()['readers'].items()},
                         {'Arena_Shop': 8, 'PVP_Shop': 8})

    def test_popup_reads_the_counter(self):
        for klass, rows in payload()['readers'].items():
            popup = [row['class_name'] for row in rows
                     if row['class_name'].startswith('Popup_')]
            self.assertEqual(len(popup), 1, klass)

    def test_three_buy_closures_re_read_for_the_text(self):
        for rows in payload()['readers'].values():
            closures = [row for row in rows if 'DisplayClass31' in row['class_name']]
            self.assertEqual(len(closures), 3)


class Snapshot(unittest.TestCase):
    def test_click_time_capture(self):
        for row in payload()['snapshot'].values():
            self.assertEqual(row['op'], 'str w0, [x21, #0x28]')
            self.assertEqual(row['field'], '0x28')

    def test_capture_follows_the_read(self):
        for row in payload()['snapshot'].values():
            self.assertLess(row['get_call_rva'], row['store_rva'])
            self.assertEqual(row['signature'],
                             'private void OnClickPlayerItem(Shop_Cell cell) { }')

    def test_closure_layout(self):
        rows = {row['offset']: row['first_read'] for row in payload()['closure_layout']}
        self.assertEqual(sorted(rows), ['0x10', '0x14', '0x18'])


class Ceilings(unittest.TestCase):
    def test_six_display_subtractions(self):
        rows = payload()['ceilings']
        self.assertEqual(len(rows), 6)
        for row in rows:
            self.assertEqual(row['max_stock_load']['op'], 'ldr w22, [x8, #0x98]')
            self.assertEqual(row['subtract']['op'], 'sub w8, w22, w0')

    def test_two_ceilings_differ(self):
        cross = payload()['cross_checks']
        self.assertTrue(cross['ceilings_differ'])
        self.assertIn('MaxStockCount', cross['slot_ceiling'])
        self.assertIn('EventRewards.stock', cross['popup_ceiling'])
        self.assertIn('no', cross['max_stock_writer'])

    def test_counter_semantics(self):
        self.assertIn('sold', payload()['cross_checks']['counter'])
        self.assertIn('ResetShop', payload()['cross_checks']['reset'])

    def test_band_constants(self):
        self.assertEqual([row['op'] for row in payload()['band_constants']],
                         ['cmp w8, #0xc7', 'cmp w8, #0x12b'])


class Findings(unittest.TestCase):
    def test_all_checks_pass(self):
        rows = payload()['checks']
        self.assertEqual(len(rows), 13)
        self.assertTrue(all(row['passed'] for row in rows), rows)

    def test_three_confirmations(self):
        rows = payload()['confirmations']
        self.assertEqual(len(rows), 3)
        self.assertIn('155', rows[0]['item'])

    def test_three_open_items(self):
        rows = payload()['open_items']
        self.assertEqual(len(rows), 3)
        self.assertIn('MaxStockCount', rows[0]['item'])
        self.assertIn('MODEL_NOT_MEASURED runtime', rows[1]['blocking'])


if __name__ == '__main__':
    unittest.main()
