# 124 — #28 Map static-value crosscheck, fallback ① — `arena/a5a74747-windwings-space-shooter-game-p`

**Status: `STATIC_CROSSCHECK_NOT_RUNTIME`.** This report executes the PR12 #28 board-approved fallback ① after checking the approved loader route; it does **not** supply a live `arr=256&depth=2` receipt and does not close the runtime-readback requirement. Reopened-lane claim: [PR12 comment 6415107893](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6415107893). The prior #28 report 121 and its `BLOCKED BEFORE SESSION` artifact remain unchanged.

## Approved loader route check

The reopened board authorized an approved loader-apk vehicle, then fallback ① if it could not be retrieved/run. I checked the exact same-repository release records and inspected the current `ef6b75ef` and `eeb95d5a` peer branch trees before selecting the fallback:

- `windwings-apk-1.3.118` lists only `windwings.xapk` (142,125,649 bytes), not a loader APK.
- `windwings-assets-1.3.118` lists asset/preview archives, manifests, and reference packs, with no APK asset.
- The checked local checkout and current peer tree tips `ef6b75ef` (`706c704e6024b831097a2b53a1d5332e588e30b6`) and `eeb95d5a` (`ceebe881d8e7bdd4a1c388897ec7b824e631123f`) expose no tracked `.apk`/`.apks` loader package. Files whose names contain “loader” in those trees are scripts or game-code analysis, not a loader APK.

The two release records are draft releases in this repository; the inventory is intentionally scoped to those exact tags and inspected branch snapshots. This is **not** a claim that no loader exists elsewhere. AI3's reported EOF while downloading the XAPK is not treated as evidence that content is missing; I did not repeat that download. No XAPK/APK was downloaded, installed, modified, or launched, and no runtime session was started. With no approved loader binary in the inspected references, I proceeded only with fallback ① as claimed; fallbacks ②/③ were not used. The metadata snapshot is `reverse-engineering/raw/l2-a5a74747-28-static-crosscheck/loader-vehicle-release-assets.json`.

## Static Map-values crosscheck

The board's fallback ① was a static Map-values crosscheck from #21, explicitly not runtime evidence. I pinned the latest static Map-entry artifact from the peer #21 lane (report 108), `datas/l2_ef6b75ef108_map_entry_bindings.json.gz`, from peer commit `706c704e6024b831097a2b53a1d5332e588e30b6` and compared its `Map_Get_Datas.listMapDatas` constructor root to both local static candidates:

| Measured check | Result |
|---|---:|
| Peer constructor-root rows | 250 |
| Prior `datas/maps.json` rows | 250 |
| `datas/map_segments_full.json`, candidate segment 35 rows | 250 |
| Map-value rows compared | 250 |
| Value mismatches | 0 |
| Allocation-site mismatches | 0 |
| Initializer field / call-site mismatches | 0 |
| Peer `InitializeArray` bindings / inline-immediate leaves | 243 / 7 |
| Total integer scalars across the 250 arrays | 742 |
| Array-length distribution | 1 value: 1 row; 2 values: 6 rows; 3 values: 243 rows |

The receipt includes all 250 arrays, their ordered values, per-row canonical-value SHA-256, source category, allocation site, and matched initializer identity where applicable. Anchors: constructor index 0 `[25, 9010]`, index 1 `[164]`, index 249 `[43, 12, 9024]`. Indices mean zero-based constructor order only; UI chapter/stage numbering remains unverified. The artifact's static route note is `Map_Get_Datas.GetListWaves` at field offset `0x28`, with the route scope retained in the receipt.

**Evidence boundary:** this is a static constructor-binding crosscheck using #21's ARM64 execution with synthetic metadata/allocator/List/Dictionary hooks, compared with prior local static extractions. Peer report108 says the constructor/ELF/RELA path was newly audited, but the scalar payloads came from the already-decoded `field-defaults.json` / `ia-resolved.json`; this is **not** a second independent APK/metadata decoder. The crosscheck supports the measured list order, values, and native site/initializer associations in that shared lineage; it is not an original-container implementation, mode-selection execution, or live phone readback. In particular, it does not establish nested-value parity with a device response. Model ≠ readback ≠ render; no screenshot, screenshot gate, or redraw was used.

