import copy
import gzip
import json
import unittest

from tools.build_l2_a5a74747_25_save_durability_audit import (
    OUTPUT_PATH,
    ROOT,
    build_receipt,
    encode_receipt,
    read_inputs,
)


class SaveDurabilityAudit25Tests(unittest.TestCase):
    def artifact(self):
        return json.loads(gzip.decompress((ROOT / OUTPUT_PATH).read_bytes()))

    def test_deterministic_scoped_builder(self):
        self.assertEqual(encode_receipt(build_receipt(*read_inputs())), (ROOT / OUTPUT_PATH).read_bytes())

    def test_status_and_limits_do_not_claim_runtime_or_global_durability(self):
        artifact = self.artifact()
        self.assertEqual(artifact["status"], "SCOPED_STATIC_SAVE_CALL_CENSUS_NOT_DURABILITY_PROOF")
        self.assertEqual(artifact["task"]["runtime_readback"], "NOT_OBSERVED")
        self.assertFalse(artifact["task"]["source_package_modified"])
        boundaries = " ".join(artifact["evidence_boundary"])
        self.assertIn("do not establish repository-wide absence", boundaries)
        self.assertIn("crash atomicity", boundaries)
        self.assertIn("migration correctness", boundaries)

    def test_pinned_method_set_has_zero_direct_playerprefs_save_edges(self):
        census = self.artifact()["persistence_receipt_method_census"]
        self.assertEqual(census["opening_contracts_method_records"], 41)
        self.assertEqual(census["player_loadout_contract_method_records"], 33)
        self.assertEqual(census["distinct_method_records"], 74)
        self.assertEqual(census["playerpreferences_bodies_in_opening_receipt"], 18)
        self.assertEqual(census["raw_playerpreferences_inventory_method_records"], 21)
        self.assertEqual(census["direct_playerprefs_save_named_call_count"], 0)
        self.assertEqual(census["direct_playerprefs_save_rva_call_count"], 0)
        self.assertEqual(census["direct_playerprefs_save_calls"], [])

    def test_custom_file_store_save_callers_are_not_playerprefs_flush(self):
        census = self.artifact()["persistence_receipt_method_census"]
        callers = {(row["caller"], row["callsite"]) for row in census["custom_save_to_disk_callers"]}
        self.assertEqual(callers, {
            ("PlayerPreferences.DeleteAll", "0x13f1ab0"),
            ("PlayerPreferences.OnApplicationFocus", "0x13f1cd0"),
            ("PlayerPreferences.OnApplicationQuit", "0x13f1c84"),
        })
        writes = census["custom_save_to_disk_file_writes"]
        self.assertEqual(len(writes), 1)
        self.assertEqual(writes[0]["target_signature"], "public static void WriteAllBytes(string path, byte[] bytes) { }")
        self.assertEqual(writes[0]["callsite"], "0x13f1b3c")
        self.assertIn("PlayerPrefs.Save RVA", self.artifact()["raw_asm_direct_branch_scan"]["search_pattern"])

    def test_asm_scan_is_pinned_and_scoped(self):
        scan = self.artifact()["raw_asm_direct_branch_scan"]
        self.assertEqual(scan["file_count"], 314)
        self.assertEqual(scan["total_bytes"], 7_823_314)
        self.assertEqual(scan["inventory_sha256"], "c9e29739bc0ade975b85bd8eb26f04afc4cb961a1f0fe3026d6811a0e74a57d0")
        self.assertEqual(scan["direct_branch_match_count"], 0)
        self.assertEqual(scan["direct_branch_matches"], [])
        self.assertIn("indirect calls", scan["boundary"])
        self.assertEqual(len(scan["file_pins"]), 314)

    def test_migration_search_and_contract_pack_version_are_scoped(self):
        census = self.artifact()["persistence_receipt_method_census"]
        self.assertEqual(census["save_format_or_migration_signal_count"], 0)
        self.assertEqual(census["save_format_or_migration_signal_hits"], [])
        self.assertEqual(census["contract_pack_schema_versions"], {
            "datas/opening_persistence.json": 1,
            "datas/player_loadout_persistence.json": 1,
        })
        self.assertIn("not the game's save format", census["contract_pack_schema_note"])

    def test_source_package_and_engine_api_are_pinned_separately(self):
        artifact = self.artifact()
        identity = artifact["source_identity"]
        self.assertEqual(identity["xapk_sha256"], "f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e")
        self.assertEqual(identity["libil2cpp_so_sha256"], "9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99")
        api = artifact["unity_playerprefs_save_api"]
        self.assertEqual(api["rva"], "0x277cf6c")
        self.assertFalse(api["body_in_dump"])
        self.assertIn("no engine implementation", api["interpretation"])

    def test_injected_call_edge_is_counted_without_becoming_raw_asm_hit(self):
        inputs = list(read_inputs())
        opening = copy.deepcopy(inputs[0])
        method = opening["methods"][0]
        method.setdefault("calls", []).append({
            "callsite": "0xdeadbeef",
            "instruction": "bl",
            "target_rva": "0x277cf6c",
            "declaration": {"class_name": "PlayerPrefs", "signature": "public static void Save() { }"},
        })
        inputs[0] = opening
        receipt = build_receipt(*inputs)
        census = receipt["persistence_receipt_method_census"]
        self.assertEqual(census["direct_playerprefs_save_named_call_count"], 1)
        self.assertEqual(census["direct_playerprefs_save_rva_call_count"], 1)
        self.assertEqual(receipt["raw_asm_direct_branch_scan"]["direct_branch_match_count"], 0)


if __name__ == "__main__":
    unittest.main()
