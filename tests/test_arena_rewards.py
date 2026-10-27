"""Contracts for report 151: the ten `ArenaManager.rewards` strings and their consumer."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import arena_rewards  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_arena_rewards.json.gz'
PIN_BYTES = 5273
PIN_SHA = 'f76d36671418c9bbd07fdd0ca5be45a7e95973647905f82315ede3e40df7373a'
PLACEMENTS = ['1', '2', '3-4', '5-10', '11-45', '46-50']


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(arena_rewards.build(), sort_keys=True, separators=(',', ':'))
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

    def test_upstream_artifact_is_139(self):
        row = payload()['provenance']['sources'][-1]
        self.assertEqual(row['path'], 'datas/l2_535b0541_arena_statics.json.gz')
        self.assertEqual(row['sha256'],
                         '261eca3a7268b5450fed691b224edaf09979a1ff9ca8662fd9ab68f48399a4b5')


class Array(unittest.TestCase):
    def test_allocation(self):
        array = payload()['array']
        self.assertEqual(array['newarr_rva'], 22692608)
        self.assertEqual(array['length_instruction'], 22692580)

    def test_ten_elements_in_offset_order(self):
        rows = payload()['array']['rows']
        self.assertEqual([row['index'] for row in rows], list(range(10)))
        self.assertEqual([row['store_offset'] for row in rows],
                         [0x20 + 8 * index for index in range(10)])

    def test_store_rvas_are_the_pinned_ones(self):
        self.assertEqual([row['store_rva'] for row in payload()['array']['rows']],
                         [22692640, 22692664, 22692688, 22692712, 22692736,
                          22692760, 22692784, 22692808, 22692832, 22692852])

    def test_every_cell_is_a_pinned_literal(self):
        for row in payload()['array']['rows']:
            self.assertTrue(row['text'].startswith('#1[Medal:'), row)
            self.assertGreater(row['addend'], 0)

    def test_order_is_not_cell_order(self):
        """The fills are not sorted by cell address — index comes from the store offset."""
        cells = [row['cell'] for row in payload()['array']['rows']]
        self.assertNotEqual(cells, sorted(cells))


class Rewards(unittest.TestCase):
    def test_ten_rows_six_bands(self):
        rows = payload()['rewards']
        self.assertEqual(len(rows), 10)
        self.assertEqual([row['band_count'] for row in rows], [6] * 10)

    def test_placements_are_the_same_six_every_season(self):
        for row in payload()['rewards']:
            self.assertEqual([band['placement'] for band in row['bands']], PLACEMENTS)

    def test_top_season_first_band(self):
        bands = payload()['rewards'][0]['bands']
        self.assertEqual((bands[0]['low'], bands[0]['high']), (1, 1))
        self.assertEqual((bands[0]['medal'], bands[0]['gems']), (680, 250))

    def test_top_season_last_band(self):
        band = payload()['rewards'][0]['bands'][-1]
        self.assertEqual((band['low'], band['high']), (46, 50))
        self.assertEqual((band['medal'], band['gems']), (60, 20))

    def test_ladder_by_index(self):
        self.assertEqual(payload()['cross_checks']['first_band_by_rank'],
                         [680, 800, 1000, 1250, 1500, 2000, 2500, 3000, 4000, 5000])
        self.assertEqual(payload()['cross_checks']['last_band_by_rank'],
                         [60, 70, 90, 110, 130, 180, 220, 270, 360, 440])

    def test_medal_and_gems_never_invert(self):
        for row in payload()['rewards']:
            for band in row['bands']:
                self.assertGreater(band['medal'], band['gems'], band)

    def test_every_row_shrinks_down_the_bands(self):
        for row in payload()['rewards']:
            medals = [band['medal'] for band in row['bands']]
            self.assertEqual(medals, sorted(medals, reverse=True), row['index'])

    def test_sixty_rows_match_139(self):
        checks = payload()['cross_checks']
        self.assertEqual(checks['rows'], 60)
        self.assertTrue(checks['match_139'])
        self.assertEqual(checks['previous_artifact_rewards'], 10)


class Format(unittest.TestCase):
    def test_steps(self):
        self.assertEqual(payload()['parse']['steps'],
                         ['Replace("]", "")', 'Replace("#", "")', 'Replace(\'"\', "")',
                          "Split(';')", "Split('[')", "Split(',')", "Split(':')",
                          'int.Parse'])

    def test_separators_are_immediates(self):
        chars = [row['char'] for row in payload()['parse']['evidence']['separators']]
        self.assertEqual(chars, [';', '[', ',', ':', ':', '-'])

    def test_literals_name_both_fields(self):
        texts = {row['text'] for row in payload()['parse']['evidence']['literals']}
        self.assertGreaterEqual(texts, {']', '#', '"', 'Medal', 'Gems', 'Reward rank:', '-'})

    def test_arena_rewards_field_offsets(self):
        self.assertEqual(payload()['parse']['arena_rewards_fields'],
                         {'medal': 0x10, 'gems': 0x14})


class Consumers(unittest.TestCase):
    def test_nine_rows(self):
        self.assertEqual(len(payload()['consumers']), 9)

    def test_only_two_read_rewards(self):
        readers = [row['class_name'] for row in payload()['consumers']
                   if row['reads_rewards']]
        self.assertEqual(sorted(readers), ['Board_Arena', 'Popup_ArenaInfo'])

    def test_only_the_cctor_writes_it(self):
        writers = [row['class_name'] for row in payload()['consumers']
                   if row['writes_rewards']]
        self.assertEqual(writers, ['ArenaManager'])

    def test_the_write_is_the_array_store(self):
        cctor = next(row for row in payload()['consumers']
                     if row['writes_rewards'])
        self.assertEqual(cctor['rva'], 22692372)
        self.assertIn({'mnemonic': 'str', 'offset': '0x38',
                       'operand': 'x0, [x8, #0x38]', 'rva': 22692868},
                      cctor['access'])

    def test_no_other_offset_is_touched(self):
        offsets = set()
        for row in payload()['consumers']:
            offsets.update(row['fields'])
        self.assertLessEqual(offsets, {'0x0', '0x18', '0x20', '0x28', '0x30', '0x38'})

    def test_reader_window_lands_on_the_consumer(self):
        reader = payload()['reader']
        self.assertEqual(reader['method']['rva'], 22794144)
        self.assertEqual(reader['read_rva'], 22795328)
        self.assertEqual(reader['window'][0]['operand'], 'x8, [x8, #0x38]')

    def test_reader_call_is_the_parser(self):
        calls = payload()['reader']['calls']
        self.assertEqual([call['rva'] for call in calls], [22795496])
        self.assertIn('GetRewards', calls[0]['signature'])

    def test_reader_guard_uses_rank(self):
        operands = [row['operand'] for row in payload()['reader']['window']]
        self.assertIn('x9, [x20, #0x1c]', operands)
        self.assertIn('w10, [x8, #0x18]', operands)
        self.assertIn('x1, [x8, #0x20]', operands)


class Census(unittest.TestCase):
    def test_six_offsets_and_their_names(self):
        rows = payload()['census']
        self.assertEqual([row['offset'] for row in rows],
                         ['0x0', '0x18', '0x20', '0x28', '0x30', '0x38'])
        self.assertEqual([row['field'] for row in rows],
                         ['IsOpen', 'SeasonTimes', 'RankMapsIndex', 'RankUpIndexs',
                          'RankDropIndexs', 'rewards'])

    def test_three_offsets_have_no_reader(self):
        silent = [row['offset'] for row in payload()['census'] if not row['reads']]
        self.assertEqual(silent, ['0x0', '0x20'])

    def test_rank_maps_index_has_two_writers(self):
        row = next(row for row in payload()['census'] if row['offset'] == '0x20')
        self.assertEqual([entry['rva'] for entry in row['writes']], [22692596, 22807948])

    def test_refill_stores(self):
        refill = payload()['census_boundary']['refill']
        self.assertEqual(refill['rva'], 22782048)
        self.assertEqual(refill['stores'], [22782328, 22782576, 22782600])

    def test_census_boundary_is_stated(self):
        self.assertIn('stur', payload()['census_boundary']['not_covered'])


class MapPool(unittest.TestCase):
    def test_bridge_reads_the_rank_setup(self):
        bridge = payload()['map_pool']
        self.assertEqual(bridge['method']['rva'], 22807856)
        self.assertEqual(bridge['read']['rva'], 22807916)
        self.assertEqual(bridge['read']['operand'], 'w20, [x20, #0x24]')

    def test_bridge_writes_rank_maps_index(self):
        bridge = payload()['map_pool']
        self.assertEqual(bridge['write']['rva'], 22807948)
        self.assertEqual(bridge['write']['operand'], 'w20, [x8, #0x20]')


class Findings(unittest.TestCase):
    def test_all_checks_pass(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 16)
        self.assertTrue(all(row['passed'] for row in checks), checks)

    def test_four_confirmations(self):
        rows = payload()['confirmations']
        self.assertEqual(len(rows), 4)
        self.assertIn('148 #11', rows[3]['item'])

    def test_three_open_items_are_runtime_or_config(self):
        rows = payload()['open_items']
        self.assertEqual(len(rows), 3)
        self.assertIn('MODEL_NOT_MEASURED runtime', rows[0]['blocking'])
        self.assertIn('RankSplit', rows[1]['blocking'])

    def test_offsets_are_decimal_in_the_prose(self):
        """RVAs are recorded as integers, never as strings."""
        for row in payload()['consumers']:
            self.assertIsInstance(row['rva'], int)
        self.assertIsInstance(payload()['reader']['method']['rva'], int)


if __name__ == '__main__':
    unittest.main()
