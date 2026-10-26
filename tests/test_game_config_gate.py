"""Contracts for report 141: `GameConfig` behind slot `0x2ADBB88` and the gate it drives."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import game_config_gate  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_game_config_gate.json.gz'
PIN_SHA = '241dfc87719d1730d4a31af9f2ffe288ff908b700d8f2c503eacd13b70456774'
SLOT = 44940168
STALE_SLOT = 44939488
FLOWS = {
    'Board_Arena.<IECheckArenaOpen>d__55': 22810128,
    'Board_Arena.<>c__DisplayClass55_0': 22806816,
    'Board_PVP.<IECheckPvPOpen>d__74': 19817328,
    'Board_PVP.<>c__DisplayClass74_0': 19803208,
    'ArenaHub.<>c__DisplayClass20_0': 22680000,
}
VERSION_RVAS = {22680092, 22807152, 19803544, 22811048, 19818236}


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(game_config_gate.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('not_decoded', blob['note'])


class Provenance(unittest.TestCase):
    def test_three_sources(self):
        self.assertEqual(len(payload()['provenance']['sources']), 3)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])

    def test_apk_digests_present(self):
        prov = payload()['provenance']
        for key in ('xapk_sha256', 'libil2cpp_sha256', 'dump_sha256'):
            self.assertEqual(len(prov[key]), 64, key)


class Slot(unittest.TestCase):
    def test_slot_decimal(self):
        self.assertEqual(payload()['slot']['decimal'], SLOT)
        self.assertEqual(payload()['slot']['va'], SLOT)

    def test_slot_is_not_the_stale_one(self):
        self.assertNotEqual(payload()['slot']['decimal'], STALE_SLOT)

    def test_twelve_byte_bias(self):
        # 0x2ADBB88 - 0x2ADB8E0 = 0x2A8; the two slots are simply different.
        self.assertEqual(SLOT - STALE_SLOT, 0x2A8)

    def test_stale_slot_scan_is_empty(self):
        blob = game_config_gate.load(game_config_gate.NATIVE)
        self.assertEqual(game_config_gate.slot_access(blob, STALE_SLOT), [])


class Identity(unittest.TestCase):
    def test_class_name(self):
        self.assertEqual(payload()['identity']['class_name'], 'GameConfig')

    def test_nine_fields(self):
        fields = payload()['identity']['fields']
        self.assertEqual([field['name'] for field in fields],
                         ['versionCode', 'isEmpty', 'backupAvailable',
                          'restoreAvailable', 'lastestVersionCode',
                          'allVersionsAreRequiredToUpdate',
                          'allVersionsAreRemindedToUpdate', 'hasGiftCode',
                          'GemCode'])

    def test_offsets(self):
        fields = payload()['identity']['fields']
        self.assertEqual([field['offset'] for field in fields],
                         [0x0, 0x4, 0x5, 0x6, 0x8, 0x10, 0x18, 0x20, 0x24])

    def test_types(self):
        fields = {field['name']: field['type']
                  for field in payload()['identity']['fields']}
        self.assertEqual(fields['versionCode'], 'int')
        self.assertEqual(fields['isEmpty'], 'bool')
        self.assertEqual(fields['lastestVersionCode'], 'int')

    def test_unique_layout_match(self):
        ident = payload()['identity']
        self.assertEqual(ident['matches'], 1)
        self.assertGreater(ident['candidates_with_statics'], 100)

    def test_observed_offsets(self):
        self.assertEqual(payload()['identity']['observed'],
                         {'0': 'int', '4': 'bool', '8': 'int'})


class Readers(unittest.TestCase):
    def test_five_flows(self):
        flows = payload()['readers']['flows']
        self.assertEqual(len(flows), 5)
        self.assertEqual({row['class_name']: row['rva'] for row in flows}, FLOWS)

    def test_no_writes_decoded(self):
        for row in payload()['readers']['flows']:
            kinds = {item['kind'] for item in row['accesses']}
            self.assertEqual(kinds, {'read'}, row['class_name'])

    def test_only_three_offsets(self):
        for row in payload()['readers']['flows']:
            self.assertTrue({item['offset'] for item in row['accesses']}
                            <= {0x0, 0x4, 0x8}, row['class_name'])

    def test_is_empty_byte_read(self):
        for row in payload()['readers']['flows']:
            if row['class_name'] == 'ArenaHub.<>c__DisplayClass20_0':
                continue
            self.assertIn('ldrb', [item['mnemonic'] for item in row['accesses']])

    def test_is_empty_readers_count(self):
        self.assertEqual(payload()['readers']['isEmpty_readers'], 4)

    def test_empty_read_sites(self):
        sites = {row['class_name']: [item['rva'] for item in row['accesses']
                                     if item['offset'] == 0x4]
                 for row in payload()['readers']['flows']}
        self.assertEqual(sites['Board_Arena.<IECheckArenaOpen>d__55'], [22810736])
        self.assertEqual(sites['Board_PVP.<IECheckPvPOpen>d__74'], [19817916])
        self.assertEqual(sites['ArenaHub.<>c__DisplayClass20_0'], [])


class Version(unittest.TestCase):
    def test_five_sites(self):
        sites = payload()['version']['sites']
        self.assertEqual(len(sites), 5)
        self.assertEqual({site['latest_read_rva'] for site in sites}, VERSION_RVAS)

    def test_rule(self):
        self.assertEqual(payload()['version']['rule'],
                         'update_required = lastestVersionCode > versionCode')

    def test_branches_off_the_update_path(self):
        for site in payload()['version']['sites']:
            if site['method'] == 'ArenaHub.<>c__DisplayClass20_0':
                self.assertEqual(site['branch'], 'cset')
                self.assertEqual(site['branch_operands'], 'w1, le')
            else:
                self.assertEqual(site['branch'], 'b.le')

    def test_reads_eight_then_zero(self):
        for site in payload()['version']['sites']:
            self.assertEqual(site['version_read_rva'] - site['latest_read_rva'], 4)

    def test_update_path_names_the_user_check(self):
        sites = {site['method']: site for site in payload()['version']['sites']}
        arena = [call['signature'] for call
                 in sites['Board_Arena.<IECheckArenaOpen>d__55']['branch_target_calls']]
        pvp = [call['signature'] for call
               in sites['Board_PVP.<IECheckPvPOpen>d__74']['branch_target_calls']]
        self.assertTrue(any('CheckArenaUser' in name for name in arena), arena)
        self.assertTrue(any('CheckPvPUserRequestAccess' in name for name in pvp), pvp)


class Gate(unittest.TestCase):
    def test_four_empty_checks(self):
        checks = payload()['gate']['empty_checks']
        self.assertEqual(len(checks), 4)

    def test_all_cbz_and_same_polarity(self):
        for check in payload()['gate']['empty_checks']:
            self.assertEqual(check['branch'], 'cbz')
            self.assertEqual(check['taken_when'], 'isEmpty is false')

    def test_not_empty_leads_to_the_version_check(self):
        checks = {check['method']: check for check in payload()['gate']['empty_checks']}
        for meth in ('Board_Arena.<IECheckArenaOpen>d__55',
                     'Board_PVP.<IECheckPvPOpen>d__74'):
            self.assertLess(checks[meth]['branch_target'], 2 ** 31)

    def test_empty_leads_to_a_config_refetch(self):
        checks = {check['method']: check for check in payload()['gate']['empty_checks']}
        for meth in ('Board_Arena.<IECheckArenaOpen>d__55',
                     'Board_PVP.<IECheckPvPOpen>d__74'):
            names = [call['signature'] for call in checks[meth]['fall_through_calls']]
            self.assertTrue(any('GetGameConfig' in name for name in names), names)

    def test_flag_name_and_offset(self):
        self.assertEqual(payload()['gate']['empty_flag'], 'isEmpty')
        self.assertEqual(payload()['gate']['empty_offset'], 0x4)


class Writers(unittest.TestCase):
    def test_three_writer_candidates(self):
        entries = payload()['writers']['entries']
        self.assertEqual([entry['name'] for entry in entries],
                         ['.cctor', 'SetupDatas', 'ReplaceDatas'])

    def test_rvas(self):
        entries = payload()['writers']['entries']
        self.assertEqual([entry['rva'] for entry in entries],
                         [19082168, 19042256, 19049040])

    def test_none_pinned(self):
        self.assertEqual(payload()['writers']['pinned'], 0)
        for entry in payload()['writers']['entries']:
            self.assertFalse(entry['pinned'], entry['name'])


class Corrections(unittest.TestCase):
    def test_slot_correction_recorded(self):
        rows = payload()['corrections']
        self.assertEqual(len(rows), 1)
        self.assertIn('0x2ADB8E0', rows[0]['item'])
        self.assertEqual(rows[0]['measured']['decimal'], SLOT)
        self.assertEqual(rows[0]['measured']['slot_ref_rvas'],
                         [22810712, 22810728, 22811040])

    def test_confirmation_present(self):
        rows = payload()['confirmations']
        self.assertEqual(len(rows), 1)
        self.assertIn('GameConfig', rows[0]['result'])


class NotDecoded(unittest.TestCase):
    def test_two_items(self):
        self.assertEqual(len(payload()['not_decoded']), 2)

    def test_values_are_runtime_only(self):
        values = payload()['not_decoded'][0]
        self.assertIn('MODEL_NOT_MEASURED runtime', values['blocking'])
        for rva in ('19082168', '19042256', '19049040'):
            self.assertIn(rva, values['blocking'])


if __name__ == '__main__':
    unittest.main()
