"""Contracts for report 171: `Board_PVP.SetupHunters` end to end.

169 mapped the six arrays to their fields. This report reads the method that spends
them: twelve points, six rewards, one `SetInfo` per odd point, and a "collected" flag
that turns out to be local device state rather than the reward arrays.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import pvp_setup_hunters as PS  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_pvp_setup_hunters.json.gz'
PIN_BYTES = 5170
PIN_SHA = '0d60c01519acaef1b76329ec72ffa554db22e5516d0012c123f4298d6013e0e1'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        _, packed = PS.build(None)
        self.assertEqual(packed, ARTIFACT.read_bytes())

    def test_static_only(self):
        self.assertEqual(payload()['evidence'], 'STATIC_ONLY_ORIGINAL_APK')

    def test_every_check_passed(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 26)
        self.assertTrue(all(row['passed'] for row in checks),
                        [row['name'] for row in checks if not row['passed']])

    def test_totals(self):
        totals = payload()['totals']
        self.assertEqual((totals['landmarks'], totals['calls'], totals['points'],
                          totals['rewards'], totals['checks_total']), (35, 23, 12, 6, 26))


class Fields(unittest.TestCase):
    def test_the_six_pov_fields(self):
        fields = payload()['class_']['board_pvp']
        self.assertEqual({offset: row['name'] for offset, row in fields.items()},
                         {'0x170': 'allDieObjects', '0x188': 'lineProgress',
                          '0x190': 'allPoints', '0x198': 'rewardIndexs',
                          '0x1a0': 'rewardValues', '0x1a8': 'rewardScales'})

    def test_allpoints_is_a_winpoint_array(self):
        self.assertEqual(payload()['class_']['board_pvp']['0x190']['declared'], 'WinPoint[]')

    def test_the_five_winpoint_fields(self):
        fields = payload()['class_']['winpoint']
        self.assertEqual({offset: row['name'] for offset, row in fields.items()},
                         {'0x20': 'textNumber', '0x28': 'boxRewards', '0x30': 'anim',
                          '0x38': 'collectedObject', '0x40': 'onClick'})

    def test_the_box_reward_holder(self):
        self.assertEqual(payload()['class_']['winpoint']['0x28']['declared'], 'Box_Rewards')


class Rows(unittest.TestCase):
    def test_twelve_points_six_rewards(self):
        table = payload()['rows']['table']
        self.assertEqual(len(table), 12)
        self.assertEqual([row['i'] for row in table], list(range(12)))
        self.assertEqual([row['reward_index'] for row in table if row['parity'] == 'odd'],
                         [0, 1, 2, 3, 4, 5])

    def test_even_points_carry_no_reward(self):
        self.assertEqual([row for row in payload()['rows']['table']
                          if row['parity'] == 'even' and row['reward_index'] is not None], [])

    def test_the_point_parts(self):
        rows = payload()['rows']
        self.assertEqual(rows['box'], 'allPoints[i].boxRewards (+0x28)')
        self.assertEqual(rows['collected'], 'allPoints[i].collectedObject (+0x38)')
        self.assertEqual(rows['click'], 'allPoints[i].onClick (+0x40)')


class Calls(unittest.TestCase):
    def test_setinfo_is_called_once_on_the_box(self):
        self.assertEqual(payload()['calls']['Box_Rewards.SetInfo'], [19792252])

    def test_the_sprite_comes_from_the_reward_id(self):
        self.assertEqual(payload()['calls']['DataShopPack.GetBoxSpriteGeneral'], [19792180])

    def test_setactive_five_times(self):
        self.assertEqual(len(payload()['calls']['GameObject.SetActive']), 5)

    def test_the_collected_marker_uses_the_static_iscollected(self):
        self.assertEqual(payload()['calls']['Board_PVP.IsCollected'], [19792380])

    def test_the_click_delegate_is_built_with_this(self):
        self.assertEqual(payload()['calls']['Action<WinPoint>..ctor'], [19792464])

    def test_the_progress_getter_is_asked_four_times(self):
        self.assertEqual(payload()['calls']['Board_PVP.get_SeasonProgress'],
                         [19792272, 19792512, 19792616, 19792692])

    def test_the_two_progress_children(self):
        self.assertEqual(payload()['calls']['Transform.GetChild'], [19792596, 19792672])

    def test_landmarks_all_match(self):
        self.assertEqual([row for row in payload()['landmarks'] if not row['pass_']], [])


class Semantics(unittest.TestCase):
    def test_icon_switch_has_two_named_ids_and_a_default(self):
        switch = payload()['icon_switch']
        self.assertEqual((switch['id_14'], switch['id_15']), ('+0x58', '+0x50'))
        self.assertIn('[list + id*8 + 0x20]', switch['other'])

    def test_the_card_flag_is_the_low_bit_pair(self):
        self.assertEqual(payload()['icon_switch']['is_cards'], '(id & 0xfffffffe) == 14')

    def test_setinfo_receives_the_three_arrays(self):
        arguments = [row['argument'] for row in payload()['setinfo']['arguments']]
        self.assertEqual(arguments, ['box', 'number', 'isCards', 'scale', 'icon', 'sprite',
                                     'call'])
        self.assertEqual(payload()['setinfo']['rva'], '0x1310880')

    def test_every_setinfo_argument_instruction_is_pinned(self):
        self.assertEqual([row for row in payload()['setinfo']['arguments']
                          if not row['pass_']], [])

    def test_the_dies_loop_bounds_on_season_dies(self):
        self.assertEqual(payload()['dies']['rule'], 'SetActive(i < get_SeasonDies())')
        self.assertEqual(payload()['dies']['getter'], 19784352)


class Collected(unittest.TestCase):
    def test_iscollected_does_not_read_the_reward_arrays(self):
        self.assertEqual(payload()['collected']['reads_reward_arrays'], 0)

    def test_it_reads_playerpreferences(self):
        classes = [row['class_name'] for row in payload()['collected']['calls']]
        self.assertIn('PlayerPreferences', classes)

    def test_the_key_is_a_prefix_plus_the_index(self):
        self.assertEqual(payload()['collected']['prefix_cell'], '0x2adffa8')
        names = [row['name'] for row in payload()['collected']['calls'] if row['name']]
        self.assertEqual(names, ['public override string ToString() { }',
                                 'public static string Concat(string str0, string str1) { }',
                                 'public static int GetInt(string key, int valueDefault) { }'])

    def test_collected_means_the_saved_int_is_one(self):
        self.assertEqual(payload()['collected']['compare'], ['cmp w0, #1'])
        self.assertEqual(payload()['collected']['returns'], ['cset w0, eq'])


class Residue(unittest.TestCase):
    def test_170_left_four_open_items(self):
        self.assertEqual(len(payload()['open_items']), 4)

    def test_the_amount_and_scale_stay_unbound(self):
        items = [row['item'] for row in payload()['open_items']]
        self.assertIn('rewardValues / rewardScales bytes', items)

    def test_d78_is_declared_not_consulted(self):
        self.assertIn('Board_PVP.<GetPvPUserCachingDatas>d__78.MoveNext',
                      payload()['boundary']['not_consulted'])


class LiveDerivation(unittest.TestCase):
    def test_fields_recompute(self):
        self.assertEqual(PS.fields(), payload()['class_'])

    def test_calls_recompute(self):
        self.assertEqual(PS.callers(), payload()['calls'])

    def test_collected_recompute(self):
        self.assertEqual(PS.collected(), payload()['collected'])


if __name__ == '__main__':
    unittest.main()
