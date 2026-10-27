"""Contracts for report 145: the 26 store calls 144 left unnamed, resolved."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import store_key_callers  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_store_key_callers.json.gz'
PIN_SHA = '8759167e9268fdf28548aaab5bb2f3581296ebf9713b97c81c6afb476f3dd875'
NEW_KEYS = ['TIME_EVENT_ENDED', 'TIME_EVENT_STARTED', 'TIME_EVENT_OPEN']


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(store_key_callers.build_payload(),
                                        sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_sources(self):
        self.assertEqual(len(payload()['provenance']['sources']), 11)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])

    def test_lists_144_as_an_input(self):
        paths = [row['path'] for row in payload()['provenance']['sources']]
        self.assertIn('datas/l2_535b0541_game_store_keys.json.gz', paths)


class Census(unittest.TestCase):
    def test_same_184_calls(self):
        census = payload()['census']
        self.assertEqual(census['calls'], 184)
        self.assertEqual(census['by_api'], {'SetInt': 67, 'GetInt': 58, 'SetString': 32,
                                            'GetString': 25, 'DeleteKey': 2})

    def test_by_raw(self):
        self.assertEqual(payload()['census']['by_raw'],
                         {'meta-rewards-535b0541': 80, 'key-grant-535b0541': 49,
                          'arena-pvp-535b0541': 41, 'box-draw-535b0541': 10,
                          'key-jump-535b0541': 4})

    def test_nothing_is_unknown_any_more(self):
        by_kind = payload()['census']['by_kind']
        self.assertEqual(by_kind, {'literal': 133, 'computed': 51, 'unknown': 0})

    def test_before_and_after_add_up(self):
        census = payload()['census']
        self.assertEqual(census['before']['by_kind'],
                         {'literal': 115, 'computed': 43, 'unknown': 26})
        self.assertEqual(census['by_kind']['literal'] - 115, 18)
        self.assertEqual(census['by_kind']['computed'] - 43, 8)

    def test_tail_calls(self):
        self.assertEqual(payload()['census']['tail_calls'], 51)


class Resolution(unittest.TestCase):
    def test_counts(self):
        resolution = payload()['resolution']
        self.assertEqual(resolution['records'], 26)
        self.assertEqual(resolution['sites'], 22)
        self.assertEqual(resolution['by_kind'], {'literal': 18, 'computed': 8})
        self.assertEqual(resolution['by_mechanism'],
                         {'helper-return': 8, 'static-field': 18})

    def test_no_row_is_still_unknown(self):
        rows = payload()['resolved']
        self.assertEqual(len(rows), 22)
        self.assertTrue(all(row['kind'] in ('literal', 'computed') for row in rows))
        self.assertTrue(all(row['via'] for row in rows))

    def test_apis_split(self):
        rows = payload()['resolved']
        apis = sorted(row['api'] for row in rows)
        self.assertEqual(apis.count('GetString'), 11)
        self.assertEqual(apis.count('SetString'), 7)
        self.assertEqual(apis.count('GetInt'), 2)
        self.assertEqual(apis.count('SetInt'), 2)

    def test_helper_sites(self):
        rows = [row for row in payload()['resolved']
                if row['mechanism'] == 'helper-return']
        self.assertEqual(sorted(row['call_rva'] for row in rows),
                         [19186252, 19186340, 19187188, 19187916])
        self.assertTrue(all(row['prefix'] == 'SLOT_FREE_CARDS_' for row in rows))
        self.assertTrue(all(len(row['raws']) == 2 for row in rows))

    def test_static_sites(self):
        rows = [row for row in payload()['resolved']
                if row['mechanism'] == 'static-field']
        self.assertEqual(len(rows), 18)
        counts = {}
        for row in rows:
            counts[row['key']] = counts.get(row['key'], 0) + 1
        self.assertEqual(counts, {'TIME_EVENT_STARTED': 6, 'TIME_EVENT_ENDED': 9,
                                  'TIME_EVENT_OPEN': 3})


class Helper(unittest.TestCase):
    def test_identity(self):
        helper = payload()['helper']
        self.assertEqual(helper['rva'], 19187948)
        self.assertEqual(helper['class_name'], 'TimeFreeRewardPack')
        self.assertEqual(helper['signature'], 'public static string Key(int slot) { }')
        self.assertEqual(helper['prefix'], 'SLOT_FREE_CARDS_')

    def test_prefix_is_a_computed_bucket(self):
        values = {row['prefix']: row['calls'] for row in payload()['computed']['values']}
        self.assertEqual(values['SLOT_FREE_CARDS_'], 8)
        self.assertEqual(values[None], 1)
        self.assertEqual(sum(values.values()), 51)


class Statics(unittest.TestCase):
    def test_three_key_rows(self):
        rows = [row for row in payload()['statics']['rows']
                if row['key'] in NEW_KEYS]
        self.assertEqual(len(rows), 3)
        self.assertEqual({row['key']: row['offset'] for row in rows},
                         {'TIME_EVENT_STARTED': 16, 'TIME_EVENT_ENDED': 24,
                          'TIME_EVENT_OPEN': 32})
        self.assertEqual({row['key']: row['addend'] for row in rows},
                         {'TIME_EVENT_STARTED': 46031720, 'TIME_EVENT_ENDED': 46031704,
                          'TIME_EVENT_OPEN': 46031712})

    def test_one_writer_class_and_rva(self):
        rows = [row for row in payload()['statics']['rows'] if row['key'] in NEW_KEYS]
        self.assertEqual({row['writer_rva'] for row in rows}, {19462112})
        self.assertEqual({row['klass_cell'] for row in rows}, {44948920})

    def test_pair_store_carries_two_keys(self):
        rows = [row for row in payload()['statics']['rows'] if row['key'] in NEW_KEYS]
        kinds = {row['key']: (row['store'], row['writer_instruction']) for row in rows}
        self.assertEqual(kinds['TIME_EVENT_STARTED'], ('str', 19464560))
        self.assertEqual(kinds['TIME_EVENT_ENDED'], ('stp', 19464596))
        self.assertEqual(kinds['TIME_EVENT_OPEN'], ('stp', 19464596))

    def test_writer_identity(self):
        writer = payload()['statics']['writer']
        self.assertEqual(writer['rva'], 19462112)
        self.assertEqual(writer['signature'], 'private static void .cctor() { }')
        self.assertEqual(writer['klass_cell'], 44948920)

    def test_offset_is_the_class_static_fields_offset(self):
        self.assertEqual(payload()['model']['static_fields_offset'], 0xB8)


class Keys(unittest.TestCase):
    def test_new_keys(self):
        self.assertEqual(payload()['new_keys']['literal'], NEW_KEYS)
        self.assertEqual(payload()['new_keys']['prefixes'], ['SLOT_FREE_CARDS_'])

    def test_literal_keys_are_144_plus_three(self):
        rows = payload()['literal_keys']
        self.assertEqual(len(rows), 28)
        self.assertEqual([row['key'] for row in rows if not row['in_144']], NEW_KEYS)
        self.assertEqual(len([row for row in rows if row['in_144']]), 25)

    def test_call_counts_preserved(self):
        rows = {row['key']: row['calls'] for row in payload()['literal_keys']}
        self.assertEqual(rows['PRO_ExpiryDateTime'], 26)
        self.assertEqual(rows['TIME_EVENT_ENDED'], 9)
        self.assertEqual(rows['TIME_EVENT_STARTED'], 6)
        self.assertEqual(rows['TIME_EVENT_OPEN'], 3)
        self.assertEqual(sum(rows.values()), 133)


class CrossCheck(unittest.TestCase):
    def test_numbers(self):
        check = payload()['cross_check']
        self.assertEqual(check['report'], 144)
        self.assertEqual(check['calls'], 184)
        self.assertEqual((check['unknown_before'], check['unknown_after']), (26, 0))
        self.assertEqual((check['literal_before'], check['literal_after']), (115, 133))
        self.assertEqual((check['computed_before'], check['computed_after']), (43, 51))

    def test_not_decoded_stays_honest(self):
        items = payload()['not_decoded']
        self.assertEqual(len(items), 3)
        blocking = ' '.join(item['blocking'] for item in items)
        self.assertIn('MODEL_NOT_MEASURED runtime', blocking)
        self.assertIn('array length', blocking)


if __name__ == '__main__':
    unittest.main()
