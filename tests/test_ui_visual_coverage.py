import ast
from collections import deque
import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('visual', ROOT / 'tools/verify/ui_visual_coverage.py')
visual = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visual)


class VisualCoverageTests(unittest.TestCase):
    def test_missing_localization_stays_missing_and_alias_reference_is_preserved(self):
        panels = [{'field': 'tutSettings', 'reference': {'m_FileID': 0, 'm_PathID': 634},
                   'status': 'local_panel_exported', 'nodes': [{'path': 'A', 'components': [{'key': 'unknown'}]}]}]
        out = visual.panel_inventory(panels, {})
        self.assertEqual(out[0]['reference']['m_PathID'], 634)
        self.assertIsNone(out[0]['texts'][0]['vi'])
        self.assertEqual(out[0]['texts'][0]['status'], 'missing_key')

    def test_budget_reports_pending_nodes(self):
        tree = ast.parse((ROOT / 'tools/apk-analyze/ui_layout.py').read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'walk')
        child = SimpleNamespace(m_Children=[])
        root = SimpleNamespace(m_Children=[child])
        ns = {'deque': deque, 'stable_object_id': id, '_pptr': lambda x: x,
              'node_info': lambda x: {'name': 'node', 'components': []}}
        exec(compile(ast.Module(body=[fn], type_ignores=[]), '<walk>', 'exec'), ns)
        d = {}
        self.assertEqual(len(ns['walk'](root, 1, d)), 1)
        self.assertTrue(d['truncated'])
        self.assertEqual(d['pending_transforms'], 1)
        d = {}
        self.assertEqual(len(ns['walk'](root, 2, d)), 2)
        self.assertFalse(d['truncated'])


if __name__ == '__main__':
    unittest.main()
