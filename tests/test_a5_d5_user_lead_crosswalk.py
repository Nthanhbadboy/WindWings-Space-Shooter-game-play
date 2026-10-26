import unittest

from tools.build_a5_d5_user_lead_crosswalk import build


class D5UserLeadCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = build()

    def test_catalog_roster_is_separate_from_component_identity(self):
        records = self.receipt["serialized_records"]["data_players_records"]
        ships = next(row for row in records if row["name"] == "Data_Players")
        self.assertEqual(25, ships["entry_count"])
        self.assertEqual(list(range(10001, 10025)) + [10999], ships["ids"])
        self.assertEqual(24, self.receipt["identity_and_ownership_boundary"]["player_attack_class_identities"])
        self.assertIn("NOT_ASSERTED", self.receipt["identity_and_ownership_boundary"]["player_attack_to_data_players_id_join"])

    def test_upgrade_ui_is_not_health_or_controller_owner(self):
        board = self.receipt["serialized_records"]["board_players"]
        refs = board["serialized_button_refs"]
        self.assertEqual(237122, refs["btnUpgradeByCoins"]["m_PathID"])
        self.assertEqual(237118, refs["btnUpgradeByGems"]["m_PathID"])
        self.assertIn("not evidence", board["interpretation"])
        self.assertEqual("NOT_BOUND_WITHIN_CAPTURED_EXPORTS", self.receipt["identity_and_ownership_boundary"]["health_owner_or_controller_owner"])

    def test_premium_and_free_life_claims_remain_bounded(self):
        claims = self.receipt["claims"]
        self.assertIn("NOT_BOUND", claims["initial_24h_premium"])
        self.assertIn("NOT_BOUND", claims["initial_extra_life_count_without_ad_or_gems"])
        self.assertIn("forever", " ".join(self.receipt["serialized_records"]["iap_product_catalog"]["selected_ids"]))

    def test_receipt_is_static_only(self):
        self.assertFalse(self.receipt["runtime_or_dps_measured"])
        self.assertEqual(126, self.receipt["pinned_export_sets"]["scriptableobject_csv"]["count"])
        self.assertEqual(140, self.receipt["pinned_export_sets"]["typetree_jsonl"]["count"])


if __name__ == "__main__":
    unittest.main()
