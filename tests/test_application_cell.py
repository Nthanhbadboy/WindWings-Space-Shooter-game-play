"""Contracts for report 142: slot `0x2ADB8E0` is the `UnityEngine.Application` klass cell."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import application_cell  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_application_cell.json.gz'
PIN_SHA = 'd618b7401b81dc3119cc11d43687aec3e33707ddabbe56664c993c4bd5518f07'
CELL = 44939488
GATE_CELL = 44940168


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(application_cell.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_sources_cover_dump_strings_and_eight_raws(self):
        rows = payload()['provenance']['sources']
        self.assertEqual(len(rows), 10)
        paths = [row['path'] for row in rows]
        self.assertIn('reverse-engineering/il2cpp/dump.cs.gz', paths)
        self.assertIn('reverse-engineering/il2cpp/stringliteral.json', paths)
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

    def test_page_and_offset(self):
        cell = payload()['cell']
        self.assertEqual(cell['page'], 0x2ADB000)
        self.assertEqual(cell['offset'], 0x8E0)

    def test_class_name(self):
        self.assertEqual(payload()['cell']['klass'], 'UnityEngine.Application')

    def test_gate_slot_from_141(self):
        gate = payload()['cell']['gate_slot_from_141']
        self.assertEqual(gate['decimal'], GATE_CELL)
        self.assertEqual(gate['klass'], 'GameConfig')

    def test_delta_between_the_two_cells(self):
        self.assertEqual(payload()['cell']['delta'], -0x2A8)
        self.assertEqual(CELL - GATE_CELL, -0x2A8)


class Census(unittest.TestCase):
    def test_method_count(self):
        self.assertEqual(payload()['census']['methods'], 47)

    def test_distinct_methods(self):
        self.assertEqual(payload()['census']['distinct_methods'], 33)

    def test_site_count(self):
        self.assertEqual(payload()['census']['sites'], 92)

    def test_per_raw(self):
        self.assertEqual(payload()['census']['per_raw'],
                         {'arena-pvp-535b0541': 23, 'key-grant-535b0541': 11,
                          'meta-rewards-535b0541': 12, 'pack-index-535b0541': 1})

    def test_rows_match_count(self):
        self.assertEqual(len(payload()['census']['rows']), 47)

    def test_every_row_calls_an_application_api(self):
        for row in payload()['census']['rows']:
            self.assertTrue(row['apis'], row['signature'])

    def test_every_row_has_class_init(self):
        for row in payload()['census']['rows']:
            self.assertIn('class_init(0x110D028)', row['idiom'], row['signature'])


class Apis(unittest.TestCase):
    def test_census(self):
        self.assertEqual(payload()['api_census'],
                         {'Application.get_internetReachability': 29,
                          'Application.get_companyName': 10,
                          'Application.OpenURL': 6,
                          'Application.get_systemLanguage': 2})

    def test_only_four_apis(self):
        self.assertEqual(len(payload()['api_census']), 4)

    def test_open_url_callers_are_the_popup_handlers(self):
        callers = {row['signature'] for row in payload()['census']['rows']
                   if 'Application.OpenURL' in row['apis']}
        self.assertTrue(any('IECheckArenaOpen' in name for name in callers), callers)
        self.assertTrue(any('IECheckPvPOpen' in name for name in callers), callers)


class Idiom(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(payload()['idiom']['kinds'],
                         {'class_init(0x110D028)': 47,
                          'initialized_flag(klass+0xE0)': 38,
                          'unclassified': 2})

    def test_note_mentions_the_initialized_byte(self):
        self.assertIn('0xE0', payload()['idiom']['note'])


class GiftLanguages(unittest.TestCase):
    def test_method(self):
        gift = payload()['gift_languages']
        self.assertEqual(gift['rva'], 20071724)
        self.assertEqual(gift['signature'], 'public static bool IsHasGiftLanguages() { }')

    def test_set(self):
        self.assertEqual(payload()['gift_languages']['languages'],
                         [8, 10, 14, 15, 22, 23, 26])

    def test_names(self):
        self.assertEqual(payload()['gift_languages']['names'],
                         ['Danish', 'English', 'French', 'German', 'Japanese',
                          'Korean', 'Norwegian'])

    def test_vietnamese_is_excluded(self):
        excluded = payload()['gift_languages']['excluded_example']
        self.assertEqual(excluded['value'], 39)
        self.assertEqual(excluded['name'], 'Vietnamese')
        self.assertNotIn(39, payload()['gift_languages']['languages'])

    def test_check_rvas(self):
        self.assertEqual([check['rva'] for check in
                          payload()['gift_languages']['checks']],
                         [20071796, 20071828, 20071860, 20071892, 20071924,
                          20071956, 20072004])


class Currency(unittest.TestCase):
    def rows(self):
        return {row['name']: row for row in payload()['currency']['rows']}

    def test_four_getters(self):
        self.assertEqual(list(self.rows()),
                         ['GameDatas.get_Gems', 'GameDatas.get_Coins',
                          'GameDatas.get_WingCoins', 'GameDatas.get_StarCount'])

    def test_rvas(self):
        self.assertEqual({row['rva'] for row in self.rows().values()},
                         {20069516, 20068904, 20075932, 20070312})

    def test_defaults(self):
        rows = self.rows()
        self.assertEqual(rows['GameDatas.get_Coins']['defaults'], [68999])
        self.assertEqual(rows['GameDatas.get_Gems']['defaults'], [500])
        self.assertEqual(rows['GameDatas.get_StarCount']['defaults'], [0])
        self.assertEqual(rows['GameDatas.get_WingCoins']['defaults'], [0, 999999])

    def test_coins_is_not_7559(self):
        # `mov w1,#0xd87` + `movk w1,#1,lsl#16` = 0x10D87, not 0x1D87.
        self.assertIn(68999, self.rows()['GameDatas.get_Coins']['defaults'])
        self.assertNotIn(7559, self.rows()['GameDatas.get_Coins']['defaults'])

    def test_cheat_offsets(self):
        rows = self.rows()
        self.assertEqual(rows['GameDatas.get_Coins']['cheat_offset'], 0x14)
        self.assertEqual(rows['GameDatas.get_Gems']['cheat_offset'], 0x18)
        self.assertEqual(rows['GameDatas.get_StarCount']['cheat_offset'], 0x1C)
        self.assertIsNone(rows['GameDatas.get_WingCoins']['cheat_offset'])

    def test_cache_offsets(self):
        rows = self.rows()
        self.assertEqual(rows['GameDatas.get_Coins']['cache_offset'], 0x44)
        self.assertEqual(rows['GameDatas.get_Gems']['cache_offset'], 0x48)
        self.assertEqual(rows['GameDatas.get_StarCount']['cache_offset'], 0x4C)
        self.assertEqual(rows['GameDatas.get_WingCoins']['cache_offset'], 0x5C)

    def test_sentinel_and_key_cells(self):
        rows = self.rows()
        for row in rows.values():
            self.assertEqual(row['sentinel'], -1)
        self.assertEqual(rows['GameDatas.get_Coins']['call_sites'][0]['key_cell'], 44941536)
        self.assertEqual(rows['GameDatas.get_Gems']['call_sites'][0]['key_cell'], 44941496)
        self.assertEqual(rows['GameDatas.get_StarCount']['call_sites'][0]['key_cell'], 44941512)
        self.assertEqual(rows['GameDatas.get_WingCoins']['call_sites'][0]['key_cell'], 44941776)

    def test_get_int_rva(self):
        self.assertEqual(payload()['currency']['get_int_rva'], 41405600)


class Coverage(unittest.TestCase):
    def test_counts(self):
        cover = payload()['coverage']
        self.assertEqual(cover['scanned'], 47)
        self.assertEqual(cover['indexed'], 45)

    def test_missing_are_check_internet(self):
        missing = payload()['coverage']['missing_from_slot_refs']
        self.assertEqual(len(missing), 2)
        for row in missing:
            self.assertEqual(row['class_name'], 'Board_PVP')
            self.assertEqual(row['signature'], 'private void CheckInternet() { }')
            self.assertEqual(row['rva'], 19787760)

    def test_note_warns_index_is_not_proof(self):
        self.assertIn('not a proof of absence', payload()['coverage']['note'])


class NotDecoded(unittest.TestCase):
    def test_two_items(self):
        self.assertEqual(len(payload()['not_decoded']), 2)

    def test_first_is_runtime(self):
        self.assertIn('MODEL_NOT_MEASURED runtime',
                      payload()['not_decoded'][0]['blocking'])

    def test_second_lists_the_key_slots(self):
        blocking = payload()['not_decoded'][1]['blocking']
        for cell in ('0x2ADC0B8', '0x2ADC0C8', '0x2ADC0E0', '0x2ADC1D0'):
            self.assertIn(cell, blocking)


if __name__ == '__main__':
    unittest.main()
