# Report 110 — Player-device save→load schema, end-to-end — `arena/a5a74747-windwings-space-shooter-game-p`

## Result

Added the bounded artifact `datas/l2_save_schema_end_to_end.json.gz` for the player-device slot family. It connects the recovered setter to typed PlayerPrefs wrappers, the corresponding reader, and identified UI/health/attack consumers. This is **not** a complete global save schema and is not runtime validation.

**Artifact SHA-256:** `b744f99bda73b542a1513df6aed0ea7c45f017e40d0e605a43791b7a71c6d9a0`

## Traced path

1. **Write — `Player_Device_Saved_Datas.SetPlayerDevices(int playerIndex, int[] devices)` (`0x14e64a4`).** The recovered body forms the player/slot key for slots `0..3`, writes the corresponding integer with `PlayerPreferences.SetInt`, and accumulates whether any slot is not `-1`. A short non-null input can have earlier slot writes complete before a later bounds fault; values beyond slot 3 are not used. The post-loop path reads `FIRST_INSTALL_DEVICE` with default `0`; when a device is present and that flag is still zero, it invokes the event path and writes the flag as `1`.
2. **Storage wrapper.** `PlayerPreferences.SetInt` (`0x13f1a04`) tail-branches to `UnityEngine.PlayerPrefs.SetInt` (`0x277cc10`). Its matching `GetInt` wrapper (`0x13f1a1c`) tail-branches to `UnityEngine.PlayerPrefs.GetInt` (`0x277cca0`). No explicit `PlayerPrefs.Save` call appears on this scoped setter path, so flush timing/durability is not established.
3. **Read — `GetPlayerDevices(int playerIndex)` (`0x14e628c`).** The normal path allocates a fresh `int[4]`, reads each slot with default `-1`, and stores the values in the result array. The pinned provisional contract and recovered branch/array evidence also show a mode-4 + active-Game override returning a fresh four-element `[-1,-1,-1,-1]` array without reading the saved keys.
4. **Consumers.** `Board_Players.SetPlayerDeviceSlots` (`0x12d5bd4`) uses the returned array for its slot/model path. `Player_Health.OnChangeDataDevice` (`0x14c58ec`) and `Player_Attack.GetDeviceAddPowerPercent` (`0x1479e34`) call the same reader, skip `-1`, pass the saved integer to `GetDevice(int instanceId)` (`0x12546d0`), then inspect the returned `Device.id`. The health consumer handles the `1000..1999` ID range using `GetStatValue1`; the attack consumer branches over `2000..4999` ranges and uses `GetStatValue1` and/or `GetStatValue2` to update fields on the attack object. This establishes static consumer paths, not invocation timing or a final combat outcome.
5. **Record/stat interpretation.** `Device` declares `id` at `0x10`, `lv` at `0x14`, `rank` at `0x18`, and `instanceId` at `0x1c`. The saved slot integer is passed as the lookup’s `instanceId` argument; `Device.id` is a separate stat/category ID. `GetStatValue2` (`0x1250134`) reads `Device.id/rank/lv`: it selects `listStatValues[id/1000 + 4][rank]`; if that base is zero it returns zero, otherwise it adds `percentByLevels2[id/1000 - 1][lv + 1] * (lv + 1)`.

## Evidence boundaries and gaps

- `GetDevice` is declared in the pinned dump and its callsites are present, but its implementation body was not present in the recovered method-body exports consulted here. Lookup mapping, identity equality, caching/invalidation, and null/error behavior remain unresolved.
- The key format `PLAYER_DEVICE_{ship}_{slot}` is corroborated by the earlier pinned provisional contract, string literal, and recovered key-builder path; it was not read back from a live app.
- No schema version, migration, cloud/cross-device sync, atomicity, persistence round-trip, or engine/platform flush guarantee is established. The artifact covers one key family only; report 66 and `datas/player_loadout_persistence.json` remain unchanged prior evidence.
- No exhaustive global caller/callee absence claim is made. Evidence comes from the specific pinned source files below; no screenshot/render gate was used.

## Source identity and SHA-256 pins

Recovery index status is `PROVISIONAL_PINNED_NATIVE_RECOVERY_NOT_RUNTIME`.

| Pinned input | SHA-256 |
|---|---|
| XAPK | `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` |
| `global-metadata.dat` | `449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69` |
| `libil2cpp.so` | `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99` |
| Decompressed `dump.cs` | `8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c` |
| `Player_Device_Saved_Datas.asm.txt` (decompressed pin in recovery index) | `4cd845eca6efa22b279ccef7fe0ad91845f1efdf6c523ab095ec47cd52bc9113` |
| `Player_Device_Saved_Datas.json` (decompressed pin in recovery index) | `a410ecc45e6956f56b38947813f36fe9838696052e0ae2b74e946f7c134185cf` |

The artifact also carries byte-level SHA-256 pins for all 13 workspace source files it consulted: the APK-analysis identity note; recovery index and provisional contract; player-device assembly/JSON and related player-save assembly; `PlayerPreferences` assembly; `dump.cs.gz` and string literals; and `Device_Get_Data`, `Player_Attack`, `Player_Health`, and `Board_Players` native exports. See `source_pins` in the artifact for the exact path-to-hash list.

## Validation

- `python3 tools/verify/l2_save_schema_end_to_end.py` — rebuilt the deterministic gzip artifact after checking all pinned source hashes and instruction/signature anchors.
- `python3 -m unittest tests/test_l2_save_schema_end_to_end.py -v` — 6 tests passed.
- `python3 -m unittest discover -s tests` — 183 tests passed.

The artifact generator and tests are new, task-owned files under `tools/verify/` and `tests/`; no other digger's tool was changed.
