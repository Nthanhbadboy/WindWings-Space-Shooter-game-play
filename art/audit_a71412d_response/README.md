# Response to Independent Audit `a71412d3427e3c2d9d01ee519a154be289091923`

**Role:** `Art-designer-B` · **Branch:** `arena/eca8588b-windwings-space-shooter-game-p` · **Date:** 2026-10-28  
**Approval status:** `[STATIC_CONFIRMED]` technical/file/metric evidence + full commercial 2.5D art overhaul submitted for review; **NOT self-approved** (Art-style-auditor Layer-1 + Layer-2 verdict & P0 hero lock pending; `[RUNTIME_UNVERIFIED]` on Godot engine integration).

---

## 1. Summary of Audit Compliance (`AUDIT_A_B_STYLES.md` §1–§7 + `6449881162`)

Protected paths (`docs/spec/`, `datas/`, `tools/`) are **100% untouched** (`[STATIC_CONFIRMED]`). Every Wave (`W0..W5`) and every Markdown manifest was regenerated **last** from the final PNGs on disk so zero byte/SHA-256 drift exists.

| Audit / Reviewer Finding | Root Cause Fixed in Variant B | Verifiable Evidence & Honest Status |
|---|---|---|
| **P0 Hero-First & Fleet Consistency (`§3, §6`)** | Submitted unlocked Hero Candidate `Ship 10001` (`player_ship_01_256@solar.png`, matched 1:1 with `W0` app icon & `w0-build-icons-b`). Built **22 dedicated `1024×1024` commercial 2.5D painted masters** (`8` ships, `3` drones, `4` dedicated enemies, `7` bosses) and rebuilt **all 25 ships + 13 drones** via modular 2.5D painted kitbashing (`art/kitbash25d.py`) — eliminating all flat/toy procedural hulls. | `comparisons/01_hero_calibration.png` (11 pairs), `hero_probe/hero_64px_probe.png`, `hero_probe/hero_panel_metrics.csv`, `w1b_side_by_side_ref.png`. `[STATIC_CONFIRMED]`; hero lock awaits Art-style-auditor. |
| **W0 Concept Hierarchy & Store Contract (`§2.3, §3`)** | Retained exact **25/25** W0 filenames, pixel dimensions & color modes (`w0_contract_check.json`). Rebuilt `S1–S4` with grounded cosmos (`p05 ~ 0.05`), 3D celestial bodies, orbital dock flank girders, sunlit lower cloud banks, painted enemy formations, `Enemy_Hp` gauges, and HUD safe margins: `720×1280` frames measure **`p95−p05 = 0.570–0.592`**, **`accent = 0.025–0.039`**, **`detail-gradient = 14.0–20.1`** (inside empirical prototype band). | `comparisons/05_w0_concept_hierarchy.png`, `w0_frame_metrics.csv`, `W0B_MANIFEST.md`. **`S1–S4` are CONCEPT composites `[RUNTIME_UNVERIFIED]`, NOT Godot runtime screenshots; recapture from playable build before store submission.** |
| **W2 Enemy Role Separation & `AP-0067` (`§3, §5`)** | Eliminated cross-role reuse of Player `drone_04` / Bosses and eliminated plastic red-pentagon hulls. Built **all 22 enemy hulls** strictly from **4 dedicated painted Enemy Invader masters** (`enemy_painted_{orb,raider,mech,saucer}_1024.png`). Removed `sactx` packed Texture2D tiles (`#28..#31`) from `w2b_side_by_side_ref.png`. `AP-0067` (`Enemy_Hp`, path `2554`) is a neutral white rounded UI HP fill measured as `ui`. | `comparisons/03_enemy_anchors.png`, `w2b_side_by_side_ref.png`, `w2b_units.{csv,json}`. `[STATIC_CONFIRMED]` on `AP-0067`; other enemy pairings without decoded wave tables are visual role analogues `[INFERRED]`. |
| **W3 Decoded Boss Anchors & Modular Parts (`§2.2, §3`)** | Mapped `GLYPH-boss-ID` via exact `datas/bosses.json` + `docs/assets/sprites-index.csv` lookup (`7001..7006 → #2..#7`, `7009..7017 → #8..#16`, `9002..9015 → #17..#30`, `9017 → #31`, `9018 → #32` — zero blank boxes). Rebuilt **all 35 boss bodies + all 7 `B-PART` modular parts** from 7 painted boss dreadnought masters. | `comparisons/02_boss_decoded_ids.png` (7 pairs), `w3b_side_by_side_ref.png` (42/42). Runtime Spine/destructible-part detachment & pivots remain `[RUNTIME_UNVERIFIED]`. |
| **W4/W5 Semantics, `outline_px ≤ 1.0`, & Shared-SHA Inventory (`§3, §4, §5`)** | Upgraded `ShopIcon` (`2871` 2.5D angled crimson cart), `nennutevent` (`2943` glowing neon holo-event frame), `Blink` (`2895` zero-edge-clip horizontal anamorphic streak), `Goicoin1` (`3045` 6-coin stacked gold bullion pile), `CoinIcon`, and tech nodes (`11_5`, `22_1`). Fixed the 3 BG edge-darkness outliers (`bg_ap_0102`, `bg_ap_0103`, `bg_ap_0109`) so **`512/512` sprites have `outline_px ≤ 1.00 px` (`0` outliers)**. | `comparisons/04_w5_semantics.png`, `planner_raw_metrics.csv`, `static_validation.{json,md}`, `nine_slice_contract.csv`. |
| **Manifest Sync (`6449881162`)** | `refresh_manifest_docs.py` computes live byte size and `sha256[:16]` directly from on-disk PNGs after all builds finish; `VARIANT_B_INDEX.md` and `VARIANT_B_METRICS.md` synced to current CSVs. | `W0B_MANIFEST.md`, `W1B..W5B_MANIFEST.md`, `VARIANT_B_INDEX.md`, `VARIANT_B_METRICS.md` (`[STATIC_CONFIRMED]`). |

