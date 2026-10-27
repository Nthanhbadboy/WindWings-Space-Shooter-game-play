"""Contracts for report 169: which instruction fills each `Board_PVP` reward array.

132 called `rewardValues` "filled at runtime" and named a `rewardTypes` field that
does not exist; 133 left the handle slots unresolved. The ctor answers the first
half without the metadata table — six `InitializeArray` calls, each followed by
`str x20, [x19, #offset]` — and the rest of the report is the honest second half:
the bytes stay `NOT_BOUND`, with the candidate census to show why.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import pvp_reward_arrays as PA  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_pvp_reward_arrays.json.gz'
PIN_BYTES = 4618
PIN_SHA = 'cb3711ec8dc742b88a1f605df2e3afdf0e78226ddc57be85d7aa57c87c8d583b'

OFFSETS = ['0x198', '0x1a0', '0x1a8', '0x208', '0x210', '0x218']
NAMES = ['rewardIndexs', 'rewardValues', 'rewardScales', 'allBetCoinValues',
         'allBetGemValues', 'allBetMedalValues']
CALLS = [19796684, 19796716, 19796748, 19796804, 19796836, 19796876]


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        _, packed = PA.build(None)
        self.assertEqual(packed, ARTIFACT.read_bytes())

    def test_static_only(self):
        self.assertEqual(payload()['evidence'], 'STATIC_ONLY_ORIGINAL_APK')

    def test_every_check_passed(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 28)
        self.assertTrue(all(row['passed'] for row in checks),
                        [row['name'] for row in checks if not row['passed']])

    def test_totals(self):
        totals = payload()['totals']
        self.assertEqual((totals['initializers'], totals['arrays'], totals['length']), (6, 6, 6))
        self.assertEqual((totals['blobs'], totals['float_candidates']), (982, 4))


class Ctor(unittest.TestCase):
    def test_the_ctor(self):
        ctor = payload()['ctor']
        self.assertEqual((ctor['rva'], ctor['size'], ctor['instructions']),
                         (19796420, 500, 125))

    def test_six_calls_in_order(self):
        rows = payload()['ctor']['initializers']
        self.assertEqual([row['call']['rva'] for row in rows], CALLS)

    def test_each_call_is_followed_by_its_store(self):
        for row in payload()['ctor']['initializers']:
            self.assertEqual(int(row['store']['rva']), row['call']['rva'] + 4, row['offset'])

    def test_the_offsets(self):
        self.assertEqual([row['offset'] for row in payload()['ctor']['initializers']], OFFSETS)

    def test_the_names(self):
        self.assertEqual([row['field'] for row in payload()['ctor']['initializers']], NAMES)

    def test_every_array_is_six(self):
        self.assertEqual({row['length'] for row in payload()['ctor']['initializers']}, {6})

    def test_every_allocation_is_the_same_helper(self):
        helpers = {row['allocate']['op'] for row in payload()['ctor']['initializers']}
        self.assertEqual(len(helpers), 1)
        self.assertTrue(helpers.pop().startswith('bl #0x110d09c'))

    def test_the_handles_come_from_cells(self):
        for row in payload()['ctor']['initializers']:
            self.assertTrue(row['handle']['op'].startswith('ldr x1, ['), row['handle']['op'])


class Fields(unittest.TestCase):
    def test_the_dump_types(self):
        fields = payload()['fields']
        self.assertEqual(sorted(fields), OFFSETS)
        self.assertEqual({offset: rows['name'] for offset, rows in fields.items()},
                         dict(zip(OFFSETS, NAMES)))

    def test_rewardscales_is_float(self):
        self.assertEqual(payload()['fields']['0x1a8']['declared'], 'float[]')

    def test_the_other_five_are_int_arrays(self):
        for offset in ('0x198', '0x1a0', '0x208', '0x210', '0x218'):
            self.assertEqual(payload()['fields'][offset]['declared'], 'int[]', offset)

    def test_no_rewardtypes_field(self):
        types = payload()['reward_types']
        self.assertEqual(types['in_class'], 0)
        self.assertEqual(sorted(types['fields_named']), sorted(NAMES))


class Readers(unittest.TestCase):
    def test_six_arrays_have_readers(self):
        self.assertEqual(sorted(payload()['readers']), sorted(NAMES))

    def test_the_reward_arrays_share_their_readers(self):
        readers = payload()['readers']
        self.assertEqual([row['rva'] for row in readers['rewardIndexs']['reads']],
                         [row['rva'] for row in readers['rewardValues']['reads']])
        self.assertEqual([row['rva'] for row in readers['rewardIndexs']['reads']],
                         [19791640, 19792936, 19811092])

    def test_rewardscales_has_two(self):
        self.assertEqual([row['rva'] for row in payload()['readers']['rewardScales']['reads']],
                         [19791640, 19811092])

    def test_the_bet_ladders(self):
        readers = payload()['readers']
        self.assertEqual([row['rva'] for row in readers['allBetCoinValues']['reads']],
                         [19779724, 19813332])
        self.assertEqual([row['rva'] for row in readers['allBetMedalValues']['reads']],
                         [19780244, 19813332])

    def test_every_reader_body_is_pinned(self):
        for entry in payload()['readers'].values():
            for row in entry['reads']:
                self.assertTrue(row['body_in_slices'], row)

    def test_every_reader_loads_its_own_offset(self):
        for entry in payload()['readers'].values():
            for row in entry['reads']:
                self.assertTrue(row['loads'], row)

    def test_the_three_reward_readers_are_named(self):
        self.assertEqual([row['method'] for row in payload()['readers']['rewardIndexs']['reads']],
                         ['private void SetupHunters() { }',
                          'private void OnClickHunterCollect(WinPoint point) { }',
                          'internal bool <IESummarySeasonRewards>g__IsCollected|0(int index) { }'])

    def test_the_bet_readers_are_the_change_handlers(self):
        readers = payload()['readers']
        self.assertEqual([row['method'] for row in readers['allBetCoinValues']['reads']],
                         ['private void OnChangeCoins(int amount) { }',
                          'private bool MoveNext() { }'])
        self.assertEqual([row['method'] for row in readers['allBetMedalValues']['reads']],
                         ['private void OnChangeMedals(int amount) { }',
                          'private bool MoveNext() { }'])


class Blobs(unittest.TestCase):
    def test_census(self):
        blobs = payload()['blobs']
        self.assertEqual((blobs['pid_fields'], blobs['exactly_24_bytes']), (982, 99))

    def test_plausible_floats(self):
        self.assertEqual(len(payload()['blobs']['float_plausible']), 7)

    def test_three_are_attributed_elsewhere(self):
        self.assertEqual(len(payload()['blobs']['attributed_to_other_ctors']), 3)

    def test_four_remain(self):
        unclaimed = payload()['blobs']['unclaimed_floats']
        self.assertEqual([row['values'] for row in unclaimed][0],
                         [0.8, 1.0, 1.5, 2.0, 2.5, 3.0])

    def test_the_indexs_blob(self):
        blob = payload()['blobs']['indexs_blob']
        self.assertEqual(blob['values'], [23, 0, 14, 1, 15, 18])
        self.assertEqual(blob['data_index'], 30944)

    def test_no_candidate_is_adjacent_to_the_indexs_data(self):
        blobs = payload()['blobs']
        self.assertFalse([row for row in blobs['float_plausible']
                          if row['data_index'] in blobs['adjacent_data_indexes']])


class StaticCtor(unittest.TestCase):
    def test_it_only_zeroes_a_struct(self):
        stat = payload()['static_ctor']
        self.assertEqual((stat['rva'], stat['size']), (19796920, 88))
        self.assertEqual([row['op'] for row in stat['stores']],
                         ['str d0, [x8]', 'str xzr, [x8, #0x10]', 'str wzr, [x8, #0x18]'])


class Corrections(unittest.TestCase):
    def test_two_corrections(self):
        rows = payload()['corrections']
        self.assertEqual([row['report'] for row in rows], [132, 133])

    def test_the_132_correction_names_the_missing_field(self):
        row = payload()['corrections'][0]
        self.assertIn('rewardTypes', row['was'])
        self.assertIn('no `rewardTypes` field', row['now'])

    def test_the_133_correction_narrows_the_block(self):
        row = payload()['corrections'][1]
        self.assertIn('0x2ae0010', row['was'])
        self.assertIn('adjacent store', row['now'])


class LiveDerivation(unittest.TestCase):
    def test_initializers_recompute(self):
        self.assertEqual(PA.initializers(), payload()['ctor']['initializers'])

    def test_fields_recompute(self):
        self.assertEqual(PA.fields_from_dump(), payload()['fields'])

    def test_readers_recompute(self):
        self.assertEqual(PA.readers(), payload()['readers'])

    def test_133_rvas_are_the_same_six(self):
        previous = json.loads(gzip.decompress(
            (ROOT / 'datas/l2_535b0541_pvp_hunter_reward_table.json.gz').read_bytes()))
        self.assertEqual([row['initarray_rva'] for row in previous['table']['arrays']], CALLS)


if __name__ == '__main__':
    unittest.main()
