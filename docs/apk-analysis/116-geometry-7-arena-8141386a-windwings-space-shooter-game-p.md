# 116 — #7: seven original builtin ParticleSystemRenderer mesh refs resolved

provenance: **`arena/8141386a-windwings-space-shooter-game-p`**
CLAIM PR12 `6417945015`, after #6-rep HANDOFF `6417920301`. Static only.

## Result and scope

**All seven raw102-gap references resolve to actual Mesh objects in the original APK's
standalone `assets/bin/Data/unity default resources`.** The missing-file error in raw102
was a missing extraction input, **not absence from the APK**. No default primitive is
constructed or substituted. Names **Cube** and **Quad** below come from original object
`m_Name` bytes, not assumptions about Unity builtin IDs.

Artifact `datas/l3_geometry_builtin_8141386a.json.gz`: **24,112 B**, SHA256
`2b1c4eace14fb770389b7c1e533a2f574270deab87641008ee994ac34133db40`.
It retains seven exact owning-file PPtrs, source SHA pins, actual vertices/all active
channels/indices, computed Mesh-local bounds, serialized AABBs, typed source-byte spans,
and the falsified initial missing-source hypothesis. **426 input/code/receipt pins.**

This is a **captured-closure** result: raw102 has **954** ParticleSystemRenderers,
**17** nonnull `m_Mesh*` pointers: **10 other/local + 7 builtin**. Original bundle
metadata contains **4,845** class199 objects; the other **3,891** renderer objects were
not decoded by this query. Do not rebrand seven as all builtin references in the APK.
Nor does resolution prove these pointers are consumed by a native particle draw.

## The counterexample that changed the investigation

1. Stream every raw102 indexed object/link JSONL shard, checking compressed SHA and row
   count. Select nonnull ParticleSystemRenderer `m_Mesh*` and resolve the PPtr using the
   **owner's** external table, never a global pathID or guessed basename join.
2. All selected links carry the original raw102 `FileNotFoundError` for `unity default
   resources`. `selected-inputs.json.gz` retains the exact rows/locations and source pins.
3. Fresh read-only source run **40338034941 SUCCESS**, source
   `2a29b83de8c25ab26ac0c55a6dc8c0bd9058387e`, produced initial inventory witness (bot
   `30c9b57d2`). The original compressed bundle has **16 nodes / 12 SerializedFiles /
   717,262 object metadata entries / 2 Mesh entries**. The desired file is not a bundle
   node. **But the nested base-APK entry-name inventory contains the standalone file.**
4. Preserve that first witness/actual run receipt as `builtin/inventory-byte-witness-v1.json.gz`
   / `inventory-ci-v1.json.gz`; do not backfit a missing-package conclusion. The helper's
   `NOT_PRESENT_AS_BUNDLE_NODE` diagnosis is only that bundle lookup and is superseded
   by the standalone lookup. No global impossibility assertion is adopted from it.
5. Extended source run **40339964488 SUCCESS**, source
   `368e5ee29f346a571303d18f9f6e91127b673655`, reads the actual standalone file and only
   the two requested Mesh objects. Bot `c06bafb62` fetched by fast-forward; no reset/rebase.

Both original recoveries are distinct from final scientific/report CI. No raw CI log,
CI test-count or CI memory claim is made from the REST run/jobs metadata.

## Original source pins and declared versions

| Source | Bytes | SHA256 |
|---|---:|---|
| original XAPK | 142125649 | `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` |
| base APK | 117158131 | `6843e79347f5b0bb68e4a2f9e1b1a3152e31d0875d4821b9928ad5799a95e1e1` |
| `data.unity3d` | 63881856 | `7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7` |
| standalone `unity default resources` | 1121184 | `a9a74ab363888de3ea14ef01e780f851a395d4c6f5d5bcebad74a2a3e4785d16` |
| final original witness `builtin/byte-witness.json.gz` | 32879 | `9013f257abf2c72eaca13db473657cc29075d9b823bd0cd5e83c37703a4b8f4e` |
| actual source CI receipt `builtin/source-ci-receipt.json.gz` | 2658 | `af3b101c794793290747c2f3e686bd927569e8bd722c316de496b6e9d2d02a17` |

