# BossSpineEventHandler script-identity boundary — phase 13

**Scope:** PR12 `#27-GS` phase-13 claim `6421122159`. Search the available serialized script-link and component indexes, same-slice typetree exports, and asset-pack catalog/manifest for a concrete mapping from `BossSpineEventHandler` TypeDefIndex `114` to a serialized script target or an instance bound to Boss-39001 `SkeletonAnimation` path `602882` / Spine JSON path `918`. Decode handler field values only if that identity/instance join exists. Static-only; no inference from the type declaration alone.

## Result

**Disposition: `BOSSSPINE_HANDLER_TYPE_METADATA_PROVEN / BOSS39001_SERIALIZED_SCRIPT_IDENTITY_AND_INSTANCE_UNRESOLVED`.** Managed metadata identifies `BossSpineEventHandler` (TypeDefIndex `114`) and its fields/methods, but the checked serialized inventories do not map that type to a concrete `MonoScript` PPtr or to a Boss-39001 component instance. The exact `Boss_1_Animation` instance and its `SkeletonAnimation` remain identifiable; their own `m_Script` target PPtrs also have blank `target_class` entries in the available script-link export. Neither target resolves to TypeDefIndex `114`.

This is a scoped export limitation, not proof that the handler is globally unused. No `attackEventName`, `preAttackEffectEventName`, `onAttack`, or `chargeEffect` values can be attributed to a Boss-39001 handler instance from these data.

## Serialized identity and corpus checks

- `script-links.jsonl.gz` contains 127,852 owner/field/PPtr rows. For `Boss_1_Animation` owner path `674445`, its `m_Script` target is path `32715571200`, but `target_class` is empty. For `SkeletonAnimation` owner path `602882`, `m_Script` targets path `29947330560`, also with empty `target_class`. The `32715571200` target occurs once in this export, on the `Boss_1_Animation` owner; it does not identify `BossSpineEventHandler`.
- The bounded legacy-instance inventory has one serialized `Boss_1_Animation` instance at path `674445`, but `BossSpineEventHandler` is `raw_file_present=false`, count `0`, and has no instances. `reverse-engineering/raw/typetrees/BossSpineEventHandler.jsonl.gz` is absent.
- Scanned all 140 top-level typetree JSONL exports: there are zero occurrences of the string `BossSpineEventHandler` and zero hits for `attackEventName` / `preAttackEffectEventName`. `script-links.jsonl.gz` has no owner or resolved target class named `BossSpineEventHandler`.
- `spine-prefabs.json` contains three exported Spine components, including the Boss-39001 `SkeletonAnimation` path `602882` → skeleton data `580611` / JSON `918`; it contains no `BossSpineEventHandler` record. The 2,081-row `prefab-roots.csv` contains only transform/GameObject/name/child hierarchy columns, not component script identities.
- The checked `asset-pack/catalog.json.gz` and `manifest-full.csv` have zero literal occurrences of `BossSpineEventHandler`, `MonoScript`, `32715571200`, and `29947330560`. They do not provide a `MonoScript`-to-TypeDefIndex mapping for this case.

The managed declaration and `BossSpineEventHandler` code still establish only that a class with configurable event-name fields and a `HandleEvent` method exists. Without a serialized type identity and instance, no configured value or callback is joined to this boss. This remains separate from Spine event keyframes and from Unity `AnimationClip` event receivers.

## Boundary

No static game-side edge in this checked script-identity slice reaches node174/native fixture `116cb40`, a native clock/output holder, or interpolation state. No `libunity.so` FDE/native analysis or runtime readback was performed. The result does not establish callback registration, event delivery, animation playback, or global handler absence; `MODEL_NOT_MEASURED` remains unchanged.

## Provenance

The companion `datas/l3_a5a74747_game_side_bossspine_handler_script_identity_boundary.json.gz` records the exact PPtr/class-resolution outcomes, per-export counts, bounded missing-instance boundary, and SHA-256 pins for the selected serialized, asset-index, and managed metadata sources.