# WindWings Godot port

A new Godot 4.x project for a portrait 2D vertical shooter. Open `game/project.godot` in Godot 4.x and run the main scene (`scenes/main.tscn`). No Android/Windows SDK, store plugin, original APK asset, copied sprite, font, audio, or decompiled executable is included.

## M1 controls

- Hold and drag with mouse/touch to steer; arrow keys are also supported.
- The ship auto-fires. Keep moving to avoid the practice turret's shots.
- `PAUSE` pauses the world; the restart button appears if hull reaches zero.
- HUD counters report shots, training-target hits, near-misses, and hull.

The M1 training target and firing lane are scaffolding, not a claimed original encounter. M2 replaces them with the decoded `Wave_0000` data. Ship, enemies, shots, pickups, and background are drawn from original vector primitives in GDScript.

## Data/evidence boundaries

- `STATIC_CONFIRMED`: the game baseline hull is 2,500; the decoded `StartMainCannonDamages[0]` is 4,500; the `CD-31002/Enemy_Ingame` projectile profile in `training_gun.json` records bullet ID 80021, damage 400, speed 4, lifetime 8 s, and its serialized burst fields. The player stat index is used as index 0; this project does **not** assert an unresolved index-to-ship-ID mapping.
- `INFERRED`: player firing period 0.24 s, player shot speed 18 units/s, and the training turret's actual aim/spawn lane are explicit prototype choices, not source values. The 0.24 s period is inside the visual-design rhythm target; it is not represented as the original rate.
- `RUNTIME_UNVERIFIED`: no original-game runtime or device test is claimed. Godot editor/runtime verification is independent of the static source-data checks.
- `UNKNOWN`: source data does not bind every shop price, all drop weights/placements, or every wave-path coordinate. Those values will not be fabricated; later milestones retain unknowns in the data model rather than presenting guesses as source truth.

Runtime data under `game/data/` is either a small, provenance-tagged extract from the fetched spec branch or clearly marked prototype tuning. Protected root folders (`docs/spec/`, `datas/`, `tools/`, `tests/`) are read-only for this port.
