#!/usr/bin/env python3
"""Write game/data/animation_variant.json for one animation build variant.

The Windows export job runs this once per matrix entry before Godot imports the
project, so each .exe ships knowing its own variant:

    python3 game/tools/build_variant.py --variant B \\
        --art-source package --art-package-commit 215aa58f

Rules enforced here (and again at runtime by scripts/animation_variant.gd):
  * A and B are layered builds: body + glow layers, boss body/gun-l/gun-r/core.
  * C is a whole-image build: one flat picture per sprite, no layer slots.
  * art_source=package requires an art package commit; placeholder does not.

`--check` verifies the file on disk already matches the requested arguments and
exits 1 when it drifted, which the workflow uses to catch a stale file.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO_ROOT / "game" / "data" / "animation_variant.json"

VARIANTS = ("A", "B", "C")
MODES = {"A": "layered", "B": "layered", "C": "whole"}
SOURCES = ("placeholder", "package")

MODE_NOTES = {
    "A": "generated clean layers: ship glow layer, boss body/gun-l/gun-r/core, guns track the ship",
    "B": "inpainted flat layers: same layer slots as A, same animation rules",
    "C": "single flat image: bob/bank/flash/shake, particle overlay on the hull, guns fixed, flame on the hull",
}


def build_document(variant: str, art_source: str, art_package_commit: str) -> dict:
    variant = variant.upper()
    if variant not in VARIANTS:
        raise SystemExit(f"unknown variant {variant!r}; expected one of {', '.join(VARIANTS)}")
    if art_source not in SOURCES:
        raise SystemExit(f"unknown art source {art_source!r}; expected one of {', '.join(SOURCES)}")
    commit = art_package_commit.strip()
    if art_source == "package" and not commit:
        raise SystemExit("--art-source package needs --art-package-commit <sha>")
    if art_source == "placeholder" and commit:
        raise SystemExit("placeholder builds must not claim an art package commit")
    return {
        "variant": variant,
        "mode": MODES[variant],
        "art_source": art_source,
        "art_package_commit": commit,
        "art_folder": f"art/{variant}",
        "note": MODE_NOTES[variant],
    }


def serialise(document: dict) -> str:
    return json.dumps(document, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", required=True, choices=VARIANTS)
    parser.add_argument("--art-source", default="placeholder", choices=SOURCES)
    parser.add_argument("--art-package-commit", default="")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail instead of writing when the file does not match the arguments",
    )
    args = parser.parse_args(argv)

    document = build_document(args.variant, args.art_source, args.art_package_commit)
    text = serialise(document)
    out = pathlib.Path(args.out)

    if args.check:
        current = out.read_text(encoding="utf-8") if out.exists() else ""
        if current == text:
            print(f"VARIANT_FILE_OK {out} {document['variant']} {document['mode']}")
            return 0
        print(f"VARIANT_FILE_STALE {out}", file=sys.stderr)
        print(current, file=sys.stderr)
        return 1

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(
        "VARIANT_WRITTEN variant=%s mode=%s art=%s source=%s commit=%s"
        % (
            document["variant"],
            document["mode"],
            document["art_folder"],
            document["art_source"],
            document["art_package_commit"] or "none",
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
