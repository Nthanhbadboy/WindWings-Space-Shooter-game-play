import copy
import gzip
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path('tools/verify').resolve()))
from sprite_geometry import RAW, build, join_sprite, load_objects, resolve, settings, within


class SpriteGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = build()
        _, cls.objects, _ = load_objects()

    def test_rebuild_and_complete_join_not_pixel_claim(self):
        self.assertEqual(json.load(gzip.open(RAW / 'resolved-geometry.json.gz', 'rt')), self.raw)
        self.assertEqual(self.raw['object_counts'], dict(Sprite=2185, Texture2D=654, SpriteAtlas=66))
        self.assertEqual(self.raw['resolved'], 2185)
        self.assertEqual(self.raw['unresolved'], [])
        self.assertEqual(self.raw['routes'], dict(sprite_render_data=635, atlas_pointer_and_render_key=1550))
        self.assertIn('NOT_PIXEL_CROP_VALIDATION', self.raw['status'])

    def test_packing_flags_and_rotation_enum(self):
        self.assertEqual(settings(65), dict(raw=65, packed=True, packing_mode=0, packing_rotation=0, mesh_type=1))
        self.assertEqual(settings(73)['packing_rotation'], 2)
        self.assertEqual(settings(77)['packing_rotation'], 3)
        self.assertEqual(self.raw['rotation_codes'], {'0': 2041, '1': 53, '2': 54, '3': 37})

    def test_file_scope_prevents_namesake_path_collision(self):
        owner = dict(serialized_file='a', externals=[dict(file_id=1, path='archive:/x/b')])
        objects = {('a', 1): {'name': 'a'}, ('b', 1): {'name': 'b'}}
        self.assertEqual(resolve(owner, dict(m_FileID=0, m_PathID=1), objects)['name'], 'a')
        self.assertEqual(resolve(owner, dict(m_FileID=1, m_PathID=1), objects)['name'], 'b')
        self.assertIsNone(resolve(owner, dict(m_FileID=0, m_PathID=0), objects))
        with self.assertRaises(ValueError):
            resolve(owner, dict(m_FileID=2, m_PathID=1), objects)

    def test_rect_predicate_not_auto_clamp(self):
        self.assertTrue(within(dict(x=0, y=0, width=10, height=20), 10, 20))
        self.assertFalse(within(dict(x=0, y=.1, width=10, height=20), 10, 20))
        self.assertFalse(within(dict(x=-.1, y=0, width=10, height=20), 10, 20))
        self.assertFalse(within(dict(x=0, y=0, width=0, height=20), 10, 20))

    def test_40_fractional_rect_exceptions_preserved(self):
        bad = [r for r in self.raw['sprites'] if not r['rect_within_texture']]
        self.assertEqual(len(bad), 40)
        excesses = []
        for r in bad:
            t = r['texture_rect']; w, h = r['texture']['dimensions']
            excesses.append(max(-t['x'], -t['y'], t['x'] + t['width'] - w, t['y'] + t['height'] - h))
        self.assertTrue(all(0 < v < 1 for v in excesses))
        self.assertTrue(all(r['route'] == 'sprite_render_data' for r in bad))

    def test_atlas_key_missing_fails_not_own_rd_fallback(self):
        objects = {(r['serialized_file'], r['path_id']): r for r in self.objects}
        row = copy.deepcopy(next(r for r in self.objects if r['type'] == 'Sprite' and r['tree']['m_SpriteAtlas']['m_PathID']))
        row['tree']['m_RenderDataKey'] = ['not_a_guid', -999]
        with self.assertRaisesRegex(ValueError, 'render key'):
            join_sprite(row, objects)

    def test_texture_projection_does_not_embed_pixels(self):
        for row in self.objects:
            if row['type'] == 'Texture2D':
                self.assertNotIn('image data', row['tree'])
                self.assertNotIn('m_ImageData', row['tree'])
                self.assertEqual(row['projection'], 'metadata_only_no_image_data')


if __name__ == '__main__':
    unittest.main()
