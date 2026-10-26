# Boss-39001 Spine state-to-UnityEvent trigger boundary — phase 9

**Scope:** PR12 `#27-GS` phase-9 claim `6420476580`. Follow the phase-7 Spine completion callback and phase-8 persistent receiver join through `Boss_1_Animation.BossWork` and `ClearGuns(turn)`. Map the state comparisons and UnityEvent invocation sites against the Boss-39001 serialized fields, then check the pinned top-level ASM corpus for direct incoming calls to the relevant methods. Spine `AnimationState` events, persistent `UnityEvent`s, and Animator clip events remain separate. Static-only; no native/FDE or runtime evidence.

## Result

**Disposition: `SPINE_COMPLETION_TO_DEFEAT_EVENT_STATIC_ROUTE_PROVEN / BURST_EVENT_CALLER_AND_RUNTIME_EXECUTION_UNRESOLVED`.** The managed completion callback tail-branches to `BossWork(entryName)`. In that method, comparisons against the serialized `stateRunAway` (`Baydi`) or `stateDie` (`Dead`) slots converge on a `UnityEvent.Invoke` call. Reconstructing the serialized field slots from the managed access anchor and the serialized field order maps that event slot to `defeatEvent`; its persistent target is the phase-8-resolved `Enemy_Destroy` path `601110`, method `OnDefeated`.

`ClearGuns(turn)` contains two guarded `UnityEvent.Invoke` paths at the metadata-confirmed `burstEvent` slot `+0x78`; its persistent target is also `Enemy_Destroy` path `601110`, method `OnBusrtItems`. A scan of the pinned 139-file top-level ASM corpus found no direct `BL`/tail-`B` caller to `ClearGuns` or the `BossDefeat` wrapper. The route is therefore statically visible, but a caller/activation for the burst-event branch is not established. None of these method bodies proves that Unity invoked a callback, an animation completed, or a death/burst action occurred.

## State and field-slot mapping

The tracked `script-declarations.json` metadata declaration for `Boss_1_Animation` (TypeDefIndex `141`) explicitly gives field offsets: `stateAppear` through `statePreAttack3` at `0x30`–`0x68`, `defeatEvent` at `0x70`, `burstEvent` at `0x78`, `hitCol` at `0x80`, and `nextTurn` at `0x88`. The serialized Boss-39001 component `674445` supplies the corresponding values and persistent calls. Independently, `Start()` loads slot `+0x30` and passes it to `AnimationState.SetAnimation`; its serialized value is `stateAppear = "Xuathien"`. The table below is therefore supported by explicit metadata offsets and method-body access, not merely by field order:

| Reconstructed slot | Serialized field | Exported value |
|---:|---|---|
| `+0x30` | `stateAppear` | `Xuathien` |
| `+0x38` | `stateRunAway` | `Baydi` |
| `+0x40` | `stateDie` | `Dead` |
| `+0x48` | `stateAttack1` | `Attack1` |
| `+0x50` | `stateAttack2` | `Attack2` |
| `+0x58` | `stateAttack3` | `Attack3` |
| `+0x60` | `statePreAttack2` | `Chuyensangattack2` |
| `+0x68` | `statePreAttack3` | `Chuyensangattack3` |
| `+0x70` | `defeatEvent` | one persistent call: `OnDefeated` → target `601110` |
| `+0x78` | `burstEvent` | one persistent call: `OnBusrtItems` → target `601110` |
| `+0x80` | `hitCol` | PPtr `487921` |

The slot assignment is static metadata evidence: the declaration records exact field offsets, and serialized values plus ARM64 loads/invokes agree with those offsets. This proves the managed method-to-field mapping in the checked build; it does not prove that any callback/event path executed.

## Callback and invocation paths

1. `SkeletonAnimation_AnimationState_Complete(TrackEntry)` at RVA `0x1247C38` obtains the animation name from the entry and tail-branches at `0x1247C50` to `BossWork(string)` at `0x1247C58`.
2. `BossWork` compares the name against slots `+0x30`, `+0x60`, `+0x68`, `+0x38`, and `+0x40`. The first three recognized branches route through the `nextTurn` delegate slot and call Spine `SetAnimation` using `+0x48`, `+0x50`, or `+0x58`. The `+0x38` or `+0x40` match reaches the call at `0x1247D94`, tail-branching to `UnityEvent.Invoke` target `0x278EF98` on slot `+0x70`—the reconstructed `defeatEvent` slot. Its serialized persistent call names `OnDefeated` on receiver `601110`.
3. `Boss_1_Animation.BossDefeat()` at RVA `0x1247DAC` also invokes slot `+0x70`. The bounded direct-call scan did not find an incoming `BL`/tail-`B` to this wrapper; this wrapper is not needed to establish the `BossWork` method-body route.
4. `ClearGuns(turn)` at RVA `0x1247A18` has two guarded paths to the same mapped `UnityEvent.Invoke` target, using slot `+0x78`—the reconstructed `burstEvent` slot: `BL` at `0x1247B00` when `turn` is nonzero and not one, and tail `B` at `0x1247C1C` when `turn==0` and the instance slot `+0x20` is zero. The serialized call names `OnBusrtItems` on receiver `601110`. `turn==1` takes a different animation-setting branch. These branch conditions are code facts, not observed game state.

The `native-calls.json` map labels `0x278EF98` as `UnityEngine.Events.UnityEvent.Invoke`; that map is provisional/direct-call-only. The serialized event target and method name are independently visible in the typetree record. The evidence establishes possible static call paths, not invocation.

## Caller scope and boundary

A byte-level direct `BL`/tail-`B` scan of the 139 top-level `.asm.txt` files found zero direct callers to `ClearGuns` RVA `0x1247A18` and zero to `BossDefeat` RVA `0x1247DAC`. `BossWork` is reached within the class by the explicit completion-callback tail branch. Zero direct references do not exclude indirect/virtual dispatch, reflection, Unity lifecycle/event wiring, or callers outside the pinned corpus.

Phase 8 resolved both persistent targets to Boss-39001 `Enemy_Destroy` component path `601110` and showed the same-root `Enemy_Controller.destroyScript` PPtr. Phase 9 adds the static state-to-event call route only. No selected call, field, event receiver, or output holder identifies node174/native fixture `116cb40`; the native interpolation join remains unresolved. No runtime callback execution, animation playback, death/burst/pooling effect, parity, or live-DPS is claimed. The Animator clip-event route and AI-1 native/FDE lane remain untouched.

## Provenance

The companion `datas/l3_a5a74747_game_side_spine_state_to_unityevent_trigger_boundary.json.gz` records the reconstructed slots and explicit confidence boundary, branch/call anchors, serialized event receiver, 139-file direct-caller scan, and SHA-256 pins for the bounded typetree/source files, selected reports/artifacts, and ASM corpus.
