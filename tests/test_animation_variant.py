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
        """Every variant folder must hold the delivered package, hashes included."""
        import hashlib

        for variant in ("A", "B", "C"):
            folder = ART / variant
            self.assertTrue(folder.is_dir(), f"missing art folder {folder}")
            readme = (folder / "README.md").read_text(encoding="utf-8")
            self.assertIn("7aa3d08", readme)
            for required in ("ships/PLAYER-10001.png", "bosses/Boss-37001.png", "manifest.json"):
                self.assertTrue((folder / required).is_file(), f"{variant} lacks {required}")

            # The package's own manifest must still describe the committed bytes:
            # nothing in game/art/<variant>/ may be edited or re-encoded.
            manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
            checked = 0
            for entry in manifest["file_list"]:
                name = entry["file"]
                if not name.startswith("game/art/"):
                    continue
                target = folder / name[len("game/art/") :]
                self.assertTrue(target.is_file(), f"{variant} lacks {name}")
                digest = hashlib.sha256(target.read_bytes()).hexdigest()
                self.assertEqual(digest, entry["sha256"], f"{variant} changed {name}")
                checked += 1
            minimum = 2 if variant == "C" else 5  # C ships two flat images, no layers
            self.assertGreaterEqual(checked, minimum, f"{variant} verified only {checked} files")

    def test_layer_packages_ship_their_layers(self) -> None:
        """A and B must carry the layer files the contract asks for."""
        expected = {
            "A": [
                "layers/ships/PLAYER-10001-canopy-glow.png",
                "layers/ships/PLAYER-10001-nozzle-glow.png",
                "layers/bosses/Boss-37001-turret-left.png",
                "layers/bosses/Boss-37001-turret-right.png",
                "layers/bosses/Boss-37001-core-glow.png",
            ],
            "B": [
                "layers/ships/PLAYER-10001-canopy-glow.png",
                "layers/bosses/Boss-37001-turret-left.png",
                "layers/bosses/Boss-37001-turret-right.png",
                "layers/bosses/Boss-37001-core-glow.png",
            ],
            "C": [],
        }
        for variant, files in expected.items():
            for relative in files:
                self.assertTrue(
                    (ART / variant / relative).is_file(), f"variant {variant} lacks {relative}"
                )
        # C is the flat package: it must NOT smuggle layers in, or the whole-image
        # build could silently switch to layered animation.
        self.assertFalse((ART / "C" / "layers").exists())


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
