# G6 — bounded field-binding census for array blobs

**Claim:** PR12 comment `6423501627` · **Evidence mode:** static only  
**Disposition:** `FIVE_CAPTURED_BLOBS_CLASSIFIED / DYNAMIC_GETCOSTCRAFTPLAYER_PAYLOADS_NOT_BOUND`

## Scope and inventory

This census is limited to the two tracked, non-PvP `reverse-engineering/raw/**/array-blobs.json.gz` exports: `player-loadout` and `audio-rules`. The `player-loadout` export records five `InitializeArray` callsites (49 logical int32 values); the `audio-rules` export contains no method or field rows. This is not a census of every array or metadata field in the program, and the empty audio export is not a global no-array finding.

The declared byte count below is allocation length × 4. `logical SHA-256` hashes exactly those declared bytes; `raw SHA-256` hashes the captured full payload, including trailing alignment/padding. The metadata-backed `<PrivateImplementationDetails>` payloads are not Unity serialized `AssetObject`s, so an asset path ID is **not applicable**. Their reproducible identity is the owning method/call ordinal, callsite, generated field name, metadata data/field indices, declared length, and payload digest.

| Source method / call ordinal | Callsite / allocation | Length; declared bytes | Metadata-backed blob identity | Binding result |
|---|---|---:|---|---|
| `Player_Device_Saved_Datas.GetPlayerDevices`, ordinal 0 | `0x14E63BC` / `0x14E63A4` | int[4]; 16 B | `5AC6…65461B`; data index 13560, field index 16573 | Method-local array used on one branch that returns from `GetPlayerDevices`; no named application field is established |
| `Player_Saved_Datas.GetCostCraftPlayer`, ordinal 0 | `0x14E7C40` / `0x14E7C28` | int[7]; 28 B | `8E74…13862`; data index 19760, field index 16733 | Method-local table; its out-of-range fallback feeds the method's scalar return at `array[rank+1]`; no named application field is established |
| `Player_Saved_Datas.cctor`, ordinal 0 | `0x14E81B0` / `0x14E81A0` | int[7]; 28 B | `FF58…50383`; data index 32416, field index 17037 | **Direct field bind:** `MaxLevelPerRanks`, static offset `+0x0` |
| `Player_Saved_Datas.cctor`, ordinal 1 | `0x14E81D8` / `0x14E81C8` | int[7]; 28 B | `0FBE…75F6A`; data index 3280, field index 16343 | **Direct field bind:** `CardUpgrades`, static offset `+0x8` |
| `Player_Saved_Datas.cctor`, ordinal 2 | `0x14E8200` / `0x14E81F0` | int[24]; 96 B | `99F8…EF52C`; data index 20744, field index 16758 | **Direct field bind:** `StartRanks`, static offset `+0x10` |

The three constructor rows are bound to declared fields by the constructor's `InitializeArray` → store sequence and the managed declaration. That proves field identity, **not** the fields' broader design purpose or every consumer. The two getter rows are local arrays rather than stored class fields; their method context is preserved instead of inventing a field name.

## One source callsite missing from the captured payload set

The two tracked `player-loadout` class ASM exports contain **six** calls to `RuntimeHelpers.InitializeArray` (`0x205B07C`) in total: five in `Player_Saved_Datas` and one in `Player_Device_Saved_Datas`. The `array-blobs.json.gz`/method-constants exports contain five records. The additional site is `GetCostCraftPlayer` ordinal 1 at `0x14E7C78`: after checking `_playerIndex - 10001` against `0..23`, code selects a `RuntimeFieldHandle` from a table based at `0x2996E38 + 0xE38`, allocates another int[7], and initializes it. That selected array then participates in the same `rank+1` scalar-return path.

**Status: `NOT_BOUND`.** The tracked blob capture has no payload row for `0x14E7C78`, and the checked method summary only records the earlier call at `0x14E7C40`. This census does not assign private-implementation field identities, per-entry payload digests, or semantic labels to the table-selected payloads. Blocking step: recover the 24 selected field handles and join each handle to its metadata field/data index and exact payload bytes, then validate declared length and hash per source-call ordinal. Until that join exists, the 24-branch payload family remains unresolved; the ordinary generic fallback row is not a substitute for it.

## Boundaries

- The five captured payload rows and hashes are checked against the pinned export. The uncaptured site is identified from the tracked ASM, not from runtime observation.
- No purpose is assigned to `MaxLevelPerRanks`, `CardUpgrades`, or `StartRanks` merely from field names or values; only their constructor field stores are bound here.
- No AI-4 PvP artifact was read or modified. No APK/native binary recovery, libunity/FDE work, runtime, runtime-probe, emulator, or secret work was performed.
- Scope is the two tracked array-blob exports and the pinned class bodies; do not generalize the residual to all arrays or all metadata in the game.

## Provenance

The companion receipt is `datas/l3_a5_g6_array_blob_field_binding_census.json`. It pins both array-blob inventories, the player-loadout method exports, the managed declarations, and report 66; it also records the 5/6 callsite coverage, digest recipe, exact unbound callsite, and the explicit blockers.