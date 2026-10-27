# G3 — Boss-39001 Spine callback and completion-route boundary

**Claim:** PR12 comment `6423862570` · **Evidence mode:** static only  
**Disposition:** `BOSS39001_SERIALIZED_SPINE_CHAIN_PROVEN / EVENT_CALLBACK_RET / COMPLETION_STATE_BRANCHES_BOUNDED / EVENT_SLOT_JOIN_UNRESOLVED`

## Result

The selected Boss-39001 export gives a bounded chain from its serialized `Boss_1_Animation` component to the shared Spine JSON, and the managed type declaration/callsite export contains a distinct `SkeletonAnimation_AnimationState_Event` body. That event callback is exactly one `RET` at RVA `0x1247DA8`: it reads neither callback argument, contains no comparison or conditional branch, and does not load an event-name string slot. Therefore there is no Boss-39001 event-name-slot join or true branch in this callback body to map to a Spine marker, `defeatEvent`, or `burstEvent`.

A separate route exists in the same managed type: `SkeletonAnimation_AnimationState_Complete` extracts the completed track's animation name and tail-branches to `BossWork`. `BossWork` compares that name with the serialized controller-state strings and has bounded true-branch actions (below). This is animation-completion/state-selection logic, not the Spine `Event` callback and not evidence that a Spine event marker was delivered.

**The event-name-slot join remains unresolved.** The checked serialized `m_Script` pointers have blank `target_class` values, and the bounded instance inventory has no `BossSpineEventHandler` instance/value set on Boss-39001. The shared Spine data path alone does not supply that missing handler/callback identity.

## Boss-39001 route and serialized values

| Link | Exported identity | Static evidence |
|---|---|---|
| Script/component record | `Boss_1_Animation`, component path `674445`, GameObject `Boss-39001/Enemy_Ingame/Body/Boss 1` | Serialized instance row; `m_Script` PPtr target `32715571200` has no resolved `target_class` |
| Skeleton component | `SkeletonAnimation`, path `602882` | `skeAnim` on path `674445` points to this component; its own `m_Script` target `29947330560` also has blank `target_class` |
| Skeleton data | `SkeletonDataAsset` path `580611` | `spine-prefabs.json` resolves Boss-39001 component `602882` to this data object |
| Spine JSON | TextAsset path `918` | The same `spine-prefabs.json` row resolves the data object's JSON reference to `918`; report 140 pins the asset-content identity and its timeline separately |

The managed dump identifies `Boss_1_Animation` as TypeDefIndex `141`; its declared fields align with the serialized record. This declaration does not resolve either serialized `m_Script` PPtr. The eight controller strings are: `stateAppear=Xuathien` (`+0x30`), `stateRunAway=Baydi` (`+0x38`), `stateDie=Dead` (`+0x40`), `stateAttack1=Attack1` (`+0x48`), `stateAttack2=Attack2` (`+0x50`), `stateAttack3=Attack3` (`+0x58`), `statePreAttack2=Chuyensangattack2` (`+0x60`), and `statePreAttack3=Chuyensangattack3` (`+0x68`). The serialized record also contains `defeatEvent` at `+0x70`, `burstEvent` at `+0x78`, and `hitCol` at `+0x80`; the two persistent events target path `601110` with method names `OnDefeated` and `OnBusrtItems`, respectively. These serialized UnityEvent targets are not Spine event-marker bindings.

## Callback registration and the empty event body

The exported `Start` body at RVA `0x12473EC` follows `skeAnim` (`this+0x28`) and contains two delegate construction/add sequences: the first spans `0x1247480–0x12474C0` (method-table load at `+0x190`, helper targets `0x220E3DC` and `0x220A648`), and the second spans `0x12474C4–0x1247508` (method-table load at `+0x180`, helper targets `0x220E2C8` and `0x220A510`). The exported class declaration identifies the corresponding callbacks as `SkeletonAnimation_AnimationState_Complete` and `SkeletonAnimation_AnimationState_Event`; this is source registration code only. It does not establish that `Start` ran, a listener was retained at runtime, or any callback was delivered.

