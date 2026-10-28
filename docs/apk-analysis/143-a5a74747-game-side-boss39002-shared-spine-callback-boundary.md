# #27-GS phase 14 — Boss-39002 shared-Spine callback boundary

**Claim:** PR12 comment `6421252055` · **Evidence mode:** static only

**Disposition:** `BOSS39002_SHARED_SPINE_CALLBACK_CODE_PRESENT / EVENT_KEY_AND_RUNTIME_BINDING_UNRESOLVED`

## Scope and serialized sibling context

This is a separate Boss-39002 check prompted by its sharing the Spine assets cited for Boss-39001. It does not transfer any object, callback, selector, or event evidence to Boss-39001.

| Object | Serialized path | Relevant local reference |
|---|---:|---|
| Boss-39002 `Boss1_Director` | 582209 | `skeleton` → component 664302; `parentDestroy` → 601111 |
| Boss-39002 `SkeletonAnimation` | 664302 | `skeletonDataAsset` → 580611; Spine JSON → 918 |
| Boss-39001 `Boss_1_Animation` | 674445 | separate component; `parentDestroy` → 601110 |
| Boss-39001 `SkeletonAnimation` | 602882 | same data asset 580611 and Spine JSON 918 |

The `Boss1_Director` row's `m_Script` PPtr target is 11492392960 with blank `target_class`; the sibling component's serialized shape does not resolve that target in this export. Managed declarations identify `Boss1_Director` as TypeDefIndex 1908, but that metadata is not itself a PPtr resolution.

## Managed-body evidence

The available `Boss1_Director` body has two distinct Spine callback methods:

- `Start`, RVA `0x14FF6E8`, constructs a delegate for `SkeletonAnimation_AnimationState_Event` and routes it through call targets `0x220E2C8` and `0x220A510`; it similarly handles the Complete callback. It then passes the serialized `stateAppear` value through call target `0x220D324`. This is evidence of code in the method body, not proof that Unity invoked `Start` or that the listener was registered at runtime.
- `SkeletonAnimation_AnimationState_Event`, RVA `0x14FFAF8`, rejects null event/data, compares the event data's name against a managed string loaded through static pointer slot `0x2ADFB48`, and on the equality branch iterates the `gun3Static` array (`this+0xB8`). For each non-null array entry the body calls `0x2781804` once with boolean argument 0 and once with argument 1. The call target's effect is not assigned a semantic name here.

The static slot's string value is not resolved by the checked exports. Consequently this callback body cannot be joined to `Attack3`, `Banplasma`, `Batdautu`, `Stop`, or any other particular Spine event name. The shared TextAsset's timeline markers remain asset-level data, not evidence that this callback received one.

## Separation and limit

The Boss-39002 serialized instance has the eight state labels also seen in the sibling context (`Xuathien`, `Baydi`, `Dead`, `Attack1`, `Attack2`, `Attack3`, `Chuyensangattack2`, `Chuyensangattack3`); no `Attack4` field is present. Its `parentDestroy` is 601111, not Boss-39001's 601110. This report therefore does not revise the Boss-39001 selector, listener, or receiver conclusions in reports 141–142.

No game-side edge from this bounded callback trace to fixture `116cb40` was established. No `libunity.so` FDE/native lane or runtime path was inspected; no event delivery, playback, or effect is claimed. Live-DPS remains `MODEL_NOT_MEASURED`.

## Provenance

The companion `datas/l3_a5a74747_game_side_boss39002_shared_spine_callback_boundary.json.gz` records the exact serialized chain, method RVAs/call targets, unresolved event-name slot, sibling separation, and SHA-256/size pins for the checked source files.