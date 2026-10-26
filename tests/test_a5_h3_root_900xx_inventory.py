import unittest

from tools.build_a5_h3_root_900xx_inventory import build_receipt


class A5H3Root900xxInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = build_receipt()

    def test_exact_roots_are_complete_metadata_records_outside_roster(self):
        summary = self.receipt["summary"]
        records = self.receipt["records"]
        self.assertEqual(summary["prefab_root_records"], 2081)
        self.assertEqual(summary["waves_roster_unique_names"], 109)
        self.assertEqual(summary["exact_five_digit_900xx_roots"], 45)
        self.assertEqual(summary["exact_names_outside_roster"], 45)
        self.assertEqual(summary["exact_roster_matches"], 0)
        self.assertEqual(summary["root_metadata_records_present"], 45)
        self.assertEqual(summary["bounded_missing_root_metadata"], 0)
        self.assertEqual(len(records), 45)
        self.assertEqual(len({row["root_name"] for row in records}), 45)
        self.assertTrue(all(row["metadata_identity_status"] == "ROOT_RECORD_PRESENT" for row in records))
        self.assertTrue(all(row["waves_roster_exact_name_match"] is False for row in records))

    def test_prefix_only_roots_are_not_miscounted_as_five_digit_ids(self):
        summary = self.receipt["summary"]
        self.assertEqual(summary["900xx_prefix_roots"], 48)
        self.assertEqual(summary["non_exact_prefix_exclusions"], 3)
        self.assertEqual(
            [row["root_name"] for row in self.receipt["prefix_only_exclusions"]],
            ["90030 [Quest_Notice]", "90036-Lasers", "90053-Laser"],
        )

    def test_metadata_ids_are_present_and_roles_remain_unassigned(self):
        records = self.receipt["records"]
        self.assertTrue(all(row["gameobject_path_id"] > 0 for row in records))
        self.assertTrue(all(row["transform_path_id"] > 0 for row in records))
        self.assertTrue(all(row["serialized_child_count"] >= 0 for row in records))
        self.assertTrue(all(row["asset_role"] == "NOT_ASSIGNED" for row in records))
        self.assertEqual(self.receipt["evidence_level"], "B")
        self.assertEqual(self.receipt["evidence_scope"], "STATIC_SERIALIZED_METADATA_ONLY")

    def test_exact_inventory_has_stable_child_count_distribution(self):
        self.assertEqual(
            self.receipt["summary"]["children_distribution"],
            [
                {"children": 0, "roots": 6},
                {"children": 1, "roots": 20},
                {"children": 2, "roots": 12},
                {"children": 3, "roots": 5},
                {"children": 4, "roots": 2},
            ],
        )


if __name__ == "__main__":
    unittest.main()
