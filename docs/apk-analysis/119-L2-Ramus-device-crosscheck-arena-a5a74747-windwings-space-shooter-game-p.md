# Report 119 — Ramus Map/device crosscheck — arena/a5a74747-windwings-space-shooter-game-p

**PR12 item #19** · claim comment `6413080203` · scope comment `6411617634`

**Status: PARTIAL — device-table grouping resolved; Map nested-value comparison still needs a refreshed runtime receipt.**

## Result summary

| Check | What the artifacts establish | What they do not establish |
|---|---|---|
| `Map_Get_Datas.listMapDatas` | Static APK table has 250 decoded entries; archived phone response reports count 250. It returned 128 type-name placeholders, not nested integers. | No comparison of nested Map contents. The archived receipt was not made with `arr=256&depth=2`; count equality is not content parity. |
| `Device_Get_Data` 12 vs 10 | The static `.cctor` has 12 `InitializeArray` captures, but classifies them as **10** `listStatValues` entries plus two separate static fields, `percentByLevels1` and `percentByLevels2`. The archived phone reports `listStatValues_count=10`. Both percent vectors match the two separate static arrays after float32 rounding. | No runtime values for the ten nested `listStatValues` rows. The phone app is modded 1.0.69; static source is official 1.3.118. No same-build value parity is claimed. |

The artifact includes the full static `datas/maps.json` table and the ten stat arrays decoded from the official source APK, but marks them as static evidence—not as phone readback. The current bridge and collector support `arr=256&depth=2`; that option is **not present in the archived phone response**. No screenshot was used as a gate or as a substitute for readback.

## Provenance kept separate

- **Static source:** package `com.Wind.wings.Space.Shooter`, version **1.3.118**, versionCode **312**; base APK SHA-256 `6843e79347f5b0bb68e4a2f9e1b1a3152e31d0875d4821b9928ad5799a95e1e1`; source XAPK SHA-256 `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`.
- **Archived runtime source:** package `com.Gcenter.WindWings.SpaceShooter.Premium`, reported **mod 1.0.69 repackaged**, on one HUAWEI Mate 20 X (`EVR-AL00`, Android 10 / API 29), Unity `2022.3.62f3`. It is not the APKPure 1.3.118 build.
- Repository search included the current branch and fetched refs `origin/arena/ef6b75ef-windwings-space-shooter-game-p` (`d7e718cf…`), `origin/arena/20330d0e-windwings-space-shooter-game-p` (`bab67115…`), `origin/a2033` (`aa07737c…`), and `origin/aef6b` (`9f90c1ac…`). The checked paths contain the same Mate 20 X receipt, not an independent second-device readback. This is a statement about those checked refs/paths, not a repository-wide claim that no other evidence exists.

## Device 12↔10: discrepancy resolved at field grouping

`datas/device_table.json` contains **12** five-float `InitializeArray` captures. Counting all captures as device rows was the category error:

1. In `Device_Get_Data..cctor`, the first ten arrays are added to the `listStatValues` list. The list reference is stored at static offset `0x0`.
2. The final two arrays are separately stored at `percentByLevels1` offset `0x8` and `percentByLevels2` offset `0x10`, as confirmed by `dump.cs` and the cctor stores.
3. The runtime JSON reports `listStatValues_count=10` and contains ten `Il2CppStructArray<float>` **type-name placeholders**. It separately reads `percentByLevels1=[0.5,0.6,0.4,0.8,1]` and `percentByLevels2=[0.1,0.1,0.3,0.4,0.5]`.
4. Static captures 10 and 11 are bitwise equal to those runtime percentage arrays after converting the runtime decimal values to IEEE-754 float32.

Therefore the static source has **10 entries in the list plus two additional arrays**, not a 12-entry device list. The static list length and archived runtime list length match at 10 **across different builds only**. This does not establish that there are ten user-facing devices, nor does it compare the values of the ten list rows.

## Map `arr=256&depth=2`: no nested-content parity yet

- The archived runtime JSON reports `_count=250`, but its outer list has 128 returned elements and all 128 are the `Il2CppStructArray<int>` type name. It contains no nested integer values to compare.
- The checked-in bridge parses `arr` and `depth`, and `runtime-probe/collect.sh` requests `&arr=256&depth=2`. The old phone receipt predates that path; its JSON cannot be upgraded retroactively.
- `datas/maps.json` contains 250 static decoded arrays from the 1.3.118 source. `docs/apk-analysis/31-map-tables.md` records the source/decoder caveats, including that static values are not runtime corroboration. The artifact preserves those values as static data and sets `content_equal=null` rather than guessing.
- The latest inspected Ramus APK preflight receipt, run `40181812673`, says the source XAPK had no `RamusBridge.dll`/loader and only `arm64-v8a` (no x86_64); it skipped before starting a Ramus session. It is not a gameplay or data readback. No session was started for this #19 attempt because that path could not produce the requested `/statics` evidence.

