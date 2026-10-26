import unittest

from tools.build_a5_h1_map_wave_inline import build


class A5H1MapWaveInlineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = build()

    def test_table_is_exactly_250_ordered_entries(self):
        entries = self.receipt["entries"]
        self.assertEqual(len(entries), 250)
        self.assertEqual([row["table_index"] for row in entries], list(range(250)))
        self.assertEqual(
            [row["values"] for row in entries[:3]],
            [[25, 9010], [164], [113, 5]],
        )

    def test_payload_source_split_and_prior_full_table_match(self):
        method = self.receipt["method"]
        self.assertEqual(method["initialize_array_count"], 243)
        self.assertEqual(method["literal_array_count"], 7)
        self.assertEqual(method["array_count"], 250)
        self.assertEqual(self.receipt["crosscheck"]["prior_local_maps_artifact"]["entries_matched"], 250)
        self.assertEqual(self.receipt["crosscheck"]["prior_local_maps_artifact"]["mismatches"], 0)

    def test_legacy_candidate_is_explicitly_superseded_not_silently_used(self):
        legacy = self.receipt["crosscheck"]["superseded_legacy_candidate"]
        self.assertEqual(legacy["entries_compared"], 250)
        self.assertEqual(legacy["mismatches"], 242)
        self.assertEqual(legacy["first_mismatches"][0]["table_index"], 4)
        self.assertEqual(legacy["first_mismatches"][0]["extracted"], [95, 11, 7008])

    def test_static_scope_boundary_is_present(self):
        self.assertEqual(self.receipt["status"], "STATIC_ONLY_EXTRACTED_LISTMAPDATAS_NOT_RUNTIME_PARITY")
        self.assertTrue(any("runtime" in limit.lower() for limit in self.receipt["limitations"]))
        self.assertEqual(self.receipt["table_field_static_offset"], "0x28")


if __name__ == "__main__":
    unittest.main()
