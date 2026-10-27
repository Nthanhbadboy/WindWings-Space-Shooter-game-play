# W2 ENEMY — Manifest / Handoff

- Lot: **W2 ENEMY** (lane ENEMY per `art-planner.csv` @ `971a7eea8`), 34 units.
- Branch: `arena/5438fec9-windwings-space-shooter-game-p` · Base (W1 tip): `8e6cd2f5e2b3de18ece9f28aebdb669f8a550358`.
- Declared on PR #12: PROGRESS `6444868171`. Builder: `build_w2.py` (deterministic, seeded). Metrics: `w2_units.csv` / `w2_units.json`. Previews: `preview/`.
- All-new filenames (plan § naming rule); no original asset traced/copied. Enemies face **down** (+Y image space): noses, barrels, pods and eyes point down-field.

## 1. Unit mapping (planner → delivered)

| Row | Planner base | Design | File | Delivered | Bytes |
|---|---|---|---|---|---:|
| AP-0046 | `1.` | lance-v0 | `enemy_body_lance01_128@teal.png` | 128x128 | 7294 |
| AP-0047 | `14_2` | lance-v1 | `enemy_body_lance02_128@teal.png` | 128x128 | 7149 |
| AP-0048 | `212_1` | shard-v0 | `enemy_body_shard01_128@teal.png` | 128x128 | 11796 |
| AP-0049 | `23_0` | barge-v0 | `enemy_body_barge01_128@teal.png` | 128x128 | 9620 |
| AP-0050 | `5_0` | saucer-v0 | `enemy_body_saucer01_128@teal.png` | 128x128 | 13256 |
| AP-0051 | `5_2` | orbiter-v0 | `enemy_body_orbiter01_128@teal.png` | 128x128 | 11448 |
| AP-0052 | `6.` | triblade-v0 | `enemy_body_triblade01_128@teal.png` | 128x128 | 6046 |
| AP-0053 | `7_1` | lance-v2 | `enemy_body_lance03_128@teal.png` | 128x128 | 7226 |
| AP-0054 | `7_4` | shard-v1 | `enemy_body_shard02_128@teal.png` | 128x128 | 9889 |
| AP-0055 | `cb` | lance-v3 | `enemy_body_lance04_128@teal.png` | 128x128 | 7329 |
| AP-0056 | `cb-` | ringgun-v0 | `enemy_body_ringgun01_128@teal.png` | 128x128 | 17000 |
| AP-0057 | `cb-009a` | saucer-v1 | `enemy_body_saucer02_128@teal.png` | 128x128 | 10445 |
| AP-0058 | `cb-009b` | triblade-v1 | `enemy_body_triblade02_128@teal.png` | 128x128 | 6936 |
| AP-0059 | `cd` | triblade-v2 | `enemy_body_triblade03_128@teal.png` | 128x128 | 8686 |
| AP-0060 | `da` | shard-v2 | `enemy_body_shard03_128@teal.png` | 128x128 | 15215 |
| AP-0061 | `droid` | orbiter-v1 | `enemy_body_orbiter02_128@teal.png` | 128x128 | 13788 |
| AP-0062 | `droid1_timer` | orbiter-v2 (timer arcs) | `enemy_body_orbiter03_128@teal.png` | 128x128 | 12612 |
| AP-0063 | `e` | saucer-v2 | `enemy_body_saucer03_128@teal.png` | 128x128 | 14893 |
| AP-0064 | `e_` | ringgun-v1 | `enemy_body_ringgun02_128@teal.png` | 128x128 | 12973 |
| AP-0065 | `e_3308a` | barge-v1 | `enemy_body_barge02_128@teal.png` | 128x128 | 11043 |
| AP-0066 | `e_3308b` | triblade-v3 | `enemy_body_triblade04_128@teal.png` | 128x128 | 8572 |
| AP-0067 | `enemy_hp` | orbiter-v3 | `enemy_body_orbiter04_128@teal.png` | 128x128 | 14447 |
| AP-0068 | `enemytut` | saucer-v3 | `enemy_body_saucer04_128@teal.png` | 128x128 | 9744 |
| AP-0070 | `22_0` | miniorb | `enemy_bullet_miniorb_64@emberdim.png` | 64x64 | 2643 |
| AP-0071 | `7_2` | teardrop | `enemy_bullet_teardrop_64@emberdim.png` | 64x64 | 2287 |
| AP-0072 | `7_3` | spike | `enemy_bullet_spike_64@emberdim.png` | 64x64 | 1772 |
| AP-0073 | `9.` | spikeheavy | `enemy_bullet_spikeheavy_64@emberdim.png` | 64x64 | 2155 |
| AP-0074 | `ebullet` | capsule | `enemy_bullet_capsule_64@emberdim.png` | 64x64 | 1652 |
| AP-0075 | `efx_bullethit` | hitburst | `enemy_bullet_hitburst_64@emberdim.png` | 64x64 | 3469 |
| AP-0076 | `sword` | blade | `enemy_bullet_blade_64@emberdim.png` | 64x64 | 2602 |
| AP-0077 | `warning` | warning | `enemy_bullet_warning_64@emberdim.png` | 64x64 | 3269 |
| AP-0078 | `arrow` | arrow | `enemy_bullet_arrow_64@emberdim.png` | 64x64 | 3345 |
| AP-0079 | `blt` | orb | `enemy_bullet_orb_64@emberdim.png` | 64x64 | 3475 |
| AP-0080 | `blt_` | orbspike | `enemy_bullet_orbspike_64@emberdim.png` | 64x64 | 3276 |

