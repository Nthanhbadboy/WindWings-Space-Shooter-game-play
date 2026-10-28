# 125 — #25 Scoped save/flush and migration-entry audit — `arena/a5a74747-windwings-space-shooter-game-p`

**Status: `SCOPED_STATIC_SAVE_CALL_CENSUS_NOT_DURABILITY_PROOF`.** This is a bounded static slice of PR12 item #25, claimed in [PR12 comment 6415333947](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6415333947). It does not claim a complete global save schema, platform durability, or runtime round-trip.

## Scope and source identity

The audit combines the pinned opening-persistence receipt (41 method records) and player-loadout receipt (33 method records), **74 distinct methods total**, plus a literal direct-branch search over every `*.asm.txt` file currently present below `reverse-engineering/raw/` (**314 files / 7,823,314 bytes**). The receipt stores per-input SHA-256 pins and a per-file SHA-256 inventory for the ASM scan.

The recovery index pins the original XAPK to `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`, `libil2cpp.so` to `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`, and `global-metadata.dat` to `449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69`. Those identities are carried forward from the pinned recovery index; the XAPK/native library were **not** retrieved in this audit.

## Measured results

| Check | Result |
|---|---:|
| Selected persistence method records | 41 opening + 33 loadout = 74 distinct |
| `PlayerPrefs.Save()` call edges in those 74 records | 0 |
| Exact direct `B`/`BL` references to Unity `PlayerPrefs.Save` RVA `0x277cf6c` in the 314 current raw ASM files | 0 |
| Custom `PlayerPreferences.SaveToDisk()` callers in the selected source set | 3 |
| `File.WriteAllBytes` edge in that custom save method | 1 |
| Save-format/migration-name signals in the selected receipt method/signature/call-declaration text | 0 |

The selected `PlayerPreferences` methods show a separate custom dictionary store: `DeleteAll`, `OnApplicationFocus`, and `OnApplicationQuit` branch to `SaveToDisk`; that method reaches `File.WriteAllBytes` at `0x13f1b3c`. This is **not** a call to `UnityEngine.PlayerPrefs.Save()`. The typed `PlayerPreferences.SetInt/SetFloat/SetString` wrappers tail-branch to their respective PlayerPrefs setters; setter calls are not an explicit flush call.

The pinned `dump.cs.gz` declares `UnityEngine.PlayerPrefs.Save()` at RVA `0x277cf6c`, but the dump contains no implementation body for it. The two contract JSONs have `schema_version: 1`; these are analysis-pack format versions, not an APK save-format version. The migration search is limited to the selected 74 methods' names, signatures, and resolved call declarations; it is not a search for every possible indirect string/data reference in the whole program.

## Evidence boundary

The 0/0 call counts mean only that no named `PlayerPrefs.Save` edge appeared in the 74 selected receipt records and no exact direct `B`/`BL` destination appeared in the 314 ASM files scanned from this checkout. The ASM search does not cover indirect calls, unexported methods, missing method ranges, other builds, or generated/native engine code. It is not a repository-wide absence proof.

No platform flush semantics, `fsync`, crash atomicity, transactional behavior, migration correctness, cloud synchronization, full global-save completeness, or runtime save/readback was tested or inferred. A custom `WriteAllBytes` call does not prove a durable or atomic write; a PlayerPrefs setter does not prove when the engine persists it. No APK was modified and no runtime vehicle/session was used.

## Reproduction and validation

- Builder: `tools/build_l2_a5a74747_25_save_durability_audit.py` (Python standard library only).
- Regression: `tests/test_l2_a5a74747_25_save_durability_audit.py` — **8 PASS**.
- Rebuild: `python tools/build_l2_a5a74747_25_save_durability_audit.py`.
- Determinism: `python tools/build_l2_a5a74747_25_save_durability_audit.py --check`.
- Cross-task regression: all `test_l2_*.py` — **49 PASS**; #5 geometry regression — **9 PASS**.
- Repository claims: `python tools/verify-claims.py` — **209 PASS / 0 FAIL / 2 SKIP / 0 ERROR**; `python tools/refresh-readme-sizes.py --check` — **0 drift**; `git diff --check` — PASS.
- The artifact includes a SHA-256 for each of the 314 scanned ASM files and the aggregate sorted-inventory pin below. Each new deliverable file is under 5 MB; protected persistence data remains unchanged.

## SHA-256 pins

| File / source identity | SHA-256 |
|---|---|
| Original XAPK identity from `reverse-engineering/raw/player-loadout/index.json` | `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` |
| Original `libil2cpp.so` identity from the same pinned index | `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99` |
| `global-metadata.dat` identity from the same pinned index | `449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69` |
| `reverse-engineering/raw/persistence/opening-contracts.json.gz` | `ec35b5ab33e4c78a77ad391e5ac9c03d00328b74abc35d8d9ed66f83ca88544f` |
| `reverse-engineering/raw/player-loadout/contracts.json.gz` | `045dd36ff3f81eb4193953860856009dde6ed8c541e2749291eeb9dae22eb276` |
| `reverse-engineering/raw/player-loadout/index.json` | `f3a049c8c6f4380946395d5e47b6e86230f164fb376dd1ad901bdaa12d4843cd` |
| `reverse-engineering/raw/ui-audit/extra-native/PlayerPreferences.asm.txt` | `aa983280bda35434d4011944a212b85381a726778c7c6b612c786afa5e4d70ac` |
| `reverse-engineering/raw/ui-audit/extra-native/PlayerPreferences.json` | `ed8dc8c7f3ffb3fbc493d7660ea4ff8f374ca6625a1ce561cc203d5aa23939bd` |
| `reverse-engineering/il2cpp/dump.cs.gz` | `e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454` |
| Decompressed `dump.cs` | `8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c` |
| Sorted inventory of 314 ASM paths/sizes/SHA-256s | `c9e29739bc0ade975b85bd8eb26f04afc4cb961a1f0fe3026d6811a0e74a57d0` |
| `datas/opening_persistence.json` | `2af3d80567a1a593376091ae24412fe17c3c9616b625f1992e28a4bf71f588e6` |
| `datas/player_loadout_persistence.json` | `2edfab3377f2d8c9cd7f4fa6704f707ca048060c0add67aa496cc1c94c36feb4` |
| `datas/l2_a5a74747_25_save_durability_audit.json.gz` (19,533 bytes) | `6283991693cfe6aaade0d15c5613639841c393bd059da177145c1e40b890a742` |
| `tools/build_l2_a5a74747_25_save_durability_audit.py` | `9b9bdab37b72e4f936ee9b34356e7f5f6415fedf8b023d9969018cd0b3c57ec2` |
| `tests/test_l2_a5a74747_25_save_durability_audit.py` | `463ccbeb889cb5ca9f8239cb388f5122f3d565db55d896f9b1af034d47def052` |

Handoff follows after branch push and remote-tip confirmation; no ACK requested from this branch.
