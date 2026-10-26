import gzip
import hashlib
import json
import unittest
from pathlib import Path

from tools.build_l2_ramus_device_crosscheck_19 import (
    ARTIFACT,
    INPUTS,
    ROOT,
    build_artifact,
)


class RamusDeviceCrosscheck19Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build_artifact()

    def test_map_outer_count_is_measured_but_nested_values_are_not(self):
        crosscheck = self.data["map_nested_array_crosscheck"]
        runtime = crosscheck["runtime_receipt"]
        static = crosscheck["static_source_apk_decoded_values"]
        self.assertEqual(runtime["reported_count"], 250)
        self.assertEqual(runtime["returned_outer_items"], 128)
        self.assertEqual(runtime["returned_placeholder_items"], 128)
        self.assertFalse(runtime["nested_integer_values_read"])
        self.assertEqual(len(static["values"]), 250)
        self.assertTrue(crosscheck["count_comparison"]["outer_length_equal"])
        self.assertIsNone(crosscheck["count_comparison"]["content_equal"])

    def test_arr_depth_recipe_exists_but_was_not_applied_to_receipt(self):
        request = self.data["map_nested_array_crosscheck"]["runtime_receipt"]["arr_depth_request"]
        self.assertEqual((request["arr"], request["depth"]), (256, 2))
        self.assertTrue(request["supported_by_current_bridge_and_collector"])
        self.assertFalse(request["applied_to_archived_phone_receipt"])
        self.assertFalse(self.data["next_measurement"]["available_capture_has_query_receipt"])

    def test_device_static_12_captures_partition_into_10_list_and_2_other_fields(self):
        check = self.data["device_list_crosscheck"]
        cctor = check["static_source_apk_cctor"]
        verdict = check["discrepancy_verdict"]
        self.assertEqual(cctor["initialize_array_captures"], 12)
        self.assertEqual(cctor["captures_appended_to_listStatValues"], 10)
        self.assertEqual(cctor["captures_assigned_to_other_fields"], 2)
        self.assertEqual(len(cctor["list_entries"]), 10)
        self.assertEqual(len(cctor["separate_percent_fields"]), 2)
        self.assertEqual(verdict["actual_static_list_entries"], 10)
        self.assertEqual(verdict["archived_runtime_list_entries"], 10)
        self.assertEqual(
            verdict["resolution"],
            "12_TOTAL_INITIALIZEARRAY_CAPTURES_EQUAL_10_LIST_ENTRIES_PLUS_2_PERCENT_FIELDS",
        )
        self.assertTrue(verdict["not_a_proven_device_count"])

    def test_percent_arrays_match_across_builds_at_float32_precision(self):
        verdict = self.data["device_list_crosscheck"]["discrepancy_verdict"]
        self.assertEqual(
            verdict["percent_arrays_crossbuild_f32_match"],
            {"percentByLevels1": True, "percentByLevels2": True},
        )
        for row in self.data["device_list_crosscheck"]["static_source_apk_cctor"]["separate_percent_fields"]:
            self.assertTrue(row["bitwise_float32_match"])
            self.assertEqual(row["static_values"], row["runtime_values_rounded_to_float32"])

    def test_build_and_device_provenance_are_not_collapsed(self):
        provenance = self.data["apk_provenance"]
        self.assertEqual(provenance["static_source"]["version"], "1.3.118")
        self.assertEqual(provenance["runtime_source"]["reported_version"], "mod 1.0.69 repackaged")
        self.assertNotEqual(provenance["static_source"]["package"], provenance["runtime_source"]["package"])
        policy = self.data["evidence_policy"]
        self.assertFalse(policy["same_build_parity_claimed"])
        self.assertFalse(policy["second_device_parity_claimed"])
        self.assertEqual(
            self.data["status"],
            "PARTIAL_MAP_CONTENTS_NOT_MEASURED_DEVICE_GROUPING_RESOLVED",
        )

    def test_source_pins_cover_inputs_and_builder(self):
        pins = self.data["source_pins"]
        self.assertEqual(pins["builder_sha256"], hashlib.sha256(Path(__file__).parents[1].joinpath("tools/build_l2_ramus_device_crosscheck_19.py").read_bytes()).hexdigest())
        self.assertEqual({row["path"] for row in pins["files"]}, set(INPUTS))
        for row in pins["files"]:
            raw = (ROOT / row["path"]).read_bytes()
            self.assertEqual(row["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(row["bytes"], len(raw))

    def test_gzip_deliverable_matches_recomputed_contract(self):
        with gzip.open(ARTIFACT, "rt", encoding="utf-8") as f:
            persisted = json.load(f)
        self.assertEqual(persisted, self.data)


if __name__ == "__main__":
    unittest.main()
