# #27-GS phase 20 — allowed text-corpus closure

**Claim:** PR12 comment `6422077957` · **Evidence mode:** static only

**Disposition:** `GAME_SIDE_TEXT_CORPUS_XREFS_BOUNDED / LITERAL_BRIDGE_REMAINS_UNRESOLVED`

## Eligible corpus and result

A text-only census covered 2,350 supported textual exports under `reverse-engineering` (uncompressed text plus gzip-wrapped JSON/JSONL/CSV/ASM/text formats), totaling 42,461,285 on-disk bytes and 326,191,797 decoded bytes. The manifest pins every eligible scanned file. Compiled binaries, this report chain, `.github` workflows, and `runtime-probe` were excluded.

Within that eligible corpus the matcher found **0** exact/decimal representations of slot `0x2ADFB48` and **4** existing `adrp 0x2ADF000` + `ldr [same register, #0xB48]` pairs, all already localized to two methods: `Boss1_Director.SkeletonAnimation_AnimationState_Event` (two uses) and `Tut_Settings1.<Start>b__11_0` (two uses). No new direct slot-to-literal record was found. The `Stop` candidate remains contextual evidence from the separate UI Animator, not a decoded callback value.

## Explicit exclusion boundary

A preliminary token-only filter encountered a textual marker in `reverse-engineering/raw/ui-audit/native-relocations.json.gz`. This is an explicitly native-relocation export, outside the allowed game-side text corpus for this phase. Its structure, mapping, and value were **not parsed or interpreted**, and it is not used as evidence. No binary was read. Accordingly this report does not claim global absence of a mapping; resolving that separate artifact would cross the native/FDE boundary expressly excluded from this work.

## Completion status

The permitted game-side static text-export census is complete. It narrows the remaining result to an explicit evidence boundary: the checked managed/serialized exports do not resolve the callback slot, while the only additional token hit is in an excluded native-relocation artifact. No Boss-39001 transfer, Spine event delivery, playback, or gameplay effect is inferred. No runtime or AI-1 native/FDE work was performed; live-DPS remains `MODEL_NOT_MEASURED`.

## Provenance

The companion `datas/l3_a5a74747_game_side_boss39002_slot_text_corpus_closure.json.gz` records exact corpus counts, slot-pattern matches, excluded-artifact boundary, and SHA-256/size pins for all 2,350 eligible text exports.