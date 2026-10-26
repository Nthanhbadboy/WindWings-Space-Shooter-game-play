# G4 — `gun3Static` call semantics in the Boss-39002 callback

**Claim:** PR12 comment `6423030332` · **Evidence mode:** static only  
**Disposition:** `BOSS39002_SET_ACTIVE_SEQUENCE_BOUND / SLOT_LITERAL_STOP / DELIVERY_MARKER_AND_DEFEAT_BURST_UNBOUND`

## Scope and prefab identity

The queued `gun3Static` callsite is the `Boss1_Director.SkeletonAnimation_AnimationState_Event` body at RVA `0x14FFAF8`. The prior source-pinned route join identifies this component as Boss-39002 path `582209` → `SkeletonAnimation` `664302`. Boss-39001 is a distinct `Boss_1_Animation` component at path `674445` → `SkeletonAnimation` `602882`; it does not acquire this callback evidence merely because the prefabs share Spine asset 580611 / JSON 918. This report is scoped to Boss-39002 only.

## Static call/dataflow result

The callback rejects a null event and null event data, then compares the event data name with the string loaded through static pointer slot `0x2ADFB48`. In the equality branch, the code reads `gun3Static` from `this+0xB8`. The declared managed field is `GameObject[]`; the serialized Boss-39002 component has three non-null references, path IDs `163907`, `163892`, and `163913`. Their GameObject names are not resolved in the pinned evidence.

The loop starts at the first array index and checks the array length. At each index, the body loads the current `gun3Static[index]`, checks it, and calls `SetActive(false)`. It then reloads both the field and the same index, checks again, and calls `SetActive(true)` on the newly loaded receiver:

| Order | RVA | Boolean | Receiver / decoded target meaning |
|---:|---:|---:|---|
| 1 | `0x2781804` | `false` | current `gun3Static[index]`; `GameObject.SetActive(false)` — request deactivation |
| 2 | `0x2781804` | `true` | reloaded `gun3Static[index]`; `GameObject.SetActive(true)` — request activation |

The target is identified by matching the call RVA to the `UnityEngine.GameObject.SetActive(bool value)` declaration in `dump.cs.gz`. The serialized array has three non-null PPtrs, but the second receiver is reloaded after the first call. Static evidence therefore establishes the same **index** and false-then-true call order, not guaranteed object identity across the two calls if runtime side effects mutate the field/array. It also does not establish that the callback was registered, delivered, or executed, nor what runtime side effects occurred.

## Static slot identity update — separate provenance

After the original G4 game-side export audit, AI-1's public HANDOFF123 independently resolved static slot `0x2ADFB48` to the metadata string literal `Stop` ([PR12 handoff](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6422951255); wording correction [comment](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6423891421)). The **literal identity** is therefore now recorded as `Stop`; the game-side G4 receipt remains source-pinned to its own managed/serialized exports, and this cross-lane note does not import or modify AI-1 raw/native artifacts.

This resolves the compared string value, not runtime delivery. The G4 body contains a name comparison against that value, but this report does not establish that a callback ran, which timeline occurrence (if any) was delivered, or that the `gun3Static` branch executed. The false→true call sequence above is unchanged. No defeat or burst event is assigned to the key or branch.

## What remains unbound

- No runtime callback delivery, branch execution, playback, or resulting active state is observed. The string key is statically identified as `Stop`; delivery of any particular Spine timeline occurrence remains unobserved.
- No source edge in this trace identifies the gate as a defeat or burst event. Those labels must not be inferred from the queue wording, method/class names, or the false/true pair.
- No Boss-39001 callback, selection, or serialized evidence is transferred from this Boss-39002 component.
- This report does not inspect the native/FDE lane or provide runtime readback. `Live-DPS` remains `MODEL_NOT_MEASURED`.

## Provenance

The companion receipt is `datas/l3_a5_g4_gun3static_semantics.json`. Its `source_sha256` entries pin only the selected game-side exports. The separate AI-1 public handoff/correction comments are recorded as external static-literal context, not folded into those source pins. Exact G4 instruction anchors and the unchanged array/call sequence are in the receipt and above.
