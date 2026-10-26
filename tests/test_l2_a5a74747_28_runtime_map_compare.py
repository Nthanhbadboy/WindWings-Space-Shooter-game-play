import unittest

from tools.compare_l2_a5a74747_28_runtime_map import compare, expected_rows


class RuntimeMapComparisonTests(unittest.TestCase):
    def synthetic_response(self):
        rows = expected_rows()
        return {
            "ok": True,
            "type": "Map_Get_Datas",
            "fields": {
                "listMapDatas": rows,
                "listMapDatas_count": len(rows),
            },
        }

    def test_synthetic_fixture_roundtrip_checks_all_742_values(self):
        # Synthetic test input only; this is not a device/session receipt.
        result = compare(self.synthetic_response())
        self.assertEqual(result["status"], "RUNTIME_READBACK_MATCHES_STATIC")
        self.assertEqual(result["rows_compared"], 250)
        self.assertEqual(result["values_compared"], 742)
        self.assertEqual(result["value_mismatch_count"], 0)

    def test_detects_one_changed_value(self):
        response = self.synthetic_response()
        response["fields"]["listMapDatas"][0][0] += 1
        result = compare(response)
        self.assertEqual(result["status"], "RUNTIME_READBACK_MISMATCH")
        self.assertEqual(result["value_mismatch_count"], 1)
        self.assertEqual(result["mismatches"][0]["row"], 0)
        self.assertEqual(result["mismatches"][0]["offset"], 0)

    def test_rejects_missing_runtime_field_without_inventing_values(self):
        response = {"ok": True, "type": "Map_Get_Datas", "fields": {}}
        with self.assertRaisesRegex(ValueError, "listMapDatas is missing"):
            compare(response)

    def test_rejects_partial_row_count(self):
        response = self.synthetic_response()
        response["fields"]["listMapDatas"].pop()
        with self.assertRaisesRegex(ValueError, "outer row count"):
            compare(response)

    def test_rejects_truncated_row_values(self):
        response = self.synthetic_response()
        response["fields"]["listMapDatas"][0].pop()
        result = compare(response)
        self.assertEqual(result["status"], "RUNTIME_READBACK_INCOMPLETE")
        self.assertFalse(result["all_rows_match"])
        self.assertEqual(result["mismatches"][0]["kind"], "length")

    def test_rejects_non_integral_readback(self):
        response = self.synthetic_response()
        response["fields"]["listMapDatas"][0][0] = 25.5
        with self.assertRaisesRegex(ValueError, "finite integral value"):
            compare(response)


if __name__ == "__main__":
    unittest.main()
