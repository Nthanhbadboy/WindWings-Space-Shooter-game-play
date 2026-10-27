# Response to independent audit `a71412d3427e3c2d9d01ee519a154be289091923`

**Role:** Art-designer-B · **Branch:** `arena/eca8588b-windwings-space-shooter-game-p` · **Date:** 2026-10-28
**Status:** static evidence + visual candidates submitted; **not self-approved** by Art-style-auditor, curator, or runtime.

## 1. What was read and what was corrected

The audit's pinned A/B snapshots, 11 comparison boards, raw planner protocol, decoded `datas/` anchors, Director `lần 157` (`NGUYÊN MẪU LÀ THƯỚC`) and `lần 158` (P0 hero-first) were read before changing art. No protected path (`docs/spec/`, `datas/`, `tools/`) is modified by this response.

| Audit finding | Response in this branch | Evidence / honest limit |
|---|---|---|
| **P0: lock a hero before fleet expansion** | `Ship 10001` is the explicit hero candidate; current #01 plus painted #08/#12/#13 and drone #04 are submitted for calibration. Existing fleet was revised, but no self-declared hero lock is claimed. | `comparisons/01_hero_calibration.png`, `hero_probe/hero_64px_probe.png`, `hero_probe/hero_panel_metrics.csv`. Auditor still must lock both technique and beauty. |
| **W0: concept is not gameplay capture; overbright/dense hierarchy** | All 25 immutable store slots retained. S1–S4 rebuilt as dark-cobalt composites from current B ship/enemy/boss/drone sprites with safe HUD margins, sparse projectiles and local impact bursts. | `comparisons/05_w0_concept_hierarchy.png`, `w0_frame_metrics.csv`, `W0B_MANIFEST.md`. **Still CONCEPT—not a Godot screenshot; recapture before store submission.** |
| **W1: repeated hull/canopy formula, missing ID clarity** | Decoded IDs now appear per row (`GLYPH-ship-10001…10999`, `GLYPH-drone-20001…20013`); new painted commercial candidates add distinct ring, mecha and articulated-wing anatomy. | `w1b_units.{json,csv}`, hero board and 64px probe. Original `unit_no → runtime sprite` binding is not invented. |
| **W2: invalid analogue pairs and AP-0067 semantics** | Five explicit auditor anchors are used. AP-0067 is a neutral white rounded HP fill and is measured as UI by the audit wrapper, not as an enemy body. | `comparisons/03_enemy_anchors.png`, `w2b_units.*`. Other enemy pairings remain visual analogues, not invented ID bindings. |
| **W3: boss comparison by row instead of decoded ID; repeated core** | Board builder now maps `GLYPH-boss-ID` through the decoded tile anchor (7001→#2 … 7005→#6). Five painted boss families and Mk variations replace the generic core/wing formula for the corresponding families. | `comparisons/02_boss_decoded_ids.png`, `w3b_side_by_side_ref.png`. Detach/destructibility/Spine/pivots remain runtime-unverified. |
| **W4/W5: logo/glyph reference misuse, bright BG, flat semantic reuse** | FX references now use bullet/FX sheets; `sky_far` and stage gradients are grounded; Earth/Jupiter receive multi-scale surface/storm structure. `ShopIcon`, `nennutevent`, `Blink`, tech nodes, `CoinIcon`, `Goicoin1` now have function-specific art. | `comparisons/04_w5_semantics.png`, `static_validation.*`, `nine_slice_contract.csv`. Remaining duplicate hashes are inventoried, not automatically called defects. |
| **Metrics ≠ beauty / conflicting gates** | Ran the unmodified planner on every current B sprite and preserved raw failures. Legacy B metrics are labelled as different definitions. No band was edited to make the art pass. | `planner_raw_metrics.csv`, `VARIANT_B_METRICS.md`, `VARIANT_B_INDEX.md`. |

## 2. Static acceptance result

Run:

```bash
python3 -B art/audit_a71412d_response/validate_static.py \
  --root . --out art/audit_a71412d_response
```

Current result:

- **512/512** sprite records across W1–W5; **510/510** non-EXCL planner-unit coverage; **25/25** W0 store slots; EXCL drawn = 0. Independent filename/px/mode comparison against pinned `4a65378e` is in `w0_contract_check.json` (`all_25_filename_px_mode_match = true`).
- Every referenced sprite and source master exists; dimensions, author, license and recipe are present.
- Straight-RGBA corner checks pass, including the corrected transparent boss flank curtain.
- **0 errors / 0 warnings** in the static validator.
- **9-slice:** three real frames × `320×240`, `480×360`, `720×1080`; corners are exact and center stretch regions are uniform in the probe. This is a static image test, **not** engine integration.
- Current inventory reports **100 duplicate extra files** across W4/W5 for review. Shared frame pixels can be intentional; the four semantic collisions specifically identified by the auditor were fixed with different art.

## 3. Unmodified planner raw metrics

The wrapper is `measure_b_with_planner.py`; the upstream function is unmodified `measure_asset.py` at planner commit `100cfcebc3`, SHA-256:

`c33182347dabf7e1eba4a3278d298a62a89a43ccbc2ae75e3ba0d6181a22b053`

Result: **512/512 PNGs read, 0 errors**. These are raw proxy measurements, not an approval score.

| Class | Files | Mean grad stops | Mean outline px | Mean detail | Mean V | Mean V std | Mean dark | Mean chroma | 3-proxy in-band |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ship | 25 | 39.32 | 0.088 | 0.661 | 0.688 | 0.229 | 0.015 | 0.313 | 0/25 |
| drone | 13 | 34.92 | 0.000 | 0.738 | 0.715 | 0.209 | 0.002 | 0.343 | 0/13 |
| enemy (AP-0067 as UI) | 22 | 37.05 | 0.166 | 0.844 | 0.657 | 0.212 | 0.004 | 0.336 | 0/22 |
| boss | 42 | 37.88 | 0.228 | 0.545 | 0.632 | 0.220 | 0.009 | 0.331 | 0/42 |
| bullet | 19 | 25.37 | 0.000 | 0.599 | 0.775 | 0.146 | 0.003 | 0.447 | 0/19 |
| fx | 28 | 10.21 | 0.000 | 0.058 | 0.931 | 0.067 | 0.000 | 0.629 | 2/28 |
| item | 9 | 21.22 | 0.000 | 0.363 | 0.842 | 0.128 | 0.000 | 0.443 | 0/9 |
| bg | 28 | 24.04 | 0.718 | 0.059 | 0.713 | 0.151 | 0.037 | 0.414 | 12/28 |
| ui (incl. AP-0067) | 326 | 15.45 | 0.001 | 0.172 | 0.753 | 0.163 | 0.001 | 0.542 | 105/326 |

- **393/512** files have at least one planner style proxy outside its band. This is deliberately visible in the CSV; the response does not claim a technical or aesthetic PASS from the older Variant-B summary.
- Three `outline_px > 1` records are the full-frame boss sky/curtain and ringed-Saturn background. The audit itself warns that opaque-canvas/background edge proxies are not cartoon-outline measurements. They remain flagged for reviewer context rather than silently removed.
- Planner `val/chroma/dark` bands are Ink & Ember anchored and **CONFLICTING** with the intentionally bright B direction; no unilateral B baseline is invented.

Reproduce:

```bash
python3 -B art/audit_a71412d_response/measure_b_with_planner.py \
  --root . --planner /tmp/ww_tools/docs/art-plan/measure_asset.py \
  --out art/audit_a71412d_response/planner_raw_metrics.csv --workers 2
```

## 4. W0 frame review flags

`measure_w0_frames.py` uses the exact pinned `tools/design-metrics.py` (`77bb6a91…`) on four original phone captures and four current B concepts. It does not promote concepts to G-C/runtime evidence.

| Frame | REF p95−p05 | B concept p95−p05 | REF accent (all hues) | B accent | REF detail-gradient | B detail-gradient |
|---|---:|---:|---:|---:|---:|---:|
| S1 / formation | 0.6674 | 0.3524 | 0.0510 | 0.0279 | 20.81 | 21.84 |
| S2 / boss | 0.5282 | 0.3467 | 0.0571 | 0.0297 | 17.38 | 26.07 |
| S3 / drones | 0.6255 | 0.3083 | 0.0540 | 0.0217 | 20.98 | 17.31 |
| S4 / beam | 0.5107 | 0.4387 | 0.0247 | 0.0207 | 13.26 | 28.31 |

The revised scenes are less overbright than the rejected B concepts, but still need real-build composition and motion review. `accent_all_hues` is not a hot-color-only budget.

## 5. Rebuild and review package

```bash
# Current-art comparison boards (23 indexed pairs, exact crops + SHA-256)
python3 -B art/audit_a71412d_response/build_comparisons.py \
  --spec-root /tmp/ww_tools --root . \
  --out art/audit_a71412d_response/comparisons

# Hero 64px + region probe
python3 -B art/audit_a71412d_response/hero_probe.py \
  --spec-root /tmp/ww_tools \
  --planner /tmp/ww_tools/docs/art-plan/measure_asset.py \
  --out art/audit_a71412d_response/hero_probe

# Static checks and manifest refresh
python3 -B art/audit_a71412d_response/validate_static.py --root . --out art/audit_a71412d_response
python3 -B art/audit_a71412d_response/refresh_manifest_docs.py
```

`comparisons/index.csv` contains **23 pairs** with reference sheet/tile/crop/SHA and candidate path/SHA. All original contact sheets and phone captures are review-only references; none is copied into a game asset.

## 6. Explicitly still open

1. Art-style-auditor must judge **both** technical floor and commercial aesthetics, then lock/reject the hero. This branch does not self-issue that verdict.
2. No Godot project/build exists on this art-only branch. Runtime capture, 10 gameplay + 3 reward frames, pivot/trim/scene placement, motion/trails, additive VFX blending and actual UI binding remain **RUNTIME_UNVERIFIED**.
3. The three-person “same game as the original” recognition test has not been performed or fabricated.
4. Store screenshots must be recaptured from the real release build; current S1–S4 are concept composites and are not submission-ready captures.
5. User confirmation of title/art rights remains pending in every manifest.
