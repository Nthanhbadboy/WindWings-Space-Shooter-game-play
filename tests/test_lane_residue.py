"""Contracts for report 168: the residue sweep of lane #29/#30.

167 closed the xref half of the reward row. What was left in the lane is the list
of 56 open items in `open_items_audit`. This report sweeps it once: two items are
closed with code that was already pinned, two rationales are corrected because the
body being absent is not the same as the call being absent, one data claim is
settled from the extracted assets, and the rest is named as blocked.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import lane_residue as LR  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_lane_residue.json.gz'
PIN_BYTES = 4902
PIN_SHA = 'bae0e6da7afa9da0bce8f005ef505af523e1c82742e505cb1edbffb6772ad402'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


def window():
    return {row['rva']: row['op'] for row in payload()['rewards_chain']['window']}


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        _, packed = LR.build(None)
        self.assertEqual(packed, ARTIFACT.read_bytes())

    def test_static_only(self):
        self.assertEqual(payload()['evidence'], 'STATIC_ONLY_ORIGINAL_APK')

    def test_every_check_passed(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 32)
        self.assertTrue(all(row['passed'] for row in checks),
                        [row['name'] for row in checks if not row['passed']])

    def test_totals(self):
        totals = payload()['totals']
        self.assertEqual((totals['closed'], totals['corrected'], totals['blocked']), (2, 2, 5))


class Census(unittest.TestCase):
    def test_the_audit_count(self):
        census = payload()['census']
        self.assertEqual(census['totals']['items'], 56)
        # 170 refreshed the audit, so the census now carries the post-169 counts
        self.assertEqual((census['totals']['still_open'], census['totals']['runtime']), (10, 20))

    def test_the_items_this_report_touches(self):
        addressed = payload()['census']['addressed']
        self.assertEqual(sorted(int(key) for key in addressed), [11, 12, 29, 39, 40, 49])
        self.assertEqual((addressed['11']['verdict'], addressed['11']['closer']),
                         ('CLOSED', 168))
        self.assertEqual((addressed['29']['verdict'], addressed['29']['closer']),
                         ('CLOSED', 168))
        self.assertEqual((addressed['39']['verdict'], addressed['39']['closer']),
                         ('RESTATED', 169))

    def test_closed_list(self):
        rows = payload()['closed']
        self.assertEqual([row['n'] for row in rows], [11, 29])
        self.assertEqual([row['report'] for row in rows], [139, 132])

    def test_corrected_list(self):
        rows = payload()['corrected']
        self.assertEqual([row['n'] for row in rows], [12, 49])
        for row in rows:
            self.assertIn('call sites', row['now'])


class RewardsChain(unittest.TestCase):
    def test_the_three_methods(self):
        chain = payload()['rewards_chain']
        self.assertEqual(chain['set_status_rank']['rva'], 22793460)
        self.assertEqual(chain['set_rewards']['rva'], 22794144)
        self.assertEqual(chain['get_rewards']['rva'], 22795496)

    def test_sizes(self):
        chain = payload()['rewards_chain']
        self.assertEqual(chain['set_status_rank']['size'], 576)
        self.assertEqual(chain['set_rewards']['size'], 1344)

    def test_the_slot_load(self):
        ops = window()
        self.assertEqual(ops[22795324], 'ldr x8, [x0, #0xb8]')
        self.assertEqual(ops[22795328], 'ldr x8, [x8, #0x38]')

    def test_the_index_and_the_bound(self):
        ops = window()
        self.assertEqual(ops[22795336], 'ldrsw x9, [x20, #0x1c]')
        self.assertEqual(ops[22795340], 'ldr w10, [x8, #0x18]')
        self.assertEqual(ops[22795344], 'cmp w9, w10')
        self.assertEqual(ops[22795348], 'b.hs #0x15bd4dc')

    def test_the_element_and_the_status(self):
        ops = window()
        self.assertEqual(ops[22795352], 'add x8, x8, x9, lsl #3')
        self.assertEqual(ops[22795356], 'ldr x1, [x8, #0x20]')
        self.assertEqual(ops[22795360], 'ldr w2, [x20, #0x28]')

    def test_the_tail_call(self):
        ops = window()
        self.assertEqual(ops[22795380], 'bl #0x15bd4e8')

    def test_xrefs(self):
        callers = payload()['rewards_chain']['callers']
        self.assertEqual([row['call'] for row in callers['set_rewards']], [22793992])
        self.assertEqual([row['call'] for row in callers['get_rewards']], [22795380])

    def test_139_contradicts_itself(self):
        prev = payload()['rewards_chain']['prev139']
        self.assertEqual(prev['read_rva'], 22795328)
        self.assertIn('+0x38', prev['open_claim'])


class SaveDataReward(unittest.TestCase):
    def test_one_call_site(self):
        pack = payload()['save_data_reward']
        self.assertEqual(pack['call_sites'], 1)
        self.assertEqual(pack['call_site']['call'], 19187472)
        self.assertEqual(pack['call_site']['caller'], 19186908)
        self.assertEqual(pack['call_site']['class_name'], 'TimeFreeRewardPack')

    def test_the_method(self):
        method = payload()['save_data_reward']['method']
        self.assertEqual((method['rva'], method['size'], method['instructions']),
                         (19188220, 1108, 277))

    def test_the_value_is_the_literal_one(self):
        arguments = payload()['save_data_reward']['arguments']
        self.assertEqual(arguments['value'], {'op': 'mov w2, #1', 'rva': 19187452})

    def test_the_other_arguments(self):
        arguments = payload()['save_data_reward']['arguments']
        self.assertEqual(arguments['device'], {'op': 'mov x3, xzr', 'rva': 19187464})
        self.assertEqual(arguments['index'], {'op': 'mov w1, w23', 'rva': 19187460})
        self.assertEqual(arguments['idDrone'], {'op': 'mov w4, w21', 'rva': 19187468})


class Absence(unittest.TestCase):
    def rows(self):
        return {row['name']: row for row in payload()['absence']}

    def test_five_rvas(self):
        self.assertEqual(sorted(self.rows()),
                         ['GameConfig..cctor', 'GameConfig.ReplaceDatas',
                          'GameConfig.SetupDatas', 'LanguageManager.GetText',
                          'MyLibrary.ToRoman'])

    def test_no_body_is_in_the_slices(self):
        for row in payload()['absence']:
            self.assertEqual(row['bodies'], 0, row['name'])
            self.assertEqual(row['body_in_slices'], [])

    def test_the_calls_exist(self):
        rows = self.rows()
        self.assertEqual(rows['MyLibrary.ToRoman']['call_sites'], 2)
        self.assertEqual(rows['LanguageManager.GetText']['call_sites'], 127)
        self.assertEqual(rows['GameConfig.ReplaceDatas']['call_sites'], 2)

    def test_the_uncalled_ones(self):
        rows = self.rows()
        self.assertEqual(rows['GameConfig..cctor']['call_sites'], 0)
        self.assertEqual(rows['GameConfig.SetupDatas']['call_sites'], 0)

    def test_names_still_resolve(self):
        for row in payload()['absence']:
            self.assertTrue(row['signature'], row['name'])


class ShopData(unittest.TestCase):
    def test_table_count(self):
        self.assertEqual(payload()['shop_data']['tables'], 126)

    def test_only_ui_references_mention_cost_price_stock(self):
        table = payload()['shop_data']['price_columns']
        self.assertEqual(list(table), ['Shop_Cell.csv'])
        self.assertTrue(all(column.startswith('text') for column in table['Shop_Cell.csv']))

    def test_no_shop_pack_asset(self):
        self.assertEqual(payload()['shop_data']['shop_pack_assets'], [])

    def test_the_shop_asset_is_sprites_only(self):
        columns = payload()['shop_data']['data_shop_pack']
        self.assertFalse([column for column in columns
                          if 'cost' in column or 'price' in column or 'stock' in column])


class Blocked(unittest.TestCase):
    def test_five_blocked_items(self):
        rows = payload()['blocked']
        self.assertEqual([row['n'] for row in rows], [39, 40, 18, 30, 9])

    def test_the_metadata_reason(self):
        rows = {row['n']: row['why'] for row in payload()['blocked']}
        self.assertIn('metadata usage table', rows[39])
        self.assertIn('0x2ae0018', rows[40])

    def test_no_metadata_table_in_the_repo(self):
        self.assertEqual(LR.metadata_present(), [])


class LiveDerivation(unittest.TestCase):
    def test_chain_recomputes(self):
        live = LR.rewards_chain()
        self.assertEqual([row['rva'] for row in live['window']],
                         [row['rva'] for row in payload()['rewards_chain']['window']])

    def test_pack_recomputes(self):
        live = LR.save_data_reward()
        self.assertEqual(live['arguments'], payload()['save_data_reward']['arguments'])

    def test_absence_recomputes(self):
        self.assertEqual(LR.absence(), payload()['absence'])


if __name__ == '__main__':
    unittest.main()
