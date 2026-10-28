# 114 — Geometry #4: original-byte TMP tables and bounded static fallback

provenance: **arena/8141386a-windwings-space-shooter-game-p**. Primary CLAIM [6415801698](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6415801698), after #5 replication HANDOFF6415795280. #5 was externally ACKed, not self-ACKed, in6416110827. This report does **not** claim native TMP generation, shaping, runtime text, scene-unit placement, readback, pixels or rendering.

## Result and evidence level

`datas/l3_geometry_tmp_8141386a.json.gz` is **448,421 bytes**, SHA256 **`9cec092ded2750f5eb5934367ebbd3dc0cca0528f91f69f119cffa31ebe980e6`**. Measured from that artifact:

- **7** owning-file-resolved static FontAssets; **2,352 glyph rows**, **2,354 character rows**, **2,285 distinct Unicode values**. Character rows and glyph rows are deliberately not conflated.
- Every glyph references a present glyph/atlas slot; **all 2,352 glyph rectangles are within their bound, actual Texture2D dimensions**. Each atlas identity and object SHA is pinned. This is rectangle/UV metadata validation, not a texture pixel/SDF validation.
- **1,737** captured TextMeshPro components each have an unmodified literal string, source identity/SHA, serialized properties and a per-codepoint static fallback plan. **79** literals are empty. Localization, runtime mutation and interpretation of markup are not inferred.
- **797** bounded literal metric previews, of which **768** have nonempty quads; **1,608** quads total. **940** rows retain their source/lookup plans but have `geometry=null` plus measured reasons. All 1,737 have `scene_geometry=null` and `runtime_text=null`.
- One null component font (`resources.assets:699094`, literal `Tip`) is **not silently assigned** TMP_Settings' default. One unresolved tab-control lookup (`resources.assets:693185`, literal `ATK\t201`) is **not a claim of a missing visible glyph**. The remaining literal, visible source-chain lookup has **0** unresolved character rows under this static policy. This is not a runtime text-demand/coverage claim.

**Status: source-owned byte-backed tables + explicit static policy. CPU metric rectangles are NOT native TMP vertex buffers.**

## Original package and fresh-byte corroboration

Original, unmodified authority:

| input | SHA256 |
|---|---|
| `windwings.xapk`, 142125649B | `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` |
| `base.apk`, 117158131B | `6843e79347f5b0bb68e4a2f9e1b1a3152e31d0875d4821b9928ad5799a95e1e1` |
| original `data.unity3d` | `7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7` |

Own read-only recovery workflow [40322602149](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/actions/runs/40322602149) is **SUCCESS**, source `33c62b5449d59ee57d768f9529d1b9e9b5c6e4f9`; bot witness commit `2985e7660761ffffcc197d81536a0a76aeeff0a0` was fetched/fast-forwarded. Cache is optional; original pinned release is fallback, not a modified APK/loader. `tmp/source-ci-receipt.json.gz` preserves actual REST run/jobs separately from the final scientific/test CI (recorded only after it actually succeeds).

`reverse-engineering/raw/geometry-8141386a/tmp/` contains:

- `selected-inputs.json.gz`: 7 fonts + 1,737 texts + 7 texture objects = **1,751 distinct object identities**, captured records, raw shard locations and source-code/file pins.
- `byte-queries.json.gz`: exact owning file/pathID/object SHA and complete expected font table arrays.
- `byte-witness.json.gz`: **1,751 original whole-object hashes** plus original object-table entries and **14 complete font-table byte spans** (160,024B including count prefixes). Full hex/offset/SHA and independent re-decoded values are retained, not just expected hashes.

The matched glyph array has a uint32 count + **52 bytes per glyph**: index, five float metrics, four signed rect coordinates, float scale, signed atlas index, signed class definition. Character arrays have count + **16 bytes per row**: element type, Unicode, glyph index, float scale. Matching is whole-array, aligned and unique; absent/duplicate/unaligned tables fail closed. The search was **seeded with the captured schema/data**; it corroborates original bytes and layout, not independent schema discovery.

All offsets below are relative to that original font object, and sizes include the 4B count:

