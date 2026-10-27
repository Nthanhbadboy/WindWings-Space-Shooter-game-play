import gzip
import json
import unittest

from tools.build_l2_a5a74747_26_static_root_projection import (
    OUTPUT_PATH,
    ROOT,
    _source_matches,
    build_receipt,
    encode_receipt,
    read_inputs,
)


class StaticRootProjection26Tests(unittest.TestCase):
    def artifact(self):
        return json.loads(gzip.decompress((ROOT / OUTPUT_PATH).read_bytes()))

    def test_deterministic_pinned_builder(self):
        self.assertEqual(encode_receipt(build_receipt(read_inputs())), (ROOT / OUTPUT_PATH).read_bytes())

    def test_exact_resources_root_and_popup_parent_chain(self):
        artifact = self.artifact()
        root = artifact["template_root"]
        popup = artifact["popup_template"]
        self.assertEqual((root["serialized_file"], root["path_id"], root["root_transform_path_id"]),
                         ("data.unity3d/resources.assets", 212696, 439142))
        self.assertFalse(root["serialized_active"])
        self.assertEqual(root["node_count"], 235)
        self.assertEqual((popup["gameobject_path_id"], popup["transform_path_id"], popup["parent_transform_path_id"]),
                         (57508, 425352, 439142))
        self.assertEqual(popup["pointers"], {
            "transform_m_GameObject": 57508,
            "transform_m_Father": 439142,
            "parent_transform_m_GameObject": 212696,
            "parent_transform_m_Father": 0,
        })
        self.assertFalse(popup["serialized_active"])
        self.assertEqual(popup["local_position"], [0.0, 0.0, -2.0])
        self.assertEqual(popup["board_pause_hierarchy_path"], "Board_Pause/Popup_QuitMissions")

    def test_projection_remains_null_and_not_render_approval(self):
        artifact = self.artifact()
        projection = artifact["projection"]
        self.assertEqual(artifact["status"], "BOUNDED_STATIC_EVIDENCE_NO_SCENE_INSTANCE_PIXEL_BOUNDS_NULL")
        self.assertEqual(projection["status"], "NOT_PROJECTED_NO_SCENE_INSTANCE_CAMERA_BINDING")
        self.assertIsNone(projection["pixel_bounds"])
        self.assertFalse(projection["rendered"])
        self.assertEqual(artifact["task"]["runtime_readback"], "NOT_OBSERVED")
        self.assertFalse(artifact["task"]["source_package_modified"])

    def test_scene_non_observation_is_explicitly_bounded(self):
        scope = self.artifact()["inventoried_scene_scope"]
        self.assertEqual(scope["root_files"], [
            "data.unity3d/level0", "data.unity3d/level1",
            "data.unity3d/level2", "data.unity3d/level3",
        ])
        self.assertEqual(scope["scene_sprites"]["object_records"], 5698)
        self.assertEqual(scope["scene_sprites"]["link_records"], 10279)
        self.assertEqual(scope["scene_sprites"]["exact_name_or_path_id_matches"], 0)
        self.assertEqual(scope["scene_sprites"]["direct_pointer_edges_to_board_pause_root"], 0)
        self.assertEqual(scope["scene_context"]["object_records"], 122)
        self.assertEqual(scope["scene_context"]["link_records"], 194)
        self.assertEqual(scope["scene_context"]["exact_name_or_path_id_matches"], 0)
        self.assertEqual(scope["scene_context"]["direct_pointer_edges_to_board_pause_root"], 0)
        self.assertIn("not proof of absence", scope["absence_boundary"])
        self.assertIn("not a complete all-class scene", scope["scene_sprites"]["scope_note"])

    def test_camera_inventory_is_not_arbitrated_to_template(self):
        artifact = self.artifact()
        cameras = artifact["camera_inventory"]
        self.assertEqual(len(cameras), 5)
        self.assertEqual({row["serialized_file"] for row in cameras}, {
            "data.unity3d/level0", "data.unity3d/level1", "data.unity3d/level2", "data.unity3d/level3",
        })
        self.assertTrue(all(row["selected_for_board_pause_projection"] is False for row in cameras))
        self.assertTrue(all(row["template_instance_link"] is None for row in cameras))
        self.assertTrue(all(row["normalized_viewport_rect"] == {
            "x": 0.0, "y": 0.0, "width": 1.0, "height": 1.0,
        } for row in cameras))
        self.assertTrue(all(row["target_texture"] == {"m_FileID": 0, "m_PathID": 0} for row in cameras))

    def test_capture_inventory_and_cross_branch_provenance_are_pinned(self):
        artifact = self.artifact()
        self.assertEqual(len(artifact["input_pins"]), 72)
        self.assertEqual(artifact["input_manifest_sha256"], "e25ebebef425f9bbafd9d7887c8097231c195fb7f3b8f0a75283ef38465748c8")
        provenance = artifact["source_provenance"]
        self.assertEqual(provenance["raw_scene_capture_snapshot"]["commit"], "33cdc61a912c006a6169583dfad444841033df7a")
        self.assertIn("not independently retrieved", provenance["package_metadata_authority"])
        self.assertEqual(provenance["transform_tree_source"]["sha256"],
                         "30624c3e69a64559d0b790d48a6aa06db725edbcb9687e1457e72e7311c76ae2")

    def test_search_helper_detects_name_ids_and_direct_pointers(self):
        objects = [{"type": "GameObject", "path_id": 212696, "tree": {"m_Name": "Board_Pause"}}]
        links = [{
            "owner": {"serialized_file": "data.unity3d/level2", "path_id": 99},
            "pointer": {"m_FileID": 3, "m_PathID": 212696},
            "target": {"serialized_file": "data.unity3d/resources.assets", "path_id": 212696},
        }]
        matches = _source_matches(objects, links)
        self.assertGreaterEqual(len(matches["exact_name_or_path_id_matches"]), 2)
        self.assertEqual(len(matches["direct_pointer_edges_to_board_pause_root"]), 1)

    def test_limits_preserve_no_screenshot_runtime_or_global_absence(self):
        boundaries = " ".join(self.artifact()["evidence_boundary"])
        self.assertIn("no screenshot", boundaries)
        self.assertIn("not repository-wide or all-bundle absence proof", boundaries)
        self.assertIn("no camera was guessed or selected", boundaries)
        self.assertIn("No runtime/render approval", boundaries)
        self.assertIn("pixel bounds", boundaries)


if __name__ == "__main__":
    unittest.main()
