from __future__ import annotations

import gzip
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools import build_l2_combat_semantics_24 as builder

ROOT = Path(__file__).resolve().parents[1]


class L2CombatSemantics24Tests(unittest.TestCase):
    def artifact(self) -> dict:
        return json.loads(gzip.decompress((ROOT / "datas/l2_combat_semantics_24.json.gz").read_bytes()))

    def test_rebuild_is_byte_deterministic(self) -> None:
        expected = builder.build_file(check=False)
        self.assertEqual(expected, (ROOT / "datas/l2_combat_semantics_24.json.gz").read_bytes())
        self.assertEqual(expected, builder.build_file(check=False))

    def test_board_display_arrays_and_combat_damage_array_are_distinct(self) -> None:
        data = self.artifact()
        board = data["board_power_display"]
        combat = data["combat_damage_path"]
        self.assertEqual([f["name"] for f in board["fields"]], ["allBasicAtk", "allDeltaAtk"])
        self.assertEqual([f["static_offset"] for f in board["fields"]], ["0x10", "0x18"])
        self.assertEqual(combat["base_array"]["field"], "StartMainCannonDamages")
        self.assertEqual(combat["base_array"]["static_offset"], "0x78")
        self.assertIn("textPlayerPower", board["display_caller"])
        self.assertIn("GetMainCannonDamage", combat["damage_method"])
        self.assertEqual(data["status"], "BOUNDED_STATIC_REPLICATION_NOT_RUNTIME")

    def test_display_path_arithmetic_is_not_recast_as_combat_damage(self) -> None:
        data = self.artifact()
        self.assertEqual(
            data["board_power_display"]["formula"],
            "basic[i] * (1 + delta[i] * GetPlayerLevel(_indexPlayer))",
        )
        self.assertIn("separate MainCannonAttack iteration decision", data["combat_damage_path"]["rank_input_to_damage_getter"])
        self.assertIn("not established as the combat damage input", data["result"]["interpretation"])

    def test_rank_gates_guarded_loop_not_per_hit_multiplier(self) -> None:
        data = self.artifact()
        rank = data["rank_attack_path"]
        self.assertEqual(rank["field_declaration"], "Player_Attack.rank @ 0x44 (base class)")
        self.assertEqual(rank["loop"]["rank_equal_3"], 2)
        self.assertEqual(rank["loop"]["rank_at_least_4"], 4)
        self.assertEqual(rank["loop"]["other_rank_below_4"], "returns before loop")
        self.assertIn("not measured successful bullets or hits", rank["qualification"])
        rank_window = data["evidence_windows"]["rank_gated_attack_loop"]["instructions"]
        self.assertTrue(any("cmp      w8, #3" in line for line in rank_window))
        self.assertTrue(any("cmp      w8, #4" in line for line in rank_window))
        self.assertTrue(any("cmp      x27, x26" in line for line in rank_window))

    def test_combat_callback_and_damage_getter_have_pinned_method_boundaries(self) -> None:
        data = self.artifact()
        boundaries = data["method_boundary_checks"]
        for name in ("get_GetMainCannonDamage", "MainCannonAttack", "OnBulletMainCannonCollided"):
            self.assertFalse(boundaries[name]["size_capped"])
            self.assertTrue(boundaries[name]["ends_clean"])
        self.assertEqual(data["combat_damage_path"]["getter_override"]["tail_branch_target"], "0x14E3948")
        self.assertEqual(data["combat_damage_path"]["collision_callback"]["crit_multiplier_choices"], [1.0, 2.0])
        self.assertEqual(data["combat_damage_path"]["collision_callback"]["receiver_dispatch"], "indirect; actual HP delta not established")

    def test_replication_identity_and_source_pins_are_embedded(self) -> None:
        data = self.artifact()
        replication = data["replication"]
        self.assertEqual(replication["label"], "REPLICATION")
        self.assertEqual(replication["source_branch"], "arena/ef6b75ef-windwings-space-shooter-game-p")
        self.assertEqual(replication["source_commit"], "72041a1d400be6b0972f5bfa9868efe3befaeca7")
        self.assertEqual(len(data["source_pins"]), len(builder.PINS))
        self.assertEqual(data["source_pins"][builder.PEER_ATTACK_ARCHIVE],
                         "eacd421213aa399fc851ab71c3be2acc310f5b05301e1840303f990ab1fe7545")
        self.assertEqual(data["source_content_pins"]["reverse-engineering/raw/player-firing/native/Player_Attack_1.asm.txt"],
                         builder.PEER_ATTACK_CONTENT_SHA256)
        self.assertEqual(data["source_pins"]["datas/l2_basic_attack_array_consumers.json.gz"],
                         "79d7232db9fcadeb94a9cbe47346c097f87e684d1cf7b55c499b84a3607b90df")
        self.assertEqual(replication["source_identity"]["xapk_sha256"],
                         "f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e")

    def test_scope_limits_forbid_runtime_and_all_ship_extrapolation(self) -> None:
        data = self.artifact()
        limits = "\n".join(data["limits"])
        self.assertIn("no runtime run", limits)
        self.assertIn("No all-24 extrapolation", data["replication"]["scope"])
        self.assertIn("No repository-wide absence claim", limits)
        self.assertIn("DPS", limits)
        self.assertIn("all-ship", limits)

    def test_mutated_peer_source_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            copied_root = Path(temp)
            for relative in builder.PINS:
                src = ROOT / relative
                dst = copied_root / relative
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
            peer_source = copied_root / builder.PEER_ATTACK_ARCHIVE
            peer_source.write_bytes(peer_source.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "source SHA mismatch"):
                builder.build(root=copied_root)


if __name__ == "__main__":
    unittest.main()
