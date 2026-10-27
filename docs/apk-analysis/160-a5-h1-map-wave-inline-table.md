# H1 — static `listMapDatas` map→wave table

**Queue item:** H1 in PR12 comment `6425374777` · **Claim:** `6425457933`  
**Outcome:** **A2 closed for the bounded static table extraction**  
**Evidence tier:** static managed-method listing + pinned `InitializeArray` payload inventory  
**Not claimed:** runtime readback/parity, scene/UI map numbering, or gameplay stage→table-index identity

## Result

The `Map_Get_Datas..cctor` source listing constructs and stores `listMapDatas` as a `List<int[]>`. The table contains **250 ordered entries** and **742 integer values**: **243** arrays initialized by `RuntimeHelpers.InitializeArray` payloads and **7** arrays populated by immediate element stores. Length distribution: **243 × 3**, **6 × 2**, **1 × 1**.

The `listMapDatas` field is static offset `0x28` in the pinned `dump.cs.gz` declaration. In the source listing, the table list is created at `0x1406bf8`, receives the ordered arrays beginning at `0x1406c08`, and is stored to static field offset `0x28` at `0x140e19c`. `GetListWaves(int mapIndex)` has a branch that reads that static field, selects a list entry, and returns the selected `int[]`. Therefore the values and internal zero-based insertion order of this static table are now extracted; the table index is **not** asserted to equal a displayed map number or a campaign/stage identifier.

The first three already-resolved values cross-check exactly:

| Internal `listMapDatas` index | Extracted wave-ID array | Match |
|---:|---|---|
| 0 | `[25, 9010]` | ✅ |
| 1 | `[164]` | ✅ |
| 2 | `[113, 5]` | ✅ |

All **250/250** extracted arrays also agree with the prior `datas/maps.json` values. The older `datas/map_waves_candidate.json` remains unchanged as historical evidence, but it is **not valid as the full table**: it differs from the source extraction at **242/250** indexes (first divergence at index 4: source `[95, 11, 7008]`, legacy candidate `[225, 227, 7016]`). The receipt records the mismatch sample and pins the legacy file; consumers should use the new receipt, not that old candidate.

## Bounded conclusion

**A2's missing value table is closed**: the static constructor's `listMapDatas` table can be recovered from the captured managed method, with exact initializer-callsite-to-payload joins and immediate stores. This does not bind each table index to a named scene/campaign/stage, settle other mode-specific table identities, or prove runtime selection/readback. Those remain separate from the table extraction; no runtime or parity claim is made.

## Reproduction and pins

Rebuild with `python tools/build_a5_h1_map_wave_inline.py`; focused tests: `python -m unittest tests.test_a5_h1_map_wave_inline` (**4 tests**). The builder checks source hashes, the class-field declaration/store offset, 250 allocation PCs, 243 matching `InitializeArray` callsites and payloads, seven literal arrays, all 250 prior `maps.json` rows, and the three known entries.

| Input | SHA-256 / identity |
|---|---|
| `reverse-engineering/raw/il2cpp-consts/Map_Get_Datas.asm.txt` (26,017 lines) | `a95539643a1d0a17e546c5fde41cf1a12a7230f934cc12a30807bcdf644edae6` |
| `reverse-engineering/raw/il2cpp-consts/Map_Get_Datas.json` (`.cctor`: 100,896 bytes, uncapped, clean end) | `1b588f39932d2ffee3de214c76fa927fa58e6d4fddf70a8426dba95de7c5b249` |
| `reverse-engineering/il2cpp/ia-resolved.json` | `2583a4c472400fe85f96b96f0a8d2839963eddae95760483424119501d989e37` |
| `reverse-engineering/il2cpp/dump.cs.gz` | compressed `e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454`; decompressed `8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c` |
| `datas/maps.json` | `93f8670dd3960d3f3792f56b5abaf7bf95f91dbd46c7c953c170b5a9165d44f9` |
| `datas/map_waves_candidate.json` (superseded full ordering) | `4c0fe9e87ad554c7d9ada0b13dde44189453f753b2082411c1c087b33ca1756b` |
| `reverse-engineering/raw/ui-audit/scene-map-flow.json.gz` (prior three-entry/flow context) | `7422d8d89fcf5c29122f583cffb5d204917db943fd835813570d4bb80036fdf4` |

Receipt: `datas/l3_a5_h1_map_wave_inline.json`, SHA-256 `48a463b675240caecfcdac6455f3ce9d1147da4629b9cd744ff1fd0fe06e94ed`. Builder SHA-256 `835ee41b4ad2e26287f33cdeb53013ec81147a4b39acf4a1c8259adfcda734a7`; test SHA-256 `32835589341342165c6bd1e9dee5a054b81cd682c77390b6f43471d4c6f24db4`.
