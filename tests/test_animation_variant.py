"""Unit tests for the animation build variant parameter (A / B / C).

The runtime half of this rule lives in game/scripts/animation_variant.gd and is
checked by game/tests/run_tests.gd; these tests cover the build-time writer that
CI runs before exporting each Windows build.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "game" / "tools" / "build_variant.py"
SHIPPED = REPO_ROOT / "game" / "data" / "animation_variant.json"
ART = REPO_ROOT / "game" / "art"


def run_tool(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TOOL), *args], capture_output=True, text=True, check=False
    )


class BuildVariantTests(unittest.TestCase):
    def test_a_and_b_are_layered_and_c_is_whole(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            modes = {}
            for variant in ("A", "B", "C"):
                out = pathlib.Path(tmp) / f"{variant}.json"
                result = run_tool("--variant", variant, "--out", str(out))
                self.assertEqual(result.returncode, 0, result.stderr)
                document = json.loads(out.read_text())
                modes[variant] = document["mode"]
                self.assertEqual(document["variant"], variant)
                self.assertEqual(document["art_folder"], f"art/{variant}")
                self.assertEqual(document["art_source"], "placeholder")
                self.assertNotIn("SCRIPT", document["note"].upper())
            self.assertEqual(modes, {"A": "layered", "B": "layered", "C": "whole"})

    def test_package_builds_must_name_their_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / "package.json"
            missing = run_tool("--variant", "B", "--art-source", "package", "--out", str(out))
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("art-package-commit", missing.stderr)
            self.assertFalse(out.exists())

            # A placeholder build must not claim a package commit either.
            fake = run_tool(
                "--variant",
                "B",
                "--art-source",
                "placeholder",
                "--art-package-commit",
                "215aa58f",
                "--out",
                str(out),
            )
            self.assertNotEqual(fake.returncode, 0)

            real = run_tool(
                "--variant",
                "B",
                "--art-source",
                "package",
                "--art-package-commit",
                "215aa58f",
                "--out",
                str(out),
            )
            self.assertEqual(real.returncode, 0, real.stderr)
            document = json.loads(out.read_text())
            self.assertEqual(document["art_source"], "package")
            self.assertEqual(document["art_package_commit"], "215aa58f")

    def test_unknown_variant_is_refused(self) -> None:
        result = run_tool("--variant", "D")
        self.assertNotEqual(result.returncode, 0)

    def test_check_mode_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / "variant.json"
            self.assertEqual(run_tool("--variant", "C", "--out", str(out)).returncode, 0)
            same = run_tool("--variant", "C", "--check", "--out", str(out))
            self.assertEqual(same.returncode, 0, same.stderr)
            drifted = run_tool("--variant", "A", "--check", "--out", str(out))
            self.assertNotEqual(drifted.returncode, 0)
            self.assertIn("VARIANT_FILE_STALE", drifted.stderr)

    def test_shipped_default_is_a_valid_variant(self) -> None:
        document = json.loads(SHIPPED.read_text())
        self.assertIn(document["variant"], ("A", "B", "C"))
        self.assertEqual(document["mode"], "whole" if document["variant"] == "C" else "layered")
        check = run_tool(
            "--variant",
            document["variant"],
            "--art-source",
            document["art_source"],
            "--art-package-commit",
            document["art_package_commit"],
            "--check",
            "--out",
            str(SHIPPED),
        )
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_each_variant_has_its_own_art_folder(self) -> None:
        for variant in ("A", "B", "C"):
            folder = ART / variant
            self.assertTrue(folder.is_dir(), f"missing art folder {folder}")
            readme = (folder / "README.md").read_text(encoding="utf-8")
            self.assertIn("placeholder", readme.lower())


class MotionReadmeTests(unittest.TestCase):
    """The motion evidence must name its variant and say when art is placeholder."""

    def test_readme_names_variant_and_placeholder(self) -> None:
        import importlib.util
        import tempfile

        try:
            import PIL  # noqa: F401
        except ImportError:  # pragma: no cover - Pillow is a CI dependency
            self.skipTest("Pillow is not installed")

        spec = importlib.util.spec_from_file_location(
            "build_motion_gifs", REPO_ROOT / "game" / "tools" / "build_motion_gifs.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as tmp:
            frames = pathlib.Path(tmp) / "frames"
            segment = frames / "hangar"
            segment.mkdir(parents=True)
            from PIL import Image
            for index in range(3):
                Image.new("RGB", (32, 48), (10, 20, 30 + index)).save(
                    segment / f"frame_{index:04d}.png"
                )
            (segment / "frames.txt").write_text("f\t0.0\nf\t0.1\nf\t0.2\n", encoding="utf-8")

            out = pathlib.Path(tmp) / "motion" / "C"
            argv = [
                "--frames",
                str(frames),
                "--out",
                str(out),
                "--variant",
                "C",
                "--mode",
                "whole",
                "--art-source",
                "placeholder",
            ]
            old_argv = sys.argv
            sys.argv = ["build_motion_gifs.py", *argv]
            try:
                self.assertEqual(module.main(), 0)
            finally:
                sys.argv = old_argv

            readme = (out / "README.md").read_text(encoding="utf-8")
            self.assertIn("ANIM-C", readme)
            self.assertIn("whole-image animation", readme)
            self.assertIn("placeholder", readme)
            self.assertIn("hangar", readme)


if __name__ == "__main__":
    unittest.main()
