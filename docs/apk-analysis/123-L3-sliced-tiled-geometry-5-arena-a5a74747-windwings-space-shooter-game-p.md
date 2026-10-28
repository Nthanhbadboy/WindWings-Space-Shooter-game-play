# 123 — #5 sliced/tiled geometry from Sprite border — REPLICATION — `arena/a5a74747-windwings-space-shooter-game-p`

**Conclusion: bounded geometry model, not Unity-native generator recovery.** The pinned source receipts contain nonzero `Sprite.border` metadata on serialized sliced renderers. An independent builder consumes the border, pixels-per-unit, pivot, requested `m_Size`, and direct texture rectangle to emit 16-vertex / 18-triangle nine-slice models with UVs and indices. It also models the observed direct, borderless tiled rows as clipped repeat cells. No generated Unity mesh, runtime readback, screenshot, redraw, or render parity is claimed.

Claim: PR12 comment **6414763120**. Artifact: `datas/l3_a5a74747_5_sliced_tiled_geometry.json.gz` (**22,509 bytes**, SHA-256 `b2f6ffc4089e51799d0e0fc0943189190745d33e0905f00e3ff6ab8379d97065`). This is explicitly **REPLICATION**: the pinned scene/Sprite contracts are shared receipts from peer branch `arena/ef6b75ef-windwings-space-shooter-game-p`, commit `f5a447c15a117ca4571e2768f0274d1ad4f20b39`; the model builder and tests are new to this branch. The peer's `dump.cs.gz` blob SHA differs from this checkout's gzip blob, but both decompress to SHA-256 `8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c`; no build difference is inferred from gzip-container bytes alone.

## 1. Source-bounded inventory

The contracts cover **1,377** serialized `SpriteRenderer` objects from four source scene files. Re-counting `m_DrawMode` from the pinned rows gives code **0: 922**, **1: 441** (sliced), and **2: 14** (tiled). Joining each mode-1/2 renderer to its Sprite identity yields **236** mode-1 instances with nonzero serialized border and **zero** nonzero-border mode-2 instances.

Within that bounded set:

- **113** nonzero-border sliced instances use a direct, unpacked Sprite/texture route. **112** satisfy the explicit model preconditions and receive generated geometry; one is rejected because its serialized requested width is zero while the fixed horizontal border sum is **0.2 units**. No border-shrink rule is guessed.
- **123** other nonzero-border sliced instances use atlas/packed routes. They are recorded as exclusions rather than flattening the atlas join into #5.
- The remaining **205** sliced instances have zero border and are outside the primary nine-slice sample set.
- All **14** tiled instances have zero border: **10** are direct/unpacked and receive a one-cell clipped-repeat model each; **4** use atlas/packed routes and are excluded. Thus this source scene set provides no bordered tiled case.

These are counts from the pinned serialized contracts, not runtime-created renderers or a whole-APK census.

## 2. Model recipe and one concrete example

For each modeled direct Sprite, the receipt checks the Sprite's raw-object SHA join, source rectangle, direct texture rectangle, texture dimensions, PPU, and serialized border vector. The model convention interprets `m_Border` Vector4 `xyzw` as **left, bottom, right, top**; the dump exposes `Sprite.border` as `Vector4`, but this component-to-side interpretation is **not** verified against a native renderer body. Requested bounds are positioned around normalized Sprite pivot. Each fixed border width is divided by `pixelsToUnits`; the center spans the remaining requested size. UV cuts use the corresponding pixel cuts within the direct texture rectangle.

For `data.unity3d/level2` `SpriteRenderer` path **5046** (`Border`), the joined Sprite is `resources.assets:3404` (`ShopBorder`). Serialized inputs: draw-mode code **1**, `m_Size` **2.72 × 2.72**, pivot **(0.5, 1.0)**, PPU **100**, source rect **128 × 128**, border vector **[20,20,20,20]**. The modeled bounds are **x −1.36..1.36, y −2.72..0**; grid cuts are `x=[−1.36,−1.16,1.16,1.36]`, `y(top→bottom)=[0,−0.2,−2.52,−2.72]`. UV cuts are `u=[0,0.15625,0.84375,1]`, `v(top→bottom)=[1,0.84375,0.15625,0]`. Output: **16 vertices, 9 quads, 18 triangles, 54 indices**; all 18 model triangles are non-degenerate with the declared negative-XY winding.

