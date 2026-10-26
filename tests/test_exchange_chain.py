"""Contracts for report 159: the exchange popup is opened by the shop click
handler, and its Buy button only compares the wallet — it never spends it."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import exchange_chain as EC  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_exchange_chain.json.gz'
PIN_BYTES = 3458
PIN_SHA = '09672352efc79270ad9e62045d4a51b9934181fab8ed8fad50d2dc68c063eb18'
GETTERS = {'Arena_Shop': 20084804, 'PVP_Shop': 20085132}
CALLS = {'Arena_Shop': 22734600, 'PVP_Shop': 19943488}
CLICK = {'Arena_Shop': 22733228, 'PVP_Shop': 19942120}
SETPOPUP = {'Arena_Shop': 22835700, 'PVP_Shop': 19888660}
BUY = {'Arena_Shop': 22837792, 'PVP_Shop': 19890912}


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(EC.build(), sort_keys=True, separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', json.dumps(blob['open_items']))


class Caller(unittest.TestCase):
    def test_exactly_one_caller_per_popup(self):
        chains = payload()['chains']
        self.assertEqual(sorted(chains), ['Arena_Shop', 'PVP_Shop'])
        for klass, row in chains.items():
            self.assertEqual(row['caller']['class_name'], klass)
            self.assertEqual(row['caller']['method_rva'], CLICK[klass])
            self.assertEqual(row['caller']['call_rva'], CALLS[klass])

    def test_the_call_is_a_tail_branch_with_three_arguments(self):
        for row in payload()['chains'].values():
            caller = row['caller']
            self.assertEqual(caller['branch'], 'b')
            self.assertEqual(sorted(caller['args']), ['w1', 'x2', 'x3'])
            self.assertEqual(caller['args']['w1']['source'], 'w22')
            self.assertEqual(caller['args']['x2']['source'], 'x21')
            self.assertEqual(caller['args']['x3']['source'], 'x23')

    def test_the_third_argument_is_a_fresh_action_int(self):
        for row in payload()['chains'].values():
            self.assertEqual(row['caller']['delegate']['op'], 'bl #0x18a4d84')
            self.assertLess(row['caller']['delegate']['rva'], row['caller']['call_rva'])


class SetPopup(unittest.TestCase):
    def test_sizes_and_entry_points(self):
        for klass, row in payload()['chains'].items():
            self.assertEqual(row['setpopup']['rva'], SETPOPUP[klass])
            self.assertIn(row['setpopup']['signature'],
                          ('public void SetPopup(int index, Board_EventSeasonPass.EventRewards '
                           'eventReward, Action<int> exit) { }',))

    def test_stores_exit_count_rewards_and_max_stock(self):
        for row in payload()['chains'].values():
            setpopup = row['setpopup']
            self.assertTrue(setpopup['exit_store'][0]['op'].endswith('#0x50]'))
            self.assertTrue(any(store['writeback'] for store in setpopup['count_store']))
            self.assertTrue(any(store['op'].endswith('#8]') for store in setpopup['rewards_store']))
            self.assertTrue(setpopup['maxstock_store'][0]['op'].endswith('#0x5c]!'))

    def test_max_stock_is_stock_minus_sold(self):
        for row in payload()['chains'].values():
            setpopup = row['setpopup']
            self.assertTrue(setpopup['stock_read']['op'].endswith('#0x20]'))
            self.assertEqual(setpopup['getstock']['target'],
                             EC.SHOPS[row['caller']['class_name']]['getstock'])
            self.assertTrue(setpopup['getstock']['op'].startswith('bl '))

    def test_cost_text_is_price_times_count(self):
        for row in payload()['chains'].values():
            setpopup = row['setpopup']
            self.assertTrue(setpopup['price_read']['op'].endswith('#0x1c]'))
            self.assertEqual(setpopup['mul']['op'], 'mul w8, w9, w8')
            self.assertEqual(setpopup['format']['op'], 'bl #0x1fe4c90')

    def test_tabs_and_slider_are_refreshed(self):
        for row in payload()['chains'].values():
            self.assertIn('SetEventRewardTabs',
                          EC.AR.owner(row['setpopup']['tabs']['target'])[1] or '')
            self.assertEqual(row['setpopup']['slider']['op'], 'bl #0x13ef6b8')


class Buy(unittest.TestCase):
    def test_compares_the_right_wallet(self):
        chains = payload()['chains']
        for klass, row in chains.items():
            self.assertEqual(row['buy']['rva'], BUY[klass])
            self.assertEqual(row['buy']['wallet_get']['target'], GETTERS[klass])

    def test_never_writes_the_wallet(self):
        for row in payload()['chains'].values():
            self.assertEqual(row['buy']['wallet_set'], [])
            self.assertEqual(row['wallet_writes'], [])

    def test_invokes_the_callback_and_hides(self):
        for row in payload()['chains'].values():
            self.assertEqual(row['buy']['exit_read']['op'], 'ldr x8, [x19, #0x50]')
            self.assertEqual(row['buy']['invoke']['op'], 'blr x9')
            self.assertEqual(row['buy']['guard']['op'].split()[0], 'b.ge')
            self.assertEqual(row['buy']['count_read']['op'], 'ldr w9, [x19, #0x58]')
            self.assertEqual(row['buy']['hide']['target'], EC.SET_ACTIVE)
            self.assertEqual(EC.AR.owner(row['buy']['hide']['target'])[1],
                             'public void SetActive(bool value) { }')

    def test_total_is_price_times_count(self):
        for row in payload()['chains'].values():
            self.assertEqual(row['buy']['mul']['op'], 'mul w20, w8, w9')
            self.assertEqual(row['buy']['compare']['op'], 'cmp w0, w20')


class ChecksAndTotals(unittest.TestCase):
    def test_every_check_passed(self):
        rows = payload()['checks']
        self.assertEqual(len(rows), 14)
        self.assertTrue(all(item['passed'] for item in rows),
                        [item for item in rows if not item['passed']])

    def test_totals(self):
        totals = payload()['totals']
        self.assertEqual(totals['popups'], 2)
        self.assertEqual(totals['setpopup_callers'], 2)
        self.assertEqual(totals['wallet_setter_calls_in_popups'], 0)

    def test_confirmations_cover_154_155_156_158(self):
        blob = '\n'.join(row['item'] for row in payload()['confirmations'])
        for report in ('154', '155', '156', '158'):
            self.assertIn(report, blob)

    def test_open_items(self):
        rows = payload()['open_items']
        self.assertEqual(len(rows), 3)
        self.assertIn('metadata', json.dumps(rows))
        self.assertIn('Popup_Exchange', json.dumps(rows))


if __name__ == '__main__':
    unittest.main()
