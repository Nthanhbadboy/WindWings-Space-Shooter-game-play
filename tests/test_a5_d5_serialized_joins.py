import unittest

from tools.build_a5_d5_serialized_joins import build_receipt


class A5D5SerializedJoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = build_receipt()

    def test_24_class_suffixes_join_to_24_static_array_indices(self):
        join = self.receipt["class_to_array_join"]
        rows = join["records"]
        self.assertEqual(join["implementation_classes"], 24)
        self.assertEqual(join["static_array_rows"], 24)
        self.assertEqual(join["joined_rows"], 24)
        self.assertEqual([row["implementation_class"] for row in rows], [f"Player_Attack_{i}" for i in range(1, 25)])
        self.assertEqual([row["static_array_index"] for row in rows], list(range(24)))
        self.assertEqual(rows[0]["static_array_values"], {
            "PlayerCosts": 0,
            "StartMainCannonDamages": 4500.0,
            "StartMainCannonRate": 4.8,
            "StartWingCannonDamages": 218.0,
        })
        self.assertEqual(rows[-1]["static_array_values"]["StartMainCannonDamages"], 3300.0)

    def test_join_is_explicitly_not_a_component_owner_or_runtime_join(self):
        self.assertEqual(self.receipt["status"], "PARTIAL_STATIC_CLASS_TO_ARRAY_JOIN_NOT_COMPONENT_OR_LIFECYCLE_CLOSURE")
        self.assertEqual(self.receipt["evidence_scope"], "STATIC_RECEIPTS_AND_SERIALIZED_CSV_ONLY")
        self.assertFalse(self.receipt["runtime_or_dps_measured"])
        self.assertTrue(all(row["serialized_component_owner"] == "NOT_BOUND" for row in self.receipt["class_to_array_join"]["records"]))

    def test_gp_datas_export_is_bounded_and_has_no_checked_extra_life_columns(self):
        boundary = self.receipt["serialized_component_boundary"]
        self.assertEqual(boundary["gp_datas_serialized_rows"], 1)
        self.assertEqual(boundary["gp_datas_path_id"], 6767)
        self.assertEqual(boundary["gp_datas_gameobject_path_id"], 404)
        self.assertEqual(boundary["gp_datas_player_path_id"], 2625)
        self.assertEqual(boundary["player_attack_class_exports_in_scriptableobject_csv"], [])
        self.assertEqual(boundary["player_attack_class_exports_in_typetree"], [])
        self.assertEqual(
            boundary["extra_life_field_names_absent_from_gp_datas_export"],
            ["countReborn", "rebornNow", "maxCountReborn", "listRebornUseItems"],
        )
        self.assertEqual(boundary["extra_life_serialized_rewire"], "NOT_BOUND_FROM_AVAILABLE_SERIALIZED_EXPORTS")

    def test_reported_limitations_do_not_promote_static_values_to_dps(self):
        self.assertTrue(any("DPS" in item or "runtime" in item for item in self.receipt["limitations"]))
        self.assertEqual(self.receipt["evidence_level"], "B")
        self.assertEqual(self.receipt["serialized_component_boundary"]["player_component_owner_join"], "NOT_BOUND")


if __name__ == "__main__":
    unittest.main()
