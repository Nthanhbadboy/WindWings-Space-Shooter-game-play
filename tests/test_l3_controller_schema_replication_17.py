import gzip
import json
import unittest
from pathlib import Path

from tools.build_l3_controller_schema_replication_17 import (
    INPUT,
    OUTPUT,
    build,
    build_from_file,
    decode_add_imm,
    decode_adrp,
    decode_bl,
    sign_extend,
)


class InstructionDecodeTests(unittest.TestCase):
    def test_sign_extend(self):
        self.assertEqual(sign_extend(0x3FFFFFF, 26), -1)
        self.assertEqual(sign_extend(0, 26), 0)

    def test_decode_adrp_and_literal_add_pair(self):
        adrp_word = int.from_bytes(bytes.fromhex("a1abffd0"), "little")
        add_word = int.from_bytes(bytes.fromhex("21101391"), "little")
        register, page = decode_adrp(adrp_word, 0xB7FCB0)
        rd, rn, immediate = decode_add_imm(add_word)
        self.assertEqual((register, rd, rn), (1, 1, 1))
        self.assertEqual(page + immediate, 0xF54C4)

    def test_decode_bl_target(self):
        word = int.from_bytes(bytes.fromhex("1eaee997"), "little")
        self.assertEqual(decode_bl(word, 0xB7FCCC), 0x5EB544)

    def test_reject_non_matching_instruction_classes(self):
        self.assertIsNone(decode_adrp(0, 0x1000))
        self.assertIsNone(decode_add_imm(0,))
        self.assertIsNone(decode_bl(0, 0x1000))


class ReplicationArtifactTests(unittest.TestCase):
    def test_pinned_source_rebuilds_deterministically(self):
        rebuilt = build_from_file(INPUT, OUTPUT, check=True)
        data = gzip.decompress(rebuilt)
        artifact = json.loads(data)
        self.assertEqual(artifact["result"], "PARTIAL_NATIVE_SERIALIZER_SEQUENCE_REPLICATION")
        self.assertTrue(artifact["replication"])

    def test_both_native_paths_contain_same_ordered_bounded_slice(self):
        artifact = json.loads(gzip.decompress(OUTPUT.read_bytes()))
        expected = ["m_InterruptionSource", "m_OrderedInterruption", "m_CanTransitionToSelf"]
        paths = artifact["observations"]
        self.assertEqual(list(paths), ["native_path_A", "native_path_B"])
        for path in paths.values():
            rows = path["field_sequence"]
            self.assertEqual([r["field"] for r in rows], expected)
            self.assertEqual(len({r["helper_target_va"] for r in rows}), 1)
            for row in rows:
                self.assertIn(row["literal_add_va"] - row["adrp_va"], (4, 8, 12))
                self.assertGreater(row["helper_call_va"], row["literal_add_va"])

    def test_source_failure_is_not_silently_accepted(self):
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            build(INPUT.read_bytes()[:-1] + b"x")

    def test_reported_limits_keep_schema_identity_open(self):
        artifact = json.loads(gzip.decompress(OUTPUT.read_bytes()))
        limits = " ".join(artifact["limits"])
        self.assertIn("not clean-room APK extraction", limits)
        self.assertIn("not independent discovery", limits)
        self.assertIn("No owning class/type-tree identity", limits)


if __name__ == "__main__":
    unittest.main()
