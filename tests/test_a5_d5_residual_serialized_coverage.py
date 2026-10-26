import unittest

from tools.build_a5_d5_residual_serialized_coverage import build_receipt


class A5D5ResidualSerializedCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = build_receipt()

    def test_pinned_export_surface_and_class_identity_boundary(self):
        sources = self.receipt["sources"]
        self.assertEqual(sources["scriptableobject_csv_set"]["count"], 126)
        self.assertEqual(sources["serialized_typetree_jsonl_set"]["count"], 140)
        self.assertEqual(self.receipt["export_coverage"]["typetree_jsonl_records_scanned"], 231957)
        identity = self.receipt["class_inventory_boundary"]
        self.assertEqual(identity["player_attack_class_identities"], 24)
        self.assertTrue(identity["player_health_class_identity_present"])
        self.assertTrue(identity["player_controller_class_identity_present"])
        self.assertEqual(identity["warning"], "class-inventory identities/counts are not serialized owner records")

    def test_player_owner_exports_and_exact_reborn_keys_are_not_in_this_snapshot(self):
        coverage = self.receipt["export_coverage"]
        self.assertEqual(coverage["player_target_csv_files"], [])
        self.assertEqual(coverage["player_target_typetree_files"], [])
        self.assertEqual(coverage["gp_datas_csv_rows"], 1)
        self.assertEqual(coverage["gp_datas_typetree_rows"], 1)
        self.assertEqual(coverage["exact_extra_life_csv_header_hits"], [])
        self.assertEqual(coverage["exact_extra_life_typetree_key_hits"], [])
        self.assertEqual(self.receipt["gp_datas_cross_export_consistency"]["extra_life_serialized_rewire"], "NOT_BOUND")

    def test_path_id_2625_does_not_create_an_owner_join(self):
        boundary = self.receipt["gp_datas_pointer_boundary"]
        self.assertEqual(boundary["player_pointer"], {"file_id": 0, "path_id": 2625})
        self.assertEqual(boundary["owner_join"], "NOT_BOUND_WITHIN_CAPTURED_EXPORTS")
        self.assertEqual(boundary["scriptableobject_csv_pptr_edges_to_path_id_2625"], [{
            "file": "reverse-engineering/scriptableobjects/GP_Datas.csv",
            "row_path_id": 6767,
            "row_gameobject": "GP_Manager",
            "field": "player.m_PathID",
            "file_id": 0,
            "path_id": 2625,
        }])
        self.assertEqual(boundary["typetree_jsonl_pptr_edges_to_path_id_2625"], [
            {
                "file": "reverse-engineering/raw/typetrees/GP_Datas.jsonl.gz",
                "row_path_id": 6767,
                "row_gameobject": "GP_Manager",
                "field": "player",
                "file_id": 0,
                "path_id": 2625,
            },
            {
                "file": "reverse-engineering/raw/typetrees/GP_Tutorials.jsonl.gz",
                "row_path_id": 7123,
                "row_gameobject": "GP_Tutorials",
                "field": "player",
                "file_id": 0,
                "path_id": 2625,
            },
        ])
        self.assertEqual(boundary["export_rows_whose_own_path_id_is_2625"][0]["file"], "reverse-engineering/scriptableobjects/Box_Rewards.csv")
        self.assertEqual(boundary["typetree_rows_whose_own_path_id_is_2625"][0]["file"], "reverse-engineering/raw/typetrees/Box_Rewards.jsonl.gz")

    def test_gp_datas_flat_csv_and_typetree_difference_is_reported_not_interpreted(self):
        consistency = self.receipt["gp_datas_cross_export_consistency"]
        self.assertEqual(consistency["row_identity"], {"path_id": 6767, "gameobject": "GP_Manager"})
        self.assertEqual(consistency["flat_csv_vs_typetree_field_differences"], [{
            "field": "listActiveEnemies",
            "csv_value": [0],
            "typetree_value": [],
        }])
        self.assertFalse(self.receipt["runtime_or_dps_measured"])
        self.assertEqual(self.receipt["evidence_scope"], "CAPTURED_SCRIPTABLEOBJECT_CSV_AND_SERIALIZED_TYPETREE_JSONL_ONLY")


if __name__ == "__main__":
    unittest.main()
