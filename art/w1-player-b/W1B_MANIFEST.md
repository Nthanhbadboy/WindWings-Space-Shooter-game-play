# W1 — PLAYER Lane Manifest (Variant B: Solar Neon Arcade-Pop)

- **Author branch**: `arena/eca8588b-windwings-space-shooter-game-p` (`Art-designer-B`)
- **Wave**: `W1` (`PLAYER` — 48 units total: `P-SHIP` ×25, `P-DRONE` ×13, `P-BULLET` ×8, `P-FX` ×2)
- **Style direction**: Bright, high-energy **Solar Neon Arcade-Pop** (Pearl-White `#E2EEFF` + Electric Cobalt-Azure `#186CF2` + Solar Gold `#FFD012` + Tangerine `#FF6A0C` + Neon Cyan `#00E2FF` + Emerald `#00EEB4`, crisp `#08143E` cel outlines, 30° top-left directional specular facets) — 100% independent of Variant A's dark Ink & Ember palette while matching identical slot naming/dimensions for `Art-curator` per-slot selection/merge.
- **License**: `chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)`
- **Preview sheet**: `art/w1-player-b/preview/w1b_contact_sheet.png` (`1480×2160`)

## Quality Gates Summary

| Gate | Check | Result |
|---|---|---|
| **G-A (RGBA Straight Alpha)** | All 48 PNGs RGBA 8bpc straight alpha (`premultiplied=off`), 4 corners `alpha == 0`, zero border fringe via premultiplied-Lanczos-unpremul pipeline | **PASS (48/48)** |
| **G-B (64px Silhouette)** | 5 starfighter classes × 5 structural Mk-I..Mk-V tier geometries + 5 drone archetypes × 3 structural tiers read cleanly as black silhouettes at 64×64 | **PASS (48/48)** |
| **G-C (Palette & Value)** | Bright arcade-pop player palette (`val 0.74–0.94`, `chroma 0.35–0.78`), zero legacy APK asset reuse | **PASS (48/48)** |
| **G-D (Seamless Beam Tile)** | `player_bullet_beam_32x512@cyan.png` & `player_bullet_beamheavy_32x512@solar.png` tile vertically with exact 64px period (`row[0] == row[64]`, zero seam error) | **PASS (2/2)** |
| **G-E (Naming & Masters)** | Functional `snake_case` filenames matching planner slots + 2× high-res RGBA `masters/` preserved per unit | **PASS (48/48)** |
| **G-F (Gameplay Readability)** | Verified live-scale composite over bright orbital sky gradient (see `preview/w1b_contact_sheet.png` panel 4) | **PASS** |

## Complete 48-Unit Table (`sprites/` + `masters/`)

