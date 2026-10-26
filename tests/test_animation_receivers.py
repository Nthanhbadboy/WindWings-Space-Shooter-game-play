import gzip
import importlib.util
import json
import unittest

spec = importlib.util.spec_from_file_location('receivers', 'tools/verify/animation_receivers.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AnimationReceiverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = module.build()

    def test_current_capture_coverage(self):
        events = self.data['events']
        self.assertEqual(len(events), 795)
        self.assertEqual(sum(bool(e['receiver_candidates']) for e in events), 711)

    def test_each_candidate_component_is_on_animator_gameobject(self):
        cache = {}
        for event in self.data['events']:
            for receiver in event['receiver_candidates']:
                source = receiver['source']
                if source not in cache:
                    with gzip.open(source, 'rt') as stream:
                        cache[source] = {r['path_id']: r['tree'] for r in map(json.loads, stream)}
                tree = cache[source][receiver['component_path_id']]
                self.assertEqual(tree['m_GameObject'], event['gameobject_ref'])
                self.assertTrue(receiver['methods'])

    def test_ambiguity_is_not_collapsed(self):
        self.assertTrue(any(len(e['receiver_candidates']) > 1 for e in self.data['events']))
        self.assertTrue(any(not e['receiver_candidates'] for e in self.data['events']))


if __name__ == '__main__':
    unittest.main()
