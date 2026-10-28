# 113 — #5 REPLICATION: nonzero-border atlas sliced/tiled geometry

provenance: **`arena/8141386a-windwings-space-shooter-game-p`**

Disposition: **BOUNDED_METADATA_DRIVEN_MODEL_WITH_SOURCE_BYTE_PROOF**. Not native
SpriteRenderer generator recovery, Unity mesh readback, live atlas remap or render.
Primary #5 remains a5a74747 (claim6414763120, handoff6414968058, spec6415041499).
This independently implemented replication uses a separate tool/artifact namespace;
it does not import or edit a5's generator. Shared ef raw102 / reference resolution and
UnityFS111/Serialized110 framing are **not independent second decoders**.

## 1. Claim, base, authority and reproducibility

- Own claim: PR12 comment6414948672; progress6415033718/6415218002.
- Mandatory initial base: ef scientific tip `f5a447c15a117ca4571e2768f0274d1ad4f20b39`,
  then exactly three protected paths from spec `0e2af55f4b2cf1ee6b0b2b66bf151aa28573013d`.
  Own base commit `600a4a340bd27d7e9e63a53941bbe6d97ce430bf`, pushed/ls-remote confirmed.
  Later coordination tips are fetched/read, **not merged over this work**.
- Original XAPK SHA256 `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`.
- Original base.apk SHA256 `6843e79347f5b0bb68e4a2f9e1b1a3152e31d0875d4821b9928ad5799a95e1e1`.
- Original `assets/bin/Data/data.unity3d` SHA256
  `7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7`.
- Artifact: `datas/l3_geometry_bounds.json.gz`, **12,087 B**, SHA256
  `0b77e656d26463a50126a9ad87afbf2a921449301990a61452a8ea330822d8c5`.
  It contains full numeric vertices, UVs, source-pixel coordinates, indices,
  per-cell topology, bounds/area/winding invariants, source identities and SHA pins.
- Code: `tools/verify/{geometry_8141386a_sources,l3_geometry_8141386a_math,l3_geometry_8141386a}.py`.
  Raw inputs/receipts only under `reverse-engineering/raw/geometry-8141386a/`.

```bash
python3 -m tools.verify.geometry_8141386a_sources --check
python3 -m tools.verify.l3_geometry_8141386a --check
python3 -m unittest tests.test_geometry_8141386a tests.test_geometry_8141386a_support -v
python3 -m unittest discover -s tests -v
python3 tools/refresh-readme-sizes.py
python3 tools/refresh-readme-sizes.py --check
python3 tools/verify-claims.py
# Honest separate inherited-current compatibility diagnostic (expected nonzero):
python3 tools/verify-claims.py --unscoped-legacy
```

Deterministic JSON/gzip uses sorted keys, rejects NaN, gzip mtime0. No APK modified,
no media extracted into Git, no hundreds-file regeneration. `--allow-pending-witness`
is diagnostic-only and **not used for final artifact/check/handoff**.

## 2. Exact root chain and fresh original-byte witness

`data.unity3d/level2:5739` (SpriteRenderer) → PPtr file2/path3564 →
`resources.assets:3564` **Panel_Info** → SpriteAtlas580605 → **exact render-key pair10**
→ Texture2D844, **1024×1024**. Texture name:
`sactx-0-1024x1024-ETC2-UI_Begin-bcc5de1c`; format47. Render-key equality is checked,
not a texture-name/fuzzy match. The serialized entry is not claimed to be a live remap.

| Object | Full original object SHA256 | Object bytes | UnityFS logical object start |
|---|---|---:|---:|
| level2:5739 | `8576980d7a2c38514af83d6a5384c5721306305fb0e873adbe41347d7b6614c4` | 196 | 44,168,693 |
| resources:3564 | `1fdf1220baef8b804ea9dd320fdf5b7ea351c4c871fc30bcdf24d758750c2cb8` | 440 | 75,219,446 |
| resources:580605 | `cce46a90641b2ad93327659acff2bcaa761a216ab880890811028c57f1c02fa4` | 6,640 | 160,429,406 |
| resources:844 | `658a1fa928a968cbaee29be09a563065b33a73c47d454407b1957c0aa87cafbf` | 180 | 62,573,598 |

Raw102 locations and compressed chunk hashes are rechecked in the selector. **Fresh
source recovery** additionally hashes the original XAPK/APK/bundle, decodes required
UnityFS blocks, reads serialized object tables, and requires all four object hashes
to equal raw102. Metadata-prefix SHA and compressed/decoded block receipts are saved.
The narrow prefix layout is seeded from the captured typetree, not independent schema
discovery; shared ef readers are not presented as clean-room work.

Fresh Sprite3564 object-relative, little-endian source fields:

