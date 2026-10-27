"""Contracts for report 158: the shop reads all eight economy fields, and the two
value/cost pairs are only ever read through `ldp` pair loads."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import shop_field_readers as SFR  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_shop_field_readers.json.gz'
PIN_BYTES = 3922
PIN_SHA = 'dd3af9c90a623c98e8d7519ddcb967964e2679717deeaa80f91a9bba95d79278'
CLICK = {'Arena_Shop': 22733228, 'PVP_Shop': 19942120}
INIT = {'Arena_Shop': 22730080, 'PVP_Shop': 19939136}
ONENABLE = {'Arena_Shop': 22727788, 'PVP_Shop': 19936844}
PAIR_FIELDS = ('ItemPlayerValue', 'ItemPlayerCost', 'ItemDroneValue', 'ItemDroneCost')


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(SFR.build(), sort_keys=True, separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', json.dumps(blob['open_items']))


class FieldCensus(unittest.TestCase):
    def test_all_eight_fields_are_present(self):
        self.assertEqual(sorted(payload()['fields']), sorted(SFR.FIELDS.values()))
        self.assertEqual(len(payload()['fields']), 8)

    def test_every_field_has_at_least_one_reader(self):
        for name, row in payload()['fields'].items():
            self.assertGreater(row['reads'], 0, name)

    def test_pair_fields_have_no_scalar_reader(self):
        for name in PAIR_FIELDS:
            row = payload()['fields'][name]
            self.assertEqual(row['direct_reads'], 0, name)
            self.assertEqual(row['pair_reads'], 6, name)
            self.assertTrue(all(site['pair'] or site['kind'] == 'write'
                                for site in row['sites']), name)

    def test_pair_loads_cover_two_adjacent_ints(self):
        values = {site['rva'] for site in payload()['fields']['ItemPlayerValue']['sites']}
        costs = {site['rva'] for site in payload()['fields']['ItemPlayerCost']['sites']}
        self.assertEqual(values, costs)
        for site in payload()['fields']['ItemPlayerValue']['sites']:
            self.assertTrue(site['op'].startswith('ldp '), site['op'])

    def test_max_stock_count_is_read_most(self):
        rows = payload()['fields']
        self.assertEqual(rows['MaxStockCount']['reads'], 16)
        self.assertEqual(rows['MaxStockCount']['reads'],
                         max(row['reads'] for row in rows.values()))

    def test_closure_reads_carry_the_captured_shop_chain(self):
        sites = [site for site in payload()['fields']['MaxStockCount']['sites']
                 if site['chain']]
        self.assertEqual(len(sites), 8)
        closure = [site for site in sites if 'DisplayClass' in site['class_name']]
        self.assertEqual(len(closure), 6)
        for site in closure:
            self.assertEqual(site['chain'], ['0x18', '0x10'])

    def test_timer_readers_are_onenable_and_the_countdown_coroutine(self):
        classes = {site['class_name'] for site in payload()['fields']['timeToReset']['sites']
                   if site['kind'] == 'read'}
        self.assertEqual(classes, {'Arena_Shop', 'Arena_Shop.<IEUpdateTime>d__43',
                                   'PVP_Shop', 'PVP_Shop.<IEUpdateTime>d__43'})

    def test_constructor_is_still_the_only_writer(self):
        methods = {site['method_rva'] for row in payload()['fields'].values()
                   for site in row['sites'] if site['kind'] == 'write'}
        self.assertEqual(methods, {22735024, 19943896})

    def test_arrays_are_read_only_in_init_and_click(self):
        for name in ('ItemResourceValues', 'ItemResourceCost'):
            methods = {site['method_rva'] for site in payload()['fields'][name]['sites']
                       if site['kind'] == 'read'}
            self.assertEqual(methods, {INIT['Arena_Shop'], CLICK['Arena_Shop'],
                                       INIT['PVP_Shop'], CLICK['PVP_Shop']}, name)


class RewardsRows(unittest.TestCase):
    def test_four_rows_per_shop(self):
        rewards = payload()['rewards']
        self.assertEqual(sorted(rewards), ['Arena_Shop', 'PVP_Shop'])
        for klass, rows in rewards.items():
            self.assertEqual(len(rows), 4, klass)
            self.assertEqual([row['method_rva'] for row in rows], [CLICK[klass]] * 4)

    def test_stock_always_comes_from_max_stock_count(self):
        for rows in payload()['rewards'].values():
            for row in rows:
                self.assertEqual(row['args']['stock']['field'], 'MaxStockCount')
                self.assertEqual(row['args']['stock']['text'], 'this.0x98')

    def test_three_rows_come_from_the_two_pairs(self):
        for rows in payload()['rewards'].values():
            self.assertEqual(
                [(row['args']['number']['field'], row['args']['price']['field'])
                 for row in rows],
                [('ItemDroneValue', 'ItemDroneCost'),
                 ('ItemPlayerValue', 'ItemPlayerCost'),
                 ('ItemDroneValue', 'ItemDroneCost'),
                 (None, None)])
            self.assertEqual(rows[3]['args']['price']['text'], 'x20.0x10')

    def test_ctor_is_the_dump_declared_one(self):
        self.assertEqual(SFR.AR.owner(SFR.REWARDS_CTOR)[1],
                         'public void .ctor(Shop_Pack pack, int number, int price, '
                         'int stock) { }')


class Totals(unittest.TestCase):
    def test_totals(self):
        totals = payload()['totals']
        self.assertEqual(totals['accesses'], 62)
        self.assertEqual(totals['reads'], 52)
        self.assertEqual(totals['writes'], 10)
        self.assertEqual(totals['pair_reads'], 24)
        self.assertEqual(totals['rewards_rows'], 8)

    def test_every_check_passed(self):
        rows = payload()['checks']
        self.assertEqual(len(rows), 15)
        self.assertTrue(all(row['passed'] for row in rows),
                        [item for item in rows if not item['passed']])

    def test_confirmations_name_154_156_and_157(self):
        blob = '\n'.join(row['item'] for row in payload()['confirmations'])
        for report in ('154', '156', '157'):
            self.assertIn(report, blob)

    def test_open_items(self):
        rows = payload()['open_items']
        self.assertEqual(len(rows), 3)
        blob = json.dumps(rows)
        self.assertIn('InitializeArray', blob)
        self.assertIn('MODEL_NOT_MEASURED runtime', blob)


if __name__ == '__main__':
    unittest.main()
