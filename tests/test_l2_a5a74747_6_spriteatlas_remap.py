import gzip
import json
import unittest

from tools.build_l2_a5a74747_6_spriteatlas_remap import (
    OUTPUT_PATH,
    ROOT,
    build_receipt,
    encode_receipt,
)


class SpriteAtlasRemap6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(gzip.decompress((ROOT / OUTPUT_PATH).read_bytes()))

    def test_deterministic_pinned_builder(self):
        self.assertEqual(encode_receipt(build_receipt()), (ROOT / OUTPUT_PATH).read_bytes())

    def test_inventory_and_static_routes_are_exact(self):
        summary = self.artifact["summary"]
        self.assertEqual(summary["raw_object_counts"], {"Sprite": 2185, "SpriteAtlas": 66, "Texture2D": 654})
        self.assertEqual(summary["sprites"], 2185)
        self.assertEqual(summary["sprite_atlases"], 66)
        self.assertEqual(summary["textures_metadata_only"], 654)
        self.assertEqual(summary["sprites_with_exact_atlas_pointer_and_render_key_join"], 1550)
        self.assertEqual(summary["sprites_using_direct_m_RD_route"], 635)
        self.assertEqual(summary["unresolved_or_ambiguous_sprite_atlas_joins"], 0)

    def test_atlas_maps_and_packed_pointers_are_bijective(self):
        atlases = self.artifact["atlases"]
        mappings = self.artifact["atlas_sprite_mappings"]
        self.assertEqual(len(atlases), 66)
        self.assertEqual(len(mappings), 1550)
        self.assertEqual(sum(row["packed_sprite_count"] for row in atlases), 1550)
        self.assertEqual(sum(row["packed_name_count"] for row in atlases), 1550)
        self.assertEqual(sum(row["render_data_map_count"] for row in atlases), 1550)
        self.assertTrue(all(row["packed_name_order_matches_sprite_pptrs"] for row in atlases))
        self.assertEqual(summary_value(self.artifact, "packed_names_matching_sprite_pointer_order"), 1550)
        sprite_ids = [
            (row["sprite"]["serialized_file"], row["sprite"]["path_id"])
            for row in mappings
        ]
        self.assertEqual(len(set(sprite_ids)), 1550)
        self.assertEqual(self.artifact["summary"]["unique_render_data_keys_across_atlases"], 1550)
        self.assertEqual(self.artifact["summary"]["cross_atlas_duplicate_render_data_keys"], 0)
        self.assertEqual(self.artifact["summary"]["unmatched_atlas_packed_sprite_pointers"], 0)

    def test_every_mapping_retains_exact_key_and_texture_render_metadata(self):
        mappings = self.artifact["atlas_sprite_mappings"]
        for row in mappings:
            self.assertEqual(row["sprite"]["serialized_file"], row["atlas"]["serialized_file"])
            self.assertGreater(row["sprite"]["path_id"], 0)
            self.assertGreater(row["atlas"]["path_id"], 0)
            self.assertEqual(len(row["render_data_key"]), 2)
            self.assertGreaterEqual(row["render_data_map_index"], 0)
            self.assertGreaterEqual(row["packed_sprite_index"], 0)
            resolved = row["resolved_render_data"]
            self.assertEqual(len(resolved["texture"]["dimensions"]), 2)
            self.assertIsNotNone(resolved["texture_rect"])
            self.assertIsNotNone(resolved["uv_transform"])

    def test_static_vertex_bounds_are_identity_joined_and_not_skin_bounds(self):
        rows = self.artifact["sprite_static_bounds_and_skin_metadata"]
        self.assertEqual(len(rows), 2185)
        self.assertEqual(len({(row["identity"]["serialized_file"], row["identity"]["path_id"]) for row in rows}), 2185)
        self.assertTrue(all(row["static_vertex_aabb"]["minimum"] is not None for row in rows))
        self.assertTrue(all(row["static_vertex_aabb"]["maximum"] is not None for row in rows))
        self.assertTrue(all(row["static_vertex_aabb"]["vertex_count"] > 0 for row in rows))
        self.assertTrue(all(row["serialized_submesh_local_aabb_zero"] for row in rows))
        self.assertEqual(self.artifact["summary"]["static_vertex_bounds_rows"], 2185)
        self.assertEqual(self.artifact["summary"]["serialized_submesh_local_aabb_zero_count"], 2185)

    def test_sprite_typetrees_have_no_serialized_bones_or_bindposes_in_scope(self):
        summary = self.artifact["summary"]
        self.assertEqual(summary["serialized_sprite_bone_count_histogram"], {"0": 2185})
        self.assertEqual(summary["serialized_sprite_bindpose_count_histogram"], {"0": 2185})
        self.assertEqual(
            summary["vertex_channel_layout_histogram"],
            {json.dumps({
                "active_channel_indices": [0, 4],
                "active_channel_descriptors": [
                    {"stream": 0, "offset": 0, "format": 0, "dimension": 3},
                    {"stream": 1, "offset": 0, "format": 0, "dimension": 2},
                ],
            }, ensure_ascii=False, sort_keys=True, separators=(",", ":")): 2185},
        )

    def test_runtime_remap_and_deformation_remain_unobserved(self):
        artifact = self.artifact
        self.assertEqual(artifact["status"], "BOUNDED_STATIC_ATLAS_MAP_AND_SPRITE_VERTEX_BOUNDS_RUNTIME_REMAP_NOT_OBSERVED")
        boundary = artifact["runtime_boundary"]
        self.assertEqual(boundary["runtime_atlas_request_or_registration"], "NOT_OBSERVED")
        api = artifact["source_provenance"]["il2cpp_api_dump"]
        self.assertEqual(api["game_subscription_or_invocation"], "NOT_OBSERVED")
        self.assertTrue(api["unity_api_declares_atlas_requested"])
        self.assertTrue(api["unity_api_declares_atlas_registered"])
        self.assertIn("does not prove", boundary["UnityEngine.U2D.SpriteAtlasManager_api"])
        self.assertIn("No rendered, runtime-deformed", " ".join(artifact["evidence_boundary"]))

    def test_raw_inputs_and_derived_mesh_contract_are_pinned(self):
        provenance = self.artifact["source_provenance"]
        raw = provenance["raw_geometry_snapshot"]
        self.assertEqual(raw["index_sha256"], "29b074baac8946033b1abc1542b945bdbd601524475e6deca1a23d06a3fe5531")
        self.assertEqual(raw["snapshot_commit"], "72041a1d400be6b0972f5bfa9868efe3befaeca7")
        self.assertEqual(len(raw["shards"]), 6)
        self.assertEqual(sum(shard["rows"] for shard in raw["shards"]), 2905)
        self.assertEqual(provenance["mesh_contract"]["compressed_sha256"],
                         "90fc5252b3e8416686c0788aa7bae50b3bb4c9b5382887d39e14bd93023eaffa")
        self.assertEqual(provenance["il2cpp_api_dump"]["compressed_sha256"],
                         "e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454")

    def test_no_gameplay_or_global_absence_claim(self):
        limits = " ".join(self.artifact["evidence_boundary"])
        self.assertIn("does not establish a live/runtime SpriteAtlasManager request", limits)
        self.assertIn("does not rule out other component types", limits)
        self.assertIn("No rendered, runtime-deformed", limits)


def summary_value(artifact, key):
    return artifact["summary"][key]


if __name__ == "__main__":
    unittest.main()
