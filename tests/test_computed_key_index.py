"""Contracts for report 146: the index half of the computed store keys."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import computed_key_index  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_computed_key_index.json.gz'
PIN_SHA = 'd9ff7301848e8bb1a4ac23105973c0c13e18a99c111fe6ba79e9f6fdee4f43c6'
PIN_BYTES = 4470


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces(self):
        rebuilt = json.loads(json.dumps(computed_key_index.build_payload(),
                                        sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class Provenance(unittest.TestCase):
    def test_sources(self):
        sources = payload()['provenance']['sources']
        self.assertEqual(len(sources), 10)
        paths = [row['path'] for row in sources]
        self.assertIn('datas/l2_535b0541_store_key_callers.json.gz', paths)
        self.assertIn('reverse-engineering/il2cpp/stringliteral.json', paths)

    def test_digests_match_workspace(self):
        for row in payload()['provenance']['sources']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])


class Census(unittest.TestCase):
    def test_records_and_sites(self):
        census = payload()['census']
        self.assertEqual(census['records'], 51)
        self.assertEqual(census['sites'], 39)
        self.assertEqual(sum(row['records'] for row in census['by_prefix']), 51)

    def test_shapes_add_up(self):
        kinds = {}
        for row in payload()['sites']:
            kinds[row['kind']] = kinds.get(row['kind'], 0) + 1
        self.assertEqual(kinds, {'parameter': 19, 'band': 12, 'helper': 4,
                                 'static-field': 3, 'counter': 1})

    def test_duplicate_sites(self):
        dups = payload()['census']['duplicates']
        self.assertEqual(len(dups), 12)
        per = {}
        for row in dups:
            per[row['prefix']] = per.get(row['prefix'], 0) + 1
        self.assertEqual(per, {'SLOT_FREE_CARDS_': 4, 'HunterCollectProgress': 2,
                               'Quest_Value_Key': 2, 'Quest_Collect_Index': 2,
                               'Quest_Check_Collect_Index': 2})
        self.assertTrue(all(len(row['raws']) == 2 for row in dups))

    def test_every_site_is_one_of_the_145_sites(self):
        rows = payload()['sites']
        self.assertEqual(len(rows), 39)
        self.assertTrue(all(row['call_rva'] and row['method_rva'] for row in rows))
        keys = {(row['method_rva'], row['call_rva']) for row in rows}
        self.assertEqual(len(keys), 39)


class Bands(unittest.TestCase):
    def test_twelve_bands_three_values(self):
        bands = payload()['bands']
        self.assertEqual(len(bands), 12)
        self.assertEqual({row['band'] for row in bands}, {100, 200, 300})
        self.assertEqual({row['shop'] for row in bands}, {'Arena_Shop', 'PVP_Shop'})
        self.assertEqual({row['namespace'] for row in bands}, {'ARENA', 'PVP'})

    def test_namespaces_stay_separate(self):
        for row in payload()['bands']:
            self.assertTrue(row['prefix'].startswith(row['namespace']))

    def test_bound_is_an_array_length(self):
        for row in payload()['bands']:
            self.assertEqual(row['bound_instruction'], 'ldr w8, [x8, #0x18]'
                             if row['band'] != 300 else 'ldr w1, [x20, #0x18]')

    def test_guard_rvas(self):
        guards = {(row['shop'], row['band']): row['guard_rva']
                  for row in payload()['bands']}
        self.assertEqual(guards[('Arena_Shop', 100)], 22729088)
        self.assertEqual(guards[('Arena_Shop', 200)], 22729088)
        self.assertEqual(guards[('Arena_Shop', 300)], 22728800)
        self.assertEqual(guards[('PVP_Shop', 100)], 19938144)
        self.assertEqual(guards[('PVP_Shop', 300)], 19937856)

    def test_one_site_per_band_and_prefix(self):
        self.assertTrue(all(row['sites'] == 1 for row in payload()['bands']))
        self.assertEqual(len({row['call_rvas'][0] for row in payload()['bands']}), 12)


class Parameters(unittest.TestCase):
    def test_one_row_per_parameter_method(self):
        methods = payload()['parameters']
        self.assertEqual(len(methods), 19)
        self.assertEqual(len({row['method_rva'] for row in methods}), 19)
        self.assertTrue(all(row['sites'] == 1 for row in methods))

    def test_quest_and_video_methods_take_an_int(self):
        names = {row['method'] for row in payload()['parameters']}
        self.assertIn('private static int GetQuestValue(int _indexQuest) { }', names)
        self.assertIn('public static bool IsVideoDone(int index) { }', names)
        self.assertIn('public static int GetStock(int index) { }', names)

    def test_instance_methods_take_the_int_in_w1(self):
        rows = {row['method']: row for row in payload()['sites']
                if row['kind'] == 'parameter'}
        self.assertEqual(rows['private int GetIdItem(int index) { }']['parameter'], 'w1')
        self.assertEqual(rows['public static int GetStockItem(int index) { }']
                         ['parameter'], 'w0')


class Sentinel(unittest.TestCase):
    def test_value_and_sites(self):
        sentinel = payload()['sentinel']
        self.assertEqual(sentinel['value'], 999)
        self.assertEqual(sentinel['sites'], 20)
        self.assertEqual(sentinel['families'], ['Quest_Collect_Index',
                                                'Quest_Value_Key'])

    def test_it_shows_up_in_two_families(self):
        per_family = {}
        for row in payload()['parameters']:
            if row['sentinel_sites']:
                per_family[row['prefix']] = per_family.get(row['prefix'], 0) + \
                    len(row['sentinel_sites'])
        self.assertEqual(per_family, {'Quest_Value_Key': 16,
                                      'Quest_Collect_Index': 4})


class Families(unittest.TestCase):
    def test_fourteen_prefix_buckets(self):
        families = payload()['families']
        self.assertEqual(len(families), 14)
        self.assertEqual(sum(row['records'] for row in families), 51)

    def test_only_the_shop_namespaces_are_enumerable(self):
        enumerable = {row['prefix'] for row in payload()['families']
                      if row['statically_enumerable']}
        self.assertEqual(enumerable, {'ARENA_SHOP_ITEM_ID', 'ARENA_SHOP_ITEM_STOCK',
                                      'PVP_SHOP_ITEM_ID', 'PVP_SHOP_ITEM_STOCK'})

    def test_helper_prefix_is_not_enumerable(self):
        row = next(row for row in payload()['families']
                   if row['prefix'] == 'SLOT_FREE_CARDS_')
        self.assertEqual(row['records'], 8)
        self.assertFalse(row['statically_enumerable'])


class NotDecoded(unittest.TestCase):
    def test_three_items_and_the_blocker(self):
        items = payload()['not_decoded']
        self.assertEqual(len(items), 3)
        text = ' '.join(item['blocking'] for item in items)
        self.assertIn('serialized', text)
        self.assertIn('MODEL_NOT_MEASURED runtime', text)


if __name__ == '__main__':
    unittest.main()
