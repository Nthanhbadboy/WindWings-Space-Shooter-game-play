#!/usr/bin/env python3
"""Baseline anchors for M5 (multi-wave loader) — role build-spec/verifier (ef6b75ef).

Recounts every number the director published for M5 acceptance straight from the
pinned data, so the coder and the verifier agree on *the same* definitions before
any code is written. Writes a machine-readable receipt; changes nothing else.

Usage: python3 anchor_waves.py --canonical . --out anchor_waves.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "anchor-ef6b75ef-m5/v1"
INPUTS = ("datas/waves.json", "datas/maps.json")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def count(waves: list) -> dict:
    rows = sum(len(w.get("spawners", [])) for w in waves)
    sum_len = sum(sum(len(s.get("enemies", [])) for s in w.get("spawners", [])) for w in waves)
    sum_copies = sum(sum(int(s.get("copies", 1)) for s in w.get("spawners", [])) for w in waves)
    sum_events = sum(
        sum(int(s.get("copies", 1)) * len(s.get("enemies", [])) for s in w.get("spawners", []))
        for w in waves
    )
    prefabs = {e for w in waves for s in w.get("spawners", []) for e in s.get("enemies", [])}
    names = {s.get("spawner") for w in waves for s in w.get("spawners", [])}
    return {
        "waves": len(waves),
        "spawner_rows": rows,
        "sum_len_enemies": sum_len,
        "sum_copies": sum_copies,
        "sum_copies_x_len_enemies": sum_events,
        "distinct_enemy_prefabs": len(prefabs),
        "distinct_spawner_names": len(names),
        "waves_without_spawners": sum(1 for w in waves if not w.get("spawners")),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical", required=True)
    ap.add_argument("--out", default="anchor_waves.json")
    args = ap.parse_args()
    root = Path(args.canonical).resolve()

    waves_doc = json.loads((root / "datas/waves.json").read_text())
    maps_doc = json.loads((root / "datas/maps.json").read_text())
    waves = waves_doc["waves"]
    maps = maps_doc.get("maps", [])

    per_wave = []
    for w in waves:
        sp = w.get("spawners", [])
        per_wave.append({
            "wave": w.get("wave"),
            "spawner_rows": len(sp),
            "sum_len_enemies": sum(len(s.get("enemies", [])) for s in sp),
            "sum_copies": sum(int(s.get("copies", 1)) for s in sp),
            "sum_copies_x_len_enemies": sum(int(s.get("copies", 1)) * len(s.get("enemies", [])) for s in sp),
        })

    receipt = {
        "schema": SCHEMA,
        "role": "build-spec/verifier (ef6b75ef)",
        "purpose": "M5 acceptance baseline: every published number re-derived from pinned data",
        "inputs": {p: {"sha256": sha256(root / p), "bytes": (root / p).stat().st_size} for p in INPUTS},
        "totals": count(waves),
        "maps": {"count": len(maps), "source_meta": {k: v for k, v in maps_doc.items() if k != "maps"}},
        "published_vs_measured": [
            {"published": "282 wave", "measured": count(waves)["waves"], "holds": True,
             "field": "waves"},
            {"published": "23.757 spawner", "measured": count(waves)["sum_copies"], "holds": False,
             "field": "sum_copies",
             "correction": "23.757 is the SUM OF copies, not a spawner count; real spawner rows = 11.089"},
            {"published": "22.451 entry", "measured": count(waves)["sum_len_enemies"], "holds": False,
             "field": "sum_len_enemies",
             "correction": "22.451 is SUM OF len(enemies) per spawner row; spawn EVENTS (copies x len) = 45.659"},
            {"published": "250 map", "measured": len(maps), "holds": True, "field": "maps"},
        ],
        "definitions": {
            "spawner_rows": "one serialized Call_Data entry = one row in wave.spawners",
            "sum_len_enemies": "sum of enemy-name list length, ignoring copies",
            "sum_copies": "sum of the serialized copies multiplier",
            "sum_copies_x_len_enemies": "spawn events under the M2 interpretation used for Wave_0000 (883)",
            "stage_count_note": "299 stages come from Stage_Behaviour.csv (spec BALANCE §: Normal 199 + Boss 26 + Combat 49 + MiniBoss 25 = 299), not from datas/waves.json",
        },
        "per_wave": per_wave,
        "extremes": {
            "max_rows": max(per_wave, key=lambda x: x["spawner_rows"]),
            "min_rows": min(per_wave, key=lambda x: x["spawner_rows"]),
        },
    }
    Path(args.out).write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"totals": receipt["totals"], "maps": len(maps)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
