"""Contracts for report 172: 169's reader lists, corrected mechanically.

169 matched `[xN, #offset]` and called every hit a reader. IL2CPP emits the same
shape for metadata cells (`adrp x8, #page` then `ldr x8, [x8, #off]`), and the cell
pages sit at convenient offsets, so `MoveNext` and one local function were listed as
readers of arrays they never touch. This report decides by the base register's last
definition, then reads the coroutine it accidentally promoted.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import pvp_move_next as PM  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_pvp_move_next.json.gz'
PIN_BYTES = 4739
PIN_SHA = 'ac3f1070c21ab2eedbea7ad64773eaba69c3b4e96ce86c680d0b894bfa60a9a4'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        _, packed = PM.build(None)
        self.assertEqual(packed, ARTIFACT.read_bytes())

    def test_static_only(self):
        self.assertEqual(payload()['evidence'], 'STATIC_ONLY_ORIGINAL_APK')

    def test_every_check_passed(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 19)
        self.assertTrue(all(row['passed'] for row in checks),
                        [row['name'] for row in checks if not row['passed']])

    def test_totals(self):
        totals = payload()['totals']
        self.assertEqual((totals['reads'], totals['real'], totals['cells'], totals['calls'],
                          totals['states']), (23, 11, 12, 29, 11))


class Readers(unittest.TestCase):
    def test_the_reward_arrays(self):
        readers = payload()['readers']
        self.assertEqual(readers['rewardIndexs']['real_readers'], [19791640, 19792936])
        self.assertEqual(readers['rewardValues']['real_readers'], [19791640, 19792936])
        self.assertEqual(readers['rewardScales']['real_readers'], [19791640])

    def test_the_bet_ladders_have_one_each(self):
        readers = payload()['readers']
        self.assertEqual([readers[field]['real_readers'] for field in
                          ('allBetCoinValues', 'allBetGemValues', 'allBetMedalValues')],
                         [[19779724], [19779984], [19780244]])

    def test_every_false_hit_names_a_cell(self):
        cells = {field: row['cells'] for field, row in payload()['readers'].items()}
        self.assertEqual(cells, {'rewardIndexs': ['0x2ae0198'],
                                 'rewardValues': ['0x2ae01a0'],
                                 'rewardScales': ['0x2ae01a8'],
                                 'allBetCoinValues': ['0x2ae0208'],
                                 'allBetGemValues': ['0x2ae0210'],
                                 'allBetMedalValues': ['0x2ae0218']})

    def test_move_next_is_in_no_reader_list(self):
        self.assertFalse([field for field, row in payload()['readers'].items()
                          if PM.MOVENEXT in row['real_readers']])

    def test_three_corrections_against_169(self):
        rows = payload()['corrected']
        self.assertEqual([row['report'] for row in rows], [169, 169, 169])
        self.assertEqual([row['field'] for row in rows],
                         ['allBetCoinValues', 'allBetGemValues', 'allBetMedalValues'])

    def test_every_read_row_is_classified(self):
        kinds = {row['kind'] for row in payload()['reads']}
        self.assertEqual(kinds, {'object_field', 'static_cell'})

    def test_a_cell_row_carries_its_address(self):
        cells = [row for row in payload()['reads'] if row['kind'] == 'static_cell']
        self.assertEqual(len(cells), 12)
        self.assertTrue(all(row['cell'] for row in cells))


class Coroutine(unittest.TestCase):
    def test_the_method(self):
        row = payload()['movenext']
        self.assertEqual((row['rva'], row['size'], row['instructions']), (19813332, 1808, 452))
        self.assertEqual(row['class_name'], 'Board_PVP.<GetPvPUserCachingDatas>d__78')

    def test_six_states(self):
        self.assertEqual(sorted(set(payload()['states']['values'])), [-1, 1, 2, 3, 4, 5])

    def test_the_state_field_is_written_to_one_slot(self):
        self.assertEqual(payload()['states']['field'], '0x10')
        self.assertEqual(len(payload()['states']['store_rvas']), 8)

    def test_it_builds_the_path_then_downloads(self):
        flow = payload()['flow']
        self.assertEqual(flow['path']['class_name'], 'PVP_Manager')
        self.assertEqual(flow['user']['class_name'], 'DataUser')
        self.assertEqual(flow['download']['class_name'], 'FirebaseDatabaseManager')
        self.assertLess(flow['path']['rva'], flow['download']['rva'])

    def test_it_waits_twice(self):
        flow = payload()['flow']
        self.assertEqual(flow['wait_until']['class_name'], 'WaitUntil')
        self.assertEqual(flow['wait_seconds']['class_name'], 'WaitForSecondsRealtime')

    def test_it_compares_a_stored_date(self):
        flow = payload()['flow']
        self.assertEqual(flow['parse_date']['class_name'], 'DateTimeMethods')
        self.assertEqual(flow['less_than']['class_name'], 'DateTime')

    def test_it_deletes_or_hands_off(self):
        flow = payload()['flow']
        self.assertEqual(flow['delete']['class_name'], 'FirebaseDatabaseManager')
        self.assertEqual(flow['summary']['class_name'], 'Board_PVP')
        self.assertEqual(flow['load']['class_name'], 'Board_PVP')
        self.assertLess(flow['summary']['rva'], flow['load']['rva'])

    def test_it_starts_two_iterators(self):
        starts = [row for row in payload()['calls']
                  if 'StartCoroutine' in (row['signature'] or '')]
        self.assertEqual(len(starts), 2)


class Residue(unittest.TestCase):
    def test_three_open_items(self):
        self.assertEqual(len(payload()['open_items']), 3)

    def test_the_served_payload_is_runtime(self):
        self.assertIn('MODEL_NOT_MEASURED runtime',
                      payload()['open_items'][0]['detail'])

    def test_169_is_named_as_the_corrected_report(self):
        self.assertEqual(payload()['boundary']['correction_of'], 169)


class LiveDerivation(unittest.TestCase):
    def test_reads_recompute(self):
        self.assertEqual(PM.reads(), payload()['reads'])

    def test_reader_table_recomputes(self):
        self.assertEqual(PM.reader_table(PM.reads()), payload()['readers'])

    def test_flow_recomputes(self):
        self.assertEqual(PM.flow(), payload()['flow'])


if __name__ == '__main__':
    unittest.main()
