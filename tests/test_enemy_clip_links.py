import importlib.util
import unittest

spec = importlib.util.spec_from_file_location('clip_links', 'tools/verify/enemy_clip_links.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EnemyClipLinksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = module.build()

    def test_external_reference_not_treated_as_local(self):
        self.assertFalse(module.local_ref({'m_FileID': 1, 'm_PathID': 37}))
        self.assertFalse(module.local_ref({'m_FileID': 0, 'm_PathID': 0}))
        self.assertTrue(module.local_ref({'m_FileID': 0, 'm_PathID': 37}))

    def test_no_controller_or_clip_dangling_in_current_capture(self):
        rows = self.result['animators']
        self.assertEqual(len(rows), 154)
        self.assertEqual(len({r['prefab_root'] for r in rows}), 63)
        for row in rows:
            self.assertEqual(row['status'], 'resolved')
            self.assertEqual(len(row['clips']), row['declared_clip_count'])
            for clip in row['clips']:
                self.assertEqual(clip['status'], 'resolved')
                self.assertEqual(len(clip['events']), clip['declared_event_count'])
                self.assertFalse(clip['curves_decoded'])

    def test_event_times_inside_clip(self):
        unique = {c['ref']['m_PathID']: c for r in self.result['animators'] for c in r['clips']}
        self.assertEqual(len(unique), 393)
        self.assertEqual(sum(len(c['events']) for c in unique.values()), 731)
        for clip in unique.values():
            for event in clip['events']:
                self.assertGreaterEqual(event['time'], clip['start'] - 1e-5)
                self.assertLessEqual(event['time'], clip['stop'] + 1e-5)


if __name__ == '__main__':
    unittest.main()