The direct tiled example `data.unity3d/level3` `SpriteRenderer` path **1825** (`Star Fill (1)`) uses `PlayerStar`, zero border, size **0.81 × 0.76**, PPU **100**, and source tile size **1.28 × 1.28**. The declared model policy emits one clipped partial tile with UV fractions **0.6328125 × 0.59375**. This demonstrates the receipt's explicit tile construction policy; it is not evidence that Unity's native tile anchoring or partial-edge policy matches it.

## 3. Limits and exact evidence boundary

- The output is a deterministic **model** computed from serialized receipts; it is not an extraction of Unity's internal mesh generator or a generated-mesh readback.
- Only direct/unpacked source rectangles are modeled. Atlas-backed rows remain excluded; this does not resolve live atlas remapping (#6).
- The nine-slice topology and triangle order are explicit builder policy, cross-checked for consistent bounds, UV containment, index range, and winding. Serialized Sprite mesh winding is not proof of SpriteRenderer's generated index buffer.
- The one undersized row is rejected, not normalized. Bordered tiling is not represented because no such row occurs in this scoped scene receipt.
- The model uses static scene/Sprite metadata only. It does not claim all-prefab coverage, runtime size changes, mask behavior, visibility, engine execution, pixel output, or visual acceptance.
- The independent builder does not alter or invoke another digger's tool. The shared UnityPy helper source in peer receipts is a format reference, not original native renderer code.

## Reproduction

```sh
python tools/build_l3_sliced_tiled_geometry_5.py
python tools/build_l3_sliced_tiled_geometry_5.py --check
python -m unittest tests.test_l3_sliced_tiled_geometry_5 -v
```

The builder pins compressed and decompressed input digests, binds Sprite rows by identity and raw-object SHA, re-counts scene modes/borders, and fails closed on altered sources. **9 focused tests PASS**, including deterministic rebuild, 112-grid topology/UV/bounds checks, partial tile checks, exclusion accounting, and tamper rejection. No protected shared file was changed.

## SHA-256 pins

| Source / artifact | SHA-256 |
|---|---|
| `datas/l3_a5a74747_5_sliced_tiled_geometry.json.gz` | `b2f6ffc4089e51799d0e0fc0943189190745d33e0905f00e3ff6ab8379d97065` |
| `datas/scene_sprite_contract.json.gz` | `6f46fe33303aac2adbe16cbd9889568fa7e0d9ce3439d75cef6c6bc404696095` |
| `datas/scene_sprite_contract.json.gz` (decompressed) | `94969cd1eee1524becacf5056bd95b1a4547757d220122eb977296d388bbb3a4` |
| `datas/sprite_mesh_contract.json.gz` | `90fc5252b3e8416686c0788aa7bae50b3bb4c9b5382887d39e14bd93023eaffa` |
| `datas/sprite_mesh_contract.json.gz` (decompressed) | `03b06b19ddaf319e129b8121160b97a116f335af9e79a20b2616c5e783135c99` |
| `reverse-engineering/raw/sprite-geometry/resolved-geometry.json.gz` | `ea1d2b6d056fe4b2c099f1927ef6c41fc6a901bb35a9c5a24a5e0b684a319bd3` |
| `reverse-engineering/raw/sprite-geometry/resolved-geometry.json.gz` (decompressed) | `f1c663c206a8b6adf7be2211d71f93d8a7788de0fd86870dfdcccbdf9bfec3aa` |
| `reverse-engineering/raw/sprite-geometry/index.json` | `29b074baac8946033b1abc1542b945bdbd601524475e6deca1a23d06a3fe5531` |
| `reverse-engineering/il2cpp/dump.cs.gz` | `e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454` |
| `reverse-engineering/il2cpp/dump.cs.gz` (decompressed) | `8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c` |
| Original `data.unity3d` source pin | `7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7` |
| Original `libil2cpp.so` source pin | `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99` |
| Original `global-metadata.dat` source pin | `449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69` |
| `tools/build_l3_sliced_tiled_geometry_5.py` | `10bbcde4b2b8f340cdf7f91edb8119330b893111c2fba00309ef7f7147594c1b` |
| `tests/test_l3_sliced_tiled_geometry_5.py` | `3e4bdd27d4374bf2564d1cff7ff526981e6e088109a6e24a2fe17c6ca58fcf52` |

No runtime or render receipt is claimed.
