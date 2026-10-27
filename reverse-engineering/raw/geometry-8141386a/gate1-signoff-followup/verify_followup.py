#!/usr/bin/env python3
"""Verify the fixed-cut Gate-1 sign-off follow-up without opening runtime/APK lanes.

This verifies the captured document, registry, earlier review and GitHub records.  It
is not a fresh audit of the original game, and cannot verify the user's private chat.
Run from any directory: python3 verify_followup.py --check [--git]
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CAPTURE_SHA256 = "805e9389594bc703b59201b54deddb2c5d0e955d73fce905e05051575f6b365d"
EXPECTED_RUNS = {
    "signed_spec": {40526758183, 40526758602, 40526758230},
    "prior_review": {40522786309, 40522785825, 40522798957, 40522799018},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_sources(check_git=False):
    manifest = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
    require(manifest["schema"] == "8141386a/gate1-signed-followup-source/1", "source schema")
    values = {}
    for entry in manifest["sources"]:
        require(entry["alias"] not in values, "duplicate source alias")
        archive = (HERE / entry["archive"]).read_bytes()
        require(len(archive) == entry["archive_bytes"], "archive size: " + entry["alias"])
        require(sha256(archive) == entry["archive_sha256"], "archive hash: " + entry["alias"])
        raw = gzip.decompress(archive)
        require(len(raw) == entry["bytes"] and sha256(raw) == entry["sha256"],
                "source content: " + entry["alias"])
        oid = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        require(oid == entry["git_blob"], "Git blob id: " + entry["alias"])
        if check_git:
            actual = subprocess.check_output(
                ["git", "-c", "gc.auto=0", "show", entry["commit"] + ":" + entry["path"]], cwd=ROOT
            )
            require(actual == raw, "Git source mismatch: " + entry["alias"])
        values[entry["alias"]] = raw
    require(len(values) == 12, "source count")
    return manifest, values


def load_capture():
    data = (HERE / "github-capture.json.gz").read_bytes()
    require(sha256(data) == CAPTURE_SHA256, "GitHub capture hash")
    value = json.loads(gzip.decompress(data))
    require(value["schema"] == "8141386a/gate1-signed-github-capture/1", "GitHub schema")
    return value


def nested_json(raw):
    """Read a captured Git blob that is itself gzip-compressed JSON."""
    return json.loads(gzip.decompress(raw))


def line_for(text, needle):
    hits = [i for i, line in enumerate(text.splitlines(), 1) if needle in line]
    require(len(hits) == 1, "proposal locator: " + needle)
    return hits[0]


def verify_ci(capture, manifest):
    seen = {label: set() for label in EXPECTED_RUNS}
    require(capture["heads"]["signed_spec"] == manifest["spec_cut"], "spec capture head")
    require(capture["heads"]["prior_review"] == manifest["review_cut"], "review capture head")
    runtime_skipped = {}
    for key, record in capture["runs"].items():
        label, run = record["head_label"], record["run"]
        require(label in seen and int(key) == run["id"], "run id/label")
        require(run["head_sha"] == capture["heads"][label], "run head")
        require(run["status"] == "completed" and run["conclusion"] == "success", "run status")
        require(record["jobs"]["total_count"] == len(record["jobs"]["jobs"]), "job pagination")
        for job in record["jobs"]["jobs"]:
            require(job["status"] == "completed" and job["conclusion"] == "success", "job status")
        if run["name"] == "runtime-probe":
            names = {step["name"]: step["conclusion"] for job in record["jobs"]["jobs"]
                     for step in job.get("steps", [])}
            for name in ("Start session", "Scenario taps", "Probe game state"):
                require(names.get(name) == "skipped", "device step was not recorded skipped: " + name)
            runtime_skipped[label] = ["Start session", "Scenario taps", "Probe game state"]
        seen[label].add(int(key))
    require(seen == EXPECTED_RUNS and set(runtime_skipped) == set(EXPECTED_RUNS), "expected CI runs")
    return {"run_ids": {label: sorted(ids) for label, ids in seen.items()},
            "status": "completed/success", "runtime_steps_skipped": runtime_skipped,
            "meaning": "Workflow success is not device measurement or user approval."}


def derive(manifest, values, capture):
    proposal = values["signed_proposal"].decode("utf-8")
    before = values["pre_signoff_proposal"].decode("utf-8")
    closure = values["closure"].decode("utf-8")
    readiness = values["readiness"].decode("utf-8")
    registry, audit = nested_json(values["registry"]), nested_json(values["audit"])
    shop = nested_json(values["shop_defaults"])
    prior = json.loads(values["prior_result"])
    rows = {row["n"]: row for row in registry["ledger"]}
    audit_rows = {row["n"]: row for row in audit["items"]}
    require(len(rows) == 32 and len(audit_rows) == 56, "registry/audit counts")
    require(registry["totals"]["closed"] == 23 and registry["totals"]["note"] == 1,
            "partition closed/note")
    require(registry["totals"]["by_label"] == {"missing-input": 3, "policy": 2,
            "runtime-gated→USER": 20, "served": 7}, "partition by label")
    require(registry["not_in_ledger"]["note_items"] == [56] and audit_rows[56]["verdict"] == "NOTE",
            "NOTE must be item 56")
    require(rows[52]["label"] == "policy" and audit_rows[52]["verdict"] == "OPEN", "item 52")
    require("Item 52 — CONFLICTING" in closure, "item 52 disposition")
    require(all(rows[n]["label"] == "missing-input" and rows[n]["kind"] == "PIN-RAW"
                for n in (12, 49, 50)), "missing-input classes")
    require("MyLibrary.ToRoman" in rows[12]["step"] and "LanguageManager.GetText" in rows[49]["step"],
            "missing bodies")
    require("0x2AEC9A0/0x2AEC9B0" in rows[50]["step"], "missing path slots")
    require(rows[51]["label"] == "policy" and audit_rows[51]["verdict"] == "OPEN"
            and "try" in rows[51]["step"], "item 51")
    require(shop["shipped"]["MaxStockCount"]["value"] == 10, "constructor stock")
    require(shop["shipped"]["ItemPlayerCost"]["value"] == 50, "constructor player cost")
    require(shop["shipped"]["ItemDroneCost"]["value"] == 30, "constructor drone cost")
    require(len(prior["c1"]["arrays"]) == 6 and "shared" in prior["c1"]["boundary"], "C1 boundary")
    require("SUPERSEDE TOÀN VĂN" in readiness and "139 file asm" in readiness, "bounded scope")

    comments = capture["comments"]
    for cid in (6445013675, 6445060900, 6445094113, 6445109638, 6445403414, 6445539115, 6445556145):
        require(comments[str(cid)]["id"] == cid, "comment id")
    require("51/52 retry" in comments["6445013675"]["body"]
            and "chưa làm" in comments["6445013675"]["body"], "producer 51/52 statement")
    require("CLAIM-182 HỦY" in comments["6445060900"]["body"], "director 182 cancellation")
    require("USER SIGN-OFF" in comments["6445403414"]["body"]
            and "Chốt gate1" in comments["6445403414"]["body"], "director-reported sign-off")

    header = ('> **✅ KẾT QUẢ: USER CHẤT — GATE-1 ĐÓNG (sign-off bằng chat 2026-10-27, lần 147: '
              '"Chốt gate1").**\n'
              '> Phạm vi duyệt = đúng tài liệu này; residuals có chủ tiếp tục được quản theo sổ '
              '(registry-v4 + DONE). Gate-2/3 hồ sơ sẵn (G9–G15 đã chốt), Gate-4 phụ thuộc verifier PASS của M1–M4.\n\n')
    require(header in proposal and proposal.replace(header, "", 1) == before, "proposal diff beyond sign-off")
    require("Chốt gate1" in proposal, "proposal sign-off")
    lines = {
        "note": line_for(proposal, "1 NOTE (item 52"),
        "missing_and_51": line_for(proposal, "missing-input 3 (cần dữ liệu server thật)"),
        "scope": line_for(proposal, "28 hạng mục #1–#28 ĐÓNG"),
        "c1": line_for(proposal, "C1: 149 đúng"),
    }
    require("51 thử join xong" in proposal.splitlines()[lines["missing_and_51"] - 1], "item 51 quote")
    return {
        "schema": "8141386a/gate1-signed-followup-result/1",
        "cut": {"signed_spec": manifest["spec_cut"], "pre_signoff_spec": manifest["pre_signoff_cut"],
                "registry": manifest["registry_cut"], "prior_review": manifest["review_cut"]},
        "source_count": len(values),
        "proposal_sha256": sha256(values["signed_proposal"]),
        "decision": {"state": "director-reported USER SIGN-OFF; Gate-1 closed",
                     "source_comment": 6445403414,
                     "boundary": "Original user chat is not in this capture; the decision is respected, not independently verified or reopened."},
        "findings": [
            {"id": "F1", "label": "CONFLICTING", "proposal_lines": [lines["note"]],
             "observed": "The NOTE parenthetical points at #52; frozen registry NOTE is #56 and #52 is policy/OPEN with CONFLICTING disposition.",
             "partition": "23 closed + 1 NOTE (#56) + 32 ledger = 56; 0 shipped-default is a label count.",
             "source_aliases": ["signed_proposal", "registry", "audit", "closure", "shop_defaults"]},
            {"id": "F2", "label": "CONFLICTING", "proposal_lines": [lines["missing_and_51"]],
             "observed": "Three missing-input rows are not three server payloads: #12/#49 lack pinned code bodies; #50 lacks root-slot binding at v4 cut.",
             "boundary": "This states only v4 cut; no new APK or later-path investigation was performed.",
             "source_aliases": ["signed_proposal", "registry", "audit"]},
            {"id": "F3", "label": "UNKNOWN", "proposal_lines": [lines["missing_and_51"]],
             "observed": "The #51 'join tried and finished' statement has no cited support in the cut reviewed. Producer comment 6445013675 states #51/#52 retry was not done at that earlier time.",
             "boundary": "That comment cannot rule out an unreported later attempt. Director 6445060900 canceled lane 182; no retry is requested.",
             "source_aliases": ["signed_proposal", "registry", "audit"], "comment_ids": [6445013675, 6445060900]},
            {"id": "F4", "label": "INFERRED", "proposal_lines": [lines["scope"], lines["c1"]],
             "observed": "The short summary risks being read more broadly than its evidence; qualify L1/sampled static scope, bounded #27 review, and the shared published C1 token convention.",
             "boundary": "Six C1 joins are reproduced, not proof of token-format semantics, full graph/heap/playback, or runtime.",
             "source_aliases": ["signed_proposal", "readiness", "closure", "prior_result"]},
        ],
        "requested_action": "Owner adds a non-reopening factual correction or supersession; preserve v4 and historical receipts.",
        "runtime": "RUNTIME_UNVERIFIED; device lane remains user-gated.",
        "scope": "Existing published evidence only; no new APK/device/SDK, no Gate-2/3 or ef M1–M4 verification.",
        "ci": verify_ci(capture, manifest),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the deterministic result")
    mode.add_argument("--check", action="store_true", help="compare with the committed result")
    parser.add_argument("--git", action="store_true", help="compare every source with its Git blob")
    args = parser.parse_args()
    manifest, values = load_sources(check_git=args.git)
    result = derive(manifest, values, load_capture())
    encoded = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    path = HERE / "followup-results.json"
    if args.write:
        path.write_bytes(encoded)
    else:
        require(path.read_bytes() == encoded, "committed result differs")
    print(f"PASS: {len(values)} source blobs; 4 bounded findings; prior exact-head CI; result sha256={sha256(encoded)}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print("FAIL:", exc, file=sys.stderr)
        sys.exit(1)
