#!/usr/bin/env python3
"""Re-fix verification for Godot-coder head 3f69db3 (round 2 of role build-spec/verifier).

Reuses `verify_m1m4.py` (schema v2) for the M1–M4 checks and adds the checks this
round needs:

  A. payload invariance   — the fix commit must not change decoded numbers
  B. evidence coverage    — every data document must carry a label from the 6-set
  C. pin integrity        — every `source_sha256` must equal sha256(bytes at the
                            commit cited in `source`), resolved from git objects
  D. pin staleness        — same file at the peer tip, to spot stale pins
  E. workflow audit       — workflows added by the branch: size, permissions,
                            references to paths that do not exist, branch guards

Usage:
  python3 verify_REFIX.py --new-tree /tmp/newtree --old-tree /tmp/ba_old \
      --canonical /home/user/WindWings-Space-Shooter-game-play \
      --peer-csv-dir /tmp/peercsv --peer-tip 4686d733b --out verify_3f69db3.json

Read-only: it runs `git show` against the canonical repo, never writes there.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_m1m4 as v2  # noqa: E402

SCHEMA = "verify-ef6b75ef-REFIX/v1"
META_KEYS = {"source", "source_sha256", "evidence", "note", "dedup_rule", "limitations"}
LABELS = {"STATIC_CONFIRMED", "RUNTIME_CONFIRMED", "INFERRED", "RUNTIME_UNVERIFIED", "UNKNOWN", "CONFLICTING"}
PIN_RE = re.compile(r"([\w][\w./-]*\.(?:json|jsonl|csv|md|gz|txt))(?: @ ([0-9a-f]{7,40}))?")


def git(canon: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(canon), *args], capture_output=True, check=False).stdout


def strip_meta(obj):
    if isinstance(obj, dict):
        return {k: strip_meta(v) for k, v in obj.items() if k not in META_KEYS}
    if isinstance(obj, list):
        return [strip_meta(x) for x in obj]
    return obj


def check_payload_invariance(old_tree: Path, new_tree: Path) -> dict:
    old_dir, new_dir = old_tree / "game/data", new_tree / "game/data"
    changed, missing = [], []
    for f in sorted(new_dir.glob("*.json")):
        if not (old_dir / f.name).exists():
            missing.append(f.name)
            continue
        before = strip_meta(json.loads((old_dir / f.name).read_text()))
        after = strip_meta(json.loads(f.read_text()))
        if before != after:
            keys = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
            changed.append({"file": f.name, "differing_top_keys": keys[:8]})
    return {"status": "PASS" if not changed and not missing else "FAIL",
            "files_compared": len(list(new_dir.glob("*.json"))),
            "payload_changed": changed, "only_in_new": missing}


def check_evidence(new_tree: Path) -> dict:
    rows = []
    for f in sorted((new_tree / "game/data").glob("*.json")):
        doc = json.loads(f.read_text())
        label = doc.get("evidence")
        rows.append({"file": f.name, "evidence": label, "valid": label in LABELS})
    bad = [r["file"] for r in rows if not r["valid"]]
    return {"status": "PASS" if not bad else "FAIL", "labelled": len(rows) - len(bad),
            "total": len(rows), "unlabelled": bad, "rows": rows}


def check_pins(canon: Path, new_tree: Path, peer_tip: str) -> dict:
    results = []
    for f in sorted((new_tree / "game/data").glob("*.json")):
        doc = json.loads(f.read_text())
        source, pinned = doc.get("source"), doc.get("source_sha256")
        entry = {"file": f.name, "source": source, "pinned": pinned, "resolved": None,
                 "commit": None, "match": None, "stale_at_peer_tip": None}
        if not source or not pinned:
            entry["status"] = "no-pin"
            results.append(entry)
            continue
        m = PIN_RE.search(source)
        if not m:
            entry["status"] = "unparseable-source"
            results.append(entry)
            continue
        path, commit = m.group(1), m.group(2) or peer_tip
        entry["commit"] = commit
        blob = git(canon, "show", f"{commit}:{path}")
        if not blob:
            entry["status"] = "source-missing"
            results.append(entry)
            continue
        digest = __import__("hashlib").sha256(blob).hexdigest()
        entry["resolved"] = digest
        entry["match"] = digest == pinned
        blob_tip = git(canon, "show", f"{peer_tip}:{path}")
        entry["stale_at_peer_tip"] = bool(blob_tip) and __import__("hashlib").sha256(blob_tip).hexdigest() != digest
        entry["status"] = "ok" if entry["match"] else "mismatch"
        results.append(entry)
    checked = [r for r in results if r["commit"]]
    bad = [r["file"] for r in checked if not r["match"]]
    return {"status": "PASS" if not bad else "FAIL", "pins_checked": len(checked),
            "mismatched": bad, "stale": [r["file"] for r in checked if r["stale_at_peer_tip"]],
            "rows": results, "peer_tip": peer_tip}


def check_workflows(canon: Path, new_tree: Path, branch_head: str) -> dict:
    base = git(canon, "merge-base", branch_head, "origin/main").decode().strip() or "origin/main"
    names = [p.name for p in sorted((new_tree / ".github/workflows").glob("*.yml"))]
    added = []
    for name in names:
        in_base = bool(git(canon, "cat-file", "-e", f"{base}:.github/workflows/{name}"))
        if in_base:
            continue
        text = (new_tree / ".github/workflows" / name).read_text()
        perms = re.findall(r"^\s{2}(contents|pull-requests|issues|actions|id-token|packages):\s*(\S+)",
                           text, re.M)
        refs = sorted(set(re.findall(r"(?:\./)?((?:runtime-probe|tools|tests)/[\w./-]+\.(?:py|cs|jar|sh|yml))", text)))
        missing = [r for r in refs if not (new_tree / r).exists()]
        guards = re.findall(r'GITHUB_REF_NAME"?\s*=\s*[\'"]([^\'"]+)', text)
        added.append({
            "workflow": name, "lines": text.count("\n") + 1,
            "triggers": sorted(set(re.findall(r"^  (\w[\w_]*):", text, re.M))),
            "write_permissions": [f"{k}:{v}" for k, v in perms if v in ("write",)],
            "paths_referenced": refs, "paths_missing_on_branch": missing,
            "branch_guards": guards,
        })
    total_lines = sum(w["lines"] for w in added)
    risky = [w["workflow"] for w in added if w["write_permissions"]]
    dead = [w["workflow"] for w in added if w["paths_missing_on_branch"]]
    guarded = [w["workflow"] for w in added if w["branch_guards"]]
    return {
        "status": "REVIEW" if (len(added) > 1 or risky or dead) else "PASS",
        "merge_base": base, "added": added, "added_count": len(added), "added_lines": total_lines,
        "with_write_permissions": risky, "referencing_missing_paths": dead,
        "with_branch_guards": guarded,
        "godot_workflow": next((w["workflow"] for w in added if "godot" in w["workflow"]), None),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--new-tree", required=True)
    ap.add_argument("--old-tree", required=True)
    ap.add_argument("--canonical", required=True)
    ap.add_argument("--peer-csv-dir", required=True)
    ap.add_argument("--peer-tip", required=True)
    ap.add_argument("--head", required=True, help="branch head sha being verified")
    ap.add_argument("--out", default="verify_REFIX.json")
    args = ap.parse_args()

    new_tree, old_tree, canon = Path(args.new_tree), Path(args.old_tree), Path(args.canonical)

    # 1. re-run the v2 M1–M4 suite against the new tree
    v2_out = Path(args.out).with_name("verify_m1m4_at_head.json")
    argv = ["verify_m1m4.py", "--target", str(new_tree), "--canonical", str(canon),
            "--peer-csv-dir", args.peer_csv_dir, "--out", str(v2_out)]
    saved, sys.argv = sys.argv, argv
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            v2.main()
    finally:
        sys.argv = saved
    baseline = json.loads(v2_out.read_text())

    receipts = {
        "schema": SCHEMA,
        "verified_head": args.head,
        "previous_verified_head": "63361095371e9bd0aa86f32910b3aa89d63ad7e8",
        "tool": {"name": "verify_REFIX.py", "reused": "verify_m1m4.py (schema v2)",
                 "parser": baseline["tool"]["parser"]},
        "baseline_v2_summary": baseline["summary"],
        "baseline_v2_receipt": str(v2_out.name),
        "checks": {
            "A_payload_invariance": check_payload_invariance(old_tree, new_tree),
            "B_evidence_coverage": check_evidence(new_tree),
            "C_pin_integrity": check_pins(canon, new_tree, args.peer_tip),
            "E_workflow_audit": check_workflows(canon, new_tree, args.head),
        },
    }
    receipts["summary"] = {**baseline["summary"],
                           **{k: v.get("status") for k, v in receipts["checks"].items()}}
    Path(args.out).write_text(json.dumps(receipts, indent=1, sort_keys=True) + "\n")
    print(json.dumps(receipts["summary"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
