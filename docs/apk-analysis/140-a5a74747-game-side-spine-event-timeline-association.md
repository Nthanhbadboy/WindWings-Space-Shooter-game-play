# Boss-39001 Spine event-timeline association — phase 11

**Scope:** PR12 `#27-GS` phase-11 claim `6420741175`. Verify the serialized Spine JSON reached from Boss-39001 `SkeletonDataAsset` path `580611` / `skeletonJSON` path `918` by its recorded byte length and SHA-256; enumerate per-animation Spine event markers and compare them to the asset's four event definitions. Reconcile the markers only with the already-bounded game-side callbacks and serialized-handler evidence. This is static asset/callback analysis, not playback or event-delivery evidence.

## Result

**Disposition: `BOSS39001_SPINE_EVENT_TIMELINE_ASSET_JOIN_PROVEN / GAME_SIDE_EVENT_RECEIVER_BINDING_UNRESOLVED`.** The checked TextAsset export matches the `spine_identity.json` record for serialized TextAsset path `918` exactly: 60,897 bytes and SHA-256 `89debb56f5b926ccb8775137daf7e744f8e558c84bfdceb99d3f1d91a55ffa4a`. Parsing that exact JSON yields six event keyframes across the ten animations: five `Stop` markers in `Attack3`, and one `Banplasma` marker in `Attack4`. The other eight animations have no event keyframes in this JSON. Of the four global definitions (`Attack3`, `Banplasma`, `Batdautu`, `Stop`), only `Banplasma` and `Stop` occur in animation timelines; `Attack3` and `Batdautu` have zero timeline uses.

This closes the **asset-level** timeline gap from phase 10, not the callback/receiver gap. `Boss_1_Animation.AnimationState_Event` remains a single `RET`; the separate `BossSpineEventHandler` has configurable event-name comparisons, but the bounded export still has no serialized handler instance or configured values binding it to this Spine asset. A keyframe name and time do not prove that a listener was bound, invoked, or produced an effect.

## Exact asset identity and event markers

The existing local PPtr chain reaches `SkeletonDataAsset` path `580611`, whose `skeletonJSON` reference is `(file 0, path 918)`. `datas/spine_identity.json` records path `918` as a 60,897-byte TextAsset with the SHA-256 above; `reverse-engineering/textassets/skeleton__21.json` matches both values. `datas/spine.json` independently records the same skeleton-data/path-918 association, the four global Spine event names, and rounded animation durations; it does **not** contain per-animation event-keyframe/time associations. Those timeline associations below come from parsing the hash-verified TextAsset JSON, not from `spine.json` or `spine-prefabs.json`. This is a content-hash join to the recorded TextAsset identity; the numbered filename `skeleton__21.json` is the repository export name, not a Unity path ID.

| Animation | Spine event keyframes (time in asset seconds) | Inventory duration (seconds) |
|---|---|---:|
| `Attack3` | `Stop` at `0.6333`, `3.3`, `5.8667`, `8.2`, `10.6` | `12.667` |
| `Attack4` | `Banplasma` at `0.7` | `1.0` |
| Other eight animations | None serialized | — |

The four event definitions in the skeleton JSON have empty payload/default objects. The complete usage counts are `Stop: 5`, `Banplasma: 1`, `Attack3: 0`, and `Batdautu: 0`. Here `Attack3` is both an animation name and a global Spine event definition, but it is **not** a keyframe event in any of the ten animation timelines. The time values above are serialized Spine keyframe positions; the rounded durations are the separate `datas/spine.json` inventory values.

These are Spine event timelines. They are not Unity `AnimationClip` event records, and their existence does not establish the active animation, playback speed, looping, or event delivery.

## Callback/receiver and native boundary

Phase 10's registered `Boss_1_Animation` Spine callback body at RVA `0x1247DA8` is a single `RET`. The separate `BossSpineEventHandler.HandleEvent()` can compare incoming Spine names with its configured `attackEventName` and `preAttackEffectEventName` and then toggle/invoke configured targets; however, its bounded serialized-instance count is zero, its typetree export is absent, and no configured field values bind it to Boss-39001. Therefore neither the five `Stop` keyframes nor the `Banplasma` keyframe can be assigned a proven receiver or gameplay effect. This does not establish global non-use of the handler.

The asset and game-side evidence checked here establish no edge to node174/native fixture `116cb40`, native clock/output holder, or interpolation state. This phase did not inspect `libunity.so` or undertake any native/FDE work. No runtime callback, playback, readback, visual parity, or live-DPS claim is made; `MODEL_NOT_MEASURED` remains unchanged.

## Provenance

The companion `datas/l3_a5a74747_game_side_spine_event_timeline_association.json.gz` records the exact asset identity/hash check, all ten timeline event lists, per-name usage counts, the phase-10 callback/handler boundary, and SHA-256 pins for the selected Spine exports and managed evidence.