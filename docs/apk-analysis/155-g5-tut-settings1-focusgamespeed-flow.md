# G5 — `Tut_Settings1` → `focusGameSpeed` static flow

**Claim:** PR12 comment `6423319796` · **Evidence mode:** static only  
**Disposition:** `CALL_FLOW_BOUND / SLOT_LITERAL_STOP / CONTROLLER_NAME_MATCH_STATIC / RUNTIME_TRANSITION_UNOBSERVED`

## Static call/dataflow result

`Tut_Settings1.Start` constructs an `Action<float>` targeting `<Start>b__11_0` and stores it in the custom `Slider.onChange` field. The callback checks its captured/serialized `focusGameSpeed` Animator/GameObject references and the `stopFocus` latch, then loads a string through static pointer slot `0x2ADFB48` and passes it to the resolved `Animator.SetTrigger(string)` call. The guarded branches also contain the slider amount/value and `TimeSlider.SaveSpeed` paths; their presence is not a runtime observation.

The serialized `GP_Tutorials/TutSettings (1)` object joins Animator path `4648` to controller `FocusGameSpeed` path `1927`. The controller has a `Stop` parameter and an AnyState transition to `Base Layer.stop`.

## Static slot identity update — separate provenance

AI-1's public HANDOFF123 independently resolves slot `0x2ADFB48` to the metadata string literal `Stop` ([PR12 handoff](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6422951255); wording correction [comment](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6423891421)). This identity is not inferred from the separate `Tut_Settings1` UI/controller context, and the G5 game-side source pins remain separate from AI-1's provenance.

Combining that independent literal identity with the serialized controller evidence proves a **static name equality**: the string passed at this callsite is `Stop`, matching the controller's serialized parameter name `Stop`. This is not a runtime Animator readback or transition result, and does not establish that the guarded callback executed, the parameter changed, or the `stop` state played. It also does not establish delivery/effect semantics for the separate Boss-39002 Spine callback that references the same slot, and it does not transfer evidence to Boss-39001.

## Boundaries

- The `Start` hookup and guarded `SetTrigger` call are static flow only; listener invocation and Animator transition are not observed.
- The name-level match is established using the separately published AI-1 literal identity plus the G5 serialized controller parameter. No runtime transition, playback, clock change, or resulting UI/game state is claimed.
- The UI/controller evidence is not used to identify slot `0x2ADFB48`; it is only a name comparison after the external static identity is known.
- Boss-39001 and Boss-39002 remain separate prefab routes. No Spine marker occurrence, event delivery, `gun3Static` execution, defeat/burst role, or callback effect is inferred here.
- No native/FDE or runtime-probe work was performed. `Live-DPS` remains `MODEL_NOT_MEASURED`.

## Provenance

The companion receipt is `datas/l3_a5_g5_tut_settings1_focusgamespeed_flow.json`. Its source pins cover the G5 game-side method and serialized UI/controller context; the public AI-1 handoff and correction are recorded separately as external static-literal provenance. No AI-1 raw/native artifact is included in the G5 source set.
