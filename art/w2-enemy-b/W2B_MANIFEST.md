# W2 — ENEMY Lane Manifest (Variant B: Solar Neon Arcade-Pop)

- **Author branch**: `arena/eca8588b-windwings-space-shooter-game-p` (`Art-designer-B`)
- **Wave**: `W2` (`ENEMY` — 34 units total: `E-BODY` ×23 @ `128×128`, `E-BULLET` ×11 @ `64×64`)
- **Style direction**: Vivid **Hyper-Crimson `#FF1E56` + Neon-Magenta `#FF2496` + Electric-Violet `#7B2CBF` + Hazard-Amber `#FFB800`** invader armada with `#160630` dark violet-indigo cel outlines, 30° top-left directional specular facets, downward combat orientation (`▼`), and white-cored bullet-hell projectiles — maximum chromatic separation against both bright orbital skies and the Pearl-Azure W1 player lane.
- **License**: `chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)`
- **Preview sheet**: `art/w2-enemy-b/preview/w2b_contact_sheet.png` (`1480×1265`)

## Quality Gates Summary

| Gate | Check | Result |
|---|---|---|
| **G-A (RGBA Straight Alpha)** | All 34 PNGs RGBA 8bpc straight alpha (`premultiplied=off`), 4 corners `alpha == 0`, zero border fringe | **PASS (34/34)** |
| **G-B (64px Silhouette)** | 23 unique enemy hull silhouettes (`scout_dart`..`target_drone`) + 11 distinct bullet silhouettes read cleanly at 64×64 | **PASS (34/34)** |
| **G-C (Faction Separation)** | Warm/electric menace hues (Crimson/Magenta/Violet/Amber) contrast cleanly against cool Pearl/Cobalt/Cyan W1 player units | **PASS (34/34)** |
| **G-E (Naming & Masters)** | Clean functional `snake_case` filenames mapped 1:1 to `AP-0046..AP-0080` + 2× high-res RGBA `masters/` preserved | **PASS (34/34)** |
| **G-F (Live W1-vs-W2 Read)** | Verified live combat composite (W1 player vs W2 enemies + bullet curtain over bright sky) | **PASS** |

## Complete 34-Unit Table (`sprites/` + `masters/`)

