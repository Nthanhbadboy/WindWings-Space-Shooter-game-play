# Variant B (`Solar Neon 2.5D Semi-Realistic Metallic`) — Full 510/510 Parity & Extended 2.5D Metrics

- **Branch:** `arena/eca8588b-windwings-space-shooter-game-p` (`Art-designer-B`)
- **Style Mandate:** `STYLE-CORRECTION ROUND 2 (lần 154 / 965c770c9)` + audit `a71412d3` — commercial 2.5D metallic (`pbr25d.py` v3 + painted masters + `mecha25d.py` v2), with AO, seams, vents, rivets, rim-light and no thick cartoon outlines.
- **Canonical Planner:** `docs/art-plan/art-planner.csv` (`788` rows total = `510` non-EXCL units + `278` EXCL rows)
- **Parity Result:** **`510 / 510` non-EXCL planner units (`100.0%`)** delivered (`512` PNG sprites + corresponding exported masters + additional painted source masters) · `EXCL` drawn = **`0`**
- **Side-by-Side Comparison Sheets (`BẢNG SO KẾ CẠNH`):** 6/6 boards generated; this is evidence, not aesthetic approval. See `audit_a71412d_response/` for decoded-ID pairs and raw planner metrics.
- **Metric caveat:** this legacy summary uses Variant-B proxy definitions; the unmodified planner's 50-bin / 0.8% metrics are reported separately in `audit_a71412d_response/planner_raw_metrics.csv`. Numbers are a floor, never a PASS by themselves.

## 1. Per-Wave §4.9 + Extended 2.5D Metrics (`STYLE-CORRECTION lần 149`)

| Wave | Files | Mean `gradient_stops` (`≥3–5`) | Mean `outline_dark_px` (`≤1.0`) | Mean `detail_density` | Mean `lum_contrast` | Mean `val` | Mean `chroma` | Mean `colors_q32` | Side-by-Side Sheet |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **W1** | **48** | **10.81** | **0.020 px** | **89.06** | **0.646** | 0.749 | 0.382 | 1758.1 | `art/w1-*/preview/w1b_side_by_side_ref.png` |
| **W2** | **34** | **12.12** | **0.011 px** | **111.95** | **0.666** | 0.666 | 0.325 | 1172.5 | `art/w2-*/preview/w2b_side_by_side_ref.png` |
| **W3** | **42** | **12.81** | **0.020 px** | **78.42** | **0.699** | 0.632 | 0.331 | 5040.0 | `art/w3-*/preview/w3b_side_by_side_ref.png` |
| **W4** | **114** | **5.81** | **0.004 px** | **20.94** | **0.517** | 0.773 | 0.536 | 598.9 | `art/w4-*/preview/w4b_side_by_side_ref.png` |
| **W5** | **274** | **6.55** | **0.002 px** | **23.77** | **0.546** | 0.759 | 0.538 | 458.2 | `art/w5-*/preview/w5b_side_by_side_ref.png` |
| **ALL (`W1..W5`)** | **512** | **7.67** | **0.006 px** | **39.60** | **0.569** | **0.745** | **0.492** | **1034.7** | **6/6 boards generated; audit pending** |

## 2. Per-Lane Parity & Extended 2.5D Summary

| Lane | Planner Units | Delivered Units | PNG Files | `gradient_stops` | `outline_dark_px` | `detail_density` | `lum_contrast` | `val` | `dark` | `chroma` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `PLAYER` | 48 | **48** | 48 | **10.81** | **0.020 px** | **89.06** | 0.646 | 0.749 | 0.009 | 0.382 |
| `ENEMY` | 34 | **34** | 34 | **12.12** | **0.011 px** | **111.95** | 0.666 | 0.666 | 0.005 | 0.325 |
| `BOSS` | 42 | **42** | 42 | **12.81** | **0.020 px** | **78.42** | 0.699 | 0.632 | 0.009 | 0.331 |
| `ITEM` | 9 | **9** | 9 | **7.56** | **0.000 px** | **43.15** | 0.563 | 0.842 | 0.000 | 0.443 |
| `FX` | 26 | **26** | 26 | **4.42** | **0.000 px** | **15.51** | 0.349 | 0.926 | 0.000 | 0.629 |
| `BG` | 44 | **44** | 46 | **6.57** | **0.014 px** | **13.45** | 0.505 | 0.655 | 0.023 | 0.425 |
| `UI` | 307 | **307** | 307 | **6.42** | **0.001 px** | **24.40** | 0.557 | 0.764 | 0.001 | 0.550 |
| `EXCL` | 0 (278 rows) | **0** | 0 | — | — | — | — | — | — | — |