---

## 2. Static Acceptance Verification (`[STATIC_CONFIRMED]`)

```bash
python3 -B art/audit_a71412d_response/validate_static.py --root . --out art/audit_a71412d_response
```

- **Sprite records:** `512 / 512` across `W1..W5` (`413` unique SHA-256 hashes; `100%` unique across all `W1` 48/48, `W2` 34/34, `W3` 42/42, `ITEM` 9/9, and `FX` 28/28).
- **Planner coverage:** `510 / 510` non-EXCL units (`100.0%`); `EXCL` drawn = `0`.
- **W0 contract:** `25 / 25` exact filenames, pixel dimensions, and RGB/RGBA modes (`w0_contract_check.json`: `all_25_filename_px_mode_match = true`).
- **Validator status:** **`0` errors, `0` warnings**, straight-RGBA `alpha == 0` corners verified on all non-full-bleed sprites.
- **9-slice static probe (`nine_slice_contract.csv`):** `AP-0273`, `AP-0352`, `AP-0353` tested at `320×240`, `480×360`, and `720×1080` (`9/9 STATIC_OK`, corners exact, center RGB std `0.0`). Static image probe only; Godot `NinePatchRect` integration remains `[RUNTIME_UNVERIFIED]`.

### Functional Inventory of Shared-SHA Reuse (`41` groups / `99` extra files in W4/W5 UI & BG)

Zero gameplay combat sprites (`P-SHIP`, `P-DRONE`, `P-BULLET`, `E-BODY`, `E-BULLET`, `B-BODY`, `B-PART`, `I-DROP`, `F-BOOM/ENEMY/GLOW`) share hashes. All 41 shared-SHA groups are intentional reusable 9-slice UI frames, HUD backing plates, or generic timer/socket rings:

| Shared-SHA Family | Groups / Extra Files | Representative Planner Slots | Functional Rationale (`[INFERRED]` until Godot UI binding) |
|---|---:|---|---|
| **9-Slice Beveled Modal & Avatar Frames (`U-KIT` / `U-META`)** | 12 groups / 43 extras | `AP-0274 kit_border_player`, `AP-0352 meta_frame_base`, `AP-0353 meta_frame_avatar` | Shared chrome/cobalt 9-slice container borders resized dynamically by UI layout. |
| **HUD Plates, Ribbons & Tab Backings (`U-HUD` / `U-KIT` / `G-UI`)** | 9 groups / 20 extras | `AP-0028 hud_score_plate`, `AP-0036 hud_info_header_tab`, `AP-0168 panel_bg_player` | Uniform HUD header/tab chrome where text/icons are overlaid at runtime. |
| **Generic Socket Rings, Duration Halos & Shop Badges (`U-ICON` / `U-SHOP`)** | 18 groups / 34 extras | `AP-0218 icon_ring`, `AP-0231 icon_timeicon`, `AP-0424 shop_iconfree` | Standardized cooldown rings, support sockets, and free-pass tier cells. |
| **Seamless Stage Sky Base (`G-PARALLAX`)** | 2 groups / 2 extras | `bgnormal` / `nen` seamless cobalt stage sky | Identical base stage sky scroll tile referenced under two legacy aliases. |

