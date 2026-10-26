# Report 166 — D5 read-only crosswalk of the 2026-10-23 runtime capture

PR12 follow-up claim: `6427801423`.

## Scope and provenance

This report reads only the already-existing files under `docs/apk-analysis/ramus/2026-10-23-phone/` listed in the companion receipt, plus published report 111. No new probe, bridge, ADB, runtime-probe workflow, emulator, native/FDE, or secret workflow was run. No capture source was changed.

The capture summary identifies a Huawei Mate 20 X running Android 10 / Unity 2022.3.62f3 IL2CPP and package `com.Gcenter.WindWings.SpaceShooter.Premium`, described as a repackaged/modded **1.0.69**. The static comparison build is official `com.Wind.wings.Space.Shooter` **1.3.118**. Therefore any comparison is **cross-build only**; it is not same-build runtime parity.

## Direct observations from the archived run

### Health: HUD and `Player_Get_Datas` both show 2500

- `screenshot_running_stage1.png` visibly shows HUD HP **2500**. The image also shows coin count 0 and counter 229; those values are not used to infer progression or entitlement here.
- Archived `/statics` output `statics_Player_Get_Datas.json` reports `StartHp=2500`. It also reports `abi7AddPlayerStartHp=1`, plus 24-element `StartMainCannonDamages`, `StartMainCannonRate`, and `StartWingCannonDamages` arrays. Example at zero-based index 2: main damage 2680 and rate 4.8.
- `health_game.json` records scene `Game` at uptime 88.0177 seconds, frame 4574, timeScale 1. This is a separate artifact; the report does **not** assert that its state was sampled at the exact instant of the screenshot.
- Bounded conclusion: the captured run directly shows HUD HP 2500 and a separate runtime `/statics` readback of `StartHp=2500`. This does not bind a `Player_Health` instance as the owner/applier, prove an upgrade state, establish official 1.3.118 parity, or measure combat damage.

### Reborn fields: no reborn recorded in the end-game snapshot; allowance unknown

The archived `boss_boss_gp.json` is a `SpaceShooter.Gameplay.GP_Datas` snapshot with `isSummary=true`. It reports:

| Field | Captured value | Bounded reading |
|---|---:|---|
| `countReborn` | 0 | No reborn is recorded in this summary snapshot. |
| `rebornNow` | 0 | No current reborn is recorded in this snapshot. |
| `listRebornUseItems` | `[false, false, false, false]` | None of these four captured flags is marked used here. |
| `maxCountReborn` | -1 | Raw sentinel/value only; its semantics are not established. |
| `pvpLife` | 3 | Distinct named field; not equated with extra lives. |

The separate runtime `/statics` type output for `SpaceShooter.Gameplay.GP_Datas` reports the corresponding field names and `maxCountReborn` getter, but does not convert the snapshot into an initial stock or entitlement receipt. These end-game values do **not** establish whether a new player starts with free extra lives, whether a reborn was free/ad/gem eligible, or what `-1` means.

### Player, attack, and controller ownership remain unbound

- `hierarchy_game.json` shows an active scene tree containing `GP_Manager/PLAYER/Player_Ingame`. The hierarchy capture labels attached components generically (`Component`, with count shorthand such as `+2`); it does not identify a live `Player_Controller`, `Player_Health`, or `Player_Attack_N` instance or expose its fields.
- The captured type-list file is filtered by `_Data`; it is not a complete type or live-instance inventory. It cannot support a global-absence claim about component classes.
- The runtime arrays above are `Player_Get_Datas` readbacks. They do not show a particular attack component firing, damage delivered to a target, or a per-object owner mapping. The scene capture includes inactive `Board_Reborn(Clone)` / `Pack_Premium` UI objects; their presence or inactive state does not establish an entitlement or starting grant.
- Report 111 independently states that runtime DPS is **not measured** and that its runtime/static inputs compare different builds. `Live-DPS` remains `MODEL_NOT_MEASURED`.

## Premium and the 24-hour claim

No inspected captured artifact provides a fresh-account/first-launch state, active Premium entitlement flag, expiry/timer, or a 24-hour grant receipt. The `.Premium` package suffix is not proof of a user's entitlement. Accordingly, the new-player 24-hour Premium grant remains **NOT_MEASURED** from this capture.

## Result and handoff

The 23-Oct artifacts answer one narrow runtime question positively: **HUD HP 2500** is visible, and the separate runtime `Player_Get_Datas` readback says **`StartHp=2500`**. They do not answer the 24-hour Premium grant or starting free extra-life allowance. They also do not join Health to a live component owner, identify the active attack/controller instance, establish same-build parity with official 1.3.118, or measure DPS.

The receipt `datas/l3_a5_d5_23oct_runtime_crosswalk.json` pins all inspected files by SHA-256 and preserves raw values separately from these interpretation limits. Builder: `tools/build_a5_d5_23oct_runtime_crosswalk.py`; focused tests: `tests/test_a5_d5_23oct_runtime_crosswalk.py` (3 tests). This is a read-only archival analysis, not authorization to reopen or rerun the runtime lane.
