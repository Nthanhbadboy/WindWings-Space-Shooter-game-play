"""Contracts for report 138: PvP/Arena `LoadRemoteConfigs` — paths, gates, callback."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import remote_configs  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_remote_configs.json.gz'
PIN_SHA = '258f68c07024cae59eae0e64d1a13fde33d666d1f97217bfd0fa0b4ef51043f5'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(remote_configs.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_three_sources(self):
        self.assertEqual(len(payload()['provenance']['sources']), 3)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])


class Paths(unittest.TestCase):
    def test_six_pvp_getters(self):
        rows = payload()['paths']['getters']
        self.assertEqual([row['name'] for row in rows],
                         ['get_pathRoot', 'get_pathOfDataConfigs', 'get_pathOfDataRanks',
                          'get_pathOfDataUsers', 'get_pathOfDataPlayOfUsers',
                          'get_pathOfDataPlayOfMachines'])

    def test_concat_values(self):
        values = {row['name']: row['value'] for row in payload()['paths']['getters']}
        self.assertEqual(values['get_pathRoot'], 'data-leagues')
        self.assertEqual(values['get_pathOfDataConfigs'], 'data-leagues/data-configs')
        self.assertEqual(values['get_pathOfDataRanks'], 'data-leagues/data-ranks')
        self.assertEqual(values['get_pathOfDataPlayOfMachines'],
                         'data-leagues/data-play/data-play-machines')

    def test_getter_rvas(self):
        rvas = {row['name']: row['rva'] for row in payload()['paths']['getters']}
        self.assertEqual(rvas['get_pathOfDataConfigs'], 19915932)
        self.assertEqual(rvas['get_pathOfDataRanks'], 19874728)

    def test_arena_root_branches(self):
        root = payload()['paths']['arena_root']
        self.assertEqual(len(root['branches']), 3)
        self.assertEqual(root['branches'][2]['result'], 'arena---datas')
        witness_rvas = [row['rva'] for row in root['method']['witnesses']]
        self.assertIn(22685812, witness_rvas)   # string.op_Equality
        self.assertIn(22685836, witness_rvas)   # PREMIUM


class Parents(unittest.TestCase):
    def test_two_parents(self):
        rows = payload()['remote_configs']['parents']
        self.assertEqual([row['class_name'] for row in rows],
                         ['PVP_Manager', 'ArenaManager'])
        self.assertEqual([row['size'] for row in rows], [544, 548])

    def test_witness_counts(self):
        rows = {row['class_name']: row for row in payload()['remote_configs']['parents']}
        self.assertEqual(len(rows['PVP_Manager']['witnesses']), 10)
        self.assertEqual(len(rows['ArenaManager']['witnesses']), 11)

    def test_both_log_no_network(self):
        for row in payload()['remote_configs']['parents']:
            self.assertIn('No network connected',
                          [item['value'] for item in row['literals']], row['class_name'])

    def test_arena_path_suffix(self):
        rows = {row['class_name']: row for row in payload()['remote_configs']['parents']}
        self.assertIn('/is-open',
                      [item['value'] for item in rows['ArenaManager']['literals']])

    def test_download_database_tail_call(self):
        for row in payload()['remote_configs']['parents']:
            sigs = [call['signature'] for call in row['calls'] if call['signature']]
            self.assertTrue(any('DownloadDatabase' in sig for sig in sigs), row['class_name'])

    def test_network_guard_present(self):
        for row in payload()['remote_configs']['parents']:
            sigs = [call['signature'] for call in row['calls'] if call['signature']]
            self.assertTrue(any('get_internetReachability' in sig for sig in sigs))


class Handlers(unittest.TestCase):
    def test_two_handlers(self):
        rows = payload()['remote_configs']['handlers']
        self.assertEqual([row['rva'] for row in rows], [19936584, 22705216])
        self.assertEqual([row['size'] for row in rows], [260, 244])

    def test_handlers_have_no_literals(self):
        for row in payload()['remote_configs']['handlers']:
            self.assertEqual(row['literals'], [])

    def test_arena_handler_parses_int(self):
        row = payload()['remote_configs']['handlers'][1]
        sigs = [call['signature'] for call in row['calls'] if call['signature']]
        self.assertTrue(any('Parse' in sig for sig in sigs))
        witness_rvas = [item['rva'] for item in row['witnesses']]
        self.assertIn(22705348, witness_rvas)   # cset w9, gt


class Gates(unittest.TestCase):
    def test_pvp_gate(self):
        gate = payload()['remote_configs']['gates'][0]
        self.assertEqual((gate['class_name'], gate['offset']), ('PVP_Manager', 0x4C))
        self.assertEqual(len(gate['writes']), 4)
        self.assertTrue(gate['fail_closed'])

    def test_arena_gate(self):
        gate = payload()['remote_configs']['gates'][1]
        self.assertEqual((gate['class_name'], gate['offset']), ('ArenaManager', 0x1C))
        self.assertEqual(gate['source'], 'Int32.Parse(snapshot raw json) > 0')

    def test_callback_contract(self):
        callback = payload()['remote_configs']['callback']
        self.assertEqual(callback['type'], 'Action<bool>')
        self.assertIn('no internet', callback['false_when'])


class Corrections(unittest.TestCase):
    def test_roman_numeral_correction(self):
        rows = payload()['corrections']
        self.assertEqual(len(rows), 1)
        self.assertIn('ToRoman', rows[0]['measured'])
        self.assertIn('21103836', rows[0]['measured'])
        self.assertIn('137', rows[0]['impact'])


class NotDecoded(unittest.TestCase):
    def test_four_open_items(self):
        self.assertEqual(len(payload()['not_decoded']), 4)

    def test_served_values_are_runtime(self):
        runtime = [row for row in payload()['not_decoded']
                   if 'MODEL_NOT_MEASURED runtime' in row['blocking']]
        self.assertEqual(len(runtime), 1)
        self.assertIn('Firebase', runtime[0]['blocking'])

    def test_root_variants_are_unread(self):
        roots = [row for row in payload()['not_decoded']
                 if row['item'] == 'ArenaManager root variants'][0]
        self.assertIn('0x2AEC9A0', roots['blocking'])
        self.assertIn('0x2AEC9B0', roots['blocking'])


if __name__ == '__main__':
    unittest.main()
