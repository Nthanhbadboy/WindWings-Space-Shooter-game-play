"""Contracts for report 165: the quantity widget of the exchange popup.

164 stopped at `SetPopup`, which writes `count = 1` and prices the pack with
`rewards.price * count`. This report closes the loop on the widget itself:
`SetPopup` wires `new Action<float>(this, cell)` onto `Slider.onChange` (0x58),
`OnChange(float)` turns a slider amount into `count`, the two step buttons move
`Slider.value` and never `count`, and the buy/exit buttons hand `count` / `0` to
163's band lambda. Everything here is static.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import qty_widget as QW  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_qty_widget.json.gz'
PIN_BYTES = 6024
PIN_SHA = '97d7b0d81590fa335db2cb6df9abc5ddebe05112d152563e050c56398ed5b574'

CLICK = {'Arena_Shop': 'Popup_ArenaShopExchange', 'PVP_Shop': 'Popup_PVPShopExchange'}
ON_CHANGE = {'Arena_Shop': 22834804, 'PVP_Shop': 19887764}
SET_POPUP = {'Arena_Shop': 22835700, 'PVP_Shop': 19888660}
MINUS = {'Arena_Shop': 22837976, 'PVP_Shop': 19891096}
ADD = {'Arena_Shop': 22838032, 'PVP_Shop': 19891152}
BUY = {'Arena_Shop': 22837792, 'PVP_Shop': 19890912}
EXIT = {'Arena_Shop': 22837720, 'PVP_Shop': 19890840}
CELL = {'Arena_Shop': '0x2adb9e0', 'PVP_Shop': '0x2adbd38'}
GUARD_REGISTER = {'Arena_Shop': 'w20', 'PVP_Shop': 'w21'}


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(QW.build(), sort_keys=True, separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertEqual(blob['schema'], 1)

    def test_every_check_passed(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 50)
        self.assertTrue(all(row['passed'] for row in checks), checks)

    def test_totals(self):
        totals = payload()['totals']
        self.assertEqual((totals['shops'], totals['checks_passed'], totals['checks_total']),
                         (2, 50, 50))
        self.assertEqual(totals['onchange_calls'], 9)
        self.assertEqual(totals['buy_calls'], 3)


class Wiring(unittest.TestCase):
    """`SetPopup` is the only place the callback is installed."""

    def test_setpopup_rva(self):
        shops = payload()['shops']
        for klass, rva in SET_POPUP.items():
            self.assertEqual(shops[klass]['wiring']['setpopup_rva'], rva)

    def test_action_float_ctor_is_the_one_call(self):
        shops = payload()['shops']
        for klass in CLICK:
            ctor = shops[klass]['wiring']['action_ctor']
            self.assertEqual(ctor['target'], 25845244)
            self.assertEqual(ctor['op'], 'bl #0x18a5dfc')

    def test_the_slider_is_loaded_from_popup_0x48(self):
        shops = payload()['shops']
        for klass in CLICK:
            self.assertEqual(shops[klass]['wiring']['slider_load']['op'],
                             'ldr x25, [x19, #0x48]')
        self.assertEqual(shops['Arena_Shop']['slider']['on_change'], 'onChange')

    def test_the_action_lands_on_slider_0x58(self):
        shops = payload()['shops']
        for klass in CLICK:
            store = shops[klass]['wiring']['slider_store']
            self.assertEqual((store['offset'], store['field']), ('0x58', 'onChange'))

    def test_method_pointer_comes_from_a_static_cell(self):
        shops = payload()['shops']
        for klass, cell in CELL.items():
            self.assertEqual(shops[klass]['wiring']['action_cell']['op'], 'ldr x2, [x23]')
            self.assertEqual(shops[klass]['wiring']['action_cell_address'], cell)
        self.assertEqual(shops['Arena_Shop']['wiring']['action_target'], 'mov x1, x19')

    def test_exactly_one_void_float_method_per_popup(self):
        shops = payload()['shops']
        for klass in CLICK:
            methods = shops[klass]['wiring']['float_methods']
            self.assertEqual(len(methods), 1)
            self.assertEqual(methods[0]['signature'], 'void OnChange(float amount) { }')
            self.assertEqual(methods[0]['rva'], ON_CHANGE[klass])


class OnChange(unittest.TestCase):
    """`count = (int)round(amount / step)`, then four refreshes."""

    def test_rva_and_size(self):
        shops = payload()['shops']
        for klass, rva in ON_CHANGE.items():
            self.assertEqual(shops[klass]['on_change']['rva'], rva)
            self.assertEqual(shops[klass]['on_change']['size'], 896)
            self.assertEqual(shops[klass]['on_change']['signature'],
                             'void OnChange(float amount) { }')

    def test_divides_by_the_step_at_0x64(self):
        shops = payload()['shops']
        for klass in CLICK:
            row = shops[klass]['on_change']
            self.assertEqual(row['step_load']['op'], 'ldr s9, [x8, #0x64]')
            self.assertEqual(row['division']['op'], 'fdiv s9, s8, s9')
            self.assertEqual(shops[klass]['slider']['step'], 'step')

    def test_rounding_is_midpoint_to_even(self):
        shops = payload()['shops']
        for klass in CLICK:
            row = shops[klass]['on_change']
            self.assertEqual(row['round_helper']['target'], 43584368)
            self.assertEqual(row['midpoint_even']['op'], 'tst x8, #1')
            self.assertEqual(row['midpoint_halves'],
                             ['fmov d1, #-0.50000000', 'fmov d1, #0.50000000'])
            self.assertEqual(row['rounding_steps'], ['frintp d0, d0', 'frintm d0, d0'])
            self.assertEqual(row['round_select']['op'], 'fcsel d0, d0, d1, eq')

    def test_result_is_stored_into_count(self):
        shops = payload()['shops']
        for klass in CLICK:
            store = shops[klass]['on_change']['count_store']
            self.assertEqual((store['field'], store['op']), ('count', 'str w8, [x20, #0x58]!'))

    def test_the_cast_has_the_int_saturation_bounds(self):
        shops = payload()['shops']
        for klass in CLICK:
            self.assertEqual(shops[klass]['on_change']['saturate'],
                             ['mov w8, #-0x7fffffff', 'csinc w8, w8, w9, eq'])

    def test_cost_text_is_price_times_count(self):
        shops = payload()['shops']
        for klass in CLICK:
            row = shops[klass]['on_change']
            self.assertEqual(row['cost_mul']['op'], 'mul w8, w9, w8')
            self.assertEqual(row['price_load']['op'], 'ldr w9, [x9, #0x1c]')
            self.assertEqual(row['rewards_load']['op'], 'ldr x9, [x20, #8]')
            self.assertEqual(row['cost_format']['method'], 'Format')
            self.assertEqual((row['cost_label']['offset'], row['cost_label']['field']),
                             ('0x30', 'textCost'))

    def test_stock_text_is_a_five_part_concat(self):
        shops = payload()['shops']
        for klass in CLICK:
            stock = shops[klass]['on_change']['stock_text']
            self.assertEqual(stock['length'], 5)
            self.assertEqual(stock['concat']['method'], 'Concat')
            self.assertEqual(stock['max_stock_read']['op'], 'add x0, x19, #0x5c')

    def test_box_number_is_rewards_number_times_count(self):
        shops = payload()['shops']
        for klass in CLICK:
            row = shops[klass]['on_change']
            self.assertEqual(row['set_number']['target'], 20001584)
            self.assertEqual(row['set_number']['arg'], 'mul w1, w8, w9')
            self.assertEqual(row['number_load']['op'], 'ldr w8, [x8, #0x18]')

    def test_affordability_flag_is_one_when_short(self):
        shops = payload()['shops']
        for klass in CLICK:
            row = shops[klass]['on_change']
            self.assertEqual(row['afford_cost']['op'], 'mul w9, w21, w20')
            self.assertEqual(row['afford_cmp']['op'], 'cmp w19, w9')
            self.assertEqual(row['afford_one']['op'], 'fmov s1, #1.00000000')
            self.assertEqual(row['afford_select']['op'], 'fcsel s0, s1, s0, lt')
            self.assertEqual((row['material_source']['offset'], row['material_source']['field']),
                             ('0x40', 'btnIcon'))
            self.assertEqual(row['material_read']['method'], 'get_material')
            self.assertEqual(row['material_set']['method'], 'SetFloat')

    def test_each_shop_reads_its_own_medal(self):
        shops = payload()['shops']
        self.assertEqual(shops['Arena_Shop']['on_change']['medal']['method'], 'get_ArenaMedal')
        self.assertEqual(shops['PVP_Shop']['on_change']['medal']['method'], 'get_PvPMedal')

    def test_onchange_never_writes_maxstock(self):
        shops = payload()['shops']
        for klass in CLICK:
            self.assertTrue(shops[klass]['on_change']['writes_count'])
            self.assertFalse(shops[klass]['on_change']['writes_maxstock'])


class StepButtons(unittest.TestCase):
    """`Minus` / `Add` move the slider; `count` follows through `OnChange`."""

    def test_rva_and_size(self):
        shops = payload()['shops']
        for klass in CLICK:
            self.assertEqual(shops[klass]['minus']['rva'], MINUS[klass])
            self.assertEqual(shops[klass]['minus']['size'], 56)
            self.assertEqual(shops[klass]['add']['rva'], ADD[klass])
            self.assertEqual(shops[klass]['add']['size'], 60)

    def test_minus_clamps_at_zero(self):
        shops = payload()['shops']
        for klass in CLICK:
            row = shops[klass]['minus']
            self.assertEqual(row['value_load']['op'], 'ldr s0, [x0, #0x68]')
            self.assertEqual(row['compare'][0]['op'], 'fcmp s0, #0.0')
            self.assertTrue(row['guard']['op'].startswith('b.le'))
            self.assertEqual(row['delta']['value'], -1.0)
        self.assertEqual(payload()['shops']['Arena_Shop']['slider']['value'], 'value')

    def test_add_clamps_at_max_value(self):
        shops = payload()['shops']
        for klass in CLICK:
            row = shops[klass]['add']
            self.assertEqual(row['limit_load']['op'], 'ldr s1, [x0, #0x60]')
            self.assertEqual(row['compare'][-1]['op'], 'fcmp s0, s1')
            self.assertTrue(row['guard']['op'].startswith('b.pl'))
            self.assertEqual(row['delta']['value'], 1.0)
        self.assertEqual(payload()['shops']['Arena_Shop']['slider']['max_value'], 'maxValue')

    def test_both_tail_call_set_Value(self):
        shops = payload()['shops']
        for klass in CLICK:
            for key in ('minus', 'add'):
                row = shops[klass][key]['set_value']
                self.assertEqual(row['target'], 20903608)
                self.assertEqual(row['op'], 'b #0x13ef6b8')

    def test_neither_button_writes_count(self):
        shops = payload()['shops']
        for klass in CLICK:
            self.assertFalse(shops[klass]['minus']['writes_count'])
            self.assertFalse(shops[klass]['add']['writes_count'])


class BuyAndExit(unittest.TestCase):
    """One `Action<int>` field, two callers, two values."""

    def test_rva_and_size(self):
        shops = payload()['shops']
        for klass in CLICK:
            self.assertEqual(shops[klass]['buy']['rva'], BUY[klass])
            self.assertEqual(shops[klass]['buy']['size'], 184)
            self.assertEqual(shops[klass]['exit_']['rva'], EXIT[klass])
            self.assertEqual(shops[klass]['exit_']['size'], 72)

    def test_buy_charges_price_times_count(self):
        shops = payload()['shops']
        for klass in CLICK:
            row = shops[klass]['buy']
            self.assertEqual(row['cost_mul']['op'], 'mul w20, w8, w9')
            self.assertEqual(row['count_load']['field'], 'count')
            self.assertEqual(row['reward_load']['op'], 'ldr x8, [x19, #0x60]')
            self.assertEqual(row['price_load']['op'], 'ldr w8, [x8, #0x1c]')

    def test_buy_gates_on_the_medal(self):
        shops = payload()['shops']
        for klass in CLICK:
            row = shops[klass]['buy']
            self.assertEqual(row['gate']['op'], 'cmp w0, w20')
            self.assertTrue(row['gate_branch']['op'].startswith('b.ge'))

    def test_buy_hands_count_to_the_same_delegate_as_exit(self):
        shops = payload()['shops']
        for klass in CLICK:
            buy = shops[klass]['buy']
            exit_ = shops[klass]['exit_']
            self.assertEqual(buy['delegate_load']['op'], 'ldr x8, [x19, #0x50]')
            self.assertEqual(buy['invoke_arg']['op'], 'ldr w1, [x19, #0x58]')
            self.assertEqual(buy['invoke']['op'], 'blr x9')
            self.assertEqual(exit_['delegate_load']['op'], 'ldr x8, [x0, #0x50]')
            self.assertEqual(exit_['invoke_arg']['op'], 'mov w1, wzr')
            self.assertEqual(exit_['invoke']['op'], 'blr x9')

    def test_both_hide_the_popup_with_false(self):
        shops = payload()['shops']
        for klass in CLICK:
            for key in ('buy', 'exit_'):
                self.assertEqual(shops[klass][key]['hide']['method'], 'SetActive')
                self.assertEqual(shops[klass][key]['hide_arg']['op'], 'mov w1, wzr')

    def test_exit_never_reads_the_wallet_or_the_rewards(self):
        shops = payload()['shops']
        for klass in CLICK:
            exit_ = shops[klass]['exit_']
            self.assertIsNone(exit_['medal'])
            self.assertIsNone(exit_['reward_load'])
            self.assertIsNone(exit_['price_load'])


class SliderRange(unittest.TestCase):
    """What `SetPopup` leaves behind: 0..maxStock-1, step 1, value 0."""

    def test_maxvalue_is_maxstock_minus_one(self):
        shops = payload()['shops']
        for klass in CLICK:
            writes = shops[klass]['slider']['slider_writes']
            self.assertEqual([(row['offset'], row['field']) for row in writes],
                             [('0x64', 'step'), ('0x60', 'maxValue')])

    def test_step_is_one_and_value_starts_at_zero(self):
        shops = payload()['shops']
        for klass in CLICK:
            self.assertEqual(shops[klass]['wiring']['step_immediate'], 'mov w9, #0x3f800000')
            self.assertEqual(shops[klass]['wiring']['value_argument'], 'fmov s0, wzr')
            call = shops[klass]['slider']['slider_value_call']
            self.assertEqual((call['method'], call['target']), ('set_Value', 20903608))

    def test_slider_is_hidden_below_two_points_of_stock(self):
        shops = payload()['shops']
        for klass, register in GUARD_REGISTER.items():
            gate = shops[klass]['slider']['slider_gate']
            self.assertEqual(gate['source'], 'ldr %s, [x19, #0x5c]' % register)
            self.assertEqual(gate['op'], 'cmp %s, #1' % register)
            self.assertTrue(gate['branch'].startswith('b.le'))

    def test_popup_starts_count_at_one(self):
        shops = payload()['shops']
        for klass in CLICK:
            writes = {row['offset']: row['field']
                      for row in shops[klass]['slider']['count_written_after']}
            self.assertEqual(writes, {'0x50': 'onExit', '0x58': 'count',
                                      '0x60': 'rewards', '0x5c': 'maxStock'})


class CrossReport(unittest.TestCase):
    """The earlier pins still hold, and the guard of 163 is what closes this."""

    def test_164_popup_still_prices_with_count(self):
        previous = json.loads(gzip.decompress(
            (ROOT / 'datas/l2_535b0541_reward_pack.json.gz').read_bytes()))
        for klass in CLICK:
            self.assertEqual(previous['shops'][klass]['popup']['cost']['op'], 'mul w8, w9, w8')
            self.assertEqual([(row['offset'], row['field'])
                              for row in previous['shops'][klass]['popup']['writes']],
                             [('0x50', 'onExit'), ('0x58', 'count'),
                              ('0x60', 'rewards'), ('0x5c', 'maxStock')])

    def test_163_lambda_still_guards_count_below_one(self):
        previous = json.loads(gzip.decompress(
            (ROOT / 'datas/l2_535b0541_buy_delegate.json.gz').read_bytes()))
        for klass in CLICK:
            for band in ('player', 'drone', 'resource'):
                guard = previous['shops'][klass]['bands'][band]['lambda_']['guard']
                self.assertEqual(guard['cmp'], 'cmp w19, #1')
                self.assertTrue(guard['branch'].startswith('b.lt'))

    def test_the_verifier_api_agrees_with_the_artifact(self):
        blob = payload()
        self.assertEqual(QW.build()['totals'], blob['totals'])
        self.assertEqual(QW.build()['raw_scan']['hits'], blob['raw_scan']['hits'])


class RawScan(unittest.TestCase):
    """The one thing this report must not assume: `Slider.set_Value` is absent."""

    def test_no_slice_holds_the_slider_bodies(self):
        scan = payload()['raw_scan']
        self.assertEqual(scan['hits'], [])
        self.assertEqual(scan['scanned'], 8)
        self.assertGreater(scan['methods'], 2400)
        self.assertEqual(scan['wanted'], [20903608, 20903864, 20904492])

    def test_open_items_are_labelled_runtime(self):
        blob = payload()
        items = blob['open_items']
        self.assertEqual(len(items), 4)
        for row in items:
            self.assertTrue(row['item'])
            self.assertTrue(row['blocking'])
        self.assertIn('MODEL_NOT_MEASURED runtime', json.dumps(items))
        self.assertIn('set_Value', json.dumps(items))

    def test_confirmations_answer_the_open_questions(self):
        blob = payload()
        self.assertEqual(len(blob['confirmations']), 4)
        self.assertIn('reachable', blob['confirmations'][0]['result'])
        table = {row['control']: row for row in blob['table']}
        self.assertEqual(sorted(table),
                         ['ButtonAdd', 'ButtonBuy', 'ButtonExit', 'ButtonMinus',
                          'slider drag'])
        self.assertEqual(table['ButtonExit']['writes'], 'onExit(0), then SetActive(false)')


class Provenance(unittest.TestCase):
    def test_every_source_is_pinned(self):
        blob = payload()
        sources = blob['provenance']['sources']
        self.assertGreaterEqual(len(sources), 13)
        for row in sources:
            self.assertEqual(len(row['sha256']), 64)
            self.assertTrue((ROOT / row['path']).exists(), row['path'])

    def test_string_literal_count(self):
        self.assertEqual(payload()['provenance']['string_literals'], 15054)

    def test_constants(self):
        constants = payload()['constants']
        self.assertEqual(constants['set_number'], 20001584)
        self.assertEqual(constants['set_value'], 20903608)
        self.assertEqual(constants['action_float_ctor'], 25845244)
        self.assertEqual(constants['round_helper'], 43584368)
        self.assertEqual(constants['tint_property_cell'], '0x2adbea8')


if __name__ == '__main__':
    unittest.main()