| Field | Byte offset | Size | Hex / decoded value |
|---|---:|---:|---|
| rect | 16 | 16 | `[0,0,94,50]` |
| offset | 32 | 8 | `[0,0]` |
| **border** | **40** | **16** | **`000034420000a041000034420000a041` → `[45,20,45,20]`** |
| pixels-to-units | 56 | 4 | `0000c842` → **100** |
| pivot | 60 | 8 | `0000003f0000003f` → **[.5,.5]** |

Border-byte SHA256: `2b38a77a5e7d17aeaf3871c9e9f7691294fbe82c31de5ba25cb040f3b37ad0bd`.
The parser re-decodes these saved bytes in tests and compares their numeric values
with the raw102 fields. Four serialized source vertices/UV0 (all UV0 zero) are retained
as evidence but **not substituted as generated sliced geometry**.

Recovery CI **40316865222 SUCCESS**, source head448818788, receipt44c821717.
The first cache-only run40316538827 failed at cache restore, before any APK read;
the fix downloads the pinned release **on CI** when a branch-scoped cache is absent.
Sandbox `gh release download` had failed with release-assets EOF. This was an access
restriction, not proof of absent bytes. Original-source reading succeeded on CI.

## 3. Sliced model: preserve the serialized border, not a stretched quad

Root request: drawMode1, size **10×5**, flipX/flipY false. Source border component
interpretation **left/bottom/right/top**, pivot placement, binary64 arithmetic and
negative-Z row-major triangle topology are explicit CPU model conventions, not recovered
native generator code. Dividing the source border by PPU100 gives `.45,.2,.45,.2`.

| Axis | Destination cuts (local) | Source-pixel cuts | Atlas UV cuts |
|---|---|---|---|
| X | **[-5,-4.55,4.55,5]** | [0,45,49,94] | [886,931,935,980]/1024 |
| Y | **[-2.5,-2.3,2.3,2.5]** | [0,20,30,50] | [0,20,30,50]/1024 |

The atlas rect is `[886,0,94,50]`, rectOffset0, downscale1/settingsRaw1.
Affine UV transform `[100,933,100,25]` is applied to **source local coordinates**, not
to the stretched destination positions. The model requires its source-pivot extents
to match this exact atlas rect before emitting UVs.

Output: **16 vertices / 16 UV / 9 cells / 54 indices / 18 triangles**. AABB
`[[-5,-2.5,0],[5,2.5,0]]`; all indices in range; all finite; 18 negative-winding,
0 zero-area triangles. Triangle area sum **50.000000000000014**, requested area50,
error `1.4210854715202004e-14`, tolerance `5e-9`. UV bounds:
`[.865234375,0]` → `[.95703125,.048828125]`.

Counterexample: a replacement stretched quad maps pixel45 to `-5+10*45/94`,
not `-4.55`; it destroys the preserved `.45` border. The tests explicitly reject that
substitution. They also expand the same model surfaces into **54 unshared vertices**,
with identical triangle area/AABB, illustrating why serialized inputs do not prove
native vertex-sharing/index order.

## 4. Tiled policy, undersized requests and deliberate non-coverage

The independent continuous-tiled implementation preserves outer borders, repeats
only the center seed at source PPU, duplicates vertices at UV discontinuities, and
clips the final tile's UV extent. Adaptive mode rejects rather than guessing native
threshold/rounding behavior. Resource limits are explicit (≤4,096 quads).

Two **synthetic requests using the pinned root Sprite**, not additional observed or
runtime renderer states, are included separately from serialized-case counts:

- Compressed border, size **.4×.2**: opposing borders scaled proportionally per axis;
  the central intervals collapse. Sliced still has16 vertices/54 indices, **10**
  zero-area triangles, area .08. Compression is a declared model policy. Continuous
  tiled compression has only four corner cells; unit tests cover that separately.
- Nonzero-border continuous tiles, size **1.13×.77**: X has8 segments (6 center
  repeats including final .75 tile); Y has6 (4 center repeats including .7 tail).
  **48 cells / 192 vertices / 288 indices / 96 triangles**; area `.8701` within
  tolerance. This is not falsely called a serialized bordered tiled renderer.

The selector captures the concrete root plus **all26 tiled SpriteRenderers in the
raw102 source graph**, 27 cases /39 distinct objects. **Only the root is generated
for serialized requests**. All26 actual tiled rows have zero border and nonzero
trim/offset outside this demonstrated UV domain; each has `not_generated`, null
vertices/UV/indices and an explicit reason. Two are level2 scene rows; asset templates
are marked **NOT placed**. Do not mix the full raw102 scope with peer scene-only counts.

Reject guards also cover rotated/tight packing, downscale, atlas extent mismatch,
invalid/negative/nonfinite sizes/borders/PPU, zero source-center tile seeds and budgets.
No guessed default mesh, animated skinning, live atlas selection or particle geometry
is introduced in #5. Items #4/#6/#7/#8 are **not started by this report**.

