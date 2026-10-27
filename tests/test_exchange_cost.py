"""Contracts for report 154: the medal exchange popup — two wallets, one formula."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import exchange_cost  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_exchange_cost.json.gz'
PIN_BYTES = 4086
PIN_SHA = 'e4045686828975f40fb1d75a941acadae9ff1d275932a166d63965a84a315d83'
WALLETS = {'Popup_PVPShopExchange': 20085132, 'Popup_ArenaShopExchange': 20084804}


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(exchange_cost.build(), sort_keys=True,
                          separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_four_sources(self):
        self.assertEqual(len(payload()['provenance']['sources']), 4)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])

    def test_previous_report_is_153(self):
        paths = [row['path'] for row in payload()['provenance']['sources']]
        self.assertIn('datas/l2_535b0541_shop_stock_layout.json.gz', paths)


class Layout(unittest.TestCase):
    def test_eleven_fields(self):
        rows = payload()['layout']['popup']
        self.assertEqual([row['name'] for row in rows],
                         ['textHeader', 'textStock', 'textCost', 'textCoinEvent', 'btnIcon',
                          'slider', 'onExit', 'count', 'maxStock', 'rewards', 'boxReward'])
        self.assertEqual([row['offset'] for row in rows],
                         ['0x20', '0x28', '0x30', '0x38', '0x40', '0x48', '0x50',
                          '0x58', '0x5c', '0x60', '0x68'])

    def test_reward_row(self):
        rows = payload()['layout']['rewards']
        self.assertEqual([row['name'] for row in rows],
                         ['pack', 'number', 'price', 'stock'])
        self.assertEqual([row['offset'] for row in rows], ['0x10', '0x18', '0x1c', '0x20'])

    def test_slider_divides_by_step_not_by_max(self):
        step = payload()['layout']['slider_step']
        self.assertEqual((step['offset'], step['field']), ('0x64', 'step'))
        self.assertIn('maxValue', step['note'])


class Wallets(unittest.TestCase):
    def test_two_different_wallets(self):
        currencies = payload()['cross_checks']['currencies']
        self.assertEqual({key: value[1] for key, value in currencies.items()}, WALLETS)

    def test_wallet_signatures(self):
        rows = payload()['popups']
        self.assertEqual(rows['Popup_PVPShopExchange']['wallet']['signature'],
                         'public static int get_PvPMedal() { }')
        self.assertEqual(rows['Popup_ArenaShopExchange']['wallet']['signature'],
                         'public static int get_ArenaMedal() { }')

    def test_wallet_is_read_before_the_gate(self):
        for row in payload()['buy'].values():
            rvas = [step['rva'] for step in row['steps']]
            self.assertLess(row['wallet']['rva'], rvas[3])


class Formula(unittest.TestCase):
    def test_count_comes_from_the_step(self):
        steps = {row['rva']: row for row in
                 payload()['on_change']['Popup_PVPShopExchange']['steps']}
        self.assertEqual(steps[19887940]['op'], 'ldr s9, [x8, #0x64]')
        self.assertEqual(steps[19887976]['op'], 'fdiv s9, s8, s9')

    def test_rounding_is_half_to_even(self):
        ops = [row['op'] for row in payload()['on_change']['Popup_PVPShopExchange']['steps']]
        self.assertIn('tst x8, #1', ops)
        self.assertIn('fcsel d0, d0, d1, eq', ops)

    def test_cost_is_price_times_count(self):
        ops = [row['op'] for row in payload()['on_change']['Popup_PVPShopExchange']['steps']]
        self.assertIn('mul w8, w9, w8', ops)
        self.assertEqual(payload()['cross_checks']['formula'],
                         'cost = EventRewards.price * round(slider.value / slider.step)')

    def test_preview_multiplies_the_reward_count(self):
        steps = {row['rva']: row for row in
                 payload()['on_change']['Popup_PVPShopExchange']['steps']}
        self.assertIn('SetNumber', steps[19888500]['meaning'])

    def test_shader_gate(self):
        self.assertEqual(payload()['on_change']['Popup_PVPShopExchange']['shader_property'],
                         '_EffectAmount')
        steps = {row['rva']: row for row in
                 payload()['on_change']['Popup_PVPShopExchange']['steps']}
        self.assertEqual(steps[19888612]['op'], 'fcsel s0, s1, s0, lt')


class Stock(unittest.TestCase):
    def test_max_stock_subtracts_what_was_bought(self):
        for row in payload()['popups'].values():
            self.assertIn('stock - GetStockItem(index)',
                          [step['meaning'] for step in row['guards']])

    def test_stock_read_is_the_shop_getter(self):
        rows = payload()['popups']
        self.assertEqual(rows['Popup_PVPShopExchange']['stock_read']['target'], 19889588)
        self.assertEqual(rows['Popup_ArenaShopExchange']['stock_read']['target'], 22732896)

    def test_stock_read_happens_before_the_subtract(self):
        for row in payload()['popups'].values():
            self.assertLess(row['stock_read']['rva'],
                            [step['rva'] for step in row['guards']][2])


class Buy(unittest.TestCase):
    def test_popup_never_deducts(self):
        for row in payload()['buy'].values():
            self.assertIn('deducts_nothing', row)
        self.assertFalse(payload()['cross_checks']['deducted_in_popup'])

    def test_buy_hands_the_count_back(self):
        for row in payload()['buy'].values():
            self.assertIn('onExit(count)', [step['meaning'] for step in row['steps']])

    def test_buy_hides_the_popup(self):
        for row in payload()['buy'].values():
            self.assertIn('SetActive', row['steps'][-1]['meaning'])

    def test_buy_methods(self):
        self.assertEqual(payload()['buy']['Popup_PVPShopExchange']['method']['rva'], 19890912)
        self.assertEqual(payload()['buy']['Popup_ArenaShopExchange']['method']['rva'],
                         22837792)


class Keys(unittest.TestCase):
    def test_two_keys_each(self):
        for row in payload()['popups'].values():
            self.assertEqual(sorted(row['keys']), ['txt_exchange', 'txt_stock'])

    def test_setpopup_calls_gettext_twice(self):
        for row in payload()['popups'].values():
            self.assertEqual(len(row['gettext_calls']), 2)
            self.assertTrue(all(call['target'] == 21202600
                                for call in row['gettext_calls']))


class Twins(unittest.TestCase):
    def test_one_size_delta(self):
        self.assertEqual(len(payload()['twins']['only_size_delta']), 1)
        self.assertIn('SetPopup', payload()['twins']['only_size_delta'][0])

    def test_eleven_fields_both(self):
        self.assertEqual(payload()['twins']['fields'], 11)

    def test_no_caller_for_setpopup(self):
        rows = payload()['entry_point']['rows']
        self.assertTrue(all(not row['callers'] for row in rows))


class ThirdPopup(unittest.TestCase):
    def test_typedef_and_arity(self):
        row = payload()['third_popup']
        self.assertEqual((row['typedef'], row['set_popup_arity'], row['fields']),
                         (693, 5, 11))

    def test_eight_methods_all_below_the_slice(self):
        row = payload()['third_popup']
        self.assertEqual(len(row['methods']), 8)
        self.assertTrue(all(method['rva'] < row['slice_span'][0]
                            for method in row['methods']))

    def test_extra_arguments_are_card_sprites(self):
        row = next(m for m in payload()['third_popup']['methods'] if m['name'] == 'SetPopup')
        self.assertIn('Sprite[] droneCardSprites', row['signature'])
        self.assertIn('Sprite[] shipCardSprites', row['signature'])

    def test_wallet_stays_unknown(self):
        self.assertEqual(payload()['third_popup']['set_popup_arity'], 5)
        self.assertNotIn('wallet', payload()['third_popup'])


class Findings(unittest.TestCase):
    def test_all_checks_pass(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 16)
        self.assertTrue(all(row['passed'] for row in checks), checks)

    def test_three_confirmations(self):
        rows = payload()['confirmations']
        self.assertEqual(len(rows), 3)
        self.assertIn('153', rows[0]['item'])

    def test_four_open_items(self):
        rows = payload()['open_items']
        self.assertEqual(len(rows), 4)
        self.assertIn('MODEL_NOT_MEASURED runtime', rows[1]['blocking'])
        self.assertIn('Popup_Exchange', rows[2]['item'])
        self.assertIn('43584368', rows[3]['item'])

    def test_rvas_are_integers(self):
        self.assertIsInstance(payload()['popups']['Popup_PVPShopExchange']['method']['rva'], int)


if __name__ == '__main__':
    unittest.main()
