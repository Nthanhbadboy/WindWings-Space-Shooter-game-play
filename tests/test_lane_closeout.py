"""Contracts for report 147: the lane #29/#30 close-out gate (reports 127-146)."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import lane_closeout  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_lane_closeout.json.gz'
PIN_SHA = '3b815fc91d8f21f2191aa4dd558aabac82f67d09adb0f24e3ce54da27a8ecadd'
PIN_BYTES = 10669


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces(self):
        rebuilt = json.loads(json.dumps(lane_closeout.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_forty_sources(self):
        sources = payload()['provenance']['sources']
        self.assertEqual(len(sources), 40)
        roles = [row['role'] for row in sources]
        self.assertEqual(roles.count('lane artifact'), 20)
        self.assertEqual(roles.count('report that cites the artifact above'), 20)

    def test_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])


class Mapping(unittest.TestCase):
    def test_one_artifact_per_report(self):
        rows = payload()['mapping']
        self.assertEqual(len(rows), 20)
        self.assertEqual(sorted(row['report'] for row in rows), list(range(127, 147)))
        self.assertEqual(len({row['artifact'] for row in rows}), 20)

    def test_a_few_known_pairs(self):
        pairs = {row['report']: row['artifact'] for row in payload()['mapping']}
        self.assertEqual(pairs[143], 'l2_535b0541_economy_keys.json.gz')
        self.assertEqual(pairs[144], 'l2_535b0541_game_store_keys.json.gz')
        self.assertEqual(pairs[146], 'l2_535b0541_computed_key_index.json.gz')

    def test_cross_mentions_are_recorded(self):
        rows = {row['report']: row for row in payload()['mapping']}
        self.assertIn('135', rows[128]['mentioned_in'])


class Checks(unittest.TestCase):
    def test_twenty_one_checks_all_pass(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 21)
        self.assertTrue(all(row['pass_'] for row in checks))

    def test_the_checks_that_carry_the_story(self):
        ids = {row['id'] for row in payload()['checks']}
        for ident in ('store-calls', 'resolution-adds-up', 'keys-25-to-28',
                      'old-keys-unchanged', 'computed-records', 'computed-families',
                      'bands', 'sentinel', 'economy-reproducible', 'economy-delta',
                      'key-spaces-disjoint', 'one-slot-per-class', 'rank-tiers',
                      'pvp-rule-pairs', 'provenance-digests'):
            self.assertIn(ident, ids)

    def test_store_numbers(self):
        checks = {row['id']: row for row in payload()['checks']}
        self.assertEqual(checks['store-calls']['actual'], [184, 184])
        self.assertEqual(checks['resolution-adds-up']['actual'],
                         {'literal': 18, 'computed': 8})
        self.assertEqual(checks['keys-25-to-28']['actual'], [25, 28, 3])
        self.assertEqual(checks['computed-records']['actual'], [51, 51])

    def test_disjoint_key_spaces(self):
        checks = {row['id']: row for row in payload()['checks']}
        self.assertEqual(checks['key-spaces-disjoint']['actual'], [0, 21, 25])


class Corrections(unittest.TestCase):
    def test_the_143_delta_is_explained(self):
        rows = payload()['corrections']
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row['target'], 145)
        self.assertIn('6 in meta-rewards', row['correction'])
        self.assertEqual(row['evidence']['inside'], 174)
        self.assertEqual(row['evidence']['outside'], 10)
        self.assertEqual(row['evidence']['outside_by_raw'],
                         {'key-jump-535b0541': 4, 'meta-rewards-535b0541': 6})


class Inventory(unittest.TestCase):
    def test_twenty_artifacts(self):
        rows = payload()['inventory']
        self.assertEqual(len(rows), 20)
        self.assertEqual(sorted(row['report'] for row in rows), list(range(127, 147)))
        self.assertTrue(all(row['sha256'] for row in rows))
        self.assertTrue(all(row['bytes'] > 0 for row in rows))

    def test_sizes_reach_disk(self):
        for row in payload()['inventory']:
            path = ROOT / 'datas' / row['artifact']
            self.assertEqual(path.stat().st_size, row['bytes'], row['artifact'])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                             row['sha256'], row['artifact'])

    def test_almost_every_artifact_has_an_open_list(self):
        rows = payload()['inventory']
        # 128 keeps its open items under `gaps` instead of `not_decoded`
        empty = [row['report'] for row in rows if row['open_items'] == 0]
        self.assertEqual(empty, [128])


class OpenItems(unittest.TestCase):
    def test_counts(self):
        blob = payload()
        self.assertEqual(blob['totals'], {'reports': 20, 'checks': 21,
                                          'open_items': 56, 'runtime_items': 17})
        self.assertEqual(len(blob['open_items']), 56)

    def test_runtime_items_are_labelled(self):
        runtime = [row for row in payload()['open_items']
                   if 'MODEL_NOT_MEASURED' in row['blocking']]
        self.assertEqual(len(runtime), 17)


if __name__ == '__main__':
    unittest.main()
