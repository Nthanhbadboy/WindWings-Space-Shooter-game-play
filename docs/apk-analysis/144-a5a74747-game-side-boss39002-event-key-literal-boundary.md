# #27-GS phase 15 — Boss-39002 callback event-key literal boundary

**Claim:** PR12 comment `6421443090` · **Evidence mode:** static only

**Disposition:** `CALLBACK_LITERAL_INDEX_ENTRIES_FOUND / SLOT_TO_LITERAL_POINTER_UNRESOLVED`

## Scope

This bounded follow-up asks whether the managed string-literal index can resolve the event-name comparison in Boss-39002 `Boss1_Director.SkeletonAnimation_AnimationState_Event` (RVA `0x14FFAF8`). It checks the existing IL2CPP string-literal index and available declaration/method exports only. The Boss-39002 callback remains separate from Boss-39001.

## Literal-index results

`reverse-engineering/il2cpp/stringliteral.json` contains 15,054 `{value,address}` rows. The four event names in the shared Spine asset have literal-index entries:

| Value | Literal address |
|---|---:|
| `Attack3` | `0x2BDAAA0` |
| `Banplasma` | `0x2BDB0A8` |
| `Batdautu` | `0x2BDB150` |
| `Stop` | `0x2BE5CB8` |

The callback's disassembly loads through static pointer slot `0x2ADFB48`, then compares that indirect value with the incoming event-data name. The literal index has no row whose address equals `0x2ADFB48`, no address beginning `0x2ADF`, and no slot-to-literal reference field. The method summary likewise has no literal-valued constant or string-literal index. Thus, the checked index confirms the candidate event strings exist, but does not identify which literal (if any) the slot resolves to.

This address mismatch is not evidence that the callback compares against none of those names: a separate pointer/relocation mapping could connect the slot to a literal, but that bridge is absent from the checked exports. The exact event key therefore remains unresolved.

## Asset boundary and conclusion

The path-918 Spine asset has five `Stop` keyframes in `Attack3` and one `Banplasma` keyframe in `Attack4` (phase 11). Those asset-level markers cannot be assigned to this callback without the missing slot-to-literal join. No listener delivery, animation selection, playback, or gameplay effect is inferred. AnimationClip events remain a separate route.

**Result:** do not attribute the Boss-39002 callback to `Attack3`, `Banplasma`, `Batdautu`, or `Stop` from the current exports. Boss-39002 remains distinct from Boss-39001 even though both components reference the same SkeletonDataAsset / JSON paths. No runtime or AI-1 native/FDE work was performed; live-DPS remains `MODEL_NOT_MEASURED`.

## Provenance

The companion `datas/l3_a5a74747_game_side_boss39002_event_key_literal_boundary.json.gz` records row counts, exact addresses, the unresolved slot join, the separate prefab boundary, and SHA-256/size pins for the checked sources.