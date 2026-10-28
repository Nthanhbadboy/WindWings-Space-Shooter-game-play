#!/usr/bin/env python3
"""Build a bounded D5 class-to-static-array join from already-published data receipts.

This does not inspect or execute game code. It is not a serialized component-owner
join, DPS model, or extra-life behavior proof.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datas/l3_a5_d5_serialized_joins.json"
INPUTS = {
    "class_inventory": {
        "path": "docs/apk-analysis/class-inventory.csv",
        "sha256": "a4d22195934a765397dc8967b430ba038c9345a411e4561c2aff4c387ad79010",
    },
    "player_static_arrays": {
        "path": "datas/player_start_stats.json",
        "sha256": "d336295ae74f7a2a77d043c3119ee5be493a6d04dbd5c57492f1d2bb20b9b566",
    },
    "gp_datas_serialized_csv": {
        "path": "reverse-engineering/scriptableobjects/GP_Datas.csv",
        "sha256": "7fe242bda781d1e30b27c0a39518625b5282ed18073cca96da79d56d32d9bb43",
    },
}
ARRAY_FIELDS = (
    "PlayerCosts",
    "StartMainCannonDamages",
    "StartMainCannonRate",
    "StartWingCannonDamages",
)
EXTRA_LIFE_SERIALIZED_FIELD_NAMES = (
    "countReborn",
    "rebornNow",
    "maxCountReborn",
    "listRebornUseItems",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_receipt() -> dict:
    input_meta = {}
    for name, item in INPUTS.items():
        path = ROOT / item["path"]
        actual = sha256(path)
        if actual != item["sha256"]:
            raise SystemExit(f"source hash mismatch: {item['path']}: {actual}")
        input_meta[name] = {**item, "bytes": path.stat().st_size}

    with (ROOT / INPUTS["class_inventory"]["path"]).open(newline="", encoding="utf-8") as stream:
        inventory_rows = list(csv.DictReader(stream))
    attack_rows = {}
    for row in inventory_rows:
        name = row["class"]
        if name.startswith("Player_Attack_"):
            suffix = name.removeprefix("Player_Attack_")
            if not suffix.isdigit():
                raise SystemExit(f"unexpected Player_Attack class name: {name}")
            attack_rows[int(suffix)] = row
    if set(attack_rows) != set(range(1, 25)):
        raise SystemExit(f"expected Player_Attack_1..24 in inventory, got {sorted(attack_rows)}")

    player_stats = json.loads((ROOT / INPUTS["player_static_arrays"]["path"]).read_text(encoding="utf-8"))
    arrays = {row["field"]: row["values"] for row in player_stats["fields"] if row["field"] in ARRAY_FIELDS}
    if set(arrays) != set(ARRAY_FIELDS) or any(len(arrays[name]) != 24 for name in ARRAY_FIELDS):
        raise SystemExit("expected four 24-entry Player_Get_Datas static arrays")
    if not all(row.get("length_valid") is True for row in player_stats["fields"] if row["field"] in ARRAY_FIELDS):
        raise SystemExit("one or more static-array receipts are not length-valid")

    with (ROOT / INPUTS["gp_datas_serialized_csv"]["path"]).open(newline="", encoding="utf-8") as stream:
        gp_rows = list(csv.DictReader(stream))
    player_attack_csv_exports = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "reverse-engineering/scriptableobjects").glob("Player_Attack_*.csv")
    )
    player_attack_typetree_exports = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "reverse-engineering/raw/typetrees").glob("Player_Attack_*.jsonl.gz")
    )
    if len(gp_rows) != 1:
        raise SystemExit(f"expected one captured GP_Datas serialized row, got {len(gp_rows)}")
    gp_fields = list(gp_rows[0])
    absent_extra_life_fields = [name for name in EXTRA_LIFE_SERIALIZED_FIELD_NAMES if name not in gp_fields]

    records = []
    for suffix in range(1, 25):
        row = attack_rows[suffix]
        index = suffix - 1
        records.append({
            "implementation_class": f"Player_Attack_{suffix}",
            "class_inventory_reported_count": int(row["instances"]),
            "static_array_index": index,
            "index_mapping_basis": "Existing published static CFG proof: DATA_SYNC.md §24.14 / report 82; 72/72 getter calls pass N-1.",
            "index_mapping_warning": "Do not derive this index from a source_id or player ID; class source IDs and array indices are distinct concepts.",
            "static_array_values": {name: arrays[name][index] for name in ARRAY_FIELDS},
            "serialized_component_owner": "NOT_BOUND",
        })

    gp = gp_rows[0]
    return {
        "schema": "a5-d5-static-array-and-serialized-coverage-v1",
        "status": "PARTIAL_STATIC_CLASS_TO_ARRAY_JOIN_NOT_COMPONENT_OR_LIFECYCLE_CLOSURE",
        "evidence_scope": "STATIC_RECEIPTS_AND_SERIALIZED_CSV_ONLY",
        "evidence_level": "B",
        "runtime_or_dps_measured": False,
        "inputs": input_meta,
        "class_to_array_join": {
            "implementation_classes": 24,
            "static_array_rows": 24,
            "joined_rows": len(records),
            "index_rule": "Player_Attack_N → static array element N-1, under the existing cited 72/72 static CFG result.",
            "static_array_source_status": player_stats.get("status"),
            "array_fields": list(ARRAY_FIELDS),
            "records": records,
        },
        "serialized_component_boundary": {
            "player_attack_class_exports_in_scriptableobject_csv": player_attack_csv_exports,
            "player_attack_class_exports_in_typetree": player_attack_typetree_exports,
            "gp_datas_serialized_rows": len(gp_rows),
            "gp_datas_path_id": int(gp["path_id"]),
            "gp_datas_gameobject_path_id": int(gp["m_GameObject.m_PathID"]),
            "gp_datas_player_path_id": int(gp["player.m_PathID"]),
            "gp_datas_fields": gp_fields,
            "extra_life_field_names_checked": list(EXTRA_LIFE_SERIALIZED_FIELD_NAMES),
            "extra_life_field_names_absent_from_gp_datas_export": absent_extra_life_fields,
            "player_component_owner_join": "NOT_BOUND",
            "extra_life_serialized_rewire": "NOT_BOUND_FROM_AVAILABLE_SERIALIZED_EXPORTS",
            "limitation": (
                "The static class-to-array join is not a Unity component-owner join. The one GP_Datas row does not "
                "serialize the checked extra-life fields; no lifecycle or event rewiring is inferred from this absence."
            ),
        },
        "limitations": [
            "This is a bounded class-suffix-to-static-array join, not a producer-to-prefab/component binding.",
            "Static damage/rate values are not converted into shots, hits, DPS, TTK, or runtime parity.",
            "Serialized component ownership for Player_Attack_N and extra-life rewiring remain NOT_BOUND.",
            "The GP_Datas CSV is one exported row, not proof of global absence or runtime state.",
            "No game method body, native/FDE artifact, emulator, runtime probe, or secret was read or used by this builder.",
        ],
    }


def main() -> None:
    receipt = build_receipt()
    OUT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    join = receipt["class_to_array_join"]
    boundary = receipt["serialized_component_boundary"]
    print(
        f"{OUT.relative_to(ROOT)}: {join['joined_rows']}/24 class→array rows; "
        f"GP_Datas serialized rows={boundary['gp_datas_serialized_rows']}; "
        f"component/extra-life joins NOT_BOUND"
    )


if __name__ == "__main__":
    main()
