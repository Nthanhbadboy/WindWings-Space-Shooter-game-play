# W4 FX + ITEM — Manifest / Handoff

- Lot: **FX lane (26) + ITEM lane (9)** per `art-planner.csv` @ `971a7eea8` — ITEM is the wave-W3 remainder (I-DROP ships with BOSS in the plan's W3), FX spans planner waves W2 (F-BOOM/F-ENEMY) and W4 (F-GLOW). Combined into one 35-unit lot, declared in advance.
- Branch: `arena/5438fec9-windwings-space-shooter-game-p` · Base (W3 tip): `7dce12dd586501b08c071ffd90c6c3efbc5f0694`.
- Declared on PR #12: PROGRESS `6445906802`. Builder: `build_w4.py` (deterministic, seeded). Metrics: `w4_units.csv` / `w4_units.json`. Previews: `preview/`.
- All-new filenames; no original asset traced/copied.

## 1. Unit mapping (planner → delivered)

ITEM @128×128 recipe `item` · FX @256×256 (AP-0088 @128) recipe `fx`. Total sprites 656 KB.

| Row | Batch | Planner base | File | Bytes |
|---|---|---|---|---:|
| AP-0130 | I-DROP | `05_0` | `item_cellamber_128@gold.png` | 9529 |
| AP-0131 | I-DROP | `05_1` | `item_cellround_128@gold.png` | 17207 |
| AP-0132 | I-DROP | `5_1` | `item_crate_128@gold.png` | 11158 |
| AP-0133 | I-DROP | `bag` | `item_lootbag_128@gold.png` | 12541 |
| AP-0134 | I-DROP | `banana` | `item_banana_128@gold.png` | 9042 |
| AP-0135 | I-DROP | `foot` | `item_landingfoot_128@gold.png` | 10685 |
| AP-0136 | I-DROP | `fullpower` | `item_fullpower_128@gold.png` | 8359 |
| AP-0137 | I-DROP | `head` | `item_bosshead_128@gold.png` | 9318 |
| AP-0138 | I-DROP | `rock` | `item_orechunk_128@gold.png` | 14783 |
| AP-0082 | F-BOOM | `bomb` | `fx_bombburst_256@paper.png` | 20626 |
| AP-0083 | F-BOOM | `boom` | `fx_boom_256@paper.png` | 37019 |
| AP-0084 | F-BOOM | `crossfire` | `fx_crossfire_256@paper.png` | 21260 |
| AP-0085 | F-BOOM | `newdevice` | `fx_newdevice_256@paper.png` | 29188 |
| AP-0086 | F-BOOM | `saw` | `fx_sawflash_256@paper.png` | 28983 |
| AP-0088 | F-ENEMY | `fxenemy` | `fx_enemyhit_128@paper.png` | 7108 |
| AP-0140 | F-GLOW | `beemap` | `fx_beemap_256@paper.png` | 25596 |
| AP-0141 | F-GLOW | `blackhold` | `fx_blackhole_256@paper.png` | 37984 |
| AP-0142 | F-GLOW | `circle_blue` | `fx_haloring_256@paper.png` | 27109 |
| AP-0143 | F-GLOW | `circle_blue copy` | `fx_haloring2_256@paper.png` | 36137 |
| AP-0144 | F-GLOW | `circle_mask_bigboss` | `fx_bossmask_256@paper.png` | 32205 |
| AP-0145 | F-GLOW | `fx_footbroken` | `fx_shatter_256@paper.png` | 22847 |
| AP-0146 | F-GLOW | `gate` | `fx_gate_256@paper.png` | 30802 |
| AP-0147 | F-GLOW | `gatenho` | `fx_gatesmall_256@paper.png` | 18011 |
| AP-0148 | F-GLOW | `ghost` | `fx_ghost_256@paper.png` | 16782 |
| AP-0149 | F-GLOW | `glow` | `fx_glowstreak_256@paper.png` | 9641 |
| AP-0150 | F-GLOW | `heal` | `fx_heal_256@paper.png` | 13479 |
| AP-0151 | F-GLOW | `lastboss` | `fx_lastbossmark_256@paper.png` | 14234 |
| AP-0152 | F-GLOW | `light` | `fx_lightshaft_256@paper.png` | 34062 |
| AP-0153 | F-GLOW | `overtime` | `fx_overtimebar_256@paper.png` | 3199 |
| AP-0154 | F-GLOW | `point_talent` | `fx_talentpoint_256@paper.png` | 14892 |
| AP-0155 | F-GLOW | `square64x` | `fx_squareglow_256@paper.png` | 9078 |
| AP-0156 | F-GLOW | `supperpower` | `fx_superpower_256@paper.png` | 15788 |
| AP-0157 | F-GLOW | `victory` | `fx_victorybar_256@paper.png` | 3777 |
| AP-0158 | F-GLOW | `powerup` | `fx_powerup_256@paper.png` | 23346 |
| AP-0159 | F-GLOW | `circle` | `fx_circleset_256@paper.png` | 35881 |

Overhead rows AP-0081/0087/0129/0139 (`n_units=0`) skipped as before; AP-0087 is the F-ENEMY overhead row (its batch contains only AP-0088). Box aspect per row follows planner `max_w×max_h` (note AP-0153/AP-0157 are extreme 11–13:1 banner strips inside the 256 canvas).

## 2. Method

Same deterministic pipeline, with one declared variant: **FX sprites skip the ink900 shadow, light pass, and grain** — they are light sources (recipe `fx`: paper 55 · white 30 · ink300 12 · teal 3; dark ≤0.02 forbids dark masses anyway). Each FX has a faint 2-step alpha halo (≤52/255 alpha, outside the §4.9 alpha>127 measurement set) under an opaque paper/white core. Items use the standard pipeline (supersample → light pass → seeded grain) at recipe ratios (ink300 45 · gold 25 · paper 25 · ink500 5). Pure white #FFFFFF is used for FX cores because recipe §4.5 explicitly lists “white 30”.

## 3. Gate results

- **G-A: PASS 35/35** — `fx` windows §4.3 (val 0.70–0.90 · val_std 0.15–0.25 · dark ≤0.02 · chroma ≤0.08), `item` windows (val 0.62–0.70 · val_std 0.22–0.28 · dark ≤0.05 · chroma 0.25–0.30), ≤1 metric out. Outs: val_std×6, val×5, chroma×1. `colors_q32` reported only: FX 19–78 (§4.3 indicative 3–10 not met — AA edges of flat shapes at 256; reaching ≤10 colors would require indexed/no-AA exports), items 182–302 (grain-carried, as W1–W3). Independent file check: 35/35 RGBA exact px, transparent corners, bytes match CSV, planner coverage exact. STATIC_CONFIRMED.
- **G-B:** `preview/w4_items_silhouettes_64.png` — 9 items distinct at 64 px (closest pair cellamber/fullpower, both battery bottles; separated in color by window+bolt vs 3 charge bars). FX silhouettes are not meaningful (additive glows) — read test done via contact sheet on ink background instead.
- **G-F:** `preview/w4_battle_mock_720x1280.png` — W3 boss under boom/shatter, item drops, heal/powerup glows at the W1 player. Concept layout, RUNTIME_UNVERIFIED.
- G-C not run (no runtime harness). G-D N/A (no destructible-block rule in this lane).

## 4. Declared deviations & limits

1. **All 35 `n_units` delivered**, incl. the many F-GLOW/B-PART-style rows with scope-B `kept_records=0` — declared in PROGRESS `6445906802`.
2. **Name interpretations (INFERRED)** — planner bases are terse; designs read the name + rule_hint: `blackhold` = bright accretion ring with a **transparent** center (a solid black disc would violate dark ≤0.02); `circle_blue` only faintly teal-tinted because recipe `fx` is near-achromatic (chroma ≤0.08); `overtime`/`victory` drawn as blank glowing banner strips **without text** (lettering belongs to UI/font and would risk copying original labels); `beemap` = honeycomb glow cluster; `lastboss` = crown mark; `banana` = stylized crescent cell (literal banana curve, ink/gold materials); `head`/`foot` per hint R23 are detached mech parts (helmet / landing foot), consistent with the plan's note that `head` records are boss parts; numeric bases `05_0`, `05_1`, `5_1` = generic energy cells/crate (no semantic hint available).
3. **Static single-frame FX** — no animation frames/sequences in planner units; motion (scale/fade/rotate, additive flash) is engine-side. Several designs (`boom`, `sawflash`, `lightshaft`, `haloring2`) are rotationally symmetric so code can spin/fade them freely.
4. **Halo blending**: with normal alpha blending over dark backgrounds the halos read as soft grey discs (visible in previews); recommend **additive (ADD) blend** for `sprites/fx/**` in Godot so they read as light. RUNTIME_UNVERIFIED.
5. `fx_circleset` is a 3×3 mini-atlas in one 256 canvas (per planner hint “≥8 mảnh trong ≤256px — bộ icon ghép”); slice into 85⅓-px cells region-wise if individual icons are needed, or request a split in a later lot.
6. Items: center pivot assumed; drop/pickup radius not embedded — awaits `sprite_mesh_contract` (unchanged).

## 5. Godot import notes

- POT RGBA (128² items, 256²/128² FX), transparent corners. Filter Linear; mipmaps optional for FX (often scaled up), on for items.
- FX: set material blend mode to **Add** (CanvasItemMaterial) for proper glow; the opaque white cores are authored to bloom under additive. `fx_blackhole` center is transparent by design — with ADD it will simply not brighten the middle.
- `overtimebar`/`victorybar` are authored content-thin inside square canvases (planner aspect); use region rects or non-uniform scale for banner backdrops.
