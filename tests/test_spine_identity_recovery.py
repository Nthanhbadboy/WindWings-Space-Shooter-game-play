from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path('tools/recovery').resolve()))
from spine_identity import atlas_pages,walk_pointers

class SpineRecoveryTests(unittest.TestCase):
    def test_atlas_pages_not_region_names(self):
        text='skeleton.png\r\nsize: 100,200\r\nformat: RGBA8888\r\nfilter: Linear,Linear\r\npart\r\n  rotate: false\r\n  xy: 0, 0\r\n\r\nsecond.png\r\nsize: 10,20\r\npart2\r\n  size: 1,2\r\n'
        self.assertEqual([p['name'] for p in atlas_pages(text)],['skeleton.png','second.png'])
        self.assertEqual(atlas_pages(text)[0]['header_lines'],['size: 100,200','format: RGBA8888','filter: Linear,Linear'])

    def test_nested_pointer_locations_keep_array_ordinals(self):
        ptr=dict(m_FileID=2,m_PathID=5)
        value={'atlasAssets':[ptr], 'materials':[dict(m_FileID=0,m_PathID=0)]}
        self.assertEqual(list(walk_pointers(value)),[('.atlasAssets[0]',ptr),('.materials[0]',dict(m_FileID=0,m_PathID=0))])

if __name__=='__main__':unittest.main()
