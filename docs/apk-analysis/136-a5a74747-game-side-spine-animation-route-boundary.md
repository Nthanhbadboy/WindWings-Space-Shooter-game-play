# Game-side Spine animation route boundary — phase 7

**Scope:** PR12 `#27-GS` phase-7 claim `6420177983`, a bounded static audit of the separate `Boss-39001` Spine route identified in reports 130/132. It traces the serialized `Boss_1_Animation` → `SkeletonAnimation` edge and available managed callbacks, then tests whether this game-side route identifies the node174 / native fixture `116cb40`. It does not inspect native implementation or enter AI-1's `libunity.so` lane.

## Result

**Disposition: `BOSS39001_SPINE_COMPONENT_AND_MANAGED_CALLBACK_ROUTE_PROVEN / NATIVE_FIXTURE_JOIN_UNRESOLVED`.** The serialized `Boss-39001` `Boss_1_Animation` component points to a concrete `SkeletonAnimation` record. Its managed `Start()` body registers Spine event/completion callbacks and selects a Spine animation; the completion callback reaches `BossWork`, which selects further Spine animations and invokes managed delegates/UnityEvents.

This is a game-side Spine route, distinct from the Boss19/20/21 Animator clip-event route in reports 132–135. The static chain terminates at Spine/Unity managed APIs and serialized effects. It does not identify a managed output or object edge to node174, native fixture `116cb40`, or native clock/output fields. No callback execution or runtime playback is claimed.

## Serialized component join

For the exported `Boss-39001` record, `Boss_1_Animation` component `674445` is on GameObject `Enemy_Ingame/Body/Boss 1` (path ID `187025`) and is enabled. Its `skeAnim` PPtr `(m_FileID 0, m_PathID 602882)` matches the `SkeletonAnimation` component record `602882` at `Boss-39001/Enemy_Ingame/Body/Boss 1/Skeleton`, GameObject path ID `163303`. That component points to skeleton-data path ID `580611`; the bounded `spine-prefabs.json` export independently records the same component, GameObject, skeleton-data reference, and prefab root.

The serialized controller strings on `Boss_1_Animation` are `Xuathien`, `Baydi`, `Dead`, `Attack1–3`, `Chuyensangattack2`, and `Chuyensangattack3`. Its `defeatEvent` and `burstEvent` each have one persistent call to local target path ID `601110` (`OnDefeated` and `OnBusrtItems` respectively). These are serialized managed event targets; they do not bridge to native interpolation state.

## Managed Spine callback path

`Boss_1_Animation` (TypeDefIndex `141`) has raw managed ARM64 disassembly and matching method declarations:

- `Start()` at RVA `0x12473EC` obtains the `SkeletonAnimation.AnimationState`, registers `AnimationState.add_Event` (callsite `0x12474C0`) and `AnimationState.add_Complete` (`0x1247508`), then calls `AnimationState.SetAnimation` (`0x1247530`). The method bodies are static evidence of a possible Unity lifecycle setup path, not evidence that `Start()` ran on this serialized record.
- `SkeletonAnimation_AnimationState_Complete(TrackEntry)` at RVA `0x1247C38` tail-branches to `BossWork(string)` at `0x1247C58` (`B` at `0x1247C50`). `BossWork` compares the incoming entry name to serialized state strings, calls `AnimationState.SetAnimation` for recognized transitions, and uses an indirect `nextTurn` delegate or invokes the serialized defeat event in its other branches.
- `SkeletonAnimation_AnimationState_Event(TrackEntry, Event)` at `0x1247DA8` is a single `RET`; no event-side gameplay logic is present in that method body.
- `ClearGuns()` and the attachment helpers also call Spine `AnimationState.SetAnimation`, `SkeletonRenderer.get_Skeleton`, and `Skeleton.SetAttachment`, with separate Unity event, pooling, audio, and transform calls. These remain within the Spine/Unity managed route.

The direct branch targets are labeled by the bounded `native-calls.json` call map as the corresponding Spine/Unity methods; that inventory is provisional and direct-call-only. The report does not infer dynamic callbacks beyond the method bodies and serialized references above.

## Separate `BossSpineEventHandler` candidate

The managed `BossSpineEventHandler` class (TypeDefIndex `114`) also has tracked raw ASM. Its `Start()` body registers `AnimationState.add_Event`, `add_Start`, and `add_End`; `HandleEvent(TrackEntry, Event)` compares event names, toggles a charge-effect GameObject, and invokes its `UnityEvent` for matching strings.

However, the bounded serialized-instance inventory reports `BossSpineEventHandler` as `raw_file_present=false`, with zero instances, and there is no `BossSpineEventHandler.jsonl.gz` component export in the tracked typetree slice. This is explicitly an export-scope limitation—not proof that the class is unused. It therefore cannot be attached to the `Boss-39001` `SkeletonAnimation` record in this report.

## Boundary against node174 / native `116cb40`

The positive chain is `Boss_1_Animation` serialized PPtr → `SkeletonAnimation` / Spine skeleton data → managed Spine animation callbacks and Unity events. No field, callback target, script link, or exported object in this slice identifies node174, a native clock/output holder, or fixture `116cb40`. This is a bounded game-side non-join, not a global proof of absence and not a runtime result. Spine's serialized animation/event inventory and the code path are kept separate from the Boss19/20/21 Animator clips and from AI-1's native/FDE evidence.

Static-only: no runtime readback/playback, parity, live-DPS, emulator, Frida, geometry/render, or `libunity.so` FDE work was performed. PPtr identity remains file-scoped; the serialized local joins above do not assert that any animation executed.

## Provenance

The companion `datas/l3_a5a74747_game_side_spine_animation_route_boundary.json.gz` records the serialized component join, managed Spine call edges, separate uninstantiated-handler boundary, native non-join, and SHA-256 pins for the selected raw ASM, metadata, animation-audit files, and the full bounded typetree export slice.
