#!/usr/bin/env python3
"""Build a bounded receipt from already-captured 2026-10-23 Ramus artifacts.

This reads archived files only. It never launches a probe, bridge, ADB, native,
FDE, emulator, or secret workflow.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = "docs/apk-analysis/ramus/2026-10-23-phone"
OUT = ROOT / "datas/l3_a5_d5_23oct_runtime_crosswalk.json"

SOURCE_PINS = {
    f"{CAPTURE}/SUMMARY_vi.md": "da2b74be5c89c80abbb29844a1de63ed114dd4313203b09dda5e1167f1b3051e",
    f"{CAPTURE}/CROSSCHECK-static-vs-runtime.md": "1083a154ee8a5a92c6e63aeb43f6ea5756990309e9095569a15a239423504bd0",
    f"{CAPTURE}/RECHECK-2026-10-26.md": "c22553d7c3d0b41c38fdb7228ecc92c96169b2290202a1d767df1a3771797862",
    f"{CAPTURE}/statics_Player_Get_Datas.json": "a99112e2b0026f5f6401c0443f1e72df35e3a15a0682a43d94aa9ad3050cba48",
    f"{CAPTURE}/health_game.json": "b92319f8a0d0dcc3af8ee7cfaf62909e808ad6424779b06759b749e23c4fbecb",
    f"{CAPTURE}/screenshot_running_stage1.png": "78d805d671142fe8752111c5f0d94f8706118c2748d19b5aeedd3960d9d07ab5",
    f"{CAPTURE}/statics_SpaceShooter_Gameplay_GP_Datas.json": "229486764e7b06b3b4f38334b498920bc53f4ca107e7e1cb1184eb4208576bde",
    f"{CAPTURE}/boss_boss_gp.json": "ac655a585c37a3719195ca0efc4f8bd6a8759f38328b07d9acc145b3c56b2ece",
    f"{CAPTURE}/hierarchy_game.json": "c41293fcf102739c12298124fab6d0e916cb632f4292a85512a251bc909f6249",
    f"{CAPTURE}/types_data.json": "fd3b111958139a344aac426143c3ba8217f30c954ebeb7ec22be89b3d034d711",
    "docs/apk-analysis/111-dps-runtime-parity-ship1-arena-a5a74747.md": "9e24ef3cf9d3f734ac320f68988b42bbfa4eeb72e608cd50c4ccf258e56fadbb",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def find_nodes(node, names: set[str], found=None):
    if found is None:
        found = {}
    if isinstance(node, dict):
        name = node.get("name")
        if name in names:
            found[name] = node
        for value in node.values():
            find_nodes(value, names, found)
    elif isinstance(node, list):
        for value in node:
            find_nodes(value, names, found)
    return found


def build() -> dict:
    pins = {}
    for rel, expected in SOURCE_PINS.items():
        path = ROOT / rel
        actual = sha256_file(path)
        if actual != expected:
            raise SystemExit(f"source pin mismatch for {rel}: {actual}")
        pins[rel] = {"sha256": actual, "bytes": path.stat().st_size}

    player = read_json(f"{CAPTURE}/statics_Player_Get_Datas.json")
    game_state = read_json(f"{CAPTURE}/health_game.json")
    gp = read_json(f"{CAPTURE}/boss_boss_gp.json")
    hierarchy = read_json(f"{CAPTURE}/hierarchy_game.json")
    type_filter = read_json(f"{CAPTURE}/types_data.json")
    fields = player["fields"]
    gp_fields = gp["fields"]
    nodes = find_nodes(
        hierarchy.get("tree", []),
        {"PLAYER", "Player_Ingame", "Board_Reborn(Clone)", "Pack_Premium"},
    )

    receipt = {
        "schema": "a5-d5-23oct-runtime-crosswalk-v1",
        "status": "CAPTURED_HEALTH_VALUE_CONFIRMED; PREMIUM_24H_AND_INITIAL_EXTRA_LIFE_NOT_MEASURED; COMPONENT_OWNER_NOT_BOUND; DPS_NOT_MEASURED",
        "scope": "READ_ONLY_EXISTING_2026-10-23_CAPTURE_ARTIFACTS",
        "workflow_replayed": False,
        "capture_identity": {
            "package": "com.Gcenter.WindWings.SpaceShooter.Premium",
            "build": "modded/repackaged 1.0.69",
            "device": "Huawei Mate 20 X",
            "android": "10",
            "unity": "2022.3.62f3 IL2CPP",
            "comparison_build": "official com.Wind.wings.Space.Shooter 1.3.118",
            "comparison_boundary": "CROSS_BUILD_ONLY; no same-build parity witness",
        },
        "source_pins": pins,
        "observed_runtime": {
            "health": {
                "hud_hp_screenshot_reading": 2500,
                "screenshot": f"{CAPTURE}/screenshot_running_stage1.png",
                "player_get_datas_start_hp": fields.get("StartHp"),
                "scene_state": {
                    "scene": game_state.get("scene"),
                    "uptime_seconds": game_state.get("uptime"),
                    "frame": game_state.get("frame"),
                },
                "temporal_qualification": "Screenshot and health_game scene-state JSON are separate artifacts; not asserted as the same instant.",
                "interpretation": "Direct captured-run HUD value and Player_Get_Datas readback both show 2500; not official-build parity or evidence of which component owns/applies it.",
            },
            "player_get_datas_arrays": {
                "StartMainCannonDamages_count": len(fields.get("StartMainCannonDamages", [])),
                "StartMainCannonRate_count": len(fields.get("StartMainCannonRate", [])),
                "StartWingCannonDamages_count": len(fields.get("StartWingCannonDamages", [])),
                "sample_main_damage_index_2": fields.get("StartMainCannonDamages", [])[2],
                "sample_main_rate_index_2": fields.get("StartMainCannonRate", [])[2],
                "interpretation": "Runtime static-data readbacks only; not per-instance attack execution or a DPS measurement.",
            },
            "endgame_gp_datas": {
                key: gp_fields.get(key)
                for key in (
                    "isSummary", "countReborn", "rebornNow", "maxCountReborn",
                    "listRebornUseItems", "pvpLife",
                )
            },
            "scene_hierarchy": {
                name: {
                    "active": nodes[name].get("active"),
                    "components": nodes[name].get("components", []),
                }
                for name in sorted(nodes)
            },
            "type_query": {
                "filter": type_filter.get("filter"),
                "interpretation": "Filtered type listing, not a complete live component-instance or ownership readback.",
            },
        },
        "claim_boundaries": {
            "new_player_24h_premium_grant": "NOT_MEASURED: no fresh-account/first-launch state, entitlement flag, expiry/timer, or 24-hour receipt in the inspected capture. The .Premium package suffix is not entitlement evidence.",
            "initial_free_extra_life_allowance": "NOT_MEASURED: the endgame snapshot records countReborn=0 and rebornNow=0 with all four listRebornUseItems false, but does not expose initial stock or free/ad/gem eligibility. maxCountReborn=-1 semantics remain unbound.",
            "pvp_life": "SEPARATE_FIELD: pvpLife=3 is not equated with extra lives.",
            "health_vs_attack_vs_controller": "StartHp=2500 is a Player_Get_Datas readback plus HUD observation. Captured hierarchy labels component types generically; no Player_Health, Player_Attack_N, or Player_Controller instance/member ownership is bound.",
            "dps": "MODEL_NOT_MEASURED; report 111 independently records no runtime DPS measurement.",
            "cross_build": "Runtime values belong to the modded 1.0.69 capture. Official 1.3.118 static comparisons remain cross-build and qualified.",
        },
        "limits": [
            "Only the listed existing capture files and published report 111 were read; no capture file was modified.",
            "No new probe, bridge, ADB, runtime workflow, emulator, native/FDE, or secret work was run.",
            "No Premium grant, initial reborn stock, component-owner mapping, or DPS value is inferred from absent evidence.",
            "The `_Data`-filtered type listing is not treated as proof that other component classes are absent.",
        ],
    }
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    result = build()
    health = result["observed_runtime"]["health"]
    reborn = result["observed_runtime"]["endgame_gp_datas"]
    print(
        f"{OUT.relative_to(ROOT)}: HUD/StartHp={health['hud_hp_screenshot_reading']}/{health['player_get_datas_start_hp']}; "
        f"endgame reborn={reborn['countReborn']}, now={reborn['rebornNow']}, max={reborn['maxCountReborn']}; "
        "Premium 24h/initial free-life allowance NOT_MEASURED"
    )
