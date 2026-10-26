# Boss-39001 Spine UnityEvent receiver boundary — phase 8

**Scope:** PR12 `#27-GS` phase-8 claim `6420325366`, a static follow-up to report 136. Resolve the two serialized persistent-call targets on Boss-39001 `Boss_1_Animation` to their exported receiver, inspect available `Enemy_Destroy`/`Enemy_Controller` methods and selected direct callers, then test the bounded route for an edge to node174/native fixture `116cb40`. This is the UnityEvent persistent-call route, not Spine's `AnimationState` callback route and not the Boss19/20/21 Animator clip-event route. No native/FDE or runtime work is in scope.

## Result

**Disposition: `BOSS39001_PERSISTENT_EVENT_RECEIVER_JOIN_PROVEN / EVENT_EXECUTION_AND_NATIVE_FIXTURE_JOIN_UNRESOLVED`.** Both exported persistent calls on the Boss-39001 `Boss_1_Animation` component target the same concrete local `Enemy_Destroy` component, path ID `601110`, on the prefab-root GameObject path ID `185722`. The same-root `Enemy_Controller` record points its serialized `destroyScript` field to that component. The managed target methods are available: `OnDefeated()` forwards statically to the bool overload with argument `true`; `OnBusrtItems()` has a substantial managed body. This closes a serialized receiver-identity gap, not an execution gap: no claim is made that Unity invoked either event or that any destruction/effect ran.

The selected managed bodies and serialized edge do not identify node174, fixture `116cb40`, a native clock/output holder, or a native interpolation input. Spine callback setup, persistent UnityEvents, and Animator clip-event dispatch remain distinct evidence paths.

## Serialized local join

- Boss-39001 `Boss_1_Animation` component `674445` is enabled on GameObject path `187025`. Its serialized `defeatEvent` has one persistent call to path `601110`, method `OnDefeated`; its `burstEvent` has one persistent call to the same path, method `OnBusrtItems`. Both calls have `m_Mode=1` and `m_CallState=2` in this export. These fields describe configured persistent calls, not observed invocation.
- `Enemy_Destroy.jsonl.gz` exports component `601110` on GameObject `Boss-39001`, GameObject path `185722`, enabled. Its serialized fields include `pointBurst` PPtr `(file 0, path 384934)`, `isNoPool=true`, and `delayDestroy=0.0`.
- `Enemy_Controller.jsonl.gz` exports component `620998` on that same root GameObject path `185722`; its `destroyScript` PPtr is `(file 0, path 601110)`. This is a local serialized component-reference join within the checked prefab export.
- Across the 140 checked top-level compressed JSONL typetree exports, `601110` has one typed record (the `Enemy_Destroy` above); path `384934` has no top-level typed record. The absent typed `pointBurst` target is an export-scope boundary, not evidence that the referenced object is globally absent.

## Available managed receiver behavior

`Enemy_Destroy.asm.txt` and its matching method metadata provide these static method-body facts:

- `OnDefeated()` at RVA `0x1584E94` sets `w1=1` and branches to `OnDefeated(bool)` at `0x1584E9C`. Thus the no-argument managed entry has a static forwarding path to that overload with `true`; it does not establish that the serialized UnityEvent invoked it.
- The bool overload calls the local `Destroyed()` helper at `0x15850BC`, then has further conditional destruction/pooling paths. The effects of its indirect/helper calls are not promoted beyond what the selected body establishes.
- `OnBusrtItems()` at RVA `0x15854D8` is a substantive body. It reads an instance slot at `+0x38`, performs checks and calls helper/callback targets. Although the serialized component has a `pointBurst` reference, the selected exports do not contain a field-layout mapping that proves `+0x38` is that serialized field; that association remains a candidate, not a resolved field-offset identity.
- `Enemy_Controller.OnTakeDamage` directly calls its own `OnDieWhenZeroHp` at `0x1582DD8`. That method later loads an instance slot at `+0x50` and performs an indirect virtual dispatch with argument zero. `Enemy_Controller.Destroyed` also dispatches indirectly through a slot with argument one. The serialized `destroyScript` PPtr is proven above, but the available selected metadata does not resolve either `+0x50` slot to that field or the virtual target to a concrete runtime dispatch.

## Caller cross-check — keep instances separate

The selected ASM files contain direct transfers to the same managed method entrypoints, but these do **not** establish callers on the Boss-39001 component instance:

- `Boss_AttackPhases.<OnGunDie>b__10_0` directly calls `OnDefeated()` at `0x153290C` and tail-branches to `OnBusrtItems()` at `0x153292C`. No serialized `Boss_AttackPhases` instance join to Boss-39001 is present in the selected exports.
- `Boss1_Director.Defeat` calls `OnBusrtItems()` at `0x1500068`, then tail-branches to `OnDefeated(bool)` with `w1=0` at `0x1500084`. Its exported record is path `582209` on **Boss-39002**, with `parentDestroy` PPtr `601111`; this is a different object from Boss-39001's receiver `601110` and is explicitly not joined to it.
- `Enemy_Destroy.OnDestroyWhenHitPlayer` and `OnDestroyByZeroHp` also call `OnBusrtItems()` internally. These are method-level static edges, not evidence that either lifecycle/death path ran for path `601110`.

## Boundary and provenance

The positive chain is `Boss_1_Animation` persistent-call PPtr → `Enemy_Destroy` path `601110` → same-root `Enemy_Controller.destroyScript` PPtr. Available managed bodies show destruction/effect/pooling-oriented code, but there is no evidenced game-side edge from that route to node174, fixture `116cb40`, a native clock/output holder, or native interpolation state. The route remains static and bounded; no UnityEvent execution, death, burst, pool transition, runtime readback, or gameplay parity is asserted.

The companion `datas/l3_a5a74747_game_side_spine_unityevent_receiver_boundary.json.gz` records the selected PPtr joins, method anchors, scoped incoming-call examples, missing path `384934` export, native non-join, and source SHA-256 pins. Pins include the inherited checked typetree slice, phase-7 lineage, and the selected managed ASM/metadata. Static-only; no runtime, `libunity.so` FDE, geometry, or rendering work was performed.