E-BODY = AP-0046…0068 (23 @128, recipe `enemy`); E-BULLET = AP-0070…0080 (11 @64, recipe `bullet`). Planner has **no AP-0069** in this lane (sequence jumps 0068 → 0070) — nothing drawn for it. Total sprites: 271 KB.

Body box aspect per unit follows planner `max_w×max_h` of its row (encoded in `build_w2.py` `BODY_ROWS`); canvas stays square POT 128 with the sprite fitted to that aspect.

## 2. Method

Same deterministic procedural pipeline as W1: draw at 4× supersample in normalized box coords → LANCZOS downscale to target → top-left light pass → seeded grain (bodies). §4.9 metrics (`colors_q32, val, val_std, dark, chroma, fill`) measured on the delivered PNG over alpha>0 pixels; G-A = recipe window check with ≤1 metric allowed out (same rule as W1). Re-running `build_w2.py` reproduces every file byte-for-byte (fixed seeds).

7 body families (parametric variants by aspect / rotation / pod count): saucer (paper dome, teal rim lights), triblade (3-blade rotor, teal roots), lance (dart), ringgun (ring + downward barrel), barge (wide slab + gun pods), orbiter (core + orbiting pods; AP-0062 adds timer arcs), shard (crystal). All bodies carry the teal “eye” as the enemy-faction signal, opposed to player ember (W1).

## 3. Gate results

- **G-A: PASS 34/34** (measured, `w2_units.csv`). Single-metric-outs within allowance: dark×6, chroma×5, val_std×3, val×2. Evidence: STATIC_CONFIRMED (re-measured from delivered files by an independent check: 34/34 RGBA, exact target px, transparent corners, byte counts match CSV, planner coverage exact).
- **G-B (silhouette @64):** `preview/w2_silhouettes_64.png` — 7 families mutually distinct at 64 px. Visual QA, STATIC_CONFIRMED.
- **G-F (in-context):** `preview/w2_combat_mock_720x1280.png` — W1 player vs W2 wave; faction colors (ember vs teal/paper) separate cleanly. Concept layout only, RUNTIME_UNVERIFIED.
- G-C not run (no runtime harness in this session, as W1). G-D N/A.

Recipe windows reverse-confirmed from measurements this lot: `enemy` ≈ val [0.58, 0.65], val_std ≥ ~0.235, dark ≤ ~0.06, chroma [~0.138, ~0.185] (INFERRED from pass/fail edges; authoritative bounds stay in the plan).

## 4. Declared deviations & limits

1. **All 34 `n_units` delivered**, including E-BULLET rows whose scope-B `kept_records=0` — declared in PROGRESS `6444868171` before drawing.
2. **Teal eye/accent on every body** (~5–9% area). Required by the `enemy` recipe chroma floor (~0.138) and used deliberately as faction identity vs W1 ember. If the plan owner wants a stricter accent cap, recipe chroma must change first — flagging, not unilaterally changing.
3. **Bullet cores are ink-900 and nearly invisible on ink-900 backgrounds** — direct consequence of recipe `bullet` (val 0.25–0.30, dark ≥ ~0.40): shells + ember-dim tips carry readability. Same character as W1 bullets. Runtime readability RUNTIME_UNVERIFIED; recommend an in-game contrast check before locking.
4. **Parametric families, not bespoke per-row art**: variants differ by aspect (planner), rotation, pod count — within-family silhouettes are related by design (same disclosed approach as W1).
5. `val_std`/`colors_q32` partially carried by seeded grain and supersampled edges, as in W1 — values are honest measurements of delivered pixels, but flattening the grain in a future style pass would move them.
6. Center pivot assumed; final pivot/anchor awaits `sprite_mesh_contract` (unchanged from W1).
7. AP-0062 “timer” read as countdown arcs on the orbiter (INFERRED from planner base name `droid1_timer`).

## 5. Godot import notes

- POT RGBA PNGs (128×128 bodies, 64×64 bullets), transparent corners, no premultiplied alpha. Suggested: Filter=Linear, Mipmaps=on for bodies scaled down in-game; bullets typically drawn near-native — either setting safe.
- Enemies are authored facing **down**; if a spawner rotates sprites toward travel direction, rotation 0 = downward (i.e., apply +90° offset vs Godot's default right-facing convention as needed).
- Files live under `art/w2-enemy/sprites/{bodies,bullets}/`; move/rename freely on import — mapping back to planner rows is in §1 + `w2_units.csv`.
