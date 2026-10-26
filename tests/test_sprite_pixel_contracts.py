import gzip
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path('tools/verify').resolve()))
from sprite_pixel_contracts import build

class SpritePixelContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=build()

    def test_preserved_contract_reproduces(self):
        saved=json.loads(gzip.decompress(Path('datas/sprite_export_contract.json.gz').read_bytes()))
        self.assertEqual(saved,self.data)

    def test_exact_export_reproduction_is_not_gpu_approval(self):
        summary=self.data['summary']
        self.assertEqual(summary['total'],2185)
        self.assertEqual(summary['outcomes'],{'match':2185})
        self.assertEqual(summary['rotation_counts'],{'0':2041,'2':54,'1':53,'3':37})
        self.assertEqual(summary['fractionals'],593)
        self.assertEqual(self.data['status'],'provisional_export_reference_not_Unity_render_approval')
        self.assertIn('not Unity GPU',self.data['limits'][-1])

    def test_float_outside_is_not_always_integer_padding(self):
        rows=self.data['fractional_outside']
        self.assertEqual(len(rows),40)
        padded=[r for r in rows if any(r['padding'].values())]
        self.assertEqual(len(padded),9)
        self.assertEqual(sum(r['padding']['top']==1 for r in padded),8)
        self.assertEqual(sum(r['padding']['right']==1 for r in padded),1)
        self.assertEqual(sum(r['export_size']!=r['counterfactual_clamped_size'] for r in rows),9)

    def test_trimmed_png_cannot_reuse_source_normalized_pivot_without_offsets(self):
        self.assertEqual(self.data['summary']['export_size_differs_from_rounded_source_rect'],517)
        self.assertIn('NOT a pivot normalized',self.data['limits'][0])
        for r in self.data['sprites']:
            self.assertIn('source_normalized_pivot',r['presentation'])
            self.assertIn('trim_offset',r['presentation'])
            self.assertNotIn('final_png_pivot',r['presentation'])

if __name__=='__main__':unittest.main()
