"""Contracts for report 167: who draws a reward row.

166 decoded what `Box_Rewards` draws. This one is the xref half: every `bl`/`b`
to the class's seven methods across the eight pinned slices, deduped because the
slices overlap, with the argument registers read at each call site. The point of
the report is that `SetInfo` is not a one-screen widget — six classes and ten
methods draw a row — and that `SetGrayScale` has no caller at all in the sample.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import reward_box_callers as RC  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_reward_box_callers.json.gz'
PIN_BYTES = 6926
PIN_SHA = '7f42bf4bac4a7606dc5e194852f4800e4f65bc6b736a4dd7b16d3366dec2644b'

METHODS = {'SetInfo': 19990656, 'SetNumber': 20001584, 'GetShortNumber': 20001844,
           'SetBoxSprite': 20002124, 'SetIconSprite': 20002152,
           'SetGrayScale': 20002236, '.ctor': 20002504}
SITES = {'SetInfo': 30, 'SetNumber': 4, 'GetShortNumber': 1, 'SetBoxSprite': 0,
         'SetIconSprite': 0, 'SetGrayScale': 0, '.ctor': 0}
CLASSES = ['Board_EventSeasonPass', 'Board_PVP', 'Board_QuestRewards',
           'Board_QuestRewards.<OpenBox>d__43', 'Popup_ArenaShopExchange',
           'Popup_PVPRewards', 'Popup_PVPShopExchange', 'TimeFreeRewardPack']


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


def info_sites():
    return [row for row in payload()['calls'] if row['method'] == 'SetInfo']


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        _, packed = RC.build(None)
        self.assertEqual(packed, ARTIFACT.read_bytes())

    def test_static_only(self):
        self.assertEqual(payload()['evidence'], 'STATIC_ONLY_ORIGINAL_APK')

    def test_every_check_passed(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 39)
        self.assertTrue(all(row['passed'] for row in checks),
                        [row['name'] for row in checks if not row['passed']])

    def test_totals(self):
        totals = payload()['totals']
        self.assertEqual(totals['sites'], 35)
        self.assertEqual(totals['raw_hits'], 38)
        self.assertEqual((totals['unique_methods'], totals['multi_slice_methods'],
                          totals['slices']), (1788, 709, 8))


class TargetTable(unittest.TestCase):
    def test_seven_targets(self):
        targets = payload()['targets']
        self.assertEqual(sorted(targets), sorted(METHODS))
        for name, rva in METHODS.items():
            self.assertEqual(targets[name]['rva'], rva)

    def test_site_counts(self):
        targets = payload()['targets']
        self.assertEqual({name: row['sites'] for name, row in targets.items()}, SITES)

    def test_raw_hits_are_never_fewer_than_deduped_sites(self):
        for row in payload()['targets'].values():
            self.assertGreaterEqual(row['raw_sites'], row['sites'])

    def test_setinfo_overlap_is_three_sites(self):
        row = payload()['targets']['SetInfo']
        self.assertEqual((row['raw_sites'], row['sites']), (33, 30))

    def test_only_the_two_popups_tail_call_setinfo(self):
        self.assertEqual(payload()['targets']['SetInfo']['tails'], 2)

    def test_setnumber_has_exactly_one_tail(self):
        self.assertEqual(payload()['targets']['SetNumber']['tails'], 1)

    def test_four_methods_are_uncalled_in_the_sample(self):
        targets = payload()['targets']
        for name in ('SetBoxSprite', 'SetIconSprite', 'SetGrayScale', '.ctor'):
            self.assertEqual(targets[name]['sites'], 0, name)
            self.assertEqual(targets[name]['classes'], [])

    def test_setinfo_classes(self):
        self.assertEqual(payload()['targets']['SetInfo']['classes'], CLASSES)


class CallSites(unittest.TestCase):
    def test_sorted_by_target_then_caller(self):
        rows = payload()['calls']
        self.assertEqual(rows, sorted(rows, key=lambda row: (row['target'],
                                                             row['caller'], row['call'])))

    def test_no_duplicate_rows(self):
        keys = [(row['target'], row['caller'], row['call']) for row in payload()['calls']]
        self.assertEqual(len(keys), len(set(keys)))

    def test_every_row_names_its_slices(self):
        for row in payload()['calls']:
            self.assertTrue(row['slices'])
            self.assertTrue(set(row['slices']) <= {'arena-pvp-535b0541', 'box-draw-535b0541',
                                                   'key-grant-535b0541', 'key-jump-535b0541',
                                                   'meta-rewards-535b0541',
                                                   'pack-index-535b0541',
                                                   'pvp-dispatch-535b0541',
                                                   'pvp-rules-535b0541'})

    def test_overlap_shows_up_as_multi_slice_rows(self):
        overlaps = [row for row in payload()['calls'] if len(row['slices']) > 1]
        self.assertTrue(overlaps)
        self.assertTrue(all(row['class_name'] in ('Board_PVP', 'TimeFreeRewardPack')
                            for row in overlaps))

    def test_setnumber_rows(self):
        rows = [(row['class_name'], row['call'])
                for row in payload()['calls'] if row['method'] == 'SetNumber']
        self.assertEqual(rows, [('Board_EventSeasonPass', 19440912),
                                ('Popup_PVPShopExchange', 19888504),
                                ('Box_Rewards', 19991068),
                                ('Popup_ArenaShopExchange', 22835544)])

    def test_getshortnumber_row(self):
        row = next(row for row in payload()['calls']
                   if row['method'] == 'GetShortNumber')
        self.assertEqual((row['class_name'], row['call']), ('Box_Rewards', 20001656))

    def test_the_quest_state_machine_owns_thirteen_rows(self):
        rows = [row for row in info_sites()
                if row['class_name'] == 'Board_QuestRewards.<OpenBox>d__43']
        self.assertEqual(len(rows), 13)
        self.assertEqual({row['caller'] for row in rows}, {19996384})

    def test_the_event_pass_board_owns_nine_rows_over_two_methods(self):
        rows = [row for row in info_sites() if row['class_name'] == 'Board_EventSeasonPass']
        self.assertEqual(len(rows), 9)
        self.assertEqual({row['caller'] for row in rows}, {19439716, 19450080})

    def test_the_two_popups_pass_a_product(self):
        rows = [row for row in payload()['calls'] if row['method'] == 'SetNumber'
                and row['class_name'].startswith('Popup_')]
        self.assertEqual([row['arguments']['number']['op'] for row in rows],
                         ['mul w1, w8, w9'] * 2)

    def test_the_setinfo_tail_row_is_method_level(self):
        row = next(row for row in payload()['calls']
                   if row['method'] == 'SetNumber' and row['class_name'] == 'Box_Rewards')
        self.assertTrue(row['tail'])
        self.assertEqual(row['caller'], METHODS['SetInfo'])


class Arguments(unittest.TestCase):
    def test_every_setinfo_site_passes_a_null_bonus(self):
        self.assertEqual(payload()['arguments']['bonus'], {'zero': 30})
        for row in info_sites():
            self.assertEqual(row['arguments']['bonus']['op'], 'mov x5, xzr')

    def test_isCards_is_mostly_a_folded_literal(self):
        self.assertEqual(payload()['arguments']['isCards'],
                         {'zero (wzr, false)': 23, 'literal': 6, 'flag': 1})

    def test_the_one_flag_badge_is_board_pvp(self):
        rows = [row for row in info_sites()
                if row['arguments']['isCards']['kind'] == 'flag']
        self.assertEqual([row['class_name'] for row in rows], ['Board_PVP'])
        self.assertEqual(rows[0]['arguments']['isCards']['op'], 'cset w4, eq')

    def test_scale_literals_and_rodata(self):
        scale = payload()['arguments']['scale']
        self.assertEqual(scale, {'float 1.00000000': 17, 'float 1.25000000': 6,
                                 'float 1.50000000': 1, 'rodata': 5, 'field': 1})

    def test_the_two_rodata_scales(self):
        cells = {row['arguments']['scale']['detail'] for row in info_sites()
                 if row['arguments']['scale']['kind'] == 'rodata'}
        self.assertEqual(cells, {'0x756c14', '0x756f10'})

    def test_number_sources(self):
        self.assertEqual(payload()['arguments']['number'],
                         {'local': 19, 'literal 1': 3, 'field': 5, 'load': 2,
                          'call-return': 1})

    def test_the_one_call_return_number(self):
        row = next(row for row in info_sites()
                   if row['arguments']['number']['kind'] == 'call-return')
        self.assertEqual(row['class_name'], 'Board_EventSeasonPass')
        self.assertEqual(row['call'], 19452264)
        self.assertEqual(row['arguments']['number']['detail']['rva'], 26393436)

    def test_the_field_numbers_are_class_fields_not_cells(self):
        for row in info_sites():
            profile = row['arguments']['number']
            if profile['kind'] != 'field':
                continue
            self.assertIsInstance(profile['detail'], dict)
            self.assertNotIn('0x2a', profile['detail']['offset'])

    def test_three_sites_hardcode_one(self):
        rows = [row for row in info_sites()
                if row['arguments']['number']['kind'] == 'literal']
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(row['arguments']['number']['detail'] == 1 for row in rows))

    def test_three_sites_pass_a_null_box_sprite(self):
        rows = [row for row in info_sites()
                if row['arguments']['box']['kind'] == 'zero']
        self.assertEqual(len(rows), 3)
        self.assertEqual([row['call'] for row in rows], [19452264, 20000140, 20000296])


class PrefixChain(unittest.TestCase):
    def test_two_dereferences(self):
        chain = payload()['prefix']
        self.assertEqual(chain['cell'], '0x2ade140')
        self.assertEqual((chain['page']['rva'], chain['first_load']['rva'],
                          chain['second_load']['rva']), (20001644, 20001648, 20001660))

    def test_the_concat_is_string_string(self):
        chain = payload()['prefix']
        self.assertEqual(chain['concat']['target'], 33439876)
        self.assertIn('Concat(string str0, string str1)', chain['concat']['signature'])
        self.assertEqual(chain['move_to_x0']['rva'], 20001672)

    def test_getshortnumber_never_reads_this(self):
        chain = payload()['prefix']
        self.assertEqual(chain['get_short_reads_this'], 0)
        self.assertEqual(chain['get_short_first_x0_write']['rva'], 20001876)
        self.assertEqual(chain['x0_writes_before_the_call'], [])


class LiveDerivation(unittest.TestCase):
    def test_recomputed_sites_match_the_artifact(self):
        live = RC.call_sites()
        self.assertEqual([(row['target'], row['caller'], row['call']) for row in live],
                         [(row['target'], row['caller'], row['call'])
                          for row in payload()['calls']])

    def test_recomputed_argument_table_matches(self):
        self.assertEqual(RC.argument_table(RC.call_sites()), payload()['arguments'])

    def test_every_target_still_resolves_to_box_rewards(self):
        for _, rva in RC.TARGETS:
            self.assertEqual(RC.BD.name(rva)['class_name'], 'Box_Rewards')

    def test_method_sizes_are_the_166_ones(self):
        sizes = {row['rva']: row['size'] for row in payload()['class_']['methods']}
        self.assertEqual(sizes, {19990656: 420, 20001584: 260, 20001844: 280,
                                 20002124: 28, 20002152: 84, 20002236: 268,
                                 20002504: 20})


class CrossReport(unittest.TestCase):
    def previous(self, name):
        return json.loads(gzip.decompress((ROOT / name).read_bytes()))

    def test_166_constants(self):
        box = self.previous('datas/l2_535b0541_reward_box.json.gz')
        self.assertEqual(box['constants']['set_info'], 19990656)
        self.assertEqual(box['constants']['get_short'], 20001844)
        self.assertEqual(box['popup']['tail_jump']['target'], 19990656)

    def test_165_onchange_call_sites(self):
        qty = self.previous('datas/l2_535b0541_qty_widget.json.gz')
        self.assertEqual(qty['shops']['Arena_Shop']['on_change']['set_number']['rva'], 22835544)
        self.assertEqual(qty['shops']['PVP_Shop']['on_change']['set_number']['rva'], 19888504)

    def test_165_writes_the_grey_flag_inline(self):
        qty = self.previous('datas/l2_535b0541_qty_widget.json.gz')
        calls = qty['shops']['Arena_Shop']['on_change']['calls']
        self.assertIn('SetFloat', [call['method'] for call in calls])

    def test_164_totals_untouched(self):
        pack = self.previous('datas/l2_535b0541_reward_pack.json.gz')
        self.assertEqual((pack['totals']['pads'], pack['totals']['packs']), (9, 8))


class OpenItems(unittest.TestCase):
    def test_four_open_items(self):
        items = payload()['open_items']
        self.assertEqual(len(items), 4)

    def test_the_prefix_cell_is_flagged(self):
        items = json.dumps(payload()['open_items'])
        self.assertIn('0x2ade140', items)
        self.assertIn('MODEL_NOT_MEASURED', items)

    def test_the_sample_warning_is_explicit(self):
        items = [row['item'] for row in payload()['open_items']]
        self.assertTrue(any('outside the eight slices' in item for item in items))

    def test_confirmations(self):
        rows = payload()['confirmations']
        self.assertEqual(len(rows), 4)
        self.assertIn('mul w1, w8, w9', json.dumps(rows))


if __name__ == '__main__':
    unittest.main()
