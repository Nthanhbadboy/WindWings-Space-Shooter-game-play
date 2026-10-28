# WindWings Godot port

A Godot 4.7.2-targeted portrait 2D vertical-shooter project. The project feature tag is pinned to 4.7.2; engine import and launch remain `RUNTIME_UNVERIFIED`. Open `game/project.godot` in the pinned editor and run the configured main scene (`scenes/main.tscn`). No Android/Windows SDK, store plugin, original APK asset, copied sprite, font, audio, or decompiled executable is included. Ships, enemies, projectiles, pickups, and background are drawn from original vector primitives in GDScript.

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
- `enemy_guns_wave_0000.json` retains distinct `Enemy_Ingame` alternatives. Exact duplicates are collapsed only when all 11 mapped fields (including `bullet_id`) match; for Wave_0000 this is `30014` 2→1 and `30018` 4→2. This is source-row normalization, not an assertion about runtime gun identity. Runtime firing is enabled only where ballistic and schedule fields agree; the component-to-runtime join, aim direction, and coroutine timing remain `INFERRED`/`RUNTIME_UNVERIFIED`. Ambiguous projectile variants are not selected.
- `wave_0000_coin_manifest.json` is a `STATIC_CONFIRMED` list of 49 serialized coin objects (IDs 70011/70012), with no coordinates or flat-denomination claim. The running prototype instead demonstrates catalog item index 1 (`+1Level`) on an 18-second timed cadence, within the source visual-design target of 15–20 seconds. Cadence/placement are `INFERRED`; collection is count-only because item effect values/durations are not asserted.

## M3 economy preview

The `SHOP` overlay is a data-led preview/transaction ledger, not a claim that every original shop row is decoded. The 24 exact `PlayerCosts[]` values feed the player-index table; `-1` stays a sentinel, `0` stays free, and positive values are shown exactly. Player indices are not mapped to ship IDs here. The local prototype wallet starts at 0 because the original starting balance and `Enemy_Data_Balance.GetBonusCoin()` are not decoded; a free row can be claimed locally, while positive-cost rows remain unaffordable until a confirmed currency source is added. This local claim ledger does not equip a ship.

`shop_contract.json` records the decoded 3-band × 5-slot layout, ID offsets, stock preference defaults/reset value 0, and popup quantity start 1 / step 1 / max rule `available_stock - 1`. `MaxStockCount` numeric value, resource prices, and `Shop_Cell` price strings are `UNKNOWN`; the UI does not invent them. `pvp_reward_arrays.json` and the overlay show all six decoded bet/reward arrays verbatim. They are build-time data only; the panel is a preview and does not grant match rewards.

## M4 monetization boundary

The shared `MonetizationProvider`/`MonetizationService` API covers initialization, product query, purchase, restore, and rewarded-ad requests. The Economy overlay's `STORE STUBS` tab exposes three fail-closed adapters: Amazon IAP, HMS IAP + Ads, and Windows Commerce. `iap_products.json` preserves the 170 decoded product IDs, but store prices are not present. Every adapter reports unavailable; test purchase, restore, and ad calls create no receipt, entitlement, wallet change, or reward. `monetization_config.json` sets `real_plugins_enabled: false`; there are no real store plugins, SDKs, credentials, or network calls. Real integration is intentionally deferred until explicitly authorized.

## Evidence and verification

- `STATIC_CONFIRMED` describes decoded/serialized source fields; it does not imply original runtime behavior.
- `INFERRED` is used for new geometry, ambiguous joins, and prototype tuning.
- `UNKNOWN` values (notably original path coordinates, coin placements/denominations, and drop weights) are not fabricated.
- `INFERRED`: the 720×1496 viewport in `project.godot` is a prototype portrait-layout choice, not an original-device resolution. The source camera contract is aspect-ratio based (`datas/camera_scaler_contract.json`), and no target device fixes this exact size; revisit it after device targets are selected.
- `source_sha256` fields in `game/data/` pin the source bytes used for extracted or derived data. They establish provenance, not runtime behavior.
- `RUNTIME_UNVERIFIED`: the sandbox has no Godot executable, so no editor import, game launch, device test, or original-game runtime match is claimed.

Suggested independent checks: run `godot --headless --path game --editor --quit`, then `godot --headless --path game --quit-after 6000`; launch interactively and verify movement, auto-fire, enemy firing/dodging, item collection, pause/replay, and the `SHOP` overlay (24 exact cost rows, `-1` sentinels, six PvP tiers, unknown stock cap). Static script checks performed in this sandbox use `gdparse`/`gdlint`; they do not replace Godot import/runtime checks.
