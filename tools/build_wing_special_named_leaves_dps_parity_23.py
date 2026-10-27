#!/usr/bin/env python3
"""Build the bounded #23 wing special-path / damage-model replication report.

Reads local evidence indexes and the pinned peer commit with git show. Writes only
 datas/l2_wing_special_named_leaves_dps_parity_23.json.gz.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "d7e718cfb5466fd7bd03e2d8357400d744b108cb"
REMOTE = "origin/arena/ef6b75ef-windwings-space-shooter-game-p"
OUT = ROOT / "datas/l2_wing_special_named_leaves_dps_parity_23.json.gz"
SPECIAL_TERMS = {
    2: ["UpdateParticle", "OnParticleCollision", "OnParticleCollision2"],
    4: ["FindAndAttackEnemies", "LevelUp"],
    6: ["SetSizeSaw", "OnCollision"],
    8: ["SetSizeSaw", "FindAndAttackEnemies", "OnCollision"],
    10: ["AttackNormal", "AttackEnemy", "HitEnemy", "UpdateRange"],
    12: ["AttackNormal", "AttackSuper", "SyncAttack", "OnHitSuper"],
    15: ["GunCheckEnemies", "UpdateLaserPositions"],
}
COMPONENT_FIELDS = {
    2: [],
    4: ["targetLayer", "allLightningScript"],
    6: ["demo", "sawParent", "sawRenderer", "sawSprites", "sawPhysics", "layerOnlyEnemy", "layerBltAndEnemy"],
    8: ["sawParent", "sawRenderer", "sawSprites", "sawPhysics", "layerOnlyEnemy", "layerBltAndEnemy", "targetLayer", "allLightningScript"],
    10: ["demo", "playerAnimation", "layerOnlyEnemy", "allShotEffects", "rangeObject"],
    12: ["demo", "playerAnimation", "layerOnlyEnemy", "allLightningScript", "supperEffect", "attackLeft", "attackRight", "attackSpec", "attackSupper", "listAngleLeft", "listAngleRight", "listTargetLeft", "listTargetRight"],
    15: ["layerOnlyEnemy", "rangeObject", "targetLayer", "allParentPoints", "allGuns", "allLines"],
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def local_bytes(path: str) -> bytes:
    return (ROOT / path).read_bytes()


def pinned_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{COMMIT}:{path}"], cwd=ROOT)


def pinned_sha(path: str) -> str:
    return sha(pinned_bytes(path))


def as_json(raw: bytes):
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def parse_index_argument(class_number: int, asm: str):
    marker = ";;; get_GetWingCannonDamage"
    start = asm.find(marker)
    if start < 0:
        raise ValueError(f"missing getter signature Player_Attack_{class_number}")
    end = asm.find("\n;;;", start + len(marker))
    body = asm[start: end if end >= 0 else len(asm)]
    lines = body.splitlines()
    call_i = next((i for i, line in enumerate(lines) if "bl       #0x14e3edc" in line), None)
    if call_i is None or call_i < 2:
        raise ValueError(f"missing shared getter call Player_Attack_{class_number}")
    callsite = re.search(r"(0x[0-9a-fA-F]+):", lines[call_i]).group(1)
    arg_line = lines[call_i - 2]
    m = re.search(r"mov\s+w0,\s*(?:#(0x[0-9a-fA-F]+|[0-9]+)|(wzr))", arg_line)
    if not m:
        raise ValueError(f"unparsed getter argument: {class_number}: {arg_line}")
    arg_text = m.group(1)
    arg = int(arg_text, 16 if arg_text.startswith("0x") else 10) if arg_text else 0
    return arg, callsite


def reduce_serialized_value(value):
    if isinstance(value, list):
        return {"count": len(value), "first_three": value[:3]}
    return value


def component_row_summary(row, number):
    tree = row.get("tree", {})
    return {
        "path_id": row.get("path_id"),
        "serialized_file": row.get("serialized_file"),
        "gameobject_name": row.get("gameobject", {}).get("tree", {}).get("m_Name"),
        "component_raw_object_sha256": row.get("raw_object_sha256"),
        "tree_field_names": sorted(tree),
        "selected_serialized_fields": {
            key: reduce_serialized_value(tree[key])
            for key in COMPONENT_FIELDS[number]
            if key in tree
        },
        "evidence_class": "SERIALIZED_SNAPSHOT_NOT_SPAWN_PROOF",
    }


def build():
    wi_path = "datas/wing_implementations.json"
    ps_path = "datas/player_start_stats.json"
    flow_path = "datas/wing_emission_flow.json"
    pooled_path = "datas/wing_pooled_leaves.json"
    wi_raw, ps_raw = local_bytes(wi_path), local_bytes(ps_path)
    flow_raw, pooled_raw = local_bytes(flow_path), local_bytes(pooled_path)
    wi, ps = json.loads(wi_raw), json.loads(ps_raw)
    flow, pooled = json.loads(flow_raw), json.loads(pooled_raw)

    # Verify all indexed source inputs against the exact peer commit before use.
    native_pins = []
    for path, expected in sorted(wi["inputs"].items()):
        actual = pinned_sha(path)
        if actual != expected:
            raise ValueError(f"pinned source mismatch: {path}: {actual} != {expected}")
        native_pins.append({"path": path, "sha256": actual})
    if len(native_pins) != 62:
        raise ValueError(f"expected 62 verified inputs, got {len(native_pins)}")

    damage_field = next(f for f in ps["fields"] if f["field"] == "StartWingCannonDamages")
    damage_values = damage_field["values"]
    if len(damage_values) != 24:
        raise ValueError("StartWingCannonDamages length is not 24")

    native_rows = []
    for number, row in enumerate(wi["implementations"], 1):
        expected_class = f"Player_Attack_{number}"
        if row["implementation"] != expected_class:
            raise ValueError(f"unexpected implementation order: {row['implementation']}")
        asm_path = f"reverse-engineering/raw/combat-chain/native/{expected_class}.asm.txt"
        asm = pinned_bytes(asm_path).decode("utf-8")
        index_arg, callsite = parse_index_argument(number, asm)
        if index_arg != number - 1:
            raise ValueError(f"getter index mismatch for {expected_class}: {index_arg}")
        getter = next((m for m in row["methods"] if m.get("cls") == expected_class and m.get("method") == "get_GetWingCannonDamage"), None)
        max_getter = next((m for m in row["methods"] if m.get("cls") == expected_class and m.get("method") == "get_GetWingCannonMaxPowerDamage"), None)
        if not getter or not max_getter:
            raise ValueError(f"missing wing damage getter metadata for {expected_class}")
        native_rows.append({
            "implementation": expected_class,
            "serialized_source_id": row.get("source_id"),
            "shared_damage_table_index": index_arg,
            "start_wing_cannon_damage_before_runtime_modifiers": damage_values[index_arg],
            "class_getter": {
                "rva": getter.get("va"),
                "sha256_method_body": getter.get("sha256"),
                "shared_accessor_callsite": callsite,
                "shared_accessor_rva": "0x14e3edc",
            },
            "max_power_damage_getter": {
                "present_in_native_class": True,
                "rva": max_getter.get("va"),
                "sha256_method_body": max_getter.get("sha256"),
                "formula_normalized_for_runtime_parity": False,
            },
            "normal_set_barrels_present_in_native_inventory": row.get("normal_set_barrels") is not None,
            "special_path": row.get("special_path"),
        })

    # Pull the serialized component readback from the same pinned source commit.
    index_path = "reverse-engineering/raw/combat-chain/component-index.json"
    index_raw = pinned_bytes(index_path)
    index = as_json(index_raw)
    shard_pins, attack_rows = [], []
    for shard_no in range(17):
        path = f"reverse-engineering/raw/combat-chain/components-{shard_no:03d}.json.gz"
        raw = pinned_bytes(path)
        shard_pins.append({"path": path, "sha256": sha(raw)})
        shard = as_json(raw)
        records = shard.get("components", []) if isinstance(shard, dict) else shard
        attack_rows.extend(r for r in records if r.get("class_name", "").startswith("Player_Attack_"))
    counts = {}
    for row in attack_rows:
        counts[row["class_name"]] = counts.get(row["class_name"], 0) + 1
    if len(attack_rows) != 101 or len(counts) != 23:
        raise ValueError(f"unexpected component snapshot coverage: {len(attack_rows)} rows, {len(counts)} types")
    samples = {}
    for number in SPECIAL_TERMS:
        cls = f"Player_Attack_{number}"
        candidates = sorted((r for r in attack_rows if r.get("class_name") == cls), key=lambda r: r.get("path_id", 0))
        if candidates:
            samples[cls] = component_row_summary(candidates[0], number)

    attack_errors = []
    for err in index.get("errors", []):
        cls = err.get("class_name", "")
        if cls.startswith("Player_Attack_"):
            attack_errors.append({
                "serialized_file": err.get("serialized_file"),
                "path_id": err.get("path_id"),
                "class_name": cls,
                "error": err.get("error"),
                "raw_object_sha256": err.get("raw_object_sha256"),
                "gameobject_name": err.get("gameobject", {}).get("tree", {}).get("m_Name"),
            })
    attack_types = {f"Player_Attack_{n}" for n in range(1, 25)}
    full_types = set(counts)
    if full_types | {e["class_name"] for e in attack_errors} != attack_types:
        raise ValueError("component snapshots/errors do not account for all 24 implementation types")

    special_paths = []
    for number, terms in SPECIAL_TERMS.items():
        row = wi["implementations"][number - 1]
        chosen = {}
        for method in row["methods"]:
            text = f"{method.get('cls', '')} {method.get('method', '')}".lower()
            if any(term.lower() in text for term in terms):
                key = (method.get("cls"), method.get("method"), method.get("va"))
                chosen[key] = method
        methods = [
            {"class": m.get("cls"), "method": m.get("method"), "rva": m.get("va"),
             "instructions": m.get("instructions"), "sha256_method_body": m.get("sha256")}
            for m in sorted(chosen.values(), key=lambda m: (m.get("va", ""), m.get("method", "")))
        ]
        special_paths.append({
            "implementation": row["implementation"],
            "special_path_inventory_label": row.get("special_path"),
            "named_native_methods": methods,
            "serialized_component_sample": samples.get(row["implementation"]),
            "coverage_limit": "Native method bodies and serialized object references are static evidence only; not proof of runtime invocation, collision, hit application, or cadence.",
        })

    pooled_classes = sorted({leaf.get("cls", "").split(".")[0] for leaf in pooled.get("leaves", [])})
    component_inputs = [{"path": index_path, "sha256": sha(index_raw)}] + shard_pins
    apk_bundle_inputs = [
        {"entry": x.get("entry"), "file": x.get("file"), "bytes": x.get("bytes"), "sha256": x.get("sha256")}
        for x in index.get("inputs", [])
    ]
    player_getter_paths = [
        "reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt",
        "reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.json",
    ]
    player_getter_pins = []
    for path in player_getter_paths:
        actual = pinned_sha(path)
        player_getter_pins.append({"path": path, "sha256": actual})

    report = {
        "schema": "l2_wing_special_named_leaves_dps_parity_23.v1",
        "report_number": 23,
        "title": "Wing special/named leaves and bounded DPS-parity evidence — arena/a5a74747-windwings-space-shooter-game-p",
        "branch": "arena/a5a74747-windwings-space-shooter-game-p",
        "evidence_sharing": "REPLICATION",
        "status": "STATIC_MODEL_PARTIAL; SERIALIZED_READBACK_LIMITED; RUNTIME_DPS_PARITY_NOT_MEASURED",
        "source_commit": {"remote_ref": REMOTE, "commit": COMMIT},
        "scope": {
            "implementation_types_reviewed": 24,
            "special_path_types": len(SPECIAL_TERMS),
            "normal_set_barrels_types": sum(r["normal_set_barrels"] is not None for r in wi["implementations"]),
            "purpose": "Cover implementation-specific named special paths and identify which wing-damage model layers can and cannot be compared.",
            "not_claimed": ["runtime spawn proof", "runtime projectile/hit proof", "shot cadence", "damage-per-second parity", "all-24 firing coverage"],
        },
        "model_readback_runtime": {
            "static_model": {
                "status": "PARTIAL_NATIVE_MODEL",
                "shared_getter": "Player_Get_Datas.GetWingCannonDamage at 0x14e3edc",
                "observed_formula_shape": "StartWingCannonDamages[playerIndex] * (1 + GetWingCannonStatPercent() + level * q(level)) in the common helper's normal branch; class-specific getter code can add more runtime-dependent factors.",
                "q_level_branches": [
                    {"levels": "<30", "coefficient": 0.168},
                    {"levels": "30..57", "coefficient": 0.1764},
                    {"levels": "58..117", "coefficient": 0.1932},
                    {"levels": "118..247", "coefficient": "table[1] at 0x757b00; numeric value not resolved in this extract"},
                    {"levels": ">=248", "coefficient": "table[0] at 0x757b00; numeric value not resolved in this extract"},
                ],
                "mode_branch_limit": "The native method has a mode-dependent level branch; report does not evaluate account/game state or class-specific modifiers.",
                "max_power_state": "A separate get_GetWingCannonMaxPowerDamage override is present in all 24 pinned class files; its state-dependent formula is not normalized or included in DPS parity.",
                "per_implementation_table": native_rows,
            },
            "serialized_readback": {
                "status": "SERIALIZED_COMPONENT_SNAPSHOTS_ONLY_NOT_LIVE_RAM",
                "component_index_status": index.get("status"),
                "component_records_total_in_index": index.get("components"),
                "player_attack_records_decoded": len(attack_rows),
                "decoded_player_attack_types": len(full_types),
                "record_counts_by_type": dict(sorted(counts.items())),
                "attack_component_errors": attack_errors,
                "special_path_component_samples": samples,
                "no_live_process_readback_attached": True,
            },
            "runtime": {
                "status": "NOT_MEASURED",
                "live_damage_samples": 0,
                "firing_intervals_or_shots_per_second": 0,
                "hit_or_collision_counts": 0,
                "runtime_dps_parity_verdict": "NONE; cannot confirm or reject parity from available static/model and serialized-snapshot evidence.",
            },
        },
        "named_special_paths": special_paths,
        "prior_pooled_leaf_boundary": {
            "pooled_leaf_count": len(pooled.get("leaves", [])),
            "pooled_leaf_classes": pooled_classes,
            "pooled_leaf_scope": pooled.get("scope"),
            "special_path_classes_not_covered_by_those_five_leaf_bodies": [f"Player_Attack_{n}" for n in SPECIAL_TERMS],
            "interpretation": "The five pooled leaves are specific bodies under Player_Attack_22/23/24; they are not coverage evidence for the seven implementation-specific special paths.",
        },
        "growth_and_display_separation": {
            "board_players_ui_power_display_delta_per_level": 0.168,
            "wing_combat_getter_level_coefficient": "separate native level-dependent term; starts at 0.168 below level 30, then 0.1764 and 0.1932, then uses an unresolved table branch",
            "ship_damage_growth_per_level": 0.16,
            "warning": "The numerically equal UI delta and first combat coefficient are different quantities; do not substitute either for ship-damage growth or infer DPS from UI power.",
        },
        "special_path_inventory": special_paths,
        "provenance": {
            "artifact_inputs": [
                {"path": wi_path, "sha256": sha(wi_raw)},
                {"path": ps_path, "sha256": sha(ps_raw)},
                {"path": flow_path, "sha256": sha(flow_raw)},
                {"path": pooled_path, "sha256": sha(pooled_raw)},
            ],
            "source_bundle_hashes": {"xapk_sha256": wi.get("xapk_sha256"), "lib_sha256": wi.get("lib_sha256")},
            "verified_native_input_manifest_count": len(native_pins),
            "verified_native_input_manifest": native_pins,
            "player_damage_getter_sources": player_getter_pins,
            "serialized_bundle_inputs": apk_bundle_inputs,
            "component_index_and_shards": component_inputs,
        },
        "conclusion": {
            "static_finding": "All 24 Player_Attack_N getters call the shared wing-damage accessor with index N-1; all 24 also contain a separate get_GetWingCannonMaxPowerDamage override. The 24 decoded start-damage entries can therefore be mapped by native code index, but max-power behavior is not normalized. Seven implementations have distinct special-path labels and pinned named method bodies; six have fully decoded representative serialized components, while Player_Attack_2 is present as component parse errors with raw-object hashes and root name." ,
            "parity_finding": "Only a bounded static base/helper model is available. Class-specific scaling, firing cadence, hit application and runtime state are not reconciled, so DPS parity remains unmeasured and open.",
            "next_evidence_needed": ["live readback for each scoped implementation", "runtime hit/damage samples", "shots-per-second or equivalent cadence under controlled state", "class-specific getter modifiers and special-path hit semantics normalized against the live samples"],
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    with OUT.open("wb") as f:
        with gzip.GzipFile(filename="", mode="wb", fileobj=f, mtime=0, compresslevel=9) as zf:
            zf.write(encoded)
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes gz; {len(encoded)} bytes json)")


if __name__ == "__main__":
    build()
