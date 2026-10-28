# #27-GS phase 16 — callback literal-slot cross-reference boundary

**Claim:** PR12 comment `6421527879` · **Evidence mode:** static only

**Disposition:** `MANAGED_SLOT_XREF_BOUNDED_TO_TWO_METHODS / LITERAL_CONTENT_UNRESOLVED`

## Corpus and matching rule

Searched all 273 available files under `reverse-engineering/raw/il2cpp-consts` that match `*.asm.txt` or `*.json` (139 disassembly text files and 134 method-summary JSONs; 7,682,988 bytes). A hit is either the exact absolute address `0x2ADFB48`, or an `adrp reg, #0x2ADF000` followed within five lines by `ldr reg, [reg, #0xB48]` using the same register.

Results: **0** exact absolute-address hits; **4** base-plus-offset pairs across **2 files and 2 methods**; **0** method-summary JSON hits. All four pairs are:

| Method | Use sites | Observation |
|---|---|---|
| `Boss1_Director.SkeletonAnimation_AnimationState_Event` (RVA `0x14FFAF8`) | `0x14FFB14`→`0x14FFB18`; `0x14FFB34`→`0x14FFB38` | Lazy string initialization load, then event-name comparison load |
| `Tut_Settings1.<Start>b__11_0` (RVA `0x13293F4`) | `0x1329450`→`0x1329454`; `0x13294DC`→`0x13294E0` | The second use supplies the same indirect slot value as an argument to call target `0x27583B0`; the receiver is loaded from `this+0x60` |

The managed declaration identifies `Tut_Settings1.this+0x60` as `focusGameSpeed: Animator`. This separate use establishes that the pointer slot is shared by code outside the Boss-39002 callback, but neither it nor target `0x27583B0` supplies the literal's text. The method summaries contain no string value or literal index for the slot.

## Result and boundary

The wider code cross-reference does **not** resolve the slot to `Attack3`, `Banplasma`, `Batdautu`, `Stop`, or another literal. The string-literal index has addresses for those four event names, but no slot-to-literal/relocation record. Sharing the slot with a second method does not reveal its content. Therefore the Boss-39002 callback cannot be joined to a specific path-918 keyframe from these exports.

This is a bounded result over the 273 checked method exports, not proof that no mapping exists elsewhere. Boss-39002 remains distinct from Boss-39001; no listener delivery, playback, or gameplay effect is inferred. No runtime or AI-1 native/FDE work was performed; live-DPS remains `MODEL_NOT_MEASURED`.

## Provenance

The companion `datas/l3_a5a74747_game_side_boss39002_event_slot_xref_boundary.json.gz` records all 273 scanned-file hashes, hit locations, the second-method context, and the unresolved literal bridge.