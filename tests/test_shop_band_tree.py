"""Contracts for report 160: `cell.id` selects the shop band, the band selects the row.

`OnClickPlayerItem` compares the raw cell id against 199 and 299, then builds one of four
`EventRewards` rows and stamps the price into a `Shop_Pack` currency slot that depends on
the band. Everything here is static: no runtime measurement is claimed.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import shop_band_tree as BT  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_shop_band_tree.json.gz'
PIN_BYTES = 4277
PIN_SHA = '17ff84e54fb29080987bd6a552a9d3faf3bb48bc18778f7dcef0e8f2f5aa90a0'

CLICK = {'Arena_Shop': 22733228, 'PVP_Shop': 19942120}
SETPOPUP = {'Arena_Shop': 22734600, 'PVP_Shop': 19943488}
ROWS = {'Arena_Shop': [22733792, 22734080, 22734380, 22734492],
        'PVP_Shop': [19942684, 19942972, 19943272, 19943384]}
EXIT = {'Arena_Shop': 22734236, 'PVP_Shop': 19943128}
WALLET = {'Arena_Shop': 20084804, 'PVP_Shop': 20085132}
GETID = {'Arena_Shop': 22732732, 'PVP_Shop': 19941788}
GETSTOCK = {'Arena_Shop': 22732896, 'PVP_Shop': 19889588}
ROLES = ['resource-pre', 'player', 'drone', 'resource-index']


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(BT.build(), sort_keys=True, separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', json.dumps(blob['open_items']))

    def test_every_check_passed(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 25)
        self.assertTrue(all(row['passed'] for row in checks), checks)


class Dispatch(unittest.TestCase):
    def test_one_click_handler_per_shop(self):
        bands = payload()['bands']
        self.assertEqual(sorted(bands), ['Arena_Shop', 'PVP_Shop'])
        for klass, row in bands.items():
            self.assertEqual(row['method_rva'], CLICK[klass])
            self.assertIn('OnClickPlayerItem', row['signature'])

    def test_id_is_read_from_cell_plus_0x64(self):
        for row in payload()['bands'].values():
            self.assertEqual(row['id_source']['op'], 'ldr w1, [x20, #0x64]')

    def test_two_thresholds_199_and_299_with_b_le(self):
        for row in payload()['bands'].values():
            self.assertEqual([item['limit'] for item in row['thresholds']], [199, 299])
            self.assertEqual([item['compare'] for item in row['thresholds']],
                             ['cmp w8, #0xc7', 'cmp w8, #0x12b'])
            self.assertTrue(all(item['branch'].startswith('b.le')
                                for item in row['thresholds']))

    def test_player_block_starts_at_first_target(self):
        expected = {'Arena_Shop': 22733852, 'PVP_Shop': 19942744}
        for klass, row in payload()['bands'].items():
            self.assertEqual(row['thresholds'][0]['target'], expected[klass])

    def test_drone_block_starts_at_second_target(self):
        expected = {'Arena_Shop': 22734128, 'PVP_Shop': 19943020}
        for klass, row in payload()['bands'].items():
            self.assertEqual(row['thresholds'][1]['target'], expected[klass])

    def test_resource_band_indexes_with_id_minus_300(self):
        for row in payload()['bands'].values():
            self.assertEqual(row['index']['base'], 300)
            self.assertEqual(row['index']['op'], 'sub w8, w8, #0x12c')

    def test_ids_are_identified_before_the_dispatch(self):
        for klass, row in payload()['bands'].items():
            self.assertEqual([call[1] for call in row['getid']], [GETID[klass]])
            self.assertEqual([call[1] for call in row['getstock']], [GETSTOCK[klass]])
            self.assertLess(row['getid'][0][0], row['thresholds'][0]['compare_rva'])
            self.assertLess(row['getstock'][0][0], row['thresholds'][0]['compare_rva'])


class Rows(unittest.TestCase):
    def test_four_event_rewards_ctor_sites_per_shop(self):
        for klass, row in payload()['bands'].items():
            self.assertEqual([item['call_rva'] for item in row['rows']], ROWS[klass])
            self.assertEqual(row['roles'], ROLES)

    def test_player_row_reads_player_fields(self):
        for row in payload()['bands'].values():
            player = next(item for item in row['rows'] if item['role'] == 'player')
            self.assertEqual((player['value']['kind'], player['value']['field']),
                             ('shop', 0x9C))
            self.assertEqual((player['cost']['kind'], player['cost']['field']),
                             ('shop', 0xA0))

    def test_drone_row_reads_drone_fields(self):
        for row in payload()['bands'].values():
            drone = next(item for item in row['rows'] if item['role'] == 'drone')
            self.assertEqual((drone['value']['field'], drone['cost']['field']), (0xA4, 0xA8))

    def test_resource_pre_row_reuses_drone_fields(self):
        for row in payload()['bands'].values():
            pre = next(item for item in row['rows'] if item['role'] == 'resource-pre')
            self.assertEqual((pre['value']['field'], pre['cost']['field']), (0xA4, 0xA8))

    def test_resource_index_row_reads_the_display_slots(self):
        for row in payload()['bands'].values():
            index = next(item for item in row['rows'] if item['role'] == 'resource-index')
            self.assertEqual((index['value']['kind'], index['value']['field']),
                             ('display', 0x14))
            self.assertEqual((index['cost']['kind'], index['cost']['field']),
                             ('display', 0x10))

    def test_every_row_caps_at_max_stock(self):
        for row in payload()['bands'].values():
            for item in row['rows']:
                self.assertEqual((item['maxstock']['kind'], item['maxstock']['field']),
                                 ('shop', 0x98))

    def test_only_the_resource_band_builds_two_rows(self):
        for row in payload()['bands'].values():
            slots = {item['role']: [slot['slot'] for slot in item['pack_slots']]
                     for item in row['rows']}
            self.assertEqual(slots['player'], [0x4C])
            self.assertEqual(slots['drone'], [0x48])
            self.assertEqual(slots['resource-pre'], [0x48])
            self.assertEqual(slots['resource-index'], [0x10, 0x2C, 0x44])

    def test_pack_slots_name_a_currency_bucket(self):
        for row in payload()['bands'].values():
            names = {slot['slot']: slot['field'] for item in row['rows']
                     for slot in item['pack_slots']}
            self.assertEqual(names, {0x10: 'Gcoins', 0x2C: 'Energy', 0x44: 'DroneExp',
                                     0x48: 'DroneCards', 0x4C: 'PlayerCards'})

    def test_card_slots_are_stamped_with_get_id_item_plus_one(self):
        for row in payload()['bands'].values():
            for item in row['rows']:
                if item['role'] == 'resource-index':
                    continue
                self.assertTrue(item['pack_slots'][0]['stamps_id_plus_one'])

    def test_resource_band_tests_300_and_301(self):
        expected = {'Arena_Shop': [(22733836, 22734428, 0x10), (22734436, 22734448, 0x2C)],
                    'PVP_Shop': [(19942728, 19943320, 0x10), (19943328, 19943340, 0x2C)]}
        for klass, row in payload()['bands'].items():
            self.assertEqual([(item['rva'], item['target'], item['slot'])
                              for item in row['equality']], expected[klass])


class Gates(unittest.TestCase):
    def test_every_band_checks_the_stock_cap(self):
        for klass, row in payload()['bands'].items():
            self.assertEqual(len(row['stock_gates']), 3)
            for gate in row['stock_gates']:
                self.assertEqual(gate['target'], EXIT[klass])
                self.assertTrue(gate['branch'].startswith('b.ge'))

    def test_every_band_rechecks_the_wallet(self):
        for klass, row in payload()['bands'].items():
            self.assertEqual(len(row['wallet']), 3)
            self.assertEqual([item['target'] for item in row['wallet']], [WALLET[klass]] * 3)

    def test_four_pack_objects_per_click(self):
        for row in payload()['bands'].values():
            self.assertEqual(len(row['packs']), 4)

    def test_setpopup_runs_once_after_the_last_row(self):
        for klass, row in payload()['bands'].items():
            self.assertEqual(len(row['setpopup']), 1)
            self.assertEqual(row['setpopup'][0]['rva'], SETPOPUP[klass])
            self.assertEqual(row['last_row'], ROWS[klass][-1])
            self.assertTrue(row['setpopup'][0]['after_last_row'])


class Layout(unittest.TestCase):
    def test_pack_layout_comes_from_the_dump(self):
        layout = payload()['pack_layout']
        self.assertEqual(layout['typedef_index'], 1032)
        self.assertEqual(layout['ctor'], 20189848)
        fields = {int(offset): row['name'] for offset, row in layout['fields'].items()}
        self.assertEqual(fields[0x10], 'Gcoins')
        self.assertEqual(fields[0x2C], 'Energy')
        self.assertEqual(fields[0x44], 'DroneExp')
        self.assertEqual(fields[0x48], 'DroneCards')
        self.assertEqual(fields[0x4C], 'PlayerCards')


class PreviousReports(unittest.TestCase):
    def test_159_chains_still_point_at_the_same_setpopup(self):
        previous = BT.load(BT.PREV)
        for klass, row in payload()['bands'].items():
            self.assertEqual(previous['chains'][klass]['caller']['call_rva'],
                             row['setpopup'][0]['rva'])

    def test_158_still_reports_four_rows_per_shop(self):
        previous = BT.load(BT.PREV158)
        self.assertTrue(all(len(rows) == 4 for rows in previous['rewards'].values()))


if __name__ == '__main__':
    unittest.main()
