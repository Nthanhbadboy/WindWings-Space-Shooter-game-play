# Game-side serialized script identity and Boss19 payload audit — phase 6

**Scope:** PR12 `#27-GS` phase-6 claim `6420031081`, a bounded static follow-up to phase 5. This slice attempts to resolve the five serialized `m_Script` PPtrs whose `script-links` entries have empty `target_class`, and to recover the missing Boss19 attack-types record/key data from available serialized exports and asset registries. PPtrs remain file-scoped; no runtime or native work is included.

## Result

**Disposition: `BOSS19_ATTACKTYPES_REFERENCE_CHAIN_PROVEN / SCRIPT_CLASS_IDENTITY_AND_ATTACKDATA_PAYLOAD_UNRESOLVED`.** Static exports show both `Boss19_AttackPhases` and `Boss_Director` on the `Boss-39019` root pointing to local `attackTypes` path ID `689449`; the director also points to the attack-phase component at `689448`. But the selected typetree corpus contains no typed record at `689449` and no `Boss19_AttackTypes` export. The component field's managed declaration is only the base type `Boss_AttackTypes`; the available script-link data does not identify the target's concrete script class.

The audit finds no available MonoScript/script-GUID bridge that resolves the five selected `m_Script` target IDs. This is a bounded corpus result, not proof that the assets or scripts do not exist in the original game.

## Boss19 local reference chain

The `Boss19_AttackPhases` typetree record has component path ID `689448`, GameObject `Boss-39019` / path ID `230427`, and `m_Script = (m_FileID 16777216, m_PathID 12650020864)`. Its `attackTypes` field is a local PPtr `(m_FileID 0, m_PathID 689449)`. The corresponding `Boss_Director` record is path ID `689450` on the same exported prefab root; it points to `attackPhases = (0, 689448)` and `attackTypes = (0, 689449)`. This confirms a same-root serialized reference convergence on the `689449` target.

The script's managed type metadata declares `Boss_AttackPhases.attackTypes` as `Boss_AttackTypes`, and `dump.cs.gz` declares `Boss19_AttackTypes : Boss_AttackTypes` with `RegisterEvents()` override RVA `0x152F414`. These facts make `Boss19_AttackTypes` a compatible candidate, but they do **not** prove that the missing serialized object at `689449` uses that concrete class. No Boss19 attack-data arrays or event-key coverage can be recovered from the missing record; phase 4's Boss19 key comparison remains unavailable.

## Script identity and export coverage

The exact five selected `m_Script` edges are:

| Owner component | Owner path ID | `m_Script.m_FileID` | `m_Script.m_PathID` | `script-links.target_class` |
|---|---:|---:|---:|---|
| `Boss19_AttackPhases` | `689448` | `16777216` | `12650020864` | empty |
| `Boss20_AttackPhases` | `634645` | `16777216` | `21189623808` | empty |
| `Boss20_AttackTypes` | `634644` | `16777216` | `19931332608` | empty |
| `Boss21_AttackPhases` | `615301` | `16777216` | `27531411456` | empty |
| `Boss21_AttackTypes` | `615302` | `16777216` | `23471325184` | empty |

Across the **140** compressed JSONL files in the tracked `reverse-engineering/raw/typetrees/` export slice (including `script-links.jsonl.gz`), plus `transform-tree.tsv.gz` and `prefab-roots.csv`, there are zero `MonoScript` text hits. None of the five script target path IDs appears as a top-level exported `path_id`; each appears only as the corresponding owner's `m_Script` target in this JSONL slice. The transform tree has 228,433 lines and none of the five script IDs or `689449`; the prefab-roots CSV has no matching ID. The `script-links` index contains **127,852** records, of which **35,797** have a nonempty `target_class`; all five selected `m_Script` entries remain unresolved. The available `script-declarations.json` is explicitly metadata-declarations-only (60 classes) and contains no mapping from these serialized script IDs to TypeDefIndex values.

The checked asset-pack files do not supply that bridge: `manifest-full.csv` has 2,907 rows with columns `type,name,bytes,path,path_id,atlas,width,height`, no script/GUID fields, and no selected-ID or MonoScript/script-GUID matches. `catalog.json.gz` is marked `PROVISIONAL_EXISTING_DRAFT_ARCHIVE_AUDIT_NOT_COMPLETE_APK_COVERAGE`; its 2,652 archived-file entries contain no MonoScript/script-GUID path or selected-ID match. The partial archive catalog is not treated as a complete APK inventory.

No dedicated MonoScript or script-GUID registry was found among the tracked sources checked. Numeric `m_Script` path IDs are not promoted to class IDs or matched to `TypeDefIndex`; the class-name gaps stay explicit.

## Bounded interpretation and limits

- The Boss19 phase and director exports point to the same local `attackTypes` target `689449`, but no selected typetree export resolves its object type or serialized attack data.
- The presence of a `Boss19_AttackTypes` class and virtual `RegisterEvents` override in managed metadata does not independently join that class to path ID `689449` or prove method invocation.
- Missing records in the per-type export slice do not prove absence from the original APK, other serialized files, or runtime objects.
- The five `m_Script` IDs remain unresolved despite available class declarations; this does not weaken the separately proven serialized Animator/event joins in reports 132–133.
- No event/call edge to native fixture `116cb40`, native node clock/output, or pose application is established. No runtime readback/parity, live-DPS, emulator, Frida, geometry/render, or `libunity.so` FDE analysis was performed; AI-1's native lane is untouched.

## Provenance

The companion `datas/l3_a5a74747_game_side_serialized_script_identity_audit.json.gz` records the five script edges, Boss19 reference chain, corpus search counts, registry candidates checked, explicit missing-export limits, and SHA-256 pins for all 141 compressed typetree-slice files plus supporting metadata, catalog, and prior reports/artifacts.
