import json
from pathlib import Path
import sys
from types import SimpleNamespace as NS
import unittest
sys.path.insert(0, str(Path('tools/recovery').resolve()))
from asset_pack_v2 import identity_path, serialized_files, text_bytes, font_extension, browser_html


class AssetPackV2Tests(unittest.TestCase):
    def test_identity_names_do_not_collapse_same_basename_or_pathid(self):
        paths = [identity_path(file, kind, pid) for file in ('one/resources.assets','two/resources.assets')
                 for kind in ('Sprite','Texture2D') for pid in (3,-3)]
        self.assertEqual(len(set(paths)), 8)
        self.assertTrue(all(len(Path(p).name) < 180 for p in paths))
        self.assertNotIn('..', identity_path('../../weird/file', 'Sprite', 1).split('/'))

    def test_walk_stops_at_serialized_object_dict(self):
        sf=NS(objects={1:NS()},files={1:NS()})
        env=NS(files={'/tmp/input/data.unity3d':NS(files={'resources.assets':sf})})
        self.assertEqual(serialized_files(env), [('data.unity3d/resources.assets',sf)])

    def test_aliases_rejected(self):
        sf=NS(objects={})
        with self.assertRaises(ValueError):
            serialized_files(NS(files={'a':sf,'b':sf}))

    def test_text_and_font_preserved_not_reinvented(self):
        self.assertEqual(text_bytes(b'\xff\x00'), b'\xff\x00')
        self.assertEqual(text_bytes('\udcff'), b'\xff')
        self.assertEqual(font_extension(b'OTTOabcd'), '.otf')
        self.assertEqual(font_extension(b'\x00\x01\x00\x00'), '.ttf')
        with self.assertRaises(ValueError):
            font_extension(b'notafont')

    def test_offline_browser_escapes_script_and_uses_text_nodes(self):
        value=browser_html(dict(objects=[dict(name='</script><script>alert(1)</script>')]))
        self.assertIn('\\u003c/script>', value)
        self.assertNotIn('innerHTML',value)
        self.assertNotIn('fetch(', value)
        self.assertIn('Spine page references have NOT been rewritten', value)


if __name__ == '__main__':
    unittest.main()
