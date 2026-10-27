# 127 — #6 bounded SpriteAtlas remap and Sprite bounds — arena/a5a74747-windwings-space-shooter-game-p

## Claim and disposition

PR12 item #6 was claimed in comment `6415839139`. This audit resolves the pinned serialized SpriteAtlas render-data maps to Sprite identities, then pairs the same Sprite object hashes with the existing serialized-mesh contract for static vertex bounds.

**Disposition: exact static atlas-map coverage; live/runtime remap and deformed skin bounds remain `NOT_OBSERVED`.** The static receipt does not establish a `SpriteAtlasManager` callback, runtime atlas request/registration, runtime scene instance, or a deformed mesh. It closes only the bounded evidence available from the pinned serialized inputs.

## Static SpriteAtlas mapping

The source index pins UnityPy 1.25.4 output from a `data.unity3d` input hash `7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7`. The inventoried six JSONL shards contain **2,185 Sprite**, **66 SpriteAtlas**, and **654 Texture2D metadata-only** records. Each shard's decoded SHA-256 and row count is checked against the raw index before the builder reads it.

The exact identity join is:

1. For an atlas-backed Sprite, resolve `m_SpriteAtlas` as a local PPtr in its owning serialized file.
2. Canonicalize the complete two-part `m_RenderDataKey` and look it up in that exact atlas's `m_RenderDataMap`.
3. Resolve the packed Sprite PPtr in `m_PackedSprites` and check its ordered `m_PackedSpriteNamesToIndex` value against the Sprite name.
4. Resolve the render-data texture PPtr to a Texture2D metadata record in the same serialized file.

| Check | Result |
|---|---:|
| Serialized SpriteAtlas objects | 66 |
| Atlas `m_RenderDataMap` entries | 1,550 |
| Atlas `m_PackedSprites` PPtrs | 1,550 |
| Atlas packed-name rows / exact ordered name matches | 1,550 / 1,550 |
| Sprite → atlas PPtr + exact render-data-key joins | **1,550** |
| Atlas texture PPtr → metadata joins | 1,550 |
| Direct Sprite `m_RD` route (no atlas PPtr) | 635 |
| Unresolved / ambiguous Sprite-atlas joins | **0** |
| Unmatched packed Sprite PPtrs | **0** |
| Cross-atlas duplicate render-data keys | **0** |

The receipt retains all 1,550 Sprite-to-atlas crosswalk rows, exact render keys, map and packed-list indices, atlas object identities, texture metadata identities/dimensions, texture rectangles, offsets, UV transforms, and packing settings. Each of the 66 atlas records also retains its object hash and normalized render-map digest. This is a serialized map join, not a rendered atlas or proof that every atlas is requested in a particular play session.

The 635 remaining Sprites have a direct serialized `m_RD` route and empty `m_AtlasTags` in this input set. Those rows are kept separate from the 1,550 atlas-backed joins; no fallback or name-only match is used.

## Skinning fields and static bounds

Across the 2,185 inventoried Sprite typetrees:

- `m_Bones` length is zero for **2,185/2,185**.
- `m_RD.m_Bindpose` length is zero for **2,185/2,185**.
- The only vertex-channel descriptors with nonzero dimensions are channel indices **0** (dimension 3) and **4** (dimension 2), for all 2,185 records. This is the serialized vertex layout; it is not a runtime skinning proof.
- The pinned `datas/sprite_mesh_contract.json.gz` has **27,072** decoded static vertices and an identity/hash match for all 2,185 raw Sprite records. The receipt stores each Sprite's static vertex AABB separately from its serialized `m_SubMeshes.localAABB`.
- The serialized submesh `localAABB` is zero for all **2,185** Sprite rows in this contract. It is not replaced with the locally measured vertex AABB.

The static vertex AABB is derived geometry from the serialized Sprite vertex data. It is **not** a skin/deformation bound, scene/world bound, Unity runtime result, or camera/pixel bound. Empty bone/bindpose fields are scoped to these Sprite typetrees; they do not prove that no other component, native system, or runtime-generated mesh can deform geometry.

## Runtime boundary

The pinned IL2CPP API dump declares `UnityEngine.U2D.SpriteAtlasManager` with `atlasRequested` and `atlasRegistered` events. Those declarations do not show that game code subscribes, raises a request, registers an atlas, or uses a remapped Sprite. No running session or readback was performed, and no callback/consumer path is asserted here.

The remaining live/remap/deformation question needs an authorized runtime receipt that identifies the loaded atlas, resolved Sprite, scene instance, and any deformed vertex/bounds state—or an owner-provided scene/runtime dump with the same placement authority. Static atlas maps alone cannot close that question. No APK modification, fabricated mesh, screenshot, or render approval was used.

## Provenance and reproducibility

The six raw geometry shards were copied byte-for-byte from peer snapshot `arena/ef6b75ef-windwings-space-shooter-game-p` at `72041a1d400be6b0972f5bfa9868efe3befaeca7`; each decoded hash and row count matches the existing local source index. The shard history commit is `d9739910662be2de07f44faba30ed72e4b593e5c`. The source index pins `data.unity3d`, `libil2cpp.so`, and `global-metadata.dat` hashes, but this audit did not independently retrieve or decode the original package. The Unity dump and mesh-contract hashes are also embedded in the receipt.

| Input / output | SHA-256 |
|---|---|
| Raw index `reverse-engineering/raw/sprite-geometry/index.json` | `29b074baac8946033b1abc1542b945bdbd601524475e6deca1a23d06a3fe5531` |
| Mesh contract `datas/sprite_mesh_contract.json.gz` | `90fc5252b3e8416686c0788aa7bae50b3bb4c9b5382887d39e14bd93023eaffa` |
| Pinned IL2CPP dump `reverse-engineering/il2cpp/dump.cs.gz` | `e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454` |
| Artifact `datas/l2_a5a74747_6_spriteatlas_remap.json.gz` (**599,494 bytes**) | `8d320f1458f8966ca9acfc11a166194cf9e4e77380db1b8f990e68f0d5338e65` |
| Builder `tools/build_l2_a5a74747_6_spriteatlas_remap.py` | `b68b320c5bf53977374fec625ab81a9d37d403290d1c5a08d2f41220cfc15892` |
| Tests `tests/test_l2_a5a74747_6_spriteatlas_remap.py` | `4d58012a13f514bad5df9c9e1d54763598961e74d1cbcdc9561edf2d2298a8e9` |

Rebuild and verify:

```bash
python3 tools/build_l2_a5a74747_6_spriteatlas_remap.py
python3 -m unittest tests.test_l2_a5a74747_6_spriteatlas_remap -v
```

## Limits

- Serialized SpriteAtlas mapping only; no live request/registration, runtime scene, GPU rendering, or pixel result.
- Static vertex AABBs are not deformed/skinned bounds; serialized submesh local AABBs remain zero.
- Empty `m_Bones` / `m_Bindpose` arrays are a scoped observation over the 2,185 inventoried Sprite typetrees, not a global absence proof for components, native code, or runtime-generated geometry.
- No independent original-package retrieval occurred in this audit; package-input hashes are those embedded in the pinned source index.
