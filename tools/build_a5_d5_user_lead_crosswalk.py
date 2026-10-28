#!/usr/bin/env python3
"""Build a bounded crosswalk for the user-provided premium/HP/player-data lead.

Reads only pinned serialized CSV/TypeTree exports and published textual receipts.
It does not inspect method bodies, native/FDE artifacts, or runtime state.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datas/l3_a5_d5_user_lead_crosswalk.json"
SO = ROOT / "reverse-engineering/scriptableobjects"
TT = ROOT / "reverse-engineering/raw/typetrees"
INVENTORY = ROOT / "docs/apk-analysis/class-inventory.csv"

EXPORT_SET_PINS = {
    "scriptableobject_csv_count": 126,
    "scriptableobject_csv_bytes": 5115187,
    "scriptableobject_csv_manifest_sha256": "2ccc90ddd13b8ee104d6fe3334dab26ebf5e58c5cbbaafb4b6c44e3122a9ebe2",
    "typetree_jsonl_count": 140,
    "typetree_jsonl_bytes": 3625299,
    "typetree_jsonl_manifest_sha256": "36adee77c37556e2b55a4198e2249f0d5e68187b654d39c479d5c8de3c143f44",
}
FILE_PINS = {
    "reverse-engineering/scriptableobjects/Data_Players.csv": "8fc676d1fb9587e5b90671c6a4ab7e4ec833725af4d1c5280b6a90129b5fcde6",
    "reverse-engineering/raw/typetrees/Data_Players.jsonl.gz": "f77ac09b9e76d325ae05ea2cb989d94243d2ed924901dd4b7002ee31ea7c328b",
    "reverse-engineering/raw/typetrees/Board_Players.jsonl.gz": "b89c197c634a91d70ca85304e3efcc8530b7b0bf0dd76e9092ca1f79f5614923",
    "reverse-engineering/scriptableobjects/Tech_Ability_Data.csv": "8fb10d492f8c455bd726f2328a56183e260f0b4fd67c97af99c16f06bc1f64bd",
    "reverse-engineering/raw/typetrees/Tech_Ability_Data.jsonl.gz": "b13e5e4f1f22379e51fa294d4d3eb05d60e4f1729be8d3c3258c6d1e3933ec94",
    "reverse-engineering/scriptableobjects/IAPProduct.csv": "8c00d9574d636af4ca25975b7053917f95b108373132df3fef349b0fe25badb8",
    "reverse-engineering/raw/typetrees/IAPProduct.jsonl.gz": "cbda15bd8f423fa0a0e49fd17e2e4206edf05b2365d4b4890eeb4cee2363a070",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def manifest(paths: list[Path]) -> dict:
    entries = []
    total = 0
    for p in sorted(paths):
        size = p.stat().st_size
        total += size
        entries.append(f"{p.relative_to(ROOT).as_posix()}\t{size}\t{sha256_file(p)}")
    digest = hashlib.sha256(("\n".join(entries) + "\n").encode()).hexdigest()
    return {"count": len(paths), "bytes": total, "manifest_sha256": digest}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_jsonl_gz(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build() -> dict:
    so_files = sorted(SO.glob("*.csv"))
    tt_files = sorted(TT.glob("*.jsonl.gz"))
    so_manifest = manifest(so_files)
    tt_manifest = manifest(tt_files)
    if so_manifest != {
        "count": EXPORT_SET_PINS["scriptableobject_csv_count"],
        "bytes": EXPORT_SET_PINS["scriptableobject_csv_bytes"],
        "manifest_sha256": EXPORT_SET_PINS["scriptableobject_csv_manifest_sha256"],
    }:
        raise SystemExit(f"ScriptableObject export-set pin mismatch: {so_manifest}")
    if tt_manifest != {
        "count": EXPORT_SET_PINS["typetree_jsonl_count"],
        "bytes": EXPORT_SET_PINS["typetree_jsonl_bytes"],
        "manifest_sha256": EXPORT_SET_PINS["typetree_jsonl_manifest_sha256"],
    }:
        raise SystemExit(f"TypeTree export-set pin mismatch: {tt_manifest}")
    file_pins = {}
    for rel, expected in FILE_PINS.items():
        path = ROOT / rel
        actual = sha256_file(path)
        if actual != expected:
            raise SystemExit(f"source pin mismatch for {rel}: {actual}")
        file_pins[rel] = {"sha256": actual, "bytes": path.stat().st_size}

    data_csv = read_csv(SO / "Data_Players.csv")
    data_tt = read_jsonl_gz(TT / "Data_Players.jsonl.gz")
    player_data = next(r for r in data_tt if r.get("tree", {}).get("m_Name") == "Data_Players")
    drone_data = next(r for r in data_tt if r.get("tree", {}).get("m_Name") == "Data_Drones")
    ships = player_data["tree"].get("allPlayers", [])
    drones = drone_data["tree"].get("allPlayers", [])

    board_rows = read_jsonl_gz(TT / "Board_Players.jsonl.gz")
    board = board_rows[0]
    board_tree = board.get("tree", {})
    button_fields = (
        "btnUpgradeByCoins", "btnUpgradeByGems", "textUpgradeCostCoins",
        "textUpgradeCostGems", "btnTry", "btnIAPBuyNow",
    )

    tech_csv = read_csv(SO / "Tech_Ability_Data.csv")
    tech_tt = read_jsonl_gz(TT / "Tech_Ability_Data.jsonl.gz")
    tech_records = []
    for record in tech_tt:
        tree = record.get("tree", {})
        tech_records.append({
            "row_path_id": record.get("path_id"),
            "name": tree.get("m_Name"),
            "listDatas_count": len(tree.get("listDatas", [])),
            "type_index_values": sorted({item.get("TypeIndex") for item in tree.get("listDatas", [])}),
        })

    iap_csv = read_csv(SO / "IAPProduct.csv")
    iap_rows = read_jsonl_gz(TT / "IAPProduct.jsonl.gz")
    iap_tree = iap_rows[0].get("tree", {})
    consumables = iap_tree.get("ConsumableProducts", [])
    nonconsumables = iap_tree.get("NonConsumableProducts", [])
    product_ids = consumables + nonconsumables
    relevant_product_ids = [x for x in product_ids if any(s in x.lower() for s in ("pro", "premium", "reborn", "timereward"))]

    with INVENTORY.open(newline="", encoding="utf-8") as f:
        class_names = {row["class"] for row in csv.DictReader(f)}
    target_classes = {"Player_Health", "Player_Controller"}
    attack_classes = sorted(x for x in class_names if x.startswith("Player_Attack_") and x.rsplit("_", 1)[-1].isdigit())

    target_asset_names = {"Player_Health", "Player_Controller", "Board_Reborn"}

    def is_target_export(stem: str) -> bool:
        return stem in target_asset_names or re.fullmatch(r"Player_Attack_\d+", stem) is not None

    target_named_exports = {
        "csv": [p.name[:-4] for p in so_files if is_target_export(p.name[:-4])],
        "typetree": [p.name[:-len(".jsonl.gz")] for p in tt_files if is_target_export(p.name[:-len(".jsonl.gz")])],
    }
    receipt = {
        "schema": "a5-d5-user-lead-crosswalk-v1",
        "status": "HEALTH_TECH_ROUTE_SUPPORTED; STARTER_PREMIUM_AND_EXTRA_LIFE_COUNT_NOT_BOUND; COMPONENT_OWNER_NOT_BOUND",
        "evidence_scope": "PINNED_SCRIPTABLEOBJECT_CSV_AND_SERIALIZED_TYPETREE_JSONL_PLUS_PRIOR_PUBLISHED_REPORTS",
        "runtime_or_dps_measured": False,
        "pinned_export_sets": {
            "scriptableobject_csv": so_manifest,
            "typetree_jsonl": tt_manifest,
        },
        "focal_source_files": file_pins,
        "serialized_records": {
            "data_players_csv_rows": len(data_csv),
            "data_players_records": [
                {"path_id": r.get("path_id"), "name": r.get("tree", {}).get("m_Name"),
                 "entry_count": len(r.get("tree", {}).get("allPlayers", [])),
                 "ids": [x.get("id") for x in r.get("tree", {}).get("allPlayers", [])],
                 "active": [x.get("Actived") for x in r.get("tree", {}).get("allPlayers", [])]}
                for r in data_tt
            ],
            "board_players": {
                "record_count": len(board_rows),
                "row_path_id": board.get("path_id"),
                "gameobject": board.get("gameobject"),
                "serialized_button_refs": {k: board_tree.get(k) for k in button_fields},
                "interpretation": "player catalogue UI references coin/gem upgrade controls; not evidence of Player_Health upgrade ownership or a Player_Controller component join",
            },
            "tech_ability_data": {
                "csv_row_count": len(tech_csv),
                "records": tech_records,
                "interpretation": "six serialized TechAbility records and TypeIndex values; the serialized rows alone do not label TypeIndex 0 as Health",
            },
            "iap_product_catalog": {
                "csv_row_count": len(iap_csv),
                "record_count": len(iap_rows),
                "consumable_count": len(consumables),
                "nonconsumable_count": len(nonconsumables),
                "selected_ids": relevant_product_ids,
                "interpretation": "product IDs indicate a catalogue only; no starter grant, expiry duration, purchase activation, or user state follows from these rows",
            },
        },
        "identity_and_ownership_boundary": {
            "player_attack_class_identities": len(attack_classes),
            "player_health_class_identity_present": "Player_Health" in class_names,
            "player_controller_class_identity_present": "Player_Controller" in class_names,
            "target_named_exports": target_named_exports,
            "player_attack_to_data_players_id_join": "NOT_ASSERTED; do not infer from the parallel 1..24 / 10001..10024 numbering",
            "health_owner_or_controller_owner": "NOT_BOUND_WITHIN_CAPTURED_EXPORTS",
        },
        "claims": {
            "initial_24h_premium": "NOT_BOUND_WITHIN_CAPTURED_EXPORTS; trial/timer UI names and product IDs do not establish 24h or a first-launch grant",
            "initial_extra_life_count_without_ad_or_gems": "NOT_BOUND_WITHIN_CAPTURED_EXPORTS; UI/API options do not establish a starting stock or eligibility",
            "health_start_and_upgrade_route": "SUPPORTED_BY_PRIOR_PUBLISHED_STATIC_ANALYSIS; Player_Get_Datas.StartHp=2500, formula reads TechStatPoints(0), and prior label mapping identifies stat 0 as Health in Basic; no serialized Player_Health owner row in this export set",
            "player_attack_n_route": "REUSE_PRIOR_REPORTS_109_AND_163; class-to-array and Board_Players display-consumer paths are distinct from GP_Datas.player PPtr; no serialized component-owner join",
            "player_controller_route": "REUSE_PRIOR_REPORTS_85_TO_87_FOR_METHOD_FLOW_ONLY; class identity is present, but no target-named serialized owner record in this export set",
        },
        "limits": [
            "The manifest is bounded to captured ScriptableObject CSV and TypeTree JSONL exports; it is not a whole-build absence proof.",
            "Data_Players numeric IDs are not equated to Player_Attack_N class suffixes in this receipt.",
            "Board_Players UI references do not establish Player_Health ownership or map to an individual Player_Controller.",
            "No coroutine or receiver inventory from reports 79-86 was repeated.",
            "No code body, native/FDE artifact, emulator, runtime probe, or secret was read or used by this builder.",
        ],
    }
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    result = build()
    print(f"{OUT.relative_to(ROOT)}: Data_Players={len(result['serialized_records']['data_players_records'])} rows, Board_Players={result['serialized_records']['board_players']['record_count']}, TechAbility={result['serialized_records']['tech_ability_data']['csv_row_count']}, IAP products={result['serialized_records']['iap_product_catalog']['consumable_count']}+{result['serialized_records']['iap_product_catalog']['nonconsumable_count']}; starter premium/extra-life count NOT_BOUND")
