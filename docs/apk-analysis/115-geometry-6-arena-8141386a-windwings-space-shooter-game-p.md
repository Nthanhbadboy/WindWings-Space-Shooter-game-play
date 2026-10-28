# 115 — Geometry #6 REPLICATION: original atlas bytes and static Sprite bounds

provenance: **arena/8141386a-windwings-space-shooter-game-p**.

Continues CLAIM [6416555265](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6416555265) after restart/OOM, preserving the same branch and the externally ACKed #5/#4 receipts. **a5 retains primary #6**: scientific `af518716b7f3f4a5d69a6a87ca75e2e8ee2692f6`, HANDOFF6416037439, external ACK6416110827. This is additional corroboration, not a takeover or a reopening of their static result.

## Delivered result — not live-remapped, not runtime-deformed

`datas/l3_geometry_atlas_8141386a.json.gz`: **1,195,537 bytes**, SHA256 **`361354d6b7ac8587c8ecb7886e25718900a562098884484696f3b008583e1cef`**.

Measured from that artifact, not estimates:

| Static check | Result |
|---|---:|
| Sprite / SpriteAtlas / Texture2D metadata identities | 2,185 / 66 / 654 |
| Sprite → exact owning atlas PPtr + complete render-data-key | 1,550 |
| Packed PPtrs / ordered name matches / atlas map rows | 1,550 / 1,550 / 1,550 |
| Unmatched packed PPtrs / unused atlas map rows / cross-atlas duplicate keys | 0 / 0 / 0 |
| Direct serialized `m_RD` route | 635 |
| Bound texture PPtr resolutions, including direct route | 2,185 |
| Independently decoded static vertex AABBs / vertices / triangle indices | 2,185 / 27,072 / 73,125 |
| Empty `m_Bones` / empty `m_RD.m_Bindpose`, scoped to these Sprites | 2,185 / 2,185 |
| Stored zero submesh localAABB / all-zero source UV0, per Sprite | 2,185 / 2,185 |

Every Sprite record preserves its exact source identity/hash/location, complete render key, original witness ordinal, atlas/map/packed-list indices or explicit direct route, texture identity/dimensions/hash, unchanged static render data, source positions/UV0/triangles, computed local AABB and original serialized submeshes. `live_remap` and `runtime_deformed_bounds` are **null for every row**. No scene/world/skin/pixel bounds are manufactured. Serialized zero AABBs are retained, not replaced by our measured vertex AABBs.

## Original authority and byte proof

| Original, unmodified input | SHA256 |
|---|---|
| `windwings.xapk` | `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` |
| `com.Wind.wings.Space.Shooter.apk` | `6843e79347f5b0bb68e4a2f9e1b1a3152e31d0875d4821b9928ad5799a95e1e1` |
| `assets/bin/Data/data.unity3d` | `7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7` |

Original-source recovery [40331600575](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/actions/runs/40331600575) is **SUCCESS**, actual source `b1b88beb78eb4ac507f02cb7bcfce08ae125df6f`, job121602146731. Bot witness `11552963cf6df1187b43560cb618a0d90d8eb274` was fetched and fast-forwarded; no reset/rebase. The recovery job used the pinned original release/cache vehicle, not a modified package. Actual REST run/jobs are preserved in `atlas/source-ci-receipt.json.gz`, distinct from final scientific CI.

Direct download in this sandbox failed at the release-assets host with EOF. Workflow log download also failed at the results-receiver host. **Neither is represented as local original retrieval or a retrieved CI log; no CI peak-RSS or test count is invented.** The branch-pushed witness and REST success are available and pinned.

`reverse-engineering/raw/geometry-8141386a/atlas/byte-witness.json.gz` is **1,670,372 bytes**, SHA256 **`07db322674ae53b889c2a841e1c24a38657717d0806deb7d6b4a61f585b04382`**. It contains:

- **2,905 / 2,905 fresh whole-object hash matches**: 2,185 Sprite + 66 SpriteAtlas + 654 Texture2D. Texture2D is deliberately **hash-only**, not a new image decode.
- **2,251 complete Sprite/SpriteAtlas objects, 1,720,744 bytes, byte-equal** to our inverse serialization. Equality covers the entire object, not only a matching prefix or a searched scalar.
- Original object-table entries, logical byte offsets, file headers/metadata prefix SHA, actual external file tables and SHA-pinned compressed/decoded block receipts.
- Full original hex/offset/size/SHA for packed PPtr arrays (**18,864B**, including count prefixes), packed names (**20,020B**) and complete render-data-map arrays (**167,664B**). Each map entry additionally has its own exact offset/size/SHA.
- Full original vertex payloads (**550,832B**) and index payloads (**146,250B**); count prefixes, channel descriptors, source key/PPtr/prefix fields and original serialized AABB spans are separate typed spans.
- **4,370 typed original zero array counts**: two per Sprite (`m_Bones` and `m_RD.m_Bindpose`), at their exact object-relative offsets. Zero is not located by an ambiguous grep for four null bytes.

Original file ownership is corroborated, not guessed from a bare pathID:

