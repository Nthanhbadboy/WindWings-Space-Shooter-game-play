import ast
import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('drawing', ROOT / 'tools/verify/ui_drawing_readiness.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class DrawingAuditTests(unittest.TestCase):
    def test_name_match_is_candidate_not_exact_pointer(self):
        self.assertEqual(mod.sprite_match('A', {'A': [{'path_id': '1'}]})['status'], 'unique_name_candidate')
        self.assertEqual(mod.sprite_match('A', {'A': [{}, {}]})['status'], 'ambiguous_name')
        self.assertEqual(mod.sprite_match('A', {})['status'], 'not_in_index')

    def test_stable_id_uses_reader_not_python_identity(self):
        # Import only this pure helper: the extractor itself needs runner UnityPy.
        tree = ast.parse((ROOT / 'tools/apk-analyze/ui_layout.py').read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'stable_object_id')
        namespace = {}
        exec(compile(ast.Module(body=[fn], type_ignores=[]), '<helper>', 'exec'), namespace)
        f = namespace['stable_object_id']
        for _ in range(2):
            self.assertEqual(f(SimpleNamespace(object_reader=SimpleNamespace(path_id=123))), 123)
        self.assertEqual(f(SimpleNamespace(path_id=456)), 456)


if __name__ == '__main__':
    unittest.main()
