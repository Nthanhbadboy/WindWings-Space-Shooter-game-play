"""Contracts for report 178: the key counters are statics, and `+0xb8` is `static_fields`.

176 answered item 32 with six writers and a premise — *"instance fields on the object behind
slot 0x2adb000+0xaf8, then +0xb8; `KeyCount0/1/2` are properties, not statics"*. The six
sites hold; the premise is inverted. `dump.cs` declares `keyCount0/1/2` as `private static`
at 0x50/0x54/0x58 of `GameDatas`, and the accessors are the canonical cctor-gated IL2CPP
static sequence, with `+0xb8` = `Il2CppClass::static_fields`.

These tests pin the census (102 stores, 16 through a static block, 6 of them GameDatas'),
the chain down to the TypeInfo cell, and the item-32 answer.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import counter_static_writers as CSW  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_counter_static_writers.json.gz'
PIN_BYTES = 2142
PIN_SHA = '11c6cf4b2b5c3a26d26086efc326652eb3d7539b6ac0667a181ce42791fcd718'

COUNTER_RVAS = {20070896: 0x50, 20071048: 0x50,
                20071224: 0x54, 20071376: 0x54,
                20071552: 0x58, 20071704: 0x58}


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        _, packed = CSW.build(None)
        self.assertEqual(packed, ARTIFACT.read_bytes())

    def test_every_check_passes(self):
        self.assertEqual([row['name'] for row in payload()['checks']
                          if not row['passed']], [])


class Chain(unittest.TestCase):
    def test_the_typeinfo_cell_is_the_one_176_named(self):
        self.assertEqual(payload()['chain']['typeinfo_cell'], ['0x2adb000', '0xaf8'])

    def test_the_second_hop_is_static_fields_not_an_object(self):
        self.assertEqual(payload()['chain']['static_hop'], '0xb8')
        self.assertEqual(payload()['chain']['cctor_gate'], '0xe0')

    def test_dump_cs_declares_three_private_statics(self):
        declared = payload()['declared']
        self.assertEqual({name: value['offset'] for name, value in declared.items()},
                         {'keyCount0': 0x50, 'keyCount1': 0x54, 'keyCount2': 0x58})
        self.assertTrue(all(value['static'] for value in declared.values()))

    def test_every_counter_write_reads_static_fields_first(self):
        for row in payload()['counters']:
            self.assertIn('#0xb8', row['static_from'], row['rva'])

    def test_every_counter_write_is_cctor_gated_and_initialised(self):
        for row in payload()['counters']:
            self.assertTrue(row['cctor']['gate'], row['rva'])
            self.assertTrue(row['cctor']['init'], row['rva'])

    def test_counter_offsets_are_word_sized_and_four_apart(self):
        offsets = sorted(row['offset'] for row in payload()['counters'])
        self.assertEqual(offsets, [0x50, 0x50, 0x54, 0x54, 0x58, 0x58])
        self.assertTrue(all(row['mnemonic'] == 'str' for row in payload()['counters']))


class Census(unittest.TestCase):
    def test_the_corpus_is_the_pinned_one(self):
        corpus = payload()['corpus']
        self.assertEqual((corpus['methods'], corpus['instructions']), (1788, 159059))

    def test_one_hundred_and_two_stores_at_the_three_offsets(self):
        self.assertEqual(payload()['census']['stores'], 102)

    def test_the_census_partitions(self):
        census = payload()['census']
        self.assertEqual(census['cell'] + census['static-block'] + census['instance']
                         + census['unknown'], census['stores'])

    def test_no_store_writes_a_metadata_cell(self):
        self.assertEqual(payload()['census']['cell'], 0)

    def test_sixteen_stores_go_through_a_static_block(self):
        self.assertEqual(payload()['census']['static-block'], 16)

    def test_ten_of_them_belong_to_other_classes(self):
        others = payload()['other_static_blocks']
        self.assertEqual(len(others), 10)
        self.assertNotIn('GameDatas', {row['klass'] for row in others})
        self.assertTrue(all(row['cell'] != ['0x2adb000', '0xaf8'] for row in others))

    def test_the_offsets_are_shared_by_other_classes(self):
        """0x50 in the corpus is not a rare offset — that is the whole trap."""
        by_offset = payload()['census']['by_offset']
        self.assertEqual(sorted(by_offset), ['0x50', '0x54', '0x58'])
        self.assertGreater(by_offset['0x50'], 6)
        self.assertGreater(payload()['census']['classes'], 1)


class Item32(unittest.TestCase):
    def test_the_six_sites_are_the_ones_176_pinned(self):
        self.assertEqual({row['rva']: row['offset']
                          for row in payload()['counters']}, COUNTER_RVAS)

    def test_the_fields_are_named(self):
        self.assertEqual([row['field'] for row in payload()['counters']],
                         ['keyCount0', 'keyCount0', 'keyCount1', 'keyCount1',
                          'keyCount2', 'keyCount2'])

    def test_the_answer_is_no_store_outside_the_three_accessors(self):
        self.assertEqual(payload()['item_32']['outside_stores'], [])
        self.assertEqual({row['accessor'] for row in payload()['counters']},
                         {'KeyCount0', 'KeyCount1', 'KeyCount2'})

    def test_the_premise_states_the_correction(self):
        premise = payload()['premise']
        self.assertIn('static_fields', premise['actual'])
        self.assertIn('not statics', premise['claimed_by_176'])
        self.assertIn('20070896', premise['unchanged'])

    def test_the_limits_are_written_down(self):
        limits = ' '.join(payload()['limits'])
        self.assertIn('MODEL_NOT_MEASURED runtime', limits)
        self.assertIn('unknown', limits)


if __name__ == '__main__':
    unittest.main()
