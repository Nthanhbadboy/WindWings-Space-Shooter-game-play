# Game-side event and lifecycle entrypoint audit — phase 4

**Scope:** PR12 `#27-GS` phase-4 claim `6419656724`, a bounded static follow-up to report 132. This phase audits serialized AnimationEvent receiver candidates, UnityEvent persistent calls, and managed lifecycle/call edges for Boss19/20/21 attack phases and the tutorial speed controls. It does not enter AI-1's native lane.

## Result

**Disposition: `ANIMATOR_CLIP_EVENT_TO_SAME_GAMEOBJECT_HANDLER_CANDIDATE_PROVEN / DYNAMIC_REGISTRATION_AND_ACTIVATION_UNRESOLVED`.** New positive static evidence links serialized clip-event records for `Boss-39019/20/21` to `BossAnimationEvents` handler candidates on the same Animator GameObject. For Boss20 and Boss21, most event string values also occur as serialized attack-data keys on the associated `Boss*_AttackTypes` object. Managed code contains a plausible dictionary/delegate dispatch mechanism for those values.

The critical runtime/activation edges are still missing: no direct caller of `Boss_AttackPhases.StartAttack` or `Boss_AttackTypes.RegisterEvents` was found in the bounded raw-ASM corpus, and the clip events are named `OnStartAttack`—they are **not** calls to the separate C# method `Boss_AttackPhases.StartAttack`. No event or object path reaches native fixture `116cb40`.

## Serialized boss object and clip-event joins

Each serialized `Boss*_AttackPhases` record contains PPtrs for inherited `attackTypes`, `animationEvents`, and `animators`. The event inventory associates the clip events with the same Animator path ID and GameObject as the exported `BossAnimationEvents` component:

| Prefab | `AttackPhases` component | `attackTypes` PPtr | `animationEvents` PPtr | Animator PPtr / event GO | `BossAnimationEvents` component | Clip-event uses: `OnStartAttack` / `OnStopAttack` / `OnStateExit` |
|---|---:|---:|---:|---|---:|---:|
| `Boss-39019` | `689448` | `689449` (target export missing) | `665857` | Animator `498950` / GO `230437` | `665857` on `Enemy_Ingame/Body` | `50 / 11 / 15` |
| `Boss-39020` | `634645` | `634644` | `676306` | Animator `495696` / GO `150160` | `676306` on `Enemy_Ingame/Body` | `46 / 16 / 13` |
| `Boss-39021` | `615301` | `615302` | `617279` | Animator `498650` / GO `230436` | `617279` on `Enemy_Ingame/Body` | `41 / 21 / 13` |

For Boss20 and Boss21, their exported `Boss*_AttackTypes` records independently point back to the same `animationEvents` PPtr as the corresponding `AttackPhases` record. The `BossAnimationEvents` typetree records have `m_Enabled=1` and GameObject IDs equal to the Animator/event owner GameObject IDs above. Boss19's serialized `attackTypes` target `689449` has no corresponding `Boss19_AttackTypes` typetree export in this bounded corpus.

The `event-receivers.json.gz` inventory labels these as **`same-gameobject-method-candidate`** records. In this slice it contains 76 Boss19, 75 Boss20, and 75 Boss21 clip-event uses; every listed `OnStartAttack`, `OnStopAttack`, and `OnStateExit` use has the matching same-GameObject `BossAnimationEvents` candidate. The data argument on the two attack handlers is a string such as `Attack1-1` or `Attack2-2`; it is not a direct invocation of `Boss_AttackPhases.StartAttack`.

### Event-string ↔ attack-data key check

The serialized `Boss20_AttackTypes` and `Boss21_AttackTypes` records expose attack-data keys. Their keys agree with most or all distinct clip-event data strings in the corresponding prefab slice:

| Prefab | `OnStartAttack` uses / distinct data strings | Distinct strings matching exported attack-data keys | Unmatched | `OnStopAttack` distinct strings matching keys |
|---|---:|---:|---|---:|
| `Boss-39019` | `50 / 17` | not measurable | `Boss19_AttackTypes` export absent | not measurable |
| `Boss-39020` | `46 / 15` | `14 / 15` | `AttackSilk` | `5 / 5` |
| `Boss-39021` | `41 / 10` | `10 / 10` | none | `8 / 8` |