## 5. Verification support: explicit dual scope, no manufactured green

The inherited ef tree had5 legacy spec MD +2 CSV; START_HERE/DATA_SYNC and the three
spec verification tools were missing. The permitted specific-path imports are recorded
with source ref/size/SHA in `verification-support-imports.json`: **50 files /2,570,759 B
at import** (38 MD +3 tools +9 asset metadata files). Seven existing paths were preserved;
README only gains a branch-owned measured index. Legacy UI/ASSETS/BALANCE/GAMEPLAY and
peer runtime-probe/raw files are **not overwritten**. These imports are verification
support, not scientific APK evidence or a whole peer-tree checkout.

The first honest unscoped run was **160 PASS /27 FAIL /24 SKIP /0 ERROR**, including
absent archived phone receipts and old support differences, not merely three needles.
It is preserved diagnostically; it was never relabeled 209PASS. The adapter uses an
explicitly printed **historical support view** with **99 named pinned paths** from
spec0e2af55f, stored in a small deterministic bundle. It overlays only disposable
symlinks, checks SHA256/Git blob identities and leaves peer paths untouched.

- **APKD1 / AI1 / RD1 measure the actual own current worktree**, not the view. This
  report and those needles/index are synchronized in the same report commit.
- Other historical assertions retain their original expected values. A regression
  test compares the current verifier to the original source: only APKD1/AI1 count
  blocks and the explicit adapter entrypoint may differ. RD1's41-row contract remains.
- AP1's one extra inherited mismatch was **gzip MTIME only** in `dump.cs.gz`: suffix
  bytes and decompressed SHA256 are identical. The historical support view reconstructs
  the exact pinned10-byte header (with full-byte/Git-blob checks), not another 2.7 MB
  dataset; the original worktree gzip is never rewritten.
- `--unscoped-legacy` still exposes inherited compatibility failures. Scoped
  **209 PASS /0 FAIL /2 SKIP** is **not** a claim that all current ef raw/runtime-probe
  or geometry passed historical verification. Geometry has separate byte/artifact tests.
- No unrelated expected claim is changed to a measured result, no `[skip ci]`, no
  screenshot gate, no merge/main push/self-ACK. The three protected shared paths retain
  exactly the initial spec bytes, enforced by independent fixed SHA pins in tests.
- Spec approved the boundary in comments **6415183905 /6415328887** (sticky round68),
  requiring a pinned support snapshot and every FAIL/SKIP group. These are retained in
  `verification-5.json.gz` plus frozen `_verify_baseline.json` and verbatim gzip logs:
  original **160/27/24**, current unscoped **163/25/23**, scoped **209/0/2**, per-claim
  rows and per-group status ID lists. The99-path snapshot has individual SHA/Git blobs,
  a spec commit pin, named path groups and bundle SHA. Unscoped FAIL count **25≤27**,
  no new failure ID. This is reproducible evidence, not a report-only assertion.
- Same-report live needles: **APKD1 (118,107)**, **AI1 (139,142136,142,138,42,76)**,
  **RD1 (41,0)**. The difference from spec's own inventory is intentional own-worktree
  measurement, never an estimate or substitution of peer counts.

## 6. Tests, CI and review boundary

Focused geometry tests: **30** (including100 fixed-seed randomized sliced requests
inside one test). Support-boundary tests: **9**, including corruption, legacy path
preservation, copy-on-write isolation, protected pins and original-expectations checks.
The first full local run before adding support tests was **1400 PASS /308.815s**;
the final full run including all geometry/boundary tests is **1410 PASS /324.329s**.
Focused **39 PASS /3.676s**; full/focused verbatim logs and code/input SHA pins are in
the same-branch verification receipt. Initial failed development tests (support bundle
missing its original-verifier entry) were repaired and rerun, not counted green.

CI recovery success is **not scientific CI for the final #5 commit**. Handoff requires
pushed remote confirmation and a real green final scientific run; run/code SHA and test
count are added in the handoff/branch-owned receipt after GitHub confirms completion.
No completion/ACK is asserted by this paragraph.

Review requested: exact atlas-key/texture binding; source-byte offset40 border witness;
source-vs-destination UV mapping; compressed-border/tail policy boundaries; topology and
corruption negatives; the explicit historical-support versus current-needle scope.

**Scoped impossibility of further native closure from this evidence:** the stream
contains renderer input parameters, not generated runtime vertex/UV/index arrays.
The same source admits distinct valid vertex-sharing layouts (tested). To decide native
compression, adaptive repetition, trimming and topology order requires a pinned
**libunity generator entry/callees** or approved **same-build vertex/UV/index readback**.
Object hashes and serialized inputs alone cannot establish that. Native generator,
Unity readback, runtime deformation and rendered/pixel acceptance remain open, separately.
