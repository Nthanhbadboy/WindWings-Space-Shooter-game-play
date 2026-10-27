"""Contracts for report 182: the Firebase path schema, resolved through the relocation table."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import firebase_paths  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_firebase_paths.json.gz'
PIN_SHA = '3dcbbb832ccf6a0e47817f31834e40b40eec80b24af0f69e361bae19aa1baa16'
IDENTITY_CELL = 44939608
IDENTITY_TARGET = 45771320
IS_OPEN_CELL = 44950432


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(firebase_paths.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])

    def test_under_size_budget(self):
        self.assertLess(ARTIFACT.stat().st_size, 5 * 1024 * 1024)


class Provenance(unittest.TestCase):
    def test_sources_cover_the_two_tables_dump_and_eight_raws(self):
        rows = payload()['provenance']['sources']
        paths = [row['path'] for row in rows]
        self.assertIn('reverse-engineering/raw/ui-audit/native-relocations.json.gz', paths)
        self.assertIn('reverse-engineering/raw/ui-audit/metadata-index.json.gz', paths)
        self.assertIn('reverse-engineering/il2cpp/dump.cs.gz', paths)
        self.assertEqual(len([path for path in paths if path.endswith('native.json.gz')]), 8)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])

    def test_apk_digests_present(self):
        prov = payload()['provenance']
        for key in ('xapk_sha256', 'libil2cpp_sha256', 'dump_sha256'):
            self.assertEqual(len(prov[key]), 64, key)


class Resolver(unittest.TestCase):
    def test_table_sizes(self):
        resolver = payload()['resolver']
        self.assertEqual(resolver['relocations'], 288733)
        self.assertEqual(resolver['script_strings'], 15054)
        self.assertEqual(resolver['script_metadata'], 10758)

    def test_rule_is_a_two_table_lookup(self):
        self.assertIn('relocations[cell]', payload()['resolver']['rule'])
        self.assertEqual(payload()['resolver']['method'],
                         'two-table lookup, no disassembly of the data page and no .so')

    def test_resolver_reproduces_the_181_identity(self):
        check = payload()['identity_crosscheck']
        self.assertEqual(check['cell'], IDENTITY_CELL)
        self.assertEqual(check['target'], IDENTITY_TARGET)
        self.assertEqual(check['metadata'], 'FirebaseDatabaseManager_TypeInfo')
        self.assertEqual(check['application_cell'], 44939488)
        self.assertEqual(check['application_metadata'], 'UnityEngine.Application_TypeInfo')

    def test_the_crosscheck_says_it_is_independent_of_181(self):
        self.assertIn('independent fifth test',
                      payload()['identity_crosscheck']['note'])


class Roots(unittest.TestCase):
    def roots(self):
        return {row['name']: row for row in payload()['roots']}

    def test_seven_getters(self):
        self.assertEqual(len(self.roots()), 7)

    def test_pvp_root_is_a_constant(self):
        root = self.roots()['PVP_Manager.get_pathRoot']
        self.assertEqual([row['value'] for row in root['literals']], ['data-leagues'])
        self.assertEqual(root['calls'], {})

    def test_arena_root_has_three_branches_with_conditions(self):
        root = self.roots()['ArenaManager.get_pathRoot']
        self.assertEqual([row['literal'] for row in root['branches']],
                         ['arena-test-datas', 'arena---datas', 'arena--datas'])
        self.assertIn('get_companyName', root['branches'][0]['condition'])
        self.assertIn('PREMIUM', root['branches'][2]['condition'])
        self.assertEqual(root['calls'].get('VersionControlSystem.get_PREMIUM'), 1)

    def test_five_path_getters_concat_the_root(self):
        getters = {name: row for name, row in self.roots().items()
                   if 'get_pathOf' in name}
        self.assertEqual(len(getters), 5)
        for name, row in getters.items():
            self.assertEqual(row['calls'].get('String.Concat'), 1, name)
        self.assertEqual(
            sorted(row['value'] for row in
                   getters['PVP_Manager.get_pathOfDataPlayOfMachines']['literals']),
            ['/data-play/data-play-machines', 'data-leagues'])


class PathLiterals(unittest.TestCase):
    def test_counts(self):
        census = payload()['census']
        self.assertEqual(census['methods'], 34)
        self.assertEqual(census['path_literals'], 27)
        self.assertEqual(census['templates'], 19)
        self.assertEqual(census['distinct_literals'], 179)

    def test_named_paths(self):
        values = {row['value']: row for row in payload()['path_literals']}
        for value in ('/is-open', 'Data-Users/', 'BackupDatas/', 'ban-accounts/',
                      '/user-datas/userList/', '{0}/data-solos/{1}',
                      '{0}/rank-{1}/map-{2}'):
            self.assertIn(value, values)
        root_values = {item['value'] for row in payload()['roots']
                       for item in row['literals']}
        for value in ('/data-users', '/data-ranks', '/data-configs',
                      '/data-play/data-play-users', '/data-play/data-play-machines'):
            self.assertIn(value, root_values)

    def test_every_path_literal_has_a_decimal_cell(self):
        for row in payload()['path_literals']:
            self.assertTrue(row['cells'], row['value'])
            for cell in row['cells']:
                self.assertIsInstance(cell, int)
                self.assertGreater(cell, 0x2AD0000)
                self.assertLess(cell, 0x2AF0000)

    def test_is_open_cell_is_the_one_138_named(self):
        row = next(item for item in payload()['path_literals']
                   if item['value'] == '/is-open')
        self.assertEqual(row['cells'], [IS_OPEN_CELL])


class Templates(unittest.TestCase):
    def test_all_contiguous_and_formatted(self):
        rows = payload()['templates']
        self.assertEqual(len(rows), 19)
        for row in rows:
            self.assertTrue(row['contiguous'], row['value'])
            self.assertTrue(any(user['format_calls'] for user in row['users']), row['value'])

    def test_set_summary_datas_template(self):
        row = next(item for item in payload()['templates']
                   if item['value'].startswith('{0}/summary-datas/season-{1}/rank-{2}'
                                               '/rooms/roomList/room-{3}'))
        self.assertEqual(row['placeholders'], [0, 1, 2, 3])
        self.assertEqual([user['rva'] for user in row['users']], [22687092])

    def test_arena_cleaner_templates_use_a_shorter_overload(self):
        row = next(item for item in payload()['templates']
                   if item['value'] == '/arena---datas/rank-configs/rank-{0}/seasonCount')
        self.assertEqual([user['rva'] for user in row['users']], [22673864])

    def test_path_templates_are_sixteen_of_nineteen(self):
        census = payload()['census']
        self.assertEqual(census['path_templates'], 16)
        self.assertEqual(sorted(census['message_templates']),
                         ['Delete rank-{0:000} season-{1}', 'PVP_Machine_{0}_{1}_{2}',
                          'user#{0}{1}{2}'])
        kinds = {row['value']: row['kind'] for row in payload()['templates']}
        self.assertEqual(kinds['{0}/data-solos/{1}'], 'path')
        self.assertEqual(kinds['PVP_Machine_{0}_{1}_{2}'], 'message')

    def test_every_template_has_a_using_method(self):
        for row in payload()['templates']:
            self.assertTrue(row['users'], row['value'])
            for user in row['users']:
                self.assertTrue(user['class_name'])


class MachineNames(unittest.TestCase):
    def test_the_pool_is_108_names_in_the_id_fabricating_method(self):
        pools = payload()['machine_names']
        self.assertEqual(len(pools), 1)
        pool = pools[0]
        self.assertEqual(pool['count'], 108)
        self.assertEqual(pool['class_name'], 'Board_PVP.<IEUploadMachineDatas>d__88')
        self.assertEqual(pool['rva'], 19831376)

    def test_the_pool_is_localised(self):
        names = payload()['machine_names'][0]['names']
        self.assertIn('Máy sấy', names)
        self.assertIn('John Lùy', names)


class AuditCorroboration(unittest.TestCase):
    def test_item_53_is_corroborated_but_still_runtime(self):
        block = payload()['audit_corroboration']
        self.assertEqual(block['item'], 53)
        self.assertIn('corroborated statically', block['verdict'])
        self.assertIn('RUNTIME', block['verdict'])
        self.assertEqual(block['here']['is_open_cell'], IS_OPEN_CELL)


class NotDecoded(unittest.TestCase):
    def test_three_items(self):
        rows = payload()['not_decoded']
        self.assertEqual(len(rows), 3)
        self.assertIn('MODEL_NOT_MEASURED runtime', rows[0]['blocking'])
        for row in rows:
            self.assertTrue(row['blocking'])


if __name__ == '__main__':
    unittest.main()
