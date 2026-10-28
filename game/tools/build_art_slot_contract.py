#!/usr/bin/env python3
"""Build the ART SLOT CONTRACT for the launch slice.

The slot list is derived from game/data/launch_slice_waves.json (the same file the
runtime spawns from), the roster in game/scripts/ship_roster.gd and the fixed
slice extras (background, bullets, FX, menu frame). Editing the wave selection
therefore changes the contract on the next run instead of leaving stale slots.

Outputs:
  game/data/art_slot_contract.json   machine-readable contract (runtime + CI)
  game/data/ART_SLOT_CONTRACT.md     the same table, for people drawing the art

No art is generated or copied here. Every slot documents what an artist must
deliver and how the game displays it.

Usage: python3 game/tools/build_art_slot_contract.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GAME = REPO / "game"
DATA = GAME / "data"
WAVES = DATA / "launch_slice_waves.json"
ROSTER = GAME / "scripts" / "ship_roster.gd"
OUT_JSON = DATA / "art_slot_contract.json"
OUT_MD = DATA / "ART_SLOT_CONTRACT.md"

ART_ROOT = "res://art"

# Folder per slot kind. Explicit so "enemy" cannot become "enemys".
KIND_FOLDER = {
    "ship": "ships",
    "enemy": "enemies",
    "boss": "bosses",
    "projectile": "projectiles",
    "fx": "fx",
    "ui": "ui",
    "background": "background",
}

# Display sizes are in playfield world units (1 unit = 1/20 of the playfield
# width). Each value keeps the current vector silhouette, which is what the
# fallback still draws, so the game looks the same size with or without art.
SHIP_DISPLAY = 1.4
ENEMY_DISPLAY = 0.78
BOSS_DISPLAY = 2.4
BULLET_PLAYER_DISPLAY = (0.20, 0.40)
BULLET_ENEMY_DISPLAY = (0.24, 0.24)
FX_HIT_DISPLAY = 1.0
FX_EXPLOSION_DISPLAY = 2.2

SHIP_CANVAS = (256, 256)
ENEMY_CANVAS = (128, 128)
BOSS_CANVAS = (512, 512)
BACKGROUND_CANVAS = (1024, 1024)
BULLET_PLAYER_CANVAS = (64, 128)
BULLET_ENEMY_CANVAS = (64, 64)
FX_CANVAS = (256, 256)
UI_CANVAS = (1080, 1920)

# Ships: PLAYER-10001 is the required slot. 10003/10004 are the other two roster
# entries, included so a player who picks them also gets art.
REQUIRED_SHIP = 10001
EXTRA_SHIPS = [10003, 10004]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slot(
    slot_id: str,
    kind: str,
    filename: str,
    canvas: tuple[int, int],
    display: object,
    facing: str,
    fallback: str,
    source: str,
    required: bool = True,
    notes: str = "",
) -> dict:
    return {
        "slot": slot_id,
        "kind": kind,
        "file": f"{KIND_FOLDER[kind]}/{filename}",
        "canvas": {"width": canvas[0], "height": canvas[1]},
        "format": "PNG, RGBA8, transparent background, no baked shadow",
        "pivot": [0.5, 0.5],
        "anchor": "center",
        "facing": facing,
        "display": display,
        "fallback": fallback,
        "source": source,
        "required": required,
        "notes": notes,
    }


def ships_slots() -> list[dict]:
    ids = [REQUIRED_SHIP] + [ship for ship in EXTRA_SHIPS]
    slots = []
    for ship_id in ids:
        slots.append(
            slot(
                f"PLAYER-{ship_id}",
                "ship",
                f"PLAYER-{ship_id}.png",
                SHIP_CANVAS,
                {
                    "unit": "world_units",
                    "height": SHIP_DISPLAY,
                    "width": SHIP_DISPLAY,
                    "mode": "fit_canvas",
                },
                "up",
                "vector hull drawn in scripts/player.gd",
                f"slice roster ship {ship_id}; damage row from data/player_start_stats.json",
                required=ship_id == REQUIRED_SHIP,
                notes=(
                    "Nose points to the TOP of the canvas. Runtime draws the texture "
                    "unrotated at the ship position."
                ),
            )
        )
    return slots


def enemy_slots(prefabs: list[str], movement: dict) -> list[dict]:
    slots = []
    for prefab in prefabs:
        info = movement.get(prefab, {})
        turret = bool(info.get("is_turret", False))
        slots.append(
            slot(
                prefab,
                "enemy",
                f"{prefab}.png",
                ENEMY_CANVAS,
                {
                    "unit": "world_units",
                    "height": ENEMY_DISPLAY,
                    "width": ENEMY_DISPLAY,
                    "mode": "fit_canvas",
                },
                "down",
                "vector enemy drawn in scripts/enemy.gd",
                (
                    "spawner rows in data/launch_slice_waves.json; "
                    f"movement listSpeeds[0]={info.get('speed', 'n/a')}, isTurret={turret}"
                ),
                notes=(
                    "Nose points to the BOTTOM of the canvas (the enemy flies down). "
                    + ("Source row is a turret: add a distinct static pose, no engine flare." if turret else "")
                ).strip(),
            )
        )
    return slots


def boss_slots(prefab: str, hp: float) -> list[dict]:
    return [
        slot(
            prefab,
            "boss",
            f"{prefab}.png",
            BOSS_CANVAS,
            {
                "unit": "world_units",
                "height": BOSS_DISPLAY,
                "width": BOSS_DISPLAY,
                "mode": "fit_canvas",
            },
            "down",
            "vector boss drawn in scripts/boss.gd",
            f"Wave_7001 boss row; hp_max {hp:g} from datas/boss_hp.json",
            notes=(
                "Faces the player below (nose DOWN). Keep the core around the canvas "
                "centre: the slice hitbox is a 1.15-unit circle at the texture centre."
            ),
        )
    ]


def extra_slots() -> list[dict]:
    return [
        slot(
            "BG-FIELD",
            "background",
            "BG-FIELD.png",
            BACKGROUND_CANVAS,
            {
                "unit": "world_units",
                "height": 19.2,
                "width": 10.8,
                "mode": "cover_view",
            },
            "none",
            "procedural starfield in scripts/background.gd",
            "visible play area of the 9:16 canvas (10.8 x 19.2 world units)",
            notes="Drawn as the full play area; 1024x1024 is scaled to cover, so keep the edges tileable/safe.",
        ),
        slot(
            "BULLET-PLAYER",
            "projectile",
            "BULLET-PLAYER.png",
            BULLET_PLAYER_CANVAS,
            {
                "unit": "world_units",
                "height": BULLET_PLAYER_DISPLAY[1],
                "width": BULLET_PLAYER_DISPLAY[0],
                "mode": "fit_canvas",
            },
            "up",
            "vector bolt in scripts/projectile.gd",
            "player shot (auto-fire), speed 18 world units/s",
            notes="Nose UP; runtime rotates the texture to the travel direction.",
        ),
        slot(
            "BULLET-ENEMY",
            "projectile",
            "BULLET-ENEMY.png",
            BULLET_ENEMY_CANVAS,
            {
                "unit": "world_units",
                "height": BULLET_ENEMY_DISPLAY[1],
                "width": BULLET_ENEMY_DISPLAY[0],
                "mode": "fit_canvas",
            },
            "down",
            "vector orb in scripts/projectile.gd",
            "enemy shots from decoded Gun_Attack rows or the labelled fallback profile",
            notes="Nose DOWN; runtime rotates the texture to the travel direction.",
        ),
        slot(
            "FX-HIT",
            "fx",
            "FX-HIT.png",
            FX_CANVAS,
            {
                "unit": "world_units",
                "height": FX_HIT_DISPLAY,
                "width": FX_HIT_DISPLAY,
                "mode": "fit_canvas",
            },
            "none",
            "vector ring in scripts/fx_burst.gd",
            "player hit (once per invulnerability window)",
            notes="Plays for 0.28 s; design it to read at 1 world unit tall.",
        ),
        slot(
            "FX-EXPLOSION",
            "fx",
            "FX-EXPLOSION.png",
            FX_CANVAS,
            {
                "unit": "world_units",
                "height": FX_EXPLOSION_DISPLAY,
                "width": FX_EXPLOSION_DISPLAY,
                "mode": "fit_canvas",
            },
            "none",
            "vector burst in scripts/fx_burst.gd",
            "enemy defeat, boss defeat",
            notes="Plays for 0.42 s (boss: 0.9 s); design it to read at 2.2 world units tall.",
        ),
        slot(
            "UI-MENU-FRAME",
            "ui",
            "UI-MENU-FRAME.png",
            UI_CANVAS,
            {"unit": "screen", "stretch": "keep_aspect_covered", "mode": "full_rect"},
            "none",
            "plain menu background in scripts/menu.gd",
            "main menu screen frame (background layer behind the buttons)",
            notes="1080x1920 (9:16). Keep the centre clear: buttons are drawn on top of it.",
        ),
    ]


def main() -> int:
    waves = json.loads(WAVES.read_text(encoding="utf-8"))
    movement = json.loads((DATA / "enemy_movement_slice.json").read_text(encoding="utf-8"))["by_prefab"]

    prefabs: list[str] = []
    for stage in waves["stages"]:
        for row in stage["rows"]:
            for enemy in row["enemies"]:
                if enemy not in prefabs:
                    prefabs.append(enemy)

    boss = waves["boss"]
    boss_prefab = boss["prefab"]
    boss_hp = 0.0
    hp_document = json.loads((DATA / "boss_slice.json").read_text(encoding="utf-8"))
    if hp_document.get("prefab") == boss_prefab:
        boss_hp = float(hp_document.get("hp_max", 0.0))

    slots = ships_slots() + enemy_slots(prefabs, movement) + boss_slots(boss_prefab, boss_hp) + extra_slots()

    ids = [entry["slot"] for entry in slots]
    files = [entry["file"] for entry in slots]
    problems = []
    if len(ids) != len(set(ids)):
        problems.append("duplicate slot ids")
    if len(files) != len(set(files)):
        problems.append("duplicate file paths")
    if "PLAYER-10001" not in ids:
        problems.append("PLAYER-10001 slot missing")
    if boss_prefab not in ids:
        problems.append("boss slot missing")
    for prefab in prefabs:
        if prefab not in ids:
            problems.append(f"enemy slot missing for {prefab}")
    for entry in slots:
        if entry["canvas"]["width"] <= 0 or entry["canvas"]["height"] <= 0:
            problems.append(f"{entry['slot']} has an invalid canvas")

    document = {
        "schema": "windwings.launch_slice.art_slots/1",
        "art_root": ART_ROOT,
        "evidence": "slot list derived from data; art itself is INFERRED until drawn",
        "generated_by": "game/tools/build_art_slot_contract.py",
        "generator_sha256": sha256(Path(__file__)),
        "sources": {
            "game/data/launch_slice_waves.json": sha256(WAVES),
            "game/data/enemy_movement_slice.json": sha256(DATA / "enemy_movement_slice.json"),
            "game/data/boss_slice.json": sha256(DATA / "boss_slice.json"),
            "game/scripts/ship_roster.gd": sha256(ROSTER),
        },
        "rules": {
            "naming": "PNG, exact slot file name, lowercase folder names under res://art/",
            "canvas": "draw at the documented canvas size; the game scales by height, so keep the subject inside a centre-safe area",
            "pivot": "every slot is anchored at its centre (0.5, 0.5)",
            "facing": "ships face UP, enemies and bosses face DOWN, bullets face their travel direction",
            "fallback": "a missing file never crashes: the slice draws the vector shape and logs the slot",
            "no_original_assets": "draw new art; do not extract or copy the original game's sprites",
        },
        "display_notes": {
            "unit": "1 world unit = 1/20 of the 20-unit playfield width; the 9:16 canvas shows about 10.8 x 19.2 units",
            "shipping": "put files under game/art/ so the export packs them; user://art/ is also read for drop-in tests",
        },
        "counts": {
            "total": len(slots),
            "ships": len(ships_slots()),
            "enemies": len(prefabs),
            "bosses": 1,
            "extras": len(extra_slots()),
        },
        "problems": problems,
        "slots": slots,
    }

    OUT_JSON.write_text(json.dumps(document, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    lines = [
        "# ART SLOT CONTRACT — launch slice",
        "",
        "Generated by `game/tools/build_art_slot_contract.py` from `game/data/launch_slice_waves.json`.",
        "Do not edit by hand; re-run the tool after changing the wave selection.",
        "",
        f"- Art root: `{ART_ROOT}` (also read: `user://art/` for drop-in tests)",
        f"- Slots: **{len(slots)}** — ships {len(ships_slots())} · enemies {len(prefabs)} · boss 1 · extras {len(extra_slots())}",
        "- Every slot: PNG RGBA8, transparent background, pivot `(0.5, 0.5)`, anchor centre.",
        "- Ships face **UP**; enemies and bosses face **DOWN**; bullets face their travel direction.",
        "- A missing file never crashes the game: the vector fallback draws instead and the slot is logged.",
        "- Draw new art. Do not extract or copy sprites from the original game.",
        "",
        "| Slot | Kind | File (`game/art/…`) | Canvas | Display | Facing | Fallback |",
        "|---|---|---|---|---|---|---|",
    ]
    for entry in slots:
        display = entry["display"]
        if display.get("unit") == "world_units":
            shown = f"{display['width']:g} × {display['height']:g} units"
        else:
            shown = str(display.get("stretch", display.get("unit", "")))
        canvas = entry["canvas"]
        lines.append(
            "| `{slot}` | {kind} | `{file}` | {cw}×{ch} | {disp} | {facing} | {fallback} |".format(
                slot=entry["slot"],
                kind=entry["kind"],
                file=entry["file"],
                cw=canvas["width"],
                ch=canvas["height"],
                disp=shown,
                facing=entry["facing"],
                fallback=entry["fallback"],
            )
        )
    lines += [
        "",
        "## Per-slot notes",
        "",
    ]
    for entry in slots:
        if not entry["notes"]:
            continue
        lines.append(f"- **`{entry['slot']}`** — {entry['notes']}")
    lines += [
        "",
        "## Where the game reads it",
        "",
        "`game/scripts/art_library.gd` resolves each slot inside `res://art/` first and `user://art/` second.",
        "A file that exists is drawn instead of the vector shape; anything missing is reported by",
        "`game/tools/art_report.gd`, which CI appends to `BUILD_INFO.txt`.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"slots: {len(slots)} (ships {len(ships_slots())}, enemies {len(prefabs)}, boss 1, extras {len(extra_slots())})")
    print(f"boss hp from data: {boss_hp:g}")
    print(f"problems: {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
