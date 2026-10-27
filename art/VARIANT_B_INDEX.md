# Variant B Master Art Suite Index — "Solar Neon Arcade-Pop"

- **Role / Author Branch**: `Art-designer-B` · `arena/eca8588b-windwings-space-shooter-game-p`
- **Visual Direction**: **Solar Neon Arcade-Pop** — bright sunlit cerulean/cyan skies (`#1677FF`/`#00E5FF`), pearl-white & electric cobalt-azure player hulls (`#E2EEFF`/`#186CF2`) with solar-gold/tangerine/cyan/emerald energy accents, hyper-crimson/violet/magenta/amber enemy & boss armadas, crisp `#08143E` / `#14062E` cel outlines, and 30° top-left directional specular facets.
- **Style Independence**: 100% independent of Variant A (`arena/5438fec9-windwings-space-shooter-game-p`, dark "Ink & Ember"), while aligned 1:1 on planner row IDs, slot dimensions, straight-alpha RGBA rules, and `ASSETS.md` §5 9-slice insets so `Art-curator` can select A, select B, or merge slot-by-slot from `masters/`.
- **License Metadata (all 263 exported slots)**: `chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)`
- **Originality Compliance**: 100% newly created digital 2D art + procedural cel-shaded vector/raster pipelines; **0** original APK/GCenter PNGs, atlases, or brand logos used; **`EXCL` (278 units: `X-BRAND`, `X-PART`, `X-TRIAGE`) = 0** per `ART_REDRAW_PLAN.md`.

---

## Wave Delivery Rollup (263 Exported Deliverables + 247 Masters)

| Wave | Directory | Scope & Planner Mapping | Exported PNGs | Masters Preserved | Manifest & Machine Registry | Preview Contact Sheet |
|---|---|---|---:|---:|---|---|
| **W0 — Store Listing** | `art/w0-listing-b/` | Microsoft Store (11) + Amazon Appstore (7) + Huawei AppGallery (7) | **25** | **9** (`masters/`) | [`W0B_MANIFEST.md`](w0-listing-b/W0B_MANIFEST.md) · [`w0b_exports.json`](w0-listing-b/w0b_exports.json) | [`w0_contact_sheet.png`](w0-listing-b/preview/w0_contact_sheet.png) |
| **W1 — PLAYER** | `art/w1-player-b/` | `P-SHIP` ×25 (`256²`), `P-DRONE` ×13 (`128²`), `P-BULLET` ×8 (`32²` & `32×512` tile), `P-FX` ×2 (`128²`) | **48** | **48** (`masters/`) | [`W1B_MANIFEST.md`](w1-player-b/W1B_MANIFEST.md) · [`w1b_units.json`](w1-player-b/w1b_units.json) · [`w1b_units.csv`](w1-player-b/w1b_units.csv) | [`w1b_contact_sheet.png`](w1-player-b/preview/w1b_contact_sheet.png) |
| **W2 — ENEMY** | `art/w2-enemy-b/` | `E-BODY` ×23 (`128²`, `AP-0046..0068`), `E-BULLET` ×11 (`64²`, `AP-0070..0080`) | **34** | **34** (`masters/`) | [`W2B_MANIFEST.md`](w2-enemy-b/W2B_MANIFEST.md) · [`w2b_units.json`](w2-enemy-b/w2b_units.json) · [`w2b_units.csv`](w2-enemy-b/w2b_units.csv) | [`w2b_contact_sheet.png`](w2-enemy-b/preview/w2b_contact_sheet.png) |
| **W3 — BOSS** | `art/w3-boss-b/` | `B-BODY` ×35 (`512²` asymmetric + ≥1 destructible satellite, `AP-0117..0120`), `B-PART` ×7 (`256²`, `AP-0122..0128`) | **42** | **42** (`masters/`) | [`W3B_MANIFEST.md`](w3-boss-b/W3B_MANIFEST.md) · [`w3b_units.json`](w3-boss-b/w3b_units.json) · [`w3b_units.csv`](w3-boss-b/w3b_units.csv) | [`w3b_contact_sheet.png`](w3-boss-b/preview/w3b_contact_sheet.png) |
| **W4-core — BG / ITEM / FX / UI** | `art/w4-core-b/` | `BG` ×12 (3 seamless `1024²` parallax + 9 `G-UI` `512²`), `ITEM` ×7 (`128²`), `FX` ×9 (`256²`), `UI` ×86 (`64²`/`256²` 9-slice) | **114** | **114** (`masters/`) | [`W4B_MANIFEST.md`](w4-core-b/W4B_MANIFEST.md) · [`w4b_units.json`](w4-core-b/w4b_units.json) · [`w4b_units.csv`](w4-core-b/w4b_units.csv) | [`w4b_contact_sheet.png`](w4-core-b/preview/w4b_contact_sheet.png) |
| **TOTAL** | `art/` | Complete Variant B Suite (`EXCL 278 = 0`) | **263** | **247** | 5 Markdown manifests + 5 JSON + 4 CSV registries | 5 full contact sheets |

---

## Technical Verification Checklist (All Waves)

- **Straight-Alpha RGBA (`premultiplied=off`)**: Verified across all in-game sprites (`W1` 48 + `W2` 34 + `W3` 42 + `W4` 113 non-sky sprites) via premultiplied-Lanczos-then-unpremultiplied downsampling; all 4 extreme corner pixels `alpha == 0` with zero dark/white halo fringe.
- **Seamless Vertical Tiling**:
  - `art/w1-player-b/sprites/bullets/player_bullet_beam_32x512@cyan.png` & `player_bullet_beamheavy_32x512@solar.png`: exact 64px vertical period (`row[0] == row[64]`).
  - `art/w4-core-b/sprites/bg/bg_parallax_01..03_*_1024@*.png`: exact 1024px vertical wrap (`row[0] == row[1023]`).
- **9-Slice Geometry (`ASSETS.md` §5)**: All 9-slice panels, buttons, cells, sliders, boss HP bars, tabs, and rank frames maintain uniform constant-thickness borders along their middle stretch spans.
- **Protected Paths Untouched**: Zero modifications to `docs/spec/`, `datas/`, `tools/`, `tests/`, or `reverse-engineering/`.