## Relation to the requested runtime receipt

The requested nested runtime values for `Map_Get_Datas.listMapDatas` with `arr=256&depth=2` remain **`NOT_OBSERVED`**. This fallback artifact labels itself `STATIC_CROSSCHECK_NOT_RUNTIME`, sets `session_started=false`, records `source_apk_modified=false`, and contains no runtime values. It supplies the board-approved static alternative only; report 121 remains the scoped pre-session blocker and was not overwritten.

## Reproduction and checks

- Builder: `tools/build_l2_a5a74747_28_static_map_crosscheck.py` (Python standard library only).
- Regression: `tests/test_l2_a5a74747_28_static_map_crosscheck.py` — **7 PASS**.
- Rebuild: `python tools/build_l2_a5a74747_28_static_map_crosscheck.py`.
- Determinism: `python tools/build_l2_a5a74747_28_static_map_crosscheck.py --check`.
- Focused tests: `python -m unittest discover -s tests -p 'test_l2_a5a74747_28_static_map_crosscheck.py' -v` — **7 PASS**. Regression set: `test_l2_*.py` — **41 PASS**; #5 geometry regression — **9 PASS**.
- Repository claim verification: `python tools/verify-claims.py` — **209 PASS / 0 FAIL / 2 SKIP / 0 ERROR**; the two pre-existing skips are B9 and F4. `python tools/refresh-readme-sizes.py --check` — **0 drift**; `git diff --check` — PASS.

The source receipt is pinned to the exact peer artifact and to the original XAPK/native-library identities documented in the copied peer report 108; neither the XAPK nor native library was retrieved in this fallback run. All new files are below 5 MB. Protected `datas/PROVENANCE.md`, `datas/boss_anim_events.csv`, and `datas/player_start_stats.json` are unchanged. This branch makes no merge, main push, or self-ACK.

## SHA-256 pins

| File / source identity | SHA-256 |
|---|---|
| Original XAPK identity as identified in peer report 108 (not retrieved in this run) | `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` |
| Original `libil2cpp.so` identity recorded by peer report 108 (not retrieved in this run) | `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99` |
| `reverse-engineering/raw/l2-a5a74747-28-static-crosscheck/peer-l2_ef6b75ef108_map_entry_bindings.json.gz` | `ccf8309e0503dd504d651abb4c6df658fb68a4836f91b2711d236797905f09cd` |
| `reverse-engineering/raw/l2-a5a74747-28-static-crosscheck/peer-report-108-ef6b75ef.md` | `a1100c0502f33717e03ed36c4396d3ed7410dcf9ab80e3c92f0447a4f7ff1424` |
| Peer report 108 artifact, decompressed JSON | `99b4d8cd40baff9e45d27b1717e839242a16ea30428d1a13c194699aa28039f3` |
| `datas/maps.json` | `93f8670dd3960d3f3792f56b5abaf7bf95f91dbd46c7c953c170b5a9165d44f9` |
| `datas/map_segments_full.json` | `1b6fe5a776419b1846e0ced64499f62e1408f9780edb46d84336410260298250` |
| `reverse-engineering/raw/l2-a5a74747-28-static-crosscheck/loader-vehicle-release-assets.json` | `84c9bf9a44a07cf320f5ed0210331debdd8afdd26cc40c5b4d64a6948dfd10b6` |
| `datas/l2_a5a74747_28_loader_fallback1.json.gz` (29,293 bytes) | `434fc2db2abf6c23d923a90d967d90289b2adab78e1fc6508b3768ff61c5511b` |
| `tools/build_l2_a5a74747_28_static_map_crosscheck.py` | `7c2abca1bba69dc7a78477d79db9c15143204ff773a7e7108dad5bedd335781e` |
| `tests/test_l2_a5a74747_28_static_map_crosscheck.py` | `3f728e43def1f5dd66f1c17c9635cbd532711445a5ff140e55e51b0623f5f198` |

Handoff will report the commit SHA after pushing this branch; no ACK requested from this branch.
