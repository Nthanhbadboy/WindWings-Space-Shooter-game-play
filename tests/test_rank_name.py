"""Contracts for report 137: `PVP_Manager.GetRankName` display string, end to end."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import rank_name  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_rank_name.json.gz'
PIN_SHA = '1596564d798a9f4ad93bfd582abd92d2dfa559b06362f28dd56cc1d0ae4636b1'
TIERS = ['Herald', 'Guardian', 'Crusader', 'Archon', 'Legend', 'Ancient', 'Divine',
         'Immortal', 'Eternal', 'God']


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(rank_name.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_four_sources(self):
        self.assertEqual(len(payload()['provenance']['sources']), 4)

    def test_source_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])


class Method(unittest.TestCase):
    def test_pinned_body(self):
        method = payload()['method']
        self.assertEqual(method['rva'], 19881572)
        self.assertEqual(method['size'], 264)
        self.assertEqual(len(method['sha256']), 64)

    def test_expression_is_measured(self):
        self.assertEqual(
            payload()['method']['expression'],
            'Concat(GetText(Concat(LIT("txt_pvp_rank_"), ToString(rank))), '
            'LIT(" "), GetRankNumber(rank, level))')

    def test_five_calls_in_order(self):
        calls = payload()['calls']
        self.assertEqual([row['call'] for row in calls],
                         ['ToString', 'Concat', 'GetText', 'GetRankNumber', 'Concat'])
        self.assertEqual([row['rva'] for row in calls],
                         [19881692, 19881712, 19881756, 19881796, 19881816])

    def test_every_call_has_a_dump_signature(self):
        for row in payload()['calls']:
            self.assertTrue(row['signature'], row['call'])
            self.assertIn(row['call'], row['signature'])

    def test_get_text_is_language_manager(self):
        get_text = [row for row in payload()['calls'] if row['call'] == 'GetText'][0]
        self.assertEqual(get_text['target_rva'], 21202600)
        self.assertEqual(get_text['signature'], 'public static string GetText(string key) { }')


class Literals(unittest.TestCase):
    def test_two_string_slots(self):
        rows = payload()['literals']
        self.assertEqual([row['value'] for row in rows], ['txt_pvp_rank_', ' '])

    def test_both_are_kind_five(self):
        for row in payload()['literals']:
            self.assertEqual(row['token_kind'], 5)

    def test_addresses_and_sources(self):
        rows = payload()['literals']
        self.assertEqual([row['literal_address'] for row in rows], [46080000, 45968752])
        self.assertEqual([row['token_source'] for row in rows], [28027, 209])

    def test_instruction_rvas(self):
        rows = payload()['literals']
        self.assertEqual([row['instruction_rva'] for row in rows], [19881696, 19881800])


class Tiers(unittest.TestCase):
    def test_ten_tiers_in_order(self):
        self.assertEqual([row['tier'] for row in payload()['tiers']], TIERS)

    def test_keys_are_prefixed_by_rank(self):
        for row in payload()['tiers']:
            self.assertEqual(row['key'], 'txt_pvp_rank_%d' % row['rank'])

    def test_label_is_localized_separately(self):
        labels = payload()['labels']
        self.assertEqual(labels['distinct'], 15)
        self.assertIn('Hạng', labels['values'])


class Languages(unittest.TestCase):
    def test_nineteen_language_assets(self):
        self.assertEqual(payload()['languages']['count'], 19)

    def test_every_language_has_all_ten_keys(self):
        for row in payload()['languages']['files']:
            self.assertEqual(sorted(row['rank_keys']), ['txt_pvp_rank_%d' % index
                                                        for index in range(10)])
            self.assertEqual([row['rank_keys']['txt_pvp_rank_%d' % index]
                              for index in range(10)], TIERS)
            self.assertEqual(list(row['other_keys']), ['txt_pvp_rank_rewards'])

    def test_language_files_match_workspace_digests(self):
        for row in payload()['languages']['files']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])


class Display(unittest.TestCase):
    def test_forty_four_rows(self):
        self.assertEqual(payload()['display']['rows'], 44)

    def test_text_is_tier_space_number(self):
        for row in payload()['display']['all_rows']:
            self.assertEqual(row['tier'], TIERS[row['rank']])
            self.assertEqual(row['rank_number'], row['cells'] - row['level'])
            self.assertEqual(row['text'], '%s %d' % (row['tier'], row['rank_number']))

    def test_cells_match_135(self):
        self.assertEqual(payload()['cross_checks']['cells'],
                         [3, 3, 4, 4, 5, 5, 5, 5, 5, 5])

    def test_first_and_last_rows(self):
        rows = payload()['display']['all_rows']
        self.assertEqual((rows[0]['text'], rows[-1]['text']), ('Herald 3', 'God 1'))


class Open(unittest.TestCase):
    def test_confirmation_names_136(self):
        rows = payload()['confirmations']
        self.assertTrue(any('136' in row['item'] for row in rows))

    def test_get_text_fallback_is_runtime(self):
        rows = payload()['not_decoded']
        self.assertEqual(len(rows), 1)
        self.assertIn('MODEL_NOT_MEASURED runtime', rows[0]['blocking'])
        self.assertIn('21202600', rows[0]['blocking'])


if __name__ == '__main__':
    unittest.main()