| font pathID | glyph rows | glyph offset/bytes | character rows | character offset/bytes |
|---|---:|---|---:|---|
| 105 | 234 | 232 / 12172 | 234 | 12404 / 3748 |
| 106 | 66 | 248 / 3436 | 66 | 3684 / 1060 |
| 107 | 329 | 228 / 17112 | 329 | 17340 / 5268 |
| 108 | 435 | 244 / 22624 | 435 | 22868 / 6964 |
| 109 | 1172 | 244 / 60948 | 1174 | 61192 / 18788 |
| 110 | 19 | 244 / 992 | 19 | 1236 / 308 |
| 111 | 97 | 224 / 5048 | 97 | 5272 / 1556 |

Font109 aliases Unicode10 and13 to glyph1; this explains its two extra character rows, not two additional visible glyph meshes. All seven are static population mode0 with null serialized source-font PPtrs. No dynamic source-font glyph is invented.

## Identity-bound atlases and source fallback

All fonts/textures are owned by `data.unity3d/sharedassets0.assets`; table identities, not name-only joins:

| FontAsset | name | Texture2D | actual atlas w×h | face pointSize | unitsPerEM |
|---|---|---:|---|---:|---:|
| 105 | AGENCYB SDF | 33 | 512×256 | 36 | 0 |
| 106 | Agency SDF-Cyrillic | 14 | 256×256 | 48 | 0 |
| 107 | Amiri-Bold SDF | 29 | 512×256 | 24 | 0 |
| 108 | NotoSansKR-Medium SDF | 13 | 512×512 | 24 | 0 |
| 109 | NotoSansSC-Medium SDF | 31 | 1024×1024 | 27 | 0 |
| 110 | Roboto-Medium SDF-Currency | 30 | 128×128 | 37 | 0 |
| 111 | SDF-Thai | 32 | 256×256 | 37 | 0 |

The serialized primary105 fallback list is **[110,106,108,109,111,107]**; the six leaf fallback lists are empty. Our static first-match depth-first lookup records each visited identity and chosen character/glyph ordinal; cycles terminate. **1,736** component font PPtrs resolve to105, one is null. TMP_Settings default-font fact is preserved separately and is **not** a proven assignment to that null component. No global/system/OS replacement font or tofu advance is manufactured. A character's availability in this bank does not establish shaping, visibility, font initialization or runtime fallback execution.

Each glyph retains original metrics, glyph rect, scale and atlas slot, bounds verdict and normalized rect UVs. Each character retains its original glyph-index relation and scale. Complete captured font feature tables are retained (the seven `m_GlyphPairAdjustmentRecords` arrays are empty); the preview still makes **no native kerning/feature/shaping parity inference** from that observation.

## Preview math, invariants and refusal policy

Preview coordinates are **pointSize-normalized design units — NOT em**, because source `m_UnitsPerEM=0`. For a resolved character/glyph in font f, the chosen, explicitly synthetic arithmetic is:

```
s = face.m_Scale * glyph.m_Scale * character.m_Scale / face.m_PointSize
x0 = penX + horizontalBearingX * s
x1 = x0 + width * s
y1 = penY + horizontalBearingY * s
y0 = y1 - height * s
advance = horizontalAdvance * s
uvRect = glyphRect / actual_bound_atlas_dimensions
```

Each nonzero-area glyph metric/rect emits four LL/LR/UL/UR vertices/UVs and six indices. Zero-area spaces may advance but produce no fabricated quad. Line steps use the **primary font's** serialized lineHeight/pointSize convention; CRLF is one model linebreak. These are declared model choices, not claims about the native primary/fallback scale, baseline, `m_fontSize`, actual line layout, SDF padding or vertex packing.

`level0:86`, literal `Version`, produces **28 vertices/28 UVs/42 indices**. Every emitted index is in range, arrays agree with 4/6 per quad, values are finite, and selected UV source glyph rectangles are bounds-checked. Quads retain texture identity instead of implying one texture across fallback fonts. No scene/world AABB, transform or actual RectTransform/container geometry is guessed.

Rows refused geometry, with independently counted overlapping reasons:

| reason | rows |
|---|---:|
| font style/case/small-caps behavior not executed | 562 |
| auto-sizing not executed | 384 |
| word-wrap needs actual container/native layout | 296 |
| nonzero spacing beyond bounded zero-spacing policy | 196 |
| rich-text tokens require parser/native evidence | 64 |
| null serialized component font | 1 |
| control outside CR/LF model domain (tab) | 1 |

Counts overlap; **940** is the union, not the sum. Literal fallback plans, including literal markup characters, are inventory/lookup plans only; markup is never claimed to draw literally or to represent final shaped glyph demand. Case flags are not implemented by Python uppercase substitutions. RTL/bidi, Arabic shaping, combining marks and unsupported controls fail closed. Visible unknown codepoints get no guessed replacement or advance.