---

## 3. Unmodified Planner Raw Metrics vs Empirical Original Prototype (`§4`)

Measured with **unmodified** `docs/art-plan/measure_asset.py` (`100cfcebc3`, SHA-256 `c33182347dabf7e1eba4a3278d298a62a89a43ccbc2ae75e3ba0d6181a22b053`) across all `512` PNGs (`planner_raw_metrics.csv`, `0` read errors).

### 3.1 Empirical Calibration Check (`NGUYÊN MẪU LÀ THƯỚC` — `[CONFLICTING]` Synthetic Bands Documented)

Per `AUDIT_A_B_STYLES.md` §4, we measured the **original WindWings commercial prototype sprites** (`ships-01 #1, #4, #8`, `bosses-01 #2, #3`) with the exact same unmodified `measure_asset.py`:
- **Original WindWings Prototype (`[STATIC_CONFIRMED]`):** `grad_stops = 33–43`, `outline_px = 0.06–0.23`, `detail = 0.700–0.876`, `val = 0.430–0.541`, `val_std = 0.187–0.256`, `dark = 0.010–0.069`, `chroma = 0.211–0.303`.
- Because real commercial 2.5D curved-metallic sprites naturally span `33–43` luminance bins (out of 50) and `0.70–0.88` surface gradient detail, the synthetic `STYLE_BANDS` caps (`grad_stops ≤ 25`, `detail ≤ 0.30`) are **`[CONFLICTING]`** with the original prototype itself. Per `AUDIT_A_B_STYLES.md` §4, we **refused to posterize, quantize, or blur** our painted 2.5D masters to game those synthetic numbers, and instead matched the empirical prototype distribution while enforcing **`outline_px ≤ 1.00 px` on `512/512` (`100%`)** of Variant B sprites (`outline_gt_1 = 0`).

### 3.2 Full 512-File Raw Class Summary (`planner_raw_metrics.csv`)

