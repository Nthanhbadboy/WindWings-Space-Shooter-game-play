# WindWings Godot port

A Godot 4.x portrait 2D vertical-shooter project. Open `game/project.godot` in Godot 4.x and run the configured main scene (`scenes/main.tscn`). No Android/Windows SDK, store plugin, original APK asset, copied sprite, font, audio, or decompiled executable is included. Ships, enemies, projectiles, pickups, and background are drawn from original vector primitives in GDScript.

## Controls

- Hold and drag with mouse/touch to steer; arrow keys are also supported.
- The ship auto-fires. Avoid incoming projectiles and collect the prototype item pickup.
- `PAUSE` pauses the world; the restart button appears on hull loss or wave completion.

## M1 baseline

The baseline hull is 2,500 and the hit-invulnerability interval is 3 seconds (`STATIC_CONFIRMED`). `player_start_stats.json` preserves the decoded 24-entry `StartMainCannonDamages` and `PlayerCosts` arrays, including `-1` sentinels. The weapon uses `StartMainCannonDamages[0] = 4,500`; the index-to-ship-ID mapping is not asserted. Player fire period 0.24 s and projectile speed 18 are `INFERRED` new-game tuning, not original runtime values. The earlier M1 training target is scaffolding and is no longer instantiated by the current main scene.

## M2 first encounter and drops

- `wave_0000.json` preserves the exact `Wave_0000` spawner rows. `STATIC_CONFIRMED`: 42 rows and `sum(copies) = 150`. `INFERRED`: this runtime repeats each row's enemy list `copies` times, giving 883 entry attempts; serialized `count` is not substituted for the enemy-list length.
- `enemy_hp_by_id.json` is the decoded 150-entry HP map. All 15 prefab IDs referenced by `Wave_0000` have an HP row, and the runtime refuses to start if a referenced HP/movement row is missing.
- `enemy_movement_wave_0000.json` preserves each referenced prefab's source `listSpeeds[0]` and `isTurret`. Their source units/Unity movement semantics are not established here. Spawn intervals are serialized; zero-rate entries are spread one per process frame.
- `point`, `point_range`, and `path` formations are `INFERRED` procedural layouts because original path coordinates/placement are unavailable. Rows run concurrently. The wave's `speed` hint is retained but not treated as the enemy movement speed.
- `enemy_guns_wave_0000.json` retains all `Enemy_Ingame` alternatives. Runtime firing is enabled only where ballistic and schedule fields agree; the component-to-runtime join, aim direction, and coroutine timing remain `INFERRED`/`RUNTIME_UNVERIFIED`. Ambiguous projectile variants are not selected.
- `wave_0000_coin_manifest.json` is a `STATIC_CONFIRMED` list of 49 serialized coin objects (IDs 70011/70012), with no coordinates or flat-denomination claim. The running prototype instead demonstrates catalog item index 1 (`+1Level`) on an 18-second timed cadence, within the source visual-design target of 15–20 seconds. Cadence/placement are `INFERRED`; collection is count-only because item effect values/durations are not asserted.

## Evidence and verification

- `STATIC_CONFIRMED` describes decoded/serialized source fields; it does not imply original runtime behavior.
- `INFERRED` is used for new geometry, ambiguous joins, and prototype tuning.
- `UNKNOWN` values (notably original path coordinates, coin placements/denominations, and drop weights) are not fabricated.
- `RUNTIME_UNVERIFIED`: the sandbox has no Godot executable, so no editor import, game launch, device test, or original-game runtime match is claimed.

Suggested independent checks: run `godot --headless --path game --editor --quit`, then `godot --path game` and verify movement, auto-fire, enemy firing/dodging, pickup collection, pause, and restart. Static script checks performed in this sandbox use `gdparse`/`gdlint`; they do not replace the Godot import/runtime checks.
