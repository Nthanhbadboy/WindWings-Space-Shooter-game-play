#!/usr/bin/env python3
"""Pin the bounded serialized-export surface relevant to the D5 residual.

Static serialized data only. This deliberately does not inspect methods, native/FDE
artifacts, runtime state, or infer global absence from incomplete exports.
"""
from __future__ import annotations

import ast
import csv
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datas/l3_a5_d5_residual_serialized_coverage.json"
SO_DIR = ROOT / "reverse-engineering/scriptableobjects"
TT_DIR = ROOT / "reverse-engineering/raw/typetrees"
CLASS_INVENTORY = ROOT / "docs/apk-analysis/class-inventory.csv"
GP_CSV = SO_DIR / "GP_Datas.csv"
GP_TT = TT_DIR / "GP_Datas.jsonl.gz"

PINS = {
    "scriptableobject_csv_set": {
        "count": 126,
        "bytes": 5115187,
        "manifest_sha256": "2ccc90ddd13b8ee104d6fe3334dab26ebf5e58c5cbbaafb4b6c44e3122a9ebe2",
    },
    "serialized_typetree_jsonl_set": {
        "count": 140,
        "bytes": 3625299,
        "manifest_sha256": "36adee77c37556e2b55a4198e2249f0d5e68187b654d39c479d5c8de3c143f44",
    },
    "class_inventory_sha256": "a4d22195934a765397dc8967b430ba038c9345a411e4561c2aff4c387ad79010",
    "gp_datas_csv_sha256": "7fe242bda781d1e30b27c0a39518625b5282ed18073cca96da79d56d32d9bb43",
    "gp_datas_typetree_sha256": "9cf367e2ebd5015bee65e2fad4af7d47a9df71538d16ca8825a25e14f7ec1471",
}
EXTRA_LIFE_FIELDS = ("countReborn", "rebornNow", "maxCountReborn", "listRebornUseItems")
TARGET_CLASSES = {"Player_Health", "Player_Controller"}
ATTACK_RE = re.compile(r"^Player_Attack_\d+$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inventory_manifest(paths: list[Path]) -> dict:
    lines = []
    total_bytes = 0
    for path in sorted(paths):
        size = path.stat().st_size
        total_bytes += size
        lines.append(f"{path.relative_to(ROOT).as_posix()}\t{size}\t{sha256_file(path)}")
    digest = sha256_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    return {"count": len(paths), "bytes": total_bytes, "manifest_sha256": digest}


def parse_csv_scalar(value: str):
    if value == "":
        return ""
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


def flatten(value, prefix="") -> dict[str, object]:
    out = {}
    if isinstance(value, dict):
        for key, child in value.items():
            name = f"{prefix}.{key}" if prefix else str(key)
            out.update(flatten(child, name))
    else:
        out[prefix] = value
    return out


def walk_exact_keys(value, names: set[str], prefix="") -> list[dict]:
    hits = []
    if isinstance(value, dict):
        for key, child in value.items():
            name = f"{prefix}.{key}" if prefix else str(key)
            if key in names:
                hits.append({"key": key, "path": name})
            hits.extend(walk_exact_keys(child, names, name))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(walk_exact_keys(child, names, f"{prefix}[{index}]"))
    return hits


def walk_pptr_path(value, target_path_id: int, prefix="") -> list[dict]:
    hits = []
    if isinstance(value, dict):
        if value.get("m_PathID") == target_path_id:
            hits.append({
                "field": prefix,
                "file_id": value.get("m_FileID"),
                "path_id": value.get("m_PathID"),
            })
        for key, child in value.items():
            name = f"{prefix}.{key}" if prefix else str(key)
            hits.extend(walk_pptr_path(child, target_path_id, name))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(walk_pptr_path(child, target_path_id, f"{prefix}[{index}]"))
    return hits


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def build_receipt() -> dict:
    so_files = sorted(SO_DIR.glob("*.csv"))
    tt_files = sorted(TT_DIR.glob("*.jsonl.gz"))
    so_manifest = inventory_manifest(so_files)
    tt_manifest = inventory_manifest(tt_files)
    if so_manifest != PINS["scriptableobject_csv_set"]:
        raise SystemExit(f"ScriptableObject export-set pin mismatch: {so_manifest}")
    if tt_manifest != PINS["serialized_typetree_jsonl_set"]:
        raise SystemExit(f"TypeTree JSONL export-set pin mismatch: {tt_manifest}")
    if sha256_file(CLASS_INVENTORY) != PINS["class_inventory_sha256"]:
        raise SystemExit("class inventory pin mismatch")
    if sha256_file(GP_CSV) != PINS["gp_datas_csv_sha256"]:
        raise SystemExit("GP_Datas CSV pin mismatch")
    if sha256_file(GP_TT) != PINS["gp_datas_typetree_sha256"]:
        raise SystemExit("GP_Datas TypeTree pin mismatch")

    with CLASS_INVENTORY.open(newline="", encoding="utf-8") as stream:
        inventory = list(csv.DictReader(stream))
    class_names = {row["class"] for row in inventory}
    attack_classes = sorted(name for name in class_names if ATTACK_RE.fullmatch(name))
    if len(attack_classes) != 24 or not TARGET_CLASSES.issubset(class_names):
        raise SystemExit("expected Player_Attack_1..24, Player_Health, Player_Controller in class inventory")

    target_csv_files = []
    pptr_2625_edges = []
    rows_with_local_path_id_2625 = []
    csv_extra_life_key_hits = []
    for path in so_files:
        headers, rows = load_csv(path)
        base_name = path.name[:-4]
        if ATTACK_RE.fullmatch(base_name) or base_name in TARGET_CLASSES:
            target_csv_files.append(path.relative_to(ROOT).as_posix())
        for field in headers:
            key = field.rsplit(".", 1)[-1]
            if key in EXTRA_LIFE_FIELDS:
                csv_extra_life_key_hits.append({"file": path.relative_to(ROOT).as_posix(), "field": field})
        for row in rows:
            if row.get("path_id", "").strip() == "2625":
                rows_with_local_path_id_2625.append({
                    "file": path.relative_to(ROOT).as_posix(),
                    "path_id": 2625,
                    "gameobject": row.get("_gameobject", ""),
                })
            for path_field in (name for name in headers if name.endswith(".m_PathID")):
                if row.get(path_field, "").strip() == "2625":
                    prefix = path_field[:-len("m_PathID")]
                    pptr_2625_edges.append({
                        "file": path.relative_to(ROOT).as_posix(),
                        "row_path_id": int(row["path_id"]) if row.get("path_id", "").isdigit() else row.get("path_id"),
                        "row_gameobject": row.get("_gameobject", ""),
                        "field": path_field,
                        "file_id": int(row[prefix + "m_FileID"]) if row.get(prefix + "m_FileID", "").isdigit() else row.get(prefix + "m_FileID"),
                        "path_id": 2625,
                    })

    typetree_target_files = []
    typetree_records = 0
    typetree_extra_life_key_hits = []
    typetree_rows_path_id_2625 = []
    typetree_pptr_2625_edges = []
    gp_records = []
    for path in tt_files:
        base_name = path.name[:-len(".jsonl.gz")]
        if ATTACK_RE.fullmatch(base_name) or base_name in TARGET_CLASSES:
            typetree_target_files.append(path.relative_to(ROOT).as_posix())
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                record = json.loads(line)
                typetree_records += 1
                exact_hits = walk_exact_keys(record, set(EXTRA_LIFE_FIELDS))
                if exact_hits:
                    typetree_extra_life_key_hits.append({
                        "file": path.relative_to(ROOT).as_posix(),
                        "line": line_number,
                        "path_id": record.get("path_id"),
                        "keys": exact_hits,
                    })
                if record.get("path_id") == 2625:
                    typetree_rows_path_id_2625.append({
                        "file": path.relative_to(ROOT).as_posix(),
                        "path_id": 2625,
                        "gameobject": record.get("gameobject", ""),
                    })
                for edge in walk_pptr_path(record.get("tree", {}), 2625):
                    typetree_pptr_2625_edges.append({
                        "file": path.relative_to(ROOT).as_posix(),
                        "row_path_id": record.get("path_id"),
                        "row_gameobject": record.get("gameobject", ""),
                        **edge,
                    })
                if path == GP_TT:
                    gp_records.append(record)

    gp_headers, gp_csv_rows = load_csv(GP_CSV)
    if len(gp_records) != 1 or len(gp_csv_rows) != 1:
        raise SystemExit("expected one GP_Datas serialized row in each pinned representation")
    gp_tree = gp_records[0]
    flat_tree = flatten(gp_tree.get("tree", {}))
    gp_diffs = []
    for field in gp_headers:
        if field == "path_id":
            csv_value = parse_csv_scalar(gp_csv_rows[0][field])
            tree_value = gp_tree.get("path_id")
        elif field == "_gameobject":
            csv_value = gp_csv_rows[0][field]
            tree_value = gp_tree.get("gameobject")
        else:
            csv_value = parse_csv_scalar(gp_csv_rows[0][field])
            tree_value = flat_tree.get(field)
        if csv_value != tree_value:
            gp_diffs.append({"field": field, "csv_value": csv_value, "typetree_value": tree_value})

    return {
        "schema": "a5-d5-residual-serialized-coverage-v1",
        "status": "BOUNDED_EXPORT_COVERAGE_PLAYER_OWNER_AND_EXTRA_LIFE_NOT_BOUND",
        "evidence_scope": "CAPTURED_SCRIPTABLEOBJECT_CSV_AND_SERIALIZED_TYPETREE_JSONL_ONLY",
        "evidence_level": "B",
        "runtime_or_dps_measured": False,
        "sources": {
            "scriptableobject_csv_set": so_manifest,
            "serialized_typetree_jsonl_set": tt_manifest,
            "class_inventory": {
                "path": CLASS_INVENTORY.relative_to(ROOT).as_posix(),
                "sha256": PINS["class_inventory_sha256"],
                "bytes": CLASS_INVENTORY.stat().st_size,
            },
            "gp_datas_csv": {
                "path": GP_CSV.relative_to(ROOT).as_posix(),
                "sha256": PINS["gp_datas_csv_sha256"],
                "bytes": GP_CSV.stat().st_size,
            },
            "gp_datas_typetree": {
                "path": GP_TT.relative_to(ROOT).as_posix(),
                "sha256": PINS["gp_datas_typetree_sha256"],
                "bytes": GP_TT.stat().st_size,
            },
        },
        "class_inventory_boundary": {
            "player_attack_class_identities": len(attack_classes),
            "player_health_class_identity_present": "Player_Health" in class_names,
            "player_controller_class_identity_present": "Player_Controller" in class_names,
            "warning": "class-inventory identities/counts are not serialized owner records",
        },
        "export_coverage": {
            "scriptableobject_csv_files": len(so_files),
            "typetree_jsonl_files": len(tt_files),
            "typetree_jsonl_records_scanned": typetree_records,
            "player_target_csv_files": target_csv_files,
            "player_target_typetree_files": typetree_target_files,
            "gp_datas_csv_rows": len(gp_csv_rows),
            "gp_datas_typetree_rows": len(gp_records),
            "exact_extra_life_fields_checked": list(EXTRA_LIFE_FIELDS),
            "exact_extra_life_csv_header_hits": csv_extra_life_key_hits,
            "exact_extra_life_typetree_key_hits": typetree_extra_life_key_hits,
        },
        "gp_datas_pointer_boundary": {
            "serialized_row_path_id": int(gp_csv_rows[0]["path_id"]),
            "gameobject": gp_csv_rows[0]["_gameobject"],
            "player_pointer": {
                "file_id": int(gp_csv_rows[0]["player.m_FileID"]),
                "path_id": int(gp_csv_rows[0]["player.m_PathID"]),
            },
            "scriptableobject_csv_pptr_edges_to_path_id_2625": pptr_2625_edges,
            "typetree_jsonl_pptr_edges_to_path_id_2625": typetree_pptr_2625_edges,
            "export_rows_whose_own_path_id_is_2625": rows_with_local_path_id_2625,
            "typetree_rows_whose_own_path_id_is_2625": typetree_rows_path_id_2625,
            "interpretation": (
                "Two TypeTree records encode the numeric PPtr pair 0:2625 (GP_Datas.player and GP_Tutorials.player); "
                "the flat CSV set contains the GP_Datas edge. The class-split exports do not preserve enough source-file "
                "context to assert these are the same target object. The same number appears as an own-row ID in "
                "Box_Rewards exports, which is not a PPtr target join. No Player_Attack/Player_Health/Player_Controller "
                "owner row is present in these captured exports."
            ),
            "owner_join": "NOT_BOUND_WITHIN_CAPTURED_EXPORTS",
        },
        "gp_datas_cross_export_consistency": {
            "row_identity": {"path_id": int(gp_tree["path_id"]), "gameobject": gp_tree["gameobject"]},
            "flat_csv_vs_typetree_field_differences": gp_diffs,
            "extra_life_serialized_rewire": "NOT_BOUND",
            "warning": "Differences are reported as extraction/export evidence only; no runtime meaning inferred.",
        },
        "limitations": [
            "The scan is bounded to the pinned exported CSV and TypeTree JSONL sets; it is not a whole-build absence proof.",
            "The class inventory proves class-name presence, not prefab/component ownership or serialized field values.",
            "Path IDs are file-local; the class-split exports do not preserve source-asset context for fileID=0, so do not assert the GP_Datas and GP_Tutorials pointers share a target or join Box_Rewards own-row 2625.",
            "The GP_Datas CSV and TypeTree render one list field differently; do not choose a representation as runtime truth.",
            "No coroutine/receiver inventory was repeated; reports 79–86 remain prior evidence only.",
            "No code body, native/FDE artifact, emulator, runtime probe, or secret was read or used.",
        ],
    }


def main() -> None:
    receipt = build_receipt()
    OUT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    coverage = receipt["export_coverage"]
    pptr = receipt["gp_datas_pointer_boundary"]
    diffs = receipt["gp_datas_cross_export_consistency"]["flat_csv_vs_typetree_field_differences"]
    print(
        f"{OUT.relative_to(ROOT)}: {coverage['scriptableobject_csv_files']} CSV + "
        f"{coverage['typetree_jsonl_files']} TypeTree files / {coverage['typetree_jsonl_records_scanned']} rows; "
        f"target owner NOT_BOUND; PPtr edges CSV/TypeTree="
        f"{len(pptr['scriptableobject_csv_pptr_edges_to_path_id_2625'])}/"
        f"{len(pptr['typetree_jsonl_pptr_edges_to_path_id_2625'])}; "
        f"GP_Datas field diffs={len(diffs)}"
    )


if __name__ == "__main__":
    main()
