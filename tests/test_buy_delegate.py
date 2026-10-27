"""Contracts for report 163: the `Action<int>` the shop binds for the popup.

The click handler allocates one `<>c__DisplayClass31_{1,2,3}` per band and passes it as
`new Action<int>(bandClosure, methodCell)`. Each of those classes declares exactly one
`void (int)` method, so the delegate target is `b__1` / `b__3` / `b__5`, which tail-branch
into `g__OnBuy|2` / `|4` / `|6`. Everything here is static.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import buy_delegate as BD  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_buy_delegate.json.gz'
PIN_BYTES = 8343
PIN_SHA = 'a1c98fc6ad2d529c26c692a9565250c94962a6e760b55ce1e11d15f1327c6f5b'

CLICK = {'Arena_Shop': 22733228, 'PVP_Shop': 19942120}
MEDAL = {'Arena_Shop': (20084804, 20085004), 'PVP_Shop': (20085132, 20085332)}
CELLS = {'Arena_Shop': {'player': (0xC8, 0xC0), 'drone': (0xD8, 0xD0),
                        'resource': (0xE8, 0xE0)},
         'PVP_Shop': {'player': (0x68, 0x60), 'drone': (0x78, 0x70),
                      'resource': (0x88, 0x80)}}
LAMBDA = {'Arena_Shop': {'player': (22735492, 22735600), 'drone': (22771704, 22771812),
                         'resource': (22772604, 22772712)},
          'PVP_Shop': {'player': (19944380, 19944488), 'drone': (19945316, 19945424),
                       'resource': (19946216, 19946324)}}
ACTION_CTOR = 25841028


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(BD.build(), sort_keys=True, separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', json.dumps(blob['open_items']))

    def test_every_check_passed(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 43)
        self.assertTrue(all(row['passed'] for row in checks), checks)

    def test_no_runtime_claim_in_the_note(self):
        note = payload()['note']
        self.assertNotIn('runtime', note)
        self.assertIn('Action<int>', note)


class Cells(unittest.TestCase):
    def test_seven_cells_per_shop(self):
        for klass, shop in payload()['shops'].items():
            self.assertEqual(len(shop['click']['cells']), 7)
            self.assertEqual(shop['click']['rva'], CLICK[klass])
            self.assertEqual(shop['click']['signatures'], 14)

    def test_class_and_method_cell_per_band(self):
        for klass, shop in payload()['shops'].items():
            for band, (class_cell, method_cell) in CELLS[klass].items():
                entry = shop['bands'][band]
                self.assertEqual(entry['class_cell']['cell'], class_cell)
                self.assertEqual(entry['method_cell']['cell'], method_cell)

    def test_each_cell_is_read_twice_once_per_path_once_in_the_static_init(self):
        for shop in payload()['shops'].values():
            self.assertEqual(len(shop['not_on_a_band_path']), 8)
            self.assertEqual(sum(len(shop['bands'][band]['path_cells'])
                                 for band in BD.BANDS), 6)

    def test_the_off_path_reads_are_the_outer_cell_plus_the_static_init_block(self):
        for shop in payload()['shops'].values():
            cells = shop['click']['cells']
            off_path = [row['cell'] for row in shop['not_on_a_band_path']]
            outer = cells[0]
            self.assertEqual(off_path[0], outer)
            self.assertEqual(sorted(off_path[1:]), sorted(cells))

    def test_the_method_cell_is_consumed_as_the_delegate_method_pointer(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                entry = shop['bands'][band]
                self.assertEqual(entry['method_cell']['consumed_by'], 'ldr x2, [x8]')
                self.assertEqual(entry['delegate']['method_pointer_rva'],
                                 entry['method_cell']['consumed_at'])


class Ladder(unittest.TestCase):
    def test_three_entries_with_the_160_thresholds(self):
        for shop in payload()['shops'].values():
            self.assertEqual([row['band'] for row in shop['ladder']],
                             ['player', 'drone', 'resource'])
            self.assertEqual([row['cmp'] for row in shop['ladder']],
                             ['cmp w8, #0xc7', 'cmp w8, #0x12b', None])
            self.assertEqual([row['band_base'] for row in shop['ladder']],
                             ['0x64', '0xc8', '0x12c'])

    def test_the_resource_band_is_the_fall_through(self):
        for shop in payload()['shops'].values():
            self.assertEqual(shop['ladder'][2]['branch'], 'fall-through')
            self.assertLess(shop['ladder'][2]['entry_rva'],
                            shop['ladder'][0]['entry_rva'])

    def test_every_path_guards_the_sold_counter_against_the_cap(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                guard = shop['bands'][band]['stock_guard'][0]
                self.assertEqual(guard['cmp'], 'cmp w8, w9')
                self.assertTrue(guard['branch'].startswith('b.ge'))

    def test_every_path_guards_the_medal_balance_inline(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                guard = shop['bands'][band]['medal_guard'][0]
                self.assertEqual(guard['cmp'], 'cmp w0, w8')
                self.assertTrue(guard['branch'].startswith('b.'))

    def test_every_path_tail_branches_into_setpopup(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                popup = shop['bands'][band]['set_popup']
                self.assertIn('SetPopup', popup['target_method'])
                self.assertTrue(popup['target_class'].endswith('ShopExchange'))

    def test_player_and_drone_stamp_a_multiplied_price(self):
        for shop in payload()['shops'].values():
            for band in ('player', 'drone'):
                ops = [row['op'] for row in shop['bands'][band]['stamp']]
                self.assertTrue(ops[-2].startswith('mul '), ops)
                self.assertIn('#0x10]', ops[-1])
                self.assertEqual(ops[-1].split(', #')[-1].rstrip(']'), '0x10')

    def test_resource_stamp_reads_the_price_list(self):
        for shop in payload()['shops'].values():
            ops = [row['op'] for row in shop['bands']['resource']['stamp']]
            self.assertFalse(any(op.startswith('mul ') for op in ops), ops)
            self.assertIn('ldr w9, [x9, #0x20]', ops)


class Delegate(unittest.TestCase):
    def test_the_action_ctor_is_the_generic_instantiation(self):
        for shop in payload()['shops'].values():
            self.assertEqual(shop['delegate_ctor']['ctor']['rva'], ACTION_CTOR)
            self.assertEqual(shop['delegate_ctor']['target_register'], 'x20')

    def test_each_band_names_a_distinct_display_class(self):
        for shop in payload()['shops'].values():
            self.assertEqual({row['display_class'] for row in shop['bands'].values()},
                             set(shop['display_classes']))

    def test_band_to_display_class_map(self):
        for klass, shop in payload()['shops'].items():
            self.assertTrue(shop['bands']['player']['display_class'].endswith('31_1'))
            self.assertTrue(shop['bands']['drone']['display_class'].endswith('31_2'))
            self.assertTrue(shop['bands']['resource']['display_class'].endswith('31_3'))
            self.assertEqual(shop['bands']['player']['display_class'],
                             f'{klass}.<>c__DisplayClass31_1')

    def test_five_ctors_are_named_and_one_folds_into_object(self):
        rows = [(klass, band) for klass, shop in payload()['shops'].items()
                for band in BD.BANDS
                if shop['bands'][band]['display_identified_by'] == 'named ctor']
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows, [('Arena_Shop', 'drone'), ('Arena_Shop', 'resource'),
                                ('PVP_Shop', 'player'), ('PVP_Shop', 'drone'),
                                ('PVP_Shop', 'resource')])

    def test_the_folded_ctor_still_names_object(self):
        arena = payload()['shops']['Arena_Shop']['bands']['player']
        self.assertEqual(arena['class_cell']['ctor']['class_name'], 'Object')

    def test_each_display_class_declares_exactly_three_methods(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                entry = shop['bands'][band]
                self.assertEqual(entry['single_int_methods'], 1)
                self.assertEqual(len(entry['declared_methods']), 3)
                ints = [sig for sig in entry['declared_methods']
                        if sig.count('int ') == 1]
                self.assertEqual(ints, [entry['delegate']['lambda_signature']])

    def test_the_outer_capture_is_not_a_band_closure(self):
        for shop in payload()['shops'].values():
            self.assertNotIn('_0', ''.join(shop['display_classes']))


class Lambdas(unittest.TestCase):
    def test_three_lambdas_per_shop_with_pinned_rvas(self):
        for klass, shop in payload()['shops'].items():
            for band, (lambda_rva, onbuy) in LAMBDA[klass].items():
                self.assertEqual(shop['bands'][band]['lambda_']['rva'], lambda_rva)
                self.assertEqual(shop['bands'][band]['closure']['rva'], onbuy)

    def test_every_lambda_is_108_bytes(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                self.assertEqual(shop['bands'][band]['lambda_']['size'], 108)

    def test_every_lambda_re_enables_the_scroll_view(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                view = shop['bands'][band]['lambda_']['scroll_view']
                self.assertEqual(view['value'], 'true')
                self.assertIn('set_EnableScrollView', view['callee'])
                self.assertEqual(view['callee_rva'], 21291032)

    def test_every_lambda_guards_count_at_one(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                guard = shop['bands'][band]['lambda_']['guard']
                self.assertEqual(guard['cmp'], 'cmp w19, #1')
                self.assertTrue(guard['branch'].startswith('b.lt'))

    def test_every_lambda_tail_branches_into_its_own_onbuy(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                tail = shop['bands'][band]['lambda_']['tail']
                self.assertEqual(tail['target'], shop['bands'][band]['closure']['rva'])
                self.assertIn('g__OnBuy', tail['target_method'])

    def test_the_lambda_signature_takes_the_count(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                self.assertIn('(int count)', shop['bands'][band]['lambda_']['signature'])
                self.assertEqual(shop['bands'][band]['lambda_']['count_register'], 'w2')
                self.assertEqual(shop['bands'][band]['lambda_']['id_load'],
                                 'ldr w1, [x8, #0x18]')


class Closures(unittest.TestCase):
    def test_every_closure_spends_the_shop_medal(self):
        for klass, shop in payload()['shops'].items():
            for band in BD.BANDS:
                medal = shop['bands'][band]['closure']['medal']
                self.assertEqual((medal['getter'], medal['setter']), MEDAL[klass])
                self.assertEqual(medal['spend']['op'], 'msub w0, w8, w21, w0')
                self.assertLess(medal['get_call'], medal['spend']['rva'])
                self.assertGreater(medal['set_call'], medal['spend']['rva'])

    def test_no_closure_re_checks_the_wallet(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                medal = shop['bands'][band]['closure']['medal']
                self.assertFalse(medal['wallet_recheck'])
                self.assertNotIn('cmp', ''.join(medal['between_get_and_spend']))

    def test_player_credits_playercards_behind_a_10001_bias(self):
        for shop in payload()['shops'].values():
            closure = shop['bands']['player']['closure']
            self.assertEqual([row['method'] for row in closure['grants']],
                             ['GetPlayerCards', 'SetPlayerCards'])
            self.assertEqual([row['bias'] for row in closure['biases']], [10001])

    def test_drone_credits_dronecards_behind_a_20001_bias(self):
        for shop in payload()['shops'].values():
            closure = shop['bands']['drone']['closure']
            self.assertEqual([row['method'] for row in closure['grants']],
                             ['GetDroneCards', 'SetDroneCards'])
            self.assertEqual([row['bias'] for row in closure['biases']], [20001])

    def test_every_credit_is_a_read_modify_write_with_madd(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                closure = shop['bands'][band]['closure']
                self.assertTrue(closure['madds'])
                self.assertEqual([row['access'] for row in closure['grants']][:2],
                                 ['get', 'set'])

    def test_every_closure_increments_the_stock_snapshot(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                stock = shop['bands'][band]['closure']['stock']
                self.assertEqual(stock['add_op'], 'add w2, w8, w21')
                self.assertTrue(stock['set_call_rva'])

    def test_every_closure_rebuilds_the_cell_text(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                text = shop['bands'][band]['closure']['cell_text']
                self.assertEqual(text['array_length'], 5)
                self.assertTrue(text['array_rva'])
                self.assertTrue(text['concat_rva'])
                self.assertTrue(text['set_stock_count'])

    def test_the_rebuilt_text_is_remaining_over_cap(self):
        for shop in payload()['shops'].values():
            for band in BD.BANDS:
                text = shop['bands'][band]['closure']['cell_text']
                self.assertEqual([row['op'] for row in text['subs']],
                                 ['sub w8, w22, w0'])
                self.assertEqual([row['op'] for row in text['max_stock_adds']],
                                 ['add x0, x8, #0x98'])
                self.assertEqual(sorted(text['cells']), ['0x2adb8d0', '0x2adbbd0'])
                self.assertEqual([row['method'] for row in text['calls']
                                  if row['method']],
                                 ['GetText', 'GetStockItem', 'ToString', 'ToString'])


class Resource(unittest.TestCase):
    def test_three_counters_by_id(self):
        for shop in payload()['shops'].values():
            closure = shop['bands']['resource']['closure']
            self.assertEqual([row['method'] for row in closure['grants']],
                             ['get_Coins', 'set_Coins', 'get_Energy', 'set_Energy',
                              'GetDroneExp', 'SetDroneExp'])
            self.assertEqual({row['op'] for row in closure['id_branches']},
                             {'cmp w20, #0x12c', 'cmp w20, #0x12d'})

    def test_energy_takes_the_second_branch(self):
        for shop in payload()['shops'].values():
            closure = shop['bands']['resource']['closure']
            self.assertEqual(closure['id_branches'][0]['op'], 'cmp w20, #0x12d')

    def test_two_effect_calls_with_distinct_types(self):
        for shop in payload()['shops'].values():
            effects = shop['bands']['resource']['closure']['effects']
            self.assertEqual([row['effect_arg'] for row in effects],
                             ['mov w0, wzr', 'mov w0, #2'])
            self.assertEqual(len(shop['bands']['resource']['closure']['posts']), 1)

    def test_the_player_and_drone_closures_have_no_effect_call(self):
        for shop in payload()['shops'].values():
            for band in ('player', 'drone'):
                self.assertEqual(shop['bands'][band]['closure']['effects'], [])


class PreviousReports(unittest.TestCase):
    def test_162_id_offset_round_trips(self):
        previous = BD.load(BD.PREV162)
        self.assertEqual(previous['totals']['id_offset'], -10001)

    def test_162_is_still_green(self):
        previous = BD.load(BD.PREV162)
        self.assertEqual(len(previous['checks']), 22)
        self.assertTrue(all(row['passed'] for row in previous['checks']))

    def test_159_still_pins_one_setpopup_per_click(self):
        previous = BD.load(BD.PREV159)
        for klass in CLICK:
            buy = previous['chains'][klass]['buy']
            self.assertEqual(buy['popup'], 'Popup_%sShopExchange'
                             % ('Arena' if klass == 'Arena_Shop' else 'PVP'))
            self.assertEqual(buy['wallet'], 'ArenaMedal' if klass == 'Arena_Shop'
                             else 'PvPMedal')
            self.assertEqual(buy['compare']['op'], 'cmp w0, w20')

    def test_160_still_pins_the_thresholds(self):
        previous = BD.load(BD.PREV160)
        for klass in CLICK:
            self.assertEqual(len(previous['bands'][klass]['thresholds']), 2)

    def test_156_still_pins_six_incrementing_writers(self):
        previous = BD.load(BD.PREV156)
        self.assertEqual(len(previous['writers']), 6)
        self.assertTrue(all(row['direction'] == 'increment'
                            for row in previous['writers']))

    def test_161_index_is_still_green(self):
        previous = BD.load(BD.PREV161)
        self.assertEqual(len(previous['checks']), 24)
        self.assertTrue(all(row['passed'] for row in previous['checks']))


class Api(unittest.TestCase):
    def test_the_grant_methods_resolve_in_the_dump(self):
        for name in ('GetPlayerCards', 'SetPlayerCards', 'GetDroneCards',
                     'SetDroneCards', 'get_Coins', 'set_Coins', 'get_Energy',
                     'set_Energy', 'GetDroneExp', 'SetDroneExp'):
            hits = [BD.short(row) for rows in BD.by_class().values() for row in rows
                    if BD.short(row) == name]
            self.assertTrue(hits, name)

    def test_the_action_ctor_is_unnamed_in_the_method_table(self):
        self.assertEqual(BD.name(ACTION_CTOR)['source'], 'generic-table')

    def test_the_helpers_are_pinned(self):
        self.assertEqual((BD.ALLOC, BD.CLASS_INIT, BD.ARRAY_NEW),
                         (17879616, 17879080, 17879196))


if __name__ == '__main__':
    unittest.main()