| owning SerializedFile | selected original objects |
|---|---:|
| `data.unity3d/globalgamemanagers.assets` | 2 |
| `data.unity3d/resources.assets` | 2,828 |
| `data.unity3d/sharedassets0.assets` | 31 |
| `data.unity3d/sharedassets2.assets` | 44 |

### What the inverse serializer does and does not prove

Layout/order is **seeded by the inherited UnityPy1.25.4 full typetrees**, with mesh75/MeshHelper channel conventions and ef UnityFS111/SerializedFile110 framing acknowledged. It is **not clean-room schema discovery, native serializer execution, TypeTree readback or a second independent APK parser**.

The Sprite serializer reproduces the name/alignment, rect/offset/border/PPU/pivot, polygon flag, full GUID+local-ID render key, tags and atlas PPtr; direct render-data PPtrs, submeshes/index/channel/vertex payloads, bindpose count, texture/packing fields, physics shapes and final bone count. The SpriteAtlas serializer reproduces all packed PPtrs, aligned UTF-8 names, every complete key/map value, tag and variant flag. Unsupported nonempty bone/bindpose/secondary-texture layouts reject; their absence here is measured from source and corroborated by the complete original bytes, not assumed globally.

Hash-equal inverse serialization first validates the captured bytes. Fresh original recovery then compares **actual object bytes to the complete expected byte string**, preserves original spans, and re-reads the typed zero counts. Thus this is stronger corroboration of this bounded capture, while still sharing schema/framing lineage. It says nothing about an unobserved runtime registration/deformation.

## Independent join and bounds reproduction

The new join code does **not instantiate the shared raw102 Graph** and does not use peer bounds as an output source:

1. Keep file-qualified identities. Resolve local or external PPtrs only through the owner's exact external path table; reject missing/ambiguous/type-mismatched targets. No name-only, pathID-only or basename fallback.
2. Reconcile each atlas's packed PPtrs against actual Sprite names in the serialized order, and check each Sprite's back-pointer to that atlas.
3. Match **all four GUID words plus the signed local-ID part** of `m_RenderDataKey` in the referenced atlas, not a partial key or texture/name heuristic. Require one-to-one map use and packed membership. Preserve static packing/UV transforms; do not claim to execute a live remap.
4. Decode the source vertex payload directly: active channels `(0,stream0,float32,3)` and `(4,stream1,float32,2)`, 16-byte stream alignment, source uint16 triangle indices and checked submesh extents. Bounds are min/max over those unchanged local positions. No pivot recentering, renderer resizing, transform, skinning or default-mesh substitute.

Concrete continuity check: the previously handed-off #5 `level2:5739` references `resources.assets:3564`, **Panel_Info**. Here it resolves to atlas580605, map index10/packed index10, texture844 **1024×1024**, source texture rect `(886,0,94,50)` and the complete GUID words `[853326460,1112935796,410675115,4067762750]` plus local-ID21300000. Its **stored four-vertex** AABB is x ±0.4699999988079071, y ±0.25, z0. That is **not** #5's separately modeled sliced16-vertex geometry for a resized renderer. The two bounds belong to different, explicitly retained stages; neither overwrites the other.

## Comparison with primary — no forced agreement

`atlas/peer-af518716b7.json.gz` is the **byte-for-byte handed-off primary artifact** extracted with `git show <scientific>:<path>`, not a peer-tree import or edit. SHA256 **`8d320f1458f8966ca9acfc11a166194cf9e4e77380db1b8f990e68f0d5338e65`**, 599,494B. It is used only after our own source joins/decodes. Adapters normalize file qualification, and compare canonical values (including signed zero and missing-vs-null distinction). Any difference would be emitted with both values/identity/source pins; no repair-to-peer path exists.

Measured comparisons in the artifact:

- Primary atlas records **66/66**, mapping rows **1,550/1,550**, static bounds/skin metadata **2,185/2,185**: all match.
- Inherited `datas/sprite_mesh_contract.json.gz` (mesh75) positions, triangles, hashes and bounds **2,185/2,185**: all match; this is explicitly shared lineage, not another original capture.
- Streamed raw102 overlap **1,389 Sprite + 44 SpriteAtlas**, including whole-object SHA, source keys/PPtrs, empty bone/bindpose arrays, source positions/indices and redacted buffer SHA (or complete Atlas trees): all match.
- **5,986 comparison records**, **1,433 raw102 crosscheck records**, **0 difference records**. Agreement reinforces the bounded static result; it is not native remap/skinning/readback agreement.

Artifact `source_pins` retains **305 path SHA pins**, including every raw geometry and scanned raw102 object shard, mesh75, peer snapshot, source witness/query, original-CI receipt and relevant code. Font73 is lineage of the preserved prior #4, **not a source of Sprite bounds in #6**.

## OOM-safe implementation and reproduction

New code is confined to the own namespace:

