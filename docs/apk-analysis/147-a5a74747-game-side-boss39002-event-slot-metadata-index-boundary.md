# #27-GS phase 18 — metadata-index/slot bridge boundary

**Claim:** PR12 comment `6421791961` · **Evidence mode:** static only

**Disposition:** `EVENT_LITERAL_ADDRESSES_RECONFIRMED / CALLBACK_SLOT_NOT_COVERED_BY_AVAILABLE_SLOT_MAP`

## Existing metadata indexes

The checked `metadata-index.json.gz` contains three tables: 10,758 `ScriptMetadata` rows, 17,933 `ScriptMetadataMethod` rows, and 15,054 `ScriptString` rows. Each of the four path-918 Spine event names has one `ScriptString` row, with the same addresses reported in phase 15:

| Value | Index address |
|---|---:|
| `Attack3` | `0x2BDAAA0` |
| `Banplasma` | `0x2BDB0A8` |
| `Batdautu` | `0x2BDB150` |
| `Stop` | `0x2BE5CB8` |

Neither the integer address fields nor any other field in this index contains callback slot `0x2ADFB48` (decimal 44,956,488). The index records literal addresses and metadata/method addresses; it does not expose a reference from the callback's static pointer slot to one of those literal rows.

The separate `metadata-slots.json` is explicitly `PROVISIONAL`. It lists 12 requested slot addresses and 12 effective-address mappings; the callback slot is not among the requests, keys, values, or sample rows. Its `ScriptString` rows are only three selected values (`TUTORIAL`, `tutorial_begin`, `tutorial_complete`), not a full pointer-slot table. It therefore cannot resolve the callback slot or justify a global-absence claim.

## Conclusion

The available indexes reconfirm the event literal rows but add no slot-to-literal bridge. The phase-17 `Stop` candidate remains contextual evidence from the unrelated `Tut_Settings1` Animator controller—not a proven string value for the shared slot, and not a proven Boss-39002 Spine event key. Boss-39001 remains separate. No binary was read, no runtime behavior was observed, and no AI-1 native/FDE work was performed; live-DPS remains `MODEL_NOT_MEASURED`.

## Provenance

The companion `datas/l3_a5a74747_game_side_boss39002_event_slot_metadata_index_boundary.json.gz` records table/row counts, exact event-literal addresses, the bounded 12-slot map coverage, and SHA-256/size pins for the checked indexes and phase-14–17 sources.