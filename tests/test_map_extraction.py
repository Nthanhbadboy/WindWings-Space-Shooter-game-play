"""Regression checks against preserved APK evidence, not gameplay assumptions."""
import json
import unittest
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text())


class MapExtractionTests(unittest.TestCase):
    def test_all_initialize_array_calls_join(self):
        rows = load('reverse-engineering/il2cpp/ia-resolved.json')['methods']['Map_Get_Datas.cctor']
        segments = load('datas/map_segments_full.json')['segments']
        arrays = [a for s in segments for a in s['arrays'] if a['source'] == 'InitializeArray']
        self.assertEqual(len(rows), 576)
        self.assertEqual(len(arrays), 576)
        self.assertEqual({a['addr'] for a in arrays}, {r['array_new_addr'] for r in rows})
        for r in rows:
            self.assertTrue(r['length_valid'])
            self.assertEqual(r['len'], len(r['ints']))

    def test_campaign_has_no_unknowns(self):
        maps = load('datas/maps.json')['maps']
        campaign = next(s for s in load('datas/map_segments_full.json')['segments'] if s['index'] == 35)
        self.assertEqual(len(maps), 250)
        self.assertEqual(maps, [a['values'] for a in campaign['arrays']])
        self.assertTrue(all(isinstance(v, int) for m in maps for v in m))
        self.assertEqual(maps[4], [95, 11, 7008])

    def test_zero_initialized_slot(self):
        segment = next(s for s in load('datas/map_segments_full.json')['segments'] if s['index'] == 69)
        first = segment['arrays'][0]
        self.assertEqual(first['addr'], '0x1416b20')
        self.assertEqual(first['values'], [0, 1])

    def test_dynamic_length_is_not_stale_immediate(self):
        data = load('datas/map_segments_full.json')
        dynamic = data['standalone_arrays'][0]
        self.assertEqual(dynamic['field'], 'mapChallangeIndexs')
        self.assertIsNone(dynamic['len'])
        self.assertEqual(dynamic['array_new_addr'], '0x14178b4')
        self.assertNotIn(dynamic['array_new_addr'], [a['addr'] for s in data['segments'] for a in s['arrays']])


if __name__ == '__main__':
    unittest.main()
