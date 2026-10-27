import copy
import gzip
import json
import unittest

from tools.build_l2_a5a74747_28_static_map_crosscheck import (
    OUTPUT_PATH,
    ROOT,
    build_receipt,
    encode_receipt,
    read_inputs,
)


class StaticMapCrosscheck28Tests(unittest.TestCase):
    def artifact(self):
        return json.loads(gzip.decompress((ROOT / OUTPUT_PATH).read_bytes()))

    def test_deterministic_static_builder(self):
        receipt = build_receipt(*read_inputs())
        self.assertEqual(encode_receipt(receipt), (ROOT / OUTPUT_PATH).read_bytes())

    def test_fallback_is_explicitly_not_runtime(self):
        artifact = self.artifact()
        self.assertEqual(artifact["status"], "STATIC_CROSSCHECK_NOT_RUNTIME")
        self.assertEqual(artifact["task"]["runtime_readback"], "NOT_OBSERVED")
        self.assertFalse(artifact["task"]["session_started"])
        self.assertFalse(artifact["task"]["source_apk_modified"])
        self.assertEqual(artifact["task"]["requested_runtime_parameters"], {"arr": 256, "depth": 2})
        self.assertNotIn("runtime_values", artifact)

    def test_all_250_values_match_both_local_static_candidates(self):
        artifact = self.artifact()
        crosscheck = artifact["crosscheck"]
        self.assertEqual(crosscheck["peer_constructor_entries"], 250)
        self.assertEqual(crosscheck["local_maps_json_entries"], 250)
        self.assertEqual(crosscheck["local_segment35_entries"], 250)
        self.assertEqual(crosscheck["value_rows_compared"], 250)
        self.assertEqual(crosscheck["value_mismatch_count"], 0)
        self.assertEqual(crosscheck["all_rows_match"], True)
        self.assertTrue(all(row["matches_previous_maps_json"] for row in crosscheck["comparison_rows"]))
        self.assertTrue(all(row["matches_previous_segment35"] for row in crosscheck["comparison_rows"]))

    def test_constructor_source_coverage_and_static_value_counts(self):
        crosscheck = self.artifact()["crosscheck"]
        self.assertEqual(crosscheck["peer_initialize_array_rows"], 243)
        self.assertEqual(crosscheck["peer_inline_literal_rows"], 7)
        self.assertEqual(crosscheck["total_integer_values"], 742)
        self.assertEqual(
            sum(int(length) * count for length, count in crosscheck["length_distribution"].items()),
            742,
        )
        rows = crosscheck["comparison_rows"]
        self.assertEqual(sum(row["source"] == "InitializeArray" for row in rows), 243)
        self.assertEqual(sum(row["source"] == "inline-immediate" for row in rows), 7)
        self.assertEqual(rows[0]["values"], [25, 9010])
        self.assertEqual(rows[1]["values"], [164])
        self.assertEqual(rows[-1]["values"], [43, 12, 9024])

    def test_peer_replication_and_source_pins_are_carried(self):
        provenance = self.artifact()["provenance"]
        self.assertTrue(provenance["replication"])
        self.assertEqual(provenance["peer_commit"], "706c704e6024b831097a2b53a1d5332e588e30b6")
        self.assertEqual(
            provenance["source_xapk_sha256"],
            "f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e",
        )
        self.assertEqual(
            provenance["peer_report_sha256"],
            "a1100c0502f33717e03ed36c4396d3ed7410dcf9ab80e3c92f0447a4f7ff1424",
        )
        self.assertEqual(
            provenance["source_lib_sha256"],
            "9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99",
        )
        self.assertEqual(provenance["static_field_offset"], "0x28")
        self.assertEqual(provenance["map_index_interpretation"], "zero-based constructor order; UI numbering not verified")
        self.assertEqual(len(provenance["local_sources"]), 2)

    def test_mutated_local_values_fail_closed(self):
        peer, maps, segments, hashes = read_inputs()
        maps = copy.deepcopy(maps)
        maps["maps"][42][0] += 1
        with self.assertRaisesRegex(ValueError, "prior datas/maps.json values differ at index 42"):
            build_receipt(peer, maps, segments, hashes)

    def test_mutated_initializer_identity_fails_closed(self):
        peer, maps, segments, hashes = read_inputs()
        segments = copy.deepcopy(segments)
        seg35 = next(segment for segment in segments["segments"] if segment["index"] == 35)
        seg35["arrays"][4]["field"] = "tampered"
        with self.assertRaisesRegex(ValueError, "initializer field differs at index 4"):
            build_receipt(peer, maps, segments, hashes)


if __name__ == "__main__":
    unittest.main()
