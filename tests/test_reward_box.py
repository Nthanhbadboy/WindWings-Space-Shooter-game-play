"""Contracts for report 166: what the exchange row draws.

165 ended at `Box_Rewards.SetNumber(rewards.number * count)`, 164 at
`SetInfo(box, icon, number, _isCards, scale, null)`. Both bodies are pinned, so
this report closes the visible half: how the number becomes text and a border
width, how `_isCards` toggles the cards badge, how the icon is scaled, what the
gray flag writes, and what a zero count does instead of printing "0".
Everything here is static.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import reward_box as RB  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_reward_box.json.gz'
PIN_BYTES = 6068
PIN_SHA = '9b2a4186fd0c5cc796a1e648210200fc28ab96d55c2a8ba07349d9e12ed718d2'

FIELD_NAMES = {'0x20': 'textNumber', '0x28': 'borderNumber', '0x30': 'grayRenderers',
               '0x38': 'boxRenderer', '0x40': 'iconRenderer', '0x48': 'objCards',
               '0x50': 'textBonus', '0x58': 'xChar', '0x5c': 'yChar', '0x60': 'id',
               '0x64': 'number'}
METHODS = {19990656: 420, 20001844: 280, 20001584: 260,
           20002124: 28, 20002152: 84, 20002236: 268, 20002504: 20}


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(RB.build(), sort_keys=True, separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        self.assertEqual(payload()['evidence'], 'STATIC_ONLY_ORIGINAL_APK')

    def test_every_check_passed(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 39)
        self.assertTrue(all(row['passed'] for row in checks), checks)

    def test_totals(self):
        totals = payload()['totals']
        self.assertEqual((totals['fields'], totals['methods']), (11, 7))
        self.assertEqual((totals['set_number_instructions'], totals['set_info_instructions'],
                          totals['get_short_instructions']), (65, 105, 70))


class ClassShape(unittest.TestCase):
    def test_field_map(self):
        blob = payload()
        fields = {hex(row['offset']): row['name'] for row in blob['class_']['fields']}
        self.assertEqual(fields, FIELD_NAMES)

    def test_rendered_offsets(self):
        rendered = {row['offset']: row['field'] for row in payload()['class_']['rendered']}
        self.assertEqual(rendered, FIELD_NAMES)

    def test_method_sizes(self):
        sizes = {row['rva']: row['size'] if 'size' in row else None
                 for row in payload()['class_']['methods']}
        self.assertEqual(sorted(sizes), sorted(METHODS))
        for rva, size in METHODS.items():
            row = next(entry for entry in RB.RP.class_block(RB.CLASS)['methods']
                       if entry['rva'] == rva)
            self.assertEqual(RB.BD.method(RB.CLASS, rva)['size'], size, row['signature'])


class SetNumber(unittest.TestCase):
    def test_rva_and_size(self):
        row = payload()['set_number']
        self.assertEqual((row['rva'], row['size'], row['instructions']),
                         (20001584, 260, 65))

    def test_stores_the_number_field(self):
        row = payload()['set_number']
        self.assertEqual((row['store']['offset'], row['store']['field']), ('0x64', 'number'))
        self.assertEqual(row['store']['op'], 'str w19, [x20, #0x64]')

    def test_only_one_instance_field_is_written(self):
        self.assertEqual(payload()['set_number']['writes_count_like_fields'], ['0x64'])

    def test_text_is_prefix_plus_short_number(self):
        row = payload()['set_number']
        self.assertEqual(row['prefix_cell'], '0x2ade140')
        self.assertEqual(row['short_number']['target'], 20001844)
        self.assertEqual(row['concat']['target'], 33439876)

    def test_text_goes_through_the_virtual_setter(self):
        row = payload()['set_number']
        self.assertEqual(row['text_receiver']['op'], 'ldr x8, [x20, #0x20]')
        self.assertEqual(row['text_slot']['op'], 'ldr x10, [x9, #0x518]')
        self.assertEqual(row['virtual_call']['op'], 'blr x10')

    def test_border_width_formula(self):
        row = payload()['set_number']
        self.assertEqual(row['chars']['op'], 'ldp s0, s1, [x20, #0x58]')
        self.assertEqual(row['length_load']['op'], 'ldr w8, [x21, #0x10]')
        self.assertEqual(row['length_plus_one']['op'], 'add w8, w8, #1')
        self.assertEqual(row['scale_mul']['op'], 'fmul s0, s0, s3')
        self.assertEqual(row['scale_add']['op'], 'fadd s0, s0, s2')
        self.assertEqual(row['pad_rodata']['op'], 'ldr s2, [x9, #0xc78]')
        self.assertEqual(row['pad_rodata']['page'], 0x756000)

    def test_width_is_clamped_at_two(self):
        row = payload()['set_number']
        self.assertEqual(row['clamp_literal']['op'], 'fmov s2, #2.00000000')
        self.assertEqual(row['clamp']['op'], 'fminnm s0, s0, s2')

    def test_size_lands_on_the_border_renderer(self):
        row = payload()['set_number']
        self.assertEqual(row['set_size']['target'], 41463348)
        self.assertEqual(row['size_receiver']['op'], 'ldr x0, [x20, #0x28]')

    def test_zero_number_disables_the_border(self):
        row = payload()['set_number']
        self.assertEqual(row['zero_cmp']['op'], 'cmp w19, #0')
        self.assertEqual(row['zero_cset']['op'], 'cset w1, gt')
        self.assertEqual(row['set_enabled']['target'], 41322360)


class GetShortNumber(unittest.TestCase):
    def test_thresholds_are_immediates(self):
        row = payload()['short_number']
        self.assertEqual(row['thresholds'], [999999, 99999999, 999999999])
        self.assertEqual(row['threshold_ops'][0], ['mov w8, #0x423f', 'movk w8, #0xf, lsl #16'])

    def test_four_ladder_steps(self):
        row = payload()['short_number']
        self.assertEqual([entry['target'] for entry in row['branches']],
                         [20002012, 20002028, 20002068])
        self.assertEqual([entry['target'] for entry in row['ladder']],
                         [20002012, 20002028, 20002068, 20001980])

    def test_plain_path_uses_int_tostring(self):
        row = payload()['short_number']
        self.assertEqual(row['int_tostring']['target'], 34616120)
        self.assertEqual(row['ladder'][0]['head'], 'add x0, sp, #0x1c')

    def test_thousand_step_uses_the_float_immediate(self):
        row = payload()['short_number']
        self.assertEqual(row['thousand_immediate']['op'], 'mov w8, #0x447a0000')
        self.assertEqual(row['ladder'][1]['head'], 'adrp x9, #0x2ae1000')

    def test_top_steps_divide_by_rodata(self):
        row = payload()['short_number']
        self.assertEqual(sorted(entry['op'] for entry in row['rodata']),
                         ['ldr s1, [x8, #0xb8]', 'ldr s1, [x8, #0xdf8]'])
        self.assertEqual(row['ladder'][2]['head'], 'adrp x8, #0x757000')
        self.assertEqual(row['ladder'][3]['head'], 'adrp x8, #0x756000')

    def test_one_shared_float_tostring_call_site(self):
        row = payload()['short_number']
        self.assertEqual(len(row['float_tostring']), 1)
        self.assertEqual(row['float_tostring'][0]['op'], 'bl #0x21172b4')

    def test_three_distinct_format_cells(self):
        self.assertEqual(sorted(payload()['short_number']['format_cells']),
                         ['0x2ae1388', '0x2ae1390', '0x2ae1398'])


class SetInfo(unittest.TestCase):
    def test_rva_and_size(self):
        row = payload()['set_info']
        self.assertEqual((row['rva'], row['size'], row['instructions']),
                         (19990656, 420, 105))

    def test_argument_registers(self):
        args = payload()['set_info']['arguments']
        self.assertEqual(args['box']['op'], 'mov x24, x1')
        self.assertEqual(args['icon']['op'], 'mov x23, x2')
        self.assertEqual(args['number']['op'], 'mov w19, w3')
        self.assertEqual(args['is_cards']['op'], 'mov w22, w4')
        self.assertEqual(args['scale']['op'], 'mov v8.16b, v0.16b')
        self.assertEqual(args['bonus']['op'], 'mov x21, x5')

    def test_both_sprites_are_written(self):
        sprites = payload()['set_info']['sprites']
        self.assertEqual([row['receiver']['op'] for row in sprites],
                         ['ldr x0, [x20, #0x38]', 'ldr x0, [x20, #0x40]'])
        self.assertEqual([row['call']['target'] for row in sprites],
                         [41463136, 41463136])

    def test_icon_scaled_on_x_and_y_only(self):
        row = payload()['set_info']
        self.assertEqual(row['scale_call']['target'], 41457984)
        self.assertEqual([entry['op'] for entry in row['scale_args']],
                         ['mov v0.16b, v8.16b', 'mov v1.16b, v8.16b', 'fmov s2, #1.00000000'])

    def test_cards_badge_is_the_isCards_bit(self):
        row = payload()['set_info']
        self.assertEqual(row['cards_mask']['op'], 'and w1, w22, #1')
        self.assertEqual(row['cards_receiver']['op'], 'ldr x0, [x20, #0x48]')
        self.assertEqual(row['cards_active']['target'], 41424900)

    def test_bonus_text_is_gated(self):
        row = payload()['set_info']
        self.assertEqual(row['bonus_null_check']['target'], 33476612)
        self.assertEqual(row['bonus_receiver']['op'], 'ldr x8, [x20, #0x50]')

    def test_only_the_number_field_is_written_here(self):
        self.assertEqual(payload()['set_info']['field_stores'], ['0x64'])

    def test_tail_calls_setnumber(self):
        tail = payload()['set_info']['tail_number']
        self.assertEqual((tail['target'], tail['op']), (20001584, 'b #0x1313330'))

    def test_bonus_branches(self):
        row = payload()['set_info']
        self.assertEqual([entry['target'] for entry in row['bonus_branch']],
                         [19991040, 19990960])
        self.assertEqual(row['bonus_paths']['empty_hide']['op'], 'mov w1, wzr')
        self.assertEqual(row['bonus_paths']['filled_show']['op'], 'mov w1, #1')
        self.assertEqual(row['bonus_shown'][-1]['target'], 41424900)

    def test_the_popup_always_passes_a_null_bonus(self):
        row = payload()['popup']
        self.assertEqual(row['tail_jump']['target'], 19990656)
        self.assertEqual([entry['op'] for entry in row['before'][-3:]],
                         ['mov x5, xzr', 'mov x6, xzr', 'ldp x30, x23, [sp], #0x30'])


class SetGrayScale(unittest.TestCase):
    def test_gray_becomes_one_or_zero(self):
        row = payload()['set_gray']
        self.assertEqual(row['flag_test']['op'], 'tst w20, #1')
        self.assertEqual(row['one']['op'], 'fmov s1, #1.00000000')
        self.assertEqual(row['zero']['op'], 'fmov s0, wzr')
        self.assertEqual(row['flag_select']['op'], 'fcsel s8, s1, s0, ne')

    def test_three_renderers_are_grayed(self):
        row = payload()['set_gray']
        self.assertEqual(len(row['set_float']), 3)
        self.assertEqual([entry['op'] for entry in row['receivers']],
                         ['ldr x0, [x19, #0x40]', 'ldr x0, [x19, #0x38]'])
        self.assertEqual(row['array']['length']['op'], 'ldr w8, [x19, #0x18]')
        self.assertEqual(row['array']['element']['op'], 'ldr x0, [x22, x21, lsl #3]')

    def test_the_same_shader_cell_as_165(self):
        row = payload()['set_gray']
        self.assertEqual(row['tint_cell'], '0x2adbea8')
        self.assertTrue(row['value_matches_165'])


class Helpers(unittest.TestCase):
    def test_set_box_sprite(self):
        row = payload()['helpers']['set_box']
        self.assertEqual(row['receiver']['op'], 'ldr x0, [x0, #0x38]')
        self.assertEqual(row['tail']['op'], 'b #0x278ad60')

    def test_set_icon_sprite(self):
        row = payload()['helpers']['set_icon']
        self.assertEqual(row['receiver']['op'], 'ldr x0, [x0, #0x40]')
        self.assertEqual(row['scale']['op'], 'fmov s2, #1.00000000')
        self.assertIn(41457984, [entry['target'] for entry in row['calls']])

    def test_ctor_seeds_both_char_floats_from_one_double(self):
        row = payload()['helpers']['ctor']
        self.assertEqual(row['rodata']['op'], 'ldr d0, [x8, #0xbb8]')
        self.assertEqual(row['page'], 0x757000)
        self.assertEqual(row['store']['op'], 'str d0, [x0, #0x58]')
        self.assertEqual(row['tail']['op'], 'b #0x2782ba0')


class CrossReport(unittest.TestCase):
    def test_165_calls_this_setnumber(self):
        previous = json.loads(gzip.decompress(
            (ROOT / 'datas/l2_535b0541_qty_widget.json.gz').read_bytes()))
        self.assertEqual(previous['constants']['set_number'], 20001584)
        self.assertEqual(previous['shops']['Arena_Shop']['on_change']['set_number']['target'],
                         20001584)

    def test_165s_tint_is_this_same_cell(self):
        previous = json.loads(gzip.decompress(
            (ROOT / 'datas/l2_535b0541_qty_widget.json.gz').read_bytes()))
        self.assertEqual(previous['constants']['tint_property_cell'], '0x2adbea8')

    def test_164_still_draws_nine_pads(self):
        previous = json.loads(gzip.decompress(
            (ROOT / 'datas/l2_535b0541_reward_pack.json.gz').read_bytes()))
        self.assertEqual(previous['totals']['pads'], 9)
        self.assertEqual(previous['totals']['packs'], 8)


class OpenItems(unittest.TestCase):
    def test_four_runtime_items(self):
        items = payload()['open_items']
        self.assertEqual(len(items), 4)
        self.assertIn('MODEL_NOT_MEASURED runtime', json.dumps(items))

    def test_confirmations(self):
        rows = payload()['confirmations']
        self.assertEqual(len(rows), 4)
        self.assertIn('never renders', rows[0]['result'])

    def test_unknowns_are_named(self):
        blob = payload()
        constants = blob['constants']
        self.assertEqual(constants['tint_cell'], '0x2adbea8')
        self.assertEqual(constants['prefix_cell'], '0x2ade140')


if __name__ == '__main__':
    unittest.main()