**Missing X for further native closure:** pinned native TMP generator/parser/font initialization/fallback/line-layout consumer with the actual context, or an approved same-build original Unity mesh readback. Actual runtime text, RectTransform sizing, glyph padding/material scaling, kerning/shaping/style, clipping and draw order must be evidenced, not filled with a static guess. This is an explicit boundary of the delivered byte-proof static artifact, not a whole-program claim that no such consumer exists.

## Reproduction and tests

```
python3 -m tools.verify.geometry_8141386a_tmp_sources --check
python3 -m tools.verify.l3_geometry_8141386a_tmp --check
python3 -m unittest tests.test_geometry_8141386a tests.test_geometry_8141386a_tmp tests.test_geometry_8141386a_support -v
python3 -m unittest discover -s tests -v
python3 -m tools.verify.geometry_8141386a_history
python3 -m tools.verify.geometry_8141386a_item_receipt --item 4 --check
python3 tools/refresh-readme-sizes.py --check
python3 tools/verify-claims.py
python3 tools/verify-claims.py --unscoped-legacy # intentionally diagnostic exit1
```

`--allow-pending-witness` is diagnostic-only; the default generator and handoff require the original-byte witness. Twenty new #4 tests cover all seven actual re-decoded tables, all 2,352 bounds, all 1,737 literal plans, source fallback order/currency/Korean/Arabic lookup, null-font non-assignment, missing/control separation, pointSize-not-em arithmetic, space/no-quad advance, CRLF, markup/case/auto-size/wrap/spacing/shaping refusals, duplicate glyphs, dangling glyphs, invalid atlases/rects, truncated/wrong-count/duplicate/unaligned byte arrays, cycles and exact deterministic gzip bytes. Synthetic negative cases are not observed game content.

Final local checks: **1,430 full tests PASS /324.824s**; **59 combined focused tests PASS /5.760s** (30 #5 +20 #4 +9 support-boundary). Source selection, default witness-required deterministic artifact, frozen #5 historical Git bytes and README0drift checks PASS. Complete final local test stdout and both verifier outputs are preserved in `reverse-engineering/raw/geometry-8141386a/verification-4*.gz`; the receipt records exact test counts/times, code pins, the frozen original baseline and every per-claim/per-group result. Final scientific CI is reported in the PR12 HANDOFF **only after** actual exact-head success; recovery GREEN above is not substituted for it. No screenshot gate or `[skip ci]`.

## Support boundary, common files and lineage

Same approved pattern as #5: **original inherited baseline160/27/24**, current unscoped diagnostic **163/25/23 (exit1)** (recorded verbatim, not relabeled GREEN), and **scoped historical-support compatibility209/0/2** with exact spec `0e2af55f4b2cf1ee6b0b2b66bf151aa28573013d`, 99-path snapshot, original SHA/Git blob pins and all211 claim rows/ordinals/per-group FAIL/SKIP results. This is NOT current-data, geometry, engine, readback or render acceptance. No new unscoped failure IDs/count regression is allowed. The old #5 report/receipt remain byte-for-byte at scientific `c86db3ee52b9dcf9108600e64717637a5ca59dd4`; legitimate later live needles are checked separately rather than rewriting history.

This report's commit synchronizes APKD1/AI1/RD1 from the **own worktree**, and refreshes measured README rows. Common changes are confined to those live needles in START_HERE/verifier/import receipt plus the own scoped workflow's #4/current/history checks. The three protected data files remain exact fixed SHA; no peer tools/artifacts or runtime-probe inputs are overwritten. No whole-peer-tree import, mass regeneration, APK modification, >5MB file/commit or name-only font/texture inference.

Mandatory initial base600a4a340 preserves ef `f5a447c15a117ca4571e2768f0274d1ad4f20b39` and the protected spec3. Shared lineage is explicit: inherited raw102 captures/owning-file Graph and ef UnityFS111/SerializedFile110 framing; font73 capture/schema informed the byte layout. Fresh original-byte table matching and own policy/tests provide additional corroboration, **not independent clean-room Unity decoding or native execution**. Latest coordination fetched/read with pagination:197 comments/sticky71, ef tip7a2a64fde and speca3c4d64a6. a5's later primary#6/127 is externally ACKed; no takeover is implied by this #4 report.
