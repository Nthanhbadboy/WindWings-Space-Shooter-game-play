# Boss-39001 Spine asset/event-handler boundary — phase 10

**Scope:** PR12 `#27-GS` phase-10 claim `6420639663`. Validate Boss-39001 `Boss_1_Animation` state labels against the animation-name inventory reached through the local `SkeletonAnimation` → `SkeletonDataAsset` PPtrs; record the asset's Spine event names; compare the registered animation-event callback body with the separate `BossSpineEventHandler` managed fields and `HandleEvent` body; then check the serialized-instance boundary. This remains separate from Unity `AnimationClip` events and from the native interpolation lane.

## Result

**Disposition: `BOSS39001_SPINE_ASSET_STATE_NAMES_MATCH / SPINE_EVENT_HANDLER_INSTANCE_AND_EVENT_VALUE_BINDING_UNRESOLVED`.** The local serialized asset chain reaches `SkeletonDataAsset` path `580611` and its `skeletonJSON` PPtr path `918`. The bounded `spine-prefabs.json` record lists ten animation names; all eight strings serialized on `Boss_1_Animation` are present exactly, including `Xuathien`, `Baydi`, `Dead`, and both transition names. This confirms name availability in the checked asset export, not animation playback or a runtime state transition.

The same asset export lists four Spine event names: `Attack3`, `Banplasma`, `Batdautu`, and `Stop`. `Boss_1_Animation.Start()` statically registers its `SkeletonAnimation_AnimationState_Event` callback, but that method body is a single `RET`. A separate `BossSpineEventHandler` class has code that can compare event names and invoke/toggle configured effects, but the bounded serialized-instance inventory has zero instances and the `BossSpineEventHandler.jsonl.gz` typetree export is absent. Therefore none of the four asset event names can be joined to its serialized `attackEventName`/`preAttackEffectEventName`, `onAttack`, or `chargeEffect` fields for this Boss-39001 record.

## Serialized asset/name join

- `Boss_1_Animation` component `674445` references `SkeletonAnimation` path `602882`; that component is on GameObject path `163303` and references `SkeletonDataAsset` path `580611`.
- The `SkeletonDataAsset` record names `skeletonJSON` PPtr `(file 0, path 918)`. The `spine-prefabs.json` local join independently records the same Boss-39001 Spine component, skeleton-data path, and skeleton JSON path; that audit labels its joins provisional and not proof of playback.
- The Boss-39001 Spine asset lists 10 animations: `Attack1`, `Attack2`, `Attack3`, `Attack4`, `Baydi`, `Chuyensangattack2`, `Chuyensangattack3`, `Dead`, `UIShow`, and `Xuathien`. All eight serialized state strings in `Boss_1_Animation` are exact members. `Attack4` and `UIShow` are additional asset names; their presence alone does not prove the controller selects them.
- Its event-name inventory is `Attack3`, `Banplasma`, `Batdautu`, and `Stop`. The available record is an event-name inventory only; it does not provide event timeline positions or prove event delivery.

## Distinct managed callbacks

`Boss_1_Animation.Start()` registers `AnimationState.add_Event` to `SkeletonAnimation_AnimationState_Event`. The method at RVA `0x1247DA8` consists of a single `RET`, so this handler body contains no event-specific gameplay action. This remains distinct from the completion callback path into `BossWork` and the separate persistent UnityEvents documented in reports 137–138.

`BossSpineEventHandler` (TypeDefIndex `114`) has explicit declaration fields: `attackEventName` (`+0x20`), `preAttackEffectEventName` (`+0x28`), `skeletonAnimation` (`+0x30`), `onAttack` (`+0x38`), and `chargeEffect` (`+0x40`). Its managed `Start()` registers Spine event/start/end callbacks. `HandleEvent()` reads the Spine event name, compares it with the two configured name fields, toggles the configured GameObject for the matching branches, and invokes `onAttack` on the attack-name branch. These are static class/method facts; they do not identify values for an instance on Boss-39001.

The serialized-instance inventory reports `BossSpineEventHandler` as `raw_file_present=false`, count `0`, and no instances; there is no `BossSpineEventHandler.jsonl.gz` in the checked typetree slice. This is a limitation of the selected export—not proof that the class is globally unused. No instance or configured field values tie any of `Attack3`, `Banplasma`, `Batdautu`, or `Stop` to this handler or its UnityEvent.

## Boundary

This phase validates only serialized asset name availability and compares the two distinct managed event-callback bodies. It does not establish callback registration/execution on a live object, animation playback, delivery of any Spine event, or a handler instance. No selected asset, managed callback, serialized event, or output identifies node174/native fixture `116cb40`, native clock/output fields, or interpolation state. Static-only; no runtime readback, native/FDE, geometry, rendering, or Animator clip-event inference.

## Provenance

The companion `datas/l3_a5a74747_game_side_spine_asset_event_handler_boundary.json.gz` records the PPtr chain, animation/event inventories, exact managed callback boundary, missing handler-instance export, and SHA-256 pins for the selected reports/artifacts and bounded typetree/ASM sources.
