#!/usr/bin/env python3
"""Build a bounded receipt from the complete archived 2026-10-23 capture folder.

Reads captured files only. It never launches a probe, bridge, ADB, native,
FDE, emulator, or secret workflow. Screenshot text is a manually reviewed,
hash-pinned visual observation, not OCR or a runtime entitlement assertion.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE_REL = "docs/apk-analysis/ramus/2026-10-23-phone"
CAPTURE = ROOT / CAPTURE_REL
OUT = ROOT / "datas/l3_a5_d5_23oct_runtime_crosswalk.json"

EXPECTED_CAPTURE_INVENTORY = {
    "file_count": 84,
    "total_bytes": 23793059,
    "manifest_sha256": "19fcf9eb4792651993f61400de9c4167dd11cd820473fbcf2c9f3c8793871787",
    "extensions": {".json": 43, ".png": 35, ".md": 3, ".log": 3},
}
SOURCE_PINS = {
    f"{CAPTURE_REL}/SUMMARY_vi.md": "da2b74be5c89c80abbb29844a1de63ed114dd4313203b09dda5e1167f1b3051e",
    f"{CAPTURE_REL}/CROSSCHECK-static-vs-runtime.md": "1083a154ee8a5a92c6e63aeb43f6ea5756990309e9095569a15a239423504bd0",
    f"{CAPTURE_REL}/RECHECK-2026-10-26.md": "c22553d7c3d0b41c38fdb7228ecc92c96169b2290202a1d767df1a3771797862",
    f"{CAPTURE_REL}/statics_Player_Get_Datas.json": "a99112e2b0026f5f6401c0443f1e72df35e3a15a0682a43d94aa9ad3050cba48",
    f"{CAPTURE_REL}/health_game.json": "b92319f8a0d0dcc3af8ee7cfaf62909e808ad6424779b06759b749e23c4fbecb",
    f"{CAPTURE_REL}/screenshot_running_stage1.png": "78d805d671142fe8752111c5f0d94f8706118c2748d19b5aeedd3960d9d07ab5",
    f"{CAPTURE_REL}/statics_SpaceShooter_Gameplay_GP_Datas.json": "229486764e7b06b3b4f38334b498920bc53f4ca107e7e1cb1184eb4208576bde",
    f"{CAPTURE_REL}/boss_boss_gp.json": "ac655a585c37a3719195ca0efc4f8bd6a8759f38328b07d9acc145b3c56b2ece",
    f"{CAPTURE_REL}/hierarchy_game.json": "c41293fcf102739c12298124fab6d0e916cb632f4292a85512a251bc909f6249",
    f"{CAPTURE_REL}/hierarchy_endgame.json": "93012f2aff9cf31ed2cfda42165df7d5dd7832b51949fa8219fb2369e0d1d154",
    f"{CAPTURE_REL}/types_data.json": "fd3b111958139a344aac426143c3ba8217f30c954ebeb7ec22be89b3d034d711",
    f"{CAPTURE_REL}/types_Wallet.json": "e81214176fc922dd5758f5b3110a5676473a2df9dd72e0a3111f5a2e846c17ad",
    f"{CAPTURE_REL}/types_Purse.json": "e95f235f925acb9060aacc5a00403f17837339c9d1b134997114291c65290d91",
    f"{CAPTURE_REL}/types_Currency.json": "1a421f987e03db1540ccec875bcb698a94640afbaef325c8ed1b71cb1fea0ba1",
    f"{CAPTURE_REL}/live_1_gp.json": "6155c4bd402b9e9d8179a7035f42ef6236a116189a8515a1dabe1480faaf5789",
    f"{CAPTURE_REL}/live_2_gp.json": "1f76432843b428303ca5b00a3c0e0357b1b8f28a65afca1360dcb1223523940f",
    f"{CAPTURE_REL}/live_3_gp.json": "1f76432843b428303ca5b00a3c0e0357b1b8f28a65afca1360dcb1223523940f",
    f"{CAPTURE_REL}/live_4_gp.json": "1f76432843b428303ca5b00a3c0e0357b1b8f28a65afca1360dcb1223523940f",
    f"{CAPTURE_REL}/live_5_gp.json": "1f76432843b428303ca5b00a3c0e0357b1b8f28a65afca1360dcb1223523940f",
    f"{CAPTURE_REL}/ramus_mirror_timeline.log": "8f29bba47bcb1f5a7a1470c22037be2d61a840136cebfca7f0fcd7f63b01fd11",
    "docs/apk-analysis/111-dps-runtime-parity-ship1-arena-a5a74747.md": "9e24ef3cf9d3f734ac320f68988b42bbfa4eeb72e608cd50c4ccf258e56fadbb",
}

PREMIUM_SCREENSHOTS = (
    "live_2_EndGame.png",
    "live_3_EndGame.png",
    "live_4_EndGame.png",
    "live_5_EndGame.png",
    "victory_next1.png",
    "victory_next2.png",
    "victory_tapoutside.png",
    "screenshot_now.png",
)
HEALTH_SCREENSHOTS = (
    "screenshot_running_stage1.png",
    "p_1_Game.png",
    "r2_1_Game.png",
)
GP_SNAPSHOT_FILES = (
    "statics_SpaceShooter_Gameplay_GP_Datas.json",
    "live_1_gp.json",
    "live_2_gp.json",
    "live_3_gp.json",
    "live_4_gp.json",
    "live_5_gp.json",
    "boss_boss_gp.json",
)
GP_FIELDS = (
    "isSummary", "countReborn", "rebornNow", "maxCountReborn",
    "listRebornUseItems", "pvpLife", "coinCount", "killCount",
    "countVideoBox", "countDeviceBox",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def capture_inventory() -> dict:
    paths = sorted(p for p in CAPTURE.iterdir() if p.is_file())
    records = []
    total = 0
    extensions = Counter()
    for path in paths:
        size = path.stat().st_size
        digest = sha256_file(path)
        total += size
        extensions[path.suffix.lower()] += 1
        records.append({
            "path": f"{CAPTURE_REL}/{path.name}",
            "bytes": size,
            "sha256": digest,
        })
    entries = [f"{Path(r['path']).name}\t{r['bytes']}\t{r['sha256']}" for r in records]
    manifest_sha = hashlib.sha256(("\n".join(entries) + "\n").encode()).hexdigest()
    actual = {
        "file_count": len(paths),
        "total_bytes": total,
        "manifest_sha256": manifest_sha,
        "extensions": dict(sorted(extensions.items())),
    }
    if actual != EXPECTED_CAPTURE_INVENTORY:
        raise SystemExit(f"full capture-folder inventory pin mismatch: {actual}")
    return {**actual, "files": records}


def find_node(node, target: str, path=""):
    if isinstance(node, dict):
        name = node.get("name")
        current = f"{path}/{name}" if name else path
        if name == target:
            return current, node
        for child in node.get("children", []):
            found = find_node(child, target, current)
            if found:
                return found
    elif isinstance(node, list):
        for child in node:
            found = find_node(child, target, path)
            if found:
                return found
    return None


def build() -> dict:
    inventory = capture_inventory()
    selected_pins = {}
    for rel, expected in SOURCE_PINS.items():
        path = ROOT / rel
        actual = sha256_file(path)
        if actual != expected:
            raise SystemExit(f"source pin mismatch for {rel}: {actual}")
        selected_pins[rel] = {"sha256": actual, "bytes": path.stat().st_size}

    player = read_json(f"{CAPTURE_REL}/statics_Player_Get_Datas.json")
    game_state = read_json(f"{CAPTURE_REL}/health_game.json")
    hierarchy_game = read_json(f"{CAPTURE_REL}/hierarchy_game.json")
    hierarchy_endgame = read_json(f"{CAPTURE_REL}/hierarchy_endgame.json")
    type_filter = read_json(f"{CAPTURE_REL}/types_data.json")
    fields = player["fields"]

    gp_snapshots = []
    snapshot_hashes = defaultdict(list)
    for name in GP_SNAPSHOT_FILES:
        data = read_json(f"{CAPTURE_REL}/{name}")
        digest = sha256_file(CAPTURE / name)
        snapshot_hashes[digest].append(name)
        gp_fields = data.get("fields", {})
        gp_snapshots.append({
            "source": f"{CAPTURE_REL}/{name}",
            "sha256": digest,
            "type": data.get("type"),
            "fields": {key: gp_fields.get(key) for key in GP_FIELDS if key in gp_fields},
            "field_presence": sorted(key for key in GP_FIELDS if key in gp_fields),
        })
    duplicate_gp_groups = [
        {"sha256": digest, "files": names}
        for digest, names in sorted(snapshot_hashes.items()) if len(names) > 1
    ]

    premium_node = find_node(
        hierarchy_endgame.get("tree", []),
        "Popup_PremiumDailyCollect(PREMIUM)(Clone)",
    )
    if not premium_node:
        raise SystemExit("expected Premium-named EndGame hierarchy node not found")
    premium_path, premium_obj = premium_node
    game_nodes = {}
    for target in ("Pack_Premium", "Board_Reborn(Clone)", "Board_RebornIAP(Clone)"):
        found = find_node(hierarchy_game.get("tree", []), target)
        if found:
            game_nodes[target] = {
                "path": found[0],
                "active": found[1].get("active"),
                "components": found[1].get("components", []),
            }

    premium_screens = []
    for name in PREMIUM_SCREENSHOTS:
        path = CAPTURE / name
        premium_screens.append({
            "path": f"{CAPTURE_REL}/{name}",
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        })
    health_screens = []
    for name in HEALTH_SCREENSHOTS:
        path = CAPTURE / name
        health_screens.append({
            "path": f"{CAPTURE_REL}/{name}",
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        })

    timeline_text = (CAPTURE / "ramus_mirror_timeline.log").read_text(encoding="utf-8")
    scene_events = []
    for line in timeline_text.lstrip("\ufeff").splitlines():
        match = re.match(r"(\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+) .*RAMUSB\|(\{.*\})", line)
        if not match:
            continue
        try:
            event = json.loads(match.group(2))
        except json.JSONDecodeError:
            continue
        if event.get("scene") in {"Menu", "Game", "EndGame"}:
            item = {
                "timestamp_local": match.group(1),
                "scene": event.get("scene"),
                "uptime_seconds": event.get("uptime"),
            }
            if not scene_events or scene_events[-1]["scene"] != item["scene"]:
                scene_events.append(item)
    logcat = (CAPTURE / "logcat_tail.log").read_text(encoding="utf-8")
    auth_context = "Google Play Games authentication reported InternalError in the captured log; this does not identify Premium entitlement state."
    if "Authentication failed" not in logcat or "SignInStatus:InternalError" not in logcat:
        auth_context = "No matching Google Play Games authentication failure string found in the captured log."

    types_wallet = read_json(f"{CAPTURE_REL}/types_Wallet.json")
    types_purse = read_json(f"{CAPTURE_REL}/types_Purse.json")
    types_currency = read_json(f"{CAPTURE_REL}/types_Currency.json")

    receipt = {
        "schema": "a5-d5-23oct-runtime-crosswalk-v2",
        "status": "PREMIUM_WELCOME_UI_AND_FREE_FIRST_REVIVAL_TEXT_OBSERVED; 24H_GRANT_AND_STARTING_LIFE_ALLOWANCE_NOT_MEASURED; COMPONENT_OWNER_NOT_BOUND; DPS_NOT_MEASURED",
        "scope": "READ_ONLY_FULL_EXISTING_2026-10-23_CAPTURE_FOLDER",
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
        "capture_folder_inventory": inventory,
        "selected_source_pins": selected_pins,
        "observed_runtime": {
            "health": {
                "hud_hp_visual_reading": 2500,
                "screenshot_sources": health_screens,
                "player_get_datas_start_hp": fields.get("StartHp"),
                "scene_state": {
                    "scene": game_state.get("scene"),
                    "uptime_seconds": game_state.get("uptime"),
                    "frame": game_state.get("frame"),
                },
                "temporal_qualification": "The screenshots and health_game scene-state JSON are separate artifacts; exact sample instants are not joined.",
                "interpretation": "Multiple captured HUD screenshots show 2500 and Player_Get_Datas.StartHp independently reads 2500 in this modded 1.0.69 run; no component owner or official-build parity follows.",
            },
            "player_get_datas_arrays": {
                "StartMainCannonDamages_count": len(fields.get("StartMainCannonDamages", [])),
                "StartMainCannonRate_count": len(fields.get("StartMainCannonRate", [])),
                "StartWingCannonDamages_count": len(fields.get("StartWingCannonDamages", [])),
                "sample_main_damage_index_2": fields.get("StartMainCannonDamages", [])[2],
                "sample_main_rate_index_2": fields.get("StartMainCannonRate", [])[2],
                "interpretation": "Runtime static-data readbacks only; not per-instance attack execution or a DPS measurement.",
            },
            "gp_runtime_snapshots": gp_snapshots,
            "byte_identical_gp_snapshot_groups": duplicate_gp_groups,
            "premium_ui": {
                "visual_review_basis": "Manual read-only review of the hash-pinned screenshots listed below; no screenshot was altered.",
                "screenshots": premium_screens,
                "transcribed_visible_text": [
                    "WELCOME TO PREMIUM VERSION",
                    "Congratulations on being a member of Premium FOREVER",
                    "NO ads.",
                    "FREE first revival.",
                    "UNLIMITED energy for play.",
                    "Get more X3 coin collected",
                    "FREE",
                ],
                "visible_reward_labels": ["+20", "+300", "+10"],
                "background_top_bar_readings": {
                    "energy": "250/200",
                    "stars": 3,
                    "coins": 71581,
                    "diamonds": 510,
                },
                "interpretation": "This is direct evidence that the captured modded build displayed a Premium welcome/benefit screen and advertised a free first revival. It is not a 24-hour timer, a clean fresh-account state, or server/backend entitlement validation.",
            },
            "endgame_hierarchy": {
                "scene": hierarchy_endgame.get("scene"),
                "node_path": premium_path,
                "active": premium_obj.get("active"),
                "components": premium_obj.get("components", []),
                "children": [
                    {"name": child.get("name"), "active": child.get("active"), "components": child.get("components", [])}
                    for child in premium_obj.get("children", [])
                ],
                "interpretation": "Premium-named popup is active in the captured EndGame hierarchy; generic Component labels do not expose entitlement fields.",
            },
            "game_hierarchy_ui_nodes": game_nodes,
            "timeline_scene_transitions": scene_events,
            "account_context": {
                "logcat_authentication_note": auth_context,
                "fresh_account_or_first_launch_proven": False,
                "interpretation": "The capture does not establish a fresh account. The Premium screenshots visibly show nonzero resource counters; those counters are kept as screenshot observations, not joined to other snapshots.",
            },
            "type_query": {
                "data_filter": type_filter.get("filter"),
                "wallet_filter_matches": types_wallet.get("matched", []),
                "purse_filter_matches": types_purse.get("matched", []),
                "currency_filter_matches": types_currency.get("matched", []),
                "interpretation": "These are narrow filtered type-list results, not a complete live instance or global wallet-absence finding.",
            },
        },
        "claim_boundaries": {
            "premium_ui": "OBSERVED: welcome modal text says member of Premium FOREVER and lists benefits. This is a UI claim from modded/repackaged 1.0.69, not proof of a fresh-account entitlement or backend state.",
            "new_player_24h_premium_grant": "NOT_MEASURED: no 24-hour duration, countdown/expiry, fresh-account state, or grant receipt appears in the inspected capture. The visible wording says FOREVER, not 24 hours.",
            "free_first_revival_benefit": "UI_ADVERTISED: Premium modal says FREE first revival. Starting free-life stock, eligibility logic, actual consumption, and whether this benefit was granted to a new account remain NOT_MEASURED.",
            "captured_reborn_activity": "NO_REBORN_RECORDED_IN_THE_CAPTURED_GP_SNAPSHOTS: visible fields report countReborn=0 and four false reborn-use flags where present. Repeated byte-identical live_2..live_5 snapshots count as one unique payload, not four independent samples.",
            "max_count_reborn": "-1 appears in statics/boss snapshot; sentinel semantics remain unbound.",
            "pvp_life": "SEPARATE_FIELD: pvpLife=3 is not equated with extra lives.",
            "health_vs_attack_vs_controller": "Multiple captured HUD images and Player_Get_Datas.StartHp show 2500. The hierarchy and filtered type results still do not bind a live Player_Health, Player_Attack_N, or Player_Controller instance/member owner.",
            "dps": "MODEL_NOT_MEASURED; report 111 independently records no runtime DPS measurement.",
            "cross_build": "All runtime values/UI belong to the modded 1.0.69 capture. Official 1.3.118 static comparisons remain cross-build and qualified.",
        },
        "limits": [
            "The complete local capture folder is inventoried and pinned; all listed source artifacts are read-only inputs.",
            "Screenshot wording is a manual visual transcription from hash-pinned images, not OCR or proof of backend entitlement.",
            "No new probe, bridge, ADB, runtime workflow, emulator, native/FDE, or secret work was run.",
            "No 24-hour grant, starting life count, component-owner mapping, same-build parity, or DPS value is inferred from absent evidence.",
            "Repeated identical GP snapshots are de-duplicated for evidentiary weight; separate snapshot files are not automatically treated as independent sessions.",
        ],
    }
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    result = build()
    runtime = result["observed_runtime"]
    gp = runtime["gp_runtime_snapshots"]
    premium = runtime["premium_ui"]
    print(
        f"{OUT.relative_to(ROOT)}: pinned capture files={result['capture_folder_inventory']['file_count']}; "
        f"HUD/StartHp={runtime['health']['hud_hp_visual_reading']}/{runtime['health']['player_get_datas_start_hp']}; "
        f"GP snapshots={len(gp)}, byte-identical live_2..5 deduplicated; Premium Forever UI + free-first-revival text observed; "
        "24h grant and starting life allowance NOT_MEASURED"
    )
