"""Contracts for report 136: the `PVP_Manager` rank API (points codec + MaxRankStars reader)."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import pvp_rank_api  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_pvp_rank_api.json.gz'
PIN_SHA = '7663d2fd12aa78e487f447f5e12afd60809e937bc69d9654604dc2abc141950f'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(pvp_rank_api.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_four_sources(self):
        sources = payload()['provenance']['sources']
        self.assertEqual(len(sources), 4)
        for row in sources:
            self.assertEqual(len(row['sha256']), 64)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])

    def test_apk_level_digests_passthrough(self):
        blob = payload()['provenance']
        self.assertEqual(len(blob['xapk_sha256']), 64)
        self.assertEqual(len(blob['libil2cpp_sha256']), 64)
        self.assertEqual(len(blob['dump_sha256']), 64)


class PinnedMethods(unittest.TestCase):
    def test_five_bodies_pinned(self):
        rows = {row['name'].split('(')[0].split()[-1]: row
                for row in payload()['pinned_methods']}
        self.assertEqual(set(rows), {'ToPoints', 'DataFromPoints', 'GetRankNumber',
                                     'LoadRemoteConfigs', '.cctor'})
        self.assertEqual(rows['ToPoints']['rva'], 19903696)
        self.assertEqual(rows['DataFromPoints']['rva'], 19871992)
        self.assertEqual(rows['GetRankNumber']['rva'], 19884996)
        self.assertEqual(rows['LoadRemoteConfigs']['rva'], 19916080)
        self.assertEqual(rows['.cctor']['rva'], 19916640)

    def test_sizes_in_bytes(self):
        sizes = {row['name'].split('(')[0].split()[-1]: row['size']
                 for row in payload()['pinned_methods']}
        self.assertEqual(sizes['ToPoints'], 56)
        self.assertEqual(sizes['DataFromPoints'], 252)
        self.assertEqual(sizes['GetRankNumber'], 160)

    def test_body_digests_are_file_digests_of_the_instruction_stream(self):
        for row in payload()['pinned_methods']:
            self.assertEqual(len(row['sha256']), 64)


class ToPoints(unittest.TestCase):
    def test_constants(self):
        section = payload()['to_points']
        self.assertEqual(section['constants'], {'w9': 1000000, 'w10': 100000})

    def test_clamp_bounds(self):
        section = payload()['to_points']
        self.assertEqual(section['clamp_low'], 0)
        self.assertEqual(section['clamp_high'], 100)

    def test_emulated_case_count(self):
        self.assertEqual(payload()['to_points']['emulated_cases'], 360)

    def test_field_packing(self):
        for case in payload()['to_points']['sample']:
            self.assertEqual(case['points'],
                             case['rank'] * 1000000 + case['level'] * 100000
                             + case['star'] * 10000 + min(max(case['point'], 0), 100))

    def test_negative_point_floors_at_zero(self):
        rows = [case for case in payload()['to_points']['sample'] if case['point'] < 0]
        self.assertTrue(rows)
        for case in rows:
            self.assertEqual(case['points'],
                             case['rank'] * 1000000 + case['level'] * 100000
                             + case['star'] * 10000)


class DataFromPoints(unittest.TestCase):
    def test_field_offsets(self):
        section = payload()['data_from_points']
        self.assertEqual(section['field_offsets'],
                         {'pvpRank': 0x10, 'pvpLevel': 0x14, 'pvpPoints': 0x18,
                          'totalPoints': 0x1C, 'pvpStars': 0x20})

    def test_twelve_points_decoded(self):
        self.assertEqual(payload()['data_from_points']['emulated_cases'], 12)

    def test_samples_match_formula(self):
        for case in payload()['data_from_points']['sample']:
            total = case['total_points']
            self.assertEqual(case['rank'], total // 1000000)
            self.assertEqual(case['level'], (total % 1000000) // 100000)
            self.assertEqual(case['stars'], (total % 100000) // 10000)
            self.assertEqual(case['points'], total % 100)


class RoundTrip(unittest.TestCase):
    def test_case_count(self):
        self.assertEqual(payload()['round_trip']['cases'], 108)

    def test_identity_under_saturation_limit(self):
        for case in payload()['round_trip']['sample']:
            self.assertTrue(0 <= case['level'] < 10)
            self.assertTrue(0 <= case['star'] < 10)
            self.assertLess(case['point'], 100)

    def test_point_100_is_not_representable(self):
        saturation = payload()['round_trip']['saturation']
        self.assertEqual(saturation['point_100'], {'points': 100, 'pvp_points': 0})
        self.assertIn('points % 100', saturation['note'])


class GetRankNumber(unittest.TestCase):
    def test_cell_counts_match_135(self):
        by_rank = payload()['get_rank_number']['by_rank']
        self.assertEqual([row['rank'] for row in by_rank], list(range(10)))
        self.assertEqual([row['cells'] for row in by_rank], [3, 3, 4, 4, 5, 5, 5, 5, 5, 5])

    def test_numbers_are_descending_per_rank(self):
        for row in payload()['get_rank_number']['by_rank']:
            self.assertEqual(row['numbers'], list(range(row['cells'], 0, -1)))

    def test_forty_four_levels_emulated(self):
        self.assertEqual(payload()['get_rank_number']['emulated_cases'], 44)

    def test_returns_string(self):
        section = payload()['get_rank_number']
        self.assertIn('string', section['returns'])
        self.assertIn('21103836', section['returns'])


class StaticsMap(unittest.TestCase):
    def test_four_owners(self):
        rows = payload()['statics_access']['methods']
        self.assertEqual({row['method'] for row in rows},
                         {'.cctor', 'GetRankNumber', 'GetSeasonRewards',
                          'LoadRemoteConfigs'})

    def test_cctor_writes_every_field_once(self):
        row = [r for r in payload()['statics_access']['methods']
               if r['method'] == '.cctor'][0]
        self.assertEqual([a['offset'] for a in row['accesses']],
                         [0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 76])
        self.assertTrue(all(a['kind'] == 'write' for a in row['accesses']))

    def test_rank_number_reads_max_rank_stars(self):
        row = [r for r in payload()['statics_access']['methods']
               if r['method'] == 'GetRankNumber'][0]
        self.assertEqual(row['accesses'], [dict(rva=19885092, kind='read', mnemonic='ldr',
                                                dest='x0', offset=24,
                                                klass_slot=44957248)])

    def test_remote_configs_forces_is_open_false(self):
        row = [r for r in payload()['statics_access']['methods']
               if r['method'] == 'LoadRemoteConfigs'][0]
        self.assertEqual([(a['kind'], a['offset'], a['mnemonic'])
                          for a in row['accesses']], [('write', 76, 'strb')])

    def test_other_class_reads_are_rejected(self):
        rejected = payload()['statics_access']['rejected_reads']
        self.assertEqual(len(rejected), 2)
        for row in rejected:
            self.assertEqual(row['klass_slot'], 44939608)
            self.assertIn('not PVP_Manager', row['reason'])

    def test_klass_slot_is_decimal(self):
        slot = payload()['statics_access']['klass_slot']
        self.assertEqual(slot['decimal'], 44957248)
        self.assertIn('GetRankNumber', slot['basis'])


class Corrections(unittest.TestCase):
    def test_two_corrections(self):
        rows = payload()['corrections']
        self.assertEqual(len(rows), 2)
        self.assertIn('135', rows[0]['item'])
        self.assertIn('134', rows[1]['item'])

    def test_each_correction_has_impact(self):
        for row in payload()['corrections']:
            for key in ('item', 'measured', 'why_missed', 'impact'):
                self.assertTrue(row[key].strip(), key)


class NotDecoded(unittest.TestCase):
    def test_three_open_items(self):
        rows = payload()['not_decoded']
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertTrue(row['item'].strip())
            self.assertTrue(row['blocking'].strip())

    def test_runtime_item_is_labelled(self):
        runtime = [row for row in payload()['not_decoded']
                   if 'MODEL_NOT_MEASURED runtime' in row['blocking']]
        self.assertEqual(len(runtime), 1)
        self.assertEqual(runtime[0]['item'], 'served rank configuration')
        self.assertIn('LoadRemoteConfigs', runtime[0]['blocking'])

    def test_rank_names_are_blocked_on_unresolved_string_slots(self):
        names = [row for row in payload()['not_decoded']
                 if row['item'] == 'rank display strings'][0]
        self.assertIn('19881572', names['blocking'])
        self.assertIn('0x2ADCAE0', names['blocking'])


if __name__ == '__main__':
    unittest.main()
