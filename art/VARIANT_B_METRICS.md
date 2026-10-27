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
| **W1** | **48** | **11.44** | **0.044 px** | **119.41** | **0.676** | 0.677 | 0.300 | 2675.6 | `art/w1-*/preview/w1b_side_by_side_ref.png` |
| **W2** | **34** | **12.47** | **0.003 px** | **114.99** | **0.642** | 0.594 | 0.260 | 1220.8 | `art/w2-*/preview/w2b_side_by_side_ref.png` |
| **W3** | **42** | **13.69** | **0.101 px** | **105.06** | **0.694** | 0.529 | 0.254 | 6485.7 | `art/w3-*/preview/w3b_side_by_side_ref.png` |
| **W4** | **114** | **5.81** | **0.004 px** | **20.94** | **0.517** | 0.773 | 0.536 | 598.9 | `art/w4-*/preview/w4b_side_by_side_ref.png` |
| **W5** | **274** | **6.54** | **0.004 px** | **23.97** | **0.548** | 0.759 | 0.538 | 459.4 | `art/w5-*/preview/w5b_side_by_side_ref.png` |
| **ALL (`W1..W5`)** | **512** | **7.81** | **0.015 px** | **44.94** | **0.571** | **0.725** | **0.474** | **1243.2** | **6/6 boards generated; audit pending** |

## 2. Per-Lane Parity & Extended 2.5D Summary

| Lane | Planner Units | Delivered Units | PNG Files | `gradient_stops` | `outline_dark_px` | `detail_density` | `lum_contrast` | `val` | `dark` | `chroma` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `PLAYER` | 48 | **48** | 48 | **11.44** | **0.044 px** | **119.41** | 0.676 | 0.677 | 0.018 | 0.300 |
| `ENEMY` | 34 | **34** | 34 | **12.47** | **0.003 px** | **114.99** | 0.642 | 0.594 | 0.002 | 0.260 |
| `BOSS` | 42 | **42** | 42 | **13.69** | **0.101 px** | **105.06** | 0.694 | 0.529 | 0.058 | 0.254 |
| `ITEM` | 9 | **9** | 9 | **7.56** | **0.000 px** | **43.15** | 0.563 | 0.842 | 0.000 | 0.443 |
| `FX` | 26 | **26** | 26 | **4.42** | **0.000 px** | **15.51** | 0.349 | 0.926 | 0.000 | 0.629 |
| `BG` | 44 | **44** | 46 | **6.22** | **0.010 px** | **13.42** | 0.497 | 0.664 | 0.002 | 0.431 |
| `UI` | 307 | **307** | 307 | **6.46** | **0.003 px** | **24.58** | 0.560 | 0.762 | 0.001 | 0.549 |
| `EXCL` | 0 (278 rows) | **0** | 0 | — | — | — | — | — | — | — |
