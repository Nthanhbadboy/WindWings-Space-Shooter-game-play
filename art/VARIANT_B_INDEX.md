# Variant B ("Solar Neon 2.5D Semi-Realistic Metallic") — Complete Art Suite Index (`510/510` Non-EXCL Parity)

- **Role / Branch:** `Art-designer-B` · `arena/eca8588b-windwings-space-shooter-game-p`
- **Style Mandate (`STYLE-CORRECTION lần 149` / `238f2b41c` / PR #12 `6446004160`):** Upgraded across all waves to **true 2.5D Semi-Realistic Military Metallic (`art/pbr25d.py` v2)** — continuous multi-stop 3D curved surface normals (`mean gradient_stops = 7.34`, `8.44–10.62` on ships/enemies/bosses), ambient occlusion (`AO`) under stacked armor plates, engraved panel seams, recessed glowing louver vents, metallic rivets, top-down zenith rim-light, focused Blinn-Phong glossy specular highlights, 3D sapphire/amber glass canopies, 3D Terminator-lit celestial planets, and **zero thick cartoon outlines (`mean outline_dark_px = 0.002 px`)** — while preserving Variant B's bright **Solar Neon** tonal polarity (`mean val = 0.794`, `chroma = 0.535`, `lum_contrast = 0.552`) distinct from Variant A's dark "Ink & Ember".
- **License (all waves):** `chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)`
- **Author (all waves):** `arena/eca8588b-windwings-space-shooter-game-p`
- **2.5D PBR Shader & Board Generators:** `art/pbr25d.py` · `art/build_side_by_side_boards.py` · `art/measure_variant_b.py`
- **Curator 510-Unit Lookup Registry:** `art/variant_b_full_510_registry.csv` & `art/variant_b_full_510_registry.json`
- **§4.9 + Extended 2.5D Quantitative Audit:** `art/VARIANT_B_METRICS.md`

## Complete Wave Inventory (`510/510` Non-EXCL Planner Units · `EXCL 278 = 0`) + Side-by-Side Comparison Sheets

| Wave | Directory | Scope & Lanes | Units | Files | Masters | Contact Sheet | Mandatory Side-by-Side Ref Sheet (`BẢNG SO KẾ CẠNH`) |
|---|---|---|---:|---:|---:|---|---|
| **W0** | `art/w0-listing-b/` | Store Listing (Microsoft / Amazon / Huawei — **immutable 25-slot contract**) | 25 store | **25** | **9** | `preview/w0_contact_sheet.png` | `art/w0-listing-b/preview/w0b_side_by_side_ref.png` |
| **W0-Icons** | `art/w0-build-icons-b/` | Build Packaging Icons (`ICO-06` `.ico` 16..256 + `ICO-07` Android `mipmap-*` 48..192) | 2 build | **6** | **1** | — | — |
| **W1** | `art/w1-player-b/` | `PLAYER` 2.5D Redo: 25 Ships (6 anodized liveries), 13 Drones, 8 Plasma Bullets/Beams, 2 FX | **48 / 48** | **48** | **48** | `preview/w1b_contact_sheet.png` | `art/w1-player-b/preview/w1b_side_by_side_ref.png` |
| **W2** | `art/w2-enemy-b/` | `ENEMY` 2.5D Redo: 23 Invader Hulls (`E-BODY`) + 11 Glowing Hazard Munitions (`E-BULLET`) | **34 / 34** | **34** | **34** | `preview/w2b_contact_sheet.png` | `art/w2-enemy-b/preview/w2b_side_by_side_ref.png` |
| **W3** | `art/w3-boss-b/` | `BOSS` 2.5D Redo: 35 Symmetrical Multi-Turret Dreadnoughts (with twin detached modules) + 7 `B-PART` | **42 / 42** | **42** | **42** | `preview/w3b_contact_sheet.png` | `art/w3-boss-b/preview/w3b_side_by_side_ref.png` |
| **W4-core** | `art/w4-core-b/` | `kept_records > 0` 2.5D Redo: `BG` (10 rows / 12 files), `ITEM` (7), `FX` (9), Beveled `UI` (86) | **112 / 112** | **114** | **114** | `preview/w4b_contact_sheet.png` | `art/w4-core-b/preview/w4b_side_by_side_ref.png` |
| **W5-full** | `art/w5-full-b/` | Remaining `kept_records == 0` 2.5D Redo: 3D Spherical Planets & `BG` (+34), `ITEM` (+2), `FX` (+17), `UI` (+221) | **274 / 274** | **274** | **274** | `preview/w5b_contact_sheet.png` | `art/w5-full-b/preview/w5b_side_by_side_ref.png` |
| **TOTAL** | `art/` | **100% Non-EXCL `art-planner.csv` Parity (`EXCL` 278 = `0`) — All Redone in 2.5D Metallic** | **510 / 510** (+25 +2) | **543** | **522** | **6 contact sheets** | **6 Side-by-Side Ref Comparison Boards** |

## Extended 2.5D Metrics Summary (`STYLE-CORRECTION lần 149` + §4.9)

| Wave | Files | `gradient_stops` (`≥3–5`) | `outline_dark_px` (`≤1.0`) | `detail_density` | `lum_contrast` (`0.45–0.80`) | `val` | `chroma` | `colors_q32` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **W1 (`PLAYER`)** | 48 | **8.44** | **0.000 px** | **68.59** | **0.617** | 0.845 | 0.482 | 1804.5 |
| **W2 (`ENEMY`)** | 34 | **10.50** | **0.000 px** | **70.70** | **0.715** | 0.784 | 0.419 | 912.3 |
| **W3 (`BOSS`)** | 42 | **10.62** | **0.000 px** | **38.22** | **0.694** | 0.782 | 0.471 | 3453.8 |
| **W4-core** | 114 | **6.37** | **0.004 px** | **20.72** | **0.485** | 0.799 | 0.547 | 556.4 |
| **W5-full** | 274 | **6.65** | **0.002 px** | **22.88** | **0.527** | 0.787 | 0.563 | 407.5 |
| **ALL (`W1..W5`)** | **512** | **7.34** | **0.002 px** | **31.12** | **0.552** | **0.794** | **0.535** | **855.0** |

## Curator Integration Notes (`Art-curator`)
1. **O(1) Row Lookup:** Open `art/variant_b_full_510_registry.csv` (keyed by `row_id`) to resolve `sprite_path`, `master_path`, `delivered_px`, `recipe`, §4.9 RGBA metrics, and Extended 2.5D metrics (`gradient_stops`, `outline_dark_px`, `detail_density`, `lum_contrast`).
2. **Straight-RGBA & 9-Slice Ready:** All non-full-bleed sprites enforce straight-RGBA premultiplied downsampling with `alpha=0` at all 4 corners and zero dark cartoon outlines. All `U-HUD` / `U-KIT` / `U-META` / `U-SHOP` / `G-UI` frames preserve uniform-color middle stretch zones per `docs/spec/ASSETS.md` §5.
3. **Immutable W0 Contract Preserved:** Verify via `art/w0-listing-b/` — exact 25 store-listing files from commit `5510180d` remain 100% intact (`git diff 5510180d -- art/w0-listing-b/microsoft-store art/w0-listing-b/amazon-appstore art/w0-listing-b/huawei` is empty); only `preview/w0b_side_by_side_ref.png` was added under `preview/`.
