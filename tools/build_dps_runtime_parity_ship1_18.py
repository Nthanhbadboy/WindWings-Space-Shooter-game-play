#!/usr/bin/env python3
"""Build bounded L2 #18 ship-10001 runtime-parity evidence.

Reads local static/runtime artifacts and a pinned peer source commit using git show.
Writes only datas/l2_dps_runtime_parity_ship1_18.json.gz.
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
OUT = ROOT / "datas/l2_dps_runtime_parity_ship1_18.json.gz"
RAMUS = "docs/apk-analysis/ramus/2026-10-23-phone/"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def local(path: str) -> bytes:
    return (ROOT / path).read_bytes()


def pinned(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{COMMIT}:{path}"], cwd=ROOT)


def jload(raw: bytes):
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def find_call(lines: list[str], target: str):
    hits = []
    for i, line in enumerate(lines):
        if f"bl       #{target}" in line or f"b        #{target}" in line:
            at = re.search(r"(0x[0-9a-f]+):", line).group(1)
            hits.append({"at": at, "line": line.strip(), "preceding": [x.strip() for x in lines[max(0, i-2):i]]})
    return hits


def parse_player_attack3(asm: str):
    setup_i = asm.index(";;; SetupDatas")
    damage_i = asm.index(";;; get_GetMainCannonDamage")
    shoot_i = asm.index(";;; MainCannonShoot")
    next_after_shoot = asm.find("\n;;;", shoot_i + 5)
    setup = asm[setup_i:damage_i].splitlines()
    damage_end = asm.find("\n;;;", damage_i + 5)
    damage = asm[damage_i:damage_end].splitlines()
    shoot = asm[shoot_i:next_after_shoot if next_after_shoot >= 0 else len(asm)].splitlines()
    if "bl       #0x14e3cd8" not in "\n".join(setup):
        raise ValueError("Player_Attack_3.SetupDatas no longer calls GetMainCannonRate")
    if "b        #0x14e3948" not in "\n".join(damage):
        raise ValueError("Player_Attack_3.get_GetMainCannonDamage no longer forwards to shared getter")
    if not any("[x19, #0xac]" in line for line in shoot) or not any("[x19, #0xf8]" in line for line in shoot):
        raise ValueError("scheduler field accesses missing")
    def call_arg(target: str, block: list[str]):
        for i, line in enumerate(block):
            if f"bl       #{target}" in line or f"b        #{target}" in line:
                lower = i
                while lower > 0 and not re.search(r"\bbl(?:r)?\s+", block[lower - 1]):
                    lower -= 1
                prev = "\n".join(block[lower:i])
                args = re.findall(r"mov\s+w0,\s*#(0x[0-9a-fA-F]+|[0-9]+)", prev)
                if args:
                    val = int(args[-1], 16 if args[-1].startswith("0x") else 10)
                    return val, re.search(r"(0x[0-9a-f]+):", line).group(1)
        raise ValueError(f"argument to {target} not found")
    rate_arg, rate_callsite = call_arg("0x14e3cd8", setup)
    damage_arg, damage_callsite = call_arg("0x14e3948", damage)
    if rate_arg != 2 or damage_arg != 2:
        raise ValueError(f"expected ship-10001 implementation index 2, got rate={rate_arg}, damage={damage_arg}")
    return {
        "setup_rate_argument": rate_arg,
        "setup_rate_callsite": rate_callsite,
        "damage_argument": damage_arg,
        "damage_tailcall": damage_callsite,
        "scheduler_deadline_field_offset": "0xf8",
        "scheduler_interval_field_offset": "0xac",
        "scheduler_deadline_and_interval_sites": [
            line.strip() for line in shoot
            if any(token in line for token in ("[x19, #0xf8]", "[x19, #0xac]"))
        ],
        "scheduler_time_check": "Time.time compared with timeToShotMainCannon@0xf8; after the scheduled action, Time.time + timeRateMainCannon@0xac is stored back to the deadline.",
        "scheduler_scope": "MainCannonShoot also has extra-shot counters and iterates serialized/runtime barrel structures; this report does not claim all spawned projectiles hit a target.",
    }


def build():
    ps_path = "datas/player_start_stats.json"
    rate_path = "datas/combat_rate_consumers.json"
    wi_path = "datas/wing_implementations.json"
    ps_raw, rate_raw, wi_raw = local(ps_path), local(rate_path), local(wi_path)
    ps, rate_index, wi = json.loads(ps_raw), json.loads(rate_raw), json.loads(wi_raw)
    damage_values = next(f["values"] for f in ps["fields"] if f["field"] == "StartMainCannonDamages")
    rate_values = next(f["values"] for f in ps["fields"] if f["field"] == "StartMainCannonRate")
    if len(damage_values) != 24 or len(rate_values) != 24:
        raise ValueError("expected 24-entry main-cannon arrays")
    ship_index = 2
    if damage_values[ship_index] != 2680 or rate_values[ship_index] != 4.8:
        raise ValueError("source model values changed; inspect before regenerating")

    attack_path = "reverse-engineering/raw/combat-chain/native/Player_Attack_3.asm.txt"
    player_data_asm_path = "reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt"
    player_data_json_path = "reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.json"
    attack_raw = pinned(attack_path)
    pdata_asm_raw = pinned(player_data_asm_path)
    pdata_json_raw = pinned(player_data_json_path)
    native = parse_player_attack3(attack_raw.decode("utf-8"))
    pdata_asm = pdata_asm_raw.decode("utf-8")
    for name, addr in [("GetMainCannonRate", "0x14e3cd8"), ("GetMainCannonDamage", "0x14e3948"), ("GetMainCannonRatePercent", "0x14e3d6c")]:
        if addr not in pdata_asm:
            raise ValueError(f"missing native method {name} at {addr}")
    if "fsub     s0, s1, s0" not in pdata_asm[pdata_asm.index(";;; GetMainCannonRate "):pdata_asm.index(";;; GetMainCannonRatePercent")]:
        raise ValueError("rate getter no longer computes base_rate * (1 - rate_percent)")

    # Match the exact serialized Player_Attack_3 instance to Player_10001.
    ci_path = "reverse-engineering/raw/combat-chain/component-index.json"
    ci_raw = pinned(ci_path)
    ci = jload(ci_raw)
    component_match = None
    component_shard_pin = None
    for shard_no in range(17):
        shard_path = f"reverse-engineering/raw/combat-chain/components-{shard_no:03d}.json.gz"
        shard_raw = pinned(shard_path)
        shard = jload(shard_raw)
        rows = shard.get("components", []) if isinstance(shard, dict) else shard
        for row in rows:
            if row.get("class_name") != "Player_Attack_3":
                continue
            gameobject = row.get("gameobject", {}).get("tree", {})
            if gameobject.get("m_Name") != "Player_10001":
                continue
            component_match = row
            component_shard_pin = {"path": shard_path, "sha256": sha(shard_raw)}
            break
        if component_match:
            break
    if not component_match:
        raise ValueError("serialized Player_Attack_3 on Player_10001 not found")
    tree = component_match.get("tree", {})
    points = tree.get("mainCannonPoints", [])
    if len(points) != 4:
        raise ValueError(f"expected 4 serialized mainCannonPoints refs, got {len(points)}")
    component_snapshot = {
        "status": ci.get("status"),
        "serialized_file": component_match.get("serialized_file"),
        "component_path_id": component_match.get("path_id"),
        "component_raw_object_sha256": component_match.get("raw_object_sha256"),
        "gameobject_name": gameobject.get("m_Name"),
        "gameobject_path_id": component_match.get("gameobject", {}).get("path_id"),
        "serialized_m_Enabled": tree.get("m_Enabled"),
        "serialized_demo": tree.get("demo"),
        "mainCannonPoints_count": len(points),
        "mainCannonPoints_refs": points,
        "evidence_limit": "SERIALIZED_SNAPSHOT_NOT_SPAWN_PROOF; count of Transform references is not a measured shot/hit count.",
    }

    runtime_file_names = [
        "statics_Player_Get_Datas.json", "health_game.json", "scene_game.json",
        "SUMMARY_vi.md", "CROSSCHECK-static-vs-runtime.md", "logcat_tail.log",
        "ramus_mirror_timeline.log", "boss_health.json", "boss_metrics.json", "boss_state.json",
    ]
    runtime_pins = []
    for name in runtime_file_names:
        path = RAMUS + name
        raw = local(path)
        runtime_pins.append({"path": path, "sha256": sha(raw)})
    runtime_player = json.loads(local(RAMUS + "statics_Player_Get_Datas.json"))
    runtime_fields = runtime_player["fields"]
    runtime_values = {
        "StartMainCannonDamages_index2": runtime_fields["StartMainCannonDamages"][ship_index],
        "StartMainCannonRate_index2": runtime_fields["StartMainCannonRate"][ship_index],
        "p3_startShotRate": runtime_fields.get("p3_startShotRate"),
        "StartMainCannonDamages_count": runtime_fields.get("StartMainCannonDamages_count"),
        "StartMainCannonRate_count": runtime_fields.get("StartMainCannonRate_count"),
    }
    if runtime_values["StartMainCannonDamages_index2"] != damage_values[ship_index] or runtime_values["StartMainCannonRate_index2"] != rate_values[ship_index]:
        raise ValueError("static/runtime table inputs no longer match")
    health = json.loads(local(RAMUS + "health_game.json"))
    scene = json.loads(local(RAMUS + "scene_game.json"))

    getter_metadata = {}
    impl3 = next(r for r in wi["implementations"] if r["implementation"] == "Player_Attack_3")
    for method_name in ["SetupDatas", "get_GetMainCannonDamage", "MainCannonShoot"]:
        methods = [m for m in impl3["methods"] if m.get("cls") == "Player_Attack_3" and m.get("method") == method_name]
        getter_metadata[method_name] = [
            {"rva": m.get("va"), "instructions": m.get("instructions"), "sha256_method_body": m.get("sha256")}
            for m in methods
        ]
    rate_ship = rate_index["ships"][2]
    report = {
        "schema": "l2_dps_runtime_parity_ship1_18.v1",
        "work_item": 18,
        "report_number": 111,
        "title": "#18 DPS runtime parity — tàu 10001 / Player_Attack_3 — arena/a5a74747-windwings-space-shooter-game-p",
        "branch": "arena/a5a74747-windwings-space-shooter-game-p",
        "evidence_sharing": "REPLICATION",
        "status": "STATIC_MODEL_AND_RUNTIME_STATIC_READBACK_MATCH; LIVE_DPS_PARITY_NOT_MEASURED",
        "source_commit": {"remote_ref": REMOTE, "commit": COMMIT},
        "scope": {
            "ship_id": 10001,
            "native_implementation": "Player_Attack_3",
            "combat_array_index": ship_index,
            "source_mapping": "The serialized Player_Attack_3 component is attached to GameObject Player_10001; its native damage getter passes index 2 to the shared helper, and SetupDatas passes index 2 to GetMainCannonRate.",
            "question": "Does the model DPS for ship 10001 agree with a live running-game measurement?",
            "not_scope": ["TTK", "ship ranking", "all-24 extrapolation", "screen/render approval"],
        },
        "model": {
            "evidence_type": "PINNED_NATIVE_SOURCE_AND_DECODED_CCTOR_DATA",
            "base_damage_per_accessor_call": damage_values[ship_index],
            "base_rate_parameter_seconds": rate_values[ship_index],
            "rate_semantics": "Interval, not shots/second: GetMainCannonRate returns StartMainCannonRate[index] * (1 - GetMainCannonRatePercent()); Player_Attack_3.SetupDatas stores it as timeRateMainCannon@0xac (unless demo override). MainCannonShoot compares Time.time to timeToShotMainCannon@0xf8 and schedules the next deadline by adding timeRateMainCannon.",
            "main_damage_formula_shape": "StartMainCannonDamages[index] * (1 + main-cannon tech-stat percent + level * q(level)) in the shared getter's normal branch; runtime level, tech, mode, crit, receiver gates and class-specific firing modifiers are not populated here.",
            "demo_branch": {"serialized_snapshot_demo": tree.get("demo"), "native_demo_interval_seconds": 3.0, "runtime_demo_state_known": False},
            "separate_p3_startShotRate": {"runtime_static_readback": runtime_values["p3_startShotRate"], "warning": "This is a separate p3_startShotRate config; do not substitute it for the timeRateMainCannon interval sourced via GetMainCannonRate(2)."},
            "conditional_single_projectile_stream_baseline": {
                "assumptions": ["tech rate percent = 0", "damage tech/level additions = 0", "demo = false", "one projectile hit per scheduled interval", "no extra-shot groups", "no crit", "no receiver reduction", "no misses"],
                "formula": "2680 / 4.8",
                "value_damage_per_second": round(damage_values[ship_index] / rate_values[ship_index], 12),
                "classification": "MODEL_ONLY_CONDITIONAL_NOT_WHOLE_SHIP_DPS",
            },
            "misleading_product_check": {
                "damage_times_rate": damage_values[ship_index] * rate_values[ship_index],
                "units": "damage·seconds, because rate is an interval",
                "valid_dps": False,
            },
            "serialized_attack_component": component_snapshot,
            "scheduler_metadata": rate_ship,
            "attack3_method_metadata": getter_metadata,
            "calls_and_sites": native,
        },
        "readback": {
            "status": "RAMUS_RUNTIME_STATIC_FIELDS_ONLY_DIFFERENT_APP_VERSION",
            "profile": {
                "package": "com.Gcenter.WindWings.SpaceShooter.Premium",
                "version": "1.0.69 modded repack, as identified in the pinned session summary",
                "device": "HUAWEI Mate 20 X / EVR-AL00, Android 10, 720x1429",
                "scene": scene.get("name"),
                "game_running_sample": health.get("playing"),
                "time_scale": health.get("timeScale"),
                "uptime_seconds": health.get("uptime"),
            },
            "runtime_static_values": runtime_values,
            "field_parity_vs_static_source": {
                "StartMainCannonDamages_index2": runtime_values["StartMainCannonDamages_index2"] == damage_values[ship_index],
                "StartMainCannonRate_index2": runtime_values["StartMainCannonRate_index2"] == rate_values[ship_index],
                "interpretation": "Both base table inputs match (2680 and 4.8) in the captured runtime static readback and the current static decode. This is field-value parity across different app versions, not runtime DPS parity.",
            },
            "app_version_mismatch": "Runtime profile is 1.0.69 modded Premium; current source APK is 1.3.118 official. Do not claim same-build parity.",
            "not_read_back": ["live Player_10001 instance/active implementation", "timeRateMainCannon@0xac", "mainCannonBarrels active count", "per-shot damage events", "target HP deltas", "hit/miss counts", "extra-shot counters"],
        },
        "runtime_dps_measurement": {
            "status": "NOT_MEASURED",
            "measured_shot_intervals": 0,
            "measured_hit_damage_events": 0,
            "measured_target_health_deltas": 0,
            "measured_dps": None,
            "reason": "The archived phone run contains static getter readback and scene/health snapshots, but no player-instance attack fields or time-series hit/HP samples. The available sandbox has no attached Android/Ramus runtime session; no screenshot was used as a gate.",
        },
        "conclusion": {
            "model_readback": "Base model inputs match the captured runtime static readback for index 2: 2680 damage and 4.8-second base interval. The static native code defines an interval scheduler, so damage*rate is not DPS; a no-modifier, single-projectile-stream model gives 558.333333333333 damage/s conditionally.",
            "runtime_parity": "OPEN: no live projectile/hit/health-delta series was collected, and archived runtime APK version differs from the source APK. No measured DPS parity verdict.",
            "next_measurement_needed": ["same-build running game with Player_10001 confirmed active", "read timeRateMainCannon and extra-shot/barrel state", "controlled target with health/shield path known", "record timestamps and target HP before/after multiple scheduled cycles", "compare measured damage/time against model under recorded tech/level/demo/crit state"],
        },
        "provenance": {
            "source_inputs": [
                {"path": ps_path, "sha256": sha(ps_raw)},
                {"path": rate_path, "sha256": sha(rate_raw)},
                {"path": wi_path, "sha256": sha(wi_raw)},
                {"path": attack_path, "sha256": sha(attack_raw)},
                {"path": player_data_asm_path, "sha256": sha(pdata_asm_raw)},
                {"path": player_data_json_path, "sha256": sha(pdata_json_raw)},
                {"path": ci_path, "sha256": sha(ci_raw)},
                component_shard_pin,
            ],
            "runtime_session_inputs": runtime_pins,
            "apk_hashes": {"xapk_sha256": wi.get("xapk_sha256"), "libil2cpp_sha256": wi.get("lib_sha256")},
            "apk_bundle_inputs": [
                {"entry": x.get("entry"), "file": x.get("file"), "bytes": x.get("bytes"), "sha256": x.get("sha256")}
                for x in ci.get("inputs", [])
            ],
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    with OUT.open("wb") as f:
        with gzip.GzipFile(filename="", mode="wb", fileobj=f, mtime=0, compresslevel=9) as zf:
            zf.write(data)
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} gz bytes; {len(data)} json bytes)")


if __name__ == "__main__":
    build()
