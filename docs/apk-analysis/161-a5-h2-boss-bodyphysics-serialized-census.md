# H2 — `Boss_BodyPhysics` serialized census (B6-half)

**Verdict:** `BOUNDED_SERIALIZED_CENSUS · SEMANTICS_NOT_BOUND · EVIDENCE_LEVEL_B`  
**Scope:** 251 serialized `Boss_BodyPhysics` records; requested 19 boss-damage Director classes. No assembly was available or consulted. This report does **not** establish that the serialized fields are read, how they affect gameplay, or which Director class consumes each component.

## Result

The source CSV contains **251 rows / 251 unique `path_id`s**. The corresponding raw TypeTree export has **251 records with the identical ID set**. Six copied fields match row-for-row across the CSV and TypeTree: `dmgFirst`, `dmgPerSec`, `isFirstTrigger`, `isTrigger`, `layerMask.m_Mask`, and `m_Enabled` (**251/251 matches for each**).

The two numeric fields are reported only as serialized values, without behavioral interpretation:

| Serialized field | Distinct values | Minimum | Median | Maximum | Value → count |
|---|---:|---:|---:|---:|---|
| `dmgFirst` | 15 | 0 | 500 | 9,000,000 | `0:4`, `200:20`, `500:114`, `900:1`, `1,000:33`, `1,500:22`, `1,800:1`, `2,000:2`, `2,500:12`, `3,000:1`, `5,000:15`, `10,000:12`, `100,000:1`, `500,000:4`, `9,000,000:9` |
| `dmgPerSec` | 16 | 5 | 50 | 1,000 | `5:5`, `10:12`, `15:31`, `20:5`, `30:24`, `50:77`, `80:5`, `100:60`, `150:6`, `180:6`, `200:2`, `240:2`, `300:9`, `360:2`, `500:1`, `1,000:4` |

Other serialized-field counts: `isFirstTrigger=true` **110** / false **141**; `isTrigger=true` **249** / false **2**; `layerMask.m_Mask=256` **251/251**; `m_Enabled=1` **251/251**. The receipt also includes the complete 32-pair (`dmgFirst`, `dmgPerSec`) frequency table and per-record values.

## Class attribution boundary

The pinned serialized prefab join resolves all 251 component IDs to root-label metadata, but those labels span **61 distinct roots** (including shared UI roots such as `Board_SelectBoss` and `Board_FightBoss`). This is not a unique mapping to the requested **19 boss-damage Director classes**. Therefore the class crosswalk is `NOT_BOUND`: **0/251** records are assigned to a Director class. No root-label co-occurrence is promoted into a class or gameplay-role claim.

The receipt preserves each row's component `path_id`, serialized game-object path, joined root label, and literal field values so a future, independently supported crosswalk can be added without recensus.

## Pinned artifacts and reproducibility

- Receipt: `datas/l3_a5_h2_boss_bodyphysics_serialized_census.json`
- Builder: `tools/build_a5_h2_boss_bodyphysics_census.py`
- Tests: `tests/test_a5_h2_boss_bodyphysics_census.py`
- Inputs, SHA-256, sizes, exact row joins, and all 251 records are recorded in the receipt.
- The builder checks every pinned input, compares CSV and TypeTree path-ID sets and six serialized fields, and verifies the existing `prefab_joins.csv.gz` component-ID set.

**B6 is not closed.** This H2 slice supports only the bounded serialized census/distribution (evidence level B). Runtime semantics, assembly consumer, and 19-class attribution remain `NOT_BOUND`; no runtime readback or parity is claimed.
