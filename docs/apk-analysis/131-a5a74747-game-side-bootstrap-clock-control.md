# Game-side bootstrap and clock/control trace — phase 2

**Scope:** PR12 round-81 `#27-GS` phase-2 claim. Static analysis only. This report traces managed game-side bootstrap candidates and clock/control writers relevant to native `116cb40` / handoff 120. It keeps those game-side observations separate from AI-1's native `libunity.so` FDE lane and from the prepared native harness state. No runtime readback, emulator, Frida, parity, or live-DPS measurement was performed.

## Result

**Disposition: `NO_GAME_SIDE_BOOTSTRAP_PATH_PROVEN / GLOBAL_UNITY_TIMESCALE_WRITERS_IDENTIFIED`.** The bounded managed evidence identifies global Unity `Time.timeScale` writers, a gameplay-level `GP_Time` abstraction, and a saved-speed UI value. None is statically connected to the native node clock fields (`+0x60` / `+0x178`), the node's clip/cache/output inputs, or the prepared service/queue/chunk represented by native `116cb40`.

This is a bounded result, not proof that no such path exists anywhere in the application. Raw ASM coverage is incomplete, direct-call inventories do not close indirect dispatch, and some managed library bodies are absent. The native peer reports describe prepared fixture inputs rather than an observed game-side startup sequence.

## Native handoff boundary

Read-only review of AI-1's peer reports 120/121 (peer branch observed at `719f6e037`) says the `116cb40` service → queue → chunk arrangement is explicitly prepared synthetic fixture state. The captured native factory caller at `6d2950..6d29e4` is not executed by those reports; post-factory clip/clock bindings remain fixture inputs. That evidence does not establish Android process-global initialization or a game-side managed caller.

The native reports' relevant node fields are `+0x118` clip blob, `+0x128` cache, `+0x130` output holder, `+0x1d0` clip pointer, and current/previous clocks `+0x60` / `+0x178`; controls include `+0x184`, `+0x188`, `+0x18c`, and `+0x1fc`. No C# object/dataflow/call edge in this phase reaches those fields. The peer native evidence is used only as a boundary for comparison; this report does not extend or reproduce the native lane.

## Managed bootstrap and animation candidates

- The existing phase-1 trace ends at game-side `Animator.SetTrigger` control requests. It found no demonstrated managed write to the native node's clip, output, cache, pose, or prior-clock fields. The 13 unique direct `SetTrigger` callsites remain control calls, not proof of node bootstrap or pose production; see report 130.
- Metadata declares Unity Playables types (`PlayableGraph`, `AnimationClipPlayable`, and `AnimatorControllerPlayable`), but the bounded game-side ASM scan did not establish their use as a route into the prepared native service or node.
- Spine metadata declares `SkeletonMecanim` (TypeDefIndex 8602) and a nested `MecanimTranslator` (TypeDefIndex 8601) that holds an `Animator` reference and exposes `Initialize`, `ApplyAnimation`, and `LateUpdate`. No matching raw ASM method body was found. The bounded prefab audit lists resolved `SkeletonAnimation` components, not `SkeletonMecanim`; this is not proof that no Mecanim component exists elsewhere, and it does not bind the bridge to the native fixture.
- `Home_Loader.<Start>d__5.MoveNext` calls Unity `Time.set_timeScale(1.0)` at `0x13BE510`. This is a home/scene clock reset, not evidence of native service creation.

**Bootstrap finding:** no inspected managed method creates or binds the synthetic service/queue/chunk, resolves the native node, or passes its clip/cache/output/clock pointers. A managed animation API call or a serialized Animator/controller asset is not promoted to a service/bootstrap edge without that missing join.

## Unity global clock writers

`UnityEngine.Time` is TypeDefIndex **7880**. Its `set_timeScale(float)` wrapper is RVA **`0x2786ED8`** and `get_timeScale()` is RVA **`0x2786EB0`**. A normalized-address scan of the tracked raw ASM corpus found **29 unique direct transfers** to the setter: **25 `BL` calls and four unconditional tail branches (`B`)**, with mirrored ASM copies deduplicated by site RVA. The four tail branches matter: a BL-only scan would miss the three GP_Tutorials restore paths and the GP_Controller smoothing return.

| Caller group | Setter sites | Value / flow visible at the call |
|---|---|---|
| `Board_Endgame` | `OnEnable` `0x1269D50`; `BackToMap` `0x126DBF4`; `Restart` `0x126E8C0`; `Continue` `0x126ED5C` | `1.0` at each site |
| `Home_Loader.<Start>d__5.MoveNext` | `0x13BE510` | `1.0` |
| `GP_Endgame` | `VictoryNow` `0x14F06FC`; `MoveOutPlayer` `0x14F0780`; `OpenEndgame` `0x14F1050`; `<CheckEndgame>d__4.MoveNext` `0x14F199C` | `1.0` at each site |
| `GP_Manager` | `CheckReborn` `0x14F4CBC`; `ActiveBoardReborn` `0x14F4EA8`; `OnExitReborn` `0x14F4FE8`; `OnReborn` `0x14F52C4`; `OpenEndgame` `0x14F5740` | `1.0`, `0.0`, `1.0`, literal-pool `0.05`, `1.0`, respectively |
| `GP_Starter.<StartScale>d__18.MoveNext` | `0x14F94D0` | literal-pool `0.05` |
| `GP_Tutorials.<TutChangeGameSpeed>d__55.MoveNext` | `0x14FC100` | `0.0` |
| `GP_Tutorials.<TutChangeGameSpeedBoss>d__58.MoveNext` | `0x14FC310` | `0.0` |
| `GP_Tutorials.<TutDrones>d__48.MoveNext` | `0x14FC67C`; `0x14FC8A4` | `0.0`; value returned by `GP_Time.get_timeScale()` |
| `GP_Tutorials.<TutTalents>d__52.MoveNext` | `0x14FCF04`; `0x14FCF9C` | `GP_Time.get_timeScale()`; `0.0` |
| `GP_Tutorials.<TutTransform>d__42.MoveNext` | `0x14FD4C4`; `0x14FD5BC`; `0x14FD6AC`; `0x14FD738` | `0.0`; literal-pool `0.1`; literal-pool `0.1`; `0.0` |
| `GP_Tutorials.OnResumeGame` | tail branch `0x14F5BF8` | returns `GP_Time.get_timeScale()` directly to Unity's setter |
| `GP_Tutorials.<OnPressedButtonQuitTutSettings>b__37_0` / `b__37_1` | tail branches `0x14FB604`, `0x14FB6D4` | each returns `GP_Time.get_timeScale()` directly to Unity's setter |
| `GP_Controller.Update` | tail branch `0x14CE9E8` | computes a linear step from current Unity scale toward `GP_Time.timeScale`, using a `0.1` multiplier, then tail-branches to the setter |

