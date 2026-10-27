"""Contracts for report 184: reconciling registry rows 50 / 51 / 52 against the pins.

The ledger in `datas/l2_535b0541_registry_v4.json.gz` is *not* rewritten here, so
these tests separate two things: the v4 bytes stay at their cut (`bcd0e0fd…`),
and the amendment rows say what changed and what is still a device question.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import registry_reconcile  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_registry_reconcile.json.gz'
LEDGER = ROOT / 'datas/l2_535b0541_registry_v4.json.gz'
PATHS_182 = ROOT / 'datas/l2_535b0541_firebase_paths.json.gz'
PIN_BYTES = 2432
PIN_SHA = 'b57602199ec2bd7e3d7530197fd087ecffbbe085138c160deef2eb387afc0ffa'
V4_BYTES = 4851
V4_SHA = 'bcd0e0fd95af375b8841021856209eb701d284bf013966d48f868e9143e21a96'
ARENA_ROOT = 22685676
CELL_52 = 44939608
CELL_51 = 44961792


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


def item(n):
    return payload()['items'][n - 50]


def slots(n):
    return {row['slot']: row for row in item(n)['slots']}


def paths_182():
    return json.loads(gzip.decompress(PATHS_182.read_bytes()))


class Pin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_payload(self):
        rebuilt = json.loads(json.dumps(registry_reconcile.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_rebuild_is_byte_identical(self):
        body = json.dumps(registry_reconcile.build_payload(), ensure_ascii=False,
                          sort_keys=True, separators=(',', ':')).encode('utf-8')
        self.assertEqual(gzip.compress(body, compresslevel=9, mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        self.assertEqual(payload()['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertEqual(payload()['schema'], 1)


class LedgerUntouched(unittest.TestCase):
    def test_v4_bytes_and_sha(self):
        blob = LEDGER.read_bytes()
        self.assertEqual(len(blob), V4_BYTES)
        self.assertEqual(hashlib.sha256(blob).hexdigest(), V4_SHA)

    def test_payload_records_that_cut(self):
        recorded = payload()['v4']
        self.assertEqual(recorded['bytes'], V4_BYTES)
        self.assertEqual(recorded['sha256'], V4_SHA)
        self.assertEqual(recorded['items'], 56)
        self.assertEqual(recorded['ledger'], 32)
        self.assertEqual(recorded['cut_report'], '180')

    def test_only_three_rows_gain_an_amendment(self):
        self.assertEqual(payload()['unchanged_rows'], 29)
        self.assertEqual([row['n'] for row in payload()['items']], [50, 51, 52])


class Provenance(unittest.TestCase):
    def test_sources_are_pinned(self):
        paths = [row['path'] for row in payload()['provenance']['sources']]
        self.assertEqual(len(paths), 5)
        self.assertIn('reverse-engineering/raw/ui-audit/native-relocations.json.gz', paths)
        self.assertIn('reverse-engineering/raw/ui-audit/metadata-index.json.gz', paths)
        self.assertIn('reverse-engineering/il2cpp/dump.cs.gz', paths)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])

    def test_table_sizes(self):
        tables = payload()['provenance']['tables']
        self.assertEqual(tables['relocations'], 288733)
        self.assertEqual(tables['script_metadata'], 10758)
        self.assertEqual(tables['script_strings'], 15054)


class Scan(unittest.TestCase):
    def test_scan_is_derived_from_the_text(self):
        scan = payload()['scan']
        self.assertEqual(scan['total'], 32)
        self.assertEqual(scan['rows_with_slots'], 3)
        self.assertEqual(scan['slots'], 4)
        self.assertEqual(scan['resolved'], 3)
        self.assertEqual(scan['unresolved'], 1)

    def test_rows_keep_their_v4_label(self):
        for row in payload()['scan']['rows']:
            self.assertEqual(row['label'], row['label_before'])
            self.assertEqual(row['verdict'], 'OPEN')

    def test_floor_ignores_offsets(self):
        # `// 0x0`, `+0xB8` etc. in a step are offsets, never slots.
        for row in payload()['scan']['rows']:
            for slot in row['slots']:
                self.assertGreaterEqual(slot, 0x1000000)


class Row50(unittest.TestCase):
    def test_amendment(self):
        row = item(50)
        self.assertEqual(row['label_before'], 'missing-input')
        self.assertEqual(row['label_after'], 'shipped-default')
        self.assertEqual(row['verdict_before'], 'OPEN')
        self.assertEqual(row['verdict_after'], 'STATIC_CONFIRMED')

    def test_three_cells(self):
        self.assertEqual(sorted(slots(50)), [45009312, 45009320, 45009328])

    def test_values(self):
        found = {row['slot']: row['value'] for row in item(50)['slots']}
        self.assertEqual(found[45009312], 'arena-test-datas')
        self.assertEqual(found[45009320], 'arena---datas')
        self.assertEqual(found[45009328], 'arena--datas')

    def test_load_sites_are_adjacent(self):
        for row in item(50)['slots']:
            self.assertEqual(row['ldr_rva'], row['adrp_rva'] + 4)

    def test_load_sites_agree_with_182(self):
        root = next(row for row in paths_182()['roots'] if row['rva'] == ARENA_ROOT)
        recorded = sorted(lit['load_rva'] for lit in root['literals']
                          if lit['cell'] in (45009312, 45009320, 45009328))
        self.assertEqual(recorded, sorted(row['adrp_rva'] for row in item(50)['slots']))

    def test_residual_is_runtime(self):
        residual = item(50)['residual']
        self.assertEqual(residual['label'], 'runtime-gated→USER')
        self.assertIn('MODEL_NOT_MEASURED runtime', residual['verdict'])


class Row51(unittest.TestCase):
    def test_stays_open(self):
        row = item(51)
        self.assertEqual(row['label_before'], 'policy')
        self.assertEqual(row['label_after'], 'policy')
        self.assertEqual(row['verdict_after'], 'OPEN')

    def test_slot_unresolved_and_never_loaded(self):
        self.assertEqual(slots(51)[CELL_51]['resolved'], False)
        self.assertEqual(item(51)['probe']['hits'], [])

    def test_probe_page(self):
        probe = item(51)['probe']
        self.assertEqual(probe['page'] + probe['offset'], CELL_51)


class Row52(unittest.TestCase):
    def test_amendment(self):
        row = item(52)
        self.assertEqual(row['label_before'], 'policy')
        self.assertEqual(row['label_after'], 'shipped-default')
        self.assertEqual(row['verdict_after'], 'STATIC_CONFIRMED')

    def test_class_is_named_by_the_relocation_table(self):
        row = slots(52)[CELL_52]
        self.assertEqual(row['kind'], 'metadata')
        self.assertEqual(row['value'], 'FirebaseDatabaseManager_TypeInfo')

    def test_static_field_zero_is_declared(self):
        declaration = item(52)['declaration']
        self.assertEqual(declaration['field_offset'], 0)
        self.assertIn('public static FirebaseDatabaseManager Instance', declaration['field_line'])
        self.assertIn('MonoBehaviour', declaration['class_line'])

    def test_census_covers_the_same_sites_as_181(self):
        census = item(52)['census']
        self.assertEqual(census['sites'], 141)
        self.assertEqual(census['methods'], 34)
        self.assertEqual(len(census['raws']), 3)

    def test_every_statics_read_is_offset_zero(self):
        census = item(52)['census']
        self.assertEqual(census['statics_offsets'], {'0': 56})

    def test_tags_account_for_every_site(self):
        census = item(52)['census']
        self.assertEqual(sum(census['tags'].values()), 141)
        self.assertEqual(census['tags']['statics(klass+0xB8)'], 56)


class Deliverable(unittest.TestCase):
    def test_all_checks_pass(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 19)
        self.assertEqual([row['name'] for row in checks if not row['ok']], [])

    def test_runtime_row_is_not_promoted(self):
        self.assertEqual(payload()['audit_53'], 'RUNTIME')

    def test_not_measured_is_labelled(self):
        rows = payload()['not_measured']
        self.assertEqual(len(rows), 3)
        self.assertTrue(all('MODEL_NOT_MEASURED runtime' in row for row in rows))

    def test_note_refuses_to_rewrite_v4(self):
        self.assertIn('v4 is not rewritten', payload()['note'])


if __name__ == '__main__':
    unittest.main()
