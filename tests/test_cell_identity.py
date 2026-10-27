"""Contracts for report 150: the lane's unnamed metadata cells."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import cell_identity  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_cell_identity.json.gz'
PIN_SHA = '23be51eba7d4cc82e597788341eb51f8d63784ab2091c51f9e352318192c2e5b'
PIN_BYTES = 8053


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


def cell(hex_):
    for row in payload()['cells']:
        if row['hex'] == hex_:
            return row
    raise AssertionError(hex_)


class ArtifactPin(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces(self):
        rebuilt = json.loads(json.dumps(cell_identity.build(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        self.assertEqual(payload()['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', payload()['note'])


class RuleK(unittest.TestCase):
    def test_control_cases(self):
        """The rule is only a rule if it agrees with the cells already named."""
        self.assertEqual(cell('0x2ADB8E0')['kind']['kind'], 'type')
        self.assertEqual(cell('0x2ADF238')['kind']['kind'], 'type')
        self.assertEqual(cell('0x2ADF3E0')['kind']['literal'], 'Test')
        self.assertEqual(cell('0x2AEC9A8')['kind']['literal'], 'arena---datas')

    def test_strings_come_from_the_pinned_table(self):
        literals = {int(row['address'], 16): row['value'] for row in
                    json.loads((ROOT / 'reverse-engineering/il2cpp/stringliteral.json')
                               .read_text())}
        self.assertEqual(literals[46033008], 'Test')
        self.assertEqual(literals[46051720], 'arena---datas')

    def test_unrecorded_cells_are_admitted(self):
        for row in payload()['cells']:
            if row['kind']['kind'] == 'unrecorded':
                self.assertIsNone(row['kind']['addend'])
                self.assertIn('no addend', row['kind']['why'])


class RuleC(unittest.TestCase):
    def test_board_pvp_is_named(self):
        row = cell('0x2ADF238')
        self.assertEqual(row['name'], 'Board_PVP')
        self.assertEqual(row['named_by'], 150)

    def test_layout_is_unique(self):
        naming = cell('0x2ADF238')['naming']
        self.assertEqual(naming['layout_matches'], ['Board_PVP'])
        self.assertTrue(naming['layout_unique'])

    def test_the_writes_cover_the_declared_statics(self):
        naming = cell('0x2ADF238')['naming']
        layout = {row['offset']: row['type'] for row in naming['declared_layout']}
        self.assertEqual(layout, {0: 'BoardID', 4: 'int', 8: 'string',
                                  16: 'int', 20: 'int', 24: 'int'})
        self.assertEqual([(row['offset'], row['width']) for row in naming['writes']],
                         [(0, 8), (16, 8), (24, 4)])
        # the only field not written is the null string
        self.assertEqual(naming['null_defaulted'], [{'offset': 8, 'type': 'string'}])

    def test_packed_literal_decodes_to_board_and_energy(self):
        board = payload()['board_pvp']
        self.assertEqual(board['packed_literal']['ints'], [1, 15])
        self.assertEqual([row['declared'] for row in board['decoded']],
                         ['backBoard', 'costEnergy'])
        self.assertEqual([row['value'] for row in board['decoded']], [1, 15])

    def test_board_id_one_is_board_home(self):
        text = gzip.decompress(
            (ROOT / 'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()).decode()
        self.assertIn('public const BoardID BoardHome = 1;', text)

    def test_bet_handlers_and_a_reader_use_the_cell(self):
        signatures = {row['signature'] for row in payload()['board_pvp']['consumers']}
        self.assertEqual(len(signatures), 5)
        self.assertTrue(any('OnChangeCoins' in s for s in signatures))
        self.assertTrue(any('AddBetValues' in s for s in signatures))


class GetPathRoot(unittest.TestCase):
    def test_three_roots(self):
        root = payload()['get_path_root']
        self.assertEqual([row['returns']['hex'] for row in root['branches']],
                         ['0x2AEC9A0', '0x2AEC9B0', '0x2AEC9A8'])

    def test_call_targets_are_named_from_dump(self):
        calls = {row['target_rva']: row for row in payload()['get_path_root']['calls']}
        self.assertEqual(calls[41274380]['klass'], 'Application')
        self.assertEqual(calls[41274380]['signature'], 'public static string get_companyName() { }')
        self.assertEqual(calls[20068044]['klass'], 'VersionControlSystem')
        self.assertEqual(calls[20068044]['signature'], 'public static bool get_PREMIUM() { }')
        self.assertEqual(calls[33475124]['signature'],
                         'public static bool op_Equality(string a, string b) { }')

    def test_fallback_is_the_new_branch(self):
        root = payload()['get_path_root']
        fallback = root['branches'][2]
        self.assertEqual(fallback['test'], 'neither')
        self.assertEqual(fallback['returns']['kind']['literal'], 'arena---datas')


class Corrections(unittest.TestCase):
    def test_two_corrections(self):
        rows = payload()['corrections']
        self.assertEqual(sorted(row['target'] for row in rows), [138, 149])

    def test_the_138_correction_names_the_third_branch(self):
        row = [row for row in payload()['corrections'] if row['target'] == 138][0]
        self.assertEqual(row['evidence']['fallback_literal'], 'arena---datas')
        self.assertEqual(row['evidence']['fallback_addend'], 46051720)
        self.assertIn('three returns', row['correction'])

    def test_the_149_correction_closes_the_cell(self):
        row = [row for row in payload()['corrections'] if row['target'] == 149][0]
        self.assertEqual(row['evidence']['klass'], 'Board_PVP')


class Totals(unittest.TestCase):
    def test_counts(self):
        totals = payload()['totals']
        self.assertEqual(totals['cells'], 8)
        self.assertEqual(totals['resolved'], 3)
        self.assertEqual(sorted(totals['unresolved']),
                         ['0x2ADB958', '0x2AE1000', '0x2AEC9A0', '0x2AEC9B0'])

    def test_named_holds_the_source_report(self):
        named = payload()['totals']['named']
        self.assertEqual(named['0x2ADB8E0'], {'klass': 'UnityEngine.Application', 'by': 142})
        self.assertEqual(named['0x2ADF238'], {'klass': 'Board_PVP', 'by': 150})

    def test_checks_all_pass(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 13)
        self.assertTrue(all(row['passed'] for row in checks))

    def test_open_items_carry_a_blocker(self):
        rows = payload()['open_items']
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row['blocking'] for row in rows))


class TokenIndex(unittest.TestCase):
    def test_every_cell_has_one_token(self):
        for row in payload()['cells']:
            if row['token']['kind'] is None:
                self.assertFalse(row['uses'], row['hex'])
            else:
                self.assertTrue(row['token']['consistent'], row['hex'])

    def test_kind_agrees_with_rule_k(self):
        pairs = {row['hex']: row for row in payload()['cells']}
        self.assertEqual(pairs['0x2ADB8E0']['token']['kind_name'], 'type')
        self.assertEqual(pairs['0x2ADF3E0']['token']['kind_name'], 'string-literal')
        self.assertEqual(pairs['0x2AE1000']['token']['kind_name'], 'method-ref')

    def test_indices_are_recorded_for_the_open_cells(self):
        index = payload()['token_index']
        self.assertEqual(index['kind_5'][1], {'hex': '0x2AEC9A8', 'index': 20957,
                                              'literal': 'arena---datas'})
        self.assertEqual(index['kind_6'], [{'hex': '0x2AE1000', 'index': 121683}])
        open_ = [row for row in index['kind_1'] if row['hex'] == '0x2ADB958'][0]
        self.assertEqual(open_['index'], 25385)


class Provenance(unittest.TestCase):
    def test_scope(self):
        self.assertEqual(payload()['provenance']['raws_scanned'], 8)
        self.assertEqual(payload()['provenance']['token_cells'],
                         payload()['provenance']['token_consistent'])

    def test_four_sources(self):
        sources = payload()['provenance']['sources']
        self.assertEqual(len(sources), 4)
        for row in sources:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])


if __name__ == '__main__':
    unittest.main()
