"""Contracts for report 183: the base behind every Firebase path literal."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import path_bases  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_path_bases.json.gz'
PIN_BYTES = 4578
PIN_SHA = '0f2d3872ea1f62402f28745f3dfb830d0988ace2261318563c0078e63a4789be'
PVP_ROOT = 19859292
ARENA_ROOT = 22685676


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


def literals():
    return {row['value']: row for row in payload()['literals']}


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(path_bases.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_sources(self):
        paths = [row['path'] for row in payload()['provenance']['sources']]
        self.assertIn('reverse-engineering/raw/ui-audit/native-relocations.json.gz', paths)
        self.assertIn('reverse-engineering/raw/ui-audit/metadata-index.json.gz', paths)
        self.assertEqual(len([path for path in paths if path.endswith('native.json.gz')]), 8)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])


class Method(unittest.TestCase):
    def test_window_and_hops(self):
        method = payload()['method']
        self.assertEqual(method['window'], 24)
        self.assertEqual(method['hops'], 1)

    def test_six_labels(self):
        self.assertEqual(sorted(payload()['method']['labels']),
                         ['call', 'cell', 'constant', 'field', 'register', 'unknown'])

    def test_caveat_is_not_overclaimed(self):
        self.assertIn('not a proof of absence', payload()['method']['caveat'])


class RoomChain(unittest.TestCase):
    def chain(self):
        return payload()['room_chain']

    def test_producer_formats_the_room_base_from_the_pvp_root(self):
        producer = self.chain()['producer']
        self.assertEqual(producer['rva'], 21267840)
        self.assertEqual(producer['root_call'], PVP_ROOT)
        self.assertEqual(producer['root_name'], 'PVP_Manager.get_pathRoot')
        self.assertEqual(producer['template'], '{0}/data-solos/{1}')
        self.assertEqual(producer['template_cell'], 44958416)
        self.assertEqual(producer['field'], 32)
        self.assertEqual(producer['field_store'], 21270168)

    def test_consumer_queries_the_base_and_its_channels(self):
        consumer = self.chain()['consumer']
        self.assertEqual(consumer['rva'], 21264984)
        self.assertEqual(consumer['query_calls'], [21265220, 21265356, 21265484])
        self.assertEqual([row['literal'] for row in consumer['concat_sites']],
                         ['/playerScores', '/playerChats'])
        self.assertTrue(all(row['base_field'] == 32 for row in consumer['concat_sites']))

    def test_verdict_names_both_channels(self):
        verdict = self.chain()['verdict']
        self.assertEqual(verdict['room_base'], 'data-leagues/data-solos/<roomId>')
        self.assertEqual(verdict['channels'],
                         ['data-leagues/data-solos/<roomId>/playerChats',
                          'data-leagues/data-solos/<roomId>/playerScores'])
        self.assertIn('MODEL_NOT_MEASURED runtime', verdict['note'])


class Literals(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(payload()['literals']), 28)

    def test_base_summary(self):
        self.assertEqual(payload()['base_summary'],
                         {'call': 17, 'field': 7, 'cell': 2, 'register': 18, 'unknown': 8})

    def test_is_open_comes_from_the_arena_root(self):
        row = literals()['/is-open']
        self.assertEqual([use['base_name'] for use in row['uses']],
                         ['ArenaManager.get_pathRoot'])
        self.assertEqual(row['uses'][0]['base_rva'], ARENA_ROOT)
        self.assertEqual(row['uses'][0]['call_rva'], 22692140)

    def test_user_list_comes_from_the_arena_root_four_times(self):
        row = literals()['/user-datas/userList/']
        self.assertEqual(len(row['uses']), 4)
        self.assertTrue(all(use['base_name'] == 'ArenaManager.get_pathRoot'
                            for use in row['uses']))

    def test_summary_payload_path_comes_from_the_arena_root(self):
        row = literals()['{0}/summary-datas/season-{1}/rank-{2}/rooms/roomList/room-{3}']
        self.assertEqual([use['base_name'] for use in row['uses']],
                         ['ArenaManager.get_pathRoot'])
        self.assertEqual([use['base_reg'] for use in row['uses']], ['array0'])
        self.assertEqual([use['call_rva'] for use in row['uses']], [22687560])

    def test_machine_path_comes_from_the_machines_getter(self):
        row = literals()['{0}/rank-{1}/map-{2}/{3}']
        self.assertEqual([use['base_name'] for use in row['uses']],
                         ['PVP_Manager.get_pathOfDataPlayOfMachines'])

    def test_solos_template_has_both_a_call_base_and_a_literal_base(self):
        row = literals()['{0}/data-solos/{1}']
        kinds = {use['base_kind']: use['base_name'] for use in row['uses']}
        self.assertEqual(kinds['call'], 'PVP_Manager.get_pathRoot')
        self.assertEqual(kinds['cell'], 'data-leagues')

    def test_channels_hang_off_a_closure_field(self):
        for value in ('/playerChats', '/playerScores'):
            row = literals()[value]
            self.assertTrue(row['uses'], value)
            self.assertTrue(all(use['base_kind'] == 'field' for use in row['uses']), value)


class Census(unittest.TestCase):
    def test_thirty_four_methods(self):
        self.assertEqual(len(payload()['census']['rows']), 34)

    def test_root_calls_are_named(self):
        rows = payload()['census']['rows']
        named = {name for row in rows for name in row['root_calls']}
        self.assertIn('PVP_Manager.get_pathRoot', named)
        self.assertIn('ArenaManager.get_pathRoot', named)

    def test_every_row_keeps_its_rva(self):
        for row in payload()['census']['rows']:
            self.assertIsInstance(row['rva'], int)
            self.assertGreater(row['rva'], 19000000)


class Audit(unittest.TestCase):
    def test_item_53_still_runtime(self):
        block = payload()['audit_corroboration']
        self.assertEqual(block['item'], 53)
        self.assertIn('RUNTIME', block['verdict'])
        self.assertEqual(block['here']['is_open_base'], ['ArenaManager.get_pathRoot'])


class NotDecoded(unittest.TestCase):
    def test_four_items_with_blocking_steps(self):
        rows = payload()['not_decoded']
        self.assertEqual(len(rows), 4)
        for row in rows:
            self.assertTrue(row['item'])
            self.assertTrue(row['blocking'])
        self.assertIn('UNKNOWN, not missing', rows[1]['blocking'])


if __name__ == '__main__':
    unittest.main()
