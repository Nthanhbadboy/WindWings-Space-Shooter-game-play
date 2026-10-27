# W3 — BOSS Lane Manifest (Variant B: Solar Neon Arcade-Pop)

- **Author branch**: `arena/eca8588b-windwings-space-shooter-game-p` (`Art-designer-B`)
- **Wave**: `W3` (`BOSS` — 42 units total: `B-BODY` ×35 @ `512×512`, `B-PART` ×7 @ `256×256` + `512×512` masters)
- **Style direction**: Vivid **Solar Neon Arcade-Pop** boss dreadnoughts (`crimson`, `violet`, `emerald`, `magenta`, `amber`) with `#14062E` cel outlines, 30° top-left directional specular facets, mandatory **left-vs-right combat asymmetry**, and **≥1 visually separated destructible glowing sub-module** per boss.
- **License**: `chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)`
- **Preview sheet**: `art/w3-boss-b/preview/w3b_contact_sheet.png` (`1520×1790`)

## Quality Gates Summary

| Gate | Check | Result |
|---|---|---|
| **G-A (RGBA Straight Alpha)** | All 42 PNGs RGBA 8bpc straight alpha (`premultiplied=off`), 4 corners `alpha == 0`, zero border fringe | **PASS (42/42)** |
| **G-B (Asymmetry & Destructible Module)** | 35/35 `B-BODY` feature asymmetric port/starboard weaponry + ≥1 tethered separated destructible glowing module (`ART_REDRAW_PLAN.md` §3.2) | **PASS (35/35)** |
| **G-C (Modular Sub-Parts)** | 7/7 `B-PART` (`AP-0122..0128`) drawn cleanly at `256×256` (`512×512` masters) with functional `snake_case` names (zero legacy Vietnamese/APK strings in filenames) | **PASS (7/7)** |
| **G-E (Masters & Metadata)** | `masters/` preserved per unit + full `source` / `license` / `author` / `recipe` manifest | **PASS (42/42)** |
| **G-F (Live Boss Showdown)** | Verified live composite (Boss + destructible turret + bullet curtain vs W1 player & cyan beam over bright sky) | **PASS** |

## Complete 42-Unit Table (`sprites/` + `masters/`)

