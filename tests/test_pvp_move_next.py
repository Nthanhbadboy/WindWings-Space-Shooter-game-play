"""Contracts for report 172: two of 169's reader lists were class-init cells.

A cell load and a field load share one instruction shape. Deciding by the base register's
last definition removes three readers from the reward arrays (`<IsCollected|0>`) and three
from the bet ladders (`MoveNext`), and leaves the table 169 should have printed.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import pvp_move_next as MN  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_pvp_move_next.json.gz'
PIN_BYTES = 2975
PIN_SHA = 'ec79aff771ea83f7011490a49fddf4fd2560eee15f1890fe4d9fb67080c53a2d'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        _, packed = MN.build(None)
        self.assertEqual(packed, ARTIFACT.read_bytes())

    def test_every_check_passed(self):
        rows = payload()['checks']
        self.assertEqual(len(rows), 13)
        self.assertEqual([row['name'] for row in rows if not row['passed']], [])


class CorrectedTable(unittest.TestCase):
    def test_the_six_readers(self):
        readers = {name: row['methods'] for name, row in payload()['readers'].items()}
        self.assertEqual(readers, {
            'rewardIndexs': [19791640, 19792936],
            'rewardValues': [19791640, 19792936],
            'rewardScales': [19791640],
            'allBetCoinValues': [19779724],
            'allBetGemValues': [19779984],
            'allBetMedalValues': [19780244],
        })

    def test_the_coroutine_is_gone_from_the_bet_ladders(self):
        for name in ('allBetCoinValues', 'allBetGemValues', 'allBetMedalValues'):
            self.assertNotIn(19813332, payload()['readers'][name]['methods'])

    def test_is_collected_is_gone_from_the_reward_arrays(self):
        for name in ('rewardIndexs', 'rewardValues', 'rewardScales'):
            self.assertNotIn(19811092, payload()['readers'][name]['methods'])

    def test_six_corrections_are_recorded(self):
        rows = payload()['corrections']
        self.assertEqual(len(rows), 6)
        self.assertEqual({row['field'] for row in rows},
                         {'rewardIndexs', 'rewardValues', 'rewardScales',
                          'allBetCoinValues', 'allBetGemValues', 'allBetMedalValues'})
        for row in rows:
            self.assertNotEqual(row['was'], row['now'])

    def test_the_cell_addresses_are_the_field_offsets(self):
        cells = [row for row in payload()['sites'] if row['kind'] == 'cell']
        self.assertEqual(len(cells), 12)
        self.assertEqual({row['offset'] for row in cells},
                         {'0x198', '0x1a0', '0x1a8', '0x208', '0x210', '0x218'})


class Sites(unittest.TestCase):
    def test_every_cell_site_is_defined_by_adrp(self):
        for row in payload()['sites']:
            if row['kind'] == 'cell':
                self.assertEqual(row['base_defined_by'], 'adrp', row['rva'])

    def test_every_instance_site_is_defined_by_a_mov(self):
        for row in payload()['sites']:
            if row['kind'] == 'instance':
                self.assertEqual(row['base_defined_by'], 'mov', row['rva'])

    def test_the_six_stores_in_the_constructor_are_instance(self):
        stores = [row for row in payload()['sites'] if row['mnemonic'] == 'str']
        self.assertEqual(len(stores), 6)
        self.assertEqual({row['method_rva'] for row in stores}, {19796420})

    def test_twenty_nine_sites(self):
        self.assertEqual(payload()['totals']['sites'], 29)
        self.assertEqual(payload()['totals']['cells'], 12)


class Coroutine(unittest.TestCase):
    def test_shape(self):
        row = payload()['move_next']
        self.assertEqual((row['rva'], row['size'], row['instructions']),
                         (19813332, 1808, 452))

    def test_it_is_the_firebase_sync(self):
        names = {row['signature'] for row in payload()['move_next']['calls']}
        self.assertTrue(any('DownloadDatabase' in name for name in names))
        self.assertTrue(any('IESummarySeasonRewards' in name for name in names))
        self.assertTrue(any('LoadPvPDatas' in name for name in names))
        self.assertTrue(any('DeleteDatabase' in name for name in names))

    def test_it_reads_no_board_field(self):
        mine = [row for row in payload()['sites'] if row['method_rva'] == 19813332]
        self.assertTrue(mine)
        self.assertTrue(all(row['kind'] == 'cell' for row in mine))

    def test_limits(self):
        text = ' '.join(payload()['limits'])
        self.assertIn('unknown', text)
        self.assertIn('MODEL_NOT_MEASURED', text)

    def test_provenance_matches(self):
        for row in payload()['provenance']['inputs']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])


if __name__ == '__main__':
    unittest.main()
