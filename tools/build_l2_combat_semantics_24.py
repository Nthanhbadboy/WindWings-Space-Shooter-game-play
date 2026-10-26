#!/usr/bin/env python3
"""Build a pinned, bounded REPLICATION receipt for #24 combat semantics.

This receipt contrasts the Board_Players display-power arrays with the
Player_Get_Datas damage getter and traces one Player_Attack_1 rank/damage path.
It does not claim runtime damage, DPS, all-ship parity, or global absence.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "datas/l2_combat_semantics_24.json.gz"
PEER_BRANCH = "arena/ef6b75ef-windwings-space-shooter-game-p"
PEER_COMMIT = "72041a1d400be6b0972f5bfa9868efe3befaeca7"
PEER_ATTACK_ARCHIVE = "reverse-engineering/raw/l2-combat-semantics-24/peer-Player_Attack_1.asm.txt.gz"
PEER_ATTACK_CONTENT_SHA256 = "ebd749901548939bfc0970752f4a9fe65505c5861eeed6788dfac909691a662d"

PINS = {
    "reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt": "dd8e6e492e4e7d5c887088798e1fa43065340f376a1e16bdc5e0e88c99406001",
    "reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt": "aa6ae77306ea48255c2c6ba47c2828b4c5ce6cf8d7be6a27c7ac52241d2df86a",
    "reverse-engineering/il2cpp/dump.cs.gz": "e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454",
    "datas/l2_basic_attack_array_consumers.json.gz": "79d7232db9fcadeb94a9cbe47346c097f87e684d1cf7b55c499b84a3607b90df",
    "reverse-engineering/raw/l2-combat-semantics-24/peer-player-firing-index.json": "2cec26c92f42b085364d08a46920ff00679b3b1340b0fbbaf75c5693654c2464",
    PEER_ATTACK_ARCHIVE: "eacd421213aa399fc851ab71c3be2acc310f5b05301e1840303f990ab1fe7545",
    "reverse-engineering/raw/l2-combat-semantics-24/peer-Player_Attack_1.json": "abca290db8e63b5aaf4ce2237f2c1bba15cd369a6e6c874ea5ff5bb32254efd6",
}

WINDOWS = {
    "board_static_array_initialization": (
        "reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt",
        0x12D63E0,
        0x12D642C,
    ),
    "board_power_display_calculation": (
        "reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt",
        0x12D5EA8,
        0x12D5F4C,
    ),
    "board_display_caller": (
        "reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt",
        0x12D13F0,
        0x12D142C,
    ),
    "main_damage_array_initialization": (
        "reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt",
        0x14E5E8C,
        0x14E5E9C,
    ),
    "main_damage_getter": (
        "reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt",
        0x14E3948,
        0x14E3B1C,
    ),
    "main_damage_stat_helper": (
        "reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt",
        0x14E3C40,
        0x14E3CD4,
    ),
    "rank_assignment": (
        PEER_ATTACK_ARCHIVE,
        0x147A394,
        0x147A3C0,
    ),
    "attack_damage_getter_override": (
        PEER_ATTACK_ARCHIVE,
        0x147A508,
        0x147A558,
    ),
    "rank_gated_attack_loop": (
        PEER_ATTACK_ARCHIVE,
        0x147B678,
        0x147B8B4,
    ),
    "main_cannon_collision_damage_callback": (
        PEER_ATTACK_ARCHIVE,
        0x147C1AC,
        0x147C3C4,
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def class_block(dump_text: str, declaration: str) -> str:
    start = dump_text.find(declaration)
    if start < 0:
        raise ValueError(f"dump declaration not found: {declaration}")
    candidates = [m.start() for m in re.finditer(r"^public (?:abstract )?class ", dump_text[start + len(declaration):], re.M)]
    if candidates:
        end = start + len(declaration) + candidates[0]
    else:
        end = len(dump_text)
    return dump_text[start:end]


def instruction_window(text: str, start: int, end: int) -> list[str]:
    rows = []
    for line in text.splitlines():
        match = re.match(r"\s*(0x[0-9a-fA-F]+):", line)
        if match and start <= int(match.group(1), 16) <= end:
            rows.append(line.strip())
    if not rows:
        raise ValueError(f"no instructions in pinned window {start:#x}..{end:#x}")
    return rows


def _method_map(payload: dict) -> dict[str, dict]:
    return {entry["method"]: entry for entry in payload.get("methods", [])}


def build(root: Path = ROOT) -> dict:
    loaded: dict[str, bytes] = {}
    for relative, expected in PINS.items():
        data = (root / relative).read_bytes()
        if sha256(data) != expected:
            raise ValueError(f"source SHA mismatch: {relative}")
        loaded[relative] = data

    board_text = loaded["reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt"].decode()
    player_data_text = loaded["reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt"].decode()
    attack_bytes = gzip.decompress(loaded[PEER_ATTACK_ARCHIVE])
    if sha256(attack_bytes) != PEER_ATTACK_CONTENT_SHA256:
        raise ValueError("decompressed peer Player_Attack_1 assembly SHA mismatch")
    attack_text = attack_bytes.decode()
    dump_text = gzip.decompress(loaded["reverse-engineering/il2cpp/dump.cs.gz"]).decode()
    board_receipt = json.loads(gzip.decompress(loaded["datas/l2_basic_attack_array_consumers.json.gz"]))
    peer_index = json.loads(loaded["reverse-engineering/raw/l2-combat-semantics-24/peer-player-firing-index.json"])
    attack_records = json.loads(loaded["reverse-engineering/raw/l2-combat-semantics-24/peer-Player_Attack_1.json"])

    if peer_index.get("status") != "PROVISIONAL_PINNED_NATIVE_RECOVERY_NOT_RUNTIME":
        raise ValueError("peer source index no longer identifies a provisional static recovery")
    if peer_index.get("xapk_sha256") != "f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e":
        raise ValueError("unexpected peer XAPK identity")
    if peer_index.get("inputs_sha256", {}).get("lib/arm64-v8a/libil2cpp.so") != "9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99":
        raise ValueError("peer native-library source pin changed")
    if peer_index.get("inputs_sha256", {}).get("assets/bin/Data/Managed/Metadata/global-metadata.dat") != "449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69":
        raise ValueError("peer metadata source pin changed")
    if peer_index.get("dump_sha256_decompressed") != "8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c":
        raise ValueError("peer dump source pin changed")

    indexed_files = {entry["path"]: entry["sha256_decompressed"] for entry in peer_index.get("files", [])}
    peer_asm_path = "reverse-engineering/raw/player-firing/native/Player_Attack_1.asm.txt"
    peer_json_path = "reverse-engineering/raw/player-firing/native/Player_Attack_1.json"
    peer_player_data_path = "reverse-engineering/raw/player-firing/native/Player_Get_Datas.asm.txt"
    if indexed_files.get(peer_asm_path) != sha256(attack_bytes):
        raise ValueError("copied peer Player_Attack_1 assembly does not match its source index")
    if indexed_files.get(peer_json_path) != sha256(loaded["reverse-engineering/raw/l2-combat-semantics-24/peer-Player_Attack_1.json"]):
        raise ValueError("copied peer Player_Attack_1 method index does not match its source index")
    if indexed_files.get(peer_player_data_path) != sha256(loaded["reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt"]):
        raise ValueError("local Player_Get_Datas assembly differs from peer indexed source")

    methods = _method_map(attack_records)
    expected_methods = {
        "SetupDatas": ("0x147a290", 260),
        "SetPlayerRank": ("0x147a394", 44),
        "get_GetMainCannonDamage": ("0x147a508", 84),
        "MainCannonAttack": ("0x147b608", 728),
        "OnBulletMainCannonCollided": ("0x147c1ac", 544),
    }
    for name, (rva, size) in expected_methods.items():
        method = methods.get(name)
        if not method or method.get("rva") != rva or method.get("bytes") != size:
            raise ValueError(f"peer method identity changed: {name}")
        if method.get("size_capped") or not method.get("ends_clean"):
            raise ValueError(f"peer method has a cap/unclean boundary: {name}")

    board_players = class_block(dump_text, "public class Board_Players : Board")
    player_get_datas = class_block(dump_text, "public class Player_Get_Datas : MonoBehaviour")
    player_attack = class_block(dump_text, "public abstract class Player_Attack : MonoBehaviour")
    if "private static float[] allBasicAtk; // 0x10" not in board_players:
        raise ValueError("Board_Players allBasicAtk declaration/offset changed")
    if "private static float[] allDeltaAtk; // 0x18" not in board_players:
        raise ValueError("Board_Players allDeltaAtk declaration/offset changed")
    if "private TextMeshPro textPlayerPower; // 0x40" not in board_players:
        raise ValueError("Board_Players textPlayerPower declaration/offset changed")
    if "private static float[] StartMainCannonDamages; // 0x78" not in player_get_datas:
        raise ValueError("Player_Get_Datas main damage field declaration/offset changed")
    if "protected int rank; // 0x44" not in player_attack:
        raise ValueError("Player_Attack inherited rank field declaration/offset changed")

    if board_receipt.get("task") != "#20 Board_Players attack-array consumers":
        raise ValueError("prior #20 display-power receipt identity changed")
    if board_receipt.get("consumer", {}).get("method") != "GetPlayerPower":
        raise ValueError("prior #20 receipt no longer names GetPlayerPower as consumer")
    if board_receipt.get("downstream_display", {}).get("field_name_source") != "dump.cs.gz Board_Players field declaration":
        raise ValueError("prior #20 display sink binding changed")
    if board_receipt.get("target", {}).get("fields", [{}])[0].get("length") != 24:
        raise ValueError("prior #20 Board_Players array length changed")

    board_formula = board_receipt["consumer"].get("observed_float_operations", [])
    if board_formula != [
        "delta[i] * GetPlayerLevel(_indexPlayer)",
        "1.0f + previous_product",
        "basic[i] * previous_sum",
    ]:
        raise ValueError("prior #20 Board_Players display formula changed")

    windows = {}
    for name, (relative, start, end) in WINDOWS.items():
        text = board_text if "Board_Players" in relative else player_data_text if "Player_Get_Datas" in relative else attack_text
        windows[name] = {
            "source": relative,
            "start": f"0x{start:x}",
            "end": f"0x{end:x}",
            "instructions": instruction_window(text, start, end),
        }

    # Assert the decisive operation chain, not merely a mnemonic or method name.
    joined = "\n".join(line for window in windows.values() for line in window["instructions"])
    required = (
        "0x12d6404: str      x19, [x8, #0x10]",
        "0x12d642c: str      x19, [x8, #0x18]",
        "0x12d5eac: ldr      x8, [x11, #0x10]",
        "0x12d5edc: ldr      x11, [x11, #0x18]",
        "0x12d5f20: fmul     s0, s1, s0",
        "0x12d5f28: fadd     s9, s0, s1",
        "0x12d5f4c: fmul     s9, s8, s9",
        "0x12d13fc: bl       #0x12d5dfc",
        "0x14e5e9c: str      x19, [x8, #0x78]",
        "0x14e3a78: ldr      x8, [x8, #0x78]",
        "0x14e3a94: bl       #0x14e3c40",
        "0x14e3afc: fmul     s0, s8, s0",
        "0x147a39c: str      w1, [x0, #0x44]",
        "0x147b678: ldr      w8, [x19, #0x44]",
        "0x147b684: mov      w26, #2",
        "0x147b694: mov      w26, #4",
        "0x147b8b0: cmp      x27, x26",
        "0x147a558: b        #0x14e3948",
        "0x147c2f4: bl       #0x14e3e24",
        "0x147c328: fmul     s0, s9, s8",
        "0x147c338: bl       #0x123b7a4",
    )
    missing = [needle for needle in required if needle not in joined]
    if missing:
        raise ValueError(f"decisive instruction missing: {missing[0]}")

    return {
        "schema_version": 1,
        "task": "#24 L2 combat semantics: Board power arrays versus attack damage/rank",
        "status": "BOUNDED_STATIC_REPLICATION_NOT_RUNTIME",
        "result": {
            "board_arrays": "The pinned #20 receipt and Board_Players native windows show allBasicAtk/allDeltaAtk read by GetPlayerPower and forwarded by SetPlayerInfo to textPlayerPower.",
            "combat_damage": "The examined Player_Attack_1 collision callback dispatches its GetMainCannonDamage override, which calls Player_Get_Datas.GetMainCannonDamage(0); that getter reads the separate StartMainCannonDamages static array at offset 0x78 and applies level/stat-dependent terms.",
            "rank": "In the examined Player_Attack_1 MainCannonAttack body, inherited rank@0x44 selects a bounded loop count (rank 3 -> 2 iterations; rank >=4 -> 4; lower other ranks return). This is not a per-hit damage multiplier in the traced getter/callback.",
            "interpretation": "The traced Board_Players power value is a display path, not established as the combat damage input for this representative attack path. This is not a global no-other-consumer claim.",
        },
        "replication": {
            "label": "REPLICATION",
            "source_branch": PEER_BRANCH,
            "source_commit": PEER_COMMIT,
            "peer_source_status": peer_index["status"],
            "scope": "One recovered Player_Attack_1 implementation plus the local #20 Board_Players receipt and common Player_Get_Datas getter. No all-24 extrapolation.",
            "source_identity": {
                "xapk_sha256": peer_index["xapk_sha256"],
                "libil2cpp_sha256": peer_index["inputs_sha256"]["lib/arm64-v8a/libil2cpp.so"],
                "metadata_sha256": peer_index["inputs_sha256"]["assets/bin/Data/Managed/Metadata/global-metadata.dat"],
                "dump_decompressed_sha256": peer_index["dump_sha256_decompressed"],
                "player_attack_1_assembly_sha256": PEER_ATTACK_CONTENT_SHA256,
            },
        },
        "board_power_display": {
            "class": "Board_Players",
            "fields": [
                {"name": "allBasicAtk", "static_offset": "0x10", "element_type": "float32", "length": 24},
                {"name": "allDeltaAtk", "static_offset": "0x18", "element_type": "float32", "length": 24},
            ],
            "consumer": "GetPlayerPower(int _indexPlayer), RVA 0x12D5DFC",
            "formula": "basic[i] * (1 + delta[i] * GetPlayerLevel(_indexPlayer))",
            "display_caller": "SetPlayerInfo RVA 0x12D1048 -> textPlayerPower instance field offset 0x40",
            "prior_receipt_sha256": PINS["datas/l2_basic_attack_array_consumers.json.gz"],
        },
        "combat_damage_path": {
            "implementation": "Player_Attack_1 (class identity from pinned peer recovery; source prefab ID mapping is outside this receipt)",
            "getter_override": {"rva": "0x147A508", "tail_branch_target": "0x14E3948", "argument": 0},
            "damage_method": "Player_Get_Datas.GetMainCannonDamage(int playerIndex)",
            "base_array": {"field": "StartMainCannonDamages", "class": "Player_Get_Datas", "static_offset": "0x78", "length": 24},
            "native_shape": "base[index] * (1 + GetMainCannonStatPercent() + level * coefficient(level)); one mode-dependent branch can zero the level term; top-tier coefficient table is not decoded here.",
            "stat_helper": {"rva": "0x14E3C40", "tech_points_getter": "Tech_Datas.GetTechStatPoints(1) @ 0x1399AA4", "common_step_field": "Player_Get_Datas.stepCommon @ 0x68"},
            "collision_callback": {"rva": "0x147C1AC", "crit_getter": "0x14E3E24", "crit_multiplier_choices": [1.0, 2.0], "damager_constructor": "0x123B7A4", "receiver_dispatch": "indirect; actual HP delta not established"},
            "rank_input_to_damage_getter": "No rank read occurs in the bounded getter override; it tail-branches with literal argument 0. Rank gating is a separate MainCannonAttack iteration decision.",
        },
        "rank_attack_path": {
            "field_declaration": "Player_Attack.rank @ 0x44 (base class)",
            "field_writer": "Player_Attack_1.SetPlayerRank writes w1 to [this+0x44] at 0x147A39C",
            "loop": {"rank_equal_3": 2, "rank_at_least_4": 4, "other_rank_below_4": "returns before loop", "counter": "x27 increments until x26 at 0x147B8AC..0x147B8B4"},
            "qualification": "Iterations pass object/component/pool/setup gates and are not measured successful bullets or hits.",
        },
        "evidence_windows": windows,
        "method_boundary_checks": {
            name: {"rva": methods[name]["rva"], "bytes": methods[name]["bytes"], "size_capped": methods[name]["size_capped"], "ends_clean": methods[name]["ends_clean"]}
            for name in expected_methods
        },
        "source_pins": {path: digest for path, digest in PINS.items()},
        "source_content_pins": {peer_asm_path: PEER_ATTACK_CONTENT_SHA256},
        "limits": [
            "Static ARM64/export evidence only; no runtime run, screenshot, redraw, or actual damage/HP delta was used.",
            "The shared Player_Attack_1 raw came from the pinned peer branch and is labelled REPLICATION; the receipt does not claim clean-room extraction.",
            "Only one Player_Attack_1 path is traced. The #82 peer 72-callsite / 24-implementation audit is not reproduced or generalized by this receipt.",
            "The exact native array-to-field mapping for the #20 Board_Players arrays remains the pinned report109 artifact's scope; no selected-player ID or index-to-prefab mapping is inferred here.",
            "The collision callback method body is not proof that every attack iteration emits a bullet, that each projectile collides, or that the receiver accepts its request.",
            "The level/stat helper inputs are not live values. One mode branch can zero the level contribution, and the coefficient table's top tier remains unresolved here.",
            "Rank changes a guarded iteration count in this body; it is not a measured hit count, DPS, TTK, or universal all-ship rank rule.",
            "No repository-wide absence claim is made about any other consumer or attack implementation.",
        ],
    }


def build_file(check: bool = False) -> bytes:
    data = gzip.compress(canonical(build()), mtime=0)
    if check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != data:
            raise SystemExit("artifact differs; rebuild with this tool")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(data)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build_file(check=args.check)
    print(f"artifact_bytes={len(data)} sha256={sha256(data)}")


if __name__ == "__main__":
    main()