| # | Planner Row | Batch | Planner Base | Variant | Sprite (`art/w3-boss-b/...`) | Master (`source`) | Sprite px | Master px | Val | Chroma | Recipe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `01` | `AP-0117` | `B-BODY` | `bosss` | `emblem_s` | `sprites/bodies/boss_body_01_sovereign_s_512@crimson.png` | `masters/bodies/boss_body_01_sovereign_s_512@crimson.png` | `512x512` | `512x512` | `0.634` | `0.702` | `b_boss_crimson` |
| `02` | `AP-0118` | `B-BODY` | `bossx` | `overlord_x` | `sprites/bodies/boss_body_02_overlord_x_512@magenta.png` | `masters/bodies/boss_body_02_overlord_x_512@magenta.png` | `512x512` | `512x512` | `0.648` | `0.719` | `b_boss_magenta` |
| `03` | `AP-0119` | `B-BODY` | `boss_shields` | `aegis_bastion` | `sprites/bodies/boss_body_03_aegis_bastion_512@amber.png` | `masters/bodies/boss_body_03_aegis_bastion_512@amber.png` | `512x512` | `512x512` | `0.750` | `0.785` | `b_boss_amber` |
| `04` | `AP-0120` | `B-BODY` | `GLYPH-boss-7001` | `citadel-mk1` | `sprites/bodies/boss_body_04_citadel_mk1_512@crimson.png` | `masters/bodies/boss_body_04_citadel_mk1_512@crimson.png` | `512x512` | `512x512` | `0.726` | `0.710` | `b_boss_crimson` |
| `05` | `AP-0120` | `B-BODY` | `GLYPH-boss-7002` | `arachnid-mk1` | `sprites/bodies/boss_body_05_arachnid_mk1_512@emerald.png` | `masters/bodies/boss_body_05_arachnid_mk1_512@emerald.png` | `512x512` | `512x512` | `0.685` | `0.729` | `b_boss_emerald` |
| `06` | `AP-0120` | `B-BODY` | `GLYPH-boss-7003` | `leviathan-mk1` | `sprites/bodies/boss_body_06_leviathan_mk1_512@amber.png` | `masters/bodies/boss_body_06_leviathan_mk1_512@amber.png` | `512x512` | `512x512` | `0.696` | `0.756` | `b_boss_amber` |
| `07` | `AP-0120` | `B-BODY` | `GLYPH-boss-7004` | `chronos-mk1` | `sprites/bodies/boss_body_07_chronos_mk1_512@violet.png` | `masters/bodies/boss_body_07_chronos_mk1_512@violet.png` | `512x512` | `512x512` | `0.618` | `0.745` | `b_boss_violet` |
| `08` | `AP-0120` | `B-BODY` | `GLYPH-boss-7005` | `seraph-mk1` | `sprites/bodies/boss_body_08_seraph_mk1_512@magenta.png` | `masters/bodies/boss_body_08_seraph_mk1_512@magenta.png` | `512x512` | `512x512` | `0.693` | `0.722` | `b_boss_magenta` |
| `09` | `AP-0120` | `B-BODY` | `GLYPH-boss-7006` | `kraken-mk1` | `sprites/bodies/boss_body_09_kraken_mk1_512@crimson.png` | `masters/bodies/boss_body_09_kraken_mk1_512@crimson.png` | `512x512` | `512x512` | `0.691` | `0.782` | `b_boss_crimson` |
| `10` | `AP-0120` | `B-BODY` | `GLYPH-boss-7009` | `scorpion-mk1` | `sprites/bodies/boss_body_10_scorpion_mk1_512@emerald.png` | `masters/bodies/boss_body_10_scorpion_mk1_512@emerald.png` | `512x512` | `512x512` | `0.636` | `0.761` | `b_boss_emerald` |
| `11` | `AP-0120` | `B-BODY` | `GLYPH-boss-7010` | `colossus-mk1` | `sprites/bodies/boss_body_11_colossus_mk1_512@amber.png` | `masters/bodies/boss_body_11_colossus_mk1_512@amber.png` | `512x512` | `512x512` | `0.717` | `0.743` | `b_boss_amber` |
| `12` | `AP-0120` | `B-BODY` | `GLYPH-boss-7011` | `citadel-mk2` | `sprites/bodies/boss_body_12_citadel_mk2_512@emerald.png` | `masters/bodies/boss_body_12_citadel_mk2_512@emerald.png` | `512x512` | `512x512` | `0.705` | `0.748` | `b_boss_emerald` |
| `13` | `AP-0120` | `B-BODY` | `GLYPH-boss-7012` | `arachnid-mk2` | `sprites/bodies/boss_body_13_arachnid_mk2_512@amber.png` | `masters/bodies/boss_body_13_arachnid_mk2_512@amber.png` | `512x512` | `512x512` | `0.721` | `0.741` | `b_boss_amber` |
| `14` | `AP-0120` | `B-BODY` | `GLYPH-boss-7013` | `leviathan-mk2` | `sprites/bodies/boss_body_14_leviathan_mk2_512@violet.png` | `masters/bodies/boss_body_14_leviathan_mk2_512@violet.png` | `512x512` | `512x512` | `0.627` | `0.693` | `b_boss_violet` |
| `15` | `AP-0120` | `B-BODY` | `GLYPH-boss-7014` | `chronos-mk2` | `sprites/bodies/boss_body_15_chronos_mk2_512@magenta.png` | `masters/bodies/boss_body_15_chronos_mk2_512@magenta.png` | `512x512` | `512x512` | `0.615` | `0.767` | `b_boss_magenta` |
| `16` | `AP-0120` | `B-BODY` | `GLYPH-boss-7015` | `seraph-mk2` | `sprites/bodies/boss_body_16_seraph_mk2_512@crimson.png` | `masters/bodies/boss_body_16_seraph_mk2_512@crimson.png` | `512x512` | `512x512` | `0.732` | `0.750` | `b_boss_crimson` |
| `17` | `AP-0120` | `B-BODY` | `GLYPH-boss-7016` | `kraken-mk2` | `sprites/bodies/boss_body_17_kraken_mk2_512@emerald.png` | `masters/bodies/boss_body_17_kraken_mk2_512@emerald.png` | `512x512` | `512x512` | `0.650` | `0.803` | `b_boss_emerald` |
| `18` | `AP-0120` | `B-BODY` | `GLYPH-boss-7017` | `scorpion-mk2` | `sprites/bodies/boss_body_18_scorpion_mk2_512@amber.png` | `masters/bodies/boss_body_18_scorpion_mk2_512@amber.png` | `512x512` | `512x512` | `0.611` | `0.740` | `b_boss_amber` |
| `19` | `AP-0120` | `B-BODY` | `GLYPH-boss-7018` | `colossus-mk2` | `sprites/bodies/boss_body_19_colossus_mk2_512@violet.png` | `masters/bodies/boss_body_19_colossus_mk2_512@violet.png` | `512x512` | `512x512` | `0.693` | `0.687` | `b_boss_violet` |
| `20` | `AP-0120` | `B-BODY` | `GLYPH-boss-9002` | `citadel-mk3` | `sprites/bodies/boss_body_20_citadel_mk3_512@amber.png` | `masters/bodies/boss_body_20_citadel_mk3_512@amber.png` | `512x512` | `512x512` | `0.754` | `0.758` | `b_boss_amber` |
| `21` | `AP-0120` | `B-BODY` | `GLYPH-boss-9003` | `arachnid-mk3` | `sprites/bodies/boss_body_21_arachnid_mk3_512@violet.png` | `masters/bodies/boss_body_21_arachnid_mk3_512@violet.png` | `512x512` | `512x512` | `0.667` | `0.683` | `b_boss_violet` |
| `22` | `AP-0120` | `B-BODY` | `GLYPH-boss-9004` | `leviathan-mk3` | `sprites/bodies/boss_body_22_leviathan_mk3_512@magenta.png` | `masters/bodies/boss_body_22_leviathan_mk3_512@magenta.png` | `512x512` | `512x512` | `0.628` | `0.704` | `b_boss_magenta` |
| `23` | `AP-0120` | `B-BODY` | `GLYPH-boss-9005` | `chronos-mk3` | `sprites/bodies/boss_body_23_chronos_mk3_512@crimson.png` | `masters/bodies/boss_body_23_chronos_mk3_512@crimson.png` | `512x512` | `512x512` | `0.662` | `0.772` | `b_boss_crimson` |
| `24` | `AP-0120` | `B-BODY` | `GLYPH-boss-9006` | `seraph-mk3` | `sprites/bodies/boss_body_24_seraph_mk3_512@emerald.png` | `masters/bodies/boss_body_24_seraph_mk3_512@emerald.png` | `512x512` | `512x512` | `0.704` | `0.773` | `b_boss_emerald` |
| `25` | `AP-0120` | `B-BODY` | `GLYPH-boss-9007` | `kraken-mk3` | `sprites/bodies/boss_body_25_kraken_mk3_512@amber.png` | `masters/bodies/boss_body_25_kraken_mk3_512@amber.png` | `512x512` | `512x512` | `0.630` | `0.778` | `b_boss_amber` |
| `26` | `AP-0120` | `B-BODY` | `GLYPH-boss-9008` | `scorpion-mk3` | `sprites/bodies/boss_body_26_scorpion_mk3_512@violet.png` | `masters/bodies/boss_body_26_scorpion_mk3_512@violet.png` | `512x512` | `512x512` | `0.616` | `0.700` | `b_boss_violet` |
| `27` | `AP-0120` | `B-BODY` | `GLYPH-boss-9009` | `colossus-mk3` | `sprites/bodies/boss_body_27_colossus_mk3_512@magenta.png` | `masters/bodies/boss_body_27_colossus_mk3_512@magenta.png` | `512x512` | `512x512` | `0.751` | `0.726` | `b_boss_magenta` |
| `28` | `AP-0120` | `B-BODY` | `GLYPH-boss-9010` | `citadel-mk4` | `sprites/bodies/boss_body_28_citadel_mk4_512@violet.png` | `masters/bodies/boss_body_28_citadel_mk4_512@violet.png` | `512x512` | `512x512` | `0.695` | `0.690` | `b_boss_violet` |
| `29` | `AP-0120` | `B-BODY` | `GLYPH-boss-9011` | `arachnid-mk4` | `sprites/bodies/boss_body_29_arachnid_mk4_512@magenta.png` | `masters/bodies/boss_body_29_arachnid_mk4_512@magenta.png` | `512x512` | `512x512` | `0.670` | `0.692` | `b_boss_magenta` |
| `30` | `AP-0120` | `B-BODY` | `GLYPH-boss-9012` | `leviathan-mk4` | `sprites/bodies/boss_body_30_leviathan_mk4_512@crimson.png` | `masters/bodies/boss_body_30_leviathan_mk4_512@crimson.png` | `512x512` | `512x512` | `0.678` | `0.726` | `b_boss_crimson` |
| `31` | `AP-0120` | `B-BODY` | `GLYPH-boss-9013` | `chronos-mk4` | `sprites/bodies/boss_body_31_chronos_mk4_512@emerald.png` | `masters/bodies/boss_body_31_chronos_mk4_512@emerald.png` | `512x512` | `512x512` | `0.643` | `0.793` | `b_boss_emerald` |
| `32` | `AP-0120` | `B-BODY` | `GLYPH-boss-9014` | `seraph-mk4` | `sprites/bodies/boss_body_32_seraph_mk4_512@amber.png` | `masters/bodies/boss_body_32_seraph_mk4_512@amber.png` | `512x512` | `512x512` | `0.690` | `0.750` | `b_boss_amber` |
| `33` | `AP-0120` | `B-BODY` | `GLYPH-boss-9015` | `kraken-mk4` | `sprites/bodies/boss_body_33_kraken_mk4_512@violet.png` | `masters/bodies/boss_body_33_kraken_mk4_512@violet.png` | `512x512` | `512x512` | `0.616` | `0.731` | `b_boss_violet` |
| `34` | `AP-0120` | `B-BODY` | `GLYPH-boss-9017` | `scorpion-mk4` | `sprites/bodies/boss_body_34_scorpion_mk4_512@magenta.png` | `masters/bodies/boss_body_34_scorpion_mk4_512@magenta.png` | `512x512` | `512x512` | `0.651` | `0.729` | `b_boss_magenta` |
| `35` | `AP-0120` | `B-BODY` | `GLYPH-boss-9018` | `colossus-mk4` | `sprites/bodies/boss_body_35_colossus_mk4_512@crimson.png` | `masters/bodies/boss_body_35_colossus_mk4_512@crimson.png` | `512x512` | `512x512` | `0.749` | `0.742` | `b_boss_crimson` |
| `36` | `AP-0122` | `B-PART` | `boss` | `command_head` | `sprites/parts/boss_part_01_command_head_256@crimson.png` | `masters/parts/boss_part_01_command_head_256@crimson.png` | `256x256` | `512x512` | `0.769` | `0.755` | `b_bosspart_crimson` |
| `37` | `AP-0123` | `B-PART` | `boss dong ho real` | `chrono_gear_turret` | `sprites/parts/boss_part_02_chrono_gear_turret_256@amber.png` | `masters/parts/boss_part_02_chrono_gear_turret_256@amber.png` | `256x256` | `512x512` | `0.693` | `0.763` | `b_bosspart_amber` |
| `38` | `AP-0124` | `B-PART` | `boss nhen doc xanh` | `venom_fang_pod` | `sprites/parts/boss_part_03_venom_fang_pod_256@emerald.png` | `masters/parts/boss_part_03_venom_fang_pod_256@emerald.png` | `256x256` | `512x512` | `0.717` | `0.780` | `b_bosspart_emerald` |
| `39` | `AP-0125` | `B-PART` | `boss to vc ban 2 ben` | `broadside_railgun` | `sprites/parts/boss_part_04_broadside_railgun_256@crimson.png` | `masters/parts/boss_part_04_broadside_railgun_256@crimson.png` | `256x256` | `512x512` | `0.605` | `0.666` | `b_bosspart_crimson` |
| `40` | `AP-0126` | `B-PART` | `minibosstronxoay` | `rotary_saw_ring` | `sprites/parts/boss_part_05_rotary_saw_ring_256@magenta.png` | `masters/parts/boss_part_05_rotary_saw_ring_256@magenta.png` | `256x256` | `512x512` | `0.661` | `0.757` | `b_bosspart_magenta` |
| `41` | `AP-0127` | `B-PART` | `sieuhopthe tachbophan` | `combiner_claw_arm` | `sprites/parts/boss_part_06_combiner_claw_arm_256@violet.png` | `masters/parts/boss_part_06_combiner_claw_arm_256@violet.png` | `256x256` | `512x512` | `0.723` | `0.675` | `b_bosspart_violet` |
| `42` | `AP-0128` | `B-PART` | `web` | `energy_snare_web` | `sprites/parts/boss_part_07_energy_snare_web_256@emerald.png` | `masters/parts/boss_part_07_energy_snare_web_256@emerald.png` | `256x256` | `512x512` | `0.594` | `0.806` | `b_bosspart_emerald` |

## Reproducibility

```bash
python3 art/w3-boss-b/build_w3b.py
python3 art/w3-boss-b/make_w3b_preview.py
```