| Class | Files | Mean `grad_stops` | Mean `outline_px` | Max `outline_px` | Mean `detail` | Mean `val` | Mean `val_std` | Mean `dark` | Mean `chroma` | `outline_px ≤ 1.0` | Synthetic 3-Band Match |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ship` | 25 | 41.36 | 0.134 | 0.62 | 0.853 | 0.608 | 0.241 | 0.033 | 0.221 | **25/25** | 0/25 (`[CONFLICTING]` vs prototype `33–43`) |
| `drone` | 13 | 37.69 | 0.000 | 0.00 | 0.921 | 0.618 | 0.210 | 0.002 | 0.238 | **13/13** | 0/13 (`[CONFLICTING]` vs prototype) |
| `enemy` (`AP-0067` as `ui`) | 22 | 38.50 | 0.000 | 0.00 | 0.874 | 0.544 | 0.209 | 0.001 | 0.234 | **22/22** | 0/22 (`[CONFLICTING]` vs prototype) |
| `boss` | 42 | 39.33 | 0.103 | 0.67 | 0.790 | 0.529 | 0.225 | 0.058 | 0.254 | **42/42** | 0/42 (`[CONFLICTING]` vs prototype `33–43`) |
| `bullet` | 19 | 26.26 | 0.000 | 0.00 | 0.624 | 0.766 | 0.151 | 0.004 | 0.432 | **19/19** | 0/19 |
| `fx` | 28 | 10.21 | 0.000 | 0.00 | 0.058 | 0.931 | 0.067 | 0.000 | 0.629 | **28/28** | 2/28 |
| `item` | 9 | 21.22 | 0.000 | 0.00 | 0.363 | 0.842 | 0.128 | 0.000 | 0.443 | **9/9** | 0/9 |
| `bg` | 28 | 22.75 | 0.001 | 0.03 | 0.057 | 0.728 | 0.143 | 0.003 | 0.423 | **28/28** | 12/28 |
| `ui` (incl. `AP-0067`) | 326 | 15.58 | 0.006 | 0.58 | 0.175 | 0.752 | 0.164 | 0.001 | 0.541 | **326/326** | 105/326 |
| **TOTAL** | **512** | — | — | **0.67** | — | — | — | — | — | **512/512 (`100%`)** | **119/512** |

---

## 4. W0 Gameplay Concept Hierarchy (`tools/design-metrics.py` SHA `77bb6a91…`)

Measured on the 4 original phone gameplay captures (`REF`) vs current Variant B `S1–S4` **CONCEPT** stills (`[RUNTIME_UNVERIFIED]`):

| Scene | `REF` `p95−p05` | `B` `720×1280` `p95−p05` | `B` `450×800` `p95−p05` | `REF` `accent` | `B` `720×1280` `accent` | `REF` `detail` | `B` `720×1280` `detail` |
|---|---:|---:|---:|---:|---:|---:|---:|
| **S1 / Wave Formation** | 0.6674 | **0.592** | **0.5966** | 0.0510 | **0.027** | 20.81 | **19.0** |
| **S2 / Boss Siege (`7001`)** | 0.5282 | **0.570** | **0.5771** | 0.0571 | **0.039** | 17.38 | **20.1** |
| **S3 / Squadron & Loot (`10008`)** | 0.6255 | **0.570** | **0.5730** | 0.0540 | **0.025** | 20.98 | **14.0** |
| **S4 / Overdrive Beam (`7006`)** | 0.5107 | **0.589** | **0.5966** | 0.0247 | **0.027** | 13.26 | **16.0** |

All four `720×1280` and `800×1280` concept screenshots sit inside the empirical original capture range (`p95−p05 ∈ [0.511, 0.667]`, `accent ∈ [0.0247, 0.0571]`, `detail ∈ [13.26, 20.98]`). They remain **CONCEPT composites (`[RUNTIME_UNVERIFIED]`)**, not Godot captures.

---

## 5. Reproducible Verification Commands

```bash
# 1. Comparison boards (31 indexed pairs with source sheet, tile, crop xyxy & SHA-256)
python3 -B art/audit_a71412d_response/build_comparisons.py \
  --spec-root /tmp/ww_tools --root . --out art/audit_a71412d_response/comparisons

# 2. P0 Hero 64px readability + per-region planner probe
python3 -B art/audit_a71412d_response/hero_probe.py \
  --spec-root /tmp/ww_tools --planner /tmp/ww_tools/docs/art-plan/measure_asset.py \
  --out art/audit_a71412d_response/hero_probe

# 3. Unmodified planner raw metrics (512/512 PNGs) + W0 frame metrics
python3 -B art/audit_a71412d_response/measure_b_with_planner.py \
  --root . --planner /tmp/ww_tools/docs/art-plan/measure_asset.py \
  --out art/audit_a71412d_response/planner_raw_metrics.csv --workers 8
python3 -B art/audit_a71412d_response/measure_w0_frames.py \
  --spec-root /tmp/ww_tools --root . --out art/audit_a71412d_response/w0_frame_metrics.csv

# 4. Static validator + live byte/SHA-256 manifest sync
python3 -B art/audit_a71412d_response/validate_static.py --root . --out art/audit_a71412d_response
python3 -B art/audit_a71412d_response/refresh_manifest_docs.py
```

---

## 6. Explicitly Open / `[RUNTIME_UNVERIFIED]` Items

1. **Art-style-auditor Layer-2 & P0 Hero Lock:** Only `Art-style-auditor` locks or rejects the hero and issues aesthetic approval.
2. **Godot Runtime Integration (`[RUNTIME_UNVERIFIED]`):** No Godot project exists on this art-only branch; 10 gameplay + 3 reward runtime captures, Spine/part pivots, 0.2s motion readability, additive VFX shaders, and `NinePatchRect` scene bindings require integration testing.
3. **3-Person Same-Game Recognition Check (`[UNKNOWN]`):** Not performed or fabricated.
4. **Store Screenshot Recapture:** `W0` `S1–S4` must be recaptured from the playable release build prior to store submission.
5. **Title / Art Rights (`USER-ONLY`):** `chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)` preserved in every manifest.