## Reproduction and deliverables

- Artifact: `datas/l2_ramus_device_crosscheck_19.json.gz` — **5,826 bytes**, SHA-256 `d9f85f085008a86cf600fe47134e2bce435cd52580a7ea19dad650a623dc8046`.
- Builder: `tools/build_l2_ramus_device_crosscheck_19.py` — SHA-256 `565eab64626b1e641788b577c2a1ef03f6c7204c3b2cecf2f42c81ea51852c01`.
- Tests: `tests/test_l2_ramus_device_crosscheck_19.py` — SHA-256 `2c3b58f8eb0c9694da304b22f7789b003ecb53d12c8af62ffec5a53a6b9c7c1a`; **7 tests PASS**.
- Rebuild: `python3 tools/build_l2_ramus_device_crosscheck_19.py`.
- Test: `python3 -m unittest tests.test_l2_ramus_device_crosscheck_19 -v`.

### SHA-256 pins for source evidence

| Source | SHA-256 |
|---|---|
| `datas/maps.json` | `93f8670dd3960d3f3792f56b5abaf7bf95f91dbd46c7c953c170b5a9165d44f9` |
| `datas/device_table.json` | `ab8084254128ffadc140d50f3d96d90b4582ffea29f06a36581eb6ca53d5b15a` |
| `docs/apk-analysis/31-map-tables.md` | `94179b17a1186e84969586ff6373decebcd6512cb75381795a4562767de4669d` |
| `docs/apk-analysis/01-apk-inventory.md` | `aa45ee808830453cb0b16ff4a763703c61f223665828f4ebe8fc736f33f5b33c` |
| `docs/apk-analysis/ramus/2026-10-23-phone/statics_Map_Get_Datas.json` | `945ee05718587cf485f6d77793947f4f2e1bcbff5095576df20a6b64f54fdae8` |
| `docs/apk-analysis/ramus/2026-10-23-phone/statics_Device_Get_Data.json` | `5ff79fb71ac7d9c5ac9a5ff7802487251bda72fb149d7660724542a809883c88` |
| `docs/apk-analysis/ramus/2026-10-23-phone/boss_state.json` | `a04ba3b0c5f20af4f2607a98996afcfc4be110d9786bc64e77477472300bed40` |
| `docs/apk-analysis/ramus/2026-10-23-phone/health_game.json` | `b92319f8a0d0dcc3af8ee7cfaf62909e808ad6424779b06759b749e23c4fbecb` |
| `docs/apk-analysis/ramus/2026-10-23-phone/CROSSCHECK-static-vs-runtime.md` | `1083a154ee8a5a92c6e63aeb43f6ea5756990309e9095569a15a239423504bd0` |
| `docs/apk-analysis/ramus/2026-10-23-phone/SUMMARY_vi.md` | `da2b74be5c89c80abbb29844a1de63ed114dd4313203b09dda5e1167f1b3051e` |
| `reverse-engineering/raw/il2cpp-consts/Device_Get_Data.asm.txt` | `a72bee63f439588733b1d7968f400d74ac94b55a3081494f7376238a0b9e2f63` |
| `reverse-engineering/raw/il2cpp-consts/Device_Get_Data.json` | `8b65838ea58cedb1ced1a5d4001be00928e641020aabaa1a26f8863919266876` |
| `reverse-engineering/il2cpp/dump.cs.gz` | `e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454` |
| `runtime-probe/RamusBridge.cs` | `d1a20f7a243e1a3baa381f3c6c188556f3c2c325a72e51b8cb869eb2e62ac9e9` |
| `runtime-probe/collect.sh` | `c6199c05432f1ad56d3495292aa1b53dbee9dbc33830c0ff3fc993e1eb8a69df` |

The artifact also embeds the input SHA pins, its builder SHA, the bounded raw-ref audit, and static/runtime provenance. The remote audit pins are recorded inside the artifact; in particular, the `ef6b75ef` raw provenance JSON is SHA-256 `c14f39e09d4b03e33891c5d386e74651d7cf335a6e0cd84271d41df3bdbfda2e` at commit `d7e718cfb5466fd7bd03e2d8357400d744b108cb`.

## Remaining evidence needed

A bridge-enabled, provenance-bound runtime capture is still needed to read `Map_Get_Datas.listMapDatas` with `arr=256&depth=2` and materialize all ten `listStatValues` float rows. The capture must retain package/version and device identity; screenshots are not required. Until then, Map nested-content parity and device-row value parity remain open.
