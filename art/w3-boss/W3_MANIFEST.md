# W3 BOSS — Manifest / Handoff

- Lot: **W3 BOSS** (lane BOSS per `art-planner.csv` @ `971a7eea8`, wave W3), 42 units.
- Branch: `arena/5438fec9-windwings-space-shooter-game-p` · Base (W2 tip): `52ea16fd9b316f5c315ecedcb3996ccfec7032b5`.
- Declared on PR #12: PROGRESS `6445426633`. Builder: `build_w3.py` (deterministic, seeded). Metrics: `w3_units.csv` / `w3_units.json`. Previews: `preview/`.
- All-new filenames; no original asset traced/copied. Bosses face **down** (+Y image space). Every body carries ≥1 glowing destructible block (ember core), ≤2 sub-blocks, asymmetric accents (plan boss rules).

## 1. Unit mapping (planner → delivered)

B-BODY = 35 @512×512 · B-PART = 7 @256×256 · recipe `boss` for all. Total sprites 4,526 KB.

| Row | Planner base | Design | File | Bytes |
|---|---|---|---|---:|
| AP-0117 | `bosss` | sentinel | `boss_sentinel_512@ember.png` | 152185 |
| AP-0118 | `bossx` | warlord | `boss_warlord_512@ember.png` | 63803 |
| AP-0119 | `boss_shields` | shieldcore | `boss_shieldcore_512@ember.png` | 89785 |
| AP-0120 | `GLYPH-boss-7001` | dreadnought-v0 | `boss_dreadnought01_512@ember.png` | 130767 |
| AP-0120 | `GLYPH-boss-7002` | spider-v0 | `boss_spider01_512@ember.png` | 160892 |
| AP-0120 | `GLYPH-boss-7003` | ringfort-v0 | `boss_ringfort01_512@ember.png` | 182367 |
| AP-0120 | `GLYPH-boss-7004` | mantis-v0 | `boss_mantis01_512@ember.png` | 85578 |
| AP-0120 | `GLYPH-boss-7005` | carrier-v0 | `boss_carrier01_512@ember.png` | 111118 |
| AP-0120 | `GLYPH-boss-7006` | sawmill-v0 | `boss_sawmill01_512@ember.png` | 120796 |
| AP-0120 | `GLYPH-boss-7009` | obelisk-v0 | `boss_obelisk01_512@ember.png` | 77053 |
| AP-0120 | `GLYPH-boss-7010` | behemoth-v0 | `boss_behemoth01_512@ember.png` | 144360 |
| AP-0120 | `GLYPH-boss-7011` | dreadnought-v1 | `boss_dreadnought02_512@ember.png` | 145930 |
| AP-0120 | `GLYPH-boss-7012` | spider-v1 | `boss_spider02_512@ember.png` | 165392 |
| AP-0120 | `GLYPH-boss-7013` | ringfort-v1 | `boss_ringfort02_512@ember.png` | 160167 |
| AP-0120 | `GLYPH-boss-7014` | mantis-v1 | `boss_mantis02_512@ember.png` | 76775 |
| AP-0120 | `GLYPH-boss-7015` | carrier-v1 | `boss_carrier02_512@ember.png` | 124598 |
| AP-0120 | `GLYPH-boss-7016` | sawmill-v1 | `boss_sawmill02_512@ember.png` | 134950 |
| AP-0120 | `GLYPH-boss-7017` | obelisk-v1 | `boss_obelisk02_512@ember.png` | 68644 |
| AP-0120 | `GLYPH-boss-7018` | behemoth-v1 | `boss_behemoth02_512@ember.png` | 141922 |
| AP-0120 | `GLYPH-boss-9002` | dreadnought-v2 | `boss_dreadnought03_512@ember.png` | 120687 |
| AP-0120 | `GLYPH-boss-9003` | spider-v2 | `boss_spider03_512@ember.png` | 147312 |
| AP-0120 | `GLYPH-boss-9004` | ringfort-v2 | `boss_ringfort03_512@ember.png` | 168941 |
| AP-0120 | `GLYPH-boss-9005` | mantis-v2 | `boss_mantis03_512@ember.png` | 92257 |
| AP-0120 | `GLYPH-boss-9006` | carrier-v2 | `boss_carrier03_512@ember.png` | 100899 |
| AP-0120 | `GLYPH-boss-9007` | sawmill-v2 | `boss_sawmill03_512@ember.png` | 109980 |
| AP-0120 | `GLYPH-boss-9008` | obelisk-v2 | `boss_obelisk03_512@ember.png` | 83081 |
| AP-0120 | `GLYPH-boss-9009` | behemoth-v2 | `boss_behemoth03_512@ember.png` | 131078 |
| AP-0120 | `GLYPH-boss-9010` | dreadnought-v3 | `boss_dreadnought04_512@ember.png` | 138334 |
| AP-0120 | `GLYPH-boss-9011` | spider-v3 | `boss_spider04_512@ember.png` | 164690 |
| AP-0120 | `GLYPH-boss-9012` | ringfort-v3 | `boss_ringfort04_512@ember.png` | 172838 |
| AP-0120 | `GLYPH-boss-9013` | mantis-v3 | `boss_mantis04_512@ember.png` | 81530 |
| AP-0120 | `GLYPH-boss-9014` | carrier-v3 | `boss_carrier04_512@ember.png` | 116744 |
| AP-0120 | `GLYPH-boss-9015` | sawmill-v3 | `boss_sawmill04_512@ember.png` | 126480 |
| AP-0120 | `GLYPH-boss-9017` | obelisk-v3 | `boss_obelisk04_512@ember.png` | 72553 |
| AP-0120 | `GLYPH-boss-9018` | behemoth-v3 | `boss_behemoth04_512@ember.png` | 150119 |
| AP-0122 | `boss` | turretcore | `bosspart_turretcore_256@ember.png` | 54261 |
| AP-0123 | `boss dong ho real` | clockcore | `bosspart_clockcore_256@ember.png` | 59648 |
| AP-0124 | `boss nhen doc xanh` | venomsac | `bosspart_venomsac_256@ember.png` | 47502 |
| AP-0125 | `boss to vc ban 2 ben` | dualcannon | `bosspart_dualcannon_256@ember.png` | 23748 |
| AP-0126 | `minibosstronxoay` | rotor | `bosspart_rotor_256@ember.png` | 20575 |
| AP-0127 | `sieuhopthe tachbophan` | dockjoint | `bosspart_dockjoint_256@ember.png` | 52385 |
| AP-0128 | `web` | web | `bosspart_web_256@ember.png` | 61388 |