This is a static serialized-string/key join, not proof that the event fired or that the action table was populated. `AttackSilk` remains unmatched by the exported Boss20 attack-data arrays; it may belong to an omitted data category or indicate a missing join.

## Managed dispatch mechanism and unresolved registration

`BossAnimationEvents` (TypeDefIndex **205**) declares `allStartAttackActions` at `this+0x28`, `allStopAttackActions` at `this+0x30`, and `onStateExit` at `this+0x20`. Its raw ASM shows:

- `OnStartAttack(string animName)` at RVA **`0x131DAA8`** looks up the string in the first dictionary (helper call at `0x1960758`) and calls a found delegate indirectly (`BLR x9` at `0x131DB08`).
- `OnStopAttack(string animName)` at **`0x131DB98`** performs the analogous lookup through the second dictionary and then calls the delegate indirectly.
- `OnStateExit()` at **`0x131DA8C`** invokes its delegate field indirectly.

The base `Boss_AttackTypes` (TypeDefIndex **2062**) declares `animationEvents` at `this+0x20` and has virtual `RegisterEvents()` at RVA **`0x1533CC4`**. Its available body initializes two dictionaries on the `BossAnimationEvents` object, walks attack-data arrays, and constructs key-bound delegate entries. The serialized Boss20/21 `animationEvents` PPtrs and the clip-event string/key matches are consistent with that static mechanism if registration occurs.

But the invocation edge is not recovered: there are **zero direct `BL`/tail-`B` callsites** to `RegisterEvents` in the tracked `reverse-engineering/raw/il2cpp-consts/*.asm.txt` set. A virtual, reflection, lifecycle, delegate, or missing-corpus caller remains possible. The matching dictionary keys do not prove runtime dictionary contents.

The two recovered Boss20 `onDestroy` persistent calls are adjacent attack-data effects, not phase activation: `allDataFixedAttack[5].onDestroy` targets `Boss20_AttackTypes.OnSpawnPoisionZone`, and `[15].onDestroy` targets `OnSpawnBullets`, both on component `634644`. The bounded persistent-call inventory contains no target named `StartAttack`, `OnStartAttack`, `OnStopAttack`, or `RegisterEvents`. Its own status is provisional: selected serialized components only, with dynamic listeners excluded.

## Tutorial speed entrypoint

`GP_Tutorials.StartTutChangeGameSpeedBoss()` is a public managed method at RVA **`0x14FA54C`**. Its body directly calls the coroutine builder `TutChangeGameSpeedBoss()` at **`0x14FA6B8`** (callsite `0x14FA698`) and then tail-branches to Unity `StartCoroutine` at `0x278276C`. However, the bounded raw-ASM search found zero direct incoming `BL`/tail-`B` sites to `StartTutChangeGameSpeedBoss`, and the extracted persistent-call inventory has no matching persistent target. This shows a path *inside* the public entrypoint, not a path into it. Reflection, dynamic listeners, and absent serialized exports remain possible.

The phase-3 `GP_Tutorials` → `Tut_Settings1` object reference and the phase-2 `TimeSlider.SaveSpeed` findings remain unchanged: no evidenced connection from this speed-control UI to `GP_Time`, a native node clock, or the prepared native fixture.

## Native boundary and limits

The event candidates terminate at managed `BossAnimationEvents` dictionaries and unresolved delegates. Neither the serialized object graph nor the event handlers connect to native service/queue/chunk state or native node clip/cache/output/current/previous-clock fields. This report makes no runtime-playback or pose-application claim and does not modify or extend AI-1's native/FDE work.

PPtr path IDs are file-scoped. Joins here are limited to the matching PPtr IDs, GameObject IDs, prefab names, and bounded event-receiver export; numeric identity is not promoted across unrelated source files. The `event-receivers` audit itself warns that overload compatibility and runtime dispatch are unverified. Static-only: no runtime, emulator, Frida, parity, live-DPS, geometry/render, or `libunity.so` FDE analysis was performed.

## Provenance and verification

The companion `datas/l3_a5a74747_game_side_event_entrypoint_audit.json.gz` captures the boss/event joins, event-data key comparisons, persistent-call slice, direct-call search results, and SHA-256 pins. The bounded negative direct-call scan pins all **139** top-level raw ASM files individually; supporting serialized records, event inventories, managed method metadata, and reports 131–132 are also pinned.
