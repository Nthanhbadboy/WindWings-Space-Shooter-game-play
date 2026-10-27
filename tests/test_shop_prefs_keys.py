"""Contracts for report 162: the shop's per-cell state lives in PlayerPrefs.

`GetIdItem`/`GetStockItem`/`SetStockItem` are one-line `PlayerPreferences.GetInt/SetInt`
calls keyed by `<cell> + index.ToString()`, and `ResetShop` writes both keys for every cell
of the three bands — id = catalogue − 10001 (player), catalogue (drone), cell id
(resource), stock = 0. Everything here is static.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import shop_prefs_keys as PK  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_shop_prefs_keys.json.gz'
PIN_BYTES = 4384
PIN_SHA = '6c0fbe7397dbb187f959a95d50b5abf29da9aa46b1b7f23e268ec3517bbf7886'

CLICK = {'Arena_Shop': 22733228, 'PVP_Shop': 19942120}
RESET = {'Arena_Shop': 22728328, 'PVP_Shop': 19937384}
ACCESSORS = {
    'Arena_Shop': {'get_id': (22732732, 164), 'get_stock': (22732896, 164),
                   'set_stock': (22733060, 168)},
    'PVP_Shop': {'get_id': (19941788, 164), 'get_stock': (19889588, 164),
                 'set_stock': (19941952, 168)},
}
WRITES = {'Arena_Shop': [22729192, 22729240, 22729804, 22729852, 22729972, 22730020],
          'PVP_Shop': [19938248, 19938296, 19938860, 19938908, 19939028, 19939076]}
API = {20912668: ('PlayerPreferences', 'GetInt(string key, int valueDefault)'),
       20912644: ('PlayerPreferences', 'SetInt(string key, int value)'),
       34616120: ('Int32', 'override string ToString()'),
       33439876: ('String', 'Concat(string str0, string str1)')}


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(PK.build(), sort_keys=True, separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', json.dumps(blob['open_items']))

    def test_every_check_passed(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 22)
        self.assertTrue(all(row['passed'] for row in checks), checks)


class Cells(unittest.TestCase):
    def test_four_cells_match_153(self):
        self.assertEqual(payload()['cells'],
                         {'ARENA_ID': 0x2AED090, 'ARENA_STOCK': 0x2AED088,
                          'PVP_ID': 0x2AE1018, 'PVP_STOCK': 0x2AE0D40})

    def test_id_cell_is_read_by_two_methods_per_shop(self):
        touches = payload()['touches']
        self.assertEqual(sorted({row['method_rva'] for row in touches['ARENA_ID']}),
                         [22728328, 22732732])
        self.assertEqual(sorted({row['method_rva'] for row in touches['PVP_ID']}),
                         [19937384, 19941788])

    def test_stock_cell_is_read_by_three_methods_per_shop(self):
        touches = payload()['touches']
        self.assertEqual(sorted({row['method_rva'] for row in touches['ARENA_STOCK']}),
                         [22728328, 22732896, 22733060])
        self.assertEqual(sorted({row['method_rva'] for row in touches['PVP_STOCK']}),
                         [19889588, 19937384, 19941952])

    def test_every_touch_is_inside_the_owning_shop_class(self):
        for name, rows in payload()['touches'].items():
            klass = 'Arena_Shop' if name.startswith('ARENA') else 'PVP_Shop'
            self.assertTrue(all(row['class_name'] == klass for row in rows), name)


class Accessors(unittest.TestCase):
    def test_three_accessors_per_shop_with_pinned_sizes(self):
        shops = payload()['shops']
        for klass, want in ACCESSORS.items():
            for role, (rva, size) in want.items():
                self.assertEqual(shops[klass][role]['method_rva'], rva)
                self.assertEqual(shops[klass][role]['size'], size)

    def test_every_accessor_calls_tostring_concat_then_preferences(self):
        for shop in payload()['shops'].values():
            for row in shop.values():
                self.assertEqual(row['callees'], ['Int32', 'String', 'PlayerPreferences'])

    def test_get_id_reads_the_id_cell_only(self):
        for shop in payload()['shops'].values():
            self.assertEqual(shop['get_id']['cell'].split('_')[-1], 'ID')
            self.assertEqual(len(shop['get_id']['cell_reads']), 2)

    def test_get_stock_and_set_stock_read_the_stock_cell_only(self):
        for shop in payload()['shops'].values():
            for role in ('get_stock', 'set_stock'):
                self.assertEqual(shop[role]['cell'].split('_')[-1], 'STOCK')

    def test_reads_default_to_zero(self):
        for shop in payload()['shops'].values():
            self.assertEqual(shop['get_id']['default'], 0)
            self.assertEqual(shop['get_stock']['default'], 0)

    def test_set_stock_writes_its_value_argument(self):
        for shop in payload()['shops'].values():
            self.assertEqual(shop['set_stock']['value_register'], 'w19')


class ResetShop(unittest.TestCase):
    def test_six_set_int_sites_per_shop(self):
        for klass, sites in WRITES.items():
            reset = payload()['reset_shop'][klass]
            self.assertEqual([row['call_rva'] for row in reset['writes']], sites)
            self.assertEqual(reset['set_int_sites'], 6)

    def test_each_band_writes_the_id_key_then_the_stock_key(self):
        for reset in payload()['reset_shop'].values():
            self.assertEqual([row['key_cell'] for row in reset['writes']],
                             ['ARENA_ID' if reset['class_name'] == 'Arena_Shop' else 'PVP_ID',
                              'ARENA_STOCK' if reset['class_name'] == 'Arena_Shop' else 'PVP_STOCK'] * 3)

    def test_band_order_is_player_drone_resource(self):
        for rows in payload()['bands'].values():
            self.assertEqual([row['band'] for row in rows],
                             ['player', 'drone', 'resource'])
            self.assertEqual([row['key_index_base'] for row in rows], [100, 200, 300])

    def test_player_band_carries_the_minus_10001(self):
        for rows in payload()['bands'].values():
            player = rows[0]
            self.assertEqual(player['id_value_op'], 'w1, w21, w29')
            self.assertEqual(player['id_value_const'], -10001)
            self.assertIn('add w28', player['key_index_op'])

    def test_drone_band_stores_the_catalogue_value(self):
        for rows in payload()['bands'].values():
            drone = rows[1]
            self.assertEqual(drone['id_value_op'], 'w1, w21')
            self.assertIsNone(drone['id_value_const'])
            self.assertIn('add w27', drone['key_index_op'])

    def test_resource_band_stores_the_cell_id(self):
        for rows in payload()['bands'].values():
            resource = rows[2]
            self.assertEqual(resource['id_value_op'], 'w1, w20')
            self.assertIn('add w20', resource['key_index_op'])

    def test_every_stock_write_is_zero(self):
        for rows in payload()['bands'].values():
            for row in rows:
                self.assertEqual(row['stock_value_op'], 'w1, wzr')


class Api(unittest.TestCase):
    def test_the_four_named_callees(self):
        api = payload()['api']
        for rva, (klass, fragment) in API.items():
            row = next(row for row in (api['get_int'], api['set_int'],
                                       api['to_string'], api['concat'])
                       if row['rva'] == rva)
            self.assertEqual(row['class_name'], klass)
            self.assertIn(fragment, row['signature'])

    def test_no_set_id_item_exists_in_the_metadata(self):
        self.assertEqual(payload()['api']['set_id_item_in_metadata'], [])

    def test_player_preferences_has_21_methods(self):
        self.assertEqual(len(payload()['api']['playerpreferences_methods']), 21)

    def test_the_typed_accessors_are_present(self):
        signatures = payload()['api']['playerpreferences_methods']
        for fragment in ('GetInt', 'SetInt', 'GetString', 'SetString',
                         'GetFloat', 'SetFloat', 'DeleteKey', 'DeleteAll'):
            self.assertTrue(any(fragment in row for row in signatures), fragment)


class PreviousReports(unittest.TestCase):
    def test_153_cells_and_keys_are_reused_not_recomputed(self):
        previous = PK.load(PK.PREV153)
        for klass in ('Arena_Shop', 'PVP_Shop'):
            keys = previous['shops'][klass]['keys']
            self.assertEqual(keys[0]['role'], 'slot id')
            self.assertEqual(keys[1]['role'], 'slot stock')

    def test_160_still_reports_four_rows(self):
        previous = PK.load(PK.PREV160)
        self.assertTrue(all(len(row['rows']) == 4 for row in previous['bands'].values()))

    def test_161_index_is_the_corrected_one(self):
        previous = PK.load(PK.PREV161)
        self.assertEqual(len(previous['checks']), 24)
        self.assertEqual(previous['totals']['classes'], 10906)


if __name__ == '__main__':
    unittest.main()
