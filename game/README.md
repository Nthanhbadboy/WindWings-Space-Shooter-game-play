# WindWings Godot port

A Godot 4.7.2-targeted portrait 2D vertical-shooter project. The project feature tag is pinned to 4.7.2; engine import and launch remain `RUNTIME_UNVERIFIED` in this repository's sandbox. Open `game/project.godot` in the pinned editor and run the configured main scene (`scenes/menu.tscn`). No Android/Windows SDK, store plugin, original APK asset, copied sprite, font, audio, or decompiled executable is included. Ships, enemies, projectiles, pickups, bosses and background are drawn from original vector primitives in GDScript; the placeholder tones in `audio/` were synthesized for this repository.

## M2 launch slice (this build)

Flow: **main menu → ship select → five real campaign waves → boss → victory (stars + save) or game over → retry**, plus **pause** and **audio settings**. The M1–M4 screens (training target, coin ledger, store stubs) are kept in the project as files but are no longer wired into the menu; the slice is the playable path.

### What the slice runs

| Element | Source | Slice behaviour |
|---|---|---|
| Waves | `datas/waves.json`, five consecutive real waves `Wave_0016 … Wave_0020` | Whole spawner rows are copied in source order under a per-wave budget of 90 enemy entries; no row value is edited. 343 entries in total. |
| Boss | `datas/waves.json` `Wave_7001` + `datas/boss_hp.json` + `datas/boss_anim_events.csv` | `Boss-37001`, HP 225,000, row `copies = 2` kept, shots at the 14 `Shoot` times of the `Attack2` clip (0.467 s … 6.6 s, 7.0 s loop). |
| Enemy HP | `datas/enemy_hp_by_id.json` | Every prefab in the slice has a decoded HP row; the run refuses to start otherwise. |
| Enemy movement | `reverse-engineering/scriptableobjects/Enemy_Movement.csv` | `listSpeeds[0]`/`isTurret`; runtime unit interpretation is not asserted. |
| Enemy guns | `reverse-engineering/scriptableobjects/Gun_Attack.csv` | Decoded profile where the rows agree; otherwise a labelled `INFERRED_FALLBACK` profile built from the median of all 458 serialized rows (only 42 of 150 wave IDs have gun rows). |
| Derived data | `game/tools/build_launch_slice_data.py` | Regenerates every `*_slice.json` file and pins the SHA-256 of each source table in `data/slice_provenance.json`. |

### Numbers the slice obeys (`scripts/launch_rules.gd`, `tests/run_tests.gd`)

- Playfield **20 × 25 units** (`border` w/x/y/z = 15 / −10 / 10 / −15). Source coordinates are y-up; gameplay nodes convert with `LaunchRules.source_to_world()`.
- Collision radius **15 source units** for enemies and bullets (`Bullet_Linearly.border.w`). The slice renders the projectile collider at `15 × 0.01 = 0.15` world units — the conversion factor is a documented slice decision, because a literal 15-unit collider would span 75% of the playfield.
- Spawner rate **median 1.0 s**, `y_spawn` **9.6** on the majority of rows. The slice keeps the real off-screen spawn heights (12.0, 15.0) instead of clamping them; those enemies fly in.
- Player hull `2500 × (1 + 0.18 × TechStatPoints(0) + ability7)`; a fresh save has both inputs at 0, so the slice starts at 2,500.
- `levelDelta = [1, 2, 3.6, 3.6]` scales **score only**. Enemy HP and enemy counts are never multiplied by mode; `LaunchRules.hp_multiplier()` returns 1.0 for every mode and the tests assert it.
- Stars: tiers `[.20, .45, .80]` (mode 0) against the entries actually spawned; a clear records the best result per stage/mode and recomputes the saved total.

### Controls and screen scaling (new design)

- Drag with the mouse (or a touch) to steer; arrow keys also move the ship. Fire is automatic.
- `P` / `Esc` pauses. Pause keeps music playing while SFX is silenced (`AudioListener.pause` analogue).
- The design canvas is 720×1280 (9:16) with `stretch/aspect = keep`, so a 16:9 desktop window shows the portrait play area letterboxed inside pillar bars. This portrait-on-16:9 rule is a **new design decision**, not a reconstruction of the original device layout.

### Save / load (`scripts/save_store.gd`, `data/save_contract.json`)

Key names, types and defaults follow `docs/spec/MISSING_FOR_NEW_GAME.md` §2.3 and §2.3b: `StarCount` (sentinel −1), `StarStageMaster{stage}_{mode}`, `PlayerUsed{slot}`, `PLAYER_RANK{ship}` (default 2), `PLAYER_DEFAULT_SKIN{ship}` (−1), `TALENT_SELECTED` (−1), `PLAYER_DEVICE_{ship}_{slot}` (−1), `StageTarget`, `ZoneUnlocked`, `TUTORIAL`, trial keys and the audio keys. Repair rules that the contract documents are implemented and tested: `PlayerUsed ≤ 0` rewrites both slots, `PLAYER_RANK ≤ 1` is floored to 2, a negative `DroneUsed` becomes 0, `PlayerUnlocked` is true below ship 10003.

Storage is a Godot `user://launch_slice_save.json` written through a temp file and rename. Atomicity, migration and cloud sync are **new design** — the source contract proves none of them. Getters are pure; the source getters' side effects (`StageTarget` +1, `TUTORIAL` → 6) are deliberately not reproduced.

### Audio (`scripts/audio_mixer.gd`, `data/audio_defaults.json`)

`datas/audio_rules.json` fixes `MUTE_AUDIO` (int, default 0, predicate `stored == 1`), `VolumeSound` (float, default ≈0.73) and `VolumeMusic` (float, default ≈0.3). The slice applies them to `SFX`/`Music` buses. Every clip is a synthesized placeholder tone; the mapping to source clip enum values is a naming convention only.

### Tests

```bash
godot --headless --path game --script res://tests/run_tests.gd   # prints TESTS_OK or TESTS_FAILED
godot --headless --path game --quit-after 120                    # menu smoke
godot --headless --path game res://scenes/main.tscn --quit-after 900   # run scene smoke
```

The rule tests cover the spec numbers, the save contract, star tiers, the boss timeline, audio defaults, the ship→combat-index mapping and the data pins. CI (`.github/workflows/windows-export.yml`) runs them plus both smoke runs before it exports a Windows executable, and fails the job on `SCRIPT ERROR` output.

### Evidence labels used in this build

- `STATIC_CONFIRMED` — values decoded from the source tables listed above.
- `INFERRED` — runtime joins and layout the source does not serialize: enemy x placement, multi-enemy row stacking, boss station/flight, turret descent, `INFERRED_FALLBACK` gun profile, contact damage, score values, the 40-projectile cap.
- `NEW_DESIGN` — portrait-on-16:9 scaling, mouse+keyboard controls, save atomicity, placeholder tones and vector art.
- `RUNTIME_UNVERIFIED` — no Windows run of this slice build was performed by this repository; a green CI export is not a runtime claim.

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
