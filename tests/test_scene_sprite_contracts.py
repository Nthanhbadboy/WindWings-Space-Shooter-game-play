import gzip
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/verify'))
import scene_sprite_contracts as scene


class SceneSpriteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.contract=scene.build()

    def test_regenerates_preserved_contract(self):
        self.assertEqual(self.contract,json.load(gzip.open(ROOT/'datas/scene_sprite_contract.json.gz','rt')))

    def test_scope_is_initial_four_scenes_not_dynamic_prefab_population(self):
        c=self.contract
        self.assertEqual(c['summary']['renderers'],1377)
        self.assertEqual(c['scope']['excluded_root_renderer_count'],61438)
        self.assertEqual(c['summary']['unique_sprite_refs'],218)
        self.assertEqual(c['summary']['unique_material_refs'],7)
        self.assertEqual(len(c['scope']['root_files']),4)
        self.assertEqual(c['scope']['object_counts']['SpriteRenderer'],1377)

    def test_buildsettings_scene_order_and_projection(self):
        self.assertEqual([Path(p).stem for p in self.contract['source_scene_paths']],['Menu','Home','Game','EndGame'])
        for row in self.contract['renderers']:
            index=int(row['identity']['serialized_file'].split('level')[-1])
            self.assertEqual(row['source_scene_path'],self.contract['source_scene_paths'][index])
        # build() explicitly checks a narrow field allowlist, not unrelated build metadata.
        self.assertEqual(self.contract['summary']['scenes']['data.unity3d/level2']['renderers'],1036)

    def test_parent_chain_cycle_is_rejected_and_order_is_leaf_to_root(self):
        parents={1:2,2:3,3:None}
        self.assertEqual(scene.ancestor_chain(1,parents.get),[1,2,3])
        parents[3]=1
        with self.assertRaises(ValueError):scene.ancestor_chain(1,parents.get)

    def test_serialized_activity_is_only_an_and_predicate(self):
        self.assertTrue(scene.serialized_activity(True,[True,True]))
        self.assertFalse(scene.serialized_activity(True,[True,False]))
        self.assertFalse(scene.serialized_activity(False,[True,True]))
        self.assertEqual(self.contract['summary']['statistics']['all_serialized_ancestor_gameobjects_active_and_renderer_enabled'],78)
        self.assertEqual(sum(r['sprite'] is None and r['all_serialized_ancestor_gameobjects_active_and_renderer_enabled'] for r in self.contract['renderers']),1)

    def test_flip_negative_scale_and_zero_scale_are_separate_raw_states(self):
        stats=self.contract['summary']['statistics']
        self.assertEqual(stats['flip_x_true'],68)
        self.assertEqual(stats['flip_y_true'],10)
        self.assertEqual(stats['ancestor_chain_negative_scale_component'],14)
        self.assertEqual(stats['ancestor_chain_zero_scale_component'],4)
        self.assertEqual(stats['ancestor_chain_contains_recttransform'],43)
        self.assertEqual(self.contract['summary']['max_ancestor_chain'],10)

    def test_null_sprite_not_repaired_and_numeric_draw_modes_retained(self):
        self.assertEqual(self.contract['summary']['statistics']['null_sprite'],56)
        self.assertEqual(self.contract['summary']['statistics']['disabled_renderer'],26)
        self.assertEqual(self.contract['summary']['draw_mode_counts'],{'0':922,'1':441,'2':14})
        self.assertEqual(self.contract['summary']['sorting_layer_id_counts'],{'0':1377})
        self.assertEqual(self.contract['summary']['mask_interaction_counts'],{'0':1074,'1':302,'2':1})
        self.assertEqual(self.contract['mask_interaction_enum_from_dump'],{'None':0,'VisibleInsideMask':1,'VisibleOutsideMask':2})
        self.assertEqual(self.contract['summary']['statistics']['serialized_renderer_color_alpha_zero'],43)
        self.assertTrue(all((r['mesh_reference'] is None)==(r['sprite'] is None) for r in self.contract['renderers']))

    def test_raw_preservation_guard_and_root_scope(self):
        sys.path.insert(0,str(ROOT/'tools/recovery'))
        import scene_sprite_renderers as recovery
        self.assertEqual(recovery.SCENE_FILES,{f'data.unity3d/level{i}' for i in range(4)})
        workflow=(ROOT/'.github/workflows/recover-scene-sprites.yml').read_text()
        self.assertIn('test -f reverse-engineering/raw/scene-sprites/index.json',workflow)
        self.assertNotIn('scene-sprites/graph-index.json',workflow)


if __name__=='__main__':unittest.main()
