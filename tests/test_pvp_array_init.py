"""Contracts for report 177: what `Board_PVP..ctor` builds.

The audit carries items 30/39/40 as `POLICY` because the two `Board_PVP` blobs were
believed to arrive with served data. The constructor builds **seven** collections — six
24-byte arrays of length 6 straight out of `<PrivateImplementationDetails>`, plus a
`List<object>` at `+0x1b0` that the earlier field table did not list. The data therefore
ships inside the APK; what is missing is the cell -> blob binding.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import pvp_array_init as PAI  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_pvp_array_init.json.gz'
PIN_BYTES = 1965
PIN_SHA = '388f4fbfdb00d2b9c0b3d9930e27c7a5564b6c51d87976203896b1e5df871ced'

STORES = [0x198, 0x1a0, 0x1a8, 0x1b0, 0x208, 0x210, 0x218]


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        _, packed = PAI.build(None)
        self.assertEqual(packed, ARTIFACT.read_bytes())

    def test_static_only(self):
        self.assertEqual(payload()['evidence'], 'STATIC_ONLY_ORIGINAL_APK')

    def test_every_check_passed(self):
        rows = payload()['checks']
        self.assertEqual(len(rows), 12)
        self.assertEqual([row['name'] for row in rows if not row['passed']], [])


class Constructor(unittest.TestCase):
    def test_the_ctor(self):
        ctor = payload()['constructor']
        self.assertEqual((ctor['klass'], ctor['rva'], ctor['size'], ctor['instructions']),
                         ('Board_PVP', 19796420, 500, 125))

    def test_it_chains_to_the_board_ctor(self):
        self.assertEqual(payload()['constructor']['chained_to'], 19131072)


class Collections(unittest.TestCase):
    def test_seven_stores_in_address_order(self):
        self.assertEqual([row['offset'] for row in payload()['collections']], STORES)

    def test_six_arrays_one_list(self):
        rows = payload()['collections']
        self.assertEqual(len([r for r in rows if r['kind'] == 'array']), 6)
        self.assertEqual(len([r for r in rows if r['kind'] == 'list']), 1)

    def test_every_array_has_length_six(self):
        arrays = [r for r in payload()['collections'] if r['kind'] == 'array']
        self.assertEqual({row['length'] for row in arrays}, {6})

    def test_they_come_from_InitializeArray(self):
        arrays = [r for r in payload()['collections'] if r['kind'] == 'array']
        for row in arrays:
            self.assertEqual(row['init_target'], 33927292)
            self.assertIsNotNone(row['init_rva'])

    def test_the_blob_cells(self):
        arrays = [r for r in payload()['collections'] if r['kind'] == 'array']
        self.assertEqual([row['cell']['offset'] for row in arrays],
                         [0x8, 0x10, 0x18, 0x30, 0x38, 0x40])
        self.assertEqual({row['cell']['page'] for row in arrays}, {0x2ae0000})

    def test_the_third_array_is_the_float_one(self):
        arrays = [r for r in payload()['collections'] if r['kind'] == 'array']
        self.assertEqual(arrays[2]['klass_cell']['offset'], 0x350)
        self.assertEqual({row['klass_cell']['offset'] for row in arrays},
                         {0x318, 0x350})

    def test_the_seventh_is_a_list_of_object(self):
        row = [r for r in payload()['collections'] if r['kind'] == 'list'][0]
        self.assertEqual(row['offset'], 0x1b0)
        self.assertEqual(row['list_ctor_target'], 29193868)
        self.assertIsNone(row['length'])

    def test_the_field_table_gains_one_row(self):
        table = {row['offset']: row['field'] for row in payload()['field_table']}
        self.assertEqual(table[0x1b0], '(unnamed List<object>)')
        self.assertEqual(table[0x198], 'rewardIndexs')
        self.assertEqual(table[0x218], 'allBetMedalValues')


class Readers(unittest.TestCase):
    def test_the_seventh_collection_is_read_where_expected(self):
        rvas = {row['rva'] for row in payload()['readers_of_1b0']}
        self.assertIn(19800320, rvas)
        self.assertIn(19811460, rvas)
        self.assertTrue(all(row['klass'].startswith('Board_PVP')
                            for row in payload()['readers_of_1b0']))


class Negatives(unittest.TestCase):
    def test_the_usage_table_is_absent(self):
        neg = payload()['negatives']
        self.assertFalse(neg['ia_has_board_pvp'])
        self.assertEqual(neg['ia_buckets'], 17)

    def test_the_blob_corpus_is_counted(self):
        neg = payload()['negatives']
        self.assertEqual(neg['pid_blobs'], 982)
        self.assertEqual(neg['defaults_count'], 10493)
        self.assertGreater(neg['pid_blobs_24_bytes'], 0)

    def test_limits_keep_the_values_unbound(self):
        text = ' '.join(payload()['limits'])
        self.assertIn('metadata usage table', text)
        self.assertIn('NOT_BOUND', text)
        self.assertIn('MODEL_NOT_MEASURED', text)

    def test_provenance_hashes_match(self):
        for row in payload()['provenance']['inputs']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])


if __name__ == '__main__':
    unittest.main()
