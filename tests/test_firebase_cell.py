"""Contracts for report 181: slot `0x2ADB958` is the `FirebaseDatabaseManager` klass cell."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import firebase_cell  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_firebase_cell.json.gz'
PIN_SHA = 'a6d4c430fcdfaa2add5de13c7d7082ee9aab7b64809db802ead3c75c7a1c3cce'
CELL = 44939608
NEIGHBOUR = 44939488


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(firebase_cell.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])

    def test_under_size_budget(self):
        self.assertLess(ARTIFACT.stat().st_size, 5 * 1024 * 1024)


class Provenance(unittest.TestCase):
    def test_sources_cover_dump_slots_and_eight_raws(self):
        rows = payload()['provenance']['sources']
        self.assertEqual(len(rows), 10)
        paths = [row['path'] for row in rows]
        self.assertIn('reverse-engineering/il2cpp/dump.cs.gz', paths)
        self.assertIn('reverse-engineering/raw/ui-audit/metadata-slots.json', paths)
        self.assertEqual(len([path for path in paths if path.endswith('native.json.gz')]), 8)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])

    def test_apk_digests_present(self):
        prov = payload()['provenance']
        for key in ('xapk_sha256', 'libil2cpp_sha256', 'dump_sha256'):
            self.assertEqual(len(prov[key]), 64, key)


class Cell(unittest.TestCase):
    def test_decimal(self):
        self.assertEqual(payload()['cell']['decimal'], CELL)

    def test_no_hex_in_the_artifact_addresses(self):
        blob = payload()
        self.assertEqual(blob['cell']['va'], blob['cell']['decimal'])
        self.assertEqual(blob['cell']['neighbour_from_142']['va'], NEIGHBOUR)

    def test_class_and_gate_neighbour(self):
        cell = payload()['cell']
        self.assertEqual(cell['klass'], 'FirebaseDatabaseManager')
        self.assertEqual(cell['neighbour_from_142']['klass'], 'UnityEngine.Application')
        self.assertEqual(cell['delta'], CELL - NEIGHBOUR)

    def test_instance_field_is_offset_zero(self):
        field = payload()['cell']['field']
        self.assertEqual(field['name'], 'Instance')
        self.assertEqual(field['offset'], 0)
        self.assertIn('// 0x0', field['declaration'])

    def test_identification_has_four_independent_tests(self):
        tests = [row['test'] for row in payload()['cell']['identification']]
        self.assertEqual(tests, ['klass-cell idiom', 'statics read offset',
                                 'statics+0x0 is `this`', 'dump.cs field'])


class Census(unittest.TestCase):
    def test_counts(self):
        census = payload()['census']
        self.assertEqual(census['distinct_methods'], 34)
        self.assertEqual(census['pairs'], 54)
        self.assertEqual(census['sites'], 141)

    def test_per_raw_sums_to_pairs(self):
        census = payload()['census']
        self.assertEqual(sum(census['per_raw'].values()), census['pairs'])
        self.assertEqual(census['per_raw'],
                         {'arena-pvp-535b0541': 34, 'key-grant-535b0541': 8,
                          'meta-rewards-535b0541': 12})

    def test_every_statics_read_is_offset_zero(self):
        rows = payload()['census']['rows']
        offsets = sorted({offset for row in rows for offset in row['statics_offsets']})
        self.assertEqual(offsets, [0])
        self.assertEqual(len([row for row in rows if row['statics_offsets']]), 30)

    def test_every_row_is_a_class_init_site(self):
        rows = payload()['census']['rows']
        self.assertTrue(all('class_init(0x110D028)' in row['idiom'] for row in rows))

    def test_rows_are_distinct_methods_per_raw(self):
        rows = payload()['census']['rows']
        keys = {(row['raw'], row['rva']) for row in rows}
        self.assertEqual(len(keys), len(rows))
        self.assertEqual(len({row['rva'] for row in rows}), 34)


class ApiCensus(unittest.TestCase):
    def test_distinct_call_sites(self):
        self.assertEqual(payload()['api_census']['calls_distinct'], 59)

    def test_per_api_sites_over_raws(self):
        self.assertEqual(payload()['api_census']['calls_per_raw'],
                         {'FirebaseDatabaseManager.DownloadDatabase': 44,
                          'FirebaseDatabaseManager.UploadDatabase': 33,
                          'FirebaseDatabaseManager.DeleteDatabase': 7,
                          'FirebaseDatabaseManager.Query': 6,
                          'FirebaseDatabaseManager.DownloadDatabaseQueryRank': 2,
                          'FirebaseDatabaseManager.UploadDatabaseObj': 1})

    def test_per_api_distinct_methods(self):
        self.assertEqual(payload()['api_census']['methods_distinct'],
                         {'FirebaseDatabaseManager.DownloadDatabase': 20,
                          'FirebaseDatabaseManager.UploadDatabase': 14,
                          'FirebaseDatabaseManager.DeleteDatabase': 4,
                          'FirebaseDatabaseManager.Query': 2,
                          'FirebaseDatabaseManager.DownloadDatabaseQueryRank': 1,
                          'FirebaseDatabaseManager.UploadDatabaseObj': 1})

    def test_api_rvas_are_decimal_and_pinned(self):
        self.assertEqual(payload()['api_census']['rvas'],
                         {'FirebaseDatabaseManager.DownloadDatabase': 21150628,
                          'FirebaseDatabaseManager.UploadDatabase': 21149804,
                          'FirebaseDatabaseManager.Query': 21152032,
                          'FirebaseDatabaseManager.DeleteDatabase': 21149616,
                          'FirebaseDatabaseManager.DownloadDatabaseQueryRank': 21150980,
                          'FirebaseDatabaseManager.UploadDatabaseObj': 21150216})

    def test_raw_counts_bound_the_distinct_counts(self):
        api = payload()['api_census']
        for name, count in api['methods_distinct'].items():
            self.assertLessEqual(count, api['calls_distinct'], name)
        self.assertEqual(sum(api['calls_per_raw'].values()), 93)


class Helpers(unittest.TestCase):
    def test_helper_census(self):
        self.assertEqual(payload()['helper_census']['calls'],
                         {'unresolved@0x18a5580': 23, 'unresolved@0x18a4388': 15,
                          'JsonParse.ToJson': 14, 'UnityEngine.Object.op_Implicit': 8,
                          'UnityEngine.Time.get_time': 2,
                          'FirebaseAuthManager.SignInWithGooglePlayGames': 2})

    def test_unresolved_rvas_are_named_as_such(self):
        names = payload()['helper_census']['calls']
        self.assertTrue(any(name.startswith('unresolved@0x') for name in names))


class HelperRvas(unittest.TestCase):
    def test_helpers_carry_decimal_rvas(self):
        self.assertEqual(payload()['helper_census']['rvas'],
                         {'UnityEngine.Object.op_Implicit': 41437640,
                          'UnityEngine.Time.get_time': 41446848,
                          'JsonParse.ToJson': 20888684,
                          'FirebaseAuthManager.SignInWithGooglePlayGames': 21141540,
                          'unresolved@0x18a4388': 25838472,
                          'unresolved@0x18a5580': 25843072})


class RetryLoop(unittest.TestCase):
    def test_the_one_row_without_an_api_call_is_the_wait_loop(self):
        rows = payload()['census']['rows']
        idle = [row for row in rows if not row['api_calls']]
        self.assertEqual(len(idle), 1)
        self.assertEqual(idle[0]['rva'], 22814532)
        self.assertEqual(payload()['retry_loop']['rva'], 22814532)

    def test_it_waits_on_the_singleton_and_the_clock(self):
        loop = payload()['retry_loop']
        self.assertEqual(loop['instance_load']['rva'], 22815084)
        self.assertEqual([row['name'] for row in loop['null_checks']],
                         ['UnityEngine.Object.op_Implicit'] * 3)
        self.assertEqual([row['name'] for row in loop['clock_reads']],
                         ['UnityEngine.Time.get_time'] * 2)
        self.assertEqual([row['text'] for row in loop['deadline']],
                         ['fmov s1, #10.00000000'])

    def test_the_loop_is_not_a_database_write(self):
        self.assertIn('writes nothing to Firebase', payload()['retry_loop']['rule'])


class Coverage(unittest.TestCase):
    def test_index_agrees_with_the_scan_here(self):
        cover = payload()['coverage']
        self.assertEqual(cover['scanned'], cover['indexed'])
        self.assertEqual(cover['scanned'], 54)
        self.assertEqual(cover['missing_from_slot_refs'], [])

    def test_note_contrasts_with_142(self):
        self.assertIn('45 of 47', payload()['coverage']['note'])


class NotDecoded(unittest.TestCase):
    def test_three_items_each_with_a_blocking_step(self):
        rows = payload()['not_decoded']
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertTrue(row['item'])
            self.assertTrue(row['blocking'])
        self.assertIn('MODEL_NOT_MEASURED runtime', rows[0]['blocking'])

    def test_string_prefixes_are_cells_not_literals(self):
        self.assertIn('string *cells*', payload()['not_decoded'][1]['blocking'])


if __name__ == '__main__':
    unittest.main()
