import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/apk-analyze'))
from ui_render_context import file_context


class RenderContextTests(unittest.TestCase):
    def test_raw_reader_with_none_object_reader_keeps_its_file(self):
        sf = SimpleNamespace(name='sharedassets0.assets', externals=[SimpleNamespace(path='resources.assets')])
        raw = SimpleNamespace(object_reader=None, assets_file=sf)
        self.assertEqual(file_context(raw)['serialized_file'], 'sharedassets0.assets')
        self.assertEqual(file_context(raw)['externals'][0]['file_id'], 1)
        self.assertEqual(file_context(SimpleNamespace(object_reader=raw)), file_context(raw))

    def test_missing_file_is_explicit(self):
        self.assertEqual(file_context(SimpleNamespace())['context_status'], 'missing_serialized_file')


if __name__ == '__main__':
    unittest.main()
