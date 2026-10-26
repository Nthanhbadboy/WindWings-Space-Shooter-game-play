import gzip
import json
import unittest
from pathlib import Path

from tools.build_l2_runtime_map_depth2_28 import (
    OUTPUT,
    PINS,
    RAW,
    build,
    build_file,
)


class RuntimeMapDepth2BlockerTests(unittest.TestCase):
    def artifact(self):
        return json.loads(gzip.decompress(OUTPUT.read_bytes()))

    def test_deterministic_builder(self):
        build_file(check=True)
        self.assertTrue(OUTPUT.exists())

    def test_no_map_values_or_session_are_claimed(self):
        a = self.artifact()
        self.assertEqual(a["result"], "BLOCKED_BEFORE_SESSION_NO_BRIDGE")
        self.assertEqual(a["runtime_readback"]["status"], "NOT_OBSERVED")
        self.assertIsNone(a["runtime_readback"]["map_values"])
        self.assertFalse(a["runtime_readback"]["session_started"])

    def test_success_conclusion_is_not_misreported_as_live_probe(self):
        a = self.artifact()
        self.assertEqual(a["run"]["run_conclusion"], "success")
        self.assertEqual(a["run"]["probe_job_conclusion"], "success")
        steps = a["run"]["relevant_step_conclusions"]
        self.assertEqual(steps["Gate on bridge presence"], "success")
        for name in ("Credentials", "Start session", "Probe game state", "End session"):
            self.assertEqual(steps[name], "skipped")

    def test_only_scoped_apk_bridge_absence_is_recorded(self):
        a = self.artifact()
        self.assertFalse(a["preflight"]["bridge_present_in_apk"])
        self.assertEqual(a["preflight"]["source_xapk_sha256"], "f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e")
        self.assertIn("not a repository-wide claim", " ".join(a["limits"]))

    def test_allow_no_bridge_is_classified_as_smoke_only(self):
        a = self.artifact()
        self.assertIn("smoke-test only", a["no_bridge_alternative"])
        self.assertIn("cannot read /scene or /statics", a["no_bridge_alternative"])

    def test_every_raw_github_receipt_is_pinned(self):
        a = self.artifact()
        for name, expected in PINS.items():
            self.assertEqual(a["source_pins"][f"raw/{name}"], expected)
            self.assertTrue((RAW / name).is_file())

    def test_tampered_receipt_fails_closed(self):
        raw_dir = Path(self._copy_raw_dir())
        try:
            target = raw_dir / next(iter(PINS))
            target.write_bytes(target.read_bytes() + b"x")
            with self.assertRaisesRegex(ValueError, "receipt SHA mismatch"):
                build(raw_dir=raw_dir)
        finally:
            for p in raw_dir.iterdir():
                p.unlink()
            raw_dir.rmdir()

    @staticmethod
    def _copy_raw_dir():
        import shutil
        import tempfile
        path = Path(tempfile.mkdtemp(prefix="l2-runtime-map-28-"))
        for file in RAW.iterdir():
            shutil.copy2(file, path / file.name)
        return path


if __name__ == "__main__":
    unittest.main()
