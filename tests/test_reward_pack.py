"""Contracts for report 164: `Shop_Pack` -> `EventRewards` -> the popup reward row.

Each shop click builds four `Shop_Pack`s, writes exactly one field on each (the wallet
pack writes one of three), wraps three of them in `EventRewards(pack, number, price,
stock)` and drops the fourth, then `SetPopup` prices it and `SetEventRewardTabs` draws
one row through a 21-entry jump table onto nine pads. Everything here is static.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import reward_pack as RP  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_reward_pack.json.gz'
PIN_BYTES = 9181
PIN_SHA = 'be544db4d0f55a8cc45276264c078726cea4eff0715186210299a991a9ce8626'

CLICK = {'Arena_Shop': 22733228, 'PVP_Shop': 19942120}
PACK_SITES = {'Arena_Shop': [22733720, 22733824, 22734004, 22734304],
              'PVP_Shop': [19942612, 19942716, 19942896, 19943196]}
REWARD_SITES = {'Arena_Shop': [22733792, 22734080, 22734380, 22734492],
                'PVP_Shop': [19942684, 19942972, 19943272, 19943384]}
POPUP = {'Arena_Shop': 22835700, 'PVP_Shop': 19888660}
TABS = {'Arena_Shop': 22836632, 'PVP_Shop': 19889752}
PADS = {'Arena_Shop': [22836820, 22836920, 22837020, 22837120, 22837220, 22837288,
                       22837400, 22837488, 22837584],
        'PVP_Shop': [19889940, 19890040, 19890140, 19890240, 19890340, 19890408,
                     19890520, 19890608, 19890704]}
ICONS = ['allSpriteRewards[ladder index]', 'allSpriteRewards[ladder index]',
         'itemRandomSprite', 'allSpriteRewards[6]', 'listSpriteDrones[value - 1]',
         'listSpritePlayers[value - 1]', 'allSpriteRewards[19]', 'allSpriteRewards[20]',
         'allSpriteRewards[21]']
SCALES = ['0x756c14', '1.0', '0x756cac', '0x756f10', '1.0', '1.0', '1.25', '1.5', '1.25']
CARDS = [False, False, False, False, True, True, False, False, False]


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(RP.build(), sort_keys=True, separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', json.dumps(blob['open_items']))

    def test_every_check_passed(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 82)
        self.assertTrue(all(row['passed'] for row in checks), checks)

    def test_totals(self):
        totals = payload()['totals']
        self.assertEqual((totals['shops'], totals['packs'], totals['rewards'],
                          totals['dropped'], totals['pads']), (2, 8, 8, 2, 9))
        self.assertEqual((totals['pack_fields'], totals['indexed_fields']), (28, 27))


class PackTable(unittest.TestCase):
    def test_twenty_eight_fields(self):
        table = payload()['pack_table']
        self.assertEqual(len(table['fields']), 28)
        self.assertEqual(table['indexed'], 27)
        self.assertEqual(table['unindexed'], ['multipleBonus'])

    def test_offsets_run_from_0x10_to_0x7c(self):
        fields = payload()['pack_table']['fields']
        self.assertEqual(fields[0]['offset'], '0x10')
        self.assertEqual(fields[-1]['offset'], '0x7c')
        self.assertEqual([row['offset_int'] for row in fields],
                         [0x10 + 4 * n for n in range(28)])

    def test_index_order_matches_129(self):
        prev = RP.load(RP.PREV129)
        self.assertEqual(payload()['pack_table']['index_order'],
                         [row['field'] for row in prev['value_index']['entries']])

    def test_the_five_fields_the_click_touches(self):
        table = {row['name']: row['offset'] for row in payload()['pack_table']['fields']}
        self.assertEqual({name: table[name] for name in
                          ('Gcoins', 'Energy', 'DroneExp', 'DroneCards', 'PlayerCards')},
                         {'Gcoins': '0x10', 'Energy': '0x2c', 'DroneExp': '0x44',
                          'DroneCards': '0x48', 'PlayerCards': '0x4c'})

    def test_the_medal_fields_sit_above_the_cards(self):
        table = {row['name']: row['offset'] for row in payload()['pack_table']['fields']}
        self.assertEqual((table['ArenaMedal'], table['PvPMedal']), ('0x68', '0x6c'))


class Packs(unittest.TestCase):
    def test_four_packs_per_shop_at_the_pinned_sites(self):
        shops = payload()['shops']
        for klass, sites in PACK_SITES.items():
            self.assertEqual([row['pack_ctor'] for row in shops[klass]['packs']], sites)

    def test_each_pack_is_banded(self):
        shops = payload()['shops']
        for klass in CLICK:
            self.assertEqual([row['bands'] for row in shops[klass]['packs']],
                             [['resource'], ['resource'], ['player'], ['drone']])

    def test_the_card_bands_write_their_card_field(self):
        shops = payload()['shops']
        for klass in CLICK:
            rows = {tuple(row['bands']): row['stores'][0]['field']
                    for row in shops[klass]['packs']}
            self.assertEqual(rows[('player',)], 'PlayerCards')
            self.assertEqual(rows[('drone',)], 'DroneCards')

    def test_the_card_packs_store_item_id_plus_one(self):
        for klass in CLICK:
            for row in payload()['shops'][klass]['packs']:
                for store in row['stores']:
                    if store['field'] not in ('PlayerCards', 'DroneCards'):
                        continue
                    self.assertEqual(store['value']['op'], 'add w8, w8, #1')
                    self.assertEqual(store['value']['operands'][0]['name'], 'itemId')
                    self.assertEqual(store['value']['operands'][0]['offset'], '0x1c')

    def test_the_wallet_pack_writes_one_of_three_slots(self):
        shops = payload()['shops']
        for klass in CLICK:
            wallet = [row for row in shops[klass]['packs'] if len(row['stores']) == 3]
            self.assertEqual(len(wallet), 1)
            self.assertEqual([(store['offset'], store['field'])
                              for store in wallet[0]['stores']],
                             [('0x10', 'Gcoins'), ('0x2c', 'Energy'), ('0x44', 'DroneExp')])
            for store in wallet[0]['stores']:
                self.assertEqual(store['value']['name'], 'itemValue')
                self.assertEqual(store['value']['offset'], '0x14')

    def test_the_wallet_slots_are_guarded_by_300_and_301(self):
        shops = payload()['shops']
        for klass in CLICK:
            wallet = [row for row in shops[klass]['packs'] if len(row['stores']) == 3][0]
            guards = RP.wallet_guards(klass, wallet['pack_ctor'], wallet['event_rewards'])
            self.assertEqual([row['op'] for row in guards],
                             ['cmp w21, #0x12c', 'cmp w21, #0x12d'])

    def test_six_of_the_eight_packs_write_exactly_one_field(self):
        rows = [row for klass in CLICK for row in payload()['shops'][klass]['packs']]
        self.assertEqual(sum(1 for row in rows if len(row['stores']) == 1), 6)


class EventRewards(unittest.TestCase):
    def test_four_rewards_per_shop_at_the_pinned_sites(self):
        shops = payload()['shops']
        for klass, sites in REWARD_SITES.items():
            self.assertEqual([row['rva'] for row in shops[klass]['rewards']], sites)

    def test_three_survive_and_one_is_dropped(self):
        shops = payload()['shops']
        for klass in CLICK:
            rows = shops[klass]['rewards']
            self.assertEqual([row['kept'] for row in rows], [False, True, True, True])

    def test_the_dropped_one_has_no_copy_of_x0(self):
        shops = payload()['shops']
        for klass in CLICK:
            dropped = [row for row in shops[klass]['rewards'] if not row['kept']][0]
            self.assertEqual(dropped['bands'], ['resource'])
            self.assertEqual(dropped['number']['name'], 'ItemDroneValue')
            self.assertEqual(dropped['price']['name'], 'ItemDroneCost')

    def test_the_economy_fields_feed_number_and_price(self):
        shops = payload()['shops']
        for klass in CLICK:
            rows = {tuple(row['bands']): row for row in shops[klass]['rewards']}
            self.assertEqual((rows[('player',)]['number']['name'],
                              rows[('player',)]['price']['name']),
                             ('ItemPlayerValue', 'ItemPlayerCost'))
            self.assertEqual((rows[('drone',)]['number']['name'],
                              rows[('drone',)]['price']['name']),
                             ('ItemDroneValue', 'ItemDroneCost'))

    def test_the_wallet_pair_reads_the_locals(self):
        shops = payload()['shops']
        for klass in CLICK:
            wallet = [row for row in shops[klass]['rewards']
                      if row['number']['kind'] == 'closure-field'][0]
            self.assertEqual((wallet['bands'], wallet['number']['name'],
                              wallet['price']['name']),
                             (['resource'], 'itemValue', 'itemCost'))
            self.assertEqual((wallet['number']['offset'], wallet['price']['offset']),
                             ('0x14', '0x10'))

    def test_stock_is_always_max_stock_count(self):
        shops = payload()['shops']
        for klass in CLICK:
            for row in shops[klass]['rewards']:
                self.assertEqual(row['stock']['name'], 'MaxStockCount')
                self.assertEqual(row['stock']['default'], 10)

    def test_the_embedded_economy(self):
        shops = payload()['shops']
        for klass in CLICK:
            rows = {tuple(row['bands']): row for row in shops[klass]['rewards']}
            self.assertEqual((rows[('player',)]['number']['default'],
                              rows[('player',)]['price']['default']), (1, 50))
            self.assertEqual((rows[('drone',)]['number']['default'],
                              rows[('drone',)]['price']['default']), (1, 30))

    def test_the_four_fields_of_the_reward_struct(self):
        fields = {row['name']: row['offset'] for row in
                  RP.class_block('Board_EventSeasonPass.EventRewards')['fields']}
        self.assertEqual(fields, {'pack': 0x10, 'number': 0x18, 'price': 0x1c,
                                  'stock': 0x20})


class Locals(unittest.TestCase):
    def test_the_locals_come_from_the_two_resource_arrays(self):
        shops = payload()['shops']
        for klass in CLICK:
            rows = shops[klass]['locals']
            self.assertEqual(rows['0x10']['array'], 'ItemResourceCost')
            self.assertEqual(rows['0x14']['array'], 'ItemResourceValues')
            self.assertEqual(rows['0x10']['field_name'], 'itemCost')
            self.assertEqual(rows['0x14']['field_name'], 'itemValue')

    def test_the_index_is_cell_id_minus_300(self):
        shops = payload()['shops']
        for klass in CLICK:
            for slot in ('0x10', '0x14'):
                row = shops[klass]['locals'][slot]
                self.assertEqual(row['index_from']['base'], 300)
                self.assertEqual(row['cell_id_load'], 'ldr w8, [x21, #0x18]')


class Popup(unittest.TestCase):
    def test_setpopup_sits_where_159_left_it(self):
        shops = payload()['shops']
        for klass, rva in POPUP.items():
            self.assertEqual(shops[klass]['popup']['rva'], rva)
        self.assertEqual(shops['Arena_Shop']['popup']['size'], 932)
        self.assertEqual(shops['PVP_Shop']['popup']['size'], 928)

    def test_four_fields_are_written(self):
        shops = payload()['shops']
        for klass in CLICK:
            self.assertEqual([(row['offset'], row['field'])
                              for row in shops[klass]['popup']['writes']],
                             [('0x50', 'onExit'), ('0x58', 'count'),
                              ('0x60', 'rewards'), ('0x5c', 'maxStock')])

    def test_the_cost_is_price_times_count_then_formatted(self):
        popup = payload()['shops']['Arena_Shop']['popup']
        self.assertEqual(popup['cost']['op'], 'mul w8, w9, w8')
        self.assertEqual([row['op'] for row in popup['cost']['operands']],
                         ['ldr w9, [x20, #0x1c]', 'ldur w8, [x21, #-4]'])
        self.assertEqual(popup['cost']['formatted_by'], 'Format')
        self.assertEqual(popup['cost']['written_to']['field'], 'textCost')
        self.assertEqual(popup['cost']['written_to']['offset'], '0x30')

    def test_the_remaining_stock_is_stock_minus_sold(self):
        popup = payload()['shops']['Arena_Shop']['popup']
        self.assertEqual(popup['remaining']['op'], 'sub w8, w23, w0')
        self.assertEqual(popup['remaining']['minuend'], 'ldr w23, [x20, #0x20]')
        self.assertEqual(popup['remaining']['stored_field'], 'maxStock')

    def test_the_slider_is_configured_and_gated(self):
        for klass in CLICK:
            popup = payload()['shops'][klass]['popup']
            self.assertEqual([(row['offset'], row['field'])
                              for row in popup['slider_writes']],
                             [('0x64', 'step'), ('0x60', 'maxValue')])
            self.assertTrue(popup['slider_gate']['op'].startswith('cmp w'))
            self.assertEqual(popup['slider_gate']['op'].split(', ')[1], '#1')
            self.assertTrue(popup['slider_gate']['source'].endswith('#0x5c]'))
            self.assertTrue(popup['slider_gate']['branch'].startswith('b.le'))
            self.assertEqual(popup['slider_value']['method'], 'set_Value')

    def test_the_medal_balance_goes_on_the_coin_label(self):
        for klass, getter in (('Arena_Shop', 'get_ArenaMedal'),
                              ('PVP_Shop', 'get_PvPMedal')):
            popup = payload()['shops'][klass]['popup']
            self.assertIn(getter, [row['method'] for row in popup['calls']])
            self.assertIn('textCoinEvent', [row['field'] for row in popup['reads']])

    def test_the_order_of_the_three_closing_calls(self):
        popup = payload()['shops']['Arena_Shop']['popup']
        live = [row['method'] for row in popup['calls'] if row['method']]
        self.assertLess(live.index('SetEventRewardTabs'), live.index('SetActive'))
        self.assertLess(live.index('SetActive'), live.index('set_Value'))

    def test_the_popup_binds_its_own_float_handler(self):
        popup = payload()['shops']['Arena_Shop']['popup']
        self.assertIn('Action<float>..ctor',
                      [row['method'] for row in popup['calls']])


class Tabs(unittest.TestCase):
    def test_set_event_reward_tabs_sits_where_160_left_it(self):
        shops = payload()['shops']
        for klass, rva in TABS.items():
            self.assertEqual(shops[klass]['tabs']['rva'], rva)

    def test_only_the_first_index_is_drawn(self):
        tabs = payload()['shops']['Arena_Shop']['tabs']
        self.assertEqual(tabs['picks']['element']['op'], 'ldr w20, [x0, #0x20]')
        self.assertEqual(tabs['picks']['empty_skip'], 'cbz x0, #0x15c79d0')

    def test_the_icon_index_is_value_minus_one(self):
        tabs = payload()['shops']['Arena_Shop']['tabs']
        self.assertEqual(tabs['picks']['minus_one']['op'], 'sub w22, w0, #1')

    def test_the_jump_table(self):
        tabs = payload()['shops']['Arena_Shop']['tabs']
        self.assertEqual(tabs['dispatch']['bound']['op'], 'cmp w20, #0x15')
        self.assertEqual(tabs['dispatch']['bound']['limit'], 21)
        self.assertEqual(tabs['table_va'], '0x779e50')
        self.assertEqual(tabs['table_bytes'], 21)
        self.assertEqual(tabs['dispatch']['br']['op'], 'br x9')

    def test_nine_pads_at_the_pinned_sites(self):
        shops = payload()['shops']
        for klass, sites in PADS.items():
            self.assertEqual([row['pad_rva'] for row in shops[klass]['tabs']['pads']],
                             sites)

    def test_the_three_ladder_index_pads_and_the_six_constants(self):
        pads = payload()['shops']['Arena_Shop']['tabs']['pads']
        self.assertEqual([row['box_arg'] for row in pads],
                         ['w20', 'w20', 'w20', '#6', '#0xe', '#0xf', '#0x13', '#0x14',
                          '#0x15'])
        self.assertEqual([row['box_arg_value'] for row in pads],
                         [None, None, None, 6, 14, 15, 19, 20, 21])

    def test_every_pad_asks_for_a_box_sprite(self):
        pads = payload()['shops']['Arena_Shop']['tabs']['pads']
        self.assertEqual([row['box'] for row in pads],
                         ['GetBoxSpriteGeneral(%s)' % arg for arg in
                          ('w20', 'w20', 'w20', '#6', '#0xe', '#0xf', '#0x13', '#0x14',
                           '#0x15')])

    def test_the_nine_icons(self):
        pads = payload()['shops']['Arena_Shop']['tabs']['pads']
        self.assertEqual([row['icon'] for row in pads], ICONS)

    def test_only_the_two_card_pads_set_is_cards(self):
        pads = payload()['shops']['Arena_Shop']['tabs']['pads']
        self.assertEqual([row['is_cards'] for row in pads], CARDS)

    def test_every_pad_shows_the_reward_number(self):
        tabs = payload()['shops']['Arena_Shop']['tabs']
        self.assertEqual(tabs['reward_number']['field'],
                         'Board_EventSeasonPass.EventRewards.number')
        self.assertEqual({row['number'] for row in tabs['pads']}, {'w19'})

    def test_the_nine_scales(self):
        pads = payload()['shops']['Arena_Shop']['tabs']['pads']
        self.assertEqual([str((row['scale'] or {}).get('value')) for row in pads], SCALES)

    def test_three_scales_are_rodata(self):
        pads = payload()['shops']['Arena_Shop']['tabs']['pads']
        self.assertEqual([(row['scale']['kind'], row['scale']['value']) for row in pads
                          if row['scale']['kind'] == 'rodata'],
                         [('rodata', '0x756c14'), ('rodata', '0x756cac'),
                          ('rodata', '0x756f10')])

    def test_the_setinfo_signature(self):
        tabs = payload()['shops']['Arena_Shop']['tabs']
        self.assertIn('public void SetInfo(', tabs['set_info'])
        self.assertIn('bool _isCards = False', tabs['set_info'])
        self.assertIn('float _scaleIcon = 1', tabs['set_info'])

    def test_pvp_mirrors_arena(self):
        shops = payload()['shops']
        arena = shops['Arena_Shop']['tabs']['pads']
        pvp = shops['PVP_Shop']['tabs']['pads']
        self.assertEqual([(row['box_arg'], row['icon'], row['is_cards'],
                           (row['scale'] or {}).get('value')) for row in pvp],
                         [(row['box_arg'], row['icon'], row['is_cards'],
                           (row['scale'] or {}).get('value')) for row in arena])


class PriorReports(unittest.TestCase):
    def test_129_index_order_is_unchanged(self):
        previous = RP.load(RP.PREV129)
        self.assertEqual([row['index'] for row in previous['value_index']['entries']],
                         list(range(27)))

    def test_157_constants_are_the_economy(self):
        previous = RP.load(RP.PREV157)
        for name, value in RP.ECONOMY_DEFAULT.items():
            self.assertEqual(previous['shipped'][name]['value'], value)

    def test_160_counted_the_same_four_sites(self):
        previous = RP.load(RP.PREV160)
        for klass in CLICK:
            self.assertEqual([row['rva'] for row in previous['bands'][klass]['packs']],
                             PACK_SITES[klass])

    def test_163_lambdas_are_the_ones_indexed_here(self):
        previous = RP.load(RP.PREV163)
        self.assertEqual([previous['shops']['Arena_Shop']['bands'][band]['lambda_']
                          ['signature'] for band in ('player', 'drone', 'resource')],
                         ['internal void <OnClickPlayerItem>b__1(int count) { }',
                          'internal void <OnClickPlayerItem>b__3(int count) { }',
                          'internal void <OnClickPlayerItem>b__5(int count) { }'])

    def test_162_is_still_green(self):
        previous = RP.load(RP.PREV162)
        self.assertEqual(len(previous['checks']), 22)
        self.assertTrue(all(row['passed'] for row in previous['checks']))

    def test_159_and_155_still_hold(self):
        self.assertTrue(RP.load(RP.PREV155))
        chains = RP.load(RP.PREV159)['chains']
        for klass in CLICK:
            self.assertTrue(chains[klass]['caller']['call_rva'])


class Api(unittest.TestCase):
    def test_the_pinned_helpers(self):
        self.assertEqual((RP.PACK_CTOR, RP.ER_CTOR, RP.SET_INFO, RP.ALLOC),
                         (0x1341298, 0x12901b4, 0x1310880, 0x110d240))

    def test_the_sprite_fields_of_the_data_holder(self):
        self.assertEqual(RP.SPRITE_FIELDS[0x20], 'allSpriteRewards')
        self.assertEqual(RP.SPRITE_FIELDS[0x30], 'listSpriteDrones')
        self.assertEqual(RP.SPRITE_FIELDS[0x38], 'listSpritePlayers')
        self.assertEqual(RP.SPRITE_FIELDS[0x60], 'itemRandomSprite')

    def test_a_store_never_counts_as_a_definition(self):
        store = {'mnemonic': 'str', 'op_str': 'w23, [x22, #0x2c]'}
        self.assertFalse(RP.defines(store, 'w23'))
        load = {'mnemonic': 'ldr', 'op_str': 'w23, [x20, #0x14]'}
        self.assertTrue(RP.defines(load, 'w23'))

    def test_branch_target_reads_conditional_branches(self):
        self.assertEqual(RP.branch_target('#0x15c7868'), 22837352)
        self.assertEqual(RP.branch_target('w20, #0x15'), 0x15)

    def test_the_resource_band_base_is_300(self):
        self.assertEqual(list(RP.BD.BANDS), ['player', 'drone', 'resource'])
        self.assertEqual(RP.BD.BAND_BASE['resource'], 0x12c)


if __name__ == '__main__':
    unittest.main()