Raw receipt paths are under `reverse-engineering/raw/geometry-8141386a/`.
The standalone file declares **Unity `2022.3.54f1`, SerializedFile v22** and has
**85 object metadata entries / 13 Mesh entries**. This file declaration is retained,
not overwritten with raw102's consulted generator version `2022.3.62f3`. Only **two**
Mesh payloads were decoded for #7; the other eleven are metadata inventory, not #8 work.
No different-build resource catalog was substituted.

## Exact owner, PPtr, and source-byte proof

All owners below are **`data.unity3d/resources.assets`**. Original external-table slot
**2** is exactly `Library/unity default resources`; all fields are `m_Mesh`.
The seven original full renderer hashes agree with raw102 (**2,180 B total**).
Each target has a **unique aligned 12-byte** original PPtr match (**84 B total**).
Field interpretation is capture-seeded; byte search is disclosed as corroboration,
not independent field-layout discovery.

| owner pathID | target pathID | original name | numeric serialized mode | PPtr object offset | original renderer SHA256 |
|---:|---:|---|---:|---:|---|
| 505276 | 10210 | Quad | 1 | 244 | `89e9ed092d6eda33b8948a39fd8eb3ae5f0f5133da3ac0585380a4908d36b23c` |
| 505279 | 10210 | Quad | 0 | 244 | `2bb37ff7b638a6f18e0732c0f4c81bba2fc834b49cd7122141d75e91e614596c` |
| 507218 | 10202 | Cube | 1 | 240 | `b038ed89209520da19f2562d107855684b618e85fd0870d14388cdb8f928a647` |
| 507699 | 10210 | Quad | 1 | 244 | `5d43d64e6bc65ebbec59e644cc9247e4e59b35be213abc89b598f3b7f5ba5025` |
| 507701 | 10210 | Quad | 0 | 244 | `2bc4b2d16d80166cd609dc70db6c1def79a3f92627ab9002b20b0b4653fd5c6a` |
| 508192 | 10210 | Quad | 0 | 244 | `1d534118d1affc8f92ae2ba45a66843e9ef824cb854eb5eaf69bd6a76fb40eed` |
| 508193 | 10210 | Quad | 1 | 244 | `4470a5ad96bfb7cbbb375aa5c72b376ef6d319c044a7d143a1f10c216df2f4bf` |

PPtr hex: target10210 = `02000000e227000000000000`; target10202 =
`02000000da27000000000000`. Numeric modes **1×4 / 0×3** are preserved without claiming
active native mesh-mode use, runtime mutation or a particle-geometry output.

## Actual Mesh bytes, independent supplied-schema decode, and static bounds

The inherited stdlib **controller109 binary Reader** consumes **all 2,428 Mesh bytes**
against explicitly captured UnityPy1.25.4 builtin schemas. **2/2 decoded trees exactly
match the captured trees** after byte-array normalization. **48 typed root spans**
retain offsets/sizes/SHA, including the non-ambiguous full `m_LocalAABB` fields.
An own decoder then reads the actual inline Float32 stream/channel layout and UInt16
indices; it does **not** call UnityPy/MeshHelper and does not generate primitives.
All four vertex/index payloads have unique exact matches in original Mesh bytes.

| actual object | object bytes | vertices / indices / triangles | original vertex payload offset:length | index payload offset:length | typed AABB offset:length |
|---|---:|---|---|---|---|
| 10202 Cube | 1820 | 24 / 36 / 12 | 248:1344 | 108:72 | 1756:24 |
| 10210 Quad | 608 | 4 / 6 / 2 | 188:192 | 108:12 | 544:24 |