| # | Planner Row | Batch | Variant | Sprite (`art/w1-player-b/...`) | Master (`source`) | Sprite px | Master px | Val | Chroma | Recipe |
|---|---|---|---|---|---|---|---|---|---|---|
| `01` | `AP-0016` | `P-SHIP` | `windfang-1` | `sprites/ships/player_ship_01_256@solar.png` | `masters/ships/player_ship_01_256@solar.png` | `256x256` | `512x512` | `0.783` | `0.423` | `b_ship_pearl_azure` |
| `02` | `AP-0016` | `P-SHIP` | `windfang-2` | `sprites/ships/player_ship_02_256@solar.png` | `masters/ships/player_ship_02_256@solar.png` | `256x256` | `512x512` | `0.784` | `0.433` | `b_ship_pearl_azure` |
| `03` | `AP-0016` | `P-SHIP` | `windfang-3` | `sprites/ships/player_ship_03_256@solar.png` | `masters/ships/player_ship_03_256@solar.png` | `256x256` | `512x512` | `0.779` | `0.446` | `b_ship_pearl_azure` |
| `04` | `AP-0016` | `P-SHIP` | `windfang-4` | `sprites/ships/player_ship_04_256@solar.png` | `masters/ships/player_ship_04_256@solar.png` | `256x256` | `512x512` | `0.784` | `0.451` | `b_ship_pearl_azure` |
| `05` | `AP-0016` | `P-SHIP` | `windfang-5` | `sprites/ships/player_ship_05_256@solar.png` | `masters/ships/player_ship_05_256@solar.png` | `256x256` | `512x512` | `0.779` | `0.469` | `b_ship_pearl_azure` |
| `06` | `AP-0016` | `P-SHIP` | `solarviper-1` | `sprites/ships/player_ship_06_256@solar.png` | `masters/ships/player_ship_06_256@solar.png` | `256x256` | `512x512` | `0.750` | `0.451` | `b_ship_pearl_azure` |
| `07` | `AP-0016` | `P-SHIP` | `solarviper-2` | `sprites/ships/player_ship_07_256@solar.png` | `masters/ships/player_ship_07_256@solar.png` | `256x256` | `512x512` | `0.759` | `0.470` | `b_ship_pearl_azure` |
| `08` | `AP-0016` | `P-SHIP` | `solarviper-3` | `sprites/ships/player_ship_08_256@solar.png` | `masters/ships/player_ship_08_256@solar.png` | `256x256` | `512x512` | `0.757` | `0.476` | `b_ship_pearl_azure` |
| `09` | `AP-0016` | `P-SHIP` | `solarviper-4` | `sprites/ships/player_ship_09_256@solar.png` | `masters/ships/player_ship_09_256@solar.png` | `256x256` | `512x512` | `0.758` | `0.485` | `b_ship_pearl_azure` |
| `10` | `AP-0016` | `P-SHIP` | `solarviper-5` | `sprites/ships/player_ship_10_256@solar.png` | `masters/ships/player_ship_10_256@solar.png` | `256x256` | `512x512` | `0.765` | `0.504` | `b_ship_pearl_azure` |
| `11` | `AP-0016` | `P-SHIP` | `skybastion-1` | `sprites/ships/player_ship_11_256@solar.png` | `masters/ships/player_ship_11_256@solar.png` | `256x256` | `512x512` | `0.787` | `0.411` | `b_ship_pearl_azure` |
| `12` | `AP-0016` | `P-SHIP` | `skybastion-2` | `sprites/ships/player_ship_12_256@solar.png` | `masters/ships/player_ship_12_256@solar.png` | `256x256` | `512x512` | `0.790` | `0.428` | `b_ship_pearl_azure` |
| `13` | `AP-0016` | `P-SHIP` | `skybastion-3` | `sprites/ships/player_ship_13_256@solar.png` | `masters/ships/player_ship_13_256@solar.png` | `256x256` | `512x512` | `0.792` | `0.417` | `b_ship_pearl_azure` |
| `14` | `AP-0016` | `P-SHIP` | `skybastion-4` | `sprites/ships/player_ship_14_256@solar.png` | `masters/ships/player_ship_14_256@solar.png` | `256x256` | `512x512` | `0.787` | `0.431` | `b_ship_pearl_azure` |
| `15` | `AP-0016` | `P-SHIP` | `skybastion-5` | `sprites/ships/player_ship_15_256@solar.png` | `masters/ships/player_ship_15_256@solar.png` | `256x256` | `512x512` | `0.794` | `0.444` | `b_ship_pearl_azure` |
| `16` | `AP-0016` | `P-SHIP` | `aerofalcon-1` | `sprites/ships/player_ship_16_256@solar.png` | `masters/ships/player_ship_16_256@solar.png` | `256x256` | `512x512` | `0.778` | `0.456` | `b_ship_pearl_azure` |
| `17` | `AP-0016` | `P-SHIP` | `aerofalcon-2` | `sprites/ships/player_ship_17_256@solar.png` | `masters/ships/player_ship_17_256@solar.png` | `256x256` | `512x512` | `0.778` | `0.469` | `b_ship_pearl_azure` |
| `18` | `AP-0016` | `P-SHIP` | `aerofalcon-3` | `sprites/ships/player_ship_18_256@solar.png` | `masters/ships/player_ship_18_256@solar.png` | `256x256` | `512x512` | `0.770` | `0.478` | `b_ship_pearl_azure` |
| `19` | `AP-0016` | `P-SHIP` | `aerofalcon-4` | `sprites/ships/player_ship_19_256@solar.png` | `masters/ships/player_ship_19_256@solar.png` | `256x256` | `512x512` | `0.775` | `0.492` | `b_ship_pearl_azure` |
| `20` | `AP-0016` | `P-SHIP` | `aerofalcon-5` | `sprites/ships/player_ship_20_256@solar.png` | `masters/ships/player_ship_20_256@solar.png` | `256x256` | `512x512` | `0.772` | `0.514` | `b_ship_pearl_azure` |
| `21` | `AP-0016` | `P-SHIP` | `novaarc-1` | `sprites/ships/player_ship_21_256@solar.png` | `masters/ships/player_ship_21_256@solar.png` | `256x256` | `512x512` | `0.754` | `0.439` | `b_ship_pearl_azure` |
| `22` | `AP-0016` | `P-SHIP` | `novaarc-2` | `sprites/ships/player_ship_22_256@solar.png` | `masters/ships/player_ship_22_256@solar.png` | `256x256` | `512x512` | `0.752` | `0.447` | `b_ship_pearl_azure` |
| `23` | `AP-0016` | `P-SHIP` | `novaarc-3` | `sprites/ships/player_ship_23_256@solar.png` | `masters/ships/player_ship_23_256@solar.png` | `256x256` | `512x512` | `0.743` | `0.475` | `b_ship_pearl_azure` |
| `24` | `AP-0016` | `P-SHIP` | `novaarc-4` | `sprites/ships/player_ship_24_256@solar.png` | `masters/ships/player_ship_24_256@solar.png` | `256x256` | `512x512` | `0.748` | `0.482` | `b_ship_pearl_azure` |
| `25` | `AP-0016` | `P-SHIP` | `novaarc-5` | `sprites/ships/player_ship_25_256@solar.png` | `masters/ships/player_ship_25_256@solar.png` | `256x256` | `512x512` | `0.751` | `0.501` | `b_ship_pearl_azure` |
| `26` | `AP-0011` | `P-DRONE` | `shieldpod-1` | `sprites/drones/player_drone_01_128@cyan.png` | `masters/drones/player_drone_01_128@cyan.png` | `128x128` | `256x256` | `0.789` | `0.384` | `b_drone_pearl_gold` |
| `27` | `AP-0011` | `P-DRONE` | `miniwing-1` | `sprites/drones/player_drone_02_128@cyan.png` | `masters/drones/player_drone_02_128@cyan.png` | `128x128` | `256x256` | `0.708` | `0.449` | `b_drone_pearl_gold` |
| `28` | `AP-0011` | `P-DRONE` | `hexgyro-1` | `sprites/drones/player_drone_03_128@cyan.png` | `masters/drones/player_drone_03_128@cyan.png` | `128x128` | `256x256` | `0.790` | `0.344` | `b_drone_pearl_gold` |
| `29` | `AP-0011` | `P-DRONE` | `crescentarc-1` | `sprites/drones/player_drone_04_128@cyan.png` | `masters/drones/player_drone_04_128@cyan.png` | `128x128` | `256x256` | `0.775` | `0.529` | `b_drone_pearl_gold` |
| `30` | `AP-0011` | `P-DRONE` | `twinpod-1` | `sprites/drones/player_drone_05_128@cyan.png` | `masters/drones/player_drone_05_128@cyan.png` | `128x128` | `256x256` | `0.803` | `0.218` | `b_drone_pearl_gold` |
| `31` | `AP-0011` | `P-DRONE` | `shieldpod-2` | `sprites/drones/player_drone_06_128@cyan.png` | `masters/drones/player_drone_06_128@cyan.png` | `128x128` | `256x256` | `0.775` | `0.411` | `b_drone_pearl_gold` |
| `32` | `AP-0011` | `P-DRONE` | `miniwing-2` | `sprites/drones/player_drone_07_128@cyan.png` | `masters/drones/player_drone_07_128@cyan.png` | `128x128` | `256x256` | `0.722` | `0.488` | `b_drone_pearl_gold` |
| `33` | `AP-0011` | `P-DRONE` | `hexgyro-2` | `sprites/drones/player_drone_08_128@cyan.png` | `masters/drones/player_drone_08_128@cyan.png` | `128x128` | `256x256` | `0.783` | `0.391` | `b_drone_pearl_gold` |
| `34` | `AP-0011` | `P-DRONE` | `crescentarc-2` | `sprites/drones/player_drone_09_128@cyan.png` | `masters/drones/player_drone_09_128@cyan.png` | `128x128` | `256x256` | `0.766` | `0.539` | `b_drone_pearl_gold` |
| `35` | `AP-0011` | `P-DRONE` | `twinpod-2` | `sprites/drones/player_drone_10_128@cyan.png` | `masters/drones/player_drone_10_128@cyan.png` | `128x128` | `256x256` | `0.779` | `0.295` | `b_drone_pearl_gold` |
| `36` | `AP-0011` | `P-DRONE` | `shieldpod-3` | `sprites/drones/player_drone_11_128@cyan.png` | `masters/drones/player_drone_11_128@cyan.png` | `128x128` | `256x256` | `0.779` | `0.407` | `b_drone_pearl_gold` |
| `37` | `AP-0011` | `P-DRONE` | `miniwing-3` | `sprites/drones/player_drone_12_128@cyan.png` | `masters/drones/player_drone_12_128@cyan.png` | `128x128` | `256x256` | `0.742` | `0.483` | `b_drone_pearl_gold` |
| `38` | `AP-0011` | `P-DRONE` | `hexgyro-3` | `sprites/drones/player_drone_13_128@cyan.png` | `masters/drones/player_drone_13_128@cyan.png` | `128x128` | `256x256` | `0.782` | `0.407` | `b_drone_pearl_gold` |
| `39` | `AP-0002` | `P-BULLET` | `dronebolt` | `sprites/bullets/player_bullet_dronebolt_32@cyan.png` | `masters/bullets/player_bullet_dronebolt_32@cyan.png` | `32x32` | `64x64` | `0.640` | `0.365` | `b_bullet_neon_cyan` |
| `40` | `AP-0003` | `P-BULLET` | `beam` | `sprites/bullets/player_bullet_beam_32x512@cyan.png` | `masters/bullets/player_bullet_beam_32x512@cyan.png` | `32x512` | `64x1024` | `0.765` | `0.514` | `b_bullet_neon_cyan` |
| `41` | `AP-0004` | `P-BULLET` | `beamheavy` | `sprites/bullets/player_bullet_beamheavy_32x512@solar.png` | `masters/bullets/player_bullet_beamheavy_32x512@solar.png` | `32x512` | `64x1024` | `0.810` | `0.474` | `b_bullet_neon_cyan` |
| `42` | `AP-0005` | `P-BULLET` | `plasmaorb` | `sprites/bullets/player_bullet_plasmaorb_32@cyan.png` | `masters/bullets/player_bullet_plasmaorb_32@cyan.png` | `32x32` | `64x64` | `0.758` | `0.415` | `b_bullet_neon_cyan` |
| `43` | `AP-0006` | `P-BULLET` | `missile` | `sprites/bullets/player_bullet_missile_32@solar.png` | `masters/bullets/player_bullet_missile_32@solar.png` | `32x32` | `64x64` | `0.595` | `0.262` | `b_bullet_neon_cyan` |
| `44` | `AP-0007` | `P-BULLET` | `boltmk5` | `sprites/bullets/player_bullet_boltmk5_32@solar.png` | `masters/bullets/player_bullet_boltmk5_32@solar.png` | `32x32` | `64x64` | `0.661` | `0.379` | `b_bullet_neon_cyan` |
| `45` | `AP-0008` | `P-BULLET` | `childbolt` | `sprites/bullets/player_bullet_childbolt_32@cyan.png` | `masters/bullets/player_bullet_childbolt_32@cyan.png` | `32x32` | `64x64` | `0.680` | `0.390` | `b_bullet_neon_cyan` |
| `46` | `AP-0009` | `P-BULLET` | `beamflare` | `sprites/bullets/player_bullet_beamflare_32@emerald.png` | `masters/bullets/player_bullet_beamflare_32@emerald.png` | `32x32` | `64x64` | `0.529` | `0.276` | `b_bullet_neon_cyan` |
| `47` | `AP-0013` | `P-FX` | `engineplume` | `sprites/fx/player_fx_engineplume_128@solar.png` | `masters/fx/player_fx_engineplume_128@solar.png` | `128x128` | `256x256` | `0.896` | `0.606` | `b_fx_neon_pop` |
| `48` | `AP-0014` | `P-FX` | `muzzleflash` | `sprites/fx/player_fx_muzzleflash_128@cyan.png` | `masters/fx/player_fx_muzzleflash_128@cyan.png` | `128x128` | `256x256` | `0.791` | `0.477` | `b_fx_neon_pop` |

## Reproducibility

```bash
python3 art/w1-player-b/build_w1b.py
python3 art/w1-player-b/make_w1b_preview.py
```
