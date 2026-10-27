"""Contracts for report 131: key/reward arrays decoded from metadata defaults."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import box_arrays  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_box_arrays.json.gz'
PIN_SHA = 'b5be797d40daedc16676e4ef1a83ce5b976458d9e5d12e1a539d9ea42a469b4d'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


def by_name():
    return {row['field'].split('.')[1]: row for row in payload()['arrays']}


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        self.assertEqual(box_arrays.build(), payload())

    def test_static_only_evidence(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Arrays(unittest.TestCase):
    def test_four_arrays_in_static_order(self):
        rows = payload()['arrays']
        self.assertEqual([r['statics_offset'] for r in rows], [0x38, 0x40, 0x48, 0x50])
        self.assertEqual([r['field'] for r in rows],
                         ['Board_Quest.BoxKeyCost', 'Board_Quest.KeyPrices',
                          'Board_Quest.NumberRewards', 'Board_Quest.AllTimeAds'])
        self.assertEqual([r['declared'] for r in rows],
                         ['int[]', 'int[]', 'int[]', 'double[]'])

    def test_values(self):
        arrays = by_name()
        self.assertEqual(arrays['BoxKeyCost']['values'], [30, 30, 30])
        self.assertEqual(arrays['KeyPrices']['values'], [6, 20, 100])
        self.assertEqual(arrays['NumberRewards']['values'], [5, 6, 9])
        self.assertEqual(arrays['AllTimeAds']['values'], [18000.0, 259200.0, 691200.0])
        self.assertEqual(arrays['AllTimeAds']['element_type'], 'float64')

    def test_tokens_are_field_handles(self):
        ordinals = [r['token']['field_ordinal'] for r in payload()['arrays']]
        self.assertEqual(ordinals, [669, 654, 690, 241])
        self.assertTrue(all(r['token']['kind'] == 4 for r in payload()['arrays']))
        self.assertTrue(all(r['token']['source'] % 2 == 1 for r in payload()['arrays']))
        self.assertTrue(all(r['token']['pid_type_index'] == 2461
                            for r in payload()['arrays']))

    def test_blob_pointers(self):
        idx = [(r['blob']['field_data_index'], r['blob']['declared_bytes'])
               for r in payload()['arrays']]
        self.assertEqual(idx, [(29304, 12), (28800, 12), (30408, 12), (11936, 24)])

    def test_extractor_blobs_are_not_contents(self):
        for row in payload()['arrays']:
            self.assertIn('not array contents', row['not_the_extractor_blobs'])

    def test_all_structural_checks_pass(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 8)
        self.assertTrue(all(c['passed'] for c in checks), [c for c in checks if not c['passed']])


class Derived(unittest.TestCase):
    def test_economy(self):
        derived = payload()['derived']
        self.assertEqual(derived['keys_per_box'], {'0': 30, '1': 30, '2': 30})
        self.assertEqual(derived['gems_per_missing_key'], {'0': 6, '1': 20, '2': 100})
        self.assertEqual(derived['buy_all_missing_keys_gems'],
                         {'0': 180, '1': 600, '2': 3000})
        self.assertEqual(derived['draws_per_box'], {'0': 5, '1': 6, '2': 9})
        self.assertEqual(derived['ad_cooldown_hours'], {'0': 5.0, '1': 72.0, '2': 192.0})

    def test_domain_matches_report_130(self):
        domain = payload()['derived']['type_box_domain']
        frozen = json.loads(gzip.decompress(
            (ROOT / 'datas/l2_535b0541_box_draw.json.gz').read_bytes()))
        self.assertEqual(domain, frozen['type_box']['domain']['values'])


class Chain(unittest.TestCase):
    def test_chain_numbers(self):
        chain = payload()['chain']
        self.assertEqual(chain['initialize_array_rva'], 33927292)
        self.assertEqual(chain['board_quest_cctor_rva'], 19972028)
        self.assertEqual(chain['board_quest_cctor_size'], 5184)
        self.assertEqual((chain['pid_type_index'], chain['pid_field_count']), (2461, 740))

    def test_seconds_unit_is_sourced(self):
        seconds = payload()['chain']['seconds_source']
        self.assertEqual(seconds['rva'], 21105208)
        self.assertEqual(seconds['method'], 'MyLibrary.GetTotalSecondsTravelTime')
        self.assertEqual(seconds['used_by'], 'Board_QuestRewards.IsTimeAdsReady')

    def test_provenance(self):
        prov = payload()['provenance']
        self.assertEqual(prov['field_defaults_count'], 10493)
        self.assertIn('fieldDefaultValues', prov['field_defaults_source'])
        self.assertEqual(len(prov['sources']), 4)


if __name__ == '__main__':
    unittest.main()
