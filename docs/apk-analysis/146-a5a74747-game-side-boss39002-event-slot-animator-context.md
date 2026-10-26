# #27-GS phase 17 — Animator context for the shared event-string slot

**Claim:** PR12 comment `6421626332` · **Evidence mode:** static only

**Disposition:** `ANIMATOR_SETTRIGGER_CALL_TARGET_RESOLVED / STOP_IS_A_CONTEXTUAL_CANDIDATE_NOT_A_SLOT_PROOF`

## Managed call target and serialized UI context

The previously unresolved call target `0x27583B0` is identified by the managed declaration as `Animator.SetTrigger(string name)` (TypeDefIndex 10666). In `Tut_Settings1.<Start>b__11_0` (RVA `0x13293F4`), the code loads the value through shared slot `0x2ADFB48` into the string argument and calls that method with the receiver loaded from `this+0x60`.

The serialized `Tut_Settings1` corpus contains two instances. Path 6825 (`GP_Tutorials/TutSettings (1)`) points `focusGameSpeed` to Animator path 4648; path 6861 has a null `focusGameSpeed`. The animator map joins path 4648 to controller path 1927 under prefab root `GP_Tutorials`. The checked controller export identifies `FocusGameSpeed` and includes one parameter entry whose `m_TOS` name is `Stop` (ID 426031496, type code 9); the same ID appears in the transition condition to state `stop`.

## Interpretation and hard limit

`Stop` is therefore a concrete **contextual candidate** for the string passed to `SetTrigger` by this separate UI/tutorial method. But the static exports do not map pointer slot `0x2ADFB48` to the controller parameter, and a `SetTrigger` call does not prove that its argument matches a declared controller parameter. The exact literal value remains unresolved.

The same slot is loaded by the separate Boss-39002 Spine callback, but the UI Animator reference is not a Boss-39002 object and does not establish a Spine listener value. Do not infer that the callback compares against Spine event `Stop`, or connect that marker to the Boss-39002 callback. Boss-39001 remains separate as well. No runtime invocation, parameter match, event delivery, playback, or effect is claimed.

## Provenance

The companion `datas/l3_a5a74747_game_side_boss39002_event_slot_animator_context.json.gz` pins the method, metadata, serialized component, animator/controller join, controller graph, and phase 14–16 context used for this bounded candidate check. No runtime or AI-1 native/FDE work was performed; live-DPS remains `MODEL_NOT_MEASURED`.