- `tools/verify/geometry_8141386a_atlas_io.py`: one-record JSONL and incremental top-level-array decoder, per-value budget, deterministic gzip/header and **250-record** flushes, atomic output.
- `tools/verify/l3_geometry_8141386a_atlas_binary.py`: seeded inverse serialization and separate static vertex/index decoding; fail-closed unsupported layouts/extents/nonfinite values.
- `tools/verify/geometry_8141386a_atlas_sources.py`: streamed source queries and exact pins.
- `tools/recovery/geometry_8141386a_atlas_bytes.py`: disk-copy nested ZIP entries, mmap **compressed** bundle bytes only, at most **16** decoded blocks, streamed object hashes; no whole-bundle inflation or whole-texture image decode.
- `tools/verify/l3_geometry_8141386a_atlas.py`: SQLite-backed joins/comparisons and incremental artifact output; only one Sprite/atlas tree or bounded metadata prefix is decoded at a time. Full-dataset fixtures are not used.

Actual standalone local builder measurement: **27,992 KiB peak RSS**, reproduced artifact SHA exact. Scope is that one local process, not full-suite or CI peak memory. `atlas/build-performance-local.json` SHA256 `415333243cccb89cff29011fbff0131b9d41870d3aa1bdd277c4db3e3dcdaed9` retains the measured value, timing, Python/code/output pins. CI peak memory is not claimed.

```bash
python3 -m tools.verify.geometry_8141386a_atlas_sources --check
python3 -m tools.verify.l3_geometry_8141386a_atlas --check
# Original source, if available (read-only):
python3 tools/recovery/geometry_8141386a_atlas_bytes.py --xapk /path/to/original/windwings.xapk
python3 -m unittest tests.test_geometry_8141386a_atlas_binary tests.test_geometry_8141386a_atlas -v
python3 -m unittest discover -s tests -v
python3 -m tools.verify.geometry_8141386a_history
python3 -m tools.verify.geometry_8141386a_item_receipt --item 6 --check
python3 tools/refresh-readme-sizes.py --check
python3 tools/verify-claims.py
python3 tools/verify-claims.py --unscoped-legacy
```

**37 focused #6 tests PASS /7.487s** before final combined/full gates. They cover original complete-object equality, deterministic streams, exact file/key identity and ambiguity, malformed key/unsupported layout/truncation/index/nonfinite counterexamples, original span/hash/count tampering, hash-only Texture2D refusal, zero-AABB distinction, canonical comparison, all static array invariants and fixed cache bounds. Source checkpoint full **1,447 PASS /304.197s** is separate from the final scientific full-suite receipt. **Final local full suite: 1,467 PASS /307.408s; combined #5/#4/support/#6 focused suite: 96 PASS /13.101s.** Complete logs and exact scientific/report pins are retained in `verification-6.json.gz`. Final exact-head CI is reported in the subsequent PR12 HANDOFF only after actual success; source recovery GREEN is not substituted for it.

## Scoped boundary and missing X

**Static byte-proof scope is delivered. Native live remapping and runtime-deformed bounds are NOT proved.** Empty Sprite arrays and a serialized atlas correspondence do not establish what native code subscribes, requests, registers, deforms or instantiates during play; nor do they prove global absence of those mechanisms. This work does not make a whole-program no-subscriber/no-SpriteSkin claim.

To go beyond this bounded result requires **X**: pinned original native remap/deformation consumers **with actual input/state/instance provenance**, or an authorized same-build runtime receipt binding loaded atlas + Sprite + render key + scene instance and placement-authoritative vertex/bounds readback. Static records have no such execution trace or deformed buffer. Declared APIs in the primary audit are not substituted for that missing state. Actual packing application, draw calls, skinning, world transforms, shader displacement, pixels and rendering remain outside this artifact. No guessed default mesh or screenshot gate.

## Verification pattern, common-file deltas and preservation

Retain the externally approved pattern: frozen original baseline **160/27/24**, **current unscoped163/25/23 (exit1, not relabeled green)**, and **scoped historical-support compatibility209/0/2** from spec0e2af55f4's immutable99-path snapshot with every claim/group/FAIL/SKIP retained. No new unscoped failure IDs/count regression is allowed. These support assertions are **not** all-current-peer, geometry/native or runtime acceptance.

Same-commit changes to shared support files are only the own live APKD1/AI1/RD1 needles, import receipt and own scoped workflow's added #6 gate/tests. Own live needles are APKD1 **120/107**, AI1 **(139,142136,142,138,42,78)**, RD1 **41/0**. README refresh/check has **0 drift**; no unrelated needle expectation is repaired. The report/receipt/logs retain exact scientific pins. `scientific-ci-4.json.gz` separately records actual old #4 GREEN REST metadata so history checks can keep #4 immutable when live needles advance, just as already done for #5. **No #4/#5 artifact, report, scientific verification receipt or pinned code is regenerated.**

The three protected paths remain unchanged and are checked against pinned hashes/latest fetched spec. No peer tool/artifact edits, old revoked-branch push, main push/merge/self-ACK, `[skip ci]`, mass regeneration, original APK modification or >5MB file/commit. #7/#8 are not started before this #6 handoff. Review requested: complete inverse-object and typed count offsets; exact ownership/key/packed reconciliation; static decode and zero-AABB distinction; canonical comparison/lineage; bounded memory behavior and native/runtime refusal boundary.
