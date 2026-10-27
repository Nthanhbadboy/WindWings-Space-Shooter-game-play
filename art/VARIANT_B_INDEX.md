# Variant B — Solar Neon Commercial 2.5D Metallic · Audit Response Index

- **Role / Branch:** `Art-designer-B` · `arena/eca8588b-windwings-space-shooter-game-p`
- **Current response:** commit `a71412d3427e3c2d9d01ee519a154be289091923` (independent A/B audit) + Director `lần 158` hero-first instruction.
- **Palette:** bright Solar Neon character/key-art accents over grounded dark-cobalt gameplay backgrounds; not Variant A's dark Ink & Ember.
- **License / author:** `chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)` / `arena/eca8588b-windwings-space-shooter-game-p` in every wave manifest.
- **Approval state:** **not self-approved**. Static checks and visual evidence are submitted for Art-style-auditor Layer-1 + Layer-2; runtime, pivot, motion, VFX blend, binding and three-person kinship remain unverified.

## Deliverables and review evidence

| Area | Current delivery | Review evidence |
|---|---|---|
| **W0 listing** | `art/w0-listing-b/` · exact **25/25** filenames, dimensions and RGB/RGBA modes; 9 masters; S1–S4 rebuilt from current B sprites on dark-cobalt stage | `preview/w0_contact_sheet.png` · `audit_a71412d_response/comparisons/05_w0_concept_hierarchy.png` · **CONCEPT, not runtime captures** |
| **W0 build icons** | `art/w0-build-icons-b/` · ICO + Android mipmap set from W0 icon master | `BUILD_ICONS_MANIFEST.md` |
| **W1 PLAYER** | `art/w1-player-b/` · **48/48** (25 ships, 13 drones, 8 bullets, 2 FX); decoded ship/drone IDs in `planner_base`; painted candidates #01/#04/#08/#12/#13 and drones #04/#05 | `preview/w1b_side_by_side_ref.png` · `audit_a71412d_response/comparisons/01_hero_calibration.png` |
| **W2 ENEMY** | `art/w2-enemy-b/` · **34/34**; AP-0067 corrected to neutral white HP fill | `preview/w2b_side_by_side_ref.png` · `audit_a71412d_response/comparisons/03_enemy_anchors.png` |
| **W3 BOSS** | `art/w3-boss-b/` · **42/42**; painted ID-anchored families for 7001–7005 and Mk variants | `preview/w3b_side_by_side_ref.png` · `audit_a71412d_response/comparisons/02_boss_decoded_ids.png` |
| **W4 CORE** | `art/w4-core-b/` · **114 files / 112 rows**; darkened sky layer; FX reference mapping corrected | `preview/w4b_side_by_side_ref.png` · `audit_a71412d_response/nine_slice_contract.csv` |
| **W5 FULL** | `art/w5-full-b/` · **274/274**; semantic ShopIcon/event/Blink/coin/tech-node corrections; planets and dark stage gradients revised | `preview/w5b_side_by_side_ref.png` · `audit_a71412d_response/comparisons/04_w5_semantics.png` |
| **Total** | **510/510 planner units**, **512 sprite records**, corresponding masters; EXCL = 0 | `audit_a71412d_response/static_validation.{json,md}` · **0 errors / 0 warnings** |

## Current Variant-B proxy summary (not planner's raw metric)

These are the branch's legacy proxy definitions, included for continuity only. They are **not** a substitute for the unmodified planner or aesthetic review.

| Wave | Files | `gradient_stops` | `outline_dark_px` | `detail_density` | `lum_contrast` | `val` | `chroma` | `colors_q32` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| W1 PLAYER | 48 | 10.81 | 0.020 px | 89.06 | 0.646 | 0.749 | 0.382 | 1758.1 |
| W2 ENEMY | 34 | 12.12 | 0.011 px | 111.95 | 0.666 | 0.666 | 0.325 | 1172.5 |
| W3 BOSS | 42 | 12.81 | 0.020 px | 78.42 | 0.699 | 0.632 | 0.331 | 5040.0 |
| W4 CORE | 114 | 5.81 | 0.004 px | 20.94 | 0.517 | 0.773 | 0.536 | 598.9 |
| W5 FULL | 274 | 6.55 | 0.002 px | 23.77 | 0.546 | 0.759 | 0.538 | 458.2 |
| **ALL W1..W5** | **512** | **7.67** | **0.006 px** | **39.60** | **0.569** | **0.745** | **0.492** | **1034.7** |

## Unmodified planner evidence (required by audit)

- `art/audit_a71412d_response/planner_raw_metrics.csv`: **512/512 PNGs measured, 0 read errors**, using unmodified `measure_asset.py` SHA-256 `c33182347dabf7e1eba4a3278d298a62a89a43ccbc2ae75e3ba0d6181a22b053` from planner `100cfcebc3`.
- Raw proxy result: **393/512** files have at least one style-band value outside the planner proxy range; this is reported, not hidden or “fixed” by changing the metric. The planner itself notes these are global proxies, not per-panel gradients or a beauty score.
- Three `outline_px > 1` records are full-frame boss sky/curtain and ringed Saturn background cases; the audit explicitly warns not to interpret opaque-canvas/background edge proxies as cartoon outlines.
- Palette `val/chroma/dark` bands remain **CONFLICTING** for bright Solar Neon B, exactly as the independent audit states; no unilateral baseline change is made.
- `art/audit_a71412d_response/planner_raw_metrics.csv` and `art/VARIANT_B_METRICS.md` intentionally use different metric definitions; do not compare their numbers as if identical.

## Static acceptance and remaining gates

- `static_validation.{json,md}`: 512 records, 25 W0 slots, metadata/source/dimensions/alpha checks, **0 errors / 0 warnings**.
- `nine_slice_contract.csv`: 3 actual frames × 3 sizes (`320×240`, `480×360`, `720×1080`), exact corner preservation and uniform-center checks pass statically.
- `duplicate_extra_files = 100` across current W4/W5 inventory: reported for semantic/integration review; duplicate hash alone is not called a defect. The four auditor-flagged semantic collisions are fixed with distinct art.
- `comparisons/`: **23 review pairs** with source sheet/tile/crop/SHA-256 and candidate SHA-256. References are never game assets.
- **Still pending:** auditor's commercial aesthetic verdict and hero lock; real Godot build capture (10 gameplay + 3 reward frames), pivot/trim/scene placement, motion/trails/additive blending, actual UI binding, and the requested three-person same-game check.
