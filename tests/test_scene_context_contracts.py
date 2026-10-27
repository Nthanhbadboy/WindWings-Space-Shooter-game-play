import gzip
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/verify'))
import scene_context_contracts as ctx


class SceneContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.contract=ctx.build()

    def test_snapshot_regeneration(self):
        self.assertEqual(self.contract,json.load(gzip.open(ROOT/'datas/scene_render_context_contract.json.gz','rt')))

    def test_layer_bitmask_including_signed_high_bit(self):
        self.assertTrue(ctx.layer_allowed(32,5));self.assertFalse(ctx.layer_allowed(32,8))
        self.assertTrue(ctx.layer_allowed(-1,31));self.assertTrue(ctx.layer_allowed(-2147483648,31))
        self.assertFalse(ctx.layer_allowed(-2147483648,0))
        for layer in [-1,32]:
            with self.assertRaises(ValueError):ctx.layer_allowed(32,layer)

    def test_scoped_context_counts_and_cross_capture_identity(self):
        s=self.contract['summary']
        self.assertEqual((s['cameras'],s['masks'],s['sorting_groups']),(5,12,0))
        self.assertEqual(s['cross_capture_objects_equal'],66)
        self.assertEqual(self.contract['scope']['all_file_context_counts']['data.unity3d/resources.assets|SpriteMask'],191)
        self.assertEqual(self.contract['scope']['all_file_context_counts']['data.unity3d/sharedassets0.assets|Camera'],1)

    def test_game_camera_and_ui_camera_are_disjoint_layer_masks(self):
        cameras=[r for r in self.contract['cameras'] if r['identity']['serialized_file']=='data.unity3d/level2']
        bits={r['identity']['path_id']:r['tree']['m_CullingMask']['m_Bits'] for r in cameras}
        self.assertEqual(bits,{3975:7959,3976:32})
        self.assertEqual(bits[3975]&bits[3976],0)
        self.assertTrue(ctx.layer_allowed(bits[3975],12));self.assertFalse(ctx.layer_allowed(bits[3976],12))
        self.assertEqual(self.contract['tagmanager']['layers'][12],'Map')
        self.assertEqual(self.contract['tagmanager']['sorting_layers'],[{'name':'Default','uniqueID':0}])

    def test_mask_fields_not_overwritten_and_not_binding_claims(self):
        masks=self.contract['masks']
        self.assertEqual(sum(m['serialized_active_enabled'] for m in masks),3)
        self.assertEqual(len({ctx.key(m['sprite']) for m in masks}),1)
        self.assertEqual(sum(m['tree']['m_IsCustomRangeActive'] for m in masks),9)
        for p in self.contract['renderer_predicates']:
            self.assertIn('not proven affecting-mask bindings',p['warning'])

    def test_activity_and_layer_predicates_do_not_claim_visibility(self):
        self.assertEqual(self.contract['summary']['mask_dependent_renderers'],303)
        self.assertEqual(self.contract['summary']['renderers_passing_any_same_scene_camera_layer_and_serialized_activity_only'],78)
        self.assertEqual(len(self.contract['renderer_predicates']),1377)
        self.assertTrue(any('not frustum' in s for s in self.contract['limits']))
        self.assertNotIn('visible_renderers',self.contract)

    def test_cameras_retain_source_projection_not_viewport_simulation(self):
        for c in self.contract['cameras']:
            t=c['tree'];self.assertTrue(t['orthographic'])
            self.assertEqual(t['orthographic size'],9.600000381469727)
            self.assertEqual(t['m_TargetTexture'],{'m_FileID':0,'m_PathID':0})
            self.assertEqual(t['m_NormalizedViewPortRect'],{'x':0.,'y':0.,'width':1.,'height':1.})
            self.assertNotIn('world_matrix',c)


if __name__=='__main__':unittest.main()
