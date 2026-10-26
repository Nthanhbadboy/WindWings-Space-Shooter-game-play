import copy
import gzip
import json
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path('tools/verify').resolve()))
from balloon_animation import RAW, SOURCE, build, decode_clip, decode_stream, path_index, width


class BalloonAnimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build()
        cls.source = json.loads(gzip.decompress(SOURCE.read_bytes()))

    def test_reproducible_and_checks(self):
        self.assertEqual(json.loads(gzip.decompress((RAW / 'decoded-clips.json.gz').read_bytes())), self.result)
        self.assertEqual(len(self.result['checks']), 17)
        self.assertTrue(all(self.result['checks'].values()))

    def test_graph_and_clip_duration(self):
        self.assertEqual([s['clip_indices'] for s in self.result['states']], [[0], [1], [2]])
        self.assertEqual([c['stop'] for c in self.result['clips']], [2.5, 10, 12])
        self.assertTrue(all(c['loop'] for c in self.result['clips']))
        self.assertEqual([len(c['frames']) for c in self.result['clips']], [9, 66, 76])

    def test_root_position_and_constant_rotation(self):
        for c in self.result['clips']:
            b = c['bindings'][0]
            self.assertEqual(b['paths'], [''])
            self.assertEqual(len(b['channels']), 3)
            self.assertEqual(b['targets'][0]['type'], 'Transform')
        attack = self.result['clips'][2]
        self.assertEqual([c['storage'] for c in attack['bindings'][-1]['channels']], ['constant'] * 3)
        self.assertEqual([c['value'] for c in attack['bindings'][-1]['channels']], [0, 0, 0])
        root = self.result['clips'][0]['bindings'][0]['channels']
        self.assertAlmostEqual(root[0]['keys'][1]['value'], -12.41, places=5)
        self.assertAlmostEqual(root[1]['keys'][-1]['value'], 2.3, places=5)

    def test_sentinel_not_playable_keyframe(self):
        for c in self.result['clips']:
            self.assertEqual(c['frames'][0]['time'], -3.4028234663852886e38)
            self.assertEqual(c['frames'][-1], dict(time='inf', keys=[]))
            self.assertEqual(c['frames'][1]['time'], 0)

    def test_enabled_targets_use_header_not_misaligned_tree_script(self):
        idle = self.result['clips'][1]
        binding = next(b for b in idle['bindings'] if b['paths'] == ['Enemy_Ingame/Barrels1'])
        self.assertEqual(binding['targets'], [dict(path='Enemy_Ingame/Barrels1', path_id=690037, type='Machine_Gun_Attack')])
        values = [(k['time'], k['value']) for k in binding['channels'][0]['keys'] if k['time'] >= 0]
        self.assertEqual(values, [(0, 1), (9, 0)])
        collider = idle['bindings'][-1]
        self.assertEqual(collider['targets'][0]['path_id'], 490394)

    def test_duplicate_child_names_preserved(self):
        self.assertEqual(len(self.result['duplicate_paths']), 9)
        for candidates in self.result['duplicate_paths'].values():
            self.assertEqual(len(candidates), 2)
        self.assertTrue(all(len(b['paths']) == 1 for c in self.result['clips'] for b in c['bindings']))

    def test_stream_rejects_bad_layout_and_index(self):
        def words(blob):
            return list(struct.unpack('<' + 'I' * (len(blob) // 4), blob))
        for blob in [struct.pack('<f', 0), struct.pack('<fi', 0, -1), struct.pack('<fi', 0, 1),
                     struct.pack('<fii4f', 0, 1, 1, 0, 0, 0, 2),
                     struct.pack('<fi', 1, 0) + struct.pack('<fi', 0, 0)]:
            with self.assertRaises(ValueError):
                decode_stream(words(blob), 1)
        blob = struct.pack('<fii4f', 0, 1, 0, 1, 2, 3, 4)
        self.assertEqual(decode_stream(words(blob), 1)[0]['keys'][0]['value'], 4)
        self.assertEqual(width(dict(typeID=4, attribute=2)), 4)

    def test_channel_coverage_fails_closed(self):
        record = copy.deepcopy(self.source['clips'][0])
        record['tree']['m_ClipBindingConstant']['genericBindings'].pop()
        with self.assertRaisesRegex(ValueError, 'coverage mismatch'):
            decode_clip(record, path_index(self.source['nodes']))
        record = copy.deepcopy(self.source['clips'][0])
        record['tree']['m_MuscleClip']['m_Clip']['data']['m_DenseClip']['m_CurveCount'] = 1
        with self.assertRaisesRegex(ValueError, 'dense sample size mismatch'):
            decode_clip(record, path_index(self.source['nodes']))


if __name__ == '__main__':
    unittest.main()
