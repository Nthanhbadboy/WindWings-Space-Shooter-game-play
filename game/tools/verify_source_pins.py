#!/usr/bin/env python3
"""Resolve each Godot data source pin against the original Git blob bytes."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "game" / "data"
MANIFEST_PATH = DATA_DIR / "source_pins.json"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def is_safe_relative_path(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts and bool(path.parts)


def git_blob(commit: str, source_path: str) -> bytes:
    spec = f"{commit}:{source_path}"
    result = subprocess.run(
        ["git", "cat-file", "blob", spec],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        fail(f"cannot resolve pinned source blob {spec}: {result.stderr.decode().strip()}")
    return result.stdout


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        fail("unsupported source_pins.json schema_version")

    commit = manifest.get("source_commit", "")
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        fail("source_commit must be a full 40-character lowercase Git SHA")
    commit_check = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if commit_check.returncode != 0:
        fail(f"pinned source commit {commit} is not present; CI must fetch it first")

    pins = manifest.get("pins")
    if not isinstance(pins, list) or not pins:
        fail("pins must be a non-empty list")

    seen_files: set[str] = set()
    source_cache: dict[str, bytes] = {}
    for pin in pins:
        if not isinstance(pin, dict):
            fail("every pin must be an object")
        local_name = pin.get("file", "")
        source_path = pin.get("source_path", "")
        expected_sha = pin.get("sha256", "")
        copy_exact = pin.get("copy_exact", False)
        if not isinstance(local_name, str) or not is_safe_relative_path(local_name):
            fail(f"unsafe or missing local file path: {local_name!r}")
        if local_name in seen_files:
            fail(f"duplicate local file pin: {local_name}")
        seen_files.add(local_name)
        if not isinstance(source_path, str) or not is_safe_relative_path(source_path):
            fail(f"unsafe or missing source path for {local_name}")
        if not isinstance(expected_sha, str) or not SHA256_RE.fullmatch(expected_sha):
            fail(f"{local_name}: sha256 must be 64 lowercase hex characters")
        if not isinstance(copy_exact, bool):
            fail(f"{local_name}: copy_exact must be boolean")

        local_path = (DATA_DIR / local_name).resolve()
        try:
            local_path.relative_to(DATA_DIR.resolve())
        except ValueError:
            fail(f"{local_name}: local path escapes game/data")
        if not local_path.is_file():
            fail(f"missing local data file game/data/{local_name}")
        local_bytes = local_path.read_bytes()

        if source_path not in source_cache:
            source_cache[source_path] = git_blob(commit, source_path)
        source_bytes = source_cache[source_path]
        actual_sha = hashlib.sha256(source_bytes).hexdigest()
        if actual_sha != expected_sha:
            fail(
                f"{local_name}: manifest pin {expected_sha} does not match "
                f"{commit}:{source_path} bytes ({actual_sha})"
            )

        if copy_exact:
            if local_bytes != source_bytes:
                fail(f"{local_name}: exact source copy differs from {commit}:{source_path}")
        elif local_path.suffix == ".json":
            document = json.loads(local_bytes)
            if document.get("source_sha256") != expected_sha:
                fail(f"{local_name}: embedded source_sha256 differs from the resolved source bytes")

    for path in sorted(DATA_DIR.glob("*.json")):
        if path.name == MANIFEST_PATH.name:
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        if "source_sha256" in document and path.name not in seen_files:
            fail(f"{path.name}: source_sha256 exists but no resolved source pin covers it")

    print(
        f"PASS: resolved {len(pins)} source pins at {commit}; "
        f"{sum(bool(pin.get('copy_exact', False)) for pin in pins)} exact source copies byte-match"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
