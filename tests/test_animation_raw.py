import importlib.util
import unittest


def load(name):
    spec = importlib.util.spec_from_file_location(name, 'tools/verify/'+name+'.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AnimationRawTests(unittest.TestCase):
    def test_inline_unityevent_in_array_and_empty_event(self):
        module = load('persistent_animation_events')
        data = {'nested': [{'event': {'m_PersistentCalls': {'m_Calls': [{'m_MethodName': 'OnMoveEnded'}]}}}],
                'empty': {'m_PersistentCalls': {'m_Calls': []}}}
        rows = list(module.walk(data))
        self.assertEqual([r[0] for r in rows], ['nested[0].event', 'empty'])
        self.assertEqual(rows[0][1][0]['m_MethodName'], 'OnMoveEnded')
        self.assertEqual(rows[1][1], [])

    def test_graph_keeps_numeric_destination_and_condition(self):
        module = load('animator_graphs')
        raw = {'data': {'m_DestinationState': 30000, 'm_HasExitTime': True,
                        'm_ConditionConstantArray': [{'data': {'m_EventID': 42, 'm_ConditionMode': 1, 'm_EventThreshold': 0.0}}]}}
        result = module.transitions([raw], {42: 'Attack'})[0]
        self.assertEqual(result['raw']['m_DestinationState'], 30000)
        self.assertTrue(result['raw']['m_HasExitTime'])
        self.assertEqual(result['conditions'][0]['parameter_name'], 'Attack')
        self.assertEqual(result['conditions'][0]['raw']['m_ConditionMode'], 1)