AP-0116 / AP-0121 are overhead rows (`n_units=0`) — nothing drawn, as in W1/W2. Glyph set = 7001–7018 excl. 7007/7008 + 9002–9018 excl. 9016 = 32 (plan §2). Box aspect per row follows planner `max_w×max_h` (singles + parts); the GLYPH row carries no max, so glyph bosses use per-family natural aspect × variant jitter — declared in PROGRESS.

## 2. Method

Same deterministic procedural pipeline as W1/W2: supersampled flat-vector draw in normalized box coords → downscale → top-left light pass → seeded grain. 8 glyph families (dreadnought, spider, ringfort, mantis, carrier, sawmill, obelisk, behemoth) × 4 parametric variants (aspect jitter, asymmetry flip, pod/core scaling) + 3 bespoke singles (crowned sentinel, X-form warlord, shield-generator) + 7 part designs read from planner base names (clock gear, venom spider sac, side-firing cannon spine, spinner rotor, combiner dock joint, web trap, generic turret core).

## 3. Gate results

- **G-A: PASS 42/42** against plan §4.3 `bosses` windows — val 0.45–0.52 · val_std 0.20–0.24 · dark ≤0.10 · chroma 0.18–0.23 — with the standing ≤1-metric-out rule. Out histogram: val_std×11, val×8, chroma×7, dark×1. `colors_q32` reported, not gated (199–381; above the §4.3 indicative 110–160 band — carried by grain + supersampled edges at 512², same disclosure as W1/W2). Independent re-check of delivered files: 42/42 RGBA exact px, transparent corners, bytes match CSV, planner coverage exact. STATIC_CONFIRMED.
- **G-B:** `preview/w3_silhouettes_128.png` — read test at 128 px (bosses are large-format assets; 64 px test from W1/W2 scaled up accordingly). 11 forms distinct; carrier/dreadnought slabs are the closest pair, separated by antenna/bow and clearly by color detail.
- **G-F:** `preview/w3_bossfight_mock_720x1280.png` — behemoth + detached parts vs W1 player; ember furnace core reads as the obvious target. Concept layout, RUNTIME_UNVERIFIED.
- G-C not run (no runtime harness in this session). G-D: boss structural rule (≥1 destructible block, ≤2 sub-blocks, asymmetry) is satisfied by construction and visible in contact sheet; in-engine destructibility wiring is code-side, RUNTIME_UNVERIFIED.

## 4. Declared deviations & limits

1. **All 42 `n_units` delivered**, incl. GLYPH scope-B kept 13/32 and B-PART kept=0 rows (except AP-0123) — declared in PROGRESS `6445426633`.
2. **Teal exception:** AP-0124 venomsac uses teal venom sacs (base name “nhện độc xanh” = green poison spider) instead of ember accents; chroma is hue-agnostic so G-A is unaffected. Declared before drawing.
3. **No phase/damage variant sprites**: planner has no per-phase units, so none were invented. Recommend runtime phase expression (tint/flash on cores, detaching B-PART sprites). The plan's W3 wave-exit (“1 boss đủ 3 phase + 2 khối phá được”, G-B/G-D) is an integration gate, not a sprite count for this lot.
4. **Parametric families** for the 32 glyph bosses (as W1 ships / W2 bodies): variants differ by proportion, asymmetry side, and sub-block layout — not 32 bespoke illustrations. This matches the plan's own cost warning (8.1 h/boss bespoke); bespoke hero-boss upgrades can replace individual files later without breaking the mapping.
5. `bosss`/`bossx` planner hint (R27, “portrait/frame”) interpreted as in-game boss bodies since the rows sit in B-BODY with recipe `boss` @512 (INFERRED; flag if portraits were intended for UI lane instead).
6. Center pivot assumed; core/part anchor points for hitboxes are not embedded — awaits `sprite_mesh_contract` (unchanged from W1/W2). Suggested destructible-block centers are the visual ember cores.
7. `val_std`/`colors_q32` partially grain-carried, as in W1/W2.

## 5. Godot import notes

- POT RGBA (512² bodies, 256² parts), transparent corners. Bosses will usually render at 0.5–1.0× → Mipmaps on, Filter Linear.
- Authored facing **down**; rotation 0 = downward. Parts are authored upright in boss-local space (barrels/mouths toward +Y) except dualcannon (barrels ±X by design — “bắn 2 bên”) and rotor (spin around center).
- Mapping back to planner rows/glyph IDs: §1 + `w3_units.csv`. Suggested boss→parts pairings for destructible setups: any glyph boss + turretcore/rotor/dockjoint as satellite blocks; spider family + venomsac/web; clockcore is self-contained (AP-0123 cluster).
