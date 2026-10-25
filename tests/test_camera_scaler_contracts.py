import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/verify'))
import camera_scaler_contracts as scaler


class CameraScalerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.contract=scaler.build()

    def test_regenerates_snapshot(self):
        self.assertEqual(self.contract,json.loads((ROOT/'datas/camera_scaler_contract.json').read_text()))

    def test_pool_values_are_exact_binary32_not_rounded_report_numbers(self):
        c=self.contract
        self.assertEqual(c['factor'],5.400000095367432)
        self.assertEqual(c['minimum'],9.600000381469727)
        self.assertEqual([r['hex'] for r in c['float_pool']],['cdccac40','9a991941'])

    def test_tall_screen_changes_size_not_always_serialized_9_6(self):
        c=self.contract;calculate=lambda w,h:scaler.scaled_ortho(w,h,c['factor'],c['minimum'])
        self.assertEqual(calculate(1080,1920),c['minimum'])
        self.assertEqual(calculate(1080,2400),12.000000953674316)
        self.assertEqual(calculate(390,844),11.68615436553955)
        self.assertEqual(calculate(1920,1080),c['minimum'])

    def test_arithmetic_model_declines_unsupported_screen_inputs(self):
        c=self.contract
        for w,h in [(0,1920),(-1,1920),(1080,0),(1<<31,1920),(1080.,1920),(True,1920)]:
            with self.assertRaises(ValueError):scaler.scaled_ortho(w,h,c['factor'],c['minimum'])

    def test_all_scene_cameras_bound_but_shared_reference_not_spawn_claim(self):
        c=self.contract
        self.assertEqual(c['summary'],{'components':5,'camera_refs':6,'scene_cameras_bound':5})
        shared=[r for r in c['components'] if r['identity']['serialized_file']=='data.unity3d/sharedassets0.assets']
        self.assertEqual(len(shared),1)
        self.assertEqual(shared[0]['camera_array_order'][0]['path_id'],79)

    def test_reverse_array_order_retained(self):
        row=next(r for r in self.contract['components'] if r['identity']['serialized_file']=='data.unity3d/level2')
        self.assertEqual([c['path_id'] for c in row['camera_array_order']],[3976,3975])
        self.assertEqual([c['path_id'] for c in row['native_write_order']],[3975,3976])

    def test_awake_analysis_clips_export_overlap(self):
        awake=self.contract['awake_declared_span']
        self.assertEqual(len(awake['instructions']),1)
        self.assertIn('0x141d70c: b',awake['instructions'][0])
        self.assertEqual(len(awake['outside_declared_span']),1)
        self.assertIn('0x141d710:',awake['outside_declared_span'][0])

    def test_consumer_checks_and_partial_class_census(self):
        self.assertTrue(all(self.contract['native_checks'].values()))
        self.assertEqual(self.contract['scan']['headers'],125453)
        self.assertEqual(len(self.contract['scan']['header_errors']),1)
        self.assertIn('set_orthographicSize',self.contract['resolved_calls']['0x275e1b0'])


if __name__=='__main__':unittest.main()
