import copy
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/verify'))
import sprite_mesh_contracts as mesh


class SpriteMeshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.contract=mesh.build()

    def test_regeneration_and_preserved_derivation(self):
        blob=gzip.decompress((ROOT/'datas/sprite_mesh_contract.json.gz').read_bytes())
        self.assertEqual(json.loads(blob),self.contract)
        evidence=json.loads((ROOT/'reverse-engineering/raw/sprite-meshes/derivation.json').read_text())
        self.assertEqual(evidence['contract_sha256_decompressed'],hashlib.sha256(blob).hexdigest())
        self.assertEqual(evidence['summary'],self.contract['summary'])
        self.assertEqual(evidence['geometry_chunks'],self.contract['source_geometry_chunks'])
        self.assertEqual(evidence['decoder']['sha256'],hashlib.sha256((ROOT/evidence['decoder']['path']).read_bytes()).hexdigest())

    def test_arithmetic_origin_is_not_clamped(self):
        points=[(1.,-1.,0.),(3.,-1.,0.),(3.,1.,0.)]
        r=mesh.mesh_metrics(points,[(0,1,2)])
        self.assertEqual(r['origin_relative_to_mesh_aabb'],[-.5,.5])
        self.assertTrue(r['origin_outside_xy_aabb_gt_1e_5'])

    def test_winding_and_zero_area_not_repaired(self):
        points=[(0.,0.,0.),(1.,0.,0.),(0.,1.,0.)];indices=[(0,1,2),(2,1,0),(0,0,1)]
        before=copy.deepcopy(indices)
        r=mesh.mesh_metrics(points,indices)
        self.assertEqual(r['triangle_cross_sign_counts'],{'positive':1,'negative':1,'zero':1})
        self.assertEqual(indices,before)

    def test_reject_nonfinite_zero_span_and_bad_index(self):
        for points,triangles in [([(0,0,0),(math.inf,1,0)],[]),([(0,0,0),(0,1,0)],[]),([(0,0,0),(1,1,0)],[(0,1,2)])]:
            with self.assertRaises(ValueError):mesh.mesh_metrics(points,triangles)

    def test_real_counts_and_distinct_serialized_bounds(self):
        s=self.contract['summary'];self.assertEqual((s['sprites'],s['vertices'],s['triangles']),(2185,27072,24375))
        self.assertEqual(s['diagnostics']['serialized_submesh_aabb_all_zero'],2185)
        self.assertEqual(s['diagnostics']['origin_outside_mesh_xy_aabb'],7)
        self.assertEqual(s['diagnostics']['origin_outside_mesh_xy_aabb_gt_1e_5'],6)
        self.assertEqual(s['diagnostics']['mesh_aabb_anchor_differs_from_source_pivot_gt_1e_5'],467)
        self.assertEqual(s['triangle_cross_sign_counts'],{'negative':24013,'zero':345,'positive':17})
        self.assertEqual(len(s['pixels_to_units_counts']),497)

    def test_source_pivot_and_mesh_anchor_remain_separate(self):
        row=next(r for r in self.contract['sprites'] if r['identity']['path_id']==3050 and r['identity']['serialized_file']=='data.unity3d/resources.assets')
        self.assertLess(row['metrics']['origin_relative_to_mesh_aabb'][0],0)
        self.assertEqual(row['source_pivot'],row['export_presentation']['source_normalized_pivot'])
        self.assertNotIn('png_pivot',row)


if __name__=='__main__':unittest.main()
