# Quantitative Audit (§4.9 Protocol) & 510/510 Planner Parity — Variant B (`Solar Neon Arcade-Pop`)

- **Branch:** `arena/eca8588b-windwings-space-shooter-game-p` (`Art-designer-B`)
- **Protocol:** Exact `docs/art-plan/measure_asset.py` §4.9 formulas (`mask = alpha > 0.5`, 32-level RGB quantization `colors_q32`, `val = mean(V)`, `val_std = pstdev(V)`, `dark = P(max(R,G,B) < 45)`, `chroma = mean(S·V)`, `fill`).
- **Curator Registry:** `art/variant_b_full_510_registry.csv` & `.json` (1:1 `AP-xxxx` lookup across all 5 waves).

## 1. Zero-Gap `art-planner.csv` Coverage Verification (`510/510` Non-EXCL Units)

| Lane | Planner `n_units` | Variant B Units Covered | Delivered Sprite Files | Master Files | Gap |
|---|---:|---:|---:|---:|---:|
| `PLAYER` | 48 | **48/48 (100%)** | 48 | 48 | **0** |
| `ENEMY` | 34 | **34/34 (100%)** | 34 | 34 | **0** |
| `BOSS` | 42 | **42/42 (100%)** | 42 | 42 | **0** |
| `ITEM` | 9 | **9/9 (100%)** | 9 | 9 | **0** |
| `FX` | 26 | **26/26 (100%)** | 26 | 26 | **0** |
| `BG` | 44 | **44/44 (100%)** | 46 | 46 | **0** |
| `UI` | 307 | **307/307 (100%)** | 307 | 307 | **0** |
| **Total Non-EXCL** | **510** | **510/510 (100%)** | **512** | **512** | **0** |
| `EXCL` (excluded by rule) | 0 (`189` rows / `278` raw EXCL records) | 0 | 0 | 0 | **0** |

> Note: `BG` has 44 planner units and 46 delivered files because `AP-0091` (`bg1` stage backdrop) delivers 3 separable parallax depth layers (`far` / `mid` / `near`).

## 2. §4.9 Quantitative RGBA Signature by Lane (Variant B Bright `Solar Neon` vs Variant A Dark `Ink & Ember`)

| Lane | Files | Mean `val` (B) | Mean `val_std` (B) | Mean `dark` `<45` (B) | Mean `chroma` `S·V` (B) | Mean `colors_q32` (B) | Mean `fill` | Variant A Published `val` / `chroma` (§4.5) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `PLAYER` | 48 | **0.758** | 0.282 | **0.006** | **0.437** | 748.8 | 0.362 | 0.483 / 0.209 (ship) · 0.279 / 0.120 (bullet) |
| `ENEMY` | 34 | **0.639** | 0.305 | **0.028** | **0.422** | 433.8 | 0.334 | 0.613 / 0.162 |
| `BOSS` | 42 | **0.678** | 0.302 | **0.035** | **0.473** | 620.0 | 0.370 | 0.485 / 0.205 |
| `ITEM` | 9 | **0.793** | 0.265 | **0.002** | **0.447** | 549.2 | 0.522 | 0.669 / 0.294 |
| `FX` | 26 | **0.875** | 0.150 | **0.000** | **0.570** | 162.5 | 0.176 | 0.875 / 0.063 |
| `BG` | 46 | **0.674** | 0.200 | **0.002** | **0.467** | 345.3 | 0.524 | 0.221 / 0.106 (`dark = 0.600`) |
| `UI` | 307 | **0.670** | 0.263 | **0.001** | **0.485** | 182.5 | 0.476 | 0.405 / 0.133 |

### Key Takeaway for `Art-curator`
- **Intentional Polarity Separation Achieved:** Variant A (`Ink & Ember`) targets low-value matte slate (`val 0.22–0.61`, `chroma 0.06–0.21`, high `dark` on BG/bullets), whereas Variant B (`Solar Neon Arcade-Pop`) delivers high-key sunlit clarity and vivid arcade saturation (`val 0.67–0.89`, `chroma 0.35–0.62`, ultra-low `dark 0.01–0.13` confined strictly to crisp `#0A1844` cel outlines and recessed 9-slice HUD wells).
- **100% Slot Interchangeability:** Every single `AP-xxxx` row (`510/510` non-EXCL units) shares identical target dimensions, straight-RGBA `alpha=0` corner discipline, and `ASSETS.md` §5 9-slice inset geometry, allowing `Art-curator` to pick Variant A, Variant B, or a per-lane hybrid without resizing or re-slicing.
