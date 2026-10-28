#!/usr/bin/env python3
"""Build the derived data files used by the M2 launch slice.

This tool never copies original game assets. It reads decoded/serialized source
tables that already live in this repository and emits small, pinned JSON files:

  game/data/launch_slice_waves.json    five real campaign waves + one real boss wave
  game/data/enemy_movement_slice.json  listSpeeds[0] / isTurret / border for the prefabs used
  game/data/enemy_guns_slice.json      Gun_Attack rows for the prefabs used
  game/data/boss_slice.json            Boss-37001 HP + animation-event shot timeline
  game/data/slice_provenance.json      source paths, SHA-256 of every source file, rules used

Design decisions that are NOT source facts are recorded inside each output file
under "design_decisions" so the runtime and the report can cite them verbatim.

Usage:  python3 game/tools/build_launch_slice_data.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "game" / "data"

WAVES_JSON = REPO / "datas" / "waves.json"
HP_BY_ID = REPO / "datas" / "enemy_hp_by_id.json"
BOSS_HP = REPO / "datas" / "boss_hp.json"
BOSS_EVENTS = REPO / "datas" / "boss_anim_events.csv"
AUDIO_RULES = REPO / "datas" / "audio_rules.json"
MOVEMENT_CSV = REPO / "reverse-engineering" / "scriptableobjects" / "Enemy_Movement.csv"
GUN_CSV = REPO / "reverse-engineering" / "scriptableobjects" / "Gun_Attack.csv"

# Stage waves are five consecutive campaign waves taken from datas/waves.json.
STAGE_WAVES = ["Wave_0016", "Wave_0017", "Wave_0018", "Wave_0019", "Wave_0020"]
# One spawner row is admitted only while the wave stays inside this many enemy
# entries. Whole rows are kept in source order; no row value is edited.
ENTRY_BUDGET_PER_WAVE = 90
BOSS_WAVE = "Wave_7001"
BOSS_PREFAB = "Boss-37001"
BOSS_CLIP = "Attack2"

GUN_SIGNATURE_FIELDS = [
    ("bullet_id", "bltId"),
    ("damage", "bltDamage"),
    ("speed", "bltSpeed"),
    ("lifetime_seconds", "bltLifetime"),
    ("gun_type", "gunType"),
    ("time_start_seconds", "timeStart"),
    ("count_mags", "allGunDatas[0].countMags"),
    ("count_shots", "allGunDatas[0].countShots"),
    ("time_reload_seconds", "allGunDatas[0].timeReload"),
    ("time_rounds_seconds", "allGunDatas[0].timeRounds"),
    ("time_shot_seconds", "allGunDatas[0].timeShot"),
]
# bullet_id differs between many rows that are otherwise identical; the source
# reader in wave_0000 only treats the remaining ten fields as ballistic/schedule
# agreement, so the same split is used here.
BALLISTIC_FIELDS = [name for name, _ in GUN_SIGNATURE_FIELDS if name != "bullet_id"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def number(value: str) -> float | int:
    if value is None or value == "":
        return 0
    try:
        parsed = float(value)
    except ValueError:
        return value
    return int(parsed) if parsed.is_integer() else parsed


def load_prefab_rows(path: Path) -> dict[str, list[dict]]:
    rows: dict[str, list[dict]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            root = row["_gameobject"].split("/")[0]
            rows[root].append(row)
    return rows


def build_waves() -> tuple[dict, list[str]]:
    document = json.loads(WAVES_JSON.read_text(encoding="utf-8"))
    by_name = {wave["wave"]: wave for wave in document["waves"]}

    stages = []
    used_prefabs: list[str] = []
    for wave_name in STAGE_WAVES:
        source = by_name[wave_name]
        rows = []
        entries = 0
        skipped_rows = 0
        for row in source["spawners"]:
            enemies = row.get("enemies") or []
            copies = int(row.get("copies", 0))
            if not enemies or copies == 0:
                skipped_rows += 1
                continue
            row_entries = len(enemies) * copies
            if entries + row_entries > ENTRY_BUDGET_PER_WAVE:
                skipped_rows += 1
                continue
            entries += row_entries
            rows.append(
                {
                    "spawner": row["spawner"],
                    "spawn_type": row["spawn_type"],
                    "enemies": list(enemies),
                    "count": int(row.get("count", 0)),
                    "rate": float(row.get("rate", 0.0)),
                    "speed": float(row.get("speed", 0.0)),
                    "y_spawn": float(row.get("y_spawn", 0.0)),
                    "radius": float(row.get("radius", 0.0)),
                    "copies": copies,
                }
            )
            for enemy in enemies:
                if enemy not in used_prefabs:
                    used_prefabs.append(enemy)
        stages.append(
            {
                "wave": wave_name,
                "source_spawner_rows": len(source["spawners"]),
                "included_rows": len(rows),
                "excluded_rows": skipped_rows,
                "entries": entries,
                "rows": rows,
            }
        )

    boss_source = by_name[BOSS_WAVE]
    boss_rows = []
    for row in boss_source["spawners"]:
        # Wave_7001 carries three rows: the boss, an empty StartPoint marker and
        # an EndPoint escort. Only the boss row is kept for the slice.
        if BOSS_PREFAB in (row.get("enemies") or []):
            boss_rows.append(
                {
                    "spawner": row["spawner"],
                    "spawn_type": row["spawn_type"],
                    "enemies": list(row["enemies"]),
                    "rate": float(row.get("rate", 0.0)),
                    "y_spawn": float(row.get("y_spawn", 0.0)),
                    "copies": int(row.get("copies", 0)),
                }
            )
            if BOSS_PREFAB not in used_prefabs:
                used_prefabs.append(BOSS_PREFAB)

    rates = [row["rate"] for stage in stages for row in stage["rows"] if row["rate"] > 0]
    total_entries = sum(stage["entries"] for stage in stages)
    document_out = {
        "schema": "windwings.launch_slice.waves/1",
        "evidence": "STATIC_CONFIRMED rows; slice selection is INFERRED",
        "source": {
            "path": "datas/waves.json",
            "sha256": sha256(WAVES_JSON),
            "count_waves": document.get("count_waves"),
            "count_spawners": document.get("count_spawners"),
        },
        "design_decisions": [
            "Stage waves are five consecutive real campaign waves (Wave_0016..Wave_0020); no wave is invented.",
            f"Each stage wave admits whole spawner rows in source order while staying within {ENTRY_BUDGET_PER_WAVE} enemy entries; row values are copied verbatim. Excluded rows are counted per wave.",
            "Rows with an empty enemy list or copies == 0 are excluded, matching the existing Wave_0000 reader.",
            f"Boss wave {BOSS_WAVE} keeps only the {BOSS_PREFAB} row; its empty StartPoint row and EndPoint escort row are out of slice scope.",
            "Spawner x placement is not serialized in the source; the running slice uses a new-design formation layout (see wave_director.gd).",
        ],
        "rate_statistics": {
            "median_positive_rate": statistics.median(rates) if rates else 0.0,
            "min": min(rates) if rates else 0.0,
            "max": max(rates) if rates else 0.0,
            "y_spawn_values": sorted({row["y_spawn"] for stage in stages for row in stage["rows"]}),
        },
        "stage_total_entries": total_entries,
        "stages": stages,
        "boss": {
            "wave": BOSS_WAVE,
            "prefab": BOSS_PREFAB,
            "rows": boss_rows,
        },
    }
    return document_out, used_prefabs


def build_movement(prefabs: list[str], rows_by_root: dict[str, list[dict]]) -> dict:
    by_prefab = {}
    missing = []
    for prefab in prefabs:
        rows = [
            row
            for row in rows_by_root.get(prefab, [])
            if row["_gameobject"] == prefab or row["_gameobject"].startswith(prefab + "/")
        ]
        speeds = [float(row["listSpeeds[0]"]) for row in rows if row["listSpeeds[0]"] != ""]
        if not rows or not speeds:
            missing.append(prefab)
            continue
        by_prefab[prefab] = {
            "prefab": prefab,
            "speed": min(speeds),
            "speed_values": sorted(set(speeds)),
            "is_turret": any(row["isTurret"] == "True" for row in rows),
            "border_w": float(rows[0]["border.w"]),
            "source_records": len(rows),
            "source_field": "listSpeeds[0]",
        }
    return {
        "schema": "windwings.launch_slice.movement/1",
        "evidence": "STATIC_CONFIRMED",
        "source": {
            "path": "reverse-engineering/scriptableobjects/Enemy_Movement.csv",
            "sha256": sha256(MOVEMENT_CSV),
        },
        "note": (
            "One row per prefab root: minimum listSpeeds[0] across the prefab's own rows, "
            "is_turret true when any own row is a turret, border.w from the first own row. "
            "Runtime unit/coordinate interpretation is not asserted."
        ),
        "missing_prefabs": missing,
        "by_prefab": by_prefab,
    }


def build_guns(prefabs: list[str], rows_by_root: dict[str, list[dict]]) -> dict:
    by_prefab = {}
    for prefab in prefabs:
        rows = [
            row
            for row in rows_by_root.get(prefab, [])
            if row["_gameobject"].startswith(prefab + "/Enemy_Ingame")
        ]
        alternatives = []
        seen = set()
        for row in rows:
            alternative = {
                "source_gameobject": row["_gameobject"],
                **{name: number(row[column]) for name, column in GUN_SIGNATURE_FIELDS},
            }
            key = tuple(alternative[name] for name, _ in GUN_SIGNATURE_FIELDS)
            if key in seen:
                continue
            seen.add(key)
            alternatives.append(alternative)
        ballistic_keys = {tuple(alt[name] for name in BALLISTIC_FIELDS) for alt in alternatives}
        same_ballistics = len(ballistic_keys) == 1 and bool(alternatives)
        if same_ballistics:
            selection = "source_agreement"
            profile = dict(alternatives[0])
        elif alternatives:
            # Most frequent ballistic signature wins; the choice is a slice
            # decision, not a claim about the original component binding.
            def ballistic_key(alternative: dict) -> tuple:
                return tuple(alternative[name] for name in BALLISTIC_FIELDS)

            counts = Counter(ballistic_key(alternative) for alternative in alternatives)
            best = max(ballistic_keys, key=lambda key: counts[key])
            profile = dict(
                next(alternative for alternative in alternatives if ballistic_key(alternative) == best)
            )
            selection = "INFERRED_most_common_signature"
        else:
            selection = "no_source_row"
            profile = None
        by_prefab[prefab] = {
            "prefab": prefab,
            "same_ballistics_and_schedule": same_ballistics,
            "selection": selection,
            "alternatives": alternatives,
            "runtime_profile": profile,
            "source_rows": len(rows),
        }
    return {
        "schema": "windwings.launch_slice.guns/1",
        "evidence": "STATIC_CONFIRMED rows; runtime profile selection is INFERRED where signatures disagree",
        "source": {
            "path": "reverse-engineering/scriptableobjects/Gun_Attack.csv",
            "sha256": sha256(GUN_CSV),
        },
        "dedup_rule": (
            "Alternatives are unique on 11 mapped fields (bullet_id included). "
            "same_ballistics_and_schedule is true only when every alternative shares the "
            "same ten ballistic/schedule fields; bullet_id may differ. When signatures "
            "disagree the most common ballistic signature is selected and labelled "
            "INFERRED_most_common_signature. Component-to-runtime binding is not asserted."
        ),
        "by_prefab": by_prefab,
    }


def build_fallback_profile(rows_by_root: dict[str, list[dict]]) -> dict:
    rows = [row for group in rows_by_root.values() for row in group]

    def median_of(column: str) -> float:
        return statistics.median(number(row[column]) for row in rows)

    return {
        "evidence": "INFERRED_FALLBACK",
        "reason": (
            "Only 42 of the 150 wave-enemy prefab IDs appear in Gun_Attack.csv. An enemy "
            "without a decoded gun row would be harmless, so the slice applies one shared "
            "fallback profile built from the median of all serialized Gun_Attack rows. This "
            "is a slice design decision, not a per-prefab source value."
        ),
        "source_rows": len(rows),
        "damage": median_of("bltDamage"),
        "speed": median_of("bltSpeed"),
        "lifetime_seconds": median_of("bltLifetime"),
        "time_start_seconds": median_of("timeStart"),
        "count_mags": int(median_of("allGunDatas[0].countMags")),
        "count_shots": int(median_of("allGunDatas[0].countShots")),
        "time_reload_seconds": median_of("allGunDatas[0].timeReload"),
        "time_rounds_seconds": median_of("allGunDatas[0].timeRounds"),
        "time_shot_seconds": median_of("allGunDatas[0].timeShot"),
    }


def build_boss() -> dict:
    hp_document = json.loads(BOSS_HP.read_text(encoding="utf-8"))
    hp_by_root = {item["root"]: item for item in hp_document["items"]}
    boss_entry = hp_by_root.get(BOSS_PREFAB, {})
    with BOSS_EVENTS.open(newline="", encoding="utf-8") as handle:
        events = [row for row in csv.DictReader(handle) if row["prefab"] == BOSS_PREFAB]
    shots = [
        {"time": float(row["time"]), "function": row["function"], "data": row["data"]}
        for row in events
        if row["clip"] == BOSS_CLIP
    ]
    shot_times = [item["time"] for item in shots if item["function"] == "Shoot"]
    loop_length = max((item["time"] for item in shots), default=0.0)
    return {
        "schema": "windwings.launch_slice.boss/1",
        "evidence": "STATIC_CONFIRMED HP and animation events; movement/attack loop are INFERRED",
        "source": {
            "hp_path": "datas/boss_hp.json",
            "hp_sha256": sha256(BOSS_HP),
            "events_path": "datas/boss_anim_events.csv",
            "events_sha256": sha256(BOSS_EVENTS),
        },
        "prefab": BOSS_PREFAB,
        "hp_max": boss_entry.get("hp_max"),
        "hp_values": boss_entry.get("hp_values", []),
        "hp_instances": boss_entry.get("instances"),
        "clip": BOSS_CLIP,
        "clip_loop_seconds": loop_length,
        "shot_times": shot_times,
        "events": shots,
        "design_decisions": [
            "The boss fires at the Shoot event times of the Attack2 clip and loops the clip every clip_loop_seconds.",
            "Boss flight path is not serialized; the slice descends to a new-design station and strafes sinusoidally.",
            "Boss projectile damage/speed are INFERRED new-game values because Gun_Attack rows are keyed per gun child, not per boss root.",
        ],
    }


def build_audio_defaults() -> dict:
    rules = json.loads(AUDIO_RULES.read_text(encoding="utf-8"))
    by_id = {rule["id"]: rule for rule in rules["rules"]}
    return {
        "schema": "windwings.launch_slice.audio/1",
        "evidence": "PROVISIONAL_STATIC_AUDIO_RULES_NOT_LISTENING_OR_RUNTIME",
        "source": {"path": "datas/audio_rules.json", "sha256": sha256(AUDIO_RULES)},
        "keys": {
            "mute": {
                "key": by_id["mute"]["key"],
                "type": "int32",
                "default": by_id["mute"]["missing_default"],
                "predicate": by_id["mute"]["predicate"],
            },
            "sound_volume": {
                "key": by_id["sound_volume"]["key"],
                "type": "float32",
                "default": by_id["sound_volume"]["missing_default_approx"],
                "predicate": by_id["sound_volume"]["predicate"],
            },
            "music_volume": {
                "key": by_id["music_volume"]["key"],
                "type": "float32",
                "default": by_id["music_volume"]["missing_default_approx"],
                "predicate": by_id["music_volume"]["predicate"],
            },
        },
        "pause": by_id["pause"],
        "registry_ids_used_for_placeholder_names": {
            "sfx_shot": 5,
            "sfx_destroy": 7,
            "ui_click": 2,
            "music_game": 33,
        },
        "design_decisions": [
            "Original audio media is not shipped. Every clip is a self-generated placeholder tone; the mapping to source clip enum values is a naming convention only.",
            "Mute forces both bus volumes to 0; music keeps playing while the game tree is paused, SFX does not (AudioListener.pause analogue).",
        ],
    }


def main() -> int:
    waves, prefabs = build_waves()
    movement = build_movement(prefabs, load_prefab_rows(MOVEMENT_CSV))
    gun_rows = load_prefab_rows(GUN_CSV)
    guns = build_guns(prefabs, gun_rows)
    guns["slice_fallback"] = build_fallback_profile(gun_rows)
    boss = build_boss()
    audio = build_audio_defaults()

    hp_by_id = json.loads(HP_BY_ID.read_text(encoding="utf-8"))["hp_by_id"]

    missing_hp = [
        prefab
        for prefab in prefabs
        if prefab != BOSS_PREFAB and prefab.split("-")[-1] not in hp_by_id
    ]
    problems = []
    if missing_hp:
        problems.append(f"missing HP rows: {missing_hp}")
    if movement["missing_prefabs"]:
        problems.append(f"missing movement rows: {movement['missing_prefabs']}")
    no_gun = [p for p, v in guns["by_prefab"].items() if not v["runtime_profile"]]
    if not guns["slice_fallback"]["source_rows"]:
        problems.append("no Gun_Attack rows available for the documented fallback profile")
    if round(float(waves["rate_statistics"]["median_positive_rate"]), 3) != 1.0:
        problems.append("median positive spawn rate is not 1.0")
    if boss.get("hp_max") is None:
        problems.append("boss HP missing")

    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "launch_slice_waves.json").write_text(
        json.dumps(waves, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    (DATA / "enemy_movement_slice.json").write_text(
        json.dumps(movement, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    (DATA / "enemy_guns_slice.json").write_text(
        json.dumps(guns, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    (DATA / "boss_slice.json").write_text(
        json.dumps(boss, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    (DATA / "audio_defaults.json").write_text(
        json.dumps(audio, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    provenance = {
        "schema": "windwings.launch_slice.provenance/1",
        "generator": "game/tools/build_launch_slice_data.py",
        "generator_sha256": sha256(Path(__file__)),
        "sources": {
            "datas/waves.json": sha256(WAVES_JSON),
            "datas/enemy_hp_by_id.json": sha256(HP_BY_ID),
            "datas/boss_hp.json": sha256(BOSS_HP),
            "datas/boss_anim_events.csv": sha256(BOSS_EVENTS),
            "datas/audio_rules.json": sha256(AUDIO_RULES),
            "reverse-engineering/scriptableobjects/Enemy_Movement.csv": sha256(MOVEMENT_CSV),
            "reverse-engineering/scriptableobjects/Gun_Attack.csv": sha256(GUN_CSV),
        },
        "prefabs": prefabs,
        "problems": problems,
    }
    (DATA / "slice_provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    print(f"stage waves: {[stage['wave'] for stage in waves['stages']]}")
    print(f"entries per wave: {[stage['entries'] for stage in waves['stages']]}")
    print(f"stage total entries: {waves['stage_total_entries']}")
    print(f"median positive rate: {waves['rate_statistics']['median_positive_rate']}")
    print(f"prefabs: {len(prefabs)}  boss hp: {boss['hp_max']}  boss shots: {len(boss['shot_times'])}")
    print(f"prefabs without a decoded gun row (fallback applies): {len(no_gun)}")
    print(f"fallback profile: {json.dumps({k: guns['slice_fallback'][k] for k in ('damage','speed','lifetime_seconds')})}")
    print(f"problems: {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
