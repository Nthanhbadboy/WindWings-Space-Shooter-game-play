#!/usr/bin/env python3
"""M5 verifier — multi-wave loader, checked against the published anchor.

Role build-spec/verifier (ef6b75ef). Never edits the coder tree, never runs Godot.

What it can prove without an engine:
  M5.1 payload present in the coder tree (else NOT_DELIVERED, no guessing)
  M5.2 282/282 waves, same names AND same order as datas/waves.json
  M5.3 per-wave counters equal to anchor_waves.json:per_wave (rows, len(enemies),
       copies, spawn events) — one unit off is a FAIL
  M5.4 no empty wave
  M5.5 payload weight (bytes, gzip) vs the 5 MB commit rule
  M5.6 provenance pin: source_sha256 must equal the canonical waves.json sha256
  M5.7 spawn-order replay, only when --trace is supplied (else UNVERIFIABLE)

Usage:
  python3 verify_m5.py --target /tmp/m5tree --canonical . \
      --anchor anchor_waves.json --out verify_m5.json [--trace /tmp/m5trace.jsonl]
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

SCHEMA = "verify-ef6b75ef-m5/v1"
CANDIDATE_GLOBS = ("game/data/*.json", "game/data/**/*.json")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def counters(wave: dict) -> dict:
    sp = wave.get("spawners", [])
    return {
        "spawner_rows": len(sp),
        "sum_len_enemies": sum(len(s.get("enemies", [])) for s in sp),
        "sum_copies": sum(int(s.get("copies", 1)) for s in sp),
        "sum_copies_x_len_enemies": sum(int(s.get("copies", 1)) * len(s.get("enemies", [])) for s in sp),
    }


def find_payload(target: Path) -> tuple[Path | None, str]:
    """Return the first JSON in game/data that holds a multi-wave payload."""
    seen = []
    for pattern in CANDIDATE_GLOBS:
        for p in sorted(target.glob(pattern)):
            if p in seen:
                continue
            seen.append(p)
            try:
                doc = json.loads(p.read_text())
            except Exception:
                continue
            waves = doc.get("waves") if isinstance(doc, dict) else doc
            if isinstance(waves, list) and len(waves) > 1 and all(
                isinstance(w, dict) and "spawners" in w for w in waves[:5]
            ):
                return p, "waves[]"
    return None, f"no multi-wave JSON among {len(seen)} data files"


def row_digest(wave: dict) -> str:
    """Order-sensitive digest of a wave's spawner rows (catches reordering)."""
    sig = [
        [r.get("spawner"), r.get("spawn_type"), int(r.get("copies", 1) or 0),
         [str(e) for e in r.get("enemies", [])]]
        for r in wave.get("spawners", [])
    ]
    return hashlib.sha256(json.dumps(sig, separators=(",", ":")).encode()).hexdigest()[:32]


