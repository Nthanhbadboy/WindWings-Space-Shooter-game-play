# Boss-39001 Spine `Attack4` selection boundary — phase 12

**Scope:** PR12 `#27-GS` phase-12 claim `6420923442`. Follow the phase-11 `Attack4` / `Banplasma` Spine keyframe against Boss-39001's serialized state/configuration and available `Boss_1_Animation` managed callsites. Check the distinct `Boss1_Director` and AnimationClip-name surfaces without merging them into the Boss-39001 Spine route. This is static source/serialization analysis only.

## Result

**Disposition: `BOSS39001_ATTACK4_NOT_IN_SERIALIZED_STATE_FIELDS / SELECTION_AND_EVENT_RECEIVER_UNRESOLVED`.** The hash-verified Spine asset contains animation `Attack4` and a `Banplasma` keyframe at `0.7` seconds, but `Boss-39001`'s serialized `Boss_1_Animation` instance has eight state strings and none is `Attack4`; its `SkeletonAnimation.initial_animation` is empty. The explicit Spine mix record is `Attack1` → `Baydi`, not `Attack4`.

The managed `Boss_1_Animation` code's direct Spine `SetAnimation` callsites pass the metadata-named serialized state fields (`Xuathien`, `Baydi`, `Dead`, `Attack1`–`Attack3`, and the two transition names). None of those call arguments is a statically named `Attack4` value. The exact asset marker is therefore not connected to a proven selection path in the selected Boss-39001 instance/code slice. This is a bounded negative result: it does not rule out dynamic/reflection paths, other callers outside the checked slice, or runtime selection.

## Boss-39001 serialized fields and direct callsites

The local serialized route is `Boss_1_Animation` component `674445` → `SkeletonAnimation` `602882` → `SkeletonDataAsset` `580611` → Spine JSON `918`. Metadata-backed field declarations and the serialized component values are:

| Field | Offset | Serialized value |
|---|---:|---|
| `stateAppear` | `+0x30` | `Xuathien` |
| `stateRunAway` | `+0x38` | `Baydi` |
| `stateDie` | `+0x40` | `Dead` |
| `stateAttack1` | `+0x48` | `Attack1` |
| `stateAttack2` | `+0x50` | `Attack2` |
| `stateAttack3` | `+0x58` | `Attack3` |
| `statePreAttack2` | `+0x60` | `Chuyensangattack2` |
| `statePreAttack3` | `+0x68` | `Chuyensangattack3` |

`Attack4` is absent from those eight serialized controller strings. The managed assembly's transfers to the Spine `SetAnimation` target `0x220D324` use these same fields:

| Method | Callsite | Serialized string field(s) supplied on bounded paths |
|---|---:|---|
| `Start` (`0x12473EC`) | `0x1247530` | `+0x30` (`stateAppear`) |
| `ClearGuns` (`0x1247A18`) | `0x1247AE4` | `+0x60` or `+0x68` (`statePreAttack2` / `statePreAttack3`) |
| `ClearGuns` | `0x1247B3C` | `+0x40` (`stateDie`) |
| `ClearGuns` | `0x1247BF0` | `+0x38` (`stateRunAway`) |
| `BossWork` (`0x1247C58`) | `0x1247D54` | `+0x48`, `+0x50`, or `+0x58` (`stateAttack1` / `stateAttack2` / `stateAttack3`) |

The rows describe static register/field flow into the managed call target, not actual call execution. The separate serialized `SkeletonAnimation` record has `initial_animation: ""` and an explicit mix only from `Attack1` to `Baydi`; neither is evidence that an animation played. The phase-11 marker remains asset data only: it does not establish selection, listener binding, or delivery.

## Similar names are separate routes

`Boss1_Director` is a different managed type with its own eight state fields; the selected serialized `Boss1_Director` record cited in phase 8 is on **Boss-39002** (path `582209`) and targets `Enemy_Destroy` path `601111`, not Boss-39001's component/receiver. Its method or object must not be used as a Boss-39001 caller without a separate identity join.

The declaration for `Boss1_AnimationEvents` (TypeDefIndex `143`) includes a method named `OnCallAttack4Event`, but the bounded legacy instance inventory reports zero instances of that class. This class/method name is not a binding to Spine `Banplasma`. Separately, in the 795-row Unity `AnimationClip` event-receiver export, there are zero rows for `Boss-39001`; its one `OnCallAttack4Event` row is on `Boss-39014` with a same-GameObject receiver candidate of `Boss12_AnimationEvents` (component `581752`). The six exact `Attack4` clip rows belong to `Boss-37001`, `Boss-39011`, `Boss-37014`, and `Boss-37019`. Those Animator/AnimationClip records are not the Spine `Attack4` animation or its `Banplasma` keyframe.

## Boundary

No selected serialized value or managed callsite statically binds the `Banplasma` event to `BossSpineEventHandler`; its configured values/instance remain unresolved as documented in phase 10. No game-side edge to node174/native fixture `116cb40`, native clock/output holder, or interpolation state was identified. No `libunity.so` FDE/native work, runtime readback, callback execution, playback, visual parity, or live-DPS claim is made. `MODEL_NOT_MEASURED` remains unchanged.

## Provenance

The companion `datas/l3_a5a74747_game_side_spine_attack4_selection_boundary.json.gz` records the serialized state-field map, direct callsite/field arguments, distinct Boss-39002 and AnimationClip contexts, and SHA-256 pins for the bounded asset, managed, and event exports.