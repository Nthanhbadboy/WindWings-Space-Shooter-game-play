# Variant B — Solar Neon Commercial 2.5D Metallic · Audit Response Index

- **Role / Branch:** `Art-designer-B` · `arena/eca8588b-windwings-space-shooter-game-p`
- **Audit Target:** Commit `a71412d3427e3c2d9d01ee519a154be289091923` (`docs/art-audit/AUDIT_A_B_STYLES.md`) + Planner `100cfcebc3` + Reviewer follow-up `6449881162` + Director `lần 157–158` (`NGUYÊN MẪU LÀ THƯỚC` & `P0 HERO-FIRST`).
- **Palette Identity:** Bright **Solar Neon** commercial 2.5D metallic (pearl-titanium, cobalt-azure, anodized solar-gold, emerald, crimson & cyan accents over grounded dark-cobalt stage backgrounds — strictly independent of Variant A's dark *Ink & Ember*).
- **License / Author:** `chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)` · `arena/eca8588b-windwings-space-shooter-game-p` in all manifests.
- **Approval State:** **Not self-approved.** `[STATIC_CONFIRMED]` inventory, metrics, and visual comparison boards are submitted for `Art-style-auditor` Layer-1 + Layer-2 review; engine integration remains `[RUNTIME_UNVERIFIED]`.

## 1. Deliverables & Review Evidence

| Area | Current Delivery | Review Boards & Evidence |
|---|---|---|
| **W0 Store Listing** | `art/w0-listing-b/` · **25/25** immutable filenames, dimensions & RGB/RGBA modes; `S1–S4` rebuilt from current painted Variant-B sprites on grounded orbital/planetary stages (`720×1280` `p95−p05 = 0.570–0.592`, `detail = 14.0–20.1`) | `preview/w0_contact_sheet.png` · `audit_a71412d_response/comparisons/05_w0_concept_hierarchy.png` · **`S1–S4` are CONCEPT composites `[RUNTIME_UNVERIFIED]`, not runtime captures** |
| **W0 Build Icons** | `art/w0-build-icons-b/` · Windows multi-res `.ico` + Android `mipmap-*` matching Hero Candidate `Ship 10001` | `BUILD_ICONS_MANIFEST.md` (`[STATIC_CONFIRMED]`) |
| **W1 PLAYER** | `art/w1-player-b/` · **48/48** (`25` ships, `13` drones, `8` bullets, `2` FX; `48/48` unique SHA-256s); **11 painted 1024px masters** (`8` ships + `3` drones) + modular 2.5D painted kitbashing across entire fleet (`kitbash25d.py`) | `preview/w1b_side_by_side_ref.png` · `audit_a71412d_response/comparisons/01_hero_calibration.png` · `hero_probe/hero_64px_probe.png` |
| **W2 ENEMY** | `art/w2-enemy-b/` · **34/34** (`22` dedicated enemy hulls built strictly from **4 dedicated painted enemy masters** — zero player/boss reuse — + `AP-0067 Enemy_Hp` UI strip + `11` projectiles; zero `sactx` packed-atlas ref tiles) | `preview/w2b_side_by_side_ref.png` · `audit_a71412d_response/comparisons/03_enemy_anchors.png` |
| **W3 BOSS** | `art/w3-boss-b/` · **42/42** (`35` boss bodies + `7` modular `B-PART` turrets/claws/web built from **7 painted boss dreadnought masters**; exact `sprites-index.csv` decoded tile mapping `7001..9018` with zero blank ref boxes) | `preview/w3b_side_by_side_ref.png` · `audit_a71412d_response/comparisons/02_boss_decoded_ids.png` |
| **W4 CORE** | `art/w4-core-b/` · **114 files / 112 rows**; grounded dark-cobalt `sky_far`; 9-slice static 3-size verification | `preview/w4b_side_by_side_ref.png` · `audit_a71412d_response/nine_slice_contract.csv` |
| **W5 FULL** | `art/w5-full-b/` · **274/274**; upgraded 2.5D `ShopIcon` (`2871`), `nennutevent` (`2943`), zero-clip `Blink` (`2895`), 6-coin `Goicoin1` (`3045`), `CoinIcon`, tech nodes, and `outline_px = 0.00` stage/planet fixes | `preview/w5b_side_by_side_ref.png` · `audit_a71412d_response/comparisons/04_w5_semantics.png` |
| **TOTAL** | **510/510 non-EXCL planner units (`100%`)**, **512 exported sprites**, **22 painted 1024px masters**, `EXCL` drawn = `0` | `audit_a71412d_response/static_validation.{json,md}` · **`0` errors / `0` warnings** · **`512/512` `outline_px ≤ 1.00 px`** |

## 2. Current Variant-B Extended Proxy Summary (`VARIANT_B_METRICS.md`)

Synced directly from `measure_variant_b.py` on final PNGs (distinct from unmodified planner 50-bin metrics in §3 below):

| Wave | Files | `gradient_stops` (16-bin) | `outline_dark_px` | `detail_density` | `lum_contrast` | `val` | `chroma` | `colors_q32` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **W1 PLAYER** | 48 | 11.44 | 0.044 px | 119.41 | 0.676 | 0.677 | 0.300 | 2675.6 |
| **W2 ENEMY** | 34 | 12.47 | 0.003 px | 115.28 | 0.642 | 0.593 | 0.258 | 1218.7 |
| **W3 BOSS** | 42 | 13.69 | 0.101 px | 105.06 | 0.694 | 0.529 | 0.254 | 6485.7 |
| **W4 CORE** | 114 | 5.81 | 0.004 px | 20.94 | 0.517 | 0.773 | 0.536 | 598.9 |
| **W5 FULL** | 274 | 6.54 | 0.004 px | 23.97 | 0.547 | 0.759 | 0.538 | 459.4 |
| **ALL (`W1..W5`)** | **512** | **7.81** | **0.015 px** | **44.96** | **0.571** | **0.725** | **0.474** | **1243.0** |

## 3. Unmodified Planner Raw Evidence (`art/audit_a71412d_response/planner_raw_metrics.csv`)

- Measured with **unmodified** `docs/art-plan/measure_asset.py` (`100cfcebc3`, SHA-256 `c33182347dabf7e1eba4a3278d298a62a89a43ccbc2ae75e3ba0d6181a22b053`): **`512/512` PNGs read, `0` errors, `512/512` (`100%`) have `outline_px ≤ 1.00 px` (`max = 0.67 px`, `outline_gt_1 = 0`)**.
- Empirical benchmark on original WindWings prototype sprites (`ships-01 #1,#4,#8`, `bosses-01 #2,#3`) gives `grad_stops = 33–43`, `detail = 0.700–0.876`, `outline_px = 0.06–0.23`; Variant B's painted combat classes (`grad_stops = 37.69–41.36`, `detail = 0.790–0.921`, `outline_px = 0.000–0.134`) align with the original commercial prototype without posterization or blur gaming (`[STATIC_CONFIRMED]`; synthetic caps `grad_stops ≤ 25` / `detail ≤ 0.30` and Ink-&-Ember `BANDS` are documented as `[CONFLICTING]`).
- Full details, shared-SHA UI frame table (`41` groups / `99` extra files), 9-slice probe (`9/9 STATIC_OK`), and `[RUNTIME_UNVERIFIED]` items are documented in `art/audit_a71412d_response/README.md`.