The `0.05` and `0.1` literal-pool values are resolved in the corresponding raw constant-summary JSON files. These are global Unity clock writes; the separate writes to tutorial/game-state fields in the same methods are not node-clock writes.

## Managed speed state and direct readers

`SpaceShooter.Gameplay.GP_Time` is TypeDefIndex **1877**. Metadata declares static `timeMulti`, `rawTimeScale`, and `timeSlowed` fields, plus `timeScale` accessors (`get_timeScale` RVA `0x14F972C`, `set_timeScale` RVA `0x14F97F4`). The bounded raw ASM corpus contains **seven** direct calls to the getter. Its setter body/callers were not recovered in this slice: there are **zero** direct BL/tail-branch sites to `0x14F97F4` in the scanned ASM corpus. The declared fields and property signatures alone do not prove the implementation or a native-node mapping.

The six direct calls to Unity `Time.get_timeScale()` (`0x2786EB0`) are in `GP_Controller.OnMoved` and `GP_Controller.Update`. `OnMoved` combines the global time scale and `Time.deltaTime` in movement calculations. `Update` compares the current Unity scale with `GP_Time.timeScale`; in the branch that restores the target, it calculates `(target - current) * 0.1 + current` and sends that value to Unity `Time.set_timeScale`. This is a concrete managed global-clock smoothing path, not a write to node `+0x60` or `+0x178`.

The broader bounded time-API scan also found direct reads of `Time.time` (39), `Time.deltaTime` (23), `Time.unscaledDeltaTime` (7), and `Time.unscaledTime` (2). It found no direct `Time.get_fixedDeltaTime` branch in the scanned ASM corpus. These counts describe the scanned corpus only.

### Saved-speed UI is not yet a native-clock edge

`TimeSlider` is TypeDefIndex **255** and declares `SaveSpeed` (`get_SaveSpeed` RVA `0x1328630`, `set_SaveSpeed` RVA `0x13286EC`). The bounded callers are in `Tut_Settings1` (TypeDefIndex 257), which has a `sliderTimeScale` field:

- `Tut_Settings1.<Start>b__11_0(float amount)` stores the slider-derived float through `TimeSlider.set_SaveSpeed` at `0x1329610` (the same callback also has a direct getter site at `0x13295E8`).
- `Tut_Settings1.OnPressedButtonSave` calls `TimeSlider.get_SaveSpeed` at `0x1329364`; based on the value it writes either the current slider value or a `-1.0` sentinel through `set_SaveSpeed` at `0x1329398`, then reads the saved value again at `0x13293A0`.
- The tracked ASM corpus contains six direct `get_SaveSpeed` calls and two direct `set_SaveSpeed` calls, all in `Tut_Settings1`. This demonstrates saved UI speed state, not that it is applied to a native node. No direct edge from these calls to `GP_Time.set_timeScale`, Unity's node clocks, or the prepared fixture was found in the bounded direct-call scan.

`Board_Pause` metadata also declares speed arrays and `freezeTime` / tutorial-time-scale flags, but no matching raw method body was present in the bounded set. Those declarations remain candidate UI/control state only.

## Unresolved edges and limits

1. Global Unity `Time.timeScale` is distinct from the native node's clock fields. No C# store or pointer/dataflow edge to `+0x60` or `+0x178` was recovered.
2. `GP_Time` gives a managed clock abstraction and is read by gameplay/tutorial paths, but its getter/setter implementation and any binding to native node state remain unresolved.
3. `TimeSlider.SaveSpeed` is written as UI preference state; its application path is not proven by the available direct callers.
4. Playables and `SkeletonMecanim` metadata are candidate API/library routes only. No game-side object binding, raw use path, service constructor call, or native handoff edge was found.
5. Peer reports 120/121 describe fixture setup and a captured, unexecuted native caller. They do not establish original game-side bootstrap or runtime execution.

Accordingly, the phase-2 conclusion is limited to **managed global clock/control behavior identified; native service bootstrap and node-clock provenance unproven**. Do not restate this as runtime parity, a native node clock writer, a game-originated `116cb40` setup, or proof of global absence.

## Provenance and verification

The companion `datas/l3_a5a74747_game_side_bootstrap_clock_control.json.gz` records normalized setter/getter callsites, value-flow classifications, the `GP_Time` and `TimeSlider` edges, peer-native boundary notes, coverage limits, and SHA-256 pins for the reviewed dump, reports, raw ASM, and constant-summary inputs. Its setter inventory includes both direct `BL` and tail-branch `B` transfers, and deduplicates mirrored callsite RVAs. No runtime readback, parity test, live-DPS measurement, emulator/Frida route, or `libunity.so` FDE analysis was used.