def replay_order(wave: dict) -> list[str]:
    order = []
    for row in wave.get("spawners", []):
        names = row.get("enemies", [])
        for _ in range(int(row.get("copies", 1))):
            order.extend(str(n) for n in names)
    return order


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--canonical", required=True)
    ap.add_argument("--anchor", required=True)
    ap.add_argument("--trace", default=None)
    ap.add_argument("--out", default="verify_m5.json")
    args = ap.parse_args()

    target, canon = Path(args.target).resolve(), Path(args.canonical).resolve()
    anchor = json.loads(Path(args.anchor).read_text())
    canonical_sha = anchor["inputs"]["datas/waves.json"]["sha256"]
    canonical_waves = json.loads((canon / "datas/waves.json").read_text())["waves"]
    canon_by_name = {w["wave"]: w for w in canonical_waves}
    anchor_by_name = {r["wave"]: r for r in anchor["per_wave"]}

    receipts: dict = {"schema": SCHEMA, "checks": {}, "anchor_pin": canonical_sha,
                      "tool": {"name": "verify_m5.py", "schema": SCHEMA}}

    payload_path, why = find_payload(target)
    if payload_path is None:
        receipts["checks"]["M5.1_payload"] = {"status": "NOT_DELIVERED", "reason": why}
        receipts["summary"] = {"M5.1_payload": "NOT_DELIVERED"}
        Path(args.out).write_text(json.dumps(receipts, indent=1, sort_keys=True) + "\n")
        print(f"NOT_DELIVERED — {why}")
        return 0

    raw = payload_path.read_bytes()
    doc = json.loads(raw)
    waves = doc.get("waves") if isinstance(doc, dict) else doc
    receipts["payload"] = {
        "path": str(payload_path.relative_to(target)).replace("\\", "/"),
        "bytes": len(raw),
        "gzip_bytes": len(gzip.compress(raw, 9)),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "waves": len(waves),
        "source": doc.get("source") if isinstance(doc, dict) else None,
        "source_sha256": doc.get("source_sha256") if isinstance(doc, dict) else None,
    }
    receipts["checks"]["M5.1_payload"] = {"status": "PASS", "path": receipts["payload"]["path"]}

    names = [w.get("wave") for w in waves]
    receipts["checks"]["M5.2_wave_set"] = {
        "status": "PASS" if names == [w["wave"] for w in canonical_waves] else "FAIL",
        "count": len(names),
        "missing": [n for n in canon_by_name if n not in set(names)][:20],
        "extra": [n for n in names if n not in canon_by_name][:20],
        "order_differs": names != [w["wave"] for w in canonical_waves] and set(names) == set(canon_by_name),
    }

    mismatches, per_wave, order_mismatch = [], {}, []
    for w in waves:
        name = w.get("wave")
        if name in canon_by_name and row_digest(w) != row_digest(canon_by_name[name]):
            order_mismatch.append(name)

    mismatches, per_wave = [], {}
    for w in waves:
        name = w.get("wave")
        if name not in anchor_by_name:
            continue
        got = counters(w)
        want = {k: anchor_by_name[name][k] for k in got}
        per_wave[name] = got
        if got != want:
            mismatches.append({
                "wave": name,
                "got": got,
                "want": want,
                "fields_diff": [k for k in got if got[k] != want[k]],
            })
    totals_got = {k: sum(v[k] for v in per_wave.values()) for k in
                  ("spawner_rows", "sum_len_enemies", "sum_copies", "sum_copies_x_len_enemies")}
    receipts["checks"]["M5.3_per_wave_counters"] = {
        "status": "PASS" if not mismatches and len(per_wave) == len(anchor_by_name) else "FAIL",
        "waves_compared": len(per_wave),
        "mismatches": mismatches[:40],
        "mismatch_count": len(mismatches),
        "totals_got": totals_got,
        "totals_want": {k: anchor["totals"][k] for k in totals_got},
    }

    receipts["checks"]["M5.3b_row_order"] = {
        "status": "PASS" if not order_mismatch else "FAIL",
        "row_digest_mismatch": order_mismatch[:40],
        "mismatch_count": len(order_mismatch),
        "note": "order-sensitive: counts can match while rows are reordered",
    }

    empty = [w.get("wave") for w in waves if not w.get("spawners")]
    receipts["checks"]["M5.4_no_empty_wave"] = {
        "status": "PASS" if not empty and anchor["totals"]["waves_without_spawners"] == 0 else "FAIL",
        "empty_waves": empty,
    }

    over = len(raw) >= 5_000_000
    receipts["checks"]["M5.5_weight"] = {
        "status": "PASS" if not over else "FAIL",
        "bytes": len(raw), "gzip_bytes": receipts["payload"]["gzip_bytes"],
        "commit_rule_bytes": 5_000_000, "over_commit_rule": over,
    }

    pin = receipts["payload"]["source_sha256"]
    receipts["checks"]["M5.6_provenance_pin"] = {
        "status": "PASS" if pin == canonical_sha else "FAIL",
        "declared": pin, "expected": canonical_sha,
        "source": receipts["payload"]["source"],
    }

    if args.trace:
        trace_path = Path(args.trace)
        samples = {}
        for line in trace_path.read_text().splitlines():
            if not line.strip():
                continue
            ev = json.loads(line)
            samples.setdefault(ev.get("wave"), []).append(str(ev.get("enemy")))
        rows = []
        for name, order in samples.items():
            want = replay_order(canon_by_name[name]) if name in canon_by_name else None
            rows.append({"wave": name, "traced": len(order),
                         "expected": len(want) if want is not None else None,
                         "match": want == order if want is not None else None})
        receipts["checks"]["M5.7_replay_order"] = {
            "status": "PASS" if rows and all(r["match"] for r in rows) else "FAIL",
            "waves": rows,
        }
    else:
        receipts["checks"]["M5.7_replay_order"] = {
            "status": "UNVERIFIABLE",
            "reason": "no --trace given; replay order needs a runtime dump (no Godot in sandbox)",
        }

    receipts["summary"] = {k: v.get("status") for k, v in receipts["checks"].items()}
    Path(args.out).write_text(json.dumps(receipts, indent=1, sort_keys=True) + "\n")
    print(json.dumps(receipts["summary"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
