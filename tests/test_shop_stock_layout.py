"""Contracts for report 153: the two arena shops — keys, bands, and the shuffle."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import shop_stock_layout  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_shop_stock_layout.json.gz'
PIN_BYTES = 4107
PIN_SHA = '792f25b76cc6aea9c8e29ded62a305227d320c05153f0cb731efdff8a29ce250'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(shop_stock_layout.build(), sort_keys=True,
                          separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_three_sources(self):
        self.assertEqual(len(payload()['provenance']['sources']), 3)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])


class Keys(unittest.TestCase):
    def test_pvp_keys(self):
        rows = payload()['shops']['PVP_Shop']['keys']
        self.assertEqual([row['name'] for row in rows],
                         ['PVP_SHOP_ITEM_ID', 'PVP_SHOP_ITEM_STOCK'])
        self.assertEqual([row['cell_hex'] for row in rows], ['0x2ae1018', '0x2ae0d40'])

    def test_arena_keys(self):
        rows = payload()['shops']['Arena_Shop']['keys']
        self.assertEqual([row['name'] for row in rows],
                         ['ARENA_SHOP_ITEM_ID', 'ARENA_SHOP_ITEM_STOCK'])
        self.assertEqual([row['cell_hex'] for row in rows], ['0x2aed090', '0x2aed088'])

    def test_every_key_is_read_through_a_getter(self):
        for shop in payload()['shops'].values():
            self.assertTrue(all(row['read_at'] for row in shop['keys']))

    def test_getters_default_to_zero(self):
        for shop in payload()['shops'].values():
            self.assertEqual(shop['getters']['get_id']['default'], 0)
            self.assertEqual(shop['getters']['get_stock']['default'], 0)

    def test_named_getters(self):
        pvp = payload()['shops']['PVP_Shop']['getters']
        self.assertEqual((pvp['get_id']['rva'], pvp['get_stock']['rva'],
                          pvp['set_stock']['rva']),
                         (19941788, 19889588, 19941952))


class Bands(unittest.TestCase):
    def test_three_bands_in_both_shops(self):
        for klass in ('PVP_Shop', 'Arena_Shop'):
            rows = payload()['bands'][klass]['rows']
            self.assertEqual([row['base'] for row in rows], [100, 200, 300])

    def test_bands_map_to_the_cell_arrays(self):
        rows = payload()['bands']['PVP_Shop']['rows']
        self.assertEqual([row['array'] for row in rows],
                         ['listItemPlayers', 'listItemDrones', 'listItemResources'])
        self.assertEqual([row['instance_offset'] for row in rows],
                         ['0x68', '0x70', '0x78'])

    def test_value_rule_per_band(self):
        writes = payload()['shops']['PVP_Shop']['reset']['writes']
        ids = [row for row in writes if row['value_rule'] != '0 (literal)']
        self.assertEqual([row['value_rule'] for row in ids],
                         ['id - 10001', 'item id', 'index + 300'])
        stocks = [row for row in writes if row['value_rule'] == '0 (literal)']
        self.assertEqual([row['band'] for row in stocks], [100, 200, 300])

    def test_both_shops_subtract_the_same_delta(self):
        for klass in ('PVP_Shop', 'Arena_Shop'):
            self.assertEqual(payload()['bands'][klass]['delta_value'], 10001)
            self.assertEqual(payload()['bands'][klass]['player_id_delta'],
                             'w29, #-0x2711')

    def test_six_writes_each(self):
        for shop in payload()['shops'].values():
            self.assertEqual(len(shop['reset']['writes']), 6)


class Catalogue(unittest.TestCase):
    def test_pool_is_the_players_own_items(self):
        rows = payload()['catalogue']['helpers']
        pool = next(row for row in rows if row['role'] == 'candidate pool')
        self.assertIn('GetListAllIdPlayerActived', pool['signature'])

    def test_pick_is_random_range(self):
        rows = payload()['catalogue']['helpers']
        pick = next(row for row in rows if row['role'] == 'pick')
        self.assertEqual(pick['class_name'], 'Random')
        self.assertIn('Range(', pick['signature'])

    def test_shuffle_uses_remove_at(self):
        rows = payload()['catalogue']['helpers']
        remove = next(row for row in rows if row['role'] == 'remove')
        self.assertIn('RemoveAt', remove['signature'])
        self.assertEqual(remove['rva'], 28926656)

    def test_order_is_recorded(self):
        self.assertEqual(len(payload()['catalogue']['order']), 6)


class Buy(unittest.TestCase):
    def test_round_trip(self):
        facts = {row['rva']: row['op'] for row in payload()['buy']['facts']}
        self.assertEqual(facts[19944916], 'mov w8, #0x2711')
        self.assertEqual(facts[19944920], 'add w22, w22, w8')

    def test_pays_in_cards(self):
        calls = payload()['buy']['calls']
        self.assertEqual(sorted(row['signature'].split('(')[0].split()[-1]
                                for row in calls),
                         ['GetPlayerCards', 'SetPlayerCards'])

    def test_madd_makes_the_price(self):
        facts = {row['rva']: row['op'] for row in payload()['buy']['facts']}
        self.assertEqual(facts[19944944], 'madd w1, w8, w21, w0')


class Twins(unittest.TestCase):
    def test_thirty_identical_fields(self):
        blob = payload()['twins']
        self.assertEqual(blob['fields'], 30)
        self.assertEqual([row['name'] for row in blob['rows']],
                         shop_stock_layout.FIELD_NAMES)

    def test_only_the_popup_type_differs(self):
        self.assertEqual(payload()['twins']['type_differences'],
                         [{'field': 'popupExchange',
                           'arena': 'Popup_ArenaShopExchange',
                           'pvp': 'Popup_PVPShopExchange'}])

    def test_one_method_size_delta(self):
        differing = [row for row in payload()['twins']['methods'] if not row['same_size']]
        self.assertEqual(len(differing), 1)
        self.assertIn('OnClickPlayerItem', differing[0]['signature'])
        self.assertEqual(differing[0]['delta'], -4)

    def test_arrays_are_serialized(self):
        rows = {row['name']: row for row in payload()['twins']['rows']}
        for name in ('listItemPlayers', 'listItemDrones', 'listItemResources'):
            self.assertTrue(rows[name]['serialized'], name)


class Findings(unittest.TestCase):
    def test_all_checks_pass(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 15)
        self.assertTrue(all(row['passed'] for row in checks), checks)

    def test_three_confirmations(self):
        self.assertEqual(len(payload()['confirmations']), 3)

    def test_three_open_items(self):
        rows = payload()['open_items']
        self.assertEqual(len(rows), 3)
        self.assertIn('MODEL_NOT_MEASURED', rows[0]['blocking'])
        self.assertIn('+0x98', rows[1]['item'])

    def test_stock_cap_has_reads_but_no_writes(self):
        blob = payload()['stock_cap']
        self.assertEqual(blob['writes'], [])
        self.assertTrue(blob['shop_reads'])

    def test_five_rows_per_family(self):
        rows = payload()['resources']['allocations']
        self.assertEqual([row['length'] for row in rows], [5, 5, 5])

    def test_rvas_are_integers(self):
        self.assertIsInstance(payload()['shops']['PVP_Shop']['reset']['rva'], int)
        self.assertIsInstance(payload()['buy']['method']['rva'], int)


if __name__ == '__main__':
    unittest.main()
