from __future__ import annotations

import gzip
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools import build_l3_sliced_tiled_geometry_5 as builder

ROOT = Path(__file__).resolve().parents[1]


class SlicedTiledGeometry5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(gzip.decompress((ROOT / "datas/l3_a5a74747_5_sliced_tiled_geometry.json.gz").read_bytes()))

    def test_builder_is_byte_deterministic(self) -> None:
        expected = builder.build_file(check=False)
        self.assertEqual(expected, (ROOT / "datas/l3_a5a74747_5_sliced_tiled_geometry.json.gz").read_bytes())
        self.assertEqual(expected, builder.build_file(check=False))
        self.assertEqual(expected, builder.build_file(check=True))

    def test_source_sha_pins_bind_peer_and_original_apk_inputs(self) -> None:
        data = self.data
        self.assertEqual(data["replication"]["label"], "REPLICATION")
        self.assertEqual(data["replication"]["source_branch"], builder.PEER_BRANCH)
        self.assertEqual(data["replication"]["source_commit"], builder.PEER_COMMIT)
        self.assertEqual(data["source_pins"], builder.PINS)
        self.assertEqual(data["source_content_pins"], builder.CONTENT_PINS)
        self.assertEqual(data["replication"]["source_identity_sha256"], builder.APK_INPUTS)

    def test_scene_drawmode_and_border_counts_are_recomputed(self) -> None:
        summary = self.data["summary"]
        self.assertEqual(summary["source_scene_sprite_renderers"], 1377)
        self.assertEqual(summary["draw_mode_code_counts"], {"0": 922, "1": 441, "2": 14})
        self.assertEqual(summary["sliced_nonzero_border_instances"], 236)
        self.assertEqual(summary["tiled_nonzero_border_instances"], 0)
        self.assertEqual(summary["direct_unpacked_nonzero_border_sliced_modelled"], 112)
        self.assertEqual(summary["direct_unpacked_borderless_tiled_modelled"], 10)

    def test_sliced_shopborder_sample_uses_serialized_border_not_a_quad(self) -> None:
        rows = self.data["outputs"]["sliced"]
        row = next(r for r in rows if r["renderer"]["serialized_file"] == "data.unity3d/level2" and r["renderer"]["path_id"] == 5046)
        self.assertEqual(row["sprite_name"], "ShopBorder")
        self.assertEqual(row["source"]["border_xyzw"], [20.0, 20.0, 20.0, 20.0])
        self.assertEqual(row["grid"], {"columns": 3, "rows": 3, "vertices": 16, "quads": 9, "triangles": 18})
        self.assertEqual(len(row["vertices"]), 16)
        self.assertEqual(len(row["triangle_indices"]), 54)
        self.assertEqual(row["triangle_indices"][:6], [0, 1, 4, 4, 1, 5])
        self.assertAlmostEqual(row["vertices"][0]["position"][0], -1.36)
        self.assertAlmostEqual(row["vertices"][1]["position"][0], -1.16)
        self.assertAlmostEqual(row["vertices"][2]["position"][0], 1.16)
        self.assertAlmostEqual(row["vertices"][4]["position"][1], -0.2)
        self.assertAlmostEqual(row["vertices"][8]["position"][1], -2.52)
        self.assertAlmostEqual(row["vertices"][1]["uv"][0], 20.0 / 128.0)
        self.assertEqual(row["classification"], "MODEL_NOT_NATIVE_RENDERER_READBACK")

    def test_all_sliced_models_preserve_bounds_uv_and_topology_invariants(self) -> None:
        for row in self.data["outputs"]["sliced"]:
            self.assertEqual(len(row["vertices"]), 16, row["renderer"])
            self.assertEqual(len(row["triangle_indices"]), 54, row["renderer"])
            self.assertEqual(min(row["triangle_indices"]), 0, row["renderer"])
            self.assertEqual(max(row["triangle_indices"]), 15, row["renderer"])
            xlo, ylo, xhi, yhi = row["metrics"]["local_bounds_xy"]
            self.assertAlmostEqual(xhi - xlo, row["requested_size"]["x"], places=7)
            self.assertAlmostEqual(yhi - ylo, row["requested_size"]["y"], places=7)
            self.assertLessEqual(row["metrics"]["triangle_signed_area_max"], 1e-9)
            u0, v0 = row["metrics"]["uv_u_left_to_right"][0], row["metrics"]["uv_v_top_to_bottom"][-1]
            u1, v1 = row["metrics"]["uv_u_left_to_right"][-1], row["metrics"]["uv_v_top_to_bottom"][0]
            for vertex in row["vertices"]:
                self.assertGreaterEqual(vertex["uv"][0] + 1e-9, u0)
                self.assertLessEqual(vertex["uv"][0], u1 + 1e-9)
                self.assertGreaterEqual(vertex["uv"][1] + 1e-9, v0)
                self.assertLessEqual(vertex["uv"][1], v1 + 1e-9)

    def test_tiled_direct_rows_are_borderless_partial_tile_models(self) -> None:
        self.assertEqual(len(self.data["outputs"]["tiled"]), 10)
        for row in self.data["outputs"]["tiled"]:
            self.assertEqual(row["source"]["border_xyzw"], [0.0, 0.0, 0.0, 0.0])
            self.assertEqual(row["grid"]["quads"], 1)
            self.assertEqual(row["grid"]["vertices"], 4)
            self.assertEqual(row["grid"]["triangles"], 2)
            self.assertEqual(len(row["triangle_indices"]), 6)
            self.assertIn("not native enum behavior", row["policy"])
        star = next(r for r in self.data["outputs"]["tiled"] if r["renderer"]["path_id"] == 1825)
        self.assertEqual(star["sprite_name"], "PlayerStar")
        self.assertAlmostEqual(star["tiles"][0]["uv_fraction_xy"][0], 0.81 / 1.28)
        self.assertAlmostEqual(star["tiles"][0]["uv_fraction_xy"][1], 0.76 / 1.28)

    def test_exclusions_are_explicit_and_no_undersize_rule_is_guessed(self) -> None:
        excluded = self.data["outputs"]["excluded"]
        reasons = {row["reason"] for row in excluded}
        self.assertIn("packed_or_atlas_route_outside_direct-texture-model", reasons)
        self.assertIn("packed_or_atlas_route_outside_direct-tile-model", reasons)
        self.assertIn("zero_border_sliced_instance_outside_primary_nonzero-border-case", reasons)
        undersized = [row for row in excluded if row["reason"] == "requested_size_below_fixed_border_sum_no_shrink_policy_assumed"]
        self.assertEqual(len(undersized), 1)
        self.assertEqual(undersized[0]["renderer"]["path_id"], 82)
        self.assertEqual(self.data["summary"]["excluded_instances"], len(excluded))

    def test_model_limits_do_not_claim_native_or_render_parity(self) -> None:
        limits = "\n".join(self.data["limits"])
        self.assertIn("not a native SpriteRenderer implementation", limits)
        self.assertIn("No SpriteRenderer generated-mesh runtime readback", limits)
        self.assertIn("not verified native method semantics", limits)
        self.assertIn("Atlas-backed", limits)
        self.assertEqual(self.data["status"], "BOUNDED_STATIC_REPLICATION_MODEL_NOT_NATIVE_GENERATOR_OR_RUNTIME")

    def test_tampered_input_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp_root = Path(directory)
            for relative in builder.PINS:
                target = temp_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)
            first = next(iter(builder.PINS))
            target = temp_root / first
            target.write_bytes(target.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "source SHA mismatch"):
                builder.build(root=temp_root)


if __name__ == "__main__":
    unittest.main()