| # | Planner Row | Batch | Planner Base | Variant | Sprite (`art/w2-enemy-b/...`) | Master (`source`) | Sprite px | Master px | Val | Chroma | Recipe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `01` | `AP-0046` | `E-BODY` | `1.` | `scout_dart` | `sprites/bodies/enemy_body_01_scout_dart_128@crimson.png` | `masters/bodies/enemy_body_01_scout_dart_128@crimson.png` | `128x128` | `256x256` | `0.645` | `0.740` | `b_enemy_crimson` |
| `02` | `AP-0047` | `E-BODY` | `14_2` | `viper_lance` | `sprites/bodies/enemy_body_02_viper_lance_128@crimson.png` | `masters/bodies/enemy_body_02_viper_lance_128@crimson.png` | `128x128` | `256x256` | `0.610` | `0.710` | `b_enemy_crimson` |
| `03` | `AP-0048` | `E-BODY` | `212_1` | `wasp_raider` | `sprites/bodies/enemy_body_03_wasp_raider_128@magenta.png` | `masters/bodies/enemy_body_03_wasp_raider_128@magenta.png` | `128x128` | `256x256` | `0.660` | `0.692` | `b_enemy_magenta` |
| `04` | `AP-0049` | `E-BODY` | `23_0` | `manta_glider` | `sprites/bodies/enemy_body_04_manta_glider_128@violet.png` | `masters/bodies/enemy_body_04_manta_glider_128@violet.png` | `128x128` | `256x256` | `0.598` | `0.698` | `b_enemy_violet` |
| `05` | `AP-0050` | `E-BODY` | `5_0` | `beetle_cruiser` | `sprites/bodies/enemy_body_05_beetle_cruiser_128@crimson.png` | `masters/bodies/enemy_body_05_beetle_cruiser_128@crimson.png` | `128x128` | `256x256` | `0.696` | `0.708` | `b_enemy_crimson` |
| `06` | `AP-0051` | `E-BODY` | `5_2` | `swarmling_pod` | `sprites/bodies/enemy_body_06_swarmling_pod_128@amber.png` | `masters/bodies/enemy_body_06_swarmling_pod_128@amber.png` | `128x128` | `256x256` | `0.741` | `0.756` | `b_enemy_amber` |
| `07` | `AP-0052` | `E-BODY` | `6.` | `stalker_blade` | `sprites/bodies/enemy_body_07_stalker_blade_128@magenta.png` | `masters/bodies/enemy_body_07_stalker_blade_128@magenta.png` | `128x128` | `256x256` | `0.659` | `0.739` | `b_enemy_magenta` |
| `08` | `AP-0053` | `E-BODY` | `7_1` | `dread_carrier` | `sprites/bodies/enemy_body_08_dread_carrier_128@violet.png` | `masters/bodies/enemy_body_08_dread_carrier_128@violet.png` | `128x128` | `256x256` | `0.588` | `0.701` | `b_enemy_violet` |
| `09` | `AP-0054` | `E-BODY` | `7_4` | `spire_frigate` | `sprites/bodies/enemy_body_09_spire_frigate_128@crimson.png` | `masters/bodies/enemy_body_09_spire_frigate_128@crimson.png` | `128x128` | `256x256` | `0.645` | `0.707` | `b_enemy_crimson` |
| `10` | `AP-0055` | `E-BODY` | `cb` | `centurion_mk1` | `sprites/bodies/enemy_body_10_centurion_mk1_128@crimson.png` | `masters/bodies/enemy_body_10_centurion_mk1_128@crimson.png` | `128x128` | `256x256` | `0.679` | `0.732` | `b_enemy_crimson` |
| `11` | `AP-0056` | `E-BODY` | `cb-` | `centurion_turret` | `sprites/bodies/enemy_body_11_centurion_turret_128@amber.png` | `masters/bodies/enemy_body_11_centurion_turret_128@amber.png` | `128x128` | `256x256` | `0.587` | `0.711` | `b_enemy_amber` |
| `12` | `AP-0057` | `E-BODY` | `cb-009a` | `wingpod_wide` | `sprites/bodies/enemy_body_12_wingpod_wide_128@crimson.png` | `masters/bodies/enemy_body_12_wingpod_wide_128@crimson.png` | `128x128` | `256x256` | `0.590` | `0.752` | `b_enemy_crimson` |
| `13` | `AP-0058` | `E-BODY` | `cb-009b` | `wingpod_core` | `sprites/bodies/enemy_body_13_wingpod_core_128@magenta.png` | `masters/bodies/enemy_body_13_wingpod_core_128@magenta.png` | `128x128` | `256x256` | `0.747` | `0.730` | `b_enemy_magenta` |
| `14` | `AP-0059` | `E-BODY` | `cd` | `cyber_disc` | `sprites/bodies/enemy_body_14_cyber_disc_128@violet.png` | `masters/bodies/enemy_body_14_cyber_disc_128@violet.png` | `128x128` | `256x256` | `0.603` | `0.728` | `b_enemy_violet` |
| `15` | `AP-0060` | `E-BODY` | `da` | `void_sentinel` | `sprites/bodies/enemy_body_15_void_sentinel_128@magenta.png` | `masters/bodies/enemy_body_15_void_sentinel_128@magenta.png` | `128x128` | `256x256` | `0.631` | `0.722` | `b_enemy_magenta` |
| `16` | `AP-0061` | `E-BODY` | `droid` | `automaton_droid` | `sprites/bodies/enemy_body_16_automaton_droid_128@amber.png` | `masters/bodies/enemy_body_16_automaton_droid_128@amber.png` | `128x128` | `256x256` | `0.639` | `0.755` | `b_enemy_amber` |
| `17` | `AP-0062` | `E-BODY` | `droid1_timer` | `chrono_mine` | `sprites/bodies/enemy_body_17_chrono_mine_128@amber.png` | `masters/bodies/enemy_body_17_chrono_mine_128@amber.png` | `128x128` | `256x256` | `0.606` | `0.710` | `b_enemy_amber` |
| `18` | `AP-0063` | `E-BODY` | `e` | `phantom_hex` | `sprites/bodies/enemy_body_18_phantom_hex_128@violet.png` | `masters/bodies/enemy_body_18_phantom_hex_128@violet.png` | `128x128` | `256x256` | `0.616` | `0.676` | `b_enemy_violet` |
| `19` | `AP-0064` | `E-BODY` | `e_` | `reaper_scythe` | `sprites/bodies/enemy_body_19_reaper_scythe_128@crimson.png` | `masters/bodies/enemy_body_19_reaper_scythe_128@crimson.png` | `128x128` | `256x256` | `0.669` | `0.728` | `b_enemy_crimson` |
| `20` | `AP-0065` | `E-BODY` | `e_3308a` | `juggernaut_hull` | `sprites/bodies/enemy_body_20_juggernaut_hull_128@crimson.png` | `masters/bodies/enemy_body_20_juggernaut_hull_128@crimson.png` | `128x128` | `256x256` | `0.654` | `0.698` | `b_enemy_crimson` |
| `21` | `AP-0066` | `E-BODY` | `e_3308b` | `juggernaut_core` | `sprites/bodies/enemy_body_21_juggernaut_core_128@amber.png` | `masters/bodies/enemy_body_21_juggernaut_core_128@amber.png` | `128x128` | `256x256` | `0.749` | `0.723` | `b_enemy_amber` |
| `22` | `AP-0067` | `E-BODY` | `enemy_hp` | `hp_pip_bar` | `sprites/bodies/enemy_body_22_hp_pip_bar_128@crimson.png` | `masters/bodies/enemy_body_22_hp_pip_bar_128@crimson.png` | `128x128` | `256x256` | `0.573` | `0.732` | `b_enemy_hud` |
| `23` | `AP-0068` | `E-BODY` | `enemytut` | `target_drone` | `sprites/bodies/enemy_body_23_target_drone_128@amber.png` | `masters/bodies/enemy_body_23_target_drone_128@amber.png` | `128x128` | `256x256` | `0.712` | `0.646` | `b_enemy_amber` |
| `24` | `AP-0070` | `E-BULLET` | `22_0` | `needle_dart` | `sprites/bullets/enemy_bullet_01_needle_dart_64@crimson.png` | `masters/bullets/enemy_bullet_01_needle_dart_64@crimson.png` | `64x64` | `128x128` | `0.634` | `0.740` | `b_ebullet_crimson` |
| `25` | `AP-0071` | `E-BULLET` | `7_2` | `twin_fang` | `sprites/bullets/enemy_bullet_02_twin_fang_64@magenta.png` | `masters/bullets/enemy_bullet_02_twin_fang_64@magenta.png` | `64x64` | `128x128` | `0.588` | `0.708` | `b_ebullet_magenta` |
| `26` | `AP-0072` | `E-BULLET` | `7_3` | `lance_spear` | `sprites/bullets/enemy_bullet_03_lance_spear_64@crimson.png` | `masters/bullets/enemy_bullet_03_lance_spear_64@crimson.png` | `64x64` | `128x128` | `0.646` | `0.771` | `b_ebullet_crimson` |
| `27` | `AP-0073` | `E-BULLET` | `9.` | `beam_shard` | `sprites/bullets/enemy_bullet_04_beam_shard_64@amber.png` | `masters/bullets/enemy_bullet_04_beam_shard_64@amber.png` | `64x64` | `128x128` | `0.659` | `0.691` | `b_ebullet_amber` |
| `28` | `AP-0074` | `E-BULLET` | `ebullet` | `nova_star` | `sprites/bullets/enemy_bullet_05_nova_star_64@magenta.png` | `masters/bullets/enemy_bullet_05_nova_star_64@magenta.png` | `64x64` | `128x128` | `0.671` | `0.648` | `b_ebullet_magenta` |
| `29` | `AP-0075` | `E-BULLET` | `efx_bullethit` | `hit_spark` | `sprites/bullets/enemy_bullet_06_hit_spark_64@amber.png` | `masters/bullets/enemy_bullet_06_hit_spark_64@amber.png` | `64x64` | `128x128` | `0.612` | `0.704` | `b_ebullet_amber` |
| `30` | `AP-0076` | `E-BULLET` | `sword` | `energy_sword` | `sprites/bullets/enemy_bullet_07_energy_sword_64@crimson.png` | `masters/bullets/enemy_bullet_07_energy_sword_64@crimson.png` | `64x64` | `128x128` | `0.566` | `0.759` | `b_ebullet_crimson` |
| `31` | `AP-0077` | `E-BULLET` | `warning` | `hazard_sign` | `sprites/bullets/enemy_bullet_08_hazard_sign_64@amber.png` | `masters/bullets/enemy_bullet_08_hazard_sign_64@amber.png` | `64x64` | `128x128` | `0.590` | `0.760` | `b_ebullet_amber` |
| `32` | `AP-0078` | `E-BULLET` | `arrow` | `lock_chevron` | `sprites/bullets/enemy_bullet_09_lock_chevron_64@crimson.png` | `masters/bullets/enemy_bullet_09_lock_chevron_64@crimson.png` | `64x64` | `128x128` | `0.629` | `0.702` | `b_ebullet_crimson` |
| `33` | `AP-0079` | `E-BULLET` | `blt` | `plasma_orb` | `sprites/bullets/enemy_bullet_10_plasma_orb_64@crimson.png` | `masters/bullets/enemy_bullet_10_plasma_orb_64@crimson.png` | `64x64` | `128x128` | `0.774` | `0.658` | `b_ebullet_crimson` |
| `34` | `AP-0080` | `E-BULLET` | `blt_` | `ring_pulse` | `sprites/bullets/enemy_bullet_11_ring_pulse_64@violet.png` | `masters/bullets/enemy_bullet_11_ring_pulse_64@violet.png` | `64x64` | `128x128` | `0.672` | `0.662` | `b_ebullet_violet` |

## Reproducibility

```bash
python3 art/w2-enemy-b/build_w2b.py
python3 art/w2-enemy-b/make_w2b_preview.py
```
