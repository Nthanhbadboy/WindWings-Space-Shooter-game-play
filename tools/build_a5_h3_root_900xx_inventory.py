#!/usr/bin/env python3
"""Build a static metadata inventory of exact five-digit 900xx roots outside waves roster."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datas/l3_a5_h3_root_900xx_outside_roster.json"
ROOTS_INPUT = {
    "path": "reverse-engineering/raw/typetrees/prefab-roots.csv",
    "sha256": "cd997d3ebf5a6d3bc82131bce443b5541ab722045eb6e11b674627e9d96285a6",
}
WAVES_INPUT = {
    "path": "datas/waves.json",
    "sha256": "dde007618b7cbc83f0702298f7744609f8b25b2d7479ab15964b1fb6fa8abc73",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_receipt() -> dict:
    source_meta = {}
    for key, item in (("prefab_roots", ROOTS_INPUT), ("waves_roster", WAVES_INPUT)):
        path = ROOT / item["path"]
        actual = sha256(path)
        if actual != item["sha256"]:
            raise SystemExit(f"source hash mismatch: {item['path']}: {actual}")
        source_meta[key] = {**item, "bytes": path.stat().st_size}

    with (ROOT / ROOTS_INPUT["path"]).open(newline="", encoding="utf-8") as stream:
        root_rows = list(csv.DictReader(stream))
    waves = json.loads((ROOT / WAVES_INPUT["path"]).read_text(encoding="utf-8"))
    roster = {
        name
        for wave in waves["waves"]
        for spawner in wave["spawners"]
        for name in spawner["enemies"]
    }

    if len(root_rows) != 2081:
        raise SystemExit(f"expected 2081 prefab-root records, got {len(root_rows)}")
    exact = [row for row in root_rows if re.fullmatch(r"900\d{2}", row["name"])]
    prefix = [row for row in root_rows if re.match(r"^900\d\d", row["name"])]
    excluded_prefix = [row for row in prefix if not re.fullmatch(r"900\d{2}", row["name"])]
    if len(exact) != 45 or len(prefix) != 48 or len(excluded_prefix) != 3:
        raise SystemExit(
            f"unexpected 900xx root census: exact={len(exact)} prefix={len(prefix)} excluded={len(excluded_prefix)}"
        )
    exact_names = [row["name"] for row in exact]
    if len(set(exact_names)) != 45:
        raise SystemExit("900xx root names are not unique")
    if any(int(row["gameobject_path_id"]) < 0 or int(row["transform_path_id"]) < 0 for row in exact):
        raise SystemExit("invalid root PPtr metadata")

    records = []
    for row in sorted(exact, key=lambda item: item["name"]):
        name = row["name"]
        if name in roster:
            raise SystemExit(f"exact 900xx root unexpectedly occurs in waves roster: {name}")
        records.append({
            "root_name": name,
            "transform_path_id": int(row["transform_path_id"]),
            "gameobject_path_id": int(row["gameobject_path_id"]),
            "serialized_child_count": int(row["children"]),
            "waves_roster_exact_name_match": False,
            "metadata_identity_status": "ROOT_RECORD_PRESENT",
            "asset_role": "NOT_ASSIGNED",
        })

    excluded = [
        {
            "root_name": row["name"],
            "transform_path_id": int(row["transform_path_id"]),
            "gameobject_path_id": int(row["gameobject_path_id"]),
            "serialized_child_count": int(row["children"]),
            "reason": "prefix match only; not exactly five digits under ^900\\d{2}$",
        }
        for row in sorted(excluded_prefix, key=lambda item: item["name"])
    ]
    roster_misses = [row["root_name"] for row in records if row["metadata_identity_status"] != "ROOT_RECORD_PRESENT"]
    receipt = {
        "schema": "a5-h3-root-900xx-outside-roster-v1",
        "evidence_level": "B",
        "evidence_scope": "STATIC_SERIALIZED_METADATA_ONLY",
        "identity_rule": "exact root name matching ^900\\d{2}$",
        "roster_rule": "exact string membership among waves[].spawners[].enemies[] names in datas/waves.json",
        "inputs": source_meta,
        "summary": {
            "prefab_root_records": len(root_rows),
            "waves_roster_unique_names": len(roster),
            "900xx_prefix_roots": len(prefix),
            "exact_five_digit_900xx_roots": len(records),
            "non_exact_prefix_exclusions": len(excluded),
            "exact_roster_matches": 0,
            "exact_names_outside_roster": len(records),
            "root_metadata_records_present": len(records),
            "bounded_missing_root_metadata": len(roster_misses),
            "children_distribution": [
                {"children": count, "roots": sum(row["serialized_child_count"] == count for row in records)}
                for count in sorted({row["serialized_child_count"] for row in records})
            ],
        },
        "records": records,
        "prefix_only_exclusions": excluded,
        "limitations": [
            "Root names, path IDs, and child counts are metadata identities only; no asset role or gameplay purpose is assigned.",
            "Roster comparison is an exact-name check against the current serialized waves roster, not proof of global non-use.",
            "The receipt does not infer art, hazard, obstacle, projectile, collision, or gameplay behavior from names or child counts.",
            "Component-level or internal asset metadata not present in the pinned root/roster exports remains bounded-missing; this receipt does not fill it by inference.",
            "No runtime, assembly, native/FDE, or AI-1 lane was consulted.",
        ],
    }
    return receipt


def main() -> None:
    receipt = build_receipt()
    OUT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"{OUT.relative_to(ROOT)}: {receipt['summary']['exact_names_outside_roster']} exact roots outside roster; "
        f"{receipt['summary']['bounded_missing_root_metadata']} root metadata missing; roles NOT_ASSIGNED"
    )


if __name__ == "__main__":
    main()
