# Variant B (`Solar Neon 2.5D Semi-Realistic Metallic`) — Full 510/510 Parity & Extended 2.5D Metrics

- **Branch:** `arena/eca8588b-windwings-space-shooter-game-p` (`Art-designer-B`)
- **Style Mandate:** `STYLE-CORRECTION (lần 149 / 238f2b41c / PR #12 6446004160)` — True 2.5D Semi-Realistic Metallic (`pbr25d.py` v2: multi-stop 3D curved normals, contact AO, engraved panel seams, louver vents, rivets, top zenith rim-light, glossy Blinn-Phong specular, **0 thick cartoon outlines**)
- **Canonical Planner:** `docs/art-plan/art-planner.csv` (`788` rows total = `510` non-EXCL units + `278` EXCL rows)
- **Parity Result:** **`510 / 510` non-EXCL planner units (`100.0%`)** delivered (`512` PNG sprites + `512` high-res `masters/`) · `EXCL` drawn = **`0`**
- **Side-by-Side Comparison Sheets (`BẢNG SO KẾ CẠNH`):** `preview/w{0,1,2,3,4,5}b_side_by_side_ref.png` generated for every wave.

## 1. Per-Wave §4.9 + Extended 2.5D Metrics (`STYLE-CORRECTION lần 149`)

| Wave | Files | Mean `gradient_stops` (`≥3–5`) | Mean `outline_dark_px` (`≤1.0`) | Mean `detail_density` | Mean `lum_contrast` | Mean `val` | Mean `chroma` | Mean `colors_q32` | Side-by-Side Sheet |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **W1** | **48** | **10.88** | **0.020 px** | **83.33** | **0.646** | 0.750 | 0.394 | 1709.9 | `art/w1-*/preview/w1b_side_by_side_ref.png` |
| **W2** | **34** | **12.71** | **0.017 px** | **98.78** | **0.687** | 0.658 | 0.356 | 1085.7 | `art/w2-*/preview/w2b_side_by_side_ref.png` |
| **W3** | **42** | **13.60** | **0.042 px** | **58.88** | **0.720** | 0.664 | 0.379 | 4668.8 | `art/w3-*/preview/w3b_side_by_side_ref.png` |
| **W4** | **114** | **6.37** | **0.004 px** | **20.72** | **0.485** | 0.799 | 0.547 | 556.4 | `art/w4-*/preview/w4b_side_by_side_ref.png` |
| **W5** | **274** | **6.55** | **0.002 px** | **23.71** | **0.551** | 0.767 | 0.544 | 463.2 | `art/w5-*/preview/w5b_side_by_side_ref.png` |
| **ALL (`W1..W5`)** | **512** | **7.90** | **0.008 px** | **36.50** | **0.568** | **0.757** | **0.505** | **987.1** | **6/6 Boards PASS** |

## 2. Per-Lane Parity & Extended 2.5D Summary

| Lane | Planner Units | Delivered Units | PNG Files | `gradient_stops` | `outline_dark_px` | `detail_density` | `lum_contrast` | `val` | `dark` | `chroma` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `PLAYER` | 48 | **48** | 48 | **10.88** | **0.020 px** | **83.33** | 0.646 | 0.750 | 0.010 | 0.394 |
| `ENEMY` | 34 | **34** | 34 | **12.71** | **0.017 px** | **98.78** | 0.687 | 0.658 | 0.007 | 0.356 |
| `BOSS` | 42 | **42** | 42 | **13.60** | **0.042 px** | **58.88** | 0.720 | 0.664 | 0.019 | 0.379 |
| `ITEM` | 9 | **9** | 9 | **6.67** | **0.000 px** | **39.22** | 0.541 | 0.891 | 0.000 | 0.455 |
| `FX` | 26 | **26** | 26 | **3.96** | **0.000 px** | **16.03** | 0.334 | 0.936 | 0.000 | 0.635 |
| `BG` | 44 | **44** | 46 | **7.26** | **0.014 px** | **12.71** | 0.519 | 0.704 | 0.016 | 0.462 |
| `UI` | 307 | **307** | 307 | **6.59** | **0.001 px** | **24.45** | 0.550 | 0.771 | 0.001 | 0.553 |
| `EXCL` | 0 (278 rows) | **0** | 0 | — | — | — | — | — | — | — |
