# D5 follow-up — bounded player-class/static-array join and lifecycle serialization boundary

**Verdict:** `PARTIAL_STATIC_ARRAY_JOIN · COMPONENT_OWNER_NOT_BOUND · EXTRA_LIFE_SERIALIZATION_NOT_BOUND` (evidence level B).  
This is a static join of implementation class names to existing captured `Player_Get_Datas` arrays. It is **not** a Unity serialized component-owner join, a measured DPS result, or a runtime lifecycle trace.

## Joined slice

The class inventory lists `Player_Attack_1` through `Player_Attack_24` (24 class names). The pinned `player_start_stats.json` receipt contains four valid 24-element arrays: `PlayerCosts`, `StartMainCannonDamages`, `StartMainCannonRate`, and `StartWingCannonDamages`. Following the **already-published** index rule in `DATA_SYNC.md` §24.14 (report 82's 72/72 static getter-argument proof), class suffix `N` maps to array index `N−1`. This builder reuses that result; it does not reopen or re-disassemble methods. Do not derive the array index from a source/player ID.

| Class | Array index | `PlayerCosts` | `StartMainCannonDamages` | `StartMainCannonRate` | `StartWingCannonDamages` |
|---|---:|---:|---:|---:|---:|
| `Player_Attack_1` | 0 | 0 | 4500 | 4.8 | 218 |
| `Player_Attack_2` | 1 | 0 | 220 | 6.8 | 75 |
| `Player_Attack_3` | 2 | 1050 | 2680 | 4.8 | 186 |
| `Player_Attack_4` | 3 | 3150 | 8000 | 5.8 | 118 |
| `Player_Attack_5` | 4 | -1 | 710 | 4.8 | 236 |
| `Player_Attack_6` | 5 | 3850 | 1650 | 4.8 | 309 |
| `Player_Attack_7` | 6 | 4550 | 255 | 5 | 365 |
| `Player_Attack_8` | 7 | 2450 | 800 | 4.8 | 99 |
| `Player_Attack_9` | 8 | 2450 | 500 | 4.8 | 165 |
| `Player_Attack_10` | 9 | -1 | 95 | 4.8 | 725 |
| `Player_Attack_11` | 10 | 3850 | 336 | 4.8 | 230 |
| `Player_Attack_12` | 11 | -1 | 3000 | 4.8 | 2800 |
| `Player_Attack_13` | 12 | 3150 | 2350 | 6.8 | 595 |
| `Player_Attack_14` | 13 | 4550 | 400 | 10.5 | 800 |
| `Player_Attack_15` | 14 | 4550 | 515 | 4.8 | 265 |
| `Player_Attack_16` | 15 | -1 | 3000 | 10.5 | 2150 |
| `Player_Attack_17` | 16 | 4550 | 2689 | 5.6 | 589 |
| `Player_Attack_18` | 17 | 2450 | 1800 | 4.8 | 345 |
| `Player_Attack_19` | 18 | -1 | 100 | 12 | 250 |
| `Player_Attack_20` | 19 | 4550 | 2250 | 7.5 | 435 |
| `Player_Attack_21` | 20 | -1 | 100 | 9 | 1650 |
| `Player_Attack_22` | 21 | 4550 | 2800 | 10.5 | 686 |
| `Player_Attack_23` | 22 | -1 | 110 | 9 | 400 |
| `Player_Attack_24` | 23 | -1 | 3300 | 10.5 | 820 |

These are captured static-array values. They are not converted to shot counts, hits, DPS, TTK, or runtime behavior. The join also does not bind any row to a concrete serialized player GameObject or prove which projectile instance was emitted.

## Serialized and extra-life boundary

- The captured ScriptableObject CSV export set contains no `Player_Attack_N` CSV or matching `Player_Attack_N` TypeTree export. Thus the class-to-array join above does **not** identify a serialized component owner.
- `GP_Datas.csv` has one serialized row (`path_id=6767`, GameObject PPtr path ID `404`, `player` PPtr path ID `2625`). Its exported columns do not include `countReborn`, `rebornNow`, `maxCountReborn`, or `listRebornUseItems`.
- Consequently, extra-life component ownership and serialized rewiring remain `NOT_BOUND` from these exports. This one-row export is not evidence of global absence, and no event delivery or lifecycle behavior is inferred.

## Pins and reproducibility

- Receipt: `datas/l3_a5_d5_serialized_joins.json` (complete 24-row join, field presence check, and input hashes).
- Builder: `tools/build_a5_d5_serialized_joins.py`; tests: `tests/test_a5_d5_serialized_joins.py`.
- Inputs pinned: `docs/apk-analysis/class-inventory.csv`, `datas/player_start_stats.json`, and `reverse-engineering/scriptableobjects/GP_Datas.csv`.
- The only index proof referenced is the prior published static result in `DATA_SYNC.md` §24.14 / report 82; no method body was read by this follow-up.
- D5 remains open for component-owner/serialized producer joins, extra-life rewiring evidence, and measured DPS. No runtime readback/parity or native/FDE work is claimed.
