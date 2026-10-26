import unittest

from tools.build_a5_d5_23oct_runtime_crosswalk import build


class A5D523OctRuntimeCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = build()
        cls.runtime = cls.receipt["observed_runtime"]
        cls.snapshots = {
            item["source"].rsplit("/", 1)[-1]: item
            for item in cls.runtime["gp_runtime_snapshots"]
        }

    def test_full_capture_folder_is_pinned(self):
        inventory = self.receipt["capture_folder_inventory"]
        self.assertEqual(84, inventory["file_count"])
        self.assertEqual(43, inventory["extensions"][".json"])
        self.assertEqual(35, inventory["extensions"][".png"])
        self.assertEqual(84, len(inventory["files"]))
        self.assertFalse(self.receipt["workflow_replayed"])

    def test_health_values_are_captured_not_promoted_to_parity(self):
        health = self.runtime["health"]
        self.assertEqual(2500, health["hud_hp_visual_reading"])
        self.assertEqual(2500, health["player_get_datas_start_hp"])
        self.assertEqual(3, len(health["screenshot_sources"]))
        self.assertEqual("Game", health["scene_state"]["scene"])
        self.assertIn("not joined", health["temporal_qualification"])
        self.assertEqual(
            "CROSS_BUILD_ONLY; no same-build parity witness",
            self.receipt["capture_identity"]["comparison_boundary"],
        )

    def test_premium_and_first_revival_copy_are_ui_evidence_only(self):
        premium = self.runtime["premium_ui"]
        text = premium["transcribed_visible_text"]
        self.assertIn("Congratulations on being a member of Premium FOREVER", text)
        self.assertIn("FREE first revival.", text)
        self.assertEqual(8, len(premium["screenshots"]))
        self.assertEqual(71581, premium["background_top_bar_readings"]["coins"])
        self.assertTrue(self.runtime["endgame_hierarchy"]["active"])
        claims = self.receipt["claim_boundaries"]
        self.assertTrue(claims["new_player_24h_premium_grant"].startswith("NOT_MEASURED"))
        self.assertTrue(claims["free_first_revival_benefit"].startswith("UI_ADVERTISED"))
        self.assertTrue(self.runtime["account_context"]["fresh_account_or_first_launch_proven"] is False)

    def test_reborn_snapshots_keep_missing_fields_and_duplicate_payloads_distinct(self):
        self.assertEqual(7, len(self.snapshots))
        boss = self.snapshots["boss_boss_gp.json"]["fields"]
        self.assertTrue(boss["isSummary"])
        self.assertEqual(0, boss["countReborn"])
        self.assertEqual(0, boss["rebornNow"])
        self.assertEqual(-1, boss["maxCountReborn"])
        self.assertEqual([False] * 4, boss["listRebornUseItems"])
        self.assertEqual(3, boss["pvpLife"])
        live2 = self.snapshots["live_2_gp.json"]
        self.assertNotIn("rebornNow", live2["field_presence"])
        self.assertNotIn("maxCountReborn", live2["field_presence"])
        self.assertEqual(4, len(self.runtime["byte_identical_gp_snapshot_groups"][0]["files"]))
        claims = self.receipt["claim_boundaries"]
        self.assertTrue(claims["captured_reborn_activity"].startswith("NO_REBORN_RECORDED"))
        self.assertIn("not equated with extra lives", claims["pvp_life"])

    def test_timeline_ownership_and_dps_boundaries(self):
        self.assertEqual(
            ["Menu", "Game", "EndGame"],
            [event["scene"] for event in self.runtime["timeline_scene_transitions"]],
        )
        claims = self.receipt["claim_boundaries"]
        self.assertIn("Player_Controller", claims["health_vs_attack_vs_controller"])
        self.assertIn("MODEL_NOT_MEASURED", claims["dps"])
        self.assertEqual("modded/repackaged 1.0.69", self.receipt["capture_identity"]["build"])


if __name__ == "__main__":
    unittest.main()
