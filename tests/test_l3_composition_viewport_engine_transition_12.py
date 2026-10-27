import unittest

from tools.build_l3_composition_viewport_engine_transition_12 import build_artifact


class CompositionViewportEngineTransition12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build_artifact()

    def test_popup_chain_is_template_local_and_complete(self):
        focus = self.data["focus"]
        chain = focus["template_local_ancestry_leaf_to_root"]
        self.assertEqual(focus["root_label"], "Board_Pause")
        self.assertEqual([n["transform_path_id"] for n in chain], [425352, 439142])
        self.assertEqual([n["gameobject_path_id"] for n in chain], [57508, 212696])
        self.assertEqual(chain[0]["parent_transform_path_id"], 439142)
        self.assertEqual(chain[1]["parent_transform_path_id"], 0)

    def test_previously_reported_box_gift_parent_is_present(self):
        correction = self.data["prior_block_recheck"]
        chain = correction["transform_chain_leaf_to_root"]
        self.assertEqual(correction["status"], "EARLIER_MISSING_PARENT_CLAIM_CORRECTED")
        self.assertEqual([n["transform_path_id"] for n in chain], [277770, 270123, 339888, 417314, 369060])
        self.assertEqual([n["gameobject_path_id"] for n in chain], [96185, 226561, 62705, 120127, 139738])
        self.assertEqual(chain[-1]["parent_transform_path_id"], 0)

    def test_transition_graph_and_clip_join(self):
        program = self.data["serialized_animator_program"]
        self.assertEqual(program["animator"]["path_id"], 495980)
        self.assertEqual(program["controller"]["identity"]["path_id"], 1974)
        self.assertEqual(program["default_state"]["name_candidates"], ["Appear"])
        self.assertEqual(program["default_state"]["clip"]["path_id"], 1572)
        self.assertEqual(program["hide_state"]["clip"]["path_id"], 1573)
        self.assertEqual(program["any_state_hide_transition"]["destination_index"], 1)
        self.assertEqual(program["any_state_hide_transition"]["conditions"][0]["parameter_names"], ["Hide"])
        self.assertTrue(program["not_a_runtime_trace"])

    def test_curve_samples_are_fp32_model_and_not_readback(self):
        clip = self.data["appear_clip"]
        self.assertEqual(clip["sample_status"], "ARITHMETIC_MODEL_NOT_UNITY_READBACK")
        samples = clip["serialized_curve_probe_samples"]
        self.assertEqual([s["time_seconds"] for s in samples], [0.0, 0.25, 0.5])
        self.assertEqual(samples[0]["local_scale"], [0.0, 0.0, 1.0])
        self.assertEqual(samples[0]["sprite_alpha"], 0.0)
        self.assertEqual(samples[1]["local_scale"], [1.0303999185562134, 1.0303999185562134, 1.0])
        self.assertEqual(samples[1]["sprite_alpha"], 0.8313725590705872)
        self.assertEqual(samples[2]["local_scale"], [1.0, 1.0, 1.0])
        self.assertEqual(samples[2]["sprite_alpha"], 0.8313725590705872)

    def test_viewport_is_explicitly_gated(self):
        viewport = self.data["composition_viewport"]
        self.assertEqual(viewport["status"], "NOT_PROJECTED_TEMPLATE_INSTANCE_AUTHORITY_NOT_ESTABLISHED")
        self.assertIsNone(viewport["pixel_bounds"])
        self.assertFalse(viewport["rendered"])
        self.assertEqual(len(viewport["camera_inventory"]), 5)

    def test_source_pins_are_present(self):
        self.assertEqual(self.data["source_corroboration"]["commit"], "d7e718cfb5466fd7bd03e2d8357400d744b108cb")
        self.assertEqual(len(self.data["source_corroboration"]["pins_sha256_of_git_blob_bytes"]), 8)
        self.assertEqual(len(self.data["inputs_sha256"]), 10)


if __name__ == "__main__":
    unittest.main()
