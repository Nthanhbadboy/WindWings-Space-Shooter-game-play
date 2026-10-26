import unittest

from tools.build_a5_d5_23oct_runtime_crosswalk import build


class A5D523OctRuntimeCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = build()

    def test_health_values_are_captured_not_promoted_to_parity(self):
        runtime = self.receipt["observed_runtime"]
        health = runtime["health"]
        self.assertEqual(2500, health["hud_hp_screenshot_reading"])
        self.assertEqual(2500, health["player_get_datas_start_hp"])
        self.assertEqual("Game", health["scene_state"]["scene"])
        self.assertIn("not asserted as the same instant", health["temporal_qualification"])
        self.assertEqual("CROSS_BUILD_ONLY; no same-build parity witness",
                         self.receipt["capture_identity"]["comparison_boundary"])

    def test_reborn_snapshot_does_not_claim_starting_allowance(self):
        gp = self.receipt["observed_runtime"]["endgame_gp_datas"]
        self.assertTrue(gp["isSummary"])
        self.assertEqual(0, gp["countReborn"])
        self.assertEqual(0, gp["rebornNow"])
        self.assertEqual(-1, gp["maxCountReborn"])
        self.assertEqual([False] * 4, gp["listRebornUseItems"])
        self.assertEqual(3, gp["pvpLife"])
        claims = self.receipt["claim_boundaries"]
        self.assertTrue(claims["initial_free_extra_life_allowance"].startswith("NOT_MEASURED"))
        self.assertIn("not equated with extra lives", claims["pvp_life"])

    def test_entitlement_ownership_and_dps_are_bounded_unknowns(self):
        claims = self.receipt["claim_boundaries"]
        self.assertTrue(claims["new_player_24h_premium_grant"].startswith("NOT_MEASURED"))
        self.assertIn("Player_Controller", claims["health_vs_attack_vs_controller"])
        self.assertIn("MODEL_NOT_MEASURED", claims["dps"])
        self.assertFalse(self.receipt["workflow_replayed"])
        self.assertEqual("modded/repackaged 1.0.69", self.receipt["capture_identity"]["build"])


if __name__ == "__main__":
    unittest.main()
