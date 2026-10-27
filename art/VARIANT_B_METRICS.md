# Variant B (`Solar Neon 2.5D Semi-Realistic Metallic`) — Full 510/510 Parity & Extended 2.5D Metrics

- **Branch:** `arena/eca8588b-windwings-space-shooter-game-p` (`Art-designer-B`)
- **Style Mandate:** `STYLE-CORRECTION (lần 149 / 238f2b41c / PR #12 6446004160)` — True 2.5D Semi-Realistic Metallic (`pbr25d.py` v2: multi-stop 3D curved normals, contact AO, engraved panel seams, louver vents, rivets, top zenith rim-light, glossy Blinn-Phong specular, **0 thick cartoon outlines**)
- **Canonical Planner:** `docs/art-plan/art-planner.csv` (`788` rows total = `510` non-EXCL units + `278` EXCL rows)
- **Parity Result:** **`510 / 510` non-EXCL planner units (`100.0%`)** delivered (`512` PNG sprites + `512` high-res `masters/`) · `EXCL` drawn = **`0`**
- **Side-by-Side Comparison Sheets (`BẢNG SO KẾ CẠNH`):** `preview/w{0,1,2,3,4,5}b_side_by_side_ref.png` generated for every wave.

## 1. Per-Wave §4.9 + Extended 2.5D Metrics (`STYLE-CORRECTION lần 149`)

| Wave | Files | Mean `gradient_stops` (`≥3–5`) | Mean `outline_dark_px` (`≤1.0`) | Mean `detail_density` | Mean `lum_contrast` | Mean `val` | Mean `chroma` | Mean `colors_q32` | Side-by-Side Sheet |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **W1** | **48** | **8.44** | **0.000 px** | **68.59** | **0.617** | 0.845 | 0.482 | 1804.5 | `art/w1-*/preview/w1b_side_by_side_ref.png` |
| **W2** | **34** | **10.50** | **0.000 px** | **70.70** | **0.715** | 0.784 | 0.419 | 912.3 | `art/w2-*/preview/w2b_side_by_side_ref.png` |
| **W3** | **42** | **10.62** | **0.000 px** | **38.22** | **0.694** | 0.782 | 0.471 | 3453.8 | `art/w3-*/preview/w3b_side_by_side_ref.png` |
| **W4** | **114** | **6.37** | **0.004 px** | **20.72** | **0.485** | 0.799 | 0.547 | 556.4 | `art/w4-*/preview/w4b_side_by_side_ref.png` |
| **W5** | **274** | **6.65** | **0.002 px** | **22.88** | **0.527** | 0.787 | 0.563 | 407.5 | `art/w5-*/preview/w5b_side_by_side_ref.png` |
| **ALL (`W1..W5`)** | **512** | **7.34** | **0.002 px** | **31.12** | **0.552** | **0.794** | **0.535** | **855.0** | **6/6 Boards PASS** |

## 2. Per-Lane Parity & Extended 2.5D Summary

| Lane | Planner Units | Delivered Units | PNG Files | `gradient_stops` | `outline_dark_px` | `detail_density` | `lum_contrast` | `val` | `dark` | `chroma` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `PLAYER` | 48 | **48** | 48 | **8.44** | **0.000 px** | **68.59** | 0.617 | 0.845 | 0.000 | 0.482 |
| `ENEMY` | 34 | **34** | 34 | **10.50** | **0.000 px** | **70.70** | 0.715 | 0.784 | 0.000 | 0.419 |
| `BOSS` | 42 | **42** | 42 | **10.62** | **0.000 px** | **38.22** | 0.694 | 0.782 | 0.002 | 0.471 |
| `ITEM` | 9 | **9** | 9 | **6.33** | **0.000 px** | **37.95** | 0.539 | 0.905 | 0.000 | 0.459 |
| `FX` | 26 | **26** | 26 | **3.35** | **0.000 px** | **15.16** | 0.311 | 0.953 | 0.000 | 0.647 |
| `BG` | 44 | **44** | 46 | **7.37** | **0.014 px** | **10.54** | 0.492 | 0.716 | 0.016 | 0.477 |
| `UI` | 307 | **307** | 307 | **6.73** | **0.001 px** | **24.14** | 0.535 | 0.784 | 0.001 | 0.566 |
| `EXCL` | 0 (278 rows) | **0** | 0 | — | — | — | — | — | — | — |
