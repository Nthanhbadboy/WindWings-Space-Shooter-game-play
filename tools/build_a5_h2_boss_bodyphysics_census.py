#!/usr/bin/env python3
"""Build a static-only, serialized census of Boss_BodyPhysics records.

This receipt deliberately does not bind the serialized field names to runtime
semantics or to the 19 boss-damage Director classes: no assembly is available
for that lane, and prefab-root joins are not a Director-class crosswalk.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datas/l3_a5_h2_boss_bodyphysics_serialized_census.json"

INPUTS = {
    "component_csv": {
        "path": "reverse-engineering/scriptableobjects/Boss_BodyPhysics.csv",
        "sha256": "412145bcfe9f250748347c93bfc5cb52dc665d16670bc66ac79151899b465a8d",
    },
    "typetree_jsonl_gzip": {
        "path": "reverse-engineering/raw/typetrees/Boss_BodyPhysics.jsonl.gz",
        "sha256": "e34c3b0c22922d8cda3b09c661d9085ad48888c24fb099d8c13a8154c5d2922c",
    },
    "serialized_prefab_join_gzip": {
        "path": "datas/prefab_joins.csv.gz",
        "sha256": "b8d136d8bb5a65dce02b164a7881cfd1366274cabff9001eef505a7b56647275",
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def as_number(value: str) -> int | float:
    number = float(value)
    return int(number) if number.is_integer() else number


def histogram(values: list[int | float]) -> list[dict[str, int | float]]:
    counts = Counter(values)
    return [{"value": value, "count": counts[value]} for value in sorted(counts)]


def build_receipt() -> dict:
    for item in INPUTS.values():
        path = ROOT / item["path"]
        actual = sha256(path)
        if actual != item["sha256"]:
            raise SystemExit(f"source hash mismatch: {item['path']}: {actual}")
        item["bytes"] = path.stat().st_size

    with (ROOT / INPUTS["component_csv"]["path"]).open(newline="", encoding="utf-8") as stream:
        csv_rows = list(csv.DictReader(stream))
    with gzip.open(ROOT / INPUTS["typetree_jsonl_gzip"]["path"], "rt", encoding="utf-8") as stream:
        typed_rows = [json.loads(line) for line in stream if line.strip()]
    with gzip.open(ROOT / INPUTS["serialized_prefab_join_gzip"]["path"], "rt", newline="", encoding="utf-8") as stream:
        joins = [row for row in csv.DictReader(stream) if row["class"] == "Boss_BodyPhysics"]

    typed_by_id = {str(row["path_id"]): row for row in typed_rows}
    join_by_id = {row["component_path_id"]: row for row in joins}
    csv_ids = [row["path_id"] for row in csv_rows]
    if len(csv_rows) != 251 or len(set(csv_ids)) != 251:
        raise SystemExit(f"expected 251 unique component CSV rows, got {len(csv_rows)}")
    if set(csv_ids) != set(typed_by_id) or len(typed_by_id) != 251:
        raise SystemExit("component CSV and TypeTree path_id sets differ")
    if set(csv_ids) != set(join_by_id) or len(join_by_id) != 251:
        raise SystemExit("component CSV and serialized prefab-join path_id sets differ")

    records = []
    first_values: list[int | float] = []
    per_sec_values: list[int | float] = []
    field_match_counts = Counter()
    roots: Counter[str] = Counter()
    for row in csv_rows:
        path_id = row["path_id"]
        typed = typed_by_id[path_id]
        tree = typed["tree"]
        check_fields = {
            "dmgFirst": as_number(row["dmgFirst"]) == tree["dmgFirst"],
            "dmgPerSec": as_number(row["dmgPerSec"]) == tree["dmgPerSec"],
            "isTrigger": (row["isTrigger"].lower() == "true") == bool(tree["isTrigger"]),
            "isFirstTrigger": (row["isFirstTrigger"].lower() == "true") == bool(tree["isFirstTrigger"]),
            "layerMask.m_Mask": int(row["layerMask.m_Mask"]) == tree["layerMask"]["m_Mask"],
            "m_Enabled": int(row["m_Enabled"]) == tree["m_Enabled"],
        }
        if not all(check_fields.values()):
            raise SystemExit(f"CSV/TypeTree field mismatch for path_id {path_id}: {check_fields}")
        field_match_counts.update(key for key, matched in check_fields.items() if matched)

        join = join_by_id[path_id]
        if join["field"] != "m_GameObject":
            raise SystemExit(f"unexpected prefab join field for {path_id}: {join['field']}")
        root = join["prefab_root"]
        roots[root] += 1
        dmg_first = as_number(row["dmgFirst"])
        dmg_per_sec = as_number(row["dmgPerSec"])
        first_values.append(dmg_first)
        per_sec_values.append(dmg_per_sec)
        records.append({
            "path_id": int(path_id),
            "prefab_root_label": root,
            "serialized_gameobject_path": row["_gameobject"],
            "dmgFirst": dmg_first,
            "dmgPerSec": dmg_per_sec,
            "isFirstTrigger": row["isFirstTrigger"].lower() == "true",
            "isTrigger": row["isTrigger"].lower() == "true",
            "layerMask.m_Mask": int(row["layerMask.m_Mask"]),
            "m_Enabled": int(row["m_Enabled"]),
        })

    pair_counts = Counter((row["dmgFirst"], row["dmgPerSec"]) for row in records)
    receipt = {
        "schema": "a5-h2-boss-bodyphysics-serialized-census-v1",
        "evidence_level": "B",
        "evidence_scope": "STATIC_SERIALIZED_ONLY",
        "assembly_available": False,
        "semantics_status": "NOT_BOUND",
        "requested_boss_damage_class_count": 19,
        "boss_damage_class_assignment_status": "NOT_BOUND",
        "boss_damage_classes_assigned": 0,
        "unassigned_component_instances": len(records),
        "class_assignment_limit": (
            "The available serialized prefab join resolves component PPtrs to 61 root labels, including shared UI roots; "
            "it does not uniquely crosswalk all component rows to the 19 boss-damage Director classes. "
            "No assembly consumer was available or consulted."
        ),
        "inputs": INPUTS,
        "crosschecks": {
            "component_csv_rows": len(csv_rows),
            "typetree_records": len(typed_rows),
            "serialized_prefab_join_rows": len(joins),
            "csv_typetree_path_id_sets_equal": True,
            "csv_prefab_join_path_id_sets_equal": True,
            "rows_matching_all_serialized_fields": len(records),
            "field_match_counts": dict(sorted(field_match_counts.items())),
        },
        "summary": {
            "instances": len(records),
            "distinct_dmgFirst_values": len(set(first_values)),
            "dmgFirst_distribution": histogram(first_values),
            "dmgFirst_min": min(first_values),
            "dmgFirst_median": sorted(first_values)[len(first_values) // 2],
            "dmgFirst_max": max(first_values),
            "distinct_dmgPerSec_values": len(set(per_sec_values)),
            "dmgPerSec_distribution": histogram(per_sec_values),
            "dmgPerSec_min": min(per_sec_values),
            "dmgPerSec_median": sorted(per_sec_values)[len(per_sec_values) // 2],
            "dmgPerSec_max": max(per_sec_values),
            "distinct_serialized_value_pairs": len(pair_counts),
            "value_pair_distribution": [
                {"dmgFirst": first, "dmgPerSec": per_sec, "count": count}
                for (first, per_sec), count in sorted(pair_counts.items())
            ],
            "isFirstTrigger_true": sum(row["isFirstTrigger"] for row in records),
            "isFirstTrigger_false": sum(not row["isFirstTrigger"] for row in records),
            "isTrigger_true": sum(row["isTrigger"] for row in records),
            "isTrigger_false": sum(not row["isTrigger"] for row in records),
            "layerMask_m_Mask_distribution": histogram([row["layerMask.m_Mask"] for row in records]),
            "m_Enabled_distribution": histogram([row["m_Enabled"] for row in records]),
            "distinct_prefab_root_labels": len(roots),
            "prefab_root_label_counts": [
                {"prefab_root_label": root, "count": count}
                for root, count in sorted(roots.items())
            ],
        },
        "records": records,
        "limitations": [
            "Serialized field names and values are reported without claiming runtime behavior or trigger/ damage semantics.",
            "The 19-class Director crosswalk is NOT_BOUND; do not allocate these 251 rows to those classes from root-label co-occurrence.",
            "No assembly semantics, callback behavior, runtime readback, or parity is claimed.",
            "Prefab root labels are serialized-join metadata, not inferred asset roles.",
        ],
    }
    return receipt


def main() -> None:
    receipt = build_receipt()
    OUT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = receipt["summary"]
    print(
        f"{OUT.relative_to(ROOT)}: {summary['instances']} rows; "
        f"{summary['distinct_dmgFirst_values']} dmgFirst values; "
        f"{summary['distinct_dmgPerSec_values']} dmgPerSec values; "
        f"{summary['distinct_prefab_root_labels']} serialized root labels; class semantics NOT_BOUND"
    )


if __name__ == "__main__":
    main()