- Cube object SHA `d8f0b9cf294e3ec49acb73d4a738a70b282c4e06890f354bb2ffe09c9be47b19`;
  local min `[-0.5,-0.5,-0.5]`, max `[0.5,0.5,0.5]`. Preserve **24 face vertices**,
  not an eight-corner cube; retain normals/tangents/UV0/**UV1** and original winding.
- Quad object SHA `a011b7668060df09340e550322f72f1ea635e5c8461ea3fbfb2a6f4071fff82a`;
  local min `[-0.5,-0.5,-3.0616168005906746e-17]`, max
  `[0.5,0.5,3.0616168005906746e-17]`. **Do not snap Z to zero** or replace UVs/indices
  with an ideal quad. Stored AABB center/extent is retained separately.

Total unique source geometry: **28 vertices / 42 indices / 14 triangles**. Zero
byte/tree/PPtr disagreements in the asserted comparisons is not a peer geometry,
native particle generator, instance transform, frame/render or runtime-parity claim.

## Memory, provenance, and scientific limitations

Original ZIP members are copied incrementally to scratch disk. Original bundle stays
compressed/mmap-backed with the frozen #6 reader's <=16 block cache (each <=2 MiB),
<=32 MiB metadata-prefix budget, one SerializedFile table at a time. The standalone
file is **1.12 MB**, explicitly refused above32MiB before UnityPy loading; metadata is
loaded, only **two small Mesh trees** decoded. No full atlas bundle inflation, all2185
Sprite fixture, giant Graph, media export, APK modification, or new runtime session.
**No measured peak-RSS claim** for these new source/full-test runs.

Lineage is explicit: raw102 UnityPy capture/schema/Graph framing, acknowledged ef
UnityFS111/SerializedFile110, frozen own #6 bounded block reader, UnityPy1.25.4
standalone framing/builtin schemas, inherited stdlib109 supplied-schema decoder, and
own Mesh stream/index decoding with consulted UnityPy layout/alignment conventions.
Byte equality strengthens this scoped extraction; it is **not clean-room schema
discovery, native execution, TypeTree readback or render acceptance**.

The captured-gap #7 is closed by **(a) original bytes + SHA pins**, not by missing-X.
Still unproved: original-instance native ParticleSystemRenderer consumer, mode/state
changes, billboard/particle generation, transforms/world/pixel bounds, live deformation
and renderer output. All such artifact fields remain null. Runtime lane is closed per
spec78/owner instruction; no device/secret request or probe is proposed here.

## Verification and handoff

Final local test/needle receipts below record actual completed runs.
Source-only checkpoints remain historical: **8focused/1475full PASS**, including
source2 full1475 in313.985s; they are not final scientific acceptance.

- New #7 regression tests: **19 PASS /4.086s** before final combined/full run.
- Final combined focused: **115 PASS /17.191s** (closed#5/#4/support/#6 +19new#7).
- Final full discovery: **1486 PASS /303.930s** (complete log ends `OK`).
- Same-report live needles: **APKD1 121/107; AI1 (139,142136,142,138,42,79); RD1 41/0**. README refresh/check: **0 drift**.
- **Scoped historical-support209/0/2**; current unscoped **163/25/23 (exit1)**, no new failure IDs versus frozen160/27/24. Full per-claim/per-group results retained, not relabeled.

Final `verification-7.json.gz` + four complete logs preserve baseline160/27/24,
per-claim/per-group support snapshot and actual local results. Approved support scope
is **historical-support209/0/2**, never all-current-ef/scientific/runtime acceptance.
The post-push exact-head Verify/scoped/PR15 vehicle run IDs belong in the PR12 HANDOFF
and separate historical CI receipt, not a self-referential pre-CI report. Vehicle
bridge/session gates may skip: successful CI still does not create runtime evidence.

Shared-file deltas are only three live needles/import hashes plus own scoped#7 gate
and tests; no unrelated spec rewrite, peer tool/tree import, revoked-branch/main push,
merge, skip-ci or self-ACK. Protected3 and handed-off #4/#5/#6 scientific bytes stay
unchanged and are verified against their actual historical Git commits. **#8 has not
been started before #7 handoff.**

Reproduce:

```sh
python3 -m tools.verify.geometry_8141386a_builtin_sources --check
python3 -m tools.verify.l3_geometry_8141386a_builtin --check
python3 -m unittest tests.test_geometry_8141386a_builtin_sources tests.test_geometry_8141386a_builtin -v
python3 -m tools.verify.geometry_8141386a_history
python3 tools/refresh-readme-sizes.py --check
python3 tools/verify-claims.py --require APKD1,AI1,RD1
```