The separately exported `SkeletonAnimation_AnimationState_Event` body at RVA `0x1247DA8` is:

```asm
0x1247da8: ret
```

There is no event-argument read, string comparison, slot load, or branch in this body. The result is limited to this exported method body; it is not a global absence claim about every possible callback path.

## Separate completion callback: bounded true-branch semantics

`SkeletonAnimation_AnimationState_Complete` at RVA `0x1247C38` null-checks the `TrackEntry` and its nested name pointer, loads the animation-name string, then tail-branches to `BossWork` at `0x1247C58`. In `BossWork`, the string comparisons are against the serialized fields above. The following are static register/field-flow results, not executed behavior:

| Compared completion name | True-branch path | Bounded action in the method body |
|---|---|---|
| `stateAppear` (`Xuathien`) | `0x1247C6C–0x1247CB0` | If `nextTurn` (`+0x88`) is non-null, calls its delegate; if the `skeAnim`/state path is non-null, passes `stateAttack1` (`+0x48`) to the known Spine `SetAnimation` target `0x220D324`, track index `0`, loop flag `1` |
| `statePreAttack2` (`Chuyensangattack2`) | `0x1247CB4–0x1247CF8` | Same optional `nextTurn` delegate path; passes `stateAttack2` (`+0x50`) to `0x220D324`, track `0`, loop flag `1` |
| `statePreAttack3` (`Chuyensangattack3`) | `0x1247CFC–0x1247D54` | Same optional `nextTurn` delegate path; passes `stateAttack3` (`+0x58`) to `0x220D324`, track `0`, loop flag `1` |
| `stateRunAway` (`Baydi`) or `stateDie` (`Dead`) | `0x1247D58–0x1247DA4` | If the `defeatEvent` field (`+0x70`) is non-null, passes it to helper target `0x278EF98`; this branch does not read `burstEvent` (`+0x78`) |

The attack-selection field-to-call mapping and the `0x220D324` target identity are also documented in report 141. This completion path is not an event-name comparison: its input is the completed animation name. The presence of serialized `defeatEvent`/`burstEvent` targets does not identify any Spine timeline marker, and this method body supplies no `burstEvent` branch.

## Event-slot, handler, and sibling-route boundaries

- Report 142's bounded script-identity census finds `BossSpineEventHandler` TypeDefIndex `114` in managed metadata but no serialized handler instance, resolved MonoScript link, or Boss-39001 configured values in the checked exports. Its fields cannot be assigned to this component from a type declaration alone.
- The Spine asset identity in this route is shared: Boss-39002's separate `SkeletonAnimation` component path `664302` also references skeleton data `580611` / JSON `918`. This common asset identity does **not** transfer Boss-39002 callback code, event slots, or selection evidence to Boss-39001. G3 uses only the Boss-39001 `Boss_1_Animation` body and its own serialized record.
- No value is attributed here to slot `0x2ADFB48`; no Spine marker is named as a callback key; no event is linked to either persistent UnityEvent target. Report 140's asset timeline remains an asset-only result.

**Bounded blocker:** a future static closure would need a resolved script/type mapping and a concrete handler instance or other explicit caller edge on the Boss-39001 object route, with that object's serialized handler fields and any relevant slot-backed literal resolved. Until those joins exist, the event-name key and marker/effect association remain `NOT_BOUND`; sibling Boss-39002 evidence is not a substitute.

## Boundary

No callback registration at runtime, event delivery, animation playback, effect execution, or runtime parity is claimed. No native/FDE, `libunity.so`, runtime-probe, emulator, or frozen-raw regeneration work was performed. No change is made to `MODEL_NOT_MEASURED`.

## Provenance

The companion receipt `datas/l3_a5_g3_boss39001_spine_callback_completion_boundary.json` records the exact component/data PPtr chain, callback and completion-body anchors, branch-to-field mapping, handler/slot gaps, separation from Boss-39002, and SHA-256 pins for each selected source.
