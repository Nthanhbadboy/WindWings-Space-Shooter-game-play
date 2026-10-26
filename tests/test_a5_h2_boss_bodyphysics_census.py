import unittest

from tools.build_a5_h2_boss_bodyphysics_census import build_receipt


class A5H2BossBodyPhysicsCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = build_receipt()

    def test_census_and_serialized_source_join_are_complete(self):
        crosschecks = self.receipt["crosschecks"]
        self.assertEqual(crosschecks["component_csv_rows"], 251)
        self.assertEqual(crosschecks["typetree_records"], 251)
        self.assertEqual(crosschecks["serialized_prefab_join_rows"], 251)
        self.assertTrue(crosschecks["csv_typetree_path_id_sets_equal"])
        self.assertTrue(crosschecks["csv_prefab_join_path_id_sets_equal"])
        self.assertEqual(crosschecks["rows_matching_all_serialized_fields"], 251)
        self.assertEqual(len(self.receipt["records"]), 251)

    def test_value_distributions_are_exact_and_sum_to_census(self):
        summary = self.receipt["summary"]
        self.assertEqual(summary["distinct_dmgFirst_values"], 15)
        self.assertEqual(summary["dmgFirst_min"], 0)
        self.assertEqual(summary["dmgFirst_median"], 500)
        self.assertEqual(summary["dmgFirst_max"], 9_000_000)
        self.assertEqual(summary["distinct_dmgPerSec_values"], 16)
        self.assertEqual(summary["dmgPerSec_min"], 5)
        self.assertEqual(summary["dmgPerSec_median"], 50)
        self.assertEqual(summary["dmgPerSec_max"], 1_000)
        self.assertEqual(sum(item["count"] for item in summary["dmgFirst_distribution"]), 251)
        self.assertEqual(sum(item["count"] for item in summary["dmgPerSec_distribution"]), 251)
        self.assertEqual(sum(item["count"] for item in summary["value_pair_distribution"]), 251)

    def test_serialized_root_metadata_is_not_promoted_to_director_class_identity(self):
        summary = self.receipt["summary"]
        self.assertEqual(summary["distinct_prefab_root_labels"], 61)
        self.assertEqual(self.receipt["requested_boss_damage_class_count"], 19)
        self.assertEqual(self.receipt["boss_damage_class_assignment_status"], "NOT_BOUND")
        self.assertEqual(self.receipt["boss_damage_classes_assigned"], 0)
        self.assertEqual(self.receipt["unassigned_component_instances"], 251)
        self.assertEqual(self.receipt["evidence_level"], "B")
        self.assertFalse(self.receipt["assembly_available"])
        self.assertEqual(self.receipt["semantics_status"], "NOT_BOUND")

    def test_flags_and_layer_mask_remain_serialized_facts(self):
        summary = self.receipt["summary"]
        self.assertEqual(summary["isTrigger_true"], 249)
        self.assertEqual(summary["isTrigger_false"], 2)
        self.assertEqual(summary["isFirstTrigger_true"], 110)
        self.assertEqual(summary["isFirstTrigger_false"], 141)
        self.assertEqual(summary["layerMask_m_Mask_distribution"], [{"value": 256, "count": 251}])
        self.assertEqual(summary["m_Enabled_distribution"], [{"value": 1, "count": 251}])


if __name__ == "__main__":
    unittest.main()
