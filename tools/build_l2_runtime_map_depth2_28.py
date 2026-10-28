#!/usr/bin/env python3
"""Build a pinned blocker receipt for #28 Map depth-2 runtime collection.

The pinned PR14 run stopped at the no-bridge gate. This records why no live
Map values exist in that run; it does not claim a Map readback or absence.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "reverse-engineering/raw/l2-runtime-map-depth2-28"
OUTPUT = ROOT / "datas/l2_runtime_map_depth2_28.json.gz"
RUN_ID = 40310064929
HEAD_SHA = "4cb2828ec5731d68100f7319ac40b48bb34e08c6"
PINS = {
    "run-40310064929.json": "467c6b7d54dbee8f87dae7f40b8fb5710022e18f703b5d2805b312421781d169",
    "jobs-40310064929.json": "51f0689a2b6b81b2ff8f6982a31b7e23c63186a80c61d6d4a81d98ebaeeeb4c6",
    "pr12-runtime-preflight-6411232160.json": "aec77bd8b3ea789d73738093cfe38d05890b92c246fd4676fd8e37fb08d52f2e",
}
SOURCE_PINS = {
    ".github/workflows/ramus-probe.yml": "0bbdf214940d9125b5867320f1c44100f72630c8fb1312941da7696161d93af8",
    ".github/scripts/probe-inputs.sh": "aff9510b781fbd4fe6daa7416c3125e8fdd6acc2dc63ff6f603fdd191d7a1b63",
    ".github/scripts/prepare-apk.sh": "8b9d5bb83037fb1570722af2ac7f4c36b4ed586723742ae91bdea6e315e71118",
    "runtime-probe/RamusBridge.cs": "d1a20f7a243e1a3baa381f3c6c188556f3c2c325a72e51b8cb869eb2e62ac9e9",
    "runtime-probe/collect.sh": "c6199c05432f1ad56d3495292aa1b53dbee9dbc33830c0ff3fc993e1eb8a69df",
}
RELEVANT_STEPS = (
    "Gate on bridge presence",
    "Check APK against the trial limit",
    "Pre-session checks",
    "Credentials",
    "Start session",
    "Upload and install the APK (session_mode=install)",
    "Launch the app (session_mode=install)",
    "Probe game state",
    "End session",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def build(raw_dir: Path = RAW, root: Path = ROOT) -> dict:
    raw_bytes = {}
    parsed = {}
    for name, expected_sha in PINS.items():
        data = (raw_dir / name).read_bytes()
        if sha256(data) != expected_sha:
            raise ValueError(f"pinned GitHub receipt SHA mismatch: {name}")
        raw_bytes[name] = data
        parsed[name] = json.loads(data)

    for name, expected_sha in SOURCE_PINS.items():
        data = (root / name).read_bytes()
        if sha256(data) != expected_sha:
            raise ValueError(f"pinned vehicle source SHA mismatch: {name}")

    run = parsed["run-40310064929.json"]
    comment = parsed["pr12-runtime-preflight-6411232160.json"]
    jobs_payload = parsed["jobs-40310064929.json"]
    if run.get("id") != RUN_ID or run.get("head_sha") != HEAD_SHA:
        raise ValueError("unexpected PR14 workflow run identity")
    if run.get("event") != "pull_request" or run.get("conclusion") != "success":
        raise ValueError("unexpected workflow event/conclusion")
    if comment.get("id") != 6411232160 or "bridge:      no" not in comment.get("body", ""):
        raise ValueError("preflight comment does not pin the no-bridge verdict")
    if "sha256:      f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e" not in comment["body"]:
        raise ValueError("XAPK source pin missing from PR preflight comment")
    if "117158131 B" not in comment["body"] or "abis=arm64-v8a" not in comment["body"]:
        raise ValueError("base APK size/ABI inventory missing from PR preflight comment")
    if "trial limit   150 MB" not in comment["body"]:
        raise ValueError("trial-size note missing from PR preflight comment")

    probe = next((j for j in jobs_payload.get("jobs", []) if j.get("name") == "ramus device probe"), None)
    if not probe or probe.get("conclusion") != "success":
        raise ValueError("expected PR14 runtime-probe job metadata")
    steps = {s["name"]: s.get("conclusion") for s in probe.get("steps", [])}
    observed_steps = {name: steps.get(name, "MISSING") for name in RELEVANT_STEPS}
    if observed_steps["Gate on bridge presence"] != "success":
        raise ValueError("bridge gate step was not observed successful")
    for name in RELEVANT_STEPS[1:]:
        if observed_steps[name] != "skipped":
            raise ValueError(f"expected {name!r} skipped after bridge gate, got {observed_steps[name]!r}")

    workflow_text = (root / ".github/workflows/ramus-probe.yml").read_text()
    if "continuing as a device/ABI smoke test only" not in workflow_text or "cannot read /scene or /statics" not in workflow_text:
        raise ValueError("workflow no-bridge boundary changed; review before regenerating")

    return {
        "artifact": "l2_runtime_map_depth2_28",
        "claim": "#28 map nested-value runtime receipt via PR14 vehicle",
        "result": "BLOCKED_BEFORE_SESSION_NO_BRIDGE",
        "requested_readback": {"type": "Map_Get_Datas", "field": "listMapDatas", "arr": 256, "depth": 2},
        "runtime_readback": {
            "status": "NOT_OBSERVED",
            "map_values": None,
            "session_started": False,
            "interpretation": "This run contains no Map runtime receipt; it does not establish that Map values are absent or unavailable elsewhere.",
        },
        "run": {
            "id": RUN_ID,
            "head_sha": run["head_sha"],
            "head_branch": run.get("head_branch"),
            "event": run["event"],
            "workflow": "runtime-probe",
            "created_at": run["created_at"],
            "updated_at": run["updated_at"],
            "run_conclusion": run["conclusion"],
            "probe_job_conclusion": probe["conclusion"],
            "relevant_step_conclusions": observed_steps,
        },
        "preflight": {
            "comment_id": comment["id"],
            "comment_updated_at": comment["updated_at"],
            "source_xapk_sha256": "f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e",
            "bridge_present_in_apk": False,
            "base_abi": ["arm64-v8a"],
            "base_apk_bytes": 117158131,
            "trial_limit_mb": 150,
            "limit_step_executed": False,
        },
        "cause": "The preflight found no RamusBridge.dll in base.apk or splits. The bridge gate passed as a skip/stop condition before trial-limit, credentials, session start, install, launch, and probe steps.",
        "no_bridge_alternative": "The workflow explicitly documents allow_no_bridge=true as device/ABI smoke-test only; it cannot read /scene or /statics. It was not used for this Map-value claim.",
        "source_pins": {
            **{f"raw/{name}": digest for name, digest in PINS.items()},
            **SOURCE_PINS,
            "pr14_source_commit": HEAD_SHA,
        },
        "limits": [
            "No Ramus session or live Map request occurred in run 40310064929.",
            "Run-level success is not a runtime-readback success: the probe job's critical steps were skipped.",
            "The 117158131-byte APK is below the documented 150 MB trial ceiling, but the trial-limit step itself was skipped; this was not a trial eligibility test.",
            "The preflight inventory says arm64-v8a only; the workflow warns Ramus uses x86_64, but no device launch was attempted, so ABI compatibility is unresolved.",
            "This is scoped to this pinned PR14 run and its pinned source; it is not a repository-wide claim that no other Map receipt or bridge exists.",
        ],
    }


def build_file(check: bool = False) -> bytes:
    data = gzip.compress(canonical(build()), mtime=0)
    if check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != data:
            raise SystemExit("artifact differs; regenerate with this builder")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(data)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build_file(check=args.check)
    print(f"artifact_bytes={len(data)} sha256={sha256(data)}")


if __name__ == "__main__":
    main()
