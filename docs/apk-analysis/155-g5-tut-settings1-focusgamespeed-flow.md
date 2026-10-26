# G5 — `Tut_Settings1` slider callback to `focusGameSpeed`

**Claim:** PR12 comment `6423319796` · **Evidence mode:** static only  
**Disposition:** `TUT_SETTINGS1_FOCUSGAMESPEED_CALL_FLOW_BOUND / SLOT_LITERAL_AND_BOSS39002_IDENTITY_UNBOUND`

## Scope

This bounded trace follows `Tut_Settings1.Start` into its generated `<Start>b__11_0(float amount)` slider callback and the callback's `focusGameSpeed` branch. It uses the managed declarations, the method assembly export, serialized `Tut_Settings1` references, the Animator map, and the exported `FocusGameSpeed` controller graph. It does not reopen the broader string-slot census.

## Callback hookup and guarded call

The managed declaration places `sliderTimeScale: Slider` at `this+0x20`, `focusGameSpeed: Animator` at `this+0x60`, and the `stopFocus` latch at `this+0x68`. In `Start` (RVA `0x1328D54`), the code constructs an `Action<float>` with the component instance and generated callback method, then stores it at `sliderTimeScale+0x58` (`0x1328F9C`–`0x1328FA4`). The `Slider` declaration identifies its `Action<float> onChange` field at `+0x58`; this binds the generated method as that slider's callback in the static code path.

In `<Start>b__11_0` (RVA `0x13293F4`), the float argument is retained while the method checks the `focusGameSpeed` reference. The focused branch:

1. loads `this+0x60` and applies Unity's `Object.op_Implicit` existence check (`0x27849C8`);
2. obtains its GameObject (`Component.get_gameObject`, `0x277F188`) and checks `GameObject.get_activeSelf` (`0x2781848`);
3. skips the trigger call if the Animator/GameObject check fails or if `stopFocus` at `this+0x68` is already true;
4. otherwise sets `stopFocus = true`, loads the string argument indirectly through slot `0x2ADFB48`, and calls `Animator.SetTrigger(string name)` at `0x13294EC` (call target `0x27583B0`).

The method continues into separate amount/value, `TimeSlider.SaveSpeed`, and UI update paths. Those paths show static UI state handling only; this trace does not establish that Unity's game clock or any native clock is changed.

## Serialized Animator/controller context

The serialized `Tut_Settings1` component at path ID **6825**, `GP_Tutorials/TutSettings (1)`, points `focusGameSpeed` to Animator path ID **4648**. The animator map joins that record to GameObject **123**, prefab root `GP_Tutorials`, and controller path ID **1927**. The second exported `Tut_Settings1` instance (path ID **6861**) has a null `focusGameSpeed` reference.

The controller graph names path 1927 `FocusGameSpeed`; its parameter table contains ID **426031496**, which the controller's `m_TOS` maps to `Stop`. An AnyState transition uses that same parameter ID and targets state index 1, whose exported path is `Base Layer.stop`. This makes `Stop` a concrete **UI-controller contextual candidate** for the indirect string passed by this callback, but it is not a slot-to-parameter mapping.

## Hard limits

- The string value in slot `0x2ADFB48` remains unresolved. The controller parameter name does not prove that the callback's argument is `Stop` or that it matches a controller parameter.
- The Animator is the separate serialized `Tut_Settings1` UI/tutorial object. This contextual trace does **not** identify the value of the same slot in `Boss1_Director.SkeletonAnimation_AnimationState_Event`, does not bind a Boss-39002 Spine event, and does not transfer evidence to Boss-39001. The boss routes remain separate.
- No runtime callback delivery/invocation, Animator transition/playback, clock change, or resulting runtime state is observed. No native/FDE or runtime-probe work was performed; `Live-DPS` remains `MODEL_NOT_MEASURED`.

## Provenance

The companion receipt is `datas/l3_a5_g5_tut_settings1_focusgamespeed_flow.json`. It records the instruction anchors, serialized references, controller context, scope boundaries, and SHA-256 pins for the source exports used here.